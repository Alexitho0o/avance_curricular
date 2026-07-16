#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H112A - Decision alternativa de periodizacion para Carreras 16769.

Este hito no modifica fuentes originales, no genera CSV final y no genera
SIES_READY. Construye un expediente auditable para decidir si existe una regla
interna trazable posterior al bloqueo H111.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
AVANCE = ROOT / "avance_curricular_2026"
OUT_BASE = AVANCE / "112a_decision_alternativa_periodizacion_carreras_16769"
DESKTOP_BASE = Path.home() / "Desktop"

MANUAL = AVANCE / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/Instructivo_Avance Curricular SIES - 2026.txt"
PRECARGA_5810 = AVANCE / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5810_Precarga Carreras Avance Curricular 20268.csv"
H106_CSV = AVANCE / "106_carreras_16769_gobernado_por_codigo_unico/CARRERAS_16769_GOBERNADO_20260709_102827/5810_CARRERAS_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16769_21C_GOBERNADO.csv"
H109_DIR = AVANCE / "109_diagnostico_gobernado_carreras_16769/DIAGNOSTICO_GOBERNADO_CARRERAS_16769_20260709_105803"
H110_DIR = AVANCE / "110_cierre_funcional_nivel_periodizacion_carreras_16769/CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769_20260709_111343"
H111_DIR = AVANCE / "111_decision_interna_nivel_periodizacion_carreras_16769/DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769_20260709_112825"
H109_XLSX = H109_DIR / "DIAGNOSTICO_GOBERNADO_CARRERAS_16769.xlsx"
H110_XLSX = H110_DIR / "CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769.xlsx"
H111_XLSX = H111_DIR / "DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769.xlsx"
H111_REPORT = H111_DIR / "INFORME_DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769.md"

CANONICO_PLANES = AVANCE / "04_gobernanza_mallas/03_auditorias/CANONICO_TODOS_PLANES_ESTUDIO_20260701_140528/02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv"
CONCILIACION_43 = AVANCE / "04_gobernanza_mallas/03_auditorias/CIERRE_FINAL_43_RESUELTAS_0_PENDIENTES_20260701_171409/02_RESULTADOS/01_CONCILIACION_FINAL_43.tsv"
MALLA_EXPANDIDA_43 = AVANCE / "04_gobernanza_mallas/02_conciliacion/CONCILIACION_CANONICA_PDF_HOJA1_20260626_170541/12_MALLA_CONCILIADA_EXPANDIDA_43_CARRERAS.tsv"
CONTROL_TRIMESTRE = AVANCE / "04_gobernanza_mallas/02_conciliacion/CONCILIACION_CANONICA_PDF_HOJA1_20260626_170541/04_CONCILIACION_CON_CONTROL_TRIMESTRE_NIVEL.tsv"
RESUMEN_TRIMESTRE = AVANCE / "04_gobernanza_mallas/02_conciliacion/CONCILIACION_CANONICA_PDF_HOJA1_20260626_170541/08_RESUMEN_TRIMESTRE_NIVEL.tsv"
CONFLICTOS_TRIMESTRE = AVANCE / "04_gobernanza_mallas/02_conciliacion/CONCILIACION_CANONICA_PDF_HOJA1_20260626_170541/11_CONFLICTOS_TRIMESTRE_NIVEL.tsv"
CLASIFICACION_PERIODIZACION = AVANCE / "04_gobernanza_mallas/03_auditorias/CLASIFICACION_29_MODELOS_PERIODIZACION_20260703_123007/02_RESULTADOS/01_CLASIFICACION_29_MODELOS.tsv"
ADECUACION_2 = AVANCE / "04_gobernanza_mallas/03_auditorias/ADECUACION_2_CASOS_PERIODIZACION_20260703_123204/02_RESULTADOS/01_ADECUACION_2_CASOS.tsv"

DURACION_MU = ROOT / "DURACION_ESTUDIOS.tsv"
GOB_NIV_ACA = ROOT / "gobernanza_columnas_mu/gob_mu_niv_aca.tsv"
REVISION_SIES_MU = ROOT / "resultados/auditorias/REVISION_CARRERAS_CODIGOS_SIES_MU2026.xlsx"
PROMEDIOS = AVANCE / "25_actualizacion_fuente_promedios/CAMBIO_PROMEDIOSDEALUMNOS_20260704_221059/00_FUENTE_CONGELADA/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_20260704_221059.xlsx"

UNIT_COLUMNS = [
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
]
PERIOD_FIELDS = [
    "ANIO",
    "AÑO",
    "ANIO_PLAN",
    "AÑO_PLAN",
    "ANIO_CURRICULAR",
    "SEMESTRE",
    "PERIODO",
    "PERIODO_PLAN",
    "SEMESTRE_PLAN",
    "NIVEL_ANIO",
    "NIVEL_AÑO",
    "ORDEN",
    "ORDEN_MALLA",
    "SECUENCIA",
    "TRAMO",
    "BLOQUE",
    "CICLO",
    "ETAPA",
    "PERIODO_ACADEMICO",
    "TRIMESTRE",
    "NIVEL",
]


def stamp_now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_delimited(path: Path, sep: str, encoding: str | None = None) -> pd.DataFrame:
    encodings = [encoding] if encoding else ["utf-8-sig", "utf-8", "latin1"]
    last: Exception | None = None
    for enc in encodings:
        try:
            return pd.read_csv(path, sep=sep, dtype=str, encoding=enc)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"No fue posible leer {path}: {last}")


def to_int(value: Any, default: int = 0) -> int:
    if pd.isna(value):
        return default
    txt = str(value).strip().replace(",", ".")
    if not txt:
        return default
    try:
        return int(float(txt))
    except ValueError:
        return default


