#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Auditoría Trazable de Nacionalidad - 257 Registros
Estudiantes Extranjeros Regulares 2026
"""

import csv
import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

TS = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
BASE = Path("/Users/alexi/Documents/GitHub/avance_curricular")
EE = BASE / "estudiantes_extranjeros_2026"

F_UNIVERSO   = EE / "resultados/auditorias/UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv"
F_PREC_ORIG  = EE / "data/raw/REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv"
F_PREC_NORM  = EE / "data/interim/PRECARGA_EXTRANJEROS_REGULARES_2026_NORMALIZADA.csv"
F_PROMEDIOS  = BASE / "input/PROMEDIOSDEALUMNOS_7804.xlsx"
F_MAT_CTRL   = BASE / "resultados/matricula_avance_curricular_2025_control.csv"
F_EXCEL_OUT  = EE / "resultados/auditorias/AUDITORIA_TRAZABLE_NACIONALIDAD_257.xlsx"
F_INSPECCION = EE / "resultados/auditorias/INSPECCION_PROMEDIOS_ALUMNOS_DATOS_PERSONALES.csv"
F_AUD_GEN    = EE / "resultados/auditorias/AUDITORIA_GENERACION_EXCEL_NACIONALIDAD_257.csv"
F_REPORTE    = EE / "resultados/reportes/REPORTE_AUDITORIA_NACIONALIDAD_257.md"

TBL_UNIV  = "tblUniverso257"
TBL_SIES  = "tblPrecargaSIES"
TBL_DA    = "tblDatosAlumnos"
TBL_MAT   = "tblMatricula2025"
TBL_TRAZ  = "tblTrazabilidad"
TBL_PRIO  = "tblPrioritarios"
TBL_CONF  = "tblConflictos"

# ── colour palette ─────────────────────────────────────────────────────────
C = {
    "hdr_raw":     "1F3864", "hdr_frm":    "375623", "hdr_ctrl":  "4A235A",
    "raw_bg":      "DCE6F1", "frm_bg":     "EBF1DE", "ctrl_bg":   "E8D5F5",
    "conflict":    "FF0000", "pending":    "FFD966", "ok":        "92D050",
    "no_data":     "D3D3D3", "prio1":      "FF0000", "prio2":     "FF9900",
    "prio3":       "FFFF00", "white":      "FFFFFF", "txt_white": "FFFFFF",
}

def fhash(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(8192): h.update(chunk)
    return h.hexdigest()[:16]

def hdr_style(bg, bold=True):
    return dict(
        font=Font(bold=bold, color=C["txt_white"], size=10),
        fill=PatternFill("solid", fgColor=bg),
        alignment=Alignment(horizontal="center", vertical="center", wrap_text=True),
        border=Border(**{s: Side(style="thin", color="808080")
                         for s in ("left","right","top","bottom")}),
    )

def cell_style(bg, fmt=None):
    s = dict(
        fill=PatternFill("solid", fgColor=bg),
        alignment=Alignment(vertical="center", wrap_text=False),
    )
    if fmt: s["number_format"] = fmt
    return s

def apply(cell, **kw):
    for k, v in kw.items(): setattr(cell, k, v)

def applydict(cell, d):
    for k, v in d.items(): setattr(cell, k, v)

def col(ws, i): return get_column_letter(i)

def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def freeze(ws, cell="A2"):
    ws.freeze_panes = cell

def autofilter(ws):
    if ws.max_row > 1:
        ws.auto_filter.ref = ws.dimensions

def make_table(ws, name, ref, style="TableStyleMedium2"):
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name=style, showFirstColumn=False,
                                      showLastColumn=False, showRowStripes=True,
                                      showColumnStripes=False)
    ws.add_table(t)

def norm_doc(v):
    if not v: return ""
    return str(v).replace(".","").replace("-","").replace(" ","").strip().upper()

def rut_num(v):
    v = str(v).strip() if v else ""
    return v.split("-")[0].replace(".","").strip()

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — load sources
# ══════════════════════════════════════════════════════════════════════════════

def load_universo():
    with open(F_UNIVERSO, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_precarga():
    with open(F_PREC_ORIG, encoding="latin-1") as f:
        return list(csv.DictReader(f, delimiter=";"))

def load_precarga_norm():
    with open(F_PREC_NORM, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_datos_alumnos():
    wb = openpyxl.load_workbook(F_PROMEDIOS, read_only=True, data_only=True)
    ws = wb["DatosAlumnos"]
    rows_iter = ws.iter_rows(values_only=True)
    raw_headers = list(next(rows_iter))
    headers = []
    seen = {}
    for i, h in enumerate(raw_headers):
        if h is None:
            h = f"_COL{i+1}"
        h = str(h).strip()
        if h in seen:
            seen[h] += 1
            h = f"{h}_{seen[h]}"
        else:
            seen[h] = 0
        headers.append(h)
    data = [list(row) for row in rows_iter]
    wb.close()
    return headers, data

def load_matricula_ctrl():
    rows = []
    with open(F_MAT_CTRL, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def build_sies_key(row):
    t = str(row.get("TIPO_DOCUMENTO","")).strip()
    n = str(row.get("NUM_DOCUMENTO","")).strip()
    cu = str(row.get("CODIGO_UNICO","")).strip()
    return f"{t}|{n}|{cu}"

def build_sies_person_key(row):
    t = str(row.get("TIPO_DOCUMENTO","")).strip()
    n = str(row.get("NUM_DOCUMENTO","")).strip()
    return f"{t}|{n}"

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — cross-references
# ══════════════════════════════════════════════════════════════════════════════

def compute_xrefs(univ, sies, da_headers, da_data):
    # Build SIES index: CLAVE_PERSONA_CARRERA → (row_in_table_1indexed, row_obj)
    sies_by_pcc = {}
    for i, s in enumerate(sies):
        k = build_sies_key(s)
        if k not in sies_by_pcc:
            sies_by_pcc[k] = (i+1, s)   # 1-indexed table row

    # Build DatosAlumnos indexes
    da_codcli_col = da_headers.index("CODCLI") if "CODCLI" in da_headers else None
    da_rut_col    = da_headers.index("RUT")    if "RUT"    in da_headers else None
    da_nac_col    = da_headers.index("NACIONALIDAD") if "NACIONALIDAD" in da_headers else None

    da_by_codcli = {}
    da_by_rutnum = {}
    for i, row in enumerate(da_data):
        codcli = str(row[da_codcli_col]).strip() if da_codcli_col is not None and row[da_codcli_col] else ""
        rut    = str(row[da_rut_col]).strip()    if da_rut_col    is not None and row[da_rut_col]    else ""
        tbl_row = i + 1  # 1-indexed table row (data only, header excluded)
        if codcli and codcli not in da_by_codcli:
            da_by_codcli[codcli] = tbl_row
        if rut:
            rn = rut_num(rut)
            if rn and rn not in da_by_rutnum:
                da_by_rutnum[rn] = tbl_row

    xrefs = []
    for u in univ:
        cpd = u.get("CLAVE_PERSONA_CARRERA","").strip()
        codcli_u = u.get("CODCLI","").strip()
        clave_doc = u.get("CLAVE_PERSONA_DOCUMENTO","").strip()

        # SIES match
        sies_row, sies_obj = sies_by_pcc.get(cpd, (0, None))

        # DA match
        da_row = 0
        da_method = "NO_MATCH"
        if codcli_u and codcli_u in da_by_codcli:
            da_row = da_by_codcli[codcli_u]
            da_method = "CODCLI"
        else:
            num = clave_doc.split("|")[1] if "|" in clave_doc else ""
            if num and num in da_by_rutnum:
                da_row = da_by_rutnum[num]
                da_method = "RUT_NUM"

        # Get raw nationality values
        sies_nac = str(sies_obj.get("NACIONALIDAD","")).strip() if sies_obj else ""
        da_nac   = ""
        if da_row > 0 and da_nac_col is not None:
            v = da_data[da_row-1][da_nac_col]
            da_nac = str(v).strip() if v is not None else ""

        xrefs.append({
            "sies_row": sies_row,
            "sies_obj": sies_obj,
            "da_row":   da_row,
            "da_method": da_method,
            "sies_nac": sies_nac,
            "da_nac":   da_nac,
        })
    return xrefs, da_nac_col, da_codcli_col, da_rut_col

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — generate inspection CSV
# ══════════════════════════════════════════════════════════════════════════════

def generate_inspection(da_headers, da_data):
    nac_terms  = {"NACIONALIDAD","PAIS_DE_ORIGEN","PAIS_ESTUDIOS_SECUNDARIOS",
                  "PAIS_EST_SEC","PAIS_ORIGEN","PAISORIGEN","PAISESTUDIOS"}
    contact_terms = {"MAIL","MAIL_INST","FONOACTUAL","FONOPROCEDENCIA","FONOEMERGENCIA",
                     "CELULAR","TELEFONO"}

    col_info = []
    for i, h in enumerate(da_headers):
        hu = h.upper().replace(" ","_").replace(".","")
        non_null = sum(1 for row in da_data if row[i] is not None and str(row[i]).strip())
        kind = "OTRO"
        if hu in nac_terms: kind = "NACIONALIDAD_O_PAIS"
        elif "RUT" in hu or "CODCLI" in hu or "CODIGO" in hu: kind = "IDENTIFICACION"
        elif "NOMBRE" in hu or "APELLIDO" in hu or "SEXO" in hu: kind = "PERSONAL"
        elif hu in contact_terms or "MAIL" in hu or "FONO" in hu: kind = "CONTACTO"
        elif "CARRERA" in hu or "SEDE" in hu or "JORNADA" in hu or "NIVEL" in hu: kind = "ACADEMICO"
        col_info.append({
            "COLUMNA_ORIGINAL": h,
            "COLUMNA_UPPER": hu,
            "POSICION_1_INDEXED": i+1,
            "TIPO": kind,
            "REGISTROS_CON_DATO": non_null,
            "REGISTROS_VACIOS": len(da_data) - non_null,
            "TOTAL_FILAS": len(da_data),
            "ES_CAMPO_PAIS_NACION": "SI" if kind == "NACIONALIDAD_O_PAIS" else "NO",
            "EXISTE_EXPLICITAMENTE": "SI",
        })

    campos_esperados = [
        "NACIONALIDAD","PAIS_DE_ORIGEN","PAIS_ESTUDIOS_SECUNDARIOS",
        "PAIS_EST_SEC","PAIS_ORIGEN","PAIS_ENSENANZA_MEDIA",
    ]
    existentes = {h.upper().replace(" ","_") for h in da_headers}
    for c in campos_esperados:
        if c not in existentes and c not in [x["COLUMNA_UPPER"] for x in col_info]:
            col_info.append({
                "COLUMNA_ORIGINAL": f"[NO EXISTE: {c}]",
                "COLUMNA_UPPER": c,
                "POSICION_1_INDEXED": "N/A",
                "TIPO": "NACIONALIDAD_O_PAIS",
                "REGISTROS_CON_DATO": 0,
                "REGISTROS_VACIOS": len(da_data),
                "TOTAL_FILAS": len(da_data),
                "ES_CAMPO_PAIS_NACION": "SI",
                "EXISTE_EXPLICITAMENTE": "NO",
            })

    with open(F_INSPECCION, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "COLUMNA_ORIGINAL","COLUMNA_UPPER","POSICION_1_INDEXED","TIPO",
            "REGISTROS_CON_DATO","REGISTROS_VACIOS","TOTAL_FILAS",
            "ES_CAMPO_PAIS_NACION","EXISTE_EXPLICITAMENTE"
        ])
        w.writeheader()
        w.writerows(col_info)
    print(f"  [OK] Inspección: {F_INSPECCION}")
    return col_info

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — build INSTRUCCIONES sheet
# ══════════════════════════════════════════════════════════════════════════════

def build_instrucciones(ws):
    ws.sheet_view.showGridLines = False
    lines = [
        ("AUDITORÍA TRAZABLE DE NACIONALIDAD — 257 REGISTROS", True, 16),
        (f"Generado: {TS}", False, 11),
        ("", False, 11),
        ("PROPÓSITO", True, 12),
        ("Este archivo permite revisar los 257 registros del universo depurado de estudiantes extranjeros regulares 2026.", False, 11),
        ("Para cada registro responde: de dónde salió, con qué nacionalidad apareció en SIES/PES, qué dice DatosAlumnos, si hay contradicción.", False, 11),
        ("", False, 11),
        ("REGLAS NORMATIVAS CRÍTICAS", True, 12),
        ("1. La NACIONALIDAD es el campo que define el vínculo jurídico. Código entre 1 y 197.", False, 11),
        ("2. Código 38 = Chile. Ningún estudiante extranjero puede tener código 38 como nacionalidad.", False, 11),
        ("3. Tener RUT NO demuestra que la persona sea chilena.", False, 11),
        ("4. La nacionalidad NUNCA se infiere desde: tipo de documento, número de documento, país de origen,", False, 11),
        ("   país de estudios secundarios, dirección, ciudad, colegio o nombre/apellido.", False, 11),
        ("5. No asumir que nacionalidad = país de origen = país de estudios secundarios.", False, 11),
        ("6. Si el campo no existe en la fuente: NO_EXISTE_EN_FUENTE", False, 11),
        ("7. Si existe la columna pero la celda está vacía: VACIO_EN_FUENTE", False, 11),
        ("", False, 11),
        ("HOJAS DEL ARCHIVO", True, 12),
        ("RAW_UNIVERSO_257        → 257 registros brutos del universo depurado", False, 11),
        ("RAW_PRECARGA_SIES       → 185 filas de la precarga oficial PES/SIES", False, 11),
        ("RAW_DATOS_ALUMNOS       → Hoja DatosAlumnos de PROMEDIOSDEALUMNOS_7804.xlsx (todos los registros)", False, 11),
        ("RAW_MATRICULA_2025      → Matrícula institucional 2025 (fuente control)", False, 11),
        ("TRAZABILIDAD_257        → Hoja maestra: 257 filas con cruce de todas las fuentes", False, 11),
        ("PRIORITARIOS_SIN_NACION → Casos que requieren revisión operativa prioritaria", False, 11),
        ("CONFLICTOS_NACIONALIDAD → Casos con conflicto entre fuentes", False, 11),
        ("MULTIPLES_CARRERAS      → Personas con más de una carrera/matrícula", False, 11),
        ("DICCIONARIO_COLUMNAS    → Definición de cada columna calculada", False, 11),
        ("CONTROL_COBERTURA       → Indicadores de cobertura y reconciliación", False, 11),
        ("FORMULAS_Y_REGLAS       → Documentación de cada fórmula y regla normativa", False, 11),
        ("", False, 11),
        ("CÓDIGO DE COLORES", True, 12),
        ("Azul oscuro (encabezado): dato raw de fuente original", False, 11),
        ("Verde oscuro (encabezado): columna calculada con fórmula Excel", False, 11),
        ("Morado (encabezado): control y auditoría", False, 11),
        ("Rojo: conflicto entre fuentes", False, 11),
        ("Amarillo: pendiente de revisión", False, 11),
        ("Verde claro: confirmado", False, 11),
        ("Gris: no aplica / no existe en fuente", False, 11),
        ("", False, 11),
        ("ADVERTENCIA", True, 12),
        ("Este archivo NO debe usarse como carga PES. Es exclusivamente un instrumento de auditoría y trazabilidad.", False, 11),
        ("EL RUT NO DEFINE LA NACIONALIDAD.", True, 13),
        ("LA NACIONALIDAD SOLO PUEDE CONFIRMARSE MEDIANTE EL CAMPO NACIONALIDAD O UNA FUENTE INSTITUCIONAL OFICIAL.", True, 11),
    ]
    for i, (text, bold, size) in enumerate(lines, 1):
        cell = ws.cell(row=i, column=1, value=text)
        cell.font = Font(bold=bold, size=size,
                         color="FF0000" if bold and "ADVERTENCIA" in text or "RUT NO" in text or "SOLO PUEDE" in text else "000000")
        cell.alignment = Alignment(wrap_text=True)
        ws.row_dimensions[i].height = 18 if not text else 22
    ws.column_dimensions["A"].width = 120
    ws.sheet_view.showGridLines = False

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — RAW_UNIVERSO_257
# ══════════════════════════════════════════════════════════════════════════════

def build_raw_universo(ws, univ, hash_val):
    if not univ: return
    orig_cols = list(univ[0].keys())
    aux_cols  = ["RAW_FILA_UNIVERSO","RAW_ARCHIVO_ORIGEN","RAW_HASH_ARCHIVO"]
    all_cols  = orig_cols + aux_cols
    h_style   = hdr_style(C["hdr_raw"])

    for j, h in enumerate(all_cols, 1):
        c = ws.cell(row=1, column=j, value=h)
        applydict(c, h_style)

    for i, row in enumerate(univ, 2):
        for j, col_name in enumerate(orig_cols, 1):
            ws.cell(row=i, column=j, value=row.get(col_name,""))
        n = len(orig_cols)
        ws.cell(row=i, column=n+1, value=i-1)
        ws.cell(row=i, column=n+2, value="UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv")
        ws.cell(row=i, column=n+3, value=hash_val)

    last_col = get_column_letter(len(all_cols))
    make_table(ws, TBL_UNIV, f"A1:{last_col}{len(univ)+1}")
    freeze(ws)
    autofilter(ws)
    widths = [12,18,22,22,28,28,28,28,18,22,12,14,10,35,35,18,20,12,8,8,30,35,40,12,45,18]
    set_widths(ws, widths[:len(all_cols)])
    print(f"  [OK] RAW_UNIVERSO_257: {len(univ)} filas")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — RAW_PRECARGA_SIES
# ══════════════════════════════════════════════════════════════════════════════

def build_raw_precarga(ws, sies, hash_val):
    if not sies: return
    orig_cols = list(sies[0].keys())
    # Add computed key columns + metadata
    aux_cols  = ["CLAVE_PC","CLAVE_PCC",
                 "RAW_FILA_PRECARGA","RAW_ARCHIVO_ORIGEN","RAW_HASH_ARCHIVO"]
    all_cols  = orig_cols + aux_cols
    h_style_raw = hdr_style(C["hdr_raw"])
    h_style_frm = hdr_style(C["hdr_frm"])

    # Column positions (1-indexed)
    tipo_col   = orig_cols.index("TIPO_DOCUMENTO")  + 1   # 2nd col in excel
    num_col    = orig_cols.index("NUM_DOCUMENTO")   + 1
    cu_col     = orig_cols.index("CODIGO_UNICO")    + 1

    for j, h in enumerate(all_cols, 1):
        c = ws.cell(row=1, column=j, value=h)
        style = h_style_frm if h in ("CLAVE_PC","CLAVE_PCC") else h_style_raw
        applydict(c, style)

    tipo_L = get_column_letter(tipo_col)
    num_L  = get_column_letter(num_col)
    cu_L   = get_column_letter(cu_col)

    n_orig = len(orig_cols)
    cpc_col_L   = get_column_letter(n_orig + 1)  # CLAVE_PC
    cpcc_col_L  = get_column_letter(n_orig + 2)  # CLAVE_PCC

    for i, row in enumerate(sies, 2):
        for j, col_name in enumerate(orig_cols, 1):
            ws.cell(row=i, column=j, value=row.get(col_name,""))
        # Excel formulas for keys
        ws.cell(row=i, column=n_orig+1,
                value=f'=UPPER(TRIM({tipo_L}{i}))&"|"&UPPER(TRIM({num_L}{i}))')
        ws.cell(row=i, column=n_orig+2,
                value=f'=UPPER(TRIM({tipo_L}{i}))&"|"&UPPER(TRIM({num_L}{i}))&"|"&UPPER(TRIM({cu_L}{i}))')
        ws.cell(row=i, column=n_orig+3, value=i-1)
        ws.cell(row=i, column=n_orig+4, value="REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv")
        ws.cell(row=i, column=n_orig+5, value=hash_val)

    last_col = get_column_letter(len(all_cols))
    make_table(ws, TBL_SIES, f"A1:{last_col}{len(sies)+1}")
    freeze(ws)
    autofilter(ws)
    print(f"  [OK] RAW_PRECARGA_SIES: {len(sies)} filas")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 7 — RAW_DATOS_ALUMNOS  (all 13708 rows)
# ══════════════════════════════════════════════════════════════════════════════

def build_raw_datos_alumnos(ws, da_headers, da_data, hash_val):
    aux_cols = ["CLAVE_RUT_NUM","CLAVE_CODCLI_STR",
                "RAW_HOJA_ORIGEN","RAW_FILA_DATOS_ALUMNOS",
                "RAW_ARCHIVO_ORIGEN","RAW_HASH_ARCHIVO"]
    all_cols = da_headers + aux_cols
    h_style_raw = hdr_style(C["hdr_raw"])
    h_style_frm = hdr_style(C["hdr_frm"])

    codcli_col_L = get_column_letter(da_headers.index("CODCLI")+1) if "CODCLI" in da_headers else None
    rut_col_L    = get_column_letter(da_headers.index("RUT")+1)    if "RUT"    in da_headers else None

    n_orig = len(da_headers)
    crut_L   = get_column_letter(n_orig+1)  # CLAVE_RUT_NUM
    ccli_L   = get_column_letter(n_orig+2)  # CLAVE_CODCLI_STR

    for j, h in enumerate(all_cols, 1):
        c = ws.cell(row=1, column=j, value=h)
        style = h_style_frm if h in ("CLAVE_RUT_NUM","CLAVE_CODCLI_STR") else h_style_raw
        applydict(c, style)

    for i, row in enumerate(da_data, 2):
        for j, v in enumerate(row, 1):
            ws.cell(row=i, column=j, value=v)
        # Formulas for keys
        if rut_col_L:
            ws.cell(row=i, column=n_orig+1,
                    value=f'=IFERROR(LEFT({rut_col_L}{i},FIND("-",{rut_col_L}{i})-1),{rut_col_L}{i})')
        else:
            ws.cell(row=i, column=n_orig+1, value="NO_EXISTE_RUT")
        if codcli_col_L:
            ws.cell(row=i, column=n_orig+2, value=f'=TEXT({codcli_col_L}{i},"@")')
        else:
            ws.cell(row=i, column=n_orig+2, value="NO_EXISTE_CODCLI")
        ws.cell(row=i, column=n_orig+3, value="DatosAlumnos")
        ws.cell(row=i, column=n_orig+4, value=i-1)
        ws.cell(row=i, column=n_orig+5, value="PROMEDIOSDEALUMNOS_7804.xlsx")
        ws.cell(row=i, column=n_orig+6, value=hash_val)

    last_col = get_column_letter(len(all_cols))
    total_rows = len(da_data) + 1
    make_table(ws, TBL_DA, f"A1:{last_col}{total_rows}")
    freeze(ws)
    autofilter(ws)
    print(f"  [OK] RAW_DATOS_ALUMNOS: {len(da_data)} filas x {len(da_headers)} cols originales")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 8 — RAW_MATRICULA_2025
# ══════════════════════════════════════════════════════════════════════════════

def build_raw_matricula(ws, mat_rows):
    if not mat_rows: return
    orig_cols = list(mat_rows[0].keys())
    aux_cols  = ["RAW_FILA_MATRICULA","RAW_ARCHIVO_ORIGEN"]
    all_cols  = orig_cols + aux_cols
    h_style   = hdr_style(C["hdr_raw"])

    for j, h in enumerate(all_cols, 1):
        applydict(ws.cell(row=1, column=j, value=h), h_style)

    for i, row in enumerate(mat_rows, 2):
        for j, cn in enumerate(orig_cols, 1):
            ws.cell(row=i, column=j, value=row.get(cn,""))
        ws.cell(row=i, column=len(orig_cols)+1, value=i-1)
        ws.cell(row=i, column=len(orig_cols)+2, value="matricula_avance_curricular_2025_control.csv")

    last_col = get_column_letter(len(all_cols))
    make_table(ws, TBL_MAT, f"A1:{last_col}{len(mat_rows)+1}")
    freeze(ws)
    autofilter(ws)
    print(f"  [OK] RAW_MATRICULA_2025: {len(mat_rows)} filas")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 9 — TRAZABILIDAD_257  (core sheet)
# ══════════════════════════════════════════════════════════════════════════════

def build_trazabilidad(ws, univ, xrefs, sies, da_headers):
    """
    Each of 257 rows. Columns: Bloque A (identity) + B (SIES) + C (DatosAlumnos)
    + D (comparison) + E (explanation).
    Helper Python-computed columns prefixed _PY_ enable INDEX formulas.
    """
    h_raw = hdr_style(C["hdr_raw"])
    h_frm = hdr_style(C["hdr_frm"])
    h_ctl = hdr_style(C["hdr_ctrl"])

    # DA column indices (0-based in da_headers list)
    def da_col(name): return da_headers.index(name)+1 if name in da_headers else None

    DA_CODCLI    = da_col("CODCLI")
    DA_RUT       = da_col("RUT")
    DA_NOMBRE    = da_col("NOMBRE")
    DA_NOMBRES   = da_col("NOMBRES")
    DA_AP        = da_col("APELLIDO PATERNO")
    DA_AM        = da_col("APELLIDO MATERNO")
    DA_FNAC      = da_col("FECHANACIMIENTO")
    DA_NAC       = da_col("NACIONALIDAD")
    DA_MAIL      = da_col("MAIL")
    DA_MAILINST  = da_col("Mail_Inst")
    DA_FONOACT   = da_col("FONOACTUAL")
    DA_FONOPROC  = da_col("FONOPROCEDENCIA")
    DA_DIRACT    = da_col("DIRECCIONACTUAL")
    DA_COMACT    = da_col("COMUNAACTUAL")
    DA_SEDE      = da_col("SEDE")
    DA_CARRERA   = da_col("NOMBRE_L")
    DA_JORNADA   = da_col("JORNADA")
    DA_MODALIDAD = da_col("MODALIDAD")

    def da_index_formula(da_row_col_L, da_tbl_col_name, row_i):
        """Returns an INDEX formula to fetch a column from tblDatosAlumnos."""
        col_safe = da_tbl_col_name.replace(" ","_")
        # Using INDIRECT to handle column names with spaces
        return (f'=IF({da_row_col_L}{row_i}>0,'
                f'IFERROR(INDEX({TBL_DA}[{da_tbl_col_name}],{da_row_col_L}{row_i}),"VACIO_EN_FUENTE"),'
                f'"NO_ENCONTRADO")')

    def sies_index_formula(sies_row_col_L, sies_col_name, row_i):
        return (f'=IF({sies_row_col_L}{row_i}>0,'
                f'IFERROR(INDEX({TBL_SIES}[{sies_col_name}],{sies_row_col_L}{row_i}),"VACIO_EN_FUENTE"),'
                f'"NO_ENCONTRADO_EN_PRECARGA")')

    # Define all columns
    # Bloque A: universe identity (from RAW_UNIVERSO_257, values)
    bloque_a = [
        "ID_CONTROL","CODCLI","CLAVE_PERSONA_DOCUMENTO","CLAVE_PERSONA_IDENTIDAD",
        "CLAVE_OFICIAL_CARGA","CLAVE_PERSONA_CARRERA","FUENTE_INCLUSION",
        "CATEGORIA_FINAL","INCLUIR_EN_PROCESO","VIGENCIA_PROPUESTA",
        "NIVEL_CONFIANZA","MOTIVO_DECISION","EVIDENCIA_2025",
    ]
    # Helper Python-computed
    bloque_helper = [
        "_PY_SIES_ROW_IN_TABLE","_PY_DA_ROW_IN_TABLE","_PY_DA_MATCH_METHOD",
        "_PY_SIES_NAC_RAW","_PY_DA_NAC_RAW",
    ]
    # Bloque B: SIES (Excel formulas using INDEX from tblPrecargaSIES)
    bloque_b = [
        "ESTA_EN_PRECARGA_SIES","FILA_PRECARGA_SIES",
        "TIPO_DOCUMENTO_SIES","NUM_DOCUMENTO_SIES","DV_SIES",
        "NACIONALIDAD_CARGADA_SIES","PAIS_ORIGEN_CARGADO_SIES","PAIS_EST_SEC_CARGADO_SIES",
        "CODIGO_UNICO_SIES","VIGENCIA_SIES","FORMA_CARGA_SIES",
    ]
    # Bloque C: DatosAlumnos (Excel formulas using INDEX from tblDatosAlumnos)
    bloque_c = [
        "ENCONTRADO_DATOS_ALUMNOS","FILA_DATOS_ALUMNOS","HOJA_DATOS_ALUMNOS",
        "CODCLI_DATOS_ALUMNOS","RUT_DATOS_ALUMNOS","NOMBRE_DATOS_ALUMNOS",
        "FECHA_NAC_DATOS_ALUMNOS","NACIONALIDAD_DATOS_ALUMNOS",
        "PAIS_ORIGEN_DATOS_ALUMNOS","PAIS_EST_SEC_DATOS_ALUMNOS",
        "CORREO_INSTITUCIONAL","CORREO_PERSONAL","TELEFONO","CELULAR",
        "DIRECCION","COMUNA","SEDE","CARRERA","JORNADA","MODALIDAD",
    ]
    # Bloque D: comparison (formulas)
    bloque_d = [
        "SIES_TIENE_NACIONALIDAD","DATOS_ALUMNOS_TIENE_NACIONALIDAD",
        "CODIGO_NACIONALIDAD_SIES","VALOR_NACIONALIDAD_DATOS_ALUMNOS",
        "ES_CHILE_SEGUN_SIES","ES_EXTRANJERO_SEGUN_SIES",
        "ES_EXTRANJERO_SEGUN_DATOS_ALUMNOS",
        "COINCIDE_NACIONALIDAD","ESTADO_FINAL_NACIONALIDAD","MOTIVO_ESTADO_NACIONALIDAD",
    ]
    # Bloque E: explanation (formulas)
    bloque_e = [
        "POR_QUE_ENTRO_AL_UNIVERSO_257","POR_QUE_SE_CONSIDERA_EXTRANJERO",
        "REQUIERE_REVISION","PRIORIDAD_REVISION","RESPONSABLE_SUGERIDO",
    ]

    all_cols = bloque_a + bloque_helper + bloque_b + bloque_c + bloque_d + bloque_e

    # Map column name → 1-indexed excel column number
    col_idx = {name: j for j, name in enumerate(all_cols, 1)}
    # Helper column letters
    sies_row_L = get_column_letter(col_idx["_PY_SIES_ROW_IN_TABLE"])
    da_row_L   = get_column_letter(col_idx["_PY_DA_ROW_IN_TABLE"])
    nac_sies_L = get_column_letter(col_idx["NACIONALIDAD_CARGADA_SIES"])
    nac_da_L   = get_column_letter(col_idx["NACIONALIDAD_DATOS_ALUMNOS"])

    # Write headers
    for j, name in enumerate(all_cols, 1):
        if name in bloque_a: style = h_raw
        elif name.startswith("_PY_"): style = hdr_style("4A235A")
        elif name in bloque_b + bloque_c: style = h_frm
        else: style = h_ctl
        applydict(ws.cell(row=1, column=j, value=name), style)

    # SIES column positions within tblPrecargaSIES
    sies_cols_map = {
        "TIPO_DOCUMENTO_SIES": "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO_SIES":  "NUM_DOCUMENTO",
        "DV_SIES":             "DV",
        "NACIONALIDAD_CARGADA_SIES": "NACIONALIDAD",
        "PAIS_ORIGEN_CARGADO_SIES":  "PAIS_ORIGEN",
        "PAIS_EST_SEC_CARGADO_SIES": "PAIS_ESTUDIOS_SECUNDARIOS",
        "CODIGO_UNICO_SIES":   "CODIGO_UNICO",
        "VIGENCIA_SIES":       "VIGENCIA",
    }
    da_cols_map = {
        "CODCLI_DATOS_ALUMNOS":    "CODCLI",
        "RUT_DATOS_ALUMNOS":       "RUT",
        "NOMBRE_DATOS_ALUMNOS":    "NOMBRE",
        "FECHA_NAC_DATOS_ALUMNOS": "FECHANACIMIENTO",
        "NACIONALIDAD_DATOS_ALUMNOS": "NACIONALIDAD",
        "CORREO_INSTITUCIONAL":    "Mail_Inst",
        "CORREO_PERSONAL":         "MAIL",
        "TELEFONO":                "FONOPROCEDENCIA",
        "CELULAR":                 "FONOACTUAL",
        "DIRECCION":               "DIRECCIONACTUAL",
        "COMUNA":                  "COMUNAACTUAL",
        "SEDE":                    "SEDE",
        "CARRERA":                 "NOMBRE_L",
        "JORNADA":                 "JORNADA",
        "MODALIDAD":               "MODALIDAD",
    }

    for i, (u, xr) in enumerate(zip(univ, xrefs), 2):
        sr = xr["sies_row"]  # table row (1-indexed) in tblPrecargaSIES, 0=not found
        dr = xr["da_row"]    # table row (1-indexed) in tblDatosAlumnos, 0=not found

        # ── Bloque A: values from universo ──────────────────────────────────
        for col_name in bloque_a:
            ws.cell(row=i, column=col_idx[col_name], value=u.get(col_name,""))

        # ── Helper Python-computed ───────────────────────────────────────────
        ws.cell(row=i, column=col_idx["_PY_SIES_ROW_IN_TABLE"], value=sr)
        ws.cell(row=i, column=col_idx["_PY_DA_ROW_IN_TABLE"],   value=dr)
        ws.cell(row=i, column=col_idx["_PY_DA_MATCH_METHOD"],   value=xr["da_method"])
        ws.cell(row=i, column=col_idx["_PY_SIES_NAC_RAW"],      value=xr["sies_nac"])
        ws.cell(row=i, column=col_idx["_PY_DA_NAC_RAW"],        value=xr["da_nac"])

        # ── Bloque B: SIES fields via Excel INDEX formulas ───────────────────
        ws.cell(row=i, column=col_idx["ESTA_EN_PRECARGA_SIES"],
                value=f'=IF({sies_row_L}{i}>0,"SI","NO")')
        ws.cell(row=i, column=col_idx["FILA_PRECARGA_SIES"],
                value=f'=IF({sies_row_L}{i}>0,{sies_row_L}{i},"N/A")')

        for dest_col, src_col in sies_cols_map.items():
            ws.cell(row=i, column=col_idx[dest_col],
                    value=sies_index_formula(sies_row_L, src_col, i))

        # FORMA_CARGA_SIES
        nac_sies_tmp = f'INDEX({TBL_SIES}[NACIONALIDAD],{sies_row_L}{i})'
        ws.cell(row=i, column=col_idx["FORMA_CARGA_SIES"],
                value=(
                    f'=IF({sies_row_L}{i}=0,"NO_ENCONTRADO_EN_PRECARGA",'
                    f'IF(IFERROR({nac_sies_tmp},"")<>"","PRECARGA_PES_CON_NACIONALIDAD",'
                    f'"PRECARGA_PES_SIN_NACIONALIDAD"))'
                ))

        # ── Bloque C: DatosAlumnos via Excel INDEX formulas ──────────────────
        ws.cell(row=i, column=col_idx["ENCONTRADO_DATOS_ALUMNOS"],
                value=f'=IF({da_row_L}{i}>0,"SI","NO")')
        ws.cell(row=i, column=col_idx["FILA_DATOS_ALUMNOS"],
                value=f'=IF({da_row_L}{i}>0,{da_row_L}{i},"N/A")')
        ws.cell(row=i, column=col_idx["HOJA_DATOS_ALUMNOS"],
                value=f'=IF({da_row_L}{i}>0,"DatosAlumnos","N/A")')

        for dest_col, src_col in da_cols_map.items():
            if src_col in da_headers:
                ws.cell(row=i, column=col_idx[dest_col],
                        value=da_index_formula(da_row_L, src_col, i))
            else:
                ws.cell(row=i, column=col_idx[dest_col], value="NO_EXISTE_EN_FUENTE")

        # PAIS_ORIGEN y PAIS_EST_SEC no existen en DatosAlumnos
        ws.cell(row=i, column=col_idx["PAIS_ORIGEN_DATOS_ALUMNOS"],  value="NO_EXISTE_EN_FUENTE")
        ws.cell(row=i, column=col_idx["PAIS_EST_SEC_DATOS_ALUMNOS"], value="NO_EXISTE_EN_FUENTE")

        # ── Bloque D: comparison formulas ────────────────────────────────────
        nL = nac_sies_L
        dL = nac_da_L

        ws.cell(row=i, column=col_idx["SIES_TIENE_NACIONALIDAD"],
                value=f'=IF(OR({nL}{i}="",{nL}{i}="NO_ENCONTRADO_EN_PRECARGA",{nL}{i}="VACIO_EN_FUENTE"),"NO","SI")')
        ws.cell(row=i, column=col_idx["DATOS_ALUMNOS_TIENE_NACIONALIDAD"],
                value=f'=IF(OR({dL}{i}="",{dL}{i}="NO_ENCONTRADO",{dL}{i}="VACIO_EN_FUENTE",{dL}{i}="NO_EXISTE_EN_FUENTE"),"NO","SI")')
        ws.cell(row=i, column=col_idx["CODIGO_NACIONALIDAD_SIES"],
                value=f'=IF({nL}{i}="","","COD_"&{nL}{i})')
        ws.cell(row=i, column=col_idx["VALOR_NACIONALIDAD_DATOS_ALUMNOS"],
                value=f'={dL}{i}')

        # ES_CHILE_SEGUN_SIES
        ws.cell(row=i, column=col_idx["ES_CHILE_SEGUN_SIES"],
                value=(
                    f'=IF(OR({nL}{i}="",{nL}{i}="NO_ENCONTRADO_EN_PRECARGA",{nL}{i}="VACIO_EN_FUENTE"),"SIN_DATO",'
                    f'IF(IFERROR(VALUE({nL}{i}),0)=38,"SI",'
                    f'IF(AND(IFERROR(VALUE({nL}{i}),0)>=1,IFERROR(VALUE({nL}{i}),0)<=197),"NO","INVALIDO")))'
                ))
        # ES_EXTRANJERO_SEGUN_SIES
        ws.cell(row=i, column=col_idx["ES_EXTRANJERO_SEGUN_SIES"],
                value=(
                    f'=IF(OR({nL}{i}="",{nL}{i}="NO_ENCONTRADO_EN_PRECARGA",{nL}{i}="VACIO_EN_FUENTE"),"NO_DETERMINABLE",'
                    f'IF(AND(IFERROR(VALUE({nL}{i}),0)>=1,IFERROR(VALUE({nL}{i}),0)<=197,IFERROR(VALUE({nL}{i}),0)<>38),"SI",'
                    f'IF(IFERROR(VALUE({nL}{i}),0)=38,"NO","NO_DETERMINABLE")))'
                ))
        # ES_EXTRANJERO_SEGUN_DATOS_ALUMNOS (text-based: "CHILENA" = Chile)
        ws.cell(row=i, column=col_idx["ES_EXTRANJERO_SEGUN_DATOS_ALUMNOS"],
                value=(
                    f'=IF(OR({dL}{i}="",{dL}{i}="NO_ENCONTRADO",{dL}{i}="VACIO_EN_FUENTE",{dL}{i}="NO_EXISTE_EN_FUENTE"),"NO_DETERMINABLE",'
                    f'IF(UPPER(TRIM({dL}{i}))="CHILENA","NO","SI"))'
                ))

        # COINCIDE_NACIONALIDAD
        sies_es_chile = get_column_letter(col_idx["ES_CHILE_SEGUN_SIES"])
        sies_es_extr  = get_column_letter(col_idx["ES_EXTRANJERO_SEGUN_SIES"])
        da_es_extr    = get_column_letter(col_idx["ES_EXTRANJERO_SEGUN_DATOS_ALUMNOS"])
        sies_tiene    = get_column_letter(col_idx["SIES_TIENE_NACIONALIDAD"])
        da_tiene      = get_column_letter(col_idx["DATOS_ALUMNOS_TIENE_NACIONALIDAD"])

        ws.cell(row=i, column=col_idx["COINCIDE_NACIONALIDAD"],
                value=(
                    f'=IF(AND({sies_tiene}{i}="NO",{da_tiene}{i}="NO"),"AMBAS_SIN_DATO",'
                    f'IF(AND({sies_es_chile}{i}="SI",UPPER(TRIM({dL}{i}))="CHILENA"),"COINCIDE_AMBAS_CHILE",'
                    f'IF(AND({sies_es_extr}{i}="SI",{da_es_extr}{i}="SI"),"COINCIDE_AMBAS_EXTRANJERO",'
                    f'IF(AND({sies_es_chile}{i}="SI",{da_es_extr}{i}="SI"),"CONFLICTO_SIES_CHILE_DA_EXTRANJERO",'
                    f'IF(AND({sies_es_extr}{i}="SI",UPPER(TRIM({dL}{i}))="CHILENA"),"CONFLICTO_SIES_EXTR_DA_CHILE",'
                    f'"PARCIAL_SIN_DATO")))))'
                ))

        # ESTADO_FINAL_NACIONALIDAD
        coinc_L = get_column_letter(col_idx["COINCIDE_NACIONALIDAD"])
        ws.cell(row=i, column=col_idx["ESTADO_FINAL_NACIONALIDAD"],
                value=(
                    f'=IF({coinc_L}{i}="COINCIDE_AMBAS_EXTRANJERO","EXTRANJERO_CONFIRMADO_AMBAS_FUENTES",'
                    f'IF({coinc_L}{i}="COINCIDE_AMBAS_CHILE","CHILE_SEGUN_AMBAS_FUENTES",'
                    f'IF({coinc_L}{i}="CONFLICTO_SIES_CHILE_DA_EXTRANJERO","CONFLICTO_SIES_VS_DATOS_ALUMNOS",'
                    f'IF({coinc_L}{i}="CONFLICTO_SIES_EXTR_DA_CHILE","CONFLICTO_SIES_VS_DATOS_ALUMNOS",'
                    f'IF(AND({sies_tiene}{i}="SI",{da_tiene}{i}="NO"),"SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO",'
                    f'IF(AND({sies_tiene}{i}="NO",{da_tiene}{i}="SI"),"SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO",'
                    f'IF({coinc_L}{i}="AMBAS_SIN_DATO","AMBAS_FUENTES_SIN_NACIONALIDAD",'
                    f'IF(IFERROR(VALUE({nL}{i}),0)=38,"CHILE_SEGUN_SIES",'
                    f'IF(UPPER(TRIM({dL}{i}))="CHILENA","CHILE_SEGUN_DATOS_ALUMNOS",'
                    f'IF(AND(IFERROR(VALUE({nL}{i}),-1)<1,IFERROR(VALUE({nL}{i}),-1)<>0),"CODIGO_INVALIDO",'
                    f'"NO_DETERMINABLE"))))))))))'
                ))

        # MOTIVO_ESTADO_NACIONALIDAD
        estado_L = get_column_letter(col_idx["ESTADO_FINAL_NACIONALIDAD"])
        ws.cell(row=i, column=col_idx["MOTIVO_ESTADO_NACIONALIDAD"],
                value=(
                    f'=IF({estado_L}{i}="EXTRANJERO_CONFIRMADO_AMBAS_FUENTES","Ambas fuentes coinciden en nacionalidad extranjera.",'
                    f'IF({estado_L}{i}="CONFLICTO_SIES_VS_DATOS_ALUMNOS","CONFLICTO: una fuente dice Chile y la otra dice extranjero.",'
                    f'IF({estado_L}{i}="AMBAS_FUENTES_SIN_NACIONALIDAD","Ninguna fuente tiene dato de nacionalidad.",'
                    f'IF({estado_L}{i}="SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO","SIES no tiene nacionalidad; DatosAlumnos sí.",'
                    f'IF({estado_L}{i}="SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO","SIES tiene nacionalidad; DatosAlumnos no tiene dato.",'
                    f'IF({estado_L}{i}="CHILE_SEGUN_SIES","SIES registra código 38 (Chile). Verificar.",'
                    f'IF({estado_L}{i}="CHILE_SEGUN_DATOS_ALUMNOS","DatosAlumnos indica CHILENA. Verificar.",'
                    f'IF({estado_L}{i}="CODIGO_INVALIDO","Código fuera del rango 1-197.",'
                    f'"Sin información suficiente."))))))))'
                ))

        # ── Bloque E: explanation ──────────────────────────────────────────
        fi_col  = get_column_letter(col_idx["FUENTE_INCLUSION"])
        cat_col = get_column_letter(col_idx["CATEGORIA_FINAL"])
        inc_col = get_column_letter(col_idx["INCLUIR_EN_PROCESO"])
        ev_col  = get_column_letter(col_idx["EVIDENCIA_2025"])

        ws.cell(row=i, column=col_idx["POR_QUE_ENTRO_AL_UNIVERSO_257"],
                value=(
                    f'=IF({fi_col}{i}="PRECARGA_PES","Incluido porque aparece en la precarga oficial PES/SIES.",'
                    f'IF({fi_col}{i}="SOLO_MATRICULA_LOCAL","Agregado porque existe evidencia institucional de matrícula 2025.",'
                    f'IF({fi_col}{i}="MISMA_PERSONA_DISTINTA_CARRERA","Pendiente: coincide la persona pero no la carrera o código único.",'
                    f'IF({inc_col}{i}="NO_INCLUIR","No incluir: corresponde a caso excluido por regla de depuración.",'
                    f'"Incluido por: "&{fi_col}{i}&". Categoría: "&{cat_col}{i}))))'
                ))

        ws.cell(row=i, column=col_idx["POR_QUE_SE_CONSIDERA_EXTRANJERO"],
                value=(
                    f'=IF({estado_L}{i}="EXTRANJERO_CONFIRMADO_AMBAS_FUENTES","Nacionalidad SIES y DatosAlumnos confirman que es extranjero.",'
                    f'IF({sies_es_extr}{i}="SI","Nacionalidad SIES es distinta de Chile (código <> 38).",'
                    f'IF({da_es_extr}{i}="SI","DatosAlumnos registra nacionalidad extranjera; SIES no tiene dato.",'
                    f'IF({fi_col}{i}="PRECARGA_PES","Viene en la precarga oficial PES como estudiante extranjero; nacionalidad pendiente de confirmación.",'
                    f'"No existe evidencia suficiente de nacionalidad extranjera. Requiere verificación."))))'
                ))

        ws.cell(row=i, column=col_idx["REQUIERE_REVISION"],
                value=(
                    f'=IF(OR({estado_L}{i}="AMBAS_FUENTES_SIN_NACIONALIDAD",'
                    f'{estado_L}{i}="CONFLICTO_SIES_VS_DATOS_ALUMNOS",'
                    f'{estado_L}{i}="CODIGO_INVALIDO",'
                    f'{estado_L}{i}="CHILE_SEGUN_SIES",'
                    f'{estado_L}{i}="CHILE_SEGUN_DATOS_ALUMNOS",'
                    f'{estado_L}{i}="SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO",'
                    f'{estado_L}{i}="SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO"),"SI","NO")'
                ))

        ws.cell(row=i, column=col_idx["PRIORIDAD_REVISION"],
                value=(
                    f'=IF(OR({estado_L}{i}="AMBAS_FUENTES_SIN_NACIONALIDAD",'
                    f'{estado_L}{i}="CONFLICTO_SIES_VS_DATOS_ALUMNOS",'
                    f'{estado_L}{i}="CODIGO_INVALIDO"),"PRIORIDAD 1",'
                    f'IF(OR({estado_L}{i}="SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO",'
                    f'{estado_L}{i}="SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO",'
                    f'{estado_L}{i}="CHILE_SEGUN_SIES",'
                    f'{estado_L}{i}="CHILE_SEGUN_DATOS_ALUMNOS"),"PRIORIDAD 2","PRIORIDAD 3"))'
                ))

        ws.cell(row=i, column=col_idx["RESPONSABLE_SUGERIDO"],
                value=(
                    f'=IF({estado_L}{i}="EXTRANJERO_CONFIRMADO_AMBAS_FUENTES","Sin acción requerida",'
                    f'IF(OR({estado_L}{i}="AMBAS_FUENTES_SIN_NACIONALIDAD",'
                    f'{estado_L}{i}="CONFLICTO_SIES_VS_DATOS_ALUMNOS"),"Registro Académico + Docencia",'
                    f'IF({fi_col}{i}="PRECARGA_PES","Registro Académico","Registro Académico"))'
                    f')'
                ))

    last_col = get_column_letter(len(all_cols))
    make_table(ws, TBL_TRAZ, f"A1:{last_col}{len(univ)+1}")
    freeze(ws, "A2")
    autofilter(ws)
    print(f"  [OK] TRAZABILIDAD_257: {len(univ)} filas x {len(all_cols)} columnas")
    return col_idx

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 10 — PRIORITARIOS (values extracted from TRAZABILIDAD via Python)
# ══════════════════════════════════════════════════════════════════════════════

def build_prioritarios(ws, univ, xrefs, sies, da_headers):
    """Write priority cases as values (Python-computed) for operational use."""
    h_ctl = hdr_style(C["hdr_ctrl"])

    cols = [
        "PRIORIDAD","ID_CONTROL","CODCLI","TIPO_DOCUMENTO","NUM_DOCUMENTO","DV",
        "NOMBRE_COMPLETO","ESTA_EN_PRECARGA_SIES","FORMA_CARGA_SIES",
        "NACIONALIDAD_CARGADA_SIES","NACIONALIDAD_DATOS_ALUMNOS",
        "ES_EXTRANJERO_SEGUN_SIES","ES_EXTRANJERO_SEGUN_DATOS_ALUMNOS",
        "ESTADO_FINAL_NACIONALIDAD","POR_QUE_SE_CONSIDERA_EXTRANJERO",
        "PAIS_ORIGEN_CARGADO_SIES","PAIS_EST_SEC_CARGADO_SIES",
        "PAIS_ORIGEN_DATOS_ALUMNOS","PAIS_EST_SEC_DATOS_ALUMNOS",
        "CORREO_INSTITUCIONAL","CORREO_PERSONAL","TELEFONO","CELULAR",
        "RESPONSABLE_SUGERIDO","RESPUESTA_NACIONALIDAD","FUENTE_RESPUESTA",
        "RESPONSABLE_RESPUESTA","FECHA_RESPUESTA","OBSERVACIONES",
    ]
    for j, h in enumerate(cols, 1):
        applydict(ws.cell(row=1, column=j, value=h), h_ctl)

    da_nac_col  = da_headers.index("NACIONALIDAD") if "NACIONALIDAD" in da_headers else None
    da_nome_col = da_headers.index("NOMBRE")       if "NOMBRE"       in da_headers else None
    da_mail_col = da_headers.index("Mail_Inst")    if "Mail_Inst"    in da_headers else None
    da_mailp_col= da_headers.index("MAIL")         if "MAIL"         in da_headers else None
    da_fono_col = da_headers.index("FONOACTUAL")   if "FONOACTUAL"   in da_headers else None
    da_fonop_col= da_headers.index("FONOPROCEDENCIA") if "FONOPROCEDENCIA" in da_headers else None

    def sies_val(xr, field):
        s = xr.get("sies_obj")
        if not s: return "NO_ENCONTRADO_EN_PRECARGA"
        v = s.get(field,"")
        return v if v else "VACIO_EN_FUENTE"

    def da_val_raw(xr, da_data_ref, col_i):
        dr = xr["da_row"]
        if dr == 0 or col_i is None: return "NO_ENCONTRADO"
        v = da_data_ref[dr-1][col_i]
        return str(v).strip() if v is not None else "VACIO_EN_FUENTE"

    # We need da_data for building prioritarios, so store it globally
    # or pass it in - we'll use a closure via the xrefs which have da_nac pre-computed
    row_out = 2
    for u, xr in zip(univ, xrefs):
        sies_nac  = xr["sies_nac"]
        da_nac    = xr["da_nac"]
        sies_row  = xr["sies_row"]
        da_row    = xr["da_row"]

        # Determine status (Python-side logic mirrors the Excel formulas)
        sies_has = bool(sies_nac and sies_nac not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO_EN_PRECARGA"))
        da_has   = bool(da_nac  and da_nac  not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO"))
        try: sies_code = int(sies_nac) if sies_has else -1
        except: sies_code = -1

        es_chile_sies  = sies_code == 38
        es_extr_sies   = sies_has and 1 <= sies_code <= 197 and sies_code != 38
        da_nac_up = da_nac.upper().strip() if da_has else ""
        es_extr_da = da_has and da_nac_up != "CHILENA"
        es_chile_da= da_has and da_nac_up == "CHILENA"

        if not sies_has and not da_has:
            estado = "AMBAS_FUENTES_SIN_NACIONALIDAD"
        elif es_chile_sies and es_extr_da:
            estado = "CONFLICTO_SIES_VS_DATOS_ALUMNOS"
        elif es_extr_sies and es_chile_da:
            estado = "CONFLICTO_SIES_VS_DATOS_ALUMNOS"
        elif es_extr_sies and es_extr_da:
            estado = "EXTRANJERO_CONFIRMADO_AMBAS_FUENTES"
        elif sies_has and not da_has:
            estado = "SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO"
        elif not sies_has and da_has:
            estado = "SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO"
        elif sies_code < 0 or sies_code > 197:
            estado = "CODIGO_INVALIDO"
        else:
            estado = "NO_DETERMINABLE"

        if estado == "EXTRANJERO_CONFIRMADO_AMBAS_FUENTES": continue  # not priority

        if estado in ("AMBAS_FUENTES_SIN_NACIONALIDAD","CONFLICTO_SIES_VS_DATOS_ALUMNOS","CODIGO_INVALIDO"):
            prioridad = "PRIORIDAD 1"
        elif estado in ("SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO","SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO","CHILE_SEGUN_SIES","CHILE_SEGUN_DATOS_ALUMNOS"):
            prioridad = "PRIORIDAD 2"
        else:
            prioridad = "PRIORIDAD 3"

        # Parse tipo/num from CLAVE_PERSONA_DOCUMENTO
        cpd = u.get("CLAVE_PERSONA_DOCUMENTO","")
        parts = cpd.split("|")
        tipo_doc = parts[0] if len(parts) > 0 else ""
        num_doc  = parts[1] if len(parts) > 1 else ""

        forma = "PRECARGA_PES_CON_NACIONALIDAD" if sies_row > 0 and sies_has else \
                "PRECARGA_PES_SIN_NACIONALIDAD" if sies_row > 0 else \
                "NO_ENCONTRADO_EN_PRECARGA"

        sies_obj = xr.get("sies_obj") or {}
        vals = [
            prioridad,
            u.get("ID_CONTROL",""),
            u.get("CODCLI",""),
            tipo_doc,
            num_doc,
            sies_obj.get("DV",""),
            u.get("CLAVE_AUXILIAR_IDENTIDAD",""),
            "SI" if sies_row > 0 else "NO",
            forma,
            sies_nac if sies_nac else "VACIO_EN_FUENTE",
            da_nac   if da_nac   else "VACIO_EN_FUENTE",
            "SI" if es_extr_sies else ("NO" if es_chile_sies else "NO_DETERMINABLE"),
            "SI" if es_extr_da   else ("NO" if es_chile_da   else "NO_DETERMINABLE"),
            estado,
            "Viene en precarga PES." if sies_row > 0 else "Agregado por evidencia institucional.",
            sies_obj.get("PAIS_ORIGEN","") or "VACIO_EN_FUENTE",
            sies_obj.get("PAIS_ESTUDIOS_SECUNDARIOS","") or "VACIO_EN_FUENTE",
            "NO_EXISTE_EN_FUENTE",  # PAIS_ORIGEN_DATOS_ALUMNOS
            "NO_EXISTE_EN_FUENTE",  # PAIS_EST_SEC_DATOS_ALUMNOS
            "",  # CORREO_INSTITUCIONAL (contact)
            "",  # CORREO_PERSONAL
            "",  # TELEFONO
            "",  # CELULAR
            "Registro Académico",
            "",  # RESPUESTA_NACIONALIDAD
            "",  # FUENTE_RESPUESTA
            "",  # RESPONSABLE_RESPUESTA
            "",  # FECHA_RESPUESTA
            "",  # OBSERVACIONES
        ]
        for j, v in enumerate(vals, 1):
            ws.cell(row=row_out, column=j, value=v)
        row_out += 1

    last_col = get_column_letter(len(cols))
    if row_out > 2:
        make_table(ws, TBL_PRIO, f"A1:{last_col}{row_out-1}")
    freeze(ws)
    autofilter(ws)
    print(f"  [OK] PRIORITARIOS_SIN_NACIONALIDAD: {row_out-2} casos")
    return row_out - 2

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 11 — CONFLICTOS_NACIONALIDAD
# ══════════════════════════════════════════════════════════════════════════════

def build_conflictos(ws, univ, xrefs):
    h_ctl = hdr_style(C["hdr_ctrl"])
    cols = [
        "ID_CONTROL","CODCLI","CLAVE_PERSONA_CARRERA",
        "SIES_NACIONALIDAD","DA_NACIONALIDAD",
        "ES_CONFLICTO","TIPO_CONFLICTO","DESCRIPCION",
    ]
    for j, h in enumerate(cols, 1):
        applydict(ws.cell(row=1, column=j, value=h), h_ctl)

    row_out = 2
    for u, xr in zip(univ, xrefs):
        sies_nac = xr["sies_nac"]
        da_nac   = xr["da_nac"]
        sies_has = bool(sies_nac and sies_nac not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO_EN_PRECARGA"))
        da_has   = bool(da_nac  and da_nac  not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO"))

        try: sies_code = int(sies_nac) if sies_has else -1
        except: sies_code = -1

        da_up = da_nac.upper().strip() if da_has else ""
        es_chile_sies = sies_code == 38
        es_extr_sies  = sies_has and 1 <= sies_code <= 197 and sies_code != 38
        es_chile_da   = da_has and da_up == "CHILENA"
        es_extr_da    = da_has and da_up != "CHILENA"
        invalid       = sies_has and (sies_code < 1 or sies_code > 197)

        conflicto = False
        tipo = ""
        desc = ""

        if es_chile_sies and es_extr_da:
            conflicto = True; tipo = "SIES_CHILE_DA_EXTRANJERO"
            desc = f"SIES código 38 (Chile), DatosAlumnos dice '{da_nac}'."
        elif es_extr_sies and es_chile_da:
            conflicto = True; tipo = "SIES_EXTRANJERO_DA_CHILE"
            desc = f"SIES código {sies_code}, DatosAlumnos dice CHILENA."
        elif invalid:
            conflicto = True; tipo = "CODIGO_INVALIDO"
            desc = f"Código SIES '{sies_nac}' fuera del rango 1-197."

        if not conflicto: continue

        row = [
            u.get("ID_CONTROL",""), u.get("CODCLI",""), u.get("CLAVE_PERSONA_CARRERA",""),
            sies_nac or "VACIO_EN_FUENTE", da_nac or "VACIO_EN_FUENTE",
            "SI", tipo, desc,
        ]
        for j, v in enumerate(row, 1):
            c = ws.cell(row=row_out, column=j, value=v)
            if tipo in ("SIES_CHILE_DA_EXTRANJERO","SIES_EXTRANJERO_DA_CHILE"):
                c.fill = PatternFill("solid", fgColor=C["conflict"])
                c.font = Font(color="FFFFFF")
        row_out += 1

    last_col = get_column_letter(len(cols))
    if row_out > 2:
        make_table(ws, TBL_CONF, f"A1:{last_col}{row_out-1}")
    freeze(ws)
    autofilter(ws)
    print(f"  [OK] CONFLICTOS_NACIONALIDAD: {row_out-2} casos")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 12 — MULTIPLES_CARRERAS
# ══════════════════════════════════════════════════════════════════════════════

def build_multiples_carreras(ws, univ, xrefs):
    h_ctl = hdr_style(C["hdr_ctrl"])
    cols = ["CPD","CANTIDAD_REGISTROS","IDS_CONTROL","CARRERAS","ESTADO_MULTIPLES"]
    for j, h in enumerate(cols, 1):
        applydict(ws.cell(row=1, column=j, value=h), h_ctl)

    from collections import defaultdict
    by_person = defaultdict(list)
    for u, xr in zip(univ, xrefs):
        cpd = u.get("CLAVE_PERSONA_DOCUMENTO","")
        by_person[cpd].append((u.get("ID_CONTROL",""), u.get("CLAVE_PERSONA_CARRERA",""), xr))

    row_out = 2
    for cpd, items in sorted(by_person.items()):
        if len(items) < 2: continue
        ids = " | ".join(x[0] for x in items)
        carreras = " | ".join(x[1] for x in items)
        nacs = set(x[2]["sies_nac"] for x in items if x[2]["sies_nac"])
        estado = "MULTIPLES_REGISTROS_MISMA_CARRERA" if len(nacs) > 1 else "MULTIPLES_CARRERAS_MISMO_CODIGO_NAC"
        row = [cpd, len(items), ids, carreras, estado]
        for j, v in enumerate(row, 1):
            ws.cell(row=row_out, column=j, value=v)
        row_out += 1

    if row_out > 2:
        make_table(ws, "tblMultiplesCarreras", f"A1:{get_column_letter(len(cols))}{row_out-1}")
    freeze(ws)
    print(f"  [OK] MULTIPLES_CARRERAS: {row_out-2} personas con múltiples registros")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 13 — DICCIONARIO_COLUMNAS
# ══════════════════════════════════════════════════════════════════════════════

def build_diccionario(ws):
    h_ctl = hdr_style(C["hdr_ctrl"])
    cols = ["HOJA","COLUMNA","TIPO","FUENTE","DESCRIPCION","PUEDE_DETERMINAR_NACIONALIDAD",
            "VALORES_POSIBLES","LIMITACIONES"]
    for j, h in enumerate(cols, 1):
        applydict(ws.cell(row=1, column=j, value=h), h_ctl)

    entries = [
        # DatosAlumnos
        ("RAW_DATOS_ALUMNOS","NACIONALIDAD","RAW","DatosAlumnos PROMEDIOSDEALUMNOS_7804.xlsx",
         "Texto de nacionalidad (ej. CHILENA, VENEZOLANA). NO es un código numérico.",
         "PARCIALMENTE (solo el campo explícito de nacionalidad, no inferir de otros campos)",
         "CHILENA / VENEZOLANA / [texto libre]","Texto libre, no codificado; no comparable directamente con código SIES"),
        ("RAW_DATOS_ALUMNOS","PAIS_DE_ORIGEN","AUSENTE","DatosAlumnos PROMEDIOSDEALUMNOS_7804.xlsx",
         "NO EXISTE como columna en DatosAlumnos. No se puede inferir de CIUDADCOLEGIO ni COLEGIO.",
         "NO","NO_EXISTE_EN_FUENTE","No existe en la fuente. No se puede inferir."),
        ("RAW_DATOS_ALUMNOS","PAIS_ESTUDIOS_SECUNDARIOS","AUSENTE","DatosAlumnos PROMEDIOSDEALUMNOS_7804.xlsx",
         "NO EXISTE como columna en DatosAlumnos. CIUDADCOLEGIO y COMUNACOLEGIO son ciudad/comuna, NO país.",
         "NO","NO_EXISTE_EN_FUENTE","No existe en la fuente. No se puede inferir."),
        ("RAW_DATOS_ALUMNOS","CIUDADCOLEGIO","RAW","DatosAlumnos",
         "Ciudad del colegio de enseñanza media. NO equivale a país de estudios secundarios.",
         "NO","Texto libre","Ciudad ≠ país. No usar como proxy de PAIS_ESTUDIOS_SECUNDARIOS."),
        ("RAW_DATOS_ALUMNOS","RUT","RAW","DatosAlumnos",
         "RUT del estudiante. Puede contener número de pasaporte u otro identificador. Formato: xxxxxxxx-d.",
         "NO — Tener RUT no implica ser chileno.","xxxxxxxx-d / texto","Identificador, no determina nacionalidad."),
        # SIES
        ("RAW_PRECARGA_SIES","NACIONALIDAD","RAW","Precarga SIES 2026",
         "Código numérico de nacionalidad según tabla SIES (1-197). Código 38 = Chile.",
         "SI — este campo define la nacionalidad para efectos SIES.","1..197","Debe estar entre 1 y 197. Si está vacío: VACIO_EN_FUENTE."),
        ("RAW_PRECARGA_SIES","PAIS_ORIGEN","RAW","Precarga SIES 2026",
         "País de origen del estudiante. Distinto de nacionalidad.",
         "NO — no es equivalente a nacionalidad.","1..197 o vacío","Distinto de NACIONALIDAD."),
        ("RAW_PRECARGA_SIES","PAIS_ESTUDIOS_SECUNDARIOS","RAW","Precarga SIES 2026",
         "País donde el estudiante cursó la enseñanza media.",
         "NO","1..197 o vacío","Distinto de NACIONALIDAD."),
        ("RAW_PRECARGA_SIES","CLAVE_PCC","FORMULA","Calculada con fórmula Excel",
         '=TIPO_DOCUMENTO&"|"&NUM_DOCUMENTO&"|"&CODIGO_UNICO. Clave de cruce persona-carrera.',
         "NO","TIPO|NUM|CODIGO_UNICO","Calculada. Ver fórmula en FORMULAS_Y_REGLAS."),
        # Trazabilidad
        ("TRAZABILIDAD_257","_PY_SIES_ROW_IN_TABLE","PYTHON","Pre-calculado en Python",
         "Fila 1-indexed dentro de tblPrecargaSIES. Permite INDEX en Excel. 0 = no encontrado.",
         "NO","0..185","Python-computed. No es una fórmula Excel."),
        ("TRAZABILIDAD_257","_PY_DA_ROW_IN_TABLE","PYTHON","Pre-calculado en Python",
         "Fila 1-indexed dentro de tblDatosAlumnos. Permite INDEX en Excel. 0 = no encontrado.",
         "NO","0..13708","Python-computed. No es una fórmula Excel."),
        ("TRAZABILIDAD_257","ESTADO_FINAL_NACIONALIDAD","FORMULA","Calculada con fórmula Excel",
         "Estado de la comparación de nationalidades entre SIES y DatosAlumnos.",
         "PARCIALMENTE","EXTRANJERO_CONFIRMADO_AMBAS_FUENTES / AMBAS_FUENTES_SIN_NACIONALIDAD / CONFLICTO_SIES_VS_DATOS_ALUMNOS / ...","Ver FORMULAS_Y_REGLAS para la fórmula completa."),
        ("TRAZABILIDAD_257","ES_CHILE_SEGUN_SIES","FORMULA","Calculada con fórmula Excel",
         "Indica si SIES tiene código 38. SI solo si código = 38.",
         "SI","SI / NO / SIN_DATO / INVALIDO","Solo mira NACIONALIDAD_CARGADA_SIES. Nunca RUT o tipo de documento."),
        ("TRAZABILIDAD_257","PRIORIDAD_REVISION","FORMULA","Calculada con fórmula Excel",
         "Nivel de urgencia de revisión operativa.",
         "NO","PRIORIDAD 1 / PRIORIDAD 2 / PRIORIDAD 3","P1=ambas vacías o conflicto. P2=una fuente sin dato. P3=diferencias menores."),
    ]
    for i, row in enumerate(entries, 2):
        for j, v in enumerate(row, 1):
            ws.cell(row=i, column=j, value=v)

    make_table(ws, "tblDiccionario", f"A1:{get_column_letter(len(cols))}{len(entries)+1}")
    freeze(ws)
    autofilter(ws)
    widths = [22,30,12,30,60,20,40,50]
    set_widths(ws, widths)
    for i in range(2, len(entries)+2):
        ws.row_dimensions[i].height = 30
    print("  [OK] DICCIONARIO_COLUMNAS")

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 14 — CONTROL_COBERTURA
# ══════════════════════════════════════════════════════════════════════════════

def build_control_cobertura(ws, univ, xrefs, sies, da_headers, n_prio):
    h_ctl = hdr_style(C["hdr_ctrl"])
    ws.cell(row=1, column=1, value="INDICADOR")
    ws.cell(row=1, column=2, value="VALOR")
    ws.cell(row=1, column=3, value="DESCRIPCION")
    for j in range(1,4): applydict(ws.cell(row=1, column=j), h_ctl)

    da_nac_col = da_headers.index("NACIONALIDAD") if "NACIONALIDAD" in da_headers else None
    da_pais_orig_exists = "PAIS_DE_ORIGEN" in [h.upper() for h in da_headers]
    da_pais_sec_exists  = "PAIS_ESTUDIOS_SECUNDARIOS" in [h.upper() for h in da_headers]
    da_mail_exists      = "MAIL" in da_headers or "Mail_Inst" in da_headers

    stats = {}
    # Core counts
    stats["Registros esperados"]  = 257
    stats["Registros obtenidos"]  = len(univ)
    stats["Personas únicas"]      = len(set(u.get("CLAVE_PERSONA_DOCUMENTO","") for u in univ))

    # SIES
    in_sies    = sum(1 for x in xrefs if x["sies_row"] > 0)
    sies_nac_ok= sum(1 for x in xrefs if x["sies_nac"] and x["sies_nac"] not in ("","VACIO_EN_FUENTE"))
    sies_nac_vac=sum(1 for x in xrefs if not x["sies_nac"] or x["sies_nac"] in ("","VACIO_EN_FUENTE"))

    stats["Registros en precarga SIES"] = in_sies
    stats["Registros agregados localmente"] = len(univ) - in_sies
    stats["Nacionalidad SIES completa"] = sies_nac_ok
    stats["Nacionalidad SIES vacía"] = sies_nac_vac

    # DatosAlumnos
    da_found   = sum(1 for x in xrefs if x["da_row"] > 0)
    da_nac_ok  = sum(1 for x in xrefs if x["da_nac"] and x["da_nac"] not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO"))
    da_nac_vac = sum(1 for x in xrefs if not x["da_nac"] or x["da_nac"] in ("","VACIO_EN_FUENTE","NO_ENCONTRADO"))

    stats["Encontrados en DatosAlumnos"] = da_found
    stats["Nacionalidad DatosAlumnos completa"] = da_nac_ok
    stats["Nacionalidad DatosAlumnos vacía"] = da_nac_vac

    # Comparison
    both_ok, both_vac, only_sies, only_da, conflict = 0,0,0,0,0
    chile38, chile_da_count, invalid_count = 0,0,0
    for x in xrefs:
        s = x["sies_nac"]; d = x["da_nac"]
        s_has = bool(s and s not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO_EN_PRECARGA"))
        d_has = bool(d and d not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO"))
        try: sc = int(s) if s_has else -1
        except: sc = -1
        dc_up = d.upper().strip() if d_has else ""
        if s_has and d_has:
            if (sc==38 and dc_up=="CHILENA") or (1<=sc<=197 and sc!=38 and dc_up!="CHILENA"): both_ok+=1
            elif sc==38 and dc_up!="CHILENA": conflict+=1
            elif sc!=38 and dc_up=="CHILENA": conflict+=1
            else: both_ok+=1
        elif s_has and not d_has: only_sies+=1
        elif not s_has and d_has: only_da+=1
        else: both_vac+=1
        if sc==38: chile38+=1
        if d_has and dc_up=="CHILENA": chile_da_count+=1
        if s_has and (sc<1 or sc>197): invalid_count+=1

    pais_orig_sies = sum(1 for x in xrefs if x.get("sies_obj") and x["sies_obj"].get("PAIS_ORIGEN",""))

    stats["Ambas fuentes coincidentes"] = both_ok
    stats["Ambas fuentes sin nacionalidad"] = both_vac
    stats["Solo SIES con nacionalidad"] = only_sies
    stats["Solo DatosAlumnos con nationalidad"] = only_da
    stats["Conflictos entre fuentes"] = conflict
    stats["Código 38 (Chile) en SIES"] = chile38
    stats["DatosAlumnos indica CHILENA"] = chile_da_count
    stats["Códigos SIES inválidos (fuera 1-197)"] = invalid_count
    stats["País de origen disponible en SIES"] = pais_orig_sies
    stats["País de origen disponible en DatosAlumnos"] = 0  # doesn't exist
    stats["País estudios secundarios SIES"] = sum(1 for x in xrefs if x.get("sies_obj") and x["sies_obj"].get("PAIS_ESTUDIOS_SECUNDARIOS",""))
    stats["País estudios secundarios DatosAlumnos"] = 0  # doesn't exist
    stats["Campo Pais_De_Origen existe en DatosAlumnos"] = "NO"
    stats["Campo Pais_Estudios_Sec existe en DatosAlumnos"] = "NO"

    descr = {
        "Registros esperados": "Deben ser exactamente 257",
        "Registros obtenidos": "Debe ser igual a 257",
        "Personas únicas": "Personas distintas por CLAVE_PERSONA_DOCUMENTO",
        "Registros en precarga SIES": "Encontrados en la precarga PES 2026",
        "Registros agregados localmente": "No están en la precarga; fuente local",
        "Nacionalidad SIES completa": "Tienen código de nationalidad en SIES",
        "Nacionalidad SIES vacía": "Sin código de nationalidad en SIES",
        "Encontrados en DatosAlumnos": "Encontrados en hoja DatosAlumnos de PROMEDIOS",
        "Nacionalidad DatosAlumnos completa": "Tienen texto de nationalidad en DatosAlumnos",
        "Nacionalidad DatosAlumnos vacía": "Sin texto de nationalidad en DatosAlumnos",
        "Ambas fuentes coincidentes": "Ambas fuentes tienen dato y son coherentes",
        "Ambas fuentes sin nacionalidad": "Ninguna fuente tiene dato → PRIORIDAD 1",
        "Solo SIES con nacionalidad": "SIES tiene dato, DatosAlumnos no → PRIORIDAD 2",
        "Solo DatosAlumnos con nationalidad": "DatosAlumnos tiene dato, SIES no → PRIORIDAD 2",
        "Conflictos entre fuentes": "Una dice Chile, otra dice extranjero → PRIORIDAD 1",
        "Código 38 (Chile) en SIES": "SIES tiene código 38. Verificar si son chilenos en universo.",
        "DatosAlumnos indica CHILENA": "DatosAlumnos dice CHILENA. Verificar.",
        "Códigos SIES inválidos (fuera 1-197)": "Código inválido según normativa → PRIORIDAD 1",
        "País de origen disponible en SIES": "Registros con PAIS_ORIGEN en precarga SIES",
        "País de origen disponible en DatosAlumnos": "Campo NO EXISTE en DatosAlumnos",
        "País estudios secundarios SIES": "Registros con PAIS_ESTUDIOS_SECUNDARIOS en SIES",
        "País estudios secundarios DatosAlumnos": "Campo NO EXISTE en DatosAlumnos",
        "Campo Pais_De_Origen existe en DatosAlumnos": "Verificado en Fase 1",
        "Campo Pais_Estudios_Sec existe en DatosAlumnos": "Verificado en Fase 1",
    }

    for i, (k, v) in enumerate(stats.items(), 2):
        ws.cell(row=i, column=1, value=k)
        ws.cell(row=i, column=2, value=v)
        ws.cell(row=i, column=3, value=descr.get(k,""))

    make_table(ws, "tblControlCobertura", f"A1:C{len(stats)+1}")
    freeze(ws)
    ws.column_dimensions["A"].width = 45
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 60
    print("  [OK] CONTROL_COBERTURA")
    return stats

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 15 — FORMULAS_Y_REGLAS
# ══════════════════════════════════════════════════════════════════════════════

def build_formulas_reglas(ws):
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 80
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 40
    ws.column_dimensions["E"].width = 50
    ws.column_dimensions["F"].width = 20

    h_ctl = hdr_style(C["hdr_ctrl"])
    headers = ["COLUMNA","FORMULA_O_LOGICA","FUENTE","REGLA_NORMATIVA",
               "VALORES_POSIBLES","PUEDE_DETERMINAR_NACIONALIDAD"]
    for j, h in enumerate(headers, 1):
        applydict(ws.cell(row=1, column=j, value=h), h_ctl)

    aviso_row = 2
    ws.cell(row=aviso_row, column=1, value="AVISO NORMATIVO").font = Font(bold=True, size=14, color="FF0000")
    ws.cell(row=aviso_row, column=2,
            value="EL RUT NO DEFINE LA NACIONALIDAD. LA NACIONALIDAD SOLO PUEDE CONFIRMARSE MEDIANTE "
                  "EL CAMPO NACIONALIDAD O UNA FUENTE INSTITUCIONAL OFICIAL.").font = Font(bold=True, color="FF0000")
    ws.row_dimensions[aviso_row].height = 40

    entries = [
        ("CLAVE_PC (RAW_PRECARGA_SIES)",
         '=UPPER(TRIM(TIPO_DOCUMENTO))&"|"&UPPER(TRIM(NUM_DOCUMENTO))',
         "Calculada Excel","Sin regla normativa",
         "TIPO|NUM_DOCUMENTO","NO"),
        ("CLAVE_PCC (RAW_PRECARGA_SIES)",
         '=UPPER(TRIM(TIPO_DOCUMENTO))&"|"&UPPER(TRIM(NUM_DOCUMENTO))&"|"&UPPER(TRIM(CODIGO_UNICO))',
         "Calculada Excel","Sin regla normativa",
         "TIPO|NUM|CODIGO_UNICO","NO"),
        ("CLAVE_RUT_NUM (RAW_DATOS_ALUMNOS)",
         '=IFERROR(LEFT(RUT,FIND("-",RUT)-1),RUT)',
         "Calculada Excel","Sin regla normativa",
         "Número RUT sin DV","NO — número no determina nationalidad"),
        ("_PY_SIES_ROW_IN_TABLE",
         "Calculado en Python. Posición 1-indexed en tblPrecargaSIES. 0=no encontrado.",
         "Python","Sin regla normativa","0..185","NO"),
        ("_PY_DA_ROW_IN_TABLE",
         "Calculado en Python. Posición 1-indexed en tblDatosAlumnos. 0=no encontrado.",
         "Python","Sin regla normativa","0..13708","NO"),
        ("NACIONALIDAD_CARGADA_SIES",
         "=IF(_PY_SIES_ROW_IN_TABLE>0, IFERROR(INDEX(tblPrecargaSIES[NACIONALIDAD],_PY_SIES_ROW_IN_TABLE),\"VACIO_EN_FUENTE\"),\"NO_ENCONTRADO_EN_PRECARGA\")",
         "Calculada Excel","Instructivo SIES 2026: campo NACIONALIDAD, rango 1-197",
         "Código numérico 1-197 / VACIO_EN_FUENTE / NO_ENCONTRADO_EN_PRECARGA","SI"),
        ("NACIONALIDAD_DATOS_ALUMNOS",
         "=IF(_PY_DA_ROW_IN_TABLE>0, IFERROR(INDEX(tblDatosAlumnos[NACIONALIDAD],_PY_DA_ROW_IN_TABLE),\"VACIO_EN_FUENTE\"),\"NO_ENCONTRADO\")",
         "Calculada Excel","Solo usar campo NACIONALIDAD explícito. No inferir.",
         "CHILENA / VENEZOLANA / [texto] / VACIO_EN_FUENTE / NO_ENCONTRADO","PARCIALMENTE"),
        ("ES_CHILE_SEGUN_SIES",
         "=IF(SIES vacío)→SIN_DATO ; IF(código=38)→SI ; IF(1<=código<=197)→NO ; ELSE→INVALIDO",
         "Calculada Excel","Código 38 = Chile. Único criterio válido.",
         "SI / NO / SIN_DATO / INVALIDO","SI"),
        ("ES_EXTRANJERO_SEGUN_SIES",
         "=IF(vacío)→NO_DETERMINABLE ; IF(1<=código<=197 y código<>38)→SI ; IF(código=38)→NO",
         "Calculada Excel","Rango válido 1-197. Código 38 = Chile.",
         "SI / NO / NO_DETERMINABLE","SI"),
        ("ES_EXTRANJERO_SEGUN_DATOS_ALUMNOS",
         "=IF(vacío)→NO_DETERMINABLE ; IF(texto=CHILENA)→NO ; ELSE→SI",
         "Calculada Excel","Solo campo NACIONALIDAD. Nunca desde RUT, dirección o colegio.",
         "SI / NO / NO_DETERMINABLE","PARCIALMENTE"),
        ("ESTADO_FINAL_NACIONALIDAD",
         "Anidamiento de condiciones: ambas coinciden extranero → CONFIRMADO; conflicto Chile/extranjero → CONFLICTO; etc.",
         "Calculada Excel","Cruce de ambas fuentes según normativa SIES.",
         "EXTRANJERO_CONFIRMADO_AMBAS_FUENTES / CONFLICTO_SIES_VS_DATOS_ALUMNOS / AMBAS_FUENTES_SIN_NACIONALIDAD / SIES_SIN_NACIONALIDAD_DATOS_ALUMNOS_CON_DATO / SIES_CON_NACIONALIDAD_DATOS_ALUMNOS_SIN_DATO / CHILE_SEGUN_SIES / CHILE_SEGUN_DATOS_ALUMNOS / CODIGO_INVALIDO / NO_DETERMINABLE","SI"),
        ("PRIORIDAD_REVISION",
         "P1: ambas vacías, conflicto, código inválido. P2: una fuente sin dato, Chile detectado. P3: diferencias menores.",
         "Calculada Excel","Operativo. No normativo.",
         "PRIORIDAD 1 / PRIORIDAD 2 / PRIORIDAD 3","NO"),
        ("PAIS_ORIGEN_DATOS_ALUMNOS",
         "Valor fijo: NO_EXISTE_EN_FUENTE",
         "Python / Inspección Fase 1",
         "Normativa prohíbe inferir país de origen de ciudad, colegio o dirección.",
         "NO_EXISTE_EN_FUENTE","NO"),
        ("PAIS_EST_SEC_DATOS_ALUMNOS",
         "Valor fijo: NO_EXISTE_EN_FUENTE",
         "Python / Inspección Fase 1",
         "Normativa prohíbe inferir país de estudios desde CIUDADCOLEGIO o COMUNACOLEGIO.",
         "NO_EXISTE_EN_FUENTE","NO"),
    ]

    for i, row in enumerate(entries, 3):
        for j, v in enumerate(row, 1):
            c = ws.cell(row=i, column=j, value=v)
            if row[5] == "NO":
                c.fill = PatternFill("solid", fgColor="FFE0E0")

    make_table(ws, "tblFormulasReglas", f"A1:F{len(entries)+2}")
    freeze(ws)
    autofilter(ws)
    for i in range(2, len(entries)+3):
        ws.row_dimensions[i].height = 28
    print("  [OK] FORMULAS_Y_REGLAS")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n=== Generador Auditoría Trazable Nacionalidad 257 ===")
    print(f"Timestamp: {TS}\n")

    # Ensure output dirs
    F_EXCEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    F_REPORTE.parent.mkdir(parents=True, exist_ok=True)

    # Backup if exists
    if F_EXCEL_OUT.exists():
        ts_safe = datetime.now().strftime('%Y%m%d_%H%M%S')
        bk = F_EXCEL_OUT.with_name(f"BACKUP_{ts_safe}_{F_EXCEL_OUT.name}")
        shutil.copy2(F_EXCEL_OUT, bk)
        print(f"  [BACKUP] {bk}")

    print("→ Cargando fuentes...")
    univ = load_universo()
    sies = load_precarga()
    da_headers, da_data = load_datos_alumnos()
    mat  = load_matricula_ctrl()
    assert len(univ) == 257, f"ERROR: universo tiene {len(univ)} filas, se esperan 257"
    print(f"  Universo: {len(univ)} filas")
    print(f"  Precarga SIES: {len(sies)} filas")
    print(f"  DatosAlumnos: {len(da_data)} filas × {len(da_headers)} cols")
    print(f"  Matrícula control: {len(mat)} filas")

    print("→ Generando inspección DatosAlumnos...")
    generate_inspection(da_headers, da_data)

    print("→ Calculando cruces...")
    xrefs, da_nac_col, da_codcli_col, da_rut_col = compute_xrefs(univ, sies, da_headers, da_data)

    print("→ Construyendo Excel...")
    wb = Workbook()
    wb.remove(wb.active)  # remove default sheet

    sheet_names = [
        "INSTRUCCIONES","RAW_UNIVERSO_257","RAW_PRECARGA_SIES","RAW_DATOS_ALUMNOS",
        "RAW_MATRICULA_2025","TRAZABILIDAD_257","PRIORITARIOS_SIN_NACIONALIDAD",
        "CONFLICTOS_NACIONALIDAD","MULTIPLES_CARRERAS","DICCIONARIO_COLUMNAS",
        "CONTROL_COBERTURA","FORMULAS_Y_REGLAS",
    ]
    sheets = {name: wb.create_sheet(name) for name in sheet_names}

    h_univ  = fhash(F_UNIVERSO)
    h_sies  = fhash(F_PREC_ORIG)
    h_promo = fhash(F_PROMEDIOS)
    h_mat   = fhash(F_MAT_CTRL)

    build_instrucciones(sheets["INSTRUCCIONES"])
    build_raw_universo(sheets["RAW_UNIVERSO_257"], univ, h_univ)
    build_raw_precarga(sheets["RAW_PRECARGA_SIES"], sies, h_sies)

    print("  → Escribiendo RAW_DATOS_ALUMNOS (13k+ filas)...")
    build_raw_datos_alumnos(sheets["RAW_DATOS_ALUMNOS"], da_headers, da_data, h_promo)

    build_raw_matricula(sheets["RAW_MATRICULA_2025"], mat)
    traz_col_idx = build_trazabilidad(sheets["TRAZABILIDAD_257"], univ, xrefs, sies, da_headers)
    n_prio = build_prioritarios(sheets["PRIORITARIOS_SIN_NACIONALIDAD"], univ, xrefs, sies, da_headers)
    build_conflictos(sheets["CONFLICTOS_NACIONALIDAD"], univ, xrefs)
    build_multiples_carreras(sheets["MULTIPLES_CARRERAS"], univ, xrefs)
    build_diccionario(sheets["DICCIONARIO_COLUMNAS"])
    stats = build_control_cobertura(sheets["CONTROL_COBERTURA"], univ, xrefs, sies, da_headers, n_prio)
    build_formulas_reglas(sheets["FORMULAS_Y_REGLAS"])

    print(f"→ Guardando Excel: {F_EXCEL_OUT}")
    wb.save(F_EXCEL_OUT)
    print(f"  [OK] Excel guardado")

    # ── Audit CSV ───────────────────────────────────────────────────────────
    with open(F_AUD_GEN, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["CAMPO","VALOR"])
        w.writerow(["TIMESTAMP_GENERACION", TS])
        w.writerow(["ARCHIVO_EXCEL_SALIDA", str(F_EXCEL_OUT)])
        w.writerow(["HASH_EXCEL", fhash(F_EXCEL_OUT)])
        w.writerow(["REGISTROS_UNIVERSO", len(univ)])
        w.writerow(["REGISTROS_PRECARGA_SIES", len(sies)])
        w.writerow(["FILAS_DATOS_ALUMNOS", len(da_data)])
        w.writerow(["COLUMNAS_DATOS_ALUMNOS", len(da_headers)])
        w.writerow(["HOJA_DATOS_ALUMNOS", "DatosAlumnos"])
        w.writerow(["HASH_UNIVERSO", h_univ])
        w.writerow(["HASH_PRECARGA_SIES", h_sies])
        w.writerow(["HASH_PROMEDIOS", h_promo])
        w.writerow(["HASH_MATRICULA", h_mat])
        for k, v in stats.items():
            w.writerow([f"STAT_{k.upper().replace(' ','_')}", v])
    print(f"  [OK] Auditoría: {F_AUD_GEN}")

    # ── Markdown report (summary tables filled from stats) ──────────────────
    sies_nac_ok = stats.get("Nacionalidad SIES completa", 0)
    sies_nac_vac= stats.get("Nacionalidad SIES vacía", 0)
    da_nac_ok   = stats.get("Nacionalidad DatosAlumnos completa", 0)
    da_nac_vac  = stats.get("Nacionalidad DatosAlumnos vacía", 0)
    both_ok_v   = stats.get("Ambas fuentes coincidentes", 0)
    only_sies_v = stats.get("Solo SIES con nacionalidad", 0)
    only_da_v   = stats.get("Solo DatosAlumnos con nationalidad", 0)
    both_vac_v  = stats.get("Ambas fuentes sin nacionalidad", 0)
    conflict_v  = stats.get("Conflictos entre fuentes", 0)
    chile38_v   = stats.get("Código 38 (Chile) en SIES", 0)
    invalid_v   = stats.get("Códigos SIES inválidos (fuera 1-197)", 0)
    total_v     = both_ok_v + only_sies_v + only_da_v + both_vac_v + conflict_v

    # Prioritarios from Python
    prio1 = sum(1 for u,x in zip(univ,xrefs) if True)  # recalculate
    p1=p2=p3=0
    for u,x in zip(univ,xrefs):
        s=x["sies_nac"]; d=x["da_nac"]
        sh=bool(s and s not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO_EN_PRECARGA"))
        dh=bool(d and d not in ("","VACIO_EN_FUENTE","NO_ENCONTRADO"))
        try: sc=int(s) if sh else -1
        except: sc=-1
        dup=d.upper().strip() if dh else ""
        if not sh and not dh: p1+=1
        elif (sc==38 and dup!="CHILENA" and dh) or (sc!=38 and sc!=-1 and dup=="CHILENA"): p1+=1
        elif sh and not dh: p2+=1
        elif not sh and dh: p2+=1
        elif sc==38: p2+=1
        elif sh and dh: pass  # confirmed
        else: p3+=1

    md = f"""# Reporte Auditoría Trazable Nacionalidad — 257 Registros
