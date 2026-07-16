#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hito 66: correccion trazable del dictamen post hito 64 para columnas 16-19
del archivo 5809 Matricula Avance Curricular.

Este script no modifica fuentes originales, no corrige datos, no genera
SIES_READY, no genera archivo de carga y no recalcula 20-21. Solo consolida
evidencia documental, datos observados y decisiones pendientes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


PROCESO = "Avance Curricular SIES 2026"
SUBPROYECTO = "Correccion trazable del dictamen post hito 64 para columnas 16-19 del archivo 5809 Matricula Avance Curricular"
ANIO_PROCESO = 2026
ANIO_REFERENCIA = 2025
ESTADO = "CORRECCION_DICTAMEN_GOBERNADA"
DECLARACION_CARGA = "NO_LISTO_PARA_CARGA"

REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BASE_OUT = REPO / "avance_curricular_2026" / "66_correccion_dictamen_post_h64_16_19_5809"

INSTRUCTIVO = REPO / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/Instructivo_Avance Curricular SIES - 2026.txt"
H51_DIR = REPO / "avance_curricular_2026/51_gobernanza_integral_inputs_columnas_transformaciones_5809/GOBERNANZA_INTEGRAL_5809_20260708_144544"
H51_XLSX = H51_DIR / "GOBERNANZA_INTEGRAL_INPUTS_COLUMNAS_TRANSFORMACIONES_5809.xlsx"
H52_DIR = REPO / "avance_curricular_2026/52_validador_gobernanza_precalculo_5809/VALIDADOR_GOBERNANZA_PRECALCULO_5809_20260708_182553_H59"
H52_XLSX = H52_DIR / "VALIDACION_GOBERNANZA_PRECALCULO_5809.xlsx"
H55_DIR = REPO / "avance_curricular_2026/55_auditoria_diferencia_16_18_multiple_5809/AUDITORIA_DIF_16_18_MULTIPLE_20260708_172433"
H56_DIR = REPO / "avance_curricular_2026/56_auditoria_sin_registros_2025_codcli_lista_5809/AUDITORIA_SIN_REGISTROS_2025_CODCLI_LISTA_20260708_173435"
H56_XLSX = H56_DIR / "AUDITORIA_SIN_REGISTROS_2025_CODCLI_LISTA_5809.xlsx"
H59_DIR = REPO / "avance_curricular_2026/59_paquete_validacion_humana_16_19_5809/PAQUETE_VALIDACION_HUMANA_16_19_20260708_182553"
H59_XLSX = H59_DIR / "PAQUETE_VALIDACION_HUMANA_16_19_5809.xlsx"
H61_DIR = REPO / "avance_curricular_2026/61_terminal_revision_218_convalidacion_homologacion_19_5809/REVISION_218_CONVALIDACION_HOMOLOGACION_19_20260708_220755"
H61_XLSX = H61_DIR / "REVISION_218_CONVALIDACION_HOMOLOGACION_19_5809.xlsx"
H62_DIR = REPO / "avance_curricular_2026/62_decision_funcional_candidata_columna_19_solo_a_5809/DECISION_FUNCIONAL_CANDIDATA_19_SOLO_A_20260708_220943"
H62_XLSX = H62_DIR / "DECISION_FUNCIONAL_CANDIDATA_COLUMNA_19_SOLO_A_5809.xlsx"
H63_DIR = REPO / "avance_curricular_2026/63_terminal_revision_38_decision_funcional_restante_5809/REVISION_38_DECISION_FUNCIONAL_RESTANTE_20260708_221125"
H63_XLSX = H63_DIR / "REVISION_38_DECISION_FUNCIONAL_RESTANTE_5809.xlsx"
H64_DIR = REPO / "avance_curricular_2026/64_exploracion_gobernanza_transversal_mu_avance/EXPLORACION_GOBERNANZA_TRANSVERSAL_MU_AVANCE_20260708_221914"
H64_XLSX = H64_DIR / "EXPLORACION_GOBERNANZA_TRANSVERSAL_MU_AVANCE.xlsx"
H65_DIR = REPO / "avance_curricular_2026/65_consolidado_post_h64_decisiones_bloqueos_16_19_5809/CONSOLIDADO_POST_H64_16_19_20260708_223521"
H65_XLSX = H65_DIR / "CONSOLIDADO_POST_H64_DECISIONES_BLOQUEOS_16_19_5809.xlsx"
H65_MD = H65_DIR / "INFORME_CONSOLIDADO_POST_H64_DECISIONES_BLOQUEOS_16_19_5809.md"

OUTPUT_FILES = {
    "excel": "CORRECCION_DICTAMEN_POST_H64_16_19_5809.xlsx",
    "informe": "INFORME_CORRECCION_DICTAMEN_POST_H64_16_19_5809.md",
    "manifest": "manifest_correccion_dictamen_post_h64_16_19_5809.json",
    "script": "correccion_dictamen_post_h64_16_19_5809.py",
    "borrador": "BORRADOR_DECISION_FUNCIONAL_16_19_POST_H64.md",
    "prompt_periodo": "PROMPT_GOBERNANZA_PERIODO_RAW_5809.md",
}

SHEETS = OrderedDict(
    [
        ("00_DICTAMEN_GLOBAL", "00_DICTAMEN_GLOBAL"),
        ("01_EXTRACTOS_INSTRUCTIVO", "01_EXTRACTOS_INSTRUCTIVO"),
        ("02_BLOQUE_218_COLUMNA_19", "02_BLOQUE_218_COLUMNA_19"),
        ("03_BLOQUE_21_ESTADO_ACADEMICO", "03_BLOQUE_21_ESTADO_ACADEMICO"),
        ("04_BLOQUE_17_PERIODO_RAW", "04_BLOQUE_17_PERIODO_RAW"),
        ("05_COMPARACION_ANTES_DESPUES", "05_COMPARACION_ANTES_DESPUES"),
        ("06_NIVELES_RESPALDO", "06_NIVELES_RESPALDO"),
        ("07_PROMPT_GOBERNANZA_PERIODO_RAW", "07_PROMPT_GOBERNANZA_PERIODO"),
        ("08_BORRADOR_DECISION_FUNCIONAL", "08_BORRADOR_DECISION_FUNCIONAL"),
        ("09_PENDIENTES_Y_BLOQUEOS", "09_PENDIENTES_Y_BLOQUEOS"),
        ("10_FUENTES", "10_FUENTES"),
        ("11_MANIFEST_LEGIBLE", "11_MANIFEST_LEGIBLE"),
    ]
)