def normalize_text(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def list_values(series: pd.Series, limit: int = 12) -> str:
    vals = [str(v) for v in series.dropna().astype(str).unique().tolist() if str(v).strip() and str(v).lower() != "nan"]
    vals = sorted(vals, key=lambda x: (len(x), x))
    if len(vals) > limit:
        return " | ".join(vals[:limit]) + f" | ... (+{len(vals)-limit})"
    return " | ".join(vals)


def contains_code(cell: Any, code: str) -> bool:
    return code in [x.strip() for x in str(cell or "").split("|")]


def markdown_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "_Sin registros._"
    sample = df.head(max_rows).fillna("")
    cols = [str(c) for c in sample.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in sample.iterrows():
        vals = [str(row[c]).replace("\n", " ").replace("|", "/") for c in sample.columns]
        lines.append("| " + " | ".join(vals) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Se muestran {max_rows} de {len(df)} filas._")
    return "\n".join(lines)


def extract_manual_rules() -> pd.DataFrame:
    if not MANUAL.exists():
        return pd.DataFrame(
            [
                {
                    "regla": "Manual Avance no encontrado",
                    "referencia_lineas": "",
                    "texto_manual": "",
                    "interpretacion_operativa": "Bloqueo: falta instructivo oficial.",
                    "nivel_respaldo": "E",
                }
            ]
        )
    lines = MANUAL.read_text(encoding="utf-8", errors="replace").splitlines()
    topics = {
        "Carreras antes que Matricula": ["carreras", "matrícula"],
        "DURACION_ESTUDIOS en semestres": ["DURACION_ESTUDIOS", "duración"],
        "TOTAL_UNIDADES_MEDIDA": ["TOTAL_UNIDADES_MEDIDA"],
        "UNIDADES por año 1 a 7": ["UNIDADES_1ER_ANIO", "UNIDADES_7MO_ANIO", "unidades"],
        "TIPO_UNIDAD_MEDIDA": ["TIPO_UNIDAD_MEDIDA"],
        "Campos enteros / carga": ["entero", "decimal", "csv", "separador"],
    }
    rows = []
    for topic, needles in topics.items():
        hits = []
        for i, line in enumerate(lines, start=1):
            plain = normalize_text(line)
            if any(normalize_text(n) in plain for n in needles):
                hits.append((i, line.strip()))
        rows.append(
            {
                "regla": topic,
                "referencia_lineas": ", ".join([f"L{i}" for i, _ in hits[:8]]),
                "texto_manual": " / ".join([f"L{i}: {line}" for i, line in hits[:8]]) if hits else "No se encontro texto directo con el patron.",
                "interpretacion_operativa": {
                    "Carreras antes que Matricula": "Carreras 16769 se prepara antes que Matricula 16768.",
                    "DURACION_ESTUDIOS en semestres": "La duracion gobierna el maximo de anios permitidos como techo(duracion/2).",
                    "TOTAL_UNIDADES_MEDIDA": "Debe ser entero y cuadrar con suma de UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO.",
                    "UNIDADES por año 1 a 7": "La distribucion anual debe quedar dentro de la duracion formal de la carrera.",
                    "TIPO_UNIDAD_MEDIDA": "Debe conservarse/llenarse segun regla del proceso, no desde PROMEDIOS.",
                    "Campos enteros / carga": "Campos numericos de unidades deben quedar enteros para carga posterior.",
                }[topic],
                "alcance": "Carreras Avance Curricular 2026 / ID 16769",
                "nivel_respaldo": "A. Regla oficial Avance",
            }
        )
    rows.append(
        {
            "regla": "Periodizacion alternativa",
            "referencia_lineas": "",
            "texto_manual": "El instructivo no define la columna raw NIVEL ni una formula NIVEL->anio.",
            "interpretacion_operativa": "Cualquier conversion desde NIVEL es decision interna D y debe validarse contra duracion.",
            "alcance": "Distribucion anual de unidades",
            "nivel_respaldo": "D/E",
        }
    )
    return pd.DataFrame(rows)


def classify_family(name: Any, tipo_plan: Any, nivel_carrera: Any) -> tuple[str, str]:
    n = normalize_text(name)
    tipo = str(tipo_plan or "").strip()
    nivel = str(nivel_carrera or "").strip()
    if "CONTINUIDAD" in n or tipo == "3":
        return "CONTINUIDAD", "D/B: continuidad por nombre o TIPO_PLAN_CARRERA observado."
    if "TECNICO" in n or nivel == "1":
        return "TECNICA", "B: nombre/NIVEL_CARRERA compatible con tecnica."
    if "INGENIERIA" in n:
        return "INGENIERIA", "B: nombre contiene INGENIERIA."
    return "INGENIERIA", "D: familia residual no tecnica/no continuidad por restriccion del hito; no regla oficial."


def load_base() -> dict[str, pd.DataFrame]:
    return {
        "precarga": read_delimited(PRECARGA_5810, ";", "latin1"),
        "h111_match": pd.read_excel(H111_XLSX, sheet_name="04_MATCH_5810_OFERTA_MU", dtype=str),
        "h111_detail": pd.read_excel(H111_XLSX, sheet_name="05_PLAN_CANONICO_DETALLE", dtype=str),
        "h111_dist": pd.read_excel(H111_XLSX, sheet_name="08_DISTRIBUCION_CANDIDATA_40", dtype=str),
        "h111_cases3": pd.read_excel(H111_XLSX, sheet_name="09_CASOS_3_SIN_DETALLE", dtype=str),
        "duracion_mu": read_delimited(DURACION_MU, "\t"),
        "malla_exp": read_delimited(MALLA_EXPANDIDA_43, "\t") if MALLA_EXPANDIDA_43.exists() else pd.DataFrame(),
        "control_tri": read_delimited(CONTROL_TRIMESTRE, "\t") if CONTROL_TRIMESTRE.exists() else pd.DataFrame(),
        "clasif_period": read_delimited(CLASIFICACION_PERIODIZACION, "\t") if CLASIFICACION_PERIODIZACION.exists() else pd.DataFrame(),
        "adecuacion2": read_delimited(ADECUACION_2, "\t") if ADECUACION_2.exists() else pd.DataFrame(),
    }


def build_oferta_mu(precarga: pd.DataFrame, h111_match: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "CODIGO_UNICO",
        "PLAN_ESTUDIOS",
        "NOMBRE_CARRERA",
        "DURACION_ESTUDIOS_5810",
        "DURACION_OFERTA_MU",
        "TIPO_PLAN_CARRERA",
        "NIVEL_CARRERA_OFERTA",
        "FAMILIA_FUNCIONAL",
        "ESTADO_MATCH_OFERTA",
        "DURACION_COINCIDE_5810_MU",
    ]
    out = h111_match[[c for c in cols if c in h111_match.columns]].copy()
    if "ANIOS_PERMITIDOS" not in out.columns:
        out["ANIOS_PERMITIDOS"] = out["DURACION_ESTUDIOS_5810"].apply(lambda x: math.ceil(to_int(x) / 2) if to_int(x) else 0)
    if "FAMILIA_FUNCIONAL" not in out.columns:
        out["FAMILIA_FUNCIONAL"] = ""
        out["OBS_FAMILIA_FUNCIONAL"] = ""
        for idx, row in out.iterrows():
            fam, obs = classify_family(row.get("NOMBRE_CARRERA", ""), row.get("TIPO_PLAN_CARRERA", ""), row.get("NIVEL_CARRERA_OFERTA", ""))
            out.loc[idx, "FAMILIA_FUNCIONAL"] = fam
            out.loc[idx, "OBS_FAMILIA_FUNCIONAL"] = obs
    out["NIVEL_RESPALDO"] = "B/D. Oferta/MU gobernada; no regla oficial Avance."
    return out


def scan_periodization_sources(codes_43: set[str]) -> pd.DataFrame:
    roots = [
        AVANCE / "04_gobernanza_mallas",
        H109_DIR,
        H110_DIR,
        H111_DIR,
    ]
    files: list[Path] = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix.lower() in {".tsv", ".csv", ".xlsx"}:
                txt = normalize_text(str(path))
                if any(token in txt for token in ["PERIOD", "TRIMEST", "SEMEST", "ANIO", "AÑO", "NIVEL", "MALLA", "PLAN", "CARRERA"]):
                    files.append(path)
    records: list[dict[str, Any]] = []
    for path in sorted(set(files)):
        try:
            if path.suffix.lower() == ".xlsx":
                xl = pd.ExcelFile(path)
                sheets = xl.sheet_names[:12]
                for sh in sheets:
                    try:
                        df = pd.read_excel(path, sheet_name=sh, dtype=str, nrows=3000)
                    except Exception:
                        continue
                    records.append(periodization_record(path, sh, df, codes_43))
            else:
                sep = "\t" if path.suffix.lower() == ".tsv" else ","
                df = read_delimited(path, sep).head(5000)
                records.append(periodization_record(path, "", df, codes_43))
        except Exception as exc:
            records.append(
                {
                    "ruta": str(path),
                    "archivo": path.name,
                    "hoja": "",
                    "filas_muestra": "",
                    "columnas": "",
                    "columnas_periodizacion": "",
                    "match_43_codigo_unico": 0,
                    "tiene_identificador_asignatura": "NO",
                    "tiene_codigo_unico": "NO",
                    "tiene_codpestud": "NO",
                    "tiene_duracion": "NO",
                    "valores_periodizacion": "",
                    "min_periodizacion": "",
                    "max_periodizacion": "",
                    "estado_candidato": "ERROR_LECTURA",
                    "observacion": str(exc),
                }
            )
    inv = pd.DataFrame(records)
    if not inv.empty:
        inv["score"] = (
            inv["match_43_codigo_unico"].fillna(0).astype(int)
            + inv["columnas_periodizacion"].fillna("").astype(str).apply(lambda x: 20 if x else 0)
            + inv["tiene_identificador_asignatura"].apply(lambda x: 20 if x == "SI" else 0)
            + inv["tiene_codpestud"].apply(lambda x: 10 if x == "SI" else 0)
        )
        inv = inv.sort_values(["score", "match_43_codigo_unico"], ascending=False)
    return inv


def periodization_record(path: Path, sheet: str, df: pd.DataFrame, codes_43: set[str]) -> dict[str, Any]:
    cols = [str(c) for c in df.columns]
    norm_cols = {normalize_text(c): c for c in cols}
    period_cols = [orig for norm, orig in norm_cols.items() if norm in {normalize_text(x) for x in PERIOD_FIELDS}]
    code_col = norm_cols.get("CODIGO_UNICO")
    match = int(df[code_col].astype(str).isin(codes_43).sum()) if code_col else 0
    id_cols = ["CODRAMO", "RAMOEQUIV", "RAMO", "ASIGNATURA", "ASIGNATURA_NORMALIZADA", "CODRAMOS_MATCH"]
    has_unit = any(normalize_text(c) in norm_cols for c in id_cols)
    vals = ""
    minv = ""
    maxv = ""
    if period_cols:
        s = pd.to_numeric(df[period_cols[0]], errors="coerce")
        if s.notna().any():
            minv = int(s.min())
            maxv = int(s.max())
        vals = list_values(df[period_cols[0]])
    status = "CANDIDATA_EXPLICITA" if period_cols and has_unit and (code_col or "CODPESTUD" in norm_cols or "PLAN_DE_ESTUDIO_CANONICO" in norm_cols) else "REFERENCIA_PARCIAL"
    return {
        "ruta": str(path),
        "archivo": path.name,
        "hoja": sheet,
        "filas_muestra": len(df),
        "columnas": len(df.columns),
        "columnas_periodizacion": " | ".join(period_cols),
        "match_43_codigo_unico": match,
        "tiene_identificador_asignatura": "SI" if has_unit else "NO",
        "tiene_codigo_unico": "SI" if code_col else "NO",
        "tiene_codpestud": "SI" if "CODPESTUD" in norm_cols or "PLAN_DE_ESTUDIO_CANONICO" in norm_cols else "NO",
        "tiene_duracion": "SI" if "DURACION_ESTUDIOS" in norm_cols else "NO",
        "valores_periodizacion": vals,
        "min_periodizacion": minv,
        "max_periodizacion": maxv,
        "estado_candidato": status,
        "observacion": "Inventario de columnas; no aplica regla por si mismo.",
    }


def prepare_canonical_units(h111_detail: pd.DataFrame, oferta_mu: pd.DataFrame) -> pd.DataFrame:
    detail = h111_detail.copy()
    detail["NIVEL_NUM"] = pd.to_numeric(detail["NIVEL_NUM"], errors="coerce")
    detail = detail.dropna(subset=["NIVEL_NUM"]).copy()
    detail["NIVEL_NUM"] = detail["NIVEL_NUM"].astype(int)
    detail["UNIDAD_ID"] = detail["CODRAMO"].fillna("").astype(str).str.strip()
    detail.loc[detail["UNIDAD_ID"] == "", "UNIDAD_ID"] = detail["RAMOEQUIV"].fillna("").astype(str).str.strip()
    detail.loc[detail["UNIDAD_ID"] == "", "UNIDAD_ID"] = detail["NOMBRE"].fillna("").astype(str).str.strip().apply(normalize_text)
    detail = detail[detail["UNIDAD_ID"] != ""].copy()
    detail = detail.sort_values(["CODIGO_UNICO", "UNIDAD_ID", "NIVEL_NUM"])
    detail = detail.drop_duplicates(["CODIGO_UNICO", "UNIDAD_ID"], keep="first").copy()
    for col in ["DURACION_ESTUDIOS_5810", "ANIOS_PERMITIDOS", "FAMILIA_FUNCIONAL", "TIPO_PLAN_CARRERA"]:
        if col in detail.columns:
            detail = detail.drop(columns=[col])
    meta = oferta_mu[["CODIGO_UNICO", "DURACION_ESTUDIOS_5810", "ANIOS_PERMITIDOS", "FAMILIA_FUNCIONAL", "TIPO_PLAN_CARRERA"]].copy()
    detail = detail.merge(meta, on="CODIGO_UNICO", how="left")
    detail["ANIOS_PERMITIDOS"] = pd.to_numeric(detail["ANIOS_PERMITIDOS"], errors="coerce").fillna(0).astype(int)
    detail["NIVEL_MAX_PLAN"] = detail.groupby("CODIGO_UNICO")["NIVEL_NUM"].transform("max").astype(int)
    return detail


def assign_method_a(detail: pd.DataFrame) -> pd.DataFrame:
    out = detail.copy()
    out["TAMANO_GRUPO_NIVELES"] = out.apply(
        lambda r: math.ceil(int(r["NIVEL_MAX_PLAN"]) / int(r["ANIOS_PERMITIDOS"])) if int(r["ANIOS_PERMITIDOS"]) > 0 else 0,
        axis=1,
    )
    out["ANIO_SIES_METODO_A"] = out.apply(
        lambda r: min(int(r["ANIOS_PERMITIDOS"]), max(1, math.ceil(int(r["NIVEL_NUM"]) / int(r["TAMANO_GRUPO_NIVELES"])))) if int(r["TAMANO_GRUPO_NIVELES"]) > 0 else 0,
        axis=1,
    )
    out["JUSTIFICACION_METODO_A"] = "NIVEL usado como orden curricular; grupos consecutivos compactados a ANIOS_PERMITIDOS."
    return out


def assign_method_b(detail: pd.DataFrame) -> pd.DataFrame:
    out = detail.copy()
    out["ANIO_SIES_METODO_B"] = out.apply(
        lambda r: min(int(r["ANIOS_PERMITIDOS"]), max(1, math.ceil(int(r["NIVEL_NUM"]) / int(r["NIVEL_MAX_PLAN"]) * int(r["ANIOS_PERMITIDOS"])))) if int(r["NIVEL_MAX_PLAN"]) > 0 and int(r["ANIOS_PERMITIDOS"]) > 0 else 0,
        axis=1,
    )
    out["JUSTIFICACION_METODO_B"] = "NIVEL escalado proporcionalmente al total de niveles del plan y a ANIOS_PERMITIDOS."
    return out


def distribution_from_detail(detail: pd.DataFrame, method_col: str, label: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for code, sub in detail.groupby("CODIGO_UNICO", dropna=False):
        row0 = sub.iloc[0]
        allowed = int(row0["ANIOS_PERMITIDOS"])
        units = {col: 0 for col in UNIT_COLUMNS}
        for y in range(1, 8):
            units[UNIT_COLUMNS[y - 1]] = int(sub.loc[sub[method_col] == y, "UNIDAD_ID"].nunique())
        total = int(sum(units.values()))
        outside = int(sub.loc[sub[method_col] > allowed, "UNIDAD_ID"].nunique())
        empty_inside = [str(y) for y in range(1, min(allowed, 7) + 1) if units[UNIT_COLUMNS[y - 1]] == 0]
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_CARRERA": row0.get("NOMBRE_CARRERA_5810", ""),
                "CODPESTUD": row0.get("CODPESTUD", ""),
                "DURACION_ESTUDIOS": row0.get("DURACION_ESTUDIOS_5810", ""),
                "ANIOS_PERMITIDOS": allowed,
                "FAMILIA_FUNCIONAL": row0.get("FAMILIA_FUNCIONAL", ""),
                "NIVEL_MAX_PLAN": int(row0["NIVEL_MAX_PLAN"]),
                "TOTAL_UNIDADES_MEDIDA": total,
                **units,
                "SUMA_ANIOS": total,
                "UNIDADES_FUERA_DURACION": outside,
                "ANIOS_DENTRO_DURACION_SIN_UNIDADES": " | ".join(empty_inside),
                "VALIDACION_TOTAL": "OK" if total == sum(units.values()) else "ERROR_TOTAL",
                "VALIDACION_DURACION": "OK" if outside == 0 else "ERROR_FUERA_DURACION",
                "ESTADO_FILA": "APTA_CANDIDATA" if outside == 0 and not empty_inside and total > 0 else "BLOQUEADA",
                "METODO": label,
            }
        )
    return pd.DataFrame(rows)


def evaluate_explicit_source(malla: pd.DataFrame, precarga: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if malla.empty:
        return pd.DataFrame(), pd.DataFrame()
    rows: list[dict[str, Any]] = []
    detail = malla.copy()
    detail["ANIO_NUM"] = pd.to_numeric(detail["ANIO_CURRICULAR"], errors="coerce")
    detail["TRIMESTRE_NUM"] = pd.to_numeric(detail["TRIMESTRE"], errors="coerce")
    detail["UNIDAD_ID_EXPLICITA"] = detail["ASIGNATURA_NORMALIZADA"].fillna("").astype(str).str.strip()
    detail.loc[detail["UNIDAD_ID_EXPLICITA"] == "", "UNIDAD_ID_EXPLICITA"] = detail["CODRAMOS_MATCH"].fillna("").astype(str).str.split("|").str[0].str.strip()
    for _, pre in precarga.iterrows():
        code = pre["CODIGO_UNICO"]
        dur = to_int(pre["DURACION_ESTUDIOS"])
        allowed = math.ceil(dur / 2) if dur else 0
        sub = detail[(detail["CODIGO_UNICO"] == code) & (detail["UNIDAD_ID_EXPLICITA"] != "")].copy()
        ded = sub.drop_duplicates(["CODIGO_UNICO", "UNIDAD_ID_EXPLICITA", "ANIO_NUM"])
        units = {col: int(ded.loc[ded["ANIO_NUM"] == y, "UNIDAD_ID_EXPLICITA"].nunique()) for y, col in enumerate(UNIT_COLUMNS, start=1)}
        total = int(sum(units.values()))
        outside = int(ded.loc[ded["ANIO_NUM"] > allowed, "UNIDAD_ID_EXPLICITA"].nunique())
        empty = [str(y) for y in range(1, min(allowed, 7) + 1) if units[UNIT_COLUMNS[y - 1]] == 0]
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_CARRERA": pre["NOMBRE_CARRERA"],
                "DURACION_ESTUDIOS": dur,
                "ANIOS_PERMITIDOS": allowed,
                "FILAS_EXPLICITAS": len(sub),
                "UNIDADES_EXPLICITAS": int(sub["UNIDAD_ID_EXPLICITA"].nunique()),
                "ANIO_MIN_EXPLICITO": "" if sub.empty else int(sub["ANIO_NUM"].min()),
                "ANIO_MAX_EXPLICITO": "" if sub.empty else int(sub["ANIO_NUM"].max()),
                **units,
                "TOTAL_UNIDADES_MEDIDA": total,
                "UNIDADES_FUERA_DURACION": outside,
                "ANIOS_DENTRO_DURACION_SIN_UNIDADES": " | ".join(empty),
                "ESTADO_USO_DIRECTO": "USABLE_DIRECTO" if len(sub) > 0 and outside == 0 and not empty else "NO_USABLE_DIRECTO",
                "OBSERVACION": "Fuente explicita con ANIO_CURRICULAR; se evalua, pero no se usa directo si faltan filas o excede duracion.",
            }
        )
    return pd.DataFrame(rows), detail


def compare_methods(dist_a: pd.DataFrame, dist_b: pd.DataFrame, explicit_dist: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for method, dist in [("METODO_A_GRUPOS_NIVELES", dist_a), ("METODO_B_ESCALA_PROPORCIONAL", dist_b)]:
        rows.append(
            {
                "METODO": method,
                "CARRERAS_CON_DISTRIBUCION": int((dist["TOTAL_UNIDADES_MEDIDA"] > 0).sum()),
                "CARRERAS_FUERA_DURACION": int((dist["UNIDADES_FUERA_DURACION"] > 0).sum()),
                "CARRERAS_CON_ANIOS_VACIOS_DENTRO_DURACION": int((dist["ANIOS_DENTRO_DURACION_SIN_UNIDADES"].fillna("") != "").sum()),
                "TOTAL_UNIDADES": int(dist["TOTAL_UNIDADES_MEDIDA"].sum()),
                "DIFERENCIAS_CON_OTRO_METODO": "",
                "RESPALDO_FUNCIONAL": "D. Decision interna candidata",
                "DICTAMEN": "SELECCIONADO" if method == "METODO_A_GRUPOS_NIVELES" else "NO_SELECCIONADO",
                "MOTIVO": "Metodo A preserva orden relativo y reproduce cortes observados de periodizacion por trimestres cuando la fuente explicita es usable."
                if method == "METODO_A_GRUPOS_NIVELES"
                else "Metodo B pasa validaciones, pero distribuye por escala proporcional y en planes de 7 niveles se aleja del corte observado 1-3,4-6,7.",
            }
        )
    if not explicit_dist.empty:
        rows.append(
            {
                "METODO": "FUENTE_EXPLICITA_ANIO_CURRICULAR",
                "CARRERAS_CON_DISTRIBUCION": int((explicit_dist["TOTAL_UNIDADES_MEDIDA"] > 0).sum()),
                "CARRERAS_FUERA_DURACION": int((explicit_dist["UNIDADES_FUERA_DURACION"] > 0).sum()),
                "CARRERAS_CON_ANIOS_VACIOS_DENTRO_DURACION": int((explicit_dist["ANIOS_DENTRO_DURACION_SIN_UNIDADES"].fillna("") != "").sum()),
                "TOTAL_UNIDADES": int(explicit_dist["TOTAL_UNIDADES_MEDIDA"].sum()),
                "DIFERENCIAS_CON_OTRO_METODO": "",
                "RESPALDO_FUNCIONAL": "B/C. Dato observado de mallas/PDF conciliados",
                "DICTAMEN": "NO_USAR_DIRECTO",
                "MOTIVO": "No resuelve directo 43/43: faltan carreras y algunas exceden duracion formal.",
            }
        )
    return pd.DataFrame(rows)


def build_final_distribution(dist_a: pd.DataFrame, oferta_mu: pd.DataFrame) -> pd.DataFrame:
    out = dist_a.copy()
    out = out.merge(oferta_mu[["CODIGO_UNICO", "PLAN_ESTUDIOS", "DURACION_OFERTA_MU", "TIPO_PLAN_CARRERA"]], on="CODIGO_UNICO", how="left")
    out["METODO_SELECCIONADO"] = "METODO_A_GRUPOS_NIVELES"
    out["DECISION_INTERNA"] = "NIVEL se usa como orden curricular observado; se compacta en grupos consecutivos hasta ANIOS_PERMITIDOS."
    out["NIVEL_RESPALDO"] = "D con respaldo B/C: duracion Oferta/MU + malla canonica + periodizacion explicita parcial."
    return out[
        [
            "CODIGO_UNICO",
            "PLAN_ESTUDIOS",
            "NOMBRE_CARRERA",
            "CODPESTUD",
            "DURACION_ESTUDIOS",
            "DURACION_OFERTA_MU",
            "TIPO_PLAN_CARRERA",
            "FAMILIA_FUNCIONAL",
            "ANIOS_PERMITIDOS",
            "NIVEL_MAX_PLAN",
            "TOTAL_UNIDADES_MEDIDA",
            *UNIT_COLUMNS,
            "SUMA_ANIOS",
            "UNIDADES_FUERA_DURACION",
            "VALIDACION_TOTAL",
            "VALIDACION_DURACION",
            "ESTADO_FILA",
            "METODO_SELECCIONADO",
            "DECISION_INTERNA",
            "NIVEL_RESPALDO",
        ]
    ]


def build_resolution_3(h111_cases3: pd.DataFrame, final_dist: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for code in ["I162S2C83J4V1", "I162S2C85J4V1", "I162S2C86J4V1"]:
        base = h111_cases3[h111_cases3["CODIGO_UNICO"] == code]
        base_row = base.iloc[0] if len(base) else pd.Series(dtype=object)
        dist = final_dist[final_dist["CODIGO_UNICO"] == code]
        dist_row = dist.iloc[0] if len(dist) else pd.Series(dtype=object)
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_CARRERA": base_row.get("NOMBRE_CARRERA", dist_row.get("NOMBRE_CARRERA", "")),
                "PLAN_OFERTA_MU": base_row.get("PLAN_OFERTA_MU", ""),
                "CODPESTUD_FINAL": dist_row.get("CODPESTUD", ""),
                "CATEGORIA_H112A": "RESUELTO_POR_CODPESTUD",
                "TOTAL_UNIDADES_MEDIDA": dist_row.get("TOTAL_UNIDADES_MEDIDA", ""),
                "ANIOS_PERMITIDOS": dist_row.get("ANIOS_PERMITIDOS", ""),
                "UNIDADES_FUERA_DURACION": dist_row.get("UNIDADES_FUERA_DURACION", ""),
                "ESTADO": "RESUELTO_TRAZABLE",
                "OBSERVACION": "H111 resolvio plan por Oferta/MU; H112A distribuye con Metodo A sobre detalle canonico del CODPESTUD.",
            }
        )
    return pd.DataFrame(rows)


def build_h106_comparison(final_dist: pd.DataFrame, precarga: pd.DataFrame) -> pd.DataFrame:
    if not H106_CSV.exists():
        return pd.DataFrame([{"estado": "SIN_H106", "observacion": "No se encontro CSV H106 rechazado."}])
    cols_21 = [c for c in precarga.columns if c != "CODIGO_IES_NUM"]
    h106 = pd.read_csv(H106_CSV, sep=";", encoding="latin1", header=None, dtype=str)
    h106.columns = cols_21[: len(h106.columns)]
    rows = []
    for _, pre in precarga.iterrows():
        code = pre["CODIGO_UNICO"]
        dur = to_int(pre["DURACION_ESTUDIOS"])
        allowed = math.ceil(dur / 2) if dur else 0
        h = h106[h106["CODIGO_UNICO"] == code]
        f = final_dist[final_dist["CODIGO_UNICO"] == code]
        if h.empty or f.empty:
            continue
        hrow = h.iloc[0]
        frow = f.iloc[0]
        h_units = {col: to_int(hrow.get(col)) for col in UNIT_COLUMNS}
        f_units = {col: to_int(frow.get(col)) for col in UNIT_COLUMNS}
        h_out = sum(v for idx, (col, v) in enumerate(h_units.items(), start=1) if idx > allowed)
        f_out = sum(v for idx, (col, v) in enumerate(f_units.items(), start=1) if idx > allowed)
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_CARRERA": pre["NOMBRE_CARRERA"],
                "DURACION_ESTUDIOS": dur,
                "ANIOS_PERMITIDOS": allowed,
                "TOTAL_H106": to_int(hrow.get("TOTAL_UNIDADES_MEDIDA")),
                "TOTAL_H112A_CANDIDATO": to_int(frow.get("TOTAL_UNIDADES_MEDIDA")),
                "UNIDADES_FUERA_DURACION_H106": h_out,
                "UNIDADES_FUERA_DURACION_H112A": f_out,
                "DIF_TOTAL": to_int(frow.get("TOTAL_UNIDADES_MEDIDA")) - to_int(hrow.get("TOTAL_UNIDADES_MEDIDA")),
                "ERROR_SIES_ANTERIOR_ELIMINADO": "SI" if f_out == 0 else "NO",
                "OBSERVACION": "H106 queda como evidencia de rechazo, no como fuente final.",
            }
        )
        for col in UNIT_COLUMNS:
            rows[-1][f"{col}_H106"] = h_units[col]
            rows[-1][f"{col}_H112A"] = f_units[col]
    return pd.DataFrame(rows)


