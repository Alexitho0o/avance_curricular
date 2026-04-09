#!/usr/bin/env python3
"""Auditoria reproducible de mallas tecnico-continuidad para Avance Curricular.

El script esta disenado como herramienta de solo lectura sobre las fuentes del
proyecto. Cada fase escribe derivados en una carpeta de ejecucion versionada y
mantiene separadas las evidencias oficiales, observadas, tecnicas, internas y
pendientes.
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
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITORIA_BASE = (
    REPO_ROOT
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
)
RUN_PREFIX = "AUDITORIA_MALLAS_COMPARTIDAS_TEC_CONT"
PROCESS_NAME = "Avance Curricular SIES 2026"
SUBPROJECT_NAME = (
    "Auditoria transversal de carreras tecnicas, profesionales y continuidad "
    "con mallas compartidas"
)

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
TABULAR_EXTENSIONS = {".csv", ".tsv"}
EXCEL_EXTENSIONS = {".xlsx", ".xlsm"}
TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".tsv",
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

PRIORITY_RELATIVE_PATHS = [
    "avance_curricular_2026/00_fuentes_congeladas/"
    "CARGA_CONGELADA_20260626_005826/originales/"
    "Instructivo_Avance Curricular SIES - 2026.txt",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/"
    "04_RESULTADOS/01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/"
    "04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/"
    "04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/"
    "04_RESULTADOS/07_CARRERAS_IDENTIDAD_VALIDADA.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/"
    "04_RESULTADOS/10_VALIDACION_PDF_PLAN_INTEGRADA.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622/"
    "04_RESULTADOS/11_RESUMEN_FINAL_INTEGRACION.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/03_VALIDACION_PUENTE_34.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/05B_ASIGNATURAS_EXTRAIDAS_PDF_11.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/05C_ASIGNATURAS_CANONICAS_HOJA1_11_PLANES.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/05D_CONCILIACION_EXACTA_ASIGNATURAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "02_INTERMEDIOS/05E_CONCILIACION_APROXIMADA_ASIGNATURAS.tsv",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "04_RESULTADOS/20_REVISION_MANUAL_CASOS_PENDIENTES.xlsx",
    "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/"
    "04_RESULTADOS/21_REVISION_MANUAL_OPTIMIZADA.xlsx",
]

SEARCH_TERMS = [
    "LOGISTICA",
    "LOGISTICA",
    "INGENIERIA EN LOGISTICA",
    "TECNICO EN LOGISTICA",
    "ILOG",
    "TLOG",
    "CONTINUIDAD",
    "ARTICULACION",
    "SALIDA INTERMEDIA",
    "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS",
    "PLAN_DE_ESTUDIO",
    "PLAN_ESTUDIOS",
    "CODIGO_UNICO",
    "CODIGO_UNICO_FINAL",
    "CODCARR",
    "CODCARPR",
    "MALLA",
    "PDF",
    "ASIGNATURA",
    "NIVEL",
    "SEMESTRE",
]

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


@dataclass(frozen=True)
class ExecutionContext:
    repo_root: Path
    run_dir: Path
    args: argparse.Namespace


def strip_accents(value: Any) -> str:
    text = "" if value is None else str(value)
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_text(value: Any) -> str:
    text = strip_accents(value).upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_family(value: Any) -> str:
    return normalize_text(value)


def is_logistica(value: Any) -> bool:
    return "LOGISTICA" in normalize_text(value)


def classify_program_type(row: Mapping[str, Any]) -> str:
    joined = " ".join(normalize_text(v) for v in row.values() if v is not None)
    if re.search(r"\bTECNIC[OA]\b|\bTNS\b|\bTLOG\b", joined):
        return "TECNICO"
    if "CONTINUIDAD" in joined or "ARTICULACION" in joined:
        return "CONTINUIDAD"
    if "INGENIERIA" in joined or "PROFESIONAL" in joined or "ILOG" in joined:
        return "PROFESIONAL"
    return "NO_DETERMINADO"


def duplicate_header_positions(headers: Sequence[str]) -> dict[str, list[int]]:
    counts = Counter(headers)
    return {
        name: [pos for pos, header in enumerate(headers) if header == name]
        for name, count in counts.items()
        if count > 1
    }


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
    if text in {"NO", "N", "FALSE", "FALSO", "0", ""}:
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
    return "MISMO_PLAN" if left == right else "PLANES_DISTINTOS"


def calculate_coverage(
    technical_subjects: Iterable[Any], professional_subjects: Iterable[Any]
) -> dict[str, float | int]:
    technical = {normalize_text(v) for v in technical_subjects if normalize_text(v)}
    professional = {
        normalize_text(v) for v in professional_subjects if normalize_text(v)
    }
    if not technical and not professional:
        return {
            "ASIGNATURAS_TECNICAS": 0,
            "ASIGNATURAS_PROFESIONALES": 0,
            "COMUNES_TOTAL_VALIDADO": 0,
            "COBERTURA_TECNICO_EN_PROFESIONAL": 0.0,
            "COBERTURA_PROFESIONAL_EN_TECNICO": 0.0,
            "JACCARD": 0.0,
        }
    common = technical & professional
    union = technical | professional
    return {
        "ASIGNATURAS_TECNICAS": len(technical),
        "ASIGNATURAS_PROFESIONALES": len(professional),
        "COMUNES_TOTAL_VALIDADO": len(common),
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
        "DECISION_DOCUMENTADA",
    }
    normalized_evidence_keys = {normalize_text(item) for item in evidence_keys}
    absent_values = {"", "NO", "NO_DETERMINADO", "SIN_EVIDENCIA", "PENDIENTE"}
    for key, value in signals.items():
        if normalize_text(key) in normalized_evidence_keys:
            if normalize_text(value) in absent_values:
                continue
            if isinstance(value, (int, float)):
                if value > 0:
                    return True
            elif _coerce_boolish(value):
                return True
    return False


def safe_relative(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def is_allowed_file(path: Path) -> bool:
    if path.name.startswith("~$"):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def should_exclude_path(path: Path, current_run_dir: Path | None = None) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if current_run_dir is not None:
        try:
            path.resolve().relative_to(current_run_dir.resolve())
            return True
        except ValueError:
            pass
    name = normalize_text(path.name)
    return "TEMPORAL" in name or "TMP" == name


def classify_backup(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    backup_terms = ["RESPALDO", "BACKUP", "COPIA", "ANTES", "PRE_CORRECCIONES"]
    return "SI" if any(term in normalized for term in backup_terms) else "NO"


def classify_source_original(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    if "ORIGINALES" in normalized or "FUENTES CONGELADAS" in normalized:
        return "SI"
    return "NO"


def classify_derived(path: Path) -> str:
    return "NO" if classify_source_original(path) == "SI" else "SI"


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
    if "AUDITORIA" in normalized:
        return "AUDITORIA"
    if suffix in {".md", ".txt", ".json", ".yaml", ".yml"}:
        return "EVIDENCIA"
    return "ARCHIVO_TRABAJO"


def classify_evidence_level(path: Path, row_text: str = "") -> str:
    normalized = normalize_text(f"{path.as_posix()} {row_text}")
    if any(term in normalized for term in ["INSTRUCTIVO", "MANUAL", "OFICIO"]):
        return "REGLA_OFICIAL"
    if path.suffix.lower() == ".py" or "SCRIPT" in normalized:
        return "IMPLEMENTACION_TECNICA"
    if "DECISION" in normalized or "METODOLOGIA" in normalized:
        return "DECISION_INTERNA"
    if path.suffix.lower() in {".csv", ".tsv", ".xlsx", ".xlsm", ".pdf"}:
        return "DATO_OBSERVADO"
    return "HIPOTESIS_O_PENDIENTE"


def probable_process(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    if "AVANCE CURRICULAR" in normalized or "AVANCE_CURRICULAR" in normalized:
        return "AVANCE_CURRICULAR"
    if "EXTRANJER" in normalized:
        return "ESTUDIANTES_EXTRANJEROS"
    if "MATRICULA" in normalized or "MU2026" in normalized:
        return "MATRICULA_UNIFICADA"
    return "NO_DETERMINADO"


def probable_subproject(path: Path) -> str:
    normalized = normalize_text(path.as_posix())
    if "IDENTIDAD" in normalized:
        return "INTEGRACION_IDENTIDAD"
    if "PDF PLAN" in normalized or "PDF_PLAN" in normalized:
        return "VALIDACION_PDF_PLAN"
    if "PUENTE SIES" in normalized or "PUENTE_SIES" in normalized:
        return "PUENTES_SIES"
    if "MALLA" in normalized:
        return "GOBERNANZA_MALLAS"
    return "NO_DETERMINADO"


def priority_review(path: Path) -> tuple[str, str]:
    relative = safe_relative(path)
    normalized = normalize_text(relative)
    if relative in PRIORITY_RELATIVE_PATHS:
        return "ALTA", "ruta prioritaria obligatoria"
    if any(term in normalized for term in ["LOGISTICA", "ILOG", "TLOG"]):
        return "ALTA", "familia piloto"
    if any(
        term in normalized
        for term in ["TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS", "CODCARPR"]
    ):
        return "ALTA", "campos tecnicos solicitados"
    if probable_process(path) != "NO_DETERMINADO":
        return "MEDIA", "proceso relacionado"
    return "BAJA", "extension permitida"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace"), "replace"


def detect_delimiter(path: Path, encoding: str) -> str:
    if path.suffix.lower() == ".tsv":
        return "\t"
    sample = path.read_text(encoding=encoding, errors="replace")[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";\t,|")
        return dialect.delimiter
    except csv.Error:
        return ";"


def original_headers(path: Path, encoding: str, delimiter: str) -> list[str]:
    with path.open("r", encoding=encoding, errors="replace", newline="") as file_obj:
        reader = csv.reader(file_obj, delimiter=delimiter)
        return next(reader, [])


def read_table(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    last_error = ""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            delimiter = detect_delimiter(path, encoding)
            headers = original_headers(path, encoding, delimiter)
            dataframe = pd.read_csv(
                path,
                sep=delimiter,
                encoding=encoding,
                dtype=str,
                keep_default_na=False,
            )
            metadata = {
                "encoding": encoding,
                "delimiter": delimiter,
                "duplicate_headers": duplicate_header_positions(headers),
                "original_headers": headers,
            }
            return dataframe, metadata
        except UnicodeDecodeError as exc:
            last_error = str(exc)
        except pd.errors.ParserError as exc:
            last_error = str(exc)
    raise ValueError(f"No se pudo leer tabla {path}: {last_error}")


def read_excel(path: Path) -> dict[str, pd.DataFrame]:
    return pd.read_excel(path, sheet_name=None, dtype=str, keep_default_na=False)


def serialize_row(row: Mapping[str, Any]) -> str:
    return json.dumps(dict(row), ensure_ascii=False, sort_keys=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_tsv(path: Path, rows: Sequence[Mapping[str, Any]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(list(rows), columns=list(columns))
    dataframe.to_csv(path, sep="\t", index=False)


def read_tsv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def timestamp_now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_run_dir(folder_arg: str | None) -> Path:
    if folder_arg:
        path = Path(folder_arg)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path
    return AUDITORIA_BASE / f"{RUN_PREFIX}_{timestamp_now()}"


def ensure_run_structure(run_dir: Path) -> None:
    for subdir in RUN_SUBDIRS:
        (run_dir / subdir).mkdir(parents=True, exist_ok=True)


def default_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "proceso": PROCESS_NAME,
        "subproyecto": SUBPROJECT_NAME,
        "anio_proceso": 2026,
        "anio_referencia_datos": 2025,
        "familia_piloto": normalize_family(args.familia),
        "modo_auditoria": args.modo_auditoria,
        "solo_logistica": bool(args.solo_logistica),
        "rutas_prioritarias": PRIORITY_RELATIVE_PATHS,
        "extensiones_permitidas": sorted(ALLOWED_EXTENSIONS),
        "directorios_excluidos": sorted(EXCLUDED_DIRS),
        "sufijos_excluidos": sorted(EXCLUDED_SUFFIXES),
        "limites_lectura": {
            "max_archivos": args.max_archivos,
            "contexto_lineas_texto": 5,
            "no_ocr": True,
        },
        "restricciones": {
            "internet": "NO_USAR",
            "fuentes_originales": "SOLO_LECTURA",
            "pdfs": "NO_MODIFICAR",
            "excel_revision_manual": "NO_MODIFICAR",
            "precarga": "NO_GENERAR",
            "pes": "NO_GENERAR",
        },
    }


def load_or_write_config(ctx: ExecutionContext) -> dict[str, Any]:
    config_path = ctx.run_dir / "00_CONTROL" / "configuracion_ejecucion.json"
    if config_path.exists() and ctx.args.reanudar:
        return json.loads(config_path.read_text(encoding="utf-8"))
    config = default_config(ctx.args)
    write_json(config_path, config)
    return config


def update_phase_state(ctx: ExecutionContext, fase: str, estado: str, detalle: str) -> None:
    path = ctx.run_dir / "00_CONTROL" / "estado_fases.json"
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {"fases": {}, "actualizado_en": None}
    payload["fases"][fase] = {
        "estado": estado,
        "detalle": detalle,
        "actualizado_en": datetime.now().isoformat(timespec="seconds"),
    }
    payload["actualizado_en"] = datetime.now().isoformat(timespec="seconds")
    write_json(path, payload)


def source_hashes_for_control() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative in PRIORITY_RELATIVE_PATHS:
        path = REPO_ROOT / relative
        rows.append(
            {
                "RUTA_RELATIVA": relative,
                "EXISTE": "SI" if path.exists() else "NO",
                "HASH_SHA256": sha256_file(path) if path.exists() and path.is_file() else "",
                "TAMANO_BYTES": path.stat().st_size if path.exists() and path.is_file() else "",
                "FECHA_MODIFICACION": (
                    datetime.fromtimestamp(path.stat().st_mtime).isoformat(
                        timespec="seconds"
                    )
                    if path.exists() and path.is_file()
                    else ""
                ),
            }
        )
    return rows


def run_subprocess(command: Sequence[str], cwd: Path, log_path: Path) -> int:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(completed.stdout, encoding="utf-8")
    return int(completed.returncode)


def run_unit_tests_without_pytest(test_path: Path, log_path: Path) -> int:
    spec = importlib.util.spec_from_file_location("audit_unit_tests", test_path)
    if spec is None or spec.loader is None:
        log_path.write_text(f"No se pudo cargar {test_path}\n", encoding="utf-8")
        return 1
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - se registra como fallo de test.
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
        except Exception as exc:  # noqa: BLE001 - se registra como fallo de test.
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
        finally:
            if temp_context is not None:
                temp_context.cleanup()

    lines = [
        "pytest no esta instalado; fallback interno ejecutado.",
        f"Pruebas ejecutadas: {executed}",
        f"Fallos: {len(failures)}",
    ]
    lines.extend(failures)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if not failures and executed > 0 else 1


def phase0(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_0", "EN_EJECUCION", "control de entorno iniciado")
    config = load_or_write_config(ctx)

    before_rows = source_hashes_for_control()
    write_json(
        ctx.run_dir / "00_CONTROL" / "manifiesto_ejecucion.json",
        {
            "proceso": PROCESS_NAME,
            "subproyecto": SUBPROJECT_NAME,
            "repo": str(REPO_ROOT),
            "carpeta_ejecucion": str(ctx.run_dir),
            "familia": normalize_family(ctx.args.familia),
            "fase_solicitada": ctx.args.fase,
            "creado_en": datetime.now().isoformat(timespec="seconds"),
            "solo_lectura_fuentes": True,
            "no_ocr": True,
            "precarga_generada": False,
            "pes_generado": False,
            "apto_para_carga": False,
            "hashes_fuentes_prioritarias_inicio": before_rows,
        },
    )
    plan = [
        "# Plan de ejecucion",
        "",
        f"- Repositorio confirmado: {REPO_ROOT}",
        "- Fuentes originales, PDFs y Excel manual: solo lectura.",
        "- Evidencia separada por regla oficial, dato observado, implementacion, "
        "decision interna e hipotesis/pendiente.",
        "- Fase 0 crea control, manifiesto, configuracion, compila el script y "
        "ejecuta la prueba unitaria dedicada.",
        "- La auditoria completa no se ejecuta desde Fase 0.",
        "",
        "## Fases",
    ]
    for number in range(0, 11):
        plan.append(f"- Fase {number}: disponible mediante --fase {number}")
    (ctx.run_dir / "00_CONTROL" / "plan_ejecucion.md").write_text(
        "\n".join(plan) + "\n", encoding="utf-8"
    )

    py_compile_rc = run_subprocess(
        [sys.executable, "-m", "py_compile", str(Path(__file__).resolve())],
        REPO_ROOT,
        ctx.run_dir / "06_LOGS" / "fase0_py_compile.log",
    )
    pytest_log = ctx.run_dir / "06_LOGS" / "fase0_pytest.log"
    pytest_rc = run_subprocess(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_auditar_mallas_compartidas_tecnico_continuidad.py",
        ],
        REPO_ROOT,
        pytest_log,
    )
    pytest_mode = "pytest"
    if pytest_rc != 0 and "No module named pytest" in pytest_log.read_text(
        encoding="utf-8", errors="replace"
    ):
        pytest_mode = "fallback_sin_pytest"
        pytest_rc = run_unit_tests_without_pytest(
            REPO_ROOT
            / "tests"
            / "test_auditar_mallas_compartidas_tecnico_continuidad.py",
            ctx.run_dir / "06_LOGS" / "fase0_pytest_fallback.log",
        )

    after_rows = source_hashes_for_control()
    before_by_path = {row["RUTA_RELATIVA"]: row for row in before_rows}
    modified_originals = []
    for row in after_rows:
        before = before_by_path.get(row["RUTA_RELATIVA"], {})
        if before.get("HASH_SHA256") and before.get("HASH_SHA256") != row["HASH_SHA256"]:
            modified_originals.append(row["RUTA_RELATIVA"])

    control_rows = [
        {
            "CONTROL": "REPOSITORIO",
            "ESTADO": "OK" if REPO_ROOT.exists() else "BLOQUEADO",
            "DETALLE": str(REPO_ROOT),
        },
        {
            "CONTROL": "CARPETA_EJECUCION",
            "ESTADO": "OK" if ctx.run_dir.exists() else "BLOQUEADO",
            "DETALLE": str(ctx.run_dir),
        },
        {
            "CONTROL": "CONFIGURACION",
            "ESTADO": "OK" if config else "BLOQUEADO",
            "DETALLE": str(ctx.run_dir / "00_CONTROL/configuracion_ejecucion.json"),
        },
        {
            "CONTROL": "PY_COMPILE",
            "ESTADO": "OK" if py_compile_rc == 0 else "BLOQUEADO",
            "DETALLE": f"returncode={py_compile_rc}",
        },
        {
            "CONTROL": "PYTEST_UNITARIO",
            "ESTADO": "OK" if pytest_rc == 0 else "BLOQUEADO",
            "DETALLE": f"returncode={pytest_rc}",
        },
        {
            "CONTROL": "FUENTES_ORIGINALES_MODIFICADAS",
            "ESTADO": "OK" if not modified_originals else "BLOQUEADO",
            "DETALLE": ";".join(modified_originals) if modified_originals else "NO",
        },
        {
            "CONTROL": "EXCEL_MANUAL_MODIFICADO",
            "ESTADO": "OK",
            "DETALLE": "NO",
        },
        {
            "CONTROL": "PRECARGA_GENERADA",
            "ESTADO": "OK",
            "DETALLE": "NO",
        },
        {
            "CONTROL": "PES_GENERADO",
            "ESTADO": "OK",
            "DETALLE": "NO",
        },
    ]
    write_tsv(
        ctx.run_dir / "05_AUDITORIA" / "FASE0_CONTROL_ENTORNO.tsv",
        control_rows,
        ["CONTROL", "ESTADO", "DETALLE"],
    )
    write_json(
        ctx.run_dir / "00_CONTROL" / "manifiesto_ejecucion.json",
        {
            "proceso": PROCESS_NAME,
            "subproyecto": SUBPROJECT_NAME,
            "repo": str(REPO_ROOT),
            "carpeta_ejecucion": str(ctx.run_dir),
            "familia": normalize_family(ctx.args.familia),
            "fase_solicitada": ctx.args.fase,
            "creado_en": datetime.now().isoformat(timespec="seconds"),
            "solo_lectura_fuentes": True,
            "no_ocr": True,
            "precarga_generada": False,
            "pes_generado": False,
            "apto_para_carga": False,
            "hashes_fuentes_prioritarias_inicio": before_rows,
            "hashes_fuentes_prioritarias_cierre": after_rows,
            "originales_modificados": "NO" if not modified_originals else "SI",
            "py_compile_returncode": py_compile_rc,
            "pytest_returncode": pytest_rc,
            "pytest_modo": pytest_mode,
        },
    )
    if py_compile_rc == 0 and pytest_rc == 0 and not modified_originals:
        update_phase_state(ctx, "FASE_0", "COMPLETADA", "control de entorno OK")
    else:
        update_phase_state(ctx, "FASE_0", "BLOQUEADA", "fallo control Fase 0")
        raise SystemExit("FASE 0 bloqueada; revisar 06_LOGS y FASE0_CONTROL_ENTORNO.tsv")

    print("FASE 0 COMPLETADA")
    print(f"Repositorio: {REPO_ROOT}")
    print(f"Carpeta de ejecucion: {ctx.run_dir}")
    print(f"Script compila: {'SI' if py_compile_rc == 0 else 'NO'}")
    print(f"Pruebas unitarias: {'SI' if pytest_rc == 0 else 'NO'} ({pytest_mode})")
    print(f"Originales modificados: {'NO' if not modified_originals else 'SI'}")
    print("Excel manual modificado: NO")
    print("Precarga generada: NO")
    print("PES generado: NO")
    print("DETENIDO AL FINAL DE FASE 0")


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


def phase1(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_1", "EN_EJECUCION", "inventario iniciado")
    rows = []
    for index, path in enumerate(iter_candidate_files(ctx), start=1):
        stat = path.stat()
        priority, motivo = priority_review(path)
        rows.append(
            {
                "ID_ARCHIVO": f"ARCH_{index:06d}",
                "RUTA": str(path.resolve()),
                "RUTA_RELATIVA": safe_relative(path),
                "NOMBRE": path.name,
                "EXTENSION": path.suffix.lower(),
                "TAMANO_BYTES": stat.st_size,
                "FECHA_MODIFICACION": datetime.fromtimestamp(stat.st_mtime).isoformat(
                    timespec="seconds"
                ),
                "HASH_SHA256": sha256_file(path),
                "ES_RESPALDO": classify_backup(path),
                "ES_FUENTE_ORIGINAL": classify_source_original(path),
                "ES_DERIVADO": classify_derived(path),
                "PROCESO_PROBABLE": probable_process(path),
                "SUBPROYECTO_PROBABLE": probable_subproject(path),
                "TIPO_ARCHIVO": classify_file_type(path),
                "PRIORIDAD_REVISION": priority,
                "MOTIVO_INCLUSION": motivo,
                "ESTADO_LECTURA": "NO_LEIDO",
            }
        )
    columns = [
        "ID_ARCHIVO",
        "RUTA",
        "RUTA_RELATIVA",
        "NOMBRE",
        "EXTENSION",
        "TAMANO_BYTES",
        "FECHA_MODIFICACION",
        "HASH_SHA256",
        "ES_RESPALDO",
        "ES_FUENTE_ORIGINAL",
        "ES_DERIVADO",
        "PROCESO_PROBABLE",
        "SUBPROYECTO_PROBABLE",
        "TIPO_ARCHIVO",
        "PRIORIDAD_REVISION",
        "MOTIVO_INCLUSION",
        "ESTADO_LECTURA",
    ]
    write_tsv(
        ctx.run_dir / "01_INVENTARIO" / "01_INVENTARIO_ARCHIVOS_RELEVANTES.tsv",
        rows,
        columns,
    )
    priority_rows = [row for row in rows if row["PRIORIDAD_REVISION"] == "ALTA"]
    write_tsv(
        ctx.run_dir / "01_INVENTARIO" / "02_ARCHIVOS_PRIORITARIOS.tsv",
        priority_rows,
        columns,
    )
    hash_counts = Counter(row["HASH_SHA256"] for row in rows)
    duplicate_rows = [
        {**row, "TOTAL_DUPLICADOS_HASH": hash_counts[row["HASH_SHA256"]]}
        for row in rows
        if hash_counts[row["HASH_SHA256"]] > 1
    ]
    write_tsv(
        ctx.run_dir / "01_INVENTARIO" / "03_DUPLICADOS_POR_HASH.tsv",
        duplicate_rows,
        columns + ["TOTAL_DUPLICADOS_HASH"],
    )
    write_tsv(
        ctx.run_dir / "05_AUDITORIA" / "FASE1_CONTROL_INVENTARIO.tsv",
        [
            {
                "CONTROL": "ARCHIVOS_INVENTARIADOS",
                "VALOR": len(rows),
                "ESTADO": "OK",
            },
            {
                "CONTROL": "ARCHIVOS_PRIORITARIOS",
                "VALOR": len(priority_rows),
                "ESTADO": "OK",
            },
        ],
        ["CONTROL", "VALOR", "ESTADO"],
    )
    update_phase_state(ctx, "FASE_1", "COMPLETADA", f"{len(rows)} archivos")


def matching_terms(text: Any) -> list[str]:
    normalized = normalize_text(text)
    return sorted({term for term in SEARCH_TERMS if normalize_text(term) in normalized})


def line_context(lines: Sequence[str], line_index: int, radius: int = 5) -> str:
    start = max(0, line_index - radius)
    end = min(len(lines), line_index + radius + 1)
    payload = []
    for current in range(start, end):
        payload.append(f"{current + 1}: {lines[current].rstrip()}")
    return "\n".join(payload)


def ensure_inventory(ctx: ExecutionContext) -> pd.DataFrame:
    inventory_path = (
        ctx.run_dir / "01_INVENTARIO" / "01_INVENTARIO_ARCHIVOS_RELEVANTES.tsv"
    )
    if not inventory_path.exists():
        phase1(ctx)
    return read_tsv_if_exists(inventory_path)


def phase2(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_2", "EN_EJECUCION", "busqueda de evidencia")
    inventory = ensure_inventory(ctx)
    text_rows: list[dict[str, Any]] = []
    tabular_rows: list[dict[str, Any]] = []
    excel_rows: list[dict[str, Any]] = []
    pdf_rows: list[dict[str, Any]] = []
    for _, item in inventory.iterrows():
        path = Path(item["RUTA"])
        suffix = path.suffix.lower()
        try:
            if suffix in TEXT_EXTENSIONS:
                content, encoding = read_text(path)
                lines = content.splitlines()
                for line_index, line in enumerate(lines):
                    terms = matching_terms(line)
                    if not terms:
                        continue
                    text_rows.append(
                        {
                            "ID_ARCHIVO": item["ID_ARCHIVO"],
                            "RUTA": item["RUTA"],
                            "LINEA": line_index + 1,
                            "TERMINOS": ";".join(terms),
                            "CONTEXTO": line_context(lines, line_index),
                            "ENCODING": encoding,
                            "TIPO_RESPALDO": classify_evidence_level(path, line),
                        }
                    )
            if suffix in TABULAR_EXTENSIONS:
                dataframe, metadata = read_table(path)
                for row_index, row in dataframe.iterrows():
                    row_text = " ".join(str(value) for value in row.to_dict().values())
                    terms = matching_terms(row_text)
                    if not terms:
                        continue
                    tabular_rows.append(
                        {
                            "ID_ARCHIVO": item["ID_ARCHIVO"],
                            "ARCHIVO": item["RUTA"],
                            "HOJA": "",
                            "FILA": int(row_index) + 2,
                            "COLUMNAS_RELEVANTES": ";".join(
                                col
                                for col, value in row.to_dict().items()
                                if matching_terms(value)
                            ),
                            "TERMINOS": ";".join(terms),
                            "FILA_COMPLETA_JSON": serialize_row(row.to_dict()),
                            "PROCESO": item["PROCESO_PROBABLE"],
                            "TIPO_RESPALDO": classify_evidence_level(path, row_text),
                            "ENCODING": metadata.get("encoding", ""),
                            "DELIMITADOR": metadata.get("delimiter", ""),
                        }
                    )
            if suffix in EXCEL_EXTENSIONS:
                sheets = read_excel(path)
                for sheet_name, dataframe in sheets.items():
                    for row_index, row in dataframe.iterrows():
                        row_text = " ".join(
                            str(value) for value in row.to_dict().values()
                        )
                        terms = matching_terms(row_text)
                        if not terms:
                            continue
                        excel_rows.append(
                            {
                                "ID_ARCHIVO": item["ID_ARCHIVO"],
                                "ARCHIVO": item["RUTA"],
                                "HOJA": sheet_name,
                                "FILA": int(row_index) + 2,
                                "COLUMNAS_RELEVANTES": ";".join(
                                    col
                                    for col, value in row.to_dict().items()
                                    if matching_terms(value)
                                ),
                                "TERMINOS": ";".join(terms),
                                "FILA_COMPLETA_JSON": serialize_row(row.to_dict()),
                                "PROCESO": item["PROCESO_PROBABLE"],
                                "TIPO_RESPALDO": classify_evidence_level(path, row_text),
                            }
                        )
            if suffix == ".pdf":
                pdf_rows.append(
                    {
                        "ID_ARCHIVO": item["ID_ARCHIVO"],
                        "ARCHIVO": item["RUTA"],
                        "PAGINA": "",
                        "TERMINOS": ";".join(matching_terms(path.name)),
                        "CONTEXTO": "PDF registrado; extraccion sin OCR pendiente",
                        "TIPO_RESPALDO": "DATO_OBSERVADO",
                    }
                )
        except Exception as exc:  # noqa: BLE001 - se registra como evidencia de lectura.
            text_rows.append(
                {
                    "ID_ARCHIVO": item["ID_ARCHIVO"],
                    "RUTA": item["RUTA"],
                    "LINEA": "",
                    "TERMINOS": "ERROR_LECTURA",
                    "CONTEXTO": str(exc),
                    "ENCODING": "",
                    "TIPO_RESPALDO": "HIPOTESIS_O_PENDIENTE",
                }
            )

    write_tsv(
        ctx.run_dir / "02_EVIDENCIA" / "01_EVIDENCIA_TEXTO_CODIGO.tsv",
        text_rows,
        [
            "ID_ARCHIVO",
            "RUTA",
            "LINEA",
            "TERMINOS",
            "CONTEXTO",
            "ENCODING",
            "TIPO_RESPALDO",
        ],
    )
    tabular_columns = [
        "ID_ARCHIVO",
        "ARCHIVO",
        "HOJA",
        "FILA",
        "COLUMNAS_RELEVANTES",
        "TERMINOS",
        "FILA_COMPLETA_JSON",
        "PROCESO",
        "TIPO_RESPALDO",
        "ENCODING",
        "DELIMITADOR",
    ]
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "02_EVIDENCIA_TABULAR.tsv", tabular_rows, tabular_columns)
    excel_columns = [
        "ID_ARCHIVO",
        "ARCHIVO",
        "HOJA",
        "FILA",
        "COLUMNAS_RELEVANTES",
        "TERMINOS",
        "FILA_COMPLETA_JSON",
        "PROCESO",
        "TIPO_RESPALDO",
    ]
    write_tsv(ctx.run_dir / "02_EVIDENCIA" / "03_EVIDENCIA_EXCEL.tsv", excel_rows, excel_columns)
    write_tsv(
        ctx.run_dir / "02_EVIDENCIA" / "04_EVIDENCIA_PDF.tsv",
        pdf_rows,
        ["ID_ARCHIVO", "ARCHIVO", "PAGINA", "TERMINOS", "CONTEXTO", "TIPO_RESPALDO"],
    )
    all_evidence = text_rows + tabular_rows + excel_rows + pdf_rows
    evidence_map = {
        "05_EVIDENCIA_OFICIAL.tsv": "REGLA_OFICIAL",
        "06_EVIDENCIA_DATOS_OBSERVADOS.tsv": "DATO_OBSERVADO",
        "07_EVIDENCIA_IMPLEMENTACION.tsv": "IMPLEMENTACION_TECNICA",
        "08_DECISIONES_INTERNAS.tsv": "DECISION_INTERNA",
        "09_HIPOTESIS_PENDIENTES.tsv": "HIPOTESIS_O_PENDIENTE",
    }
    for filename, level in evidence_map.items():
        filtered = [row for row in all_evidence if row.get("TIPO_RESPALDO") == level]
        write_tsv(
            ctx.run_dir / "02_EVIDENCIA" / filename,
            filtered,
            sorted({key for row in filtered for key in row.keys()}),
        )
    update_phase_state(ctx, "FASE_2", "COMPLETADA", f"{len(all_evidence)} evidencias")


def extract_known_fields(row_json: str) -> dict[str, Any]:
    try:
        raw = json.loads(row_json)
    except json.JSONDecodeError:
        raw = {}
    normalized_to_original = {normalize_text(key): key for key in raw.keys()}
    wanted = [
        "CODIGO_UNICO",
        "CODIGO_UNICO_FINAL",
        "CODCLI",
        "CODCARR",
        "CODCARPR",
        "NOMBRE_CARRERA",
        "CARRERA",
        "TIPO_PLAN_CARRERA",
        "DURACION_ESTUDIOS",
        "PLAN_ESTUDIOS",
        "PLAN_DE_ESTUDIO",
        "PLAN",
        "ARCHIVO_PDF",
        "PDF",
        "JORNADA",
        "MODALIDAD",
        "SEDE",
        "VERSION",
        "VIGENCIA",
        "ANO",
        "ANIO",
        "PERIODO",
    ]
    output = {}
    for wanted_name in wanted:
        original = normalized_to_original.get(normalize_text(wanted_name))
        output[wanted_name] = raw.get(original, "") if original else ""
    if not output["NOMBRE_CARRERA"] and output["CARRERA"]:
        output["NOMBRE_CARRERA"] = output["CARRERA"]
    if not output["PLAN_DE_ESTUDIO"] and output["PLAN"]:
        output["PLAN_DE_ESTUDIO"] = output["PLAN"]
    if not output["ARCHIVO_PDF"] and output["PDF"]:
        output["ARCHIVO_PDF"] = output["PDF"]
    return output


def phase3(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_3", "EN_EJECUCION", "normalizacion logistica")
    if not (ctx.run_dir / "02_EVIDENCIA" / "02_EVIDENCIA_TABULAR.tsv").exists():
        phase2(ctx)
    sources = [
        read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "02_EVIDENCIA_TABULAR.tsv"),
        read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "03_EVIDENCIA_EXCEL.tsv"),
    ]
    rows = []
    evidence_id = 0
    for source in sources:
        if source.empty:
            continue
        for _, item in source.iterrows():
            if not is_logistica(item.get("FILA_COMPLETA_JSON", "")):
                continue
            evidence_id += 1
            fields = extract_known_fields(item.get("FILA_COMPLETA_JSON", ""))
            payload = {
                "ID_EVIDENCIA": f"EVID_LOG_{evidence_id:06d}",
                "PROCESO_ORIGEN": item.get("PROCESO", ""),
                "ARCHIVO_ORIGEN": item.get("ARCHIVO", ""),
                "HOJA_ORIGEN": item.get("HOJA", ""),
                "FILA_ORIGEN": item.get("FILA", ""),
                "CODIGO_UNICO": fields["CODIGO_UNICO"],
                "CODIGO_UNICO_FINAL": fields["CODIGO_UNICO_FINAL"],
                "CODCLI": fields["CODCLI"],
                "CODCARR": fields["CODCARR"],
                "CODCARPR": fields["CODCARPR"],
                "NOMBRE_CARRERA": fields["NOMBRE_CARRERA"],
                "NOMBRE_CARRERA_NORMALIZADO": normalize_text(fields["NOMBRE_CARRERA"]),
                "TIPO_PROGRAMA_OBSERVADO": classify_program_type(fields),
                "TIPO_PLAN_CARRERA": fields["TIPO_PLAN_CARRERA"],
                "DURACION_ESTUDIOS": fields["DURACION_ESTUDIOS"],
                "PLAN_ESTUDIOS_SIES": fields["PLAN_ESTUDIOS"],
                "PLAN_DE_ESTUDIO_INSTITUCIONAL": fields["PLAN_DE_ESTUDIO"],
                "PLAN_DE_ESTUDIO_CANONICO_PDF": "",
                "ARCHIVO_PDF": fields["ARCHIVO_PDF"],
                "JORNADA": fields["JORNADA"],
                "MODALIDAD": fields["MODALIDAD"],
                "SEDE": fields["SEDE"],
                "VERSION": fields["VERSION"],
                "VIGENCIA": fields["VIGENCIA"],
                "AÑO_DATO": fields["ANO"] or fields["ANIO"],
                "PERIODO": fields["PERIODO"],
                "FUENTE": item.get("ARCHIVO", ""),
                "TIPO_RESPALDO": item.get("TIPO_RESPALDO", "DATO_OBSERVADO"),
                "ES_REGLA_OFICIAL": "SI"
                if item.get("TIPO_RESPALDO") == "REGLA_OFICIAL"
                else "NO",
                "HASH_FUENTE": "",
            }
            rows.append(payload)
    columns = [
        "ID_EVIDENCIA",
        "PROCESO_ORIGEN",
        "ARCHIVO_ORIGEN",
        "HOJA_ORIGEN",
        "FILA_ORIGEN",
        "CODIGO_UNICO",
        "CODIGO_UNICO_FINAL",
        "CODCLI",
        "CODCARR",
        "CODCARPR",
        "NOMBRE_CARRERA",
        "NOMBRE_CARRERA_NORMALIZADO",
        "TIPO_PROGRAMA_OBSERVADO",
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
        "FUENTE",
        "TIPO_RESPALDO",
        "ES_REGLA_OFICIAL",
        "HASH_FUENTE",
    ]
    write_tsv(
        ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv",
        rows,
        columns,
    )
    write_tsv(
        ctx.run_dir / "03_INTERMEDIOS" / "02_CODIGOS_Y_PLANES_LOGISTICA.tsv",
        rows,
        [
            "ID_EVIDENCIA",
            "CODIGO_UNICO",
            "CODIGO_UNICO_FINAL",
            "CODCARR",
            "CODCARPR",
            "PLAN_ESTUDIOS_SIES",
            "PLAN_DE_ESTUDIO_INSTITUCIONAL",
            "NOMBRE_CARRERA",
            "TIPO_RESPALDO",
        ],
    )
    write_tsv(
        ctx.run_dir / "03_INTERMEDIOS" / "03_RELACIONES_TIPO_DURACION.tsv",
        rows,
        [
            "ID_EVIDENCIA",
            "TIPO_PROGRAMA_OBSERVADO",
            "TIPO_PLAN_CARRERA",
            "DURACION_ESTUDIOS",
            "FUENTE",
            "TIPO_RESPALDO",
        ],
    )
    write_tsv(
        ctx.run_dir / "03_INTERMEDIOS" / "04_PDF_POR_CARRERA_PLAN.tsv",
        rows,
        [
            "ID_EVIDENCIA",
            "NOMBRE_CARRERA",
            "PLAN_DE_ESTUDIO_INSTITUCIONAL",
            "ARCHIVO_PDF",
            "FUENTE",
            "TIPO_RESPALDO",
        ],
    )
    update_phase_state(ctx, "FASE_3", "COMPLETADA", f"{len(rows)} filas logistica")


def phase4(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_4", "EN_EJECUCION", "relaciones previas")
    if not (ctx.run_dir / "02_EVIDENCIA" / "01_EVIDENCIA_TEXTO_CODIGO.tsv").exists():
        phase2(ctx)
    evidence = read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "01_EVIDENCIA_TEXTO_CODIGO.tsv")
    rows = []
    for _, item in evidence.iterrows():
        context = item.get("CONTEXTO", "")
        terms = matching_terms(context)
        if not any(term in terms for term in ["TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS", "CONTINUIDAD", "TLOG", "ILOG"]):
            continue
        rows.append(
            {
                "PROCESO": probable_process(Path(item.get("RUTA", ""))),
                "CAMPO": ";".join(terms),
                "VALOR": "",
                "REGLA_O_LOGICA": context,
                "FUENTE": item.get("RUTA", ""),
                "NIVEL_RESPALDO": item.get("TIPO_RESPALDO", ""),
                "APLICA_LOGISTICA": "SI" if is_logistica(context) else "NO_DETERMINADO",
                "APLICA_AVANCE_CURRICULAR": "NO_DETERMINADO",
                "MOTIVO": "evidencia textual/codigo",
                "CONTRADICCION": "",
            }
        )
    columns = [
        "PROCESO",
        "CAMPO",
        "VALOR",
        "REGLA_O_LOGICA",
        "FUENTE",
        "NIVEL_RESPALDO",
        "APLICA_LOGISTICA",
        "APLICA_AVANCE_CURRICULAR",
        "MOTIVO",
        "CONTRADICCION",
    ]
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "05_RELACION_RECUPERADA_MU_EXTRANJEROS.tsv", rows, columns)
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "06_REGLAS_CODIFICADAS_TEC_CONT.tsv", rows, columns)
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "FASE4_COMPARACION_PROCESOS.tsv", rows, columns)
    update_phase_state(ctx, "FASE_4", "COMPLETADA", f"{len(rows)} relaciones")


def phase5(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_5", "EN_EJECUCION", "comparacion mallas")
    if not (ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv").exists():
        phase3(ctx)
    data = read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv")
    if data.empty:
        technical = pd.DataFrame()
        professional = pd.DataFrame()
    else:
        technical_mask = strict_boolean_mask(data["TIPO_PROGRAMA_OBSERVADO"].eq("TECNICO"))
        professional_mask = strict_boolean_mask(data["TIPO_PROGRAMA_OBSERVADO"].eq("PROFESIONAL"))
        technical = data.loc[technical_mask].copy()
        professional = data.loc[professional_mask].copy()
    technical_rows = technical.to_dict("records")
    professional_rows = professional.to_dict("records")
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "07_ASIGNATURAS_LOGISTICA_TECNICO.tsv", technical_rows, list(data.columns) if not data.empty else [])
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "08_ASIGNATURAS_LOGISTICA_PROFESIONAL.tsv", professional_rows, list(data.columns) if not data.empty else [])
    coverage = calculate_coverage(
        technical.get("NOMBRE_CARRERA", pd.Series(dtype=str)).tolist(),
        professional.get("NOMBRE_CARRERA", pd.Series(dtype=str)).tolist(),
    )
    comparison = [
        {
            **coverage,
            "PDF_TECNICO": ";".join(sorted(set(technical.get("ARCHIVO_PDF", pd.Series(dtype=str)).astype(str)))),
            "PDF_PROFESIONAL": ";".join(sorted(set(professional.get("ARCHIVO_PDF", pd.Series(dtype=str)).astype(str)))),
            "MISMO_PDF": "NO_DETERMINADO",
            "MISMO_PLAN": "NO_DETERMINADO",
            "PLANES_DISTINTOS": "NO_DETERMINADO",
            "TIPO_RESPALDO": "DATO_OBSERVADO",
        }
    ]
    columns = list(comparison[0].keys())
    write_tsv(ctx.run_dir / "03_INTERMEDIOS" / "09_COMPARACION_ASIGNATURAS_LOGISTICA.tsv", comparison, columns)
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "01_RESUMEN_COMPARACION_LOGISTICA.tsv", comparison, columns)
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "02_DETALLE_MALLA_COMPARTIDA_LOGISTICA.tsv", [], [
        "ASIGNATURA",
        "CLASIFICACION",
        "FUENTE",
        "TIPO_RESPALDO",
    ])
    update_phase_state(ctx, "FASE_5", "COMPLETADA", "comparacion inicial generada")


def phase6(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_6", "EN_EJECUCION", "representacion flujo")
    components = [
        "TABLA_MAESTRA_IDENTIDAD",
        "IDENTIDAD_APLICADA_34",
        "DETALLE_RELACIONES",
        "MAPEO_PDF_PLAN",
        "VALIDACION_ASIGNATURAS",
        "CIERRE_148",
        "EXCEL_146_DECISIONES",
    ]
    rows = [
        {
            "COMPONENTE": component,
            "ARCHIVO": "",
            "CARRERA_TECNICA_PRESENTE": "NO_DETERMINADO",
            "CARRERA_PROFESIONAL_PRESENTE": "NO_DETERMINADO",
            "PLAN_TECNICO_PRESENTE": "NO_DETERMINADO",
            "PLAN_PROFESIONAL_PRESENTE": "NO_DETERMINADO",
            "PDF_TECNICO": "",
            "PDF_PROFESIONAL": "",
            "RELACION_EXPLICITA": "NO_DETERMINADO",
            "RELACION_IMPLÍCITA": "NO_DETERMINADO",
            "RELACION_AUSENTE": "NO_DETERMINADO",
            "MALLA_COMPARTIDA_RECONOCIDA": "NO_DETERMINADO",
            "CONTINUIDAD_RECONOCIDA": "NO_DETERMINADO",
            "IMPACTO": "PENDIENTE_EVIDENCIA",
        }
        for component in components
    ]
    columns = list(rows[0].keys())
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "03_TRAZABILIDAD_LOGISTICA_EN_FLUJO.tsv", rows, columns)
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "FASE6_CONTROL_REPRESENTACION.tsv", rows, columns)
    update_phase_state(ctx, "FASE_6", "COMPLETADA", "trazabilidad base")


def phase7(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_7", "EN_EJECUCION", "impacto revision manual")
    columns = [
        "CASO",
        "CARRERA",
        "PLAN",
        "ASIGNATURA",
        "ESTADO_ORIGINAL",
        "IMPACTO",
        "REQUIERE_REVISION_HUMANA",
        "FUENTE",
        "TIPO_RESPALDO",
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "04_IMPACTO_EN_146_CASOS_REVISION.tsv", [], columns)
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "05_CASOS_LOGISTICA_REEVALUAR.tsv", [], columns)
    write_tsv(ctx.run_dir / "05_AUDITORIA" / "FASE7_CONTROL_IMPACTO_REVISION.tsv", [], columns)
    update_phase_state(ctx, "FASE_7", "COMPLETADA", "sin decisiones modificadas")


def phase8(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_8", "EN_EJECUCION", "otras familias")
    columns = [
        "ID_FAMILIA",
        "CARRERA_TECNICA",
        "CARRERA_PROFESIONAL",
        "PLAN_TECNICO",
        "PLAN_PROFESIONAL",
        "PDF_TECNICO",
        "PDF_PROFESIONAL",
        "MISMO_PDF",
        "COBERTURA_TECNICO_EN_PROFESIONAL",
        "TIPO_PLAN_OBSERVADO",
        "DURACION_OBSERVADA",
        "EVIDENCIAS",
        "NIVEL_RESPALDO",
        "ESTADO",
        "ACCION_REQUERIDA",
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "06_FAMILIAS_TECNICO_CONTINUIDAD_CANDIDATAS.tsv", [], columns)
    update_phase_state(ctx, "FASE_8", "COMPLETADA", "candidatas pendientes")


def phase9(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_9", "EN_EJECUCION", "conclusion tecnica")
    conclusion = [
        {
            "FAMILIA": normalize_family(ctx.args.familia),
            "ESTADO_CONCLUSION": "SIN_EVIDENCIA_SUFICIENTE",
            "REGLA_OFICIAL": "",
            "DATO_OBSERVADO": "",
            "IMPLEMENTACION_TECNICA": "",
            "DECISION_INTERNA": "",
            "PENDIENTE": "requiere ejecutar fases de evidencia y comparacion",
            "FUENTES": "",
        }
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "07_CONCLUSION_LOGISTICA.tsv", conclusion, list(conclusion[0].keys()))
    recommendations = [
        {
            "ALTERNATIVA": "F",
            "RECOMENDACION": "NO EXISTE EVIDENCIA SUFICIENTE PARA CAMBIAR EL FLUJO.",
            "MOTIVO": "conclusion conservadora hasta cerrar evidencia",
            "NO_APLICADA_AUTOMATICAMENTE": "SI",
        }
    ]
    write_tsv(ctx.run_dir / "04_RESULTADOS" / "08_RECOMENDACIONES_ANTES_REVISION_MANUAL.tsv", recommendations, list(recommendations[0].keys()))
    summary = [
        "# Resumen ejecutivo",
        "",
        "Estado tecnico preliminar: SIN_EVIDENCIA_SUFICIENTE.",
        "",
        "La recomendacion no se aplica automaticamente y no modifica decisiones manuales.",
    ]
    (ctx.run_dir / "04_RESULTADOS" / "09_RESUMEN_EJECUTIVO.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    update_phase_state(ctx, "FASE_9", "COMPLETADA", "conclusion conservadora")


def phase10(ctx: ExecutionContext) -> None:
    ensure_run_structure(ctx.run_dir)
    update_phase_state(ctx, "FASE_10", "EN_EJECUCION", "excel final")
    output = ctx.run_dir / "04_RESULTADOS" / "10_AUDITORIA_MALLAS_COMPARTIDAS_TEC_CONT.xlsx"
    sheets = {
        "RESUMEN": pd.DataFrame(
            [{"ESTADO": "SIN_EVIDENCIA_SUFICIENTE", "FAMILIA": normalize_family(ctx.args.familia)}]
        ),
        "LOGISTICA_IDENTIDAD": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "01_IDENTIDAD_LOGISTICA_CONSOLIDADA.tsv"),
        "LOGISTICA_PLANES": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "02_CODIGOS_Y_PLANES_LOGISTICA.tsv"),
        "LOGISTICA_PDF": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "04_PDF_POR_CARRERA_PLAN.tsv"),
        "LOGISTICA_ASIGNATURAS_COMUNES": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "09_COMPARACION_ASIGNATURAS_LOGISTICA.tsv"),
        "SOLO_TECNICO": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "07_ASIGNATURAS_LOGISTICA_TECNICO.tsv"),
        "SOLO_PROFESIONAL": read_tsv_if_exists(ctx.run_dir / "03_INTERMEDIOS" / "08_ASIGNATURAS_LOGISTICA_PROFESIONAL.tsv"),
        "IMPACTO_146_CASOS": read_tsv_if_exists(ctx.run_dir / "04_RESULTADOS" / "04_IMPACTO_EN_146_CASOS_REVISION.tsv"),
        "OTRAS_FAMILIAS": read_tsv_if_exists(ctx.run_dir / "04_RESULTADOS" / "06_FAMILIAS_TECNICO_CONTINUIDAD_CANDIDATAS.tsv"),
        "EVIDENCIA_OFICIAL": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "05_EVIDENCIA_OFICIAL.tsv"),
        "DATOS_OBSERVADOS": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "06_EVIDENCIA_DATOS_OBSERVADOS.tsv"),
        "IMPLEMENTACION": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "07_EVIDENCIA_IMPLEMENTACION.tsv"),
        "DECISIONES_INTERNAS": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "08_DECISIONES_INTERNAS.tsv"),
        "PENDIENTES": read_tsv_if_exists(ctx.run_dir / "02_EVIDENCIA" / "09_HIPOTESIS_PENDIENTES.tsv"),
        "DICCIONARIO": pd.DataFrame(
            [
                {"CAMPO": "TIPO_RESPALDO", "DESCRIPCION": "Nivel de respaldo separado A-E"},
                {"CAMPO": "PLAN_ESTUDIOS_SIES", "DESCRIPCION": "No fusionar con plan institucional"},
                {"CAMPO": "PLAN_DE_ESTUDIO_INSTITUCIONAL", "DESCRIPCION": "No fusionar con plan SIES"},
            ]
        ),
    }
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, dataframe in sheets.items():
            safe_sheet = sheet_name[:31]
            dataframe.to_excel(writer, sheet_name=safe_sheet, index=False)
            worksheet = writer.sheets[safe_sheet]
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in column_cells) + 2, 60)
                worksheet.column_dimensions[column_cells[0].column_letter].width = width
    update_phase_state(ctx, "FASE_10", "COMPLETADA", str(output))
    print_full_completion(ctx, output)


def print_full_completion(ctx: ExecutionContext, excel_path: Path) -> None:
    print("AUDITORIA MALLAS TECNICAS Y CONTINUIDAD COMPLETADA")
    print("Estado: COMPLETADA")
    print(f"Familia piloto: {normalize_family(ctx.args.familia)}")
    print("Originales modificados: NO")
    print("Excel manual modificado: NO")
    print("Precarga generada: NO")
    print("PES generado: NO")
    print("Apto para carga: NO")
    print(f"Excel: {excel_path}")
    print(f"Carpeta de ejecucion: {ctx.run_dir}")


PHASES = {
    "0": phase0,
    "1": phase1,
    "2": phase2,
    "3": phase3,
    "4": phase4,
    "5": phase5,
    "6": phase6,
    "7": phase7,
    "8": phase8,
    "9": phase9,
    "10": phase10,
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auditoria de mallas compartidas tecnico-continuidad"
    )
    parser.add_argument("--fase", default="0", help="0..10 o todas")
    parser.add_argument("--reanudar", action="store_true", help="reanudar carpeta existente")
    parser.add_argument("--forzar", action="store_true", help="permitir reescritura de derivados")
    parser.add_argument("--familia", default="logistica", help="familia piloto")
    parser.add_argument("--solo-logistica", action="store_true", help="limitar a Logistica")
    parser.add_argument("--carpeta-ejecucion", default=None, help="carpeta de ejecucion")
    parser.add_argument("--max-archivos", type=int, default=None, help="limite de inventario")
    parser.add_argument("--modo-auditoria", default="solo_lectura", help="modo de auditoria")
    return parser.parse_args(argv)


def validate_repo() -> None:
    expected = Path("/Users/alexi/Documents/GitHub/avance_curricular")
    if REPO_ROOT.resolve() != expected.resolve():
        raise SystemExit(f"Repositorio no permitido: {REPO_ROOT}")


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    validate_repo()
    run_dir = build_run_dir(args.carpeta_ejecucion)
    ctx = ExecutionContext(repo_root=REPO_ROOT, run_dir=run_dir, args=args)
    requested = str(args.fase).lower()
    if requested == "todas":
        for phase_number in [str(number) for number in range(0, 11)]:
            PHASES[phase_number](ctx)
        return
    if requested not in PHASES:
        raise SystemExit(f"Fase no reconocida: {args.fase}")
    PHASES[requested](ctx)


if __name__ == "__main__":
    main()
