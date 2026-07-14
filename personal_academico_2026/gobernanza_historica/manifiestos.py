"""Escritura de manifiestos y auditorias de gobernanza historica."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .configuracion import TRANSFORMER_VERSION
from .descubrimiento_fuentes import sha256_file


def json_default(value: Any) -> Any:
    """Serializa valores no nativos para JSON."""

    if isinstance(value, Path):
        return str(value)
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def records(frame: pd.DataFrame) -> list[dict[str, object]]:
    """Convierte DataFrame a registros JSON estables."""

    if frame.empty:
        return []
    return frame.where(pd.notna(frame), "").to_dict(orient="records")


def write_json(path: Path, payload: dict[str, object] | list[dict[str, object]]) -> Path:
    """Escribe JSON gobernado."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=json_default) + "\n", encoding="utf-8")
    return path


def write_csv(path: Path, frame: pd.DataFrame) -> Path:
    """Escribe CSV gobernado con separador estable."""

    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
    return path


def audit_dir(project_root: Path) -> Path:
    """Crea nueva auditoria timestamp sin sobrescribir."""

    target = project_root / "auditorias" / f"gobernanza_historica_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    target.mkdir(parents=True, exist_ok=False)
    return target


def schema_payload(homologation: pd.DataFrame) -> dict[str, object]:
    """Construye schema homologado sin datos personales."""

    return {
        "version_transformador": TRANSFORMER_VERSION,
        "reglas": records(homologation),
        "politica_valores_no_disponibles": "NO_DISPONIBLE_EN_ESE_AÑO",
        "politica_no_imputacion": "No se inventan valores, no se rellenan ceros y no se copian valores entre anios.",
    }


def versions_payload(frozen: pd.DataFrame, normalized: pd.DataFrame) -> dict[str, object]:
    """Construye configuracion permanente por anio."""

    normalized_by_year = {int(row["anio"]): row for _idx, row in normalized.iterrows()} if not normalized.empty else {}
    payload: dict[str, object] = {}
    for _index, row in frozen.iterrows():
        year = int(row["anio"])
        normalized_row = normalized_by_year.get(year)
        payload[str(year)] = {
            "archivo": row.get("archivo", ""),
            "ruta_original": row.get("ruta_original", ""),
            "ruta_gobernada": row.get("ruta_gobernada", ""),
            "ruta_normalizada": "" if normalized_row is None else normalized_row.get("ruta_normalizada", ""),
            "formato_normalizado": "" if normalized_row is None else normalized_row.get("formato", ""),
            "sha256": row.get("sha256_original", ""),
            "estado": row.get("estado", ""),
            "version": row.get("version", ""),
            "fecha_congelamiento": row.get("fecha_congelamiento", ""),
            "observaciones": row.get("observaciones", ""),
        }
    return payload


def markdown_summary(
    inventory: pd.DataFrame,
    frozen: pd.DataFrame,
    normalized: pd.DataFrame,
    validation: pd.DataFrame,
) -> str:
    """Genera resumen ejecutivo sin datos personales."""

    lines = [
        "# Gobernanza Historica Personal Academico SIES",
        "",
        "Fase 1: infraestructura historica gobernada. No calcula KPI historicos.",
        "",
        f"- Fuentes candidatas inventariadas: {len(inventory)}",
        f"- Fuentes congeladas: {len(frozen)}",
        f"- Versiones normalizadas: {len(normalized)}",
        f"- Validaciones OK: {int(validation['severidad'].eq('OK').sum()) if not validation.empty else 0}",
        f"- Validaciones no OK: {int(validation['severidad'].ne('OK').sum()) if not validation.empty else 0}",
        "",
        "## Fuentes Por Anio",
        "",
    ]
    for _index, row in frozen.iterrows():
        lines.append(
            f"- {int(row['anio'])}: {row.get('archivo')} | sha256={row.get('sha256_original')} | estado={row.get('estado')}"
        )
    lines.extend(
        [
            "",
            "## Restricciones",
            "",
            "- No se modificaron fuentes OneDrive.",
            "- No se integro al flujo PES.",
            "- No se recalculo rotacion.",
            "- Las fuentes restringidas y normalizadas quedan ignoradas por .gitignore.",
        ]
    )
    return "\n".join(lines) + "\n"


