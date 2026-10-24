#!/usr/bin/env python3
"""Genera un Excel completo, trazable y con graficos nativos de Excel."""

from pathlib import Path

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


BASE_DIR = Path(__file__).resolve().parent
SALIDA_DIR = BASE_DIR / "salida"
FUENTE = SALIDA_DIR / "reporte_matricula_ip_san_sebastian_ORIGINAL.csv"
ARCHIVO_SALIDA = SALIDA_DIR / "Consolidado_Retencion_Trazable_Completo.xlsx"
COLOR_ENCABEZADO = "1F497D"
FLAG_COLUMNS = ["RETENIDO_INST", "RETENIDO_CARRERA", "RETENIDO_PROGRAMA"]


def cargar_base(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta, dtype="string", encoding="utf-8-sig")
    df.columns = [col.strip() for col in df.columns]
    columns_lower = {col.lower(): col for col in df.columns}
    required = {
        "cat_periodo", "mrun", "anio_ing_carr_act", "cod_inst", "nomb_inst",
        "cod_carrera", "nomb_carrera", "codigo_unico", "tipo_plan_carr",
        "nivel_carrera_2",
    }
    missing = sorted(required - set(columns_lower))
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    rename = {original: lower for lower, original in columns_lower.items()}
    df = df.rename(columns=rename)
    for col in ("cat_periodo", "anio_ing_carr_act"):
        df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")
    df["mrun"] = df["mrun"].str.strip()
    return df


def aplicar_diccionario_tipo_carrera(df: pd.DataFrame) -> pd.DataFrame:
    """Completa el tipo de carrera usando el primer valor historico valido."""
    mapping_carreras = (
        df.dropna(subset=["nivel_carrera_2"])
        .loc[lambda frame: frame["cod_carrera"].notna()]
        .groupby("cod_carrera")["nivel_carrera_2"]
        .first()
        .to_dict()
    )
    df = df.copy()
    tipo_mapeado = df["cod_carrera"].map(mapping_carreras)
    df["nivel_carrera_2"] = tipo_mapeado.fillna(df["nivel_carrera_2"])
    return df


def construir_detalle_completo(df: pd.DataFrame) -> pd.DataFrame:
    """Preserva el crudo completo y agrega flags solo a cohortes evaluables."""
    resultado = df.copy()
    for column in FLAG_COLUMNS:
        resultado[column] = pd.NA

    for anio in sorted(df["cat_periodo"].dropna().unique()):
        cohorte_mask = (
            (df["cat_periodo"] == anio)
            & (df["anio_ing_carr_act"] == anio)
            & df["tipo_plan_carr"].fillna("").str.casefold().eq("plan regular")
            & df["mrun"].notna()
            & df["mrun"].ne("")
        )
        futuro = df[
            (df["cat_periodo"] == anio + 1)
            & df["mrun"].notna()
            & df["mrun"].ne("")
        ]
        if not cohorte_mask.any() or futuro.empty:
            continue

        futuro_inst = set(zip(futuro["mrun"], futuro["cod_inst"]))
        futuro_carrera = set(zip(futuro["mrun"], futuro["cod_carrera"]))
        futuro_programa = set(zip(futuro["mrun"], futuro["codigo_unico"]))
        indices = resultado.index[cohorte_mask]
        resultado.loc[indices, "RETENIDO_INST"] = [
            int((mrun, cod_inst) in futuro_inst)
            for mrun, cod_inst in zip(df.loc[indices, "mrun"], df.loc[indices, "cod_inst"])
        ]
        resultado.loc[indices, "RETENIDO_CARRERA"] = [
            int((mrun, cod_carrera) in futuro_carrera)
            for mrun, cod_carrera in zip(df.loc[indices, "mrun"], df.loc[indices, "cod_carrera"])
        ]
        resultado.loc[indices, "RETENIDO_PROGRAMA"] = [
            int((mrun, codigo_unico) in futuro_programa)
            for mrun, codigo_unico in zip(df.loc[indices, "mrun"], df.loc[indices, "codigo_unico"])
        ]
    return resultado


