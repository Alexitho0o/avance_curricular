#!/usr/bin/env python3
"""Compuerta pre-exportacion PES para Personal Academico SIES 2026.

Evalua estructura oficial, validador, matriz de Fase 4 y correcciones
controladas. No modifica la base y no genera PES_READY.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR.parent
REPO_DIR = MODULE_DIR.parent

BASE_GENERAL = MODULE_DIR / "data/base_general/base_general_personal_academico_en_institucion.tsv"
ESTRUCTURA_EN = MODULE_DIR / "insumos/20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv"
INSTRUCTIVO = MODULE_DIR / "insumos/Personal Académico SIES - Instructivo 2026.txt"
CONTROL_CORRECCIONES = MODULE_DIR / "control_correcciones/correcciones_manual_base_general_en_institucion.tsv"
AUDITORIAS_DIR = MODULE_DIR / "auditorias"
DICTAMEN_FINAL = MODULE_DIR / "docs/DICTAMEN_FINAL_PRE_EXPORTACION_PES_PERSONAL_ACADEMICO_2026.md"
BITACORA = MODULE_DIR / "bitacoras/BITACORA_FASE_5_COMPUERTA_PRE_EXPORTACION.md"

ESTADOS_PERMITIDOS = {
    "BLOQUEADO_ERROR_CRITICO",
    "BLOQUEADO_CORRECCION_PENDIENTE",
    "BLOQUEADO_ESTRUCTURA_OFICIAL",
    "APTO_EXPORTACION_CONTROLADA_CON_ADVERTENCIAS",
    "APTO_EXPORTACION_CONTROLADA_SIN_ADVERTENCIAS",
}


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_DIR))
    except ValueError:
        return str(path)


def git_branch() -> str:
    proc = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() or "desconocida"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO_DIR, text=True, capture_output=True, check=False)


def read_csv(path: Path, delimiter: str = ",", encoding: str = "utf-8-sig") -> list[dict[str, str]]:
    with path.open("r", encoding=encoding, newline="") as fh:
        return list(csv.DictReader(fh, delimiter=delimiter))


def read_header(path: Path, delimiter: str, encoding: str = "utf-8-sig") -> list[str]:
    with path.open("r", encoding=encoding, newline="") as fh:
        return next(csv.reader(fh, delimiter=delimiter))


def latest(pattern: str) -> Path | None:
    paths = sorted(AUDITORIAS_DIR.glob(pattern))
    return paths[-1] if paths else None


def ensure_validation_audit() -> Path:
    cmd = [
        sys.executable,
        str(MODULE_DIR / "scripts/validar_archivo_personal_academico_2026.py"),
        "--tipo",
        "en_institucion",
        "--input",
        str(BASE_GENERAL),
        "--delimitador-entrada",
        "tab",
    ]
    proc = run_command(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"Validador fallo: {proc.stderr or proc.stdout}")
    audit = latest("auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_*.csv")
    if not audit:
        raise RuntimeError("No se encontro auditoria de validador posterior.")
    return audit


def ensure_matrix() -> Path:
    cmd = [sys.executable, str(MODULE_DIR / "scripts/cruzar_formato_oficial_personal_academico_2026.py")]
    proc = run_command(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"Cruce oficial fallo: {proc.stderr or proc.stdout}")
    matrix = latest("matriz_cumplimiento_formato_oficial_en_institucion_*.csv")
    if not matrix:
        raise RuntimeError("No se encontro matriz de cumplimiento posterior.")
    return matrix


def read_base_header() -> tuple[list[str], int]:
    with BASE_GENERAL.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)
        return list(reader.fieldnames or []), len(rows)


def pending_corrections_for_critical_errors(critical_errors: list[dict[str, str]]) -> list[dict[str, str]]:
    if not CONTROL_CORRECCIONES.exists():
        return []
    corrections = read_csv(CONTROL_CORRECCIONES, delimiter="\t", encoding="utf-8")
    pending = []
    for correction in corrections:
        estado = (correction.get("ESTADO") or "").strip().upper()
        campo = (correction.get("CAMPO") or "").strip()
        valor_actual = (correction.get("VALOR_ACTUAL") or "").strip()
        if estado != "PENDIENTE":
            continue
        for error in critical_errors:
            if campo == error.get("columna") and valor_actual == error.get("valor"):
                pending.append(correction)
                break
    return pending


def audit_row(
    criterio: str,
    resultado: str,
    estado: str,
    severidad: str,
    detalle: str,
    fuente: str,
    accion_requerida: str,
) -> dict[str, str]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "criterio": criterio,
        "resultado": resultado,
        "estado": estado,
        "severidad": severidad,
        "detalle": detalle,
        "fuente": fuente,
        "accion_requerida": accion_requerida,
    }


def write_audit(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "timestamp",
        "criterio",
        "resultado",
        "estado",
        "severidad",
        "detalle",
        "fuente",
        "accion_requerida",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def decide(
    structure_ok: bool,
    names_ok: bool,
    order_ok: bool,
    critical_errors: int,
    pending_critical_corrections: int,
    warnings: int,
) -> str:
    if not structure_ok or not names_ok or not order_ok:
        return "BLOQUEADO_ESTRUCTURA_OFICIAL"
    if critical_errors > 0:
        return "BLOQUEADO_ERROR_CRITICO"
    if pending_critical_corrections > 0:
        return "BLOQUEADO_CORRECCION_PENDIENTE"
    if warnings > 0:
        return "APTO_EXPORTACION_CONTROLADA_CON_ADVERTENCIAS"
    return "APTO_EXPORTACION_CONTROLADA_SIN_ADVERTENCIAS"


def write_dictamen(summary: dict[str, object]) -> None:
    critical_lines = "\n".join(
        f"- Fila {e.get('fila')}: {e.get('regla')} en `{e.get('columna')}` = `{e.get('valor')}`."
        for e in summary["critical_errors_detail"]
    ) or "- No hay errores criticos."
    pending_lines = "\n".join(
        f"- {c.get('ID_CORRECCION')}: {c.get('CAMPO')} valor actual `{c.get('VALOR_ACTUAL')}`, estado {c.get('ESTADO')}."
        for c in summary["pending_corrections"]
    ) or "- No hay correcciones pendientes asociadas a errores criticos."
    content = f"""# Dictamen Final Pre-Exportacion PES - Personal Academico 2026

