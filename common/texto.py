"""Normalización de texto: mayúsculas, quitar acentos, limpiar especiales."""

import unicodedata
import re


def normalizar(texto: str) -> str:
    """
    Normalizar a mayúsculas, sin acentos, sin espacios en blanco especiales.
    Limpia \xa0 (non-breaking space) y espacios múltiples.
    """
    if not isinstance(texto, str) or not texto.strip():
        return ""

    # Convertir a mayúsculas
    texto = texto.upper().strip()

    # Remover \xa0 (non-breaking space)
    texto = texto.replace('\xa0', ' ')

    # Normalizar acentos: descomponer y descartar marcas diacríticas
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    # Limpiar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)

    return texto.strip()


def limpiar_numero_texto(valor: str) -> float or str:
    """
    Si es un número guardado como texto ('168.2', '292.1'), convertir a float.
    Si no es número, retornar el valor limpio.
    """
    if not isinstance(valor, str):
        return valor

    valor_limpio = valor.strip()
    try:
        return float(valor_limpio)
    except ValueError:
        return valor_limpio


def sin_acentos_ascii(texto: str) -> str:
    """Versión estricta: solo A-Z, 0-9 y espacios. Útil para nombres únicos."""
    texto = normalizar(texto)
    # Remover caracteres no ASCII, excepto espacios y números
    texto = re.sub(r'[^A-Z0-9\s]', '', texto)
    # Limpiar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto
