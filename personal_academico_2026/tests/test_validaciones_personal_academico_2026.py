from pathlib import Path
import sys

import pandas as pd

MODULE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = MODULE_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from config_personal_academico_2026 import (  # noqa: E402
    COLUMNAS_EN_INSTITUCION,
    COLUMNAS_FUERA_INSTITUCION,
)
from validaciones_personal_academico_2026 import (  # noqa: E402
    calcular_dv_rut_chileno,
    normalizar_texto_basico,
    validar_columnas_exactas,
    validar_duplicados_documento,
    validar_fechas_formato,
    validar_horas_numericas,
)


FIXTURES = MODULE_DIR / "tests" / "fixtures"


def leer_fixture(nombre):
    return pd.read_csv(FIXTURES / nombre, sep=";", dtype=str, keep_default_na=False)


def test_columnas_en_institucion_34():
    assert len(COLUMNAS_EN_INSTITUCION) == 34


def test_columnas_fuera_institucion_27():
    assert len(COLUMNAS_FUERA_INSTITUCION) == 27


def test_valida_columnas_exactas_ok():
    df = leer_fixture("en_institucion_valido_minimo.csv")
    resultado = validar_columnas_exactas(df, COLUMNAS_EN_INSTITUCION)
    assert resultado["ok"] is True


def test_detecta_columna_extra():
    df = leer_fixture("fuera_institucion_columna_extra.csv")
    resultado = validar_columnas_exactas(df, COLUMNAS_FUERA_INSTITUCION)
    assert resultado["ok"] is False
    assert resultado["resumen"]["adicionales"] == ["COLUMNA_EXTRA"]


def test_detecta_mal_orden():
    df = leer_fixture("en_institucion_columnas_mal_orden.csv")
    resultado = validar_columnas_exactas(df, COLUMNAS_EN_INSTITUCION)
    assert resultado["ok"] is False
    assert resultado["resumen"]["fuera_orden"]


def test_detecta_duplicado_documento():
    df = leer_fixture("en_institucion_duplicado_documento.csv")
    resultado = validar_duplicados_documento(df)
    assert resultado["ok"] is False
    assert resultado["resumen"]["duplicados"] == 2


def test_calcula_dv_rut():
    assert calcular_dv_rut_chileno("11111111") == "1"
    assert calcular_dv_rut_chileno("12345678") == "5"


def test_normaliza_texto_basico():
    assert normalizar_texto_basico("  ángel   ñúñez  ") == "ANGEL ÑUÑEZ"


def test_valida_horas_negativas():
    df = pd.DataFrame({"NUM_HORAS_PLANTA": ["-1"]})
    resultado = validar_horas_numericas(df, ["NUM_HORAS_PLANTA"])
    assert resultado["ok"] is False


def test_valida_fechas_invalidas():
    df = pd.DataFrame({"FECHA_NACIMIENTO": ["31-02-2020"]})
    resultado = validar_fechas_formato(df, ["FECHA_NACIMIENTO"])
    assert resultado["ok"] is False
