#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retencion longitudinal institucional por persona."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd

from caracterizacion_rut import normalizar_rut_clave


ESTADOS_BASE_ELEGIBLES = {"VIGENTE", "SUSPENDIDO"}
ESTADOS_DESTINO_RETENIDOS = {"VIGENTE", "SUSPENDIDO"}
ESTADOS_EXCLUIDOS = {"TITULADO", "ELIMINADO", "DEFUNCION", "FALLECIDO"}


@dataclass(frozen=True)
class RetencionLongitudinalResult:
    detalle: pd.DataFrame
    resumen_global: pd.DataFrame
    resumen_dimensiones: dict[str, pd.DataFrame]
    auditoria: pd.DataFrame


def _norm_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if bool(pd.isna(value)):
            return ""
    except (TypeError, ValueError):
        pass
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", str(value))
        if not unicodedata.combining(ch)
    ).upper().strip()
    return re.sub(r"\s+", " ", text)


def _norm_program(value: Any) -> str:
    text = _norm_text(value)
    return re.sub(r"[^A-Z0-9]+", "", text)


def _col(df: pd.DataFrame, name: str, default: Any = "") -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series(default, index=df.index)


def _prepare_retention_frame(
    df: pd.DataFrame,
    *,
    col_rut: str,
    col_codcli: str,
    col_programa: str,
    col_carrera: str,
    col_jornada: str,
    col_sede: str,
    col_nivel: str,
    col_sexo: str,
    col_tipo: str | None,
    col_anio: str,
    col_periodo: str,
    col_estado: str,
) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("La fuente de retencion debe ser un DataFrame.")
    work = pd.DataFrame(index=df.index)
    work["RUT_ORIGINAL"] = _col(df, col_rut)
    work["RUT_NORMALIZADO"] = work["RUT_ORIGINAL"].map(normalizar_rut_clave)
    work["CODCLI"] = _col(df, col_codcli).fillna("").astype(str).str.strip()
    work["PROGRAMA_ID"] = _col(df, col_programa).map(_norm_program)
    work["CARRERA"] = _col(df, col_carrera).fillna("").astype(str).str.strip()
    work["CARRERA_NORM"] = work["CARRERA"].map(_norm_text)
    work["JORNADA"] = _col(df, col_jornada).fillna("").astype(str).str.strip()
    work["SEDE"] = _col(df, col_sede).fillna("").astype(str).str.strip()
    work["NIVEL"] = _col(df, col_nivel).fillna("").astype(str).str.strip()
    work["SEXO"] = _col(df, col_sexo).fillna("").astype(str).str.strip()
    work["TIPO_ESTUDIANTE"] = _col(df, col_tipo, "") if col_tipo else ""
    work["ANIO"] = pd.to_numeric(_col(df, col_anio), errors="coerce")
    work["PERIODO"] = pd.to_numeric(_col(df, col_periodo), errors="coerce")
    work["ESTADO"] = _col(df, col_estado).map(_norm_text)
    work = work[work["ANIO"].notna() & work["PERIODO"].notna()].copy()
    work["ANIO"] = work["ANIO"].astype(int)
    work["PERIODO"] = work["PERIODO"].astype(int)
    work["ORDEN"] = work["ANIO"] * 10 + work["PERIODO"]
    if work["PROGRAMA_ID"].eq("").all():
        work["PROGRAMA_ID"] = work["CARRERA_NORM"].map(_norm_program)
    return work


