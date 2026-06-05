#!/usr/bin/env python3
"""Hito 7 BIS CNED: mapear campos reales contra el Manual INDICES/CNED local.

El script no genera archivo final de subida. Extrae evidencia desde el manual
local disponible, cruza columnas reales del candidato Hito 5 y reevalua los
bloqueos de Hito 6 para dejar un diccionario oficial/preliminar trazable.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[2]
CNED = ROOT / "cned"
INPUT_BASE = CNED / "resultados/archivos_subida/CNED_BASE_SANEADA_PRELIMINAR_HITO5_20260605_135231.xlsx"
HITO6 = CNED / "resultados/archivos_subida/CNED_MATRIZ_RESOLUCION_BLOQUEOS_HITO6_20260605_140333.xlsx"
REPORT_DIR = CNED / "resultados/reportes"
AUDIT_DIR = CNED / "resultados/auditorias"
OUTPUT_DIR = CNED / "resultados/archivos_subida"
MANUAL_PRIORITARIO = ROOT / "indices_2025/docs/Manual_INDICES_2025 2.txt"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

EXCEL_OUT = OUTPUT_DIR / f"CNED_HITO7BIS_DICCIONARIO_OFICIAL_APLICADO_{TIMESTAMP}.xlsx"
MD_OUT = REPORT_DIR / f"CNED_HITO7BIS_DICCIONARIO_OFICIAL_CNED_{TIMESTAMP}.md"
CSV_DICT_OUT = AUDIT_DIR / f"CNED_HITO7BIS_DICCIONARIO_MANUAL_{TIMESTAMP}.csv"
CSV_MAP_OUT = AUDIT_DIR / f"CNED_HITO7BIS_MAPEO_COLUMNAS_{TIMESTAMP}.csv"
CSV_IMPACT_OUT = AUDIT_DIR / f"CNED_HITO7BIS_IMPACTO_BLOQUEOS_{TIMESTAMP}.csv"
JSON_OUT = AUDIT_DIR / f"CNED_HITO7BIS_RESUMEN_{TIMESTAMP}.json"

SHEET_PREFERENCE = [
    "CANDIDATO_CARGA_LIMPIO",
    "BASE_AUDITADA_ORIGINAL",
    "BASE_AUDITADA",
    "BASE_REFERENCIA",
]

AUXILIARY_PATTERNS = [
    "CNED_",
    "MATCH",
    "SCORE",
    "TRAZABILIDAD",
    "OBSERVACION_TECNICA",
    "ALERTAS",
    "AUDITORIA",
]

OFFICIAL_CORE_NORMALIZED = {
    "CODIGO_UNICO",
    "CODIGO_IES",
    "CODIGO_IES_NUM",
    "COD_SEDE",
    "CODIGO_SEDE",
    "SEDE",
    "NOMBRE_SEDE",
    "COD_CARRERA",
    "CODIGO_CARRERA",
    "COD_CARRERA_DERIVADO",
    "NOMBRE_CARRERA",
    "NOMBRE_CARRERA_ORIGINAL",
    "MODALIDAD",
    "MODALIDAD_ORIGINAL",
    "JORNADA",
    "COD_JORNADA",
    "VERSION",
    "VERSION_DERIVADA",
    "ANIO_INICIO",
    "ANO_INICIO",
    "VIGENCIA",
    "VIGENCIA_CARRERA",
    "REGIMEN",
    "DURACION_REGIMEN",
    "DURACION_TOTAL",
    "DURACION_ESTUDIOS",
    "NOMBRE_TITULO",
    "ACREDITACION",
    "REQUISITO_INGRESO",
    "SEMESTRES_RECONOCIDOS",
    "AREA_ACTUAL",
}

FORM_FIELD_NORMALIZED = {
    "TIPO_DE_CARRERA_PROGRAMA",
    "TIPO_CARRERA",
    "NOMBRE_DEL_PROGRAMA",
    "NOMBRE",
    "ESPECIALIZACIONES_Y_MENCIONES",
    "MENCION_O_ESPECIALIDAD",
    "ANO_DE_INICIO_DE_ACTIVIDADES",
    "ANIO_INICIO",
    "CAMPUS",
    "HORARIO",
    "ESTADO_DE_LA_CARRERA_O_PROGRAMA",
    "ESTADO",
    "TIPO_DEL_PROGRAMA",
    "TIPO_PROGRAMA",
    "DETALLE_DEL_TIPO_DE_PROGRAMA_ESPECIALES",
    "DETALLE_DEL_TIPO_DE_PROGRAMA",
    "MODALIDAD_DEL_PROGRAMA",
    "AREA_SUBAREA_CARRERA_GENERICA",
    "AREA_DEL_CONOCIMIENTO",
    "SUB_AREA",
    "CARRERA_GENERICA",
    "TITULO",
    "TITULO_QUE_OTORGA_EL_PROGRAMA",
    "GRADO_ACADEMICO",
    "GRADO_ACADEMICO_QUE_OTORGA_EL_PROGRAMA",
    "DEPENDENCIA",
    "TIPO_REGIMEN",
    "REGIMEN",
    "DURACION",
    "DURACION_DEL_PROGRAMA_EN_SEMESTRES",
    "FORMAS_DE_INGRESO",
    "INGRESO_DIRECTO",
    "INGRESO_DESDE_UN_PLAN_COMUN",
    "INGRESO_DESDE_BACHILLERATO",
    "OTRO_TIPO_DE_INGRESO",
    "VALOR_DE_LA_MATRICULA",
    "VALOR_MATRICULA_ANUAL",
    "VALOR_ARANCEL_ANUAL",
    "ARANCEL_ANUAL",
    "VALOR_TITULACION",
    "COSTO_TITULACION",
    "TIPO_MONEDA",
    "FORMATO_VALOR",
    "VACANTES_PRIMER_SEMESTRE",
    "VACANTES_SEGUNDO_SEMESTRE",
}

EXPECTED_FIELDS: list[dict[str, Any]] = [
    {
        "campo": "Tipo de Carrera/Programa",
        "sinonimos": ["Tipo de Carrera/Programa", "Tipo Carrera", "Tipo de Carrera"],
        "seccion": "Nuevos Programas",
        "tipo": "Texto",
    },
    {"campo": "Nombre del Programa", "sinonimos": ["Nombre del Programa", "Nombre"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {
        "campo": "Especializaciones y menciones",
        "sinonimos": ["Especializaciones y menciones", "Especialidad o mención", "EspecialidadOMencion"],
        "seccion": "Nuevos Programas",
        "tipo": "Texto",
    },
    {
        "campo": "Año de Inicio de actividades",
        "sinonimos": ["Año de Inicio de actividades", "AnioInicioActividades", "ANIO_INICIO", "AÑO_INICIO"],
        "seccion": "Nuevos Programas",
        "tipo": "N° Entero Positivo",
    },
    {"campo": "Campus", "sinonimos": ["Campus", "nombreCampus"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {"campo": "Horario", "sinonimos": ["Horario", "Jornada"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {
        "campo": "Estado de la carrera o programa",
        "sinonimos": ["Estado de la carrera o programa", "Estado del programa", "idEstadoCarrera", "Vigencia"],
        "seccion": "Nuevos Programas",
        "tipo": "Texto",
    },
    {"campo": "Tipo del programa", "sinonimos": ["Tipo del programa", "Tipo Programa"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {
        "campo": "Detalle del Tipo de Programa (especiales)",
        "sinonimos": ["Detalle del Tipo de Programa", "Detalle del Tipo de Programa (especiales)"],
        "seccion": "Nuevos Programas",
        "tipo": "Texto",
    },
    {"campo": "Modalidad del Programa", "sinonimos": ["Modalidad del Programa", "Modalidad"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {
        "campo": "Área, Subárea, Carrera genérica",
        "sinonimos": ["Área, Subárea, Carrera genérica", "Área del Conocimiento", "Sub Área", "Carrera Genérica", "AREA_ACTUAL"],
        "seccion": "Nuevos Programas",
        "tipo": "Texto",
    },
    {"campo": "Título", "sinonimos": ["Título", "Titulo", "NOMBRE_TITULO"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {"campo": "Grado académico", "sinonimos": ["Grado académico", "Grado Academico"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {"campo": "Dependencia", "sinonimos": ["Dependencia", "NombreDependencia"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {"campo": "Tipo Régimen", "sinonimos": ["Tipo Régimen", "Régimen", "REGIMEN"], "seccion": "Nuevos Programas", "tipo": "Texto"},
    {
        "campo": "Duración",
        "sinonimos": ["Duración", "Duración en semestres", "DURACION_TOTAL", "Duración del programa en Semestres"],
        "seccion": "Nuevos Programas",
        "tipo": "N° Entero Positivo",
    },
    {"campo": "Formas de ingreso", "sinonimos": ["Formas de ingreso", "REQUISITO_INGRESO"], "seccion": "Nuevos Programas", "tipo": "Ticket y Texto"},
    {"campo": "Valor de la Matrícula", "sinonimos": ["Valor de la Matrícula", "valorMatAnual", "VALOR_MATRICULA_ANUAL"], "seccion": "Evolución Programas", "tipo": "N° Entero Positivo"},
    {"campo": "Valor arancel anual", "sinonimos": ["Valor arancel anual", "valorArancelAnual", "ARANCEL_ANUAL"], "seccion": "Evolución Programas", "tipo": "N° Entero Positivo"},
    {"campo": "Valor titulación", "sinonimos": ["Valor titulación", "valorTitulo", "COSTO_TITULACION"], "seccion": "Evolución Programas", "tipo": "N° Entero Positivo"},
    {"campo": "Tipo Moneda", "sinonimos": ["Tipo Moneda", "TipoMoneda", "FORMATO_VALOR"], "seccion": "Evolución Programas", "tipo": "Texto"},
    {"campo": "Vacantes Primer Semestre", "sinonimos": ["Vacantes Primer Semestre", "VacantesSemestre1", "VACANTES_PRIMER_SEMESTRE"], "seccion": "Evolución Programas", "tipo": "N° Entero Positivo"},
    {"campo": "Vacantes Segundo Semestre", "sinonimos": ["Vacantes Segundo Semestre", "VacantesSemestre2", "VACANTES_SEGUNDO_SEMESTRE"], "seccion": "Evolución Programas", "tipo": "N° Entero Positivo"},
    {"campo": "Código único", "sinonimos": ["Código único", "CODIGO_UNICO"], "seccion": "Estructura interna / CSV", "tipo": "Código"},
    {"campo": "Código de carrera", "sinonimos": ["Código de carrera", "Codcarr", "COD_CARRERA", "CODIGO_CARRERA"], "seccion": "CSV Evolución Carreras", "tipo": "N° entero positivo"},
    {"campo": "Sede", "sinonimos": ["Sede", "Idsede", "NOMBRE_SEDE", "COD_SEDE"], "seccion": "CSV Evolución Carreras", "tipo": "Texto/Código"},
    {"campo": "Jornada", "sinonimos": ["Jornada", "Horario", "COD_JORNADA"], "seccion": "CSV Evolución Carreras", "tipo": "Texto/Código"},
    {"campo": "Versión", "sinonimos": ["Versión", "VERSION", "VERSION_CARRERA"], "seccion": "Estructura interna", "tipo": "Código"},
    {"campo": "Vigencia", "sinonimos": ["Vigencia", "Estado de la carrera o programa", "Estado del programa"], "seccion": "Nuevos/Evolución Programas", "tipo": "Texto/Código"},
    {"campo": "Duración régimen", "sinonimos": ["Duración régimen", "DURACION_REGIMEN"], "seccion": "Estructura interna", "tipo": "N° Entero Positivo"},
    {"campo": "Requisito ingreso", "sinonimos": ["Requisito ingreso", "REQUISITO_INGRESO", "Formas de ingreso"], "seccion": "Nuevos Programas", "tipo": "Código/Texto"},
    {"campo": "Semestres reconocidos", "sinonimos": ["Semestres reconocidos", "SEMESTRES_RECONOCIDOS"], "seccion": "Estructura interna", "tipo": "N° Entero Positivo"},
    {"campo": "Acreditación", "sinonimos": ["Acreditación", "ACREDITACION"], "seccion": "Estructura interna", "tipo": "Código/Texto"},
    {"campo": "Área actual", "sinonimos": ["Área actual", "AREA_ACTUAL", "Área del Conocimiento"], "seccion": "Nuevos Programas", "tipo": "Código/Texto"},
    {"campo": "Malla Curricular", "sinonimos": ["Malla Curricular", "Malla"], "seccion": "Malla Curricular", "tipo": "Archivo/Texto"},
    {"campo": "Perfil de Egreso", "sinonimos": ["Perfil de Egreso", "PERFIL_EGRESO"], "seccion": "No confirmado como tabla de Nuevos Programas", "tipo": "Texto"},
]

EXPLICIT_EQUIVALENCES = {
    "ANIO_INICIO": ["ANO_DE_INICIO_DE_ACTIVIDADES", "ANIOINICIOACTIVIDADES"],
    "ANO_INICIO": ["ANO_DE_INICIO_DE_ACTIVIDADES", "ANIOINICIOACTIVIDADES"],
    "AÑO_INICIO": ["ANO_DE_INICIO_DE_ACTIVIDADES", "ANIOINICIOACTIVIDADES"],
    "REGIMEN": ["TIPO_REGIMEN"],
    "DURACION_REGIMEN": ["DURACION", "DURACION_EN_SEMESTRES"],
    "NOMBRE_TITULO": ["TITULO"],
    "AREA_ACTUAL": ["AREA_SUBAREA_CARRERA_GENERICA", "AREA_DEL_CONOCIMIENTO"],
    "REQUISITO_INGRESO": ["FORMAS_DE_INGRESO"],
    "VIGENCIA_CARRERA": ["ESTADO_DE_LA_CARRERA_O_PROGRAMA", "ESTADO_DEL_PROGRAMA", "VIGENCIA"],
    "CODIGO_UNICO": ["CODIGO_UNICO"],
    "COD_CARRERA": ["CODIGO_DE_CARRERA"],
    "COD_CARRERA_DERIVADO": ["CODIGO_DE_CARRERA"],
    "MODALIDAD": ["MODALIDAD_DEL_PROGRAMA"],
    "MODALIDAD_ORIGINAL": ["MODALIDAD_DEL_PROGRAMA"],
    "JORNADA": ["HORARIO", "JORNADA"],
    "VERSION": ["VERSION"],
    "VERSION_DERIVADA": ["VERSION"],
    "SEMESTRES_RECONOCIDOS": ["SEMESTRES_RECONOCIDOS"],
    "ACREDITACION": ["ACREDITACION"],
    "VACANTES_PRIMER_SEMESTRE": ["VACANTES_PRIMER_SEMESTRE"],
    "VACANTES_SEGUNDO_SEMESTRE": ["VACANTES_SEGUNDO_SEMESTRE"],
    "ARANCEL_ANUAL": ["VALOR_ARANCEL_ANUAL"],
    "VALOR_MATRICULA_ANUAL": ["VALOR_DE_LA_MATRICULA"],
    "COSTO_TITULACION": ["VALOR_TITULACION"],
    "FORMATO_VALOR": ["TIPO_MONEDA"],
}


def normalize(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def compact(value: Any) -> str:
    return normalize(value).replace("_", "")


def sha256_short(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def run_guardrail() -> str:
    result = subprocess.run(
        [sys.executable, "cned/scripts/check_no_tocar_mu2026.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        raise RuntimeError(f"Guardrail MU2026 falló:\n{output}")
    return output


def discover_manual_sources() -> list[Path]:
    candidates = []
    if MANUAL_PRIORITARIO.exists():
        candidates.append(MANUAL_PRIORITARIO)
    for pattern in [
        "indices_2025/docs/*Manual*INDICES*.txt",
        "indices_2025/docs/*Manual*INDICES*.pdf",
        "archive/**/manual*.txt",
        "archive/**/*INDICES*.txt",
        "docs/**/*INDICES*.txt",
    ]:
        for path in ROOT.glob(pattern):
            if path.is_file() and path not in candidates:
                name = str(path)
                if any(part in name for part in ["/.git/", "/.venv/", "__pycache__"]):
                    continue
                candidates.append(path)
    return candidates


def read_manual_text(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def find_context(text: str, phrases: list[str]) -> tuple[str, str]:
    norm_to_original = text
    normalized_text = normalize(text)
    for phrase in phrases:
        cp = compact(phrase)
        if not cp:
            continue
        compact_text = compact(normalized_text)
        pos = compact_text.find(cp)
        if pos >= 0:
            # Approximate context on original text by direct regex when possible.
            patt = re.compile(re.escape(str(phrase)), re.IGNORECASE)
            match = patt.search(norm_to_original)
            if match:
                start = max(0, match.start() - 180)
                end = min(len(norm_to_original), match.end() + 260)
                snippet = " ".join(norm_to_original[start:end].split())
            else:
                snippet = f"Coincidencia normalizada detectada para: {phrase}"
            return "CONFIRMADO_EN_MANUAL", snippet
    # Token overlap only as possible equivalence.
    manual_tokens = set(normalized_text.split("_"))
    best_phrase = ""
    best_score = 0.0
    for phrase in phrases:
        toks = {t for t in normalize(phrase).split("_") if len(t) > 2}
        if not toks:
            continue
        score = len(toks & manual_tokens) / len(toks)
        if score > best_score:
            best_score = score
            best_phrase = phrase
    if best_score >= 0.75:
        return "POSIBLE_EQUIVALENCIA_REQUIERE_VALIDACION", f"Tokens del campo aparecen en el manual, pero no como etiqueta exacta: {best_phrase}"
    return "NO_CONFIRMADO_EN_MANUAL", "No se encontró etiqueta ni equivalencia explícita en las fuentes normativas locales revisadas."


def build_manual_dictionary(source: Path, text: str) -> pd.DataFrame:
    rows = []
    for item in EXPECTED_FIELDS:
        status, snippet = find_context(text, item["sinonimos"])
        rows.append(
            {
                "CAMPO_MANUAL": item["campo"],
                "CAMPO_NORMALIZADO": normalize(item["campo"]),
                "SECCION_MANUAL": item["seccion"],
                "DESCRIPCION_MANUAL": snippet,
                "TIPO_CAMPO_MANUAL": item["tipo"],
                "OBLIGATORIEDAD_MANUAL": "NO_DETERMINADA_EN_EXTRACCION",
                "OBSERVACION": "Campo de lista objetivo Hito 7 BIS; obligatoriedad no se asume si el manual no la explicita.",
                "FUENTE_ARCHIVO": str(source.relative_to(ROOT)),
                "ESTADO_FUENTE": status,
            }
        )
    return pd.DataFrame(rows)


def choose_base_sheet(path: Path) -> str:
    wb = load_workbook(path, read_only=True, data_only=True)
    names = wb.sheetnames
    for name in SHEET_PREFERENCE:
        if name in names:
            wb.close()
            return name
    stats = []
    for ws in wb.worksheets:
        stats.append((ws.max_row * ws.max_column, ws.title))
    wb.close()
    return sorted(stats, reverse=True)[0][1]


def examples(series: pd.Series, limit: int = 8) -> str:
    vals = []
    for value in series.dropna().astype(str).tolist():
        if value.strip() == "":
            continue
        if value not in vals:
            vals.append(value)
        if len(vals) >= limit:
            break
    return " | ".join(vals)


def read_real_columns(path: Path) -> tuple[str, pd.DataFrame, pd.DataFrame]:
    sheet = choose_base_sheet(path)
    df = pd.read_excel(path, sheet_name=sheet, dtype=object)
    rows = []
    total = len(df)
    for col in df.columns:
        s = df[col]
        non_empty = int(s.notna().sum() - (s.fillna("").astype(str).str.strip() == "").sum())
        rows.append(
            {
                "COLUMNA_REAL": col,
                "COLUMNA_NORMALIZADA": normalize(col),
                "TOTAL_FILAS": total,
                "NO_VACIOS": non_empty,
                "VACIOS": total - non_empty,
                "PORCENTAJE_COMPLETITUD": round((non_empty / total * 100) if total else 0, 2),
                "VALORES_UNICOS": int(s.nunique(dropna=True)),
                "EJEMPLOS": examples(s),
                "CONTIENE_MARCAS_TECNICAS": bool(s.fillna("").astype(str).str.contains(r"REVISAR|CONFLICTO|DECISION|MATCH_", case=False, regex=True).any()),
                "HOJA_BASE": sheet,
            }
        )
    return sheet, df, pd.DataFrame(rows)


def token_similarity(a: str, b: str) -> float:
    ta = {t for t in normalize(a).split("_") if t}
    tb = {t for t in normalize(b).split("_") if t}
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def map_column(col_norm: str, manual_df: pd.DataFrame) -> dict[str, Any]:
    manual_confirmed = manual_df[manual_df["ESTADO_FUENTE"].isin(["CONFIRMADO_EN_MANUAL", "POSIBLE_EQUIVALENCIA_REQUIERE_VALIDACION"])].copy()
    manual_confirmed["COMPACT"] = manual_confirmed["CAMPO_NORMALIZADO"].map(compact)
    col_compact = compact(col_norm)

    exact = manual_confirmed[manual_confirmed["CAMPO_NORMALIZADO"] == col_norm]
    if not exact.empty:
        row = exact.iloc[0]
        return {"CAMPO_MANUAL_MAPEADO": row["CAMPO_MANUAL"], "METODO_MAPEO": "EXACTO_NORMALIZADO", "SCORE_MAPEO": 1.0, "ESTADO_FUENTE_MANUAL": row["ESTADO_FUENTE"]}

    for source, targets in EXPLICIT_EQUIVALENCES.items():
        if col_norm == source or col_norm in [normalize(t) for t in targets]:
            for target in targets:
                target_norm = normalize(target)
                candidate = manual_confirmed[manual_confirmed["CAMPO_NORMALIZADO"] == target_norm]
                if candidate.empty:
                    candidate = manual_confirmed[manual_confirmed["CAMPO_NORMALIZADO"].map(compact) == compact(target)]
                if not candidate.empty:
                    row = candidate.iloc[0]
                    return {"CAMPO_MANUAL_MAPEADO": row["CAMPO_MANUAL"], "METODO_MAPEO": "EQUIVALENCIA_EXPLICITA", "SCORE_MAPEO": 0.98, "ESTADO_FUENTE_MANUAL": row["ESTADO_FUENTE"]}
            # Equivalence was defined but manual label itself was not confirmed.
            return {"CAMPO_MANUAL_MAPEADO": targets[0], "METODO_MAPEO": "EQUIVALENCIA_EXPLICITA_NO_CONFIRMADA", "SCORE_MAPEO": 0.75, "ESTADO_FUENTE_MANUAL": "POSIBLE_EQUIVALENCIA_REQUIERE_VALIDACION"}

    contains = manual_confirmed[
        manual_confirmed["CAMPO_NORMALIZADO"].map(lambda x: compact(x) in col_compact or col_compact in compact(x))
    ]
    if not contains.empty and len(col_compact) >= 4:
        row = contains.iloc[0]
        return {"CAMPO_MANUAL_MAPEADO": row["CAMPO_MANUAL"], "METODO_MAPEO": "CONTIENE_O_CONTENIDO", "SCORE_MAPEO": 0.82, "ESTADO_FUENTE_MANUAL": row["ESTADO_FUENTE"]}

    scored = []
    for _, row in manual_confirmed.iterrows():
        score = token_similarity(col_norm, row["CAMPO_NORMALIZADO"])
        scored.append((score, row))
    if scored:
        score, row = max(scored, key=lambda item: item[0])
        if score >= 0.45:
            return {"CAMPO_MANUAL_MAPEADO": row["CAMPO_MANUAL"], "METODO_MAPEO": "SIMILITUD_TOKENS", "SCORE_MAPEO": round(score, 3), "ESTADO_FUENTE_MANUAL": row["ESTADO_FUENTE"]}

    return {"CAMPO_MANUAL_MAPEADO": "", "METODO_MAPEO": "SIN_MAPEO", "SCORE_MAPEO": 0.0, "ESTADO_FUENTE_MANUAL": "NO_CONFIRMADO_EN_MANUAL"}


def classify_column(col_norm: str, mapped: dict[str, Any]) -> str:
    if any(pat in col_norm for pat in AUXILIARY_PATTERNS):
        return "AUXILIAR_TECNICA"
    if col_norm in {"FUENTE", "OBSERVACION_AUDITORIA", "OBSERVACIONES_TRAZABILIDAD"}:
        return "TRAZABILIDAD_INTERNA"
    estado = mapped["ESTADO_FUENTE_MANUAL"]
    method = mapped["METODO_MAPEO"]
    if estado == "CONFIRMADO_EN_MANUAL":
        if col_norm in OFFICIAL_CORE_NORMALIZED or mapped["CAMPO_MANUAL_MAPEADO"] in {"Código único", "Código de carrera", "Sede", "Jornada", "Versión", "Vigencia", "Duración régimen", "Requisito ingreso", "Semestres reconocidos", "Acreditación", "Área actual"}:
            return "OFICIAL_CNED_CONFIRMADO"
        return "FORMULARIO_CNED_CONFIRMADO"
    if estado == "POSIBLE_EQUIVALENCIA_REQUIERE_VALIDACION" or method in {"SIMILITUD_TOKENS", "CONTIENE_O_CONTENIDO", "EQUIVALENCIA_EXPLICITA_NO_CONFIRMADA"}:
        return "REQUIERE_REVISION_MANUAL"
    return "NO_CONFIRMADO_EN_MANUAL"


def build_mapping(real_df: pd.DataFrame, manual_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in real_df.iterrows():
        col_norm = row["COLUMNA_NORMALIZADA"]
        mapped = map_column(col_norm, manual_df)
        classification = classify_column(col_norm, mapped)
        rows.append({**row.to_dict(), **mapped, "RECLASIFICACION_HITO7BIS": classification})
    return pd.DataFrame(rows)


def read_hito6() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    resumen = pd.read_excel(HITO6, sheet_name="RESUMEN_POR_CAMPO", dtype=object)
    oficiales = pd.read_excel(HITO6, sheet_name="CAMPOS_OFICIALES", dtype=object)
    formulario = pd.read_excel(HITO6, sheet_name="CAMPOS_FORMULARIO", dtype=object)
    auxiliares = pd.read_excel(HITO6, sheet_name="CAMPOS_AUXILIARES", dtype=object)
    return resumen, oficiales, formulario, auxiliares


def build_impact(hito6_resumen: pd.DataFrame, mapping_df: pd.DataFrame) -> pd.DataFrame:
    map_by_norm = (
        mapping_df.drop_duplicates(subset=["COLUMNA_NORMALIZADA"], keep="first")
        .set_index("COLUMNA_NORMALIZADA")
        .to_dict(orient="index")
    )
    rows = []
    for _, row in hito6_resumen.iterrows():
        campo = row["campo"]
        n = normalize(campo)
        mapped = map_by_norm.get(n)
        if not mapped:
            # Try loose exact against real column labels.
            candidates = mapping_df[mapping_df["COLUMNA_NORMALIZADA"].map(lambda x: x == n or compact(x) == compact(n))]
            mapped = candidates.iloc[0].to_dict() if not candidates.empty else {}
        reclass = mapped.get("RECLASIFICACION_HITO7BIS", "NO_CONFIRMADO_EN_MANUAL")
        estado_manual = mapped.get("ESTADO_FUENTE_MANUAL", "NO_CONFIRMADO_EN_MANUAL")
        if row.get("tipo_campo") == "AUXILIAR_TECNICA" or reclass == "AUXILIAR_TECNICA":
            impacto = "AUXILIAR_EXCLUIBLE_DE_CARGA"
        elif reclass in {"OFICIAL_CNED_CONFIRMADO", "FORMULARIO_CNED_CONFIRMADO"}:
            impacto = "CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA"
        elif reclass == "REQUIERE_REVISION_MANUAL":
            impacto = "REQUIERE_VALIDACION_DE_EQUIVALENCIA"
        else:
            impacto = "SIGUE_NO_CONFIRMADO_EN_MANUAL"
        rows.append(
            {
                **row.to_dict(),
                "campo_normalizado": n,
                "CAMPO_MANUAL_MAPEADO": mapped.get("CAMPO_MANUAL_MAPEADO", ""),
                "METODO_MAPEO": mapped.get("METODO_MAPEO", "SIN_MAPEO"),
                "ESTADO_FUENTE_MANUAL": estado_manual,
                "RECLASIFICACION_HITO7BIS": reclass,
                "IMPACTO_HITO7BIS": impacto,
            }
        )
    return pd.DataFrame(rows)


def make_plan(impact_df: pd.DataFrame, mapping_df: pd.DataFrame) -> pd.DataFrame:
    confirmed_blockers = impact_df[
        (impact_df["bloquea_subida"].astype(str).str.upper() == "SI")
        & (impact_df["RECLASIFICACION_HITO7BIS"].isin(["OFICIAL_CNED_CONFIRMADO", "FORMULARIO_CNED_CONFIRMADO"]))
    ]
    still_unknown = impact_df[impact_df["IMPACTO_HITO7BIS"] == "SIGUE_NO_CONFIRMADO_EN_MANUAL"]
    return pd.DataFrame(
        [
            {
                "orden": 1,
                "accion": "Actualizar Hito 5/Hito 6 con diccionario manual",
                "detalle": "Reclasificar campos confirmados por Manual INDICES para evitar tratarlos como desconocidos.",
                "salida_esperada": f"{len(confirmed_blockers)} campos bloqueantes/formulario con respaldo manual quedan trazables.",
            },
            {
                "orden": 2,
                "accion": "Separar auxiliares de carga",
                "detalle": "Excluir solo columnas claramente auxiliares/trace del candidato de carga; mantenerlas en auditoría.",
                "salida_esperada": "Campos AUXILIAR_TECNICA fuera de la hoja operativa de carga.",
            },
            {
                "orden": 3,
                "accion": "Resolver campos confirmados que tienen marcas",
                "detalle": "No basta confirmar que el campo existe; se debe reemplazar la marca técnica por fuente institucional válida.",
                "salida_esperada": "Hito 5 reejecutado sin marcas en campos oficiales confirmados.",
            },
            {
                "orden": 4,
                "accion": "Validar campos no confirmados",
                "detalle": f"Revisar {len(still_unknown)} campos que no aparecen en el manual local o no tienen equivalencia suficiente.",
                "salida_esperada": "Decisión institucional: excluir, mantener trazabilidad o aportar fuente normativa.",
            },
            {
                "orden": 5,
                "accion": "No generar carga final todavía",
                "detalle": "El Hito 7 BIS solo entrega diccionario, mapeo e impacto. La subida requiere reejecutar saneamiento y validación.",
                "salida_esperada": "Sin archivo final CNED declarado.",
            },
        ]
    )


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)


def validate_excel(path: Path, expected_sheets: list[str]) -> None:
    wb = load_workbook(path, read_only=True, data_only=False)
    missing = [s for s in expected_sheets if s not in wb.sheetnames]
    overlong = [s for s in wb.sheetnames if len(s) > 31]
    formulas = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    formulas.append(f"{ws.title}!{cell.coordinate}")
                    break
            if formulas:
                break
    wb.close()
    if missing:
        raise RuntimeError(f"Faltan hojas esperadas en Excel: {missing}")
    if overlong:
        raise RuntimeError(f"Hojas con nombre mayor a 31 caracteres: {overlong}")
    if formulas:
        raise RuntimeError(f"Se detectaron fórmulas en Excel generado: {formulas[:5]}")


def write_outputs(
    manual_df: pd.DataFrame,
    real_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
    impact_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    summary: dict[str, Any],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    confirmed_official = mapping_df[mapping_df["RECLASIFICACION_HITO7BIS"] == "OFICIAL_CNED_CONFIRMADO"]
    confirmed_form = mapping_df[mapping_df["RECLASIFICACION_HITO7BIS"] == "FORMULARIO_CNED_CONFIRMADO"]
    not_confirmed = mapping_df[mapping_df["RECLASIFICACION_HITO7BIS"] == "NO_CONFIRMADO_EN_MANUAL"]
    aux = mapping_df[mapping_df["RECLASIFICACION_HITO7BIS"] == "AUXILIAR_TECNICA"]
    reclass = mapping_df[
        [
            "COLUMNA_REAL",
            "COLUMNA_NORMALIZADA",
            "CAMPO_MANUAL_MAPEADO",
            "METODO_MAPEO",
            "SCORE_MAPEO",
            "ESTADO_FUENTE_MANUAL",
            "RECLASIFICACION_HITO7BIS",
            "CONTIENE_MARCAS_TECNICAS",
        ]
    ].copy()

    resumen_df = pd.DataFrame([{"campo": k, "valor": v} for k, v in summary.items()])
    expected_sheets = [
        "RESUMEN_EJECUTIVO",
        "DICCIONARIO_MANUAL_CNED",
        "COLUMNAS_REALES_BASE",
        "MAPEO_COLUMNAS_MANUAL",
        "RECLASIFICACION_CAMPOS",
        "CAMPOS_OFICIALES_CONFIRMADOS",
        "CAMPOS_FORMULARIO_CONFIRMADOS",
        "CAMPOS_NO_CONFIRMADOS",
        "CAMPOS_AUXILIARES_TECNICOS",
        "IMPACTO_SOBRE_BLOQUEOS_HITO6",
        "PLAN_ACCION_POST_DICCIONARIO",
    ]
    with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as writer:
        resumen_df.to_excel(writer, sheet_name="RESUMEN_EJECUTIVO", index=False)
        manual_df.to_excel(writer, sheet_name="DICCIONARIO_MANUAL_CNED", index=False)
        real_df.to_excel(writer, sheet_name="COLUMNAS_REALES_BASE", index=False)
        mapping_df.to_excel(writer, sheet_name="MAPEO_COLUMNAS_MANUAL", index=False)
        reclass.to_excel(writer, sheet_name="RECLASIFICACION_CAMPOS", index=False)
        confirmed_official.to_excel(writer, sheet_name="CAMPOS_OFICIALES_CONFIRMADOS", index=False)
        confirmed_form.to_excel(writer, sheet_name="CAMPOS_FORMULARIO_CONFIRMADOS", index=False)
        not_confirmed.to_excel(writer, sheet_name="CAMPOS_NO_CONFIRMADOS", index=False)
        aux.to_excel(writer, sheet_name="CAMPOS_AUXILIARES_TECNICOS", index=False)
        impact_df.to_excel(writer, sheet_name="IMPACTO_SOBRE_BLOQUEOS_HITO6", index=False)
        plan_df.to_excel(writer, sheet_name="PLAN_ACCION_POST_DICCIONARIO", index=False)
    validate_excel(EXCEL_OUT, expected_sheets)

    write_csv(CSV_DICT_OUT, manual_df)
    write_csv(CSV_MAP_OUT, mapping_df)
    write_csv(CSV_IMPACT_OUT, impact_df)
    JSON_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    official_blockers = impact_df[
        (impact_df["bloquea_subida"].astype(str).str.upper() == "SI")
        & (impact_df["RECLASIFICACION_HITO7BIS"].isin(["OFICIAL_CNED_CONFIRMADO", "FORMULARIO_CNED_CONFIRMADO"]))
    ]
    still_unknown = impact_df[impact_df["IMPACTO_HITO7BIS"] == "SIGUE_NO_CONFIRMADO_EN_MANUAL"]
    md = f"""# CNED Hito 7 BIS - Diccionario oficial aplicado

