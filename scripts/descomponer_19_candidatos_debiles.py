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

FUENTE = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "DIAGNOSTICO_27_CODCLI_PLAN_20260703_123419"
    / "02_RESULTADOS"
    / "DIAGNOSTICO_27_PENDIENTES_CODCLI_PLAN.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"DESCOMPOSICION_19_CANDIDATOS_DEBILES_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"

RESULTADOS.mkdir(parents=True, exist_ok=False)
AUDITORIAS.mkdir(parents=True, exist_ok=True)


def norm(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(r"\s+", "", texto)


def separar(valor):
    return sorted({
        norm(elemento)
        for elemento in re.split(
            r"\s*\|\s*",
            str(valor or ""),
        )
        if norm(elemento)
    })


if not FUENTE.exists():
    raise RuntimeError(
        f"No existe la fuente: {FUENTE}"
    )


libro = pd.ExcelFile(
    FUENTE,
    engine="openpyxl",
)

for hoja in [
    "CANDIDATOS_DEBILES",
    "DETALLE_HISTORICO",
]:
    if hoja not in libro.sheet_names:
        raise RuntimeError(
            f"Falta la hoja requerida: {hoja}"
        )


candidatos = pd.read_excel(
    FUENTE,
    sheet_name="CANDIDATOS_DEBILES",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

detalle = pd.read_excel(
    FUENTE,
    sheet_name="DETALLE_HISTORICO",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if len(candidatos) != 19:
    raise RuntimeError(
        f"Se esperaban 19 candidatos débiles y se encontraron "
        f"{len(candidatos)}."
    )


MODELOS = {
    "IECIREOL": {
        "familias": {"IECIREOL"},
        "carreras": {"IECIREOL", "IINF"},
        "planes": {"IECIREOL"},
        "tipo": "ANTIGUA_EXTENDIDA_20_PERIODOS_4_ANIOS",
        "regla": (
            "1-5→Año 1; 6-10→Año 2; "
            "11-15→Año 3; 16-20→Año 4"
        ),
    },
    "TCIB20241": {
        "familias": {"TCIB"},
        "carreras": {"TCIB", "ICIB"},
        "planes": {"TCIB20241"},
        "tipo": "INTENSIVA_7_PERIODOS_3_ANIOS",
        "regla": (
            "1-3→Año 1; 4-6→Año 2; 7→Año 3"
        ),
    },
}


filas = []

for _, candidato in candidatos.iterrows():
    id_fila = candidato["ID_FILA_5809"]

    historico = detalle[
        detalle["ID_FILA_5809"].eq(id_fila)
    ].copy()

    if historico.empty:
        filas.append({
            "ID_FILA_5809": id_fila,
            "ESTADO_DESCOMPOSICION":
            "SIN_DETALLE_HISTORICO",
            "MODELO_EVALUADO": "",
            "COINCIDE_FAMILIA_CODCLI": "NO",
            "COINCIDE_CARRERA": "NO",
            "COINCIDE_PLAN": "NO",
            "COINCIDE_NIVEL_RANGO": "NO_EVALUABLE",
            "RESPALDO_REAL": "NINGUNO",
            "PUEDE_CONVERTIR": "NO",
            "FUNDAMENTO":
            "No existe detalle histórico para evaluar el caso.",
        })
        continue

    for _, registro in historico.iterrows():
        familia = norm(
            registro.get(
                "FAMILIA_CODCLI",
                "",
            )
        )

        carrera = norm(
            registro.get(
                "CODCARPR_DATOS",
                "",
            )
        )

        plan = norm(
            registro.get(
                "PLAN_DATOS",
                "",
            )
        )

        nivel = pd.to_numeric(
            pd.Series([
                registro.get(
                    "NIVEL_DATOS",
                    "",
                )
            ]),
            errors="coerce",
        ).iloc[0]

        for nombre_modelo, modelo in MODELOS.items():
            coincide_familia = (
                familia in modelo["familias"]
            )

            coincide_carrera = (
                carrera in modelo["carreras"]
            )

            coincide_plan = (
                plan in modelo["planes"]
            )

            if nombre_modelo == "IECIREOL":
                coincide_nivel = (
                    not pd.isna(nivel)
                    and 1 <= float(nivel) <= 20
                )

            elif nombre_modelo == "TCIB20241":
                coincide_nivel = (
                    not pd.isna(nivel)
                    and 1 <= float(nivel) <= 7
                )

            else:
                coincide_nivel = False

            variables_coincidentes = []

            if coincide_familia:
                variables_coincidentes.append(
                    "FAMILIA_CODCLI"
                )

            if coincide_carrera:
                variables_coincidentes.append(
                    "CARRERA"
                )

            if coincide_plan:
                variables_coincidentes.append(
                    "PLAN"
                )

            if coincide_nivel:
                variables_coincidentes.append(
                    "NIVEL_EN_RANGO"
                )

            if coincide_plan and coincide_familia:
                respaldo = "PLAN_Y_FAMILIA"

            elif coincide_familia and coincide_carrera:
                respaldo = "FAMILIA_Y_CARRERA"

            elif coincide_plan and coincide_carrera:
                respaldo = "PLAN_Y_CARRERA"

            elif coincide_familia:
                respaldo = "SOLO_FAMILIA"

            elif coincide_plan:
                respaldo = "SOLO_PLAN"

            elif coincide_carrera:
                respaldo = "SOLO_CARRERA"

            elif coincide_nivel:
                respaldo = "SOLO_NIVEL_EN_RANGO"

            else:
                respaldo = "NINGUNO"

            puede_convertir = "NO"

            if coincide_plan and coincide_familia:
                estado = (
                    "REQUIERE_CONFIRMAR_PERIODIZACION_DEL_PLAN"
                )

                fundamento = (
                    "Existe coincidencia simultánea de plan y "
                    "familia del CODCLI, pero falta una fuente "
                    "institucional que confirme que este estudiante "
                    "utiliza la misma periodización del caso modelo."
                )

            elif respaldo in {
                "FAMILIA_Y_CARRERA",
                "PLAN_Y_CARRERA",
            }:
                estado = (
                    "COINCIDENCIA_PARCIAL_RELEVANTE"
                )

                fundamento = (
                    "Existen dos variables coincidentes, pero no "
                    "la combinación plan y familia del CODCLI."
                )

            elif respaldo in {
                "SOLO_FAMILIA",
                "SOLO_PLAN",
                "SOLO_CARRERA",
            }:
                estado = (
                    "COINCIDENCIA_UNICA_INSUFICIENTE"
                )

                fundamento = (
                    "Solo una variable relaciona el estudiante con "
                    "el modelo. No demuestra su periodización."
                )

            elif respaldo == "SOLO_NIVEL_EN_RANGO":
                estado = (
                    "NIVEL_COMPATIBLE_SIN_IDENTIFICACION"
                )

                fundamento = (
                    "El nivel cabe dentro del rango del modelo, "
                    "pero no coincide el CODCLI, plan ni carrera."
                )

            else:
                estado = "SIN_COINCIDENCIA"
                fundamento = (
                    "El registro histórico no coincide con el modelo."
                )

            filas.append({
                "ID_FILA_5809": id_fila,
                "RUT_5809_CONTROL":
                candidato.get(
                    "RUT_5809_CONTROL",
                    "",
                ),
                "RUT_EVIDENCIA_CRUCE":
                candidato.get(
                    "RUT_EVIDENCIA_CRUCE",
                    "",
                ),
                "CODCLI_DATOS":
                registro.get(
                    "CODCLI_DATOS",
                    "",
                ),
                "FAMILIA_CODCLI":
                familia,
                "CODCARPR_DATOS":
                carrera,
                "PLAN_DATOS":
                plan,
                "NIVEL_DATOS":
                registro.get(
                    "NIVEL_DATOS",
                    "",
                ),
                "MODELO_EVALUADO":
                nombre_modelo,
                "TIPO_PERIODIZACION_MODELO":
                modelo["tipo"],
                "REGLA_MODELO":
                modelo["regla"],
                "COINCIDE_FAMILIA_CODCLI":
                "SI" if coincide_familia else "NO",
                "COINCIDE_CARRERA":
                "SI" if coincide_carrera else "NO",
                "COINCIDE_PLAN":
                "SI" if coincide_plan else "NO",
                "COINCIDE_NIVEL_RANGO":
                "SI" if coincide_nivel else "NO",
                "VARIABLES_COINCIDENTES":
                " | ".join(variables_coincidentes),
                "RESPALDO_REAL":
                respaldo,
                "ESTADO_DESCOMPOSICION":
                estado,
                "PUEDE_CONVERTIR":
                puede_convertir,
                "FUNDAMENTO":
                fundamento,
            })


resultado = pd.DataFrame(filas)


# Seleccionar el mejor respaldo observado por estudiante.
prioridad = {
    "PLAN_Y_FAMILIA": 1,
    "FAMILIA_Y_CARRERA": 2,
    "PLAN_Y_CARRERA": 3,
    "SOLO_FAMILIA": 4,
    "SOLO_PLAN": 5,
    "SOLO_CARRERA": 6,
    "SOLO_NIVEL_EN_RANGO": 7,
    "NINGUNO": 8,
}

resultado["PRIORIDAD_RESPALDO"] = (
    resultado["RESPALDO_REAL"]
    .map(prioridad)
    .fillna(99)
    .astype(int)
)

mejor_respaldo = (
    resultado.sort_values(
        [
            "ID_FILA_5809",
            "PRIORIDAD_RESPALDO",
            "MODELO_EVALUADO",
        ]
    )
    .groupby(
        "ID_FILA_5809",
        as_index=False,
    )
    .first()
)

if len(mejor_respaldo) != 19:
    raise RuntimeError(
        "El resumen no conserva los 19 estudiantes."
    )


def clasificar_final(fila):
    respaldo = fila["RESPALDO_REAL"]

    if respaldo == "PLAN_Y_FAMILIA":
        return (
            "PENDIENTE_FUERTE_REQUIERE_REPORTE_O_REGLA_DE_PLAN"
        )

    if respaldo in {
        "FAMILIA_Y_CARRERA",
        "PLAN_Y_CARRERA",
    }:
        return (
            "PENDIENTE_INTERMEDIO_REQUIERE_VALIDACION_INSTITUCIONAL"
        )

    if respaldo in {
        "SOLO_FAMILIA",
        "SOLO_PLAN",
        "SOLO_CARRERA",
    }:
        return (
            "PENDIENTE_DEBIL_NO_CONVERTIR"
        )

    return "SIN_MODELO_DEMOSTRADO"


mejor_respaldo["ESTADO_FINAL_19"] = (
    mejor_respaldo.apply(
        clasificar_final,
        axis=1,
    )
)

mejor_respaldo["DECISION_ACTUAL"] = (
    "MANTENER_PENDIENTE"
)

mejor_respaldo[
    "FUENTE_NECESARIA_PARA_RESOLVER"
] = ""

mejor_respaldo.loc[
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ].eq(
        "PENDIENTE_FUERTE_REQUIERE_REPORTE_O_REGLA_DE_PLAN"
    ),
    "FUENTE_NECESARIA_PARA_RESOLVER",
] = (
    "Avance de Malla individual o tabla institucional "
    "de periodización del plan."
)

mejor_respaldo.loc[
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ].eq(
        "PENDIENTE_INTERMEDIO_REQUIERE_VALIDACION_INSTITUCIONAL"
    ),
    "FUENTE_NECESARIA_PARA_RESOLVER",
] = (
    "Confirmación del plan histórico y de su modalidad "
    "de periodización."
)

mejor_respaldo.loc[
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ].isin([
        "PENDIENTE_DEBIL_NO_CONVERTIR",
        "SIN_MODELO_DEMOSTRADO",
    ]),
    "FUENTE_NECESARIA_PARA_RESOLVER",
] = (
    "Avance de Malla individual del estudiante."
)


