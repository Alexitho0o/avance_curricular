#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


# ============================================================
# CONTEXTO
# ============================================================

RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

PLANILLA_29 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "PLANILLA_DECISION_29_P1_20260703_095214"
    / "02_RESULTADOS"
    / "01_PLANILLA_OPERATIVA_DECISION_29_P1.tsv"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"ANALISIS_DESCARTE_1_A_1_29_P1_{timestamp}"
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


def norm_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )

    return re.sub(
        r"[^A-Z0-9]+",
        "",
        texto,
    )


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


def numero(valor):
    return pd.to_numeric(
        pd.Series([valor]),
        errors="coerce",
    ).iloc[0]


def lista_codigos(valor):
    if pd.isna(valor):
        return []

    partes = re.split(
        r"\s*\|\s*|\s*;\s*|,\s*",
        str(valor),
    )

    return sorted({
        norm_codigo(parte)
        for parte in partes
        if norm_codigo(parte)
    })


def lista_niveles(valor):
    if pd.isna(valor):
        return []

    partes = re.split(
        r"\s*\|\s*|\s*;\s*|,\s*",
        str(valor),
    )

    niveles = []

    for parte in partes:
        valor_num = pd.to_numeric(
            pd.Series([parte]),
            errors="coerce",
        ).iloc[0]

        if pd.notna(valor_num):
            niveles.append(int(valor_num))

    return sorted(set(niveles))


def disponible(valor):
    return norm_texto(valor) != ""


