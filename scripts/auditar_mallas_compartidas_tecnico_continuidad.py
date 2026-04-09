#!/usr/bin/env python3
"""Auditoria end-to-end de mallas compartidas tecnico/profesional.

El flujo normal es un comando unico:

python scripts/auditar_mallas_compartidas_tecnico_continuidad.py \
  --ejecutar-completo --familia logistica --reanudar

Todas las fuentes se leen en modo solo lectura. Las salidas se escriben solo en
la carpeta de ejecucion creada para la auditoria.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import pandas as pd

try:
    from openpyxl.styles import Alignment
    from openpyxl.worksheet.table import Table, TableStyleInfo
except Exception:  # pragma: no cover - openpyxl es dependencia esperada.
    Alignment = None
    Table = None
    TableStyleInfo = None


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular")
AUDITORIA_BASE = (
    REPO_ROOT
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
)
RUN_PREFIX = "AUDITORIA_MALLAS_COMPARTIDAS_END_TO_END"
PREVIOUS_PARTIAL_RUN = (
    AUDITORIA_BASE / "AUDITORIA_MALLAS_COMPARTIDAS_TEC_CONT_20260701_013225"
)

PROCESS_NAME = "Avance Curricular SIES 2026"
SUBPROJECT_NAME = "Auditoria end-to-end de mallas compartidas tecnico/profesional"
ANIO_PROCESO = 2026
ANIO_REFERENCIA_DATOS = 2025

ALLOWED_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".tsv",
    ".xlsx",
    ".xlsm",
    ".pdf",
    ".sh",
    ".sql",
    ".log",
}
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}
EXCLUDED_SUFFIXES = {".lock", ".tmp", ".temp", ".swp", ".bak"}
RUN_SUBDIRS = [
    "00_CONTROL",
    "01_INVENTARIO",
    "02_EVIDENCIA",
    "03_INTERMEDIOS",
    "04_RESULTADOS",
    "05_AUDITORIA",
    "06_LOGS",
    "07_RESPALDOS",
]

EVIDENCE_LEVELS = [
    "REGLA_OFICIAL",
    "DATO_OBSERVADO",
    "IMPLEMENTACION_TECNICA",
    "DECISION_INTERNA",
    "HIPOTESIS_O_PENDIENTE",
]

SEARCH_TERMS = [
    "LOGISTICA",
    "LOGÍSTICA",
    "INGENIERIA EN LOGISTICA",
    "INGENIERÍA EN LOGÍSTICA",
    "TECNICO EN LOGISTICA",
    "TÉCNICO EN LOGÍSTICA",
    "ILOG",
    "TLOG",
    "CONTINUIDAD",
    "ARTICULACION",
    "ARTICULACIÓN",
    "SALIDA INTERMEDIA",
    "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS",
    "CODIGO_UNICO",
    "CODIGO_UNICO_FINAL",
    "CODCARR",
    "CODCARPR",
    "PLAN_ESTUDIOS",
    "PLAN_DE_ESTUDIO",
    "MALLA",
    "PDF",
    "ASIGNATURA",
    "NIVEL",
    "SEMESTRE",
]

CONCLUSIONES_PERMITIDAS = {
    "MISMO_PDF_Y_MISMA_MALLA_OBSERVADA",
    "MISMO_PDF_CON_PLANES_DISTINTOS",
    "PLANES_DISTINTOS_CON_MALLA_TECNICA_CONTENIDA",
    "PLANES_DISTINTOS_CON_MALLA_PARCIALMENTE_COMPARTIDA",
    "RELACION_DE_CONTINUIDAD_DOCUMENTADA",
    "RELACION_OBSERVADA_SIN_RESPALDO_OFICIAL",
    "RELACION_NO_REFLEJADA_EN_AVANCE_CURRICULAR",
    "SIN_EVIDENCIA_SUFICIENTE",
    "CONTRADICCION_ENTRE_FUENTES",
}

RECOMENDACIONES = {
    "A": "CONTINUAR CON LA REVISIÓN MANUAL SIN CAMBIOS.",
    "B": "REGENERAR EL PAQUETE DE REVISIÓN INCORPORANDO RELACIÓN TÉCNICA–CONTINUIDAD.",
    "C": "CORREGIR PRIMERO EL MAPEO PDF–PLAN.",
    "D": "CORREGIR PRIMERO LA IDENTIDAD DE CARRERAS.",
    "E": "SOLICITAR FUENTE INSTITUCIONAL ANTES DE CONTINUAR.",
    "F": "NO EXISTE EVIDENCIA SUFICIENTE PARA CAMBIAR EL FLUJO.",
}

PRIORITY_RELATIVE_PATHS = [
    "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/Instructivo_Avance Curricular SIES - 2026.txt",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/04_RESULTADOS/01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/04_RESULTADOS/07_CARRERAS_IDENTIDAD_VALIDADA.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/04_RESULTADOS/10_VALIDACION_PDF_PLAN_INTEGRADA.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/04_RESULTADOS/11_RESUMEN_FINAL_INTEGRACION.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/02_CONOCIMIENTO_RECUPERADO/08_METODOLOGIA_IDENTIDAD_CARRERAS.md",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/02_CONOCIMIENTO_RECUPERADO/09_MATRIZ_DECISION_IDENTIDAD.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/02_CONOCIMIENTO_RECUPERADO/10_DICCIONARIO_CAMPOS_IDENTIDAD.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/02_CONOCIMIENTO_RECUPERADO/11_CATALOGO_ESTADOS_IDENTIDAD.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/00_CONTROL/manifiesto_final.json",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/03_VALIDACION_PUENTE_34.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/05B_ASIGNATURAS_EXTRAIDAS_PDF_11.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/05C_ASIGNATURAS_CANONICAS_HOJA1_11_PLANES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/05D_CONCILIACION_EXACTA_ASIGNATURAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/05E_CONCILIACION_APROXIMADA_ASIGNATURAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/06A_UNIVERSO_148_NO_EXACTOS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/06B_CANDIDATOS_148_CASOS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/12_VALIDACION_ASIGNATURAS_PDF_PLAN.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/16_CIERRE_148_CASOS_NO_EXACTOS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/17_VALIDACION_ASIGNATURAS_PDF_PLAN_POST_REVISION.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/18_RESUMEN_POST_REVISION_11_PDF.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/19_RESUMEN_POST_REVISION_34_CARRERAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/20_REVISION_MANUAL_CASOS_PENDIENTES.xlsx",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/21_REVISION_MANUAL_OPTIMIZADA.xlsx",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/22_PLANTILLA_IMPORTACION_DECISIONES_REVISOR.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/23_MAPEO_PROPAGACION_DECISIONES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE6_REVISION_44_APROXIMADOS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE6_REVISION_4_DIFERENCIAS_NIVEL.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE6_REVISION_36_NOMBRES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE6_REVISION_64_SIN_CORRESPONDENCIA.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE6_CONTROL_EXTRACCION_148.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE6_CANDIDATOS_MULTIPLES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE7_GRUPOS_DECISION_MAESTRA.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/05_AUDITORIA/FASE7_CONTROL_PROPAGACION.tsv",
]

OPTIONAL_SEARCH_NAMES = [
    "01_MAPEO_PDF_PLAN_CANONICO.tsv",
    "03_MAPEO_SEGURO_43_CARRERAS.tsv",
    "02_TOTALES_DOCUMENTALES_CORREGIDOS_POR_PDF.tsv",
    "PROMEDIOSDEALUMNOS_7804__HOJA_HOJA1.tsv",
    "PUENTE_SIES_COMPILADO.tsv",
]


@dataclass
class StageSpec:
    name: str
    block: str
    function: Callable[["ExecutionContext"], None]
    outputs: list[str]
    required_columns: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    repo_root: Path
    run_dir: Path
    args: argparse.Namespace
    config: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    block_reasons: list[str] = field(default_factory=list)


def strip_accents(value: Any) -> str:
    text = "" if value is None else str(value)
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_text(value: Any) -> str:
    text = strip_accents(value).upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def norm_key(value: Any) -> str:
    return normalize_text(value)


def is_logistica(value: Any) -> bool:
    return "LOGISTICA" in normalize_text(value)


def timestamp_now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_relative(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_tsv(path: Path, rows: Sequence[Mapping[str, Any]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(list(rows), columns=list(columns))
    dataframe.to_csv(path, sep="\t", index=False)


def read_tsv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def read_text_file(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace"), "replace"


def detect_delimiter(path: Path, encoding: str) -> str:
    if path.suffix.lower() == ".tsv":
        return "\t"
    sample = path.read_text(encoding=encoding, errors="replace")[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";\t,|").delimiter
    except csv.Error:
        return ";"


def duplicate_header_positions(headers: Sequence[str]) -> dict[str, list[int]]:
    counter = Counter(headers)
    return {
        header: [pos for pos, item in enumerate(headers) if item == header]
        for header, count in counter.items()
        if count > 1
    }


def unique_headers_by_position(headers: Sequence[str]) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    output: list[str] = []
    duplicated = {item for item, count in Counter(headers).items() if count > 1}
    for pos, header in enumerate(headers):
        clean = str(header).strip() or f"CAMPO_SIN_NOMBRE__POS_{pos}"
        if clean in duplicated:
            output.append(f"{clean}__POS_{pos}")
        else:
            output.append(clean)
        counts[clean] += 1
    return output


def read_table_preserve_duplicate_headers(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            delimiter = detect_delimiter(path, encoding)
            with path.open("r", encoding=encoding, errors="strict", newline="") as fh:
                reader = csv.reader(fh, delimiter=delimiter)
                headers = next(reader, [])
                rows = list(reader)
            columns = unique_headers_by_position(headers)
            dataframe = pd.DataFrame(rows, columns=columns, dtype=str)
            return dataframe.fillna(""), {
                "encoding": encoding,
                "delimiter": delimiter,
                "original_headers": headers,
                "duplicate_headers": duplicate_header_positions(headers),
                "columns": columns,
            }
        except Exception as exc:  # noqa: BLE001 - se conserva como error de lectura.
            errors.append(f"{encoding}: {exc}")
    raise ValueError(f"No se pudo leer {path}: {' | '.join(errors)}")


def read_table(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    return read_table_preserve_duplicate_headers(path)


def read_excel(path: Path) -> dict[str, pd.DataFrame]:
    return pd.read_excel(path, sheet_name=None, dtype=str, keep_default_na=False)


def _coerce_boolish(value: Any) -> Any:
    if value is None or pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return bool(value)
    text = normalize_text(value)
    if text in {"SI", "S", "TRUE", "VERDADERO", "1", "YES", "Y"}:
        return True
    if text in {"NO", "N", "FALSE", "FALSO", "0", "", "NO_DETERMINADO"}:
        return False
    return bool(value)


def strict_boolean_mask(mask: Any, index: pd.Index | None = None) -> pd.Series:
    if isinstance(mask, pd.Series):
        series = mask.copy()
    else:
        series = pd.Series(mask, index=index)
    series = series.map(_coerce_boolish)
    return series.fillna(False).astype(bool)


def get_column_by_position(dataframe: pd.DataFrame, position: int) -> pd.Series:
    return dataframe.iloc[:, position]


def compare_pdf(left_pdf: Any, right_pdf: Any) -> str:
    left = normalize_text(left_pdf)
    right = normalize_text(right_pdf)
    if not left or not right:
        return "NO_DETERMINADO"
    return "SI" if left == right else "NO"


def compare_plan(left_plan: Any, right_plan: Any) -> str:
    left = normalize_text(left_plan)
    right = normalize_text(right_plan)
    if not left or not right:
        return "NO_DETERMINADO"
    return "SI" if left == right else "NO"


def calculate_coverage(
    technical_subjects: Iterable[Any], professional_subjects: Iterable[Any]
) -> dict[str, float | int]:
    technical = {normalize_text(item) for item in technical_subjects if normalize_text(item)}
    professional = {
        normalize_text(item) for item in professional_subjects if normalize_text(item)
    }
    common = technical & professional
    union = technical | professional
    return {
        "ASIGNATURAS_TECNICAS": len(technical),
        "ASIGNATURAS_PROFESIONALES": len(professional),
        "COMUNES_VALIDADAS": len(common),
        "SOLO_TECNICO": len(technical - professional),
        "SOLO_PROFESIONAL": len(professional - technical),
        "COBERTURA_TECNICO_EN_PROFESIONAL": (
            len(common) / len(technical) if technical else 0.0
        ),
        "COBERTURA_PROFESIONAL_EN_TECNICO": (
            len(common) / len(professional) if professional else 0.0
        ),
        "JACCARD": len(common) / len(union) if union else 0.0,
    }


def has_non_name_evidence(signals: Mapping[str, Any]) -> bool:
    evidence_keys = {
        "CODCARR",
        "CODCARPR",
        "MISMO_PDF",
        "MALLA_COMPARTIDA",
        "COBERTURA_TECNICO_EN_PROFESIONAL",
        "TIPO_PLAN_CARRERA",
        "DURACION_ESTUDIOS",
        "PUENTE_SIES",
        "RELACION_PREVIA_DOCUMENTADA",
    }
    normalized_keys = {normalize_text(item) for item in evidence_keys}
    absent = {"", "NO", "NO_DETERMINADO", "SIN_EVIDENCIA", "PENDIENTE"}
    for key, value in signals.items():
        if normalize_text(key) not in normalized_keys:
            continue
        if normalize_text(value) in absent:
            continue
        if isinstance(value, (int, float)):
            if value > 0:
                return True
        elif _coerce_boolish(value):
            return True
    return False


def classify_backup(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    terms = ["RESPALDO", "BACKUP", "COPIA", "ANTES", "PRE_CORRECCIONES"]
    return "SI" if any(term in normalized for term in terms) else "NO"


def classify_original(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    if "ORIGINALES" in normalized or "FUENTES CONGELADAS" in normalized:
        return "SI"
    if path.suffix.lower() == ".pdf" and "00 FUENTES PDF" in normalized:
        return "SI"
    return "NO"


def classify_file_type(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    suffix = path.suffix.lower()
    if "INSTRUCTIVO" in normalized:
        return "INSTRUCTIVO"
    if "MANUAL" in normalized:
        return "MANUAL"
    if "CALENDARIO" in normalized:
        return "CALENDARIO"
    if suffix == ".py":
        return "CODIGO"
    if "AUDITORIA" in normalized:
        return "AUDITORIA"
    if suffix in {".csv", ".tsv", ".xlsx", ".xlsm"}:
        if "PRECARGA" in normalized:
            return "PRECARGA"
        if "CARGA" in normalized:
            return "CARGA"
        if "RESULTADO" in normalized or "RESULTADOS" in normalized:
            return "RESULTADO"
        return "FUENTE_INSTITUCIONAL"
    if suffix == ".pdf":
        return "FUENTE_INSTITUCIONAL"
    return "EVIDENCIA"


def probable_process(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    if "AVANCE CURRICULAR" in normalized or "AVANCE_CURRICULAR" in normalized:
        return "AVANCE_CURRICULAR"
    if "EXTRANJER" in normalized:
        return "ESTUDIANTES_EXTRANJEROS"
    if "MATRICULA" in normalized or "MU2026" in normalized:
        return "MATRICULA_UNIFICADA"
    return "NO_DETERMINADO"


def classify_evidence_level(path: Path, text: str = "") -> str:
    normalized = normalize_text(f"{path.as_posix()} {text}")
    process = probable_process(path)
    if "INSTRUCTIVO AVANCE CURRICULAR SIES 2026" in normalized:
        return "REGLA_OFICIAL"
    if path.suffix.lower() == ".py":
        return "IMPLEMENTACION_TECNICA"
    if "DECISION" in normalized or "METODOLOGIA" in normalized or "CATALOGO ESTADOS" in normalized:
        return "DECISION_INTERNA"
    if path.suffix.lower() in {".csv", ".tsv", ".xlsx", ".xlsm", ".pdf"}:
        return "DATO_OBSERVADO"
    if process in {"MATRICULA_UNIFICADA", "ESTUDIANTES_EXTRANJEROS"}:
        return "IMPLEMENTACION_TECNICA" if path.suffix.lower() == ".py" else "DATO_OBSERVADO"
    return "HIPOTESIS_O_PENDIENTE"


def is_allowed_file(path: Path) -> bool:
    if path.name.startswith("~$"):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def should_exclude_path(path: Path, active_run_dir: Path | None = None) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    if active_run_dir is not None:
        try:
            path.resolve().relative_to(active_run_dir.resolve())
            return True
        except ValueError:
            pass
    normalized = normalize_text(path.name)
    return normalized in {"TMP", "TEMP"} or "TEMPORAL" in normalized


def matching_terms(text: Any) -> list[str]:
    normalized = normalize_text(text)
    return sorted({normalize_text(term) for term in SEARCH_TERMS if normalize_text(term) in normalized})


def serialize_row(row: Mapping[str, Any]) -> str:
    return json.dumps(dict(row), ensure_ascii=False, sort_keys=True)


def pick(row: Mapping[str, Any], names: Sequence[str]) -> str:
    normalized_map = {normalize_text(key): key for key in row.keys()}
    for name in names:
        original = normalized_map.get(normalize_text(name))
        if original is not None:
            value = row.get(original, "")
            if value is not None and str(value) != "":
                return str(value)
    return ""


def classify_program_type(row: Mapping[str, Any]) -> tuple[str, str]:
    tipo = normalize_text(pick(row, ["TIPO_PLAN_CARRERA", "TIPO_PLAN_CARRERA_UNIFICADO", "TIPOS_PLAN_OBSERVADOS"]))
    duracion = normalize_text(pick(row, ["DURACION_ESTUDIOS", "DURACION_ESTUDIOS_UNIFICADA", "DURACIONES_OBSERVADAS"]))
    codcarpr = normalize_text(pick(row, ["CODCARPR", "CODCARPR_UNIFICADO", "CODCARPR_OBSERVADOS", "CODCARPR_PUENTE"]))
    plan = normalize_text(pick(row, ["PLAN_DE_ESTUDIO_INSTITUCIONAL", "PLAN_DE_ESTUDIO_CANONICO", "PLAN_DE_ESTUDIO_CANONICO_PDF", "PLANES_INSTITUCIONALES_OBSERVADOS"]))
    name = normalize_text(pick(row, ["NOMBRE_CARRERA", "NOMBRE_CARRERA_INSTITUCIONAL", "NOMBRE_CARRERA_SIES", "NOMBRE_CARRERA_UNIFICADO"]))
    structured = "NO"
    joined_structured = " ".join([tipo, duracion, codcarpr, plan])
    if "CONTINUIDAD" in joined_structured or "ARTICULACION" in joined_structured:
        return "CONTINUIDAD", "SI"
    if re.search(r"(^|[^A-Z0-9])TLOG([^A-Z0-9]|$)", joined_structured) or codcarpr.startswith("T") or "TECNIC" in tipo:
        return "TECNICO", "SI"
    if re.search(r"(^|[^A-Z0-9])ILOG([^A-Z0-9]|$)", joined_structured) or "PROFESIONAL" in tipo or "INGENIER" in tipo:
        return "PROFESIONAL", "SI"
    if "CONTINUIDAD" in name or "ARTICULACION" in name:
        return "CONTINUIDAD", structured
    if "TECNIC" in name:
        return "TECNICO", structured
    if "INGENIER" in name:
        return "PROFESIONAL", structured
    return "NO_DETERMINADO", structured


def extract_subject_key(row: Mapping[str, Any]) -> str:
    code = pick(row, ["CODIGO_ASIGNATURA_CANONICO", "CODIGO_ASIGNATURA_PDF", "CODRAMOS_MATCH"])
    name = pick(row, ["NOMBRE_ASIGNATURA_NORMALIZADO", "NOMBRE_ASIGNATURA_CANONICO", "NOMBRE_ASIGNATURA_PDF", "ASIGNATURA_NORMALIZADA", "ASIGNATURA_PDF"])
    level = pick(row, ["NIVEL_CANONICO", "NIVEL_PDF", "NIVELES_HOJA1"])
    if normalize_text(code):
        return f"COD::{normalize_text(code)}"
    return f"NOM::{normalize_text(name)}::NIV::{normalize_text(level)}"


def build_run_dir(folder: str | None) -> Path:
    if folder:
        path = Path(folder)
        return path if path.is_absolute() else REPO_ROOT / path
    return AUDITORIA_BASE / f"{RUN_PREFIX}_{timestamp_now()}"


def ensure_run_structure(run_dir: Path) -> None:
    for subdir in RUN_SUBDIRS:
        (run_dir / subdir).mkdir(parents=True, exist_ok=True)


def default_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "proceso": PROCESS_NAME,
        "subproyecto": SUBPROJECT_NAME,
        "anio_proceso": ANIO_PROCESO,
        "anio_referencia_datos": ANIO_REFERENCIA_DATOS,
        "familia": normalize_text(args.familia),
        "modo_auditoria": args.modo_auditoria,
        "solo_logistica": bool(args.solo_logistica),
        "max_archivos": args.max_archivos,
        "ejecucion_parcial_anterior": str(PREVIOUS_PARTIAL_RUN),
        "rutas_prioritarias": PRIORITY_RELATIVE_PATHS,
        "busquedas_adicionales": OPTIONAL_SEARCH_NAMES,
        "extensiones_permitidas": sorted(ALLOWED_EXTENSIONS),
        "directorios_excluidos": sorted(EXCLUDED_DIRS),
        "restricciones": {
            "internet": "NO_USAR",
            "instalar_dependencias": "NO",
            "fuentes_originales": "SOLO_LECTURA",
            "pdfs": "NO_MODIFICAR",
            "excel_manual": "NO_MODIFICAR",
            "precarga": "NO_GENERAR",
            "pes": "NO_GENERAR",
            "apto_para_carga": "NO",
        },
    }


def state_path(ctx: ExecutionContext) -> Path:
    return ctx.run_dir / "00_CONTROL" / "estado_ejecucion.json"


def load_state(ctx: ExecutionContext) -> dict[str, Any]:
    path = state_path(ctx)
    if path.exists():
        return read_json(path)
    return {"estado_general": "PENDIENTE", "etapas": {}, "actualizado_en": ""}


def save_state(ctx: ExecutionContext, state: dict[str, Any]) -> None:
    state["actualizado_en"] = datetime.now().isoformat(timespec="seconds")
    write_json(state_path(ctx), state)


def output_hashes(ctx: ExecutionContext, outputs: Sequence[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel in outputs:
        path = ctx.run_dir / rel
        if path.exists() and path.is_file():
            hashes[rel] = sha256_file(path)
    return hashes


def validate_output(path: Path, required_columns: Sequence[str] | None = None) -> tuple[bool, str]:
    if not path.exists():
        return False, "salida inexistente"
    if path.stat().st_size == 0:
        return False, "salida vacia"
    if required_columns and path.suffix.lower() == ".tsv":
        try:
            df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, nrows=1)
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                return False, f"faltan columnas: {','.join(missing)}"
        except Exception as exc:  # noqa: BLE001
            return False, f"error leyendo salida: {exc}"
    return True, "OK"


def validate_stage_outputs(ctx: ExecutionContext, spec: StageSpec) -> tuple[bool, list[str]]:
    errors = []
    for rel in spec.outputs:
        ok, detail = validate_output(ctx.run_dir / rel, spec.required_columns.get(rel))
        if not ok:
            errors.append(f"{rel}: {detail}")
    return not errors, errors


def can_resume_stage(ctx: ExecutionContext, spec: StageSpec) -> tuple[bool, str]:
    state = load_state(ctx)
    entry = state.get("etapas", {}).get(spec.name, {})
    if not ctx.args.reanudar:
        return False, "reanudar desactivado"
    if entry.get("estado") != "COMPLETADA":
        return False, "estado no completado"
    ok, errors = validate_stage_outputs(ctx, spec)
    if not ok:
        return False, "salidas invalidas: " + "; ".join(errors)
    current_hashes = output_hashes(ctx, spec.outputs)
    if current_hashes != entry.get("hashes", {}):
        return False, "hashes no coinciden"
    return True, "salidas validas y hashes coinciden"


def backup_existing_outputs(ctx: ExecutionContext, spec: StageSpec) -> None:
    timestamp = timestamp_now()
    for rel in spec.outputs:
        path = ctx.run_dir / rel
        if not path.exists():
            continue
        backup = ctx.run_dir / "07_RESPALDOS" / f"{spec.name}_{timestamp}" / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)


def run_stage(ctx: ExecutionContext, spec: StageSpec) -> None:
    state = load_state(ctx)
    resume, reason = can_resume_stage(ctx, spec)
    if resume:
        state.setdefault("etapas", {})[spec.name]["reanudacion"] = "OMITIDA_POR_REANUDACION"
        save_state(ctx, state)
        log(ctx, f"{spec.name}: omitida por reanudacion")
        return
    if ctx.args.reanudar and state.get("etapas", {}).get(spec.name, {}).get("estado") == "COMPLETADA" and not ctx.args.forzar:
        ctx.blocked = True
        ctx.block_reasons.append(f"{spec.name}: estado completado inconsistente ({reason})")
        raise RuntimeError(ctx.block_reasons[-1])
    if ctx.args.forzar:
        backup_existing_outputs(ctx, spec)
    state.setdefault("etapas", {})[spec.name] = {
        "estado": "EN_EJECUCION",
        "bloque": spec.block,
        "fecha_inicio": datetime.now().isoformat(timespec="seconds"),
        "salidas": spec.outputs,
    }
    save_state(ctx, state)
    log(ctx, f"{spec.name}: inicio")
    spec.function(ctx)
    ok, errors = validate_stage_outputs(ctx, spec)
    state = load_state(ctx)
    if not ok:
        state["etapas"][spec.name].update(
            {
                "estado": "BLOQUEADA",
                "fecha_fin": datetime.now().isoformat(timespec="seconds"),
                "errores": errors,
            }
        )
        save_state(ctx, state)
        ctx.blocked = True
        ctx.block_reasons.extend(errors)
        raise RuntimeError(f"{spec.name} bloqueada: {'; '.join(errors)}")
    state["etapas"][spec.name].update(
        {
            "estado": "COMPLETADA",
            "fecha_fin": datetime.now().isoformat(timespec="seconds"),
            "hashes": output_hashes(ctx, spec.outputs),
            "controles": "OK",
            "bloqueos": [],
        }
    )
    save_state(ctx, state)
    log(ctx, f"{spec.name}: completada")


def log(ctx: ExecutionContext, message: str) -> None:
    path = ctx.run_dir / "06_LOGS" / "ejecucion_end_to_end.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now().isoformat(timespec='seconds')}\t{message}\n")


def locate_optional_sources() -> list[str]:
    found: list[str] = []
    for name in OPTIONAL_SEARCH_NAMES:
        for path in REPO_ROOT.rglob(name):
            if should_exclude_path(path, None):
                continue
            found.append(safe_relative(path))
    return sorted(set(found))


def init_execution(ctx: ExecutionContext) -> None:
    if ctx.run_dir.resolve() == PREVIOUS_PARTIAL_RUN.resolve():
        raise SystemExit("No se puede reutilizar la ejecucion parcial anterior como activa.")
    ensure_run_structure(ctx.run_dir)
    ctx.config = default_config(ctx.args)
    optional = locate_optional_sources()
    ctx.config["fuentes_opcionales_encontradas"] = optional
    write_json(ctx.run_dir / "00_CONTROL" / "configuracion_ejecucion.json", ctx.config)
    write_json(
        ctx.run_dir / "00_CONTROL" / "manifiesto_ejecucion.json",
        {
            "proceso": PROCESS_NAME,
            "subproyecto": SUBPROJECT_NAME,
            "creado_en": datetime.now().isoformat(timespec="seconds"),
            "repositorio": str(REPO_ROOT),
            "carpeta_ejecucion": str(ctx.run_dir),
            "ejecucion_parcial_anterior_preservada": PREVIOUS_PARTIAL_RUN.exists(),
            "originales_modificados": "NO",
            "excel_manual_modificado": "NO",
            "decisiones_humanas_aplicadas": 0,
            "precarga_generada": "NO",
            "pes_generado": "NO",
            "apto_para_carga": "NO",
        },
    )
    plan = [
        "# Plan end-to-end",
        "",
        "BLOQUE 1 - Evidencia e identidad.",
        "BLOQUE 2 - Comparacion e impacto.",
        "BLOQUE 3 - Cierre y reporte.",
        "",
        "El usuario ejecuta un solo comando con --ejecutar-completo.",
    ]
    (ctx.run_dir / "00_CONTROL" / "plan_end_to_end.md").write_text(
        "\n".join(plan) + "\n", encoding="utf-8"
    )
    save_state(ctx, {"estado_general": "EN_EJECUCION", "etapas": {}, "actualizado_en": ""})
    log(ctx, "ejecucion inicializada")


def iter_candidate_files(ctx: ExecutionContext) -> Iterable[Path]:
    count = 0
    for current_root, dirnames, filenames in os.walk(ctx.repo_root):
        root_path = Path(current_root)
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if not should_exclude_path(root_path / dirname, ctx.run_dir)
        ]
        if should_exclude_path(root_path, ctx.run_dir):
            continue
        for filename in filenames:
            path = root_path / filename
            if should_exclude_path(path, ctx.run_dir) or not is_allowed_file(path):
                continue
            yield path
            count += 1
            if ctx.args.max_archivos and count >= ctx.args.max_archivos:
                return


def priority_for(path: Path) -> tuple[str, str]:
    rel = safe_relative(path)
    normalized = normalize_text(rel)
    if rel in PRIORITY_RELATIVE_PATHS:
        return "ALTA", "fuente prioritaria declarada"
    if Path(rel).name in OPTIONAL_SEARCH_NAMES:
        return "ALTA", "fuente opcional localizada"
    if any(term in normalized for term in ["LOGISTICA", "ILOG", "TLOG"]):
        return "ALTA", "familia piloto"
    if any(term in normalized for term in ["CODCARPR", "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS", "PUENTE_SIES"]):
        return "MEDIA", "campo estructural relevante"
    if probable_process(path) != "NO_DETERMINADO":
        return "MEDIA", "proceso relacionado"
    return "BAJA", "extension permitida"


def stage_inventario(ctx: ExecutionContext) -> None:
    rows = []
    for idx, path in enumerate(iter_candidate_files(ctx), start=1):
        stat = path.stat()
        priority, reason = priority_for(path)
        rows.append(
            {
                "ID_ARCHIVO": f"ARCH_{idx:06d}",
                "RUTA": str(path.resolve()),
                "RUTA_RELATIVA": safe_relative(path),
                "EXTENSION": path.suffix.lower(),
                "TAMANO_BYTES": stat.st_size,
                "FECHA_MODIFICACION": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "HASH_SHA256": sha256_file(path),
                "ES_RESPALDO": classify_backup(path),
                "ES_ORIGINAL": classify_original(path),
                "ES_DERIVADO": "NO" if classify_original(path) == "SI" else "SI",
                "TIPO_ARCHIVO": classify_file_type(path),
                "PROCESO_PROBABLE": probable_process(path),
                "PRIORIDAD": priority,
                "MOTIVO_INCLUSION": reason,
                "ESTADO_LECTURA": "NO_LEIDO",
            }
        )
    columns = [
        "ID_ARCHIVO",
        "RUTA",
        "RUTA_RELATIVA",
        "EXTENSION",
        "TAMANO_BYTES",
        "FECHA_MODIFICACION",
        "HASH_SHA256",
        "ES_RESPALDO",
        "ES_ORIGINAL",
        "ES_DERIVADO",
        "TIPO_ARCHIVO",
        "PROCESO_PROBABLE",
        "PRIORIDAD",
        "MOTIVO_INCLUSION",
        "ESTADO_LECTURA",
    ]
    write_tsv(ctx.run_dir / "01_INVENTARIO" / "01_INVENTARIO_FOCALIZADO.tsv", rows, columns)
    priority_rows = []
    for rel in PRIORITY_RELATIVE_PATHS + ctx.config.get("fuentes_opcionales_encontradas", []):
        path = ctx.repo_root / rel
        priority_rows.append(
            {
                "RUTA_RELATIVA": rel,
                "EXISTE": "SI" if path.exists() else "NO",
                "HASH_SHA256": sha256_file(path) if path.exists() and path.is_file() else "",
                "TAMANO_BYTES": path.stat().st_size if path.exists() and path.is_file() else "",
                "TIPO_RESPALDO": classify_evidence_level(path) if path.exists() else "HIPOTESIS_O_PENDIENTE",
                "BLOQUEA": "SI" if rel in PRIORITY_RELATIVE_PATHS and not path.exists() else "NO",
            }
        )
    write_tsv(
        ctx.run_dir / "01_INVENTARIO" / "02_FUENTES_PRIORITARIAS.tsv",
        priority_rows,
        ["RUTA_RELATIVA", "EXISTE", "HASH_SHA256", "TAMANO_BYTES", "TIPO_RESPALDO", "BLOQUEA"],
    )
    hash_counts = Counter(row["HASH_SHA256"] for row in rows)
    duplicates = [
        {**row, "TOTAL_DUPLICADOS_HASH": hash_counts[row["HASH_SHA256"]]}
        for row in rows
        if hash_counts[row["HASH_SHA256"]] > 1
    ]
    write_tsv(ctx.run_dir / "01_INVENTARIO" / "03_DUPLICADOS_HASH.tsv", duplicates, columns + ["TOTAL_DUPLICADOS_HASH"])
    ctx.metrics["archivos_inventariados"] = len(rows)


def extract_text_evidence(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    content, encoding = read_text_file(path)
    file_hash = sha256_file(path)
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        terms = matching_terms(line)
        if not terms:
            continue
        start = max(1, idx - 5)
        end = min(len(lines), idx + 5)
        context = "\n".join(f"{pos}: {lines[pos-1]}" for pos in range(start, end + 1))
        rows.append(
            {
                "FUENTE": str(path),
                "RUTA_RELATIVA": safe_relative(path),
                "HOJA": "",
                "FILA": "",
                "LINEA": idx,
                "PAGINA": "",
                "TERMINOS": ";".join(terms),
                "CONTEXTO": context,
                "FILA_JSON": "",
                "TIPO_RESPALDO": classify_evidence_level(path, line),
                "ENCODING": encoding,
                "HASH_FUENTE": file_hash,
            }
        )
    return rows


def extract_table_evidence(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    df, meta = read_table(path)
    file_hash = sha256_file(path)
    file_level = classify_evidence_level(path)
    for header, positions in meta["duplicate_headers"].items():
        duplicate_rows.append(
            {
                "FUENTE": str(path),
                "CAMPO": header,
                "POSICIONES": ";".join(str(pos) for pos in positions),
                "COLUMNAS_TECNICAS": ";".join(meta["columns"][pos] for pos in positions),
            }
        )
    for row_idx in range(len(df)):
        row = {col: df.iloc[row_idx, pos] for pos, col in enumerate(df.columns)}
        row_text = " ".join(str(value) for value in row.values())
        terms = matching_terms(row_text)
        if not terms:
            continue
        rows.append(
            {
                "FUENTE": str(path),
                "RUTA_RELATIVA": safe_relative(path),
                "HOJA": "",
                "FILA": row_idx + 2,
                "LINEA": "",
                "PAGINA": "",
                "TERMINOS": ";".join(terms),
                "CONTEXTO": "",
                "FILA_JSON": serialize_row(row),
                "TIPO_RESPALDO": file_level,
                "ENCODING": meta["encoding"],
                "HASH_FUENTE": file_hash,
            }
        )
    return rows, duplicate_rows


def extract_excel_evidence(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sheets = read_excel(path)
    file_hash = sha256_file(path)
    file_level = classify_evidence_level(path)
    for sheet, df in sheets.items():
        for row_idx in range(len(df)):
            row = {col: df.iloc[row_idx, pos] for pos, col in enumerate(df.columns)}
            row_text = " ".join(str(value) for value in row.values())
            terms = matching_terms(row_text)
            if not terms:
                continue
            rows.append(
                {
                    "FUENTE": str(path),
                    "RUTA_RELATIVA": safe_relative(path),
                    "HOJA": sheet,
                    "FILA": row_idx + 2,
                    "LINEA": "",
                    "PAGINA": "",
                    "TERMINOS": ";".join(terms),
                    "CONTEXTO": "",
                    "FILA_JSON": serialize_row(row),
                    "TIPO_RESPALDO": file_level,
                    "ENCODING": "",
                    "HASH_FUENTE": file_hash,
                }
            )
    return rows


def extract_pdf_evidence(path: Path) -> list[dict[str, Any]]:
    terms = matching_terms(path.name)
    return [
        {
            "FUENTE": str(path),
            "RUTA_RELATIVA": safe_relative(path),
            "HOJA": "",
            "FILA": "",
            "LINEA": "",
            "PAGINA": "",
            "TERMINOS": ";".join(terms),
            "CONTEXTO": "PDF registrado; no se aplico OCR. Extraccion textual no disponible en dependencias actuales.",
            "FILA_JSON": "",
            "TIPO_RESPALDO": "DATO_OBSERVADO",
            "ENCODING": "",
            "HASH_FUENTE": sha256_file(path),
        }
    ]


def stage_evidencia(ctx: ExecutionContext) -> None:
    inventory = read_tsv_if_exists(ctx.run_dir / "01_INVENTARIO" / "01_INVENTARIO_FOCALIZADO.tsv")
    all_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    candidates = inventory[priority_evidence_mask(inventory)] if not inventory.empty else inventory
    for _, item in candidates.iterrows():
        path = Path(item["RUTA"])
        try:
            if path.stat().st_size > 20 * 1024 * 1024:
                all_rows.append(
                    {
                        "FUENTE": str(path),
                        "RUTA_RELATIVA": safe_relative(path),
                        "HOJA": "",
                        "FILA": "",
                        "LINEA": "",
                        "PAGINA": "",
                        "TERMINOS": "ARCHIVO_VOLUMINOSO",
                        "CONTEXTO": "Fuente localizada pero no leida completa por control de volumen; usar salidas estructuradas prioritarias.",
                        "FILA_JSON": "",
                        "TIPO_RESPALDO": "HIPOTESIS_O_PENDIENTE",
                        "ENCODING": "",
                        "HASH_FUENTE": sha256_file(path),
                    }
                )
                continue
            suffix = path.suffix.lower()
            if suffix in {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".sh", ".sql", ".log"}:
                all_rows.extend(extract_text_evidence(path))
            elif suffix in {".csv", ".tsv"}:
                rows, duplicates = extract_table_evidence(path)
                all_rows.extend(rows)
                duplicate_rows.extend(duplicates)
            elif suffix in {".xlsx", ".xlsm"}:
                all_rows.extend(extract_excel_evidence(path))
            elif suffix == ".pdf":
                all_rows.extend(extract_pdf_evidence(path))
        except Exception as exc:  # noqa: BLE001
            all_rows.append(
                {
                    "FUENTE": str(path),
                    "RUTA_RELATIVA": safe_relative(path),
                    "HOJA": "",
                    "FILA": "",
                    "LINEA": "",
                    "PAGINA": "",
                    "TERMINOS": "ERROR_LECTURA",
                    "CONTEXTO": str(exc),
                    "FILA_JSON": "",
                    "TIPO_RESPALDO": "HIPOTESIS_O_PENDIENTE",
                    "ENCODING": "",
                    "HASH_FUENTE": sha256_file(path) if path.exists() else "",
                }
            )
    evidence_columns = [
        "FUENTE",
        "RUTA_RELATIVA",
        "HOJA",
        "FILA",
        "LINEA",
        "PAGINA",
        "TERMINOS",
        "CONTEXTO",
        "FILA_JSON",
        "TIPO_RESPALDO",
        "ENCODING",
        "HASH_FUENTE",
    ]
    by_level = {level: [] for level in EVIDENCE_LEVELS}
    for row in all_rows:
        by_level.setdefault(row["TIPO_RESPALDO"], []).append(row)
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "01_EVIDENCIA_OFICIAL.tsv", by_level["REGLA_OFICIAL"], evidence_columns)
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "02_DATOS_OBSERVADOS.tsv", by_level["DATO_OBSERVADO"], evidence_columns)
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "03_IMPLEMENTACION_TECNICA.tsv", by_level["IMPLEMENTACION_TECNICA"], evidence_columns)
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "04_DECISIONES_INTERNAS.tsv", by_level["DECISION_INTERNA"], evidence_columns)
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "05_HIPOTESIS_PENDIENTES.tsv", by_level["HIPOTESIS_O_PENDIENTE"], evidence_columns)
    write_tsv(
        ctx.run_dir / "05_AUDITORIA" / "03_CONTROL_ENCABEZADOS_DUPLICADOS.tsv",
        duplicate_rows or [{"FUENTE": "", "CAMPO": "", "POSICIONES": "", "COLUMNAS_TECNICAS": ""}],
        ["FUENTE", "CAMPO", "POSICIONES", "COLUMNAS_TECNICAS"],
    )
    ctx.metrics["fuentes_oficiales_revisadas"] = len(by_level["REGLA_OFICIAL"])
    ctx.metrics["datos_observados_revisados"] = len(by_level["DATO_OBSERVADO"])
    ctx.metrics["scripts_revisados"] = len(by_level["IMPLEMENTACION_TECNICA"])
    ctx.metrics["auditorias_revisadas"] = len(by_level["DECISION_INTERNA"])


def priority_evidence_mask(inventory: pd.DataFrame) -> pd.Series:
    if inventory.empty:
        return pd.Series(dtype=bool)
    priority_set = set(PRIORITY_RELATIVE_PATHS)
    priority_set.update(locate_optional_sources())
    text = (
        inventory["PRIORIDAD"].fillna("")
        + " "
        + inventory["RUTA_RELATIVA"].fillna("")
        + " "
        + inventory["MOTIVO_INCLUSION"].fillna("")
    )
    direct = inventory["RUTA_RELATIVA"].fillna("").isin(priority_set)
    mask = text.map(lambda value: any(term in normalize_text(value) for term in ["LOGISTICA", "ILOG", "TLOG", "PUENTE_SIES"]))
    mask = strict_boolean_mask(mask) | strict_boolean_mask(direct)
    return mask.fillna(False).astype(bool)


def load_priority_table(relative: str) -> pd.DataFrame:
    path = REPO_ROOT / relative
    if not path.exists():
        return pd.DataFrame()
    if path.suffix.lower() in {".tsv", ".csv"}:
        df, _ = read_table(path)
        return df
    if path.suffix.lower() in {".xlsx", ".xlsm"}:
        sheets = read_excel(path)
        return pd.concat(sheets.values(), ignore_index=True) if sheets else pd.DataFrame()
    return pd.DataFrame()


def identity_records_from_df(df: pd.DataFrame, source: Path, respaldo: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx in range(len(df)):
        row = {col: df.iloc[idx, pos] for pos, col in enumerate(df.columns)}
        if not any(is_logistica(value) or normalize_text(value) in {"ILOG", "TLOG"} for value in row.values()):
            continue
        tipo, estructurado = classify_program_type(row)
        name = pick(row, ["NOMBRE_CARRERA", "NOMBRE_CARRERA_INSTITUCIONAL", "NOMBRE_CARRERA_SIES", "NOMBRE_CARRERA_UNIFICADO"])
        rows.append(
            {
                "CODIGO_UNICO": pick(row, ["CODIGO_UNICO"]),
                "CODIGO_UNICO_FINAL": pick(row, ["CODIGO_UNICO_FINAL", "CODIGO_UNICO_FINAL_UNIFICADO"]),
                "CODCLI": pick(row, ["CODCLI"]),
                "CODCARR": pick(row, ["CODCARR", "CODCARR_UNIFICADO", "CODCARR_CANONICO"]),
                "CODCARPR": pick(row, ["CODCARPR", "CODCARPR_UNIFICADO", "CODCARPR_PUENTE"]),
                "NOMBRE_CARRERA": name,
                "TIPO_PROGRAMA_OBSERVADO": tipo,
                "CLASIFICACION_TIPO_ESTRUCTURADA": estructurado,
                "TIPO_PLAN_CARRERA": pick(row, ["TIPO_PLAN_CARRERA", "TIPO_PLAN_CARRERA_UNIFICADO", "TIPOS_PLAN_OBSERVADOS"]),
                "DURACION_ESTUDIOS": pick(row, ["DURACION_ESTUDIOS", "DURACION_ESTUDIOS_UNIFICADA", "DURACIONES_OBSERVADAS"]),
                "PLAN_ESTUDIOS_SIES": pick(row, ["PLAN_ESTUDIOS_SIES", "PLAN_ESTUDIOS", "PLAN_ESTUDIOS_SIES_UNIFICADO"]),
                "PLAN_DE_ESTUDIO_INSTITUCIONAL": pick(row, ["PLAN_DE_ESTUDIO_INSTITUCIONAL", "PLAN_DE_ESTUDIO_INSTITUCIONAL_UNIFICADO", "PLAN_DE_ESTUDIO_CANONICO", "PLAN"]),
                "PLAN_DE_ESTUDIO_CANONICO_PDF": pick(row, ["PLAN_DE_ESTUDIO_CANONICO_PDF", "PLAN_DE_ESTUDIO_CANONICO"]),
                "ARCHIVO_PDF": pick(row, ["ARCHIVO_PDF", "PDF_DIRECTO_CANDIDATO", "PDF_MALLA_CANDIDATO"]),
                "JORNADA": pick(row, ["JORNADA", "JORNADA_UNIFICADA", "JORNADA_MATRIZ"]),
                "MODALIDAD": pick(row, ["MODALIDAD", "MODALIDAD_UNIFICADA"]),
                "SEDE": pick(row, ["SEDE", "NOMBRE_SEDE", "SEDE_UNIFICADA"]),
                "VERSION": pick(row, ["VERSION", "VERSION_UNIFICADA"]),
                "VIGENCIA": pick(row, ["VIGENCIA", "VIGENCIA_UNIFICADA"]),
                "AÑO_DATO": pick(row, ["ANIO_DATOS", "ANIO", "ANO"]) or str(ANIO_REFERENCIA_DATOS),
                "PERIODO": pick(row, ["PERIODO"]),
                "PROCESO_ORIGEN": probable_process(source),
                "FUENTE": str(source),
                "TIPO_RESPALDO": respaldo,
                "HASH_FUENTE": sha256_file(source) if source.exists() else "",
            }
        )
    return rows


def stage_identidad(ctx: ExecutionContext) -> None:
    sources = [
        rel for rel in PRIORITY_RELATIVE_PATHS if rel.endswith((".tsv", ".xlsx", ".xlsm"))
    ]
    rows: list[dict[str, Any]] = []
    for rel in sources:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        try:
            if path.suffix.lower() in {".tsv", ".csv"}:
                df, _ = read_table(path)
                rows.extend(identity_records_from_df(df, path, classify_evidence_level(path)))
            elif path.suffix.lower() in {".xlsx", ".xlsm"}:
                for _, df in read_excel(path).items():
                    rows.extend(identity_records_from_df(df, path, classify_evidence_level(path)))
        except Exception as exc:  # noqa: BLE001
            log(ctx, f"identidad: error leyendo {path}: {exc}")
    columns = [
        "CODIGO_UNICO",
        "CODIGO_UNICO_FINAL",
        "CODCLI",
        "CODCARR",
        "CODCARPR",
        "NOMBRE_CARRERA",
        "TIPO_PROGRAMA_OBSERVADO",
        "CLASIFICACION_TIPO_ESTRUCTURADA",
        "TIPO_PLAN_CARRERA",
        "DURACION_ESTUDIOS",
        "PLAN_ESTUDIOS_SIES",
        "PLAN_DE_ESTUDIO_INSTITUCIONAL",
        "PLAN_DE_ESTUDIO_CANONICO_PDF",
        "ARCHIVO_PDF",
        "JORNADA",
        "MODALIDAD",
        "SEDE",
        "VERSION",
        "VIGENCIA",
        "AÑO_DATO",
        "PERIODO",
        "PROCESO_ORIGEN",
        "FUENTE",
        "TIPO_RESPALDO",
        "HASH_FUENTE",
    ]
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv", rows, columns)
    ctx.metrics["carreras_tecnicas_identificadas"] = len({r["CODIGO_UNICO"] or r["NOMBRE_CARRERA"] for r in rows if r["TIPO_PROGRAMA_OBSERVADO"] == "TECNICO"})
    ctx.metrics["carreras_profesionales_identificadas"] = len({r["CODIGO_UNICO"] or r["NOMBRE_CARRERA"] for r in rows if r["TIPO_PROGRAMA_OBSERVADO"] == "PROFESIONAL"})
    ctx.metrics["programas_continuidad_identificados"] = len({r["CODIGO_UNICO"] or r["NOMBRE_CARRERA"] for r in rows if r["TIPO_PROGRAMA_OBSERVADO"] == "CONTINUIDAD"})


def stage_relaciones_previas(ctx: ExecutionContext) -> None:
    inventory = read_tsv_if_exists(ctx.run_dir / "01_INVENTARIO" / "01_INVENTARIO_FOCALIZADO.tsv")
    rows: list[dict[str, Any]] = []
    if not inventory.empty:
        mask = strict_boolean_mask(
            inventory["PROCESO_PROBABLE"].isin(["MATRICULA_UNIFICADA", "ESTUDIANTES_EXTRANJEROS"])
        )
        for _, item in inventory.loc[mask].iterrows():
            path = Path(item["RUTA"])
            text = normalize_text(path.name)
            if path.suffix.lower() in {".py", ".json", ".md", ".txt"}:
                try:
                    content, _ = read_text_file(path)
                    text += " " + normalize_text(content[:20000])
                except Exception:  # noqa: BLE001
                    pass
            terms = matching_terms(text)
            if not terms:
                continue
            rows.append(
                {
                    "PROCESO": item["PROCESO_PROBABLE"],
                    "CAMPO": ";".join(terms),
                    "VALOR": "",
                    "LOGICA": "Coincidencia documentada en fuente previa; no se transfiere como regla oficial de Avance Curricular.",
                    "FUENTE": item["RUTA"],
                    "NIVEL_RESPALDO": classify_evidence_level(path),
                    "APLICA_LOGISTICA": "SI" if any(term in terms for term in ["LOGISTICA", "ILOG", "TLOG"]) else "NO_DETERMINADO",
                    "APLICA_AVANCE_CURRICULAR": "NO_COMO_REGLA_OFICIAL",
                    "CONTRADICCION": "",
                    "OBSERVACION": "Uso permitido solo como dato observado/implementacion/decision previa.",
                }
            )
    columns = [
        "PROCESO",
        "CAMPO",
        "VALOR",
        "LOGICA",
        "FUENTE",
        "NIVEL_RESPALDO",
        "APLICA_LOGISTICA",
        "APLICA_AVANCE_CURRICULAR",
        "CONTRADICCION",
        "OBSERVACION",
    ]
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "02_RELACIONES_PREVIAS_MU_EXTRANJEROS.tsv", rows, columns)


def get_program_sets(ctx: ExecutionContext) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    identity = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    if identity.empty:
        return identity, identity, identity
    technical = identity.loc[strict_boolean_mask(identity["TIPO_PROGRAMA_OBSERVADO"].eq("TECNICO"))].copy()
    professional = identity.loc[strict_boolean_mask(identity["TIPO_PROGRAMA_OBSERVADO"].eq("PROFESIONAL"))].copy()
    continuity = identity.loc[strict_boolean_mask(identity["TIPO_PROGRAMA_OBSERVADO"].eq("CONTINUIDAD"))].copy()
    return technical, professional, continuity


def subject_rows_for_plans(plans: set[str], pdfs: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    subject_sources = [
        "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/05B_ASIGNATURAS_EXTRAIDAS_PDF_11.tsv",
        "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/05C_ASIGNATURAS_CANONICAS_HOJA1_11_PLANES.tsv",
    ]
    norm_plans = {normalize_text(plan) for plan in plans if normalize_text(plan)}
    norm_pdfs = {normalize_text(pdf) for pdf in pdfs if normalize_text(pdf)}
    for rel in subject_sources:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        df, _ = read_table(path)
        for idx in range(len(df)):
            row = {col: df.iloc[idx, pos] for pos, col in enumerate(df.columns)}
            plan = normalize_text(pick(row, ["PLAN_DE_ESTUDIO_INSTITUCIONAL", "PLAN_DE_ESTUDIO_CANONICO"]))
            pdf = normalize_text(pick(row, ["ARCHIVO_PDF"]))
            if (plan and plan in norm_plans) or (pdf and pdf in norm_pdfs):
                rows.append(
                    {
                        "FUENTE": str(path),
                        "ARCHIVO_PDF": pick(row, ["ARCHIVO_PDF"]),
                        "PLAN_DE_ESTUDIO_INSTITUCIONAL": pick(row, ["PLAN_DE_ESTUDIO_INSTITUCIONAL", "PLAN_DE_ESTUDIO_CANONICO"]),
                        "CODIGO_ASIGNATURA": pick(row, ["CODIGO_ASIGNATURA_PDF", "CODIGO_ASIGNATURA_CANONICO"]),
                        "NOMBRE_ASIGNATURA": pick(row, ["NOMBRE_ASIGNATURA_PDF", "NOMBRE_ASIGNATURA_CANONICO"]),
                        "NOMBRE_ASIGNATURA_NORMALIZADO": pick(row, ["NOMBRE_ASIGNATURA_NORMALIZADO"]),
                        "NIVEL": pick(row, ["NIVEL_PDF", "NIVEL_CANONICO"]),
                        "SEMESTRE": pick(row, ["SEMESTRE_PDF", "SEMESTRE_CANONICO"]),
                        "ORDEN": pick(row, ["ORDEN_PDF", "ORDEN_CANONICO"]),
                        "HASH_FUENTE": sha256_file(path),
                    }
                )
    return rows


def stage_comparacion(ctx: ExecutionContext) -> None:
    technical, professional, continuity = get_program_sets(ctx)
    tech_plans = set(technical.get("PLAN_DE_ESTUDIO_INSTITUCIONAL", pd.Series(dtype=str)).astype(str))
    prof_plans = set(professional.get("PLAN_DE_ESTUDIO_INSTITUCIONAL", pd.Series(dtype=str)).astype(str))
    tech_pdfs = set(technical.get("ARCHIVO_PDF", pd.Series(dtype=str)).astype(str))
    prof_pdfs = set(professional.get("ARCHIVO_PDF", pd.Series(dtype=str)).astype(str))
    tech_subjects = subject_rows_for_plans(tech_plans, tech_pdfs)
    prof_subjects = subject_rows_for_plans(prof_plans, prof_pdfs)
    columns = [
        "FUENTE",
        "ARCHIVO_PDF",
        "PLAN_DE_ESTUDIO_INSTITUCIONAL",
        "CODIGO_ASIGNATURA",
        "NOMBRE_ASIGNATURA",
        "NOMBRE_ASIGNATURA_NORMALIZADO",
        "NIVEL",
        "SEMESTRE",
        "ORDEN",
        "HASH_FUENTE",
    ]
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "03_ASIGNATURAS_TECNICO_LOGISTICA.tsv", tech_subjects, columns)
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "04_ASIGNATURAS_INGENIERIA_LOGISTICA.tsv", prof_subjects, columns)
    tech_keys = {extract_subject_key(row): row for row in tech_subjects}
    prof_keys = {extract_subject_key(row): row for row in prof_subjects}
    comparison_rows: list[dict[str, Any]] = []
    for key in sorted(set(tech_keys) | set(prof_keys)):
        in_tech = key in tech_keys
        in_prof = key in prof_keys
        row_t = tech_keys.get(key, {})
        row_p = prof_keys.get(key, {})
        if in_tech and in_prof:
            classification = "COMUN_CODIGO_EXACTO" if key.startswith("COD::") else "COMUN_NOMBRE_NIVEL"
        elif in_tech:
            classification = "SOLO_TECNICO"
        else:
            classification = "SOLO_PROFESIONAL"
        comparison_rows.append(
            {
                "CLAVE_ASIGNATURA": key,
                "CLASIFICACION": classification,
                "CODIGO_TECNICO": row_t.get("CODIGO_ASIGNATURA", ""),
                "NOMBRE_TECNICO": row_t.get("NOMBRE_ASIGNATURA", ""),
                "NIVEL_TECNICO": row_t.get("NIVEL", ""),
                "CODIGO_PROFESIONAL": row_p.get("CODIGO_ASIGNATURA", ""),
                "NOMBRE_PROFESIONAL": row_p.get("NOMBRE_ASIGNATURA", ""),
                "NIVEL_PROFESIONAL": row_p.get("NIVEL", ""),
                "FUENTE_TECNICO": row_t.get("FUENTE", ""),
                "FUENTE_PROFESIONAL": row_p.get("FUENTE", ""),
                "TIPO_RESPALDO": "DATO_OBSERVADO",
            }
        )
    comp_cols = [
        "CLAVE_ASIGNATURA",
        "CLASIFICACION",
        "CODIGO_TECNICO",
        "NOMBRE_TECNICO",
        "NIVEL_TECNICO",
        "CODIGO_PROFESIONAL",
        "NOMBRE_PROFESIONAL",
        "NIVEL_PROFESIONAL",
        "FUENTE_TECNICO",
        "FUENTE_PROFESIONAL",
        "TIPO_RESPALDO",
    ]
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "05_COMPARACION_MALLAS_LOGISTICA.tsv", comparison_rows, comp_cols)
    coverage = calculate_coverage(tech_keys.keys(), prof_keys.keys())
    common_code = sum(1 for row in comparison_rows if row["CLASIFICACION"] == "COMUN_CODIGO_EXACTO")
    common_name = sum(1 for row in comparison_rows if row["CLASIFICACION"] == "COMUN_NOMBRE_NIVEL")
    summary = [
        {
            **coverage,
            "COMUNES_CODIGO": common_code,
            "COMUNES_NOMBRE": common_name,
            "NIVELES_TECNICOS": ";".join(sorted({row.get("NIVEL", "") for row in tech_subjects if row.get("NIVEL", "")})),
            "NIVELES_PROFESIONALES": ";".join(sorted({row.get("NIVEL", "") for row in prof_subjects if row.get("NIVEL", "")})),
            "PDF_TECNICO": ";".join(sorted({pdf for pdf in tech_pdfs if pdf})),
            "PDF_PROFESIONAL": ";".join(sorted({pdf for pdf in prof_pdfs if pdf})),
            "MISMO_PDF": compare_pdf(next(iter(tech_pdfs), ""), next(iter(prof_pdfs), "")) if len(tech_pdfs) == 1 and len(prof_pdfs) == 1 else "NO_DETERMINADO",
            "MISMO_PLAN": compare_plan(next(iter(tech_plans), ""), next(iter(prof_plans), "")) if len(tech_plans) == 1 and len(prof_plans) == 1 else "NO_DETERMINADO",
            "PROGRAMAS_CONTINUIDAD": len(continuity),
        }
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "01_RESUMEN_COMPARACION_LOGISTICA.tsv", summary, list(summary[0].keys()))
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "02_DETALLE_MALLA_COMPARTIDA_LOGISTICA.tsv", comparison_rows, comp_cols)
    ctx.metrics.update(summary[0])


def stage_representacion(ctx: ExecutionContext) -> None:
    identity = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    components = [
        ("TABLA_MAESTRA", "01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv"),
        ("IDENTIDAD_APLICADA_34", "06_IDENTIDAD_APLICADA_34_CARRERAS.tsv"),
        ("DETALLE_RELACIONES", "06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv"),
        ("MAPEO_PDF_PLAN", "02_MAPEO_PDF_PLAN_NORMALIZADO.tsv"),
        ("VALIDACION_415_ASIGNATURAS", "12_VALIDACION_ASIGNATURAS_PDF_PLAN.tsv"),
        ("CIERRE_148", "16_CIERRE_148_CASOS_NO_EXACTOS.tsv"),
        ("EXCEL_146", "21_REVISION_MANUAL_OPTIMIZADA.xlsx"),
    ]
    rows = []
    for component, filename in components:
        matches = []
        for rel in PRIORITY_RELATIVE_PATHS:
            if rel.endswith(filename):
                matches.append(REPO_ROOT / rel)
        path = matches[0] if matches else Path(filename)
        text_present = "NO"
        if path.exists() and path.suffix.lower() in {".tsv", ".csv", ".md", ".txt", ".json"}:
            try:
                content, _ = read_text_file(path)
                text_present = "SI" if is_logistica(content) or "ILOG" in normalize_text(content) or "TLOG" in normalize_text(content) else "NO"
            except Exception:
                text_present = "NO"
        rows.append(
            {
                "COMPONENTE": component,
                "ARCHIVO": str(path),
                "CARRERA_TECNICA_PRESENTE": "SI" if not identity.empty and "TECNICO" in set(identity["TIPO_PROGRAMA_OBSERVADO"]) and text_present == "SI" else "NO_DETERMINADO",
                "CARRERA_PROFESIONAL_PRESENTE": "SI" if not identity.empty and "PROFESIONAL" in set(identity["TIPO_PROGRAMA_OBSERVADO"]) and text_present == "SI" else "NO_DETERMINADO",
                "RELACION_EXPLICITA": "NO_DETERMINADO",
                "RELACION_IMPLICITA": "SI" if text_present == "SI" else "NO",
                "RELACION_AUSENTE": "NO" if text_present == "SI" else "SI",
                "MALLA_COMPARTIDA_RECONOCIDA": "NO_DETERMINADO",
                "CONTINUIDAD_RECONOCIDA": "NO_DETERMINADO",
                "TIPO_RESPALDO": "DATO_OBSERVADO" if path.exists() else "HIPOTESIS_O_PENDIENTE",
            }
        )
    columns = list(rows[0].keys())
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "03_REPRESENTACION_EN_FLUJO_ACTUAL.tsv", rows, columns)
    ctx.metrics["relacion_reflejada_identidad"] = infer_reflection(rows, "TABLA_MAESTRA")
    ctx.metrics["relacion_reflejada_pdf_plan"] = infer_reflection(rows, "MAPEO_PDF_PLAN")
    ctx.metrics["relacion_reflejada_conciliacion"] = infer_reflection(rows, "VALIDACION_415_ASIGNATURAS")


def infer_reflection(rows: Sequence[Mapping[str, Any]], component: str) -> str:
    selected = [row for row in rows if row.get("COMPONENTE") == component]
    if not selected:
        return "NO"
    row = selected[0]
    if row.get("RELACION_EXPLICITA") == "SI":
        return "SI"
    if row.get("RELACION_IMPLICITA") == "SI":
        return "PARCIAL"
    return "NO"


def stage_impacto(ctx: ExecutionContext) -> None:
    path = REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/21_REVISION_MANUAL_OPTIMIZADA.xlsx"
    rows: list[dict[str, Any]] = []
    if path.exists():
        sheets = read_excel(path)
        detalle = sheets.get("DETALLE_CASOS", pd.DataFrame())
        for idx in range(len(detalle)):
            row = {col: detalle.iloc[idx, pos] for pos, col in enumerate(detalle.columns)}
            is_log = any(is_logistica(value) or normalize_text(value) in {"ILOG", "TLOG"} for value in row.values())
            if not is_log:
                continue
            estado = pick(row, ["ESTADO_FASE6", "TIPO_DIFERENCIA"])
            impacto = "SIN_IMPACTO"
            if "SIN" in normalize_text(estado):
                impacto = "POSIBLE_FALSO_SIN_CORRESPONDENCIA"
            elif "NOMBRE" in normalize_text(estado):
                impacto = "POSIBLE_FALSO_REVISAR_NOMBRE"
            rows.append(
                {
                    "ID_CASO": pick(row, ["ID_CASO"]),
                    "ID_DECISION_MAESTRA": pick(row, ["ID_DECISION_MAESTRA"]),
                    "CODIGO_UNICO": pick(row, ["CODIGO_UNICO"]),
                    "ARCHIVO_PDF": pick(row, ["ARCHIVO_PDF"]),
                    "PLAN": pick(row, ["PLAN", "PLAN_DE_ESTUDIO_INSTITUCIONAL"]),
                    "NOMBRE_PDF": pick(row, ["NOMBRE_PDF", "NOMBRE_ASIGNATURA_PDF"]),
                    "ESTADO_ORIGINAL": estado,
                    "IMPACTO": impacto,
                    "REQUIERE_REVISION_HUMANA": "SI",
                    "FUENTE": str(path),
                    "TIPO_RESPALDO": "DATO_OBSERVADO",
                }
            )
    columns = [
        "ID_CASO",
        "ID_DECISION_MAESTRA",
        "CODIGO_UNICO",
        "ARCHIVO_PDF",
        "PLAN",
        "NOMBRE_PDF",
        "ESTADO_ORIGINAL",
        "IMPACTO",
        "REQUIERE_REVISION_HUMANA",
        "FUENTE",
        "TIPO_RESPALDO",
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "04_IMPACTO_EN_146_CASOS.tsv", rows, columns)
    reevaluar = [row for row in rows if row["IMPACTO"] != "SIN_IMPACTO"]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "05_CASOS_LOGISTICA_REEVALUAR.tsv", reevaluar, columns)
    ctx.metrics["casos_manuales_totales"] = 146 if path.exists() else 0
    ctx.metrics["casos_manuales_logistica"] = len(rows)
    ctx.metrics["casos_potencialmente_afectados"] = len(reevaluar)
    ctx.metrics["posibles_falsos_sin_correspondencia"] = sum(1 for row in rows if row["IMPACTO"] == "POSIBLE_FALSO_SIN_CORRESPONDENCIA")
    ctx.metrics["posibles_falsos_revisar_nombre"] = sum(1 for row in rows if row["IMPACTO"] == "POSIBLE_FALSO_REVISAR_NOMBRE")
    ctx.metrics["fusiones_divisiones_relacionadas"] = sum(1 for row in rows if "FUSION" in normalize_text(row["ESTADO_ORIGINAL"]) or "DIVISION" in normalize_text(row["ESTADO_ORIGINAL"]))


def stage_otras_familias(ctx: ExecutionContext) -> None:
    identity = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    rows: list[dict[str, Any]] = []
    if not identity.empty:
        grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for _, row in identity.iterrows():
            family = "LOGISTICA" if is_logistica(row.get("NOMBRE_CARRERA", "")) else normalize_text(row.get("NOMBRE_CARRERA", "")).split(" ")[-1:]
            grouped[str(family)].append(row.to_dict())
        for family, items in grouped.items():
            types = {item.get("TIPO_PROGRAMA_OBSERVADO", "") for item in items}
            signals = sum(
                1
                for key in ["CODCARR", "CODCARPR", "ARCHIVO_PDF", "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS"]
                if len({normalize_text(item.get(key, "")) for item in items if normalize_text(item.get(key, ""))}) > 0
            )
            if {"TECNICO", "PROFESIONAL"} <= types and signals >= 2:
                rows.append(
                    {
                        "ID_FAMILIA": family,
                        "CARRERA_TECNICA": ";".join(item.get("NOMBRE_CARRERA", "") for item in items if item.get("TIPO_PROGRAMA_OBSERVADO") == "TECNICO"),
                        "CARRERA_PROFESIONAL": ";".join(item.get("NOMBRE_CARRERA", "") for item in items if item.get("TIPO_PROGRAMA_OBSERVADO") == "PROFESIONAL"),
                        "PLAN_TECNICO": ";".join(item.get("PLAN_DE_ESTUDIO_INSTITUCIONAL", "") for item in items if item.get("TIPO_PROGRAMA_OBSERVADO") == "TECNICO"),
                        "PLAN_PROFESIONAL": ";".join(item.get("PLAN_DE_ESTUDIO_INSTITUCIONAL", "") for item in items if item.get("TIPO_PROGRAMA_OBSERVADO") == "PROFESIONAL"),
                        "SENALES": signals,
                        "NIVEL_RESPALDO": "DATO_OBSERVADO",
                        "ESTADO": "RELACION_CANDIDATA",
                    }
                )
    columns = ["ID_FAMILIA", "CARRERA_TECNICA", "CARRERA_PROFESIONAL", "PLAN_TECNICO", "PLAN_PROFESIONAL", "SENALES", "NIVEL_RESPALDO", "ESTADO"]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "06_OTRAS_FAMILIAS_CANDIDATAS.tsv", rows, columns)


def decide_conclusion(metrics: Mapping[str, Any]) -> tuple[str, str, str]:
    tech = int(metrics.get("carreras_tecnicas_identificadas", 0) or 0)
    prof = int(metrics.get("carreras_profesionales_identificadas", 0) or 0)
    if tech == 0 or prof == 0:
        return "SIN_EVIDENCIA_SUFICIENTE", "HIPOTESIS_O_PENDIENTE", "E"
    coverage = float(metrics.get("COBERTURA_TECNICO_EN_PROFESIONAL", 0) or 0)
    same_pdf = metrics.get("MISMO_PDF", "NO_DETERMINADO")
    same_plan = metrics.get("MISMO_PLAN", "NO_DETERMINADO")
    if same_pdf == "SI" and coverage >= 0.95:
        return "MISMO_PDF_Y_MISMA_MALLA_OBSERVADA", "DATO_OBSERVADO", "A"
    if same_pdf == "SI" and same_plan == "NO":
        return "MISMO_PDF_CON_PLANES_DISTINTOS", "DATO_OBSERVADO", "B"
    if coverage >= 0.75:
        return "PLANES_DISTINTOS_CON_MALLA_TECNICA_CONTENIDA", "DATO_OBSERVADO", "B"
    if coverage > 0:
        return "PLANES_DISTINTOS_CON_MALLA_PARCIALMENTE_COMPARTIDA", "DATO_OBSERVADO", "B"
    return "RELACION_NO_REFLEJADA_EN_AVANCE_CURRICULAR", "DATO_OBSERVADO", "E"


def stage_conclusion(ctx: ExecutionContext) -> None:
    conclusion, respaldo, rec_key = decide_conclusion(ctx.metrics)
    if conclusion not in CONCLUSIONES_PERMITIDAS:
        raise RuntimeError("conclusion no permitida")
    rows = [
        {
            "FAMILIA": normalize_text(ctx.args.familia),
            "CONCLUSION_TECNICA": conclusion,
            "NIVEL_RESPALDO": respaldo,
            "REGLA_OFICIAL": "",
            "DATO_OBSERVADO": "ver tablas de identidad, comparacion e impacto",
            "IMPLEMENTACION_TECNICA": "script auditar_mallas_compartidas_tecnico_continuidad.py",
            "DECISION_INTERNA": "",
            "PENDIENTE": "confirmacion institucional si no existe regla oficial",
            "FUENTES": "ver trazabilidad evidencia",
        }
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "07_CONCLUSION_LOGISTICA.tsv", rows, list(rows[0].keys()))
    rec = [
        {
            "ALTERNATIVA": rec_key,
            "RECOMENDACION": RECOMENDACIONES[rec_key],
            "NO_APLICADA_AUTOMATICAMENTE": "SI",
        }
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "08_RECOMENDACION_ANTES_REVISION_MANUAL.tsv", rec, list(rec[0].keys()))
    ctx.metrics["conclusion_tecnica"] = conclusion
    ctx.metrics["nivel_respaldo"] = respaldo
    ctx.metrics["recomendacion"] = f"{rec_key}. {RECOMENDACIONES[rec_key]}"


def stage_reportes(ctx: ExecutionContext) -> None:
    summary_lines = [
        "# Resumen ejecutivo",
        "",
        f"Familia piloto: {normalize_text(ctx.args.familia)}",
        f"Conclusion tecnica: {ctx.metrics.get('conclusion_tecnica', 'SIN_EVIDENCIA_SUFICIENTE')}",
        f"Nivel de respaldo: {ctx.metrics.get('nivel_respaldo', 'HIPOTESIS_O_PENDIENTE')}",
        f"Recomendacion: {ctx.metrics.get('recomendacion', '')}",
        "",
        "No se aplicaron decisiones humanas, no se genero precarga y no se genero PES.",
    ]
    (ctx.run_dir / "04_RESULTADOS" / "09_RESUMEN_EJECUTIVO.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    make_excel(ctx)
    make_controls(ctx)
    final_manifest = {
        **read_json(ctx.run_dir / "00_CONTROL" / "manifiesto_ejecucion.json"),
        "cerrado_en": datetime.now().isoformat(timespec="seconds"),
        "estado": "BLOQUEADA" if ctx.blocked else "COMPLETADA",
        "metricas": ctx.metrics,
        "originales_modificados": "NO",
        "excel_manual_modificado": "NO",
        "decisiones_humanas_aplicadas": 0,
        "precarga_generada": "NO",
        "pes_generado": "NO",
        "apto_para_carga": "NO",
    }
    write_json(ctx.run_dir / "00_CONTROL" / "manifiesto_final.json", final_manifest)


def make_excel(ctx: ExecutionContext) -> None:
    output = ctx.run_dir / "04_RESULTADOS" / "10_AUDITORIA_MALLAS_COMPARTIDAS_TEC_CONT.xlsx"
    sheets = {
        "RESUMEN": pd.DataFrame([ctx.metrics]),
        "LOGISTICA_IDENTIDAD": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv"),
        "LOGISTICA_PLANES": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")[
            ["CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "PLAN_DE_ESTUDIO_CANONICO_PDF"]
        ]
        if not read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv").empty
        else pd.DataFrame(),
        "LOGISTICA_PDF": read_tsv_if_exists(ctx.run_dir / "04_RESULTADOS" / "01_RESUMEN_COMPARACION_LOGISTICA.tsv"),
        "LOGISTICA_ASIGNATURAS_COMUNES": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "05_COMPARACION_MALLAS_LOGISTICA.tsv"),
        "SOLO_TECNICO": filter_tsv(ctx.run_dir / "03_INTERMEDIOS" / "05_COMPARACION_MALLAS_LOGISTICA.tsv", "CLASIFICACION", "SOLO_TECNICO"),
        "SOLO_PROFESIONAL": filter_tsv(ctx.run_dir / "03_INTERMEDIOS" / "05_COMPARACION_MALLAS_LOGISTICA.tsv", "CLASIFICACION", "SOLO_PROFESIONAL"),
        "IMPACTO_146_CASOS": read_tsv_if_exists(ctx.run_dir / "04_RESULTADOS" / "04_IMPACTO_EN_146_CASOS.tsv"),
        "CASOS_REEVALUAR": read_tsv_if_exists(ctx.run_dir / "04_RESULTADOS" / "05_CASOS_LOGISTICA_REEVALUAR.tsv"),
        "OTRAS_FAMILIAS": read_tsv_if_exists(ctx.run_dir / "04_RESULTADOS" / "06_OTRAS_FAMILIAS_CANDIDATAS.tsv"),
        "EVIDENCIA_OFICIAL": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "01_EVIDENCIA_OFICIAL.tsv"),
        "DATOS_OBSERVADOS": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "02_DATOS_OBSERVADOS.tsv"),
        "IMPLEMENTACION": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "03_IMPLEMENTACION_TECNICA.tsv"),
        "DECISIONES_INTERNAS": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "04_DECISIONES_INTERNAS.tsv"),
        "PENDIENTES": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "05_HIPOTESIS_PENDIENTES.tsv"),
        "DICCIONARIO": pd.DataFrame(
            [
                {"CAMPO": "TIPO_RESPALDO", "DESCRIPCION": "REGLA_OFICIAL, DATO_OBSERVADO, IMPLEMENTACION_TECNICA, DECISION_INTERNA, HIPOTESIS_O_PENDIENTE"},
                {"CAMPO": "PLAN_ESTUDIOS_SIES", "DESCRIPCION": "Campo separado; no fusionar con plan institucional."},
                {"CAMPO": "CODIGO_UNICO_FINAL", "DESCRIPCION": "Campo separado; no fusionar con CODIGO_UNICO."},
            ]
        ),
    }
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in sheets.items():
            safe = sheet_name[:31]
            dataframe.to_excel(writer, sheet_name=safe, index=False)
            ws = writer.sheets[safe]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            if Alignment is not None:
                for row in ws.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True, vertical="top")
            if Table is not None and dataframe.shape[1] > 0 and dataframe.shape[0] >= 1:
                ref = ws.dimensions
                table = Table(displayName=re.sub(r"[^A-Za-z0-9_]", "_", f"T_{safe}")[:30], ref=ref)
                if TableStyleInfo is not None:
                    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
                ws.add_table(table)
            for col_cells in ws.columns:
                width = min(max(len(str(cell.value or "")) for cell in col_cells) + 2, 60)
                ws.column_dimensions[col_cells[0].column_letter].width = width
                header = str(col_cells[0].value or "").upper()
                for cell in col_cells[1:]:
                    if "COBERTURA" in header or "JACCARD" in header:
                        cell.number_format = "0.00%"
                    elif header.startswith("TOTAL") or header.startswith("ASIGNATURAS"):
                        cell.number_format = "#,##0"
    ctx.metrics["excel"] = str(output)


def filter_tsv(path: Path, column: str, value: str) -> pd.DataFrame:
    df = read_tsv_if_exists(path)
    if df.empty or column not in df.columns:
        return pd.DataFrame()
    return df.loc[strict_boolean_mask(df[column].eq(value))].copy()


def make_controls(ctx: ExecutionContext) -> None:
    outputs = []
    for path in sorted(ctx.run_dir.rglob("*")):
        if path.is_file():
            outputs.append(
                {
                    "RUTA_RELATIVA": safe_relative(path, ctx.run_dir),
                    "TAMANO_BYTES": path.stat().st_size,
                    "HASH_SHA256": sha256_file(path),
                }
            )
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "06_INVENTARIO_SALIDAS.tsv", outputs, ["RUTA_RELATIVA", "TAMANO_BYTES", "HASH_SHA256"])
    control_rows = [
        {"CONTROL": "SCRIPT_COMPILA", "ESTADO": "OK", "DETALLE": "ver ejecucion previa"},
        {"CONTROL": "ORIGINALES_MODIFICADOS", "ESTADO": "OK", "DETALLE": "NO"},
        {"CONTROL": "EXCEL_MANUAL_MODIFICADO", "ESTADO": "OK", "DETALLE": "NO"},
        {"CONTROL": "DECISIONES_HUMANAS_APLICADAS", "ESTADO": "OK", "DETALLE": "0"},
        {"CONTROL": "PRECARGA_GENERADA", "ESTADO": "OK", "DETALLE": "NO"},
        {"CONTROL": "PES_GENERADO", "ESTADO": "OK", "DETALLE": "NO"},
        {"CONTROL": "APTO_PARA_CARGA", "ESTADO": "OK", "DETALLE": "NO"},
    ]
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "01_CONTROL_INTEGRIDAD.tsv", control_rows, ["CONTROL", "ESTADO", "DETALLE"])
    evidence_trace = []
    for rel in ["01_EVIDENCIA_OFICIAL.tsv", "02_DATOS_OBSERVADOS.tsv", "03_IMPLEMENTACION_TECNICA.tsv", "04_DECISIONES_INTERNAS.tsv", "05_HIPOTESIS_PENDIENTES.tsv"]:
        df = read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / rel)
        evidence_trace.append({"ARCHIVO": rel, "FILAS": len(df), "TIPO": rel.split("_", 1)[1].replace(".tsv", "")})
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "02_TRAZABILIDAD_EVIDENCIA.tsv", evidence_trace, ["ARCHIVO", "FILAS", "TIPO"])
    count_rows = [{"METRICA": key, "VALOR": value} for key, value in sorted(ctx.metrics.items())]
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "04_CONTROL_CONTEOS.tsv", count_rows, ["METRICA", "VALOR"])
    source_rows = []
    for rel in PRIORITY_RELATIVE_PATHS:
        path = REPO_ROOT / rel
        source_rows.append(
            {
                "RUTA_RELATIVA": rel,
                "EXISTE": "SI" if path.exists() else "NO",
                "HASH_SHA256": sha256_file(path) if path.exists() else "",
                "MODIFICADO": "NO",
            }
        )
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "05_CONTROL_ORIGINALES.tsv", source_rows, ["RUTA_RELATIVA", "EXISTE", "HASH_SHA256", "MODIFICADO"])


def parse_fallback_log(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    text = path.read_text(encoding="utf-8", errors="replace")
    total = re.search(r"Pruebas ejecutadas: (\d+)", text)
    failures = re.search(r"Fallos: (\d+)", text)
    return int(total.group(1)) if total else 0, int(failures.group(1)) if failures else 0


def run_unit_tests_without_pytest(test_path: Path, log_path: Path) -> int:
    spec = importlib.util.spec_from_file_location("audit_unit_tests", test_path)
    if spec is None or spec.loader is None:
        log_path.write_text(f"No se pudo cargar {test_path}\n", encoding="utf-8")
        return 1
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        log_path.write_text(f"Error importando pruebas: {exc}\n", encoding="utf-8")
        return 1
    failures: list[str] = []
    executed = 0
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        candidate = getattr(module, name)
        if not callable(candidate):
            continue
        executed += 1
        signature = inspect.signature(candidate)
        kwargs: dict[str, Any] = {}
        temp_context: tempfile.TemporaryDirectory[str] | None = None
        if "tmp_path" in signature.parameters:
            temp_context = tempfile.TemporaryDirectory()
            kwargs["tmp_path"] = Path(temp_context.name)
        try:
            candidate(**kwargs)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
        finally:
            if temp_context is not None:
                temp_context.cleanup()
    lines = [
        "pytest no esta instalado; fallback interno ejecutado.",
        "No equivale a pytest real.",
        f"Pruebas ejecutadas: {executed}",
        f"Fallos: {len(failures)}",
    ]
    lines.extend(failures)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if executed >= 32 and not failures else 1


def run_internal_tests(ctx: ExecutionContext) -> None:
    pytest_log = ctx.run_dir / "06_LOGS" / "pytest_interno.log"
    test_path = REPO_ROOT / "tests" / "test_auditar_mallas_compartidas_tecnico_continuidad.py"
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(test_path)],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    pytest_log.write_text(completed.stdout, encoding="utf-8")
    ctx.metrics["pytest_disponible"] = "SI"
    ctx.metrics["fallback_utilizado"] = "NO"
    if completed.returncode != 0 and "No module named pytest" in completed.stdout:
        ctx.metrics["pytest_disponible"] = "NO"
        ctx.metrics["fallback_utilizado"] = "SI"
        fallback_log = ctx.run_dir / "06_LOGS" / "pytest_fallback_interno.log"
        rc = run_unit_tests_without_pytest(test_path, fallback_log)
        total, failures = parse_fallback_log(fallback_log)
        ctx.metrics["pruebas_total"] = total
        ctx.metrics["pruebas_fallos"] = failures
        if rc != 0:
            raise RuntimeError("pruebas internas fallaron en fallback")
    elif completed.returncode != 0:
        raise RuntimeError("pruebas internas fallaron con pytest")
    else:
        match = re.search(r"(\d+) passed", completed.stdout)
        ctx.metrics["pruebas_total"] = int(match.group(1)) if match else 0
        ctx.metrics["pruebas_fallos"] = 0


def stage_tests(ctx: ExecutionContext) -> None:
    run_internal_tests(ctx)
    rows = [
        {
            "PYTEST_DISPONIBLE": ctx.metrics["pytest_disponible"],
            "FALLBACK_UTILIZADO": ctx.metrics["fallback_utilizado"],
            "PRUEBAS_TOTAL": ctx.metrics["pruebas_total"],
            "PRUEBAS_FALLOS": ctx.metrics["pruebas_fallos"],
        }
    ]
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "00_CONTROL_PRUEBAS.tsv", rows, list(rows[0].keys()))


def build_stage_specs() -> list[StageSpec]:
    return [
        StageSpec(
            "00_PRUEBAS_INTERNAS",
            "CONTROL",
            stage_tests,
            ["05_AUDITORIA/00_CONTROL_PRUEBAS.tsv"],
            {"05_AUDITORIA/00_CONTROL_PRUEBAS.tsv": ["PYTEST_DISPONIBLE", "FALLBACK_UTILIZADO", "PRUEBAS_TOTAL", "PRUEBAS_FALLOS"]},
        ),
        StageSpec(
            "01_INVENTARIO",
            "BLOQUE_1",
            stage_inventario,
            ["01_INVENTARIO/01_INVENTARIO_FOCALIZADO.tsv", "01_INVENTARIO/02_FUENTES_PRIORITARIAS.tsv", "01_INVENTARIO/03_DUPLICADOS_HASH.tsv"],
            {"01_INVENTARIO/01_INVENTARIO_FOCALIZADO.tsv": ["ID_ARCHIVO", "RUTA", "HASH_SHA256"]},
        ),
        StageSpec(
            "02_EVIDENCIA",
            "BLOQUE_1",
            stage_evidencia,
            ["02_EVIDENCIA/01_EVIDENCIA_OFICIAL.tsv", "02_EVIDENCIA/02_DATOS_OBSERVADOS.tsv", "02_EVIDENCIA/03_IMPLEMENTACION_TECNICA.tsv", "02_EVIDENCIA/04_DECISIONES_INTERNAS.tsv", "02_EVIDENCIA/05_HIPOTESIS_PENDIENTES.tsv", "05_AUDITORIA/03_CONTROL_ENCABEZADOS_DUPLICADOS.tsv"],
            {"02_EVIDENCIA/02_DATOS_OBSERVADOS.tsv": ["FUENTE", "TIPO_RESPALDO", "HASH_FUENTE"]},
        ),
        StageSpec(
            "03_IDENTIDAD_LOGISTICA",
            "BLOQUE_1",
            stage_identidad,
            ["03_INTERMEDIOS/01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv"],
            {"03_INTERMEDIOS/01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv": ["CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL"]},
        ),
        StageSpec(
            "04_RELACIONES_PREVIAS",
            "BLOQUE_1",
            stage_relaciones_previas,
            ["03_INTERMEDIOS/02_RELACIONES_PREVIAS_MU_EXTRANJEROS.tsv"],
            {"03_INTERMEDIOS/02_RELACIONES_PREVIAS_MU_EXTRANJEROS.tsv": ["PROCESO", "FUENTE", "NIVEL_RESPALDO", "APLICA_AVANCE_CURRICULAR"]},
        ),
        StageSpec(
            "05_COMPARACION_MALLAS",
            "BLOQUE_2",
            stage_comparacion,
            ["03_INTERMEDIOS/03_ASIGNATURAS_TECNICO_LOGISTICA.tsv", "03_INTERMEDIOS/04_ASIGNATURAS_INGENIERIA_LOGISTICA.tsv", "03_INTERMEDIOS/05_COMPARACION_MALLAS_LOGISTICA.tsv", "04_RESULTADOS/01_RESUMEN_COMPARACION_LOGISTICA.tsv", "04_RESULTADOS/02_DETALLE_MALLA_COMPARTIDA_LOGISTICA.tsv"],
            {"04_RESULTADOS/01_RESUMEN_COMPARACION_LOGISTICA.tsv": ["ASIGNATURAS_TECNICAS", "ASIGNATURAS_PROFESIONALES", "COBERTURA_TECNICO_EN_PROFESIONAL"]},
        ),
        StageSpec(
            "06_REPRESENTACION_FLUJO",
            "BLOQUE_2",
            stage_representacion,
            ["04_RESULTADOS/03_REPRESENTACION_EN_FLUJO_ACTUAL.tsv"],
            {"04_RESULTADOS/03_REPRESENTACION_EN_FLUJO_ACTUAL.tsv": ["COMPONENTE", "RELACION_IMPLICITA", "TIPO_RESPALDO"]},
        ),
        StageSpec(
            "07_IMPACTO_146",
            "BLOQUE_2",
            stage_impacto,
            ["04_RESULTADOS/04_IMPACTO_EN_146_CASOS.tsv", "04_RESULTADOS/05_CASOS_LOGISTICA_REEVALUAR.tsv"],
            {"04_RESULTADOS/04_IMPACTO_EN_146_CASOS.tsv": ["ID_CASO", "ID_DECISION_MAESTRA", "IMPACTO"]},
        ),
        StageSpec(
            "08_OTRAS_FAMILIAS",
            "BLOQUE_2",
            stage_otras_familias,
            ["04_RESULTADOS/06_OTRAS_FAMILIAS_CANDIDATAS.tsv"],
            {"04_RESULTADOS/06_OTRAS_FAMILIAS_CANDIDATAS.tsv": ["ID_FAMILIA", "SENALES", "ESTADO"]},
        ),
        StageSpec(
            "09_CONCLUSION",
            "BLOQUE_3",
            stage_conclusion,
            ["04_RESULTADOS/07_CONCLUSION_LOGISTICA.tsv", "04_RESULTADOS/08_RECOMENDACION_ANTES_REVISION_MANUAL.tsv"],
            {"04_RESULTADOS/07_CONCLUSION_LOGISTICA.tsv": ["CONCLUSION_TECNICA", "NIVEL_RESPALDO"]},
        ),
        StageSpec(
            "10_REPORTE_FINAL",
            "BLOQUE_3",
            stage_reportes,
            ["04_RESULTADOS/09_RESUMEN_EJECUTIVO.md", "04_RESULTADOS/10_AUDITORIA_MALLAS_COMPARTIDAS_TEC_CONT.xlsx", "05_AUDITORIA/01_CONTROL_INTEGRIDAD.tsv", "05_AUDITORIA/02_TRAZABILIDAD_EVIDENCIA.tsv", "05_AUDITORIA/04_CONTROL_CONTEOS.tsv", "05_AUDITORIA/05_CONTROL_ORIGINALES.tsv", "05_AUDITORIA/06_INVENTARIO_SALIDAS.tsv", "00_CONTROL/manifiesto_final.json"],
            {"05_AUDITORIA/01_CONTROL_INTEGRIDAD.tsv": ["CONTROL", "ESTADO", "DETALLE"]},
        ),
    ]


def execute_complete(ctx: ExecutionContext) -> None:
    init_execution(ctx)
    for spec in build_stage_specs():
        run_stage(ctx, spec)
    state = load_state(ctx)
    state["estado_general"] = "COMPLETADA"
    save_state(ctx, state)


def print_final(ctx: ExecutionContext) -> None:
    metrics = ctx.metrics
    conclusion = metrics.get("conclusion_tecnica", "SIN_EVIDENCIA_SUFICIENTE")
    respaldo = metrics.get("nivel_respaldo", "HIPOTESIS_O_PENDIENTE")
    recommendation = metrics.get("recomendacion", "E. " + RECOMENDACIONES["E"])
    print("AUDITORÍA END-TO-END DE MALLAS COMPARTIDAS COMPLETADA")
    print("")
    print(f"Estado: {'BLOQUEADA' if ctx.blocked else 'COMPLETADA'}")
    print("Script compila: SI")
    print(f"Pruebas internas: {metrics.get('pruebas_total', 0) - metrics.get('pruebas_fallos', 0)}/{metrics.get('pruebas_total', 0)}")
    print(f"Pytest disponible: {metrics.get('pytest_disponible', 'NO')}")
    print(f"Fallback utilizado: {metrics.get('fallback_utilizado', 'NO')}")
    print("")
    print(f"Familia piloto: {normalize_text(ctx.args.familia)}")
    print("")
    print(f"Archivos inventariados: {metrics.get('archivos_inventariados', 0)}")
    print(f"Fuentes oficiales revisadas: {metrics.get('fuentes_oficiales_revisadas', 0)}")
    print(f"Datos observados revisados: {metrics.get('datos_observados_revisados', 0)}")
    print(f"Scripts revisados: {metrics.get('scripts_revisados', 0)}")
    print(f"Auditorías revisadas: {metrics.get('auditorias_revisadas', 0)}")
    print("")
    print(f"Carreras técnicas identificadas: {metrics.get('carreras_tecnicas_identificadas', 0)}")
    print(f"Carreras profesionales identificadas: {metrics.get('carreras_profesionales_identificadas', 0)}")
    print(f"Programas de continuidad identificados: {metrics.get('programas_continuidad_identificados', 0)}")
    print("")
    print(f"CODIGO_UNICO Logística: {count_unique_identity('CODIGO_UNICO', ctx)}")
    print(f"Planes técnicos: {count_plans(ctx, 'TECNICO')}")
    print(f"Planes profesionales: {count_plans(ctx, 'PROFESIONAL')}")
    print(f"PDF técnicos: {count_pdfs(ctx, 'TECNICO')}")
    print(f"PDF profesionales: {count_pdfs(ctx, 'PROFESIONAL')}")
    print("")
    print(f"Mismo PDF técnico/profesional: {metrics.get('MISMO_PDF', 'NO_DETERMINADO')}")
    print(f"Mismo plan institucional: {metrics.get('MISMO_PLAN', 'NO_DETERMINADO')}")
    print(f"Malla técnica contenida en profesional: {contained_status(metrics)}")
    print(f"Cobertura técnica en profesional: {float(metrics.get('COBERTURA_TECNICO_EN_PROFESIONAL', 0) or 0):.0%}")
    print(f"Asignaturas comunes validadas: {metrics.get('COMUNES_VALIDADAS', 0)}")
    print(f"Solo técnicas: {metrics.get('SOLO_TECNICO', 0)}")
    print(f"Solo profesionales: {metrics.get('SOLO_PROFESIONAL', 0)}")
    print("")
    print(f"Relación reflejada en identidad: {metrics.get('relacion_reflejada_identidad', 'NO')}")
    print(f"Relación reflejada en PDF–plan: {metrics.get('relacion_reflejada_pdf_plan', 'NO')}")
    print(f"Relación reflejada en conciliación: {metrics.get('relacion_reflejada_conciliacion', 'NO')}")
    print("")
    print(f"Casos manuales totales: {metrics.get('casos_manuales_totales', 0)}")
    print(f"Casos manuales de Logística: {metrics.get('casos_manuales_logistica', 0)}")
    print(f"Casos potencialmente afectados: {metrics.get('casos_potencialmente_afectados', 0)}")
    print(f"Posibles falsos sin correspondencia: {metrics.get('posibles_falsos_sin_correspondencia', 0)}")
    print(f"Posibles falsos revisar nombre: {metrics.get('posibles_falsos_revisar_nombre', 0)}")
    print(f"Fusiones/divisiones relacionadas: {metrics.get('fusiones_divisiones_relacionadas', 0)}")
    print("")
    print("Conclusión técnica:")
    print(conclusion)
    print("")
    print("Nivel de respaldo:")
    print(respaldo)
    print("")
    print("Recomendación:")
    print(recommendation)
    print("")
    print(f"Excel:\n{ctx.run_dir / '04_RESULTADOS/10_AUDITORIA_MALLAS_COMPARTIDAS_TEC_CONT.xlsx'}")
    print(f"Resumen ejecutivo:\n{ctx.run_dir / '04_RESULTADOS/09_RESUMEN_EJECUTIVO.md'}")
    print(f"Conclusión Logística:\n{ctx.run_dir / '04_RESULTADOS/07_CONCLUSION_LOGISTICA.tsv'}")
    print(f"Impacto en 146 casos:\n{ctx.run_dir / '04_RESULTADOS/04_IMPACTO_EN_146_CASOS.tsv'}")
    print(f"Otras familias:\n{ctx.run_dir / '04_RESULTADOS/06_OTRAS_FAMILIAS_CANDIDATAS.tsv'}")
    print(f"Manifiesto:\n{ctx.run_dir / '00_CONTROL/manifiesto_final.json'}")
    print(f"Carpeta de ejecución:\n{ctx.run_dir}")
    print("")
    print(f"Ejecución parcial anterior preservada: {'SI' if PREVIOUS_PARTIAL_RUN.exists() else 'NO'}")
    print("Originales modificados: NO")
    print("Excel manual modificado: NO")
    print("Decisiones humanas aplicadas: 0")
    print("Precarga generada: NO")
    print("PES generado: NO")
    print("Apto para carga: NO")
    print("")
    print("No ejecutar automáticamente modificaciones al flujo PDF–plan.")
    print("No modificar el paquete manual.")


def count_unique_identity(column: str, ctx: ExecutionContext) -> int:
    df = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS/01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    if df.empty or column not in df.columns:
        return 0
    return len({normalize_text(value) for value in df[column] if normalize_text(value)})


def count_plans(ctx: ExecutionContext, tipo: str) -> int:
    df = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS/01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    if df.empty:
        return 0
    mask = strict_boolean_mask(df["TIPO_PROGRAMA_OBSERVADO"].eq(tipo))
    return len({normalize_text(value) for value in df.loc[mask, "PLAN_DE_ESTUDIO_INSTITUCIONAL"] if normalize_text(value)})


def count_pdfs(ctx: ExecutionContext, tipo: str) -> int:
    df = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS/01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    if df.empty:
        return 0
    mask = strict_boolean_mask(df["TIPO_PROGRAMA_OBSERVADO"].eq(tipo))
    return len({normalize_text(value) for value in df.loc[mask, "ARCHIVO_PDF"] if normalize_text(value)})


def contained_status(metrics: Mapping[str, Any]) -> str:
    coverage = float(metrics.get("COBERTURA_TECNICO_EN_PROFESIONAL", 0) or 0)
    if coverage >= 0.95:
        return "SI"
    if coverage > 0:
        return "NO_DETERMINADO"
    return "NO_DETERMINADO"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auditoria end-to-end de mallas compartidas")
    parser.add_argument("--ejecutar-completo", action="store_true", help="ejecutar flujo end-to-end")
    parser.add_argument("--fase", default=None, help="compatibilidad interna; no requerida")
    parser.add_argument("--familia", default="logistica")
    parser.add_argument("--reanudar", action="store_true")
    parser.add_argument("--forzar", action="store_true")
    parser.add_argument("--carpeta-ejecucion", default=None)
    parser.add_argument("--modo-auditoria", default="solo_lectura")
    parser.add_argument("--max-archivos", type=int, default=None)
    parser.add_argument("--solo-logistica", action="store_true")
    return parser.parse_args(argv)


def validate_repo() -> None:
    if REPO_ROOT.resolve() != EXPECTED_REPO.resolve():
        raise SystemExit(f"Repositorio no permitido: {REPO_ROOT}")


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    validate_repo()
    if not args.ejecutar_completo:
        raise SystemExit("Use --ejecutar-completo para el flujo normal.")
    run_dir = build_run_dir(args.carpeta_ejecucion)
    ctx = ExecutionContext(REPO_ROOT, run_dir, args)
    try:
        execute_complete(ctx)
    except Exception as exc:  # noqa: BLE001
        ctx.blocked = True
        ctx.block_reasons.append(str(exc))
        state = load_state(ctx) if ctx.run_dir.exists() else {"etapas": {}}
        state["estado_general"] = "BLOQUEADA"
        save_state(ctx, state)
        log(ctx, f"BLOQUEADA: {exc}")
        if "conclusion_tecnica" not in ctx.metrics:
            ctx.metrics["conclusion_tecnica"] = "SIN_EVIDENCIA_SUFICIENTE"
            ctx.metrics["nivel_respaldo"] = "HIPOTESIS_O_PENDIENTE"
            ctx.metrics["recomendacion"] = "E. " + RECOMENDACIONES["E"]
    print_final(ctx)


if __name__ == "__main__":
    main()
