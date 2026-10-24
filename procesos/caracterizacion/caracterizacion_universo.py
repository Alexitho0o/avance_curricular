#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reglas focalizadas y reutilizables del universo institucional.

Este módulo no construye universos ni decide períodos. Solo clasifica nombres
de programa con reglas parametrizables para que cada consumidor aplique el
mismo criterio antes de publicar una vista de pregrado.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from typing import Any, Pattern

import pandas as pd

TIPO_PREGRADO = "PREGRADO"
TIPO_DIPLOMADO = "DIPLOMADO"
TIPO_POSTITULO = "POSTITULO"
TIPO_CATALOGO_EXCLUSION = "CATALOGO_EXCLUSION"
TIPO_SIN_INFORMACION = "SIN_INFORMACION"

PATRONES_PROGRAMA_DEFAULT: dict[str, str] = {
    TIPO_DIPLOMADO: r"\bDIPLOMAD[OA]S?\b",
    TIPO_POSTITULO: r"\b(?:POSTITULOS?|POST\s+TITULOS?)\b",
}

TIPOS_EXCLUIDOS_DEFAULT = frozenset(
    {TIPO_DIPLOMADO, TIPO_POSTITULO, TIPO_CATALOGO_EXCLUSION}
)


def normalizar_programa(valor: Any) -> str:
    """Normaliza acentos, caja, puntuación y espacios de un nombre."""
    if valor is None:
        return ""
    try:
        if bool(pd.isna(valor)):
            return ""
    except (TypeError, ValueError):
        pass

    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    texto = texto.upper()
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _catalogo_normalizado(catalogo_exclusion: Iterable[Any] | None) -> frozenset[str]:
    if catalogo_exclusion is None:
        return frozenset()
    return frozenset(
        nombre
        for nombre in (normalizar_programa(valor) for valor in catalogo_exclusion)
        if nombre
    )


def _reglas_compiladas(
    patrones: Mapping[str, str | Pattern[str]] | None,
) -> tuple[tuple[str, Pattern[str]], ...]:
    reglas: dict[str, str | Pattern[str]] = dict(PATRONES_PROGRAMA_DEFAULT)
    if patrones:
        reglas.update(patrones)
    return tuple(
        (
            str(tipo).strip().upper(),
            patron if hasattr(patron, "search") else re.compile(str(patron)),
        )
        for tipo, patron in reglas.items()
    )


def _clasificar_normalizado(
    nombre_normalizado: str,
    *,
    catalogo_normalizado: frozenset[str],
    reglas: tuple[tuple[str, Pattern[str]], ...],
    tipo_default: str,
) -> str:
    if not nombre_normalizado:
        return TIPO_SIN_INFORMACION
    for tipo, patron in reglas:
        if patron.search(nombre_normalizado):
            return tipo
    if nombre_normalizado in catalogo_normalizado:
        return TIPO_CATALOGO_EXCLUSION
    return tipo_default


def clasificar_programa(
    valor: Any,
    *,
    catalogo_exclusion: Iterable[Any] | None = None,
    patrones: Mapping[str, str | Pattern[str]] | None = None,
    tipo_default: str = TIPO_PREGRADO,
) -> str:
    """Clasifica un programa sin depender de año, período ni catálogo fijo.

    ``patrones`` agrega reglas o reemplaza una regla predeterminada si reutiliza
    su etiqueta. Los patrones se evalúan sobre el nombre ya normalizado.
    Cualquier coincidencia exacta con ``catalogo_exclusion`` también queda
    excluida, aunque su texto no contenga las palabras diplomado o postítulo.
    """
    return _clasificar_normalizado(
        normalizar_programa(valor),
        catalogo_normalizado=_catalogo_normalizado(catalogo_exclusion),
        reglas=_reglas_compiladas(patrones),
        tipo_default=str(tipo_default).strip().upper() or TIPO_PREGRADO,
    )


def mascara_programas_excluidos(
    programas: pd.Series,
    *,
    catalogo_exclusion: Iterable[Any] | None = None,
    patrones: Mapping[str, str | Pattern[str]] | None = None,
    tipos_excluidos: Iterable[str] = TIPOS_EXCLUIDOS_DEFAULT,
) -> pd.Series:
    """Retorna una máscara booleana alineada con la serie recibida."""
    if not isinstance(programas, pd.Series):
        raise TypeError("programas debe ser una pandas.Series para conservar su índice.")

    catalogo = _catalogo_normalizado(catalogo_exclusion)
    reglas = _reglas_compiladas(patrones)
    excluidos = {str(tipo).strip().upper() for tipo in tipos_excluidos}
    clasificaciones = programas.map(
        lambda valor: _clasificar_normalizado(
            normalizar_programa(valor),
            catalogo_normalizado=catalogo,
            reglas=reglas,
            tipo_default=TIPO_PREGRADO,
        )
    )
    mascara = clasificaciones.isin(excluidos)
    mascara.name = programas.name
    return mascara.astype(bool)


__all__ = [
    "PATRONES_PROGRAMA_DEFAULT",
    "TIPO_CATALOGO_EXCLUSION",
    "TIPO_DIPLOMADO",
    "TIPO_POSTITULO",
    "TIPO_PREGRADO",
    "TIPO_SIN_INFORMACION",
    "TIPOS_EXCLUIDOS_DEFAULT",
    "clasificar_programa",
    "mascara_programas_excluidos",
    "normalizar_programa",
]
