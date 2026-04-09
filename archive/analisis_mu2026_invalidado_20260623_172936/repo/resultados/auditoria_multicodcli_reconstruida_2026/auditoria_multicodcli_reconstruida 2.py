#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


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

CRITICAL_FIELDS = ["ANIO_ING_ORI", "NIV_ACA", "COD_CAR", "MODALIDAD", "JOR"]
ACTIVE_STATUSES = {
    "VIGENTE_2026_1_CONFIRMADO",
    "VIGENTE_SIMULTANEO",
    "VIGENTE_PARA_OTRA_OFERTA",
}

JORNADA_TO_MU = {
    "D": ("1", "1"),
    "V": ("1", "2"),
    "O": ("3", "4"),
}

SEDE_TO_MU = {
    "RE": "2",
    "CO": "3",
    "CASA CENTRAL (SANTIAGO)": "2",
    "SANTIAGO": "2",
    "SEDE CONCEPCION": "3",
    "CONCEPCION": "3",
}


@dataclass
class Trajectory:
    rut: str
    dv: str = ""
    nombre: str = ""
    codcli: str = ""
    codcarr: str = ""
    carrera: str = ""
    jornada_fuente: str = ""
    sede_fuente: str = ""
    cod_sed_fuente: str = ""
    anio_ingreso: str = ""
    periodo_ingreso: str = ""
    nivel_fuente: str = ""
    actividad_2026_1: str = "NO"
    estado_vigencia: str = "SIN_EVIDENCIA_2026_1"
    primer_periodo: str = ""
    ultimo_periodo: str = ""
    source_file: str = ""
    source_sheet: str = ""
    source_row: str = ""
    evidencia: str = ""
    da_rows: pd.DataFrame = field(default_factory=pd.DataFrame)
    h_rows: pd.DataFrame = field(default_factory=pd.DataFrame)
    bd_rows: pd.DataFrame = field(default_factory=pd.DataFrame)
    offer_candidates: list[dict[str, str]] = field(default_factory=list)
    offer_match_quality: str = ""
    identity_status: str = "IDENTIDAD_CONFIRMADA_POR_RUT"
    observacion_identidad: str = ""
    matched_any_mu: bool = False
    exact_active_mu_matches: int = 0

    @property
    def is_active_confirmed(self) -> bool:
        return self.estado_vigencia in ACTIVE_STATUSES

    @property
    def is_historical(self) -> bool:
        return self.estado_vigencia == "HISTORICO_NO_VIGENTE"


