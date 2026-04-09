#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

TRAZA_5809 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "RECALCULO_MAPA_43_CARRERAS_20260702_000938"
    / "06_5809_TRAZABILIDAD_RECALCULADA.tsv"
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

DIAGNOSTICO_CREDITOS = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "DIAGNOSTICO_CREDITOS_MALLAS_20260702_001339"
    / "01_RESUMEN.tsv"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"RECALCULO_NIVELES_2371_CORREGIDO_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in (RESULTADOS, AUDITORIAS, REPORTES):
    carpeta.mkdir(parents=True, exist_ok=True)


def norm_col(valor):
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
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


def normalizar_numero(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in {
        "",
        "nan",
        "none",
        "null",
        "n/a",
        "na",
    }:
        return ""

    texto = texto.replace("\u00a0", "")
    texto = texto.replace(" ", "")

    if "," in texto and "." not in texto:
        texto = texto.replace(",", ".")
    elif "," in texto and "." in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")

    return texto


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
    return " | ".join(
        sorted({
            norm_codigo(valor)
            for valor in serie
            if norm_codigo(valor)
        })
    )


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
    "TRAZA_5809": TRAZA_5809,
    "PROMEDIOS": PROMEDIOS,
    "MALLAS": MALLAS,
    "DIAGNOSTICO_CREDITOS": DIAGNOSTICO_CREDITOS,
}

for nombre, ruta in fuentes.items():
    if not ruta.exists():
        raise RuntimeError(
            f"No existe fuente requerida {nombre}: {ruta}"
        )


# ============================================================
# 2. UNIVERSO RECTOR
# ============================================================

