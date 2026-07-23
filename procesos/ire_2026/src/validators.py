"""Reglas de validación IRE 2026 (Anexo III)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
from typing import Optional, Dict
import unicodedata
from common.validacion import Regla, Severidad
from src.schema import (
    CATALOGO_TIPO_INFRAESTRUCTURA,
    CATALOGO_SITUACION_TENENCIA,
    CATALOGO_USO_EXCLUSIVO,
    CATALOGO_UR_SITUACION_TENENCIA,
    CATALOGO_VIGENCIA,
)


def es_entero(valor: str) -> bool:
    """Verificar si un valor es un número entero."""
    try:
        int(str(valor).strip())
        return True
    except (ValueError, TypeError):
        return False


def es_numero(valor: str) -> bool:
    """Verificar si un valor es un número (entero o decimal)."""
    try:
        float(str(valor).strip())
        return True
    except (ValueError, TypeError):
        return False


def es_fecha_aaaa_mm(valor: str) -> bool:
    """Verificar formato AAAA-MM."""
    if not valor or not isinstance(valor, str):
        return False
    match = re.match(r'^\d{4}-\d{2}$', valor.strip())
    return match is not None


def sin_acentos_ni_especiales(texto: str) -> bool:
    """Verificar que no tenga acentos ni caracteres no ASCII."""
    if not isinstance(texto, str):
        return False
    # Normalizar y descomponer
    nfkd = unicodedata.normalize('NFKD', texto)
    # Verificar que no haya caracteres diacríticos (categoría Mn)
    for c in nfkd:
        if unicodedata.category(c) == 'Mn':
            return False
    return True


def crear_reglas() -> list:
    """Crear todas las reglas de validación."""
    reglas = []

    # ============ TRANSVERSALES ============

    reglas.append(Regla(
        id="TIPO_INFRAESTRUCTURA_valido",
        descripcion="TIPO_INFRAESTRUCTURA debe estar entre 1 y 6",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if (
            "TIPO_INFRAESTRUCTURA" in fila and
            es_entero(fila["TIPO_INFRAESTRUCTURA"]) and
            1 <= int(fila["TIPO_INFRAESTRUCTURA"]) <= 6
        ) else "TIPO_INFRAESTRUCTURA fuera de rango [1-6]",
    ))

    reglas.append(Regla(
        id="VIGENCIA_valido",
        descripcion="VIGENCIA debe ser 0 o 1",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if (
            "VIGENCIA" in fila and
            es_entero(fila["VIGENCIA"]) and
            int(fila["VIGENCIA"]) in [0, 1]
        ) else "VIGENCIA debe ser 0 o 1",
    ))

    reglas.append(Regla(
        id="NOMBRE_IDENTIFICACION_no_vacio",
        descripcion="NOMBRE_IDENTIFICACION no puede estar vacío",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if fila.get("NOMBRE_IDENTIFICACION", "").strip() else "NOMBRE_IDENTIFICACION vacío",
    ))

    reglas.append(Regla(
        id="COMUNA_no_vacio",
        descripcion="COMUNA no puede estar vacío",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if fila.get("COMUNA", "").strip() else "COMUNA vacío",
    ))

    reglas.append(Regla(
        id="DIRECCION_INMUEBLE_no_vacio",
        descripcion="DIRECCION_INMUEBLE no puede estar vacío",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if fila.get("DIRECCION_INMUEBLE", "").strip() else "DIRECCION_INMUEBLE vacío",
    ))

    # ============ TIPO 1 — Inmueble de Uso Permanente ============

    def validar_tipo1_obligatorios(fila: Dict) -> Optional[str]:
        """TIPO 1 requiere campos obligatorios."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "1":
            return None

        campos_obligatorios = [
            "SITUACION_TENENCIA", "ANIO_INICIO_USO_INMUEBLE", "USO_EXCLUSIVO",
            "TOTAL_M2_TERRENO", "TOTAL_M2_EDIFICADOS",
            "TOTAL_SALAS_CLASES", "CAPACIDAD_SALAS_CLASES", "TOTAL_M2_SALAS_CLASES",
            "TOTAL_AUDITORIOS", "CAPACIDAD_AUDITORIOS", "TOTAL_M2_AUDITORIOS",
            "TOTAL_LABORATORIOS", "TOTAL_M2_LABORATORIOS",
            "TOTAL_TALLERES", "TOTAL_M2_TALLERES",
            "TOTAL_PC_NB_DISPONIBLE", "TOTAL_M2_CASINOS_CAFETERIAS", "TOTAL_M2_AREAS_VERDES"
        ]

        for campo in campos_obligatorios:
            valor = fila.get(campo, "").strip()
            if not valor:
                return f"TIPO 1: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO1_campos_obligatorios",
        descripcion="TIPO 1 debe tener campos obligatorios",
        severidad=Severidad.ERROR,
        validar=validar_tipo1_obligatorios,
    ))

    def validar_tipo1_funciones(fila: Dict) -> Optional[str]:
        """TIPO 1: al menos una función principal."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "1":
            return None

        funciones = ["FUNCION_DOCENCIA", "FUNCION_INVESTIGACION", "FUNCION_EXTENSION",
                     "FUNCION_ADM_OFICINAS", "FUNCION_OTRAS"]
        tiene_funcion = any(fila.get(f, "").strip() == "X" for f in funciones)

        return None if tiene_funcion else "TIPO 1: debe tener al menos una función principal"

    reglas.append(Regla(
        id="TIPO1_una_funcion",
        descripcion="TIPO 1 debe tener al menos una función",
        severidad=Severidad.ERROR,
        validar=validar_tipo1_funciones,
    ))

    def validar_tipo1_funcion_otras(fila: Dict) -> Optional[str]:
        """TIPO 1: FUNCION_OTRAS ⟺ DESC_OTRAS_FUNCIONES."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "1":
            return None

        tiene_x = fila.get("FUNCION_OTRAS", "").strip() == "X"
        tiene_desc = fila.get("DESC_OTRAS_FUNCIONES", "").strip()

        if tiene_x and not tiene_desc:
            return "TIPO 1: FUNCION_OTRAS=X requiere DESC_OTRAS_FUNCIONES"
        if tiene_desc and not tiene_x:
            return "TIPO 1: DESC_OTRAS_FUNCIONES requiere FUNCION_OTRAS=X"

        return None

    reglas.append(Regla(
        id="TIPO1_funcion_otras_coherencia",
        descripcion="FUNCION_OTRAS ⟺ DESC_OTRAS_FUNCIONES",
        severidad=Severidad.ERROR,
        validar=validar_tipo1_funcion_otras,
    ))

    # ============ TIPO 2 — Inmueble de Uso Restringido ============

    def validar_tipo2_obligatorios(fila: Dict) -> Optional[str]:
        """TIPO 2 requiere UR_* obligatorios."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "2":
            return None

        campos_obligatorios = ["UR_DESC_ACTIVIDADES", "UR_TOTAL_M2_TERRENO",
                               "UR_TOTAL_M2_CONSTRUIDOS", "UR_SITUACION_TENENCIA"]

        for campo in campos_obligatorios:
            valor = fila.get(campo, "").strip()
            if not valor:
                return f"TIPO 2: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO2_campos_obligatorios",
        descripcion="TIPO 2 debe tener campos UR_* obligatorios",
        severidad=Severidad.ERROR,
        validar=validar_tipo2_obligatorios,
    ))

    # ============ TIPO 3 — Biblioteca ============

    def validar_tipo3_obligatorios(fila: Dict) -> Optional[str]:
        """TIPO 3 requiere campos de biblioteca."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "3":
            return None

        campos_obligatorios = ["TOTAL_M2_BIBLIOTECA", "TOTAL_M2_SALAS_LECTURA",
                               "TOTAL_PROFESIONALES_BIBLIOTECA", "HORAS_PERSONAL_BIBLIOTECA",
                               "TOTAL_TITULOS_DISPONIBLES", "TOTAL_VOLUMENES_DISPONIBLES",
                               "TOTAL_SUSCRIPCIONES_REVISTAS"]

        for campo in campos_obligatorios:
            valor = fila.get(campo, "").strip()
            if not valor:
                return f"TIPO 3: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO3_campos_obligatorios",
        descripcion="TIPO 3 debe tener campos de biblioteca",
        severidad=Severidad.ERROR,
        validar=validar_tipo3_obligatorios,
    ))

    # ============ TIPO 4 — Digital ============

    def validar_tipo4_obligatorios(fila: Dict) -> Optional[str]:
        """TIPO 4 requiere campos digitales."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "4":
            return None

        campos_obligatorios = ["TOTAL_TITULOS_LIBROS_DIGITALES",
                               "TOTAL_SUSCRIPCIONES_DIGITALES", "TOTAL_BASE_DATOS"]

        for campo in campos_obligatorios:
            valor = fila.get(campo, "").strip()
            if not valor:
                return f"TIPO 4: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO4_campos_obligatorios",
        descripcion="TIPO 4 debe tener campos digitales",
        severidad=Severidad.ERROR,
        validar=validar_tipo4_obligatorios,
    ))

    # ============ TIPO 5 — Predio ============

    def validar_tipo5_obligatorios(fila: Dict) -> Optional[str]:
        """TIPO 5 requiere TOTAL_HECTAREAS_PREDIO."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "5":
            return None

        valor = fila.get("TOTAL_HECTAREAS_PREDIO", "").strip()
        return None if valor else "TIPO 5: TOTAL_HECTAREAS_PREDIO obligatorio pero vacío"

    reglas.append(Regla(
        id="TIPO5_campos_obligatorios",
        descripcion="TIPO 5 debe tener TOTAL_HECTAREAS_PREDIO",
        severidad=Severidad.ERROR,
        validar=validar_tipo5_obligatorios,
    ))

    # ============ TIPO 6 — Plataforma Virtual ============

    def validar_tipo6_obligatorios(fila: Dict) -> Optional[str]:
        """TIPO 6 requiere campos de plataforma."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "6":
            return None

        campos_obligatorios = ["SISTEMA_GESTION_APRENDIZAJES", "SISTEMA_VIDEO_CONFERENCIA",
                               "SISTEMA_APLICACION_EVALUACION", "DESCRIPCION_PLATAFORMA_VIRTUAL"]

        for campo in campos_obligatorios:
            valor = fila.get(campo, "").strip()
            if not valor:
                return f"TIPO 6: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO6_campos_obligatorios",
        descripcion="TIPO 6 debe tener campos de plataforma",
        severidad=Severidad.ERROR,
        validar=validar_tipo6_obligatorios,
    ))

    def validar_tipo6_descripcion_longitud(fila: Dict) -> Optional[str]:
        """TIPO 6: DESCRIPCION_PLATAFORMA_VIRTUAL ≤ 1000 caracteres."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "6":
            return None

        desc = fila.get("DESCRIPCION_PLATAFORMA_VIRTUAL", "")
        if len(desc) > 1000:
            return f"TIPO 6: DESCRIPCION_PLATAFORMA_VIRTUAL excede 1000 caracteres ({len(desc)})"

        return None

    reglas.append(Regla(
        id="TIPO6_descripcion_longitud",
        descripcion="DESCRIPCION_PLATAFORMA_VIRTUAL ≤ 1000 caracteres",
        severidad=Severidad.ERROR,
        validar=validar_tipo6_descripcion_longitud,
    ))

    # ============ Consistencias aritméticas ============

    def validar_aritmética_salas(fila: Dict) -> Optional[str]:
        """TOTAL_M2_SALAS_CLASES ≤ TOTAL_M2_EDIFICADOS (TIPO 1)."""
        if fila.get("TIPO_INFRAESTRUCTURA") != "1":
            return None

        try:
            salas = float(fila.get("TOTAL_M2_SALAS_CLASES", 0) or 0)
            edificados = float(fila.get("TOTAL_M2_EDIFICADOS", 0) or 0)

            if salas > edificados:
                return f"M² salas ({salas}) > M² edificados ({edificados})"
        except (ValueError, TypeError):
            pass

        return None

    reglas.append(Regla(
        id="ARITMÉTICA_salas_vs_edificados",
        descripcion="M² salas ≤ M² edificados",
        severidad=Severidad.ADVERTENCIA,
        validar=validar_aritmética_salas,
    ))

    # ============ Identidad (llave única) ============

    reglas.append(Regla(
        id="IDENTIDAD_llave_global",
        descripcion="Llave única será verificada al nivel de conjunto de filas",
        severidad=Severidad.ERROR,
        validar=lambda fila: None,  # Verificada post-lectura
    ))

    return reglas


def obtener_reglas() -> list:
    """Obtener lista de reglas."""
    return crear_reglas()
