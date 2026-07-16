#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidado gobernado de resolucion 16-19 para los 423 pendientes auditados.

No modifica fuentes originales, no corrige datos, no genera SIES_READY, no
recalcula 20-21 y no crea archivo de carga. Solo consolida rutas de resolucion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


PROCESO = "Avance Curricular SIES 2026"
SUBPROYECTO = "Consolidado resolucion 16-19 gobernado 5809"
ANIO_PROCESO = 2026
ANIO_REFERENCIA_DATOS = 2025
DECLARACION_CARGA = "NO_LISTO_PARA_CARGA"
NO_CORRECCION = "NO_APLICAR_CORRECCION_AUTOMATICA"
ESTADO_VALIDADOR_REQUERIDO = "APTO_PARA_CONTROL_PREVIO"

REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BASE_58 = REPO / "avance_curricular_2026" / "58_consolidado_resolucion_16_19_gobernado_5809"

GOBERNANZA_51 = (
    REPO
    / "avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/"
    / "GOBERNANZA_INTEGRAL_5809_20260708_144544/"
    / "GOBERNANZA_INTEGRAL_INPUTS_COLUMNAS_TRANSFORMACIONES_5809.xlsx"
)
VALIDADOR_52_SCRIPT = (
    REPO
    / "avance_curricular_2026/52_validador_gobernanza_precalculo_5809/"
    / "VALIDADOR_GOBERNANZA_PRECALCULO_5809_20260708_165151/"
    / "validador_gobernanza_precalculo_5809.py"
)
VALIDADOR_52_XLSX = (
    REPO
    / "avance_curricular_2026/52_validador_gobernanza_precalculo_5809/"
    / "VALIDADOR_GOBERNANZA_PRECALCULO_5809_20260708_165151/"
    / "VALIDACION_GOBERNANZA_PRECALCULO_5809.xlsx"
)
MATRIZ_53 = (
    REPO
    / "avance_curricular_2026/53_matriz_resolucion_bloqueos_16_19_gobernada_5809/"
    / "MATRIZ_RESOLUCION_BLOQUEOS_16_19_GOBERNADA_20260708_170521/"
    / "MATRIZ_RESOLUCION_BLOQUEOS_16_19_GOBERNADA_5809.xlsx"
)
H54_XLSX = (
    REPO
    / "avance_curricular_2026/54_auditoria_diferencia_solo_aprobadas_19_5809/"
    / "AUDITORIA_DIF_SOLO_APROBADAS_19_20260708_171351/"
    / "AUDITORIA_DIFERENCIA_SOLO_APROBADAS_19_5809.xlsx"
)
H55_XLSX = (
    REPO
    / "avance_curricular_2026/55_auditoria_diferencia_16_18_multiple_5809/"
    / "AUDITORIA_DIF_16_18_MULTIPLE_20260708_172433/"
    / "AUDITORIA_DIFERENCIA_16_18_MULTIPLE_5809.xlsx"
)
H56_XLSX = (
    REPO
    / "avance_curricular_2026/56_auditoria_sin_registros_2025_codcli_lista_5809/"
    / "AUDITORIA_SIN_REGISTROS_2025_CODCLI_LISTA_20260708_173435/"
    / "AUDITORIA_SIN_REGISTROS_2025_CODCLI_LISTA_5809.xlsx"
)
H57_XLSX = (
    REPO
    / "avance_curricular_2026/57_auditoria_sin_codcli_lista_5809/"
    / "AUDITORIA_SIN_CODCLI_LISTA_20260708_175249/"
    / "AUDITORIA_SIN_CODCLI_LISTA_5809.xlsx"
)
H54_MANIFEST = H54_XLSX.with_name("manifest_auditoria_diferencia_solo_aprobadas_19_5809.json")
H55_MANIFEST = H55_XLSX.with_name("manifest_auditoria_diferencia_16_18_multiple_5809.json")
H56_MANIFEST = H56_XLSX.with_name("manifest_auditoria_sin_registros_2025_codcli_lista_5809.json")
H57_MANIFEST = H57_XLSX.with_name("manifest_auditoria_sin_codcli_lista_5809.json")

OUTPUT_FILES = {
    "excel": "CONSOLIDADO_RESOLUCION_16_19_GOBERNADO_5809.xlsx",
    "informe": "INFORME_CONSOLIDADO_RESOLUCION_16_19_GOBERNADO_5809.md",
    "manifest": "manifest_consolidado_resolucion_16_19_gobernado_5809.json",
    "script": "consolidado_resolucion_16_19_gobernado_5809.py",
}

ROUTES = [
    "RESOLUBLE_CON_DECISION_FUNCIONAL",
    "REQUIERE_MAPEO_INSTITUCIONAL",
    "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA",
    "REQUIERE_REVISION_FUNCIONAL",
    "NO_RESOLVER_AUTOMATICO",
    "BLOQUEADO",
]

