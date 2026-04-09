#!/usr/bin/env python3
"""Reconstruye el universo corregido de extranjeros regulares 2025.

No genera CSV final para PES. La salida separa evidencia 2025 real de fuentes
2026 usadas solo como apoyo de identificacion o enriquecimiento.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation


ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT / "estudiantes_extranjeros_2026"
AUD = SUB / "resultados" / "auditorias"
REP = SUB / "resultados" / "reportes"
GEST = SUB / "resultados" / "archivos_gestion"
INTERIM = SUB / "data" / "interim"
BACKUPS = SUB / "backups"
DOCS = SUB / "docs"

RUN_TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

INSTRUCTIVO = DOCS / "Instructivo_Estudiantes_Extranjeros_SIES_2026.txt"
DATOS_XLSX = ROOT / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"
MATRICULA_2025_CONTROL = ROOT / "resultados" / "matricula_avance_curricular_2025_control.csv"
MATRICULA_2025_PES_READY = ROOT / "resultados" / "matricula_avance_curricular_2025_pes_ready.csv"
ARCHIVO_LISTO_2026 = ROOT / "resultados" / "archivo_listo_para_sies.xlsx"
BRIDGE = ROOT / "control" / "catalogos" / "PUENTE_SIES_COMPILADO.tsv"
GOB_NAC = ROOT / "gobernanza_nac.tsv"

OUTPUTS = [
    AUD / "INVENTARIO_FUENTES_OFICIALES_2025.csv",
    REP / "DIAGNOSTICO_PRECARGA_PES.md",
    REP / "IDENTIFICACION_MATRICULA_OFICIAL_2025.md",
    AUD / "JERARQUIA_FUENTES_MATRICULA_2025.csv",
    AUD / "UNIVERSO_RECONSTRUIDO_EXTRANJEROS_2025.csv",
    AUD / "COMPARACION_UNIVERSO_ANTERIOR_VS_CORREGIDO.csv",
    INTERIM / "BASE_MAESTRA_EXTRANJEROS_REGULARES_2025_CORREGIDA.csv",
    AUD / "AUDITORIA_VIGENCIA_2025_CORREGIDA.csv",
    AUD / "AUDITORIA_REUTILIZACION_CAMPOS_CORREGIDA.csv",
    GEST / "PLANILLA_GESTION_DOCENCIA_EXTRANJEROS_2025_CORREGIDA.xlsx",
    REP / "DIAGNOSTICO_ESTUDIANTES_INTERCAMBIO_2025.md",
    AUD / "VALIDACION_UNIVERSO_CORREGIDO.csv",
    REP / "REPORTE_CORRECCION_UNIVERSO.md",
    AUD / "MANIFIESTO_ARCHIVOS_CORRECCION_UNIVERSO.csv",
]

OFFICIAL_FIELDS = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "TIPO_RESIDENCIA_ESTUDIANTE",
    "PAIS_DE_ORIGEN",
    "PAIS_ESTUDIOS_SECUNDARIOS",
    "CODIGO_UNICO",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "NOMBRE_UNIVERSIDAD_ORIGEN",
    "PAIS_UNIVERSIDAD_ORIGEN",
    "VIGENCIA",
]


def ensure_dirs() -> None:
    for path in [AUD, REP, GEST, INTERIM, BACKUPS]:
        path.mkdir(parents=True, exist_ok=True)


def clean(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = re.sub(r"\s+", " ", str(value).strip())
    return "" if text.lower() == "nan" else text


def upper_ascii(value: Any) -> str:
    text = clean(value).upper()
    return text.translate(str.maketrans("ÁÉÍÓÚÜÑ", "AEIOUUN"))


def normalize_doc(value: Any) -> str:
    return re.sub(r"[.\-,\s]", "", clean(value).upper())


def split_run(value: Any) -> tuple[str, str]:
    text = normalize_doc(value)
    if len(text) >= 2 and text[-1] in "0123456789K" and text[:-1].isdigit():
        return text[:-1], text[-1]
    return text, ""


def normalize_date(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=False)
    return parsed.strftime("%d-%m-%Y") if not pd.isna(parsed) else text


def normalize_sex(value: Any) -> str:
    raw = clean(value).upper()
    if raw == "F":
        return "M"
    if raw == "M":
        return "H"
    if raw in {"H", "NB"}:
        return raw
    return ""


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if row.get(k) is None else row.get(k) for k in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def backup_existing(paths: list[Path]) -> Path:
    backup_dir = BACKUPS / f"pre_correccion_universo_{RUN_STAMP}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in paths:
        if not path.exists():
            continue
        target = backup_dir / path.name
        shutil.copy2(path, target)
        rows.append(
            {
                "archivo_original": rel(path),
                "archivo_respaldo": rel(target),
                "sha256_original": sha256(path),
                "tamano_bytes": path.stat().st_size,
                "fecha_respaldo": RUN_TS,
            }
        )
    manifest = backup_dir / "MANIFIESTO_RESPALDO_PRE_CORRECCION_UNIVERSO.csv"
    write_csv(manifest, rows, ["archivo_original", "archivo_respaldo", "sha256_original", "tamano_bytes", "fecha_respaldo"])
    return backup_dir


def row_count_text(path: Path) -> int:
    try:
        with path.open("rb") as f:
            return max(sum(1 for _ in f) - 1, 0)
    except Exception:
        return 0


def inspect_candidate(path: Path) -> dict[str, Any]:
    headers: list[str] = []
    sheets: list[str] = []
    rows = ""
    snippet = ""
    ext = path.suffix.lower()
    try:
        if ext in {".csv", ".tsv"}:
            sep = "\t" if ext == ".tsv" else ","
            df = pd.read_csv(path, sep=sep, dtype=str, nrows=3, encoding_errors="replace")
            headers = [clean(c) for c in df.columns]
            rows = str(row_count_text(path))
            snippet = " ".join(headers[:20])
        elif ext in {".xlsx", ".xls"}:
            wb = load_workbook(path, read_only=True, data_only=True)
            for ws in wb.worksheets:
                sheets.append(ws.title)
                values = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), ())
                headers.extend([clean(v) for v in values if clean(v)][:20])
            rows = " | ".join(f"{ws.title}:{max(ws.max_row - 1, 0)}" for ws in wb.worksheets[:10])
            snippet = " ".join(sheets + headers[:30])
            wb.close()
        elif ext in {".txt", ".md"}:
            snippet = path.read_text(encoding="utf-8", errors="replace")[:4000]
            headers = []
            rows = str(row_count_text(path))
    except Exception as exc:
        snippet = f"ERROR_INSPECCION={type(exc).__name__}: {exc}"
    return {
        "hojas": " | ".join(sheets),
        "encabezados": " | ".join(headers[:80]),
        "filas": rows,
        "snippet": snippet,
    }


def infer_source(path: Path, snippet: str) -> tuple[str, str, str, str]:
    text = upper_ascii(f"{path} {snippet}")
    period = "2025" if "2025" in text else ("2026" if "2026" in text else "NO_DETERMINADO")
    level = "registro_estudiante_programa" if any(k in text for k in ["NUM_DOCUMENTO", "N_DOC", "CODCLI", "CODIGO_UNICO"]) else "documental"
    evidence = "NO"
    utility = "BAJA"
    priority = "99"
    if "REPORTE PRECARGA" in text and "EXTRANJ" in text:
        evidence, utility, priority = "POSIBLE_DESCARGA_PES", "PRECARGA_PES", "1"
    elif path == MATRICULA_2025_CONTROL:
        evidence, utility, priority = "CONTROL_LOCAL_2025_CON_PES_READY_ASOCIADO", "FUENTE_PRINCIPAL_EVIDENCIA_2025", "2"
    elif path == MATRICULA_2025_PES_READY:
        evidence, utility, priority = "CSV_PES_READY_AVANCE_2025_SIN_ENCABEZADO", "RESPALDO_ENTREGA_2025", "2"
    elif path == DATOS_XLSX:
        evidence, utility, priority = "FUENTE_INSTITUCIONAL_DATOSALUMNOS_Y_ACTIVIDAD_2025", "COMPLEMENTO_IDENTIDAD_NACIONALIDAD_Y_EVIDENCIA", "3"
    elif "ARCHIVO_LISTO_PARA_SIES" in text:
        evidence, utility, priority = "RESULTADO_MU2026_NO_PRUEBA_MATRICULA_2025", "SOLO_APOYO_IDENTIFICACION_ENRIQUECIMIENTO", "4"
    elif "MATRICULA_UNIFICADA_2026" in text or "MU2026" in text:
        evidence, utility, priority = "FUENTE_2026", "SOLO_REFERENCIA_2026", "4"
    elif "AVANCE_CURRICULAR_2025" in text or "HOJA1" in text:
        evidence, utility, priority = "EVIDENCIA_ACTIVIDAD_2025", "COMPLEMENTO_EVIDENCIA_2025", "3"
    return period, level, evidence, utility, priority


def discover_sources() -> list[dict[str, Any]]:
    keywords = [
        "precarga",
        "extranj",
        "16765",
        "matricula",
        "matrícula",
        "avance_curricular_2025",
        "unificada_2025",
        "congel",
        "archivo_listo_para_sies",
        "pes_ready",
        "sies_2025",
        "intercambio",
        "movilidad",
        "study",
    ]
    explicit = {DATOS_XLSX, MATRICULA_2025_CONTROL, MATRICULA_2025_PES_READY, ARCHIVO_LISTO_2026}
    candidates: set[Path] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".csv", ".xlsx", ".xls", ".tsv", ".txt", ".md"}:
            continue
        name = upper_ascii(str(path.relative_to(ROOT)))
        if path in explicit or any(upper_ascii(k) in name for k in keywords):
            candidates.add(path)
    rows: list[dict[str, Any]] = []
    for path in sorted(candidates, key=lambda p: str(p).lower()):
        info = inspect_candidate(path)
        period, level, evidence, utility, priority = infer_source(path, info["snippet"])
        rows.append(
            {
                "RUTA_ABSOLUTA": str(path.resolve()),
                "NOMBRE": path.name,
                "EXTENSION": path.suffix.lower(),
                "TAMANO_BYTES": path.stat().st_size,
                "FECHA_MODIFICACION": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "SHA256": sha256(path),
                "HOJAS": info["hojas"],
                "ENCABEZADOS": info["encabezados"],
                "CANTIDAD_FILAS": info["filas"],
                "PERIODO_REPRESENTADO": period,
                "NIVEL_INFORMACION": level,
                "EVIDENCIA_ENTREGA_OFICIAL": evidence,
                "UTILIDAD_PROCESO": utility,
                "PRIORIDAD_USO": priority,
            }
        )
    return rows


def read_inputs() -> dict[str, Any]:
    da = pd.read_excel(DATOS_XLSX, sheet_name="DatosAlumnos", dtype=str, engine="openpyxl")
    da.columns = [clean(c) for c in da.columns]
    da["_FILA_ORIGEN"] = da.index + 2
    da["RUN_CUERPO"] = da["RUT"].map(lambda x: split_run(x)[0])
    da["DV_NORM"] = da["RUT"].map(lambda x: split_run(x)[1])
    da["NAC_NORM"] = da["NACIONALIDAD"].map(upper_ascii)

    hoja = pd.read_excel(
        DATOS_XLSX,
        sheet_name="Hoja1",
        dtype=str,
        engine="openpyxl",
        usecols=lambda c: c
        in {
            "CODCLI",
            "RUT",
            "DIG",
            "NOMBRE",
            "PATERNO",
            "MATERNO",
            "CODCARR",
            "CARRERA",
            "JORNADA",
            "ANO",
            "PERIODO",
            "ESTADO_ACADEMICO",
            "PLAN_DE_ESTUDIO",
        },
    )
    hoja.columns = [clean(c) for c in hoja.columns]
    hoja["_FILA_ORIGEN"] = hoja.index + 2
    hoja["RUN_CUERPO"] = hoja["RUT"].map(normalize_doc)

    ctrl = pd.read_csv(MATRICULA_2025_CONTROL, dtype=str, keep_default_na=False)
    ctrl["_FILA_ORIGEN"] = ctrl.index + 2
    ctrl["RUN_CUERPO"] = ctrl["NUM_DOCUMENTO"].map(normalize_doc)

    gob = pd.read_csv(GOB_NAC, sep="\t", dtype=str, keep_default_na=False)
    gob["NAC_JOIN"] = gob["NACIONALIDAD_ORIG"].map(upper_ascii)

    bridge = pd.read_csv(BRIDGE, sep="\t", dtype=str, keep_default_na=False)

    return {"da": da, "hoja": hoja, "ctrl": ctrl, "gob": gob, "bridge": bridge}


def nationality_code(gob: pd.DataFrame, raw: Any) -> str:
    norm = upper_ascii(raw)
    hit = gob[gob["NAC_JOIN"] == norm]
    if hit.empty:
        return ""
    return clean(hit.iloc[0].get("COD_NAC", ""))


def nationality_status(raw: Any, code: str) -> str:
    norm = upper_ascii(raw)
    if not norm:
        return "SIN_DATO"
    if "CHIL" in norm or code == "38":
        return "CHILENA_NO_CORRESPONDE"
    if norm in {"POR DEFINIR", "SIN INFORMACION", "NO INFORMADO"} or not code:
        return "NACIONALIDAD_POR_CONFIRMAR"
    return "EXTRANJERA_CONFIRMADA"


def da_candidates_by_run(da: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {run: group.copy() for run, group in da.groupby("RUN_CUERPO", dropna=False) if clean(run)}


def pick_da_for_control(ctrl_row: pd.Series, da_by_run: dict[str, pd.DataFrame]) -> pd.Series | None:
    run = clean(ctrl_row.get("RUN_CUERPO", ""))
    codcarpr = clean(ctrl_row.get("CODIGO_UNICO", ""))
    group = da_by_run.get(run)
    if group is None or group.empty:
        return None
    exact = group[group.get("CODCARPR", "").fillna("").map(clean) == codcarpr]
    if not exact.empty:
        exact_2025 = exact[exact.get("ANOMATRICULA", "").fillna("").map(clean) == "2025"]
        if not exact_2025.empty:
            return exact_2025.iloc[0]
        return exact.sort_values("ANOMATRICULA", ascending=False).iloc[0]
    year_2025 = group[group.get("ANOMATRICULA", "").fillna("").map(clean) == "2025"]
    if not year_2025.empty:
        return year_2025.iloc[0]
    return group.sort_values("ANOMATRICULA", ascending=False).iloc[0]


def jornada_lookup(hoja: pd.DataFrame) -> dict[tuple[str, str], str]:
    h25 = hoja[hoja["ANO"].fillna("").map(clean) == "2025"].copy()
    lookup: dict[tuple[str, str], str] = {}
    for (run, codcarr), group in h25.groupby(["RUN_CUERPO", "CODCARR"], dropna=False):
        jornadas = sorted({clean(x) for x in group["JORNADA"] if clean(x)})
        if len(jornadas) == 1:
            lookup[(clean(run), clean(codcarr))] = jornadas[0]
    return lookup


def nombre_completo(row: pd.Series | dict[str, Any]) -> str:
    if row is None:
        return ""
    nombres = clean(row.get("NOMBRES", "")) or clean(row.get("NOMBRE", ""))
    ap1 = clean(row.get("APELLIDO PATERNO", "")) or clean(row.get("PATERNO", ""))
    ap2 = clean(row.get("APELLIDO MATERNO", "")) or clean(row.get("MATERNO", ""))
    return clean(f"{nombres} {ap1} {ap2}")


def build_universe(inputs: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    da = inputs["da"]
    ctrl = inputs["ctrl"]
    gob = inputs["gob"]
    da_by_run = da_candidates_by_run(da)
    jornada_by_key = jornada_lookup(inputs["hoja"])
    rows: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for _, ctrl_row in ctrl.iterrows():
        da_row = pick_da_for_control(ctrl_row, da_by_run)
        if da_row is None:
            continue
        code = nationality_code(gob, da_row.get("NACIONALIDAD", ""))
        nat_status = nationality_status(da_row.get("NACIONALIDAD", ""), code)
        if nat_status == "CHILENA_NO_CORRESPONDE" or nat_status == "SIN_DATO":
            continue
        run = clean(ctrl_row.get("RUN_CUERPO", ""))
        internal_code = clean(ctrl_row.get("CODIGO_UNICO", ""))
        key = (run, internal_code, clean(ctrl_row.get("PLAN_ESTUDIOS", "")))
        seen_keys.add(key)
        classification = "CONFIRMADO_MATRICULA_2025" if nat_status == "EXTRANJERA_CONFIRMADA" else "NACIONALIDAD_POR_CONFIRMAR"
        include = "SI" if nat_status == "EXTRANJERA_CONFIRMADA" else "PENDIENTE_CONFIRMACION"
        jornada = jornada_by_key.get((run, internal_code), clean(da_row.get("JORNADA", "")))
        rows.append(
            {
                "ID_CONTROL": f"CORR-2025-{len(rows)+1:04d}",
                "CODCLI": clean(da_row.get("CODCLI", "")),
                "TIPO_DOCUMENTO": clean(ctrl_row.get("TIPO_DOCUMENTO", "")) or "R",
                "NUM_DOCUMENTO": run,
                "DV": clean(ctrl_row.get("DV", "")),
                "NOMBRE_COMPLETO": nombre_completo(da_row),
                "NACIONALIDAD": clean(da_row.get("NACIONALIDAD", "")),
                "CODIGO_NACIONALIDAD": code,
                "FUENTE_INGRESO_UNIVERSO": "MATRICULA_OFICIAL_2025",
                "ARCHIVO_FUENTE": str(MATRICULA_2025_CONTROL.resolve()),
                "HOJA": "",
                "FILA_ORIGEN": clean(ctrl_row.get("_FILA_ORIGEN", "")),
                "EVIDENCIA_MATRICULA_2025": f"matricula_avance_curricular_2025_control.csv fila {ctrl_row.get('_FILA_ORIGEN')}; PLAN_ESTUDIOS={clean(ctrl_row.get('PLAN_ESTUDIOS',''))}; CURSO_1ER_SEM={clean(ctrl_row.get('CURSO_1ER_SEM',''))}; UNIDADES_CURSADAS={clean(ctrl_row.get('UNIDADES_CURSADAS',''))}; UNID_CURSADAS_TOTAL={clean(ctrl_row.get('UNID_CURSADAS_TOTAL',''))}",
                "TIPO_EVIDENCIA": "CONTROL_AVANCE_CURRICULAR_2025",
                "CLASIFICACION_UNIVERSO": classification,
                "MOTIVO_CLASIFICACION": "Documento presente en control de avance/matricula 2025; nacionalidad cruzada por fuente institucional.",
                "INCLUIR_EN_PROCESO": include,
                "REQUIERE_CONFIRMACION": "SI" if include != "SI" else "NO",
                "OBSERVACION": "Precarga PES no encontrada localmente; no se uso matricula congelada 2026 como evidencia.",
                "CODIGO_CARRERA_INTERNO": internal_code,
                "PLAN_ESTUDIOS": clean(ctrl_row.get("PLAN_ESTUDIOS", "")),
                "JORNADA_EVIDENCIA": jornada,
                "SEDE": clean(da_row.get("SEDE", "")),
                "NOMBRE_CARRERA": clean(da_row.get("NOMBRE_L", "")),
                "ANOMATRICULA_IDENTIDAD": clean(da_row.get("ANOMATRICULA", "")),
                "FILA_IDENTIDAD_DATOSALUMNOS": clean(da_row.get("_FILA_ORIGEN", "")),
                "FECHA_MATRICULA_DA": normalize_date(da_row.get("FECHAMATRICULA", "")),
                "ESTADOACADEMICO_DA": clean(da_row.get("ESTADOACADEMICO", "")),
                "SITUACION_DA": clean(da_row.get("SITUACION", "")),
                "MATRICULA_DA": clean(da_row.get("MATRICULA", "")),
                "SEXO_DA": clean(da_row.get("SEXO", "")),
                "FECHA_NACIMIENTO_DA": normalize_date(da_row.get("FECHANACIMIENTO", "")),
                "NOMBRES_DA": clean(da_row.get("NOMBRES", "")),
                "PRIMER_APELLIDO_DA": clean(da_row.get("APELLIDO PATERNO", "")),
                "SEGUNDO_APELLIDO_DA": clean(da_row.get("APELLIDO MATERNO", "")),
                "ANOINGRESO_DA": clean(da_row.get("ANOINGRESO", "")),
                "PERIODOINGRESO_DA": clean(da_row.get("PERIODOINGRESO", "")),
            }
        )

    da_2025 = da[da["ANOMATRICULA"].fillna("").map(clean) == "2025"].copy()
    for _, da_row in da_2025.iterrows():
        run = clean(da_row.get("RUN_CUERPO", ""))
        codcarpr = clean(da_row.get("CODCARPR", ""))
        if (run, codcarpr, clean(codcarpr + clean(da_row.get("ANOINGRESO", "")))) in seen_keys:
            continue
        if any(r["NUM_DOCUMENTO"] == run and r["CODIGO_CARRERA_INTERNO"] == codcarpr for r in rows):
            continue
        code = nationality_code(gob, da_row.get("NACIONALIDAD", ""))
        nat_status = nationality_status(da_row.get("NACIONALIDAD", ""), code)
        if nat_status == "CHILENA_NO_CORRESPONDE" or nat_status == "SIN_DATO":
            continue
        classification = "CONFIRMADO_OTRA_EVIDENCIA_2025" if nat_status == "EXTRANJERA_CONFIRMADA" else "NACIONALIDAD_POR_CONFIRMAR"
        include = "SI" if nat_status == "EXTRANJERA_CONFIRMADA" else "PENDIENTE_CONFIRMACION"
        rows.append(
            {
                "ID_CONTROL": f"CORR-2025-{len(rows)+1:04d}",
                "CODCLI": clean(da_row.get("CODCLI", "")),
                "TIPO_DOCUMENTO": "R" if run else "",
                "NUM_DOCUMENTO": run,
                "DV": clean(da_row.get("DV_NORM", "")),
                "NOMBRE_COMPLETO": nombre_completo(da_row),
                "NACIONALIDAD": clean(da_row.get("NACIONALIDAD", "")),
                "CODIGO_NACIONALIDAD": code,
                "FUENTE_INGRESO_UNIVERSO": "OTRA_EVIDENCIA_2025",
                "ARCHIVO_FUENTE": str(DATOS_XLSX.resolve()),
                "HOJA": "DatosAlumnos",
                "FILA_ORIGEN": clean(da_row.get("_FILA_ORIGEN", "")),
                "EVIDENCIA_MATRICULA_2025": f"DatosAlumnos fila {da_row.get('_FILA_ORIGEN')}; ANOMATRICULA=2025; FECHAMATRICULA={normalize_date(da_row.get('FECHAMATRICULA',''))}; ESTADOACADEMICO={clean(da_row.get('ESTADOACADEMICO',''))}; SITUACION={clean(da_row.get('SITUACION',''))}; MATRICULA={clean(da_row.get('MATRICULA',''))}",
                "TIPO_EVIDENCIA": "DATOSALUMNOS_ANOMATRICULA_2025",
                "CLASIFICACION_UNIVERSO": classification,
                "MOTIVO_CLASIFICACION": "No aparece en control principal 2025, pero DatosAlumnos registra ANOMATRICULA=2025 con nacionalidad extranjera o pendiente.",
                "INCLUIR_EN_PROCESO": include,
                "REQUIERE_CONFIRMACION": "SI" if include != "SI" else "NO",
                "OBSERVACION": "Caso agregado solo por evidencia institucional 2025 complementaria; requiere revision si no aparece en entrega/control 2025.",
                "CODIGO_CARRERA_INTERNO": codcarpr,
                "PLAN_ESTUDIOS": "",
                "JORNADA_EVIDENCIA": clean(da_row.get("JORNADA", "")),
                "SEDE": clean(da_row.get("SEDE", "")),
                "NOMBRE_CARRERA": clean(da_row.get("NOMBRE_L", "")),
                "ANOMATRICULA_IDENTIDAD": clean(da_row.get("ANOMATRICULA", "")),
                "FILA_IDENTIDAD_DATOSALUMNOS": clean(da_row.get("_FILA_ORIGEN", "")),
                "FECHA_MATRICULA_DA": normalize_date(da_row.get("FECHAMATRICULA", "")),
                "ESTADOACADEMICO_DA": clean(da_row.get("ESTADOACADEMICO", "")),
                "SITUACION_DA": clean(da_row.get("SITUACION", "")),
                "MATRICULA_DA": clean(da_row.get("MATRICULA", "")),
                "SEXO_DA": clean(da_row.get("SEXO", "")),
                "FECHA_NACIMIENTO_DA": normalize_date(da_row.get("FECHANACIMIENTO", "")),
                "NOMBRES_DA": clean(da_row.get("NOMBRES", "")),
                "PRIMER_APELLIDO_DA": clean(da_row.get("APELLIDO PATERNO", "")),
                "SEGUNDO_APELLIDO_DA": clean(da_row.get("APELLIDO MATERNO", "")),
                "ANOINGRESO_DA": clean(da_row.get("ANOINGRESO", "")),
                "PERIODOINGRESO_DA": clean(da_row.get("PERIODOINGRESO", "")),
            }
        )

    reference_2026 = build_only_2026_reference(inputs, {r["NUM_DOCUMENTO"] for r in rows})
    rows.extend(reference_2026)
    aux = {r["ID_CONTROL"]: r for r in rows}
    return rows, aux


def build_only_2026_reference(inputs: dict[str, Any], docs_with_evidence: set[str]) -> list[dict[str, Any]]:
    if not ARCHIVO_LISTO_2026.exists():
        return []
    cols = [
        "TIPO_DOC",
        "N_DOC",
        "DV",
        "PRIMER_APELLIDO",
        "SEGUNDO_APELLIDO",
        "NOMBRE",
        "NAC",
        "CODCLI",
        "DA_ANOMATRICULA",
        "CODIGO_CARRERA_SIES_FINAL",
        "INCLUIR_EN_MATRICULA_32",
    ]
    df = pd.read_excel(ARCHIVO_LISTO_2026, sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str, engine="openpyxl", usecols=lambda c: c in cols)
    for col in cols:
        if col not in df:
            df[col] = ""
    df["RUN_CUERPO"] = df["N_DOC"].map(normalize_doc)
    foreign = df[df["NAC"].fillna("").map(clean).ne("") & df["NAC"].fillna("").map(clean).ne("38")].copy()
    foreign = foreign[~foreign["RUN_CUERPO"].isin(docs_with_evidence)]
    rows = []
    for _, r in foreign.drop_duplicates(["RUN_CUERPO", "CODIGO_CARRERA_SIES_FINAL"]).iterrows():
        rows.append(
            {
                "ID_CONTROL": f"CORR-2025-REF-{len(rows)+1:04d}",
                "CODCLI": clean(r.get("CODCLI", "")),
                "TIPO_DOCUMENTO": clean(r.get("TIPO_DOC", "")),
                "NUM_DOCUMENTO": clean(r.get("RUN_CUERPO", "")),
                "DV": clean(r.get("DV", "")),
                "NOMBRE_COMPLETO": clean(f"{r.get('NOMBRE','')} {r.get('PRIMER_APELLIDO','')} {r.get('SEGUNDO_APELLIDO','')}"),
                "NACIONALIDAD": "",
                "CODIGO_NACIONALIDAD": clean(r.get("NAC", "")),
                "FUENTE_INGRESO_UNIVERSO": "SOLO_REFERENCIA_2026",
                "ARCHIVO_FUENTE": str(ARCHIVO_LISTO_2026.resolve()),
                "HOJA": "ARCHIVO_LISTO_SUBIDA",
                "FILA_ORIGEN": "",
                "EVIDENCIA_MATRICULA_2025": "",
                "TIPO_EVIDENCIA": "SIN_EVIDENCIA_2025",
                "CLASIFICACION_UNIVERSO": "SOLO_REFERENCIA_2026_SIN_EVIDENCIA_2025",
                "MOTIVO_CLASIFICACION": "Presente en fuente 2026 sin evidencia 2025 local.",
                "INCLUIR_EN_PROCESO": "NO",
                "REQUIERE_CONFIRMACION": "NO",
                "OBSERVACION": "No incorporar al proceso sin evidencia 2025.",
                "CODIGO_CARRERA_INTERNO": "",
                "PLAN_ESTUDIOS": "",
                "JORNADA_EVIDENCIA": "",
                "SEDE": "",
                "NOMBRE_CARRERA": "",
                "ANOMATRICULA_IDENTIDAD": clean(r.get("DA_ANOMATRICULA", "")),
                "FILA_IDENTIDAD_DATOSALUMNOS": "",
                "FECHA_MATRICULA_DA": "",
                "ESTADOACADEMICO_DA": "",
                "SITUACION_DA": "",
                "MATRICULA_DA": "",
                "SEXO_DA": "",
                "FECHA_NACIMIENTO_DA": "",
                "NOMBRES_DA": clean(r.get("NOMBRE", "")),
                "PRIMER_APELLIDO_DA": clean(r.get("PRIMER_APELLIDO", "")),
                "SEGUNDO_APELLIDO_DA": clean(r.get("SEGUNDO_APELLIDO", "")),
                "ANOINGRESO_DA": "",
                "PERIODOINGRESO_DA": "",
            }
        )
    return rows


def resolve_codigo_sies(row: dict[str, Any], bridge: pd.DataFrame) -> tuple[str, str, str]:
    codcarpr = clean(row.get("CODIGO_CARRERA_INTERNO", ""))
    jornada = clean(row.get("JORNADA_EVIDENCIA", ""))
    if not codcarpr:
        return "", "SIN_CODCARPR", "No hay codigo interno de carrera/programa."
    matches = bridge[bridge["CODCARPR"].fillna("").map(clean) == codcarpr].copy()
    if matches.empty:
        return "", "SIN_CODIGO", "CODCARPR no aparece en puente SIES."
    if jornada:
        exact = matches[matches["JORNADA"].fillna("").map(clean) == jornada]
        finals = sorted({clean(x) for x in exact.get("CODIGO_UNICO_FINAL", pd.Series(dtype=str)) if clean(x)})
        if len(finals) == 1:
            return finals[0], "RESUELTO_REGLA_INSTITUCIONAL", "CODCARPR + jornada con un CODIGO_UNICO_FINAL."
        potentials = sorted({clean(x) for x in exact.get("CODIGOS_SIES_POTENCIALES", pd.Series(dtype=str)) if clean(x)})
        if potentials:
            return "", "AMBIGUO", " | ".join(potentials)
    finals = sorted({clean(x) for x in matches.get("CODIGO_UNICO_FINAL", pd.Series(dtype=str)) if clean(x)})
    if len(finals) == 1:
        return finals[0], "RESUELTO_UNICO_CODCARPR", "CODCARPR posee un unico codigo final en puente."
    if finals:
        return "", "AMBIGUO", " | ".join(finals)
    potentials = sorted({clean(x) for x in matches.get("CODIGOS_SIES_POTENCIALES", pd.Series(dtype=str)) if clean(x)})
    return "", "REQUIERE_CONFIRMACION" if potentials else "SIN_CODIGO", " | ".join(potentials)


def set_trace(row: dict[str, Any], field: str, value: str, raw: str, source: str, rule: str, status: str) -> None:
    row[field] = value
    row[f"FUENTE_DATO_{field}"] = source
    row[f"DATO_BRUTO_{field}"] = raw
    row[f"DATO_NORMALIZADO_{field}"] = value
    row[f"REGLA_{field}"] = rule
    row[f"ESTADO_CAMPO_{field}"] = status


def build_base(universe: list[dict[str, Any]], inputs: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    base_rows: list[dict[str, Any]] = []
    vig_rows: list[dict[str, Any]] = []
    reuse_rows: list[dict[str, Any]] = []
    bridge = inputs["bridge"]
    for src in universe:
        if src["INCLUIR_EN_PROCESO"] == "NO":
            continue
        row: dict[str, Any] = {
            "ID_CONTROL": src["ID_CONTROL"],
            "CODCLI": src["CODCLI"],
            "FUENTE_UNIVERSO": src["FUENTE_INGRESO_UNIVERSO"],
            "ARCHIVO_ORIGEN_UNIVERSO": src["ARCHIVO_FUENTE"],
            "HOJA_ORIGEN_UNIVERSO": src["HOJA"],
            "FILA_ORIGEN_UNIVERSO": src["FILA_ORIGEN"],
            "EVIDENCIA_2025": src["EVIDENCIA_MATRICULA_2025"],
            "ESTADO_EVIDENCIA": "EVIDENCIA_2025_VALIDA" if src["EVIDENCIA_MATRICULA_2025"] else "SIN_EVIDENCIA_2025",
            "DECISION_INCLUSION": src["INCLUIR_EN_PROCESO"],
            "MOTIVO_DECISION": src["MOTIVO_CLASIFICACION"],
            "CLASIFICACION_UNIVERSO": src["CLASIFICACION_UNIVERSO"],
            "REQUIERE_CONFIRMACION": src["REQUIERE_CONFIRMACION"],
            "CODIGO_CARRERA_INTERNO": src["CODIGO_CARRERA_INTERNO"],
            "PLAN_ESTUDIOS": src["PLAN_ESTUDIOS"],
            "JORNADA_EVIDENCIA": src["JORNADA_EVIDENCIA"],
            "SEDE": src["SEDE"],
            "NOMBRE_CARRERA": src["NOMBRE_CARRERA"],
        }
        for field in OFFICIAL_FIELDS:
            set_trace(row, field, "", "", "", "", "PENDIENTE")

        set_trace(row, "TIPO_DOCUMENTO", src["TIPO_DOCUMENTO"], src["TIPO_DOCUMENTO"], src["ARCHIVO_FUENTE"], "Solo R/P; IPE no permitido.", "COMPLETO")
        set_trace(row, "NUM_DOCUMENTO", src["NUM_DOCUMENTO"], src["NUM_DOCUMENTO"], src["ARCHIVO_FUENTE"], "Documento normalizado sin puntuacion; CODCLI no reemplaza documento.", "COMPLETO")
        set_trace(row, "DV", src["DV"], src["DV"], src["ARCHIVO_FUENTE"], "DV separado del RUN; vacio solo si pasaporte.", "COMPLETO")
        set_trace(row, "PRIMER_APELLIDO", upper_ascii(src["PRIMER_APELLIDO_DA"]), src["PRIMER_APELLIDO_DA"], "DatosAlumnos", "Mayusculas, sin acentos, espacios simples.", "COMPLETO" if src["PRIMER_APELLIDO_DA"] else "PENDIENTE")
        set_trace(row, "SEGUNDO_APELLIDO", upper_ascii(src["SEGUNDO_APELLIDO_DA"]), src["SEGUNDO_APELLIDO_DA"], "DatosAlumnos", "Mayusculas, sin acentos, espacios simples.", "COMPLETO" if src["SEGUNDO_APELLIDO_DA"] else "PENDIENTE")
        set_trace(row, "NOMBRES", upper_ascii(src["NOMBRES_DA"]), src["NOMBRES_DA"], "DatosAlumnos", "Mayusculas, sin acentos, espacios simples.", "COMPLETO" if src["NOMBRES_DA"] else "PENDIENTE")
        sexo = normalize_sex(src["SEXO_DA"])
        set_trace(row, "SEXO", sexo, src["SEXO_DA"], "DatosAlumnos", "Mapeo institucional F/M a catalogo SIES M/H.", "COMPLETO" if sexo else "PENDIENTE")
        set_trace(row, "FECHA_NACIMIENTO", src["FECHA_NACIMIENTO_DA"], src["FECHA_NACIMIENTO_DA"], "DatosAlumnos", "Fecha normalizada DD-MM-AAAA.", "COMPLETO" if src["FECHA_NACIMIENTO_DA"] else "PENDIENTE")
        nac_status = "COMPLETO" if src["CODIGO_NACIONALIDAD"] and src["CODIGO_NACIONALIDAD"] != "38" else "PENDIENTE_CONFIRMACION"
        set_trace(row, "NACIONALIDAD", src["CODIGO_NACIONALIDAD"], src["NACIONALIDAD"], "DatosAlumnos + gobernanza_nac.tsv", "Mapeo gobernado; no inferir nacionalidad.", nac_status)

        set_trace(row, "TIPO_RESIDENCIA_ESTUDIANTE", "", "", "No detectada", "No inferir desde domicilio, nacionalidad ni modalidad.", "PENDIENTE_GESTION")
        set_trace(row, "PAIS_DE_ORIGEN", "", "", "No detectada", "Depende de residencia; no inferir desde nacionalidad.", "PENDIENTE_GESTION")
        set_trace(row, "PAIS_ESTUDIOS_SECUNDARIOS", "", "", "No completado automaticamente", "Debe responderse con pais donde completo secundaria.", "PENDIENTE_GESTION")

        code, code_status, code_obs = resolve_codigo_sies(src, bridge)
        code_field_status = "COMPLETO" if code else "CONFLICTO_CODIGO_UNICO"
        set_trace(row, "CODIGO_UNICO", code, code_obs, "PUENTE_SIES_COMPILADO.tsv", "Resolver por CODCARPR+jornada o codigo unico deterministico; no por similitud de nombre.", code_field_status)
        row["CODIGO_UNICO_ESTADO_RESOLUCION"] = code_status
        row["CODIGO_UNICO_OBSERVACION"] = code_obs

        if src["ANOMATRICULA_IDENTIDAD"] == "2025":
            set_trace(row, "ANIO_INGRESO_CARRERA_ACTUAL", src["ANOINGRESO_DA"], src["ANOINGRESO_DA"], "DatosAlumnos", "Reutilizado solo porque la fila de identidad corresponde a ANOMATRICULA=2025.", "COMPLETO" if src["ANOINGRESO_DA"] else "PENDIENTE")
            set_trace(row, "SEM_INGRESO_CARRERA_ACTUAL", src["PERIODOINGRESO_DA"], src["PERIODOINGRESO_DA"], "DatosAlumnos", "Reutilizado solo porque la fila de identidad corresponde a ANOMATRICULA=2025.", "COMPLETO" if src["PERIODOINGRESO_DA"] else "PENDIENTE")
        else:
            set_trace(row, "ANIO_INGRESO_CARRERA_ACTUAL", "", src["ANOINGRESO_DA"], "DatosAlumnos", "No se reutiliza dato de identidad 2026 sin respaldo historico 2025.", "PENDIENTE_CONFIRMACION")
            set_trace(row, "SEM_INGRESO_CARRERA_ACTUAL", "", src["PERIODOINGRESO_DA"], "DatosAlumnos", "No se reutiliza dato de identidad 2026 sin respaldo historico 2025.", "PENDIENTE_CONFIRMACION")
        set_trace(row, "ANIO_INGRESO_CARRERA_ORIGEN", "", "", "No resuelto", "No copiar ingreso actual sin regla trazada.", "PENDIENTE_CONFIRMACION")
        set_trace(row, "SEM_INGRESO_CARRERA_ORIGEN", "", "", "No resuelto", "No copiar ingreso actual sin regla trazada.", "PENDIENTE_CONFIRMACION")
        set_trace(row, "NOMBRE_UNIVERSIDAD_ORIGEN", "", "", "No detectada", "Solo aplica doble titulacion; no inferir.", "NO_APLICA_PENDIENTE_CONFIRMACION")
        set_trace(row, "PAIS_UNIVERSIDAD_ORIGEN", "", "", "No detectada", "Solo aplica doble titulacion; no inferir.", "NO_APLICA_PENDIENTE_CONFIRMACION")
        set_trace(row, "VIGENCIA", "1", src["EVIDENCIA_MATRICULA_2025"], src["ARCHIVO_FUENTE"], "Asignar 1 solo por evidencia de matricula/actividad 2025.", "COMPLETO_EVIDENCIA_2025")
        row["CLAVE_OFICIAL_PRELIMINAR"] = f"162|{row['TIPO_DOCUMENTO']}|{row['NUM_DOCUMENTO']}|{row['CODIGO_UNICO'] or 'SIN_CODIGO'}"
        base_rows.append(row)

        vig_rows.append(
            {
                "ID_CONTROL": src["ID_CONTROL"],
                "CODCLI": src["CODCLI"],
                "NUM_DOCUMENTO": src["NUM_DOCUMENTO"],
                "CODIGO_UNICO": code,
                "VIGENCIA_PROPUESTA": "1",
                "EVIDENCIA_2025": src["EVIDENCIA_MATRICULA_2025"],
                "FUENTE_EVIDENCIA": src["ARCHIVO_FUENTE"],
                "ESTADO_VALIDACION": "EVIDENCIA_2025_VALIDA",
                "NO_USA_MATRICULA_2026": "SI",
                "REQUIERE_CONFIRMACION": src["REQUIERE_CONFIRMACION"],
                "OBSERVACION": "Vigencia 2025 no se asigna desde matricula 2026.",
            }
        )

    reuse_rows = build_reuse_audit(base_rows)
    return base_rows, vig_rows, reuse_rows


def build_reuse_audit(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    watched = [
        "NUM_DOCUMENTO",
        "NACIONALIDAD",
        "CODIGO_UNICO",
        "ANIO_INGRESO_CARRERA_ACTUAL",
        "SEM_INGRESO_CARRERA_ACTUAL",
        "ANIO_INGRESO_CARRERA_ORIGEN",
        "SEM_INGRESO_CARRERA_ORIGEN",
        "VIGENCIA",
    ]
    rows = []
    for field in watched:
        sources = Counter(clean(r.get(f"FUENTE_DATO_{field}", "")) for r in base_rows)
        statuses = Counter(clean(r.get(f"ESTADO_CAMPO_{field}", "")) for r in base_rows)
        requires = "SI" if any(k.startswith("PENDIENTE") or "CONFLICTO" in k for k in statuses) else "NO"
        compatibility = "COMPATIBLE" if requires == "NO" else "COMPATIBLE_PARCIAL"
        if field in {"ANIO_INGRESO_CARRERA_ACTUAL", "SEM_INGRESO_CARRERA_ACTUAL"}:
            compatibility = "COMPATIBLE_SOLO_CON_FILA_2025; 2026_NO_REUTILIZADO"
        rows.append(
            {
                "CAMPO": field,
                "FUENTE": " | ".join(f"{k}:{v}" for k, v in sources.items()),
                "PERIODO": "2025 para evidencia; 2026 solo apoyo si se marco pendiente",
                "DEFINICION": "Variable oficial del Anexo I Extranjeros Regulares 2026.",
                "COMPATIBILIDAD_INSTRUCTIVO": compatibility,
                "NIVEL_CONFIANZA": "ALTO" if requires == "NO" else "MEDIO/BAJO",
                "REQUIERE_CONFIRMACION": requires,
                "ESTADOS_CAMPO": " | ".join(f"{k}:{v}" for k, v in statuses.items()),
            }
        )
    return rows


def compare_previous(universe: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prev_u = AUD / "UNIVERSO_CANDIDATOS_EXTRANJEROS_2025.csv"
    prev_b = INTERIM / "BASE_MAESTRA_EXTRANJEROS_REGULARES_2025.csv"
    if not prev_u.exists():
        return []
    prev = pd.read_csv(prev_u, dtype=str, keep_default_na=False)
    prev["RUN_CUERPO"] = prev["NUM_DOCUMENTO_BRUTO"].map(lambda x: split_run(x)[0])
    prev_base = pd.read_csv(prev_b, dtype=str, keep_default_na=False) if prev_b.exists() else pd.DataFrame()
    by_doc = defaultdict(list)
    for r in universe:
        by_doc[r["NUM_DOCUMENTO"]].append(r)
    rows = []
    for _, p in prev.iterrows():
        run = clean(p.get("RUN_CUERPO", ""))
        matches = by_doc.get(run, [])
        appears_official = any(m["FUENTE_INGRESO_UNIVERSO"] == "MATRICULA_OFICIAL_2025" for m in matches)
        appears_other = any(m["FUENTE_INGRESO_UNIVERSO"] == "OTRA_EVIDENCIA_2025" for m in matches)
        appears_2026 = any(m["FUENTE_INGRESO_UNIVERSO"] == "SOLO_REFERENCIA_2026" for m in matches)
        confirmed = any(m["CODIGO_NACIONALIDAD"] and m["CODIGO_NACIONALIDAD"] != "38" for m in matches)
        evidence = " | ".join(sorted({m["TIPO_EVIDENCIA"] for m in matches if m["EVIDENCIA_MATRICULA_2025"]}))
        if any(m["CLASIFICACION_UNIVERSO"] == "NACIONALIDAD_POR_CONFIRMAR" for m in matches):
            decision = "NACIONALIDAD_PENDIENTE"
        elif appears_official and confirmed:
            decision = "CONFIRMADO_MATRICULA_2025"
        elif appears_other and confirmed:
            decision = "CONFIRMADO_OTRA_EVIDENCIA_2025"
        elif appears_2026:
            decision = "SOLO_2026_NO_INCLUIR"
        else:
            decision = "SIN_EVIDENCIA"
        base_hit = prev_base[prev_base["NUM_DOCUMENTO"].map(clean) == run] if not prev_base.empty and "NUM_DOCUMENTO" in prev_base else pd.DataFrame()
        rows.append(
            {
                "CODCLI": clean(p.get("CODCLI", "")),
                "NUM_DOCUMENTO": run,
                "NOMBRE_COMPLETO": clean(p.get("NOMBRE_COMPLETO", "")),
                "APARECE_PRECARGA_PES": "NO",
                "APARECE_MATRICULA_OFICIAL_2025": "SI" if appears_official else "NO",
                "APARECE_OTRA_FUENTE_MATRICULA_2025": "SI" if appears_other else "NO",
                "APARECE_SOLO_FUENTE_2026": "SI" if appears_2026 and not (appears_official or appears_other) else "NO",
                "NO_ENCONTRADO": "SI" if not matches else "NO",
                "NACIONALIDAD_CONFIRMADA": "SI" if confirmed else "NO",
                "EVIDENCIA_MATRICULA_EFECTIVA_2025": evidence,
                "DECISION_CORREGIDA": decision,
                "CODIGO_UNICO_BASE_ANTERIOR": " | ".join(sorted({clean(x) for x in base_hit.get("CODIGO_UNICO", []) if clean(x)})) if not base_hit.empty else "",
                "OBSERVACION": "Comparacion contra universo/base fase anterior; no se arrastra sin evidencia 2025.",
            }
        )
    return rows


def validate_universe(universe: list[dict[str, Any]], base_rows: list[dict[str, Any]], precarga_status: str) -> list[dict[str, Any]]:
    issues = []
    base_by_id = {r["ID_CONTROL"]: r for r in base_rows}
    doc_counts = Counter(r["NUM_DOCUMENTO"] for r in universe if r["INCLUIR_EN_PROCESO"] != "NO")
    for r in universe:
        included = r["INCLUIR_EN_PROCESO"] != "NO"
        base = base_by_id.get(r["ID_CONTROL"], {})
        def add(tipo: str, sev: str, msg: str) -> None:
            issues.append(
                {
                    "ID_CONTROL": r["ID_CONTROL"],
                    "CODCLI": r["CODCLI"],
                    "NUM_DOCUMENTO": r["NUM_DOCUMENTO"],
                    "TIPO_HALLAZGO": tipo,
                    "SEVERIDAD": sev,
                    "MENSAJE": msg,
                    "ACCION_REQUERIDA": "Revisar antes de generar CSV final PES.",
                }
            )
        if included and not r["EVIDENCIA_MATRICULA_2025"]:
            add("REGISTRO_SIN_EVIDENCIA_2025", "ERROR", "Registro incluido o pendiente sin evidencia 2025.")
        if r["CLASIFICACION_UNIVERSO"] == "SOLO_REFERENCIA_2026_SIN_EVIDENCIA_2025":
            add("REGISTRO_PRESENTE_SOLO_2026", "INFO", "Referencia 2026 excluida del proceso.")
        if included and upper_ascii(r["NACIONALIDAD"]).find("CHIL") >= 0:
            add("NACIONALIDAD_CHILENA", "ERROR", "Registro incluido con nacionalidad chilena.")
        if included and r["CLASIFICACION_UNIVERSO"] == "NACIONALIDAD_POR_CONFIRMAR":
            add("NACIONALIDAD_AMBIGUA", "PENDIENTE", "Nacionalidad no confirmada o sin codigo gobernado.")
        if included and doc_counts[r["NUM_DOCUMENTO"]] > 1:
            add("DUPLICIDAD_DOCUMENTAL", "ADVERTENCIA", "Documento aparece en mas de una combinacion; validar carreras/programas.")
        if included and clean(base.get("ESTADO_CAMPO_CODIGO_UNICO", "")).startswith("CONFLICTO"):
            add("CODIGO_UNICO_AMBIGUO", "PENDIENTE", clean(base.get("CODIGO_UNICO_OBSERVACION", "")))
        if included and clean(base.get("VIGENCIA", "")) != "1":
            add("VIGENCIA_SIN_EVIDENCIA", "ERROR", "Vigencia no puede asignarse sin evidencia 2025.")
        if included and precarga_status == "PRECARGA_NO_ENCONTRADA":
            add("MATRICULA_OFICIAL_AUSENTE_EN_PRECARGA_LOCAL", "ADVERTENCIA", "No existe precarga local para comprobar si este registro estaba precargado.")
    if precarga_status == "PRECARGA_NO_ENCONTRADA":
        issues.append(
            {
                "ID_CONTROL": "",
                "CODCLI": "",
                "NUM_DOCUMENTO": "",
                "TIPO_HALLAZGO": "PRECARGA_NO_ENCONTRADA",
                "SEVERIDAD": "ADVERTENCIA",
                "MENSAJE": "No se encontro reporte local de precarga PES Extranjeros Regulares 2026.",
                "ACCION_REQUERIDA": "Descargar/adjuntar reporte PES para cerrar comparacion oficial.",
            }
        )
    return issues


def coverage_rows(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    total = len(base_rows)
    for field in OFFICIAL_FIELDS:
        statuses = Counter(clean(r.get(f"ESTADO_CAMPO_{field}", "")) for r in base_rows)
        complete = sum(v for k, v in statuses.items() if k.startswith("COMPLETO"))
        pending = sum(v for k, v in statuses.items() if k.startswith("PENDIENTE"))
        conflicts = sum(v for k, v in statuses.items() if "CONFLICTO" in k)
        no_aplica = sum(v for k, v in statuses.items() if k.startswith("NO_APLICA"))
        denom = total - no_aplica if total > no_aplica else total
        rows.append(
            {
                "VARIABLE": field,
                "TOTAL": total,
                "COMPLETOS": complete,
                "PENDIENTES": pending,
                "CONFLICTOS": conflicts,
                "NO_APLICA": no_aplica,
                "COBERTURA": f"{(complete / denom * 100) if denom else 0:.1f}%",
                "ACCION": "Sin accion" if pending == 0 and conflicts == 0 else "Gestionar/confirmar",
            }
        )
    return rows


def create_management_workbook(path: Path, base_rows: list[dict[str, Any]], validation: list[dict[str, Any]], hierarchy: list[dict[str, Any]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "INSTRUCCIONES"
    instructions = [
        "Planilla corregida para Estudiantes Extranjeros Regulares SIES 2026, periodo 01-01-2025 a 31-12-2025.",
        "No se uso matricula congelada 2026 para demostrar vigencia 2025.",
        "Completar solo datos pendientes; no inferir nacionalidad, pais de origen ni pais de estudios secundarios.",
        "TIPO_RESIDENCIA_ESTUDIANTE: 1 con residencia previa, 2 sin residencia previa, 3 no reside en Chile.",
        "Si residencia=1, PAIS_DE_ORIGEN debe quedar vacio. Si residencia=2 o 3, debe completarse y no puede ser Chile.",
        "PAIS_ESTUDIOS_SECUNDARIOS corresponde al pais donde completo y aprobo la ensenanza secundaria.",
    ]
    for i, line in enumerate(instructions, 1):
        ws.cell(i, 1, line)
    ws.column_dimensions["A"].width = 130

    ws = wb.create_sheet("ESTUDIANTES")
    headers = [
        "ID_CONTROL",
        "CODCLI",
        "FUENTE_INCLUSION_PROCESO",
        "DECISION_INCLUSION",
        "NOMBRE_COMPLETO",
        "CARRERA",
        "SEDE",
        "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO",
        "DV",
        "NACIONALIDAD_CODIGO_ACTUAL",
        "CODIGO_UNICO_ACTUAL",
        "CODIGO_UNICO_ESTADO",
        "EVIDENCIA_2025",
        "TIPO_RESIDENCIA_ESTUDIANTE_RESPUESTA",
        "PAIS_DE_ORIGEN_RESPUESTA",
        "PAIS_ESTUDIOS_SECUNDARIOS_RESPUESTA",
        "NACIONALIDAD_RESPUESTA",
        "CONFIRMA_INCLUSION_PROCESO",
        "OBSERVACIONES_DOCENCIA",
        "RESPONSABLE_RESPUESTA",
        "FECHA_RESPUESTA",
    ]
    ws.append(headers)
    for r in base_rows:
        ws.append(
            [
                r["ID_CONTROL"],
                r["CODCLI"],
                r["FUENTE_UNIVERSO"],
                r["DECISION_INCLUSION"],
                clean(f"{r.get('NOMBRES','')} {r.get('PRIMER_APELLIDO','')} {r.get('SEGUNDO_APELLIDO','')}"),
                r["NOMBRE_CARRERA"],
                r["SEDE"],
                r["TIPO_DOCUMENTO"],
                r["NUM_DOCUMENTO"],
                r["DV"],
                r["NACIONALIDAD"],
                r["CODIGO_UNICO"],
                r["CODIGO_UNICO_ESTADO_RESOLUCION"],
                r["EVIDENCIA_2025"],
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="305496")
    ws.freeze_panes = "A2"
    widths = [16, 18, 28, 24, 36, 44, 12, 14, 16, 8, 20, 24, 26, 80, 34, 30, 36, 28, 24, 36, 24, 18]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx) if idx <= 26 else "Z"].width = width
    pending_fill = PatternFill("solid", fgColor="FFF2CC")
    conflict_fill = PatternFill("solid", fgColor="F4CCCC")
    for row_idx in range(2, ws.max_row + 1):
        for col_idx in [15, 16, 17]:
            ws.cell(row_idx, col_idx).fill = pending_fill
        if ws.cell(row_idx, 13).value not in {"RESUELTO_REGLA_INSTITUCIONAL", "RESUELTO_UNICO_CODCARPR"}:
            ws.cell(row_idx, 13).fill = conflict_fill
        if ws.cell(row_idx, 4).value == "PENDIENTE_CONFIRMACION":
            ws.cell(row_idx, 4).fill = pending_fill

    dv_res = DataValidation(type="list", formula1='"1 - Con residencia previa en Chile,2 - Sin residencia previa en Chile,3 - No reside en Chile"', allow_blank=True)
    dv_si_no = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
    ws.add_data_validation(dv_res)
    ws.add_data_validation(dv_si_no)
    dv_res.add(f"O2:O{max(ws.max_row, 2)}")
    dv_si_no.add(f"S2:S{max(ws.max_row, 2)}")

    ws_cov = wb.create_sheet("CONTROL_COBERTURA")
    cov = coverage_rows(base_rows)
    ws_cov.append(list(cov[0].keys()))
    for r in cov:
        ws_cov.append(list(r.values()))
    for cell in ws_cov[1]:
        cell.font = Font(bold=True)

    ws_val = wb.create_sheet("VALIDACION")
    val_headers = list(validation[0].keys()) if validation else ["SIN_HALLAZGOS"]
    ws_val.append(val_headers)
    for r in validation:
        ws_val.append([r.get(h, "") for h in val_headers])

    ws_f = wb.create_sheet("FUENTES")
    f_headers = list(hierarchy[0].keys()) if hierarchy else ["FUENTE"]
    ws_f.append(f_headers)
    for r in hierarchy:
        ws_f.append([r.get(h, "") for h in f_headers])

    wb.save(path)


def build_hierarchy(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "PRIORIDAD": "1",
            "FUENTE": "Reporte Precarga del Proceso Extranjeros Regulares 2026",
            "ARCHIVO": "NO_ENCONTRADO_LOCALMENTE",
            "ROL": "Fuente normativa prioritaria",
            "DECISION": "No reemplazar silenciosamente; queda brecha institucional.",
            "ESTADO": "PRECARGA_NO_ENCONTRADA",
        },
        {
            "PRIORIDAD": "2",
            "FUENTE": "Control local avance/matricula 2025",
            "ARCHIVO": rel(MATRICULA_2025_CONTROL),
            "ROL": "Fuente principal local de evidencia 2025",
            "DECISION": "Usar para reconstruir universo con nacionalidad cruzada; requiere confirmacion de si corresponde a entrega oficial SIES.",
            "ESTADO": "PRINCIPAL_DISPONIBLE",
        },
        {
            "PRIORIDAD": "2",
            "FUENTE": "PES ready avance curricular 2025",
            "ARCHIVO": rel(MATRICULA_2025_PES_READY),
            "ROL": "Respaldo de salida/carga 2025 asociada al control",
            "DECISION": "No usar como fuente de campos por ausencia de encabezado; conservar como evidencia de entrega/preparacion.",
            "ESTADO": "COMPLEMENTARIA",
        },
        {
            "PRIORIDAD": "3",
            "FUENTE": "DatosAlumnos y Hoja1 2025",
            "ARCHIVO": rel(DATOS_XLSX),
            "ROL": "Nacionalidad, identidad y evidencia complementaria 2025",
            "DECISION": "Usar para agregar casos con ANOMATRICULA=2025 no presentes en control principal.",
            "ESTADO": "COMPLEMENTARIA_2025",
        },
        {
            "PRIORIDAD": "4",
            "FUENTE": "Archivo listo para SIES / MU2026",
            "ARCHIVO": rel(ARCHIVO_LISTO_2026),
            "ROL": "Apoyo de identificacion/enriquecimiento 2026",
            "DECISION": "No usar para demostrar matricula efectiva 2025.",
            "ESTADO": "SOLO_APOYO_2026",
        },
    ]
    return rows


def report_precarga(status: str, inventory: list[dict[str, Any]]) -> str:
    possible = [r for r in inventory if "PRECARGA" in upper_ascii(r["NOMBRE"]) and "EXTRANJ" in upper_ascii(r["NOMBRE"])]
    lines = "\n".join(f"- `{r['RUTA_ABSOLUTA']}`" for r in possible) or "- No se encontraron archivos candidatos por nombre."
    return f"""# Diagnostico Precarga PES