def evaluar_caso(fila, excluir=None):
    excluir = set(excluir or [])

    evidencia = {}
    observaciones = []

    documento = norm_documento(
        fila.get("DOCUMENTO", "")
    )

    rut_evidencia = lista_codigos(
        fila.get("RUT_EVIDENCIA_IDENTIDAD", "")
    )

    nombres = norm_texto(
        fila.get("NOMBRES", "")
    )

    paterno = norm_texto(
        fila.get("PRIMER_APELLIDO", "")
    )

    materno = norm_texto(
        fila.get("SEGUNDO_APELLIDO", "")
    )

    plan_vigente = norm_codigo(
        fila.get("CODPESTUD_VIGENTE", "")
    )

    carrera_plan = norm_codigo(
        fila.get("CODCARR_PLAN_VIGENTE", "")
    )

    carrera_evidencia = norm_codigo(
        fila.get("CODCARPR_EVIDENCIA", "")
    )

    nivel_evidencia = numero(
        fila.get("NIVEL_EVIDENCIA", "")
    )

    nivel_max_plan = numero(
        fila.get("NIVEL_MAX_PLAN", "")
    )

    planes_historicos = lista_codigos(
        fila.get("PLANES_HISTORICOS", "")
    )

    carreras_historicas = lista_codigos(
        fila.get("CARRERAS_EVIDENCIA_IDENTIDAD", "")
    )

    niveles_historicos = lista_niveles(
        fila.get("NIVELES_EVIDENCIA_IDENTIDAD", "")
    )

    categoria_origen = norm_codigo(
        fila.get("CATEGORIA_REVISION", "")
    )

    # --------------------------------------------------------
    # 1. Identidad
    # --------------------------------------------------------

    if "DOCUMENTO" not in excluir:
        if documento and rut_evidencia:
            coincide_documento = (
                documento in {
                    norm_documento(valor)
                    for valor in rut_evidencia
                }
            )

            evidencia["DOCUMENTO"] = (
                "COINCIDE"
                if coincide_documento
                else "CONFLICTO"
            )
        elif documento:
            evidencia["DOCUMENTO"] = "SIN_COMPARADOR"
        else:
            evidencia["DOCUMENTO"] = "VACIO"

    if "NOMBRES" not in excluir:
        evidencia["NOMBRES"] = (
            "DISPONIBLE"
            if nombres
            else "VACIO"
        )

    if "PRIMER_APELLIDO" not in excluir:
        evidencia["PRIMER_APELLIDO"] = (
            "DISPONIBLE"
            if paterno
            else "VACIO"
        )

    if "SEGUNDO_APELLIDO" not in excluir:
        evidencia["SEGUNDO_APELLIDO"] = (
            "DISPONIBLE"
            if materno
            else "VACIO"
        )

    # --------------------------------------------------------
    # 2. Plan y carrera
    # --------------------------------------------------------

    if "CODPESTUD_VIGENTE" not in excluir:
        evidencia["CODPESTUD_VIGENTE"] = (
            "DISPONIBLE"
            if plan_vigente
            else "VACIO"
        )

    if "CODCARR_PLAN_VIGENTE" not in excluir:
        evidencia["CODCARR_PLAN_VIGENTE"] = (
            "DISPONIBLE"
            if carrera_plan
            else "VACIO"
        )

    if "CODCARPR_EVIDENCIA" not in excluir:
        if carrera_plan and carrera_evidencia:
            evidencia["CODCARPR_EVIDENCIA"] = (
                "COINCIDE"
                if carrera_plan == carrera_evidencia
                else "CONFLICTO"
            )
        elif carrera_evidencia:
            evidencia["CODCARPR_EVIDENCIA"] = (
                "SIN_COMPARADOR"
            )
        else:
            evidencia["CODCARPR_EVIDENCIA"] = "VACIO"

    # --------------------------------------------------------
    # 3. Nivel
    # --------------------------------------------------------

    if "NIVEL_EVIDENCIA" not in excluir:
        if pd.notna(nivel_evidencia):
            if (
                pd.notna(nivel_max_plan)
                and nivel_evidencia >= 1
                and nivel_evidencia <= nivel_max_plan
            ):
                evidencia["NIVEL_EVIDENCIA"] = (
                    "DENTRO_RANGO"
                )
            elif pd.notna(nivel_max_plan):
                evidencia["NIVEL_EVIDENCIA"] = (
                    "FUERA_RANGO"
                )
            else:
                evidencia["NIVEL_EVIDENCIA"] = (
                    "SIN_MAXIMO_PLAN"
                )
        else:
            evidencia["NIVEL_EVIDENCIA"] = "VACIO"

    if "NIVEL_MAX_PLAN" not in excluir:
        evidencia["NIVEL_MAX_PLAN"] = (
            "DISPONIBLE"
            if pd.notna(nivel_max_plan)
            else "VACIO"
        )

    # --------------------------------------------------------
    # 4. Historia
    # --------------------------------------------------------

    if "PLANES_HISTORICOS" not in excluir:
        if not planes_historicos:
            evidencia["PLANES_HISTORICOS"] = "VACIO"

        elif plan_vigente in planes_historicos:
            evidencia["PLANES_HISTORICOS"] = (
                "INCLUYE_PLAN_VIGENTE"
            )

        elif len(planes_historicos) == 1:
            evidencia["PLANES_HISTORICOS"] = (
                "UN_PLAN_DISTINTO"
            )

        else:
            evidencia["PLANES_HISTORICOS"] = (
                "MULTIPLES_PLANES"
            )

    if "CARRERAS_HISTORICAS" not in excluir:
        if not carreras_historicas:
            evidencia["CARRERAS_HISTORICAS"] = "VACIO"

        elif carrera_plan in carreras_historicas:
            evidencia["CARRERAS_HISTORICAS"] = (
                "INCLUYE_CARRERA_VIGENTE"
            )

        elif len(carreras_historicas) == 1:
            evidencia["CARRERAS_HISTORICAS"] = (
                "UNA_CARRERA_DISTINTA"
            )

        else:
            evidencia["CARRERAS_HISTORICAS"] = (
                "MULTIPLES_CARRERAS"
            )

    if "NIVELES_HISTORICOS" not in excluir:
        if not niveles_historicos:
            evidencia["NIVELES_HISTORICOS"] = "VACIO"

        elif len(niveles_historicos) == 1:
            evidencia["NIVELES_HISTORICOS"] = (
                "UN_NIVEL"
            )

        else:
            evidencia["NIVELES_HISTORICOS"] = (
                "MULTIPLES_NIVELES"
            )

    # --------------------------------------------------------
    # 5. Reglas conservadoras de decisión técnica
    # --------------------------------------------------------

    conflicto_documento = (
        evidencia.get("DOCUMENTO") == "CONFLICTO"
    )

    conflicto_carrera = (
        evidencia.get("CODCARPR_EVIDENCIA")
        == "CONFLICTO"
    )

    nivel_fuera_rango = (
        evidencia.get("NIVEL_EVIDENCIA")
        == "FUERA_RANGO"
    )

    multiples_planes = (
        evidencia.get("PLANES_HISTORICOS")
        == "MULTIPLES_PLANES"
    )

    multiples_carreras = (
        evidencia.get("CARRERAS_HISTORICAS")
        == "MULTIPLES_CARRERAS"
    )

    multiples_niveles = (
        evidencia.get("NIVELES_HISTORICOS")
        == "MULTIPLES_NIVELES"
    )

    carrera_coincide = (
        evidencia.get("CODCARPR_EVIDENCIA")
        == "COINCIDE"
    )

    nivel_en_rango = (
        evidencia.get("NIVEL_EVIDENCIA")
        == "DENTRO_RANGO"
    )

    identidad_minima = all([
        nombres,
        paterno,
    ])

    plan_disponible = bool(plan_vigente)
    carrera_plan_disponible = bool(carrera_plan)

    if conflicto_documento:
        decision = "RECHAZAR_EVIDENCIA_IDENTIDAD"
        observaciones.append(
            "El documento de la evidencia no coincide."
        )

    elif nivel_fuera_rango:
        decision = "RECHAZAR_NIVEL_FUERA_DE_RANGO"
        observaciones.append(
            "El nivel observado excede o no pertenece "
            "al rango físico del plan."
        )

    elif conflicto_carrera:
        decision = "RECHAZAR_NIVEL_CARRERA_DISTINTA"
        observaciones.append(
            "La carrera de la evidencia no coincide "
            "con la carrera del plan vigente."
        )

    elif (
        multiples_planes
        or multiples_carreras
        or multiples_niveles
    ):
        decision = "MANTENER_PENDIENTE_AMBIGUEDAD"
        observaciones.append(
            "Existen múltiples trayectorias posibles."
        )

    elif all([
        identidad_minima,
        plan_disponible,
        carrera_plan_disponible,
        carrera_coincide,
        nivel_en_rango,
    ]):
        decision = "CANDIDATO_APROBACION_TECNICA"
        observaciones.append(
            "Identidad disponible, carrera coincidente "
            "y nivel dentro del rango del plan."
        )

    else:
        decision = "MANTENER_PENDIENTE_EVIDENCIA_INSUFICIENTE"
        observaciones.append(
            "No se cumplen todos los criterios conservadores."
        )

    estados = " | ".join(
        f"{clave}={valor}"
        for clave, valor in evidencia.items()
    )

    return {
        "DECISION_RESULTANTE": decision,
        "EVIDENCIA_RESULTANTE": estados,
        "OBSERVACION_RESULTANTE": " ".join(
            observaciones
        ),
        "NIVEL_CANDIDATO_RESULTANTE": (
            int(nivel_evidencia)
            if (
                decision
                == "CANDIDATO_APROBACION_TECNICA"
                and pd.notna(nivel_evidencia)
            )
            else pd.NA
        ),
        "CATEGORIA_ORIGEN": categoria_origen,
    }


