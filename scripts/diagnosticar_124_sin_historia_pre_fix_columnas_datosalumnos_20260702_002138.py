#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

RECLASIFICACION_686 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "CORRECCION_CLASIFICACION_686_20260702_001937"
    / "01_RECLASIFICACION_CORREGIDA_686.tsv"
)

PROMEDIOS = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "PROMEDIOSDEALUMNOS_7804.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"DIAGNOSTICO_124_SIN_HISTORIA_{timestamp}"
)

SALIDA.mkdir(parents=True, exist_ok=False)


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


def buscar_columna(df, opciones):
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    for opcion in opciones:
        clave = norm_col(opcion)

        if clave in mapa:
            return mapa[clave]

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


for ruta in (
    RECLASIFICACION_686,
    PROMEDIOS,
):
    if not ruta.exists():
        raise RuntimeError(f"No existe: {ruta}")


diag = pd.read_csv(
    RECLASIFICACION_686,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

casos_124 = diag[
    diag["CLASIFICACION_CORREGIDA"].eq(
        "SIN_PLANES_HISTORICOS"
    )
].copy()

if len(casos_124) != 124:
    raise RuntimeError(
        f"Se esperaban 124 casos y se encontraron "
        f"{len(casos_124)}."
    )

if casos_124["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Existen ID_FILA_5809 duplicados."
    )

casos_124["DOCUMENTO_NORM"] = (
    casos_124["DOCUMENTO_NORM"]
    .map(norm_documento)
)


datos = pd.read_excel(
    PROMEDIOS,
    sheet_name="DatosAlumnos",
    dtype=object,
)

inventario_columnas = pd.DataFrame({
    "N_ORDEN": range(1, len(datos.columns) + 1),
    "COLUMNA_ORIGINAL": list(datos.columns),
    "COLUMNA_NORMALIZADA": [
        norm_col(columna)
        for columna in datos.columns
    ],
})

col_documento = buscar_columna(
    datos,
    [
        "RUT",
        "NUM_DOCUMENTO",
        "N_DOC",
        "DOCUMENTO",
    ],
)

col_codcli = buscar_columna(
    datos,
    ["CODCLI"],
)

col_nivel = buscar_columna(
    datos,
    [
        "NIVEL",
        "DA_NIVEL",
        "NIV_ACA",
        "NIVEL_ACADEMICO",
    ],
)

col_carrera = buscar_columna(
    datos,
    [
        "CODCARPR",
        "CODCARR",
        "COD_CAR",
        "CODIGO_CARRERA",
    ],
)

col_plan = buscar_columna(
    datos,
    [
        "CODPESTUD",
        "PLAN_ESTUDIOS",
        "PLAN_DE_ESTUDIO",
    ],
)

columnas_detectadas = pd.DataFrame([
    {
        "ROL": "DOCUMENTO",
        "COLUMNA": col_documento or "",
        "DISPONIBLE": bool(col_documento),
    },
    {
        "ROL": "CODCLI",
        "COLUMNA": col_codcli or "",
        "DISPONIBLE": bool(col_codcli),
    },
    {
        "ROL": "NIVEL",
        "COLUMNA": col_nivel or "",
        "DISPONIBLE": bool(col_nivel),
    },
    {
        "ROL": "CARRERA",
        "COLUMNA": col_carrera or "",
        "DISPONIBLE": bool(col_carrera),
    },
    {
        "ROL": "PLAN",
        "COLUMNA": col_plan or "",
        "DISPONIBLE": bool(col_plan),
    },
])

if not col_documento:
    raise RuntimeError(
        "DatosAlumnos no contiene una columna de documento "
        "identificable."
    )


d = datos.copy()

d["DOCUMENTO_NORM_DIAG"] = (
    d[col_documento].map(norm_documento)
)

d["CODCLI_DATOS"] = (
    d[col_codcli].map(norm_codigo)
    if col_codcli
    else ""
)

d["NIVEL_DATOS_NUM"] = (
    pd.to_numeric(
        d[col_nivel],
        errors="coerce",
    )
    if col_nivel
    else pd.NA
)

d["CARRERA_DATOS"] = (
    d[col_carrera].map(norm_codigo)
    if col_carrera
    else ""
)

d["PLAN_DATOS"] = (
    d[col_plan].map(norm_codigo)
    if col_plan
    else ""
)

d = d[
    d["DOCUMENTO_NORM_DIAG"].ne("")
].copy()


resumen_datos = (
    d.groupby(
        "DOCUMENTO_NORM_DIAG",
        dropna=False,
    )
    .agg(
        REGISTROS_DATOSALUMNOS=(
            "DOCUMENTO_NORM_DIAG",
            "size",
        ),
        CODCLI_DATOS=(
            "CODCLI_DATOS",
            unir_unicos,
        ),
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
        N_PLANES_DATOS=(
            "PLAN_DATOS",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        PLANES_DATOS=(
            "PLAN_DATOS",
            unir_unicos,
        ),
        NIVELES_DATOS=(
            "NIVEL_DATOS_NUM",
            unir_niveles,
        ),
        NIVEL_MIN_DATOS=(
            "NIVEL_DATOS_NUM",
            "min",
        ),
        NIVEL_MAX_DATOS=(
            "NIVEL_DATOS_NUM",
            "max",
        ),
        N_NIVELES_DATOS=(
            "NIVEL_DATOS_NUM",
            lambda serie: (
                pd.to_numeric(
                    serie,
                    errors="coerce",
                )
                .dropna()
                .nunique()
            ),
        ),
    )
    .reset_index()
)


resultado = casos_124.merge(
    resumen_datos,
    left_on="DOCUMENTO_NORM",
    right_on="DOCUMENTO_NORM_DIAG",
    how="left",
    validate="many_to_one",
)

if len(resultado) != 124:
    raise RuntimeError(
        "El cruce alteró el universo de 124 casos."
    )


resultado["ESTADO_DIAGNOSTICO_124"] = ""
resultado["NIVEL_CANDIDATO"] = pd.NA
resultado["METODO_CANDIDATO"] = ""
resultado["ASIGNACION_AUTOMATICA"] = "NO"
resultado["MOTIVO_PENDIENTE"] = ""

registros = pd.to_numeric(
    resultado["REGISTROS_DATOSALUMNOS"],
    errors="coerce",
).fillna(0)

n_carreras = pd.to_numeric(
    resultado["N_CARRERAS_DATOS"],
    errors="coerce",
).fillna(0)

n_planes = pd.to_numeric(
    resultado["N_PLANES_DATOS"],
    errors="coerce",
).fillna(0)

n_niveles = pd.to_numeric(
    resultado["N_NIVELES_DATOS"],
    errors="coerce",
).fillna(0)

nivel_max = pd.to_numeric(
    resultado["NIVEL_MAX_DATOS"],
    errors="coerce",
)

nivel_max_plan = pd.to_numeric(
    resultado.get(
        "NIVEL_MAX_PLAN_DIAG",
        pd.Series(index=resultado.index, dtype=float),
    ),
    errors="coerce",
)


mask_sin_datos = registros.eq(0)

resultado.loc[
    mask_sin_datos,
    "ESTADO_DIAGNOSTICO_124",
] = "SIN_REGISTRO_EN_DATOSALUMNOS"

resultado.loc[
    mask_sin_datos,
    "MOTIVO_PENDIENTE",
] = (
    "No existe registro por documento en DatosAlumnos."
)


mask_sin_nivel = (
    registros.gt(0)
    & n_niveles.eq(0)
)

resultado.loc[
    mask_sin_nivel,
    "ESTADO_DIAGNOSTICO_124",
] = "DATOSALUMNOS_SIN_NIVEL"

resultado.loc[
    mask_sin_nivel,
    "MOTIVO_PENDIENTE",
] = (
    "Existe registro en DatosAlumnos, pero no contiene "
    "un nivel numérico utilizable."
)


mask_nivel_unico_plan_unico = (
    registros.gt(0)
    & n_niveles.eq(1)
    & n_planes.eq(1)
    & nivel_max.notna()
)

resultado.loc[
    mask_nivel_unico_plan_unico,
    "NIVEL_CANDIDATO",
] = nivel_max.loc[
    mask_nivel_unico_plan_unico
].astype("Int64")

resultado.loc[
    mask_nivel_unico_plan_unico,
    "METODO_CANDIDATO",
] = "DATOSALUMNOS_PLAN_UNICO_NIVEL_UNICO"

mask_plan_exacto = (
    mask_nivel_unico_plan_unico
    & resultado["PLANES_DATOS"]
    .map(norm_codigo)
    .eq(
        resultado["CODPESTUD_RESUELTO"]
        .map(norm_codigo)
    )
)

mask_plan_exacto_valido = (
    mask_plan_exacto
    & nivel_max.ge(1)
    & nivel_max.le(nivel_max_plan)
)

resultado.loc[
    mask_plan_exacto_valido,
    "ESTADO_DIAGNOSTICO_124",
] = "CANDIDATO_PLAN_EXACTO_REQUIERE_VALIDACION"

resultado.loc[
    mask_plan_exacto_valido,
    "MOTIVO_PENDIENTE",
] = (
    "DatosAlumnos entrega plan exacto y nivel único dentro "
    "de la malla. Falta validar que el campo corresponda "
    "al nivel exigido por Avance Curricular."
)


mask_plan_distinto = (
    mask_nivel_unico_plan_unico
    & ~mask_plan_exacto
)

resultado.loc[
    mask_plan_distinto,
    "ESTADO_DIAGNOSTICO_124",
] = "DATOSALUMNOS_PLAN_DISTINTO"

resultado.loc[
    mask_plan_distinto,
    "MOTIVO_PENDIENTE",
] = (
    "DatosAlumnos contiene un plan distinto del CODPESTUD "
    "resuelto; no se transfiere el nivel."
)


mask_multiples = (
    registros.gt(0)
    & (
        n_niveles.gt(1)
        | n_planes.gt(1)
        | n_carreras.gt(1)
    )
    & resultado["ESTADO_DIAGNOSTICO_124"].eq("")
)

resultado.loc[
    mask_multiples,
    "ESTADO_DIAGNOSTICO_124",
] = "DATOSALUMNOS_MULTIPLES_TRAYECTORIAS"

resultado.loc[
    mask_multiples,
    "MOTIVO_PENDIENTE",
] = (
    "Existen múltiples niveles, planes o carreras en "
    "DatosAlumnos; no se selecciona uno automáticamente."
)


mask_restante = (
    resultado["ESTADO_DIAGNOSTICO_124"].eq("")
)

resultado.loc[
    mask_restante,
    "ESTADO_DIAGNOSTICO_124",
] = "EVIDENCIA_INSUFICIENTE_DATOSALUMNOS"

resultado.loc[
    mask_restante,
    "MOTIVO_PENDIENTE",
] = (
    "La evidencia disponible no permite resolver el nivel "
    "con las reglas conservadoras aplicadas."
)


resultado["NIVEL_CANDIDATO"] = pd.to_numeric(
    resultado["NIVEL_CANDIDATO"],
    errors="coerce",
).astype("Int64")

resultado["ANIO_CURRICULAR_CANDIDATO"] = (
    (
        resultado["NIVEL_CANDIDATO"] + 1
    ) // 2
).astype("Int64")


resumen_estados = (
    resultado["ESTADO_DIAGNOSTICO_124"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

candidatos = resultado[
    resultado["ESTADO_DIAGNOSTICO_124"].eq(
        "CANDIDATO_PLAN_EXACTO_REQUIERE_VALIDACION"
    )
].copy()

pendientes_reales = resultado[
    ~resultado["ESTADO_DIAGNOSTICO_124"].eq(
        "CANDIDATO_PLAN_EXACTO_REQUIERE_VALIDACION"
    )
].copy()


resultado.to_csv(
    SALIDA / "01_DIAGNOSTICO_COMPLETO_124.tsv",
    sep="\t",
    index=False,
)

candidatos.to_csv(
    SALIDA / "02_CANDIDATOS_PLAN_EXACTO.tsv",
    sep="\t",
    index=False,
)

pendientes_reales.to_csv(
    SALIDA / "03_PENDIENTES_REALES_124.tsv",
    sep="\t",
    index=False,
)

resumen_estados.to_csv(
    SALIDA / "04_RESUMEN_ESTADOS.tsv",
    sep="\t",
    index=False,
)

columnas_detectadas.to_csv(
    SALIDA / "05_COLUMNAS_DETECTADAS_DATOSALUMNOS.tsv",
    sep="\t",
    index=False,
)

inventario_columnas.to_csv(
    SALIDA / "06_INVENTARIO_COLUMNAS_DATOSALUMNOS.tsv",
    sep="\t",
    index=False,
)


excel = (
    SALIDA
    / "DIAGNOSTICO_124_SIN_HISTORIA.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_estados.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    candidatos.to_excel(
        writer,
        sheet_name="CANDIDATOS",
        index=False,
    )

    pendientes_reales.to_excel(
        writer,
        sheet_name="PENDIENTES",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="DETALLE_124",
        index=False,
    )

    columnas_detectadas.to_excel(
        writer,
        sheet_name="COLUMNAS_DETECTADAS",
        index=False,
    )

    inventario_columnas.to_excel(
        writer,
        sheet_name="INVENTARIO_COLUMNAS",
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


manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia": 2025,
    "casos_analizados": len(resultado),
    "candidatos_plan_exacto": len(candidatos),
    "pendientes_reales": len(pendientes_reales),
    "asignaciones_automaticas": 0,
    "fuentes_modificadas": False,
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


print()
print("=" * 94)
print("DIAGNÓSTICO DE LOS 124 CASOS SIN HISTORIA")
print("=" * 94)
print(f"Casos analizados: {len(resultado)}")
print()
print("COLUMNAS DETECTADAS")
print("-" * 94)

for _, fila in columnas_detectadas.iterrows():
    print(
        f"{fila['ROL']}: "
        f"{fila['COLUMNA'] or 'NO ENCONTRADA'}"
    )

print()
print("RESULTADO")
print("-" * 94)

for _, fila in resumen_estados.iterrows():
    print(
        f"{fila['ESTADO']}: {fila['CASOS']}"
    )

print()
print(
    "Candidatos con plan exacto y nivel único: "
    f"{len(candidatos)}"
)
print(
    "Pendientes reales: "
    f"{len(pendientes_reales)}"
)
print("Asignaciones automáticas realizadas: 0")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 94)