Fecha: {RUN_TS}

Estado: **{status}**

No se encontro localmente un archivo que pueda acreditarse como "Reporte Precarga del Proceso Extranjeros Regulares 2026" descargado desde Reportes Asociados de PES.

## Candidatos por nombre

{lines}

## Decision

No se reemplazo la precarga con otra fuente. La reconstruccion usa fuentes 2025 locales y marca la ausencia de precarga como brecha institucional.
"""


def report_matricula(hierarchy: list[dict[str, Any]], universe: list[dict[str, Any]]) -> str:
    counts = Counter(r["FUENTE_INGRESO_UNIVERSO"] for r in universe)
    h_lines = "\n".join(f"| {r['PRIORIDAD']} | {r['FUENTE']} | `{r['ARCHIVO']}` | {r['ESTADO']} | {r['DECISION']} |" for r in hierarchy)
    return f"""# Identificacion Matricula Oficial 2025

Fecha: {RUN_TS}

No se encontro un archivo nombrado explicitamente como "matricula unificada 2025 congelada/oficial". La fuente principal local disponible para evidencia 2025 es `resultados/matricula_avance_curricular_2025_control.csv`, respaldada por `resultados/matricula_avance_curricular_2025_pes_ready.csv`.

## Conteos de reconstruccion

{json.dumps(dict(counts), ensure_ascii=False, indent=2)}

