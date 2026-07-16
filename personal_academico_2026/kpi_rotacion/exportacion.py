"""Exportaciones oficiales e institucionales del hito de rotacion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .auditoria import flatten_audit
from .comparacion import ComparisonResult
from .validacion import ValidationIssue, issues_to_frame


def ensure_output_dir(output_dir: Path) -> Path:
    """Crea la carpeta de salida del hito si no existe."""

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def detail_csv_frame(detail: pd.DataFrame) -> pd.DataFrame:
    """Construye el CSV detalle con las columnas requeridas por el hito."""

    return pd.DataFrame(
        {
            "Tipo documento": detail.get("TIPO_DOCUMENTO", pd.Series(dtype=str)),
            "Documento": detail.get("NUM_DOCUMENTO", pd.Series(dtype=str)),
            "DV": detail.get("DV", pd.Series(dtype=str)),
            "Nombre": detail.get("NOMBRE", pd.Series(dtype=str)),
            "Estado": detail.get("ESTADO_ROTACION", pd.Series(dtype=str)),
            "Permanece": detail.get("PERMANECE", pd.Series(dtype=int)),
            "Rota": detail.get("ROTA", pd.Series(dtype=int)),
            "Nuevo": detail.get("NUEVO", pd.Series(dtype=int)),
            "Año base": detail.get("ANIO_BASE", pd.Series(dtype=int)),
            "Año comparación": detail.get("ANIO_COMPARACION", pd.Series(dtype=int)),
            "Cargo": detail.get("CARGO", pd.Series(dtype=str)),
            "Programa": detail.get("PROGRAMA", pd.Series(dtype=str)),
            "Jerarquía": detail.get("JERARQUIA", pd.Series(dtype=str)),
            "Horas": detail.get("HORAS", pd.Series(dtype=float)),
            "Observaciones": detail.get("OBSERVACIONES", pd.Series(dtype=str)),
        }
    )


def official_rotation_sheet(kpi_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une indicador oficial total y desagregaciones oficiales."""

    summary = kpi_tables["indicador_oficial"].copy()
    summary["SECCION"] = "RESUMEN_OFICIAL"
    variable = kpi_tables["rotacion_por_variable"].copy()
    variable["SECCION"] = "DESAGREGACION_OFICIAL"
    return pd.concat([summary, variable], ignore_index=True, sort=False)


