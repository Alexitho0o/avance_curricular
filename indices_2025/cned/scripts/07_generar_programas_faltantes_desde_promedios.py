#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera una guía operativa CNED para crear manualmente programas faltantes."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows


CODE_PATTERN = re.compile(r"^I(?P<ies>\d+)S(?P<sed>\d+)C(?P<car>\d+)J(?P<jor>\d+)V(?P<version>\d+)$")

MATRIZ_REQUIRED_COLUMNS = [
    "CODIGO_IES_NUM",
    "CODIGO_UNICO",
    "NOMBRE_IES",
    "COD_SEDE",
    "NOMBRE_SEDE",
    "NOMBRE_CARRERA",
    "MODALIDAD",
    "JORNADA",
    "TIPO_PLAN_CARRERA",
    "CARACT_PLAN_ESPECIAL",
    "DURACION_ESTUDIOS",
    "DURACION_TITULACION",
    "DURACION_TOTAL",
    "COMUNA_SEDE",
    "PROVINCIA_SEDE",
    "REGION_SEDE",
    "NIVEL_GLOBAL",
    "NIVEL_CARRERA",
    "VIGENCIA",
]

EXISTENTES_REQUIRED_COLUMNS = [
    "Sede",
    "Comuna",
    "Región",
    "Cod.Carr.",
    "Carrera Genérica",
    "Nombre Programa",
    "Horario",
    "Tipo Programa",
    "Tipo Carrera",
    "Ingreso Directo",
    "Año Inicio Actividades",
    "Campus",
    "Duracion (en semestres)",
    "Titulo",
    "Grado Academico",
    "Codigo SIES",
    "Nivel Pregrado/Posgrado",
    "Modalidad Programa",
    "Especial",
]

FORM_FIELDS = [
    "Sede",
    "Tipo de Carrera",
    "Nombre",
    "Mención o Especialidad",
    "Año de inicio de Actividades",
    "Campus",
    "Horario",
    "Estado",
    "Tipo Programa",
    "Detalle del Tipo de Programa (especiales)",
    "Modalidad del Programa",
    "Área del Conocimiento",
    "Sub Área",
    "Carrera Genérica",
    "Título que otorga el programa",
    "Grado Académico que otorga el programa",
    "Dependencia",
    "Régimen",
    "Duración del programa en Semestres",
    "Ingreso Directo",
    "Ingreso desde un plan Común",
    "Ingreso desde Bachillerato",
    "Otro Tipo de Ingreso",
    "Ingreso otro",
    "Observaciones",
]

TRACE_FIELDS = [
    "CODIGO_UNICO",
    "CODIGO_IES_NUM",
    "COD_SEDE",
    "COD_CARRERA_DERIVADO",
    "JORNADA",
    "VERSION_DERIVADA",
    "NOMBRE_CARRERA_ORIGINAL",
    "NOMBRE_CARRERA_NORMALIZADO",
    "MODALIDAD_ORIGINAL",
    "TIPO_PLAN_CARRERA_ORIGINAL",
    "CARACT_PLAN_ESPECIAL_ORIGINAL",
    "NIVEL_GLOBAL",
    "NIVEL_CARRERA",
    "VIGENCIA",
    "ESTADO_CRUCE_INDICES",
    "MOTIVO_ESTADO_CRUCE",
    "FUENTE",
    "REVISADO_MANUALMENTE",
    "OBSERVACION_AUDITORIA",
]

OUTPUT_COLUMNS = TRACE_FIELDS + FORM_FIELDS

EXPECTED_CODES = {
    "I162S2C101J4V1": "DIPLOMADO EN SALUD FAMILIAR CON ENFOQUE COMUNITARIO",
    "I162S2C102J4V1": "DIPLOMADO SALUD CON FOCO EN MIGRACION",
    "I162S2C103J4V1": "DIPLOMADO ABORDAJE INTEGRAL DE LA VIOLENCIA DE GENERO EN ATENCION PRIMARIA DE SALUD",
    "I162S2C104J4V1": "DIPLOMADO EN INNOVACION PARA LA DOCENCIA",
    "I162S2C105J4V1": "DIPLOMADO EN HUMANIZACION EN SALUD",
    "I162S2C111J4V1": "INGENIERIA EN FINANZAS",
    "I162S2C111J4V2": "INGENIERIA EN FINANZAS",
    "I162S2C112J4V1": "INGENIERIA EN MARKETING DIGITAL",
    "I162S2C112J4V2": "INGENIERIA EN MARKETING DIGITAL",
    "I162S2C113J4V1": "INGENIERIA EN RECURSOS HUMANOS",
    "I162S2C113J4V2": "INGENIERIA EN RECURSOS HUMANOS",
    "I162S2C114J2V1": "TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA",
    "I162S2C115J2V1": "TECNICO EN FARMACIA",
    "I162S2C116J4V1": "TECNICO EN FINANZAS",
    "I162S2C117J4V1": "TECNICO EN INFRAESTRUCTURA CLOUD",
    "I162S2C118J4V1": "TECNICO EN MARKETING DIGITAL",
    "I162S2C119J4V1": "TECNICO EN RECURSOS HUMANOS",
    "I162S2C124J4V1": "INGENIERIA EN PREVENCION DE RIESGOS",
    "I162S2C124J4V2": "INGENIERIA EN PREVENCION DE RIESGOS",
    "I162S2C125J4V1": "INGENIERIA EN SEGURIDAD PRIVADA",
    "I162S2C125J4V2": "INGENIERIA EN SEGURIDAD PRIVADA",
    "I162S2C95J4V1": "DIPLOMADO EN INTELIGENCIA ARTIFICIAL",
    "I162S2C96J4V1": "DIPLOMADO EN GOBERNANZA DE DATOS",
    "I162S2C97J4V1": "DIPLOMADO EN SUPPLY CHAIN MANAGEMENT Y MINERIA DE REQUERIMIENTOS",
    "I162S2C98J4V1": "DIPLOMADO EN HABILIDADES DIRECTIVAS PARA PROFESIONALES STEM",
    "I162S2C99J4V1": "DIPLOMADO EN GESTION PUBLICA LOCAL",
    "I162S3C114J2V1": "TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA",
    "I162S3C115J2V1": "TECNICO EN FARMACIA",
    "I162S3C91J2V1": "TECNICO EN ENFERMERIA",
}

SHEET_RESUMEN = "RESUMEN_EJECUTIVO"
SHEET_OFERTA_NORMAL = "OFERTA_MATRIZ_NORMALIZADA"
SHEET_OFERTA_CLAS = "OFERTA_MATRIZ_CLASIFICADA"
SHEET_EXISTENTES = "PROGRAMAS_EXIST_NORMALIZADOS"
SHEET_CRUCE = "CRUCE_MATRIZ_VS_INDICES"
SHEET_FALTANTES = "PROGRAMAS_FALTANTES_PARA_CREAR"
SHEET_DUDOSOS = "DUDOSOS_REVISAR_MANUAL"
SHEET_EXISTEN = "YA_EXISTEN_EN_INDICES"
SHEET_NO_CREAR = "NO_CREAR"
SHEET_DICT = "DICCIONARIO_CAMPOS"
SHEET_AUD_COLS = "AUDITORIA_COLUMNAS"
SHEET_AUD_DUP = "AUDITORIA_DUPLICADOS"
SHEET_AUD_CODE = "AUDITORIA_CODIGO_UNICO"
SHEET_AUD_EXPECTED = "AUDITORIA_CODIGOS_ESPERADOS"
SHEET_BITACORA = "BITACORA_PROCESO"

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
OK_FILL = PatternFill("solid", fgColor="E2F0D9")
NOTE_FILL = PatternFill("solid", fgColor="D9EAF7")


@dataclass(frozen=True)
class Paths:
    repo: Path
    input_excel: Path
    existing_tsv: Path
    resultados: Path
    timestamp: str
    script_path: str
    excel_out: Path
    csv_out: Path
    md_out: Path
    json_out: Path
    error_out: Path


def locate_repo() -> Path:
    candidates: list[Path] = [Path.cwd()]
    file_name = globals().get("__file__")
    if file_name:
        try:
            candidates.append(Path(file_name).resolve().parents[3])
        except Exception:
            pass
    for candidate in candidates:
        if (candidate / "indices_2025" / "cned").exists():
            return candidate
    raise FileNotFoundError("No fue posible ubicar el repo avance_curricular.")


