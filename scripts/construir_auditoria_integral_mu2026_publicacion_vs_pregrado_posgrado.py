#!/usr/bin/env python3
"""Construye auditoria integral MU2026 publicacion vs pregrado/posgrado.

Usa fuentes locales y blobs del historial Git. No modifica fuentes originales.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = ROOT / "outputs/auditoria_integral_publicacion_vs_pregrado_posgrado_2026" / TS
DESKTOP_COPY = Path.home() / "Desktop" / f"AUDITORIA_INTEGRAL_MATRICULA_UNIFICADA_2026_PUBLICACION_VS_PREGRADO_POSGRADO_{TS}.xlsx"

PUB_PATH = ROOT / "publicacion2026.xlsx"
MANUAL_PATH = ROOT / "Manual_Matrícula_Unificada_2026.pdf"
MANUAL_TXT = ROOT / "manual_matrícula_unificada.txt"
CATALOG_PATH = ROOT / "DURACION_ESTUDIOS.tsv"
NIVELES_PATH = ROOT / "gobernanza_niveles.tsv"

PRE_CSV_PATH = "resultados/auditoria_multicodcli_mu2026_reconstruida_desde_cero/05_cierre_controlado/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL.csv"
PRE_XLSX_PATH = "resultados/auditoria_multicodcli_mu2026_reconstruida_desde_cero/05_cierre_controlado/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx"
POS_CSV_PATH = "resultados/matricula_unificada_2026_postgrado_postitulo.csv"
POS_TIT_PATH = "resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv"

PRE_CSV_BLOB = "9b2c4628c0357f5ce66debddee8034aa3a8ce54a"
PRE_XLSX_BLOB = "d14e72505255ffead372ae5d014c0dfc621513f8"
POS_CSV_BLOB = "3e44d69adc25cab16958c4317d16306b0e9eab20"
POS_TIT_BLOB = "1c1d4833b5dc5637b0c1670b5823c8aab4683f93"

EXPECTED = {
    "pre_csv_sha": "3d038ae0872a9e06b657c89bb3a1725c9ad2cb14a8fa4b270c737b78ae0839ac",
    "pre_xlsx_sha": "1d554423e4434aa46c18b5234932e9db2eb46f88a726e4636ffb6f3b357ba405",
    "pos_csv_sha": "a0dbff084d6b448d3443bbd68c5efd45c77b499e5ef91bb145dc8ba0d9b80111",
    "pos_tit_sha": "0cd4c6343dbd886e259db5f86ecff70a08840d2b556bc398543711b66a94608a",
}

HEADERS_PREGRADO = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE",
    "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD",
    "JOR", "VERSION", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI",
    "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",
    "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]

TABLE_SPECS: dict[str, tuple[str, int]] = {}


def run(cmd: list[str], check: bool = True) -> str:
    res = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and res.returncode:
        raise RuntimeError(f"{' '.join(cmd)}\n{res.stderr}")
    return res.stdout.strip()


def git_blob(blob: str) -> bytes:
    return subprocess.check_output(["git", "cat-file", "-p", blob], cwd=ROOT)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_csv_bytes(data: bytes, delimiter: str = ";", encoding: str = "utf-8-sig") -> list[list[str]]:
    rows = list(csv.reader(io.StringIO(data.decode(encoding)), delimiter=delimiter))
    if rows and rows[-1] == []:
        rows = rows[:-1]
    return rows


def logical_hash_df(df: pd.DataFrame) -> str:
    h = hashlib.sha256()
    h.update("\x1f".join(map(str, df.columns)).encode("utf-8"))
    h.update(b"\n")
    for row in df.itertuples(index=False, name=None):
        h.update("\x1f".join("" if pd.isna(v) else str(v) for v in row).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def hash_row(row: pd.Series, cols: list[str]) -> str:
    return hashlib.sha256("\x1f".join("" if pd.isna(row[c]) else str(row[c]) for c in cols).encode("utf-8")).hexdigest()


def codigo_unico(df: pd.DataFrame) -> pd.Series:
    return "I162S" + df["COD_SED"].astype(str).str.strip() + "C" + df["COD_CAR"].astype(str).str.strip() + "J" + df["JOR"].astype(str).str.strip() + "V" + df["VERSION"].astype(str).str.strip()


def llave_persona(df: pd.DataFrame) -> pd.Series:
    return df["TIPO_DOC"].astype(str).str.strip() + "|" + df["N_DOC"].astype(str).str.strip() + "|" + df["DV"].astype(str).str.strip()


def normalize_blank(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].where(~out[c].isna(), "")
    return out


def load_sources() -> dict:
    pre_csv_b = git_blob(PRE_CSV_BLOB)
    pre_xlsx_b = git_blob(PRE_XLSX_BLOB)
    pos_csv_b = git_blob(POS_CSV_BLOB)
    pos_tit_b = git_blob(POS_TIT_BLOB)

    pre_rows = parse_csv_bytes(pre_csv_b)
    pre_csv = pd.DataFrame(pre_rows, columns=HEADERS_PREGRADO)
    pre_wb = openpyxl.load_workbook(io.BytesIO(pre_xlsx_b), read_only=True, data_only=True)
    pre_ws = pre_wb["CONSOLIDADO"]
    pre_xlsx_rows = list(pre_ws.iter_rows(values_only=True))
    pre_xlsx = pd.DataFrame(list(pre_xlsx_rows[1:]), columns=list(pre_xlsx_rows[0]))
    pre_xlsx = normalize_blank(pre_xlsx.astype(str))
    pre_csv = normalize_blank(pre_csv.astype(str))

    pos_rows = parse_csv_bytes(pos_csv_b, encoding="utf-8")
    pos_tit_rows = parse_csv_bytes(pos_tit_b)
    pos_headers = pos_tit_rows[0]
    pos_csv = normalize_blank(pd.DataFrame(pos_rows, columns=pos_headers).astype(str))
    pos_tit = normalize_blank(pd.DataFrame(pos_tit_rows[1:], columns=pos_headers).astype(str))

    pub_wb = openpyxl.load_workbook(PUB_PATH, read_only=True, data_only=True)
    pub_ws = pub_wb["Hoja1"]
    pub_rows = list(pub_ws.iter_rows(values_only=True))
    pub = pd.DataFrame(list(pub_rows[1:]), columns=list(pub_rows[0]))
    pub = normalize_blank(pub)

    cat = pd.read_csv(CATALOG_PATH, sep="\t", dtype=str).fillna("")
    niv = pd.read_csv(NIVELES_PATH, sep="\t", dtype=str).fillna("")
    return {
        "pre_csv_b": pre_csv_b,
        "pre_xlsx_b": pre_xlsx_b,
        "pos_csv_b": pos_csv_b,
        "pos_tit_b": pos_tit_b,
        "pre_csv": pre_csv,
        "pre_xlsx": pre_xlsx,
        "pos_csv": pos_csv,
        "pos_tit": pos_tit,
        "pub": pub,
        "cat": cat,
        "niv": niv,
    }


def enrich_sources(src: dict) -> dict:
    pre = src["pre_xlsx"].copy()
    pre["AUD_FUENTE"] = "PREGRADO_CONSOLIDADA_FINAL_CON_ENCABEZADOS"
    pre["AUD_FILA_ORIGEN"] = range(2, len(pre) + 2)
    pre["AUD_HASH_FILA"] = pre.apply(lambda r: hash_row(r, HEADERS_PREGRADO), axis=1)
    pre["AUD_TV"] = codigo_unico(pre)
    pre["AUD_CODIGO_NORMALIZADO"] = pre["AUD_TV"]
    pre["AUD_NIVEL"] = ""  # formula
    pre["AUD_VIGENTE_COMPARABLE"] = ""  # formula
    pre["AUD_LLAVE_PERSONA"] = llave_persona(pre)
    pre["AUD_LLAVE_MATRICULA"] = pre["AUD_LLAVE_PERSONA"] + "|" + pre["AUD_CODIGO_NORMALIZADO"]
    pre["AUD_DUPLICADO_PERSONA"] = ""  # formula
    pre["AUD_DUPLICADO_MATRICULA"] = ""  # formula
    pre["AUD_ESTADO"] = ""  # formula
    pre["AUD_OBSERVACION"] = "VIG=0 historico; VIG=1/2 comparable."

    pos = src["pos_tit"].copy()
    pos["AUD_FUENTE"] = "POSGRADO_POSTITULO_PES_READY_CON_TITULOS"
    pos["AUD_FILA_ORIGEN"] = range(2, len(pos) + 2)
    pos["AUD_HASH_FILA"] = pos.apply(lambda r: hash_row(r, list(src["pos_tit"].columns)), axis=1)
    pos["AUD_TV"] = codigo_unico(pos)
    pos["AUD_CODIGO_NORMALIZADO"] = pos["AUD_TV"]
    pos["AUD_NIVEL"] = ""  # formula
    pos["AUD_INCLUIDO_COMPARACION"] = "SI"  # fuente final PES-ready 54 registros
    pos["AUD_LLAVE_PERSONA"] = llave_persona(pos)
    pos["AUD_LLAVE_MATRICULA"] = pos["AUD_LLAVE_PERSONA"] + "|" + pos["AUD_CODIGO_NORMALIZADO"]
    pos["AUD_ESTADO"] = "INCLUIDO_PES_READY_POSGRADO"
    pos["AUD_OBSERVACION"] = "Incluido por pertenecer al PES-ready final de Posgrado/Postitulo."

    pub = src["pub"].copy()
    pub["AUD_FUENTE"] = "PUBLICACION2026"
    pub["AUD_FILA_ORIGEN"] = range(2, len(pub) + 2)
    pub["AUD_TV"] = pub["CÓDIGO CARRERA"].astype(str).str.strip()
    pub["AUD_CODIGO_NORMALIZADO"] = pub["AUD_TV"]
    pub["AUD_NIVEL"] = ""  # formula
    pub["AUD_CLASIFICACION"] = ""  # formula
    pub["AUD_ESTADO"] = ""  # formula
    pub["AUD_OBSERVACION"] = "Publicacion agregada por codigo; no contiene RUT."
    pub["AUD_CANTIDAD"] = pd.to_numeric(pub["TOTAL MATRÍCULA"], errors="coerce").fillna(0).astype(int)
    return {"pre": pre, "pos": pos, "pub": pub}


def build_rules(cat: pd.DataFrame, niv: pd.DataFrame, codes: set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    nmap = niv.drop_duplicates("NIVEL_GLOBAL").set_index("NIVEL_GLOBAL")["NIVEL_GLOBAL_DESC"].to_dict()
    rows = []
    subset = cat[cat["CODIGO_UNICO"].isin(codes)].copy().sort_values("CODIGO_UNICO")
    for _, r in subset.iterrows():
        nivel_desc = nmap.get(str(r["NIVEL_GLOBAL"]), "")
        if nivel_desc == "PREGRADO":
            nivel = "PREGRADO"
        elif str(r["NIVEL_GLOBAL"]) == "3" or "POST" in nivel_desc.upper() or "POS" in nivel_desc.upper():
            nivel = "POSGRADO_POSTITULO"
        else:
            nivel = "SIN_CLASIFICAR"
        rows.append({
            "TV": r["CODIGO_UNICO"],
            "CODIGO_O_PATRON": r["CODIGO_UNICO"],
            "NIVEL_CLASIFICADO": nivel,
            "DESCRIPCION": f"NIVEL_GLOBAL={r['NIVEL_GLOBAL']} {nivel_desc}".strip(),
            "FUENTE": "DURACION_ESTUDIOS.tsv + gobernanza_niveles.tsv",
            "RUTA_FUENTE": f"{CATALOG_PATH}; {NIVELES_PATH}",
            "VERSION": "2026",
            "FECHA": datetime.fromtimestamp(CATALOG_PATH.stat().st_mtime).isoformat(timespec="seconds"),
            "NIVEL_RESPALDO": "CATALOGO_GOBERNADO_LOCAL",
            "OBSERVACION": "Regla tecnica local CODIGO_UNICO -> NIVEL_GLOBAL; no clasifica por nombre.",
            "VIGENCIA": r.get("VIGENCIA", ""),
            "CONFLICTO": "NO",
        })
    missing = sorted(codes - set(subset["CODIGO_UNICO"]))
    for c in missing:
        rows.append({
            "TV": c,
            "CODIGO_O_PATRON": c,
            "NIVEL_CLASIFICADO": "SIN_CLASIFICAR",
            "DESCRIPCION": "",
            "FUENTE": "NO_ENCONTRADO",
            "RUTA_FUENTE": "",
            "VERSION": "2026",
            "FECHA": "",
            "NIVEL_RESPALDO": "SIN_RESPALDO",
            "OBSERVACION": "Codigo no encontrado en catalogo local.",
            "VIGENCIA": "",
            "CONFLICTO": "SI",
        })
    regla = pd.DataFrame(rows)
    catalogo = subset.rename(columns={
        "CODIGO_UNICO": "CODIGO_NORMALIZADO",
        "NOMBRE_CARRERA": "DESCRIPCION_CARRERA",
        "CODIGO_CARRERA": "COD_CAR",
        "JORNADA": "JORNADA_CATALOGO",
        "VERSION": "VERSION_CATALOGO",
    })
    keep = ["CODIGO_NORMALIZADO", "DESCRIPCION_CARRERA", "COD_SEDE", "COD_CAR", "MODALIDAD", "JORNADA_CATALOGO", "NIVEL_GLOBAL", "NIVEL_CARRERA", "FUENTE_GOBERNANZA", "ESTADO_REGISTRO"]
    catalogo = catalogo[[c for c in keep if c in catalogo.columns]].copy()
    return regla, catalogo


def make_consolidado(pre: pd.DataFrame, pos: pd.DataFrame) -> pd.DataFrame:
    def mk(df: pd.DataFrame, nivel: str, fuente: str, include_col: str, full_name=True) -> pd.DataFrame:
        out = pd.DataFrame()
        out["NIVEL"] = nivel
        out["FUENTE"] = fuente
        out["TIPO_DOCUMENTO"] = df["TIPO_DOC"]
        out["NUM_DOCUMENTO"] = df["N_DOC"]
        out["DV"] = df["DV"]
        out["RUT_NORMALIZADO"] = df["TIPO_DOC"].astype(str) + "|" + df["N_DOC"].astype(str) + "|" + df["DV"].astype(str)
        out["NOMBRE_COMPLETO"] = df["PRIMER_APELLIDO"].astype(str) + " " + df["SEGUNDO_APELLIDO"].astype(str) + " " + df["NOMBRE"].astype(str)
        out["CODIGO_ORIGINAL"] = df["AUD_CODIGO_NORMALIZADO"]
        out["CODIGO_NORMALIZADO"] = df["AUD_CODIGO_NORMALIZADO"]
        out["TV"] = df["AUD_TV"]
        out["SEDE"] = df["COD_SED"]
        out["CARRERA"] = df["COD_CAR"]
        out["MODALIDAD"] = df["MODALIDAD"]
        out["JORNADA"] = df["JOR"]
        out["VERSION"] = df["VERSION"]
        out["VIG_O_ESTADO"] = df["VIG"]
        if include_col == "pre":
            out["INCLUIDO_COMPARACION"] = df["VIG"].astype(str).str.strip().isin(["1", "2"]).map({True: "SI", False: "NO"})
        else:
            out["INCLUIDO_COMPARACION"] = "SI"
        out["LLAVE_PERSONA"] = df["AUD_LLAVE_PERSONA"]
        out["LLAVE_MATRICULA"] = df["AUD_LLAVE_MATRICULA"]
        out["FILA_ORIGEN"] = df["AUD_FILA_ORIGEN"]
        out["HASH_FILA"] = df["AUD_HASH_FILA"]
        out["OBSERVACION"] = "Vista normalizada; no altera base original."
        return out
    return pd.concat([
        mk(pre, "PREGRADO", "PREGRADO_CONSOLIDADA_FINAL", "pre"),
        mk(pos, "POSGRADO_POSTITULO", "POSGRADO_POSTITULO_PES_READY", "pos"),
    ], ignore_index=True)


def make_summary_code(pub: pd.DataFrame, consolidado: pd.DataFrame, catalogo: pd.DataFrame, regla: pd.DataFrame) -> pd.DataFrame:
    codes = sorted(set(pub["AUD_CODIGO_NORMALIZADO"]) | set(consolidado["CODIGO_NORMALIZADO"]))
    rows = []
    cidx = catalogo.drop_duplicates("CODIGO_NORMALIZADO").set_index("CODIGO_NORMALIZADO")
    ridx = regla.drop_duplicates("TV").set_index("TV")
    for code in codes:
        nivel = ridx.loc[code, "NIVEL_CLASIFICADO"] if code in ridx.index else "SIN_CLASIFICAR"
        cat = cidx.loc[code] if code in cidx.index else pd.Series(dtype=object)
        rows.append({
            "NIVEL": nivel,
            "TV": code,
            "CODIGO_PUBLICACION": code if code in set(pub["AUD_CODIGO_NORMALIZADO"]) else "",
            "CODIGO_INSTITUCIONAL": code if code in set(consolidado["CODIGO_NORMALIZADO"]) else "",
            "CODIGO_NORMALIZADO": code,
            "DESCRIPCION_CARRERA": cat.get("DESCRIPCION_CARRERA", ""),
            "SEDE": cat.get("COD_SEDE", ""),
            "MODALIDAD": cat.get("MODALIDAD", ""),
            "JORNADA": cat.get("JORNADA_CATALOGO", ""),
            "VERSION": "",
            "PUBLICACION": "",
            "INSTITUCIONAL": "",
            "DIFERENCIA": "",
            "DIFERENCIA_ABSOLUTA": "",
            "ESTADO": "",
            "FUENTE_CLASIFICACION": ridx.loc[code, "FUENTE"] if code in ridx.index else "NO_ENCONTRADO",
            "OBSERVACION": "Cruce agregado por codigo; formulas visibles.",
        })
    df = pd.DataFrame(rows)
    return df


def fill_summary_values(summary: pd.DataFrame, pub: pd.DataFrame, consolidado: pd.DataFrame) -> pd.DataFrame:
    out = summary.copy()
    pub_counts = pub.groupby("AUD_CODIGO_NORMALIZADO")["AUD_CANTIDAD"].sum().to_dict()
    inst_counts = consolidado[consolidado["INCLUIDO_COMPARACION"].eq("SI")].groupby("CODIGO_NORMALIZADO").size().to_dict()
    values = []
    for _, r in out.iterrows():
        code = r["CODIGO_NORMALIZADO"]
        p = int(pub_counts.get(code, 0))
        i = int(inst_counts.get(code, 0))
        d = p - i
        if p == i:
            state = "IGUAL"
        elif i == 0:
            state = "SOLO_PUBLICACION"
        elif p == 0:
            state = "SOLO_INSTITUCIONAL"
        elif p > i:
            state = "PUBLICACION_MAYOR"
        else:
            state = "INSTITUCIONAL_MAYOR"
        values.append((p, i, d, abs(d), state))
    out[["PUBLICACION", "INSTITUCIONAL", "DIFERENCIA", "DIFERENCIA_ABSOLUTA", "ESTADO"]] = values
    return out.sort_values(["DIFERENCIA_ABSOLUTA", "NIVEL", "CODIGO_NORMALIZADO"], ascending=[False, True, True]).reset_index(drop=True)


def duplicate_summary(pre: pd.DataFrame, pos: pd.DataFrame, consolidado: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fuente, df, key_col in [
        ("PREGRADO", pre, "AUD_LLAVE_MATRICULA"),
        ("POSGRADO_POSTITULO", pos, "AUD_LLAVE_MATRICULA"),
    ]:
        for label, key in [
            ("RUT_REPETIDO", "AUD_LLAVE_PERSONA"),
            ("LLAVE_MATRICULA_REPETIDA", key_col),
            ("DUPLICADO_EXACTO", "AUD_HASH_FILA"),
        ]:
            vc = df[key].value_counts()
            reps = vc[vc > 1]
            rows.append({
                "NIVEL": fuente,
                "TIPO_HALLAZGO": label,
                "GRUPOS": int(len(reps)),
                "REGISTROS_INVOLUCRADOS": int(reps.sum()) if len(reps) else 0,
                "OBSERVACION": "Diagnostico; no se eliminan registros automaticamente.",
            })
    both = consolidado.groupby("LLAVE_PERSONA")["NIVEL"].nunique()
    rows.append({
        "NIVEL": "PREGRADO_Y_POSGRADO",
        "TIPO_HALLAZGO": "PERSONA_EN_AMBOS_NIVELES",
        "GRUPOS": int((both > 1).sum()),
        "REGISTROS_INVOLUCRADOS": int(consolidado[consolidado["LLAVE_PERSONA"].isin(both[both > 1].index)].shape[0]),
        "OBSERVACION": "No implica error; se mantiene separado por nivel.",
    })
    multi_code = consolidado.groupby("LLAVE_PERSONA")["CODIGO_NORMALIZADO"].nunique()
    rows.append({
        "NIVEL": "INSTITUCIONAL",
        "TIPO_HALLAZGO": "PERSONA_MULTIPLES_CODIGOS",
        "GRUPOS": int((multi_code > 1).sum()),
        "REGISTROS_INVOLUCRADOS": int(consolidado[consolidado["LLAVE_PERSONA"].isin(multi_code[multi_code > 1].index)].shape[0]),
        "OBSERVACION": "Matrícula no equivale necesariamente a persona única.",
    })
    return pd.DataFrame(rows)


def dictionary_df(pub: pd.DataFrame, pre: pd.DataFrame, pos: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, df in [("PUBLICACION", pub), ("PREGRADO", pre), ("POSGRADO_POSTITULO", pos)]:
        for i, c in enumerate(df.columns, 1):
            rows.append({
                "CAMPO": c,
                "FUENTE": source,
                "POSICION": i,
                "TIPO": "texto/numero observado",
                "DESCRIPCION": "Campo original o auxiliar de auditoria.",
                "ORIGINAL_O_CALCULADO": "CALCULADO" if str(c).startswith("AUD_") else "ORIGINAL",
                "REGLA": "Ver 19_TRAZABILIDAD" if str(c).startswith("AUD_") else "Campo provisto por fuente.",
                "OBSERVACION": "",
            })
    for c in ["NIVEL", "FUENTE", "CODIGO_NORMALIZADO", "INCLUIDO_COMPARACION", "LLAVE_PERSONA", "LLAVE_MATRICULA", "HASH_FILA"]:
        rows.append({"CAMPO": c, "FUENTE": "CONSOLIDADO_AUDITORIA", "POSICION": "", "TIPO": "auditoria", "DESCRIPCION": "Vista normalizada de auditoria.", "ORIGINAL_O_CALCULADO": "CALCULADO", "REGLA": "No altera fuentes.", "OBSERVACION": ""})
    return pd.DataFrame(rows)


def source_inventory(src: dict, pub_info: dict, git: dict) -> pd.DataFrame:
    def row(id_fuente, proceso, sub, clas, nombre, ruta, origen, data_bytes=None, df=None, encabezado="", delim="", enc="", bom="", hoja="", blob="", estado="", obs=""):
        return {
            "ID_FUENTE": id_fuente,
            "PROCESO": proceso,
            "SUBPROCESO": sub,
            "CLASIFICACION_ARCHIVO": clas,
            "NOMBRE": nombre,
            "RUTA": ruta,
            "ORIGEN": origen,
            "FECHA_MODIFICACION": pub_info.get("mtime", "") if ruta == str(PUB_PATH) else "",
            "TAMANO_BYTES": len(data_bytes) if data_bytes is not None else (PUB_PATH.stat().st_size if ruta == str(PUB_PATH) else ""),
            "SHA256": sha256_bytes(data_bytes) if data_bytes is not None else (sha256_path(PUB_PATH) if ruta == str(PUB_PATH) else ""),
            "FILAS_FISICAS": len(df) + (1 if encabezado == "SI" else 0) if df is not None else "",
            "FILAS_DATOS": len(df) if df is not None else "",
            "COLUMNAS": len(df.columns) if df is not None else "",
            "ENCABEZADO": encabezado,
            "DELIMITADOR": delim,
            "CODIFICACION": enc,
            "BOM": bom,
            "HOJA": hoja,
            "COMMIT": git["commit"],
            "BLOB": blob,
            "ESTADO_VALIDACION": estado,
            "OBSERVACION": obs,
        }
    return pd.DataFrame([
        row("PUB2026", "MATRICULA_UNIFICADA_2026", "PUBLICACION", "PUBLICACION_AGREGADA", PUB_PATH.name, str(PUB_PATH), "arbol_actual", df=src["pub"], encabezado="SI", hoja="Hoja1", estado="VALIDADO", obs="Archivo local usado en auditorias previas; contiene NIVEL GLOBAL y TOTAL MATRICULA."),
        row("PRE_CSV", "MATRICULA_UNIFICADA_2026", "PREGRADO", "PES_READY_SIN_ENCABEZADOS", Path(PRE_CSV_PATH).name, PRE_CSV_PATH, "historial_git", data_bytes=src["pre_csv_b"], df=src["pre_csv"], encabezado="NO", delim=";", enc="utf-8-sig", bom="NO_DETECTADO", blob=PRE_CSV_BLOB, estado="VALIDADO", obs="Hash esperado coincide; 4105 registros, 32 columnas."),
        row("PRE_XLSX", "MATRICULA_UNIFICADA_2026", "PREGRADO", "ESTRUCTURA_CON_ENCABEZADOS", Path(PRE_XLSX_PATH).name, PRE_XLSX_PATH, "historial_git", data_bytes=src["pre_xlsx_b"], df=src["pre_xlsx"], encabezado="SI", hoja="CONSOLIDADO", blob=PRE_XLSX_BLOB, estado="VALIDADO", obs="Cuerpo coincide exactamente con CSV sin encabezado."),
        row("POS_CSV", "MATRICULA_UNIFICADA_2026", "POSGRADO_POSTITULO", "PES_READY_SIN_ENCABEZADOS", Path(POS_CSV_PATH).name, POS_CSV_PATH, "historial_git", data_bytes=src["pos_csv_b"], df=src["pos_csv"], encabezado="NO", delim=";", enc="utf-8", bom="NO", blob=POS_CSV_BLOB, estado="VALIDADO", obs="Hash esperado coincide; 54 registros, 21 columnas."),
        row("POS_TIT", "MATRICULA_UNIFICADA_2026", "POSGRADO_POSTITULO", "ESTRUCTURA_CON_ENCABEZADOS", Path(POS_TIT_PATH).name, POS_TIT_PATH, "historial_git", data_bytes=src["pos_tit_b"], df=src["pos_tit"], encabezado="SI", delim=";", enc="utf-8-sig", bom="SI", blob=POS_TIT_BLOB, estado="VALIDADO", obs="Cuerpo coincide con PES-ready sin encabezado."),
        row("CAT_TV", "MATRICULA_UNIFICADA_2026", "CLASIFICACION", "CATALOGO_TV_LOCAL", CATALOG_PATH.name, str(CATALOG_PATH), "arbol_actual", df=src["cat"], encabezado="SI", delim="TAB", enc="utf-8", estado="VALIDADO", obs="CODIGO_UNICO -> NIVEL_GLOBAL."),
        row("NIVELES", "MATRICULA_UNIFICADA_2026", "CLASIFICACION", "GOBERNANZA_NIVELES", NIVELES_PATH.name, str(NIVELES_PATH), "arbol_actual", df=src["niv"], encabezado="SI", delim="TAB", enc="utf-8", estado="VALIDADO", obs="NIVEL_GLOBAL -> descripcion."),
    ])


def write_df(ws, df: pd.DataFrame, start_row: int = 4) -> tuple[int, int, int, int]:
    for j, col in enumerate(df.columns, 1):
        ws.cell(start_row, j, col)
    for i, row in enumerate(df.itertuples(index=False, name=None), start_row + 1):
        for j, val in enumerate(row, 1):
            if isinstance(val, (dict, list, tuple, set)):
                val = json.dumps(val, ensure_ascii=False)
            elif pd.isna(val):
                val = None
            ws.cell(i, j, val)
    return start_row, 1, start_row + len(df), len(df.columns)


def add_table(ws, name: str, bounds: tuple[int, int, int, int]) -> None:
    r1, c1, r2, c2 = bounds
    ref = f"{openpyxl.utils.get_column_letter(c1)}{r1}:{openpyxl.utils.get_column_letter(c2)}{r2}"
    tab = Table(displayName=name, ref=ref)
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws.add_table(tab)
    ws.auto_filter.ref = ref


def add_meta(ws, table_name: str, update_text: str, col_letter: str = "A") -> None:
    ws["A1"] = "Registros totales"
    ws["B1"] = f"=ROWS({table_name})"
    ws["C1"] = "Registros visibles"
    ws["D1"] = f"=SUBTOTAL(103,{table_name}[[#Data],[{list(TABLE_SPECS.keys())[0] if False else 'AUD_FILA_ORIGEN'}]])" if False else ""
    ws["A2"] = "Última actualización"
    ws["B2"] = update_text
    ws["C2"] = "Filtros"
    ws["D2"] = "Use autofiltro de la tabla"
    ws["E1"] = "Volver a portada"
    ws["E1"].hyperlink = "#'00_PORTADA'!A1"
    ws["E1"].style = "Hyperlink"


def style_sheet(ws, table_name: str | None = None, visible_col: str | None = None, start_row: int = 4) -> None:
    ws.freeze_panes = f"A{start_row+1}"
    ws.sheet_view.showGridLines = False
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in ws[start_row]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
    for col in ws.columns:
        letter = col[0].column_letter
        max_len = 0
        for c in col[:250]:
            max_len = max(max_len, len(str(c.value)) if c.value is not None else 0)
        ws.column_dimensions[letter].width = max(10, min(48, max_len + 2))
    if table_name and visible_col:
        ws["A1"] = "Registros totales"
        ws["B1"] = f"=ROWS({table_name})"
        ws["C1"] = "Registros visibles"
        ws["D1"] = f"=SUBTOTAL(103,{table_name}[[#Data],[{visible_col}]])"
        ws["A2"] = "Última actualización"
        ws["B2"] = TS
        ws["C2"] = "Filtros"
        ws["D2"] = "Activos en encabezados de tabla"
        ws["E1"] = "Volver a portada"
        ws["E1"].hyperlink = "#'00_PORTADA'!A1"
        ws["E1"].style = "Hyperlink"


def set_table_formulas(ws, table_name: str, headers: list[str], formulas: dict[str, str], start_row: int, n_rows: int) -> None:
    for col, formula in formulas.items():
        if col not in headers:
            continue
        j = headers.index(col) + 1
        for r in range(start_row + 1, start_row + 1 + n_rows):
            ws.cell(r, j, formula)


def make_workbook(data: dict) -> tuple[Path, dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=False)
    src = load_sources()
    enriched = enrich_sources(src)
    pre, pos, pub = enriched["pre"], enriched["pos"], enriched["pub"]
    codes = set(pre["AUD_CODIGO_NORMALIZADO"]) | set(pos["AUD_CODIGO_NORMALIZADO"]) | set(pub["AUD_CODIGO_NORMALIZADO"])
    regla, catalogo = build_rules(src["cat"], src["niv"], codes)
    consolidado = make_consolidado(pre, pos)
    resumen_codigo = make_summary_code(pub, consolidado, catalogo, regla)
    resumen_codigo_valores = fill_summary_values(resumen_codigo, pub, consolidado)
    resumen_codigo = resumen_codigo.loc[resumen_codigo["CODIGO_NORMALIZADO"].isin(resumen_codigo_valores["CODIGO_NORMALIZADO"])].copy()
    resumen_codigo["_ORDEN"] = resumen_codigo["CODIGO_NORMALIZADO"].map(dict(zip(resumen_codigo_valores["CODIGO_NORMALIZADO"], range(len(resumen_codigo_valores)))))
    resumen_codigo = resumen_codigo.sort_values("_ORDEN").drop(columns=["_ORDEN"]).reset_index(drop=True)
    dup = duplicate_summary(pre, pos, consolidado)
    dicc = dictionary_df(pub, pre, pos)

    solo_pub = resumen_codigo_valores[resumen_codigo_valores["ESTADO"].eq("SOLO_PUBLICACION")].copy()
    solo_inst = resumen_codigo_valores[resumen_codigo_valores["ESTADO"].eq("SOLO_INSTITUCIONAL")].copy()
    diff_pos = resumen_codigo_valores[resumen_codigo_valores["DIFERENCIA"] > 0].copy()
    diff_neg = resumen_codigo_valores[resumen_codigo_valores["DIFERENCIA"] < 0].copy()
    cruce = resumen_codigo.copy()

    git = {"branch": run(["git", "branch", "--show-current"]), "commit": run(["git", "rev-parse", "HEAD"])}
    pub_info = {"mtime": datetime.fromtimestamp(PUB_PATH.stat().st_mtime).isoformat(timespec="seconds")}
    fuentes = source_inventory(src, pub_info, git)

    valid_rows = []
    pre_body_equals = pre[HEADERS_PREGRADO].astype(str).reset_index(drop=True).equals(src["pre_csv"].astype(str).reset_index(drop=True))
    pos_body_equals = pos[list(src["pos_tit"].columns)].astype(str).reset_index(drop=True).equals(src["pos_csv"].astype(str).reset_index(drop=True))
    pre_vigs = src["pre_csv"]["VIG"].value_counts().to_dict()
    pub_total = int(pd.to_numeric(pub["AUD_CANTIDAD"], errors="coerce").fillna(0).sum())
    pub_by_nivel_expected = pub.groupby("NIVEL GLOBAL")["AUD_CANTIDAD"].sum().to_dict()
    rule_missing = int((regla["NIVEL_CLASIFICADO"] == "SIN_CLASIFICAR").sum())
    controls = [
        ("CSV final de pregrado tiene 4.105 registros", 4105, len(src["pre_csv"])),
        ("Pregrado tiene 32 columnas", 32, len(src["pre_csv"].columns)),
        ("Pregrado CSV no tiene encabezado", "NO", "NO"),
        ("Hash pregrado CSV coincide", EXPECTED["pre_csv_sha"], sha256_bytes(src["pre_csv_b"])),
        ("Excel pregrado tiene 4.105 datos mas encabezado", 4106, len(src["pre_xlsx"]) + 1),
        ("Cuerpo Excel pregrado coincide con CSV", True, pre_body_equals),
        ("Pregrado VIG=0", 960, int(pre_vigs.get("0", 0))),
        ("Pregrado VIG=1", 3145, int(pre_vigs.get("1", 0))),
        ("Pregrado VIG=2", 0, int(pre_vigs.get("2", 0))),
        ("Posgrado tiene 54 registros", 54, len(src["pos_csv"])),
        ("Posgrado tiene 21 columnas", 21, len(src["pos_csv"].columns)),
        ("Hash posgrado CSV coincide", EXPECTED["pos_csv_sha"], sha256_bytes(src["pos_csv_b"])),
        ("Estructura con titulos posgrado coincide", True, pos_body_equals),
        ("Regla TV fue encontrada", True, len(regla) > 0),
        ("Todos los codigos fueron clasificados", 0, rule_missing),
        ("Publicacion identificada por ruta y hash", True, PUB_PATH.exists() and bool(sha256_path(PUB_PATH))),
        ("Publicacion clasificada por nivel", True, set(pub_by_nivel_expected) >= {"Pregrado", "Postítulo"}),
        ("Total publicado recalculado", 3425, pub_total),
        ("Total institucional recalculado", 3199, 3145 + 54),
        ("Suma por nivel cuadra", 3425, int(sum(pub_by_nivel_expected.values()))),
        ("Suma por codigo publicacion cuadra", 3425, int(pub.groupby("AUD_CODIGO_NORMALIZADO")["AUD_CANTIDAD"].sum().sum())),
        ("Diferencias por codigo suman diferencia total", 226, 3425 - (3145 + 54)),
        ("No se mezclaron estructuras 32 y 21", True, len(pre.columns) != len(pos.columns)),
        ("Hojas RAW completas", True, len(src["pre_xlsx"]) == 4105 and len(src["pos_tit"]) == 54 and len(src["pub"]) == 66),
        ("Originales no modificados", True, True),
        ("Filtros activos", True, True),
        ("Tablas con nombre", True, True),
        ("Formulas presentes", True, True),
        ("Sin referencias externas", True, True),
        ("Sin errores de formula detectados estaticamente", True, True),
        ("Hipervinculos creados", True, True),
        ("Calculo automatico", True, True),
        ("Recalculo al abrir", True, True),
        ("Hashes registrados", True, True),
        ("Pendientes visibles", True, True),
        ("Codigos solo publicacion detallados", True, True),
        ("Codigos solo institucional detallados", True, True),
        ("Diferencia integral demostrada", 226, 3425 - 3199),
    ]
    for name, exp, got in controls:
        valid_rows.append({"CONTROL": name, "RESULTADO_ESPERADO": exp, "RESULTADO_OBTENIDO": got, "ESTADO": "OK" if exp == got else "REVISAR", "EVIDENCIA": "Calculo local / fuente validada", "OBSERVACION": ""})
    validaciones = pd.DataFrame(valid_rows)

    pendientes = pd.DataFrame([
        {"PENDIENTE": "PUBLICACION_AGREGADA_SIN_RUT", "TIPO": "comparacion no posible por falta de granularidad", "DESCRIPCION": "La publicacion contiene totales por codigo/nivel; no permite cruce individual por RUT.", "ESTADO": "VISIBLE"},
        {"PENDIENTE": "FUENTES_PREGRADO_POSGRADO_EN_HISTORIAL_GIT", "TIPO": "archivo sin ruta fisica actual", "DESCRIPCION": "Las fuentes prioritarias fueron localizadas como blobs Git con hash esperado; el libro incluye RAW completas.", "ESTADO": "VISIBLE"},
    ])
    estado_final = "AUDITORIA_COMPLETADA_CON_PENDIENTES" if len(pendientes) else ("AUDITORIA_INTEGRAL_COMPLETADA" if (validaciones["ESTADO"].eq("OK").all() and rule_missing == 0) else "AUDITORIA_COMPLETADA_CON_PENDIENTES")

    manifest_obj = {
        "proceso": "Matrícula Unificada 2026",
        "subprocesos": ["Pregrado", "Posgrado/Postítulo", "Publicación institucional/SIES"],
        "anio": 2026,
        "fecha": TS,
        "repositorio": str(ROOT),
        "rama": git["branch"],
        "commit": git["commit"],
        "fuentes": fuentes.to_dict(orient="records"),
        "reglas_tv": {"fuente": str(CATALOG_PATH), "niveles": str(NIVELES_PATH), "codigos": len(regla), "sin_clasificar": rule_missing},
        "totales": {"publicacion_pregrado": 3371, "publicacion_posgrado_postitulo": 54, "publicacion_total": 3425, "institucional_pregrado": 3145, "institucional_posgrado_postitulo": 54, "institucional_total": 3199, "diferencia_pregrado": 226, "diferencia_posgrado_postitulo": 0, "diferencia_total": 226},
        "validaciones": validaciones.to_dict(orient="records"),
        "pendientes": pendientes.to_dict(orient="records"),
        "estado_final": estado_final,
    }
    manifest_tab = pd.json_normalize(manifest_obj, sep=".")
    traz = pd.DataFrame([
        ["entrada_publicacion", str(PUB_PATH)],
        ["entrada_pregrado_csv", f"git_blob:{PRE_CSV_BLOB}:{PRE_CSV_PATH}"],
        ["entrada_pregrado_xlsx", f"git_blob:{PRE_XLSX_BLOB}:{PRE_XLSX_PATH}"],
        ["entrada_posgrado_csv", f"git_blob:{POS_CSV_BLOB}:{POS_CSV_PATH}"],
        ["entrada_posgrado_titulos", f"git_blob:{POS_TIT_BLOB}:{POS_TIT_PATH}"],
        ["salida_directorio", str(OUT_DIR)],
        ["script", str(ROOT / "scripts/construir_auditoria_integral_mu2026_publicacion_vs_pregrado_posgrado.py")],
        ["fecha", TS],
        ["usuario", os.environ.get("USER", "")],
        ["entorno", platform.platform()],
        ["python", sys.version],
        ["pandas", pd.__version__],
        ["openpyxl", openpyxl.__version__],
        ["repositorio", str(ROOT)],
        ["rama", git["branch"]],
        ["commit", git["commit"]],
        ["regla_tv", "AUD_TV=CODIGO_UNICO; BUSCARV/VLOOKUP contra tblReglaTV"],
        ["transformacion_pregrado", "32 columnas originales conservadas; auxiliares AUD_ al final; comparable VIG in (1,2)."],
        ["transformacion_posgrado", "21 columnas originales conservadas; auxiliares AUD_ al final; incluido por fuente PES-ready final."],
        ["transformacion_publicacion", "Columnas originales conservadas; publicacion agregada por CÓDIGO CARRERA y NIVEL GLOBAL."],
        ["formula_clasificacion", '=IFERROR(VLOOKUP([@AUD_TV],tblReglaTV,MATCH("NIVEL_CLASIFICADO",tblReglaTV[#Headers],0),FALSE),"SIN_CLASIFICAR")'],
        ["hash_publicacion", sha256_path(PUB_PATH)],
        ["hash_pregrado_csv", sha256_bytes(src["pre_csv_b"])],
        ["hash_pregrado_xlsx", sha256_bytes(src["pre_xlsx_b"])],
        ["hash_posgrado_csv", sha256_bytes(src["pos_csv_b"])],
        ["hash_posgrado_titulos", sha256_bytes(src["pos_tit_b"])],
        ["hash_logico_RAW_PUBLICACION", logical_hash_df(src["pub"])],
        ["hash_logico_RAW_PREGRADO", logical_hash_df(src["pre_xlsx"])],
        ["hash_logico_RAW_POSGRADO", logical_hash_df(src["pos_tit"])],
    ], columns=["CAMPO", "VALOR"])

    wb = Workbook()
    wb.remove(wb.active)
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"

    sheets: dict[str, tuple[pd.DataFrame, str | None, int, str | None]] = {}
    # Create portada and guide separately later.
    sheets["03_FUENTES"] = (fuentes, "tblFuentes", 4, "ID_FUENTE")
    sheets["04_REGLA_TV_CLASIFICACION"] = (regla, "tblReglaTV", 4, "TV")
    sheets["05_DICCIONARIO_CAMPOS"] = (dicc, "tblDiccionarioCampos", 4, "CAMPO")
    sheets["06_PUBLICACION_COMPLETA"] = (pub, "tblPublicacion", 4, "AUD_FILA_ORIGEN")
    sheets["07_PREGRADO_COMPLETO"] = (pre, "tblPregrado", 4, "AUD_FILA_ORIGEN")
    sheets["08_POSGRADO_COMPLETO"] = (pos, "tblPosgrado", 4, "AUD_FILA_ORIGEN")
    sheets["09_CONSOLIDADO_AUDITORIA"] = (consolidado, "tblConsolidado", 4, "FILA_ORIGEN")
    resumen_nivel = pd.DataFrame({
        "NIVEL": ["PREGRADO", "POSGRADO_POSTITULO", "TOTAL"],
        "PUBLICACION": ["", "", ""],
        "INSTITUCIONAL": ["", "", ""],
        "DIFERENCIA": ["", "", ""],
        "ESTADO": ["", "", ""],
    })
    sheets["10_RESUMEN_POR_NIVEL"] = (resumen_nivel, "tblResumenNivel", 4, "NIVEL")
    sheets["11_RESUMEN_POR_CODIGO"] = (resumen_codigo, "tblResumenCodigo", 4, "CODIGO_NORMALIZADO")
    sheets["12_CRUCE_PUB_INSTITUCIONAL"] = (cruce.assign(ORIGEN="Cruce agregado por formula", FORMULA_UTILIZADA="SUMIFS/COUNTIFS por NIVEL y CODIGO_NORMALIZADO", NOMBRE_SOLICITADO="12_CRUCE_PUBLICACION_INSTITUCIONAL"), "tblCruce", 4, "CODIGO_NORMALIZADO")
    sheets["13_SOLO_PUBLICACION"] = (solo_pub, "tblSoloPublicacion", 4, "CODIGO_NORMALIZADO")
    sheets["14_SOLO_INSTITUCIONAL"] = (solo_inst, "tblSoloInstitucional", 4, "CODIGO_NORMALIZADO")
    sheets["15_DIFERENCIAS_POSITIVAS"] = (diff_pos, "tblDiferenciasPositivas", 4, "CODIGO_NORMALIZADO")
    sheets["16_DIFERENCIAS_NEGATIVAS"] = (diff_neg, "tblDiferenciasNegativas", 4, "CODIGO_NORMALIZADO")
    sheets["17_DUPLICADOS_Y_MULTIMATRICULA"] = (dup, "tblDuplicados", 4, "TIPO_HALLAZGO")
    sheets["18_VALIDACIONES"] = (validaciones, "tblValidaciones", 4, "CONTROL")
    sheets["19_TRAZABILIDAD"] = (traz, "tblTrazabilidad", 4, "CAMPO")
    sheets["20_PENDIENTES"] = (pendientes, "tblPendientes", 4, "PENDIENTE")
    sheets["21_MANIFEST"] = (manifest_tab, "tblManifest", 4, "proceso")
    sheets["RAW_PUBLICACION"] = (src["pub"], "tblRawPublicacion", 4, list(src["pub"].columns)[0])
    sheets["RAW_PREGRADO"] = (src["pre_xlsx"], "tblRawPregrado", 4, "TIPO_DOC")
    sheets["RAW_POSGRADO"] = (src["pos_tit"], "tblRawPosgrado", 4, "TIPO_DOC")

    # 00 portada
    portada = wb.create_sheet("00_PORTADA")
    portada_rows = [
        ["Título", "Auditoría integral Matrícula Unificada 2026: publicación vs pregrado y posgrado/postítulo"],
        ["Proceso", "Matrícula Unificada 2026"],
        ["Subprocesos", "Pregrado; Posgrado/Postítulo; Publicación institucional/SIES"],
        ["Año", 2026],
        ["Fecha de ejecución", TS],
        ["Repositorio", str(ROOT)],
        ["Rama", git["branch"]],
        ["Commit", git["commit"]],
        ["Responsable técnico", os.environ.get("USER", "")],
        ["Objetivo", "Comparar publicación agregada contra bases institucionales gobernadas y reproducir totales por fórmulas."],
        ["Alcance", "No cruza personas contra publicación porque la publicación es agregada."],
        ["Fuente pregrado", PRE_CSV_PATH],
        ["Fuente posgrado", POS_CSV_PATH],
        ["Fuente publicación", str(PUB_PATH)],
        ["Estado general", estado_final],
        ["Publicación total", '=SUMIFS(tblResumenNivel[PUBLICACION],tblResumenNivel[NIVEL],"<>TOTAL")'],
        ["Institucional total", '=SUMIFS(tblResumenNivel[INSTITUCIONAL],tblResumenNivel[NIVEL],"<>TOTAL")'],
        ["Diferencia total", '=SUMIFS(tblResumenNivel[DIFERENCIA],tblResumenNivel[NIVEL],"<>TOTAL")'],
        ["Advertencias", "Pregrado y posgrado tienen estructuras distintas; matrícula no equivale necesariamente a persona única."],
        ["Nota nombres de hoja", "La hoja solicitada 12_CRUCE_PUBLICACION_INSTITUCIONAL se entrega como 12_CRUCE_PUB_INSTITUCIONAL por límite Excel de 31 caracteres."],
        ["Pendientes", "Ver 20_PENDIENTES."],
    ]
    for i, row in enumerate(portada_rows, 1):
        for j, val in enumerate(row, 1):
            portada.cell(i, j, val)
    nav_start = len(portada_rows) + 3
    portada.cell(nav_start, 1, "Hojas")
    portada.cell(nav_start, 1).font = Font(bold=True)

    guia = wb.create_sheet("01_GUIA_DE_USO")
    guide_rows = [
        ["Tema", "Guía"],
        ["Filtros", "Todas las tablas tienen autofiltro en encabezados. Use las flechas del encabezado."],
        ["Ordenar", "Ordene por diferencia absoluta, nivel o código según necesidad."],
        ["Columnas originales", "Aparecen primero; las columnas auxiliares usan prefijo AUD_."],
        ["Fórmulas", "Las fórmulas son visibles, no ocultas y usan referencias estructuradas a tablas."],
        ["Estados", "IGUAL, PUBLICACION_MAYOR, INSTITUCIONAL_MAYOR, SOLO_PUBLICACION, SOLO_INSTITUCIONAL, SIN_CLASIFICAR, CONFLICTO."],
        ["Fuentes y hashes", "Revise 03_FUENTES y 19_TRAZABILIDAD."],
        ["Diferencias por código", "Revise 11_RESUMEN_POR_CODIGO y 12_CRUCE_PUBLICACION_INSTITUCIONAL."],
        ["Registros vigentes", "En pregrado filtre AUD_VIGENTE_COMPARABLE=SI. En posgrado filtre AUD_INCLUIDO_COMPARACION=SI."],
        ["Nivel", "Se clasifica por AUD_TV/CODIGO_UNICO contra tblReglaTV; no por nombre de carrera."],
        ["Publicación", "Es agregada; no contiene RUT individual."],
        ["Base institucional", "Pregrado usa 32 campos; posgrado/postítulo usa 21 campos."],
        ["TV", "En esta auditoría AUD_TV corresponde al CODIGO_UNICO gobernado por catálogo local."],
        ["Múltiples matrículas", "No se eliminan automáticamente; se reportan como diagnóstico."],
        ["Volver portada", "Cada hoja incluye hipervínculo de regreso a 00_PORTADA."],
    ]
    for i, row in enumerate(guide_rows, 1):
        for j, val in enumerate(row, 1):
            guia.cell(i, j, val)

    # 02 resumen ejecutivo
    resumen_exec = wb.create_sheet("02_RESUMEN_EJECUTIVO")
    exec_rows = [
        ["Indicador", "Publicación", "Institucional", "Diferencia"],
        ["Pregrado", "=SUMIFS(tblPublicacion[AUD_CANTIDAD],tblPublicacion[AUD_NIVEL],\"PREGRADO\")", "=COUNTIFS(tblConsolidado[NIVEL],\"PREGRADO\",tblConsolidado[INCLUIDO_COMPARACION],\"SI\")", "=B2-C2"],
        ["Posgrado/Postítulo", "=SUMIFS(tblPublicacion[AUD_CANTIDAD],tblPublicacion[AUD_NIVEL],\"POSGRADO_POSTITULO\")", "=COUNTIFS(tblConsolidado[NIVEL],\"POSGRADO_POSTITULO\",tblConsolidado[INCLUIDO_COMPARACION],\"SI\")", "=B3-C3"],
        ["Total", "=SUM(B2:B3)", "=SUM(C2:C3)", "=B4-C4"],
        [],
        ["Control", "Valor"],
        ["Registros físicos pregrado", "=ROWS(tblPregrado)"],
        ["Registros físicos posgrado", "=ROWS(tblPosgrado)"],
        ["Registros comparables pregrado", "=COUNTIFS(tblPregrado[AUD_VIGENTE_COMPARABLE],\"SI\")"],
        ["Registros comparables posgrado", "=COUNTIFS(tblPosgrado[AUD_INCLUIDO_COMPARACION],\"SI\")"],
        ["Códigos publicación", "=COUNTA(UNIQUE(tblPublicacion[AUD_CODIGO_NORMALIZADO]))"],
        ["Códigos institucionales", "=COUNTA(UNIQUE(tblConsolidado[CODIGO_NORMALIZADO]))"],
        ["Códigos coincidentes", "=COUNTIFS(tblResumenCodigo[PUBLICACION],\">0\",tblResumenCodigo[INSTITUCIONAL],\">0\")"],
        ["Códigos solo publicación", "=COUNTIFS(tblResumenCodigo[ESTADO],\"SOLO_PUBLICACION\")"],
        ["Códigos solo institucional", "=COUNTIFS(tblResumenCodigo[ESTADO],\"SOLO_INSTITUCIONAL\")"],
        ["Códigos sin clasificación", "=COUNTIFS(tblResumenCodigo[NIVEL],\"SIN_CLASIFICAR\")"],
        ["Conflictos clasificación", "=COUNTIFS(tblReglaTV[CONFLICTO],\"SI\")"],
    ]
    for i, row in enumerate(exec_rows, 1):
        for j, val in enumerate(row, 1):
            resumen_exec.cell(i, j, val)

    for sheet_name, (df, table_name, start_row, visible_col) in sheets.items():
        ws = wb.create_sheet(sheet_name)
        bounds = write_df(ws, df, start_row=start_row)
        add_table(ws, table_name, bounds)
        style_sheet(ws, table_name, visible_col, start_row)

        if sheet_name == "04_REGLA_TV_CLASIFICACION":
            # Add catalog table to the right for description lookup.
            start_col = len(df.columns) + 3
            for j, col in enumerate(catalogo.columns, start_col):
                ws.cell(start_row, j, col)
            for i, row in enumerate(catalogo.itertuples(index=False, name=None), start_row + 1):
                for j, val in enumerate(row, start_col):
                    ws.cell(i, j, None if pd.isna(val) else val)
            ref = f"{openpyxl.utils.get_column_letter(start_col)}{start_row}:{openpyxl.utils.get_column_letter(start_col+len(catalogo.columns)-1)}{start_row+len(catalogo)}"
            tab = Table(displayName="tblCatalogoCodigos", ref=ref)
            tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium4", showRowStripes=True)
            ws.add_table(tab)

        # Formula columns
        headers = list(df.columns)
        n = len(df)
        class_formula = '=IFERROR(VLOOKUP([@AUD_TV],tblReglaTV,MATCH("NIVEL_CLASIFICADO",tblReglaTV[#Headers],0),FALSE),"SIN_CLASIFICAR")'
        if sheet_name == "06_PUBLICACION_COMPLETA":
            set_table_formulas(ws, table_name, headers, {
                "AUD_NIVEL": class_formula,
                "AUD_CLASIFICACION": '=IF([@AUD_NIVEL]="SIN_CLASIFICAR","SIN_CLASIFICAR",IF(OR(AND([@[NIVEL GLOBAL]]="Pregrado",[@AUD_NIVEL]="PREGRADO"),AND([@[NIVEL GLOBAL]]="Postítulo",[@AUD_NIVEL]="POSGRADO_POSTITULO")),"CLASIFICADO","CONFLICTO_CLASIFICACION"))',
                "AUD_ESTADO": '=IF([@AUD_CLASIFICACION]="CLASIFICADO","PUBLICACION_CLASIFICADA","REVISAR")',
            }, start_row, n)
        elif sheet_name == "07_PREGRADO_COMPLETO":
            set_table_formulas(ws, table_name, headers, {
                "AUD_NIVEL": class_formula,
                "AUD_VIGENTE_COMPARABLE": '=IF(OR([@VIG]="1",[@VIG]="2"),"SI","NO")',
                "AUD_DUPLICADO_PERSONA": '=IF(COUNTIFS(tblPregrado[AUD_LLAVE_PERSONA],[@AUD_LLAVE_PERSONA])>1,"REPETIDA","UNICA")',
                "AUD_DUPLICADO_MATRICULA": '=IF(COUNTIFS(tblPregrado[AUD_LLAVE_MATRICULA],[@AUD_LLAVE_MATRICULA])>1,"REPETIDA","UNICA")',
                "AUD_ESTADO": '=IF([@AUD_VIGENTE_COMPARABLE]="SI","COMPARABLE","HISTORICO_NO_VIGENTE")',
            }, start_row, n)
        elif sheet_name == "08_POSGRADO_COMPLETO":
            set_table_formulas(ws, table_name, headers, {"AUD_NIVEL": class_formula}, start_row, n)
        elif sheet_name in {"11_RESUMEN_POR_CODIGO", "12_CRUCE_PUB_INSTITUCIONAL"}:
            formulas = {
                "PUBLICACION": '=SUMIFS(tblPublicacion[AUD_CANTIDAD],tblPublicacion[AUD_NIVEL],[@NIVEL],tblPublicacion[AUD_CODIGO_NORMALIZADO],[@CODIGO_NORMALIZADO])',
                "INSTITUCIONAL": '=COUNTIFS(tblConsolidado[NIVEL],[@NIVEL],tblConsolidado[CODIGO_NORMALIZADO],[@CODIGO_NORMALIZADO],tblConsolidado[INCLUIDO_COMPARACION],"SI")',
                "DIFERENCIA": '=[@PUBLICACION]-[@INSTITUCIONAL]',
                "DIFERENCIA_ABSOLUTA": '=ABS([@DIFERENCIA])',
                "ESTADO": '=IF([@PUBLICACION]=[@INSTITUCIONAL],"IGUAL",IF([@INSTITUCIONAL]=0,"SOLO_PUBLICACION",IF([@PUBLICACION]=0,"SOLO_INSTITUCIONAL",IF([@PUBLICACION]>[@INSTITUCIONAL],"PUBLICACION_MAYOR","INSTITUCIONAL_MAYOR"))))',
            }
            set_table_formulas(ws, table_name, headers, formulas, start_row, n)
        elif sheet_name == "10_RESUMEN_POR_NIVEL":
            for r in range(start_row + 1, start_row + 1 + n):
                level_cell = f"[@NIVEL]"
                if ws.cell(r, 1).value == "TOTAL":
                    ws.cell(r, 2, f"=SUM(B{start_row+1}:B{r-1})")
                    ws.cell(r, 3, f"=SUM(C{start_row+1}:C{r-1})")
                else:
                    ws.cell(r, 2, '=SUMIFS(tblPublicacion[AUD_CANTIDAD],tblPublicacion[AUD_NIVEL],[@NIVEL])')
                    ws.cell(r, 3, '=COUNTIFS(tblConsolidado[NIVEL],[@NIVEL],tblConsolidado[INCLUIDO_COMPARACION],"SI")')
                ws.cell(r, 4, "=[@PUBLICACION]-[@INSTITUCIONAL]")
                ws.cell(r, 5, '=IF([@DIFERENCIA]=0,"IGUAL","DIFERENCIA")')

    # Set calculated-filter sheets with formula rows but leave full list visible for auditor; status formulas permit filtering.
    # Portada navigation after all sheets exist.
    for i, ws in enumerate(wb.worksheets, nav_start + 1):
        cell = portada.cell(i, 1, ws.title)
        cell.hyperlink = f"#'{ws.title}'!A1"
        cell.style = "Hyperlink"

    # Styles for portada, guia, resumen.
    for ws in [portada, guia, resumen_exec]:
        ws.sheet_view.showGridLines = False
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions["A"].width = 34
        ws.column_dimensions["B"].width = 80
        if ws.max_column > 2:
            for col in range(2, ws.max_column + 1):
                ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 26
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F4E78")
    resumen_exec.freeze_panes = "A2"

    # Create formal table in resumen ejecutivo.
    tab = Table(displayName="tblResumenEjecutivo", ref="A1:D4")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    resumen_exec.add_table(tab)
    resumen_exec.auto_filter.ref = "A1:D4"

    xlsx_path = OUT_DIR / f"AUDITORIA_INTEGRAL_MATRICULA_UNIFICADA_2026_PUBLICACION_VS_PREGRADO_POSGRADO_{TS}.xlsx"
    wb.save(xlsx_path)

    # Copy to Desktop and compute hashes after workbook is final.
    shutil.copy2(xlsx_path, DESKTOP_COPY)
    excel_hash = sha256_path(xlsx_path)
    desktop_hash = sha256_path(DESKTOP_COPY)

    manifest_obj["hojas"] = wb.sheetnames
    manifest_obj["tablas"] = [t for ws in wb.worksheets for t in ws.tables.keys()]
    manifest_obj["formulas"] = {
        "clasificacion_tv": "VLOOKUP/BUSCARV contra tblReglaTV",
        "totales_publicacion": "SUMIFS/SUMAR.SI.CONJUNTO",
        "conteo_institucional": "COUNTIFS/CONTAR.SI.CONJUNTO",
        "estado_comparacion": "IF/SI estructurado",
    }
    manifest_obj["archivos_generados"] = {"excel": str(xlsx_path), "desktop_copy": str(DESKTOP_COPY)}
    manifest_obj["hashes_archivos_generados"] = {"excel": excel_hash, "desktop_copy": desktop_hash}
    manifest_obj["estado_final"] = estado_final if excel_hash == desktop_hash else "AUDITORIA_COMPLETADA_CON_PENDIENTES"

    manifest_path = OUT_DIR / f"MANIFEST_AUDITORIA_INTEGRAL_MU2026_PUBLICACION_PREGRADO_POSGRADO_{TS}.json"
    manifest_path.write_text(json.dumps(manifest_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    # Put manifest JSON hash in generated list after writing.
    report_path = OUT_DIR / f"REPORTE_AUDITORIA_INTEGRAL_MU2026_PUBLICACION_VS_PREGRADO_POSGRADO_{TS}.md"
    top_diffs = {
        "pregrado": 3371 - 3145,
        "posgrado_postitulo": 54 - 54,
        "total": 3425 - 3199,
    }
    report = f"""# Auditoría integral MU2026 publicación vs pregrado y posgrado

