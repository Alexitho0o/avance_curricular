"""Descubrimiento, inventario y perfilado de fuentes historicas."""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

import pandas as pd

from .lectura import detect_delimiter, parse_line, read_first_line, sha256_file


CANDIDATE_EXTENSIONS = {
    ".csv",
    ".txt",
    ".xlsx",
    ".xls",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}


@dataclass(frozen=True)
class SourceProfile:
    """Perfil no destructivo de una fuente historica candidata."""

    fuente_id: str
    path: Path
    relative_path: str
    name: str
    extension: str
    size_bytes: int
    created_at: str
    modified_at: str
    sha256: str
    year_from_path: int | None
    year_from_name: int | None
    year_from_content: int | None
    encoding: str
    delimiter: str
    has_header: bool
    sheet_count: int
    sheet_names: str
    selected_sheet: str
    column_count: int
    column_names: str
    physical_rows: int
    data_rows: int
    preliminary_classification: str
    evidence_pes: str
    evidence_finalized: str
    evidence_error: str
    observations: str


def normalize_text(value: object) -> str:
    """Normaliza texto para busquedas insensibles a acentos."""

    text = "" if value is None else str(value)
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return without_marks.upper()


def infer_year_from_text(text: str) -> int | None:
    """Infiere el primer anio 20xx razonable contenido en un texto."""

    matches = re.findall(r"20[0-9]{2}", text)
    if not matches:
        return None
    years = [int(match) for match in matches if 2000 <= int(match) <= 2099]
    return years[0] if years else None


def infer_year_from_path(path: Path, root: Path) -> int | None:
    """Infiere anio desde los componentes relativos de una ruta."""

    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    for part in parts:
        year = infer_year_from_text(part)
        if year is not None:
            return year
    return None


def discover_candidate_files(root: Path) -> list[Path]:
    """Lista recursivamente fuentes candidatas sin modificar archivos."""

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in CANDIDATE_EXTENSIONS
    )


def datetime_from_timestamp(value: float) -> str:
    """Convierte un timestamp local a texto ISO sin microsegundos."""

    return datetime.fromtimestamp(value).replace(microsecond=0).isoformat()


def looks_like_header(values: Sequence[str], official_headers: Sequence[str]) -> bool:
    """Evalua si una fila parece encabezado academico."""

    normalized = [normalize_text(value) for value in values]
    official = {normalize_text(value) for value in official_headers}
    score = sum(1 for value in normalized if value in official)
    return "TIPO_DOCUMENTO" in normalized or score >= 5


def header_score(values: Sequence[str], official_headers: Sequence[str]) -> int:
    """Puntua una lista de columnas por similitud con encabezados oficiales."""

    official = {normalize_text(value) for value in official_headers}
    normalized = [normalize_text(value) for value in values]
    return sum(1 for value in normalized if value in official)


def text_profile(path: Path, official_headers: Sequence[str]) -> dict[str, object]:
    """Perfila un archivo de texto o CSV sin cargarlo como fuente oficial."""

    try:
        first_line, encoding = read_first_line(path, ["utf-8-sig", "cp1252", "latin1"])
    except UnicodeDecodeError:
        return {
            "encoding": "NO_DETERMINADO",
            "delimiter": "",
            "has_header": False,
            "column_count": 0,
            "column_names": "",
            "physical_rows": 0,
            "data_rows": 0,
            "year_from_content": None,
            "observations": "No se pudo decodificar como texto tabular.",
        }
    delimiter = detect_delimiter(first_line)
    first_values = parse_line(first_line, delimiter) if first_line else []
    has_header = looks_like_header(first_values, official_headers)
    physical_rows = 0
    with path.open("r", encoding=encoding, errors="replace", newline="") as handle:
        for _row in csv.reader(handle, delimiter=delimiter):
            physical_rows += 1
    column_names = first_values if has_header else []
    content_year = infer_year_from_text(first_line)
    return {
        "encoding": encoding,
        "delimiter": delimiter,
        "has_header": has_header,
        "column_count": len(first_values),
        "column_names": ";".join(str(value) for value in column_names),
        "physical_rows": physical_rows,
        "data_rows": max(physical_rows - 1, 0) if has_header else physical_rows,
        "year_from_content": content_year,
        "observations": "",
    }


def excel_profile(path: Path, official_headers: Sequence[str]) -> dict[str, object]:
    """Perfila un archivo Excel e identifica la hoja mas plausible."""

    try:
        workbook = pd.ExcelFile(path)
    except Exception as exc:  # noqa: BLE001
        return {
            "encoding": "BINARIO",
            "delimiter": "",
            "has_header": False,
            "sheet_count": 0,
            "sheet_names": "",
            "selected_sheet": "",
            "column_count": 0,
            "column_names": "",
            "physical_rows": 0,
            "data_rows": 0,
            "year_from_content": None,
            "observations": f"No se pudo abrir Excel: {type(exc).__name__}",
        }
    best_sheet = ""
    best_columns: list[str] = []
    best_rows = 0
    best_score = -1
    for sheet in workbook.sheet_names:
        try:
            sample = pd.read_excel(path, sheet_name=sheet, nrows=10, dtype=str)
        except Exception:
            continue
        score = header_score([str(column) for column in sample.columns], official_headers)
        if score > best_score:
            best_score = score
            best_sheet = sheet
            best_columns = [str(column) for column in sample.columns]
            try:
                best_rows = len(pd.read_excel(path, sheet_name=sheet, dtype=str))
            except Exception:
                best_rows = len(sample)
    content_year = infer_year_from_text(" ".join([best_sheet, " ".join(best_columns)]))
    return {
        "encoding": "BINARIO_EXCEL",
        "delimiter": "",
        "has_header": bool(best_columns),
        "sheet_count": len(workbook.sheet_names),
        "sheet_names": ";".join(workbook.sheet_names),
        "selected_sheet": best_sheet,
        "column_count": len(best_columns),
        "column_names": ";".join(best_columns),
        "physical_rows": best_rows,
        "data_rows": best_rows,
        "year_from_content": content_year,
        "observations": "" if best_score > 0 else "No se detectaron encabezados academicos en hojas muestreadas.",
    }


