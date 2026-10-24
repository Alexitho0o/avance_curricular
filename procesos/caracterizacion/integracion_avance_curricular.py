# integracion_avance_curricular.py
# Módulo puente entre CARACTERIZACIÓN y avance_curricular.
# Fuente operativa: PROMEDIOSDEALUMNOS_7804.xlsx (Hoja1 + DatosAlumnos)
# DESACTIVADO POR DEFECTO. No ejecuta lógica productiva mientras la bandera esté en False.
# No modifica salidas existentes. No bloqueante. Reversible.

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# BANDERA MAESTRA — mantener en False hasta activación explícita supervisada
# ──────────────────────────────────────────────────────────────────────────────
ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = False

# ──────────────────────────────────────────────────────────────────────────────
# Logger interno — prefijo fijo para trazabilidad
# ──────────────────────────────────────────────────────────────────────────────
_log = logging.getLogger("MU_INTEGRACION")
if not _log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[MU_INTEGRACION] %(levelname)s - %(message)s"))
    _log.addHandler(_h)
    _log.setLevel(logging.INFO)


def log_mu(msg: str, level: str = "info") -> None:
    getattr(_log, level, _log.info)(msg)


# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE CÁLCULO ACADÉMICO
# Adaptadas de avance_curricular/codigo_gobernanza_v2.py (no importado).
# ──────────────────────────────────────────────────────────────────────────────

# Patrones de DESCRIPCION_ESTADO
_PAT_TRANSFER   = re.compile(r"CONVALID|HOMOLOG|RECONOC|EQUIV", re.IGNORECASE)
_PAT_APROB      = re.compile(r"APROB", re.IGNORECASE)
_PAT_APROB_HIS  = re.compile(r"APROB|CONVALID|RECONOC|EQUIV|HOMOLOG", re.IGNORECASE)

# PERIODO=3 equivale operacionalmente a 2do semestre (regla L619 de codigo_gobernanza_v2.py)
_PERIODOS_SEM2 = {2, 3}

# Columnas mínimas que Hoja1 debe tener
_COLS_HOJA1_MIN     = {"CODCLI", "ANO", "PERIODO", "CODRAMO"}
# Columnas opcionales útiles para métricas completas
_COLS_HOJA1_OPC     = {"DESCRIPCION_ESTADO", "CONVALIDADO", "NOTA_FINAL",
                        "NIVEL", "RUT", "DIG", "CODCARR", "ESTADO"}
# Columnas mínimas de DatosAlumnos para NIV_ACA
_COLS_DA_MIN        = {"CODCLI", "NIVEL"}


# ──────────────────────────────────────────────────────────────────────────────
# Funciones públicas — guardia y normalización
# ──────────────────────────────────────────────────────────────────────────────

def esta_activa() -> bool:
    """Retorna True solo si la bandera maestra está activa."""
    return bool(ACTIVAR_INTEGRACION_AVANCE_CURRICULAR)


def normalizar_codcli(serie: pd.Series) -> pd.Series:
    """Normaliza CODCLI a string con strip() para joins consistentes."""
    return serie.fillna("").astype(str).str.strip()


# ──────────────────────────────────────────────────────────────────────────────
# API principal — motor académico desde PROMEDIOS
# ──────────────────────────────────────────────────────────────────────────────

def cargar_promedios_contexto(
    ruta_promedios: str | Path,
    anio_ref: Optional[int] = None,
    periodo_ref: Optional[int] = None,
) -> Optional[dict]:
    """
    Lee PROMEDIOSDEALUMNOS_7804.xlsx y calcula métricas académicas por CODCLI.

    Esta función puede llamarse independientemente de la bandera para diagnóstico.
    La bandera controla únicamente enriquecer_trayectoria_con_promedios().

    Parámetros
    ----------
    ruta_promedios : ruta al archivo Excel.
    anio_ref       : ANIO_ANALISIS (ej. 2026). El año de referencia para cálculos
                     ANT se calcula como min(max_año_datos, anio_ref - 1).
                     Si None, se usa max(ANO) del archivo.
    periodo_ref    : PERIODO_ANALISIS — informativo, no filtra aún.

    Retorna
    -------
    dict con claves: por_codcli, por_rut_codcarr, kpi, auditoria, ruta, anio_ref, periodo_ref.
    None si la carga falla (no bloqueante).
    """
    ruta = Path(ruta_promedios)
    if not ruta.exists():
        log_mu(f"Archivo no encontrado: {ruta}", "warning")
        return None

    # Leer Hoja1
    try:
        df_hoja1 = pd.read_excel(ruta, sheet_name="Hoja1", dtype=str)
    except Exception as exc:
        log_mu(f"Error leyendo Hoja1 de {ruta.name}: {exc}", "warning")
        return None

    # Leer DatosAlumnos (opcional — para NIV_ACA prioritario)
    df_da: Optional[pd.DataFrame] = None
    try:
        df_da = pd.read_excel(ruta, sheet_name="DatosAlumnos", dtype=str)
        log_mu(f"DatosAlumnos cargado: {len(df_da)} filas", "info")
    except Exception as exc:
        log_mu(f"DatosAlumnos no disponible (NIV_ACA usará fallback Hoja1): {exc}", "info")

    try:
        ctx = calcular_metricas_promedios_hoja1(
            df_hoja1=df_hoja1,
            df_datos_alumnos=df_da,
            anio_ref=anio_ref,
        )
    except Exception as exc:
        log_mu(f"Error en cálculo de métricas (no bloqueante): {exc}", "warning")
        return None

    ctx["ruta"] = str(ruta)
    ctx["anio_ref"] = anio_ref
    ctx["periodo_ref"] = periodo_ref
    return ctx


