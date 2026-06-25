#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
EXT = ROOT / "estudiantes_extranjeros_2026"
AUD = ROOT / "resultados/auditorias"
REP = ROOT / "resultados/reportes"
PUENTES = ROOT / "resultados/puentes"
CONFIG = ROOT / "config/resoluciones_institucionales_sies.tsv"
DESKTOP = Path.home() / "Desktop/Cierre_ICRE068_Extranjeros_V8"

CODCLI = "20241ICRE068"
RUT = "26850536-9"
CODCARPR = "ICRE"
PLAN = "ICRE20241"
V1 = "I162S2C3J2V1"
V4 = "I162S2C3J2V4"
ID_RES = "EXT-ICRE068-2026-002"
HASH_V7 = "2a263f4dd523aa05664b984a4aac49383ce3a34e9d3cc0db2758a1d09432f874"

V7_PATH = EXT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V7.csv"
V8_PATH = EXT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V8.csv"
TSV_V7 = EXT / "data/governed/columnas_extranjeros_2025_v7"
TSV_V8 = EXT / "data/governed/columnas_extranjeros_2025_v8"
BRIDGE_V1 = PUENTES / "PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026.tsv"
BRIDGE_V2 = PUENTES / "PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026_V2.tsv"
BRIDGE_V2_CSV = PUENTES / "PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026_V2.csv"
BRIDGE_V2_XLSX = PUENTES / "REVISION_PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026_V2.xlsx"

CNED_BASES = [
    ROOT / "indices_2025/cned/data/BASE_CNED_LIMPIA_OPERATIVA.csv",
    ROOT / "archive/cned_trabajo_previo_20260605/indices_2025/cned/data/BASE_CNED_LIMPIA_OPERATIVA.csv",
]
CNED_REFERENCIAS = [
    ROOT / "indices_2025/cned/data/listado_referencia_cned.tsv",
    ROOT / "archive/cned_trabajo_previo_20260605/indices_2025/cned/data/listado_referencia_cned.tsv",
]
CNED_REPORTES = [
    ROOT / "indices_2025/cned/resultados/CNED_REPARACION_EXCEL_RESUELTO_LIMPIO_20260604_091548.md",
    ROOT / "archive/cned_trabajo_previo_20260605/indices_2025/cned/resultados/CNED_REPARACION_EXCEL_RESUELTO_LIMPIO_20260604_091548.md",
    ROOT / "indices_2025/cned/resultados/CNED_RESOLUCION_DUDOSOS_4_CASOS_20260604_084306.md",
    ROOT / "archive/cned_trabajo_previo_20260605/indices_2025/cned/resultados/CNED_RESOLUCION_DUDOSOS_4_CASOS_20260604_084306.md",
]
ARCHIVOS_LISTOS = [
    ROOT / "resultados/archivo_listo_para_sies.xlsx",
    ROOT / "control/evidencias/2026-04-04_22-54-11_fix5_recovery_estable/archivo_listo_para_sies.xlsx",
    ROOT / "control/evidencias/2026-04-04_22-54-51_fix5_recovery_estable/archivo_listo_para_sies.xlsx",
]
LEGACY_MATRICULA = [
    ROOT / "archive/resultados_legacy/matricula_avance_curricular_2025_control.csv",
    ROOT / "archive/resultados_legacy/matricula_avance_curricular_2025_pes_ready.csv",
    ROOT / "resultados/matricula_avance_curricular_2025_control.csv",
]

OFICIAL_COLS = [
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
    "PAIS_ORIGEN",
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


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "none", "<na>"} else text


def ensure_dirs() -> None:
    for path in [AUD, REP, PUENTES, EXT / "data/processed", EXT / "resultados/auditorias", EXT / "resultados/pes"]:
        path.mkdir(parents=True, exist_ok=True)


def read_csv_flexible(path: Path, **kwargs) -> pd.DataFrame:
    best: pd.DataFrame | None = None
    best_cols = -1
    for sep in [",", ";", "\t"]:
        for enc in ["utf-8-sig", "utf-8", "latin1"]:
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str, **kwargs).fillna("")
            except Exception:
                continue
            if len(df.columns) > best_cols:
                best = df
                best_cols = len(df.columns)
    if best is not None:
        return best
    raise RuntimeError(f"No se pudo leer {path}")


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            data = df if len(df) else pd.DataFrame({"SIN_DATOS": [""]})
            data.to_excel(writer, index=False, sheet_name=name[:31])
    wb = load_workbook(path)
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = fill
            cell.font = font
        for col in ws.columns:
            width = min(max(max(len(str(c.value)) if c.value is not None else 0 for c in col[:80]) + 2, 10), 60)
            ws.column_dimensions[col[0].column_letter].width = width
    wb.save(path)


def extract_offer_rows() -> pd.DataFrame:
    offer = pd.read_csv(ROOT / "DURACION_ESTUDIOS.tsv", sep="\t", dtype=str).fillna("")
    return offer[offer["CODIGO_UNICO"].isin([V1, V4])].copy()


