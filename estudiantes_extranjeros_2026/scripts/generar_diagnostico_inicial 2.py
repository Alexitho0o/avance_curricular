#!/usr/bin/env python3
"""Diagnostico inicial para Estudiantes Extranjeros SIES 2026.

Este script no genera archivos de carga PES. Solo localiza/documenta el
instructivo, perfila fuentes existentes y crea artefactos de diagnostico.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import openpyxl
except Exception:  # pragma: no cover
    openpyxl = None


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path(__file__).resolve()
SUB = ROOT / "estudiantes_extranjeros_2026"
DOCS = SUB / "docs"
DATA_RAW = SUB / "data" / "raw"
DATA_INTERIM = SUB / "data" / "interim"
DATA_PROCESSED = SUB / "data" / "processed"
REPORTES = SUB / "resultados" / "reportes"
AUDITORIAS = SUB / "resultados" / "auditorias"
EVIDENCIAS = SUB / "resultados" / "evidencias"
CONFIG = SUB / "config"
BACKUPS = SUB / "backups"

RUN_TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

INSTRUCTIVO_ORIGINAL = ROOT / "Instructivo _Estudiantes_Extranjeros_SIES.txt"
INSTRUCTIVO_COPIA = DOCS / "Instructivo_Estudiantes_Extranjeros_SIES_2026.txt"

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache"}
INVENTORY_EXTS = {
    ".csv",
    ".tsv",
    ".xlsx",
    ".xls",
    ".xlsm",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".pdf",
}
DATA_EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".xlsm"}
CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
DOC_EXTS = {".md", ".txt", ".pdf"}
MAX_EXCEL_PROFILE_BYTES = 25_000_000


def ensure_dirs() -> None:
    for path in [
        DOCS,
        DATA_RAW,
        DATA_INTERIM,
        DATA_PROCESSED,
        REPORTES,
        AUDITORIAS,
        EVIDENCIAS,
        CONFIG,
        BACKUPS,
        SUB / "scripts",
        SUB / "resultados" / "archivos_subida",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    try:
        with path.open("rb") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def newline_count(path: Path) -> int:
    try:
        with path.open("rb") as f:
            return sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(1024 * 1024), b""))
    except Exception:
        return 0


def detect_encoding(path: Path) -> str:
    raw = path.read_bytes()[:4096]
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            raw.decode(enc)
            return enc.replace("-sig", "")
        except Exception:
            continue
    return "desconocida"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if row.get(k) is None else row.get(k) for k in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def no_accents_upper(value: Any) -> str:
    text = clean_text(value).upper()
    repl = str.maketrans("ÁÉÍÓÚÜÑ", "AEIOUUN")
    return text.translate(repl)


def normalize_doc(value: Any) -> str:
    text = clean_text(value).upper()
    return re.sub(r"[.\-,\s]", "", text)


def split_run(value: Any) -> tuple[str, str]:
    text = normalize_doc(value)
    if len(text) >= 2 and text[-1] in "0123456789K" and text[:-1].isdigit():
        return text[:-1], text[-1]
    return text, ""


def sniff_delimiter(sample: str, suffix: str) -> str:
    if suffix == ".tsv":
        return "\t"
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except Exception:
        counts = {d: sample.count(d) for d in [",", ";", "\t", "|"]}
        return max(counts, key=counts.get) if max(counts.values()) else ","


def classify_file(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    text = str(path).lower()
    if suffix in {".csv", ".tsv"}:
        return "CSV/TSV"
    if suffix in {".xlsx", ".xls", ".xlsm"}:
        return "Excel"
    if suffix == ".py":
        return "script_python"
    if suffix in CONFIG_EXTS:
        return "configuracion"
    if suffix in DOC_EXTS:
        return "documentacion"
    if "diccionario" in text or "gobernanza" in text:
        return "diccionario_variables"
    if "resultado" in text or "auditoria" in text or "reporte" in text:
        return "resultado/auditoria"
    return suffix.lstrip(".") or "archivo"


def infer_period(path: Path, headers: list[str]) -> str:
    text = f"{path} {' '.join(headers)}".lower()
    years = sorted(set(re.findall(r"20[0-9]{2}", text)))
    return "|".join(years) if years else "no_identificado"


def infer_level(path: Path, headers: list[str]) -> str:
    text = f"{path} {' '.join(headers)}".lower()
    if "intercambio" in text:
        return "intercambio"
    if "postgrado" in text or "postitulo" in text or "postítulo" in text:
        return "postgrado/postitulo"
    if "pregrado" in text:
        return "pregrado"
    if "oferta" in text or "carrera" in text or "programa" in text:
        return "oferta/programa"
    if "matricula" in text or "matrícula" in text or "estudiante" in text or "alumno" in text:
        return "estudiante/matricula"
    if "gobernanza" in text or "diccionario" in text:
        return "diccionario/gobernanza"
    if "auditoria" in text or "reporte" in text or "resultado" in text:
        return "resultado/auditoria"
    return "no_identificado"


def detect_identifier(headers: list[str]) -> str:
    normalized = {no_accents_upper(h) for h in headers}
    ids = []
    if "CODCLI" in normalized:
        ids.append("CODCLI")
    if {"N_DOC", "NUM_DOCUMENTO", "RUT", "RUN"} & normalized:
        ids.append("RUN/RUT/NUM_DOCUMENTO")
    if "DV" in normalized or "DIG" in normalized:
        ids.append("DV")
    if "PASAPORTE" in normalized:
        ids.append("PASAPORTE")
    if {"NOMBRE", "NOMBRES", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO"} & normalized:
        ids.append("NOMBRES")
    return "|".join(ids) if ids else "no_identificado"


KEYWORD_MAP = {
    "CODCLI": ["CODCLI"],
    "RUN/RUT": ["RUT", "RUN", "N_DOC", "NUM_DOCUMENTO", "TIPO_DOC", "TIPO_DOCUMENTO", "DV", "DIG"],
    "PASAPORTE": ["PASAPORTE"],
    "NACIONALIDAD": ["NAC", "NACIONALIDAD"],
    "PAIS_ESTUDIOS_SECUNDARIOS": ["PAIS_EST_SEC", "PAIS_ESTUDIOS_SECUNDARIOS", "COMUNACOLEGIO", "CIUDADCOLEGIO"],
    "CARRERA/PROGRAMA": ["CODCARPR", "COD_CAR", "CODIGO_UNICO", "CODIGO_CARRERA", "NOMBRE_CARRERA", "NOMBRE_L"],
    "SEDE": ["SEDE", "COD_SED", "COD_SEDE", "NOMBRE_SEDE"],
    "JORNADA": ["JORNADA", "JOR"],
    "MODALIDAD": ["MODALIDAD"],
    "INGRESO": ["ANIO_ING", "ANOINGRESO", "SEM_ING", "PERIODOINGRESO"],
    "VIGENCIA": ["VIG", "VIGENCIA", "ESTADOACADEMICO", "SITUACION"],
    "FECHA_NACIMIENTO": ["FECH_NAC", "FECHA_NACIMIENTO", "FECHANACIMIENTO"],
    "SEXO": ["SEXO"],
}


def useful_variables(headers: list[str], path: Path) -> str:
    text = " ".join([no_accents_upper(h) for h in headers] + [no_accents_upper(path.name)])
    hits = []
    for label, keys in KEYWORD_MAP.items():
        if any(k in text for k in keys):
            hits.append(label)
    return "|".join(hits)


def reuse_score(path: Path, headers: list[str], variables: str) -> tuple[str, str]:
    text = str(path).lower()
    if not variables:
        return "BAJA", "sin variables utiles detectadas por encabezado/nombre"
    if any(x in text for x in ["matricula_unificada", "archivo_listo_para_sies", "datosalumnos", "puente_sies", "oferta_academica", "gobernanza_columnas_mu"]):
        return "ALTA", "fuente alineada con MU/oferta/gobernanza ya validada"
    if any(x in text for x in ["matricula", "avance", "control", "reporte", "auditoria", "cned", "gobernanza"]):
        return "MEDIA", "fuente reutilizable con validacion de periodo y granularidad"
    return "MEDIA", "contiene variables utiles; requiere revision semantica"


def duplication_risk(path: Path, headers: list[str]) -> str:
    text = str(path).lower()
    if "archive" in text or "backup" in text or "bkp" in text or "legacy" in text:
        return "ALTO: archivo historico/respaldo"
    if "resultados" in text and ("archivo_listo_para_sies" in text or "pes_ready" in text):
        return "MEDIO: salida validada, no sobrescribir"
    if "control" in text or "gobernanza" in text or "catalogo" in text:
        return "BAJO: fuente maestra/control"
    return "MEDIO: verificar version antes de reutilizar"


def profile_text_table(path: Path) -> tuple[list[str], int, int, str, str]:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:8192]
    delimiter = sniff_delimiter(sample, path.suffix.lower())
    rows = 0
    header: list[str] = []
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader, [])
            rows = sum(1 for _ in reader)
    except Exception:
        header = []
        rows = line_count(path)
    return [clean_text(h) for h in header], rows, len(header), delimiter, ""


def profile_excel(path: Path) -> tuple[list[str], int, int, str, str]:
    if openpyxl is None:
        return [], 0, 0, "", "openpyxl no disponible"
    if path.suffix.lower() == ".xls":
        return [], 0, 0, "", "xls no perfilado; xlrd no disponible"
    if path.stat().st_size > MAX_EXCEL_PROFILE_BYTES:
        return [], 0, 0, "", "Excel mayor a umbral; solo metadata de archivo"
    if "archive/cleanup" in str(path).replace("\\", "/"):
        return [], 0, 0, "", "Excel en archive/cleanup; no se abrio"
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheet_summaries = []
        first_header: list[str] = []
        total_rows = 0
        max_cols = 0
        for ws in wb.worksheets[:12]:
            header: list[str] = []
            if ws.max_row:
                for row in ws.iter_rows(min_row=1, max_row=1, values_only=True):
                    header = [clean_text(x) for x in row]
                    break
            if not first_header and header:
                first_header = header
            total_rows += max(ws.max_row - 1, 0)
            max_cols = max(max_cols, ws.max_column)
            sheet_summaries.append(f"{ws.title}: filas={ws.max_row}, cols={ws.max_column}, encabezados={'; '.join(header[:25])}")
        wb.close()
        return first_header, total_rows, max_cols, " | ".join(sheet_summaries), ""
    except Exception as exc:
        return [], 0, 0, "", f"error perfilando Excel: {type(exc).__name__}: {exc}"


def inventory_repo() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        path_dir = Path(dirpath)
        if SUB in [path_dir, *path_dir.parents]:
            continue
        for filename in filenames:
            path = path_dir / filename
            suffix = path.suffix.lower()
            if suffix not in INVENTORY_EXTS:
                continue
            stat = path.stat()
            headers: list[str] = []
            n_rows = ""
            n_cols = ""
            hojas = ""
            delim = ""
            obs = ""
            if suffix in {".csv", ".tsv"}:
                headers, rows_count, cols_count, delim, obs = profile_text_table(path)
                n_rows = rows_count
                n_cols = cols_count
            elif suffix in {".xlsx", ".xls", ".xlsm"}:
                headers, rows_count, cols_count, hojas, obs = profile_excel(path)
                n_rows = rows_count
                n_cols = cols_count
            elif suffix in {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
                try:
                    text = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
                    headers = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", text)[:80]
                    n_rows = line_count(path)
                    n_cols = ""
                except Exception as exc:
                    obs = f"no se pudo leer muestra textual: {exc}"
            variables = useful_variables(headers, path)
            reuse, reuse_obs = reuse_score(path, headers, variables)
            obs = "; ".join([x for x in [obs, reuse_obs] if x])
            rows.append(
                {
                    "archivo": path.name,
                    "ubicacion": rel(path.parent),
                    "ruta_relativa": rel(path),
                    "tipo": classify_file(path),
                    "periodo": infer_period(path, headers),
                    "nivel_datos": infer_level(path, headers),
                    "identificador_disponible": detect_identifier(headers),
                    "variables_utiles": variables,
                    "posibilidad_reutilizacion": reuse,
                    "riesgo_duplicacion": duplication_risk(path, headers),
                    "observaciones": obs,
                    "tamano_bytes": stat.st_size,
                    "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "filas_detectadas": n_rows,
                    "columnas_detectadas": n_cols,
                    "delimitador": delim,
                    "hojas_excel": hojas,
                    "encabezados_muestra": " | ".join(headers[:80]),
                }
            )
    rows.sort(key=lambda r: (r["tipo"], r["ruta_relativa"]))
    return rows


REGULAR_ERRORS = [
    "Cuando el TIPO_RESIDENCIA_ESTUDIANTE es 2 o 3, el PAIS_ORIGEN se debe completar.",
    "Cuando no se tiene la informacion del TIPO_RESIDENCIA_ESTUDIANTE, no se debe completar el PAIS_ORIGEN.",
    "Cuando el TIPO_RESIDENCIA_ESTUDIANTE es 1, no se debe completar el PAIS_ORIGEN.",
    "En el campo PAIS_ORIGEN no puede ingresar el codigo 38 que corresponde a CHILE.",
    "La VIGENCIA considera valores 0 y 1.",
    "El PAIS_ESTUDIOS_SECUNDARIOS debe ser entre 1 y 197.",
    "El CODIGO_UNICO acepta codigos oficiales SIES de oferta 2025 o codigos temporales solicitados en este proceso.",
    "El DV debe ser nulo cuando el TIPO_DOCUMENTO es igual a P.",
    "El TIPO_DOCUMENTO debe ser R de RUT o P de Pasaporte.",
    "El DV debe completarse con valores de 0 a 9 y K cuando TIPO_DOCUMENTO es R.",
    "La NACIONALIDAD debe ser entre 1 y 197 y no puede ser 38 Chile.",
    "NUM_DOCUMENTO no puede contener letras/simbolos cuando TIPO_DOCUMENTO es R y no puede comenzar con 0.",
    "FECHA_NACIMIENTO no puede ser anterior a 01/01/1900 ni posterior a 30/06/2010.",
    "NOMBRE_UNIVERSIDAD_ORIGEN y PAIS_UNIVERSIDAD_ORIGEN se completan en conjunto.",
    "No se permiten espacios iniciales/finales ni dobles espacios en nombres/apellidos.",
]

INTERCAMBIO_ERRORS = [
    "ESP_TIPO_PROGRAMA_INTERCAMBIO se debe completar cuando TIPO_PROGRAMA_INTERCAMBIO es 4.",
    "NUM_DOCUMENTO no debe estar vacio.",
    "Cuando TIPO_RESIDENCIA_ESTUDIANTE es 2, PAIS_ORIGEN se debe completar.",
    "PAIS_ORIGEN no puede ser 38 Chile.",
    "COMUNA_PROGRAMA debe ser valida y en mayuscula.",
    "Cuando EXISTE_CONVENIO es 1, se debe completar NOMBRE_UNIVERSIDAD_ORIGEN.",
    "NOMBRE_UNIVERSIDAD_ORIGEN y PAIS_UNIVERSIDAD_ORIGEN se completan en conjunto.",
    "FECHA_INICIO_PROGRAMA no puede ser posterior a 2025.",
    "FECHA_TERMINO_PROGRAMA no puede ser menor que FECHA_INICIO_PROGRAMA.",
    "EXISTE_CONVENIO admite 1 SI, 2 NO y 0 Sin Informacion segun mensajes de error.",
    "TIPO_PROGRAMA_INTERCAMBIO admite 1 Programa de Intercambio, 2 Pasantias Medicas, 3 Cursos Especiales, 4 Otro.",
    "NACIONALIDAD debe estar entre 1 y 197 y no puede ser 38 Chile.",
    "DV nulo si TIPO_DOCUMENTO es P; DV 0..9/K si TIPO_DOCUMENTO es R.",
    "TIPO_DOCUMENTO debe ser R o P.",
    "JORNADA_INTERCAMBIO admite 1 Diurno, 2 Vespertino, 3 Otro.",
    "SEXO debe ser M Mujer, H Hombre o NB No Binario.",
    "No se permiten espacios iniciales/finales ni dobles espacios en nombres/apellidos.",
]


def official_fields() -> list[dict[str, Any]]:
    regular = [
        ("A", 1, "TIPO_DOCUMENTO", "Tipo de documento de identificacion del estudiante. Puede ser RUN chileno o pasaporte.", "texto", "SI", "P: Pasaporte; R: RUN", "Letra mayuscula", "No usar IPE; R requiere NUM_DOCUMENTO numerico y DV; P requiere DV vacio", "TIPO_DOC", "TIPO_DOCUMENTO", "DISPONIBLE_CON_TRANSFORMACION"),
        ("B", 2, "NUM_DOCUMENTO", "Cuerpo del Rol Unico Nacional o pasaporte que posee el estudiante.", "texto", "SI", "No aplica", "Sin puntos, comas ni guiones", "Si TIPO_DOCUMENTO=R debe ser numerico y no iniciar con 0; pasaporte alfanumerico permitido", "DatosAlumnos/MU", "RUT/N_DOC/NUM_DOCUMENTO", "DISPONIBLE_DIRECTO"),
        ("C", 3, "DV", "Digito verificador del RUN.", "texto", "CONDICIONAL", "0..9, K", "Mayuscula", "Debe ser nulo si TIPO_DOCUMENTO=P; obligatorio y consistente si R", "DatosAlumnos/MU", "DV/DIG", "DISPONIBLE_DIRECTO"),
        ("D", 4, "PRIMER_APELLIDO", "Primer apellido completo del estudiante.", "texto", "SI", "No aplica", "Mayusculas A-Z sin acentos; no abreviar", "Sin espacios inicial/final ni dobles espacios", "DatosAlumnos/MU", "APELLIDO PATERNO/PRIMER_APELLIDO", "DISPONIBLE_CON_TRANSFORMACION"),
        ("E", 5, "SEGUNDO_APELLIDO", "Segundo apellido completo del estudiante.", "texto", "NO", "No aplica", "Mayusculas A-Z sin acentos; no abreviar", "Permite vacio cuando corresponda", "DatosAlumnos/MU", "APELLIDO MATERNO/SEGUNDO_APELLIDO", "DISPONIBLE_CON_TRANSFORMACION"),
        ("F", 6, "NOMBRES", "Todos los nombres completos del estudiante.", "texto", "SI", "No aplica", "Mayusculas A-Z sin acentos; no abreviar", "Sin espacios inicial/final ni dobles espacios", "DatosAlumnos/MU", "NOMBRES/NOMBRE", "DISPONIBLE_CON_TRANSFORMACION"),
        ("G", 7, "SEXO", "Condicion mujer, hombre o no binario.", "texto", "SI", "M: Mujer; H: Hombre; NB: No Binario", "Mayusculas", "Debe estar en catalogo", "DatosAlumnos/MU", "SEXO", "DISPONIBLE_CON_TRANSFORMACION"),
        ("H", 8, "FECHA_NACIMIENTO", "Fecha de nacimiento del estudiante.", "fecha", "SI", "No aplica", "DD-MM-AAAA", "Entre 01-01-1900 y 30-06-2010", "DatosAlumnos/MU", "FECHANACIMIENTO/FECH_NAC", "DISPONIBLE_CON_TRANSFORMACION"),
        ("I", 9, "NACIONALIDAD", "Pais con el cual el estudiante mantiene vinculo juridico de pertenencia.", "entero", "SI", "1..197 segun tabla de paises; no 38 Chile", "Numero entero", "No inferir; estudiantes con nacionalidad chilena no aplican", "gobernanza_nac.tsv/DatosAlumnos", "NACIONALIDAD/NAC", "DISPONIBLE_PARCIAL"),
        ("J", 10, "TIPO_RESIDENCIA_ESTUDIANTE", "Residencia previa en Chile, sin residencia previa o no residente.", "entero", "SI", "1: con residencia previa; 2: sin residencia previa; 3: no reside en Chile", "Numero entero", "No inferir desde domicilio, modalidad online ni nacionalidad", "No detectada", "", "NO_DISPONIBLE"),
        ("K", 11, "PAIS_DE_ORIGEN", "Pais donde residia habitualmente el estudiante sin residencia previa antes de iniciar estudios en Chile, o pais donde reside si no reside en Chile.", "entero", "CONDICIONAL", "1..197; no 38 Chile", "Numero entero", "Completar si TIPO_RESIDENCIA_ESTUDIANTE es 2 o 3; no completar si es 1", "No detectada", "", "NO_DISPONIBLE"),
        ("L", 12, "PAIS_ESTUDIOS_SECUNDARIOS", "Pais donde completo y aprobo la ensenanza secundaria.", "entero", "SI", "1..197", "Numero entero", "No inferir desde nacionalidad ni pais de origen; requiere evidencia academica", "MU/gobernanza_pais_est_sec.tsv/DatosAlumnos", "PAIS_EST_SEC/COMUNACOLEGIO/CIUDADCOLEGIO", "DISPONIBLE_PARCIAL"),
        ("M", 13, "CODIGO_UNICO", "Codigo unico SIES de la carrera o programa.", "texto", "SI", "Codigo oficial SIES oferta 2025 o temporal solicitado", "Codigo SIES/temporal", "No debe estar vacio; si no existe codigo debe solicitarse temporal", "PUENTE_SIES_COMPILADO/MU/oferta", "CODIGO_CARRERA_SIES_FINAL/CODIGO_UNICO", "DISPONIBLE_MEDIANTE_CRUCE"),
        ("N", 14, "ANIO_INGRESO_CARRERA_ACTUAL", "Anio en que ingreso a la carrera actual.", "entero", "SI", "No aplica", "AAAA", "Rango de mensajes: 1950..2025", "DatosAlumnos/MU", "ANOINGRESO/ANIO_ING_ACT", "DISPONIBLE_DIRECTO"),
        ("O", 15, "SEM_INGRESO_CARRERA_ACTUAL", "Semestre del anio en que ingreso a la carrera.", "entero", "SI", "1: Primer semestre; 2: Segundo semestre", "Numero entero", "Debe ser 1 o 2", "DatosAlumnos/MU", "PERIODOINGRESO/SEM_ING_ACT", "DISPONIBLE_DIRECTO"),
        ("P", 16, "ANIO_INGRESO_CARRERA_ORIGEN", "Anio de ingreso al primer anio del plan de estudios de la carrera.", "entero", "SI", "1900 o 1950..2025", "AAAA", "No puede ser mayor que anio actual; 1900 segun corresponda", "MU normalizado", "ANIO_ING_ORI", "DISPONIBLE_MEDIANTE_CRUCE"),
        ("Q", 17, "SEM_INGRESO_CARRERA_ORIGEN", "Semestre en que ingreso a primer anio de la carrera.", "entero", "SI", "0 si anio origen 1900; 1; 2", "Numero entero", "0 solo cuando ANIO_INGRESO_CARRERA_ORIGEN=1900", "MU normalizado", "SEM_ING_ORI", "DISPONIBLE_MEDIANTE_CRUCE"),
        ("R", 18, "NOMBRE_UNIVERSIDAD_ORIGEN", "Nombre oficial de universidad de origen para doble titulacion.", "texto", "CONDICIONAL", "No aplica", "Mayusculas; no abreviar", "Si PAIS_UNIVERSIDAD_ORIGEN tiene informacion, completar este campo", "DatosAlumnos", "NOMBREUNIVERSIDAD", "REQUIERE_CONFIRMACION_INSTITUCIONAL"),
        ("S", 19, "PAIS_UNIVERSIDAD_ORIGEN", "Pais donde se ubica la universidad de origen para doble titulacion.", "entero", "CONDICIONAL", "1..197", "Numero entero", "Si NOMBRE_UNIVERSIDAD_ORIGEN tiene informacion, completar este campo", "No detectada", "", "NO_DISPONIBLE"),
        ("T", 20, "VIGENCIA", "Mantener o eliminar registro de estudiante 2025.", "entero", "SI", "0: Eliminar; 1: Mantener", "Numero entero", "No refiere a vigencia 2026; refiere a mantener/eliminar matricula 2025", "MU normalizado/DatosAlumnos", "VIG/ESTADOACADEMICO/MATRICULA", "DISPONIBLE_MEDIANTE_CRUCE"),
    ]
    intercambio = [
        ("A", 1, "TIPO_DOCUMENTO", "Tipo de documento de identificacion RUN o pasaporte.", "texto", "SI", "P: Pasaporte; R: RUN", "Letra mayuscula", "R requiere NUM_DOCUMENTO numerico y DV; P requiere DV vacio", "No detectada", "", "NO_DISPONIBLE"),
        ("B", 2, "NUM_DOCUMENTO", "Cuerpo del Rol Unico Nacional o pasaporte.", "texto", "SI", "No aplica", "Sin puntos, comas ni guiones", "Obligatorio; R solo numerico", "No detectada", "", "NO_DISPONIBLE"),
        ("C", 3, "DV", "Digito verificador del RUN.", "texto", "CONDICIONAL", "0..9, K", "Mayuscula", "Nulo si TIPO_DOCUMENTO=P", "No detectada", "", "NO_DISPONIBLE"),
        ("D", 4, "PRIMER_APELLIDO", "Primer apellido completo.", "texto", "SI", "No aplica", "Mayusculas sin acentos", "Sin espacios inicial/final ni dobles espacios", "No detectada", "", "NO_DISPONIBLE"),
        ("E", 5, "SEGUNDO_APELLIDO", "Segundo apellido completo.", "texto", "NO", "No aplica", "Mayusculas sin acentos", "Permite vacio cuando corresponda", "No detectada", "", "NO_DISPONIBLE"),
        ("F", 6, "NOMBRES", "Todos los nombres completos.", "texto", "SI", "No aplica", "Mayusculas sin acentos", "Sin espacios inicial/final ni dobles espacios", "No detectada", "", "NO_DISPONIBLE"),
        ("G", 7, "SEXO", "Condicion mujer, hombre o no binario.", "texto", "SI", "M: Mujer; H: Hombre; NB: No Binario", "Mayusculas", "Debe estar en catalogo", "No detectada", "", "NO_DISPONIBLE"),
        ("H", 8, "FECHA_NACIMIENTO", "Fecha de nacimiento.", "fecha", "SI", "No aplica", "DD-MM-AAAA", "Entre 01-01-1900 y 30-06-2010", "No detectada", "", "NO_DISPONIBLE"),
        ("I", 9, "NACIONALIDAD", "Pais con vinculo juridico de pertenencia.", "entero", "SI", "1..197; no 38 Chile", "Numero entero", "No inferir", "No detectada", "", "NO_DISPONIBLE"),
        ("J", 10, "TIPO_RESIDENCIA_ESTUDIANTE", "Residencia previa o sin residencia previa antes del programa de intercambio.", "entero", "SI", "1: con residencia previa; 2: sin residencia previa", "Numero entero", "Mensajes mencionan tambien 0 Sin Informacion; validar con PES antes de carga", "No detectada", "", "NO_DISPONIBLE"),
        ("K", 11, "PAIS_ORIGEN", "Pais de residencia habitual o del cual proviene antes de iniciar estudios.", "entero", "CONDICIONAL", "1..197; no 38 Chile", "Numero entero", "Completar solo para tipo residencia 2 segun mensajes", "No detectada", "", "NO_DISPONIBLE"),
        ("L", 12, "NOMBRE_PROGRAMA", "Denominacion del programa o actividad academica formativa.", "texto", "SI", "No aplica", "Mayusculas; no abreviar", "No debe estar vacio", "No detectada", "", "NO_DISPONIBLE"),
        ("M", 13, "TIPO_PROGRAMA_INTERCAMBIO", "Clasificacion del programa de intercambio.", "entero", "SI", "1: Programa de intercambio; 2: Pasantias medicas; 3: Cursos especiales; 4: Otros", "Numero entero", "Si 4, completar especificacion", "No detectada", "", "NO_DISPONIBLE"),
        ("N", 14, "ESP_TIPO_PROGRAMA_INTERCAMBIO", "Especificacion cuando el tipo de programa es 4 Otros.", "texto", "CONDICIONAL", "No aplica", "Mayusculas; no abreviar", "Obligatorio si tipo programa=4", "No detectada", "", "NO_DISPONIBLE"),
        ("O", 15, "JORNADA_INTERCAMBIO", "Jornada del programa.", "entero", "SI", "1: Diurno; 2: Vespertino; 3: Otro", "Numero entero", "Debe estar en catalogo", "No detectada", "", "NO_DISPONIBLE"),
        ("P", 16, "DURACION_PROGRAMA", "Duracion formal del programa en meses.", "decimal", "SI", "No aplica", "Numero; permite decimales", "Expresar en meses, no semestres", "No detectada", "", "NO_DISPONIBLE"),
        ("Q", 17, "COMUNA_PROGRAMA", "Comuna donde se ubica la sede donde se imparte el programa.", "texto", "SI", "Comuna valida", "Mayusculas; no abreviar", "No debe estar vacio", "No detectada", "", "NO_DISPONIBLE"),
        ("R", 18, "FECHA_INICIO_PROGRAMA", "Fecha de ingreso al programa.", "fecha", "SI", "No aplica", "DD-MM-AAAA", "No posterior a 2025", "No detectada", "", "NO_DISPONIBLE"),
        ("S", 19, "FECHA_TERMINO_PROGRAMA", "Fecha de termino del programa.", "fecha", "NO", "No aplica", "DD-MM-AAAA", "No anterior a fecha de inicio", "No detectada", "", "NO_DISPONIBLE"),
        ("T", 20, "EXISTE_CONVENIO", "Indica si ingreso por convenio previo con institucion extranjera.", "entero", "SI", "1: SI; 2: NO; mensajes aceptan 0 Sin Informacion", "Numero entero", "Si 1, completar universidad/institucion de origen", "No detectada", "", "NO_DISPONIBLE"),
        ("U", 21, "NOMBRE_UNIVERSIDAD_INSTITUCION_ORIGEN", "Nombre oficial de la universidad/institucion de origen asociada al convenio.", "texto", "CONDICIONAL", "No aplica", "Mayusculas; no abreviar", "Completar si EXISTE_CONVENIO=1", "No detectada", "", "NO_DISPONIBLE"),
        ("V", 22, "PAIS_UNIVERSIDAD_INSTITUCION_ORIGEN", "Pais de la universidad/institucion de origen.", "entero", "CONDICIONAL", "1..197", "Numero entero", "Completar en conjunto con nombre de universidad/institucion", "No detectada", "", "NO_DISPONIBLE"),
        ("W", 23, "VIGENCIA", "Mantener o eliminar registro.", "entero", "SI", "0: Eliminar; 1: Mantener", "Numero entero", "Debe estar en catalogo", "No detectada", "", "NO_DISPONIBLE"),
    ]
    rows = []
    for carga, carga_id, source_rows, errors in [
        ("EXTRANJEROS_REGULARES_2026", "16765", regular, REGULAR_ERRORS),
        ("EXTRANJEROS_INTERCAMBIO_2026", "16764", intercambio, INTERCAMBIO_ERRORS),
    ]:
        for col, pos, name, definition, typ, req, codes, fmt, cond, fuente, var, status in source_rows:
            rows.append(
                {
                    "CARGA": carga,
                    "ID_CARGA": carga_id,
                    "COLUMNA": col,
                    "POSICION": pos,
                    "NOMBRE_OFICIAL": name,
                    "DEFINICION": definition,
                    "TIPO": typ,
                    "OBLIGATORIEDAD": req,
                    "CODIGOS_PERMITIDOS": codes,
                    "FORMATO": fmt,
                    "REGLAS_CONDICIONALES": cond,
                    "MENSAJES_ERROR_ASOCIADOS": " | ".join([e for e in errors if name in e or ("PAIS_ORIGEN" in e and name in {"PAIS_DE_ORIGEN", "PAIS_ORIGEN"})]) or "Ver REGLAS_VALIDACION_INSTRUCTIVO.md",
                    "FUENTE_INTERNA_CANDIDATA": fuente,
                    "VARIABLE_INTERNA_CANDIDATA": var,
                    "ESTADO_DISPONIBILIDAD": status,
                    "TRAZA_INSTRUCTIVO": "Anexo I" if carga_id == "16765" else "Anexo II",
                }
            )
    return rows


@dataclass
class DiagnosticData:
    candidates: pd.DataFrame
    confirmed: pd.DataFrame
    normalized_ok: pd.DataFrame
    conflicts: list[dict[str, Any]]
    source_stats: dict[str, Any]


def read_diagnostics_data() -> DiagnosticData:
    candidates = pd.DataFrame()
    normalized_ok = pd.DataFrame()
    conflicts: list[dict[str, Any]] = []
    stats: dict[str, Any] = {}

    da_path = ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"
    if da_path.exists():
        da = pd.read_excel(da_path, sheet_name="DatosAlumnos", dtype=str, engine="openpyxl")
        da.columns = [clean_text(c) for c in da.columns]
        nat_norm = da["NACIONALIDAD"].map(no_accents_upper) if "NACIONALIDAD" in da else ""
        candidates = da[
            da.get("ANOMATRICULA", "").astype(str).str.strip().eq("2025")
            & pd.Series(nat_norm).ne("")
            & ~pd.Series(nat_norm).str.contains("CHIL", na=False)
            & pd.Series(nat_norm).ne("NAN")
        ].copy()
        candidates["NACIONALIDAD_NORM"] = candidates.get("NACIONALIDAD", "").map(no_accents_upper)
        candidates["RUN_CUERPO"] = candidates.get("RUT", "").map(lambda x: split_run(x)[0])
        candidates["DV_NORM"] = candidates.get("RUT", "").map(lambda x: split_run(x)[1])
        candidates["TIPO_DOCUMENTO_CANDIDATO"] = candidates["RUN_CUERPO"].map(lambda x: "R" if x else "")
        candidates["NOMBRE_COMPLETO"] = (
            candidates.get("NOMBRES", "").fillna("").astype(str).str.strip()
            + " "
            + candidates.get("APELLIDO PATERNO", "").fillna("").astype(str).str.strip()
            + " "
            + candidates.get("APELLIDO MATERNO", "").fillna("").astype(str).str.strip()
        ).str.replace(r"\s+", " ", regex=True).str.strip()

    gob_path = ROOT / "gobernanza_nac.tsv"
    if not candidates.empty and gob_path.exists():
        gob = pd.read_csv(gob_path, sep="\t", dtype=str)
        gob["NACIONALIDAD_NORM_JOIN"] = gob["NACIONALIDAD_ORIG"].map(no_accents_upper)
        candidates = candidates.merge(
            gob[["NACIONALIDAD_NORM_JOIN", "COD_NAC", "ESTADO_GOBERNANZA"]],
            how="left",
            left_on="NACIONALIDAD_NORM",
            right_on="NACIONALIDAD_NORM_JOIN",
        )

    # Avance curricular 2025: solo para diagnosticar presencia y conflictos.
    ac_path = ROOT / "resultados" / "matricula_avance_curricular_2025_control.csv"
    if not candidates.empty and ac_path.exists():
        ac = pd.read_csv(ac_path, dtype=str)
        ac["NUM_DOCUMENTO_NORM"] = ac.get("NUM_DOCUMENTO", "").map(normalize_doc)
        ac_codes = ac.groupby("NUM_DOCUMENTO_NORM")["CODIGO_UNICO"].apply(lambda s: sorted({clean_text(x) for x in s if clean_text(x)})).to_dict()
        candidates["AC_CODIGOS_UNICOS"] = candidates["RUN_CUERPO"].map(lambda x: " | ".join(ac_codes.get(x, [])))
        candidates["AC_N_CODIGOS"] = candidates["RUN_CUERPO"].map(lambda x: len(ac_codes.get(x, [])))
        for _, row in candidates[candidates["AC_N_CODIGOS"].fillna(0).astype(int) > 1].iterrows():
            conflicts.append(
                {
                    "TIPO_CONFLICTO": "MULTIPLES_CODIGOS_UNICOS_AVANCE_2025",
                    "CLAVE": row.get("CODCLI", ""),
                    "N_REGISTROS": row.get("AC_N_CODIGOS", ""),
                    "DETALLE": row.get("AC_CODIGOS_UNICOS", ""),
                    "FUENTE": rel(ac_path),
                    "SEVERIDAD": "MEDIA",
                    "OBSERVACION": "No resolver automaticamente; requiere validacion de carrera/programa efectivo 2025.",
                }
            )

    bridge_path = ROOT / "control" / "catalogos" / "PUENTE_SIES_COMPILADO.tsv"
    if not candidates.empty and bridge_path.exists():
        bridge = pd.read_csv(bridge_path, sep="\t", dtype=str)
        grouped = bridge.groupby("CODCARPR").agg(
            CODIGOS=("CODIGO_UNICO_FINAL", lambda s: " | ".join(sorted({clean_text(x) for x in s if clean_text(x)}))),
            STATUS=("RESOLUCION_STATUS", lambda s: " | ".join(sorted({clean_text(x) for x in s if clean_text(x)}))),
        )
        candidates["PUENTE_CODIGOS_SIES"] = candidates.get("CODCARPR", "").map(lambda x: grouped["CODIGOS"].get(x, ""))
        candidates["PUENTE_STATUS"] = candidates.get("CODCARPR", "").map(lambda x: grouped["STATUS"].get(x, "SIN_MATCH"))
        for _, row in candidates[candidates["PUENTE_STATUS"].fillna("").str.contains("AMBIGUO", na=False)].iterrows():
            conflicts.append(
                {
                    "TIPO_CONFLICTO": "CODCARPR_CON_PUENTE_SIES_AMBIGUO",
                    "CLAVE": row.get("CODCLI", ""),
                    "N_REGISTROS": "",
                    "DETALLE": f"CODCARPR={row.get('CODCARPR','')}; codigos={row.get('PUENTE_CODIGOS_SIES','')}",
                    "FUENTE": rel(bridge_path),
                    "SEVERIDAD": "MEDIA",
                    "OBSERVACION": "Usar reglas de oferta/jor/version existentes; no elegir codigo por nombre solamente.",
                }
            )

    if not candidates.empty:
        for label, group_col, value_col in [
            ("CODCLI_ASOCIADO_A_MAS_DE_UN_DOCUMENTO", "CODCLI", "RUN_CUERPO"),
            ("DOCUMENTO_ASOCIADO_A_MAS_DE_UN_CODCLI", "RUN_CUERPO", "CODCLI"),
        ]:
            counts = candidates.groupby(group_col)[value_col].nunique()
            for key, n in counts[counts > 1].items():
                conflicts.append(
                    {
                        "TIPO_CONFLICTO": label,
                        "CLAVE": key,
                        "N_REGISTROS": int(n),
                        "DETALLE": "",
                        "FUENTE": rel(da_path),
                        "SEVERIDAD": "ALTA",
                        "OBSERVACION": "Conflicto identitario; requiere revision manual antes de cualquier carga.",
                    }
                )

    listo_path = ROOT / "resultados" / "archivo_listo_para_sies.xlsx"
    if listo_path.exists():
        usecols = [
            "TIPO_DOC",
            "N_DOC",
            "DV",
            "PRIMER_APELLIDO",
            "SEGUNDO_APELLIDO",
            "NOMBRE",
            "SEXO",
            "FECH_NAC",
            "NAC",
            "PAIS_EST_SEC",
            "CODIGO_CARRERA_SIES_FINAL",
            "ANIO_ING_ACT",
            "SEM_ING_ACT",
            "ANIO_ING_ORI",
            "SEM_ING_ORI",
            "VIG",
            "CODCLI",
            "DA_ANOMATRICULA",
            "INCLUIR_EN_MATRICULA_32",
            "ESTADO_CARGA_PREGRADO",
        ]
        try:
            normalized = pd.read_excel(
                listo_path,
                sheet_name="ARCHIVO_LISTO_SUBIDA",
                dtype=str,
                usecols=lambda c: c in usecols,
                engine="openpyxl",
            )
            normalized_ok = normalized[
                normalized.get("DA_ANOMATRICULA", "").astype(str).str.strip().eq("2025")
                & normalized.get("NAC", "").astype(str).str.strip().ne("38")
                & normalized.get("NAC", "").notna()
                & normalized.get("INCLUIR_EN_MATRICULA_32", "").astype(str).str.upper().eq("SI")
            ].copy()
        except Exception as exc:
            stats["archivo_listo_para_sies_error"] = f"{type(exc).__name__}: {exc}"

    confirmed = candidates[candidates.get("COD_NAC", pd.Series(dtype=str)).notna()].copy() if not candidates.empty else candidates
    if not confirmed.empty:
        confirmed = confirmed[confirmed["COD_NAC"].astype(str).str.strip().ne("38")]

    stats.update(
        {
            "candidatos_datosalumnos_2025_no_chile_o_por_definir": int(len(candidates)),
            "confirmados_extranjeros_mapeables": int(len(confirmed)),
            "nacionalidad_no_mapeada": int(candidates.get("COD_NAC", pd.Series(dtype=str)).isna().sum()) if not candidates.empty else 0,
            "normalizados_ok_carga_pregrado_2025": int(normalized_ok["CODCLI"].nunique()) if not normalized_ok.empty else 0,
            "intercambio_fuentes_detectadas": 0,
        }
    )
    return DiagnosticData(candidates=candidates, confirmed=confirmed, normalized_ok=normalized_ok, conflicts=conflicts, source_stats=stats)


def n_complete(series: pd.Series | None) -> int:
    if series is None:
        return 0
    return int(series.fillna("").astype(str).str.strip().ne("").sum())


def matrix_rows(fields: list[dict[str, Any]], diag: DiagnosticData) -> list[dict[str, Any]]:
    c = diag.candidates
    ok = diag.normalized_ok
    n_total = len(c)
    n_ok = int(ok["CODCLI"].nunique()) if not ok.empty and "CODCLI" in ok else 0
    coverage: dict[str, dict[str, Any]] = {}

    def add(field: str, src: str, hoja: str, var: str, tipo: str, rule: str, key: str, complete: int, conflicts: int, status: str, obs: str, manual: str) -> None:
        coverage[field] = {
            "ARCHIVO_FUENTE_CANDIDATO": src,
            "HOJA": hoja,
            "VARIABLE_ORIGEN": var,
            "TIPO_ORIGEN": tipo,
            "REGLA_TRANSFORMACION": rule,
            "CLAVE_CRUCE": key,
            "N_COMPLETOS": complete,
            "N_NULOS": max(n_total - complete, 0),
            "N_CONFLICTOS": conflicts,
            "ESTADO_MAPEO": status,
            "OBSERVACION": obs,
            "REQUIERE_GESTION_MANUAL": manual,
        }

    if not c.empty:
        add("TIPO_DOCUMENTO", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "RUT", "texto", "Si RUT documental esta presente, proponer R; no usar IPE.", "RUN normalizado", n_complete(c.get("RUN_CUERPO")), 0, "DISPONIBLE_CON_TRANSFORMACION", "Todos los candidatos poseen RUT/RUN en fuente interna; pasaporte no detectado.", "NO")
        add("NUM_DOCUMENTO", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "RUT", "texto", "Eliminar puntos, comas, guion y separar DV.", "RUN normalizado", n_complete(c.get("RUN_CUERPO")), 0, "DISPONIBLE_DIRECTO", "CODCLI no reemplaza NUM_DOCUMENTO.", "NO")
        add("DV", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "RUT", "texto", "Separar DV; vacio solo si tipo P.", "RUN normalizado", n_complete(c.get("DV_NORM")), 0, "DISPONIBLE_CON_TRANSFORMACION", "Validar modulo RUN antes de carga final.", "NO")
        add("PRIMER_APELLIDO", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "APELLIDO PATERNO", "texto", "Mayusculas, sin acentos, trim, dobles espacios.", "CODCLI/RUN", n_complete(c.get("APELLIDO PATERNO")), 0, "DISPONIBLE_CON_TRANSFORMACION", "", "NO")
        add("SEGUNDO_APELLIDO", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "APELLIDO MATERNO", "texto", "Mayusculas, sin acentos, trim, dobles espacios.", "CODCLI/RUN", n_complete(c.get("APELLIDO MATERNO")), 0, "DISPONIBLE_CON_TRANSFORMACION", "Campo no siempre obligatorio, pero existe para candidatos revisados.", "NO")
        add("NOMBRES", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "NOMBRES", "texto", "Mayusculas, sin acentos, trim, dobles espacios.", "CODCLI/RUN", n_complete(c.get("NOMBRES")), 0, "DISPONIBLE_CON_TRANSFORMACION", "", "NO")
        add("SEXO", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "SEXO", "texto", "Mapear sexo institucional a M/H/NB segun instructivo.", "CODCLI/RUN", n_complete(c.get("SEXO")), 0, "DISPONIBLE_CON_TRANSFORMACION", "Verificar semantica M/F de DatosAlumnos antes de carga.", "NO")
        add("FECHA_NACIMIENTO", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "FECHANACIMIENTO", "fecha", "Normalizar a DD-MM-AAAA.", "CODCLI/RUN", n_complete(c.get("FECHANACIMIENTO")), 0, "DISPONIBLE_CON_TRANSFORMACION", "", "NO")
        add("NACIONALIDAD", "gobernanza_nac.tsv + input/PROMEDIOSDEALUMNOS_7804.xlsx", "DatosAlumnos", "NACIONALIDAD -> COD_NAC", "texto/codigo", "Mapeo gobernado; no aceptar Chile=38.", "NACIONALIDAD normalizada", n_complete(c.get("COD_NAC")), int(c.get("COD_NAC", pd.Series(dtype=str)).isna().sum()), "DISPONIBLE_PARCIAL", "Existe un caso con nacionalidad no mapeada/Por definir.", "SI")
        add("TIPO_RESIDENCIA_ESTUDIANTE", "No detectada", "", "", "entero", "Debe levantarse institucionalmente; no inferir.", "CODCLI/RUN", 0, 0, "NO_DISPONIBLE", "Campo critico ausente.", "SI")
        add("PAIS_DE_ORIGEN", "No detectada", "", "", "entero", "Completar solo si residencia 2 o 3; no inferir.", "CODCLI/RUN", 0, 0, "NO_DISPONIBLE", "Campo condicional critico ausente.", "SI")
        add("PAIS_ESTUDIOS_SECUNDARIOS", "resultados/archivo_listo_para_sies.xlsx + gobernanza_pais_est_sec.tsv", "ARCHIVO_LISTO_SUBIDA", "PAIS_EST_SEC", "entero", "Reutilizable solo si se confirma que corresponde al pais donde completo secundaria.", "CODCLI/RUN", n_ok, n_total - n_ok, "DISPONIBLE_PARCIAL", "La cobertura normalizada existe para 16 OK; requiere confirmacion porque no debe inferirse desde nacionalidad/origen.", "SI")
        add("CODIGO_UNICO", "control/catalogos/PUENTE_SIES_COMPILADO.tsv + resultados/archivo_listo_para_sies.xlsx", "ARCHIVO_LISTO_SUBIDA", "CODIGO_CARRERA_SIES_FINAL/CODIGO_UNICO_FINAL", "texto", "Cruzar por CODCARPR, jornada, modalidad, version y oferta; no elegir por nombre solo.", "CODCARPR+JORNADA+VERSION", n_ok, sum(1 for x in diag.conflicts if x["TIPO_CONFLICTO"].startswith("CODCARPR")), "DISPONIBLE_MEDIANTE_CRUCE", "Hay codigos ambiguos en puente para varios CODCARPR.", "SI")
        add("ANIO_INGRESO_CARRERA_ACTUAL", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "ANOINGRESO", "entero", "Formato AAAA; validar rango instructivo.", "CODCLI", n_complete(c.get("ANOINGRESO")), 0, "DISPONIBLE_DIRECTO", "", "NO")
        add("SEM_INGRESO_CARRERA_ACTUAL", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "PERIODOINGRESO", "entero", "Mapear a 1/2.", "CODCLI", n_complete(c.get("PERIODOINGRESO")), 0, "DISPONIBLE_DIRECTO", "", "NO")
        add("ANIO_INGRESO_CARRERA_ORIGEN", "resultados/archivo_listo_para_sies.xlsx", "ARCHIVO_LISTO_SUBIDA", "ANIO_ING_ORI", "entero", "Reutilizar motor MU; validar reglas 1900 y no mayor que actual.", "CODCLI", n_ok, 0, "DISPONIBLE_MEDIANTE_CRUCE", "Disponible en normalizacion MU para 16 OK; no recalcular aqui.", "SI")
        add("SEM_INGRESO_CARRERA_ORIGEN", "resultados/archivo_listo_para_sies.xlsx", "ARCHIVO_LISTO_SUBIDA", "SEM_ING_ORI", "entero", "Reutilizar motor MU; validar 0 solo si anio origen=1900.", "CODCLI", n_ok, 0, "DISPONIBLE_MEDIANTE_CRUCE", "Disponible en normalizacion MU para 16 OK; no recalcular aqui.", "SI")
        add("NOMBRE_UNIVERSIDAD_ORIGEN", rel(ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"), "DatosAlumnos", "NOMBREUNIVERSIDAD", "texto", "Solo doble titulacion; confirmar aplicabilidad.", "CODCLI", n_complete(c.get("NOMBREUNIVERSIDAD")), 0, "REQUIERE_CONFIRMACION_INSTITUCIONAL", "En DatosAlumnos parece institucion anterior, no necesariamente doble titulacion.", "SI")
        add("PAIS_UNIVERSIDAD_ORIGEN", "No detectada", "", "", "entero", "Completar solo si hay universidad de origen para doble titulacion.", "CODCLI", 0, 0, "NO_DISPONIBLE", "", "SI")
        add("VIGENCIA", "resultados/archivo_listo_para_sies.xlsx", "ARCHIVO_LISTO_SUBIDA", "VIG", "entero", "Reutilizar VIG normalizado solo como candidato; confirmar mantener/eliminar 2025.", "CODCLI", n_ok, 0, "DISPONIBLE_MEDIANTE_CRUCE", "VIG del instructivo EE no es vigencia 2026.", "SI")

    rows: list[dict[str, Any]] = []
    for field in fields:
        carga = field["CARGA"]
        campo = field["NOMBRE_OFICIAL"]
        base = coverage.get(campo, {}) if carga == "EXTRANJEROS_REGULARES_2026" else {}
        if carga == "EXTRANJEROS_INTERCAMBIO_2026":
            base = {
                "ARCHIVO_FUENTE_CANDIDATO": "No se detecto fuente de intercambio/movilidad en el repositorio",
                "HOJA": "",
                "VARIABLE_ORIGEN": "",
                "TIPO_ORIGEN": "",
                "REGLA_TRANSFORMACION": "Pendiente de fuente institucional; no inferir desde matricula regular.",
                "CLAVE_CRUCE": "Documento normalizado; CODCLI solo si existe tabla maestra",
                "N_COMPLETOS": 0,
                "N_NULOS": 0,
                "N_CONFLICTOS": 0,
                "ESTADO_MAPEO": "NO_DISPONIBLE",
                "OBSERVACION": "Universo de intercambio no detectado en esta ejecucion.",
                "REQUIERE_GESTION_MANUAL": "SI",
            }
        complete = int(base.get("N_COMPLETOS", 0) or 0)
        nulls = int(base.get("N_NULOS", 0) or 0)
        denom = complete + nulls
        rows.append(
            {
                "CARGA": carga,
                "ID_CARGA": field["ID_CARGA"],
                "CAMPO_OFICIAL": campo,
                "DEFINICION_OFICIAL": field["DEFINICION"],
                "OBLIGATORIO": field["OBLIGATORIEDAD"],
                "ARCHIVO_FUENTE_CANDIDATO": base.get("ARCHIVO_FUENTE_CANDIDATO", ""),
                "HOJA": base.get("HOJA", ""),
                "VARIABLE_ORIGEN": base.get("VARIABLE_ORIGEN", ""),
                "TIPO_ORIGEN": base.get("TIPO_ORIGEN", ""),
                "REGLA_TRANSFORMACION": base.get("REGLA_TRANSFORMACION", ""),
                "CLAVE_CRUCE": base.get("CLAVE_CRUCE", ""),
                "COBERTURA": f"{(complete / denom * 100):.1f}%" if denom else "NA",
                "N_COMPLETOS": complete,
                "N_NULOS": nulls,
                "N_CONFLICTOS": base.get("N_CONFLICTOS", 0),
                "ESTADO_MAPEO": base.get("ESTADO_MAPEO", field["ESTADO_DISPONIBILIDAD"]),
                "OBSERVACION": base.get("OBSERVACION", ""),
                "REQUIERE_GESTION_MANUAL": base.get("REQUIERE_GESTION_MANUAL", "SI"),
            }
        )
    return rows


def critical_gaps(diag: DiagnosticData) -> list[dict[str, Any]]:
    total = int(len(diag.candidates))
    mapped_nat = int(diag.candidates.get("COD_NAC", pd.Series(dtype=str)).notna().sum()) if total else 0
    n_ok = int(diag.normalized_ok["CODCLI"].nunique()) if not diag.normalized_ok.empty and "CODCLI" in diag.normalized_ok else 0
    rows = [
        ("NUM_DOCUMENTO", total, total, 0, "DISPONIBLE_DIRECTO", "Disponible desde RUT en DatosAlumnos; no reemplazar por CODCLI."),
        ("NACIONALIDAD", mapped_nat, total, total - mapped_nat, "DISPONIBLE_PARCIAL", "Un caso Por definir/no mapeado requiere gestion."),
        ("TIPO_RESIDENCIA_ESTUDIANTE", 0, total, total, "NO_DISPONIBLE", "No inferir desde domicilio, modalidad ni nacionalidad."),
        ("PAIS_DE_ORIGEN", 0, total, total, "NO_DISPONIBLE", "Condicional a residencia 2/3; no inferir desde nacionalidad."),
        ("PAIS_ESTUDIOS_SECUNDARIOS", n_ok, total, total - n_ok, "DISPONIBLE_PARCIAL", "Existe candidato normalizado para 16 OK; requiere confirmacion de pais donde completo secundaria."),
    ]
    return [
        {
            "CAMPO_CRITICO": name,
            "N_COMPLETOS_CANDIDATO": complete,
            "N_TOTAL_CANDIDATOS": denom,
            "COBERTURA": f"{complete / denom * 100:.1f}%" if denom else "NA",
            "N_REQUIERE_GESTION": manual,
            "ESTADO": status,
            "OBSERVACION": obs,
        }
        for name, complete, denom, manual, status, obs in rows
    ]


def manual_nomina(diag: DiagnosticData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if diag.candidates.empty:
        return rows
    for _, r in diag.candidates.iterrows():
        base = {
            "CODCLI": r.get("CODCLI", ""),
            "TIPO_DOCUMENTO": r.get("TIPO_DOCUMENTO_CANDIDATO", ""),
            "NUM_DOCUMENTO_DISPONIBLE": r.get("RUN_CUERPO", ""),
            "NOMBRE_COMPLETO": r.get("NOMBRE_COMPLETO", ""),
            "CARRERA": r.get("NOMBRE_L", ""),
            "SEDE": r.get("SEDE", ""),
            "FUENTE_REVISADA": "input/PROMEDIOSDEALUMNOS_7804.xlsx::DatosAlumnos; gobernanza_nac.tsv; resultados/archivo_listo_para_sies.xlsx",
        }
        checks = [
            ("TIPO_RESIDENCIA_ESTUDIANTE", "Campo critico no disponible en fuentes revisadas.", "Levantar con Docencia/Registro Academico; no inferir."),
            ("PAIS_DE_ORIGEN", "Campo condicional no disponible; depende de residencia 2 o 3.", "Completar solo si residencia es 2 o 3; no usar nacionalidad."),
            ("PAIS_ESTUDIOS_SECUNDARIOS", "Debe confirmar pais donde completo y aprobo secundaria.", "No inferir desde nacionalidad ni pais de origen; validar evidencia academica."),
        ]
        if not clean_text(r.get("COD_NAC", "")):
            checks.append(("NACIONALIDAD", "Nacionalidad no mapeada a codigo oficial.", f"Valor fuente: {r.get('NACIONALIDAD','')}"))
        if clean_text(r.get("PUENTE_STATUS", "")).find("AMBIGUO") >= 0:
            checks.append(("CODIGO_UNICO", "Puente SIES presenta ambiguedad para CODCARPR.", f"CODCARPR={r.get('CODCARPR','')}; codigos={r.get('PUENTE_CODIGOS_SIES','')}"))
        for field, motivo, obs in checks:
            row = dict(base)
            row.update({"CAMPO_FALTANTE": field, "MOTIVO": motivo, "OBSERVACION": obs})
            rows.append(row)
    return rows


def instructivo_location_rows() -> list[dict[str, Any]]:
    rows = []
    for label, path in [("ORIGINAL", INSTRUCTIVO_ORIGINAL), ("COPIA_DOCUMENTAL", INSTRUCTIVO_COPIA)]:
        if not path.exists():
            continue
        stat = path.stat()
        rows.append(
            {
                "TIPO": label,
                "RUTA_ABSOLUTA": str(path.resolve()),
                "NOMBRE": path.name,
                "TAMANO_BYTES": stat.st_size,
                "FECHA_MODIFICACION": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "SHA256": sha256(path),
                "LINEAS_TEXTO": line_count(path),
                "LINEAS_WC": newline_count(path),
                "CODIFICACION_DETECTADA": detect_encoding(path),
            }
        )
    return rows


def validation_rules_md() -> str:
    regular = "\n".join(f"- {x}" for x in REGULAR_ERRORS)
    intercambio = "\n".join(f"- {x}" for x in INTERCAMBIO_ERRORS)
    return f"""# Reglas de Validacion Trazadas al Instructivo