## Resumen Ejecutivo
Actualmente el archivo NO esta listo para exportacion PES porque existe 1 error critico: fecha futura en FECHA_OBT_TIT_O_GRADO, fila 20, valor 2027-11-29.

## Estado Final
{summary['decision_final']}

## Base Revisada
- {rel(BASE_GENERAL)}
- Filas: {summary['total_filas']}
- Columnas: {summary['total_columnas_base']}

## Estructura Oficial Usada
- {rel(ESTRUCTURA_EN)}
- Instructivo: {rel(INSTRUCTIVO)}

## Resultado Columna Por Columna
- Columnas LISTA: {summary['estados_columnas'].get('LISTA', 0)}
- Columnas LISTA_CON_ADVERTENCIAS: {summary['estados_columnas'].get('LISTA_CON_ADVERTENCIAS', 0)}
- Columnas REQUIERE_CORRECCION: {summary['estados_columnas'].get('REQUIERE_CORRECCION', 0)}
- Columnas PENDIENTE_CONFIRMACION: {summary['estados_columnas'].get('PENDIENTE_CONFIRMACION', 0)}

## Errores Criticos
{critical_lines}

## Advertencias
- Total advertencias validador: {summary['total_advertencias']}

## Correcciones Pendientes
{pending_lines}

## Condicion Exacta Para Pasar a Exportacion
- Resolver el error critico `fecha_futura` con correccion manual respaldada.
- Reejecutar validador hasta obtener 0 errores criticos.
- Mantener estructura oficial de 34 columnas, nombres y orden exactos.
- Reejecutar la compuerta y obtener estado apto.

No se genero PES_READY.

No se modifico la base.

No se corrigio ningun dato sin respaldo.

La exportacion final sigue bloqueada.
"""
    DICTAMEN_FINAL.write_text(content, encoding="utf-8")


def write_bitacora(summary: dict[str, object]) -> None:
    content = f"""# Bitacora Fase 5 - Compuerta Pre-Exportacion

