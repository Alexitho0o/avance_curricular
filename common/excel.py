"""Helpers para openpyxl: estilos, anchos, autofiltro, freeze panes."""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import List, Tuple, Optional


def crear_libro() -> Workbook:
    """Crear un nuevo workbook."""
    return Workbook()


def configurar_hoja_base(
    ws,
    encabezados: List[str],
    anchos: Optional[List[int]] = None,
) -> None:
    """
    Configurar hoja con encabezados en negrita, relleno, freeze panes y autofiltro.

    Args:
        ws: Worksheet
        encabezados: Lista de nombres de columna
        anchos: Lista de anchos (opcional)
    """
    # Escribir encabezados
    for col_idx, nombre in enumerate(encabezados, start=1):
        celda = ws.cell(row=1, column=col_idx, value=nombre)
        celda.font = Font(bold=True, name='Arial')
        celda.fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        celda.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Freeze panes
    ws.freeze_panes = 'A2'

    # Autofiltro
    ws.auto_filter.ref = f'A1:{get_column_letter(len(encabezados))}1'

    # Anchos
    if anchos:
        for col_idx, ancho in enumerate(anchos, start=1):
            ws.column_dimensions[get_column_letter(col_idx)].width = ancho
    else:
        # Auto-ajuste genérico
        for col_idx in range(1, len(encabezados) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 20


def destacar_editables(ws, filas_rango: Tuple[int, int], columnas_idx: List[int]) -> None:
    """
    Destacar celdas editables con relleno amarillo.

    Args:
        ws: Worksheet
        filas_rango: (fila_inicio, fila_fin) inclusive
        columnas_idx: Lista de índices de columna (1-based)
    """
    amarillo = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

    for fila in range(filas_rango[0], filas_rango[1] + 1):
        for col_idx in columnas_idx:
            ws.cell(row=fila, column=col_idx).fill = amarillo


def guardar_libro(wb: Workbook, ruta: str) -> None:
    """Guardar workbook en archivo."""
    wb.save(ruta)