def calcular_metricas_promedios_hoja1(
    df_hoja1: pd.DataFrame,
    df_datos_alumnos: Optional[pd.DataFrame] = None,
    anio_ref: Optional[int] = None,
) -> dict:
    """
    Calcula métricas académicas desde Hoja1 (y opcionalmente DatosAlumnos).

    Lógica adaptada de _build_mu_historico_summary() en avance_curricular/codigo_gobernanza_v2.py.

    Retorna
    -------
    dict con claves:
        por_codcli      : DataFrame — métricas por CODCLI (llave primaria)
        por_rut_codcarr : DataFrame — métricas por (RUT, CODCARR) (llave alternativa)
        kpi             : DataFrame — KPIs agregados del universo
        auditoria       : dict — metadatos de columnas, cobertura y año de referencia
    """
    audit: dict = {}

    # ── Validar columnas mínimas ─────────────────────────────────────────────
    presentes = set(df_hoja1.columns)
    faltantes_min = _COLS_HOJA1_MIN - presentes
    if faltantes_min:
        raise ValueError(f"Hoja1 no tiene columnas mínimas: {faltantes_min}")

    audit["columnas_hoja1_presentes"]  = sorted(presentes)
    audit["columnas_opc_disponibles"]  = sorted(_COLS_HOJA1_OPC & presentes)
    audit["columnas_opc_faltantes"]    = sorted(_COLS_HOJA1_OPC - presentes)

    # ── Normalizar columnas clave ────────────────────────────────────────────
    df = df_hoja1.copy()
    df["CODCLI"]     = normalizar_codcli(df["CODCLI"])
    df["_ANO_NUM"]   = pd.to_numeric(df["ANO"], errors="coerce")
    df["_PER_NUM"]   = pd.to_numeric(df["PERIODO"], errors="coerce")

    # Clave alternativa RUT+CODCARR (si disponibles)
    _tiene_rut_codcarr = {"RUT", "CODCARR"}.issubset(presentes)
    if _tiene_rut_codcarr:
        df["_RUT_KEY"]    = df["RUT"].fillna("").astype(str).str.strip()
        df["_CODCARR_KEY"]= df["CODCARR"].fillna("").astype(str).str.strip().str.upper()

    # ── Año de referencia para cálculos ANT ─────────────────────────────────
    anios_datos = df["_ANO_NUM"].dropna()
    anio_max = int(anios_datos.max()) if not anios_datos.empty else None
    if anio_ref is not None and anio_max is not None:
        anio_ref_calc = min(anio_max, anio_ref - 1)
    else:
        anio_ref_calc = anio_max

    anios_lista = sorted({int(v) for v in anios_datos.dropna().unique()})
    audit["anio_max_datos"]     = anio_max
    audit["anio_ref_calculo"]   = anio_ref_calc
    audit["anios_en_datos"]     = anios_lista
    audit["alcance_historico"]  = "MULTIANUAL" if len(anios_lista) > 1 else "ANIO_UNICO"
    if audit["alcance_historico"] == "ANIO_UNICO":
        audit["cautela_historico"] = (
            "ASI_INS_HIS y ASI_APR_HIS calculados con solo un año disponible. "
            "No representan histórico multianual completo."
        )

    # ── Máscaras de estado (vectorizadas) ───────────────────────────────────
    if "DESCRIPCION_ESTADO" in df.columns:
        _desc = df["DESCRIPCION_ESTADO"].fillna("").astype(str).str.upper()
    elif "ESTADO" in df.columns:
        _desc = df["ESTADO"].fillna("").astype(str).str.upper()
    else:
        _desc = pd.Series("", index=df.index, dtype=str)

    _conv = (
        df["CONVALIDADO"].fillna("").astype(str).str.strip().str.upper()
        if "CONVALIDADO" in df.columns
        else pd.Series("", index=df.index, dtype=str)
    )
    _nota_raw = (
        pd.to_numeric(df["NOTA_FINAL"], errors="coerce")
        if "NOTA_FINAL" in df.columns
        else pd.Series(pd.NA, index=df.index, dtype="float64")
    )

    df["_IS_TRANSFER"]  = _desc.str.contains(_PAT_TRANSFER.pattern, regex=True, na=False) | _conv.eq("S")
    df["_IS_APROB"]     = _desc.str.contains(_PAT_APROB.pattern, regex=True, na=False)
    df["_IS_APROB_HIS"] = _desc.str.contains(_PAT_APROB_HIS.pattern, regex=True, na=False)
    df["_NOTA_NUM"]     = _nota_raw

    # ── Subconjunto del año de referencia ───────────────────────────────────
    df_ref = df[df["_ANO_NUM"] == anio_ref_calc].copy() if anio_ref_calc is not None else pd.DataFrame(columns=df.columns)
    audit["filas_hoja1_total"]  = len(df)
    audit["filas_anio_ref"]     = len(df_ref)

    # ── Universo CODCLI presentes en Hoja1 ──────────────────────────────────
    all_codcli = df["CODCLI"][df["CODCLI"].ne("")].dropna().unique()
    por_codcli = pd.DataFrame({"CODCLI": all_codcli})

    # ── ASI_INS_ANT: distinct CODRAMO año de ref, no transfer ───────────────
    _m_ins_ref = ~df_ref["_IS_TRANSFER"] & df_ref["CODRAMO"].notna()
    _s = (df_ref[_m_ins_ref]
          .groupby("CODCLI")["CODRAMO"]
          .nunique()
          .rename("ASI_INS_ANT")
          .reset_index())
    por_codcli = por_codcli.merge(_s, on="CODCLI", how="left")

    # ── ASI_APR_ANT: distinct CODRAMO año de ref, aprobado, no transfer ─────
    _m_apr_ref = df_ref["_IS_APROB"] & ~df_ref["_IS_TRANSFER"] & df_ref["CODRAMO"].notna()
    _s = (df_ref[_m_apr_ref]
          .groupby("CODCLI")["CODRAMO"]
          .nunique()
          .rename("ASI_APR_ANT")
          .reset_index())
    por_codcli = por_codcli.merge(_s, on="CODCLI", how="left")

    # ── ASI_INS_HIS: total registros CODRAMO no nulos, histórico completo ───
    _s = (df[df["CODRAMO"].notna()]
          .groupby("CODCLI")["CODRAMO"]
          .count()          # count() — no distinct; coincide con avance_curricular L745
          .rename("ASI_INS_HIS")
          .reset_index())
    por_codcli = por_codcli.merge(_s, on="CODCLI", how="left")

    # ── ASI_APR_HIS: distinct CODRAMO aprobados/homologados, histórico ──────
    _m_apr_his = df["_IS_APROB_HIS"] & df["CODRAMO"].notna()
    _s = (df[_m_apr_his]
          .groupby("CODCLI")["CODRAMO"]
          .nunique()
          .rename("ASI_APR_HIS")
          .reset_index())
    por_codcli = por_codcli.merge(_s, on="CODCLI", how="left")

    # ── PROM_PRI_SEM: promedio año de ref, PERIODO=1, no transfer, nota válida
    _m_nota_ref = ~df_ref["_IS_TRANSFER"] & df_ref["_NOTA_NUM"].notna()
    _s = (df_ref[_m_nota_ref & (df_ref["_PER_NUM"] == 1)]
          .groupby("CODCLI")["_NOTA_NUM"]
          .mean()
          .rename("PROM_PRI_SEM")
          .reset_index())
    por_codcli = por_codcli.merge(_s, on="CODCLI", how="left")

    # ── PROM_SEG_SEM: promedio año de ref, PERIODO in {2,3}, no transfer ────
    _s = (df_ref[_m_nota_ref & df_ref["_PER_NUM"].isin(_PERIODOS_SEM2)]
          .groupby("CODCLI")["_NOTA_NUM"]
          .mean()
          .rename("PROM_SEG_SEM")
          .reset_index())
    por_codcli = por_codcli.merge(_s, on="CODCLI", how="left")

    # Rellenar enteros con cero donde no hay dato
    for col in ["ASI_INS_ANT", "ASI_APR_ANT", "ASI_INS_HIS", "ASI_APR_HIS"]:
        por_codcli[col] = por_codcli[col].fillna(0).astype(int)

    # ── NIV_ACA — cascada DA_NIVEL > HOJA1_NIVEL ────────────────────────────
    niv_da_df = pd.DataFrame(columns=["CODCLI", "_NIV_DA"])
    if df_datos_alumnos is not None and _COLS_DA_MIN.issubset(set(df_datos_alumnos.columns)):
        _da = df_datos_alumnos.copy()
        _da["CODCLI"] = normalizar_codcli(_da["CODCLI"])
        niv_da_df = (
            _da[_da["NIVEL"].notna() & _da["CODCLI"].ne("")]
            .groupby("CODCLI")["NIVEL"]
            .first()
            .rename("_NIV_DA")
            .reset_index()
        )
        audit["niv_da_disponible"]   = True
        audit["codcli_con_nivel_da"] = len(niv_da_df)
    else:
        audit["niv_da_disponible"] = False

    niv_h1_df = pd.DataFrame(columns=["CODCLI", "_NIV_H1"])
    if "NIVEL" in df.columns:
        niv_h1_df = (
            df[df["NIVEL"].notna() & df["CODCLI"].ne("")]
            .groupby("CODCLI")["NIVEL"]
            .last()
            .rename("_NIV_H1")
            .reset_index()
        )
        audit["niv_hoja1_disponible"] = True
    else:
        audit["niv_hoja1_disponible"] = False

    por_codcli = por_codcli.merge(niv_da_df,  on="CODCLI", how="left")
    por_codcli = por_codcli.merge(niv_h1_df,  on="CODCLI", how="left")

    por_codcli["_AC_NIV_ACA"] = por_codcli["_NIV_DA"].combine_first(por_codcli["_NIV_H1"])
    por_codcli["_AC_NIV_ACA_FUENTE"] = np.where(
        por_codcli["_NIV_DA"].notna(), "DA_NIVEL",
        np.where(por_codcli["_NIV_H1"].notna(), "HOJA1_NIVEL", "SIN_NIVEL"),
    )
    por_codcli.drop(columns=["_NIV_DA", "_NIV_H1"], errors="ignore", inplace=True)

    # Renombrar métricas con prefijo _AC_
    por_codcli.rename(columns={
        "ASI_INS_ANT":  "_AC_ASI_INS_ANT",
        "ASI_APR_ANT":  "_AC_ASI_APR_ANT",
        "ASI_INS_HIS":  "_AC_ASI_INS_HIS",
        "ASI_APR_HIS":  "_AC_ASI_APR_HIS",
        "PROM_PRI_SEM": "_AC_PROM_PRI_SEM",
        "PROM_SEG_SEM": "_AC_PROM_SEG_SEM",
    }, inplace=True)

    # ── Clave alternativa: RUT + CODCARR ────────────────────────────────────
    por_rut_codcarr = pd.DataFrame()
    if _tiene_rut_codcarr:
        _grp = ["_RUT_KEY", "_CODCARR_KEY"]

        _m_ins_rc  = ~df_ref["_IS_TRANSFER"] & df_ref["CODRAMO"].notna()
        _m_apr_rc  = df_ref["_IS_APROB"] & ~df_ref["_IS_TRANSFER"] & df_ref["CODRAMO"].notna()
        _m_his_rc  = df["CODRAMO"].notna()
        _m_ahis_rc = df["_IS_APROB_HIS"] & df["CODRAMO"].notna()
        _m_nota_rc = ~df_ref["_IS_TRANSFER"] & df_ref["_NOTA_NUM"].notna()

        rc_parts = [
            df_ref[_m_ins_rc ].groupby(_grp)["CODRAMO"].nunique().rename("_AC_ASI_INS_ANT"),
            df_ref[_m_apr_rc ].groupby(_grp)["CODRAMO"].nunique().rename("_AC_ASI_APR_ANT"),
            df[_m_his_rc     ].groupby(_grp)["CODRAMO"].count()  .rename("_AC_ASI_INS_HIS"),
            df[_m_ahis_rc    ].groupby(_grp)["CODRAMO"].nunique().rename("_AC_ASI_APR_HIS"),
            df_ref[_m_nota_rc & (df_ref["_PER_NUM"] == 1)       ].groupby(_grp)["_NOTA_NUM"].mean().rename("_AC_PROM_PRI_SEM"),
            df_ref[_m_nota_rc & df_ref["_PER_NUM"].isin(_PERIODOS_SEM2)].groupby(_grp)["_NOTA_NUM"].mean().rename("_AC_PROM_SEG_SEM"),
        ]
        por_rut_codcarr = pd.concat(rc_parts, axis=1).reset_index()
        for col in ["_AC_ASI_INS_ANT", "_AC_ASI_APR_ANT", "_AC_ASI_INS_HIS", "_AC_ASI_APR_HIS"]:
            if col in por_rut_codcarr.columns:
                por_rut_codcarr[col] = por_rut_codcarr[col].fillna(0).astype(int)

    audit["por_codcli_filas"]      = len(por_codcli)
    audit["por_rut_codcarr_filas"] = len(por_rut_codcarr) if not por_rut_codcarr.empty else 0

    # ── KPIs agregados ───────────────────────────────────────────────────────
    kpi_rows: list[dict] = []
    int_cols  = ["_AC_ASI_INS_ANT", "_AC_ASI_APR_ANT", "_AC_ASI_INS_HIS", "_AC_ASI_APR_HIS"]
    float_cols = ["_AC_PROM_PRI_SEM", "_AC_PROM_SEG_SEM"]

    for col in int_cols:
        if col in por_codcli.columns:
            kpi_rows.append({
                "METRICA":         col,
                "MEDIA":           round(float(por_codcli[col].mean()), 2),
                "MEDIANA":         round(float(por_codcli[col].median()), 2),
                "MAX":             int(por_codcli[col].max()),
                "CODCLI_CON_DATO": int((por_codcli[col] > 0).sum()),
                "TOTAL_CODCLI":    len(por_codcli),
            })
    for col in float_cols:
        if col in por_codcli.columns:
            s = por_codcli[col].dropna()
            kpi_rows.append({
                "METRICA":         col,
                "MEDIA":           round(float(s.mean()), 4)   if len(s) else float("nan"),
                "MEDIANA":         round(float(s.median()), 4) if len(s) else float("nan"),
                "MAX":             round(float(s.max()), 4)    if len(s) else float("nan"),
                "CODCLI_CON_DATO": int(s.notna().sum()),
                "TOTAL_CODCLI":    len(por_codcli),
            })
    kpi_rows.append({
        "METRICA":         "_AC_NIV_ACA",
        "MEDIA":           float("nan"),
        "MEDIANA":         float("nan"),
        "MAX":             float("nan"),
        "CODCLI_CON_DATO": int(por_codcli["_AC_NIV_ACA"].notna().sum()),
        "TOTAL_CODCLI":    len(por_codcli),
    })
    kpi = pd.DataFrame(kpi_rows)

    log_mu(
        f"Cálculo completado | CODCLI={len(por_codcli)} | "
        f"RUT+CODCARR={audit['por_rut_codcarr_filas']} | "
        f"anio_ref_calc={anio_ref_calc} | "
        f"alcance={audit['alcance_historico']}",
        "info",
    )

    return {
        "por_codcli":       por_codcli,
        "por_rut_codcarr":  por_rut_codcarr,
        "kpi":              kpi,
        "auditoria":        audit,
    }


