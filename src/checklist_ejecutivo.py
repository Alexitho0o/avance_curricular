"""
checklist_ejecutivo.py
======================
Genera el resumen ejecutivo impreso en terminal al finalizar el pipeline
de Matrícula Unificada 2026 Pregrado.

Todas las métricas se calculan desde los DataFrames internos del pipeline
o desde los archivos finales generados. No modifica datos ni genera commits.

Uso desde el pipeline
---------------------
    from src.checklist_ejecutivo import imprimir_checklist_ejecutivo_mu2026

    imprimir_checklist_ejecutivo_mu2026(
        df_mu32       = matricula_unificada_32,   # 32 cols PES, antes de CSV
        df_subida     = archivo_subida,           # 210 cols con CODCLI
        pes_ready_path= pes_ready_path,           # resultados/..._PES_READY.csv
        desktop_path  = desktop_path,             # /Users/alexi/Desktop/...
        output_dir    = output_dir,               # resultados/
        report        = _report,                  # dict del pipeline
    )
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


# ── Columnas PES (orden exacto en el CSV sin cabecera) ─────────────────────
_PES_COLS = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO",
    "NOMBRE", "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC",
    "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION",
    "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI",
    "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",
    "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]
_N_PES_COLS = len(_PES_COLS)  # 32

# ── Símbolos de estado ──────────────────────────────────────────────────────
_OK = "OK      "
_REV = "REVISAR "
_CRIT = "CRÍTICO "

_NA = "NO DISPONIBLE"


def _ico(ok: bool | None, critical: bool = False) -> str:
    if ok is None:
        return f"  {_REV}·"
    if ok:
        return f"  {_OK}·"
    return f"  {_CRIT}·" if critical else f"  {_REV}·"


def _pct(num: int | float, denom: int | float) -> str:
    if not denom:
        return "0,0%"
    return f"{num / denom * 100:.1f}%".replace(".", ",")


def _n(v: Any) -> str:
    """Formatea un entero con separador de miles (punto)."""
    try:
        return f"{int(v):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(v)


# ───────────────────────────────────────────────────────────────────────────
def _get_inner(report: dict[str, Any]) -> dict[str, Any]:
    """Soporta estructura flat (pipeline en caliente) y anidada (JSON guardado)."""
    wrapper = report.get("matricula_unificada_fallback_report")
    return wrapper if isinstance(wrapper, dict) else report


# ───────────────────────────────────────────────────────────────────────────
def imprimir_checklist_ejecutivo_mu2026(
    df_mu32: pd.DataFrame,
    df_subida: pd.DataFrame,
    pes_ready_path: Path,
    desktop_path: Path,
    output_dir: Path,
    report: dict[str, Any],
) -> None:
    """Imprime el checklist ejecutivo en terminal y guarda CSV de carreras.

    Parámetros
    ----------
    df_mu32 : DataFrame con las 32 columnas PES (universo final exportado)
    df_subida : DataFrame interno completo (210 cols, incluye CODCLI, NOMBRE_CARRERA_TSV)
    pes_ready_path : ruta al CSV PES_READY generado
    desktop_path : ruta a la copia de Escritorio
    output_dir : directorio resultados/
    report : dict retornado por ejecutar_pipeline_matricula_unificada_legacy_like
    """
    try:
        _ejecutar(df_mu32, df_subida, pes_ready_path, desktop_path, output_dir, report)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"\n  ⚠️  Checklist ejecutivo: error inesperado ({exc}). Pipeline no afectado.")


# ───────────────────────────────────────────────────────────────────────────
def _ejecutar(
    df_mu32: pd.DataFrame,
    df_subida: pd.DataFrame,
    pes_ready_path: Path,
    desktop_path: Path,
    output_dir: Path,
    report: dict[str, Any],
) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sep = "=" * 62

    # ── Navegar reporte (flat desde pipeline o anidado desde JSON) ─────────
    inner = _get_inner(report)

    # ── Validación estructural con csv.reader ─────────────────────────────
    pes_rows_raw: list[list[str]] = []
    pes_read_ok = False
    if pes_ready_path.exists():
        try:
            with pes_ready_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
                for row in csv.reader(f, delimiter=";"):
                    pes_rows_raw.append(row)
            pes_read_ok = True
        except Exception:
            pass

    bad_fields = sum(1 for r in pes_rows_raw if len(r) != _N_PES_COLS)
    _HEADER_TOKENS = {"TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO"}
    has_header = bool(pes_rows_raw and _HEADER_TOKENS & set(pes_rows_raw[0]))

    # ── Cargar PES_READY como DataFrame — fuente principal de métricas ─────
    df_pes: pd.DataFrame = pd.DataFrame(columns=_PES_COLS)
    if pes_ready_path.exists() and pes_read_ok:
        try:
            df_pes = pd.read_csv(
                pes_ready_path,
                sep=";",
                header=None,
                names=_PES_COLS,
                dtype=str,
                keep_default_na=False,
                encoding="utf-8-sig",
            )
        except Exception:
            pass

    total_pes = len(df_pes)

    # ── Métricas básicas desde df_pes ─────────────────────────────────────
    if total_pes > 0:
        vig_s = df_pes["VIG"].str.strip()
        ndoc_s = df_pes["N_DOC"].str.strip()
        anio_act_s = df_pes["ANIO_ING_ACT"].str.strip()
        anio_ori_s = df_pes["ANIO_ING_ORI"].str.strip()
        nuevo_mask = anio_act_s == anio_ori_s
    else:
        vig_s = ndoc_s = anio_act_s = anio_ori_s = pd.Series(dtype=str)
        nuevo_mask = pd.Series(dtype=bool)

    vig1 = int((vig_s == "1").sum())
    vig0 = int((vig_s == "0").sum())
    vig2 = int((vig_s == "2").sum())
    rut_unicos = ndoc_s.nunique()
    rut_dup = total_pes - rut_unicos

    nuevos_vig = int((nuevo_mask & (vig_s == "1")).sum())
    antiguos_vig = int((~nuevo_mask & (vig_s == "1")).sum())
    nuevos_all = int(nuevo_mask.sum())
    antiguos_all = int((~nuevo_mask).sum())

    # ── Exclusiones PES_READY — cadena de fallback desde reporte ──────────
    pes_rpt = inner.get("pes_ready_report", {}) or {}
    ev = pes_rpt.get("exclusion_verification", {}) or {}

    # Preferencia 1: exclusion_verification.rows_excluded
    # Preferencia 2: pes_ready_report.rows_excluded (clave directa)
    # Preferencia 3: rows_bruto - rows_pes_ready
    # Preferencia 4: _NA
    _ev_excl = ev.get("rows_excluded")
    if _ev_excl is not None:
        exc_total: Any = int(_ev_excl)
    else:
        _direct = pes_rpt.get("rows_excluded")
        if _direct is not None:
            exc_total = int(_direct)
        else:
            _bruto = pes_rpt.get("rows_bruto") or pes_rpt.get("rows_initial")
            _final = pes_rpt.get("rows_pes_ready") or pes_rpt.get("rows_final")
            exc_total = (int(_bruto) - int(_final)) if (_bruto is not None and _final is not None) else _NA

    # Excluidos sin trazabilidad
    _ev_st = ev.get("excluded_without_trace_count")
    if _ev_st is not None:
        exc_sin_traza: Any = int(_ev_st)
    else:
        _wt = (
            pes_rpt.get("without_trace")
            or pes_rpt.get("rows_excluded_without_trace")
            or pes_rpt.get("excluded_without_trace_count")
        )
        exc_sin_traza = int(_wt) if _wt is not None else _NA

    exc_razones: dict[str, int] = ev.get("reason_counts") or pes_rpt.get("reason_counts") or {}

    # ── CODCLI — universo interno (no existe en PES_READY) ────────────────
    codcli_col_exists = "CODCLI" in df_subida.columns
    if codcli_col_exists:
        _ccs = df_subida["CODCLI"].astype(str).str.strip()
        codcli_total = len(_ccs)
        codcli_unicos = _ccs.nunique()
        codcli_fuente_nota = ""
    else:
        codcli_total = codcli_unicos = 0
        codcli_fuente_nota = "(CODCLI no disponible en DataFrame interno)"

    # CODCLI únicos en carga final: N_DOC(PES_READY) ∩ df_subida
    codcli_final_unicos: Any = _NA
    if codcli_col_exists and "N_DOC" in df_subida.columns and total_pes > 0:
        try:
            _pes_ndoc = set(ndoc_s)
            _mask = df_subida["N_DOC"].astype(str).str.strip().isin(_pes_ndoc)
            codcli_final_unicos = int(
                df_subida.loc[_mask, "CODCLI"].astype(str).str.strip().nunique()
            )
        except Exception:
            pass

    vig0_ctrl = inner.get("control_vigencia_0_codcli", {}) or {}
    ctrl_codcli_count = vig0_ctrl.get("codcli_control_total", _NA)
    ctrl_found = vig0_ctrl.get("codcli_encontrados_salida_final", _NA)
    ctrl_not_found = vig0_ctrl.get("codcli_no_encontrados", _NA)
    ctrl_rows_affected = vig0_ctrl.get("filas_afectadas", _NA)
    ctrl_altered_outside = vig0_ctrl.get("codcli_fuera_control_alterados_por_regla", _NA)

    depur = inner.get("depuracion_rut_multi_codcli", {}) or {}
    depur_codcli_exc = depur.get("codcli_excluidos", _NA) if depur else _NA
    depur_filas_exc = depur.get("filas_excluidas", _NA) if depur else _NA

    # ── Mapa COD_CAR → nombre (solo enriquecimiento) ──────────────────────
    nombre_car_map: dict[str, str] = {}
    if "COD_CAR" in df_subida.columns and "NOMBRE_CARRERA_TSV" in df_subida.columns:
        _lk = (
            df_subida[["COD_CAR", "NOMBRE_CARRERA_TSV"]]
            .dropna(subset=["NOMBRE_CARRERA_TSV"])
            .astype(str)
        )
        for _, _row in _lk.drop_duplicates("COD_CAR").iterrows():
            _k = _row["COD_CAR"].strip()
            _v = _row["NOMBRE_CARRERA_TSV"].strip()
            if _k and _v and _v.lower() != "nan":
                nombre_car_map[_k] = _v

    # ── Tablas carreras y sedes — 100% desde df_pes ───────────────────────
    carrera_rows = _build_carrera_table_from_pes(df_pes, nombre_car_map)
    sede_rows = _build_sede_table_from_pes(df_pes)
    total_car_sum = sum(r["total"] for r in carrera_rows)
    total_sed_sum = sum(r["total"] for r in sede_rows)

    # ── Guardar CSV completo de carreras ──────────────────────────────────
    carreras_csv_path: Any = output_dir / f"checklist_terminal_carreras_mu2026_{ts}.csv"
    try:
        _save_carreras_csv(carrera_rows, carreras_csv_path)
    except Exception:
        carreras_csv_path = None

    # ── Validaciones ──────────────────────────────────────────────────────
    val_pes_ok = pes_ready_path.exists()
    val_desktop_ok = desktop_path.exists()
    val_32_ok = bad_fields == 0 and pes_read_ok and total_pes > 0
    val_no_header = not has_header and pes_read_ok
    val_sin_traza = (exc_sin_traza == 0) if isinstance(exc_sin_traza, int) else None
    val_ctrl_nf = (ctrl_not_found == 0) if isinstance(ctrl_not_found, int) else None
    val_ctrl_outside = (ctrl_altered_outside == 0) if isinstance(ctrl_altered_outside, int) else None
    val_rut_dup = rut_dup == 0

    _CAMPOS_CRIT = ["TIPO_DOC", "N_DOC", "DV", "COD_SED", "COD_CAR", "VIG", "FOR_ING_ACT", "SEXO"]
    vacios_crit: list[str] = []
    if total_pes > 0:
        for cc in _CAMPOS_CRIT:
            if cc in df_pes.columns:
                n_vac = int((df_pes[cc].str.strip() == "").sum())
                if n_vac > 0:
                    vacios_crit.append(f"{cc}={_n(n_vac)}")
    val_campos_criticos = (len(vacios_crit) == 0) if total_pes > 0 else None

    # ════════════════════════════════════════════════════════════════════
    # IMPRIMIR CHECKLIST
    # ════════════════════════════════════════════════════════════════════
    print(f"\n{sep}")
    print("  CHECKLIST EJECUTIVO MU2026")
    print(sep)

    # ── [ARCHIVOS] ───────────────────────────────────────────────────────
    print("\n[ARCHIVOS]")
    _info("PES_READY", val_pes_ok,
          f"{_n(total_pes)} filas · {_N_PES_COLS} campos · "
          f"{'sin encabezado' if not has_header else '⚠️ TIENE ENCABEZADO'}",
          f"{pes_ready_path}")
    _info("Escritorio", val_desktop_ok, str(desktop_path))
    if bad_fields > 0:
        print(f"  ⚠️  {_n(bad_fields)} filas con campos ≠ {_N_PES_COLS}")

    # ── [CARGA PES_READY] ────────────────────────────────────────────────
    print("\n[CARGA PES_READY]")
    print(f"  Registros a cargar (PES_READY):  {_n(total_pes)}")
    print(f"  RUT únicos a cargar:             {_n(rut_unicos)}")
    if rut_dup > 0:
        print(f"  ⚠️  RUT duplicados en PES_READY: {_n(rut_dup)}")
    print(f"  VIG = 1 (vigentes):              {_n(vig1)}  ({_pct(vig1, total_pes)})")
    print(f"  VIG = 0 (no vigentes):           {_n(vig0)}  ({_pct(vig0, total_pes)})")
    if vig2 > 0:
        print(f"  VIG = 2 (egresados):             {_n(vig2)}  ({_pct(vig2, total_pes)})")
    print(f"  Excluidos PES_READY:             {_n(exc_total)}")
    if isinstance(exc_razones, dict) and exc_razones:
        for motivo, n_exc in sorted(exc_razones.items(), key=lambda x: -x[1]):
            print(f"    → {motivo}: {_n(n_exc)}")
    print(f"  Excluidos sin trazabilidad:      {_n(exc_sin_traza)}")

    # ── [CODCLI] ─────────────────────────────────────────────────────────
    print("\n[CODCLI]")
    if codcli_fuente_nota:
        print(f"  ℹ️  {codcli_fuente_nota}")
    print(f"  CODCLI procesados (universo):    {_n(codcli_total) if codcli_col_exists else _NA}")
    print(f"  CODCLI únicos (universo):        {_n(codcli_unicos) if codcli_col_exists else _NA}")
    print(f"  CODCLI únicos en carga final:    {_n(codcli_final_unicos)}")
    print(f"  CODCLI excluidos (multi-CODCLI): {_n(depur_codcli_exc)}")
    print(f"  Filas excluidas (multi-CODCLI):  {_n(depur_filas_exc)}")
    print(f"  CODCLI en control VIG=0:         {_n(ctrl_codcli_count)}")
    print(f"  CODCLI encontrados (VIG=0):      {_n(ctrl_found)}")
    print(f"  CODCLI no encontrados (VIG=0):   {_n(ctrl_not_found)}")
    print(f"  Filas afectadas VIG=0:           {_n(ctrl_rows_affected)}")
    if isinstance(ctrl_altered_outside, int) and ctrl_altered_outside > 0:
        print(f"  ⚠️  CODCLI fuera de control alterados: {_n(ctrl_altered_outside)}")
    else:
        _alt_str = _n(ctrl_altered_outside) if isinstance(ctrl_altered_outside, int) else "0"
        print(f"  CODCLI fuera de control alterados: {_alt_str}")

    # ── [NUEVOS / ANTIGUOS] ──────────────────────────────────────────────
    print("\n[NUEVOS / ANTIGUOS]")
    print(f"  Definición → Nuevo: ANIO_ING_ACT = ANIO_ING_ORI")
    print(f"  Nuevos vigentes (VIG=1):              {_n(nuevos_vig)}  ({_pct(nuevos_vig, vig1)})")
    print(f"  Antiguos/Reingresantes vigentes:      {_n(antiguos_vig)}  ({_pct(antiguos_vig, vig1)})")
    print(f"  Nuevos total (incl. VIG=0):           {_n(nuevos_all)}")
    print(f"  Antiguos/Reingresantes total:         {_n(antiguos_all)}")

    # ── [CARRERAS · TOP 20] ──────────────────────────────────────────────
    print("\n[CARRERAS · TOP 20]")
    if carrera_rows:
        hdr = (
            f"  {'COD_CAR':>8} │ {'Registros':>10} │ {'RUT únicos':>10} │"
            f" {'VIG=1':>7} │ {'VIG=0':>7} │ {'Nuevos':>7} │ {'Antiguos':>8} │"
            f" {'S1':>5} │ {'S2':>5} │ Nombre carrera"
        )
        print(hdr)
        print("  " + "─" * (len(hdr) - 2))
        for row in carrera_rows[:20]:
            nombre = (row["nombre"] or "")[:30]
            print(
                f"  {str(row['cod_car']):>8} │ {_n(row['total']):>10} │"
                f" {_n(row['rut_unicos']):>10} │ {_n(row['vig1']):>7} │"
                f" {_n(row['vig0']):>7} │ {_n(row['nuevos']):>7} │"
                f" {_n(row['antiguos']):>8} │ {_n(row['sem1']):>5} │"
                f" {_n(row['sem2']):>5} │ {nombre}"
            )
        _check = "  ✓" if total_car_sum == total_pes else f"  ⚠️ discrepancia ({_n(total_pes - total_car_sum)} sin clasificar)"
        print(f"\n  Σ total carreras: {_n(total_car_sum)} / PES_READY: {_n(total_pes)}{_check}")
        if carreras_csv_path:
            print(f"  📄 CSV completo ({len(carrera_rows)} carreras): {carreras_csv_path}")
    else:
        print(f"  {_NA}")

    # ── [SEDES] ──────────────────────────────────────────────────────────
    print("\n[SEDES]")
    if sede_rows:
        hdr_s = (
            f"  {'COD_SED':>8} │ {'Registros':>10} │ {'RUT únicos':>10} │"
            f" {'VIG=1':>7} │ {'VIG=0':>7} │ {'Nuevos':>7} │ {'Antiguos':>8} │ Carreras únicas"
        )
        print(hdr_s)
        print("  " + "─" * (len(hdr_s) - 2))
        for row in sede_rows:
            print(
                f"  {str(row['cod_sed']):>8} │ {_n(row['total']):>10} │"
                f" {_n(row['rut_unicos']):>10} │ {_n(row['vig1']):>7} │"
                f" {_n(row['vig0']):>7} │ {_n(row['nuevos']):>7} │"
                f" {_n(row['antiguos']):>8} │ {_n(row['carreras_unicas'])}"
            )
        _check_s = "  ✓" if total_sed_sum == total_pes else f"  ⚠️ discrepancia ({_n(total_pes - total_sed_sum)} sin clasificar)"
        print(f"\n  Σ total sedes: {_n(total_sed_sum)} / PES_READY: {_n(total_pes)}{_check_s}")
    else:
        print(f"  {_NA}")

    # ── [VALIDACIONES] ───────────────────────────────────────────────────
    print("\n[VALIDACIONES]")
    print(_ico(val_pes_ok, critical=True) + " PES_READY existe")
    print(_ico(val_desktop_ok) + " Archivo Escritorio existe")
    print(_ico(val_32_ok, critical=True) + f" {_N_PES_COLS} campos por fila" +
          (f" ({_n(bad_fields)} filas inválidas)" if not val_32_ok and bad_fields > 0 else ""))
    print(_ico(val_no_header, critical=True) + " Sin encabezado en PES_READY")
    print(_ico(val_sin_traza) + f" Excluidos sin trazabilidad = {_n(exc_sin_traza)}")
    print(_ico(val_ctrl_nf, critical=True) +
          f" CODCLI no encontrados en control VIG=0 = {_n(ctrl_not_found)}")
    print(_ico(val_ctrl_outside, critical=True) +
          f" CODCLI fuera de control alterados = {_n(ctrl_altered_outside)}")
    print(_ico(val_rut_dup) + f" RUT duplicados en PES_READY = {_n(rut_dup)}")
    if val_campos_criticos is None:
        print(f"  {_REV}· Campos críticos vacíos: PES_READY no disponible")
    elif not val_campos_criticos:
        print(f"  {_REV}· Campos críticos vacíos: {', '.join(vacios_crit)}")
    else:
        print(f"  {_OK}· Campos críticos vacíos = 0")

    print(f"\n{sep}\n")


# ───────────────────────────────────────────────────────────────────────────
# Helpers internos
# ───────────────────────────────────────────────────────────────────────────

def _info(label: str, ok: bool, *parts: str) -> None:
    icon = "✅" if ok else "❌"
    estado = "OK" if ok else "FALTA"
    text = "  ·  ".join(p for p in parts if p)
    print(f"  {icon} {label:12} [{estado}]  {text}")


def _build_carrera_table_from_pes(
    df_pes: pd.DataFrame,
    nombre_car_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Construye tabla de carreras 100% desde el CSV PES_READY final."""
    if df_pes.empty or "COD_CAR" not in df_pes.columns:
        return []

    vig_s = df_pes["VIG"].str.strip()
    ndoc_s = df_pes["N_DOC"].str.strip()
    sem_s = df_pes["SEM_ING_ACT"].str.strip()
    anio_act_s = df_pes["ANIO_ING_ACT"].str.strip()
    anio_ori_s = df_pes["ANIO_ING_ORI"].str.strip()
    nuevo_mask = anio_act_s == anio_ori_s

    rows: list[dict[str, Any]] = []
    for car_val, grp in df_pes.groupby("COD_CAR", sort=False):
        idx = grp.index
        g_vig = vig_s.loc[idx]
        g_ndoc = ndoc_s.loc[idx]
        g_sem = sem_s.loc[idx]
        g_nuevo = nuevo_mask.loc[idx]
        nombre = nombre_car_map.get(str(car_val).strip(), "")
        rows.append({
            "cod_car": car_val,
            "nombre": nombre,
            "total": len(grp),
            "rut_unicos": g_ndoc.nunique(),
            "codcli_unicos": 0,  # CODCLI no existe en PES_READY
            "vig1": int((g_vig == "1").sum()),
            "vig0": int((g_vig == "0").sum()),
            "nuevos": int(g_nuevo.sum()),
            "antiguos": int((~g_nuevo).sum()),
            "sem1": int((g_sem == "1").sum()),
            "sem2": int((g_sem == "2").sum()),
        })
    rows.sort(key=lambda x: -x["total"])
    return rows


