#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria tecnico-funcional Avance Curricular SIES 2026.

Subproyecto: validacion fila a fila de columnas 16-21 del archivo 5809.
Foco principal: demostrar si columnas 16-19 se respaldan con registros ANO=2025.

Reglas incorporadas:
- No modifica fuentes originales ni CSV 5809 original.
- Lee el CSV 5809 sin encabezado, separador ;, encoding cp1252.
- Lee todas las hojas de PROMEDIOSDEALUMNOS y audita Hoja1 como detalle.
- Impide usar CODCLI, RUT, NUM_DOCUMENTO, DV, ANO, PERIODO o identificadores como NOTA.
- Separa columnas anuales 2025 de columnas acumuladas hasta cierre 2025.
- Genera Excel, Markdown y manifest JSON, y copia los tres al Escritorio.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import sys
import unicodedata
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import pandas as pd

try:
    from openpyxl.utils.exceptions import IllegalCharacterError
except Exception:  # pragma: no cover
    IllegalCharacterError = Exception


REPO_ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
SOURCE_XLSX = REPO_ROOT / (
    "avance_curricular_2026/25_actualizacion_fuente_promedios/"
    "CAMBIO_PROMEDIOSDEALUMNOS_20260704_221059/00_FUENTE_CONGELADA/"
    "PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_20260704_221059.xlsx"
)
SOURCE_CSV_5809 = REPO_ROOT / (
    "avance_curricular_2026/14_sies_ready_5809/"
    "SIES_READY_TECNICO_5809_22_COLUMNAS_20260704_151418/"
    "01_ARCHIVO_SIES_READY_TECNICO/"
    "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_TECNICO.csv"
)
OUTPUT_DIR = REPO_ROOT / "avance_curricular_2026/29_auditoria_corregida_logica_2025_5809"

EXCEL_NAME = "AUDITORIA_CORREGIDA_LOGICA_2025_5809.xlsx"
MD_NAME = "INFORME_AUDITORIA_CORREGIDA_LOGICA_2025_5809.md"
MANIFEST_NAME = "manifest_auditoria_corregida_logica_2025_5809.json"

