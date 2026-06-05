#!/usr/bin/env python3
"""Aplica correcciones manuales respaldadas a la base general preliminar.

Solo modifica la base si existen correcciones AUTORIZADAS con respaldo completo.
No genera archivo final PES_READY.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime
from pathlib import Path
import shutil
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR.parent
REPO_DIR = MODULE_DIR.parent

BASE_GENERAL = MODULE_DIR / "data/base_general/base_general_personal_academico_en_institucion.tsv"
BACKUPS_DIR = MODULE_DIR / "data/base_general/backups"
CONTROL = MODULE_DIR / "control_correcciones/correcciones_manual_base_general_en_institucion.tsv"
AUDITORIAS_DIR = MODULE_DIR / "auditorias/base_preliminar"
REPORTE = MODULE_DIR / "docs/REPORTE_FASE_3C_CORRECCIONES_CONTROLADAS.md"
BITACORA = MODULE_DIR / "bitacoras/base_preliminar/BITACORA_FASE_3C_CORRECCIONES_CONTROLADAS.md"
FECHA_REFERENCIA = date(2026, 6, 11)

COLUMNAS_OFICIALES = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "NIVEL_FORMACION_ACADEMICO",
    "NOMBRE_TITULO_O_GRADO",
    "NOMBRE_INSTITUCION_OBT_TITULO",
    "PAIS_OBTENCION_TIT_O_GRADO",
    "FECHA_OBT_TIT_O_GRADO",
    "NIVEL_FORMACION_ESPECIALIDAD",
    "TIPO_ESPECIALIDAD",
    "NOMBRE_ESPECIALIDAD",
    "NOMBRE_INST_OBT_ESPECIALIDAD",
    "PAIS_OBTENCION_ESPECIALIDAD",
    "FECHA_OBTENCION_ESPECIALIDAD",
    "PRINCIPAL_CARGO_ACADEMICO",
    "CARGO_NORMALIZADO",
    "NIVEL_SUPERIOR_ADSCRIPCION",
    "NIVEL_SECUNDARIO_ADSCRIPCION",
    "COMUNA_MAYOR_FUNCION",
    "NOMBRE_PRINCIPAL_PROGRAMA",
    "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
    "COMUNA_PRINCIPAL_PROGRAMA",
    "NUM_HORAS_PLANTA",
    "NUM_HORAS_CONTRATA",
    "NUM_HORAS_HONORARIOS",
    "JERARQUIA_ACADEMICA",
    "JERARQUIA_ACADEMICA_OCDE",
    "VIGENCIA",
]
CONTROL_COLUMNS = [
    "ID_CORRECCION",
    "ESTADO",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "CAMPO",
    "VALOR_ACTUAL",
    "VALOR_CORREGIDO",
    "MOTIVO",
    "RESPALDO",
    "FECHA_AUTORIZACION",
    "RESPONSABLE",
    "OBSERVACION",
]

FUENTE_CORRECCION = "CORRECCION_MANUAL_RESPALDADA"
FUENTE_PENDIENTE = "PENDIENTE_CONFIRMACION"
FUENTE_PREVENTIVA = "VALIDACION_TECNICA_PREVENTIVA"


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


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class Auditor:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.events: list[dict[str, object]] = []

    def add(
        self,
        *,
        id_correccion: str = "",
        estado_correccion: str = "",
        tipo_evento: str,
        severidad: str,
        fila_base: object = "",
        tipo_documento: str = "",
        num_documento: str = "",
        dv: str = "",
        campo: str = "",
        valor_anterior: str = "",
        valor_nuevo: str = "",
        accion: str = "",
        motivo: str = "",
        respaldo: str = "",
        fecha_autorizacion: str = "",
        responsable: str = "",
        mensaje: str = "",
        fuente_regla: str = FUENTE_PREVENTIVA,
    ) -> None:
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "id_correccion": id_correccion,
                "estado_correccion": estado_correccion,
                "tipo_evento": tipo_evento,
                "severidad": severidad,
                "fila_base": fila_base,
                "tipo_documento": tipo_documento,
                "num_documento": num_documento,
                "dv": dv,
                "campo": campo,
                "valor_anterior": valor_anterior,
                "valor_nuevo": valor_nuevo,
                "accion": accion,
                "motivo": motivo,
                "respaldo": respaldo,
                "fecha_autorizacion": fecha_autorizacion,
                "responsable": responsable,
                "mensaje": mensaje,
                "fuente_regla": fuente_regla,
            }
        )

    def write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "timestamp",
            "id_correccion",
            "estado_correccion",
            "tipo_evento",
            "severidad",
            "fila_base",
            "tipo_documento",
            "num_documento",
            "dv",
            "campo",
            "valor_anterior",
            "valor_nuevo",
            "accion",
            "motivo",
            "respaldo",
            "fecha_autorizacion",
            "responsable",
            "mensaje",
            "fuente_regla",
        ]
        with self.path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.events)


def ensure_control_file() -> None:
    CONTROL.parent.mkdir(parents=True, exist_ok=True)
    if CONTROL.exists():
        return
    row = {
        "ID_CORRECCION": "CORR_FECHA_TITULO_FUTURA_001",
        "ESTADO": "PENDIENTE",
        "TIPO_DOCUMENTO": "",
        "NUM_DOCUMENTO": "",
        "DV": "",
        "CAMPO": "FECHA_OBT_TIT_O_GRADO",
        "VALOR_ACTUAL": "2027-11-29",
        "VALOR_CORREGIDO": "",
        "MOTIVO": "Fecha de obtencion de titulo aparece como futura y bloquea validacion.",
        "RESPALDO": "PENDIENTE",
        "FECHA_AUTORIZACION": "",
        "RESPONSABLE": "",
        "OBSERVACION": "Completar con fecha correcta respaldada antes de activar.",
    }
    write_tsv(CONTROL, CONTROL_COLUMNS, [row])


def correction_value(correction: dict[str, str], key: str) -> str:
    return (correction.get(key) or "").strip()


def validate_iso_date(value: str) -> tuple[bool, str, date | None]:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return False, "Valor corregido no tiene formato ISO YYYY-MM-DD valido.", None
    if parsed > FECHA_REFERENCIA:
        return False, "Valor corregido es fecha futura respecto a 2026-06-11.", parsed
    return True, "Fecha corregida valida tecnicamente.", parsed


def find_matches(rows: list[dict[str, str]], correction: dict[str, str]) -> list[tuple[int, dict[str, str]]]:
    campo = correction_value(correction, "CAMPO")
    valor_actual = correction_value(correction, "VALOR_ACTUAL")
    tipo = correction_value(correction, "TIPO_DOCUMENTO")
    numero = correction_value(correction, "NUM_DOCUMENTO")
    dv = correction_value(correction, "DV")
    matches = []
    for idx, row in enumerate(rows, start=2):
        if row.get(campo, "") != valor_actual:
            continue
        if tipo or numero or dv:
            if row.get("TIPO_DOCUMENTO", "") == tipo and row.get("NUM_DOCUMENTO", "") == numero and row.get("DV", "") == dv:
                matches.append((idx, row))
        else:
            matches.append((idx, row))
    return matches


def audit_from_correction(
    auditor: Auditor,
    correction: dict[str, str],
    *,
    tipo_evento: str,
    severidad: str,
    mensaje: str,
    fuente_regla: str,
    fila_base: object = "",
    valor_anterior: str | None = None,
    valor_nuevo: str | None = None,
    accion: str = "",
) -> None:
    auditor.add(
        id_correccion=correction_value(correction, "ID_CORRECCION"),
        estado_correccion=correction_value(correction, "ESTADO"),
        tipo_evento=tipo_evento,
        severidad=severidad,
        fila_base=fila_base,
        tipo_documento=correction_value(correction, "TIPO_DOCUMENTO"),
        num_documento=correction_value(correction, "NUM_DOCUMENTO"),
        dv=correction_value(correction, "DV"),
        campo=correction_value(correction, "CAMPO"),
        valor_anterior=correction_value(correction, "VALOR_ACTUAL") if valor_anterior is None else valor_anterior,
        valor_nuevo=correction_value(correction, "VALOR_CORREGIDO") if valor_nuevo is None else valor_nuevo,
        accion=accion,
        motivo=correction_value(correction, "MOTIVO"),
        respaldo=correction_value(correction, "RESPALDO"),
        fecha_autorizacion=correction_value(correction, "FECHA_AUTORIZACION"),
        responsable=correction_value(correction, "RESPONSABLE"),
        mensaje=mensaje,
        fuente_regla=fuente_regla,
    )


def evaluate_correction(
    correction: dict[str, str],
    rows: list[dict[str, str]],
    auditor: Auditor,
) -> tuple[bool, tuple[int, dict[str, str]] | None]:
    estado = correction_value(correction, "ESTADO").upper()
    campo = correction_value(correction, "CAMPO")
    valor_corregido = correction_value(correction, "VALOR_CORREGIDO")
    respaldo = correction_value(correction, "RESPALDO")
    fecha_autorizacion = correction_value(correction, "FECHA_AUTORIZACION")
    responsable = correction_value(correction, "RESPONSABLE")

    if estado != "AUTORIZADA":
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_PENDIENTE_NO_APLICADA",
            severidad="WARN",
            mensaje="Correccion no autorizada; no se aplica.",
            fuente_regla=FUENTE_PENDIENTE,
            accion="SIN_CAMBIOS",
        )
        return False, None
    if not valor_corregido:
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_VALOR_VACIO",
            severidad="ERROR",
            mensaje="Correccion autorizada sin valor corregido.",
            fuente_regla=FUENTE_PENDIENTE,
            accion="RECHAZAR",
        )
        return False, None
    if not respaldo or respaldo.upper() == "PENDIENTE":
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_SIN_RESPALDO",
            severidad="ERROR",
            mensaje="Correccion autorizada sin respaldo valido.",
            fuente_regla=FUENTE_PENDIENTE,
            accion="RECHAZAR",
        )
        return False, None
    if not fecha_autorizacion:
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_SIN_FECHA_AUTORIZACION",
            severidad="ERROR",
            mensaje="Correccion autorizada sin fecha de autorizacion.",
            fuente_regla=FUENTE_PENDIENTE,
            accion="RECHAZAR",
        )
        return False, None
    if not responsable:
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_SIN_RESPONSABLE",
            severidad="ERROR",
            mensaje="Correccion autorizada sin responsable.",
            fuente_regla=FUENTE_PENDIENTE,
            accion="RECHAZAR",
        )
        return False, None
    if campo not in COLUMNAS_OFICIALES:
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_CAMPO_INEXISTENTE",
            severidad="ERROR",
            mensaje="Campo no existe en estructura oficial de 34 columnas.",
            fuente_regla=FUENTE_PREVENTIVA,
            accion="RECHAZAR",
        )
        return False, None
    if campo in {"FECHA_NACIMIENTO", "FECHA_OBT_TIT_O_GRADO", "FECHA_OBTENCION_ESPECIALIDAD"}:
        ok, message, _parsed = validate_iso_date(valor_corregido)
        if not ok and "futura" in message:
            event = "CORRECCION_RECHAZADA_FECHA_FUTURA"
        elif not ok:
            event = "CORRECCION_RECHAZADA_FORMATO"
        else:
            event = ""
        if event:
            audit_from_correction(
                auditor,
                correction,
                tipo_evento=event,
                severidad="ERROR",
                mensaje=message,
                fuente_regla=FUENTE_PREVENTIVA,
                accion="RECHAZAR",
            )
            return False, None
    matches = find_matches(rows, correction)
    if not matches:
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_SIN_COINCIDENCIA",
            severidad="ERROR",
            mensaje="No se encontro registro coincidente para CAMPO + VALOR_ACTUAL y clave informada.",
            fuente_regla=FUENTE_PREVENTIVA,
            accion="RECHAZAR",
        )
        return False, None
    if len(matches) > 1:
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_RECHAZADA_AMBIGUA",
            severidad="ERROR",
            mensaje=f"Se encontraron {len(matches)} coincidencias; no se aplica por ambiguedad.",
            fuente_regla=FUENTE_PREVENTIVA,
            accion="RECHAZAR",
        )
        return False, None
    return True, matches[0]


def write_report(summary: dict[str, object]) -> None:
    applied_details = summary.get("applied_details", [])
    if applied_details:
        detail = "\n".join(
            (
                f"- Fila {d['fila_base']}: {d['campo']} `{d['valor_anterior']}` -> "
                f"`{d['valor_nuevo']}`; respaldo: {d['respaldo']}; responsable: {d['responsable']}"
            )
            for d in applied_details
        )
        status_text = "Se aplicaron correcciones autorizadas y respaldadas."
    else:
        detail = "- No se aplico ninguna correccion."
        status_text = (
            "La base sigue rechazada por falta de correccion autorizada para la fecha futura."
        )
    content = f"""# Reporte Fase 3C - Correcciones Controladas

