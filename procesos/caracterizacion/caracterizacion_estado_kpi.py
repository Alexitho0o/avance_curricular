#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regla única de "es titulado" para universos KPI (1.2.C y 1.2.D).

Antes de este módulo, la exclusión de filas VIGENTE-pero-en-realidad-tituladas
(ESTADOACADEMICO aún no actualizado, pero SITUACION ya dice
"TITULADO APROBADO") vivía duplicada de forma inconsistente dentro de
caracterizacion.py: la Sección 1.2.C la aplicaba y la Sección 1.2.D
("Histórico comparativo por períodos") no, pese a declararse "misma lógica
KPI". Este módulo es ahora la única fuente de verdad de esa regla; ambas
secciones deben importar de aquí y no reimplementar el criterio.

No decide universo, período ni exclusiones de programa/administración/
participante: solo clasifica, fila a fila, si corresponde a un titulado según
ESTADOACADEMICO o SITUACION, para que el llamador decida qué hacer con eso.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

import pandas as pd

SITUACION_TITULADO_APROBADO = "TITULADO APROBADO"
ESTADOACADEMICO_TITULADO = "TITULADO"


def _norm_txt_local(valor: Any) -> str:
    """Normalización local equivalente a la usada en caracterizacion.py:
    quita acentos, pasa a mayúsculas y colapsa espacios. Se mantiene aquí
    (en vez de importar desde caracterizacion.py) para que este módulo sea
    importable de forma independiente, sin ejecutar el script principal."""
    if valor is None:
        return ""
    try:
        if bool(pd.isna(valor)):
            return ""
    except (TypeError, ValueError):
        pass
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.upper().strip()
    return re.sub(r"\s+", " ", texto)


def es_titulado_kpi(estado_valor: Any, situacion_valor: Any) -> bool:
    """True si la fila corresponde a un titulado, ya sea porque
    ESTADOACADEMICO=='TITULADO' o porque SITUACION contiene
    'TITULADO APROBADO' (caso de desfase administrativo: el estado académico
    aún dice VIGENTE pero la situación ya refleja el título aprobado).

    Réplica exacta de la regla histórica de caracterizacion.py (antes
    ``_es_titulado_kpi``, Sección 1.2.F); no cambia el criterio, solo lo
    centraliza.
    """
    estado = _norm_txt_local(estado_valor)
    situacion = _norm_txt_local(situacion_valor)
    if estado == ESTADOACADEMICO_TITULADO:
        return True
    if SITUACION_TITULADO_APROBADO in situacion:
        return True
    return False


def mascara_titulado_kpi(estados: pd.Series, situaciones: pd.Series) -> pd.Series:
    """Versión vectorizada de :func:`es_titulado_kpi` para aplicar sobre un
    DataFrame completo. Devuelve una máscara booleana alineada con el índice
    de ``estados`` (True = fila corresponde a titulado).

    Debe producir, fila a fila, el mismo resultado que
    ``estados.combine(situaciones, es_titulado_kpi)`` — se mantiene vectorizada
    solo por rendimiento en universos históricos grandes (1.2.D).
    """
    if not isinstance(estados, pd.Series):
        raise TypeError("estados debe ser una pandas.Series para conservar su índice.")
    estado_norm = estados.map(_norm_txt_local)
    situacion_norm = situaciones.map(_norm_txt_local) if isinstance(situaciones, pd.Series) else (
        pd.Series([_norm_txt_local(situaciones)] * len(estados), index=estados.index)
    )
    mascara = (estado_norm == ESTADOACADEMICO_TITULADO) | situacion_norm.str.contains(
        SITUACION_TITULADO_APROBADO, na=False
    )
    mascara.name = estados.name
    return mascara.astype(bool)


__all__ = [
    "ESTADOACADEMICO_TITULADO",
    "SITUACION_TITULADO_APROBADO",
    "es_titulado_kpi",
    "mascara_titulado_kpi",
]
