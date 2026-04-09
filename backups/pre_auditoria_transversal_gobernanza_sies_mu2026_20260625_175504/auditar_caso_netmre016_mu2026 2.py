from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
AUD = ROOT / "resultados" / "auditorias"
REP = ROOT / "resultados" / "reportes"
DESKTOP = Path.home() / "Desktop" / "Revision_Caso_NETMRE016_MU2026"

CODCLI = "20171NETMRE016"
RUT_NUM = "16935626"
RUT_DV = "2"
PLAN = "NETMRE20121"
CODCARPR = "NETMRE"
V1 = "I162S2C3J4V1"
V2 = "I162S2C3J4V2"
V3 = "I162S2C3J4V3"

MU_COLS = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE", "SEXO", "FECH_NAC",
    "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION", "FOR_ING_ACT",
    "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",
    "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL",
    "SUS_PRE", "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]

TARGETS = {
    "apariciones": AUD / "INVENTARIO_APARICIONES_20171NETMRE016.csv",
    "archivo_real": AUD / "IDENTIFICACION_ARCHIVO_REAL_CARGA_MU2026.csv",
    "fila": AUD / "FILA_REAL_CARGADA_20171NETMRE016.csv",
    "oferta": AUD / "COMPARACION_V1_V2_NETMRE.csv",
    "plan": AUD / "PLAN_NETMRE20121_Y_HOMOLOGOS.csv",
    "post": AUD / "ESTADO_POST_CARGA_20171NETMRE016.csv",
    "impacto": AUD / "IMPACTO_FINAL_20171NETMRE016.csv",
    "excel": AUD / "REVISION_CASO_NETMRE016_MU2026.xlsx",
    "reporte": REP / "REPORTE_CASO_CRITICO_NETMRE016_MU2026.md",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if re.fullmatch(r"\d+\.0", text):
        return text[:-2]
    return text


def up(value: object) -> str:
    return clean(value).upper()


def backup_existing() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / "backups" / f"pre_auditoria_caso_netmre016_mu2026_{ts}"
    backup.mkdir(parents=True, exist_ok=True)
    for path in TARGETS.values():
        if path.exists():
            shutil.copy2(path, backup / path.name)
    return backup


def file_meta(path: Path) -> dict[str, object]:
    return {
        "fecha": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "tamaño": path.stat().st_size,
        "hash": sha256(path),
    }


def read_stage() -> pd.DataFrame:
    df = pd.read_excel(ROOT / "resultados" / "archivo_listo_para_sies.xlsx", sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str).fillna("")
    df["_FILA_EXCEL"] = [i + 2 for i in range(len(df))]
    return df


def read_mu32() -> pd.DataFrame:
    df = pd.read_excel(ROOT / "resultados" / "archivo_listo_para_sies.xlsx", sheet_name="MATRICULA_UNIFICADA_32", dtype=str).fillna("")
    df["_FILA_EXCEL"] = [i + 2 for i in range(len(df))]
    return df


def read_final_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", header=None, names=MU_COLS, dtype=str, keep_default_na=False)
    df["_FILA_CSV"] = [i + 1 for i in range(len(df))]
    return df.fillna("")


def read_control_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=",", dtype=str, keep_default_na=False).fillna("")


def candidate_files() -> list[Path]:
    paths = [
        ROOT / "resultados" / "matricula_unificada_2026_pregrado.csv",
        ROOT / "control" / "punto_0_carga_principal_mu2026" / "archivos_congelados" / "BRUTO_REPO__matricula_unificada_2026_pregrado.csv",
        ROOT / "control" / "auditoria_mu2026_punto0_complemento95" / "archivos_congelados" / "carga_principal" / "matricula_unificada_2026_pregrado.csv",
        ROOT / "resultados" / "matricula_unificada_2026_control.csv",
        ROOT / "resultados" / "matricula_unificada_2026_oficial.xlsx",
        ROOT / "resultados" / "archivo_listo_para_sies.xlsx",
        ROOT / "resultados" / "matricula_unificada_2026_pregrado_PES_READY.csv",
    ]
    return [p for p in paths if p.exists()]