SHEETS = OrderedDict(
    [
        ("00_DICTAMEN", "00_DICTAMEN"),
        ("01_VALIDACION_GOBERNANZA", "01_VALIDACION_GOBERNANZA"),
        ("02_RESUMEN_EJECUTIVO", "02_RESUMEN_EJECUTIVO"),
        ("03_CONSOLIDADO_423", "03_CONSOLIDADO_423"),
        ("04_RUTA_DECISION_FUNCIONAL", "04_RUTA_DECISION_FUNCIONAL"),
        ("05_RUTA_MAPEO_INSTITUCIONAL", "05_RUTA_MAPEO_INSTITUCIONAL"),
        ("06_RUTA_FUENTE_COMPLEMENTARIA", "06_RUTA_FUENTE_COMPLEMENTARIA"),
        ("07_RUTA_NO_RESOLVER_AUTOMATICO", "07_RUTA_NO_RESOLVER_AUTOMATICO"),
        ("08_PROPUESTA_PLAN_ACCION", "08_PROPUESTA_PLAN_ACCION"),
        ("09_PENDIENTES_POR_PRIORIDAD", "09_PENDIENTES_POR_PRIORIDAD"),
        ("10_FUENTES", "10_FUENTES"),
    ]
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def display(value: Any, max_len: int = 160) -> str:
    text = clean(value)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "(sin filas)"
    cols = list(df.columns)
    widths = []
    for col in cols:
        values = [str(col)] + [display(v, 100) for v in df[col].tolist()]
        widths.append(max(len(v) for v in values))
    header = "| " + " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(cols)) + " |"
    sep = "| " + " | ".join("-" * width for width in widths) + " |"
    body = []
    for _, row in df.iterrows():
        body.append(
            "| "
            + " | ".join(display(row[col], 100).ljust(widths[i]) for i, col in enumerate(cols))
            + " |"
        )
    return "\n".join([header, sep] + body)


def read_sheet(path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet, dtype=str).fillna("")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_paths() -> None:
    paths = [
        GOBERNANZA_51,
        VALIDADOR_52_SCRIPT,
        VALIDADOR_52_XLSX,
        MATRIZ_53,
        H54_XLSX,
        H55_XLSX,
        H56_XLSX,
        H57_XLSX,
        H54_MANIFEST,
        H55_MANIFEST,
        H56_MANIFEST,
        H57_MANIFEST,
    ]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan entradas obligatorias:\n" + "\n".join(missing))


def run_validator_52(output_dir: Path, timestamp: str) -> Dict[str, Any]:
    plan_path = output_dir / "plan_uso_validador_h52_consolidado_resolucion_16_19.json"
    plan = {
        "descripcion": (
            "Consolidado gobernado documental de 423 pendientes 16-19. "
            "No corrige, no recalcula 20-21, no genera carga y no crea SIES_READY."
        ),
        "columnas_usadas": [
            "CODIGO_UNICO",
            "PLAN_ESTUDIOS",
            "CODCLI_LISTA",
            "CODCLI",
            "ANO",
            "PERIODO",
            "CODRAMO",
            "ESTADO",
            "DESCRIPCION_ESTADO",
        ],
        "llaves_usadas": ["CODCLI_LISTA", "CODIGO_UNICO", "PLAN_ESTUDIOS"],
        "diccionarios_usados": ["DIC_ESTADO_PROMEDIOS"],
        "transformaciones": ["Consolidacion documental de rutas; sin correccion ni recalculo"],
        "campos_calculo": [],
        "anio_calculo": 2025,
        "genera_sies_ready": False,
        "modifica_fuentes_originales": False,
        "usa_todos_codcli_rut": False,
        "filtra_por_programa": True,
        "usa_inferencias_como_reglas_oficiales": False,
        "usa_estados_AEIR": True,
        "usa_codcli_lista": True,
        "mezcla_anual_acumulado": False,
        "modo": "CONSOLIDADO_GOBERNADO_NO_CORRECTIVO_16_19",
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    validator_timestamp = f"{timestamp}_H58"
    cmd = [
        sys.executable,
        str(VALIDADOR_52_SCRIPT),
        "--timestamp",
        validator_timestamp,
        "--plan-json",
        str(plan_path),
    ]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    validator_dir = (
        REPO
        / "avance_curricular_2026/52_validador_gobernanza_precalculo_5809"
        / f"VALIDADOR_GOBERNANZA_PRECALCULO_5809_{validator_timestamp}"
    )
    manifest_path = validator_dir / "manifest_validacion_gobernanza_precalculo_5809.json"
    manifest: Dict[str, Any] = {}
    if manifest_path.exists():
        manifest = load_json(manifest_path)
    result = {
        "plan_path": str(plan_path),
        "validator_timestamp": validator_timestamp,
        "validator_dir": str(validator_dir),
        "validator_manifest": str(manifest_path),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "estado_validador": manifest.get("estado_validador", "SIN_MANIFEST"),
        "manifest": manifest,
    }
    if completed.returncode != 0:
        raise RuntimeError(
            "Validador hito 52 fallo.\nSTDOUT:\n"
            + completed.stdout
            + "\nSTDERR:\n"
            + completed.stderr
        )
    if result["estado_validador"] != ESTADO_VALIDADOR_REQUERIDO:
        raise RuntimeError(f"Validador hito 52 no apto: {result['estado_validador']}")
    return result


def route_for_case(hito: str, cause: str, detected: str) -> str:
    cause = clean(cause)
    detected = clean(detected)
    if hito == "H54":
        if cause == "CONVALIDACION_HOMOLOGACION_YA_GOBERNADA":
            return "RESOLUBLE_CON_DECISION_FUNCIONAL"
        if cause == "ESTADO_NULL_O_BLANCO":
            return "REQUIERE_REVISION_FUNCIONAL"
        return "REQUIERE_REVISION_FUNCIONAL"
    if hito == "H55":
        if cause == "CODCLI_LISTA_MULTIPLE_AFECTA_CONTEO":
            return "REQUIERE_MAPEO_INSTITUCIONAL"
        if cause == "PERIODO_NO_1_2":
            return "RESOLUBLE_CON_DECISION_FUNCIONAL"
        return "REQUIERE_REVISION_FUNCIONAL"
    if hito == "H56":
        if cause == "ESTADO_ACADEMICO_EXPLICA_AUSENCIA_2025":
            return "RESOLUBLE_CON_DECISION_FUNCIONAL"
        if "POSIBLE_MAPEO_CODCLI_LISTA_INCOMPLETO" in detected:
            return "REQUIERE_MAPEO_INSTITUCIONAL"
        return "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA"
    if hito == "H57":
        return "REQUIERE_MAPEO_INSTITUCIONAL"
    return "BLOQUEADO"


def risk_for_route(route: str, cause: str) -> str:
    if route == "RESOLUBLE_CON_DECISION_FUNCIONAL":
        return "ALTO: aplicar conteos sin decision funcional puede cambiar 16-19 sin regla cerrada."
    if route == "REQUIERE_MAPEO_INSTITUCIONAL":
        return "ALTO: asociar CODCLI/programa sin mapeo puede sumar actividad de otra identidad o carrera."
    if route == "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA":
        return "ALTO: ausencia de registros 2025 puede ocultar actividad academica no cubierta por PROMEDIOS."
    if route == "REQUIERE_REVISION_FUNCIONAL":
        return "MEDIO-ALTO: la evidencia actual no explica completamente la diferencia."
    if route == "NO_RESOLVER_AUTOMATICO":
        return "ALTO: no existe regla gobernada suficiente para correccion automatica."
    return "CRITICO: bloqueo de gobernanza impide cualquier uso operativo."


def priority_for_route(route: str, cause: str) -> str:
    if route in {"REQUIERE_MAPEO_INSTITUCIONAL", "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA", "BLOQUEADO"}:
        return "ALTA"
    if cause in {"POSIBLE_DATO_5809_NO_CALZA_CON_PROMEDIOS", "ESTADO_NULL_O_BLANCO"}:
        return "ALTA"
    return "MEDIA"


def action_for_route(route: str, cause: str, action_observed: str) -> str:
    if action_observed:
        return action_observed
    if route == "RESOLUBLE_CON_DECISION_FUNCIONAL":
        return "Cerrar decision funcional documentada y volver a validar gobernanza antes de corregir."
    if route == "REQUIERE_MAPEO_INSTITUCIONAL":
        return "Completar/validar mapeo institucional CODCLI_LISTA por programa antes de calcular."
    if route == "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA":
        return "Solicitar evidencia academica 2025 complementaria o documentar ausencia funcional."
    if route == "REQUIERE_REVISION_FUNCIONAL":
        return "Revisar manualmente la evidencia y documentar decision funcional."
    return "No ejecutar correccion automatica; mantener caso visible como pendiente."


def affected_columns(row: pd.Series, hito: str) -> str:
    if hito == "H54":
        return "19"
    if hito == "H55":
        cols = []
        if clean(row.get("DIF_CURSO_1ER_SEM", "")) == "SI":
            cols.append("16")
        if clean(row.get("DIF_CURSO_2DO_SEM", "")) == "SI":
            cols.append("17")
        if clean(row.get("DIF_UNIDADES_CURSADAS", "")) == "SI":
            cols.append("18")
        return ",".join(cols) if cols else "16,17,18"
    if hito in {"H56", "H57"}:
        return "16,17,18,19"
    return "16,17,18,19"


def observed_diff_columns(row: pd.Series) -> str:
    mapping = [
        ("OK_16_CURSO_1ER_SEM", "16"),
        ("OK_17_CURSO_2DO_SEM", "17"),
        ("OK_18_CURSADAS", "18"),
        ("OK_19_APROBADAS", "19"),
    ]
    cols = [col for field, col in mapping if field in row.index and clean(row.get(field, "")) == "NO"]
    return ",".join(cols) if cols else "SIN_DIFERENCIA_NUMERICA_OBSERVADA"


def normalize_case_frame(df: pd.DataFrame, hito: str, bloque: str) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        cause = clean(row.get("CAUSA_PRINCIPAL_PROPUESTA", "")) or clean(row.get("CAUSA_PRINCIPAL", ""))
        detected = clean(row.get("CAUSAS_DETECTADAS", ""))
        original = clean(row.get("DICTAMEN_HITO_53", "")) or clean(row.get("DICTAMEN_DICCIONARIO_ESTADO", ""))
        route = route_for_case(hito, cause, detected)
        action = action_for_route(route, cause, clean(row.get("ACCION_PROPUESTA", "")))
        rows.append(
            {
                "ID_CONSOLIDADO": f"{hito}_{clean(row.get('FILA_5809', ''))}",
                "HITO_AUDITORIA": hito,
                "BLOQUE_AUDITADO": bloque,
                "FILA_5809": clean(row.get("FILA_5809", "")),
                "RUT_NORMALIZADO": clean(row.get("RUT_NORMALIZADO", "")),
                "CODIGO_UNICO": clean(row.get("CODIGO_UNICO", "")),
                "PLAN_ESTUDIOS": clean(row.get("PLAN_ESTUDIOS", "")),
                "CODCLI_LISTA_NORM": clean(row.get("CODCLI_LISTA_NORM", "")),
                "CODCLI_LISTA_CANTIDAD": clean(row.get("CODCLI_LISTA_CANTIDAD", "")),
                "CAUSA_ORIGINAL_HITO_53": original,
                "CAUSA_AUDITADA": cause,
                "CAUSAS_DETECTADAS": detected,
                "COLUMNA_AFECTADA_16_19": affected_columns(row, hito),
                "COLUMNAS_CON_DIFERENCIA_OBSERVADA": observed_diff_columns(row),
                "RUTA_RESOLUCION": route,
                "ACCION_SUGERIDA": action,
                "RIESGO": risk_for_route(route, cause),
                "PRIORIDAD": priority_for_route(route, cause),
                "PUEDE_CORREGIRSE_AUTOMATICAMENTE": "NO",
                "REQUIERE_VALIDACION_HUMANA": "SI",
                "AFECTA_20_21": "NO EVALUADO / SEPARADO",
                "NO_APLICAR_CORRECCION": clean(row.get("NO_APLICAR_CORRECCION", "")) or NO_CORRECCION,
                "DECLARACION_CARGA": clean(row.get("DECLARACION_CARGA", "")) or DECLARACION_CARGA,
                "MOTIVO_DIAGNOSTICO": clean(row.get("MOTIVO_DIAGNOSTICO", "")),
            }
        )
    return pd.DataFrame(rows)


def load_consolidated_cases() -> pd.DataFrame:
    h54 = normalize_case_frame(read_sheet(H54_XLSX, "03_223_CASOS"), "H54", "DIFERENCIA_SOLO_APROBADAS_19")
    h55 = normalize_case_frame(read_sheet(H55_XLSX, "03_71_CASOS"), "H55", "DIFERENCIA_16_18_O_MULTIPLE")
    h56 = normalize_case_frame(read_sheet(H56_XLSX, "03_122_CASOS"), "H56", "SIN_REGISTROS_2025_PARA_CODCLI_LISTA")
    h57 = normalize_case_frame(read_sheet(H57_XLSX, "03_7_CASOS"), "H57", "BLOQUEO_SIN_CODCLI_LISTA")
    consolidated = pd.concat([h54, h55, h56, h57], ignore_index=True)
    if len(consolidated) != 423:
        raise RuntimeError(f"Consolidado debe tener 423 casos; tiene {len(consolidated)}")
    if consolidated["FILA_5809"].duplicated().any():
        dup = consolidated[consolidated["FILA_5809"].duplicated(keep=False)]["FILA_5809"].tolist()
        raise RuntimeError("FILA_5809 duplicadas en consolidado: " + ", ".join(dup[:20]))
    return consolidated


def validate_against_h53(consolidated: pd.DataFrame) -> pd.DataFrame:
    h53_parts = [
        ("03_DIF_SOLO_APROBADAS_19", read_sheet(MATRIZ_53, "03_DIF_SOLO_APROBADAS_19")),
        ("04_DIF_16_18_MULTIPLE", read_sheet(MATRIZ_53, "04_DIF_16_18_MULTIPLE")),
        ("05_SIN_REGISTROS_2025", read_sheet(MATRIZ_53, "05_SIN_REGISTROS_2025")),
        ("06_SIN_CODCLI_LISTA", read_sheet(MATRIZ_53, "06_SIN_CODCLI_LISTA")),
    ]
    rows = []
    expected_ids = set()
    for sheet, df in h53_parts:
        ids = {clean(v) for v in df["FILA_5809"].tolist()}
        expected_ids |= ids
        rows.append(
            {
                "Control": f"Matriz hito 53 hoja {sheet}",
                "Estado": "OK",
                "Casos": len(df),
                "Observacion": "Casos incorporados al universo consolidado.",
            }
        )
    actual_ids = set(consolidated["FILA_5809"].tolist())
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    rows.append(
        {
            "Control": "Cobertura consolidado vs hito 53",
            "Estado": "OK" if not missing and not extra and len(actual_ids) == 423 else "REVISAR",
            "Casos": len(actual_ids),
            "Observacion": f"faltantes={len(missing)}; extras={len(extra)}; unicos={len(actual_ids)}",
        }
    )
    if missing or extra or len(actual_ids) != 423:
        raise RuntimeError(f"Cobertura hito 53 no cierra: faltantes={missing[:10]}, extras={extra[:10]}")
    return pd.DataFrame(rows)


def build_resumen_ejecutivo(consolidated: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {"Indicador": "Estado de carga", "Valor": DECLARACION_CARGA, "Detalle": "No crear archivo de carga."},
        {"Indicador": "Total casos consolidados", "Valor": len(consolidated), "Detalle": "Universo 223+71+122+7."},
        {
            "Indicador": "Casos corregibles automaticamente ahora",
            "Valor": int((consolidated["PUEDE_CORREGIRSE_AUTOMATICAMENTE"] == "SI").sum()),
            "Detalle": "Debe ser 0 por gobernanza.",
        },
        {
            "Indicador": "Casos con validacion humana requerida",
            "Valor": int((consolidated["REQUIERE_VALIDACION_HUMANA"] == "SI").sum()),
            "Detalle": "Todos requieren decision, mapeo o fuente.",
        },
    ]
    for route in ROUTES:
        rows.append(
            {
                "Indicador": f"Ruta {route}",
                "Valor": int((consolidated["RUTA_RESOLUCION"] == route).sum()),
                "Detalle": "Clasificacion primaria de resolucion.",
            }
        )
    return pd.DataFrame(rows)


def build_plan_accion(consolidated: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        consolidated.groupby(["RUTA_RESOLUCION", "CAUSA_AUDITADA", "PRIORIDAD"], dropna=False)
        .agg(
            CASOS=("FILA_5809", "count"),
            COLUMNAS_AFECTADAS=("COLUMNA_AFECTADA_16_19", lambda s: " | ".join(sorted(set(s)))),
            ACCION_SUGERIDA=("ACCION_SUGERIDA", "first"),
            RIESGO=("RIESGO", "first"),
        )
        .reset_index()
    )
    order = {"ALTA": 1, "MEDIA": 2, "BAJA": 3}
    grouped["ORDEN_PRIORIDAD"] = grouped["PRIORIDAD"].map(order).fillna(9).astype(int)
    grouped["RESPONSABLE_SUGERIDO"] = grouped["RUTA_RESOLUCION"].map(
        {
            "RESOLUBLE_CON_DECISION_FUNCIONAL": "Responsable funcional academico",
            "REQUIERE_MAPEO_INSTITUCIONAL": "Equipo de datos institucionales / registro academico",
            "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA": "Area academica fuente PROMEDIOS",
            "REQUIERE_REVISION_FUNCIONAL": "Responsable funcional academico",
            "NO_RESOLVER_AUTOMATICO": "Comite proceso SIES",
            "BLOQUEADO": "Gobernanza del proceso",
        }
    )
    grouped["PUEDE_CORREGIRSE_AUTOMATICAMENTE_AHORA"] = "NO"
    grouped["DECLARACION_CARGA"] = DECLARACION_CARGA
    return grouped.sort_values(["ORDEN_PRIORIDAD", "RUTA_RESOLUCION", "CASOS"], ascending=[True, True, False])


def build_validation_df(validator: Dict[str, Any], coverage_df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "Control": "Gobernanza integral hito 51",
            "Estado": "USADA",
            "Evidencia": str(GOBERNANZA_51),
            "Hash SHA256": sha256_file(GOBERNANZA_51),
            "Observacion": "Base obligatoria para fuentes, columnas, llaves y diccionarios.",
        },
        {
            "Control": "Validador hito 52",
            "Estado": validator["estado_validador"],
            "Evidencia": validator["validator_manifest"],
            "Hash SHA256": sha256_file(Path(validator["validator_manifest"])),
            "Observacion": "Compuerta ejecutada antes de generar hito 58.",
        },
        {
            "Control": "Matriz hito 53",
            "Estado": "USADA",
            "Evidencia": str(MATRIZ_53),
            "Hash SHA256": sha256_file(MATRIZ_53),
            "Observacion": "Universo original de 423 pendientes 16-19.",
        },
    ]
    for label, path in [
        ("Auditoria hito 54", H54_XLSX),
        ("Auditoria hito 55", H55_XLSX),
        ("Auditoria hito 56", H56_XLSX),
        ("Auditoria hito 57", H57_XLSX),
    ]:
        rows.append(
            {
                "Control": label,
                "Estado": "USADA",
                "Evidencia": str(path),
                "Hash SHA256": sha256_file(path),
                "Observacion": "Entrada auditada no modificada.",
            }
        )
    rows.append(
        {
            "Control": "Cobertura hito 53",
            "Estado": "OK",
            "Evidencia": " / ".join(coverage_df["Control"].tolist()),
            "Hash SHA256": "",
            "Observacion": "Cobertura completa: 423 casos unicos.",
        }
    )
    rows.append(
        {
            "Control": "Plan validador hito 52 para consolidado",
            "Estado": validator["estado_validador"],
            "Evidencia": validator["plan_path"],
            "Hash SHA256": sha256_file(Path(validator["plan_path"])),
            "Observacion": "Plan documental no correctivo.",
        }
    )
    return pd.DataFrame(rows)


def build_dictamen(consolidated: pd.DataFrame, validator: Dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Proceso": PROCESO,
                "Subproyecto": SUBPROYECTO,
                "Anio proceso": ANIO_PROCESO,
                "Anio referencia datos": ANIO_REFERENCIA_DATOS,
                "Estado de carga": DECLARACION_CARGA,
                "Estado validador": validator["estado_validador"],
                "Fuentes originales modificadas": "NO",
                "Correcciones aplicadas": "NO",
                "SIES_READY generado": "NO",
                "Archivo de carga creado": "NO",
                "Recalculo 20-21": "NO",
                "Total casos consolidados": len(consolidated),
                "Total rutas": consolidated["RUTA_RESOLUCION"].nunique(),
                "Corregibles automaticamente ahora": int(
                    (consolidated["PUEDE_CORREGIRSE_AUTOMATICAMENTE"] == "SI").sum()
                ),
                "Requieren validacion humana": int(
                    (consolidated["REQUIERE_VALIDACION_HUMANA"] == "SI").sum()
                ),
                "Dictamen global": (
                    "NO_LISTO_PARA_CARGA: consolidado gobernado de resolucion 16-19; "
                    "no aplica correccion automatica ni generacion de carga."
                ),
                "Proximo paso permitido": (
                    "Cerrar decisiones funcionales, mapeos institucionales y/o fuentes complementarias; "
                    "luego revalidar gobernanza antes de cualquier correccion."
                ),
            }
        ]
    )