base = pd.read_csv(
    TRAZA_5809,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(base) != 2371:
    raise RuntimeError(
        f"Universo 5809 inesperado: {len(base)}."
    )

if "ID_FILA_5809" not in base.columns:
    raise RuntimeError(
        "Falta ID_FILA_5809."
    )

if base["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "ID_FILA_5809 contiene duplicados."
    )

base["DOCUMENTO_NORM"] = (
    base["DOCUMENTO_NORM"].map(norm_documento)
)

base["CODPESTUD_RESUELTO"] = (
    base["CODPESTUD_RESUELTO"].map(norm_codigo)
)

if base["CODPESTUD_RESUELTO"].eq("").any():
    raise RuntimeError(
        "Existen estudiantes sin CODPESTUD resuelto."
    )

planes_proceso = {
    valor
    for valor in base["CODPESTUD_RESUELTO"]
    if valor
}

if len(planes_proceso) != 16:
    raise RuntimeError(
        f"Se esperaban 16 CODPESTUD y se observaron "
        f"{len(planes_proceso)}."
    )


# ============================================================
# 3. HOJA1: DOCUMENTO + PLAN + NIVEL
# ============================================================

hoja1 = pd.read_excel(
    PROMEDIOS,
    sheet_name="Hoja1",
    dtype=object,
)

h_documento = buscar_columna(
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

h_codramo = buscar_columna(
    hoja1,
    ["CODRAMO", "CODIGO_ASIGNATURA"],
)

h = hoja1.copy()

h["DOCUMENTO_NORM"] = (
    h[h_documento].map(norm_documento)
)

h["CODPESTUD_HOJA1"] = (
    h[h_plan].map(norm_codigo)
)

h["NIVEL_HOJA1_NUM"] = pd.to_numeric(
    h[h_nivel],
    errors="coerce",
)

h["CODCLI_HOJA1"] = (
    h[h_codcli].map(norm_codigo)
    if h_codcli
    else ""
)

h["CODRAMO_HOJA1"] = (
    h[h_codramo].map(norm_codigo)
    if h_codramo
    else ""
)

h_valida = h[
    h["DOCUMENTO_NORM"].ne("")
    & h["CODPESTUD_HOJA1"].ne("")
].copy()

evidencia_exacta = (
    h_valida.groupby(
        [
            "DOCUMENTO_NORM",
            "CODPESTUD_HOJA1",
        ],
        dropna=False,
    )
    .agg(
        NIVEL_MIN_HOJA1=(
            "NIVEL_HOJA1_NUM",
            "min",
        ),
        NIVEL_MAX_HOJA1=(
            "NIVEL_HOJA1_NUM",
            "max",
        ),
        NIVELES_HOJA1=(
            "NIVEL_HOJA1_NUM",
            unir_niveles,
        ),
        REGISTROS_HOJA1=(
            "CODPESTUD_HOJA1",
            "size",
        ),
        RAMOS_DISTINTOS_HOJA1=(
            "CODRAMO_HOJA1",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CODCLI_HOJA1=(
            "CODCLI_HOJA1",
            unir_unicos,
        ),
    )
    .reset_index()
)

trayectorias = (
    h_valida.groupby(
        "DOCUMENTO_NORM",
        dropna=False,
    )
    .agg(
        N_PLANES_DOCUMENTO=(
            "CODPESTUD_HOJA1",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        PLANES_DOCUMENTO=(
            "CODPESTUD_HOJA1",
            unir_unicos,
        ),
        NIVEL_MAX_GLOBAL_DOCUMENTO=(
            "NIVEL_HOJA1_NUM",
            "max",
        ),
        CODCLI_DOCUMENTO=(
            "CODCLI_HOJA1",
            unir_unicos,
        ),
    )
    .reset_index()
)


# ============================================================
# 4. MALLAS: FILTRAR PRIMERO A LOS 16 PLANES
# ============================================================

mallas = pd.read_excel(
    MALLAS,
    sheet_name="BBDD Bruta",
    dtype=object,
)

m_plan = buscar_columna(
    mallas,
    ["CODPESTUD"],
    obligatoria=True,
    contexto="Mallas/CODPESTUD",
)

m_ramo = buscar_columna(
    mallas,
    ["CODRAMO"],
    obligatoria=True,
    contexto="Mallas/CODRAMO",
)

m_nivel = buscar_columna(
    mallas,
    ["NIVEL"],
    obligatoria=True,
    contexto="Mallas/NIVEL",
)

m_credito = buscar_columna(
    mallas,
    ["CREDITO", "CREDITOS"],
    obligatoria=True,
    contexto="Mallas/CREDITO",
)

mc = mallas.copy()

mc["CODPESTUD_NORM"] = (
    mc[m_plan].map(norm_codigo)
)

mc["CODRAMO_NORM"] = (
    mc[m_ramo].map(norm_codigo)
)

# Corrección central:
# se limita la validación a los 16 planes del proceso.
mc = mc[
    mc["CODPESTUD_NORM"].isin(
        planes_proceso
    )
].copy()

mc["NIVEL_TEXTO"] = (
    mc[m_nivel]
    .fillna("")
    .astype(str)
    .str.strip()
)

mc["NIVEL_NUM"] = pd.to_numeric(
    mc["NIVEL_TEXTO"],
    errors="coerce",
)

mc["CREDITO_TEXTO"] = (
    mc[m_credito].map(normalizar_numero)
)

mc["CREDITO_NUM"] = pd.to_numeric(
    mc["CREDITO_TEXTO"],
    errors="coerce",
)

mc = mc[
    mc["CODPESTUD_NORM"].ne("")
    & mc["CODRAMO_NORM"].ne("")
    & mc["NIVEL_TEXTO"].ne("")
].copy()

niveles_invalidos = mc[
    mc["NIVEL_NUM"].isna()
].copy()

creditos_vacios = mc[
    mc["CREDITO_TEXTO"].eq("")
].copy()

creditos_invalidos = mc[
    mc["CREDITO_TEXTO"].ne("")
    & mc["CREDITO_NUM"].isna()
].copy()

if not niveles_invalidos.empty:
    raise RuntimeError(
        f"Existen {len(niveles_invalidos)} niveles inválidos "
        "dentro de los 16 planes."
    )

if not creditos_vacios.empty:
    raise RuntimeError(
        f"Existen {len(creditos_vacios)} créditos vacíos "
        "dentro de los 16 planes."
    )

if not creditos_invalidos.empty:
    raise RuntimeError(
        f"Existen {len(creditos_invalidos)} créditos inválidos "
        "dentro de los 16 planes."
    )

if len(mc) != 1347:
    raise RuntimeError(
        f"Filas relevantes de malla inesperadas: "
        f"{len(mc)}; esperado según diagnóstico: 1347."
    )

llave_canonica = [
    "CODPESTUD_NORM",
    "CODRAMO_NORM",
    "NIVEL_NUM",
    "CREDITO_NUM",
]

malla_canonica = mc.drop_duplicates(
    llave_canonica,
    keep="first",
).copy()

malla_canonica["ANIO_CURRICULAR"] = (
    (malla_canonica["NIVEL_NUM"] + 1) // 2
).astype("Int64")

resumen_malla = (
    malla_canonica.groupby(
        "CODPESTUD_NORM",
        dropna=False,
    )
    .agg(
        NIVEL_MIN_PLAN=(
            "NIVEL_NUM",
            "min",
        ),
        NIVEL_MAX_PLAN=(
            "NIVEL_NUM",
            "max",
        ),
        RAMOS_DISTINTOS_PLAN=(
            "CODRAMO_NORM",
            "nunique",
        ),
        TOTAL_UNIDADES_PLAN=(
            "CREDITO_NUM",
            "sum",
        ),
    )
    .reset_index()
)

resumen_malla["ANIO_MAX_PLAN"] = (
    (resumen_malla["NIVEL_MAX_PLAN"] + 1) // 2
).astype("Int64")

if len(resumen_malla) != 16:
    raise RuntimeError(
        f"Resumen de mallas contiene "
        f"{len(resumen_malla)} planes; esperados: 16."
    )


# ============================================================
# 5. CRUZAR EVIDENCIA
# ============================================================

resultado = base.merge(
    evidencia_exacta,
    left_on=[
        "DOCUMENTO_NORM",
        "CODPESTUD_RESUELTO",
    ],
    right_on=[
        "DOCUMENTO_NORM",
        "CODPESTUD_HOJA1",
    ],
    how="left",
    validate="many_to_one",
)

resultado = resultado.merge(
    trayectorias,
    on="DOCUMENTO_NORM",
    how="left",
    validate="many_to_one",
)

resultado = resultado.merge(
    resumen_malla,
    left_on="CODPESTUD_RESUELTO",
    right_on="CODPESTUD_NORM",
    how="left",
    validate="many_to_one",
)

if len(resultado) != 2371:
    raise RuntimeError(
        "El cruce alteró el universo de 2.371 filas."
    )

if resultado["CODPESTUD_NORM"].isna().any():
    raise RuntimeError(
        "Existen estudiantes cuyo CODPESTUD no aparece "
        "en el resumen de los 16 planes."
    )


# ============================================================
# 6. RESOLUCIÓN CONSERVADORA DE NIVEL
# ============================================================

resultado["NIVEL_FINAL"] = pd.NA
resultado["ANIO_CURRICULAR_FINAL"] = pd.NA
resultado["ESTADO_NIVEL_FINAL"] = ""
resultado["METODO_RESOLUCION_NIVEL"] = ""
resultado["FUENTE_NIVEL_FINAL"] = ""
resultado["OBSERVACION_NIVEL"] = ""

nivel_observado = pd.to_numeric(
    resultado["NIVEL_MAX_HOJA1"],
    errors="coerce",
)

nivel_max_plan = pd.to_numeric(
    resultado["NIVEL_MAX_PLAN"],
    errors="coerce",
)

mask_exacta = (
    resultado["CODPESTUD_HOJA1"]
    .fillna("")
    .ne("")
    & nivel_observado.notna()
)

mask_valida = (
    mask_exacta
    & nivel_observado.ge(1)
    & nivel_observado.le(nivel_max_plan)
)

resultado.loc[
    mask_valida,
    "NIVEL_FINAL",
] = nivel_observado.loc[
    mask_valida
].astype("Int64")

resultado.loc[
    mask_valida,
    "ANIO_CURRICULAR_FINAL",
] = (
    (
        nivel_observado.loc[
            mask_valida
        ].astype("Int64") + 1
    ) // 2
)

resultado.loc[
    mask_valida,
    "ESTADO_NIVEL_FINAL",
] = "NIVEL_VALIDADO_PLAN_EXACTO"

resultado.loc[
    mask_valida,
    "METODO_RESOLUCION_NIVEL",
] = "DOCUMENTO_MAS_CODPESTUD_EXACTO"

resultado.loc[
    mask_valida,
    "FUENTE_NIVEL_FINAL",
] = "PROMEDIOSDEALUMNOS::Hoja1"

resultado.loc[
    mask_valida,
    "OBSERVACION_NIVEL",
] = (
    "Nivel máximo observado para documento y CODPESTUD "
    "exactos; no supera el máximo físico de la malla."
)

mask_supera = (
    mask_exacta
    & nivel_observado.gt(nivel_max_plan)
)

resultado.loc[
    mask_supera,
    "ESTADO_NIVEL_FINAL",
] = "CONFLICTO_NIVEL_SUPERA_PLAN"

resultado.loc[
    mask_supera,
    "METODO_RESOLUCION_NIVEL",
] = "DOCUMENTO_MAS_CODPESTUD_EXACTO"

resultado.loc[
    mask_supera,
    "FUENTE_NIVEL_FINAL",
] = "PROMEDIOSDEALUMNOS::Hoja1"

resultado.loc[
    mask_supera,
    "OBSERVACION_NIVEL",
] = (
    "El nivel observado supera el nivel máximo de la malla."
)

mask_otro_plan = (
    resultado["ESTADO_NIVEL_FINAL"].eq("")
    & pd.to_numeric(
        resultado["N_PLANES_DOCUMENTO"],
        errors="coerce",
    ).fillna(0).gt(0)
)

resultado.loc[
    mask_otro_plan,
    "ESTADO_NIVEL_FINAL",
] = "DOCUMENTO_CON_TRAYECTORIA_EN_OTRO_PLAN"

resultado.loc[
    mask_otro_plan,
    "METODO_RESOLUCION_NIVEL",
] = "NO_ASIGNADO"

resultado.loc[
    mask_otro_plan,
    "FUENTE_NIVEL_FINAL",
] = "PROMEDIOSDEALUMNOS::Hoja1"

resultado.loc[
    mask_otro_plan,
    "OBSERVACION_NIVEL",
] = (
    "El documento tiene trayectoria observada, pero no "
    "coincide con el CODPESTUD resuelto para esta fila."
)

mask_sin_evidencia = (
    resultado["ESTADO_NIVEL_FINAL"].eq("")
)

resultado.loc[
    mask_sin_evidencia,
    "ESTADO_NIVEL_FINAL",
] = "SIN_EVIDENCIA_DE_NIVEL"

resultado.loc[
    mask_sin_evidencia,
    "METODO_RESOLUCION_NIVEL",
] = "NO_ASIGNADO"

resultado.loc[
    mask_sin_evidencia,
    "OBSERVACION_NIVEL",
] = (
    "No existe evidencia exacta de nivel para "
    "documento y CODPESTUD."
)

resultado["NIVEL_FINAL"] = pd.to_numeric(
    resultado["NIVEL_FINAL"],
    errors="coerce",
).astype("Int64")

resultado["ANIO_CURRICULAR_FINAL"] = pd.to_numeric(
    resultado["ANIO_CURRICULAR_FINAL"],
    errors="coerce",
).astype("Int64")

resultado["REGLA_TECNICA_NIVEL_ANIO"] = (
    "ANIO_CURRICULAR=TECHO(NIVEL/2)"
)

resultado["NIVEL_ANIO_ES_REGLA_OFICIAL"] = "NO"

resultado["ESTADO_TRAZABILIDAD_FINAL"] = (
    resultado["ESTADO_NIVEL_FINAL"]
)

resultado.loc[
    resultado["ESTADO_NIVEL_FINAL"].eq(
        "NIVEL_VALIDADO_PLAN_EXACTO"
    ),
    "ESTADO_TRAZABILIDAD_FINAL",
] = "TRAZABLE_PLAN_MALLA_NIVEL"


# ============================================================
# 7. RESÚMENES
# ============================================================

resumen_estados = (
    resultado[
        "ESTADO_TRAZABILIDAD_FINAL"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

resumen_por_plan = (
    resultado.groupby(
        [
            "CODIGO_UNICO",
            "CODPESTUD_RESUELTO",
        ],
        dropna=False,
    )
    .agg(
        ESTUDIANTES=(
            "ID_FILA_5809",
            "size",
        ),
        NIVELES_VALIDADOS=(
            "ESTADO_NIVEL_FINAL",
            lambda serie: int(
                serie.eq(
                    "NIVEL_VALIDADO_PLAN_EXACTO"
                ).sum()
            ),
        ),
        PENDIENTES_O_CONFLICTOS=(
            "ESTADO_NIVEL_FINAL",
            lambda serie: int(
                (~serie.eq(
                    "NIVEL_VALIDADO_PLAN_EXACTO"
                )).sum()
            ),
        ),
        NIVEL_MIN_VALIDADO=(
            "NIVEL_FINAL",
            "min",
        ),
        NIVEL_MAX_VALIDADO=(
            "NIVEL_FINAL",
            "max",
        ),
    )
    .reset_index()
)

resumen_por_plan["COBERTURA_NIVEL_PCT"] = (
    resumen_por_plan["NIVELES_VALIDADOS"]
    / resumen_por_plan["ESTUDIANTES"]
    * 100
).round(2)

trazables = resultado[
    resultado["ESTADO_NIVEL_FINAL"].eq(
        "NIVEL_VALIDADO_PLAN_EXACTO"
    )
].copy()

pendientes = resultado[
    ~resultado["ESTADO_NIVEL_FINAL"].eq(
        "NIVEL_VALIDADO_PLAN_EXACTO"
    )
].copy()

total = len(resultado)
validados = len(trazables)
pendientes_total = len(pendientes)

cobertura = round(
    validados / total * 100,
    2,
)


# ============================================================
# 8. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_5809",
        "RESULTADO": (
            "OK" if total == 2371 else "ERROR"
        ),
        "DETALLE": total,
    },
    {
        "VALIDACION": "PLANES_PROCESO",
        "RESULTADO": (
            "OK"
            if len(planes_proceso) == 16
            else "ERROR"
        ),
        "DETALLE": len(planes_proceso),
    },
    {
        "VALIDACION": "FILAS_MALLA_RELEVANTES",
        "RESULTADO": (
            "OK" if len(mc) == 1347 else "ERROR"
        ),
        "DETALLE": len(mc),
    },
    {
        "VALIDACION": "CREDITOS_VACIOS_RELEVANTES",
        "RESULTADO": (
            "OK"
            if creditos_vacios.empty
            else "ERROR"
        ),
        "DETALLE": len(creditos_vacios),
    },
    {
        "VALIDACION": "CREDITOS_INVALIDOS_RELEVANTES",
        "RESULTADO": (
            "OK"
            if creditos_invalidos.empty
            else "ERROR"
        ),
        "DETALLE": len(creditos_invalidos),
    },
    {
        "VALIDACION": "TODOS_CON_ESTADO_FINAL",
        "RESULTADO": (
            "OK"
            if resultado[
                "ESTADO_TRAZABILIDAD_FINAL"
            ].ne("").all()
            else "ERROR"
        ),
        "DETALLE": int(
            resultado[
                "ESTADO_TRAZABILIDAD_FINAL"
            ].eq("").sum()
        ),
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
# 9. EXPORTACIÓN
# ============================================================

resultado.to_csv(
    RESULTADOS
    / "01_5809_TRAZABILIDAD_PLAN_MALLA_NIVEL.tsv",
    sep="\t",
    index=False,
)

trazables.to_csv(
    RESULTADOS
    / "02_5809_TRAZABLES_PLAN_MALLA_NIVEL.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    AUDITORIAS
    / "01_PENDIENTES_O_CONFLICTOS_NIVEL.tsv",
    sep="\t",
    index=False,
)

evidencia_exacta.to_csv(
    AUDITORIAS
    / "02_EVIDENCIA_DOCUMENTO_PLAN_NIVEL.tsv",
    sep="\t",
    index=False,
)

malla_canonica.to_csv(
    AUDITORIAS
    / "03_MALLA_CANONICA_16_PLANES.tsv",
    sep="\t",
    index=False,
)

resumen_malla.to_csv(
    AUDITORIAS
    / "04_RESUMEN_16_PLANES.tsv",
    sep="\t",
    index=False,
)

resumen_estados.to_csv(
    AUDITORIAS
    / "05_RESUMEN_ESTADOS.tsv",
    sep="\t",
    index=False,
)

resumen_por_plan.to_csv(
    AUDITORIAS
    / "06_COBERTURA_POR_PLAN.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "07_VALIDACIONES.tsv",
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
    / "08_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)

resumen_kpi = pd.DataFrame([
    {
        "INDICADOR": "Universo 5809",
        "VALOR": total,
    },
    {
        "INDICADOR": "CODPESTUD distintos",
        "VALOR": len(planes_proceso),
    },
    {
        "INDICADOR": "Filas de malla relevantes",
        "VALOR": len(mc),
    },
    {
        "INDICADOR": "Niveles validados",
        "VALOR": validados,
    },
    {
        "INDICADOR": "Pendientes o conflictos",
        "VALOR": pendientes_total,
    },
    {
        "INDICADOR": "Cobertura de nivel",
        "VALOR": f"{cobertura}%",
    },
    {
        "INDICADOR": "Archivo definitivo de carga",
        "VALOR": "NO GENERADO",
    },
])

excel = (
    RESULTADOS
    / "RECALCULO_NIVELES_2371_CORREGIDO.xlsx"
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

    resumen_por_plan.to_excel(
        writer,
        sheet_name="COBERTURA_POR_PLAN",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="5809_TRAZABILIDAD",
        index=False,
    )

    trazables.to_excel(
        writer,
        sheet_name="TRAZABLES",
        index=False,
    )

    pendientes.to_excel(
        writer,
        sheet_name="PENDIENTES",
        index=False,
    )

    resumen_malla.to_excel(
        writer,
        sheet_name="RESUMEN_MALLAS",
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
# 10. MANIFIESTO Y REPORTE
# ============================================================

estado = (
    "NIVELES_100_PORCIENTO_VALIDADOS"
    if pendientes_total == 0
    else "NIVELES_PARCIALMENTE_VALIDADOS"
)

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "universo": total,
    "planes_proceso": len(planes_proceso),
    "filas_malla_relevantes": len(mc),
    "creditos_vacios_relevantes": len(
        creditos_vacios
    ),
    "creditos_invalidos_relevantes": len(
        creditos_invalidos
    ),
    "niveles_validados": validados,
    "pendientes_o_conflictos": pendientes_total,
    "cobertura_nivel_pct": cobertura,
    "estado": estado,
    "metodo_nivel": (
        "Documento + CODPESTUD exactos en Hoja1; "
        "nivel máximo observado dentro del rango de la malla."
    ),
    "regla_tecnica_anio": (
        "ANIO_CURRICULAR=TECHO(NIVEL/2)"
    ),
    "es_regla_oficial_avance": False,
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
    "RECALCULO DE NIVELES 2.371 ESTUDIANTES",
    "=" * 90,
    f"Universo: {total}",
    f"Planes: {len(planes_proceso)}",
    f"Filas de malla relevantes: {len(mc)}",
    f"Niveles validados: {validados}",
    f"Pendientes o conflictos: {pendientes_total}",
    f"Cobertura: {cobertura}%",
    "",
    "Estados:",
]

for _, fila in resumen_estados.iterrows():
    lineas.append(
        f"- {fila['ESTADO']}: {fila['CASOS']}"
    )

lineas.extend([
    "",
    f"Estado: {estado}",
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
# 11. TERMINAL
# ============================================================

print()
print("=" * 94)
print("RECALCULO CORREGIDO DE NIVELES DE 2.371 ESTUDIANTES")
print("=" * 94)
print(f"Universo 5809: {total}")
print(f"CODPESTUD distintos: {len(planes_proceso)}")
print(f"Filas de malla relevantes: {len(mc)}")
print("Créditos vacíos relevantes: 0")
print("Créditos inválidos relevantes: 0")
print()
print("RESULTADO")
print("-" * 94)

for _, fila in resumen_estados.iterrows():
    print(
        f"{fila['ESTADO']}: {fila['CASOS']}"
    )

print()
print(
    f"Niveles validados: "
    f"{validados}/{total} ({cobertura}%)"
)
print(
    f"Pendientes o conflictos: "
    f"{pendientes_total}"
)
print()
print(f"Estado: {estado}")
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print()
print("Fuentes modificadas: NO")
print("Precargas modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 94)