def enriquecer_trayectoria_con_promedios(
    df_tray: pd.DataFrame,
    ctx_promedios: Optional[dict],
    force: bool = False,
) -> pd.DataFrame:
    """
    Enriquece df_tray con métricas académicas calculadas desde PROMEDIOS.

    Join primario por CODCLI; fallback por RUT+CODCARR si disponible.
    Agrega columnas con prefijo _AC_ sin modificar columnas existentes.
    No bloqueante: retorna df_tray sin cambios ante cualquier falla.
    Solo ejecuta lógica si ACTIVAR_INTEGRACION_AVANCE_CURRICULAR = True
    o si se pasa force=True (FASE 22B: hook sectorizado permanente).
    """
    if not force and not esta_activa():
        return df_tray

    if ctx_promedios is None:
        log_mu("ctx_promedios es None — enriquecimiento omitido.", "info")
        return df_tray

    if not isinstance(df_tray, pd.DataFrame) or df_tray.empty:
        log_mu("df_tray vacío o no es DataFrame — enriquecimiento omitido.", "info")
        return df_tray

    try:
        por_codcli:      pd.DataFrame = ctx_promedios.get("por_codcli",      pd.DataFrame())
        por_rut_codcarr: pd.DataFrame = ctx_promedios.get("por_rut_codcarr", pd.DataFrame())
        cols_ac = [c for c in por_codcli.columns if c.startswith("_AC_")]

        col_codcli_tray = _detectar_col(df_tray, ["CODCLI", "codcli", "COD_CLI"])

        # ── Join primario: CODCLI ────────────────────────────────────────────
        if col_codcli_tray and not por_codcli.empty and cols_ac:
            slim = por_codcli[["CODCLI"] + cols_ac].drop_duplicates("CODCLI").copy()
            slim.rename(columns={"CODCLI": "_AC_JOIN_KEY"}, inplace=True)
            df_out = df_tray.copy()
            df_out["_AC_JOIN_KEY"] = normalizar_codcli(df_out[col_codcli_tray])
            df_out = df_out.merge(slim, on="_AC_JOIN_KEY", how="left")
            df_out.drop(columns=["_AC_JOIN_KEY"], inplace=True)
            n = df_out[cols_ac[0]].notna().sum() if cols_ac else 0
            log_mu(f"Join CODCLI completado | enriquecidas={n}/{len(df_out)} | cols={cols_ac}", "info")
            return df_out

        # ── Fallback: RUT + CODCARR ──────────────────────────────────────────
        col_rut    = _detectar_col(df_tray, ["RUT", "N_DOC", "rut"])
        col_codcarr = _detectar_col(df_tray, ["CODCARR", "CODCARPR", "COD_CAR"])
        rc_cols_ac  = [c for c in por_rut_codcarr.columns if c.startswith("_AC_")]

        if col_rut and col_codcarr and not por_rut_codcarr.empty and rc_cols_ac:
            slim_rc = por_rut_codcarr[["_RUT_KEY", "_CODCARR_KEY"] + rc_cols_ac].copy()
            df_out = df_tray.copy()
            df_out["_AC_RUT_KEY"]    = df_out[col_rut].fillna("").astype(str).str.strip()
            df_out["_AC_CODCARR_KEY"]= df_out[col_codcarr].fillna("").astype(str).str.strip().str.upper()
            slim_rc = slim_rc.rename(columns={"_RUT_KEY": "_AC_RUT_KEY", "_CODCARR_KEY": "_AC_CODCARR_KEY"})
            df_out = df_out.merge(slim_rc, on=["_AC_RUT_KEY", "_AC_CODCARR_KEY"], how="left")
            df_out.drop(columns=["_AC_RUT_KEY", "_AC_CODCARR_KEY"], inplace=True)
            n = df_out[rc_cols_ac[0]].notna().sum() if rc_cols_ac else 0
            log_mu(f"Join RUT+CODCARR (fallback) | enriquecidas={n}/{len(df_out)}", "info")
            return df_out

        log_mu("No se encontró llave de join válida — df_tray sin cambios.", "warning")
        return df_tray

    except Exception as exc:
        log_mu(f"Error en enriquecimiento (no bloqueante): {exc}", "warning")
        return df_tray


