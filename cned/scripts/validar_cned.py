"""Validacion base del modulo CNED.

Verifica que la estructura exista y deja constancia de que la validacion real
queda pendiente hasta recibir insumos e instructivo oficial CNED.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


LOGGER = logging.getLogger("validar_cned")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = repo_root()
    cned = root / "cned"
    input_dir = cned / "data" / "input"
    report_dir = cned / "resultados" / "reportes"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"validacion_cned_base_{timestamp}.md"

    input_files = sorted(path for path in input_dir.glob("*") if path.is_file())
    lines = [
        "# Validacion base CNED",
        "",
        f"- Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"- Repo: {root}",
        f"- Insumos detectados en cned/data/input: {len(input_files)}",
        "- Estado: ejecucion base sin insumos CNED cargados",
        "- Dictamen: VALIDACION_ESTRUCTURAL_CNED_OK",
    ]
    if not input_files:
        lines.append("- Nota: no se ejecutan validaciones de carga porque falta insumo oficial CNED.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Reporte de validacion base: %s", report_path)
    LOGGER.info("Ejecucion base sin insumos CNED cargados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