def row_from_any(path: Path) -> tuple[pd.DataFrame, str, str]:
    if path.name == "matricula_unificada_2026_control.csv":
        df = read_control_csv(path)
        row = df[(df["N_DOC"].astype(str).eq(RUT_NUM)) & (df["DV"].astype(str).str.upper().eq(RUT_DV))]
        return row, "CSV_CONTROL_CON_HEADER", ""
    if path.suffix.lower() == ".csv":
        sep = ";" if "pregrado" in path.name.lower() or "pes_ready" in path.name.lower() else ","
        if sep == ";":
            df = read_final_csv(path)
        else:
            df = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False).fillna("")
        row = df[(df.get("N_DOC", "").astype(str).eq(RUT_NUM)) & (df.get("DV", "").astype(str).str.upper().eq(RUT_DV))]
        return row, "CSV", ""
    if path.name == "archivo_listo_para_sies.xlsx":
        rows = []
        sheets = []
        for sheet in ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32", "SIES_AMBIGUOS_POR_RESOL"]:
            try:
                df = pd.read_excel(path, sheet_name=sheet, dtype=str).fillna("")
                df["_FILA_EXCEL"] = [i + 2 for i in range(len(df))]
                row = df[(df.get("CODCLI", "").astype(str).eq(CODCLI)) | ((df.get("N_DOC", "").astype(str).eq(RUT_NUM)) & (df.get("DV", "").astype(str).str.upper().eq(RUT_DV)))]
                if not row.empty:
                    row = row.copy()
                    row["_HOJA"] = sheet
                    rows.append(row)
                    sheets.append(sheet)
            except Exception:
                pass
        return (pd.concat(rows, ignore_index=True, sort=False) if rows else pd.DataFrame()), "XLSX", " | ".join(sheets)
    if path.suffix.lower() == ".xlsx":
        rows = []
        sheets = []
        try:
            xl = pd.ExcelFile(path)
            for sheet in xl.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet, dtype=str).fillna("")
                df["_FILA_EXCEL"] = [i + 2 for i in range(len(df))]
                row = df[(df.get("N_DOC", "").astype(str).eq(RUT_NUM)) & (df.get("DV", "").astype(str).str.upper().eq(RUT_DV))]
                if not row.empty:
                    row = row.copy()
                    row["_HOJA"] = sheet
                    rows.append(row)
                    sheets.append(sheet)
        except Exception:
            pass
        return (pd.concat(rows, ignore_index=True, sort=False) if rows else pd.DataFrame()), "XLSX", " | ".join(sheets)
    return pd.DataFrame(), "OTRO", ""