def evidence_flags(path: Path) -> tuple[str, str, str]:
    """Detecta evidencias textuales de PES, finalizacion y errores."""

    text = normalize_text(path.as_posix())
    evidence_pes = "SI" if any(token in text for token in ["PES", "CARGA", "ENVIADO", "ENVIADOS", "SIES"]) else "NO"
    evidence_finalized = "SI" if any(token in text for token in ["FINALIZADO", "OFICIAL", "PES_READY", "VF"]) else "NO"
    evidence_error = "SI" if any(token in text for token in ["PROBLEMA", "ERROR", "ERRORES", "FALTANTE"]) else "NO"
    return evidence_pes, evidence_finalized, evidence_error


def preliminary_classification(path: Path, profile: dict[str, object]) -> str:
    """Clasifica preliminarmente una fuente sin descartarla del inventario."""

    text = normalize_text(path.as_posix())
    if "ESTRUCTURA" in text and int(profile.get("data_rows", 0) or 0) <= 1:
        return "ESTRUCTURA_VACIA"
    if "INSTRUCTIVO" in text or path.suffix.lower() in {".zip", ".rar", ".7z", ".tar", ".gz"}:
        return "ARCHIVO_NO_APTO"
    if "PROBLEMA" in text or "ERROR" in text or path.suffix.lower() == ".txt":
        return "REPORTE_ERROR_PES"
    if "PAC_WEB" in text or "BASE DE DATOS" in text:
        return "CONSULTA_PES"
    if "BACKUP" in text or "RESPALDO" in text:
        return "POSIBLE_RESPALDO"
    columns = normalize_text(profile.get("column_names", ""))
    if "PES_READY" in text or "CARGA_IPSSVF" in text or "OFICIAL" in text:
        return "POSIBLE_ARCHIVO_ENVIADO"
    if "TIPO_DOCUMENTO" in columns and "NUM_DOCUMENTO" in columns:
        return "CANDIDATO_OFICIAL"
    return "NO_DETERMINABLE"


def profile_source(path: Path, root: Path, official_headers: Sequence[str], index: int) -> SourceProfile:
    """Construye el perfil de inventario para un archivo historico."""

    stat = path.stat()
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        profile = text_profile(path, official_headers)
    elif suffix in {".xlsx", ".xls"}:
        profile = excel_profile(path, official_headers)
    else:
        profile = {
            "encoding": "BINARIO",
            "delimiter": "",
            "has_header": False,
            "sheet_count": 0,
            "sheet_names": "",
            "selected_sheet": "",
            "column_count": 0,
            "column_names": "",
            "physical_rows": 0,
            "data_rows": 0,
            "year_from_content": None,
            "observations": "Archivo comprimido o no tabular; no se descomprime automaticamente.",
        }
    evidence_pes, evidence_finalized, evidence_error = evidence_flags(path)
    rel_path = path.relative_to(root).as_posix()
    classification = preliminary_classification(path, profile)
    return SourceProfile(
        fuente_id=f"FUENTE_{index:04d}",
        path=path,
        relative_path=rel_path,
        name=path.name,
        extension=suffix,
        size_bytes=stat.st_size,
        created_at=datetime_from_timestamp(stat.st_ctime),
        modified_at=datetime_from_timestamp(stat.st_mtime),
        sha256=sha256_file(path),
        year_from_path=infer_year_from_path(path, root),
        year_from_name=infer_year_from_text(path.name),
        year_from_content=profile.get("year_from_content"),
        encoding=str(profile.get("encoding", "")),
        delimiter=str(profile.get("delimiter", "")),
        has_header=bool(profile.get("has_header", False)),
        sheet_count=int(profile.get("sheet_count", 0) or 0),
        sheet_names=str(profile.get("sheet_names", "")),
        selected_sheet=str(profile.get("selected_sheet", "")),
        column_count=int(profile.get("column_count", 0) or 0),
        column_names=str(profile.get("column_names", "")),
        physical_rows=int(profile.get("physical_rows", 0) or 0),
        data_rows=int(profile.get("data_rows", 0) or 0),
        preliminary_classification=classification,
        evidence_pes=evidence_pes,
        evidence_finalized=evidence_finalized,
        evidence_error=evidence_error,
        observations=str(profile.get("observations", "")),
    )


def inventory_sources(root: Path, official_headers: Sequence[str]) -> pd.DataFrame:
    """Genera el inventario historico completo de fuentes candidatas."""

    profiles = [
        profile_source(path, root, official_headers, index)
        for index, path in enumerate(discover_candidate_files(root), start=1)
    ]
    return pd.DataFrame([profile.__dict__ | {"path": str(profile.path)} for profile in profiles])