def build_fuentes_df(output_dir: Path, output_paths: Dict[str, Path], validator: Dict[str, Any]) -> pd.DataFrame:
    inputs = [
        ("INPUT", "Gobernanza integral hito 51", GOBERNANZA_51),
        ("INPUT", "Validador hito 52 xlsx base", VALIDADOR_52_XLSX),
        ("INPUT", "Validador hito 52 script", VALIDADOR_52_SCRIPT),
        ("INPUT", "Matriz hito 53", MATRIZ_53),
        ("INPUT", "Auditoria hito 54", H54_XLSX),
        ("INPUT", "Auditoria hito 55", H55_XLSX),
        ("INPUT", "Auditoria hito 56", H56_XLSX),
        ("INPUT", "Auditoria hito 57", H57_XLSX),
        ("INPUT", "Manifest hito 54", H54_MANIFEST),
        ("INPUT", "Manifest hito 55", H55_MANIFEST),
        ("INPUT", "Manifest hito 56", H56_MANIFEST),
        ("INPUT", "Manifest hito 57", H57_MANIFEST),
        ("INPUT_DERIVADO", "Manifest validador hito 52 ejecucion hito 58", Path(validator["validator_manifest"])),
    ]
    rows = []
    for tipo, nombre, path in inputs:
        rows.append(
            {
                "Tipo": tipo,
                "Nombre": nombre,
                "Ruta": str(path),
                "Existe": "SI" if path.exists() else "NO",
                "Hash SHA256": sha256_file(path) if path.exists() else "",
                "Uso": "Entrada o compuerta obligatoria; no modificada.",
            }
        )
    for key, path in output_paths.items():
        rows.append(
            {
                "Tipo": "OUTPUT",
                "Nombre": key,
                "Ruta": str(path),
                "Existe": "SI" if path.exists() else "NO",
                "Hash SHA256": sha256_file(path) if path.exists() and key != "manifest" else "",
                "Uso": "Producto hito 58 no apto para carga. Manifest sin hash autorreferencial.",
            }
        )
    rows.append(
        {
            "Tipo": "OUTPUT_DIR",
            "Nombre": "Carpeta hito 58",
            "Ruta": str(output_dir),
            "Existe": "SI" if output_dir.exists() else "NO",
            "Hash SHA256": "",
            "Uso": "Contenedor de consolidado gobernado.",
        }
    )
    return pd.DataFrame(rows)