def estilo_encabezado(ws, row: int, last_column: int) -> None:
    fill = PatternFill("solid", fgColor=COLOR_ENCABEZADO)
    for col in range(1, last_column + 1):
        cell = ws.cell(row, col)
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def aplicar_estilo_total(ws, row: int, last_column: int) -> None:
    """Destaca el total y usa borde contable de doble linea."""
    from openpyxl.styles import Border, Side

    borde = Border(bottom=Side(style="double", color="000000"))
    for col in range(1, last_column + 1):
        ws.cell(row, col).font = Font(bold=True)
        ws.cell(row, col).border = borde
    count_start = 4 if last_column >= 6 else 2
    ws.cell(row, count_start).number_format = ws.cell(row, count_start + 1).number_format = "#,##0"
    if last_column >= 4:
        ws.cell(row, last_column).number_format = "0.0%"


def ajustar_ancho(ws) -> None:
    for column_cells in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        letter = get_column_letter(column_cells[0].column)
        ws.column_dimensions[letter].width = min(max(max_length + 3, 10), 55)


def valor_excel(value):
    return None if pd.isna(value) else value


def mapa_columnas(ws) -> dict[str, str]:
    return {
        str(ws.cell(1, col).value).upper(): get_column_letter(col)
        for col in range(1, ws.max_column + 1)
    }


def preparar_resumenes(detalle: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    evaluable = detalle[
        detalle["RETENIDO_INST"].notna()
        & detalle["cat_periodo"].notna()
    ].copy()
    carrera = evaluable[["cat_periodo", "cod_carrera", "nomb_carrera"]].drop_duplicates()
    programa = evaluable[["cat_periodo", "codigo_unico", "nomb_carrera"]].drop_duplicates()
    anios = pd.DataFrame({"cat_periodo": sorted(evaluable["cat_periodo"].unique())})
    return anios, carrera.sort_values(list(carrera.columns)), programa.sort_values(list(programa.columns))


def escribir_institucional(ws, anios: pd.DataFrame, cols: dict[str, str]) -> None:
    ws["A1"] = "Evolución de Retención Institucional"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:D1")
    ws.append(["Año Cohorte", "Tamaño Cohorte (N)", "Alumnos Retenidos", "Tasa Retención %"])
    estilo_encabezado(ws, 2, 4)
    for row, anio in enumerate(anios["cat_periodo"], 3):
        ws.cell(row, 1, int(anio))
        ws.cell(row, 2, f'=COUNTIFS(\'Detalle_Raw\'!{cols["CAT_PERIODO"]}:{cols["CAT_PERIODO"]},A{row},\'Detalle_Raw\'!{cols["RETENIDO_INST"]}:{cols["RETENIDO_INST"]},"<>")')
        ws.cell(row, 3, f'=COUNTIFS(\'Detalle_Raw\'!{cols["CAT_PERIODO"]}:{cols["CAT_PERIODO"]},A{row},\'Detalle_Raw\'!{cols["RETENIDO_INST"]}:{cols["RETENIDO_INST"]},1)')
        ws.cell(row, 4, f'=IFERROR(C{row}/B{row},0)')
        ws.cell(row, 2).number_format = ws.cell(row, 3).number_format = "#,##0"
        ws.cell(row, 4).number_format = "0.0%"

    total_row = ws.max_row + 1
    ws.cell(total_row, 1, "TOTAL GENERAL")
    ws.cell(total_row, 2, f"=SUM(B3:B{total_row - 1})")
    ws.cell(total_row, 3, f"=SUM(C3:C{total_row - 1})")
    ws.cell(total_row, 4, f"=IFERROR(C{total_row}/B{total_row},0)")
    aplicar_estilo_total(ws, total_row, 4)

    chart = LineChart()
    chart.title = "Evolución de la Retención Institucional"
    chart.y_axis.title = "Tasa Retención %"
    chart.x_axis.title = "Año Cohorte"
    chart.y_axis.numFmt = "0%"
    chart.add_data(Reference(ws, min_col=4, min_row=2, max_row=total_row - 1), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=3, max_row=total_row - 1))
    chart.height = 8
    chart.width = 16
    ws.add_chart(chart, "F1")


