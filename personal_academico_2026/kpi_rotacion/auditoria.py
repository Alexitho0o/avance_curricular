"""Auditoria de ejecucion para el KPI de rotacion academica."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Sequence

import pandas as pd

from .config import RunConfig, module_version
from .lectura import AcademicDataset, sha256_file
from .validacion import ValidationIssue, build_identifier_series, issue_to_dict


def start_timer() -> float:
    """Inicia un temporizador monotonicamente estable."""

    return time.perf_counter()


def elapsed_seconds(start_value: float) -> float:
    """Calcula segundos transcurridos desde un valor de inicio."""

    return round(time.perf_counter() - start_value, 4)


def now_stamp() -> datetime:
    """Entrega la fecha y hora local de auditoria."""

    return datetime.now()


def count_unique_people(frame: pd.DataFrame) -> int:
    """Cuenta personas unicas usando el identificador SIES."""

    if frame.empty:
        return 0
    identifiers = build_identifier_series(frame)
    return int(identifiers[identifiers.str.strip().ne("||")].nunique())


def count_duplicates(frame: pd.DataFrame) -> int:
    """Cuenta filas con identificador SIES duplicado."""

    if frame.empty:
        return 0
    identifiers = build_identifier_series(frame)
    return int(identifiers.duplicated(keep=False).sum())


def source_record(path: Path, label: str) -> dict[str, object]:
    """Construye un registro de auditoria para una fuente documental."""

    return {
        "tipo": label,
        "archivo": str(path),
        "sha256": sha256_file(path),
    }


def dataset_record(dataset: AcademicDataset, label: str) -> dict[str, object]:
    """Construye un registro de auditoria para un archivo anual."""

    return {
        "tipo": label,
        "archivo": str(dataset.path),
        "sha256": dataset.file_sha256,
        "filas": dataset.rows,
        "columnas": dataset.columns,
        "personas_unicas": count_unique_people(dataset.frame),
        "duplicados": count_duplicates(dataset.frame),
        "delimitador": dataset.delimiter,
        "encoding": dataset.encoding,
        "tiene_encabezado": dataset.has_header,
    }


def issue_counts(issues: Sequence[ValidationIssue]) -> dict[str, int]:
    """Resume errores y advertencias detectadas."""

    errors = sum(1 for issue in issues if issue.severidad == "ERROR")
    warnings = sum(1 for issue in issues if issue.severidad == "ADVERTENCIA")
    return {"errores": errors, "advertencias": warnings}


def build_audit(
    config: RunConfig,
    base_dataset: AcademicDataset,
    comparison_dataset: AcademicDataset,
    issues: Sequence[ValidationIssue],
    elapsed: float,
) -> dict[str, object]:
    """Construye la auditoria completa solicitada por el hito."""

    now = now_stamp()
    counts = issue_counts(issues)
    return {
        "fecha": now.date().isoformat(),
        "hora": now.time().replace(microsecond=0).isoformat(),
        "version": module_version(),
        "anio_base": config.anio_base,
        "anio_comparacion": config.anio_comparacion,
        "tipo_archivo": config.tipo_archivo,
        "tiempo_ejecucion_segundos": elapsed,
        "cantidad_advertencias": counts["advertencias"],
        "cantidad_errores": counts["errores"],
        "fuentes_oficiales": [
            source_record(config.sources.instructivo, "instructivo_2026"),
            source_record(config.sources.estructura_en_institucion, "estructura_en_institucion_2026"),
            source_record(config.sources.estructura_fuera_institucion, "estructura_fuera_institucion_2026"),
        ],
        "archivos_utilizados": [
            dataset_record(base_dataset, "anio_base"),
            dataset_record(comparison_dataset, "anio_comparacion"),
        ],
        "validaciones": [issue_to_dict(issue) for issue in issues],
    }


def flatten_audit(audit: dict[str, object]) -> pd.DataFrame:
    """Aplana la auditoria principal en pares clave valor para Excel."""

    rows: list[dict[str, object]] = []
    for key, value in audit.items():
        if key in {"fuentes_oficiales", "archivos_utilizados", "validaciones"}:
            continue
        rows.append({"CAMPO": key, "VALOR": value})
    for source in audit.get("fuentes_oficiales", []):
        if isinstance(source, dict):
            rows.append({"CAMPO": f"fuente_{source.get('tipo')}", "VALOR": source.get("archivo")})
            rows.append({"CAMPO": f"sha256_{source.get('tipo')}", "VALOR": source.get("sha256")})
    for file_record in audit.get("archivos_utilizados", []):
        if isinstance(file_record, dict):
            prefix = str(file_record.get("tipo"))
            for key, value in file_record.items():
                if key == "tipo":
                    continue
                rows.append({"CAMPO": f"{prefix}_{key}", "VALOR": value})
    return pd.DataFrame(rows)