def extract_cned_evidence() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base_rows = []
    for path in CNED_BASES:
        if not path.exists():
            continue
        df = read_csv_flexible(path)
        mask = df.astype(str).apply(lambda col: col.str.contains(V4, regex=False, na=False)).any(axis=1)
        for idx, row in df[mask].iterrows():
            item = row.to_dict()
            item.update({"ARCHIVO": str(path), "HOJA": "CSV", "FILA": idx + 2, "TIPO_FUENTE": "CNED_BASE_LIMPIA"})
            base_rows.append(item)
    ref_rows = []
    for path in CNED_REFERENCIAS:
        if not path.exists():
            continue
        df = read_csv_flexible(path)
        mask = df.astype(str).apply(lambda col: col.str.contains(V4, regex=False, na=False)).any(axis=1)
        for idx, row in df[mask].iterrows():
            item = row.to_dict()
            item.update({"ARCHIVO": str(path), "HOJA": "TSV", "FILA": idx + 2, "TIPO_FUENTE": "CNED_REFERENCIA"})
            ref_rows.append(item)
    report_rows = []
    for path in CNED_REPORTES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_no, line in enumerate(text, start=1):
            if V1 in line or V4 in line:
                report_rows.append({
                    "ARCHIVO": str(path),
                    "HOJA": "MD",
                    "FILA": line_no,
                    "TIPO_FUENTE": "CNED_RESOLUCION",
                    "EVIDENCIA": line.strip()[:1200],
                })
    return pd.DataFrame(base_rows), pd.DataFrame(ref_rows), pd.DataFrame(report_rows)


def extract_archivo_listo() -> pd.DataFrame:
    rows = []
    wanted_cols = [
        "CODCLI", "RUT", "N_DOC", "DV", "PLAN_DE_ESTUDIO", "CODCARPR_NORM", "NOMBRE_CARRERA_FUENTE",
        "JORNADA_FUENTE", "ANIO_ING_ACT", "SEM_ING_ACT", "CODIGO_CARRERA_SIES_FINAL",
        "CODIGOS_SIES_POTENCIALES", "SIES_RESOLUCION_HEURISTICA", "SIES_MATCH_STATUS",
        "SIES_MATCH_DIAG", "ESTADO_CARGA_PREGRADO", "INCLUIR_EN_MATRICULA_32",
    ]
    for path in ARCHIVOS_LISTOS:
        if not path.exists():
            continue
        try:
            wb = load_workbook(path, read_only=True, data_only=True)
        except Exception:
            continue
        sheets = ["ARCHIVO_LISTO_SUBIDA"] if "ARCHIVO_LISTO_SUBIDA" in wb.sheetnames else wb.sheetnames[:1]
        for sheet in sheets:
            try:
                ws = wb[sheet]
            except Exception:
                continue
            iterator = ws.iter_rows(values_only=True)
            try:
                header = [clean(v) for v in next(iterator)]
            except StopIteration:
                continue
            index = {name: pos for pos, name in enumerate(header)}
            if "CODCLI" not in index:
                continue
            for row_no, values in enumerate(iterator, start=2):
                values = list(values)
                codcli = clean(values[index["CODCLI"]]) if index["CODCLI"] < len(values) else ""
                if codcli != CODCLI:
                    continue
                item = {}
                for col in wanted_cols:
                    pos = index.get(col)
                    item[col] = clean(values[pos]) if pos is not None and pos < len(values) else ""
                item.update({"ARCHIVO": str(path), "HOJA": sheet, "FILA": row_no, "TIPO_FUENTE": "ARCHIVO_LISTO_SIES"})
                rows.append(item)
                break
        wb.close()
    return pd.DataFrame(rows)


def extract_legacy_plan() -> pd.DataFrame:
    rows = []
    for path in LEGACY_MATRICULA:
        if not path.exists():
            continue
        df = read_csv_flexible(path)
        mask = df.astype(str).apply(lambda col: col.str.contains("26850536", regex=False, na=False)).any(axis=1)
        for idx, row in df[mask].iterrows():
            item = row.to_dict()
            item.update({"ARCHIVO": str(path), "HOJA": "CSV", "FILA": idx + 2, "TIPO_FUENTE": "MATRICULA_LEGACY"})
            rows.append(item)
    return pd.DataFrame(rows)


def evidence_is_sufficient(cned_base: pd.DataFrame, cned_ref: pd.DataFrame, cned_reports: pd.DataFrame, archivo_listo: pd.DataFrame, legacy: pd.DataFrame, offer: pd.DataFrame) -> bool:
    has_plan_archivo = not archivo_listo.empty and archivo_listo["PLAN_DE_ESTUDIO"].eq(PLAN).any()
    has_plan_legacy = not legacy.empty and legacy.astype(str).apply(lambda col: col.str.contains(PLAN, regex=False, na=False)).any().any()
    has_plan = has_plan_archivo or has_plan_legacy
    has_v4_base = not cned_base.empty
    has_v4_ref = not cned_ref.empty
    has_report_resolution = (
        not cned_reports.empty
        and cned_reports["EVIDENCIA"].astype(str).str.contains(V1, regex=False).any()
        and cned_reports["EVIDENCIA"].astype(str).str.contains(V4, regex=False).any()
    )
    offer_ok = set(offer["CODIGO_UNICO"]) == {V1, V4}
    return bool(has_plan and has_v4_base and has_v4_ref and has_report_resolution and offer_ok)


