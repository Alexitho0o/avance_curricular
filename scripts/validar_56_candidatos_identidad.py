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

CANDIDATOS_56 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "DIAGNOSTICO_124_POR_IDENTIDAD_20260702_002433"
    / "02_CANDIDATOS_IDENTIDAD_EXACTA.tsv"
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
    / f"VALIDACION_56_IDENTIDAD_CARRERA_{timestamp}"
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


for ruta in (CANDIDATOS_56, MALLAS):
    if not ruta.exists():
        raise RuntimeError(f"No existe: {ruta}")


# ============================================================
# 1. CANDIDATOS
# ============================================================

candidatos = pd.read_csv(
    CANDIDATOS_56,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(candidatos) != 56:
    raise RuntimeError(
        f"Se esperaban 56 candidatos y se encontraron "
        f"{len(candidatos)}."
    )

if candidatos["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Existen ID_FILA_5809 duplicados."
    )

columnas_requeridas = [
    "CODPESTUD_RESUELTO",
    "CARRERAS_DATOS_IDENTIDAD",
    "NIVEL_CANDIDATO_IDENTIDAD",
    "NIVEL_MAX_PLAN_DIAG",
]

faltantes = [
    columna
    for columna in columnas_requeridas
    if columna not in candidatos.columns
]

if faltantes:
    raise RuntimeError(
        "Faltan columnas en candidatos: "
        + " | ".join(faltantes)
    )

candidatos["CODPESTUD_RESUELTO_NORM"] = (
    candidatos["CODPESTUD_RESUELTO"]
    .map(norm_codigo)
)

candidatos["CODCARPR_DATOS_NORM"] = (
    candidatos["CARRERAS_DATOS_IDENTIDAD"]
    .map(norm_codigo)
)

candidatos["NIVEL_CANDIDATO_NUM"] = pd.to_numeric(
    candidatos["NIVEL_CANDIDATO_IDENTIDAD"],
    errors="coerce",
)

candidatos["NIVEL_MAX_PLAN_NUM"] = pd.to_numeric(
    candidatos["NIVEL_MAX_PLAN_DIAG"],
    errors="coerce",
)


# ============================================================
# 2. MAPA CODPESTUD → CODCARR
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

m_carrera = buscar_columna(
    mallas,
    [
        "CODCARR",
        "CODCARPR",
        "COD_CAR",
    ],
    obligatoria=True,
    contexto="Mallas/CODCARR",
)

mapa = mallas[
    [m_plan, m_carrera]
].copy()

mapa["CODPESTUD_MALLA_NORM"] = (
    mapa[m_plan].map(norm_codigo)
)

mapa["CODCARR_PLAN_NORM"] = (
    mapa[m_carrera].map(norm_codigo)
)

mapa = (
    mapa[
        mapa["CODPESTUD_MALLA_NORM"].ne("")
    ]
    .groupby(
        "CODPESTUD_MALLA_NORM",
        dropna=False,
    )
    .agg(
        CODCARR_PLAN_NORM=(
            "CODCARR_PLAN_NORM",
            unir_unicos,
        ),
        N_CODCARR_PLAN=(
            "CODCARR_PLAN_NORM",
            lambda serie: len({
                valor
                for valor in serie
                if valor
            }),
        ),
    )
    .reset_index()
)

if mapa["CODPESTUD_MALLA_NORM"].duplicated().any():
    raise RuntimeError(
        "El mapa CODPESTUD-CODCARR quedó duplicado."
    )


# ============================================================
# 3. CRUCE
# ============================================================

resultado = candidatos.merge(
    mapa,
    left_on="CODPESTUD_RESUELTO_NORM",
    right_on="CODPESTUD_MALLA_NORM",
    how="left",
    validate="many_to_one",
)

if len(resultado) != 56:
    raise RuntimeError(
        "El cruce alteró el universo de 56 candidatos."
    )

if resultado["CODCARR_PLAN_NORM"].fillna("").eq("").any():
    faltantes_plan = (
        resultado.loc[
            resultado[
                "CODCARR_PLAN_NORM"
            ].fillna("").eq(""),
            "CODPESTUD_RESUELTO_NORM",
        ]
        .drop_duplicates()
        .tolist()
    )

    raise RuntimeError(
        "Existen CODPESTUD sin CODCARR en la malla: "
        + " | ".join(faltantes_plan)
    )


# ============================================================
# 4. VALIDACIÓN
# ============================================================

resultado["ESTADO_VALIDACION_56"] = ""
resultado["NIVEL_VALIDABLE"] = pd.NA
resultado["ANIO_CURRICULAR_VALIDABLE"] = pd.NA
resultado["MOTIVO_VALIDACION"] = ""
resultado["ASIGNACION_AUTOMATICA"] = "NO"

n_carreras_plan = pd.to_numeric(
    resultado["N_CODCARR_PLAN"],
    errors="coerce",
).fillna(0)

nivel = resultado["NIVEL_CANDIDATO_NUM"]
nivel_max = resultado["NIVEL_MAX_PLAN_NUM"]

mask_plan_ambiguo = n_carreras_plan.ne(1)

resultado.loc[
    mask_plan_ambiguo,
    "ESTADO_VALIDACION_56",
] = "CODPESTUD_CON_CODCARR_AMBIGUO"

resultado.loc[
    mask_plan_ambiguo,
    "MOTIVO_VALIDACION",
] = (
    "El CODPESTUD aparece asociado a más de un CODCARR "
    "en la fuente de mallas."
)


mask_carrera_exacta = (
    resultado["ESTADO_VALIDACION_56"].eq("")
    & resultado["CODCARPR_DATOS_NORM"].ne("")
    & resultado["CODCARPR_DATOS_NORM"].eq(
        resultado["CODCARR_PLAN_NORM"]
    )
)

mask_carrera_distinta = (
    resultado["ESTADO_VALIDACION_56"].eq("")
    & resultado["CODCARPR_DATOS_NORM"].ne("")
    & ~resultado["CODCARPR_DATOS_NORM"].eq(
        resultado["CODCARR_PLAN_NORM"]
    )
)

mask_carrera_vacia = (
    resultado["ESTADO_VALIDACION_56"].eq("")
    & resultado["CODCARPR_DATOS_NORM"].eq("")
)

resultado.loc[
    mask_carrera_distinta,
    "ESTADO_VALIDACION_56",
] = "CODCARPR_DISTINTO_DE_CODCARR_PLAN"

resultado.loc[
    mask_carrera_distinta,
    "MOTIVO_VALIDACION",
] = (
    "La carrera observada en DatosAlumnos no coincide "
    "con la carrera asociada al CODPESTUD vigente."
)

resultado.loc[
    mask_carrera_vacia,
    "ESTADO_VALIDACION_56",
] = "CODCARPR_DATOSALUMNOS_VACIO"

resultado.loc[
    mask_carrera_vacia,
    "MOTIVO_VALIDACION",
] = (
    "DatosAlumnos no entrega un código de carrera utilizable."
)


mask_nivel_valido = (
    mask_carrera_exacta
    & nivel.notna()
    & nivel.ge(1)
    & nivel.le(nivel_max)
)

resultado.loc[
    mask_nivel_valido,
    "ESTADO_VALIDACION_56",
] = "VALIDABLE_IDENTIDAD_CARRERA_NIVEL"

resultado.loc[
    mask_nivel_valido,
    "NIVEL_VALIDABLE",
] = nivel.loc[
    mask_nivel_valido
].astype("Int64")

resultado.loc[
    mask_nivel_valido,
    "ANIO_CURRICULAR_VALIDABLE",
] = (
    (
        nivel.loc[
            mask_nivel_valido
        ].astype("Int64") + 1
    ) // 2
)

resultado.loc[
    mask_nivel_valido,
    "MOTIVO_VALIDACION",
] = (
    "Identidad exacta, trayectoria única, CODCARPR igual "
    "al CODCARR del plan y nivel dentro del rango de la malla."
)


mask_nivel_supera = (
    mask_carrera_exacta
    & (
        nivel.isna()
        | nivel.lt(1)
        | nivel.gt(nivel_max)
    )
)

resultado.loc[
    mask_nivel_supera,
    "ESTADO_VALIDACION_56",
] = "CONFLICTO_NIVEL_FUERA_DE_RANGO"

resultado.loc[
    mask_nivel_supera,
    "MOTIVO_VALIDACION",
] = (
    "La carrera coincide, pero el nivel está vacío, es menor "
    "que 1 o supera el nivel máximo del plan."
)


if resultado["ESTADO_VALIDACION_56"].eq("").any():
    raise RuntimeError(
        "Quedaron casos sin clasificación."
    )

resultado["NIVEL_VALIDABLE"] = pd.to_numeric(
    resultado["NIVEL_VALIDABLE"],
    errors="coerce",
).astype("Int64")

resultado["ANIO_CURRICULAR_VALIDABLE"] = pd.to_numeric(
    resultado["ANIO_CURRICULAR_VALIDABLE"],
    errors="coerce",
).astype("Int64")


# ============================================================
# 5. RESÚMENES
# ============================================================

resumen = (
    resultado["ESTADO_VALIDACION_56"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

validables = resultado[
    resultado["ESTADO_VALIDACION_56"].eq(
        "VALIDABLE_IDENTIDAD_CARRERA_NIVEL"
    )
].copy()

no_validables = resultado[
    ~resultado["ESTADO_VALIDACION_56"].eq(
        "VALIDABLE_IDENTIDAD_CARRERA_NIVEL"
    )
].copy()

cobertura_potencial = round(
    (1685 + len(validables)) / 2371 * 100,
    2,
)


# ============================================================
# 6. EXPORTACIÓN
# ============================================================

resultado.to_csv(
    SALIDA / "01_VALIDACION_COMPLETA_56.tsv",
    sep="\t",
    index=False,
)

validables.to_csv(
    SALIDA / "02_VALIDABLES_IDENTIDAD_CARRERA_NIVEL.tsv",
    sep="\t",
    index=False,
)

no_validables.to_csv(
    SALIDA / "03_NO_VALIDABLES.tsv",
    sep="\t",
    index=False,
)

resumen.to_csv(
    SALIDA / "04_RESUMEN_ESTADOS.tsv",
    sep="\t",
    index=False,
)

mapa.to_csv(
    SALIDA / "05_MAPA_CODPESTUD_CODCARR.tsv",
    sep="\t",
    index=False,
)


excel = (
    SALIDA
    / "VALIDACION_56_IDENTIDAD_CARRERA.xlsx"
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

    validables.to_excel(
        writer,
        sheet_name="VALIDABLES",
        index=False,
    )

    no_validables.to_excel(
        writer,
        sheet_name="NO_VALIDABLES",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="DETALLE_56",
        index=False,
    )

    mapa.to_excel(
        writer,
        sheet_name="MAPA_PLAN_CARRERA",
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
    "candidatos_analizados": len(resultado),
    "validables_identidad_carrera_nivel": len(validables),
    "no_validables": len(no_validables),
    "niveles_previamente_validados": 1685,
    "cobertura_potencial_pct": cobertura_potencial,
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
print("VALIDACIÓN DE LOS 56 CANDIDATOS POR CARRERA")
print("=" * 96)
print(f"Candidatos analizados: {len(resultado)}")
print()
print("RESULTADO")
print("-" * 96)

for _, fila in resumen.iterrows():
    print(
        f"{fila['ESTADO']}: {fila['CASOS']}"
    )

print()
print(
    "Casos validables por identidad, carrera y nivel: "
    f"{len(validables)}"
)
print(
    "Casos no validables: "
    f"{len(no_validables)}"
)
print(
    "Cobertura potencial si se aprueban los validables: "
    f"{cobertura_potencial}%"
)
print("Asignaciones automáticas realizadas: 0")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 96)
