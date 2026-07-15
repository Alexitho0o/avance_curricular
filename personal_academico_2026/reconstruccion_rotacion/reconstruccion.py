"""Panel, clasificacion anual, KPI, reingresos y movilidad."""

from __future__ import annotations

from typing import Sequence

import pandas as pd


def pct(numerator: float, denominator: float) -> float | None:
    """Calcula porcentaje sin redondeo prematuro."""

    if denominator == 0:
        return None
    return (numerator / denominator) * 100


def build_panel(longitudinal: pd.DataFrame, years: Sequence[int]) -> pd.DataFrame:
    """Construye panel de presencia por persona y anio."""

    keys = sorted(longitudinal["CLAVE_DOCUMENTAL"].unique())
    rows: list[dict[str, object]] = []
    for key in keys:
        group = longitudinal[longitudinal["CLAVE_DOCUMENTAL"].eq(key)]
        present = set(group[group["VIGENCIA"].astype(str).eq("1")]["ANIO"].astype(int))
        row: dict[str, object] = {"CLAVE_DOCUMENTAL": key}
        for year in years:
            row[str(year)] = 1 if year in present else 0
        states = [row[str(year)] for year in years]
        present_years = [year for year in years if row[str(year)] == 1]
        first_year = min(present_years) if present_years else None
        last_year = max(present_years) if present_years else None
        gaps = []
        if first_year is not None and last_year is not None:
            gaps = [year for year in range(first_year, last_year + 1) if row.get(str(year), 0) == 0]
        row["PRIMER_ANIO_APARICION"] = first_year
        row["ULTIMO_ANIO_OBSERVADO"] = last_year
        row["PERMANENCIA_CONTINUA"] = int(not gaps)
        row["TUVO_SALIDA"] = int(any(state == 0 for state in states[states.index(1) + 1:]) if 1 in states else 0)
        row["TUVO_REINGRESO"] = int(has_reentry(states))
        row["SALIDA_TEMPORAL"] = row["TUVO_REINGRESO"]
        row["SALIDA_DEFINITIVA_OBSERVADA"] = int(last_year is not None and last_year < max(years))
        rows.append(row)
    return pd.DataFrame(rows)


def has_reentry(states: list[int]) -> bool:
    """Detecta patron presencia-ausencia-presencia."""

    seen_present = False
    seen_gap = False
    for state in states:
        if state == 1 and seen_gap:
            return True
        if state == 1:
            seen_present = True
        if state == 0 and seen_present:
            seen_gap = True
    return False


def pair_detail(longitudinal: pd.DataFrame, year: int, next_year: int) -> pd.DataFrame:
    """Clasifica PERMANECE, ROTA y NUEVO INGRESO por conjuntos."""

    base = longitudinal[(longitudinal["ANIO"].eq(year)) & (longitudinal["VIGENCIA"].astype(str).eq("1"))].copy()
    comp = longitudinal[(longitudinal["ANIO"].eq(next_year)) & (longitudinal["VIGENCIA"].astype(str).eq("1"))].copy()
    base_keys = set(base["CLAVE_DOCUMENTAL"])
    comp_keys = set(comp["CLAVE_DOCUMENTAL"])
    remain = base_keys & comp_keys
    rotate = base_keys - comp_keys
    new = comp_keys - base_keys
    rows = []
    for key in sorted(base_keys | comp_keys):
        state = "PERMANECE" if key in remain else ("ROTA" if key in rotate else "NUEVO INGRESO")
        rows.append(
            {
                "ANIO_BASE": year,
                "ANIO_COMPARACION": next_year,
                "CLAVE_DOCUMENTAL": key,
                "ESTADO_ROTACION": state,
                "PERMANECE": int(state == "PERMANECE"),
                "ROTA": int(state == "ROTA"),
                "NUEVO": int(state == "NUEVO INGRESO"),
            }
        )
    detail = pd.DataFrame(rows)
    base_attrs = base.rename(columns={"ANIO": "ANIO_BASE"})
    detail = detail.merge(base_attrs, on=["ANIO_BASE", "CLAVE_DOCUMENTAL"], how="left")
    return detail


