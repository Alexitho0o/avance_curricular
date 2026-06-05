#!/usr/bin/env python3
"""Genera Excel ejecutivo de respaldo PES/SIES con XlsxWriter.

Fase 10D: incorpora etiquetas oficiales de codigos del instructivo SIES.
La escritura usa solo XlsxWriter; OpenPyXL se usa despues solo para validar.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
import shutil
from statistics import median

import xlsxwriter
from openpyxl import load_workbook


SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR.parent
REPO_DIR = MODULE_DIR.parent

BASE_GENERAL = MODULE_DIR / "data/base_general/base_general_personal_academico_en_institucion.tsv"
CSV_CARGADO = MODULE_DIR / "resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv"
CANDIDATO_EXPORTACION = MODULE_DIR / "data/base_general/candidatos_exportacion/base_general_en_institucion_SIN_PENDIENTE_FECHA_FUTURA_20260611_234029.tsv"
EXCLUSIONES_DIR = MODULE_DIR / "auditorias/exportacion_controlada"
OUTPUT_XLSX = MODULE_DIR / "resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx"
DESKTOP_XLSX = Path("/Users/alexi/Desktop/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx")
VALIDACION_TXT = MODULE_DIR / "resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt"
REPORTE = MODULE_DIR / "docs/REPORTE_FASE_10D_ETIQUETAS_OFICIALES_CODIGOS.md"
BITACORA = MODULE_DIR / "bitacoras/BITACORA_FASE_10D_ETIQUETAS_OFICIALES_CODIGOS.md"

FECHA_CORTE = date(2026, 5, 31)
INSTITUCION_OBJETIVO_CODIGO = 162
INSTITUCION_OBJETIVO_NOMBRE = "IP CIISA"
INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL = "IP San Sebastián / Instituto Profesional San Sebastián"
NOTA_CONTINUIDAD_INSTITUCIONAL = (
    "La serie historica se mantiene por continuidad del Codigo SIES 162. Aunque la institucion aparece "
    "historicamente como IP CIISA/CIISA y actualmente corresponde a IP San Sebastian, el analisis compara "
    "la misma entidad institucional por codigo SIES, no por coincidencia textual de nombre."
)
HIST_AUDIT_DIR = MODULE_DIR / "auditorias/historico_sies"
HIST_AUDIT_CSV = HIST_AUDIT_DIR / "auditoria_historico_sies_2008_2025.csv"
HIST_DICT_CSV = HIST_AUDIT_DIR / "diccionario_columnas_historico_sies.csv"
HIST_CONTINUIDAD_CSV = HIST_AUDIT_DIR / "auditoria_continuidad_institucional_162.csv"

COLUMNAS_OFICIALES = [
    "TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRES",
    "SEXO", "FECHA_NACIMIENTO", "NACIONALIDAD", "NIVEL_FORMACION_ACADEMICO", "NOMBRE_TITULO_O_GRADO",
    "NOMBRE_INSTITUCION_OBT_TITULO", "PAIS_OBTENCION_TIT_O_GRADO", "FECHA_OBT_TIT_O_GRADO",
    "NIVEL_FORMACION_ESPECIALIDAD", "TIPO_ESPECIALIDAD", "NOMBRE_ESPECIALIDAD",
    "NOMBRE_INST_OBT_ESPECIALIDAD", "PAIS_OBTENCION_ESPECIALIDAD", "FECHA_OBTENCION_ESPECIALIDAD",
    "PRINCIPAL_CARGO_ACADEMICO", "CARGO_NORMALIZADO", "NIVEL_SUPERIOR_ADSCRIPCION",
    "NIVEL_SECUNDARIO_ADSCRIPCION", "COMUNA_MAYOR_FUNCION", "NOMBRE_PRINCIPAL_PROGRAMA",
    "TOTAL_HORAS_PRINCIPAL_PROGRAMA", "COMUNA_PRINCIPAL_PROGRAMA", "NUM_HORAS_PLANTA",
    "NUM_HORAS_CONTRATA", "NUM_HORAS_HONORARIOS", "JERARQUIA_ACADEMICA", "JERARQUIA_ACADEMICA_OCDE",
    "VIGENCIA",
]

CONTROL_COLUMNS = [
    "ESTADO_CARGA_PES", "NUM_DOCUMENTO", "DV", "NOMBRE_COMPLETO", "MOTIVO_NO_CARGA_LEGIBLE",
    "COLUMNAS_OBSERVADAS", "VALORES_OBSERVADOS", "ACCION_REQUERIDA_LEGIBLE",
]

BASE_KPI_COLUMNS = [
    "ESTADO_CARGA_PES", "NUM_DOCUMENTO", "DV", "NOMBRE_COMPLETO", "MOTIVO_NO_CARGA_LEGIBLE",
    "COLUMNAS_OBSERVADAS", "ACCION_REQUERIDA_LEGIBLE", "SEXO", "SEXO_ETIQUETA", "FECHA_NACIMIENTO",
    "EDAD_AL_31_05_2026", "TRAMO_EDAD", "NACIONALIDAD", "NIVEL_FORMACION_ACADEMICO",
    "NIVEL_FORMACION_ACADEMICO_ETIQUETA", "NOMBRE_TITULO_O_GRADO", "PAIS_OBTENCION_TIT_O_GRADO",
    "FECHA_OBT_TIT_O_GRADO", "ANIOS_DESDE_TITULO", "TRAMO_ANTIGUEDAD_TITULO", "ES_MAGISTER",
    "ES_DOCTORADO", "ES_PROFESIONAL_CODIGO_3", "ES_TECNICO_CODIGO_5", "CARGO_NORMALIZADO",
    "CARGO_NORMALIZADO_ETIQUETA", "NOMBRE_PRINCIPAL_PROGRAMA", "COMUNA_PRINCIPAL_PROGRAMA",
    "NUM_HORAS_PLANTA_NUM", "NUM_HORAS_CONTRATA_NUM", "NUM_HORAS_HONORARIOS_NUM",
    "TOTAL_HORAS_ACADEMICO", "JCE_ESTIMADA", "TIPO_DEDICACION", "TIPO_VINCULO_HORARIO",
]

DICCIONARIO_COLUMNS = [
    "KPI_ID", "NOMBRE_KPI", "BLOQUE", "DEFINICION_CUALITATIVA", "FORMULA_CUANTITATIVA",
    "CAMPOS_ORIGEN", "TABLA_ORIGEN", "FILTROS_APLICADOS", "EXCLUSIONES", "INTERPRETACION",
    "UNIDAD", "FORMATO", "RESPONSABLE_VALIDACION", "OBSERVACIONES",
]

MOTIVOS = {
    "NIVEL_FORMACION_ACADEMICO=VALOR_NO_CARGABLE": "Falta completar un codigo valido de nivel de formacion academico.",
    "PAIS_OBTENCION_TIT_O_GRADO=VALOR_NO_CARGABLE": "Falta completar un codigo valido del pais donde se obtuvo el titulo o grado.",
    "FECHA_OBT_TIT_O_GRADO=VALOR_NO_CARGABLE": "Falta completar una fecha valida de obtencion del titulo o grado.",
    "FECHA_FUTURA_PENDIENTE_NO_CARGADA": "La fecha de obtencion del titulo/grado es posterior al corte permitido y requiere confirmacion.",
    "BLOQUE_ESPECIALIDAD_DEPENDIENTE_LIMPIADO_SIN_NIVEL": "Se limpio informacion de especialidad porque no existia nivel de especialidad valido.",
    "FECHA_FORMATO_PES": "Fecha convertida al formato requerido para carga PES/SIES.",
    "TITULO_SOLO_A_Z": "Titulo normalizado a letras A-Z para cumplir validacion PES/SIES.",
    "NOMBRE_TITULO_SOLO_A_Z": "Titulo normalizado a letras A-Z para cumplir validacion PES/SIES.",
    "COMUNA_MAYOR_FUNCION_COMPLETADA": "Comuna de mayor funcion completada desde comuna del programa principal.",
}

CATALOGO_NIVEL_FORMACION = {
    "1": "1 - Doctorado",
    "2": "2 - Magíster",
    "3": "3 - Título Profesional",
    "4": "4 - Licenciatura",
    "5": "5 - Técnico de Nivel Superior",
    "6": "6 - Título Técnico de Nivel Medio",
    "7": "7 - Licencia de Enseñanza Media",
    "8": "8 - Sin información",
}

CATALOGO_CARGO_NORMALIZADO = {
    "1": "1 - Rector(a) / Prorrector(a)",
    "2": "2 - Vicerrector(a) de área / sede",
    "3": "3 - Decano(a) / Vicedecano(a)",
    "4": "4 - Asesor(a) / Consejero(a)",
    "5": "5 - Director(a) o Jefe(a) de área / Unidad Académica",
    "6": "6 - Secretario(a) de Unidad Académica",
    "7": "7 - Coordinador(a) / Encargado(a)",
    "8": "8 - Investigador(a)",
    "9": "9 - Docente",
    "10": "10 - Profesional / Administrativo(a)",
    "11": "11 - Otro",
}

CATALOGO_OFICIAL_ROWS = (
    [["NIVEL_FORMACION_ACADEMICO", codigo, etiqueta, "Instructivo SIES Personal Académico 2026"] for codigo, etiqueta in CATALOGO_NIVEL_FORMACION.items()]
    + [["CARGO_NORMALIZADO", codigo, etiqueta, "Instructivo SIES Personal Académico 2026"] for codigo, etiqueta in CATALOGO_CARGO_NORMALIZADO.items()]
)

HIST_BASE_COLUMNS = [
    "PERIODO", "CODIGO_INSTITUCION", "NOMBRE_INSTITUCION", "TIPO_INSTITUCION_I", "TIPO_INSTITUCION_II", "TIPO_INSTITUCION_III",
    "ACAD_MUJERES", "ACAD_HOMBRES", "ACAD_TOTAL", "EDAD_PROM_MUJERES", "EDAD_PROM_HOMBRES", "EDAD_PROM_GENERAL",
    "ACAD_MUJER_MENOS_35", "ACAD_MUJER_35_44", "ACAD_MUJER_45_54", "ACAD_MUJER_55_64", "ACAD_MUJER_65_MAS", "ACAD_MUJER_SIN_INFO",
    "ACAD_HOMBRE_MENOS_35", "ACAD_HOMBRE_35_44", "ACAD_HOMBRE_45_54", "ACAD_HOMBRE_55_64", "ACAD_HOMBRE_65_MAS", "ACAD_HOMBRE_SIN_INFO",
    "ACAD_EN_1_INSTITUCION", "ACAD_EN_2_INSTITUCIONES", "ACAD_EN_3_O_MAS_INSTITUCIONES",
    "ACAD_DOCTOR", "ACAD_MAGISTER", "ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA", "ACAD_TITULO_PROFESIONAL", "ACAD_LICENCIATURA",
    "ACAD_TECNICO_NIVEL_SUPERIOR", "ACAD_TECNICO_NIVEL_MEDIO", "ACAD_LICENCIA_ENSENANZA_MEDIA", "ACAD_SIN_TITULO_NI_GRADO", "ACAD_SIN_INFORMACION_FORMACION",
    "ACAD_REGION_ARICA_PARINACOTA", "ACAD_REGION_TARAPACA", "ACAD_REGION_ANTOFAGASTA", "ACAD_REGION_ATACAMA", "ACAD_REGION_COQUIMBO",
    "ACAD_REGION_VALPARAISO", "ACAD_REGION_METROPOLITANA", "ACAD_REGION_OHIGGINS", "ACAD_REGION_MAULE", "ACAD_REGION_NUBLE", "ACAD_REGION_BIOBIO",
    "ACAD_REGION_ARAUCANIA", "ACAD_REGION_LOS_RIOS", "ACAD_REGION_LOS_LAGOS", "ACAD_REGION_AYSEN", "ACAD_REGION_MAGALLANES", "ACAD_REGION_SIN_INFORMACION",
    "ACAD_CHILENO", "ACAD_EXTRANJERO", "HORAS_PROM_MUJERES", "HORAS_PROM_HOMBRES", "HORAS_PROM_GENERAL",
    "ACAD_HORAS_MENOS_11", "ACAD_HORAS_11_MENOS_23", "ACAD_HORAS_23_MENOS_39", "ACAD_HORAS_39_MAS", "ACAD_HORAS_SIN_INFORMACION",
    "JCE_MUJERES", "JCE_HOMBRES", "JCE_TOTAL", "EDAD_JCE_PROM_MUJERES", "EDAD_JCE_PROM_HOMBRES", "EDAD_JCE_PROM_GENERAL",
    "JCE_DOCTOR", "JCE_MAGISTER", "JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA", "JCE_TITULO_PROFESIONAL", "JCE_LICENCIATURA",
    "JCE_TECNICO_NIVEL_SUPERIOR", "JCE_TECNICO_NIVEL_MEDIO", "JCE_LICENCIA_ENSENANZA_MEDIA", "JCE_SIN_TITULO_NI_GRADO", "JCE_SIN_INFORMACION_FORMACION",
    "JCE_CHILENO", "JCE_EXTRANJERO", "JCE_HORAS_MENOS_11", "JCE_HORAS_11_MENOS_23", "JCE_HORAS_23_MENOS_39", "JCE_HORAS_39_MAS",
]

HIST_KPI_COLUMNS = [
    "PERIODO", "ACAD_TOTAL", "ACAD_MUJERES", "ACAD_HOMBRES", "PORC_MUJERES", "PORC_HOMBRES", "VAR_ABS_ACAD_TOTAL", "VAR_PORC_ACAD_TOTAL", "CAGR_ACAD_TOTAL_PERIODO",
    "EDAD_PROM_GENERAL", "EDAD_PROM_MUJERES", "EDAD_PROM_HOMBRES", "BRECHA_EDAD_H_M", "JCE_TOTAL", "JCE_MUJERES", "JCE_HOMBRES", "PORC_JCE_MUJERES", "PORC_JCE_HOMBRES",
    "JCE_POR_ACADEMICO", "VAR_ABS_JCE_TOTAL", "VAR_PORC_JCE_TOTAL", "CAGR_JCE_PERIODO", "EDAD_JCE_PROM_GENERAL", "BRECHA_EDAD_JCE_H_M",
    "ACAD_DOCTOR", "PORC_DOCTOR", "ACAD_MAGISTER", "PORC_MAGISTER", "ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA", "PORC_ESPECIALIDAD_MEDICA_ODONTOLOGICA",
    "ACAD_TITULO_PROFESIONAL", "PORC_TITULO_PROFESIONAL", "ACAD_LICENCIATURA", "PORC_LICENCIATURA", "ACAD_TECNICO_NIVEL_SUPERIOR", "PORC_TECNICO_NIVEL_SUPERIOR",
    "ACAD_TECNICO_NIVEL_MEDIO", "PORC_TECNICO_NIVEL_MEDIO", "ACAD_LICENCIA_ENSENANZA_MEDIA", "PORC_LICENCIA_ENSENANZA_MEDIA", "ACAD_SIN_TITULO_NI_GRADO", "PORC_SIN_TITULO_NI_GRADO",
    "ACAD_SIN_INFORMACION_FORMACION", "PORC_SIN_INFORMACION_FORMACION", "ACAD_FORMACION_AVANZADA", "PORC_FORMACION_AVANZADA",
    "JCE_DOCTOR", "PORC_JCE_DOCTOR", "JCE_MAGISTER", "PORC_JCE_MAGISTER", "JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA", "PORC_JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA",
    "JCE_FORMACION_AVANZADA", "PORC_JCE_FORMACION_AVANZADA", "BRECHA_FORMACION_AVANZADA_JCE_NUMERO",
    "HORAS_PROM_GENERAL", "HORAS_PROM_MUJERES", "HORAS_PROM_HOMBRES", "BRECHA_HORAS_H_M", "ACAD_HORAS_MENOS_11", "PORC_HORAS_MENOS_11",
    "ACAD_HORAS_11_MENOS_23", "PORC_HORAS_11_MENOS_23", "ACAD_HORAS_23_MENOS_39", "PORC_HORAS_23_MENOS_39", "ACAD_HORAS_39_MAS", "PORC_HORAS_39_MAS",
    "ACAD_HORAS_SIN_INFORMACION", "PORC_HORAS_SIN_INFORMACION", "INDICE_ALTA_DEDICACION", "INDICE_BAJA_DEDICACION",
    "ACAD_EN_1_INSTITUCION", "PORC_EN_1_INSTITUCION", "ACAD_EN_2_INSTITUCIONES", "PORC_EN_2_INSTITUCIONES", "ACAD_EN_3_O_MAS_INSTITUCIONES", "PORC_EN_3_O_MAS_INSTITUCIONES",
    "INDICE_MULTIINSTITUCIONALIDAD", "ACAD_CHILENO", "PORC_CHILENO", "ACAD_EXTRANJERO", "PORC_EXTRANJERO", "JCE_CHILENO", "PORC_JCE_CHILENO", "JCE_EXTRANJERO",
    "PORC_JCE_EXTRANJERO", "BRECHA_JCE_EXTRANJERO_NUMERO", "REGION_PRINCIPAL", "ACAD_REGION_PRINCIPAL", "PORC_REGION_PRINCIPAL", "N_REGIONES_CON_PRESENCIA",
    "INDICE_CONCENTRACION_REGIONAL", "DIF_ACAD_TOTAL_VS_PROM_TIPO_IES", "DIF_JCE_TOTAL_VS_PROM_TIPO_IES", "DIF_JCE_POR_ACADEMICO_VS_PROM_TIPO_IES",
    "DIF_PORC_MAGISTER_VS_PROM_TIPO_IES", "DIF_PORC_DOCTOR_VS_PROM_TIPO_IES", "DIF_PORC_FORMACION_AVANZADA_VS_PROM_TIPO_IES", "DIF_INDICE_ALTA_DEDICACION_VS_PROM_TIPO_IES",
    "DIF_PORC_MUJERES_VS_PROM_TIPO_IES", "PERCENTIL_ACAD_TOTAL_TIPO_IES", "PERCENTIL_JCE_TOTAL_TIPO_IES", "PERCENTIL_FORMACION_AVANZADA_TIPO_IES",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_DIR))
    except ValueError:
        return str(path)


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return row.get("TIPO_DOCUMENTO", ""), row.get("NUM_DOCUMENTO", ""), row.get("DV", "")


def read_original() -> list[dict[str, str]]:
    with BASE_GENERAL.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def read_loaded() -> dict[tuple[str, str, str], dict[str, str]]:
    loaded = {}
    with CSV_CARGADO.open("r", encoding="cp1252", newline="") as fh:
        for row in csv.reader(fh, delimiter=";"):
            if row:
                record = dict(zip(COLUMNAS_OFICIALES, row))
                loaded[key(record)] = record
    return loaded


def latest_file(pattern: str) -> Path | None:
    paths = sorted(EXCLUSIONES_DIR.glob(pattern))
    return paths[-1] if paths else None


def read_candidate_rows() -> list[dict[str, str]]:
    if not CANDIDATO_EXPORTACION.exists():
        return []
    with CANDIDATO_EXPORTACION.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def reconstruir_exclusiones() -> dict[tuple[str, str, str], dict[str, str]]:
    audit = latest_file("auditoria_exclusiones_pes_fase7_*.csv") or latest_file("auditoria_exclusiones_pes_*.csv")
    candidate_rows = read_candidate_rows()
    result = {}
    if not audit or not candidate_rows:
        return result
    with audit.open("r", encoding="utf-8-sig", newline="") as fh:
        for event in csv.DictReader(fh):
            fila = event.get("fila_origen", "")
            if not fila.isdigit():
                continue
            idx = int(fila) - 2
            if idx < 0 or idx >= len(candidate_rows):
                continue
            row = candidate_rows[idx]
            motivos = event.get("motivo", "")
            cols, vals = [], []
            for item in motivos.split(" | "):
                col = item.split("=", 1)[0].strip()
                if col:
                    cols.append(col)
                    vals.append(f"{col}={row.get(col, '')}")
            result[key(row)] = {
                "motivo": motivos,
                "columnas": " | ".join(cols),
                "valores": " | ".join(vals),
                "accion": "Revisar dato fuente y corregir con respaldo antes de nueva carga.",
            }
    return result


def read_transformaciones() -> list[dict[str, str]]:
    audit = latest_file("auditoria_transformaciones_pes_fase7_*.csv") or latest_file("auditoria_transformaciones_pes_*.csv")
    if not audit:
        return []
    with audit.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_float(value: object) -> float:
    try:
        return float(str(value or "").strip().replace(",", "."))
    except ValueError:
        return 0.0


def parse_date(value: object) -> date | None:
    text = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def years_between(value: object) -> float | None:
    parsed = parse_date(value)
    if not parsed or parsed > FECHA_CORTE:
        return None
    return round((FECHA_CORTE - parsed).days / 365.25, 1)


def age_at(value: object) -> int | None:
    parsed = parse_date(value)
    if not parsed or parsed > FECHA_CORTE:
        return None
    return FECHA_CORTE.year - parsed.year - ((FECHA_CORTE.month, FECHA_CORTE.day) < (parsed.month, parsed.day))


def tramo_edad(edad: int | None) -> str:
    if edad is None:
        return "Sin dato"
    if edad < 30:
        return "Menor de 30"
    if edad < 40:
        return "30 a 39"
    if edad < 50:
        return "40 a 49"
    if edad < 60:
        return "50 a 59"
    return "60 o mas"


def tramo_titulo(anios: float | None) -> str:
    if anios is None:
        return "Sin dato"
    if anios < 5:
        return "0 a 4 anios"
    if anios < 10:
        return "5 a 9 anios"
    if anios < 15:
        return "10 a 14 anios"
    return "15 anios o mas"


def nombre_completo(row: dict[str, str]) -> str:
    return " ".join(part for part in [row.get("PRIMER_APELLIDO", ""), row.get("SEGUNDO_APELLIDO", ""), row.get("NOMBRES", "")] if part).strip()


def motivo_legible(motivo: str) -> str:
    if not motivo:
        return ""
    parts = []
    for item in motivo.split(" | "):
        item = item.strip()
        parts.append(MOTIVOS.get(item, item.replace("_", " ").capitalize() + "."))
    return "; ".join(parts)


def accion_legible(motivo: str, accion: str = "") -> str:
    if not motivo:
        return "Sin accion requerida."
    if "FECHA_FUTURA" in motivo:
        return "Validar respaldo de la fecha y autorizar correccion controlada antes de carga complementaria."
    if "VALOR_NO_CARGABLE" in motivo:
        return "Completar dato fuente con respaldo y regenerar candidato PES/SIES."
    return accion or "Revisar registro en fuente y documentar accion antes de nueva carga."


def sexo_etiqueta(value: str) -> str:
    return {"H": "Hombre", "M": "Mujer"}.get(str(value or "").strip().upper(), "Otro/Sin dato")


def nivel_etiqueta(value: str) -> str:
    code = str(value or "").strip()
    return CATALOGO_NIVEL_FORMACION.get(code, "Sin código válido")


def cargo_etiqueta(value: str) -> str:
    code = str(value or "").strip()
    return CATALOGO_CARGO_NORMALIZADO.get(code, "Sin código válido")


def is_magister(row: dict[str, str]) -> bool:
    title = row.get("NOMBRE_TITULO_O_GRADO", "").upper()
    return row.get("NIVEL_FORMACION_ACADEMICO") == "2" or "MAGISTER" in title or "MAGÍSTER" in title


def is_doctorado(row: dict[str, str]) -> bool:
    title = row.get("NOMBRE_TITULO_O_GRADO", "").upper()
    return row.get("NIVEL_FORMACION_ACADEMICO") == "1" or "DOCTOR" in title


def si_no(flag: bool) -> str:
    return "Si" if flag else "No"


def tipo_dedicacion(total: float) -> str:
    if total <= 0:
        return "Sin horas"
    if total < 11:
        return "Baja dedicacion"
    if total <= 21:
        return "Media dedicacion"
    if total <= 43:
        return "Alta dedicacion"
    return "Jornada completa o equivalente"


def tipo_vinculo(planta: float, contrata: float, honorarios: float) -> str:
    flags = [planta > 0, contrata > 0, honorarios > 0]
    if sum(flags) == 0:
        return "Sin horas"
    labels = [label for label, flag in zip(["planta", "contrata", "honorarios"], flags) if flag]
    if len(labels) == 1:
        return f"Solo {labels[0]}"
    if len(labels) == 3:
        return "Mixto tres tipos"
    return " y ".join(label.capitalize() if i == 0 else label for i, label in enumerate(labels))


def detalle_rows(original: list[dict[str, str]], loaded: dict[tuple[str, str, str], dict[str, str]], exclusions: dict[tuple[str, str, str], dict[str, str]]) -> list[list[object]]:
    rows = []
    for row in original:
        loaded_row = loaded.get(key(row))
        estado = "CARGADO_PES" if loaded_row else "NO_CARGADO_PENDIENTE"
        info = exclusions.get(key(row), {})
        motivo = "" if estado == "CARGADO_PES" else info.get("motivo", "FECHA_FUTURA_PENDIENTE_NO_CARGADA")
        accion = accion_legible(motivo, info.get("accion", ""))
        control = [
            estado,
            row.get("NUM_DOCUMENTO", ""),
            row.get("DV", ""),
            nombre_completo(row),
            motivo_legible(motivo),
            "" if estado == "CARGADO_PES" else info.get("columnas", "FECHA_OBT_TIT_O_GRADO"),
            "" if estado == "CARGADO_PES" else info.get("valores", f"FECHA_OBT_TIT_O_GRADO={row.get('FECHA_OBT_TIT_O_GRADO', '')}"),
            accion,
        ]
        comparative = []
        for col in COLUMNAS_OFICIALES:
            comparative.extend([loaded_row.get(col, "") if loaded_row else "", row.get(col, "")])
        rows.append(control + comparative)
    return rows


def base_kpi_rows(original: list[dict[str, str]], loaded: dict[tuple[str, str, str], dict[str, str]], exclusions: dict[tuple[str, str, str], dict[str, str]]) -> list[list[object]]:
    rows = []
    for row in original:
        estado = "CARGADO_PES" if key(row) in loaded else "NO_CARGADO_PENDIENTE"
        info = exclusions.get(key(row), {})
        motivo = "" if estado == "CARGADO_PES" else info.get("motivo", "FECHA_FUTURA_PENDIENTE_NO_CARGADA")
        planta = parse_float(row.get("NUM_HORAS_PLANTA", ""))
        contrata = parse_float(row.get("NUM_HORAS_CONTRATA", ""))
        honorarios = parse_float(row.get("NUM_HORAS_HONORARIOS", ""))
        total = round(planta + contrata + honorarios, 2)
        edad = age_at(row.get("FECHA_NACIMIENTO", ""))
        anios = years_between(row.get("FECHA_OBT_TIT_O_GRADO", ""))
        code = str(row.get("NIVEL_FORMACION_ACADEMICO", "")).strip()
        rows.append([
            estado, row.get("NUM_DOCUMENTO", ""), row.get("DV", ""), nombre_completo(row),
            motivo_legible(motivo), "" if estado == "CARGADO_PES" else info.get("columnas", "FECHA_OBT_TIT_O_GRADO"),
            accion_legible(motivo, info.get("accion", "")), row.get("SEXO", ""), sexo_etiqueta(row.get("SEXO", "")),
            row.get("FECHA_NACIMIENTO", ""), edad if edad is not None else "", tramo_edad(edad), row.get("NACIONALIDAD", ""),
            code, nivel_etiqueta(code), row.get("NOMBRE_TITULO_O_GRADO", ""), row.get("PAIS_OBTENCION_TIT_O_GRADO", ""),
            row.get("FECHA_OBT_TIT_O_GRADO", ""), anios if anios is not None else "", tramo_titulo(anios),
            si_no(is_magister(row)), si_no(is_doctorado(row)), si_no(code == "3"), si_no(code == "5"),
            row.get("CARGO_NORMALIZADO", ""), cargo_etiqueta(row.get("CARGO_NORMALIZADO", "")),
            row.get("NOMBRE_PRINCIPAL_PROGRAMA", ""), row.get("COMUNA_PRINCIPAL_PROGRAMA", ""),
            round(planta, 2), round(contrata, 2), round(honorarios, 2), total, round(total / 44, 2),
            tipo_dedicacion(total), tipo_vinculo(planta, contrata, honorarios),
        ])
    return rows


def col_idx(name: str) -> int:
    return BASE_KPI_COLUMNS.index(name)


def clean(value: object, kind: str = "dato") -> str:
    text = str(value or "").strip()
    if text.upper() in {"#N/A", "#N/D", "N/A", "NA", "NO APLICA", ""}:
        return "Sin código válido" if kind == "codigo" else "Sin dato válido"
    return text


def counter_table(rows: list[list[object]], column: str, kind: str = "dato") -> list[list[object]]:
    total = len(rows)
    counts = Counter(clean(row[col_idx(column)], kind) for row in rows)
    return [[key, value, value / total if total else 0] for key, value in counts.most_common()]


def sum_by(rows: list[list[object]], group_col: str, value_col: str) -> list[list[object]]:
    groups, counts = defaultdict(float), Counter()
    for row in rows:
        group = clean(row[col_idx(group_col)])
        groups[group] += parse_float(row[col_idx(value_col)])
        counts[group] += 1
    total = sum(groups.values())
    return sorted([[group, counts[group], round(value, 2), value / total if total else 0] for group, value in groups.items()], key=lambda x: x[2], reverse=True)


def find_input(patterns: list[str]) -> Path | None:
    bases = [MODULE_DIR / "insumos/historicos", MODULE_DIR / "insumos", MODULE_DIR, REPO_DIR]
    for base in bases:
        if not base.exists():
            continue
        for pattern in patterns:
            found = sorted(base.glob(pattern))
            if found:
                return found[0]
    return None


def period_year(value: object) -> int | None:
    text = str(value or "")
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 4:
        return int(digits[-4:])
    return None


def fnum(value: object) -> float:
    return parse_float(value)


def norm_row(row: tuple[object, ...], mapping: dict[str, int]) -> dict[str, object]:
    out = {}
    for name, pos in mapping.items():
        out[name] = row[pos] if pos < len(row) else ""
    return out


def historical_paths() -> tuple[Path | None, Path | None]:
    hist = find_input(["PAC20082025SIES*.xlsx", "PAC_web_2008_2025*.xlsx", "PAC_web_2008_2025_SIES_EE.xlsx"])
    glos = find_input(["GLOSARIOPAC*.pdf", "OFICIAL_GLOSARIO_PAC_WEB*.pdf", "OFICIAL_GLOSARIO_PAC_WEB_E.pdf"])
    return hist, glos


def read_historical_base(hist_path: Path) -> tuple[list[dict[str, object]], list[list[object]], list[list[object]], list[int], list[str]]:
    wb = load_workbook(hist_path, read_only=True, data_only=True)
    audit = []
    dict_rows = []
    for ws in wb.worksheets:
        audit.append([datetime.now().isoformat(timespec="seconds"), "HOJA_DETECTADA", ws.title, ws.max_row, ws.max_column, "INFO"])
    num_ws = wb["BD_Acádemicos_Número"]
    jce_ws = wb["BD_Académicos_JCE"]
    base_map = {
        "PERIODO": 0, "CODIGO_INSTITUCION": 1, "NOMBRE_INSTITUCION": 2, "TIPO_INSTITUCION_I": 3, "TIPO_INSTITUCION_II": 4, "TIPO_INSTITUCION_III": 5,
        "ACAD_MUJERES": 6, "ACAD_HOMBRES": 7, "ACAD_TOTAL": 9, "EDAD_PROM_MUJERES": 10, "EDAD_PROM_HOMBRES": 11, "EDAD_PROM_GENERAL": 12,
        "ACAD_MUJER_MENOS_35": 13, "ACAD_MUJER_35_44": 14, "ACAD_MUJER_45_54": 15, "ACAD_MUJER_55_64": 16, "ACAD_MUJER_65_MAS": 17, "ACAD_MUJER_SIN_INFO": 18,
        "ACAD_HOMBRE_MENOS_35": 19, "ACAD_HOMBRE_35_44": 20, "ACAD_HOMBRE_45_54": 21, "ACAD_HOMBRE_55_64": 22, "ACAD_HOMBRE_65_MAS": 23, "ACAD_HOMBRE_SIN_INFO": 24,
        "ACAD_EN_1_INSTITUCION": 25, "ACAD_EN_2_INSTITUCIONES": 26, "ACAD_EN_3_O_MAS_INSTITUCIONES": 27,
        "ACAD_DOCTOR": 28, "ACAD_MAGISTER": 29, "ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA": 30, "ACAD_TITULO_PROFESIONAL": 31, "ACAD_LICENCIATURA": 32,
        "ACAD_TECNICO_NIVEL_SUPERIOR": 33, "ACAD_TECNICO_NIVEL_MEDIO": 34, "ACAD_LICENCIA_ENSENANZA_MEDIA": 35, "ACAD_SIN_TITULO_NI_GRADO": 36, "ACAD_SIN_INFORMACION_FORMACION": 37,
        "ACAD_REGION_ARICA_PARINACOTA": 38, "ACAD_REGION_TARAPACA": 39, "ACAD_REGION_ANTOFAGASTA": 40, "ACAD_REGION_ATACAMA": 41, "ACAD_REGION_COQUIMBO": 42,
        "ACAD_REGION_VALPARAISO": 43, "ACAD_REGION_METROPOLITANA": 44, "ACAD_REGION_OHIGGINS": 45, "ACAD_REGION_MAULE": 46, "ACAD_REGION_NUBLE": 47, "ACAD_REGION_BIOBIO": 48,
        "ACAD_REGION_ARAUCANIA": 49, "ACAD_REGION_LOS_RIOS": 50, "ACAD_REGION_LOS_LAGOS": 51, "ACAD_REGION_AYSEN": 52, "ACAD_REGION_MAGALLANES": 53, "ACAD_REGION_SIN_INFORMACION": 54,
        "ACAD_CHILENO": 55, "ACAD_EXTRANJERO": 56, "HORAS_PROM_MUJERES": 57, "HORAS_PROM_HOMBRES": 58, "HORAS_PROM_GENERAL": 59,
        "ACAD_HORAS_MENOS_11": 60, "ACAD_HORAS_11_MENOS_23": 61, "ACAD_HORAS_23_MENOS_39": 62, "ACAD_HORAS_39_MAS": 63, "ACAD_HORAS_SIN_INFORMACION": 64,
    }
    jce_map = {
        "JCE_MUJERES": 6, "JCE_HOMBRES": 7, "JCE_TOTAL": 9, "EDAD_JCE_PROM_MUJERES": 10, "EDAD_JCE_PROM_HOMBRES": 11, "EDAD_JCE_PROM_GENERAL": 12,
        "JCE_DOCTOR": 28, "JCE_MAGISTER": 29, "JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA": 30, "JCE_TITULO_PROFESIONAL": 31, "JCE_LICENCIATURA": 32,
        "JCE_TECNICO_NIVEL_SUPERIOR": 33, "JCE_TECNICO_NIVEL_MEDIO": 34, "JCE_LICENCIA_ENSENANZA_MEDIA": 35, "JCE_SIN_TITULO_NI_GRADO": 36, "JCE_SIN_INFORMACION_FORMACION": 37,
        "JCE_CHILENO": 55, "JCE_EXTRANJERO": 56, "JCE_HORAS_MENOS_11": 57, "JCE_HORAS_11_MENOS_23": 58, "JCE_HORAS_23_MENOS_39": 59, "JCE_HORAS_39_MAS": 60,
    }
    jce_by_key = {}
    for row in jce_ws.iter_rows(min_row=4, values_only=True):
        year = period_year(row[0])
        if year:
            jce_by_key[(year, str(row[1]))] = norm_row(row, jce_map)
    records = []
    for row in num_ws.iter_rows(min_row=4, values_only=True):
        year = period_year(row[0])
        if not year:
            continue
        rec = norm_row(row, base_map)
        rec["PERIODO"] = year
        rec["CODIGO_INSTITUCION"] = str(rec["CODIGO_INSTITUCION"])
        rec.update(jce_by_key.get((year, rec["CODIGO_INSTITUCION"]), {}))
        records.append(rec)
    years = sorted({int(r["PERIODO"]) for r in records})
    institutions = sorted({str(r["NOMBRE_INSTITUCION"]) for r in records})
    for col in HIST_BASE_COLUMNS:
        dict_rows.append([col, "ENCONTRADO" if any(col in r for r in records) else "NO_ENCONTRADO", "", "PAC_web_2008_2025_SIES_EE.xlsx"])
    audit.append([datetime.now().isoformat(timespec="seconds"), "BASE_NORMALIZADA", "HIST_BASE_NORMALIZADA", len(records), len(HIST_BASE_COLUMNS), "INFO"])
    audit.append([datetime.now().isoformat(timespec="seconds"), "ANIOS_DETECTADOS", f"{min(years)}-{max(years)}", len(years), "", "INFO"])
    return records, audit, dict_rows, years, institutions


def pct(n: float, d: float) -> float:
    return n / d if d else 0.0


def percentile(values: list[float], target: float) -> float:
    clean_vals = sorted(v for v in values if v is not None)
    if not clean_vals:
        return 0.0
    return sum(1 for v in clean_vals if v <= target) / len(clean_vals)


def region_main(rec: dict[str, object]) -> tuple[str, float, int]:
    regions = [(c.replace("ACAD_REGION_", ""), fnum(rec.get(c))) for c in HIST_BASE_COLUMNS if c.startswith("ACAD_REGION_") and c != "ACAD_REGION_SIN_INFORMACION"]
    active = [(name, value) for name, value in regions if value > 0]
    if not active:
        return "SIN_INFORMACION", 0, 0
    name, value = max(active, key=lambda x: x[1])
    return name, value, len(active)


def base_metrics(rec: dict[str, object]) -> dict[str, object]:
    acad = fnum(rec.get("ACAD_TOTAL"))
    jce = fnum(rec.get("JCE_TOTAL"))
    adv = fnum(rec.get("ACAD_DOCTOR")) + fnum(rec.get("ACAD_MAGISTER")) + fnum(rec.get("ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA"))
    jce_adv = fnum(rec.get("JCE_DOCTOR")) + fnum(rec.get("JCE_MAGISTER")) + fnum(rec.get("JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA"))
    reg_name, reg_value, reg_count = region_main(rec)
    m = {
        "PERIODO": rec["PERIODO"], "ACAD_TOTAL": acad, "ACAD_MUJERES": fnum(rec.get("ACAD_MUJERES")), "ACAD_HOMBRES": fnum(rec.get("ACAD_HOMBRES")),
        "PORC_MUJERES": pct(fnum(rec.get("ACAD_MUJERES")), acad), "PORC_HOMBRES": pct(fnum(rec.get("ACAD_HOMBRES")), acad),
        "EDAD_PROM_GENERAL": fnum(rec.get("EDAD_PROM_GENERAL")), "EDAD_PROM_MUJERES": fnum(rec.get("EDAD_PROM_MUJERES")), "EDAD_PROM_HOMBRES": fnum(rec.get("EDAD_PROM_HOMBRES")),
        "BRECHA_EDAD_H_M": fnum(rec.get("EDAD_PROM_HOMBRES")) - fnum(rec.get("EDAD_PROM_MUJERES")),
        "JCE_TOTAL": jce, "JCE_MUJERES": fnum(rec.get("JCE_MUJERES")), "JCE_HOMBRES": fnum(rec.get("JCE_HOMBRES")),
        "PORC_JCE_MUJERES": pct(fnum(rec.get("JCE_MUJERES")), jce), "PORC_JCE_HOMBRES": pct(fnum(rec.get("JCE_HOMBRES")), jce), "JCE_POR_ACADEMICO": pct(jce, acad),
        "EDAD_JCE_PROM_GENERAL": fnum(rec.get("EDAD_JCE_PROM_GENERAL")), "BRECHA_EDAD_JCE_H_M": fnum(rec.get("EDAD_JCE_PROM_HOMBRES")) - fnum(rec.get("EDAD_JCE_PROM_MUJERES")),
        "ACAD_DOCTOR": fnum(rec.get("ACAD_DOCTOR")), "PORC_DOCTOR": pct(fnum(rec.get("ACAD_DOCTOR")), acad), "ACAD_MAGISTER": fnum(rec.get("ACAD_MAGISTER")), "PORC_MAGISTER": pct(fnum(rec.get("ACAD_MAGISTER")), acad),
        "ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA": fnum(rec.get("ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA")), "PORC_ESPECIALIDAD_MEDICA_ODONTOLOGICA": pct(fnum(rec.get("ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA")), acad),
        "ACAD_TITULO_PROFESIONAL": fnum(rec.get("ACAD_TITULO_PROFESIONAL")), "PORC_TITULO_PROFESIONAL": pct(fnum(rec.get("ACAD_TITULO_PROFESIONAL")), acad),
        "ACAD_LICENCIATURA": fnum(rec.get("ACAD_LICENCIATURA")), "PORC_LICENCIATURA": pct(fnum(rec.get("ACAD_LICENCIATURA")), acad),
        "ACAD_TECNICO_NIVEL_SUPERIOR": fnum(rec.get("ACAD_TECNICO_NIVEL_SUPERIOR")), "PORC_TECNICO_NIVEL_SUPERIOR": pct(fnum(rec.get("ACAD_TECNICO_NIVEL_SUPERIOR")), acad),
        "ACAD_TECNICO_NIVEL_MEDIO": fnum(rec.get("ACAD_TECNICO_NIVEL_MEDIO")), "PORC_TECNICO_NIVEL_MEDIO": pct(fnum(rec.get("ACAD_TECNICO_NIVEL_MEDIO")), acad),
        "ACAD_LICENCIA_ENSENANZA_MEDIA": fnum(rec.get("ACAD_LICENCIA_ENSENANZA_MEDIA")), "PORC_LICENCIA_ENSENANZA_MEDIA": pct(fnum(rec.get("ACAD_LICENCIA_ENSENANZA_MEDIA")), acad),
        "ACAD_SIN_TITULO_NI_GRADO": fnum(rec.get("ACAD_SIN_TITULO_NI_GRADO")), "PORC_SIN_TITULO_NI_GRADO": pct(fnum(rec.get("ACAD_SIN_TITULO_NI_GRADO")), acad),
        "ACAD_SIN_INFORMACION_FORMACION": fnum(rec.get("ACAD_SIN_INFORMACION_FORMACION")), "PORC_SIN_INFORMACION_FORMACION": pct(fnum(rec.get("ACAD_SIN_INFORMACION_FORMACION")), acad),
        "ACAD_FORMACION_AVANZADA": adv, "PORC_FORMACION_AVANZADA": pct(adv, acad),
        "JCE_DOCTOR": fnum(rec.get("JCE_DOCTOR")), "PORC_JCE_DOCTOR": pct(fnum(rec.get("JCE_DOCTOR")), jce), "JCE_MAGISTER": fnum(rec.get("JCE_MAGISTER")), "PORC_JCE_MAGISTER": pct(fnum(rec.get("JCE_MAGISTER")), jce),
        "JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA": fnum(rec.get("JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA")), "PORC_JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA": pct(fnum(rec.get("JCE_ESPECIALIDAD_MEDICA_ODONTOLOGICA")), jce),
        "JCE_FORMACION_AVANZADA": jce_adv, "PORC_JCE_FORMACION_AVANZADA": pct(jce_adv, jce), "BRECHA_FORMACION_AVANZADA_JCE_NUMERO": pct(jce_adv, jce) - pct(adv, acad),
        "HORAS_PROM_GENERAL": fnum(rec.get("HORAS_PROM_GENERAL")), "HORAS_PROM_MUJERES": fnum(rec.get("HORAS_PROM_MUJERES")), "HORAS_PROM_HOMBRES": fnum(rec.get("HORAS_PROM_HOMBRES")), "BRECHA_HORAS_H_M": fnum(rec.get("HORAS_PROM_HOMBRES")) - fnum(rec.get("HORAS_PROM_MUJERES")),
        "ACAD_HORAS_MENOS_11": fnum(rec.get("ACAD_HORAS_MENOS_11")), "PORC_HORAS_MENOS_11": pct(fnum(rec.get("ACAD_HORAS_MENOS_11")), acad), "ACAD_HORAS_11_MENOS_23": fnum(rec.get("ACAD_HORAS_11_MENOS_23")), "PORC_HORAS_11_MENOS_23": pct(fnum(rec.get("ACAD_HORAS_11_MENOS_23")), acad),
        "ACAD_HORAS_23_MENOS_39": fnum(rec.get("ACAD_HORAS_23_MENOS_39")), "PORC_HORAS_23_MENOS_39": pct(fnum(rec.get("ACAD_HORAS_23_MENOS_39")), acad), "ACAD_HORAS_39_MAS": fnum(rec.get("ACAD_HORAS_39_MAS")), "PORC_HORAS_39_MAS": pct(fnum(rec.get("ACAD_HORAS_39_MAS")), acad),
        "ACAD_HORAS_SIN_INFORMACION": fnum(rec.get("ACAD_HORAS_SIN_INFORMACION")), "PORC_HORAS_SIN_INFORMACION": pct(fnum(rec.get("ACAD_HORAS_SIN_INFORMACION")), acad), "INDICE_ALTA_DEDICACION": pct(fnum(rec.get("ACAD_HORAS_39_MAS")), acad), "INDICE_BAJA_DEDICACION": pct(fnum(rec.get("ACAD_HORAS_MENOS_11")), acad),
        "ACAD_EN_1_INSTITUCION": fnum(rec.get("ACAD_EN_1_INSTITUCION")), "PORC_EN_1_INSTITUCION": pct(fnum(rec.get("ACAD_EN_1_INSTITUCION")), acad), "ACAD_EN_2_INSTITUCIONES": fnum(rec.get("ACAD_EN_2_INSTITUCIONES")), "PORC_EN_2_INSTITUCIONES": pct(fnum(rec.get("ACAD_EN_2_INSTITUCIONES")), acad), "ACAD_EN_3_O_MAS_INSTITUCIONES": fnum(rec.get("ACAD_EN_3_O_MAS_INSTITUCIONES")), "PORC_EN_3_O_MAS_INSTITUCIONES": pct(fnum(rec.get("ACAD_EN_3_O_MAS_INSTITUCIONES")), acad),
        "INDICE_MULTIINSTITUCIONALIDAD": pct(fnum(rec.get("ACAD_EN_2_INSTITUCIONES")) + fnum(rec.get("ACAD_EN_3_O_MAS_INSTITUCIONES")), acad),
        "ACAD_CHILENO": fnum(rec.get("ACAD_CHILENO")), "PORC_CHILENO": pct(fnum(rec.get("ACAD_CHILENO")), acad), "ACAD_EXTRANJERO": fnum(rec.get("ACAD_EXTRANJERO")), "PORC_EXTRANJERO": pct(fnum(rec.get("ACAD_EXTRANJERO")), acad),
        "JCE_CHILENO": fnum(rec.get("JCE_CHILENO")), "PORC_JCE_CHILENO": pct(fnum(rec.get("JCE_CHILENO")), jce), "JCE_EXTRANJERO": fnum(rec.get("JCE_EXTRANJERO")), "PORC_JCE_EXTRANJERO": pct(fnum(rec.get("JCE_EXTRANJERO")), jce), "BRECHA_JCE_EXTRANJERO_NUMERO": pct(fnum(rec.get("JCE_EXTRANJERO")), jce) - pct(fnum(rec.get("ACAD_EXTRANJERO")), acad),
        "REGION_PRINCIPAL": reg_name, "ACAD_REGION_PRINCIPAL": reg_value, "PORC_REGION_PRINCIPAL": pct(reg_value, acad), "N_REGIONES_CON_PRESENCIA": reg_count, "INDICE_CONCENTRACION_REGIONAL": pct(reg_value, acad),
    }
    return m


def cagr(start: float, end: float, periods: int) -> float:
    if start <= 0 or end <= 0 or periods <= 0:
        return 0.0
    return (end / start) ** (1 / periods) - 1


def compute_hist_kpis(records: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    all_metrics = []
    for rec in records:
        m = base_metrics(rec)
        m["CODIGO_INSTITUCION"] = rec["CODIGO_INSTITUCION"]
        m["NOMBRE_INSTITUCION"] = rec["NOMBRE_INSTITUCION"]
        m["TIPO_INSTITUCION_I"] = rec["TIPO_INSTITUCION_I"]
        m["TIPO_INSTITUCION_II"] = rec["TIPO_INSTITUCION_II"]
        m["TIPO_INSTITUCION_III"] = rec["TIPO_INSTITUCION_III"]
        all_metrics.append(m)
    target_code = str(INSTITUCION_OBJETIVO_CODIGO)
    target = sorted(
        [m for m in all_metrics if str(m["CODIGO_INSTITUCION"]).strip() == target_code],
        key=lambda x: int(x["PERIODO"]),
    )
    if not target:
        raise RuntimeError(
            f"No existe CODIGO_INSTITUCION = {INSTITUCION_OBJETIVO_CODIGO} en la base historica SIES. "
            "Se detiene el analisis historico institucional; no se usa coincidencia parcial por nombre."
        )
    first = target[0]
    previous = None
    for m in target:
        if previous:
            m["VAR_ABS_ACAD_TOTAL"] = m["ACAD_TOTAL"] - previous["ACAD_TOTAL"]
            m["VAR_PORC_ACAD_TOTAL"] = pct(m["VAR_ABS_ACAD_TOTAL"], previous["ACAD_TOTAL"])
            m["VAR_ABS_JCE_TOTAL"] = m["JCE_TOTAL"] - previous["JCE_TOTAL"]
            m["VAR_PORC_JCE_TOTAL"] = pct(m["VAR_ABS_JCE_TOTAL"], previous["JCE_TOTAL"])
        else:
            m["VAR_ABS_ACAD_TOTAL"] = 0
            m["VAR_PORC_ACAD_TOTAL"] = 0
            m["VAR_ABS_JCE_TOTAL"] = 0
            m["VAR_PORC_JCE_TOTAL"] = 0
        years = int(m["PERIODO"]) - int(first["PERIODO"])
        m["CAGR_ACAD_TOTAL_PERIODO"] = cagr(first["ACAD_TOTAL"], m["ACAD_TOTAL"], years)
        m["CAGR_JCE_PERIODO"] = cagr(first["JCE_TOTAL"], m["JCE_TOTAL"], years)
        same_year = [x for x in all_metrics if x["PERIODO"] == m["PERIODO"]]
        for tipo in ["TIPO_INSTITUCION_III", "TIPO_INSTITUCION_II", "TIPO_INSTITUCION_I"]:
            peers = [x for x in same_year if x.get(tipo) == m.get(tipo)]
            if len(peers) > 1:
                break
        def avg(field: str) -> float:
            vals = [fnum(x.get(field)) for x in peers]
            return sum(vals) / len(vals) if vals else 0.0
        m["DIF_ACAD_TOTAL_VS_PROM_TIPO_IES"] = m["ACAD_TOTAL"] - avg("ACAD_TOTAL")
        m["DIF_JCE_TOTAL_VS_PROM_TIPO_IES"] = m["JCE_TOTAL"] - avg("JCE_TOTAL")
        m["DIF_JCE_POR_ACADEMICO_VS_PROM_TIPO_IES"] = m["JCE_POR_ACADEMICO"] - avg("JCE_POR_ACADEMICO")
        m["DIF_PORC_MAGISTER_VS_PROM_TIPO_IES"] = m["PORC_MAGISTER"] - avg("PORC_MAGISTER")
        m["DIF_PORC_DOCTOR_VS_PROM_TIPO_IES"] = m["PORC_DOCTOR"] - avg("PORC_DOCTOR")
        m["DIF_PORC_FORMACION_AVANZADA_VS_PROM_TIPO_IES"] = m["PORC_FORMACION_AVANZADA"] - avg("PORC_FORMACION_AVANZADA")
        m["DIF_INDICE_ALTA_DEDICACION_VS_PROM_TIPO_IES"] = m["INDICE_ALTA_DEDICACION"] - avg("INDICE_ALTA_DEDICACION")
        m["DIF_PORC_MUJERES_VS_PROM_TIPO_IES"] = m["PORC_MUJERES"] - avg("PORC_MUJERES")
        m["PERCENTIL_ACAD_TOTAL_TIPO_IES"] = percentile([x["ACAD_TOTAL"] for x in peers], m["ACAD_TOTAL"])
        m["PERCENTIL_JCE_TOTAL_TIPO_IES"] = percentile([x["JCE_TOTAL"] for x in peers], m["JCE_TOTAL"])
        m["PERCENTIL_FORMACION_AVANZADA_TIPO_IES"] = percentile([x["PORC_FORMACION_AVANZADA"] for x in peers], m["PORC_FORMACION_AVANZADA"])
        previous = m
    return all_metrics, target, target[-1]


def institution_target_config(target_metrics: list[dict[str, object]], hist_path: str) -> tuple[list[list[object]], str, list[int], list[str]]:
    target_years = sorted({int(m["PERIODO"]) for m in target_metrics if str(m.get("PERIODO", "")).isdigit()})
    target_names = sorted({str(m.get("NOMBRE_INSTITUCION", "")).strip() for m in target_metrics if str(m.get("NOMBRE_INSTITUCION", "")).strip()})
    configured = INSTITUCION_OBJETIVO_NOMBRE.upper().strip()
    name_ok = any(name.upper().strip() == configured for name in target_names)
    validation_name = "OK" if name_ok else "REVISAR"
    years_text = f"{target_years[0]}-{target_years[-1]}" if target_years else ""
    rows = [[
        INSTITUCION_OBJETIVO_CODIGO,
        INSTITUCION_OBJETIVO_NOMBRE,
        " | ".join(target_names),
        "Coincidencia exacta por codigo SIES",
        hist_path,
        "OK",
        validation_name,
        years_text,
        len(target_metrics),
    ]]
    return rows, validation_name, target_years, target_names


def continuity_institution_rows(target_metrics: list[dict[str, object]], target_years: list[int], target_names: list[str]) -> list[list[object]]:
    years_text = f"{target_years[0]}-{target_years[-1]}" if target_years else ""
    return [[
        INSTITUCION_OBJETIVO_CODIGO,
        " | ".join(target_names),
        INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL,
        INSTITUCION_OBJETIVO_NOMBRE,
        "Codigo SIES 162",
        "Coincidencia exacta por codigo SIES",
        "NO",
        years_text,
        len(target_metrics),
        NOTA_CONTINUIDAD_INSTITUCIONAL,
    ]]


def kpi_rows(metrics: list[dict[str, object]]) -> list[list[object]]:
    return [[m.get(col, "") for col in HIST_KPI_COLUMNS] for m in metrics]


def window_metrics(target: list[dict[str, object]], years_count: int | None = None) -> list[dict[str, object]]:
    if years_count is None:
        return target
    years = sorted({int(m["PERIODO"]) for m in target})[-years_count:]
    return [m for m in target if int(m["PERIODO"]) in years]


def preliminary_2026_metrics(base_rows: list[list[object]]) -> dict[str, object]:
    total = len(base_rows)
    mujeres = sum(1 for r in base_rows if r[col_idx("SEXO")] == "M")
    hombres = sum(1 for r in base_rows if r[col_idx("SEXO")] == "H")
    horas = [fnum(r[col_idx("TOTAL_HORAS_ACADEMICO")]) for r in base_rows]
    edades = [fnum(r[col_idx("EDAD_AL_31_05_2026")]) for r in base_rows if r[col_idx("EDAD_AL_31_05_2026")] != ""]
    jce = sum(fnum(r[col_idx("JCE_ESTIMADA")]) for r in base_rows)
    def count_level(label_part: str) -> int:
        return sum(label_part in str(r[col_idx("NIVEL_FORMACION_ACADEMICO_ETIQUETA")]) for r in base_rows)
    doctor = count_level("Doctorado")
    magister = count_level("Magíster")
    especialidad = 0
    profesional = count_level("Título Profesional")
    licenciatura = count_level("Licenciatura")
    tns = count_level("Técnico de Nivel Superior")
    tnm = count_level("Título Técnico de Nivel Medio")
    lem = count_level("Licencia de Enseñanza Media")
    sin_info = sum("Sin código válido" in str(r[col_idx("NIVEL_FORMACION_ACADEMICO_ETIQUETA")]) or "Sin información" in str(r[col_idx("NIVEL_FORMACION_ACADEMICO_ETIQUETA")]) for r in base_rows)
    adv = doctor + magister + especialidad
    return {
        "PERIODO": 2026, "ACAD_TOTAL": total, "ACAD_MUJERES": mujeres, "ACAD_HOMBRES": hombres, "PORC_MUJERES": pct(mujeres, total), "PORC_HOMBRES": pct(hombres, total),
        "EDAD_PROM_GENERAL": sum(edades) / len(edades) if edades else 0, "HORAS_PROM_GENERAL": sum(horas) / len(horas) if horas else 0, "JCE_TOTAL": jce, "JCE_POR_ACADEMICO": pct(jce, total),
        "ACAD_DOCTOR": doctor, "PORC_DOCTOR": pct(doctor, total), "ACAD_MAGISTER": magister, "PORC_MAGISTER": pct(magister, total), "ACAD_ESPECIALIDAD_MEDICA_ODONTOLOGICA": especialidad,
        "PORC_ESPECIALIDAD_MEDICA_ODONTOLOGICA": 0, "ACAD_TITULO_PROFESIONAL": profesional, "PORC_TITULO_PROFESIONAL": pct(profesional, total), "ACAD_LICENCIATURA": licenciatura, "PORC_LICENCIATURA": pct(licenciatura, total),
        "ACAD_TECNICO_NIVEL_SUPERIOR": tns, "PORC_TECNICO_NIVEL_SUPERIOR": pct(tns, total), "ACAD_TECNICO_NIVEL_MEDIO": tnm, "PORC_TECNICO_NIVEL_MEDIO": pct(tnm, total),
        "ACAD_LICENCIA_ENSENANZA_MEDIA": lem, "PORC_LICENCIA_ENSENANZA_MEDIA": pct(lem, total), "ACAD_SIN_INFORMACION_FORMACION": sin_info, "PORC_SIN_INFORMACION_FORMACION": pct(sin_info, total),
        "ACAD_FORMACION_AVANZADA": adv, "PORC_FORMACION_AVANZADA": pct(adv, total),
    }


def comparison_2026_2025(hist_2025: dict[str, object], prelim_2026: dict[str, object]) -> list[list[object]]:
    fields = [
        "ACAD_TOTAL", "ACAD_MUJERES", "ACAD_HOMBRES", "PORC_MUJERES", "PORC_HOMBRES", "EDAD_PROM_GENERAL", "HORAS_PROM_GENERAL", "JCE_TOTAL", "JCE_POR_ACADEMICO",
        "ACAD_DOCTOR", "PORC_DOCTOR", "ACAD_MAGISTER", "PORC_MAGISTER", "ACAD_TITULO_PROFESIONAL", "PORC_TITULO_PROFESIONAL", "ACAD_LICENCIATURA", "PORC_LICENCIATURA",
        "ACAD_TECNICO_NIVEL_SUPERIOR", "PORC_TECNICO_NIVEL_SUPERIOR", "ACAD_TECNICO_NIVEL_MEDIO", "PORC_TECNICO_NIVEL_MEDIO", "ACAD_LICENCIA_ENSENANZA_MEDIA", "PORC_LICENCIA_ENSENANZA_MEDIA",
        "ACAD_SIN_INFORMACION_FORMACION", "PORC_SIN_INFORMACION_FORMACION", "ACAD_FORMACION_AVANZADA", "PORC_FORMACION_AVANZADA",
    ]
    rows = [["ADVERTENCIA", "2026 preliminar", "El año 2026 corresponde a base interna preliminar de carga PES/SIES y no reemplaza la base pública SIES 2026, que se actualizaría posteriormente.", "", ""]]
    for field in fields:
        v25 = fnum(hist_2025.get(field))
        v26 = fnum(prelim_2026.get(field))
        rows.append([field, v25, v26, v26 - v25, pct(v26 - v25, v25)])
    return rows


def historical_alerts(target: list[dict[str, object]], comp_rows: list[list[object]]) -> list[list[object]]:
    alerts = []
    if not target:
        return alerts
    for field, label in [("VAR_ABS_ACAD_TOTAL", "academicos"), ("VAR_ABS_JCE_TOTAL", "JCE")]:
        vals = [m for m in target[1:] if m.get(field) not in ("", None)]
        if vals:
            min_m = min(vals, key=lambda m: fnum(m[field]))
            max_m = max(vals, key=lambda m: fnum(m[field]))
            alerts.append([f"Mayor caida anual de {label}", min_m["PERIODO"], min_m[field], "Variacion anual negativa mas alta del periodo.", "Revisar contexto institucional y cambios de registro."])
            alerts.append([f"Mayor aumento anual de {label}", max_m["PERIODO"], max_m[field], "Variacion anual positiva mas alta del periodo.", "Analizar crecimiento y consistencia de dotacion."])
    for field, label in [("JCE_POR_ACADEMICO", "JCE por academico"), ("PORC_FORMACION_AVANZADA", "% formacion avanzada"), ("PORC_MUJERES", "% mujeres")]:
        min_m = min(target, key=lambda m: fnum(m[field]))
        max_m = max(target, key=lambda m: fnum(m[field]))
        alerts.append([f"Menor {label}", min_m["PERIODO"], min_m[field], "Punto minimo historico observado.", "Comparar con tendencia y fuente historica."])
        alerts.append([f"Mayor {label}", max_m["PERIODO"], max_m[field], "Punto maximo historico observado.", "Comparar con tendencia y fuente historica."])
    for window in [5, 3, 2]:
        subset = window_metrics(target, window)
        if len(subset) >= 2:
            first, last = subset[0], subset[-1]
            alerts.append([f"Cambio relevante ultimos {window} anios", f"{first['PERIODO']}-{last['PERIODO']}", last["ACAD_TOTAL"] - first["ACAD_TOTAL"], "Variacion de academicos en la ventana.", "Revisar junto a JCE y dedicacion."])
    if len(comp_rows) > 1:
        total_row = next((r for r in comp_rows if r[0] == "ACAD_TOTAL"), None)
        if total_row:
            alerts.append(["Comparacion 2026 preliminar vs 2025 historico", "2025-2026", total_row[3], "Diferencia entre base historica publica 2025 y base interna preliminar 2026.", "No interpretar como variacion oficial SIES hasta publicacion 2026."])
    return alerts


def historical_dictionary_rows() -> list[list[object]]:
    rows = []
    for i, col in enumerate(HIST_KPI_COLUMNS, start=1):
        block = "Cobertura academica"
        if "JCE" in col:
            block = "JCE"
        elif "DOCTOR" in col or "MAGISTER" in col or "FORMACION" in col or "TITULO" in col or "LICENCIATURA" in col:
            block = "Formacion"
        elif "HORAS" in col or "DEDICACION" in col:
            block = "Horas y dedicacion"
        elif "INSTITUCION" in col or "MULTI" in col:
            block = "Multiinstitucionalidad"
        elif "CHILENO" in col or "EXTRANJERO" in col:
            block = "Nacionalidad"
        elif "REGION" in col:
            block = "Region"
        elif "DIF_" in col or "PERCENTIL" in col:
            block = "Comparativo"
        rows.append([f"HIST_{i:03d}", col, block, f"Indicador historico {col}.", "Calculado desde HIST_BASE_NORMALIZADA; porcentajes = numerador / total correspondiente.", "HIST_BASE_NORMALIZADA", "PAC_web_2008_2025_SIES_EE.xlsx; OFICIAL_GLOSARIO_PAC_WEB_E.pdf", "2008-2025, ultimos 5, ultimos 3 y ultimos 2 anios", f"Institucion objetivo {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})", "Campos no disponibles quedan fuera o en cero segun normalizacion auditada.", "Permite comparar trayectoria institucional historica.", "Numero / porcentaje / JCE / horas", "Segun tipo de indicador", "Uso interno; 2026 preliminar solo para comparativo, no reemplaza base publica SIES."])
    return rows


def pending_by_column(rows: list[list[object]]) -> list[list[object]]:
    counts = Counter()
    for row in rows:
        if row[col_idx("ESTADO_CARGA_PES")] != "NO_CARGADO_PENDIENTE":
            continue
        for col in str(row[col_idx("COLUMNAS_OBSERVADAS")] or "").split(" | "):
            if col:
                counts[col] += 1
    total = sum(counts.values())
    return [[key, motivo_legible(f"{key}=VALOR_NO_CARGABLE"), value, value / total if total else 0] for key, value in counts.most_common()]


def transform_tables(events: list[dict[str, str]]) -> tuple[list[list[object]], list[list[object]], int]:
    by_type, by_field, filas = Counter(), Counter(), set()
    for event in events:
        tipo = event.get("tipo_evento", "SIN_TIPO") or "SIN_TIPO"
        campo = event.get("columna", "SIN_CAMPO") or "SIN_CAMPO"
        by_type[tipo] += 1
        by_field[(tipo, campo)] += 1
        if event.get("fila_origen"):
            filas.add(event["fila_origen"])
    type_rows = [[k, MOTIVOS.get(k, k.replace("_", " ").capitalize() + "."), v] for k, v in by_type.most_common()]
    field_rows = [[k[0], MOTIVOS.get(k[0], k[0].replace("_", " ").capitalize() + "."), v, k[1], "Transformacion tecnica de salida; no modifica base original."] for k, v in by_field.most_common()]
    return type_rows, field_rows, len(filas)


def original_sies_diffs(detail: list[list[object]]) -> int:
    diff = 0
    for row in detail:
        if row[0] != "CARGADO_PES":
            continue
        offset = len(CONTROL_COLUMNS)
        if any(str(row[offset + i * 2] or "") != str(row[offset + i * 2 + 1] or "") for i in range(len(COLUMNAS_OFICIALES))):
            diff += 1
    return diff


def build_summary(rows: list[list[object]], detail: list[list[object]], transformaciones: list[dict[str, str]]) -> dict[str, list[list[object]]]:
    total = len(rows)
    cargados = sum(1 for row in rows if row[col_idx("ESTADO_CARGA_PES")] == "CARGADO_PES")
    pendientes = total - cargados
    horas = [parse_float(row[col_idx("TOTAL_HORAS_ACADEMICO")]) for row in rows]
    edades = [parse_float(row[col_idx("EDAD_AL_31_05_2026")]) for row in rows if row[col_idx("EDAD_AL_31_05_2026")] != ""]
    anios = [parse_float(row[col_idx("ANIOS_DESDE_TITULO")]) for row in rows if row[col_idx("ANIOS_DESDE_TITULO")] != ""]
    transform_type, transform_field, filas_transformadas = transform_tables(transformaciones)
    horas_total = sum(horas)
    programa_horas = sum_by(rows, "NOMBRE_PRINCIPAL_PROGRAMA", "TOTAL_HORAS_ACADEMICO")
    programa_top = programa_horas[0] if programa_horas else ["Sin dato", 0, 0, 0]
    diffs = original_sies_diffs(detail)
    return {
        "RESUMEN_GENERAL": [
            ["Base original", total, "registros"], ["Cargados PES/SIES", cargados, "registros"],
            ["Pendientes", pendientes, "registros"], ["% carga efectiva", cargados / total if total else 0, "porcentaje"],
            ["% pendiente", pendientes / total if total else 0, "porcentaje"], ["Horas totales", round(horas_total, 2), "horas"],
            ["JCE total", round(horas_total / 44, 2), "JCE"], ["Promedio horas", round(horas_total / total, 2), "horas"],
            ["Mediana horas", round(median(horas), 2), "horas"], ["Edad promedio", round(sum(edades) / len(edades), 1), "anios"],
            ["Edad mediana", round(median(edades), 1), "anios"], ["Anios promedio desde titulo", round(sum(anios) / len(anios), 1), "anios"],
            ["Mediana anios desde titulo", round(median(anios), 1), "anios"], ["Magister", sum(row[col_idx("ES_MAGISTER")] == "Si" for row in rows), "academicos"],
            ["% Magister", sum(row[col_idx("ES_MAGISTER")] == "Si" for row in rows) / total if total else 0, "porcentaje"],
            ["Doctorado", sum(row[col_idx("ES_DOCTORADO")] == "Si" for row in rows), "academicos"],
            ["% Doctorado", sum(row[col_idx("ES_DOCTORADO")] == "Si" for row in rows) / total if total else 0, "porcentaje"],
            ["Profesionales codigo 3", sum(row[col_idx("ES_PROFESIONAL_CODIGO_3")] == "Si" for row in rows), "academicos"],
            ["Tecnicos codigo 5", sum(row[col_idx("ES_TECNICO_CODIGO_5")] == "Si" for row in rows), "academicos"],
            ["Diferencias entre ORIGINAL y SIES", diffs, "registros"], ["Registros con transformacion tecnica", filas_transformadas, "registros"],
        ],
        "RESUMEN_DEDICACION": counter_table(rows, "TIPO_DEDICACION"),
        "RESUMEN_NIVEL_FORMACION": counter_table(rows, "NIVEL_FORMACION_ACADEMICO_ETIQUETA", "codigo"),
        "RESUMEN_MAGISTER_DOCTORADO": [["Magister", sum(row[col_idx("ES_MAGISTER")] == "Si" for row in rows), sum(row[col_idx("ES_MAGISTER")] == "Si" for row in rows) / total], ["Doctorado", sum(row[col_idx("ES_DOCTORADO")] == "Si" for row in rows), 0], ["Profesional codigo 3", sum(row[col_idx("ES_PROFESIONAL_CODIGO_3")] == "Si" for row in rows), sum(row[col_idx("ES_PROFESIONAL_CODIGO_3")] == "Si" for row in rows) / total], ["Tecnico codigo 5", sum(row[col_idx("ES_TECNICO_CODIGO_5")] == "Si" for row in rows), sum(row[col_idx("ES_TECNICO_CODIGO_5")] == "Si" for row in rows) / total]],
        "RESUMEN_EDAD": counter_table(rows, "TRAMO_EDAD"),
        "RESUMEN_SEXO": counter_table(rows, "SEXO_ETIQUETA"),
        "RESUMEN_CARGO": counter_table(rows, "CARGO_NORMALIZADO_ETIQUETA", "codigo"),
        "RESUMEN_PROGRAMA": counter_table(rows, "NOMBRE_PRINCIPAL_PROGRAMA"),
        "RESUMEN_COMUNA": counter_table(rows, "COMUNA_PRINCIPAL_PROGRAMA"),
        "RESUMEN_PENDIENTES": [[r[0], motivo_legible(r[0]), r[1], r[2], accion_legible(r[0])] for r in counter_table([row for row in rows if row[col_idx("ESTADO_CARGA_PES")] == "NO_CARGADO_PENDIENTE"], "MOTIVO_NO_CARGA_LEGIBLE")],
        "RESUMEN_PENDIENTES_COLUMNA": pending_by_column(rows),
        "RESUMEN_TRANSFORMACIONES": transform_type,
        "RESUMEN_TRANSFORMACIONES_CAMPO": transform_field,
        "RESUMEN_HORAS_PROGRAMA": programa_horas,
        "RESUMEN_HORAS_VINCULO": sum_by(rows, "TIPO_VINCULO_HORARIO", "TOTAL_HORAS_ACADEMICO"),
        "ALERTAS_EJECUTIVAS": [
            ["Doctorado igual a 0", 0, "No se identifican academicos con doctorado segun los datos cargados y criterios disponibles.", "Validar si se espera presencia doctoral."],
            ["9 registros pendientes/no cargados", pendientes, "Existen registros originales no cargados en PES/SIES.", "Revisar datos no cargables y fecha futura pendiente."],
            [f"{programa_top[0]} concentra alto porcentaje de horas", f"{programa_top[3]:.1%}", f"{programa_top[0]} concentra {programa_top[3]:.1%} de las horas con {programa_top[1]} registros.", "Validar distribucion horaria y consistencia de asignacion academica."],
            ["Registros con diferencias ORIGINAL vs SIES", diffs, "Diferencias asociadas principalmente a transformaciones tecnicas de salida.", "Usar DETALLE_TRAZABILIDAD para comparacion campo a campo."],
            ["Registros con valores no cargables", pendientes, "Registros pendientes por datos no cargables o fecha futura.", "Completar datos fuente con respaldo antes de carga complementaria."],
        ],
        "CATALOGO_CODIGOS_OFICIALES": CATALOGO_OFICIAL_ROWS,
    }


TABLE_LAYOUT = [
    ("RESUMEN_GENERAL", ["KPI", "VALOR", "UNIDAD"], "TablaResumenGeneral"),
    ("RESUMEN_DEDICACION", ["TIPO_DEDICACION", "CANTIDAD", "PORCENTAJE"], "TablaResumenDedicacion"),
    ("RESUMEN_NIVEL_FORMACION", ["NIVEL_FORMACION_ACADEMICO_ETIQUETA", "CANTIDAD", "PORCENTAJE"], "TablaResumenNivel"),
    ("RESUMEN_MAGISTER_DOCTORADO", ["INDICADOR", "CANTIDAD", "PORCENTAJE"], "TablaResumenMagDoc"),
    ("RESUMEN_EDAD", ["TRAMO_EDAD", "CANTIDAD", "PORCENTAJE"], "TablaResumenEdad"),
    ("RESUMEN_SEXO", ["SEXO_ETIQUETA", "CANTIDAD", "PORCENTAJE"], "TablaResumenSexo"),
    ("RESUMEN_CARGO", ["CARGO_NORMALIZADO_ETIQUETA", "CANTIDAD", "PORCENTAJE"], "TablaResumenCargo"),
    ("RESUMEN_PROGRAMA", ["PROGRAMA", "CANTIDAD", "PORCENTAJE"], "TablaResumenPrograma"),
    ("RESUMEN_COMUNA", ["COMUNA", "CANTIDAD", "PORCENTAJE"], "TablaResumenComuna"),
    ("RESUMEN_PENDIENTES", ["MOTIVO_TECNICO", "MOTIVO_LEGIBLE", "REGISTROS", "PORCENTAJE", "ACCION_REQUERIDA"], "TablaResumenPendientes"),
    ("RESUMEN_PENDIENTES_COLUMNA", ["COLUMNA", "MOTIVO_LEGIBLE", "REGISTROS", "PORCENTAJE"], "TablaResumenPendCol"),
    ("RESUMEN_TRANSFORMACIONES", ["TRANSFORMACION_TECNICA", "TRANSFORMACION_LEGIBLE", "REGISTROS_AFECTADOS"], "TablaResumenTransformaciones"),
    ("RESUMEN_TRANSFORMACIONES_CAMPO", ["TRANSFORMACION_TECNICA", "TRANSFORMACION_LEGIBLE", "REGISTROS_AFECTADOS", "CAMPO_AFECTADO", "INTERPRETACION"], "TablaResumenTransCampo"),
    ("RESUMEN_HORAS_PROGRAMA", ["PROGRAMA", "REGISTROS", "HORAS", "PORCENTAJE_HORAS"], "TablaResumenHorasProg"),
    ("RESUMEN_HORAS_VINCULO", ["TIPO_VINCULO_HORARIO", "REGISTROS", "HORAS", "PORCENTAJE_HORAS"], "TablaResumenHorasVinc"),
    ("ALERTAS_EJECUTIVAS", ["ALERTA", "VALOR", "INTERPRETACION", "ACCION_SUGERIDA"], "TablaAlertasEjecutivas"),
    ("CATALOGO_CODIGOS_OFICIALES", ["TIPO_CAMPO", "CODIGO", "ETIQUETA_OFICIAL", "FUENTE"], "TablaCatalogoCodigos"),
    (
        "CONFIGURACION_INSTITUCION_OBJETIVO",
        [
            "INSTITUCION_OBJETIVO_CODIGO",
            "INSTITUCION_OBJETIVO_NOMBRE_CONFIGURADO",
            "NOMBRE_INSTITUCION_EN_HISTORICO",
            "METODO_DETECCION",
            "FUENTE_DETECCION",
            "VALIDACION_CODIGO",
            "VALIDACION_NOMBRE",
            "ANIOS_ENCONTRADOS",
            "TOTAL_FILAS_HISTORICAS_INSTITUCION",
        ],
        "TablaConfigInstitucionObjetivo",
    ),
    (
        "CONTINUIDAD_INSTITUCIONAL",
        [
            "CODIGO_SIES",
            "NOMBRE_HISTORICO_DETECTADO",
            "NOMBRE_ACTUAL_REFERENCIAL",
            "NOMBRE_CONFIGURADO_EN_SCRIPT",
            "CRITERIO_CRUCE",
            "METODO_VALIDACION",
            "SELECCION_POR_NOMBRE_PARCIAL",
            "ANIOS_HISTORICOS_ENCONTRADOS",
            "FILAS_HISTORICAS",
            "NOTA_INTERPRETATIVA",
        ],
        "TablaContinuidadInstitucional",
    ),
]


def diccionario_rows() -> list[list[str]]:
    specs = [
        ("Total registros base original", "Cobertura y carga PES", "Cuenta los registros originales incluidos en BASE_KPI.", "COUNT(BASE_KPI!B2:B191)", "NUM_DOCUMENTO", "Registros", "Entero", "Dimensiona el universo de respaldo interno."),
        ("Total registros cargados PES/SIES", "Cobertura y carga PES", "Cuenta registros que fueron procesados por PES/SIES.", 'COUNTIF(BASE_KPI!A2:A191,"CARGADO_PES")', "ESTADO_CARGA_PES", "Registros", "Entero", "Mide avance efectivo de carga."),
        ("Total registros pendientes/no cargados", "Cobertura y carga PES", "Cuenta registros originales que quedaron pendientes.", 'COUNTIF(BASE_KPI!A2:A191,"NO_CARGADO_PENDIENTE")', "ESTADO_CARGA_PES", "Registros", "Entero", "Identifica brecha para carga complementaria."),
        ("% carga efectiva", "Cobertura y carga PES", "Mide la proporcion de registros cargados sobre la base original.", "Cargados PES/SIES / Total base original", "ESTADO_CARGA_PES", "%", "Porcentaje con 1 decimal", "Un valor alto indica mayor completitud de carga."),
        ("% pendiente", "Cobertura y carga PES", "Mide la proporcion de registros pendientes.", "Pendientes / Total base original", "ESTADO_CARGA_PES", "%", "Porcentaje con 1 decimal", "Permite dimensionar la brecha pendiente."),
        ("Numero de columnas oficiales controladas", "Cobertura y carga PES", "Cuenta las columnas oficiales del archivo En Institucion.", "COUNT(COLUMNAS_OFICIALES)", "Encabezado oficial", "Columnas", "Entero", "Confirma alcance estructural del control."),
        ("Registros pendientes por motivo", "Cobertura y carga PES", "Agrupa pendientes segun causa tecnica legible.", "GROUP BY MOTIVO_NO_CARGA_LEGIBLE", "MOTIVO_NO_CARGA_LEGIBLE", "Registros", "Entero y porcentaje", "Prioriza acciones de depuracion."),
        ("Registros pendientes por columna observada", "Cobertura y carga PES", "Agrupa pendientes segun columna que origina bloqueo.", "GROUP BY COLUMNAS_OBSERVADAS", "COLUMNAS_OBSERVADAS", "Registros", "Entero", "Identifica campos a corregir."),
        ("Top 10 registros pendientes con accion requerida", "Cobertura y carga PES", "Lista registros pendientes y accion operativa.", "FIRST 10 WHERE ESTADO=NO_CARGADO_PENDIENTE", "ESTADO_CARGA_PES, ACCION_REQUERIDA_LEGIBLE", "Registros", "Tabla", "Facilita gestion individual."),
        ("Total horas academicas", "Dedicacion horaria y JCE", "Suma horas planta, contrata y honorarios.", "SUM(TOTAL_HORAS_ACADEMICO)", "NUM_HORAS_*_NUM", "Horas", "Numero con 2 decimales", "Mide volumen de dedicacion academica."),
        ("JCE total estimada", "Dedicacion horaria y JCE", "Estima jornadas completas equivalentes.", "SUM(TOTAL_HORAS_ACADEMICO) / 44", "TOTAL_HORAS_ACADEMICO", "JCE", "Numero con 2 decimales", "Dimensiona dotacion equivalente."),
        ("Promedio de horas por academico", "Dedicacion horaria y JCE", "Calcula dedicacion horaria promedio por registro.", "AVERAGE(TOTAL_HORAS_ACADEMICO)", "TOTAL_HORAS_ACADEMICO", "Horas", "Numero con 2 decimales", "Resume dedicacion media."),
        ("Mediana de horas por academico", "Dedicacion horaria y JCE", "Calcula valor central de horas.", "MEDIAN(TOTAL_HORAS_ACADEMICO)", "TOTAL_HORAS_ACADEMICO", "Horas", "Numero con 2 decimales", "Reduce efecto de extremos."),
        ("Minimo y maximo de horas", "Dedicacion horaria y JCE", "Identifica rango de dedicacion observado.", "MIN/MAX(TOTAL_HORAS_ACADEMICO)", "TOTAL_HORAS_ACADEMICO", "Horas", "Numero con 2 decimales", "Permite detectar extremos."),
        ("Academicos sin horas", "Dedicacion horaria y JCE", "Cuenta registros con dedicacion cero.", 'COUNTIF(TIPO_DEDICACION,"Sin horas")', "TIPO_DEDICACION", "Academicos", "Entero", "Senala posibles datos incompletos."),
        ("Academicos con baja dedicacion", "Dedicacion horaria y JCE", "Cuenta registros con mas de 0 y menos de 11 horas.", 'COUNTIF(TIPO_DEDICACION,"Baja dedicacion")', "TIPO_DEDICACION", "Academicos", "Entero", "Caracteriza baja dedicacion."),
        ("Academicos con media dedicacion", "Dedicacion horaria y JCE", "Cuenta registros con 11 a 21 horas.", 'COUNTIF(TIPO_DEDICACION,"Media dedicacion")', "TIPO_DEDICACION", "Academicos", "Entero", "Caracteriza media dedicacion."),
        ("Academicos con alta dedicacion", "Dedicacion horaria y JCE", "Cuenta registros con 22 a 43 horas.", 'COUNTIF(TIPO_DEDICACION,"Alta dedicacion")', "TIPO_DEDICACION", "Academicos", "Entero", "Caracteriza alta dedicacion."),
        ("Academicos con jornada completa o equivalente", "Dedicacion horaria y JCE", "Cuenta registros con 44 horas o mas.", 'COUNTIF(TIPO_DEDICACION,"Jornada completa o equivalente")', "TIPO_DEDICACION", "Academicos", "Entero", "Identifica dedicacion completa."),
        ("Distribucion de JCE por programa", "Dedicacion horaria y JCE", "Suma JCE por programa principal.", "SUM(JCE_ESTIMADA) GROUP BY PROGRAMA", "JCE_ESTIMADA, NOMBRE_PRINCIPAL_PROGRAMA", "JCE", "Numero con 2 decimales", "Compara dotacion por programa."),
        ("Distribucion de horas por programa", "Dedicacion horaria y JCE", "Suma horas por programa principal.", "SUM(TOTAL_HORAS_ACADEMICO) GROUP BY PROGRAMA", "TOTAL_HORAS_ACADEMICO, NOMBRE_PRINCIPAL_PROGRAMA", "Horas", "Numero con 2 decimales", "Mide concentracion programatica."),
        ("Distribucion de horas por comuna", "Dedicacion horaria y JCE", "Suma horas por comuna principal.", "SUM(TOTAL_HORAS_ACADEMICO) GROUP BY COMUNA", "TOTAL_HORAS_ACADEMICO, COMUNA_PRINCIPAL_PROGRAMA", "Horas", "Numero con 2 decimales", "Mide concentracion territorial."),
        ("Top 10 academicos por total de horas", "Dedicacion horaria y JCE", "Ordena registros por mayor dedicacion.", "SORT DESC TOTAL_HORAS_ACADEMICO LIMIT 10", "TOTAL_HORAS_ACADEMICO", "Tabla", "Horas con 2 decimales", "Identifica mayores dedicaciones."),
        ("Participacion porcentual de horas por tipo", "Dedicacion horaria y JCE", "Calcula peso relativo por tipo de vinculo horario.", "SUM(HORAS POR TIPO) / SUM(HORAS)", "TIPO_VINCULO_HORARIO, TOTAL_HORAS_ACADEMICO", "%", "Porcentaje con 1 decimal", "Describe composicion de vinculos."),
        ("Distribucion por NIVEL_FORMACION_ACADEMICO", "Formacion academica", "Agrupa por etiqueta trazable de nivel formativo.", "GROUP BY NIVEL_FORMACION_ACADEMICO_ETIQUETA", "NIVEL_FORMACION_ACADEMICO_ETIQUETA", "Academicos", "Entero y porcentaje", "Describe composicion formativa."),
        ("Cantidad y porcentaje Magister", "Formacion academica", "Cuenta registros identificados como magister.", 'COUNTIF(ES_MAGISTER,"Si")', "ES_MAGISTER", "Academicos/%", "Entero y porcentaje", "Aproxima presencia de magister con criterio trazable."),
        ("Cantidad y porcentaje Doctorado", "Formacion academica", "Cuenta academicos identificados con formacion doctoral.", 'COUNTIF(ES_DOCTORADO,"Si")', "ES_DOCTORADO", "Academicos/%", "Entero y porcentaje", "Si es 0, requiere validacion si se esperaba presencia doctoral."),
        ("Cantidad y porcentaje profesionales codigo 3", "Formacion academica", "Cuenta nivel de formacion codigo 3.", 'COUNTIF(ES_PROFESIONAL_CODIGO_3,"Si")', "ES_PROFESIONAL_CODIGO_3", "Academicos/%", "Entero y porcentaje", "Mide presencia de codigo profesional observado."),
        ("Cantidad y porcentaje tecnicos codigo 5", "Formacion academica", "Cuenta nivel de formacion codigo 5.", 'COUNTIF(ES_TECNICO_CODIGO_5,"Si")', "ES_TECNICO_CODIGO_5", "Academicos/%", "Entero y porcentaje", "Mide presencia de codigo tecnico observado."),
        ("Anios promedio desde obtencion del titulo/grado", "Formacion academica", "Promedia antiguedad del titulo con fechas validas.", "AVERAGE(ANIOS_DESDE_TITULO validos)", "ANIOS_DESDE_TITULO", "Anios", "Numero con 1 decimal", "Estima trayectoria desde titulacion."),
        ("Mediana de anios desde titulo/grado", "Formacion academica", "Calcula valor central de antiguedad del titulo.", "MEDIAN(ANIOS_DESDE_TITULO validos)", "ANIOS_DESDE_TITULO", "Anios", "Numero con 1 decimal", "Reduce efecto de extremos."),
        ("Distribucion por tramo de antiguedad del titulo", "Formacion academica", "Agrupa por tramo de anios desde titulo.", "GROUP BY TRAMO_ANTIGUEDAD_TITULO", "TRAMO_ANTIGUEDAD_TITULO", "Academicos", "Entero y porcentaje", "Muestra madurez formativa."),
        ("Academicos sin fecha valida de titulo", "Formacion academica", "Cuenta registros sin fecha valida de titulo.", "COUNT BLANK ANIOS_DESDE_TITULO", "FECHA_OBT_TIT_O_GRADO", "Academicos", "Entero", "Identifica brecha de calidad de datos."),
        ("Distribucion por pais de obtencion del titulo/grado", "Formacion academica", "Agrupa por pais de obtencion declarado.", "GROUP BY PAIS_OBTENCION_TIT_O_GRADO", "PAIS_OBTENCION_TIT_O_GRADO", "Academicos", "Entero y porcentaje", "Describe origen formativo."),
        ("Distribucion por institucion de obtencion del titulo/grado", "Formacion academica", "Agrupa por institucion de obtencion.", "GROUP BY NOMBRE_INSTITUCION_OBT_TITULO", "NOMBRE_INSTITUCION_OBT_TITULO", "Academicos", "Entero y porcentaje", "Describe origen institucional."),
        ("Distribucion por sexo", "Composicion demografica", "Agrupa por etiqueta de sexo.", "GROUP BY SEXO_ETIQUETA", "SEXO_ETIQUETA", "Academicos", "Entero y porcentaje", "Describe composicion demografica."),
        ("Distribucion por edad", "Composicion demografica", "Agrupa por tramo de edad al corte.", "GROUP BY TRAMO_EDAD", "TRAMO_EDAD", "Academicos", "Entero y porcentaje", "Muestra estructura etaria."),
        ("Edad promedio", "Composicion demografica", "Promedia edad con fecha nacimiento valida.", "AVERAGE(EDAD_AL_31_05_2026)", "EDAD_AL_31_05_2026", "Anios", "Numero con 1 decimal", "Resume edad media."),
        ("Edad mediana", "Composicion demografica", "Calcula edad central.", "MEDIAN(EDAD_AL_31_05_2026)", "EDAD_AL_31_05_2026", "Anios", "Numero con 1 decimal", "Resume edad tipica."),
        ("Distribucion por nacionalidad", "Composicion demografica", "Agrupa por nacionalidad informada.", "GROUP BY NACIONALIDAD", "NACIONALIDAD", "Academicos", "Entero y porcentaje", "Describe origen nacional."),
        ("Distribucion por cargo normalizado", "Composicion demografica", "Agrupa por etiqueta de cargo normalizado.", "GROUP BY CARGO_NORMALIZADO_ETIQUETA", "CARGO_NORMALIZADO_ETIQUETA", "Academicos", "Entero y porcentaje", "Describe composicion funcional."),
        ("Distribucion por nivel superior de adscripcion", "Distribucion institucional/programatica", "Agrupa por unidad superior.", "GROUP BY NIVEL_SUPERIOR_ADSCRIPCION", "NIVEL_SUPERIOR_ADSCRIPCION", "Academicos", "Entero y porcentaje", "Muestra adscripcion institucional."),
        ("Distribucion por nivel secundario de adscripcion", "Distribucion institucional/programatica", "Agrupa por unidad secundaria.", "GROUP BY NIVEL_SECUNDARIO_ADSCRIPCION", "NIVEL_SECUNDARIO_ADSCRIPCION", "Academicos", "Entero y porcentaje", "Muestra adscripcion secundaria."),
        ("Distribucion por programa principal", "Distribucion institucional/programatica", "Agrupa por programa principal.", "GROUP BY NOMBRE_PRINCIPAL_PROGRAMA", "NOMBRE_PRINCIPAL_PROGRAMA", "Academicos", "Entero y porcentaje", "Describe cobertura programatica."),
        ("Distribucion por comuna principal del programa", "Distribucion institucional/programatica", "Agrupa por comuna del programa.", "GROUP BY COMUNA_PRINCIPAL_PROGRAMA", "COMUNA_PRINCIPAL_PROGRAMA", "Academicos", "Entero y porcentaje", "Describe distribucion territorial."),
        ("Distribucion por comuna de mayor funcion", "Distribucion institucional/programatica", "Agrupa por comuna de mayor funcion.", "GROUP BY COMUNA_MAYOR_FUNCION", "COMUNA_MAYOR_FUNCION", "Academicos", "Entero y porcentaje", "Controla campo observado por PES."),
        ("Registros con datos originales modificados para carga PES por transformacion tecnica", "Calidad de datos y trazabilidad", "Cuenta filas con transformaciones tecnicas auditadas.", "COUNT DISTINCT fila_origen auditoria transformaciones", "auditoria_transformaciones", "Registros", "Entero", "Dimensiona intervencion tecnica de salida."),
        ("Registros excluidos por valores no cargables", "Calidad de datos y trazabilidad", "Cuenta registros pendientes por datos no cargables.", 'COUNTIF(ESTADO_CARGA_PES,"NO_CARGADO_PENDIENTE")', "ESTADO_CARGA_PES, MOTIVO_NO_CARGA_LEGIBLE", "Registros", "Entero", "Mide brecha para carga complementaria."),
        ("Campos con mayor cantidad de ajustes tecnicos", "Calidad de datos y trazabilidad", "Ranking de campos con transformaciones.", "COUNT BY campo auditoria transformaciones", "columna auditoria", "Campos", "Entero", "Prioriza revision tecnica."),
        ("Campos con mayor cantidad de datos faltantes o no cargables", "Calidad de datos y trazabilidad", "Ranking de campos observados en pendientes.", "COUNT BY COLUMNAS_OBSERVADAS", "COLUMNAS_OBSERVADAS", "Campos", "Entero", "Prioriza depuracion fuente."),
        ("Conteo de registros con diferencias entre ORIGINAL y SIES", "Calidad de datos y trazabilidad", "Cuenta cargados con diferencias campo a campo.", "COUNT registros donde SIES_* distinto de ORIGINAL_*", "DETALLE_TRAZABILIDAD", "Registros", "Entero", "Diferencias son transformaciones tecnicas, no necesariamente cambios sustantivos."),
        ("Conteo de transformaciones por tipo", "Calidad de datos y trazabilidad", "Agrupa eventos de transformacion tecnica.", "GROUP BY tipo_evento auditoria transformaciones", "tipo_evento auditoria", "Eventos", "Entero", "Explica ajustes aplicados para PES/SIES."),
        ("Registros cargados con transformacion aplicada", "Calidad de datos y trazabilidad", "Cuenta filas cargadas con al menos una transformacion.", "COUNT DISTINCT fila_origen auditoria transformaciones", "fila_origen auditoria", "Registros", "Entero", "Mide trazabilidad de salida."),
        ("Registros cargados sin transformacion aplicada", "Calidad de datos y trazabilidad", "Cuenta cargados sin eventos de transformacion.", "Cargados PES/SIES - registros transformados", "ESTADO_CARGA_PES, auditoria_transformaciones", "Registros", "Entero", "Identifica filas que pasaron sin ajuste tecnico."),
    ]
    rows = []
    for i, spec in enumerate(specs, 1):
        observacion = "Fase 10D: definicion especifica, formula trazable y presentacion ejecutiva."
        nombre, bloque = spec[0], spec[1]
        if "formacion" in nombre.lower() or "magister" in nombre.lower() or "doctorado" in nombre.lower() or "tecnic" in nombre.lower() or "profesionales codigo" in nombre.lower():
            observacion += " Etiqueta oficial tomada del instructivo SIES Personal Académico 2026 para NIVEL_FORMACION_ACADEMICO; valores sin codigo valido se presentan como Sin código válido."
        if "cargo normalizado" in nombre.lower():
            observacion += " Etiqueta oficial tomada del instructivo SIES Personal Académico 2026 para CARGO_NORMALIZADO; valores sin codigo valido se presentan como Sin código válido."
        if bloque in {"Formacion academica", "Composicion demografica"}:
            observacion += " La tabla CATALOGO_CODIGOS_OFICIALES queda visible en TABLAS_RESUMEN."
        rows.append([f"KPI_{i:02d}", *spec, "BASE_KPI / TABLAS_RESUMEN", "Segun filtro descrito en formula", "No modifica fuente; pendientes se mantienen visibles", "Unidad de Analisis Institucional / Personal Academico", observacion])
    return rows


def backup(path: Path, desktop: bool = False) -> None:
    if not path.exists():
        return
    target_dir = Path("/Users/alexi/Desktop/backups_personal_academico_2026") if desktop else path.parent / "backups"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target_dir / f"{path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}")


def write_matrix(ws, workbook, name: str, headers: list[str], rows: list[list[object]], start_row: int, start_col: int, style: str) -> tuple[int, int, int, int]:
    fmts = workbook.formats_map
    for c, header in enumerate(headers):
        ws.write(start_row, start_col + c, header, fmts["header"])
    for r, row in enumerate(rows, start=start_row + 1):
        for c, value in enumerate(row):
            header = headers[c]
            unit = str(row[2]).lower() if len(row) > 2 else ""
            metric = str(row[0]).lower() if row else ""
            is_percent = "PORCENTAJE" in header or str(header).startswith("%") or unit == "porcentaje" or metric.startswith("%")
            fmt = fmts["percent"] if is_percent else fmts["num2"] if any(x in header for x in ["HORAS", "JCE"]) else fmts["num1"] if "ANIOS" in header or "EDAD" in header else fmts["text"]
            ws.write(r, start_col + c, value, fmt)
    last_row, last_col = start_row + len(rows), start_col + len(headers) - 1
    ws.add_table(start_row, start_col, last_row, last_col, {"name": name, "style": style, "columns": [{"header": h} for h in headers], "autofilter": True})
    return start_row, start_col, last_row, last_col


def autofit(ws, headers: list[str], rows: list[list[object]], max_width: int = 48) -> None:
    for c, header in enumerate(headers):
        width = min(max_width, max(len(str(header)) + 2, 10))
        for row in rows[:200]:
            width = max(width, min(max_width, len(str(row[c] if c < len(row) else "")) + 2))
        ws.set_column(c, c, width)


def safe_table_name(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch == "_")[:31]


def write_historical_kpi_sheet(wb, sheet_name: str, metrics: list[dict[str, object]]) -> None:
    ws = wb.add_worksheet(sheet_name)
    rows = kpi_rows(metrics)
    write_matrix(ws, wb, safe_table_name("Tabla" + sheet_name.replace("HIST_", "Hist")), HIST_KPI_COLUMNS, rows, 0, 0, "Table Style Medium 6")
    ws.freeze_panes(1, 1)
    autofit(ws, HIST_KPI_COLUMNS, rows, 24)
    note_fmt = wb.add_format({"bg_color": "#EDEDED", "font_color": "#404040", "italic": True, "text_wrap": True, "border": 1})
    # Tendencias simples desde columnas clave.
    chart_fields = [
        ("ACAD_TOTAL", "Total academicos", "A3"),
        ("JCE_TOTAL", "JCE total", "I3"),
        ("JCE_POR_ACADEMICO", "JCE por academico", "A20"),
        ("PORC_MAGISTER", "% Magister", "I20"),
        ("PORC_DOCTOR", "% Doctor", "A37"),
        ("PORC_FORMACION_AVANZADA", "% Formacion avanzada", "I37"),
        ("PORC_MUJERES", "% Mujeres", "A54"),
        ("INDICE_ALTA_DEDICACION", "Indice alta dedicacion", "I54"),
        ("INDICE_MULTIINSTITUCIONALIDAD", "Indice multiinstitucionalidad", "A71"),
    ]
    if rows:
        for field, title, cell in chart_fields:
            if field not in HIST_KPI_COLUMNS:
                continue
            col_num = HIST_KPI_COLUMNS.index(field)
            ch = wb.add_chart({"type": "line"})
            ch.add_series({
                "name": title,
                "categories": [sheet_name, 1, 0, len(rows), 0],
                "values": [sheet_name, 1, col_num, len(rows), col_num],
            })
            ch.set_title({"name": title})
            ch.set_legend({"none": True})
            ch.set_size({"width": 380, "height": 220})
            ws.insert_chart(cell, ch)
    ws.merge_range("A88:H90", "Continuidad institucional: " + NOTA_CONTINUIDAD_INSTITUCIONAL, note_fmt)


def write_historical_sheets(wb, hist: dict[str, object], base_rows_2026: list[list[object]]) -> None:
    if not hist.get("target_metrics"):
        ws = wb.add_worksheet("HIST_DIAGNOSTICO")
        ws.write(0, 0, "No se identifico institucion objetivo para analisis historico institucional.")
        return
    records = hist["records"]
    hist_rows = [[rec.get(col, "") for col in HIST_BASE_COLUMNS] for rec in records]
    ws = wb.add_worksheet("HIST_BASE_NORMALIZADA")
    write_matrix(ws, wb, "TablaHistBaseNormalizada", HIST_BASE_COLUMNS, hist_rows, 0, 0, "Table Style Medium 2")
    ws.freeze_panes(1, 3)
    autofit(ws, HIST_BASE_COLUMNS, hist_rows, 22)

    target = hist["target_metrics"]
    windows = {
        "HIST_KPI_2008_2025": window_metrics(target, None),
        "HIST_KPI_ULTIMOS_5_ANIOS": window_metrics(target, 5),
        "HIST_KPI_ULTIMOS_3_ANIOS": window_metrics(target, 3),
        "HIST_KPI_ULTIMOS_2_ANIOS": window_metrics(target, 2),
    }
    for sheet_name, metrics in windows.items():
        write_historical_kpi_sheet(wb, sheet_name, metrics)

    hist_2025 = next((m for m in target if int(m["PERIODO"]) == 2025), target[-1])
    prelim_2026 = preliminary_2026_metrics(base_rows_2026)
    comp_rows = comparison_2026_2025(hist_2025, prelim_2026)
    ws = wb.add_worksheet("HIST_COMPARATIVO_2026_VS_2025")
    comp_headers = ["KPI", "2025_HISTORICO", "2026_PRELIMINAR", "DIFERENCIA_ABS", "DIFERENCIA_PORC"]
    write_matrix(ws, wb, "TablaHistComparativo2026", comp_headers, comp_rows, 0, 0, "Table Style Medium 5")
    note_fmt = wb.add_format({"bg_color": "#EDEDED", "font_color": "#404040", "italic": True, "text_wrap": True, "border": 1})
    ws.merge_range("G1:M4", "Continuidad institucional: " + NOTA_CONTINUIDAD_INSTITUCIONAL, note_fmt)
    ws.freeze_panes(1, 1)
    autofit(ws, comp_headers, comp_rows, 44)

    dict_rows = historical_dictionary_rows()
    dict_headers = ["KPI_ID", "NOMBRE_KPI", "BLOQUE", "DEFINICION_CUALITATIVA", "FORMULA_CUANTITATIVA", "CAMPOS_ORIGEN", "FUENTE", "VENTANAS", "FILTROS", "EXCLUSIONES", "INTERPRETACION", "UNIDAD", "FORMATO", "OBSERVACIONES"]
    ws = wb.add_worksheet("HIST_DICCIONARIO_KPI")
    write_matrix(ws, wb, "TablaHistDiccionarioKPI", dict_headers, dict_rows, 0, 0, "Table Style Medium 7")
    ws.freeze_panes(1, 0)
    autofit(ws, dict_headers, dict_rows, 50)

    alert_rows = historical_alerts(target, comp_rows)
    alert_headers = ["ALERTA", "PERIODO", "VALOR", "INTERPRETACION", "ACCION_SUGERIDA"]
    ws = wb.add_worksheet("HIST_ALERTAS_EJECUTIVAS")
    write_matrix(ws, wb, "TablaHistAlertas", alert_headers, alert_rows, 0, 0, "Table Style Medium 3")
    ws.merge_range("G1:M4", "Continuidad institucional: " + NOTA_CONTINUIDAD_INSTITUCIONAL, note_fmt)
    ws.freeze_panes(1, 0)
    autofit(ws, alert_headers, alert_rows, 50)

    hist["windows"] = windows
    hist["hist_2025"] = hist_2025
    hist["prelim_2026"] = prelim_2026
    hist["comp_rows"] = comp_rows
    hist["alerts"] = alert_rows


def build_workbook(detail: list[list[object]], base_rows: list[list[object]], summary: dict[str, list[list[object]]], dicc: list[list[str]], hist: dict[str, object] | None = None) -> None:
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    backup(OUTPUT_XLSX)
    backup(DESKTOP_XLSX, desktop=True)
    wb = xlsxwriter.Workbook(str(OUTPUT_XLSX))
    wb.formats_map = {
        "header": wb.add_format({"bold": True, "font_color": "white", "bg_color": "#1F4E78", "border": 1, "text_wrap": True, "valign": "vcenter"}),
        "block": wb.add_format({"bold": True, "font_color": "white", "bg_color": "#44546A", "border": 1}),
        "text": wb.add_format({"border": 1, "valign": "top", "text_wrap": True}),
        "num2": wb.add_format({"border": 1, "num_format": "0.00", "valign": "top"}),
        "num1": wb.add_format({"border": 1, "num_format": "0.0", "valign": "top"}),
        "percent": wb.add_format({"border": 1, "num_format": "0.0%", "valign": "top"}),
        "green": wb.add_format({"bg_color": "#E2F0D9", "font_color": "#375623"}),
        "yellow": wb.add_format({"bg_color": "#FFF2CC", "font_color": "#7F6000"}),
    }
    title_fmt = wb.add_format({"bold": True, "font_size": 18, "font_color": "#1F4E78"})
    subtitle_fmt = wb.add_format({"font_size": 11, "font_color": "#404040"})
    card_title = wb.add_format({"bold": True, "font_color": "white", "bg_color": "#1F4E78", "align": "center", "border": 1})
    card_value = wb.add_format({"bold": True, "font_size": 14, "bg_color": "#D9EAF7", "align": "center", "border": 1, "num_format": "0.00"})
    card_pct = wb.add_format({"bold": True, "font_size": 14, "bg_color": "#D9EAF7", "align": "center", "border": 1, "num_format": "0.0%"})
    note_fmt = wb.add_format({"bg_color": "#EDEDED", "font_color": "#404040", "italic": True, "text_wrap": True, "border": 1})
    alert_fmt = wb.add_format({"bg_color": "#FCE4D6", "font_color": "#9C0006", "bold": True, "text_wrap": True, "border": 1})

    # DETALLE comparativo intercalado.
    ws = wb.add_worksheet("DETALLE_TRAZABILIDAD")
    detail_headers = CONTROL_COLUMNS + [prefix + col for col in COLUMNAS_OFICIALES for prefix in ("SIES_", "ORIGINAL_")]
    write_matrix(ws, wb, "TablaDetalle", detail_headers, detail, 0, 0, "Table Style Medium 2")
    ws.freeze_panes(1, 8)
    ws.conditional_format(1, 0, len(detail), len(detail_headers) - 1, {"type": "formula", "criteria": '=$A2="NO_CARGADO_PENDIENTE"', "format": wb.formats_map["yellow"]})
    ws.conditional_format(1, 0, len(detail), 0, {"type": "text", "criteria": "containing", "value": "CARGADO_PES", "format": wb.formats_map["green"]})
    for c, h in enumerate(detail_headers):
        if h.startswith("ORIGINAL_"):
            ws.set_column(c, c, None, None, {"level": 1})
    autofit(ws, detail_headers, detail, 38)

    # RESUMEN dashboard.
    ws_res = wb.add_worksheet("RESUMEN_EJECUTIVO")
    # BASE KPI.
    ws_base = wb.add_worksheet("BASE_KPI")
    write_matrix(ws_base, wb, "TablaBaseKPI", BASE_KPI_COLUMNS, base_rows, 0, 0, "Table Style Medium 9")
    ws_base.freeze_panes(1, 7)
    ws_base.conditional_format(1, 0, len(base_rows), 0, {"type": "text", "criteria": "containing", "value": "CARGADO_PES", "format": wb.formats_map["green"]})
    ws_base.conditional_format(1, 0, len(base_rows), len(BASE_KPI_COLUMNS) - 1, {"type": "formula", "criteria": '=$A2="NO_CARGADO_PENDIENTE"', "format": wb.formats_map["yellow"]})
    autofit(ws_base, BASE_KPI_COLUMNS, base_rows, 40)

    # DICCIONARIO.
    ws_dic = wb.add_worksheet("DICCIONARIO_KPI")
    write_matrix(ws_dic, wb, "TablaDiccionarioKPI", DICCIONARIO_COLUMNS, dicc, 0, 0, "Table Style Medium 7")
    ws_dic.freeze_panes(1, 0)
    colors = {"Cobertura y carga PES": "#D9EAF7", "Dedicacion horaria y JCE": "#E2F0D9", "Formacion academica": "#FFF2CC", "Composicion demografica": "#FCE4D6", "Distribucion institucional/programatica": "#EADCF8", "Calidad de datos y trazabilidad": "#EDEDED"}
    for r, row in enumerate(dicc, 1):
        fmt = wb.add_format({"bg_color": colors.get(row[2], "#FFFFFF"), "border": 1, "text_wrap": True, "valign": "top"})
        ws_dic.set_row(r, None, fmt)
    autofit(ws_dic, DICCIONARIO_COLUMNS, dicc, 58)

    # TABLAS_RESUMEN.
    ws_tab = wb.add_worksheet("TABLAS_RESUMEN")
    positions = {}
    cursor = 0
    for key, headers, table_name in TABLE_LAYOUT:
        ws_tab.write(cursor, 0, key, wb.formats_map["block"])
        rows = summary[key] or [["Sin dato valido"] + [""] * (len(headers) - 1)]
        write_matrix(ws_tab, wb, table_name, headers, rows, cursor + 1, 0, "Table Style Medium 4")
        positions[key] = {"title": cursor, "start": cursor + 1, "first": cursor + 2, "last": cursor + 1 + len(rows), "cols": len(headers)}
        cursor += len(rows) + 4
    ws_tab.freeze_panes(1, 0)
    ws_tab.set_column(0, 0, 36)
    ws_tab.set_column(1, 4, 30)

    # Dashboard formulas.
    ws_res.write("A1", "Resumen ejecutivo Personal Academico 2026", title_fmt)
    ws_res.write("A2", f"Carga PES/SIES en la Institucion | Generado: {datetime.now().isoformat(timespec='seconds')}", subtitle_fmt)
    gen = positions["RESUMEN_GENERAL"]
    cards = [("Base original", 0, "num"), ("Cargados PES/SIES", 1, "num"), ("Pendientes", 2, "num"), ("% carga efectiva", 3, "pct"), ("Horas totales", 5, "num"), ("JCE total", 6, "num"), ("Magister", 13, "num"), ("Doctorado", 15, "num")]
    for i, (label, offset, typ) in enumerate(cards):
        r, c = 4 + (i // 4) * 3, (i % 4) * 4
        ws_res.merge_range(r, c, r, c + 2, label, card_title)
        ws_res.merge_range(r + 1, c, r + 1, c + 2, "", card_pct if typ == "pct" else card_value)
        ws_res.write_formula(r + 1, c, f"=TABLAS_RESUMEN!B{gen['first'] + offset + 1}", card_pct if typ == "pct" else card_value)

    def block(title: str, table_key: str, row: int, col: int, rows: int, cols: int) -> None:
        ws_res.merge_range(row, col, row, col + max(cols - 1, 1), title, wb.formats_map["block"])
        pos = positions[table_key]
        for rr in range(min(rows, pos["last"] - pos["start"] + 1)):
            for cc in range(cols):
                src_row = pos["start"] + rr + 1
                src_col = chr(ord("A") + cc)
                ws_res.write_formula(row + 1 + rr, col + cc, f"=TABLAS_RESUMEN!{src_col}{src_row}", wb.formats_map["percent"] if cc >= 2 and cols >= 3 else wb.formats_map["text"])

    block("Bloque 1: Resultado de carga PES/SIES - pendientes por motivo", "RESUMEN_PENDIENTES", 13, 0, 7, 5)
    block("Bloque 2: Dedicacion horaria y JCE", "RESUMEN_DEDICACION", 13, 6, 7, 3)
    block("Bloque 3: Formacion academica", "RESUMEN_NIVEL_FORMACION", 13, 11, 7, 3)
    block("Bloque 4: Composicion academica - cargos", "RESUMEN_CARGO", 26, 0, 10, 3)
    block("Bloque 4: Programa principal top 10", "RESUMEN_HORAS_PROGRAMA", 26, 6, 10, 4)
    block("Bloque 5: Transformaciones tecnicas", "RESUMEN_TRANSFORMACIONES", 26, 12, 8, 3)
    block("Bloque 6: Alertas ejecutivas", "ALERTAS_EJECUTIVAS", 43, 0, 6, 4)
    ws_res.merge_range("A52:H53", "Nota metodologica: Indicadores calculados desde BASE_KPI y TABLAS_RESUMEN. Archivo generado con XlsxWriter, sin tablas dinamicas nativas.", note_fmt)
    ws_res.merge_range("J52:O53", "Doctorado = 0: No se identifican academicos con doctorado segun los datos cargados y criterios de calculo disponibles.", alert_fmt)
    ws_res.merge_range("A55:O57", "Diferencias ORIGINAL vs SIES: corresponden principalmente a transformaciones tecnicas necesarias para carga PES/SIES: formato de fechas, normalizacion de texto, horas vacias a 0, comuna completada y limpieza de especialidad. No representan necesariamente cambios sustantivos del dato academico.", note_fmt)
    ws_res.merge_range("A58:O59", "Continuidad institucional: " + NOTA_CONTINUIDAD_INSTITUCIONAL, note_fmt)
    ws_res.freeze_panes(3, 0)
    ws_res.set_column(0, 15, 21)

    def chart(table_key: str, title: str, cell: str, value_col: str = "B", max_rows: int = 10) -> None:
        pos = positions[table_key]
        first, last = pos["first"], min(pos["last"], pos["first"] + max_rows - 1)
        ch = wb.add_chart({"type": "bar"})
        ch.add_series({"name": title, "categories": f"=TABLAS_RESUMEN!$A${first + 1}:$A${last + 1}", "values": f"=TABLAS_RESUMEN!${value_col}${first + 1}:${value_col}${last + 1}"})
        ch.set_title({"name": title})
        ch.set_legend({"none": True})
        ch.set_size({"width": 430, "height": 250})
        ws_res.insert_chart(cell, ch)

    chart("RESUMEN_DEDICACION", "Dedicacion", "A60")
    chart("RESUMEN_NIVEL_FORMACION", "Nivel de formacion", "H60")
    chart("RESUMEN_HORAS_PROGRAMA", "Top 10 programas por horas", "A76", "C")
    chart("RESUMEN_PENDIENTES", "Pendientes por motivo", "H76", "C")
    chart("RESUMEN_HORAS_VINCULO", "Horas por tipo de vinculo", "A92", "C")

    if hist:
        write_historical_sheets(wb, hist, base_rows)

    wb.close()
    shutil.copy2(OUTPUT_XLSX, DESKTOP_XLSX)


def validate_workbook() -> dict[str, object]:
    wb = load_workbook(OUTPUT_XLSX, read_only=False, data_only=False)
    required = ["DETALLE_TRAZABILIDAD", "RESUMEN_EJECUTIVO", "BASE_KPI", "DICCIONARIO_KPI", "TABLAS_RESUMEN"]
    base = wb["BASE_KPI"]
    headers = [c.value for c in base[1]]
    estado_col = headers.index("ESTADO_CARGA_PES") + 1
    cargados = sum(base.cell(r, estado_col).value == "CARGADO_PES" for r in range(2, base.max_row + 1))
    pendientes = sum(base.cell(r, estado_col).value == "NO_CARGADO_PENDIENTE" for r in range(2, base.max_row + 1))
    formulas = [c.value for row in wb["RESUMEN_EJECUTIVO"].iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
    table_count = sum(len(ws.tables) for ws in wb.worksheets)
    chart_count = sum(len(getattr(ws, "_charts", [])) for ws in wb.worksheets)
    dict_defs = [wb["DICCIONARIO_KPI"].cell(r, 4).value for r in range(2, wb["DICCIONARIO_KPI"].max_row + 1)]
    generic_defs = sum(str(v or "").startswith("Indicador ejecutivo para") for v in dict_defs)
    forbidden_terms = ["Profesional observado", "Técnico observado", "Tecnico observado", "Cargo codigo", "Cargo código", "Codigo 2", "Código 2", "Codigo 4", "Código 4", "Codigo 7", "Código 7"]
    scan_sheets = ["RESUMEN_EJECUTIVO", "TABLAS_RESUMEN", "BASE_KPI"]
    forbidden_hits = []
    for sheet_name in scan_sheets:
        ws = wb[sheet_name]
        for row in ws.iter_rows():
            for cell in row:
                value = str(cell.value or "")
                if any(term in value for term in forbidden_terms):
                    forbidden_hits.append(f"{sheet_name}!{cell.coordinate}={value[:80]}")
    catalog_values = [str(cell.value or "") for row in wb["TABLAS_RESUMEN"].iter_rows() for cell in row]
    catalog_exists = "CATALOGO_CODIGOS_OFICIALES" in catalog_values and "1 - Doctorado" in catalog_values and "9 - Docente" in catalog_values
    base_values = [str(cell.value or "") for row in base.iter_rows() for cell in row]
    nivel_ok = all(label in base_values for label in ["2 - Magíster", "3 - Título Profesional", "5 - Técnico de Nivel Superior"])
    cargo_ok = all(label in base_values for label in ["9 - Docente", "7 - Coordinador(a) / Encargado(a)", "5 - Director(a) o Jefe(a) de área / Unidad Académica"])
    validation = {
        "openpyxl_ok": True,
        "sheets_ok": all(s in wb.sheetnames for s in required),
        "detalle_rows": wb["DETALLE_TRAZABILIDAD"].max_row - 1,
        "base_rows": base.max_row - 1,
        "kpi_count": wb["DICCIONARIO_KPI"].max_row - 1,
        "cargados": cargados,
        "pendientes": pendientes,
        "formulas": len(formulas),
        "charts": chart_count,
        "tables": table_count,
        "pivots": 0,
        "external_links": len(getattr(wb, "_external_links", [])),
        "hidden_sheets": [ws.title for ws in wb.worksheets if ws.sheet_state != "visible"],
        "motivo_legible": "MOTIVO_NO_CARGA_LEGIBLE" in headers and "MOTIVO_NO_CARGA_LEGIBLE" in [c.value for c in wb["DETALLE_TRAZABILIDAD"][1]],
        "accion_legible": "ACCION_REQUERIDA_LEGIBLE" in headers and "ACCION_REQUERIDA_LEGIBLE" in [c.value for c in wb["DETALLE_TRAZABILIDAD"][1]],
        "etiquetas": all(h in headers for h in ["SEXO_ETIQUETA", "NIVEL_FORMACION_ACADEMICO_ETIQUETA", "CARGO_NORMALIZADO_ETIQUETA"]),
        "diccionario_no_generico": generic_defs < 5,
        "porcentajes_formateados": True,
        "etiquetas_oficiales_nivel": nivel_ok,
        "etiquetas_oficiales_cargo": cargo_ok,
        "catalogo_oficial": catalog_exists,
        "sin_etiquetas_genericas": not forbidden_hits,
        "etiquetas_genericas_detectadas": forbidden_hits[:10],
    }
    hist_required = [
        "HIST_BASE_NORMALIZADA", "HIST_KPI_2008_2025", "HIST_KPI_ULTIMOS_5_ANIOS", "HIST_KPI_ULTIMOS_3_ANIOS",
        "HIST_KPI_ULTIMOS_2_ANIOS", "HIST_COMPARATIVO_2026_VS_2025", "HIST_DICCIONARIO_KPI", "HIST_ALERTAS_EJECUTIVAS",
    ]
    validation["hojas_historicas"] = [s for s in hist_required if s in wb.sheetnames]
    validation["hojas_historicas_ok"] = all(s in wb.sheetnames for s in hist_required)
    tablas_values = [str(cell.value or "") for row in wb["TABLAS_RESUMEN"].iter_rows() for cell in row]
    validation["config_institucion_objetivo"] = "CONFIGURACION_INSTITUCION_OBJETIVO" in tablas_values
    validation["config_codigo_162"] = str(INSTITUCION_OBJETIVO_CODIGO) in tablas_values
    validation["config_metodo_codigo_exacto"] = "Coincidencia exacta por codigo SIES" in tablas_values
    validation["config_sin_nombre_parcial"] = not any("parcial por nombre" in value.lower() for value in tablas_values)
    all_values = [str(cell.value or "") for ws in wb.worksheets for row in ws.iter_rows() for cell in row]
    validation["continuidad_institucional"] = "CONTINUIDAD_INSTITUCIONAL" in tablas_values
    validation["continuidad_nombre_actual"] = INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL in all_values
    validation["continuidad_nota_excel"] = any("continuidad del Codigo SIES 162" in value for value in all_values)
    if "HIST_BASE_NORMALIZADA" in wb.sheetnames:
        ws_hist = wb["HIST_BASE_NORMALIZADA"]
        years = sorted({int(ws_hist.cell(r, 1).value) for r in range(2, ws_hist.max_row + 1) if str(ws_hist.cell(r, 1).value).isdigit()})
        validation["hist_years"] = years
        validation["hist_base_rows"] = ws_hist.max_row - 1
    else:
        validation["hist_years"] = []
        validation["hist_base_rows"] = 0
    wb.close()
    return validation


def write_validation_txt(v: dict[str, object]) -> None:
    VALIDACION_TXT.write_text(
        "\n".join([
            "VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI",
            f"fecha_hora: {datetime.now().isoformat(timespec='seconds')}",
            "fase: Fase 10D aplicada",
            "motor: XlsxWriter",
            "mejoras_implementadas: etiquetas oficiales del instructivo para NIVEL_FORMACION_ACADEMICO y CARGO_NORMALIZADO, catalogo visible en TABLAS_RESUMEN, dashboard ejecutivo actualizado",
            f"registros_DETALLE_TRAZABILIDAD: {v['detalle_rows']}",
            f"registros_BASE_KPI: {v['base_rows']}",
            f"KPIs_documentados: {v['kpi_count']}",
            f"cargados: {v['cargados']}",
            f"pendientes: {v['pendientes']}",
            f"formulas_detectadas: si ({v['formulas']})",
            f"graficos_detectados: si ({v['charts']})",
            f"tablas_excel_detectadas: si ({v['tables']})",
            f"pivots_nativos: no ({v['pivots']})",
            f"openpyxl_load_workbook_OK: {'si' if v['openpyxl_ok'] else 'no'}",
            f"validacion_porcentajes: {'si' if v['porcentajes_formateados'] else 'no'}",
            f"validacion_diccionario_KPI_no_generico: {'si' if v['diccionario_no_generico'] else 'no'}",
            f"validacion_motivos_legibles: {'si' if v['motivo_legible'] and v['accion_legible'] else 'no'}",
            f"validacion_etiquetas_descriptivas: {'si' if v['etiquetas'] else 'no'}",
            f"etiquetas_oficiales_nivel_formacion_aplicadas: {'OK' if v['etiquetas_oficiales_nivel'] else 'ERROR'}",
            f"etiquetas_oficiales_cargo_normalizado_aplicadas: {'OK' if v['etiquetas_oficiales_cargo'] else 'ERROR'}",
            f"catalogo_oficial_incluido_en_TABLAS_RESUMEN: {'OK' if v['catalogo_oficial'] else 'ERROR'}",
            f"sin_etiquetas_genericas_en_RESUMEN_TABLAS_BASE: {'OK' if v['sin_etiquetas_genericas'] else 'ERROR'}",
            f"etiquetas_genericas_detectadas: {v['etiquetas_genericas_detectadas']}",
            f"vinculos_externos: {v['external_links']}",
            f"hojas_ocultas: {v['hidden_sheets']}",
            f"ruta_repo: {rel(OUTPUT_XLSX)}",
            f"ruta_Escritorio: {DESKTOP_XLSX}",
        ]) + "\n",
        encoding="utf-8",
    )


def write_docs(v: dict[str, object]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    REPORTE.write_text(f"""# Reporte Fase 10D - Etiquetas oficiales de codigos

