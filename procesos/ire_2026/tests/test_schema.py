"""Test del schema: 54 columnas exactas contra archivo oficial."""

import pytest
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schema import COLUMNAS


@pytest.fixture
def ruta_estructura_oficial():
    """Ruta al archivo oficial de estructura."""
    return Path(__file__).parent.parent / "data" / "estructura" / "20260706_89535_Estructura_IRE_ID_16770.csv"


def test_columnas_cantidad():
    """Las 54 columnas tienen exactamente 54 elementos."""
    assert len(COLUMNAS) == 54, f"Se esperan 54 columnas, se encontraron {len(COLUMNAS)}"


def test_columnas_contra_archivo_oficial(ruta_estructura_oficial):
    """Las 54 columnas coinciden 1-a-1 con el archivo oficial."""
    assert ruta_estructura_oficial.exists(), f"Archivo oficial no encontrado: {ruta_estructura_oficial}"

    with open(ruta_estructura_oficial, 'r', encoding='utf-8') as f:
        primera_linea = f.readline()

    # Limpiar BOM si existe
    if primera_linea.startswith('﻿'):
        primera_linea = primera_linea[1:]

    # Parsear encabezados oficiales
    encabezados_oficiales = [col.strip() for col in primera_linea.strip().split(';')]

    # Verificar cantidad
    assert len(encabezados_oficiales) == 54, \
        f"Archivo oficial tiene {len(encabezados_oficiales)} columnas, se esperan 54"

    # Verificar coincidencia elemento a elemento
    for i, (oficial, local) in enumerate(zip(encabezados_oficiales, COLUMNAS)):
        assert oficial == local, \
            f"Columna {i+1}: oficial='{oficial}', schema='{local}'"


def test_columnas_sin_duplicados():
    """No hay nombres de columna duplicados."""
    assert len(COLUMNAS) == len(set(COLUMNAS)), "Hay nombres de columna duplicados"


def test_columnas_no_vacias():
    """Todas las columnas tienen nombres no vacíos."""
    for col in COLUMNAS:
        assert col.strip(), "Hay una columna vacía o con solo espacios"