# ──────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────────────────────

def _detectar_col(df: pd.DataFrame, candidatos: list[str]) -> Optional[str]:
    """Retorna el primer nombre de columna encontrado en df, o None."""
    for c in candidatos:
        if c in df.columns:
            return c
    return None


# ──────────────────────────────────────────────────────────────────────────────
# LEGADO — funciones de la versión CSV MU posicional (descartada como fuente)
# Mantenidas para compatibilidad con el hook existente en caracterizacion.py.
# El hook no ejecuta nada porque la bandera está en False.
# ──────────────────────────────────────────────────────────────────────────────

def cargar_contexto_mu(
    ruta_csv=None,
    anio: Optional[int] = None,
    periodo: Optional[int] = None,
) -> Optional[dict]:
    """LEGADO: fuente CSV MU posicional descartada. Retorna None sin hacer nada."""
    log_mu(
        "cargar_contexto_mu() es función legado — fuente CSV MU descartada. "
        "Usar cargar_promedios_contexto() con ruta al PROMEDIOSDEALUMNOS_7804.xlsx.",
        "debug",
    )
    return None


def enriquecer_trayectoria_con_mu(
    df_tray: pd.DataFrame,
    ctx_mu: Optional[dict],
) -> pd.DataFrame:
    """LEGADO: retorna df_tray sin modificaciones."""
    return df_tray