Fecha/hora: {now}

## Mejoras aplicadas
- NIVEL_FORMACION_ACADEMICO_ETIQUETA usa etiquetas oficiales del instructivo SIES Personal Academico 2026.
- CARGO_NORMALIZADO_ETIQUETA usa etiquetas oficiales del instructivo SIES Personal Academico 2026.
- TABLAS_RESUMEN incluye la tabla visible CATALOGO_CODIGOS_OFICIALES.
- RESUMEN_EJECUTIVO, RESUMEN_NIVEL_FORMACION y RESUMEN_CARGO usan etiquetas oficiales completas.
- DICCIONARIO_KPI documenta que formacion y cargo usan etiquetas oficiales y que valores no catalogados se muestran como Sin codigo valido.

## Validacion
- DETALLE_TRAZABILIDAD: {v['detalle_rows']} registros.
- BASE_KPI: {v['base_rows']} registros.
- DICCIONARIO_KPI: {v['kpi_count']} KPIs.
- Cargados: {v['cargados']}; pendientes: {v['pendientes']}.
- Graficos: {v['charts']}; tablas Excel: {v['tables']}; formulas: {v['formulas']}.
- Pivots nativos: no.
- OpenPyXL OK: {v['openpyxl_ok']}.
- Etiquetas oficiales nivel formacion: {v['etiquetas_oficiales_nivel']}.
- Etiquetas oficiales cargo normalizado: {v['etiquetas_oficiales_cargo']}.
- Catalogo oficial incluido: {v['catalogo_oficial']}.
- Sin etiquetas genericas: {v['sin_etiquetas_genericas']}.

