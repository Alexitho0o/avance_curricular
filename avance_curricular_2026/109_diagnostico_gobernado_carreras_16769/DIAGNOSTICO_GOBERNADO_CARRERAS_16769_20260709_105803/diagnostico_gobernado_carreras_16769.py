#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostico gobernado Carreras Avance Curricular 2026, ID carga SIES 16769.

Este hito no genera CSV de carga, no corrige datos y no modifica fuentes
originales. Produce un expediente diagnostico reproducible para decidir si
existe evidencia suficiente antes de materializar una segunda etapa.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BASE_2026 = RAIZ / "avance_curricular_2026"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA_BASE = BASE_2026 / "109_diagnostico_gobernado_carreras_16769"
SALIDA = SALIDA_BASE / f"DIAGNOSTICO_GOBERNADO_CARRERAS_16769_{TS}"
DESKTOP = Path.home() / "Desktop" / f"AVANCE_CURRICULAR_2026_DIAGNOSTICO_GOBERNADO_CARRERAS_16769_{TS}"

MANUAL = (
    BASE_2026
    / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/"
    / "Instructivo_Avance Curricular SIES - 2026.txt"
)
PRECARGA_5810 = (
    BASE_2026
    / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/"
    / "5810_Precarga Carreras Avance Curricular 20268.csv"
)
CANONICO_PLANES = (
    BASE_2026
    / "04_gobernanza_mallas/03_auditorias/CANONICO_TODOS_PLANES_ESTUDIO_20260701_140528/"
    / "02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv"
)
CONCILIACION_43 = (
    BASE_2026
    / "04_gobernanza_mallas/03_auditorias/CIERRE_FINAL_43_RESUELTAS_0_PENDIENTES_20260701_171409/"
    / "02_RESULTADOS/01_CONCILIACION_FINAL_43.tsv"
)
DESBLOQUEO_43 = (
    BASE_2026
    / "04_gobernanza_mallas/03_auditorias/DESBLOQUEO_NIVELES_EVIDENCIAS_CARRERAS_43_20260701_180302/"
    / "05_RESULTADOS/DESBLOQUEO_FUNCIONAL_CARRERAS_43.xlsx"
)
DETALLE_9 = (
    BASE_2026
    / "04_gobernanza_mallas/03_auditorias/DESBLOQUEO_NIVELES_EVIDENCIAS_CARRERAS_43_20260701_180302/"
    / "03_EVIDENCIAS/detalle_asignaturas_creditos_niveles_9.tsv"
)
FUERA_DURACION_PREVIO = (
    BASE_2026
    / "04_gobernanza_mallas/03_auditorias/DESBLOQUEO_NIVELES_EVIDENCIAS_CARRERAS_43_20260701_180302/"
    / "02_NIVELES/detalle_asignaturas_fuera_duracion.tsv"
)
DETALLE_UNIDADES_PLAN = (
    BASE_2026
    / "04_gobernanza_mallas/03_auditorias/VALIDACION_FUNCIONAL_CARRERAS_43_REANUDADA_20260701_174055/"
    / "03_UNIDADES/detalle_unidades_por_plan.tsv"
)
H106_XLSX = (
    BASE_2026
    / "106_carreras_16769_gobernado_por_codigo_unico/CARRERAS_16769_GOBERNADO_20260709_102827/"
    / "5810_CARRERAS_AVANCE_CURRICULAR_2026_REVISION_GOBERNADA_21C.xlsx"
)
H106_CSV = (
    BASE_2026
    / "106_carreras_16769_gobernado_por_codigo_unico/CARRERAS_16769_GOBERNADO_20260709_102827/"
    / "5810_CARRERAS_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16769_21C_GOBERNADO.csv"
)
H106_MANIFEST = (
    BASE_2026
    / "106_carreras_16769_gobernado_por_codigo_unico/CARRERAS_16769_GOBERNADO_20260709_102827/"
    / "manifest_h106_carreras_16769.json"
)

UNIT_COLS = [
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
]

SIES_21_COLS = [
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
    *UNIT_COLS,
    "VIGENCIA",
]


def sha256(path: Path) -> str:
    if not path.exists() or path.is_dir():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().upper()).strip("_")
    return text


def read_csv_any(path: Path, sep: str | None = None, nrows: int | None = None) -> pd.DataFrame:
    seps = [sep] if sep else ["\t", ";", ","]
    encodings = ["utf-8-sig", "utf-8", "latin1"]
    last_error: Exception | None = None
    for candidate_sep in seps:
        for encoding in encodings:
            try:
                return pd.read_csv(path, sep=candidate_sep, encoding=encoding, dtype=str, nrows=nrows).fillna("")
            except Exception as exc:  # noqa: BLE001
                last_error = exc
    raise RuntimeError(f"No se pudo leer {path}: {last_error}")


def as_int(value: Any, default: int = 0) -> int:
    text = "" if value is None else str(value).strip()
    if text == "":
        return default
    try:
        return int(float(text.replace(",", ".")))
    except Exception:  # noqa: BLE001
        return default


def ceil_div2(value: Any) -> int | None:
    text = "" if value is None else str(value).strip()
    if text == "":
        return None
    try:
        return int(math.ceil(float(text.replace(",", ".")) / 2.0))
    except Exception:  # noqa: BLE001
        return None


def ordered_unique(values: pd.Series) -> str:
    cleaned = [str(v).strip() for v in values.dropna().astype(str) if str(v).strip() != ""]
    if not cleaned:
        return ""

    def sort_key(x: str) -> tuple[int, Any]:
        return (0, int(x)) if re.fullmatch(r"-?\d+", x) else (1, x)

    return " | ".join(sorted(set(cleaned), key=sort_key))


