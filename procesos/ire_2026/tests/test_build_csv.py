"""Tests de build_csv.py: normalización de decimales de superficie."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.build_csv import normalizar_decimales


def test_normalizar_decimales_redondea_a_uno():
    fila = {
        "TOTAL_M2_TALLERES": "449.81",
        "TOTAL_M2_TERRENO": "789",
        "TOTAL_M2_AREAS_VERDES": "440.90",
    }
    normalizar_decimales(fila)
    assert fila["TOTAL_M2_TALLERES"] == "449.8"    # redondeado
    assert fila["TOTAL_M2_TERRENO"] == "789"        # entero intacto, sin .0
    assert fila["TOTAL_M2_AREAS_VERDES"] == "440.9"  # cero de más eliminado


def test_normalizar_decimales_devuelve_cambios():
    fila = {"TOTAL_M2_SALAS_CLASES": "162.11", "TOTAL_M2_AUDITORIOS": "181.3"}
    cambios = normalizar_decimales(fila)

    assert ("TOTAL_M2_SALAS_CLASES", "162.11", "162.1") in cambios
    # 181.3 ya tiene 1 decimal: no debe reportarse como cambio
    assert not any(c[0] == "TOTAL_M2_AUDITORIOS" for c in cambios)


def test_normalizar_decimales_ignora_campo_vacio_o_no_numerico():
    fila = {"TOTAL_M2_TERRENO": "", "TOTAL_M2_BIBLIOTECA": "no-es-numero"}
    cambios = normalizar_decimales(fila)
    assert cambios == []
    assert fila["TOTAL_M2_BIBLIOTECA"] == "no-es-numero"  # no lo toca; lo atrapa la validacion


def test_normalizar_decimales_ignora_campos_fuera_de_la_lista():
    """Campos que no son de superficie (p. ej. capacidades) no se tocan."""
    fila = {"CAPACIDAD_SALAS_CLASES": "141.55"}
    cambios = normalizar_decimales(fila)
    assert cambios == []
    assert fila["CAPACIDAD_SALAS_CLASES"] == "141.55"
