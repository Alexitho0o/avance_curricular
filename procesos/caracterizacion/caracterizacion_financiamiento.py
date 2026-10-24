#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrato de la pregunta multiseleccion G01Q19 de financiamiento."""

from __future__ import annotations

import re
from collections.abc import Iterable


CODIGOS_FINANCIAMIENTO_G01Q19 = (
    "G01Q19[SQ002]",
    "G01Q19[SQ003]",
    "G01Q19[SQ004]",
    "G01Q19[SQ005]",
    "G01Q19[SQ006]",
    "G01Q19[SQ007]",
    "G01Q19[SQ008]",
    "G01Q19[SQ009]",
    "G01Q19[SQ010]",
    "G01Q19[SQ011]",
    "G01Q19[SQ012]",
)

DETALLES_FINANCIAMIENTO_G01Q19 = {
    "G01Q19[SQ002]": "¿Cómo vas a financiar tus estudios? [Ingresos propios]",
    "G01Q19[SQ003]": "¿Cómo vas a financiar tus estudios? [Ingresos de mi padre o madre]",
    "G01Q19[SQ004]": "¿Cómo vas a financiar tus estudios? [Ingresos de otros familiares]",
    "G01Q19[SQ005]": "¿Cómo vas a financiar tus estudios? [Ingresos de otras personas]",
    "G01Q19[SQ006]": "¿Cómo vas a financiar tus estudios? [Gratuidad]",
    "G01Q19[SQ007]": "¿Cómo vas a financiar tus estudios? [Otras becas del Estado]",
    "G01Q19[SQ008]": "¿Cómo vas a financiar tus estudios? [Becas externas]",
    "G01Q19[SQ009]": "¿Cómo vas a financiar tus estudios? [Crédito con Aval del Estado (CAE)]",
    "G01Q19[SQ010]": "¿Cómo vas a financiar tus estudios? [Crédito bancario o similares]",
    "G01Q19[SQ011]": "¿Cómo vas a financiar tus estudios? [Mi empleador o empresa]",
    "G01Q19[SQ012]": "¿Cómo vas a financiar tus estudios? [Beca institucional (IPSS)]",
}

_RE_CODIGO_FINANCIAMIENTO = re.compile(
    r"^\s*(G01Q19\[SQ\d+\])(?:\.|\s|$)",
    flags=re.IGNORECASE,
)


def codigos_financiamiento_en_headers(headers: Iterable[object]) -> tuple[str, ...]:
    """Extrae subpreguntas G01Q19 y excluye metadatos como G01Q19Time."""
    detectados: set[str] = set()
    for header in headers:
        match = _RE_CODIGO_FINANCIAMIENTO.match(str(header))
        if match:
            detectados.add(match.group(1).upper())
    return tuple(sorted(detectados))


def validar_cobertura_financiamiento(headers: Iterable[object]) -> tuple[str, ...]:
    """Exige que el instrumento contenga exactamente las 11 alternativas."""
    esperados = set(CODIGOS_FINANCIAMIENTO_G01Q19)
    detectados = set(codigos_financiamiento_en_headers(headers))
    faltantes = sorted(esperados - detectados)
    inesperados = sorted(detectados - esperados)
    if faltantes or inesperados:
        raise ValueError(
            "Cobertura G01Q19 invalida: "
            f"esperadas={len(esperados)} detectadas={len(detectados)} "
            f"faltantes={faltantes} inesperadas={inesperados}"
        )
    return CODIGOS_FINANCIAMIENTO_G01Q19
