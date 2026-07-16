#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H111 - Decision interna NIVEL -> periodizacion anual para Carreras 16769.

Este hito es documental y de diagnostico. No modifica fuentes originales, no
genera CSV de carga y no genera SIES_READY.
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
OUT_BASE = AVANCE / "111_decision_interna_nivel_periodizacion_carreras_16769"
DESKTOP_BASE = Path.home() / "Desktop"

MANUAL = AVANCE / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/Instructivo_Avance Curricular SIES - 2026.txt"
PRECARGA_5810 = AVANCE / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5810_Precarga Carreras Avance Curricular 20268.csv"
H109_DIR = AVANCE / "109_diagnostico_gobernado_carreras_16769/DIAGNOSTICO_GOBERNADO_CARRERAS_16769_20260709_105803"
H110_DIR = AVANCE / "110_cierre_funcional_nivel_periodizacion_carreras_16769/CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769_20260709_111343"
H109_XLSX = H109_DIR / "DIAGNOSTICO_GOBERNADO_CARRERAS_16769.xlsx"
H110_XLSX = H110_DIR / "CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769.xlsx"
CANONICO_PLANES = AVANCE / "04_gobernanza_mallas/03_auditorias/CANONICO_TODOS_PLANES_ESTUDIO_20260701_140528/02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv"
CONCILIACION_43 = AVANCE / "04_gobernanza_mallas/03_auditorias/CIERRE_FINAL_43_RESUELTAS_0_PENDIENTES_20260701_171409/02_RESULTADOS/01_CONCILIACION_FINAL_43.tsv"
DURACION_MU = ROOT / "DURACION_ESTUDIOS.tsv"
GOB_NIV_ACA = ROOT / "gobernanza_columnas_mu/gob_mu_niv_aca.tsv"
REVISION_SIES_MU = ROOT / "resultados/auditorias/REVISION_CARRERAS_CODIGOS_SIES_MU2026.xlsx"
RESUMEN_SIES_MU = ROOT / "resultados/auditorias/RESUMEN_CARRERAS_RESOLUCION_SIES_MU2026.csv"
MAPEO_OFERTA_CODCLI = ROOT / "resultados/auditoria_integral_multicodcli_2026/auditoria_20260618_144641/05_MAPEO_OFERTA_CODCLI.xlsx"
REPORTE_FASE2_MU = ROOT / "control/reportes/reporte_fase_2_sies_oferta_mu_2026.md"
REPORTE_SIES_MU_JSON = ROOT / "control/reportes/reporte_sies_oferta_mu_2026.json"
MU_CONTROL = ROOT / "resultados/matricula_unificada_2026_control.csv"
MU_OFICIAL = ROOT / "resultados/matricula_unificada_2026_oficial.xlsx"
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


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_flexible(path: Path, sep: str = ";", encoding: str | None = None) -> pd.DataFrame:
    encodings = [encoding] if encoding else ["utf-8-sig", "utf-8", "latin1"]
    last_error: Exception | None = None
    for enc in encodings:
        try:
            return pd.read_csv(path, sep=sep, dtype=str, encoding=enc)
        except Exception as exc:  # pragma: no cover - fallback path
            last_error = exc
    raise RuntimeError(f"No fue posible leer {path}: {last_error}")


