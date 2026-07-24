"""Tests de validación: reglas Anexo III completas + casos negativos."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.validacion import ejecutar, agrupar_por_severidad, Severidad
from common.io_csv import leer_csv
from src.schema import COLUMNAS
from src.validators import obtener_reglas, validar_dataset


@pytest.fixture
def reglas():
    """Obtener todas las reglas por fila."""
    return obtener_reglas()


@pytest.fixture
def historico_2025():
    """Cargar histórico 2025 normalizado."""
    ruta = Path(__file__).parent.parent / "data" / "historico" / "ire_historico.csv"
    encabezados, filas = leer_csv(str(ruta), delimitador=';', encoding='utf-8')
    return encabezados, filas


def fila_vacia() -> dict:
    """Fila base con las 54 columnas vacías."""
    return {col: "" for col in COLUMNAS}


def fila_tipo1_valida() -> dict:
    """Fila TIPO 1 mínima válida, para usar como base en tests negativos."""
    fila = fila_vacia()
    fila.update({
        "TIPO_INFRAESTRUCTURA": "1",
        "NOMBRE_IDENTIFICACION": "INSTITUTO PROFESIONAL SAN SEBASTIAN",
        "COMUNA": "SANTIAGO",
        "DIRECCION_INMUEBLE": "AVENIDA LIBERTADOR BERNARDO OHIGGINS 2221",
        "SITUACION_TENENCIA": "2",
        "ANIO_INICIO_USO_INMUEBLE": "2014",
        "USO_EXCLUSIVO": "1",
        "FECHA_INICIO_TENENCIA": "2025-01",
        "FECHA_TERMINO": "2026-12",
        "FUNCION_DOCENCIA": "X",
        "TOTAL_M2_TERRENO": "789",
        "TOTAL_M2_EDIFICADOS": "1362",
        "TOTAL_SALAS_CLASES": "5",
        "CAPACIDAD_SALAS_CLASES": "141",
        "TOTAL_M2_SALAS_CLASES": "168.2",
        "TOTAL_AUDITORIOS": "1",
        "CAPACIDAD_AUDITORIOS": "85",
        "TOTAL_M2_AUDITORIOS": "72.1",
        "TOTAL_LABORATORIOS": "0",
        "TOTAL_M2_LABORATORIOS": "0",
        "TOTAL_TALLERES": "9",
        "TOTAL_M2_TALLERES": "292.1",
        "TOTAL_PC_NB_DISPONIBLE": "252",
        "TOTAL_M2_CASINOS_CAFETERIAS": "34.3",
        "TOTAL_M2_AREAS_VERDES": "440.9",
        "VIGENCIA": "1",
    })
    return fila


def errores_de(reglas, fila) -> list:
    """Ejecutar reglas sobre una única fila y retornar mensajes de ERROR."""
    resultados, _ = ejecutar(reglas, [fila], detener_en_error=False)
    por_severidad = agrupar_por_severidad(resultados)
    return [r.mensaje for r in por_severidad[Severidad.ERROR]]


# ============ Tests contra histórico 2025 (deben pasar sin errores) ============

def test_historico_carga_exitosa(historico_2025):
    """Verificar que el histórico se carga correctamente."""
    encabezados, filas = historico_2025

    assert len(encabezados) == 54, f"Se esperan 54 columnas, se encontraron {len(encabezados)}"
    assert len(filas) >= 5, f"Se esperan al menos 5 registros históricos, se encontraron {len(filas)}"


def test_historico_sin_errores(reglas, historico_2025):
    """Verificar que el histórico 2025 pase todas las reglas por fila SIN ERRORES."""
    encabezados, filas = historico_2025

    resultados, sin_errores = ejecutar(reglas, filas, detener_en_error=False)
    por_severidad = agrupar_por_severidad(resultados)

    assert sin_errores, f"El histórico tiene {len(por_severidad[Severidad.ERROR])} errores"
    assert len(por_severidad[Severidad.ERROR]) == 0, \
        "Errores encontrados:\n" + \
        "\n".join(f"  Fila {r.fila_indice}: {r.regla_id} - {r.mensaje}"
                  for r in por_severidad[Severidad.ERROR][:10])


def test_historico_sin_errores_dataset(historico_2025):
    """Verificar que el histórico 2025 pase las reglas a nivel de dataset."""
    encabezados, filas = historico_2025

    errores = validar_dataset(filas)
    assert errores == [], f"Errores de dataset encontrados: {errores}"


def test_historico_tipos_infraestructura(historico_2025):
    """Verificar que los tipos de infraestructura sean válidos."""
    encabezados, filas = historico_2025

    tipos_encontrados = set()
    for fila in filas:
        tipo = fila.get("TIPO_INFRAESTRUCTURA", "")
        if tipo.strip():
            tipos_encontrados.add(int(tipo))

    assert 1 in tipos_encontrados, "Debe haber al menos un TIPO 1"
    assert 2 in tipos_encontrados, "Debe haber al menos un TIPO 2"
    assert 3 in tipos_encontrados, "Debe haber al menos un TIPO 3"
    assert 4 in tipos_encontrados, "Debe haber al menos un TIPO 4"
    assert 6 in tipos_encontrados, "Debe haber al menos un TIPO 6"


def test_historico_vigencia(historico_2025):
    """Verificar que todos los registros tengan VIGENCIA = 1."""
    encabezados, filas = historico_2025

    for i, fila in enumerate(filas):
        vigencia = fila.get("VIGENCIA", "").strip()
        assert vigencia in ["0", "1"], f"Fila {i}: VIGENCIA inválida = '{vigencia}'"
        assert vigencia == "1", f"Fila {i}: VIGENCIA debe ser 1 en histórico, se encontró {vigencia}"


# ============ Tests negativos: cada uno debe disparar su ERROR ============

def test_negativo_campo_prohibido_lleno(reglas):
    """TIPO 1 con un campo de TIPO 3 (prohibido) lleno debe fallar."""
    fila = fila_tipo1_valida()
    fila["TOTAL_M2_BIBLIOTECA"] = "80"  # Prohibido para TIPO 1

    errores = errores_de(reglas, fila)
    assert any("prohibido" in (m or "") for m in errores), \
        f"Se esperaba error de campo prohibido, se obtuvo: {errores}"


def test_negativo_tenencia_propia_con_fecha(reglas):
    """SITUACION_TENENCIA=1 (Propio) con FECHA_INICIO_TENENCIA debe fallar."""
    fila = fila_tipo1_valida()
    fila["SITUACION_TENENCIA"] = "1"
    fila["FECHA_INICIO_TENENCIA"] = "2020-01"  # Prohibido si es Propio

    errores = errores_de(reglas, fila)
    assert any("Propio" in (m or "") for m in errores), \
        f"Se esperaba error de tenencia Propio con fecha, se obtuvo: {errores}"


def test_negativo_fecha_malformada(reglas):
    """FECHA_INICIO_TENENCIA con formato inválido debe fallar."""
    fila = fila_tipo1_valida()
    fila["FECHA_INICIO_TENENCIA"] = "01-2025"  # Formato incorrecto

    errores = errores_de(reglas, fila)
    assert any("formato AAAA-MM" in (m or "") for m in errores), \
        f"Se esperaba error de formato de fecha, se obtuvo: {errores}"


def test_negativo_uso_compartido_sin_porcentaje(reglas):
    """USO_EXCLUSIVO=2 (Compartido) sin PORCENTAJE_USO debe fallar."""
    fila = fila_tipo1_valida()
    fila["USO_EXCLUSIVO"] = "2"
    fila["PORCENTAJE_USO"] = ""
    fila["NOMBRE_INSTITUCION_COMPARTE"] = "OTRA INSTITUCION"

    errores = errores_de(reglas, fila)
    assert any("PORCENTAJE_USO obligatorio" in (m or "") for m in errores), \
        f"Se esperaba error de porcentaje de uso obligatorio, se obtuvo: {errores}"


def test_negativo_llave_duplicada():
    """Dos filas con la misma llave (TIPO+NOMBRE+COMUNA+DIRECCION) deben fallar."""
    fila1 = fila_tipo1_valida()
    fila2 = fila_tipo1_valida()  # Llave idéntica

    errores = validar_dataset([fila1, fila2])
    assert any("Llave duplicada" in e for e in errores), \
        f"Se esperaba error de llave duplicada, se obtuvo: {errores}"


def test_negativo_dos_filas_tipo6():
    """Más de una fila TIPO 6 debe fallar."""
    fila_tipo6_a = fila_vacia()
    fila_tipo6_a.update({
        "TIPO_INFRAESTRUCTURA": "6",
        "NOMBRE_IDENTIFICACION": "INSTITUTO PROFESIONAL SAN SEBASTIAN",
        "COMUNA": "SANTIAGO",
        "DIRECCION_INMUEBLE": "DIRECCION A",
        "SISTEMA_GESTION_APRENDIZAJES": "MOODLE",
        "SISTEMA_VIDEO_CONFERENCIA": "TEAMS",
        "SISTEMA_APLICACION_EVALUACION": "NO APLICA",
        "DESCRIPCION_PLATAFORMA_VIRTUAL": "DESCRIPCION A",
        "VIGENCIA": "1",
    })
    fila_tipo6_b = fila_vacia()
    fila_tipo6_b.update({
        "TIPO_INFRAESTRUCTURA": "6",
        "NOMBRE_IDENTIFICACION": "INSTITUTO PROFESIONAL SAN SEBASTIAN",
        "COMUNA": "SANTIAGO",
        "DIRECCION_INMUEBLE": "DIRECCION B",
        "SISTEMA_GESTION_APRENDIZAJES": "MOODLE",
        "SISTEMA_VIDEO_CONFERENCIA": "TEAMS",
        "SISTEMA_APLICACION_EVALUACION": "NO APLICA",
        "DESCRIPCION_PLATAFORMA_VIRTUAL": "DESCRIPCION B",
        "VIGENCIA": "1",
    })

    errores = validar_dataset([fila_tipo6_a, fila_tipo6_b])
    assert any("exactamente una fila TIPO 6" in e for e in errores), \
        f"Se esperaba error de multiples filas TIPO 6, se obtuvo: {errores}"


def test_negativo_texto_con_enie(reglas):
    """Texto con 'ñ' debe fallar (solo ASCII permitido)."""
    fila = fila_tipo1_valida()
    fila["NOMBRE_INSTITUCION_COMPARTE"] = ""
    fila["COMUNA"] = "PENALOLEN"  # válido de referencia
    fila["NOMBRE_IDENTIFICACION"] = "INSTITUTO CAMPAÑA"  # contiene ñ

    errores = errores_de(reglas, fila)
    assert any("ASCII" in (m or "") for m in errores), \
        f"Se esperaba error de caracter no ASCII (ñ), se obtuvo: {errores}"


def test_negativo_texto_con_punto_y_coma(reglas):
    """Texto con ';' debe fallar (rompe el delimitador del CSV)."""
    fila = fila_tipo1_valida()
    fila["NOMBRE_IDENTIFICACION"] = "INSTITUTO; PROFESIONAL"

    errores = errores_de(reglas, fila)
    assert any("rompe el delimitador" in (m or "") for m in errores), \
        f"Se esperaba error de ';' en campo, se obtuvo: {errores}"


def test_negativo_anio_fuera_de_rango(reglas):
    """ANIO_INICIO_USO_INMUEBLE fuera de [1800-2026] debe fallar."""
    fila = fila_tipo1_valida()
    fila["ANIO_INICIO_USO_INMUEBLE"] = "1750"

    errores = errores_de(reglas, fila)
    assert any("ANIO_INICIO_USO_INMUEBLE fuera de rango" in (m or "") for m in errores), \
        f"Se esperaba error de año fuera de rango, se obtuvo: {errores}"


def test_negativo_comuna_con_numeros(reglas):
    """COMUNA con números debe fallar (solo letras)."""
    fila = fila_tipo1_valida()
    fila["COMUNA"] = "SANTIAGO2"

    errores = errores_de(reglas, fila)
    assert any("solo letras" in (m or "") for m in errores), \
        f"Se esperaba error de COMUNA con numeros, se obtuvo: {errores}"


def test_superficie_dos_decimales_es_error(reglas):
    """Un m² con 2 decimales debe producir error de validación (PES rechaza)."""
    fila = fila_tipo1_valida()
    fila["TOTAL_M2_TALLERES"] = "449.81"

    errores = errores_de(reglas, fila)
    assert any("decimal" in (m or "").lower() for m in errores), \
        f"Se esperaba error de mas de 1 decimal en superficie, se obtuvo: {errores}"


def test_superficie_un_decimal_no_es_error(reglas):
    """Un m² con 1 decimal (o entero) no debe disparar la regla de decimales."""
    fila = fila_tipo1_valida()  # ya trae valores con 1 decimal (168.2, 72.1, etc.)

    errores = errores_de(reglas, fila)
    assert not any("decimal" in (m or "").lower() for m in errores), \
        f"No se esperaba error de decimales con valores válidos, se obtuvo: {errores}"