DICTAMEN_218 = (
    "La exclusion de E=CONVALIDACION e I=HOMOLOGADO en columna 19 anual 2025 es consistente "
    "con la regla oficial del instructivo que excluye unidades aprobadas por validacion de estudios "
    "o reconocimiento de aprendizajes previos, considerando que E/I son datos observados en PROMEDIOS "
    "y no codigos definidos por el instructivo."
)

DICTAMEN_21 = (
    "Los 21 casos no presentan diferencia numerica entre 5809 y el recalculo: ambos mantienen 0,0,0,0. "
    "La evidencia muestra ausencia de registros academicos 2025 para CODCLI_LISTA y estado academico "
    "observado principalmente ELIMINADO. No corresponde denominar 'inactivo' al estado academico. "
    "Estos casos son cerrables sin cambio solo si se valida/documenta que la ausencia de registros 2025 "
    "y el estado academico observado no contradicen mantener 0,0,0,0."
)

DICTAMEN_17 = (
    "Los 17 casos PERIODO_NO_1_2 permanecen bloqueados. No se aplica el criterio 1=primer semestre "
    "y 2/3=segundo semestre, porque el hito 64 clasifico PERIODO raw como pendiente/bloqueado y sin "
    "respaldo oficial suficiente. Debe abrirse una gobernanza especifica de PERIODO raw para determinar "
    "significado de PERIODO 1, 2, 3, 4 y 5 en PROMEDIOS y su uso en columnas 16-18 del archivo 5809."
)

PROMPT_PERIODO = """Construir hito específico de gobernanza PERIODO raw para Avance Curricular 5809, sin modificar fuentes, sin corregir datos y sin generar carga. Debe explorar PROMEDIOS, control trace, TSV locales, scripts y manual/instructivo para determinar significado de PERIODO 1,2,3,4,5. Debe separar regla oficial, dato observado, implementación técnica, decisión interna e hipótesis. Debe producir matriz de decisión para uso o bloqueo de PERIODO raw en columnas 16,17,18. No debe aplicar criterio 1=SEM1 y 2/3=SEM2 salvo respaldo documental o validación funcional formal.

Fuentes mínimas sugeridas:
- PROMEDIOSDEALUMNOS actualizado y su diccionario interno.
- Hito 51 gobernanza integral 5809.
- Hito 52 validador precálculo.
- Hito 55 auditoría diferencia 16-18 múltiple.
- Hito 63 revisión 38 decisión funcional restante.
- Hito 64 exploración gobernanza transversal MU / Avance.
- TSV/control/trace locales con PERIODO, PERIODOMATRICULA o reglas equivalentes.
- Instructivo oficial Avance Curricular SIES 2026.

Productos mínimos:
- Matriz de PERIODO raw 1,2,3,4,5 por fuente, uso observado, uso permitido, uso prohibido, respaldo A/B/C/D/E y bloqueo.
- Decisión explícita para columnas 16, 17 y 18.
- Lista de casos afectados, sin recalcular datos.
- Recomendación de actualización del validador si se aprueba una regla funcional.
"""


