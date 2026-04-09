from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


BASE = Path("/Users/alexi/Documents/GitHub/avance_curricular")

FUENTE = (
    BASE
    / "avance_curricular_2026/01_fuentes_institucionales/planes_estudio"
    / "Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx"
)

AUDITORIAS = (
    BASE
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias"
)


def normalizar_columna(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    return texto.strip("_")


def limpiar(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if re.fullmatch(r"\d+\.0", texto):
        return texto[:-2]

    return texto


def unir_unicos(serie):
    valores = sorted({
        limpiar(valor)
        for valor in serie
        if limpiar(valor)
    })

    return "; ".join(valores)


def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


# ============================================================
# VALIDACIÓN FUENTE
# ============================================================

if not FUENTE.exists():
    raise SystemExit(
        f"NO EXISTE LA FUENTE:\n{FUENTE}"
    )

marca = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    AUDITORIAS
    / f"CANONICO_TODOS_PLANES_ESTUDIO_{marca}"
)

for subcarpeta in [
    "00_CONTROL",
    "01_INTERMEDIOS",
    "02_RESULTADOS",
    "03_AUDITORIA",
]:
    (SALIDA / subcarpeta).mkdir(
        parents=True,
        exist_ok=False,
    )


# ============================================================
# LECTURA
# ============================================================

xls = pd.ExcelFile(FUENTE)

if "BBDD Bruta" not in xls.sheet_names:
    raise SystemExit(
        "BLOQUEO: no existe la hoja 'BBDD Bruta'.\n"
        f"Hojas observadas: {xls.sheet_names}"
    )

df = pd.read_excel(
    FUENTE,
    sheet_name="BBDD Bruta",
    dtype=str,
)

columnas_originales = list(df.columns)

df.columns = [
    normalizar_columna(columna)
    for columna in df.columns
]

requeridas = {
    "CODPESTUD",
    "CODRAMO",
    "NOMBRE",
    "NIVEL",
}

faltantes = sorted(
    requeridas - set(df.columns)
)

if faltantes:
    raise SystemExit(
        "BLOQUEO: faltan columnas requeridas: "
        + ", ".join(faltantes)
    )

for columna in df.columns:
    df[columna] = df[columna].map(limpiar)

df["CODPESTUD"] = (
    df["CODPESTUD"]
    .str.upper()
)

df["CODRAMO"] = (
    df["CODRAMO"]
    .str.upper()
)

df.insert(
    0,
    "FILA_EXCEL_ORIGINAL",
    df.index + 2,
)


# ============================================================
# REGISTROS UTILIZABLES Y EXCLUIDOS
# ============================================================

sin_plan = df[
    df["CODPESTUD"].eq("")
].copy()

sin_codigo_ramo = df[
    df["CODRAMO"].eq("")
].copy()

sin_nombre_ramo = df[
    df["NOMBRE"].eq("")
].copy()

sin_nivel = df[
    df["NIVEL"].eq("")
].copy()

utilizables = df[
    df["CODPESTUD"].ne("")
    & df["CODRAMO"].ne("")
    & df["NOMBRE"].ne("")
    & df["NIVEL"].ne("")
].copy()

utilizables["LLAVE_CANONICA"] = (
    utilizables["CODPESTUD"]
    + "||"
    + utilizables["CODRAMO"]
    + "||"
    + utilizables["NIVEL"]
)


# ============================================================
# DUPLICADOS
# ============================================================

duplicados = utilizables[
    utilizables.duplicated(
        subset=[
            "CODPESTUD",
            "CODRAMO",
            "NIVEL",
        ],
        keep=False,
    )
].copy()

duplicados = duplicados.sort_values(
    [
        "CODPESTUD",
        "NIVEL",
        "CODRAMO",
        "FILA_EXCEL_ORIGINAL",
    ]
)


# ============================================================
# CANÓNICO GENERAL
# ============================================================

agregaciones = {
    "NOMBRE": "first",
    "FILA_EXCEL_ORIGINAL": "min",
}

for columna in [
    "CODCARR",
    "NOMBRE_L",
    "NOMPESTUD",
    "SEDE",
    "SIGLA",
    "ORDENRAMO",
    "RAMOEQUIV",
    "DESCRAMOEQUIV",
    "RAMOREQ",
    "DESCRAMOREQ",
    "ESTADO",
    "TIPO",
    "AREA",
]:
    if columna in utilizables.columns:
        agregaciones[columna] = unir_unicos

canonico = (
    utilizables
    .groupby(
        [
            "CODPESTUD",
            "CODRAMO",
            "NIVEL",
            "LLAVE_CANONICA",
        ],
        as_index=False,
        dropna=False,
    )
    .agg(agregaciones)
)

canonico["NIVEL_ORDEN"] = pd.to_numeric(
    canonico["NIVEL"],
    errors="coerce",
)

canonico = (
    canonico
    .sort_values(
        [
            "CODPESTUD",
            "NIVEL_ORDEN",
            "CODRAMO",
        ],
        na_position="last",
    )
    .drop(columns="NIVEL_ORDEN")
)

canonico.insert(
    0,
    "ID_CANONICO",
    range(1, len(canonico) + 1),
)

canonico["FUENTE"] = str(FUENTE)
canonico["HOJA_FUENTE"] = "BBDD Bruta"
canonico["NIVEL_RESPALDO"] = "DATO_OBSERVADO"
canonico["ESTADO_CANONICO"] = "CANONICO_INSTITUCIONAL"


# ============================================================
# RESUMEN POR PLAN
# ============================================================

columnas_resumen = {
    "TOTAL_ASIGNATURAS": (
        "CODRAMO",
        "size",
    ),
    "NIVELES_DISTINTOS": (
        "NIVEL",
        "nunique",
    ),
    "NIVEL_MINIMO": (
        "NIVEL",
        lambda s: min(
            [
                int(x)
                for x in s
                if str(x).isdigit()
            ],
            default=None,
        ),
    ),
    "NIVEL_MAXIMO": (
        "NIVEL",
        lambda s: max(
            [
                int(x)
                for x in s
                if str(x).isdigit()
            ],
            default=None,
        ),
    ),
}

resumen_plan = (
    canonico
    .groupby(
        "CODPESTUD",
        dropna=False,
    )
    .agg(**columnas_resumen)
    .reset_index()
)

for columna in [
    "NOMPESTUD",
    "NOMBRE_L",
    "CODCARR",
    "SEDE",
]:
    if columna in canonico.columns:
        auxiliar = (
            canonico
            .groupby("CODPESTUD")[columna]
            .apply(unir_unicos)
            .reset_index()
        )

        resumen_plan = resumen_plan.merge(
            auxiliar,
            on="CODPESTUD",
            how="left",
        )

resumen_plan = resumen_plan.sort_values(
    [
        "NOMBRE_L"
        if "NOMBRE_L" in resumen_plan.columns
        else "CODPESTUD",
        "CODPESTUD",
    ]
)


# ============================================================
# CONTEO POR NIVEL
# ============================================================

conteo_nivel = (
    canonico
    .groupby(
        [
            "CODPESTUD",
            "NIVEL",
        ],
        dropna=False,
    )
    .agg(
        CANTIDAD_ASIGNATURAS=(
            "CODRAMO",
            "size",
        ),
        CODIGOS=(
            "CODRAMO",
            unir_unicos,
        ),
        ASIGNATURAS=(
            "NOMBRE",
            unir_unicos,
        ),
    )
    .reset_index()
)

conteo_nivel["NIVEL_ORDEN"] = pd.to_numeric(
    conteo_nivel["NIVEL"],
    errors="coerce",
)

conteo_nivel = (
    conteo_nivel
    .sort_values(
        [
            "CODPESTUD",
            "NIVEL_ORDEN",
        ],
        na_position="last",
    )
    .drop(columns="NIVEL_ORDEN")
)


# ============================================================
# MATRIZ PLAN × NIVEL
# ============================================================

matriz_niveles = (
    conteo_nivel
    .pivot(
        index="CODPESTUD",
        columns="NIVEL",
        values="CANTIDAD_ASIGNATURAS",
    )
    .fillna(0)
    .astype(int)
    .reset_index()
)

columnas_nivel = [
    columna
    for columna in matriz_niveles.columns
    if columna != "CODPESTUD"
]

columnas_nivel_ordenadas = sorted(
    columnas_nivel,
    key=lambda valor: (
        0,
        int(valor),
    )
    if str(valor).isdigit()
    else (
        1,
        str(valor),
    ),
)

matriz_niveles = matriz_niveles[
    ["CODPESTUD"]
    + columnas_nivel_ordenadas
]

matriz_niveles["TOTAL"] = (
    matriz_niveles[
        columnas_nivel_ordenadas
    ].sum(axis=1)
)


# ============================================================
# CONTROLES DE CONSISTENCIA
# ============================================================

control_totales = (
    canonico
    .groupby("CODPESTUD")
    .size()
    .reset_index(name="TOTAL_CANONICO")
    .merge(
        matriz_niveles[
            [
                "CODPESTUD",
                "TOTAL",
            ]
        ],
        on="CODPESTUD",
        how="outer",
    )
)

control_totales["DIFERENCIA"] = (
    control_totales["TOTAL_CANONICO"]
    - control_totales["TOTAL"]
)

control_totales["ESTADO"] = (
    control_totales["DIFERENCIA"]
    .map(
        lambda valor: (
            "OK"
            if valor == 0
            else "ERROR"
        )
    )
)

errores_control = control_totales[
    control_totales["ESTADO"].ne("OK")
]

if not errores_control.empty:
    raise SystemExit(
        "BLOQUEO: existen diferencias entre "
        "canónico y matriz por nivel."
    )


# ============================================================
# POSIBLES INCONSISTENCIAS
# ============================================================

nombres_multiples_codigo = (
    canonico
    .groupby(
        [
            "CODPESTUD",
            "CODRAMO",
        ]
    )
    .agg(
        NOMBRES_DISTINTOS=(
            "NOMBRE",
            "nunique",
        ),
        NOMBRES=(
            "NOMBRE",
            unir_unicos,
        ),
        NIVELES=(
            "NIVEL",
            unir_unicos,
        ),
    )
    .reset_index()
)

nombres_multiples_codigo = (
    nombres_multiples_codigo[
        nombres_multiples_codigo[
            "NOMBRES_DISTINTOS"
        ] > 1
    ]
)

codigo_en_varios_niveles = (
    canonico
    .groupby(
        [
            "CODPESTUD",
            "CODRAMO",
        ]
    )
    .agg(
        NIVELES_DISTINTOS=(
            "NIVEL",
            "nunique",
        ),
        NIVELES=(
            "NIVEL",
            unir_unicos,
        ),
        NOMBRE=(
            "NOMBRE",
            "first",
        ),
    )
    .reset_index()
)

codigo_en_varios_niveles = (
    codigo_en_varios_niveles[
        codigo_en_varios_niveles[
            "NIVELES_DISTINTOS"
        ] > 1
    ]
)


# ============================================================
# RESUMEN GENERAL
# ============================================================

resumen_general = pd.DataFrame([
    {
        "INDICADOR": "Filas fuente bruta",
        "VALOR": len(df),
    },
    {
        "INDICADOR": "Filas utilizables",
        "VALOR": len(utilizables),
    },
    {
        "INDICADOR": "Registros canónicos",
        "VALOR": len(canonico),
    },
    {
        "INDICADOR": "Planes distintos",
        "VALOR": canonico[
            "CODPESTUD"
        ].nunique(),
    },
    {
        "INDICADOR": "Códigos de carrera distintos",
        "VALOR": (
            canonico["CODCARR"].nunique()
            if "CODCARR" in canonico.columns
            else ""
        ),
    },
    {
        "INDICADOR": "Filas duplicadas auditadas",
        "VALOR": len(duplicados),
    },
    {
        "INDICADOR": "Filas sin plan",
        "VALOR": len(sin_plan),
    },
    {
        "INDICADOR": "Filas sin código de ramo",
        "VALOR": len(sin_codigo_ramo),
    },
    {
        "INDICADOR": "Filas sin nombre",
        "VALOR": len(sin_nombre_ramo),
    },
    {
        "INDICADOR": "Filas sin nivel",
        "VALOR": len(sin_nivel),
    },
    {
        "INDICADOR": "Nivel de respaldo",
        "VALOR": "DATO_OBSERVADO",
    },
    {
        "INDICADOR": "Fuente original modificada",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "Precarga generada",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "PES generado",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "Apto para carga",
        "VALOR": "NO",
    },
])


# ============================================================
# EXPORTACIÓN TSV
# ============================================================

utilizables.to_csv(
    SALIDA
    / "01_INTERMEDIOS/01_BBDD_BRUTA_UTILIZABLE.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

canonico.to_csv(
    SALIDA
    / "02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

resumen_plan.to_csv(
    SALIDA
    / "02_RESULTADOS/02_RESUMEN_POR_PLAN.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

conteo_nivel.to_csv(
    SALIDA
    / "02_RESULTADOS/03_CONTEO_POR_PLAN_Y_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

matriz_niveles.to_csv(
    SALIDA
    / "02_RESULTADOS/04_MATRIZ_PLAN_POR_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

control_totales.to_csv(
    SALIDA
    / "03_AUDITORIA/01_CONTROL_TOTALES.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

duplicados.to_csv(
    SALIDA
    / "03_AUDITORIA/02_DUPLICADOS_FUENTE_BRUTA.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

nombres_multiples_codigo.to_csv(
    SALIDA
    / "03_AUDITORIA/03_CODIGOS_CON_NOMBRES_MULTIPLES.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

codigo_en_varios_niveles.to_csv(
    SALIDA
    / "03_AUDITORIA/04_CODIGOS_EN_VARIOS_NIVELES.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

sin_plan.to_csv(
    SALIDA
    / "03_AUDITORIA/05_FILAS_SIN_PLAN.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

sin_codigo_ramo.to_csv(
    SALIDA
    / "03_AUDITORIA/06_FILAS_SIN_CODIGO_RAMO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

sin_nombre_ramo.to_csv(
    SALIDA
    / "03_AUDITORIA/07_FILAS_SIN_NOMBRE_RAMO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

sin_nivel.to_csv(
    SALIDA
    / "03_AUDITORIA/08_FILAS_SIN_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# EXCEL
# ============================================================

excel = (
    SALIDA
    / "02_RESULTADOS/05_CANONICO_TODOS_PLANES_ESTUDIO.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_general.to_excel(
        writer,
        sheet_name="RESUMEN_GENERAL",
        index=False,
    )

    resumen_plan.to_excel(
        writer,
        sheet_name="RESUMEN_POR_PLAN",
        index=False,
    )

    matriz_niveles.to_excel(
        writer,
        sheet_name="MATRIZ_PLAN_NIVEL",
        index=False,
    )

    conteo_nivel.to_excel(
        writer,
        sheet_name="DETALLE_PLAN_NIVEL",
        index=False,
    )

    canonico.to_excel(
        writer,
        sheet_name="CANONICO_COMPLETO",
        index=False,
    )

    control_totales.to_excel(
        writer,
        sheet_name="CONTROL_TOTALES",
        index=False,
    )

    duplicados.to_excel(
        writer,
        sheet_name="DUPLICADOS",
        index=False,
    )

    nombres_multiples_codigo.to_excel(
        writer,
        sheet_name="NOMBRES_MULTIPLES",
        index=False,
    )

    codigo_en_varios_niveles.to_excel(
        writer,
        sheet_name="CODIGO_VARIOS_NIVELES",
        index=False,
    )

    for hoja in writer.book.worksheets:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for columna in hoja.columns:
            letra = columna[0].column_letter

            ancho = max(
                len(str(celda.value or ""))
                for celda in columna[:1500]
            )

            hoja.column_dimensions[letra].width = min(
                max(ancho + 2, 12),
                55,
            )


# ============================================================
# MANIFIESTO
# ============================================================

manifiesto = {
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Canónico institucional de todos los planes",
    "fecha_ejecucion": datetime.now().isoformat(),
    "fuente": str(FUENTE),
    "hash_sha256_fuente": sha256(FUENTE),
    "hoja_fuente": "BBDD Bruta",
    "columnas_originales": columnas_originales,
    "llave_canonica": [
        "CODPESTUD",
        "CODRAMO",
        "NIVEL",
    ],
    "filas_fuente": len(df),
    "filas_utilizables": len(utilizables),
    "registros_canonicos": len(canonico),
    "planes_distintos": int(
        canonico["CODPESTUD"].nunique()
    ),
    "nivel_respaldo": "DATO_OBSERVADO",
    "regla_oficial": False,
    "fuente_original_modificada": False,
    "precarga_generada": False,
    "pes_generado": False,
    "apto_para_carga": False,
}

manifiesto_path = (
    SALIDA / "00_CONTROL/manifiesto.json"
)

with manifiesto_path.open(
    "w",
    encoding="utf-8",
) as archivo:
    json.dump(
        manifiesto,
        archivo,
        ensure_ascii=False,
        indent=2,
    )

hashes_path = (
    SALIDA / "00_CONTROL/hashes_salidas.sha256"
)

with hashes_path.open(
    "w",
    encoding="utf-8",
) as archivo:
    for ruta in sorted(SALIDA.rglob("*")):
        if ruta.is_file() and ruta != hashes_path:
            archivo.write(
                f"{sha256(ruta)}  "
                f"{ruta.relative_to(SALIDA)}\n"
            )


# ============================================================
# SALIDA TERMINAL
# ============================================================

print()
print("CANÓNICO DE TODOS LOS PLANES GENERADO")
print("=" * 85)
print()
print(f"Filas fuente bruta: {len(df)}")
print(f"Filas utilizables: {len(utilizables)}")
print(f"Registros canónicos: {len(canonico)}")
print(
    "Planes distintos: "
    f"{canonico['CODPESTUD'].nunique()}"
)
print(
    "Códigos de carrera distintos: "
    + (
        str(canonico["CODCARR"].nunique())
        if "CODCARR" in canonico.columns
        else "NO DISPONIBLE"
    )
)
print(f"Filas duplicadas auditadas: {len(duplicados)}")
print(f"Filas sin plan: {len(sin_plan)}")
print(f"Filas sin código de ramo: {len(sin_codigo_ramo)}")
print(f"Filas sin nombre: {len(sin_nombre_ramo)}")
print(f"Filas sin nivel: {len(sin_nivel)}")
print()
print("PRIMEROS 20 PLANES")
print(
    resumen_plan.head(20).to_string(
        index=False,
    )
)
print()
print(f"Excel: {excel}")
print(
    "Canónico TSV: "
    f"{SALIDA / '02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv'}"
)
print(
    "Resumen por plan: "
    f"{SALIDA / '02_RESULTADOS/02_RESUMEN_POR_PLAN.tsv'}"
)
print(
    "Matriz plan por nivel: "
    f"{SALIDA / '02_RESULTADOS/04_MATRIZ_PLAN_POR_NIVEL.tsv'}"
)
print(f"Manifiesto: {manifiesto_path}")
print(f"Carpeta: {SALIDA}")
print()
print("Fuente original modificada: NO")
print("Resultados anteriores sobrescritos: NO")
print("Regla oficial generada: NO")
print("Precarga generada: NO")
print("PES generado: NO")
print("Apto para carga: NO")