resumen = (
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

resumen_respaldo = (
    mejor_respaldo[
        "RESPALDO_REAL"
    ]
    .value_counts(dropna=False)
    .rename_axis("RESPALDO")
    .reset_index(name="CASOS")
)


resultado.to_csv(
    RESULTADOS
    / "01_EVALUACION_COMPLETA_19_X_MODELO.tsv",
    sep="\t",
    index=False,
)

mejor_respaldo.to_csv(
    RESULTADOS
    / "02_MEJOR_RESPALDO_19.tsv",
    sep="\t",
    index=False,
)

mejor_respaldo[
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ].eq(
        "PENDIENTE_FUERTE_REQUIERE_REPORTE_O_REGLA_DE_PLAN"
    )
].to_csv(
    RESULTADOS
    / "03_PENDIENTES_FUERTES.tsv",
    sep="\t",
    index=False,
)

mejor_respaldo[
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ].eq(
        "PENDIENTE_INTERMEDIO_REQUIERE_VALIDACION_INSTITUCIONAL"
    )
].to_csv(
    RESULTADOS
    / "04_PENDIENTES_INTERMEDIOS.tsv",
    sep="\t",
    index=False,
)

mejor_respaldo[
    mejor_respaldo[
        "ESTADO_FINAL_19"
    ].isin([
        "PENDIENTE_DEBIL_NO_CONVERTIR",
        "SIN_MODELO_DEMOSTRADO",
    ])
].to_csv(
    RESULTADOS
    / "05_PENDIENTES_DEBILES_O_SIN_MODELO.tsv",
    sep="\t",
    index=False,
)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_19",
        "RESULTADO": (
            "OK"
            if len(mejor_respaldo) == 19
            else "ERROR"
        ),
        "DETALLE": len(mejor_respaldo),
    },
    {
        "VALIDACION": "CONVERSION_AUTOMATICA",
        "RESULTADO": "OK",
        "DETALLE": "NO",
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
])

