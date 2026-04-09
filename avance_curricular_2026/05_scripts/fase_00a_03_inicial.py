#!/usr/bin/env python3
"""Fases 00A-03 for Avance Curricular SIES 2026.

The script freezes observed sources, creates technical derivatives and
non-personal control artifacts for the initial Avance Curricular workflow.
It intentionally avoids printing or writing row samples with student data in
documentation or versionable control files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from openpyxl import load_workbook


TZ = ZoneInfo("America/Santiago")
REPO = Path(__file__).resolve().parents[2]
PROCESS_ROOT = REPO / "avance_curricular_2026"
DOWNLOADS = Path("/Users/alexi/Downloads")
NOW = datetime.now(TZ)
STAMP = NOW.strftime("%Y%m%d_%H%M%S")
FREEZE_DIR = PROCESS_ROOT / "00_fuentes_congeladas" / f"CARGA_CONGELADA_{STAMP}"
ORIG_DIR = FREEZE_DIR / "originales"
DER_DIR = FREEZE_DIR / "derivados_tsv"
PROF_DIR = FREEZE_DIR / "perfiles"
MAN_DIR = FREEZE_DIR / "manifiestos"
EVID_DIR = FREEZE_DIR / "evidencia"
LOG_DIR = FREEZE_DIR / "logs"

PROCESS = "Avance Curricular SIES 2026"
YEAR_PROCESS = "2026"
YEAR_DATA = "2025"
ACADEMIC_PERIOD = (
    "Año académico 2025: primer semestre 2025, segundo semestre 2025, "
    "avance anual 2025 y acumulado hasta cierre 2025"
)

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".sh",
    ".yml",
    ".yaml",
    ".toml",
    ".cfg",
    ".ini",
    ".tsv",
    ".csv",
}


CSV_DERIVATIVES = {
    "FUENTE_5810_CARRERAS": "5810_PRECARGA_CARRERAS_AVANCE_CURRICULAR_2026_CONGELADA.tsv",
    "FUENTE_5809_MATRICULA": "5809_PRECARGA_MATRICULA_AVANCE_CURRICULAR_2026_CONGELADA.tsv",
}


EXPECTED_SOURCES: list[dict[str, Any]] = [
    {
        "id": "FUENTE_5810_CARRERAS",
        "name": "5810_Precarga Carreras Avance Curricular 20268.csv",
        "subprocess": "Carreras Avance Curricular 2026",
        "classification": "precarga oficial; estructura de referencia descargada desde PES",
        "backup_level": "ORIGINAL_OFICIAL_DESCARGAS",
        "format": "CSV",
        "extension": ".csv",
        "personal": "NO",
        "sensitive": "NO",
    },
    {
        "id": "FUENTE_5809_MATRICULA",
        "name": "5809_Precarga Matrícula Avance Curricular 2026.csv",
        "subprocess": "Matrícula Avance Curricular 2026",
        "classification": "precarga oficial; matrícula y avance referidos al año 2025",
        "backup_level": "ORIGINAL_OFICIAL_DESCARGAS",
        "format": "CSV",
        "extension": ".csv",
        "personal": "SI",
        "sensitive": "POSIBLE",
    },
    {
        "id": "FUENTE_INSTRUCTIVO_TXT",
        "name": "Instructivo_Avance Curricular SIES - 2026.txt",
        "subprocess": "Proceso Avance Curricular SIES 2026",
        "classification": "instructivo oficial; fuente normativa textual",
        "backup_level": "ORIGINAL_OFICIAL_DESCARGAS",
        "format": "TXT",
        "extension": ".txt",
        "personal": "NO",
        "sensitive": "NO",
    },
    {
        "id": "FUENTE_PROMEDIOS_7804",
        "name": "PROMEDIOSDEALUMNOS_7804.xlsx",
        "subprocess": "Fuente institucional candidata",
        "classification": "fuente institucional candidata; datos personales y académicos",
        "backup_level": "ORIGINAL_INSTITUCIONAL_CANDIDATO",
        "format": "XLSX",
        "extension": ".xlsx",
        "personal": "SI",
        "sensitive": "POSIBLE",
    },
]


CARRERAS_FIELDS = [
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "NOMBRE_SEDE",
    "NOMBRE_CARRERA",
    "JORNADA",
    "VERSION",
    "DURACION_ESTUDIOS",
    "DURACION_TITULACION",
    "DURACION_TOTAL",
    "NIVEL_CARRERA",
    "TIPO_UNIDAD_MEDIDA",
    "OTRA_UNIDAD_MEDIDA",
    "TOTAL_UNIDADES_MEDIDA",
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
    "VIGENCIA",
]

MATRICULA_FIELDS = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

CARRERAS_MODIFIABLE = {
    "PLAN_ESTUDIOS",
    "TIPO_UNIDAD_MEDIDA",
    "OTRA_UNIDAD_MEDIDA",
    "TOTAL_UNIDADES_MEDIDA",
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
    "VIGENCIA",
}

MATRICULA_MODIFIABLE = {
    "PLAN_ESTUDIOS",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
}

PERSONAL_FIELD_NAMES = {
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "RUT",
    "DIG",
    "NOMBRE",
    "PATERNO",
    "MATERNO",
    "CODCLI",
}


FIELD_DEFINITIONS: dict[str, dict[str, str]] = {
    "CODIGO_UNICO": {
        "desc": "Código de la carrera o programa.",
        "def": "Identificador único de la carrera o programa informado por SIES.",
        "type": "TEXTO",
        "domain": "Código único SIES.",
    },
    "PLAN_ESTUDIOS": {
        "desc": "Plan de Estudios de la Carrera.",
        "def": "Correlativo del plan de estudios vigente; precargado con 1 y modificable cuando exista evidencia de planes vigentes distintos.",
        "type": "ENTERO",
        "domain": "Números correlativos por CODIGO_UNICO.",
    },
    "NOMBRE_SEDE": {
        "desc": "Nombre de la Sede.",
        "def": "Sede en que se imparte la carrera o programa informado.",
        "type": "TEXTO",
        "domain": "Dato precargado.",
    },
    "NOMBRE_CARRERA": {
        "desc": "Nombre de la Carrera o Programa.",
        "def": "Nombre completo de la carrera o programa informado.",
        "type": "TEXTO",
        "domain": "Dato precargado.",
    },
    "JORNADA": {
        "desc": "Jornada de la Carrera.",
        "def": "Jornada en que se imparte la carrera o programa.",
        "type": "ENTERO",
        "domain": "1 Diurna; 2 Vespertina; 3 Semipresencial; 4 A Distancia; 5 Otra.",
    },
    "VERSION": {
        "desc": "Versión de la carrera.",
        "def": "Número de versión del programa de estudios.",
        "type": "ENTERO",
        "domain": "Dato precargado.",
    },
    "DURACION_ESTUDIOS": {
        "desc": "Duración de los estudios de la carrera.",
        "def": "Duración del plan en semestres, sin incluir titulación cuando esté fuera del plan.",
        "type": "ENTERO",
        "domain": "Semestres.",
    },
    "DURACION_TITULACION": {
        "desc": "Duración del proceso de titulación.",
        "def": "Duración normal estimada del proceso de titulación, no plazo máximo.",
        "type": "ENTERO",
        "domain": "Semestres.",
    },
    "DURACION_TOTAL": {
        "desc": "Duración total de la carrera.",
        "def": "Duración teórica total hasta título o grado terminal.",
        "type": "ENTERO",
        "domain": "Semestres.",
    },
    "NIVEL_CARRERA": {
        "desc": "Clasificación por Nivel Carrera.",
        "def": "Nivel específico al que pertenecen los estudios.",
        "type": "ENTERO",
        "domain": "0 Bachillerato/Ciclo inicial/Plan común; 1 TNS; 2 Profesional sin licenciatura; 3 Licenciatura no conducente; 4 Profesional con licenciatura.",
    },
    "TIPO_UNIDAD_MEDIDA": {
        "desc": "Tipo de Unidad de Medida.",
        "def": "Unidad usada por la institución para cuantificar el avance curricular.",
        "type": "ENTERO",
        "domain": "1 Asignaturas/cursos/módulos; 2 Créditos académicos o SCT-Chile; 3 Otra unidad.",
    },
    "OTRA_UNIDAD_MEDIDA": {
        "desc": "Otra Unidad de Medida.",
        "def": "Nombre descriptivo cuando TIPO_UNIDAD_MEDIDA es 3.",
        "type": "TEXTO",
        "domain": "Texto; requerido solo cuando tipo es 3 según Anexo IV.",
    },
    "TOTAL_UNIDADES_MEDIDA": {
        "desc": "Número total de Unidades de Medida.",
        "def": "Total de unidades que componen el plan de estudios.",
        "type": "ENTERO",
        "domain": "Números enteros; obligatorio.",
    },
    "UNIDADES_1ER_ANIO": {
        "desc": "Unidades del 1er año.",
        "def": "Total de unidades que componen el primer año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "UNIDADES_2DO_ANIO": {
        "desc": "Unidades del 2do año.",
        "def": "Total de unidades que componen el segundo año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "UNIDADES_3ER_ANIO": {
        "desc": "Unidades del 3er año.",
        "def": "Total de unidades que componen el tercer año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "UNIDADES_4TO_ANIO": {
        "desc": "Unidades del 4to año.",
        "def": "Total de unidades que componen el cuarto año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "UNIDADES_5TO_ANIO": {
        "desc": "Unidades del 5to año.",
        "def": "Total de unidades que componen el quinto año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "UNIDADES_6TO_ANIO": {
        "desc": "Unidades del 6to año.",
        "def": "Total de unidades que componen el sexto año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "UNIDADES_7MO_ANIO": {
        "desc": "Unidades del 7mo año.",
        "def": "Total de unidades que componen el séptimo año del plan.",
        "type": "ENTERO",
        "domain": "Números enteros.",
    },
    "VIGENCIA": {
        "desc": "Vigencia.",
        "def": "Variable para mantener o eliminar un registro cargado en este proceso.",
        "type": "ENTERO",
        "domain": "0 Eliminar registro; 1 Mantener registro.",
    },
    "TIPO_DOCUMENTO": {
        "desc": "Tipo de documento.",
        "def": "Tipo de documento de identificación de cada estudiante.",
        "type": "TEXTO",
        "domain": "R RUN; P Pasaporte.",
    },
    "NUM_DOCUMENTO": {
        "desc": "Número de documento.",
        "def": "Cuerpo del RUN o número de pasaporte.",
        "type": "TEXTO",
        "domain": "Dato precargado.",
    },
    "DV": {
        "desc": "Dígito Verificador.",
        "def": "Dígito verificador del RUN.",
        "type": "TEXTO",
        "domain": "0-9 o K.",
    },
    "PRIMER_APELLIDO": {
        "desc": "Primer Apellido.",
        "def": "Primer apellido completo de cada estudiante.",
        "type": "TEXTO",
        "domain": "Dato precargado.",
    },
    "SEGUNDO_APELLIDO": {
        "desc": "Segundo Apellido.",
        "def": "Segundo apellido completo de cada estudiante.",
        "type": "TEXTO",
        "domain": "Dato precargado.",
    },
    "NOMBRES": {
        "desc": "Nombres.",
        "def": "Nombres completos de cada estudiante.",
        "type": "TEXTO",
        "domain": "Dato precargado.",
    },
    "SEXO": {
        "desc": "Sexo.",
        "def": "Condición de mujer, hombre o no binario reportada en matrícula.",
        "type": "TEXTO",
        "domain": "M Mujer; H Hombre; X No Binario.",
    },
    "FECHA_NACIMIENTO": {
        "desc": "Fecha de nacimiento.",
        "def": "Fecha de nacimiento del/de la estudiante.",
        "type": "FECHA_TEXTO",
        "domain": "Dato precargado.",
    },
    "ANIO_INGRESO_CARRERA_ACTUAL": {
        "desc": "Año de ingreso a la carrera actual.",
        "def": "Año en que cada estudiante ingresó a la carrera actual.",
        "type": "ENTERO",
        "domain": "Año calendario; no mayor a 2025 según Anexo V.",
    },
    "SEM_INGRESO_CARRERA_ACTUAL": {
        "desc": "Semestre de ingreso a la carrera actual.",
        "def": "Semestre de ingreso a la carrera actual.",
        "type": "ENTERO",
        "domain": "1 Primer Semestre; 2 Segundo Semestre.",
    },
    "ANIO_INGRESO_CARRERA_ORIGEN": {
        "desc": "Año de ingreso a la carrera de origen.",
        "def": "Año de ingreso al primer año del plan de estudios de la carrera de origen.",
        "type": "ENTERO",
        "domain": "Año calendario; no mayor a 2025 según Anexo V.",
    },
    "SEM_INGRESO_CARRERA_ORIGEN": {
        "desc": "Semestre de ingreso a la carrera de origen.",
        "def": "Semestre de ingreso a la carrera de origen o primer año.",
        "type": "ENTERO",
        "domain": "1 Primer Semestre; 2 Segundo Semestre.",
    },
    "CURSO_1ER_SEM": {
        "desc": "Presencia en primer semestre.",
        "def": "Indica si cursó actividades académicas durante el primer semestre 2025.",
        "type": "TEXTO",
        "domain": "SI; NO.",
    },
    "CURSO_2DO_SEM": {
        "desc": "Presencia en segundo semestre.",
        "def": "Indica si cursó actividades académicas durante el segundo semestre 2025.",
        "type": "TEXTO",
        "domain": "SI; NO.",
    },
    "UNIDADES_CURSADAS": {
        "desc": "Unidades cursadas durante 2025.",
        "def": "Unidades cursadas efectivamente durante 2025 pertenecientes al plan informado.",
        "type": "NUMERO",
        "domain": "Números; no incluye validación o reconocimiento en avance anual.",
    },
    "UNIDADES_APROBADAS": {
        "desc": "Unidades aprobadas durante 2025.",
        "def": "Unidades aprobadas efectivamente durante 2025 pertenecientes al plan informado.",
        "type": "NUMERO",
        "domain": "Números; no incluye validación o reconocimiento en avance anual.",
    },
    "UNID_CURSADAS_TOTAL": {
        "desc": "Unidades cursadas acumuladas.",
        "def": "Unidades cursadas desde ingreso hasta cierre de 2025.",
        "type": "NUMERO",
        "domain": "Números; puede incluir validación o reconocimiento según instructivo.",
    },
    "UNID_APROBADAS_TOTAL": {
        "desc": "Unidades aprobadas acumuladas.",
        "def": "Unidades aprobadas desde ingreso hasta cierre de 2025.",
        "type": "NUMERO",
        "domain": "Números; límite de referencia es total del plan con tolerancia de 25%.",
    },
}


def run(cmd: list[str], cwd: Path = REPO) -> str:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return proc.stdout.strip()
    except FileNotFoundError as exc:
        return f"ERROR_COMANDO_NO_DISPONIBLE: {exc}"


def ensure_dirs() -> None:
    for path in [
        PROCESS_ROOT / "00_fuentes_congeladas",
        PROCESS_ROOT / "01_documentacion",
        PROCESS_ROOT / "02_contratos",
        PROCESS_ROOT / "03_gobernanza_columnas",
        PROCESS_ROOT / "04_configuracion",
        PROCESS_ROOT / "05_scripts",
        PROCESS_ROOT / "06_tests",
        PROCESS_ROOT / "07_control",
        PROCESS_ROOT / "08_auditorias",
        PROCESS_ROOT / "09_pendientes",
        PROCESS_ROOT / "10_resultados",
        PROCESS_ROOT / "11_archivos_subida",
        ORIG_DIR,
        DER_DIR,
        PROF_DIR,
        MAN_DIR,
        EVID_DIR,
        LOG_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def safe_sheet_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    asciiish = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    asciiish = re.sub(r"[^A-Za-z0-9]+", "_", asciiish).strip("_").upper()
    return asciiish or "SIN_NOMBRE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iso_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, TZ).isoformat()


def stat_info(path: Path) -> dict[str, Any]:
    st = path.stat()
    return {
        "size": st.st_size,
        "mtime": iso_from_timestamp(st.st_mtime),
    }


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: stringify(row.get(field, "NO_DETERMINADO")) for field in fields})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "SI" if value else "NO"
    if isinstance(value, (list, tuple, set)):
        return " | ".join(stringify(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def detect_encoding(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig", "BOM_UTF8"
    for enc in ["utf-8", "cp1252", "latin-1"]:
        try:
            data.decode(enc)
            return enc, "SIN_BOM"
        except UnicodeDecodeError:
            continue
    return "latin-1", "FALLBACK_LATIN1"


def detect_delimiter(text: str) -> str:
    sample = text[:65536]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        first = next((line for line in sample.splitlines() if line.strip()), "")
        counts = {delim: first.count(delim) for delim in [",", ";", "\t", "|"]}
        return max(counts, key=counts.get) if any(counts.values()) else ","


def read_csv_rows(path: Path, encoding: str, delimiter: str) -> list[list[str]]:
    with path.open("r", encoding=encoding, newline="") as fh:
        return [list(row) for row in csv.reader(fh, delimiter=delimiter)]


def write_rows_tsv(path: Path, rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        for row in rows:
            writer.writerow(["" if cell is None else str(cell) for cell in row])


def delimiter_label(delim: str) -> str:
    if delim == "\t":
        return "TAB"
    if delim == ";":
        return "PUNTO_Y_COMA"
    if delim == ",":
        return "COMA"
    return delim


def locate_sources() -> tuple[dict[str, list[Path]], list[dict[str, str]]]:
    files = [p for p in DOWNLOADS.iterdir() if p.is_file()]
    normalized = [(nfc(p.name), p) for p in files]
    found: dict[str, list[Path]] = {}
    for item in EXPECTED_SOURCES:
        target = nfc(item["name"])
        found[item["id"]] = [p for name, p in normalized if name == target]

    excluded: list[dict[str, str]] = []
    target_names = {nfc(item["name"]) for item in EXPECTED_SOURCES}
    excluded_exact = "Reporte Precarga del Proceso Extranjeros Regulares 2026.csv"
    for name, path in normalized:
        if name == nfc(excluded_exact):
            excluded.append(
                {
                    "NOMBRE_ARCHIVO": path.name,
                    "RUTA": str(path),
                    "CLASIFICACION": "precarga de otro proceso",
                    "PROCESO_ASOCIADO": "Estudiantes Extranjeros",
                    "MOTIVO_EXCLUSION": "Pertenece al proceso Estudiantes Extranjeros, no a Avance Curricular.",
                    "FECHA_REVISION": NOW.isoformat(),
                    "OBSERVACION": "Registrado por instrucción; no copiado ni procesado.",
                }
            )
        elif (
            ("Precarga" in name or "Avance Curricular" in name or "Instructivo_Avance" in name)
            and name not in target_names
        ):
            excluded.append(
                {
                    "NOMBRE_ARCHIVO": path.name,
                    "RUTA": str(path),
                    "CLASIFICACION": "archivo cercano no seleccionado",
                    "PROCESO_ASOCIADO": "NO_DETERMINADO",
                    "MOTIVO_EXCLUSION": "No coincide exactamente con los cinco nombres requeridos para esta carga congelada.",
                    "FECHA_REVISION": NOW.isoformat(),
                    "OBSERVACION": "No se inspeccionó contenido; exclusión por nombre normalizado.",
                }
            )
    return found, excluded


def repo_visibility() -> dict[str, str]:
    url = "https://api.github.com/repos/Alexitho0o/avance_curricular"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return {
            "estado": "VERIFICADO_API_GITHUB",
            "visibility": payload.get("visibility", "NO_DETERMINADO"),
            "private": "SI" if payload.get("private") else "NO",
            "html_url": payload.get("html_url", "NO_DETERMINADO"),
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "estado": "NO_VERIFICABLE",
            "visibility": "NO_VERIFICABLE",
            "private": "NO_VERIFICABLE",
            "html_url": "https://github.com/Alexitho0o/avance_curricular",
            "error": str(exc),
        }


def get_git_context() -> dict[str, Any]:
    branches_local = run(["git", "branch", "--list"]).splitlines()
    branches_remote = run(["git", "branch", "--remotes"]).splitlines()
    candidate_lines = [
        line.strip().lstrip("* ").strip()
        for line in branches_local + branches_remote
        if re.search(r"avance|curricular", line, flags=re.I)
    ]
    return {
        "branch": run(["git", "branch", "--show-current"]),
        "commit": run(["git", "rev-parse", "--short", "HEAD"]),
        "commit_full": run(["git", "rev-parse", "HEAD"]),
        "status_short": run(["git", "status", "--short", "--branch"]),
        "status_porcelain": run(["git", "status", "--porcelain=v1"]),
        "branches_local": branches_local,
        "branches_remote": branches_remote,
        "candidate_branches": sorted(set(candidate_lines)),
        "remote_v": run(["git", "remote", "-v"]),
        "last_commits": run(
            [
                "git",
                "for-each-ref",
                "--format=%(refname:short)\t%(objectname:short)\t%(committerdate:iso8601)\t%(subject)",
                "refs/heads",
                "refs/remotes",
            ]
        ),
        "diff_main_stat": run(["git", "diff", "--stat", "main...HEAD"]),
        "ahead_behind_main": run(["git", "rev-list", "--left-right", "--count", "main...HEAD"]),
        "merge_base_main": run(["git", "merge-base", "main", "HEAD"])[:7],
    }


def profile_csv(path: Path, source_id: str, expected_fields: list[str]) -> dict[str, Any]:
    encoding, bom = detect_encoding(path)
    text = path.read_bytes().decode(encoding)
    delimiter = detect_delimiter(text)
    rows = read_csv_rows(path, encoding, delimiter)
    header = rows[0] if rows else []
    data = rows[1:] if rows else []
    col_count = len(header)
    row_len_counts = Counter(len(r) for r in rows)
    anomalous = [
        {"numero_fila_1_base": idx + 1, "columnas": len(row)}
        for idx, row in enumerate(rows)
        if len(row) != col_count
    ]
    empty_counts: dict[str, int] = {}
    distinct_counts: dict[str, int] = {}
    type_observed: dict[str, list[str]] = {}
    for col_idx, col in enumerate(header):
        values = [row[col_idx] if col_idx < len(row) else "" for row in data]
        empty_counts[col] = sum(1 for value in values if value == "")
        distinct_counts[col] = len(set(values))
        observed = set()
        for value in values:
            if value == "":
                observed.add("VACIO")
            elif re.fullmatch(r"-?\d+", value):
                observed.add("ENTERO_TEXTO")
            elif re.fullmatch(r"-?\d+[.,]\d+", value):
                observed.add("DECIMAL_TEXTO")
            else:
                observed.add("TEXTO")
        type_observed[col] = sorted(observed)

    missing_official = [field for field in expected_fields if field not in header]
    extra_fields = [field for field in header if field not in expected_fields and field != "CODIGO_IES_NUM"]
    first_column = header[0] if header else "NO_DETERMINADO"
    first_column_status = (
        "COLUMNA_INSTITUCIONAL_A_ELIMINAR_SOLO_EN_PES"
        if first_column == "CODIGO_IES_NUM"
        else "PENDIENTE_CONFIRMACION"
    )
    key_candidates: dict[str, Any] = {}
    if source_id == "FUENTE_5810_CARRERAS":
        key_fields = ["CODIGO_UNICO", "PLAN_ESTUDIOS"]
        key_candidates["CODIGO_UNICO_PLAN_ESTUDIOS"] = duplicate_summary(data, header, key_fields)
        key_candidates["CODIGO_UNICO"] = duplicate_summary(data, header, ["CODIGO_UNICO"])
    elif source_id == "FUENTE_5809_MATRICULA":
        key_fields = ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "PLAN_ESTUDIOS"]
        key_candidates["DOCUMENTO_CODIGO_PLAN"] = duplicate_summary(data, header, key_fields)
        key_candidates["DOCUMENTO_CODIGO"] = duplicate_summary(
            data, header, ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO"]
        )

    profile = {
        "archivo": path.name,
        "ruta": str(path),
        "source_id": source_id,
        "sha256": sha256(path),
        "tamano_bytes": path.stat().st_size,
        "fecha_modificacion": iso_from_timestamp(path.stat().st_mtime),
        "codificacion_detectada": encoding,
        "bom": bom,
        "delimitador_detectado": delimiter_label(delimiter),
        "salto_linea": newline_summary(path.read_bytes()),
        "tiene_encabezado": "SI" if bool(header) else "NO",
        "filas_totales_incluye_encabezado": len(rows),
        "filas_datos": len(data),
        "columnas": col_count,
        "encabezados": header,
        "orden_columnas_preservado_referencia": "PERFIL_ORIGINAL",
        "campos_oficiales_faltantes": missing_official,
        "campos_extra_no_oficiales": extra_fields,
        "primera_columna": first_column,
        "primera_columna_estado": first_column_status,
        "filas_con_distinto_numero_campos": anomalous,
        "conteo_columnas_por_fila": dict(row_len_counts),
        "vacios_por_columna": empty_counts,
        "conteo_valores_distintos_por_columna": distinct_counts,
        "tipos_observados_por_columna": type_observed,
        "claves_candidatas": key_candidates,
        "contiene_datos_personales": "SI" if any(col in PERSONAL_FIELD_NAMES for col in header) else "NO",
        "contiene_datos_sensibles": "POSIBLE" if any(col in {"SEXO", "FECHA_NACIMIENTO"} for col in header) else "NO",
        "muestras_reales_incluidas": "NO",
        "observacion_seguridad": "Perfil sin muestras de registros para evitar exposición de datos personales.",
    }
    return profile


def duplicate_summary(data: list[list[str]], header: list[str], fields: list[str]) -> dict[str, Any]:
    missing = [field for field in fields if field not in header]
    if missing:
        return {"estado": "NO_EVALUADO", "campos_faltantes": missing}
    indexes = [header.index(field) for field in fields]
    counter = Counter(tuple(row[i] if i < len(row) else "" for i in indexes) for row in data)
    duplicate_groups = sum(1 for count in counter.values() if count > 1)
    duplicate_rows = sum(count for count in counter.values() if count > 1)
    return {
        "estado": "EVALUADO_SIN_VALORES_REALES",
        "campos": fields,
        "llaves_distintas": len(counter),
        "grupos_duplicados": duplicate_groups,
        "filas_en_grupos_duplicados": duplicate_rows,
    }


def newline_summary(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    parts = []
    if crlf:
        parts.append(f"CRLF={crlf}")
    if lf:
        parts.append(f"LF={lf}")
    if cr:
        parts.append(f"CR={cr}")
    return "; ".join(parts) if parts else "NO_DETERMINADO"


def derive_csv_to_tsv(
    original: Path,
    source_id: str,
    derivative_name: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    encoding = profile["codificacion_detectada"]
    delimiter = {
        "PUNTO_Y_COMA": ";",
        "COMA": ",",
        "TAB": "\t",
    }.get(profile["delimitador_detectado"], profile["delimitador_detectado"])
    original_rows = read_csv_rows(original, encoding, delimiter)
    out_path = DER_DIR / derivative_name
    write_rows_tsv(out_path, original_rows)
    derived_rows = read_csv_rows(out_path, "utf-8", "\t")
    equivalent = original_rows == derived_rows
    validation = {
        "archivo_origen": str(original),
        "archivo_derivado": str(out_path),
        "filas_origen_incluye_encabezado": len(original_rows),
        "filas_derivado_incluye_encabezado": len(derived_rows),
        "columnas_origen": len(original_rows[0]) if original_rows else 0,
        "columnas_derivado": len(derived_rows[0]) if derived_rows else 0,
        "encabezados_preservados": "SI" if original_rows[:1] == derived_rows[:1] else "NO",
        "contenido_textual_por_celda_preservado": "SI" if equivalent else "NO",
        "orden_filas_preservado": "SI" if equivalent else "NO",
        "orden_columnas_preservado": "SI" if equivalent else "NO",
        "columnas_auxiliares_agregadas": "NO",
        "indice_agregado": "NO",
        "ordenamiento_realizado": "NO",
        "deduplicacion_realizada": "NO",
        "estado_validacion": "CONGELADO_VALIDADO" if equivalent else "BLOQUEADO",
        "observaciones": (
            "Equivalencia exacta validada mediante lectura CSV original y TSV derivado."
            if equivalent
            else "La lectura estructurada del TSV no coincide con la lectura estructurada del CSV original."
        ),
        "sha256_origen": sha256(original),
        "sha256_derivado": sha256(out_path),
    }
    name = "CARRERAS" if source_id == "FUENTE_5810_CARRERAS" else "MATRICULA"
    write_json(PROF_DIR / f"VALIDACION_EQUIVALENCIA_PRECARGA_{name}.json", validation)
    return {
        "ID_DERIVADO": f"DERIVADO_{source_id}",
        "ID_FUENTE_ORIGEN": source_id,
        "NOMBRE_ORIGEN": original.name,
        "NOMBRE_DERIVADO": derivative_name,
        "RUTA_DERIVADO": str(out_path),
        "TIPO_DERIVACION": "CSV_A_TSV_UTF8",
        "SCRIPT_GENERADOR": str(Path(__file__).relative_to(REPO)),
        "VERSION_SCRIPT": "1.0",
        "FECHA_GENERACION": NOW.isoformat(),
        "SHA256_ORIGEN": sha256(original),
        "SHA256_DERIVADO": sha256(out_path),
        "FILAS_ORIGEN": max(0, len(original_rows) - 1),
        "FILAS_DERIVADO": max(0, len(derived_rows) - 1),
        "COLUMNAS_ORIGEN": len(original_rows[0]) if original_rows else 0,
        "COLUMNAS_DERIVADO": len(derived_rows[0]) if derived_rows else 0,
        "ORDEN_FILAS_PRESERVADO": "SI" if equivalent else "NO",
        "ORDEN_COLUMNAS_PRESERVADO": "SI" if equivalent else "NO",
        "ENCABEZADOS_PRESERVADOS": "SI" if original_rows[:1] == derived_rows[:1] else "NO",
        "TIPOS_FORZADOS_A_TEXTO": "SI",
        "CAMBIOS_REALIZADOS": "Único cambio esperado: delimitador de salida tabulación y codificación de escritura UTF-8.",
        "PERDIDAS_DE_INFORMACION_DETECTADAS": "NO" if equivalent else "SI",
        "ESTADO_VALIDACION": "CONGELADO_VALIDADO" if equivalent else "BLOQUEADO",
        "OBSERVACIONES": validation["observaciones"],
    }


def cell_to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def profile_and_export_excel(path: Path, source_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    wb = load_workbook(path, read_only=False, data_only=False)
    workbook_profile: dict[str, Any] = {
        "archivo": path.name,
        "ruta": str(path),
        "source_id": source_id,
        "sha256": sha256(path),
        "tamano_bytes": path.stat().st_size,
        "fecha_modificacion": iso_from_timestamp(path.stat().st_mtime),
        "hojas": [],
        "contiene_datos_personales": "SI",
        "contiene_datos_sensibles": "POSIBLE",
        "muestras_reales_incluidas": "NO",
        "observacion_seguridad": "Perfil de Excel sin muestras de registros.",
    }
    derivatives: list[dict[str, Any]] = []
    for idx, ws in enumerate(wb.worksheets, start=1):
        max_row = ws.max_row or 0
        max_col = ws.max_column or 0
        formula_cells = 0
        empty_rows = 0
        nonempty_by_col = [0] * max_col
        type_counter: Counter[str] = Counter()
        header_row_idx = None
        header_values: list[str] = []
        rows_out: list[list[str]] = []

        for row_idx in range(1, max_row + 1):
            row_values: list[str] = []
            nonempty_this_row = 0
            for col_idx in range(1, max_col + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                value = cell.value
                if isinstance(value, str) and value.startswith("="):
                    formula_cells += 1
                    type_counter["FORMULA_ALMACENADA"] += 1
                elif value is None:
                    type_counter["VACIO"] += 1
                else:
                    type_counter[type(value).__name__] += 1
                text = cell_to_text(value)
                row_values.append(text)
                if text != "":
                    nonempty_this_row += 1
                    nonempty_by_col[col_idx - 1] += 1
            if nonempty_this_row == 0:
                empty_rows += 1
            elif header_row_idx is None and row_idx <= 50 and nonempty_this_row >= 2:
                header_row_idx = row_idx
                header_values = row_values
            rows_out.append(row_values)

        empty_cols = sum(1 for count in nonempty_by_col if count == 0)
        header_tokens = " ".join(header_values).upper()
        key_candidates = [
            token
            for token in [
                "RUT",
                "DV",
                "DIG",
                "CODCLI",
                "CODIGO_UNICO",
                "CODCARPR",
                "CODCARR",
                "PLAN_ESTUDIOS",
            ]
            if token in header_tokens
        ]
        relevance = "pendiente de clasificación"
        if any(token in header_tokens for token in ["RUT", "ALUMNO", "CODCLI", "PROMEDIO", "NOTA", "CODCARPR"]):
            relevance = "potencialmente relevante"
        if any(token in header_tokens for token in ["CODIGO_UNICO", "PLAN_ESTUDIOS", "UNIDADES"]):
            relevance = "relevante para Avance Curricular"

        derived_name = f"PROMEDIOSDEALUMNOS_7804__HOJA_{safe_sheet_name(ws.title)}.tsv"
        derived_path = DER_DIR / derived_name
        write_rows_tsv(derived_path, rows_out)

        sheet_profile = {
            "indice_hoja": idx,
            "nombre_hoja": ws.title,
            "filas": max_row,
            "columnas": max_col,
            "celdas_con_formula": formula_cells,
            "celdas_combinadas": len(list(ws.merged_cells.ranges)),
            "rangos_combinados": [str(rng) for rng in ws.merged_cells.ranges],
            "filas_completamente_vacias": empty_rows,
            "columnas_completamente_vacias": empty_cols,
            "encabezados_detectados": header_values,
            "posicion_encabezado": header_row_idx if header_row_idx is not None else "NO_DETERMINADO",
            "tipos_observados": dict(type_counter),
            "campos_clave_candidatos": key_candidates,
            "clasificacion": relevance,
            "exportacion_tsv": {
                "ruta": str(derived_path),
                "sha256": sha256(derived_path),
                "modo_formula": "FORMULA_ALMACENADA_NO_EVALUADA",
                "muestras_reales_incluidas_en_perfil": "NO",
            },
        }
        workbook_profile["hojas"].append(sheet_profile)
        derivatives.append(
            {
                "ID_DERIVADO": f"DERIVADO_{source_id}_HOJA_{idx}",
                "ID_FUENTE_ORIGEN": source_id,
                "NOMBRE_ORIGEN": path.name,
                "NOMBRE_DERIVADO": derived_name,
                "RUTA_DERIVADO": str(derived_path),
                "TIPO_DERIVACION": "XLSX_HOJA_A_TSV_UTF8_FORMULAS_ALMACENADAS",
                "SCRIPT_GENERADOR": str(Path(__file__).relative_to(REPO)),
                "VERSION_SCRIPT": "1.0",
                "FECHA_GENERACION": NOW.isoformat(),
                "SHA256_ORIGEN": sha256(path),
                "SHA256_DERIVADO": sha256(derived_path),
                "FILAS_ORIGEN": max_row,
                "FILAS_DERIVADO": max_row,
                "COLUMNAS_ORIGEN": max_col,
                "COLUMNAS_DERIVADO": max_col,
                "ORDEN_FILAS_PRESERVADO": "SI",
                "ORDEN_COLUMNAS_PRESERVADO": "SI",
                "ENCABEZADOS_PRESERVADOS": "SI",
                "TIPOS_FORZADOS_A_TEXTO": "SI",
                "CAMBIOS_REALIZADOS": "Exportación técnica de hoja Excel a TSV UTF-8; fórmulas almacenadas como fórmula, sin evaluación.",
                "PERDIDAS_DE_INFORMACION_DETECTADAS": "NO_DETERMINADO",
                "ESTADO_VALIDACION": "CONGELADO_CON_OBSERVACIONES",
                "OBSERVACIONES": "Excel preservado como original probatorio; TSV no reemplaza al original.",
            }
        )
    return workbook_profile, derivatives



def compare_instructivo(txt_path: Path, pdf_path: Path) -> dict[str, Any]:
    return {
        "decision_interna": "DI-AC-2026-001",
        "estado": "PDF_RETIRADO_NO_COMPARAR",
        "dictamen": "El TXT es fuente normativa única; no corresponde comparar TXT/PDF.",
    }


def build_manifest_rows(
    found: dict[str, list[Path]],
    copies: dict[str, Path],
    profiles: dict[str, dict[str, Any]],
    visibility: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in EXPECTED_SOURCES:
        matches = found[item["id"]]
        source = matches[0] if len(matches) == 1 else None
        copy = copies.get(item["id"])
        profile = profiles.get(item["id"], {})
        if source and copy:
            source_hash = sha256(source)
            copy_hash = sha256(copy)
            source_stat = stat_info(source)
            copy_stat = stat_info(copy)
            status = "CONGELADO_VALIDADO" if source_hash == copy_hash else "ERROR_HASH"
            hash_match = "SI" if source_hash == copy_hash else "NO"
            obs = "Copia validada byte a byte por SHA-256."
        elif len(matches) > 1:
            source_hash = copy_hash = "NO_APLICA"
            source_stat = {"size": "NO_APLICA", "mtime": "NO_APLICA"}
            copy_stat = {"size": "NO_APLICA", "mtime": "NO_APLICA"}
            status = "CANDIDATOS_MULTIPLES"
            hash_match = "NO_APLICA"
            obs = "Múltiples candidatos por nombre normalizado; selección detenida."
        else:
            source_hash = copy_hash = "NO_APLICA"
            source_stat = {"size": "NO_APLICA", "mtime": "NO_APLICA"}
            copy_stat = {"size": "NO_APLICA", "mtime": "NO_APLICA"}
            status = "NO_ENCONTRADO"
            hash_match = "NO_APLICA"
            obs = "Archivo no encontrado en Descargas por nombre normalizado."

        personal = item["personal"]
        apt_git = "NO" if personal == "SI" or visibility.get("private") != "SI" else "SI_CON_REVISION"
        apt_push = "NO" if personal == "SI" or visibility.get("private") != "SI" else "SI_CON_REVISION"
        rows.append(
            {
                "ID_FUENTE": item["id"],
                "PROCESO": PROCESS,
                "SUBPROCESO": item["subprocess"],
                "ANIO_PROCESO": YEAR_PROCESS,
                "ANIO_REFERENCIA_DATOS": YEAR_DATA,
                "PERIODO_ACADEMICO": ACADEMIC_PERIOD,
                "NOMBRE_ORIGINAL": item["name"] if not source else source.name,
                "NOMBRE_NORMALIZADO_UNICODE": nfc(item["name"]),
                "CLASIFICACION": item["classification"],
                "NIVEL_RESPALDO": item["backup_level"],
                "ORIGEN": "Descargas local",
                "RUTA_ORIGEN": str(source) if source else "NO_APLICA",
                "RUTA_CONGELADA": str(copy) if copy else "NO_APLICA",
                "FORMATO": item["format"],
                "EXTENSION": item["extension"],
                "TAMANO_BYTES_ORIGEN": source_stat["size"],
                "TAMANO_BYTES_COPIA": copy_stat["size"],
                "FECHA_MODIFICACION_ORIGEN": source_stat["mtime"],
                "FECHA_CONGELAMIENTO": NOW.isoformat(),
                "ZONA_HORARIA": "America/Santiago",
                "SHA256_ORIGEN": source_hash,
                "SHA256_COPIA": copy_hash,
                "HASH_COINCIDE": hash_match,
                "CODIFICACION_DETECTADA": profile.get("codificacion_detectada", "NO_APLICA"),
                "DELIMITADOR_DETECTADO": profile.get("delimitador_detectado", "NO_APLICA"),
                "TIENE_ENCABEZADO": profile.get("tiene_encabezado", "NO_APLICA"),
                "FILAS_OBSERVADAS": profile.get("filas_datos", profile.get("filas", "NO_APLICA")),
                "COLUMNAS_OBSERVADAS": profile.get("columnas", "NO_APLICA"),
                "HOJAS_OBSERVADAS": len(profile.get("hojas", [])) if item["format"] == "XLSX" else "NO_APLICA",
                "CONTIENE_DATOS_PERSONALES": personal,
                "CONTIENE_DATOS_SENSIBLES": item["sensitive"],
                "APTO_PARA_GIT": apt_git,
                "APTO_PARA_PUSH": apt_push,
                "ESTADO_VALIDACION": status,
                "OBSERVACIONES": obs,
            }
        )
    return rows


def set_readonly(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def write_policy(visibility: dict[str, str]) -> None:
    content = f"""# Política de Datos y Git - Avance Curricular SIES 2026

