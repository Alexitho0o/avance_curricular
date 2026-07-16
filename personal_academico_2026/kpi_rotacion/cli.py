"""CLI del modulo desacoplado de rotacion de personal academico."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

from .auditoria import build_audit, elapsed_seconds, start_timer
from .comparacion import compare_years
from .config import (
    RunConfig,
    TipoArchivo,
    default_output_dir,
    resolve_default_sources,
    structure_path_for_type,
)
from .exportacion import export_all
from .historico_consolidacion import build_historical_tables
from .historico_exportacion import export_historical_package
from .historico_fuentes import inventory_sources
from .kpis import build_kpi_tables
from .lectura import read_academic_file, read_official_headers
from .validacion import validate_cross_year_consistency, validate_dataset


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos del CLI."""

    parser = argparse.ArgumentParser(
        description="Calcula tasa oficial SIES de rotacion de personal academico."
    )
    parser.add_argument("--input-base", type=Path, help="Archivo del anio base.")
    parser.add_argument("--input-comparacion", type=Path, help="Archivo del anio t+1.")
    parser.add_argument("--anio-base", type=int, help="Anio base t.")
    parser.add_argument("--anio-comparacion", type=int, help="Anio de comparacion t+1.")
    parser.add_argument("--historico-root", type=Path, default=None, help="Carpeta historica institucional a inventariar.")
    parser.add_argument("--desde-anio", type=int, default=None, help="Primer anio del rango historico a evaluar.")
    parser.add_argument("--hasta-anio", type=int, default=None, help="Ultimo anio del rango historico a evaluar.")
    parser.add_argument(
        "--modo",
        choices=["comparacion", "auditoria"],
        default="comparacion",
        help="Modo de ejecucion historica. Auditoria conserva estados conservadores.",
    )
    parser.add_argument(
        "--historico-output-base",
        type=Path,
        default=None,
        help="Carpeta base para auditorias historicas con timestamp.",
    )
    parser.add_argument(
        "--tipo-archivo",
        choices=["en_institucion", "fuera_institucion"],
        default="en_institucion",
        help="Tipo de estructura oficial a validar.",
    )
    parser.add_argument("--instructivo", type=Path, default=None, help="Ruta al instructivo oficial 2026.")
    parser.add_argument("--estructura-en", type=Path, default=None, help="Ruta a estructura en institucion 2026.")
    parser.add_argument("--estructura-fuera", type=Path, default=None, help="Ruta a estructura fuera institucion 2026.")
    parser.add_argument("--output-dir", type=Path, default=default_output_dir(), help="Carpeta de salida.")
    parser.add_argument("--log-level", default="INFO", help="Nivel de logging.")
    return parser


def configure_logging(level: str) -> logging.Logger:
    """Configura logging de consola para una ejecucion."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    return logging.getLogger("personal_academico_2026.kpi_rotacion")


def config_from_args(args: argparse.Namespace) -> RunConfig:
    """Convierte argumentos CLI en configuracion inmutable."""

    missing = [
        name
        for name, value in [
            ("--input-base", args.input_base),
            ("--input-comparacion", args.input_comparacion),
            ("--anio-base", args.anio_base),
            ("--anio-comparacion", args.anio_comparacion),
        ]
        if value is None
    ]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Faltan argumentos para comparacion manual: {joined}")
    sources = resolve_default_sources(
        instructivo=args.instructivo,
        estructura_en_institucion=args.estructura_en,
        estructura_fuera_institucion=args.estructura_fuera,
    )
    return RunConfig(
        input_base=args.input_base,
        input_comparacion=args.input_comparacion,
        anio_base=args.anio_base,
        anio_comparacion=args.anio_comparacion,
        output_dir=args.output_dir,
        tipo_archivo=args.tipo_archivo,
        sources=sources,
    )


def run(config: RunConfig, logger: logging.Logger) -> dict[str, Path]:
    """Ejecuta lectura, validacion, comparacion, KPI, auditoria y exportacion."""

    timer = start_timer()
    structure_path = structure_path_for_type(config.sources, config.tipo_archivo)
    official_headers = read_official_headers(structure_path)
    logger.info("Estructura oficial cargada: %s columnas=%s", structure_path, len(official_headers))

    base_dataset = read_academic_file(config.input_base, official_headers, logger)
    comparison_dataset = read_academic_file(config.input_comparacion, official_headers, logger)

    issues = []
    issues.extend(validate_dataset(base_dataset, official_headers, config.anio_base))
    issues.extend(validate_dataset(comparison_dataset, official_headers, config.anio_comparacion))
    issues.extend(
        validate_cross_year_consistency(
            base_dataset,
            comparison_dataset,
            config.anio_base,
            config.anio_comparacion,
        )
    )

    comparison = compare_years(
        base_dataset.frame,
        comparison_dataset.frame,
        config.anio_base,
        config.anio_comparacion,
        official_headers,
    )
    kpi_tables = build_kpi_tables(
        comparison,
        config.anio_base,
        config.anio_comparacion,
        official_headers,
    )
    audit = build_audit(
        config=config,
        base_dataset=base_dataset,
        comparison_dataset=comparison_dataset,
        issues=issues,
        elapsed=elapsed_seconds(timer),
    )
    outputs = export_all(config.output_dir, comparison, kpi_tables, issues, audit)
    logger.info("Exportaciones generadas: %s", {key: str(value) for key, value in outputs.items()})
    return outputs


def run_historical(args: argparse.Namespace, logger: logging.Logger) -> dict[str, Path]:
    """Ejecuta inventario, seleccion, KPI historico, auditoria y exportacion."""

    if args.historico_root is None:
        raise ValueError("Debe indicar --historico-root para ejecucion historica.")
    if not args.historico_root.exists():
        raise FileNotFoundError(f"No existe la carpeta historica: {args.historico_root}")

    started_at = datetime.now()
    start = time.perf_counter()
    sources = resolve_default_sources(
        instructivo=args.instructivo,
        estructura_en_institucion=args.estructura_en,
        estructura_fuera_institucion=args.estructura_fuera,
    )
    structure_path = structure_path_for_type(sources, args.tipo_archivo)
    official_headers = read_official_headers(structure_path)
    logger.info("Inventariando fuentes historicas en: %s", args.historico_root)
    inventory = inventory_sources(args.historico_root, official_headers)
    logger.info("Fuentes inventariadas: %s", len(inventory))
    tables = build_historical_tables(
        inventory,
        official_headers,
        desde_anio=args.desde_anio,
        hasta_anio=args.hasta_anio,
    )
    command = [
        "python3 -m personal_academico_2026.kpi_rotacion",
        f"--historico-root {args.historico_root}",
        *( [f"--desde-anio {args.desde_anio}"] if args.desde_anio is not None else [] ),
        *( [f"--hasta-anio {args.hasta_anio}"] if args.hasta_anio is not None else [] ),
        f"--modo {args.modo}",
    ]
    outputs = export_historical_package(
        tables=tables,
        root=args.historico_root,
        desde_anio=args.desde_anio,
        hasta_anio=args.hasta_anio,
        modo=args.modo,
        commands=[" ".join(command)],
        started_at=started_at,
        elapsed_seconds=time.perf_counter() - start,
        output_base_dir=args.historico_output_base,
    )
    logger.info("Auditoria historica generada en: %s", outputs["output_dir"])
    return outputs


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de linea de comandos."""

    parser = build_parser()
    args = parser.parse_args(argv)
    logger = configure_logging(args.log_level)
    if args.historico_root is not None:
        run_historical(args, logger)
    else:
        config = config_from_args(args)
        run(config, logger)
    return 0
