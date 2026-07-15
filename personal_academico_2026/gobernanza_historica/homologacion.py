"""Homologacion explicita de columnas historicas."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Sequence

import pandas as pd

from .inventario import detect_delimiter, has_header, parse_line, read_first_line


def normalize_header(value: object) -> str:
    """Normaliza encabezado para comparacion controlada."""

    text = "" if value is None else str(value).strip().upper()
    text = re.sub(r"[^A-Z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def read_official_headers(structure_path: Path) -> list[str]:
    """Lee encabezados oficiales desde estructura 2026 local."""

    first_line, _encoding = read_first_line(structure_path)
    delimiter = detect_delimiter(first_line)
    return [value.strip() for value in parse_line(first_line, delimiter)]


def read_source_frame(path: Path, official_headers: Sequence[str], sheet_name: str = "") -> tuple[pd.DataFrame, dict[str, object]]:
    """Lee una fuente gobernada preservando columnas originales."""

    if path.suffix.lower() in {".xlsx", ".xls"}:
        sheet = sheet_name or 0
        frame = pd.read_excel(path, sheet_name=sheet, dtype=str, keep_default_na=False).fillna("")
        return frame, {"tipo": "excel", "hoja": sheet_name, "encoding": "BINARIO_EXCEL", "delimitador": ""}
    first_line, encoding = read_first_line(path)
    delimiter = detect_delimiter(first_line)
    values = parse_line(first_line, delimiter)
    header = has_header(values, official_headers)
    rows: list[list[str]] = []
    with path.open("r", encoding=encoding, errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for line_number, row in enumerate(reader, start=1):
            if line_number == 1 and header:
                continue
            rows.append(row)
    if header:
        columns = values
    elif rows and len(rows[0]) == len(official_headers):
        columns = list(official_headers)
    else:
        width = max([len(row) for row in rows], default=len(values))
        columns = [f"COLUMNA_ORIGINAL_{index + 1}" for index in range(width)]
    normalized_rows = [row + [""] * (len(columns) - len(row)) for row in rows]
    frame = pd.DataFrame(normalized_rows, columns=columns, dtype=str).fillna("")
    return frame, {"tipo": "texto", "hoja": "", "encoding": encoding, "delimitador": delimiter}


def build_column_mapping(columns: Sequence[object], official_headers: Sequence[str]) -> dict[str, str]:
    """Construye equivalencias directas de columnas historicas a homologadas."""

    official_by_norm = {normalize_header(header): header for header in official_headers}
    aliases = {
        "NUM_HORAS_HONORARIO": "NUM_HORAS_HONORARIOS",
        "HORAS_HONORARIO": "NUM_HORAS_HONORARIOS",
        "TOTAL_HORAS": "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
    }
    mapping: dict[str, str] = {}
    for column in columns:
        key = normalize_header(column)
        homologated = official_by_norm.get(key) or aliases.get(key)
        if homologated:
            mapping[str(column)] = homologated
    return mapping


def homologation_records(anio: int, columns: Sequence[object], official_headers: Sequence[str]) -> list[dict[str, object]]:
    """Registra diccionario de equivalencias por anio."""

    mapping = build_column_mapping(columns, official_headers)
    used = set(mapping.values())
    rows = [
        {
            "anio": anio,
            "columna_original": original,
            "nombre_homologado": homologated,
            "tipo": "string",
            "obligatoria": "SI" if homologated in {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "VIGENCIA"} else "NO",
            "equivalencia": "DIRECTA",
            "observaciones": "",
        }
        for original, homologated in mapping.items()
    ]
    for header in official_headers:
        if header not in used:
            rows.append(
                {
                    "anio": anio,
                    "columna_original": "",
                    "nombre_homologado": header,
                    "tipo": "string",
                    "obligatoria": "SI" if header in {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "VIGENCIA"} else "NO",
                    "equivalencia": "NO_DISPONIBLE_EN_ESE_AÑO",
                    "observaciones": "No se inventa valor; queda documentado como no disponible.",
                }
            )
    return rows