def build_inventory(stage: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    # Structured priority files.
    for path in candidate_files():
        found, tipo, sheets = row_from_any(path)
        meta = file_meta(path)
        if found.empty:
            rows.append(base_inventory_row(path, "", "", tipo, "", meta, "SIN_FILA_CASO"))
            continue
        for _, r in found.iterrows():
            rows.append(inventory_from_row(path, clean(r.get("_HOJA", sheets)), r, tipo, meta))
    # Text hits from rg.
    try:
        proc = subprocess.run(
            [
                "rg", "-n", f"{CODCLI}|{PLAN}|{CODCARPR}",
                str(ROOT),
                "--glob", "!**/.git/**",
                "--glob", "!**/.venv/**",
                "--glob", "!**/__pycache__/**",
                "--glob", "!**/backups/**",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in proc.stdout.splitlines():
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue
            p = Path(parts[0])
            try:
                rel = str(p.relative_to(ROOT))
            except Exception:
                rel = str(p)
            rows.append(
                {
                    "ARCHIVO": rel,
                    "HOJA": "",
                    "FILA": parts[1],
                    "TIPO_FUENTE": "TEXTO_RG",
                    "ES_PRODUCTIVO": "NO",
                    "ES_ARCHIVO_CARGADO": "NO",
                    "CODCLI": CODCLI if CODCLI in parts[2] else "",
                    "RUT": "",
                    "NOMBRE": "",
                    "CODCARPR": CODCARPR if CODCARPR in parts[2] else "",
                    "PLAN_DE_ESTUDIO": PLAN if PLAN in parts[2] else "",
                    "COD_SED": "",
                    "COD_CAR": "",
                    "MODALIDAD": "",
                    "JOR": "",
                    "VERSION": "",
                    "VIG": "",
                    "CODIGO_CARRERA_SIES_FINAL": "",
                    "ESTADO_CARGA": "",
                    "OBSERVACION": parts[2][:300],
                }
            )
    except Exception:
        pass
    return pd.DataFrame(rows)


def base_inventory_row(path: Path, hoja: str, fila: str, tipo: str, codcli: str, meta: dict[str, object], obs: str) -> dict[str, object]:
    return {
        "ARCHIVO": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "HOJA": hoja,
        "FILA": fila,
        "TIPO_FUENTE": tipo,
        "ES_PRODUCTIVO": "SI" if "resultados/matricula_unificada_2026_pregrado.csv" in str(path) else "NO",
        "ES_ARCHIVO_CARGADO": "SI" if path.name == "matricula_unificada_2026_pregrado.csv" and "resultados" in path.parts else "NO",
        "CODCLI": codcli,
        "RUT": "",
        "NOMBRE": "",
        "CODCARPR": "",
        "PLAN_DE_ESTUDIO": "",
        "COD_SED": "",
        "COD_CAR": "",
        "MODALIDAD": "",
        "JOR": "",
        "VERSION": "",
        "VIG": "",
        "CODIGO_CARRERA_SIES_FINAL": "",
        "ESTADO_CARGA": "",
        "OBSERVACION": obs,
    }


def inventory_from_row(path: Path, hoja: str, r: pd.Series, tipo: str, meta: dict[str, object]) -> dict[str, object]:
    fila = clean(r.get("_FILA_CSV")) or clean(r.get("_FILA_EXCEL"))
    return {
        "ARCHIVO": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "HOJA": hoja,
        "FILA": fila,
        "TIPO_FUENTE": tipo,
        "ES_PRODUCTIVO": "SI" if path == ROOT / "resultados" / "matricula_unificada_2026_pregrado.csv" else "NO",
        "ES_ARCHIVO_CARGADO": "SI" if path == ROOT / "resultados" / "matricula_unificada_2026_pregrado.csv" else "NO",
        "CODCLI": clean(r.get("CODCLI")),
        "RUT": f"{clean(r.get('N_DOC'))}-{clean(r.get('DV'))}",
        "NOMBRE": clean(r.get("NOMBRE")),
        "CODCARPR": clean(r.get("CODCARPR_NORM")) or clean(r.get("CODCARPR")),
        "PLAN_DE_ESTUDIO": clean(r.get("PLAN_DE_ESTUDIO")),
        "COD_SED": clean(r.get("COD_SED")),
        "COD_CAR": clean(r.get("COD_CAR")),
        "MODALIDAD": clean(r.get("MODALIDAD")),
        "JOR": clean(r.get("JOR")),
        "VERSION": clean(r.get("VERSION")),
        "VIG": clean(r.get("VIG")),
        "CODIGO_CARRERA_SIES_FINAL": clean(r.get("CODIGO_CARRERA_SIES_FINAL")),
        "ESTADO_CARGA": clean(r.get("ESTADO_CARGA_PREGRADO")) or clean(r.get("INCLUIR_EN_MATRICULA_32")),
        "OBSERVACION": f"fecha={meta['fecha']}; hash={meta['hash']}",
    }


def build_real_file_identification() -> pd.DataFrame:
    rows = []
    evidence = {
        "resultados/matricula_unificada_2026_pregrado.csv": "README y DOCUMENTACION_TECNICA lo declaran CSV regulatorio final; control/punto_0 lo congela como carga principal.",
        "resultados/archivo_listo_para_sies.xlsx": "Workbook de auditoría/trazabilidad; contiene hoja MATRICULA_UNIFICADA_32 y ARCHIVO_LISTO_SUBIDA.",
        "resultados/matricula_unificada_2026_oficial.xlsx": "Copia Excel con 32 columnas y encabezados; no es CSV sin header.",
        "resultados/matricula_unificada_2026_control.csv": "Control con encabezados; no es archivo CSV regulatorio sin header.",
    }
    for path in candidate_files():
        meta = file_meta(path)
        total = ""
        try:
            if path.name == "matricula_unificada_2026_pregrado.csv":
                total = len(read_final_csv(path))
            elif path.name == "matricula_unificada_2026_control.csv":
                total = len(read_control_csv(path))
            elif path.suffix.lower() == ".xlsx":
                if path.name == "archivo_listo_para_sies.xlsx":
                    total = len(read_mu32())
                else:
                    total = len(pd.read_excel(path, dtype=str))
            elif path.suffix.lower() == ".csv":
                total = sum(1 for _ in path.open("r", encoding="utf-8", errors="replace"))
        except Exception:
            total = ""
        rel = str(path.relative_to(ROOT))
        is_final = rel == "resultados/matricula_unificada_2026_pregrado.csv"
        rows.append(
            {
                "archivo_candidato": rel,
                "fecha": meta["fecha"],
                "tamaño": meta["tamaño"],
                "hash": meta["hash"],
                "total_filas": total,
                "evidencia_de_carga": evidence.get(rel, ""),
                "estado": "ARCHIVO_REAL_CARGADO" if is_final else "SOPORTE_AUDITORIA_O_COPIA",
                "prioridad": 1 if is_final else 2,
                "conclusión": "Archivo final exacto cargado/regulatorio vigente." if is_final else "No se asume como carga principal.",
            }
        )
    return pd.DataFrame(rows).sort_values(["prioridad", "archivo_candidato"])


def reconstruct_code(row: pd.Series) -> tuple[str, str, str]:
    cod_sed = clean(row.get("COD_SED"))
    cod_car = clean(row.get("COD_CAR"))
    jor = clean(row.get("JOR"))
    version = clean(row.get("VERSION"))
    if not version:
        return "", "VERSION_VACIA", "VERSION vacía; no permite reconstruir código SIES."
    if version not in {"1", "2", "3", "4", "5"}:
        return "", "VERSION_INVALIDA", f"VERSION={version} no válida para reconstrucción controlada."
    if not all([cod_sed, cod_car, jor]):
        return "", "COMPONENTES_INCOMPLETOS", "Faltan COD_SED, COD_CAR o JOR."
    code = f"I162S{cod_sed}C{cod_car}J{jor}V{version}"
    if code == V1:
        return code, "RECONSTRUIDO_V1", "El código reconstruido coincide con candidato V1."
    if code == V2:
        return code, "RECONSTRUIDO_V2", "El código reconstruido coincide con candidato V2."
    return code, "CODIGO_NO_ES_CANDIDATO_NETMRE", "El código reconstruido no coincide con V1/V2 del caso."


def build_final_row() -> pd.DataFrame:
    path = ROOT / "resultados" / "matricula_unificada_2026_pregrado.csv"
    df = read_final_csv(path)
    row = df[(df["N_DOC"].eq(RUT_NUM)) & (df["DV"].str.upper().eq(RUT_DV))].copy()
    meta = file_meta(path)
    if row.empty:
        return pd.DataFrame()
    code, state, obs = reconstruct_code(row.iloc[0])
    row["ARCHIVO_ORIGEN"] = str(path.relative_to(ROOT))
    row["HOJA"] = "CSV_SIN_ENCABEZADO"
    row["FILA_EXCEL"] = row["_FILA_CSV"]
    row["HASH_ARCHIVO"] = meta["hash"]
    row["FECHA_ARCHIVO"] = meta["fecha"]
    row["CODIGO_SIES_RECONSTRUIDO"] = code
    row["ESTADO_RECONSTRUCCION"] = state
    row["OBSERVACION"] = obs
    return row.drop(columns=["_FILA_CSV"])


def build_offer_comparison() -> pd.DataFrame:
    offer = pd.read_csv(ROOT / "DURACION_ESTUDIOS.tsv", sep="\t", dtype=str, keep_default_na=False).fillna("")
    rows = offer[offer["CODIGO_UNICO"].isin([V1, V2, V3])].copy()
    return rows[
        [
            "CODIGO_UNICO", "NOMBRE_IES", "NOMBRE_CARRERA", "MODALIDAD", "JORNADA",
            "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL", "VIGENCIA",
            "CODCARPR_CANONICO", "CODCARPR_ALIAS_LIST", "FUENTE_GOBERNANZA", "ESTADO_REGISTRO",
        ]
    ]


def build_plan_homologs(stage: pd.DataFrame) -> pd.DataFrame:
    mask = (
        stage["PLAN_DE_ESTUDIO"].astype(str).eq(PLAN)
        | stage["CODCARPR_NORM"].astype(str).eq(CODCARPR)
        | stage["CODCLI"].astype(str).eq(CODCLI)
    )
    cols = [
        "CODCLI", "N_DOC", "DV", "PLAN_DE_ESTUDIO", "CODCARPR_NORM", "NOMBRE_CARRERA_FUENTE",
        "ANIO_ING_ACT", "JORNADA_FUENTE", "MODALIDAD", "DURACION_ESTUDIOS_REF", "SIES_RESOLUCION_HEURISTICA",
        "CODIGO_CARRERA_SIES_FINAL", "VERSION", "INCLUIR_EN_MATRICULA_32", "ESTADO_CARGA_PREGRADO", "_FILA_EXCEL",
    ]
    out = stage.loc[mask, [c for c in cols if c in stage.columns]].copy()
    out["RUT"] = out["N_DOC"].astype(str) + "-" + out["DV"].astype(str)
    out["FUENTE"] = "resultados/archivo_listo_para_sies.xlsx!ARCHIVO_LISTO_SUBIDA"
    out["ESTADO"] = out["ESTADO_CARGA_PREGRADO"].astype(str) + " / INCLUIR=" + out["INCLUIR_EN_MATRICULA_32"].astype(str)
    rename = {
        "CODCARPR_NORM": "CODCARPR",
        "NOMBRE_CARRERA_FUENTE": "NOMBRE_CARRERA",
        "ANIO_ING_ACT": "AÑO_INGRESO",
        "JORNADA_FUENTE": "JORNADA",
        "DURACION_ESTUDIOS_REF": "DURACION_PLAN",
        "SIES_RESOLUCION_HEURISTICA": "TIPO_PLAN",
        "CODIGO_CARRERA_SIES_FINAL": "CODIGO_SIES_FINAL",
    }
    out = out.rename(columns=rename)
    order = [
        "CODCLI", "RUT", "PLAN_DE_ESTUDIO", "CODCARPR", "NOMBRE_CARRERA", "AÑO_INGRESO",
        "JORNADA", "MODALIDAD", "DURACION_PLAN", "TIPO_PLAN", "CODIGO_SIES_FINAL", "VERSION", "FUENTE", "ESTADO", "_FILA_EXCEL",
    ]
    return out[[c for c in order if c in out.columns]]


def build_post_load(final_row: pd.DataFrame, stage_row: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for path in [
        ROOT / "control" / "gate" / "gate_final_mu_2026.md",
        ROOT / "control" / "auditoria_ayz" / "resumen_ayz.json",
        ROOT / "control" / "auditoria_ayz" / "reporte_cierre_ayz.md",
        ROOT / "resultados" / "reporte_validacion.json",
        ROOT / "resultados" / "resumen_verificacion_exclusiones_pes_ready_20260508_230900.md",
        ROOT / "control" / "reportes" / "sies_pendientes.tsv",
    ]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        mention = CODCLI in text or RUT_NUM in text or "matricula_unificada_2026_pregrado.csv" in text
        rows.append(
            {
                "ARCHIVO": str(path.relative_to(ROOT)),
                "TIPO_EVIDENCIA": "VALIDADOR_O_COMPROBANTE",
                "MENCIONA_CASO": "SI" if (CODCLI in text or RUT_NUM in text) else "NO",
                "MENCIONA_ARCHIVO_FINAL": "SI" if "matricula_unificada_2026_pregrado.csv" in text else "NO",
                "ESTADO": infer_post_status(path, text),
                "OBSERVACION": extract_context(text),
            }
        )
    if not final_row.empty:
        rows.append({"ARCHIVO": "resultados/matricula_unificada_2026_pregrado.csv", "TIPO_EVIDENCIA": "FILA_FINAL", "MENCIONA_CASO": "SI", "MENCIONA_ARCHIVO_FINAL": "SI", "ESTADO": "INCLUIDA_EN_ARCHIVO_CARGADO", "OBSERVACION": "Fila encontrada por RUT 16935626-2."})
    if not stage_row.empty:
        rows.append({"ARCHIVO": "resultados/archivo_listo_para_sies.xlsx!ARCHIVO_LISTO_SUBIDA", "TIPO_EVIDENCIA": "STAGING_TRAZABILIDAD", "MENCIONA_CASO": "SI", "MENCIONA_ARCHIVO_FINAL": "NO", "ESTADO": clean(stage_row.iloc[0].get("ESTADO_CARGA_PREGRADO")), "OBSERVACION": clean(stage_row.iloc[0].get("SIES_RESOLUCION_HEURISTICA"))})
    return pd.DataFrame(rows)


def infer_post_status(path: Path, text: str) -> str:
    if path.name == "sies_pendientes.tsv" and CODCLI in text:
        return "PENDIENTE_GOBERNANZA_OK_CARGA_PREGRADO"
    if "Todos los checks pasaron" in text or '"decision": "APROBADO"' in text:
        return "VALIDACION_GENERAL_OK"
    if "CSV final sin header" in text:
        return "GATE_FINAL_OK"
    return "EVIDENCIA_REVISADA"


def extract_context(text: str) -> str:
    for token in [CODCLI, RUT_NUM, "CSV final sin header", "Todos los checks pasaron", "archivo_final"]:
        idx = text.find(token)
        if idx >= 0:
            return text[max(0, idx - 120): idx + 220].replace("\n", " ")[:500]
    return ""


def build_impact(final_row: pd.DataFrame, stage_row: pd.DataFrame, oferta: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    final = final_row.iloc[0] if not final_row.empty else pd.Series(dtype=str)
    stage = stage_row.iloc[0] if not stage_row.empty else pd.Series(dtype=str)
    code = clean(final.get("CODIGO_SIES_RECONSTRUIDO"))
    state = clean(final.get("ESTADO_RECONSTRUCCION"))
    version = clean(final.get("VERSION"))
    exists_offer = code in set(oferta["CODIGO_UNICO"].astype(str)) if code else False
    included = not final_row.empty
    stage_pending = clean(stage.get("SIES_RESOLUCION_HEURISTICA")) == "PENDIENTE_GOBERNANZA"
    final_class = "F. INFORMACION_INSUFICIENTE"
    need_rect = "NO_DETERMINADO"
    risk = "MEDIO"
    if included and state == "RECONSTRUIDO_V1" and exists_offer and stage_pending:
        final_class = "B. CODIGO_CARGADO_VALIDO_PERO_NO_JUSTIFICADO"
        need_rect = "NO_INMEDIATA_SI_SIES_ACEPTO; SI_DOCUMENTAR_JUSTIFICACION_VERSION"
        risk = "MEDIO_ALTO"
    elif included and state == "RECONSTRUIDO_V2" and exists_offer and stage_pending:
        final_class = "B. CODIGO_CARGADO_VALIDO_PERO_NO_JUSTIFICADO"
        need_rect = "NO_INMEDIATA_SI_SIES_ACEPTO; SI_DOCUMENTAR_JUSTIFICACION_VERSION"
        risk = "MEDIO_ALTO"
    elif included and state == "CODIGO_NO_ES_CANDIDATO_NETMRE" and exists_offer:
        final_class = "B. CODIGO_CARGADO_VALIDO_PERO_NO_JUSTIFICADO"
        need_rect = "REQUIERE_REVISION_INSTITUCIONAL_PREVIA_A_RECTIFICAR"
        risk = "ALTO"
    elif included and state in {"VERSION_VACIA", "VERSION_INVALIDA", "COMPONENTES_INCOMPLETOS"}:
        final_class = "D. VERSION_VACIA_O_INVALIDA"
        need_rect = "SI_PROBABLE"
        risk = "ALTO"
    elif not included:
        final_class = "E. REGISTRO_NO_DEBIO_SER_INCLUIDO_O_NO_INFORMADO"
        need_rect = "NO_APLICA_SI_NO_FUE_CARGADO"
        risk = "BAJO"
    rows = [
        {
            "CODCLI": CODCLI,
            "RUT": f"{RUT_NUM}-{RUT_DV}",
            "FUE_INFORMADO": "SI" if included else "NO",
            "CODIGO_RECONSTRUIDO": code,
            "VERSION_FINAL": version,
            "CODIGO_EXISTE_EN_OFERTA": "SI" if exists_offer else "NO",
            "ESTADO_STAGING": clean(stage.get("ESTADO_CARGA_PREGRADO")),
            "RESOLUCION_STAGING": clean(stage.get("SIES_RESOLUCION_HEURISTICA")),
            "CLASIFICACION_FINAL": final_class,
            "REQUIERE_RECTIFICACION": need_rect,
            "RIESGO": risk,
            "ACCION_RECOMENDADA": "Revisar evidencia institucional para justificar V1 vs V2 antes de reutilizar la lógica; no rectificar automáticamente desde esta auditoría.",
            "OBSERVACION": "La fila final contiene VERSION=3 y reconstruye I162S2C3J4V3. Ese código existe en oferta, pero el staging NETMRE quedó PENDIENTE_GOBERNANZA entre V1/V2 y V3 pertenece a alias/canon CICRE, tipo plan 3, duración 4.",
        }
    ]
    return pd.DataFrame(rows), {"clasificacion": final_class, "rectificacion": need_rect, "riesgo": risk}


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            out = df.copy()
            if out.empty:
                out = pd.DataFrame({"SIN_DATOS": [""]})
            out.to_excel(writer, sheet_name=name[:31], index=False)
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
            max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col[:80])
            ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 60)
    wb.save(path)


def copy_to_desktop() -> pd.DataFrame:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    rows = []
    for key in ["apariciones", "archivo_real", "fila", "oferta", "plan", "post", "impacto", "excel", "reporte"]:
        src = TARGETS[key]
        dst = DESKTOP / src.name
        shutil.copy2(src, dst)
        rows.append({"ARCHIVO": src.name, "HASH_ORIGINAL": sha256(src), "HASH_COPIA": sha256(dst), "COINCIDE": sha256(src) == sha256(dst)})
    try:
        subprocess.run(["open", str(DESKTOP)], check=False)
    except Exception:
        pass
    return pd.DataFrame(rows)


def main() -> None:
    AUD.mkdir(parents=True, exist_ok=True)
    REP.mkdir(parents=True, exist_ok=True)
    backup = backup_existing()
    stage = read_stage()
    stage_row = stage[stage["CODCLI"].astype(str).eq(CODCLI)].copy()

    inventory = build_inventory(stage)
    inventory.to_csv(TARGETS["apariciones"], index=False, encoding="utf-8-sig")

    file_id = build_real_file_identification()
    file_id.to_csv(TARGETS["archivo_real"], index=False, encoding="utf-8-sig")

    final_row = build_final_row()
    final_row.to_csv(TARGETS["fila"], index=False, encoding="utf-8-sig")

    oferta = build_offer_comparison()
    oferta.to_csv(TARGETS["oferta"], index=False, encoding="utf-8-sig")

    homologs = build_plan_homologs(stage)
    homologs.to_csv(TARGETS["plan"], index=False, encoding="utf-8-sig")

    post = build_post_load(final_row, stage_row)
    post.to_csv(TARGETS["post"], index=False, encoding="utf-8-sig")

    impact, conclusion = build_impact(final_row, stage_row, oferta)
    impact.to_csv(TARGETS["impacto"], index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            {"PREGUNTA": "Archivo real cargado", "RESPUESTA": "resultados/matricula_unificada_2026_pregrado.csv"},
            {"PREGUNTA": "CODCLI incluido", "RESPUESTA": "SI" if not final_row.empty else "NO"},
            {"PREGUNTA": "Código reconstruido", "RESPUESTA": clean(final_row.iloc[0].get("CODIGO_SIES_RECONSTRUIDO")) if not final_row.empty else ""},
            {"PREGUNTA": "Clasificación final", "RESPUESTA": conclusion["clasificacion"]},
            {"PREGUNTA": "Riesgo", "RESPUESTA": conclusion["riesgo"]},
            {"PREGUNTA": "Rectificación", "RESPUESTA": conclusion["rectificacion"]},
        ]
    )
    components = final_row[[c for c in MU_COLS + ["CODIGO_SIES_RECONSTRUIDO", "ESTADO_RECONSTRUCCION", "OBSERVACION"] if c in final_row.columns]].copy()
    write_excel(
        TARGETS["excel"],
        {
            "RESUMEN": summary,
            "APARICIONES": inventory,
            "ARCHIVO_REAL": file_id,
            "FILA_CARGADA": final_row,
            "COMPONENTES_SIES": components,
            "OFERTA_V1_V2": oferta,
            "PLAN_NETMRE20121": homologs,
            "HOMOLOGOS": homologs,
            "VALIDADORES": post,
            "POST_CARGA": post,
            "IMPACTO": impact,
            "CONCLUSION": summary,
        },
    )

    report = build_report(backup, file_id, final_row, stage_row, oferta, homologs, post, impact, conclusion)
    TARGETS["reporte"].write_text(report, encoding="utf-8")

    copies = copy_to_desktop()
    copies.to_csv(AUD / "HASH_COPIAS_ESCRITORIO_NETMRE016_MU2026.csv", index=False, encoding="utf-8-sig")

    run_summary = {
        "backup": str(backup),
        "hashes": {k: sha256(v) for k, v in TARGETS.items()},
        "copias": copies.to_dict("records"),
        "clasificacion": conclusion,
        "archivo_real": "resultados/matricula_unificada_2026_pregrado.csv",
        "fila": final_row.iloc[0].to_dict() if not final_row.empty else {},
    }
    (AUD / "RESUMEN_EJECUCION_CASO_NETMRE016_MU2026.json").write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(run_summary, ensure_ascii=False, indent=2))


def build_report(
    backup: Path,
    file_id: pd.DataFrame,
    final_row: pd.DataFrame,
    stage_row: pd.DataFrame,
    oferta: pd.DataFrame,
    homologs: pd.DataFrame,
    post: pd.DataFrame,
    impact: pd.DataFrame,
    conclusion: dict[str, str],
) -> str:
    f = final_row.iloc[0] if not final_row.empty else pd.Series(dtype=str)
    s = stage_row.iloc[0] if not stage_row.empty else pd.Series(dtype=str)
    code = clean(f.get("CODIGO_SIES_RECONSTRUIDO"))
    hom_same = homologs[homologs["PLAN_DE_ESTUDIO"].eq(PLAN)] if "PLAN_DE_ESTUDIO" in homologs.columns else pd.DataFrame()
    return f"""# Reporte caso crítico NETMRE016 MU2026

Generado: {datetime.now().isoformat(timespec="seconds")}

## Respuesta corta

El archivo real cargado/regulatorio vigente es `resultados/matricula_unificada_2026_pregrado.csv`.
El registro `CODCLI={CODCLI}` sí fue incluido en la salida final por RUT `{RUT_NUM}-{RUT_DV}`.

La fila final tiene `VERSION={clean(f.get('VERSION'))}` y permite reconstruir el código `{code}`.
Ese código coincide con **{('V1' if code == V1 else 'V2' if code == V2 else 'V3' if code == V3 else 'ningún candidato V1/V2/V3')}**.

Clasificación final: **{conclusion['clasificacion']}**.

## Valores finales cargados

- COD_SED: `{clean(f.get('COD_SED'))}`
- COD_CAR: `{clean(f.get('COD_CAR'))}`
- MODALIDAD: `{clean(f.get('MODALIDAD'))}`
- JOR: `{clean(f.get('JOR'))}`
- VERSION: `{clean(f.get('VERSION'))}`
- VIG: `{clean(f.get('VIG'))}`
- Código reconstruido: `{code}`
- Estado reconstrucción: `{clean(f.get('ESTADO_RECONSTRUCCION'))}`
- Fila CSV: `{clean(f.get('FILA_EXCEL'))}`
- Hash archivo: `{clean(f.get('HASH_ARCHIVO'))}`

## Staging/trazabilidad

En `ARCHIVO_LISTO_SUBIDA`, el caso figura con:

- CODCLI: `{clean(s.get('CODCLI'))}`
- Plan: `{clean(s.get('PLAN_DE_ESTUDIO'))}`
- CODCARPR: `{clean(s.get('CODCARPR_NORM'))}`
- Estado carga: `{clean(s.get('ESTADO_CARGA_PREGRADO'))}`
- Incluir en MU32: `{clean(s.get('INCLUIR_EN_MATRICULA_32'))}`
- Resolución SIES: `{clean(s.get('SIES_RESOLUCION_HEURISTICA'))}`
- Candidatos: `{clean(s.get('CODIGOS_SIES_POTENCIALES'))}`
- Código SIES final trazado: `{clean(s.get('CODIGO_CARRERA_SIES_FINAL'))}`

## Oferta V1/V2

Los candidatos V1/V2 del staging y el V3 reconstruido existen en `DURACION_ESTUDIOS.tsv`. La diferencia relevante es institucional:

- `{V1}`: IP CIISA, modalidad 3, jornada 4, tipo plan 1, duración 8.
- `{V2}`: IP SAN SEBASTIAN, modalidad 3, jornada 4, tipo plan 1, duración 8.
- `{V3}`: IP SAN SEBASTIAN, modalidad 3, jornada 4, tipo plan 3, duración 4, asociado a `CICRE`/continuidad; no aparece como candidato NETMRE en el staging del caso.

## Homólogos

Registros encontrados para `PLAN_DE_ESTUDIO={PLAN}`: {len(hom_same)}.

No se usa mayoría como regla. En la evidencia estructurada disponible, el caso queda sin resolución institucional explícita para distinguir V1/V2 en staging.

## Validador y post-carga

La evidencia local indica validación general del archivo final y presencia del caso en `sies_pendientes.tsv` como `PENDIENTE_GOBERNANZA` con `OK_CARGA_PREGRADO`.

## Impacto

- Fue efectivamente informado: **SI**.
- SIES recibió componentes que reconstruyen un código válido: **SI, `{code}`**.
- Riesgo material: **{conclusion['riesgo']}**.
- Necesidad de rectificación: **{conclusion['rectificacion']}**.

## Acción recomendada

No generar rectificación automática desde esta auditoría. Confirmar institucionalmente por qué una fila `NETMRE20121`/`NETMRE` fue cargada con `VERSION=3` (`{V3}`), cuando el staging del caso solo mostraba V1/V2 como candidatos y dejó `PENDIENTE_GOBERNANZA`. Si no existe respaldo, evaluar rectificación con acto institucional separado.

Backup: `{backup}`
"""


if __name__ == "__main__":
    main()
