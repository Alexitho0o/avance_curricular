#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


# ============================================================
# CONTEXTO
# ============================================================

RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

CASOS_29 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "EXTRACCION_RUT_CODCLI_29_20260703_104251"
    / "02_RESULTADOS"
    / "01_REVISION_RUT_CODCLI_29.tsv"
)

PROMEDIOS_CANDIDATOS = [
    RAIZ / "PROMEDIOSDEALUMNOS_7804.xlsx",
    Path.home() / "Downloads" / "PROMEDIOSDEALUMNOS_7804.xlsx",
    Path.home() / "Desktop" / "PROMEDIOSDEALUMNOS_7804.xlsx",
]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"CRUCE_29_PROMEDIOALUMNOS_AVANCE_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in (RESULTADOS, AUDITORIAS, REPORTES):
    carpeta.mkdir(parents=True, exist_ok=True)


# ============================================================
# UTILIDADES
# ============================================================

def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def texto_limpio(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def norm_col(valor):
    texto = texto_limpio(valor).upper()
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(
        r"[^A-Z0-9]+",
        "_",
        texto,
    ).strip("_")


def norm_codigo(valor):
    texto = texto_limpio(valor).upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"\s+", "", texto)


def norm_rut(valor):
    texto = texto_limpio(valor).upper()

    if re.fullmatch(r"\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"[^0-9K]", "", texto)


def norm_texto(valor):
    texto = texto_limpio(valor).upper()
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(r"[^A-Z0-9]+", "", texto)


def buscar_columna(df, candidatas, obligatoria=False):
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    for candidata in candidatas:
        clave = norm_col(candidata)

        if clave in mapa:
            return mapa[clave]

    # Búsqueda parcial conservadora.
    for candidata in candidatas:
        clave = norm_col(candidata)

        coincidencias = [
            original
            for normalizada, original in mapa.items()
            if clave
            and (
                normalizada.startswith(clave)
                or normalizada.endswith(clave)
            )
        ]

        if len(coincidencias) == 1:
            return coincidencias[0]

    if obligatoria:
        raise RuntimeError(
            "No se encontró ninguna de las columnas requeridas: "
            + ", ".join(candidatas)
        )

    return None


def localizar_ultima(rutas):
    existentes = [
        ruta.resolve()
        for ruta in rutas
        if ruta.exists() and ruta.is_file()
    ]

    if not existentes:
        return None

    return max(
        existentes,
        key=lambda ruta: ruta.stat().st_mtime,
    )


def convertir_numero(valor):
    numero = pd.to_numeric(
        pd.Series([valor]),
        errors="coerce",
    ).iloc[0]

    if pd.isna(numero):
        return ""

    if float(numero).is_integer():
        return str(int(numero))

    return str(numero)


# ============================================================
# 1. LOCALIZAR FUENTES
# ============================================================

if not CASOS_29.exists():
    raise RuntimeError(
        f"No existe la fuente de 29 casos: {CASOS_29}"
    )

PROMEDIOS = localizar_ultima(
    PROMEDIOS_CANDIDATOS
)

if PROMEDIOS is None:
    raise RuntimeError(
        "No se encontró PROMEDIOSDEALUMNOS_7804.xlsx "
        "en el repositorio, Downloads o Desktop."
    )


directorios_avance = [
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    RAIZ,
]

candidatos_avance = []

for directorio in directorios_avance:
    if directorio.exists():
        candidatos_avance.extend(
            directorio.glob(
                "Avance de Malla03-07-2026*.xls"
            )
        )

archivos_avance = sorted({
    ruta.resolve()
    for ruta in candidatos_avance
    if ruta.is_file()
    and not ruta.name.startswith("~$")
})

if len(archivos_avance) < 2:
    raise RuntimeError(
        "No se encontraron los dos archivos "
        "'Avance de Malla03-07-2026*.xls'."
    )

archivos_avance = sorted(
    archivos_avance,
    key=lambda ruta: ruta.stat().st_mtime,
    reverse=True,
)[:2]

archivos_avance = sorted(
    archivos_avance,
    key=lambda ruta: ruta.name,
)


# ============================================================
# 2. LEER LOS 29 CASOS
# ============================================================

casos = pd.read_csv(
    CASOS_29,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(casos) != 29:
    raise RuntimeError(
        f"Se esperaban 29 casos y se encontraron "
        f"{len(casos)}."
    )

if casos["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Existen ID_FILA_5809 duplicados."
    )

col_rut_evidencia = buscar_columna(
    casos,
    [
        "RUT_EVIDENCIA_NORMALIZADO",
        "RUT_EVIDENCIA",
        "RUT_DATOS_IDENTIDAD",
        "RUT_DATOS_NORM",
    ],
    obligatoria=True,
)

col_rut_5809 = buscar_columna(
    casos,
    [
        "RUT_5809_NORMALIZADO",
        "RUT_5809",
        "DOCUMENTO_NORM",
        "NUM_DOCUMENTO",
        "RUT",
    ],
    obligatoria=True,
)

casos["RUT_EVIDENCIA_CRUCE"] = (
    casos[col_rut_evidencia]
    .map(norm_rut)
)

casos["RUT_5809_CONTROL"] = (
    casos[col_rut_5809]
    .map(norm_rut)
)

casos["RUT_CRUCE"] = (
    casos["RUT_EVIDENCIA_CRUCE"]
)

casos["COINCIDE_RUT_5809_EVIDENCIA"] = [
    (
        "SI"
        if rut_5809 and rut_evidencia
        and rut_5809 == rut_evidencia
        else (
            "NO"
            if rut_5809 and rut_evidencia
            else "SIN_COMPARADOR"
        )
    )
    for rut_5809, rut_evidencia in zip(
        casos["RUT_5809_CONTROL"],
        casos["RUT_EVIDENCIA_CRUCE"],
    )
]

if casos["RUT_EVIDENCIA_CRUCE"].eq("").any():
    faltantes = casos[
        casos["RUT_EVIDENCIA_CRUCE"].eq("")
    ]["ID_FILA_5809"].tolist()

    raise RuntimeError(
        "Existen casos sin RUT de evidencia para cruzar: "
        + " | ".join(faltantes)
    )

print()
print("LLAVES DE IDENTIFICACIÓN")
print("-" * 108)
print(
    "RUT principal para recuperar CODCLI: "
    "RUT_EVIDENCIA_NORMALIZADO"
)
print(
    "RUT 5809 conservado como control: "
    "RUT_5809_NORMALIZADO"
)
print(
    "RUT distintos entre 5809 y evidencia: "
    f"{casos['COINCIDE_RUT_5809_EVIDENCIA'].eq('NO').sum()}"
)
print("-" * 108)


# ============================================================
# 3. LEER PROMEDIOS DE ALUMNOS
# ============================================================

libro_promedios = pd.ExcelFile(
    PROMEDIOS,
    engine="openpyxl",
)

diagnostico_hojas_promedios = []
candidatas_hoja = []

orden_hojas = sorted(
    libro_promedios.sheet_names,
    key=lambda hoja: (
        0 if norm_col(hoja) == "DATOSALUMNOS" else 1,
        hoja,
    ),
)

for hoja in orden_hojas:
    df_hoja = pd.read_excel(
        PROMEDIOS,
        sheet_name=hoja,
        dtype=object,
        engine="openpyxl",
    )

    df_hoja = df_hoja.dropna(
        axis=0,
        how="all",
    ).dropna(
        axis=1,
        how="all",
    )

    col_rut_hoja = buscar_columna(
        df_hoja,
        [
            "RUT",
            "RUT_ALUMNO",
            "NUM_DOCUMENTO",
            "DOCUMENTO",
            "RUTALUMNO",
        ],
        obligatoria=False,
    )

    col_codcli_hoja = buscar_columna(
        df_hoja,
        [
            "CODCLI",
            "CODIGO_ALUMNO",
            "COD_ALUMNO",
            "CODIGO_ESTUDIANTE",
            "COD_ESTUDIANTE",
        ],
        obligatoria=False,
    )

    diagnostico_hojas_promedios.append({
        "HOJA": hoja,
        "FILAS": len(df_hoja),
        "COLUMNAS": len(df_hoja.columns),
        "COLUMNA_RUT": col_rut_hoja or "",
        "COLUMNA_CODCLI": col_codcli_hoja or "",
        "ES_CANDIDATA": (
            "SI"
            if col_rut_hoja and col_codcli_hoja
            else "NO"
        ),
    })

    if col_rut_hoja and col_codcli_hoja:
        candidatas_hoja.append({
            "HOJA": hoja,
            "DF": df_hoja,
            "COL_RUT": col_rut_hoja,
            "COL_CODCLI": col_codcli_hoja,
        })

if not candidatas_hoja:
    detalle = pd.DataFrame(
        diagnostico_hojas_promedios
    ).to_string(index=False)

    raise RuntimeError(
        "Ninguna hoja de PROMEDIOSDEALUMNOS contiene "
        "simultáneamente RUT y CODCLI.\n\n"
        + detalle
    )

datosalumnos = [
    candidata
    for candidata in candidatas_hoja
    if norm_col(candidata["HOJA"]) == "DATOSALUMNOS"
]

if len(datosalumnos) == 1:
    seleccion = datosalumnos[0]

elif len(candidatas_hoja) == 1:
    seleccion = candidatas_hoja[0]

else:
    nombres = " | ".join(
        candidata["HOJA"]
        for candidata in candidatas_hoja
    )

    raise RuntimeError(
        "Existe más de una hoja con RUT y CODCLI y no se "
        "puede seleccionar automáticamente. Hojas: "
        + nombres
    )

hoja_preferida = seleccion["HOJA"]
promedios = seleccion["DF"]
col_rut_promedios = seleccion["COL_RUT"]
col_codcli_promedios = seleccion["COL_CODCLI"]

print()
print("HOJA PROMEDIOS SELECCIONADA")
print("-" * 108)
print(f"Hoja: {hoja_preferida}")
print(f"Columna RUT: {col_rut_promedios}")
print(f"Columna CODCLI: {col_codcli_promedios}")
print(f"Filas útiles: {len(promedios)}")
print("-" * 108)

col_carrera_promedios = buscar_columna(
    promedios,
    [
        "CODCARPR",
        "CODCARR",
        "CODIGO_CARRERA",
        "COD_CARRERA",
        "CARRERA",
        "NOMBRE_CARRERA",
    ],
)

col_plan_promedios = buscar_columna(
    promedios,
    [
        "CODPESTUD",
        "PLAN_ESTUDIOS",
        "PLAN_DE_ESTUDIO",
        "CODIGO_PLAN",
        "PLAN",
    ],
)

col_sede_promedios = buscar_columna(
    promedios,
    [
        "CODSEDE",
        "SEDE",
        "CODIGO_SEDE",
    ],
)

col_jornada_promedios = buscar_columna(
    promedios,
    [
        "CODJOR",
        "JORNADA",
        "CODIGO_JORNADA",
    ],
)


promedios_base = pd.DataFrame({
    "RUT_PROMEDIOS":
    promedios[col_rut_promedios].map(norm_rut),

    "CODCLI_PROMEDIOS":
    promedios[col_codcli_promedios].map(norm_codigo),

    "CARRERA_PROMEDIOS":
    (
        promedios[col_carrera_promedios].map(norm_codigo)
        if col_carrera_promedios
        else ""
    ),

    "PLAN_PROMEDIOS":
    (
        promedios[col_plan_promedios].map(norm_codigo)
        if col_plan_promedios
        else ""
    ),

    "SEDE_PROMEDIOS":
    (
        promedios[col_sede_promedios].map(norm_codigo)
        if col_sede_promedios
        else ""
    ),

    "JORNADA_PROMEDIOS":
    (
        promedios[col_jornada_promedios].map(norm_codigo)
        if col_jornada_promedios
        else ""
    ),

    "FILA_PROMEDIOS":
    range(2, len(promedios) + 2),
})

promedios_base = promedios_base[
    promedios_base["RUT_PROMEDIOS"].ne("")
    & promedios_base["CODCLI_PROMEDIOS"].ne("")
].copy()


# ============================================================
# 4. DIAGNOSTICAR MULTIPLICIDAD RUT → CODCLI
# ============================================================

resumen_rut_promedios = (
    promedios_base.groupby(
        "RUT_PROMEDIOS",
        dropna=False,
    )
    .agg(
        REGISTROS_PROMEDIOS=(
            "CODCLI_PROMEDIOS",
            "size",
        ),
        N_CODCLI_PROMEDIOS=(
            "CODCLI_PROMEDIOS",
            "nunique",
        ),
        CODCLI_PROMEDIOS_LISTA=(
            "CODCLI_PROMEDIOS",
            lambda serie: " | ".join(
                sorted(set(serie))
            ),
        ),
        N_CARRERAS_PROMEDIOS=(
            "CARRERA_PROMEDIOS",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CARRERAS_PROMEDIOS_LISTA=(
            "CARRERA_PROMEDIOS",
            lambda serie: " | ".join(
                sorted({
                    valor
                    for valor in serie
                    if valor
                })
            ),
        ),
        PLANES_PROMEDIOS_LISTA=(
            "PLAN_PROMEDIOS",
            lambda serie: " | ".join(
                sorted({
                    valor
                    for valor in serie
                    if valor
                })
            ),
        ),
    )
    .reset_index()
)


# ============================================================
# 5. CRUZAR 29 RUT CON PROMEDIOS DE ALUMNOS
# ============================================================

cruce_rut = casos.merge(
    resumen_rut_promedios,
    left_on="RUT_CRUCE",
    right_on="RUT_PROMEDIOS",
    how="left",
    validate="one_to_one",
)

if len(cruce_rut) != 29:
    raise RuntimeError(
        "El cruce con Promedio Alumnos alteró "
        "el universo de 29 casos."
    )

cruce_rut["REGISTROS_PROMEDIOS"] = (
    pd.to_numeric(
        cruce_rut["REGISTROS_PROMEDIOS"],
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)

cruce_rut["N_CODCLI_PROMEDIOS"] = (
    pd.to_numeric(
        cruce_rut["N_CODCLI_PROMEDIOS"],
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)

cruce_rut["ESTADO_RUT_CODCLI"] = ""

cruce_rut.loc[
    cruce_rut["N_CODCLI_PROMEDIOS"].eq(0),
    "ESTADO_RUT_CODCLI",
] = "RUT_NO_ENCONTRADO_EN_PROMEDIOS"

cruce_rut.loc[
    cruce_rut["N_CODCLI_PROMEDIOS"].eq(1),
    "ESTADO_RUT_CODCLI",
] = "RUT_CON_CODCLI_UNICO"

cruce_rut.loc[
    cruce_rut["N_CODCLI_PROMEDIOS"].gt(1),
    "ESTADO_RUT_CODCLI",
] = "RUT_CON_MULTIPLES_CODCLI"


# ============================================================
# 6. EXPANDIR RUT → CODCLI PARA BUSCAR EN AVANCE
# ============================================================

detalle_rut_codcli = casos[
    [
        "ID_FILA_5809",
        "RUT_5809_CONTROL",
        "RUT_EVIDENCIA_CRUCE",
        "RUT_CRUCE",
        "COINCIDE_RUT_5809_EVIDENCIA",
        "DECISION_RECOMENDADA",
        "CATEGORIA_REVISION",
        "CODCARR_PLAN_VIGENTE",
        "CODCARPR_EVIDENCIA",
    ]
].merge(
    promedios_base,
    left_on="RUT_CRUCE",
    right_on="RUT_PROMEDIOS",
    how="left",
)

detalle_rut_codcli["CODCLI_PROMEDIOS"] = (
    detalle_rut_codcli[
        "CODCLI_PROMEDIOS"
    ].fillna("")
)


# ============================================================
# 7. LEER LOS AVANCES COMO MATRIZ CRUDA
# ============================================================

celdas_avance = []
inventario_hojas = []

for archivo in archivos_avance:
    libro = pd.ExcelFile(
        archivo,
        engine="xlrd",
    )

    for hoja in libro.sheet_names:
        crudo = pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=None,
            dtype=object,
            engine="xlrd",
        )

        inventario_hojas.append({
            "ARCHIVO": str(archivo),
            "HOJA": hoja,
            "FILAS_FISICAS": len(crudo),
            "COLUMNAS_FISICAS": len(crudo.columns),
        })

        for fila_pos in range(len(crudo)):
            for col_pos in range(len(crudo.columns)):
                valor = crudo.iat[
                    fila_pos,
                    col_pos,
                ]

                if pd.isna(valor):
                    continue

                valor_texto = texto_limpio(valor)

                if not valor_texto:
                    continue

                celdas_avance.append({
                    "FUENTE_ARCHIVO": archivo.name,
                    "FUENTE_RUTA": str(archivo),
                    "FUENTE_HOJA": hoja,
                    "FILA_XLS": fila_pos + 1,
                    "COLUMNA_XLS": col_pos + 1,
                    "VALOR_ORIGINAL": valor_texto,
                    "VALOR_CODIGO_NORM": norm_codigo(
                        valor_texto
                    ),
                    "VALOR_TEXTO_NORM": norm_texto(
                        valor_texto
                    ),
                })


celdas_avance = pd.DataFrame(
    celdas_avance
)

if celdas_avance.empty:
    raise RuntimeError(
        "Los reportes de Avance de Malla no contienen "
        "celdas utilizables."
    )


# ============================================================
# 8. BUSCAR CODCLI DE PROMEDIOS EN CUALQUIER CELDA DEL AVANCE
# ============================================================

codcli_objetivo = sorted({
    valor
    for valor in detalle_rut_codcli[
        "CODCLI_PROMEDIOS"
    ]
    if valor
})

coincidencias_codcli = celdas_avance[
    celdas_avance[
        "VALOR_CODIGO_NORM"
    ].isin(codcli_objetivo)
].copy()

if coincidencias_codcli.empty:
    coincidencias_resumen = pd.DataFrame(
        columns=[
            "CODCLI_PROMEDIOS",
            "N_COINCIDENCIAS_AVANCE",
            "ARCHIVOS_AVANCE",
            "HOJAS_AVANCE",
            "UBICACIONES_AVANCE",
        ]
    )
else:
    coincidencias_resumen = (
        coincidencias_codcli.groupby(
            "VALOR_CODIGO_NORM",
            dropna=False,
        )
        .agg(
            N_COINCIDENCIAS_AVANCE=(
                "VALOR_CODIGO_NORM",
                "size",
            ),
            ARCHIVOS_AVANCE=(
                "FUENTE_ARCHIVO",
                lambda serie: " | ".join(
                    sorted(set(serie))
                ),
            ),
            HOJAS_AVANCE=(
                "FUENTE_HOJA",
                lambda serie: " | ".join(
                    sorted(set(map(str, serie)))
                ),
            ),
            UBICACIONES_AVANCE=(
                "FILA_XLS",
                lambda serie: " | ".join(
                    map(str, serie)
                ),
            ),
        )
        .reset_index()
        .rename(
            columns={
                "VALOR_CODIGO_NORM":
                "CODCLI_PROMEDIOS"
            }
        )
    )


# ============================================================
# 9. CONSOLIDAR POR ESTUDIANTE
# ============================================================

detalle_final = detalle_rut_codcli.merge(
    coincidencias_resumen,
    on="CODCLI_PROMEDIOS",
    how="left",
)

detalle_final["N_COINCIDENCIAS_AVANCE"] = (
    pd.to_numeric(
        detalle_final["N_COINCIDENCIAS_AVANCE"],
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)

detalle_final["ENCONTRADO_EN_AVANCE"] = (
    detalle_final[
        "N_COINCIDENCIAS_AVANCE"
    ].gt(0)
    .map({
        True: "SI",
        False: "NO",
    })
)


def resolver_estado_grupo(grupo):
    codcli = sorted({
        norm_codigo(valor)
        for valor in grupo["CODCLI_PROMEDIOS"]
        if norm_codigo(valor)
    })

    encontrados = sorted({
        norm_codigo(valor)
        for valor, existe in zip(
            grupo["CODCLI_PROMEDIOS"],
            grupo["ENCONTRADO_EN_AVANCE"],
        )
        if norm_codigo(valor) and existe == "SI"
    })

    carreras = sorted({
        norm_codigo(valor)
        for valor in grupo["CARRERA_PROMEDIOS"]
        if norm_codigo(valor)
    })

    if not codcli:
        estado = "SIN_CODCLI_DESDE_PROMEDIOS"
    elif len(codcli) == 1 and len(encontrados) == 1:
        estado = "CODCLI_UNICO_ENCONTRADO_EN_AVANCE"
    elif len(codcli) == 1 and not encontrados:
        estado = "CODCLI_UNICO_NO_ENCONTRADO_EN_AVANCE"
    elif len(codcli) > 1 and len(encontrados) == 1:
        estado = "MULTIPLES_CODCLI_UNO_ENCONTRADO_EN_AVANCE"
    elif len(codcli) > 1 and len(encontrados) > 1:
        estado = "MULTIPLES_CODCLI_ENCONTRADOS_EN_AVANCE"
    else:
        estado = "MULTIPLES_CODCLI_NINGUNO_ENCONTRADO"

    return pd.Series({
        "N_CODCLI_PROMEDIOS": len(codcli),
        "CODCLI_PROMEDIOS_LISTA": " | ".join(
            codcli
        ),
        "N_CODCLI_ENCONTRADOS_AVANCE": len(
            encontrados
        ),
        "CODCLI_ENCONTRADOS_AVANCE": " | ".join(
            encontrados
        ),
        "N_CARRERAS_PROMEDIOS": len(carreras),
        "CARRERAS_PROMEDIOS_LISTA": " | ".join(
            carreras
        ),
        "ESTADO_CRUCE_FINAL": estado,
    })


resumen_final = (
    detalle_final.groupby(
        "ID_FILA_5809",
        dropna=False,
    )
    .apply(
        resolver_estado_grupo,
        include_groups=False,
    )
    .reset_index()
)

resultado = casos.merge(
    resumen_final,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

if len(resultado) != 29:
    raise RuntimeError(
        "El consolidado final no conserva los 29 casos."
    )


# ============================================================
# 10. CARRERA COMO SEGUNDA VARIABLE
# ============================================================

resultado["CARRERA_5809_NORM"] = (
    resultado[
        "CODCARR_PLAN_VIGENTE"
    ].map(norm_codigo)
)

resultado["CARRERA_EVIDENCIA_NORM"] = (
    resultado[
        "CODCARPR_EVIDENCIA"
    ].map(norm_codigo)
)

resultado["VALIDACION_CARRERA_SECUNDARIA"] = ""

for indice, fila in resultado.iterrows():
    carreras = {
        valor
        for valor in str(
            fila.get(
                "CARRERAS_PROMEDIOS_LISTA",
                "",
            )
        ).split(" | ")
        if valor
    }

    carrera_5809 = fila[
        "CARRERA_5809_NORM"
    ]

    carrera_evidencia = fila[
        "CARRERA_EVIDENCIA_NORM"
    ]

    if not carreras:
        estado = "SIN_CARRERA_EN_PROMEDIOS"

    elif carrera_5809 in carreras:
        estado = "COINCIDE_CARRERA_5809"

    elif carrera_evidencia in carreras:
        estado = "COINCIDE_CARRERA_EVIDENCIA"

    elif len(carreras) > 1:
        estado = "MULTIPLES_CARRERAS_SIN_COINCIDENCIA"

    else:
        estado = "CARRERA_PROMEDIOS_DISTINTA"

    resultado.at[
        indice,
        "VALIDACION_CARRERA_SECUNDARIA",
    ] = estado


# ============================================================
# 11. CLASIFICAR PARA SIGUIENTE FASE
# ============================================================

resultado["ESTADO_PARA_REVISION_AVANCE"] = ""
resultado["ADECUAR_NIVEL_AUN"] = "NO"

mask_unico = resultado[
    "ESTADO_CRUCE_FINAL"
].eq(
    "CODCLI_UNICO_ENCONTRADO_EN_AVANCE"
)

resultado.loc[
    mask_unico,
    "ESTADO_PARA_REVISION_AVANCE",
] = "CODCLI_CONFIRMADO_REVISAR_PERIODIZACION"

mask_multiple_uno = resultado[
    "ESTADO_CRUCE_FINAL"
].eq(
    "MULTIPLES_CODCLI_UNO_ENCONTRADO_EN_AVANCE"
)

resultado.loc[
    mask_multiple_uno,
    "ESTADO_PARA_REVISION_AVANCE",
] = "CODCLI_RESUELTO_POR_PRESENCIA_EN_AVANCE"

mask_ambiguo = resultado[
    "ESTADO_CRUCE_FINAL"
].isin([
    "MULTIPLES_CODCLI_ENCONTRADOS_EN_AVANCE",
    "MULTIPLES_CODCLI_NINGUNO_ENCONTRADO",
])

resultado.loc[
    mask_ambiguo,
    "ESTADO_PARA_REVISION_AVANCE",
] = "MANTENER_PENDIENTE_CODCLI_AMBIGUO"

mask_no_encontrado = resultado[
    "ESTADO_CRUCE_FINAL"
].isin([
        "CODCLI_UNICO_NO_ENCONTRADO_EN_AVANCE",
        "SIN_CODCLI_DESDE_PROMEDIOS",
    ])

resultado.loc[
    mask_no_encontrado,
    "ESTADO_PARA_REVISION_AVANCE",
] = "MANTENER_PENDIENTE_SIN_EVIDENCIA_AVANCE"


# ============================================================
# 12. RESÚMENES
# ============================================================

resumen_estados = (
    resultado[
        "ESTADO_CRUCE_FINAL"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

resumen_carrera = (
    resultado[
        "VALIDACION_CARRERA_SECUNDARIA"
    ]
    .value_counts(dropna=False)
    .rename_axis("VALIDACION_CARRERA")
    .reset_index(name="CASOS")
)

resumen_kpi = pd.DataFrame([
    {
        "INDICADOR": "Casos analizados",
        "VALOR": len(resultado),
    },
    {
        "INDICADOR": "RUT encontrados en Promedio Alumnos",
        "VALOR": int(
            resultado[
                "N_CODCLI_PROMEDIOS"
            ].fillna(0).gt(0).sum()
        ),
    },
    {
        "INDICADOR": "CODCLI únicos encontrados en avance",
        "VALOR": int(
            resultado[
                "ESTADO_CRUCE_FINAL"
            ].eq(
                "CODCLI_UNICO_ENCONTRADO_EN_AVANCE"
            ).sum()
        ),
    },
    {
        "INDICADOR": "Múltiples CODCLI con uno en avance",
        "VALOR": int(
            resultado[
                "ESTADO_CRUCE_FINAL"
            ].eq(
                "MULTIPLES_CODCLI_UNO_ENCONTRADO_EN_AVANCE"
            ).sum()
        ),
    },
    {
        "INDICADOR": "Casos aún ambiguos",
        "VALOR": int(
            resultado[
                "ESTADO_PARA_REVISION_AVANCE"
            ].str.startswith(
                "MANTENER_PENDIENTE",
                na=False,
            ).sum()
        ),
    },
    {
        "INDICADOR": "Niveles modificados",
        "VALOR": 0,
    },
])


# ============================================================
# 13. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_29",
        "RESULTADO": (
            "OK" if len(resultado) == 29 else "ERROR"
        ),
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "RUT_EVIDENCIA_COMPLETOS",
        "RESULTADO": (
            "OK"
            if resultado[
                "RUT_EVIDENCIA_CRUCE"
            ].ne("").all()
            else "ERROR"
        ),
        "DETALLE": int(
            resultado[
                "RUT_EVIDENCIA_CRUCE"
            ].eq("").sum()
        ),
    },
    {
        "VALIDACION": "RUT_5809_VS_EVIDENCIA_DISTINTOS",
        "RESULTADO": "INFORMATIVO",
        "DETALLE": int(
            resultado[
                "COINCIDE_RUT_5809_EVIDENCIA"
            ].eq("NO").sum()
        ),
    },
    {
        "VALIDACION": "NIVELES_MODIFICADOS",
        "RESULTADO": "OK",
        "DETALLE": 0,
    },
    {
        "VALIDACION": "FUENTES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "ARCHIVO_CARGA_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


# ============================================================
# 14. EXPORTAR
# ============================================================

resultado.to_csv(
    RESULTADOS
    / "01_CRUCE_29_RUT_CODCLI_AVANCE.tsv",
    sep="\t",
    index=False,
)

detalle_final.to_csv(
    RESULTADOS
    / "02_DETALLE_RUT_CODCLI_PROMEDIOS_AVANCE.tsv",
    sep="\t",
    index=False,
)

coincidencias_codcli.to_csv(
    RESULTADOS
    / "03_COINCIDENCIAS_CODCLI_EN_CELDAS_AVANCE.tsv",
    sep="\t",
    index=False,
)

promedios_base.to_csv(
    AUDITORIAS
    / "01_BASE_PROMEDIOS_NORMALIZADA.tsv",
    sep="\t",
    index=False,
)

pd.DataFrame(inventario_hojas).to_csv(
    AUDITORIAS
    / "02_INVENTARIO_HOJAS_AVANCE.tsv",
    sep="\t",
    index=False,
)

pd.DataFrame(
    diagnostico_hojas_promedios
).to_csv(
    AUDITORIAS
    / "02B_DIAGNOSTICO_HOJAS_PROMEDIOS.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "03_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


fuentes = pd.DataFrame([
    {
        "ROL": "CASOS_29",
        "RUTA": str(CASOS_29),
        "SHA256": sha256(CASOS_29),
        "TAMANO_BYTES": CASOS_29.stat().st_size,
    },
    {
        "ROL": "PROMEDIOS_ALUMNOS",
        "RUTA": str(PROMEDIOS),
        "SHA256": sha256(PROMEDIOS),
        "TAMANO_BYTES": PROMEDIOS.stat().st_size,
    },
    *[
        {
            "ROL": f"AVANCE_MALLA_{numero}",
            "RUTA": str(ruta),
            "SHA256": sha256(ruta),
            "TAMANO_BYTES": ruta.stat().st_size,
        }
        for numero, ruta in enumerate(
            archivos_avance,
            start=1,
        )
    ],
])

fuentes.to_csv(
    AUDITORIAS
    / "04_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 15. EXCEL
# ============================================================

excel = (
    RESULTADOS
    / "CRUCE_29_PROMEDIOALUMNOS_AVANCE.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_kpi.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resumen_estados.to_excel(
        writer,
        sheet_name="ESTADOS_CODCLI",
        index=False,
    )

    resumen_carrera.to_excel(
        writer,
        sheet_name="CONTROL_CARRERA",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="CRUCE_29",
        index=False,
    )

    resultado[
        resultado[
            "ESTADO_PARA_REVISION_AVANCE"
        ].isin([
            "CODCLI_CONFIRMADO_REVISAR_PERIODIZACION",
            "CODCLI_RESUELTO_POR_PRESENCIA_EN_AVANCE",
        ])
    ].to_excel(
        writer,
        sheet_name="CODCLI_CONFIRMADOS",
        index=False,
    )

    resultado[
        resultado[
            "ESTADO_PARA_REVISION_AVANCE"
        ].str.startswith(
            "MANTENER_PENDIENTE",
            na=False,
        )
    ].to_excel(
        writer,
        sheet_name="AUN_PENDIENTES",
        index=False,
    )

    detalle_final.to_excel(
        writer,
        sheet_name="DETALLE_RUT_CODCLI",
        index=False,
    )

    coincidencias_codcli.to_excel(
        writer,
        sheet_name="CELDAS_AVANCE",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
        index=False,
    )

    fuentes.to_excel(
        writer,
        sheet_name="FUENTES",
        index=False,
    )

    for hoja in writer.book.worksheets:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for columna in hoja.columns:
            letra = columna[0].column_letter

            ancho = max(
                len(str(celda.value or ""))
                for celda in columna[:2000]
            )

            hoja.column_dimensions[letra].width = min(
                max(ancho + 2, 12),
                55,
            )


# ============================================================
# 16. MANIFIESTO
# ============================================================

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "universo": 29,
    "secuencia_cruce": [
        "RUT_EVIDENCIA_IDENTIDAD",
        "PROMEDIOSDEALUMNOS_DATOSALUMNOS",
        "CODCLI",
        "AVANCE_DE_MALLA",
        "CARRERA_COMO_SEGUNDA_VARIABLE",
        "RUT_5809_COMO_CONTROL",
    ],
    "hoja_promedios": hoja_preferida,
    "niveles_modificados": 0,
    "decisiones_modificadas": False,
    "fuentes_modificadas": False,
    "archivo_carga_generado": False,
    "salida": str(SALIDA),
}

(SALIDA / "manifest_ejecucion.json").write_text(
    json.dumps(
        manifiesto,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)


# ============================================================
# 17. TERMINAL
# ============================================================

print()
print("=" * 108)
print("CRUCE 29 CASOS: RUT → PROMEDIO ALUMNOS → CODCLI → AVANCE")
print("=" * 108)
print(f"Casos analizados: {len(resultado)}")
print(f"Hoja Promedio Alumnos: {hoja_preferida}")
print()
print("ESTADOS CODCLI")
print("-" * 108)

for _, fila in resumen_estados.iterrows():
    print(
        f"{fila['ESTADO']}: "
        f"{fila['CASOS']}"
    )

print()
print("VALIDACIÓN DE CARRERA COMO SEGUNDA VARIABLE")
print("-" * 108)

for _, fila in resumen_carrera.iterrows():
    print(
        f"{fila['VALIDACION_CARRERA']}: "
        f"{fila['CASOS']}"
    )

print()
print(
    "CODCLI confirmados para revisar periodización: "
    f"{resultado['ESTADO_PARA_REVISION_AVANCE'].isin([
        'CODCLI_CONFIRMADO_REVISAR_PERIODIZACION',
        'CODCLI_RESUELTO_POR_PRESENCIA_EN_AVANCE',
    ]).sum()}"
)
print(
    "Casos que continúan pendientes: "
    f"{resultado['ESTADO_PARA_REVISION_AVANCE'].str.startswith(
        'MANTENER_PENDIENTE',
        na=False,
    ).sum()}"
)
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Niveles modificados: 0")
print("Decisiones modificadas: NO")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 108)
