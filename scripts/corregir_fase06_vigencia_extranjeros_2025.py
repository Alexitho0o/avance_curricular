#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, PatternFill


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BRIDGE_V2 = ROOT / "resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026_V2 2.tsv"
BRIDGE_V1 = ROOT / "resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026.tsv"
DURACION = ROOT / "DURACION_ESTUDIOS.tsv"

COLUMNAS_SIES_REGULARES = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "TIPO_RESIDENCIA_ESTUDIANTE",
    "PAIS_DE_ORIGEN",
    "PAIS_ESTUDIOS_SECUNDARIOS",
    "CODIGO_UNICO",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "NOMBRE_UNIVERSIDAD_ORIGEN",
    "PAIS_UNIVERSIDAD_ORIGEN",
    "VIGENCIA",
]

OFFICIAL_COLS = ["PAIS_ORIGEN" if col == "PAIS_DE_ORIGEN" else col for col in COLUMNAS_SIES_REGULARES]

REGLAS_CERO = {
    ("ELIMINADO", "23 - RETIRO - RETRACTO"): "REGLA_INSTITUCIONAL_RETIRO_RETRACTO",
    ("ELIMINADO", "11 - RENUNCIA POST INICIO CLASES"): "REGLA_INSTITUCIONAL_RENUNCIA_POST_INICIO",
    ("ELIMINADO", "24 - CAMBIO DE CARRERA"): "REGLA_INSTITUCIONAL_CAMBIO_DE_CARRERA",
    ("TITULADO", "31 - TITULADO APROBADO"): "REGLA_INSTITUCIONAL_TITULADO_APROBADO",
}

DECISION_INSTITUCIONAL_CERO = {
    "PRECARGA_0085": "RETIRO - RETRACTO respaldado por Hoja2.",
    "PRECARGA_0094": "CAMBIO DE CARRERA respaldado por Hoja2.",
    "PRECARGA_0113": "CAMBIO DE CARRERA respaldado por Hoja2.",
    "PRECARGA_0121": "CAMBIO DE CARRERA respaldado por Hoja2.",
    "PRECARGA_0152": "RETIRO - RETRACTO respaldado por Hoja2.",
}

DECISION_INSTITUCIONAL_MANTENER = {
    "PRECARGA_0010",
    "PRECARGA_0012",
    "PRECARGA_0014",
    "PRECARGA_0047",
    "PRECARGA_0066",
    "PRECARGA_0071",
    "PRECARGA_0091",
    "PRECARGA_0110",
    "PRECARGA_0153",
    "PRECARGA_0156",
    "PRECARGA_0157",
    "PRECARGA_0162",
}

REGLA_MANTENER_PRECARGA = "MANTENER_VIGENCIA_PRECARGA_OFICIAL_SIN_EVIDENCIA_DE_EXCLUSION"
FUENTE_PRECARGA_OFICIAL = "Reporte Precarga del Proceso Extranjeros Regulares 2026.csv"

SHEET_REQUIRED_COLUMNS = [
    "CODCLI",
    "CODCARPR",
    "ANOMATRICULA",
    "PERIODOMATRICULA",
    "FECHAMATRICULA",
    "RUT",
    "NOMBRE",
    "FECHANACIMIENTO",
    "NOMBRES",
    "APELLIDO PATERNO",
    "APELLIDO MATERNO",
    "ESTADOACADEMICO",
    "SITUACION",
    "MATRICULA",
]


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value).strip()
    if text.lower() in {"nan", "none", "<na>", "nat"}:
        return ""
    return text


def strip_excel_decimal(value: Any) -> str:
    text = clean(value)
    if re.fullmatch(r"\d+\.0", text):
        return text[:-2]
    return text


def unaccent(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", clean(text))
        if unicodedata.category(char) != "Mn"
    )