Proceso: {PROCESS}

Fecha de emisión: {NOW.isoformat()} America/Santiago

## Visibilidad del repositorio

- Remote observado: `https://github.com/Alexitho0o/avance_curricular.git`
- Verificación: {visibility.get("estado", "NO_DETERMINADO")}
- Visibilidad reportada: {visibility.get("visibility", "NO_DETERMINADO")}
- Privado: {visibility.get("private", "NO_DETERMINADO")}

## Conservación solo local

Se conservan solo localmente las copias originales y derivados ubicados bajo:

- `avance_curricular_2026/00_fuentes_congeladas/`
- `avance_curricular_2026/10_resultados/`
- `avance_curricular_2026/11_archivos_subida/`

Estas rutas pueden contener RUT, pasaporte, nombres, apellidos, sexo, fecha de nacimiento y datos académicos.

## Elementos versionables

Pueden versionarse, previa revisión:

- scripts reproducibles;
- documentación metodológica sin muestras reales de estudiantes;
- contratos de datos;
- matrices normativas;
- inventarios sin registros personales;
- hashes, conteos y reportes agregados.

## Elementos no aptos para Git ni push

No se deben incorporar al historial Git:

- originales descargados desde PES o fuentes institucionales con datos personales;
- TSV derivados con datos personales;
- Excel institucional `PROMEDIOSDEALUMNOS_7804.xlsx`;
- salidas de control o PES con registros reales.

