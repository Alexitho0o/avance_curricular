#!/usr/bin/env python3
"""
Motor de derivación CAMPOS ING — MU 2026
Campos: ANIO_ING_ACT, SEM_ING_ACT, ANIO_ING_ORI, SEM_ING_ORI

Lee DatosAlumnos + Hoja1 + base_datos + FOR_ING_ACT trace,
aplica reglas normativas (config JSON) y genera:
  - campos_ing_trace_long.tsv     (trazabilidad por registro)
  - AUDIT_CAMPOS_ING.xlsx         (auditoría completa)
  - campos_ing_governance_report.md (reporte + dictamen)
"""
import json, os, sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

# ── paths ────────────────────────────────────────────────────────────────
BASE     = Path(__file__).resolve().parent.parent          # avance_curricular/
EXCEL_IN = Path(os.environ.get(
    "EXCEL_INPUT",
    "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx"))
CFG_PATH = BASE / "control" / "config_campos_ing.json"
FOR_TRACE = BASE / "control" / "for_ing_act_trace_long.tsv"
OUT_DIR  = BASE / "resultados"
CTRL_DIR = BASE / "control"

TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── load config ──────────────────────────────────────────────────────────
with open(CFG_PATH) as f:
    CFG = json.load(f)

ANIO_ACT_RANGE = tuple(CFG["campos"]["ANIO_ING_ACT"]["rango"])
ANIO_ACT_FALLBACK = CFG["campos"]["ANIO_ING_ACT"]["fallback_ultimo_recurso"]
SEM_ACT_CATALOGO = set(CFG["campos"]["SEM_ING_ACT"]["catalogo"])
SEM_ACT_MAPEO = {int(k): v for k, v in CFG["campos"]["SEM_ING_ACT"]["regla_institucional"]["mapeo"].items()}
SEM_ACT_FALLBACK = CFG["campos"]["SEM_ING_ACT"]["fallback_ultimo_recurso"]
ANIO_ORI_RANGE = tuple(CFG["campos"]["ANIO_ING_ORI"]["rango"])
SEM_ORI_CATALOGO = set(CFG["campos"]["SEM_ING_ORI"]["catalogo"])


# ═══════════════════════════════════════════════════════════════════════════
# 1. CARGA
# ═══════════════════════════════════════════════════════════════════════════

def load_data():
    """Carga DatosAlumnos filtrado + Hoja1 filtrado + trace FOR_ING_ACT."""
    xls = pd.ExcelFile(EXCEL_IN)
    da  = pd.read_excel(xls, sheet_name="DatosAlumnos")
    h1  = pd.read_excel(xls, sheet_name="Hoja1",
                        usecols=["CODCLI", "RUT", "CODCARR", "ANO", "PERIODO"])
    bd  = pd.read_excel(xls, sheet_name="base_datos")

    ruts_bd = set(bd["N_DOC"].dropna().astype(int))

    da["_RUT_NUM"] = (da["RUT"].astype(str)
                      .str.extract(r"(\d+)", expand=False)
                      .astype(float).astype("Int64"))
    h1["_RUT_NUM"] = (h1["RUT"].astype(str)
                      .str.extract(r"(\d+)", expand=False)
                      .astype(float).astype("Int64"))

    da_f = da[da["_RUT_NUM"].isin(ruts_bd)].copy()
    h1_f = h1[h1["_RUT_NUM"].isin(ruts_bd)].copy()

    # Cast numéricos
    for col in ["ANOINGRESO", "PERIODOINGRESO", "ANOMATRICULA", "PERIODOMATRICULA"]:
        if col in da_f.columns:
            da_f[col] = pd.to_numeric(da_f[col], errors="coerce").astype("Int64")
    h1_f["ANO"] = pd.to_numeric(h1_f["ANO"], errors="coerce").astype("Int64")
    h1_f["PERIODO"] = pd.to_numeric(h1_f["PERIODO"], errors="coerce").astype("Int64")

    # Normalizar CODCARPR
    if "CODCARPR" in da_f.columns:
        da_f["CODCARPR"] = da_f["CODCARPR"].astype(str).str.upper().str.strip()
    if "CODCARR" in h1_f.columns:
        h1_f["CODCARR"] = h1_f["CODCARR"].astype(str).str.upper().str.strip()

    # Cargar trace FOR_ING_ACT
    trace_for = pd.read_csv(FOR_TRACE, sep="\t")

    return da_f, h1_f, trace_for