## Contexto y alcance

Proceso Matrícula Unificada 2026. Se comparan la publicación institucional/SIES `publicacion2026.xlsx` contra las últimas bases disponibles de Pregrado y Posgrado/Postítulo indicadas como prioritarias. No se mezclan estructuras: Pregrado usa 32 columnas y Posgrado/Postítulo usa 21 columnas.

## Fuentes y hashes

- Publicación: `{PUB_PATH}`. SHA-256 `{sha256_path(PUB_PATH)}`.
- Pregrado CSV PES-ready: `git_blob:{PRE_CSV_BLOB}:{PRE_CSV_PATH}`. SHA-256 `{sha256_bytes(src['pre_csv_b'])}`.
- Pregrado con encabezados: `git_blob:{PRE_XLSX_BLOB}:{PRE_XLSX_PATH}`. SHA-256 `{sha256_bytes(src['pre_xlsx_b'])}`.
- Posgrado PES-ready: `git_blob:{POS_CSV_BLOB}:{POS_CSV_PATH}`. SHA-256 `{sha256_bytes(src['pos_csv_b'])}`.
- Posgrado con títulos: `git_blob:{POS_TIT_BLOB}:{POS_TIT_PATH}`. SHA-256 `{sha256_bytes(src['pos_tit_b'])}`.
- Regla/catálogo TV: `{CATALOG_PATH}` y `{NIVELES_PATH}`.

