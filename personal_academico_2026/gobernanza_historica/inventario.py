"""Inventario completo de candidatos historicos de Personal Academico."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd

from .descubrimiento_fuentes import (
    discover_candidate_files,
    infer_year_from_path,
    infer_year_from_text,
    iso_from_timestamp,
    normalize_text,
    relative_path,
    sha256_file,
)


@dataclass(frozen=True)
class InventoryRecord:
    """Perfil gobernado de un candidato historico."""

    fuente_id: str
    ruta: str
    ruta_relativa: str
    nombre: str
    extension: str
    size_bytes: int
    fecha_modificacion: str
    sha256: str
    anio_inferido: int | None
    anio_por_carpeta: int | None
    anio_por_contenido: int | None
    encoding: str
    delimitador: str
    cantidad_hojas: int
    hojas: str
    hoja_seleccionada: str
    cantidad_filas: int
    cantidad_columnas: int
    encabezados: str
    personas: int
    personas_vigentes: int
    personas_no_vigentes: int
    duplicados: int
    estado_preliminar: str
    evidencia_pes: str
    observaciones: str


def read_first_line(path: Path) -> tuple[str, str]:
    """Lee primera linea probando codificaciones usuales."""

    last_error: UnicodeDecodeError | None = None
    for encoding in ["utf-8-sig", "cp1252", "latin1"]:
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return handle.readline().rstrip("\r\n"), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return "", "NO_DETERMINADO"


def detect_delimiter(first_line: str) -> str:
    """Detecta delimitador simple desde una primera linea."""

    counts = {candidate: first_line.count(candidate) for candidate in [";", "\t", ","]}
    return max(counts, key=counts.get)


def parse_line(line: str, delimiter: str) -> list[str]:
    """Parsea una linea tabular."""

    if line == "":
        return []
    return next(csv.reader([line], delimiter=delimiter))


def normalize_header(value: object) -> str:
    """Normaliza encabezados para emparejar estructuras."""

    return "_".join(normalize_text(value).replace("-", " ").replace(".", " ").split())


def header_score(values: Sequence[object], official_headers: Sequence[str]) -> int:
    """Mide similitud de encabezados con estructura oficial."""

    official = {normalize_header(header) for header in official_headers}
    return sum(1 for value in values if normalize_header(value) in official)


def has_header(values: Sequence[object], official_headers: Sequence[str]) -> bool:
    """Determina si una fila parece encabezado academico."""

    normalized = [normalize_header(value) for value in values]
    return "TIPO_DOCUMENTO" in normalized or header_score(values, official_headers) >= 5


def normalize_document(tipo: object, numero: object, dv: object) -> str:
    """Construye clave documental normalizada solo para conteos."""

    tipo_text = normalize_text(tipo).strip()
    number = "" if pd.isna(numero) else str(numero).strip()
    check = "" if pd.isna(dv) else str(dv).strip().upper()
    if tipo_text == "R":
        number = "".join(ch for ch in number if ch.isdigit())
        check = check.replace(".", "").replace("-", "").replace(" ", "")
    if tipo_text == "P":
        number = number.replace(" ", "")
        check = ""
    if tipo_text == "" or number == "":
        return ""
    return f"{tipo_text}|{number}|{check}"


def people_metrics(frame: pd.DataFrame) -> dict[str, int]:
    """Calcula personas, vigencia y duplicados sin exponer identidades."""

    if not {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"}.issubset(frame.columns):
        return {"personas": 0, "personas_vigentes": 0, "personas_no_vigentes": 0, "duplicados": 0}
    identifiers = frame.apply(lambda row: normalize_document(row.get("TIPO_DOCUMENTO"), row.get("NUM_DOCUMENTO"), row.get("DV")), axis=1)
    valid = identifiers[identifiers.astype(str).str.len() > 0]
    if "VIGENCIA" in frame.columns:
        vigencia = frame["VIGENCIA"].astype(str).str.strip()
        vigentes = identifiers[(vigencia == "1") & identifiers.astype(str).str.len().gt(0)]
        no_vigentes = identifiers[(vigencia != "1") & identifiers.astype(str).str.len().gt(0)]
    else:
        vigentes = pd.Series(dtype=str)
        no_vigentes = pd.Series(dtype=str)
    return {
        "personas": int(valid.nunique()),
        "personas_vigentes": int(vigentes.nunique()),
        "personas_no_vigentes": int(no_vigentes.nunique()),
        "duplicados": int(valid.duplicated(keep=False).sum()),
    }


def classify_candidate(path: Path, columns: Sequence[object], observations: str) -> tuple[str, str]:
    """Clasifica preliminarmente candidatos sin descartarlos."""

    text = normalize_text(path.as_posix())
    headers = normalize_text(";".join(str(column) for column in columns))
    evidence = "SI" if any(token in text for token in ["SIES", "PES", "CARGA", "ENVIADO", "OFICIAL", "PES_READY", "PAC"]) else "NO"
    if observations:
        return "REVISION_REQUERIDA", evidence
    if "PROBLEMA" in text or "ERROR" in text or path.suffix.lower() == ".txt":
        return "REPORTE_ERROR_O_TEXTO", evidence
    if "ESTRUCTURA" in text or "INSTRUCTIVO" in text:
        return "DOCUMENTO_REFERENCIAL_NO_FUENTE_ANUAL", evidence
    if "TIPO_DOCUMENTO" in headers and "NUM_DOCUMENTO" in headers:
        return "CANDIDATO_TABULAR_CON_ESTRUCTURA", evidence
    return "CANDIDATO_NO_DETERMINADO", evidence


def text_profile(path: Path, official_headers: Sequence[str]) -> dict[str, object]:
    """Perfila un CSV/TXT candidato."""

    first_line, encoding = read_first_line(path)
    delimiter = detect_delimiter(first_line)
    first_values = parse_line(first_line, delimiter)
    header = has_header(first_values, official_headers)
    rows: list[list[str]] = []
    with path.open("r", encoding=encoding, errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for line_number, row in enumerate(reader, start=1):
            if line_number == 1 and header:
                continue
            rows.append(row)
    if header:
        columns = [str(value).strip() for value in first_values]
    elif rows and len(rows[0]) == len(official_headers):
        columns = list(official_headers)
    else:
        columns = [f"COLUMNA_{index + 1}" for index in range(len(first_values))]
    width = max([len(columns)] + [len(row) for row in rows])
    if len(columns) < width:
        columns = columns + [f"COLUMNA_EXTRA_{index + 1}" for index in range(width - len(columns))]
    normalized_rows = [row + [""] * (width - len(row)) if len(row) < width else row[:width] for row in rows]
    frame = pd.DataFrame(normalized_rows, columns=columns, dtype=str) if rows else pd.DataFrame(columns=columns)
    metrics = people_metrics(frame.fillna(""))
    return {
        "encoding": encoding,
        "delimitador": delimiter,
        "cantidad_hojas": 0,
        "hojas": "",
        "hoja_seleccionada": "",
        "cantidad_filas": len(frame),
        "cantidad_columnas": len(columns),
        "encabezados": ";".join(columns),
        "anio_por_contenido": infer_year_from_text(first_line),
        "observaciones": "",
        **metrics,
    }


def excel_profile(path: Path, official_headers: Sequence[str]) -> dict[str, object]:
    """Perfila un Excel candidato sin modificarlo."""

    try:
        workbook = pd.ExcelFile(path)
    except Exception as exc:  # noqa: BLE001
        return {
            "encoding": "BINARIO_EXCEL",
            "delimitador": "",
            "cantidad_hojas": 0,
            "hojas": "",
            "hoja_seleccionada": "",
            "cantidad_filas": 0,
            "cantidad_columnas": 0,
            "encabezados": "",
            "anio_por_contenido": None,
            "personas": 0,
            "personas_vigentes": 0,
            "personas_no_vigentes": 0,
            "duplicados": 0,
            "observaciones": f"No se pudo abrir Excel: {type(exc).__name__}",
        }
    best_sheet = ""
    best_columns: list[str] = []
    best_score = -1
    best_frame = pd.DataFrame()
    for sheet in workbook.sheet_names:
        try:
            sample = pd.read_excel(path, sheet_name=sheet, nrows=10, dtype=str)
        except Exception:
            continue
        score = header_score(sample.columns, official_headers)
        if score > best_score:
            best_score = score
            best_sheet = str(sheet)
            best_columns = [str(column) for column in sample.columns]
            try:
                best_frame = pd.read_excel(path, sheet_name=sheet, dtype=str, keep_default_na=False).fillna("")
            except Exception:
                best_frame = sample.fillna("")
    metrics = people_metrics(best_frame)
    return {
        "encoding": "BINARIO_EXCEL",
        "delimitador": "",
        "cantidad_hojas": len(workbook.sheet_names),
        "hojas": ";".join(str(sheet) for sheet in workbook.sheet_names),
        "hoja_seleccionada": best_sheet,
        "cantidad_filas": len(best_frame),
        "cantidad_columnas": len(best_columns),
        "encabezados": ";".join(best_columns),
        "anio_por_contenido": infer_year_from_text(" ".join([best_sheet, " ".join(best_columns)])),
        "observaciones": "" if best_score > 0 else "No se detectaron encabezados academicos compatibles.",
        **metrics,
    }


def profile_file(path: Path, root: Path, official_headers: Sequence[str], index: int) -> InventoryRecord:
    """Construye registro de inventario para un archivo candidato."""

    stat = path.stat()
    if path.suffix.lower() in {".csv", ".txt"}:
        profile = text_profile(path, official_headers)
    else:
        profile = excel_profile(path, official_headers)
    status, evidence = classify_candidate(path, str(profile.get("encabezados", "")).split(";"), str(profile.get("observaciones", "")))
    year_path = infer_year_from_path(path, root)
    year_name = infer_year_from_text(path.name)
    year_content = profile.get("anio_por_contenido")
    return InventoryRecord(
        fuente_id=f"FH_{index:04d}",
        ruta=str(path),
        ruta_relativa=relative_path(path, root),
        nombre=path.name,
        extension=path.suffix.lower(),
        size_bytes=stat.st_size,
        fecha_modificacion=iso_from_timestamp(stat.st_mtime),
        sha256=sha256_file(path),
        anio_inferido=year_path or year_name or (int(year_content) if year_content else None),
        anio_por_carpeta=year_path,
        anio_por_contenido=int(year_content) if year_content else None,
        encoding=str(profile.get("encoding", "")),
        delimitador=str(profile.get("delimitador", "")),
        cantidad_hojas=int(profile.get("cantidad_hojas", 0) or 0),
        hojas=str(profile.get("hojas", "")),
        hoja_seleccionada=str(profile.get("hoja_seleccionada", "")),
        cantidad_filas=int(profile.get("cantidad_filas", 0) or 0),
        cantidad_columnas=int(profile.get("cantidad_columnas", 0) or 0),
        encabezados=str(profile.get("encabezados", "")),
        personas=int(profile.get("personas", 0) or 0),
        personas_vigentes=int(profile.get("personas_vigentes", 0) or 0),
        personas_no_vigentes=int(profile.get("personas_no_vigentes", 0) or 0),
        duplicados=int(profile.get("duplicados", 0) or 0),
        estado_preliminar=status,
        evidencia_pes=evidence,
        observaciones=str(profile.get("observaciones", "")),
    )


def build_inventory(root: Path, official_headers: Sequence[str]) -> pd.DataFrame:
    """Genera inventario recursivo completo de fuentes candidatas."""

    records = [
        profile_file(path, root, official_headers, index)
        for index, path in enumerate(discover_candidate_files(root), start=1)
    ]
    return pd.DataFrame([asdict(record) for record in records])
