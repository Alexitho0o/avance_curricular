"""Utilidades compartidas para reconstruccion longitudinal."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


def sha256_file(path: Path) -> str:
    """Calcula SHA256 para verificar integridad de fuente gobernada."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_value(value: object) -> str:
    """Normaliza un valor escalar sin corregir datos fuente."""

    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.upper() in {"NAN", "NONE", "NULL"} else text


def parse_number(value: object) -> float | None:
    """Convierte numero SIES con coma o punto decimal."""

    text = normalize_value(value)
    if text == "":
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def normalize_document(tipo: object, numero: object, dv: object) -> str:
    """Construye clave documental normalizada TIPO|NUM|DV."""

    tipo_text = normalize_value(tipo).upper()
    number = normalize_value(numero)
    check = normalize_value(dv).upper()
    if tipo_text == "R":
        number = "".join(ch for ch in number if ch.isdigit())
        check = check.replace(".", "").replace("-", "").replace(" ", "")
    elif tipo_text == "P":
        number = number.replace(" ", "")
        check = ""
    else:
        number = number.replace(" ", "")
    if tipo_text == "" or number == "":
        return ""
    return f"{tipo_text}|{number}|{check}"


def compute_rut_dv(number: str) -> str | None:
    """Calcula DV de un RUT chileno."""

    if not number.isdigit():
        return None
    factors = [2, 3, 4, 5, 6, 7]
    total = 0
    for index, digit in enumerate(reversed(number)):
        total += int(digit) * factors[index % len(factors)]
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def first_value(row: pd.Series, *columns: str) -> str:
    """Obtiene el primer valor disponible entre columnas candidatas."""

    for column in columns:
        if column in row.index:
            value = normalize_value(row.get(column))
            if value != "":
                return value
    return ""


def hour_band(total_hours: float | None) -> str:
    """Clasifica tramo horario institucional requerido por Fase 2A."""

    if total_hours is None or total_hours <= 0:
        return "SIN HORAS"
    if total_hours < 11:
        return "menos de 11"
    if total_hours <= 22:
        return "11-22"
    if total_hours <= 38:
        return "23-38"
    return "39 o mas"


def contract_type(planta: float | None, contrata: float | None, honorarios: float | None) -> str:
    """Determina tipo contractual predominante institucional."""

    values = {
        "PLANTA": planta or 0.0,
        "CONTRATA": contrata or 0.0,
        "HONORARIOS": honorarios or 0.0,
    }
    positives = [name for name, value in values.items() if value > 0]
    if not positives:
        return "SIN HORAS"
    return positives[0] if len(positives) == 1 else "MIXTO"
