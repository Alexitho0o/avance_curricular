# Perfilamiento tecnico (Fase 2) - Entrega Etapa 2 (Oferta Academica Nueva TP Adscritas) 20260827
# No modifica el archivo original. Solo lectura.
import json, re, datetime, sys
import openpyxl
from collections import Counter, defaultdict

SRC = "/root/mnt_placeholder"  # se sobreescribe abajo
import os
BASE = os.path.expanduser("~/mnt/avance_curricular/oferta_academica_2027")
SRC = os.path.join(BASE, "03_fuentes_institucionales/entregas_docencia/20260827_etapa2_entrega_01/Oferta 2027 Etapa2_prueba_1.xlsx")
OUT_DIR = os.path.join(BASE, "06_validaciones")
STAMP = "20260827_etapa2_entrega01"

wb = openpyxl.load_workbook(SRC, data_only=False)
wb_values = openpyxl.load_workbook(SRC, data_only=True)

profile = {
    "archivo": os.path.basename(SRC),
    "ruta": SRC,
    "generado": datetime.datetime.now().isoformat(),
    "hojas": {}
}

INVISIBLE_RE = re.compile(r'^\s+|\s+$|\s{2,}|[ ​‌‍﻿]')

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    wsv = wb_values[sheet_name]
    max_row, max_col = ws.max_row, ws.max_column

    # Encabezados (fila 1)
    headers = []
    for c in range(1, max_col+1):
        v = ws.cell(row=1, column=c).value
        headers.append(v)

    # filas no vacias (excluyendo encabezado), columnas vacias
    non_empty_rows = 0
    empty_rows = []
    col_nonempty_count = [0]*(max_col+1)
    col_types = defaultdict(Counter)
    col_unique_vals = defaultdict(Counter)
    col_text_numbers = defaultdict(int)  # valores numericos guardados como texto
    col_invisible_spaces = defaultdict(int)
    formula_cells = []
    comment_cells = []
    colored_cells = defaultdict(list)  # color -> list of coords
    excel_errors = []
    hidden_rows = []
    hidden_cols = []

    # columnas ocultas
    for c in range(1, max_col+1):
        letter = openpyxl.utils.get_column_letter(c)
        dim = ws.column_dimensions.get(letter)
        if dim is not None and dim.hidden:
            hidden_cols.append(letter)

    for r in range(2, max_row+1):
        row_dim = ws.row_dimensions.get(r)
        if row_dim is not None and row_dim.hidden:
            hidden_rows.append(r)

        row_all_empty = True
        for c in range(1, max_col+1):
            cell = ws.cell(row=r, column=c)
            vcell = wsv.cell(row=r, column=c)
            val = cell.value
            val_computed = vcell.value

            if val is not None and str(val).strip() != "":
                row_all_empty = False
                col_nonempty_count[c] += 1

            # formulas
            if isinstance(val, str) and val.startswith("="):
                formula_cells.append({"celda": f"{openpyxl.utils.get_column_letter(c)}{r}", "columna": headers[c-1], "formula": val})

            # comentarios
            if cell.comment is not None:
                comment_cells.append({"celda": f"{openpyxl.utils.get_column_letter(c)}{r}", "columna": headers[c-1], "comentario": str(cell.comment.text)[:200]})

            # colores de relleno (fill)
            try:
                fill = cell.fill
                if fill is not None and fill.fgColor is not None:
                    rgb = fill.fgColor.rgb
                    if rgb and rgb not in ("00000000", None) and fill.patternType not in (None,):
                        colored_cells[str(rgb)].append(f"{openpyxl.utils.get_column_letter(c)}{r}")
            except Exception:
                pass

            # errores de excel (valores calculados tipo #N/A, #REF!, etc.)
            if isinstance(val_computed, str) and val_computed.startswith("#"):
                excel_errors.append({"celda": f"{openpyxl.utils.get_column_letter(c)}{r}", "columna": headers[c-1], "valor": val_computed})

            # tipos observados y valores unicos (usar valor computado si es formula)
            eff_val = val_computed if isinstance(val, str) and val.startswith("=") else val
            tname = type(eff_val).__name__ if eff_val is not None else "NoneType"
            col_types[c][tname] += 1

            if isinstance(eff_val, str):
                if INVISIBLE_RE.search(eff_val):
                    col_invisible_spaces[c] += 1
                stripped = eff_val.strip()
                if stripped != "" and re.match(r'^-?\d+([.,]\d+)?$', stripped):
                    col_text_numbers[c] += 1
                if eff_val.strip() != "":
                    col_unique_vals[c][eff_val.strip()] += 1
            elif eff_val is not None:
                col_unique_vals[c][str(eff_val)] += 1

        if row_all_empty:
            empty_rows.append(r)
        else:
            non_empty_rows += 1

    empty_cols = [openpyxl.utils.get_column_letter(c) for c in range(1, max_col+1) if col_nonempty_count[c] == 0]

    # duplicados: por fila completa (tupla de valores) y clave diagnostica simple (si existen columnas reconocibles)
    row_tuples = []
    for r in range(2, max_row+1):
        tup = tuple(ws.cell(row=r, column=c).value for c in range(1, max_col+1))
        row_tuples.append((r, tup))
    tup_counter = Counter(t for _, t in row_tuples)
    dup_full_rows = [r for r, t in row_tuples if tup_counter[t] > 1]

    # tipos observados por columna, resumido
    col_summary = []
    for c in range(1, max_col+1):
        letter = openpyxl.utils.get_column_letter(c)
        types_c = dict(col_types[c])
        uniq = col_unique_vals[c]
        is_categorical = 0 < len(uniq) <= 25
        col_summary.append({
            "posicion": c,
            "letra": letter,
            "encabezado": headers[c-1],
            "no_vacios": col_nonempty_count[c],
            "vacios": (max_row - 1) - col_nonempty_count[c],
            "tipos_observados": types_c,
            "valores_unicos_n": len(uniq),
            "categorica": is_categorical,
            "valores_unicos_muestra": dict(uniq.most_common(25)) if is_categorical else None,
            "numeros_almacenados_como_texto": col_text_numbers.get(c, 0),
            "celdas_con_espacios_invisibles": col_invisible_spaces.get(c, 0),
        })

    profile["hojas"][sheet_name] = {
        "dimensiones": ws.dimensions,
        "max_fila": max_row,
        "max_columna": max_col,
        "filas_totales_incluye_encabezado": max_row,
        "filas_de_datos_no_vacias": non_empty_rows,
        "filas_completamente_vacias": empty_rows,
        "columnas_vacias": empty_cols,
        "columnas_ocultas": hidden_cols,
        "filas_ocultas": hidden_rows,
        "celdas_combinadas": [str(r) for r in ws.merged_cells.ranges],
        "filas_duplicadas_completas": sorted(set(dup_full_rows)),
        "celdas_con_formula": formula_cells,
        "celdas_con_comentario": comment_cells,
        "colores_relleno_usados": {k: {"n_celdas": len(v), "muestra": v[:10]} for k, v in colored_cells.items()},
        "errores_excel_detectados": excel_errors,
        "columnas": col_summary,
    }

os.makedirs(OUT_DIR, exist_ok=True)
json_path = os.path.join(OUT_DIR, f"PERFIL_ENTREGA_ETAPA2_{STAMP}.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(profile, f, ensure_ascii=False, indent=2, default=str)

# TSV resumido (por columna)
tsv_path = os.path.join(OUT_DIR, f"PERFIL_ENTREGA_ETAPA2_{STAMP}.tsv")
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("hoja\tposicion\tletra\tencabezado\tno_vacios\tvacios\ttipos_observados\tvalores_unicos_n\tnumeros_como_texto\tespacios_invisibles\n")
    for sheet_name, data in profile["hojas"].items():
        for col in data["columnas"]:
            f.write(f"{sheet_name}\t{col['posicion']}\t{col['letra']}\t{col['encabezado']}\t{col['no_vacios']}\t{col['vacios']}\t{col['tipos_observados']}\t{col['valores_unicos_n']}\t{col['numeros_almacenados_como_texto']}\t{col['celdas_con_espacios_invisibles']}\n")

print("JSON:", json_path)
print("TSV:", tsv_path)
print("OK")
