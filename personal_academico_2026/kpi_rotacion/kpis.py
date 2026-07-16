"""Calculo de indicador oficial SIES y KPI institucionales separados."""

from __future__ import annotations

from typing import Sequence

import pandas as pd

from .comparacion import ComparisonResult
from .validacion import normalize_value, parse_number


def safe_percent(numerator: float, denominator: float) -> float:
    """Calcula un porcentaje con denominador protegido."""

    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 4)


def official_indicator(detail: pd.DataFrame) -> pd.DataFrame:
    """Calcula la tasa oficial de rotacion SIES."""

    base_rows = detail[detail["ESTADO_ROTACION"].isin(["PERMANECE", "ROTA"])]
    total_base = int(len(base_rows))
    permanecen = int((base_rows["ESTADO_ROTACION"] == "PERMANECE").sum())
    rotan = int((base_rows["ESTADO_ROTACION"] == "ROTA").sum())
    return pd.DataFrame(
        [
            {
                "TIPO_KPI": "KPI OFICIAL SIES",
                "INDICADOR": "TOTAL ACADEMICOS ANIO BASE",
                "VALOR": total_base,
                "FORMULA": "Conteo de identificadores presentes en anio base",
            },
            {
                "TIPO_KPI": "KPI OFICIAL SIES",
                "INDICADOR": "ACADEMICOS QUE PERMANECEN",
                "VALOR": permanecen,
                "FORMULA": "Presentes en anio base y presentes en anio comparacion",
            },
            {
                "TIPO_KPI": "KPI OFICIAL SIES",
                "INDICADOR": "ACADEMICOS QUE ROTAN",
                "VALOR": rotan,
                "FORMULA": "Presentes en anio base y ausentes en anio comparacion",
            },
            {
                "TIPO_KPI": "KPI OFICIAL SIES",
                "INDICADOR": "TASA OFICIAL DE ROTACION",
                "VALOR": safe_percent(rotan, total_base),
                "FORMULA": "(Academicos base ausentes en comparacion / Academicos base) * 100",
            },
        ]
    )


def analysis_variables(frame_columns: Sequence[str]) -> list[tuple[str, str, str]]:
    """Entrega variables oficiales disponibles para desagregacion."""

    candidates = [
        ("SEXO", "SEXO", "05_SEXO"),
        ("NIVEL_FORMACION_ACADEMICO", "NIVEL_FORMACION_ACADEMICO", "06_FORMACION"),
        ("PRINCIPAL_CARGO_ACADEMICO", "PRINCIPAL_CARGO_ACADEMICO", "08_CARGO"),
        ("CARGO_NORMALIZADO", "CARGO_NORMALIZADO", "08_CARGO"),
        ("NOMBRE_PRINCIPAL_PROGRAMA", "NOMBRE_PRINCIPAL_PROGRAMA", "09_PROGRAMA"),
        ("NIVEL_SUPERIOR_ADSCRIPCION", "NIVEL_SUPERIOR_ADSCRIPCION", "10_ADSCRIPCION"),
        ("NIVEL_SECUNDARIO_ADSCRIPCION", "NIVEL_SECUNDARIO_ADSCRIPCION", "10_ADSCRIPCION"),
        ("JERARQUIA_ACADEMICA", "JERARQUIA_ACADEMICA", "11_JERARQUIA"),
        ("JERARQUIA_ACADEMICA_OCDE", "JERARQUIA_ACADEMICA_OCDE", "11_JERARQUIA"),
        ("COMUNA_MAYOR_FUNCION", "COMUNA_MAYOR_FUNCION", "01_ROTACION_OFICIAL"),
        ("COMUNA_PRINCIPAL_PROGRAMA", "COMUNA_PRINCIPAL_PROGRAMA", "01_ROTACION_OFICIAL"),
        ("VIGENCIA", "VIGENCIA", "01_ROTACION_OFICIAL"),
    ]
    return [candidate for candidate in candidates if candidate[1] in frame_columns]