def sheet_dimensions_xlsx(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            out.append({"sheet": ws.title, "rows": max(ws.max_row - 1, 0), "columns": ws.max_column})
        wb.close()
    except Exception:  # noqa: BLE001
        return out
    return out


def detect_columns(columns: list[str]) -> dict[str, str]:
    by_norm = {norm_text(c): c for c in columns}

    def first(*names: str) -> str:
        for name in names:
            if name in by_norm:
                return by_norm[name]
        return ""

    out = {
        "codigo_unico": first("CODIGO_UNICO"),
        "plan_estudios": first("PLAN_ESTUDIOS", "PLAN_ESTUDIOS_PROPUESTO", "PLAN_DE_ESTUDIO_CANONICO", "CODPESTUD"),
        "codpestud": first("CODPESTUD", "PLAN_DE_ESTUDIO_CANONICO", "PLAN_DE_ESTUDIO_CANONICO_CIERRE"),
        "nombre_carrera": first("NOMBRE_CARRERA", "NOMBRE_CARRERA_5810", "NOMBRE_L", "CARRERA"),
        "jornada": first("JORNADA", "JORNADA_5810", "JORNADA_MAPEO"),
        "version": first("VERSION", "VERSION_5810", "VERSION_MAPEO"),
        "nivel": first("NIVEL", "NIVEL_ORIGINAL"),
        "semestre": first("SEMESTRE"),
        "anio": first("ANIO", "ANO", "ANIO_DISTRIBUCION", "AÑO"),
        "asignatura": first(
            "RAMOEQUIV",
            "CODRAMO",
            "CODIGO_ASIGNATURA",
            "RAMO",
            "ASIGNATURA",
            "NOMBRE_ASIGNATURA",
            "NOMBRE",
        ),
        "creditos": first("CREDITO", "CREDITOS", "TOTAL_CREDITOS_PLAN"),
        "tipo_unidad": first("TIPO_UNIDAD_MEDIDA"),
        "total_unidades": first("TOTAL_UNIDADES_MEDIDA"),
    }
    out["unidades_anio"] = "SI" if all(col in by_norm for col in [norm_text(c) for c in UNIT_COLS]) else "NO"
    return out


def classify_source(path: Path) -> tuple[str, str]:
    p = norm_text(str(path.relative_to(RAIZ) if path.is_relative_to(RAIZ) else path))
    if "INSTRUCTIVO" in p or "MANUAL" in p:
        return "manual/instructivo", "A"
    if "PRECARGA" in p or "FUENTES_CONGELADAS" in p:
        return "precarga/fuente congelada", "B"
    if "PLANES_ESTUDIO" in p or "MALLA" in p or "CANONICO" in p:
        return "fuente institucional malla/planes", "B"
    if "SCRIPT" in p or path.suffix.lower() == ".py":
        return "implementacion tecnica", "C"
    if "AUDITORIA" in p or "VALIDACION" in p or "DIAGNOSTICO" in p:
        return "auditoria/resultado", "C"
    return "archivo de trabajo/evidencia", "B"


def source_tokens_score(path: Path) -> int:
    text = norm_text(str(path.relative_to(RAIZ) if path.is_relative_to(RAIZ) else path))
    good = [
        "MALLA",
        "MALLAS",
        "PLAN",
        "PLANES",
        "PLAN_ESTUDIO",
        "ASIGNATURA",
        "ASIGNATURAS",
        "RAMO",
        "CODRAMO",
        "RAMOEQUIV",
        "NIVEL",
        "CARRERA",
        "CARRERAS",
        "ESTRUCTURA",
        "GOBERNANZA",
        "CANONICO",
        "CONCILIACION",
        "DISTRIBUCION",
        "UNIDADES",
    ]
    bad = ["5809", "MATRICULA", "ESTUDIANTE", "ALUMNO", "PROMEDIOS"]
    score = sum(1 for token in good if token in text) * 3
    score -= sum(1 for token in bad if token in text) * 8
    if "04_GOBERNANZA_MALLAS" in text or "01_FUENTES_INSTITUCIONALES_PLANES_ESTUDIO" in text:
        score += 20
    return score


def inventory_sources(precarga_codes: set[str], precarga_pairs: set[tuple[str, str]], conc_43: pd.DataFrame) -> pd.DataFrame:
    curated = {
        CANONICO_PLANES,
        CONCILIACION_43,
        DESBLOQUEO_43,
        DETALLE_9,
        FUERA_DURACION_PREVIO,
        DETALLE_UNIDADES_PLAN,
        H106_XLSX,
        H106_CSV,
    }
    extensions = {".tsv", ".csv", ".xlsx", ".xls"}
    found: set[Path] = set()
    for path in RAIZ.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        rel_norm = norm_text(str(path.relative_to(RAIZ)))
        if any(skip in rel_norm for skip in ["__PYCACHE__", ".GIT", "NODE_MODULES"]):
            continue
        if path in curated or source_tokens_score(path) > 0:
            found.add(path)
    found.update(curated)

    codp_to_codes = {}
    if "CODPESTUD" in conc_43.columns and "CODIGO_UNICO" in conc_43.columns:
        tmp = conc_43[["CODIGO_UNICO", "CODPESTUD"]].drop_duplicates()
        codp_to_codes = tmp.groupby("CODPESTUD")["CODIGO_UNICO"].apply(lambda s: set(s.astype(str))).to_dict()

    rows: list[dict[str, Any]] = []
    for path in sorted(found, key=lambda p: (-source_tokens_score(p), str(p))):
        tipo, respaldo = classify_source(path)
        base_row = {
            "archivo": path.name,
            "ruta": str(path),
            "existe": "SI" if path.exists() else "NO",
            "tipo": path.suffix.lower().replace(".", "").upper(),
            "clasificacion": tipo,
            "nivel_respaldo": respaldo,
            "hash_sha256": sha256(path),
            "score_nombre_ruta": source_tokens_score(path),
        }
        if not path.exists():
            rows.append(base_row)
            continue
        try:
            if path.suffix.lower() in {".xlsx", ".xls"}:
                dims = sheet_dimensions_xlsx(path)
                sheet_names = [d["sheet"] for d in dims] or [None]
                for sheet in sheet_names:
                    dim = next((d for d in dims if d["sheet"] == sheet), {"rows": "", "columns": ""})
                    try:
                        df = pd.read_excel(path, sheet_name=sheet, dtype=str, nrows=5000).fillna("")
                    except Exception:
                        df = pd.DataFrame()
                    rows.append(profile_candidate_sheet(base_row, sheet or "", dim.get("rows", len(df)), dim.get("columns", len(df.columns)), df, precarga_codes, precarga_pairs, codp_to_codes))
            else:
                df = read_csv_any(path, sep="\t" if path.suffix.lower() == ".tsv" else None, nrows=None if path.stat().st_size < 20_000_000 else 5000)
                rows.append(profile_candidate_sheet(base_row, "CSV/TSV", len(df), len(df.columns), df, precarga_codes, precarga_pairs, codp_to_codes))
        except Exception as exc:  # noqa: BLE001
            row = dict(base_row)
            row.update({"hoja": "", "filas": "", "columnas": "", "error_lectura": str(exc)[:300]})
            rows.append(row)

    inv = pd.DataFrame(rows).fillna("")
    if inv.empty:
        return inv
    inv["score_ranking"] = inv.apply(score_inventory_row, axis=1)
    return inv.sort_values(["score_ranking", "score_nombre_ruta"], ascending=False).reset_index(drop=True)


def profile_candidate_sheet(
    base_row: dict[str, Any],
    sheet: str,
    rows_count: Any,
    cols_count: Any,
    df: pd.DataFrame,
    precarga_codes: set[str],
    precarga_pairs: set[tuple[str, str]],
    codp_to_codes: dict[str, set[str]],
) -> dict[str, Any]:
    row = dict(base_row)
    row.update({"hoja": sheet, "filas": rows_count, "columnas": cols_count})
    cols = list(df.columns)
    detected = detect_columns(cols)
    row.update(
        {
            "tiene_codigo_unico": "SI" if detected["codigo_unico"] else "NO",
            "tiene_plan_estudios_o_codpestud": "SI" if detected["plan_estudios"] else "NO",
            "tiene_nombre_carrera": "SI" if detected["nombre_carrera"] else "NO",
            "tiene_jornada": "SI" if detected["jornada"] else "NO",
            "tiene_version": "SI" if detected["version"] else "NO",
            "tiene_nivel": "SI" if detected["nivel"] else "NO",
            "nivel_columna": detected["nivel"],
            "tiene_semestre": "SI" if detected["semestre"] else "NO",
            "tiene_anio": "SI" if detected["anio"] else "NO",
            "tiene_asignatura_ramo": "SI" if detected["asignatura"] else "NO",
            "asignatura_columna": detected["asignatura"],
            "tiene_creditos": "SI" if detected["creditos"] else "NO",
            "tiene_tipo_unidad_medida": "SI" if detected["tipo_unidad"] else "NO",
            "tiene_total_unidades_medida": "SI" if detected["total_unidades"] else "NO",
            "tiene_unidades_1_a_7": detected["unidades_anio"],
            "valores_nivel": "",
            "nivel_min": "",
            "nivel_max": "",
            "niveles_fuera_1_14": "",
            "niveles_15_20": "",
            "match_43_codigo_unico": 0,
            "match_43_codigo_unico_plan": 0,
            "match_43_por_codpestud": 0,
            "duplicados_codigo_unico": "",
            "duplicados_codigo_unico_plan": "",
            "registros_por_carrera_min": "",
            "registros_por_carrera_max": "",
            "asignaturas_unicas_por_carrera_min": "",
            "asignaturas_unicas_por_carrera_max": "",
            "penalizacion_matricula_5809": "SI"
            if ("5809" in norm_text(str(base_row["ruta"])) or "MATRICULA" in norm_text(str(base_row["ruta"])))
            else "NO",
            "observacion_ranking": "",
        }
    )
    if df.empty:
        row["observacion_ranking"] = "No se pudo leer muestra para perfilar columnas."
        return row

    if detected["nivel"]:
        level_series = df[detected["nivel"]].astype(str).str.strip()
        row["valores_nivel"] = ordered_unique(level_series)
        nums = pd.to_numeric(level_series, errors="coerce").dropna()
        if not nums.empty:
            row["nivel_min"] = int(nums.min())
            row["nivel_max"] = int(nums.max())
            outside = sorted({int(x) for x in nums if int(x) < 1 or int(x) > 14})
            row["niveles_fuera_1_14"] = " | ".join(map(str, outside))
            high = sorted({int(x) for x in nums if 15 <= int(x) <= 20})
            row["niveles_15_20"] = " | ".join(map(str, high))

    if detected["codigo_unico"]:
        codes = set(df[detected["codigo_unico"]].astype(str).str.strip())
        row["match_43_codigo_unico"] = len(codes.intersection(precarga_codes))
        row["duplicados_codigo_unico"] = int(df[detected["codigo_unico"]].duplicated().sum())
        if detected["plan_estudios"]:
            pairs = set(
                zip(
                    df[detected["codigo_unico"]].astype(str).str.strip(),
                    df[detected["plan_estudios"]].astype(str).str.strip(),
                )
            )
            row["match_43_codigo_unico_plan"] = len(pairs.intersection(precarga_pairs))
            row["duplicados_codigo_unico_plan"] = int(df.duplicated([detected["codigo_unico"], detected["plan_estudios"]]).sum())
        if detected["asignatura"]:
            grouped = df.groupby(detected["codigo_unico"], dropna=False)
            counts = grouped.size()
            row["registros_por_carrera_min"] = int(counts.min()) if not counts.empty else ""
            row["registros_por_carrera_max"] = int(counts.max()) if not counts.empty else ""
            unique_counts = grouped[detected["asignatura"]].nunique()
            row["asignaturas_unicas_por_carrera_min"] = int(unique_counts.min()) if not unique_counts.empty else ""
            row["asignaturas_unicas_por_carrera_max"] = int(unique_counts.max()) if not unique_counts.empty else ""

    if detected["codpestud"]:
        codps = set(df[detected["codpestud"]].astype(str).str.strip())
        covered: set[str] = set()
        for codp in codps:
            covered.update(codp_to_codes.get(codp, set()))
        row["match_43_por_codpestud"] = len(covered.intersection(precarga_codes))

    observations = []
    if row["penalizacion_matricula_5809"] == "SI":
        observations.append("Penalizada: ruta/nombre asociado a matrícula 5809 o estudiantes.")
    if row["tiene_nivel"] == "NO":
        observations.append("No contiene NIVEL util para distribucion por plan.")
    if row["tiene_asignatura_ramo"] == "NO":
        observations.append("No contiene asignatura/ramo para detalle.")
    if int(row.get("match_43_codigo_unico") or 0) == 43 or int(row.get("match_43_por_codpestud") or 0) == 43:
        observations.append("Cubre 43/43 por CODIGO_UNICO o por CODPESTUD trazable.")
    row["observacion_ranking"] = " ".join(observations)
    return row


def score_inventory_row(row: pd.Series) -> int:
    score = int(row.get("score_nombre_ruta") or 0)
    if row.get("tiene_codigo_unico") == "SI":
        score += 30
    if row.get("tiene_plan_estudios_o_codpestud") == "SI":
        score += 15
    if row.get("tiene_nivel") == "SI":
        score += 25
    if row.get("tiene_asignatura_ramo") == "SI":
        score += 25
    if row.get("tiene_creditos") == "SI":
        score += 5
    if int(row.get("match_43_codigo_unico") or 0) == 43 or int(row.get("match_43_por_codpestud") or 0) == 43:
        score += 35
    try:
        if int(row.get("filas") or 0) > 43:
            score += 10
    except Exception:  # noqa: BLE001
        pass
    if row.get("penalizacion_matricula_5809") == "SI":
        score -= 120
    return score


def extract_manual_rules() -> pd.DataFrame:
    lines = MANUAL.read_text(encoding="utf-8", errors="replace").splitlines()
    refs = [
        ("criterio_temporalidad", 193, 199, "A", "Proceso y temporalidad", "Carreras/Matrícula"),
        ("identificacion_carreras", 200, 220, "A", "Orden conceptual y completitud Carreras", "Carreras"),
        ("precarga_no_modificable", 211, 220, "A", "Campos precargados y campos a completar", "Carreras"),
        ("anexo_i_carreras_id", 262, 263, "A", "ID carga 16769", "Carreras"),
        ("codigo_unico", 264, 266, "A", "Campo no modificable CODIGO_UNICO", "Carreras"),
        ("plan_estudios", 267, 274, "A", "Plan de estudios", "Carreras"),
        ("duracion_estudios", 292, 296, "A", "DURACION_ESTUDIOS en semestres", "Carreras"),
        ("tipo_unidad_medida", 319, 322, "A", "TIPO_UNIDAD_MEDIDA", "Carreras"),
        ("otra_unidad_medida", 323, 325, "A", "OTRA_UNIDAD_MEDIDA", "Carreras"),
        ("total_unidades", 326, 328, "A", "TOTAL_UNIDADES_MEDIDA", "Carreras"),
        ("unidades_1er_anio", 329, 332, "A", "UNIDADES_1ER_ANIO", "Carreras"),
        ("unidades_2do_7mo_anio", 337, 365, "A", "UNIDADES_2DO_ANIO a UNIDADES_7MO_ANIO", "Carreras"),
        ("vigencia_carreras", 367, 369, "A", "VIGENCIA", "Carreras"),
        ("eliminar_columna_institucion_y_encabezado", 516, 524, "A", "Formato CSV de carga", "Carreras/Matrícula"),
        ("orden_carga", 543, 552, "A", "Carreras antes que Matrícula", "Carreras/Matrícula"),
        ("llave_carga_acumulativa", 555, 559, "A", "Llave acumulativa Carreras", "Carreras"),
        ("errores_carreras", 601, 624, "A", "Mensajes de error de carga Carreras", "Carreras"),
    ]
    rows = []
    for rule_id, start, end, respaldo, regla, alcance in refs:
        text = " ".join(line.strip() for line in lines[start - 1 : end] if line.strip())
        rows.append(
            {
                "regla": regla,
                "referencia_lineas": f"{start}-{end}",
                "texto_manual": text,
                "interpretacion_operativa": manual_interpretation(rule_id),
                "alcance": alcance,
                "nivel_respaldo": respaldo,
            }
        )
    return pd.DataFrame(rows)


def manual_interpretation(rule_id: str) -> str:
    mapping = {
        "criterio_temporalidad": "El plan de estudios vigente durante 2025 es el marco temporal de la estructura informada.",
        "identificacion_carreras": "Carreras identifica programas/planes y debe cargar la estructura del plan antes de Matrícula.",
        "precarga_no_modificable": "No alterar datos ya presentados salvo plan de estudios y vigencia; completar tipo, total y distribución de unidades.",
        "anexo_i_carreras_id": "La carga Carreras corresponde al ID 16769.",
        "codigo_unico": "Conservar desde precarga; no modificable.",
        "plan_estudios": "Usar correlativo; puede modificarse/duplicarse solo si hay más de un plan vigente.",
        "duracion_estudios": "La duración se expresa en semestres y no incluye titulación fuera del plan.",
        "tipo_unidad_medida": "Debe ser código 1, 2 o 3; obligatorio.",
        "otra_unidad_medida": "Solo aplica si TIPO_UNIDAD_MEDIDA=3.",
        "total_unidades": "Debe ser entero y representar el total del plan informado.",
        "unidades_1er_anio": "Debe ser entero y representar unidades del primer año formal del plan.",
        "unidades_2do_7mo_anio": "Cada campo anual debe representar unidades del año formal respectivo del plan.",
        "vigencia_carreras": "0 elimina registro; 1 mantiene registro; obligatorio.",
        "eliminar_columna_institucion_y_encabezado": "Para CSV se elimina CODIGO_IES_NUM y encabezados; estructura fisica de Carreras queda en 21 columnas.",
        "orden_carga": "Carreras debe cargarse antes que Matrícula.",
        "llave_carga_acumulativa": "Carga acumulativa por Código de Institución + Código Único + Plan de Estudios.",
        "errores_carreras": "La plataforma bloquea si el total no suma años o si la distribución no coincide con duración.",
    }
    return mapping.get(rule_id, "")


def build_h106_diagnostics(h106: pd.DataFrame) -> pd.DataFrame:
    errors = []
    for idx, row in h106.iterrows():
        dur = as_int(row.get("DURACION_ESTUDIOS"))
        allowed = ceil_div2(dur)
        for n, col in enumerate(UNIT_COLS, start=1):
            val = as_int(row.get(col))
            if allowed is not None and n > allowed and val > 0:
                errors.append(
                    {
                        "fila_excel_h106": idx + 2,
                        "CODIGO_UNICO": row.get("CODIGO_UNICO", ""),
                        "PLAN_ESTUDIOS": row.get("PLAN_ESTUDIOS", ""),
                        "NOMBRE_CARRERA": row.get("NOMBRE_CARRERA", ""),
                        "DURACION_ESTUDIOS": dur,
                        "ANIOS_PERMITIDOS": allowed,
                        "COLUMNA": col,
                        "ANIO_COLUMNA": n,
                        "VALOR_H106": val,
                        "error": "UNIDADES_FUERA_DE_DURACION",
                        "fuente": str(H106_XLSX),
                        "accion_requerida": "No reutilizar distribución H106; reconstruir desde detalle y validar semántica NIVEL/duración.",
                    }
                )
    return pd.DataFrame(errors)


def select_and_expand_detail(precarga: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    if not CANONICO_PLANES.exists() or not CONCILIACION_43.exists():
        return pd.DataFrame(), pd.DataFrame(), "BLOQUEADO: no existen fuente canónica o conciliación 43."
    canon = read_csv_any(CANONICO_PLANES, sep="\t")
    conc = read_csv_any(CONCILIACION_43, sep="\t")
    needed = ["CODIGO_UNICO", "PLAN_ESTUDIOS", "NOMBRE_CARRERA", "DURACION_ESTUDIOS", "JORNADA", "VERSION"]
    prec = precarga[[c for c in needed if c in precarga.columns]].copy()
    if "CODPESTUD" not in conc.columns:
        return pd.DataFrame(), pd.DataFrame(), "BLOQUEADO: conciliación 43 no contiene CODPESTUD."
    map43 = conc[["CODIGO_UNICO", "CODPESTUD", "CODCARR", "PLAN_DE_ESTUDIO_CANONICO_CIERRE", "CODCARR_CANONICO_CIERRE", "ESTADO_CIERRE", "NIVEL_RESPALDO_DECISION"]].copy()
    map43 = prec.merge(map43, on="CODIGO_UNICO", how="left", suffixes=("", "_CONC"))
    detail = map43.merge(canon, on="CODPESTUD", how="left", suffixes=("_5810", "_CANONICO")).fillna("")
    detail["FUENTE_DETALLE_SELECCIONADA"] = str(CANONICO_PLANES)
    detail["FUENTE_MAPEO_CODIGO_UNICO_CODPESTUD"] = str(CONCILIACION_43)
    detail["MOTIVO_SELECCION"] = (
        "Detalle canónico de planes con CODPESTUD, CODRAMO y NIVEL; cobertura 43/43 mediante conciliación CODIGO_UNICO->CODPESTUD. "
        "Se usa solo para diagnóstico porque la semántica de NIVEL no queda confirmada como regla oficial."
    )
    if "RAMOEQUIV" in detail.columns and (detail["RAMOEQUIV"].astype(str).str.strip() != "").all():
        detail["UNIDAD_ID_USADA"] = detail["RAMOEQUIV"].astype(str).str.strip()
        unidad_msg = "RAMOEQUIV completo."
    elif "CODRAMO" in detail.columns:
        detail["UNIDAD_ID_USADA"] = detail["CODRAMO"].astype(str).str.strip()
        unidad_msg = "CODRAMO usado porque RAMOEQUIV no está completo."
    else:
        detail["UNIDAD_ID_USADA"] = detail.get("NOMBRE", "").astype(str).str.strip().str.upper()
        unidad_msg = "Nombre de asignatura usado por ausencia de código estable."
    detail["LLAVE_UNIDAD_DECISION"] = unidad_msg
    detail["NIVEL_NUM"] = pd.to_numeric(detail.get("NIVEL", ""), errors="coerce")
    detail["ANIO_SIES_CANDIDATO"] = detail["NIVEL_NUM"].apply(lambda x: int(math.ceil(x / 2.0)) if pd.notna(x) else "")
    detail["ANIOS_PERMITIDOS"] = detail["DURACION_ESTUDIOS"].apply(ceil_div2)
    detail["JUSTIFICACION_CONVERSION"] = (
        "Conversión técnica candidata NIVEL 1/2->año 1, 3/4->año 2, etc.; no aplicada como regla final."
    )
    detail["BLOQUEO_CONVERSION"] = detail.apply(block_reason_detail, axis=1)

    selected_summary = pd.DataFrame(
        [
            {
                "fuente_detalle_seleccionada": str(CANONICO_PLANES),
                "fuente_mapeo": str(CONCILIACION_43),
                "cobertura_codigo_unico": f"{map43['CODIGO_UNICO'].nunique()}/43",
                "codpestud_unicos_43": map43["CODPESTUD"].nunique(),
                "filas_detalle_expandido": len(detail),
                "codigos_con_detalle": detail.loc[detail["CODRAMO"].astype(str).str.strip() != "", "CODIGO_UNICO"].nunique()
                if "CODRAMO" in detail.columns
                else 0,
                "unidad_id_usada": unidad_msg,
                "estado": "CANDIDATA_NO_APLICADA",
                "dictamen": "Fuente de detalle útil para diagnóstico, pero no basta para generar CSV mientras NIVEL no esté gobernado y duración no valide.",
            }
        ]
    )
    return detail, selected_summary, "OK"


def block_reason_detail(row: pd.Series) -> str:
    reasons = ["SEMANTICA_NIVEL_NO_CONFIRMADA"]
    nivel = row.get("NIVEL_NUM")
    anio = row.get("ANIO_SIES_CANDIDATO")
    allowed = row.get("ANIOS_PERMITIDOS")
    if pd.isna(nivel):
        reasons.append("NIVEL_NO_NUMERICO")
    else:
        if int(nivel) < 1:
            reasons.append("NIVEL_MENOR_1")
        if int(nivel) > 14:
            reasons.append("NIVEL_MAYOR_14")
    if anio != "" and allowed not in ("", None) and pd.notna(allowed):
        try:
            if int(anio) > int(allowed):
                reasons.append("ANIO_CANDIDATO_FUERA_DE_DURACION")
        except Exception:  # noqa: BLE001
            pass
    return " | ".join(dict.fromkeys(reasons))


def build_distribution(detail: pd.DataFrame, precarga: pd.DataFrame, h106: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if detail.empty:
        empty = pd.DataFrame()
        return empty, empty, empty

    usable = detail[
        (detail["UNIDAD_ID_USADA"].astype(str).str.strip() != "")
        & (detail["ANIO_SIES_CANDIDATO"].astype(str).str.strip() != "")
    ].copy()
    usable["ANIO_SIES_CANDIDATO"] = usable["ANIO_SIES_CANDIDATO"].astype(int)
    usable = usable.drop_duplicates(["CODIGO_UNICO", "UNIDAD_ID_USADA", "ANIO_SIES_CANDIDATO"])

    dist_rows = []
    for _, row in precarga.iterrows():
        code = str(row["CODIGO_UNICO"]).strip()
        subset = usable[usable["CODIGO_UNICO"].astype(str).str.strip() == code]
        counts = subset.groupby("ANIO_SIES_CANDIDATO")["UNIDAD_ID_USADA"].nunique().to_dict()
        dur = as_int(row["DURACION_ESTUDIOS"])
        allowed = ceil_div2(dur)
        dist = {col: int(counts.get(i, 0)) for i, col in enumerate(UNIT_COLS, start=1)}
        total_unique = int(subset["UNIDAD_ID_USADA"].nunique())
        sum_years = sum(dist.values())
        outside = sum(v for i, v in enumerate(dist.values(), start=1) if allowed is not None and i > allowed)
        inside_empty = [
            str(i)
            for i, col in enumerate(UNIT_COLS, start=1)
            if allowed is not None and i <= allowed and int(dist[col]) == 0
        ]
        status = "BLOQUEADO"
        reasons = ["SEMANTICA_NIVEL_NO_CONFIRMADA"]
        if subset.empty:
            reasons.append("SIN_DETALLE_ASIGNATURAS")
        if outside > 0:
            reasons.append("UNIDADES_FUERA_DE_DURACION")
        if total_unique != sum_years:
            reasons.append("UNIDAD_ID_EN_MULTIPLES_ANIOS")
        if inside_empty:
            reasons.append("ANIOS_DENTRO_DURACION_SIN_UNIDADES_REVISAR")
        if not outside and not subset.empty and total_unique == sum_years and not inside_empty:
            status = "BLOQUEADO_POR_SEMANTICA_NIVEL"
        dist_rows.append(
            {
                "CODIGO_UNICO": code,
                "PLAN_ESTUDIOS": row.get("PLAN_ESTUDIOS", ""),
                "NOMBRE_CARRERA": row.get("NOMBRE_CARRERA", ""),
                "DURACION_ESTUDIOS": dur,
                "ANIOS_PERMITIDOS": allowed,
                "TOTAL_UNIDADES_MEDIDA": total_unique,
                **dist,
                "SUMA_ANIOS": sum_years,
                "VALIDACION_TOTAL": "OK" if total_unique == sum_years else "BLOQUEO_TOTAL_DIFIERE_DE_SUM_ANIOS",
                "UNIDADES_FUERA_DURACION": outside,
                "VALIDACION_DURACION": "OK" if outside == 0 else "BLOQUEO_UNIDADES_FUERA_DURACION",
                "ANIOS_DENTRO_DURACION_SIN_UNIDADES": " | ".join(inside_empty),
                "ESTADO_FILA": status,
                "MOTIVO_ESTADO": " | ".join(dict.fromkeys(reasons)),
            }
        )
    distribution = pd.DataFrame(dist_rows)

    comp = h106[[c for c in ["CODIGO_UNICO", "PLAN_ESTUDIOS", "NOMBRE_CARRERA", "DURACION_ESTUDIOS", "TOTAL_UNIDADES_MEDIDA", *UNIT_COLS] if c in h106.columns]].copy()
    rename = {"TOTAL_UNIDADES_MEDIDA": "TOTAL_H106"}
    rename.update({col: f"{col}_H106" for col in UNIT_COLS})
    comp = comp.rename(columns=rename)
    reco = distribution[["CODIGO_UNICO", "TOTAL_UNIDADES_MEDIDA", *UNIT_COLS, "VALIDACION_DURACION", "ESTADO_FILA", "MOTIVO_ESTADO"]].rename(
        columns={"TOTAL_UNIDADES_MEDIDA": "TOTAL_RECONSTRUIDO", **{col: f"{col}_RECONSTRUIDO" for col in UNIT_COLS}}
    )
    comp = comp.merge(reco, on="CODIGO_UNICO", how="left")
    for col in ["TOTAL", *[c.replace("UNIDADES_", "") for c in UNIT_COLS]]:
        pass
    comp["DIF_TOTAL"] = comp["TOTAL_RECONSTRUIDO"].apply(as_int) - comp["TOTAL_H106"].apply(as_int)
    for col in UNIT_COLS:
        comp[f"DIF_{col}"] = comp[f"{col}_RECONSTRUIDO"].apply(as_int) - comp[f"{col}_H106"].apply(as_int)
    comp["motivo_rechazo_anterior"] = "H106 conserva suma total, pero ubica unidades en años mayores al techo(DURACION_ESTUDIOS/2)."

    errors = []
    for _, row in distribution.iterrows():
        if row["ESTADO_FILA"] != "BLOQUEADO_POR_SEMANTICA_NIVEL":
            errors.append(
                {
                    "fila": "",
                    "carrera": row["NOMBRE_CARRERA"],
                    "codigo": row["CODIGO_UNICO"],
                    "error": row["MOTIVO_ESTADO"],
                    "fuente": str(CANONICO_PLANES),
                    "accion_requerida": "Confirmar semantica NIVEL y periodizacion anual por plan antes de generar CSV.",
                }
            )
        elif "SEMANTICA_NIVEL_NO_CONFIRMADA" in row["MOTIVO_ESTADO"]:
            errors.append(
                {
                    "fila": "",
                    "carrera": row["NOMBRE_CARRERA"],
                    "codigo": row["CODIGO_UNICO"],
                    "error": "SEMANTICA_NIVEL_NO_CONFIRMADA",
                    "fuente": str(CANONICO_PLANES),
                    "accion_requerida": "Validacion funcional/documental de NIVEL requerida.",
                }
            )
    return distribution, comp, pd.DataFrame(errors)


def build_trazabilidad_columns() -> pd.DataFrame:
    rows = []
    for col in SIES_21_COLS:
        if col in {
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
            "VIGENCIA",
        }:
            rows.append(
                {
                    "columna_sies": col,
                    "origen": "Precarga 5810",
                    "tratamiento": "Conservar desde precarga; PLAN_ESTUDIOS/VIGENCIA solo ajustables bajo regla oficial.",
                    "nivel_respaldo": "A/B",
                    "observacion": "Manual define no modificables y excepciones; no se alteran fuentes originales.",
                }
            )
        elif col == "TIPO_UNIDAD_MEDIDA":
            rows.append(
                {
                    "columna_sies": col,
                    "origen": "Manual + fuente detalle candidata",
                    "tratamiento": "Debe ser 1, 2 o 3; no fijar definitivo sin validar unidad institucional del plan.",
                    "nivel_respaldo": "A/B/E",
                    "observacion": "Manual entrega catálogo oficial; dato observado de malla no reemplaza decisión funcional.",
                }
            )
        elif col == "OTRA_UNIDAD_MEDIDA":
            rows.append(
                {
                    "columna_sies": col,
                    "origen": "Manual",
                    "tratamiento": "Solo completar si TIPO_UNIDAD_MEDIDA=3.",
                    "nivel_respaldo": "A",
                    "observacion": "Pendiente si se define tipo 3; no aplica si tipo 1/2.",
                }
            )
        else:
            rows.append(
                {
                    "columna_sies": col,
                    "origen": "Fuente detalle canónica de planes + conversión NIVEL->año candidata",
                    "tratamiento": "Diagnóstico solamente; no materializar mientras NIVEL y duración no estén gobernados.",
                    "nivel_respaldo": "B/C/E",
                    "observacion": "No usar matriz agregada H106 si contradice duración; reconstrucción requiere detalle y validación funcional.",
                }
            )
    return pd.DataFrame(rows)


def build_kpi(
    precarga: pd.DataFrame,
    inventory: pd.DataFrame,
    distribution: pd.DataFrame,
    h106_errors: pd.DataFrame,
    detail: pd.DataFrame,
) -> pd.DataFrame:
    levels_15_20_sources = 0
    if not inventory.empty and "niveles_15_20" in inventory.columns:
        levels_15_20_sources = int((inventory["niveles_15_20"].astype(str).str.strip() != "").sum())
    if distribution.empty:
        blocked = len(precarga)
        apt = 0
    else:
        blocked = int(distribution["ESTADO_FILA"].astype(str).str.contains("BLOQUEADO").sum())
        apt = int((distribution["ESTADO_FILA"] == "APTA_DIAGNOSTICO").sum())
    total_by_year = {}
    if not distribution.empty:
        total_by_year = {col: int(distribution[col].apply(as_int).sum()) for col in UNIT_COLS}
    rows = [
        {"indicador": "filas_precarga_5810", "valor": len(precarga)},
        {"indicador": "columnas_precarga_5810", "valor": len(precarga.columns)},
        {"indicador": "columnas_sies_sin_codigo_ies", "valor": len(SIES_21_COLS)},
        {"indicador": "carreras_codigo_unico_unico", "valor": precarga["CODIGO_UNICO"].nunique()},
        {"indicador": "duplicados_codigo_unico_plan_precarga", "valor": int(precarga.duplicated(["CODIGO_UNICO", "PLAN_ESTUDIOS"]).sum())},
        {"indicador": "fuentes_hojas_inventariadas", "valor": len(inventory)},
        {"indicador": "fuentes_con_niveles_15_20_detectadas", "valor": levels_15_20_sources},
        {"indicador": "h106_filas_con_unidades_fuera_duracion", "valor": h106_errors["CODIGO_UNICO"].nunique() if not h106_errors.empty else 0},
        {"indicador": "h106_errores_unidades_fuera_duracion", "valor": len(h106_errors)},
        {"indicador": "detalle_expandido_filas", "valor": len(detail)},
        {"indicador": "carreras_bloqueadas_diagnostico", "valor": blocked},
        {"indicador": "carreras_aptas_diagnostico", "valor": apt},
        {"indicador": "estado_final", "valor": "BLOQUEADO" if blocked else "APTO_PARA_GENERAR_CSV"},
    ]
    for col, value in total_by_year.items():
        rows.append({"indicador": f"total_reconstruido_{col.lower()}", "valor": value})
    return pd.DataFrame(rows)


def to_sheet(writer: pd.ExcelWriter, df: pd.DataFrame, sheet: str) -> None:
    safe = sheet[:31]
    out = df.copy()
    if out.empty:
        out = pd.DataFrame([{"sin_datos": ""}])
    # Excel tiene limite de filas, pero este diagnostico queda muy por debajo.
    out.to_excel(writer, sheet_name=safe, index=False)
    ws = writer.book[safe]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col_cells in ws.columns:
        header = str(col_cells[0].value or "")
        width = min(max(len(header) + 2, 12), 60)
        ws.column_dimensions[col_cells[0].column_letter].width = width


def make_manifest(
    excel_out: Path,
    informe_out: Path,
    manifest_out: Path,
    script_out: Path,
    estado_final: str,
    fuentes: list[Path],
) -> dict[str, Any]:
    return {
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "Carreras Avance Curricular 2026 / ID Carga SIES 16769",
        "hito": "109_diagnostico_gobernado_carreras_16769",
        "fecha_ejecucion": TS,
        "estado_final": estado_final,
        "declaracion_carga": "NO_LISTO_PARA_CARGA" if estado_final == "BLOQUEADO" else "PENDIENTE_SEGUNDA_ETAPA",
        "fuentes_originales_modificadas": "NO",
        "csv_final_generado": "NO",
        "sies_ready_generado": "NO",
        "restricciones": [
            "No se modifican fuentes originales.",
            "No se genera CSV final de carga.",
            "No se genera SIES_READY.",
            "No se usa PROMEDIOS como fuente normativa para Carreras.",
            "No se redistribuyen manualmente unidades fuera de duración.",
        ],
        "entradas": [{"ruta": str(p), "existe": p.exists(), "sha256": sha256(p)} for p in fuentes],
        "salidas": {
            "excel": str(excel_out),
            "informe": str(informe_out),
            "manifest": str(manifest_out),
            "script": str(script_out),
            "carpeta_escritorio": str(DESKTOP),
        },
    }


def write_report(
    path: Path,
    estado_final: str,
    resumen: pd.DataFrame,
    kpi: pd.DataFrame,
    selected_summary: pd.DataFrame,
    distribution: pd.DataFrame,
) -> None:
    rows = {str(r["indicador"]): r["valor"] for _, r in kpi.iterrows()}
    selected_dict = selected_summary.iloc[0].to_dict() if not selected_summary.empty else {}
    blocked_rows = 0 if distribution.empty else int(distribution["ESTADO_FILA"].astype(str).str.contains("BLOQUEADO").sum())
    text = f"""# Diagnóstico gobernado Carreras Avance Curricular 2026 / ID 16769

## Dictamen

Estado final: **{estado_final}**.

Declaración de carga: **NO_LISTO_PARA_CARGA**.

No se modificaron fuentes originales, no se corrigieron datos, no se generó CSV final y no se generó SIES_READY.

## A. Regla oficial

El instructivo oficial indica que la carga Carreras Avance Curricular 2026 corresponde al ID 16769, se realiza antes de Matrícula, usa la estructura del Anexo I, requiere eliminar la primera columna de institución y los encabezados para el CSV, y define DURACION_ESTUDIOS en semestres. También define TOTAL_UNIDADES_MEDIDA y UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO como enteros asociados a la distribución formal del plan.

El Anexo IV contiene el error de plataforma: “Distribución de unidades de medida no coincide con duración de la carrera”, además de la validación de suma total contra años.

## B. Dato observado

La precarga 5810 contiene {rows.get('filas_precarga_5810')} filas y {rows.get('columnas_precarga_5810')} columnas. La estructura física de carga queda en {rows.get('columnas_sies_sin_codigo_ies')} columnas al excluir CODIGO_IES_NUM, consistente con la indicación del manual y con la validación previa de plataforma.

El H106 tiene 43 filas y 21 columnas, pero al reproducir la validación por duración presenta {rows.get('h106_filas_con_unidades_fuera_duracion')} filas con unidades fuera de duración y {rows.get('h106_errores_unidades_fuera_duracion')} celdas con UNIDADES_N_ANIO en años mayores al techo(DURACION_ESTUDIOS/2).

La fuente de detalle candidata seleccionada es:

`{selected_dict.get('fuente_detalle_seleccionada', '')}`

El cruce hacia las 43 carreras se obtiene mediante:

`{selected_dict.get('fuente_mapeo', '')}`

## C. Implementación técnica

Se reconstruyó una distribución diagnóstica desde detalle de asignaturas/planes usando CODPESTUD como puente trazable hacia CODIGO_UNICO. La unidad estable usada fue: {selected_dict.get('unidad_id_usada', '')}.

La conversión NIVEL -> año SIES se calculó solo como escenario técnico candidato para auditar duración. No fue aplicada como regla final.

## D. Decisión interna

El procedimiento penaliza hojas de Matrícula 5809 y PROMEDIOS para el ranking de Carreras. PROMEDIOS no se usa como fuente normativa ni como fuente de estructura de Carreras.

## E. Pendiente

NIVEL no queda gobernado como semestre ni como año formal por el manual. Hay {blocked_rows} carreras bloqueadas en el diagnóstico por semántica de NIVEL, duración o necesidad de revisión. Por tanto no corresponde generar CSV final todavía.

## Conclusión

El diagnóstico corrige el rumbo de H108A: prioriza detalle de mallas/planes/asignaturas y deja fuera las hojas de matrícula 5809 como fuente de estructura de Carreras. Sin embargo, la evidencia local disponible no permite cerrar de forma automática la conversión de NIVEL a distribución anual SIES ni redistribuir unidades fuera de duración.

No se propone comando de generación de CSV final mientras el estado sea BLOQUEADO.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)

    print("[1/7] Leyendo manual y precarga 5810...", flush=True)
    manual_rules = extract_manual_rules()
    precarga = pd.read_csv(PRECARGA_5810, sep=";", encoding="latin1", dtype=str).fillna("")
    precarga_codes = set(precarga["CODIGO_UNICO"].astype(str).str.strip())
    precarga_pairs = set(zip(precarga["CODIGO_UNICO"].astype(str).str.strip(), precarga["PLAN_ESTUDIOS"].astype(str).str.strip()))

    print("[2/7] Reproduciendo rechazo por duración de H106...", flush=True)
    h106 = pd.read_excel(H106_XLSX, sheet_name="CARGA_SIES_16769_21C", dtype=str).fillna("")
    h106_errors = build_h106_diagnostics(h106)

    print("[3/7] Inventariando fuentes de detalle y penalizando matrícula 5809...", flush=True)
    conc43 = read_csv_any(CONCILIACION_43, sep="\t") if CONCILIACION_43.exists() else pd.DataFrame()
    inventory = inventory_sources(precarga_codes, precarga_pairs, conc43)

    print("[4/7] Expandiendo fuente detalle candidata y simulando conversión NIVEL->año...", flush=True)
    detail, selected_summary, selected_status = select_and_expand_detail(precarga)
    distribution, comparison_h106, blocking_errors_reco = build_distribution(detail, precarga, h106)

    print("[5/7] Armando dictamen, trazabilidad y KPI...", flush=True)
    h106_error_summary = (
        h106_errors.groupby(["COLUMNA"], dropna=False)
        .size()
        .reset_index(name="errores_h106")
        .sort_values("COLUMNA")
        if not h106_errors.empty
        else pd.DataFrame(columns=["COLUMNA", "errores_h106"])
    )
    blocking_errors = pd.concat(
        [
            h106_errors.rename(columns={"CODIGO_UNICO": "codigo", "NOMBRE_CARRERA": "carrera"})[
                ["fila_excel_h106", "carrera", "codigo", "error", "fuente", "accion_requerida"]
            ].rename(columns={"fila_excel_h106": "fila"}),
            blocking_errors_reco,
        ],
        ignore_index=True,
    ).fillna("")
    trazabilidad = build_trazabilidad_columns()
    kpi = build_kpi(precarga, inventory, distribution, h106_errors, detail)
    estado_final = "BLOQUEADO" if str(kpi.loc[kpi["indicador"] == "estado_final", "valor"].iloc[0]) == "BLOQUEADO" else "APTO_PARA_GENERAR_CSV"

    resumen = pd.DataFrame(
        [
            {"campo": "proceso", "valor": "Avance Curricular SIES 2026"},
            {"campo": "carga", "valor": "Carreras Avance Curricular 2026"},
            {"campo": "id_carga", "valor": "16769"},
            {"campo": "manual_usado", "valor": str(MANUAL)},
            {"campo": "precarga_usada", "valor": str(PRECARGA_5810)},
            {"campo": "fuente_detalle_seleccionada", "valor": str(CANONICO_PLANES)},
            {"campo": "fuente_mapeo_codigo_unico_codpestud", "valor": str(CONCILIACION_43)},
            {"campo": "estado_final", "valor": estado_final},
            {"campo": "declaracion_carga", "valor": "NO_LISTO_PARA_CARGA"},
            {"campo": "csv_final_generado", "valor": "NO"},
            {"campo": "fuentes_originales_modificadas", "valor": "NO"},
            {
                "campo": "motivo_si_bloqueado",
                "valor": (
                    "NIVEL no está gobernado como semestre/año formal; H106 tiene 42 filas y 83 celdas fuera de duración; "
                    "no se debe redistribuir manualmente sin fuente/decisión funcional."
                    if estado_final == "BLOQUEADO"
                    else ""
                ),
            },
            {"campo": "estado_fuente_detalle", "valor": selected_status},
        ]
    )

    manifest_legible_fuentes = pd.DataFrame(
        [
            {"tipo": "manual", "ruta": str(MANUAL), "existe": MANUAL.exists(), "sha256": sha256(MANUAL)},
            {"tipo": "precarga_5810", "ruta": str(PRECARGA_5810), "existe": PRECARGA_5810.exists(), "sha256": sha256(PRECARGA_5810)},
            {"tipo": "canonico_planes", "ruta": str(CANONICO_PLANES), "existe": CANONICO_PLANES.exists(), "sha256": sha256(CANONICO_PLANES)},
            {"tipo": "conciliacion_43", "ruta": str(CONCILIACION_43), "existe": CONCILIACION_43.exists(), "sha256": sha256(CONCILIACION_43)},
            {"tipo": "desbloqueo_43_h106_fuente", "ruta": str(DESBLOQUEO_43), "existe": DESBLOQUEO_43.exists(), "sha256": sha256(DESBLOQUEO_43)},
            {"tipo": "h106_xlsx", "ruta": str(H106_XLSX), "existe": H106_XLSX.exists(), "sha256": sha256(H106_XLSX)},
            {"tipo": "h106_manifest", "ruta": str(H106_MANIFEST), "existe": H106_MANIFEST.exists(), "sha256": sha256(H106_MANIFEST)},
        ]
    )

    excel_out = SALIDA / "DIAGNOSTICO_GOBERNADO_CARRERAS_16769.xlsx"
    informe_out = SALIDA / "INFORME_DIAGNOSTICO_GOBERNADO_CARRERAS_16769.md"
    manifest_out = SALIDA / "manifest_diagnostico_gobernado_carreras_16769.json"
    script_out = SALIDA / "diagnostico_gobernado_carreras_16769.py"

    print("[6/7] Escribiendo Excel, informe, manifest y script...", flush=True)
    with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
        to_sheet(writer, resumen, "00_RESUMEN")
        to_sheet(writer, manual_rules, "01_REGLAS_MANUAL")
        to_sheet(writer, precarga, "02_PRECARGA_5810")
        to_sheet(writer, inventory, "03_INVENTARIO_FUENTES_DETALLE")
        to_sheet(writer, selected_summary, "04_FUENTE_DETALLE_SELECCIONADA")
        cols_conversion = [
            "CODIGO_UNICO",
            "PLAN_ESTUDIOS",
            "NOMBRE_CARRERA",
            "DURACION_ESTUDIOS",
            "ANIOS_PERMITIDOS",
            "CODPESTUD",
            "CODRAMO",
            "RAMOEQUIV",
            "NOMBRE",
            "NIVEL",
            "NIVEL_NUM",
            "ANIO_SIES_CANDIDATO",
            "UNIDAD_ID_USADA",
            "JUSTIFICACION_CONVERSION",
            "BLOQUEO_CONVERSION",
            "FUENTE_DETALLE_SELECCIONADA",
        ]
        to_sheet(writer, detail[[c for c in cols_conversion if c in detail.columns]], "05_CONVERSION_NIVEL_A_ANIO")
        to_sheet(writer, distribution, "06_DISTRIBUCION_RECONSTRUIDA")
        to_sheet(writer, comparison_h106, "07_COMPARACION_CON_H106")
        to_sheet(writer, blocking_errors, "08_ERRORES_BLOQUEANTES")
        to_sheet(writer, trazabilidad, "09_TRAZABILIDAD_COLUMNAS")
        to_sheet(writer, kpi, "10_KPI")
        to_sheet(writer, manifest_legible_fuentes, "11_MANIFEST")

    write_report(informe_out, estado_final, resumen, kpi, selected_summary, distribution)
    manifest = make_manifest(
        excel_out,
        informe_out,
        manifest_out,
        script_out,
        estado_final,
        [MANUAL, PRECARGA_5810, CANONICO_PLANES, CONCILIACION_43, DESBLOQUEO_43, H106_XLSX, H106_CSV, H106_MANIFEST],
    )
    manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(Path(__file__).resolve(), script_out)

    print("[7/7] Copiando paquete al Escritorio...", flush=True)
    if DESKTOP.exists():
        shutil.rmtree(DESKTOP)
    shutil.copytree(SALIDA, DESKTOP)

    def print_table(title: str, df: pd.DataFrame, n: int = 12) -> None:
        print(f"\n{title}")
        if df.empty:
            print("(sin datos)")
        else:
            print(df.head(n).to_string(index=False))

    print("\nDIAGNÓSTICO GOBERNADO CARRERAS 16769 — GENERADO")
    print("Fuentes originales modificadas: NO")
    print("CSV final generado: NO")
    print("SIES_READY generado: NO")
    print("Declaración carga: NO_LISTO_PARA_CARGA")
    print(f"Estado final: {estado_final}")
    print_table("RESUMEN", resumen)
    print_table("KPI", kpi, 20)
    print_table("H106 UNIDADES FUERA DURACIÓN", h106_error_summary)
    print_table("FUENTE DETALLE SELECCIONADA", selected_summary)
    print_table("ERRORES BLOQUEANTES", blocking_errors, 20)
    print("\nARCHIVOS")
    print(f"Excel: {excel_out}")
    print(f"Informe: {informe_out}")
    print(f"Manifest: {manifest_out}")
    print(f"Script: {script_out}")
    print(f"Carpeta escritorio: {DESKTOP}")


if __name__ == "__main__":
    main()