def escribir_apertura(ws, filas: pd.DataFrame, cols: dict[str, str], nivel: str) -> None:
    es_carrera = nivel == "carrera"
    if es_carrera:
        headers = ["Año Cohorte", "Código Carrera", "Nombre Carrera", "Tamaño Cohorte (N)", "Alumnos Retenidos", "Tasa Retención %"]
        key_col, flag_col = "COD_CARRERA", "RETENIDO_CARRERA"
    else:
        headers = ["Año Cohorte", "Código Único", "Nombre Carrera", "Tamaño Cohorte (N)", "Alumnos Retenidos", "Tasa Retención %"]
        key_col, flag_col = "CODIGO_UNICO", "RETENIDO_PROGRAMA"
    ws.append(headers)
    estilo_encabezado(ws, 1, 6)
    for row, (_, item) in enumerate(filas.iterrows(), 2):
        ws.cell(row, 1, int(item["cat_periodo"]))
        ws.cell(row, 2, item[key_col.lower()])
        ws.cell(row, 3, item["nomb_carrera"])
        ws.cell(row, 4, f'=COUNTIFS(\'Detalle_Raw\'!{cols["CAT_PERIODO"]}:{cols["CAT_PERIODO"]},A{row},\'Detalle_Raw\'!{cols[key_col]}:{cols[key_col]},B{row},\'Detalle_Raw\'!{cols[flag_col]}:{cols[flag_col]},"<>")')
        ws.cell(row, 5, f'=COUNTIFS(\'Detalle_Raw\'!{cols["CAT_PERIODO"]}:{cols["CAT_PERIODO"]},A{row},\'Detalle_Raw\'!{cols[key_col]}:{cols[key_col]},B{row},\'Detalle_Raw\'!{cols[flag_col]}:{cols[flag_col]},1)')
        ws.cell(row, 6, f'=IFERROR(E{row}/D{row},0)')
        ws.cell(row, 4).number_format = ws.cell(row, 5).number_format = "#,##0"
        ws.cell(row, 6).number_format = "0.0%"

    total_row = ws.max_row + 1
    ws.cell(total_row, 1, "TOTAL GENERAL")
    ws.cell(total_row, 4, f"=SUM(D2:D{total_row - 1})")
    ws.cell(total_row, 5, f"=SUM(E2:E{total_row - 1})")
    ws.cell(total_row, 6, f"=IFERROR(E{total_row}/D{total_row},0)")
    aplicar_estilo_total(ws, total_row, 6)

    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "Cohorte y retenidos por periodo"
    chart.y_axis.title = "Alumnos"
    chart.x_axis.title = "Registro"
    chart.add_data(Reference(ws, min_col=4, max_col=5, min_row=1, max_row=min(total_row - 1, 31)), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=2, min_row=2, max_row=min(total_row - 1, 31)))
    chart.height = 8
    chart.width = 16
    ws.add_chart(chart, "H1")


def escribir_segmento(
    ws,
    filas: pd.DataFrame,
    cols: dict[str, str],
    categoria: str,
    titulo: str,
    nivel: str,
) -> None:
    """Escribe resumen segmentado por nivel y agrega un grafico de tasas."""
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")
    headers = [
        "Año Cohorte",
        "Código Carrera",
        "Nombre Carrera",
        "Tamaño Cohorte (N)",
        "Alumnos Retenidos",
        "Tasa Retención %",
    ]
    ws.append(headers)
    estilo_encabezado(ws, 2, len(headers))
    key_col = "COD_CARRERA"
    flag_col = "RETENIDO_CARRERA"
    grupos = filas[
        filas["nivel_carrera_2"].fillna("").eq(categoria)
    ][["cat_periodo", "cod_carrera", "nomb_carrera"]].drop_duplicates()
    grupos = grupos.sort_values(list(grupos.columns))
    for row, (_, item) in enumerate(grupos.iterrows(), 3):
        ws.cell(row, 1, int(item["cat_periodo"]))
        ws.cell(row, 2, valor_excel(item["cod_carrera"]))
        ws.cell(row, 3, valor_excel(item["nomb_carrera"]))
        base = (
            f"'Detalle_Raw'!{cols['NIVEL_CARRERA_2']}:{cols['NIVEL_CARRERA_2']},\"{categoria}\","
            f"'Detalle_Raw'!{cols['CAT_PERIODO']}:{cols['CAT_PERIODO']},A{row},"
            f"'Detalle_Raw'!{cols[key_col]}:{cols[key_col]},B{row},"
            f"'Detalle_Raw'!{cols[flag_col]}:{cols[flag_col]},\"<>\""
        )
        ws.cell(row, 4, f"=COUNTIFS({base})")
        base_retenidos = base[:-5] + "1"
        ws.cell(row, 5, f"=COUNTIFS({base_retenidos})")
        ws.cell(row, 6, f"=IFERROR(E{row}/D{row},0)")
        ws.cell(row, 4).number_format = ws.cell(row, 5).number_format = "#,##0"
        ws.cell(row, 6).number_format = "0.0%"

    total_row = ws.max_row + 1
    ws.cell(total_row, 1, "TOTAL GENERAL")
    ws.cell(total_row, 4, f"=SUM(D3:D{total_row - 1})")
    ws.cell(total_row, 5, f"=SUM(E3:E{total_row - 1})")
    ws.cell(total_row, 6, f"=IFERROR(E{total_row}/D{total_row},0)")
    aplicar_estilo_total(ws, total_row, 6)

    chart = LineChart()
    chart.title = f"Evolución de Retención: {categoria}"
    chart.y_axis.title = "Tasa Retención %"
    chart.x_axis.title = "Año Cohorte"
    chart.y_axis.numFmt = "0%"
    if total_row > 3:
        chart.add_data(Reference(ws, min_col=6, min_row=2, max_row=total_row - 1), titles_from_data=True)
        chart.set_categories(Reference(ws, min_col=1, min_row=3, max_row=total_row - 1))
    chart.height = 8
    chart.width = 16
    ws.add_chart(chart, "H2")
    ws.freeze_panes = "A3"
    ws.sheet_view.showGridLines = True
    ajustar_ancho(ws)


