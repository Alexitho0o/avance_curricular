"""Indicadores derivados IRE 2026. Denominador: matrícula jornada principal."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Optional


# Serie histórica 2023-2025 (§4 del encargo). Claves ausentes = dato no informado
# en la fuente original para ese año; no se inventa, se deja fuera del dict.
SERIE_HISTORICA: Dict[int, Dict] = {
    2023: {
        "matricula": 220,
        "m2_terreno": 1280,
        "m2_edificados": 1360.8,
        "m2_areas_verdes": 440.9,
        "m2_talleres": 292.1,
        "m2_laboratorios": 0,
        "total_auditorios": 1,
        "total_pc_nb_disponible": 242,
        "total_talleres": 9,
        "total_salas_clases": 2,
        "total_laboratorios": 0,
        "total_titulos_libros_digitales": 62391,
        "lms": "MOODLE 4.0.12",
        "videoconferencia": "ZOOM / TEAMS",
        "razon_social": "INSTITUTO PROFESIONAL CIISA",
    },
    2024: {
        "matricula": 160,
        "m2_terreno": 789,
        "m2_edificados": 1362,
        "m2_areas_verdes": 440.9,
        "m2_talleres": 292.1,
        "m2_laboratorios": 0,
        "total_auditorios": 1,
        "total_pc_nb_disponible": 252,
        "total_talleres": 9,
        "total_salas_clases": 5,
        "total_laboratorios": 0,
        "total_titulos_libros_digitales": 63189,
        "lms": "MOODLE 4.0.12",
        "videoconferencia": "ZOOM / TEAMS",
        "razon_social": "INSTITUTO PROFESIONAL SAN SEBASTIAN",
    },
    2025: {
        "matricula": 248,
        "m2_terreno": 789,
        "m2_edificados": 1362,
        "m2_areas_verdes": 440.9,
        "m2_talleres": 292.1,
        "m2_laboratorios": 0,
        "total_auditorios": 1,
        "total_pc_nb_disponible": 252,
        "total_talleres": 9,
        "total_salas_clases": 5,
        "capacidad_salas_clases": 141,
        "total_volumenes_disponibles": 705,
        "total_titulos_disponibles": 705,
        "total_suscripciones_revistas": 0,
        "horas_personal_biblioteca": 44,
        "total_titulos_libros_digitales": 63755,
        "total_suscripciones_digitales": 1,
        "total_base_datos": 0,
        "lms": "MOODLE 4.4.4",
        "videoconferencia": "MICROSOFT TEAMS",
        "razon_social": "INSTITUTO PROFESIONAL SAN SEBASTIAN",
    },
    2026: {
        # ---- PROCEDENCIA (registro raw verificado) ----
        # ARCHIVO: PARA_SUBIR_DESKTOP__matricula_unificada_2026_pregrado_PARA_SUBIR.csv
        # COMMIT_QUE_LO_AGREGO: 4f1108c
        # RAMA: respaldo/ire-2026-sucio-20260722_2259  (NO BORRAR: unica fuente)
        # SHA256: 8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704
        # FECHA_VERIFICACION: 2026-07-22
        # CRITERIO: VIG=1 AND MODALIDAD=1 AND JOR IN (1,2)
        # MODALIDAD: 1=Presencial, 3=A distancia
        # JOR: 1=Diurno, 2=Vespertino, 4=Virtual (solo con MOD=3)
        # TOTAL_FILAS: 4070 | VIG_1: 3110 | VIG_0: 960
        # PRESENCIAL_DIURNO: 193 | PRESENCIAL_VESPERTINO: 497
        # DENOMINADOR: 690 | ONLINE_EXCLUIDOS: 2420
        "matricula": 690,
    },
}


def _dividir(numerador: Optional[float], denominador: Optional[float]) -> Optional[float]:
    """División segura: retorna None si falta algún operando o el denominador es 0."""
    if numerador is None or denominador is None or denominador == 0:
        return None
    return numerador / denominador


def calcular_indicadores(datos: Dict) -> Dict[str, Optional[float]]:
    """
    Calcular los 9 indicadores derivados para un año dado.

    Args:
        datos: dict con matricula y magnitudes crudas del año (ver SERIE_HISTORICA).
               Claves ausentes producen indicador None (no se inventa dato).

    Returns:
        dict con los 9 indicadores en precisión completa (sin redondear).
    """
    if "matricula" not in datos:
        raise ValueError("'matricula' es obligatoria como denominador de todos los KPI")

    matricula = datos["matricula"]

    m2_talleres = datos.get("m2_talleres")
    m2_laboratorios = datos.get("m2_laboratorios")
    talleres_lab = None
    if m2_talleres is not None and m2_laboratorios is not None:
        talleres_lab = m2_talleres + m2_laboratorios

    return {
        "m2_construidos_por_estudiante": _dividir(datos.get("m2_edificados"), matricula),
        "m2_areas_verdes_por_estudiante": _dividir(datos.get("m2_areas_verdes"), matricula),
        "m2_talleres_lab_por_estudiante": _dividir(talleres_lab, matricula),
        "computadores_por_estudiante": _dividir(datos.get("total_pc_nb_disponible"), matricula),
        "capacidad_salas_por_estudiante": _dividir(datos.get("capacidad_salas_clases"), matricula),
        "volumenes_fisicos_por_estudiante": _dividir(datos.get("total_volumenes_disponibles"), matricula),
        "ebooks_por_estudiante": _dividir(datos.get("total_titulos_libros_digitales"), matricula),
        "horas_bibliotecario_por_100_estudiantes": _dividir(
            datos.get("horas_personal_biblioteca"), matricula / 100 if matricula else None
        ),
        "tasa_ocupacion_salas": _dividir(matricula, datos.get("capacidad_salas_clases")),
    }


def calcular_serie_historica() -> Dict[int, Dict[str, Optional[float]]]:
    """Calcular indicadores derivados para cada año de SERIE_HISTORICA."""
    return {anio: calcular_indicadores(datos) for anio, datos in SERIE_HISTORICA.items()}


def calcular_variacion(valor_actual: Optional[float], valor_anterior: Optional[float]) -> Dict[str, Optional[float]]:
    """
    Calcular variación interanual absoluta y porcentual.

    Returns:
        {"absoluta": ..., "porcentual": ...} o None en ambos si falta algún dato.
    """
    if valor_actual is None or valor_anterior is None:
        return {"absoluta": None, "porcentual": None}

    absoluta = valor_actual - valor_anterior
    porcentual = (absoluta / valor_anterior * 100) if valor_anterior != 0 else None

    return {"absoluta": absoluta, "porcentual": porcentual}


def redondear_presentacion(valor: Optional[float], decimales: int = 2) -> Optional[float]:
    """Redondear solo al momento de presentar (nunca durante el cálculo)."""
    if valor is None:
        return None
    return round(valor, decimales)