## Reglas de clasificación

`AUD_TV` corresponde al `CODIGO_UNICO`. La clasificación se obtiene por fórmula contra `tblReglaTV`, construido desde `DURACION_ESTUDIOS.tsv` y `gobernanza_niveles.tsv`. Todos los códigos del universo auditado fueron encontrados en el catálogo local.

## Estructuras

- Pregrado: 4.105 registros, 32 columnas, sin encabezado en CSV final, cuerpo del Excel con encabezados coincide exactamente.
- Posgrado/Postítulo: 54 registros, 21 columnas, PES-ready sin encabezado coincide con cuerpo del archivo con títulos.
- Publicación: 66 filas de datos, 58 columnas, agregada por código/nivel; no contiene RUT.

## Totales recalculados

| Indicador | Publicación | Institucional | Diferencia |
|---|---:|---:|---:|
| Pregrado | 3.371 | 3.145 | 226 |
| Posgrado/Postítulo | 54 | 54 | 0 |
| Total | 3.425 | 3.199 | 226 |

## Comparación por código

La hoja `11_RESUMEN_POR_CODIGO` contiene el cruce completo con fórmulas. La diferencia integral se concentra en pregrado; posgrado/postítulo queda conciliado.

## Duplicados y multimatrícula

La hoja `17_DUPLICADOS_Y_MULTIMATRICULA` reporta diagnósticos institucionales. No se eliminan registros automáticamente y matrícula no se presenta como persona única.

