"""Comparacion anual y clasificacion oficial de rotacion SIES."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from .validacion import (
    build_identifier_series,
    has_valid_identifier,
    normalize_value,
    parse_number,
)


@dataclass(frozen=True)
class ComparisonResult:
    """Resultado completo de la clasificacion anual de academicos."""

    detail: pd.DataFrame
    base_unique: pd.DataFrame
    comparison_unique: pd.DataFrame
    excluded_without_identifier: pd.DataFrame


def unique_valid_people(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deduplica personas con identificador oficial valido para comparacion."""

    working = frame.copy()
    working["IDENTIFICADOR_SIES"] = build_identifier_series(working)
    valid_mask = working.apply(has_valid_identifier, axis=1)
    if "VIGENCIA" in working.columns:
        valid_mask = valid_mask & working["VIGENCIA"].map(lambda value: normalize_value(value) == "1")
    excluded = working[~valid_mask].copy()
    valid = working[valid_mask].copy()
    valid = valid.drop_duplicates(subset=["IDENTIFICADOR_SIES"], keep="first").reset_index(drop=True)
    return valid, excluded


def full_name(row: pd.Series) -> str:
    """Construye un nombre completo solo para auditoria y reportes."""

    parts = [
        normalize_value(row.get("NOMBRES", "")),
        normalize_value(row.get("PRIMER_APELLIDO", "")),
        normalize_value(row.get("SEGUNDO_APELLIDO", "")),
    ]
    return " ".join(part for part in parts if part)


def total_hours(row: pd.Series) -> float:
    """Calcula horas totales disponibles segun columnas oficiales presentes."""

    contract_columns = ["NUM_HORAS_PLANTA", "NUM_HORAS_CONTRATA", "NUM_HORAS_HONORARIOS"]
    if all(column in row.index for column in contract_columns):
        values = [parse_number(row.get(column, "")) for column in contract_columns]
        return sum(value or 0.0 for value in values)
    value = parse_number(row.get("TOTAL_HORAS_CONTRATADAS", ""))
    if value is not None:
        return value
    principal = parse_number(row.get("TOTAL_HORAS_PRINCIPAL_PROGRAMA", ""))
    return principal or 0.0


def source_row(
    identifier: str,
    base_by_id: dict[str, pd.Series],
    comparison_by_id: dict[str, pd.Series],
) -> pd.Series:
    """Selecciona la fila base para reportar, o comparacion si es nuevo ingreso."""

    if identifier in base_by_id:
        return base_by_id[identifier]
    return comparison_by_id[identifier]


def changed(row_base: pd.Series | None, row_comparison: pd.Series | None, columns: Sequence[str]) -> bool:
    """Evalua si alguna columna cambio para una persona que permanece."""

    if row_base is None or row_comparison is None:
        return False
    for column in columns:
        if column in row_base.index and column in row_comparison.index:
            if normalize_value(row_base.get(column, "")) != normalize_value(row_comparison.get(column, "")):
                return True
    return False


def observations(row_base: pd.Series | None, row_comparison: pd.Series | None, state: str) -> str:
    """Construye observaciones de auditoria para el detalle."""

    notes: list[str] = []
    if state == "NUEVO INGRESO":
        notes.append("KPI INSTITUCIONAL: no participa en tasa oficial SIES")
    if changed(row_base, row_comparison, ["PRINCIPAL_CARGO_ACADEMICO", "CARGO_NORMALIZADO"]):
        notes.append("Cambio de cargo")
    if changed(row_base, row_comparison, ["JERARQUIA_ACADEMICA", "JERARQUIA_ACADEMICA_OCDE"]):
        notes.append("Cambio de jerarquia")
    if changed(row_base, row_comparison, ["NIVEL_SUPERIOR_ADSCRIPCION", "NIVEL_SECUNDARIO_ADSCRIPCION"]):
        notes.append("Cambio de adscripcion")
    if changed(row_base, row_comparison, ["NOMBRE_PRINCIPAL_PROGRAMA"]):
        notes.append("Cambio de programa")
    return "; ".join(notes)


def value_from_pair(
    row_base: pd.Series | None,
    row_comparison: pd.Series | None,
    column: str,
) -> tuple[str, str]:
    """Obtiene valores base y comparacion para una columna opcional."""

    base_value = "" if row_base is None or column not in row_base.index else normalize_value(row_base.get(column, ""))
    comp_value = "" if row_comparison is None or column not in row_comparison.index else normalize_value(row_comparison.get(column, ""))
    return base_value, comp_value