CSV_5809_COLUMNS = [
    "CODIGO_IES_NUM",
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

EXPECTED_SHEETS = [
    "DICTAMEN_GLOBAL",
    "VALIDACIONES",
    "COLUMNAS_DETECTADAS",
    "CATALOGO_ESTADO",
    "MAPEO_CODCLI_RUT",
    "AUDITORIA_ANUAL_2025_FILA_A_FILA",
    "FILAS_REVISAR_ANUAL_2025",
    "RESUMEN_ANUAL_2025",
    "AUDITORIA_ACUMULADO_2025_FILA_A_FILA",
    "FILAS_REVISAR_ACUMULADO_2025",
    "RESUMEN_ACUMULADO_2025",
    "LOGICA_AUDITADA",
    "FUENTES",
]

CRITICAL_COLUMNS = [
    "CODCLI",
    "ANO",
    "PERIODO",
    "CODRAMO_ASIGNATURA",
    "ESTADO",
]

FORBIDDEN_NOTE_NORMALIZED = {
    "CODCLI",
    "RUT",
    "NUMDOCUMENTO",
    "NUMERODOCUMENTO",
    "DOCUMENTO",
    "DV",
    "DIG",
    "DIGITO",
    "DIGITOVERIFICADOR",
    "ANO",
    "ANIO",
    "PERIODO",
}


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text


def normalize_col_name(value: Any) -> str:
    text = normalize_text(value).upper()
    return re.sub(r"[^A-Z0-9]+", "", text)


def clean_key(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if value.is_integer():
            return str(int(value))
    text = str(value).strip()
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    if re.fullmatch(r"\d+\.0", text):
        return text[:-2]
    return text


def normalize_rut(num: Any, dv: Any = None) -> str:
    raw_num = clean_key(num).upper()
    raw_dv = clean_key(dv).upper()
    if not raw_num:
        return ""
    if "-" in raw_num and not raw_dv:
        left, right = raw_num.rsplit("-", 1)
        raw_num, raw_dv = left, right
    raw_num = re.sub(r"[^0-9K]", "", raw_num)
    raw_dv = re.sub(r"[^0-9K]", "", raw_dv)
    if not raw_num:
        return ""
    if raw_dv:
        return f"{raw_num}-{raw_dv[-1]}"
    return raw_num


def numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", ".", regex=False).str.strip(),
        errors="coerce",
    )


def to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = clean_key(value)
    if text == "":
        return None
    try:
        return int(float(text.replace(",", ".")))
    except Exception:
        return None


def normalize_si_no(value: Any) -> str:
    text = normalize_text(value).strip().upper()
    if text in {"SI", "SÍ", "S", "1", "TRUE", "VERDADERO"}:
        return "SI"
    if text in {"NO", "N", "0", "FALSE", "FALSO"}:
        return "NO"
    return text


def bool_to_si_no(value: bool) -> str:
    return "SI" if value else "NO"


def safe_join(values: Iterable[Any], sep: str = " | ") -> str:
    cleaned = [clean_key(v) for v in values if clean_key(v)]
    return sep.join(cleaned)


def sanitize_excel_value(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", value)
    return value


def sanitize_df_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].map(sanitize_excel_value)
    return out


def list_candidate_columns(columns: Sequence[Any], category: str) -> List[str]:
    candidates: List[str] = []
    for col in columns:
        if col is None or str(col).strip() == "":
            continue
        raw = str(col)
        norm = normalize_col_name(raw)
        if category == "CODCLI":
            ok = norm in {"CODCLI", "CODCLIENTE", "CODALUMNO"} or "CODCLI" in norm
        elif category == "RUT":
            ok = "RUT" in norm
        elif category == "DV":
            ok = norm in {"DV", "DIG", "DIGITO", "DIGITOVERIFICADOR", "DVRUT"}
        elif category == "ANO":
            ok = norm in {"ANO", "ANIO", "ANHO"} or norm.startswith("ANO")
        elif category == "PERIODO":
            ok = "PERIODO" in norm or "SEMESTRE" in norm or norm in {"SEM", "SEMES"}
        elif category == "CODRAMO_ASIGNATURA":
            ok = "CODRAMO" in norm or "RAMO" in norm or "ASIGNAT" in norm or "CURSO" in norm
        elif category == "ESTADO":
            ok = "ESTADO" in norm or "SITUACION" in norm
        elif category == "NOTA":
            ok = "NOTA" in norm or "PROMEDIO" in norm or "CALIFIC" in norm
        else:
            ok = False
        if ok:
            candidates.append(raw)
    return candidates


def detect_best_column(
    columns: Sequence[Any],
    preferred: Sequence[str],
    candidates: Sequence[str],
    exclude_norm_contains: Sequence[str] = (),
) -> Optional[str]:
    col_by_norm = {normalize_col_name(c): str(c) for c in columns if c is not None}
    for wanted in preferred:
        norm = normalize_col_name(wanted)
        if norm in col_by_norm:
            return col_by_norm[norm]
    for cand in candidates:
        norm = normalize_col_name(cand)
        if any(token in norm for token in exclude_norm_contains):
            continue
        return str(cand)
    return None


def identifier_like_ratio(series: pd.Series) -> float:
    values = [clean_key(v) for v in series.dropna().head(5000)]
    values = [v for v in values if v != ""]
    if not values:
        return 0.0
    id_count = 0
    for text in values:
        compact = re.sub(r"[^A-Za-z0-9Kk]", "", text)
        upper = compact.upper()
        numeric = re.sub(r"[^0-9]", "", compact)
        has_alpha = bool(re.search(r"[A-Za-z]", compact))
        has_digit = bool(re.search(r"\d", compact))
        looks_rut = bool(re.fullmatch(r"\d{6,9}[0-9K]?", upper))
        looks_long_numeric = bool(re.fullmatch(r"\d{5,}", numeric)) and len(compact) >= 5
        looks_alnum_code = has_alpha and has_digit and len(compact) >= 6
        looks_long_unique = len(compact) >= 10 and has_digit
        if looks_rut or looks_long_numeric or looks_alnum_code or looks_long_unique:
            id_count += 1
    return id_count / len(values)


def evaluate_note_candidate(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    norm = normalize_col_name(column)
    if norm in FORBIDDEN_NOTE_NORMALIZED:
        return {
            "columna": column,
            "valida": False,
            "motivo": "Nombre prohibido para NOTA por regla de auditoria",
            "identifier_like_ratio": None,
            "escala": "",
            "pct_escala_1_7": None,
            "pct_escala_100_700": None,
        }
    if any(forbidden in norm for forbidden in FORBIDDEN_NOTE_NORMALIZED):
        return {
            "columna": column,
            "valida": False,
            "motivo": "Nombre contiene identificador o columna temporal prohibida",
            "identifier_like_ratio": None,
            "escala": "",
            "pct_escala_1_7": None,
            "pct_escala_100_700": None,
        }
    id_ratio = identifier_like_ratio(df[column])
    if id_ratio > 0.80:
        return {
            "columna": column,
            "valida": False,
            "motivo": "Mas de 80% de valores parecen identificadores",
            "identifier_like_ratio": round(id_ratio, 4),
            "escala": "",
            "pct_escala_1_7": None,
            "pct_escala_100_700": None,
        }
    nums = numeric_series(df[column]).dropna()
    if nums.empty:
        return {
            "columna": column,
            "valida": False,
            "motivo": "No contiene valores numericos evaluables como nota",
            "identifier_like_ratio": round(id_ratio, 4),
            "escala": "",
            "pct_escala_1_7": 0.0,
            "pct_escala_100_700": 0.0,
        }
    pct_1_7 = float(((nums >= 1) & (nums <= 7)).mean())
    pct_100_700 = float(((nums >= 100) & (nums <= 700)).mean())
    if pct_1_7 >= 0.80:
        return {
            "columna": column,
            "valida": True,
            "motivo": "Valores compatibles con escala 1 a 7; umbral interno >=80%",
            "identifier_like_ratio": round(id_ratio, 4),
            "escala": "1_7",
            "pct_escala_1_7": round(pct_1_7, 4),
            "pct_escala_100_700": round(pct_100_700, 4),
        }
    if pct_100_700 >= 0.80:
        return {
            "columna": column,
            "valida": True,
            "motivo": "Valores compatibles con escala 100 a 700; umbral interno >=80%",
            "identifier_like_ratio": round(id_ratio, 4),
            "escala": "100_700",
            "pct_escala_1_7": round(pct_1_7, 4),
            "pct_escala_100_700": round(pct_100_700, 4),
        }
    return {
        "columna": column,
        "valida": False,
        "motivo": "No alcanza compatibilidad minima con escala 1-7 ni 100-700",
        "identifier_like_ratio": round(id_ratio, 4),
        "escala": "",
        "pct_escala_1_7": round(pct_1_7, 4),
        "pct_escala_100_700": round(pct_100_700, 4),
    }


def classify_estado(value: Any) -> Tuple[str, str]:
    text = normalize_text(value).upper()
    text = re.sub(r"\s+", " ", text).strip()
    if text == "":
        return "NO_CLASIFICADO", "Estado vacio"

    no_patterns = [
        ("REPROB", "contiene REPROB"),
        (r"\bREP\b", "contiene REP"),
        (r"NO\s+APROB", "contiene NO APROB"),
        (r"\bNCR\b", "contiene NCR"),
    ]
    yes_patterns = [
        (r"(?<!NO\s)APROB", "contiene APROB"),
        (r"\bAPR\b", "contiene APR"),
        ("CONVALID", "contiene CONVALID"),
        ("HOMOLOG", "contiene HOMOLOG"),
        ("RECONOC", "contiene RECONOC"),
    ]

    no_hits = [crit for pat, crit in no_patterns if re.search(pat, text)]
    yes_hits = [crit for pat, crit in yes_patterns if re.search(pat, text)]
    if yes_hits and no_hits:
        return "NO_CLASIFICADO", "Senales contradictorias: " + "; ".join(yes_hits + no_hits)
    if yes_hits:
        return "APROBADO", "; ".join(yes_hits)
    if no_hits:
        return "NO_APROBADO", "; ".join(no_hits)
    return "NO_CLASIFICADO", "Sin patron explicito permitido"


def detect_columns_for_hoja1(hoja1: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
    cols = list(hoja1.columns)
    candidates = {
        "CODCLI": list_candidate_columns(cols, "CODCLI"),
        "RUT": list_candidate_columns(cols, "RUT"),
        "DV": list_candidate_columns(cols, "DV"),
        "ANO": list_candidate_columns(cols, "ANO"),
        "PERIODO": list_candidate_columns(cols, "PERIODO"),
        "CODRAMO_ASIGNATURA": list_candidate_columns(cols, "CODRAMO_ASIGNATURA"),
        "ESTADO": list_candidate_columns(cols, "ESTADO"),
        "NOTA": list_candidate_columns(cols, "NOTA"),
    }
    selected: Dict[str, Any] = {}
    selected["CODCLI"] = detect_best_column(cols, ["CODCLI"], candidates["CODCLI"])
    selected["RUT"] = detect_best_column(cols, ["RUT"], candidates["RUT"], ["RESPONSABLE", "EJECUTIVO"])
    selected["DV"] = detect_best_column(cols, ["DIG", "DV"], candidates["DV"])
    selected["ANO"] = detect_best_column(cols, ["ANO", "ANIO"], candidates["ANO"], ["INGRESO", "MATRICULA", "EGRESO"])
    selected["PERIODO"] = detect_best_column(cols, ["PERIODO"], candidates["PERIODO"], ["INGRESO", "MATRICULA"])
    selected["CODRAMO_ASIGNATURA"] = detect_best_column(
        cols,
        ["CODRAMO", "RAMOEQUIV", "ASIGNATURA"],
        candidates["CODRAMO_ASIGNATURA"],
    )

    # Preferimos una columna de estado con texto explicitamente clasificable.
    estado_candidates = candidates["ESTADO"]
    best_estado = None
    best_score = -1.0
    estado_eval_rows: List[Dict[str, Any]] = []
    for cand in estado_candidates:
        sample = hoja1[cand].dropna()
        if sample.empty:
            score = 0.0
        else:
            cls = sample.map(lambda x: classify_estado(x)[0])
            score = float((cls != "NO_CLASIFICADO").mean())
        estado_eval_rows.append(
            {
                "columna": cand,
                "pct_valores_clasificables_patrones_explicitos": round(score, 4),
                "motivo": "evaluacion por patrones APROB/CONVALID/HOMOLOG/RECONOC y REPROB/REP/NO APROB/NCR",
            }
        )
        if score > best_score:
            best_score = score
            best_estado = cand
    selected["ESTADO"] = best_estado
    selected["ESTADO_DETECCION_MOTIVO"] = (
        "Seleccionada por mayor porcentaje de valores clasificables con patrones explicitos"
        if best_estado
        else "No detectada"
    )

    note_evals: List[Dict[str, Any]] = []
    for cand in candidates["NOTA"]:
        note_evals.append(evaluate_note_candidate(hoja1, cand))
    valid_notes = [row for row in note_evals if row["valida"]]
    selected["NOTA"] = valid_notes[0]["columna"] if valid_notes else None
    selected["NOTA_ESCALA"] = valid_notes[0]["escala"] if valid_notes else ""
    selected["NOTA_DETECCION_MOTIVO"] = (
        valid_notes[0]["motivo"] if valid_notes else "No existe nota valida segun reglas"
    )
    selected["CANDIDATAS"] = candidates
    selected["EVALUACION_NOTA"] = note_evals
    selected["EVALUACION_ESTADO"] = estado_eval_rows
    return selected, pd.DataFrame(estado_eval_rows + note_evals)


def build_column_diagnostics(sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for sheet, df in sheets.items():
        cols = [str(c) for c in df.columns if c is not None and str(c).strip() != ""]
        rows.append(
            {
                "hoja": sheet,
                "cantidad_filas": int(len(df)),
                "cantidad_columnas": int(len(df.columns)),
                "lista_columnas": safe_join(cols),
                "candidatas_CODCLI": safe_join(list_candidate_columns(cols, "CODCLI")),
                "candidatas_RUT": safe_join(list_candidate_columns(cols, "RUT")),
                "candidatas_DV": safe_join(list_candidate_columns(cols, "DV")),
                "candidatas_ANO": safe_join(list_candidate_columns(cols, "ANO")),
                "candidatas_PERIODO": safe_join(list_candidate_columns(cols, "PERIODO")),
                "candidatas_CODRAMO_ASIGNATURA": safe_join(
                    list_candidate_columns(cols, "CODRAMO_ASIGNATURA")
                ),
                "candidatas_ESTADO": safe_join(list_candidate_columns(cols, "ESTADO")),
                "candidatas_NOTA": safe_join(list_candidate_columns(cols, "NOTA")),
            }
        )
    return pd.DataFrame(rows)


def build_catalogo_estado(df: pd.DataFrame, estado_col: Optional[str]) -> pd.DataFrame:
    if not estado_col:
        return pd.DataFrame(
            [
                {
                    "valor_original_ESTADO": "",
                    "frecuencia": 0,
                    "clasificacion_propuesta": "NO_CLASIFICADO",
                    "criterio_usado": "No se detecto columna ESTADO",
                }
            ]
        )
    counts = df[estado_col].fillna("").map(lambda x: normalize_text(x).strip()).value_counts(dropna=False)
    rows: List[Dict[str, Any]] = []
    for value, freq in counts.items():
        cls, criterio = classify_estado(value)
        rows.append(
            {
                "valor_original_ESTADO": value,
                "frecuencia": int(freq),
                "clasificacion_propuesta": cls,
                "criterio_usado": criterio,
            }
        )
    return pd.DataFrame(rows)


def normalize_source_rut(row: pd.Series, rut_col: Optional[str], dv_col: Optional[str]) -> str:
    if not rut_col:
        return ""
    dv = row[dv_col] if dv_col and dv_col in row.index else None
    return normalize_rut(row[rut_col], dv)


def detect_mapping_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    cols = list(df.columns)
    codcli = detect_best_column(cols, ["CODCLI"], list_candidate_columns(cols, "CODCLI"))
    rut = detect_best_column(cols, ["RUT"], list_candidate_columns(cols, "RUT"), ["RESPONSABLE", "EJECUTIVO"])
    dv = detect_best_column(cols, ["DIG", "DV"], list_candidate_columns(cols, "DV"))
    return {"CODCLI": codcli, "RUT": rut, "DV": dv}


def build_mapping(sheets: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    priority = [("Hoja1", 1), ("DatosAlumnos", 2), ("Matricula_2025", 3)]
    evidence_rows: List[Dict[str, Any]] = []
    for sheet_name, prio in priority:
        if sheet_name not in sheets:
            continue
        df = sheets[sheet_name]
        cols = detect_mapping_columns(df)
        if not cols["CODCLI"] or not cols["RUT"]:
            continue
        temp = pd.DataFrame(
            {
                "CODCLI": df[cols["CODCLI"]].map(clean_key),
                "RUT_NORMALIZADO": [
                    normalize_source_rut(row, cols["RUT"], cols["DV"])
                    for _, row in df[[c for c in [cols["RUT"], cols["DV"]] if c]].iterrows()
                ],
            }
        )
        temp = temp[(temp["CODCLI"] != "") & (temp["RUT_NORMALIZADO"] != "")]
        grouped = temp.groupby(["CODCLI", "RUT_NORMALIZADO"], dropna=False).size().reset_index(name="cantidad_apariciones")
        for _, row in grouped.iterrows():
            evidence_rows.append(
                {
                    "CODCLI": row["CODCLI"],
                    "RUT_NORMALIZADO": row["RUT_NORMALIZADO"],
                    "hoja_origen": sheet_name,
                    "prioridad_origen": prio,
                    "cantidad_apariciones": int(row["cantidad_apariciones"]),
                }
            )

    evidence = pd.DataFrame(evidence_rows)
    if evidence.empty:
        return evidence, {}

    selected_rows: List[pd.DataFrame] = []
    for _, group in evidence.groupby("CODCLI", dropna=False):
        min_prio = group["prioridad_origen"].min()
        selected_rows.append(group[group["prioridad_origen"] == min_prio])
    mapping = pd.concat(selected_rows, ignore_index=True)

    codcli_to_ruts = mapping.groupby("CODCLI")["RUT_NORMALIZADO"].nunique(dropna=True).to_dict()
    rut_to_codclis = mapping.groupby("RUT_NORMALIZADO")["CODCLI"].nunique(dropna=True).to_dict()
    mapping["conflicto_rut_mismo_codcli"] = mapping["CODCLI"].map(lambda x: "SI" if codcli_to_ruts.get(x, 0) > 1 else "NO")
    mapping["multiples_codcli_mismo_rut"] = mapping["RUT_NORMALIZADO"].map(
        lambda x: "SI" if rut_to_codclis.get(x, 0) > 1 else "NO"
    )

    rut_to_codcli_list: Dict[str, List[str]] = defaultdict(list)
    for _, row in mapping.sort_values(["RUT_NORMALIZADO", "CODCLI"]).iterrows():
        rut_to_codcli_list[row["RUT_NORMALIZADO"]].append(row["CODCLI"])
    rut_to_codcli_list = {rut: sorted(set(codes)) for rut, codes in rut_to_codcli_list.items()}

    ordered_cols = [
        "CODCLI",
        "RUT_NORMALIZADO",
        "hoja_origen",
        "cantidad_apariciones",
        "conflicto_rut_mismo_codcli",
        "multiples_codcli_mismo_rut",
        "prioridad_origen",
    ]
    return mapping[ordered_cols], rut_to_codcli_list


def prepare_hoja1(
    hoja1: pd.DataFrame,
    selected: Dict[str, Any],
) -> pd.DataFrame:
    df = hoja1.copy()
    codcli_col = selected.get("CODCLI")
    ano_col = selected.get("ANO")
    periodo_col = selected.get("PERIODO")
    course_col = selected.get("CODRAMO_ASIGNATURA")
    estado_col = selected.get("ESTADO")
    nota_col = selected.get("NOTA")
    nota_escala = selected.get("NOTA_ESCALA")

    df["_CODCLI_KEY"] = df[codcli_col].map(clean_key) if codcli_col else ""
    df["_ANO_INT"] = numeric_series(df[ano_col]).astype("Int64") if ano_col else pd.Series([pd.NA] * len(df), dtype="Int64")
    df["_PERIODO_INT"] = (
        numeric_series(df[periodo_col]).astype("Int64") if periodo_col else pd.Series([pd.NA] * len(df), dtype="Int64")
    )
    df["_COURSE_KEY"] = df[course_col].map(clean_key) if course_col else ""
    if estado_col:
        df["_ESTADO_ORIG"] = df[estado_col].map(lambda x: normalize_text(x).strip())
        estado_class = df["_ESTADO_ORIG"].map(classify_estado)
        df["_ESTADO_CLASIFICACION"] = estado_class.map(lambda x: x[0])
        df["_ESTADO_CRITERIO"] = estado_class.map(lambda x: x[1])
    else:
        df["_ESTADO_ORIG"] = ""
        df["_ESTADO_CLASIFICACION"] = "NO_CLASIFICADO"
        df["_ESTADO_CRITERIO"] = "No se detecto columna ESTADO"

    if nota_col:
        df["_NOTA_NUM"] = numeric_series(df[nota_col])
    else:
        df["_NOTA_NUM"] = pd.Series([pd.NA] * len(df), dtype="Float64")

    if nota_col and nota_escala == "1_7":
        df["_NOTA_APOYA_APROBADO"] = df["_NOTA_NUM"] >= 4.0
    elif nota_col and nota_escala == "100_700":
        df["_NOTA_APOYA_APROBADO"] = df["_NOTA_NUM"] >= 400.0
    else:
        df["_NOTA_APOYA_APROBADO"] = False

    df["_APROBADO_CALC"] = (df["_ESTADO_CLASIFICACION"] == "APROBADO") | (
        (df["_ESTADO_CLASIFICACION"] == "NO_CLASIFICADO") & df["_NOTA_APOYA_APROBADO"]
    )
    return df


def aggregate_by_codcli(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    metrics: Dict[str, Dict[str, Any]] = {}
    valid = df[df["_CODCLI_KEY"] != ""]
    for codcli, group in valid.groupby("_CODCLI_KEY", dropna=False):
        g2025 = group[group["_ANO_INT"] == 2025]
        g2026 = group[group["_ANO_INT"] == 2026]
        gle2025 = group[group["_ANO_INT"].notna() & (group["_ANO_INT"] <= 2025)]
        courses_2025 = set(g2025.loc[g2025["_COURSE_KEY"] != "", "_COURSE_KEY"])
        approved_2025 = set(g2025.loc[(g2025["_COURSE_KEY"] != "") & (g2025["_APROBADO_CALC"]), "_COURSE_KEY"])
        unclassified_2025 = set(
            g2025.loc[
                (g2025["_COURSE_KEY"] != "") & (g2025["_ESTADO_CLASIFICACION"] == "NO_CLASIFICADO"),
                "_COURSE_KEY",
            ]
        )
        courses_le2025 = set(gle2025.loc[gle2025["_COURSE_KEY"] != "", "_COURSE_KEY"])
        approved_le2025 = set(
            gle2025.loc[(gle2025["_COURSE_KEY"] != "") & (gle2025["_APROBADO_CALC"]), "_COURSE_KEY"]
        )
        periods_2025 = set(int(x) for x in g2025["_PERIODO_INT"].dropna().tolist())
        metrics[str(codcli)] = {
            "registros_2025": int(len(g2025)),
            "registros_2026": int(len(g2026)),
            "periodos_2025": periods_2025,
            "courses_2025": courses_2025,
            "approved_2025": approved_2025,
            "unclassified_courses_2025": unclassified_2025,
            "courses_le2025": courses_le2025,
            "approved_le2025": approved_le2025,
        }
    return metrics


def union_metrics(codclis: Sequence[str], metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    result = {
        "registros_2025": 0,
        "registros_2026": 0,
        "periodos_2025": set(),
        "courses_2025": set(),
        "approved_2025": set(),
        "unclassified_courses_2025": set(),
        "courses_le2025": set(),
        "approved_le2025": set(),
    }
    for codcli in codclis:
        item = metrics.get(codcli)
        if not item:
            continue
        result["registros_2025"] += item["registros_2025"]
        result["registros_2026"] += item["registros_2026"]
        for key in [
            "periodos_2025",
            "courses_2025",
            "approved_2025",
            "unclassified_courses_2025",
            "courses_le2025",
            "approved_le2025",
        ]:
            result[key] = result[key] | set(item[key])
    return result


def detect_b2_plan_key(hoja1_proc: pd.DataFrame, csv_5809: pd.DataFrame) -> Dict[str, Any]:
    source_candidates = [c for c in hoja1_proc.columns if normalize_col_name(c) in {"CODIGOUNICO", "PLANESTUDIOS", "PLANDEESTUDIO"}]
    checks: List[Dict[str, Any]] = []
    pairs = [
        ("CODIGO_UNICO", "CODIGO_UNICO"),
        ("PLAN_ESTUDIOS", "PLAN_ESTUDIOS"),
        ("PLAN_ESTUDIOS", "PLAN_DE_ESTUDIO"),
    ]
    for out_col, src_col in pairs:
        if out_col not in csv_5809.columns or src_col not in hoja1_proc.columns:
            checks.append(
                {
                    "columna_5809": out_col,
                    "columna_hoja1": src_col,
                    "ejecutable": "NO",
                    "interseccion_valores": 0,
                    "motivo": "Columna no disponible en ambas fuentes",
                }
            )
            continue
        out_vals = set(csv_5809[out_col].map(clean_key))
        src_vals = set(hoja1_proc[src_col].map(clean_key))
        out_vals.discard("")
        src_vals.discard("")
        overlap = out_vals & src_vals
        checks.append(
            {
                "columna_5809": out_col,
                "columna_hoja1": src_col,
                "ejecutable": "SI" if overlap else "NO",
                "interseccion_valores": len(overlap),
                "motivo": "Existe interseccion directa de valores" if overlap else "Sin interseccion directa de valores",
            }
        )
        if overlap:
            return {
                "ejecutable": True,
                "output_col": out_col,
                "source_col": src_col,
                "checks": checks,
                "reason": f"B2 ejecutable con llave directa {out_col} <-> {src_col}",
            }
    return {
        "ejecutable": False,
        "output_col": None,
        "source_col": None,
        "checks": checks,
        "reason": (
            "No existe llave plan/carrera directa compatible entre 5809 y Hoja1. "
            "CODIGO_UNICO no existe en Hoja1; PLAN_ESTUDIOS del 5809 no intersecta con PLAN_DE_ESTUDIO de Hoja1."
        ),
    }


def aggregate_b2_by_codcli_and_plan(
    hoja1_proc: pd.DataFrame,
    source_plan_col: str,
) -> Dict[Tuple[str, str], Dict[str, Set[str]]]:
    metrics: Dict[Tuple[str, str], Dict[str, Set[str]]] = {}
    valid = hoja1_proc[(hoja1_proc["_CODCLI_KEY"] != "") & (hoja1_proc[source_plan_col].map(clean_key) != "")]
    for (codcli, plan), group in valid.groupby(["_CODCLI_KEY", source_plan_col], dropna=False):
        gle2025 = group[group["_ANO_INT"].notna() & (group["_ANO_INT"] <= 2025)]
        courses = set(gle2025.loc[gle2025["_COURSE_KEY"] != "", "_COURSE_KEY"])
        approved = set(gle2025.loc[(gle2025["_COURSE_KEY"] != "") & (gle2025["_APROBADO_CALC"]), "_COURSE_KEY"])
        metrics[(str(codcli), clean_key(plan))] = {"courses": courses, "approved": approved}
    return metrics


def audit_rows(
    csv_5809: pd.DataFrame,
    rut_to_codcli_list: Dict[str, List[str]],
    metrics_by_codcli: Dict[str, Dict[str, Any]],
    b2_info: Dict[str, Any],
    hoja1_proc: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    annual_rows: List[Dict[str, Any]] = []
    accum_rows: List[Dict[str, Any]] = []

    b2_metrics: Dict[Tuple[str, str], Dict[str, Set[str]]] = {}
    if b2_info.get("ejecutable"):
        b2_metrics = aggregate_b2_by_codcli_and_plan(hoja1_proc, b2_info["source_col"])

    for idx, row in csv_5809.iterrows():
        rut = normalize_rut(row["NUM_DOCUMENTO"], row["DV"])
        codclis = rut_to_codcli_list.get(rut, [])
        metric = union_metrics(codclis, metrics_by_codcli)

        calc_curso_1 = bool_to_si_no(1 in metric["periodos_2025"])
        calc_curso_2 = bool_to_si_no(2 in metric["periodos_2025"])
        calc_cursadas_2025 = len(metric["courses_2025"])
        calc_aprobadas_2025 = len(metric["approved_2025"])
        calc_cursadas_b1 = len(metric["courses_le2025"])
        calc_aprobadas_b1 = len(metric["approved_le2025"])

        orig_curso_1 = normalize_si_no(row["CURSO_1ER_SEM"])
        orig_curso_2 = normalize_si_no(row["CURSO_2DO_SEM"])
        orig_cursadas_2025 = to_int(row["UNIDADES_CURSADAS"])
        orig_aprobadas_2025 = to_int(row["UNIDADES_APROBADAS"])
        orig_cursadas_total = to_int(row["UNID_CURSADAS_TOTAL"])
        orig_aprobadas_total = to_int(row["UNID_APROBADAS_TOTAL"])

        ok_curso_1 = orig_curso_1 == calc_curso_1
        ok_curso_2 = orig_curso_2 == calc_curso_2
        ok_cursadas_2025 = orig_cursadas_2025 == calc_cursadas_2025
        ok_aprobadas_2025 = orig_aprobadas_2025 == calc_aprobadas_2025
        unclassified_count = len(metric["unclassified_courses_2025"])
        tiene_2025 = metric["registros_2025"] > 0
        tiene_2026 = metric["registros_2026"] > 0

        if not codclis:
            dictamen = "BLOQUEO_SIN_CODCLI_ASOCIADO"
        elif not tiene_2025:
            dictamen = "BLOQUEO_SIN_EVIDENCIA_2025"
        elif unclassified_count > 0:
            dictamen = "BLOQUEO_ESTADO_NO_CLASIFICADO"
        elif ok_curso_1 and ok_curso_2 and ok_cursadas_2025 and ok_aprobadas_2025 and tiene_2026:
            dictamen = "OK_ANUAL_2025_CALZA_PERO_CODCLI_TAMBIEN_TIENE_2026"
        elif ok_curso_1 and ok_curso_2 and ok_cursadas_2025 and ok_aprobadas_2025:
            dictamen = "OK_ANUAL_2025_CALZA"
        else:
            dictamen = "DIFERENCIA_ANUAL_2025"

        annual_rows.append(
            {
                "FILA_5809": idx + 1,
                "RUT_NORMALIZADO": rut,
                "CODCLI_LISTA": safe_join(codclis, ";"),
                "CODCLI_CANTIDAD": len(codclis),
                "CODIGO_UNICO": row["CODIGO_UNICO"],
                "PLAN_ESTUDIOS": row["PLAN_ESTUDIOS"],
                "CURSO_1ER_SEM original": row["CURSO_1ER_SEM"],
                "CURSO_1ER_SEM_CALC": calc_curso_1,
                "OK_CURSO_1ER_SEM": "SI" if ok_curso_1 else "NO",
                "CURSO_2DO_SEM original": row["CURSO_2DO_SEM"],
                "CURSO_2DO_SEM_CALC": calc_curso_2,
                "OK_CURSO_2DO_SEM": "SI" if ok_curso_2 else "NO",
                "UNIDADES_CURSADAS original": row["UNIDADES_CURSADAS"],
                "UNIDADES_CURSADAS_2025_CALC": calc_cursadas_2025,
                "DIF_UNIDADES_CURSADAS_2025": (
                    None if orig_cursadas_2025 is None else calc_cursadas_2025 - orig_cursadas_2025
                ),
                "OK_UNIDADES_CURSADAS_2025": "SI" if ok_cursadas_2025 else "NO",
                "UNIDADES_APROBADAS original": row["UNIDADES_APROBADAS"],
                "UNIDADES_APROBADAS_2025_CALC": calc_aprobadas_2025,
                "DIF_UNIDADES_APROBADAS_2025": (
                    None if orig_aprobadas_2025 is None else calc_aprobadas_2025 - orig_aprobadas_2025
                ),
                "OK_UNIDADES_APROBADAS_2025": "SI" if ok_aprobadas_2025 else "NO",
                "REGISTROS_2025": metric["registros_2025"],
                "REGISTROS_2026_MISMO_CODCLI": metric["registros_2026"],
                "TIENE_EVIDENCIA_2025": "SI" if tiene_2025 else "NO",
                "TIENE_EVIDENCIA_2026_MISMO_CODCLI": "SI" if tiene_2026 else "NO",
                "ESTADOS_NO_CLASIFICADOS_2025_DISTINTOS_CURSOS": unclassified_count,
                "DICTAMEN_ANUAL_2025": dictamen,
            }
        )

        ok_b1_cursadas = orig_cursadas_total == calc_cursadas_b1
        ok_b1_aprobadas = orig_aprobadas_total == calc_aprobadas_b1

        if b2_info.get("ejecutable"):
            b2_courses: Set[str] = set()
            b2_approved: Set[str] = set()
            plan_value = clean_key(row[b2_info["output_col"]])
            for codcli in codclis:
                item = b2_metrics.get((codcli, plan_value), {"courses": set(), "approved": set()})
                b2_courses |= set(item["courses"])
                b2_approved |= set(item["approved"])
            calc_cursadas_b2: Any = len(b2_courses)
            calc_aprobadas_b2: Any = len(b2_approved)
            ok_b2_cursadas: Any = "SI" if orig_cursadas_total == calc_cursadas_b2 else "NO"
            ok_b2_aprobadas: Any = "SI" if orig_aprobadas_total == calc_aprobadas_b2 else "NO"
            b2_status = "EJECUTADO"
            b2_reason = b2_info["reason"]
        else:
            calc_cursadas_b2 = "NO_EJECUTABLE"
            calc_aprobadas_b2 = "NO_EJECUTABLE"
            ok_b2_cursadas = "NO_EJECUTABLE"
            ok_b2_aprobadas = "NO_EJECUTABLE"
            b2_status = "NO_EJECUTABLE_SIN_LLAVE_PLAN_CARRERA"
            b2_reason = b2_info["reason"]

        if not codclis:
            dictamen_acum = "BLOQUEO_SIN_CODCLI_ASOCIADO"
        elif not tiene_2025:
            dictamen_acum = "BLOQUEO_SIN_EVIDENCIA_2025"
        elif ok_b1_cursadas and ok_b1_aprobadas and b2_info.get("ejecutable") and ok_b2_cursadas == "SI" and ok_b2_aprobadas == "SI":
            dictamen_acum = "OK_ACUMULADO_RESPALDADO_B1_B2"
        elif ok_b1_cursadas and ok_b1_aprobadas:
            dictamen_acum = "OK_ACUMULADO_RESPALDADO_B1_B2_NO_EJECUTABLE"
        else:
            dictamen_acum = "REVISAR_LOGICA_ACUMULADA"

        accum_rows.append(
            {
                "FILA_5809": idx + 1,
                "RUT_NORMALIZADO": rut,
                "CODCLI_LISTA": safe_join(codclis, ";"),
                "CODCLI_CANTIDAD": len(codclis),
                "CODIGO_UNICO": row["CODIGO_UNICO"],
                "PLAN_ESTUDIOS": row["PLAN_ESTUDIOS"],
                "UNID_CURSADAS_TOTAL original": row["UNID_CURSADAS_TOTAL"],
                "UNID_CURSADAS_TOTAL_CALC_1": calc_cursadas_b1,
                "DIF_UNID_CURSADAS_TOTAL_B1": (
                    None if orig_cursadas_total is None else calc_cursadas_b1 - orig_cursadas_total
                ),
                "OK_UNID_CURSADAS_TOTAL_B1": "SI" if ok_b1_cursadas else "NO",
                "UNID_APROBADAS_TOTAL original": row["UNID_APROBADAS_TOTAL"],
                "UNID_APROBADAS_TOTAL_CALC_1": calc_aprobadas_b1,
                "DIF_UNID_APROBADAS_TOTAL_B1": (
                    None if orig_aprobadas_total is None else calc_aprobadas_b1 - orig_aprobadas_total
                ),
                "OK_UNID_APROBADAS_TOTAL_B1": "SI" if ok_b1_aprobadas else "NO",
                "UNID_CURSADAS_TOTAL_CALC_2": calc_cursadas_b2,
                "UNID_APROBADAS_TOTAL_CALC_2": calc_aprobadas_b2,
                "OK_UNID_CURSADAS_TOTAL_B2": ok_b2_cursadas,
                "OK_UNID_APROBADAS_TOTAL_B2": ok_b2_aprobadas,
                "B2_ESTADO": b2_status,
                "B2_MOTIVO": b2_reason,
                "REGISTROS_2025": metric["registros_2025"],
                "REGISTROS_2026_MISMO_CODCLI": metric["registros_2026"],
                "DICTAMEN_ACUMULADO_FILA": dictamen_acum,
            }
        )

    annual_df = pd.DataFrame(annual_rows)
    accum_df = pd.DataFrame(accum_rows)
    stats = {
        "total_filas": int(len(csv_5809)),
        "filas_con_codcli": int((annual_df["CODCLI_CANTIDAD"] > 0).sum()),
        "filas_sin_codcli": int((annual_df["CODCLI_CANTIDAD"] == 0).sum()),
        "filas_con_evidencia_2025": int((annual_df["TIENE_EVIDENCIA_2025"] == "SI").sum()),
        "filas_con_evidencia_2026_mismo_codcli": int((annual_df["TIENE_EVIDENCIA_2026_MISMO_CODCLI"] == "SI").sum()),
        "filas_ok_columnas_16_19": int(
            annual_df["DICTAMEN_ANUAL_2025"].isin(
                ["OK_ANUAL_2025_CALZA", "OK_ANUAL_2025_CALZA_PERO_CODCLI_TAMBIEN_TIENE_2026"]
            ).sum()
        ),
        "filas_diferencia_columnas_16_19": int((annual_df["DICTAMEN_ANUAL_2025"] == "DIFERENCIA_ANUAL_2025").sum()),
        "filas_estados_no_clasificados": int((annual_df["ESTADOS_NO_CLASIFICADOS_2025_DISTINTOS_CURSOS"] > 0).sum()),
        "filas_sin_evidencia_2025": int((annual_df["TIENE_EVIDENCIA_2025"] == "NO").sum()),
        "filas_b1_ok_20_21": int(
            ((accum_df["OK_UNID_CURSADAS_TOTAL_B1"] == "SI") & (accum_df["OK_UNID_APROBADAS_TOTAL_B1"] == "SI")).sum()
        ),
        "filas_b1_diferencia_20_21": int(
            ((accum_df["OK_UNID_CURSADAS_TOTAL_B1"] != "SI") | (accum_df["OK_UNID_APROBADAS_TOTAL_B1"] != "SI")).sum()
        ),
    }
    return annual_df, accum_df, stats


def annual_global_dictamen(stats: Dict[str, Any], blocked_columns: List[str]) -> str:
    if "CODCLI" in blocked_columns:
        return "BLOQUEO_SIN_CODCLI"
    if stats["filas_sin_codcli"] > 0:
        return "BLOQUEO_SIN_CODCLI"
    if stats["filas_sin_evidencia_2025"] > 0:
        return "BLOQUEO_SIN_EVIDENCIA_2025"
    if stats["filas_estados_no_clasificados"] > 0:
        return "BLOQUEO_ESTADOS_NO_CLASIFICADOS"
    if stats["filas_diferencia_columnas_16_19"] > 0:
        return "REVISAR_DIFERENCIAS_COLUMNAS_16_19"
    return "OK_COLUMNAS_16_19_RESPALDADAS_2025"


def accumulated_global_dictamen(stats: Dict[str, Any], blocked_columns: List[str], b2_info: Dict[str, Any]) -> str:
    if blocked_columns:
        return "BLOQUEO"
    if stats["filas_b1_diferencia_20_21"] > 0:
        return "REVISAR_LOGICA_ACUMULADA"
    if not b2_info.get("ejecutable"):
        return "NO_EJECUTABLE_SIN_LLAVE_PLAN_CARRERA"
    return "OK_COLUMNAS_20_21_RESPALDADAS"


def build_validaciones(
    selected: Dict[str, Any],
    blocked_columns: List[str],
    b2_info: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for logical in CRITICAL_COLUMNS:
        col = selected.get(logical)
        rows.append(
            {
                "validacion": f"Columna critica {logical}",
                "estado": "OK" if col else "BLOQUEO",
                "evidencia": col or "No detectada",
                "tipo": "Dato observado",
            }
        )
    rows.append(
        {
            "validacion": "Columna NOTA valida",
            "estado": "OK" if selected.get("NOTA") else "ADVERTENCIA",
            "evidencia": selected.get("NOTA") or "No se usara NOTA; aprobadas por ESTADO",
            "tipo": "Implementacion tecnica",
        }
    )
    rows.append(
        {
            "validacion": "Proteccion NOTA contra identificadores",
            "estado": "OK",
            "evidencia": "CODCLI/RUT/NUM_DOCUMENTO/DV/ANO/PERIODO excluidos; ratio identificador >80% bloquea candidato",
            "tipo": "Decision interna",
        }
    )
    rows.append(
        {
            "validacion": "B2 acumulado con llave plan/carrera",
            "estado": "OK" if b2_info.get("ejecutable") else "NO_EJECUTABLE",
            "evidencia": b2_info["reason"],
            "tipo": "Pendiente/bloqueo" if not b2_info.get("ejecutable") else "Implementacion tecnica",
        }
    )
    rows.append(
        {
            "validacion": "Exclusion tecnica ANO=2026 en calculo anual",
            "estado": "OK",
            "evidencia": (
                "Columnas 16-19 recalculadas solo con ANO=2025; "
                f"{stats['filas_con_evidencia_2026_mismo_codcli']} filas tienen 2026 mismo CODCLI reportado aparte"
            ),
            "tipo": "Implementacion tecnica",
        }
    )
    if blocked_columns:
        rows.append(
            {
                "validacion": "Bloqueo por columnas criticas",
                "estado": "BLOQUEO",
                "evidencia": safe_join(blocked_columns),
                "tipo": "Pendiente/bloqueo",
            }
        )
    return pd.DataFrame(rows)


def build_logica_auditada(selected: Dict[str, Any], b2_info: Dict[str, Any]) -> pd.DataFrame:
    rows = [
        {
            "bloque": "Dato observado",
            "elemento": "Archivo 5809",
            "detalle": "CSV sin encabezado; 22 columnas exactas; separador punto y coma; encoding cp1252",
        },
        {
            "bloque": "Dato observado",
            "elemento": "PROMEDIOSDEALUMNOS",
            "detalle": "Se leen todas las hojas; Hoja1 es la hoja principal de detalle de asignaturas",
        },
        {
            "bloque": "Dato observado",
            "elemento": "Columnas seleccionadas Hoja1",
            "detalle": json.dumps(
                {
                    "CODCLI": selected.get("CODCLI"),
                    "RUT": selected.get("RUT"),
                    "DV": selected.get("DV"),
                    "ANO": selected.get("ANO"),
                    "PERIODO": selected.get("PERIODO"),
                    "CODRAMO_ASIGNATURA": selected.get("CODRAMO_ASIGNATURA"),
                    "ESTADO": selected.get("ESTADO"),
                    "NOTA": selected.get("NOTA"),
                    "NOTA_ESCALA": selected.get("NOTA_ESCALA"),
                },
                ensure_ascii=False,
            ),
        },
        {
            "bloque": "Implementacion tecnica",
            "elemento": "Columnas 16-19",
            "detalle": "Se filtra Hoja1 por ANO=2025. Periodo 1/2 solo determina CURSO_1ER_SEM y CURSO_2DO_SEM. Unidades son CODRAMO distintos.",
        },
        {
            "bloque": "Implementacion tecnica",
            "elemento": "Columnas 20-21 B1",
            "detalle": "Se cuentan CODRAMO distintos con ANO<=2025, y aprobadas con ESTADO clasificado APROBADO; NOTA solo apoya si ESTADO no clasifica.",
        },
        {
            "bloque": "Pendiente/bloqueo",
            "elemento": "Columnas 20-21 B2",
            "detalle": b2_info["reason"],
        },
        {
            "bloque": "Decision interna",
            "elemento": "NOTA valida",
            "detalle": "Umbral interno: al menos 80% de valores numericos en escala 1-7 o 100-700; >80% apariencia identificador invalida el candidato.",
        },
        {
            "bloque": "Decision interna",
            "elemento": "Diferencias numericas",
            "detalle": "DIF = valor calculado por auditoria menos valor original observado en 5809.",
        },
        {
            "bloque": "Implementacion tecnica",
            "elemento": "Exclusion ANO=2026",
            "detalle": "ANO=2026 nunca entra al calculo anual 2025; se reporta solo como REGISTROS_2026_MISMO_CODCLI.",
        },
    ]
    return pd.DataFrame(rows)


def build_fuentes(timestamp: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "tipo": "Fuente PROMEDIOSDEALUMNOS",
                "ruta": str(SOURCE_XLSX),
                "existe": SOURCE_XLSX.exists(),
                "bytes": SOURCE_XLSX.stat().st_size if SOURCE_XLSX.exists() else None,
                "sha256": sha256_file(SOURCE_XLSX) if SOURCE_XLSX.exists() else "",
                "modificada_por_auditoria": "NO",
            },
            {
                "tipo": "Archivo 5809 salida",
                "ruta": str(SOURCE_CSV_5809),
                "existe": SOURCE_CSV_5809.exists(),
                "bytes": SOURCE_CSV_5809.stat().st_size if SOURCE_CSV_5809.exists() else None,
                "sha256": sha256_file(SOURCE_CSV_5809) if SOURCE_CSV_5809.exists() else "",
                "modificada_por_auditoria": "NO",
            },
            {
                "tipo": "Carpeta salida auditoria",
                "ruta": str(OUTPUT_DIR),
                "existe": OUTPUT_DIR.exists(),
                "bytes": "",
                "sha256": "",
                "modificada_por_auditoria": "SI, solo derivados versionados",
            },
            {
                "tipo": "Timestamp ejecucion",
                "ruta": timestamp,
                "existe": True,
                "bytes": "",
                "sha256": "",
                "modificada_por_auditoria": "NO APLICA",
            },
        ]
    )


def write_markdown_report(
    path: Path,
    stats: Dict[str, Any],
    annual_dictamen: str,
    accum_dictamen: str,
    selected: Dict[str, Any],
    catalogo_estado: pd.DataFrame,
    b2_info: Dict[str, Any],
    output_paths: Dict[str, str],
) -> None:
    no_clas = catalogo_estado[catalogo_estado["clasificacion_propuesta"] == "NO_CLASIFICADO"]
    lines = [
        "# Informe Auditoria Corregida Logica 2025 5809",
        "",
        "## Alcance",
        "",
        "- Proceso: Avance Curricular SIES 2026.",
        "- Subproyecto: validacion fila a fila de columnas 16-21 del archivo 5809.",
        "- Prioridad: responder si columnas 16-19 fueron calculadas con registros `ANO=2025`.",
        "- Regla operacional: no se modificaron fuentes originales ni el CSV 5809.",
        "",
        "## Dictamen global",
        "",
        f"- DICTAMEN_ANUAL_2025: `{annual_dictamen}`",
        f"- DICTAMEN_ACUMULADO_2025: `{accum_dictamen}`",
        "",
        "## Resumen de consola requerido",
        "",
        f"1. Total filas 5809: {stats['total_filas']}",
        f"2. Filas con CODCLI asociado: {stats['filas_con_codcli']}",
        f"3. Filas sin CODCLI: {stats['filas_sin_codcli']}",
        f"4. Filas con evidencia 2025: {stats['filas_con_evidencia_2025']}",
        f"5. Filas con evidencia 2026 mismo CODCLI: {stats['filas_con_evidencia_2026_mismo_codcli']}",
        f"6. Filas OK columnas 16-19: {stats['filas_ok_columnas_16_19']}",
        f"7. Filas con diferencia columnas 16-19: {stats['filas_diferencia_columnas_16_19']}",
        f"8. Filas con estados no clasificados: {stats['filas_estados_no_clasificados']}",
        f"9. Dictamen anual 2025: {annual_dictamen}",
        f"10. Dictamen acumulado 2025: {accum_dictamen}",
        f"11. Rutas: Excel `{output_paths['excel']}`; informe `{output_paths['markdown']}`; manifest `{output_paths['manifest']}`; carpeta Escritorio `{output_paths['desktop_dir']}`",
        "",
        "## Columnas detectadas en Hoja1",
        "",
        f"- CODCLI: `{selected.get('CODCLI')}`",
        f"- RUT: `{selected.get('RUT')}`",
        f"- DV: `{selected.get('DV')}`",
        f"- ANO: `{selected.get('ANO')}`",
        f"- PERIODO: `{selected.get('PERIODO')}`",
        f"- CODRAMO/asignatura: `{selected.get('CODRAMO_ASIGNATURA')}`",
        f"- ESTADO usado para clasificar: `{selected.get('ESTADO')}`",
        f"- NOTA valida: `{selected.get('NOTA') or 'NO'}`",
        f"- Motivo NOTA: {selected.get('NOTA_DETECCION_MOTIVO')}",
        "",
        "## Proteccion contra error previo de NOTA",
        "",
        "La auditoria invalida como NOTA cualquier columna llamada o equivalente a `CODCLI`, `RUT`, `NUM_DOCUMENTO`, `DV`, `ANO` o `PERIODO`. Tambien invalida candidatos donde mas del 80% de valores parecen identificadores. Por esta regla, `CODCLI` no puede volver a ser usado como nota.",
        "",
        "## Catalogo de estado",
        "",
        "La clasificacion usa solo patrones explicitos permitidos: APROB/APR/CONVALID/HOMOLOG/RECONOC para aprobado; REPROB/REP/NO APROB/NCR para no aprobado. Senales contradictorias quedan como NO_CLASIFICADO.",
        "",
        f"- Valores NO_CLASIFICADO en catalogo: {len(no_clas)}",
        "",
        "## Acumulado B2",
        "",
        f"- Estado B2: {'EJECUTABLE' if b2_info.get('ejecutable') else 'NO_EJECUTABLE'}",
        f"- Motivo: {b2_info['reason']}",
        "",
        "## No listo para carga",
        "",
    ]
    if annual_dictamen == "OK_COLUMNAS_16_19_RESPALDADAS_2025" and accum_dictamen == "OK_COLUMNAS_20_21_RESPALDADAS":
        lines.append("No se detectaron bloqueos segun las reglas definidas para columnas 16-21.")
    else:
        lines.append(
            "No se declara listo para carga: el dictamen global exige revisar o bloquea al menos una parte del proceso, segun las reglas solicitadas."
        )
    lines.extend(
        [
            "",
            "## Comando reproducible",
            "",
            "```bash",
            "cd /Users/alexi/Documents/GitHub/avance_curricular",
            "python3 avance_curricular_2026/29_auditoria_corregida_logica_2025_5809/auditoria_corregida_logica_2025_5809.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_manifest(
    path: Path,
    timestamp: str,
    stats: Dict[str, Any],
    annual_dictamen: str,
    accum_dictamen: str,
    selected: Dict[str, Any],
    output_paths: Dict[str, str],
    b2_info: Dict[str, Any],
) -> None:
    manifest = {
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "validacion fila a fila columnas 16-21 archivo 5809",
        "timestamp": timestamp,
        "fuentes": {
            "promediosdealumnos": {
                "ruta": str(SOURCE_XLSX),
                "sha256": sha256_file(SOURCE_XLSX),
                "modificada": False,
            },
            "csv_5809": {
                "ruta": str(SOURCE_CSV_5809),
                "sha256": sha256_file(SOURCE_CSV_5809),
                "modificada": False,
            },
        },
        "salidas": output_paths,
        "columnas_detectadas": {
            "CODCLI": selected.get("CODCLI"),
            "RUT": selected.get("RUT"),
            "DV": selected.get("DV"),
            "ANO": selected.get("ANO"),
            "PERIODO": selected.get("PERIODO"),
            "CODRAMO_ASIGNATURA": selected.get("CODRAMO_ASIGNATURA"),
            "ESTADO": selected.get("ESTADO"),
            "NOTA": selected.get("NOTA"),
            "NOTA_ESCALA": selected.get("NOTA_ESCALA"),
        },
        "nota_salvaguardas": {
            "prohibidas_por_nombre": sorted(FORBIDDEN_NOTE_NORMALIZED),
            "umbral_identificador": ">80%",
            "umbral_compatibilidad_escala": ">=80%",
            "motivo": selected.get("NOTA_DETECCION_MOTIVO"),
        },
        "b2_acumulado": b2_info,
        "metricas": stats,
        "dictamen_anual_2025": annual_dictamen,
        "dictamen_acumulado_2025": accum_dictamen,
        "hojas_excel_requeridas": EXPECTED_SHEETS,
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_excel(
    path: Path,
    sheets_to_write: Dict[str, pd.DataFrame],
) -> None:
    # openpyxl permite escribir nombres largos solicitados por el usuario; Excel puede advertir por >31 caracteres.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for sheet_name, df in sheets_to_write.items():
                safe_df = sanitize_df_for_excel(df)
                safe_df.to_excel(writer, sheet_name=sheet_name, index=False)


def load_inputs() -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    if not SOURCE_XLSX.exists():
        raise FileNotFoundError(f"No existe fuente Excel: {SOURCE_XLSX}")
    if not SOURCE_CSV_5809.exists():
        raise FileNotFoundError(f"No existe CSV 5809: {SOURCE_CSV_5809}")

    sheets = pd.read_excel(SOURCE_XLSX, sheet_name=None, engine="openpyxl", dtype=object)
    csv_5809 = pd.read_csv(
        SOURCE_CSV_5809,
        sep=";",
        encoding="cp1252",
        header=None,
        names=CSV_5809_COLUMNS,
        dtype=str,
        keep_default_na=False,
    )
    return sheets, csv_5809


def main() -> int:
    timestamp = now_stamp()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    desktop_dir = Path.home() / "Desktop" / f"AVANCE_CURRICULAR_2026_AUDITORIA_LOGICA_2025_5809_{timestamp}"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    excel_path = OUTPUT_DIR / EXCEL_NAME
    md_path = OUTPUT_DIR / MD_NAME
    manifest_path = OUTPUT_DIR / MANIFEST_NAME

    sheets, csv_5809 = load_inputs()
    if "Hoja1" not in sheets:
        raise RuntimeError("BLOQUEO: PROMEDIOSDEALUMNOS no contiene Hoja1")

    hoja1 = sheets["Hoja1"]
    column_diag = build_column_diagnostics(sheets)
    selected, detection_eval = detect_columns_for_hoja1(hoja1)
    blocked_columns = [logical for logical in CRITICAL_COLUMNS if not selected.get(logical)]

    catalogo_estado = build_catalogo_estado(hoja1, selected.get("ESTADO"))
    mapping_df, rut_to_codcli = build_mapping(sheets)

    if blocked_columns:
        hoja1_proc = prepare_hoja1(hoja1, selected)
        metrics_by_codcli: Dict[str, Dict[str, Any]] = {}
    else:
        hoja1_proc = prepare_hoja1(hoja1, selected)
        metrics_by_codcli = aggregate_by_codcli(hoja1_proc)

    b2_info = detect_b2_plan_key(hoja1_proc, csv_5809)
    annual_df, accum_df, stats = audit_rows(csv_5809, rut_to_codcli, metrics_by_codcli, b2_info, hoja1_proc)

    annual_dictamen = annual_global_dictamen(stats, blocked_columns)
    accum_dictamen = accumulated_global_dictamen(stats, blocked_columns, b2_info)

    output_paths = {
        "excel": str(excel_path),
        "markdown": str(md_path),
        "manifest": str(manifest_path),
        "desktop_dir": str(desktop_dir),
    }

    dictamen_global_df = pd.DataFrame(
        [
            {"indicador": "DICTAMEN_ANUAL_2025", "valor": annual_dictamen},
            {"indicador": "DICTAMEN_ACUMULADO_2025", "valor": accum_dictamen},
            {"indicador": "TOTAL_FILAS_5809", "valor": stats["total_filas"]},
            {"indicador": "FILAS_CON_CODCLI", "valor": stats["filas_con_codcli"]},
            {"indicador": "FILAS_SIN_CODCLI", "valor": stats["filas_sin_codcli"]},
            {"indicador": "FILAS_CON_EVIDENCIA_2025", "valor": stats["filas_con_evidencia_2025"]},
            {
                "indicador": "FILAS_CON_EVIDENCIA_2026_MISMO_CODCLI",
                "valor": stats["filas_con_evidencia_2026_mismo_codcli"],
            },
            {"indicador": "FILAS_OK_COLUMNAS_16_19", "valor": stats["filas_ok_columnas_16_19"]},
            {
                "indicador": "FILAS_CON_DIFERENCIA_COLUMNAS_16_19",
                "valor": stats["filas_diferencia_columnas_16_19"],
            },
            {
                "indicador": "FILAS_CON_ESTADOS_NO_CLASIFICADOS",
                "valor": stats["filas_estados_no_clasificados"],
            },
            {"indicador": "FILAS_B1_OK_COLUMNAS_20_21", "valor": stats["filas_b1_ok_20_21"]},
            {"indicador": "FILAS_B1_DIFERENCIA_COLUMNAS_20_21", "valor": stats["filas_b1_diferencia_20_21"]},
            {"indicador": "B2_ESTADO", "valor": "EJECUTABLE" if b2_info.get("ejecutable") else "NO_EJECUTABLE"},
            {"indicador": "B2_MOTIVO", "valor": b2_info["reason"]},
        ]
    )

    validaciones_df = build_validaciones(selected, blocked_columns, b2_info, stats)
    columnas_detectadas_df = column_diag.copy()
    selected_rows = []
    for logical in [
        "CODCLI",
        "RUT",
        "DV",
        "ANO",
        "PERIODO",
        "CODRAMO_ASIGNATURA",
        "ESTADO",
        "NOTA",
    ]:
        selected_rows.append(
            {
                "hoja": "Hoja1",
                "tipo_registro": "SELECCION_AUDITORIA",
                "campo_logico": logical,
                "columna_seleccionada": selected.get(logical) or "",
                "motivo": selected.get(f"{logical}_DETECCION_MOTIVO", ""),
            }
        )
    selected_df = pd.DataFrame(selected_rows)
    if not detection_eval.empty:
        detection_eval_copy = detection_eval.copy()
        detection_eval_copy.insert(0, "hoja", "Hoja1")
        detection_eval_copy.insert(1, "tipo_registro", "EVALUACION_CANDIDATO")
        detection_eval_copy["campo_logico"] = detection_eval_copy.apply(
            lambda r: "NOTA" if "escala" in r.index and pd.notna(r.get("escala", None)) else "ESTADO",
            axis=1,
        )
        columnas_detectadas_df = pd.concat([columnas_detectadas_df, selected_df, detection_eval_copy], ignore_index=True, sort=False)
    else:
        columnas_detectadas_df = pd.concat([columnas_detectadas_df, selected_df], ignore_index=True, sort=False)

    revisar_anual = annual_df[
        ~annual_df["DICTAMEN_ANUAL_2025"].isin(
            ["OK_ANUAL_2025_CALZA", "OK_ANUAL_2025_CALZA_PERO_CODCLI_TAMBIEN_TIENE_2026"]
        )
    ].copy()

    resumen_anual = pd.concat(
        [
            annual_df["DICTAMEN_ANUAL_2025"].value_counts().rename_axis("DICTAMEN_ANUAL_2025").reset_index(name="filas"),
            pd.DataFrame(
                [
                    {"DICTAMEN_ANUAL_2025": "TOTAL", "filas": len(annual_df)},
                    {"DICTAMEN_ANUAL_2025": "FILAS_CON_EVIDENCIA_2026_MISMO_CODCLI", "filas": stats["filas_con_evidencia_2026_mismo_codcli"]},
                ]
            ),
        ],
        ignore_index=True,
    )

    revisar_acum = accum_df[
        (accum_df["OK_UNID_CURSADAS_TOTAL_B1"] != "SI")
        | (accum_df["OK_UNID_APROBADAS_TOTAL_B1"] != "SI")
        | (accum_df["B2_ESTADO"] != "EJECUTADO")
        | (accum_df["DICTAMEN_ACUMULADO_FILA"].str.startswith("BLOQUEO"))
    ].copy()

    resumen_acum = pd.concat(
        [
            accum_df["DICTAMEN_ACUMULADO_FILA"].value_counts().rename_axis("DICTAMEN_ACUMULADO_FILA").reset_index(name="filas"),
            pd.DataFrame(
                [
                    {"DICTAMEN_ACUMULADO_FILA": "TOTAL", "filas": len(accum_df)},
                    {"DICTAMEN_ACUMULADO_FILA": "FILAS_B1_OK_COLUMNAS_20_21", "filas": stats["filas_b1_ok_20_21"]},
                    {
                        "DICTAMEN_ACUMULADO_FILA": "FILAS_B1_DIFERENCIA_COLUMNAS_20_21",
                        "filas": stats["filas_b1_diferencia_20_21"],
                    },
                ]
            ),
        ],
        ignore_index=True,
    )

    b2_checks_df = pd.DataFrame(b2_info.get("checks", []))
    logica_df = pd.concat([build_logica_auditada(selected, b2_info), b2_checks_df.assign(bloque="Pendiente/bloqueo", elemento="Chequeo llave B2", detalle=lambda x: x.astype(str).agg(" | ".join, axis=1))[["bloque", "elemento", "detalle"]]], ignore_index=True)
    fuentes_df = build_fuentes(timestamp)

    sheets_to_write = {
        "DICTAMEN_GLOBAL": dictamen_global_df,
        "VALIDACIONES": validaciones_df,
        "COLUMNAS_DETECTADAS": columnas_detectadas_df,
        "CATALOGO_ESTADO": catalogo_estado,
        "MAPEO_CODCLI_RUT": mapping_df,
        "AUDITORIA_ANUAL_2025_FILA_A_FILA": annual_df,
        "FILAS_REVISAR_ANUAL_2025": revisar_anual,
        "RESUMEN_ANUAL_2025": resumen_anual,
        "AUDITORIA_ACUMULADO_2025_FILA_A_FILA": accum_df,
        "FILAS_REVISAR_ACUMULADO_2025": revisar_acum,
        "RESUMEN_ACUMULADO_2025": resumen_acum,
        "LOGICA_AUDITADA": logica_df,
        "FUENTES": fuentes_df,
    }
    write_excel(excel_path, sheets_to_write)
    write_markdown_report(md_path, stats, annual_dictamen, accum_dictamen, selected, catalogo_estado, b2_info, output_paths)
    write_manifest(manifest_path, timestamp, stats, annual_dictamen, accum_dictamen, selected, output_paths, b2_info)

    for p in [excel_path, md_path, manifest_path]:
        shutil.copy2(p, desktop_dir / p.name)

    print("1. Total filas 5809:", stats["total_filas"])
    print("2. Filas con CODCLI asociado:", stats["filas_con_codcli"])
    print("3. Filas sin CODCLI:", stats["filas_sin_codcli"])
    print("4. Filas con evidencia 2025:", stats["filas_con_evidencia_2025"])
    print("5. Filas con evidencia 2026 mismo CODCLI:", stats["filas_con_evidencia_2026_mismo_codcli"])
    print("6. Filas OK columnas 16-19:", stats["filas_ok_columnas_16_19"])
    print("7. Filas con diferencia columnas 16-19:", stats["filas_diferencia_columnas_16_19"])
    print("8. Filas con estados no clasificados:", stats["filas_estados_no_clasificados"])
    print("9. Dictamen anual 2025:", annual_dictamen)
    print("10. Dictamen acumulado 2025:", accum_dictamen)
    print("11. Rutas de Excel, informe, manifest y carpeta Escritorio:")
    print("    Excel:", excel_path)
    print("    Informe:", md_path)
    print("    Manifest:", manifest_path)
    print("    Carpeta Escritorio:", desktop_dir)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IllegalCharacterError as exc:
        print(f"ERROR Excel por caracter ilegal: {exc}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"ERROR AUDITORIA: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
