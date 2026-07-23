"""Lectura y escritura de CSV con parámetros customizables."""

import csv
from pathlib import Path
from typing import List, Dict, Optional


def leer_csv(
    ruta: str,
    delimitador: str = ',',
    encoding: str = 'utf-8',
    sin_bom: bool = True,
) -> tuple[List[str], List[Dict[str, str]]]:
    """
    Leer CSV y retornar (encabezados, filas).

    Args:
        ruta: Ruta del archivo
        delimitador: ';' o ','
        encoding: 'utf-8' o 'latin-1'
        sin_bom: Si True, remover BOM de UTF-8 si existe

    Returns:
        (lista_columnas, lista_filas_dict)
    """
    ruta_path = Path(ruta)

    with open(ruta_path, 'r', encoding=encoding, newline='') as f:
        contenido = f.read()

    if sin_bom and contenido.startswith('﻿'):
        contenido = contenido[1:]

    lineas = contenido.split('\n')
    reader = csv.reader(lineas, delimiter=delimitador)

    encabezados = None
    filas = []

    for i, fila in enumerate(reader):
        if i == 0:
            encabezados = fila
        else:
            if fila and any(fila):  # Saltar filas vacías
                filas.append({encabezados[j]: (fila[j] if j < len(fila) else '')
                             for j in range(len(encabezados))})

    return encabezados, filas


def escribir_csv(
    ruta: str,
    encabezados: List[str],
    filas: List[Dict[str, str]],
    delimitador: str = ',',
    encoding: str = 'utf-8',
    con_encabezados: bool = True,
    quote_minimal: bool = True,
) -> None:
    """
    Escribir CSV.

    Args:
        ruta: Ruta de salida
        encabezados: Lista de nombres de columnas
        filas: Lista de diccionarios {col: valor}
        delimitador: ';' o ','
        encoding: 'utf-8' o 'latin-1'
        con_encabezados: Si False, omitir fila de encabezados
        quote_minimal: Si True, usar QUOTE_MINIMAL; si False, QUOTE_ALL
    """
    ruta_path = Path(ruta)
    ruta_path.parent.mkdir(parents=True, exist_ok=True)

    quoting = csv.QUOTE_MINIMAL if quote_minimal else csv.QUOTE_ALL

    with open(ruta_path, 'w', encoding=encoding, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados, delimiter=delimitador, quoting=quoting)

        if con_encabezados:
            writer.writeheader()

        writer.writerows(filas)
