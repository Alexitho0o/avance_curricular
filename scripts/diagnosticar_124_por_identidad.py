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
    / f"DIAGNOSTICO_124_POR_IDENTIDAD_{timestamp}"
)

SALIDA.mkdir(parents=True, exist_ok=False)


def norm_col(valor):
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"[^A-Z0-9]+", "_", texto).strip("_")


def norm_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"[^A-Z0-9]+", "", texto)


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


def norm_fecha(valor):
    fecha = pd.to_datetime(
        valor,
        errors="coerce",
        dayfirst=True,
    )

    if pd.isna(fecha):
        return ""

    return fecha.strftime("%Y%m%d")


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


def unir_unicos(serie, normalizador=norm_codigo):
    valores = sorted({
        normalizador(valor)
        for valor in serie
        if normalizador(valor)
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
# 1. LEER LOS 124 CASOS
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
# 2. DETECTAR CAMPOS PERSONALES EN LA TRAZABILIDAD 5809
# ============================================================

c_nombres = buscar_columna(
    casos,
    ["NOMBRES"],
    obligatoria=True,
    contexto="124 casos/NOMBRES",
)

c_paterno = buscar_columna(
    casos,
    ["PRIMER_APELLIDO"],
    obligatoria=True,
    contexto="124 casos/PRIMER_APELLIDO",
)

c_materno = buscar_columna(
    casos,
    ["SEGUNDO_APELLIDO"],
    obligatoria=True,
    contexto="124 casos/SEGUNDO_APELLIDO",
)

c_fecha = buscar_columna(
    casos,
    ["FECHA_NACIMIENTO"],
    obligatoria=True,
    contexto="124 casos/FECHA_NACIMIENTO",
)

casos["NOMBRES_5809_NORM"] = (
    casos[c_nombres].map(norm_texto)
)

casos["PATERNO_5809_NORM"] = (
    casos[c_paterno].map(norm_texto)
)

casos["MATERNO_5809_NORM"] = (
    casos[c_materno].map(norm_texto)
)

casos["FECHA_NAC_5809_NORM"] = (
    casos[c_fecha].map(norm_fecha)
)

casos["CLAVE_IDENTIDAD_5809"] = (
    casos["NOMBRES_5809_NORM"]
    + "|"
    + casos["PATERNO_5809_NORM"]
    + "|"
    + casos["MATERNO_5809_NORM"]
    + "|"
    + casos["FECHA_NAC_5809_NORM"]
)

casos["IDENTIDAD_5809_COMPLETA"] = (
    casos[
        [
            "NOMBRES_5809_NORM",
            "PATERNO_5809_NORM",
            "MATERNO_5809_NORM",
            "FECHA_NAC_5809_NORM",
        ]
    ]
    .ne("")
    .all(axis=1)
)


# ============================================================
# 3. DATOSALUMNOS
# ============================================================

datos = pd.read_excel(
    PROMEDIOS,
    sheet_name="DatosAlumnos",
    dtype=object,
)

d_nombres = buscar_columna(
    datos,
    ["NOMBRES", "NOMBRE"],
    obligatoria=True,
    contexto="DatosAlumnos/nombres",
)

d_paterno = buscar_columna(
    datos,
    ["APELLIDO PATERNO", "PATERNO"],
    obligatoria=True,
    contexto="DatosAlumnos/apellido paterno",
)

d_materno = buscar_columna(
    datos,
    ["APELLIDO MATERNO", "MATERNO"],
    obligatoria=True,
    contexto="DatosAlumnos/apellido materno",
)

d_fecha = buscar_columna(
    datos,
    ["FECHANACIMIENTO", "FECHA_NACIMIENTO"],
    obligatoria=True,
    contexto="DatosAlumnos/fecha nacimiento",
)

d_rut = buscar_columna(
    datos,
    ["RUT"],
    obligatoria=True,
    contexto="DatosAlumnos/RUT",
)

d_codcli = buscar_columna(
    datos,
    ["CODCLI"],
    obligatoria=True,
    contexto="DatosAlumnos/CODCLI",
)

d_carrera = buscar_columna(
    datos,
    ["CODCARPR"],
    obligatoria=True,
    contexto="DatosAlumnos/CODCARPR",
)

d_nivel = buscar_columna(
    datos,
    ["NIVEL"],
    obligatoria=True,
    contexto="DatosAlumnos/NIVEL",
)

d = datos.copy()

d["NOMBRES_DATOS_NORM"] = (
    d[d_nombres].map(norm_texto)
)

d["PATERNO_DATOS_NORM"] = (
    d[d_paterno].map(norm_texto)
)

d["MATERNO_DATOS_NORM"] = (
    d[d_materno].map(norm_texto)
)

d["FECHA_NAC_DATOS_NORM"] = (
    d[d_fecha].map(norm_fecha)
)

d["RUT_DATOS_NORM"] = (
    d[d_rut].map(norm_documento)
)

d["CODCLI_DATOS_NORM"] = (
    d[d_codcli].map(norm_codigo)
)

d["CARRERA_DATOS_NORM"] = (
    d[d_carrera].map(norm_codigo)
)

d["NIVEL_DATOS_NUM"] = pd.to_numeric(
    d[d_nivel],
    errors="coerce",
)

d["CLAVE_IDENTIDAD_DATOS"] = (
    d["NOMBRES_DATOS_NORM"]
    + "|"
    + d["PATERNO_DATOS_NORM"]
    + "|"
    + d["MATERNO_DATOS_NORM"]
    + "|"
    + d["FECHA_NAC_DATOS_NORM"]
)

d = d[
    d[
        [
            "NOMBRES_DATOS_NORM",
            "PATERNO_DATOS_NORM",
            "MATERNO_DATOS_NORM",
            "FECHA_NAC_DATOS_NORM",
        ]
    ]
    .ne("")
    .all(axis=1)
].copy()


# ============================================================
# 4. RESUMEN POR IDENTIDAD EXACTA
# ============================================================

resumen_identidad = (
    d.groupby(
        "CLAVE_IDENTIDAD_DATOS",
        dropna=False,
    )
    .agg(
        REGISTROS_IDENTIDAD=(
            "CLAVE_IDENTIDAD_DATOS",
            "size",
        ),
        N_RUT_IDENTIDAD=(
            "RUT_DATOS_NORM",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        RUT_DATOS_IDENTIDAD=(
            "RUT_DATOS_NORM",
            lambda serie: unir_unicos(
                serie,
                norm_documento,
            ),
        ),
        N_CODCLI_IDENTIDAD=(
            "CODCLI_DATOS_NORM",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CODCLI_DATOS_IDENTIDAD=(
            "CODCLI_DATOS_NORM",
            unir_unicos,
        ),
        N_CARRERAS_IDENTIDAD=(
            "CARRERA_DATOS_NORM",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
        CARRERAS_DATOS_IDENTIDAD=(
            "CARRERA_DATOS_NORM",
            unir_unicos,
        ),
        N_NIVELES_IDENTIDAD=(
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
        NIVELES_DATOS_IDENTIDAD=(
            "NIVEL_DATOS_NUM",
            unir_niveles,
        ),
        NIVEL_MIN_IDENTIDAD=(
            "NIVEL_DATOS_NUM",
            "min",
        ),
        NIVEL_MAX_IDENTIDAD=(
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
    resumen_identidad,
    left_on="CLAVE_IDENTIDAD_5809",
    right_on="CLAVE_IDENTIDAD_DATOS",
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

resultado["ESTADO_IDENTIDAD"] = ""
resultado["NIVEL_CANDIDATO_IDENTIDAD"] = pd.NA
resultado["ASIGNACION_AUTOMATICA"] = "NO"
resultado["MOTIVO_PENDIENTE_IDENTIDAD"] = ""

registros = pd.to_numeric(
    resultado["REGISTROS_IDENTIDAD"],
    errors="coerce",
).fillna(0)

n_rut = pd.to_numeric(
    resultado["N_RUT_IDENTIDAD"],
    errors="coerce",
).fillna(0)

n_codcli = pd.to_numeric(
    resultado["N_CODCLI_IDENTIDAD"],
    errors="coerce",
).fillna(0)

n_carreras = pd.to_numeric(
    resultado["N_CARRERAS_IDENTIDAD"],
    errors="coerce",
).fillna(0)

n_niveles = pd.to_numeric(
    resultado["N_NIVELES_IDENTIDAD"],
    errors="coerce",
).fillna(0)

nivel_max = pd.to_numeric(
    resultado["NIVEL_MAX_IDENTIDAD"],
    errors="coerce",
)

nivel_max_plan = pd.to_numeric(
    resultado["NIVEL_MAX_PLAN_DIAG"],
    errors="coerce",
)


mask_identidad_incompleta = (
    ~resultado["IDENTIDAD_5809_COMPLETA"]
)

resultado.loc[
    mask_identidad_incompleta,
    "ESTADO_IDENTIDAD",
] = "IDENTIDAD_5809_INCOMPLETA"


mask_sin_coincidencia = (
    resultado["IDENTIDAD_5809_COMPLETA"]
    & registros.eq(0)
)

resultado.loc[
    mask_sin_coincidencia,
    "ESTADO_IDENTIDAD",
] = "SIN_COINCIDENCIA_IDENTIDAD_EXACTA"


mask_identidad_ambigua = (
    registros.gt(0)
    & (
        n_rut.gt(1)
        | n_codcli.gt(1)
        | n_carreras.gt(1)
        | n_niveles.gt(1)
    )
)

resultado.loc[
    mask_identidad_ambigua,
    "ESTADO_IDENTIDAD",
] = "IDENTIDAD_EXACTA_MULTIPLES_TRAYECTORIAS"


mask_unico = (
    registros.gt(0)
    & n_rut.eq(1)
    & n_codcli.eq(1)
    & n_carreras.eq(1)
    & n_niveles.eq(1)
    & nivel_max.notna()
    & resultado["ESTADO_IDENTIDAD"].eq("")
)

resultado.loc[
    mask_unico,
    "NIVEL_CANDIDATO_IDENTIDAD",
] = nivel_max.loc[
    mask_unico
].astype("Int64")

mask_unico_valido = (
    mask_unico
    & nivel_max.ge(1)
    & nivel_max.le(nivel_max_plan)
)

resultado.loc[
    mask_unico_valido,
    "ESTADO_IDENTIDAD",
] = "CANDIDATO_IDENTIDAD_EXACTA_REQUIERE_VALIDACION"

resultado.loc[
    mask_unico_valido,
    "MOTIVO_PENDIENTE_IDENTIDAD",
] = (
    "Coincidencia exacta de nombres, apellidos y fecha de "
    "nacimiento; existe una trayectoria única y un nivel "
    "dentro de la malla. Falta validar la carrera observada "
    "contra el CODPESTUD vigente."
)


mask_unico_supera = (
    mask_unico
    & ~mask_unico_valido
)

resultado.loc[
    mask_unico_supera,
    "ESTADO_IDENTIDAD",
] = "CONFLICTO_NIVEL_IDENTIDAD_SUPERA_PLAN"


mask_restante = (
    resultado["ESTADO_IDENTIDAD"].eq("")
)

resultado.loc[
    mask_restante,
    "ESTADO_IDENTIDAD",
] = "EVIDENCIA_IDENTIDAD_INSUFICIENTE"


resultado["NIVEL_CANDIDATO_IDENTIDAD"] = pd.to_numeric(
    resultado["NIVEL_CANDIDATO_IDENTIDAD"],
    errors="coerce",
).astype("Int64")


# ============================================================
# 7. SALIDAS
# ============================================================

resumen = (
    resultado["ESTADO_IDENTIDAD"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

candidatos = resultado[
    resultado["ESTADO_IDENTIDAD"].eq(
        "CANDIDATO_IDENTIDAD_EXACTA_REQUIERE_VALIDACION"
    )
].copy()

pendientes = resultado[
    ~resultado["ESTADO_IDENTIDAD"].eq(
        "CANDIDATO_IDENTIDAD_EXACTA_REQUIERE_VALIDACION"
    )
].copy()


resultado.to_csv(
    SALIDA / "01_DIAGNOSTICO_COMPLETO_124_IDENTIDAD.tsv",
    sep="\t",
    index=False,
)

candidatos.to_csv(
    SALIDA / "02_CANDIDATOS_IDENTIDAD_EXACTA.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    SALIDA / "03_PENDIENTES_IDENTIDAD.tsv",
    sep="\t",
    index=False,
)

resumen.to_csv(
    SALIDA / "04_RESUMEN_ESTADOS.tsv",
    sep="\t",
    index=False,
)


excel = (
    SALIDA
    / "DIAGNOSTICO_124_POR_IDENTIDAD.xlsx"
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
    "llave_diagnostico": (
        "NOMBRES+PRIMER_APELLIDO+SEGUNDO_APELLIDO+"
        "FECHA_NACIMIENTO"
    ),
    "candidatos_identidad_exacta": len(candidatos),
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
print("DIAGNÓSTICO DE LOS 124 CASOS POR IDENTIDAD PERSONAL")
print("=" * 96)
print(f"Casos analizados: {len(resultado)}")
print(
    "Llave: NOMBRES + PRIMER_APELLIDO + "
    "SEGUNDO_APELLIDO + FECHA_NACIMIENTO"
)
print()
print("RESULTADO")
print("-" * 96)

for _, fila in resumen.iterrows():
    print(
        f"{fila['ESTADO']}: {fila['CASOS']}"
    )

print()
print(
    "Candidatos por identidad exacta: "
    f"{len(candidatos)}"
)
print("Asignaciones automáticas realizadas: 0")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 96)
