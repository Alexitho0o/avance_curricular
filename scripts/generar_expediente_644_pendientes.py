#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json

import pandas as pd


# ============================================================
# CONTEXTO
# ============================================================

RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

PENDIENTES_644 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "INCORPORACION_42_NIVELES_VALIDADOS_20260702_011152"
    / "03_AUDITORIAS"
    / "01_5809_PENDIENTES_644.tsv"
)

DIAGNOSTICO_IDENTIDAD_124 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "DIAGNOSTICO_124_POR_IDENTIDAD_20260702_002433"
    / "01_DIAGNOSTICO_COMPLETO_124_IDENTIDAD.tsv"
)

VALIDACION_56 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "VALIDACION_56_IDENTIDAD_CARRERA_20260702_002659"
    / "01_VALIDACION_COMPLETA_56.tsv"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"EXPEDIENTE_REVISION_644_{timestamp}"
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

def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def texto(serie):
    return serie.fillna("").astype(str).str.strip()


def asegurar_columna(df, columna, valor=""):
    if columna not in df.columns:
        df[columna] = valor

    return df


# ============================================================
# 1. VALIDAR FUENTES
# ============================================================

fuentes = {
    "PENDIENTES_644": PENDIENTES_644,
    "DIAGNOSTICO_IDENTIDAD_124": DIAGNOSTICO_IDENTIDAD_124,
    "VALIDACION_56": VALIDACION_56,
}

for nombre, ruta in fuentes.items():
    if not ruta.exists():
        raise RuntimeError(
            f"No existe la fuente requerida {nombre}: {ruta}"
        )


# ============================================================
# 2. LEER FUENTES
# ============================================================