def build_pair_outputs(longitudinal: pd.DataFrame, years: Sequence[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula detalle y KPI por pares consecutivos."""

    details = [pair_detail(longitudinal, year, year + 1) for year in years if year + 1 in years]
    detail = pd.concat(details, ignore_index=True) if details else pd.DataFrame()
    kpis: list[dict[str, object]] = []
    for (year, next_year), group in detail.groupby(["ANIO_BASE", "ANIO_COMPARACION"]):
        base_rows = group[group["ESTADO_ROTACION"].isin(["PERMANECE", "ROTA"])]
        comp_rows = group[group["ESTADO_ROTACION"].isin(["PERMANECE", "NUEVO INGRESO"])]
        dot_base = len(base_rows)
        dot_comp = len(comp_rows)
        remain = int(group["PERMANECE"].sum())
        rotate = int(group["ROTA"].sum())
        new = int(group["NUEVO"].sum())
        if dot_base != remain + rotate or dot_comp != remain + new:
            raise ValueError(f"Identidad de conjuntos fallida {year}-{next_year}")
        kpis.append(
            {
                "ANIO_BASE": year,
                "ANIO_COMPARACION": next_year,
                "DOTACION_BASE": dot_base,
                "DOTACION_SIGUIENTE": dot_comp,
                "PERMANECEN": remain,
                "ROTAN": rotate,
                "NUEVOS": new,
                "TASA_OFICIAL_ROTACION": pct(rotate, dot_base),
                "TASA_RETENCION": pct(remain, dot_base),
                "VARIACION_NETA": dot_comp - dot_base,
                "VARIACION_PORCENTUAL": pct(dot_comp - dot_base, dot_base),
                "ESTADO_PUBLICACION": "NO_PUBLICABLE_FASE_2A",
            }
        )
    return detail, pd.DataFrame(kpis)


def detect_reentries(panel: pd.DataFrame, years: Sequence[int]) -> pd.DataFrame:
    """Detecta reingresos sin modificar clasificacion anual."""

    rows: list[dict[str, object]] = []
    for _index, row in panel.iterrows():
        seen_present = False
        absent_years: list[int] = []
        last_present = None
        for year in years:
            state = row[str(year)]
            if state == 1 and absent_years and seen_present:
                rows.append(
                    {
                        "CLAVE_DOCUMENTAL": row["CLAVE_DOCUMENTAL"],
                        "ANIO_SALIDA": last_present,
                        "ANIO_REINGRESO": year,
                        "ANIOS_AUSENTES": ",".join(map(str, absent_years)),
                    }
                )
                absent_years = []
            if state == 1:
                seen_present = True
                last_present = year
            elif state == 0 and seen_present:
                absent_years.append(year)
    return pd.DataFrame(rows, columns=["CLAVE_DOCUMENTAL", "ANIO_SALIDA", "ANIO_REINGRESO", "ANIOS_AUSENTES"])


def detect_mobility(detail: pd.DataFrame, longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Registra movilidad de atributos para permanentes."""

    if detail.empty:
        return pd.DataFrame()
    fields = ["CARGO", "FORMACION", "PROGRAMA_PRINCIPAL", "ADSCRIPCION", "TOTAL_HORAS", "JERARQUIA_OCDE", "TIPO_CONTRACTUAL"]
    indexed = longitudinal.set_index(["ANIO", "CLAVE_DOCUMENTAL"], drop=False)
    rows: list[dict[str, object]] = []
    remain = detail[detail["ESTADO_ROTACION"].eq("PERMANECE")]
    for _index, item in remain.iterrows():
        base_key = (item["ANIO_BASE"], item["CLAVE_DOCUMENTAL"])
        comp_key = (item["ANIO_COMPARACION"], item["CLAVE_DOCUMENTAL"])
        if base_key not in indexed.index or comp_key not in indexed.index:
            continue
        base = indexed.loc[base_key]
        comp = indexed.loc[comp_key]
        changed = [field for field in fields if str(base.get(field, "")) != str(comp.get(field, ""))]
        if changed:
            rows.append(
                {
                    "ANIO_BASE": item["ANIO_BASE"],
                    "ANIO_COMPARACION": item["ANIO_COMPARACION"],
                    "CLAVE_DOCUMENTAL": item["CLAVE_DOCUMENTAL"],
                    "CAMPOS_CAMBIADOS": ";".join(changed),
                    "CANTIDAD_CAMBIOS": len(changed),
                }
            )
    return pd.DataFrame(rows, columns=["ANIO_BASE", "ANIO_COMPARACION", "CLAVE_DOCUMENTAL", "CAMPOS_CAMBIADOS", "CANTIDAD_CAMBIOS"])


def desaggregate(detail: pd.DataFrame, column: str, variable: str) -> pd.DataFrame:
    """Calcula KPI por variable del anio base."""

    rows: list[dict[str, object]] = []
    base = detail[detail["ESTADO_ROTACION"].isin(["PERMANECE", "ROTA"])].copy()
    if column not in base.columns:
        return pd.DataFrame()
    for (year, next_year, value), group in base.groupby(["ANIO_BASE", "ANIO_COMPARACION", column], dropna=False):
        total = len(group)
        rotate = int(group["ROTA"].sum())
        rows.append(
            {
                "VARIABLE": variable,
                "ANIO_BASE": year,
                "ANIO_COMPARACION": next_year,
                "CATEGORIA": "" if pd.isna(value) else str(value),
                "DOTACION_BASE": total,
                "PERMANECEN": int(group["PERMANECE"].sum()),
                "ROTAN": rotate,
                "TASA_OFICIAL_ROTACION": pct(rotate, total),
                "ESTADO_PUBLICACION": "NO_PUBLICABLE_FASE_2A",
            }
        )
    return pd.DataFrame(rows)