# ═══════════════════════════════════════════════════════════════════════════
# 2. DERIVACIÓN ANIO_ING_ACT  (Campo Q)
# ═══════════════════════════════════════════════════════════════════════════

def derive_anio_ing_act(da: pd.DataFrame) -> pd.DataFrame:
    """
    Cascada: ANOINGRESO → DA_ANOINGRESO → CODCLI[:4] → fallback 2026
    """
    da["ANIO_ING_ACT"] = pd.NA
    da["ANIO_ING_ACT_FUENTE"] = ""
    da["ANIO_ING_ACT_REGLA"] = ""

    lo, hi = ANIO_ACT_RANGE

    for idx, row in da.iterrows():
        # Regla R_ACT_01: ANOINGRESO directo
        val = row.get("ANOINGRESO")
        if pd.notna(val):
            v = int(val)
            if lo <= v <= hi:
                da.at[idx, "ANIO_ING_ACT"] = v
                da.at[idx, "ANIO_ING_ACT_FUENTE"] = "ANOINGRESO"
                da.at[idx, "ANIO_ING_ACT_REGLA"] = "R_ACT_01"
                continue

        # Regla R_ACT_02: DA_ANOINGRESO (si viniera de otra fuente)
        da_ano = row.get("DA_ANOINGRESO")
        if pd.notna(da_ano):
            v = int(da_ano)
            if lo <= v <= hi:
                da.at[idx, "ANIO_ING_ACT"] = v
                da.at[idx, "ANIO_ING_ACT_FUENTE"] = "DA_ANOINGRESO"
                da.at[idx, "ANIO_ING_ACT_REGLA"] = "R_ACT_02"
                continue

        # Regla R_ACT_03: Inferencia desde CODCLI
        codcli = str(row.get("CODCLI", ""))
        if len(codcli) >= 4:
            try:
                ano_codcli = int(codcli[:4])
                if lo <= ano_codcli <= hi:
                    da.at[idx, "ANIO_ING_ACT"] = ano_codcli
                    da.at[idx, "ANIO_ING_ACT_FUENTE"] = "CODCLI_INFERIDO"
                    da.at[idx, "ANIO_ING_ACT_REGLA"] = "R_ACT_03"
                    continue
            except ValueError:
                pass

        # Regla R_ACT_04: Fallback último recurso
        da.at[idx, "ANIO_ING_ACT"] = ANIO_ACT_FALLBACK
        da.at[idx, "ANIO_ING_ACT_FUENTE"] = "DEFAULT"
        da.at[idx, "ANIO_ING_ACT_REGLA"] = "R_ACT_04"

    da["ANIO_ING_ACT"] = da["ANIO_ING_ACT"].astype("Int64")
    return da


# ═══════════════════════════════════════════════════════════════════════════
# 3. DERIVACIÓN SEM_ING_ACT  (Campo R)
# ═══════════════════════════════════════════════════════════════════════════

def derive_sem_ing_act(da: pd.DataFrame) -> pd.DataFrame:
    """
    Regla institucional: PERIODOINGRESO {1→1, 2→2, 3→2}
    Fallback: DA_PERIODOINGRESO → default 1
    """
    da["SEM_ING_ACT"] = pd.NA
    da["SEM_ING_ACT_FUENTE"] = ""
    da["SEM_ING_ACT_REGLA"] = ""

    for idx, row in da.iterrows():
        # R_SEM_01 / R_SEM_02: PERIODOINGRESO directo con mapeo
        pi = row.get("PERIODOINGRESO")
        if pd.notna(pi):
            pi_int = int(pi)
            mapped = SEM_ACT_MAPEO.get(pi_int)
            if mapped is not None:
                da.at[idx, "SEM_ING_ACT"] = mapped
                da.at[idx, "SEM_ING_ACT_FUENTE"] = "PERIODOINGRESO"
                if pi_int == 1:
                    da.at[idx, "SEM_ING_ACT_REGLA"] = "R_SEM_01"
                else:
                    da.at[idx, "SEM_ING_ACT_REGLA"] = "R_SEM_02"
                continue

        # R_SEM_03: DA_PERIODOINGRESO
        da_pi = row.get("DA_PERIODOINGRESO")
        if pd.notna(da_pi):
            da_pi_int = int(da_pi)
            mapped = SEM_ACT_MAPEO.get(da_pi_int)
            if mapped is not None:
                da.at[idx, "SEM_ING_ACT"] = mapped
                da.at[idx, "SEM_ING_ACT_FUENTE"] = "DA_PERIODOINGRESO"
                da.at[idx, "SEM_ING_ACT_REGLA"] = "R_SEM_03"
                continue

        # R_SEM_04: Fallback
        da.at[idx, "SEM_ING_ACT"] = SEM_ACT_FALLBACK
        da.at[idx, "SEM_ING_ACT_FUENTE"] = "DEFAULT"
        da.at[idx, "SEM_ING_ACT_REGLA"] = "R_SEM_04"

    da["SEM_ING_ACT"] = da["SEM_ING_ACT"].astype("Int64")
    return da


