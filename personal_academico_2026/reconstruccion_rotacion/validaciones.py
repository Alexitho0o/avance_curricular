"""Validaciones no destructivas de la reconstruccion Fase 2A."""

from __future__ import annotations

import pandas as pd

from .utilidades import compute_rut_dv, normalize_value


def validate_longitudinal(longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta validaciones documentales, vigencia, duplicados y horas."""

    rows: list[dict[str, object]] = []
    duplicated = longitudinal[longitudinal.duplicated(["ANIO", "CLAVE_DOCUMENTAL"], keep=False)]
    for year, group in duplicated.groupby("ANIO"):
        rows.append({"ANIO": year, "CODIGO": "DUPLICADO_CLAVE_ANIO", "SEVERIDAD": "ERROR", "CASOS": len(group), "DETALLE": "Clave documental duplicada en anio."})
    for _index, row in longitudinal.iterrows():
        year = int(row["ANIO"])
        key = normalize_value(row["CLAVE_DOCUMENTAL"])
        tipo = normalize_value(row["TIPO_DOCUMENTO"]).upper()
        numero = normalize_value(row["NUM_DOCUMENTO"])
        dv = normalize_value(row["DV"]).upper()
        if key == "" or tipo == "" or numero == "":
            rows.append({"ANIO": year, "CODIGO": "DOCUMENTO_VACIO", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": "Registro sin clave documental completa."})
        if tipo not in {"R", "P"}:
            rows.append({"ANIO": year, "CODIGO": "TIPO_DOCUMENTO_INVALIDO", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": "Tipo distinto de R/P."})
        if tipo == "R":
            number = "".join(ch for ch in numero if ch.isdigit())
            expected = compute_rut_dv(number)
            if expected is None or dv not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "K"}:
                rows.append({"ANIO": year, "CODIGO": "RUT_FORMATO_INVALIDO", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": "RUT o DV con formato invalido."})
            elif expected != dv:
                rows.append({"ANIO": year, "CODIGO": "RUT_DV_NO_CORRESPONDE", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": "RUT no corresponde con DV."})
        if tipo == "P" and dv != "":
            rows.append({"ANIO": year, "CODIGO": "PASAPORTE_DV_NO_VACIO", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": "Pasaporte debe tener DV vacio."})
        if normalize_value(row["VIGENCIA"]) not in {"0", "1"}:
            rows.append({"ANIO": year, "CODIGO": "VIGENCIA_INVALIDA", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": "Vigencia distinta de 0/1."})
        for column in ["HORAS_PLANTA", "HORAS_CONTRATA", "HORAS_HONORARIOS", "TOTAL_HORAS"]:
            value = row.get(column)
            if pd.isna(value):
                rows.append({"ANIO": year, "CODIGO": "HORAS_NULAS", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": column})
                continue
            if float(value) < 0:
                rows.append({"ANIO": year, "CODIGO": "HORAS_NEGATIVAS", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": column})
            if float(value) > 56:
                rows.append({"ANIO": year, "CODIGO": "HORAS_SOBRE_MAXIMO", "SEVERIDAD": "ERROR", "CASOS": 1, "DETALLE": column})
    if not rows:
        return pd.DataFrame([{"ANIO": "", "CODIGO": "SIN_HALLAZGOS_BLOQUEANTES", "SEVERIDAD": "OK", "CASOS": 0, "DETALLE": "Validaciones sin errores."}])
    return pd.DataFrame(rows)
