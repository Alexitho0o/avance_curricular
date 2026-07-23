"""Schema IRE 2026: 54 columnas exactas, tipos, aplicabilidad, catálogos."""

from enum import Enum
from typing import List, Optional, Set


class TipoInfraestructura(Enum):
    """Categorías de infraestructura."""
    INMUEBLE_PERMANENTE = 1
    INMUEBLE_RESTRINGIDO = 2
    BIBLIOTECA = 3
    DIGITAL = 4
    PREDIO = 5
    PLATAFORMA_VIRTUAL = 6


class Tipo:
    """Definición de un tipo de columna."""
    TEXTO = "texto"
    NUMERO = "numero"
    NUMERO_ENTERO = "numero_entero"
    FECHA_AAAA_MM = "fecha_aaaa_mm"
    MARCA = "marca"  # "X" o vacío


# Las 54 columnas exactas en orden
COLUMNAS = [
    "TIPO_INFRAESTRUCTURA",
    "NOMBRE_IDENTIFICACION",
    "COMUNA",
    "DIRECCION_INMUEBLE",
    "SITUACION_TENENCIA",
    "ANIO_INICIO_USO_INMUEBLE",
    "USO_EXCLUSIVO",
    "PORCENTAJE_USO",
    "NOMBRE_INSTITUCION_COMPARTE",
    "FECHA_INICIO_TENENCIA",
    "FECHA_TERMINO",
    "DESCRIPCION_OTRA_TENENCIA",
    "FUNCION_DOCENCIA",
    "FUNCION_INVESTIGACION",
    "FUNCION_EXTENSION",
    "FUNCION_ADM_OFICINAS",
    "FUNCION_OTRAS",
    "DESC_OTRAS_FUNCIONES",
    "TOTAL_M2_TERRENO",
    "TOTAL_M2_EDIFICADOS",
    "TOTAL_SALAS_CLASES",
    "CAPACIDAD_SALAS_CLASES",
    "TOTAL_M2_SALAS_CLASES",
    "TOTAL_AUDITORIOS",
    "CAPACIDAD_AUDITORIOS",
    "TOTAL_M2_AUDITORIOS",
    "TOTAL_LABORATORIOS",
    "TOTAL_M2_LABORATORIOS",
    "TOTAL_TALLERES",
    "TOTAL_M2_TALLERES",
    "TOTAL_PC_NB_DISPONIBLE",
    "TOTAL_M2_CASINOS_CAFETERIAS",
    "TOTAL_M2_AREAS_VERDES",
    "UR_DESC_ACTIVIDADES",
    "UR_TOTAL_M2_TERRENO",
    "UR_TOTAL_M2_CONSTRUIDOS",
    "UR_SITUACION_TENENCIA",
    "UR_DESC_TENENCIA_OTRA",
    "TOTAL_M2_BIBLIOTECA",
    "TOTAL_M2_SALAS_LECTURA",
    "TOTAL_PROFESIONALES_BIBLIOTECA",
    "HORAS_PERSONAL_BIBLIOTECA",
    "TOTAL_TITULOS_DISPONIBLES",
    "TOTAL_VOLUMENES_DISPONIBLES",
    "TOTAL_SUSCRIPCIONES_REVISTAS",
    "TOTAL_TITULOS_LIBROS_DIGITALES",
    "TOTAL_SUSCRIPCIONES_DIGITALES",
    "TOTAL_BASE_DATOS",
    "TOTAL_HECTAREAS_PREDIO",
    "SISTEMA_GESTION_APRENDIZAJES",
    "SISTEMA_VIDEO_CONFERENCIA",
    "SISTEMA_APLICACION_EVALUACION",
    "DESCRIPCION_PLATAFORMA_VIRTUAL",
    "VIGENCIA",
]

# Catálogos
CATALOGO_TIPO_INFRAESTRUCTURA = {
    1: "Inmueble de Uso Permanente",
    2: "Inmueble de Uso Restringido",
    3: "Características de Biblioteca",
    4: "Características de Libros y Bases Digitales",
    5: "Predios",
    6: "Plataformas Virtuales",
}

CATALOGO_SITUACION_TENENCIA = {
    1: "Propio",
    2: "Arrendado",
    3: "En Comodato",
    4: "En Usufructo",
    5: "Leasing o LeaseBack",
    6: "Otro",
}

CATALOGO_USO_EXCLUSIVO = {
    1: "Exclusivo",
    2: "Compartido",
}

CATALOGO_UR_SITUACION_TENENCIA = {
    1: "Arrendado",
    2: "Otra",
}

CATALOGO_VIGENCIA = {
    0: "Eliminar registro",
    1: "Mantener",
}

