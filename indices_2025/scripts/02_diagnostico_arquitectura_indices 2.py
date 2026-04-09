#!/usr/bin/env python3
"""FASE 2: diagnostico global de arquitectura INDICES 2025."""

from __future__ import annotations

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR / "core"))

from indices_core import configurar_logger, escribir_json, timestamp_actual  # noqa: E402
from indices_pipeline import (  # noqa: E402
    FASE0_SECTIONS,
    FASE1_DICT,
    MANUAL_PATH,
    PROJECT_DIR,
    PROCESOS_CSV,
    PROCESOS_JSON,
    REQUIRED_DIRS,
    cargar_o_crear_catalogo,
    process_paths,
)


REPORT_PATH = PROJECT_DIR / "resultados" / "reportes_validacion" / "FASE2_DIAGNOSTICO_ARQUITECTURA_INDICES_2025.md"
STATE_PATH = PROJECT_DIR / "resultados" / "auditoria" / "estado_arquitectura_indices_2025.json"
LOG_PATH = PROJECT_DIR / "resultados" / "logs" / "fase2_diagnostico_arquitectura_indices.log"


def md(value: object) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def path_state(path: Path) -> dict:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def collect_state() -> dict:
    procesos = cargar_o_crear_catalogo()
    proceso_estados = []
    for index, process in enumerate(procesos, start=3):
        paths = process_paths(process, index)
        files = {name: path_state(path) for name, path in paths.items()}
        pending = [name for name, info in files.items() if not info["exists"]]
        proceso_estados.append(
            {
                "id_proceso": process["id_proceso"],
                "nombre_proceso": process["nombre_proceso"],
                "tipo_proceso": process["tipo_proceso"],
                "estado_implementacion": process["estado_implementacion"],
                "archivos": files,
                "pendientes": pending,
            }
        )

    expected_global = {
        "manual": path_state(MANUAL_PATH),
        "fase0_secciones": path_state(FASE0_SECTIONS),
        "fase1_diccionario_evolucion_carreras": path_state(FASE1_DICT),
        "procesos_json": path_state(PROCESOS_JSON),
        "procesos_csv": path_state(PROCESOS_CSV),
        "estado_proyecto": path_state(PROJECT_DIR / "resultados" / "auditoria" / "ESTADO_PROYECTO_INDICES_2025.md"),
        "bitacora_decisiones": path_state(PROJECT_DIR / "resultados" / "auditoria" / "BITACORA_DECISIONES_INDICES_2025.md"),
    }
    folders = [
        {
            "path": str(path),
            "relative_path": str(path.relative_to(PROJECT_DIR)),
            "exists": path.exists(),
        }
        for path in REQUIRED_DIRS
    ]
    return {
        "fecha_hora": timestamp_actual(),
        "fuente_oficial": str(MANUAL_PATH),
        "artefactos_globales": expected_global,
        "carpetas": folders,
        "procesos": proceso_estados,
    }


def risks(state: dict) -> list[str]:
    risks_found = [
        "Los procesos quedan en estado esqueleto; no validan datos reales todavía.",
        "Las reglas específicas no se completaron salvo referencias ya disponibles en FASE 1 para Evolución de Carreras.",
        "Las tablas del manual provienen de texto extraído y pueden requerir revisión manual antes de reglas bloqueantes.",
        "Los fixtures creados son vacíos; se necesitan archivos reales de prueba para FASE 3.",
        "Los catálogos CNED/SIES mencionados por el manual quedan como dependencia a confirmar, no como reglas implementadas.",
    ]
    missing = [
        process["id_proceso"]
        for process in state["procesos"]
        if process["pendientes"]
    ]
    if missing:
        risks_found.append(f"Hay procesos con archivos faltantes: {', '.join(missing)}.")
    return risks_found


def recommendation(state: dict) -> str:
    missing = sum(len(process["pendientes"]) for process in state["procesos"])
    if missing:
        return "Completar archivos faltantes de arquitectura antes de FASE 3."
    return (
        "FASE 3 — Implementación del primer validador funcional, comenzando por CSV "
        "Evolución de Carreras, usando el diccionario técnico de FASE 1 y la arquitectura "
        "de esqueletos de FASE 2."
    )