def clean(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_xlsx(path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet, dtype=str).fillna("")


def display(value: Any, max_len: int = 110) -> str:
    text = clean(value)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def md_cell(value: Any, max_len: int = 110) -> str:
    return display(value, max_len).replace("|", "\\|").replace("\n", "<br>")


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "(sin filas)"
    cols = list(df.columns)
    widths: List[int] = []
    for col in cols:
        values = [str(col)] + [md_cell(v, 100) for v in df[col].tolist()]
        widths.append(max(len(v) for v in values))
    header = "| " + " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(cols)) + " |"
    sep = "| " + " | ".join("-" * width for width in widths) + " |"
    body = []
    for _, row in df.iterrows():
        body.append("| " + " | ".join(md_cell(row[col], 100).ljust(widths[i]) for i, col in enumerate(cols)) + " |")
    return "\n".join([header, sep] + body)


def keyify(df: pd.DataFrame, column: str = "FILA_KEY") -> pd.DataFrame:
    out = df.copy()
    if column in out.columns:
        out[column] = out[column].map(lambda x: clean(x).split(".")[0])
    return out


def instructivo_line(num: int, lines: List[str]) -> str:
    if num < 1 or num > len(lines):
        return ""
    return lines[num - 1].rstrip("\n")


def build_extractos_instructivo() -> pd.DataFrame:
    lines = INSTRUCTIVO.read_text(encoding="utf-8", errors="replace").splitlines()
    specs = [
        ("Definicion avance curricular", 140, "Contexto avance curricular", "16-19", "A", "Contextualiza unidades de medida y aprobacion."),
        ("Definicion avance curricular", 141, "Contexto avance curricular", "16-19", "A", "Contextualiza unidades de medida y plan de estudios."),
        ("Definicion unidades cursadas anual", 158, "UNIDADES_CURSADAS", "18", "A", "Separa cursadas de aprobadas."),
        ("Exclusion anual cursadas", 162, "UNIDADES_CURSADAS", "18", "A", "No resuelve bloque 218, pero confirma separacion anual/acumulado."),
        ("Exclusion anual cursadas", 165, "UNIDADES_CURSADAS", "18", "A", "Menciona validacion/reconocimiento para anual."),
        ("Definicion unidades aprobadas", 171, "UNIDADES_APROBADAS", "19", "A", "Inicio de definicion oficial del campo."),
        ("Definicion unidades aprobadas", 172, "UNIDADES_APROBADAS", "19", "A", "Aprobacion formal segun reglamentacion institucional."),
        ("Definicion unidades aprobadas", 173, "UNIDADES_APROBADAS", "19", "A", "Carrera informada en matricula 2025."),
        ("Exclusion anual aprobadas", 174, "UNIDADES_APROBADAS anual 2025", "19", "A", "Aplica directamente al bloque 218."),
        ("Exclusion anual aprobadas", 175, "UNIDADES_APROBADAS anual 2025", "19", "A", "Aplica directamente al bloque 218."),
        ("Exclusion anual aprobadas", 176, "UNIDADES_APROBADAS anual 2025", "19", "A", "Aplica directamente al bloque 218."),
        ("Inclusion acumulado aprobadas", 177, "UNID_APROBADAS_TOTAL", "21", "A", "20-21 queda separado; no se recalcula."),
        ("Inclusion acumulado aprobadas", 179, "UNID_APROBADAS_TOTAL", "21", "A", "Confirma que acumulado tiene regla distinta del anual."),
        ("Cuidado con estudiantes convalidantes", 181, "UNIDADES_APROBADAS / acumulado", "19/21", "A", "E/I son dato observado, no codigo del instructivo."),
        ("Campo UNIDADES_APROBADAS", 466, "UNIDADES_APROBADAS", "19", "A", "Tabla de campo oficial."),
        ("Campo UNIDADES_APROBADAS", 468, "UNIDADES_APROBADAS", "19", "A", "Especificacion: no incluir validacion/reconocimiento."),
        ("Campo UNIDADES_APROBADAS", 470, "UNIDADES_APROBADAS", "19", "A", "Especificacion: no incluir validacion/reconocimiento."),
        ("Campo UNIDADES_APROBADAS", 472, "UNIDADES_APROBADAS", "19", "A", "Especificacion: no incluir validacion/reconocimiento."),
        ("Campo UNID_APROBADAS_TOTAL", 493, "UNID_APROBADAS_TOTAL", "21", "A", "Acumulado separado; fuera del alcance."),
        ("Campo UNID_APROBADAS_TOTAL", 495, "UNID_APROBADAS_TOTAL", "21", "A", "Acumulado permite validacion/reconocimiento."),
    ]
    rows = []
    for tema, line_no, campo, bloque, respaldo, obs in specs:
        rows.append(
            {
                "Tema": tema,
                "Texto exacto encontrado": instructivo_line(line_no, lines).strip(),
                "Linea/seccion/pagina": f"Linea {line_no}",
                "Campo afectado": campo,
                "Tipo de respaldo": respaldo,
                "Aplicacion al bloque 218": "SI" if bloque == "19" or "UNIDADES_APROBADAS" in campo else "NO/DIFERENCIAR",
                "Observacion": obs,
            }
        )
    return pd.DataFrame(rows)


def build_bloque_218() -> pd.DataFrame:
    dictamen_h62 = read_xlsx(H62_XLSX, "00_DICTAMEN")
    escenarios = read_xlsx(H62_XLSX, "03_ESCENARIOS_H61")
    calce = read_xlsx(H62_XLSX, "04_CALCE_H61")
    tipo_e_i = read_xlsx(H62_XLSX, "05_TIPO_E_I")
    dicc_estado = read_xlsx(H51_XLSX, "05_DICCIONARIO_ESTADO_PROMEDIOS")

    total = int(clean(dictamen_h62.loc[0, "TOTAL_CASOS"]) or 0)
    calzan_solo_a = int(clean(dictamen_h62.loc[0, "CALZAN_SOLO_A"]) or 0)
    calzan_aei = int(clean(dictamen_h62.loc[0, "CALZAN_A_E_I"]) or 0)
    escenario_solo_a = escenarios.loc[escenarios["ESCENARIO"] == "SOLO_A"].iloc[0].to_dict()
    escenario_aei = escenarios.loc[escenarios["ESCENARIO"] == "A_E_I"].iloc[0].to_dict()
    dicc_txt = "; ".join(
        f"{clean(r['Estado'])}={clean(r['Descripcion'])}" for _, r in dicc_estado.iterrows()
    )
    rows = [
        {
            "Total casos": total,
            "Evidencia hito 61/62": f"H61/H62: {calzan_solo_a} de {total} calzan con SOLO A; {calzan_aei} de {total} calzan con A+E+I. Tipos E/I: {tipo_e_i.to_dict(orient='records')}. Calce: {calce.to_dict(orient='records')}.",
            "Escenario SOLO A": f"{escenario_solo_a.get('DESCRIPCION','')} | calzan={escenario_solo_a.get('CASOS_QUE_CALZAN_CON_5809','')}",
            "Escenario A+E+I": f"{escenario_aei.get('DESCRIPCION','')} | calzan={escenario_aei.get('CASOS_QUE_CALZAN_CON_5809','')}",
            "Regla oficial relacionada": "Instructivo Avance Curricular 2026: UNIDADES_APROBADAS anual 2025 excluye unidades aprobadas por validacion de estudios o reconocimiento de aprendizajes previos.",
            "Dato observado PROMEDIOS": dicc_txt,
            "Tratamiento A": "A=APROBADO cuenta como aprobada.",
            "Tratamiento E": "E=CONVALIDACION no cuenta en UNIDADES_APROBADAS anual 2025 por consistencia con exclusion oficial de validacion/convalidacion.",
            "Tratamiento I": "I=HOMOLOGADO no cuenta en UNIDADES_APROBADAS anual 2025 por consistencia con exclusion oficial de reconocimiento/homologacion.",
            "Tratamiento R": "R=REPROBADO no cuenta.",
            "Tratamiento NULL": "NULL/blanco no cuenta automaticamente y debe quedar en revision si aparece.",
            "Dictamen corregido": DICTAMEN_218,
            "Requiere validacion funcional": "SI: para formalizar que E/I observados en PROMEDIOS corresponden al alcance institucional de convalidacion/homologacion; el respaldo normativo A y el dato observado B ya sustentan no contar E/I en anual 2025.",
            "Correccion requerida": "NO",
        }
    ]
    return pd.DataFrame(rows)


def build_bloque_21() -> pd.DataFrame:
    detalle = keyify(read_xlsx(H63_XLSX, "03_21_ESTADO_ACAD"))
    evidencia = keyify(read_xlsx(H63_XLSX, "05_EVIDENCIA_H56"))
    merged = detalle.merge(evidencia, on="FILA_KEY", how="left", suffixes=("", "_H56"))
    rows = []
    for _, r in merged.iterrows():
        rows.append(
            {
                "FILA_5809": clean(r.get("FILA_5809")),
                "NUM_DOCUMENTO": clean(r.get("NUM_DOCUMENTO")),
                "DV": clean(r.get("DV")),
                "CODIGO_UNICO": clean(r.get("CODIGO_UNICO")),
                "PLAN_ESTUDIOS": clean(r.get("PLAN_ESTUDIOS")),
                "CODCLI_LISTA": clean(r.get("CODCLI_LISTA")),
                "Valor 5809": clean(r.get("VALOR_ACTUAL_5809")),
                "Valor recalculado observado": clean(r.get("VALOR_RECALCULADO_OBSERVADO")),
                "FILAS_2025_CODCLI_LISTA": clean(r.get("FILAS_2025_CODCLI_LISTA")),
                "ESTADOS_ACADEMICOS_OBSERVADOS": clean(r.get("ESTADOS_ACADEMICOS_OBSERVADOS")),
                "Indicador tecnico previo": f"{clean(r.get('ESTADO_ACADEMICO_INACTIVO_OBSERVADO'))}; indicador tecnico, no nombre de estado academico",
                "Dictamen corregido": DICTAMEN_21,
                "Correccion requerida": "NO, si se valida cierre sin cambio",
                "Validacion pendiente": "Validar/documentar que ausencia de registros 2025 y estado academico observado no contradicen mantener 0,0,0,0.",
            }
        )
    return pd.DataFrame(rows)


def build_bloque_17() -> pd.DataFrame:
    detalle = keyify(read_xlsx(H63_XLSX, "04_17_PERIODO_NO_1_2"))
    evidencia = keyify(read_xlsx(H63_XLSX, "06_EVIDENCIA_H55"))
    merged = detalle.merge(evidencia, on="FILA_KEY", how="left", suffixes=("", "_H55"))
    evidencia_h64 = (
        "H64: PERIODO raw 3/4/5 no confirmado como semestre para Avance ni MU; "
        "PERIODO 2/3 como segundo semestre queda pendiente/bloqueado; no aplicar transversalmente sin confirmacion."
    )
    rows = []
    for _, r in merged.iterrows():
        rows.append(
            {
                "FILA_5809": clean(r.get("FILA_5809")),
                "NUM_DOCUMENTO": clean(r.get("NUM_DOCUMENTO")),
                "DV": clean(r.get("DV")),
                "CODIGO_UNICO": clean(r.get("CODIGO_UNICO")),
                "PLAN_ESTUDIOS": clean(r.get("PLAN_ESTUDIOS")),
                "CODCLI_LISTA": clean(r.get("CODCLI_LISTA")),
                "Valor 5809": clean(r.get("VALOR_ACTUAL_5809")),
                "Valor recalculado observado": clean(r.get("VALOR_RECALCULADO_OBSERVADO")),
                "Evidencia hito 64": evidencia_h64,
                "PERIODO raw observado": clean(r.get("PERIODOS_OBSERVADOS")),
                "Columnas afectadas": clean(r.get("COLUMNA_AFECTADA_16_19")),
                "Ramos unicos PERIODO no 1/2": clean(r.get("RAMOS_UNICOS_PERIODO_NO_1_2")),
                "Por que sigue bloqueado": "No existe respaldo oficial suficiente para mapear PERIODO raw 3/4/5 a semestre ni para aplicar 2/3=segundo semestre.",
                "Que falta para cerrar": "Gobernanza especifica de PERIODO raw con significado de 1,2,3,4,5 y validacion funcional/documental.",
                "Dictamen": DICTAMEN_17,
                "Correccion requerida": "NO",
                "Estado": "BLOQUEADO",
            }
        )
    return pd.DataFrame(rows)


def build_comparacion() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Afirmacion anterior": "estado academico inactivo/eliminado",
                "Problema detectado": "Usa 'inactivo' como si fuera estado academico, pero la evidencia muestra valores observados reales.",
                "Correccion aplicada": "estado academico observado principalmente ELIMINADO; no usar inactivo como estado. Evidencia: 20 ELIMINADO y 1 ELIMINADO | VIGENTE.",
                "Nivel de respaldo": "B/C/D",
                "Estado": "CORREGIDO",
            },
            {
                "Afirmacion anterior": "218 si se valida mantener criterio observado",
                "Problema detectado": "No vinculaba suficientemente el cierre con regla oficial del instructivo.",
                "Correccion aplicada": "218 consistentes con regla oficial de excluir validacion/reconocimiento, usando E/I como dato observado PROMEDIOS y no como codigos del instructivo.",
                "Nivel de respaldo": "A/B/C/D",
                "Estado": "CORREGIDO",
            },
            {
                "Afirmacion anterior": "17 bloqueados por hito 64",
                "Problema detectado": "Correcto, pero faltaba dejar siguiente gobernanza especifica de PERIODO raw como obligacion.",
                "Correccion aplicada": "Se mantiene bloqueo y se agrega obligacion de gobernanza especifica PERIODO raw antes de usar criterio 1=SEM1 y 2/3=SEM2.",
                "Nivel de respaldo": "D/E",
                "Estado": "AMPLIADO",
            },
            {
                "Afirmacion anterior": "20-21 no evaluado / separado",
                "Problema detectado": "Debe permanecer fuera del alcance del hito 66.",
                "Correccion aplicada": "20-21 se declara separado y no evaluado; no se recalcula.",
                "Nivel de respaldo": "A/D",
                "Estado": "MANTENIDO",
            },
        ]
    )


