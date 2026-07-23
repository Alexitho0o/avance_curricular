"""Motor genérico de validación: Regla, Severidad, Resultado, ejecutar()."""

from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional, List, Dict


class Severidad(Enum):
    """Niveles de severidad de una regla."""
    ERROR = "ERROR"       # Bloquea generación
    ADVERTENCIA = "ADVERTENCIA"  # Solo informa


@dataclass
class Regla:
    """Definición de una regla de validación."""
    id: str
    descripcion: str
    severidad: Severidad
    validar: Callable[[Dict], Optional[str]]  # Retorna None si OK, mensaje si falla


@dataclass
class Resultado:
    """Resultado de ejecutar una regla sobre una fila."""
    regla_id: str
    fila_indice: int
    es_valido: bool
    severidad: Severidad
    mensaje: Optional[str] = None


def ejecutar(
    reglas: List[Regla],
    filas: List[Dict],
    detener_en_error: bool = False,
) -> tuple[List[Resultado], bool]:
    """
    Ejecutar un conjunto de reglas sobre todas las filas.

    Args:
        reglas: Lista de Regla
        filas: Lista de diccionarios (fila)
        detener_en_error: Si True, parar en el primer ERROR

    Returns:
        (lista_resultados, sin_errores)
        sin_errores: True si no hay errores (ADVERTENCIA no cuenta)
    """
    resultados = []
    sin_errores = True

    for indice, fila in enumerate(filas):
        for regla in reglas:
            try:
                mensaje = regla.validar(fila)
                es_valido = mensaje is None

                resultado = Resultado(
                    regla_id=regla.id,
                    fila_indice=indice,
                    es_valido=es_valido,
                    severidad=regla.severidad,
                    mensaje=mensaje,
                )
                resultados.append(resultado)

                if not es_valido:
                    if regla.severidad == Severidad.ERROR:
                        sin_errores = False
                        if detener_en_error:
                            return resultados, sin_errores

            except Exception as e:
                # Error interno en la regla
                resultado = Resultado(
                    regla_id=regla.id,
                    fila_indice=indice,
                    es_valido=False,
                    severidad=Severidad.ERROR,
                    mensaje=f"Excepción: {str(e)}",
                )
                resultados.append(resultado)
                sin_errores = False
                if detener_en_error:
                    return resultados, sin_errores

    return resultados, sin_errores


def agrupar_por_severidad(resultados: List[Resultado]) -> Dict[Severidad, List[Resultado]]:
    """Agrupar resultados inválidos por severidad."""
    por_severidad = {Severidad.ERROR: [], Severidad.ADVERTENCIA: []}
    for r in resultados:
        # Solo agrupar resultados que fallaron (es_valido=False)
        if not r.es_valido and r.severidad in por_severidad:
            por_severidad[r.severidad].append(r)
    return por_severidad


def filtrar_invalidos(resultados: List[Resultado]) -> List[Resultado]:
    """Retornar solo los resultados que fallaron (es_valido=False)."""
    return [r for r in resultados if not r.es_valido]