def escribir_segmento_anual(ws, detalle: pd.DataFrame, cols: dict[str, str], categoria: str, titulo: str) -> None:
    """Escribe la evolucion anual segmentada con formulas COUNTIFS."""
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:D1")
    headers = ["Año Cohorte", "Tamaño Cohorte (N)", "Alumnos Retenidos", "Tasa Retención %"]
    ws.append(headers)
    estilo_encabezado(ws, 2, len(headers))
    anios = sorted(
        detalle.loc[
            detalle["nivel_carrera_2"].fillna("").eq(categoria), "cat_periodo"
        ].dropna().unique()
    )
    for row, anio in enumerate(anios, 3):
        ws.cell(row, 1, int(anio))
        criterio = (
            f"'Detalle_Raw'!{cols['NIVEL_CARRERA_2']}:{cols['NIVEL_CARRERA_2']},\"{categoria}\","
            f"'Detalle_Raw'!{cols['CAT_PERIODO']}:{cols['CAT_PERIODO']},A{row},"
            f"'Detalle_Raw'!{cols['RETENIDO_INST']}:{cols['RETENIDO_INST']},\"<>\""
        )
        ws.cell(row, 2, f"=COUNTIFS({criterio})")
        criterio_retenidos = criterio[:-5] + "1"
        ws.cell(row, 3, f"=COUNTIFS({criterio_retenidos})")
        ws.cell(row, 4, f"=IFERROR(C{row}/B{row},0)")
        ws.cell(row, 2).number_format = ws.cell(row, 3).number_format = "#,##0"
        ws.cell(row, 4).number_format = "0.0%"
    total_row = ws.max_row + 1
    ws.cell(total_row, 1, "TOTAL GENERAL")
    ws.cell(total_row, 2, f"=SUM(B3:B{total_row - 1})")
    ws.cell(total_row, 3, f"=SUM(C3:C{total_row - 1})")
    ws.cell(total_row, 4, f"=IFERROR(C{total_row}/B{total_row},0)")
    aplicar_estilo_total(ws, total_row, 4)
    chart = LineChart()
    chart.title = f"Evolución de Retención: {categoria}"
    chart.y_axis.title = "Tasa Retención %"
    chart.x_axis.title = "Año Cohorte"
    chart.y_axis.numFmt = "0%"
    chart.add_data(Reference(ws, min_col=4, min_row=2, max_row=total_row - 1), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=3, max_row=total_row - 1))
    chart.height = 8
    chart.width = 16
    ws.add_chart(chart, "F2")
    ws.freeze_panes = "A3"
    ws.sheet_view.showGridLines = True
    ajustar_ancho(ws)


