"""CLI de reconstruccion longitudinal y KPI oficial Fase 2A."""

from __future__ import annotations

import argparse
import logging

from .configuracion import EXPECTED_UNIVERSES, config_frame, load_config
from .carga import build_longitudinal, verify_config_and_sources
from .exportacion import export_all
from .reconstruccion import build_pair_outputs, build_panel, desaggregate, detect_mobility, detect_reentries
from .validaciones import validate_longitudinal


def build_parser() -> argparse.ArgumentParser:
    """Construye parser CLI."""

    parser = argparse.ArgumentParser(description="Reconstruye panel longitudinal y KPI rotacion Fase 2A.")
    parser.add_argument("--log-level", default="INFO")
    return parser


def configure_logging(level: str) -> logging.Logger:
    """Configura logging."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    return logging.getLogger("personal_academico_2026.reconstruccion_rotacion")


def run(logger: logging.Logger) -> dict[str, object]:
    """Ejecuta reconstruccion desde fuentes gobernadas."""

    config = load_config()
    raw, config_validations = verify_config_and_sources(config)
    if raw.empty and config_validations["SEVERIDAD"].eq("BLOQUEANTE").any():
        raise RuntimeError("Validacion bloqueante de configuracion o universos.")
    longitudinal = build_longitudinal(raw)
    validations = validate_longitudinal(longitudinal)
    validations = __import__("pandas").concat([config_validations, validations], ignore_index=True, sort=False)
    years = sorted(EXPECTED_UNIVERSES)
    panel = build_panel(longitudinal, years)
    detail, kpi = build_pair_outputs(longitudinal, years)
    reentries = detect_reentries(panel, years)
    mobility = detect_mobility(detail, longitudinal)
    desaggs = {
        "sexo": desaggregate(detail, "SEXO", "SEXO"),
        "formacion": desaggregate(detail, "FORMACION", "FORMACION"),
        "horas": desaggregate(detail, "TRAMO_HORAS", "TRAMO_HORAS"),
        "cargo": desaggregate(detail, "CARGO_NORMALIZADO", "CARGO"),
        "programa": desaggregate(detail, "PROGRAMA_PRINCIPAL", "PROGRAMA"),
        "jerarquia": desaggregate(detail, "JERARQUIA_OCDE", "JERARQUIA"),
        "adscripcion": desaggregate(detail, "ADSCRIPCION", "ADSCRIPCION"),
        "tipo_contractual": desaggregate(detail, "TIPO_CONTRACTUAL", "TIPO_CONTRACTUAL"),
    }
    sources = config_frame(config)
    outputs = export_all(
        longitudinal=longitudinal,
        panel=panel,
        detail=detail,
        kpi=kpi,
        reentries=reentries,
        mobility=mobility,
        desaggs=desaggs,
        validations=validations,
        sources=sources,
        commands=["python3 -m personal_academico_2026.reconstruccion_rotacion"],
    )
    logger.info("Auditoria Fase 2A creada en %s", outputs["audit_dir"])
    return outputs


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada."""

    parser = build_parser()
    args = parser.parse_args(argv)
    logger = configure_logging(args.log_level)
    run(logger)
    return 0