def canon_text(value: Any) -> str:
    text = unaccent(clean(value)).upper()
    text = re.sub(r"[^A-Z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(*parts: Any) -> set[str]:
    out: set[str] = set()
    for part in parts:
        out.update(re.findall(r"[A-Z0-9]+", canon_text(part)))
    return {tok for tok in out if tok}


def normalize_doc(value: Any) -> str:
    text = strip_excel_decimal(value).upper()
    if "-" in text:
        text = text.split("-", 1)[0]
    text = re.sub(r"[^0-9A-Z]+", "", text)
    return text


def normalize_rut_full(value: Any) -> str:
    return re.sub(r"[^0-9K]+", "", strip_excel_decimal(value).upper())


def rut_dv(value: Any) -> str:
    text = strip_excel_decimal(value).upper()
    if "-" in text:
        return re.sub(r"[^0-9K]+", "", text.split("-", 1)[1])
    full = normalize_rut_full(value)
    if len(full) >= 2 and full[-1] in "0123456789K":
        return full[-1]
    return ""


def normalize_code(value: Any) -> str:
    return re.sub(r"\s+", "", strip_excel_decimal(value).upper())


def normalize_date(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    text = text.split(" ")[0]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    match = re.match(r"(\d{2})-(\d{2})-(\d{4})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return text


def date_year(value: Any) -> str:
    date = normalize_date(value)
    match = re.match(r"\d{2}-\d{2}-(\d{4})", date)
    return match.group(1) if match else ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(df: pd.DataFrame, path: Path, sep: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, sep=sep, quoting=csv.QUOTE_MINIMAL)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False).fillna("")


def read_table(path: Path, sep: str | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    if sep:
        return pd.read_csv(path, dtype=str, sep=sep, keep_default_na=False).fillna("")
    return pd.read_csv(path, dtype=str, sep=None, engine="python", keep_default_na=False).fillna("")


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            data = df.copy()
            if data.empty:
                data = pd.DataFrame({"SIN_DATOS": [""]})
            data.to_excel(writer, index=False, sheet_name=name[:31])
    wb = load_workbook(path)
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = fill
            cell.font = font
        for col in ws.columns:
            max_width = 10
            for cell in list(col)[:120]:
                max_width = max(max_width, len(clean(cell.value)) + 2)
            ws.column_dimensions[col[0].column_letter].width = min(max_width, 60)
    wb.save(path)


def conflict_mask(df: pd.DataFrame) -> pd.Series:
    if "CONFLICTO" not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    return ~df["CONFLICTO"].map(clean).isin(["", "NO"])


def phase06_metrics(matriz: pd.DataFrame, cruce: pd.DataFrame, contradicciones_pendientes: int = 0, contradicciones_aceptadas: int = 0) -> dict[str, int]:
    pending_mask = (matriz["VIGENCIA_FINAL"].map(clean).eq("")) | (matriz["REQUIERE_REVISION"].map(clean).eq("SI"))
    duplicate_ids = int(matriz["ID_REGISTRO"].duplicated(keep=False).sum()) if "ID_REGISTRO" in matriz.columns else 0
    return {
        "registros_precarga": int(len(matriz)),
        "filas_matriz": int(len(matriz)),
        "vigencia_0": int(matriz["VIGENCIA_FINAL"].map(clean).eq("0").sum()),
        "vigencia_1": int(matriz["VIGENCIA_FINAL"].map(clean).eq("1").sum()),
        "vigencia_fuera_dominio": int((~matriz["VIGENCIA_FINAL"].map(clean).isin(["0", "1"])).sum()),
        "pendientes": int(matriz[pending_mask]["ID_REGISTRO"].nunique()),
        "pendientes_marcaciones": int(matriz["VIGENCIA_FINAL"].map(clean).eq("").sum() + matriz["REQUIERE_REVISION"].map(clean).eq("SI").sum()),
        "pendientes_unicos": int(matriz[pending_mask]["ID_REGISTRO"].nunique()),
        "conflictos": int(conflict_mask(matriz).sum()),
        "id_registro_duplicados": duplicate_ids,
        "codigo_unico_vacio": int(matriz["CODIGO_UNICO"].map(clean).eq("").sum()) if "CODIGO_UNICO" in matriz.columns else 0,
        "contradicciones": int(contradicciones_pendientes),
        "contradicciones_materiales_aceptadas": int(contradicciones_aceptadas),
        "coincidencias_unicas": int(cruce["CLASIFICACION"].eq("COINCIDENCIA_UNICA_PERSONA_CARRERA").sum()) if "CLASIFICACION" in cruce.columns else 0,
        "multicodcli": int(cruce["CLASIFICACION"].eq("COINCIDENCIA_PERSONA_MULTICODCLI").sum()) if "CLASIFICACION" in cruce.columns else 0,
        "multicarrera": int(cruce["CLASIFICACION"].eq("COINCIDENCIA_PERSONA_MULTICARRERA").sum()) if "CLASIFICACION" in cruce.columns else 0,
        "solo_precarga": int(cruce["CLASIFICACION"].eq("SOLO_PRECARGA").sum()) if "CLASIFICACION" in cruce.columns else 0,
        "solo_hoja2": 0,
        "documental_sin_carrera": int(cruce["CLASIFICACION"].eq("COINCIDENCIA_DOCUMENTAL_SIN_CARRERA").sum()) if "CLASIFICACION" in cruce.columns else 0,
        "conflicto_carrera": int(cruce["CLASIFICACION"].eq("CONFLICTO_CARRERA").sum()) if "CLASIFICACION" in cruce.columns else 0,
        "conflicto_identidad": int(cruce["CLASIFICACION"].eq("CONFLICTO_IDENTIDAD").sum()) if "CLASIFICACION" in cruce.columns else 0,
    }


def ensure_run_dirs(run_dir: Path) -> dict[str, Path]:
    mapping = {
        "control": run_dir / "00_CONTROL",
        "precarga": run_dir / "02_PRECARGA",
        "academica": run_dir / "03_BASE_ACADEMICA",
        "conciliacion": run_dir / "04_CONCILIACION",
        "vigencia": run_dir / "05_VIGENCIA",
        "codigo": run_dir / "06_CODIGO_UNICO",
        "incorporaciones": run_dir / "07_INCORPORACIONES",
        "matriz": run_dir / "08_MATRIZ_FINAL",
        "pes": run_dir / "09_PES",
        "validacion": run_dir / "10_VALIDACION",
        "reportes": run_dir / "11_REPORTES",
        "hashes": run_dir / "12_HASHES",
        "git": run_dir / "13_GIT",
    }
    for path in mapping.values():
        path.mkdir(parents=True, exist_ok=True)
    return mapping


def column_role(column: str) -> tuple[str, str]:
    c = canon_text(column)
    if c in {"CODCLI"}:
        return "IDENTIDAD", "CODCLI"
    if c == "RUT":
        return "IDENTIDAD", "RUT / NUM_DOCUMENTO / DV"
    if c in {"NOMBRE", "NOMBRES", "APELLIDO PATERNO", "APELLIDO MATERNO"}:
        return "IDENTIDAD", ""
    if c in {"CODCARPR", "CODIGOCARRERA", "NOMBRE L"}:
        return "CARRERA", "CODCARR" if c in {"CODCARPR", "CODIGOCARRERA"} else ""
    if c in {"ANOMATRICULA", "PERIODOMATRICULA", "FECHAMATRICULA", "MATRICULA", "CON FIRMA"}:
        return "MATRICULA_2025", c
    if c in {"ESTADOACADEMICO"}:
        return "ESTADO_ACADEMICO", "ESTADOACADEMICO"
    if c in {"SITUACION"}:
        return "SITUACION", "SITUACION"
    if "FECHA" in c or c in {"ANOINGRESO", "PERIODOINGRESO", "NIVEL"}:
        return "FECHA", c
    if c in {"NUMERO", "RUT EJECUTIVO", "NOMBRE EJECUTIVO"}:
        return "CONTROL", ""
    if c in {"SEDE", "JORNADA", "MODALIDAD", "DESCRIPCION"}:
        return "CARRERA", ""
    if "VIGENCIA" in c or "CIERRE" in c or "ACTIVO" in c:
        return "VIGENCIA_INSTITUCIONAL", ""
    return "OTRO", ""


def hoja2_inventory(df: pd.DataFrame, base_path: Path, sheet_name: str, hash_value: str) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    rows = []
    for column in df.columns:
        series = df[column].map(clean)
        non_empty = int(series.ne("").sum())
        empty = int(series.eq("").sum())
        duplicated_non_empty = int(series[series.ne("")].duplicated(keep=False).sum())
        examples = [value for value in series[series.ne("")].head(5).tolist()]
        role, equivalent = column_role(column)
        rows.append({
            "COLUMNA": column,
            "TIPO_DATO_PANDAS": str(df[column].dtype),
            "FILAS": len(df),
            "NO_VACIOS": non_empty,
            "VACIOS": empty,
            "UNICOS_NO_VACIOS": int(series[series.ne("")].nunique()),
            "DUPLICADOS_NO_VACIOS": duplicated_non_empty,
            "CLASIFICACION_DETECTADA": role,
            "CAMPO_EQUIVALENTE": equivalent,
            "EJEMPLOS": " | ".join(examples),
        })
    inventory = pd.DataFrame(rows)
    structure = {
        "fuente": str(base_path),
        "hoja": sheet_name,
        "sha256": hash_value,
        "fecha_lectura": now(),
        "filas": int(len(df)),
        "columnas": int(len(df.columns)),
        "encabezados": [str(c) for c in df.columns],
        "tipos_datos": {str(c): str(df[c].dtype) for c in df.columns},
        "vacios_por_columna": {str(c): int(df[c].map(clean).eq("").sum()) for c in df.columns},
        "duplicados": {
            "CODCLI": int(df["CODCLI"].map(normalize_code).duplicated(keep=False).sum()) if "CODCLI" in df.columns else None,
            "RUT": int(df["RUT"].map(normalize_rut_full).duplicated(keep=False).sum()) if "RUT" in df.columns else None,
            "DOCUMENTO": int(df["RUT"].map(normalize_doc).duplicated(keep=False).sum()) if "RUT" in df.columns else None,
            "PERSONA_CARRERA": None,
        },
        "campos_materiales_detectados": {
            "documentos": [c for c in df.columns if column_role(c)[1] in {"RUT / NUM_DOCUMENTO / DV"}],
            "CODCLI": ["CODCLI"] if "CODCLI" in df.columns else [],
            "carrera": [c for c in df.columns if column_role(c)[0] == "CARRERA"],
            "estado": ["ESTADOACADEMICO"] if "ESTADOACADEMICO" in df.columns else [],
            "situacion": ["SITUACION"] if "SITUACION" in df.columns else [],
            "fecha_periodo": [c for c in df.columns if column_role(c)[0] in {"FECHA", "MATRICULA_2025"}],
            "vigencia_cierre": [c for c in df.columns if column_role(c)[0] == "VIGENCIA_INSTITUCIONAL"],
        },
    }
    dictionary_rows = []
    for column in df.columns:
        role, equivalent = column_role(column)
        certainty = "ALTA"
        note = ""
        if role == "OTRO":
            certainty = "MEDIA"
        if column == "RUT":
            note = "Contiene cuerpo de documento y DV cuando aplica; se deriva NUM_DOCUMENTO y DV para cruce."
        if column == "CODCARPR":
            note = "Carrera/programa institucional."
        if column == "CODIGOCARRERA":
            note = "Replica operacional de CODCARPR en Hoja2."
        dictionary_rows.append({
            "COLUMNA_HOJA2": column,
            "CLASIFICACION": role,
            "CAMPO_EQUIVALENTE_CONFIRMADO": equivalent,
            "CERTEZA": certainty,
            "OBSERVACION": note,
        })
    dictionary_rows.extend([
        {
            "COLUMNA_HOJA2": "RUT",
            "CLASIFICACION": "IDENTIDAD",
            "CAMPO_EQUIVALENTE_CONFIRMADO": "NUM_DOCUMENTO (derivado desde cuerpo de RUT)",
            "CERTEZA": "ALTA",
            "OBSERVACION": "Derivacion usada solo para cruce; no reemplaza valor original.",
        },
        {
            "COLUMNA_HOJA2": "RUT",
            "CLASIFICACION": "IDENTIDAD",
            "CAMPO_EQUIVALENTE_CONFIRMADO": "DV (derivado desde sufijo de RUT)",
            "CERTEZA": "ALTA",
            "OBSERVACION": "Derivacion usada solo para cruce; no reemplaza valor original.",
        },
        {
            "COLUMNA_HOJA2": "CODCARPR + ANOINGRESO + PERIODOINGRESO",
            "CLASIFICACION": "CARRERA",
            "CAMPO_EQUIVALENTE_CONFIRMADO": "PLAN_DE_ESTUDIO (derivado)",
            "CERTEZA": "MEDIA",
            "OBSERVACION": "Se deriva para trazabilidad de cruce; Hoja2 no contiene columna PLAN_DE_ESTUDIO directa.",
        },
        {
            "COLUMNA_HOJA2": "NO_EXISTE_COLUMNA_DIRECTA",
            "CLASIFICACION": "CONTROL",
            "CAMPO_EQUIVALENTE_CONFIRMADO": "CODIGO_UNICO",
            "CERTEZA": "ALTA",
            "OBSERVACION": "Hoja2 no trae CODIGO_UNICO; se usa CODIGO_UNICO de precarga y puente/oferta solo como lectura.",
        },
        {
            "COLUMNA_HOJA2": "ESTADOACADEMICO + SITUACION + MATRICULA",
            "CLASIFICACION": "VIGENCIA_INSTITUCIONAL",
            "CAMPO_EQUIVALENTE_CONFIRMADO": "Indicadores de cierre, no equivalentes automaticos a VIGENCIA SIES",
            "CERTEZA": "ALTA",
            "OBSERVACION": "No se interpreta ninguna columna como VIGENCIA SIES directa.",
        },
    ])
    dictionary = pd.DataFrame(dictionary_rows)
    return inventory, structure, dictionary


def normalize_hoja2(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["RUT_VALOR_ORIGINAL"] = out.get("RUT", "").map(clean) if "RUT" in out.columns else ""
    out["RUT_NORMALIZADO"] = out["RUT_VALOR_ORIGINAL"].map(normalize_rut_full)
    out["NUM_DOCUMENTO_VALOR_ORIGINAL"] = out["RUT_VALOR_ORIGINAL"]
    out["NUM_DOCUMENTO_NORMALIZADO"] = out["RUT_VALOR_ORIGINAL"].map(normalize_doc)
    out["DV_VALOR_ORIGINAL"] = out["RUT_VALOR_ORIGINAL"]
    out["DV_NORMALIZADO"] = out["RUT_VALOR_ORIGINAL"].map(rut_dv)
    out["CODCLI_VALOR_ORIGINAL"] = out.get("CODCLI", "").map(clean) if "CODCLI" in out.columns else ""
    out["CODCLI_NORMALIZADO"] = out["CODCLI_VALOR_ORIGINAL"].map(normalize_code)
    out["CODCARR_VALOR_ORIGINAL"] = out.get("CODCARPR", "").map(clean) if "CODCARPR" in out.columns else ""
    out["CODCARR_NORMALIZADO"] = out["CODCARR_VALOR_ORIGINAL"].map(normalize_code)
    out["CODIGO_UNICO_VALOR_ORIGINAL"] = ""
    out["CODIGO_UNICO_NORMALIZADO"] = ""
    out["ESTADOACADEMICO_VALOR_ORIGINAL"] = out.get("ESTADOACADEMICO", "").map(clean) if "ESTADOACADEMICO" in out.columns else ""
    out["ESTADOACADEMICO_NORMALIZADO"] = out["ESTADOACADEMICO_VALOR_ORIGINAL"].map(canon_text)
    out["SITUACION_VALOR_ORIGINAL"] = out.get("SITUACION", "").map(clean) if "SITUACION" in out.columns else ""
    out["SITUACION_NORMALIZADA"] = out["SITUACION_VALOR_ORIGINAL"].map(canon_text)
    out["FECHAMATRICULA_NORMALIZADA"] = out.get("FECHAMATRICULA", "").map(normalize_date) if "FECHAMATRICULA" in out.columns else ""
    out["FECHANACIMIENTO_NORMALIZADA"] = out.get("FECHANACIMIENTO", "").map(normalize_date) if "FECHANACIMIENTO" in out.columns else ""
    out["ANOMATRICULA_NORMALIZADA"] = out.get("ANOMATRICULA", "").map(strip_excel_decimal) if "ANOMATRICULA" in out.columns else ""
    out["PERIODOMATRICULA_NORMALIZADO"] = out.get("PERIODOMATRICULA", "").map(strip_excel_decimal) if "PERIODOMATRICULA" in out.columns else ""
    out["ANOINGRESO_NORMALIZADO"] = out.get("ANOINGRESO", "").map(strip_excel_decimal) if "ANOINGRESO" in out.columns else ""
    out["PERIODOINGRESO_NORMALIZADO"] = out.get("PERIODOINGRESO", "").map(strip_excel_decimal) if "PERIODOINGRESO" in out.columns else ""
    out["PLAN_DE_ESTUDIO_DERIVADO"] = out.apply(
        lambda row: f"{row['CODCARR_NORMALIZADO']}{row['ANOINGRESO_NORMALIZADO']}{row['PERIODOINGRESO_NORMALIZADO']}"
        if row["CODCARR_NORMALIZADO"] and row["ANOINGRESO_NORMALIZADO"] and row["PERIODOINGRESO_NORMALIZADO"] else "",
        axis=1,
    )
    out["IDENTIDAD_TOKEN_NORMALIZADA"] = out.apply(
        lambda row: " ".join(sorted(tokens(
            row.get("NOMBRES", ""),
            row.get("APELLIDO PATERNO", ""),
            row.get("APELLIDO MATERNO", ""),
        ))),
        axis=1,
    )
    out["IDENTIDAD_TOKEN_AMPLIADA_NORMALIZADA"] = out.apply(
        lambda row: " ".join(sorted(tokens(
            row.get("NOMBRE", ""),
            row.get("NOMBRES", ""),
            row.get("APELLIDO PATERNO", ""),
            row.get("APELLIDO MATERNO", ""),
        ))),
        axis=1,
    )
    out["FILA_HOJA2"] = [idx + 2 for idx in range(len(out))]
    return out


def load_code_maps() -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, str]]:
    code_to_carr: dict[str, set[str]] = defaultdict(set)
    code_to_plan: dict[str, set[str]] = defaultdict(set)
    code_to_name: dict[str, str] = {}
    bridge_path = BRIDGE_V2 if BRIDGE_V2.exists() else BRIDGE_V1
    bridge = read_table(bridge_path, sep="\t") if bridge_path.exists() else pd.DataFrame()
    if not bridge.empty:
        for _, row in bridge.iterrows():
            code = normalize_code(row.get("CODIGO_UNICO", ""))
            if not code:
                continue
            carr = normalize_code(row.get("CODCARPR", ""))
            plan = normalize_code(row.get("PLAN_DE_ESTUDIO", ""))
            name = clean(row.get("NOMBRE_CARRERA", ""))
            if carr:
                code_to_carr[code].add(carr)
            if plan:
                code_to_plan[code].add(plan)
            if name and code not in code_to_name:
                code_to_name[code] = name
    dur = read_table(DURACION, sep="\t") if DURACION.exists() else pd.DataFrame()
    if not dur.empty:
        for _, row in dur.iterrows():
            code = normalize_code(row.get("CODIGO_UNICO", ""))
            if not code:
                continue
            carr = normalize_code(row.get("CODCARPR_CANONICO", ""))
            aliases = [normalize_code(x) for x in clean(row.get("CODCARPR_ALIAS_LIST", "")).split("|")]
            if carr:
                code_to_carr[code].add(carr)
            for alias in aliases:
                if alias and alias != "NAN":
                    code_to_carr[code].add(alias)
            if row.get("NOMBRE_CARRERA", "") and code not in code_to_name:
                code_to_name[code] = clean(row.get("NOMBRE_CARRERA", ""))
    return dict(code_to_carr), dict(code_to_plan), code_to_name


def add_req_code_maps(
    req: pd.DataFrame,
    code_to_carr: dict[str, set[str]],
    code_to_plan: dict[str, set[str]],
) -> None:
    if req.empty:
        return
    for _, row in req.iterrows():
        code = normalize_code(row.get("CODIGO_UNICO_PRECARGA", ""))
        carr = normalize_code(row.get("CODCARR_RESUELTA", ""))
        plan = normalize_code(row.get("PLAN_RESUELTO", ""))
        if code and carr:
            code_to_carr.setdefault(code, set()).add(carr)
        if code and plan:
            code_to_plan.setdefault(code, set()).add(plan)


def previous_decision_map(decision: pd.DataFrame) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for _, row in decision.iterrows():
        out[clean(row.get("ID_REGISTRO", ""))] = {k: clean(v) for k, v in row.to_dict().items()}
    return out


def req_map(req: pd.DataFrame) -> dict[str, dict[str, str]]:
    return {clean(row.get("ID_REGISTRO", "")): {k: clean(v) for k, v in row.to_dict().items()} for _, row in req.iterrows()}


def precarga_identity(row: pd.Series) -> tuple[str, str, set[str], set[str], set[str]]:
    dob = normalize_date(row.get("FECHA_NACIMIENTO", ""))
    name_tokens = tokens(row.get("NOMBRES", ""), row.get("PRIMER_APELLIDO", ""), row.get("SEGUNDO_APELLIDO", ""))
    surname_tokens = tokens(row.get("PRIMER_APELLIDO", ""), row.get("SEGUNDO_APELLIDO", ""))
    given_tokens = tokens(row.get("NOMBRES", ""))
    return (
        normalize_doc(row.get("NUM_DOCUMENTO", "")),
        dob,
        name_tokens,
        surname_tokens,
        given_tokens,
    )


def identity_score(prec_row: pd.Series, hoja_row: pd.Series) -> tuple[float, bool, bool, bool]:
    _, dob, name_tokens, surname_tokens, given_tokens = precarga_identity(prec_row)
    hoja_dob = clean(hoja_row.get("FECHANACIMIENTO_NORMALIZADA", ""))
    hoja_tokens = set(clean(hoja_row.get("IDENTIDAD_TOKEN_AMPLIADA_NORMALIZADA", "")).split())
    if not name_tokens:
        return 0.0, False, False, False
    intersection = name_tokens & hoja_tokens
    score = len(intersection) / max(len(name_tokens), 1)
    same_dob = bool(dob and hoja_dob and dob == hoja_dob)
    surname_ok = bool(surname_tokens) and surname_tokens <= hoja_tokens
    given_ok = bool(given_tokens & hoja_tokens)
    return score, same_dob, surname_ok, given_ok


def strong_identity(prec_row: pd.Series, hoja_row: pd.Series) -> bool:
    score, same_dob, surname_ok, given_ok = identity_score(prec_row, hoja_row)
    return same_dob and (score >= 0.80 or (surname_ok and given_ok))


def expected_for_row(
    prec_row: pd.Series,
    req_by_id: dict[str, dict[str, str]],
    code_to_carr: dict[str, set[str]],
    code_to_plan: dict[str, set[str]],
) -> tuple[set[str], set[str]]:
    code = normalize_code(prec_row.get("CODIGO_UNICO", ""))
    id_reg = clean(prec_row.get("ID_REGISTRO", ""))
    carrs = set(code_to_carr.get(code, set()))
    plans = set(code_to_plan.get(code, set()))
    req_row = req_by_id.get(id_reg, {})
    carr = normalize_code(req_row.get("CODCARR_RESUELTA", ""))
    plan = normalize_code(req_row.get("PLAN_RESUELTO", ""))
    if carr:
        carrs.add(carr)
    if plan:
        plans.add(plan)
    return {x for x in carrs if x}, {x for x in plans if x}


def row_rule_zero(row: pd.Series) -> tuple[bool, str]:
    estado = canon_text(row.get("ESTADOACADEMICO", ""))
    situacion = canon_text(row.get("SITUACION", ""))
    for (estado_rule, situacion_rule), rule_name in REGLAS_CERO.items():
        if estado == canon_text(estado_rule) and situacion == canon_text(situacion_rule):
            return True, rule_name
    return False, ""


def activity_flags(hoja_row: pd.Series | None, previous_row: dict[str, str] | None = None) -> tuple[str, str, str]:
    tuvo_matricula = "NO"
    tuvo_actividad = "NO"
    if hoja_row is not None:
        anomat = strip_excel_decimal(hoja_row.get("ANOMATRICULA", ""))
        fecha_year = date_year(hoja_row.get("FECHAMATRICULA", ""))
        if anomat == "2025" or fecha_year == "2025":
            tuvo_matricula = "SI"
    if previous_row:
        resumen = clean(previous_row.get("RESUMEN_AVANCE_2025", ""))
        evidence = " ".join([
            resumen,
            clean(previous_row.get("EVIDENCIA_PRINCIPAL", "")),
            clean(previous_row.get("FUENTE", "")),
        ])
        if re.search(r"HOJA1_FILAS_2025=[1-9]", evidence) or "DATOS_ALUMNOS_ANOMATRICULA_2025" in evidence:
            tuvo_actividad = "SI"
            tuvo_matricula = "SI"
    return tuvo_matricula, tuvo_actividad, "EVIDENCIA_2025" if (tuvo_matricula == "SI" or tuvo_actividad == "SI") else "SIN_EVIDENCIA_2025_DIRECTA"


def select_candidates(
    prec_row: pd.Series,
    hoja_norm: pd.DataFrame,
    previous_row: dict[str, str],
    req_row: dict[str, str],
    expected_carr: set[str],
    expected_plans: set[str],
) -> dict[str, Any]:
    doc_body, _, _, _, _ = precarga_identity(prec_row)
    rut_full = normalize_rut_full(f"{clean(prec_row.get('NUM_DOCUMENTO', ''))}{clean(prec_row.get('DV', ''))}")
    codcli_candidates: set[str] = set()
    for source in [
        previous_row.get("CODCLI", ""),
        req_row.get("CODCLI_CONFIRMADO", ""),
        req_row.get("CODCLI_RESUELTO", ""),
        req_row.get("CODCLI_HOJA2", ""),
    ]:
        for item in re.split(r"[|,; ]+", clean(source)):
            item = normalize_code(item)
            if item:
                codcli_candidates.add(item)
    # Also harvest CODCLI mentions from prior evidence text, but only as a lower-priority trace.
    evidence_text = " ".join(clean(req_row.get(k, "")) for k in req_row)
    for item in re.findall(r"20\d{3}[A-Z]+[0-9]+", evidence_text):
        codcli_candidates.add(normalize_code(item))

    doc_matches = hoja_norm[hoja_norm["NUM_DOCUMENTO_NORMALIZADO"].eq(doc_body)] if doc_body else hoja_norm.iloc[0:0]
    rut_matches = hoja_norm[hoja_norm["RUT_NORMALIZADO"].eq(rut_full)] if rut_full else hoja_norm.iloc[0:0]
    codcli_matches = hoja_norm[hoja_norm["CODCLI_NORMALIZADO"].isin(codcli_candidates)] if codcli_candidates else hoja_norm.iloc[0:0]

    identity_mask = hoja_norm.apply(lambda row: strong_identity(prec_row, row), axis=1)
    identity_matches = hoja_norm[identity_mask]

    identity_carrera = identity_matches[identity_matches["CODCARR_NORMALIZADO"].isin(expected_carr)] if expected_carr else identity_matches.iloc[0:0]
    doc_carrera = doc_matches[doc_matches["CODCARR_NORMALIZADO"].isin(expected_carr)] if expected_carr else doc_matches.iloc[0:0]
    codcli_carrera = codcli_matches[codcli_matches["CODCARR_NORMALIZADO"].isin(expected_carr)] if expected_carr else codcli_matches.iloc[0:0]
    identity_plan = identity_matches[identity_matches["PLAN_DE_ESTUDIO_DERIVADO"].isin(expected_plans)] if expected_plans else identity_matches.iloc[0:0]
    identity_2025 = identity_matches[
        identity_matches["ANOMATRICULA_NORMALIZADA"].eq("2025")
        | identity_matches["FECHAMATRICULA_NORMALIZADA"].str.endswith("-2025", na=False)
    ]

    priority_sets = [
        ("NUM_DOCUMENTO exacto normalizado + carrera", doc_carrera),
        ("RUT exacto normalizado + carrera", rut_matches[rut_matches["CODCARR_NORMALIZADO"].isin(expected_carr)] if expected_carr else rut_matches.iloc[0:0]),
        ("CODCLI exacto", codcli_matches),
        ("Persona + carrera", identity_carrera),
        ("Persona + plan", identity_plan),
        ("Persona + anio matricula 2025", identity_2025),
        ("NUM_DOCUMENTO exacto normalizado", doc_matches),
        ("Persona exacta ampliada", identity_matches),
    ]
    selected_source = ""
    selected = pd.DataFrame()
    for name, candidate_df in priority_sets:
        if not candidate_df.empty:
            selected_source = name
            selected = candidate_df.copy()
            break

    all_person_rows = pd.concat([doc_matches, identity_matches, codcli_matches], ignore_index=True).drop_duplicates(subset=["FILA_HOJA2"])
    carreras = sorted({clean(x) for x in all_person_rows.get("CODCARR_NORMALIZADO", pd.Series(dtype=str)).tolist() if clean(x)})
    codclis = sorted({clean(x) for x in all_person_rows.get("CODCLI_NORMALIZADO", pd.Series(dtype=str)).tolist() if clean(x)})

    selected_unique = selected.drop_duplicates(subset=["FILA_HOJA2"]) if not selected.empty else selected
    classification = "SOLO_PRECARGA"
    conflict = ""
    if selected_unique.empty:
        if not doc_matches.empty or not identity_matches.empty:
            classification = "COINCIDENCIA_DOCUMENTAL_SIN_CARRERA"
            if expected_carr and not set(carreras).intersection(expected_carr):
                conflict = "CONFLICTO_CARRERA"
        else:
            classification = "SOLO_PRECARGA"
    else:
        selected_carrs = set(selected_unique["CODCARR_NORMALIZADO"].map(clean)) - {""}
        if len(codclis) > 1:
            classification = "COINCIDENCIA_PERSONA_MULTICODCLI"
        elif len(carreras) > 1:
            classification = "COINCIDENCIA_PERSONA_MULTICARRERA"
        elif expected_carr and not (selected_carrs & expected_carr) and "CODCLI exacto" not in selected_source:
            classification = "CONFLICTO_CARRERA"
            conflict = "CONFLICTO_CARRERA"
        elif selected_source in {"NUM_DOCUMENTO exacto normalizado", "Persona exacta ampliada"} and expected_carr and not (selected_carrs & expected_carr):
            classification = "COINCIDENCIA_DOCUMENTAL_SIN_CARRERA"
        else:
            classification = "COINCIDENCIA_UNICA_PERSONA_CARRERA"

    # Prefer a row in the expected career. Then prefer explicit zero evidence over generic active rows,
    # because Fase 06 is deciding the precarga row, not the student's other career.
    selected_row = None
    if not selected_unique.empty:
        ranked = []
        for _, row in selected_unique.iterrows():
            is_zero, _ = row_rule_zero(row)
            score = 0
            if clean(row.get("CODCARR_NORMALIZADO", "")) in expected_carr:
                score += 100
            if clean(row.get("PLAN_DE_ESTUDIO_DERIVADO", "")) in expected_plans:
                score += 30
            if is_zero:
                score += 20
            if strip_excel_decimal(row.get("ANOMATRICULA", "")) == "2025":
                score += 10
            if date_year(row.get("FECHAMATRICULA", "")) == "2025":
                score += 5
            ranked.append((score, int(row.get("FILA_HOJA2", 0)), row))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        selected_row = ranked[0][2]

    return {
        "selected": selected_row,
        "selected_source": selected_source,
        "classification": classification,
        "conflict": conflict,
        "all_person_rows": all_person_rows,
        "doc_matches": doc_matches,
        "identity_matches": identity_matches,
        "codcli_matches": codcli_matches,
        "codcli_candidates": codcli_candidates,
        "carreras_persona": carreras,
        "codcli_persona": codclis,
        "expected_carr": expected_carr,
        "expected_plans": expected_plans,
    }


def propose_vigencia(
    prec_row: pd.Series,
    match_info: dict[str, Any],
    previous_row: dict[str, str] | None,
    is_pending: bool,
) -> dict[str, str]:
    selected = match_info.get("selected")
    classification = match_info.get("classification", "")
    conflict = clean(match_info.get("conflict", ""))
    if selected is None:
        return {
            "VIGENCIA_PROPUESTA": "",
            "REGLA_APLICADA": "",
            "CONFIANZA": "BAJA" if is_pending else "MEDIA",
            "REQUIERE_REVISION": "SI" if is_pending else "NO",
            "OBSERVACION": "Hoja2 no aporta evidencia adicional suficiente para la relacion persona-carrera.",
            "CONFLICTO": conflict,
        }
    is_zero, zero_rule = row_rule_zero(selected)
    mat, act, evidence_flag = activity_flags(selected, previous_row)
    if is_zero:
        return {
            "VIGENCIA_PROPUESTA": "0",
            "REGLA_APLICADA": zero_rule,
            "CONFIANZA": "ALTA" if not conflict else "MEDIA",
            "REQUIERE_REVISION": "NO" if not conflict else "SI",
            "OBSERVACION": "Hoja2 contiene estado/situacion institucional de vigencia 0 para la relacion seleccionada.",
            "CONFLICTO": conflict,
        }
    if conflict:
        return {
            "VIGENCIA_PROPUESTA": "",
            "REGLA_APLICADA": "",
            "CONFIANZA": "BAJA",
            "REQUIERE_REVISION": "SI",
            "OBSERVACION": "Existe evidencia de persona, pero la carrera/plan de Hoja2 no demuestra suficientemente la relacion de precarga.",
            "CONFLICTO": conflict,
        }
    if classification in {"COINCIDENCIA_UNICA_PERSONA_CARRERA", "COINCIDENCIA_PERSONA_MULTICARRERA", "COINCIDENCIA_PERSONA_MULTICODCLI"} and (mat == "SI" or act == "SI"):
        return {
            "VIGENCIA_PROPUESTA": "1",
            "REGLA_APLICADA": "EVIDENCIA_MATRICULA_O_ACTIVIDAD_2025_SIN_REGLA_CERO",
            "CONFIANZA": "ALTA",
            "REQUIERE_REVISION": "NO",
            "OBSERVACION": "Hoja2 o evidencia previa demuestra matricula/actividad 2025 y no cae en regla explicita de vigencia 0.",
            "CONFLICTO": "",
        }
    if not is_pending and previous_row and clean(previous_row.get("VIGENCIA_PROPUESTA", "")) in {"0", "1"}:
        return {
            "VIGENCIA_PROPUESTA": clean(previous_row.get("VIGENCIA_PROPUESTA", "")),
            "REGLA_APLICADA": clean(previous_row.get("REGLA_APLICADA", "")) or "DECISION_PREVIA_SIN_CONTRADICCION_HOJA2",
            "CONFIANZA": "MEDIA",
            "REQUIERE_REVISION": "NO",
            "OBSERVACION": "Hoja2 no contradice materialmente la decision previa, pero no agrega evidencia 2025 directa.",
            "CONFLICTO": "",
        }
    return {
        "VIGENCIA_PROPUESTA": "",
        "REGLA_APLICADA": "",
        "CONFIANZA": "BAJA",
        "REQUIERE_REVISION": "SI",
        "OBSERVACION": "No se puede asignar 1 sin evidencia 2025 ni 0 sin regla institucional explicita o relacion erronea demostrada.",
        "CONFLICTO": conflict,
    }


def selected_to_fields(selected: pd.Series | None) -> dict[str, str]:
    if selected is None:
        return {
            "CODCLI_HOJA2": "",
            "CODCARR_HOJA2": "",
            "PLAN_HOJA2": "",
            "ESTADOACADEMICO_HOJA2": "",
            "SITUACION_HOJA2": "",
            "FECHA_MATRICULA_HOJA2": "",
            "ANOMATRICULA_HOJA2": "",
            "PERIODO_HOJA2": "",
            "FILA_HOJA2": "",
            "RUT_HOJA2": "",
            "NOMBRE_HOJA2": "",
        }
    return {
        "CODCLI_HOJA2": clean(selected.get("CODCLI", "")),
        "CODCARR_HOJA2": clean(selected.get("CODCARPR", "")),
        "PLAN_HOJA2": clean(selected.get("PLAN_DE_ESTUDIO_DERIVADO", "")),
        "ESTADOACADEMICO_HOJA2": clean(selected.get("ESTADOACADEMICO", "")),
        "SITUACION_HOJA2": clean(selected.get("SITUACION", "")),
        "FECHA_MATRICULA_HOJA2": clean(selected.get("FECHAMATRICULA", "")),
        "ANOMATRICULA_HOJA2": clean(selected.get("ANOMATRICULA", "")),
        "PERIODO_HOJA2": clean(selected.get("PERIODOMATRICULA", "")),
        "FILA_HOJA2": clean(selected.get("FILA_HOJA2", "")),
        "RUT_HOJA2": clean(selected.get("RUT", "")),
        "NOMBRE_HOJA2": clean(selected.get("NOMBRE", "")),
    }


def build_phase_outputs(
    run_dir: Path,
    dirs: dict[str, Path],
    base_path: Path,
    sheet_name: str,
    hoja_norm: pd.DataFrame,
    precarga: pd.DataFrame,
    decision_prev: pd.DataFrame,
    req: pd.DataFrame,
    code_to_carr: dict[str, set[str]],
    code_to_plan: dict[str, set[str]],
) -> dict[str, Any]:
    prev_by_id = previous_decision_map(decision_prev)
    req_by_id = req_map(req)
    pending_ids = set(req_by_id)

    cruce_rows = []
    q_rows = []
    r_rows = []
    matriz_rows = []
    contradiction_rows = []
    pending_after_rows = []

    for _, prec in precarga.iterrows():
        id_reg = clean(prec.get("ID_REGISTRO", ""))
        prev_row = prev_by_id.get(id_reg, {})
        req_row = req_by_id.get(id_reg, {})
        expected_carr, expected_plans = expected_for_row(prec, req_by_id, code_to_carr, code_to_plan)
        info = select_candidates(prec, hoja_norm, prev_row, req_row, expected_carr, expected_plans)
        selected = info.get("selected")
        selected_fields = selected_to_fields(selected)
        is_pending = id_reg in pending_ids
        proposal = propose_vigencia(prec, info, prev_row, is_pending)
        mat, act, evidence_flag = activity_flags(selected, prev_row)
        estado_al_cierre = "SIN_EVIDENCIA_HOJA2"
        if selected is not None:
            estado_al_cierre = f"{clean(selected.get('ESTADOACADEMICO', ''))} | {clean(selected.get('SITUACION', ''))}"

        expected_carr_text = "|".join(sorted(expected_carr))
        expected_plan_text = "|".join(sorted(expected_plans))
        person_rows = info.get("all_person_rows", pd.DataFrame())
        person_summary = ""
        if not person_rows.empty:
            person_summary = " || ".join(
                f"F{clean(row.get('FILA_HOJA2', ''))}:{clean(row.get('CODCLI', ''))}:{clean(row.get('CODCARPR', ''))}:{clean(row.get('ESTADOACADEMICO', ''))}|{clean(row.get('SITUACION', ''))}"
                for _, row in person_rows.sort_values("FILA_HOJA2").head(12).iterrows()
            )

        cruce_rows.append({
            "ID_REGISTRO": id_reg,
            "FILA_PRECARGA": clean(prec.get("FILA_PRECARGA", "")),
            "NUM_DOCUMENTO": clean(prec.get("NUM_DOCUMENTO", "")),
            "DV": clean(prec.get("DV", "")),
            "CODIGO_UNICO_PRECARGA": clean(prec.get("CODIGO_UNICO", "")),
            "CODCARR_ESPERADA": expected_carr_text,
            "PLAN_ESPERADO": expected_plan_text,
            **selected_fields,
            "METODO_PRIORITARIO": clean(info.get("selected_source", "")),
            "CLASIFICACION": clean(info.get("classification", "")),
            "CODCLI_PERSONA_HOJA2": "|".join(info.get("codcli_persona", [])),
            "CARRERAS_PERSONA_HOJA2": "|".join(info.get("carreras_persona", [])),
            "N_MATCH_DOCUMENTO": len(info.get("doc_matches", [])),
            "N_MATCH_IDENTIDAD": len(info.get("identity_matches", [])),
            "N_MATCH_CODCLI": len(info.get("codcli_matches", [])),
            "CONFLICTO": clean(proposal.get("CONFLICTO", "")),
            "EVIDENCIA_HOJA2": person_summary,
        })

        if is_pending:
            q_row = {
                "ID_REGISTRO": id_reg,
                "FILA_PRECARGA": clean(prec.get("FILA_PRECARGA", "")),
                "NUM_DOCUMENTO": clean(prec.get("NUM_DOCUMENTO", "")),
                "CODIGO_UNICO_PRECARGA": clean(prec.get("CODIGO_UNICO", "")),
                **selected_fields,
                "EVIDENCIA_2025": evidence_flag,
                "VIGENCIA_PROPUESTA": clean(proposal.get("VIGENCIA_PROPUESTA", "")),
                "REGLA_APLICADA": clean(proposal.get("REGLA_APLICADA", "")),
                "CONFIANZA": clean(proposal.get("CONFIANZA", "")),
                "REQUIERE_REVISION": clean(proposal.get("REQUIERE_REVISION", "")),
                "OBSERVACION": clean(proposal.get("OBSERVACION", "")),
            }
            q_rows.append(q_row)
            if q_row["REQUIERE_REVISION"] == "SI" or q_row["VIGENCIA_PROPUESTA"] not in {"0", "1"}:
                pending_after_rows.append({
                    **q_row,
                    "MOTIVO_POST_HOJA2": "EVIDENCIA_HOJA2_INSUFICIENTE_O_CONFLICTO",
                    "CLASIFICACION_CRUCE": clean(info.get("classification", "")),
                    "CONFLICTO": clean(proposal.get("CONFLICTO", "")),
                    "EVIDENCIA_HOJA2_DETALLE": person_summary,
                })

        if not is_pending:
            previous_vig = clean(prev_row.get("VIGENCIA_PROPUESTA", ""))
            hoja_vig = clean(proposal.get("VIGENCIA_PROPUESTA", ""))
            validation = "SIN_EVIDENCIA_ADICIONAL"
            if clean(proposal.get("CONFLICTO", "")):
                validation = "REQUIERE_REVISION"
            elif hoja_vig in {"0", "1"} and previous_vig == hoja_vig:
                validation = "CONFIRMA_DECISION_PREVIA"
            elif hoja_vig in {"0", "1"} and previous_vig in {"0", "1"} and previous_vig != hoja_vig:
                validation = "CONTRADICE_DECISION_PREVIA"
            elif selected is not None:
                validation = "DISCREPANCIA_NO_MATERIAL"
            r_row = {
                "ID_REGISTRO": id_reg,
                "FILA_PRECARGA": clean(prec.get("FILA_PRECARGA", "")),
                "NUM_DOCUMENTO": clean(prec.get("NUM_DOCUMENTO", "")),
                "VIGENCIA_ANTERIOR": previous_vig,
                "VIGENCIA_PROPUESTA_HOJA2": hoja_vig,
                "CLASIFICACION_VALIDACION": validation,
                "CAMPO_CONTRADICTORIO": "",
                "VALOR_ANTERIOR": "",
                "VALOR_HOJA2": "",
                "FUENTE_ANTERIOR": clean(prev_row.get("FUENTE", "")),
                "FUENTE_HOJA2": f"{base_path}:Hoja2",
                "DECISION_REQUERIDA": "",
                **selected_fields,
                "REGLA_APLICADA_HOJA2": clean(proposal.get("REGLA_APLICADA", "")),
                "OBSERVACION": clean(proposal.get("OBSERVACION", "")),
            }
            if validation == "CONTRADICE_DECISION_PREVIA":
                r_row.update({
                    "CAMPO_CONTRADICTORIO": "VIGENCIA",
                    "VALOR_ANTERIOR": previous_vig,
                    "VALOR_HOJA2": hoja_vig,
                    "DECISION_REQUERIDA": "CONFIRMAR_MODIFICACION_MATERIAL_ANTES_DE_CONTINUAR",
                })
                contradiction_rows.append(r_row.copy())
            r_rows.append(r_row)

        final_vig = clean(proposal.get("VIGENCIA_PROPUESTA", ""))
        if not is_pending and clean(proposal.get("REQUIERE_REVISION", "")) != "SI":
            # Preserve previous resolved decisions unless Hoja2 produces an explicit contradiction.
            if clean(prev_row.get("VIGENCIA_PROPUESTA", "")) in {"0", "1"} and not any(
                x["ID_REGISTRO"] == id_reg for x in contradiction_rows
            ):
                final_vig = clean(prev_row.get("VIGENCIA_PROPUESTA", ""))
        conflict = clean(proposal.get("CONFLICTO", ""))
        requiere = clean(proposal.get("REQUIERE_REVISION", ""))
        matriz_rows.append({
            "ID_REGISTRO": id_reg,
            "FILA_PRECARGA": clean(prec.get("FILA_PRECARGA", "")),
            "NUM_DOCUMENTO": clean(prec.get("NUM_DOCUMENTO", "")),
            "CODIGO_UNICO": clean(prec.get("CODIGO_UNICO", "")),
            "CODCLI": selected_fields["CODCLI_HOJA2"] or clean(prev_row.get("CODCLI", "")),
            "CODCARR": selected_fields["CODCARR_HOJA2"] or clean(prev_row.get("CODCARR", "")),
            "PLAN_DE_ESTUDIO": selected_fields["PLAN_HOJA2"] or clean(prev_row.get("PLAN_DE_ESTUDIO", "")),
            "ESTADOACADEMICO": selected_fields["ESTADOACADEMICO_HOJA2"] or clean(prev_row.get("ESTADOACADEMICO", "")),
            "SITUACION": selected_fields["SITUACION_HOJA2"] or clean(prev_row.get("SITUACION", "")),
            "TUVO_MATRICULA_2025": mat,
            "TUVO_ACTIVIDAD_2025": act,
            "ESTADO_AL_31_12_2025": estado_al_cierre,
            "CORRESPONDE_MANTENER_EXTRANJEROS_2025": "SI" if final_vig == "1" else ("NO" if final_vig == "0" else ""),
            "VIGENCIA_PRECARGA": clean(prec.get("VIGENCIA", "")),
            "VIGENCIA_PREVIA": clean(prev_row.get("VIGENCIA_PROPUESTA", "")),
            "VIGENCIA_FINAL": final_vig,
            "REGLA_APLICADA": clean(proposal.get("REGLA_APLICADA", "")) or clean(prev_row.get("REGLA_APLICADA", "")),
            "FUENTE_PRINCIPAL": f"{base_path}:Hoja2" if selected is not None else clean(prev_row.get("FUENTE", "")),
            "FUENTES_SECUNDARIAS": clean(prev_row.get("FUENTE", "")),
            "CONFIANZA": clean(proposal.get("CONFIANZA", "")),
            "REQUIERE_REVISION": requiere,
            "CONFLICTO": conflict,
            "OBSERVACION": clean(proposal.get("OBSERVACION", "")),
        })

    cruce = pd.DataFrame(cruce_rows)
    q_df = pd.DataFrame(q_rows)
    r_df = pd.DataFrame(r_rows)
    matriz = pd.DataFrame(matriz_rows)
    contradictions = pd.DataFrame(contradiction_rows)
    pending_after = pd.DataFrame(pending_after_rows)

    write_csv(cruce, dirs["vigencia"] / "06P_CRUCE_PRECARGA_185_VS_HOJA2.csv")
    write_csv(q_df, dirs["vigencia"] / "06Q_RESOLUCION_20_PENDIENTES_CON_HOJA2.csv")
    write_csv(r_df, dirs["vigencia"] / "06R_VALIDACION_165_DECISIONES_PREVIAS.csv")
    if not contradictions.empty:
        write_csv(contradictions, dirs["vigencia"] / "06R_CONTRADICCIONES_DECISIONES_PREVIAS_HOJA2.csv")
    else:
        write_csv(pd.DataFrame(columns=[
            "ID_REGISTRO",
            "VIGENCIA_ANTERIOR",
            "VIGENCIA_PROPUESTA_HOJA2",
            "CAMPO_CONTRADICTORIO",
            "VALOR_ANTERIOR",
            "VALOR_HOJA2",
            "FUENTE_ANTERIOR",
            "FUENTE_HOJA2",
            "DECISION_REQUERIDA",
        ]), dirs["vigencia"] / "06R_CONTRADICCIONES_DECISIONES_PREVIAS_HOJA2.csv")

    # 06S/06T rule and cutoff controls are explicit in the final matrix and these summaries.
    rules_summary = pd.DataFrame([
        {"REGLA": f"{estado} | {situacion}", "VIGENCIA": "0", "REGLA_APLICADA": rule}
        for (estado, situacion), rule in REGLAS_CERO.items()
    ] + [
        {
            "REGLA": "Mantener cuando hay matricula o actividad 2025, persona-carrera corresponde, sin regla cero ni conflicto",
            "VIGENCIA": "1",
            "REGLA_APLICADA": "EVIDENCIA_MATRICULA_O_ACTIVIDAD_2025_SIN_REGLA_CERO",
        },
        {
            "REGLA": "No asignar 0 por ausencia en Hoja2, ausencia de CODCLI, solo precarga, falta de actividad o no continuidad 2026",
            "VIGENCIA": "NO_AUTOMATICO",
            "REGLA_APLICADA": "REQUIERE_EVIDENCIA_MATERIAL",
        },
    ])
    cutoff = matriz[[
        "ID_REGISTRO",
        "FILA_PRECARGA",
        "NUM_DOCUMENTO",
        "TUVO_MATRICULA_2025",
        "TUVO_ACTIVIDAD_2025",
        "ESTADO_AL_31_12_2025",
        "CORRESPONDE_MANTENER_EXTRANJEROS_2025",
        "VIGENCIA_FINAL",
        "REQUIERE_REVISION",
        "CONFLICTO",
    ]].copy()
    write_csv(rules_summary, dirs["vigencia"] / "06S_REGLAS_VIGENCIA_HOJA2.csv")
    write_csv(cutoff, dirs["vigencia"] / "06T_CONTROL_FECHA_31_12_2025.csv")
    write_csv(matriz, dirs["vigencia"] / "DECISION_VIGENCIA_FINAL_185_HOJA2.csv")

    metrics = phase06_metrics(matriz, cruce, contradicciones_pendientes=len(contradictions))
    write_csv(pd.DataFrame([metrics]), dirs["vigencia"] / "06U_VALIDACION_MATRIZ_FINAL_185_HOJA2.csv")

    if pending_after.empty:
        post = matriz[(matriz["VIGENCIA_FINAL"].eq("")) | (matriz["REQUIERE_REVISION"].eq("SI")) | (matriz["CONFLICTO"].ne(""))].copy()
    else:
        post = pending_after.copy()
    if not post.empty:
        write_csv(post, dirs["vigencia"] / "PENDIENTES_POST_HOJA2.csv")
    else:
        write_csv(pd.DataFrame(columns=["ID_REGISTRO", "MOTIVO_POST_HOJA2"]), dirs["vigencia"] / "PENDIENTES_POST_HOJA2.csv")

    return {
        "cruce": cruce,
        "q": q_df,
        "r": r_df,
        "matriz": matriz,
        "contradictions": contradictions,
        "pending_after": post,
        "metrics": metrics,
    }


def apply_institutional_phase06_closure(
    outputs: dict[str, Any],
    dirs: dict[str, Path],
    base_path: Path,
) -> dict[str, Any]:
    matriz = outputs["matriz"].copy()
    q_df = outputs["q"].copy()
    r_df = outputs["r"].copy()
    cruce = outputs["cruce"].copy()
    accepted_contradictions = outputs["contradictions"].copy()
    audit_rows: list[dict[str, str]] = []

    keep_observation = (
        "Decision institucional: se mantiene VIGENCIA=1 por precarga oficial; no hay conflicto de identidad, "
        "CODIGO_UNICO esta informado, no existe evidencia directa de exclusion y no se amplian reglas de vigencia 0 por semejanza."
    )
    keep_secondary_default = "BASE EXTRANJEROS.xlsx:Hoja2"

    for id_reg in sorted(DECISION_INSTITUCIONAL_MANTENER):
        mask = matriz["ID_REGISTRO"].eq(id_reg)
        if not mask.any():
            continue
        before = clean(matriz.loc[mask, "VIGENCIA_FINAL"].iloc[0])
        had_hoja2 = clean(matriz.loc[mask, "CODCLI"].iloc[0]) or clean(matriz.loc[mask, "ESTADO_AL_31_12_2025"].iloc[0]) not in {"", "SIN_EVIDENCIA_HOJA2"}
        matriz.loc[mask, "VIGENCIA_FINAL"] = "1"
        matriz.loc[mask, "CORRESPONDE_MANTENER_EXTRANJEROS_2025"] = "SI"
        matriz.loc[mask, "REGLA_APLICADA"] = REGLA_MANTENER_PRECARGA
        matriz.loc[mask, "FUENTE_PRINCIPAL"] = FUENTE_PRECARGA_OFICIAL
        matriz.loc[mask, "FUENTES_SECUNDARIAS"] = keep_secondary_default if had_hoja2 else ""
        matriz.loc[mask, "CONFIANZA"] = "ALTA"
        matriz.loc[mask, "REQUIERE_REVISION"] = "NO"
        matriz.loc[mask, "CONFLICTO"] = "NO"
        matriz.loc[mask, "OBSERVACION"] = keep_observation

        q_mask = q_df["ID_REGISTRO"].eq(id_reg) if not q_df.empty else pd.Series(dtype=bool)
        if not q_df.empty and q_mask.any():
            q_df.loc[q_mask, "VIGENCIA_PROPUESTA"] = "1"
            q_df.loc[q_mask, "REGLA_APLICADA"] = REGLA_MANTENER_PRECARGA
            q_df.loc[q_mask, "CONFIANZA"] = "ALTA"
            q_df.loc[q_mask, "REQUIERE_REVISION"] = "NO"
            q_df.loc[q_mask, "OBSERVACION"] = keep_observation

        row = matriz.loc[mask].iloc[0].to_dict()
        audit_rows.append({
            "ID_REGISTRO": id_reg,
            "TIPO_DECISION": "MANTENER_1_DECISION_INSTITUCIONAL",
            "VIGENCIA_ANTES": before,
            "VIGENCIA_DESPUES": "1",
            "FUENTE_PRINCIPAL": FUENTE_PRECARGA_OFICIAL,
            "FUENTE_SECUNDARIA": keep_secondary_default if had_hoja2 else "",
            "REGLA_APLICADA": REGLA_MANTENER_PRECARGA,
            "OBSERVACION": keep_observation,
            "NUM_DOCUMENTO": clean(row.get("NUM_DOCUMENTO", "")),
            "CODIGO_UNICO": clean(row.get("CODIGO_UNICO", "")),
        })

    for id_reg, reason in DECISION_INSTITUCIONAL_CERO.items():
        mask = matriz["ID_REGISTRO"].eq(id_reg)
        if not mask.any():
            continue
        before_prev = clean(matriz.loc[mask, "VIGENCIA_PREVIA"].iloc[0])
        before_final = clean(matriz.loc[mask, "VIGENCIA_FINAL"].iloc[0])
        matriz.loc[mask, "VIGENCIA_FINAL"] = "0"
        matriz.loc[mask, "CORRESPONDE_MANTENER_EXTRANJEROS_2025"] = "NO"
        matriz.loc[mask, "CONFIANZA"] = "ALTA"
        matriz.loc[mask, "REQUIERE_REVISION"] = "NO"
        matriz.loc[mask, "CONFLICTO"] = "NO"
        matriz.loc[mask, "FUENTE_PRINCIPAL"] = f"{base_path}:Hoja2"
        matriz.loc[mask, "OBSERVACION"] = f"Decision institucional aceptada: cambio material {before_prev or '1'} a 0. {reason}"

        r_mask = r_df["ID_REGISTRO"].eq(id_reg) if not r_df.empty else pd.Series(dtype=bool)
        if not r_df.empty and r_mask.any():
            r_df.loc[r_mask, "DECISION_REQUERIDA"] = "DECISION_INSTITUCIONAL_APLICADA_VIGENCIA_0"
            r_df.loc[r_mask, "OBSERVACION"] = f"Decision institucional aceptada: {reason}"

        row = matriz.loc[mask].iloc[0].to_dict()
        audit_rows.append({
            "ID_REGISTRO": id_reg,
            "TIPO_DECISION": "CORREGIR_1_A_0_DECISION_INSTITUCIONAL",
            "VIGENCIA_ANTES": before_prev or before_final,
            "VIGENCIA_DESPUES": "0",
            "FUENTE_PRINCIPAL": f"{base_path}:Hoja2",
            "FUENTE_SECUNDARIA": clean(row.get("FUENTES_SECUNDARIAS", "")),
            "REGLA_APLICADA": clean(row.get("REGLA_APLICADA", "")),
            "OBSERVACION": reason,
            "NUM_DOCUMENTO": clean(row.get("NUM_DOCUMENTO", "")),
            "CODIGO_UNICO": clean(row.get("CODIGO_UNICO", "")),
        })

    audit = pd.DataFrame(audit_rows)
    metrics = phase06_metrics(
        matriz,
        cruce,
        contradicciones_pendientes=0,
        contradicciones_aceptadas=len(DECISION_INSTITUCIONAL_CERO),
    )
    phase06_complete = {
        "fase": 6,
        "estado": "FASE_06_COMPLETADA",
        "fecha": now(),
        "decision_institucional_aplicada": True,
        "registros_corregidos_1_a_0": len(DECISION_INSTITUCIONAL_CERO),
        "registros_mantenidos_1": len(DECISION_INSTITUCIONAL_MANTENER),
        **metrics,
    }

    write_csv(matriz, dirs["vigencia"] / "DECISION_VIGENCIA_FINAL_185_HOJA2.csv")
    write_csv(matriz[matriz["VIGENCIA_FINAL"].eq("0")].copy(), dirs["vigencia"] / "VIGENCIA_0_FINAL.csv")
    write_csv(matriz[matriz["VIGENCIA_FINAL"].eq("1")].copy(), dirs["vigencia"] / "VIGENCIA_1_FINAL.csv")
    write_csv(audit, dirs["vigencia"] / "AUDITORIA_DECISION_INSTITUCIONAL_FASE_06.csv")
    write_csv(q_df, dirs["vigencia"] / "06Q_RESOLUCION_20_PENDIENTES_CON_HOJA2.csv")
    write_csv(r_df, dirs["vigencia"] / "06R_VALIDACION_165_DECISIONES_PREVIAS.csv")
    write_csv(pd.DataFrame([metrics]), dirs["vigencia"] / "06U_VALIDACION_MATRIZ_FINAL_185_HOJA2.csv")
    write_csv(pd.DataFrame(columns=["ID_REGISTRO", "MOTIVO_POST_HOJA2"]), dirs["vigencia"] / "PENDIENTES_POST_HOJA2.csv")
    (dirs["vigencia"] / "RESUMEN_FINAL_FASE_06.json").write_text(
        json.dumps(phase06_complete, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (dirs["vigencia"] / "FASE_06_COMPLETADA.json").write_text(
        json.dumps(phase06_complete, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    outputs["matriz"] = matriz
    outputs["q"] = q_df
    outputs["r"] = r_df
    outputs["audit_phase06"] = audit
    outputs["pending_after"] = pd.DataFrame(columns=["ID_REGISTRO", "MOTIVO_POST_HOJA2"])
    outputs["metrics"] = metrics
    return outputs


def validate_final_pes(pes: pd.DataFrame) -> dict[str, Any]:
    mandatory = [
        "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO",
        "PRIMER_APELLIDO",
        "NOMBRES",
        "SEXO",
        "FECHA_NACIMIENTO",
        "PAIS_ESTUDIOS_SECUNDARIOS",
        "CODIGO_UNICO",
        "ANIO_INGRESO_CARRERA_ACTUAL",
        "SEM_INGRESO_CARRERA_ACTUAL",
        "ANIO_INGRESO_CARRERA_ORIGEN",
        "SEM_INGRESO_CARRERA_ORIGEN",
        "VIGENCIA",
    ]
    failures = []
    if len(pes) != 185:
        failures.append("UNIVERSO_PRECARGA_DISTINTO_185")
    if not pes["VIGENCIA"].isin(["0", "1"]).all():
        failures.append("VIGENCIA_FUERA_DOMINIO")
    if pes["CODIGO_UNICO"].map(clean).eq("").sum() != 0:
        failures.append("CODIGO_UNICO_VACIO")
    empty_mandatory = {}
    for col in mandatory:
        if col in pes.columns:
            n = int(pes[col].map(clean).eq("").sum())
            if n:
                empty_mandatory[col] = n
    if empty_mandatory:
        failures.append("CAMPOS_OBLIGATORIOS_VACIOS")
    return {
        "filas": int(len(pes)),
        "vigencia_0": int(pes["VIGENCIA"].eq("0").sum()),
        "vigencia_1": int(pes["VIGENCIA"].eq("1").sum()),
        "codigo_unico_vacio": int(pes["CODIGO_UNICO"].map(clean).eq("").sum()),
        "campos_obligatorios_vacios": empty_mandatory,
        "campos_obligatorios_controlados": mandatory,
        "campos_condicionales_no_forzados_en_fase06": [
            "DV",
            "SEGUNDO_APELLIDO",
            "NACIONALIDAD",
            "TIPO_RESIDENCIA_ESTUDIANTE",
            "PAIS_ORIGEN",
            "NOMBRE_UNIVERSIDAD_ORIGEN",
            "PAIS_UNIVERSIDAD_ORIGEN",
        ],
        "pruebas_fallidas": failures,
    }


def continue_phases(
    run_dir: Path,
    dirs: dict[str, Path],
    precarga: pd.DataFrame,
    matriz: pd.DataFrame,
    base_path: Path,
    sheet_name: str,
    base_hash: str,
    audit_phase06: pd.DataFrame | None = None,
) -> dict[str, Any]:
    merged = precarga.merge(
        matriz[["ID_REGISTRO", "VIGENCIA_FINAL"]],
        on="ID_REGISTRO",
        how="left",
        validate="one_to_one",
    )
    pes = merged.copy()
    pes["VIGENCIA"] = pes["VIGENCIA_FINAL"]
    pes = pes[OFFICIAL_COLS].copy()
    for col in OFFICIAL_COLS:
        pes[col] = pes[col].map(clean)
    pes_path = dirs["pes"] / "EXTRANJEROS_REGULARES_2025_FINAL_PES_HOJA2.csv"
    write_csv(pes, pes_path, sep=";")
    pes_hash = sha256(pes_path)

    codigo_val = pd.DataFrame({
        "ID_REGISTRO": matriz["ID_REGISTRO"],
        "CODIGO_UNICO": matriz["CODIGO_UNICO"],
        "CODIGO_UNICO_VACIO": matriz["CODIGO_UNICO"].map(clean).eq("").map(lambda x: "SI" if x else "NO"),
    })
    write_csv(codigo_val, dirs["codigo"] / "07_VALIDACION_CODIGO_UNICO.csv")
    incorporaciones = pd.DataFrame([{
        "INCORPORACIONES": 0,
        "OBSERVACION": "No se incorporan registros fuera de la precarga oficial de 185.",
    }])
    write_csv(incorporaciones, dirs["incorporaciones"] / "08_INCORPORACIONES_HOJA2.csv")
    write_csv(matriz, dirs["matriz"] / "09_MATRIZ_FINAL_185_HOJA2.csv")

    validation = validate_final_pes(pes)
    pending_mask = matriz["REQUIERE_REVISION"].map(clean).eq("SI") | matriz["VIGENCIA_FINAL"].map(clean).eq("")
    validation["pendientes"] = int(matriz[pending_mask]["ID_REGISTRO"].nunique())
    validation["conflictos"] = int(conflict_mask(matriz).sum())
    validation["id_registro_duplicados"] = int(matriz["ID_REGISTRO"].duplicated(keep=False).sum())
    validation["incorporaciones_confirmadas"] = 0
    if validation["pendientes"]:
        validation["pruebas_fallidas"].append("PENDIENTES_NO_CERO")
    if validation["conflictos"]:
        validation["pruebas_fallidas"].append("CONFLICTOS_NO_CERO")
    if validation["id_registro_duplicados"]:
        validation["pruebas_fallidas"].append("ID_REGISTRO_DUPLICADO")
    validation["base_institucional"] = str(base_path)
    validation["hash_base_institucional"] = base_hash
    validation["hoja"] = sheet_name
    (dirs["validacion"] / "11_VALIDACION_END_TO_END_HOJA2.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(pd.DataFrame([validation]), dirs["validacion"] / "11_VALIDACION_END_TO_END_HOJA2.csv")

    audit_path = dirs["reportes"] / "12_EXCEL_AUDITORIA_EXTRANJEROS_2025_HOJA2.xlsx"
    write_excel(audit_path, {
        "Matriz final": matriz,
        "PES": pes,
        "Validacion": pd.DataFrame([validation]),
        "Auditoria Fase 06": audit_phase06 if audit_phase06 is not None else pd.DataFrame(),
    })
    report_path = dirs["reportes"] / "13_REPORTE_FINAL_EXTRANJEROS_2025_HOJA2.md"
    report_path.write_text(
        "\n".join([
            "# Reporte final Extranjeros Regulares 2025 - Hoja2",
            "",
            f"- Fecha: {now()}",
            f"- Base institucional: {base_path}",
            f"- Hash base institucional: {base_hash}",
            f"- Hoja usada: {sheet_name}",
            f"- Registros PES: {len(pes)}",
            f"- VIGENCIA 0: {int(pes['VIGENCIA'].eq('0').sum())}",
            f"- VIGENCIA 1: {int(pes['VIGENCIA'].eq('1').sum())}",
            f"- Incorporaciones confirmadas: 0",
            f"- Pendientes: {validation['pendientes']}",
            f"- Conflictos: {validation['conflictos']}",
            f"- Pruebas fallidas: {len(validation['pruebas_fallidas'])}",
            "",
            "## Fases 07 a 15",
            "",
            "- Fase 07: CODIGO_UNICO validado.",
            "- Fase 08: incorporaciones revisadas; no se incorporan registros fuera de la precarga oficial.",
            "- Fase 09: matriz final generada.",
            "- Fase 10: PES generado.",
            "- Fase 11: validacion end-to-end generada.",
            "- Fase 12: Excel de auditoria generado.",
            "- Fase 13: reporte final generado.",
            "- Fase 14: hashes finales generados.",
            "- Fase 15: controles Git ejecutados sin commit ni push.",
        ]),
        encoding="utf-8",
    )

    hash_lines = []
    for path in [pes_path, audit_path, report_path, dirs["matriz"] / "09_MATRIZ_FINAL_185_HOJA2.csv"]:
        hash_lines.append(f"{sha256(path)}  {path}")
    hash_path = dirs["hashes"] / "14_HASHES_FINALES_HOJA2.sha256"
    hash_path.write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    desktop_dir = Path.home() / f"Desktop/EXTRANJEROS_REGULARES_2025_LISTO_PES_HOJA2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    for path in [pes_path, audit_path, report_path, hash_path]:
        shutil.copy2(path, desktop_dir / path.name)

    return {
        "pes": str(pes_path),
        "pes_hash": pes_hash,
        "audit": str(audit_path),
        "report": str(report_path),
        "desktop": str(desktop_dir),
        "validation": validation,
    }


def write_block(run_dir: Path, dirs: dict[str, Path], outputs: dict[str, Any], estado_path: Path) -> None:
    metrics = outputs["metrics"]
    pending = outputs["pending_after"]
    reason = "BLOQUEADO_EN_FASE_06_CON_EVIDENCIA_HOJA2_INSUFICIENTE"
    lines = [
        "# Bloqueo Fase 06 - Hoja2",
        "",
        f"Fecha: {now()}",
        "",
        f"Motivo: {reason}",
        "",
        "Criterios de salida no cumplidos:",
        f"- pendientes_unicos: {metrics['pendientes_unicos']}",
        f"- conflictos: {metrics['conflictos']}",
        f"- contradicciones_decisiones_previas: {metrics['contradicciones']}",
        f"- vigencia_fuera_dominio: {metrics['vigencia_fuera_dominio']}",
        "",
        "No se continua a Fase 07. No se genera PES final.",
    ]
    if not pending.empty:
        lines.extend(["", "Pendientes principales:"])
        for _, row in pending.head(30).iterrows():
            lines.append(
                f"- {clean(row.get('ID_REGISTRO', ''))}: {clean(row.get('MOTIVO_POST_HOJA2', '')) or clean(row.get('OBSERVACION', ''))}"
            )
    (dirs["vigencia"] / "BLOQUEO_FASE_06_HOJA2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    estado = {
        "ultima_fase_completada": 5,
        "fase_actual": "06",
        "estado": reason,
        "bloqueado": True,
        "motivo_bloqueo": reason,
        "fecha_actualizacion": now(),
    }
    estado_path.parent.mkdir(parents=True, exist_ok=True)
    estado_path.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_complete_state(estado_path: Path) -> None:
    estado = {
        "ultima_fase_completada": 6,
        "fase_actual": 7,
        "estado": "LISTA_PARA_SIGUIENTE_FASE",
        "bloqueado": False,
        "motivo_bloqueo": "",
        "fecha_actualizacion": now(),
    }
    estado_path.parent.mkdir(parents=True, exist_ok=True)
    estado_path.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_final_state(estado_path: Path, final_info: dict[str, Any]) -> None:
    validation = final_info.get("validation", {})
    estado = {
        "ultima_fase_completada": 15,
        "fase_actual": "COMPLETADA",
        "estado": "LISTO_PARA_CARGA_PES",
        "bloqueado": False,
        "motivo_bloqueo": "",
        "archivo_pes": final_info.get("pes", ""),
        "hash_pes": final_info.get("pes_hash", ""),
        "excel_auditoria": final_info.get("audit", ""),
        "reporte": final_info.get("report", ""),
        "carpeta_escritorio": final_info.get("desktop", ""),
        "pruebas_fallidas": validation.get("pruebas_fallidas", []),
        "fecha_actualizacion": now(),
    }
    estado_path.parent.mkdir(parents=True, exist_ok=True)
    estado_path.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_git_checks(run_dir: Path, dirs: dict[str, Path]) -> None:
    commands = {
        "git_status_short_branch.txt": ["git", "status", "--short", "--branch"],
        "git_diff_stat.txt": ["git", "diff", "--stat"],
        "git_diff_check.txt": ["git", "diff", "--check"],
    }
    for filename, cmd in commands.items():
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
        text = proc.stdout
        if proc.stderr:
            text += "\n[stderr]\n" + proc.stderr
        text += f"\n[returncode] {proc.returncode}\n"
        (dirs["git"] / filename).write_text(text, encoding="utf-8")


def canonical_sies_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "PAIS_ORIGEN" in out.columns and "PAIS_DE_ORIGEN" not in out.columns:
        out = out.rename(columns={"PAIS_ORIGEN": "PAIS_DE_ORIGEN"})
    return out


def csv_sies_source_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = canonical_sies_columns(df)
    return out[COLUMNAS_SIES_REGULARES].copy()


def apply_residencia_sin_informacion(row: pd.Series) -> pd.Series:
    out = row.copy()
    if clean(out.get("TIPO_RESIDENCIA_ESTUDIANTE", "")) == "":
        out["TIPO_RESIDENCIA_ESTUDIANTE"] = "0"
        out["PAIS_DE_ORIGEN"] = ""
    return out


def prepare_sies_loadable(final_185: pd.DataFrame, decision_nacionalidad: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    final = canonical_sies_columns(final_185)
    final.insert(0, "ID_REGISTRO", [f"PRECARGA_{i:04d}" for i in range(1, len(final) + 1)])
    decision_ids = set(decision_nacionalidad["ID_REGISTRO"].map(clean))
    excluded_base = final[final["ID_REGISTRO"].isin(decision_ids)].copy()
    sies = final[~final["ID_REGISTRO"].isin(decision_ids)].copy()
    sies = sies[COLUMNAS_SIES_REGULARES].copy()
    sies = sies.apply(apply_residencia_sin_informacion, axis=1)
    sies["FECHA_NACIMIENTO"] = sies["FECHA_NACIMIENTO"].map(normalize_date)
    for col in COLUMNAS_SIES_REGULARES:
        sies[col] = sies[col].map(clean)
    return sies, excluded_base


def build_excluidos_nacionalidad(final_185: pd.DataFrame, decision: pd.DataFrame) -> pd.DataFrame:
    final = canonical_sies_columns(final_185)
    final.insert(0, "ID_REGISTRO", [f"PRECARGA_{i:04d}" for i in range(1, len(final) + 1)])
    merged = decision.merge(final, on="ID_REGISTRO", how="left", validate="one_to_one")
    rows = []
    for _, row in merged.iterrows():
        clasificacion = clean(row.get("CLASIFICACION", ""))
        if clasificacion == "CHILENA_CONFIRMADA":
            motivo = "Nacionalidad chilena confirmada por fuente institucional; no corresponde al universo de extranjeros."
            accion = "EXCLUIR_DE_CARGA_CONSERVAR_EN_AUDITORIA"
        elif clasificacion == "SIN_FUENTE_CONCLUYENTE":
            motivo = "Nacionalidad no demostrada por fuentes autorizadas."
            accion = "EXCLUIR_DE_CARGA_CONSERVAR_EN_PENDIENTES_Y_AUDITORIA"
        else:
            motivo = "Clasificacion de nacionalidad no apta para carga automatica."
            accion = "BLOQUEAR"
        out = {
            "ID_REGISTRO": clean(row.get("ID_REGISTRO", "")),
            "CLASIFICACION_EXCLUSION": clasificacion,
            "MOTIVO_EXCLUSION": motivo,
            "ACCION": accion,
            "FUENTE": clean(row.get("FUENTE_1", "")),
            "VALOR_NACIONALIDAD_INSTITUCIONAL": clean(row.get("NACIONALIDAD_FUENTE_1", "")),
        }
        for col in COLUMNAS_SIES_REGULARES:
            out[col] = clean(row.get(col, ""))
        rows.append(out)
    return pd.DataFrame(rows)


def validate_sies_rows(sies: pd.DataFrame) -> pd.DataFrame:
    rows = []
    duplicate_mask = sies.duplicated(subset=["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "CODIGO_UNICO"], keep=False)
    for idx, row in sies.iterrows():
        errors: list[str] = []
        if clean(row["NACIONALIDAD"]) == "":
            errors.append("NACIONALIDAD_VACIA")
        if clean(row["NACIONALIDAD"]) == "38":
            errors.append("NACIONALIDAD_38_CHILE")
        if clean(row["CODIGO_UNICO"]) == "":
            errors.append("CODIGO_UNICO_VACIO")
        if clean(row["VIGENCIA"]) not in {"0", "1"}:
            errors.append("VIGENCIA_FUERA_DOMINIO")
        residencia = clean(row["TIPO_RESIDENCIA_ESTUDIANTE"])
        pais_origen = clean(row["PAIS_DE_ORIGEN"])
        if residencia not in {"0", "1", "2", "3"}:
            errors.append("TIPO_RESIDENCIA_FUERA_DOMINIO")
        if residencia == "0" and pais_origen:
            errors.append("PAIS_DE_ORIGEN_INFORMADO_CON_RESIDENCIA_0")
        if residencia in {"2", "3"} and not pais_origen:
            errors.append("PAIS_DE_ORIGEN_VACIO_CON_RESIDENCIA_2_3")
        if bool(clean(row["NOMBRE_UNIVERSIDAD_ORIGEN"])) != bool(clean(row["PAIS_UNIVERSIDAD_ORIGEN"])):
            errors.append("INCONSISTENCIA_UNIVERSIDAD_PAIS")
        fecha = normalize_date(row["FECHA_NACIMIENTO"])
        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", fecha):
            errors.append("FECHA_INVALIDA")
        if duplicate_mask.loc[idx]:
            errors.append("DUPLICADO_PERSONA_CARRERA")
        rows.append({
            "FILA_SIES": int(idx) + 1,
            "TIPO_DOCUMENTO": row["TIPO_DOCUMENTO"],
            "NUM_DOCUMENTO": row["NUM_DOCUMENTO"],
            "CODIGO_UNICO": row["CODIGO_UNICO"],
            "CANTIDAD_ERRORES": len(errors),
            "MOTIVOS_INCOMPLETITUD": " | ".join(errors),
        })
    return pd.DataFrame(rows)


def write_final_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    wb = load_workbook(path)
    fills = {
        "SIES_CON_TITULOS": PatternFill("solid", fgColor="D9EAD3"),
        "EXCLUIDOS_NACIONALIDAD": PatternFill("solid", fgColor="F4CCCC"),
        "EXTRANJEROS_INCOMPLETOS": PatternFill("solid", fgColor="FFF2CC"),
    }
    default_fill = PatternFill("solid", fgColor="1F4E78")
    font_default = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        if ws.max_row >= 1 and ws.max_column >= 1:
            ws.auto_filter.ref = ws.dimensions
        fill = fills.get(ws.title, default_fill)
        font = Font(color="000000", bold=True) if ws.title in fills else font_default
        for cell in ws[1]:
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        max_format_row = min(ws.max_row, 200)
        max_col = ws.max_column
        for row in ws.iter_rows(min_row=1, max_row=max_format_row, max_col=max_col):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                cell.number_format = "@"
        for col in ws.columns:
            max_width = 10
            for cell in list(col)[:200]:
                max_width = max(max_width, len(clean(cell.value)) + 2)
            ws.column_dimensions[col[0].column_letter].width = min(max_width, 55)
    wb.save(path)


def row_to_sies_line(values: list[str]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";", lineterminator="", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(values)
    return buffer.getvalue()


def sanitize_cp1252_text(value: str) -> str:
    # Replace or drop characters not encodable in cp1252 while preserving visible text.
    return clean(value).encode("cp1252", errors="replace").decode("cp1252")


def write_sies_csv_cp1252_no_final_newline(df: pd.DataFrame, path: Path) -> None:
    lines = []
    for _, row in df.iterrows():
        lines.append(row_to_sies_line([sanitize_cp1252_text(clean(row[col])) for col in COLUMNAS_SIES_REGULARES]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("\n".join(lines).encode("cp1252"))


def detect_csv_physical(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    lines = data.splitlines()
    first_line = lines[0].decode("cp1252", errors="replace") if lines else ""
    return {
        "bytes": len(data),
        "bom": "SI" if data.startswith(b"\xef\xbb\xbf") else "NO",
        "termina_con_salto": "SI" if data.endswith((b"\n", b"\r", b"\r\n")) else "NO",
        "lineas_fisicas": len(lines),
        "delimitadores_por_linea_ok": all(line.decode("cp1252", errors="replace").count(";") == 19 for line in lines),
        "encabezado": "SI" if "TIPO_DOCUMENTO" in first_line and "VIGENCIA" in first_line else "NO",
        "delimitador": ";",
        "codificacion": "cp1252",
    }


def compare_frames(left: pd.DataFrame, right: pd.DataFrame, label_left: str, label_right: str) -> pd.DataFrame:
    rows = []
    if left.shape != right.shape:
        rows.append({
            "FILA": "",
            "COLUMNA": "",
            "VALOR_1": str(left.shape),
            "VALOR_2": str(right.shape),
            "TIPO_DIFERENCIA": "DIFERENCIA_DIMENSION",
            "FUENTE_1": label_left,
            "FUENTE_2": label_right,
        })
        return pd.DataFrame(rows)
    left = left.reset_index(drop=True).astype(str)
    right = right.reset_index(drop=True).astype(str)
    for ridx in range(len(left)):
        for col in left.columns:
            if clean(left.loc[ridx, col]) != clean(right.loc[ridx, col]):
                rows.append({
                    "FILA": ridx + 1,
                    "COLUMNA": col,
                    "VALOR_1": clean(left.loc[ridx, col]),
                    "VALOR_2": clean(right.loc[ridx, col]),
                    "TIPO_DIFERENCIA": "VALOR_DISTINTO",
                    "FUENTE_1": label_left,
                    "FUENTE_2": label_right,
                })
    return pd.DataFrame(rows, columns=["FILA", "COLUMNA", "VALOR_1", "VALOR_2", "TIPO_DIFERENCIA", "FUENTE_1", "FUENTE_2"])


def regression_reference_frame(path: Path) -> pd.DataFrame:
    ref = pd.read_csv(path, sep=";", header=None, encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    ref.columns = COLUMNAS_SIES_REGULARES
    return ref


def final_mode_defaults(run_dir: Path) -> dict[str, Path]:
    return {
        "precarga": ROOT / "estudiantes_extranjeros_2026/Reporte Precarga del Proceso Extranjeros Regulares 2026.csv",
        "base": Path("/Users/alexi/Desktop/BASE EXTRANJEROS.xlsx"),
        "diagnostico": run_dir / "12_VALIDACION_FINAL_SIES/DIAGNOSTICO_103_CHILENAS_20260626_113142",
        "aplicacion": run_dir / "12_VALIDACION_FINAL_SIES/APLICACION_103_EXCLUSIONES_REVISION_20260626_113832",
        "regresion": Path("/Users/alexi/Desktop/EXTRANJEROS_REGULARES_2025_PES_READY_RESIDENCIA_0_20260626_121728.csv"),
        "salida": run_dir / "13_CIERRE_AUTOMATIZADO",
    }


def validate_preconditions(
    precarga: pd.DataFrame,
    base: pd.DataFrame,
    final_185: pd.DataFrame,
    decision: pd.DataFrame,
    sies: pd.DataFrame,
    completitud: pd.DataFrame,
) -> list[str]:
    failures: list[str] = []
    if precarga.shape != (185, 21):
        failures.append(f"PRECARGA_ESTRUCTURA_INVALIDA:{precarga.shape}")
    if len(final_185) != 185:
        failures.append("UNIVERSO_CONCILIADO_DISTINTO_185")
    if len(decision) != 104:
        failures.append("EXCLUIDOS_DISTINTOS_104")
    if int(decision["CLASIFICACION"].eq("CHILENA_CONFIRMADA").sum()) != 103:
        failures.append("CHILENAS_CONFIRMADAS_DISTINTO_103")
    if int(decision["CLASIFICACION"].eq("SIN_FUENTE_CONCLUYENTE").sum()) != 1:
        failures.append("SIN_NACIONALIDAD_DISTINTO_1")
    if len(sies) != 81:
        failures.append("EXTRANJEROS_COMPLETOS_DISTINTO_81")
    if int(completitud["CANTIDAD_ERRORES"].astype(int).gt(0).sum()) != 0:
        failures.append("EXTRANJEROS_INCOMPLETOS_DISTINTO_0")
    if list(sies.columns) != COLUMNAS_SIES_REGULARES:
        failures.append("ESTRUCTURA_20_COLUMNAS_INVALIDA")
    if sies.duplicated(subset=["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "CODIGO_UNICO"], keep=False).any():
        failures.append("DUPLICADOS_PERSONA_CARRERA")
    if sies["NACIONALIDAD"].map(clean).eq("").any():
        failures.append("NACIONALIDAD_VACIA")
    if sies["NACIONALIDAD"].map(clean).eq("38").any():
        failures.append("NACIONALIDAD_38")
    if sies["CODIGO_UNICO"].map(clean).eq("").any():
        failures.append("CODIGO_UNICO_VACIO")
    if (~sies["VIGENCIA"].map(clean).isin(["0", "1"])).any():
        failures.append("VIGENCIA_FUERA_DOMINIO")
    if (~sies["TIPO_RESIDENCIA_ESTUDIANTE"].map(clean).isin(["0", "1", "2", "3"])).any():
        failures.append("TIPO_RESIDENCIA_FUERA_DOMINIO")
    if ((sies["TIPO_RESIDENCIA_ESTUDIANTE"].eq("0")) & (sies["PAIS_DE_ORIGEN"].map(clean).ne(""))).any():
        failures.append("PAIS_DE_ORIGEN_INFORMADO_CON_RESIDENCIA_0")
    if ((sies["TIPO_RESIDENCIA_ESTUDIANTE"].isin(["2", "3"])) & (sies["PAIS_DE_ORIGEN"].map(clean).eq(""))).any():
        failures.append("PAIS_DE_ORIGEN_VACIO_CON_RESIDENCIA_2_3")
    if (sies["NOMBRE_UNIVERSIDAD_ORIGEN"].map(clean).ne("") != sies["PAIS_UNIVERSIDAD_ORIGEN"].map(clean).ne("")).any():
        failures.append("INCONSISTENCIA_UNIVERSIDAD_PAIS")
    if not sies["FECHA_NACIMIENTO"].map(lambda x: bool(re.fullmatch(r"\d{2}-\d{2}-\d{4}", clean(x)))).all():
        failures.append("FECHA_INVALIDA")
    if int(sies["VIGENCIA"].eq("0").sum()) != 16 or int(sies["VIGENCIA"].eq("1").sum()) != 65:
        failures.append("CONTEO_VIGENCIA_DISTINTO_16_65")
    if base.empty:
        failures.append("BASE_INSTITUCIONAL_VACIA")
    return failures


def run_final_mode(args: argparse.Namespace) -> int:
    run_dir = Path(args.reanudar).parent if args.reanudar else Path(args.ejecucion)
    defaults = final_mode_defaults(run_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    precarga_path = Path(args.precarga) if args.precarga else defaults["precarga"]
    base_path = Path(args.base_institucional) if args.base_institucional else defaults["base"]
    diagnostico_dir = Path(args.diagnostico_nacionalidad) if args.diagnostico_nacionalidad else defaults["diagnostico"]
    aplicacion_dir = Path(args.matriz_revision) if args.matriz_revision else defaults["aplicacion"]
    regresion_path = Path(args.archivo_regresion) if args.archivo_regresion else defaults["regresion"]
    salida_root = Path(args.salida) if args.salida else defaults["salida"]
    out_dir = salida_root / f"PES_READY_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    script_path = Path(__file__).resolve()
    final_pes_185_path = run_dir / "09_PES/EXTRANJEROS_REGULARES_2025_FINAL_PES_HOJA2.csv"
    decision_path = diagnostico_dir / "08_DECISION_NACIONALIDAD_104.csv"
    matriz_revision_path = aplicacion_dir / "DECISION_VIGENCIA_POST_NACIONALIDAD_185_REVISION.csv"
    source_paths = {
        "precarga": precarga_path,
        "base_institucional": base_path,
        "diagnostico_nacionalidad": decision_path,
        "matriz_revision_aplicada": matriz_revision_path,
        "pes_185_referencia_ejecucion": final_pes_185_path,
        "archivo_regresion_aprobado": regresion_path,
        "script": script_path,
    }
    missing = [name for name, path in source_paths.items() if not path.exists()]
    if missing:
        summary = {"estado": "BLOQUEADO_POR_VALIDACION_FINAL", "bloqueos": [f"FUENTE_FALTANTE:{name}" for name in missing]}
        (out_dir / "07_RESUMEN_EJECUCION.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2

    xl = pd.ExcelFile(base_path)
    if args.hoja not in xl.sheet_names:
        summary = {"estado": "BLOQUEADO_POR_VALIDACION_FINAL", "bloqueos": [f"HOJA_FALTANTE:{args.hoja}"]}
        (out_dir / "07_RESUMEN_EJECUCION.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2

    precarga = pd.read_csv(precarga_path, sep=";", encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    base = pd.read_excel(base_path, sheet_name=args.hoja, dtype=str, keep_default_na=False).fillna("")
    final_185 = pd.read_csv(final_pes_185_path, sep=";", dtype=str, keep_default_na=False).fillna("")
    decision = pd.read_csv(decision_path, dtype=str, keep_default_na=False).fillna("")
    matriz_revision = pd.read_csv(matriz_revision_path, dtype=str, keep_default_na=False).fillna("")

    sies, _ = prepare_sies_loadable(final_185, decision)
    completitud = validate_sies_rows(sies)
    incompletos = sies[completitud["CANTIDAD_ERRORES"].astype(int).gt(0).to_numpy()].copy()
    incompletos = pd.concat([
        completitud[completitud["CANTIDAD_ERRORES"].astype(int).gt(0)][["CANTIDAD_ERRORES", "MOTIVOS_INCOMPLETITUD"]].reset_index(drop=True),
        incompletos.reset_index(drop=True),
    ], axis=1)
    if incompletos.empty:
        incompletos = pd.DataFrame(columns=["CANTIDAD_ERRORES", "MOTIVOS_INCOMPLETITUD"] + COLUMNAS_SIES_REGULARES)

    excluded = build_excluidos_nacionalidad(final_185, decision)
    failures = validate_preconditions(precarga, base, final_185, decision, sies, completitud)
    status = "LISTO_PARA_CARGA_SIES" if not failures else "BLOQUEADO_POR_VALIDACION_FINAL"

    csv_path = out_dir / "02_EXTRANJEROS_REGULARES_2025_PES_READY.csv"
    excel_path = out_dir / "01_RESUMEN_EXTRANJEROS_REGULARES_2025.xlsx"
    relectura = pd.DataFrame()
    comparacion_regresion = pd.DataFrame(columns=["FILA", "COLUMNA", "VALOR_1", "VALOR_2", "TIPO_DIFERENCIA", "FUENTE_1", "FUENTE_2"])
    diferencias_excel_csv = pd.DataFrame(columns=["FILA", "COLUMNA", "VALOR_1", "VALOR_2", "TIPO_DIFERENCIA", "FUENTE_1", "FUENTE_2"])
    csv_hash = ""
    copied_excel = ""
    copied_csv = ""
    copied_excel_hash = ""
    copied_csv_hash = ""

    resumen_preliminar = pd.DataFrame([{
        "proceso": "Estudiantes Extranjeros Regulares SIES 2026",
        "anio_datos": args.anio_datos,
        "fecha_ejecucion": now(),
        "fuentes_utilizadas": " | ".join(str(p) for p in source_paths.values()),
        "hashes_fuentes": json.dumps({k: sha256(v) for k, v in source_paths.items()}, ensure_ascii=False),
        "universo_precarga": len(precarga),
        "excluidos_por_nacionalidad_chilena": int(decision["CLASIFICACION"].eq("CHILENA_CONFIRMADA").sum()),
        "excluidos_sin_nacionalidad_demostrada": int(decision["CLASIFICACION"].eq("SIN_FUENTE_CONCLUYENTE").sum()),
        "extranjeros_completos": len(sies),
        "extranjeros_incompletos": len(incompletos),
        "VIGENCIA_0": int(sies["VIGENCIA"].eq("0").sum()),
        "VIGENCIA_1": int(sies["VIGENCIA"].eq("1").sum()),
        "duplicados": int(sies.duplicated(subset=["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "CODIGO_UNICO"], keep=False).sum()),
        "estado_final": status,
        "ruta_CSV": str(csv_path) if status == "LISTO_PARA_CARGA_SIES" else "",
        "hash_CSV": "",
    }])

    if status == "LISTO_PARA_CARGA_SIES" and args.generar_pes:
        write_sies_csv_cp1252_no_final_newline(sies, csv_path)
        physical = detect_csv_physical(csv_path)
        reread = pd.read_csv(csv_path, sep=";", header=None, encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
        reread.columns = COLUMNAS_SIES_REGULARES
        diferencias_excel_csv = compare_frames(sies, reread, "SIES_CON_TITULOS", "CSV_RELECTURA")
        ref = regression_reference_frame(regresion_path)
        comparacion_regresion = compare_frames(sies, ref, "SIES_CON_TITULOS", "ARCHIVO_APROBADO")
        relectura = pd.DataFrame([{
            **physical,
            "filas_relectura": int(reread.shape[0]),
            "columnas_relectura": int(reread.shape[1]),
            "diferencias_excel_vs_csv": int(len(diferencias_excel_csv)),
            "diferencias_con_archivo_aprobado": int(len(comparacion_regresion)),
            "hash_csv": sha256(csv_path),
            "hash_archivo_aprobado": sha256(regresion_path),
            "hash_coincide_archivo_aprobado": "SI" if sha256(csv_path) == sha256(regresion_path) else "NO",
        }])
        physical_failures = []
        if physical["bom"] != "NO":
            physical_failures.append("CSV_CON_BOM")
        if physical["termina_con_salto"] != "NO":
            physical_failures.append("CSV_TERMINA_CON_SALTO")
        if physical["lineas_fisicas"] != 81:
            physical_failures.append("CSV_LINEAS_DISTINTO_81")
        if not physical["delimitadores_por_linea_ok"]:
            physical_failures.append("CSV_DELIMITADORES_INVALIDOS")
        if physical["encabezado"] != "NO":
            physical_failures.append("CSV_CON_ENCABEZADO")
        if reread.shape != (81, 20):
            physical_failures.append("CSV_RELECTURA_DIMENSION_INVALIDA")
        if len(diferencias_excel_csv):
            physical_failures.append("DIFERENCIAS_EXCEL_VS_CSV")
        if len(comparacion_regresion):
            physical_failures.append("DIFERENCIAS_CON_ARCHIVO_APROBADO")
        if physical_failures:
            failures.extend(physical_failures)
            status = "BLOQUEADO_POR_VALIDACION_FINAL"
            csv_path.unlink(missing_ok=True)
        else:
            csv_hash = sha256(csv_path)

    if args.generar_excel:
        resumen_final = resumen_preliminar.copy()
        resumen_final.loc[0, "estado_final"] = status
        resumen_final.loc[0, "ruta_CSV"] = str(csv_path) if csv_path.exists() else ""
        resumen_final.loc[0, "hash_CSV"] = csv_hash
        write_final_excel(excel_path, {
            "RESUMEN": resumen_final,
            "RAW_ALUMNO_31122025": base,
            "RAW_PRECARGA_2026": precarga,
            "EXCLUIDOS_NACIONALIDAD": excluded,
            "SIES_CON_TITULOS": sies,
            "EXTRANJEROS_INCOMPLETOS": incompletos,
        })

    write_csv(excluded, out_dir / "03_AUDITORIA_EXCLUSIONES_NACIONALIDAD.csv")
    write_csv(completitud, out_dir / "04_AUDITORIA_COMPLETITUD.csv")
    if relectura.empty:
        relectura = pd.DataFrame(columns=[
            "bytes", "bom", "termina_con_salto", "lineas_fisicas", "delimitadores_por_linea_ok",
            "encabezado", "delimitador", "codificacion", "filas_relectura", "columnas_relectura",
            "diferencias_excel_vs_csv", "diferencias_con_archivo_aprobado", "hash_csv",
            "hash_archivo_aprobado", "hash_coincide_archivo_aprobado",
        ])
    write_csv(relectura, out_dir / "05_AUDITORIA_RELECTURA_CSV.csv")
    write_csv(comparacion_regresion, out_dir / "06_COMPARACION_CON_ARCHIVO_APROBADO.csv")

    if status == "LISTO_PARA_CARGA_SIES" and args.copiar_escritorio:
        desktop = Path.home() / "Desktop"
        excel_desktop = desktop / f"RESUMEN_EXTRANJEROS_REGULARES_2025_{timestamp}.xlsx"
        csv_desktop = desktop / f"EXTRANJEROS_REGULARES_2025_PES_READY_{timestamp}.csv"
        shutil.copy2(excel_path, excel_desktop)
        shutil.copy2(csv_path, csv_desktop)
        copied_excel = str(excel_desktop)
        copied_csv = str(csv_desktop)
        copied_excel_hash = sha256(excel_desktop)
        copied_csv_hash = sha256(csv_desktop)
        if copied_excel_hash != sha256(excel_path) or copied_csv_hash != sha256(csv_path):
            failures.append("COPIA_ESCRITORIO_HASH_DISTINTO")
            status = "BLOQUEADO_POR_VALIDACION_FINAL"
        elif args.abrir_resultados:
            subprocess.run(["open", str(excel_desktop)], check=False)
            subprocess.run(["open", "-R", str(csv_desktop)], check=False)

    output_paths = {
        "excel": str(excel_path) if excel_path.exists() else "",
        "csv": str(csv_path) if csv_path.exists() else "",
        "auditoria_exclusiones": str(out_dir / "03_AUDITORIA_EXCLUSIONES_NACIONALIDAD.csv"),
        "auditoria_completitud": str(out_dir / "04_AUDITORIA_COMPLETITUD.csv"),
        "auditoria_relectura": str(out_dir / "05_AUDITORIA_RELECTURA_CSV.csv"),
        "comparacion_regresion": str(out_dir / "06_COMPARACION_CON_ARCHIVO_APROBADO.csv"),
        "desktop_excel": copied_excel,
        "desktop_csv": copied_csv,
    }
    source_hashes = {k: sha256(v) for k, v in source_paths.items()}
    output_hashes = {k: sha256(Path(v)) for k, v in output_paths.items() if v and Path(v).exists()}
    conteos = {
        "universo": int(len(final_185)),
        "excluidos": int(len(decision)),
        "chilenas": int(decision["CLASIFICACION"].eq("CHILENA_CONFIRMADA").sum()),
        "sin_nacionalidad": int(decision["CLASIFICACION"].eq("SIN_FUENTE_CONCLUYENTE").sum()),
        "extranjeros_completos": int(len(sies)),
        "extranjeros_incompletos": int(len(incompletos)),
        "vigencia_0": int(sies["VIGENCIA"].eq("0").sum()),
        "vigencia_1": int(sies["VIGENCIA"].eq("1").sum()),
        "residencia_0": int(sies["TIPO_RESIDENCIA_ESTUDIANTE"].eq("0").sum()),
        "nacionalidad_vacia": int(sies["NACIONALIDAD"].map(clean).eq("").sum()),
        "nacionalidad_38": int(sies["NACIONALIDAD"].map(clean).eq("38").sum()),
        "codigo_unico_vacio": int(sies["CODIGO_UNICO"].map(clean).eq("").sum()),
    }
    relectura_row = relectura.iloc[0].to_dict() if not relectura.empty and len(relectura) else {}
    resumen = {
        "timestamp": timestamp,
        "proceso": "Estudiantes Extranjeros Regulares SIES 2026",
        "anio_proceso": 2026,
        "anio_datos": args.anio_datos,
        "script": str(script_path),
        "script_version_sha256": sha256(script_path),
        "fuentes": {k: str(v) for k, v in source_paths.items()},
        "hashes_fuentes": source_hashes,
        "conteos": conteos,
        "validaciones": {
            "bloqueos": failures,
            "diferencias_excel_vs_csv": int(len(diferencias_excel_csv)),
            "diferencias_con_archivo_aprobado": int(len(comparacion_regresion)),
            "relectura": relectura_row,
        },
        "salidas": output_paths,
        "hashes_salidas": output_hashes,
        "estado": status,
    }
    write_csv(pd.DataFrame([resumen]), out_dir / "07_RESUMEN_EJECUCION.csv")
    (out_dir / "07_RESUMEN_EJECUCION.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    branch = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False).stdout.strip()
    manifest = {
        "timestamp": timestamp,
        "proceso": "Estudiantes Extranjeros Regulares SIES 2026",
        "año_proceso": 2026,
        "año_datos": args.anio_datos,
        "repositorio": str(ROOT),
        "rama": branch,
        "script": str(script_path),
        "version_script": sha256(script_path),
        "fuentes": {k: str(v) for k, v in source_paths.items()},
        "hashes_fuentes": source_hashes,
        "parametros": vars(args),
        "reglas_aplicadas": [
            "EXCLUSION_NACIONALIDAD_CHILENA",
            "EXCLUSION_SIN_NACIONALIDAD_DEMOSTRADA",
            "RESIDENCIA_SIN_INFORMACION_CODIGO_0",
            "CONSERVAR_VIGENCIA_DOCUMENTADA",
        ],
        "conteos": conteos,
        "salidas": output_paths,
        "hashes_salidas": output_hashes,
        "validaciones": resumen["validaciones"],
        "estado": status,
        "bloqueos": failures,
        "fases": {
            "FASE_01_LOCALIZACION": "COMPLETADA",
            "FASE_02_LECTURA": "COMPLETADA",
            "FASE_03_CONCILIACION": "COMPLETADA",
            "FASE_04_NACIONALIDAD": "COMPLETADA",
            "FASE_05_VIGENCIA": "COMPLETADA",
            "FASE_06_COMPLETITUD": "COMPLETADA",
            "FASE_07_EXCEL": "COMPLETADA" if excel_path.exists() else "NO_SOLICITADA",
            "FASE_08_CSV": "COMPLETADA" if csv_path.exists() else "BLOQUEADA",
            "FASE_09_RELECTURA": "COMPLETADA" if not relectura.empty and len(relectura) else "BLOQUEADA",
            "FASE_10_REGRESION": "COMPLETADA" if status == "LISTO_PARA_CARGA_SIES" else "BLOQUEADA",
            "FASE_11_CIERRE": "COMPLETADA" if status == "LISTO_PARA_CARGA_SIES" else "BLOQUEADA",
        },
    }
    (out_dir / "09_MANIFEST_EJECUCION.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Cierre automatizado Extranjeros Regulares 2025",
        "",
        f"Estado: {status}",
        f"Universo: {conteos['universo']}",
        f"Excluidos: {conteos['excluidos']}",
        f"Extranjeros completos: {conteos['extranjeros_completos']}",
        f"Extranjeros incompletos: {conteos['extranjeros_incompletos']}",
        f"VIGENCIA=0: {conteos['vigencia_0']}",
        f"VIGENCIA=1: {conteos['vigencia_1']}",
        f"CSV: {output_paths['csv'] or 'NO_GENERADO'}",
        f"Excel: {output_paths['excel'] or 'NO_GENERADO'}",
        f"Bloqueos: {', '.join(failures) if failures else '0'}",
    ]
    (out_dir / "10_REPORTE_CIERRE.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    hash_lines = []
    for path in sorted(out_dir.glob("*")):
        if path.is_file() and path.name != "08_HASHES.sha256":
            hash_lines.append(f"{sha256(path)}  {path}")
    (out_dir / "08_HASHES.sha256").write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0 if status == "LISTO_PARA_CARGA_SIES" else 2


def normalize_key(value: Any) -> str:
    text = canon_text(value)
    return re.sub(r"[^A-Z0-9]+", "", text)


def read_csv_flexible(path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "cp1252", "latin1"]
    separators = [";", ",", "\t", "|"]
    for enc in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding=enc).fillna("")
                if len(df.columns) >= 2:
                    return df
            except Exception:
                continue
    return pd.DataFrame()


def split_rut(value: Any) -> tuple[str, str, str]:
    raw = clean(value).upper()
    if not raw:
        return "", "", ""
    compact = re.sub(r"[^0-9K]", "", raw)
    if not compact:
        return "", "", ""
    if "-" in raw:
        left, right = raw.split("-", 1)
        body = re.sub(r"[^0-9]", "", left)
        dv = re.sub(r"[^0-9K]", "", right)
        if body and dv:
            return body, dv[-1], f"{body}{dv[-1]}"
    if len(compact) >= 2 and compact[-1] in "0123456789K":
        return compact[:-1], compact[-1], compact
    return compact, "", compact


def rut_variants(body: str, dv: str) -> set[str]:
    out: set[str] = set()
    if body:
        out.add(body)
    if body and dv:
        out.add(f"{body}{dv}")
        out.add(f"{body}-{dv}")
    return {re.sub(r"[^0-9A-Z]", "", x.upper()) for x in out if clean(x)}


def doc_variants(num_documento: str, dv: str) -> set[str]:
    body = re.sub(r"[^0-9]", "", clean(num_documento))
    dv_norm = re.sub(r"[^0-9K]", "", clean(dv).upper())
    return rut_variants(body, dv_norm[-1] if dv_norm else "")


def format_row_location(file_path: Path, sheet_name: str, row_idx: int, col_name: str) -> dict[str, str]:
    return {
        "ARCHIVO_FUENTE": str(file_path),
        "HOJA_FUENTE": sheet_name,
        "FILA_FUENTE": str(row_idx),
        "COLUMNA_MATCH": clean(col_name),
    }


def load_nacionalidad_catalogo() -> tuple[dict[str, str], dict[str, str], set[str]]:
    cat = ROOT / "estudiantes_extranjeros_2026/data/governed/catalogos/NACIONALIDAD_SIES.tsv"
    by_code: dict[str, str] = {}
    by_text: dict[str, str] = {}
    codes: set[str] = set()
    if not cat.exists():
        return by_code, by_text, codes
    df = pd.read_csv(cat, sep="\t", dtype=str, keep_default_na=False).fillna("")
    for _, row in df.iterrows():
        code = strip_excel_decimal(row.get("CODIGO", ""))
        desc = clean(row.get("DESCRIPCION_OFICIAL", ""))
        desc_norm = canon_text(row.get("DESCRIPCION_NORMALIZADA", ""))
        sinonimos = clean(row.get("SINONIMOS_CONTROLADOS", ""))
        if not code:
            continue
        codes.add(code)
        if desc:
            by_code[code] = desc
        for txt in [desc, desc_norm] + [x.strip() for x in sinonimos.split("|") if x.strip()]:
            key = canon_text(txt)
            if key:
                by_text[key] = code
    return by_code, by_text, codes


def map_nacionalidad_to_sies(value: str, by_text: dict[str, str], valid_codes: set[str]) -> str:
    v = clean(value)
    if not v:
        return ""
    numeric = strip_excel_decimal(v)
    if numeric in valid_codes:
        return numeric
    key = canon_text(v)
    return by_text.get(key, "")


def classify_nacionalidad(codes: set[str]) -> str:
    if not codes:
        return "SIN_NACIONALIDAD_EN_FUENTES"
    if len(codes) > 1:
        return "CONFLICTO_MULTIPLES_NACIONALIDADES"
    only = next(iter(codes))
    if only == "38":
        return "SOLO_CHILENA_CONFIRMADA"
    return "NACIONALIDAD_UNICA_RECUPERADA"


ESTADO_KEYS = {
    "ESTADO",
    "ESTADOACADEMICO",
    "ESTADO_ACADEMICO",
    "ESTACAD",
    "SITUACION",
    "SITUACIONACADEMICA",
    "SITUACION_ACADEMICA",
    "ESTADOALUMNO",
    "ESTADO_MATRICULA",
}

ACTIVIDAD_KEYS = {
    "ANOMATRICULA",
    "ANIOMATRICULA",
    "AÑO_MATRICULA",
    "PERIODO",
    "PERIODOACADEMICO",
    "PERIODO_ACADEMICO",
    "ASIGNATURAS",
    "ASIGNATURASINSCRITAS",
    "ASIGNATURAS_INSCRITAS",
    "ASIGNATURASCURSADAS",
    "ASIGNATURAS_CURSADAS",
    "RAMOSINSCRITOS",
    "RAMOS_INSCRITOS",
    "RAMOSCURSADOS",
    "RAMOS_CURSADOS",
    "CREDITOSINSCRITOS",
    "CREDITOS_INSCRITOS",
    "CREDITOSAPROBADOS",
    "CREDITOS_APROBADOS",
    "ACTIVIDADACADEMICA",
    "ACTIVIDAD_ACADEMICA",
    "MATRICULA2025",
    "MATRICULA_2025",
    "INSCRIPCION2025",
    "INSCRIPCION_2025",
}

CODCLI_KEYS = {"CODCLI", "CODALUMNO", "CODIGOALUMNO", "IDALUMNO"}
DOC_KEYS = {"RUT", "RUN", "NRODOC", "NUMDOCUMENTO", "DOCUMENTO", "RUTALUMNO", "RUNALUMNO", "N_DOC"}


def classify_estado_academico(value: str) -> str:
    v = canon_text(value)
    if not v:
        return "ESTADO_NO_ENCONTRADO"
    if any(tok in v for tok in ["ELIMIN", "DESERT", "INACT", "ABANDON", "RETIR", "BAJA", "SUSPEND"]):
        return "ESTADO_ELIMINADO_DESERTOR_INACTIVO"
    if any(tok in v for tok in ["EGRES", "TITUL"]):
        return "ESTADO_EGRESADO_TITULADO"
    if any(tok in v for tok in ["VIGENTE", "ACTIV", "REGULAR", "MATRICUL"]):
        return "ESTADO_ACTIVO_O_VIGENTE"
    return "ESTADO_NO_CLASIFICADO"


def activity_2025_from_row(activity_values: dict[str, str]) -> tuple[str, str]:
    used_fields = [k for k, v in activity_values.items() if clean(v)]
    if not used_fields:
        return "ACTIVIDAD_2025_NO_DETERMINADA", ""

    observed = False
    explicit_negative = False
    details: list[str] = []
    for key, raw in activity_values.items():
        val = clean(raw)
        if not val:
            continue
        nkey = normalize_key(key)
        nval = canon_text(val)
        details.append(f"{key}={val}")
        if "2025" in val:
            observed = True
        if nkey in {"ANOMATRICULA", "ANIOMATRICULA", "MATRICULA2025", "INSCRIPCION2025"} and val == "2025":
            observed = True
        if re.fullmatch(r"\d+(\.\d+)?", val):
            try:
                observed = observed or float(val) > 0
                explicit_negative = explicit_negative or float(val) == 0
            except ValueError:
                pass
        if any(tok in nval for tok in ["SI", "VIGENTE", "INSCRIT", "CURSAD", "ACTIVO", "MATRICUL", "APROBAD"]):
            observed = True
        if any(tok in nval for tok in ["NO", "SIN", "NINGUNA", "NINGUNO", "INACT", "DESERT", "ELIMIN"]):
            explicit_negative = True

    if observed:
        return "ACTIVIDAD_2025_OBSERVADA", " | ".join(details[:6])
    if explicit_negative:
        return "SIN_ACTIVIDAD_2025_OBSERVADA", " | ".join(details[:6])
    return "ACTIVIDAD_2025_NO_DETERMINADA", " | ".join(details[:6])


def classify_nacionalidad_observada(values: set[str]) -> tuple[str, str]:
    clean_values = {canon_text(v) for v in values if clean(v)}
    if not clean_values:
        return "SIN_NACIONALIDAD_OBSERVADA", ""
    if len(clean_values) > 1:
        has_chile = any("CHIL" in v for v in clean_values)
        has_other = any("CHIL" not in v for v in clean_values)
        if has_chile and has_other:
            return "CONFLICTO_NACIONALIDAD", " | ".join(sorted(clean_values))
    only = next(iter(clean_values)) if len(clean_values) == 1 else ""
    if only and "CHIL" in only:
        return "NACIONALIDAD_OBSERVADA_CHILENA", only
    if only:
        return "NACIONALIDAD_OBSERVADA_EXTRANJERA", only
    return "CONFLICTO_NACIONALIDAD", " | ".join(sorted(clean_values))


def select_best_match_row(case_matches: pd.DataFrame) -> pd.Series | None:
    if case_matches.empty:
        return None
    ranked: list[tuple[int, int, pd.Series]] = []
    for idx, row in case_matches.reset_index(drop=True).iterrows():
        score = 0
        if clean(row.get("NACIONALIDAD_DATOS_ALUMNOS", "")):
            score += 50
        if clean(row.get("LETRA_COLUMNA_NACIONALIDAD", "")) == "Z":
            score += 20
        if clean(row.get("ESTADO_ACADEMICO_OBSERVADO", "")):
            score += 10
        if clean(row.get("ACTIVIDAD_2025_EVIDENCIA", "")):
            score += 10
        ranked.append((score, idx, row))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked[0][2]


def motivo_vigencia_0(
    num_doc: str,
    clas_nac: str,
    clas_estado: str,
    clas_actividad: str,
    has_complementary_evidence: bool,
) -> str:
    if re.sub(r"[^0-9]", "", num_doc) == "26481336":
        return "DECISION_OPERATIVA_TVS_OBSERVADO"
    if clas_nac == "NACIONALIDAD_OBSERVADA_CHILENA":
        if has_complementary_evidence:
            return "NACIONALIDAD_CHILENA_Y_EVIDENCIA_ACADEMICA_COMPLEMENTARIA"
        return "NACIONALIDAD_CHILENA_NO_CORRESPONDE_UNIVERSO_EXTRANJEROS"
    if clas_nac == "NACIONALIDAD_OBSERVADA_EXTRANJERA":
        if clas_estado == "ESTADO_ELIMINADO_DESERTOR_INACTIVO" and clas_actividad != "ACTIVIDAD_2025_OBSERVADA":
            return "ESTADO_ACADEMICO_ELIMINADO_SIN_ACTIVIDAD_2025"
        if clas_actividad == "SIN_ACTIVIDAD_2025_OBSERVADA":
            return "SIN_MATRICULA_O_SIN_ASIGNATURAS_2025"
    return "SIN_NACIONALIDAD_EXTRANJERA_DEMOSTRADA"


def run_sies120_mode(args: argparse.Namespace) -> int:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = ROOT / "estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455"
    out_base = run_root / "14_CORRECCION_SIES_120_CASOS"
    if args.generar_carga_104_vigencia_0 and args.auditar_estado_actividad:
        out_dir = out_base / f"GENERACION_CARGA_104_VIGENCIA_0_AUDITORIA_ESTADO_{ts}"
    elif args.generar_carga_104_vigencia_0:
        out_dir = out_base / f"GENERACION_CARGA_104_VIGENCIA_0_CHILENA_TVS_{ts}"
    else:
        out_dir = out_base / f"RESOLUCION_104_NACIONALIDAD_DATOS_ALUMNOS_Z_{ts}"
    out_dir.mkdir(parents=True, exist_ok=False)

    listado_src = Path(args.listado_sies_120)
    precarga_path = Path(args.precarga) if args.precarga else ROOT / "estudiantes_extranjeros_2026/Reporte Precarga del Proceso Extranjeros Regulares 2026.csv"
    csv_prev_path = Path(args.csv_previo)
    fallback_csv_previo = ROOT / "estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455/13_CIERRE_AUTOMATIZADO/PES_READY_20260626_130431/02_EXTRANJEROS_REGULARES_2025_PES_READY.csv"
    if not csv_prev_path.exists() and fallback_csv_previo.exists():
        csv_prev_path = fallback_csv_previo
    script_path = Path(__file__).resolve()

    bloqueos: list[str] = []
    source_hashes: dict[str, str] = {}

    for name, path in {
        "listado_sies_120": listado_src,
        "precarga_oficial": precarga_path,
        "csv_previo": csv_prev_path,
    }.items():
        if not path.exists():
            raise SystemExit(f"BLOQUEADO_POR_VALIDACION_FINAL:{name.upper()}_INEXISTENTE:{path}")
        source_hashes[name] = sha256(path)
    source_hashes["script"] = sha256(script_path)

    if source_hashes["csv_previo"] != "e45eba791c4575dc90ddb31d2ed6bcca4feb1f35f5f41ba8d80af5c514d697d2":
        raise SystemExit("BLOQUEADO_POR_VALIDACION_FINAL:CSV_PREVIO_HASH_NO_COINCIDE")

    listado = pd.read_excel(listado_src, sheet_name=0, dtype=str, keep_default_na=False).fillna("")
    if len(listado) != 120:
        bloqueos.append(f"LISTADO_SIES_NO_TIENE_120_FILAS:{len(listado)}")

    alias_120 = {
        "TIPO_DOCUMENTO": ["TIPODOCUMENTO"],
        "NUM_DOCUMENTO": ["NUMDOCUMENTO"],
        "DV": ["DV"],
        "PRIMER_APELLIDO": ["PRIMERAPELLIDO"],
        "SEGUNDO_APELLIDO": ["SEGUNDOAPELLIDO"],
        "NOMBRES": ["NOMBRES"],
        "CODIGO_UNICO": ["CODIGOUNICO"],
        "VIGENCIA": ["CARGAREGULARVIGENCIA", "VIGENCIA"],
    }
    key_to_col = {normalize_key(c): c for c in listado.columns}
    map_120: dict[str, str] = {}
    for logical, keys in alias_120.items():
        found = ""
        for k in keys:
            if k in key_to_col:
                found = key_to_col[k]
                break
        if not found:
            bloqueos.append(f"LISTADO_SIES_COLUMNA_FALTANTE:{logical}")
        else:
            map_120[logical] = found

    if any(x.startswith("LISTADO_SIES_COLUMNA_FALTANTE") for x in bloqueos):
        raise SystemExit("BLOQUEADO_POR_VALIDACION_FINAL:LISTADO_SIES_ESTRUCTURA_INVALIDA")

    l120 = pd.DataFrame({
        "TIPO_DOCUMENTO": listado[map_120["TIPO_DOCUMENTO"]].map(clean),
        "NUM_DOCUMENTO": listado[map_120["NUM_DOCUMENTO"]].map(strip_excel_decimal),
        "DV": listado[map_120["DV"]].map(clean),
        "PRIMER_APELLIDO": listado[map_120["PRIMER_APELLIDO"]].map(clean),
        "SEGUNDO_APELLIDO": listado[map_120["SEGUNDO_APELLIDO"]].map(clean),
        "NOMBRES": listado[map_120["NOMBRES"]].map(clean),
        "CODIGO_UNICO": listado[map_120["CODIGO_UNICO"]].map(clean),
        "VIGENCIA_SIES_LISTADO": listado[map_120["VIGENCIA"]].map(clean),
    })
    l120["DOC_BODY"] = l120["NUM_DOCUMENTO"].map(lambda x: re.sub(r"[^0-9]", "", clean(x)))
    l120["DV_NORM"] = l120["DV"].map(lambda x: re.sub(r"[^0-9K]", "", clean(x).upper())[-1:] if clean(x) else "")
    l120["CODIGO_UNICO_NORM"] = l120["CODIGO_UNICO"].map(normalize_code)
    l120["KEY_DOC"] = l120.apply(lambda r: f"{r['TIPO_DOCUMENTO']}|{r['DOC_BODY']}|{r['DV_NORM']}|{r['CODIGO_UNICO_NORM']}", axis=1)
    if int(l120["KEY_DOC"].nunique()) != 120:
        bloqueos.append("LISTADO_SIES_NO_TIENE_120_CASOS_UNICOS")

    precarga = pd.read_csv(precarga_path, sep=";", encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    if "PAIS_ORIGEN" in precarga.columns and "PAIS_DE_ORIGEN" not in precarga.columns:
        precarga = precarga.rename(columns={"PAIS_ORIGEN": "PAIS_DE_ORIGEN"})
    precarga.insert(0, "ID_REGISTRO", [f"PRECARGA_{i:04d}" for i in range(1, len(precarga) + 1)])
    for col in ["NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "TIPO_DOCUMENTO"]:
        precarga[col] = precarga[col].map(clean)
    precarga["DOC_BODY"] = precarga["NUM_DOCUMENTO"].map(lambda x: re.sub(r"[^0-9]", "", clean(x)))
    precarga["DV_NORM"] = precarga["DV"].map(lambda x: re.sub(r"[^0-9K]", "", clean(x).upper())[-1:] if clean(x) else "")
    precarga["CODIGO_UNICO_NORM"] = precarga["CODIGO_UNICO"].map(normalize_code)
    precarga["KEY_DOC"] = precarga.apply(lambda r: f"{r['TIPO_DOCUMENTO']}|{r['DOC_BODY']}|{r['DV_NORM']}|{r['CODIGO_UNICO_NORM']}", axis=1)

    prev = pd.read_csv(csv_prev_path, sep=";", header=None, encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    if prev.shape[1] != 20:
        bloqueos.append(f"CSV_PREVIO_COLUMNAS_INVALIDAS:{prev.shape[1]}")
    prev.columns = COLUMNAS_SIES_REGULARES
    for col in ["NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "TIPO_DOCUMENTO"]:
        prev[col] = prev[col].map(clean)
    prev["DOC_BODY"] = prev["NUM_DOCUMENTO"].map(lambda x: re.sub(r"[^0-9]", "", clean(x)))
    prev["DV_NORM"] = prev["DV"].map(lambda x: re.sub(r"[^0-9K]", "", clean(x).upper())[-1:] if clean(x) else "")
    prev["CODIGO_UNICO_NORM"] = prev["CODIGO_UNICO"].map(normalize_code)
    prev["KEY_DOC"] = prev.apply(lambda r: f"{r['TIPO_DOCUMENTO']}|{r['DOC_BODY']}|{r['DV_NORM']}|{r['CODIGO_UNICO_NORM']}", axis=1)

    c120 = l120.merge(
        precarga[["ID_REGISTRO", "KEY_DOC"] + COLUMNAS_SIES_REGULARES],
        on="KEY_DOC",
        how="left",
        validate="one_to_one",
        suffixes=("", "_PRECARGA"),
    )
    if c120["ID_REGISTRO"].map(clean).eq("").any():
        bloqueos.append("NO_SE_PUEDE_CONTRASTAR_120_VS_PRECARGA")

    c120["EN_CSV_PREVIO"] = c120["KEY_DOC"].isin(set(prev["KEY_DOC"]))
    ya_cargados = c120[c120["EN_CSV_PREVIO"]].copy()
    pendientes = c120[~c120["EN_CSV_PREVIO"]].copy()
    if len(ya_cargados) != 16 or len(pendientes) != 104:
        bloqueos.append(f"CONTEO_YA_CARGADOS_PENDIENTES_INVALIDO:{len(ya_cargados)}:{len(pendientes)}")

    pendientes = pendientes.reset_index(drop=True)
    pendientes["CASE_ID"] = [f"CASO_{i+1:03d}" for i in range(len(pendientes))]
    pendientes["RUT_VARIANTS"] = pendientes.apply(lambda r: sorted(doc_variants(r["NUM_DOCUMENTO"], r["DV"])), axis=1)

    case_variants: dict[str, set[str]] = {}
    variant_to_cases: dict[str, set[str]] = defaultdict(set)
    for _, row in pendientes.iterrows():
        case = clean(row["CASE_ID"])
        vars_set = set(row["RUT_VARIANTS"])
        case_variants[case] = vars_set
        for v in vars_set:
            variant_to_cases[v].add(case)

    keywords = [
        "DATOS ALUMNOS",
        "DATOSDEALUMNOS",
        "PROMEDIOSDEALUMNOS",
        "BASE EXTRANJEROS",
        "ALUMNOS",
        "MATRICULA",
        "MATRÍCULA",
        "ASIGNATURAS",
        "AVANCE",
        "INSCRIPCIONES",
        "RAMOS",
        "ACTAS",
    ]
    exclude_name_tokens = [
        "BUSQUEDA_NACIONALIDAD",
        "RESOLUCION_104_NACIONALIDAD",
        "CORRECCION_SIES_120",
        "AUDITORIA_MATCH_RUT",
        "EVIDENCIA_NACIONALIDAD_104",
    ]
    roots = [Path("/Users/alexi/Desktop"), ROOT]
    skip_dirs = {".git", ".venv", "node_modules", "__pycache__", "archive", "backups", "resultados", "build", "dist"}
    files: list[Path] = []
    for rt in roots:
        for dirpath, dirnames, filenames in os.walk(rt):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for name in filenames:
                if not name.lower().endswith((".xlsx", ".xls", ".csv")):
                    continue
                fp = Path(dirpath) / name
                n_full = canon_text(str(fp))
                if any(tok in n_full for tok in exclude_name_tokens):
                    continue
                score = 0
                n = canon_text(fp.name)
                p = canon_text(str(fp.parent))
                for kw in keywords:
                    if kw in n:
                        score += 2
                    if kw in p:
                        score += 1
                if score > 0:
                    files.append(fp)
    files = sorted(set(files))

    probable_doc_cols = set(DOC_KEYS)
    probable_codcli_cols = set(CODCLI_KEYS)

    match_rows: list[dict[str, Any]] = []
    reviewed_rows: list[dict[str, Any]] = []

    for file_path in files:
        ext = file_path.suffix.lower()
        try:
            if ext in {".xlsx", ".xls"}:
                xl = pd.ExcelFile(file_path)
                for sh in xl.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sh, dtype=str, keep_default_na=False).fillna("")
                    if df.empty:
                        continue
                    col_keys = {c: normalize_key(c) for c in df.columns}
                    doc_cols = [c for c, k in col_keys.items() if k in probable_doc_cols]
                    codcli_cols = [c for c, k in col_keys.items() if k in probable_codcli_cols]
                    estado_cols = [c for c, k in col_keys.items() if k in ESTADO_KEYS]
                    actividad_cols = [c for c, k in col_keys.items() if k in ACTIVIDAD_KEYS or "2025" in clean(c)]

                    nac_cols: list[tuple[str, str, str]] = []
                    if len(df.columns) >= 26:
                        z_col = df.columns[25]
                        z_head = canon_text(z_col)
                        if "NACIONALIDAD" in z_head:
                            nac_cols.append((z_col, "Z", "Z"))
                    for i, c in enumerate(df.columns, start=1):
                        head = canon_text(c)
                        if "NACIONALIDAD" in head:
                            letter = get_column_letter(i)
                            if not any(x[0] == c for x in nac_cols):
                                nac_cols.append((c, letter, "HEADER"))

                    reviewed_rows.append({
                        "ARCHIVO": str(file_path),
                        "HOJA": sh,
                        "FILAS": int(len(df)),
                        "COLUMNAS": int(len(df.columns)),
                        "TIENE_COLUMNA_Z": "SI" if len(df.columns) >= 26 else "NO",
                        "HEADER_Z": clean(df.columns[25]) if len(df.columns) >= 26 else "",
                        "COLUMNA_NACIONALIDAD_DETECTADA": "|".join([f"{x[0]}({x[1]})" for x in nac_cols]),
                    })

                    for idx, row in df.iterrows():
                        cell_hits: list[tuple[str, str, str, str]] = []
                        search_cols = doc_cols if doc_cols else list(df.columns)
                        for c in search_cols:
                            raw = clean(row.get(c, ""))
                            if not raw:
                                continue
                            body, dvf, full = split_rut(raw)
                            variants = rut_variants(body, dvf)
                            if not variants:
                                continue
                            matched_cases: set[str] = set()
                            for v in variants:
                                matched_cases |= variant_to_cases.get(v, set())
                            if not matched_cases:
                                continue
                            for case in sorted(matched_cases):
                                cell_hits.append((case, c, raw, "DOC_DIRECTO" if c in doc_cols else "BUSQUEDA_BRUTA"))

                        if not cell_hits:
                            continue

                        codcli = ""
                        for cc in codcli_cols:
                            codcli = clean(row.get(cc, ""))
                            if codcli:
                                break

                        nac_values = []
                        for nc, letter, source in nac_cols:
                            nac_raw = clean(row.get(nc, ""))
                            nac_values.append((nc, letter, source, nac_raw))
                        if not nac_values:
                            nac_values = [("", "", "", "")]

                        estado_obs = ""
                        for ec in estado_cols:
                            estado_obs = clean(row.get(ec, ""))
                            if estado_obs:
                                break
                        actividad_raw = {ac: clean(row.get(ac, "")) for ac in actividad_cols}
                        clas_act_row, actividad_evidencia = activity_2025_from_row(actividad_raw)

                        for case, match_col, rut_raw, tmatch in cell_hits:
                            b, d, f = split_rut(rut_raw)
                            for nc, letter, source, nac_raw in nac_values:
                                match_rows.append({
                                    "CASE_ID": case,
                                    "RUT_DATOS_ALUMNOS": rut_raw,
                                    "RUT_CUERPO_DATOS_ALUMNOS": b,
                                    "DV_DATOS_ALUMNOS": d,
                                    "CODCLI_DATOS_ALUMNOS": codcli,
                                    "NACIONALIDAD_DATOS_ALUMNOS": nac_raw,
                                    "COLUMNA_NACIONALIDAD": nc,
                                    "LETRA_COLUMNA_NACIONALIDAD": letter,
                                    "ESTADO_ACADEMICO_OBSERVADO": estado_obs,
                                    "CLASIFICACION_ACTIVIDAD_2025_FILA": clas_act_row,
                                    "ACTIVIDAD_2025_EVIDENCIA": actividad_evidencia,
                                    "ARCHIVO_FUENTE": str(file_path),
                                    "HOJA_FUENTE": sh,
                                    "FILA_EXCEL": int(idx + 2),
                                    "TIPO_MATCH": tmatch,
                                    "COLUMNA_MATCH_RUT": match_col,
                                    "FUENTE_COLUMNA_NACIONALIDAD": source,
                                })
            else:
                df = read_csv_flexible(file_path)
                if df.empty:
                    reviewed_rows.append({
                        "ARCHIVO": str(file_path),
                        "HOJA": "CSV",
                        "FILAS": 0,
                        "COLUMNAS": 0,
                        "TIENE_COLUMNA_Z": "NO",
                        "HEADER_Z": "",
                        "COLUMNA_NACIONALIDAD_DETECTADA": "",
                    })
                    continue
                col_keys = {c: normalize_key(c) for c in df.columns}
                doc_cols = [c for c, k in col_keys.items() if k in probable_doc_cols]
                codcli_cols = [c for c, k in col_keys.items() if k in probable_codcli_cols]
                estado_cols = [c for c, k in col_keys.items() if k in ESTADO_KEYS]
                actividad_cols = [c for c, k in col_keys.items() if k in ACTIVIDAD_KEYS or "2025" in clean(c)]
                nac_cols = []
                for i, c in enumerate(df.columns, start=1):
                    if "NACIONALIDAD" in canon_text(c):
                        nac_cols.append((c, get_column_letter(i), "HEADER"))
                reviewed_rows.append({
                    "ARCHIVO": str(file_path),
                    "HOJA": "CSV",
                    "FILAS": int(len(df)),
                    "COLUMNAS": int(len(df.columns)),
                    "TIENE_COLUMNA_Z": "NO",
                    "HEADER_Z": "",
                    "COLUMNA_NACIONALIDAD_DETECTADA": "|".join([f"{x[0]}({x[1]})" for x in nac_cols]),
                })
                for idx, row in df.iterrows():
                    search_cols = doc_cols if doc_cols else list(df.columns)
                    found_cases: set[str] = set()
                    match_col = ""
                    rut_raw = ""
                    for c in search_cols:
                        raw = clean(row.get(c, ""))
                        if not raw:
                            continue
                        body, dvf, _ = split_rut(raw)
                        vars_set = rut_variants(body, dvf)
                        for v in vars_set:
                            if v in variant_to_cases:
                                found_cases |= variant_to_cases[v]
                                match_col = c
                                rut_raw = raw
                    if not found_cases:
                        continue
                    codcli = ""
                    for cc in codcli_cols:
                        codcli = clean(row.get(cc, ""))
                        if codcli:
                            break
                    nac_values = [("", "", "", "")]
                    if nac_cols:
                        nac_values = [(nc, letter, src, clean(row.get(nc, ""))) for nc, letter, src in nac_cols]
                    estado_obs = ""
                    for ec in estado_cols:
                        estado_obs = clean(row.get(ec, ""))
                        if estado_obs:
                            break
                    actividad_raw = {ac: clean(row.get(ac, "")) for ac in actividad_cols}
                    clas_act_row, actividad_evidencia = activity_2025_from_row(actividad_raw)
                    b, d, _ = split_rut(rut_raw)
                    for case in sorted(found_cases):
                        for nc, letter, source, nac_raw in nac_values:
                            match_rows.append({
                                "CASE_ID": case,
                                "RUT_DATOS_ALUMNOS": rut_raw,
                                "RUT_CUERPO_DATOS_ALUMNOS": b,
                                "DV_DATOS_ALUMNOS": d,
                                "CODCLI_DATOS_ALUMNOS": codcli,
                                "NACIONALIDAD_DATOS_ALUMNOS": nac_raw,
                                "COLUMNA_NACIONALIDAD": nc,
                                "LETRA_COLUMNA_NACIONALIDAD": letter,
                                "ESTADO_ACADEMICO_OBSERVADO": estado_obs,
                                "CLASIFICACION_ACTIVIDAD_2025_FILA": clas_act_row,
                                "ACTIVIDAD_2025_EVIDENCIA": actividad_evidencia,
                                "ARCHIVO_FUENTE": str(file_path),
                                "HOJA_FUENTE": "CSV",
                                "FILA_EXCEL": int(idx + 2),
                                "TIPO_MATCH": "DOC_DIRECTO" if match_col in doc_cols else "BUSQUEDA_BRUTA",
                                "COLUMNA_MATCH_RUT": match_col,
                                "FUENTE_COLUMNA_NACIONALIDAD": source,
                            })
        except Exception as exc:
            reviewed_rows.append({
                "ARCHIVO": str(file_path),
                "HOJA": "",
                "FILAS": 0,
                "COLUMNAS": 0,
                "TIENE_COLUMNA_Z": "",
                "HEADER_Z": "",
                "COLUMNA_NACIONALIDAD_DETECTADA": f"ERROR:{type(exc).__name__}",
            })

    matches_df = pd.DataFrame(match_rows)
    reviewed_df = pd.DataFrame(reviewed_rows)

    required_match_cols = [
        "NUM_DOCUMENTO_SIES", "DV_SIES", "CODIGO_UNICO", "NOMBRES", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO",
        "RUT_DATOS_ALUMNOS", "RUT_CUERPO_DATOS_ALUMNOS", "DV_DATOS_ALUMNOS", "CODCLI_DATOS_ALUMNOS",
        "NACIONALIDAD_DATOS_ALUMNOS", "COLUMNA_NACIONALIDAD", "LETRA_COLUMNA_NACIONALIDAD", "ARCHIVO_FUENTE",
        "HOJA_FUENTE", "FILA_EXCEL", "TIPO_MATCH", "CLASIFICACION_FINAL",
        "ESTADO_ACADEMICO_OBSERVADO", "CLASIFICACION_ACTIVIDAD_2025_FILA", "ACTIVIDAD_2025_EVIDENCIA",
    ]

    clas_rows = []
    full_match_rows = []
    z_match_rows = []
    for _, prow in pendientes.iterrows():
        case = clean(prow["CASE_ID"])
        subset = matches_df[matches_df["CASE_ID"].eq(case)].copy() if not matches_df.empty else pd.DataFrame()
        subset_nac = subset[subset["NACIONALIDAD_DATOS_ALUMNOS"].map(clean).ne("")] if not subset.empty else pd.DataFrame()
        nac_norms = set(subset_nac["NACIONALIDAD_DATOS_ALUMNOS"].map(canon_text).tolist()) if not subset_nac.empty else set()
        if subset.empty:
            clas = "SIN_MATCH_DATOS_ALUMNOS"
        elif subset_nac.empty:
            clas = "MATCH_SIN_NACIONALIDAD"
        elif len(nac_norms) > 1:
            clas = "CONFLICTO_NACIONALIDAD"
        else:
            only = next(iter(nac_norms))
            if "CHIL" in only:
                clas = "NACIONALIDAD_OBSERVADA_CHILENA"
            else:
                clas = "NACIONALIDAD_OBSERVADA_EXTRANJERA"

        row_base = {
            "CASE_ID": case,
            "NUM_DOCUMENTO_SIES": clean(prow.get("NUM_DOCUMENTO", "")),
            "DV_SIES": clean(prow.get("DV", "")),
            "CODIGO_UNICO": clean(prow.get("CODIGO_UNICO", "")),
            "NOMBRES": clean(prow.get("NOMBRES", "")),
            "PRIMER_APELLIDO": clean(prow.get("PRIMER_APELLIDO", "")),
            "SEGUNDO_APELLIDO": clean(prow.get("SEGUNDO_APELLIDO", "")),
            "CLASIFICACION_FINAL": clas,
        }
        clas_rows.append(row_base)

        if subset.empty:
            full_match_rows.append({
                **row_base,
                "RUT_DATOS_ALUMNOS": "",
                "RUT_CUERPO_DATOS_ALUMNOS": "",
                "DV_DATOS_ALUMNOS": "",
                "CODCLI_DATOS_ALUMNOS": "",
                "NACIONALIDAD_DATOS_ALUMNOS": "",
                "COLUMNA_NACIONALIDAD": "",
                "LETRA_COLUMNA_NACIONALIDAD": "",
                "ARCHIVO_FUENTE": "",
                "HOJA_FUENTE": "",
                "FILA_EXCEL": "",
                "TIPO_MATCH": "",
            })
            continue

        for _, m in subset.iterrows():
            merged = {
                **row_base,
                "RUT_DATOS_ALUMNOS": clean(m.get("RUT_DATOS_ALUMNOS", "")),
                "RUT_CUERPO_DATOS_ALUMNOS": clean(m.get("RUT_CUERPO_DATOS_ALUMNOS", "")),
                "DV_DATOS_ALUMNOS": clean(m.get("DV_DATOS_ALUMNOS", "")),
                "CODCLI_DATOS_ALUMNOS": clean(m.get("CODCLI_DATOS_ALUMNOS", "")),
                "NACIONALIDAD_DATOS_ALUMNOS": clean(m.get("NACIONALIDAD_DATOS_ALUMNOS", "")),
                "COLUMNA_NACIONALIDAD": clean(m.get("COLUMNA_NACIONALIDAD", "")),
                "LETRA_COLUMNA_NACIONALIDAD": clean(m.get("LETRA_COLUMNA_NACIONALIDAD", "")),
                "ARCHIVO_FUENTE": clean(m.get("ARCHIVO_FUENTE", "")),
                "HOJA_FUENTE": clean(m.get("HOJA_FUENTE", "")),
                "FILA_EXCEL": clean(m.get("FILA_EXCEL", "")),
                "TIPO_MATCH": clean(m.get("TIPO_MATCH", "")),
                "ESTADO_ACADEMICO_OBSERVADO": clean(m.get("ESTADO_ACADEMICO_OBSERVADO", "")),
                "CLASIFICACION_ACTIVIDAD_2025_FILA": clean(m.get("CLASIFICACION_ACTIVIDAD_2025_FILA", "")),
                "ACTIVIDAD_2025_EVIDENCIA": clean(m.get("ACTIVIDAD_2025_EVIDENCIA", "")),
            }
            full_match_rows.append(merged)
            if clean(m.get("LETRA_COLUMNA_NACIONALIDAD", "")) == "Z":
                z_match_rows.append(merged)

    clas_df = pd.DataFrame(clas_rows)
    match_full_df = pd.DataFrame(full_match_rows)
    if match_full_df.empty:
        match_full_df = pd.DataFrame(columns=required_match_cols)
    match_full_df = match_full_df[required_match_cols].copy()
    match_z_df = pd.DataFrame(z_match_rows)
    if match_z_df.empty:
        match_z_df = pd.DataFrame(columns=required_match_cols)
    else:
        match_z_df = match_z_df[required_match_cols].copy()

    chilena_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("NACIONALIDAD_OBSERVADA_CHILENA")].copy()
    extranjera_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("NACIONALIDAD_OBSERVADA_EXTRANJERA")].copy()
    sin_match_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("SIN_MATCH_DATOS_ALUMNOS")].copy()
    sin_nac_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("MATCH_SIN_NACIONALIDAD")].copy()
    conflictos_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("CONFLICTO_NACIONALIDAD")].copy()

    if int(l120["KEY_DOC"].nunique()) != 120:
        bloqueos.append("LISTADO_SIES_NO_TIENE_120_CASOS_UNICOS")
    if len(pendientes) != 104:
        bloqueos.append("PENDIENTES_DISTINTOS_104")

    # Forzar caso especial TVS 26481336 como chilena observada manual
    clas_df.loc[clas_df["NUM_DOCUMENTO_SIES"].eq("26481336"), "CLASIFICACION_FINAL"] = "NACIONALIDAD_OBSERVADA_CHILENA_TVS"

    chilena_df = clas_df[clas_df["CLASIFICACION_FINAL"].isin(["NACIONALIDAD_OBSERVADA_CHILENA", "NACIONALIDAD_OBSERVADA_CHILENA_TVS"])].copy()
    extranjera_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("NACIONALIDAD_OBSERVADA_EXTRANJERA")].copy()
    sin_match_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("SIN_MATCH_DATOS_ALUMNOS")].copy()
    sin_nac_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("MATCH_SIN_NACIONALIDAD")].copy()
    conflictos_df = clas_df[clas_df["CLASIFICACION_FINAL"].eq("CONFLICTO_NACIONALIDAD")].copy()

    if not args.generar_carga_104_vigencia_0:
        if len(chilena_df) > 0:
            bloqueos.append("NO_GENERAR_CSV_POR_CHILENA_OBSERVADA")
        if len(sin_match_df) > 0 or len(sin_nac_df) > 0:
            bloqueos.append("NO_GENERAR_CSV_POR_FALTA_NACIONALIDAD")
        if len(conflictos_df) > 0:
            bloqueos.append("NO_GENERAR_CSV_POR_CONFLICTO_NACIONALIDAD")

        resumen = pd.DataFrame([{
            "PROCESO": "Estudiantes Extranjeros Regulares SIES 2026",
            "ANIO_DATOS": clean(args.anio_datos),
            "CASOS_SIES": int(len(c120)),
            "CASOS_UNICOS_SIES": int(l120["KEY_DOC"].nunique()),
            "YA_CARGADOS": int(len(ya_cargados)),
            "PENDIENTES": int(len(pendientes)),
            "MATCH_EN_DATOS_ALUMNOS": int(len(clas_df[clas_df["CLASIFICACION_FINAL"].ne("SIN_MATCH_DATOS_ALUMNOS")])),
            "CON_NACIONALIDAD_OBSERVADA": int(len(chilena_df) + len(extranjera_df)),
            "NACIONALIDAD_OBSERVADA_CHILENA": int(len(chilena_df)),
            "NACIONALIDAD_OBSERVADA_EXTRANJERA": int(len(extranjera_df)),
            "SIN_MATCH_DATOS_ALUMNOS": int(len(sin_match_df)),
            "MATCH_SIN_NACIONALIDAD": int(len(sin_nac_df)),
            "CONFLICTO_NACIONALIDAD": int(len(conflictos_df)),
            "CSV_GENERADO": "NO",
            "ESTADO_FINAL": "DIAGNOSTICO_CORREGIDO_CON_EVIDENCIA_DATOS_ALUMNOS",
        }])

        out_01 = out_dir / "01_RESUMEN.xlsx"
        out_02 = out_dir / "02_104_PENDIENTES_BASE.xlsx"
        out_03 = out_dir / "03_MATCH_DATOS_ALUMNOS_COLUMNA_Z.xlsx"
        out_04 = out_dir / "04_EVIDENCIA_NACIONALIDAD_104.xlsx"
        out_05 = out_dir / "05_AUDITORIA_MATCH_RUT.csv"
        out_06 = out_dir / "06_RESUMEN_EJECUCION.json"
        out_07 = out_dir / "07_REPORTE_PARA_SIES.md"
        out_08 = out_dir / "08_HASHES.sha256"

        write_excel(out_01, {
            "RESUMEN": resumen,
            "120_SIES": c120,
            "16_YA_CARGADOS": ya_cargados,
            "104_PENDIENTES": pendientes,
        })
        write_excel(out_02, {"104_PENDIENTES": pendientes})
        write_excel(out_03, {"MATCH_COLUMNA_Z": match_z_df})
        write_excel(out_04, {
            "RESUMEN": resumen,
            "104_PENDIENTES": pendientes,
            "MATCHES_DATOS_ALUMNOS": match_full_df,
            "CHILENA_OBSERVADA": chilena_df,
            "EXTRANJERA_OBSERVADA": extranjera_df,
            "SIN_MATCH": sin_match_df,
            "MATCH_SIN_NACIONALIDAD": sin_nac_df,
            "CONFLICTOS": conflictos_df,
            "ARCHIVOS_REVISADOS": reviewed_df,
        })
        write_csv(match_full_df, out_05)

        resumen_json = {
            "timestamp": ts,
            "proceso": "Estudiantes Extranjeros Regulares SIES 2026",
            "anio_datos": clean(args.anio_datos),
            "script": str(script_path),
            "fuentes": {
                "listado_sies_120": str(listado_src),
                "precarga_oficial": str(precarga_path),
                "csv_previo": str(csv_prev_path),
                "busqueda_raices": ["/Users/alexi/Desktop", str(ROOT)],
            },
            "hashes_fuentes": source_hashes,
            "conteos": resumen.iloc[0].to_dict(),
            "bloqueos": bloqueos,
            "csv_generado": "NO",
            "estado": "DIAGNOSTICO_CORREGIDO_CON_EVIDENCIA_DATOS_ALUMNOS",
            "salidas": {
                "01_RESUMEN": str(out_01),
                "02_104_PENDIENTES_BASE": str(out_02),
                "03_MATCH_DATOS_ALUMNOS_COLUMNA_Z": str(out_03),
                "04_EVIDENCIA_NACIONALIDAD_104": str(out_04),
                "05_AUDITORIA_MATCH_RUT": str(out_05),
                "06_RESUMEN_EJECUCION": str(out_06),
                "07_REPORTE_PARA_SIES": str(out_07),
                "08_HASHES": str(out_08),
            },
        }
        out_06.write_text(json.dumps(resumen_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        report_lines = [
            "# Reporte para SIES - Diagnostico corregido con Datos Alumnos",
            "",
            "## Resultado del contraste 120 casos",
            f"- Total informado por SIES: {len(c120)}.",
            f"- Ya cargados con VIGENCIA=0: {len(ya_cargados)}.",
            f"- Pendientes: {len(pendientes)}.",
            "",
            "## Revisión de nacionalidad observada en Datos Alumnos",
            "Se realizó búsqueda directa por RUT con y sin DV (incluyendo formatos con puntos y guion) en archivos de Datos Alumnos.",
            f"- NACIONALIDAD_OBSERVADA_CHILENA: {len(chilena_df)}.",
            f"- NACIONALIDAD_OBSERVADA_EXTRANJERA: {len(extranjera_df)}.",
            f"- SIN_MATCH_DATOS_ALUMNOS: {len(sin_match_df)}.",
            f"- MATCH_SIN_NACIONALIDAD: {len(sin_nac_df)}.",
            f"- CONFLICTO_NACIONALIDAD: {len(conflictos_df)}.",
            "",
            "## Estado operativo",
            "No se genera CSV de carga en este diagnóstico, por presencia de nacionalidad chilena observada y/o faltantes/conflictos de nacionalidad en pendientes.",
        ]
        out_07.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        hash_targets = [out_01, out_02, out_03, out_04, out_05, out_06, out_07]
        out_08.write_text("\n".join([f"{sha256(p)}  {p}" for p in hash_targets]) + "\n", encoding="utf-8")

        print(json.dumps(resumen_json, ensure_ascii=False, indent=2))
        return 2

    # Generation branch: 104 with NACIONALIDAD=38 and VIGENCIA=0 plus auditable rationale.
    carga_cols = COLUMNAS_SIES_REGULARES.copy()
    carga_104 = pendientes[carga_cols].copy()
    for col in carga_cols:
        carga_104[col] = carga_104[col].map(clean)
    carga_104["FECHA_NACIMIENTO"] = carga_104["FECHA_NACIMIENTO"].map(normalize_date)
    carga_104["NACIONALIDAD"] = "38"
    carga_104["VIGENCIA"] = "0"

    mask_res_vacia = carga_104["TIPO_RESIDENCIA_ESTUDIANTE"].map(clean).eq("")
    carga_104.loc[mask_res_vacia, "TIPO_RESIDENCIA_ESTUDIANTE"] = "0"
    mask_origen_blank = carga_104["TIPO_RESIDENCIA_ESTUDIANTE"].isin(["0", "1"])
    carga_104.loc[mask_origen_blank, "PAIS_DE_ORIGEN"] = ""

    evidencia_nac_rows: list[dict[str, Any]] = []
    evidencia_estado_rows: list[dict[str, Any]] = []
    auditoria_rows: list[dict[str, Any]] = []
    clas_prev_map = {clean(r.get("CASE_ID", "")): clean(r.get("CLASIFICACION_FINAL", "")) for _, r in clas_df.iterrows()}

    for _, row in pendientes.iterrows():
        case_id = clean(row.get("CASE_ID", ""))
        num_doc = clean(row.get("NUM_DOCUMENTO", ""))
        dv = clean(row.get("DV", ""))
        codigo_unico = clean(row.get("CODIGO_UNICO", ""))

        case_matches = match_full_df[match_full_df["CASE_ID"].eq(case_id)].copy() if "CASE_ID" in match_full_df.columns else pd.DataFrame()
        best = select_best_match_row(case_matches)

        nac_vals = set(case_matches["NACIONALIDAD_DATOS_ALUMNOS"].map(clean).tolist()) if not case_matches.empty else set()
        clas_nac, nac_value = classify_nacionalidad_observada(nac_vals)
        clas_prev = clas_prev_map.get(case_id, "")
        if clas_prev in {"NACIONALIDAD_OBSERVADA_CHILENA", "NACIONALIDAD_OBSERVADA_EXTRANJERA"}:
            clas_nac = clas_prev
            if not nac_value:
                nac_value = "CHILENA" if clas_prev == "NACIONALIDAD_OBSERVADA_CHILENA" else "EXTRANJERA"

        estado_values = [clean(x) for x in case_matches.get("ESTADO_ACADEMICO_OBSERVADO", pd.Series(dtype=str)).tolist() if clean(x)]
        estado_obs = clean(best.get("ESTADO_ACADEMICO_OBSERVADO", "")) if best is not None else ""
        if not estado_obs and estado_values:
            estado_obs = estado_values[0]
        clas_estado = classify_estado_academico(estado_obs)

        actividad_classes = [clean(x) for x in case_matches.get("CLASIFICACION_ACTIVIDAD_2025_FILA", pd.Series(dtype=str)).tolist() if clean(x)]
        if best is not None and clean(best.get("CLASIFICACION_ACTIVIDAD_2025_FILA", "")):
            clas_actividad = clean(best.get("CLASIFICACION_ACTIVIDAD_2025_FILA", ""))
        elif "ACTIVIDAD_2025_OBSERVADA" in actividad_classes:
            clas_actividad = "ACTIVIDAD_2025_OBSERVADA"
        elif "SIN_ACTIVIDAD_2025_OBSERVADA" in actividad_classes:
            clas_actividad = "SIN_ACTIVIDAD_2025_OBSERVADA"
        else:
            clas_actividad = "ACTIVIDAD_2025_NO_DETERMINADA"

        actividad_obs = clean(best.get("ACTIVIDAD_2025_EVIDENCIA", "")) if best is not None else ""
        if not actividad_obs and not case_matches.empty:
            evidencias = [clean(x) for x in case_matches.get("ACTIVIDAD_2025_EVIDENCIA", pd.Series(dtype=str)).tolist() if clean(x)]
            actividad_obs = " | ".join(evidencias[:3])

        archivo_nac = clean(best.get("ARCHIVO_FUENTE", "")) if best is not None else ""
        hoja_nac = clean(best.get("HOJA_FUENTE", "")) if best is not None else ""
        fila_nac = clean(best.get("FILA_EXCEL", "")) if best is not None else ""
        col_nac = clean(best.get("COLUMNA_NACIONALIDAD", "")) if best is not None else ""
        letra_nac = clean(best.get("LETRA_COLUMNA_NACIONALIDAD", "")) if best is not None else ""
        codcli_obs = clean(best.get("CODCLI_DATOS_ALUMNOS", "")) if best is not None else ""
        rut_obs = clean(best.get("RUT_DATOS_ALUMNOS", "")) if best is not None else ""

        archivo_estado = archivo_nac
        hoja_estado = hoja_nac
        fila_estado = fila_nac

        fuente_decision = "Regla institucional de descarte de precarga Extranjeros Regulares"
        observacion_operativa = ""

        if re.sub(r"[^0-9]", "", num_doc) == "26481336":
            clas_nac = "NACIONALIDAD_OBSERVADA_CHILENA_TVS"
            nac_value = "CHILENA"
            fuente_decision = "Decisión operativa manual / TVS observado"
            observacion_operativa = "TVS observado; se completa como Chilena para carga de descarte VIGENCIA=0."

        has_complementary = bool(estado_obs or actividad_obs)
        motivo = motivo_vigencia_0(num_doc, clas_nac, clas_estado, clas_actividad, has_complementary)

        evidencia_parts: list[str] = []
        if letra_nac == "Z":
            evidencia_parts.append("Datos Alumnos columna Z NACIONALIDAD")
        elif col_nac:
            evidencia_parts.append(f"Datos Alumnos columna {col_nac} NACIONALIDAD")
        if estado_obs:
            evidencia_parts.append(f"Datos Alumnos ESTADO_ACADEMICO={estado_obs}")
        if actividad_obs:
            evidencia_parts.append(f"Evidencia actividad/asignaturas 2025: {actividad_obs}")
        if archivo_nac:
            evidencia_parts.append(f"Fuente: {Path(archivo_nac).name} hoja {hoja_nac} fila {fila_nac}")
        if fuente_decision.startswith("Decisión operativa manual"):
            evidencia_parts.append("Decisión operativa manual TVS observado")
        evidencia_usada = " | ".join([p for p in evidencia_parts if clean(p)])
        if not evidencia_usada:
            evidencia_usada = "Sin evidencia documental concluyente; se aplica descarte de precarga según regla institucional del proceso."

        nacionalidad_valor_observada = nac_value if nac_value else ""
        if not nacionalidad_valor_observada and clas_nac == "NACIONALIDAD_OBSERVADA_CHILENA":
            nacionalidad_valor_observada = "CHILENA"

        evidencia_nac_rows.append({
            "CASE_ID": case_id,
            "NUM_DOCUMENTO": num_doc,
            "DV": dv,
            "CODIGO_UNICO": codigo_unico,
            "NOMBRES": clean(row.get("NOMBRES", "")),
            "PRIMER_APELLIDO": clean(row.get("PRIMER_APELLIDO", "")),
            "SEGUNDO_APELLIDO": clean(row.get("SEGUNDO_APELLIDO", "")),
            "NACIONALIDAD_VALOR_OBSERVADA": nacionalidad_valor_observada,
            "CLASIFICACION_NACIONALIDAD": clas_nac,
            "NACIONALIDAD_CODIGO_USADO": "38",
            "ARCHIVO_FUENTE_NACIONALIDAD": archivo_nac,
            "HOJA_FUENTE_NACIONALIDAD": hoja_nac,
            "FILA_FUENTE_NACIONALIDAD": fila_nac,
            "COLUMNA_NACIONALIDAD": col_nac,
            "LETRA_COLUMNA_NACIONALIDAD": letra_nac,
            "EVIDENCIA_USADA": evidencia_usada,
        })

        evidencia_estado_rows.append({
            "CASE_ID": case_id,
            "NUM_DOCUMENTO": num_doc,
            "DV": dv,
            "CODIGO_UNICO": codigo_unico,
            "ESTADO_ACADEMICO_OBSERVADO": estado_obs,
            "CLASIFICACION_ESTADO_ACADEMICO": clas_estado,
            "ACTIVIDAD_2025_OBSERVADA": actividad_obs,
            "CLASIFICACION_ACTIVIDAD_2025": clas_actividad,
            "CODCLI_DATOS_ALUMNOS": codcli_obs,
            "RUT_DATOS_ALUMNOS": rut_obs,
            "ARCHIVO_FUENTE_ESTADO": archivo_estado,
            "HOJA_FUENTE_ESTADO": hoja_estado,
            "FILA_FUENTE_ESTADO": fila_estado,
        })

        auditoria_rows.append({
            "NUM_DOCUMENTO": num_doc,
            "DV": dv,
            "CODIGO_UNICO": codigo_unico,
            "NOMBRES": clean(row.get("NOMBRES", "")),
            "PRIMER_APELLIDO": clean(row.get("PRIMER_APELLIDO", "")),
            "SEGUNDO_APELLIDO": clean(row.get("SEGUNDO_APELLIDO", "")),
            "NACIONALIDAD_FINAL": "38",
            "VIGENCIA_FINAL": "0",
            "ESTADO_ACADEMICO_OBSERVADO": estado_obs,
            "ACTIVIDAD_2025_OBSERVADA": actividad_obs,
            "CLASIFICACION_NACIONALIDAD": clas_nac,
            "CLASIFICACION_ESTADO_ACADEMICO": clas_estado,
            "CLASIFICACION_ACTIVIDAD_2025": clas_actividad,
            "MOTIVO_VIGENCIA_0": motivo,
            "EVIDENCIA_USADA": evidencia_usada,
            "FUENTE_DECISION": fuente_decision,
            "OBSERVACION_OPERATIVA": observacion_operativa,
            "NACIONALIDAD_VALOR_OBSERVADA": nacionalidad_valor_observada,
            "NACIONALIDAD_CODIGO_USADO": "38",
            "CODCLI_DATOS_ALUMNOS": codcli_obs,
            "RUT_DATOS_ALUMNOS": rut_obs,
            "ARCHIVO_FUENTE_NACIONALIDAD": archivo_nac,
            "HOJA_FUENTE_NACIONALIDAD": hoja_nac,
            "FILA_FUENTE_NACIONALIDAD": fila_nac,
            "ARCHIVO_FUENTE_ESTADO": archivo_estado,
            "HOJA_FUENTE_ESTADO": hoja_estado,
            "FILA_FUENTE_ESTADO": fila_estado,
        })

    evidencia_nac_df = pd.DataFrame(evidencia_nac_rows)
    evidencia_estado_df = pd.DataFrame(evidencia_estado_rows)
    auditoria_full_df = pd.DataFrame(auditoria_rows)

    auditoria_cols = [
        "NUM_DOCUMENTO",
        "DV",
        "CODIGO_UNICO",
        "NOMBRES",
        "PRIMER_APELLIDO",
        "SEGUNDO_APELLIDO",
        "NACIONALIDAD_FINAL",
        "VIGENCIA_FINAL",
        "ESTADO_ACADEMICO_OBSERVADO",
        "ACTIVIDAD_2025_OBSERVADA",
        "CLASIFICACION_NACIONALIDAD",
        "CLASIFICACION_ESTADO_ACADEMICO",
        "CLASIFICACION_ACTIVIDAD_2025",
        "MOTIVO_VIGENCIA_0",
        "EVIDENCIA_USADA",
        "FUENTE_DECISION",
        "OBSERVACION_OPERATIVA",
    ]
    auditoria_df = auditoria_full_df[auditoria_cols].copy()

    out_01 = out_dir / "01_RESUMEN_GENERACION_CARGA.xlsx"
    out_02 = out_dir / "02_CARGA_104_CON_TITULOS.xlsx"
    out_03 = out_dir / "03_CARGA_104_FORMATO_SIES.csv"
    out_04 = out_dir / "04_AUDITORIA_DECISIONES_104.csv"
    out_05 = out_dir / "05_VALIDACION_CSV_SIES.csv"
    out_06 = out_dir / "06_RESUMEN_EJECUCION.json"
    out_07 = out_dir / "07_HASHES.sha256"
    out_08 = out_dir / "08_REPORTE_PARA_SIES.md"

    write_csv(auditoria_df, out_04)

    carga_titulos = carga_104[carga_cols].copy()
    carga_titulos = carga_titulos.merge(
        auditoria_full_df,
        on=["NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "NOMBRES", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO"],
        how="left",
        validate="one_to_one",
    )

    ordered_titulo_cols = carga_cols + [
        "CLASIFICACION_NACIONALIDAD",
        "CLASIFICACION_ESTADO_ACADEMICO",
        "CLASIFICACION_ACTIVIDAD_2025",
        "MOTIVO_VIGENCIA_0",
        "EVIDENCIA_USADA",
        "NACIONALIDAD_VALOR_OBSERVADA",
        "NACIONALIDAD_CODIGO_USADO",
        "ESTADO_ACADEMICO_OBSERVADO",
        "ACTIVIDAD_2025_OBSERVADA",
        "CODCLI_DATOS_ALUMNOS",
        "RUT_DATOS_ALUMNOS",
        "ARCHIVO_FUENTE_NACIONALIDAD",
        "HOJA_FUENTE_NACIONALIDAD",
        "FILA_FUENTE_NACIONALIDAD",
        "ARCHIVO_FUENTE_ESTADO",
        "HOJA_FUENTE_ESTADO",
        "FILA_FUENTE_ESTADO",
        "OBSERVACION_OPERATIVA",
    ]
    for col in ordered_titulo_cols:
        if col not in carga_titulos.columns:
            carga_titulos[col] = ""
    carga_titulos = carga_titulos[ordered_titulo_cols].copy()

    estado_summary = (
        auditoria_df["CLASIFICACION_ESTADO_ACADEMICO"].value_counts(dropna=False).rename_axis("CLASIFICACION").reset_index(name="CANTIDAD")
        if not auditoria_df.empty else pd.DataFrame(columns=["CLASIFICACION", "CANTIDAD"])
    )
    actividad_summary = (
        auditoria_df["CLASIFICACION_ACTIVIDAD_2025"].value_counts(dropna=False).rename_axis("CLASIFICACION").reset_index(name="CANTIDAD")
        if not auditoria_df.empty else pd.DataFrame(columns=["CLASIFICACION", "CANTIDAD"])
    )

    resumen_carga = pd.DataFrame([{
        "PROCESO": "Estudiantes Extranjeros Regulares SIES 2026",
        "ANIO_DATOS": clean(args.anio_datos),
        "CASOS_SIES": int(len(c120)),
        "YA_CARGADOS": int(len(ya_cargados)),
        "PENDIENTES_INCLUIDOS_CSV": int(len(carga_titulos)),
        "NACIONALIDAD_38_FILAS": int(carga_titulos["NACIONALIDAD"].eq("38").sum()),
        "VIGENCIA_0_FILAS": int(carga_titulos["VIGENCIA"].eq("0").sum()),
        "CASO_TVS_26481336": int((carga_titulos["NUM_DOCUMENTO"].map(lambda x: re.sub(r"[^0-9]", "", clean(x))).eq("26481336")).sum()),
    }])

    write_sies_csv_cp1252_no_final_newline(carga_104[carga_cols], out_03)
    physical = detect_csv_physical(out_03)
    reread = pd.read_csv(out_03, sep=";", header=None, encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    reread.columns = carga_cols
    dup_count = int(reread.duplicated(subset=["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "CODIGO_UNICO"], keep=False).sum())

    csv_lines = out_03.read_bytes().splitlines()
    delimitadores_ok = all(line.decode("cp1252", errors="replace").count(";") == 19 for line in csv_lines)
    vigencia_ok = int(reread["VIGENCIA"].eq("0").sum()) == 104
    nacionalidad_no_vacia_ok = int(reread["NACIONALIDAD"].map(clean).eq("").sum()) == 0
    nacionalidad_38_ok = int(reread["NACIONALIDAD"].eq("38").sum()) == 104
    motivo_ok = int(auditoria_df["MOTIVO_VIGENCIA_0"].map(clean).eq("").sum()) == 0
    evidencia_ok = int(auditoria_df["EVIDENCIA_USADA"].map(clean).eq("").sum()) == 0
    tvs_mask = auditoria_df["NUM_DOCUMENTO"].map(lambda x: re.sub(r"[^0-9]", "", clean(x))).eq("26481336")
    tvs_ok = False
    if int(tvs_mask.sum()) == 1:
        tvs_row = auditoria_df[tvs_mask].iloc[0]
        tvs_ok = (
            clean(tvs_row.get("CLASIFICACION_NACIONALIDAD", "")) == "NACIONALIDAD_OBSERVADA_CHILENA_TVS"
            and "OPERATIVA MANUAL" in canon_text(tvs_row.get("FUENTE_DECISION", ""))
            and "TVS OBSERVADO" in canon_text(tvs_row.get("OBSERVACION_OPERATIVA", ""))
        )

    validation_rows = [
        {"REGLA": "FILAS_EXACTAS_104", "OK": "SI" if len(reread) == 104 else "NO", "DETALLE": str(len(reread))},
        {"REGLA": "COLUMNAS_EXACTAS_20", "OK": "SI" if reread.shape[1] == 20 else "NO", "DETALLE": str(reread.shape[1])},
        {"REGLA": "SIN_ENCABEZADO", "OK": "SI" if physical["encabezado"] == "NO" else "NO", "DETALLE": physical["encabezado"]},
        {"REGLA": "DELIMITADORES_19_POR_FILA", "OK": "SI" if delimitadores_ok else "NO", "DETALLE": str(delimitadores_ok)},
        {"REGLA": "VIGENCIA_TODO_0", "OK": "SI" if vigencia_ok else "NO", "DETALLE": str(int(reread["VIGENCIA"].eq("0").sum()))},
        {"REGLA": "NACIONALIDAD_NO_VACIA", "OK": "SI" if nacionalidad_no_vacia_ok else "NO", "DETALLE": str(int(reread["NACIONALIDAD"].map(clean).eq("").sum()))},
        {"REGLA": "NACIONALIDAD_TODO_38", "OK": "SI" if nacionalidad_38_ok else "NO", "DETALLE": str(int(reread["NACIONALIDAD"].eq("38").sum()))},
        {"REGLA": "SIN_BOM", "OK": "SI" if physical["bom"] == "NO" else "NO", "DETALLE": physical["bom"]},
        {"REGLA": "SIN_LINEA_FINAL_VACIA", "OK": "SI" if physical["termina_con_salto"] == "NO" else "NO", "DETALLE": physical["termina_con_salto"]},
        {"REGLA": "RELECTURA_CP1252_OK", "OK": "SI" if len(reread) == 104 else "NO", "DETALLE": "cp1252;"},
        {"REGLA": "SIN_DUPLICADOS_DOC_CODIGO", "OK": "SI" if dup_count == 0 else "NO", "DETALLE": str(dup_count)},
        {"REGLA": "CASO_26481336_TVS_OBSERVADO", "OK": "SI" if tvs_ok else "NO", "DETALLE": str(int(tvs_mask.sum()))},
        {"REGLA": "MOTIVO_VIGENCIA_0_COMPLETO", "OK": "SI" if motivo_ok else "NO", "DETALLE": str(int(auditoria_df["MOTIVO_VIGENCIA_0"].map(clean).eq("").sum()))},
        {"REGLA": "EVIDENCIA_USADA_COMPLETA", "OK": "SI" if evidencia_ok else "NO", "DETALLE": str(int(auditoria_df["EVIDENCIA_USADA"].map(clean).eq("").sum()))},
    ]
    valid_df = pd.DataFrame(validation_rows)
    write_csv(valid_df, out_05)

    failed = valid_df[valid_df["OK"].ne("SI")].copy()
    if not failed.empty:
        bloqueos.extend([f"VALIDACION_FALLA:{x}" for x in failed["REGLA"].tolist()])

    write_excel(out_02, {
        "RESUMEN": resumen_carga,
        "CARGA_104_CON_TITULOS": carga_titulos,
        "EVIDENCIA_NACIONALIDAD": evidencia_nac_df,
        "EVIDENCIA_ESTADO_ACTIVIDAD": evidencia_estado_df,
        "CASO_TVS_OBSERVADO": auditoria_df[tvs_mask].copy(),
        "AUDITORIA_DECISIONES": auditoria_df,
        "VALIDACION_CSV": valid_df,
        "ARCHIVOS_REVISADOS": reviewed_df,
    })
    write_excel(out_01, {
        "RESUMEN": resumen_carga,
        "ESTADOS_ACADEMICOS": estado_summary,
        "ACTIVIDAD_2025": actividad_summary,
    })

    desktop_xlsx = Path.home() / f"Desktop/CARGA_104_EXTRANJEROS_VIGENCIA_0_CON_TITULOS_AUDITADO_{ts}.xlsx"
    desktop_csv = Path.home() / f"Desktop/CARGA_104_EXTRANJEROS_VIGENCIA_0_FORMATO_SIES_AUDITADO_{ts}.csv"
    shutil.copy2(out_02, desktop_xlsx)
    shutil.copy2(out_03, desktop_csv)

    csv_hash = sha256(out_03)
    chilena_count = int(auditoria_df["CLASIFICACION_NACIONALIDAD"].eq("NACIONALIDAD_OBSERVADA_CHILENA").sum())
    chilena_tvs_count = int(auditoria_df["CLASIFICACION_NACIONALIDAD"].eq("NACIONALIDAD_OBSERVADA_CHILENA_TVS").sum())
    summary_json = {
        "timestamp": ts,
        "proceso": "Estudiantes Extranjeros Regulares SIES 2026",
        "anio_datos": clean(args.anio_datos),
        "script": str(script_path),
        "fuentes": {
            "listado_sies_120": str(listado_src),
            "precarga_oficial": str(precarga_path),
            "csv_previo": str(csv_prev_path),
            "busqueda_raices": ["/Users/alexi/Desktop", str(ROOT)],
        },
        "hashes_fuentes": source_hashes,
        "conteos": {
            "casos_sies": int(len(c120)),
            "ya_cargados": int(len(ya_cargados)),
            "pendientes_cargados": int(len(carga_104)),
            "nacionalidad_38": int(carga_104["NACIONALIDAD"].eq("38").sum()),
            "vigencia_0": int(carga_104["VIGENCIA"].eq("0").sum()),
            "nacionalidad_observada_chilena": chilena_count,
            "nacionalidad_observada_chilena_tvs": chilena_tvs_count,
            "caso_tvs_26481336": int(tvs_mask.sum()),
        },
        "resumen_estados_academicos": estado_summary.to_dict(orient="records"),
        "resumen_actividad_2025": actividad_summary.to_dict(orient="records"),
        "csv_hash_sha256": csv_hash,
        "csv_generado": "SI" if failed.empty else "NO",
        "estado": "GENERACION_CARGA_104_VIGENCIA_0_COMPLETA" if failed.empty else "BLOQUEADO_POR_VALIDACION_CSV",
        "bloqueos": bloqueos,
        "salidas": {
            "01_RESUMEN_GENERACION_CARGA": str(out_01),
            "02_CARGA_104_CON_TITULOS": str(out_02),
            "03_CARGA_104_FORMATO_SIES": str(out_03),
            "04_AUDITORIA_DECISIONES_104": str(out_04),
            "05_VALIDACION_CSV_SIES": str(out_05),
            "06_RESUMEN_EJECUCION": str(out_06),
            "07_HASHES": str(out_07),
            "08_REPORTE_PARA_SIES": str(out_08),
            "desktop_xlsx": str(desktop_xlsx),
            "desktop_csv": str(desktop_csv),
        },
    }
    out_06.write_text(json.dumps(summary_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Reporte para SIES - Carga correctiva 104 registros auditada",
        "",
        "- SIES informó 120 casos.",
        "- 16 ya estaban cargados con VIGENCIA=0.",
        "- Se generó archivo correctivo solo con los 104 pendientes.",
        "- Los 104 se informan con VIGENCIA=0 para descarte de precarga.",
        "- La VIGENCIA=0 no proviene directamente de un campo de Datos Alumnos.",
        "- La VIGENCIA=0 corresponde a la decisión de descartar del proceso de Extranjeros Regulares.",
        "- La decisión se fundamenta en:",
        f"  - nacionalidad chilena observada en Datos Alumnos para {chilena_count} casos;",
        "  - TVS observado para 26481336;",
        "  - estado académico/actividad 2025 como evidencia complementaria cuando existe.",
        "- El CSV no incorpora estudiantes extranjeros vigentes; solo informa registros de descarte de precarga.",
    ]
    out_08.write_text("\n".join(report) + "\n", encoding="utf-8")

    hash_targets = [out_01, out_02, out_03, out_04, out_05, out_06, out_08]
    out_07.write_text("\n".join([f"{sha256(p)}  {p}" for p in hash_targets]) + "\n", encoding="utf-8")

    print(json.dumps(summary_json, ensure_ascii=False, indent=2))
    return 0 if failed.empty else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Proceso Estudiantes Extranjeros Regulares 2025 - SIES 2026"
    )
    parser.add_argument("--modo", choices=["fase06", "final", "sies120"], default="fase06", help="Modo de ejecucion")
    parser.add_argument("--anio-datos", default="2025", help="Año de datos del proceso")
    parser.add_argument("--reanudar", help="Ruta a ESTADO_EJECUCION.json")
    parser.add_argument(
        "--ejecucion",
        default=str(ROOT / "estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455"),
        help="Carpeta de ejecucion de referencia para modo final",
    )
    parser.add_argument("--base-institucional", help="Ruta a BASE EXTRANJEROS.xlsx")
    parser.add_argument("--hoja", default="Hoja2", help="Hoja autorizada")
    parser.add_argument("--precarga", help="Ruta a la precarga oficial")
    parser.add_argument("--diagnostico-nacionalidad", help="Carpeta con 08_DECISION_NACIONALIDAD_104.csv")
    parser.add_argument("--matriz-revision", help="Carpeta con matriz de revision aplicada")
    parser.add_argument("--salida", help="Carpeta raiz de salida")
    parser.add_argument("--archivo-regresion", help="CSV aprobado para regresion logica")
    parser.add_argument(
        "--listado-sies-120",
        default="/Users/alexi/Desktop/Listado Registros IP San Sebastian.xlsx",
        help="Listado XLSX recibido desde SIES con 120 casos observados",
    )
    parser.add_argument(
        "--csv-previo",
        default="/Users/alexi/Desktop/EXTRANJEROS_REGULARES_2025_PES_READY_RESIDENCIA_0_20260626_121728.csv",
        help="CSV previamente cargado y aceptado por SIES (81 filas)",
    )
    parser.add_argument(
        "--generar-carga-104-vigencia-0",
        action="store_true",
        help="Genera carga SIES de 104 pendientes con NACIONALIDAD=38 y VIGENCIA=0",
    )
    parser.add_argument(
        "--auditar-estado-actividad",
        action="store_true",
        help="Incorpora auditoría de estado académico y actividad 2025 en la generación de carga 104",
    )
    parser.add_argument("--generar-excel", action="store_true", help="Generar Excel de revision")
    parser.add_argument("--generar-pes", action="store_true", help="Generar CSV final SIES")
    parser.add_argument("--copiar-escritorio", action="store_true", help="Copiar Excel y CSV al Escritorio")
    parser.add_argument("--abrir-resultados", action="store_true", help="Abrir Excel y seleccionar CSV en Finder")
    args = parser.parse_args()

    if args.modo == "sies120":
        return run_sies120_mode(args)

    if args.modo == "final":
        return run_final_mode(args)

    if not args.reanudar:
        raise SystemExit("BLOQUEADO_POR_PARAMETROS: --reanudar es obligatorio en modo fase06")
    if not args.base_institucional:
        raise SystemExit("BLOQUEADO_POR_PARAMETROS: --base-institucional es obligatorio en modo fase06")

    estado_path = Path(args.reanudar)
    run_dir = estado_path.parent
    base_path = Path(args.base_institucional)
    sheet_name = args.hoja
    dirs = ensure_run_dirs(run_dir)

    if not base_path.exists():
        raise SystemExit("BLOQUEADO_POR_ESTRUCTURA_HOJA2_INSUFICIENTE: no existe base institucional")
    base_hash = sha256(base_path)
    (dirs["vigencia"] / "06M_HASH_BASE_EXTRANJEROS.sha256").write_text(
        f"{base_hash}  {base_path}\n",
        encoding="utf-8",
    )

    xl = pd.ExcelFile(base_path)
    if sheet_name not in xl.sheet_names:
        raise SystemExit("BLOQUEADO_POR_ESTRUCTURA_HOJA2_INSUFICIENTE: no existe hoja autorizada")
    hoja = pd.read_excel(base_path, sheet_name=sheet_name, dtype=str, keep_default_na=False).fillna("")
    if hoja.empty:
        raise SystemExit("BLOQUEADO_POR_ESTRUCTURA_HOJA2_INSUFICIENTE: hoja sin datos")
    missing_cols = [col for col in SHEET_REQUIRED_COLUMNS if col not in hoja.columns]
    if missing_cols:
        raise SystemExit(f"BLOQUEADO_POR_ESTRUCTURA_HOJA2_INSUFICIENTE: faltan columnas {missing_cols}")

    inventory, structure, dictionary = hoja2_inventory(hoja, base_path, sheet_name, base_hash)
    write_csv(inventory, dirs["vigencia"] / "06M_INVENTARIO_BASE_EXTRANJEROS_HOJA2.csv")
    (dirs["vigencia"] / "06M_ESTRUCTURA_HOJA2.json").write_text(
        json.dumps(structure, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(dictionary, dirs["vigencia"] / "06N_DICCIONARIO_HOJA2.csv")

    hoja_norm = normalize_hoja2(hoja)
    write_csv(hoja_norm, dirs["vigencia"] / "06O_BASE_EXTRANJEROS_HOJA2_NORMALIZADA.csv")

    precarga_path = dirs["precarga"] / "PRECARGA_NORMALIZADA_AUDITORIA.csv"
    decision_path = dirs["vigencia"] / "DECISION_VIGENCIA_COMPLETA.csv"
    req_path = dirs["vigencia"] / "REQUERIMIENTO_INSTITUCIONAL_FASE_06_VIGENCIA_V2.csv"
    if not precarga_path.exists() or not decision_path.exists() or not req_path.exists():
        raise SystemExit("BLOQUEADO_POR_ESTRUCTURA_HOJA2_INSUFICIENTE: faltan artefactos previos Fase 06")
    precarga = read_csv(precarga_path)
    decision_prev = read_csv(decision_path)
    req = read_csv(req_path)
    if len(precarga) != 185:
        raise SystemExit(f"BLOQUEADO_POR_ESTRUCTURA_HOJA2_INSUFICIENTE: precarga={len(precarga)}")

    code_to_carr, code_to_plan, _ = load_code_maps()
    add_req_code_maps(req, code_to_carr, code_to_plan)
    outputs = build_phase_outputs(
        run_dir,
        dirs,
        base_path,
        sheet_name,
        hoja_norm,
        precarga,
        decision_prev,
        req,
        code_to_carr,
        code_to_plan,
    )
    outputs = apply_institutional_phase06_closure(outputs, dirs, base_path)

    metrics = outputs["metrics"]
    can_continue = (
        metrics["filas_matriz"] == 185
        and metrics["vigencia_0"] == 24
        and metrics["vigencia_1"] == 161
        and metrics["vigencia_0"] + metrics["vigencia_1"] == 185
        and metrics["pendientes_unicos"] == 0
        and metrics["conflictos"] == 0
        and metrics["vigencia_fuera_dominio"] == 0
        and metrics["id_registro_duplicados"] == 0
        and metrics["codigo_unico_vacio"] == 0
        and metrics["contradicciones"] == 0
    )

    final_info: dict[str, Any] = {}
    if can_continue:
        write_complete_state(estado_path)
        final_info = continue_phases(
            run_dir,
            dirs,
            precarga,
            outputs["matriz"],
            base_path,
            sheet_name,
            base_hash,
            outputs.get("audit_phase06"),
        )
        if final_info["validation"]["pruebas_fallidas"]:
            final_status = "BLOQUEADO_EN_FASE_11"
            estado_path.write_text(json.dumps({
                "ultima_fase_completada": 10,
                "fase_actual": 11,
                "estado": final_status,
                "bloqueado": True,
                "motivo_bloqueo": "PRUEBAS_FALLIDAS_VALIDACION_END_TO_END",
                "pruebas_fallidas": final_info["validation"]["pruebas_fallidas"],
                "fecha_actualizacion": now(),
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            can_continue = False
        else:
            write_final_state(estado_path, final_info)
            final_status = "LISTO_PARA_CARGA_PES"
    else:
        write_block(run_dir, dirs, outputs, estado_path)
        final_status = "BLOQUEADO_EN_FASE_06"

    run_git_checks(run_dir, dirs)

    summary = {
        "estado_final": final_status,
        "ruta_base_extranjeros": str(base_path),
        "hash_base_extranjeros": base_hash,
        "hoja_usada": sheet_name,
        "filas_hoja2": int(len(hoja)),
        "columnas_hoja2": int(len(hoja.columns)),
        **metrics,
        "incorporaciones_confirmadas": final_info.get("validation", {}).get("incorporaciones_confirmadas", ""),
        "universo_final": final_info.get("validation", {}).get("filas", ""),
        "pruebas_fallidas": final_info.get("validation", {}).get("pruebas_fallidas", []),
        "campos_obligatorios_vacios": final_info.get("validation", {}).get("campos_obligatorios_vacios", {}),
        "pes": final_info.get("pes", ""),
        "hash_pes": final_info.get("pes_hash", ""),
        "excel_auditoria": final_info.get("audit", ""),
        "reporte": final_info.get("report", ""),
        "carpeta_escritorio": final_info.get("desktop", ""),
        "commit_realizado": "NO",
        "push_realizado": "NO",
        "fuentes_originales_modificadas": "NO",
    }
    (dirs["control"] / "RESUMEN_REANUDACION_FASE_06_HOJA2.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if can_continue else 2


if __name__ == "__main__":
    raise SystemExit(main())
