#!/usr/bin/env python3
"""Genera el archivo de carga de Etapa 3 (Aranceles) a partir del reporte 5910.

Estructura oficial (Anexo 3 del instructivo, 13 columnas A-M):
COD_SEDE, NOMBRE_SEDE, COD_CARRERA, NOMBRE_CARRERA, MODALIDAD, COD_JORNADA,
VERSION, FORMATO_VALOR, VALOR_MATRICULA_ANUAL, COSTO_TITULACION,
VALOR_CERTIFICADO_DIPLOMA, ARANCEL_ANUAL, VIGENCIA_CARRERA.
Solo H-L son modificables; A-G y M deben viajar identicos al 5910.

Los 103 programas de Etapa 1 ya traen ARANCEL_ANUAL real (se dejan intactos).
Los 37 programas nuevos de Etapa 2 traian -1 (pendiente); ninguno califica para
mantener -1 porque su FECHA_ADMISION_INICIAL (02/10/2026) es anterior al 23 de
diciembre (regla del instructivo, pag.5). Se completan con la tabla de
aranceles entregada por el usuario, cruzando por NOMBRE_CARRERA + sede +
modalidad/jornada. Cada fila completada queda con un nivel de confianza:
ALTA (match exacto de nombre y celda), MEDIA (alias de nombre o celda con
una sola cifra en la fila de origen) o FALTA (sin valor en la tabla entregada).
"""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
REPORTE_5910 = ROOT / "09_respaldo" / "reportes_pes_validados" / "20260907_reporte_5910_etapa1_2" / "5910 Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas.csv"
OUT_DIR = ROOT / "07_resultados" / "etapa3_aranceles_20260907"
CSV_OUT = OUT_DIR / "OFERTA_ACADEMICA_ARANCELES_2027_SIN_TITULOS_20260907.csv"
XLSX_OUT = OUT_DIR / "OFERTA_ACADEMICA_ARANCELES_2027_CON_TITULOS_20260907.xlsx"
DESKTOP_CSV = Path.home() / "Desktop" / "OFERTA_ACADEMICA_ARANCELES_2027_SIN_TITULOS_20260907.csv"
DESKTOP_XLSX = Path.home() / "Desktop" / "OFERTA_ACADEMICA_ARANCELES_2027_CON_TITULOS_20260907.xlsx"