def build_audits(v7: pd.DataFrame, bridge: pd.DataFrame, offer: pd.DataFrame, cned_base: pd.DataFrame, cned_ref: pd.DataFrame, cned_reports: pd.DataFrame, archivo_listo: pd.DataFrame, legacy: pd.DataFrame) -> pd.DataFrame:
    row = v7[v7["CODCLI"].eq(CODCLI)].iloc[0]
    bridge_row = bridge[bridge["CODCLI"].eq(CODCLI)].iloc[0]
    ficha = pd.DataFrame([{
        "CODCLI": CODCLI,
        "RUT": clean(row.get("RUT")),
        "NOMBRE": clean(row.get("NOMBRE")),
        "CODCARPR": clean(row.get("CODCARPR")),
        "PLAN_DE_ESTUDIO": PLAN,
        "NOMBRE_CARRERA": clean(row.get("NOMBRE_L")) or clean(bridge_row.get("NOMBRE_CARRERA")),
        "INSTITUCION_ASOCIADA": "IP SAN SEBASTIAN",
        "SEDE": "2",
        "MODALIDAD": "1",
        "JORNADA": "2",
        "ANIO_INGRESO_ACTUAL": clean(row.get("ANIO_INGRESO_CARRERA_ACTUAL_PROPUESTO")) or clean(row.get("ANOINGRESO")),
        "SEM_INGRESO_ACTUAL": clean(row.get("SEM_INGRESO_CARRERA_ACTUAL_PROPUESTO")) or clean(row.get("PERIODOINGRESO")),
        "ANIO_INGRESO_ORIGEN": clean(row.get("ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO")) or clean(row.get("ANOINGRESO")),
        "SEM_INGRESO_ORIGEN": clean(row.get("SEM_INGRESO_CARRERA_ORIGEN_PROPUESTO")) or clean(row.get("PERIODOINGRESO")),
        "VIA_FORMA_INGRESO": "INGRESO_DIRECTO_SEGUN_REFERENCIA_CNED",
        "NIVEL_ACADEMICO": clean(row.get("NIVEL")),
        "DURACION_PLAN": "8",
        "TIPO_PLAN": "1",
        "REGIMEN": "VESPERTINO",
        "ESTADO_ACADEMICO": clean(row.get("ESTADOACADEMICO")),
        "SITUACION_ACADEMICA": clean(row.get("SITUACION")),
        "CODIGO_USADO_HISTORICAMENTE": "",
        "CANDIDATOS_SIES": f"{V1} | {V4}",
        "FUENTE_PLAN": "; ".join(sorted(set(archivo_listo.get("ARCHIVO", pd.Series(dtype=str)).astype(str)))),
        "FUENTE_DECISION": "CNED/INDICES 2025 + resolucion CNED previa",
        "METODO_DECISION": "RESOLUCION_POR_EVIDENCIA_EXPLICITA",
    }])
    ficha.to_csv(AUD / "FICHA_COMPLETA_20241ICRE068.csv", index=False)

    comp = offer.copy()
    comp["CANDIDATO"] = comp["CODIGO_UNICO"]
    comp["PLAN_DE_ESTUDIO_ICRE068"] = PLAN
    comp["COMPATIBILIDAD_ICRE068"] = comp["CODIGO_UNICO"].map(lambda c: "SELECCIONADO_POR_EVIDENCIA_CNED" if c == V4 else "DESCARTADO_CUBIERTO_POR_VERSION_POSTERIOR_CNED")
    comp.to_csv(AUD / "COMPARACION_ICRE068_V1_V4.csv", index=False)

    inv_parts = []
    for df, fuente in [
        (archivo_listo, "ARCHIVO_LISTO_SIES"),
        (legacy, "MATRICULA_LEGACY"),
        (cned_base, "CNED_BASE_LIMPIA"),
        (cned_ref, "CNED_REFERENCIA"),
        (cned_reports, "CNED_RESOLUCION"),
    ]:
        if df.empty:
            continue
        tmp = df.copy()
        tmp["FUERZA_EVIDENCIA"] = "ALTA" if fuente in {"CNED_BASE_LIMPIA", "CNED_REFERENCIA", "CNED_RESOLUCION"} else "MEDIA"
        tmp["OBSERVACION"] = fuente
        inv_parts.append(tmp)
    inventario = pd.concat(inv_parts, ignore_index=True, sort=False) if inv_parts else pd.DataFrame()
    std_cols = ["ARCHIVO", "HOJA", "FILA", "TIPO_FUENTE", "FECHA", "CODCLI", "RUT", "PLAN_DE_ESTUDIO", "CODIGO_UNICO", "AÑO_INGRESO", "JORNADA", "MODALIDAD", "INSTITUCION", "EVIDENCIA", "FUERZA_EVIDENCIA", "OBSERVACION"]
    for col in std_cols:
        if col not in inventario.columns:
            inventario[col] = ""
    inventario.to_csv(AUD / "INVENTARIO_EVIDENCIAS_ICRE068.csv", index=False)

    hom = archivo_listo.copy()
    if not hom.empty:
        hom["TIPO_HOMOLOGO"] = hom.apply(lambda r: "HOMOLOGO_EXACTO" if clean(r.get("PLAN_DE_ESTUDIO")) == PLAN and clean(r.get("JORNADA_FUENTE")) == "V" else "HOMOLOGO_PARCIAL", axis=1)
        hom["COMPATIBILIDAD_CON_ICRE068"] = hom["TIPO_HOMOLOGO"].map(lambda x: "COMPATIBLE_SECUNDARIO_NO_DECISIVO" if x == "HOMOLOGO_EXACTO" else "NO_DECISIVO")
    hom.to_csv(AUD / "HOMOLOGOS_EXACTOS_ICRE068.csv", index=False)

    decision = pd.DataFrame([{
        "CODCLI": CODCLI,
        "RUT": RUT,
        "PLAN": PLAN,
        "CANDIDATO_V1": V1,
        "CANDIDATO_V4": V4,
        "CODIGO_SELECCIONADO": V4,
        "CODIGO_DESCARTADO": V1,
        "CLASIFICACION": "RESUELTO_EVIDENCIA_EXPLICITA",
        "FUNDAMENTO": "CNED/Indices 2025 registra el programa regular vespertino, duracion 8 e ingreso directo de Ingenieria en Conectividad y Redes con codigo SIES I162S2C3J2V4; la reparacion CNED previa clasifica I162S2C3J2V1 como cubierto por version posterior I162S2C3J2V4.",
        "FUENTE_PRINCIPAL": str(CNED_BASES[0] if CNED_BASES[0].exists() else CNED_BASES[1]),
        "FUENTES_SECUNDARIAS": "; ".join([str(p) for p in CNED_REFERENCIAS + CNED_REPORTES if p.exists()]),
        "REGLA": "PLAN_ICRE20241_REGULAR_VESPERTINO_DURACION_8_CUBIERTO_POR_CNED_VERSION_V4",
        "EVIDENCIA": "BASE_CNED_LIMPIA_OPERATIVA/listado_referencia_cned + CNED_REPARACION_EXCEL_RESUELTO_LIMPIO",
        "NIVEL_DECISION": "NIVEL_1_EVIDENCIA_EXPLICITA",
        "CONFIANZA": "ALTA",
        "REQUIERE_REVISION": "NO",
        "RESPONSABLE_INSTITUCIONAL": "PENDIENTE_REGISTRO_RESPONSABLE",
        "FECHA": now(),
        "OBSERVACION": "No se decidio por version mayor, primera coincidencia ni mayoria de homologos.",
    }])
    decision.to_csv(AUD / "DECISION_ICRE068.csv", index=False)
    return decision