# Especificación: tipo, aplicabilidad, obligatorio
ESPECIFICACION = {
    "TIPO_INFRAESTRUCTURA": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1, 2, 3, 4, 5, 6}, "obligatorio": True},
    "NOMBRE_IDENTIFICACION": {"tipo": Tipo.TEXTO, "aplica": {1, 2, 3, 4, 5, 6}, "obligatorio": True},
    "COMUNA": {"tipo": Tipo.TEXTO, "aplica": {1, 2, 3, 4, 5, 6}, "obligatorio": True},
    "DIRECCION_INMUEBLE": {"tipo": Tipo.TEXTO, "aplica": {1, 2, 3, 4, 5, 6}, "obligatorio": True},
    "SITUACION_TENENCIA": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "ANIO_INICIO_USO_INMUEBLE": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "USO_EXCLUSIVO": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "PORCENTAJE_USO": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": False},
    "NOMBRE_INSTITUCION_COMPARTE": {"tipo": Tipo.TEXTO, "aplica": {1}, "obligatorio": False},
    "FECHA_INICIO_TENENCIA": {"tipo": Tipo.FECHA_AAAA_MM, "aplica": {1}, "obligatorio": False},
    "FECHA_TERMINO": {"tipo": Tipo.FECHA_AAAA_MM, "aplica": {1}, "obligatorio": False},
    "DESCRIPCION_OTRA_TENENCIA": {"tipo": Tipo.TEXTO, "aplica": {1}, "obligatorio": False},
    "FUNCION_DOCENCIA": {"tipo": Tipo.MARCA, "aplica": {1}, "obligatorio": False},
    "FUNCION_INVESTIGACION": {"tipo": Tipo.MARCA, "aplica": {1}, "obligatorio": False},
    "FUNCION_EXTENSION": {"tipo": Tipo.MARCA, "aplica": {1}, "obligatorio": False},
    "FUNCION_ADM_OFICINAS": {"tipo": Tipo.MARCA, "aplica": {1}, "obligatorio": False},
    "FUNCION_OTRAS": {"tipo": Tipo.MARCA, "aplica": {1}, "obligatorio": False},
    "DESC_OTRAS_FUNCIONES": {"tipo": Tipo.TEXTO, "aplica": {1}, "obligatorio": False},
    "TOTAL_M2_TERRENO": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_EDIFICADOS": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_SALAS_CLASES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "CAPACIDAD_SALAS_CLASES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_SALAS_CLASES": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_AUDITORIOS": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "CAPACIDAD_AUDITORIOS": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_AUDITORIOS": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_LABORATORIOS": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_LABORATORIOS": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_TALLERES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_TALLERES": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_PC_NB_DISPONIBLE": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_CASINOS_CAFETERIAS": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "TOTAL_M2_AREAS_VERDES": {"tipo": Tipo.NUMERO, "aplica": {1}, "obligatorio": True},
    "UR_DESC_ACTIVIDADES": {"tipo": Tipo.TEXTO, "aplica": {2}, "obligatorio": True},
    "UR_TOTAL_M2_TERRENO": {"tipo": Tipo.NUMERO, "aplica": {2}, "obligatorio": True},
    "UR_TOTAL_M2_CONSTRUIDOS": {"tipo": Tipo.NUMERO, "aplica": {2}, "obligatorio": True},
    "UR_SITUACION_TENENCIA": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {2}, "obligatorio": True},
    "UR_DESC_TENENCIA_OTRA": {"tipo": Tipo.TEXTO, "aplica": {2}, "obligatorio": False},
    "TOTAL_M2_BIBLIOTECA": {"tipo": Tipo.NUMERO, "aplica": {3}, "obligatorio": True},
    "TOTAL_M2_SALAS_LECTURA": {"tipo": Tipo.NUMERO, "aplica": {3}, "obligatorio": True},
    "TOTAL_PROFESIONALES_BIBLIOTECA": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {3}, "obligatorio": True},
    "HORAS_PERSONAL_BIBLIOTECA": {"tipo": Tipo.NUMERO, "aplica": {3}, "obligatorio": True},
    "TOTAL_TITULOS_DISPONIBLES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {3}, "obligatorio": True},
    "TOTAL_VOLUMENES_DISPONIBLES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {3}, "obligatorio": True},
    "TOTAL_SUSCRIPCIONES_REVISTAS": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {3}, "obligatorio": True},
    "TOTAL_TITULOS_LIBROS_DIGITALES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {4}, "obligatorio": True},
    "TOTAL_SUSCRIPCIONES_DIGITALES": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {4}, "obligatorio": True},
    "TOTAL_BASE_DATOS": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {4}, "obligatorio": True},
    "TOTAL_HECTAREAS_PREDIO": {"tipo": Tipo.NUMERO, "aplica": {5}, "obligatorio": True},
    "SISTEMA_GESTION_APRENDIZAJES": {"tipo": Tipo.TEXTO, "aplica": {6}, "obligatorio": True},
    "SISTEMA_VIDEO_CONFERENCIA": {"tipo": Tipo.TEXTO, "aplica": {6}, "obligatorio": True},
    "SISTEMA_APLICACION_EVALUACION": {"tipo": Tipo.TEXTO, "aplica": {6}, "obligatorio": True},
    "DESCRIPCION_PLATAFORMA_VIRTUAL": {"tipo": Tipo.TEXTO, "aplica": {6}, "obligatorio": True},
    "VIGENCIA": {"tipo": Tipo.NUMERO_ENTERO, "aplica": {1, 2, 3, 4, 5, 6}, "obligatorio": True},
}


def obtener_columnas_aplicables(tipo_infraestructura: int) -> Set[str]:
    """Retornar set de columnas que aplican para un TIPO_INFRAESTRUCTURA."""
    return {col for col, spec in ESPECIFICACION.items() if tipo_infraestructura in spec["aplica"]}
