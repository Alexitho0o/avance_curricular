"""Congelamiento local de fuentes anuales gobernadas."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from .descubrimiento_fuentes import iso_from_timestamp, sha256_file


def raw_restricted_root(project_root: Path) -> Path:
    """Ruta de fuentes originales gobernadas restringidas."""

    return project_root / "data" / "raw_restricted"


def freeze_sources(project_root: Path, approved: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Copia fuentes aprobadas sin modificar contenido ni nombre."""

    rows: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    root = raw_restricted_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    frozen_at = datetime.now().replace(microsecond=0).isoformat()
    for _index, source in approved.iterrows():
        year = int(source["anio"])
        source_path = Path(str(source["ruta_original"]))
        year_dir = root / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        target_path = year_dir / str(source["archivo"])
        if not source_path.exists():
            events.append({"anio": year, "evento": "NO_CONGELADO_FUENTE_NO_EXISTE", "ruta": str(source_path)})
            continue
        source_hash = sha256_file(source_path)
        if target_path.exists():
            target_hash = sha256_file(target_path)
            if target_hash != source_hash:
                raise FileExistsError(f"Copia gobernada existe con hash distinto: {target_path}")
            action = "YA_EXISTE_MISMO_SHA"
        else:
            shutil.copy2(source_path, target_path)
            target_hash = sha256_file(target_path)
            action = "COPIA_GOBERNADA_CREADA"
        stat = target_path.stat()
        rows.append(
            {
                **source.to_dict(),
                "ruta_gobernada": str(target_path),
                "sha256_original": source_hash,
                "sha256_gobernado": target_hash,
                "size_bytes_gobernado": stat.st_size,
                "fecha_modificacion_gobernado": iso_from_timestamp(stat.st_mtime),
                "fecha_congelamiento": frozen_at,
                "accion_congelamiento": action,
                "integridad_copia": "OK" if source_hash == target_hash else "ERROR_HASH_DISTINTO",
            }
        )
    return pd.DataFrame(rows), events
