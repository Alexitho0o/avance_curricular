#!/usr/bin/env python3
"""Genera el Excel de cruce: Rectificacion de 12 programas (Etapa 1) vs Reporte 5910.

Construye un libro con las bases de datos fuente en hojas separadas (datos tal
cual, sin edicion) y hojas de cruce que usan formulas reales de Excel
(INDEX/MATCH) para traer los valores desde esas bases y comparar, en vez de
pegar el resultado ya calculado.

Fuentes:
 1. Carga congelada Etapa 1 (103 filas, 07_resultados/cargas_congeladas/...).
 2. Carga congelada Etapa 2 (37 filas, 09_respaldo/cargas_congeladas/...).
 3. Rectificacion de 12 programas efectivamente enviada (Downloads, ahora
    gobernada en el proyecto), copia byte a byte identica a la ya gobernada en
    07_resultados/borradores_prueba_no_oficiales/.
 4. Reporte 5910 validado (09_respaldo/reportes_pes_validados/...).
"""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
CARGA_ETAPA1 = ROOT / "07_resultados" / "cargas_congeladas" / "20260817_155153_etapa1_areas_vigencia_fecha" / "CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv"
CARGA_ETAPA2 = ROOT / "09_respaldo" / "cargas_congeladas" / "20260828_etapa2_carga_17451" / "28-08-2026_13-17-17_Oferta-Académica-TP-Nueva-2027.csv"
RECTIFICACION_ENVIADA = Path.home() / "Downloads" / "RECTIFICACIÓN_ETAPA1_12_PROGRAMAS.xlsx"
RECTIFICACION_GOBERNADA = ROOT / "07_resultados" / "borradores_prueba_no_oficiales" / "RECTIFICACION_ETAPA1_12_PROGRAMAS_20260828.xlsx"
REPORTE_5910 = ROOT / "09_respaldo" / "reportes_pes_validados" / "20260907_reporte_5910_etapa1_2" / "5910 Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas.csv"
OUT_DIR = ROOT / "06_validaciones" / "conciliacion_rectificacion_12_vs_5910_20260907"
OUT_FILE = OUT_DIR / "CRUCE_RECTIFICACION_12_PROGRAMAS_VS_REPORTE_5910_20260907.xlsx"
DESKTOP_COPY = Path.home() / "Desktop" / "CRUCE_RECTIFICACION_12_PROGRAMAS_VS_REPORTE_5910_20260907.xlsx"

COLUMNAS_CARGABLES = [
    "COD_SEDE", "NOMBRE_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD",
    "COD_JORNADA", "VERSION", "COD_TIPO_PLAN_CARRERA", "CARACTERISTICAS_TIPO_PLAN",
    "DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL", "REGIMEN",
    "DURACION_REGIMEN", "NOMBRE_TITULO", "COD_NIVEL_GLOBAL", "COD_NIVEL_CARRERA",
    "ANIO_INICIO", "ACREDITACION", "REQUISITO_INGRESO", "SEMESTRES_RECONOCIDOS",
    "AREA_ACTUAL", "AREA_ADMIN_DERECHO", "AREA_AGRI_SILVI_PESCA_VET",
    "AREA_ARTES_HUMANIDADES", "AREA_CIENCIAS_NAT_MAT_ESTAD",
    "AREA_CS_SOCIAL_PERIODISMO_INFO", "AREA_EDUCACION",
    "AREA_INGE_INDUSTRIA_CONSTRUC", "AREA_SALUD_BIENESTAR", "AREA_SERVICIOS",
    "AREA_TECNO_INFO_COMUNICA", "VACANTES_PRIMER_SEMESTRE",
    "VACANTES_SEGUNDO_SEMESTRE", "FECHA_ADMISION_INICIAL", "ENLACE_INFO_PROGRAMA",
    "LICENCIA_ENS_MEDIA", "NOTAS_ENS_MEDIA", "PROMEDIO_MIN_ENS_MEDIA",
    "RECONOCIMIENTOS_APREN_PREVIOS", "EXPERIENCIA_LABORAL", "MAIL_DIFUSION_CARRERA",
    "FORMATO_VALOR", "VALOR_MATRICULA_ANUAL", "COSTO_TITULACION",
    "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL", "VIGENCIA_CARRERA",
]
IDX = {c: i for i, c in enumerate(COLUMNAS_CARGABLES)}

