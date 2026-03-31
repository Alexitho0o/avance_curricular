from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

import codigo as base


RESULT_DIAG_FILENAME = "niv_aca_fase2_diagnostico.csv"
RESULT_SUMMARY_FILENAME = "niv_aca_fase2_resumen.csv"
RESULT_META_FILENAME = "niv_aca_fase2_metadata.json"


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def _normalize_codcli(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _as_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text in {"1", "true", "t", "si", "sí", "y", "yes"}


def _valid_semester(value: object) -> bool:
    v = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return pd.notna(v) and int(v) in {1, 2}


def _normalize_semester(value: object, policy: str) -> tuple[float, str]:
    v = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(v):
        return float("nan"), "missing"
    i = int(v)
    if i in {1, 2}:
        return float(i), "exact"
    if i == 3 and policy == "map_3_to_2":
        return 2.0, "mapped_3_to_2"
    return float("nan"), f"invalid_{i}"


def _semester_index(year: object, sem: object) -> float:
    y = pd.to_numeric(pd.Series([year]), errors="coerce").iloc[0]
    s = pd.to_numeric(pd.Series([sem]), errors="coerce").iloc[0]
    if pd.isna(y) or pd.isna(s) or int(s) not in {1, 2}:
        return float("nan")
    return float(int(y) * 2 + (int(s) - 1))


def _infer_year_from_codcli(codcli: object) -> float:
    if pd.isna(codcli):
        return float("nan")
    text = re.sub(r"\D", "", str(codcli))
    if len(text) >= 4:
        year = int(text[:4])
        if 1900 <= year <= 2100:
            return float(year)
    return float("nan")


def _pick_first_column(df: pd.DataFrame, options: list[str]) -> str | None:
    upper_map = {c.upper(): c for c in df.columns}
    for opt in options:
        if opt.upper() in upper_map:
            return upper_map[opt.upper()]
    return None


def _load_source_views(input_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    book = pd.read_excel(input_path, sheet_name=None)
    hoja1 = book.get("Hoja1")
    datos_alumnos = book.get("DatosAlumnos")
    if hoja1 is None:
        raise ValueError("No existe hoja 'Hoja1' en el archivo de entrada.")
    if datos_alumnos is None:
        raise ValueError("No existe hoja 'DatosAlumnos' en el archivo de entrada.")
    return hoja1.copy(), datos_alumnos.copy()


def _build_hoja1_profile(hoja1: pd.DataFrame) -> pd.DataFrame:
    required = ["CODCLI", "CODCARR"]
    missing = [c for c in required if c not in hoja1.columns]
    if missing:
        raise ValueError(f"Hoja1 no contiene columnas obligatorias para Fase 2: {missing}")

    work = hoja1.copy()
    work["CODCLI_N"] = work["CODCLI"].map(_normalize_codcli)
    work["CODCARR_N"] = work["CODCARR"].map(_normalize_text)

    if "NIVEL" in work.columns:
        work["NIVEL_NUM"] = _to_num(work["NIVEL"])
    else:
        work["NIVEL_NUM"] = pd.NA
    work["ANO_NUM"] = _to_num(work["ANO"]) if "ANO" in work.columns else pd.NA
    work["PERIODO_NUM"] = _to_num(work["PERIODO"]) if "PERIODO" in work.columns else pd.NA

    # Último nivel observado en Hoja1 por CODCLI/CODCARR.
    latest = (
        work.sort_values(["CODCLI_N", "CODCARR_N", "ANO_NUM", "PERIODO_NUM"], na_position="last")
        .groupby(["CODCLI_N", "CODCARR_N"], as_index=False)
        .tail(1)[["CODCLI_N", "CODCARR_N", "NIVEL_NUM", "ANO_NUM", "PERIODO_NUM"]]
        .rename(
            columns={
                "NIVEL_NUM": "NIVEL_HOJA1_LAST",
                "ANO_NUM": "ANO_HOJA1_LAST",
                "PERIODO_NUM": "PERIODO_HOJA1_LAST",
            }
        )
    )

    agg = (
        work.groupby("CODCLI_N", as_index=False)
        .agg(
            CODCARR_H_COUNT=("CODCARR_N", "nunique"),
            CODCARR_H_MAIN=("CODCARR_N", lambda s: s.dropna().iloc[0] if s.dropna().size else ""),
            NIVEL_HOJA1_MIN=("NIVEL_NUM", "min"),
            NIVEL_HOJA1_MAX=("NIVEL_NUM", "max"),
            NIVEL_HOJA1_NUNIQUE=("NIVEL_NUM", lambda s: int(pd.Series(s).dropna().nunique())),
            ANO_HOJA1_MAX=("ANO_NUM", "max"),
            PERIODO_HOJA1_MAX=("PERIODO_NUM", "max"),
        )
        .merge(
            latest[["CODCLI_N", "CODCARR_N", "NIVEL_HOJA1_LAST", "ANO_HOJA1_LAST", "PERIODO_HOJA1_LAST"]],
            left_on=["CODCLI_N", "CODCARR_H_MAIN"],
            right_on=["CODCLI_N", "CODCARR_N"],
            how="left",
        )
        .drop(columns=["CODCARR_N"])
    )

    return agg


def _build_datos_alumnos_profile(datos: pd.DataFrame) -> pd.DataFrame:
    required = ["CODCLI", "CODCARPR", "ANOINGRESO", "PERIODOINGRESO", "NIVEL"]
    missing = [c for c in required if c not in datos.columns]
    if missing:
        raise ValueError(f"DatosAlumnos no contiene columnas obligatorias para Fase 2: {missing}")

    work = datos.copy()
    work["CODCLI_N"] = work["CODCLI"].map(_normalize_codcli)
    work["CODCARPR_N"] = work["CODCARPR"].map(_normalize_text)
    work["ANOINGRESO_NUM"] = _to_num(work["ANOINGRESO"])
    work["PERIODOINGRESO_NUM"] = _to_num(work["PERIODOINGRESO"])
    work["NIVEL_DA_NUM"] = _to_num(work["NIVEL"])
    work["ANOMATRICULA_NUM"] = _to_num(work["ANOMATRICULA"]) if "ANOMATRICULA" in work.columns else pd.NA
    work["PERIODOMATRICULA_NUM"] = _to_num(work["PERIODOMATRICULA"]) if "PERIODOMATRICULA" in work.columns else pd.NA

    latest = (
        work.sort_values(["CODCLI_N", "ANOMATRICULA_NUM", "PERIODOMATRICULA_NUM"], na_position="last")
        .groupby("CODCLI_N", as_index=False)
        .tail(1)
    )

    agg = (
        work.groupby("CODCLI_N", as_index=False)
        .agg(
            CODCARPR_DA_COUNT=("CODCARPR_N", "nunique"),
            CODCARPR_DA_MAIN=("CODCARPR_N", lambda s: s.dropna().iloc[0] if s.dropna().size else ""),
            NIVEL_DA_MIN=("NIVEL_DA_NUM", "min"),
            NIVEL_DA_MAX=("NIVEL_DA_NUM", "max"),
            NIVEL_DA_NUNIQUE=("NIVEL_DA_NUM", lambda s: int(pd.Series(s).dropna().nunique())),
        )
        .merge(
            latest[
                [
                    "CODCLI_N",
                    "CODCARPR_N",
                    "ANOINGRESO_NUM",
                    "PERIODOINGRESO_NUM",
                    "ANOMATRICULA_NUM",
                    "PERIODOMATRICULA_NUM",
                    "NIVEL_DA_NUM",
                ]
            ],
            on="CODCLI_N",
            how="left",
            suffixes=("", "_LAST"),
        )
    )

    # Carrera principal de la última fila de datos alumnos.
    agg["CODCARPR_DA_LAST"] = agg["CODCARPR_N"]
    agg = agg.drop(columns=["CODCARPR_N"])

    return agg


def _aggregate_duration_rows(rows: pd.DataFrame) -> pd.DataFrame:
    rows = rows.copy()
    rows["CODCARR_N"] = rows["CODCARR_N"].map(_normalize_text)
    rows["DURACION_SEMESTRES"] = _to_num(rows["DURACION_SEMESTRES"])
    if "SOURCE_PRIORITY" not in rows.columns:
        rows["SOURCE_PRIORITY"] = 999
    rows = rows[rows["CODCARR_N"] != ""].copy()
    rows = rows[rows["DURACION_SEMESTRES"].notna()].copy()
    rows = rows[rows["DURACION_SEMESTRES"] > 0].copy()
    if rows.empty:
        return pd.DataFrame(columns=["CODCARR_N", "DURACION_SEMESTRES", "DURACION_AMBIGUA", "DURACION_FUENTES"])

    # Mantener solo la(s) fuente(s) de mayor prioridad (menor número) por código.
    min_pri = rows.groupby("CODCARR_N")["SOURCE_PRIORITY"].transform("min")
    rows = rows[rows["SOURCE_PRIORITY"] == min_pri].copy()

    ag = (
        rows.groupby("CODCARR_N", as_index=False)
        .agg(
            DURACION_SEMESTRES_MIN=("DURACION_SEMESTRES", "min"),
            DURACION_SEMESTRES_MAX=("DURACION_SEMESTRES", "max"),
            N_DISTINCT_DUR=("DURACION_SEMESTRES", "nunique"),
            DURACION_FUENTES=("SOURCE", lambda s: " | ".join(sorted(set(map(str, s))))),
            DURACION_SOURCE_PRIORITY=("SOURCE_PRIORITY", "min"),
        )
    )
    ag["DURACION_SEMESTRES"] = ag["DURACION_SEMESTRES_MAX"]
    ag["DURACION_AMBIGUA"] = ag["N_DISTINCT_DUR"] > 1
    return ag[["CODCARR_N", "DURACION_SEMESTRES", "DURACION_AMBIGUA", "DURACION_FUENTES", "DURACION_SOURCE_PRIORITY"]].copy()


def _load_duration_table(path: Path | None, reference_codes: set[str] | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    if path is None:
        return pd.DataFrame(columns=["CODCARR_N", "DURACION_SEMESTRES", "DURACION_AMBIGUA"]), {
            "duration_source": None,
            "duration_rows": 0,
            "duration_mapped_programs": 0,
        }

    if not path.exists():
        raise FileNotFoundError(f"No existe archivo de oferta/duración: {path}")

    suffix = path.suffix.lower()
    code_options = ["CODCARPR", "CODCARR", "CODIGO_UNICO", "COD_CAR", "CODIGOCARRERA", "CODIGO_SIES"]
    dur_options = ["DURACION_TOTAL", "DURACION_ESTUDIOS", "DURACION_SEMESTRES", "SEMESTRES", "DURACION_ESTUDIOS_REF"]

    selected_sheet = None
    selected_code_col = None
    selected_dur_col = None
    raw = None
    xls = None

    if suffix in {".csv"}:
        raw = pd.read_csv(path)
        selected_code_col = _pick_first_column(raw, code_options)
        selected_dur_col = _pick_first_column(raw, dur_options)
        selected_sheet = "__csv__"
    elif suffix in {".tsv"}:
        raw = pd.read_csv(path, sep="\t")
        selected_code_col = _pick_first_column(raw, code_options)
        selected_dur_col = _pick_first_column(raw, dur_options)
        selected_sheet = "__tsv__"
    elif suffix in {".xlsx", ".xls"}:
        xls = pd.ExcelFile(path)
        best_score = -1
        for sh in xls.sheet_names:
            candidate = pd.read_excel(path, sheet_name=sh)
            code_col = _pick_first_column(candidate, code_options)
            dur_col = _pick_first_column(candidate, dur_options)
            if code_col is None or dur_col is None:
                continue
            usable = candidate[[code_col, dur_col]].dropna(how="any").copy()
            score_rows = int(usable.shape[0])
            overlap = 0
            if reference_codes:
                cand_codes = set(usable[code_col].map(_normalize_text))
                overlap = len(cand_codes & reference_codes)
            # Priorizamos cobertura sobre códigos de referencia.
            score = overlap * 100000 + score_rows
            if score > best_score:
                best_score = score
                raw = candidate
                selected_sheet = sh
                selected_code_col = code_col
                selected_dur_col = dur_col
    else:
        raise ValueError(f"Formato no soportado para oferta/duración: {path.suffix}")

    if raw is None or selected_code_col is None or selected_dur_col is None:
        raise ValueError(
            "No se encontraron columnas de código de carrera y duración en archivo de oferta. "
            "Esperadas: código en {CODCARPR,CODCARR,CODIGO_UNICO,COD_CAR,CODIGOCARRERA} y duración en "
            "{DURACION_TOTAL,DURACION_ESTUDIOS,DURACION_SEMESTRES,SEMESTRES}."
        )

    base_df = raw[[selected_code_col, selected_dur_col]].copy()
    base_df = base_df.rename(columns={selected_code_col: "CODCARR_N", selected_dur_col: "DURACION_SEMESTRES"})
    base_df["SOURCE"] = f"primary:{selected_sheet}:{selected_code_col}:{selected_dur_col}"
    base_df["SOURCE_PRIORITY"] = 1

    extra_frames: list[pd.DataFrame] = []

    # Enriquecimiento Fase 2.2 para workbooks multi-hoja:
    # 1) CODCARPR + DURACION_ESTUDIOS_REF desde 'CUADRO HOMOLOGACIÓN'
    # 2) CODCARPR + CODIGO_SIES + DURACION_TOTAL desde hoja 5320
    # 3) CODCARPR + CODIGO_CARRERA_SIES desde puente_sies.tsv del repo + DURACION_TOTAL(5320)
    if xls is not None:
        oa_candidates = []
        for sh in xls.sheet_names:
            candidate = pd.read_excel(path, sheet_name=sh)
            col_sies = _pick_first_column(candidate, ["CODIGO_UNICO"])
            col_dur_total = _pick_first_column(candidate, ["DURACION_TOTAL"])
            if col_sies and col_dur_total:
                usable = candidate[[col_sies, col_dur_total]].dropna(how="any")
                if not usable.empty:
                    oa_candidates.append((sh, col_sies, col_dur_total, usable))

        oa_map = None
        if oa_candidates:
            sh, col_sies, col_dur_total, usable = max(oa_candidates, key=lambda x: len(x[3]))
            oa_map = usable.copy()
            oa_map["CODIGO_SIES_N"] = oa_map[col_sies].map(_normalize_text)
            oa_map["DURACION_TOTAL_NUM"] = _to_num(oa_map[col_dur_total])
            oa_map = oa_map[["CODIGO_SIES_N", "DURACION_TOTAL_NUM"]].dropna()

        if "CUADRO HOMOLOGACIÓN" in xls.sheet_names:
            hom = pd.read_excel(path, sheet_name="CUADRO HOMOLOGACIÓN")
            hom_code = _pick_first_column(hom, ["CODCARPR"])
            hom_dur = _pick_first_column(hom, ["DURACION_ESTUDIOS_REF"])
            hom_sies = _pick_first_column(hom, ["CODIGO_SIES"])

            if hom_code and hom_dur:
                h = hom[[hom_code, hom_dur]].copy()
                h = h.rename(columns={hom_code: "CODCARR_N", hom_dur: "DURACION_SEMESTRES"})
                h["SOURCE"] = "enrich:CUADRO_HOMOLOGACION:DURACION_ESTUDIOS_REF"
                h["SOURCE_PRIORITY"] = 1
                extra_frames.append(h)

            if hom_code and hom_sies and oa_map is not None and not oa_map.empty:
                h2 = hom[[hom_code, hom_sies]].copy()
                h2["CODIGO_SIES_N"] = h2[hom_sies].map(_normalize_text)
                h2["CODCARR_N"] = h2[hom_code].map(_normalize_text)
                h2 = h2.merge(oa_map, on="CODIGO_SIES_N", how="left")
                h2 = h2.rename(columns={"DURACION_TOTAL_NUM": "DURACION_SEMESTRES"})
                h2["SOURCE"] = "enrich:CUADRO_HOMOLOGACION+5320:DURACION_TOTAL"
                h2["SOURCE_PRIORITY"] = 2
                extra_frames.append(h2[["CODCARR_N", "DURACION_SEMESTRES", "SOURCE", "SOURCE_PRIORITY"]])

        puente_path = Path(__file__).with_name("puente_sies.tsv")
        if puente_path.exists() and oa_map is not None and not oa_map.empty:
            pu = pd.read_csv(puente_path, sep="\t")
            if {"CODCARPR", "CODIGO_CARRERA_SIES"}.issubset(pu.columns):
                pu2 = pu[["CODCARPR", "CODIGO_CARRERA_SIES"]].copy()
                pu2["CODCARR_N"] = pu2["CODCARPR"].map(_normalize_text)
                pu2["CODIGO_SIES_N"] = pu2["CODIGO_CARRERA_SIES"].map(_normalize_text)
                pu2 = pu2.merge(oa_map, on="CODIGO_SIES_N", how="left")
                pu2 = pu2.rename(columns={"DURACION_TOTAL_NUM": "DURACION_SEMESTRES"})
                pu2["SOURCE"] = "enrich:puente_sies+5320:DURACION_TOTAL"
                pu2["SOURCE_PRIORITY"] = 3
                extra_frames.append(pu2[["CODCARR_N", "DURACION_SEMESTRES", "SOURCE", "SOURCE_PRIORITY"]])

    all_rows = [base_df[["CODCARR_N", "DURACION_SEMESTRES", "SOURCE", "SOURCE_PRIORITY"]]]
    all_rows.extend(extra_frames)
    out = _aggregate_duration_rows(pd.concat(all_rows, ignore_index=True))
    base_clean = _aggregate_duration_rows(base_df[["CODCARR_N", "DURACION_SEMESTRES", "SOURCE", "SOURCE_PRIORITY"]])

    base_codes = set(base_clean["CODCARR_N"]) if not base_clean.empty else set()
    final_codes = set(out["CODCARR_N"]) if not out.empty else set()
    enriched_codes = final_codes - base_codes

    meta = {
        "duration_source": str(path),
        "duration_sheet": selected_sheet,
        "duration_rows": int(len(base_df)),
        "duration_mapped_programs": int(out["CODCARR_N"].nunique()),
        "duration_code_column": selected_code_col,
        "duration_value_column": selected_dur_col,
        "duration_reference_codes": int(len(reference_codes)) if reference_codes else 0,
        "duration_overlap_reference_codes": int(len(set(out["CODCARR_N"]) & set(reference_codes))) if reference_codes else 0,
        "duration_base_codes": int(len(base_codes)),
        "duration_enriched_codes": int(len(enriched_codes)),
        "duration_sources_used": sorted(
            set(
                src
                for src in out.get("DURACION_FUENTES", pd.Series(dtype=str)).dropna().astype(str)
            )
        ),
    }
    return out, meta


def _classify_niv_aca(
    df: pd.DataFrame,
    tolerance: int,
    periodo_policy: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        codcli = r["CODCLI_N"]
        carrera_h = r.get("CODCARR_H_MAIN", "")
        carrera_d = r.get("CODCARPR_DA_MAIN", "")
        carrera_d_last = r.get("CODCARPR_DA_LAST", "")
        carrera_ref = carrera_d_last if carrera_d_last else (carrera_d if carrera_d else carrera_h)

        insuff: list[str] = []
        manual: list[str] = []

        if r.get("CODCARPR_DA_COUNT", 0) == 0:
            insuff.append("sin_registro_en_datos_alumnos")
        if r.get("CODCARR_H_COUNT", 0) == 0:
            insuff.append("sin_registro_en_hoja1")
        if r.get("CODCARR_H_COUNT", 0) > 1:
            manual.append("multiples_carreras_en_hoja1")
        if r.get("CODCARPR_DA_COUNT", 0) > 1:
            manual.append("multiples_carreras_en_datos_alumnos")
        if carrera_h and carrera_d and carrera_h != carrera_d:
            manual.append("conflicto_carrera_hoja1_vs_datos_alumnos")

        dur = pd.to_numeric(pd.Series([r.get("DURACION_SEMESTRES")]), errors="coerce").iloc[0]
        dur_ambigua = _as_bool(r.get("DURACION_AMBIGUA", False))
        if pd.isna(dur):
            insuff.append("sin_duracion_carrera")
        if dur_ambigua:
            manual.append("duracion_carrera_ambigua")

        anio_ing = pd.to_numeric(pd.Series([r.get("ANOINGRESO_NUM")]), errors="coerce").iloc[0]
        sem_ing_raw = pd.to_numeric(pd.Series([r.get("PERIODOINGRESO_NUM")]), errors="coerce").iloc[0]
        anio_mat = pd.to_numeric(pd.Series([r.get("ANOMATRICULA_NUM")]), errors="coerce").iloc[0]
        sem_mat_raw = pd.to_numeric(pd.Series([r.get("PERIODOMATRICULA_NUM")]), errors="coerce").iloc[0]

        sem_ing, sem_ing_trace = _normalize_semester(sem_ing_raw, periodo_policy)
        sem_mat, sem_mat_trace = _normalize_semester(sem_mat_raw, periodo_policy)

        if pd.isna(anio_ing):
            insuff.append("sin_anio_ingreso")
        if not _valid_semester(sem_ing):
            insuff.append("semestre_ingreso_fuera_1_2")
        if pd.isna(anio_mat):
            insuff.append("sin_anio_matricula")
        if not _valid_semester(sem_mat):
            insuff.append("semestre_matricula_fuera_1_2")

        nivel_da = pd.to_numeric(pd.Series([r.get("NIVEL_DA_NUM")]), errors="coerce").iloc[0]
        nivel_h = pd.to_numeric(pd.Series([r.get("NIVEL_HOJA1_LAST")]), errors="coerce").iloc[0]
        nivel_obs = nivel_da if pd.notna(nivel_da) else nivel_h
        fuente_nivel = "DatosAlumnos.NIVEL" if pd.notna(nivel_da) else ("Hoja1.NIVEL" if pd.notna(nivel_h) else "")
        if pd.isna(nivel_obs):
            insuff.append("sin_nivel_observado")

        idx_ing = _semester_index(anio_ing, sem_ing)
        idx_mat = _semester_index(anio_mat, sem_mat)
        nivel_esperado = float("nan")
        diff = float("nan")
        if pd.notna(idx_ing) and pd.notna(idx_mat):
            nivel_esperado = float(idx_mat - idx_ing + 1)
            if nivel_esperado < 1:
                manual.append("nivel_esperado_menor_a_1")

        if pd.notna(nivel_esperado) and pd.notna(dur):
            if nivel_esperado > dur:
                manual.append("nivel_esperado_supera_duracion")
        if pd.notna(nivel_obs) and pd.notna(dur):
            if nivel_obs < 1:
                manual.append("nivel_observado_menor_a_1")
            if nivel_obs > dur:
                manual.append("nivel_observado_supera_duracion")

        anio_codcli = _infer_year_from_codcli(codcli)
        if pd.notna(anio_codcli) and pd.notna(anio_ing):
            if abs(anio_codcli - anio_ing) > 1:
                manual.append("conflicto_anio_codcli_vs_anioingreso")

        if pd.notna(nivel_esperado) and pd.notna(nivel_obs):
            diff = abs(nivel_obs - nivel_esperado)
            if diff > tolerance:
                manual.append("nivel_observado_no_coherente_con_nivel_esperado")

        if manual:
            clasificacion = "requiere_revision_manual"
        elif insuff:
            clasificacion = "sin_insumos_suficientes"
        else:
            clasificacion = "confirmado_1_a_1"

        rows.append(
            {
                "CODCLI": codcli,
                "CODCARR_HOJA1": carrera_h,
                "CODCARPR_DATOS_ALUMNOS": carrera_d,
                "CODCARPR_DATOS_ALUMNOS_LAST": carrera_d_last,
                "CODCARR_REFERENCIA": carrera_ref,
                "ANOINGRESO_REF": anio_ing,
                "PERIODOINGRESO_RAW": sem_ing_raw,
                "PERIODOINGRESO_REF": sem_ing,
                "ANOMATRICULA_REF": anio_mat,
                "PERIODOMATRICULA_RAW": sem_mat_raw,
                "PERIODOMATRICULA_REF": sem_mat,
                "NIVEL_OBSERVADO": nivel_obs,
                "FUENTE_NIVEL_OBSERVADO": fuente_nivel,
                "NIVEL_ESPERADO": nivel_esperado,
                "DIFERENCIA_NIVELES_ABS": diff,
                "DURACION_SEMESTRES": dur,
                "DURACION_AMBIGUA": dur_ambigua,
                "DURACION_FUENTES": r.get("DURACION_FUENTES", ""),
                "ANO_INFERIDO_CODCLI": anio_codcli,
                "CLASIFICACION_NIV_ACA": clasificacion,
                "MOTIVOS_REVISION_MANUAL": " | ".join(dict.fromkeys(manual)),
                "MOTIVOS_INSUMOS": " | ".join(dict.fromkeys(insuff)),
                "TRACE_LLAVE_PRIMARIA": "CODCLI",
                "TRACE_CRUCE_CARRERA": "CODCARR(Hoja1)=CODCARPR(DatosAlumnos)",
                "TRACE_REGLA": "nivel_esperado_por_ingreso_vs_matricula_con_restriccion_duracion",
                "TRACE_PERIODO_POLICY": periodo_policy,
                "TRACE_PERIODOINGRESO": sem_ing_trace,
                "TRACE_PERIODOMATRICULA": sem_mat_trace,
            }
        )

    return pd.DataFrame(rows)


def _build_phase2_dataset(
    hoja1: pd.DataFrame,
    datos: pd.DataFrame,
    duraciones: pd.DataFrame,
    sample_codcli: int | None,
    sample_seed: int,
) -> pd.DataFrame:
    h_profile = _build_hoja1_profile(hoja1)
    d_profile = _build_datos_alumnos_profile(datos)

    universe = h_profile.merge(d_profile, on="CODCLI_N", how="left")
    universe["CARRERA_REF"] = universe["CODCARPR_DA_LAST"].where(
        universe["CODCARPR_DA_LAST"].astype(str).str.strip() != "",
        universe["CODCARR_H_MAIN"],
    )

    if not duraciones.empty:
        universe = universe.merge(
            duraciones,
            left_on="CARRERA_REF",
            right_on="CODCARR_N",
            how="left",
        ).drop(columns=["CODCARR_N"])
    else:
        universe["DURACION_SEMESTRES"] = pd.NA
        universe["DURACION_AMBIGUA"] = False

    if sample_codcli is not None:
        unique_codcli = universe["CODCLI_N"].dropna().drop_duplicates()
        n = min(sample_codcli, len(unique_codcli))
        sample = unique_codcli.sample(n=n, random_state=sample_seed)
        universe = universe[universe["CODCLI_N"].isin(set(sample))].copy()

    return universe


def _run_base_pipeline(args: argparse.Namespace, out_dir: Path) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    if args.proceso_base in {"avance", "ambos"}:
        reports["avance"] = base.ejecutar_pipeline(args.input, out_dir)
    if args.proceso_base in {"matricula", "ambos"}:
        cat = base._resolve_optional_path(args.catalogo_manual_tsv, base.DEFAULT_CATALOGO_MANUAL_CANDIDATES)
        pu = base._resolve_optional_path(args.puente_sies_tsv, base.DEFAULT_PUENTE_SIES_CANDIDATES)
        reports["matricula"] = base.ejecutar_pipeline_matricula_unificada_legacy_like(
            args.input,
            out_dir,
            sheet_name=args.sheet,
            catalogo_manual_tsv_path=cat,
            puente_sies_tsv_path=pu,
            excluir_diplomados=args.excluir_diplomados,
        )
    return reports


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Fase 2 NIV_ACA: diagnóstico trazable de consistencia alumno-carrera-ingreso-nivel "
            "con soporte opcional de duración de carrera."
        )
    )
    p.add_argument("--input", required=True, type=Path, help="Excel fuente (debe contener Hoja1 y DatosAlumnos).")
    p.add_argument("--output-dir", default="resultados", type=Path, help="Directorio de salida.")
    p.add_argument(
        "--proceso-base",
        default="none",
        choices=["none", "avance", "matricula", "ambos"],
        help="Opcional: ejecutar pipeline base antes del diagnóstico Fase 2.",
    )
    p.add_argument("--sheet", default=None, help="Hoja para proceso matrícula base.")
    p.add_argument("--catalogo-manual-tsv", default=None, help="TSV catálogo manual para proceso base.")
    p.add_argument("--puente-sies-tsv", default=None, help="TSV puente SIES para proceso base.")
    p.add_argument(
        "--excluir-diplomados",
        action="store_true",
        default=True,
        help="Para proceso base matrícula: excluir diplomados en asignación SIES.",
    )
    p.add_argument(
        "--oferta-duracion",
        type=Path,
        default=None,
        help=(
            "Archivo opcional con duración de carrera (csv/tsv/xlsx). "
            "Debe incluir código de carrera y duración en semestres."
        ),
    )
    p.add_argument(
        "--nivel-tolerancia",
        type=int,
        default=1,
        help="Tolerancia permitida entre nivel observado y nivel esperado para confirmar 1 a 1.",
    )
    p.add_argument(
        "--periodo-policy",
        choices=["strict", "map_3_to_2"],
        default="strict",
        help="Política de semestre: strict (solo 1/2) o map_3_to_2 (interpreta 3 como 2).",
    )
    p.add_argument(
        "--sample-codcli",
        type=int,
        default=None,
        help="Opcional: limitar diagnóstico a una muestra aleatoria de CODCLI (ej. 1000).",
    )
    p.add_argument("--sample-seed", type=int, default=42, help="Semilla para muestreo de CODCLI.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.input = args.input.expanduser().resolve()
    if not args.input.exists():
        raise FileNotFoundError(f"No existe archivo de entrada: {args.input}")

    out_dir = args.output_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    base_reports = _run_base_pipeline(args, out_dir)

    hoja1, datos = _load_source_views(args.input)
    reference_codes: set[str] = set()
    if "CODCARR" in hoja1.columns:
        reference_codes |= set(hoja1["CODCARR"].map(_normalize_text).replace("", pd.NA).dropna().tolist())
    if "CODCARPR" in datos.columns:
        reference_codes |= set(datos["CODCARPR"].map(_normalize_text).replace("", pd.NA).dropna().tolist())

    dur_df, dur_meta = _load_duration_table(
        args.oferta_duracion.expanduser().resolve() if args.oferta_duracion else None,
        reference_codes=reference_codes if reference_codes else None,
    )
    universe = _build_phase2_dataset(hoja1, datos, dur_df, args.sample_codcli, args.sample_seed)
    diag = _classify_niv_aca(universe, tolerance=args.nivel_tolerancia, periodo_policy=args.periodo_policy)

    summary = (
        diag["CLASIFICACION_NIV_ACA"]
        .value_counts(dropna=False)
        .rename_axis("clasificacion")
        .reset_index(name="n")
        .sort_values(["n", "clasificacion"], ascending=[False, True])
    )

    diag_path = out_dir / RESULT_DIAG_FILENAME
    sum_path = out_dir / RESULT_SUMMARY_FILENAME
    meta_path = out_dir / RESULT_META_FILENAME
    diag.to_csv(diag_path, index=False, encoding="utf-8")
    summary.to_csv(sum_path, index=False, encoding="utf-8")

    meta = {
        "input": str(args.input),
        "output_dir": str(out_dir),
        "proceso_base": args.proceso_base,
        "sample_codcli": args.sample_codcli,
        "sample_seed": args.sample_seed,
        "nivel_tolerancia": args.nivel_tolerancia,
        "periodo_policy": args.periodo_policy,
        "rows_universe": int(len(universe)),
        "rows_diag": int(len(diag)),
        "hoja1_rows": int(len(hoja1)),
        "datos_alumnos_rows": int(len(datos)),
        "duracion_meta": dur_meta,
        "clasificacion_counts": summary.set_index("clasificacion")["n"].to_dict(),
        "base_reports_keys": list(base_reports.keys()),
        "outputs": {
            "diagnostico_csv": str(diag_path),
            "resumen_csv": str(sum_path),
        },
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