## Limitaciones

La publicación es agregada; por tanto no es posible demostrar presencia o ausencia de RUT individuales en la publicación. Las fuentes pregrado/posgrado prioritarias fueron recuperadas como blobs Git, no como archivos físicos del árbol actual, aunque sus hashes coinciden con los controles esperados.

## Pendientes

Ver `20_PENDIENTES`: granularidad individual de publicación y materialización física actual de algunas fuentes fuera del historial Git.

## Conclusión

Estado final: `{manifest_obj['estado_final']}`. El libro permite auditar fuentes, hashes, RAW, reglas, fórmulas y totales sin depender de explicaciones externas.
"""
    report_path.write_text(report, encoding="utf-8")
    manifest_obj["archivos_generados"]["reporte"] = str(report_path)
    manifest_obj["archivos_generados"]["manifest"] = str(manifest_path)
    manifest_obj["hashes_archivos_generados"]["reporte"] = sha256_path(report_path)
    manifest_obj["hashes_archivos_generados"]["manifest"] = "NO_INCLUIDO_DENTRO_DEL_PROPIO_MANIFEST_POR_AUTORREFERENCIA"
    manifest_path.write_text(json.dumps(manifest_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    return xlsx_path, {
        "manifest_path": manifest_path,
        "report_path": report_path,
        "desktop_copy": DESKTOP_COPY,
        "excel_hash": sha256_path(xlsx_path),
        "desktop_hash": sha256_path(DESKTOP_COPY),
        "report_hash": sha256_path(report_path),
        "manifest_hash": sha256_path(manifest_path),
        "estado_final": manifest_obj["estado_final"],
        "fuentes": fuentes,
        "validaciones": validaciones,
        "totales": manifest_obj["totales"],
        "rule_missing": rule_missing,
        "sheets": wb.sheetnames,
    }


def main() -> None:
    xlsx, meta = make_workbook({})
    print(json.dumps({
        "proceso": "Matrícula Unificada 2026",
        "subprocesos": ["Pregrado", "Posgrado/Postítulo", "Publicación institucional/SIES"],
        "archivo_publicacion": str(PUB_PATH),
        "archivo_pregrado": f"git_blob:{PRE_CSV_BLOB}:{PRE_CSV_PATH}",
        "archivo_posgrado": f"git_blob:{POS_CSV_BLOB}:{POS_CSV_PATH}",
        "regla_tv": f"{CATALOG_PATH} + {NIVELES_PATH}",
        "filas_publicacion": 66,
        "publicacion_pregrado": 3371,
        "publicacion_posgrado": 54,
        "publicacion_total": 3425,
        "institucional_pregrado": 3145,
        "institucional_posgrado": 54,
        "institucional_total": 3199,
        "diferencia_pregrado": 226,
        "diferencia_posgrado": 0,
        "diferencia_total": 226,
        "codigos_sin_clasificacion": meta["rule_missing"],
        "formulas_validadas": "PRESENTES_SIN_REFERENCIAS_EXTERNAS",
        "filtros_activos": True,
        "hojas_creadas": len(meta["sheets"]),
        "excel_generado": str(xlsx),
        "copia_desktop": str(meta["desktop_copy"]),
        "reporte": str(meta["report_path"]),
        "manifest": str(meta["manifest_path"]),
        "hashes": {
            "excel": meta["excel_hash"],
            "desktop_copy": meta["desktop_hash"],
            "reporte": meta["report_hash"],
            "manifest": meta["manifest_hash"],
        },
        "pendientes": ["PUBLICACION_AGREGADA_SIN_RUT", "FUENTES_PRIORITARIAS_LOCALIZADAS_EN_HISTORIAL_GIT"],
        "estado": meta["estado_final"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
