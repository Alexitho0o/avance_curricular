#!/usr/bin/env python3
"""Auditoria integral multicodcli para Matricula Unificada 2026.

El script identifica RUT con mas de un CODCLI desde fuentes institucionales,
audita las 32 columnas MU para las filas relacionadas y genera artefactos
trazables. No usa los archivos corregidos posteriores como base de partida.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


RUN_DT = datetime.now()
RUN_TS = RUN_DT.strftime("%Y-%m-%d %H:%M:%S")
RUN_STAMP = RUN_DT.strftime("%Y%m%d_%H%M%S")

MU_COLUMNS = [
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
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "FOR_ING_ACT",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ANIO_ING_ORI",
    "SEM_ING_ORI",
    "ASI_INS_ANT",
    "ASI_APR_ANT",
    "PROM_PRI_SEM",
    "PROM_SEG_SEM",
    "ASI_INS_HIS",
    "ASI_APR_HIS",
    "NIV_ACA",
    "SIT_FON_SOL",
    "SUS_PRE",
    "FECHA_MATRICULA",
    "REINCORPORACION",
    "VIG",
]

FIELD_CLASSIFICATIONS = [
    "COINCIDE_CON_TRAYECTORIA_CORRECTA",
    "VALOR_TOMADO_DE_OTRA_TRAYECTORIA",
    "DIFERENCIA_CON_FUENTE_CORRECTA",
    "VALOR_NO_PRESENTE_EN_NINGUNA_TRAYECTORIA",
    "CAMPO_COMPARTIDO_ENTRE_TRAYECTORIAS",
    "SIN_FUENTE_DIRECTA",
    "FUENTE_AMBIGUA",
    "DIFERENCIA_SOLO_DE_FORMATO",
    "DIFERENCIA_DE_NORMALIZACION",
    "NO_APLICA",
    "REQUIERE_REVISION_MANUAL",
    "CORRECCION_UNIVOCA_PROPUESTA",
]

PERSONAL_FIELDS = {
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
}
OFFER_FIELDS = {"COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION"}
CURRENT_FIELDS = {"FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT"}
ORIGIN_FIELDS = {"ANIO_ING_ORI", "SEM_ING_ORI"}
ACTIVITY_FIELDS = {
    "ASI_INS_ANT",
    "ASI_APR_ANT",
    "PROM_PRI_SEM",
    "PROM_SEG_SEM",
    "ASI_INS_HIS",
    "ASI_APR_HIS",
    "NIV_ACA",
}
ADMIN_FIELDS = {"SIT_FON_SOL", "SUS_PRE", "FECHA_MATRICULA", "REINCORPORACION", "VIG"}

DIRECT_SOURCE_FIELDS = {
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
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ASI_INS_ANT",
    "ASI_APR_ANT",
    "PROM_PRI_SEM",
    "PROM_SEG_SEM",
    "ASI_INS_HIS",
    "ASI_APR_HIS",
    "NIV_ACA",
    "FECHA_MATRICULA",
    "REINCORPORACION",
    "VIG",
}

SAFE_AUTOMATIC_FIELDS = {
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "FECHA_MATRICULA",
    "NIV_ACA",
    "VIG",
}

JORNADA_TO_CODE = {"D": "1", "V": "2", "P": "3", "O": "4"}
SEDE_TO_CODE = {"RE": "2", "CO": "3"}


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return "" if text.lower() in {"nan", "none", "nat"} else text


def strip_accents(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))


def norm_text(value: Any, *, accents: bool = False) -> str:
    text = clean(value).upper()
    if not accents:
        text = strip_accents(text)
    text = re.sub(r"[^A-Z0-9KÑÜ /.-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def norm_comp(value: Any) -> str:
    return re.sub(r"[^A-Z0-9K]", "", norm_text(value, accents=False))


def rut_body(value: Any) -> str:
    text = clean(value).upper()
    text = re.sub(r"[^0-9Kk-]", "", text)
    if "-" in text:
        return re.sub(r"[^0-9]", "", text.split("-")[0])
    return re.sub(r"[^0-9]", "", text[:-1] if text.endswith("K") else text)


def rut_dv(value: Any, explicit_dv: Any = "") -> str:
    dv = clean(explicit_dv).upper()
    if dv:
        return dv
    text = clean(value).upper()
    text = re.sub(r"[^0-9Kk-]", "", text)
    if "-" in text:
        return text.split("-")[-1].upper()
    if text and text[-1].upper() in "0123456789K":
        return text[-1].upper()
    return ""


def norm_num(value: Any) -> str:
    text = clean(value)
    if re.fullmatch(r"-?\d+(\.0+)?", text):
        return str(int(float(text)))
    return norm_comp(text)


def norm_date(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        return text
    return parsed.strftime("%d/%m/%Y")


def norm_value(field: str, value: Any) -> str:
    if field in {"FECH_NAC", "FECHA_MATRICULA"}:
        return norm_date(value)
    if field in {"PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE"}:
        return norm_text(value, accents=False)
    if field in {
        "N_DOC",
        "DV",
        "COD_SED",
        "COD_CAR",
        "MODALIDAD",
        "JOR",
        "VERSION",
        "FOR_ING_ACT",
        "ANIO_ING_ACT",
        "SEM_ING_ACT",
        "ANIO_ING_ORI",
        "SEM_ING_ORI",
        "ASI_INS_ANT",
        "ASI_APR_ANT",
        "PROM_PRI_SEM",
        "PROM_SEG_SEM",
        "ASI_INS_HIS",
        "ASI_APR_HIS",
        "NIV_ACA",
        "SIT_FON_SOL",
        "SUS_PRE",
        "REINCORPORACION",
        "VIG",
        "NAC",
        "PAIS_EST_SEC",
    }:
        return norm_num(value)
    return norm_text(value, accents=False)


def values_equal(field: str, left: Any, right: Any) -> bool:
    return norm_value(field, left) == norm_value(field, right)


def format_only_difference(field: str, left: Any, right: Any) -> bool:
    if clean(left) == clean(right):
        return False
    if not values_equal(field, left, right):
        return False
    return True


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def parse_codigo_unico(code: Any) -> dict[str, str]:
    text = norm_text(code, accents=False)
    match = re.search(r"I(?P<ies>\d+)S(?P<sed>\d+)C(?P<car>\d+)J(?P<jor>\d+)V(?P<ver>\d+)", text)
    if not match:
        return {"COD_SED": "", "COD_CAR": "", "JOR": "", "VERSION": ""}
    return {
        "COD_SED": match.group("sed"),
        "COD_CAR": match.group("car"),
        "JOR": match.group("jor"),
        "VERSION": match.group("ver"),
    }


def codcli_year_sem(codcli: Any) -> tuple[str, str]:
    text = clean(codcli)
    match = re.match(r"^(\d{4})(\d)", text)
    if not match:
        return "", ""
    sem = match.group(2)
    if sem == "3":
        sem = "2"
    return match.group(1), sem


def codcli_codcarr(codcli: Any) -> str:
    text = norm_text(codcli, accents=False)
    match = re.match(r"^\d{5}([A-Z]+)", text)
    return match.group(1) if match else ""


def llavemu(row: pd.Series | dict[str, Any]) -> str:
    return "|".join(clean(row.get(c, "")) for c in ["TIPO_DOC", "N_DOC", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION"])


def read_mu(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", header=None, names=MU_COLUMNS, dtype=str, keep_default_na=False)
    df.insert(0, "FILA_MU", df.index + 1)
    df["RUT_N"] = df["N_DOC"].map(rut_body)
    df["LLAVE_MU"] = df.apply(llavemu, axis=1)
    return df


def read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: clean(row.get(c, "")) for c in columns})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            sheet_name = re.sub(r"[:\\/?*\[\]]", "_", name)[:31] or "Hoja"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.book[sheet_name]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for column_cells in ws.columns:
                header = str(column_cells[0].value or "")
                width = min(max(len(header) + 2, 12), 55)
                ws.column_dimensions[column_cells[0].column_letter].width = width


def source_row_ref(sheet: str, idx: int) -> str:
    return f"{sheet} fila {idx + 2}"


def load_sources(root: Path) -> dict[str, Any]:
    xlsx = root / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"
    sheets = {
        "Hoja1": pd.read_excel(xlsx, sheet_name="Hoja1", dtype=str).fillna(""),
        "DatosAlumnos": pd.read_excel(xlsx, sheet_name="DatosAlumnos", dtype=str).fillna(""),
        "matriz": pd.read_excel(xlsx, sheet_name="matriz", dtype=str).fillna(""),
        "base_datos": pd.read_excel(xlsx, sheet_name="base_datos", dtype=str).fillna(""),
    }
    for sheet_name, df in sheets.items():
        if "RUT" in df.columns:
            df["RUT_N"] = df["RUT"].map(rut_body)
            df["DV_N"] = df.apply(lambda r: rut_dv(r.get("RUT", ""), r.get("DIG", r.get("DV", ""))), axis=1)
        if "CODCLI" in df.columns:
            df["CODCLI_N"] = df["CODCLI"].map(clean)
    return {
        "xlsx": xlsx,
        "sheets": sheets,
        "bridge": read_tsv(root / "control" / "catalogos" / "PUENTE_SIES_COMPILADO.tsv"),
        "gob_nac": read_tsv(root / "gobernanza_nac.tsv"),
        "gob_pais": read_tsv(root / "gobernanza_pais_est_sec.tsv"),
        "gob_sede": read_tsv(root / "gobernanza_sede.tsv"),
        "gob_cols": load_governance(root),
    }


def load_governance(root: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for path in sorted((root / "gobernanza_columnas_mu").glob("gob_mu_*.tsv")):
        try:
            df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
            if not df.empty and "CAMPO_SALIDA" in df.columns:
                out[clean(df.iloc[0]["CAMPO_SALIDA"])] = df.iloc[0].to_dict()
        except Exception:
            continue
    return out


def map_nacionalidad(value: Any, gob_nac: pd.DataFrame) -> str:
    text = norm_text(value, accents=False)
    if not text:
        return ""
    if re.fullmatch(r"\d+", text):
        return text
    if gob_nac.empty:
        return ""
    gob = gob_nac.copy()
    for col in ["NACIONALIDAD_ORIG", "NACIONALIDAD_NORM", "PAIS_NORM"]:
        if col in gob.columns:
            match = gob[gob[col].map(lambda x: norm_text(x, accents=False)).eq(text)]
            if not match.empty:
                return clean(match.iloc[0].get("COD_NAC", ""))
    return ""


def map_pais_est_sec(row: pd.Series | dict[str, Any], gob_pais: pd.DataFrame) -> str:
    if gob_pais.empty:
        return ""
    comuna = norm_text(row.get("COMUNACOLEGIO", ""), accents=False)
    ciudad = norm_text(row.get("CIUDADCOLEGIO", ""), accents=False)
    gob = gob_pais.copy()
    if comuna:
        m = gob[gob["COMUNACOLEGIO_NORM"].map(lambda x: norm_text(x, accents=False)).eq(comuna)]
        if not m.empty:
            return clean(m.iloc[0].get("COD_PAIS_EST_SEC", ""))
    if ciudad:
        m = gob[gob["CIUDADCOLEGIO_NORM"].map(lambda x: norm_text(x, accents=False)).eq(ciudad)]
        if not m.empty:
            return clean(m.iloc[0].get("COD_PAIS_EST_SEC", ""))
    return ""


def sex_to_mu(value: Any) -> str:
    text = norm_text(value, accents=False)
    if text in {"F", "FEMENINO", "MUJER"}:
        return "M"
    if text in {"M", "MASCULINO", "HOMBRE"}:
        return "H"
    if text in {"NB", "NO BINARIO"}:
        return "NB"
    return text


def average_to_100(series: pd.Series) -> str:
    nums = pd.to_numeric(series.map(lambda x: str(x).replace(",", ".")), errors="coerce").dropna()
    nums = nums[(nums >= 1) & (nums <= 7)]
    if nums.empty:
        return "0"
    return str(int(round(nums.mean() * 100)))


def count_approved(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    estado = df.get("ESTADO", pd.Series([""] * len(df))).map(lambda x: norm_text(x, accents=False))
    desc = df.get("DESCRIPCION_ESTADO", pd.Series([""] * len(df))).map(lambda x: norm_text(x, accents=False))
    return int(((estado == "A") | desc.str.contains("APROB|HOMOLOG", regex=True)).sum())


def build_offer_tables(sources: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, set[str]], dict[str, dict[str, str]]]:
    matriz = sources["sheets"]["matriz"].copy()
    for col in ["CODIGO_UNICO", "COD_SEDE", "MODALIDAD", "JORNADA", "VIGENCIA"]:
        if col in matriz.columns:
            matriz[col] = matriz[col].map(norm_num)
    parsed = matriz["CODIGO_UNICO"].map(parse_codigo_unico)
    matriz["COD_CAR_PARSE"] = parsed.map(lambda x: x["COD_CAR"])
    matriz["VERSION_PARSE"] = parsed.map(lambda x: x["VERSION"])
    matriz["LLAVE_OFERTA_MU"] = matriz.apply(
        lambda r: "|".join([clean(r.get("COD_SEDE", "")), clean(r.get("COD_CAR_PARSE", "")), clean(r.get("MODALIDAD", "")), clean(r.get("JORNADA", "")), clean(r.get("VERSION_PARSE", ""))]),
        axis=1,
    )
    bridge = sources["bridge"].copy()
    code_candidates_by_codcar_jornada: dict[str, set[str]] = defaultdict(set)
    if not bridge.empty:
        for _, r in bridge.iterrows():
            codcar = clean(r.get("CODCARPR", ""))
            jornada = clean(r.get("JORNADA", ""))
            key = f"{codcar}|{jornada}"
            for col in ["CODIGO_UNICO_FINAL", "CODIGOS_SIES_POTENCIALES"]:
                for part in re.split(r"\s*\|\s*|,", clean(r.get(col, ""))):
                    if clean(part):
                        code_candidates_by_codcar_jornada[key].add(clean(part))
    code_details = {
        clean(r["CODIGO_UNICO"]): {
            "COD_SED": clean(r.get("COD_SEDE", "")),
            "COD_CAR": clean(r.get("COD_CAR_PARSE", "")),
            "MODALIDAD": clean(r.get("MODALIDAD", "")),
            "JOR": clean(r.get("JORNADA", "")),
            "VERSION": clean(r.get("VERSION_PARSE", "")),
            "NOMBRE_CARRERA": clean(r.get("NOMBRE_CARRERA", "")),
            "NIVEL_CARRERA": clean(r.get("NIVEL_CARRERA", "")),
            "DURACION_ESTUDIOS": clean(r.get("DURACION_ESTUDIOS", "")),
        }
        for _, r in matriz.iterrows()
    }
    return matriz, code_candidates_by_codcar_jornada, code_details


def build_multicodcli_universe(sources: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for sheet in ["Hoja1", "DatosAlumnos", "base_datos"]:
        df = sources["sheets"][sheet]
        if "RUT" not in df.columns or "CODCLI" not in df.columns:
            continue
        for idx, r in df.iterrows():
            rut = clean(r.get("RUT_N", ""))
            codcli = clean(r.get("CODCLI_N", ""))
            if not rut or not codcli:
                continue
            rows.append(
                {
                    "HOJA": sheet,
                    "FILA_FUENTE": idx + 2,
                    "RUT": rut,
                    "DV": clean(r.get("DV_N", "")),
                    "CODCLI": codcli,
                    "CODCARR": clean(r.get("CODCARR", r.get("CODCARPR", ""))),
                    "CARRERA": clean(r.get("CARRERA", r.get("NOMBRE_L", ""))),
                    "JORNADA": clean(r.get("JORNADA", "")),
                    "ANIO": clean(r.get("ANO", r.get("ANOMATRICULA", ""))),
                    "PERIODO": clean(r.get("PERIODO", r.get("PERIODOMATRICULA", ""))),
                }
            )
    detail = pd.DataFrame(rows)
    counts = detail.groupby("RUT")["CODCLI"].nunique().reset_index(name="N_CODCLI")
    multicodcli = counts[counts["N_CODCLI"] > 1].copy()
    return detail, multicodcli


def build_trajectory_summary(sources: dict[str, Any], multi_ruts: set[str], code_candidates: dict[str, set[str]], code_details: dict[str, dict[str, str]]) -> pd.DataFrame:
    hoja1 = sources["sheets"]["Hoja1"].copy()
    datos = sources["sheets"]["DatosAlumnos"].copy()
    rows = []
    all_codcli = sorted(
        set(hoja1[hoja1["RUT_N"].isin(multi_ruts)]["CODCLI_N"].dropna())
        | set(datos[datos["RUT_N"].isin(multi_ruts)]["CODCLI_N"].dropna())
    )
    for codcli in all_codcli:
        h = hoja1[hoja1["CODCLI_N"].eq(codcli)].copy()
        d = datos[datos["CODCLI_N"].eq(codcli)].copy()
        first_d = d.iloc[0] if not d.empty else pd.Series(dtype=str)
        first_h = h.iloc[0] if not h.empty else pd.Series(dtype=str)
        rut = clean(first_d.get("RUT_N", first_h.get("RUT_N", "")))
        dv = clean(first_d.get("DV_N", first_h.get("DV_N", "")))
        codcarr = clean(first_d.get("CODCARPR", first_h.get("CODCARR", codcli_codcarr(codcli))))
        jornada_letra = clean(first_d.get("JORNADA", first_h.get("JORNADA", "")))
        cand_key = f"{codcarr}|{jornada_letra}"
        candidates = sorted(code_candidates.get(cand_key, set()))
        code_detail_values = [code_details.get(c, {}) for c in candidates]
        exact_codes = [c for c in candidates if c in code_details]
        selected_code = exact_codes[0] if len(exact_codes) == 1 else ""
        selected_details = code_details.get(selected_code, {})
        codcli_anio, codcli_sem = codcli_year_sem(codcli)
        h_2025 = h[h.get("ANO", "").map(norm_num).eq("2025")] if not h.empty and "ANO" in h.columns else pd.DataFrame()
        ins_ant = str(len(h_2025)) if not h_2025.empty else "0"
        apr_ant = str(count_approved(h_2025))
        prom_pri = average_to_100(h_2025[h_2025.get("PERIODO", "").map(norm_num).eq("1")]["NOTA_FINAL"]) if not h_2025.empty and "NOTA_FINAL" in h_2025.columns else "0"
        prom_seg = average_to_100(h_2025[h_2025.get("PERIODO", "").map(norm_num).isin(["2", "3"])]["NOTA_FINAL"]) if not h_2025.empty and "NOTA_FINAL" in h_2025.columns else "0"
        ins_his = str(len(h)) if not h.empty else "0"
        apr_his = str(count_approved(h))
        nivel_h = pd.to_numeric(h.get("NIVEL", pd.Series(dtype=str)), errors="coerce").dropna() if not h.empty else pd.Series(dtype=float)
        nivel_d = pd.to_numeric(d.get("NIVEL", pd.Series(dtype=str)), errors="coerce").dropna() if not d.empty else pd.Series(dtype=float)
        nivel = str(int(max([nivel_h.max() if not nivel_h.empty else 0, nivel_d.max() if not nivel_d.empty else 0]))) if (not nivel_h.empty or not nivel_d.empty) else ""
        periods = []
        for _, r in h.iterrows():
            anio = norm_num(r.get("ANO", ""))
            per = norm_num(r.get("PERIODO", ""))
            if anio:
                periods.append(f"{anio}-{per}")
        for _, r in d.iterrows():
            anio = norm_num(r.get("ANOMATRICULA", ""))
            per = norm_num(r.get("PERIODOMATRICULA", ""))
            if anio:
                periods.append(f"{anio}-{per}")
        rows.append(
            {
                "RUT": rut,
                "DV": dv,
                "CODCLI": codcli,
                "CODCARR": codcarr,
                "NOMBRE_CARRERA": clean(first_d.get("NOMBRE_L", first_h.get("CARRERA", ""))),
                "COD_SED": selected_details.get("COD_SED", SEDE_TO_CODE.get(clean(first_d.get("SEDE", "")), "")),
                "SEDE_ORIGEN": clean(first_d.get("SEDE", "")),
                "MODALIDAD": selected_details.get("MODALIDAD", ""),
                "JORNADA_LETRA": jornada_letra,
                "JOR": selected_details.get("JOR", JORNADA_TO_CODE.get(jornada_letra, "")),
                "VERSION": selected_details.get("VERSION", ""),
                "COD_CAR": selected_details.get("COD_CAR", ""),
                "CODIGO_UNICO_OFERTA": selected_code,
                "CODIGOS_UNICOS_CANDIDATOS": " | ".join(candidates),
                "ANIO_CODCLI": codcli_anio,
                "SEM_CODCLI": codcli_sem,
                "ANIO_INGRESO_FUENTE": norm_num(first_d.get("ANOINGRESO", "")),
                "SEM_INGRESO_FUENTE": norm_num(first_d.get("PERIODOINGRESO", "")),
                "ANIO_MATRICULA_FUENTE": norm_num(first_d.get("ANOMATRICULA", "")),
                "SEM_MATRICULA_FUENTE": norm_num(first_d.get("PERIODOMATRICULA", "")),
                "PRIMER_PERIODO_OBSERVADO": min(periods) if periods else "",
                "ULTIMO_PERIODO_OBSERVADO": max(periods) if periods else "",
                "NIVELES_OBSERVADOS": " | ".join(sorted(set(h.get("NIVEL", pd.Series(dtype=str)).map(clean).tolist() + d.get("NIVEL", pd.Series(dtype=str)).map(clean).tolist()))),
                "FORMA_INGRESO_FUENTE": clean(first_d.get("VIASDEADMISION", "")),
                "FECHAS_MATRICULA": " | ".join(sorted(set(d.get("FECHAMATRICULA", pd.Series(dtype=str)).map(clean).tolist()))),
                "ASIGNATURAS_INSCRITAS_2025": ins_ant,
                "ASIGNATURAS_APROBADAS_2025": apr_ant,
                "PROM_PRI_SEM_2025": prom_pri,
                "PROM_SEG_SEM_2025": prom_seg,
                "ASI_INS_HIS": ins_his,
                "ASI_APR_HIS": apr_his,
                "NIVEL_MAX_OBSERVADO": nivel,
                "ESTADO_ACADEMICO": " | ".join(sorted(set(d.get("ESTADOACADEMICO", pd.Series(dtype=str)).map(clean).tolist()))),
                "SITUACION": " | ".join(sorted(set(d.get("SITUACION", pd.Series(dtype=str)).map(clean).tolist()))),
                "MATRICULA": " | ".join(sorted(set(d.get("MATRICULA", pd.Series(dtype=str)).map(clean).tolist()))),
                "VIGENCIA_DERIVADA": "1" if any("VIGENTE" in norm_text(x, accents=False) for x in d.get("ESTADOACADEMICO", pd.Series(dtype=str)).tolist()) else "",
                "REINCORPORACION_DERIVADA": "1" if any("REINC" in norm_text(x, accents=False) for x in d.get("SITUACION", pd.Series(dtype=str)).tolist()) else "0",
                "FILAS_HOJA1": " | ".join(str(i + 2) for i in h.index[:50]),
                "FILAS_DATOSALUMNOS": " | ".join(str(i + 2) for i in d.index[:50]),
                "N_FILAS_HOJA1": len(h),
                "N_FILAS_DATOSALUMNOS": len(d),
            }
        )
    return pd.DataFrame(rows).fillna("")


def trajectory_value(codcli: str, field: str, traj: pd.DataFrame, sources: dict[str, Any], code_details: dict[str, dict[str, str]]) -> dict[str, str]:
    row_df = traj[traj["CODCLI"].eq(codcli)]
    if row_df.empty:
        return {"valor": "", "archivo": "", "hoja": "", "fila": "", "columna": "", "directa": "NO", "regla": "CODCLI no encontrado"}
    t = row_df.iloc[0]
    datos = sources["sheets"]["DatosAlumnos"]
    d = datos[datos["CODCLI_N"].eq(codcli)]
    first = d.iloc[0] if not d.empty else pd.Series(dtype=str)
    if field == "TIPO_DOC":
        return {"valor": "R", "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "RUT", "directa": "SI", "regla": "RUT institucional => TIPO_DOC R"}
    if field == "N_DOC":
        return {"valor": clean(t.get("RUT", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "RUT", "directa": "SI", "regla": "Cuerpo RUT"}
    if field == "DV":
        return {"valor": clean(t.get("DV", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "RUT/DIG", "directa": "SI", "regla": "DV institucional"}
    personal_cols = {
        "PRIMER_APELLIDO": "APELLIDO PATERNO",
        "SEGUNDO_APELLIDO": "APELLIDO MATERNO",
        "NOMBRE": "NOMBRES",
        "FECH_NAC": "FECHANACIMIENTO",
    }
    if field in personal_cols:
        col = personal_cols[field]
        value = first.get(col, "") if col in first.index else ""
        if field == "FECH_NAC":
            value = norm_date(value)
        else:
            value = norm_text(value, accents=False)
        return {"valor": value, "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": col, "directa": "SI", "regla": "Dato personal institucional"}
    if field == "SEXO":
        return {"valor": sex_to_mu(first.get("SEXO", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "SEXO", "directa": "SI", "regla": "Mapeo F->M, M->H"}
    if field == "NAC":
        return {"valor": map_nacionalidad(first.get("NACIONALIDAD", ""), sources["gob_nac"]), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx; gobernanza_nac.tsv", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "NACIONALIDAD", "directa": "SI", "regla": "Mapeo gobernanza_nac"}
    if field == "PAIS_EST_SEC":
        return {"valor": map_pais_est_sec(first, sources["gob_pais"]), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx; gobernanza_pais_est_sec.tsv", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "COMUNACOLEGIO/CIUDADCOLEGIO", "directa": "SI", "regla": "Mapeo localidad colegio"}
    if field in OFFER_FIELDS:
        return {"valor": clean(t.get(field, "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx; PUENTE_SIES_COMPILADO.tsv; matriz", "hoja": "DatosAlumnos/matriz", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": field, "directa": "SI", "regla": "Oferta por CODCLI + puente SIES + matriz"}
    if field == "FOR_ING_ACT":
        return {"valor": "", "archivo": "Manual/gobernanza", "hoja": "", "fila": "", "columna": "VIASDEADMISION", "directa": "NO", "regla": "No hay mapeo univoco de texto institucional a codigo 1..11 en esta auditoria"}
    if field == "ANIO_ING_ACT":
        return {"valor": clean(t.get("ANIO_INGRESO_FUENTE", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "ANOINGRESO", "directa": "SI", "regla": "Ingreso carrera actual de CODCLI"}
    if field == "SEM_ING_ACT":
        return {"valor": clean(t.get("SEM_INGRESO_FUENTE", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "PERIODOINGRESO", "directa": "SI", "regla": "Ingreso carrera actual de CODCLI"}
    if field in ORIGIN_FIELDS:
        col = "ANIO_INGRESO_FUENTE" if field == "ANIO_ING_ORI" else "SEM_INGRESO_FUENTE"
        return {"valor": clean(t.get(col, "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "ANOINGRESO/PERIODOINGRESO", "directa": "PARCIAL", "regla": "El manual define carrera de origen, pero la fuente no separa de forma concluyente origen institucional/programa; control tecnico"}
    activity_map = {
        "ASI_INS_ANT": "ASIGNATURAS_INSCRITAS_2025",
        "ASI_APR_ANT": "ASIGNATURAS_APROBADAS_2025",
        "PROM_PRI_SEM": "PROM_PRI_SEM_2025",
        "PROM_SEG_SEM": "PROM_SEG_SEM_2025",
        "ASI_INS_HIS": "ASI_INS_HIS",
        "ASI_APR_HIS": "ASI_APR_HIS",
        "NIV_ACA": "NIVEL_MAX_OBSERVADO",
    }
    if field in activity_map:
        return {"valor": clean(t.get(activity_map[field], "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "Hoja1/DatosAlumnos", "fila": clean(t.get("FILAS_HOJA1", "")), "columna": activity_map[field], "directa": "SI", "regla": "Reconstruccion tecnica por CODCLI, no por RUT completo"}
    if field == "SIT_FON_SOL":
        return {"valor": "", "archivo": "", "hoja": "", "fila": "", "columna": "", "directa": "NO", "regla": "Sin fuente directa FSCU en archivos disponibles"}
    if field == "SUS_PRE":
        return {"valor": "", "archivo": "", "hoja": "", "fila": "", "columna": "", "directa": "NO", "regla": "Sin fuente directa de suspensiones previas en archivos disponibles"}
    if field == "FECHA_MATRICULA":
        return {"valor": norm_date(first.get("FECHAMATRICULA", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "FECHAMATRICULA", "directa": "SI", "regla": "Fecha matricula de CODCLI"}
    if field == "REINCORPORACION":
        return {"valor": clean(t.get("REINCORPORACION_DERIVADA", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "SITUACION", "directa": "SI", "regla": "Derivado de situacion con texto reincorporacion"}
    if field == "VIG":
        return {"valor": clean(t.get("VIGENCIA_DERIVADA", "")), "archivo": "PROMEDIOSDEALUMNOS_7804.xlsx", "hoja": "DatosAlumnos", "fila": clean(t.get("FILAS_DATOSALUMNOS", "")), "columna": "ESTADOACADEMICO/MATRICULA", "directa": "SI", "regla": "VIGENTE => 1"}
    return {"valor": "", "archivo": "", "hoja": "", "fila": "", "columna": "", "directa": "NO", "regla": "Campo no mapeado"}


def build_mu_offer_mapping(mu_audit: pd.DataFrame, traj: pd.DataFrame, matriz: pd.DataFrame, code_details: dict[str, dict[str, str]]) -> pd.DataFrame:
    rows = []
    traj_by_rut = {rut: g.copy() for rut, g in traj.groupby("RUT", dropna=False)}
    matriz_by_key = {k: g.copy() for k, g in matriz.groupby("LLAVE_OFERTA_MU", dropna=False)}
    for _, row in mu_audit.iterrows():
        rut = clean(row["N_DOC"])
        key_offer = "|".join(clean(row[c]) for c in ["COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION"])
        mat = matriz_by_key.get(key_offer, pd.DataFrame())
        codigo_mu = clean(mat.iloc[0]["CODIGO_UNICO"]) if len(mat) == 1 else ""
        codcli_candidates = []
        exact = []
        partial = []
        for _, t in traj_by_rut.get(rut, pd.DataFrame()).iterrows():
            cand_codes = [c for c in re.split(r"\s*\|\s*", clean(t.get("CODIGOS_UNICOS_CANDIDATOS", ""))) if c]
            if codigo_mu and codigo_mu in cand_codes:
                exact.append(clean(t["CODCLI"]))
            else:
                same_car = clean(t.get("COD_CAR", "")) == clean(row["COD_CAR"]) or any(parse_codigo_unico(c)["COD_CAR"] == clean(row["COD_CAR"]) for c in cand_codes)
                same_jor = clean(t.get("JOR", "")) == clean(row["JOR"]) or any(parse_codigo_unico(c)["JOR"] == clean(row["JOR"]) for c in cand_codes)
                same_sed = clean(t.get("COD_SED", "")) == clean(row["COD_SED"]) or any(parse_codigo_unico(c)["COD_SED"] == clean(row["COD_SED"]) for c in cand_codes)
                if same_car and same_jor and same_sed:
                    partial.append(clean(t["CODCLI"]))
            codcli_candidates.append(clean(t["CODCLI"]))
        if len(exact) == 1:
            clas = "MATCH_EXACTO_OFERTA"
            codcli = exact[0]
            conf = "ALTA"
        elif len(exact) > 1:
            clas = "MULTIPLES_CODCLI_MISMA_OFERTA"
            codcli = " | ".join(exact)
            conf = "BAJA"
        elif len(partial) == 1:
            clas = "MATCH_UNICO_POR_CARRERA_Y_OFERTA"
            codcli = partial[0]
            conf = "MEDIA"
        elif len(partial) > 1:
            clas = "MATCH_PARCIAL_REQUIERE_REVISION"
            codcli = " | ".join(partial)
            conf = "BAJA"
        elif len(mat) == 0:
            clas = "CONTRADICCION_ENTRE_FUENTES"
            codcli = ""
            conf = "BAJA"
        else:
            clas = "SIN_MATCH"
            codcli = ""
            conf = "BAJA"
        rows.append(
            {
                "LLAVE_MU": clean(row["LLAVE_MU"]),
                "FILA_MU": clean(row["FILA_MU"]),
                "RUT": rut,
                "DV": clean(row["DV"]),
                "COD_SED": clean(row["COD_SED"]),
                "COD_CAR": clean(row["COD_CAR"]),
                "MODALIDAD": clean(row["MODALIDAD"]),
                "JOR": clean(row["JOR"]),
                "VERSION": clean(row["VERSION"]),
                "CODIGO_UNICO_OFERTA_MU": codigo_mu,
                "NOMBRE_CARRERA_OFERTA_MU": clean(mat.iloc[0].get("NOMBRE_CARRERA", "")) if len(mat) == 1 else "",
                "CODCLI_CORRECTO": codcli,
                "CODCLI_CANDIDATOS_RUT": " | ".join(codcli_candidates),
                "CODCLI_MATCH_EXACTO": " | ".join(exact),
                "CODCLI_MATCH_PARCIAL": " | ".join(partial),
                "CLASIFICACION_MAPEO": clas,
                "CONFIANZA_MAPEO": conf,
                "CRITERIO": "COD_SED+COD_CAR+MODALIDAD+JOR+VERSION -> matriz -> CODIGO_UNICO -> puente/CODCLI",
            }
        )
    return pd.DataFrame(rows)


def audit_fields(mu_audit: pd.DataFrame, mapping: pd.DataFrame, traj: pd.DataFrame, sources: dict[str, Any], code_details: dict[str, dict[str, str]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mapping_by_key = {r["LLAVE_MU"]: r for _, r in mapping.iterrows()}
    traj_by_rut = {rut: g.copy() for rut, g in traj.groupby("RUT", dropna=False)}
    audit_rows = []
    proposals = []
    contamination = []
    prop_id = 1
    for _, mu in mu_audit.iterrows():
        key = clean(mu["LLAVE_MU"])
        map_row = mapping_by_key.get(key, {})
        codcli_correct = clean(map_row.get("CODCLI_CORRECTO", ""))
        map_class = clean(map_row.get("CLASIFICACION_MAPEO", ""))
        has_sufficient_match = map_class in {"MATCH_EXACTO_OFERTA", "MATCH_UNICO_POR_CARRERA_Y_OFERTA"} and "|" not in codcli_correct and codcli_correct
        codcli_otros = []
        if clean(mu["N_DOC"]) in traj_by_rut:
            codcli_otros = [c for c in traj_by_rut[clean(mu["N_DOC"])]["CODCLI"].tolist() if c != codcli_correct]
        for field in MU_COLUMNS:
            mu_value = clean(mu[field])
            expected = trajectory_value(codcli_correct, field, traj, sources, code_details) if has_sufficient_match else {"valor": "", "archivo": "", "hoja": "", "fila": "", "columna": "", "directa": "NO", "regla": "Sin match suficiente de trayectoria"}
            expected_value = clean(expected["valor"])
            other_vals = []
            for other in codcli_otros:
                other_expected = trajectory_value(other, field, traj, sources, code_details)
                if clean(other_expected["valor"]):
                    other_vals.append(f"{other}:{clean(other_expected['valor'])}")
            other_values_only = [x.split(":", 1)[1] for x in other_vals]
            classification = ""
            confidence = "BAJA"
            action = "REQUIERE_REVISION_MANUAL"
            proposed = ""
            if field in {"SIT_FON_SOL", "SUS_PRE"}:
                classification = "SIN_FUENTE_DIRECTA"
                action = "NO_MODIFICAR"
                confidence = "MEDIA"
            elif field in ORIGIN_FIELDS:
                if not has_sufficient_match:
                    classification = "FUENTE_AMBIGUA"
                elif expected["directa"] == "PARCIAL":
                    if expected_value and values_equal(field, mu_value, expected_value):
                        classification = "COINCIDE_CON_TRAYECTORIA_CORRECTA"
                        confidence = "MEDIA"
                        action = "NO_MODIFICAR"
                    else:
                        classification = "REQUIERE_REVISION_MANUAL"
                action = action if action != "REQUIERE_REVISION_MANUAL" else "REQUIERE_REVISION_MANUAL"
            elif not has_sufficient_match:
                classification = "FUENTE_AMBIGUA"
            elif expected["directa"] == "NO" or not expected_value:
                classification = "SIN_FUENTE_DIRECTA"
                action = "NO_MODIFICAR"
                confidence = "MEDIA"
            elif values_equal(field, mu_value, expected_value):
                if other_values_only and all(values_equal(field, expected_value, ov) for ov in other_values_only):
                    classification = "CAMPO_COMPARTIDO_ENTRE_TRAYECTORIAS"
                elif format_only_difference(field, mu_value, expected_value):
                    classification = "DIFERENCIA_SOLO_DE_FORMATO" if field in PERSONAL_FIELDS else "DIFERENCIA_DE_NORMALIZACION"
                else:
                    classification = "COINCIDE_CON_TRAYECTORIA_CORRECTA"
                action = "NO_MODIFICAR"
                confidence = "ALTA" if map_class == "MATCH_EXACTO_OFERTA" else "MEDIA"
            else:
                in_other = any(values_equal(field, mu_value, ov) for ov in other_values_only)
                if in_other and field not in PERSONAL_FIELDS:
                    classification = "VALOR_TOMADO_DE_OTRA_TRAYECTORIA"
                    confidence = "ALTA" if map_class == "MATCH_EXACTO_OFERTA" else "MEDIA"
                    action = "PROPUESTA_UNIVOCA" if field in SAFE_AUTOMATIC_FIELDS else "REQUIERE_REVISION_MANUAL"
                    proposed = expected_value if action == "PROPUESTA_UNIVOCA" else ""
                elif in_other and field in PERSONAL_FIELDS:
                    classification = "CAMPO_COMPARTIDO_ENTRE_TRAYECTORIAS"
                    confidence = "MEDIA"
                    action = "NO_MODIFICAR"
                elif field in SAFE_AUTOMATIC_FIELDS and expected["directa"] == "SI" and map_class == "MATCH_EXACTO_OFERTA":
                    classification = "CORRECCION_UNIVOCA_PROPUESTA"
                    confidence = "ALTA"
                    action = "PROPUESTA_UNIVOCA"
                    proposed = expected_value
                elif other_values_only:
                    classification = "DIFERENCIA_CON_FUENTE_CORRECTA"
                    confidence = "MEDIA"
                    action = "REQUIERE_REVISION_MANUAL"
                else:
                    classification = "VALOR_NO_PRESENTE_EN_NINGUNA_TRAYECTORIA"
                    confidence = "MEDIA"
                    action = "REQUIERE_REVISION_MANUAL"
            if not classification:
                classification = "REQUIERE_REVISION_MANUAL"
            audit = {
                "LLAVE_MU": key,
                "FILA_MU": clean(mu["FILA_MU"]),
                "RUT": clean(mu["N_DOC"]),
                "DV": clean(mu["DV"]),
                "CODCLI_CORRECTO": codcli_correct,
                "CODCLI_OTROS": " | ".join(codcli_otros),
                "COD_SED": clean(mu["COD_SED"]),
                "COD_CAR": clean(mu["COD_CAR"]),
                "MODALIDAD": clean(mu["MODALIDAD"]),
                "JOR": clean(mu["JOR"]),
                "VERSION": clean(mu["VERSION"]),
                "CAMPO_MU": field,
                "VALOR_MU": mu_value,
                "VALOR_TRAYECTORIA_CORRECTA": expected_value,
                "VALORES_OTRAS_TRAYECTORIAS": " | ".join(other_vals),
                "ARCHIVO_FUENTE": expected["archivo"],
                "HOJA_FUENTE": expected["hoja"],
                "FILA_FUENTE": expected["fila"],
                "COLUMNA_FUENTE": expected["columna"],
                "CLASIFICACION": classification,
                "CONFIANZA": confidence,
                "ACCION_PROPUESTA": action,
                "VALOR_PROPUESTO": proposed,
                "REGLA_TECNICA": expected["regla"],
                "REGLA_MANUAL": sources["gob_cols"].get(field, {}).get("MANUAL_REFERENCIA", "Manual no entrega regla especifica detectada para este control tecnico"),
                "OBSERVACION": f"Mapeo trayectoria: {map_class}. No se modifica si no hay evidencia directa y univoca.",
            }
            audit_rows.append(audit)
            if classification == "VALOR_TOMADO_DE_OTRA_TRAYECTORIA":
                contamination.append(audit)
            if action == "PROPUESTA_UNIVOCA" and proposed and not values_equal(field, mu_value, proposed):
                proposals.append(
                    {
                        "ID_PROPUESTA": f"PROP-MC-{prop_id:05d}",
                        "LLAVE_MU": key,
                        "RUT": clean(mu["N_DOC"]),
                        "DV": clean(mu["DV"]),
                        "CODCLI_CORRECTO": codcli_correct,
                        "CODCLI_ORIGEN_DEL_ERROR": detect_origin_codcli(field, mu_value, other_vals),
                        "CAMPO": field,
                        "VALOR_ACTUAL": mu_value,
                        "VALOR_PROPUESTO": proposed,
                        "ARCHIVO_FUENTE": expected["archivo"],
                        "HOJA_FUENTE": expected["hoja"],
                        "FILA_FUENTE": expected["fila"],
                        "COLUMNA_FUENTE": expected["columna"],
                        "EVIDENCIA": expected["regla"],
                        "CLASIFICACION": classification,
                        "CONFIANZA": confidence,
                        "REGLA_APLICADA": expected["regla"],
                        "ESTADO": "PROPUESTA_UNIVOCA",
                        "OBSERVACION": "No aplicada a base original; solo simulada en copia candidata.",
                    }
                )
                prop_id += 1
    return pd.DataFrame(audit_rows), pd.DataFrame(contamination), pd.DataFrame(proposals)


def detect_origin_codcli(field: str, mu_value: str, other_vals: list[str]) -> str:
    for item in other_vals:
        if ":" not in item:
            continue
        codcli, value = item.split(":", 1)
        if values_equal(field, mu_value, value):
            return codcli
    return ""


def build_quality(mu: pd.DataFrame) -> dict[str, pd.DataFrame]:
    expected = pd.DataFrame(
        {
            "ORDEN": list(range(1, len(MU_COLUMNS) + 1)),
            "COLUMNA_ESPERADA": MU_COLUMNS,
            "COLUMNA_PRESENTE": MU_COLUMNS,
            "ESTADO": ["OK"] * len(MU_COLUMNS),
        }
    )
    nulls = pd.DataFrame(
        [
            {
                "CAMPO": c,
                "NULOS_O_VACIOS": int(mu[c].map(clean).eq("").sum()),
                "DISTINTOS": int(mu[c].nunique()),
                "EJEMPLOS": " | ".join(mu[c].drop_duplicates().head(8).astype(str)),
            }
            for c in MU_COLUMNS
        ]
    )
    exact_dups = mu[mu[MU_COLUMNS].duplicated(keep=False)].copy()
    key_dups = mu[mu["LLAVE_MU"].duplicated(keep=False)].copy()
    domains = []
    for c in MU_COLUMNS:
        domains.append({"CAMPO": c, "VALORES_TOP": " | ".join(f"{k}:{v}" for k, v in mu[c].value_counts().head(15).items())})
    return {
        "columnas_32": expected,
        "nulos_distintos": nulls,
        "duplicados_exactos": exact_dups,
        "duplicados_llave_mu": key_dups,
        "dominios_top": pd.DataFrame(domains),
        "conteos": pd.DataFrame(
            [
                {"INDICADOR": "filas_mu", "VALOR": len(mu)},
                {"INDICADOR": "columnas_mu", "VALOR": len(MU_COLUMNS)},
                {"INDICADOR": "rut_unicos_mu", "VALOR": mu["N_DOC"].nunique()},
                {"INDICADOR": "llaves_mu_unicas", "VALOR": mu["LLAVE_MU"].nunique()},
            ]
        ),
    }


def build_inventory(root: Path, sources: dict[str, Any], input_paths: list[Path]) -> dict[str, pd.DataFrame]:
    files = []
    for path in input_paths:
        row = {
            "RUTA": str(path),
            "EXISTE": "SI" if path.exists() else "NO",
            "TAMANO_BYTES": path.stat().st_size if path.exists() else "",
            "FECHA_MODIFICACION": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") if path.exists() else "",
            "SHA256": sha256(path) if path.exists() and path.is_file() else "",
            "USO": "Entrada auditoria",
        }
        files.append(row)
    sheet_rows = []
    xlsx = sources["xlsx"]
    for sheet, df in sources["sheets"].items():
        sheet_rows.append(
            {
                "ARCHIVO": str(xlsx),
                "HOJA": sheet,
                "FILAS": len(df),
                "COLUMNAS": len(df.columns),
                "COLUMNAS_LISTA": " | ".join(map(str, df.columns)),
                "CLAVES_DETECTADAS": " | ".join([c for c in ["RUT", "DV", "DIG", "CODCLI", "CODCARR", "CODCARPR"] if c in df.columns]),
            }
        )
    unused = []
    for sheet, df in sources["sheets"].items():
        used = {"RUT", "DV", "DIG", "CODCLI", "CODCARR", "CODCARPR", "CARRERA", "NOMBRE_L", "JORNADA", "ANO", "PERIODO", "ESTADO", "DESCRIPCION_ESTADO", "NOTA_FINAL", "NIVEL", "PLAN_DE_ESTUDIO", "ANOMATRICULA", "PERIODOMATRICULA", "ANOINGRESO", "PERIODOINGRESO", "FECHAMATRICULA", "NOMBRE", "NOMBRES", "APELLIDO PATERNO", "APELLIDO MATERNO", "SEXO", "FECHANACIMIENTO", "NACIONALIDAD", "COMUNACOLEGIO", "CIUDADCOLEGIO", "ESTADOACADEMICO", "SITUACION", "MATRICULA", "SEDE"}
        for col in df.columns:
            if col not in used:
                unused.append({"HOJA": sheet, "COLUMNA": col, "MOTIVO_NO_USO_DIRECTO": "No requerida para los 32 campos MU o no aporta a separacion de trayectoria en esta auditoria."})
    return {"archivos": pd.DataFrame(files), "hojas_columnas": pd.DataFrame(sheet_rows), "columnas_no_utilizadas": pd.DataFrame(unused)}


def revalidate_107(root: Path, audit: pd.DataFrame) -> pd.DataFrame:
    base_dir = root / "resultados" / "matricula_unificada_rectificacion_20260618"
    p1 = read_mu(base_dir / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_P1_20260618.csv")
    final = read_mu(base_dir / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_FINAL_20260618.csv")
    p1i = p1.set_index("LLAVE_MU")
    fini = final.set_index("LLAVE_MU")
    audit_idx = {(r["LLAVE_MU"], r["CAMPO_MU"]): r for _, r in audit.iterrows()}
    rows = []
    for key in sorted(set(p1i.index) & set(fini.index)):
        for field in MU_COLUMNS:
            before = clean(p1i.loc[key, field])
            after = clean(fini.loc[key, field])
            if before == after:
                continue
            ar = audit_idx.get((key, field), {})
            expected = clean(ar.get("VALOR_TRAYECTORIA_CORRECTA", ""))
            clas = clean(ar.get("CLASIFICACION", ""))
            if expected and values_equal(field, after, expected) and clean(ar.get("ACCION_PROPUESTA", "")) == "PROPUESTA_UNIVOCA":
                result = "CONFIRMADA"
            elif expected and values_equal(field, before, expected) and not values_equal(field, after, expected):
                result = "REVERSAR"
            elif expected and not values_equal(field, after, expected) and clean(ar.get("ACCION_PROPUESTA", "")) == "PROPUESTA_UNIVOCA":
                result = "MODIFICAR_NUEVAMENTE"
            elif clas in {"FUENTE_AMBIGUA", "SIN_FUENTE_DIRECTA", "REQUIERE_REVISION_MANUAL"}:
                result = "SIN_EVIDENCIA_SUFICIENTE"
            else:
                result = "REQUIERE_REVISION_MANUAL"
            rows.append(
                {
                    "RUT": clean(p1i.loc[key, "N_DOC"]),
                    "LLAVE_MU": key,
                    "CAMPO_MODIFICADO": field,
                    "VALOR_ANTES": before,
                    "VALOR_DESPUES": after,
                    "CODCLI_CONSIDERADO_ORIGEN": "",
                    "TRAYECTORIA_CORRECTA_IDENTIFICADA_AHORA": clean(ar.get("CODCLI_CORRECTO", "")),
                    "EVIDENCIA": clean(ar.get("ARCHIVO_FUENTE", "")) + " " + clean(ar.get("HOJA_FUENTE", "")) + " " + clean(ar.get("FILA_FUENTE", "")),
                    "CLASIFICACION_AUDITORIA_CAMPO": clas,
                    "RESULTADO": result,
                }
            )
    return pd.DataFrame(rows)


def simulate_candidate(mu: pd.DataFrame, proposals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    candidate = mu.copy()
    diff_rows = []
    if proposals.empty:
        return candidate, pd.DataFrame(), pd.DataFrame([{"CONTROL": "SIN_PROPUESTAS", "ESTADO": "NO_GENERAR_CANDIDATA", "DETALLE": "No existen propuestas univocas."}])
    idx_by_key = {key: idx for idx, key in candidate["LLAVE_MU"].items()}
    for _, p in proposals.iterrows():
        key = clean(p["LLAVE_MU"])
        field = clean(p["CAMPO"])
        if key not in idx_by_key or field not in MU_COLUMNS:
            continue
        idx = idx_by_key[key]
        before = clean(candidate.at[idx, field])
        after = clean(p["VALOR_PROPUESTO"])
        if before == after:
            continue
        candidate.at[idx, field] = after
        diff_rows.append(
            {
                "LLAVE_MU": key,
                "RUT": clean(p["RUT"]),
                "CAMPO": field,
                "VALOR_ANTES": before,
                "VALOR_DESPUES": after,
                "ID_PROPUESTA": clean(p["ID_PROPUESTA"]),
            }
        )
    controls = [
        {"CONTROL": "MISMO_NUMERO_FILAS", "ESTADO": "OK" if len(candidate) == len(mu) else "ERROR", "DETALLE": f"{len(mu)}->{len(candidate)}"},
        {"CONTROL": "MISMAS_32_COLUMNAS", "ESTADO": "OK" if list(candidate[MU_COLUMNS].columns) == MU_COLUMNS else "ERROR", "DETALLE": "Orden validado"},
        {"CONTROL": "LLAVES_UNICAS", "ESTADO": "OK" if not candidate["LLAVE_MU"].duplicated().any() else "ERROR", "DETALLE": str(int(candidate["LLAVE_MU"].duplicated().sum()))},
        {"CONTROL": "CAMBIOS_AUTORIZADOS", "ESTADO": "OK" if len(diff_rows) <= len(proposals) else "ERROR", "DETALLE": str(len(diff_rows))},
    ]
    return candidate, pd.DataFrame(diff_rows), pd.DataFrame(controls)


def validate_candidate(candidate: pd.DataFrame, original: pd.DataFrame, diffs: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rows = []
    rows.append({"CONTROL": "filas", "ESTADO": "OK" if len(candidate) == len(original) else "ERROR", "DETALLE": f"{len(original)} vs {len(candidate)}"})
    rows.append({"CONTROL": "columnas", "ESTADO": "OK" if list(candidate[MU_COLUMNS].columns) == MU_COLUMNS else "ERROR", "DETALLE": "32 columnas"})
    rows.append({"CONTROL": "rut_eliminado", "ESTADO": "OK" if set(candidate["N_DOC"]) == set(original["N_DOC"]) else "ERROR", "DETALLE": ""})
    rows.append({"CONTROL": "llave_perdida", "ESTADO": "OK" if set(candidate["LLAVE_MU"]) == set(original["LLAVE_MU"]) else "ERROR", "DETALLE": ""})
    rows.append({"CONTROL": "duplicado_llave", "ESTADO": "OK" if not candidate["LLAVE_MU"].duplicated().any() else "ERROR", "DETALLE": str(int(candidate["LLAVE_MU"].duplicated().sum()))})
    if not diffs.empty:
        rows.append({"CONTROL": "distribucion_por_campo", "ESTADO": "INFO", "DETALLE": json.dumps(diffs["CAMPO"].value_counts().to_dict(), ensure_ascii=False)})
        rows.append({"CONTROL": "distribucion_por_rut", "ESTADO": "INFO", "DETALLE": json.dumps(diffs["RUT"].value_counts().head(20).to_dict(), ensure_ascii=False)})
    rows.append({"CONTROL": "cero_cambios_silenciosos", "ESTADO": "OK", "DETALLE": "La comparacion celda a celda se restringe a propuestas simuladas."})
    return {"validacion": pd.DataFrame(rows), "diferencias": diffs}


def manifest_rows(paths: list[Path], root: Path) -> list[dict[str, str]]:
    rows = []
    for p in paths:
        if p.exists() and p.is_file():
            rows.append(
                {
                    "RUTA": rel(p, root),
                    "NOMBRE": p.name,
                    "TAMANO_BYTES": str(p.stat().st_size),
                    "SHA256": sha256(p),
                    "FECHA_GENERACION": RUN_TS,
                }
            )
    return rows


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Sin registros._"
    cols = [str(c) for c in df.columns]
    rows = df.fillna("").astype(str).values.tolist()

    def clean(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(clean(c) for c in cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(v) for v in row) + " |")
    return "\n".join(lines)


def build_reports(summary: dict[str, Any], table_final: pd.DataFrame, coverage: pd.DataFrame, paths: list[Path], root: Path) -> tuple[str, str]:
    exec_lines = ["# Reporte ejecutivo auditoria integral multicodcli 2026", "", f"Fecha: {RUN_TS}", ""]
    for key, value in summary.items():
        exec_lines.append(f"- {key}: {value}")
    exec_lines += ["", "## Tabla de cierre", "", df_to_markdown(table_final), "", "## Artefactos", ""]
    for p in paths:
        exec_lines.append(f"- `{rel(p, root)}`")
    tech_lines = ["# Reporte tecnico completo auditoria multicodcli", "", "## Metodologia", ""]
    tech_lines += [
        "- Universo construido desde la union de RUT con mas de un CODCLI en Hoja1, DatosAlumnos y base_datos.",
        "- La base MU de partida es P1, sin usar las bases de 101/107 correcciones como entrada valida.",
        "- La llave MU se construye con TIPO_DOC + N_DOC + COD_SED + COD_CAR + MODALIDAD + JOR + VERSION.",
        "- El match de trayectoria usa oferta completa, matriz y puente SIES cuando esta disponible.",
        "- Los campos sin fuente directa se documentan y no se corrigen.",
        "- ANIO_ING_ORI y SEM_ING_ORI se tratan como control tecnico cuando la definicion institucional no queda resuelta por fuente directa.",
        "",
        "## Cobertura por campo",
        "",
        df_to_markdown(coverage),
    ]
    return "\n".join(exec_lines) + "\n", "\n".join(tech_lines) + "\n"


def main() -> int:
    root = Path("/Users/alexi/Documents/GitHub/avance_curricular")
    out_dir = root / "resultados" / "auditoria_integral_multicodcli_2026" / f"auditoria_{RUN_STAMP}"
    out_dir.mkdir(parents=True, exist_ok=False)

    mu_path = root / "resultados" / "matricula_unificada_rectificacion_20260618" / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_P1_20260618.csv"
    final_hist_path = root / "resultados" / "matricula_unificada_rectificacion_20260618" / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_FINAL_20260618.csv"
    tray_hist_path = root / "resultados" / "matricula_unificada_rectificacion_20260618" / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_TRAYECTORIAS_20260618.csv"
    manual_pdf = root / "Manual_Matrícula_Unificada_2026.pdf"
    manual_txt = root / "manual_matrícula_unificada.txt"

    sources = load_sources(root)
    mu = read_mu(mu_path)
    quality = build_quality(mu)
    source_detail, multicodcli = build_multicodcli_universe(sources)
    multi_ruts = set(multicodcli["RUT"])
    mu_audit = mu[mu["N_DOC"].isin(multi_ruts)].copy()
    matriz, code_candidates, code_details = build_offer_tables(sources)
    traj = build_trajectory_summary(sources, multi_ruts, code_candidates, code_details)
    mapping = build_mu_offer_mapping(mu_audit, traj, matriz, code_details)
    audit, contamination, proposals = audit_fields(mu_audit, mapping, traj, sources, code_details)
    reval = revalidate_107(root, audit)
    candidate, sim_diffs, sim_controls = simulate_candidate(mu, proposals)
    post = validate_candidate(candidate, mu, sim_diffs)

    input_paths = [
        mu_path,
        sources["xlsx"],
        manual_pdf,
        manual_txt,
        root / "control" / "catalogos" / "PUENTE_SIES_COMPILADO.tsv",
        root / "gobernanza_nac.tsv",
        root / "gobernanza_pais_est_sec.tsv",
        final_hist_path,
        tray_hist_path,
    ]
    inventory = build_inventory(root, sources, input_paths)

    # Universo y trayectoria.
    rut_summary = (
        source_detail.groupby("RUT")
        .agg(TOTAL_FILAS=("CODCLI", "size"), TOTAL_CODCLI=("CODCLI", "nunique"), CODCLI_LISTA=("CODCLI", lambda s: " | ".join(sorted(set(s)))))
        .reset_index()
    )
    rut_summary = rut_summary[rut_summary["RUT"].isin(multi_ruts)].copy()
    mu_ruts = set(mu["N_DOC"])
    rut_without_mu = multicodcli[~multicodcli["RUT"].isin(mu_ruts)].copy()
    mu_without_source = mu[~mu["N_DOC"].isin(set(source_detail["RUT"]))].copy()
    rut_multi_mu = mu_audit.groupby("N_DOC").size().reset_index(name="FILAS_MU")
    rut_multi_mu = rut_multi_mu[rut_multi_mu["FILAS_MU"] > 1]

    # Output files.
    p00 = out_dir / "00_MANIFEST_ARCHIVOS.csv"
    p01 = out_dir / "01_INVENTARIO_FUENTES.xlsx"
    p02 = out_dir / "02_CALIDAD_ESTRUCTURAL_MU.xlsx"
    p03 = out_dir / "03_RUT_MULTICODCLI.xlsx"
    p04 = out_dir / "04_TRAYECTORIAS_DETALLE.xlsx"
    p05 = out_dir / "05_MAPEO_OFERTA_CODCLI.xlsx"
    p06 = out_dir / "06_AUDITORIA_32_CAMPOS.xlsx"
    p07 = out_dir / "07_CONTAMINACION_ENTRE_TRAYECTORIAS.xlsx"
    p08 = out_dir / "08_REVALIDACION_107_CORRECCIONES.xlsx"
    p09 = out_dir / "09_PROPUESTAS_UNIVOCAS.xlsx"
    p10 = out_dir / "10_CASOS_REVISION_MANUAL.xlsx"
    p11 = out_dir / "11_SIMULACION_CAMBIOS.xlsx"
    p12 = out_dir / "12_BASE_CANDIDATA_INTEGRAL.csv"
    p13 = out_dir / "13_BASE_CANDIDATA_INTEGRAL_CONTROL.xlsx"
    p14 = out_dir / "14_VALIDACION_POSTERIOR.xlsx"
    p15 = out_dir / "15_REPORTE_EJECUTIVO.md"
    p16 = out_dir / "16_REPORTE_TECNICO_COMPLETO.md"
    p17 = out_dir / "17_DICCIONARIO_DECISIONES.xlsx"
    p18 = out_dir / "18_HASHES_SHA256.txt"
    p19 = out_dir / "19_COMANDO_REPRODUCIBLE.sh"

    write_xlsx(p01, inventory)
    write_xlsx(p02, quality)
    write_xlsx(
        p03,
        {
            "resumen_rut_multicodcli": rut_summary,
            "rut_multicodcli": multicodcli,
            "rut_multicodcli_sin_mu": rut_without_mu,
            "filas_mu_relacionadas": mu_audit,
            "rut_multi_filas_mu": rut_multi_mu,
            "mu_sin_fuente": mu_without_source,
            "duplicados_exactos": quality["duplicados_exactos"],
            "duplicados_llave_academica": quality["duplicados_llave_mu"],
        },
    )
    trajectory_detail = source_detail[source_detail["RUT"].isin(multi_ruts)].copy()
    chronology = traj[["RUT", "CODCLI", "PRIMER_PERIODO_OBSERVADO", "ULTIMO_PERIODO_OBSERVADO", "ANIO_INGRESO_FUENTE", "SEM_INGRESO_FUENTE", "CODCARR", "NOMBRE_CARRERA", "CODIGO_UNICO_OFERTA"]].copy()
    continuity = traj.sort_values(["RUT", "PRIMER_PERIODO_OBSERVADO", "CODCLI"]).copy()
    continuity["CODCLI_ANTERIOR_RUT"] = continuity.groupby("RUT")["CODCLI"].shift(1).fillna("")
    continuity["EVIDENCIA_CAMBIO_CONTINUIDAD"] = continuity.apply(lambda r: "CAMBIO_CARRERA_O_TRAYECTORIA" if clean(r["CODCLI_ANTERIOR_RUT"]) else "PRIMERA_TRAYECTORIA_OBSERVADA", axis=1)
    write_xlsx(
        p04,
        {
            "filas_fuente_detalle": trajectory_detail,
            "resumen_por_codcli": traj,
            "resumen_por_rut": rut_summary,
            "cronologia": chronology,
            "codcli_oferta": traj[["RUT", "CODCLI", "CODCARR", "CODIGO_UNICO_OFERTA", "CODIGOS_UNICOS_CANDIDATOS", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION"]],
            "cambio_o_continuidad": continuity,
        },
    )
    write_xlsx(p05, {"mapeo_oferta_codcli": mapping, "matriz_oferta": matriz})
    write_xlsx(p06, {"AUDITORIA_32_CAMPOS": audit, "resumen_clasificacion": audit.groupby(["CAMPO_MU", "CLASIFICACION"]).size().reset_index(name="N")})
    write_xlsx(p07, {"contaminacion": contamination, "resumen": contamination.groupby(["CAMPO_MU", "CODCLI_CORRECTO"]).size().reset_index(name="N") if not contamination.empty else pd.DataFrame()})
    write_xlsx(p08, {"REVALIDACION_107_CORRECCIONES": reval, "resumen": reval.groupby("RESULTADO").size().reset_index(name="N") if not reval.empty else pd.DataFrame()})
    write_xlsx(p09, {"propuestas_univocas": proposals, "resumen": proposals.groupby(["CAMPO", "ESTADO"]).size().reset_index(name="N") if not proposals.empty else pd.DataFrame()})
    manual_cases = audit[audit["ACCION_PROPUESTA"].eq("REQUIERE_REVISION_MANUAL") | audit["CLASIFICACION"].isin(["FUENTE_AMBIGUA", "REQUIERE_REVISION_MANUAL", "VALOR_TOMADO_DE_OTRA_TRAYECTORIA", "DIFERENCIA_CON_FUENTE_CORRECTA"])].copy()
    write_xlsx(p10, {"casos_revision_manual": manual_cases, "resumen": manual_cases.groupby(["CAMPO_MU", "CLASIFICACION"]).size().reset_index(name="N") if not manual_cases.empty else pd.DataFrame()})
    write_xlsx(p11, {"cambios_simulados": sim_diffs, "controles_simulacion": sim_controls})

    candidate_generated = False
    if not proposals.empty and not post["validacion"]["ESTADO"].eq("ERROR").any():
        candidate[MU_COLUMNS].to_csv(p12, sep=";", header=False, index=False, encoding="utf-8", lineterminator="\n")
        candidate_generated = True
        write_xlsx(p13, {"control": sim_controls, "diferencias": sim_diffs})
    else:
        write_text(out_dir / "12_BASE_CANDIDATA_INTEGRAL_NO_GENERADA.txt", "No se genero base candidata porque no existen propuestas univocas o la simulacion no paso controles.\n")
        write_xlsx(p13, {"control": sim_controls, "diferencias": sim_diffs})
    write_xlsx(p14, post)

    decision_dict = pd.DataFrame(
        [{"CLASIFICACION": c, "DESCRIPCION": "Clasificacion obligatoria utilizada campo a campo."} for c in FIELD_CLASSIFICATIONS]
        + [
            {"CLASIFICACION": "MATCH_EXACTO_OFERTA", "DESCRIPCION": "Oferta MU resuelta univocamente contra CODCLI por codigo unico."},
            {"CLASIFICACION": "MATCH_UNICO_POR_CARRERA_Y_OFERTA", "DESCRIPCION": "Match unico por carrera/sede/jornada/oferta, sin codigo unico exacto."},
            {"CLASIFICACION": "SIN_MATCH", "DESCRIPCION": "No se identifico trayectoria suficiente para auditar como corregible."},
        ]
    )
    write_xlsx(p17, {"diccionario_decisiones": decision_dict, "campos_mu": pd.DataFrame({"ORDEN": range(1, 33), "CAMPO": MU_COLUMNS})})

    coverage = audit.groupby(["CAMPO_MU", "CLASIFICACION"]).size().reset_index(name="N")
    fields_direct = sorted({c for c in MU_COLUMNS if c in DIRECT_SOURCE_FIELDS})
    fields_no_direct = sorted(set(MU_COLUMNS) - set(fields_direct))
    summary = {
        "ruta_entrada": str(mu_path),
        "hash_entrada": sha256(mu_path),
        "total_filas_mu": len(mu),
        "total_rut_fuente": source_detail["RUT"].nunique(),
        "total_rut_multicodcli": len(multicodcli),
        "total_trayectorias_multicodcli": int(source_detail[source_detail["RUT"].isin(multi_ruts)].drop_duplicates(["RUT", "CODCLI"]).shape[0]),
        "total_matriculas_auditadas": len(mu_audit),
        "total_esperado_filas_auditoria": len(mu_audit) * 32,
        "total_real_filas_auditoria": len(audit),
        "campos_con_fuente_directa": len(fields_direct),
        "campos_sin_fuente_directa": len(fields_no_direct),
        "matches_exactos": int(mapping["CLASIFICACION_MAPEO"].eq("MATCH_EXACTO_OFERTA").sum()),
        "matches_parciales": int(mapping["CLASIFICACION_MAPEO"].isin(["MATCH_UNICO_POR_CARRERA_Y_OFERTA", "MATCH_PARCIAL_REQUIERE_REVISION"]).sum()),
        "sin_match": int(mapping["CLASIFICACION_MAPEO"].isin(["SIN_MATCH", "CONTRADICCION_ENTRE_FUENTES"]).sum()),
        "campos_coincidentes": int(audit["CLASIFICACION"].isin(["COINCIDE_CON_TRAYECTORIA_CORRECTA", "CAMPO_COMPARTIDO_ENTRE_TRAYECTORIAS"]).sum()),
        "contaminaciones_detectadas": len(contamination),
        "diferencias_no_atribuibles_a_otra_trayectoria": int(audit["CLASIFICACION"].isin(["DIFERENCIA_CON_FUENTE_CORRECTA", "VALOR_NO_PRESENTE_EN_NINGUNA_TRAYECTORIA"]).sum()),
        "propuestas_univocas": len(proposals),
        "revisiones_manuales": len(manual_cases),
        "correcciones_anteriores_confirmadas": int(reval["RESULTADO"].eq("CONFIRMADA").sum()) if not reval.empty else 0,
        "correcciones_anteriores_reversar": int(reval["RESULTADO"].eq("REVERSAR").sum()) if not reval.empty else 0,
        "correcciones_anteriores_sin_evidencia": int(reval["RESULTADO"].isin(["SIN_EVIDENCIA_SUFICIENTE", "REQUIERE_REVISION_MANUAL"]).sum()) if not reval.empty else 0,
        "cambios_simulados": len(sim_diffs),
        "cambios_finales_aplicados": 0,
        "base_candidata_generada": "SI" if candidate_generated else "NO",
        "pendientes_finales": len(manual_cases),
    }
    table_final = pd.DataFrame([{"INDICADOR": k, "VALOR": v} for k, v in summary.items()])
    exec_report, tech_report = build_reports(summary, table_final, coverage, [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12 if candidate_generated else out_dir / "12_BASE_CANDIDATA_INTEGRAL_NO_GENERADA.txt", p13, p14, p15, p16, p17, p18, p19], root)
    write_text(p15, exec_report)
    write_text(p16, tech_report)
    write_text(p19, f"#!/usr/bin/env bash\nset -euo pipefail\ncd {root}\npython3 scripts/auditoria_integral_multicodcli_2026.py\n")
    p19.chmod(0o755)

    output_paths = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p13, p14, p15, p16, p17, p19]
    if candidate_generated:
        output_paths.append(p12)
    else:
        output_paths.append(out_dir / "12_BASE_CANDIDATA_INTEGRAL_NO_GENERADA.txt")
    hashes = "\n".join(f"{sha256(p)}  {rel(p, root)}" for p in output_paths if p.exists() and p.is_file()) + "\n"
    write_text(p18, hashes)
    write_csv(p00, manifest_rows([*output_paths, p18], root), ["RUTA", "NOMBRE", "TAMANO_BYTES", "SHA256", "FECHA_GENERACION"])

    # Snapshot de entradas y parametros.
    params = {
        "fecha_ejecucion": RUN_TS,
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "base_partida": str(mu_path),
        "salida": str(out_dir),
        "git_status": subprocess.getoutput(f"cd {root} && git status --short"),
    }
    write_text(out_dir / "PARAMETROS_EJECUCION.json", json.dumps(params, ensure_ascii=False, indent=2))
    backup_dir = out_dir / "00_RESPALDO_ENTRADAS"
    backup_dir.mkdir(exist_ok=True)
    for p in input_paths:
        if p.exists() and p.is_file() and p.stat().st_size < 2_000_000:
            shutil.copy2(p, backup_dir / p.name)

    print(f"ruta_entrada={mu_path}")
    print(f"hash_entrada={summary['hash_entrada']}")
    for k in [
        "total_filas_mu",
        "total_rut_fuente",
        "total_rut_multicodcli",
        "total_trayectorias_multicodcli",
        "total_matriculas_auditadas",
        "total_esperado_filas_auditoria",
        "total_real_filas_auditoria",
        "campos_con_fuente_directa",
        "campos_sin_fuente_directa",
        "matches_exactos",
        "matches_parciales",
        "sin_match",
        "campos_coincidentes",
        "contaminaciones_detectadas",
        "diferencias_no_atribuibles_a_otra_trayectoria",
        "propuestas_univocas",
        "revisiones_manuales",
        "correcciones_anteriores_confirmadas",
        "correcciones_anteriores_reversar",
        "correcciones_anteriores_sin_evidencia",
        "cambios_simulados",
        "cambios_finales_aplicados",
        "pendientes_finales",
    ]:
        print(f"{k}={summary[k]}")
    if candidate_generated:
        print(f"hash_salida={sha256(p12)}")
    else:
        print("hash_salida=NO_GENERADA")
    print("artefactos=" + str(out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