def rotation_by_variable(detail: pd.DataFrame, variables: Sequence[tuple[str, str, str]]) -> pd.DataFrame:
    """Calcula rotacion oficial por variable usando valores del anio base."""

    rows: list[dict[str, object]] = []
    base_rows = detail[detail["ESTADO_ROTACION"].isin(["PERMANECE", "ROTA"])].copy()
    for variable_name, column, sheet in variables:
        base_column = f"{column}_BASE"
        if base_column not in base_rows.columns:
            continue
        grouped = base_rows.groupby(base_rows[base_column].map(lambda value: normalize_value(value) or "SIN_DATO_EN_ARCHIVO"))
        for value, group in grouped:
            total = int(len(group))
            remain = int((group["ESTADO_ROTACION"] == "PERMANECE").sum())
            rotate = int((group["ESTADO_ROTACION"] == "ROTA").sum())
            rows.append(
                {
                    "TIPO_KPI": "KPI OFICIAL SIES",
                    "VARIABLE": variable_name,
                    "VALOR_VARIABLE": value,
                    "TOTAL_BASE": total,
                    "PERMANECEN": remain,
                    "ROTAN": rotate,
                    "TASA_ROTACION": safe_percent(rotate, total),
                    "HOJA_SUGERIDA": sheet,
                    "FORMULA": "(ROTAN / TOTAL_BASE) * 100",
                }
            )
    return pd.DataFrame(rows)


def sum_column(frame: pd.DataFrame, column: str) -> float:
    """Suma una columna numerica SIES tolerando coma decimal."""

    if column not in frame.columns:
        return 0.0
    return round(sum(parse_number(value) or 0.0 for value in frame[column]), 4)


def total_contract_hours(frame: pd.DataFrame) -> float:
    """Suma horas totales de contrato segun columnas disponibles."""

    contract_columns = ["NUM_HORAS_PLANTA", "NUM_HORAS_CONTRATA", "NUM_HORAS_HONORARIOS"]
    if all(column in frame.columns for column in contract_columns):
        return round(sum(sum_column(frame, column) for column in contract_columns), 4)
    return sum_column(frame, "TOTAL_HORAS_CONTRATADAS")