Generado: {TS}

## Archivos generados
- Excel: `{F_EXCEL_OUT}`
- Inspección: `{F_INSPECCION}`
- Auditoría generación: `{F_AUD_GEN}`

## Hoja de datos personales identificada
| Campo | Valor |
|---|---|
| Nombre de la hoja | DatosAlumnos |
| Filas de datos | {len(da_data):,} |
| Columnas originales | {len(da_headers)} |
| Columna NACIONALIDAD existe | SÍ (texto, no código) |
| Columna PAIS_DE_ORIGEN existe | NO |
| Columna PAIS_ESTUDIOS_SECUNDARIOS existe | NO |

## Confirmación de 257 registros
- Registros en universo depurado: **{len(univ)}** ✓

## TABLA 1 — NACIONALIDAD

| Estado | Registros |
|---|---:|
| SIES y DatosAlumnos coinciden | {both_ok_v} |
| SIES con dato / DatosAlumnos vacío | {only_sies_v} |
| SIES vacío / DatosAlumnos con dato | {only_da_v} |
| Ambas fuentes vacías | {both_vac_v} |
| Conflicto entre fuentes | {conflict_v} |
| Código Chile 38 | {chile38_v} |
| Código inválido | {invalid_v} |
| **Total** | **{len(univ)}** |