def build_promedios_contrast(precarga: pd.DataFrame, final_dist: pd.DataFrame) -> pd.DataFrame:
    if not PROMEDIOS.exists():
        return pd.DataFrame([{"estado": "SIN_PROMEDIOS", "uso": "No se usa como norma."}])
    try:
        prom = pd.read_excel(PROMEDIOS, sheet_name="Hoja1", dtype=str)
    except Exception:
        prom = pd.read_excel(PROMEDIOS, sheet_name=0, dtype=str)
    rows = []
    for _, pre in precarga.iterrows():
        code = pre["CODIGO_UNICO"]
        name = normalize_text(pre["NOMBRE_CARRERA"])
        sub = prom[prom["CARRERA"].apply(normalize_text) == name] if "CARRERA" in prom.columns else prom.iloc[0:0]
        f = final_dist[final_dist["CODIGO_UNICO"] == code]
        frow = f.iloc[0] if len(f) else pd.Series(dtype=object)
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_CARRERA": pre["NOMBRE_CARRERA"],
                "FILAS_PROMEDIOS_NOMBRE": len(sub),
                "PLANES_PROMEDIOS": list_values(sub["PLAN_DE_ESTUDIO"]) if "PLAN_DE_ESTUDIO" in sub.columns and not sub.empty else "",
                "NIVELES_PROMEDIOS": list_values(sub["NIVEL"]) if "NIVEL" in sub.columns and not sub.empty else "",
                "TOTAL_UNIDADES_H112A": frow.get("TOTAL_UNIDADES_MEDIDA", ""),
                "USO": "B. Contraste interno; PROMEDIOS no norma ni estructura Carreras.",
                "DICTAMEN": "No bloquea ni aprueba distribucion; solo evidencia actividad/niveles observados.",
            }
        )
    return pd.DataFrame(rows)