def clean(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except TypeError:
        pass
    if isinstance(v, float) and math.isfinite(v) and v.is_integer():
        return str(int(v))
    s = str(v).strip()
    if s.lower() in {"nan", "none", "nat"}:
        return ""
    if re.fullmatch(r"-?\d+\.0", s):
        return s[:-2]
    return s.strip()


def norm_text(v: Any) -> str:
    s = clean(v).upper()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def norm_num(v: Any) -> str:
    s = clean(v)
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return re.sub(r"\s+", "", s)


def parse_rut(rut_value: Any, dv_value: Any = "") -> tuple[str, str]:
    rut_s = clean(rut_value).replace(".", "").strip()
    dv_s = clean(dv_value).upper().replace(".", "").strip()
    if "-" in rut_s:
        base, dv = rut_s.rsplit("-", 1)
        rut_s = base
        dv_s = dv
    rut_digits = re.sub(r"\D", "", rut_s)
    dv_s = re.sub(r"[^0-9Kk]", "", dv_s).upper()
    return rut_digits, dv_s


def period_tuple(year: Any, period: Any) -> tuple[int, int] | None:
    y = norm_num(year)
    p = norm_num(period)
    if not y or not p or not y.isdigit() or not p.isdigit():
        return None
    return int(y), int(p)


def format_period(period: tuple[int, int] | None) -> str:
    if period is None:
        return ""
    return f"{period[0]}-{period[1]}"


def join_unique(values: list[Any] | set[Any], sep: str = " | ") -> str:
    cleaned: list[str] = []
    seen: set[str] = set()
    for v in values:
        s = clean(v)
        if not s or s in seen:
            continue
        cleaned.append(s)
        seen.add(s)
    return sep.join(sorted(cleaned, key=lambda x: (len(x), x)))


def normalize_career_variants(carrera: str) -> list[str]:
    n = norm_text(carrera)
    variants = [n]

    if n.startswith("CONTINUIDAD "):
        base = n.replace("CONTINUIDAD ", "", 1)
        base = re.sub(r"\bINGENIERIA\s+", "INGENIERIA ", base)
        variants.append(base)
        if base.startswith("INGENIERIA ") and not base.startswith("INGENIERIA EN ") and base != "INGENIERIA INDUSTRIAL":
            variants.append("INGENIERIA EN " + base[len("INGENIERIA ") :])
        if base == "EN PREVENCION DE RIESGOS":
            variants.append("INGENIERIA EN PREVENCION DE RIESGOS")

    if n == "CONTINUIDAD EN PREVENCION DE RIESGOS":
        variants.append("INGENIERIA EN PREVENCION DE RIESGOS")

    replacements = {
        "DIPLOMADO EN FULL STACK": "DIPLOMADO EN FULLSTACK",
        "DIPLOMADO EN REDES INDUSTRIALES": "DIPLOMADO REDES INDUSTRIALES",
        "DIPLOMADO EN CIBERSEGURIDAD": "DIPLOMADO EN CIBERSEGURIDAD APLICADA",
        "INGENIERIA EN INFORMATICA": "INGENIERIA EN INFORMATICA",
        "INGENIERIA EN CONECTIVIDAD Y REDES": "INGENIERIA EN CONECTIVIDAD Y REDES",
    }
    if n in replacements:
        variants.append(replacements[n])

    compact = n.replace(" ", "")
    if "FULLSTACK" in compact:
        variants.append("DIPLOMADO EN FULLSTACK")

    output: list[str] = []
    for v in variants:
        v = re.sub(r"\s+", " ", v).strip()
        if v and v not in output:
            output.append(v)
    return output


def is_continuity(codcarr: str, carrera: str) -> bool:
    code = norm_text(codcarr)
    career = norm_text(carrera)
    return career.startswith("CONTINUIDAD") or code.startswith("CI") or code.startswith("CA")


def build_matrix_candidates(matriz: pd.DataFrame) -> dict[tuple[str, str, str, str], list[dict[str, str]]]:
    mat = matriz.copy()
    mat["COD_CAR"] = mat["CODIGO_UNICO"].astype(str).str.extract(r"C(\d+)J", expand=False).fillna("")
    mat["VERSION"] = mat["CODIGO_UNICO"].astype(str).str.extract(r"V(\d+)$", expand=False).fillna("")
    mat["NOMBRE_NORM"] = mat["NOMBRE_CARRERA"].map(norm_text)
    out: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for _, row in mat.iterrows():
        key = (
            clean(row["NOMBRE_NORM"]),
            norm_num(row["COD_SEDE"]),
            norm_num(row["MODALIDAD"]),
            norm_num(row["JORNADA"]),
        )
        out[key].append(
            {
                "CODIGO_UNICO": clean(row["CODIGO_UNICO"]),
                "COD_SED": norm_num(row["COD_SEDE"]),
                "COD_CAR": norm_num(row["COD_CAR"]),
                "MODALIDAD": norm_num(row["MODALIDAD"]),
                "JOR": norm_num(row["JORNADA"]),
                "VERSION": norm_num(row["VERSION"]),
                "CARRERA_MATRIZ": clean(row["NOMBRE_CARRERA"]),
                "TIPO_PLAN_CARRERA": norm_num(row["TIPO_PLAN_CARRERA"]),
                "DURACION_ESTUDIOS": norm_num(row["DURACION_ESTUDIOS"]),
                "NIVEL_CARRERA": norm_num(row["NIVEL_CARRERA"]),
                "VIGENCIA_MATRIZ": norm_num(row["VIGENCIA"]),
            }
        )
    return out


def candidate_offers_for_trajectory(
    tr: Trajectory, matrix_index: dict[tuple[str, str, str, str], list[dict[str, str]]]
) -> tuple[list[dict[str, str]], str]:
    career_variants = normalize_career_variants(tr.carrera)
    sede_code = tr.cod_sed_fuente
    jornada_letter = norm_text(tr.jornada_fuente)
    modalidad, jornada = JORNADA_TO_MU.get(jornada_letter, ("", ""))
    if not sede_code or not modalidad or not jornada:
        return [], "SIN_MAPEO_SEDE_JORNADA"

    candidates: list[dict[str, str]] = []
    for career_norm in career_variants:
        candidates.extend(matrix_index.get((career_norm, sede_code, modalidad, jornada), []))

    if not candidates:
        return [], "SIN_MATCH_MATRIZ"

    continuity = is_continuity(tr.codcarr, tr.carrera)
    if continuity:
        preferred = [c for c in candidates if c["TIPO_PLAN_CARRERA"] == "3"]
        if preferred:
            candidates = preferred
    else:
        preferred = [c for c in candidates if c["TIPO_PLAN_CARRERA"] != "3"]
        if preferred:
            candidates = preferred

    seen: set[tuple[str, str, str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for c in candidates:
        key = (c["COD_SED"], c["COD_CAR"], c["MODALIDAD"], c["JOR"], c["VERSION"])
        if key in seen:
            continue
        unique.append(c)
        seen.add(key)

    quality = "MATCH_MATRIZ_UNICO" if len(unique) == 1 else "MATCH_MATRIZ_MULTIPLES_VERSIONES"
    return unique, quality


def source_values_for_field(tr: Trajectory, field_name: str) -> set[str]:
    if field_name == "ANIO_ING_ORI":
        return {tr.anio_ingreso} if tr.anio_ingreso else set()
    if field_name == "NIV_ACA":
        return {tr.nivel_fuente} if tr.nivel_fuente else set()
    if field_name == "COD_CAR":
        return {c["COD_CAR"] for c in tr.offer_candidates if c.get("COD_CAR")}
    if field_name == "MODALIDAD":
        return {c["MODALIDAD"] for c in tr.offer_candidates if c.get("MODALIDAD")}
    if field_name == "JOR":
        return {c["JOR"] for c in tr.offer_candidates if c.get("JOR")}
    return set()


def offer_keys(tr: Trajectory) -> set[tuple[str, str, str, str, str]]:
    return {
        (c["COD_SED"], c["COD_CAR"], c["MODALIDAD"], c["JOR"], c["VERSION"])
        for c in tr.offer_candidates
        if c.get("COD_SED") and c.get("COD_CAR") and c.get("MODALIDAD") and c.get("JOR") and c.get("VERSION")
    }


def offer_keys_wo_version(tr: Trajectory) -> set[tuple[str, str, str, str]]:
    return {
        (c["COD_SED"], c["COD_CAR"], c["MODALIDAD"], c["JOR"])
        for c in tr.offer_candidates
        if c.get("COD_SED") and c.get("COD_CAR") and c.get("MODALIDAD") and c.get("JOR")
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_directory(path: Path) -> tuple[str, int, int]:
    h = hashlib.sha256()
    file_count = 0
    total_bytes = 0
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = file_path.relative_to(path).as_posix()
        file_hash = sha256_file(file_path)
        size = file_path.stat().st_size
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(file_hash.encode("ascii"))
        h.update(b"\0")
        h.update(str(size).encode("ascii"))
        h.update(b"\n")
        file_count += 1
        total_bytes += size
    return h.hexdigest(), file_count, total_bytes


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "Sin registros."
    text_df = df.copy().fillna("").astype(str)
    headers = list(text_df.columns)
    rows = text_df.values.tolist()
    widths = [
        max(len(str(header)), *(len(str(row[i])) for row in rows))
        for i, header in enumerate(headers)
    ]
    header_line = "| " + " | ".join(str(header).ljust(widths[i]) for i, header in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *body])


def sniff_csv_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter


def add_rut_columns_from_combined(df: pd.DataFrame, col: str, dv_col: str | None = None) -> pd.DataFrame:
    out = df.copy()
    ruts: list[str] = []
    dvs: list[str] = []
    for _, row in out.iterrows():
        rut, dv = parse_rut(row.get(col, ""), row.get(dv_col, "") if dv_col else "")
        ruts.append(rut)
        dvs.append(dv)
    out["_RUT_NUM"] = ruts
    out["_DV"] = dvs
    return out


def select_first_nonempty(rows: pd.DataFrame, columns: list[str]) -> str:
    for col in columns:
        if col in rows.columns:
            for v in rows[col].tolist():
                s = clean(v)
                if s:
                    return s
    return ""


def most_common_nonempty(values: list[Any]) -> str:
    cleaned = [clean(v) for v in values if clean(v)]
    if not cleaned:
        return ""
    counts = Counter(cleaned)
    max_count = max(counts.values())
    winners = sorted(v for v, c in counts.items() if c == max_count)
    return winners[0] if len(winners) == 1 else " | ".join(winners)


def build_trajectory(
    rut: str,
    codcli: str,
    da_rows: pd.DataFrame,
    h_rows: pd.DataFrame,
    bd_rows: pd.DataFrame,
    matrix_index: dict[tuple[str, str, str, str], list[dict[str, str]]],
) -> Trajectory:
    tr = Trajectory(rut=rut, codcli=codcli, da_rows=da_rows, h_rows=h_rows, bd_rows=bd_rows)
    tr.dv = select_first_nonempty(da_rows, ["_DV"]) or select_first_nonempty(h_rows, ["DIG"]) or select_first_nonempty(bd_rows, ["DV"])
    tr.nombre = (
        select_first_nonempty(da_rows, ["NOMBRE"])
        or " ".join(
            x
            for x in [
                select_first_nonempty(h_rows, ["NOMBRE"]),
                select_first_nonempty(h_rows, ["PATERNO"]),
                select_first_nonempty(h_rows, ["MATERNO"]),
            ]
            if x
        )
    )
    tr.codcarr = select_first_nonempty(da_rows, ["CODCARPR", "CODIGOCARRERA"]) or select_first_nonempty(h_rows, ["CODCARR"])
    tr.carrera = select_first_nonempty(da_rows, ["NOMBRE_L"]) or select_first_nonempty(h_rows, ["CARRERA"])
    tr.jornada_fuente = select_first_nonempty(da_rows, ["JORNADA"]) or select_first_nonempty(h_rows, ["JORNADA"])
    tr.sede_fuente = select_first_nonempty(da_rows, ["SEDE"])
    tr.cod_sed_fuente = SEDE_TO_MU.get(norm_text(tr.sede_fuente), "")
    if not tr.cod_sed_fuente and tr.sede_fuente:
        tr.cod_sed_fuente = norm_num(tr.sede_fuente)

    tr.anio_ingreso = select_first_nonempty(da_rows, ["ANOINGRESO"])
    tr.periodo_ingreso = select_first_nonempty(da_rows, ["PERIODOINGRESO"])

    da_active = pd.DataFrame()
    if not da_rows.empty:
        da_active = da_rows[
            (da_rows["ANOMATRICULA"].map(norm_num) == "2026")
            & (da_rows["PERIODOMATRICULA"].map(norm_num) == "1")
        ]
    h_active = pd.DataFrame()
    if not h_rows.empty:
        h_active = h_rows[(h_rows["ANO"].map(norm_num) == "2026") & (h_rows["PERIODO"].map(norm_num) == "1")]

    if not da_active.empty:
        tr.nivel_fuente = most_common_nonempty(da_active["NIVEL"].tolist())
    elif not h_active.empty:
        tr.nivel_fuente = most_common_nonempty(h_active["NIVEL"].tolist())
    else:
        tr.nivel_fuente = most_common_nonempty(da_rows["NIVEL"].tolist() if "NIVEL" in da_rows.columns else [])

    periods: list[tuple[int, int]] = []
    for _, row in da_rows.iterrows():
        for y_col, p_col in [("ANOINGRESO", "PERIODOINGRESO"), ("ANOMATRICULA", "PERIODOMATRICULA")]:
            p = period_tuple(row.get(y_col, ""), row.get(p_col, ""))
            if p:
                periods.append(p)
    for _, row in h_rows.iterrows():
        p = period_tuple(row.get("ANO", ""), row.get("PERIODO", ""))
        if p:
            periods.append(p)
    if periods:
        tr.primer_periodo = format_period(min(periods))
        tr.ultimo_periodo = format_period(max(periods))

    has_da_2026_1 = not da_active.empty
    has_h_2026_1 = not h_active.empty
    tr.actividad_2026_1 = "SI" if has_da_2026_1 or has_h_2026_1 else "NO"

    estados_da = {norm_text(v) for v in da_active.get("ESTADOACADEMICO", pd.Series(dtype=str)).tolist() if clean(v)}
    estados_h = {norm_text(v) for v in h_active.get("ESTADO_ACADEMICO", pd.Series(dtype=str)).tolist() if clean(v)}
    has_vigente = "VIGENTE" in estados_da or "VIGENTE" in estados_h
    if (has_da_2026_1 or has_h_2026_1) and has_vigente:
        tr.estado_vigencia = "VIGENTE_2026_1_CONFIRMADO"
    elif has_da_2026_1 or has_h_2026_1:
        tr.estado_vigencia = "VIGENCIA_AMBIGUA"
    elif periods:
        tr.estado_vigencia = "HISTORICO_NO_VIGENTE"
    else:
        tr.estado_vigencia = "SIN_EVIDENCIA_2026_1"

    if not da_active.empty:
        r = da_active.iloc[0]
        tr.source_file = "PROMEDIOSDEALUMNOS_7804.xlsx"
        tr.source_sheet = "DatosAlumnos"
        tr.source_row = clean(r.get("_EXCEL_ROW", ""))
    elif not h_active.empty:
        r = h_active.iloc[0]
        tr.source_file = "PROMEDIOSDEALUMNOS_7804.xlsx"
        tr.source_sheet = "Hoja1"
        tr.source_row = clean(r.get("_EXCEL_ROW", ""))
    elif not da_rows.empty:
        r = da_rows.iloc[0]
        tr.source_file = "PROMEDIOSDEALUMNOS_7804.xlsx"
        tr.source_sheet = "DatosAlumnos"
        tr.source_row = clean(r.get("_EXCEL_ROW", ""))
    elif not h_rows.empty:
        r = h_rows.iloc[0]
        tr.source_file = "PROMEDIOSDEALUMNOS_7804.xlsx"
        tr.source_sheet = "Hoja1"
        tr.source_row = clean(r.get("_EXCEL_ROW", ""))
    elif not bd_rows.empty:
        r = bd_rows.iloc[0]
        tr.source_file = "PROMEDIOSDEALUMNOS_7804.xlsx"
        tr.source_sheet = "base_datos"
        tr.source_row = clean(r.get("_EXCEL_ROW", ""))

    tr.offer_candidates, tr.offer_match_quality = candidate_offers_for_trajectory(tr, matrix_index)
    estados_all = join_unique(
        list(da_rows.get("ESTADOACADEMICO", pd.Series(dtype=str)).tolist())
        + list(h_rows.get("ESTADO_ACADEMICO", pd.Series(dtype=str)).tolist())
    )
    situaciones = join_unique(list(da_rows.get("SITUACION", pd.Series(dtype=str)).tolist()))
    tr.evidencia = (
        f"DatosAlumnos filas={join_unique(da_rows.get('_EXCEL_ROW', pd.Series(dtype=str)).tolist()) or 'NA'}; "
        f"Hoja1 filas={join_unique(h_rows.get('_EXCEL_ROW', pd.Series(dtype=str)).tolist()) or 'NA'}; "
        f"base_datos filas={join_unique(bd_rows.get('_EXCEL_ROW', pd.Series(dtype=str)).tolist()) or 'NA'}; "
        f"periodos={tr.primer_periodo}..{tr.ultimo_periodo}; "
        f"2026-1_DatosAlumnos={len(da_active)}; 2026-1_Hoja1={len(h_active)}; "
        f"estados={estados_all or 'NA'}; situaciones={situaciones or 'NA'}; "
        f"mapeo_matriz={tr.offer_match_quality}"
    )
    return tr


def mu_offer_key(row: pd.Series) -> tuple[str, str, str, str, str]:
    return (
        norm_num(row.get("COD_SED", "")),
        norm_num(row.get("COD_CAR", "")),
        norm_num(row.get("MODALIDAD", "")),
        norm_num(row.get("JOR", "")),
        norm_num(row.get("VERSION", "")),
    )


def mu_offer_key_wo_version(row: pd.Series) -> tuple[str, str, str, str]:
    return (
        norm_num(row.get("COD_SED", "")),
        norm_num(row.get("COD_CAR", "")),
        norm_num(row.get("MODALIDAD", "")),
        norm_num(row.get("JOR", "")),
    )


def is_mu_vigente(row: pd.Series) -> bool:
    return norm_num(row.get("VIG", "")) in {"1", "2"}


def classify_field_result(
    field_name: str,
    mu_value: str,
    correct_tr: Trajectory | None,
    this_tr: Trajectory,
    other_trajs: list[Trajectory],
) -> str:
    this_values = source_values_for_field(this_tr, field_name)
    if correct_tr is not None and this_tr.codcli == correct_tr.codcli:
        if not this_values:
            return "SIN_FUENTE_DIRECTA"
        if mu_value in this_values:
            return "COINCIDE_CODCLI_VIGENTE"
        for other in other_trajs:
            other_values = source_values_for_field(other, field_name)
            if mu_value and mu_value in other_values:
                if other.is_active_confirmed:
                    return "VALOR_DE_OTRO_CODCLI_VIGENTE"
                if other.is_historical:
                    return "VALOR_DE_TRAYECTORIA_HISTORICA"
        return "DIFERENCIA_SIN_EVIDENCIA_DE_MEZCLA"

    if not this_values:
        return "NO_APLICA"
    if mu_value in this_values:
        if this_tr.is_active_confirmed:
            return "VALOR_DE_OTRO_CODCLI_VIGENTE"
        if this_tr.is_historical:
            return "VALOR_DE_TRAYECTORIA_HISTORICA"
        return "REQUIERE_REVISION"
    return "NO_APLICA"


def detect_field_issue(result: str) -> bool:
    return result in {
        "VALOR_DE_TRAYECTORIA_HISTORICA",
        "VALOR_DE_OTRO_CODCLI_VIGENTE",
        "DIFERENCIA_SIN_EVIDENCIA_DE_MEZCLA",
        "SIN_FUENTE_DIRECTA",
        "REQUIERE_REVISION",
    }


def classify_match_for_trace(
    tr: Trajectory,
    mu_row: pd.Series,
    rut_active_count: int,
    rut_mu_count: int,
    rut_distinct_mu_offers: int,
) -> str:
    exact = mu_offer_key(mu_row) in offer_keys(tr)
    approx = mu_offer_key_wo_version(mu_row) in offer_keys_wo_version(tr)
    if exact and tr.is_active_confirmed:
        if rut_mu_count >= 2 and rut_distinct_mu_offers >= 2:
            return "DOS_FILAS_MU_DOS_OFERTAS_VIGENTES"
        if rut_active_count >= 2:
            return "DOS_CODCLI_VIGENTES_MISMA_PERSONA"
        return "MATCH_EXACTO_CODCLI_VIGENTE"
    if exact and tr.is_historical:
        return "MATCH_EXACTO_TRAYECTORIA_HISTORICA_NO_APLICA"
    if approx:
        return "MATCH_AMBIGUO"
    return "SIN_MATCH"


def source_value_display(tr: Trajectory, field_name: str) -> str:
    values = source_values_for_field(tr, field_name)
    return " | ".join(sorted(values, key=lambda x: (len(x), x)))


def build_outputs() -> dict[str, Any]:
    script_path = Path(__file__).resolve()
    output_dir = script_path.parent
    root = output_dir.parents[1]
    resultados_dir = root / "resultados"
    source_xlsx = root / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"
    mu_csv = resultados_dir / "matricula_unificada_rectificacion_20260618" / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_P1_20260618.csv"
    manual_pdf = root / "Manual_Matrícula_Unificada_2026.pdf"
    manual_txt = root / "manual_matrícula_unificada.txt"

    run_started = datetime.now().isoformat(timespec="seconds")

    historical_dirs: list[dict[str, Any]] = []
    for d in sorted(p for p in resultados_dir.iterdir() if p.is_dir() and p.resolve() != output_dir.resolve()):
        digest, file_count, total_bytes = sha256_directory(d)
        historical_dirs.append(
            {
                "tipo": "CARPETA_HISTORICA",
                "ruta": str(d.relative_to(root)),
                "estado_uso": "HISTORICO_NO_USAR_COMO_FUENTE_DE_DECISION",
                "sha256_directorio": digest,
                "archivos": file_count,
                "bytes": total_bytes,
            }
        )

    delimiter = sniff_csv_delimiter(mu_csv)
    mu = pd.read_csv(mu_csv, sep=delimiter, header=None, names=MU_COLUMNS, dtype=str, encoding="utf-8-sig")
    mu = mu.fillna("")
    mu["_MU_LINEA"] = [str(i) for i in range(1, len(mu) + 1)]
    mu["_RUT_NUM"] = mu["N_DOC"].map(lambda x: parse_rut(x)[0])
    mu["_DV"] = mu["DV"].map(lambda x: clean(x).upper())
    mu["_LLAVE_MU"] = mu.apply(
        lambda r: (
            f"MU_LINEA_{int(r['_MU_LINEA']):05d}|RUT={r['_RUT_NUM']}-{r['_DV']}|"
            f"S{norm_num(r['COD_SED'])}C{norm_num(r['COD_CAR'])}M{norm_num(r['MODALIDAD'])}"
            f"J{norm_num(r['JOR'])}V{norm_num(r['VERSION'])}"
        ),
        axis=1,
    )
    mu["_OFFER"] = mu.apply(mu_offer_key, axis=1)
    mu_ruts = set(mu["_RUT_NUM"])

    hoja1 = pd.read_excel(source_xlsx, sheet_name="Hoja1", dtype=str).fillna("")
    datos = pd.read_excel(source_xlsx, sheet_name="DatosAlumnos", dtype=str).fillna("")
    matriz = pd.read_excel(source_xlsx, sheet_name="matriz", dtype=str).fillna("")
    base_datos = pd.read_excel(source_xlsx, sheet_name="base_datos", dtype=str).fillna("")

    hoja1["_EXCEL_ROW"] = [str(i) for i in range(2, len(hoja1) + 2)]
    datos["_EXCEL_ROW"] = [str(i) for i in range(2, len(datos) + 2)]
    matriz["_EXCEL_ROW"] = [str(i) for i in range(2, len(matriz) + 2)]
    base_datos["_EXCEL_ROW"] = [str(i) for i in range(2, len(base_datos) + 2)]

    hoja1 = add_rut_columns_from_combined(hoja1, "RUT", "DIG")
    datos = add_rut_columns_from_combined(datos, "RUT")
    base_datos = add_rut_columns_from_combined(base_datos, "RUT", "DV")

    hoja1_mu = hoja1[hoja1["_RUT_NUM"].isin(mu_ruts)].copy()
    datos_mu = datos[datos["_RUT_NUM"].isin(mu_ruts)].copy()
    base_datos_mu = base_datos[base_datos["_RUT_NUM"].isin(mu_ruts)].copy()

    matrix_index = build_matrix_candidates(matriz)

    keys: set[tuple[str, str]] = set()
    for df in [datos_mu, hoja1_mu, base_datos_mu]:
        if df.empty:
            continue
        for _, row in df.iterrows():
            rut = clean(row.get("_RUT_NUM"))
            codcli = clean(row.get("CODCLI"))
            if rut and codcli:
                keys.add((rut, codcli))

    grouped_da = {k: g.copy() for k, g in datos_mu.groupby(["_RUT_NUM", "CODCLI"], dropna=False)}
    grouped_h = {k: g.copy() for k, g in hoja1_mu.groupby(["_RUT_NUM", "CODCLI"], dropna=False)}
    grouped_bd = {k: g.copy() for k, g in base_datos_mu.groupby(["_RUT_NUM", "CODCLI"], dropna=False)}

    trajectories_by_rut: dict[str, list[Trajectory]] = defaultdict(list)
    for rut, codcli in sorted(keys):
        da_rows = grouped_da.get((rut, codcli), pd.DataFrame())
        h_rows = grouped_h.get((rut, codcli), pd.DataFrame())
        bd_rows = grouped_bd.get((rut, codcli), pd.DataFrame())
        tr = build_trajectory(rut, codcli, da_rows, h_rows, bd_rows, matrix_index)
        trajectories_by_rut[rut].append(tr)

    mu_by_rut = {rut: g.copy() for rut, g in mu.groupby("_RUT_NUM", dropna=False)}

    # Update simultaneous/other-offer status only after MU matching can be checked.
    for rut, trajs in trajectories_by_rut.items():
        active = [tr for tr in trajs if tr.estado_vigencia == "VIGENTE_2026_1_CONFIRMADO"]
        if len(active) >= 2:
            for tr in active:
                tr.estado_vigencia = "VIGENTE_SIMULTANEO"

        rut_mu = mu_by_rut.get(rut, pd.DataFrame())
        for tr in trajs:
            if not tr.is_active_confirmed:
                continue
            exact_matches = 0
            for _, mu_row in rut_mu.iterrows():
                if mu_offer_key(mu_row) in offer_keys(tr):
                    exact_matches += 1
            tr.exact_active_mu_matches = exact_matches
            tr.matched_any_mu = exact_matches > 0
            if tr.estado_vigencia == "VIGENTE_2026_1_CONFIRMADO" and exact_matches == 0:
                tr.estado_vigencia = "VIGENTE_PARA_OTRA_OFERTA"

    rut_summaries: dict[str, dict[str, Any]] = {}
    trace_rows: list[dict[str, Any]] = []
    field_review_counter: Counter[str] = Counter()
    field_result_counter: Counter[str] = Counter()

    for rut in sorted(mu_ruts, key=lambda x: int(x) if x.isdigit() else x):
        rut_mu = mu_by_rut.get(rut, pd.DataFrame()).copy()
        trajs = trajectories_by_rut.get(rut, [])
        mu_count = len(rut_mu)
        distinct_mu_offers = len({mu_offer_key(row) for _, row in rut_mu.iterrows()})
        mu_vigente_rows = [row for _, row in rut_mu.iterrows() if is_mu_vigente(row)]
        mu_no_vigente_rows = [row for _, row in rut_mu.iterrows() if not is_mu_vigente(row)]
        mu_vigente_count = len(mu_vigente_rows)
        distinct_mu_vigente_offers = len({mu_offer_key(row) for row in mu_vigente_rows})
        mu_vig_set = join_unique([row.get("VIG", "") for _, row in rut_mu.iterrows()])
        active_trajs = [tr for tr in trajs if tr.is_active_confirmed]
        hist_trajs = [tr for tr in trajs if tr.is_historical]
        ambiguous_vig_trajs = [tr for tr in trajs if tr.estado_vigencia == "VIGENCIA_AMBIGUA"]
        exact_active_by_mu: dict[str, list[Trajectory]] = {}
        exact_historical_by_mu: dict[str, list[Trajectory]] = {}
        approx_by_mu: dict[str, list[Trajectory]] = {}
        correct_by_mu: dict[str, Trajectory | None] = {}
        field_issues_by_mu: dict[str, set[str]] = defaultdict(set)
        confirmed_mix_fields: set[str] = set()

        for _, mu_row in rut_mu.iterrows():
            llave = clean(mu_row["_LLAVE_MU"])
            row_requires_active = is_mu_vigente(mu_row)
            m_offer = mu_offer_key(mu_row)
            m_offer_wo = mu_offer_key_wo_version(mu_row)
            exact_active_by_mu[llave] = [tr for tr in active_trajs if m_offer in offer_keys(tr)]
            exact_historical_by_mu[llave] = [tr for tr in hist_trajs if m_offer in offer_keys(tr)]
            approx_by_mu[llave] = [tr for tr in trajs if m_offer_wo in offer_keys_wo_version(tr) and m_offer not in offer_keys(tr)]

            correct: Trajectory | None = None
            if row_requires_active and len(exact_active_by_mu[llave]) == 1:
                correct = exact_active_by_mu[llave][0]
            elif row_requires_active and len(active_trajs) == 1:
                # A single confirmed active trajectory is the only defensible CODCLI for critical-field diagnostics,
                # even when the offer fields do not all match. This does not make the match exact.
                correct = active_trajs[0]
            correct_by_mu[llave] = correct

            if row_requires_active and correct is not None:
                other_trajs = [tr for tr in trajs if tr.codcli != correct.codcli]
                for field_name in CRITICAL_FIELDS:
                    result = classify_field_result(field_name, norm_num(mu_row[field_name]), correct, correct, other_trajs)
                    field_result_counter[(field_name, result)] += 1
                    if detect_field_issue(result):
                        field_issues_by_mu[llave].add(field_name)
                        if field_name != "ANIO_ING_ORI" and result in {
                            "VALOR_DE_TRAYECTORIA_HISTORICA",
                            "VALOR_DE_OTRO_CODCLI_VIGENTE",
                        }:
                            if field_name in {"COD_CAR", "MODALIDAD", "JOR"}:
                                confirmed_mix_fields.add(field_name)
                for field_name in field_issues_by_mu[llave]:
                    field_review_counter[field_name] += 1

        vigente_llaves = {clean(row["_LLAVE_MU"]) for row in mu_vigente_rows}
        no_vigente_llaves = {clean(row["_LLAVE_MU"]) for row in mu_no_vigente_rows}
        row_level_exact_matches = sum(1 for llave in vigente_llaves if len(exact_active_by_mu.get(llave, [])) == 1)
        row_level_ambiguous_matches = sum(
            1
            for llave, matches in exact_active_by_mu.items()
            if llave in vigente_llaves
            if len(matches) != 1 and (len(matches) > 1 or approx_by_mu.get(llave) or ambiguous_vig_trajs)
        )
        row_level_no_match = sum(1 for llave in vigente_llaves if len(exact_active_by_mu.get(llave, [])) == 0)
        nonvigente_con_activo_exact = sum(1 for llave in no_vigente_llaves if len(exact_active_by_mu.get(llave, [])) >= 1)
        nonvigente_historico_exact = sum(1 for llave in no_vigente_llaves if len(exact_historical_by_mu.get(llave, [])) >= 1)
        all_field_issues = set().union(*field_issues_by_mu.values()) if field_issues_by_mu else set()

        if not trajs:
            rut_class = "SIN_EVIDENCIA_SUFICIENTE"
        elif confirmed_mix_fields:
            rut_class = "ERROR_MEZCLA_CONFIRMADA"
        elif nonvigente_con_activo_exact:
            rut_class = "REVISAR_VIGENCIA_CODCLI"
        elif row_level_no_match and not active_trajs and (ambiguous_vig_trajs or hist_trajs):
            rut_class = "REVISAR_VIGENCIA_CODCLI"
        elif row_level_no_match and ambiguous_vig_trajs:
            rut_class = "REVISAR_VIGENCIA_CODCLI"
        elif row_level_no_match and any(exact_historical_by_mu.get(llave) for llave in vigente_llaves):
            rut_class = "REVISAR_VIGENCIA_CODCLI"
        elif row_level_no_match and not active_trajs:
            rut_class = "SIN_EVIDENCIA_SUFICIENTE"
        elif any(len(v) > 1 for v in exact_active_by_mu.values()):
            rut_class = "REVISAR_MATCH_CODCLI"
        elif row_level_no_match and len(active_trajs) >= 2:
            rut_class = "REVISAR_MATCH_CODCLI"
        elif row_level_no_match and active_trajs:
            rut_class = "REVISAR_MATCH_CODCLI"
        elif row_level_ambiguous_matches:
            rut_class = "REVISAR_MATCH_CODCLI"
        elif all_field_issues:
            if len(all_field_issues) == 1:
                rut_class = "REVISAR_" + next(iter(all_field_issues))
            else:
                rut_class = "REVISAR_MULTIPLES_CAMPOS_CRITICOS"
        elif mu_vigente_count >= 2 and distinct_mu_vigente_offers >= 2 and row_level_exact_matches == mu_vigente_count:
            rut_class = "OK_DOS_FILAS_MU_DOS_CARRERAS_CORRECTAS"
        elif len(active_trajs) >= 2 and row_level_no_match == 0 and mu_vigente_count >= 1:
            rut_class = "OK_DOS_TRAYECTORIAS_VIGENTES_BIEN_INFORMADAS"
        elif len(trajs) >= 2 and len(active_trajs) == 1 and hist_trajs and mu_vigente_count == 1:
            rut_class = "OK_UNA_TRAYECTORIA_VIGENTE_OTRA_HISTORICA"
        else:
            rut_class = "OK_SIN_MEZCLA_DE_TRAYECTORIAS"

        rut_name_mu = ""
        rut_dv_mu = ""
        if not rut_mu.empty:
            first_mu = rut_mu.iloc[0]
            rut_dv_mu = clean(first_mu["DV"])
            rut_name_mu = " ".join(
                clean(first_mu[c])
                for c in ["NOMBRE", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO"]
                if clean(first_mu[c])
            )

        rut_summaries[rut] = {
            "RUT": rut,
            "DV": rut_dv_mu,
            "nombre_MU": rut_name_mu,
            "filas_MU": mu_count,
            "filas_MU_vigentes": mu_vigente_count,
            "VIG_MU": mu_vig_set,
            "ofertas_MU_distintas": distinct_mu_offers,
            "ofertas_MU_vigentes_distintas": distinct_mu_vigente_offers,
            "codcli_fuente": len(trajs),
            "codcli_vigentes_2026_1": len(active_trajs),
            "codcli_historicos": len(hist_trajs),
            "codcli_vigencia_ambigua": len(ambiguous_vig_trajs),
            "clasificacion_RUT": rut_class,
            "matches_exactos_fila_MU_vigente": row_level_exact_matches,
            "matches_ambiguos_fila_MU_vigente": row_level_ambiguous_matches,
            "filas_MU_vigentes_sin_match_activo": row_level_no_match,
            "filas_MU_no_vigentes_con_match_historico": nonvigente_historico_exact,
            "filas_MU_no_vigentes_con_match_activo": nonvigente_con_activo_exact,
            "campos_revision": join_unique(all_field_issues),
            "codcli_vigentes": join_unique([tr.codcli for tr in active_trajs]),
            "codcli_historicos_detalle": " || ".join(
                f"{tr.codcli}:{tr.codcarr}:{tr.carrera}:{tr.primer_periodo}-{tr.ultimo_periodo}" for tr in hist_trajs
            ),
            "codcli_vigentes_detalle": " || ".join(
                f"{tr.codcli}:{tr.codcarr}:{tr.carrera}:{tr.primer_periodo}-{tr.ultimo_periodo}" for tr in active_trajs
            ),
            "accion_recomendada": (
                "Sin accion sobre base; caso OK"
                if rut_class.startswith("OK_")
                else "Revisar solo campos criticos indicados; no aplicar correccion automatica"
            ),
        }

        trace_trajs = trajs if trajs else [Trajectory(rut=rut, codcli="SIN_CODCLI_FUENTE", estado_vigencia="SIN_EVIDENCIA_2026_1")]
        for _, mu_row in rut_mu.iterrows():
            llave = clean(mu_row["_LLAVE_MU"])
            correct = correct_by_mu.get(llave)
            for tr in trace_trajs:
                if tr.codcli == "SIN_CODCLI_FUENTE":
                    match_class = "SIN_MATCH"
                else:
                    match_class = classify_match_for_trace(tr, mu_row, len(active_trajs), mu_count, distinct_mu_offers)
                other_trajs = [x for x in trajs if x.codcli != tr.codcli]
                field_results: dict[str, str] = {}
                for field_name in CRITICAL_FIELDS:
                    field_results[field_name] = classify_field_result(
                        field_name, norm_num(mu_row[field_name]), correct, tr, other_trajs
                    )

                otros = [x.codcli for x in trajs if x.codcli != tr.codcli]
                ofertas = tr.offer_candidates
                trace_rows.append(
                    {
                        "RUT": rut,
                        "DV": tr.dv or clean(mu_row["DV"]),
                        "nombre": tr.nombre or rut_name_mu,
                        "CODCLI": tr.codcli,
                        "estado_de_vigencia": tr.estado_vigencia,
                        "primer_periodo": tr.primer_periodo,
                        "ultimo_periodo": tr.ultimo_periodo,
                        "actividad_2026_1": tr.actividad_2026_1,
                        "carrera": tr.carrera,
                        "CODCARR": tr.codcarr,
                        "COD_CAR": source_value_display(tr, "COD_CAR"),
                        "sede": tr.cod_sed_fuente,
                        "modalidad": source_value_display(tr, "MODALIDAD"),
                        "jornada": source_value_display(tr, "JOR"),
                        "version": join_unique([c["VERSION"] for c in ofertas]),
                        "LLAVE_MU": llave,
                        "VIG_MU": norm_num(mu_row["VIG"]),
                        "cantidad_filas_MU_RUT": mu_count,
                        "cantidad_filas_MU_vigentes_RUT": mu_vigente_count,
                        "cantidad_CODCLI_RUT": len(trajs),
                        "cantidad_CODCLI_vigentes_2026_1": len(active_trajs),
                        "clasificacion_RUT": rut_class,
                        "clasificacion_match": match_class,
                        "ANIO_ING_ORI_MU": norm_num(mu_row["ANIO_ING_ORI"]),
                        "ANIO_ING_ORI_fuente": source_value_display(tr, "ANIO_ING_ORI"),
                        "resultado_ANIO_ING_ORI": field_results["ANIO_ING_ORI"],
                        "NIV_ACA_MU": norm_num(mu_row["NIV_ACA"]),
                        "NIV_ACA_fuente": source_value_display(tr, "NIV_ACA"),
                        "resultado_NIV_ACA": field_results["NIV_ACA"],
                        "COD_CAR_MU": norm_num(mu_row["COD_CAR"]),
                        "COD_CAR_fuente": source_value_display(tr, "COD_CAR"),
                        "resultado_COD_CAR": field_results["COD_CAR"],
                        "MODALIDAD_MU": norm_num(mu_row["MODALIDAD"]),
                        "MODALIDAD_fuente": source_value_display(tr, "MODALIDAD"),
                        "resultado_MODALIDAD": field_results["MODALIDAD"],
                        "JOR_MU": norm_num(mu_row["JOR"]),
                        "JOR_fuente": source_value_display(tr, "JOR"),
                        "resultado_JOR": field_results["JOR"],
                        "otros_CODCLI_del_RUT": join_unique(otros),
                        "detalle_trayectorias_historicas": rut_summaries[rut]["codcli_historicos_detalle"],
                        "detalle_trayectorias_vigentes": rut_summaries[rut]["codcli_vigentes_detalle"],
                        "evidencia": tr.evidencia,
                        "archivo": tr.source_file,
                        "hoja": tr.source_sheet,
                        "fila": tr.source_row,
                        "observacion": (
                            f"{tr.identity_status}; {tr.offer_match_quality}; "
                            f"revision_campos={join_unique(field_issues_by_mu.get(llave, set())) or 'NA'}"
                        ),
                        "accion_recomendada": rut_summaries[rut]["accion_recomendada"],
                    }
                )

    trace_df = pd.DataFrame(trace_rows)
    summary_df = pd.DataFrame(rut_summaries.values()).sort_values(["clasificacion_RUT", "RUT"])

    traj_rows: list[dict[str, Any]] = []
    for rut, trajs in trajectories_by_rut.items():
        for tr in trajs:
            traj_rows.append(
                {
                    "RUT": rut,
                    "DV": tr.dv,
                    "nombre": tr.nombre,
                    "CODCLI": tr.codcli,
                    "estado_de_vigencia": tr.estado_vigencia,
                    "primer_periodo": tr.primer_periodo,
                    "ultimo_periodo": tr.ultimo_periodo,
                    "actividad_2026_1": tr.actividad_2026_1,
                    "CODCARR": tr.codcarr,
                    "carrera": tr.carrera,
                    "sede": tr.cod_sed_fuente,
                    "modalidad": source_value_display(tr, "MODALIDAD"),
                    "jornada": source_value_display(tr, "JOR"),
                    "version": join_unique([c["VERSION"] for c in tr.offer_candidates]),
                    "ANIO_ING_ORI_fuente": source_value_display(tr, "ANIO_ING_ORI"),
                    "NIV_ACA_fuente": source_value_display(tr, "NIV_ACA"),
                    "mapeo_matriz": tr.offer_match_quality,
                    "evidencia": tr.evidencia,
                    "archivo": tr.source_file,
                    "hoja": tr.source_sheet,
                    "fila": tr.source_row,
                }
            )
    trajectories_df = pd.DataFrame(traj_rows)

    controls = {
        "total_RUT_analizados": int(mu["_RUT_NUM"].nunique()),
        "RUT_con_multiples_CODCLI_fuente": int(sum(1 for s in rut_summaries.values() if s["codcli_fuente"] >= 2)),
        "CODCLI_totales_fuente_asociados_a_RUT_MU": int(len(trajectories_df)),
        "CODCLI_vigentes_2026_1": int(sum(1 for _, row in trajectories_df.iterrows() if row["estado_de_vigencia"] in ACTIVE_STATUSES)),
        "CODCLI_historicos": int(sum(1 for _, row in trajectories_df.iterrows() if row["estado_de_vigencia"] == "HISTORICO_NO_VIGENTE")),
        "RUT_con_una_fila_MU": int(sum(1 for s in rut_summaries.values() if s["filas_MU"] == 1)),
        "RUT_con_dos_o_mas_filas_MU": int(sum(1 for s in rut_summaries.values() if s["filas_MU"] >= 2)),
        "RUT_con_dos_o_mas_CODCLI_vigentes_2026_1": int(sum(1 for s in rut_summaries.values() if s["codcli_vigentes_2026_1"] >= 2)),
        "RUT_con_dos_carreras_MU_vigentes": int(
            sum(
                1
                for s in rut_summaries.values()
                if s["filas_MU_vigentes"] >= 2
                and s["ofertas_MU_vigentes_distintas"] >= 2
                and s["matches_exactos_fila_MU_vigente"] == s["filas_MU_vigentes"]
            )
        ),
        "RUT_con_una_MU_y_otra_trayectoria_historica": int(
            sum(
                1
                for s in rut_summaries.values()
                if s["filas_MU_vigentes"] == 1 and s["codcli_vigentes_2026_1"] == 1 and s["codcli_historicos"] >= 1
            )
        ),
        "matches_exactos": int(sum(s["matches_exactos_fila_MU_vigente"] for s in rut_summaries.values())),
        "matches_ambiguos": int(sum(s["matches_ambiguos_fila_MU_vigente"] for s in rut_summaries.values())),
        "casos_realmente_enviados_a_revision": int(
            sum(
                1
                for s in rut_summaries.values()
                if s["clasificacion_RUT"].startswith("REVISAR_")
                or s["clasificacion_RUT"].startswith("ERROR_")
                or s["clasificacion_RUT"].startswith("SIN_")
            )
        ),
        "revisiones_ANIO_ING_ORI": int(field_review_counter["ANIO_ING_ORI"]),
        "revisiones_NIV_ACA": int(field_review_counter["NIV_ACA"]),
        "revisiones_COD_CAR": int(field_review_counter["COD_CAR"]),
        "revisiones_MODALIDAD": int(field_review_counter["MODALIDAD"]),
        "revisiones_JOR": int(field_review_counter["JOR"]),
        "errores_mezcla_confirmada": int(sum(1 for s in rut_summaries.values() if s["clasificacion_RUT"] == "ERROR_MEZCLA_CONFIRMADA")),
        "casos_OK": int(sum(1 for s in rut_summaries.values() if s["clasificacion_RUT"].startswith("OK_"))),
        "casos_sin_evidencia": int(sum(1 for s in rut_summaries.values() if s["clasificacion_RUT"] == "SIN_EVIDENCIA_SUFICIENTE")),
        "duplicados_RUT_CODCLI_LLAVE_MU": int(trace_df.duplicated(["RUT", "CODCLI", "LLAVE_MU"]).sum()),
        "cambios_automaticos_sin_evidencia": 0,
        "revisiones_por_diferencias_personales_menores": 0,
    }

    class_dist = summary_df["clasificacion_RUT"].value_counts().rename_axis("clasificacion").reset_index(name="cantidad")
    field_dist_rows: list[dict[str, Any]] = []
    for (field_name, result), count in sorted(field_result_counter.items()):
        field_dist_rows.append({"campo": field_name, "resultado": result, "cantidad": count})
    field_dist = pd.DataFrame(field_dist_rows)
    controls_df = pd.DataFrame([{"control": k, "valor": v} for k, v in controls.items()])

    revision_df = summary_df[
        summary_df["clasificacion_RUT"].str.startswith("REVISAR_")
        | summary_df["clasificacion_RUT"].str.startswith("ERROR_")
        | summary_df["clasificacion_RUT"].str.startswith("SIN_")
    ].copy()
    ok_df = summary_df[summary_df["clasificacion_RUT"].str.startswith("OK_")].copy()
    vigentes_df = trajectories_df[trajectories_df["estado_de_vigencia"].isin(ACTIVE_STATUSES)].copy()
    historicos_df = trajectories_df[trajectories_df["estado_de_vigencia"] == "HISTORICO_NO_VIGENTE"].copy()
    dos_carreras_df = summary_df[
        (summary_df["filas_MU_vigentes"] >= 2)
        & (summary_df["ofertas_MU_vigentes_distintas"] >= 2)
        & (summary_df["matches_exactos_fila_MU_vigente"] == summary_df["filas_MU_vigentes"])
    ].copy()
    una_historica_df = summary_df[
        (summary_df["filas_MU_vigentes"] == 1) & (summary_df["codcli_vigentes_2026_1"] == 1) & (summary_df["codcli_historicos"] >= 1)
    ].copy()
    mezcla_df = summary_df[summary_df["clasificacion_RUT"] == "ERROR_MEZCLA_CONFIRMADA"].copy()

    artifacts: dict[str, pd.DataFrame] = {
        "TRAZABILIDAD_RUT_CODCLI.xlsx": trace_df,
        "CASOS_REVISION_CRITICA.xlsx": revision_df,
        "CASOS_OK.xlsx": ok_df,
        "CODCLI_VIGENTES_2026_1.xlsx": vigentes_df,
        "CODCLI_HISTORICOS.xlsx": historicos_df,
        "RUT_DOS_CARRERAS_MU.xlsx": dos_carreras_df,
        "RUT_UNA_MU_OTRA_HISTORICA.xlsx": una_historica_df,
        "ERRORES_MEZCLA_CONFIRMADA.xlsx": mezcla_df,
    }
    for filename, df in artifacts.items():
        sheet = "TRAZABILIDAD_RUT_CODCLI" if filename == "TRAZABILIDAD_RUT_CODCLI.xlsx" else Path(filename).stem[:31]
        with pd.ExcelWriter(output_dir / filename, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet)
            ws = writer.book[sheet]
            ws.freeze_panes = "A2"
            for column_cells in ws.columns:
                max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells[:200])
                ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 10), 60)

    resumen_path = output_dir / "RESUMEN_EJECUTIVO.xlsx"
    with pd.ExcelWriter(resumen_path, engine="openpyxl") as writer:
        controls_df.to_excel(writer, index=False, sheet_name="CONTROLES")
        class_dist.to_excel(writer, index=False, sheet_name="CLASIFICACION_RUT")
        field_dist.to_excel(writer, index=False, sheet_name="RESULTADOS_CAMPOS")
        summary_df.to_excel(writer, index=False, sheet_name="RESUMEN_RUT")
        hist_df = pd.DataFrame(historical_dirs)
        hist_df.to_excel(writer, index=False, sheet_name="HISTORICOS")
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            for column_cells in ws.columns:
                max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells[:200])
                ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 10), 70)

    report_lines = [
        "# Reporte tecnico - auditoria multicodcli reconstruida 2026",
        "",
        f"Fecha de ejecucion: {run_started}",
        "",
        "## Fuentes usadas",
        "",
        f"- Fuente institucional principal: `{source_xlsx.relative_to(root)}`.",
        f"- Base MU limpia: `{mu_csv.relative_to(root)}`.",
        f"- Manual normativo: `{manual_pdf.relative_to(root)}`; usado para nombres/definiciones de columnas MU.",
        "- Resultados historicos: registrados y hasheados solo como evidencia; no se usaron como fuente de decision.",
        "",
        "## Metodo corregido",
        "",
        "1. Se reconstruyo el universo desde todos los RUT presentes en MU.",
        "2. Para cada RUT se buscaron todos los CODCLI en Hoja1, DatosAlumnos y base_datos.",
        "3. La vigencia 2026-1 se determino antes del match, usando periodo 2026-1 y estado academico compatible.",
        "4. La fila MU se asocio por oferta: sede, carrera, modalidad, jornada y version candidata desde matriz.",
        "5. Solo despues se revisaron los cinco campos criticos: ANIO_ING_ORI, NIV_ACA, COD_CAR, MODALIDAD y JOR.",
        "6. Las diferencias personales no generaron revision academica; solo se usaron para confirmar identidad por RUT/DV.",
        "7. No se genero base corregida ni se aplico ningun cambio automatico.",
        "",
        "## Controles principales",
        "",
    ]
    for key, value in controls.items():
        report_lines.append(f"- {key}: {value}")
    report_lines.extend(
        [
            "",
            "## Distribucion de clasificacion por RUT",
            "",
            df_to_markdown(class_dist),
            "",
            "## Distribucion por campo critico",
            "",
            df_to_markdown(field_dist) if not field_dist.empty else "Sin diferencias de campos criticos.",
            "",
            "## Tratamiento de historicos",
            "",
            "Las carpetas anteriores bajo `resultados/` fueron registradas con `estado_uso=HISTORICO_NO_USAR_COMO_FUENTE_DE_DECISION` en `MANIFEST_ARCHIVOS.csv` y `RESUMEN_EJECUTIVO.xlsx`. Sus hashes se calcularon como hash de directorio a partir de hashes SHA256 de sus archivos y rutas relativas. No se escribio ningun marcador dentro de esas carpetas para preservar los artefactos historicos intactos.",
            "",
            "## Decision de cambio",
            "",
            "Esta fase es diagnostica. No se modifica ninguna base y no se propone correccion automatica cuando ANIO_ING_ORI depende de definicion institucional no resoluble solo desde las fuentes.",
        ]
    )
    (output_dir / "REPORTE_TECNICO.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    command = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            'cd "$(dirname "$0")/../.."',
            "python3 resultados/auditoria_multicodcli_reconstruida_2026/auditoria_multicodcli_reconstruida.py",
            "",
        ]
    )
    command_path = output_dir / "COMANDO_REPRODUCIBLE.sh"
    command_path.write_text(command, encoding="utf-8")
    command_path.chmod(0o755)

    manifest_rows: list[dict[str, Any]] = []
    for p in [source_xlsx, mu_csv, manual_pdf, manual_txt]:
        if p.exists():
            manifest_rows.append(
                {
                    "tipo": "FUENTE",
                    "ruta": str(p.relative_to(root)),
                    "estado_uso": "FUENTE_DIRECTA_USADA",
                    "sha256": sha256_file(p),
                    "bytes": p.stat().st_size,
                }
            )
    for row in historical_dirs:
        manifest_rows.append(row)

    output_files = [
        "TRAZABILIDAD_RUT_CODCLI.xlsx",
        "RESUMEN_EJECUTIVO.xlsx",
        "CASOS_REVISION_CRITICA.xlsx",
        "CASOS_OK.xlsx",
        "CODCLI_VIGENTES_2026_1.xlsx",
        "CODCLI_HISTORICOS.xlsx",
        "RUT_DOS_CARRERAS_MU.xlsx",
        "RUT_UNA_MU_OTRA_HISTORICA.xlsx",
        "ERRORES_MEZCLA_CONFIRMADA.xlsx",
        "REPORTE_TECNICO.md",
        "COMANDO_REPRODUCIBLE.sh",
        "auditoria_multicodcli_reconstruida.py",
    ]
    for name in output_files:
        p = output_dir / name
        if p.exists():
            manifest_rows.append(
                {
                    "tipo": "ARTEFACTO_NUEVO",
                    "ruta": str(p.relative_to(root)),
                    "estado_uso": "SALIDA_DIAGNOSTICO_RECONSTRUIDO",
                    "sha256": sha256_file(p),
                    "bytes": p.stat().st_size,
                }
            )

    manifest_df = pd.DataFrame(manifest_rows)
    manifest_path = output_dir / "MANIFEST_ARCHIVOS.csv"
    manifest_df.to_csv(manifest_path, index=False, encoding="utf-8-sig")

    hash_lines = [
        "# SHA256 - auditoria multicodcli reconstruida 2026",
        "# HISTORICOS marcados como HISTORICO_NO_USAR_COMO_FUENTE_DE_DECISION solo en este registro.",
        "",
    ]
    for row in manifest_rows:
        if row.get("tipo") == "CARPETA_HISTORICA":
            hash_lines.append(
                f"{row['sha256_directorio']}  {row['ruta']}/  [{row['estado_uso']}; archivos={row['archivos']}; bytes={row['bytes']}]"
            )
        elif row.get("sha256"):
            hash_lines.append(f"{row['sha256']}  {row['ruta']}  [{row['estado_uso']}]")
    hash_lines.append(f"{sha256_file(manifest_path)}  {manifest_path.relative_to(root)}  [SALIDA_DIAGNOSTICO_RECONSTRUIDO]")
    hashes_path = output_dir / "HASHES_SHA256.txt"
    hashes_path.write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    terminal = {
        "total de RUT analizados": controls["total_RUT_analizados"],
        "RUT con múltiples CODCLI": controls["RUT_con_multiples_CODCLI_fuente"],
        "CODCLI totales": controls["CODCLI_totales_fuente_asociados_a_RUT_MU"],
        "CODCLI vigentes 2026-1": controls["CODCLI_vigentes_2026_1"],
        "CODCLI históricos": controls["CODCLI_historicos"],
        "RUT con una fila MU": controls["RUT_con_una_fila_MU"],
        "RUT con dos o más filas MU": controls["RUT_con_dos_o_mas_filas_MU"],
        "RUT con dos carreras MU vigentes": controls["RUT_con_dos_carreras_MU_vigentes"],
        "RUT con una MU y otra trayectoria histórica": controls["RUT_con_una_MU_y_otra_trayectoria_historica"],
        "matches exactos": controls["matches_exactos"],
        "matches ambiguos": controls["matches_ambiguos"],
        "revisiones ANIO_ING_ORI": controls["revisiones_ANIO_ING_ORI"],
        "revisiones NIV_ACA": controls["revisiones_NIV_ACA"],
        "revisiones COD_CAR": controls["revisiones_COD_CAR"],
        "revisiones MODALIDAD": controls["revisiones_MODALIDAD"],
        "revisiones JOR": controls["revisiones_JOR"],
        "mezclas confirmadas": controls["errores_mezcla_confirmada"],
        "casos OK": controls["casos_OK"],
        "casos sin evidencia": controls["casos_sin_evidencia"],
        "ruta de los artefactos": str(output_dir),
        "hashes": str(hashes_path),
    }

    print("RESULTADO AUDITORIA MULTICODCLI RECONSTRUIDA 2026")
    for key, value in terminal.items():
        print(f"{key}: {value}")
    print("controles cero:")
    print(f"duplicados RUT+CODCLI+LLAVE_MU: {controls['duplicados_RUT_CODCLI_LLAVE_MU']}")
    print(f"cambios automaticos sin evidencia: {controls['cambios_automaticos_sin_evidencia']}")
    print(f"revisiones por diferencias personales menores: {controls['revisiones_por_diferencias_personales_menores']}")

    return {
        "controls": controls,
        "terminal": terminal,
        "output_dir": output_dir,
        "manifest": manifest_path,
        "hashes": hashes_path,
    }


if __name__ == "__main__":
    build_outputs()