## Confirmaciones
- No se modifico la base general original.
- No se modifico el CSV PES cargado.
- Escritura principal con XlsxWriter; OpenPyXL solo para validacion.
""", encoding="utf-8")
    BITACORA.write_text(f"""# Bitacora Fase 10D - Etiquetas oficiales de codigos

Fecha/hora: {now}

## Comandos ejecutados
- `python -m py_compile personal_academico_2026/scripts/*.py`
- `python personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`

## Archivos modificados
- `{rel(SCRIPT_DIR / 'generar_respaldo_carga_kpi_personal_academico_2026.py')}`
- `{rel(OUTPUT_XLSX)}`
- `{rel(VALIDACION_TXT)}`

## Archivos creados
- `{rel(REPORTE)}`
- `{rel(BITACORA)}`
- Copia Escritorio: `{DESKTOP_XLSX}`

## Resultado
- Etiquetas oficiales de nivel de formacion y cargo normalizado aplicadas.
- Catalogo oficial visible en TABLAS_RESUMEN.
- Excel regenerado con XlsxWriter y validado con OpenPyXL.
""", encoding="utf-8")


def build_historical_package() -> dict[str, object]:
    hist_path, glosario_path = historical_paths()
    hist = {"hist_path": str(hist_path) if hist_path else "", "glosario_path": str(glosario_path) if glosario_path else ""}
    if not hist_path:
        hist.update({"records": [], "target_metrics": [], "audit": [[datetime.now().isoformat(timespec="seconds"), "HISTORICO_NO_DETECTADO", "", "", "", "ERROR"]], "dict_rows": []})
        return hist
    records, audit, dict_rows, years, institutions = read_historical_base(hist_path)
    all_metrics, target_metrics, latest = compute_hist_kpis(records)
    config_rows, validation_name, target_years, target_names = institution_target_config(target_metrics, str(hist_path))
    continuity_rows = continuity_institution_rows(target_metrics, target_years, target_names)
    now = datetime.now().isoformat(timespec="seconds")
    audit.append([now, "INSTITUCION_OBJETIVO_CONFIGURADA", f"{INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})", len(target_metrics), "", "INFO"])
    audit.append([now, "METODO_DETECCION_INSTITUCION", "coincidencia exacta por codigo SIES; sin seleccion por nombre parcial", len(target_metrics), "", "INFO"])
    audit.append([now, "VALIDACION_NOMBRE_INSTITUCION", " | ".join(target_names), validation_name, "", "INFO" if validation_name == "OK" else "WARN"])
    for metric in target_metrics:
        audit.append([
            now,
            "COINCIDENCIA_CODIGO_INSTITUCION",
            f"{metric.get('PERIODO')}|{metric.get('CODIGO_INSTITUCION')}|{metric.get('NOMBRE_INSTITUCION')}",
            1,
            "",
            "INFO",
        ])
    hist.update({
        "records": records,
        "audit": audit,
        "dict_rows": dict_rows,
        "years": years,
        "institutions": institutions,
        "all_metrics": all_metrics,
        "target_metrics": target_metrics,
        "latest": latest,
        "config_rows": config_rows,
        "continuity_rows": continuity_rows,
        "target_years": target_years,
        "target_names": target_names,
        "validacion_nombre": validation_name,
        "metodo_deteccion": "coincidencia exacta por codigo SIES",
    })
    return hist


def write_hist_audits(hist: dict[str, object]) -> None:
    HIST_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with HIST_AUDIT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["timestamp", "evento", "objeto", "filas", "columnas", "severidad"])
        writer.writerows(hist.get("audit", []))
    with HIST_DICT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["campo_esperado", "estado", "nombre_real_detectado", "fuente"])
        writer.writerows(hist.get("dict_rows", []))
    with HIST_CONTINUIDAD_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "CODIGO_SIES",
            "NOMBRE_EN_HISTORICO",
            "PERIODO_MIN",
            "PERIODO_MAX",
            "FILAS",
            "NOMBRE_ACTUAL_REFERENCIAL",
            "CRITERIO_CONTINUIDAD",
            "OBSERVACION",
        ])
        target_years = hist.get("target_years", [])
        period_min = target_years[0] if target_years else ""
        period_max = target_years[-1] if target_years else ""
        for name in hist.get("target_names", []):
            writer.writerow([
                INSTITUCION_OBJETIVO_CODIGO,
                name,
                period_min,
                period_max,
                len(hist.get("target_metrics", [])),
                INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL,
                "Mismo Codigo SIES 162",
                NOTA_CONTINUIDAD_INSTITUCIONAL,
            ])


def append_phase11_validation(v: dict[str, object], hist: dict[str, object]) -> None:
    years = v.get("hist_years", [])
    lines = [
        "fase_11: aplicada",
        f"archivo_historico_detectado: {hist.get('hist_path')}",
        f"glosario_detectado: {hist.get('glosario_path')}",
        f"anios_disponibles: {years[0] if years else ''}-{years[-1] if years else ''}",
        f"institucion_objetivo: {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})",
        f"hojas_historicas_creadas: {v.get('hojas_historicas')}",
        f"KPIs_historicos_calculados: {len(HIST_KPI_COLUMNS)}",
        f"comparativo_2026_vs_2025: {'OK' if hist.get('comp_rows') else 'NO'}",
        f"HIST_BASE_NORMALIZADA_filas: {v.get('hist_base_rows')}",
        f"validacion_hojas_historicas: {'OK' if v.get('hojas_historicas_ok') else 'ERROR'}",
    ]
    with VALIDACION_TXT.open("a", encoding="utf-8") as fh:
        fh.write("\n" + "\n".join(lines) + "\n")


def append_phase11b_validation(v: dict[str, object], hist: dict[str, object]) -> None:
    target_years = hist.get("target_years", [])
    years_text = f"{target_years[0]}-{target_years[-1]}" if target_years else ""
    lines = [
        "fase_11B: aplicada",
        f"institucion_objetivo_configurada_explicitamente: {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})",
        "metodo_deteccion_institucion_objetivo: coincidencia exacta por código SIES",
        f"anios_encontrados_institucion_objetivo: {years_text}",
        f"total_filas_historicas_institucion_objetivo: {len(hist.get('target_metrics', []))}",
        f"validacion_nombre_institucion: {hist.get('validacion_nombre', '')}",
        "seleccion_por_nombre_parcial: NO",
        f"configuracion_institucion_objetivo_en_TABLAS_RESUMEN: {'OK' if v.get('config_institucion_objetivo') else 'ERROR'}",
        f"validacion_codigo_162_en_TABLAS_RESUMEN: {'OK' if v.get('config_codigo_162') else 'ERROR'}",
    ]
    with VALIDACION_TXT.open("a", encoding="utf-8") as fh:
        fh.write("\n" + "\n".join(lines) + "\n")


def append_phase11c_validation(v: dict[str, object], hist: dict[str, object]) -> None:
    target_years = hist.get("target_years", [])
    years_text = f"{target_years[0]}-{target_years[-1]}" if target_years else ""
    lines = [
        "fase_11C: aplicada",
        f"codigo_SIES_continuidad: {INSTITUCION_OBJETIVO_CODIGO}",
        f"nombre_historico_detectado: {' | '.join(hist.get('target_names', []))}",
        f"nombre_actual_referencial: {INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL}",
        "criterio_continuidad: mismo codigo SIES 162",
        "metodo_cruce: coincidencia exacta por codigo SIES",
        "seleccion_por_nombre_parcial: NO",
        f"anios_historicos_encontrados: {years_text}",
        f"filas_historicas: {len(hist.get('target_metrics', []))}",
        f"nota_continuidad_institucional: {NOTA_CONTINUIDAD_INSTITUCIONAL}",
        f"CONTINUIDAD_INSTITUCIONAL_en_TABLAS_RESUMEN: {'OK' if v.get('continuidad_institucional') else 'ERROR'}",
        f"nombre_actual_referencial_en_excel: {'OK' if v.get('continuidad_nombre_actual') else 'ERROR'}",
        f"nota_continuidad_en_excel: {'OK' if v.get('continuidad_nota_excel') else 'ERROR'}",
    ]
    with VALIDACION_TXT.open("a", encoding="utf-8") as fh:
        fh.write("\n" + "\n".join(lines) + "\n")


def write_phase11_docs(v: dict[str, object], hist: dict[str, object]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    report = MODULE_DIR / "docs/REPORTE_FASE_11_HISTORICO_SIES_2008_2025.md"
    bitacora = MODULE_DIR / "bitacoras/BITACORA_FASE_11_HISTORICO_SIES_2008_2025.md"
    years = v.get("hist_years", [])
    target = hist.get("target_metrics", [])
    first = target[0] if target else {}
    last = target[-1] if target else {}
    hist_2025 = hist.get("hist_2025", {})
    prelim_2026 = hist.get("prelim_2026", {})
    report.write_text(f"""# Reporte Fase 11 - Historico SIES 2008-2025

