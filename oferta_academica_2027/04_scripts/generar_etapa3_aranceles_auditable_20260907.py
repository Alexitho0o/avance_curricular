#!/usr/bin/env python3
from __future__ import annotations

import csv
import shutil
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from generar_etapa3_aranceles_20260907 import (
    ALIAS,
    COLUMNAS_5910,
    COLUMNAS_ETAPA3,
    CONFIRMADOS_USUARIO,
    IDX,
    REPORTE_5910,
    TABLA_ARANCELES,
    buscar_arancel,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "07_resultados" / "etapa3_aranceles_20260907"
XLSX_OUT = OUT_DIR / "OFERTA_ACADEMICA_ARANCELES_2027_AUDITABLE_CON_FORMULAS_20260907.xlsx"
CSV_OUT = OUT_DIR / "OFERTA_ACADEMICA_ARANCELES_2027_SIN_TITULOS_20260907.csv"
DESKTOP_XLSX = Path.home() / "Desktop" / XLSX_OUT.name
DESKTOP_CSV = Path.home() / "Desktop" / CSV_OUT.name
CONVENTIONAL_XLSX = OUT_DIR / "OFERTA_ACADEMICA_ARANCELES_2027_CON_TITULOS_20260907.xlsx"
DESKTOP_CONVENTIONAL_XLSX = Path.home() / "Desktop" / CONVENTIONAL_XLSX.name

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def read_5910() -> tuple[list[str], list[list[str]]]:
    with REPORTE_5910.open("r", encoding="latin-1", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=";"))
    return rows[0], rows[1:]