# ═══════════════════════════════════════════════════════════════════════════
# 4. DERIVACIÓN ANIO_ING_ORI + SEM_ING_ORI  (Campos S, T)
# ═══════════════════════════════════════════════════════════════════════════

def derive_campos_ori(da: pd.DataFrame, h1: pd.DataFrame,
                      trace_for: pd.DataFrame) -> pd.DataFrame:
    """
    Derivación según FOR_ING_ACT:
      FOR=1  → ORI = ACT (copia)
      FOR=11 → ORI = TNS_PREV_MIN_ANO_DA / periodo TNS en Hoja1
      FOR=2  → ORI = 1900/0 (sin datos origen)
      FOR=3  → buscar programa anterior en DA, luego Hoja1
      FOR=4  → ORI = 1900/0 (bloqueado)
    """
    # Merge FOR_ING_ACT + flags TNS
    for_cols = ["CODCLI", "FOR_ING_ACT", "TIENE_TNS_PREV_DA",
                "TNS_PREV_MIN_ANO_DA", "TNS_PREV_CODCLI_EJEMPLO_DA"]
    for_cols = [c for c in for_cols if c in trace_for.columns]
    trace_sub = trace_for[for_cols].copy()
    da = da.merge(trace_sub, on="CODCLI", how="left", suffixes=("", "_FOR"))

    # Defaults
    da["ANIO_ING_ORI"] = pd.NA
    da["ANIO_ING_ORI_FUENTE"] = ""
    da["ANIO_ING_ORI_REGLA"] = ""
    da["SEM_ING_ORI"] = pd.NA
    da["SEM_ING_ORI_FUENTE"] = ""
    da["SEM_ING_ORI_REGLA"] = ""

    # Pre-compute lookups for FOR=3
    # All DatosAlumnos by RUT (full, with different CODCLI)
    lookup_cols = ["CODCLI", "ANOINGRESO", "PERIODOINGRESO"]
    if "CODCARPR" in da.columns:
        lookup_cols.append("CODCARPR")
    da_by_rut = da.groupby("_RUT_NUM").apply(
        lambda g: g[lookup_cols].to_dict("records"),
        include_groups=False
    ).to_dict()

    # Hoja1 by RUT: min ANO (with different CODCARR)
    h1_by_rut = {}
    for rut, grp in h1.groupby("_RUT_NUM"):
        h1_by_rut[rut] = grp[["CODCLI", "CODCARR", "ANO", "PERIODO"]].to_dict("records")

    lo_ori, hi_ori = ANIO_ORI_RANGE

    for idx, row in da.iterrows():
        for_code = row.get("FOR_ING_ACT")
        if pd.isna(for_code):
            for_code = 1  # default si no tiene trace
        for_code = int(for_code)
        anio_act = row["ANIO_ING_ACT"]
        sem_act = row["SEM_ING_ACT"]
        rut = row["_RUT_NUM"]
        codcli = str(row.get("CODCLI", ""))

        # ── ANIO_ING_ORI ──
        if for_code == 1:
            # R_ORI_A01: Directo → ORI = ACT
            da.at[idx, "ANIO_ING_ORI"] = anio_act
            da.at[idx, "ANIO_ING_ORI_FUENTE"] = "COPIA_ACTUAL"
            da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A01"
            # R_ORI_S01: SEM_ORI = SEM_ACT
            da.at[idx, "SEM_ING_ORI"] = sem_act
            da.at[idx, "SEM_ING_ORI_FUENTE"] = "COPIA_ACTUAL"
            da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S01"
            continue

        if for_code == 11:
            # R_ORI_A02 / R_ORI_A03: Articulación
            tns_ano = row.get("TNS_PREV_MIN_ANO_DA")
            if pd.notna(tns_ano):
                tns_ano_int = int(tns_ano)
                da.at[idx, "ANIO_ING_ORI"] = tns_ano_int
                da.at[idx, "ANIO_ING_ORI_FUENTE"] = "TNS_PREV"
                da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A02"
                # R_ORI_S03/S04: Periodo TNS
                tns_codcli_ej = str(row.get("TNS_PREV_CODCLI_EJEMPLO_DA", ""))
                sem_ori = _lookup_tns_periodo(rut, tns_codcli_ej, h1_by_rut)
                if sem_ori is not None:
                    da.at[idx, "SEM_ING_ORI"] = sem_ori
                    da.at[idx, "SEM_ING_ORI_FUENTE"] = "TNS_PREV_PERIODO"
                    da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S03"
                else:
                    da.at[idx, "SEM_ING_ORI"] = 1
                    da.at[idx, "SEM_ING_ORI_FUENTE"] = "DEFAULT"
                    da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S04"
            else:
                da.at[idx, "ANIO_ING_ORI"] = 1900
                da.at[idx, "ANIO_ING_ORI_FUENTE"] = "DESCONOCIDO"
                da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A03"
                da.at[idx, "SEM_ING_ORI"] = 0
                da.at[idx, "SEM_ING_ORI_FUENTE"] = "REGLA_1900"
                da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S02"
            continue

        if for_code == 2:
            # R_ORI_A04: Continuidad sin datos origen
            da.at[idx, "ANIO_ING_ORI"] = 1900
            da.at[idx, "ANIO_ING_ORI_FUENTE"] = "DESCONOCIDO"
            da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A04"
            da.at[idx, "SEM_ING_ORI"] = 0
            da.at[idx, "SEM_ING_ORI_FUENTE"] = "REGLA_1900"
            da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S02"
            continue

        if for_code == 3:
            # R_ORI_A05 / R_ORI_A06: Cambio interno
            ori_ano, ori_sem = _lookup_programa_anterior(
                rut, codcli, da_by_rut, h1_by_rut)
            if ori_ano is not None:
                da.at[idx, "ANIO_ING_ORI"] = ori_ano
                da.at[idx, "ANIO_ING_ORI_FUENTE"] = "PROG_ANTERIOR_DA"
                da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A05"
                sem_val = ori_sem if ori_sem is not None else 0
                da.at[idx, "SEM_ING_ORI"] = sem_val
                da.at[idx, "SEM_ING_ORI_FUENTE"] = "PROG_ANTERIOR_DA" if ori_sem else "DEFAULT"
                da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S05" if ori_sem else "R_ORI_S06"
            else:
                da.at[idx, "ANIO_ING_ORI"] = 1900
                da.at[idx, "ANIO_ING_ORI_FUENTE"] = "DESCONOCIDO"
                da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A06"
                da.at[idx, "SEM_ING_ORI"] = 0
                da.at[idx, "SEM_ING_ORI_FUENTE"] = "REGLA_1900"
                da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S02"
            continue

        # FOR=4 o desconocido: R_ORI_A07
        da.at[idx, "ANIO_ING_ORI"] = 1900
        da.at[idx, "ANIO_ING_ORI_FUENTE"] = "DESCONOCIDO"
        da.at[idx, "ANIO_ING_ORI_REGLA"] = "R_ORI_A07"
        da.at[idx, "SEM_ING_ORI"] = 0
        da.at[idx, "SEM_ING_ORI_FUENTE"] = "REGLA_1900"
        da.at[idx, "SEM_ING_ORI_REGLA"] = "R_ORI_S02"

    da["ANIO_ING_ORI"] = da["ANIO_ING_ORI"].astype("Int64")
    da["SEM_ING_ORI"] = da["SEM_ING_ORI"].astype("Int64")
    return da


