#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Politica operativa para pendientes de incorporacion a LimeSurvey."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


CATEGORIA_EN_VENTANA = "EN_VENTANA_DIARIA"
CATEGORIA_REZAGADO = "REZAGADO_FUERA_DE_VENTANA"
CATEGORIA_FECHA_INVALIDA = "FECHA_MATRICULA_INVALIDA"
CATEGORIA_FECHA_POSTERIOR = "FECHA_MATRICULA_POSTERIOR_A_VENTANA"
CATEGORIA_NO_OBJETIVO_ANOINGRESO = "NO_OBJETIVO_ANOINGRESO"
POLITICA_PENDIENTES_LIMESURVEY_ID = "H045-v3"


@dataclass(frozen=True)
class ClasificacionPendienteLimeSurvey:
    categoria: str
    fecha_matricula: date | None
    es_objetivo: bool
    en_ventana: bool
    es_rezagado: bool


def clasificar_pendiente_limesurvey(
    fecha_matricula: date | datetime | None,
    *,
    ano_ingreso: object,
    anio_objetivo: int,
    ventana_inicio: date,
    ventana_fin: date,
) -> ClasificacionPendienteLimeSurvey:
    """Clasifica un vigente sin token dentro de la poblacion objetivo.

    La encuesta de caracterizacion se aplica solo cuando ``ANOINGRESO`` es
    igual al anio analizado. Dentro de esa poblacion, ``FECHAMATRICULA``
    determina ventana diaria o rezago.
    """
    if ventana_inicio > ventana_fin:
        raise ValueError("ventana_inicio no puede ser posterior a ventana_fin")

    try:
        ano_num = float(str(ano_ingreso).strip())
        ano_normalizado = int(ano_num) if ano_num.is_integer() else None
    except (TypeError, ValueError):
        ano_normalizado = None

    if ano_normalizado != int(anio_objetivo):
        return ClasificacionPendienteLimeSurvey(
            categoria=CATEGORIA_NO_OBJETIVO_ANOINGRESO,
            fecha_matricula=None,
            es_objetivo=False,
            en_ventana=False,
            es_rezagado=False,
        )

    if isinstance(fecha_matricula, datetime):
        fecha = fecha_matricula.date()
    elif isinstance(fecha_matricula, date):
        fecha = fecha_matricula
    else:
        fecha = None

    if fecha is None:
        return ClasificacionPendienteLimeSurvey(
            categoria=CATEGORIA_FECHA_INVALIDA,
            fecha_matricula=None,
            es_objetivo=True,
            en_ventana=False,
            es_rezagado=False,
        )
    if fecha < ventana_inicio:
        return ClasificacionPendienteLimeSurvey(
            categoria=CATEGORIA_REZAGADO,
            fecha_matricula=fecha,
            es_objetivo=True,
            en_ventana=False,
            es_rezagado=True,
        )
    if fecha > ventana_fin:
        return ClasificacionPendienteLimeSurvey(
            categoria=CATEGORIA_FECHA_POSTERIOR,
            fecha_matricula=fecha,
            es_objetivo=True,
            en_ventana=False,
            es_rezagado=False,
        )
    return ClasificacionPendienteLimeSurvey(
        categoria=CATEGORIA_EN_VENTANA,
        fecha_matricula=fecha,
        es_objetivo=True,
        en_ventana=True,
        es_rezagado=False,
    )