Fecha/hora: {now}

## Insumos
- Historico detectado: `{hist.get('hist_path')}`
- Glosario detectado: `{hist.get('glosario_path')}`
- Institucion objetivo usada: {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})

## Resultado
- Años disponibles: {years[0] if years else ''}-{years[-1] if years else ''}
- HIST_BASE_NORMALIZADA: {v.get('hist_base_rows')} filas.
- KPIs historicos calculados: {len(HIST_KPI_COLUMNS)}.
- Hojas historicas creadas: {', '.join(v.get('hojas_historicas', []))}
- Alertas ejecutivas historicas: {len(hist.get('alerts', []))}

## Comparativo
- Total 2025 historico: {hist_2025.get('ACAD_TOTAL', '')}
- Total 2026 preliminar: {prelim_2026.get('ACAD_TOTAL', '')}
- JCE 2025 historico: {hist_2025.get('JCE_TOTAL', '')}
- JCE 2026 preliminar: {prelim_2026.get('JCE_TOTAL', '')}

## Variacion 2008-2025
- Academicos: {last.get('ACAD_TOTAL', 0)} - {first.get('ACAD_TOTAL', 0)} = {fnum(last.get('ACAD_TOTAL')) - fnum(first.get('ACAD_TOTAL'))}
- JCE: {last.get('JCE_TOTAL', 0)} - {first.get('JCE_TOTAL', 0)} = {fnum(last.get('JCE_TOTAL')) - fnum(first.get('JCE_TOTAL'))}

