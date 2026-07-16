"""Lectura gobernada de archivos oficiales y archivos anuales academicos."""

from __future__ import annotations

import csv
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd


@dataclass(frozen=True)
class AcademicDataset:
    """Representa un archivo academico leido y su perfil fisico."""

    frame: pd.DataFrame
    path: Path
    delimiter: str
    encoding: str
    has_header: bool
    rows: int
    columns: int
    expected_columns: int
    file_sha256: str
    field_count_errors: tuple[dict[str, object], ...]


def sha256_file(path: Path) -> str:
    """Calcula el hash SHA256 de un archivo sin modificarlo."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_first_line(path: Path, encodings: Sequence[str]) -> tuple[str, str]:
    """Lee la primera linea disponible probando encodings conocidos."""

    last_error: UnicodeDecodeError | None = None
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return handle.readline().rstrip("\r\n"), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise ValueError(f"No se pudo leer el archivo: {path}")


def detect_delimiter(first_line: str) -> str:
    """Detecta un delimitador simple a partir de la primera linea."""

    candidates = [";", "\t", ","]
    counts = {candidate: first_line.count(candidate) for candidate in candidates}
    return max(counts, key=counts.get)


def parse_line(line: str, delimiter: str) -> list[str]:
    """Parsea una linea CSV usando el delimitador indicado."""

    return next(csv.reader([line], delimiter=delimiter))


def read_official_headers(structure_path: Path) -> list[str]:
    """Lee los encabezados oficiales desde una estructura SIES CSV."""

    first_line, _encoding = read_first_line(structure_path, ["utf-8-sig", "cp1252", "latin1"])
    delimiter = detect_delimiter(first_line)
    return [value.strip() for value in parse_line(first_line, delimiter)]


def normalize_row_length(row: list[str], expected_columns: int) -> list[str]:
    """Ajusta una fila al largo esperado para permitir validacion no bloqueante."""

    if len(row) < expected_columns:
        return row + [""] * (expected_columns - len(row))
    if len(row) > expected_columns:
        return row[:expected_columns]
    return row


def read_rows_with_profile(
    path: Path,
    delimiter: str,
    encoding: str,
    expected_columns: int,
    has_header: bool,
) -> tuple[list[list[str]], tuple[dict[str, object], ...]]:
    """Lee filas y registra diferencias de cantidad de columnas sin detener."""

    rows: list[list[str]] = []
    field_errors: list[dict[str, object]] = []
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for line_number, row in enumerate(reader, start=1):
            if line_number == 1 and has_header:
                continue
            if len(row) != expected_columns:
                field_errors.append(
                    {
                        "linea": line_number,
                        "columnas_observadas": len(row),
                        "columnas_esperadas": expected_columns,
                    }
                )
            rows.append(normalize_row_length([str(value) for value in row], expected_columns))
    return rows, tuple(field_errors)


def detect_header(first_values: Sequence[str], official_headers: Sequence[str]) -> bool:
    """Determina si la primera fila corresponde al encabezado oficial."""

    normalized_first = [value.strip() for value in first_values]
    normalized_official = [value.strip() for value in official_headers]
    return normalized_first == normalized_official


def read_academic_file(
    path: Path,
    official_headers: Sequence[str],
    logger: logging.Logger,
    encodings: Sequence[str] | None = None,
) -> AcademicDataset:
    """Lee un archivo anual con o sin encabezado y aplica la estructura oficial."""

    encoding_candidates = encodings or ["utf-8-sig", "cp1252", "latin1"]
    first_line, encoding = read_first_line(path, encoding_candidates)
    delimiter = detect_delimiter(first_line)
    first_values = parse_line(first_line, delimiter)
    has_header = detect_header(first_values, official_headers)
    rows, field_errors = read_rows_with_profile(
        path=path,
        delimiter=delimiter,
        encoding=encoding,
        expected_columns=len(official_headers),
        has_header=has_header,
    )
    frame = pd.DataFrame(rows, columns=list(official_headers), dtype=str)
    frame = frame.fillna("")
    logger.info(
        "Archivo leido: %s filas=%s columnas=%s header=%s delimiter=%r encoding=%s",
        path,
        len(frame),
        len(frame.columns),
        has_header,
        delimiter,
        encoding,
    )
    return AcademicDataset(
        frame=frame,
        path=path,
        delimiter=delimiter,
        encoding=encoding,
        has_header=has_header,
        rows=len(frame),
        columns=len(frame.columns),
        expected_columns=len(official_headers),
        file_sha256=sha256_file(path),
        field_count_errors=field_errors,
    )