def build_niveles_respaldo() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Fuente o criterio": "Instructivo Avance Curricular SIES 2026",
                "Nivel respaldo": "A",
                "Uso en hito 66": "Regla oficial para UNIDADES_APROBADAS anual 2025 y separacion anual/acumulado.",
                "Puede ser regla oficial": "SI",
                "Observacion": "Manual/instructivo del mismo proceso y periodo.",
            },
            {
                "Fuente o criterio": "PROMEDIOS ESTADO/DESCRIPCION_ESTADO gobernado en hito 51",
                "Nivel respaldo": "B",
                "Uso en hito 66": "Dato observado: A=APROBADO, E=CONVALIDACION, I=HOMOLOGADO, R=REPROBADO, NULL/blanco.",
                "Puede ser regla oficial": "NO",
                "Observacion": "No reemplaza instructivo; permite interpretar dato fuente.",
            },
            {
                "Fuente o criterio": "Hito 61 revision 218",
                "Nivel respaldo": "C",
                "Uso en hito 66": "Evidencia tecnica: 218 calzan SOLO A y 0 calzan A+E+I.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Resultado/auditoria tecnica.",
            },
            {
                "Fuente o criterio": "Hito 62 decision funcional candidata columna 19 SOLO A",
                "Nivel respaldo": "D con evidencia C",
                "Uso en hito 66": "Decision candidata corregida y reforzada con respaldo A/B.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Requiere formalizacion funcional; no aplica datos.",
            },
            {
                "Fuente o criterio": "Hito 63 revision 38",
                "Nivel respaldo": "C/D",
                "Uso en hito 66": "Separa 21 casos ausencia 2025 y 17 PERIODO_NO_1_2.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Auditoria y clasificacion; no normativa.",
            },
            {
                "Fuente o criterio": "Hito 64 exploracion transversal MU / Avance",
                "Nivel respaldo": "D/E",
                "Uso en hito 66": "Bloquea PERIODO raw 2/3=segundo semestre y 3/4/5 sin confirmacion.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Exploratorio; no aplica reglas transversales.",
            },
            {
                "Fuente o criterio": "Hito 65 consolidado post hito 64",
                "Nivel respaldo": "C/D",
                "Uso en hito 66": "Dictamen previo corregido.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Este hito corrige redaccion y sustento.",
            },
            {
                "Fuente o criterio": "Criterio PERIODO 2/3 = segundo semestre",
                "Nivel respaldo": "D/E pendiente",
                "Uso en hito 66": "No aplicado; queda bloqueado.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Requiere gobernanza PERIODO raw.",
            },
            {
                "Fuente o criterio": "Dictamen corregido hito 66",
                "Nivel respaldo": "D con respaldo A/B/C",
                "Uso en hito 66": "Documento de decision y ruta de cierre; no corrige datos.",
                "Puede ser regla oficial": "NO",
                "Observacion": "Formaliza trazabilidad y pendientes.",
            },
        ]
    )