def _lookup_tns_periodo(rut, tns_codcli_ej: str, h1_by_rut: dict) -> int | None:
    """Busca periodo del primer registro TNS en Hoja1 para el RUT."""
    records = h1_by_rut.get(rut, [])
    # Buscar el registro que coincide con el CODCLI ejemplo TNS
    for rec in records:
        if str(rec.get("CODCLI", "")) == tns_codcli_ej:
            p = rec.get("PERIODO")
            if pd.notna(p):
                p_int = int(p)
                if p_int in (1, 2, 3):
                    return 2 if p_int == 3 else p_int
    # Buscar cualquier registro TNS (CODCARR empieza con T) para el RUT
    for rec in sorted(records, key=lambda r: r.get("ANO", 9999)):
        codcarr = str(rec.get("CODCARR", ""))
        if codcarr.startswith("T"):
            p = rec.get("PERIODO")
            if pd.notna(p):
                p_int = int(p)
                if p_int in (1, 2, 3):
                    return 2 if p_int == 3 else p_int
    return None


def _lookup_programa_anterior(rut, codcli_actual: str,
                              da_by_rut: dict, h1_by_rut: dict
                              ) -> tuple[int | None, int | None]:
    """Para cambio interno (FOR=3): busca año/sem del programa anterior del mismo RUT."""
    # 1) Buscar en DatosAlumnos: otro CODCLI del mismo RUT con ANOINGRESO ≤ actual
    da_records = da_by_rut.get(rut, [])
    best_ano = None
    best_sem = None
    for rec in da_records:
        if str(rec.get("CODCLI", "")) == codcli_actual:
            continue
        ano = rec.get("ANOINGRESO")
        if pd.notna(ano):
            ano_int = int(ano)
            if best_ano is None or ano_int < best_ano:
                best_ano = ano_int
                p = rec.get("PERIODOINGRESO")
                best_sem = int(p) if pd.notna(p) else None

    # 2) Buscar en Hoja1: CODCARR diferente, ANO más antiguo
    h1_records = h1_by_rut.get(rut, [])
    # Extraer CODCARR del CODCLI actual (posición 5+ en CODCLI, primeros chars después de año+sem)
    codcarr_actual = codcli_actual[5:] if len(codcli_actual) > 5 else ""
    for rec in sorted(h1_records, key=lambda r: r.get("ANO", 9999)):
        codcarr = str(rec.get("CODCARR", ""))
        if codcarr and codcarr != codcarr_actual:
            ano = rec.get("ANO")
            if pd.notna(ano):
                ano_int = int(ano)
                if best_ano is None or ano_int < best_ano:
                    best_ano = ano_int
                    p = rec.get("PERIODO")
                    best_sem = int(p) if pd.notna(p) else None

    # Normalizar sem: {3,4,...}→2, fuera de {1,2}→None
    if best_sem is not None:
        if best_sem == 1:
            pass
        elif best_sem in (2, 3, 4):
            best_sem = 2 if best_sem != 1 else 1
        else:
            best_sem = None  # valor atípico → fallback

    return best_ano, best_sem


