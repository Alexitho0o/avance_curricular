"""Entregable 2: Excel de respaldo con encabezados, tipado real y diccionario."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # raíz del monorepo (para 'common.*')
sys.path.insert(0, str(Path(__file__).parent.parent))       # procesos/ire_2026 (para 'src.*')

from datetime import datetime
from typing import List, Dict

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from common.io_csv import leer_csv
from common.excel import configurar_hoja_base, destacar_editables, guardar_libro
from src.schema import COLUMNAS, ESPECIFICACION, CATALOGO_TIPO_INFRAESTRUCTURA

RAIZ_PROCESO = Path(__file__).parent.parent
RUTA_OUTPUT = RAIZ_PROCESO / "output"
RUTA_HISTORICO = RAIZ_PROCESO / "data" / "historico" / "ire_historico.csv"

# Columnas donde el valor, si viene, es numérico real (no texto) en el Excel
COLUMNAS_NUMERICAS = {
    col for col, spec in ESPECIFICACION.items()
    if spec["tipo"] in ("numero", "numero_entero")
}


def _valor_tipado(columna: str, valor: str):
    """Convertir a número si la columna es numérica y el valor no está vacío."""
    if not valor or not valor.strip():
        return None
    if columna in COLUMNAS_NUMERICAS:
        try:
            numero = float(valor)
            return int(numero) if numero == int(numero) else numero
        except ValueError:
            return valor
    return valor


def construir_hoja_carga(wb: Workbook, filas: List[Dict]) -> None:
    """Hoja CARGA_2026: datos con encabezados y tipado real."""
    ws = wb.active
    ws.title = "CARGA_2026"

    configurar_hoja_base(ws, COLUMNAS)

    for fila_idx, fila in enumerate(filas, start=2):
        for col_idx, columna in enumerate(COLUMNAS, start=1):
            valor = _valor_tipado(columna, fila.get(columna, ""))
            ws.cell(row=fila_idx, column=col_idx, value=valor)

    # Destacar como editables las columnas numéricas de magnitudes (no identidad ni catálogos)
    columnas_editables_idx = [
        i for i, col in enumerate(COLUMNAS, start=1)
        if col in COLUMNAS_NUMERICAS
    ]
    if filas:
        destacar_editables(ws, (2, len(filas) + 1), columnas_editables_idx)

    # Leyenda
    fila_leyenda = len(filas) + 3
    celda = ws.cell(row=fila_leyenda, column=1, value="Amarillo = campo editable (magnitud numérica sujeta a actualización anual)")
    celda.font = Font(italic=True, size=9)


def construir_hoja_diccionario(wb: Workbook) -> None:
    """Hoja DICCIONARIO: las 54 columnas con definición, códigos y especificación."""
    ws = wb.create_sheet("DICCIONARIO")

    encabezados = ["#", "CAMPO", "TIPO", "APLICA A TIPO", "OBLIGATORIO", "CATÁLOGO / NOTA"]
    configurar_hoja_base(ws, encabezados, anchos=[5, 35, 16, 16, 14, 60])

    catalogos_nota = {
        "TIPO_INFRAESTRUCTURA": "1=Uso Permanente, 2=Uso Restringido, 3=Biblioteca, 4=Digital, 5=Predios, 6=Plataformas",
        "SITUACION_TENENCIA": "1=Propio, 2=Arrendado, 3=Comodato, 4=Usufructo, 5=Leasing, 6=Otro",
        "USO_EXCLUSIVO": "1=Exclusivo, 2=Compartido",
        "UR_SITUACION_TENENCIA": "1=Arrendado, 2=Otra",
        "VIGENCIA": "0=Eliminar registro cargado, 1=Mantener",
    }

    for i, columna in enumerate(COLUMNAS, start=1):
        spec = ESPECIFICACION[columna]
        aplica = ", ".join(str(t) for t in sorted(spec["aplica"]))
        obligatorio = "Sí" if spec["obligatorio"] else "Condicional"
        nota = catalogos_nota.get(columna, "")

        ws.cell(row=i + 1, column=1, value=i)
        ws.cell(row=i + 1, column=2, value=columna)
        ws.cell(row=i + 1, column=3, value=spec["tipo"])
        ws.cell(row=i + 1, column=4, value=aplica)
        ws.cell(row=i + 1, column=5, value=obligatorio)
        ws.cell(row=i + 1, column=6, value=nota)


def construir_hoja_historico(wb: Workbook, filas_historico: List[Dict]) -> None:
    """Hoja HISTORICO: comparativo 2023-2025 (según serie documentada en kpi.py)."""
    ws = wb.create_sheet("HISTORICO")

    from src.kpi import SERIE_HISTORICA

    encabezados = ["CONCEPTO", "2023", "2024", "2025"]
    configurar_hoja_base(ws, encabezados, anchos=[35, 15, 15, 15])

    conceptos = [
        ("Matrícula jornada principal", "matricula"),
        ("M² de terreno", "m2_terreno"),
        ("M² construidos", "m2_edificados"),
        ("M² áreas verdes y esparcimiento", "m2_areas_verdes"),
        ("M² talleres", "m2_talleres"),
        ("Nº auditorios", "total_auditorios"),
        ("Nº computadores", "total_pc_nb_disponible"),
        ("Nº talleres", "total_talleres"),
        ("Nº salas", "total_salas_clases"),
        ("Nº laboratorios", "total_laboratorios"),
        ("Libros digitales (e-books)", "total_titulos_libros_digitales"),
        ("LMS", "lms"),
        ("Videoconferencia", "videoconferencia"),
        ("Razón social informada", "razon_social"),
    ]

    for i, (etiqueta, clave) in enumerate(conceptos, start=2):
        ws.cell(row=i, column=1, value=etiqueta)
        for j, anio in enumerate([2023, 2024, 2025], start=2):
            valor = SERIE_HISTORICA[anio].get(clave, "—")
            ws.cell(row=i, column=j, value=valor)


def generar_xlsx(filas: List[Dict], fecha_sufijo: str = None) -> Path:
    """Generar el Excel de respaldo completo."""
    if fecha_sufijo is None:
        fecha_sufijo = datetime.now().strftime('%Y%m%d')

    RUTA_OUTPUT.mkdir(parents=True, exist_ok=True)
    ruta_salida = RUTA_OUTPUT / f"IRE_2026_respaldo_{fecha_sufijo}.xlsx"

    wb = Workbook()
    construir_hoja_carga(wb, filas)
    construir_hoja_diccionario(wb)

    _, filas_historico = leer_csv(str(RUTA_HISTORICO), delimitador=';', encoding='utf-8')
    construir_hoja_historico(wb, filas_historico)

    guardar_libro(wb, str(ruta_salida))
    return ruta_salida


def main():
    from src.build_csv import construir_dataset, validar_dataset_completo, ValidacionFallida
    from src.config_loader import ConfiguracionIncompleta

    print("=" * 70)
    print("IRE 2026 — Generación del Excel de respaldo")
    print("=" * 70)

    try:
        filas = construir_dataset()
    except ConfiguracionIncompleta as e:
        print("\n✗ PIPELINE DETENIDO — configuración incompleta\n")
        print(str(e))
        sys.exit(1)

    es_valido, mensajes = validar_dataset_completo(filas)
    if not es_valido:
        print(f"\n✗ VALIDACIÓN FALLIDA — {len(mensajes)} error(es):\n")
        for m in mensajes:
            print(f"  - {m}")
        raise ValidacionFallida(f"{len(mensajes)} error(es) de validación")

    ruta = generar_xlsx(filas)
    print(f"\n✓ Generado: {ruta}")


if __name__ == '__main__':
    main()