## Resumen

- Fecha de generación: {summary['fecha_generacion']}
- Manual/fuente principal: `{summary['manual_principal']}`
- Base real auditada: `{summary['base_hito5']}`
- Hoja real auditada: `{summary['hoja_base_usada']}`
- Campos del diccionario manual: {summary['campos_diccionario_manual']}
- Columnas reales mapeadas: {summary['columnas_reales_base']}
- Campos confirmados oficiales: {summary['campos_oficiales_confirmados']}
- Campos confirmados de formulario: {summary['campos_formulario_confirmados']}
- Campos no confirmados en manual: {summary['campos_no_confirmados']}
- Campos auxiliares técnicos: {summary['campos_auxiliares_tecnicos']}
- Dictamen: **{summary['dictamen_final']}**

## Fuente usada

Se usó como fuente normativa principal el Manual INDICES local disponible en
`{summary['manual_principal']}`. La sección más relevante detectada es
**Tabla 21: Nuevos Programas**, complementada con **Tabla 22: Evolución Programas**
y **CSV Evolución Carreras** para campos de evolución/carga.

No se usó conocimiento externo ni búsqueda web. Cuando el manual no confirmó una
etiqueta o equivalencia, el campo quedó como `NO_CONFIRMADO_EN_MANUAL` o
`REQUIERE_REVISION_MANUAL`.