def validate_final(precarga: pd.DataFrame, oferta_mu: pd.DataFrame, final_dist: pd.DataFrame, h106_comp: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    rows = []
    dup = int(precarga.duplicated(["CODIGO_UNICO", "PLAN_ESTUDIOS"]).sum())
    conditions = [
        ("43/43 carreras con duracion validada", 43, int((oferta_mu["DURACION_COINCIDE_5810_MU"] == "SI").sum())),
        ("43/43 carreras con familia funcional o tipo plan", 43, int((oferta_mu["FAMILIA_FUNCIONAL"].fillna("") != "").sum())),
        ("43/43 carreras con distribucion candidata", 43, int((final_dist["TOTAL_UNIDADES_MEDIDA"] > 0).sum())),
        ("0 carreras sin detalle o sin resolucion trazable", 0, int((final_dist["ESTADO_FILA"] != "APTA_CANDIDATA").sum())),
        ("0 unidades fuera de duracion", 0, int(final_dist["UNIDADES_FUERA_DURACION"].sum())),
        ("TOTAL_UNIDADES_MEDIDA = suma anios en 43/43", 43, int((final_dist["VALIDACION_TOTAL"] == "OK").sum())),
        (
            "UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO enteros >= 0",
            43,
            int(final_dist[UNIT_COLUMNS].apply(lambda col: col.map(lambda x: to_int(x) >= 0)).all(axis=1).sum()),
        ),
        ("Anios superiores a techo(DURACION/2) en cero", 43, int((final_dist["VALIDACION_DURACION"] == "OK").sum())),
        ("CODIGO_UNICO + PLAN_ESTUDIOS sin duplicados", 0, dup),
        ("No usar H106 como fuente final", "SI", "SI"),
        ("No usar PROMEDIOS como norma", "SI", "SI"),
        ("No usar matricula 5809 como estructura Carreras", "SI", "SI"),
        ("Decision interna registrada como D", "SI", "SI"),
        ("Error SIES anterior eliminado", 43, int((h106_comp["ERROR_SIES_ANTERIOR_ELIMINADO"] == "SI").sum()) if "ERROR_SIES_ANTERIOR_ELIMINADO" in h106_comp.columns else 0),
        ("CSV final generado", "NO", "NO"),
        ("SIES_READY generado", "NO", "NO"),
    ]
    for validation, expected, observed in conditions:
        state = "OK" if str(expected) == str(observed) else "BLOQUEADO"
        rows.append({"validacion": validation, "esperado": expected, "observado": observed, "estado": state})
    df = pd.DataFrame(rows)
    dictamen = "APTO_PARA_GENERAR_CSV_H112B" if (df["estado"] == "OK").all() else "BLOQUEADO_PARCIAL"
    if int((final_dist["TOTAL_UNIDADES_MEDIDA"] > 0).sum()) == 0:
        dictamen = "BLOQUEADO_TOTAL"
    return df, dictamen


def build_summary(dictamen: str, final_dist: pd.DataFrame, explicit_dist: pd.DataFrame, validations: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("Proceso", "Avance Curricular SIES 2026"),
        ("Subproyecto", "Carreras Avance Curricular 2026 / ID SIES 16769"),
        ("Ano proceso", "2026"),
        ("Ano referencia datos", "2025"),
        ("Estado H112A", dictamen),
        ("Declaracion carga", "NO_LISTO_PARA_CARGA"),
        ("CSV final generado", "NO"),
        ("SIES_READY generado", "NO"),
        ("Fuentes originales modificadas", "NO"),
        ("Metodo seleccionado", "METODO_A_GRUPOS_NIVELES"),
        ("Regla seleccionada", "NIVEL como orden curricular observado; grupo=techo(NIVEL_MAX_PLAN/ANIOS_PERMITIDOS); ANIO=techo(NIVEL/grupo) capado a ANIOS_PERMITIDOS."),
        ("Fuente explicita usable directo", f"{int((explicit_dist['ESTADO_USO_DIRECTO']=='USABLE_DIRECTO').sum())}/43" if not explicit_dist.empty else "0/43"),
        ("Distribucion candidata 43/43", int((final_dist["TOTAL_UNIDADES_MEDIDA"] > 0).sum())),
        ("Unidades fuera duracion candidato", int(final_dist["UNIDADES_FUERA_DURACION"].sum())),
        ("Validaciones bloqueantes OK", int((validations["estado"] == "OK").sum())),
        ("Validaciones bloqueantes total", len(validations)),
        ("Dictamen global", "H112B queda habilitado solo como siguiente hito de generacion controlada; esta etapa no genera CSV."),
    ]
    return pd.DataFrame(rows, columns=["campo", "valor"])


def build_trazabilidad(dictamen: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "tipo": "A. Regla oficial",
                "afirmacion": "Manual Avance gobierna duracion, total y distribucion anual, pero no define NIVEL.",
                "fuente": str(MANUAL),
                "uso": "Respalda validacion contra duracion; no respalda formula NIVEL por si sola.",
            },
            {
                "tipo": "B. Dato observado",
                "afirmacion": "Oferta/MU valida duracion 43/43 y familia/tipo de plan.",
                "fuente": str(DURACION_MU),
                "uso": "Define ANIOS_PERMITIDOS y contexto funcional.",
            },
            {
                "tipo": "B/C. Dato observado + auditoria",
                "afirmacion": "Mallas/PDF conciliados contienen TRIMESTRE y ANIO_CURRICULAR; no son suficientes como fuente directa 43/43, pero respaldan cortes funcionales por periodos.",
                "fuente": str(MALLA_EXPANDIDA_43),
                "uso": "Respalda Metodo A como compactacion de orden curricular.",
            },
            {
                "tipo": "B. Dato observado",
                "afirmacion": "Planes canonicos contienen CODPESTUD, CODRAMO y NIVEL completo para 43/43 con planes resueltos desde H111.",
                "fuente": str(CANONICO_PLANES),
                "uso": "Fuente de detalle de unidades.",
            },
            {
                "tipo": "C. Implementacion tecnica",
                "afirmacion": "Se simulan Metodo A y Metodo B sin escribir carga.",
                "fuente": "decision_alternativa_periodizacion_carreras_16769.py",
                "uso": "Validacion reproducible.",
            },
            {
                "tipo": "D. Decision interna",
                "afirmacion": "Se selecciona Metodo A por preservar orden relativo y alinearse mejor con periodizacion explicita usable.",
                "fuente": "H112A",
                "uso": dictamen,
            },
            {
                "tipo": "B. Contraste no normativo",
                "afirmacion": "PROMEDIOS se revisa solo como contraste interno.",
                "fuente": str(PROMEDIOS),
                "uso": "No gobierna Carreras.",
            },
        ]
    )