# ═══════════════════════════════════════════════════════════════════════════
# 5. VALIDACIONES
# ═══════════════════════════════════════════════════════════════════════════

def run_validations(da: pd.DataFrame) -> list[dict]:
    """Ejecuta validaciones normativas y devuelve hallazgos."""
    findings = []
    lo_act, hi_act = ANIO_ACT_RANGE
    lo_ori, hi_ori = ANIO_ORI_RANGE

    # V_RANGO_ACT
    fuera_act = da[(da["ANIO_ING_ACT"] < lo_act) | (da["ANIO_ING_ACT"] > hi_act)]
    if len(fuera_act) > 0:
        findings.append({
            "id": "V_RANGO_ACT", "severidad": "BLOQUEANTE",
            "msg": f"{len(fuera_act)} registros con ANIO_ING_ACT fuera de [{lo_act},{hi_act}]",
            "n": len(fuera_act), "codclis": fuera_act["CODCLI"].tolist()[:10]
        })

    # V_CATALOGO_SEM_ACT
    fuera_sem = da[~da["SEM_ING_ACT"].isin(SEM_ACT_CATALOGO)]
    if len(fuera_sem) > 0:
        findings.append({
            "id": "V_CATALOGO_SEM_ACT", "severidad": "BLOQUEANTE",
            "msg": f"{len(fuera_sem)} registros con SEM_ING_ACT fuera de {SEM_ACT_CATALOGO}",
            "n": len(fuera_sem), "codclis": fuera_sem["CODCLI"].tolist()[:10]
        })

    # V_RANGO_ORI
    fuera_ori = da[
        (da["ANIO_ING_ORI"] != 1900) &
        ((da["ANIO_ING_ORI"] < lo_ori) | (da["ANIO_ING_ORI"] > hi_ori))
    ]
    if len(fuera_ori) > 0:
        findings.append({
            "id": "V_RANGO_ORI", "severidad": "BLOQUEANTE",
            "msg": f"{len(fuera_ori)} registros con ANIO_ING_ORI fuera de [{lo_ori},{hi_ori}] ∪ {{1900}}",
            "n": len(fuera_ori), "codclis": fuera_ori["CODCLI"].tolist()[:10]
        })

    # V_CATALOGO_SEM_ORI
    fuera_sem_ori = da[~da["SEM_ING_ORI"].isin(SEM_ORI_CATALOGO)]
    if len(fuera_sem_ori) > 0:
        findings.append({
            "id": "V_CATALOGO_SEM_ORI", "severidad": "BLOQUEANTE",
            "msg": f"{len(fuera_sem_ori)} registros con SEM_ING_ORI fuera de {SEM_ORI_CATALOGO}",
            "n": len(fuera_sem_ori), "codclis": fuera_sem_ori["CODCLI"].tolist()[:10]
        })

    # V_COHERENCIA_FOR1
    for1 = da[da["FOR_ING_ACT"] == 1]
    bad_anio = for1[for1["ANIO_ING_ORI"] != for1["ANIO_ING_ACT"]]
    bad_sem = for1[for1["SEM_ING_ORI"] != for1["SEM_ING_ACT"]]
    if len(bad_anio) > 0 or len(bad_sem) > 0:
        n = max(len(bad_anio), len(bad_sem))
        findings.append({
            "id": "V_COHERENCIA_FOR1", "severidad": "BLOQUEANTE",
            "msg": f"{n} registros FOR=1 donde ORI ≠ ACT (anio:{len(bad_anio)}, sem:{len(bad_sem)})",
            "n": n
        })

    # V_COHERENCIA_FOR_NO1 (warning — ACT > ORI excepto ORI=1900)
    not1 = da[(da["FOR_ING_ACT"] != 1) & (da["ANIO_ING_ORI"] != 1900)]
    bad_order = not1[not1["ANIO_ING_ACT"] <= not1["ANIO_ING_ORI"]]
    if len(bad_order) > 0:
        findings.append({
            "id": "V_COHERENCIA_FOR_NO1", "severidad": "WARNING",
            "msg": f"{len(bad_order)} registros FOR≠1 donde ANIO_ACT ≤ ANIO_ORI (esperado ACT > ORI)",
            "n": len(bad_order), "codclis": bad_order["CODCLI"].tolist()[:10]
        })

    # V_COHERENCIA_1900
    ori_1900 = da[da["ANIO_ING_ORI"] == 1900]
    bad_1900 = ori_1900[ori_1900["SEM_ING_ORI"] != 0]
    if len(bad_1900) > 0:
        findings.append({
            "id": "V_COHERENCIA_1900", "severidad": "BLOQUEANTE",
            "msg": f"{len(bad_1900)} registros con ANIO_ORI=1900 pero SEM_ORI≠0",
            "n": len(bad_1900), "codclis": bad_1900["CODCLI"].tolist()[:10]
        })

    # V_NULOS
    for campo in ["ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI"]:
        nulos = da[da[campo].isna()]
        if len(nulos) > 0:
            findings.append({
                "id": f"V_NULO_{campo}", "severidad": "BLOQUEANTE",
                "msg": f"{len(nulos)} registros con {campo} nulo",
                "n": len(nulos)
            })

    return findings


