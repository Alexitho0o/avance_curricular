"""Carga y aplicación del contrato de configuración 2026 (§7 del encargo)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from typing import Dict, List, Tuple


RAIZ_PROCESO = Path(__file__).parent.parent
RUTA_INSTITUCION = RAIZ_PROCESO / "config" / "institucion.yaml"
RUTA_PARAMETROS = RAIZ_PROCESO / "config" / "parametros_2026.yaml"

# Claves bloqueantes: si siguen en null, el pipeline se detiene (no heredan de 2025)
CLAVES_BLOQUEANTES = [
    "matricula_jornada_principal_2026",
    ("tenencia", "fecha_inicio"),
    ("tenencia", "fecha_termino"),
    "uso_restringido_uss_vigente",
]

# Mapeo clave de config (minusculas) -> nombre de columna del schema (TIPO 1)
MAPEO_INMUEBLE_PERMANENTE = {
    "total_m2_terreno": "TOTAL_M2_TERRENO",
    "total_m2_edificados": "TOTAL_M2_EDIFICADOS",
    "total_salas_clases": "TOTAL_SALAS_CLASES",
    "capacidad_salas_clases": "CAPACIDAD_SALAS_CLASES",
    "total_m2_salas_clases": "TOTAL_M2_SALAS_CLASES",
    "total_auditorios": "TOTAL_AUDITORIOS",
    "capacidad_auditorios": "CAPACIDAD_AUDITORIOS",
    "total_m2_auditorios": "TOTAL_M2_AUDITORIOS",
    "total_laboratorios": "TOTAL_LABORATORIOS",
    "total_m2_laboratorios": "TOTAL_M2_LABORATORIOS",
    "total_talleres": "TOTAL_TALLERES",
    "total_m2_talleres": "TOTAL_M2_TALLERES",
    "total_pc_nb_disponible": "TOTAL_PC_NB_DISPONIBLE",
    "total_m2_casinos_cafeterias": "TOTAL_M2_CASINOS_CAFETERIAS",
    "total_m2_areas_verdes": "TOTAL_M2_AREAS_VERDES",
}

MAPEO_BIBLIOTECA = {
    "total_m2_biblioteca": "TOTAL_M2_BIBLIOTECA",
    "total_m2_salas_lectura": "TOTAL_M2_SALAS_LECTURA",
    "total_profesionales": "TOTAL_PROFESIONALES_BIBLIOTECA",
    "horas_personal": "HORAS_PERSONAL_BIBLIOTECA",
    "total_titulos": "TOTAL_TITULOS_DISPONIBLES",
    "total_volumenes": "TOTAL_VOLUMENES_DISPONIBLES",
    "total_suscripciones_revistas": "TOTAL_SUSCRIPCIONES_REVISTAS",
}

MAPEO_DIGITAL = {
    "total_titulos_libros_digitales": "TOTAL_TITULOS_LIBROS_DIGITALES",
    "total_suscripciones_digitales": "TOTAL_SUSCRIPCIONES_DIGITALES",
    "total_base_datos": "TOTAL_BASE_DATOS",
}

MAPEO_PLATAFORMAS = {
    "lms": "SISTEMA_GESTION_APRENDIZAJES",
    "videoconferencia": "SISTEMA_VIDEO_CONFERENCIA",
    "evaluacion": "SISTEMA_APLICACION_EVALUACION",
    "descripcion": "DESCRIPCION_PLATAFORMA_VIRTUAL",
}


class ConfiguracionIncompleta(Exception):
    """Error accionable: falta una clave requerida en la configuración."""
    pass


def cargar_institucion() -> Dict:
    """Cargar config/institucion.yaml."""
    with open(RUTA_INSTITUCION, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def cargar_parametros() -> Dict:
    """Cargar config/parametros_2026.yaml."""
    with open(RUTA_PARAMETROS, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _obtener(d: Dict, clave):
    """Obtener valor de clave simple o tupla (anidada)."""
    if isinstance(clave, tuple):
        actual = d
        for parte in clave:
            if not isinstance(actual, dict) or parte not in actual:
                return None
            actual = actual[parte]
        return actual
    return d.get(clave)


def _nombre_clave(clave) -> str:
    return ".".join(clave) if isinstance(clave, tuple) else clave


def verificar_claves_bloqueantes(parametros: Dict) -> None:
    """
    Verificar que ninguna clave bloqueante siga en null.

    Raises:
        ConfiguracionIncompleta: con mensaje claro nombrando la clave y el archivo.
    """
    faltantes = []
    for clave in CLAVES_BLOQUEANTES:
        valor = _obtener(parametros, clave)
        if valor is None:
            faltantes.append(_nombre_clave(clave))

    if faltantes:
        lista = "\n".join(f"  - {c}" for c in faltantes)
        raise ConfiguracionIncompleta(
            f"No se puede generar el CSV de carga: faltan claves requeridas en "
            f"'config/parametros_2026.yaml' (no admiten herencia silenciosa de 2025):\n"
            f"{lista}\n\n"
            f"Completa estas claves en config/parametros_2026.yaml y vuelve a ejecutar."
        )


def aplicar_herencias(parametros: Dict, filas: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Aplicar el contrato de configuración sobre las filas del input.

    - Claves bloqueantes ya verificadas: se aplican directamente (tenencia,
      uso_restringido_uss_vigente).
    - Claves de inmueble_permanente/biblioteca/digital/plataformas: si son
      explícitas (no null), sobrescriben la fila; si son null, se conserva
      el valor ya presente en el input (2025) y se registra la herencia.

    Returns:
        (filas_actualizadas, log_herencias)
    """
    log_herencias = []

    tenencia = parametros.get("tenencia", {}) or {}
    fecha_inicio = tenencia.get("fecha_inicio")
    fecha_termino = tenencia.get("fecha_termino")
    uso_uss_vigente = parametros.get("uso_restringido_uss_vigente")

    inmueble = parametros.get("inmueble_permanente", {}) or {}
    biblioteca = parametros.get("biblioteca", {}) or {}
    digital = parametros.get("digital", {}) or {}
    plataformas = parametros.get("plataformas", {}) or {}

    def aplicar_grupo(fila: Dict, grupo: Dict, mapeo: Dict, etiqueta: str):
        for clave_config, columna in mapeo.items():
            valor = grupo.get(clave_config)
            if valor is not None:
                fila[columna] = str(valor)
            else:
                log_herencias.append(
                    f"{etiqueta}.{clave_config} ({columna}): heredado de 2025, no confirmado para 2026"
                )

    for fila in filas:
        tipo = fila.get("TIPO_INFRAESTRUCTURA", "").strip()

        if tipo == "1":
            fila["FECHA_INICIO_TENENCIA"] = str(fecha_inicio)
            fila["FECHA_TERMINO"] = str(fecha_termino)
            aplicar_grupo(fila, inmueble, MAPEO_INMUEBLE_PERMANENTE, "inmueble_permanente")

        elif tipo == "2":
            # Convenio USS Los Leones: vigente sigue VIGENCIA=1, si no, VIGENCIA=0
            fila["VIGENCIA"] = "1" if uso_uss_vigente else "0"

        elif tipo == "3":
            aplicar_grupo(fila, biblioteca, MAPEO_BIBLIOTECA, "biblioteca")

        elif tipo == "4":
            aplicar_grupo(fila, digital, MAPEO_DIGITAL, "digital")

        elif tipo == "6":
            aplicar_grupo(fila, plataformas, MAPEO_PLATAFORMAS, "plataformas")

    return filas, log_herencias