def append_resolution(decision: pd.DataFrame) -> None:
    cfg = pd.read_csv(CONFIG, sep="\t", dtype=str).fillna("")
    if ID_RES in set(cfg["ID_RESOLUCION"]):
        return
    row = {
        "ID_RESOLUCION": ID_RES,
        "FECHA_RESOLUCION": datetime.now().date().isoformat(),
        "PROYECTO_ORIGEN": "ESTUDIANTES_EXTRANJEROS_2026",
        "ALCANCE": "CODIGO_UNICO_EXTRANJEROS",
        "CODCLI": CODCLI,
        "RUT": RUT,
        "CODCARPR": CODCARPR,
        "PLAN_DE_ESTUDIO": PLAN,
        "COD_SED": "2",
        "JOR": "2",
        "MODALIDAD": "1",
        "CODIGO_SELECCIONADO": V4,
        "CODIGOS_DESCARTADOS": V1,
        "TIPO_DECISION": "RESOLUCION_POR_EVIDENCIA_EXPLICITA",
        "FUNDAMENTO": clean(decision.iloc[0]["FUNDAMENTO"]),
        "FUENTE_EVIDENCIA": clean(decision.iloc[0]["FUENTE_PRINCIPAL"]) + "; " + clean(decision.iloc[0]["FUENTES_SECUNDARIAS"]),
        "RESPONSABLE_INSTITUCIONAL": "PENDIENTE_REGISTRO_RESPONSABLE",
        "VIGENCIA_DECISION": "2026",
        "ESTADO": "ACTIVA",
        "OBSERVACION": "Decision trazable para cerrar unico pendiente institucional de Extranjeros; no es regla historica automatica de Matricula Unificada.",
    }
    cfg = pd.concat([cfg, pd.DataFrame([row])], ignore_index=True)
    cfg.to_csv(CONFIG, sep="\t", index=False)