def institutional_kpis(result: ComparisonResult, anio_base: int, anio_comparacion: int) -> pd.DataFrame:
    """Calcula KPI institucionales separados del indicador oficial SIES."""

    detail = result.detail
    total_base = int(len(result.base_unique))
    total_comp = int(len(result.comparison_unique))
    remain = int((detail["ESTADO_ROTACION"] == "PERMANECE").sum())
    new_entries = int((detail["ESTADO_ROTACION"] == "NUEVO INGRESO").sum())
    variation = total_comp - total_base
    rows: list[dict[str, object]] = [
        {
            "TIPO_KPI": "KPI INSTITUCIONAL",
            "INDICADOR": "RETENCION",
            "VALOR": safe_percent(remain, total_base),
            "ANIO": f"{anio_base}-{anio_comparacion}",
            "OBSERVACION": "Permanecen / total anio base",
        },
        {
            "TIPO_KPI": "KPI INSTITUCIONAL",
            "INDICADOR": "PERMANENCIA",
            "VALOR": remain,
            "ANIO": f"{anio_base}-{anio_comparacion}",
            "OBSERVACION": "Conteo de academicos presentes en ambos anos",
        },
        {
            "TIPO_KPI": "KPI INSTITUCIONAL",
            "INDICADOR": "INGRESOS",
            "VALOR": new_entries,
            "ANIO": str(anio_comparacion),
            "OBSERVACION": "Nuevos ingresos no participan en tasa oficial SIES",
        },
        {
            "TIPO_KPI": "KPI INSTITUCIONAL",
            "INDICADOR": "VARIACION_DOTACION",
            "VALOR": variation,
            "ANIO": f"{anio_base}-{anio_comparacion}",
            "OBSERVACION": "Total comparacion - total base",
        },
        {
            "TIPO_KPI": "KPI INSTITUCIONAL",
            "INDICADOR": "VARIACION_PORCENTAJE",
            "VALOR": safe_percent(variation, total_base),
            "ANIO": f"{anio_base}-{anio_comparacion}",
            "OBSERVACION": "(Variacion dotacion / total base) * 100",
        },
    ]
    for year, frame in [(anio_base, result.base_unique), (anio_comparacion, result.comparison_unique)]:
        rows.extend(
            [
                {
                    "TIPO_KPI": "KPI INSTITUCIONAL",
                    "INDICADOR": "HORAS_PLANTA",
                    "VALOR": sum_column(frame, "NUM_HORAS_PLANTA"),
                    "ANIO": str(year),
                    "OBSERVACION": "Suma institucional de horas planta",
                },
                {
                    "TIPO_KPI": "KPI INSTITUCIONAL",
                    "INDICADOR": "HORAS_CONTRATA",
                    "VALOR": sum_column(frame, "NUM_HORAS_CONTRATA"),
                    "ANIO": str(year),
                    "OBSERVACION": "Suma institucional de horas contrata",
                },
                {
                    "TIPO_KPI": "KPI INSTITUCIONAL",
                    "INDICADOR": "HORAS_HONORARIOS",
                    "VALOR": sum_column(frame, "NUM_HORAS_HONORARIOS"),
                    "ANIO": str(year),
                    "OBSERVACION": "Suma institucional de horas honorarios",
                },
                {
                    "TIPO_KPI": "KPI INSTITUCIONAL",
                    "INDICADOR": "HORAS_TOTALES",
                    "VALOR": total_contract_hours(frame),
                    "ANIO": str(year),
                    "OBSERVACION": "Suma institucional de horas totales",
                },
            ]
        )
    remain_count = max(remain, 1)
    change_map = [
        ("CAMBIO_DE_CARGO", "CAMBIO_CARGO"),
        ("CAMBIO_DE_JERARQUIA", "CAMBIO_JERARQUIA"),
        ("CAMBIO_DE_ADSCRIPCION", "CAMBIO_ADSCRIPCION"),
        ("CAMBIO_DE_PROGRAMA", "CAMBIO_PROGRAMA"),
    ]
    remain_rows = detail[detail["ESTADO_ROTACION"] == "PERMANECE"]
    for indicator, column in change_map:
        value = int(remain_rows[column].sum()) if column in remain_rows.columns else 0
        rows.append(
            {
                "TIPO_KPI": "KPI INSTITUCIONAL",
                "INDICADOR": indicator,
                "VALOR": value,
                "ANIO": f"{anio_base}-{anio_comparacion}",
                "OBSERVACION": f"Casos y porcentaje entre permanentes: {safe_percent(value, remain_count)}%",
            }
        )
    rows.append(
        {
            "TIPO_KPI": "KPI INSTITUCIONAL",
            "INDICADOR": "TRAMOS_HORAS",
            "VALOR": "NO_CALCULADO",
            "ANIO": f"{anio_base}-{anio_comparacion}",
            "OBSERVACION": "El instructivo 2026 revisado no define tramos de horas; no se inventan tramos oficiales.",
        }
    )
    return pd.DataFrame(rows)


def build_kpi_tables(
    result: ComparisonResult,
    anio_base: int,
    anio_comparacion: int,
    official_headers: Sequence[str],
) -> dict[str, pd.DataFrame]:
    """Construye todas las tablas KPI requeridas para exportacion."""

    variables = analysis_variables(official_headers)
    official = official_indicator(result.detail)
    by_variable = rotation_by_variable(result.detail, variables)
    institutional = institutional_kpis(result, anio_base, anio_comparacion)
    return {
        "indicador_oficial": official,
        "rotacion_por_variable": by_variable,
        "kpi_institucional": institutional,
    }