def build_report(state: dict) -> str:
    procesos = state["procesos"]
    report = [
        "# FASE 2 — Diagnóstico de arquitectura INDICES 2025",
        "",
        "## 1. Fuente oficial utilizada",
        f"- Manual: `{state['fuente_oficial']}`",
        f"- Fecha/hora de ejecución: `{state['fecha_hora']}`",
        "",
        "## 2. Artefactos previos revisados",
    ]
    for name, info in state["artefactos_globales"].items():
        report.append(f"- `{name}`: {'existe' if info['exists'] else 'faltante'} — `{info['path']}`")

    report.extend(
        [
            "",
            "## 3. Procesos detectados",
            "| ID | Nombre | Tipo | Estado | Pendientes |",
            "|---|---|---|---|---:|",
        ]
    )
    for process in procesos:
        report.append(
            "| "
            f"{md(process['id_proceso'])} | {md(process['nombre_proceso'])} | "
            f"{md(process['tipo_proceso'])} | {md(process['estado_implementacion'])} | "
            f"{len(process['pendientes'])} |"
        )

    report.extend(["", "## 4. Estructura de carpetas"])
    for folder in state["carpetas"]:
        report.append(f"- `{folder['relative_path']}`: {'OK' if folder['exists'] else 'FALTANTE'}")

    sections = [
        ("## 5. Scripts esqueleto creados", "script"),
        ("## 6. Configuraciones YAML creadas", "yaml"),
        ("## 7. Diccionarios esqueleto creados", "diccionario"),
        ("## 8. Plantillas Markdown creadas", "plantilla_markdown"),
        ("## 9. Plantillas Excel creadas", "plantilla_excel"),
        ("## 10. Fixtures creados", "fixture"),
    ]
    for title, key in sections:
        report.extend(["", title])
        for process in procesos:
            info = process["archivos"][key]
            report.append(
                f"- `{process['id_proceso']}`: {'OK' if info['exists'] else 'FALTANTE'} — `{info['path']}`"
            )

    report.extend(
        [
            "",
            "## 11. Estado por proceso",
            "| Proceso | Script | YAML | Diccionario | Excel | Markdown | Fixture |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for process in procesos:
        files = process["archivos"]
        report.append(
            "| "
            f"{md(process['id_proceso'])} | "
            f"{'OK' if files['script']['exists'] else 'FALTANTE'} | "
            f"{'OK' if files['yaml']['exists'] else 'FALTANTE'} | "
            f"{'OK' if files['diccionario']['exists'] else 'FALTANTE'} | "
            f"{'OK' if files['plantilla_excel']['exists'] else 'FALTANTE'} | "
            f"{'OK' if files['plantilla_markdown']['exists'] else 'FALTANTE'} | "
            f"{'OK' if files['fixture']['exists'] else 'FALTANTE'} |"
        )

    report.extend(["", "## 12. Riesgos técnicos"])
    for item in risks(state):
        report.append(f"- {item}")

    report.extend(
        [
            "",
            "## 13. Recomendación de FASE 3",
            recommendation(state),
            "",
            "## 14. Punto exacto para reanudar",
            "PUNTO EXACTO PARA REANUDAR:",
            "FASE 3 — Implementación del primer validador funcional, comenzando por CSV Evolución de Carreras, usando el diccionario técnico de FASE 1 y la arquitectura de esqueletos de FASE 2.",
            "",
        ]
    )
    return "\n".join(report)


def main() -> None:
    logger = configurar_logger("fase2_diagnostico_arquitectura_indices", LOG_PATH)
    logger.info("Inicio diagnostico FASE 2")
    if not MANUAL_PATH.exists():
        raise SystemExit(f"No existe manual requerido: {MANUAL_PATH}")
    state = collect_state()
    escribir_json(STATE_PATH, state)
    REPORT_PATH.write_text(build_report(state), encoding="utf-8")
    logger.info("Procesos revisados: %s", len(state["procesos"]))
    logger.info("Reporte generado: %s", REPORT_PATH)
    logger.info("Estado JSON generado: %s", STATE_PATH)
    logger.info("Fin diagnostico FASE 2")
    print(f"Reporte FASE 2: {REPORT_PATH}")
    print(f"Estado arquitectura: {STATE_PATH}")
    print(f"Procesos revisados: {len(state['procesos'])}")
    print(f"Recomendación FASE 3: {recommendation(state)}")


if __name__ == "__main__":
    main()