## Jerarquia aplicada

| Prioridad | Fuente | Archivo | Estado | Decision |
|---:|---|---|---|---|
{h_lines}
"""


def report_intercambio(inventory: list[dict[str, Any]]) -> str:
    hits = [
        r
        for r in inventory
        if any(k in upper_ascii(f"{r['NOMBRE']} {r['ENCABEZADOS']} {r['HOJAS']}") for k in ["INTERCAMBIO", "MOVILIDAD", "STUDY", "PASANT", "VISITANTE", "RELACIONES INTERNACIONALES"])
        and "INSTRUCTIVO" not in upper_ascii(r["NOMBRE"])
        and "ESTUDIANTES_EXTRANJEROS_2026" not in upper_ascii(r["RUTA_ABSOLUTA"])
    ]
    status = "SIN_FUENTE_LOCAL" if not hits else "REQUIERE_CONSULTA_INSTITUCIONAL"
    hit_lines = "\n".join(f"- `{h['RUTA_ABSOLUTA']}` ({h['UTILIDAD_PROCESO']})" for h in hits) or "- No se detectaron fuentes locales explicitas distintas de instructivos, backups o scripts."
    return f"""# Diagnostico Estudiantes de Intercambio 2025

Fecha: {RUN_TS}

Estado: **{status}**

