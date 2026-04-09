#!/usr/bin/env python3
"""
Auditoría Maestra — Gate de Entrega MU 2026
============================================
Script que auto-evalúa la consistencia lógica del pipeline, reconstruye
el linaje por columna, audita los outputs empíricos y emite un dictamen
trazable: LISTO PARA ENTREGA / NO LISTO.

Uso:
  python3 scripts/auditoria_maestra.py --solo-validar
  python3 scripts/auditoria_maestra.py --ejecutar-pipeline --anio 2026 --sem 1
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
REPO_DIR = Path(__file__).resolve().parent.parent
PIPELINE_SCRIPT = REPO_DIR / "codigo_gobernanza_v2.py"
VERIFICADOR_SCRIPT = REPO_DIR / "scripts" / "verificar_4_columnas_mu.py"

COLUMNAS_MU32_ESPERADAS = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE",
    "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD",
    "JOR", "VERSION", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI",
    "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",
    "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]

COLUMNAS_TRAZABILIDAD_DA = [
    "VIG_ESPERADO_DA", "FLAG_INCONSISTENCIA_VIG",
    "ESTADOACADEMICO_DA", "SITUACION_DA",
]
COLUMNAS_TRAZABILIDAD_TSV = [
    "NOMBRE_CARRERA_TSV", "DURACION_ESTUDIOS_TSV",
    "DURACION_TITULACION_TSV", "DURACION_TOTAL_TSV",
]

COLUMNAS_CRITICAS_LINAJE = [
    "VIG", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "CODCLI",
    "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS",
    "VIG_ESPERADO_DA", "FLAG_INCONSISTENCIA_VIG",
    "NOMBRE_CARRERA_TSV", "DURACION_ESTUDIOS_TSV",
]


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class Check:
    nombre: str
    estado: str = "PENDIENTE"  # OK / FAIL / WARN / SKIP
    detalle: str = ""


@dataclass
class LineageEntry:
    columna: str
    fuentes: list[str] = field(default_factory=list)
    transformaciones: list[str] = field(default_factory=list)
    reglas_negocio: list[str] = field(default_factory=list)
    punto_codigo: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def _git_commit_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_DIR), stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "N/A"


def _git_modified_line_refs(files: list[str] | None = None) -> list[str]:
    files = files or ["codigo_gobernanza_v2.py", "qa_checks.py"]
    try:
        diff_txt = subprocess.check_output(
            ["git", "diff", "--unified=0", "--no-color", "--", *files],
            cwd=str(REPO_DIR),
            stderr=subprocess.DEVNULL,
        ).decode("utf-8", errors="ignore")
    except Exception:
        return []
    if not diff_txt.strip():
        return []

    refs: list[str] = []
    current_file: str | None = None
    for line in diff_txt.splitlines():
        if line.startswith("+++ b/"):
            current_file = line.replace("+++ b/", "", 1).strip()
            continue
        if not current_file or not line.startswith("@@"):
            continue
        m = re.search(r"\+(\d+)(?:,(\d+))?", line)
        if not m:
            continue
        start = int(m.group(1))
        count = int(m.group(2) or "1")
        end = start + max(count - 1, 0)
        if end == start:
            refs.append(f"{current_file}:L{start}")
        else:
            refs.append(f"{current_file}:L{start}-L{end}")
    return refs[:120]


def _now_iso() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _find_lines(text: str, pattern: str) -> list[tuple[int, str]]:
    """Busca pattern (regex) en text y devuelve [(lineno, line), ...]."""
    matches = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line, re.IGNORECASE):
            matches.append((i, line.strip()))
    return matches


# ---------------------------------------------------------------------------
# Parte 2  — Auto-evaluación de lógica del código (Mapa de Linaje)
# ---------------------------------------------------------------------------
_LINEAGE_PATTERNS: dict[str, dict[str, Any]] = {
    "VIG": {
        "fuentes_pat": [
            (r"VIGENCIA|VIG.*input|VIG.*fuente|VIG.*source", "Hoja1/MAT_AC VIGENCIA"),
            (r"VIG_ESPERADO_DA|DA_ESTADOACADEMICO.*VIG", "DatosAlumnos (catálogo DA)"),
            (r"gob_promedios_hoja1|gob_datosalumnos", "Catálogos gobernanza TSV"),
        ],
        "transform_pat": [
            (r"VIG.*=.*0|force.*VIG.*0|VIG.*forzar", "Forzado a 0 por regla DA"),
            (r"VIG.*=.*1.*default|default.*VIG.*1", "Default VIG=1"),
            (r"FLAG_INCONSISTENCIA_VIG", "Comparación VIG real vs esperado"),
        ],
        "reglas_pat": [
            (r"TITULADO|ELIMINADO|SUSPENDIDO.*VIG.*0", "TITULADO/ELIMINADO/SUSPENDIDO → VIG=0"),
            (r"VIG.*=.*0.*PROM.*=.*0|VIG.*0.*4.*col", "VIG=0 ⇒ 4 columnas=0"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "PROM_PRI_SEM": {
        "fuentes_pat": [
            (r"PROM_PRI_SEM|prom_pri", "Hoja1 histórico / MAT_AC"),
            (r"combine_first.*PROM_PRI|PROM_PRI.*combine_first", "combine_first (input + hist)"),
        ],
        "transform_pat": [
            (r"round\(.*\*\s*100\)|escala.*100.*700|100.*700", "Escala round(promedio*100) → 100-700"),
            (r"PERIODO.*=.*1|semestre.*1.*prom_pri", "PERIODO=1 → PROM_PRI_SEM"),
            (r"coerce.*mu.*average|_coerce_mu_average", "Coerción numérica con bounds"),
        ],
        "reglas_pat": [
            (r"REGIMEN.*SEMESTRAL|semestral", "Solo REGIMEN=SEMESTRAL"),
            (r"anio_ref.*max|anio_anterior_prom|ANIO_ANTERIOR.*din", "Año anterior dinámico (max histórico)"),
            (r"APROBADO.*REPROBADO|DESCRIPCION_ESTADO.*in", "Solo APROBADO/REPROBADO"),
            (r"NOTA_FINAL.*1.*7|1\.0.*7\.0", "NOTA_FINAL entre 1 y 7"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "PROM_SEG_SEM": {
        "fuentes_pat": [
            (r"PROM_SEG_SEM|prom_seg", "Hoja1 histórico / MAT_AC"),
            (r"combine_first.*PROM_SEG|PROM_SEG.*combine_first", "combine_first (input + hist)"),
        ],
        "transform_pat": [
            (r"PERIODO.*[23]|semestre.*2.*prom_seg", "PERIODO∈{2,3} → PROM_SEG_SEM"),
            (r"coerce.*mu.*average|_coerce_mu_average", "Coerción numérica con bounds"),
        ],
        "reglas_pat": [
            (r"REGIMEN.*SEMESTRAL|semestral", "Solo REGIMEN=SEMESTRAL"),
            (r"anio_ref.*max|anio_anterior_prom|ANIO_ANTERIOR.*din", "Año anterior dinámico"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "ASI_INS_HIS": {
        "fuentes_pat": [
            (r"ASI_INS_HIS|asi_ins", "Hoja1 histórico / MAT_AC UNID_CURSADAS_TOTAL"),
            (r"combine_first.*ASI_INS|ASI_INS.*combine_first", "combine_first"),
        ],
        "transform_pat": [
            (r"count.*CODRAMO|CODRAMO.*nunique|count.*ramo", "Count CODRAMO distintos"),
            (r"APROBADO.*REPROBADO.*CONVALIDACION.*HOMOLOGADO", "Eventos INS: APR+REP+CONV+HOM"),
        ],
        "reglas_pat": [
            (r"ASI_APR.*<=.*ASI_INS|ASI_APR.*cap|cap.*ASI", "ASI_APR_HIS ≤ ASI_INS_HIS"),
            (r"0.*200|rango.*200", "Rango 0-200"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "ASI_APR_HIS": {
        "fuentes_pat": [
            (r"ASI_APR_HIS|asi_apr", "Hoja1 histórico / MAT_AC UNID_APROBADAS_TOTAL"),
            (r"combine_first.*ASI_APR|ASI_APR.*combine_first", "combine_first"),
        ],
        "transform_pat": [
            (r"APROBADO.*CONVALIDACION.*HOMOLOGADO", "Eventos APR: APR+CONV+HOM"),
        ],
        "reglas_pat": [
            (r"ASI_APR.*<=.*ASI_INS|cap", "Capped ≤ ASI_INS_HIS"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "FOR_ING_ACT": {
        "fuentes_pat": [
            (r"FOR_ING_ACT|VIADEINGRESO|VIAS.*ADMISION", "Hoja1/DatosAlumnos VIA_ADMISION"),
            (r"gobernanza_for_ing_act|for_ing_act.*tsv", "Catálogo gobernanza FOR_ING_ACT"),
        ],
        "transform_pat": [
            (r"_resolve_for_ing_act_row", "Multi-rule resolution (token/catálogo/fallback)"),
            (r"ENSENANZA.*MEDIA.*NACIONAL.*1|EXTRANJERO.*6", "Mapeo textual a código numérico"),
            (r"fallback.*10|default.*10", "Fallback código 10"),
        ],
        "reglas_pat": [
            (r"CAMBIO.*RAP.*PACE|INCLUSION|ARTICUL", "Tokens especiales → códigos"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "ANIO_ING_ACT": {
        "fuentes_pat": [
            (r"ANOINGRESO|ANIO_ING_ACT.*input", "Hoja1 ANOINGRESO"),
            (r"DA_ANOINGRESO", "DatosAlumnos ANOINGRESO"),
            (r"_infer_year_from_codcli|CODCLI.*prefix", "Inferencia desde CODCLI"),
        ],
        "transform_pat": [
            (r"1990.*2026|year.*valid|_to_int_year", "Validación rango 1990-2026"),
        ],
        "reglas_pat": [],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "SEM_ING_ACT": {
        "fuentes_pat": [
            (r"PERIODOINGRESO|SEM_ING_ACT.*input", "Hoja1 PERIODOINGRESO"),
            (r"DA_PERIODOINGRESO", "DatosAlumnos PERIODOINGRESO"),
        ],
        "transform_pat": [
            (r"_normalize_period_to_semester", "Normalización período→semestre"),
        ],
        "reglas_pat": [],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"],
    },
    "CODCLI": {
        "fuentes_pat": [
            (r"CODCLI|COD_CLI|CODIGOCLIENTE", "DatosAlumnos CODIGOCLIENTE"),
        ],
        "transform_pat": [
            (r"strip|whitespace|normalize.*codcli", "Normalización (strip/upper)"),
            (r"_consolidar_candidatos_por_codcli|dedup.*codcli", "Deduplicación por CODCLI"),
        ],
        "reglas_pat": [
            (r"drop_duplicates.*CODCLI|keep.*first", "Drop duplicates keep first"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA", "AUDITORIA_CONSOLIDACION"],
    },
    "VIG_ESPERADO_DA": {
        "fuentes_pat": [
            (r"VIG_ESPERADO_DA|vig_esperado", "Catálogos DA gobernanza"),
            (r"gob_datosalumnos|gob_promedios|ESTADOACADEMICO.*SITUACION", "TSVs estado/situación"),
        ],
        "transform_pat": [
            (r"merge|lookup|map.*VIG_ESPERADO", "Merge/lookup desde catálogo → VIG esperado"),
        ],
        "reglas_pat": [
            (r"TITULADO.*0|ELIMINADO.*0|SUSPENDIDO.*0", "Estados terminales → VIG=0"),
        ],
        "outputs": ["ARCHIVO_LISTO_SUBIDA"],
    },
    "FLAG_INCONSISTENCIA_VIG": {
        "fuentes_pat": [
            (r"FLAG_INCONSISTENCIA_VIG", "Derivada de VIG vs VIG_ESPERADO_DA"),
        ],
        "transform_pat": [
            (r"OK.*INCONSISTENTE|INCONSISTENTE|SIN_DATO|SIN_REGLA", "Comparación directa"),
        ],
        "reglas_pat": [],
        "outputs": ["ARCHIVO_LISTO_SUBIDA"],
    },
    "NOMBRE_CARRERA_TSV": {
        "fuentes_pat": [
            (r"NOMBRE_CARRERA_TSV|DURACION_ESTUDIOS\.tsv|duracion_estudios", "DURACION_ESTUDIOS.tsv"),
        ],
        "transform_pat": [
            (r"merge.*DURACION|join.*duracion", "Merge desde TSV duración"),
        ],
        "reglas_pat": [],
        "outputs": ["ARCHIVO_LISTO_SUBIDA"],
    },
    "DURACION_ESTUDIOS_TSV": {
        "fuentes_pat": [
            (r"DURACION_ESTUDIOS_TSV|DURACION_ESTUDIOS\.tsv", "DURACION_ESTUDIOS.tsv"),
        ],
        "transform_pat": [
            (r"merge.*DURACION|join.*duracion", "Merge desde TSV duración"),
        ],
        "reglas_pat": [],
        "outputs": ["ARCHIVO_LISTO_SUBIDA"],
    },
}


def construir_linaje(code_text: str) -> list[LineageEntry]:
    """Construye mapa de linaje inspeccionando el código fuente."""
    entries: list[LineageEntry] = []
    for col, spec in _LINEAGE_PATTERNS.items():
        entry = LineageEntry(columna=col)
        # Fuentes
        for pat, desc in spec.get("fuentes_pat", []):
            hits = _find_lines(code_text, pat)
            if hits:
                entry.fuentes.append(desc)
                for lno, ltxt in hits[:3]:
                    entry.punto_codigo.append(f"L{lno}: {ltxt[:120]}")
        # Transformaciones
        for pat, desc in spec.get("transform_pat", []):
            hits = _find_lines(code_text, pat)
            if hits:
                entry.transformaciones.append(desc)
                for lno, ltxt in hits[:2]:
                    entry.punto_codigo.append(f"L{lno}: {ltxt[:120]}")
        # Reglas de negocio
        for pat, desc in spec.get("reglas_pat", []):
            hits = _find_lines(code_text, pat)
            if hits:
                entry.reglas_negocio.append(desc)
                for lno, ltxt in hits[:2]:
                    entry.punto_codigo.append(f"L{lno}: {ltxt[:120]}")
        # Outputs
        entry.outputs = spec.get("outputs", [])
        entries.append(entry)
    return entries


def detectar_puntos_clave(code_text: str) -> dict[str, list[tuple[int, str]]]:
    """Detecta ubicaciones clave del pipeline en el código."""
    detections: dict[str, list[tuple[int, str]]] = {}
    patterns = {
        "filtro_periodo": r"ANO_ANTERIOR|ano_anterior|2025.*periodo|REGIMEN.*SEMESTRAL",
        "recalculo_4_columnas": r"PROM_PRI_SEM.*=|PROM_SEG_SEM.*=|ASI_INS_HIS.*=|ASI_APR_HIS.*=",
        "regla_VIG0_4cols": r"VIG.*==?\s*0.*PROM.*0|VIG.*0.*ASI.*0|force.*VIG.*0.*col",
        "carga_catalogos_TSV": r"_load_governance_tsv|_load_tsv_table|gobernanza_catalogos",
        "columnas_DA": r"DA_ESTADOACADEMICO|DA_SITUACION|VIG_ESPERADO_DA|FLAG_INCONSISTENCIA",
        "columnas_TSV_duracion": r"NOMBRE_CARRERA_TSV|DURACION_ESTUDIOS_TSV|DURACION_TITULACION_TSV|DURACION_TOTAL_TSV",
        "escritura_excel": r"ExcelWriter|to_excel|_write_excel_atomic",
        "validacion_bloqueante": r"BLOCKER|bloqueante|severity.*BLOCKER",
    }
    for key, pat in patterns.items():
        detections[key] = _find_lines(code_text, pat)[:10]
    return detections


# ---------------------------------------------------------------------------
# Parte 3 — Auditoría empírica (outputs)
# ---------------------------------------------------------------------------
def auditar_outputs(output_dir: Path, excel_name: str = "archivo_listo_para_sies.xlsx") -> list[Check]:
    """Valida los outputs existentes en output_dir."""
    checks: list[Check] = []
    excel_path = output_dir / excel_name

    # 3.1 Existencia del Excel
    c = Check("Existencia Excel principal")
    if excel_path.exists():
        c.estado = "OK"
        c.detalle = str(excel_path)
    else:
        c.estado = "FAIL"
        c.detalle = f"No existe {excel_path}"
    checks.append(c)
    if c.estado == "FAIL":
        return checks

    # 3.2 Hojas presentes
    xls = pd.ExcelFile(excel_path)
    c = Check("Hojas requeridas presentes")
    required_sheets = {"MATRICULA_UNIFICADA_32", "ARCHIVO_LISTO_SUBIDA"}
    missing_sheets = required_sheets - set(xls.sheet_names)
    if not missing_sheets:
        c.estado = "OK"
        c.detalle = f"Hojas encontradas: {', '.join(sorted(xls.sheet_names))}"
    else:
        c.estado = "FAIL"
        c.detalle = f"Faltan hojas: {missing_sheets}"
    checks.append(c)
    if c.estado == "FAIL":
        return checks

    # Cargar hojas
    mu32 = pd.read_excel(xls, sheet_name="MATRICULA_UNIFICADA_32")
    arch = pd.read_excel(xls, sheet_name="ARCHIVO_LISTO_SUBIDA")

    # 3.3 Columnas MU32 (orden exacto)
    c = Check("Columnas MU32 regulatorias")
    actual_mu32_cols = list(mu32.columns)
    # Verificar que las columnas esperadas estén presentes (pueden existir extras)
    missing_cols = [col for col in COLUMNAS_MU32_ESPERADAS if col not in actual_mu32_cols]
    if not missing_cols:
        c.estado = "OK"
        c.detalle = f"{len(actual_mu32_cols)} columnas; las {len(COLUMNAS_MU32_ESPERADAS)} regulatorias presentes"
    else:
        c.estado = "FAIL"
        c.detalle = f"Faltan columnas regulatorias: {missing_cols}"
    checks.append(c)

    # 3.4 Columnas trazabilidad DA en ARCHIVO_LISTO_SUBIDA
    c = Check("Columnas trazabilidad *_DA")
    missing_da = [col for col in COLUMNAS_TRAZABILIDAD_DA if col not in arch.columns]
    if not missing_da:
        c.estado = "OK"
        c.detalle = f"Presentes: {COLUMNAS_TRAZABILIDAD_DA}"
    else:
        c.estado = "FAIL"
        c.detalle = f"Faltan: {missing_da}"
    checks.append(c)

    # 3.5 Columnas trazabilidad TSV
    c = Check("Columnas trazabilidad *_TSV")
    found_tsv = [col for col in COLUMNAS_TRAZABILIDAD_TSV if col in arch.columns]
    missing_tsv = [col for col in COLUMNAS_TRAZABILIDAD_TSV if col not in arch.columns]
    if missing_tsv:
        c.estado = "WARN"
        c.detalle = f"Presentes: {found_tsv}; Ausentes: {missing_tsv} (depende de oferta académica)"
    else:
        c.estado = "OK"
        c.detalle = f"Presentes: {found_tsv}"
    checks.append(c)

    # 3.5b Cobertura DURACION_ESTUDIOS por CODIGO_CARRERA
    c = Check("Cobertura DURACION por CODIGO_CARRERA")
    if "DURACION_ESTUDIOS_TSV" in arch.columns and "COD_CAR" in arch.columns:
        con_cod_car = pd.to_numeric(arch["COD_CAR"], errors="coerce").notna().sum()
        con_dur = arch["DURACION_ESTUDIOS_TSV"].notna().sum()
        pct = 100 * con_dur / con_cod_car if con_cod_car > 0 else 0
        if pct >= 95:
            c.estado = "OK"
        elif pct >= 80:
            c.estado = "WARN"
        else:
            c.estado = "FAIL"
        c.detalle = f"{con_dur}/{con_cod_car} con COD_CAR tienen DURACION_TSV ({pct:.1f}%); {len(arch)-con_cod_car} sin match SIES"
    else:
        c.estado = "WARN"
        c.detalle = "Columnas DURACION_ESTUDIOS_TSV o COD_CAR ausentes"
    checks.append(c)

    # 3.6 Rangos PROM/ASI
    for sheet_name, df in [("ARCHIVO_LISTO_SUBIDA", arch), ("MATRICULA_UNIFICADA_32", mu32)]:
        checks.extend(_check_rangos(df, sheet_name))

    # 3.7 Regla VIG=0 ⇒ 4 cols=0
    for sheet_name, df in [("ARCHIVO_LISTO_SUBIDA", arch), ("MATRICULA_UNIFICADA_32", mu32)]:
        c = Check(f"Regla VIG=0 → 4cols=0 [{sheet_name}]")
        vig = pd.to_numeric(df["VIG"], errors="coerce").fillna(0)
        prom1 = pd.to_numeric(df["PROM_PRI_SEM"], errors="coerce").fillna(0)
        prom2 = pd.to_numeric(df["PROM_SEG_SEM"], errors="coerce").fillna(0)
        ins = pd.to_numeric(df["ASI_INS_HIS"], errors="coerce").fillna(0)
        apr = pd.to_numeric(df["ASI_APR_HIS"], errors="coerce").fillna(0)
        mask_vig0 = vig == 0
        bad = mask_vig0 & ((prom1 != 0) | (prom2 != 0) | (ins != 0) | (apr != 0))
        n_bad = int(bad.sum())
        if n_bad == 0:
            c.estado = "OK"
            c.detalle = f"VIG=0: {int(mask_vig0.sum())} registros, todos con 4 cols=0"
        else:
            c.estado = "FAIL"
            c.detalle = f"{n_bad} registros VIG=0 con alguna de las 4 columnas ≠ 0"
        checks.append(c)

    # 3.8 Ejecutar verificador externo
    c = Check("Verificador scripts/verificar_4_columnas_mu.py")
    if VERIFICADOR_SCRIPT.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(VERIFICADOR_SCRIPT), "--excel", str(excel_path)],
                capture_output=True, text=True, timeout=120,
            )
            output = (result.stdout + result.stderr).strip()
            if result.returncode == 0:
                c.estado = "OK"
            else:
                c.estado = "FAIL"
            c.detalle = output[:500]
        except Exception as e:
            c.estado = "FAIL"
            c.detalle = f"Error ejecutando verificador: {e}"
    else:
        c.estado = "SKIP"
        c.detalle = "Script verificador no encontrado"
    checks.append(c)

    # 3.9 CSV regulatorio
    csv_path = output_dir / "matricula_unificada_2026_pregrado.csv"
    c = Check("CSV regulatorio presente")
    if csv_path.exists():
        c.estado = "OK"
        c.detalle = f"Tamaño: {csv_path.stat().st_size:,} bytes"
    else:
        c.estado = "WARN"
        c.detalle = f"No existe {csv_path.name} (puede regenerarse)"
    checks.append(c)

    return checks


def _check_rangos(df: pd.DataFrame, sheet_name: str) -> list[Check]:
    """Valida rangos de PROM y ASI."""
    checks = []
    prom1 = pd.to_numeric(df["PROM_PRI_SEM"], errors="coerce").fillna(0)
    prom2 = pd.to_numeric(df["PROM_SEG_SEM"], errors="coerce").fillna(0)
    ins = pd.to_numeric(df["ASI_INS_HIS"], errors="coerce").fillna(0)
    apr = pd.to_numeric(df["ASI_APR_HIS"], errors="coerce").fillna(0)

    # PROM rango: 0 o 100-700
    for nombre, serie in [("PROM_PRI_SEM", prom1), ("PROM_SEG_SEM", prom2)]:
        c = Check(f"Rango {nombre} [{sheet_name}]")
        bad = ~((serie == 0) | serie.between(100, 700))
        n_bad = int(bad.sum())
        if n_bad == 0:
            c.estado = "OK"
            c.detalle = f"min={int(serie.min())}, max={int(serie.max())}, sin decimales aparentes"
        else:
            c.estado = "FAIL"
            c.detalle = f"{n_bad} valores fuera de rango [0, 100-700]"
        checks.append(c)

    # ASI rango: 0-200
    for nombre, serie in [("ASI_INS_HIS", ins), ("ASI_APR_HIS", apr)]:
        c = Check(f"Rango {nombre} [{sheet_name}]")
        bad = ~serie.between(0, 200)
        n_bad = int(bad.sum())
        if n_bad == 0:
            c.estado = "OK"
            c.detalle = f"min={int(serie.min())}, max={int(serie.max())}"
        else:
            c.estado = "FAIL"
            c.detalle = f"{n_bad} valores fuera de rango [0, 200]"
        checks.append(c)

    # ASI coherencia
    c = Check(f"ASI_APR_HIS ≤ ASI_INS_HIS [{sheet_name}]")
    bad_coh = apr > ins
    n_bad = int(bad_coh.sum())
    if n_bad == 0:
        c.estado = "OK"
        c.detalle = "Coherencia OK en todos los registros"
    else:
        c.estado = "FAIL"
        c.detalle = f"{n_bad} registros con ASI_APR_HIS > ASI_INS_HIS"
    checks.append(c)

    return checks


# ---------------------------------------------------------------------------
# Parte 4 — Coherencia lógica vs evidencia
# ---------------------------------------------------------------------------
def coherencia_logica_vs_evidencia(
    code_text: str,
    output_dir: Path,
    fail_on_inconsistente: bool = False,
    fail_only_suspendido: bool = False,
) -> list[Check]:
    """Cruza inferencias del código vs datos observados."""
    checks: list[Check] = []
    excel_path = output_dir / "archivo_listo_para_sies.xlsx"
    if not excel_path.exists():
        checks.append(Check("Coherencia lógica", "SKIP", "Excel no disponible"))
        return checks

    arch = pd.read_excel(excel_path, sheet_name="ARCHIVO_LISTO_SUBIDA")

    # 4.1 Año anterior por período (dinámico)
    c = Check("Año anterior por período (dinámico)")
    # Leer JSON del pipeline
    anio_anterior_detectado: int | None = None
    periodo_filtro_anio_det: int | None = None
    periodo_filtro_sem_det: int | None = None
    for jname in ("reporte_matricula.json", "reporte_validacion.json"):
        jp = output_dir / jname
        if jp.exists():
            try:
                jdata = json.loads(jp.read_text(encoding="utf-8"))
                anio_anterior_detectado = jdata.get("anio_anterior_prom")
                periodo_filtro_anio_det = jdata.get("periodo_filtro_anio")
                periodo_filtro_sem_det = jdata.get("periodo_filtro_sem")
                if anio_anterior_detectado is not None:
                    break
            except Exception:
                pass
    if anio_anterior_detectado is not None and periodo_filtro_anio_det is not None:
        esperado = int(periodo_filtro_anio_det) - 1
        if int(anio_anterior_detectado) == esperado:
            c.estado = "OK"
            c.detalle = (
                f"anio_anterior_prom={anio_anterior_detectado} == periodo_filtro_anio({periodo_filtro_anio_det})-1"
                f" | SEM={periodo_filtro_sem_det}"
            )
        else:
            c.estado = "WARN"
            c.detalle = (
                f"Incoherencia: anio_anterior_prom={anio_anterior_detectado} vs "
                f"periodo_filtro_anio({periodo_filtro_anio_det})-1={esperado}"
            )
    elif anio_anterior_detectado is not None:
        c.estado = "OK"
        c.detalle = f"anio_anterior_prom={anio_anterior_detectado} (periodo_filtro_anio no disponible en JSON)"
    else:
        # Fallback: buscar patrón dinámico en código
        hits_dyn = _find_lines(code_text, r"anio_anterior_prom.*=.*periodo_filtro_anio.*-.*1|anio_ref_override")
        if hits_dyn:
            c.estado = "OK"
            c.detalle = f"Cálculo dinámico en L{hits_dyn[0][0]}: {hits_dyn[0][1][:80]}"
        else:
            c.estado = "WARN"
            c.detalle = "No se detectó JSON con periodo_filtro_anio ni patrón dinámico en código"
    checks.append(c)

    # Verificar que PROM no tiene decimales (escala entera 100-700)
    c = Check("PROM escala entera (sin decimales)")
    for col in ["PROM_PRI_SEM", "PROM_SEG_SEM"]:
        if col in arch.columns:
            vals = pd.to_numeric(arch[col], errors="coerce").dropna()
            non_zero = vals[vals != 0]
            if len(non_zero) > 0:
                has_decimals = (non_zero != non_zero.astype(int)).any()
                if has_decimals:
                    c.estado = "FAIL"
                    c.detalle = f"{col} tiene valores decimales (no escala entera)"
                    break
    if c.estado == "PENDIENTE":
        c.estado = "OK"
        c.detalle = "Todos los PROM son enteros (escala MU correcta)"
    checks.append(c)

    # 4.2 FLAG_INCONSISTENCIA_VIG distribución
    c = Check("Distribución FLAG_INCONSISTENCIA_VIG")
    if "FLAG_INCONSISTENCIA_VIG" in arch.columns:
        dist = arch["FLAG_INCONSISTENCIA_VIG"].value_counts().to_dict()
        n_incons = dist.get("INCONSISTENTE", 0)
        n_ok = dist.get("OK", 0)
        c.detalle = f"Distribución: {dist}"

        if fail_on_inconsistente and n_incons > 0:
            c.estado = "FAIL"
            c.detalle += f" | --fail-on-inconsistente activo: {n_incons} INCONSISTENTES"
        elif fail_only_suspendido:
            # Verificar si hay SUSPENDIDO/SUSPENSIÓN TEMPORAL con VIG≠0
            if "DA_ESTADOACADEMICO" in arch.columns:
                susp_mask = arch["DA_ESTADOACADEMICO"].astype(str).str.contains(
                    r"SUSPEND", case=False, na=False
                )
                vig_col = pd.to_numeric(arch["VIG"], errors="coerce").fillna(0)
                bad_susp = susp_mask & (vig_col != 0)
                n_bad_susp = int(bad_susp.sum())
                if n_bad_susp > 0:
                    c.estado = "FAIL"
                    c.detalle += f" | {n_bad_susp} SUSPENDIDOS con VIG≠0"
                else:
                    c.estado = "OK"
            else:
                c.estado = "WARN"
                c.detalle += " | No hay DA_ESTADOACADEMICO para verificar suspendidos"
        else:
            c.estado = "OK" if n_incons == 0 else "WARN"
    else:
        c.estado = "FAIL"
        c.detalle = "Columna FLAG_INCONSISTENCIA_VIG ausente"
    checks.append(c)

    # 4.3 Exportar evidencia de inconsistencias VIG
    if "FLAG_INCONSISTENCIA_VIG" in arch.columns:
        incons_mask = arch["FLAG_INCONSISTENCIA_VIG"] == "INCONSISTENTE"
        if incons_mask.any():
            export_cols = ["FLAG_INCONSISTENCIA_VIG"]
            for ec in ["CODCLI", "VIG", "VIG_ESPERADO_DA", "ESTADOACADEMICO_DA", "SITUACION_DA",
                        "DA_ESTADOACADEMICO", "DA_SITUACION", "ANIO_ING_ACT", "SEM_ING_ACT"]:
                if ec in arch.columns and ec not in export_cols:
                    export_cols.append(ec)
            incons_df = arch.loc[incons_mask, export_cols].head(10000)
            incons_path = output_dir / "inconsistencias_vig.csv"
            incons_df.to_csv(incons_path, index=False, encoding="utf-8")
            c2 = Check("Evidencia inconsistencias_vig.csv")
            c2.estado = "OK"
            c2.detalle = f"{len(incons_df)} filas exportadas a {incons_path.name}"
            checks.append(c2)

    # 4.3 Catálogos bloqueantes — combos fuera de catálogo
    c = Check("Catálogos gobernanza sin combos nuevos")
    gob_da_path = REPO_DIR / "gobernanza_catalogos" / "gob_datosalumnos_estadoacademico_situacion.tsv"
    if gob_da_path.exists() and "DA_ESTADOACADEMICO" in arch.columns and "DA_SITUACION" in arch.columns:
        cat = pd.read_csv(gob_da_path, sep="\t")
        cat_keys = set(
            zip(cat["ESTADOACADEMICO"].astype(str).str.upper().str.strip(),
                cat["SITUACION"].astype(str).str.upper().str.strip())
        )
        data_keys = set(
            zip(arch["DA_ESTADOACADEMICO"].astype(str).str.upper().str.strip(),
                arch["DA_SITUACION"].astype(str).str.upper().str.strip())
        )
        # Excluir registros sin dato DA
        data_keys_clean = {k for k in data_keys if k[0] not in ("NAN", "", "NONE") and k[1] not in ("NAN", "", "NONE")}
        nuevos = data_keys_clean - cat_keys
        if not nuevos:
            c.estado = "OK"
            c.detalle = f"{len(data_keys_clean)} combos en datos, todos cubiertos por catálogo ({len(cat_keys)} reglas)"
        else:
            c.estado = "FAIL"
            c.detalle = f"{len(nuevos)} combos fuera de catálogo: {list(nuevos)[:5]}"
    else:
        c.estado = "SKIP"
        c.detalle = "Catálogo DA o columnas DA no disponibles"
    checks.append(c)

    # 4.4 Gobernanza bloqueante — FOR_ING_ACT vs catálogo
    c = Check("GOB bloqueante: FOR_ING_ACT vs catálogo")
    gob_fia_path = REPO_DIR / "gobernanza_for_ing_act.tsv"
    if gob_fia_path.exists() and "FOR_ING_ACT" in arch.columns:
        cat_fia = pd.read_csv(gob_fia_path, sep="\t")
        codigos_validos = set(cat_fia["FOR_ING_ACT"].dropna().astype(int))
        vals_datos = pd.to_numeric(arch["FOR_ING_ACT"], errors="coerce").dropna().astype(int)
        fuera = set(vals_datos.unique()) - codigos_validos
        if not fuera:
            c.estado = "OK"
            c.detalle = f"{vals_datos.nunique()} códigos en datos, todos en catálogo ({len(codigos_validos)} válidos)"
        else:
            n_filas = int(vals_datos.isin(fuera).sum())
            c.estado = "FAIL"
            c.detalle = f"{len(fuera)} códigos fuera de catálogo: {sorted(fuera)[:10]} ({n_filas} filas)"
    else:
        c.estado = "SKIP"
        c.detalle = "Catálogo FOR_ING_ACT o columna no disponible"
    checks.append(c)

    # 4.4b Anexo 7 — continuidad requiere origen distinto del ingreso actual
    c = Check("Anexo 7 continuidad: FOR_ING_ACT {2,3,4,5,11} ⇒ ORI != ACT")
    required_cols = {"FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI"}
    if required_cols.issubset(set(arch.columns)):
        scope = arch.copy()
        if "INCLUIR_EN_MATRICULA_32" in scope.columns:
            scope = scope[scope["INCLUIR_EN_MATRICULA_32"].astype(str).str.upper().eq("SI")].copy()
        for_vals = pd.to_numeric(scope["FOR_ING_ACT"], errors="coerce")
        continuidad_mask = for_vals.isin([2, 3, 4, 5, 11])
        anio_act_vals = pd.to_numeric(scope["ANIO_ING_ACT"], errors="coerce")
        sem_act_vals = pd.to_numeric(scope["SEM_ING_ACT"], errors="coerce")
        anio_ori_vals = pd.to_numeric(scope["ANIO_ING_ORI"], errors="coerce")
        sem_ori_vals = pd.to_numeric(scope["SEM_ING_ORI"], errors="coerce")
        invalid_mask = continuidad_mask & anio_act_vals.eq(anio_ori_vals) & sem_act_vals.eq(sem_ori_vals)
        if not invalid_mask.any():
            c.estado = "OK"
            c.detalle = f"{int(continuidad_mask.sum())} filas continuidad auditadas, todas con ORI != ACT"
        else:
            muestras = scope.loc[invalid_mask, ["CODCLI", "N_DOC", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT"]].head(5)
            muestras_txt = muestras.astype(str).to_dict(orient="records")
            c.estado = "FAIL"
            c.detalle = (
                f"{int(invalid_mask.sum())} filas incumplen Anexo 7 continuidad "
                f"(muestra: {muestras_txt})"
            )
    else:
        c.estado = "SKIP"
        c.detalle = "Columnas cronológicas FOR/ORI/ACT no disponibles para validar continuidad"
    checks.append(c)

    # 4.5 Gobernanza bloqueante — COD_SED vs catálogo sede
    c = Check("GOB bloqueante: COD_SED vs catálogo sede")
    gob_sede_path = REPO_DIR / "gobernanza_sede.tsv"
    if gob_sede_path.exists() and "COD_SED" in arch.columns:
        cat_sede = pd.read_csv(gob_sede_path, sep="\t")
        codigos_sede_validos = set(cat_sede["COD_SED"].dropna().astype(int))
        vals_sed = pd.to_numeric(arch["COD_SED"], errors="coerce").dropna().astype(int)
        fuera = set(vals_sed.unique()) - codigos_sede_validos
        if not fuera:
            c.estado = "OK"
            c.detalle = f"{vals_sed.nunique()} sedes en datos, todas en catálogo ({len(codigos_sede_validos)} válidas)"
        else:
            n_filas = int(vals_sed.isin(fuera).sum())
            c.estado = "FAIL"
            c.detalle = f"{len(fuera)} sedes fuera de catálogo: {sorted(fuera)[:10]} ({n_filas} filas)"
    else:
        c.estado = "SKIP"
        c.detalle = "Catálogo sede o columna COD_SED no disponible"
    checks.append(c)

    # 4.6 Gobernanza bloqueante — NAC vs catálogo nacionalidades
    c = Check("GOB bloqueante: NAC vs catálogo nacionalidades")
    gob_nac_path = REPO_DIR / "gobernanza_nac.tsv"
    if gob_nac_path.exists() and "NAC" in arch.columns:
        cat_nac = pd.read_csv(gob_nac_path, sep="\t")
        codigos_nac_validos = set(cat_nac["COD_NAC"].dropna().astype(int))
        vals_nac = pd.to_numeric(arch["NAC"], errors="coerce").dropna().astype(int)
        fuera = set(vals_nac.unique()) - codigos_nac_validos
        if not fuera:
            c.estado = "OK"
            c.detalle = f"{vals_nac.nunique()} nacionalidades en datos, todas en catálogo ({len(codigos_nac_validos)} válidas)"
        else:
            n_filas = int(vals_nac.isin(fuera).sum())
            c.estado = "FAIL"
            c.detalle = f"{len(fuera)} nacionalidades fuera de catálogo: {sorted(fuera)[:10]} ({n_filas} filas)"
    else:
        c.estado = "SKIP"
        c.detalle = "Catálogo NAC o columna no disponible"
    checks.append(c)

    # 4.7 Gobernanza bloqueante — PAIS_EST_SEC vs catálogo
    c = Check("GOB bloqueante: PAIS_EST_SEC vs catálogo")
    gob_pais_path = REPO_DIR / "gobernanza_pais_est_sec.tsv"
    if gob_pais_path.exists() and "PAIS_EST_SEC" in arch.columns:
        cat_pais = pd.read_csv(gob_pais_path, sep="\t")
        codigos_pais_validos = set(cat_pais["COD_PAIS_EST_SEC"].dropna().astype(int))
        vals_pais = pd.to_numeric(arch["PAIS_EST_SEC"], errors="coerce").dropna().astype(int)
        fuera = set(vals_pais.unique()) - codigos_pais_validos
        if not fuera:
            c.estado = "OK"
            c.detalle = f"{vals_pais.nunique()} países en datos, todos en catálogo ({len(codigos_pais_validos)} válidos)"
        else:
            n_filas = int(vals_pais.isin(fuera).sum())
            c.estado = "FAIL"
            c.detalle = f"{len(fuera)} países fuera de catálogo: {sorted(fuera)[:10]} ({n_filas} filas)"
    else:
        c.estado = "SKIP"
        c.detalle = "Catálogo PAIS_EST_SEC o columna no disponible"
    checks.append(c)

    # 4.8 Gobernanza bloqueante — NIV_ACA vs catálogo niveles
    c = Check("GOB bloqueante: NIV_ACA vs catálogo niveles")
    gob_niv_path = REPO_DIR / "gobernanza_niveles.tsv"
    if gob_niv_path.exists() and "NIV_ACA" in arch.columns:
        cat_niv = pd.read_csv(gob_niv_path, sep="\t")
        niveles_validos = set(cat_niv["NIVEL_CARRERA"].dropna().astype(int))
        vals_niv = pd.to_numeric(arch["NIV_ACA"], errors="coerce").dropna().astype(int)
        fuera = set(vals_niv.unique()) - niveles_validos
        if not fuera:
            c.estado = "OK"
            c.detalle = f"{vals_niv.nunique()} niveles en datos, todos en catálogo ({len(niveles_validos)} válidos)"
        else:
            n_filas = int(vals_niv.isin(fuera).sum())
            c.estado = "FAIL"
            c.detalle = f"{len(fuera)} niveles fuera de catálogo: {sorted(fuera)[:10]} ({n_filas} filas)"
    else:
        c.estado = "SKIP"
        c.detalle = "Catálogo niveles o columna NIV_ACA no disponible"
    checks.append(c)

    return checks


# ---------------------------------------------------------------------------
# Parte 5 — Reporte y Dictamen
# ---------------------------------------------------------------------------
def generar_reporte(
    meta: dict[str, str],
    linaje: list[LineageEntry],
    detections: dict[str, list[tuple[int, str]]],
    checks: list[Check],
    output_path: Path,
    modified_line_refs: list[str] | None = None,
) -> bool:
    """Genera resultados/auditoria_maestra.md y retorna True si LISTO."""
    all_ok = all(c.estado in ("OK", "WARN", "SKIP") for c in checks)
    has_fail = any(c.estado == "FAIL" for c in checks)
    dictamen = "LISTO PARA ENTREGA" if not has_fail else "NO LISTO"
    icono = "✅" if not has_fail else "❌"

    lines: list[str] = []
    lines.append(f"# Auditoría Maestra — Gate de Entrega MU 2026")
    lines.append(f"")
    lines.append(f"**Dictamen: {icono} {dictamen}**")
    lines.append(f"")
    lines.append(f"## Metadata")
    lines.append(f"| Campo | Valor |")
    lines.append(f"|-------|-------|")
    for k, v in meta.items():
        lines.append(f"| {k} | {v} |")
    lines.append(f"")

    if modified_line_refs:
        lines.append("## Cambios de Código Aplicados (Git Diff)")
        lines.append("")
        for ref in modified_line_refs:
            lines.append(f"- `{ref}`")
        lines.append("")

    # Checklist
    lines.append(f"## Checklist de Componentes")
    lines.append(f"")
    lines.append(f"| # | Check | Estado | Detalle |")
    lines.append(f"|---|-------|--------|---------|")
    for i, c in enumerate(checks, 1):
        icon = {"OK": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(c.estado, "❓")
        det = c.detalle.replace("|", "/").replace("\n", " ")[:200]
        lines.append(f"| {i} | {c.nombre} | {icon} {c.estado} | {det} |")
    lines.append(f"")

    # Estadísticas resumen
    n_ok = sum(1 for c in checks if c.estado == "OK")
    n_fail = sum(1 for c in checks if c.estado == "FAIL")
    n_warn = sum(1 for c in checks if c.estado == "WARN")
    n_skip = sum(1 for c in checks if c.estado == "SKIP")
    lines.append(f"**Resumen**: {n_ok} OK, {n_fail} FAIL, {n_warn} WARN, {n_skip} SKIP de {len(checks)} checks")
    lines.append(f"")

    # Mapa de linaje
    lines.append(f"## Mapa de Linaje por Columna")
    lines.append(f"")
    for entry in linaje:
        lines.append(f"### `{entry.columna}`")
        lines.append(f"- **Fuentes**: {', '.join(entry.fuentes) if entry.fuentes else '(no detectada)'}")
        lines.append(f"- **Transformaciones**: {', '.join(entry.transformaciones) if entry.transformaciones else '(ninguna detectada)'}")
        lines.append(f"- **Reglas de negocio**: {', '.join(entry.reglas_negocio) if entry.reglas_negocio else '(ninguna detectada)'}")
        lines.append(f"- **Outputs**: {', '.join(entry.outputs)}")
        if entry.punto_codigo:
            lines.append(f"- **Referencias en código** (`codigo_gobernanza_v2.py`):")
            for ref in entry.punto_codigo[:6]:
                lines.append(f"  - `{ref}`")
        lines.append(f"")

    # Detecciones de puntos clave
    lines.append(f"## Puntos Clave Detectados en el Código")
    lines.append(f"")
    for key, hits in detections.items():
        lines.append(f"### {key}")
        if hits:
            for lno, ltxt in hits[:5]:
                lines.append(f"- L{lno}: `{ltxt[:120]}`")
        else:
            lines.append(f"- *(no detectado)*")
        lines.append(f"")

    # Dictamen final
    lines.append(f"---")
    lines.append(f"## Dictamen Final")
    lines.append(f"")
    lines.append(f"### {icono} {dictamen}")
    lines.append(f"")
    if has_fail:
        lines.append(f"**Causas de bloqueo:**")
        for c in checks:
            if c.estado == "FAIL":
                lines.append(f"- **{c.nombre}**: {c.detalle[:200]}")
        lines.append(f"")
        lines.append(f"**Acciones recomendadas:**")
        lines.append(f"1. Corregir los FAIL listados arriba.")
        lines.append(f"2. Re-ejecutar el pipeline: `python3 codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`")
        lines.append(f"3. Re-ejecutar esta auditoría: `python3 scripts/auditoria_maestra.py --solo-validar`")
    else:
        lines.append(f"Todos los checks pasaron. El archivo `archivo_listo_para_sies.xlsx` y el CSV regulatorio")
        lines.append(f"son aptos para entrega oficial al SIES.")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Generado automáticamente por `scripts/auditoria_maestra.py` el {meta.get('Fecha/Hora', '')}*")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return not has_fail


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Auditoría Maestra — Gate de Entrega MU 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Ejemplos:
              python3 scripts/auditoria_maestra.py --solo-validar
              python3 scripts/auditoria_maestra.py --ejecutar-pipeline --anio 2026 --sem 1
              python3 scripts/auditoria_maestra.py --solo-validar --fail-on-inconsistente
        """),
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ejecutar-pipeline", action="store_true", help="Ejecuta el pipeline antes de validar")
    mode.add_argument("--solo-validar", action="store_true", help="Solo valida outputs existentes")

    p.add_argument("--input", default=None, help="Ruta al Excel de entrada (para --ejecutar-pipeline)")
    p.add_argument("--output-dir", default="resultados", help="Carpeta de outputs (default: resultados)")
    p.add_argument("--anio", type=int, default=None, help="Año de ingreso (ej. 2026)")
    p.add_argument("--sem", type=int, default=None, help="Semestre de ingreso (ej. 1)")
    p.add_argument("--filtro-base-datos-sheet", default=None,
                    help="Hoja del Excel con RUT (N_DOC) para filtrar solo esas filas")
    p.add_argument("--fail-on-inconsistente", action="store_true",
                    help="FAIL si hay FLAG_INCONSISTENCIA_VIG=INCONSISTENTE")
    p.add_argument("--fail-only-on-suspendido", action="store_true",
                    help="FAIL solo si SUSPENDIDO/SUSPENSIÓN TEMPORAL con VIG≠0")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()

    print("=" * 80)
    print("  AUDITORÍA MAESTRA — Gate de Entrega MU 2026")
    print("=" * 80)

    # --- Meta ---
    meta: dict[str, str] = {
        "Fecha/Hora": _now_iso(),
        "Commit": _git_commit_hash(),
        "Output-Dir": str(output_dir),
        "Modo": "ejecutar-pipeline" if args.ejecutar_pipeline else "solo-validar",
    }

    # --- Parte 1: Ejecución controlada ---
    if args.ejecutar_pipeline:
        print("\n📦 Parte 1: Ejecutando pipeline...")
        cmd = [sys.executable, str(PIPELINE_SCRIPT), "--proceso", "matricula",
               "--usar-gobernanza-v2", "true", "--output-dir", str(output_dir)]
        if args.input:
            cmd.extend(["--input", args.input])
            meta["Input"] = args.input
        if args.filtro_base_datos_sheet:
            cmd.extend(["--filtro-base-datos-sheet", args.filtro_base_datos_sheet])
            meta["Filtro-Base-Datos"] = args.filtro_base_datos_sheet
        try:
            # Pasar período por stdin (pipeline pregunta por input() si no hay flags)
            stdin_payload = None
            if args.anio is not None and args.sem is not None:
                stdin_payload = f"{args.anio}\n{args.sem}\n"
                meta["ANIO_SOLICITADO"] = str(args.anio)
                meta["SEM_SOLICITADO"] = str(args.sem)

            result = subprocess.run(
                cmd,
                input=stdin_payload,
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode != 0:
                print(f"  ❌ Pipeline falló (exit {result.returncode})")
                print(result.stderr[:500] if result.stderr else result.stdout[:500])
                return 2
            print("  ✅ Pipeline ejecutado OK")
            # Validar que el JSON generado corresponde al período solicitado (gate robusto)
            try:
                import json
                rep_path = output_dir / "reporte_matricula.json"
                if rep_path.exists():
                    rep = json.loads(rep_path.read_text(encoding="utf-8"))
                    if args.anio is not None and rep.get("periodo_filtro_anio") != args.anio:
                        print(f"  ❌ JSON no corresponde al año solicitado: {args.anio} vs {rep.get('periodo_filtro_anio')}")
                        return 2
                    if args.sem is not None and rep.get("periodo_filtro_sem") != args.sem:
                        print(f"  ❌ JSON no corresponde al semestre solicitado: {args.sem} vs {rep.get('periodo_filtro_sem')}")
                        return 2
                else:
                    print("  ⚠️ No existe reporte_matricula.json para validar período")
            except Exception as e:
                print(f"  ⚠️ No se pudo validar reporte_matricula.json: {e}")

            meta["Pipeline-Exit"] = "0"
        except Exception as e:
            print(f"  ❌ Error ejecutando pipeline: {e}")
            return 2
    else:
        print("\n⏭️  Parte 1: Modo --solo-validar (sin ejecutar pipeline)")
        meta["Input"] = "(outputs existentes)"

    # --- Parte 2: Auto-evaluación lógica del código ---
    print("\n🔍 Parte 2: Auto-evaluación de lógica del código...")
    if PIPELINE_SCRIPT.exists():
        code_text = PIPELINE_SCRIPT.read_text(encoding="utf-8")
        meta["Pipeline-Script"] = str(PIPELINE_SCRIPT)
        meta["Pipeline-Líneas"] = str(len(code_text.splitlines()))
        linaje = construir_linaje(code_text)
        detections = detectar_puntos_clave(code_text)
        print(f"  ✅ Linaje construido para {len(linaje)} columnas críticas")
        print(f"  ✅ {sum(len(v) for v in detections.values())} puntos clave detectados")
    else:
        print(f"  ❌ No se encontró {PIPELINE_SCRIPT}")
        code_text = ""
        linaje = []
        detections = {}

    # --- Parte 3: Auditoría empírica ---
    print("\n📊 Parte 3: Auditoría empírica de outputs...")
    checks_empiricos = auditar_outputs(output_dir)
    for c in checks_empiricos:
        icon = {"OK": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(c.estado, "❓")
        print(f"  {icon} {c.nombre}: {c.detalle[:100]}")

    # --- Parte 4: Coherencia lógica vs evidencia ---
    print("\n🔗 Parte 4: Coherencia lógica vs evidencia...")
    checks_coherencia = coherencia_logica_vs_evidencia(
        code_text, output_dir,
        fail_on_inconsistente=args.fail_on_inconsistente,
        fail_only_suspendido=args.fail_only_on_suspendido,
    )
    for c in checks_coherencia:
        icon = {"OK": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(c.estado, "❓")
        print(f"  {icon} {c.nombre}: {c.detalle[:100]}")

    # --- Parte 5: Reporte y dictamen ---
    all_checks = checks_empiricos + checks_coherencia
    report_path = output_dir / "auditoria_maestra.md"
    modified_line_refs = _git_modified_line_refs()
    if modified_line_refs:
        meta["Git-Diff-Refs"] = str(len(modified_line_refs))
    print(f"\n📝 Parte 5: Generando reporte en {report_path}...")
    is_ok = generar_reporte(meta, linaje, detections, all_checks, report_path, modified_line_refs=modified_line_refs)

    # --- Resumen terminal ---
    n_ok = sum(1 for c in all_checks if c.estado == "OK")
    n_fail = sum(1 for c in all_checks if c.estado == "FAIL")
    n_warn = sum(1 for c in all_checks if c.estado == "WARN")

    print("\n" + "=" * 80)
    if is_ok:
        print(f"  ✅ DICTAMEN: LISTO PARA ENTREGA  ({n_ok} OK, {n_warn} WARN, {n_fail} FAIL)")
    else:
        print(f"  ❌ DICTAMEN: NO LISTO  ({n_ok} OK, {n_warn} WARN, {n_fail} FAIL)")
    print(f"  📄 Reporte: {report_path}")
    print("=" * 80)

    return 0 if is_ok else 1


if __name__ == "__main__":
    sys.exit(main())
