"""Auditoria base del modulo CNED.

Este script valida la estructura minima del modulo CNED y emite un reporte
estructural. No procesa datos reales hasta que existan insumos oficiales.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


LOGGER = logging.getLogger("auditar_cned")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = repo_root()
    cned = root / "cned"
    required_dirs = [
        cned / "data" / "input",
        cned / "data" / "catalogos",
        cned / "data" / "processed",
        cned / "scripts",
        cned / "resultados" / "archivos_subida",
        cned / "resultados" / "auditorias",
        cned / "resultados" / "reportes",
        cned / "docs",
        cned / "tests",
    ]

    missing = [path for path in required_dirs if not path.exists()]
    report_dir = cned / "resultados" / "reportes"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"auditoria_cned_base_{timestamp}.md"

    lines = [
        "# Auditoria base CNED",
        "",
        f"- Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"- Repo: {root}",
        "- Tipo ejecucion: base sin insumos CNED cargados",
        f"- Directorios requeridos: {len(required_dirs)}",
        f"- Directorios faltantes: {len(missing)}",
    ]
    if missing:
        lines.append("")
        lines.append("## Faltantes")
        lines.extend(f"- {path.relative_to(root)}" for path in missing)
    else:
        lines.append("- Estado estructura: OK")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Reporte de auditoria base: %s", report_path)
    if missing:
        LOGGER.error("Faltan directorios CNED requeridos.")
        return 1
    LOGGER.info("Ejecucion base sin insumos CNED cargados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