def _build_sede_table_from_pes(df_pes: pd.DataFrame) -> list[dict[str, Any]]:
    """Construye tabla de sedes 100% desde el CSV PES_READY final."""
    if df_pes.empty or "COD_SED" not in df_pes.columns:
        return []

    vig_s = df_pes["VIG"].str.strip()
    ndoc_s = df_pes["N_DOC"].str.strip()
    anio_act_s = df_pes["ANIO_ING_ACT"].str.strip()
    anio_ori_s = df_pes["ANIO_ING_ORI"].str.strip()
    nuevo_mask = anio_act_s == anio_ori_s

    rows: list[dict[str, Any]] = []
    for sed_val, grp in df_pes.groupby("COD_SED", sort=False):
        idx = grp.index
        g_vig = vig_s.loc[idx]
        g_ndoc = ndoc_s.loc[idx]
        g_nuevo = nuevo_mask.loc[idx]
        carreras_unicas = df_pes.loc[idx, "COD_CAR"].nunique() if "COD_CAR" in df_pes.columns else 0
        rows.append({
            "cod_sed": sed_val,
            "total": len(grp),
            "rut_unicos": g_ndoc.nunique(),
            "vig1": int((g_vig == "1").sum()),
            "vig0": int((g_vig == "0").sum()),
            "nuevos": int(g_nuevo.sum()),
            "antiguos": int((~g_nuevo).sum()),
            "carreras_unicas": carreras_unicas,
        })
    rows.sort(key=lambda x: -x["total"])
    return rows


def _save_carreras_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    fieldnames = [
        "cod_car", "nombre", "total", "rut_unicos", "codcli_unicos",
        "vig1", "vig0", "nuevos", "antiguos", "sem1", "sem2",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