def filter_variable_sheet(variable_frame: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """Filtra desagregaciones oficiales asignadas a una hoja Excel."""

    if variable_frame.empty or "HOJA_SUGERIDA" not in variable_frame.columns:
        return pd.DataFrame()
    return variable_frame[variable_frame["HOJA_SUGERIDA"].eq(sheet_name)].reset_index(drop=True)


def hours_sheet(kpi_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Construye la hoja de horas como KPI institucional sin tramos inventados."""

    institutional = kpi_tables["kpi_institucional"]
    if institutional.empty:
        return institutional
    mask = institutional["INDICADOR"].astype(str).str.contains("HORAS|TRAMOS_HORAS", regex=True)
    return institutional[mask].reset_index(drop=True)


def resumen_sheet(kpi_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Construye la hoja resumen separando KPI oficial e institucional."""

    official = kpi_tables["indicador_oficial"].copy()
    institutional = kpi_tables["kpi_institucional"].copy()
    return pd.concat([official, institutional], ignore_index=True, sort=False)


def validation_sheet(issues: list[ValidationIssue]) -> pd.DataFrame:
    """Construye la hoja de validaciones."""

    return issues_to_frame(issues)


def export_detail_csv(output_dir: Path, detail: pd.DataFrame) -> Path:
    """Exporta el detalle de clasificacion anual en CSV."""

    path = output_dir / "ROTACION_DOCENTE_DETALLE.csv"
    detail_csv_frame(detail).to_csv(path, index=False, sep=";", encoding="utf-8-sig")
    return path


def export_excel(
    output_dir: Path,
    result: ComparisonResult,
    kpi_tables: dict[str, pd.DataFrame],
    issues: list[ValidationIssue],
    audit: dict[str, object],
) -> Path:
    """Exporta el libro Excel con las hojas solicitadas por el hito."""

    path = output_dir / "KPI_ROTACION_DOCENTE.xlsx"
    variable_frame = kpi_tables["rotacion_por_variable"]
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        resumen_sheet(kpi_tables).to_excel(writer, sheet_name="00_RESUMEN", index=False)
        official_rotation_sheet(kpi_tables).to_excel(writer, sheet_name="01_ROTACION_OFICIAL", index=False)
        result.detail[result.detail["ESTADO_ROTACION"].eq("PERMANECE")].to_excel(writer, sheet_name="02_PERMANECEN", index=False)
        result.detail[result.detail["ESTADO_ROTACION"].eq("ROTA")].to_excel(writer, sheet_name="03_ROTAN", index=False)
        result.detail[result.detail["ESTADO_ROTACION"].eq("NUEVO INGRESO")].to_excel(writer, sheet_name="04_INGRESOS", index=False)
        filter_variable_sheet(variable_frame, "05_SEXO").to_excel(writer, sheet_name="05_SEXO", index=False)
        filter_variable_sheet(variable_frame, "06_FORMACION").to_excel(writer, sheet_name="06_FORMACION", index=False)
        hours_sheet(kpi_tables).to_excel(writer, sheet_name="07_HORAS", index=False)
        filter_variable_sheet(variable_frame, "08_CARGO").to_excel(writer, sheet_name="08_CARGO", index=False)
        filter_variable_sheet(variable_frame, "09_PROGRAMA").to_excel(writer, sheet_name="09_PROGRAMA", index=False)
        filter_variable_sheet(variable_frame, "10_ADSCRIPCION").to_excel(writer, sheet_name="10_ADSCRIPCION", index=False)
        filter_variable_sheet(variable_frame, "11_JERARQUIA").to_excel(writer, sheet_name="11_JERARQUIA", index=False)
        validation_sheet(issues).to_excel(writer, sheet_name="12_VALIDACIONES", index=False)
        flatten_audit(audit).to_excel(writer, sheet_name="13_AUDITORIA", index=False)
    return path


def json_default(value: Any) -> Any:
    """Serializa objetos no nativos usados en auditoria."""

    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def frame_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    """Convierte un DataFrame a registros JSON estables."""

    if frame.empty:
        return []
    return frame.fillna("").to_dict(orient="records")


def export_json(
    output_dir: Path,
    result: ComparisonResult,
    kpi_tables: dict[str, pd.DataFrame],
    issues: list[ValidationIssue],
    audit: dict[str, object],
) -> Path:
    """Exporta el paquete de KPI y auditoria en JSON."""

    payload = {
        "indicador_oficial": frame_records(kpi_tables["indicador_oficial"]),
        "rotacion_por_variable": frame_records(kpi_tables["rotacion_por_variable"]),
        "kpi_institucional": frame_records(kpi_tables["kpi_institucional"]),
        "detalle": frame_records(detail_csv_frame(result.detail)),
        "validaciones": frame_records(validation_sheet(issues)),
        "auditoria": audit,
    }
    path = output_dir / "kpi_rotacion.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, default=json_default)
    return path


def markdown_lines(
    kpi_tables: dict[str, pd.DataFrame],
    issues: list[ValidationIssue],
    audit: dict[str, object],
) -> list[str]:
    """Construye el reporte Markdown de cierre tecnico."""

    official = kpi_tables["indicador_oficial"]
    institutional = kpi_tables["kpi_institucional"]
    rows = ["# ROTACION DOCENTE", ""]
    rows.append("## KPI OFICIAL SIES")
    rows.append("")
    rows.append("Formula implementada: academicos presentes en anio base y ausentes en anio comparacion, dividido por total de academicos presentes en anio base, multiplicado por 100.")
    rows.append("")
    for record in frame_records(official):
        rows.append(f"- {record.get('INDICADOR')}: {record.get('VALOR')}")
    rows.append("")
    rows.append("## KPI INSTITUCIONAL")
    rows.append("")
    rows.append("Los siguientes indicadores son complementarios y no forman parte de la tasa oficial SIES.")
    for record in frame_records(institutional):
        rows.append(f"- {record.get('INDICADOR')} ({record.get('ANIO', '')}): {record.get('VALOR')}")
    rows.append("")
    rows.append("## Validaciones")
    rows.append("")
    rows.append(f"- Errores: {audit.get('cantidad_errores')}")
    rows.append(f"- Advertencias: {audit.get('cantidad_advertencias')}")
    rows.append(f"- Hallazgos registrados: {len(issues)}")
    rows.append("")
    rows.append("## Auditoria")
    rows.append("")
    rows.append(f"- Fecha: {audit.get('fecha')}")
    rows.append(f"- Hora: {audit.get('hora')}")
    rows.append(f"- Version modulo: {audit.get('version')}")
    rows.append(f"- Tiempo ejecucion segundos: {audit.get('tiempo_ejecucion_segundos')}")
    return rows


def export_markdown(
    output_dir: Path,
    kpi_tables: dict[str, pd.DataFrame],
    issues: list[ValidationIssue],
    audit: dict[str, object],
) -> Path:
    """Exporta el reporte Markdown del hito."""

    path = output_dir / "ROTACION_DOCENTE.md"
    path.write_text("\n".join(markdown_lines(kpi_tables, issues, audit)) + "\n", encoding="utf-8")
    return path


def export_all(
    output_dir: Path,
    result: ComparisonResult,
    kpi_tables: dict[str, pd.DataFrame],
    issues: list[ValidationIssue],
    audit: dict[str, object],
) -> dict[str, Path]:
    """Ejecuta todas las exportaciones requeridas por la especificacion."""

    target = ensure_output_dir(output_dir)
    return {
        "detalle_csv": export_detail_csv(target, result.detail),
        "excel": export_excel(target, result, kpi_tables, issues, audit),
        "markdown": export_markdown(target, kpi_tables, issues, audit),
        "json": export_json(target, result, kpi_tables, issues, audit),
    }