## Impacto sobre Hito 6

- Campos Hito 6 antes clasificados con bloqueo/marca: {summary['campos_hito6_evaluados']}
- Campos Hito 6 confirmados por manual o equivalencia: {summary['bloqueos_confirmados_por_manual']}
- Campos Hito 6 auxiliares excluibles de carga: {summary['bloqueos_auxiliares_excluibles']}
- Campos Hito 6 que siguen no confirmados: {summary['bloqueos_no_confirmados']}

### Campos bloqueantes confirmados

{official_blockers[['campo','tipo_campo','CAMPO_MANUAL_MAPEADO','RECLASIFICACION_HITO7BIS','IMPACTO_HITO7BIS']].to_markdown(index=False) if not official_blockers.empty else 'No se detectaron campos bloqueantes confirmados.'}

### Campos que siguen sin confirmación suficiente

{still_unknown[['campo','tipo_campo','total_marcas','IMPACTO_HITO7BIS']].head(30).to_markdown(index=False) if not still_unknown.empty else 'No quedan campos Hito 6 sin confirmación manual.'}

## Recomendación

1. Ajustar Hito 5/Hito 6 para usar este diccionario y no tratar como desconocidos los campos confirmados por Manual INDICES.
2. Mantener fuera de la carga solo campos `AUXILIAR_TECNICA` claros, conservándolos en trazabilidad.
3. Resolver marcas técnicas en campos oficiales/formulario confirmados con fuente institucional; confirmar existencia del campo no equivale a completar su valor.
4. No generar archivo final CNED hasta reejecutar el saneamiento y validar contra instructivo/estructura oficial de carga.