def artifact_hashes(paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    """Calcula hashes de artefactos existentes."""

    return {
        key: {"path": str(path), "sha256": sha256_file(path)}
        for key, path in paths.items()
        if path.exists()
    }


def write_manifests(
    project_root: Path,
    inventory: pd.DataFrame,
    frozen: pd.DataFrame,
    normalized: pd.DataFrame,
    homologation: pd.DataFrame,
    validation: pd.DataFrame,
    commands: list[str],
) -> dict[str, Path]:
    """Escribe manifiestos permanentes y auditoria timestamp."""

    manifests_root = project_root / "data" / "manifests"
    target_audit = audit_dir(project_root)
    artifacts: dict[str, Path] = {}
    fuentes_payload = {"version_transformador": TRANSFORMER_VERSION, "fuentes": records(frozen), "normalizados": records(normalized)}
    versions = versions_payload(frozen, normalized)
    schema = schema_payload(homologation)

    artifacts["fuentes_json"] = write_json(manifests_root / "fuentes_personal_academico.json", fuentes_payload)
    artifacts["fuentes_csv"] = write_csv(manifests_root / "fuentes_personal_academico.csv", frozen)
    artifacts["schema_json"] = write_json(manifests_root / "schema_homologado.json", schema)
    artifacts["hashes_csv"] = write_csv(manifests_root / "hashes_fuentes.csv", frozen[["anio", "archivo", "ruta_gobernada", "sha256_original", "sha256_gobernado"]])
    artifacts["versiones_json"] = write_json(manifests_root / "versiones_fuentes.json", versions)
    artifacts["config_json"] = write_json(manifests_root / "config_fuentes_aprobadas.json", versions)
    artifacts["homologacion_json"] = write_json(manifests_root / "homologacion_columnas.json", records(homologation))

    artifacts["audit_inventario_csv"] = write_csv(target_audit / "01_inventario_completo.csv", inventory)
    artifacts["audit_fuentes_csv"] = write_csv(target_audit / "02_fuentes_congeladas.csv", frozen)
    artifacts["audit_hashes_csv"] = write_csv(target_audit / "03_hashes_fuentes.csv", frozen[["anio", "archivo", "sha256_original", "sha256_gobernado", "integridad_copia"]])
    artifacts["audit_homologacion_csv"] = write_csv(target_audit / "04_homologacion_columnas.csv", homologation)
    artifacts["audit_normalizados_csv"] = write_csv(target_audit / "05_normalizaciones.csv", normalized)
    artifacts["audit_integridad_csv"] = write_csv(target_audit / "06_validacion_integridad.csv", validation)
    artifacts["audit_diccionario_json"] = write_json(target_audit / "07_diccionario.json", schema)
    artifacts["audit_config_json"] = write_json(target_audit / "08_configuracion_fuentes.json", versions)
    artifacts["audit_resumen_md"] = target_audit / "09_resumen_gobernanza.md"
    artifacts["audit_resumen_md"].write_text(markdown_summary(inventory, frozen, normalized, validation), encoding="utf-8")
    audit_payload = {
        "fecha": datetime.now().date().isoformat(),
        "hora": datetime.now().time().replace(microsecond=0).isoformat(),
        "version_transformador": TRANSFORMER_VERSION,
        "commands": commands,
        "inventario_total": len(inventory),
        "fuentes_congeladas": len(frozen),
        "normalizados": len(normalized),
        "validaciones": records(validation),
        "artefactos": artifact_hashes(artifacts),
    }
    artifacts["audit_resumen_json"] = write_json(target_audit / "10_resumen_gobernanza.json", audit_payload)
    artifacts["audit_dir"] = target_audit
    return artifacts