def build_prompt_sheet() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Seccion": "Prompt completo", "Contenido": PROMPT_PERIODO},
            {"Seccion": "Regla critica", "Contenido": "No aplicar criterio 1=SEM1 y 2/3=SEM2 salvo respaldo documental o validacion funcional formal."},
            {"Seccion": "Salida esperada", "Contenido": "Matriz de decision para uso o bloqueo de PERIODO raw en columnas 16,17,18."},
        ]
    )


def build_borrador_text() -> str:
    return f"""# Borrador decision funcional 16-19 post hito 64

Proceso: {PROCESO}
Archivo: 5809 Matricula Avance Curricular
Ano proceso: {ANIO_PROCESO}
Ano referencia datos: {ANIO_REFERENCIA}
Declaracion de carga: {DECLARACION_CARGA}

Estimadas/os,

Se solicita validacion funcional del dictamen corregido para los bloques 218, 21 y 17 de columnas 16-19 del archivo 5809, sin solicitar carga, sin modificar fuentes originales y sin aplicar correcciones automaticas.

## 1. Bloque 218 columna 19 UNIDADES_APROBADAS

El instructivo oficial de Avance Curricular SIES 2026 indica que las unidades aprobadas durante el ultimo ano academico 2025 no deben incluir unidades aprobadas por validacion de estudios o reconocimiento de aprendizajes previos.

La fuente PROMEDIOS contiene el dato observado ESTADO/DESCRIPCION_ESTADO:
- A = APROBADO
- E = CONVALIDACION
- I = HOMOLOGADO
- R = REPROBADO
- NULL/blanco = en blanco

La evidencia de los hitos 61/62 muestra que 218 de 218 casos calzan con contar solo A y 0 de 218 calzan con A+E+I. Se solicita validar cierre sin cambio de estos 218 casos, considerando que E/I son datos observados de PROMEDIOS y que su exclusion en columna 19 anual 2025 es consistente con la regla oficial de excluir validacion/reconocimiento.

## 2. Bloque 21 ausencia de registros 2025

Los 21 casos no presentan diferencia numerica entre 5809 y recalculo observado: 16=NO, 17=NO, 18=0, 19=0. La evidencia muestra FILAS_2025_CODCLI_LISTA=0 y estado academico observado principalmente ELIMINADO, con un caso ELIMINADO | VIGENTE.

No se debe denominar 'inactivo' al estado academico. Ese termino solo aparecia como indicador tecnico previo, no como valor observado de estado academico.

Se solicita validar cierre sin cambio de estos 21 casos si la ausencia de registros academicos 2025 y los estados observados no contradicen mantener 0,0,0,0.

## 3. Bloque 17 PERIODO_NO_1_2

Los 17 casos permanecen bloqueados. No se aplica el criterio 1=primer semestre y 2/3=segundo semestre, porque el hito 64 clasifico PERIODO raw como pendiente/bloqueado y sin respaldo oficial suficiente.

Se solicita confirmar que estos 17 casos deben permanecer bloqueados hasta ejecutar una gobernanza especifica de PERIODO raw para PROMEDIOS.

## 4. Alcance excluido

Las columnas 20-21 acumuladas estan fuera de alcance de este paquete, permanecen separadas y no evaluadas.

Resultado esperado de la validacion:
- Confirmar o rechazar cierre sin cambio de los 218 casos.
- Confirmar o rechazar cierre sin cambio de los 21 casos.
- Confirmar bloqueo de los 17 casos hasta gobernanza PERIODO raw.
- Confirmar que 20-21 no se evalua en este hito.
"""


def build_borrador_sheet(text: str) -> pd.DataFrame:
    rows = []
    for idx, paragraph in enumerate(text.split("\n\n"), start=1):
        rows.append({"Orden": idx, "Texto": paragraph.strip()})
    return pd.DataFrame(rows)


def build_pendientes() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Pendiente/Bloqueo": "17 PERIODO_NO_1_2",
                "Casos": 17,
                "Estado": "BLOQUEADO",
                "Requisito para cerrar": "Gobernanza especifica PERIODO raw para significado 1,2,3,4,5 y uso en 16-18.",
                "20-21": "NO EVALUADO / SEPARADO",
            },
            {
                "Pendiente/Bloqueo": "184 pendientes restantes estimados",
                "Casos": 184,
                "Estado": "PENDIENTE",
                "Requisito para cerrar": "Dependen de validaciones funcionales y rutas no abordadas en este hito.",
                "20-21": "NO EVALUADO / SEPARADO",
            },
            {
                "Pendiente/Bloqueo": "Validacion funcional bloque 218",
                "Casos": 218,
                "Estado": "VALIDACION_FUNCIONAL_PENDIENTE",
                "Requisito para cerrar": "Formalizar que cierre sin cambio es aceptado por regla oficial + dato observado.",
                "20-21": "NO EVALUADO / SEPARADO",
            },
            {
                "Pendiente/Bloqueo": "Validacion funcional bloque 21",
                "Casos": 21,
                "Estado": "VALIDACION_FUNCIONAL_PENDIENTE",
                "Requisito para cerrar": "Formalizar que ausencia de registros 2025 y estados observados permiten mantener 0,0,0,0.",
                "20-21": "NO EVALUADO / SEPARADO",
            },
            {
                "Pendiente/Bloqueo": "20-21 acumulado",
                "Casos": "No cuantificado en este hito",
                "Estado": "SEPARADO_NO_EVALUADO",
                "Requisito para cerrar": "Gobernanza/acumulado especifico; no recalcular en hito 66.",
                "20-21": "NO EVALUADO / SEPARADO",
            },
            {
                "Pendiente/Bloqueo": "Fuente faltante PERIODO raw",
                "Casos": 17,
                "Estado": "FUENTE_O_DECISION_FUNCIONAL_REQUERIDA",
                "Requisito para cerrar": "Documento, control, trace o validacion formal que gobierne PERIODO raw en PROMEDIOS.",
                "20-21": "NO EVALUADO / SEPARADO",
            },
        ]
    )