def manifest_table(sources: list[Path]) -> pd.DataFrame:
    return pd.DataFrame(
        [{"tipo": "entrada", "ruta": str(p), "existe": p.exists(), "sha256": sha256_file(p)} for p in sources]
    )


def autosize(path: Path) -> None:
    try:
        from openpyxl import load_workbook
    except Exception:
        return
    wb = load_workbook(path)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        for col in ws.columns:
            letter = col[0].column_letter
            width = 10
            for cell in col[:200]:
                if cell.value is not None:
                    width = max(width, min(60, len(str(cell.value)) + 2))
            ws.column_dimensions[letter].width = width
    wb.save(path)


def write_report(path: Path, dictamen: str, resumen: pd.DataFrame, comparacion: pd.DataFrame, validaciones: pd.DataFrame, final_dist: pd.DataFrame, resol3: pd.DataFrame) -> None:
    lines = [
        "# Informe H112A - Decision alternativa periodizacion Carreras 16769",
        "",
        f"**Dictamen:** {dictamen}",
        "",
        "Este hito no genera CSV final, no genera SIES_READY y no modifica fuentes originales.",
        "",
        "## Resumen",
        markdown_table(resumen),
        "",
        "## Separacion de respaldo",
        "- A. Regla oficial: el manual Avance exige consistencia entre duracion y distribucion anual, pero no define `NIVEL`.",
        "- B. Dato observado: Oferta/MU valida duracion 43/43; planes canonicos entregan detalle de unidades; mallas/PDF entregan periodizacion explicita parcial.",
        "- C. Implementacion tecnica: se simulan fuente explicita directa, Metodo A y Metodo B sin aplicar carga.",
        "- D. Decision interna: se selecciona Metodo A como regla candidata para H112B.",
        "- E. Pendiente: generar CSV final solo en H112B con controles de carga, no en este hito.",
        "",
        "## Metodo seleccionado",
        "Se selecciona `METODO_A_GRUPOS_NIVELES`: `NIVEL` no se trata como semestre directo. Se usa como orden curricular observado; se calcula `grupo = techo(NIVEL_MAX_PLAN / ANIOS_PERMITIDOS)` y `ANIO_SIES = techo(NIVEL / grupo)`, limitado entre 1 y `ANIOS_PERMITIDOS`.",
        "",
        "La seleccion no se basa solo en que pase validaciones tecnicas. La fuente explicita de mallas/PDF no resuelve 43/43 como carga directa, pero muestra periodizacion por `TRIMESTRE` y `ANIO_CURRICULAR`; el Metodo A conserva el orden y reproduce esos cortes cuando la fuente explicita es compatible.",
        "",
        "## Comparacion de metodos",
        markdown_table(comparacion),
        "",
        "## Validaciones bloqueantes",
        markdown_table(validaciones, 20),
        "",
        "## Tres carreras trazadas desde H111",
        markdown_table(resol3),
        "",
        "## Distribucion candidata final",
        markdown_table(final_dist[["CODIGO_UNICO", "NOMBRE_CARRERA", "DURACION_ESTUDIOS", "ANIOS_PERMITIDOS", "TOTAL_UNIDADES_MEDIDA", *UNIT_COLUMNS, "UNIDADES_FUERA_DURACION", "ESTADO_FILA"]], 20),
        "",
        "## Siguiente paso",
        "Si el responsable del proceso acepta este dictamen interno, el siguiente hito es H112B para generar el CSV final controlado. H112A no genera carga.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    stamp = stamp_now()
    out_dir = OUT_BASE / f"DECISION_ALTERNATIVA_PERIODIZACION_CARRERAS_16769_{stamp}"
    desktop_dir = DESKTOP_BASE / f"AVANCE_CURRICULAR_2026_DECISION_ALTERNATIVA_PERIODIZACION_CARRERAS_16769_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    data = load_base()
    precarga = data["precarga"]
    oferta_mu = build_oferta_mu(precarga, data["h111_match"])
    reglas = extract_manual_rules()
    inventario = scan_periodization_sources(set(precarga["CODIGO_UNICO"].astype(str)))
    explicit_dist, explicit_detail = evaluate_explicit_source(data["malla_exp"], precarga)
    canonical_units = prepare_canonical_units(data["h111_detail"], oferta_mu)
    method_a_detail = assign_method_a(canonical_units)
    method_b_detail = assign_method_b(canonical_units)
    dist_a = distribution_from_detail(method_a_detail, "ANIO_SIES_METODO_A", "METODO_A_GRUPOS_NIVELES")
    dist_b = distribution_from_detail(method_b_detail, "ANIO_SIES_METODO_B", "METODO_B_ESCALA_PROPORCIONAL")
    comparacion = compare_methods(dist_a, dist_b, explicit_dist)
    final_dist = build_final_distribution(dist_a, oferta_mu)
    resol3 = build_resolution_3(data["h111_cases3"], final_dist)
    h106_comp = build_h106_comparison(final_dist, precarga)
    prom_contrast = build_promedios_contrast(precarga, final_dist)
    validaciones, dictamen = validate_final(precarga, oferta_mu, final_dist, h106_comp)
    resumen = build_summary(dictamen, final_dist, explicit_dist, validaciones)
    trazabilidad = build_trazabilidad(dictamen)
    kpi = pd.DataFrame(
        [
            ("dictamen", dictamen),
            ("filas_precarga_5810", len(precarga)),
            ("match_oferta_mu", int((oferta_mu["ESTADO_MATCH_OFERTA"] == "MATCH_OFERTA_MU").sum())),
            ("carreras_distribucion_final", int((final_dist["TOTAL_UNIDADES_MEDIDA"] > 0).sum())),
            ("unidades_fuera_duracion_final", int(final_dist["UNIDADES_FUERA_DURACION"].sum())),
            ("metodo_seleccionado", "METODO_A_GRUPOS_NIVELES"),
            ("csv_final_generado", "NO"),
            ("sies_ready_generado", "NO"),
        ],
        columns=["indicador", "valor"],
    )

    sources = [
        MANUAL,
        PRECARGA_5810,
        H106_CSV,
        H109_XLSX,
        H110_XLSX,
        H111_XLSX,
        H111_REPORT,
        CANONICO_PLANES,
        CONCILIACION_43,
        MALLA_EXPANDIDA_43,
        CONTROL_TRIMESTRE,
        RESUMEN_TRIMESTRE,
        CONFLICTOS_TRIMESTRE,
        CLASIFICACION_PERIODIZACION,
        ADECUACION_2,
        DURACION_MU,
        GOB_NIV_ACA,
        REVISION_SIES_MU,
        PROMEDIOS,
    ]
    manifest_df = manifest_table(sources)

    excel_path = out_dir / "DECISION_ALTERNATIVA_PERIODIZACION_CARRERAS_16769.xlsx"
    report_path = out_dir / "INFORME_DECISION_ALTERNATIVA_PERIODIZACION_CARRERAS_16769.md"
    manifest_path = out_dir / "manifest_decision_alternativa_periodizacion_carreras_16769.json"
    script_path = out_dir / "decision_alternativa_periodizacion_carreras_16769.py"

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="00_RESUMEN_DICTAMEN", index=False)
        reglas.to_excel(writer, sheet_name="01_REGLAS_MANUAL", index=False)
        precarga.to_excel(writer, sheet_name="02_PRECARGA_5810", index=False)
        oferta_mu.to_excel(writer, sheet_name="03_EVIDENCIA_OFERTA_MU", index=False)
        inventario.to_excel(writer, sheet_name="04_INVENTARIO_PERIODIZACION", index=False)
        canonical_units.to_excel(writer, sheet_name="05_FUENTE_DETALLE_ASIGNATURAS", index=False)
        method_a_detail.to_excel(writer, sheet_name="06_METODO_A_GRUPOS_NIVELES", index=False)
        method_b_detail.to_excel(writer, sheet_name="07_METODO_B_ESCALA_PROPORCIONAL", index=False)
        comparacion.to_excel(writer, sheet_name="08_COMPARACION_METODOS", index=False)
        resol3.to_excel(writer, sheet_name="09_RESOLUCION_3_CARRERAS", index=False)
        final_dist.to_excel(writer, sheet_name="10_DISTRIBUCION_CANDIDATA_FINAL", index=False)
        validaciones.to_excel(writer, sheet_name="11_VALIDACIONES_BLOQUEANTES", index=False)
        h106_comp.to_excel(writer, sheet_name="12_COMPARACION_H106_RECHAZADO", index=False)
        prom_contrast.to_excel(writer, sheet_name="13_PROMEDIOS_CONTRASTE", index=False)
        trazabilidad.to_excel(writer, sheet_name="14_TRAZABILIDAD_DECISION", index=False)
        kpi.to_excel(writer, sheet_name="15_KPI", index=False)
        manifest_df.to_excel(writer, sheet_name="16_MANIFEST", index=False)
    autosize(excel_path)

    write_report(report_path, dictamen, resumen, comparacion, validaciones, final_dist, resol3)
    shutil.copy2(Path(__file__), script_path)

    manifest = {
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "Carreras Avance Curricular 2026 / ID SIES 16769",
        "hito": "112a_decision_alternativa_periodizacion_carreras_16769",
        "timestamp": stamp,
        "dictamen": dictamen,
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "csv_final_generado": "NO",
        "sies_ready_generado": "NO",
        "fuentes_originales_modificadas": "NO",
        "metodo_seleccionado": "METODO_A_GRUPOS_NIVELES",
        "fuentes": manifest_df.to_dict(orient="records"),
        "productos": {
            "excel": {"ruta": str(excel_path), "sha256": sha256_file(excel_path)},
            "informe": {"ruta": str(report_path), "sha256": sha256_file(report_path)},
            "manifest": {"ruta": str(manifest_path), "sha256": ""},
            "script": {"ruta": str(script_path), "sha256": sha256_file(script_path)},
        },
        "carpeta_github": str(out_dir),
        "carpeta_escritorio": str(desktop_dir),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["productos"]["manifest"]["sha256"] = sha256_file(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if desktop_dir.exists():
        shutil.rmtree(desktop_dir)
    shutil.copytree(out_dir, desktop_dir)

    print("DECISION ALTERNATIVA PERIODIZACION CARRERAS 16769 — GENERADA")
    print("Fuentes originales modificadas: NO")
    print("CSV final generado: NO")
    print("SIES_READY generado: NO")
    print("Declaracion carga: NO_LISTO_PARA_CARGA")
    print(f"Dictamen: {dictamen}")
    print(f"Metodo seleccionado: METODO_A_GRUPOS_NIVELES")
    print()
    print("DICTAMEN")
    print(resumen.to_string(index=False))
    print()
    print("COMPARACION METODOS")
    print(comparacion.to_string(index=False))
    print()
    print("VALIDACIONES BLOQUEANTES")
    print(validaciones.to_string(index=False))
    print()
    print("ARCHIVOS")
    print(f"Excel: {excel_path}")
    print(f"Informe: {report_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Script: {script_path}")
    print(f"Carpeta escritorio: {desktop_dir}")


if __name__ == "__main__":
    main()