{hit_lines}

La ausencia de fuente local no confirma que no existan estudiantes de intercambio. Se requiere consulta institucional a Relaciones Internacionales/Docencia para cerrar el universo de intercambio 2025.
"""


def correction_report(universe: list[dict[str, Any]], base_rows: list[dict[str, Any]], comparison: list[dict[str, Any]], validation: list[dict[str, Any]], backup_dir: Path, precarga_status: str) -> str:
    counts = Counter(r["CLASIFICACION_UNIVERSO"] for r in universe)
    include_counts = Counter(r["INCLUIR_EN_PROCESO"] for r in universe)
    source_counts = Counter(r["FUENTE_INGRESO_UNIVERSO"] for r in universe)
    comp_counts = Counter(r["DECISION_CORREGIDA"] for r in comparison)
    val_counts = Counter(r["SEVERIDAD"] for r in validation)
    cov = coverage_rows(base_rows)
    cov_lines = "\n".join(f"| {r['VARIABLE']} | {r['TOTAL']} | {r['COMPLETOS']} | {r['PENDIENTES']} | {r['CONFLICTOS']} | {r['NO_APLICA']} | {r['COBERTURA']} | {r['ACCION']} |" for r in cov)
    return f"""# Reporte Correccion Universo Extranjeros Regulares 2025