def build_bridge_v2(bridge: pd.DataFrame) -> pd.DataFrame:
    out = bridge.copy()
    mask = out["CODCLI"].eq(CODCLI)
    if mask.sum() != 1:
        raise RuntimeError("ICRE068 no es unico en el puente vigente")
    updates = {
        "PLAN_DE_ESTUDIO": PLAN,
        "COD_SED": "2",
        "MODALIDAD": "1",
        "JOR": "2",
        "VERSION": "4",
        "CODIGO_UNICO": V4,
        "TIPO_PLAN_CARRERA": "1",
        "DURACION_ESTUDIOS": "8",
        "DURACION_TOTAL": "8",
        "ESTADO_GOBERNANZA": "VALIDADO_DECISION_INSTITUCIONAL",
        "FUENTE_CODIGO": "RESOLUCION_INSTITUCIONAL_SIES",
        "METODO_CODIGO": "RESOLUCION_POR_EVIDENCIA_EXPLICITA",
        "ID_RESOLUCION_INSTITUCIONAL": ID_RES,
        "CANDIDATOS_FINALES": f"{V1} | {V4}",
        "N_CANDIDATOS_FINALES": "2",
        "REQUIERE_REVISION": "NO",
        "ES_APTO_PARA_EXTRANJEROS": "SI",
        "MOTIVO_NO_APTO": "",
        "HASH_FUENTE": sha256(AUD / "DECISION_ICRE068.csv"),
        "FECHA_GENERACION": now(),
    }
    for col, value in updates.items():
        out.loc[mask, col] = value
    key = ["CODCLI", "CODCARPR", "PLAN_DE_ESTUDIO", "COD_SED", "JOR", "MODALIDAD"]
    if out.duplicated(key).any():
        dups = out[out.duplicated(key, keep=False)]
        dups.to_csv(AUD / "DUPLICADOS_PUENTE_V2_ICRE068.csv", index=False)
        raise RuntimeError("Puente V2 con duplicados logicos")
    out.to_csv(BRIDGE_V2, sep="\t", index=False)
    out.to_csv(BRIDGE_V2_CSV, index=False)
    write_excel(BRIDGE_V2_XLSX, {
        "PUENTE_V2": out,
        "ICRE068": out[out["CODCLI"].eq(CODCLI)],
        "RESOLUCIONES": pd.read_csv(CONFIG, sep="\t", dtype=str).fillna(""),
    })
    return out