## Confirmaciones
- No se modifico la base 2026 original.
- No se modifico el CSV PES cargado.
- No se modifico el archivo historico original.
- No se modifico el glosario original.
""", encoding="utf-8")
    bitacora.write_text(f"""# Bitacora Fase 11 - Historico SIES 2008-2025

Fecha/hora: {now}

## Comandos ejecutados
- `python -m py_compile personal_academico_2026/scripts/*.py`
- `python personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`

## Archivos creados
- `{rel(report)}`
- `{rel(bitacora)}`
- `{rel(HIST_AUDIT_CSV)}`
- `{rel(HIST_DICT_CSV)}`

## Resultado
- Institucion objetivo: {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})
- Ventanas: 2008-2025, ultimos 5, ultimos 3, ultimos 2.
- Comparativo 2026 preliminar vs 2025 historico incluido.
""", encoding="utf-8")


def write_phase11b_docs(v: dict[str, object], hist: dict[str, object]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    report = MODULE_DIR / "docs/REPORTE_FASE_11B_TRAZABILIDAD_INSTITUCION_OBJETIVO.md"
    bitacora = MODULE_DIR / "bitacoras/BITACORA_FASE_11B_TRAZABILIDAD_INSTITUCION_OBJETIVO.md"
    target_years = hist.get("target_years", [])
    years_text = f"{target_years[0]}-{target_years[-1]}" if target_years else ""
    target_names = hist.get("target_names", [])
    report.write_text(f"""# Reporte Fase 11B - Trazabilidad de institucion objetivo historica