## Objetivo
Crear un flujo de correcciones manuales respaldadas para errores criticos puntuales de la base general preliminar, sin modificar datos de forma silenciosa.

## Resumen
- Fecha/hora: {summary['fecha_hora']}
- Base revisada: {rel(BASE_GENERAL)}
- Archivo de control usado: {rel(CONTROL)}
- Total correcciones leidas: {summary['total_correcciones_leidas']}
- Total correcciones pendientes: {summary['total_correcciones_pendientes']}
- Total correcciones autorizadas: {summary['total_correcciones_autorizadas']}
- Total correcciones aplicadas: {summary['total_correcciones_aplicadas']}
- Total correcciones rechazadas: {summary['total_correcciones_rechazadas']}
- Auditoria: {summary['auditoria']}

## Error Critico Actual
- Campo: FECHA_OBT_TIT_O_GRADO
- Fila reportada por validador: 20
- Valor actual: 2027-11-29
- Valor fuente observado previamente: 29-11-2027

## Resultado
{status_text}

## Correcciones Aplicadas
{detail}

## Validacion Posterior
- Base general TSV: {summary.get('validacion_base_general', 'pendiente')}
- Fixtures: {summary.get('validacion_fixtures', 'pendiente')}
- Exportador: {summary.get('estado_exportador', 'pendiente')}