## Reproducción sin exposición

Para reproducir la fase inicial, ejecutar el script desde el repositorio local con las fuentes originales disponibles en `/Users/alexi/Downloads`. El script genera manifiestos, perfiles sin muestras reales, hashes y contratos. Los archivos con datos personales quedan ignorados por `.gitignore`.
"""
    (PROCESS_ROOT / "01_documentacion" / "POLITICA_DATOS_Y_GIT.md").write_text(content, encoding="utf-8")


def build_normative_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(
        rid: str,
        subprocess_: str,
        section: str,
        page: str,
        field: str,
        rule: str,
        typ: str,
        implementation: str,
        validation: str,
        severity: str = "ALTA",
        status_: str = "EXTRAIDA_TXT",
        obs: str = "",
    ) -> None:
        rows.append(
            {
                "ID_REGLA": rid,
                "PROCESO": PROCESS,
                "SUBPROCESO": subprocess_,
                "ANIO_PROCESO": YEAR_PROCESS,
                "ANIO_DATOS": YEAR_DATA,
                "PERIODO": ACADEMIC_PERIOD,
                "SECCION_INSTRUCTIVO": section,
                "PAGINA": page,
                "CAMPO_O_TEMA": field,
                "REGLA_OFICIAL": rule,
                "TIPO_REGLA": typ,
                "NIVEL_RESPALDO": "TXT_OFICIAL_OBSERVADO",
                "FUENTE": "Instructivo_Avance Curricular SIES - 2026.txt",
                "IMPLEMENTACION_REQUERIDA": implementation,
                "VALIDACION_REQUERIDA": validation,
                "SEVERIDAD": severity,
                "ESTADO": status_,
                "OBSERVACIONES": obs or "NO_APLICA",
            }
        )

    add(
        "AC2026-GEN-001",
        "Proceso",
        "1. Introducción",
        "1",
        "Plazo",
        "El plazo de carga del archivo correctamente completado es el 10 de julio de 2026.",
        "TEMPORALIDAD",
        "Registrar fecha límite y no desplazar año de proceso.",
        "Control documental.",
    )
    add(
        "AC2026-GEN-002",
        "Proceso",
        "2. Alcance",
        "2",
        "Universo",
        "La solicitud se construye sobre estudiantes de pregrado informados en matrícula 2025 y carreras asociadas.",
        "UNIVERSO",
        "Usar precargas oficiales como estructura de referencia.",
        "Cruzar matrícula contra carreras solo después de validar congelamiento.",
    )
    add(
        "AC2026-GEN-003",
        "Matrícula Avance Curricular 2026",
        "3.2 letra g",
        "4-5",
        "Avance curricular",
        "El avance curricular vincula unidades aprobadas en un periodo respecto del total del plan.",
        "DEFINICION",
        "Diferenciar avance anual y acumulado.",
        "Validar unidades contra total del plan.",
    )
    add(
        "AC2026-GEN-004",
        "Matrícula Avance Curricular 2026",
        "IMPORTANTE cambio interno",
        "5",
        "Carrera informada en 2025",
        "El avance consultado corresponde a la carrera en que el/la estudiante fue informado/a en 2025; no trasladar avance de una nueva carrera sin continuidad natural.",
        "REGLA_FUNCIONAL",
        "Mantener referencia a matrícula 2025.",
        "Controlar cambios internos con evidencia institucional.",
    )
    add(
        "AC2026-GEN-005",
        "Matrícula Avance Curricular 2026",
        "3.2 letras i-j",
        "5",
        "Convalidaciones y reconocimientos",
        "En avance anual 2025 no se incluyen unidades por validación de estudios o reconocimiento; en acumulado sí se incluyen cuando corresponda.",
        "REGLA_FUNCIONAL",
        "Separar anual y acumulado.",
        "Validar fuente institucional de convalidaciones y reconocimientos.",
    )
    add(
        "AC2026-GEN-006",
        "Matrícula Avance Curricular 2026",
        "3.2 letra j",
        "5",
        "Tolerancia 25%",
        "El total aprobado tiene como límite de referencia el total del plan; si sobrepasa se aplicará tolerancia de 25%.",
        "VALIDACION",
        "Generar alerta/bloqueo según regla operativa documentada.",
        "Comparar UNID_APROBADAS_TOTAL contra TOTAL_UNIDADES_MEDIDA.",
    )
    add(
        "AC2026-GEN-007",
        "Proceso",
        "4.1 Temporalidad",
        "6",
        "30 de abril 2025",
        "Se consideran estudiantes informados como matrícula y/o inscripción al 30 de abril de 2025.",
        "UNIVERSO",
        "No usar matrícula actual 2026 como universo.",
        "Validar contra precarga oficial.",
    )
    add(
        "AC2026-GEN-008",
        "Proceso",
        "4.2 Cargas",
        "6",
        "Dos cargas",
        "El módulo se compone de Carreras Avance Curricular 2026 y Matrícula Avance Curricular 2026.",
        "ESTRUCTURA",
        "Separar pipelines y contratos.",
        "Validar orden de ejecución.",
    )
    add(
        "AC2026-GEN-009",
        "Carreras Avance Curricular 2026",
        "4.2 Precarga Carreras",
        "6",
        "Campos no modificables",
        "La institución no puede modificar valores precargados, con excepción de plan de estudios y vigencia, y puede duplicar carrera para más de un plan vigente.",
        "MODIFICABILIDAD",
        "Preservar campos no modificables.",
        "Comparar contra precarga original.",
    )
    add(
        "AC2026-GEN-010",
        "Matrícula Avance Curricular 2026",
        "4.2 Precarga Matrícula",
        "6-7",
        "Campos faltantes",
        "La institución debe llenar presencia semestral, avance anual 2025 y avance acumulado.",
        "MODIFICABILIDAD",
        "Completar solo campos permitidos con fuente institucional.",
        "Comparar campos no modificables contra precarga.",
    )
    add(
        "AC2026-GEN-011",
        "Matrícula Avance Curricular 2026",
        "IMPORTANTE VIGENCIA",
        "7",
        "VIGENCIA",
        "En matrícula deben considerarse vigentes (1) todos los registros aunque la persona se haya retirado después del 30 de abril de 2025; vigencia solo mantiene o elimina el registro del proceso actual.",
        "REGLA_FUNCIONAL",
        "No interpretar vigencia como estado académico actual.",
        "Requerir evidencia para VIGENCIA=0.",
    )
    add(
        "AC2026-GEN-012",
        "Proceso",
        "Anexo III",
        "15",
        "Preparación PES",
        "Para cargar en PES se debe eliminar la primera columna correspondiente al Código de la Institución y los encabezados.",
        "SALIDA_TECNICA",
        "Eliminar primera columna y encabezados solo en archivo PES final aprobado.",
        "Validar columna institucional antes de eliminar.",
    )
    add(
        "AC2026-GEN-013",
        "Proceso",
        "Anexo III",
        "17",
        "Orden de cargas",
        "Debe cargarse primero Carreras y posteriormente Matrícula; de lo contrario el sistema puede arrojar error.",
        "ORDEN_EJECUCION",
        "Implementar gate: matrícula depende de carreras validada.",
        "Validar catálogo de CODIGO_UNICO + PLAN_ESTUDIOS.",
    )

    for pos, field in enumerate(CARRERAS_FIELDS, start=1):
        definition = FIELD_DEFINITIONS[field]
        mod = "modificable" if field in CARRERAS_MODIFIABLE else "no modificable"
        add(
            f"AC2026-CAR-CAMPO-{pos:02d}",
            "Carreras Avance Curricular 2026",
            "Anexo I",
            "8-10",
            field,
            f"{field}: {definition['def']} Campo {mod}. Dominio: {definition['domain']}",
            "CAMPO_OFICIAL",
            "Incluir en contrato Carreras sin columna institucional.",
            "Validar posición, obligatoriedad, dominio y modificabilidad.",
            "ALTA" if field in {"CODIGO_UNICO", "PLAN_ESTUDIOS", "TIPO_UNIDAD_MEDIDA", "TOTAL_UNIDADES_MEDIDA", "VIGENCIA"} else "MEDIA",
        )

    for pos, field in enumerate(MATRICULA_FIELDS, start=1):
        definition = FIELD_DEFINITIONS[field]
        mod = "modificable" if field in MATRICULA_MODIFIABLE else "no modificable"
        add(
            f"AC2026-MAT-CAMPO-{pos:02d}",
            "Matrícula Avance Curricular 2026",
            "Anexo II",
            "11-14",
            field,
            f"{field}: {definition['def']} Campo {mod}. Dominio: {definition['domain']}",
            "CAMPO_OFICIAL",
            "Incluir en contrato Matrícula sin columna institucional.",
            "Validar posición, obligatoriedad, dominio y modificabilidad.",
            "ALTA" if field in {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "CODIGO_UNICO", "PLAN_ESTUDIOS", "UNIDADES_APROBADAS", "UNID_APROBADAS_TOTAL", "VIGENCIA"} else "MEDIA",
        )

    annex_iv = [
        "Uno o más atributos no modificables han sido editados con respecto a la precarga.",
        "Los valores permitidos para VIGENCIA son 0 y 1.",
        "Para TIPO_UNIDAD_MEDIDA 3 debe especificar la unidad de medida que utiliza.",
        "Campo OTRA_UNIDAD_MEDIDA se completa solo si TIPO_UNIDAD_MEDIDA es 3.",
        "TOTAL_UNIDADES_MEDIDA no coincide con la suma de las unidades ingresadas por año.",
        "Tipo de unidad de medida puede ser 1, 2 o 3.",
        "Distribución de unidades de medida no coincide con duración de la carrera.",
    ]
    for idx, msg in enumerate(annex_iv, start=1):
        add(
            f"AC2026-CAR-VAL-{idx:02d}",
            "Carreras Avance Curricular 2026",
            "Anexo IV",
            "21",
            "Validación Carreras",
            msg,
            "VALIDACION_EXPLICITA",
            "Implementar como validación de control antes de PES.",
            "Registrar errores por fila/campo sin corregir automáticamente.",
            "ALTA",
        )

    annex_v = [
        "Cantidad total de unidades aprobadas es excesivamente superior al número total de unidades de la carrera.",
        "Uno o más atributos no modificables han sido editados respecto a la precarga.",
        "Los valores permitidos para CURSO_1ER_SEM son SI y NO.",
        "Los valores permitidos para CURSO_2DO_SEM son SI y NO.",
        "Cantidad de unidades aprobadas total no puede ser mayor a las unidades cursadas.",
        "Cantidad de unidades aprobadas en 2025 no puede ser mayor a las unidades cursadas.",
        "Combinación CODIGO_UNICO + PLAN_ESTUDIOS ingresado no existe en la carga de carreras.",
        "Si campos CURSO_1ER_SEM y CURSO_2DO_SEM se informan como NO, UNIDADES_CURSADAS debe ser 0.",
        "Los valores permitidos para VIGENCIA son 0 y 1.",
    ]
    for idx, msg in enumerate(annex_v, start=1):
        add(
            f"AC2026-MAT-VAL-{idx:02d}",
            "Matrícula Avance Curricular 2026",
            "Anexo V",
            "22",
            "Validación Matrícula",
            msg,
            "VALIDACION_EXPLICITA",
            "Implementar como validación de control antes de PES.",
            "Registrar errores por fila/campo sin corregir automáticamente.",
            "ALTA",
        )

    add(
        "AC2026-AMB-001",
        "Proceso",
        "Anexo III",
        "17",
        "Año nombrado en texto de combinación",
        "El texto de Anexo III menciona combinaciones para carga Carreras Avance Curricular 2025 y Matrícula Avance Curricular Matrícula 2025, dentro de un proceso e IDs 2026.",
        "AMBIGUEDAD",
        "No cambiar año del proceso; conservar evidencia textual.",
        "Documentar como ambigüedad de redacción no resuelta por código.",
        "MEDIA",
        "PENDIENTE",
        "Debe revisarse si la plataforma muestra nomenclatura distinta; no bloquea la fase 00-03.",
    )
    add(
        "AC2026-VAC-001",
        "Carreras Avance Curricular 2026",
        "Anexo I",
        "8-10",
        "Total y distribución de unidades",
        "El instructivo exige tipo, total y distribución de unidades, pero la fuente institucional definitiva no se identifica en el instructivo.",
        "VACIO_OPERATIVO",
        "Requerir catálogo/mallas/planes institucionales.",
        "Bloquear salida PES si falta fuente institucional.",
        "ALTA",
        "PENDIENTE",
    )
    return rows


def write_normative_outputs(rows: list[dict[str, str]]) -> None:
    fields = [
        "ID_REGLA",
        "PROCESO",
        "SUBPROCESO",
        "ANIO_PROCESO",
        "ANIO_DATOS",
        "PERIODO",
        "SECCION_INSTRUCTIVO",
        "PAGINA",
        "CAMPO_O_TEMA",
        "REGLA_OFICIAL",
        "TIPO_REGLA",
        "NIVEL_RESPALDO",
        "FUENTE",
        "IMPLEMENTACION_REQUERIDA",
        "VALIDACION_REQUERIDA",
        "SEVERIDAD",
        "ESTADO",
        "OBSERVACIONES",
    ]
    write_tsv(PROCESS_ROOT / "07_control" / "MATRIZ_NORMATIVA.tsv", rows, fields)
    summary = Counter(row["TIPO_REGLA"] for row in rows)
    md = [
        "# Matriz normativa - Avance Curricular SIES 2026",
        "",
        f"Fuente textual: `Instructivo_Avance Curricular SIES - 2026.txt`.",
        f"Fecha de extracción: {NOW.isoformat()} America/Santiago.",
        "",
        "## Resumen",
        "",
    ]
    for key, value in sorted(summary.items()):
        md.append(f"- {key}: {value}")
    md.extend(
        [
            "",
            "## Criterios de lectura",
            "",
            "- La versión TXT se usó como fuente normativa textual principal.",
            "- El PDF fue retirado por decisión interna DI-AC-2026-001; el TXT es fuente normativa única.",
            "- Las reglas se separan entre regla oficial, validación, ambigüedad y vacío operativo.",
            "- No se completaron vacíos con supuestos ni con reglas de otros procesos.",
            "",
            "## Contradicciones y vacíos identificados",
            "",
            "- `AC2026-AMB-001`: redacción de Anexo III usa denominación 2025 en la descripción de combinaciones dentro del proceso 2026.",
            "- `AC2026-VAC-001`: faltan fuentes institucionales definitivas para total y distribución de unidades por plan.",
            "",
            "La matriz completa está en `avance_curricular_2026/07_control/MATRIZ_NORMATIVA.tsv`.",
            "",
        ]
    )
    (PROCESS_ROOT / "01_documentacion" / "01_MATRIZ_NORMATIVA.md").write_text("\n".join(md), encoding="utf-8")


def build_contract(subprocess_: str, fields: list[str], modifiable: set[str], page: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for pos, field in enumerate(fields, start=1):
        info = FIELD_DEFINITIONS[field]
        preloaded = "NO" if field in modifiable and field not in {"PLAN_ESTUDIOS", "VIGENCIA"} else "SI"
        if field in {
            "TIPO_UNIDAD_MEDIDA",
            "OTRA_UNIDAD_MEDIDA",
            "TOTAL_UNIDADES_MEDIDA",
            "UNIDADES_1ER_ANIO",
            "UNIDADES_2DO_ANIO",
            "UNIDADES_3ER_ANIO",
            "UNIDADES_4TO_ANIO",
            "UNIDADES_5TO_ANIO",
            "UNIDADES_6TO_ANIO",
            "UNIDADES_7MO_ANIO",
            "CURSO_1ER_SEM",
            "CURSO_2DO_SEM",
            "UNIDADES_CURSADAS",
            "UNIDADES_APROBADAS",
            "UNID_CURSADAS_TOTAL",
            "UNID_APROBADAS_TOTAL",
        }:
            preloaded = "NO"
        rows.append(
            {
                "POSICION": str(pos),
                "NOMBRE_CAMPO": field,
                "NOMBRE_DESCRIPTIVO": info["desc"],
                "SUBPROCESO": subprocess_,
                "DEFINICION_OFICIAL": info["def"],
                "TIPO_DATO": info["type"],
                "LONGITUD": "NO_DETERMINADO",
                "DOMINIO": info["domain"],
                "CODIGOS": info["domain"] if any(token in info["domain"] for token in [";", "0 ", "1 ", "SI"]) else "NO_APLICA",
                "OBLIGATORIO": "SI" if field in modifiable or field in {"CODIGO_UNICO", "TIPO_DOCUMENTO", "NUM_DOCUMENTO"} else "SI_PRECARGADO",
                "PRECARGADO": preloaded,
                "MODIFICABLE": "SI" if field in modifiable else "NO",
                "NULO_PERMITIDO": "NO_DETERMINADO",
                "FUENTE_NORMATIVA": f"Instructivo_Avance Curricular SIES - 2026.txt, Anexo {'I' if 'Carreras' in subprocess_ else 'II'}, página {page}",
                "FUENTE_INSTITUCIONAL": "PENDIENTE",
                "REGLA_TRANSFORMACION": "Preservar exactamente si no modificable; completar solo con fuente institucional si modificable.",
                "VALIDACION_ESTRUCTURAL": "Posición, nombre, tipo textual y cantidad de columnas.",
                "VALIDACION_SEMANTICA": "Dominio oficial y reglas explícitas del instructivo.",
                "VALIDACION_CRUZADA": (
                    "Llave CODIGO_UNICO + PLAN_ESTUDIOS con Carreras."
                    if field in {"CODIGO_UNICO", "PLAN_ESTUDIOS"}
                    else "NO_APLICA"
                ),
                "DEPENDENCIAS": "Carreras validada" if "Matrícula" in subprocess_ and field in {"CODIGO_UNICO", "PLAN_ESTUDIOS"} else "NO_APLICA",
                "LLAVE": "SI" if field in {"CODIGO_UNICO", "PLAN_ESTUDIOS", "TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"} else "NO",
                "SEVERIDAD": "ALTA" if field in modifiable or field in {"CODIGO_UNICO", "PLAN_ESTUDIOS"} else "MEDIA",
                "SALIDA_AUDITORIA": "SI",
                "ESTADO_IMPLEMENTACION": "CONTRATO_INICIAL",
                "OBSERVACIONES": "La columna institucional CODIGO_IES_NUM observada en precarga no forma parte del contrato PES.",
            }
        )
    return rows


def write_contracts() -> None:
    fields = [
        "POSICION",
        "NOMBRE_CAMPO",
        "NOMBRE_DESCRIPTIVO",
        "SUBPROCESO",
        "DEFINICION_OFICIAL",
        "TIPO_DATO",
        "LONGITUD",
        "DOMINIO",
        "CODIGOS",
        "OBLIGATORIO",
        "PRECARGADO",
        "MODIFICABLE",
        "NULO_PERMITIDO",
        "FUENTE_NORMATIVA",
        "FUENTE_INSTITUCIONAL",
        "REGLA_TRANSFORMACION",
        "VALIDACION_ESTRUCTURAL",
        "VALIDACION_SEMANTICA",
        "VALIDACION_CRUZADA",
        "DEPENDENCIAS",
        "LLAVE",
        "SEVERIDAD",
        "SALIDA_AUDITORIA",
        "ESTADO_IMPLEMENTACION",
        "OBSERVACIONES",
    ]
    carreras = build_contract("Carreras Avance Curricular 2026", CARRERAS_FIELDS, CARRERAS_MODIFIABLE, "8-10")
    matricula = build_contract("Matrícula Avance Curricular 2026", MATRICULA_FIELDS, MATRICULA_MODIFIABLE, "11-14")
    write_tsv(PROCESS_ROOT / "02_contratos" / "CONTRATO_CARRERAS_AVANCE_CURRICULAR_2026.tsv", carreras, fields)
    write_tsv(PROCESS_ROOT / "02_contratos" / "CONTRATO_MATRICULA_AVANCE_CURRICULAR_2026.tsv", matricula, fields)


def write_structure_observed(profile: dict[str, Any], out_path: Path, official_fields: list[str], modifiable: set[str]) -> None:
    header = profile.get("encabezados", [])
    rows = []
    empty_counts = profile.get("vacios_por_columna", {})
    distinct = profile.get("conteo_valores_distintos_por_columna", {})
    for idx, col in enumerate(header, start=1):
        rows.append(
            {
                "POSICION_OBSERVADA": idx,
                "NOMBRE_CAMPO_OBSERVADO": col,
                "EN_CONTRATO_PES": "SI" if col in official_fields else "NO",
                "PRIMERA_COLUMNA_INSTITUCIONAL": "SI" if idx == 1 and col == "CODIGO_IES_NUM" else "NO",
                "MODIFICABLE_SEGUN_INSTRUCTIVO": "SI" if col in modifiable else "NO",
                "NO_MODIFICABLE_SEGUN_INSTRUCTIVO": "NO" if col in modifiable or col == "CODIGO_IES_NUM" else "SI",
                "CONTIENE_DATOS_PERSONALES_POR_NOMBRE": "SI" if col in PERSONAL_FIELD_NAMES else "NO",
                "VACIOS_OBSERVADOS": empty_counts.get(col, "NO_DETERMINADO"),
                "VALORES_DISTINTOS_CONTEO": distinct.get(col, "NO_DETERMINADO"),
                "TIPOS_OBSERVADOS": profile.get("tipos_observados_por_columna", {}).get(col, []),
                "OBSERVACIONES": (
                    "Columna institucional a eliminar solo al generar PES final."
                    if idx == 1 and col == "CODIGO_IES_NUM"
                    else "NO_APLICA"
                ),
            }
        )
    write_tsv(
        out_path,
        rows,
        [
            "POSICION_OBSERVADA",
            "NOMBRE_CAMPO_OBSERVADO",
            "EN_CONTRATO_PES",
            "PRIMERA_COLUMNA_INSTITUCIONAL",
            "MODIFICABLE_SEGUN_INSTRUCTIVO",
            "NO_MODIFICABLE_SEGUN_INSTRUCTIVO",
            "CONTIENE_DATOS_PERSONALES_POR_NOMBRE",
            "VACIOS_OBSERVADOS",
            "VALORES_DISTINTOS_CONTEO",
            "TIPOS_OBSERVADOS",
            "OBSERVACIONES",
        ],
    )


def write_precarga_report(carreras_profile: dict[str, Any], matricula_profile: dict[str, Any]) -> None:
    md = [
        "# Reporte de Precargas - Avance Curricular SIES 2026",
        "",
        f"Fecha: {NOW.isoformat()} America/Santiago",
        "",
        "## Carreras",
        "",
        f"- Archivo: `{carreras_profile['archivo']}`",
        f"- Filas de datos: {carreras_profile['filas_datos']}",
        f"- Columnas: {carreras_profile['columnas']}",
        f"- Codificación: {carreras_profile['codificacion_detectada']}",
        f"- Delimitador: {carreras_profile['delimitador_detectado']}",
        f"- Primera columna: `{carreras_profile['primera_columna']}` ({carreras_profile['primera_columna_estado']})",
        f"- Campos faltantes oficiales: {', '.join(carreras_profile['campos_oficiales_faltantes']) or 'ninguno'}",
        "",
        "Campos modificables: "
        + ", ".join(field for field in CARRERAS_FIELDS if field in CARRERAS_MODIFIABLE),
        "",
        "## Matrícula",
        "",
        f"- Archivo: `{matricula_profile['archivo']}`",
        f"- Filas de datos: {matricula_profile['filas_datos']}",
        f"- Columnas: {matricula_profile['columnas']}",
        f"- Codificación: {matricula_profile['codificacion_detectada']}",
        f"- Delimitador: {matricula_profile['delimitador_detectado']}",
        f"- Primera columna: `{matricula_profile['primera_columna']}` ({matricula_profile['primera_columna_estado']})",
        f"- Campos faltantes oficiales: {', '.join(matricula_profile['campos_oficiales_faltantes']) or 'ninguno'}",
        "",
        "Campos modificables: "
        + ", ".join(field for field in MATRICULA_FIELDS if field in MATRICULA_MODIFIABLE),
        "",
        "## Observaciones",
        "",
        "- La columna `CODIGO_IES_NUM` se observa como primera columna institucional en ambas precargas; no se elimina en la carga congelada ni en derivados TSV.",
        "- Los perfiles no contienen muestras reales de estudiantes.",
        "- Los TSV derivados preservan orden de filas y columnas y se validan contra la lectura estructurada del CSV original.",
        "",
    ]
    (PROCESS_ROOT / "01_documentacion" / "02_REPORTE_PRECARGAS.md").write_text("\n".join(md), encoding="utf-8")


def classify_path(path: Path) -> str:
    s = str(path)
    name = path.name.lower()
    if s.startswith("avance_curricular_2026/00_fuentes_congeladas"):
        return "carga congelada local"
    if "instructivo" in name or "manual" in name:
        return "fuente normativa"
    if "precarga" in name:
        return "precarga oficial o evidencia de precarga"
    if s.startswith("scripts/") or s.startswith("src/") or s.startswith("core/scripts/"):
        return "código activo o transicional"
    if s.startswith("archive/") or "legacy" in s.lower():
        return "código legacy o resultado histórico"
    if s.startswith("resultados/"):
        return "resultado histórico o auditoría"
    if s.startswith("control/"):
        return "control, auditoría o gobernanza"
    if s.startswith("gobernanza"):
        return "gobernanza existente"
    if s.startswith("estudiantes_extranjeros_2026/"):
        return "otro proceso: estudiantes extranjeros"
    if s.startswith("personal_academico_2026/"):
        return "otro proceso: personal académico"
    if s.startswith("cned/") or s.startswith("indices_2025/"):
        return "otro proceso: CNED/índices"
    return "otro"


def sanitize_inventory_text(value: str) -> str:
    """Mask identifiers embedded in historical path names before versioning."""
    value = re.sub(r"(?i)(rut[_ -]?)[0-9][0-9._ -]{5,15}[0-9Kk]?", r"\1<ID_MASKED>", value)
    value = re.sub(r"(?i)(run[_ -]?)[0-9][0-9._ -]{5,15}[0-9Kk]?", r"\1<ID_MASKED>", value)
    return value


def git_status_map() -> dict[str, str]:
    result = {}
    for line in run(["git", "status", "--porcelain=v1", "-uall"]).splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        result[path] = status
    return result


def write_repository_inventory(git_ctx: dict[str, Any]) -> None:
    status = git_status_map()
    rows = []
    skip_dirs = {".git", ".venv", "__pycache__"}
    for root, dirs, files in os.walk(REPO):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for filename in files:
            path = root_path / filename
            rel = path.relative_to(REPO).as_posix()
            try:
                st = path.stat()
            except FileNotFoundError:
                continue
            rows.append(
                {
                    "RUTA": sanitize_inventory_text(rel),
                    "NOMBRE": sanitize_inventory_text(filename),
                    "EXTENSION": path.suffix,
                    "TAMANO_BYTES": st.st_size,
                    "FECHA_MODIFICACION": iso_from_timestamp(st.st_mtime),
                    "ESTADO_GIT": status.get(rel, "TRACKED_OR_UNMODIFIED"),
                    "CLASIFICACION": classify_path(Path(rel)),
                    "CONTIENE_DATOS_PERSONALES_POTENCIAL": "SI" if path.suffix.lower() in {".xlsx", ".csv", ".tsv"} and ("resultados" in rel or "data" in rel or "fuentes" in rel) else "NO_DETERMINADO",
                    "OBSERVACIONES": "Inventario por ruta y metadatos; no inspecciona registros personales.",
                }
            )
    write_tsv(
        PROCESS_ROOT / "07_control" / "INVENTARIO_REPOSITORIO.tsv",
        rows,
        [
            "RUTA",
            "NOMBRE",
            "EXTENSION",
            "TAMANO_BYTES",
            "FECHA_MODIFICACION",
            "ESTADO_GIT",
            "CLASIFICACION",
            "CONTIENE_DATOS_PERSONALES_POTENCIAL",
            "OBSERVACIONES",
        ],
    )

    code_rows = []
    patterns = re.compile(r"avance curricular|carreras_avance|matricula_avance|matrícula avance|sies", re.I)
    candidate_roots = ["scripts", "src", "core", "control", "docs", ".github", "tools"]
    for base in candidate_roots:
        base_path = REPO / base
        if not base_path.exists():
            continue
        for path in base_path.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if path.stat().st_size > 1_000_000:
                continue
            rel = path.relative_to(REPO).as_posix()
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            matches = len(patterns.findall(text)) + (1 if patterns.search(rel) else 0)
            if matches:
                code_rows.append(
                    {
                        "RUTA": sanitize_inventory_text(rel),
                        "CLASIFICACION": classify_path(Path(rel)),
                        "MENCIONES_AVANCE_SIES": matches,
                        "POTENCIAL_MEZCLA_PROCESOS": "SI" if re.search(r"matricula_unificada|mu2026|extranjeros|cned", text, re.I) else "NO",
                        "USO_RECOMENDADO": "NO_REACTIVAR_SIN_REVISION" if "archive" in rel or "legacy" in rel else "REVISAR_ANTES_DE_REUTILIZAR",
                        "OBSERVACIONES": "Conteo de menciones sin extraer datos personales.",
                    }
                )
    write_tsv(
        PROCESS_ROOT / "07_control" / "INVENTARIO_CODIGO_AVANCE_CURRICULAR.tsv",
        code_rows,
        [
            "RUTA",
            "CLASIFICACION",
            "MENCIONES_AVANCE_SIES",
            "POTENCIAL_MEZCLA_PROCESOS",
            "USO_RECOMENDADO",
            "OBSERVACIONES",
        ],
    )

    md = [
        "# Diagnóstico del repositorio - Avance Curricular SIES 2026",
        "",
        f"Fecha: {NOW.isoformat()} America/Santiago",
        "",
        "## Git",
        "",
        f"- Rama activa: `{git_ctx['branch']}`",
        f"- Commit inicial: `{git_ctx['commit']}`",
        f"- Merge-base con main: `{git_ctx['merge_base_main']}`",
        f"- Ahead/behind contra main: `{git_ctx['ahead_behind_main']}`",
        f"- Ramas candidatas por nombre: {', '.join(git_ctx['candidate_branches']) or 'ninguna'}",
        "",
        "La rama utilizada es la única rama local cuyo nombre contiene `avance`; se observa como rama de respaldo histórica. No se creó rama nueva.",
        "",
        "## Estado de trabajo",
        "",
        "Hay archivos no rastreados preexistentes de otros procesos al trabajar en esta rama. No fueron modificados ni agregados por esta ejecución.",
        "",
        "## Estructura y mezclas detectadas",
        "",
        "- Existen carpetas y scripts de Matrícula Unificada, Estudiantes Extranjeros, CNED, Índices y Personal Académico.",
        "- Existen resultados legacy de Avance Curricular 2025 en `archive/resultados_legacy` y `archive/resultados_diagnostico`.",
        "- No se deben reutilizar reglas ni salidas legacy como normativa para Avance Curricular 2026.",
        "",
        "## Inventarios",
        "",
        "- `avance_curricular_2026/07_control/INVENTARIO_REPOSITORIO.tsv`",
        "- `avance_curricular_2026/07_control/INVENTARIO_FUENTES.tsv`",
        "- `avance_curricular_2026/07_control/INVENTARIO_CODIGO_AVANCE_CURRICULAR.tsv`",
        "",
    ]
    (PROCESS_ROOT / "01_documentacion" / "00_DIAGNOSTICO_REPOSITORIO.md").write_text("\n".join(md), encoding="utf-8")


def write_sources_inventory(manifest_rows: list[dict[str, Any]], excluded: list[dict[str, str]]) -> None:
    rows = []
    for row in manifest_rows:
        rows.append(
            {
                "ID_FUENTE": row["ID_FUENTE"],
                "NOMBRE": row["NOMBRE_ORIGINAL"],
                "RUTA": row["RUTA_CONGELADA"],
                "CLASIFICACION": row["CLASIFICACION"],
                "PROCESO_ASOCIADO": row["PROCESO"],
                "ESTADO": row["ESTADO_VALIDACION"],
                "HASH": row["SHA256_COPIA"],
                "CONTIENE_DATOS_PERSONALES": row["CONTIENE_DATOS_PERSONALES"],
                "APTO_PARA_GIT": row["APTO_PARA_GIT"],
                "OBSERVACIONES": row["OBSERVACIONES"],
            }
        )
    for item in excluded:
        rows.append(
            {
                "ID_FUENTE": "EXCLUIDO",
                "NOMBRE": item["NOMBRE_ARCHIVO"],
                "RUTA": item["RUTA"],
                "CLASIFICACION": item["CLASIFICACION"],
                "PROCESO_ASOCIADO": item["PROCESO_ASOCIADO"],
                "ESTADO": "EXCLUIDO_OTRO_PROCESO",
                "HASH": "NO_CALCULADO",
                "CONTIENE_DATOS_PERSONALES": "NO_DETERMINADO",
                "APTO_PARA_GIT": "NO",
                "OBSERVACIONES": item["MOTIVO_EXCLUSION"],
            }
        )
    write_tsv(
        PROCESS_ROOT / "07_control" / "INVENTARIO_FUENTES.tsv",
        rows,
        [
            "ID_FUENTE",
            "NOMBRE",
            "RUTA",
            "CLASIFICACION",
            "PROCESO_ASOCIADO",
            "ESTADO",
            "HASH",
            "CONTIENE_DATOS_PERSONALES",
            "APTO_PARA_GIT",
            "OBSERVACIONES",
        ],
    )


def write_freeze_readme(
    git_ctx: dict[str, Any],
    manifest_rows: list[dict[str, Any]],
    derivative_rows: list[dict[str, Any]],
    excluded: list[dict[str, str]],
    comparison: dict[str, Any],
    visibility: dict[str, str],
) -> None:
    state = "CARGA_CONGELADA_VALIDADA"
    observations = []
    if any(row["ESTADO_VALIDACION"] != "CONGELADO_VALIDADO" for row in manifest_rows):
        state = "CARGA_CONGELADA_BLOQUEADA"
    if comparison["comparacion_contenido_textual"]["estado"] != "EXTRAIDO":
        state = "CARGA_CONGELADA_CON_OBSERVACIONES" if state != "CARGA_CONGELADA_BLOQUEADA" else state
        observations.append("El PDF fue retirado por decisión interna DI-AC-2026-001; no existe bloqueo por extracción PDF.")
    if git_ctx["status_porcelain"]:
        state = "CARGA_CONGELADA_CON_OBSERVACIONES" if state != "CARGA_CONGELADA_BLOQUEADA" else state
        observations.append("Working tree contiene cambios/no rastreados; los preexistentes no fueron tocados.")

    lines = [
        "# README Carga Congelada - Avance Curricular SIES 2026",
        "",
        f"Proceso: {PROCESS}",
        "Subprocesos: Carreras Avance Curricular 2026 (ID 16769); Matrícula Avance Curricular 2026 (ID 16768)",
        f"Año del proceso: {YEAR_PROCESS}",
        f"Año de referencia de datos: {YEAR_DATA}",
        f"Fecha y hora: {NOW.isoformat()}",
        "Zona horaria: America/Santiago",
        f"Rama: {git_ctx['branch']}",
        f"Commit inicial: {git_ctx['commit']}",
        f"Origen: {DOWNLOADS}",
        f"Ubicación congelada: {FREEZE_DIR}",
        "Método de copia: `shutil.copy2` con validación SHA-256 origen/copia.",
        f"Script usado: `{Path(__file__).relative_to(REPO)}`",
        "",
        "## Fuentes incluidas",
        "",
        "| ID | Nombre | Hash origen | Hash copia | Estado |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in manifest_rows:
        lines.append(
            f"| {row['ID_FUENTE']} | {row['NOMBRE_ORIGINAL']} | {row['SHA256_ORIGEN']} | {row['SHA256_COPIA']} | {row['ESTADO_VALIDACION']} |"
        )
    lines.extend(["", "## Fuentes excluidas", ""])
    if excluded:
        for item in excluded:
            lines.append(f"- `{item['NOMBRE_ARCHIVO']}`: {item['MOTIVO_EXCLUSION']}")
    else:
        lines.append("- No se detectaron exclusiones cercanas.")
    lines.extend(["", "## Derivados generados", ""])
    for row in derivative_rows:
        lines.append(f"- `{row['NOMBRE_DERIVADO']}`: {row['ESTADO_VALIDACION']} ({row['SHA256_DERIVADO']})")
    lines.extend(
        [
            "",
            "## Validaciones",
            "",
            "- Hash origen/copia: registrado en `manifiestos/MANIFIESTO_CARGA_CONGELADA.tsv`.",
            "- Equivalencia CSV a TSV: registrada en `perfiles/VALIDACION_EQUIVALENCIA_PRECARGA_CARRERAS.json` y `perfiles/VALIDACION_EQUIVALENCIA_PRECARGA_MATRICULA.json`.",
            "- Decisión DI-AC-2026-001: no corresponde comparación TXT/PDF; TXT fuente normativa única.",
            "",
            "## Datos personales y Git",
            "",
            f"- Visibilidad remota: {visibility.get('visibility', 'NO_DETERMINADO')} (privado: {visibility.get('private', 'NO_DETERMINADO')}).",
            "- Originales, derivados TSV y resultados con datos personales quedan ignorados por `.gitignore`.",
            "- No se ejecutó `git add`, `git commit`, `git push` ni apertura de PR.",
            "",
            "## Bloqueos y observaciones",
            "",
        ]
    )
    if observations:
        lines.extend(f"- {obs}" for obs in observations)
    else:
        lines.append("- No hay bloqueos de congelamiento.")
    lines.extend(["", f"Estado final: {state}", ""])
    (FREEZE_DIR / "README_CARGA_CONGELADA.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if FREEZE_DIR.exists():
        raise RuntimeError(f"La carpeta de congelamiento ya existe: {FREEZE_DIR}")
    ensure_dirs()
    git_ctx = get_git_context()
    visibility = repo_visibility()
    found, excluded = locate_sources()

    copies: dict[str, Path] = {}
    profiles: dict[str, dict[str, Any]] = {}
    derivative_rows: list[dict[str, Any]] = []
    readonly_paths: list[Path] = []

    for item in EXPECTED_SOURCES:
        matches = found[item["id"]]
        if len(matches) != 1:
            continue
        source = matches[0]
        dest = ORIG_DIR / source.name
        shutil.copy2(source, dest)
        copies[item["id"]] = dest
        readonly_paths.append(dest)

    for item in EXPECTED_SOURCES:
        copy = copies.get(item["id"])
        if not copy:
            continue
        if item["format"] == "CSV":
            expected = CARRERAS_FIELDS if item["id"] == "FUENTE_5810_CARRERAS" else MATRICULA_FIELDS
            profile = profile_csv(copy, item["id"], expected)
            profiles[item["id"]] = profile
            profile_name = "PERFIL_PRECARGA_CARRERAS.json" if item["id"] == "FUENTE_5810_CARRERAS" else "PERFIL_PRECARGA_MATRICULA.json"
            write_json(PROF_DIR / profile_name, profile)
            derivative = derive_csv_to_tsv(copy, item["id"], CSV_DERIVATIVES[item["id"]], profile)
            derivative_rows.append(derivative)
            readonly_paths.append(Path(derivative["RUTA_DERIVADO"]))
            if item["id"] == "FUENTE_5810_CARRERAS":
                write_structure_observed(
                    profile,
                    PROCESS_ROOT / "07_control" / "ESTRUCTURA_OBSERVADA_CARRERAS.tsv",
                    CARRERAS_FIELDS,
                    CARRERAS_MODIFIABLE,
                )
            else:
                write_structure_observed(
                    profile,
                    PROCESS_ROOT / "07_control" / "ESTRUCTURA_OBSERVADA_MATRICULA.tsv",
                    MATRICULA_FIELDS,
                    MATRICULA_MODIFIABLE,
                )
        elif item["format"] == "XLSX":
            profile, derivatives = profile_and_export_excel(copy, item["id"])
            profiles[item["id"]] = profile
            write_json(PROF_DIR / "PERFIL_PROMEDIOSDEALUMNOS_7804.json", profile)
            derivative_rows.extend(derivatives)
            readonly_paths.extend(Path(row["RUTA_DERIVADO"]) for row in derivatives)
        elif item["format"] == "TXT":
            enc, bom = detect_encoding(copy)
            text = copy.read_text(encoding=enc, errors="replace")
            profiles[item["id"]] = {
                "codificacion_detectada": enc,
                "bom": bom,
                "filas": text.count("\n") + 1,
                "columnas": "NO_APLICA",
                "tiene_encabezado": "NO_APLICA",
            }
        elif item["format"] == "PDF":
            profiles[item["id"]] = {
                "codificacion_detectada": "NO_APLICA",
                "filas": "NO_APLICA",
                "columnas": "NO_APLICA",
                "tiene_encabezado": "NO_APLICA",
            }

    comparison = {"estado": "PDF_RETIRADO_NO_COMPARAR", "decision_interna": "DI-AC-2026-001"}

    manifest_rows = build_manifest_rows(found, copies, profiles, visibility)
    manifest_fields = [
        "ID_FUENTE",
        "PROCESO",
        "SUBPROCESO",
        "ANIO_PROCESO",
        "ANIO_REFERENCIA_DATOS",
        "PERIODO_ACADEMICO",
        "NOMBRE_ORIGINAL",
        "NOMBRE_NORMALIZADO_UNICODE",
        "CLASIFICACION",
        "NIVEL_RESPALDO",
        "ORIGEN",
        "RUTA_ORIGEN",
        "RUTA_CONGELADA",
        "FORMATO",
        "EXTENSION",
        "TAMANO_BYTES_ORIGEN",
        "TAMANO_BYTES_COPIA",
        "FECHA_MODIFICACION_ORIGEN",
        "FECHA_CONGELAMIENTO",
        "ZONA_HORARIA",
        "SHA256_ORIGEN",
        "SHA256_COPIA",
        "HASH_COINCIDE",
        "CODIFICACION_DETECTADA",
        "DELIMITADOR_DETECTADO",
        "TIENE_ENCABEZADO",
        "FILAS_OBSERVADAS",
        "COLUMNAS_OBSERVADAS",
        "HOJAS_OBSERVADAS",
        "CONTIENE_DATOS_PERSONALES",
        "CONTIENE_DATOS_SENSIBLES",
        "APTO_PARA_GIT",
        "APTO_PARA_PUSH",
        "ESTADO_VALIDACION",
        "OBSERVACIONES",
    ]
    write_tsv(MAN_DIR / "MANIFIESTO_CARGA_CONGELADA.tsv", manifest_rows, manifest_fields)
    write_tsv(
        MAN_DIR / "ARCHIVOS_EXCLUIDOS_DESCARGAS.tsv",
        excluded,
        [
            "NOMBRE_ARCHIVO",
            "RUTA",
            "CLASIFICACION",
            "PROCESO_ASOCIADO",
            "MOTIVO_EXCLUSION",
            "FECHA_REVISION",
            "OBSERVACION",
        ],
    )
    write_tsv(
        MAN_DIR / "MANIFIESTO_DERIVADOS_TSV.tsv",
        derivative_rows,
        [
            "ID_DERIVADO",
            "ID_FUENTE_ORIGEN",
            "NOMBRE_ORIGEN",
            "NOMBRE_DERIVADO",
            "RUTA_DERIVADO",
            "TIPO_DERIVACION",
            "SCRIPT_GENERADOR",
            "VERSION_SCRIPT",
            "FECHA_GENERACION",
            "SHA256_ORIGEN",
            "SHA256_DERIVADO",
            "FILAS_ORIGEN",
            "FILAS_DERIVADO",
            "COLUMNAS_ORIGEN",
            "COLUMNAS_DERIVADO",
            "ORDEN_FILAS_PRESERVADO",
            "ORDEN_COLUMNAS_PRESERVADO",
            "ENCABEZADOS_PRESERVADOS",
            "TIPOS_FORZADOS_A_TEXTO",
            "CAMBIOS_REALIZADOS",
            "PERDIDAS_DE_INFORMACION_DETECTADAS",
            "ESTADO_VALIDACION",
            "OBSERVACIONES",
        ],
    )

    write_sources_inventory(manifest_rows, excluded)
    write_policy(visibility)
    write_repository_inventory(git_ctx)
    normative_rows = build_normative_rows()
    write_normative_outputs(normative_rows)
    write_contracts()
    if "FUENTE_5810_CARRERAS" in profiles and "FUENTE_5809_MATRICULA" in profiles:
        write_precarga_report(profiles["FUENTE_5810_CARRERAS"], profiles["FUENTE_5809_MATRICULA"])
    write_freeze_readme(git_ctx, manifest_rows, derivative_rows, excluded, comparison, visibility)

    set_readonly(readonly_paths)

    summary = {
        "proceso": PROCESS,
        "rama": git_ctx["branch"],
        "commit": git_ctx["commit"],
        "carga_congelada": str(FREEZE_DIR),
        "fuentes_encontradas": sum(1 for rows in found.values() if len(rows) == 1),
        "derivados_tsv": len(derivative_rows),
        "manifest": str(MAN_DIR / "MANIFIESTO_CARGA_CONGELADA.tsv"),
        "estado": "COMPLETADO_CON_OBSERVACIONES" if git_ctx["status_porcelain"] else "COMPLETADO",
    }
    write_json(LOG_DIR / "resumen_fase_00a_03.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