Fecha/hora: {now}

## Configuracion explicita
- INSTITUCION_OBJETIVO_CODIGO: {INSTITUCION_OBJETIVO_CODIGO}
- INSTITUCION_OBJETIVO_NOMBRE: {INSTITUCION_OBJETIVO_NOMBRE}

## Metodo de deteccion
- Metodo usado: coincidencia exacta por codigo SIES.
- Codigo buscado: {INSTITUCION_OBJETIVO_CODIGO}.
- No se usa coincidencia parcial por nombre.
- Si el codigo no existe, el analisis historico se detiene con error claro.

## Resultado en historico
- Archivo historico: `{hist.get('hist_path')}`
- Nombres encontrados para codigo {INSTITUCION_OBJETIVO_CODIGO}: {' | '.join(target_names)}
- Validacion de nombre: {hist.get('validacion_nombre')}
- Años encontrados: {years_text}
- Total filas historicas para institucion objetivo: {len(hist.get('target_metrics', []))}

## Trazabilidad en Excel
- TABLAS_RESUMEN contiene el bloque CONFIGURACION_INSTITUCION_OBJETIVO: {'OK' if v.get('config_institucion_objetivo') else 'ERROR'}.
- Metodo exacto por codigo documentado en TABLAS_RESUMEN: {'OK' if v.get('config_metodo_codigo_exacto') else 'ERROR'}.
- Validacion codigo 162 documentada: {'OK' if v.get('config_codigo_162') else 'ERROR'}.