No se genero archivo final PES_READY.

Toda correccion queda trazada.

La base sigue preliminar hasta validacion completa.
"""
    REPORTE.write_text(content, encoding="utf-8")


def write_bitacora(summary: dict[str, object]) -> None:
    content = f"""# Bitacora Fase 3C - Correcciones Controladas

- Fecha/hora: {summary['fecha_hora']}
- Rama: {summary['rama']}

## Archivos Creados
- {rel(CONTROL)}
- {summary['auditoria']}
- {rel(REPORTE)}
- {rel(BITACORA)}

## Archivos Modificados
- {rel(BASE_GENERAL) if summary['total_correcciones_aplicadas'] else 'Ninguno en base general; sin correcciones autorizadas validas.'}

## Comandos Ejecutados
- `git branch --show-current`
- `git status --short`
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/aplicar_correcciones_base_general_personal_academico_2026.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Resultado Antes
- Base general preliminar rechazada por 1 `fecha_futura`.

## Resultado Despues
- Correcciones leidas: {summary['total_correcciones_leidas']}
- Correcciones aplicadas: {summary['total_correcciones_aplicadas']}
- Correcciones pendientes: {summary['total_correcciones_pendientes']}
- Correcciones rechazadas: {summary['total_correcciones_rechazadas']}