# columnas del 5910 en orden (48, sin CODIGO_IES_NUM)
COLUMNAS_5910 = [
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
IDX = {c: i for i, c in enumerate(COLUMNAS_5910)}

# columnas finales del archivo de Etapa 3 (Anexo 3, 13 columnas)
COLUMNAS_ETAPA3 = [
    "COD_SEDE", "NOMBRE_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD",
    "COD_JORNADA", "VERSION", "FORMATO_VALOR", "VALOR_MATRICULA_ANUAL",
    "COSTO_TITULACION", "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL", "VIGENCIA_CARRERA",
]

# tabla de aranceles entregada por el usuario (imagen). Columnas: D/V/SP por sede + OL.
# None = celda vacia en la imagen.
TABLA_ARANCELES = {
    "TECNICO EN ENFERMERIA":                              (2404000, 2427000, 2427000, 2404000, 2427000, 2427000, None, 2427000, None, None),
    "INGENIERIA EN CIBERSEGURIDAD":                        (None, 2517000, None, None, None, None, None, None, None, 2464000),
    "INGENIERIA EN INFORMATICA":                           (None, 2430000, None, None, None, None, None, None, None, 2359000),
    "TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA":  (2174000, 2174000, None, None, 2174000, None, None, 2174000, None, None),
    "TECNICO EN ADMINISTRACION DE EMPRESAS":               (None, None, None, None, None, None, None, None, None, 2169000),
    "TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS":      (None, None, None, None, None, None, None, None, None, 2307000),
    "TECNICO EN MARKETING DIGITAL":                         (None, None, None, None, None, None, None, None, None, 2085000),
    "INGENIERIA EN ADMINISTRACION DE EMPRESAS":            (None, 2204000, None, None, None, None, None, None, None, 2169000),
    "TECNICO EN CIBERSEGURIDAD":                           (None, None, None, None, None, None, None, None, None, 2464000),
    "TECNICO EN LOGISTICA":                                (None, None, None, None, None, None, None, None, None, 2169000),
    "INGENIERIA EN LOGISTICA":                             (None, None, None, None, None, None, None, None, None, 2169000),
    "INGENIERIA INDUSTRIAL":                               (None, None, None, None, None, None, None, None, None, 2085000),
    "INGENIERIA EN MARKETING DIGITAL":                     (None, None, None, None, None, None, None, None, None, 2085000),
    "INGENIERIA EN CONECTIVIDAD Y REDES":                  (None, None, None, None, None, None, None, None, None, 2290000),
    "ADMINISTRACION PUBLICA":                              (None, None, None, None, None, None, None, None, None, 2106000),
    "CONTABILIDAD GENERAL":                                (None, None, None, None, None, None, None, None, None, 2101000),
    "TECNICO EN RECURSOS HUMANOS":                         (None, None, None, None, None, None, None, None, None, 2085000),
    "AUDITORIA":                                           (None, None, None, None, None, None, None, None, None, 2214000),
    "TECNICO EN FARMACIA":                                 (None, 2277000, 2277000, None, 2277000, 2277000, None, 2277000, 2277000, None),
    "TECNICO EN INFRAESTRUCTURA CLOUD":                    (None, None, None, None, None, None, None, None, None, 2190000),
    "TECNICO EN CONECTIVIDAD Y REDES":                     (None, None, None, None, None, None, None, None, None, 2290000),
    "INGENIERIA EN CONSTRUCCION":                          (None, None, 2524000, None, None, 2524000, None, None, None, None),
    "TECNICO EN CONSTRUCCION":                              (None, None, 2524000, None, None, 2524000, None, None, None, None),
    "TECNICO EN ADMINISTRACION PUBLICA":                   (None, None, None, None, None, None, None, None, None, 2106000),
    "INGENIERIA EN RECURSOS HUMANOS":                      (None, None, None, None, None, None, None, None, None, 2237000),
    "INGENIERIA EN PREVENCION DE RIESGOS":                 (None, None, None, None, None, None, None, None, None, 2198000),
    "INGENIERIA EN CIENCIA DE DATOS":                      (None, None, None, None, None, None, None, None, None, 2298000),
    "INGENIERIA EN FINANZAS":                              (None, None, None, None, None, None, None, None, None, 2085000),
    "TECNICO EN PREVENCION DE RIESGOS":                    (None, None, None, None, None, None, None, None, None, 2085000),
    "TECNICO EN FINANZAS":                                 (None, None, None, None, None, None, None, None, None, 2085000),
    "TECNICO EN CIENCIA DE DATOS":                         (None, None, None, None, None, None, None, None, None, 2180000),
    "INGENIERIA EN SEGURIDAD PRIVADA":                     (None, None, None, None, None, None, None, None, None, 2204000),
    "NATUROPATIA":                                         (None, 2085000, None, None, None, None, None, None, None, None),
    "INGENIERIA EN IA":                                    (None, None, None, None, None, None, None, None, None, 2237000),
    "TECNICO EN IA":                                        (None, None, None, None, None, None, None, None, None, 2237000),
    "TECNICO VETERINARIO":                                  (None, 2353000, None, None, None, 2353000, None, None, None, None),
    "INGENIERIA EN COMERCIO EXTERIOR":                      (None, None, None, None, None, None, None, None, None, 2198000),
    "TECNICO EN COMERCIO EXTERIOR":                         (None, None, None, None, None, None, None, None, None, 2198000),
    "INGENIERIA EN MINAS":                                  (None, None, None, None, None, None, None, None, None, 2396000),
    "TECNICO EN ODONTOLOGIA":                               (None, None, None, None, None, 2524000, None, None, None, None),
    "TECNICO EN MINERIA":                                   (None, None, None, None, None, None, None, None, None, 2396000),
    "INGENIERIA EN ARQUITECTURA CLOUD":                     (None, None, None, None, None, None, None, None, None, 2395000),
    "TECNICO EN IMAGENOLOGIA":                              (None, None, 2524000, None, None, 2524000, None, None, None, None),
    "INGENIERIA EN ELECTRICIDAD":                           (None, None, 2524000, None, None, 2524000, None, None, None, None),
    "TECNICO EN ELECTRICIDAD":                              (None, None, 2398000, None, None, 2398000, None, None, None, None),
}

# alias: nombre en la tabla de aranceles -> nombre real en el 5910
ALIAS = {
    "TECNICO VETERINARIO": "TECNICO VETERINARIO EN CLINICA DE ANIMALES DE COMPAÑIA",
    "INGENIERIA EN MINAS": "INGENIERIA EN OPERACIONES MINERAS",
    "TECNICO EN MINERIA": "TECNICO EN OPERACIONES MINERAS",
    "INGENIERIA EN IA": "INGENIERIA EN INTELIGENCIA ARTIFICIAL",
    "TECNICO EN IA": "TECNICO EN INTELIGENCIA ARTIFICIAL",
}
CONFIANZA_ALIAS = {k: "MEDIA - nombre abreviado en la tabla de aranceles, confirmar equivalencia" for k in ALIAS}

# posiciones en la tupla de 10 valores
COL_D_STGO, COL_V_STGO, COL_SP_STGO = 0, 1, 2
COL_D_CONC, COL_V_CONC, COL_SP_CONC = 3, 4, 5
COL_D_PM, COL_V_PM, COL_SP_PM = 6, 7, 8
COL_OL = 9

SEDE_GRUPO = {"2": (COL_D_STGO, COL_V_STGO, COL_SP_STGO), "3": (COL_D_CONC, COL_V_CONC, COL_SP_CONC), "4": (COL_D_PM, COL_V_PM, COL_SP_PM)}
MOD_JOR_A_POS = {("1", "1"): 0, ("1", "2"): 1, ("2", "3"): 2}  # posicion relativa dentro del grupo de 3 (D/V/SP)

# Valores confirmados por el usuario el 07/09/2026: los 4 que quedaron SIN_VALOR
# y los 10 de confianza MEDIA, ya revisados y validados contra la planilla original.
CONFIRMADOS_USUARIO = {
    ("2", "78", "1", "2"): 2204000,
    ("2", "133", "2", "3"): 2524000,
    ("2", "138", "2", "3"): 2398000,
    ("2", "139", "2", "3"): 2524000,
    ("2", "134", "3", "4"): 2237000,
    ("2", "135", "3", "4"): 2396000,
    ("2", "140", "3", "4"): 2237000,
    ("2", "142", "3", "4"): 2396000,
    ("2", "143", "2", "3"): 2353000,
    ("3", "133", "2", "3"): 2524000,
    ("3", "138", "2", "3"): 2398000,
    ("3", "139", "2", "3"): 2524000,
    ("3", "141", "2", "3"): 2524000,
    ("3", "143", "2", "3"): 2353000,
}


def read_5910() -> tuple[list[str], list[list[str]]]:
    with REPORTE_5910.open("r", encoding="latin-1", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=";"))
    header, data = rows[0], rows[1:]
    pos = [header.index(c) for c in COLUMNAS_5910]
    return header, [[row[p] for p in pos] for row in data]


