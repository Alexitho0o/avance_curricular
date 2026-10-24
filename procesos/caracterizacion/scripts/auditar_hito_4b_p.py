#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditor automático HITO 4B-P.

Uso típico:
    python3 scripts/auditar_hito_4b_p.py \
        --sectorizado SECTORIZADO_AC_....xlsx --universo 627 \
        --sies CRUCE_SIES_....xlsx \
        --retencion KPI_ACADEMICOS_....xlsx

El auditor es deliberadamente conservador: si una salida requerida no existe,
si una hoja crítica no está disponible o si una identidad matemática falla,
termina con código 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(str(path))
    with pd.ExcelFile(path) as xls:
        if sheet_name not in xls.sheet_names:
            raise ValueError(f"{path.name}: falta hoja {sheet_name}")
        return pd.read_excel(xls, sheet_name=sheet_name)


def _ok(rows: list[dict[str, Any]], control: str, valor: Any = "", detalle: str = "") -> None:
    rows.append({"control": control, "resultado": "OK", "valor": valor, "detalle": detalle})


def _fail(rows: list[dict[str, Any]], control: str, valor: Any = "", detalle: str = "") -> None:
    rows.append({"control": control, "resultado": "ERROR", "valor": valor, "detalle": detalle})


def _jsonable(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if not isinstance(value, (list, tuple, dict, set)):
        try:
            if bool(pd.isna(value)):
                return None
        except (TypeError, ValueError):
            pass
    return value


def _jsonable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: _jsonable(v) for k, v in row.items()} for row in rows]


def auditar_sectorizado(path: Path, universo: int | None, rows: list[dict[str, Any]]) -> None:
    base = _sheet(path, "BASE_SECTORIZADA")
    _ok(rows, "sectorizado.archivo_generado", path.name)
    if universo is not None and len(base) != universo:
        _fail(rows, "sectorizado.filas_salida", len(base), f"universo={universo}")
    else:
        _ok(rows, "sectorizado.filas_salida", len(base), f"universo={universo if universo is not None else 'no_declarado'}")
    key = "LLAVE_ESTUDIANTE" if "LLAVE_ESTUDIANTE" in base.columns else None
    if key:
        duplicados = int(base[key].duplicated().sum())
        (_ok if duplicados == 0 else _fail)(rows, "sectorizado.duplicados_llave_maestra", duplicados)
    else:
        _fail(rows, "sectorizado.llave_maestra", "", "falta LLAVE_ESTUDIANTE")
    if "ESTADO_RESPUESTA" in base.columns:
        estados = base["ESTADO_RESPUESTA"].fillna("").astype(str).str.upper()
        total_estados = int(estados.isin(["SI", "INCOMPLETO", "NO"]).sum())
        (_ok if total_estados == len(base) else _fail)(rows, "sectorizado.estados_exhaustivos", total_estados, f"filas={len(base)}")
    else:
        _fail(rows, "sectorizado.estados_exhaustivos", "", "falta ESTADO_RESPUESTA")


def auditar_sies(path: Path, rows: list[dict[str, Any]]) -> None:
    detalle = _sheet(path, "CRUCE_SIES_DETALLE")
    indicadores = _sheet(path, "INDICADORES_CRUCE_SIES")
    total = len(detalle)
    flags = detalle.get("FLAG_MATCH", pd.Series("", index=detalle.index)).fillna("").astype(str).str.upper()
    matches = int(flags.eq("SI").sum())
    sin_match = int(flags.eq("NO").sum())
    conflictos = int(detalle.get("N_CANDIDATOS_MEJOR_SCORE", pd.Series(0, index=detalle.index)).fillna(0).astype(float).gt(1).sum())
    (_ok if total == matches + sin_match else _fail)(rows, "sies.identidad_filas", total, f"matches={matches}; sin_match={sin_match}; conflictos={conflictos}")
    if "CALIDAD_MATCH" in detalle.columns:
        calidades = set(detalle["CALIDAD_MATCH"].fillna("").astype(str))
        (_ok if calidades else _fail)(rows, "sies.calidad_match_documentada", ",".join(sorted(calidades)))
    else:
        _fail(rows, "sies.calidad_match_documentada", "", "falta CALIDAD_MATCH")
    estado = ""
    if {"INDICADOR", "VALOR"}.issubset(indicadores.columns):
        vals = indicadores.loc[indicadores["INDICADOR"].astype(str).eq("ESTADO_VALIDACION_SIES"), "VALOR"]
        estado = str(vals.iloc[0]) if not vals.empty else ""
    (_ok if estado else _fail)(rows, "sies.estado_validacion", estado)


def auditar_retencion(path: Path, rows: list[dict[str, Any]]) -> None:
    resumen = _sheet(path, "RET_LONG_RESUMEN")
    auditoria = _sheet(path, "RET_LONG_AUDITORIA")
    if resumen.empty:
        _fail(rows, "retencion.resumen", "", "RET_LONG_RESUMEN vacío")
    else:
        row = resumen.iloc[0]
        cohorte = int(pd.to_numeric(row.get("COHORTE_ELEGIBLE", 0), errors="coerce") or 0)
        retenidos = int(pd.to_numeric(row.get("RETENIDOS_INSTITUCIONALES", 0), errors="coerce") or 0)
        tasa = pd.to_numeric(row.get("RETENCION_INSTITUCIONAL_PCT", None), errors="coerce")
        (_ok if 0 <= retenidos <= cohorte else _fail)(rows, "retencion.retenidos_en_cohorte", retenidos, f"cohorte={cohorte}")
        (_ok if pd.isna(tasa) or 0 <= float(tasa) <= 100 else _fail)(rows, "retencion.tasa_rango", tasa)
    if {"METRICA", "RESULTADO"}.issubset(auditoria.columns):
        comparables = auditoria.loc[auditoria["METRICA"].astype(str).eq("periodos_comparables"), "RESULTADO"].astype(str).tolist()
        (_ok if comparables else _fail)(rows, "retencion.periodos_comparables_documentados", ",".join(comparables))
    else:
        _fail(rows, "retencion.auditoria", "", "faltan columnas METRICA/RESULTADO")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sectorizado", type=Path)
    parser.add_argument("--sies", type=Path)
    parser.add_argument("--retencion", type=Path)
    parser.add_argument("--universo", type=int)
    args = parser.parse_args(argv)
    rows: list[dict[str, Any]] = []
    try:
        if args.sectorizado:
            auditar_sectorizado(args.sectorizado, args.universo, rows)
        if args.sies:
            auditar_sies(args.sies, rows)
        if args.retencion:
            auditar_retencion(args.retencion, rows)
    except Exception as exc:
        _fail(rows, "auditor.excepcion", type(exc).__name__, str(exc))
    print(json.dumps(_jsonable_rows(rows), ensure_ascii=False, indent=2))
    return 1 if any(row["resultado"] == "ERROR" for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
