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

EJECUCION = (
    RAIZ
    / "avance_curricular_2026"
    / "05_cierre_integral"
    / "CIERRE_AVANCE_CURRICULAR_20260703_125157"
)

BLOQUEADOS = (
    EJECUCION
    / "03_CONCILIACION_CARRERAS"
    / "PLANES_DISTRIBUCION_NO_DEMOSTRADA.tsv"
)

CONCILIACION = (
    EJECUCION
    / "03_CONCILIACION_CARRERAS"
    / "CONCILIACION_CARRERAS_PLANES.xlsx"
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
    EJECUCION
    / "03_CONCILIACION_CARRERAS"
    / f"EXPEDIENTE_42_PERIODIZACIONES_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
SOLICITUD = SALIDA / "04_SOLICITUD_INSTITUCIONAL"

for carpeta in (
    RESULTADOS,
    AUDITORIA,
    SOLICITUD,
):
    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )


def norm_col(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

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

    return re.sub(
        r"\s+",
        "",
        texto,
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


def buscar_columna(df, candidatas, obligatoria=False):
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    for candidata in candidatas:
        clave = norm_col(candidata)

        if clave in mapa:
            return mapa[clave]

    if obligatoria:
        raise RuntimeError(
            "No se encontró columna requerida entre: "
            + " | ".join(candidatas)
        )

    return None


def unir_unicos(serie):
    valores = sorted({
        norm_codigo(valor)
        for valor in serie
        if norm_codigo(valor)
    })

    return " | ".join(valores)


for ruta in (
    BLOQUEADOS,
    CONCILIACION,
    MALLAS,
):
    if not ruta.exists():
        raise RuntimeError(
            f"No existe la fuente requerida: {ruta}"
        )


bloqueados = pd.read_csv(
    BLOQUEADOS,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if bloqueados.empty:
    raise RuntimeError(
        "El archivo de planes bloqueados está vacío."
    )

print()
print("UNIVERSO FÍSICO DEL BLOQUEO")
print("-" * 108)
print(f"Filas del archivo de bloqueo: {len(bloqueados)}")


mallas = pd.read_excel(
    MALLAS,
    sheet_name="BBDD Bruta",
    dtype=object,
    engine="openpyxl",
)

mallas = mallas.dropna(
    axis=0,
    how="all",
).dropna(
    axis=1,
    how="all",
)


col_plan_malla = buscar_columna(
    mallas,
    [
        "CODPESTUD",
        "PLAN_ESTUDIOS",
        "CODIGO_PLAN",
        "PLAN",
    ],
    obligatoria=True,
)

col_nivel = buscar_columna(
    mallas,
    [
        "NIVEL",
        "NIVEL_MALLA",
        "PERIODO",
        "SEMESTRE",
        "TRIMESTRE",
    ],
    obligatoria=True,
)

col_carrera = buscar_columna(
    mallas,
    [
        "CODCARR",
        "CODCARPR",
        "CODIGO_CARRERA",
        "CARRERA",
    ],
)

col_nombre_carrera = buscar_columna(
    mallas,
    [
        "NOMBRE_CARRERA",
        "NOMCARR",
        "CARRERA_DESCRIPCION",
    ],
)

col_anio = buscar_columna(
    mallas,
    [
        "ANIO",
        "ANO",
        "ANIO_CURRICULAR",
        "ANO_CURRICULAR",
        "ANIO_MALLA",
        "ANO_MALLA",
    ],
)

col_periodo = buscar_columna(
    mallas,
    [
        "PERIODO",
        "PERIODO_MALLA",
    ],
)

col_semestre = buscar_columna(
    mallas,
    [
        "SEMESTRE",
    ],
)

col_asignatura = buscar_columna(
    mallas,
    [
        "CODRAMO",
        "CODIGO_ASIGNATURA",
        "ASIGNATURA",
        "NOMBRE_ASIGNATURA",
    ],
)


mallas_base = pd.DataFrame({
    "PLAN_MALLA":
    mallas[col_plan_malla].map(norm_codigo),

    "NIVEL_ORIGINAL":
    mallas[col_nivel],

    "CARRERA_MALLA":
    (
        mallas[col_carrera].map(norm_codigo)
        if col_carrera
        else ""
    ),

    "NOMBRE_CARRERA_MALLA":
    (
        mallas[col_nombre_carrera].astype(str)
        if col_nombre_carrera
        else ""
    ),

    "ANIO_EXPLICITO":
    (
        mallas[col_anio]
        if col_anio
        else ""
    ),

    "PERIODO_EXPLICITO":
    (
        mallas[col_periodo]
        if col_periodo
        else ""
    ),

    "SEMESTRE_EXPLICITO":
    (
        mallas[col_semestre]
        if col_semestre
        else ""
    ),

    "ASIGNATURA":
    (
        mallas[col_asignatura].astype(str)
        if col_asignatura
        else ""
    ),

    "FILA_MALLA":
    range(
        2,
        len(mallas) + 2,
    ),
})

mallas_base["NIVEL_NUM"] = pd.to_numeric(
    mallas_base["NIVEL_ORIGINAL"],
    errors="coerce",
)

mallas_base["ANIO_NUM"] = pd.to_numeric(
    mallas_base["ANIO_EXPLICITO"],
    errors="coerce",
)

mallas_base["PERIODO_NUM"] = pd.to_numeric(
    mallas_base["PERIODO_EXPLICITO"],
    errors="coerce",
)

mallas_base["SEMESTRE_NUM"] = pd.to_numeric(
    mallas_base["SEMESTRE_EXPLICITO"],
    errors="coerce",
)


col_plan_bloqueo = buscar_columna(
    bloqueados,
    [
        "CODPESTUD",
        "PLAN_ESTUDIOS",
        "PLAN",
        "CODPESTUD_RESUELTO",
    ],
    obligatoria=True,
)

bloqueados["PLAN_NORM"] = (
    bloqueados[col_plan_bloqueo]
    .map(norm_codigo)
)

if bloqueados["PLAN_NORM"].eq("").any():
    filas_vacias = bloqueados[
        bloqueados["PLAN_NORM"].eq("")
    ].index.tolist()

    raise RuntimeError(
        "Existen filas bloqueadas sin plan normalizado. "
        f"Índices: {filas_vacias[:20]}"
    )

# El archivo de bloqueo puede contener varias filas por plan.
# Se conserva el detalle físico y se construye un universo
# único para la conciliación de periodización.

columnas_identificacion = [
    columna
    for columna in [
        "CODIGO_UNICO",
        "CODIGO_UNICO_NORM",
        "CODCARR",
        "CODCARPR",
        "CARRERA",
        "NOMBRE_CARRERA",
        "PLAN_ESTUDIOS",
        "CODPESTUD",
        "CODPESTUD_RESUELTO",
    ]
    if columna in bloqueados.columns
]

def unir_valores_unicos(serie):
    valores = sorted({
        norm_codigo(valor)
        for valor in serie
        if norm_codigo(valor)
    })

    return " | ".join(valores)

agregaciones = {
    "N_FILAS_BLOQUEO": (
        "PLAN_NORM",
        "size",
    ),
}

for columna in columnas_identificacion:
    agregaciones[
        f"{norm_col(columna)}_VALORES"
    ] = (
        columna,
        unir_valores_unicos,
    )

bloqueados_planes = (
    bloqueados.groupby(
        "PLAN_NORM",
        dropna=False,
    )
    .agg(**agregaciones)
    .reset_index()
)

duplicados_plan = (
    bloqueados.groupby(
        "PLAN_NORM",
        dropna=False,
    )
    .size()
    .reset_index(name="N_FILAS")
)

duplicados_plan = duplicados_plan[
    duplicados_plan["N_FILAS"].gt(1)
].copy()

planes_objetivo = set(
    bloqueados_planes["PLAN_NORM"]
)

detalle = mallas_base[
    mallas_base["PLAN_MALLA"].isin(
        planes_objetivo
    )
].copy()


resumen_malla = (
    detalle.groupby(
        "PLAN_MALLA",
        dropna=False,
    )
    .agg(
        REGISTROS_MALLA=(
            "PLAN_MALLA",
            "size",
        ),
        CARRERAS_MALLA=(
            "CARRERA_MALLA",
            unir_unicos,
        ),
        N_NIVELES=(
            "NIVEL_NUM",
            lambda serie: (
                pd.to_numeric(
                    serie,
                    errors="coerce",
                )
                .dropna()
                .nunique()
            ),
        ),
        NIVEL_MIN=(
            "NIVEL_NUM",
            "min",
        ),
        NIVEL_MAX=(
            "NIVEL_NUM",
            "max",
        ),
        NIVELES_OBSERVADOS=(
            "NIVEL_NUM",
            lambda serie: " | ".join(
                str(int(valor))
                for valor in sorted({
                    float(valor)
                    for valor in pd.to_numeric(
                        serie,
                        errors="coerce",
                    ).dropna()
                })
            ),
        ),
        N_ANIOS_EXPLICITOS=(
            "ANIO_NUM",
            lambda serie: (
                pd.to_numeric(
                    serie,
                    errors="coerce",
                )
                .dropna()
                .nunique()
            ),
        ),
        ANIOS_EXPLICITOS=(
            "ANIO_NUM",
            lambda serie: " | ".join(
                str(int(valor))
                for valor in sorted({
                    float(valor)
                    for valor in pd.to_numeric(
                        serie,
                        errors="coerce",
                    ).dropna()
                })
            ),
        ),
        N_PERIODOS_EXPLICITOS=(
            "PERIODO_NUM",
            lambda serie: (
                pd.to_numeric(
                    serie,
                    errors="coerce",
                )
                .dropna()
                .nunique()
            ),
        ),
        PERIODOS_EXPLICITOS=(
            "PERIODO_NUM",
            lambda serie: " | ".join(
                str(int(valor))
                for valor in sorted({
                    float(valor)
                    for valor in pd.to_numeric(
                        serie,
                        errors="coerce",
                    ).dropna()
                })
            ),
        ),
        N_SEMESTRES_EXPLICITOS=(
            "SEMESTRE_NUM",
            lambda serie: (
                pd.to_numeric(
                    serie,
                    errors="coerce",
                )
                .dropna()
                .nunique()
            ),
        ),
        SEMESTRES_EXPLICITOS=(
            "SEMESTRE_NUM",
            lambda serie: " | ".join(
                str(int(valor))
                for valor in sorted({
                    float(valor)
                    for valor in pd.to_numeric(
                        serie,
                        errors="coerce",
                    ).dropna()
                })
            ),
        ),
    )
    .reset_index()
    .rename(
        columns={
            "PLAN_MALLA":
            "PLAN_NORM"
        }
    )
)


resultado = bloqueados_planes.merge(
    resumen_malla,
    on="PLAN_NORM",
    how="left",
    validate="one_to_one",
)

universo_planes_unicos = bloqueados_planes["PLAN_NORM"].nunique()

if len(resultado) != universo_planes_unicos:
    raise RuntimeError(
        "La consolidación no conserva el universo único "
        f"de planes. Esperados: {universo_planes_unicos}; "
        f"obtenidos: {len(resultado)}."
    )

if resultado["PLAN_NORM"].duplicated().any():
    duplicados = resultado[
        resultado["PLAN_NORM"].duplicated(
            keep=False
        )
    ]["PLAN_NORM"].tolist()

    raise RuntimeError(
        "Persisten planes duplicados después de consolidar: "
        + " | ".join(sorted(set(duplicados)))
    )


for columna in [
    "REGISTROS_MALLA",
    "N_NIVELES",
    "N_ANIOS_EXPLICITOS",
    "N_PERIODOS_EXPLICITOS",
    "N_SEMESTRES_EXPLICITOS",
]:
    resultado[columna] = (
        pd.to_numeric(
            resultado[columna],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )


resultado["ESTADO_EVIDENCIA_PERIODIZACION"] = ""
resultado["FUENTE_NECESARIA"] = ""
resultado["ACCION_REQUERIDA"] = ""
resultado["PUEDE_CONSTRUIR_DISTRIBUCION"] = "NO"
resultado["OBSERVACION"] = ""


mask_sin_malla = (
    resultado["REGISTROS_MALLA"].eq(0)
)

resultado.loc[
    mask_sin_malla,
    "ESTADO_EVIDENCIA_PERIODIZACION",
] = "PLAN_SIN_REGISTROS_EN_MALLA"

resultado.loc[
    mask_sin_malla,
    "FUENTE_NECESARIA",
] = (
    "Malla institucional vigente 2025 del plan."
)

resultado.loc[
    mask_sin_malla,
    "ACCION_REQUERIDA",
] = (
    "Solicitar o localizar malla institucional."
)


mask_anio_explicito = (
    resultado["N_ANIOS_EXPLICITOS"].gt(0)
)

resultado.loc[
    mask_anio_explicito,
    "ESTADO_EVIDENCIA_PERIODIZACION",
] = "ANIO_EXPLICITO_DISPONIBLE"

resultado.loc[
    mask_anio_explicito,
    "PUEDE_CONSTRUIR_DISTRIBUCION",
] = "REQUIERE_VALIDAR_COERENCIA"

resultado.loc[
    mask_anio_explicito,
    "ACCION_REQUERIDA",
] = (
    "Validar que el año explícito corresponde a la "
    "distribución exigida por Carreras Avance Curricular."
)


mask_periodo_sin_anio = (
    ~mask_sin_malla
    & ~mask_anio_explicito
    & (
        resultado["N_PERIODOS_EXPLICITOS"].gt(0)
        | resultado["N_SEMESTRES_EXPLICITOS"].gt(0)
    )
)

resultado.loc[
    mask_periodo_sin_anio,
    "ESTADO_EVIDENCIA_PERIODIZACION",
] = "PERIODO_O_SEMESTRE_SIN_ANIO"

resultado.loc[
    mask_periodo_sin_anio,
    "FUENTE_NECESARIA",
] = (
    "Tabla institucional que relacione período/semestre "
    "con año curricular para el plan."
)

resultado.loc[
    mask_periodo_sin_anio,
    "ACCION_REQUERIDA",
] = (
    "Confirmar institucionalmente la periodización."
)


mask_solo_nivel = (
    ~mask_sin_malla
    & ~mask_anio_explicito
    & ~mask_periodo_sin_anio
    & resultado["N_NIVELES"].gt(0)
)

resultado.loc[
    mask_solo_nivel,
    "ESTADO_EVIDENCIA_PERIODIZACION",
] = "SOLO_NIVEL_SIN_SEMANTICA_CONFIRMADA"

resultado.loc[
    mask_solo_nivel,
    "FUENTE_NECESARIA",
] = (
    "Definición institucional de NIVEL y mapa "
    "NIVEL → AÑO CURRICULAR para el plan."
)

resultado.loc[
    mask_solo_nivel,
    "ACCION_REQUERIDA",
] = (
    "No convertir. Solicitar confirmación documental."
)


mask_sin_dato = (
    resultado[
        "ESTADO_EVIDENCIA_PERIODIZACION"
    ].eq("")
)

resultado.loc[
    mask_sin_dato,
    "ESTADO_EVIDENCIA_PERIODIZACION",
] = "SIN_DATO_DE_PERIODIZACION"

resultado.loc[
    mask_sin_dato,
    "FUENTE_NECESARIA",
] = (
    "Malla y tabla institucional de distribución anual."
)

resultado.loc[
    mask_sin_dato,
    "ACCION_REQUERIDA",
] = (
    "Solicitar antecedentes institucionales."
)


solicitud = resultado.copy()

solicitud[
    "CONFIRMAR_SEMANTICA_NIVEL"
] = ""

solicitud[
    "TIPO_PERIODIZACION"
] = ""

solicitud[
    "NIVEL_INICIAL_ANIO_1"
] = ""

solicitud[
    "NIVEL_FINAL_ANIO_1"
] = ""

solicitud[
    "NIVEL_INICIAL_ANIO_2"
] = ""

solicitud[
    "NIVEL_FINAL_ANIO_2"
] = ""

solicitud[
    "NIVEL_INICIAL_ANIO_3"
] = ""

solicitud[
    "NIVEL_FINAL_ANIO_3"
] = ""

solicitud[
    "NIVEL_INICIAL_ANIO_4"
] = ""

solicitud[
    "NIVEL_FINAL_ANIO_4"
] = ""

solicitud[
    "NIVEL_INICIAL_ANIO_5"
] = ""

solicitud[
    "NIVEL_FINAL_ANIO_5"
] = ""

solicitud[
    "NIVEL_INICIAL_ANIO_6"
] = ""

solicitud[
    "NIVEL_FINAL_ANIO_6"
] = ""

solicitud[
    "FUENTE_RESPALDO"
] = ""

solicitud[
    "RESPONSABLE_CONFIRMACION"
] = ""

solicitud[
    "FECHA_CONFIRMACION"
] = ""

solicitud[
    "OBSERVACION_INSTITUCIONAL"
] = ""


resumen = (
    resultado[
        "ESTADO_EVIDENCIA_PERIODIZACION"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="PLANES")
)


resultado.to_csv(
    RESULTADOS
    / "01_DIAGNOSTICO_PLANES_PERIODIZACIONES.tsv",
    sep="\t",
    index=False,
)

bloqueados.to_csv(
    AUDITORIA
    / "00_DETALLE_FISICO_BLOQUEO.tsv",
    sep="\t",
    index=False,
)

bloqueados_planes.to_csv(
    AUDITORIA
    / "00B_UNIVERSO_UNICO_PLANES.tsv",
    sep="\t",
    index=False,
)

duplicados_plan.to_csv(
    AUDITORIA
    / "00C_PLANES_REPETIDOS_EN_BLOQUEO.tsv",
    sep="\t",
    index=False,
)

detalle.to_csv(
    RESULTADOS
    / "02_DETALLE_MALLAS_42.tsv",
    sep="\t",
    index=False,
)

solicitud.to_csv(
    SOLICITUD
    / "01_PLANILLA_CONFIRMACION_INSTITUCIONAL_42.tsv",
    sep="\t",
    index=False,
)


excel = (
    RESULTADOS
    / "EXPEDIENTE_42_PERIODIZACIONES.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="DIAGNOSTICO_42",
        index=False,
    )

    solicitud.to_excel(
        writer,
        sheet_name="SOLICITUD_CONFIRMACION",
        index=False,
    )

    detalle.to_excel(
        writer,
        sheet_name="DETALLE_MALLAS",
        index=False,
    )

    bloqueados_planes.to_excel(
        writer,
        sheet_name="UNIVERSO_PLANES",
        index=False,
    )

    duplicados_plan.to_excel(
        writer,
        sheet_name="PLANES_REPETIDOS",
        index=False,
    )

    bloqueados.to_excel(
        writer,
        sheet_name="BLOQUEO_ORIGEN",
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
                60,
            )


fuentes = pd.DataFrame([
    {
        "ROL": "PLANES_BLOQUEADOS",
        "RUTA": str(BLOQUEADOS),
        "SHA256": sha256(BLOQUEADOS),
    },
    {
        "ROL": "CONCILIACION_FASE_4",
        "RUTA": str(CONCILIACION),
        "SHA256": sha256(CONCILIACION),
    },
    {
        "ROL": "MALLAS_INSTITUCIONALES",
        "RUTA": str(MALLAS),
        "SHA256": sha256(MALLAS),
    },
])

fuentes.to_csv(
    AUDITORIA
    / "01_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "FILAS_FISICAS_BLOQUEO",
        "RESULTADO": "INFORMATIVO",
        "DETALLE": len(bloqueados),
    },
    {
        "VALIDACION": "UNIVERSO_PLANES_UNICOS",
        "RESULTADO": (
            "OK"
            if len(resultado) == universo_planes_unicos
            else "ERROR"
        ),
        "DETALLE": universo_planes_unicos,
    },
    {
        "VALIDACION": "PLANES_REPETIDOS_EN_ARCHIVO_BLOQUEO",
        "RESULTADO": (
            "INFORMATIVO"
            if len(duplicados_plan) > 0
            else "OK"
        ),
        "DETALLE": len(duplicados_plan),
    },
    {
        "VALIDACION": "CONVERSIONES_APLICADAS",
        "RESULTADO": "OK",
        "DETALLE": 0,
    },
    {
        "VALIDACION": "FUENTES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "FASE_4_DESBLOQUEADA",
        "RESULTADO": "NO",
        "DETALLE": (
            "Requiere completar la confirmación institucional."
        ),
    },
])

validaciones.to_csv(
    AUDITORIA
    / "02_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproceso": "Carreras Avance Curricular",
    "fase": "4B",
    "filas_fisicas_bloqueo": len(bloqueados),
    "universo_planes_unicos": universo_planes_unicos,
    "planes_repetidos_en_bloqueo": len(duplicados_plan),
    "conversiones_aplicadas": 0,
    "fuentes_modificadas": False,
    "fase_4_desbloqueada": False,
    "salida": str(SALIDA),
}

(SALIDA / "manifest_ejecucion.json").write_text(
    json.dumps(
        manifiesto,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 108)
print("EXPEDIENTE DE PLANES SIN PERIODIZACIÓN DEMOSTRADA")
print("=" * 108)

print(
    f"Filas físicas en archivo de bloqueo: "
    f"{len(bloqueados)}"
)
print(
    f"Planes únicos bloqueados: "
    f"{universo_planes_unicos}"
)
print(
    f"Planes repetidos en archivo de bloqueo: "
    f"{len(duplicados_plan)}"
)
print()

for _, fila in resumen.iterrows():
    print(
        f"{fila['ESTADO']}: "
        f"{fila['PLANES']}"
    )

print()
print(f"Excel: {excel}")
print(
    "Planilla institucional: "
    f"{SOLICITUD / '01_PLANILLA_CONFIRMACION_INSTITUCIONAL_42.tsv'}"
)
print(f"Carpeta: {SALIDA}")
print("Conversiones aplicadas: 0")
print("Fuentes modificadas: NO")
print("Fase 4 desbloqueada: NO")
print("=" * 108)
