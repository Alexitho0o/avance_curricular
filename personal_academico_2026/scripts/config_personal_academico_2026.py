"""Configuracion centralizada para Personal Academico SIES 2026.

Las estructuras oficiales observadas en `insumos/` usan separador `;`.
El instructivo 2026 menciona archivos CSV delimitados por comas.

Por esa tension documentada, la salida final debe quedar parametrizada y
ningun archivo oficial debe generarse sin auditoria previa. La decision final
de delimitador de salida debe quedar registrada en la auditoria asociada.
"""

from __future__ import annotations

from pathlib import Path
import unicodedata


PROCESO = "PERSONAL_ACADEMICO_SIES_2026"
FECHA_CORTE_REFERENCIAL = "2026-05"
PLAZO_CARGA_INSTRUCTIVO = "2026-06-12"

MODULE_DIR = Path(__file__).resolve().parents[1]
INSUMOS_DIR = MODULE_DIR / "insumos"
DOCS_DIR = MODULE_DIR / "docs"
RESULTADOS_DIR = MODULE_DIR / "resultados"
AUDITORIAS_DIR = MODULE_DIR / "auditorias"
BITACORAS_DIR = MODULE_DIR / "bitacoras"
TESTS_DIR = MODULE_DIR / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
SCRIPTS_DIR = MODULE_DIR / "scripts"

ARCHIVO_ESTRUCTURA_EN_INSTITUCION = (
    "20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv"
)
ARCHIVO_ESTRUCTURA_FUERA_INSTITUCION = (
    "20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv"
)
ARCHIVO_INSTRUCTIVO = "Personal Académico SIES - Instructivo 2026.txt"

DELIMITADOR_ESTRUCTURA_OBSERVADO = ";"
DELIMITADOR_INSTRUCTIVO_DECLARADO = ","
EXPORTAR_CON_ENCABEZADO_DEFAULT = False
EXPORTAR_INDICE_DEFAULT = False
ENCODING_DEFAULT = "utf-8-sig"

COLUMNAS_EN_INSTITUCION = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "NIVEL_FORMACION_ACADEMICO",
    "NOMBRE_TITULO_O_GRADO",
    "NOMBRE_INSTITUCION_OBT_TITULO",
    "PAIS_OBTENCION_TIT_O_GRADO",
    "FECHA_OBT_TIT_O_GRADO",
    "NIVEL_FORMACION_ESPECIALIDAD",
    "TIPO_ESPECIALIDAD",
    "NOMBRE_ESPECIALIDAD",
    "NOMBRE_INST_OBT_ESPECIALIDAD",
    "PAIS_OBTENCION_ESPECIALIDAD",
    "FECHA_OBTENCION_ESPECIALIDAD",
    "PRINCIPAL_CARGO_ACADEMICO",
    "CARGO_NORMALIZADO",
    "NIVEL_SUPERIOR_ADSCRIPCION",
    "NIVEL_SECUNDARIO_ADSCRIPCION",
    "COMUNA_MAYOR_FUNCION",
    "NOMBRE_PRINCIPAL_PROGRAMA",
    "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
    "COMUNA_PRINCIPAL_PROGRAMA",
    "NUM_HORAS_PLANTA",
    "NUM_HORAS_CONTRATA",
    "NUM_HORAS_HONORARIOS",
    "JERARQUIA_ACADEMICA",
    "JERARQUIA_ACADEMICA_OCDE",
    "VIGENCIA",
]

COLUMNAS_FUERA_INSTITUCION = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "NIVEL_FORMACION_ACADEMICO",
    "NOMBRE_TITULO_O_GRADO",
    "NOMBRE_INSTITUCION_OBT_TITULO",
    "PAIS_OBTENCION_TIT_O_GRADO",
    "FECHA_OBT_TIT_O_GRADO",
    "NIVEL_FORMACION_ESPECIALIDAD",
    "TIPO_ESPECIALIDAD",
    "NOMBRE_ESPECIALIDAD",
    "NOMBRE_INST_OBT_ESPECIALIDAD",
    "PAIS_OBTENCION_ESPECIALIDAD",
    "FECHA_OBTENCION_ESPECIALIDAD",
    "TOTAL_HORAS_CONTRATADAS",
    "MOTIVO_COMISION_FUERA_IES",
    "NOMBRE_PROGRAMA_DE_ESTUDIOS",
    "INSTITUCION_PROGRAMA_ESTUDIOS",
    "PAIS_PROGRAMA_ESTUDIOS",
    "FECHA_INICIO_PROGRAMA_ESTUDIOS",
    "VIGENCIA",
]

COLUMNAS_OBLIGATORIAS_BASICAS_PREVENTIVAS = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "NIVEL_FORMACION_ACADEMICO",
    "VIGENCIA",
]

COLUMNAS_FECHA_COMUNES = [
    "FECHA_NACIMIENTO",
    "FECHA_OBT_TIT_O_GRADO",
    "FECHA_OBTENCION_ESPECIALIDAD",
]

COLUMNAS_FECHA_FUERA_INSTITUCION = COLUMNAS_FECHA_COMUNES + [
    "FECHA_INICIO_PROGRAMA_ESTUDIOS",
]

COLUMNAS_HORAS_EN_INSTITUCION = [
    "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
    "NUM_HORAS_PLANTA",
    "NUM_HORAS_CONTRATA",
    "NUM_HORAS_HONORARIOS",
]

COLUMNAS_HORAS_FUERA_INSTITUCION = [
    "TOTAL_HORAS_CONTRATADAS",
]


def normalizar_nombre_archivo(nombre: str) -> str:
    """Devuelve el nombre en NFC para comparar rutas con acentos."""
    return unicodedata.normalize("NFC", nombre)


def resolver_insumo(nombre_oficial: str) -> Path:
    """Resuelve un insumo aunque macOS lo presente en composicion Unicode NFD."""
    objetivo = normalizar_nombre_archivo(nombre_oficial)
    candidato = INSUMOS_DIR / nombre_oficial
    if candidato.exists():
        return candidato
    for path in INSUMOS_DIR.iterdir():
        if normalizar_nombre_archivo(path.name) == objetivo:
            return path
    raise FileNotFoundError(f"No se encontro insumo oficial: {nombre_oficial}")


def columnas_por_tipo(tipo: str) -> list[str]:
    if tipo == "en_institucion":
        return COLUMNAS_EN_INSTITUCION
    if tipo == "fuera_institucion":
        return COLUMNAS_FUERA_INSTITUCION
    raise ValueError("tipo debe ser 'en_institucion' o 'fuera_institucion'")


def columnas_fecha_por_tipo(tipo: str) -> list[str]:
    if tipo == "fuera_institucion":
        return COLUMNAS_FECHA_FUERA_INSTITUCION
    return COLUMNAS_FECHA_COMUNES


def columnas_horas_por_tipo(tipo: str) -> list[str]:
    if tipo == "fuera_institucion":
        return COLUMNAS_HORAS_FUERA_INSTITUCION
    return COLUMNAS_HORAS_EN_INSTITUCION