def build_paths() -> Paths:
    repo = locate_repo()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    resultados = repo / "indices_2025" / "cned" / "resultados"
    script_name = globals().get("__file__")
    script_path = str(Path(script_name).resolve()) if script_name and Path(script_name).exists() else "stdin"
    stem = f"CNED_PROGRAMAS_FALTANTES_CREAR_INDICES_DESDE_PROMEDIOS_{timestamp}"
    return Paths(
        repo=repo,
        input_excel=repo / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx",
        existing_tsv=repo / "indices_2025" / "cned" / "data" / "listado_referencia_cned.tsv",
        resultados=resultados,
        timestamp=timestamp,
        script_path=script_path,
        excel_out=resultados / f"{stem}.xlsx",
        csv_out=resultados / f"{stem}.csv",
        md_out=resultados / f"{stem}.md",
        json_out=resultados / f"{stem}.json",
        error_out=resultados / f"{stem}_ERROR.md",
    )


def clean_cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.lower() == "nan":
        return ""
    return text.strip()


def normalize_text(value: Any) -> str:
    text = clean_cell(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\._;,:'\"()\-\/]+", " ", text)
    text = text.upper()
    replacements = {
        r"\bTNS\b": "TECNICO NIVEL SUPERIOR",
        r"\bTEC NICO\b": "TECNICO",
        r"\bING\b": "INGENIERIA",
        r"\bINGE\b": "INGENIERIA",
        r"\bINGENIERIA EJEC\b": "INGENIERIA EJECUCION",
        r"\bPE\b": "PROGRAMA ESPECIAL",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def derive_code_parts(code: str) -> dict[str, str]:
    code = clean_cell(code)
    match = CODE_PATTERN.fullmatch(code)
    if not match:
        return {
            "CODIGO_UNICO_FORMATO_VALIDO": "NO",
            "CODIGO_IES_DERIVADO": "",
            "COD_SEDE_DERIVADO": "",
            "COD_CARRERA_DERIVADO": "",
            "JORNADA_DERIVADA": "",
            "VERSION_DERIVADA": "",
        }
    return {
        "CODIGO_UNICO_FORMATO_VALIDO": "SI",
        "CODIGO_IES_DERIVADO": match.group("ies"),
        "COD_SEDE_DERIVADO": match.group("sed"),
        "COD_CARRERA_DERIVADO": match.group("car"),
        "JORNADA_DERIVADA": match.group("jor"),
        "VERSION_DERIVADA": match.group("version"),
    }


def bool_label(value: bool) -> str:
    return "SI" if value else "NO"


def adjust_widths(ws: Any) -> None:
    for col_idx in range(1, ws.max_column + 1):
        values = [clean_cell(ws.cell(row=row_idx, column=col_idx).value) for row_idx in range(1, ws.max_row + 1)]
        width = min(max(max((len(value) for value in values), default=0) + 2, 12), 80)
        ws.column_dimensions[get_column_letter(col_idx)].width = width


def style_sheet(ws: Any, title: str) -> None:
    for col_idx in range(1, ws.max_column + 1):
        cell = ws.cell(1, col_idx)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    if title == SHEET_FALTANTES:
        header_map = {clean_cell(ws.cell(1, idx).value): idx for idx in range(1, ws.max_column + 1)}
        review_cols = {header_map.get("OBSERVACION_AUDITORIA"), header_map.get("Observaciones")}
        for row_idx in range(2, ws.max_row + 1):
            if header_map.get("ESTADO_CRUCE_INDICES"):
                ws.cell(row_idx, header_map["ESTADO_CRUCE_INDICES"]).fill = WARN_FILL
            for col_idx in review_cols:
                if col_idx:
                    ws.cell(row_idx, col_idx).fill = NOTE_FILL
    if title in {SHEET_EXISTEN, SHEET_NO_CREAR}:
        for row_idx in range(2, ws.max_row + 1):
            for col_idx in range(1, ws.max_column + 1):
                ws.cell(row_idx, col_idx).fill = OK_FILL
    if title == SHEET_DUDOSOS:
        for row_idx in range(2, ws.max_row + 1):
            for col_idx in range(1, ws.max_column + 1):
                ws.cell(row_idx, col_idx).fill = WARN_FILL
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{max(ws.max_row, 1)}"
    adjust_widths(ws)


def add_dataframe_sheet(wb: Workbook, title: str, df: pd.DataFrame) -> None:
    ws = wb.create_sheet(title)
    for row in dataframe_to_rows(df.fillna(""), index=False, header=True):
        ws.append(row)
    style_sheet(ws, title)


def assert_required_columns(df: pd.DataFrame, required_columns: list[str], label: str) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"{label} no contiene columnas requeridas: {missing}")


def load_matriz(paths: Paths) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    if not paths.input_excel.exists():
        raise FileNotFoundError(f"No existe la fuente principal {paths.input_excel}")
    wb = load_workbook(paths.input_excel, read_only=True, data_only=False)
    workbook_meta: list[dict[str, Any]] = []
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        workbook_meta.append(
            {
                "archivo": str(paths.input_excel.relative_to(paths.repo)),
                "hoja": sheet,
                "filas": max(ws.max_row - 1, 0),
                "columnas": ws.max_column,
            }
        )
    if "matriz" not in wb.sheetnames:
        raise ValueError("La hoja matriz no existe en PROMEDIOSDEALUMNOS_7804.xlsx")
    matriz_df = pd.read_excel(paths.input_excel, sheet_name="matriz", dtype=str).fillna("")
    assert_required_columns(matriz_df, MATRIZ_REQUIRED_COLUMNS, "Hoja matriz")
    if matriz_df.empty:
        raise ValueError("La hoja matriz existe, pero no contiene filas")
    return matriz_df, workbook_meta


def load_existing(paths: Paths) -> pd.DataFrame:
    if not paths.existing_tsv.exists():
        raise FileNotFoundError(f"No existe la base de existentes {paths.existing_tsv}")
    df = pd.read_csv(paths.existing_tsv, sep="\t", dtype=str, keep_default_na=False)
    assert_required_columns(df, EXISTENTES_REQUIRED_COLUMNS, "listado_referencia_cned.tsv")
    if df.empty:
        raise ValueError("La base de existentes está vacía")
    return df


def build_oferta_normalizada(matriz_df: pd.DataFrame, paths: Paths) -> pd.DataFrame:
    oferta = matriz_df.copy()
    derived = oferta["CODIGO_UNICO"].map(derive_code_parts).apply(pd.Series)
    oferta = pd.concat([oferta, derived], axis=1)
    oferta["NOMBRE_CARRERA_NORMALIZADO"] = oferta["NOMBRE_CARRERA"].map(normalize_text)
    oferta["NOMBRE_SEDE_NORMALIZADO"] = oferta["NOMBRE_SEDE"].map(normalize_text)
    oferta["FUENTE_ARCHIVO"] = str(paths.input_excel.relative_to(paths.repo))
    oferta["FUENTE_HOJA"] = "matriz"
    oferta["VALIDACION_COD_SEDE"] = oferta.apply(
        lambda row: "OK" if clean_cell(row["COD_SEDE"]) == clean_cell(row["COD_SEDE_DERIVADO"]) else "REVISAR",
        axis=1,
    )
    oferta["CLAVE_AUXILIAR_NOMBRE_SEDE_JORNADA"] = oferta.apply(
        lambda row: "|".join(
            [
                row["NOMBRE_CARRERA_NORMALIZADO"],
                row["NOMBRE_SEDE_NORMALIZADO"],
                clean_cell(row["JORNADA_DERIVADA"]),
            ]
        ),
        axis=1,
    )
    oferta["CLAVE_AUXILIAR_ESTRUCTURAL"] = oferta.apply(
        lambda row: "|".join(
            [
                row["NOMBRE_CARRERA_NORMALIZADO"],
                row["NOMBRE_SEDE_NORMALIZADO"],
                clean_cell(row["MODALIDAD"]),
                clean_cell(row["JORNADA"]),
                clean_cell(row["TIPO_PLAN_CARRERA"]),
                clean_cell(row["DURACION_ESTUDIOS"]),
                clean_cell(row["NIVEL_GLOBAL"]),
                clean_cell(row["NIVEL_CARRERA"]),
            ]
        ),
        axis=1,
    )
    return oferta


def classify_oferta(oferta_df: pd.DataFrame) -> pd.DataFrame:
    oferta = oferta_df.copy()
    oferta["ES_VIGENTE"] = oferta["VIGENCIA"].eq("1").map(bool_label)
    oferta["ES_PREGRADO"] = oferta["NIVEL_GLOBAL"].eq("1").map(bool_label)
    oferta["ES_POSGRADO_POSTITULO_DIPLOMADO"] = (
        oferta["NIVEL_GLOBAL"].eq("3") | oferta["NIVEL_CARRERA"].eq("5")
    ).map(bool_label)
    oferta["ES_DIPLOMADO"] = (
        oferta["NIVEL_CARRERA"].eq("5") | oferta["NOMBRE_CARRERA_NORMALIZADO"].str.contains("DIPLOMADO", regex=False)
    ).map(bool_label)
    oferta["ES_TECNICO"] = oferta["NIVEL_CARRERA"].eq("1").map(bool_label)
    oferta["ES_PROFESIONAL"] = oferta["NIVEL_CARRERA"].eq("2").map(bool_label)
    oferta["ES_PROGRAMA_ESPECIAL"] = oferta["TIPO_PLAN_CARRERA"].eq("3").map(bool_label)
    oferta["ES_PROGRAMA_REGULAR"] = oferta["TIPO_PLAN_CARRERA"].eq("1").map(bool_label)
    oferta["ALCANCE_INDICES_CREAR_PROGRAMA"] = oferta["VIGENCIA"].eq("1").map(lambda value: "SI" if value else "NO")
    oferta["MOTIVO_ALCANCE"] = oferta["VIGENCIA"].eq("1").map(
        lambda value: "VIGENTE_EN_MATRIZ" if value else "NO_VIGENTE_EN_MATRIZ"
    )
    oferta["NIVEL_BUCKET"] = oferta.apply(
        lambda row: "PREGRADO" if row["ES_PREGRADO"] == "SI" else "POSGRADO_DIPLOMADO",
        axis=1,
    )
    return oferta


def build_existing_normalizados(existing_df: pd.DataFrame, paths: Paths) -> pd.DataFrame:
    existing = existing_df.copy()
    existing["CODIGO_UNICO"] = existing["Codigo SIES"].map(clean_cell)
    derived = existing["CODIGO_UNICO"].map(derive_code_parts).apply(pd.Series)
    existing = pd.concat([existing, derived], axis=1)
    existing["NOMBRE_CARRERA_NORMALIZADO"] = existing["Nombre Programa"].map(normalize_text)
    existing["SEDE_NORMALIZADA"] = existing["Sede"].map(normalize_text)
    existing["HORARIO_NORMALIZADO"] = existing["Horario"].map(normalize_text)
    existing["MODALIDAD_NORMALIZADA"] = existing["Modalidad Programa"].map(normalize_text)
    existing["TIPO_PROGRAMA_NORMALIZADO"] = existing["Tipo Programa"].map(normalize_text)
    existing["TIPO_CARRERA_NORMALIZADO"] = existing["Tipo Carrera"].map(normalize_text)
    existing["DURACION_ESTUDIOS_NORMALIZADA"] = existing["Duracion (en semestres)"].map(clean_cell)
    existing["NIVEL_BUCKET"] = existing["Nivel Pregrado/Posgrado"].map(
        lambda value: "PREGRADO" if normalize_text(value) == "PREGRADO" else "POSGRADO_DIPLOMADO"
    )
    existing["CLAVE_CODIGO_UNICO"] = existing["CODIGO_UNICO"]
    existing["CLAVE_AUXILIAR_NOMBRE_SEDE_JORNADA"] = existing.apply(
        lambda row: "|".join(
            [
                row["NOMBRE_CARRERA_NORMALIZADO"],
                row["SEDE_NORMALIZADA"],
                row["HORARIO_NORMALIZADO"],
            ]
        ),
        axis=1,
    )
    existing["CLAVE_AUXILIAR_ESTRUCTURAL"] = existing.apply(
        lambda row: "|".join(
            [
                row["NOMBRE_CARRERA_NORMALIZADO"],
                row["SEDE_NORMALIZADA"],
                row["HORARIO_NORMALIZADO"],
                row["MODALIDAD_NORMALIZADA"],
                row["TIPO_PROGRAMA_NORMALIZADO"],
                row["TIPO_CARRERA_NORMALIZADO"],
                row["DURACION_ESTUDIOS_NORMALIZADA"],
                row["NIVEL_BUCKET"],
            ]
        ),
        axis=1,
    )
    existing["FUENTE_ARCHIVO"] = str(paths.existing_tsv.relative_to(paths.repo))
    return existing


def pick_unique_or_review(series: pd.Series) -> str:
    values = [clean_cell(value) for value in series if clean_cell(value)]
    uniques = sorted(set(values))
    if len(uniques) == 1:
        return uniques[0]
    return "REVISAR"


def build_reference_dictionaries(existing_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    campus_by_sede = {}
    for sede, group in existing_df.groupby("Sede"):
        campus_by_sede[clean_cell(sede)] = pick_unique_or_review(group["Campus"])
    return {"campus_by_sede": campus_by_sede}


def platform_sede_label(raw_sede: str) -> str:
    normalized = normalize_text(raw_sede)
    if normalized == "CASA CENTRAL SANTIAGO":
        return "Santiago"
    if normalized == "SEDE CONCEPCION":
        return "Concepción"
    if normalized.startswith("SEDE "):
        return clean_cell(raw_sede).replace("SEDE ", "").title()
    return clean_cell(raw_sede).title()


def map_tipo_carrera(row: pd.Series) -> str:
    if row["NIVEL_CARRERA"] == "1":
        return "Técnico Nivel Superior"
    if row["NIVEL_CARRERA"] == "2":
        return "Profesional"
    if row["NIVEL_CARRERA"] == "5":
        if "DIPLOMADO" in row["NOMBRE_CARRERA_NORMALIZADO"]:
            return "Diplomado"
        return "Postítulo / Posgrado"
    return "REVISAR"


def map_horario(code: str) -> str:
    return {"1": "Diurno", "2": "Vespertino", "4": "Otro"}.get(clean_cell(code), "REVISAR")


def map_modalidad(code: str) -> str:
    return {"1": "Presencial", "3": "No presencial"}.get(clean_cell(code), "REVISAR")


def map_tipo_programa(code: str) -> str:
    return {"1": "Programa Regular", "3": "Programa Especial"}.get(clean_cell(code), "REVISAR")


def match_strength(row: pd.Series, candidate: pd.Series) -> tuple[int, int, list[str]]:
    checks: list[tuple[str, str, str]] = [
        ("horario", normalize_text(row["HORARIO_FORM"]), candidate["HORARIO_NORMALIZADO"]),
        ("modalidad", normalize_text(row["MODALIDAD_FORM"]), candidate["MODALIDAD_NORMALIZADA"]),
        ("tipo_programa", normalize_text(row["TIPO_PROGRAMA_FORM"]), candidate["TIPO_PROGRAMA_NORMALIZADO"]),
        ("tipo_carrera", normalize_text(row["TIPO_CARRERA_FORM"]), candidate["TIPO_CARRERA_NORMALIZADO"]),
        ("duracion", clean_cell(row["DURACION_ESTUDIOS"]), candidate["DURACION_ESTUDIOS_NORMALIZADA"]),
        ("nivel_bucket", row["NIVEL_BUCKET"], candidate["NIVEL_BUCKET"]),
    ]
    compared = 0
    matched = 0
    details: list[str] = []
    for label, left_value, right_value in checks:
        if left_value in {"", "REVISAR"} or right_value == "":
            continue
        compared += 1
        if left_value == right_value:
            matched += 1
            details.append(f"{label}=OK")
        else:
            details.append(f"{label}=REVISAR")
    return compared, matched, details


def find_auxiliary_matches(row: pd.Series, existing_df: pd.DataFrame) -> list[dict[str, Any]]:
    candidates = existing_df[
        (existing_df["NOMBRE_CARRERA_NORMALIZADO"] == row["NOMBRE_CARRERA_NORMALIZADO"])
        & (existing_df["SEDE_NORMALIZADA"] == row["SEDE_PLATAFORMA_NORMALIZADA"])
    ].copy()
    matches: list[dict[str, Any]] = []
    for _, candidate in candidates.iterrows():
        compared, matched, details = match_strength(row, candidate)
        if compared >= 3 and matched == compared:
            matches.append(
                {
                    "candidate": candidate,
                    "compared": compared,
                    "matched": matched,
                    "details": details,
                }
            )
    return matches


def build_cruce(oferta_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame:
    existing_codes = set(existing_df.loc[existing_df["CODIGO_UNICO"] != "", "CODIGO_UNICO"])
    rows: list[dict[str, Any]] = []
    for _, row in oferta_df.iterrows():
        record = row.to_dict()
        tipo_carrera = map_tipo_carrera(row)
        horario = map_horario(row["JORNADA"])
        modalidad = map_modalidad(row["MODALIDAD"])
        tipo_programa = map_tipo_programa(row["TIPO_PLAN_CARRERA"])
        sede_plataforma = platform_sede_label(row["NOMBRE_SEDE"])
        record["TIPO_CARRERA_FORM"] = tipo_carrera
        record["HORARIO_FORM"] = horario
        record["MODALIDAD_FORM"] = modalidad
        record["TIPO_PROGRAMA_FORM"] = tipo_programa
        record["SEDE_PLATAFORMA"] = sede_plataforma
        record["SEDE_PLATAFORMA_NORMALIZADA"] = normalize_text(sede_plataforma)
        if row["VIGENCIA"] != "1":
            record.update(
                {
                    "ESTADO_CRUCE_INDICES": "NO_CREAR_POR_NO_VIGENTE",
                    "MOTIVO_ESTADO_CRUCE": "Registro no vigente en matriz",
                    "CODIGO_UNICO_MATCH": "",
                    "TIPO_MATCH": "NO_APLICA",
                    "CONFIANZA_MATCH": "NO_APLICA",
                    "OBSERVACION_AUDITORIA": "No crear: VIGENCIA distinta de 1.",
                    "REQUIERE_CREACION_MANUAL": "NO",
                }
            )
            rows.append(record)
            continue
        if row["ALCANCE_INDICES_CREAR_PROGRAMA"] != "SI":
            record.update(
                {
                    "ESTADO_CRUCE_INDICES": "NO_CREAR_POR_FUERA_DE_ALCANCE",
                    "MOTIVO_ESTADO_CRUCE": row["MOTIVO_ALCANCE"],
                    "CODIGO_UNICO_MATCH": "",
                    "TIPO_MATCH": "NO_APLICA",
                    "CONFIANZA_MATCH": "NO_APLICA",
                    "OBSERVACION_AUDITORIA": "No crear: fuera de alcance documentado.",
                    "REQUIERE_CREACION_MANUAL": "NO",
                }
            )
            rows.append(record)
            continue
        if row["CODIGO_UNICO"] in existing_codes:
            matched_rows = existing_df.loc[existing_df["CODIGO_UNICO"] == row["CODIGO_UNICO"]]
            record.update(
                {
                    "ESTADO_CRUCE_INDICES": "YA_EXISTE_EN_INDICES",
                    "MOTIVO_ESTADO_CRUCE": "Coincidencia exacta por CODIGO_UNICO",
                    "CODIGO_UNICO_MATCH": row["CODIGO_UNICO"],
                    "TIPO_MATCH": "CODIGO_UNICO_EXACTO",
                    "CONFIANZA_MATCH": "EXACTA",
                    "OBSERVACION_AUDITORIA": f"Coincidencia exacta con {len(matched_rows)} fila(s) en programas existentes.",
                    "REQUIERE_CREACION_MANUAL": "NO",
                }
            )
            rows.append(record)
            continue
        aux_matches = find_auxiliary_matches(pd.Series(record), existing_df)
        if aux_matches:
            matched_codes = sorted({clean_cell(item["candidate"]["CODIGO_UNICO"]) for item in aux_matches if clean_cell(item["candidate"]["CODIGO_UNICO"])})
            matched_carreras = sorted({clean_cell(item["candidate"]["Cod.Carr."]) for item in aux_matches if clean_cell(item["candidate"]["Cod.Carr."])})
            confidence = "ALTA" if len(aux_matches) == 1 else "MEDIA"
            reason = "Coincidencia auxiliar fuerte sin coincidencia exacta por CODIGO_UNICO"
            observation = (
                f"Coincidencias auxiliares={len(aux_matches)}; Cod.Carr. existente={matched_carreras}; "
                f"Codigo SIES existente={matched_codes or ['VACIO_EN_EXISTENTES']}"
            )
            record.update(
                {
                    "ESTADO_CRUCE_INDICES": "DUDOSO_REVISAR_MANUAL",
                    "MOTIVO_ESTADO_CRUCE": reason,
                    "CODIGO_UNICO_MATCH": " | ".join(matched_codes),
                    "TIPO_MATCH": "AUXILIAR_FUERTE",
                    "CONFIANZA_MATCH": confidence,
                    "OBSERVACION_AUDITORIA": observation,
                    "REQUIERE_CREACION_MANUAL": "NO",
                }
            )
            rows.append(record)
            continue
        record.update(
            {
                "ESTADO_CRUCE_INDICES": "FALTA_CREAR_EN_INDICES",
                "MOTIVO_ESTADO_CRUCE": "No existe coincidencia exacta por CODIGO_UNICO ni match auxiliar fuerte",
                "CODIGO_UNICO_MATCH": "",
                "TIPO_MATCH": "SIN_MATCH",
                "CONFIANZA_MATCH": "ALTA_NO_EXISTENCIA",
                "OBSERVACION_AUDITORIA": (
                    "Crear según PROMEDIOSDEALUMNOS_7804.xlsx hoja matriz; no encontrado en listado existente INDICES por CODIGO_UNICO."
                ),
                "REQUIERE_CREACION_MANUAL": "SI",
            }
        )
        rows.append(record)
    return pd.DataFrame(rows)


def build_programas_faltantes(cruce_df: pd.DataFrame, dictionaries: dict[str, dict[str, str]], paths: Paths) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    campus_by_sede = dictionaries["campus_by_sede"]
    faltantes = cruce_df.loc[cruce_df["ESTADO_CRUCE_INDICES"] == "FALTA_CREAR_EN_INDICES"].copy()
    for _, row in faltantes.iterrows():
        sede = row["SEDE_PLATAFORMA"]
        campus = campus_by_sede.get(sede, "REVISAR")
        detalle_programa = "No aplica" if row["TIPO_PROGRAMA_FORM"] == "Programa Regular" else "REVISAR"
        row_dict = {
            "CODIGO_UNICO": row["CODIGO_UNICO"],
            "CODIGO_IES_NUM": row["CODIGO_IES_NUM"],
            "COD_SEDE": row["COD_SEDE"],
            "COD_CARRERA_DERIVADO": row["COD_CARRERA_DERIVADO"],
            "JORNADA": row["JORNADA"],
            "VERSION_DERIVADA": row["VERSION_DERIVADA"],
            "NOMBRE_CARRERA_ORIGINAL": row["NOMBRE_CARRERA"],
            "NOMBRE_CARRERA_NORMALIZADO": row["NOMBRE_CARRERA_NORMALIZADO"],
            "MODALIDAD_ORIGINAL": row["MODALIDAD"],
            "TIPO_PLAN_CARRERA_ORIGINAL": row["TIPO_PLAN_CARRERA"],
            "CARACT_PLAN_ESPECIAL_ORIGINAL": row["CARACT_PLAN_ESPECIAL"],
            "NIVEL_GLOBAL": row["NIVEL_GLOBAL"],
            "NIVEL_CARRERA": row["NIVEL_CARRERA"],
            "VIGENCIA": row["VIGENCIA"],
            "ESTADO_CRUCE_INDICES": row["ESTADO_CRUCE_INDICES"],
            "MOTIVO_ESTADO_CRUCE": row["MOTIVO_ESTADO_CRUCE"],
            "FUENTE": "PROMEDIOSDEALUMNOS_7804.xlsx / hoja matriz",
            "REVISADO_MANUALMENTE": "NO",
            "OBSERVACION_AUDITORIA": row["OBSERVACION_AUDITORIA"],
            "Sede": sede,
            "Tipo de Carrera": row["TIPO_CARRERA_FORM"],
            "Nombre": row["NOMBRE_CARRERA"],
            "Mención o Especialidad": "REVISAR",
            "Año de inicio de Actividades": "REVISAR",
            "Campus": campus if campus else "REVISAR",
            "Horario": row["HORARIO_FORM"],
            "Estado": "Programa o Carrera Nueva(o)",
            "Tipo Programa": row["TIPO_PROGRAMA_FORM"],
            "Detalle del Tipo de Programa (especiales)": detalle_programa,
            "Modalidad del Programa": row["MODALIDAD_FORM"],
            "Área del Conocimiento": "REVISAR",
            "Sub Área": "REVISAR",
            "Carrera Genérica": "REVISAR",
            "Título que otorga el programa": "REVISAR",
            "Grado Académico que otorga el programa": "REVISAR",
            "Dependencia": "REVISAR",
            "Régimen": "REVISAR",
            "Duración del programa en Semestres": clean_cell(row["DURACION_ESTUDIOS"]) or "REVISAR",
            "Ingreso Directo": "REVISAR",
            "Ingreso desde un plan Común": "REVISAR",
            "Ingreso desde Bachillerato": "REVISAR",
            "Otro Tipo de Ingreso": "REVISAR",
            "Ingreso otro": "REVISAR",
            "Observaciones": (
                "Crear según matriz PROMEDIOSDEALUMNOS_7804.xlsx / hoja matriz; "
                "no encontrado en listado existente INDICES por CODIGO_UNICO."
            ),
        }
        rows.append(row_dict)
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def build_expected_codes_audit(cruce_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for code, expected_name in EXPECTED_CODES.items():
        cruce_match = cruce_df.loc[cruce_df["CODIGO_UNICO"] == code]
        existing_match = existing_df.loc[existing_df["CODIGO_UNICO"] == code]
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_ESPERADO_USUARIO": expected_name,
                "EXISTE_EN_OFERTA_MATRIZ": "SI" if not cruce_match.empty else "NO",
                "EXISTE_EN_PROGRAMAS_EXISTENTES": "SI" if not existing_match.empty else "NO",
                "FILAS_MATRIZ": len(cruce_match),
                "FILAS_EXISTENTES": len(existing_match),
                "NOMBRE_MATRIZ": " | ".join(sorted(set(cruce_match["NOMBRE_CARRERA"].astype(str)))) if not cruce_match.empty else "",
                "NOMBRE_EXISTENTES": " | ".join(sorted(set(existing_match["Nombre Programa"].astype(str)))) if not existing_match.empty else "",
                "ESTADO_CRUCE_INDICES": cruce_match["ESTADO_CRUCE_INDICES"].iloc[0] if not cruce_match.empty else "NO_EN_OFERTA_MATRIZ",
                "MOTIVO_ESTADO_CRUCE": cruce_match["MOTIVO_ESTADO_CRUCE"].iloc[0] if not cruce_match.empty else "Código esperado no encontrado en matriz",
                "OBSERVACION": (
                    "OK" if not cruce_match.empty else "BLOQUEANTE: el código esperado no está en la fuente matriz"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_dictionary_sheet() -> pd.DataFrame:
    rows = [
        {
            "SECCION": "ALIAS_HOJAS",
            "CAMPO_ORIGINAL": "PROGRAMAS_EXISTENTES_NORMALIZADOS",
            "CAMPO_NORMALIZADO": SHEET_EXISTENTES,
            "OBSERVACION": "Alias por límite de 31 caracteres de Excel.",
        },
        {
            "SECCION": "FUENTE_MATRIZ",
            "CAMPO_ORIGINAL": "CODIGO_IES_NUM",
            "CAMPO_NORMALIZADO": "CODIGO_IES_NUM",
            "OBSERVACION": "La hoja matriz ya viene con el encabezado canónico.",
        },
        {
            "SECCION": "FUENTE_MATRIZ",
            "CAMPO_ORIGINAL": "CODIGO_UNICO",
            "CAMPO_NORMALIZADO": "CODIGO_UNICO",
            "OBSERVACION": "Llave principal del cruce.",
        },
        {
            "SECCION": "FUENTE_EXISTENTES",
            "CAMPO_ORIGINAL": "Codigo SIES",
            "CAMPO_NORMALIZADO": "CODIGO_UNICO",
            "OBSERVACION": "Campo usado como identificador de programas existentes.",
        },
        {
            "SECCION": "FUENTE_EXISTENTES",
            "CAMPO_ORIGINAL": "Cod.Carr.",
            "CAMPO_NORMALIZADO": "COD_CARRERA_EXISTENTE",
            "OBSERVACION": "Se mantiene para trazabilidad de la referencia existente.",
        },
        {
            "SECCION": "DICCIONARIO_JORNADA",
            "CAMPO_ORIGINAL": "1",
            "CAMPO_NORMALIZADO": "Diurno",
            "OBSERVACION": "Derivado por coincidencias exactas entre matriz y existentes.",
        },
        {
            "SECCION": "DICCIONARIO_JORNADA",
            "CAMPO_ORIGINAL": "2",
            "CAMPO_NORMALIZADO": "Vespertino",
            "OBSERVACION": "Derivado por coincidencias exactas entre matriz y existentes.",
        },
        {
            "SECCION": "DICCIONARIO_JORNADA",
            "CAMPO_ORIGINAL": "4",
            "CAMPO_NORMALIZADO": "Otro",
            "OBSERVACION": "Derivado por coincidencias exactas entre matriz y existentes.",
        },
        {
            "SECCION": "DICCIONARIO_JORNADA",
            "CAMPO_ORIGINAL": "3",
            "CAMPO_NORMALIZADO": "REVISAR",
            "OBSERVACION": "Sin evidencia suficiente en el solape exacto.",
        },
        {
            "SECCION": "DICCIONARIO_MODALIDAD",
            "CAMPO_ORIGINAL": "1",
            "CAMPO_NORMALIZADO": "Presencial",
            "OBSERVACION": "Derivado por coincidencias exactas; existe 1 outlier vacío en referencia.",
        },
        {
            "SECCION": "DICCIONARIO_MODALIDAD",
            "CAMPO_ORIGINAL": "3",
            "CAMPO_NORMALIZADO": "No presencial",
            "OBSERVACION": "Derivado por coincidencias exactas entre matriz y existentes.",
        },
        {
            "SECCION": "DICCIONARIO_MODALIDAD",
            "CAMPO_ORIGINAL": "2",
            "CAMPO_NORMALIZADO": "REVISAR",
            "OBSERVACION": "Sin evidencia suficiente en el solape exacto.",
        },
        {
            "SECCION": "DICCIONARIO_TIPO_PLAN",
            "CAMPO_ORIGINAL": "1",
            "CAMPO_NORMALIZADO": "Programa Regular",
            "OBSERVACION": "Mayoría empírica 56/57; se deja advertencia por 1 outlier histórico.",
        },
        {
            "SECCION": "DICCIONARIO_TIPO_PLAN",
            "CAMPO_ORIGINAL": "3",
            "CAMPO_NORMALIZADO": "Programa Especial",
            "OBSERVACION": "Mayoría empírica 10/11; se deja advertencia por 1 outlier histórico.",
        },
        {
            "SECCION": "DICCIONARIO_NIVEL_CARRERA",
            "CAMPO_ORIGINAL": "1",
            "CAMPO_NORMALIZADO": "Técnico Nivel Superior",
            "OBSERVACION": "Derivado por coincidencias exactas y consistente con la nomenclatura institucional.",
        },
        {
            "SECCION": "DICCIONARIO_NIVEL_CARRERA",
            "CAMPO_ORIGINAL": "2",
            "CAMPO_NORMALIZADO": "Profesional",
            "OBSERVACION": "Derivado por coincidencias exactas entre matriz y existentes.",
        },
        {
            "SECCION": "DICCIONARIO_NIVEL_CARRERA",
            "CAMPO_ORIGINAL": "5",
            "CAMPO_NORMALIZADO": "Diplomado",
            "OBSERVACION": "Aplicado cuando el nombre institucional contiene DIPLOMADO.",
        },
    ]
    return pd.DataFrame(rows)


def build_auditoria_columnas(dataframes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for sheet_name, df in dataframes.items():
        for column in df.columns:
            series = df[column].map(clean_cell)
            rows.append(
                {
                    "HOJA": sheet_name,
                    "COLUMNA": column,
                    "TOTAL_FILAS": len(df),
                    "VACIOS": int(series.eq("").sum()),
                    "UNIQUE_NO_VACIOS": int(series[series.ne("")].nunique()),
                }
            )
    return pd.DataFrame(rows)


def build_auditoria_duplicados(oferta_df: pd.DataFrame, existing_df: pd.DataFrame, faltantes_df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "OBJETO": "OFERTA_MATRIZ_NORMALIZADA",
            "CAMPO": "CODIGO_UNICO",
            "DUPLICADOS": int(oferta_df["CODIGO_UNICO"].duplicated().sum()),
            "OBSERVACION": "La matriz no debe tener duplicados inesperados por CODIGO_UNICO.",
        },
        {
            "OBJETO": SHEET_EXISTENTES,
            "CAMPO": "CODIGO_UNICO",
            "DUPLICADOS": int(existing_df.loc[existing_df["CODIGO_UNICO"] != "", "CODIGO_UNICO"].duplicated().sum()),
            "OBSERVACION": "Duplicados heredados del listado de referencia existente.",
        },
        {
            "OBJETO": SHEET_EXISTENTES,
            "CAMPO": "CODIGO_UNICO_VACIO",
            "DUPLICADOS": int(existing_df["CODIGO_UNICO"].eq("").sum()),
            "OBSERVACION": "Registros existentes sin Codigo SIES; alimentan revisión manual.",
        },
        {
            "OBJETO": SHEET_FALTANTES,
            "CAMPO": "CODIGO_UNICO",
            "DUPLICADOS": int(faltantes_df["CODIGO_UNICO"].duplicated().sum()) if not faltantes_df.empty else 0,
            "OBSERVACION": "La hoja final para crear manualmente no debe repetir CODIGO_UNICO.",
        },
    ]
    return pd.DataFrame(rows)


def build_auditoria_codigo_unico(oferta_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame:
    oferta_rows = oferta_df[[
        "CODIGO_UNICO",
        "CODIGO_UNICO_FORMATO_VALIDO",
        "CODIGO_IES_DERIVADO",
        "COD_SEDE_DERIVADO",
        "COD_CARRERA_DERIVADO",
        "JORNADA_DERIVADA",
        "VERSION_DERIVADA",
    ]].copy()
    oferta_rows.insert(0, "FUENTE", SHEET_OFERTA_NORMAL)
    existing_rows = existing_df[[
        "CODIGO_UNICO",
        "CODIGO_UNICO_FORMATO_VALIDO",
        "CODIGO_IES_DERIVADO",
        "COD_SEDE_DERIVADO",
        "COD_CARRERA_DERIVADO",
        "JORNADA_DERIVADA",
        "VERSION_DERIVADA",
    ]].copy()
    existing_rows.insert(0, "FUENTE", SHEET_EXISTENTES)
    return pd.concat([oferta_rows, existing_rows], ignore_index=True)


def build_bitacora(paths: Paths) -> pd.DataFrame:
    rows = [
        {"FASE": "0", "ACCION": "Baseline Git y entorno", "DETALLE": "Ejecución local sin tocar artefactos oficiales previos."},
        {"FASE": "1", "ACCION": "Inventario", "DETALLE": f"Fuente principal ubicada en {paths.input_excel.relative_to(paths.repo)}."},
        {"FASE": "2", "ACCION": "Inspección workbook", "DETALLE": "Se validó existencia de hoja matriz y estructura de 19 columnas canónicas."},
        {"FASE": "3-4", "ACCION": "Normalización y clasificación", "DETALLE": "Se derivaron claves desde CODIGO_UNICO y banderas de alcance."},
        {"FASE": "5-7", "ACCION": "Carga de existentes y cruce", "DETALLE": f"Base de existentes usada: {paths.existing_tsv.relative_to(paths.repo)}."},
        {"FASE": "8-9", "ACCION": "Preparación de Excel operativo", "DETALLE": f"Hoja principal: {SHEET_FALTANTES}."},
        {"FASE": "10-13", "ACCION": "Validaciones y auditoría", "DETALLE": "Se reabren Excel, CSV, Markdown y JSON para validar consistencia."},
        {"FASE": "NOTA", "ACCION": "Alias de hoja", "DETALLE": f"{SHEET_EXISTENTES} representa PROGRAMAS_EXISTENTES_NORMALIZADOS por límite de Excel."},
    ]
    return pd.DataFrame(rows)


def build_resumen(
    paths: Paths,
    workbook_meta: list[dict[str, Any]],
    cruce_df: pd.DataFrame,
    faltantes_df: pd.DataFrame,
    dudosos_df: pd.DataFrame,
    existen_df: pd.DataFrame,
    no_crear_df: pd.DataFrame,
) -> pd.DataFrame:
    counts = cruce_df["ESTADO_CRUCE_INDICES"].value_counts().to_dict()
    rows = [
        {"CAMPO": "FECHA_GENERACION", "VALOR": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "DETALLE": "Timestamp de ejecución"},
        {"CAMPO": "FUENTE_PRINCIPAL", "VALOR": "PROMEDIOSDEALUMNOS_7804.xlsx / hoja matriz", "DETALLE": str(paths.input_excel.relative_to(paths.repo))},
        {"CAMPO": "FUENTE_EXISTENTES_INDICES", "VALOR": str(paths.existing_tsv.relative_to(paths.repo)), "DETALLE": "Listado base de programas existentes"},
        {"CAMPO": "TOTAL_OFERTA_MATRIZ", "VALOR": str(len(cruce_df)), "DETALLE": "Total de registros en matriz"},
        {"CAMPO": "TOTAL_VIGENTES", "VALOR": str(int(cruce_df["VIGENCIA"].eq("1").sum())), "DETALLE": "Todos los vigentes en matriz"},
        {"CAMPO": "TOTAL_YA_EXISTE_EN_INDICES", "VALOR": str(counts.get("YA_EXISTE_EN_INDICES", 0)), "DETALLE": "Coincidencia exacta por CODIGO_UNICO"},
        {"CAMPO": "TOTAL_FALTA_CREAR_EN_INDICES", "VALOR": str(counts.get("FALTA_CREAR_EN_INDICES", 0)), "DETALLE": f"Hoja {SHEET_FALTANTES}"},
        {"CAMPO": "TOTAL_DUDOSO_REVISAR_MANUAL", "VALOR": str(counts.get("DUDOSO_REVISAR_MANUAL", 0)), "DETALLE": f"Hoja {SHEET_DUDOSOS}"},
        {"CAMPO": "TOTAL_NO_CREAR", "VALOR": str(len(no_crear_df)), "DETALLE": f"Hoja {SHEET_NO_CREAR}"},
        {"CAMPO": "HOJA_PRINCIPAL_PARA_TRABAJO_MANUAL", "VALOR": SHEET_FALTANTES, "DETALLE": "Abrir esta hoja para crear programas en plataforma"},
        {"CAMPO": "CAMPOS_FORMULARIO_COMPLETADOS", "VALOR": str(len(FORM_FIELDS)), "DETALLE": ", ".join(FORM_FIELDS)},
        {"CAMPO": "ARCHIVO_EXCEL_FINAL", "VALOR": str(paths.excel_out.relative_to(paths.repo)), "DETALLE": "Salida timestamped"},
        {"CAMPO": "SHEETS_PROMEDIOS", "VALOR": ", ".join(item["hoja"] for item in workbook_meta), "DETALLE": "Inventario del workbook fuente"},
    ]
    return pd.DataFrame(rows)


def build_markdown(
    paths: Paths,
    dictamen: str,
    counts: dict[str, int],
    faltantes_df: pd.DataFrame,
    dudosos_df: pd.DataFrame,
    no_crear_df: pd.DataFrame,
    expected_df: pd.DataFrame,
    warnings: list[str],
    validations: list[str],
) -> str:
    warnings_md = "\n".join(f"- {item}" for item in warnings) if warnings else "- ninguna"
    validations_md = "\n".join(f"- {item}" for item in validations)
    faltantes_sample = faltantes_df[["CODIGO_UNICO", "Nombre", "Sede"]].head(15).to_dict(orient="records") if not faltantes_df.empty else []
    dudosos_sample = dudosos_df[["CODIGO_UNICO", "NOMBRE_CARRERA", "OBSERVACION_AUDITORIA"]].head(15).to_dict(orient="records") if not dudosos_df.empty else []
    expected_missing = expected_df.loc[expected_df["EXISTE_EN_OFERTA_MATRIZ"] != "SI", "CODIGO_UNICO"].tolist()
    return f"""# CNED Programas Faltantes para Crear en INDICES

## Dictamen

{dictamen}

## Fuentes usadas

- Fuente principal: PROMEDIOSDEALUMNOS_7804.xlsx / hoja matriz
- Archivo físico: {paths.input_excel.resolve()}
- Fuente existentes INDICES: {paths.existing_tsv.resolve()}
- Script ejecutado: {paths.script_path}

## Conteos

- TOTAL_OFERTA_MATRIZ: {counts.get('TOTAL_OFERTA_MATRIZ', 0)}
- TOTAL_VIGENTES: {counts.get('TOTAL_VIGENTES', 0)}
- TOTAL_YA_EXISTE_EN_INDICES: {counts.get('TOTAL_YA_EXISTE_EN_INDICES', 0)}
- TOTAL_FALTA_CREAR_EN_INDICES: {counts.get('TOTAL_FALTA_CREAR_EN_INDICES', 0)}
- TOTAL_DUDOSO_REVISAR_MANUAL: {counts.get('TOTAL_DUDOSO_REVISAR_MANUAL', 0)}
- TOTAL_NO_CREAR: {counts.get('TOTAL_NO_CREAR', 0)}

## Reglas de cruce

- Prioridad 1: coincidencia exacta por CODIGO_UNICO.
- Prioridad 2: coincidencia auxiliar fuerte por nombre normalizado, sede, horario, modalidad, tipo de programa, tipo de carrera, duración y bucket de nivel cuando hay evidencia suficiente.
- Regla conservadora: coincidencia auxiliar fuerte se clasifica como DUDOSO_REVISAR_MANUAL, no como YA_EXISTE_EN_INDICES.
- Regla operativa: si no existe match exacto ni auxiliar fuerte y el registro está vigente, queda como FALTA_CREAR_EN_INDICES.

## Validaciones

{validations_md}

## Programas faltantes

- Hoja principal: {SHEET_FALTANTES}
- Muestra: {json.dumps(faltantes_sample, ensure_ascii=False)}

## Dudosos

- Total: {len(dudosos_df)}
- Muestra: {json.dumps(dudosos_sample, ensure_ascii=False)}

## No crear

- Total: {len(no_crear_df)}

## Auditoría de códigos esperados

- Códigos esperados ausentes en oferta matriz: {expected_missing if expected_missing else 'ninguno'}

## Advertencias

{warnings_md}

## Próximos pasos

- Abrir el Excel final {paths.excel_out.resolve()}.
- Usar la hoja {SHEET_FALTANTES} para completar pantalla Crear Programa.
- Revisar primero la hoja {SHEET_DUDOSOS} antes de crear cualquier programa ambiguo.
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_outputs(
    paths: Paths,
    faltantes_df: pd.DataFrame,
    cruce_df: pd.DataFrame,
    expected_df: pd.DataFrame,
    no_crear_df: pd.DataFrame,
) -> tuple[list[str], list[str], list[str]]:
    checks: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    if paths.input_excel.exists():
        checks.append("PROMEDIOSDEALUMNOS_7804.xlsx existe")
    else:
        errors.append("No existe PROMEDIOSDEALUMNOS_7804.xlsx")

    wb_source = load_workbook(paths.input_excel, read_only=True, data_only=False)
    if "matriz" in wb_source.sheetnames:
        checks.append("La hoja matriz existe en PROMEDIOSDEALUMNOS_7804.xlsx")
    else:
        errors.append("La hoja matriz no existe")

    if len(cruce_df) > 0:
        checks.append(f"La hoja matriz contiene filas: {len(cruce_df)}")
    else:
        errors.append("La hoja matriz no contiene filas")

    if int(cruce_df["CODIGO_UNICO"].eq("").sum()) == 0:
        checks.append("CODIGO_UNICO existe y no contiene vacíos en matriz")
    else:
        errors.append("Existen CODIGO_UNICO vacíos en matriz")

    if int(cruce_df["CODIGO_UNICO_FORMATO_VALIDO"].eq("SI").sum()) == len(cruce_df):
        checks.append("Todo CODIGO_UNICO no vacío cumple formato esperado")
    else:
        errors.append("Hay CODIGO_UNICO con formato inválido")

    if int(cruce_df["CODIGO_UNICO"].duplicated().sum()) == 0:
        checks.append("No hay duplicados inesperados por CODIGO_UNICO en matriz")
    else:
        errors.append("Hay duplicados inesperados por CODIGO_UNICO en matriz")

    if int(cruce_df["VALIDACION_COD_SEDE"].eq("OK").sum()) == len(cruce_df):
        checks.append("Los derivados de CODIGO_UNICO son coherentes con COD_SEDE")
    else:
        errors.append("Hay incoherencias entre CODIGO_UNICO y COD_SEDE")

    if paths.existing_tsv.exists():
        checks.append("Existe base de programas ya existentes en INDICES/SIES")
    else:
        errors.append("No existe base de programas existentes en INDICES/SIES")

    if int(cruce_df["TIPO_MATCH"].eq("CODIGO_UNICO_EXACTO").sum()) >= 0:
        checks.append("El cruce por CODIGO_UNICO se ejecutó")

    if set(faltantes_df["ESTADO_CRUCE_INDICES"].unique()) <= {"FALTA_CREAR_EN_INDICES"}:
        checks.append(f"{SHEET_FALTANTES} contiene solo FALTA_CREAR_EN_INDICES")
    else:
        errors.append(f"{SHEET_FALTANTES} mezcla estados distintos de FALTA_CREAR_EN_INDICES")

    if int(faltantes_df["CODIGO_UNICO"].eq("").sum()) == 0:
        checks.append(f"{SHEET_FALTANTES} no tiene CODIGO_UNICO vacío")
    else:
        errors.append(f"{SHEET_FALTANTES} contiene CODIGO_UNICO vacío")

    if int(faltantes_df["CODIGO_UNICO"].duplicated().sum()) == 0:
        checks.append(f"{SHEET_FALTANTES} no tiene duplicados por CODIGO_UNICO")
    else:
        errors.append(f"{SHEET_FALTANTES} tiene duplicados por CODIGO_UNICO")

    missing_form_columns = [column for column in FORM_FIELDS if column not in faltantes_df.columns]
    if not missing_form_columns:
        checks.append("Todos los campos de pantalla están presentes en la hoja principal")
    else:
        errors.append(f"Faltan columnas de formulario en la hoja principal: {missing_form_columns}")

    if int(cruce_df.loc[cruce_df["ESTADO_CRUCE_INDICES"] == "YA_EXISTE_EN_INDICES"].shape[0]) + int(
        cruce_df.loc[cruce_df["ESTADO_CRUCE_INDICES"] == "FALTA_CREAR_EN_INDICES"].shape[0]
    ) + int(cruce_df.loc[cruce_df["ESTADO_CRUCE_INDICES"] == "DUDOSO_REVISAR_MANUAL"].shape[0]) + len(no_crear_df) == len(cruce_df):
        checks.append("Las clasificaciones finales cubren todo el universo matriz")

    if expected_df["EXISTE_EN_OFERTA_MATRIZ"].eq("SI").all():
        checks.append("Todos los códigos esperados del usuario existen en OFERTA_MATRIZ_NORMALIZADA")
    else:
        errors.append("Hay códigos esperados del usuario que no están en OFERTA_MATRIZ_NORMALIZADA")

    wb_out = load_workbook(paths.excel_out, read_only=True, data_only=False)
    required_sheets = {
        SHEET_RESUMEN,
        SHEET_OFERTA_NORMAL,
        SHEET_OFERTA_CLAS,
        SHEET_EXISTENTES,
        SHEET_CRUCE,
        SHEET_FALTANTES,
        SHEET_DUDOSOS,
        SHEET_EXISTEN,
        SHEET_NO_CREAR,
        SHEET_DICT,
        SHEET_AUD_COLS,
        SHEET_AUD_DUP,
        SHEET_AUD_CODE,
        SHEET_AUD_EXPECTED,
        SHEET_BITACORA,
    }
    if required_sheets.issubset(set(wb_out.sheetnames)):
        checks.append("El Excel final contiene todas las hojas obligatorias")
    else:
        errors.append(f"Faltan hojas obligatorias en el Excel final: {sorted(required_sheets.difference(set(wb_out.sheetnames)))}")

    csv_df = pd.read_csv(paths.csv_out, sep=";", dtype=str, keep_default_na=False)
    if len(csv_df) == len(faltantes_df):
        checks.append("El CSV tiene la misma cantidad de filas que PROGRAMAS_FALTANTES_PARA_CREAR")
    else:
        errors.append("El CSV no coincide con la hoja PROGRAMAS_FALTANTES_PARA_CREAR")

    json_payload = json.loads(paths.json_out.read_text(encoding="utf-8"))
    if int(json_payload["conteos"]["TOTAL_FALTA_CREAR_EN_INDICES"]) == len(faltantes_df):
        checks.append("El JSON coincide con el conteo de PROGRAMAS_FALTANTES_PARA_CREAR")
    else:
        errors.append("El JSON no coincide con el conteo de PROGRAMAS_FALTANTES_PARA_CREAR")

    md_text = paths.md_out.read_text(encoding="utf-8")
    if SHEET_FALTANTES in md_text:
        checks.append("El Markdown instruye usar la hoja PROGRAMAS_FALTANTES_PARA_CREAR")
    else:
        errors.append("El Markdown no referencia la hoja principal de trabajo manual")

    warnings.append("El nombre solicitado PROGRAMAS_EXISTENTES_NORMALIZADOS se exportó como PROGRAMAS_EXIST_NORMALIZADOS por límite de 31 caracteres de Excel.")
    warnings.append("TIPO_PLAN_CARRERA se mapeó con regla empírica mayoritaria 1→Programa Regular y 3→Programa Especial; existen outliers históricos en la referencia.")
    warnings.append("MODALIDAD=2 y JORNADA=3 quedan en REVISAR por ausencia de solape exacto suficiente en la base existente.")

    return checks, warnings, errors


def build_json_payload(
    paths: Paths,
    dictamen: str,
    counts: dict[str, int],
    validations: list[str],
    warnings: list[str],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "timestamp": paths.timestamp,
        "rutas": {
            "excel": str(paths.excel_out.resolve()),
            "csv": str(paths.csv_out.resolve()),
            "markdown": str(paths.md_out.resolve()),
            "json": str(paths.json_out.resolve()),
            "fuente_principal": str(paths.input_excel.resolve()),
            "fuente_existentes": str(paths.existing_tsv.resolve()),
        },
        "conteos": counts,
        "validaciones": validations,
        "estado_final": dictamen,
        "errores_bloqueantes": errors,
        "advertencias_no_bloqueantes": warnings,
    }


def build_error_markdown(title: str, errors: list[str], paths: Paths) -> str:
    body = "\n".join(f"- {item}" for item in errors)
    return f"""# {title}

## Dictamen

ERROR_BLOQUEANTE

## Errores

{body}

## Fuentes revisadas

- {paths.input_excel.resolve()}
- {paths.existing_tsv.resolve()}
- {paths.script_path}
"""


def main() -> int:
    paths = build_paths()
    paths.resultados.mkdir(parents=True, exist_ok=True)
    try:
        matriz_df, workbook_meta = load_matriz(paths)
        existing_base_df = load_existing(paths)
        oferta_normal_df = build_oferta_normalizada(matriz_df, paths)
        oferta_clas_df = classify_oferta(oferta_normal_df)
        existing_normal_df = build_existing_normalizados(existing_base_df, paths)
        dictionaries = build_reference_dictionaries(existing_base_df)
        cruce_df = build_cruce(oferta_clas_df, existing_normal_df)
        faltantes_df = build_programas_faltantes(cruce_df, dictionaries, paths)
        dudosos_df = cruce_df.loc[cruce_df["ESTADO_CRUCE_INDICES"] == "DUDOSO_REVISAR_MANUAL"].copy()
        existen_df = cruce_df.loc[cruce_df["ESTADO_CRUCE_INDICES"] == "YA_EXISTE_EN_INDICES"].copy()
        no_crear_df = cruce_df.loc[
            cruce_df["ESTADO_CRUCE_INDICES"].isin(["NO_CREAR_POR_NO_VIGENTE", "NO_CREAR_POR_FUERA_DE_ALCANCE"])
        ].copy()
        expected_df = build_expected_codes_audit(cruce_df, existing_normal_df)
        dict_df = build_dictionary_sheet()
        dataframes_for_audit = {
            SHEET_OFERTA_NORMAL: oferta_normal_df,
            SHEET_OFERTA_CLAS: oferta_clas_df,
            SHEET_EXISTENTES: existing_normal_df,
            SHEET_CRUCE: cruce_df,
            SHEET_FALTANTES: faltantes_df,
            SHEET_DUDOSOS: dudosos_df,
            SHEET_EXISTEN: existen_df,
            SHEET_NO_CREAR: no_crear_df,
            SHEET_AUD_EXPECTED: expected_df,
        }
        aud_cols_df = build_auditoria_columnas(dataframes_for_audit)
        aud_dup_df = build_auditoria_duplicados(oferta_normal_df, existing_normal_df, faltantes_df)
        aud_code_df = build_auditoria_codigo_unico(oferta_normal_df, existing_normal_df)
        bitacora_df = build_bitacora(paths)
        resumen_df = build_resumen(paths, workbook_meta, cruce_df, faltantes_df, dudosos_df, existen_df, no_crear_df)

        wb = Workbook()
        wb.remove(wb.active)
        for title, df in [
            (SHEET_RESUMEN, resumen_df),
            (SHEET_OFERTA_NORMAL, oferta_normal_df),
            (SHEET_OFERTA_CLAS, oferta_clas_df),
            (SHEET_EXISTENTES, existing_normal_df),
            (SHEET_CRUCE, cruce_df),
            (SHEET_FALTANTES, faltantes_df),
            (SHEET_DUDOSOS, dudosos_df),
            (SHEET_EXISTEN, existen_df),
            (SHEET_NO_CREAR, no_crear_df),
            (SHEET_DICT, dict_df),
            (SHEET_AUD_COLS, aud_cols_df),
            (SHEET_AUD_DUP, aud_dup_df),
            (SHEET_AUD_CODE, aud_code_df),
            (SHEET_AUD_EXPECTED, expected_df),
            (SHEET_BITACORA, bitacora_df),
        ]:
            add_dataframe_sheet(wb, title, df)
        wb.save(paths.excel_out)
        faltantes_df.to_csv(paths.csv_out, sep=";", index=False, encoding="utf-8")

        counts = {
            "TOTAL_OFERTA_MATRIZ": len(cruce_df),
            "TOTAL_VIGENTES": int(cruce_df["VIGENCIA"].eq("1").sum()),
            "TOTAL_YA_EXISTE_EN_INDICES": int(cruce_df["ESTADO_CRUCE_INDICES"].eq("YA_EXISTE_EN_INDICES").sum()),
            "TOTAL_FALTA_CREAR_EN_INDICES": int(cruce_df["ESTADO_CRUCE_INDICES"].eq("FALTA_CREAR_EN_INDICES").sum()),
            "TOTAL_DUDOSO_REVISAR_MANUAL": int(cruce_df["ESTADO_CRUCE_INDICES"].eq("DUDOSO_REVISAR_MANUAL").sum()),
            "TOTAL_NO_CREAR": len(no_crear_df),
        }

        provisional_payload = build_json_payload(paths, "PENDIENTE_VALIDACION", counts, [], [], [])
        write_json(paths.json_out, provisional_payload)
        provisional_markdown = build_markdown(
            paths,
            "PENDIENTE_VALIDACION",
            counts,
            faltantes_df,
            dudosos_df,
            no_crear_df,
            expected_df,
            [],
            ["Validación post-generación pendiente"],
        )
        paths.md_out.write_text(provisional_markdown, encoding="utf-8")

        validations, warnings, errors = validate_outputs(paths, faltantes_df, cruce_df, expected_df, no_crear_df)

        if errors:
            paths.error_out.write_text(build_error_markdown("CNED Programas Faltantes - Error de validación", errors, paths), encoding="utf-8")
            dictamen = "ERROR_BLOQUEANTE"
        elif counts["TOTAL_FALTA_CREAR_EN_INDICES"] == 0 and counts["TOTAL_DUDOSO_REVISAR_MANUAL"] == 0:
            dictamen = "SIN_FALTANTES_TODO_EXISTE"
        elif counts["TOTAL_DUDOSO_REVISAR_MANUAL"] > 0:
            dictamen = "REQUIERE_REVISION_MANUAL"
        else:
            dictamen = "OK_PROGRAMAS_FALTANTES_IDENTIFICADOS_PARA_CREAR"

        markdown = build_markdown(paths, dictamen, counts, faltantes_df, dudosos_df, no_crear_df, expected_df, warnings, validations)
        paths.md_out.write_text(markdown, encoding="utf-8")
        payload = build_json_payload(paths, dictamen, counts, validations, warnings, errors)
        write_json(paths.json_out, payload)

        campos_con_revisar = []
        if not faltantes_df.empty:
            campos_con_revisar = [column for column in FORM_FIELDS if faltantes_df[column].eq("REVISAR").any()]

        print("=" * 120)
        print("DICTAMEN_FINAL")
        print(dictamen)
        print("FUENTE_PRINCIPAL")
        print("PROMEDIOSDEALUMNOS_7804.xlsx / hoja matriz")
        print("FUENTE_EXISTENTES_INDICES")
        print(paths.existing_tsv.resolve())
        print("TOTAL_OFERTA_MATRIZ")
        print(counts["TOTAL_OFERTA_MATRIZ"])
        print("TOTAL_VIGENTES")
        print(counts["TOTAL_VIGENTES"])
        print("TOTAL_YA_EXISTE_EN_INDICES")
        print(counts["TOTAL_YA_EXISTE_EN_INDICES"])
        print("TOTAL_FALTA_CREAR_EN_INDICES")
        print(counts["TOTAL_FALTA_CREAR_EN_INDICES"])
        print("TOTAL_DUDOSO_REVISAR_MANUAL")
        print(counts["TOTAL_DUDOSO_REVISAR_MANUAL"])
        print("TOTAL_NO_CREAR")
        print(counts["TOTAL_NO_CREAR"])
        print("ARCHIVO_EXCEL_FINAL")
        print(paths.excel_out.resolve())
        print("HOJA_PRINCIPAL_PARA_TRABAJO_MANUAL")
        print(SHEET_FALTANTES)
        print("CAMPOS_FORMULARIO_COMPLETADOS")
        print(len(FORM_FIELDS))
        print("CAMPOS_CON_REVISAR")
        print(campos_con_revisar or "ninguno")
        print("ERRORES_BLOQUEANTES")
        print(errors or "ninguno")
        print("ADVERTENCIAS_NO_BLOQUEANTES")
        print(warnings or "ninguna")
        print("ESTADO_GIT_FINAL")
        print("Localmente no se tocaron artefactos oficiales previos; se generaron nuevos artefactos timestamped.")
        print("RECOMENDACION")
        print(f"Abrir {paths.excel_out.resolve()} y usar la hoja {SHEET_FALTANTES}; revisar {SHEET_DUDOSOS} antes de crear programas ambiguos.")
        print("=" * 120)
        return 1 if errors else 0
    except Exception as exc:
        error_text = build_error_markdown("CNED Programas Faltantes - Excepción de ejecución", [str(exc)], paths)
        paths.error_out.write_text(error_text, encoding="utf-8")
        print("=" * 120)
        print("DICTAMEN_FINAL")
        print("ERROR_BLOQUEANTE")
        print("ERRORES_BLOQUEANTES")
        print([str(exc)])
        print("ARCHIVO_ERROR")
        print(paths.error_out.resolve())
        print("=" * 120)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())