def to_int(value: Any, default: int = 0) -> int:
    if pd.isna(value):
        return default
    text = str(value).strip().replace(",", ".")
    if text == "":
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def normalize_text(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def contains_code(cell: Any, code: str) -> bool:
    parts = [p.strip() for p in str(cell or "").split("|")]
    return code in parts


def split_codes(cell: Any) -> list[str]:
    return [p.strip() for p in str(cell or "").split("|") if p.strip() and p.strip().lower() != "nan"]


def extract_code_parts(code: str) -> dict[str, str]:
    m = re.match(r"I(?P<ies>\d+)S(?P<sede>\d+)C(?P<carrera>\d+)J(?P<jornada>\d+)V(?P<version>\d+)", str(code))
    if not m:
        return {"CODIGO_IES_NUM_PARSE": "", "COD_SEDE_PARSE": "", "COD_CARRERA_PARSE": "", "JORNADA_PARSE": "", "VERSION_PARSE": ""}
    return {
        "CODIGO_IES_NUM_PARSE": m.group("ies"),
        "COD_SEDE_PARSE": m.group("sede"),
        "COD_CARRERA_PARSE": m.group("carrera"),
        "JORNADA_PARSE": m.group("jornada"),
        "VERSION_PARSE": m.group("version"),
    }


def classify_family(nombre: Any, tipo_plan: Any, nivel_carrera: Any) -> tuple[str, str]:
    name = normalize_text(nombre)
    tipo = str(tipo_plan or "").strip()
    nivel = str(nivel_carrera or "").strip()
    if "CONTINUIDAD" in name or tipo == "3":
        return "CONTINUIDAD", "D. Decision interna: continuidad por nombre o TIPO_PLAN_CARRERA=3 observado en MU/Oferta."
    if "TECNICO" in name or nivel == "1":
        return "TECNICA", "B. Dato observado: nombre/NIVEL_CARRERA de MU/Oferta compatible con carrera tecnica."
    if "INGENIERIA" in name:
        return "INGENIERIA", "B. Dato observado: nombre contiene INGENIERIA."
    return "INGENIERIA", "D. Decision interna restringida por el hito: familia residual no tecnica/no continuidad se agrupa como INGENIERIA para esta decision; no es regla oficial."


def list_values(series: pd.Series, limit: int = 12) -> str:
    vals = [str(v) for v in series.dropna().astype(str).unique().tolist() if str(v).strip()]
    vals = sorted(vals, key=lambda x: (len(x), x))
    if len(vals) > limit:
        return " | ".join(vals[:limit]) + f" | ... (+{len(vals)-limit})"
    return " | ".join(vals)


def make_markdown_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "_Sin registros._"
    sample = df.head(max_rows).copy()
    sample = sample.fillna("")
    cols = [str(c) for c in sample.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in sample.iterrows():
        vals = [str(row[c]).replace("\n", " ").replace("|", "/") for c in sample.columns]
        lines.append("| " + " | ".join(vals) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Se muestran {max_rows} de {len(df)} filas._")
    return "\n".join(lines)


def source_record(path: Path, tipo: str, clasificacion: str, nivel: str, utilidad: str, sheet: str = "") -> dict[str, Any]:
    return {
        "ruta": str(path),
        "archivo": path.name,
        "hoja": sheet,
        "existe": "SI" if path.exists() else "NO",
        "tipo_fuente": tipo,
        "clasificacion": clasificacion,
        "nivel_respaldo": nivel,
        "sha256": sha256_file(path),
        "utilidad_decision_funcional": utilidad,
    }


def inventory_dataframe(path: Path, sheet: str, df: pd.DataFrame, codes_43: set[str], base: dict[str, Any]) -> dict[str, Any]:
    cols = [str(c) for c in df.columns]
    upper_cols = {normalize_text(c): c for c in cols}
    cod_col = upper_cols.get("CODIGO_UNICO")
    if cod_col:
        match = int(df[cod_col].astype(str).isin(codes_43).sum())
        dup = int(df[cod_col].astype(str).duplicated().sum())
    else:
        match = 0
        dup = 0
    row = dict(base)
    row.update(
        {
            "hoja": sheet,
            "filas": len(df),
            "columnas": len(df.columns),
            "lista_columnas": " | ".join(cols[:45]) + (" | ..." if len(cols) > 45 else ""),
            "contiene_CODIGO_UNICO": "SI" if "CODIGO_UNICO" in upper_cols else "NO",
            "contiene_COD_CARRERA": "SI" if any(c in upper_cols for c in ["COD_CARRERA", "COD_CAR", "CODCARPR", "CODCARR"]) else "NO",
            "contiene_COD_SEDE": "SI" if any(c in upper_cols for c in ["COD_SEDE", "COD_SED", "SEDE"]) else "NO",
            "contiene_JORNADA": "SI" if "JORNADA" in upper_cols or "JOR" in upper_cols else "NO",
            "contiene_VERSION": "SI" if "VERSION" in upper_cols else "NO",
            "contiene_DURACION_ESTUDIOS": "SI" if "DURACION_ESTUDIOS" in upper_cols else "NO",
            "contiene_TIPO_PLAN_CARRERA": "SI" if "TIPO_PLAN_CARRERA" in upper_cols else "NO",
            "contiene_NOMBRE_CARRERA": "SI" if "NOMBRE_CARRERA" in upper_cols or "CARRERA" in upper_cols else "NO",
            "contiene_familia_funcional": "SI" if any("TECNIC" in normalize_text(c) or "CONTINUID" in normalize_text(c) or "INGENIER" in normalize_text(c) for c in cols) else "NO",
            "match_43_CODIGO_UNICO": match,
            "duplicados_CODIGO_UNICO": dup,
        }
    )
    return row


def extract_manual_rules() -> pd.DataFrame:
    if not MANUAL.exists():
        return pd.DataFrame(
            [
                {
                    "regla": "Manual no encontrado",
                    "referencia_lineas": "",
                    "texto_manual": "",
                    "interpretacion_operativa": "Bloqueo: no se encontro instructivo oficial.",
                    "alcance": "Carreras Avance Curricular 16769",
                    "nivel_respaldo": "E",
                }
            ]
        )
    lines = MANUAL.read_text(encoding="utf-8", errors="replace").splitlines()
    topics = {
        "Orden de carga Carreras antes que Matricula": ["carreras", "matrícula"],
        "DURACION_ESTUDIOS": ["DURACION_ESTUDIOS", "duración"],
        "TOTAL_UNIDADES_MEDIDA": ["TOTAL_UNIDADES_MEDIDA"],
        "UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO": ["UNIDADES_1ER_ANIO", "UNIDADES_7MO_ANIO", "unidades"],
        "TIPO_UNIDAD_MEDIDA": ["TIPO_UNIDAD_MEDIDA"],
        "VIGENCIA": ["VIGENCIA"],
    }
    records: list[dict[str, Any]] = []
    for topic, needles in topics.items():
        hits: list[tuple[int, str]] = []
        for idx, line in enumerate(lines, start=1):
            plain = normalize_text(line)
            if any(normalize_text(n) in plain for n in needles):
                hits.append((idx, line.strip()))
        if hits:
            text = " / ".join([f"L{idx}: {line}" for idx, line in hits[:6]])
            ref = ", ".join([f"L{idx}" for idx, _ in hits[:6]])
        else:
            text = "No se encontro extracto textual directo con los terminos buscados."
            ref = ""
        records.append(
            {
                "regla": topic,
                "referencia_lineas": ref,
                "texto_manual": text,
                "interpretacion_operativa": {
                    "Orden de carga Carreras antes que Matricula": "Carreras 16769 se prepara antes que Matricula 16768.",
                    "DURACION_ESTUDIOS": "Duracion de estudios se trata como semestres para validar anios permitidos.",
                    "TOTAL_UNIDADES_MEDIDA": "Debe corresponder al total entero de unidades informadas para la carrera.",
                    "UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO": "Distribucion anual de unidades del plan; no debe exceder la duracion formal.",
                    "TIPO_UNIDAD_MEDIDA": "Campo de unidad de medida definido por el instructivo; no se deriva desde PROMEDIOS.",
                    "VIGENCIA": "Debe conservar la regla/codigo del instructivo y la precarga.",
                }[topic],
                "alcance": "Carreras Avance Curricular 2026 / ID 16769",
                "nivel_respaldo": "A. Regla oficial Avance",
            }
        )
    records.append(
        {
            "regla": "Semantica de NIVEL en fuente canonica",
            "referencia_lineas": "",
            "texto_manual": "El instructivo no define la columna raw NIVEL de los planes canonicos.",
            "interpretacion_operativa": "No se puede presentar NIVEL->anio como regla oficial; solo podria ser decision interna si supera validaciones.",
            "alcance": "Planes canonicos usados para reconstruir unidades anuales",
            "nivel_respaldo": "E. Pendiente respecto del manual",
        }
    )
    return pd.DataFrame(records)


def load_inputs() -> dict[str, pd.DataFrame]:
    precarga = read_csv_flexible(PRECARGA_5810, sep=";", encoding="latin1")
    canonico = read_csv_flexible(CANONICO_PLANES, sep="\t")
    conciliacion = read_csv_flexible(CONCILIACION_43, sep="\t")
    duracion = read_csv_flexible(DURACION_MU, sep="\t")
    niv_aca = read_csv_flexible(GOB_NIV_ACA, sep="\t")
    por_plan = pd.read_excel(REVISION_SIES_MU, sheet_name="POR_PLAN", dtype=str)
    resumen_mu = read_csv_flexible(RESUMEN_SIES_MU, sep=",") if RESUMEN_SIES_MU.exists() else pd.DataFrame()
    return {
        "precarga": precarga,
        "canonico": canonico,
        "conciliacion": conciliacion,
        "duracion": duracion,
        "niv_aca": niv_aca,
        "por_plan": por_plan,
        "resumen_mu": resumen_mu,
    }


def build_inventory(codes_43: set[str], data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []

    base_sources = [
        (DURACION_MU, "TSV", "Oferta/MU gobernada", "B/D", "Fuente local clave para duracion, tipo de plan, Codigo Unico y familia funcional."),
        (GOB_NIV_ACA, "TSV", "Gobernanza columna MU", "D", "Evidencia MU: NIV_ACA como semestre curricular; no regla automatica de Avance."),
        (REVISION_SIES_MU, "XLSX", "Auditoria Oferta/MU", "B/D", "Resuelve codigos SIES, planes, duracion y tipo plan en Matricula Unificada."),
        (RESUMEN_SIES_MU, "CSV", "Resumen Oferta/MU", "B/D", "Resumen de resolucion SIES-MU."),
        (MAPEO_OFERTA_CODCLI, "XLSX", "Mapeo Oferta/MU", "B/D", "Cruce oferta CODCLI y matriz oferta."),
        (REPORTE_FASE2_MU, "MD", "Reporte tecnico Oferta/MU", "C/D", "Reporte de fase SIES/Oferta MU."),
        (REPORTE_SIES_MU_JSON, "JSON", "Reporte tecnico Oferta/MU", "C/D", "Reporte JSON SIES/Oferta MU."),
        (MU_CONTROL, "CSV", "Salida control MU", "B/C", "Dato de contraste, no fuente estructural para Carreras."),
        (MU_OFICIAL, "XLSX", "Salida MU", "B/C", "Dato de contraste, no fuente estructural para Carreras."),
    ]
    for path, tipo, clasif, nivel, utilidad in base_sources:
        base = source_record(path, tipo, clasif, nivel, utilidad)
        if not path.exists():
            records.append(base)
            continue
        try:
            if tipo == "TSV":
                df = read_csv_flexible(path, sep="\t")
                records.append(inventory_dataframe(path, "", df, codes_43, base))
            elif tipo == "CSV":
                df = read_csv_flexible(path, sep=",")
                records.append(inventory_dataframe(path, "", df, codes_43, base))
            elif tipo == "XLSX":
                xl = pd.ExcelFile(path)
                for sh in xl.sheet_names:
                    try:
                        df = pd.read_excel(path, sheet_name=sh, dtype=str, nrows=50000)
                    except Exception:
                        continue
                    records.append(inventory_dataframe(path, sh, df, codes_43, base))
            else:
                text = path.read_text(encoding="utf-8", errors="replace")
                rec = dict(base)
                rec.update(
                    {
                        "filas": len(text.splitlines()),
                        "columnas": "",
                        "lista_columnas": "",
                        "contiene_CODIGO_UNICO": "SI" if "CODIGO_UNICO" in text else "NO",
                        "contiene_COD_CARRERA": "SI" if any(t in text for t in ["COD_CARRERA", "COD_CAR", "CODCARPR"]) else "NO",
                        "contiene_COD_SEDE": "SI" if "COD_SEDE" in text else "NO",
                        "contiene_JORNADA": "SI" if "JORNADA" in text else "NO",
                        "contiene_VERSION": "SI" if "VERSION" in text else "NO",
                        "contiene_DURACION_ESTUDIOS": "SI" if "DURACION_ESTUDIOS" in text else "NO",
                        "contiene_TIPO_PLAN_CARRERA": "SI" if "TIPO_PLAN_CARRERA" in text else "NO",
                        "contiene_NOMBRE_CARRERA": "SI" if "NOMBRE_CARRERA" in text else "NO",
                        "contiene_familia_funcional": "SI" if any(t in normalize_text(text) for t in ["TECNIC", "CONTINUID", "INGENIER"]) else "NO",
                        "match_43_CODIGO_UNICO": sum(1 for code in codes_43 if code in text),
                        "duplicados_CODIGO_UNICO": "",
                    }
                )
                records.append(rec)
        except Exception as exc:
            rec = dict(base)
            rec["observacion_error_lectura"] = str(exc)
            records.append(rec)

    return pd.DataFrame(records)


def build_codigo_plan_map(precarga: pd.DataFrame, canonico: pd.DataFrame, conciliacion: pd.DataFrame, por_plan: pd.DataFrame) -> tuple[dict[str, str], dict[str, str]]:
    canonical_set = set(canonico["CODPESTUD"].astype(str).str.strip())
    code_to_plan: dict[str, str] = {}
    origin: dict[str, str] = {}
    candidates = [
        "CODPESTUD",
        "PLAN_DE_ESTUDIO_CANONICO_CIERRE",
        "PLAN_DE_ESTUDIO_CANONICO_DECISION",
        "PLAN_DE_ESTUDIO_CANONICO",
    ]
    for _, row in conciliacion.iterrows():
        code = str(row.get("CODIGO_UNICO", "")).strip()
        for col in candidates:
            if col not in conciliacion.columns:
                continue
            value = str(row.get(col, "")).strip()
            if value and value.lower() != "nan" and value in canonical_set:
                code_to_plan[code] = value
                origin[code] = f"CONCILIACION_43:{col}"
                break

    for _, row in por_plan.iterrows():
        finals = split_codes(row.get("CODIGOS_SIES_FINALES_USADOS", ""))
        plan = str(row.get("PLAN_DE_ESTUDIO", "")).strip()
        if not plan or plan not in canonical_set:
            continue
        for code in finals:
            if code in set(precarga["CODIGO_UNICO"].astype(str)) and code not in code_to_plan:
                code_to_plan[code] = plan
                origin[code] = "OFERTA_MU_POR_PLAN:CODIGOS_SIES_FINALES_USADOS"
    return code_to_plan, origin


def build_match_oferta(precarga: pd.DataFrame, duracion: pd.DataFrame, por_plan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    dur_idx = duracion.drop_duplicates("CODIGO_UNICO").set_index("CODIGO_UNICO")
    for _, row in precarga.iterrows():
        code = str(row["CODIGO_UNICO"]).strip()
        parts = extract_code_parts(code)
        dur_row = dur_idx.loc[code] if code in dur_idx.index else pd.Series(dtype=object)
        por_rows = por_plan[por_plan["CODIGOS_SIES_FINALES_USADOS"].apply(lambda x: contains_code(x, code))]
        por = por_rows.iloc[0] if len(por_rows) else pd.Series(dtype=object)
        tipo_plan = por.get("TIPO_PLAN_CARRERA", dur_row.get("TIPO_PLAN_CARRERA", ""))
        nivel_carrera = dur_row.get("NIVEL_CARRERA", row.get("NIVEL_CARRERA", ""))
        family, family_obs = classify_family(row.get("NOMBRE_CARRERA", ""), tipo_plan, nivel_carrera)
        rows.append(
            {
                "CODIGO_UNICO": code,
                "PLAN_ESTUDIOS": row.get("PLAN_ESTUDIOS", ""),
                "NOMBRE_CARRERA": row.get("NOMBRE_CARRERA", ""),
                "JORNADA": row.get("JORNADA", ""),
                "VERSION": row.get("VERSION", ""),
                **parts,
                "DURACION_ESTUDIOS_5810": row.get("DURACION_ESTUDIOS", ""),
                "DURACION_OFERTA_MU": dur_row.get("DURACION_ESTUDIOS", ""),
                "DURACION_POR_PLAN_MU": por.get("DURACION_ESTUDIOS", ""),
                "TIPO_PLAN_CARRERA": tipo_plan,
                "NIVEL_CARRERA_OFERTA": nivel_carrera,
                "CODCARPR_CANONICO_OFERTA": dur_row.get("CODCARPR_CANONICO", ""),
                "PLAN_DE_ESTUDIO_MU": por.get("PLAN_DE_ESTUDIO", ""),
                "CODIGOS_SIES_FINALES_MU": por.get("CODIGOS_SIES_FINALES_USADOS", ""),
                "ESTADO_RESOLUCION_MU": por.get("ESTADO_RESOLUCION", ""),
                "METODOS_USADOS_MU": por.get("METODOS_USADOS", ""),
                "REGLAS_MANUALES_MU": por.get("REGLAS_MANUALES", ""),
                "FAMILIA_FUNCIONAL": family,
                "OBS_FAMILIA_FUNCIONAL": family_obs,
                "ESTADO_MATCH_OFERTA": "MATCH_OFERTA_MU" if code in dur_idx.index else "SIN_MATCH_OFERTA_MU",
                "DURACION_COINCIDE_5810_MU": "SI" if str(row.get("DURACION_ESTUDIOS", "")).strip() == str(dur_row.get("DURACION_ESTUDIOS", "")).strip() else "NO",
                "OBSERVACION": "Dato observado MU/Oferta; no reemplaza regla oficial de Avance.",
            }
        )
    return pd.DataFrame(rows)


def build_plan_detail(
    precarga: pd.DataFrame,
    canonico: pd.DataFrame,
    code_to_plan: dict[str, str],
    plan_origin: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    detail_rows: list[pd.DataFrame] = []
    dist_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    for _, row in precarga.iterrows():
        code = str(row["CODIGO_UNICO"]).strip()
        dur = to_int(row.get("DURACION_ESTUDIOS"))
        allowed = math.ceil(dur / 2) if dur else 0
        plan = code_to_plan.get(code, "")
        det = canonico[canonico["CODPESTUD"].astype(str).str.strip() == plan].copy() if plan else canonico.iloc[0:0].copy()
        units_by_year = {col: 0 for col in UNIT_COLUMNS}
        outside_units = 0
        years_without_units: list[str] = []
        if not det.empty:
            det["CODIGO_UNICO"] = code
            det["NOMBRE_CARRERA_5810"] = row.get("NOMBRE_CARRERA", "")
            det["DURACION_ESTUDIOS_5810"] = dur
            det["ANIOS_PERMITIDOS"] = allowed
            det["NIVEL_NUM"] = pd.to_numeric(det["NIVEL"], errors="coerce")
            det = det.dropna(subset=["NIVEL_NUM"]).copy()
            det["NIVEL_NUM"] = det["NIVEL_NUM"].astype(int)
            det["ANIO_SIES_CANDIDATO"] = ((det["NIVEL_NUM"] + 1) // 2).astype(int)
            det["UNIDAD_ID_USADA"] = det["CODRAMO"].astype(str).str.strip()
            det["VALIDACION_DURACION_UNIDAD"] = det["ANIO_SIES_CANDIDATO"].apply(lambda x: "FUERA_DURACION" if x > allowed else "DENTRO_DURACION")
            detail_rows.append(
                det[
                    [
                        "CODIGO_UNICO",
                        "CODPESTUD",
                        "CODRAMO",
                        "RAMOEQUIV",
                        "NOMBRE",
                        "NIVEL",
                        "NIVEL_NUM",
                        "ANIO_SIES_CANDIDATO",
                        "UNIDAD_ID_USADA",
                        "DURACION_ESTUDIOS_5810",
                        "ANIOS_PERMITIDOS",
                        "VALIDACION_DURACION_UNIDAD",
                        "FUENTE",
                        "HOJA_FUENTE",
                        "NIVEL_RESPALDO",
                        "ESTADO_CANONICO",
                    ]
                ]
            )
            dedup = det.drop_duplicates(["CODIGO_UNICO", "UNIDAD_ID_USADA", "ANIO_SIES_CANDIDATO"])
            for y in range(1, 8):
                col = UNIT_COLUMNS[y - 1]
                units_by_year[col] = int(dedup.loc[dedup["ANIO_SIES_CANDIDATO"] == y, "UNIDAD_ID_USADA"].nunique())
            outside_units = int(dedup.loc[dedup["ANIO_SIES_CANDIDATO"] > allowed, "UNIDAD_ID_USADA"].nunique())
            for y in range(1, min(allowed, 7) + 1):
                if units_by_year[UNIT_COLUMNS[y - 1]] == 0:
                    years_without_units.append(str(y))
            niveles = sorted(det["NIVEL_NUM"].dropna().astype(int).unique().tolist())
            nivel_min = min(niveles) if niveles else ""
            nivel_max = max(niveles) if niveles else ""
            registros_detalle = len(det)
            unidades_unicas = int(det["UNIDAD_ID_USADA"].nunique())
        else:
            niveles = []
            nivel_min = ""
            nivel_max = ""
            registros_detalle = 0
            unidades_unicas = 0

        total = int(sum(units_by_year.values()))
        estado = "BLOQUEADO"
        motivo = []
        if not plan:
            motivo.append("sin CODPESTUD trazable")
        if registros_detalle == 0:
            motivo.append("sin detalle canonico")
        if outside_units > 0:
            motivo.append("conversion candidata genera unidades fuera de duracion")
        if not motivo:
            estado = "APTO_CANDIDATO"
            motivo.append("sin unidades fuera bajo regla candidata")
        dist_rows.append(
            {
                "CODIGO_UNICO": code,
                "PLAN_ESTUDIOS": row.get("PLAN_ESTUDIOS", ""),
                "NOMBRE_CARRERA": row.get("NOMBRE_CARRERA", ""),
                "DURACION_ESTUDIOS": dur,
                "ANIOS_PERMITIDOS": allowed,
                "CODPESTUD": plan,
                "ORIGEN_CODPESTUD": plan_origin.get(code, ""),
                "REGISTROS_DETALLE": registros_detalle,
                "UNIDADES_UNICAS_CODRAMO": unidades_unicas,
                "NIVELES_OBSERVADOS": ", ".join(map(str, niveles)),
                "NIVEL_MIN": nivel_min,
                "NIVEL_MAX": nivel_max,
                "TOTAL_UNIDADES_MEDIDA_CANDIDATO": total,
                **units_by_year,
                "SUMA_ANIOS": total,
                "VALIDACION_TOTAL": "OK_TOTAL_SUMA_ANIOS" if total == sum(units_by_year.values()) else "ERROR_TOTAL",
                "UNIDADES_FUERA_DURACION": outside_units,
                "ANIOS_DENTRO_DURACION_SIN_UNIDADES": ", ".join(years_without_units),
                "ESTADO_FILA": estado,
                "MOTIVO_ESTADO": " | ".join(motivo),
            }
        )
        decision_rows.append(
            {
                "CODIGO_UNICO": code,
                "CODPESTUD": plan,
                "NOMBRE_CARRERA": row.get("NOMBRE_CARRERA", ""),
                "DURACION_ESTUDIOS": dur,
                "ANIOS_PERMITIDOS": allowed,
                "NIVEL_MAX": nivel_max,
                "UNIDADES_FUERA_DURACION": outside_units,
                "EVIDENCIA_A": "Manual exige distribucion anual compatible con duracion; no define NIVEL.",
                "EVIDENCIA_B": f"Plan canonico {plan} presenta NIVEL {nivel_min}-{nivel_max} y {unidades_unicas} CODRAMO unicos.",
                "EVIDENCIA_C": "Prueba tecnica ANIO=techo(NIVEL/2).",
                "DECISION_D": "NO_APROBAR_REGLA_GLOBAL" if outside_units > 0 else "APTO_SOLO_COMO_CASO_COMPATIBLE_NO_GLOBAL",
                "PENDIENTE_E": "Se requiere otra fuente/regla interna que ubique unidades por anio sin exceder duracion." if outside_units > 0 else "No pendiente para esta fila, pero regla global no queda aprobada por el conjunto.",
            }
        )
    detalle = pd.concat(detail_rows, ignore_index=True) if detail_rows else pd.DataFrame()
    distribucion = pd.DataFrame(dist_rows)
    decision = pd.DataFrame(decision_rows)
    return detalle, distribucion, decision


def build_cases_3(precarga: pd.DataFrame, conciliacion: pd.DataFrame, por_plan: pd.DataFrame, distribucion: pd.DataFrame) -> pd.DataFrame:
    codes = ["I162S2C83J4V1", "I162S2C85J4V1", "I162S2C86J4V1"]
    rows: list[dict[str, Any]] = []
    for code in codes:
        pre = precarga[precarga["CODIGO_UNICO"] == code].iloc[0]
        con = conciliacion[conciliacion["CODIGO_UNICO"] == code]
        con_row = con.iloc[0] if len(con) else pd.Series(dtype=object)
        por = por_plan[por_plan["CODIGOS_SIES_FINALES_USADOS"].apply(lambda x: contains_code(x, code))]
        por_row = por.iloc[0] if len(por) else pd.Series(dtype=object)
        dist = distribucion[distribucion["CODIGO_UNICO"] == code]
        dist_row = dist.iloc[0] if len(dist) else pd.Series(dtype=object)
        if str(por_row.get("PLAN_DE_ESTUDIO", "")).strip():
            categoria = "RESUELTO_POR_OFERTA_MU_Y_PROMEDIOS"
            obs = "Oferta/MU entrega plan y Codigo Unico final; PROMEDIOS queda solo como contraste no normativo."
        else:
            categoria = "BLOQUEADO"
            obs = "No se encontro plan en Oferta/MU."
        rows.append(
            {
                "CODIGO_UNICO": code,
                "NOMBRE_CARRERA": pre.get("NOMBRE_CARRERA", ""),
                "DURACION_ESTUDIOS_5810": pre.get("DURACION_ESTUDIOS", ""),
                "PLAN_CONCILIACION_H110": con_row.get("PLAN_DE_ESTUDIO_CANONICO_CIERRE", ""),
                "FUNDAMENTO_H110": con_row.get("FUNDAMENTO", ""),
                "EXCEPCION_H110": con_row.get("EXCEPCION", ""),
                "PLAN_OFERTA_MU": por_row.get("PLAN_DE_ESTUDIO", ""),
                "TIPO_PLAN_CARRERA_MU": por_row.get("TIPO_PLAN_CARRERA", ""),
                "DURACION_MU": por_row.get("DURACION_ESTUDIOS", ""),
                "ESTADO_RESOLUCION_MU": por_row.get("ESTADO_RESOLUCION", ""),
                "METODOS_USADOS_MU": por_row.get("METODOS_USADOS", ""),
                "CODPESTUD_USADO_CANDIDATO": dist_row.get("CODPESTUD", ""),
                "REGISTROS_DETALLE_CANONICO": dist_row.get("REGISTROS_DETALLE", ""),
                "NIVELES_OBSERVADOS": dist_row.get("NIVELES_OBSERVADOS", ""),
                "UNIDADES_FUERA_DURACION_BAJO_TECHO_NIVEL_2": dist_row.get("UNIDADES_FUERA_DURACION", ""),
                "CATEGORIA": categoria,
                "DICTAMEN_CASO": "Plan trazable resuelto; distribucion anual sigue bloqueada por regla NIVEL->anio." if categoria != "BLOQUEADO" else "Bloqueado por falta de evidencia.",
                "OBSERVACION": obs,
            }
        )
    return pd.DataFrame(rows)


def build_promedios_contrast(precarga: pd.DataFrame) -> pd.DataFrame:
    if not PROMEDIOS.exists():
        return pd.DataFrame(
            [
                {
                    "estado": "SIN_PROMEDIOS",
                    "observacion": "No se encontro PROMEDIOS. No se usa como fuente normativa.",
                }
            ]
        )
    try:
        hoja = pd.read_excel(PROMEDIOS, sheet_name="Hoja1", dtype=str)
    except Exception:
        hoja = pd.read_excel(PROMEDIOS, sheet_name=0, dtype=str)
    rows: list[dict[str, Any]] = []
    for _, pre in precarga.iterrows():
        nombre = normalize_text(pre.get("NOMBRE_CARRERA", ""))
        cod_carrera = extract_code_parts(str(pre.get("CODIGO_UNICO", ""))).get("COD_CARRERA_PARSE", "")
        # PROMEDIOS no contiene CODIGO_UNICO; se usa contraste por nombre/CODCARR si aparece.
        subset = hoja.iloc[0:0]
        if "CARRERA" in hoja.columns:
            subset = hoja[hoja["CARRERA"].apply(normalize_text) == nombre]
        if subset.empty and "CODCARR" in hoja.columns:
            # Codigo carrera SIES no equivale necesariamente a CODCARPR; se registra solo si hay coincidencia textual exacta.
            subset = hoja[hoja["CODCARR"].astype(str).str.extract(r"(\d+)", expand=False).fillna("") == cod_carrera]
        nivel_values = list_values(pd.to_numeric(subset["NIVEL"], errors="coerce").dropna().astype(int).astype(str)) if "NIVEL" in subset.columns and not subset.empty else ""
        rows.append(
            {
                "CODIGO_UNICO": pre.get("CODIGO_UNICO", ""),
                "NOMBRE_CARRERA": pre.get("NOMBRE_CARRERA", ""),
                "FILAS_PROMEDIOS_CONTRASTE": len(subset),
                "CODCARR_PROMEDIOS": list_values(subset["CODCARR"]) if "CODCARR" in subset.columns and not subset.empty else "",
                "PLANES_PROMEDIOS": list_values(subset["PLAN_DE_ESTUDIO"]) if "PLAN_DE_ESTUDIO" in subset.columns and not subset.empty else "",
                "NIVELES_PROMEDIOS_OBSERVADOS": nivel_values,
                "ANOS_PROMEDIOS": list_values(subset["ANO"]) if "ANO" in subset.columns and not subset.empty else "",
                "PERIODOS_PROMEDIOS": list_values(subset["PERIODO"]) if "PERIODO" in subset.columns and not subset.empty else "",
                "USO": "Contraste interno B; no fuente normativa ni estructural para Carreras.",
                "DICTAMEN_CONTRASTE": "PROMEDIOS contiene NIVEL academico observado, pero no gobierna estructura anual de Carreras 16769.",
            }
        )
    return pd.DataFrame(rows)


def build_validations(
    precarga: pd.DataFrame,
    match_oferta: pd.DataFrame,
    distribucion: pd.DataFrame,
    cases_3: pd.DataFrame,
) -> tuple[pd.DataFrame, str]:
    total_43 = len(precarga)
    match_mu = int((match_oferta["ESTADO_MATCH_OFERTA"] == "MATCH_OFERTA_MU").sum())
    dur_match = int((match_oferta["DURACION_COINCIDE_5810_MU"] == "SI").sum())
    detalle = int((distribucion["REGISTROS_DETALLE"] > 0).sum())
    fuera = int((distribucion["UNIDADES_FUERA_DURACION"] > 0).sum())
    total_ok = int((distribucion["VALIDACION_TOTAL"] == "OK_TOTAL_SUMA_ANIOS").sum())
    tres_resueltos = int((cases_3["CATEGORIA"] != "BLOQUEADO").sum())
    conversion_aprobada = fuera == 0 and detalle == 43
    validations = [
        ("43/43 carreras con duracion validada en MU/Oferta", "43", match_mu, "OK" if match_mu == 43 else "BLOQUEADO"),
        ("Duracion 5810 coincide con Oferta/MU", "43", dur_match, "OK" if dur_match == 43 else "BLOQUEADO"),
        ("43/43 carreras con detalle o justificacion formal", "43", detalle, "OK" if detalle == 43 else "BLOQUEADO"),
        ("3 carreras sin detalle H110 resueltas trazablemente", "3", tres_resueltos, "OK" if tres_resueltos == 3 else "BLOQUEADO"),
        ("NIVEL interpretado trazablemente como semestre para Avance", "SI", "NO", "BLOQUEADO"),
        ("ANIO=techo(NIVEL/2) aprobado como decision interna global", "SI", "NO" if not conversion_aprobada else "SI", "BLOQUEADO" if not conversion_aprobada else "OK"),
        ("Cero carreras con unidades fuera de duracion", "0", fuera, "OK" if fuera == 0 else "BLOQUEADO"),
        ("TOTAL_UNIDADES_MEDIDA = suma anios candidato", "43", total_ok, "OK" if total_ok == 43 else "BLOQUEADO"),
        ("Sin PROMEDIOS como norma", "SI", "SI", "OK"),
        ("Sin matricula 5809 como fuente estructural", "SI", "SI", "OK"),
        ("Sin matriz agregada rechazada por SIES como fuente final", "SI", "SI", "OK"),
        ("CSV final generado", "NO", "NO", "OK"),
        ("SIES_READY generado", "NO", "NO", "OK"),
    ]
    val_df = pd.DataFrame(validations, columns=["validacion", "esperado", "observado", "estado"])
    if conversion_aprobada and match_mu == 43 and dur_match == 43 and tres_resueltos == 3:
        dictamen = "APTO_PARA_GENERAR_CSV_H112"
    elif not conversion_aprobada:
        dictamen = "BLOQUEADO_TOTAL"
    else:
        dictamen = "BLOQUEADO_PARCIAL"
    return val_df, dictamen


def build_summary(dictamen: str, precarga: pd.DataFrame, match_oferta: pd.DataFrame, distribucion: pd.DataFrame, cases_3: pd.DataFrame) -> pd.DataFrame:
    total = len(precarga)
    match_mu = int((match_oferta["ESTADO_MATCH_OFERTA"] == "MATCH_OFERTA_MU").sum())
    detalle = int((distribucion["REGISTROS_DETALLE"] > 0).sum())
    fuera = int((distribucion["UNIDADES_FUERA_DURACION"] > 0).sum())
    tres_resueltos = int((cases_3["CATEGORIA"] != "BLOQUEADO").sum())
    rows = [
        ("Proceso", "Avance Curricular SIES 2026"),
        ("Subproyecto", "Carreras Avance Curricular 2026 / ID SIES 16769"),
        ("Ano proceso", "2026"),
        ("Ano referencia datos", "2025"),
        ("Estado final", dictamen),
        ("Declaracion carga", "NO_LISTO_PARA_CARGA"),
        ("CSV final generado", "NO"),
        ("SIES_READY generado", "NO"),
        ("Fuentes originales modificadas", "NO"),
        ("Precarga 5810 filas", total),
        ("Match Oferta/MU por CODIGO_UNICO", f"{match_mu}/43"),
        ("Carreras con detalle canonico despues de resolver H110+MU", f"{detalle}/43"),
        ("Tres carreras H110 sin detalle resueltas por Oferta/MU", f"{tres_resueltos}/3"),
        ("Carreras con unidades fuera de duracion bajo ANIO=techo(NIVEL/2)", fuera),
        ("Decision interna NIVEL->anio", "NO_APROBADA_GLOBALMENTE"),
        ("Motivo dictamen", "La evidencia interna resuelve duracion, tipo plan y CODPESTUD, pero la regla candidata genera unidades fuera de duracion en 42/43 carreras; no queda habilitado H112."),
    ]
    return pd.DataFrame(rows, columns=["campo", "valor"])


def build_trazabilidad(dictamen: str) -> pd.DataFrame:
    rows = [
        {
            "tipo": "A. Regla oficial",
            "afirmacion": "Carreras 16769 informa estructura de plan; duracion de estudios se valida como semestres y la distribucion anual debe coincidir con la duracion.",
            "fuente": str(MANUAL),
            "uso_en_dictamen": "Gobierna la exigencia de distribucion compatible con duracion; no define NIVEL.",
        },
        {
            "tipo": "B. Dato observado",
            "afirmacion": "Precarga 5810 contiene 43 carreras, duracion, columnas de unidades y CODIGO_UNICO.",
            "fuente": str(PRECARGA_5810),
            "uso_en_dictamen": "Base de universo 43 y duracion a validar.",
        },
        {
            "tipo": "B/D. Dato observado + decision interna previa",
            "afirmacion": "Oferta/MU resuelve 43/43 CODIGO_UNICO, duracion y tipo de plan; ademas resuelve ADMP20251, CONG20251 y AUDT20251.",
            "fuente": str(REVISION_SIES_MU),
            "uso_en_dictamen": "Permite cerrar enlace de los tres casos sin CODPESTUD estructurado en H110.",
        },
        {
            "tipo": "B. Dato observado",
            "afirmacion": "Planes canonicos contienen CODPESTUD, CODRAMO y NIVEL, pero no diccionario de equivalencia temporal.",
            "fuente": str(CANONICO_PLANES),
            "uso_en_dictamen": "Permite probar regla candidata y detectar contradiccion con duracion.",
        },
        {
            "tipo": "C. Implementacion tecnica",
            "afirmacion": "Se simula ANIO=techo(NIVEL/2), deduplicando por CODRAMO y validando contra techo(DURACION_ESTUDIOS/2).",
            "fuente": "decision_interna_nivel_periodizacion_carreras_16769.py",
            "uso_en_dictamen": "Prueba controlada; no aplica correcciones ni genera carga.",
        },
        {
            "tipo": "D. Decision interna",
            "afirmacion": "No se aprueba globalmente ANIO=techo(NIVEL/2) para H112.",
            "fuente": "H111",
            "uso_en_dictamen": dictamen,
        },
        {
            "tipo": "E. Pendiente",
            "afirmacion": "Se requiere una regla/fuente interna distinta que ubique unidades por anio formal sin exceder duracion.",
            "fuente": "H111",
            "uso_en_dictamen": "Mantiene NO_LISTO_PARA_CARGA.",
        },
    ]
    return pd.DataFrame(rows)


def build_kpi(
    precarga: pd.DataFrame,
    match_oferta: pd.DataFrame,
    distribucion: pd.DataFrame,
    detalle: pd.DataFrame,
    prom: pd.DataFrame,
    dictamen: str,
) -> pd.DataFrame:
    rows = [
        ("dictamen", dictamen),
        ("filas_precarga_5810", len(precarga)),
        ("columnas_precarga_5810", len(precarga.columns)),
        ("match_oferta_mu", int((match_oferta["ESTADO_MATCH_OFERTA"] == "MATCH_OFERTA_MU").sum())),
        ("duracion_coincide_5810_mu", int((match_oferta["DURACION_COINCIDE_5810_MU"] == "SI").sum())),
        ("carreras_con_detalle_candidato", int((distribucion["REGISTROS_DETALLE"] > 0).sum())),
        ("carreras_sin_detalle_candidato", int((distribucion["REGISTROS_DETALLE"] == 0).sum())),
        ("carreras_con_unidades_fuera_duracion", int((distribucion["UNIDADES_FUERA_DURACION"] > 0).sum())),
        ("carreras_sin_unidades_fuera_duracion", int((distribucion["UNIDADES_FUERA_DURACION"] == 0).sum())),
        ("unidades_fuera_duracion_total", int(distribucion["UNIDADES_FUERA_DURACION"].sum())),
        ("niveles_min_max_detalle", f"{detalle['NIVEL_NUM'].min() if not detalle.empty else ''}-{detalle['NIVEL_NUM'].max() if not detalle.empty else ''}"),
        ("filas_promedios_contraste_total", int(pd.to_numeric(prom["FILAS_PROMEDIOS_CONTRASTE"], errors="coerce").fillna(0).sum()) if "FILAS_PROMEDIOS_CONTRASTE" in prom.columns else 0),
        ("csv_final_generado", "NO"),
        ("sies_ready_generado", "NO"),
    ]
    return pd.DataFrame(rows, columns=["indicador", "valor"])


def build_manifest(out_dir: Path, desktop_dir: Path, generated: dict[str, Path], dictamen: str, sources: list[Path]) -> dict[str, Any]:
    return {
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "Carreras Avance Curricular 2026 / ID SIES 16769",
        "hito": "111_decision_interna_nivel_periodizacion_carreras_16769",
        "timestamp": out_dir.name.split("_")[-2] + "_" + out_dir.name.split("_")[-1],
        "dictamen": dictamen,
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "csv_final_generado": "NO",
        "sies_ready_generado": "NO",
        "fuentes_originales_modificadas": "NO",
        "fuentes": [
            {
                "ruta": str(path),
                "existe": path.exists(),
                "sha256": sha256_file(path),
            }
            for path in sources
        ],
        "productos": {
            key: {
                "ruta": str(path),
                "existe": path.exists(),
                "sha256": sha256_file(path),
            }
            for key, path in generated.items()
        },
        "carpeta_github": str(out_dir),
        "carpeta_escritorio": str(desktop_dir),
    }


def write_report(
    path: Path,
    dictamen: str,
    resumen: pd.DataFrame,
    reglas: pd.DataFrame,
    match_oferta: pd.DataFrame,
    decision: pd.DataFrame,
    distribucion: pd.DataFrame,
    cases_3: pd.DataFrame,
    validations: pd.DataFrame,
) -> None:
    fuera = distribucion[distribucion["UNIDADES_FUERA_DURACION"] > 0]
    compatibles = distribucion[distribucion["UNIDADES_FUERA_DURACION"] == 0]
    lines = [
        "# Informe H111 - Decision interna NIVEL / periodizacion Carreras 16769",
        "",
        f"**Dictamen:** {dictamen}",
        "",
        "Este hito no modifica fuentes originales, no genera CSV final, no genera SIES_READY y no declara carga lista.",
        "",
        "## Resumen",
        make_markdown_table(resumen),
        "",
        "## A. Regla oficial",
        "El instructivo Avance Curricular gobierna Carreras 16769 como estructura de plan, con duracion de estudios en semestres y distribucion anual de unidades. El instructivo no define la columna raw `NIVEL` de los planes canonicos.",
        "",
        make_markdown_table(reglas[["regla", "referencia_lineas", "interpretacion_operativa", "nivel_respaldo"]]),
        "",
        "## B. Datos observados",
        "- Precarga 5810: 43 carreras.",
        "- Oferta/MU `DURACION_ESTUDIOS.tsv`: match 43/43 por `CODIGO_UNICO` y duracion coincidente con 5810.",
        "- Auditoria SIES/MU: resuelve los tres planes que H110 habia dejado sin enlace estructurado: ADMP20251, CONG20251 y AUDT20251.",
        "- Plan canonico: contiene `CODPESTUD`, `CODRAMO` y `NIVEL`, pero no trae diccionario que convierta `NIVEL` a anio formal SIES.",
        "- PROMEDIOS se usa solo como contraste interno; no es fuente normativa ni estructural para Carreras.",
        "",
        "## C. Implementacion tecnica probada",
        "Se simulo `ANIO_SIES = techo(NIVEL / 2)` sobre los planes canonicos, deduplicando unidades por `CODRAMO`, y se valido contra `ANIOS_PERMITIDOS = techo(DURACION_ESTUDIOS / 2)`.",
        "",
        "## D. Decision interna",
        "La decision interna de H111 es **no aprobar globalmente** la conversion `ANIO = techo(NIVEL / 2)` para generar H112. Aunque la evidencia MU/Oferta resuelve duracion, tipo de plan y los tres `CODPESTUD` faltantes, la conversion candidata produce unidades fuera de duracion en 42 de 43 carreras.",
        "",
        "La evidencia interna si permite cerrar que las tres carreras H110 sin enlace estructurado tienen plan trazable por Oferta/MU, pero eso no basta para reconstruir la distribucion anual.",
        "",
        "## E. Pendientes",
        "Queda pendiente una fuente o regla interna distinta que ubique cada unidad del plan en el anio formal SIES sin exceder duracion. No corresponde pasar a H112 mientras esa regla no exista o no supere las validaciones bloqueantes.",
        "",
        "## Match 5810 vs Oferta/MU",
        make_markdown_table(match_oferta[["CODIGO_UNICO", "NOMBRE_CARRERA", "DURACION_ESTUDIOS_5810", "DURACION_OFERTA_MU", "TIPO_PLAN_CARRERA", "FAMILIA_FUNCIONAL", "ESTADO_MATCH_OFERTA"]], 12),
        "",
        "## Decision NIVEL a anio",
        make_markdown_table(decision[["CODIGO_UNICO", "CODPESTUD", "NOMBRE_CARRERA", "DURACION_ESTUDIOS", "NIVEL_MAX", "UNIDADES_FUERA_DURACION", "DECISION_D", "PENDIENTE_E"]], 12),
        "",
        "## Resultado de validaciones",
        make_markdown_table(validations),
        "",
        "## Tres carreras H110",
        make_markdown_table(cases_3),
        "",
        "## Carreras compatibles bajo la regla candidata",
        make_markdown_table(compatibles[["CODIGO_UNICO", "NOMBRE_CARRERA", "CODPESTUD", "DURACION_ESTUDIOS", "NIVEL_MAX", "UNIDADES_FUERA_DURACION"]]),
        "",
        "## Carreras con unidades fuera de duracion",
        make_markdown_table(fuera[["CODIGO_UNICO", "NOMBRE_CARRERA", "CODPESTUD", "DURACION_ESTUDIOS", "ANIOS_PERMITIDOS", "NIVEL_MAX", "UNIDADES_FUERA_DURACION", "MOTIVO_ESTADO"]], 20),
        "",
        "## Conclusion",
        f"Dictamen H111: **{dictamen}**. No se habilita generacion de CSV final en H112 con la regla candidata actual.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def autosize_excel(path: Path) -> None:
    try:
        from openpyxl import load_workbook
    except Exception:
        return
    wb = load_workbook(path)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        for col_cells in ws.columns:
            letter = col_cells[0].column_letter
            width = 10
            for cell in col_cells[:200]:
                if cell.value is None:
                    continue
                width = max(width, min(60, len(str(cell.value)) + 2))
            ws.column_dimensions[letter].width = width
    wb.save(path)


def main() -> None:
    stamp = now_stamp()
    out_dir = OUT_BASE / f"DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769_{stamp}"
    desktop_dir = DESKTOP_BASE / f"AVANCE_CURRICULAR_2026_DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    data = load_inputs()
    precarga = data["precarga"]
    canonico = data["canonico"]
    conciliacion = data["conciliacion"]
    duracion = data["duracion"]
    por_plan = data["por_plan"]
    codes_43 = set(precarga["CODIGO_UNICO"].astype(str))

    reglas = extract_manual_rules()
    inventario = build_inventory(codes_43, data)
    match_oferta = build_match_oferta(precarga, duracion, por_plan)
    code_to_plan, plan_origin = build_codigo_plan_map(precarga, canonico, conciliacion, por_plan)
    detalle, distribucion, decision = build_plan_detail(precarga, canonico, code_to_plan, plan_origin)
    prom_contrast = build_promedios_contrast(precarga)
    cases_3 = build_cases_3(precarga, conciliacion, por_plan, distribucion)
    validations, dictamen = build_validations(precarga, match_oferta, distribucion, cases_3)
    resumen = build_summary(dictamen, precarga, match_oferta, distribucion, cases_3)
    trazabilidad = build_trazabilidad(dictamen)
    kpi = build_kpi(precarga, match_oferta, distribucion, detalle, prom_contrast, dictamen)

    sources = [
        MANUAL,
        PRECARGA_5810,
        H109_XLSX,
        H110_XLSX,
        CANONICO_PLANES,
        CONCILIACION_43,
        DURACION_MU,
        GOB_NIV_ACA,
        REVISION_SIES_MU,
        RESUMEN_SIES_MU,
        MAPEO_OFERTA_CODCLI,
        REPORTE_FASE2_MU,
        REPORTE_SIES_MU_JSON,
        MU_CONTROL,
        MU_OFICIAL,
        PROMEDIOS,
    ]

    excel_path = out_dir / "DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769.xlsx"
    report_path = out_dir / "INFORME_DECISION_INTERNA_NIVEL_PERIODIZACION_CARRERAS_16769.md"
    manifest_path = out_dir / "manifest_decision_interna_nivel_periodizacion_carreras_16769.json"
    script_path = out_dir / "decision_interna_nivel_periodizacion_carreras_16769.py"

    manifest_preview = pd.DataFrame(
        [
            {"tipo": "entrada", "ruta": str(path), "existe": path.exists(), "sha256": sha256_file(path)}
            for path in sources
        ]
    )

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="00_RESUMEN_DICTAMEN", index=False)
        reglas.to_excel(writer, sheet_name="01_REGLAS_MANUAL", index=False)
        precarga.to_excel(writer, sheet_name="02_PRECARGA_5810", index=False)
        inventario.to_excel(writer, sheet_name="03_INVENTARIO_OFERTA_MU", index=False)
        match_oferta.to_excel(writer, sheet_name="04_MATCH_5810_OFERTA_MU", index=False)
        detalle.to_excel(writer, sheet_name="05_PLAN_CANONICO_DETALLE", index=False)
        prom_contrast.to_excel(writer, sheet_name="06_PROMEDIOS_CONTRASTE", index=False)
        decision.to_excel(writer, sheet_name="07_DECISION_NIVEL_A_ANIO", index=False)
        distribucion.to_excel(writer, sheet_name="08_DISTRIBUCION_CANDIDATA_40", index=False)
        cases_3.to_excel(writer, sheet_name="09_CASOS_3_SIN_DETALLE", index=False)
        validations.to_excel(writer, sheet_name="10_VALIDACIONES_BLOQUEANTES", index=False)
        trazabilidad.to_excel(writer, sheet_name="11_TRAZABILIDAD_DECISION", index=False)
        kpi.to_excel(writer, sheet_name="12_KPI", index=False)
        manifest_preview.to_excel(writer, sheet_name="13_MANIFEST", index=False)
    autosize_excel(excel_path)

    write_report(report_path, dictamen, resumen, reglas, match_oferta, decision, distribucion, cases_3, validations)
    shutil.copy2(Path(__file__), script_path)

    generated = {
        "excel": excel_path,
        "informe": report_path,
        "manifest": manifest_path,
        "script": script_path,
    }
    manifest = build_manifest(out_dir, desktop_dir, generated, dictamen, sources)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if desktop_dir.exists():
        shutil.rmtree(desktop_dir)
    shutil.copytree(out_dir, desktop_dir)

    print("DECISION INTERNA NIVEL PERIODIZACION CARRERAS 16769 — GENERADA")
    print("Fuentes originales modificadas: NO")
    print("CSV final generado: NO")
    print("SIES_READY generado: NO")
    print("Declaracion carga: NO_LISTO_PARA_CARGA")
    print(f"Dictamen: {dictamen}")
    print()
    print("DICTAMEN")
    print(resumen.to_string(index=False))
    print()
    print("VALIDACIONES BLOQUEANTES")
    print(validations.to_string(index=False))
    print()
    print("CASOS 3 SIN DETALLE")
    print(cases_3[["CODIGO_UNICO", "NOMBRE_CARRERA", "PLAN_OFERTA_MU", "CATEGORIA", "DICTAMEN_CASO"]].to_string(index=False))
    print()
    print("ARCHIVOS")
    print(f"Excel: {excel_path}")
    print(f"Informe: {report_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Script: {script_path}")
    print(f"Carpeta escritorio: {desktop_dir}")


if __name__ == "__main__":
    main()
