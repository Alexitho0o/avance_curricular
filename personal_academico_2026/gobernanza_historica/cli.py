"""CLI de Fase 1 para gobernanza historica de Personal Academico."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .configuracion import build_approved_sources
from .congelamiento import freeze_sources
from .homologacion import read_official_headers
from .integridad import validate_governance
from .inventario import build_inventory
from .manifiestos import write_manifests
from .normalizacion import normalize_sources


def personal_project_root() -> Path:
    """Resuelve raiz del subproyecto Personal Academico 2026."""

    return Path(__file__).resolve().parents[1]


def repository_root() -> Path:
    """Resuelve raiz del repositorio."""

    return Path(__file__).resolve().parents[2]


def default_structure_path() -> Path:
    """Busca estructura oficial en institucion 2026 dentro del repositorio."""

    root = repository_root()
    matches = sorted(root.glob("*Estructura_Personal_Acad*en_Institucio*n_2026.csv"))
    if not matches:
        raise FileNotFoundError("No se encontro estructura Personal Academico en Institucion 2026.")
    return matches[0]


def build_parser() -> argparse.ArgumentParser:
    """Construye parser CLI."""

    parser = argparse.ArgumentParser(description="Construye gobernanza historica Fase 1 sin calcular KPI.")
    parser.add_argument("--historico-root", required=True, type=Path, help="Carpeta OneDrive fuente maestra institucional.")
    parser.add_argument("--desde-anio", type=int, default=2022, help="Primer anio gobernado.")
    parser.add_argument("--hasta-anio", type=int, default=2026, help="Ultimo anio gobernado.")
    parser.add_argument("--estructura-en", type=Path, default=None, help="Estructura oficial en institucion 2026.")
    parser.add_argument(
        "--responsable",
        default="Codex Fase 1 - pendiente validacion institucional",
        help="Responsable registrado para fuentes congeladas.",
    )
    parser.add_argument("--log-level", default="INFO", help="Nivel de logging.")
    return parser


def configure_logging(level: str) -> logging.Logger:
    """Configura logging de consola."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    return logging.getLogger("personal_academico_2026.gobernanza_historica")


def run(args: argparse.Namespace, logger: logging.Logger) -> dict[str, Path]:
    """Ejecuta Fase 1 de gobernanza historica."""

    if not args.historico_root.exists():
        raise FileNotFoundError(f"No existe historico-root: {args.historico_root}")
    project_root = personal_project_root()
    structure_path = args.estructura_en or default_structure_path()
    official_headers = read_official_headers(structure_path)
    expected_years = list(range(args.desde_anio, args.hasta_anio + 1))

    logger.info("Inventariando candidatos en %s", args.historico_root)
    inventory = build_inventory(args.historico_root, official_headers)
    logger.info("Candidatos inventariados: %s", len(inventory))
    approved = build_approved_sources(args.historico_root, inventory, args.responsable)
    approved = approved[approved["anio"].isin(expected_years)].reset_index(drop=True)
    frozen, events = freeze_sources(project_root, approved)
    if events:
        logger.warning("Eventos de congelamiento: %s", events)
    normalized, homologation = normalize_sources(project_root, frozen, official_headers)
    validation = validate_governance(approved, frozen, normalized, expected_years)
    command = [
        "python3 -m personal_academico_2026.gobernanza_historica",
        f"--historico-root {args.historico_root}",
        f"--desde-anio {args.desde_anio}",
        f"--hasta-anio {args.hasta_anio}",
    ]
    artifacts = write_manifests(
        project_root=project_root,
        inventory=inventory,
        frozen=frozen,
        normalized=normalized,
        homologation=homologation,
        validation=validation,
        commands=[" ".join(command)],
    )
    logger.info("Auditoria creada en %s", artifacts["audit_dir"])
    return artifacts


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada."""

    parser = build_parser()
    args = parser.parse_args(argv)
    logger = configure_logging(args.log_level)
    run(args, logger)
    return 0