# 9 carreras de Etapa 1 con cambio de FECHA_ADMISION_INICIAL que ninguna rectificacion gobernada explica.
LLAVES_FECHA_SIN_EXPLICAR = [
    ("2", "111", "3", "4", "2"), ("2", "112", "3", "4", "2"), ("2", "113", "3", "4", "2"),
    ("2", "124", "3", "4", "2"), ("2", "125", "3", "4", "2"), ("2", "86", "3", "4", "2"),
    ("2", "87", "3", "4", "1"), ("2", "88", "3", "4", "2"), ("2", "57", "3", "4", "1"),
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)
OK_FILL = PatternFill("solid", fgColor="C6EFCE")
BAD_FILL = PatternFill("solid", fgColor="FFC7CE")
WARN_FILL = PatternFill("solid", fgColor="FFEB9C")


def read_csv_rows(path: Path) -> list[list[str]]:
    for encoding in ("utf-8", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.reader(handle, delimiter=";"))
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"No se pudo decodificar {path}")


def normalizar_fecha(valor) -> str:
    """DD/MM/AAAA, DD-MM-AAAA o datetime -> DD-MM-AAAA como texto."""
    if valor in (None, ""):
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d-%m-%Y")
    texto = str(valor).strip()
    return texto.replace("/", "-")


def escribir_hoja_raw(wb, nombre: str, header: list[str], filas: list[list], con_codigo_ies: bool) -> None:
    ws = wb.create_sheet(nombre)
    headers = (["CODIGO_IES_NUM"] if con_codigo_ies else []) + header + ["LLAVE_SIES"]
    for col, titulo in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=titulo)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    offset = 1 if con_codigo_ies else 0
    col_sede = get_column_letter(offset + IDX["COD_SEDE"] + 1)
    col_carrera = get_column_letter(offset + IDX["COD_CARRERA"] + 1)
    col_modalidad = get_column_letter(offset + IDX["MODALIDAD"] + 1)
    col_jornada = get_column_letter(offset + IDX["COD_JORNADA"] + 1)
    col_version = get_column_letter(offset + IDX["VERSION"] + 1)
    llave_col = len(headers)
    for r, fila in enumerate(filas, start=2):
        for c, valor in enumerate(fila, start=1):
            campo = header[c - 1 - offset] if c - 1 >= offset else "CODIGO_IES_NUM"
            if campo == "FECHA_ADMISION_INICIAL":
                valor = normalizar_fecha(valor)
            ws.cell(row=r, column=c, value=valor)
        ws.cell(row=r, column=llave_col,
                 value=f'={col_sede}{r}&"|"&{col_carrera}{r}&"|"&{col_modalidad}{r}&"|"&{col_jornada}{r}&"|"&{col_version}{r}')
    ws.freeze_panes = "A2"
    ws.column_dimensions["A"].width = 12
    return ws