# ============================================================
# 1. LEER FUENTE
# ============================================================

if not PLANILLA_29.exists():
    raise RuntimeError(
        f"No existe la planilla de 29 casos: {PLANILLA_29}"
    )

base = pd.read_csv(
    PLANILLA_29,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(base) != 29:
    raise RuntimeError(
        f"Se esperaban 29 casos y se encontraron "
        f"{len(base)}."
    )

if base["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Existen ID_FILA_5809 duplicados."
    )


# ============================================================
# 2. VARIABLES EVALUADAS
# ============================================================

variables = [
    "DOCUMENTO",
    "NOMBRES",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "CODPESTUD_VIGENTE",
    "CODCARR_PLAN_VIGENTE",
    "CODCARPR_EVIDENCIA",
    "NIVEL_EVIDENCIA",
    "NIVEL_MAX_PLAN",
    "PLANES_HISTORICOS",
    "CARRERAS_HISTORICAS",
    "NIVELES_HISTORICOS",
]


# ============================================================
# 3. DECISIÓN CON TODAS LAS VARIABLES
# ============================================================

evaluacion_completa = base.apply(
    lambda fila: pd.Series(
        evaluar_caso(
            fila,
            excluir=[],
        )
    ),
    axis=1,
)

resultado = pd.concat(
    [
        base.reset_index(drop=True),
        evaluacion_completa.add_prefix(
            "BASE_"
        ).reset_index(drop=True),
    ],
    axis=1,
)


# ============================================================
# 4. DESCARTE 1 A 1
# ============================================================

filas_ablation = []

for indice, fila in base.iterrows():
    evaluacion_base = evaluar_caso(
        fila,
        excluir=[],
    )

    for variable in variables:
        evaluacion_sin = evaluar_caso(
            fila,
            excluir=[variable],
        )

        cambio = (
            evaluacion_base[
                "DECISION_RESULTANTE"
            ]
            != evaluacion_sin[
                "DECISION_RESULTANTE"
            ]
        )

        filas_ablation.append({
            "ID_FILA_5809":
            fila["ID_FILA_5809"],

            "N_ORDEN_REVISION":
            fila.get(
                "N_ORDEN_REVISION",
                "",
            ),

            "CATEGORIA_REVISION":
            fila.get(
                "CATEGORIA_REVISION",
                "",
            ),

            "VARIABLE_EXCLUIDA":
            variable,

            "DECISION_CON_TODAS":
            evaluacion_base[
                "DECISION_RESULTANTE"
            ],

            "DECISION_SIN_VARIABLE":
            evaluacion_sin[
                "DECISION_RESULTANTE"
            ],

            "CAMBIA_DECISION":
            "SI" if cambio else "NO",

            "EVIDENCIA_CON_TODAS":
            evaluacion_base[
                "EVIDENCIA_RESULTANTE"
            ],

            "EVIDENCIA_SIN_VARIABLE":
            evaluacion_sin[
                "EVIDENCIA_RESULTANTE"
            ],
        })

ablation = pd.DataFrame(filas_ablation)


# ============================================================
# 5. IMPORTANCIA DE CADA VARIABLE
# ============================================================

impacto_variables = (
    ablation.groupby(
        "VARIABLE_EXCLUIDA",
        dropna=False,
    )
    .agg(
        CASOS_EVALUADOS=(
            "ID_FILA_5809",
            "nunique",
        ),
        CASOS_CAMBIA_DECISION=(
            "CAMBIA_DECISION",
            lambda serie: int(
                serie.eq("SI").sum()
            ),
        ),
    )
    .reset_index()
)

impacto_variables[
    "PORCENTAJE_IMPACTO"
] = (
    impacto_variables[
        "CASOS_CAMBIA_DECISION"
    ]
    / impacto_variables[
        "CASOS_EVALUADOS"
    ]
    * 100
).round(2)

impacto_variables = impacto_variables.sort_values(
    [
        "CASOS_CAMBIA_DECISION",
        "VARIABLE_EXCLUIDA",
    ],
    ascending=[
        False,
        True,
    ],
)


# ============================================================
# 6. VARIABLES DECISIVAS POR CASO
# ============================================================

variables_decisivas = (
    ablation[
        ablation["CAMBIA_DECISION"].eq("SI")
    ]
    .groupby(
        "ID_FILA_5809",
        dropna=False,
    )
    .agg(
        VARIABLES_QUE_CAMBIAN_DECISION=(
            "VARIABLE_EXCLUIDA",
            lambda serie: " | ".join(
                sorted(set(serie))
            ),
        ),
        N_VARIABLES_DECISIVAS=(
            "VARIABLE_EXCLUIDA",
            "nunique",
        ),
    )
    .reset_index()
)

resultado = resultado.merge(
    variables_decisivas,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

resultado[
    "VARIABLES_QUE_CAMBIAN_DECISION"
] = resultado[
    "VARIABLES_QUE_CAMBIAN_DECISION"
].fillna("NINGUNA")

resultado[
    "N_VARIABLES_DECISIVAS"
] = pd.to_numeric(
    resultado[
        "N_VARIABLES_DECISIVAS"
    ],
    errors="coerce",
).fillna(0).astype(int)


# ============================================================
# 7. CLASIFICACIÓN FINAL DE CONFIANZA
# ============================================================

resultado["NIVEL_CONFIANZA_TECNICA"] = ""
resultado["RECOMENDACION_REVISION"] = ""

decision_base = resultado[
    "BASE_DECISION_RESULTANTE"
]

n_decisivas = resultado[
    "N_VARIABLES_DECISIVAS"
]


mask_aprobacion = decision_base.eq(
    "CANDIDATO_APROBACION_TECNICA"
)

resultado.loc[
    mask_aprobacion & n_decisivas.le(2),
    "NIVEL_CONFIANZA_TECNICA",
] = "ALTA"

resultado.loc[
    mask_aprobacion & n_decisivas.gt(2),
    "NIVEL_CONFIANZA_TECNICA",
] = "MEDIA"

resultado.loc[
    mask_aprobacion,
    "RECOMENDACION_REVISION",
] = (
    "Revisar las variables decisivas y aprobar únicamente "
    "si la evidencia institucional las confirma."
)


mask_rechazo = decision_base.isin([
    "RECHAZAR_EVIDENCIA_IDENTIDAD",
    "RECHAZAR_NIVEL_FUERA_DE_RANGO",
    "RECHAZAR_NIVEL_CARRERA_DISTINTA",
])

resultado.loc[
    mask_rechazo,
    "NIVEL_CONFIANZA_TECNICA",
] = "ALTA"

resultado.loc[
    mask_rechazo,
    "RECOMENDACION_REVISION",
] = (
    "No utilizar el nivel observado mientras el conflicto "
    "no sea corregido por una fuente institucional."
)


mask_ambiguo = decision_base.eq(
    "MANTENER_PENDIENTE_AMBIGUEDAD"
)

resultado.loc[
    mask_ambiguo,
    "NIVEL_CONFIANZA_TECNICA",
] = "BAJA"

resultado.loc[
    mask_ambiguo,
    "RECOMENDACION_REVISION",
] = (
    "Revisión individual obligatoria. No seleccionar el "
    "máximo nivel ni una trayectoria por defecto."
)


mask_insuficiente = decision_base.eq(
    "MANTENER_PENDIENTE_EVIDENCIA_INSUFICIENTE"
)

resultado.loc[
    mask_insuficiente,
    "NIVEL_CONFIANZA_TECNICA",
] = "BAJA"

resultado.loc[
    mask_insuficiente,
    "RECOMENDACION_REVISION",
] = (
    "Solicitar evidencia adicional antes de tomar decisión."
)


# ============================================================
# 8. RESÚMENES
# ============================================================

resumen_decisiones = (
    resultado[
        "BASE_DECISION_RESULTANTE"
    ]
    .value_counts(dropna=False)
    .rename_axis("DECISION_TECNICA")
    .reset_index(name="CASOS")
)

resumen_confianza = (
    resultado[
        "NIVEL_CONFIANZA_TECNICA"
    ]
    .value_counts(dropna=False)
    .rename_axis("CONFIANZA")
    .reset_index(name="CASOS")
)

resumen_categoria_decision = (
    resultado.groupby(
        [
            "CATEGORIA_REVISION",
            "BASE_DECISION_RESULTANTE",
            "NIVEL_CONFIANZA_TECNICA",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="CASOS")
)


# ============================================================
# 9. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_29",
        "RESULTADO": (
            "OK" if len(resultado) == 29 else "ERROR"
        ),
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "DESCARTES_ESPERADOS",
        "RESULTADO": (
            "OK"
            if len(ablation)
            == len(base) * len(variables)
            else "ERROR"
        ),
        "DETALLE": len(ablation),
    },
    {
        "VALIDACION": "VARIABLES_EVALUADAS",
        "RESULTADO": "OK",
        "DETALLE": len(variables),
    },
    {
        "VALIDACION": "DECISIONES_AUTOMATICAS_INCORPORADAS",
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
# 10. EXPORTAR
# ============================================================

resultado.to_csv(
    RESULTADOS
    / "01_RESULTADO_DESCARTE_1_A_1_29.tsv",
    sep="\t",
    index=False,
)

ablation.to_csv(
    RESULTADOS
    / "02_DETALLE_DESCARTE_VARIABLE_POR_VARIABLE.tsv",
    sep="\t",
    index=False,
)

impacto_variables.to_csv(
    AUDITORIAS
    / "01_IMPACTO_VARIABLES.tsv",
    sep="\t",
    index=False,
)

resumen_decisiones.to_csv(
    AUDITORIAS
    / "02_RESUMEN_DECISIONES.tsv",
    sep="\t",
    index=False,
)

resumen_confianza.to_csv(
    AUDITORIAS
    / "03_RESUMEN_CONFIANZA.tsv",
    sep="\t",
    index=False,
)

resumen_categoria_decision.to_csv(
    AUDITORIAS
    / "04_CATEGORIA_VS_DECISION.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "05_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)

fuentes_df = pd.DataFrame([
    {
        "ROL": "PLANILLA_OPERATIVA_29",
        "RUTA": str(PLANILLA_29),
        "SHA256": sha256(PLANILLA_29),
        "TAMANO_BYTES": PLANILLA_29.stat().st_size,
    }
])

fuentes_df.to_csv(
    AUDITORIAS
    / "06_FUENTE_Y_HASH.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 11. EXCEL
# ============================================================

excel = (
    RESULTADOS
    / "ANALISIS_DESCARTE_1_A_1_29_P1.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_decisiones.to_excel(
        writer,
        sheet_name="RESUMEN_DECISIONES",
        index=False,
    )

    resumen_confianza.to_excel(
        writer,
        sheet_name="RESUMEN_CONFIANZA",
        index=False,
    )

    impacto_variables.to_excel(
        writer,
        sheet_name="IMPACTO_VARIABLES",
        index=False,
    )

    resumen_categoria_decision.to_excel(
        writer,
        sheet_name="CATEGORIA_DECISION",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="RESULTADO_29",
        index=False,
    )

    ablation.to_excel(
        writer,
        sheet_name="DESCARTE_1_A_1",
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
# 12. MANIFIESTO
# ============================================================

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "casos_analizados": 29,
    "variables_evaluadas": variables,
    "metodo": "descarte de una variable por iteración",
    "decisiones_incorporadas": 0,
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
# 13. REPORTE
# ============================================================

lineas = [
    "ANÁLISIS DE DESCARTE 1 A 1 — 29 CASOS P1",
    "=" * 100,
    "Proceso: Avance Curricular SIES 2026",
    "Subproyecto: 5809 Matrícula",
    "Año de referencia: 2025",
    "",
    "Cada caso fue evaluado con todas las variables y luego",
    "repitiendo la evaluación al excluir una variable por vez.",
    "",
    "DECISIONES TÉCNICAS",
    "-------------------",
]

for _, fila in resumen_decisiones.iterrows():
    lineas.append(
        f"{fila['DECISION_TECNICA']}: "
        f"{fila['CASOS']}"
    )

lineas.extend([
    "",
    f"Excel: {excel}",
    f"Carpeta: {SALIDA}",
    "",
    "Las decisiones son recomendaciones técnicas.",
    "No se incorporó ningún nivel automáticamente.",
    "Fuentes modificadas: NO",
    "Archivo final de carga generado: NO",
])

(REPORTES / "RESUMEN_EJECUCION.txt").write_text(
    "\n".join(lineas),
    encoding="utf-8",
)


# ============================================================
# 14. TERMINAL
# ============================================================

print()
print("=" * 104)
print("ANÁLISIS DE DESCARTE VARIABLE POR VARIABLE — 29 CASOS P1")
print("=" * 104)
print(f"Casos analizados: {len(resultado)}")
print(f"Variables evaluadas: {len(variables)}")
print(f"Simulaciones de descarte: {len(ablation)}")
print()
print("DECISIONES CON TODAS LAS VARIABLES")
print("-" * 104)

for _, fila in resumen_decisiones.iterrows():
    print(
        f"{fila['DECISION_TECNICA']}: "
        f"{fila['CASOS']}"
    )

print()
print("VARIABLES CON MAYOR IMPACTO")
print("-" * 104)

for _, fila in impacto_variables.head(12).iterrows():
    print(
        f"{fila['VARIABLE_EXCLUIDA']}: "
        f"{fila['CASOS_CAMBIA_DECISION']} casos "
        f"({fila['PORCENTAJE_IMPACTO']}%)"
    )

print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Decisiones incorporadas automáticamente: 0")
print("Fuentes modificadas: NO")
print("Precargas modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 104)