validaciones.to_csv(
    AUDITORIAS / "01_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


excel = (
    RESULTADOS
    / "DESCOMPOSICION_19_CANDIDATOS_DEBILES.xlsx"
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

    resumen_respaldo.to_excel(
        writer,
        sheet_name="TIPOS_RESPALDO",
        index=False,
    )

    mejor_respaldo.to_excel(
        writer,
        sheet_name="MEJOR_RESPALDO_19",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="EVALUACION_COMPLETA",
        index=False,
    )

    mejor_respaldo[
        mejor_respaldo[
            "ESTADO_FINAL_19"
        ].eq(
            "PENDIENTE_FUERTE_REQUIERE_REPORTE_O_REGLA_DE_PLAN"
        )
    ].to_excel(
        writer,
        sheet_name="PENDIENTES_FUERTES",
        index=False,
    )

    mejor_respaldo[
        mejor_respaldo[
            "ESTADO_FINAL_19"
        ].eq(
            "PENDIENTE_INTERMEDIO_REQUIERE_VALIDACION_INSTITUCIONAL"
        )
    ].to_excel(
        writer,
        sheet_name="PENDIENTES_INTERMEDIOS",
        index=False,
    )

    mejor_respaldo[
        mejor_respaldo[
            "ESTADO_FINAL_19"
        ].isin([
            "PENDIENTE_DEBIL_NO_CONVERTIR",
            "SIN_MODELO_DEMOSTRADO",
        ])
    ].to_excel(
        writer,
        sheet_name="DEBILES_SIN_MODELO",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
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


manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia": 2025,
    "universo": 19,
    "objetivo": (
        "Descomponer la evidencia de asociación con los "
        "dos modelos de periodización."
    ),
    "conversion_automatica": False,
    "niveles_modificados": 0,
    "fuentes_modificadas": False,
    "archivo_carga_generado": False,
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
print("DESCOMPOSICIÓN DE LOS 19 CANDIDATOS DÉBILES")
print("=" * 108)

for _, fila in resumen.iterrows():
    print(
        f"{fila['ESTADO']}: "
        f"{fila['CASOS']}"
    )

print()
print("TIPOS DE RESPALDO")
print("-" * 108)

for _, fila in resumen_respaldo.iterrows():
    print(
        f"{fila['RESPALDO']}: "
        f"{fila['CASOS']}"
    )

print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Conversión automática: NO")
print("Niveles modificados: 0")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 108)
