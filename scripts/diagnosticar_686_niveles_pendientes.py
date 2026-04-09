#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


# ============================================================
# CONTEXTO Y RUTAS
# ============================================================

RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

RESULTADO_NIVELES = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "RECALCULO_NIVELES_2371_CORREGIDO_20260702_001635"
    / "02_RESULTADOS"
    / "01_5809_TRAZABILIDAD_PLAN_MALLA_NIVEL.tsv"
)

PENDIENTES_NIVELES = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "RECALCULO_NIVELES_2371_CORREGIDO_20260702_001635"
    / "03_AUDITORIAS"
    / "01_PENDIENTES_O_CONFLICTOS_NIVEL.tsv"
)

PROMEDIOS = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "PROMEDIOSDEALUMNOS_7804.xlsx"
)

MALLAS = (
    RAIZ
    / "avance_curricular_2026"
    / "01_fuentes_institucionales"
    / "planes_estudio"
    / "Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"DIAGNOSTICO_686_NIVELES_PENDIENTES_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in (
    RESULTADOS,
    AUDITORIAS,
    REPORTES,
):
    carpeta.mkdir(parents=True, exist_ok=True)


# ============================================================
# UTILIDADES
# ============================================================

def norm_col(valor):
    texto = str(valor).strip().upper()
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
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"\s+", "", texto)


def norm_documento(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"[^0-9K]", "", texto)


def buscar_columna(
    df,
    opciones,
    obligatoria=False,
    contexto="",
):
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    for opcion in opciones:
        clave = norm_col(opcion)

        if clave in mapa:
            return mapa[clave]

    if obligatoria:
        raise RuntimeError(
            f"No se encontró columna requerida en {contexto}: "
            f"{opciones}. Disponibles: {list(df.columns)}"
        )

    return None


def unir_unicos(serie):
    valores = sorted({
        norm_codigo(valor)
        for valor in serie
        if norm_codigo(valor)
    })

    return " | ".join(valores)


def unir_niveles(serie):
    valores = pd.to_numeric(
        serie,
        errors="coerce",
    ).dropna()

    return " | ".join(
        str(int(valor))
        for valor in sorted(set(valores))
    )


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
# 1. VALIDAR FUENTES
# ============================================================

fuentes = {
    "RESULTADO_NIVELES": RESULTADO_NIVELES,
    "PENDIENTES_NIVELES": PENDIENTES_NIVELES,
    "PROMEDIOS": PROMEDIOS,
    "MALLAS": MALLAS,
}

for nombre, ruta in fuentes.items():
    if not ruta.exists():
        raise RuntimeError(
            f"No existe fuente requerida {nombre}: {ruta}"
        )


# ============================================================
# 2. LEER UNIVERSO Y PENDIENTES
# ============================================================

