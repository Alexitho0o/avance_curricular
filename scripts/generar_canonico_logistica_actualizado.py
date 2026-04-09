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

AUDITORIA = (
    BASE
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias"
    / "AUDITORIA_MALLAS_COMPARTIDAS_END_TO_END_20260701_090314"
)

PLANES = ["TLOG20241", "ILOG20241", "CILOG20241"]

TOTALES_ESPERADOS = {
    "TLOG20241": 26,
    "ILOG20241": 48,
    "CILOG20241": 23,
}


def norm(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    return texto.strip("_")


def limpio(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if re.fullmatch(r"\d+\.0", texto):
        return texto[:-2]

    return texto


def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)

    return h.hexdigest()


if not FUENTE.exists():
    raise SystemExit(f"No existe la fuente:\n{FUENTE}")

marca = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    AUDITORIA
    / "03_RESULTADOS"
    / f"CANONICO_LOGISTICA_ACTUALIZADO_{marca}"
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
# LECTURA FUENTE INSTITUCIONAL
# ============================================================

df = pd.read_excel(
    FUENTE,
    sheet_name="BBDD Bruta",
    dtype=str,
)

columnas_originales = list(df.columns)
df.columns = [norm(c) for c in df.columns]

requeridas = {
    "CODPESTUD",
    "CODRAMO",
    "NOMBRE",
    "NIVEL",
}

faltantes = requeridas - set(df.columns)

if faltantes:
    raise SystemExit(
        "Faltan columnas requeridas: "
        + ", ".join(sorted(faltantes))
    )

for columna in df.columns:
    df[columna] = df[columna].map(limpio)

df["CODPESTUD"] = df["CODPESTUD"].str.upper()
df["CODRAMO"] = df["CODRAMO"].str.upper()

bruto = df[
    df["CODPESTUD"].isin(PLANES)
].copy()

bruto.insert(
    0,
    "FILA_EXCEL_ORIGINAL",
    bruto.index + 2,
)

bruto["LLAVE_CANONICA"] = (
    bruto["CODPESTUD"]
    + "||"
    + bruto["CODRAMO"]
    + "||"
    + bruto["NIVEL"]
)


# ============================================================
# AUDITORÍA DUPLICADOS
# ============================================================

duplicados = bruto[
    bruto.duplicated(
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
# CANÓNICO
# ============================================================

def unir_unicos(serie):
    valores = sorted({
        str(valor).strip()
        for valor in serie
        if str(valor).strip()
    })

    return "; ".join(valores)


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
]:
    if columna in bruto.columns:
        agregaciones[columna] = unir_unicos

canonico = (
    bruto
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

canonico = canonico.sort_values(
    [
        "CODPESTUD",
        "NIVEL_ORDEN",
        "CODRAMO",
    ],
    na_position="last",
).drop(columns="NIVEL_ORDEN")

canonico.insert(
    0,
    "ID_CANONICO",
    range(1, len(canonico) + 1),
)

canonico["FUENTE"] = str(FUENTE)
canonico["HOJA_FUENTE"] = "BBDD Bruta"
canonico["NIVEL_RESPALDO"] = "DATO_OBSERVADO"
canonico["ESTADO"] = "CANONICO_ACTUALIZADO"


# ============================================================
# CONTROLES
# ============================================================

totales = (
    canonico
    .groupby("CODPESTUD")
    .size()
    .reindex(PLANES, fill_value=0)
)

errores = []

for plan, esperado in TOTALES_ESPERADOS.items():
    observado = int(totales[plan])

    if observado != esperado:
        errores.append(
            f"{plan}: esperado={esperado}, observado={observado}"
        )

if errores:
    raise SystemExit(
        "BLOQUEO: no se reproducen los totales:\n"
        + "\n".join(errores)
    )

if len(canonico) != 97:
    raise SystemExit(
        f"BLOQUEO: se esperaban 97 registros y se obtuvieron "
        f"{len(canonico)}."
    )

sin_codigo = canonico[
    canonico["CODRAMO"].eq("")
].copy()

sin_nombre = canonico[
    canonico["NOMBRE"].eq("")
].copy()

sin_nivel = canonico[
    canonico["NIVEL"].eq("")
].copy()

if not sin_codigo.empty:
    raise SystemExit("BLOQUEO: existen registros sin código.")

if not sin_nombre.empty:
    raise SystemExit("BLOQUEO: existen registros sin nombre.")

if not sin_nivel.empty:
    raise SystemExit("BLOQUEO: existen registros sin nivel.")


# ============================================================
# CONTEO POR NIVEL
# ============================================================

conteo_detalle = (
    canonico
    .groupby(
        ["CODPESTUD", "NIVEL"],
        dropna=False,
    )
    .agg(
        CANTIDAD_ASIGNATURAS=("CODRAMO", "size"),
        CODIGOS=("CODRAMO", unir_unicos),
        ASIGNATURAS=("NOMBRE", unir_unicos),
    )
    .reset_index()
)

tabla_niveles = (
    conteo_detalle
    .pivot(
        index="NIVEL",
        columns="CODPESTUD",
        values="CANTIDAD_ASIGNATURAS",
    )
    .fillna(0)
    .astype(int)
    .reset_index()
)

for plan in PLANES:
    if plan not in tabla_niveles.columns:
        tabla_niveles[plan] = 0

tabla_niveles["ORDEN"] = pd.to_numeric(
    tabla_niveles["NIVEL"],
    errors="coerce",
)

tabla_niveles = (
    tabla_niveles
    .sort_values("ORDEN")
    .drop(columns="ORDEN")
)

fila_total = {
    "NIVEL": "TOTAL",
    "TLOG20241": int(totales["TLOG20241"]),
    "ILOG20241": int(totales["ILOG20241"]),
    "CILOG20241": int(totales["CILOG20241"]),
}

tabla_niveles = pd.concat(
    [
        tabla_niveles,
        pd.DataFrame([fila_total]),
    ],
    ignore_index=True,
)


# ============================================================
# COMPARACIÓN CANÓNICO ANTERIOR
# ============================================================

comparacion = pd.DataFrame([
    {
        "CODPESTUD": plan,
        "TOTAL_CANONICO_ANTERIOR": anterior,
        "TOTAL_CANONICO_ACTUALIZADO": TOTALES_ESPERADOS[plan],
        "DIFERENCIA": TOTALES_ESPERADOS[plan] - anterior,
        "ESTADO": (
            "SIN_CAMBIO"
            if TOTALES_ESPERADOS[plan] == anterior
            else "ACTUALIZADO_CON_NUEVA_FUENTE"
        ),
    }
    for plan, anterior in {
        "TLOG20241": 26,
        "ILOG20241": 30,
        "CILOG20241": 17,
    }.items()
])


# ============================================================
# SALIDAS TSV
# ============================================================

bruto.to_csv(
    SALIDA / "01_INTERMEDIOS/01_LOGISTICA_BRUTO_FILTRADO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

canonico.to_csv(
    SALIDA / "02_RESULTADOS/01_CANONICO_LOGISTICA_ACTUALIZADO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

conteo_detalle.to_csv(
    SALIDA / "02_RESULTADOS/02_CONTEO_DETALLADO_POR_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

tabla_niveles.to_csv(
    SALIDA / "02_RESULTADOS/03_RESUMEN_ASIGNATURAS_POR_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

comparacion.to_csv(
    SALIDA / "02_RESULTADOS/04_COMPARACION_CANONICO_ANTERIOR.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

duplicados.to_csv(
    SALIDA / "03_AUDITORIA/01_DUPLICADOS_FUENTE_BRUTA.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# EXCEL FINAL
# ============================================================

excel = (
    SALIDA
    / "02_RESULTADOS/05_TABLA_CANONICA_LOGISTICA_ACTUALIZADA.xlsx"
)

resumen = pd.DataFrame([
    ["Proceso", "Avance Curricular SIES 2026"],
    ["Subproyecto", "Planes de estudio Logística"],
    ["Fuente", str(FUENTE)],
    ["Hoja fuente", "BBDD Bruta"],
    ["TLOG20241", 26],
    ["ILOG20241", 48],
    ["CILOG20241", 23],
    ["Total registros canónicos", 97],
    ["Llave canónica", "CODPESTUD + CODRAMO + NIVEL"],
    ["Nivel de respaldo", "DATO_OBSERVADO"],
    ["Original modificado", "NO"],
    ["Canónico anterior sobrescrito", "NO"],
    ["Precarga generada", "NO"],
    ["PES generado", "NO"],
    ["Apto para carga", "NO"],
], columns=["CAMPO", "VALOR"])

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    tabla_niveles.to_excel(
        writer,
        sheet_name="ASIGNATURAS_POR_NIVEL",
        index=False,
    )

    canonico.to_excel(
        writer,
        sheet_name="CANONICO_COMPLETO",
        index=False,
    )

    for plan in PLANES:
        canonico[
            canonico["CODPESTUD"].eq(plan)
        ].to_excel(
            writer,
            sheet_name=plan.replace("20241", ""),
            index=False,
        )

    conteo_detalle.to_excel(
        writer,
        sheet_name="DETALLE_POR_NIVEL",
        index=False,
    )

    comparacion.to_excel(
        writer,
        sheet_name="COMPARACION_ANTERIOR",
        index=False,
    )

    duplicados.to_excel(
        writer,
        sheet_name="DUPLICADOS_FUENTE",
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
    "subproyecto": "Canónico Logística actualizado",
    "fecha_ejecucion": datetime.now().isoformat(),
    "fuente": str(FUENTE),
    "hash_sha256_fuente": sha256(FUENTE),
    "hoja_fuente": "BBDD Bruta",
    "columnas_originales": columnas_originales,
    "planes": PLANES,
    "llave_canonica": [
        "CODPESTUD",
        "CODRAMO",
        "NIVEL",
    ],
    "totales": {
        plan: int(totales[plan])
        for plan in PLANES
    },
    "total_registros": len(canonico),
    "nivel_respaldo": "DATO_OBSERVADO",
    "fuente_original_modificada": False,
    "canonico_anterior_sobrescrito": False,
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
) as f:
    json.dump(
        manifiesto,
        f,
        ensure_ascii=False,
        indent=2,
    )

hash_salida = (
    SALIDA / "00_CONTROL/hashes_salidas.sha256"
)

with hash_salida.open(
    "w",
    encoding="utf-8",
) as f:
    for ruta in sorted(SALIDA.rglob("*")):
        if ruta.is_file() and ruta != hash_salida:
            f.write(
                f"{sha256(ruta)}  {ruta.relative_to(SALIDA)}\n"
            )


# ============================================================
# SALIDA TERMINAL
# ============================================================

print()
print("CANÓNICO LOGÍSTICA ACTUALIZADO GENERADO")
print("=" * 85)

print()
print("ASIGNATURAS POR NIVEL")
print(tabla_niveles.to_string(index=False))

print()
print("COMPARACIÓN CON CANÓNICO ANTERIOR")
print(comparacion.to_string(index=False))

print()
print(f"Registros canónicos: {len(canonico)}")
print(f"Filas brutas Logística: {len(bruto)}")
print(f"Filas duplicadas auditadas: {len(duplicados)}")
print()
print(f"Excel: {excel}")
print(
    "TSV canónico: "
    f"{SALIDA / '02_RESULTADOS/01_CANONICO_LOGISTICA_ACTUALIZADO.tsv'}"
)
print(f"Manifiesto: {manifiesto_path}")
print(f"Carpeta: {SALIDA}")
print()
print("Fuente original modificada: NO")
print("Canónico anterior sobrescrito: NO")
print("Precarga generada: NO")
print("PES generado: NO")
print("Apto para carga: NO")