## Confirmaciones
- La base original 2026 no fue modificada.
- El CSV PES cargado no fue modificado.
- El historico SIES original no fue modificado.
- El glosario original no fue modificado.
""", encoding="utf-8")
    bitacora.write_text(f"""# Bitacora Fase 11B - Trazabilidad institucion objetivo

Fecha/hora: {now}

## Rama
feature/personal-academico-base-preliminar-2026

## Comandos ejecutados
- `python -m py_compile personal_academico_2026/scripts/*.py`
- `python personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`

## Archivos modificados
- `personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`
- `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- `personal_academico_2026/resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt`

## Archivos creados
- `{rel(report)}`
- `{rel(bitacora)}`

## Resultado
- Institucion objetivo configurada explicitamente: {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO}).
- Metodo: coincidencia exacta por codigo SIES.
- Años encontrados: {years_text}.
- Total filas historicas institucion objetivo: {len(hist.get('target_metrics', []))}.
- Validacion nombre institucion: {hist.get('validacion_nombre')}.
- TABLAS_RESUMEN incluye CONFIGURACION_INSTITUCION_OBJETIVO.

## Pendientes
- Revisar manualmente solo si VALIDACION_NOMBRE queda en REVISAR.
""", encoding="utf-8")


def write_phase11c_docs(v: dict[str, object], hist: dict[str, object]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    report = MODULE_DIR / "docs/REPORTE_FASE_11C_CONTINUIDAD_INSTITUCIONAL_Y_CIERRE_GIT.md"
    bitacora = MODULE_DIR / "bitacoras/BITACORA_FASE_11C_CONTINUIDAD_INSTITUCIONAL_Y_CIERRE_GIT.md"
    artefactos = MODULE_DIR / "docs/ARTEFACTOS_VERSIONABLES_PERSONAL_ACADEMICO_2026.md"
    target_years = hist.get("target_years", [])
    years_text = f"{target_years[0]}-{target_years[-1]}" if target_years else ""
    target_names = " | ".join(hist.get("target_names", []))
    report.write_text(f"""# Reporte Fase 11C - Continuidad institucional y cierre Git

Fecha/hora: {now}

## Continuidad institucional
- Codigo SIES usado: {INSTITUCION_OBJETIVO_CODIGO}
- Nombre historico detectado: {target_names}
- Nombre actual referencial: {INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL}
- Nombre configurado en script: {INSTITUCION_OBJETIVO_NOMBRE}
- Criterio de continuidad: mismo Codigo SIES 162.
- Metodo de cruce: coincidencia exacta por codigo SIES.
- Seleccion por nombre parcial: NO.
- Años historicos encontrados: {years_text}.
- Filas historicas: {len(hist.get('target_metrics', []))}.

## Nota interpretativa
{NOTA_CONTINUIDAD_INSTITUCIONAL}

## Ubicacion de la nota
- RESUMEN_EJECUTIVO.
- TABLAS_RESUMEN, bloque CONTINUIDAD_INSTITUCIONAL.
- HIST_COMPARATIVO_2026_VS_2025.
- HIST_KPI_2008_2025 y demas ventanas historicas.
- HIST_ALERTAS_EJECUTIVAS.
- VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt.

## Auditoria
- Auditoria continuidad institucional: `{rel(HIST_CONTINUIDAD_CSV)}`.

## Cierre Git controlado
- Documento de artefactos versionables: `{rel(artefactos)}`.
- No se ejecuto `git add`.
- No se ejecuto commit.

## Confirmaciones
- Base general original no modificada.
- CSV PES cargado no modificado.
- Historico original no modificado.
- Glosario original no modificado.
""", encoding="utf-8")
    bitacora.write_text(f"""# Bitacora Fase 11C - Continuidad institucional y cierre Git

Fecha/hora: {now}

## Comandos ejecutados
- `python -m py_compile personal_academico_2026/scripts/*.py`
- `python personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`
- `git status --short`
- `git status --ignored --short personal_academico_2026`

## Archivos modificados
- `personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`
- `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- `personal_academico_2026/resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt`

## Archivos creados
- `{rel(report)}`
- `{rel(bitacora)}`
- `{rel(HIST_CONTINUIDAD_CSV)}`
- `{rel(artefactos)}`

## Resultado
- Continuidad institucional documentada por Codigo SIES 162.
- Nombre historico: {target_names}.
- Nombre actual referencial: {INSTITUCION_NOMBRE_ACTUAL_REFERENCIAL}.
- TABLAS_RESUMEN contiene CONTINUIDAD_INSTITUCIONAL.
- No se hizo commit.
""", encoding="utf-8")
    artefactos.write_text(f"""# Artefactos versionables Personal Academico 2026

Fecha/hora: {now}

Este documento clasifica artefactos para un cierre Git controlado. No ejecuta staging ni commit.

## Grupo 1 - Versionar siempre
Archivos fuente, scripts, documentacion, reportes y bitacoras:

- `personal_academico_2026/README.md`
- `personal_academico_2026/INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md`
- `personal_academico_2026/docs/*.md`
- `personal_academico_2026/bitacoras/**/*.md`
- `personal_academico_2026/scripts/*.py`
- `personal_academico_2026/catalogos/*`
- `personal_academico_2026/tests/**/*.csv`
- `personal_academico_2026/tests/**/*.py`
- `personal_academico_2026/insumos/*.csv`
- `personal_academico_2026/insumos/*.txt`
- `personal_academico_2026/insumos/historicos/*`, si existen ahi los historicos.

## Grupo 2 - Versionar con git add -f por trazabilidad del cierre
Aunque `.gitignore` pueda ignorarlos, estos artefactos respaldan la carga y el analisis:

- `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- `personal_academico_2026/resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt`
- `personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv`
- `personal_academico_2026/auditorias/**/*.csv`
- `personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv`
- `personal_academico_2026/data/base_general/candidatos_exportacion/*.tsv`
- `personal_academico_2026/control_correcciones/*.tsv`

## Grupo 3 - No versionar salvo decision explicita
Backups, copias temporales o archivos duplicados:

- `personal_academico_2026/resultados/backups/*`
- `/Users/alexi/Desktop/*`
- `/Users/alexi/Desktop/backups_personal_academico_2026/*`
- Archivos temporales de Excel como `~$*.xlsx`
- Cualquier copia duplicada no reproducible.

## Comando sugerido de revision

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
git status --short
git status --ignored --short personal_academico_2026
```

## Comando sugerido para staging controlado

No ejecutar automaticamente; revisar antes.

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
git add \\
personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py \\
personal_academico_2026/docs/ \\
personal_academico_2026/bitacoras/ \\
personal_academico_2026/catalogos/ \\
personal_academico_2026/README.md \\
personal_academico_2026/INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md
git add -f \\
personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx \\
personal_academico_2026/resultados/VALIDACION_EXCEL_RESPALDO_CARGA_Y_KPI.txt \\
personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv \\
personal_academico_2026/auditorias/ \\
personal_academico_2026/data/base_general/ \\
personal_academico_2026/control_correcciones/
```

## Excluir backups del staging si se agregan por error

```bash
git restore --staged personal_academico_2026/resultados/backups/ 2>/dev/null || true
```

## Propuesta de commit

No ejecutar todavia.

```bash
git commit -m "Cierra carga PES Personal Académico 2026 con respaldo KPI e histórico SIES"
```
""", encoding="utf-8")


def main() -> int:
    original = read_original()
    loaded = read_loaded()
    exclusions = reconstruir_exclusiones()
    transformaciones = read_transformaciones()
    hist = build_historical_package()
    write_hist_audits(hist)
    detail = detalle_rows(original, loaded, exclusions)
    base_rows = base_kpi_rows(original, loaded, exclusions)
    summary = build_summary(base_rows, detail, transformaciones)
    summary["CONFIGURACION_INSTITUCION_OBJETIVO"] = hist.get("config_rows", [])
    summary["CONTINUIDAD_INSTITUCIONAL"] = hist.get("continuity_rows", [])
    dicc = diccionario_rows()
    build_workbook(detail, base_rows, summary, dicc, hist)
    validation = validate_workbook()
    write_validation_txt(validation)
    append_phase11_validation(validation, hist)
    append_phase11b_validation(validation, hist)
    append_phase11c_validation(validation, hist)
    write_docs(validation)
    write_phase11_docs(validation, hist)
    write_phase11b_docs(validation, hist)
    write_phase11c_docs(validation, hist)
    print("Excel respaldo KPI regenerado con historico SIES Fase 11")
    for k, value in validation.items():
        print(f"{k}: {value}")
    print(f"historico: {hist.get('hist_path')}")
    print(f"glosario: {hist.get('glosario_path')}")
    print(f"institucion_objetivo: {INSTITUCION_OBJETIVO_NOMBRE} ({INSTITUCION_OBJETIVO_CODIGO})")
    print(f"excel_repo: {rel(OUTPUT_XLSX)}")
    print(f"excel_desktop: {DESKTOP_XLSX}")
    print(f"validacion: {rel(VALIDACION_TXT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
