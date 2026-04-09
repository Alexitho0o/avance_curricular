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

DIAG_124 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "DIAGNOSTICO_124_SIN_HISTORIA_20260702_002138"
    / "01_DIAGNOSTICO_COMPLETO_124.tsv"
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
    / f"DIAGNOSTICO_124_POR_CODCLI_{timestamp}"
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


def unir_documentos(serie):
    valores = sorted({
        norm_documento(valor)
        for valor in serie
        if norm_documento(valor)
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


for ruta in (DIAG_124, PROMEDIOS):
    if not ruta.exists():
        raise RuntimeError(f"No existe: {ruta}")


# ============================================================
# 1. CASOS PENDIENTES
# ============================================================

casos = pd.read_csv(
    DIAG_124,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

casos = casos[
    casos["ESTADO_DIAGNOSTICO_124"].eq(
        "SIN_REGISTRO_EN_DATOSALUMNOS"
    )
].copy()

if len(casos) != 124:
    raise RuntimeError(
        f"Se esperaban 124 casos y se encontraron {len(casos)}."
    )

if casos["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Existen ID_FILA_5809 duplicados."
    )


# ============================================================
# 2. IDENTIFICAR CODCLI EN EL UNIVERSO 5809
# ============================================================

col_codcli_casos = buscar_columna(
    casos,
    [
        "CODCLI",
        "CODCLI_5809",
        "CODIGO_ALUMNO",
    ],
)

if not col_codcli_casos:
    candidatas = [
        columna
        for columna in casos.columns
        if "CODCLI" in norm_col(columna)
    ]

    raise RuntimeError(
        "No se encontró una columna CODCLI utilizable en los "
        "124 casos. Columnas candidatas: "
        + " | ".join(candidatas)
    )

casos["CODCLI_5809_NORM"] = (
    casos[col_codcli_casos].map(norm_codigo)
)

casos["DOCUMENTO_5809_NORM"] = (
    casos["DOCUMENTO_NORM"].map(norm_documento)
)

sin_codcli = casos[
    casos["CODCLI_5809_NORM"].eq("")
].copy()


# ============================================================
# 3. DATOSALUMNOS
# ============================================================

datos = pd.read_excel(
    PROMEDIOS,
    sheet_name="DatosAlumnos",
    dtype=object,
)

d_codcli = buscar_columna(
    datos,
    ["CODCLI"],
    obligatoria=True,
    contexto="DatosAlumnos/CODCLI",
)

d_documento = buscar_columna(
    datos,
    [
        "RUT",
        "NUM_DOCUMENTO",
        "N_DOC",
        "DOCUMENTO",
    ],
    obligatoria=True,
    contexto="DatosAlumnos/documento",
)

d_carrera = buscar_columna(
    datos,
    [
        "CODCARPR",
        "CODCARR",
        "COD_CAR",
        "CODIGO_CARRERA",
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
        "NIVEL_ACADEMICO",
    ],
    obligatoria=True,
    contexto="DatosAlumnos/nivel",
)

d = datos.copy()

d["CODCLI_DATOS_NORM"] = (
    d[d_codcli].map(norm_codigo)
)

d["DOCUMENTO_DATOS_NORM"] = (
    d[d_documento].map(norm_documento)
)

d["CARRERA_DATOS_NORM"] = (
    d[d_carrera].map(norm_codigo)
)

d["NIVEL_DATOS_NUM"] = pd.to_numeric(
    d[d_nivel],
    errors="coerce",
)

d = d[
    d["CODCLI_DATOS_NORM"].ne("")
].copy()


# ============================================================
# 4. RESUMEN POR CODCLI
# ============================================================

resumen_codcli = (
    d.groupby(
        "CODCLI_DATOS_NORM",
        dropna=False,
    )
    .agg(
        REGISTROS_DATOSALUMNOS_CODCLI=(
            "CODCLI_DATOS_NORM",
            "size",
        ),
        N_DOCUMENTOS_DATOS_CODCLI=(
            "DOCUMENTO_DATOS_NORM",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        DOCUMENTOS_DATOS_CODCLI=(
            "DOCUMENTO_DATOS_NORM",
            unir_documentos,
        ),
        N_CARRERAS_DATOS_CODCLI=(
            "CARRERA_DATOS_NORM",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CARRERAS_DATOS_CODCLI=(
            "CARRERA_DATOS_NORM",
            unir_unicos,
        ),
        N_NIVELES_DATOS_CODCLI=(
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
        NIVELES_DATOS_CODCLI=(
            "NIVEL_DATOS_NUM",
            unir_niveles,
        ),
        NIVEL_MIN_DATOS_CODCLI=(
            "NIVEL_DATOS_NUM",
            "min",
        ),
        NIVEL_MAX_DATOS_CODCLI=(
            "NIVEL_DATOS_NUM",
            "max",
        ),
    )
    .reset_index()
)


# ============================================================
# 5. CRUCE
# ============================================================

resultado = casos.merge(
    resumen_codcli,
    left_on="CODCLI_5809_NORM",
    right_on="CODCLI_DATOS_NORM",
    how="left",
    validate="many_to_one",
)

if len(resultado) != 124:
    raise RuntimeError(
        "El cruce alteró el universo de 124 casos."
    )


# ============================================================
# 6. CLASIFICACIÓN
# ============================================================

resultado["ESTADO_DIAGNOSTICO_CODCLI"] = ""
resultado["NIVEL_CANDIDATO_CODCLI"] = pd.NA
resultado["ASIGNACION_AUTOMATICA"] = "NO"
resultado["MOTIVO_PENDIENTE_CODCLI"] = ""

registros = pd.to_numeric(
    resultado["REGISTROS_DATOSALUMNOS_CODCLI"],
    errors="coerce",
).fillna(0)

n_documentos = pd.to_numeric(
    resultado["N_DOCUMENTOS_DATOS_CODCLI"],
    errors="coerce",
).fillna(0)

n_carreras = pd.to_numeric(
    resultado["N_CARRERAS_DATOS_CODCLI"],
    errors="coerce",
).fillna(0)

n_niveles = pd.to_numeric(
    resultado["N_NIVELES_DATOS_CODCLI"],
    errors="coerce",
).fillna(0)

nivel_max = pd.to_numeric(
    resultado["NIVEL_MAX_DATOS_CODCLI"],
    errors="coerce",
)

nivel_max_plan = pd.to_numeric(
    resultado.get(
        "NIVEL_MAX_PLAN_DIAG",
        pd.Series(index=resultado.index, dtype=float),
    ),
    errors="coerce",
)


mask_sin_codcli = (
    resultado["CODCLI_5809_NORM"].eq("")
)

resultado.loc[
    mask_sin_codcli,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "SIN_CODCLI_EN_5809"

resultado.loc[
    mask_sin_codcli,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "El caso no contiene CODCLI utilizable en la trazabilidad 5809."
)


mask_sin_coincidencia = (
    ~mask_sin_codcli
    & registros.eq(0)
)

resultado.loc[
    mask_sin_coincidencia,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "CODCLI_NO_ENCONTRADO_EN_DATOSALUMNOS"

resultado.loc[
    mask_sin_coincidencia,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "El CODCLI de 5809 no aparece en DatosAlumnos."
)


mask_codcli_ambiguo = (
    registros.gt(0)
    & n_documentos.gt(1)
)

resultado.loc[
    mask_codcli_ambiguo,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "CODCLI_ASOCIADO_A_MULTIPLES_DOCUMENTOS"

resultado.loc[
    mask_codcli_ambiguo,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "El mismo CODCLI aparece asociado a más de un documento."
)


mask_sin_nivel = (
    registros.gt(0)
    & n_documentos.le(1)
    & n_niveles.eq(0)
)

resultado.loc[
    mask_sin_nivel,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "CODCLI_ENCONTRADO_SIN_NIVEL"

resultado.loc[
    mask_sin_nivel,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "Existe coincidencia por CODCLI, pero no hay nivel numérico."
)


mask_unico = (
    registros.gt(0)
    & n_documentos.eq(1)
    & n_carreras.eq(1)
    & n_niveles.eq(1)
    & nivel_max.notna()
    & resultado["ESTADO_DIAGNOSTICO_CODCLI"].eq("")
)

resultado.loc[
    mask_unico,
    "NIVEL_CANDIDATO_CODCLI",
] = nivel_max.loc[
    mask_unico
].astype("Int64")

mask_unico_dentro_plan = (
    mask_unico
    & nivel_max.ge(1)
    & nivel_max.le(nivel_max_plan)
)

resultado.loc[
    mask_unico_dentro_plan,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "CANDIDATO_CODCLI_UNICO_REQUIERE_VALIDACION"

resultado.loc[
    mask_unico_dentro_plan,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "CODCLI único, documento único, carrera única y nivel único "
    "dentro de la malla. Falta demostrar compatibilidad entre "
    "CODCARPR y el CODPESTUD actual."
)


mask_unico_supera = (
    mask_unico
    & ~mask_unico_dentro_plan
)

resultado.loc[
    mask_unico_supera,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "CONFLICTO_NIVEL_CODCLI_SUPERA_PLAN"

resultado.loc[
    mask_unico_supera,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "El nivel observado por CODCLI supera el máximo del plan."
)


mask_multiples = (
    registros.gt(0)
    & resultado["ESTADO_DIAGNOSTICO_CODCLI"].eq("")
)

resultado.loc[
    mask_multiples,
    "ESTADO_DIAGNOSTICO_CODCLI",
] = "CODCLI_CON_MULTIPLES_TRAYECTORIAS"

resultado.loc[
    mask_multiples,
    "MOTIVO_PENDIENTE_CODCLI",
] = (
    "El CODCLI presenta más de una carrera o más de un nivel."
)


resultado["NIVEL_CANDIDATO_CODCLI"] = pd.to_numeric(
    resultado["NIVEL_CANDIDATO_CODCLI"],
    errors="coerce",
).astype("Int64")

resultado["ANIO_CURRICULAR_CANDIDATO_CODCLI"] = (
    (
        resultado["NIVEL_CANDIDATO_CODCLI"] + 1
    ) // 2
).astype("Int64")


# ============================================================
# 7. RESÚMENES
# ============================================================

resumen = (
    resultado["ESTADO_DIAGNOSTICO_CODCLI"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

candidatos = resultado[
    resultado["ESTADO_DIAGNOSTICO_CODCLI"].eq(
        "CANDIDATO_CODCLI_UNICO_REQUIERE_VALIDACION"
    )
].copy()

pendientes = resultado[
    ~resultado["ESTADO_DIAGNOSTICO_CODCLI"].eq(
        "CANDIDATO_CODCLI_UNICO_REQUIERE_VALIDACION"
    )
].copy()

conflictos_documento = resultado[
    resultado["ESTADO_DIAGNOSTICO_CODCLI"].eq(
        "CODCLI_ASOCIADO_A_MULTIPLES_DOCUMENTOS"
    )
].copy()


# ============================================================
# 8. EXPORTACIÓN
# ============================================================

resultado.to_csv(
    SALIDA / "01_DIAGNOSTICO_COMPLETO_124_CODCLI.tsv",
    sep="\t",
    index=False,
)

candidatos.to_csv(
    SALIDA / "02_CANDIDATOS_CODCLI_UNICO.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    SALIDA / "03_PENDIENTES_CODCLI.tsv",
    sep="\t",
    index=False,
)

conflictos_documento.to_csv(
    SALIDA / "04_CONFLICTOS_CODCLI_DOCUMENTO.tsv",
    sep="\t",
    index=False,
)

resumen.to_csv(
    SALIDA / "05_RESUMEN_ESTADOS.tsv",
    sep="\t",
    index=False,
)

sin_codcli.to_csv(
    SALIDA / "06_CASOS_SIN_CODCLI_5809.tsv",
    sep="\t",
    index=False,
)


excel = (
    SALIDA
    / "DIAGNOSTICO_124_POR_CODCLI.xlsx"
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

    candidatos.to_excel(
        writer,
        sheet_name="CANDIDATOS",
        index=False,
    )

    pendientes.to_excel(
        writer,
        sheet_name="PENDIENTES",
        index=False,
    )

    conflictos_documento.to_excel(
        writer,
        sheet_name="CONFLICTOS_DOCUMENTO",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="DETALLE_124",
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
    "llave_diagnostico": "CODCLI",
    "candidatos_codcli_unico": len(candidatos),
    "pendientes": len(pendientes),
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
print("=" * 96)
print("DIAGNÓSTICO DE LOS 124 CASOS MEDIANTE CODCLI")
print("=" * 96)
print(f"Casos analizados: {len(resultado)}")
print(f"Columna CODCLI de 5809: {col_codcli_casos}")
print()
print("RESULTADO")
print("-" * 96)

for _, fila in resumen.iterrows():
    print(
        f"{fila['ESTADO']}: {fila['CASOS']}"
    )

print()
print(
    "Candidatos CODCLI único que requieren validación: "
    f"{len(candidatos)}"
)
print(f"Pendientes: {len(pendientes)}")
print("Asignaciones automáticas realizadas: 0")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 96)