Fecha: {RUN_TS}

## Resultado

- Precarga PES: {precarga_status}
- Universo reconstruido total auditado: {len(universe)}
- Base maestra corregida: {len(base_rows)}
- Inclusion: {dict(include_counts)}
- Por fuente: {dict(source_counts)}
- Por clasificacion: {dict(counts)}
- Comparacion de 30 anteriores: {dict(comp_counts)}
- Validacion: {dict(val_counts)}
- Respaldo previo: `{rel(backup_dir)}`

## Cobertura Base Corregida

| Variable | Total | Completos | Pendientes | Conflictos | No aplica | Cobertura | Accion |
|---|---:|---:|---:|---:|---:|---:|---|
{cov_lines}

## Decision

No generar CSV final PES hasta incorporar la precarga oficial o confirmar institucionalmente su ausencia, resolver nacionalidades pendientes, campos criticos y codigos unicos ambiguos.
"""


def manifest(paths: list[Path], backup_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for p in paths:
        if not p.exists():
            continue
        rows.append(
            {
                "RUTA_RELATIVA": rel(p),
                "NOMBRE": p.name,
                "TAMANO_BYTES": p.stat().st_size,
                "SHA256": sha256(p),
                "FECHA_GENERACION": RUN_TS,
                "OBSERVACION": "Correccion universo; no es CSV final PES",
            }
        )
    rows.append(
        {
            "RUTA_RELATIVA": rel(backup_dir),
            "NOMBRE": backup_dir.name,
            "TAMANO_BYTES": "",
            "SHA256": "",
            "FECHA_GENERACION": RUN_TS,
            "OBSERVACION": "Respaldos previos si existian salidas corregidas",
        }
    )
    return rows


def main() -> int:
    ensure_dirs()
    backup_dir = backup_existing(OUTPUTS)
    inventory = discover_sources()
    precarga_status = "PRECARGA_NO_ENCONTRADA"
    hierarchy = build_hierarchy(inventory)
    inputs = read_inputs()
    universe, _ = build_universe(inputs)
    base_rows, vig_rows, reuse_rows = build_base(universe, inputs)
    comparison = compare_previous(universe)
    validation = validate_universe(universe, base_rows, precarga_status)

    universe_fields = [
        "ID_CONTROL",
        "CODCLI",
        "TIPO_DOCUMENTO",
        "NUM_DOCUMENTO",
        "DV",
        "NOMBRE_COMPLETO",
        "NACIONALIDAD",
        "CODIGO_NACIONALIDAD",
        "FUENTE_INGRESO_UNIVERSO",
        "ARCHIVO_FUENTE",
        "HOJA",
        "FILA_ORIGEN",
        "EVIDENCIA_MATRICULA_2025",
        "TIPO_EVIDENCIA",
        "CLASIFICACION_UNIVERSO",
        "MOTIVO_CLASIFICACION",
        "INCLUIR_EN_PROCESO",
        "REQUIERE_CONFIRMACION",
        "OBSERVACION",
        "CODIGO_CARRERA_INTERNO",
        "PLAN_ESTUDIOS",
        "JORNADA_EVIDENCIA",
        "SEDE",
        "NOMBRE_CARRERA",
        "ANOMATRICULA_IDENTIDAD",
        "FILA_IDENTIDAD_DATOSALUMNOS",
    ]
    base_fields = [
        "ID_CONTROL",
        "CODCLI",
        "FUENTE_UNIVERSO",
        "ARCHIVO_ORIGEN_UNIVERSO",
        "HOJA_ORIGEN_UNIVERSO",
        "FILA_ORIGEN_UNIVERSO",
        "EVIDENCIA_2025",
        "ESTADO_EVIDENCIA",
        "DECISION_INCLUSION",
        "MOTIVO_DECISION",
        "CLASIFICACION_UNIVERSO",
        "REQUIERE_CONFIRMACION",
        "CODIGO_CARRERA_INTERNO",
        "PLAN_ESTUDIOS",
        "JORNADA_EVIDENCIA",
        "SEDE",
        "NOMBRE_CARRERA",
        "CLAVE_OFICIAL_PRELIMINAR",
        "CODIGO_UNICO_ESTADO_RESOLUCION",
        "CODIGO_UNICO_OBSERVACION",
    ]
    for field in OFFICIAL_FIELDS:
        base_fields.extend([field, f"FUENTE_DATO_{field}", f"DATO_BRUTO_{field}", f"DATO_NORMALIZADO_{field}", f"REGLA_{field}", f"ESTADO_CAMPO_{field}"])

    write_csv(AUD / "INVENTARIO_FUENTES_OFICIALES_2025.csv", inventory, ["RUTA_ABSOLUTA", "NOMBRE", "EXTENSION", "TAMANO_BYTES", "FECHA_MODIFICACION", "SHA256", "HOJAS", "ENCABEZADOS", "CANTIDAD_FILAS", "PERIODO_REPRESENTADO", "NIVEL_INFORMACION", "EVIDENCIA_ENTREGA_OFICIAL", "UTILIDAD_PROCESO", "PRIORIDAD_USO"])
    write_csv(AUD / "JERARQUIA_FUENTES_MATRICULA_2025.csv", hierarchy, ["PRIORIDAD", "FUENTE", "ARCHIVO", "ROL", "DECISION", "ESTADO"])
    write_csv(AUD / "UNIVERSO_RECONSTRUIDO_EXTRANJEROS_2025.csv", universe, universe_fields)
    write_csv(AUD / "COMPARACION_UNIVERSO_ANTERIOR_VS_CORREGIDO.csv", comparison, ["CODCLI", "NUM_DOCUMENTO", "NOMBRE_COMPLETO", "APARECE_PRECARGA_PES", "APARECE_MATRICULA_OFICIAL_2025", "APARECE_OTRA_FUENTE_MATRICULA_2025", "APARECE_SOLO_FUENTE_2026", "NO_ENCONTRADO", "NACIONALIDAD_CONFIRMADA", "EVIDENCIA_MATRICULA_EFECTIVA_2025", "DECISION_CORREGIDA", "CODIGO_UNICO_BASE_ANTERIOR", "OBSERVACION"])
    write_csv(INTERIM / "BASE_MAESTRA_EXTRANJEROS_REGULARES_2025_CORREGIDA.csv", base_rows, base_fields)
    write_csv(AUD / "AUDITORIA_VIGENCIA_2025_CORREGIDA.csv", vig_rows, ["ID_CONTROL", "CODCLI", "NUM_DOCUMENTO", "CODIGO_UNICO", "VIGENCIA_PROPUESTA", "EVIDENCIA_2025", "FUENTE_EVIDENCIA", "ESTADO_VALIDACION", "NO_USA_MATRICULA_2026", "REQUIERE_CONFIRMACION", "OBSERVACION"])
    write_csv(AUD / "AUDITORIA_REUTILIZACION_CAMPOS_CORREGIDA.csv", reuse_rows, ["CAMPO", "FUENTE", "PERIODO", "DEFINICION", "COMPATIBILIDAD_INSTRUCTIVO", "NIVEL_CONFIANZA", "REQUIERE_CONFIRMACION", "ESTADOS_CAMPO"])
    write_csv(AUD / "VALIDACION_UNIVERSO_CORREGIDO.csv", validation, ["ID_CONTROL", "CODCLI", "NUM_DOCUMENTO", "TIPO_HALLAZGO", "SEVERIDAD", "MENSAJE", "ACCION_REQUERIDA"])

    write_text(REP / "DIAGNOSTICO_PRECARGA_PES.md", report_precarga(precarga_status, inventory))
    write_text(REP / "IDENTIFICACION_MATRICULA_OFICIAL_2025.md", report_matricula(hierarchy, universe))
    write_text(REP / "DIAGNOSTICO_ESTUDIANTES_INTERCAMBIO_2025.md", report_intercambio(inventory))
    write_text(REP / "REPORTE_CORRECCION_UNIVERSO.md", correction_report(universe, base_rows, comparison, validation, backup_dir, precarga_status))
    create_management_workbook(GEST / "PLANILLA_GESTION_DOCENCIA_EXTRANJEROS_2025_CORREGIDA.xlsx", base_rows, validation, hierarchy)
    write_csv(AUD / "MANIFIESTO_ARCHIVOS_CORRECCION_UNIVERSO.csv", manifest(OUTPUTS, backup_dir), ["RUTA_RELATIVA", "NOMBRE", "TAMANO_BYTES", "SHA256", "FECHA_GENERACION", "OBSERVACION"])

    print(
        json.dumps(
            {
                "precarga": precarga_status,
                "universo": len(universe),
                "base_corregida": len(base_rows),
                "clasificacion": Counter(r["CLASIFICACION_UNIVERSO"] for r in universe),
                "inclusion": Counter(r["INCLUIR_EN_PROCESO"] for r in universe),
                "validacion": Counter(r["SEVERIDAD"] for r in validation),
                "backup": rel(backup_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