def build_detail_row(
    identifier: str,
    state: str,
    anio_base: int,
    anio_comparacion: int,
    base_by_id: dict[str, pd.Series],
    comparison_by_id: dict[str, pd.Series],
    official_headers: Sequence[str],
) -> dict[str, object]:
    """Crea una fila de detalle para un identificador clasificado."""

    row_base = base_by_id.get(identifier)
    row_comparison = comparison_by_id.get(identifier)
    report_row = source_row(identifier, base_by_id, comparison_by_id)
    detail: dict[str, object] = {
        "IDENTIFICADOR_SIES": identifier,
        "TIPO_DOCUMENTO": normalize_value(report_row.get("TIPO_DOCUMENTO", "")),
        "NUM_DOCUMENTO": normalize_value(report_row.get("NUM_DOCUMENTO", "")),
        "DV": normalize_value(report_row.get("DV", "")),
        "NOMBRE": full_name(report_row),
        "ESTADO_ROTACION": state,
        "PERMANECE": 1 if state == "PERMANECE" else 0,
        "ROTA": 1 if state == "ROTA" else 0,
        "NUEVO": 1 if state == "NUEVO INGRESO" else 0,
        "ANIO_BASE": anio_base,
        "ANIO_COMPARACION": anio_comparacion,
        "CARGO": normalize_value(report_row.get("PRINCIPAL_CARGO_ACADEMICO", "")),
        "PROGRAMA": normalize_value(report_row.get("NOMBRE_PRINCIPAL_PROGRAMA", "")),
        "JERARQUIA": normalize_value(report_row.get("JERARQUIA_ACADEMICA", "")),
        "HORAS": total_hours(report_row),
        "OBSERVACIONES": observations(row_base, row_comparison, state),
        "CAMBIO_CARGO": int(changed(row_base, row_comparison, ["PRINCIPAL_CARGO_ACADEMICO", "CARGO_NORMALIZADO"])),
        "CAMBIO_JERARQUIA": int(changed(row_base, row_comparison, ["JERARQUIA_ACADEMICA", "JERARQUIA_ACADEMICA_OCDE"])),
        "CAMBIO_ADSCRIPCION": int(changed(row_base, row_comparison, ["NIVEL_SUPERIOR_ADSCRIPCION", "NIVEL_SECUNDARIO_ADSCRIPCION"])),
        "CAMBIO_PROGRAMA": int(changed(row_base, row_comparison, ["NOMBRE_PRINCIPAL_PROGRAMA"])),
    }
    for column in official_headers:
        base_value, comp_value = value_from_pair(row_base, row_comparison, column)
        detail[f"{column}_BASE"] = base_value
        detail[f"{column}_COMPARACION"] = comp_value
    return detail


def empty_detail_frame(official_headers: Sequence[str]) -> pd.DataFrame:
    """Entrega un detalle vacio con columnas estables para KPI y exportacion."""

    base_columns = [
        "IDENTIFICADOR_SIES",
        "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO",
        "DV",
        "NOMBRE",
        "ESTADO_ROTACION",
        "PERMANECE",
        "ROTA",
        "NUEVO",
        "ANIO_BASE",
        "ANIO_COMPARACION",
        "CARGO",
        "PROGRAMA",
        "JERARQUIA",
        "HORAS",
        "OBSERVACIONES",
        "CAMBIO_CARGO",
        "CAMBIO_JERARQUIA",
        "CAMBIO_ADSCRIPCION",
        "CAMBIO_PROGRAMA",
    ]
    pair_columns = [
        column
        for official in official_headers
        for column in (f"{official}_BASE", f"{official}_COMPARACION")
    ]
    return pd.DataFrame(columns=base_columns + pair_columns)


def compare_years(
    base_frame: pd.DataFrame,
    comparison_frame: pd.DataFrame,
    anio_base: int,
    anio_comparacion: int,
    official_headers: Sequence[str],
) -> ComparisonResult:
    """Clasifica PERMANECE, ROTA y NUEVO INGRESO usando el identificador oficial."""

    base_unique, base_excluded = unique_valid_people(base_frame)
    comparison_unique, comparison_excluded = unique_valid_people(comparison_frame)
    base_by_id = {
        normalize_value(row["IDENTIFICADOR_SIES"]): row
        for _index, row in base_unique.iterrows()
    }
    comparison_by_id = {
        normalize_value(row["IDENTIFICADOR_SIES"]): row
        for _index, row in comparison_unique.iterrows()
    }
    identifiers = sorted(set(base_by_id).union(set(comparison_by_id)))
    rows: list[dict[str, object]] = []
    for identifier in identifiers:
        in_base = identifier in base_by_id
        in_comparison = identifier in comparison_by_id
        if in_base and in_comparison:
            state = "PERMANECE"
        elif in_base:
            state = "ROTA"
        else:
            state = "NUEVO INGRESO"
        rows.append(
            build_detail_row(
                identifier=identifier,
                state=state,
                anio_base=anio_base,
                anio_comparacion=anio_comparacion,
                base_by_id=base_by_id,
                comparison_by_id=comparison_by_id,
                official_headers=official_headers,
            )
        )
    excluded = pd.concat([base_excluded.assign(ANIO=anio_base), comparison_excluded.assign(ANIO=anio_comparacion)])
    detail = pd.DataFrame(rows) if rows else empty_detail_frame(official_headers)
    return ComparisonResult(
        detail=detail,
        base_unique=base_unique,
        comparison_unique=comparison_unique,
        excluded_without_identifier=excluded.reset_index(drop=True),
    )