def aplicar_convenios_nuevos(parametros: Dict, filas: List[Dict], columnas: List[str]) -> List[Dict]:
    """Agregar registros TIPO 2 adicionales desde parametros_2026.yaml."""
    convenios = parametros.get("convenios_nuevos") or []
    for convenio in convenios:
        fila = {col: "" for col in columnas}
        fila["TIPO_INFRAESTRUCTURA"] = "2"
        fila["VIGENCIA"] = "1"
        fila.update({k: str(v) for k, v in convenio.items()})
        filas.append(fila)
    return filas


def aplicar_predios(parametros: Dict, filas: List[Dict], columnas: List[str]) -> List[Dict]:
    """Agregar registros TIPO 5 (predios) desde parametros_2026.yaml."""
    predios = parametros.get("predios") or []
    for predio in predios:
        fila = {col: "" for col in columnas}
        fila["TIPO_INFRAESTRUCTURA"] = "5"
        fila["VIGENCIA"] = "1"
        fila.update({k: str(v) for k, v in predio.items()})
        filas.append(fila)
    return filas


def aplicar_eliminaciones(parametros: Dict, filas: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Marcar VIGENCIA=0 en filas que coincidan con registros_a_eliminar."""
    eliminaciones = parametros.get("registros_a_eliminar") or []
    log = []

    for elim in eliminaciones:
        llave_buscada = (
            str(elim.get("tipo_infraestructura", "")),
            elim.get("nombre_identificacion", "").strip().upper(),
            elim.get("comuna", "").strip().upper(),
            elim.get("direccion_inmueble", "").strip().upper(),
        )
        encontrado = False
        for fila in filas:
            llave_fila = (
                fila.get("TIPO_INFRAESTRUCTURA", "").strip(),
                fila.get("NOMBRE_IDENTIFICACION", "").strip().upper(),
                fila.get("COMUNA", "").strip().upper(),
                fila.get("DIRECCION_INMUEBLE", "").strip().upper(),
            )
            if llave_fila == llave_buscada:
                fila["VIGENCIA"] = "0"
                log.append(f"Marcado VIGENCIA=0: {llave_buscada}")
                encontrado = True
                break

        if not encontrado:
            log.append(f"ADVERTENCIA: registro a eliminar no encontrado en el dataset: {llave_buscada}")

    return filas, log
