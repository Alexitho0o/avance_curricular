#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizacion institucional de RUT/RUN para cruces auditables."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd


NULL_STRINGS = {"", "nan", "none", "null", "nat", "<na>"}


@dataclass(frozen=True)
class RutComponentes:
    rut_original: str
    rut_normalizado: str
    rut_sin_dv: str
    dv: str
    rut_valido_estructural: bool
    rut_dv_valido: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "RUT_ORIGINAL": self.rut_original,
            "RUT_NORMALIZADO": self.rut_normalizado,
            "RUT_SIN_DV": self.rut_sin_dv,
            "DV": self.dv,
            "RUT_VALIDO_ESTRUCTURAL": self.rut_valido_estructural,
            "RUT_DV_VALIDO": self.rut_dv_valido,
        }


def _text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if bool(pd.isna(value)):
            return ""
    except (TypeError, ValueError):
        pass
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", str(value)).strip()
    if text.lower() in NULL_STRINGS:
        return ""
    if re.fullmatch(r"-?\d+\.0+", text):
        text = text.split(".", 1)[0]
    return text


def calcular_dv_mod11(rut_sin_dv: str) -> str:
    digits = re.sub(r"\D", "", str(rut_sin_dv))
    if not digits:
        return ""
    suma = 0
    factor = 2
    for char in reversed(digits):
        suma += int(char) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def normalizar_rut_componentes(value: Any, *, validar_dv: bool = True) -> RutComponentes:
    raw_input = "" if value is None else str(value).strip()
    excel_integer = re.fullmatch(r"-?\d+\.0+", raw_input) is not None
    original = _text(value)
    if not original:
        return RutComponentes("", "", "", "", False, False)

    clean = original.upper().replace(".", "").replace(" ", "").replace("\u00a0", "")
    clean = re.sub(r"[^0-9Kk\-]", "", clean).upper()
    if not clean:
        return RutComponentes(original, "", "", "", False, False)

    if "-" in clean:
        body, dv = clean.split("-", 1)
        body = re.sub(r"\D", "", body)
        dv = re.sub(r"[^0-9K]", "", dv.upper())[:1]
    else:
        raw = re.sub(r"[^0-9K]", "", clean)
        if excel_integer:
            body, dv = raw, ""
        elif raw.endswith("K"):
            body, dv = raw[:-1], "K"
        elif len(raw) >= 9:
            body, dv = raw[:-1], raw[-1:]
        else:
            body, dv = raw, ""

    rut_normalizado = f"{body}{dv}" if dv else body
    estructural = bool(body) and 5 <= len(body) <= 9 and (dv == "" or re.fullmatch(r"[0-9K]", dv) is not None)
    dv_valido = False
    if validar_dv and estructural and dv:
        dv_valido = calcular_dv_mod11(body) == dv
    elif not validar_dv and estructural and dv:
        dv_valido = True
    return RutComponentes(original, rut_normalizado, body, dv, estructural, dv_valido)


def normalizar_rut_clave(value: Any, *, incluir_dv: bool = False) -> str:
    partes = normalizar_rut_componentes(value)
    return partes.rut_normalizado if incluir_dv else partes.rut_sin_dv


def normalizar_rut_dataframe(
    serie: pd.Series,
    *,
    prefijo: str = "",
    validar_dv: bool = True,
) -> pd.DataFrame:
    if not isinstance(serie, pd.Series):
        raise TypeError("normalizar_rut_dataframe requiere una Series de pandas.")
    rows = [normalizar_rut_componentes(value, validar_dv=validar_dv).as_dict() for value in serie.tolist()]
    out = pd.DataFrame(rows, index=serie.index)
    if prefijo:
        out = out.rename(columns={col: f"{prefijo}{col}" for col in out.columns})
    return out


def enmascarar_rut_clave(value: Any) -> str:
    key = normalizar_rut_clave(value, incluir_dv=False)
    if not key:
        return ""
    if len(key) <= 4:
        return "*" * len(key)
    return f"{key[:2]}***{key[-2:]}"
