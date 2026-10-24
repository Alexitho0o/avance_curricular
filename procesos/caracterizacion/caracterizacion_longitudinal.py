#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Procesos longitudinales desacoplados de Caracterización.

Este módulo es el punto de entrada explícito para análisis de retención,
permanencia, continuidad y cambios de programa. El pipeline normal de
Caracterización no debe importarlo ni ejecutarlo salvo opt-in deliberado.
"""

from __future__ import annotations

from caracterizacion_retencion import RetencionLongitudinalResult, calcular_retencion_longitudinal

__all__ = ["RetencionLongitudinalResult", "calcular_retencion_longitudinal"]
