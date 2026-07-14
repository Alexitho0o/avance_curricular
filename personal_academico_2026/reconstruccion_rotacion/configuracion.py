"""Carga gobernada de configuracion aprobada Fase 1."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


EXPECTED_UNIVERSES = {2022: 71, 2023: 70, 2024: 85, 2025: 124, 2026: 202}


def project_root() -> Path:
    """Resuelve raiz del subproyecto Personal Academico."""

    return Path(__file__).resolve().parents[1]


def load_config() -> dict[str, dict[str, object]]:
    """Carga config_fuentes_aprobadas.json sin modificarlo."""

    path = project_root() / "data" / "manifests" / "config_fuentes_aprobadas.json"
    return json.loads(path.read_text(encoding="utf-8"))


def config_frame(config: dict[str, dict[str, object]]) -> pd.DataFrame:
    """Convierte configuracion aprobada en tabla."""

    rows = []
    for year, payload in sorted(config.items()):
        rows.append({"anio": int(year), **payload})
    return pd.DataFrame(rows)


def ensure_project_local(path_value: object) -> Path:
    """Valida que una ruta de consumo operativo viva dentro del proyecto."""

    path = Path(str(path_value))
    root = project_root().resolve()
    resolved = path.resolve()
    if "OneDrive" in resolved.as_posix():
        raise ValueError(f"Ruta no autorizada para Fase 2A: {resolved}")
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Ruta fuera del subproyecto Personal Academico: {resolved}") from exc
    return resolved