Fuente documental: `{rel(INSTRUCTIVO_COPIA)}`.

## Extranjeros Regulares 2026 - ID 16765

{regular}

Reglas de no inferencia aplicadas en esta fase:

- No asumir nacionalidad = pais de origen.
- No asumir pais de origen = pais de estudios secundarios.
- No asumir pais de emision de pasaporte = nacionalidad.
- No asumir que nacionalidad extranjera implica ausencia de RUN.
- No usar domicilio actual para determinar tipo de residencia.
- No usar modalidad online para inferir residencia o no residencia en Chile.
- No usar IPE como tipo de documento.

## Extranjeros de Intercambio 2026 - ID 16764

{intercambio}

## Estrategia jerarquica propuesta de cruce

1. Identificador documental exacto normalizado: tipo documento, cuerpo del RUN/pasaporte y DV cuando corresponda.
2. CODCLI mediante tabla maestra de equivalencias; CODCLI no reemplaza NUM_DOCUMENTO.
3. Identificador institucional estable cuando exista en una fuente maestra.
4. Combinacion controlada de nombres y fecha de nacimiento solo para diagnostico, nunca para completar automaticamente sin validacion.

## Normalizaciones minimas

- Eliminar puntos, comas y guiones donde corresponda.
- Convertir a mayusculas.
- Limpiar espacios iniciales/finales y dobles espacios.
- Separar cuerpo RUN y DV.
- Conservar pasaporte como alfanumerico.
- DV vacio cuando TIPO_DOCUMENTO=P.
- Controlar caracteres validos.
"""


def readme_md(diag: DiagnosticData) -> str:
    return f"""# Estudiantes Extranjeros SIES 2026

