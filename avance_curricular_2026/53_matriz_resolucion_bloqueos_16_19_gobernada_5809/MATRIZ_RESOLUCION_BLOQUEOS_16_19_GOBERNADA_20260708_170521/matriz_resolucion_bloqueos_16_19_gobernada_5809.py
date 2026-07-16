#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Matriz gobernada de resolucion de bloqueos 16-19, paso 50.

Este hito clasifica y propone rutas de resolucion. No modifica fuentes
originales, no genera SIES_READY, no recalcula 20-21 y no aplica correcciones
automaticas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import unicodedata
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


PROCESO = "Avance Curricular SIES 2026"
SUBPROYECTO = "Matriz resolucion bloqueos 16-19 gobernada 5809"
ANIO_PROCESO = 2026
ANIO_REFERENCIA_DATOS = 2025
DECLARACION_CARGA = "NO_LISTO_PARA_CARGA"
NO_CORRECCION = "NO_APLICAR_CORRECCION_AUTOMATICA"

REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BASE_53 = REPO / "avance_curricular_2026" / "53_matriz_resolucion_bloqueos_16_19_gobernada_5809"

GOBERNANZA_51 = (
    REPO
    / "avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/"
    / "GOBERNANZA_INTEGRAL_5809_20260708_144544/"
    / "GOBERNANZA_INTEGRAL_INPUTS_COLUMNAS_TRANSFORMACIONES_5809.xlsx"
)
VALIDADOR_52 = (
    REPO
    / "avance_curricular_2026/52_validador_gobernanza_precalculo_5809/"
    / "VALIDADOR_GOBERNANZA_PRECALCULO_5809_20260708_165151/"
    / "validador_gobernanza_precalculo_5809.py"
)
RECALCULO_50 = (
    REPO
    / "avance_curricular_2026/50_recalculo_16_19_diccionario_estado_promedios/"
    / "RECALCULO_16_19_DICCIONARIO_ESTADO_PROMEDIOS_20260708_143748/"
    / "02_RESULTADOS/RECALCULO_16_19_DICCIONARIO_ESTADO_PROMEDIOS.xlsx"
)

OUTPUT_FILES = {
    "excel": "MATRIZ_RESOLUCION_BLOQUEOS_16_19_GOBERNADA_5809.xlsx",
    "informe": "INFORME_MATRIZ_RESOLUCION_BLOQUEOS_16_19_GOBERNADA_5809.md",
    "manifest": "manifest_matriz_resolucion_bloqueos_16_19_gobernada_5809.json",
    "script": "matriz_resolucion_bloqueos_16_19_gobernada_5809.py",
}