def build_dictamen_global(bloque21: pd.DataFrame, bloque17: pd.DataFrame) -> pd.DataFrame:
    estados_21 = bloque21["ESTADOS_ACADEMICOS_OBSERVADOS"].value_counts().to_dict()
    return pd.DataFrame(
        [
            {
                "Proceso": PROCESO,
                "Subproyecto": SUBPROYECTO,
                "Año proceso": ANIO_PROCESO,
                "Año referencia": ANIO_REFERENCIA,
                "Estado": ESTADO,
                "Declaración carga": DECLARACION_CARGA,
                "Fuentes originales modificadas": "NO",
                "Correcciones aplicadas": "NO",
                "SIES_READY generado": "NO",
                "20-21 evaluado": "NO_SEPARADO",
                "Total pendientes originales 16-19": 423,
                "Bloque 218: estado corregido": "CERRABLE_SIN_CAMBIO_CON_RESPALDO_A_B_Y_VALIDACION_FUNCIONAL_PENDIENTE",
                "Bloque 21: estado corregido": f"CERRABLE_SIN_CAMBIO_SI_SE_VALIDA; estados observados={estados_21}",
                "Bloque 17: bloqueado por PERIODO raw hito 64": "BLOQUEADO",
                "Cerrables sin cambio con respaldo oficial/dato observado/validación pendiente": 239,
                "Bloqueados": len(bloque17),
                "Pendientes restantes estimados": 184,
                "Dictamen global": "Se corrige el dictamen del hito 65: bloque 218 queda sustentado por instructivo oficial y diccionario observado PROMEDIOS; bloque 21 se redacta con estados reales observados; bloque 17 permanece bloqueado por PERIODO raw segun hito 64. No hay carga ni correccion de datos.",
            }
        ]
    )


def build_fuentes(output_paths: Dict[str, Path], desktop_dir: Path) -> pd.DataFrame:
    entries = [
        ("A", "Instructivo oficial Avance", INSTRUCTIVO, "Regla oficial del proceso."),
        ("D", "Hito 51 carpeta", H51_DIR, "Gobernanza integral 5809."),
        ("B/D", "Hito 51 Excel", H51_XLSX, "Diccionario ESTADO/DESCRIPCION_ESTADO PROMEDIOS."),
        ("C", "Hito 52 carpeta", H52_DIR, "Validador gobernanza precalculo."),
        ("C", "Hito 52 Excel", H52_XLSX, "Evidencia validador precalculo."),
        ("C", "Hito 55 carpeta", H55_DIR, "Evidencia previa PERIODO_NO_1_2."),
        ("C/D", "Hito 56 carpeta", H56_DIR, "Evidencia ausencia registros 2025."),
        ("C/D", "Hito 56 Excel", H56_XLSX, "Estados academicos observados bloque 21."),
        ("D", "Hito 59 carpeta", H59_DIR, "Paquete validacion humana 16-19."),
        ("D", "Hito 59 Excel", H59_XLSX, "Clasificacion previa 423 casos."),
        ("C", "Hito 61 carpeta", H61_DIR, "Revision 218 convalidacion/homologacion."),
        ("C", "Hito 61 Excel", H61_XLSX, "Escenarios SOLO A y A+E+I."),
        ("D", "Hito 62 carpeta", H62_DIR, "Decision funcional candidata columna 19 SOLO A."),
        ("D", "Hito 62 Excel", H62_XLSX, "Dictamen candidato y detalle 218."),
        ("C/D", "Hito 63 carpeta", H63_DIR, "Revision 38 decision funcional restante."),
        ("C/D", "Hito 63 Excel", H63_XLSX, "Detalle 21 y 17."),
        ("D/E", "Hito 64 carpeta", H64_DIR, "Exploracion gobernanza transversal."),
        ("D/E", "Hito 64 Excel", H64_XLSX, "Bloqueo PERIODO raw."),
        ("C/D", "Hito 65 carpeta", H65_DIR, "Dictamen anterior a corregir."),
        ("C/D", "Hito 65 Excel", H65_XLSX, "Consolidado post H64."),
        ("C/D", "Hito 65 informe", H65_MD, "Redaccion anterior comparada."),
    ]
    rows = []
    for idx, (nivel, tipo, path, uso) in enumerate(entries, start=1):
        rows.append(
            {
                "ID": f"F{idx:03d}",
                "Tipo": tipo,
                "Ruta": str(path),
                "Existe": "SI" if path.exists() else "NO",
                "Hash SHA256": sha256_file(path) if path.exists() and path.is_file() else "",
                "Nivel respaldo": nivel,
                "Uso": uso,
            }
        )
    for key, path in output_paths.items():
        rows.append(
            {
                "ID": f"OUT_{key.upper()}",
                "Tipo": "Producto hito 66",
                "Ruta": str(path),
                "Existe": "SI" if path.exists() else "NO",
                "Hash SHA256": sha256_file(path) if path.exists() and path.is_file() and key != "manifest" else "",
                "Nivel respaldo": "DERIVADO",
                "Uso": "Producto generado; no fuente normativa.",
            }
        )
    rows.append(
        {
            "ID": "OUT_DESKTOP",
            "Tipo": "Copia escritorio",
            "Ruta": str(desktop_dir),
            "Existe": "SI" if desktop_dir.exists() else "NO",
            "Hash SHA256": "",
            "Nivel respaldo": "DERIVADO",
            "Uso": "Copia de productos al Escritorio.",
        }
    )
    return pd.DataFrame(rows)