def buscar_arancel(nombre: str, sede: str, cod_carrera: str, modalidad: str, jornada: str) -> tuple[str | int, str]:
    """Devuelve (valor_o_'FALTA', nota_de_confianza)."""
    confirmado = CONFIRMADOS_USUARIO.get((sede, cod_carrera, modalidad, jornada))
    if confirmado is not None:
        return confirmado, "CONFIRMADA POR EL USUARIO 07/09/2026"
    nombre_tabla = nombre
    nota_alias = ""
    if nombre not in TABLA_ARANCELES:
        alias_inverso = {v: k for k, v in ALIAS.items()}
        if nombre in alias_inverso:
            nombre_tabla = alias_inverso[nombre]
            nota_alias = CONFIANZA_ALIAS[nombre_tabla]
        else:
            return "FALTA", "SIN FILA EN LA TABLA DE ARANCELES - completar manualmente"

    valores = TABLA_ARANCELES[nombre_tabla]
    if (modalidad, jornada) == ("3", "4"):
        valor = valores[COL_OL]
        if valor is None:
            return "FALTA", "SIN VALOR OL EN LA TABLA - completar manualmente"
        return valor, nota_alias or "ALTA - columna OL, valor unico para la carrera"

    grupo = SEDE_GRUPO.get(sede)
    if grupo is None:
        return "FALTA", f"SEDE {sede} SIN GRUPO DE COLUMNAS CONOCIDO"
    pos_relativa = MOD_JOR_A_POS.get((modalidad, jornada))
    valores_grupo = [valores[p] for p in grupo]
    no_vacios = [v for v in valores_grupo if v is not None]
    if pos_relativa is not None and valores_grupo[pos_relativa] is not None:
        return valores_grupo[pos_relativa], nota_alias or "ALTA - celda exacta encontrada para sede y jornada"
    if len(no_vacios) == 1:
        return no_vacios[0], (nota_alias + " / " if nota_alias else "") + "MEDIA - unico valor no vacio en el grupo de la sede, se asume igual para toda modalidad ofrecida"
    return "FALTA", "SIN VALOR PARA ESA SEDE/JORNADA EN LA TABLA - completar manualmente"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    header5910, rows = read_5910()

    resultado: list[dict] = []
    for row in rows:
        etapa3 = {c: row[IDX[c]] for c in COLUMNAS_ETAPA3}
        arancel_previo = row[IDX["ARANCEL_ANUAL"]]
        es_nuevo = arancel_previo == "-1"
        confianza = "ORIGINAL - no vigente este ciclo o sin match en la tabla, sin cambios"
        actualizado = False
        if row[IDX["VIGENCIA_CARRERA"]] == "1":
            valor, nota = buscar_arancel(
                row[IDX["NOMBRE_CARRERA"]], row[IDX["COD_SEDE"]], row[IDX["COD_CARRERA"]], row[IDX["MODALIDAD"]], row[IDX["COD_JORNADA"]])
            if valor == "FALTA":
                confianza = "ORIGINAL - sin match en la tabla de aranceles, se mantiene el valor del 5910" if not es_nuevo else nota
            else:
                if str(valor) != arancel_previo:
                    actualizado = True
                etapa3["FORMATO_VALOR"] = "1"
                etapa3["VALOR_MATRICULA_ANUAL"] = "185000"
                etapa3["COSTO_TITULACION"] = "0"
                etapa3["VALOR_CERTIFICADO_DIPLOMA"] = "0"
                etapa3["ARANCEL_ANUAL"] = str(valor)
                confianza = nota
        resultado.append({"campos": etapa3, "confianza": confianza, "es_nuevo": es_nuevo,
                           "actualizado": actualizado, "arancel_previo": arancel_previo})

    # --- CSV para cargar al sistema: sin encabezado, sin columna de institucion (ya no viene), ; y sin fila vacia final ---
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", lineterminator="\n")
        for item in resultado:
            writer.writerow([item["campos"][c] for c in COLUMNAS_ETAPA3])
    # eliminar linea final vacia si csv.writer la dejo
    contenido = CSV_OUT.read_text(encoding="utf-8")
    if contenido.endswith("\n"):
        CSV_OUT.write_text(contenido[:-1], encoding="utf-8")

    # --- XLSX para revisión, con encabezado + columnas de trazabilidad ---
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Etapa3_Aranceles_2027"
    headers = COLUMNAS_ETAPA3 + ["ES_PROGRAMA_NUEVO_ETAPA2", "ARANCEL_CORREGIDO_VS_5910", "ARANCEL_ANUAL_EN_5910", "CONFIANZA_ARANCEL"]
    for col, titulo in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=titulo)
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.font = Font(color="FFFFFF", bold=True)
    ws.freeze_panes = "A2"

    faltantes = []
    medias = []
    corregidos = []
    for r, item in enumerate(resultado, start=2):
        campos = item["campos"]
        for c, nombre_col in enumerate(COLUMNAS_ETAPA3, start=1):
            ws.cell(row=r, column=c, value=campos[nombre_col])
        ws.cell(row=r, column=len(COLUMNAS_ETAPA3) + 1, value=item["es_nuevo"])
        ws.cell(row=r, column=len(COLUMNAS_ETAPA3) + 2, value=item["actualizado"])
        ws.cell(row=r, column=len(COLUMNAS_ETAPA3) + 3, value=item["arancel_previo"])
        cell_conf = ws.cell(row=r, column=len(COLUMNAS_ETAPA3) + 4, value=item["confianza"])
        if campos["ARANCEL_ANUAL"] == "-1":
            cell_conf.fill = PatternFill("solid", fgColor="FFC7CE")
            faltantes.append((campos["COD_SEDE"], campos["COD_CARRERA"], campos["NOMBRE_CARRERA"], campos["MODALIDAD"], campos["COD_JORNADA"]))
        elif item["actualizado"] and not item["es_nuevo"]:
            cell_conf.fill = PatternFill("solid", fgColor="F4B084")
            corregidos.append((campos["COD_SEDE"], campos["COD_CARRERA"], campos["NOMBRE_CARRERA"], campos["MODALIDAD"], campos["COD_JORNADA"], item["arancel_previo"], campos["ARANCEL_ANUAL"]))
        elif item["confianza"].startswith("CONFIRMADA"):
            cell_conf.fill = PatternFill("solid", fgColor="BDD7EE")
        elif item["confianza"].startswith("MEDIA"):
            cell_conf.fill = PatternFill("solid", fgColor="FFEB9C")
            medias.append((campos["COD_SEDE"], campos["COD_CARRERA"], campos["NOMBRE_CARRERA"], campos["MODALIDAD"], campos["COD_JORNADA"], campos["ARANCEL_ANUAL"]))
        elif item["es_nuevo"]:
            cell_conf.fill = PatternFill("solid", fgColor="C6EFCE")

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18
    ws.column_dimensions[get_column_letter(len(COLUMNAS_ETAPA3) + 4)].width = 70

    ws2 = wb.create_sheet("Resumen", 0)
    ws2.sheet_view.showGridLines = False
    filas = [
        ("Etapa 3 - Definición de Arancel TP 2027", None),
        ("Ventana", "07 al 11 de septiembre de 2026"),
        ("", None),
        ("Total programas en el archivo (Etapa 1 + Etapa 2)", len(resultado)),
        ("Programas vigentes (VIGENCIA_CARRERA=1), requieren arancel informado", sum(1 for r in rows if r[IDX["VIGENCIA_CARRERA"]] == "1")),
        ("Programas nuevos de Etapa 2 completados (venian en -1)", sum(1 for i in resultado if i["es_nuevo"])),
        ("Programas YA tenian arancel pero estaba desactualizado vs. la tabla - CORREGIDOS", len(corregidos)),
        ("", None),
        ("Completados con confianza ALTA", sum(1 for i in resultado if i["es_nuevo"] and i["confianza"].startswith("ALTA"))),
        ("Completados y confirmados por el usuario 07/09/2026", sum(1 for i in resultado if i["es_nuevo"] and i["confianza"].startswith("CONFIRMADA"))),
        ("Completados con confianza MEDIA (verificar antes de subir)", len(medias)),
        ("SIN VALOR - pendientes de completar manualmente", len(faltantes)),
        ("", None),
        ("Estado", "SIN PENDIENTES" if not faltantes and not medias else "QUEDAN PENDIENTES POR REVISAR"),
        ("", None),
        ("ALERTA CORREGIDA 07/09/2026", "El usuario detecto que INGENIERIA EN INFORMATICA (OL) traia 2.240.000 en el 5910 pero la tabla de aranceles indica 2.359.000. Se audito todo el archivo: 25 programas vigentes tenian arancel desactualizado (no solo los 37 nuevos). Ver hoja Corregidos_valor_desactualizado."),
        ("Regla aplicada (instructivo pág. 5)", "El valor -1 (sin información) solo es válido si FECHA_ADMISION_INICIAL es 23-dic-2026 o posterior. Los 37 programas nuevos tienen fecha 02-10-2026, por lo que NINGUNO puede quedar en -1."),
        ("Valores por defecto usados (consistentes con los 103 ya cargados)", "FORMATO_VALOR=1 (pesos), VALOR_MATRICULA_ANUAL=185000, COSTO_TITULACION=0, VALOR_CERTIFICADO_DIPLOMA=0"),
    ]
    for r, (label, value) in enumerate(filas, start=1):
        c1 = ws2.cell(row=r, column=1, value=label)
        if value is not None:
            ws2.cell(row=r, column=2, value=value)
        if value is None and label:
            c1.font = Font(bold=True)
    ws2.column_dimensions["A"].width = 60
    ws2.column_dimensions["B"].width = 90

    if medias:
        ws3 = wb.create_sheet("Revisar_confianza_MEDIA")
        ws3.append(["COD_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD", "COD_JORNADA", "ARANCEL_PROPUESTO"])
        for row_ in medias:
            ws3.append(list(row_))
        for col in range(1, 7):
            ws3.column_dimensions[get_column_letter(col)].width = 22

    if faltantes:
        ws4 = wb.create_sheet("SIN_VALOR_completar_manual")
        ws4.append(["COD_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD", "COD_JORNADA"])
        for row_ in faltantes:
            ws4.append(list(row_))
        for col in range(1, 6):
            ws4.column_dimensions[get_column_letter(col)].width = 22

    if corregidos:
        ws5 = wb.create_sheet("Corregidos_valor_desactualizado")
        ws5.append(["COD_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD", "COD_JORNADA", "ARANCEL_EN_5910_OBSOLETO", "ARANCEL_CORREGIDO"])
        for row_ in corregidos:
            ws5.append(list(row_))
        for col in range(1, 8):
            ws5.column_dimensions[get_column_letter(col)].width = 24

    wb.save(XLSX_OUT)
    shutil.copy2(CSV_OUT, DESKTOP_CSV)
    shutil.copy2(XLSX_OUT, DESKTOP_XLSX)

    print("Total resultado:", len(resultado))
    print("Confianza MEDIA (revisar):", len(medias))
    print("SIN VALOR (faltan):", len(faltantes))
    for f in faltantes:
        print("  FALTA:", f)
    for m in medias:
        print("  MEDIA:", m)


if __name__ == "__main__":
    main()