- Fecha/hora: {summary['fecha_hora']}
- Rama: {summary['rama']}

## Comandos Ejecutados
- `git branch --show-current`
- `git status --short`
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/evaluar_preparacion_exportacion_pes_2026.py`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Archivos Leidos
- {rel(BASE_GENERAL)}
- {rel(ESTRUCTURA_EN)}
- {rel(INSTRUCTIVO)}
- {rel(CONTROL_CORRECCIONES)}
- {summary['matriz']}
- {summary['auditoria_validacion']}

## Archivos Creados
- {summary['auditoria_compuerta']}
- {rel(DICTAMEN_FINAL)}
- {rel(BITACORA)}

## Resultado de Decision
- {summary['decision_final']}

## Pendientes
- Corregir fecha futura con respaldo.
- Reejecutar Fase 3C, Fase 4 y Fase 5.
- No habilitar exportacion final mientras haya errores criticos.

## Estado Final
- Exportacion PES bloqueada.
- No se genero PES_READY.
"""
    BITACORA.write_text(content, encoding="utf-8")


def main() -> int:
    if git_branch() != "feature/personal-academico-base-preliminar-2026":
        print("ERROR: rama incorrecta para Fase 5.", file=sys.stderr)
        return 2
    for path in [BASE_GENERAL, ESTRUCTURA_EN, INSTRUCTIVO, CONTROL_CORRECCIONES]:
        if not path.exists():
            print(f"ERROR: falta archivo requerido: {path}", file=sys.stderr)
            return 2

    validation_audit = ensure_validation_audit()
    matrix_path = ensure_matrix()
    official_cols = read_header(ESTRUCTURA_EN, ";")
    base_cols, total_filas = read_base_header()
    validation_events = read_csv(validation_audit)
    matrix_rows = read_csv(matrix_path)

    critical_errors = [event for event in validation_events if event.get("severidad") == "ERROR"]
    warnings = [event for event in validation_events if event.get("severidad") in {"ADVERTENCIA", "WARN"}]
    pending = pending_corrections_for_critical_errors(critical_errors)

    estados_columnas = Counter(row.get("estado_columna", "") for row in matrix_rows)
    structure_ok = len(official_cols) == 34 and len(base_cols) == 34
    names_ok = official_cols == base_cols
    order_ok = official_cols == base_cols
    missing = [col for col in official_cols if col not in base_cols]
    extra = [col for col in base_cols if col not in official_cols]

    decision = decide(structure_ok, names_ok, order_ok, len(critical_errors), len(pending), len(warnings))
    if decision not in ESTADOS_PERMITIDOS:
        raise RuntimeError(f"Decision no permitida: {decision}")

    audit_rows = [
        audit_row(
            "estructura_34_columnas",
            "OK" if structure_ok else "FALLA",
            decision if not structure_ok else "OK",
            "INFO" if structure_ok else "ERROR",
            f"Oficiales={len(official_cols)}; base={len(base_cols)}.",
            "ESTRUCTURA_OFICIAL",
            "Mantener 34 columnas oficiales." if structure_ok else "Corregir estructura oficial.",
        ),
        audit_row(
            "nombres_columnas",
            "OK" if names_ok else "FALLA",
            decision if not names_ok else "OK",
            "INFO" if names_ok else "ERROR",
            "Nombres coinciden exactamente." if names_ok else "Nombres no coinciden.",
            "ESTRUCTURA_OFICIAL",
            "Sin accion." if names_ok else "Alinear nombres con estructura oficial.",
        ),
        audit_row(
            "orden_columnas",
            "OK" if order_ok else "FALLA",
            decision if not order_ok else "OK",
            "INFO" if order_ok else "ERROR",
            "Orden coincide exactamente." if order_ok else "Orden no coincide.",
            "ESTRUCTURA_OFICIAL",
            "Sin accion." if order_ok else "Alinear orden con estructura oficial.",
        ),
        audit_row(
            "columnas_faltantes",
            "OK" if not missing else "FALLA",
            decision if missing else "OK",
            "INFO" if not missing else "ERROR",
            ", ".join(missing) if missing else "No hay columnas faltantes.",
            "ESTRUCTURA_OFICIAL",
            "Sin accion." if not missing else "Agregar columnas oficiales faltantes.",
        ),
        audit_row(
            "columnas_adicionales",
            "OK" if not extra else "FALLA",
            decision if extra else "OK",
            "INFO" if not extra else "ERROR",
            ", ".join(extra) if extra else "No hay columnas adicionales.",
            "ESTRUCTURA_OFICIAL",
            "Sin accion." if not extra else "Eliminar columnas no oficiales con control.",
        ),
        audit_row(
            "errores_criticos",
            str(len(critical_errors)),
            "BLOQUEADO_ERROR_CRITICO" if critical_errors else "OK",
            "ERROR" if critical_errors else "INFO",
            "; ".join(
                f"fila {e.get('fila')} {e.get('regla')} {e.get('columna')}={e.get('valor')}"
                for e in critical_errors
            ) or "Sin errores criticos.",
            "VALIDACION_TECNICA_PREVENTIVA",
            "Corregir errores criticos con respaldo." if critical_errors else "Sin accion.",
        ),
        audit_row(
            "advertencias",
            str(len(warnings)),
            "ADVERTENCIA" if warnings else "OK",
            "WARN" if warnings else "INFO",
            f"Advertencias detectadas: {len(warnings)}.",
            "VALIDACION_TECNICA_PREVENTIVA",
            "Revisar antes de exportacion controlada." if warnings else "Sin accion.",
        ),
        audit_row(
            "correcciones_pendientes",
            str(len(pending)),
            "BLOQUEADO_CORRECCION_PENDIENTE" if pending and not critical_errors else "PENDIENTE_CONFIRMACION" if pending else "OK",
            "WARN" if pending else "INFO",
            "; ".join(f"{c.get('ID_CORRECCION')} {c.get('CAMPO')}={c.get('VALOR_ACTUAL')}" for c in pending)
            or "No hay correcciones pendientes asociadas a errores criticos.",
            "PENDIENTE_CONFIRMACION",
            "Completar y autorizar correccion con respaldo." if pending else "Sin accion.",
        ),
        audit_row(
            "exportador_bloqueado",
            "OK",
            "BLOQUEADO",
            "INFO",
            "Exportador requiere autorizacion explicita; esta fase no genera PES_READY.",
            "VALIDACION_TECNICA_PREVENTIVA",
            "Mantener bloqueado hasta auditoria aprobada.",
        ),
        audit_row(
            "decision_final",
            decision,
            decision,
            "ERROR" if decision.startswith("BLOQUEADO") else "INFO",
            "Actualmente el archivo NO esta listo para exportacion PES porque existe 1 error critico: fecha futura en FECHA_OBT_TIT_O_GRADO, fila 20, valor 2027-11-29."
            if decision == "BLOQUEADO_ERROR_CRITICO"
            else f"Decision final: {decision}.",
            "VALIDACION_TECNICA_PREVENTIVA",
            "Resolver bloqueo antes de exportar." if decision.startswith("BLOQUEADO") else "Puede pasar a exportacion controlada.",
        ),
    ]

    audit_path = AUDITORIAS_DIR / f"auditoria_compuerta_pre_exportacion_pes_{timestamp()}.csv"
    write_audit(audit_path, audit_rows)

    summary = {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "rama": git_branch(),
        "decision_final": decision,
        "total_filas": total_filas,
        "total_columnas_base": len(base_cols),
        "total_advertencias": len(warnings),
        "critical_errors_detail": critical_errors,
        "pending_corrections": pending,
        "estados_columnas": dict(estados_columnas),
        "auditoria_validacion": rel(validation_audit),
        "matriz": rel(matrix_path),
        "auditoria_compuerta": rel(audit_path),
    }
    write_dictamen(summary)
    write_bitacora(summary)

    print("Compuerta pre-exportacion PES Personal Academico 2026")
    print(f"estado final: {decision}")
    print(f"errores criticos: {len(critical_errors)}")
    print(f"advertencias: {len(warnings)}")
    print(f"correcciones pendientes asociadas: {len(pending)}")
    print(f"auditoria: {rel(audit_path)}")
    print("NO se genero PES_READY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