universo = pd.read_csv(
    RESULTADO_NIVELES,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

pendientes = pd.read_csv(
    PENDIENTES_NIVELES,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(universo) != 2371:
    raise RuntimeError(
        f"Universo inesperado: {len(universo)}."
    )

if len(pendientes) != 686:
    raise RuntimeError(
        f"Pendientes inesperados: {len(pendientes)}; "
        "esperados: 686."
    )

if pendientes["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Los pendientes contienen ID_FILA_5809 duplicado."
    )

pendientes["DOCUMENTO_NORM"] = (
    pendientes["DOCUMENTO_NORM"].map(norm_documento)
)

pendientes["CODPESTUD_RESUELTO"] = (
    pendientes["CODPESTUD_RESUELTO"].map(norm_codigo)
)


# ============================================================
# 3. LEER HOJA1 Y DATOSALUMNOS
# ============================================================

hoja1 = pd.read_excel(
    PROMEDIOS,
    sheet_name="Hoja1",
    dtype=object,
)

datos = pd.read_excel(
    PROMEDIOS,
    sheet_name="DatosAlumnos",
    dtype=object,
)

h_doc = buscar_columna(
    hoja1,
    ["RUT", "NUM_DOCUMENTO", "N_DOC"],
    obligatoria=True,
    contexto="Hoja1/documento",
)

h_plan = buscar_columna(
    hoja1,
    [
        "CODPESTUD",
        "PLAN_DE_ESTUDIO",
        "PLAN_ESTUDIOS",
    ],
    obligatoria=True,
    contexto="Hoja1/plan",
)

h_nivel = buscar_columna(
    hoja1,
    ["NIVEL", "NIV_ACA"],
    obligatoria=True,
    contexto="Hoja1/nivel",
)

h_codcli = buscar_columna(
    hoja1,
    ["CODCLI"],
)

h_ramo = buscar_columna(
    hoja1,
    ["CODRAMO", "CODIGO_ASIGNATURA"],
)

h = hoja1.copy()

h["DOCUMENTO_NORM_DIAG"] = (
    h[h_doc].map(norm_documento)
)

h["CODPESTUD_HISTORICO"] = (
    h[h_plan].map(norm_codigo)
)

h["NIVEL_HISTORICO"] = pd.to_numeric(
    h[h_nivel],
    errors="coerce",
)

h["CODCLI_HISTORICO"] = (
    h[h_codcli].map(norm_codigo)
    if h_codcli
    else ""
)

h["CODRAMO_HISTORICO"] = (
    h[h_ramo].map(norm_codigo)
    if h_ramo
    else ""
)

h = h[
    h["DOCUMENTO_NORM_DIAG"].ne("")
    & h["CODPESTUD_HISTORICO"].ne("")
].copy()


# ============================================================
# 4. DATOSALUMNOS
# ============================================================

d_doc = buscar_columna(
    datos,
    ["RUT", "NUM_DOCUMENTO", "N_DOC"],
    obligatoria=True,
    contexto="DatosAlumnos/documento",
)

d_codcli = buscar_columna(
    datos,
    ["CODCLI"],
)

d_carrera = buscar_columna(
    datos,
    [
        "CODCARPR",
        "CODCARR",
        "COD_CAR",
    ],
    obligatoria=True,
    contexto="DatosAlumnos/carrera",
)

d_nivel = buscar_columna(
    datos,
    [
        "NIVEL",
        "DA_NIVEL",
        "NIV_ACA",
    ],
    obligatoria=True,
    contexto="DatosAlumnos/nivel",
)

d = datos.copy()

d["DOCUMENTO_NORM_DIAG"] = (
    d[d_doc].map(norm_documento)
)

d["CODCLI_DATOS"] = (
    d[d_codcli].map(norm_codigo)
    if d_codcli
    else ""
)

d["CARRERA_DATOS"] = (
    d[d_carrera].map(norm_codigo)
)

d["NIVEL_DATOS"] = pd.to_numeric(
    d[d_nivel],
    errors="coerce",
)

d = d[
    d["DOCUMENTO_NORM_DIAG"].ne("")
].copy()


# ============================================================
# 5. RESUMEN DE HISTORIA POR DOCUMENTO Y PLAN
# ============================================================

historia_plan = (
    h.groupby(
        [
            "DOCUMENTO_NORM_DIAG",
            "CODPESTUD_HISTORICO",
        ],
        dropna=False,
    )
    .agg(
        NIVEL_MIN_HISTORICO=(
            "NIVEL_HISTORICO",
            "min",
        ),
        NIVEL_MAX_HISTORICO=(
            "NIVEL_HISTORICO",
            "max",
        ),
        NIVELES_HISTORICOS=(
            "NIVEL_HISTORICO",
            unir_niveles,
        ),
        RAMOS_DISTINTOS_HISTORICOS=(
            "CODRAMO_HISTORICO",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CODCLI_HISTORICOS=(
            "CODCLI_HISTORICO",
            unir_unicos,
        ),
    )
    .reset_index()
)

historia_documento = (
    h.groupby(
        "DOCUMENTO_NORM_DIAG",
        dropna=False,
    )
    .agg(
        N_PLANES_HISTORICOS=(
            "CODPESTUD_HISTORICO",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        PLANES_HISTORICOS=(
            "CODPESTUD_HISTORICO",
            unir_unicos,
        ),
        NIVEL_MAX_GLOBAL_HISTORICO=(
            "NIVEL_HISTORICO",
            "max",
        ),
        CODCLI_HISTORICOS_DOCUMENTO=(
            "CODCLI_HISTORICO",
            unir_unicos,
        ),
    )
    .reset_index()
)


# ============================================================
# 6. RESUMEN DATOSALUMNOS POR DOCUMENTO
# ============================================================

datos_documento = (
    d.groupby(
        "DOCUMENTO_NORM_DIAG",
        dropna=False,
    )
    .agg(
        N_CARRERAS_DATOS=(
            "CARRERA_DATOS",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CARRERAS_DATOS=(
            "CARRERA_DATOS",
            unir_unicos,
        ),
        NIVEL_MIN_DATOS=(
            "NIVEL_DATOS",
            "min",
        ),
        NIVEL_MAX_DATOS=(
            "NIVEL_DATOS",
            "max",
        ),
        NIVELES_DATOS=(
            "NIVEL_DATOS",
            unir_niveles,
        ),
        CODCLI_DATOS_DOCUMENTO=(
            "CODCLI_DATOS",
            unir_unicos,
        ),
    )
    .reset_index()
)


# ============================================================
# 7. RESUMEN DE MALLAS PARA RELACIONAR PLANES
# ============================================================

mallas = pd.read_excel(
    MALLAS,
    sheet_name="BBDD Bruta",
    dtype=object,
)

m_codcarr = buscar_columna(
    mallas,
    ["CODCARR", "CODCARPR", "COD_CAR"],
    obligatoria=True,
    contexto="Mallas/CODCARR",
)

m_plan = buscar_columna(
    mallas,
    ["CODPESTUD"],
    obligatoria=True,
    contexto="Mallas/CODPESTUD",
)

m_nivel = buscar_columna(
    mallas,
    ["NIVEL"],
    obligatoria=True,
    contexto="Mallas/NIVEL",
)

m_ramo = buscar_columna(
    mallas,
    ["CODRAMO"],
    obligatoria=True,
    contexto="Mallas/CODRAMO",
)

mc = mallas.copy()

mc["CODCARR_MALLA"] = (
    mc[m_codcarr].map(norm_codigo)
)

mc["CODPESTUD_MALLA"] = (
    mc[m_plan].map(norm_codigo)
)

mc["NIVEL_MALLA"] = pd.to_numeric(
    mc[m_nivel],
    errors="coerce",
)

mc["CODRAMO_MALLA"] = (
    mc[m_ramo].map(norm_codigo)
)

resumen_planes = (
    mc[
        mc["CODPESTUD_MALLA"].ne("")
    ]
    .groupby(
        "CODPESTUD_MALLA",
        dropna=False,
    )
    .agg(
        CODCARR_PLAN=(
            "CODCARR_MALLA",
            unir_unicos,
        ),
        NIVEL_MIN_PLAN_DIAG=(
            "NIVEL_MALLA",
            "min",
        ),
        NIVEL_MAX_PLAN_DIAG=(
            "NIVEL_MALLA",
            "max",
        ),
        RAMOS_PLAN_DIAG=(
            "CODRAMO_MALLA",
            "nunique",
        ),
    )
    .reset_index()
)

mapa_plan_carrera = dict(
    zip(
        resumen_planes["CODPESTUD_MALLA"],
        resumen_planes["CODCARR_PLAN"],
    )
)


# ============================================================
# 8. CRUZAR LOS 686 PENDIENTES
# ============================================================

diag = pendientes.merge(
    historia_documento,
    left_on="DOCUMENTO_NORM",
    right_on="DOCUMENTO_NORM_DIAG",
    how="left",
    validate="many_to_one",
)

diag = diag.merge(
    datos_documento,
    left_on="DOCUMENTO_NORM",
    right_on="DOCUMENTO_NORM_DIAG",
    how="left",
    suffixes=("_HIST", "_DATOS"),
    validate="many_to_one",
)

diag = diag.merge(
    resumen_planes.rename(
        columns={
            "CODPESTUD_MALLA":
            "CODPESTUD_RESUELTO_PLAN_DIAG"
        }
    ),
    left_on="CODPESTUD_RESUELTO",
    right_on="CODPESTUD_RESUELTO_PLAN_DIAG",
    how="left",
    validate="many_to_one",
)

if len(diag) != 686:
    raise RuntimeError(
        f"El cruce alteró los 686 pendientes: {len(diag)}."
    )


# ============================================================
# 9. ANALIZAR PLANES HISTÓRICOS
# ============================================================

def clasificar_planes_historicos(fila):
    actual = norm_codigo(
        fila.get("CODPESTUD_RESUELTO", "")
    )

    carrera_actual = norm_codigo(
        fila.get("CODCARR_PLAN", "")
    )

    planes = [
        norm_codigo(valor)
        for valor in str(
            fila.get("PLANES_HISTORICOS", "")
        ).split("|")
        if norm_codigo(valor)
    ]

    planes_misma_carrera = []
    planes_otra_carrera = []

    for plan in planes:
        carrera_plan = norm_codigo(
            mapa_plan_carrera.get(plan, "")
        )

        if (
            carrera_actual
            and carrera_plan
            and carrera_plan == carrera_actual
        ):
            planes_misma_carrera.append(plan)
        else:
            planes_otra_carrera.append(plan)

    if actual in planes:
        estado = "PLAN_ACTUAL_PRESENTE_EN_HISTORIA"
    elif len(planes_misma_carrera) == 1:
        estado = "UN_PLAN_HISTORICO_MISMA_CARRERA"
    elif len(planes_misma_carrera) > 1:
        estado = "MULTIPLES_PLANES_HISTORICOS_MISMA_CARRERA"
    elif planes:
        estado = "SOLO_PLANES_HISTORICOS_OTRA_CARRERA"
    else:
        estado = "SIN_PLANES_HISTORICOS"

    return pd.Series({
        "PLANES_HISTORICOS_MISMA_CARRERA":
        " | ".join(sorted(set(planes_misma_carrera))),
        "N_PLANES_HISTORICOS_MISMA_CARRERA":
        len(set(planes_misma_carrera)),
        "PLANES_HISTORICOS_OTRA_CARRERA":
        " | ".join(sorted(set(planes_otra_carrera))),
        "CLASIFICACION_PLAN_HISTORICO": estado,
    })


clasificacion = diag.apply(
    clasificar_planes_historicos,
    axis=1,
)

diag = pd.concat(
    [
        diag.reset_index(drop=True),
        clasificacion.reset_index(drop=True),
    ],
    axis=1,
)


# ============================================================
# 10. NIVEL DEL ÚNICO PLAN HISTÓRICO DE LA MISMA CARRERA
# ============================================================

historia_lookup = historia_plan.copy()

historia_lookup["CLAVE_HISTORIA"] = (
    historia_lookup["DOCUMENTO_NORM_DIAG"]
    + "|"
    + historia_lookup["CODPESTUD_HISTORICO"]
)

lookup_nivel = dict(
    zip(
        historia_lookup["CLAVE_HISTORIA"],
        historia_lookup["NIVEL_MAX_HISTORICO"],
    )
)

diag["PLAN_HISTORICO_MISMA_CARRERA_UNICO"] = (
    diag[
        "PLANES_HISTORICOS_MISMA_CARRERA"
    ].map(
        lambda valor: (
            norm_codigo(valor)
            if (
                valor
                and "|" not in str(valor)
            )
            else ""
        )
    )
)

diag["CLAVE_PLAN_HISTORICO_CANDIDATO"] = (
    diag["DOCUMENTO_NORM"]
    + "|"
    + diag[
        "PLAN_HISTORICO_MISMA_CARRERA_UNICO"
    ]
)

diag["NIVEL_MAX_PLAN_HISTORICO_MISMA_CARRERA"] = (
    diag["CLAVE_PLAN_HISTORICO_CANDIDATO"]
    .map(lookup_nivel)
)

diag[
    "NIVEL_MAX_PLAN_HISTORICO_MISMA_CARRERA"
] = pd.to_numeric(
    diag[
        "NIVEL_MAX_PLAN_HISTORICO_MISMA_CARRERA"
    ],
    errors="coerce",
).astype("Int64")


# ============================================================
# 11. CLASIFICACIÓN DE RESOLUCIÓN POSIBLE
# ============================================================

diag["ESTADO_DIAGNOSTICO_FINAL"] = ""
diag["NIVEL_CANDIDATO_DIAGNOSTICO"] = pd.NA
diag["METODO_CANDIDATO_DIAGNOSTICO"] = ""
diag["APTO_AUTOMATICO"] = "NO"
diag["MOTIVO_NO_AUTOMATICO"] = ""

nivel_max_plan_actual = pd.to_numeric(
    diag["NIVEL_MAX_PLAN_DIAG"],
    errors="coerce",
)

nivel_hist_misma = pd.to_numeric(
    diag[
        "NIVEL_MAX_PLAN_HISTORICO_MISMA_CARRERA"
    ],
    errors="coerce",
)

nivel_datos = pd.to_numeric(
    diag["NIVEL_MAX_DATOS"],
    errors="coerce",
)


# A. Único plan histórico de la misma carrera.
mask_unico_misma = (
    diag[
        "CLASIFICACION_PLAN_HISTORICO"
    ].eq("UN_PLAN_HISTORICO_MISMA_CARRERA")
    & nivel_hist_misma.notna()
)

diag.loc[
    mask_unico_misma,
    "NIVEL_CANDIDATO_DIAGNOSTICO",
] = nivel_hist_misma.loc[
    mask_unico_misma
].astype("Int64")

diag.loc[
    mask_unico_misma,
    "METODO_CANDIDATO_DIAGNOSTICO",
] = "UN_PLAN_HISTORICO_MISMA_CARRERA"

mask_unico_misma_cubre = (
    mask_unico_misma
    & nivel_hist_misma.ge(1)
    & nivel_hist_misma.le(nivel_max_plan_actual)
)

diag.loc[
    mask_unico_misma_cubre,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "CANDIDATO_MISMA_CARRERA_REQUIERE_VALIDACION"

diag.loc[
    mask_unico_misma_cubre,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "El nivel pertenece a otra versión del plan de la misma "
    "carrera. Se requiere confirmar la regla de transición "
    "entre versiones antes de incorporarlo."
)

mask_unico_misma_no_cubre = (
    mask_unico_misma
    & ~mask_unico_misma_cubre
)

diag.loc[
    mask_unico_misma_no_cubre,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "CONFLICTO_NIVEL_OTRO_PLAN_SUPERA_PLAN_ACTUAL"

diag.loc[
    mask_unico_misma_no_cubre,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "El nivel del plan histórico de la misma carrera supera "
    "el nivel máximo del plan actual."
)


# B. Múltiples planes históricos de la misma carrera.
mask_multi_misma = (
    diag[
        "CLASIFICACION_PLAN_HISTORICO"
    ].eq(
        "MULTIPLES_PLANES_HISTORICOS_MISMA_CARRERA"
    )
)

diag.loc[
    mask_multi_misma,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "MULTIPLES_VERSIONES_MISMA_CARRERA"

diag.loc[
    mask_multi_misma,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "Existen múltiples versiones históricas de la misma "
    "carrera; no se selecciona una automáticamente."
)


# C. Solo planes de otra carrera.
mask_otra_carrera = (
    diag[
        "CLASIFICACION_PLAN_HISTORICO"
    ].eq("SOLO_PLANES_HISTORICOS_OTRA_CARRERA")
)

diag.loc[
    mask_otra_carrera,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "TRAYECTORIA_SOLO_EN_OTRA_CARRERA"

diag.loc[
    mask_otra_carrera,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "La historia académica observada corresponde a otra "
    "carrera; no se transfiere el nivel."
)


# D. Sin historia en Hoja1, pero DatosAlumnos con carrera única.
mask_sin_historia = (
    diag[
        "CLASIFICACION_PLAN_HISTORICO"
    ].eq("SIN_PLANES_HISTORICOS")
)

mask_datos_unica = (
    mask_sin_historia
    & pd.to_numeric(
        diag["N_CARRERAS_DATOS"],
        errors="coerce",
    ).fillna(0).eq(1)
    & nivel_datos.notna()
)

diag.loc[
    mask_datos_unica,
    "NIVEL_CANDIDATO_DIAGNOSTICO",
] = nivel_datos.loc[
    mask_datos_unica
].astype("Int64")

diag.loc[
    mask_datos_unica,
    "METODO_CANDIDATO_DIAGNOSTICO",
] = "DATOSALUMNOS_DOCUMENTO_CARRERA_UNICA"

mask_datos_unica_cubre = (
    mask_datos_unica
    & nivel_datos.ge(1)
    & nivel_datos.le(nivel_max_plan_actual)
)

diag.loc[
    mask_datos_unica_cubre,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "CANDIDATO_DATOSALUMNOS_REQUIERE_VALIDACION"

diag.loc[
    mask_datos_unica_cubre,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "DatosAlumnos entrega una sola carrera y un nivel, pero "
    "falta demostrar la equivalencia entre su código de carrera "
    "y el CODPESTUD actual."
)

mask_datos_unica_no_cubre = (
    mask_datos_unica
    & ~mask_datos_unica_cubre
)

diag.loc[
    mask_datos_unica_no_cubre,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "CONFLICTO_NIVEL_DATOSALUMNOS_SUPERA_PLAN"


# E. Sin historia y múltiples carreras en DatosAlumnos.
mask_datos_multiple = (
    mask_sin_historia
    & pd.to_numeric(
        diag["N_CARRERAS_DATOS"],
        errors="coerce",
    ).fillna(0).gt(1)
    & diag["ESTADO_DIAGNOSTICO_FINAL"].eq("")
)

diag.loc[
    mask_datos_multiple,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "DATOSALUMNOS_MULTIPLES_CARRERAS"

diag.loc[
    mask_datos_multiple,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "DatosAlumnos contiene múltiples carreras para el documento."
)


# F. Sin evidencia en ninguna fuente.
mask_sin_evidencia = (
    diag["ESTADO_DIAGNOSTICO_FINAL"].eq("")
)

diag.loc[
    mask_sin_evidencia,
    "ESTADO_DIAGNOSTICO_FINAL",
] = "SIN_EVIDENCIA_ADICIONAL"

diag.loc[
    mask_sin_evidencia,
    "MOTIVO_NO_AUTOMATICO",
] = (
    "No existe evidencia adicional suficiente en Hoja1 "
    "ni en DatosAlumnos."
)


diag[
    "NIVEL_CANDIDATO_DIAGNOSTICO"
] = pd.to_numeric(
    diag["NIVEL_CANDIDATO_DIAGNOSTICO"],
    errors="coerce",
).astype("Int64")

diag["ANIO_CURRICULAR_CANDIDATO"] = (
    (
        diag["NIVEL_CANDIDATO_DIAGNOSTICO"] + 1
    ) // 2
).astype("Int64")


# ============================================================
# 12. RESÚMENES
# ============================================================

resumen_estados = (
    diag[
        "ESTADO_DIAGNOSTICO_FINAL"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

resumen_por_plan = (
    diag.groupby(
        [
            "CODIGO_UNICO",
            "CODPESTUD_RESUELTO",
            "ESTADO_DIAGNOSTICO_FINAL",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="CASOS")
)

resumen_origen = (
    diag.groupby(
        [
            "ESTADO_NIVEL_FINAL",
            "CLASIFICACION_PLAN_HISTORICO",
            "ESTADO_DIAGNOSTICO_FINAL",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="CASOS")
)

candidatos_revision = diag[
    diag["ESTADO_DIAGNOSTICO_FINAL"].isin([
        "CANDIDATO_MISMA_CARRERA_REQUIERE_VALIDACION",
        "CANDIDATO_DATOSALUMNOS_REQUIERE_VALIDACION",
    ])
].copy()

conflictos = diag[
    ~diag["ESTADO_DIAGNOSTICO_FINAL"].isin([
        "CANDIDATO_MISMA_CARRERA_REQUIERE_VALIDACION",
        "CANDIDATO_DATOSALUMNOS_REQUIERE_VALIDACION",
    ])
].copy()


# ============================================================
# 13. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_PENDIENTES",
        "RESULTADO": (
            "OK" if len(diag) == 686 else "ERROR"
        ),
        "DETALLE": len(diag),
    },
    {
        "VALIDACION": "TODOS_CON_ESTADO_DIAGNOSTICO",
        "RESULTADO": (
            "OK"
            if diag[
                "ESTADO_DIAGNOSTICO_FINAL"
            ].ne("").all()
            else "ERROR"
        ),
        "DETALLE": int(
            diag[
                "ESTADO_DIAGNOSTICO_FINAL"
            ].eq("").sum()
        ),
    },
    {
        "VALIDACION": "ASIGNACIONES_AUTOMATICAS_REALIZADAS",
        "RESULTADO": "OK",
        "DETALLE": 0,
    },
    {
        "VALIDACION": "FUENTES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "ARCHIVOS_CARGA_GENERADOS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


# ============================================================
# 14. EXPORTAR
# ============================================================

diag.to_csv(
    RESULTADOS
    / "01_DIAGNOSTICO_COMPLETO_686.tsv",
    sep="\t",
    index=False,
)

candidatos_revision.to_csv(
    RESULTADOS
    / "02_CANDIDATOS_REQUIEREN_VALIDACION.tsv",
    sep="\t",
    index=False,
)

conflictos.to_csv(
    AUDITORIAS
    / "01_CONFLICTOS_Y_SIN_EVIDENCIA.tsv",
    sep="\t",
    index=False,
)

historia_plan.to_csv(
    AUDITORIAS
    / "02_HISTORIA_DOCUMENTO_PLAN.tsv",
    sep="\t",
    index=False,
)

historia_documento.to_csv(
    AUDITORIAS
    / "03_HISTORIA_DOCUMENTO.tsv",
    sep="\t",
    index=False,
)

datos_documento.to_csv(
    AUDITORIAS
    / "04_DATOSALUMNOS_DOCUMENTO.tsv",
    sep="\t",
    index=False,
)

resumen_planes.to_csv(
    AUDITORIAS
    / "05_MAPA_CODPESTUD_CODCARR.tsv",
    sep="\t",
    index=False,
)

resumen_estados.to_csv(
    AUDITORIAS
    / "06_RESUMEN_ESTADOS.tsv",
    sep="\t",
    index=False,
)

resumen_por_plan.to_csv(
    AUDITORIAS
    / "07_RESUMEN_POR_PLAN.tsv",
    sep="\t",
    index=False,
)

resumen_origen.to_csv(
    AUDITORIAS
    / "08_RESUMEN_ORIGEN_PENDIENTE.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "09_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)

fuentes_df = pd.DataFrame([
    {
        "ROL": nombre,
        "RUTA": str(ruta),
        "SHA256": sha256(ruta),
        "TAMANO_BYTES": ruta.stat().st_size,
    }
    for nombre, ruta in fuentes.items()
])

fuentes_df.to_csv(
    AUDITORIAS
    / "10_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 15. EXCEL
# ============================================================

resumen_kpi = pd.DataFrame([
    {
        "INDICADOR": "Pendientes analizados",
        "VALOR": len(diag),
    },
    {
        "INDICADOR": "Con trayectoria en otro plan",
        "VALOR": int(
            pendientes[
                "ESTADO_NIVEL_FINAL"
            ].eq(
                "DOCUMENTO_CON_TRAYECTORIA_EN_OTRO_PLAN"
            ).sum()
        ),
    },
    {
        "INDICADOR": "Sin evidencia inicial",
        "VALOR": int(
            pendientes[
                "ESTADO_NIVEL_FINAL"
            ].eq(
                "SIN_EVIDENCIA_DE_NIVEL"
            ).sum()
        ),
    },
    {
        "INDICADOR": "Candidatos para validación",
        "VALOR": len(candidatos_revision),
    },
    {
        "INDICADOR": "Asignados automáticamente",
        "VALOR": 0,
    },
])

excel = (
    RESULTADOS
    / "DIAGNOSTICO_686_NIVELES_PENDIENTES.xlsx"
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
        sheet_name="ESTADOS",
        index=False,
    )

    candidatos_revision.to_excel(
        writer,
        sheet_name="CANDIDATOS",
        index=False,
    )

    conflictos.to_excel(
        writer,
        sheet_name="CONFLICTOS",
        index=False,
    )

    diag.to_excel(
        writer,
        sheet_name="DETALLE_686",
        index=False,
    )

    resumen_por_plan.to_excel(
        writer,
        sheet_name="POR_PLAN",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
        index=False,
    )

    fuentes_df.to_excel(
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
                48,
            )


# ============================================================
# 16. MANIFIESTO Y REPORTE
# ============================================================

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "pendientes_analizados": len(diag),
    "candidatos_requieren_validacion": len(
        candidatos_revision
    ),
    "asignaciones_automaticas": 0,
    "criterio": (
        "No transferir nivel entre planes sin demostrar "
        "compatibilidad de carrera, versión y trayectoria."
    ),
    "fuentes_modificadas": False,
    "precargas_modificadas": False,
    "archivo_final_carga_generado": False,
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

lineas = [
    "DIAGNOSTICO DE 686 NIVELES PENDIENTES",
    "=" * 90,
    f"Pendientes analizados: {len(diag)}",
    f"Candidatos para validación: {len(candidatos_revision)}",
    "Asignaciones automáticas: 0",
    "",
    "Estados:",
]

for _, fila in resumen_estados.iterrows():
    lineas.append(
        f"- {fila['ESTADO']}: {fila['CASOS']}"
    )

lineas.extend([
    "",
    f"Excel: {excel}",
    f"Carpeta: {SALIDA}",
    "Fuentes modificadas: NO",
    "Archivo final de carga generado: NO",
])

(REPORTES / "RESUMEN_EJECUCION.txt").write_text(
    "\n".join(lineas),
    encoding="utf-8",
)


# ============================================================
# 17. TERMINAL
# ============================================================

print()
print("=" * 96)
print("DIAGNOSTICO DE LOS 686 NIVELES PENDIENTES")
print("=" * 96)
print(f"Pendientes analizados: {len(diag)}")
print()
print("RESULTADO")
print("-" * 96)

for _, fila in resumen_estados.iterrows():
    print(
        f"{fila['ESTADO']}: {fila['CASOS']}"
    )

print()
print(
    "Candidatos que requieren validación: "
    f"{len(candidatos_revision)}"
)
print("Asignaciones automáticas realizadas: 0")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print()
print("Fuentes modificadas: NO")
print("Precargas modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 96)