# ═══════════════════════════════════════════════════════════════════════════
# 6. ARTEFACTOS
# ═══════════════════════════════════════════════════════════════════════════

TRACE_COLS = [
    "CODCLI", "_RUT_NUM",
    # Fuentes
    "ANOINGRESO", "PERIODOINGRESO", "ANOMATRICULA", "PERIODOMATRICULA",
    # FOR_ING_ACT
    "FOR_ING_ACT", "TIENE_TNS_PREV_DA", "TNS_PREV_MIN_ANO_DA",
    # Derivados
    "ANIO_ING_ACT", "ANIO_ING_ACT_FUENTE", "ANIO_ING_ACT_REGLA",
    "SEM_ING_ACT", "SEM_ING_ACT_FUENTE", "SEM_ING_ACT_REGLA",
    "ANIO_ING_ORI", "ANIO_ING_ORI_FUENTE", "ANIO_ING_ORI_REGLA",
    "SEM_ING_ORI", "SEM_ING_ORI_FUENTE", "SEM_ING_ORI_REGLA",
]


def write_trace_tsv(da: pd.DataFrame, path: Path):
    cols = [c for c in TRACE_COLS if c in da.columns]
    da[cols].to_csv(path, sep="\t", index=False)
    print(f"  ✓ Trace TSV: {path}  ({len(da)} filas)")


