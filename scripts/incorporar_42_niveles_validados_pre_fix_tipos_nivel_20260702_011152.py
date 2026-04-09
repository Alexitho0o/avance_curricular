#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json

import pandas as pd


RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

MATRIZ_BASE = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "RECALCULO_NIVELES_2371_CORREGIDO_20260702_001635"
    / "02_RESULTADOS"
    / "01_5809_TRAZABILIDAD_PLAN_MALLA_NIVEL.tsv"
)

VALIDABLES_42 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "VALIDACION_56_IDENTIDAD_CARRERA_20260702_002659"
    / "02_VALIDABLES_IDENTIDAD_CARRERA_NIVEL.tsv"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"INCORPORACION_42_NIVELES_VALIDADOS_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in (RESULTADOS, AUDITORIAS, REPORTES):
    carpeta.mkdir(parents=True, exist_ok=True)


def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


for ruta in (MATRIZ_BASE, VALIDABLES_42):
    if not ruta.exists():
        raise RuntimeError(f"No existe: {ruta}")


# ============================================================
# 1. LEER FUENTES
# ============================================================

base = pd.read_csv(
    MATRIZ_BASE,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

validables = pd.read_csv(
    VALIDABLES_42,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(base) != 2371:
    raise RuntimeError(
        f"Universo base inesperado: {len(base)}."
    )

if len(validables) != 42:
    raise RuntimeError(
        f"Se esperaban 42 casos validables y se encontraron "
        f"{len(validables)}."
    )

if base["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "La matriz base contiene ID_FILA_5809 duplicados."
    )

if validables["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Los 42 validables contienen ID_FILA_5809 duplicados."
    )


# ============================================================
# 2. VALIDAR CAMPOS REQUERIDOS
# ============================================================

columnas_validables = [
    "ID_FILA_5809",
    "NIVEL_VALIDABLE",
    "ANIO_CURRICULAR_VALIDABLE",
    "CODCARPR_DATOS_NORM",
    "CODCARR_PLAN_NORM",
    "CODPESTUD_RESUELTO",
    "ESTADO_VALIDACION_56",
]

faltantes = [
    columna
    for columna in columnas_validables
    if columna not in validables.columns
]

if faltantes:
    raise RuntimeError(
        "Faltan columnas en los 42 validables: "
        + " | ".join(faltantes)
    )

validables = validables[
    columnas_validables
].copy()

validables["NIVEL_VALIDABLE"] = pd.to_numeric(
    validables["NIVEL_VALIDABLE"],
    errors="coerce",
).astype("Int64")

validables["ANIO_CURRICULAR_VALIDABLE"] = pd.to_numeric(
    validables["ANIO_CURRICULAR_VALIDABLE"],
    errors="coerce",
).astype("Int64")

if validables["NIVEL_VALIDABLE"].isna().any():
    raise RuntimeError(
        "Existen validables sin NIVEL_VALIDABLE."
    )

if validables[
    "ANIO_CURRICULAR_VALIDABLE"
].isna().any():
    raise RuntimeError(
        "Existen validables sin ANIO_CURRICULAR_VALIDABLE."
    )

if not validables[
    "ESTADO_VALIDACION_56"
].eq(
    "VALIDABLE_IDENTIDAD_CARRERA_NIVEL"
).all():
    raise RuntimeError(
        "Existe algún caso que no tiene el estado validable esperado."
    )

if not validables[
    "CODCARPR_DATOS_NORM"
].eq(
    validables["CODCARR_PLAN_NORM"]
).all():
    raise RuntimeError(
        "Existe algún caso con carrera distinta."
    )


# ============================================================
# 3. VERIFICAR QUE LOS 42 ESTABAN PENDIENTES
# ============================================================

estado_base = base[
    [
        "ID_FILA_5809",
        "ESTADO_NIVEL_FINAL",
        "ESTADO_TRAZABILIDAD_FINAL",
    ]
].copy()

control_previo = validables.merge(
    estado_base,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

if control_previo[
    "ESTADO_NIVEL_FINAL"
].eq("NIVEL_VALIDADO_PLAN_EXACTO").any():
    raise RuntimeError(
        "Al menos uno de los 42 ya estaba validado en la matriz base."
    )

if control_previo[
    "ESTADO_TRAZABILIDAD_FINAL"
].eq("TRAZABLE_PLAN_MALLA_NIVEL").any():
    raise RuntimeError(
        "Al menos uno de los 42 ya estaba trazable."
    )


# ============================================================
# 4. PREPARAR APORTE DE LOS 42
# ============================================================

aporte = validables.rename(
    columns={
        "NIVEL_VALIDABLE":
        "NIVEL_VALIDADO_IDENTIDAD_CARRERA",

        "ANIO_CURRICULAR_VALIDABLE":
        "ANIO_VALIDADO_IDENTIDAD_CARRERA",

        "CODCARPR_DATOS_NORM":
        "CODCARPR_EVIDENCIA_IDENTIDAD",

        "CODCARR_PLAN_NORM":
        "CODCARR_PLAN_VALIDADO",
    }
).copy()

resultado = base.merge(
    aporte,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
    suffixes=("", "_APORTE"),
)

if len(resultado) != 2371:
    raise RuntimeError(
        "El cruce alteró el universo de 2.371 estudiantes."
    )

mask_42 = resultado[
    "NIVEL_VALIDADO_IDENTIDAD_CARRERA"
].notna()

if int(mask_42.sum()) != 42:
    raise RuntimeError(
        f"Se esperaban 42 incorporaciones y se obtuvieron "
        f"{int(mask_42.sum())}."
    )


# ============================================================
# 5. MATERIALIZAR RESOLUCIÓN INTERNA
# ============================================================

resultado.loc[
    mask_42,
    "NIVEL_FINAL",
] = resultado.loc[
    mask_42,
    "NIVEL_VALIDADO_IDENTIDAD_CARRERA",
].astype("Int64")

resultado.loc[
    mask_42,
    "ANIO_CURRICULAR_FINAL",
] = resultado.loc[
    mask_42,
    "ANIO_VALIDADO_IDENTIDAD_CARRERA",
].astype("Int64")

resultado.loc[
    mask_42,
    "ESTADO_NIVEL_FINAL",
] = "NIVEL_VALIDADO_IDENTIDAD_CARRERA"

resultado.loc[
    mask_42,
    "METODO_RESOLUCION_NIVEL",
] = (
    "IDENTIDAD_PERSONAL_EXACTA_MAS_CARRERA_MAS_NIVEL"
)

resultado.loc[
    mask_42,
    "FUENTE_NIVEL_FINAL",
] = "PROMEDIOSDEALUMNOS::DatosAlumnos"

resultado.loc[
    mask_42,
    "OBSERVACION_NIVEL",
] = (
    "Identidad personal exacta; trayectoria única; "
    "CODCARPR igual al CODCARR del plan; "
    "nivel dentro del rango físico de la malla."
)

resultado.loc[
    mask_42,
    "ESTADO_TRAZABILIDAD_FINAL",
] = "TRAZABLE_PLAN_MALLA_NIVEL"

resultado["TIPO_RESPALDO_NIVEL"] = ""

resultado.loc[
    resultado["ESTADO_NIVEL_FINAL"].eq(
        "NIVEL_VALIDADO_PLAN_EXACTO"
    ),
    "TIPO_RESPALDO_NIVEL",
] = "DATO_OBSERVADO_PLAN_EXACTO"

resultado.loc[
    mask_42,
    "TIPO_RESPALDO_NIVEL",
] = "DECISION_TECNICA_INTERNA_DOCUMENTADA"

resultado["ES_REGLA_OFICIAL"] = "NO"

resultado["NOTA_RESPALDO"] = ""

resultado.loc[
    mask_42,
    "NOTA_RESPALDO",
] = (
    "Resolución técnica interna basada en identidad, carrera "
    "y nivel observados; no corresponde a una regla oficial "
    "explícita del instructivo."
)


# ============================================================
# 6. NORMALIZAR TIPOS
# ============================================================

resultado["NIVEL_FINAL"] = pd.to_numeric(
    resultado["NIVEL_FINAL"],
    errors="coerce",
).astype("Int64")

resultado["ANIO_CURRICULAR_FINAL"] = pd.to_numeric(
    resultado["ANIO_CURRICULAR_FINAL"],
    errors="coerce",
).astype("Int64")


# ============================================================
# 7. RESÚMENES
# ============================================================

trazables = resultado[
    resultado["ESTADO_TRAZABILIDAD_FINAL"].eq(
        "TRAZABLE_PLAN_MALLA_NIVEL"
    )
].copy()

pendientes = resultado[
    ~resultado["ESTADO_TRAZABILIDAD_FINAL"].eq(
        "TRAZABLE_PLAN_MALLA_NIVEL"
    )
].copy()

if len(trazables) != 1727:
    raise RuntimeError(
        f"Trazables inesperados: {len(trazables)}; "
        "esperados: 1727."
    )

if len(pendientes) != 644:
    raise RuntimeError(
        f"Pendientes inesperados: {len(pendientes)}; "
        "esperados: 644."
    )

resumen_estados = (
    resultado["ESTADO_NIVEL_FINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_NIVEL")
    .reset_index(name="CASOS")
)

resumen_trazabilidad = (
    resultado["ESTADO_TRAZABILIDAD_FINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_TRAZABILIDAD")
    .reset_index(name="CASOS")
)

resumen_metodo = (
    resultado.groupby(
        [
            "ESTADO_NIVEL_FINAL",
            "METODO_RESOLUCION_NIVEL",
            "FUENTE_NIVEL_FINAL",
            "TIPO_RESPALDO_NIVEL",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="CASOS")
)

cobertura = round(
    len(trazables) / len(resultado) * 100,
    2,
)


# ============================================================
# 8. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_CONSERVADO",
        "RESULTADO": "OK",
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "CASOS_INCORPORADOS",
        "RESULTADO": (
            "OK" if int(mask_42.sum()) == 42 else "ERROR"
        ),
        "DETALLE": int(mask_42.sum()),
    },
    {
        "VALIDACION": "TRAZABLES_FINALES",
        "RESULTADO": (
            "OK" if len(trazables) == 1727 else "ERROR"
        ),
        "DETALLE": len(trazables),
    },
    {
        "VALIDACION": "PENDIENTES_FINALES",
        "RESULTADO": (
            "OK" if len(pendientes) == 644 else "ERROR"
        ),
        "DETALLE": len(pendientes),
    },
    {
        "VALIDACION": "NIVELES_42_NO_NULOS",
        "RESULTADO": (
            "OK"
            if resultado.loc[
                mask_42,
                "NIVEL_FINAL",
            ].notna().all()
            else "ERROR"
        ),
        "DETALLE": int(
            resultado.loc[
                mask_42,
                "NIVEL_FINAL",
            ].isna().sum()
        ),
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
# 9. EXPORTACIÓN
# ============================================================

resultado.to_csv(
    RESULTADOS
    / "01_5809_TRAZABILIDAD_FINAL_CON_42.tsv",
    sep="\t",
    index=False,
)

trazables.to_csv(
    RESULTADOS
    / "02_5809_TRAZABLES_1727.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    AUDITORIAS
    / "01_5809_PENDIENTES_644.tsv",
    sep="\t",
    index=False,
)

resultado.loc[
    mask_42
].to_csv(
    AUDITORIAS
    / "02_DETALLE_42_INCORPORADOS.tsv",
    sep="\t",
    index=False,
)

control_previo.to_csv(
    AUDITORIAS
    / "03_CONTROL_ESTADO_PREVIO_42.tsv",
    sep="\t",
    index=False,
)

resumen_estados.to_csv(
    AUDITORIAS
    / "04_RESUMEN_ESTADOS_NIVEL.tsv",
    sep="\t",
    index=False,
)

resumen_trazabilidad.to_csv(
    AUDITORIAS
    / "05_RESUMEN_TRAZABILIDAD.tsv",
    sep="\t",
    index=False,
)

resumen_metodo.to_csv(
    AUDITORIAS
    / "06_RESUMEN_METODOS.tsv",
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
        "ROL": "MATRIZ_BASE",
        "RUTA": str(MATRIZ_BASE),
        "SHA256": sha256(MATRIZ_BASE),
        "TAMANO_BYTES": MATRIZ_BASE.stat().st_size,
    },
    {
        "ROL": "VALIDABLES_42",
        "RUTA": str(VALIDABLES_42),
        "SHA256": sha256(VALIDABLES_42),
        "TAMANO_BYTES": VALIDABLES_42.stat().st_size,
    },
])

fuentes_df.to_csv(
    AUDITORIAS
    / "08_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 10. EXCEL
# ============================================================

resumen_kpi = pd.DataFrame([
    {
        "INDICADOR": "Universo 5809",
        "VALOR": 2371,
    },
    {
        "INDICADOR": "Validados plan exacto",
        "VALOR": 1685,
    },
    {
        "INDICADOR": "Incorporados identidad+carrera+nivel",
        "VALOR": 42,
    },
    {
        "INDICADOR": "Trazables totales",
        "VALOR": 1727,
    },
    {
        "INDICADOR": "Pendientes o conflictos",
        "VALOR": 644,
    },
    {
        "INDICADOR": "Cobertura nivel",
        "VALOR": f"{cobertura}%",
    },
    {
        "INDICADOR": "Archivo definitivo de carga",
        "VALOR": "NO GENERADO",
    },
])

excel = (
    RESULTADOS
    / "TRAZABILIDAD_5809_CON_42_INCORPORADOS.xlsx"
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
        sheet_name="ESTADOS_NIVEL",
        index=False,
    )

    resumen_trazabilidad.to_excel(
        writer,
        sheet_name="TRAZABILIDAD",
        index=False,
    )

    resultado.loc[
        mask_42
    ].to_excel(
        writer,
        sheet_name="42_INCORPORADOS",
        index=False,
    )

    trazables.to_excel(
        writer,
        sheet_name="TRAZABLES_1727",
        index=False,
    )

    pendientes.to_excel(
        writer,
        sheet_name="PENDIENTES_644",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="MATRIZ_FINAL",
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
                50,
            )


# ============================================================
# 11. MANIFIESTO Y REPORTE
# ============================================================

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "universo": 2371,
    "niveles_plan_exacto": 1685,
    "niveles_incorporados_identidad_carrera": 42,
    "trazables_finales": 1727,
    "pendientes_finales": 644,
    "cobertura_nivel_pct": cobertura,
    "tipo_resolucion_42": (
        "DECISION_TECNICA_INTERNA_DOCUMENTADA"
    ),
    "es_regla_oficial": False,
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
    "INCORPORACION DE 42 NIVELES VALIDADOS",
    "=" * 90,
    "Proceso: Avance Curricular SIES 2026",
    "Subproyecto: 5809 Matrícula",
    "Año de referencia: 2025",
    "",
    "Nivel validado por plan exacto: 1685",
    "Incorporados por identidad+carrera+nivel: 42",
    "Trazables finales: 1727",
    "Pendientes finales: 644",
    f"Cobertura: {cobertura}%",
    "",
    "La incorporación de los 42 corresponde a una decisión",
    "técnica interna documentada y no a una regla oficial.",
    "",
    f"Excel: {excel}",
    f"Carpeta: {SALIDA}",
    "Fuentes modificadas: NO",
    "Archivo final de carga generado: NO",
]

(REPORTES / "RESUMEN_EJECUCION.txt").write_text(
    "\n".join(lineas),
    encoding="utf-8",
)


# ============================================================
# 12. TERMINAL
# ============================================================

print()
print("=" * 96)
print("INCORPORACIÓN DE LOS 42 NIVELES VALIDADOS")
print("=" * 96)
print("Universo 5809: 2371")
print("Validados previamente por plan exacto: 1685")
print("Incorporados por identidad+carrera+nivel: 42")
print()
print(f"TRAZABLES FINALES: {len(trazables)}")
print(f"PENDIENTES O CONFLICTOS: {len(pendientes)}")
print(f"COBERTURA FINAL DE NIVEL: {cobertura}%")
print()
print(
    "Tipo de respaldo de los 42: "
    "DECISION_TECNICA_INTERNA_DOCUMENTADA"
)
print("Regla oficial del instructivo: NO")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Fuentes modificadas: NO")
print("Precargas modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 96)