SHEETS = [
    "00_DICTAMEN",
    "01_VALIDACION_GOBERNANZA",
    "02_RESUMEN_BLOQUEOS",
    "03_DIF_SOLO_APROBADAS_19",
    "04_DIF_16_18_MULTIPLE",
    "05_SIN_REGISTROS_2025",
    "06_SIN_CODCLI_LISTA",
    "07_PROPUESTA_ACCION",
    "08_NO_RESOLVER_AUTOMATICO",
    "09_FUENTES",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def clean(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def norm(value: Any) -> str:
    text = clean(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    out = []
    for ch in text.upper():
        out.append(ch if ch.isalnum() else "_")
    return "_".join("".join(out).split("_"))


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


def read_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, dtype=str).fillna("")


def style_workbook(path: Path) -> None:
    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="305496")
    header_font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for col_idx in range(1, min(ws.max_column, 50) + 1):
            letter = get_column_letter(col_idx)
            max_len = 12
            for cell in ws[letter][: min(ws.max_row, 200)]:
                text = "" if cell.value is None else str(cell.value)
                max_len = max(max_len, min(len(text), 90))
            ws.column_dimensions[letter].width = min(max_len + 2, 65)
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(path)
    wb.close()


def write_excel(path: Path, dataframes: OrderedDict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in dataframes.items():
            safe_df = df.copy()
            for col in safe_df.columns:
                safe_df[col] = safe_df[col].map(
                    lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                )
            safe_df.to_excel(writer, sheet_name=sheet_name, index=False)
    style_workbook(path)


def parse_states(value: Any) -> List[str]:
    text = clean(value).replace("NULL", "NULL")
    if not text:
        return []
    states = []
    for part in text.split("|"):
        item = part.strip().upper()
        if not item:
            continue
        states.append(item)
    return sorted(set(states))


def state_summary(states: List[str]) -> str:
    return " | ".join(states) if states else "SIN_ESTADOS_2025"


def classify_row(row: pd.Series) -> Dict[str, str]:
    dictamen = clean(row.get("DICTAMEN_DICCIONARIO_ESTADO", ""))
    states = parse_states(row.get("ESTADOS_OBSERVADOS_2025", ""))
    state_set = set(states)
    has_e = "E" in state_set
    has_i = "I" in state_set
    has_null = "NULL" in state_set or "" in state_set
    has_unknown = bool(state_set - {"A", "E", "I", "R", "NULL"})

    base = {
        "ESTADOS_NORMALIZADOS": state_summary(states),
        "PUEDE_RESOLVERSE_AUTOMATICAMENTE_AHORA": "NO",
        "NO_APLICAR_CORRECCION": NO_CORRECCION,
        "DECLARACION_CARGA": DECLARACION_CARGA,
    }

    if dictamen == "BLOQUEO_SIN_CODCLI_LISTA":
        base.update(
            {
                "TIPO_RESOLUCION": "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL",
                "SUBCATEGORIA_RESOLUCION": "SIN_LLAVE_CODCLI_LISTA",
                "REQUIERE_REVISION_FUNCIONAL": "SI",
                "RESOLUBLE_TECNICAMENTE_POST_VALIDACION": "NO",
                "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL": "SI",
                "ACCION_PROPUESTA": "Resolver identidad academica y completar CODCLI_LISTA antes de cualquier conteo.",
                "EVIDENCIA_MINIMA_PARA_RESOLVER": "CODCLI_LISTA validado contra PROMEDIOS y programa 2025.",
                "MOTIVO_NO_AUTOMATICO": "Sin llave academica gobernada no existe cruce permitido.",
            }
        )
        return base

    if dictamen == "SIN_REGISTROS_2025_PARA_CODCLI_LISTA":
        base.update(
            {
                "TIPO_RESOLUCION": "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL",
                "SUBCATEGORIA_RESOLUCION": "SIN_REGISTROS_2025_EN_PROMEDIOS",
                "REQUIERE_REVISION_FUNCIONAL": "SI",
                "RESOLUBLE_TECNICAMENTE_POST_VALIDACION": "NO",
                "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL": "SI",
                "ACCION_PROPUESTA": "Revisar cobertura de PROMEDIOS, mapeo CODCLI_LISTA y evidencia academica 2025.",
                "EVIDENCIA_MINIMA_PARA_RESOLVER": "Registro academico 2025 valido o decision funcional documentada de ausencia.",
                "MOTIVO_NO_AUTOMATICO": "No hay evidencia 2025 para sustentar conteo automatico.",
            }
        )
        return base

    if dictamen == "DIFERENCIA_16_18_O_MULTIPLE":
        mismatches = []
        for field, label in [
            ("OK_16_CURSO_1ER_SEM", "16"),
            ("OK_17_CURSO_2DO_SEM", "17"),
            ("OK_18_CURSADAS", "18"),
            ("OK_19_APROBADAS", "19"),
        ]:
            if clean(row.get(field, "")).upper() == "NO":
                mismatches.append(label)
        base.update(
            {
                "TIPO_RESOLUCION": "REQUIERE_REVISION_TECNICA_FUNCIONAL",
                "SUBCATEGORIA_RESOLUCION": "DIFERENCIA_" + "_".join(mismatches or ["MULTIPLE"]),
                "REQUIERE_REVISION_FUNCIONAL": "SI",
                "RESOLUBLE_TECNICAMENTE_POST_VALIDACION": "SI",
                "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL": "NO",
                "ACCION_PROPUESTA": "Revisar periodo, CODRAMO unico, duplicados, programa 2025 y coherencia semestres/cursadas.",
                "EVIDENCIA_MINIMA_PARA_RESOLVER": "Cardinalidad CODCLI-programa, ANO=2025, PERIODO y deduplicacion CODRAMO documentadas.",
                "MOTIVO_NO_AUTOMATICO": "La diferencia afecta presencia/cursadas y no solo diccionario de aprobadas.",
            }
        )
        return base

    if dictamen == "DIFERENCIA_SOLO_APROBADAS_19":
        if has_null or has_unknown:
            sub = "APROBADAS_19_CON_NULL_O_ESTADO_NO_CATALOGADO"
            tipo = "REQUIERE_REVISION_FUNCIONAL"
            funcional = "SI"
            tecnica = "NO"
            accion = "Resolver tratamiento de NULL/blanco o estado no catalogado antes de contar aprobadas."
            evidencia = "Decision funcional para NULL/blanco y trazabilidad por CODRAMO."
            motivo = "NULL/blanco no se aplica automaticamente segun gobernanza 51."
        elif has_e and has_i:
            sub = "APROBADAS_19_CON_CONVALIDACION_Y_HOMOLOGACION"
            tipo = "REQUIERE_REVISION_FUNCIONAL"
            funcional = "SI"
            tecnica = "SI"
            accion = "Definir separacion anual 2025 vs convalidacion/homologacion antes de aceptar recuento."
            evidencia = "Decision funcional documentada para E e I en UNIDADES_APROBADAS anual."
            motivo = "E/I requieren validacion funcional para el campo anual 19."
        elif has_e:
            sub = "APROBADAS_19_CON_CONVALIDACION"
            tipo = "REQUIERE_REVISION_FUNCIONAL"
            funcional = "SI"
            tecnica = "SI"
            accion = "Confirmar si E=CONVALIDACION aplica al campo anual 19 o queda excluido."
            evidencia = "Decision funcional sobre convalidaciones anuales 2025."
            motivo = "El instructivo excluye validaciones en aprobadas anuales salvo decision funcional aplicable."
        elif has_i:
            sub = "APROBADAS_19_CON_HOMOLOGACION"
            tipo = "REQUIERE_REVISION_FUNCIONAL"
            funcional = "SI"
            tecnica = "SI"
            accion = "Confirmar si I=HOMOLOGADO aplica al campo anual 19 o queda excluido."
            evidencia = "Decision funcional sobre homologaciones anuales 2025."
            motivo = "I es aprobatorio observado, pero su aplicacion anual debe validarse."
        elif state_set and state_set.issubset({"A", "R"}):
            sub = "APROBADAS_19_SOLO_ESTADOS_CERRADOS_A_R"
            tipo = "RESOLUBLE_TECNICO_POST_VALIDACION"
            funcional = "NO"
            tecnica = "SI"
            accion = "Revisar conteo CODRAMO unico con A aprobado y R no aprobado; preparar ajuste candidato no automatico."
            evidencia = "Detalle por CODRAMO, deduplicacion y confirmacion de programa 2025."
            motivo = "Aunque el diccionario esta cerrado para A/R, no se aplican correcciones automaticas en este hito."
        else:
            sub = "APROBADAS_19_SIN_ESTADOS_OBSERVADOS"
            tipo = "REQUIERE_REVISION_FUNCIONAL"
            funcional = "SI"
            tecnica = "NO"
            accion = "Revisar evidencia academica antes de clasificar aprobadas.",
            evidencia = "Estados observados y detalle por CODRAMO."
            motivo = "No hay estados suficientes para resolver."
        base.update(
            {
                "TIPO_RESOLUCION": tipo,
                "SUBCATEGORIA_RESOLUCION": sub,
                "REQUIERE_REVISION_FUNCIONAL": funcional,
                "RESOLUBLE_TECNICAMENTE_POST_VALIDACION": tecnica,
                "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL": "NO" if tecnica == "SI" else "SI",
                "ACCION_PROPUESTA": accion if isinstance(accion, str) else accion[0],
                "EVIDENCIA_MINIMA_PARA_RESOLVER": evidencia,
                "MOTIVO_NO_AUTOMATICO": motivo,
            }
        )
        return base

    base.update(
        {
            "TIPO_RESOLUCION": "REQUIERE_REVISION_FUNCIONAL",
            "SUBCATEGORIA_RESOLUCION": "DICTAMEN_NO_CATALOGADO",
            "REQUIERE_REVISION_FUNCIONAL": "SI",
            "RESOLUBLE_TECNICAMENTE_POST_VALIDACION": "NO",
            "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL": "SI",
            "ACCION_PROPUESTA": "Catalogar dictamen antes de resolver.",
            "EVIDENCIA_MINIMA_PARA_RESOLVER": "Regla de clasificacion gobernada.",
            "MOTIVO_NO_AUTOMATICO": "Dictamen no reconocido por la matriz.",
        }
    )
    return base


def classify_pending(pending_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in pending_df.iterrows():
        classification = classify_row(row)
        rows.append({**row.to_dict(), **classification})
    preferred = [
        "FILA_5809",
        "RUT_NORMALIZADO",
        "CODIGO_UNICO",
        "PLAN_ESTUDIOS",
        "CODCLI_LISTA_NORM",
        "CODCLI_LISTA_CANTIDAD",
        "REGISTROS_2025",
        "DICTAMEN_DICCIONARIO_ESTADO",
        "TIPO_RESOLUCION",
        "SUBCATEGORIA_RESOLUCION",
        "ESTADOS_OBSERVADOS_2025",
        "ESTADOS_NORMALIZADOS",
        "REQUIERE_REVISION_FUNCIONAL",
        "RESOLUBLE_TECNICAMENTE_POST_VALIDACION",
        "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL",
        "PUEDE_RESOLVERSE_AUTOMATICAMENTE_AHORA",
        "ACCION_PROPUESTA",
        "EVIDENCIA_MINIMA_PARA_RESOLVER",
        "MOTIVO_NO_AUTOMATICO",
        "NO_APLICAR_CORRECCION",
        "DECLARACION_CARGA",
    ]
    out = pd.DataFrame(rows)
    cols = [c for c in preferred if c in out.columns] + [c for c in out.columns if c not in preferred]
    return out[cols]


def build_summary(classified_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        classified_df.groupby(
            [
                "DICTAMEN_DICCIONARIO_ESTADO",
                "TIPO_RESOLUCION",
                "SUBCATEGORIA_RESOLUCION",
                "REQUIERE_REVISION_FUNCIONAL",
                "RESOLUBLE_TECNICAMENTE_POST_VALIDACION",
                "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="CASOS")
        .sort_values(["DICTAMEN_DICCIONARIO_ESTADO", "CASOS"], ascending=[True, False])
    )
    return summary


def build_actions(classified_df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        classified_df.groupby(
            [
                "TIPO_RESOLUCION",
                "SUBCATEGORIA_RESOLUCION",
                "ACCION_PROPUESTA",
                "EVIDENCIA_MINIMA_PARA_RESOLVER",
                "MOTIVO_NO_AUTOMATICO",
            ],
            dropna=False,
        )
        .agg(
            CASOS=("FILA_5809", "count"),
            BLOQUEOS=("DICTAMEN_DICCIONARIO_ESTADO", lambda x: " | ".join(sorted(set(map(clean, x))))),
        )
        .reset_index()
    )
    grouped["PUEDE_RESOLVERSE_AUTOMATICAMENTE_AHORA"] = "NO"
    grouped["SIGUIENTE_HITO_PROPUESTO"] = grouped["TIPO_RESOLUCION"].map(
        {
            "RESOLUBLE_TECNICO_POST_VALIDACION": "Preparar ajuste candidato auditado, previa validacion funcional de no impacto.",
            "REQUIERE_REVISION_FUNCIONAL": "Mesa funcional: confirmar regla o documentar exclusion.",
            "REQUIERE_REVISION_TECNICA_FUNCIONAL": "Auditoria tecnica y funcional de periodo/programa/deduplicacion.",
            "NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL": "Completar fuente, llave o evidencia antes de cualquier propuesta.",
        }
    )
    return grouped.sort_values(["TIPO_RESOLUCION", "CASOS"], ascending=[True, False])


def build_no_auto(classified_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "FILA_5809",
        "RUT_NORMALIZADO",
        "CODIGO_UNICO",
        "PLAN_ESTUDIOS",
        "CODCLI_LISTA_NORM",
        "DICTAMEN_DICCIONARIO_ESTADO",
        "TIPO_RESOLUCION",
        "SUBCATEGORIA_RESOLUCION",
        "MOTIVO_NO_AUTOMATICO",
        "ACCION_PROPUESTA",
        "NO_APLICAR_CORRECCION",
        "DECLARACION_CARGA",
    ]
    return classified_df[[c for c in cols if c in classified_df.columns]].copy()


def run_validator_52(output_dir: Path, timestamp: str) -> Dict[str, Any]:
    plan_path = output_dir / "plan_uso_validador_h52_matriz_16_19.json"
    plan = {
        "descripcion": "Matriz de clasificacion de bloqueos 16-19. No recalcula, no corrige, no genera carga.",
        "columnas_usadas": ["CODIGO_UNICO", "PLAN_ESTUDIOS", "CODCLI_LISTA", "ESTADO", "DESCRIPCION_ESTADO"],
        "llaves_usadas": ["CODCLI_LISTA", "CODIGO_UNICO", "PLAN_ESTUDIOS"],
        "diccionarios_usados": ["DIC_ESTADO_PROMEDIOS"],
        "transformaciones": ["Clasificacion documental de bloqueos; sin transformacion de datos fuente"],
        "campos_calculo": ["16", "17", "18", "19"],
        "anio_calculo": 2025,
        "genera_sies_ready": False,
        "modifica_fuentes_originales": False,
        "usa_todos_codcli_rut": False,
        "filtra_por_programa": True,
        "usa_inferencias_como_reglas_oficiales": False,
        "usa_estados_AEIR": True,
        "usa_codcli_lista": True,
        "mezcla_anual_acumulado": False,
        "modo": "CLASIFICACION_NO_OPERATIVA_SIN_RECALCULO",
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    validator_timestamp = f"{timestamp}_H53"
    cmd = [
        sys.executable,
        str(VALIDADOR_52),
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
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = {
        "plan_path": str(plan_path),
        "validator_timestamp": validator_timestamp,
        "validator_dir": str(validator_dir),
        "validator_manifest": str(manifest_path),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "estado_validador": manifest.get("estado_validador", "SIN_MANIFEST"),
        "declaracion_carga": manifest.get("estado_carga", ""),
        "fuentes_originales_modificadas": manifest.get("fuentes_originales_modificadas", ""),
        "plan": plan,
    }
    if completed.returncode != 0:
        raise RuntimeError("Validador hito 52 fallo:\n" + completed.stdout + "\n" + completed.stderr)
    if result["estado_validador"] != "APTO_PARA_CONTROL_PREVIO":
        raise RuntimeError(f"Validador hito 52 no apto: {result['estado_validador']}")
    return result


def build_validation_sheet(validator_result: Dict[str, Any]) -> pd.DataFrame:
    rows = [
        {
            "Control": "Validador hito 52 ejecutado",
            "Estado": "OK" if validator_result["returncode"] == 0 else "ERROR",
            "Evidencia": validator_result["validator_manifest"],
            "Observacion": "Ejecucion obligatoria previa al hito 53.",
        },
        {
            "Control": "Estado validador",
            "Estado": validator_result["estado_validador"],
            "Evidencia": validator_result["validator_dir"],
            "Observacion": "Debe ser APTO_PARA_CONTROL_PREVIO para construir matriz.",
        },
        {
            "Control": "Declaracion carga heredada",
            "Estado": validator_result["declaracion_carga"],
            "Evidencia": validator_result["validator_manifest"],
            "Observacion": "La matriz conserva NO_LISTO_PARA_CARGA.",
        },
        {
            "Control": "Fuentes originales modificadas",
            "Estado": validator_result["fuentes_originales_modificadas"],
            "Evidencia": validator_result["validator_manifest"],
            "Observacion": "Debe ser NO.",
        },
        {
            "Control": "Uso de columnas derivadas paso 50",
            "Estado": "EVIDENCIA_TECNICA_NO_NORMATIVA",
            "Evidencia": "RECALCULO_16_19_DICCIONARIO_ESTADO_PROMEDIOS.xlsx / hoja 06_PENDIENTES_16_19",
            "Observacion": "No se usan como regla oficial ni como correccion automatica.",
        },
    ]
    return pd.DataFrame(rows)


def source_hashes(paths: Dict[str, Path]) -> Dict[str, str]:
    return {key: sha256_file(path) for key, path in paths.items()}


def build_sources(paths: Dict[str, Path], hashes_before: Dict[str, str], hashes_after: Dict[str, str], outputs: Dict[str, Path]) -> pd.DataFrame:
    rows = []
    for key, path in paths.items():
        rows.append(
            {
                "Tipo": "INPUT_OBLIGATORIO",
                "ID": key,
                "Ruta": str(path),
                "Hash antes": hashes_before.get(key, ""),
                "Hash despues": hashes_after.get(key, ""),
                "Modificada": "NO" if hashes_before.get(key, "") == hashes_after.get(key, "") else "SI",
                "Uso": "Lectura / evidencia gobernada; no se modifica.",
            }
        )
    for key, path in outputs.items():
        rows.append(
            {
                "Tipo": "SALIDA_HITO_53",
                "ID": key,
                "Ruta": str(path),
                "Hash antes": "",
                "Hash despues": sha256_file(path) if path.exists() and path.is_file() else "",
                "Modificada": "DERIVADO",
                "Uso": "Producto generado por hito 53.",
            }
        )
    return pd.DataFrame(rows)


def build_markdown(
    dictamen_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    actions_df: pd.DataFrame,
    manifest: Dict[str, Any],
) -> str:
    lines = [
        "# Matriz de resolucion de bloqueos 16-19 gobernada 5809",
        "",
        f"Proceso: **{PROCESO}**",
        f"Subproyecto: **{SUBPROYECTO}**",
        f"Año proceso: **{ANIO_PROCESO}**",
        f"Año referencia datos: **{ANIO_REFERENCIA_DATOS}**",
        f"Declaración carga: **{DECLARACION_CARGA}**",
        "",
        "## Dictamen",
        "",
        markdown_table(dictamen_df),
        "",
        "## Validacion gobernanza",
        "",
        markdown_table(validation_df),
        "",
        "## Resumen bloqueos",
        "",
        markdown_table(summary_df),
        "",
        "## Propuesta de accion",
        "",
        markdown_table(actions_df),
        "",
        "## Alcance",
        "",
        "- No se modificaron fuentes originales.",
        "- No se genero SIES_READY.",
        "- No se recalcularon 20-21.",
        "- No se aplicaron correcciones automaticas.",
        "- Las columnas derivadas del paso 50 se usan solo para clasificacion y trazabilidad, no como regla oficial.",
        "",
        "## Archivos",
        "",
    ]
    for key, value in manifest.get("archivos", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def scan_sies_ready(output_dir: Path) -> List[str]:
    return [str(path) for path in output_dir.rglob("*SIES_READY*")]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = parser.parse_args()

    output_dir = BASE_53 / f"MATRIZ_RESOLUCION_BLOQUEOS_16_19_GOBERNADA_{args.timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    excel_path = output_dir / OUTPUT_FILES["excel"]
    md_path = output_dir / OUTPUT_FILES["informe"]
    manifest_path = output_dir / OUTPUT_FILES["manifest"]
    script_path = output_dir / OUTPUT_FILES["script"]
    current_script = Path(__file__).resolve()
    if current_script != script_path.resolve():
        shutil.copy2(current_script, script_path)

    input_paths = OrderedDict(
        [
            ("GOBERNANZA_51", GOBERNANZA_51),
            ("VALIDADOR_52_SCRIPT", VALIDADOR_52),
            ("RECALCULO_50", RECALCULO_50),
        ]
    )
    for path in input_paths.values():
        if not path.exists():
            raise FileNotFoundError(path)
    hashes_before = source_hashes(input_paths)

    validator_result = run_validator_52(output_dir, args.timestamp)
    validation_df = build_validation_sheet(validator_result)

    pending_df = read_sheet(RECALCULO_50, "06_PENDIENTES_16_19")
    classified_df = classify_pending(pending_df)
    summary_df = build_summary(classified_df)
    actions_df = build_actions(classified_df)
    no_auto_df = build_no_auto(classified_df)

    dif_19_df = classified_df[classified_df["DICTAMEN_DICCIONARIO_ESTADO"] == "DIFERENCIA_SOLO_APROBADAS_19"].copy()
    dif_multi_df = classified_df[classified_df["DICTAMEN_DICCIONARIO_ESTADO"] == "DIFERENCIA_16_18_O_MULTIPLE"].copy()
    sin_2025_df = classified_df[classified_df["DICTAMEN_DICCIONARIO_ESTADO"] == "SIN_REGISTROS_2025_PARA_CODCLI_LISTA"].copy()
    sin_codcli_df = classified_df[classified_df["DICTAMEN_DICCIONARIO_ESTADO"] == "BLOQUEO_SIN_CODCLI_LISTA"].copy()

    total = len(classified_df)
    dictamen_df = pd.DataFrame(
        [
            {
                "Proceso": PROCESO,
                "Subproyecto": SUBPROYECTO,
                "Anio proceso": ANIO_PROCESO,
                "Anio referencia datos": ANIO_REFERENCIA_DATOS,
                "Declaracion carga": DECLARACION_CARGA,
                "Total pendientes paso 50": total,
                "Diferencia solo aprobadas 19": len(dif_19_df),
                "Diferencia 16-18 o multiple": len(dif_multi_df),
                "Sin registros 2025 para CODCLI_LISTA": len(sin_2025_df),
                "Sin CODCLI_LISTA": len(sin_codcli_df),
                "Correcciones automaticas aplicadas": "NO",
                "Recalculo 20-21": "NO",
                "SIES_READY generado": "NO",
                "Estado validador hito 52": validator_result["estado_validador"],
                "Dictamen": "MATRIZ_CLASIFICACION_GENERADA_NO_LISTA_PARA_CARGA",
                "Proximo paso permitido": "Revisar propuestas funcionales/tecnicas; no aplicar correcciones automaticas.",
            }
        ]
    )

    output_placeholders = {
        "Excel": excel_path,
        "Informe": md_path,
        "Manifest": manifest_path,
        "Script": script_path,
    }
    hashes_after_pre = source_hashes(input_paths)
    fuentes_modificadas = "SI" if hashes_before != hashes_after_pre else "NO"

    manifest: Dict[str, Any] = {
        "proceso": PROCESO,
        "subproyecto": SUBPROYECTO,
        "timestamp": args.timestamp,
        "anio_proceso": ANIO_PROCESO,
        "anio_referencia_datos": ANIO_REFERENCIA_DATOS,
        "declaracion_carga": DECLARACION_CARGA,
        "fuentes_originales_modificadas": fuentes_modificadas,
        "correcciones_automaticas_aplicadas": "NO",
        "recalculo_20_21": "NO",
        "sies_ready_generado": "NO",
        "validator_52": validator_result,
        "conteos": {
            "total_pendientes": total,
            "dif_solo_aprobadas_19": len(dif_19_df),
            "dif_16_18_multiple": len(dif_multi_df),
            "sin_registros_2025": len(sin_2025_df),
            "sin_codcli_lista": len(sin_codcli_df),
            "resoluble_tecnico_post_validacion": int((classified_df["TIPO_RESOLUCION"] == "RESOLUBLE_TECNICO_POST_VALIDACION").sum()),
            "requiere_revision_funcional": int(classified_df["REQUIERE_REVISION_FUNCIONAL"].eq("SI").sum()),
            "no_resoluble_con_evidencia_actual": int(classified_df["NO_RESOLUBLE_CON_EVIDENCIA_ACTUAL"].eq("SI").sum()),
        },
        "hashes_inputs_antes": hashes_before,
        "hashes_inputs_despues_pre_outputs": hashes_after_pre,
        "archivos": {key: str(path) for key, path in output_placeholders.items()},
    }

    fuentes_df = build_sources(input_paths, hashes_before, hashes_after_pre, output_placeholders)
    dataframes = OrderedDict(
        [
            ("00_DICTAMEN", dictamen_df),
            ("01_VALIDACION_GOBERNANZA", validation_df),
            ("02_RESUMEN_BLOQUEOS", summary_df),
            ("03_DIF_SOLO_APROBADAS_19", dif_19_df),
            ("04_DIF_16_18_MULTIPLE", dif_multi_df),
            ("05_SIN_REGISTROS_2025", sin_2025_df),
            ("06_SIN_CODCLI_LISTA", sin_codcli_df),
            ("07_PROPUESTA_ACCION", actions_df),
            ("08_NO_RESOLVER_AUTOMATICO", no_auto_df),
            ("09_FUENTES", fuentes_df),
        ]
    )
    write_excel(excel_path, dataframes)

    md_text = build_markdown(dictamen_df, validation_df, summary_df, actions_df, manifest)
    md_path.write_text(md_text, encoding="utf-8")

    hashes_after = source_hashes(input_paths)
    fuentes_modificadas_final = "SI" if hashes_before != hashes_after else "NO"
    sies_ready = scan_sies_ready(output_dir)
    manifest["fuentes_originales_modificadas"] = fuentes_modificadas_final
    manifest["hashes_inputs_despues"] = hashes_after
    manifest["sies_ready_detectado"] = sies_ready
    manifest["hashes_salidas"] = {
        "Excel": sha256_file(excel_path),
        "Informe": sha256_file(md_path),
        "Script": sha256_file(script_path),
    }
    if sies_ready:
        manifest["sies_ready_generado"] = "SI"
        dictamen_df.loc[0, "SIES_READY generado"] = "SI"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("MATRIZ RESOLUCION BLOQUEOS 16-19 GOBERNADA 5809 — GENERADA")
    print(f"Fuentes originales modificadas: {fuentes_modificadas_final}")
    print(f"Declaración carga: {DECLARACION_CARGA}")
    print(f"Correcciones automáticas aplicadas: NO")
    print(f"Recalculo 20-21: NO")
    print()
    print("DICTAMEN")
    print(markdown_table(dictamen_df))
    print()
    print("RESUMEN BLOQUEOS")
    print(markdown_table(summary_df))
    print()
    print("ARCHIVOS")
    print(f"Excel: {excel_path}")
    print(f"Informe: {md_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Script: {script_path}")


if __name__ == "__main__":
    main()