def criterio_postgrado(cols: dict[str, str], row: int, retenidos: bool = False) -> str:
    flag = f",'Detalle_Raw'!{cols['RETENIDO_INST']}:{cols['RETENIDO_INST']},"
    flag += "1" if retenidos else '"<>"'
    partes = []
    for nivel in ("Postgrado", "Postítulo"):
        partes.append(
            f"COUNTIFS('Detalle_Raw'!{cols['NIVEL_GLOBAL']}:{cols['NIVEL_GLOBAL']},\"{nivel}\","
            f"'Detalle_Raw'!{cols['CAT_PERIODO']}:{cols['CAT_PERIODO']},A{row}"
            f"{flag})"
        )
    return " + ".join(partes)


def escribir_postgrado_anual(ws, detalle: pd.DataFrame, cols: dict[str, str]) -> None:
    ws["A1"] = "Evolución de Retención de Postgrados y Postítulos - IP"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:D1")
    ws.append(["Año Cohorte", "Tamaño Cohorte (N)", "Alumnos Retenidos", "Tasa Retención %"])
    estilo_encabezado(ws, 2, 4)
    anios = sorted(detalle.loc[detalle["nivel_global"].isin(["Postgrado", "Postítulo"]), "cat_periodo"].dropna().unique())
    for row, anio in enumerate(anios, 3):
        ws.cell(row, 1, int(anio))
        ws.cell(row, 2, f"={criterio_postgrado(cols, row)}")
        ws.cell(row, 3, f"={criterio_postgrado(cols, row, True)}")
        ws.cell(row, 4, f"=IFERROR(C{row}/B{row},0)")
        ws.cell(row, 2).number_format = ws.cell(row, 3).number_format = "#,##0"
        ws.cell(row, 4).number_format = "0.0%"
    total_row = ws.max_row + 1
    ws.cell(total_row, 1, "TOTAL GENERAL")
    ws.cell(total_row, 2, f"=SUM(B3:B{total_row - 1})")
    ws.cell(total_row, 3, f"=SUM(C3:C{total_row - 1})")
    ws.cell(total_row, 4, f"=IFERROR(C{total_row}/B{total_row},0)")
    aplicar_estilo_total(ws, total_row, 4)
    chart = LineChart()
    chart.title = "Evolución de Retención: Postgrados y Postítulos"
    chart.y_axis.title = "Tasa Retención %"
    chart.x_axis.title = "Año Cohorte"
    chart.y_axis.numFmt = "0%"
    chart.add_data(Reference(ws, min_col=4, min_row=2, max_row=total_row - 1), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=3, max_row=total_row - 1))
    chart.height = 8
    chart.width = 16
    ws.add_chart(chart, "F2")
    ws.freeze_panes = "A3"
    ws.sheet_view.showGridLines = True
    ajustar_ancho(ws)


def escribir_postgrado_carrera(ws, detalle: pd.DataFrame, cols: dict[str, str]) -> None:
    ws["A1"] = "Retención de Carreras de Postgrado y Postítulo"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")
    ws.append(["Año Cohorte", "Código Carrera", "Nombre Carrera", "Tamaño Cohorte (N)", "Alumnos Retenidos", "Tasa Retención %"])
    estilo_encabezado(ws, 2, 6)
    grupos = detalle[detalle["nivel_global"].isin(["Postgrado", "Postítulo"])][["cat_periodo", "cod_carrera", "nomb_carrera"]].drop_duplicates().sort_values(["cat_periodo", "cod_carrera", "nomb_carrera"])
    for row, (_, item) in enumerate(grupos.iterrows(), 3):
        ws.cell(row, 1, int(item["cat_periodo"]))
        ws.cell(row, 2, valor_excel(item["cod_carrera"]))
        ws.cell(row, 3, valor_excel(item["nomb_carrera"]))
        criteria = []
        criteria_ret = []
        for nivel in ("Postgrado", "Postítulo"):
            base = f"'Detalle_Raw'!{cols['NIVEL_GLOBAL']}:{cols['NIVEL_GLOBAL']},\"{nivel}\",'Detalle_Raw'!{cols['CAT_PERIODO']}:{cols['CAT_PERIODO']},A{row},'Detalle_Raw'!{cols['COD_CARRERA']}:{cols['COD_CARRERA']},B{row}"
            criteria.append(f"COUNTIFS({base},'Detalle_Raw'!{cols['RETENIDO_CARRERA']}:{cols['RETENIDO_CARRERA']},\"<>\")")
            criteria_ret.append(f"COUNTIFS({base},'Detalle_Raw'!{cols['RETENIDO_CARRERA']}:{cols['RETENIDO_CARRERA']},1)")
        ws.cell(row, 4, "=" + " + ".join(criteria))
        ws.cell(row, 5, "=" + " + ".join(criteria_ret))
        ws.cell(row, 6, f"=IFERROR(E{row}/D{row},0)")
        ws.cell(row, 4).number_format = ws.cell(row, 5).number_format = "#,##0"
        ws.cell(row, 6).number_format = "0.0%"
    total_row = ws.max_row + 1
    ws.cell(total_row, 1, "TOTAL GENERAL")
    ws.cell(total_row, 4, f"=SUM(D3:D{total_row - 1})")
    ws.cell(total_row, 5, f"=SUM(E3:E{total_row - 1})")
    ws.cell(total_row, 6, f"=IFERROR(E{total_row}/D{total_row},0)")
    aplicar_estilo_total(ws, total_row, 6)
    ws.freeze_panes = "A3"
    ws.sheet_view.showGridLines = True
    ajustar_ancho(ws)