## Validacion Posterior
- Base general TSV: {summary.get('validacion_base_general', 'pendiente')}
- Fixtures: {summary.get('validacion_fixtures', 'pendiente')}

## Estado de Exportador
- {summary.get('estado_exportador', 'pendiente')}

## Pendientes
- Completar archivo de control con fecha corregida respaldada, autorizacion, responsable y respaldo.
- Reejecutar correcciones y validaciones.
- No generar PES_READY hasta auditoria aprobada.
"""
    BITACORA.write_text(content, encoding="utf-8")


def main() -> int:
    if git_branch() != "feature/personal-academico-base-preliminar-2026":
        print("ERROR: rama actual no es feature/personal-academico-base-preliminar-2026", file=sys.stderr)
        return 2
    if not BASE_GENERAL.exists():
        print(f"ERROR: no existe base general: {BASE_GENERAL}", file=sys.stderr)
        return 2

    ensure_control_file()
    AUDITORIAS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    auditoria_path = AUDITORIAS_DIR / f"auditoria_correcciones_base_general_{timestamp()}.csv"
    auditor = Auditor(auditoria_path)

    columnas, rows = read_tsv(BASE_GENERAL)
    if columnas != COLUMNAS_OFICIALES:
        auditor.add(
            tipo_evento="SIN_CAMBIOS",
            severidad="ERROR",
            mensaje="La base general no conserva exactamente las 34 columnas oficiales en orden.",
            fuente_regla=FUENTE_PREVENTIVA,
            accion="DETENER",
        )
        auditor.write()
        print("ERROR: estructura de base general no coincide con 34 columnas oficiales.", file=sys.stderr)
        return 1

    control_columns, corrections = read_tsv(CONTROL)
    missing_control = [col for col in CONTROL_COLUMNS if col not in control_columns]
    if missing_control:
        auditor.add(
            tipo_evento="SIN_CAMBIOS",
            severidad="ERROR",
            mensaje=f"Archivo de control incompleto; faltan columnas: {', '.join(missing_control)}",
            fuente_regla=FUENTE_PREVENTIVA,
            accion="DETENER",
        )
        auditor.write()
        return 1

    counts: Counter[str] = Counter()
    applied_details: list[dict[str, str]] = []
    pending_or_rejected = 0

    for correction in corrections:
        estado = correction_value(correction, "ESTADO").upper()
        counts["leidas"] += 1
        if estado == "AUTORIZADA":
            counts["autorizadas"] += 1
        else:
            counts["pendientes"] += 1

        ok, match = evaluate_correction(correction, rows, auditor)
        if not ok:
            if estado == "AUTORIZADA":
                pending_or_rejected += 1
            continue
        assert match is not None
        fila_base, row = match
        campo = correction_value(correction, "CAMPO")
        valor_anterior = row[campo]
        valor_nuevo = correction_value(correction, "VALOR_CORREGIDO")
        row[campo] = valor_nuevo
        counts["aplicadas"] += 1
        applied_details.append(
            {
                "fila_base": str(fila_base),
                "campo": campo,
                "valor_anterior": valor_anterior,
                "valor_nuevo": valor_nuevo,
                "respaldo": correction_value(correction, "RESPALDO"),
                "responsable": correction_value(correction, "RESPONSABLE"),
            }
        )
        audit_from_correction(
            auditor,
            correction,
            tipo_evento="CORRECCION_AUTORIZADA_APLICADA",
            severidad="INFO",
            fila_base=fila_base,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            mensaje="Correccion manual respaldada aplicada.",
            fuente_regla=FUENTE_CORRECCION,
            accion="APLICAR_CORRECCION",
        )

    backup_path = ""
    if counts["aplicadas"] > 0:
        backup = BACKUPS_DIR / f"base_general_personal_academico_en_institucion_PRE_CORRECCION_{timestamp()}.tsv"
        shutil.copy2(BASE_GENERAL, backup)
        backup_path = rel(backup)
        auditor.add(
            tipo_evento="BACKUP_PRE_CORRECCION",
            severidad="INFO",
            mensaje="Backup creado antes de guardar correcciones.",
            fuente_regla=FUENTE_PREVENTIVA,
            accion="CREAR_BACKUP",
            valor_nuevo=backup_path,
        )
        write_tsv(BASE_GENERAL, COLUMNAS_OFICIALES, rows)
        auditor.add(
            tipo_evento="BASE_GENERAL_CORREGIDA",
            severidad="INFO",
            mensaje=f"Base general guardada con {counts['aplicadas']} correcciones.",
            fuente_regla=FUENTE_CORRECCION,
            accion="GUARDAR_BASE_GENERAL",
        )
    else:
        auditor.add(
            tipo_evento="SIN_CAMBIOS",
            severidad="INFO",
            mensaje="No hay correcciones autorizadas validas; base general queda sin cambios.",
            fuente_regla=FUENTE_PENDIENTE,
            accion="SIN_CAMBIOS",
        )

    rejected_events = {
        "CORRECCION_RECHAZADA_SIN_RESPALDO",
        "CORRECCION_RECHAZADA_SIN_RESPONSABLE",
        "CORRECCION_RECHAZADA_SIN_FECHA_AUTORIZACION",
        "CORRECCION_RECHAZADA_VALOR_VACIO",
        "CORRECCION_RECHAZADA_CAMPO_INEXISTENTE",
        "CORRECCION_RECHAZADA_SIN_COINCIDENCIA",
        "CORRECCION_RECHAZADA_AMBIGUA",
        "CORRECCION_RECHAZADA_FORMATO",
        "CORRECCION_RECHAZADA_FECHA_FUTURA",
    }
    rejected_count = sum(1 for e in auditor.events if e["tipo_evento"] in rejected_events)
    summary = {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "rama": git_branch(),
        "auditoria": rel(auditoria_path),
        "backup": backup_path,
        "total_correcciones_leidas": counts["leidas"],
        "total_correcciones_pendientes": counts["pendientes"],
        "total_correcciones_autorizadas": counts["autorizadas"],
        "total_correcciones_aplicadas": counts["aplicadas"],
        "total_correcciones_rechazadas": rejected_count,
        "applied_details": applied_details,
    }
    auditor.write()
    write_report(summary)
    write_bitacora(summary)

    print("Correcciones controladas Personal Academico 2026")
    print(f"correcciones leidas: {summary['total_correcciones_leidas']}")
    print(f"correcciones aplicadas: {summary['total_correcciones_aplicadas']}")
    print(f"correcciones pendientes: {summary['total_correcciones_pendientes']}")
    print(f"correcciones rechazadas: {summary['total_correcciones_rechazadas']}")
    print(f"auditoria: {summary['auditoria']}")
    print("NO se genero archivo final PES_READY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