## TABLA 2 — PRIORITARIOS

| Prioridad | Registros | Motivo principal |
|---|---:|---|
| Prioridad 1 | {p1} | Ambas fuentes sin dato / conflicto Chile-extranjero / código inválido |
| Prioridad 2 | {p2} | Una fuente sin dato / Chile detectado en una fuente |
| Prioridad 3 | {p3} | Diferencias menores o sin prioridad activa |

## TABLA 3 — DISPONIBILIDAD DE DATOS EN DatosAlumnos

| Campo | Existe como columna | Registros con dato | Registros vacíos |
|---|---|---:|---:|
| Nacionalidad | SÍ (texto) | {da_nac_ok} | {da_nac_vac} |
| País de origen | NO | 0 | {len(da_data)} |
| País estudios secundarios | NO | 0 | {len(da_data)} |
| Correo institucional (Mail_Inst) | SÍ | — | — |
| Correo personal (MAIL) | SÍ | — | — |
| Teléfono (FONOACTUAL) | SÍ | — | — |
| Dirección (DIRECCIONACTUAL) | SÍ | — | — |

## Hashes de integridad
| Archivo | Hash SHA-256 (16 chars) |
|---|---|
| UNIVERSO_DEPURADO | {h_univ} |
| PRECARGA_SIES_ORIGINAL | {h_sies} |
| PROMEDIOSDEALUMNOS | {h_promo} |
| MATRICULA_CONTROL | {h_mat} |
| EXCEL_AUDITORIA (salida) | {fhash(F_EXCEL_OUT)} |