def main() -> None:
    detalle = construir_detalle_completo(aplicar_diccionario_tipo_carrera(cargar_base(FUENTE)))
    detalle = detalle.replace({pd.NA: None, np.nan: None})
    wb = Workbook()
    raw = wb.active
    raw.title = "Detalle_Raw"
    raw.sheet_view.showGridLines = True
    raw.append(list(detalle.columns))
    for row in detalle.itertuples(index=False, name=None):
        raw.append([None if pd.isna(value) else value for value in row])
    estilo_encabezado(raw, 1, raw.max_column)
    raw.freeze_panes = "A2"
    raw.auto_filter.ref = raw.dimensions
    raw_table = Table(displayName="DetalleRaw", ref=raw.dimensions)
    raw_table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False)
    raw.add_table(raw_table)

    cols = mapa_columnas(raw)
    anios, carreras, programas = preparar_resumenes(detalle)
    for sheet_name, writer, rows, level in [
        ("Retencion_Institucional", escribir_institucional, anios, "institucional"),
        ("Retencion_Por_Carrera", escribir_apertura, carreras, "carrera"),
        ("Retencion_Por_Programa", escribir_apertura, programas, "programa"),
    ]:
        ws = wb.create_sheet(sheet_name)
        ws.sheet_view.showGridLines = True
        ws.freeze_panes = "A2"
        if level == "institucional":
            writer(ws, rows, cols)
        else:
            writer(ws, rows, cols, level)
        ajustar_ancho(ws)

    escribir_segmento_anual(
        wb.create_sheet("Evol_Ret_Tecnicas_IP"), detalle, cols,
        "Carreras Técnicas",
        "Evolución de Retención de 1er año de carreras técnicas - IP",
    )
    escribir_segmento_anual(
        wb.create_sheet("Evol_Ret_Profesionales_IP"), detalle, cols,
        "Carreras Profesionales",
        "Evolución de Retención de 1er año de carreras profesionales - IP",
    )
    escribir_segmento(
        wb.create_sheet("Ret_Carrera_Tec_IP"), detalle, cols,
        "Carreras Técnicas",
        "Evolución de Retención de Carreras Técnicas (Detalle Carrera)",
        "carrera",
    )
    escribir_segmento(
        wb.create_sheet("Ret_Carrera_Prof_IP"), detalle, cols,
        "Carreras Profesionales",
        "Evolución de Retención de Carreras Profesionales (Detalle Carrera)",
        "carrera",
    )
    escribir_postgrado_anual(wb.create_sheet("Evol_Ret_Postgrados_IP"), detalle, cols)
    escribir_postgrado_carrera(wb.create_sheet("Ret_Carrera_Post_IP"), detalle, cols)

    ajustar_ancho(raw)
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.save(ARCHIVO_SALIDA)
    print(f"Filas originales preservadas: {len(detalle):,}")
    print(f"Columnas originales + flags: {len(detalle.columns)}")
    print(f"Filas evaluables: {int(detalle['RETENIDO_INST'].notna().sum()):,}")
    print(f"Archivo generado: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()