def write_excel(path: Path, sheets: Dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for logical_name, df in sheets.items():
            df.to_excel(writer, sheet_name=SHEETS.get(logical_name, logical_name)[:31], index=False)
    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        for col_idx, column_cells in enumerate(ws.columns, start=1):
            values = [display(cell.value, 90) for cell in column_cells[:200]]
            width = min(max([len(v) for v in values] + [10]) + 2, 60)
            ws.column_dimensions[get_column_letter(col_idx)].width = width
    wb.save(path)


def build_manifest(
    timestamp: str,
    output_dir: Path,
    output_paths: Dict[str, Path],
    validator: Dict[str, Any],
    dictamen_df: pd.DataFrame,
    consolidated: pd.DataFrame,
    sheets: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    return {
        "proceso": PROCESO,
        "subproyecto": SUBPROYECTO,
        "timestamp": timestamp,
        "anio_proceso": ANIO_PROCESO,
        "anio_referencia_datos": ANIO_REFERENCIA_DATOS,
        "declaracion_carga": DECLARACION_CARGA,
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "sies_ready_generado": "NO",
        "archivo_carga_creado": "NO",
        "recalculo_20_21": "NO",
        "estado_validador_hito_52": validator["estado_validador"],
        "carpeta_salida": str(output_dir),
        "archivos": {key: str(path) for key, path in output_paths.items()},
        "entradas_obligatorias": {
            "gobernanza_51": str(GOBERNANZA_51),
            "validador_52_script": str(VALIDADOR_52_SCRIPT),
            "validador_52_xlsx": str(VALIDADOR_52_XLSX),
            "matriz_53": str(MATRIZ_53),
            "hito_54": str(H54_XLSX),
            "hito_55": str(H55_XLSX),
            "hito_56": str(H56_XLSX),
            "hito_57": str(H57_XLSX),
        },
        "validador_hito_52_ejecucion": {
            "plan": validator["plan_path"],
            "manifest": validator["validator_manifest"],
            "carpeta": validator["validator_dir"],
            "returncode": validator["returncode"],
        },
        "conteos": {
            "casos_consolidados": int(dictamen_df.loc[0, "Total casos consolidados"]),
            "rutas": consolidated["RUTA_RESOLUCION"].value_counts().to_dict(),
            "bloques": consolidated["BLOQUE_AUDITADO"].value_counts().to_dict(),
            "corregibles_automaticamente_ahora": int(
                (consolidated["PUEDE_CORREGIRSE_AUTOMATICAMENTE"] == "SI").sum()
            ),
            "validacion_humana_requerida": int((consolidated["REQUIERE_VALIDACION_HUMANA"] == "SI").sum()),
            "hojas_excel": {name: len(df) for name, df in sheets.items()},
        },
        "hashes_salida": {
            key: sha256_file(path) for key, path in output_paths.items() if path.exists() and key != "manifest"
        },
    }


def build_markdown(
    output_dir: Path,
    dictamen_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    resumen_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    manifest: Dict[str, Any],
) -> str:
    lines = [
        "# Informe Consolidado Resolucion 16-19 Gobernado 5809",
        "",
        f"- Proceso: {PROCESO}",
        f"- Subproyecto: {SUBPROYECTO}",
        f"- Anio proceso: {ANIO_PROCESO}",
        f"- Anio referencia datos: {ANIO_REFERENCIA_DATOS}",
        f"- Declaracion carga: {DECLARACION_CARGA}",
        "- Fuentes originales modificadas: NO",
        "- Correcciones aplicadas: NO",
        "- SIES_READY generado: NO",
        "- Archivo de carga creado: NO",
        "- Recalculo 20-21: NO",
        f"- Carpeta: {output_dir}",
        "",
        "## Dictamen",
        "",
        markdown_table(dictamen_df),
        "",
        "## Validacion de gobernanza",
        "",
        markdown_table(validation_df[["Control", "Estado", "Observacion"]]),
        "",
        "## Resumen ejecutivo",
        "",
        markdown_table(resumen_df),
        "",
        "## Plan de accion propuesto",
        "",
        markdown_table(
            plan_df[
                [
                    "RUTA_RESOLUCION",
                    "CAUSA_AUDITADA",
                    "PRIORIDAD",
                    "CASOS",
                    "RESPONSABLE_SUGERIDO",
                    "PUEDE_CORREGIRSE_AUTOMATICAMENTE_AHORA",
                ]
            ],
            max_rows=25,
        ),
        "",
        "## Criterio operativo",
        "",
        "- Este consolidado no corrige datos y no crea salida de carga.",
        "- Todas las rutas quedan con correccion automatica actual en NO.",
        "- 20-21 permanece NO EVALUADO / SEPARADO.",
        "- Cualquier correccion futura debe reingresar por gobernanza y validador precalculo.",
        "",
        "## Archivos",
        "",
        f"- Excel: {manifest.get('archivos', {}).get('excel', '')}",
        f"- Informe: {manifest.get('archivos', {}).get('informe', '')}",
        f"- Manifest: {manifest.get('archivos', {}).get('manifest', '')}",
        f"- Script: {manifest.get('archivos', {}).get('script', '')}",
        "",
    ]
    return "\n".join(lines)


def print_console(
    dictamen_df: pd.DataFrame,
    resumen_df: pd.DataFrame,
    consolidated: pd.DataFrame,
    output_paths: Dict[str, Path],
    output_dir: Path,
    validator_state: str,
) -> None:
    print("CONSOLIDADO RESOLUCION 16-19 GOBERNADO 5809 — GENERADO")
    print("Fuentes originales modificadas: NO")
    print("Declaracion carga: NO_LISTO_PARA_CARGA")
    print(f"Estado validador: {validator_state}")
    print()
    print("DICTAMEN")
    print(dictamen_df.to_string(index=False))
    print()
    print("RESUMEN RUTAS")
    print(consolidated["RUTA_RESOLUCION"].value_counts().rename_axis("RUTA_RESOLUCION").reset_index(name="CASOS").to_string(index=False))
    print()
    print("RESUMEN EJECUTIVO")
    print(resumen_df.to_string(index=False))
    print()
    print("ARCHIVOS")
    print(f"Excel: {output_paths['excel']}")
    print(f"Informe: {output_paths['informe']}")
    print(f"Manifest: {output_paths['manifest']}")
    print(f"Script: {output_paths['script']}")
    print(f"Carpeta hito: {output_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolidado hito 58 resolucion 16-19 gobernado 5809")
    parser.add_argument("--timestamp", default=None, help="Timestamp YYYYMMDD_HHMMSS. Si se omite, usa fecha/hora actual.")
    args = parser.parse_args()

    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = BASE_58 / f"CONSOLIDADO_RESOLUCION_16_19_GOBERNADO_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = {
        "excel": output_dir / OUTPUT_FILES["excel"],
        "informe": output_dir / OUTPUT_FILES["informe"],
        "manifest": output_dir / OUTPUT_FILES["manifest"],
        "script": output_dir / OUTPUT_FILES["script"],
    }

    require_paths()
    current_script = Path(__file__).resolve()
    target_script = output_paths["script"].resolve()
    if current_script != target_script:
        shutil.copy2(current_script, target_script)

    validator = run_validator_52(output_dir, timestamp)
    consolidated = load_consolidated_cases()
    coverage_df = validate_against_h53(consolidated)
    dictamen_df = build_dictamen(consolidated, validator)
    validation_df = build_validation_df(validator, coverage_df)
    resumen_df = build_resumen_ejecutivo(consolidated)
    plan_df = build_plan_accion(consolidated)
    pendientes_df = consolidated.sort_values(["PRIORIDAD", "RUTA_RESOLUCION", "FILA_5809"]).copy()

    sheets = OrderedDict(
        [
            ("00_DICTAMEN", dictamen_df),
            ("01_VALIDACION_GOBERNANZA", validation_df),
            ("02_RESUMEN_EJECUTIVO", resumen_df),
            ("03_CONSOLIDADO_423", consolidated),
            (
                "04_RUTA_DECISION_FUNCIONAL",
                consolidated[consolidated["RUTA_RESOLUCION"] == "RESOLUBLE_CON_DECISION_FUNCIONAL"],
            ),
            (
                "05_RUTA_MAPEO_INSTITUCIONAL",
                consolidated[consolidated["RUTA_RESOLUCION"] == "REQUIERE_MAPEO_INSTITUCIONAL"],
            ),
            (
                "06_RUTA_FUENTE_COMPLEMENTARIA",
                consolidated[consolidated["RUTA_RESOLUCION"] == "REQUIERE_FUENTE_ACADEMICA_COMPLEMENTARIA"],
            ),
            (
                "07_RUTA_NO_RESOLVER_AUTOMATICO",
                consolidated[consolidated["PUEDE_CORREGIRSE_AUTOMATICAMENTE"] == "NO"],
            ),
            ("08_PROPUESTA_PLAN_ACCION", plan_df),
            ("09_PENDIENTES_POR_PRIORIDAD", pendientes_df),
        ]
    )
    sheets["10_FUENTES"] = build_fuentes_df(output_dir, output_paths, validator)
    write_excel(output_paths["excel"], sheets)

    manifest = build_manifest(timestamp, output_dir, output_paths, validator, dictamen_df, consolidated, sheets)
    output_paths["informe"].write_text(
        build_markdown(output_dir, dictamen_df, validation_df, resumen_df, plan_df, manifest),
        encoding="utf-8",
    )
    sheets["10_FUENTES"] = build_fuentes_df(output_dir, output_paths, validator)
    write_excel(output_paths["excel"], sheets)
    manifest = build_manifest(timestamp, output_dir, output_paths, validator, dictamen_df, consolidated, sheets)
    output_paths["manifest"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print_console(dictamen_df, resumen_df, consolidated, output_paths, output_dir, validator["estado_validador"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