Subproducto para organizar y diagnosticar la entrega **Estudiantes Extranjeros SIES 2026**, correspondiente a estudiantes con nacionalidad extranjera matriculados o con actividad academica entre el **1 de enero y el 31 de diciembre de 2025**.

## Objetivo

Integrar el proceso al repositorio existente sin crear una linea paralela de trabajo, reutilizando la gobernanza de Matricula Unificada, fuentes de estudiantes, oferta academica, puente SIES y auditorias ya disponibles.

## Entregas normativas

- Extranjeros Regulares 2026, ID de carga 16765: estudiantes extranjeros regulares en programas conducentes o certificables de pregrado, postgrado o postitulo.
- Extranjeros de Intercambio 2026, ID de carga 16764: estudiantes extranjeros en programas o actividades formativas de corta duracion, presenciales en Chile, no orientadas a titulo o grado institucional.

## Alcance de esta ejecucion

Esta fase no genera CSV definitivo para PES. Solo crea diagnostico, inventario, diccionario oficial, matriz de mapeo, brechas, reglas y nominas de gestion.

## Fuentes candidatas detectadas

- `input/PROMEDIOSDEALUMNOS_7804.xlsx`, hoja `DatosAlumnos`: CODCLI, RUT, nombres, sexo, fecha de nacimiento, nacionalidad, carrera, sede, jornada, anio/periodo de matricula e ingreso.
- `resultados/archivo_listo_para_sies.xlsx`, hoja `ARCHIVO_LISTO_SUBIDA`: campos MU normalizados, CODCLI, trazas y codigo SIES final para parte del universo.
- `gobernanza_columnas_mu/`: definiciones y reglas ya documentadas para TIPO_DOC, N_DOC, DV, nombres, sexo, FECH_NAC, NAC, PAIS_EST_SEC, ingreso y VIG.
- `gobernanza_nac.tsv` y `gobernanza_pais_est_sec.tsv`: catalogos de normalizacion existentes.
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`: puente de CODCARPR/oferta a codigo unico SIES.
- `indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.*`: oferta/diccionario reutilizable como contraste de programas.

## Claves de cruce propuestas

1. Documento oficial normalizado: tipo documento, NUM_DOCUMENTO y DV.
2. CODCLI mediante equivalencia maestra, sin reemplazar NUM_DOCUMENTO.
3. CODCARPR + jornada + modalidad + version para CODIGO_UNICO.
4. Nombres + fecha de nacimiento solo para diagnostico y nunca para completar automaticamente.

## Campos criticos

No se deben inferir `NACIONALIDAD`, `TIPO_RESIDENCIA_ESTUDIANTE`, `PAIS_DE_ORIGEN` ni `PAIS_ESTUDIOS_SECUNDARIOS`. En esta ejecucion se detectaron {diag.source_stats.get("confirmados_extranjeros_mapeables", 0)} extranjeros confirmados por nacionalidad mapeable y {diag.source_stats.get("nacionalidad_no_mapeada", 0)} caso con nacionalidad no mapeada/por definir.

## Flujo propuesto

1. Validar universo 2025 regular con Docencia/Registro Academico.
2. Obtener fuente institucional de intercambio 2025 si existe.
3. Resolver campos criticos de residencia, origen y estudios secundarios.
4. Confirmar CODIGO_UNICO con puente SIES/oferta y resolver ambiguedades.
5. Ejecutar transformaciones en script separado, con auditoria y sin sobrescribir entregas previas.

## Riesgos

- Ausencia de fuente de intercambio.
- `TIPO_RESIDENCIA_ESTUDIANTE` no existe en fuentes revisadas.
- `PAIS_DE_ORIGEN` es condicional y no debe inferirse.
- `PAIS_ESTUDIOS_SECUNDARIOS` requiere evidencia de secundaria completada, no solo localidad o nacionalidad.
- Hay ambiguedades de codigo unico en puente SIES para algunos programas.
- Una nacionalidad aparece como `Por definir`.
"""


def diagnostic_report_md(diag: DiagnosticData, inventory_rows: list[dict[str, Any]], matrix: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> str:
    inv_count = len(inventory_rows)
    type_counts = Counter(r["tipo"] for r in inventory_rows)
    high_reuse = [r for r in inventory_rows if r["posibilidad_reutilizacion"] == "ALTA"][:20]
    high_list = "\n".join(f"- `{r['ruta_relativa']}`: {r['variables_utiles']}" for r in high_reuse) or "- No detectado"
    conflict_summary = Counter(r["TIPO_CONFLICTO"] for r in diag.conflicts)
    conflicts = "\n".join(f"- {k}: {v}" for k, v in conflict_summary.items()) or "- Sin conflictos identitarios duros en candidatos; si hay ambiguedades de codigo SIES."
    gap_lines = "\n".join(f"- {g['CAMPO_CRITICO']}: {g['COBERTURA']} ({g['ESTADO']})" for g in gaps)
    cobertura_oficial = "\n".join(
        f"- {r['CAMPO_OFICIAL']} ({r['CARGA']}): {r['COBERTURA']} - {r['ESTADO_MAPEO']}"
        for r in matrix
        if r["CARGA"] == "EXTRANJEROS_REGULARES_2026"
    )
    return f"""# Reporte Diagnostico Inicial

Fecha de ejecucion: {RUN_TS}

## Localizacion del instructivo

- Original: `{rel(INSTRUCTIVO_ORIGINAL)}`
- Copia documental estable: `{rel(INSTRUCTIVO_COPIA)}`
- SHA-256 original/copia: `{sha256(INSTRUCTIVO_ORIGINAL)}` / `{sha256(INSTRUCTIVO_COPIA)}`
- Codificacion detectada: {detect_encoding(INSTRUCTIVO_ORIGINAL)}
- Lineas: {line_count(INSTRUCTIVO_ORIGINAL)}

## Diagnostico del repositorio

Se inventariaron {inv_count} archivos relevantes fuera del nuevo subproducto. Distribucion por tipo:

{json.dumps(type_counts, ensure_ascii=False, indent=2)}

Fuentes de alta reutilizacion detectadas:

{high_list}

## Universo inicial

- Candidatos 2025 no Chile o por definir desde `DatosAlumnos`: {diag.source_stats.get("candidatos_datosalumnos_2025_no_chile_o_por_definir", 0)}
- Confirmados extranjeros con nacionalidad mapeable: {diag.source_stats.get("confirmados_extranjeros_mapeables", 0)}
- Casos con nacionalidad no mapeada/por definir: {diag.source_stats.get("nacionalidad_no_mapeada", 0)}
- Registros/codcli ya normalizados como OK en `archivo_listo_para_sies.xlsx`: {diag.source_stats.get("normalizados_ok_carga_pregrado_2025", 0)}
- Fuentes de intercambio detectadas: {diag.source_stats.get("intercambio_fuentes_detectadas", 0)}

## Cobertura por variable oficial regular

{cobertura_oficial}

## Brechas criticas

{gap_lines}

## Conflictos detectados

{conflicts}

## Propuesta de cruce

1. Documento exacto normalizado.
2. CODCLI solo como llave interna mediante equivalencias trazables.
3. CODCARPR + jornada + modalidad + version para obtener CODIGO_UNICO con puente SIES/oferta.
4. Nombre y fecha de nacimiento solo para diagnostico.

## Campos que requieren gestion institucional

- TIPO_RESIDENCIA_ESTUDIANTE: ausente para todos los candidatos.
- PAIS_DE_ORIGEN: condicional a residencia 2/3; no disponible.
- PAIS_ESTUDIOS_SECUNDARIOS: requiere confirmacion de secundaria completada.
- NACIONALIDAD: un caso `Por definir`.
- CODIGO_UNICO: resolver ambiguedades de puente antes de carga.

## Siguiente fase recomendada

Levantar con Docencia/Registro Academico una planilla de resolucion de campos criticos para los candidatos 2025, confirmar si existe universo de intercambio 2025 y luego implementar transformaciones en un script separado con pruebas y auditoria.
"""


def control_cambios_rows(created_paths: list[Path]) -> list[dict[str, Any]]:
    rows = [
        {
            "FECHA_HORA": RUN_TS,
            "ARCHIVO_MODIFICADO": "",
            "TIPO_CAMBIO": "SIN_MODIFICACION_EXISTENTE",
            "MOTIVO": "Esta ejecucion no modifico archivos existentes; solo creo estructura nueva y copio instructivo.",
            "LINEAS_O_SECCIONES_CAMBIADAS": "",
            "HASH_ORIGINAL": "",
            "HASH_POSTERIOR": "",
            "RESPALDO": "No aplica",
        }
    ]
    for path in created_paths:
        if path.exists():
            rows.append(
                {
                    "FECHA_HORA": RUN_TS,
                    "ARCHIVO_MODIFICADO": rel(path),
                    "TIPO_CAMBIO": "CREACION_ARTEFACTO",
                    "MOTIVO": "Artefacto de diagnostico inicial del subproducto.",
                    "LINEAS_O_SECCIONES_CAMBIADAS": "archivo completo",
                    "HASH_ORIGINAL": "",
                    "HASH_POSTERIOR": sha256(path),
                    "RESPALDO": "No aplica; archivo nuevo",
                }
            )
    return rows


def manifest_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        rows.append(
            {
                "RUTA_RELATIVA": rel(path),
                "NOMBRE": path.name,
                "TIPO": classify_file(path),
                "TAMANO_BYTES": path.stat().st_size,
                "SHA256": sha256(path),
                "FECHA_GENERACION_O_COPIA": RUN_TS,
                "ORIGEN": "copia instructivo original" if path == INSTRUCTIVO_COPIA else "generado por diagnostico inicial",
                "OBSERVACION": "No es archivo de carga PES" if "archivos_subida" not in rel(path) else "",
            }
        )
    return rows


def main() -> int:
    ensure_dirs()
    if not INSTRUCTIVO_ORIGINAL.exists():
        print(f"No se encontro el instructivo esperado: {INSTRUCTIVO_ORIGINAL}", file=sys.stderr)
        return 2
    if not INSTRUCTIVO_COPIA.exists() or sha256(INSTRUCTIVO_COPIA) != sha256(INSTRUCTIVO_ORIGINAL):
        shutil.copy2(INSTRUCTIVO_ORIGINAL, INSTRUCTIVO_COPIA)

    fields = official_fields()
    diag = read_diagnostics_data()
    inventory = inventory_repo()
    matrix = matrix_rows(fields, diag)
    gaps = critical_gaps(diag)
    manual = manual_nomina(diag)

    created: list[Path] = [SCRIPT_PATH]

    path = DOCS / "DICCIONARIO_VARIABLES_OFICIALES.csv"
    write_csv(
        path,
        fields,
        [
            "CARGA",
            "ID_CARGA",
            "COLUMNA",
            "POSICION",
            "NOMBRE_OFICIAL",
            "DEFINICION",
            "TIPO",
            "OBLIGATORIEDAD",
            "CODIGOS_PERMITIDOS",
            "FORMATO",
            "REGLAS_CONDICIONALES",
            "MENSAJES_ERROR_ASOCIADOS",
            "FUENTE_INTERNA_CANDIDATA",
            "VARIABLE_INTERNA_CANDIDATA",
            "ESTADO_DISPONIBILIDAD",
            "TRAZA_INSTRUCTIVO",
        ],
    )
    created.append(path)

    path = AUDITORIAS / "INVENTARIO_FUENTES_EXISTENTES.csv"
    write_csv(
        path,
        inventory,
        [
            "archivo",
            "ubicacion",
            "ruta_relativa",
            "tipo",
            "periodo",
            "nivel_datos",
            "identificador_disponible",
            "variables_utiles",
            "posibilidad_reutilizacion",
            "riesgo_duplicacion",
            "observaciones",
            "tamano_bytes",
            "fecha_modificacion",
            "filas_detectadas",
            "columnas_detectadas",
            "delimitador",
            "hojas_excel",
            "encabezados_muestra",
        ],
    )
    created.append(path)

    path = AUDITORIAS / "MATRIZ_MAPEO_INICIAL.csv"
    write_csv(
        path,
        matrix,
        [
            "CARGA",
            "ID_CARGA",
            "CAMPO_OFICIAL",
            "DEFINICION_OFICIAL",
            "OBLIGATORIO",
            "ARCHIVO_FUENTE_CANDIDATO",
            "HOJA",
            "VARIABLE_ORIGEN",
            "TIPO_ORIGEN",
            "REGLA_TRANSFORMACION",
            "CLAVE_CRUCE",
            "COBERTURA",
            "N_COMPLETOS",
            "N_NULOS",
            "N_CONFLICTOS",
            "ESTADO_MAPEO",
            "OBSERVACION",
            "REQUIERE_GESTION_MANUAL",
        ],
    )
    created.append(path)

    path = REPORTES / "REPORTE_DIAGNOSTICO_INICIAL.md"
    write_text(path, diagnostic_report_md(diag, inventory, matrix, gaps))
    created.append(path)

    path = AUDITORIAS / "BRECHAS_DATOS_CRITICOS.csv"
    write_csv(path, gaps, ["CAMPO_CRITICO", "N_COMPLETOS_CANDIDATO", "N_TOTAL_CANDIDATOS", "COBERTURA", "N_REQUIERE_GESTION", "ESTADO", "OBSERVACION"])
    created.append(path)

    path = DOCS / "REGLAS_VALIDACION_INSTRUCTIVO.md"
    write_text(path, validation_rules_md())
    created.append(path)

    path = AUDITORIAS / "NOMINA_GESTION_MANUAL.csv"
    write_csv(
        path,
        manual,
        ["CODCLI", "TIPO_DOCUMENTO", "NUM_DOCUMENTO_DISPONIBLE", "NOMBRE_COMPLETO", "CARRERA", "SEDE", "CAMPO_FALTANTE", "MOTIVO", "FUENTE_REVISADA", "OBSERVACION"],
    )
    created.append(path)

    path = AUDITORIAS / "CONFLICTOS_IDENTIFICADORES_Y_CRUCES.csv"
    write_csv(path, diag.conflicts, ["TIPO_CONFLICTO", "CLAVE", "N_REGISTROS", "DETALLE", "FUENTE", "SEVERIDAD", "OBSERVACION"])
    created.append(path)

    path = AUDITORIAS / "INSTRUCTIVO_LOCALIZACION.csv"
    write_csv(path, instructivo_location_rows(), ["TIPO", "RUTA_ABSOLUTA", "NOMBRE", "TAMANO_BYTES", "FECHA_MODIFICACION", "SHA256", "LINEAS_TEXTO", "LINEAS_WC", "CODIFICACION_DETECTADA"])
    created.append(path)

    path = SUB / "README.md"
    write_text(path, readme_md(diag))
    created.append(path)

    path = AUDITORIAS / "CONTROL_CAMBIOS.csv"
    # CONTROL_CAMBIOS depends on all previous hashes.
    write_csv(
        path,
        control_cambios_rows([INSTRUCTIVO_COPIA] + created),
        ["FECHA_HORA", "ARCHIVO_MODIFICADO", "TIPO_CAMBIO", "MOTIVO", "LINEAS_O_SECCIONES_CAMBIADAS", "HASH_ORIGINAL", "HASH_POSTERIOR", "RESPALDO"],
    )
    created.append(path)

    path = AUDITORIAS / "MANIFIESTO_ARCHIVOS.csv"
    write_csv(
        path,
        manifest_rows([INSTRUCTIVO_COPIA] + created),
        ["RUTA_RELATIVA", "NOMBRE", "TIPO", "TAMANO_BYTES", "SHA256", "FECHA_GENERACION_O_COPIA", "ORIGEN", "OBSERVACION"],
    )
    created.append(path)

    print(json.dumps(diag.source_stats, ensure_ascii=False, indent=2))
    print(f"Artefactos creados: {len(created)}")
    for p in created:
        print(rel(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
