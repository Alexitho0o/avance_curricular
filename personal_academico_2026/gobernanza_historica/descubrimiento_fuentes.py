"""Descubrimiento no destructivo de fuentes historicas institucionales."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime
from pathlib import Path


CANDIDATE_EXTENSIONS = {".csv", ".txt", ".xlsx", ".xls"}


def normalize_text(value: object) -> str:
    """Normaliza texto para comparaciones insensibles a acentos."""

    text = "" if value is None else str(value)
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return without_marks.upper()


def infer_year_from_text(text: object) -> int | None:
    """Extrae un anio 20xx razonable desde un texto."""

    matches = re.findall(r"20[0-9]{2}", str(text))
    for match in matches:
        year = int(match)
        if 2000 <= year <= 2099:
            return year
    return None


def infer_year_from_path(path: Path, root: Path) -> int | None:
    """Infiere anio desde componentes de una ruta relativa."""

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
    """Lista candidatos tabulares permitidos sin modificar la fuente."""

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in CANDIDATE_EXTENSIONS
    )


def sha256_file(path: Path) -> str:
    """Calcula SHA256 de un archivo."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_from_timestamp(value: float) -> str:
    """Convierte timestamp local a ISO sin microsegundos."""

    return datetime.fromtimestamp(value).replace(microsecond=0).isoformat()


def relative_path(path: Path, root: Path) -> str:
    """Devuelve ruta relativa estable cuando es posible."""

    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