pendientes = pd.read_csv(
    PENDIENTES_644,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

identidad = pd.read_csv(
    DIAGNOSTICO_IDENTIDAD_124,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

validacion_56 = pd.read_csv(
    VALIDACION_56,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)


# ============================================================
# 3. VALIDACIONES DE UNIVERSO
# ============================================================

if len(pendientes) != 644:
    raise RuntimeError(
        f"Pendientes inesperados: {len(pendientes)}; "
        "esperados: 644."
    )

for nombre, df in {
    "pendientes": pendientes,
    "identidad": identidad,
    "validacion_56": validacion_56,
}.items():
    if "ID_FILA_5809" not in df.columns:
        raise RuntimeError(
            f"Falta ID_FILA_5809 en {nombre}."
        )

    if df["ID_FILA_5809"].duplicated().any():
        raise RuntimeError(
            f"Existen ID_FILA_5809 duplicados en {nombre}."
        )


# ============================================================
# 4. PREPARAR DIAGNÓSTICOS AUXILIARES
# ============================================================

columnas_identidad = [
    "ID_FILA_5809",
    "ESTADO_IDENTIDAD",
    "NIVEL_CANDIDATO_IDENTIDAD",
    "RUT_DATOS_IDENTIDAD",
    "CODCLI_DATOS_IDENTIDAD",
    "CARRERAS_DATOS_IDENTIDAD",
    "NIVELES_DATOS_IDENTIDAD",
    "N_RUT_IDENTIDAD",
    "N_CODCLI_IDENTIDAD",
    "N_CARRERAS_IDENTIDAD",
    "N_NIVELES_IDENTIDAD",
    "MOTIVO_PENDIENTE_IDENTIDAD",
]

for columna in columnas_identidad:
    asegurar_columna(identidad, columna)

identidad_aporte = identidad[
    columnas_identidad
].copy()

columnas_validacion = [
    "ID_FILA_5809",
    "ESTADO_VALIDACION_56",
    "CODCARPR_DATOS_NORM",
    "CODCARR_PLAN_NORM",
    "NIVEL_CANDIDATO_NUM",
    "NIVEL_MAX_PLAN_NUM",
    "MOTIVO_VALIDACION",
]

for columna in columnas_validacion:
    asegurar_columna(validacion_56, columna)

validacion_aporte = validacion_56[
    columnas_validacion
].copy()


# ============================================================
# 5. CONSOLIDAR
# ============================================================

resultado = pendientes.merge(
    identidad_aporte,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
    suffixes=("", "_IDENTIDAD"),
)

resultado = resultado.merge(
    validacion_aporte,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
    suffixes=("", "_VALIDACION56"),
)

if len(resultado) != 644:
    raise RuntimeError(
        "La consolidación alteró el universo de 644 casos."
    )


# ============================================================
# COALESCENCIA DE COLUMNAS DERIVADAS
# ============================================================
#
# Las fuentes consolidadas pueden contener columnas homónimas.
# Pandas agrega sufijos durante los merge. Se recupera para cada
# campo el primer valor no vacío, priorizando el aporte específico
# más reciente. No se modifica ninguna fuente original.

def coalescer_columnas(
    df,
    destino,
    candidatas,
):
    existentes = [
        columna
        for columna in candidatas
        if columna in df.columns
    ]

    if not existentes:
        df[destino] = ""
        return

    consolidada = pd.Series(
        "",
        index=df.index,
        dtype="string",
    )

    for columna in existentes:
        valores = (
            df[columna]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        mask = (
            consolidada.fillna("").eq("")
            & valores.ne("")
        )

        consolidada.loc[mask] = valores.loc[mask]

    df[destino] = consolidada.fillna("").astype(str)


coalescer_columnas(
    resultado,
    "ESTADO_IDENTIDAD",
    [
        "ESTADO_IDENTIDAD_IDENTIDAD",
        "ESTADO_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "NIVEL_CANDIDATO_IDENTIDAD",
    [
        "NIVEL_CANDIDATO_IDENTIDAD_IDENTIDAD",
        "NIVEL_CANDIDATO_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "RUT_DATOS_IDENTIDAD",
    [
        "RUT_DATOS_IDENTIDAD_IDENTIDAD",
        "RUT_DATOS_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "CODCLI_DATOS_IDENTIDAD",
    [
        "CODCLI_DATOS_IDENTIDAD_IDENTIDAD",
        "CODCLI_DATOS_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "CARRERAS_DATOS_IDENTIDAD",
    [
        "CARRERAS_DATOS_IDENTIDAD_IDENTIDAD",
        "CARRERAS_DATOS_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "NIVELES_DATOS_IDENTIDAD",
    [
        "NIVELES_DATOS_IDENTIDAD_IDENTIDAD",
        "NIVELES_DATOS_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "MOTIVO_PENDIENTE_IDENTIDAD",
    [
        "MOTIVO_PENDIENTE_IDENTIDAD_IDENTIDAD",
        "MOTIVO_PENDIENTE_IDENTIDAD",
    ],
)

coalescer_columnas(
    resultado,
    "ESTADO_VALIDACION_56",
    [
        "ESTADO_VALIDACION_56_VALIDACION56",
        "ESTADO_VALIDACION_56",
    ],
)

coalescer_columnas(
    resultado,
    "CODCARPR_DATOS_NORM",
    [
        "CODCARPR_DATOS_NORM_VALIDACION56",
        "CODCARPR_DATOS_NORM",
    ],
)

coalescer_columnas(
    resultado,
    "CODCARR_PLAN_NORM",
    [
        "CODCARR_PLAN_NORM_VALIDACION56",
        "CODCARR_PLAN_NORM",
    ],
)

coalescer_columnas(
    resultado,
    "NIVEL_CANDIDATO_NUM",
    [
        "NIVEL_CANDIDATO_NUM_VALIDACION56",
        "NIVEL_CANDIDATO_NUM",
    ],
)

coalescer_columnas(
    resultado,
    "NIVEL_MAX_PLAN_NUM",
    [
        "NIVEL_MAX_PLAN_NUM_VALIDACION56",
        "NIVEL_MAX_PLAN_NUM",
    ],
)

coalescer_columnas(
    resultado,
    "MOTIVO_VALIDACION",
    [
        "MOTIVO_VALIDACION_VALIDACION56",
        "MOTIVO_VALIDACION",
    ],
)

for columna in [
    "ESTADO_NIVEL_FINAL",
    "ESTADO_IDENTIDAD",
    "ESTADO_VALIDACION_56",
]:
    asegurar_columna(resultado, columna)


# ============================================================
# AUDITORÍA DE ESTADOS CONSOLIDADOS
# ============================================================

auditoria_estados = (
    resultado[
        [
            "ESTADO_NIVEL_FINAL",
            "ESTADO_IDENTIDAD",
            "ESTADO_VALIDACION_56",
        ]
    ]
    .value_counts(dropna=False)
    .reset_index(name="CASOS")
)

auditoria_estados.to_csv(
    AUDITORIAS
    / "00_ESTADOS_DESPUES_COALESCENCIA.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 6. CLASIFICACIÓN FINAL DEL EXPEDIENTE
# ============================================================

resultado["CATEGORIA_REVISION_644"] = ""
resultado["PRIORIDAD_REVISION"] = ""
resultado["ACCION_REQUERIDA"] = ""
resultado["PUEDE_INCORPORARSE"] = "NO"
resultado["NIVEL_PROPUESTO"] = pd.NA
resultado["RESPALDO_ACTUAL"] = ""
resultado["OBSERVACION_EXPEDIENTE"] = ""


# ------------------------------------------------------------
# A. Trayectoria exclusivamente en otra carrera
# ------------------------------------------------------------

mask_otra_carrera = texto(
    resultado["ESTADO_NIVEL_FINAL"]
).eq(
    "DOCUMENTO_CON_TRAYECTORIA_EN_OTRO_PLAN"
)

resultado.loc[
    mask_otra_carrera,
    "CATEGORIA_REVISION_644",
] = "TRAYECTORIA_EXCLUSIVAMENTE_EN_OTRA_CARRERA"

resultado.loc[
    mask_otra_carrera,
    "PRIORIDAD_REVISION",
] = "P3_BAJA"

resultado.loc[
    mask_otra_carrera,
    "ACCION_REQUERIDA",
] = (
    "Mantener pendiente. No transferir el nivel de otra carrera. "
    "Requiere fuente institucional del plan vigente."
)

resultado.loc[
    mask_otra_carrera,
    "RESPALDO_ACTUAL",
] = "HISTORIA_ACADEMICA_EN_OTRO_PLAN"

resultado.loc[
    mask_otra_carrera,
    "OBSERVACION_EXPEDIENTE",
] = (
    "Existe trayectoria académica observada, pero solamente "
    "en una carrera distinta de la carrera informada en 5809."
)


# ------------------------------------------------------------
# B. CODCARPR distinto del CODCARR del plan
# ------------------------------------------------------------

mask_carrera_distinta = texto(
    resultado["ESTADO_VALIDACION_56"]
).eq(
    "CODCARPR_DISTINTO_DE_CODCARR_PLAN"
)

resultado.loc[
    mask_carrera_distinta,
    "CATEGORIA_REVISION_644",
] = "CONFLICTO_CARRERA_DATOSALUMNOS_VS_PLAN"

resultado.loc[
    mask_carrera_distinta,
    "PRIORIDAD_REVISION",
] = "P1_ALTA"

resultado.loc[
    mask_carrera_distinta,
    "ACCION_REQUERIDA",
] = (
    "Revisar individualmente la carrera vigente, CODCARPR, "
    "CODCARR y CODPESTUD antes de utilizar cualquier nivel."
)

resultado.loc[
    mask_carrera_distinta,
    "RESPALDO_ACTUAL",
] = "IDENTIDAD_EXACTA_CON_CARRERA_DISTINTA"

resultado.loc[
    mask_carrera_distinta,
    "OBSERVACION_EXPEDIENTE",
] = (
    "La identidad personal coincide, pero la carrera observada "
    "en DatosAlumnos no coincide con la carrera del plan vigente."
)


# ------------------------------------------------------------
# C. Sin coincidencia de identidad exacta
# ------------------------------------------------------------

mask_sin_identidad = texto(
    resultado["ESTADO_IDENTIDAD"]
).eq(
    "SIN_COINCIDENCIA_IDENTIDAD_EXACTA"
)

resultado.loc[
    mask_sin_identidad,
    "CATEGORIA_REVISION_644",
] = "SIN_COINCIDENCIA_IDENTIDAD_EXACTA"

resultado.loc[
    mask_sin_identidad,
    "PRIORIDAD_REVISION",
] = "P2_MEDIA"

resultado.loc[
    mask_sin_identidad,
    "ACCION_REQUERIDA",
] = (
    "Solicitar o buscar una fuente institucional adicional que "
    "contenga identidad, carrera vigente y nivel académico."
)

resultado.loc[
    mask_sin_identidad,
    "RESPALDO_ACTUAL",
] = "SIN_COINCIDENCIA_EN_HOJA1_NI_DATOSALUMNOS"

resultado.loc[
    mask_sin_identidad,
    "OBSERVACION_EXPEDIENTE",
] = (
    "No existe coincidencia por documento ni por identidad "
    "personal exacta en las fuentes revisadas."
)


# ------------------------------------------------------------
# D. Identidad exacta con múltiples trayectorias
# ------------------------------------------------------------

mask_multiples = texto(
    resultado["ESTADO_IDENTIDAD"]
).eq(
    "IDENTIDAD_EXACTA_MULTIPLES_TRAYECTORIAS"
)

resultado.loc[
    mask_multiples,
    "CATEGORIA_REVISION_644",
] = "IDENTIDAD_EXACTA_MULTIPLES_TRAYECTORIAS"

resultado.loc[
    mask_multiples,
    "PRIORIDAD_REVISION",
] = "P1_ALTA"

resultado.loc[
    mask_multiples,
    "ACCION_REQUERIDA",
] = (
    "Revisar individualmente todas las carreras, niveles, RUT "
    "y CODCLI asociados. No seleccionar el máximo automáticamente."
)

resultado.loc[
    mask_multiples,
    "RESPALDO_ACTUAL",
] = "IDENTIDAD_EXACTA_CON_MULTIPLICIDAD"

resultado.loc[
    mask_multiples,
    "OBSERVACION_EXPEDIENTE",
] = (
    "La identidad personal coincide, pero existen múltiples "
    "trayectorias o niveles observados."
)


# ------------------------------------------------------------
# E. Nivel observado supera el máximo del plan
# ------------------------------------------------------------

mask_supera_plan = texto(
    resultado["ESTADO_IDENTIDAD"]
).eq(
    "CONFLICTO_NIVEL_IDENTIDAD_SUPERA_PLAN"
)

resultado.loc[
    mask_supera_plan,
    "CATEGORIA_REVISION_644",
] = "NIVEL_OBSERVADO_SUPERA_MAXIMO_PLAN"

resultado.loc[
    mask_supera_plan,
    "PRIORIDAD_REVISION",
] = "P1_CRITICA"

resultado.loc[
    mask_supera_plan,
    "ACCION_REQUERIDA",
] = (
    "Revisar malla, versión del plan, carrera y fuente del nivel. "
    "No truncar ni reemplazar automáticamente."
)

resultado.loc[
    mask_supera_plan,
    "RESPALDO_ACTUAL",
] = "IDENTIDAD_EXACTA_NIVEL_FUERA_DE_RANGO"

resultado.loc[
    mask_supera_plan,
    "OBSERVACION_EXPEDIENTE",
] = (
    "El nivel observado para la identidad excede el nivel máximo "
    "registrado en la malla del CODPESTUD vigente."
)


# ============================================================
# 7. CONTROL DE CASOS NO CLASIFICADOS
# ============================================================

mask_sin_clasificar = texto(
    resultado["CATEGORIA_REVISION_644"]
).eq("")

if mask_sin_clasificar.any():
    no_clasificados = resultado.loc[
        mask_sin_clasificar
    ].copy()

    no_clasificados.to_csv(
        AUDITORIAS
        / "00_CASOS_NO_CLASIFICADOS.tsv",
        sep="\t",
        index=False,
    )

    estados_no_clasificados = (
        no_clasificados[
            [
                "ESTADO_NIVEL_FINAL",
                "ESTADO_IDENTIDAD",
                "ESTADO_VALIDACION_56",
            ]
        ]
        .value_counts(dropna=False)
        .reset_index(name="CASOS")
    )

    estados_no_clasificados.to_csv(
        AUDITORIAS
        / "00_ESTADOS_NO_CLASIFICADOS.tsv",
        sep="\t",
        index=False,
    )

    raise RuntimeError(
        f"Quedaron {int(mask_sin_clasificar.sum())} casos "
        "sin clasificación. Se generó auditoría de bloqueo."
    )


# ============================================================
# 8. VALIDAR DISTRIBUCIÓN ESPERADA
# ============================================================

conteos_esperados = {
    "TRAYECTORIA_EXCLUSIVAMENTE_EN_OTRA_CARRERA": 562,
    "CONFLICTO_CARRERA_DATOSALUMNOS_VS_PLAN": 14,
    "SIN_COINCIDENCIA_IDENTIDAD_EXACTA": 53,
    "IDENTIDAD_EXACTA_MULTIPLES_TRAYECTORIAS": 14,
    "NIVEL_OBSERVADO_SUPERA_MAXIMO_PLAN": 1,
}

conteos_observados = (
    resultado[
        "CATEGORIA_REVISION_644"
    ]
    .value_counts()
    .to_dict()
)

diferencias = []

for categoria, esperado in conteos_esperados.items():
    observado = int(
        conteos_observados.get(categoria, 0)
    )

    if observado != esperado:
        diferencias.append({
            "CATEGORIA": categoria,
            "ESPERADO": esperado,
            "OBSERVADO": observado,
        })

if diferencias:
    pd.DataFrame(diferencias).to_csv(
        AUDITORIAS
        / "00_DIFERENCIAS_CONTEOS_ESPERADOS.tsv",
        sep="\t",
        index=False,
    )

    raise RuntimeError(
        "La distribución observada no coincide con los "
        "conteos previamente confirmados."
    )


# ============================================================
# 9. ORDEN DE REVISIÓN
# ============================================================

orden_prioridad = {
    "P1_CRITICA": 1,
    "P1_ALTA": 2,
    "P2_MEDIA": 3,
    "P3_BAJA": 4,
}

resultado["ORDEN_PRIORIDAD"] = (
    resultado["PRIORIDAD_REVISION"]
    .map(orden_prioridad)
)

columnas_orden = [
    columna
    for columna in [
        "ORDEN_PRIORIDAD",
        "CATEGORIA_REVISION_644",
        "CODPESTUD_RESUELTO",
        "CODIGO_UNICO",
        "ID_FILA_5809",
    ]
    if columna in resultado.columns
]

resultado = resultado.sort_values(
    columnas_orden,
    kind="stable",
).reset_index(drop=True)

resultado["N_ORDEN_REVISION"] = range(
    1,
    len(resultado) + 1,
)


# ============================================================
# 10. SUBCONJUNTOS
# ============================================================

criticos = resultado[
    resultado["PRIORIDAD_REVISION"].eq(
        "P1_CRITICA"
    )
].copy()

alta = resultado[
    resultado["PRIORIDAD_REVISION"].eq(
        "P1_ALTA"
    )
].copy()

media = resultado[
    resultado["PRIORIDAD_REVISION"].eq(
        "P2_MEDIA"
    )
].copy()

baja = resultado[
    resultado["PRIORIDAD_REVISION"].eq(
        "P3_BAJA"
    )
].copy()

revision_individual = resultado[
    resultado["PRIORIDAD_REVISION"].isin([
        "P1_CRITICA",
        "P1_ALTA",
    ])
].copy()

solicitud_fuente = resultado[
    resultado["CATEGORIA_REVISION_644"].isin([
        "SIN_COINCIDENCIA_IDENTIDAD_EXACTA",
        "TRAYECTORIA_EXCLUSIVAMENTE_EN_OTRA_CARRERA",
    ])
].copy()


# ============================================================
# 11. RESÚMENES
# ============================================================

resumen_categoria = (
    resultado.groupby(
        [
            "PRIORIDAD_REVISION",
            "CATEGORIA_REVISION_644",
            "ACCION_REQUERIDA",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="CASOS")
)

resumen_prioridad = (
    resultado[
        "PRIORIDAD_REVISION"
    ]
    .value_counts()
    .rename_axis("PRIORIDAD")
    .reset_index(name="CASOS")
)

resumen_plan = (
    resultado.groupby(
        [
            "CODPESTUD_RESUELTO",
            "CATEGORIA_REVISION_644",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="CASOS")
    .sort_values(
        [
            "CASOS",
            "CODPESTUD_RESUELTO",
        ],
        ascending=[
            False,
            True,
        ],
    )
)

resumen_kpi = pd.DataFrame([
    {
        "INDICADOR": "Universo pendiente",
        "VALOR": 644,
    },
    {
        "INDICADOR": "Prioridad crítica",
        "VALOR": len(criticos),
    },
    {
        "INDICADOR": "Prioridad alta",
        "VALOR": len(alta),
    },
    {
        "INDICADOR": "Prioridad media",
        "VALOR": len(media),
    },
    {
        "INDICADOR": "Prioridad baja",
        "VALOR": len(baja),
    },
    {
        "INDICADOR": "Revisión individual inmediata",
        "VALOR": len(revision_individual),
    },
    {
        "INDICADOR": "Requieren fuente institucional adicional",
        "VALOR": len(solicitud_fuente),
    },
    {
        "INDICADOR": "Casos incorporables actualmente",
        "VALOR": 0,
    },
    {
        "INDICADOR": "Archivo definitivo de carga",
        "VALOR": "NO GENERADO",
    },
])


# ============================================================
# 12. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_644",
        "RESULTADO": (
            "OK" if len(resultado) == 644 else "ERROR"
        ),
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "ID_FILA_UNICO",
        "RESULTADO": (
            "OK"
            if not resultado[
                "ID_FILA_5809"
            ].duplicated().any()
            else "ERROR"
        ),
        "DETALLE": int(
            resultado[
                "ID_FILA_5809"
            ].duplicated().sum()
        ),
    },
    {
        "VALIDACION": "TODOS_CLASIFICADOS",
        "RESULTADO": (
            "OK"
            if resultado[
                "CATEGORIA_REVISION_644"
            ].ne("").all()
            else "ERROR"
        ),
        "DETALLE": int(
            resultado[
                "CATEGORIA_REVISION_644"
            ].eq("").sum()
        ),
    },
    {
        "VALIDACION": "CONTEOS_COINCIDEN",
        "RESULTADO": "OK",
        "DETALLE": 644,
    },
    {
        "VALIDACION": "INCORPORACIONES_AUTOMATICAS",
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
# 13. EXPORTAR TSV
# ============================================================

resultado.to_csv(
    RESULTADOS
    / "01_EXPEDIENTE_COMPLETO_644.tsv",
    sep="\t",
    index=False,
)

revision_individual.to_csv(
    RESULTADOS
    / "02_REVISION_INDIVIDUAL_PRIORIDAD_1.tsv",
    sep="\t",
    index=False,
)

solicitud_fuente.to_csv(
    RESULTADOS
    / "03_CASOS_REQUIEREN_FUENTE_ADICIONAL.tsv",
    sep="\t",
    index=False,
)

criticos.to_csv(
    AUDITORIAS
    / "01_PRIORIDAD_CRITICA.tsv",
    sep="\t",
    index=False,
)

alta.to_csv(
    AUDITORIAS
    / "02_PRIORIDAD_ALTA.tsv",
    sep="\t",
    index=False,
)

media.to_csv(
    AUDITORIAS
    / "03_PRIORIDAD_MEDIA.tsv",
    sep="\t",
    index=False,
)

baja.to_csv(
    AUDITORIAS
    / "04_PRIORIDAD_BAJA.tsv",
    sep="\t",
    index=False,
)

resumen_categoria.to_csv(
    AUDITORIAS
    / "05_RESUMEN_CATEGORIAS.tsv",
    sep="\t",
    index=False,
)

resumen_plan.to_csv(
    AUDITORIAS
    / "06_RESUMEN_POR_PLAN.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "07_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 14. FUENTES Y HASHES
# ============================================================

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


# ============================================================
# 15. EXCEL
# ============================================================

excel = (
    RESULTADOS
    / "EXPEDIENTE_REVISION_644_PENDIENTES.xlsx"
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

    resumen_categoria.to_excel(
        writer,
        sheet_name="CATEGORIAS",
        index=False,
    )

    revision_individual.to_excel(
        writer,
        sheet_name="REVISION_P1",
        index=False,
    )

    criticos.to_excel(
        writer,
        sheet_name="CRITICOS",
        index=False,
    )

    alta.to_excel(
        writer,
        sheet_name="PRIORIDAD_ALTA",
        index=False,
    )

    media.to_excel(
        writer,
        sheet_name="PRIORIDAD_MEDIA",
        index=False,
    )

    baja.to_excel(
        writer,
        sheet_name="PRIORIDAD_BAJA",
        index=False,
    )

    solicitud_fuente.to_excel(
        writer,
        sheet_name="FUENTE_ADICIONAL",
        index=False,
    )

    resumen_plan.to_excel(
        writer,
        sheet_name="POR_PLAN",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="DETALLE_644",
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
    "universo_pendiente": 644,
    "categorias": {
        categoria: int(casos)
        for categoria, casos in conteos_observados.items()
    },
    "prioridades": {
        fila["PRIORIDAD"]: int(fila["CASOS"])
        for _, fila in resumen_prioridad.iterrows()
    },
    "revision_individual_prioridad_1": len(
        revision_individual
    ),
    "requieren_fuente_adicional": len(
        solicitud_fuente
    ),
    "casos_incorporables": 0,
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


# ============================================================
# 17. REPORTE
# ============================================================

lineas = [
    "EXPEDIENTE DE REVISIÓN DE 644 PENDIENTES",
    "=" * 96,
    "Proceso: Avance Curricular SIES 2026",
    "Subproyecto: 5809 Matrícula",
    "Año de referencia: 2025",
    "",
    "DISTRIBUCIÓN",
    "------------",
]

for _, fila in resumen_categoria.iterrows():
    lineas.append(
        f"{fila['CATEGORIA_REVISION_644']}: "
        f"{fila['CASOS']}"
    )

lineas.extend([
    "",
    f"Revisión individual inmediata: {len(revision_individual)}",
    f"Requieren fuente adicional: {len(solicitud_fuente)}",
    "Casos incorporables actualmente: 0",
    "",
    f"Excel: {excel}",
    f"Carpeta: {SALIDA}",
    "",
    "Fuentes modificadas: NO",
    "Precargas modificadas: NO",
    "Archivo final de carga generado: NO",
])

(REPORTES / "RESUMEN_EJECUCION.txt").write_text(
    "\n".join(lineas),
    encoding="utf-8",
)


# ============================================================
# 18. TERMINAL
# ============================================================

print()
print("=" * 100)
print("EXPEDIENTE DE REVISIÓN DE LOS 644 PENDIENTES")
print("=" * 100)
print(f"Universo pendiente: {len(resultado)}")
print()
print("CATEGORÍAS")
print("-" * 100)

for _, fila in resumen_categoria.iterrows():
    print(
        f"{fila['CATEGORIA_REVISION_644']}: "
        f"{fila['CASOS']}"
    )

print()
print("PRIORIDADES")
print("-" * 100)

for _, fila in resumen_prioridad.iterrows():
    print(
        f"{fila['PRIORIDAD']}: {fila['CASOS']}"
    )

print()
print(
    "Casos para revisión individual inmediata: "
    f"{len(revision_individual)}"
)
print(
    "Casos que requieren fuente institucional adicional: "
    f"{len(solicitud_fuente)}"
)
print("Casos incorporables actualmente: 0")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Fuentes modificadas: NO")
print("Precargas modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 100)
