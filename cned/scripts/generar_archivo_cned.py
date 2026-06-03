"""Generador base de archivo CNED.

No genera archivos de subida reales hasta contar con insumo oficial,
estructura de carga y reglas de mapeo validadas.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


LOGGER = logging.getLogger("generar_archivo_cned")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = repo_root()
    report_dir = root / "cned" / "resultados" / "reportes"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"generacion_cned_base_{timestamp}.md"

    lines = [
        "# Generacion base CNED",
        "",
        f"- Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"- Repo: {root}",
        "- Archivo de subida generado: NO",
        "- Motivo: falta insumo oficial, instructivo de estructura y mapeo validado.",
        "- Estado: ejecucion base sin insumos CNED cargados",
        "- Dictamen: GENERACION_CNED_NO_EJECUTADA_POR_FALTA_DE_INSUMO_OFICIAL",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Reporte de generacion base: %s", report_path)
    LOGGER.info("No se genero archivo de subida CNED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