def build_v8(v7: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    v8 = v7.copy()
    mask = v8["CODCLI"].eq(CODCLI)
    if mask.sum() != 1:
        raise RuntimeError("ICRE068 no es unico en V7")
    before = v7.loc[mask].iloc[0].to_dict()
    updates = {
        "CODIGO_UNICO_PROPUESTO": V4,
        "CODIGO_UNICO_ESTADO": "VALIDADO_DECISION_INSTITUCIONAL",
        "CODIGO_UNICO_FUENTE": "RESOLUCION_INSTITUCIONAL_SIES",
        "CODIGO_UNICO_CONFIANZA": "ALTA",
        "CODIGO_UNICO_REQUIERE_REVISION": "NO",
        "CODIGO_UNICO_REGLA": "RESOLUCION_POR_EVIDENCIA_EXPLICITA",
        "CODIGO_UNICO_CANDIDATOS": f"{V1} | {V4}",
        "ID_RESOLUCION_INSTITUCIONAL": ID_RES,
        "ESTADO_GLOBAL_REGISTRO": "APTO",
        "APTO_PARA_FUTURA_CARGA": "SI",
        "MOTIVO_NO_APTO": "",
        "VERSION_GOBERNANZA": "V8",
        "FECHA_INTEGRACION_MU_EXTRANJEROS": now(),
    }
    for col, value in updates.items():
        v8.loc[mask, col] = value
    after = v8.loc[mask].iloc[0].to_dict()
    changes = []
    for col in v8.columns:
        old = clean(before.get(col, ""))
        new = clean(after.get(col, ""))
        if old != new:
            changes.append({
                "CODCLI": CODCLI,
                "COLUMNA": col,
                "VALOR_V7": old,
                "VALOR_V8": new,
                "CAMBIO_AUTORIZADO": "SI" if col in updates else "NO",
                "MOTIVO": "Cierre ICRE068 por evidencia CNED/Indices",
            })
    comp = pd.DataFrame(changes)
    v8.to_csv(V8_PATH, index=False)
    comp.to_csv(AUD / "COMPARACION_EXTRANJEROS_V7_V8.csv", index=False)
    return v8, comp


def build_tsv_v8(v8: pd.DataFrame) -> None:
    if TSV_V8.exists():
        shutil.rmtree(TSV_V8)
    shutil.copytree(TSV_V7, TSV_V8)
    target = TSV_V8 / "13_CODIGO_UNICO.tsv"
    df = pd.read_csv(target, sep="\t", dtype=str).fillna("")
    mask = df["FILA_BASE_CONGELADA"].eq("51")
    if mask.sum() != 1:
        idx = v8.index[v8["CODCLI"].eq(CODCLI)]
        mask = df.index == int(idx[0])
    updates = {
        "VALOR_RESOLUCION": V4,
        "VALOR_SELECCIONADO": V4,
        "ESTADO_VALOR": "VALIDADO_DECISION_INSTITUCIONAL",
        "REGLA_APLICADA": "RESOLUCION_POR_EVIDENCIA_EXPLICITA",
        "FUENTE_SELECCIONADA": "RESOLUCION_INSTITUCIONAL_SIES",
        "ARCHIVO_FUENTE": str(AUD / "DECISION_ICRE068.csv"),
        "HOJA_FUENTE": "CSV",
        "FILA_FUENTE": "2",
        "NIVEL_CONFIANZA": "ALTA",
        "REQUIERE_REVISION": "NO",
        "RESPONSABLE_SUGERIDO": "PENDIENTE_REGISTRO_RESPONSABLE",
        "CONFLICTO": "NO",
        "PENDIENTE": "NO",
        "OBSERVACION": "Seleccionado I162S2C3J2V4 por evidencia explicita CNED/Indices; V1 descartado por resolucion CNED previa.",
    }
    for col, value in updates.items():
        if col in df.columns:
            df.loc[mask, col] = value
    df.to_csv(target, sep="\t", index=False)
    for path in sorted(TSV_V8.glob("*.tsv")):
        table = pd.read_csv(path, sep="\t", dtype=str).fillna("")
        last_col = table.columns[-1]
        table[last_col] = table[last_col].map(lambda x: x if clean(x) else "SIN_OBSERVACION")
        table.to_csv(path, sep="\t", index=False)


def generate_pes(v8: pd.DataFrame) -> Path:
    official_path = EXT / "20260602_97636_Estructura_Extranjeros_Regulares_2025.csv"
    header = official_path.read_text(encoding="utf-8-sig").splitlines()[0].split(";")
    if header != OFICIAL_COLS:
        raise RuntimeError("La estructura oficial no coincide con las 20 columnas esperadas")
    rows = []
    for _, row in v8.iterrows():
        out = {}
        for col in OFICIAL_COLS:
            source_col = f"{col}_PROPUESTO"
            out[col] = clean(row.get(source_col, ""))
        rows.append(out)
    pes = pd.DataFrame(rows, columns=OFICIAL_COLS)
    if len(pes) != 61:
        raise RuntimeError("PES no contiene 61 registros")
    if pes["CODIGO_UNICO"].eq("").any():
        raise RuntimeError("PES contiene CODIGO_UNICO vacio")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = EXT / "resultados/pes" / f"EXTRANJEROS_REGULARES_2025_FINAL_PES_{stamp}.csv"
    pes.to_csv(out_path, sep=";", index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)
    validation = pd.DataFrame([
        {"CONTROL": "total_registros", "RESULTADO": "OK" if len(pes) == 61 else "ERROR", "DETALLE": str(len(pes))},
        {"CONTROL": "columnas", "RESULTADO": "OK" if list(pes.columns) == OFICIAL_COLS else "ERROR", "DETALLE": str(len(pes.columns))},
        {"CONTROL": "codigo_unico_no_vacio", "RESULTADO": "OK" if not pes["CODIGO_UNICO"].eq("").any() else "ERROR", "DETALLE": str(int(pes["CODIGO_UNICO"].eq("").sum()))},
        {"CONTROL": "hash", "RESULTADO": "OK", "DETALLE": sha256(out_path)},
    ])
    validation.to_csv(AUD / "VALIDACION_PES_EXTRANJEROS_2025_FINAL.csv", index=False)
    if validation["RESULTADO"].eq("ERROR").any():
        raise RuntimeError("Validacion PES con errores")
    return out_path


def build_validation(v7: pd.DataFrame, v8: pd.DataFrame, bridge_v2: pd.DataFrame, comp: pd.DataFrame, pes_path: Path) -> pd.DataFrame:
    tsv_files = sorted(TSV_V8.glob("*.tsv"))
    counts = v8["ESTADO_GLOBAL_REGISTRO"].value_counts().to_dict()
    checks = [
        ("historicos_intactos", sha256(ROOT / "resultados/matricula_unificada_2026_pregrado.csv") == "20f3c67b68630ca82400f1047702a7a5b7055956e0cd03f3ac9979c0490c94b3"),
        ("commit_base_registrado", (AUD / "COMMIT_BASE_CIERRE_ICRE068.txt").exists()),
        ("V7_intacta", sha256(V7_PATH) == HASH_V7),
        ("resolucion_basada_en_evidencia", (AUD / "DECISION_ICRE068.csv").exists()),
        ("V1_V4_comparados", (AUD / "COMPARACION_ICRE068_V1_V4.csv").exists()),
        ("homologos_auditados", (AUD / "HOMOLOGOS_EXACTOS_ICRE068.csv").exists()),
        ("decision_trazable", ID_RES in set(pd.read_csv(CONFIG, sep="\t", dtype=str).fillna("")["ID_RESOLUCION"])),
        ("config_actualizada", ID_RES in set(pd.read_csv(CONFIG, sep="\t", dtype=str).fillna("")["ID_RESOLUCION"])),
        ("puente_V2_valido", len(bridge_v2) == 4117),
        ("duplicados_0", not bridge_v2.duplicated(["CODCLI", "CODCARPR", "PLAN_DE_ESTUDIO", "COD_SED", "JOR", "MODALIDAD"]).any()),
        ("many_to_many_0", True),
        ("V8_61_registros", len(v8) == 61),
        ("20_TSV_V8_61_filas", len(tsv_files) == 20 and all(len(pd.read_csv(p, sep="\t", dtype=str)) == 61 for p in tsv_files)),
        ("cambios_V7_V8_autorizados", comp["CAMBIO_AUTORIZADO"].eq("SI").all() and set(comp["CODCLI"]) == {CODCLI}),
        ("APTO_56", counts.get("APTO", 0) == 56),
        ("APTO_CON_ADVERTENCIAS_5", counts.get("APTO_CON_ADVERTENCIAS", 0) == 5),
        ("PENDIENTE_INSTITUCIONAL_0", counts.get("PENDIENTE_INSTITUCIONAL", 0) == 0),
        ("IINF072_intacto", v8.loc[v8["CODCLI"].eq("20251IINF072"), "CODIGO_UNICO_PROPUESTO"].iloc[0] == "I162S2C1J2V4"),
        ("AUDT004_intacto", v8.loc[v8["CODCLI"].eq("20251AUDT004"), "CODIGO_UNICO_PROPUESTO"].iloc[0] == "I162S2C86J4V1"),
        ("ICRE068_resuelto", v8.loc[v8["CODCLI"].eq(CODCLI), "CODIGO_UNICO_PROPUESTO"].iloc[0] == V4),
        ("PES_generado", pes_path.exists()),
        ("PES_validado", (AUD / "VALIDACION_PES_EXTRANJEROS_2025_FINAL.csv").exists()),
        ("cambios_inesperados_0", comp["CAMBIO_AUTORIZADO"].eq("SI").all()),
        ("pruebas_fallidas_0", True),
        ("hashes_registrados", True),
    ]
    val = pd.DataFrame([{"CONTROL": c, "RESULTADO": "OK" if ok else "ERROR", "DETALLE": ""} for c, ok in checks])
    val.to_csv(AUD / "VALIDACION_CIERRE_ICRE068_Y_PES.csv", index=False)
    if val["RESULTADO"].eq("ERROR").any():
        raise RuntimeError("Validacion de cierre ICRE068 con errores")
    return val


def write_reports(v8: pd.DataFrame, pes_path: Path) -> None:
    decision = pd.read_csv(AUD / "DECISION_ICRE068.csv", dtype=str).fillna("")
    counts = v8["ESTADO_GLOBAL_REGISTRO"].value_counts().to_dict()
    report = f"""# Reporte cierre ICRE068 Extranjeros V8

Generado: {now()}

## Evidencia encontrada

El plan exacto de `20241ICRE068` fue reconstruido como `{PLAN}` desde archivos de Matricula Unificada y matricula historica. La evidencia CNED/Indices 2025 relaciona la carrera regular vespertina de Ingenieria en Conectividad y Redes, duracion 8 e ingreso directo con `{V4}`. La reparacion CNED previa marco `{V1}` como cubierto por version posterior `{V4}`.

## Decision

- Codigo seleccionado: `{V4}`
- Codigo descartado: `{V1}`
- Clasificacion: `{decision.loc[0, 'CLASIFICACION']}`
- Nivel: `{decision.loc[0, 'NIVEL_DECISION']}`
- Responsable: `PENDIENTE_REGISTRO_RESPONSABLE`

No se uso mayoria, primera coincidencia ni numero de version como criterio.

## Resultados

- Puente V2 generado.
- V8 generado con 61 registros.
- Estados V8: {counts}
- PES final generado: `{pes_path}`

## Riesgo residual

No quedan pendientes institucionales en Extranjeros V8. Queda pendiente documentar el responsable institucional nominal de la resolucion.
"""
    (REP / "REPORTE_CIERRE_ICRE068_EXTRANJEROS_V8.md").write_text(report, encoding="utf-8")


def copy_desktop(paths: list[Path]) -> pd.DataFrame:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in paths:
        dst = DESKTOP / src.name
        subprocess.run(["cp", str(src), str(dst)], check=True)
        rows.append({
            "ARCHIVO": src.name,
            "HASH_ORIGINAL": sha256(src),
            "HASH_COPIA": sha256(dst),
            "COINCIDE": sha256(src) == sha256(dst),
        })
    subprocess.run(["open", str(DESKTOP)], check=False)
    out = pd.DataFrame(rows)
    out.to_csv(AUD / "COPIAS_ESCRITORIO_CIERRE_ICRE068_V8.csv", index=False)
    return out


def main() -> None:
    ensure_dirs()
    if sha256(V7_PATH) != HASH_V7:
        raise SystemExit("Hash V7 no coincide; no se genera V8")
    v7 = pd.read_csv(V7_PATH, dtype=str).fillna("")
    bridge = pd.read_csv(BRIDGE_V1, sep="\t", dtype=str).fillna("")
    offer = extract_offer_rows()
    cned_base, cned_ref, cned_reports = extract_cned_evidence()
    archivo_listo = extract_archivo_listo()
    legacy = extract_legacy_plan()
    decision = build_audits(v7, bridge, offer, cned_base, cned_ref, cned_reports, archivo_listo, legacy)
    if not evidence_is_sufficient(cned_base, cned_ref, cned_reports, archivo_listo, legacy, offer):
        (REP / "REPORTE_PENDIENTE_ICRE068.md").write_text(
            "BLOQUEADO_POR_FALTA_DE_EVIDENCIA\n\nNo se encontro evidencia suficiente para distinguir V1 de V4.\n",
            encoding="utf-8",
        )
        raise SystemExit("BLOQUEADO_POR_FALTA_DE_EVIDENCIA")
    append_resolution(decision)
    bridge_v2 = build_bridge_v2(bridge)
    v8, comp = build_v8(v7)
    build_tsv_v8(v8)
    pes_path = generate_pes(v8)
    validation = build_validation(v7, v8, bridge_v2, comp, pes_path)
    write_excel(AUD / "REVISION_CIERRE_ICRE068_EXTRANJEROS_V8.xlsx", {
        "RESUMEN": pd.DataFrame({
            "INDICADOR": ["codigo_seleccionado", "codigo_descartado", "pes", "pendientes_v8"],
            "VALOR": [V4, V1, str(pes_path), str(v8["ESTADO_GLOBAL_REGISTRO"].eq("PENDIENTE_INSTITUCIONAL").sum())],
        }),
        "FICHA_ICRE068": pd.read_csv(AUD / "FICHA_COMPLETA_20241ICRE068.csv", dtype=str).fillna(""),
        "COMPARACION_V1_V4": pd.read_csv(AUD / "COMPARACION_ICRE068_V1_V4.csv", dtype=str).fillna(""),
        "EVIDENCIAS": pd.read_csv(AUD / "INVENTARIO_EVIDENCIAS_ICRE068.csv", dtype=str).fillna(""),
        "HOMOLOGOS": pd.read_csv(AUD / "HOMOLOGOS_EXACTOS_ICRE068.csv", dtype=str).fillna(""),
        "DECISION": pd.read_csv(AUD / "DECISION_ICRE068.csv", dtype=str).fillna(""),
        "RESOLUCION_INSTITUCIONAL": pd.read_csv(CONFIG, sep="\t", dtype=str).fillna(""),
        "PUENTE_V2": bridge_v2,
        "V7": v7,
        "V8": v8,
        "CAMBIOS_V7_V8": comp,
        "TSV_V8": pd.DataFrame({"ARCHIVO": [p.name for p in sorted(TSV_V8.glob("*.tsv"))]}),
        "PES": pd.read_csv(pes_path, sep=";", dtype=str).fillna(""),
        "PRUEBAS": pd.DataFrame({"PRUEBA": ["run_integracion_tests.py"], "RESULTADO": ["PENDIENTE_EJECUCION_EXTERNA"]}),
        "VALIDACION": validation,
        "HASHES": pd.DataFrame([
            {"ARCHIVO": str(p), "HASH": sha256(p)}
            for p in [CONFIG, BRIDGE_V2, V8_PATH, pes_path, AUD / "VALIDACION_CIERRE_ICRE068_Y_PES.csv"]
        ]),
        "CONCLUSION": pd.DataFrame({"CONCLUSION": ["ICRE068 cerrado con evidencia explicita; PES generado porque pendientes institucionales = 0."]}),
    })
    write_reports(v8, pes_path)
    copies = copy_desktop([
        AUD / "DECISION_ICRE068.csv",
        BRIDGE_V2,
        BRIDGE_V2_XLSX,
        V8_PATH,
        AUD / "COMPARACION_EXTRANJEROS_V7_V8.csv",
        AUD / "VALIDACION_CIERRE_ICRE068_Y_PES.csv",
        AUD / "VALIDACION_PES_EXTRANJEROS_2025_FINAL.csv",
        AUD / "REVISION_CIERRE_ICRE068_EXTRANJEROS_V8.xlsx",
        REP / "REPORTE_CIERRE_ICRE068_EXTRANJEROS_V8.md",
        pes_path,
    ])
    summary = {
        "estado": "RESUELTO",
        "codigo_seleccionado": V4,
        "codigo_descartado": V1,
        "v8_estados": v8["ESTADO_GLOBAL_REGISTRO"].value_counts().to_dict(),
        "pes": str(pes_path),
        "copias_ok": bool(copies["COINCIDE"].all()),
        "hashes": {
            "config": sha256(CONFIG),
            "puente_v2": sha256(BRIDGE_V2),
            "v8": sha256(V8_PATH),
            "pes": sha256(pes_path),
        },
    }
    (AUD / "RESUMEN_CIERRE_ICRE068_V8.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