## Notas normativas críticas
- **EL RUT NO DEFINE LA NACIONALIDAD.**
- La NACIONALIDAD SOLO PUEDE CONFIRMARSE MEDIANTE EL CAMPO NACIONALIDAD O UNA FUENTE INSTITUCIONAL OFICIAL.
- En DatosAlumnos, CIUDADCOLEGIO y COMUNACOLEGIO NO son equivalentes a país de estudios secundarios.
- PAIS_DE_ORIGEN y PAIS_ESTUDIOS_SECUNDARIOS no existen como columnas en DatosAlumnos.
"""
    with open(F_REPORTE, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  [OK] Reporte: {F_REPORTE}")

    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Excel:             {F_EXCEL_OUT}")
    print(f"Hoja DatosAlumnos: DatosAlumnos ({len(da_data)} filas × {len(da_headers)} cols)")
    print(f"Universo 257:      {len(univ)} registros confirmados")
    print(f"En precarga SIES:  {stats.get('Registros en precarga SIES',0)}")
    print(f"Match DatosAlumnos:{stats.get('Encontrados en DatosAlumnos',0)}")
    print(f"Nac SIES completa: {sies_nac_ok}")
    print(f"Nac DA completa:   {da_nac_ok}")
    print(f"Coincidentes:      {both_ok_v}")
    print(f"Conflictos:        {conflict_v}")
    print(f"Ambas vacías:      {both_vac_v}")
    print(f"Solo SIES:         {only_sies_v}")
    print(f"Solo DatosAlumnos: {only_da_v}")
    print(f"Código 38 (Chile): {chile38_v}")
    print(f"Códigos inválidos: {invalid_v}")
    print(f"PAIS_ORIGEN DA:    NO EXISTE EN FUENTE")
    print(f"PAIS_EST_SEC DA:   NO EXISTE EN FUENTE")
    print(f"Prioritarios P1:   {p1}")
    print(f"Prioritarios P2:   {p2}")
    print(f"Prioritarios P3:   {p3}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