def write_audit_xlsx(da: pd.DataFrame, findings: list, path: Path):
    cols = [c for c in TRACE_COLS if c in da.columns]
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        da[cols].to_excel(w, sheet_name="TRAZABILIDAD", index=False)

        # Resumen ANIO_ING_ACT
        r_act = da["ANIO_ING_ACT"].value_counts().sort_index().reset_index()
        r_act.columns = ["ANIO_ING_ACT", "CONTEO"]
        r_act.to_excel(w, sheet_name="RESUMEN_ANIO_ACT", index=False)

        # Resumen SEM_ING_ACT
        r_sem = da["SEM_ING_ACT"].value_counts().sort_index().reset_index()
        r_sem.columns = ["SEM_ING_ACT", "CONTEO"]
        r_sem.to_excel(w, sheet_name="RESUMEN_SEM_ACT", index=False)

        # Resumen ANIO_ING_ORI
        r_ori = da["ANIO_ING_ORI"].value_counts().sort_index().reset_index()
        r_ori.columns = ["ANIO_ING_ORI", "CONTEO"]
        r_ori.to_excel(w, sheet_name="RESUMEN_ANIO_ORI", index=False)

        # Resumen SEM_ING_ORI
        r_sori = da["SEM_ING_ORI"].value_counts().sort_index().reset_index()
        r_sori.columns = ["SEM_ING_ORI", "CONTEO"]
        r_sori.to_excel(w, sheet_name="RESUMEN_SEM_ORI", index=False)

        # Cruce FOR x ANIO_ORI
        cruce = pd.crosstab(da["FOR_ING_ACT"], da["ANIO_ING_ORI"])
        cruce.to_excel(w, sheet_name="CRUCE_FOR_x_ORI")

        # Hallazgos
        fd = pd.DataFrame(findings)
        fd.to_excel(w, sheet_name="HALLAZGOS", index=False)
    print(f"  ✓ Audit XLSX: {path}")