def _select_one_per_person(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    state_prio = {"VIGENTE": 0, "SUSPENDIDO": 1, "TITULADO": 2, "EGRESADO": 3, "ELIMINADO": 4}
    out = df.copy()
    out["_ESTADO_PRIO"] = out["ESTADO"].map(state_prio).fillna(9).astype(int)
    out.sort_values(["RUT_NORMALIZADO", "_ESTADO_PRIO", "ORDEN", "CODCLI"], ascending=[True, True, False, True], inplace=True)
    out = out.groupby("RUT_NORMALIZADO", dropna=False).head(1).copy()
    return out.drop(columns=["_ESTADO_PRIO"], errors="ignore")


def _summarise(detalle: pd.DataFrame, dims: Sequence[str]) -> pd.DataFrame:
    cols = list(dims) + [
        "COHORTE_ELEGIBLE",
        "RETENIDOS_INSTITUCIONALES",
        "RETENIDOS_MISMO_PROGRAMA",
        "RETENIDOS_CAMBIO_PROGRAMA",
        "NO_RETENIDOS",
        "TITULADOS_ANTES_SEGUIMIENTO",
        "EXCLUIDOS",
        "AMBIGUOS",
        "SIN_LLAVE_VALIDA",
        "RETENCION_INSTITUCIONAL_PCT",
        "RETENCION_MISMO_PROGRAMA_PCT",
        "ESTADO_VALIDACION",
    ]
    if detalle.empty:
        return pd.DataFrame(columns=cols)
    data = detalle.copy()
    data["_RET_INST"] = data["RESULTADO_RETENCION"].eq("RETENIDO_INSTITUCIONAL").astype(int)
    data["_RET_MISMO"] = data["RESULTADO_PROGRAMA"].eq("MISMO_PROGRAMA").astype(int)
    data["_RET_CAMBIO"] = data["RESULTADO_PROGRAMA"].eq("CAMBIO_PROGRAMA").astype(int)
    data["_NO_RET"] = data["RESULTADO_RETENCION"].eq("NO_RETENIDO").astype(int)
    data["_TIT_ANTES"] = data["RESULTADO_RETENCION"].eq("TITULADO_ANTES_SEGUIMIENTO").astype(int)
    data["_EXCL"] = data["RESULTADO_RETENCION"].str.startswith("EXCLUIDO").astype(int)
    data["_AMB"] = data["RESULTADO_RETENCION"].eq("AMBIGUO").astype(int)
    data["_SIN_LLAVE"] = data["RESULTADO_RETENCION"].eq("SIN_LLAVE_VALIDA").astype(int)
    if dims:
        grouped = data.groupby(list(dims), dropna=False)
    else:
        grouped = [((), data)]
    rows: list[dict[str, Any]] = []
    for key, group in grouped:
        row: dict[str, Any] = {}
        if dims:
            key_tuple = key if isinstance(key, tuple) else (key,)
            row.update(dict(zip(dims, key_tuple)))
        eligible = int(group["ES_ELEGIBLE"].sum())
        ret_inst = int(group["_RET_INST"].sum())
        ret_mismo = int(group["_RET_MISMO"].sum())
        row.update(
            {
                "COHORTE_ELEGIBLE": eligible,
                "RETENIDOS_INSTITUCIONALES": ret_inst,
                "RETENIDOS_MISMO_PROGRAMA": ret_mismo,
                "RETENIDOS_CAMBIO_PROGRAMA": int(group["_RET_CAMBIO"].sum()),
                "NO_RETENIDOS": int(group["_NO_RET"].sum()),
                "TITULADOS_ANTES_SEGUIMIENTO": int(group["_TIT_ANTES"].sum()),
                "EXCLUIDOS": int(group["_EXCL"].sum()),
                "AMBIGUOS": int(group["_AMB"].sum()),
                "SIN_LLAVE_VALIDA": int(group["_SIN_LLAVE"].sum()),
                "RETENCION_INSTITUCIONAL_PCT": round(ret_inst / eligible * 100, 2) if eligible else np.nan,
                "RETENCION_MISMO_PROGRAMA_PCT": round(ret_mismo / eligible * 100, 2) if eligible else np.nan,
                "ESTADO_VALIDACION": "VALIDADO" if eligible and ret_inst <= eligible and ret_mismo <= eligible else "NO_VALIDADO",
            }
        )
        rows.append(row)
    return pd.DataFrame(rows, columns=cols)


def calcular_retencion_longitudinal(
    df: pd.DataFrame,
    *,
    anio_base: int,
    anio_destino: int,
    periodo_base: int,
    periodo_destino: int,
    fecha_corte: str,
    col_rut: str = "RUT",
    col_codcli: str = "CODCLI",
    col_programa: str = "CODCARPR",
    col_carrera: str = "CARRERA",
    col_jornada: str = "JORNADA",
    col_sede: str = "SEDE",
    col_nivel: str = "NIVEL",
    col_sexo: str = "SEXO",
    col_tipo: str | None = "TIPO_ESTUDIANTE",
    col_anio: str = "ANIO",
    col_periodo: str = "PERIODO",
    col_estado: str = "ESTADO",
    umbral_cohorte_grande: int = 30,
) -> RetencionLongitudinalResult:
    work = _prepare_retention_frame(
        df,
        col_rut=col_rut,
        col_codcli=col_codcli,
        col_programa=col_programa,
        col_carrera=col_carrera,
        col_jornada=col_jornada,
        col_sede=col_sede,
        col_nivel=col_nivel,
        col_sexo=col_sexo,
        col_tipo=col_tipo,
        col_anio=col_anio,
        col_periodo=col_periodo,
        col_estado=col_estado,
    )
    base_raw = work[(work["ANIO"].eq(int(anio_base))) & (work["PERIODO"].eq(int(periodo_base)))].copy()
    dest_raw = work[(work["ANIO"].eq(int(anio_destino))) & (work["PERIODO"].eq(int(periodo_destino)))].copy()
    base = _select_one_per_person(base_raw[base_raw["RUT_NORMALIZADO"].ne("")])
    dest = _select_one_per_person(dest_raw[dest_raw["RUT_NORMALIZADO"].ne("")])
    dest_by_rut = dest.set_index("RUT_NORMALIZADO", drop=False)
    rows: list[dict[str, Any]] = []
    for _, row in base.iterrows():
        rut = row["RUT_NORMALIZADO"]
        estado_base = row["ESTADO"]
        if not rut:
            resultado = "SIN_LLAVE_VALIDA"
            eligible = False
            dest_row = pd.Series(dtype="object")
        elif estado_base in {"TITULADO"}:
            resultado = "TITULADO_ANTES_SEGUIMIENTO"
            eligible = False
            dest_row = pd.Series(dtype="object")
        elif estado_base in ESTADOS_EXCLUIDOS:
            resultado = f"EXCLUIDO_{estado_base}"
            eligible = False
            dest_row = pd.Series(dtype="object")
        else:
            eligible = estado_base in ESTADOS_BASE_ELEGIBLES
            dest_row = dest_by_rut.loc[rut] if rut in dest_by_rut.index else pd.Series(dtype="object")
            if not eligible:
                resultado = "EXCLUIDO_ESTADO_BASE_NO_ELEGIBLE"
            elif not dest_row.empty and str(dest_row.get("ESTADO", "")) in ESTADOS_DESTINO_RETENIDOS:
                resultado = "RETENIDO_INSTITUCIONAL"
            else:
                resultado = "NO_RETENIDO"
        prog_base = str(row.get("PROGRAMA_ID", ""))
        prog_dest = str(dest_row.get("PROGRAMA_ID", "")) if not dest_row.empty else ""
        if resultado == "RETENIDO_INSTITUCIONAL":
            resultado_programa = "MISMO_PROGRAMA" if prog_base and prog_base == prog_dest else "CAMBIO_PROGRAMA"
        else:
            resultado_programa = "NO_APLICA"
        rows.append(
            {
                "RUT_NORMALIZADO": rut,
                "RUT_ORIGINAL": row.get("RUT_ORIGINAL", ""),
                "CODCLI_BASE": row.get("CODCLI", ""),
                "CODCLI_DESTINO": dest_row.get("CODCLI", "") if not dest_row.empty else "",
                "ANIO_BASE": int(anio_base),
                "PERIODO_BASE": int(periodo_base),
                "ANIO_DESTINO": int(anio_destino),
                "PERIODO_DESTINO": int(periodo_destino),
                "FECHA_CORTE": fecha_corte,
                "CARRERA_BASE": row.get("CARRERA", ""),
                "CARRERA_DESTINO": dest_row.get("CARRERA", "") if not dest_row.empty else "",
                "PROGRAMA_BASE": prog_base,
                "PROGRAMA_DESTINO": prog_dest,
                "JORNADA": row.get("JORNADA", ""),
                "SEDE": row.get("SEDE", ""),
                "NIVEL": row.get("NIVEL", ""),
                "SEXO": row.get("SEXO", ""),
                "TIPO_ESTUDIANTE": row.get("TIPO_ESTUDIANTE", ""),
                "ESTADO_BASE": estado_base,
                "ESTADO_DESTINO": dest_row.get("ESTADO", "") if not dest_row.empty else "",
                "ES_ELEGIBLE": bool(eligible),
                "RESULTADO_RETENCION": resultado,
                "RESULTADO_PROGRAMA": resultado_programa,
            }
        )
    detalle = pd.DataFrame(rows)
    resumen_global = _summarise(detalle, [])
    dimensiones = {
        "CARRERA": _summarise(detalle, ["CARRERA_BASE"]),
        "JORNADA": _summarise(detalle, ["JORNADA"]),
        "SEDE": _summarise(detalle, ["SEDE"]),
        "COHORTE": _summarise(detalle, ["ANIO_BASE", "PERIODO_BASE"]),
        "SEXO": _summarise(detalle, ["SEXO"]),
        "TIPO_ESTUDIANTE": _summarise(detalle, ["TIPO_ESTUDIANTE"]),
        "NIVEL": _summarise(detalle, ["NIVEL"]),
    }
    audit_rows = [
            {"METRICA": "filas_fuente", "VALOR": int(len(df)), "RESULTADO": "INFO"},
            {"METRICA": "filas_normalizadas", "VALOR": int(len(work)), "RESULTADO": "INFO"},
            {"METRICA": "base_bruta_periodo", "VALOR": int(len(base_raw)), "RESULTADO": "INFO"},
            {"METRICA": "destino_bruto_periodo", "VALOR": int(len(dest_raw)), "RESULTADO": "INFO"},
            {"METRICA": "base_personas_con_llave", "VALOR": int(len(base)), "RESULTADO": "INFO"},
            {"METRICA": "destino_personas_con_llave", "VALOR": int(len(dest)), "RESULTADO": "INFO"},
            {
                "METRICA": "periodos_comparables",
                "VALOR": "SI" if int(periodo_base) == int(periodo_destino) else "NO",
                "RESULTADO": "OK" if int(periodo_base) == int(periodo_destino) else "ERROR",
            },
            {
                "METRICA": "definicion",
                "VALOR": "RETENCION_INSTITUCIONAL_POR_RUT_Y_RETENCION_MISMO_PROGRAMA_SEPARADAS",
                "RESULTADO": "OK",
            },
    ]
    if not resumen_global.empty:
        cohorte = int(pd.to_numeric(resumen_global.iloc[0].get("COHORTE_ELEGIBLE", 0), errors="coerce") or 0)
        retenidos = int(pd.to_numeric(resumen_global.iloc[0].get("RETENIDOS_INSTITUCIONALES", 0), errors="coerce") or 0)
        audit_rows.append(
            {
                "METRICA": "plausibilidad_retencion_cero_cohorte_grande",
                "VALOR": "SI" if cohorte >= int(umbral_cohorte_grande) and retenidos == 0 else "NO",
                "RESULTADO": "ADVERTENCIA" if cohorte >= int(umbral_cohorte_grande) and retenidos == 0 else "OK",
            }
        )
        audit_rows.append(
            {
                "METRICA": "identidad_retenidos_en_cohorte",
                "VALOR": f"{retenidos}<={cohorte}",
                "RESULTADO": "OK" if 0 <= retenidos <= cohorte else "ERROR",
            }
        )
    auditoria = pd.DataFrame(audit_rows)
    return RetencionLongitudinalResult(detalle, resumen_global, dimensiones, auditoria)