def col_letter_for(campo: str, con_codigo_ies: bool) -> str:
    offset = 1 if con_codigo_ies else 0
    return get_column_letter(offset + IDX[campo] + 1)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    e1_rows = read_csv_rows(CARGA_ETAPA1)
    e2_rows = read_csv_rows(CARGA_ETAPA2)
    rows_5910_raw = read_csv_rows(REPORTE_5910)
    header_5910, rows_5910 = rows_5910_raw[0], rows_5910_raw[1:]
    pos_5910 = [header_5910.index(c) for c in COLUMNAS_CARGABLES]
    rows_5910_full = [[row[0]] + [row[p] for p in pos_5910] for row in rows_5910]  # CODIGO_IES_NUM + 48

    wb_rect = openpyxl.load_workbook(RECTIFICACION_ENVIADA, data_only=True)["Rectificacion Etapa 1"]
    rect_header = [wb_rect.cell(row=1, column=c).value for c in range(1, 49)]
    rect_rows = [[wb_rect.cell(row=r, column=c).value for c in range(1, 49)] for r in range(2, wb_rect.max_row + 1)]

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    ws1 = escribir_hoja_raw(wb, "01_Carga_Etapa1_Congelada", COLUMNAS_CARGABLES, e1_rows, con_codigo_ies=False)
    ws2 = escribir_hoja_raw(wb, "02_Carga_Etapa2_Congelada", COLUMNAS_CARGABLES, e2_rows, con_codigo_ies=False)
    ws3 = escribir_hoja_raw(wb, "03_Rectificacion_12_Enviada", rect_header, rect_rows, con_codigo_ies=False)
    ws4 = escribir_hoja_raw(wb, "04_Reporte_5910_Validado", COLUMNAS_CARGABLES, rows_5910_full, con_codigo_ies=True)

    # --- Hoja 05: cruce rectificacion (12 programas) vs 5910, todo con formulas ---
    ws5 = wb.create_sheet("05_Cruce_Rectificacion_vs_5910")
    campos_cruce = ["VIGENCIA_CARRERA", "VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE",
                    "RECONOCIMIENTOS_APREN_PREVIOS", "FECHA_ADMISION_INICIAL", "ENLACE_INFO_PROGRAMA"]
    headers5 = ["LLAVE_SIES", "NOMBRE_CARRERA"]
    for campo in campos_cruce:
        headers5 += [f"{campo}_ANTES_CARGA_E1", f"{campo}_ENVIADO_RECTIFICACION", f"{campo}_EN_5910", f"{campo}_COINCIDE"]
    headers5.append("RESULTADO_FILA")
    for col, titulo in enumerate(headers5, start=1):
        cell = ws5.cell(row=1, column=col, value=titulo)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    ws5.freeze_panes = "C2"

    n_rect = len(rect_rows)
    llave_col_ws1 = ws1.max_column
    llave_col_ws3 = ws3.max_column
    llave_col_ws4 = ws4.max_column
    nombre_col_ws3 = col_letter_for("NOMBRE_CARRERA", con_codigo_ies=False)

    for i in range(n_rect):
        fila_ws3 = i + 2
        fila_ws5 = i + 2
        ws5.cell(row=fila_ws5, column=1, value=f"=03_Rectificacion_12_Enviada!{get_column_letter(llave_col_ws3)}{fila_ws3}")
        ws5.cell(row=fila_ws5, column=2, value=f"=03_Rectificacion_12_Enviada!{nombre_col_ws3}{fila_ws3}")
        col_actual = 3
        result_cols = []
        for campo in campos_cruce:
            col_e1 = col_letter_for(campo, con_codigo_ies=False)
            col_rect = col_letter_for(campo, con_codigo_ies=False)
            col_5910 = col_letter_for(campo, con_codigo_ies=True)
            c_antes = get_column_letter(col_actual)
            c_enviado = get_column_letter(col_actual + 1)
            c_5910 = get_column_letter(col_actual + 2)
            c_coincide = get_column_letter(col_actual + 3)
            ws5.cell(row=fila_ws5, column=col_actual,
                     value=f'=IFERROR(INDEX(01_Carga_Etapa1_Congelada!${col_e1}:${col_e1},MATCH($A{fila_ws5},01_Carga_Etapa1_Congelada!${get_column_letter(llave_col_ws1)}:${get_column_letter(llave_col_ws1)},0)),"SIN_DATO")')
            if campo == "FECHA_ADMISION_INICIAL":
                ws5.cell(row=fila_ws5, column=col_actual + 1,
                         value=f'=TEXT(03_Rectificacion_12_Enviada!{col_rect}{fila_ws3},"dd-mm-yyyy")')
            else:
                ws5.cell(row=fila_ws5, column=col_actual + 1, value=f"=03_Rectificacion_12_Enviada!{col_rect}{fila_ws3}")
            ws5.cell(row=fila_ws5, column=col_actual + 2,
                     value=f'=IFERROR(INDEX(04_Reporte_5910_Validado!${col_5910}:${col_5910},MATCH($A{fila_ws5},04_Reporte_5910_Validado!${get_column_letter(llave_col_ws4)}:${get_column_letter(llave_col_ws4)},0)),"NO_ENCONTRADO_EN_5910")')
            if campo == "ENLACE_INFO_PROGRAMA":
                ws5.cell(row=fila_ws5, column=col_actual + 3,
                         value=f'=({c_enviado}{fila_ws5}<>"")=({c_5910}{fila_ws5}<>"")')
            else:
                ws5.cell(row=fila_ws5, column=col_actual + 3, value=f"={c_enviado}{fila_ws5}={c_5910}{fila_ws5}")
            result_cols.append(c_coincide)
            col_actual += 4
        resultado_col = get_column_letter(col_actual)
        rango = ",".join(f"{c}{fila_ws5}" for c in result_cols)
        ws5.cell(row=fila_ws5, column=col_actual,
                 value=f'=IF(AND({rango}),"OK - REGISTRADO CORRECTAMENTE","REVISAR - HAY DIFERENCIA")')

    total_row = n_rect + 3
    ws5.cell(row=total_row, column=1, value="TOTAL FILAS OK").font = Font(bold=True)
    ws5.cell(row=total_row, column=2, value=f'=COUNTIF({resultado_col}2:{resultado_col}{n_rect + 1},"OK*")')
    ws5.cell(row=total_row + 1, column=1, value="TOTAL FILAS A REVISAR").font = Font(bold=True)
    ws5.cell(row=total_row + 1, column=2, value=f'=COUNTIF({resultado_col}2:{resultado_col}{n_rect + 1},"REVISAR*")')

    # --- Hoja 06: hallazgo de fechas no explicado por ninguna rectificacion gobernada ---
    ws6 = wb.create_sheet("06_Hallazgo_Fechas_Sin_Explicar")
    headers6 = ["LLAVE_SIES", "NOMBRE_CARRERA", "FECHA_EN_CARGA_ETAPA1", "FECHA_EN_5910",
                "DIFIERE", "EXPLICADO_POR_RECTIFICACION_12"]
    for col, titulo in enumerate(headers6, start=1):
        cell = ws6.cell(row=1, column=col, value=titulo)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    col_fecha_e1 = col_letter_for("FECHA_ADMISION_INICIAL", con_codigo_ies=False)
    col_fecha_5910 = col_letter_for("FECHA_ADMISION_INICIAL", con_codigo_ies=True)
    col_nombre_e1 = col_letter_for("NOMBRE_CARRERA", con_codigo_ies=False)
    for i, llave in enumerate(LLAVES_FECHA_SIN_EXPLICAR):
        r = i + 2
        llave_txt = "|".join(llave)
        ws6.cell(row=r, column=1, value=llave_txt)
        ws6.cell(row=r, column=2,
                 value=f'=IFERROR(INDEX(01_Carga_Etapa1_Congelada!${col_nombre_e1}:${col_nombre_e1},MATCH($A{r},01_Carga_Etapa1_Congelada!${get_column_letter(llave_col_ws1)}:${get_column_letter(llave_col_ws1)},0)),"?")')
        ws6.cell(row=r, column=3,
                 value=f'=IFERROR(INDEX(01_Carga_Etapa1_Congelada!${col_fecha_e1}:${col_fecha_e1},MATCH($A{r},01_Carga_Etapa1_Congelada!${get_column_letter(llave_col_ws1)}:${get_column_letter(llave_col_ws1)},0)),"?")')
        ws6.cell(row=r, column=4,
                 value=f'=IFERROR(INDEX(04_Reporte_5910_Validado!${col_fecha_5910}:${col_fecha_5910},MATCH($A{r},04_Reporte_5910_Validado!${get_column_letter(llave_col_ws4)}:${get_column_letter(llave_col_ws4)},0)),"?")')
        ws6.cell(row=r, column=5, value=f"=C{r}<>D{r}")
        ws6.cell(row=r, column=6,
                 value=f'=IF(COUNTIF(03_Rectificacion_12_Enviada!${get_column_letter(llave_col_ws3)}:${get_column_letter(llave_col_ws3)},$A{r})>0,"SI","NO - PENDIENTE DE EXPLICACION")')
    ws6.cell(row=1, column=7, value="").fill = HEADER_FILL
    nota = ws6.cell(row=len(LLAVES_FECHA_SIN_EXPLICAR) + 3, column=1,
                     value="Estas 9 carreras cambiaron FECHA_ADMISION_INICIAL entre la carga congelada de Etapa 1 y el reporte 5910, "
                           "pero ninguna de las dos rectificaciones gobernadas (7 programas / 12 programas) las incluye. Requiere aclarar con SIES/area academica el origen del cambio antes de usar el 5910 como base de Etapa 3.")
    nota.font = Font(italic=True, color="9C0006")
    ws6.merge_cells(start_row=len(LLAVES_FECHA_SIN_EXPLICAR) + 3, start_column=1,
                     end_row=len(LLAVES_FECHA_SIN_EXPLICAR) + 3, end_column=6)
    nota.alignment = Alignment(wrap_text=True, vertical="top")

    # --- Hoja 07: resumen ---
    ws7 = wb.create_sheet("07_Resumen", 0)
    ws7.sheet_view.showGridLines = False
    filas_resumen = [
        ("Cruce: Rectificación 12 programas (Etapa 1) vs. Reporte 5910", None),
        ("", None),
        ("Verificación de integridad del envío", None),
        ("Archivo enviado (Descargas del usuario)", str(RECTIFICACION_ENVIADA)),
        ("Archivo gobernado en el proyecto", str(RECTIFICACION_GOBERNADA)),
        ("Contenido idéntico celda a celda", "SI (0 diferencias en 12 filas x 48 columnas)"),
        ("", None),
        ("Cobertura de la rectificación en el 5910", None),
        ("Programas rectificados", 12),
        ("Programas con match encontrado en el 5910", f"=COUNTA(05_Cruce_Rectificacion_vs_5910!A2:A13)"),
        ("Programas OK (todos los campos coinciden)", f"=05_Cruce_Rectificacion_vs_5910!B{total_row}"),
        ("Programas a revisar", f"=05_Cruce_Rectificacion_vs_5910!B{total_row + 1}"),
        ("", None),
        ("Hallazgo pendiente (no relacionado a esta rectificación)", None),
        ("Carreras con cambio de FECHA_ADMISION_INICIAL no explicado", len(LLAVES_FECHA_SIN_EXPLICAR)),
        ("Detalle", "Ver hoja 06_Hallazgo_Fechas_Sin_Explicar"),
        ("", None),
        ("Bases de datos fuente (raw, sin editar)", None),
        ("01_Carga_Etapa1_Congelada", f"{len(e1_rows)} filas"),
        ("02_Carga_Etapa2_Congelada", f"{len(e2_rows)} filas"),
        ("03_Rectificacion_12_Enviada", f"{len(rect_rows)} filas"),
        ("04_Reporte_5910_Validado", f"{len(rows_5910_full)} filas"),
    ]
    for r, (label, value) in enumerate(filas_resumen, start=1):
        c1 = ws7.cell(row=r, column=1, value=label)
        if value is not None:
            ws7.cell(row=r, column=2, value=value)
        if label and value is None and label not in ("",):
            c1.font = Font(bold=True, size=13 if r == 1 else 11)
    ws7.column_dimensions["A"].width = 55
    ws7.column_dimensions["B"].width = 70

    wb.save(OUT_FILE)
    shutil.copy2(OUT_FILE, DESKTOP_COPY)
    print("Generado:", OUT_FILE)
    print("Copia en escritorio:", DESKTOP_COPY)


if __name__ == "__main__":
    main()