def write_governance_report(da: pd.DataFrame, findings: list, path: Path):
    total = len(da)
    bloqueantes = [f for f in findings if f["severidad"] == "BLOQUEANTE"]
    errores     = [f for f in findings if f["severidad"] == "ERROR"]
    warnings    = [f for f in findings if f["severidad"] == "WARNING"]

    dictamen = "✅ LISTO PARA ENTREGA"
    if bloqueantes:
        dictamen = "❌ NO LISTO — hay errores bloqueantes"
    elif errores:
        dictamen = "❌ NO LISTO — hay errores"
    elif warnings:
        dictamen = "⚠️ LISTO CON OBSERVACIONES"

    # Distribuciones
    dist_anio_act = da["ANIO_ING_ACT"].value_counts().sort_index()
    dist_sem_act = da["SEM_ING_ACT"].value_counts().sort_index()
    dist_anio_ori = da["ANIO_ING_ORI"].value_counts().sort_index()
    dist_sem_ori = da["SEM_ING_ORI"].value_counts().sort_index()
    dist_regla_anio_act = da["ANIO_ING_ACT_REGLA"].value_counts()
    dist_regla_sem_act = da["SEM_ING_ACT_REGLA"].value_counts()
    dist_regla_anio_ori = da["ANIO_ING_ORI_REGLA"].value_counts()
    dist_regla_sem_ori = da["SEM_ING_ORI_REGLA"].value_counts()

    # Markdown
    lines = [
        f"# Reporte Gobernanza — Campos ING (Q, R, S, T)",
        f"",
        f"**Fecha generación:** {TS}",
        f"**Total registros:** {total}",
        f"**Dictamen:** {dictamen}",
        f"",
        f"## 1. ANIO_ING_ACT (Campo Q)",
        f"",
        f"| Año | Conteo |",
        f"|-----|--------|",
    ]
    for ano, cnt in dist_anio_act.items():
        lines.append(f"| {ano} | {cnt} |")
    lines += [
        f"",
        f"**Reglas aplicadas:**",
        f"",
        f"| Regla | Conteo |",
        f"|-------|--------|",
    ]
    for regla, cnt in dist_regla_anio_act.items():
        lines.append(f"| {regla} | {cnt} |")

    lines += [
        f"",
        f"## 2. SEM_ING_ACT (Campo R)",
        f"",
        f"| Semestre | Conteo |",
        f"|----------|--------|",
    ]
    for sem, cnt in dist_sem_act.items():
        lines.append(f"| {sem} | {cnt} |")
    lines += [
        f"",
        f"**Reglas aplicadas:**",
        f"",
        f"| Regla | Conteo |",
        f"|-------|--------|",
    ]
    for regla, cnt in dist_regla_sem_act.items():
        lines.append(f"| {regla} | {cnt} |")

    lines += [
        f"",
        f"## 3. ANIO_ING_ORI (Campo S)",
        f"",
        f"| Año | Conteo |",
        f"|-----|--------|",
    ]
    for ano, cnt in dist_anio_ori.items():
        lines.append(f"| {ano} | {cnt} |")
    lines += [
        f"",
        f"**Reglas aplicadas:**",
        f"",
        f"| Regla | Conteo |",
        f"|-------|--------|",
    ]
    for regla, cnt in dist_regla_anio_ori.items():
        lines.append(f"| {regla} | {cnt} |")

    lines += [
        f"",
        f"## 4. SEM_ING_ORI (Campo T)",
        f"",
        f"| Semestre | Conteo |",
        f"|----------|--------|",
    ]
    for sem, cnt in dist_sem_ori.items():
        lines.append(f"| {sem} | {cnt} |")
    lines += [
        f"",
        f"**Reglas aplicadas:**",
        f"",
        f"| Regla | Conteo |",
        f"|-------|--------|",
    ]
    for regla, cnt in dist_regla_sem_ori.items():
        lines.append(f"| {regla} | {cnt} |")

    lines += [
        f"",
        f"## 5. Coherencia FOR_ING_ACT × ORI",
        f"",
        f"| FOR | n | ANIO_ORI=1900 | ANIO_ORI≠1900 |",
        f"|-----|---|---------------|---------------|",
    ]
    for code in [1, 2, 3, 4, 11]:
        sub = da[da["FOR_ING_ACT"] == code]
        if len(sub) == 0:
            continue
        n_1900 = (sub["ANIO_ING_ORI"] == 1900).sum()
        n_ok = len(sub) - n_1900
        lines.append(f"| {code} | {len(sub)} | {n_1900} | {n_ok} |")

    lines += [
        f"",
        f"## 6. Hallazgos",
        f"",
    ]
    if not findings:
        lines.append("Sin hallazgos.")
    for f in findings:
        lines.append(f"- **[{f['severidad']}]** {f['id']}: {f['msg']}")

    lines += [
        f"",
        f"---",
        f"*Generado por motor_campos_ing.py — {TS}*",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ Governance Report: {path}")
    return dictamen


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print(f"═══ Motor Campos ING — MU 2026 ═══  ({TS})")
    print(f"  Excel : {EXCEL_IN}")
    print(f"  Config: {CFG_PATH}")
    print(f"  FOR   : {FOR_TRACE}")
    print()

    # 1. Carga
    print("1. Cargando datos...")
    da, h1, trace_for = load_data()
    print(f"   DatosAlumnos filtrados: {len(da)}")
    print(f"   Hoja1 filtrada:         {len(h1)}")
    print(f"   FOR_ING_ACT trace:      {len(trace_for)}")
    print()

    # 2. ANIO_ING_ACT
    print("2. Derivando ANIO_ING_ACT...")
    da = derive_anio_ing_act(da)
    print(f"   Distribución reglas: {da['ANIO_ING_ACT_REGLA'].value_counts().to_dict()}")
    print()

    # 3. SEM_ING_ACT
    print("3. Derivando SEM_ING_ACT...")
    da = derive_sem_ing_act(da)
    print(f"   Distribución reglas: {da['SEM_ING_ACT_REGLA'].value_counts().to_dict()}")
    print()

    # 4. ANIO_ING_ORI + SEM_ING_ORI
    print("4. Derivando ANIO_ING_ORI + SEM_ING_ORI...")
    da = derive_campos_ori(da, h1, trace_for)
    print(f"   Reglas ANIO_ORI: {da['ANIO_ING_ORI_REGLA'].value_counts().to_dict()}")
    print(f"   Reglas SEM_ORI:  {da['SEM_ING_ORI_REGLA'].value_counts().to_dict()}")
    print()

    # 5. Validaciones
    print("5. Ejecutando validaciones...")
    findings = run_validations(da)
    for f in findings:
        print(f"   [{f['severidad']}] {f['id']}: {f['msg']}")
    print()

    # 6. Artefactos
    print("6. Generando artefactos...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_trace_tsv(da, CTRL_DIR / "campos_ing_trace_long.tsv")
    write_audit_xlsx(da, findings, OUT_DIR / "AUDIT_CAMPOS_ING.xlsx")
    dictamen = write_governance_report(da, findings,
                                       CTRL_DIR / "campos_ing_governance_report.md")
    print()
    print(f"═══ DICTAMEN: {dictamen} ═══")

    return 0 if "BLOQUEANTE" not in dictamen else 1


if __name__ == "__main__":
    sys.exit(main())