## Advertencia

Este Hito 7 BIS no genera archivo final de subida CNED. Solo entrega diccionario,
mapeo, reclasificación e impacto metodológico.
"""
    MD_OUT.write_text(md, encoding="utf-8")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    guardrail_before = run_guardrail()
    manual_sources = discover_manual_sources()
    if not manual_sources:
        raise FileNotFoundError("No se encontraron fuentes locales tipo Manual INDICES/CNED.")
    manual_source = manual_sources[0]
    manual_text = read_manual_text(manual_source)
    if not manual_text:
        raise RuntimeError(f"No se pudo leer texto del manual principal: {manual_source}")
    if not INPUT_BASE.exists():
        raise FileNotFoundError(INPUT_BASE)
    if not HITO6.exists():
        raise FileNotFoundError(HITO6)

    manual_df = build_manual_dictionary(manual_source, manual_text)
    hoja_base, _base_df, real_df = read_real_columns(INPUT_BASE)
    mapping_df = build_mapping(real_df, manual_df)
    hito6_resumen, _oficiales, _formulario, _auxiliares = read_hito6()
    impact_df = build_impact(hito6_resumen, mapping_df)
    plan_df = make_plan(impact_df, mapping_df)

    counts = Counter(mapping_df["RECLASIFICACION_HITO7BIS"])
    impact_counts = Counter(impact_df["IMPACTO_HITO7BIS"])
    summary = {
        "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
        "manual_principal": str(manual_source.relative_to(ROOT)),
        "manual_sha256_16": sha256_short(manual_source),
        "fuentes_locales_detectadas": len(manual_sources),
        "base_hito5": str(INPUT_BASE.relative_to(ROOT)),
        "base_hito5_sha256_16": sha256_short(INPUT_BASE),
        "hito6_matriz": str(HITO6.relative_to(ROOT)),
        "hito6_sha256_16": sha256_short(HITO6),
        "hoja_base_usada": hoja_base,
        "campos_diccionario_manual": len(manual_df),
        "campos_confirmados_en_manual": int((manual_df["ESTADO_FUENTE"] == "CONFIRMADO_EN_MANUAL").sum()),
        "campos_posible_equivalencia_manual": int((manual_df["ESTADO_FUENTE"] == "POSIBLE_EQUIVALENCIA_REQUIERE_VALIDACION").sum()),
        "campos_no_confirmados_manual": int((manual_df["ESTADO_FUENTE"] == "NO_CONFIRMADO_EN_MANUAL").sum()),
        "columnas_reales_base": len(mapping_df),
        "campos_oficiales_confirmados": counts["OFICIAL_CNED_CONFIRMADO"],
        "campos_formulario_confirmados": counts["FORMULARIO_CNED_CONFIRMADO"],
        "campos_no_confirmados": counts["NO_CONFIRMADO_EN_MANUAL"],
        "campos_auxiliares_tecnicos": counts["AUXILIAR_TECNICA"],
        "campos_requieren_revision_manual": counts["REQUIERE_REVISION_MANUAL"],
        "campos_hito6_evaluados": len(impact_df),
        "bloqueos_confirmados_por_manual": impact_counts["CAMPO_CONFIRMADO_POR_MANUAL_O_EQUIVALENCIA"],
        "bloqueos_auxiliares_excluibles": impact_counts["AUXILIAR_EXCLUIBLE_DE_CARGA"],
        "bloqueos_no_confirmados": impact_counts["SIGUE_NO_CONFIRMADO_EN_MANUAL"],
        "bloqueos_requieren_validacion_equivalencia": impact_counts["REQUIERE_VALIDACION_DE_EQUIVALENCIA"],
        "excel_salida": str(EXCEL_OUT.relative_to(ROOT)),
        "markdown_salida": str(MD_OUT.relative_to(ROOT)),
        "csv_diccionario": str(CSV_DICT_OUT.relative_to(ROOT)),
        "csv_mapeo": str(CSV_MAP_OUT.relative_to(ROOT)),
        "csv_impacto": str(CSV_IMPACT_OUT.relative_to(ROOT)),
        "json_resumen": str(JSON_OUT.relative_to(ROOT)),
        "guardrail_mu2026_inicio": guardrail_before,
        "dictamen_final": "DICTAMEN_FINAL: HITO7BIS_DICCIONARIO_OFICIAL_CNED_GENERADO",
    }
    write_outputs(manual_df, real_df, mapping_df, impact_df, plan_df, summary)

    for path in [EXCEL_OUT, MD_OUT, CSV_DICT_OUT, CSV_MAP_OUT, CSV_IMPACT_OUT, JSON_OUT]:
        if not path.exists():
            raise RuntimeError(f"No se generó salida esperada: {path}")
        if not str(path.relative_to(ROOT)).startswith("cned/"):
            raise RuntimeError(f"Salida fuera de cned/: {path}")
    guardrail_after = run_guardrail()
    summary["guardrail_mu2026_final"] = guardrail_after
    JSON_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("======================================================================")
    print("HITO 7 BIS CNED - DICCIONARIO OFICIAL APLICADO")
    print("======================================================================")
    print(f"Manual principal: {summary['manual_principal']}")
    print(f"Hoja base usada: {hoja_base}")
    print(f"Campos diccionario manual: {len(manual_df)}")
    print(f"Campos confirmados en manual: {summary['campos_confirmados_en_manual']}")
    print(f"Columnas reales base: {len(mapping_df)}")
    print(f"Oficiales confirmados: {summary['campos_oficiales_confirmados']}")
    print(f"Formulario confirmados: {summary['campos_formulario_confirmados']}")
    print(f"No confirmados: {summary['campos_no_confirmados']}")
    print(f"Auxiliares técnicos: {summary['campos_auxiliares_tecnicos']}")
    print(f"Impacto Hito 6 confirmado: {summary['bloqueos_confirmados_por_manual']}")
    print(f"Impacto Hito 6 no confirmado: {summary['bloqueos_no_confirmados']}")
    print(f"Excel: {EXCEL_OUT}")
    print(f"Markdown: {MD_OUT}")
    print(f"CSV diccionario: {CSV_DICT_OUT}")
    print(f"CSV mapeo: {CSV_MAP_OUT}")
    print(f"CSV impacto: {CSV_IMPACT_OUT}")
    print(f"JSON: {JSON_OUT}")
    print(guardrail_after)
    print(summary["dictamen_final"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
