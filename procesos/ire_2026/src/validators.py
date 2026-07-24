"""Reglas de validación IRE 2026 (Anexo III)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import unicodedata
from typing import Optional, Dict, List
from common.validacion import Regla, Severidad
from src.schema import ESPECIFICACION, COLUMNAS, CAMPOS_UN_DECIMAL


# ---------- Helpers de tipo ----------

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
    """Verificar formato AAAA-MM (mes 01-12)."""
    if not valor or not isinstance(valor, str):
        return False
    return re.match(r'^\d{4}-(0[1-9]|1[0-2])$', valor.strip()) is not None


def sin_acentos_ni_especiales(texto: str) -> bool:
    """Verificar que no tenga acentos, ñ ni caracteres no ASCII."""
    if not isinstance(texto, str):
        return False
    nfkd = unicodedata.normalize('NFKD', texto)
    for c in nfkd:
        if unicodedata.category(c) == 'Mn':
            return False
    try:
        texto.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True


def _tipo(fila: Dict) -> Optional[int]:
    """Obtener TIPO_INFRAESTRUCTURA de la fila como entero, o None si inválido."""
    valor = fila.get("TIPO_INFRAESTRUCTURA", "")
    return int(valor) if es_entero(valor) else None


def _vacio(fila: Dict, campo: str) -> bool:
    return not fila.get(campo, "").strip()


# ---------- Reglas por fila ----------

def crear_reglas() -> List[Regla]:
    """Crear todas las reglas de validación por fila (Anexo III)."""
    reglas = []

    # ============ TRANSVERSALES ============

    reglas.append(Regla(
        id="TIPO_INFRAESTRUCTURA_valido",
        descripcion="TIPO_INFRAESTRUCTURA debe estar entre 1 y 6",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if (
            es_entero(fila.get("TIPO_INFRAESTRUCTURA", "")) and
            1 <= int(fila["TIPO_INFRAESTRUCTURA"]) <= 6
        ) else "TIPO_INFRAESTRUCTURA fuera de rango [1-6]",
    ))

    reglas.append(Regla(
        id="VIGENCIA_valido",
        descripcion="VIGENCIA debe ser 0 o 1",
        severidad=Severidad.ERROR,
        validar=lambda fila: None if (
            es_entero(fila.get("VIGENCIA", "")) and
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

    def validar_comuna_solo_letras(fila: Dict) -> Optional[str]:
        comuna = fila.get("COMUNA", "").strip()
        if not comuna:
            return None
        if not re.match(r'^[A-Za-z\s]+$', comuna):
            return f"COMUNA debe contener solo letras y espacios: '{comuna}'"
        return None

    reglas.append(Regla(
        id="COMUNA_solo_letras",
        descripcion="COMUNA solo admite letras y espacios",
        severidad=Severidad.ERROR,
        validar=validar_comuna_solo_letras,
    ))

    # ============ G. Sanidad de caracteres ============

    def validar_sin_delimitador_ni_saltos(fila: Dict) -> Optional[str]:
        """Ningún valor puede contener ';' ni saltos de línea."""
        for campo, valor in fila.items():
            if not isinstance(valor, str):
                continue
            if ';' in valor:
                return f"{campo} contiene ';' (rompe el delimitador del CSV)"
            if '\n' in valor or '\r' in valor:
                return f"{campo} contiene salto de línea"
        return None

    reglas.append(Regla(
        id="SANIDAD_sin_delimitador_ni_saltos",
        descripcion="Ningún campo contiene ';' ni saltos de línea",
        severidad=Severidad.ERROR,
        validar=validar_sin_delimitador_ni_saltos,
    ))

    def validar_solo_ascii(fila: Dict) -> Optional[str]:
        """Todo texto debe ser ASCII: sin acentos, sin ñ, sin caracteres especiales."""
        for campo, valor in fila.items():
            if not isinstance(valor, str) or not valor.strip():
                continue
            if not sin_acentos_ni_especiales(valor):
                return f"{campo} contiene acentos, ñ u otro carácter no ASCII: '{valor}'"
        return None

    reglas.append(Regla(
        id="SANIDAD_solo_ascii",
        descripcion="Todo texto debe ser ASCII (sin acentos ni ñ)",
        severidad=Severidad.ERROR,
        validar=validar_solo_ascii,
    ))

    # ============ A. Reglas espejo: campos prohibidos por tipo ============

    def validar_campos_prohibidos(fila: Dict) -> Optional[str]:
        """Ningún campo que no aplique al TIPO de la fila puede venir con valor."""
        tipo = _tipo(fila)
        if tipo is None:
            return None

        for campo, spec in ESPECIFICACION.items():
            if tipo in spec["aplica"]:
                continue
            valor = fila.get(campo, "")
            if isinstance(valor, str) and valor.strip():
                return f"TIPO {tipo}: campo prohibido '{campo}' viene con valor '{valor}'"
        return None

    reglas.append(Regla(
        id="CAMPOS_PROHIBIDOS_por_tipo",
        descripcion="Campos no aplicables al TIPO deben venir vacíos (regla espejo)",
        severidad=Severidad.ERROR,
        validar=validar_campos_prohibidos,
    ))

    # ============ TIPO 1 — Inmueble de Uso Permanente ============

    def validar_tipo1_obligatorios(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
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
            if _vacio(fila, campo):
                return f"TIPO 1: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO1_campos_obligatorios",
        descripcion="TIPO 1 debe tener campos obligatorios",
        severidad=Severidad.ERROR,
        validar=validar_tipo1_obligatorios,
    ))

    def validar_tipo1_funciones(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
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
        if _tipo(fila) != 1:
            return None

        tiene_x = fila.get("FUNCION_OTRAS", "").strip() == "X"
        tiene_desc = bool(fila.get("DESC_OTRAS_FUNCIONES", "").strip())

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

    # ---- B. Condicionales de tenencia (solo TIPO 1) ----

    def validar_tenencia_condicional(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
            return None

        situacion = fila.get("SITUACION_TENENCIA", "").strip()
        if not es_entero(situacion):
            return None  # Ya cubierto por TIPO1_campos_obligatorios
        situacion = int(situacion)

        fecha_inicio = fila.get("FECHA_INICIO_TENENCIA", "").strip()
        fecha_termino = fila.get("FECHA_TERMINO", "").strip()
        desc_otra = fila.get("DESCRIPCION_OTRA_TENENCIA", "").strip()

        if situacion == 1:  # Propio
            if fecha_inicio or fecha_termino or desc_otra:
                return "SITUACION_TENENCIA=1 (Propio): FECHA_INICIO_TENENCIA, FECHA_TERMINO y DESCRIPCION_OTRA_TENENCIA deben estar vacíos"
        elif situacion in (2, 4, 5):  # Arrendado, Usufructo, Leasing
            if not fecha_termino:
                return f"SITUACION_TENENCIA={situacion}: FECHA_TERMINO obligatoria"
            if desc_otra:
                return f"SITUACION_TENENCIA={situacion}: DESCRIPCION_OTRA_TENENCIA debe estar vacía"
        elif situacion == 3:  # Comodato
            if not fecha_inicio:
                return "SITUACION_TENENCIA=3 (Comodato): FECHA_INICIO_TENENCIA obligatoria"
            if not fecha_termino:
                return "SITUACION_TENENCIA=3 (Comodato): FECHA_TERMINO obligatoria"
            if desc_otra:
                return "SITUACION_TENENCIA=3 (Comodato): DESCRIPCION_OTRA_TENENCIA debe estar vacía"
        elif situacion == 6:  # Otro
            if not desc_otra:
                return "SITUACION_TENENCIA=6 (Otro): DESCRIPCION_OTRA_TENENCIA obligatoria"

        # Regla general: 2-6 requieren FECHA_INICIO_TENENCIA
        if situacion in (2, 3, 4, 5, 6) and not fecha_inicio:
            return f"SITUACION_TENENCIA={situacion}: FECHA_INICIO_TENENCIA obligatoria"

        return None

    reglas.append(Regla(
        id="TENENCIA_condicional",
        descripcion="Campos de tenencia condicionales según SITUACION_TENENCIA",
        severidad=Severidad.ERROR,
        validar=validar_tenencia_condicional,
    ))

    # ---- C. Formatos y ventanas de fecha ----

    def validar_formato_fechas(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
            return None

        for campo in ["FECHA_INICIO_TENENCIA", "FECHA_TERMINO"]:
            valor = fila.get(campo, "").strip()
            if valor and not es_fecha_aaaa_mm(valor):
                return f"{campo} no tiene formato AAAA-MM: '{valor}'"
        return None

    reglas.append(Regla(
        id="FECHA_formato_aaaa_mm",
        descripcion="Fechas de tenencia deben tener formato AAAA-MM",
        severidad=Severidad.ERROR,
        validar=validar_formato_fechas,
    ))

    def validar_ventana_fechas(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
            return None

        fecha_inicio = fila.get("FECHA_INICIO_TENENCIA", "").strip()
        fecha_termino = fila.get("FECHA_TERMINO", "").strip()

        if fecha_inicio and es_fecha_aaaa_mm(fecha_inicio):
            if fecha_inicio >= "2026-07":
                return f"FECHA_INICIO_TENENCIA debe ser anterior a 2026-07: '{fecha_inicio}'"

        if fecha_termino and es_fecha_aaaa_mm(fecha_termino):
            if fecha_termino <= "2026-05":
                return f"FECHA_TERMINO debe ser posterior a 2026-05: '{fecha_termino}'"

        return None

    reglas.append(Regla(
        id="FECHA_ventana_valida",
        descripcion="FECHA_INICIO_TENENCIA < 2026-07 y FECHA_TERMINO > 2026-05",
        severidad=Severidad.ERROR,
        validar=validar_ventana_fechas,
    ))

    def validar_anio_inicio_uso(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
            return None

        valor = fila.get("ANIO_INICIO_USO_INMUEBLE", "").strip()
        if not valor or not es_entero(valor):
            return None  # Cubierto por obligatorios

        anio = int(valor)
        if not (1800 <= anio <= 2026):
            return f"ANIO_INICIO_USO_INMUEBLE fuera de rango [1800-2026]: {anio}"
        return None

    reglas.append(Regla(
        id="ANIO_INICIO_USO_INMUEBLE_rango",
        descripcion="ANIO_INICIO_USO_INMUEBLE entre 1800 y 2026",
        severidad=Severidad.ERROR,
        validar=validar_anio_inicio_uso,
    ))

    # ---- D. Uso compartido (solo TIPO 1) ----

    def validar_uso_compartido(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
            return None

        uso_exclusivo = fila.get("USO_EXCLUSIVO", "").strip()
        if not es_entero(uso_exclusivo):
            return None  # Cubierto por obligatorios

        uso_exclusivo = int(uso_exclusivo)
        porcentaje = fila.get("PORCENTAJE_USO", "").strip()
        institucion = fila.get("NOMBRE_INSTITUCION_COMPARTE", "").strip()

        if uso_exclusivo == 2:  # Compartido
            if not porcentaje:
                return "USO_EXCLUSIVO=2 (Compartido): PORCENTAJE_USO obligatorio"
            if not es_entero(porcentaje) or not (1 <= int(porcentaje) <= 99):
                return f"PORCENTAJE_USO fuera de rango [1-99]: '{porcentaje}'"
            if not institucion:
                return "USO_EXCLUSIVO=2 (Compartido): NOMBRE_INSTITUCION_COMPARTE obligatorio"
        elif uso_exclusivo == 1:  # Exclusivo
            if porcentaje or institucion:
                return "USO_EXCLUSIVO=1 (Exclusivo): PORCENTAJE_USO y NOMBRE_INSTITUCION_COMPARTE deben estar vacíos"

        return None

    reglas.append(Regla(
        id="USO_EXCLUSIVO_condicional",
        descripcion="PORCENTAJE_USO y NOMBRE_INSTITUCION_COMPARTE según USO_EXCLUSIVO",
        severidad=Severidad.ERROR,
        validar=validar_uso_compartido,
    ))

    # ============ TIPO 2 — Inmueble de Uso Restringido ============

    def validar_tipo2_obligatorios(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 2:
            return None

        campos_obligatorios = ["UR_DESC_ACTIVIDADES", "UR_TOTAL_M2_TERRENO",
                               "UR_TOTAL_M2_CONSTRUIDOS", "UR_SITUACION_TENENCIA"]

        for campo in campos_obligatorios:
            if _vacio(fila, campo):
                return f"TIPO 2: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO2_campos_obligatorios",
        descripcion="TIPO 2 debe tener campos UR_* obligatorios",
        severidad=Severidad.ERROR,
        validar=validar_tipo2_obligatorios,
    ))

    # ---- E. UR_SITUACION_TENENCIA (TIPO 2) ----

    def validar_ur_situacion_tenencia(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 2:
            return None

        valor = fila.get("UR_SITUACION_TENENCIA", "").strip()
        if not valor or not es_entero(valor):
            return None  # Cubierto por obligatorios

        valor = int(valor)
        if valor not in (1, 2):
            return f"UR_SITUACION_TENENCIA debe ser 1 o 2: {valor}"

        desc_otra = fila.get("UR_DESC_TENENCIA_OTRA", "").strip()
        if valor == 2 and not desc_otra:
            return "UR_SITUACION_TENENCIA=2 (Otra): UR_DESC_TENENCIA_OTRA obligatoria"
        if valor == 1 and desc_otra:
            return "UR_SITUACION_TENENCIA=1 (Arrendado): UR_DESC_TENENCIA_OTRA debe estar vacía"

        return None

    reglas.append(Regla(
        id="UR_SITUACION_TENENCIA_condicional",
        descripcion="UR_DESC_TENENCIA_OTRA según UR_SITUACION_TENENCIA",
        severidad=Severidad.ERROR,
        validar=validar_ur_situacion_tenencia,
    ))

    # ============ TIPO 3 — Biblioteca ============

    def validar_tipo3_obligatorios(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 3:
            return None

        campos_obligatorios = ["TOTAL_M2_BIBLIOTECA", "TOTAL_M2_SALAS_LECTURA",
                               "TOTAL_PROFESIONALES_BIBLIOTECA", "HORAS_PERSONAL_BIBLIOTECA",
                               "TOTAL_TITULOS_DISPONIBLES", "TOTAL_VOLUMENES_DISPONIBLES",
                               "TOTAL_SUSCRIPCIONES_REVISTAS"]

        for campo in campos_obligatorios:
            if _vacio(fila, campo):
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
        if _tipo(fila) != 4:
            return None

        campos_obligatorios = ["TOTAL_TITULOS_LIBROS_DIGITALES",
                               "TOTAL_SUSCRIPCIONES_DIGITALES", "TOTAL_BASE_DATOS"]

        for campo in campos_obligatorios:
            if _vacio(fila, campo):
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
        if _tipo(fila) != 5:
            return None

        return None if not _vacio(fila, "TOTAL_HECTAREAS_PREDIO") else "TIPO 5: TOTAL_HECTAREAS_PREDIO obligatorio pero vacío"

    reglas.append(Regla(
        id="TIPO5_campos_obligatorios",
        descripcion="TIPO 5 debe tener TOTAL_HECTAREAS_PREDIO",
        severidad=Severidad.ERROR,
        validar=validar_tipo5_obligatorios,
    ))

    # ============ TIPO 6 — Plataforma Virtual ============

    def validar_tipo6_obligatorios(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 6:
            return None

        campos_obligatorios = ["SISTEMA_GESTION_APRENDIZAJES", "SISTEMA_VIDEO_CONFERENCIA",
                               "SISTEMA_APLICACION_EVALUACION", "DESCRIPCION_PLATAFORMA_VIRTUAL"]

        for campo in campos_obligatorios:
            if _vacio(fila, campo):
                return f"TIPO 6: {campo} obligatorio pero vacío"

        return None

    reglas.append(Regla(
        id="TIPO6_campos_obligatorios",
        descripcion="TIPO 6 debe tener campos de plataforma",
        severidad=Severidad.ERROR,
        validar=validar_tipo6_obligatorios,
    ))

    def validar_tipo6_descripcion_longitud(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 6:
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

    # ============ H. Consistencias aritméticas (ahora ERROR) ============

    def validar_aritmética_salas(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 1:
            return None

        try:
            salas = float(fila.get("TOTAL_M2_SALAS_CLASES", "") or 0)
            edificados = float(fila.get("TOTAL_M2_EDIFICADOS", "") or 0)
            if salas > edificados:
                return f"M² salas ({salas}) > M² edificados ({edificados})"
        except (ValueError, TypeError):
            pass

        return None

    reglas.append(Regla(
        id="ARITMETICA_salas_vs_edificados",
        descripcion="M² salas ≤ M² edificados",
        severidad=Severidad.ERROR,
        validar=validar_aritmética_salas,
    ))

    def validar_aritmética_lectura(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 3:
            return None

        try:
            lectura = float(fila.get("TOTAL_M2_SALAS_LECTURA", "") or 0)
            biblioteca = float(fila.get("TOTAL_M2_BIBLIOTECA", "") or 0)
            if lectura > biblioteca:
                return f"M² salas de lectura ({lectura}) > M² biblioteca ({biblioteca})"
        except (ValueError, TypeError):
            pass

        return None

    reglas.append(Regla(
        id="ARITMETICA_lectura_vs_biblioteca",
        descripcion="M² salas de lectura ≤ M² biblioteca",
        severidad=Severidad.ERROR,
        validar=validar_aritmética_lectura,
    ))

    def validar_aritmética_titulos(fila: Dict) -> Optional[str]:
        if _tipo(fila) != 3:
            return None

        try:
            titulos = float(fila.get("TOTAL_TITULOS_DISPONIBLES", "") or 0)
            volumenes = float(fila.get("TOTAL_VOLUMENES_DISPONIBLES", "") or 0)
            if titulos > volumenes:
                return f"TOTAL_TITULOS_DISPONIBLES ({titulos}) > TOTAL_VOLUMENES_DISPONIBLES ({volumenes})"
        except (ValueError, TypeError):
            pass

        return None

    reglas.append(Regla(
        id="ARITMETICA_titulos_vs_volumenes",
        descripcion="TOTAL_TITULOS_DISPONIBLES ≤ TOTAL_VOLUMENES_DISPONIBLES",
        severidad=Severidad.ERROR,
        validar=validar_aritmética_titulos,
    ))

    # ============ Superficie: máximo 1 decimal (red de seguridad) ============
    # normalizar_decimales() en build_csv.py ya redondea antes de llegar aquí;
    # esta regla es el bloqueo si alguien edita el CSV a mano o cambia el
    # generador sin pasar por esa normalización.

    def _validar_decimales_superficie(fila: Dict) -> Optional[str]:
        for campo in CAMPOS_UN_DECIMAL:
            v = str(fila.get(campo, "")).strip()
            if not v or "." not in v:
                continue
            decimales = v.split(".", 1)[1]
            if len(decimales) > 1:
                return (
                    f"{campo}='{v}' tiene más de un decimal; "
                    f"PES exige máximo uno (rechaza con 'no cumple con estructura')"
                )
        return None

    reglas.append(Regla(
        id="SUPERFICIE_max_1_decimal",
        descripcion="Campos de superficie con máximo 1 decimal",
        severidad=Severidad.ERROR,
        validar=_validar_decimales_superficie,
    ))

    return reglas


# ---------- F. Validaciones a nivel de dataset ----------

def validar_dataset(filas: List[Dict]) -> List[str]:
    """
    Validar reglas que dependen del conjunto completo de filas.

    Returns:
        Lista de mensajes de error (vacía si todo OK).
    """
    errores = []

    # Llave única: TIPO + NOMBRE_IDENTIFICACION + COMUNA + DIRECCION_INMUEBLE
    llaves_vistas = {}
    for i, fila in enumerate(filas):
        llave = (
            fila.get("TIPO_INFRAESTRUCTURA", "").strip(),
            fila.get("NOMBRE_IDENTIFICACION", "").strip(),
            fila.get("COMUNA", "").strip(),
            fila.get("DIRECCION_INMUEBLE", "").strip(),
        )
        if llave in llaves_vistas:
            errores.append(
                f"Llave duplicada en filas {llaves_vistas[llave]} y {i}: {llave}"
            )
        else:
            llaves_vistas[llave] = i

    # Cardinalidad (TIPO 6 exactamente una, TIPO 1 al menos una): se evalúa solo
    # sobre filas VIGENTES (VIGENCIA=1). La carga es acumulativa (§0): una fila
    # VIGENCIA=0 es una instrucción de eliminación de un registro histórico
    # (p. ej. al cambiar de domicilio la casa central), no un segundo registro
    # activo, y no debe contar para estos límites.
    def _vigente(fila: Dict) -> bool:
        return fila.get("VIGENCIA", "").strip() == "1"

    # Exactamente una fila TIPO 6 vigente
    filas_tipo6_vigentes = [
        i for i, fila in enumerate(filas)
        if fila.get("TIPO_INFRAESTRUCTURA", "").strip() == "6" and _vigente(fila)
    ]
    if len(filas_tipo6_vigentes) == 0:
        errores.append("Debe existir exactamente una fila TIPO 6 vigente (Plataformas Virtuales); no hay ninguna")
    elif len(filas_tipo6_vigentes) > 1:
        errores.append(
            f"Debe existir exactamente una fila TIPO 6 vigente; se encontraron "
            f"{len(filas_tipo6_vigentes)} en filas {filas_tipo6_vigentes}"
        )

    # Al menos una fila TIPO 1 vigente
    filas_tipo1_vigentes = [
        i for i, fila in enumerate(filas)
        if fila.get("TIPO_INFRAESTRUCTURA", "").strip() == "1" and _vigente(fila)
    ]
    if len(filas_tipo1_vigentes) == 0:
        errores.append("Debe existir al menos una fila TIPO 1 vigente (Inmueble de Uso Permanente)")

    return errores


def obtener_reglas() -> List[Regla]:
    """Obtener lista de reglas por fila."""
    return crear_reglas()
