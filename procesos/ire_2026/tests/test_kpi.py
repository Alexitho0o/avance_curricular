"""Tests de KPI: indicadores derivados contra valores verificados (§6)."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kpi import (
    calcular_indicadores,
    calcular_serie_historica,
    calcular_variacion,
    redondear_presentacion,
    SERIE_HISTORICA,
)

TOLERANCIA = 1e-3

# Valores verificados (§6 del encargo)
REFERENCIA_M2_CONSTRUIDOS_POR_ESTUDIANTE = {2023: 6.185, 2024: 8.513, 2025: 5.492}
REFERENCIA_M2_AREAS_VERDES_POR_ESTUDIANTE = {2023: 2.004, 2024: 2.756, 2025: 1.778}
REFERENCIA_M2_TALLERES_LAB_POR_ESTUDIANTE = {2023: 1.328, 2024: 1.826, 2025: 1.178}
REFERENCIA_COMPUTADORES_POR_ESTUDIANTE = {2023: 1.100, 2024: 1.575, 2025: 1.016}


@pytest.fixture
def serie():
    """Calcular la serie histórica completa."""
    return calcular_serie_historica()


@pytest.mark.parametrize("anio", [2023, 2024, 2025])
def test_m2_construidos_por_estudiante(serie, anio):
    valor = serie[anio]["m2_construidos_por_estudiante"]
    esperado = REFERENCIA_M2_CONSTRUIDOS_POR_ESTUDIANTE[anio]
    assert valor == pytest.approx(esperado, abs=TOLERANCIA), \
        f"{anio}: se esperaba {esperado}, se obtuvo {valor}"


@pytest.mark.parametrize("anio", [2023, 2024, 2025])
def test_m2_areas_verdes_por_estudiante(serie, anio):
    valor = serie[anio]["m2_areas_verdes_por_estudiante"]
    esperado = REFERENCIA_M2_AREAS_VERDES_POR_ESTUDIANTE[anio]
    assert valor == pytest.approx(esperado, abs=TOLERANCIA), \
        f"{anio}: se esperaba {esperado}, se obtuvo {valor}"


@pytest.mark.parametrize("anio", [2023, 2024, 2025])
def test_m2_talleres_lab_por_estudiante(serie, anio):
    valor = serie[anio]["m2_talleres_lab_por_estudiante"]
    esperado = REFERENCIA_M2_TALLERES_LAB_POR_ESTUDIANTE[anio]
    assert valor == pytest.approx(esperado, abs=TOLERANCIA), \
        f"{anio}: se esperaba {esperado}, se obtuvo {valor}"


@pytest.mark.parametrize("anio", [2023, 2024, 2025])
def test_computadores_por_estudiante(serie, anio):
    valor = serie[anio]["computadores_por_estudiante"]
    esperado = REFERENCIA_COMPUTADORES_POR_ESTUDIANTE[anio]
    assert valor == pytest.approx(esperado, abs=TOLERANCIA), \
        f"{anio}: se esperaba {esperado}, se obtuvo {valor}"


def test_indicadores_2025_completos(serie):
    """2025 tiene datos completos: verificar los 9 indicadores calculan sin None."""
    indicadores_2025 = serie[2025]

    for nombre, valor in indicadores_2025.items():
        assert valor is not None, f"Indicador '{nombre}' es None para 2025 (dato completo esperado)"


def test_indicadores_2023_2024_incompletos_dan_none(serie):
    """2023 y 2024 no tienen biblioteca/capacidad completa: deben dar None, no inventar dato."""
    for anio in (2023, 2024):
        indicadores = serie[anio]
        # No hay capacidad_salas_clases ni volumenes ni horas_personal_biblioteca en la fuente
        assert indicadores["capacidad_salas_por_estudiante"] is None
        assert indicadores["volumenes_fisicos_por_estudiante"] is None
        assert indicadores["horas_bibliotecario_por_100_estudiantes"] is None
        assert indicadores["tasa_ocupacion_salas"] is None


def test_ebooks_por_estudiante_serie_completa(serie):
    """E-books por estudiante SI está disponible para los 3 años (dato en la fuente)."""
    for anio in (2023, 2024, 2025):
        assert serie[anio]["ebooks_por_estudiante"] is not None, \
            f"ebooks_por_estudiante deberia estar disponible para {anio}"


def test_matricula_obligatoria():
    """calcular_indicadores debe fallar si falta matricula."""
    with pytest.raises(ValueError, match="matricula"):
        calcular_indicadores({"m2_edificados": 1000})


def test_precision_completa_sin_redondeo_prematuro():
    """El calculo interno debe mantener precision completa, no redondear hasta presentar."""
    datos = {"matricula": 160, "m2_edificados": 1362}
    resultado = calcular_indicadores(datos)
    valor_exacto = 1362 / 160

    assert resultado["m2_construidos_por_estudiante"] == valor_exacto, \
        "El calculo interno no debe redondear (solo redondear_presentacion() al presentar)"


def test_redondear_presentacion():
    """redondear_presentacion() aplica 2 decimales solo al presentar."""
    assert redondear_presentacion(8.5125, 2) in (8.51, 8.52)  # banker's rounding en el limite
    assert redondear_presentacion(None) is None
    assert redondear_presentacion(1.0 / 3, 2) == 0.33


def test_calcular_variacion():
    """Variacion interanual absoluta y porcentual."""
    variacion = calcular_variacion(248, 160)
    assert variacion["absoluta"] == 88
    assert variacion["porcentual"] == pytest.approx(55.0, abs=TOLERANCIA)


def test_calcular_variacion_con_none():
    """Si falta algun valor, la variacion debe ser None (no inventar)."""
    variacion = calcular_variacion(None, 160)
    assert variacion["absoluta"] is None
    assert variacion["porcentual"] is None


def test_serie_historica_matricula_correcta():
    """Verificar que la matricula base de la serie historica sea la documentada."""
    assert SERIE_HISTORICA[2023]["matricula"] == 220
    assert SERIE_HISTORICA[2024]["matricula"] == 160
    assert SERIE_HISTORICA[2025]["matricula"] == 248