def build_manifest(timestamp: str, output_dir: Path, desktop_dir: Path, output_paths: Dict[str, Path], sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    return {
        "proceso": PROCESO,
        "subproyecto": SUBPROYECTO,
        "timestamp": timestamp,
        "estado": ESTADO,
        "declaracion_carga": DECLARACION_CARGA,
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "sies_ready_generado": "NO",
        "archivo_carga_generado": "NO",
        "recalculo_20_21": "NO",
        "reglas_no_gobernadas_aplicadas": "NO",
        "total_pendientes_originales_16_19": 423,
        "bloque_218": {
            "casos": 218,
            "estado": "CERRABLE_SIN_CAMBIO_CON_RESPALDO_A_B_Y_VALIDACION_FUNCIONAL_PENDIENTE",
            "correccion_requerida": "NO",
        },
        "bloque_21": {
            "casos": 21,
            "estado": "CERRABLE_SIN_CAMBIO_SI_SE_VALIDA",
            "correccion_requerida": "NO",
            "estado_academico_redaccion": "usar valores observados reales; no denominar inactivo al estado",
        },
        "bloque_17": {
            "casos": 17,
            "estado": "BLOQUEADO_PERIODO_RAW_H64",
            "correccion_requerida": "NO",
        },
        "cerrables_sin_cambio_si_se_validan": 239,
        "pendientes_restantes_estimados": 184,
        "carpeta_salida": str(output_dir),
        "carpeta_escritorio": str(desktop_dir),
        "productos": {key: str(path) for key, path in output_paths.items()},
        "hojas_excel": {logical: {"hoja_excel": SHEETS.get(logical, logical)[:31], "filas": len(df)} for logical, df in sheets.items()},
        "hashes_salida": {key: sha256_file(path) for key, path in output_paths.items() if path.exists() and path.is_file() and key != "manifest"},
    }


def manifest_legible(manifest: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for key, value in manifest.items():
        rows.append({"Clave": key, "Valor": json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value})
    return pd.DataFrame(rows)


def excel_safe_frame(df: pd.DataFrame) -> pd.DataFrame:
    def safe(value: Any) -> Any:
        if isinstance(value, str) and len(value) > 32000:
            return value[:31980] + " [...TRUNCADO_PARA_EXCEL]"
        return value

    return df.map(safe)


def write_excel(path: Path, sheets: Dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for logical_name, df in sheets.items():
            sheet_name = SHEETS.get(logical_name, logical_name)[:31]
            excel_safe_frame(df).to_excel(writer, sheet_name=sheet_name, index=False)
    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        for idx, column_cells in enumerate(ws.columns, start=1):
            values = [display(cell.value, 80) for cell in column_cells[:120]]
            width = min(max([len(v) for v in values] + [10]) + 2, 60)
            ws.column_dimensions[get_column_letter(idx)].width = width
    wb.save(path)


def build_markdown(
    dictamen: pd.DataFrame,
    extractos: pd.DataFrame,
    bloque218: pd.DataFrame,
    bloque21: pd.DataFrame,
    bloque17: pd.DataFrame,
    comparacion: pd.DataFrame,
    pendientes: pd.DataFrame,
    output_paths: Dict[str, Path],
    desktop_dir: Path,
) -> str:
    estados_21 = bloque21["ESTADOS_ACADEMICOS_OBSERVADOS"].value_counts().to_dict()
    periodos_17 = bloque17["PERIODO raw observado"].value_counts().to_dict()
    return f"""# Correccion dictamen post H64 16-19 - 5809

## Estado

- Proceso: {PROCESO}
- Subproyecto: {SUBPROYECTO}
- Ano proceso: {ANIO_PROCESO}
- Ano referencia datos: {ANIO_REFERENCIA}
- Declaracion carga: {DECLARACION_CARGA}
- Fuentes originales modificadas: NO
- Correcciones aplicadas: NO
- SIES_READY generado: NO
- Archivo de carga generado: NO
- 20-21: NO evaluado / separado

## Que se corrigio

Se corrige el dictamen del hito 65 en tres puntos: el bloque 218 queda vinculado explicitamente al instructivo oficial; el bloque 21 deja de usar "inactivo" como nombre de estado academico; y el bloque 17 queda bloqueado hasta una gobernanza especifica de PERIODO raw.

## Instructivo y UNIDADES_APROBADAS

El instructivo oficial define UNIDADES_APROBADAS para la carrera informada en 2025 y, para el ano academico 2025, excluye unidades aprobadas por validacion de estudios o reconocimiento de aprendizajes previos. Tambien separa la regla anual de la acumulada: las columnas 20-21 tienen tratamiento distinto y no se evalúan en este hito.

Extractos trazables:

{markdown_table(extractos[["Tema", "Texto exacto encontrado", "Linea/seccion/pagina", "Campo afectado"]], max_rows=12)}

## Relacion con E/I observados en PROMEDIOS

La gobernanza hito 51 registra el dato observado PROMEDIOS: A=APROBADO, E=CONVALIDACION, I=HOMOLOGADO, R=REPROBADO y NULL/blanco. Estos codigos no son codigos oficiales del instructivo; se usan como dato observado de la fuente academica.

Para columna 19 anual 2025, la exclusion de E e I es consistente con la regla oficial que excluye validacion/reconocimiento. Por eso los 218 son cerrables sin cambio con respaldo A/B y validacion funcional pendiente, no por inferencia ni por presentar PROMEDIOS como norma.

## Bloque 218

{markdown_table(bloque218[["Total casos", "Escenario SOLO A", "Escenario A+E+I", "Tratamiento A", "Tratamiento E", "Tratamiento I", "Correccion requerida"]])}

Dictamen corregido: {DICTAMEN_218}

## Bloque 21

Los 21 casos no presentan diferencia numerica entre 5809 y recalculo observado: ambos mantienen 16=NO, 17=NO, 18=0, 19=0. En los 21 casos FILAS_2025_CODCLI_LISTA=0. Estados academicos observados reales: {estados_21}.

No se debe decir "inactivo" como estado academico. En la evidencia existia un indicador tecnico, pero los valores observados reales son ELIMINADO y ELIMINADO | VIGENTE.

Dictamen corregido: {DICTAMEN_21}

## Bloque 17

Los 17 casos siguen bloqueados. Periodos observados: {periodos_17}. El hito 64 indica que PERIODO raw 3/4/5 no esta confirmado como semestre para Avance ni MU, y que no hay evidencia oficial suficiente para homologar PERIODO raw 2/3 a segundo semestre.

Dictamen: {DICTAMEN_17}

## Comparacion antes/despues

{markdown_table(comparacion)}

## Pendientes

{markdown_table(pendientes)}

## Por que NO_LISTO_PARA_CARGA

No se corrigieron datos, no se genero archivo de carga, no se genero SIES_READY, 20-21 esta separado y no evaluado, y existen 17 casos bloqueados por PERIODO raw mas pendientes estimados que requieren validacion funcional o fuente complementaria.

## Archivos

- Excel: {output_paths['excel']}
- Informe: {output_paths['informe']}
- Manifest: {output_paths['manifest']}
- Script: {output_paths['script']}
- Borrador decision: {output_paths['borrador']}
- Prompt PERIODO raw: {output_paths['prompt_periodo']}
- Carpeta escritorio: {desktop_dir}
"""


def copy_to_desktop(output_dir: Path, desktop_dir: Path) -> None:
    desktop_dir.parent.mkdir(parents=True, exist_ok=True)
    if desktop_dir.exists():
        shutil.rmtree(desktop_dir)
    shutil.copytree(output_dir, desktop_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def print_console(
    dictamen: pd.DataFrame,
    bloque218: pd.DataFrame,
    bloque21: pd.DataFrame,
    bloque17: pd.DataFrame,
    pendientes: pd.DataFrame,
    output_paths: Dict[str, Path],
    desktop_dir: Path,
) -> None:
    print("CORRECCIÓN DICTAMEN POST H64 16-19 — GENERADA")
    print("Fuentes originales modificadas: NO")
    print("Correcciones aplicadas: NO")
    print("SIES_READY generado: NO")
    print("Declaración carga: NO_LISTO_PARA_CARGA")
    print()
    print("DICTAMEN GLOBAL")
    print(dictamen.to_string(index=False))
    print()
    print("BLOQUE 218")
    print(bloque218[["Total casos", "Escenario SOLO A", "Escenario A+E+I", "Correccion requerida"]].to_string(index=False))
    print()
    print("BLOQUE 21")
    resumen21 = pd.DataFrame(
        [
            {
                "Casos": len(bloque21),
                "FILAS_2025_CODCLI_LISTA": bloque21["FILAS_2025_CODCLI_LISTA"].value_counts().to_dict(),
                "ESTADOS_ACADEMICOS_OBSERVADOS": bloque21["ESTADOS_ACADEMICOS_OBSERVADOS"].value_counts().to_dict(),
                "Correccion requerida": "NO, si se valida cierre sin cambio",
            }
        ]
    )
    print(resumen21.to_string(index=False))
    print()
    print("BLOQUE 17")
    resumen17 = pd.DataFrame(
        [
            {
                "Casos": len(bloque17),
                "PERIODO raw observado": bloque17["PERIODO raw observado"].value_counts().to_dict(),
                "Estado": "BLOQUEADO",
                "Correccion requerida": "NO",
            }
        ]
    )
    print(resumen17.to_string(index=False))
    print()
    print("PENDIENTES")
    print(pendientes.to_string(index=False))
    print()
    print("ARCHIVOS")
    print(f"Excel: {output_paths['excel']}")
    print(f"Informe: {output_paths['informe']}")
    print(f"Manifest: {output_paths['manifest']}")
    print(f"Script: {output_paths['script']}")
    print(f"Borrador decisión: {output_paths['borrador']}")
    print(f"Prompt PERIODO raw: {output_paths['prompt_periodo']}")
    print(f"Carpeta escritorio: {desktop_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Correccion dictamen post H64 16-19 5809")
    parser.add_argument("--timestamp", default=None, help="Timestamp YYYYMMDD_HHMMSS")
    args = parser.parse_args()
    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")

    output_dir = BASE_OUT / f"CORRECCION_DICTAMEN_POST_H64_16_19_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    desktop_dir = Path.home() / "Desktop" / f"AVANCE_CURRICULAR_2026_CORRECCION_DICTAMEN_POST_H64_16_19_{timestamp}"
    output_paths = {key: output_dir / filename for key, filename in OUTPUT_FILES.items()}

    current_script = Path(__file__).resolve()
    if current_script != output_paths["script"].resolve():
        shutil.copy2(current_script, output_paths["script"])

    extractos = build_extractos_instructivo()
    bloque218 = build_bloque_218()
    bloque21 = build_bloque_21()
    bloque17 = build_bloque_17()
    comparacion = build_comparacion()
    niveles = build_niveles_respaldo()
    prompt_sheet = build_prompt_sheet()
    borrador_text = build_borrador_text()
    borrador_sheet = build_borrador_sheet(borrador_text)
    pendientes = build_pendientes()
    dictamen = build_dictamen_global(bloque21, bloque17)

    sheets: Dict[str, pd.DataFrame] = OrderedDict(
        [
            ("00_DICTAMEN_GLOBAL", dictamen),
            ("01_EXTRACTOS_INSTRUCTIVO", extractos),
            ("02_BLOQUE_218_COLUMNA_19", bloque218),
            ("03_BLOQUE_21_ESTADO_ACADEMICO", bloque21),
            ("04_BLOQUE_17_PERIODO_RAW", bloque17),
            ("05_COMPARACION_ANTES_DESPUES", comparacion),
            ("06_NIVELES_RESPALDO", niveles),
            ("07_PROMPT_GOBERNANZA_PERIODO_RAW", prompt_sheet),
            ("08_BORRADOR_DECISION_FUNCIONAL", borrador_sheet),
            ("09_PENDIENTES_Y_BLOQUEOS", pendientes),
        ]
    )

    output_paths["borrador"].write_text(borrador_text, encoding="utf-8")
    output_paths["prompt_periodo"].write_text(PROMPT_PERIODO, encoding="utf-8")
    output_paths["informe"].write_text(
        build_markdown(dictamen, extractos, bloque218, bloque21, bloque17, comparacion, pendientes, output_paths, desktop_dir),
        encoding="utf-8",
    )

    sheets["10_FUENTES"] = build_fuentes(output_paths, desktop_dir)
    manifest = build_manifest(timestamp, output_dir, desktop_dir, output_paths, sheets)
    sheets["11_MANIFEST_LEGIBLE"] = manifest_legible(manifest)
    write_excel(output_paths["excel"], sheets)
    sheets["10_FUENTES"] = build_fuentes(output_paths, desktop_dir)
    manifest = build_manifest(timestamp, output_dir, desktop_dir, output_paths, sheets)
    sheets["11_MANIFEST_LEGIBLE"] = manifest_legible(manifest)
    write_excel(output_paths["excel"], sheets)
    output_paths["manifest"].write_text(json.dumps(build_manifest(timestamp, output_dir, desktop_dir, output_paths, sheets), ensure_ascii=False, indent=2), encoding="utf-8")
    sheets["10_FUENTES"] = build_fuentes(output_paths, desktop_dir)
    manifest = build_manifest(timestamp, output_dir, desktop_dir, output_paths, sheets)
    sheets["11_MANIFEST_LEGIBLE"] = manifest_legible(manifest)
    write_excel(output_paths["excel"], sheets)
    output_paths["manifest"].write_text(json.dumps(build_manifest(timestamp, output_dir, desktop_dir, output_paths, sheets), ensure_ascii=False, indent=2), encoding="utf-8")

    copy_to_desktop(output_dir, desktop_dir)
    print_console(dictamen, bloque218, bloque21, bloque17, pendientes, output_paths, desktop_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
