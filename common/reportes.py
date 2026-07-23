"""Helpers para salida md/docx y gráficos."""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json


def crear_reporte_md(
    titulo: str,
    secciones: List[Dict[str, str]],
    metadata: Optional[Dict] = None,
) -> str:
    """
    Crear reporte en Markdown.

    Args:
        titulo: Título principal
        secciones: Lista de {"titulo": str, "contenido": str}
        metadata: Diccionario con keys: fecha, autor, institución, etc.

    Returns:
        Texto del reporte en Markdown
    """
    lineas = []

    lineas.append(f"# {titulo}\n")

    if metadata:
        lineas.append("## Información General\n")
        for clave, valor in metadata.items():
            lineas.append(f"- **{clave}**: {valor}")
        lineas.append("")

    for seccion in secciones:
        lineas.append(f"## {seccion.get('titulo', 'Sin título')}\n")
        lineas.append(seccion.get('contenido', '') + "\n")

    return "\n".join(lineas)


def guardar_reporte_md(contenido: str, ruta: str) -> None:
    """Guardar reporte Markdown."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)


def tabla_markdown(
    encabezados: List[str],
    filas: List[List[str]],
) -> str:
    """
    Generar tabla Markdown.

    Args:
        encabezados: Lista de nombres de columna
        filas: Lista de listas de valores

    Returns:
        Tabla en formato Markdown
    """
    lineas = []

    # Encabezado
    lineas.append("| " + " | ".join(encabezados) + " |")
    lineas.append("|" + "|".join(["---"] * len(encabezados)) + "|")

    # Filas
    for fila in filas:
        lineas.append("| " + " | ".join(str(v) for v in fila) + " |")

    return "\n".join(lineas)


def guardar_json(datos: Dict, ruta: str) -> None:
    """Guardar datos como JSON."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def timestamp_archivo() -> str:
    """Retornar timestamp AAAAMMDD para nombres de archivo."""
    return datetime.now().strftime('%Y%m%d')