def write_headers(ws, headers: list[str]) -> None:
    for col, header in enumerate(headers, 1):
        cell = ws.cell(1, col, header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT


def formula_sheet_ref(sheet: str, col: int, row: int) -> str:
    return f"'{sheet}'!{get_column_letter(col)}{row}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    header_5910, rows_5910 = read_5910()
    header_idx = {name: i for i, name in enumerate(header_5910)}

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # Raw 5910: fuente validada sin modificar.
    raw = wb.create_sheet("Raw_5910")
    write_headers(raw, header_5910)
    for row_number, row in enumerate(rows_5910, 2):
        for col, value in enumerate(row, 1):
            raw.cell(row_number, col, value)
    raw.freeze_panes = "A2"
    raw.auto_filter.ref = raw.dimensions

    # Raw de la imagen: esta es la transcripcion auditable de la fuente visual.
    table = wb.create_sheet("Raw_Tabla_Imagen")
    table_headers = ["NOMBRE_TABLA", "2|D", "2|V", "2|SP", "3|D", "3|V", "3|SP", "4|D", "4|V", "4|SP", "OL"]
    write_headers(table, table_headers)
    for row_number, (name, values) in enumerate(TABLA_ARANCELES.items(), 2):
        table.cell(row_number, 1, name)
        for col, value in enumerate(values, 2):
            table.cell(row_number, col, value)
    table.freeze_panes = "A2"
    table.auto_filter.ref = table.dimensions

    # Alias explícitos: el MATCH no "adivina" nombres abreviados.
    aliases = wb.create_sheet("Alias_Nombres")
    write_headers(aliases, ["NOMBRE_5910", "NOMBRE_TABLA", "MOTIVO"])
    exact_names = set(TABLA_ARANCELES) - set(ALIAS)
    alias_rows = [(name, name, "Nombre exacto") for name in sorted(exact_names)]
    alias_rows += [(full_name, table_name, "Alias explícito revisado") for table_name, full_name in sorted(ALIAS.items())]
    for row_number, values in enumerate(alias_rows, 2):
        for col, value in enumerate(values, 1):
            aliases.cell(row_number, col, value)
    aliases.freeze_panes = "A2"
    aliases.auto_filter.ref = aliases.dimensions

    params = wb.create_sheet("Parametros")
    write_headers(params, ["PARAMETRO", "VALOR", "FUENTE"])
    param_rows = [
        ("FORMATO_VALOR", 1, "Anexo 3: 1 = pesos chilenos"),
        ("VALOR_MATRICULA_ANUAL", 185000, "Patron observado en los 103 registros Etapa 1"),
        ("COSTO_TITULACION", 0, "Patron observado en los 103 registros Etapa 1"),
        ("VALOR_CERTIFICADO_DIPLOMA", 0, "Patron observado en los 103 registros Etapa 1"),
    ]
    for row_number, values in enumerate(param_rows, 2):
        for col, value in enumerate(values, 1):
            params.cell(row_number, col, value)

    # Hoja con formulas visibles. Las columnas A-G y M se traen desde Raw_5910.
    calc = wb.create_sheet("Calculo_Formulas")
    calc_headers = COLUMNAS_ETAPA3 + [
        "NOMBRE_TABLA_BUSCADO", "COLUMNA_SEDE_JORNADA", "FILA_TABLA_MATCH", "ARANCEL_FORMULA", "ESTADO_CRUCE"
    ]
    write_headers(calc, calc_headers)
    calc.freeze_panes = "A2"

    raw_col = {name: index + 1 for index, name in enumerate(header_5910)}
    table_last = len(TABLA_ARANCELES) + 1
    alias_last = len(alias_rows) + 1
    for out_row, source_row in enumerate(rows_5910, 2):
        # Identificadores y vigencia: formulas directas contra el 5910 raw.
        for out_col, field in enumerate(COLUMNAS_ETAPA3[:7], 1):
            calc.cell(out_row, out_col, f"={formula_sheet_ref('Raw_5910', raw_col[field], source_row and out_row)}")
        calc.cell(out_row, 13, f"={formula_sheet_ref('Raw_5910', raw_col['VIGENCIA_CARRERA'], out_row)}")

        # Nombre equivalente: INDEX/MATCH explícito contra la hoja de alias.
        calc.cell(out_row, 14, f'=IFERROR(INDEX(Alias_Nombres!$B$2:$B${alias_last},MATCH(D{out_row},Alias_Nombres!$A$2:$A${alias_last},0)),"NO_HAY_ALIAS")')
        calc.cell(out_row, 15, f'=IF(AND(E{out_row}=3,F{out_row}=4),"OL",E{out_row}&"|"&IF(F{out_row}=1,"D",IF(F{out_row}=2,"V","SP")))')
        calc.cell(out_row, 16, f'=IFERROR(MATCH(N{out_row},Raw_Tabla_Imagen!$A$2:$A${table_last},0)+1,"NO_MATCH")')

        # Campos modificables: formulas contra Parametros y arancel por INDEX/MATCH.
        calc.cell(out_row, 8, f'=IF(M{out_row}<>1,{formula_sheet_ref("Raw_5910", raw_col["FORMATO_VALOR"], out_row)},INDEX(Parametros!$B:$B,MATCH("FORMATO_VALOR",Parametros!$A:$A,0)))')
        calc.cell(out_row, 9, f'=IF(M{out_row}<>1,{formula_sheet_ref("Raw_5910", raw_col["VALOR_MATRICULA_ANUAL"], out_row)},INDEX(Parametros!$B:$B,MATCH("VALOR_MATRICULA_ANUAL",Parametros!$A:$A,0)))')
        calc.cell(out_row, 10, f'=IF(M{out_row}<>1,{formula_sheet_ref("Raw_5910", raw_col["COSTO_TITULACION"], out_row)},INDEX(Parametros!$B:$B,MATCH("COSTO_TITULACION",Parametros!$A:$A,0)))')
        calc.cell(out_row, 11, f'=IF(M{out_row}<>1,{formula_sheet_ref("Raw_5910", raw_col["VALOR_CERTIFICADO_DIPLOMA"], out_row)},INDEX(Parametros!$B:$B,MATCH("VALOR_CERTIFICADO_DIPLOMA",Parametros!$A:$A,0)))')
        formula = (
            f'=IF(M{out_row}<>1,{formula_sheet_ref("Raw_5910", raw_col["ARANCEL_ANUAL"], out_row)},IFERROR(IF(O{out_row}="OL",'
            f'INDEX(Raw_Tabla_Imagen!$K$2:$K${table_last},MATCH(N{out_row},Raw_Tabla_Imagen!$A$2:$A${table_last},0)),'
            f'INDEX(Raw_Tabla_Imagen!$B$2:$J${table_last},MATCH(N{out_row},Raw_Tabla_Imagen!$A$2:$A${table_last},0),MATCH(O{out_row},Raw_Tabla_Imagen!$B$1:$J$1,0))),"REVISAR_SIN_MATCH"))'
        )
        calc.cell(out_row, 12, formula)
        calc.cell(out_row, 17, f'=FORMULATEXT(L{out_row})')
        calc.cell(out_row, 18, f'=IF(L{out_row}="REVISAR_SIN_MATCH","REVISAR",IF(L{out_row}="","SIN_VALOR", "OK_FORMULA"))')

    # Hoja de carga: solo formulas que proyectan las 13 columnas calculadas.
    carga = wb.create_sheet("Carga_13_Columnas")
    write_headers(carga, COLUMNAS_ETAPA3)
    for row_number in range(2, len(rows_5910) + 2):
        for col in range(1, 14):
            carga.cell(row_number, col, f"=Calculo_Formulas!{get_column_letter(col)}{row_number}")
    carga.freeze_panes = "A2"
    carga.auto_filter.ref = carga.dimensions

    # Resumen formula-driven, sin afirmar que los valores estan pegados.
    resumen = wb.create_sheet("Resumen", 0)
    resumen.sheet_view.showGridLines = False
    summary = [
        ("Libro auditable Etapa 3 - Aranceles 2027", None),
        ("Fuente de programas", "Raw_5910"),
        ("Fuente visual transcrita", "Raw_Tabla_Imagen"),
        ("Equivalencias de nombres", "Alias_Nombres"),
        ("Logica principal", "INDEX/MATCH por nombre equivalente + sede/modalidad/jornada"),
        ("", None),
        ("Filas 5910", "=COUNTA(Raw_5910!A2:A141)"),
        ("Filas de carga calculada", "=COUNTA(Carga_13_Columnas!A2:A141)"),
        ("Filas con estado OK_FORMULA", '=COUNTIF(Calculo_Formulas!R2:R141,"OK_FORMULA")'),
        ("Filas a revisar", '=COUNTIF(Calculo_Formulas!R2:R141,"REVISAR")'),
        ("Filas sin valor", '=COUNTIF(Calculo_Formulas!R2:R141,"SIN_VALOR")'),
        ("", None),
        ("Formula de arancel", "=IF(M2<>1,0,IFERROR(IF(O2=\"OL\",INDEX(Raw_Tabla_Imagen!$K$2:$K$29,MATCH(N2,Raw_Tabla_Imagen!$A$2:$A$29,0)),INDEX(Raw_Tabla_Imagen!$B$2:$J$29,MATCH(N2,Raw_Tabla_Imagen!$A$2:$A$29,0),MATCH(O2,Raw_Tabla_Imagen!$B$1:$J$1,0))),\"REVISAR_SIN_MATCH\"))"),
        ("Nota", "El CSV se materializa desde la misma logica Python para carga; este XLSX permite auditar la logica mediante las formulas visibles y FORMULATEXT."),
    ]
    for row_number, (label, value) in enumerate(summary, 1):
        resumen.cell(row_number, 1, label)
        if value is not None:
            resumen.cell(row_number, 2, value)
        if value is None and label:
            resumen.cell(row_number, 1).font = Font(bold=True)
    resumen.column_dimensions["A"].width = 34
    resumen.column_dimensions["B"].width = 120

    for ws in wb.worksheets:
        if ws.title not in {"Resumen"}:
            for col in range(1, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(col)].width = max(14, min(42, len(str(ws.cell(1, col).value or "")) + 4))

    # CSV materializado con el mismo resolver, dejando el XLSX como prueba de la formula.
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", lineterminator="\n")
        for row in rows_5910:
            name, sede, career, modality, journey = row[header_idx["NOMBRE_CARRERA"]], row[header_idx["COD_SEDE"]], row[header_idx["COD_CARRERA"]], row[header_idx["MODALIDAD"]], row[header_idx["COD_JORNADA"]]
            if row[header_idx["VIGENCIA_CARRERA"]] == "1":
                value, _ = buscar_arancel(name, sede, career, modality, journey)
                arancel = str(value) if value != "FALTA" else "-1"
                values = [sede, row[header_idx["NOMBRE_SEDE"]], career, name, modality, journey, row[header_idx["VERSION"]], "1", "185000", "0", "0", arancel, row[header_idx["VIGENCIA_CARRERA"]]]
            else:
                values = [sede, row[header_idx["NOMBRE_SEDE"]], career, name, modality, journey, row[header_idx["VERSION"]], row[header_idx["FORMATO_VALOR"]], row[header_idx["VALOR_MATRICULA_ANUAL"]], row[header_idx["COSTO_TITULACION"]], row[header_idx["VALOR_CERTIFICADO_DIPLOMA"]], row[header_idx["ARANCEL_ANUAL"]], row[header_idx["VIGENCIA_CARRERA"]]]
            writer.writerow(values)
    content = CSV_OUT.read_text(encoding="utf-8")
    if content.endswith("\n"):
        CSV_OUT.write_text(content[:-1], encoding="utf-8")

    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    wb.save(XLSX_OUT)
    shutil.copy2(XLSX_OUT, DESKTOP_XLSX)
    shutil.copy2(XLSX_OUT, CONVENTIONAL_XLSX)
    shutil.copy2(XLSX_OUT, DESKTOP_CONVENTIONAL_XLSX)
    shutil.copy2(CSV_OUT, DESKTOP_CSV)
    print("XLSX auditable:", XLSX_OUT)
    print("CSV materializado:", CSV_OUT)


if __name__ == "__main__":
    main()
