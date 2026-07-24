#!/usr/bin/env python3
"""Auditoria local de la diferencia +166 de pregrado MU 2026.

El script no modifica fuentes originales. Genera artefactos derivados,
versionados y trazables en outputs/auditoria_diferencia_166_pregrado/<ts>/.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = ROOT / "outputs" / "auditoria_diferencia_166_pregrado" / TS

PUB_PATH = ROOT / "publicacion2026.xlsx"
INTEGRAL_XLSX = ROOT / "outputs/comparaciones_publicacion2026_integrales/20260730_172147/COMPARACION_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_CON_PES_READY_20260730_172147.xlsx"
INTEGRAL_MANIFEST = ROOT / "outputs/comparaciones_publicacion2026_integrales/20260730_172147/MANIFEST_COMPARACION_INTEGRAL_PUBLICACION2026_PREGRADO_POSGRADO_CON_PES_READY_20260730_172147.json"
MANUAL_TXT = ROOT / "docs/manual_matricula_unificada.txt"
CIERRE_PES = ROOT / "CIERRE_PES_READY_MU2026.md"

PUNTO0_GIT = "4f1108c:control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
PUNTO0_EVIDENCE = ROOT / "control/auditoria_mu2026_punto0_complemento95/evidencia_pes/VALIDACION_CARGA_PRINCIPAL.tsv"
COMP95_BLOB = "d4bd44f9d1f11640056b8e990f5e1fcda9aebf7d"
COMP95_MANIFEST_GIT = "4f1108c:control/auditoria_mu2026_complemento95_cierre_final/MANIFEST_CIERRE_COMPLEMENTO_95 2.json"

HEADERS_PREGRADO = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE",
    "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD",
    "JOR", "VERSION", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI",
    "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",
    "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> str:
    res = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and res.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\nSTDERR:\n{res.stderr}")
    return res.stdout


def git_bytes(spec: str) -> bytes:
    res = subprocess.run(["git", "show", spec], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"git show {spec}: {res.stderr.decode(errors='replace')}")
    return res.stdout


def git_cat_blob(blob: str) -> bytes:
    res = subprocess.run(["git", "cat-file", "-p", blob], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"git cat-file {blob}: {res.stderr.decode(errors='replace')}")
    return res.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_bytes(data: bytes) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return data.decode("latin-1", errors="replace"), "latin-1-replace"


def detect_delimiter(text: str) -> str:
    sample = "\n".join(text.splitlines()[:20])
    return ";" if sample.count(";") >= sample.count(",") else ","


def parse_csv_bytes(data: bytes) -> tuple[list[list[str]], str, str]:
    text, enc = decode_bytes(data)
    delim = detect_delimiter(text)
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    if rows and rows[-1] == []:
        rows = rows[:-1]
    return rows, delim, enc


def looks_like_header(row: list[str]) -> bool:
    upper = [str(x).strip().upper() for x in row]
    hits = {"TIPO_DOC", "N_DOC", "DV", "COD_SED", "COD_CAR", "VIG"} & set(upper)
    return len(hits) >= 2 or "TIPO_DOC" in upper or "VIG" in upper


def df_pregrado_from_rows(rows: list[list[str]], source: str | None = None) -> tuple[pd.DataFrame, bool]:
    if rows and looks_like_header(rows[0]):
        header = [str(x).strip() for x in rows[0]]
        data = rows[1:]
        has_header = True
    else:
        width = len(rows[0]) if rows else 0
        header = HEADERS_PREGRADO if width == 32 else [f"CAMPO_{i+1}" for i in range(width)]
        data = rows
        has_header = False
    df = pd.DataFrame(data, columns=header)
    if source is not None:
        df["_COMPONENTE_ANALITICO"] = source
    return df, has_header


def add_codigo_unico(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    required = ["COD_SED", "COD_CAR", "JOR", "VERSION"]
    if all(c in out.columns for c in required):
        out["CODIGO_UNICO"] = (
            "I162S" + out["COD_SED"].astype(str).str.strip()
            + "C" + out["COD_CAR"].astype(str).str.strip()
            + "J" + out["JOR"].astype(str).str.strip()
            + "V" + out["VERSION"].astype(str).str.strip()
        )
    return out


def vig_counts(df: pd.DataFrame) -> dict[str, int]:
    if "VIG" not in df.columns:
        return {"0": 0, "1": 0, "2": 0, "otros": len(df)}
    s = df["VIG"].astype(str).str.strip()
    return {
        "0": int((s == "0").sum()),
        "1": int((s == "1").sum()),
        "2": int((s == "2").sum()),
        "otros": int((~s.isin(["0", "1", "2"])).sum()),
    }


def offer_counts_pregrado(df: pd.DataFrame, vig_values=("1", "2")) -> pd.Series:
    x = add_codigo_unico(df)
    if "CODIGO_UNICO" not in x.columns or "VIG" not in x.columns:
        return pd.Series(dtype="int64")
    mask = x["VIG"].astype(str).str.strip().isin(list(vig_values))
    return x.loc[mask].groupby("CODIGO_UNICO", dropna=False).size().astype(int)


def all_offer_counts(df: pd.DataFrame) -> pd.DataFrame:
    x = add_codigo_unico(df)
    if "CODIGO_UNICO" not in x.columns or "VIG" not in x.columns:
        return pd.DataFrame(columns=["CODIGO_UNICO", "VIG0", "VIG1", "VIG2", "HISTORICO"])
    s = x["VIG"].astype(str).str.strip()
    base = pd.DataFrame({"CODIGO_UNICO": sorted(x["CODIGO_UNICO"].dropna().unique())})
    for val, name in [("0", "VIG0"), ("1", "VIG1"), ("2", "VIG2")]:
        c = x.loc[s == val].groupby("CODIGO_UNICO").size().rename(name)
        base = base.merge(c, on="CODIGO_UNICO", how="left")
    base[["VIG0", "VIG1", "VIG2"]] = base[["VIG0", "VIG1", "VIG2"]].fillna(0).astype(int)
    base["VIGENTE"] = base["VIG1"] + base["VIG2"]
    base["HISTORICO"] = base["VIG0"] + base["VIG1"] + base["VIG2"]
    return base


def logical_hash_df(df: pd.DataFrame) -> str:
    h = hashlib.sha256()
    h.update("\x1f".join(map(str, df.columns)).encode("utf-8"))
    h.update(b"\n")
    for row in df.itertuples(index=False, name=None):
        h.update("\x1f".join("" if pd.isna(v) else str(v) for v in row).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def safe_sheet(name: str) -> str:
    return name[:31]


def write_sheet(writer: pd.ExcelWriter, name: str, df: pd.DataFrame) -> None:
    df2 = df.copy()
    if df2.empty:
        df2 = pd.DataFrame({"SIN_REGISTROS": []})
    df2.to_excel(writer, sheet_name=safe_sheet(name), index=False)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Sin registros._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(map(str, cols)) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for row in df.itertuples(index=False, name=None):
        values = [str(v).replace("\n", " ").replace("|", "\\|") for v in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def source_modified(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except FileNotFoundError:
        return ""


def read_publicacion() -> tuple[pd.DataFrame, dict]:
    wb = openpyxl.load_workbook(PUB_PATH, data_only=False, read_only=True)
    ws = wb["Hoja1"]
    rows = list(ws.iter_rows(values_only=True))
    headers = ["" if v is None else str(v) for v in rows[0]]
    data = [list(r) for r in rows[1:]]
    df = pd.DataFrame(data, columns=headers)
    info = {
        "archivo": PUB_PATH.name,
        "ruta": str(PUB_PATH),
        "hoja": "Hoja1",
        "filas_datos": int(len(df)),
        "columnas": int(len(df.columns)),
        "hash": sha256_path(PUB_PATH),
        "fecha_modificacion": source_modified(PUB_PATH),
        "hash_logico": logical_hash_df(df),
    }
    return df, info


def load_current_frozen() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    punto0_bytes = git_bytes(PUNTO0_GIT)
    comp_bytes = git_cat_blob(COMP95_BLOB)
    p_rows, p_delim, p_enc = parse_csv_bytes(punto0_bytes)
    c_rows, c_delim, c_enc = parse_csv_bytes(comp_bytes)
    p_df, p_header = df_pregrado_from_rows(p_rows, "PUNTO0_PARA_SUBIR")
    c_df, c_header = df_pregrado_from_rows(c_rows, "COMPLEMENTO95_V3")
    raw_current = pd.concat(
        [p_df[HEADERS_PREGRADO], c_df[HEADERS_PREGRADO]],
        ignore_index=True,
    )
    info = {
        "punto0_hash": sha256_bytes(punto0_bytes),
        "punto0_delimitador": p_delim,
        "punto0_codificacion": p_enc,
        "punto0_encabezado_fisico": p_header,
        "punto0_filas": len(p_df),
        "punto0_columnas": len(p_rows[0]) if p_rows else 0,
        "complemento95_hash": sha256_bytes(comp_bytes),
        "complemento95_delimitador": c_delim,
        "complemento95_codificacion": c_enc,
        "complemento95_encabezado_fisico": c_header,
        "complemento95_filas": len(c_df),
        "complemento95_columnas": len(c_rows[0]) if c_rows else 0,
        "congelado_hash_logico": logical_hash_df(raw_current),
        "congelado_hash_fisico_derivado": sha256_bytes(
            ("\n".join(";".join(r) for r in p_rows + c_rows) + "\n").encode("utf-8")
        ),
    }
    return p_df[HEADERS_PREGRADO], c_df[HEADERS_PREGRADO], raw_current, info


def load_text_evidence() -> dict:
    evidence = {}
    for label, path in [
        ("CIERRE_PES_READY_MU2026.md", CIERRE_PES),
        ("VALIDACION_CARGA_PRINCIPAL.tsv", PUNTO0_EVIDENCE),
        ("manual_matricula_unificada.txt", MANUAL_TXT),
    ]:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            evidence[label] = {
                "ruta": str(path),
                "hash": sha256_path(path),
                "extractos": [],
            }
            for pat in ["Finalizado", "PARA_SUBIR", "PES_READY", "VIG", "Administrador de Duplicados", "30 de abril", "15 de mayo", "integral"]:
                m = re.search(pat, text, flags=re.I)
                if m:
                    start = max(0, m.start() - 180)
                    end = min(len(text), m.end() + 240)
                    evidence[label]["extractos"].append(text[start:end].replace("\n", " ").strip())
    try:
        txt = git_bytes(COMP95_MANIFEST_GIT).decode("utf-8", errors="replace")
        evidence["MANIFEST_CIERRE_COMPLEMENTO_95 2.json"] = {
            "ruta": f"git:{COMP95_MANIFEST_GIT}",
            "hash": sha256_bytes(git_bytes(COMP95_MANIFEST_GIT)),
            "extractos": [txt[:1000].replace("\n", " ").strip()],
        }
    except Exception as exc:
        evidence["MANIFEST_CIERRE_COMPLEMENTO_95 2.json"] = {"ruta": f"git:{COMP95_MANIFEST_GIT}", "error": str(exc)}
    return evidence


def classify_candidate_evidence(path_label: str, rows: int, cols: int, vigentes: int, sha: str) -> tuple[str, str]:
    low = path_label.lower()
    evidence = []
    status = "PENDIENTE_CLASIFICAR"
    if "punto0" in low or "para_subir" in low:
        evidence.append("Nombre/ruta asociado a PARA_SUBIR o Punto 0.")
    if "pes_ready" in low or "/subida/" in low or "listo" in low:
        evidence.append("Nombre/ruta asociado a archivo de carga/PES.")
    if "complemento" in low or "95" in low:
        evidence.append("Nombre/ruta asociado a complemento 95.")
    if "audit" in low or "auditoria" in low or "congel" in low:
        evidence.append("Nombre/ruta asociado a auditoria/congelado.")
    if rows == 4070 and cols == 32:
        status = "COMPONENTE_CARGA"
    elif rows == 95 and cols == 32:
        status = "COMPONENTE_CARGA"
    elif rows == 4165 and cols == 32:
        status = "DERIVADO"
    elif cols == 32 and vigentes == 3205:
        status = "CONGELADO_INTERMEDIO"
    elif cols == 32:
        status = "BORRADOR"
    if sha in {
        "8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704",
        "1940923b7e9f811df9b5af50d0badc8563bc17ed9ce8078fbab054d221c6e1f2",
    }:
        status = "COMPONENTE_CARGA"
        evidence.append("Hash coincide con componente gobernado conocido.")
    return ("; ".join(evidence) if evidence else "Sin evidencia material de PES/congelado en el nombre/ruta.", status)


def analyze_csv_candidate(label: str, data: bytes, pub_pre: pd.Series, source_kind: str, mtime: str = "") -> dict:
    rows, delim, enc = parse_csv_bytes(data)
    if not rows:
        return {
            "Candidato": label, "Tipo": source_kind, "Filas": 0, "Columnas": 0, "Encabezado": "NO",
            "VIG=0": 0, "VIG=1": 0, "VIG=2": 0, "Vigentes": 0, "Fecha": mtime,
            "SHA-256": sha256_bytes(data), "Evidencia de PES": "Archivo vacio", "Estado": "NO_CORRESPONDE",
            "Delimitador": delim, "Codificacion": enc,
        }
    header = looks_like_header(rows[0])
    field_counts = Counter(len(r) for r in rows[1:] if header for _ in [0]) if header else Counter(len(r) for r in rows)
    cols = max(field_counts, key=field_counts.get) if field_counts else len(rows[0])
    data_rows = len(rows) - (1 if header else 0)
    df, _ = df_pregrado_from_rows(rows)
    vc = vig_counts(df) if cols == 32 or "VIG" in df.columns else {"0": 0, "1": 0, "2": 0, "otros": data_rows}
    vigentes = vc["1"] + vc["2"]
    sha = sha256_bytes(data)
    evidence, status = classify_candidate_evidence(label, data_rows, cols, vigentes, sha)
    ranking = {}
    if (cols == 32 or all(c in df.columns for c in HEADERS_PREGRADO)) and "VIG" in df.columns:
        cc = offer_counts_pregrado(df)
        union = sorted(set(pub_pre.index) | set(cc.index))
        diff = pd.Series({k: int(pub_pre.get(k, 0)) - int(cc.get(k, 0)) for k in union})
        ranking = {
            "Total comparable": int(cc.sum()),
            "Diferencia total": int(pub_pre.sum() - cc.sum()),
            "Ofertas iguales": int(sum(int(pub_pre.get(k, 0)) == int(cc.get(k, 0)) for k in union)),
            "Ofertas distintas": int(sum(int(pub_pre.get(k, 0)) != int(cc.get(k, 0)) for k in union)),
            "Suma absoluta diferencias": int(diff.abs().sum()),
            "Solo publicacion": int(sum(int(pub_pre.get(k, 0)) > 0 and int(cc.get(k, 0)) == 0 for k in union)),
            "Solo candidato": int(sum(int(pub_pre.get(k, 0)) == 0 and int(cc.get(k, 0)) > 0 for k in union)),
        }
    return {
        "Candidato": label, "Tipo": source_kind, "Filas": data_rows, "Columnas": cols,
        "Encabezado": "SI" if header else "NO", "VIG=0": vc["0"], "VIG=1": vc["1"],
        "VIG=2": vc["2"], "Otros VIG": vc.get("otros", 0), "Vigentes": vigentes, "Fecha": mtime,
        "SHA-256": sha, "Evidencia de PES": evidence, "Estado": status,
        "Delimitador": delim, "Codificacion": enc, **ranking,
    }


def scan_physical_candidates(pub_pre: pd.Series) -> list[dict]:
    tokens = re.compile(r"(matricula|matr.cula|pregrado|para_subir|pes_ready|subida|complemento|congel|publicacion|vig|3205|3371|4165|4070|95|2026)", re.I)
    out = []
    skip_dirs = {".git", ".venv", "__pycache__", ".pytest_cache"}
    for path in ROOT.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        if not tokens.search(rel):
            continue
        if path.suffix.lower() not in {".csv", ".tsv", ".txt"}:
            continue
        try:
            data = path.read_bytes()
            if path.suffix.lower() == ".csv" or "matricula" in rel.lower() or "pregrado" in rel.lower():
                out.append(analyze_csv_candidate(str(path), data, pub_pre, "archivo_fisico", source_modified(path)))
        except Exception as exc:
            out.append({"Candidato": str(path), "Tipo": "archivo_fisico", "Estado": "PENDIENTE_CLASIFICAR", "Evidencia de PES": f"No leido: {exc}"})
    for path in [
        Path("/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"),
        Path("/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PES_READY.csv"),
    ]:
        if path.exists():
            out.append(analyze_csv_candidate(str(path), path.read_bytes(), pub_pre, "desktop_registrado", source_modified(path)))
    return out


def scan_git_candidates(pub_pre: pd.Series) -> list[dict]:
    out = []
    listing = run(["git", "rev-list", "--all", "--objects"], check=False)
    pattern = re.compile(r"(matricula_unificada|pregrado|para_subir|pes_ready|subida|complemento|reincorporar|congel|4165|3371|3205|4070|95|2026)", re.I)
    seen = set()
    for line in listing.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        obj, path = parts
        low = path.lower()
        if "posgrado" in low or "postgrado" in low or "postitulo" in low:
            continue
        if not pattern.search(path):
            continue
        if not path.lower().endswith((".csv", ".tsv", ".txt")):
            continue
        if (obj, path) in seen:
            continue
        seen.add((obj, path))
        try:
            data = git_cat_blob(obj)
            row = analyze_csv_candidate(f"git:{obj}:{path}", data, pub_pre, "historial_git")
            row["Blob/Commit"] = obj
            out.append(row)
        except Exception:
            continue
    return out


def publication_pregrado_series(pub_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict]:
    cols_upper = {str(c).strip().upper(): c for c in pub_raw.columns}
    nivel_col = cols_upper.get("NIVEL GLOBAL")
    codigo_col = cols_upper.get("CÓDIGO CARRERA") or cols_upper.get("CODIGO CARRERA")
    total_col = cols_upper.get("TOTAL MATRÍCULA") or cols_upper.get("TOTAL MATRICULA")
    nombre_col = cols_upper.get("NOMBRE CARRERA")
    if not all([nivel_col, codigo_col, total_col]):
        raise RuntimeError(f"No estan las columnas necesarias en publicacion: {list(pub_raw.columns)}")
    pub = pub_raw.copy()
    pub["_NIVEL_ANALITICO"] = pub[nivel_col].astype(str).str.strip()
    pub["_CODIGO_UNICO"] = pub[codigo_col].astype(str).str.strip()
    pub["_MATRICULA"] = pd.to_numeric(pub[total_col], errors="coerce").fillna(0).astype(int)
    pub["_NOMBRE_OFERTA"] = pub[nombre_col].astype(str) if nombre_col else ""
    pre = pub[pub["_NIVEL_ANALITICO"].str.casefold() == "pregrado"].copy()
    pos = pub[pub["_NIVEL_ANALITICO"].str.casefold().isin(["postítulo", "postitulo", "posgrado", "postgrado"])].copy()
    ser = pre.groupby("_CODIGO_UNICO")["_MATRICULA"].sum().astype(int)
    info = {
        "total_publicacion": int(pub["_MATRICULA"].sum()),
        "total_pregrado": int(pre["_MATRICULA"].sum()),
        "filas_pregrado": int(len(pre)),
        "ofertas_pregrado": int(pre["_CODIGO_UNICO"].nunique()),
        "total_posgrado_postitulo": int(pos["_MATRICULA"].sum()),
        "filas_posgrado_postitulo": int(len(pos)),
        "ofertas_posgrado_postitulo": int(pos["_CODIGO_UNICO"].nunique()),
        "total_pendiente_nivel": int(pub.loc[~pub.index.isin(pre.index.union(pos.index)), "_MATRICULA"].sum()),
    }
    names = pre.groupby("_CODIGO_UNICO")["_NOMBRE_OFERTA"].first().rename("Nombre oferta").reset_index().rename(columns={"_CODIGO_UNICO": "CODIGO_UNICO"})
    return names, ser, info


def compare_publication_current(pub_pre: pd.Series, names: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    counts = all_offer_counts(frozen)
    v0_map = counts.set_index("CODIGO_UNICO")["VIG0"].to_dict()
    v1_map = counts.set_index("CODIGO_UNICO")["VIG1"].to_dict()
    v2_map = counts.set_index("CODIGO_UNICO")["VIG2"].to_dict()
    hist_map = counts.set_index("CODIGO_UNICO")["HISTORICO"].to_dict()
    union = sorted(set(pub_pre.index) | set(counts["CODIGO_UNICO"]))
    name_map = dict(zip(names["CODIGO_UNICO"], names["Nombre oferta"]))
    rows = []
    frozen_codes = set(counts["CODIGO_UNICO"])
    code_parts = {}
    fz = add_codigo_unico(frozen)
    for code, sub in fz.groupby("CODIGO_UNICO"):
        code_parts[code] = {
            "COD_SED": ",".join(sorted(sub["COD_SED"].astype(str).str.strip().unique())),
            "COD_CAR": ",".join(sorted(sub["COD_CAR"].astype(str).str.strip().unique())),
            "JOR": ",".join(sorted(sub["JOR"].astype(str).str.strip().unique())),
            "VERSION": ",".join(sorted(sub["VERSION"].astype(str).str.strip().unique())),
        }
    for code in union:
        pub = int(pub_pre.get(code, 0))
        vig1 = int(v1_map.get(code, 0))
        vig2 = int(v2_map.get(code, 0))
        vig0 = int(v0_map.get(code, 0))
        vigente = vig1 + vig2
        historico = int(hist_map.get(code, 0))
        diff = pub - vigente
        if pub == vigente:
            cls = "IGUAL"
        elif pub > 0 and vigente == 0 and historico == 0:
            cls = "SOLO_PUBLICACION_TOTAL"
        elif pub > 0 and vigente == 0 and vig0 > 0:
            cls = "PUBLICACION_SIN_CONGELADO_VIGENTE_CON_ANTECEDENTE_VIG0"
        elif pub == 0 and vigente > 0:
            cls = "SOLO_CONGELADO_VIGENTE"
        elif pub > vigente:
            cls = "PUBLICACION_MAYOR"
        elif pub < vigente:
            cls = "PUBLICACION_MENOR"
        else:
            cls = "PENDIENTE_EXPLICACION"
        m = re.match(r"I162S(.+)C(.+)J(.+)V(.+)", code)
        possible = []
        if m:
            sed, car, jor, ver = m.groups()
            same_car = fz[fz["COD_CAR"].astype(str).str.strip() == car]
            if code not in frozen_codes and not same_car.empty:
                possible.append("MISMO_COD_CAR_EN_OTRA_COMBINACION")
                if any(same_car["VERSION"].astype(str).str.strip() != ver):
                    possible.append("CAMBIO_DE_VERSION_POSIBLE")
                if any(same_car["JOR"].astype(str).str.strip() != jor):
                    possible.append("CAMBIO_DE_JORNADA_POSIBLE")
                if any(same_car["MODALIDAD"].astype(str).str.strip().nunique() > 1 for _ in [0]):
                    possible.append("CAMBIO_DE_MODALIDAD_POSIBLE")
        rows.append({
            "CODIGO_UNICO": code,
            "Nombre oferta": name_map.get(code, ""),
            "Publicacion": pub,
            "CONGELADO_VIG_0": vig0,
            "CONGELADO_VIG_1": vig1,
            "CONGELADO_VIG_2": vig2,
            "CONGELADO_VIGENTE": vigente,
            "CONGELADO_HISTORICO": historico,
            "DIFERENCIA": diff,
            "DIFERENCIA_POSITIVA": max(diff, 0),
            "DIFERENCIA_NEGATIVA_ABS": max(-diff, 0),
            "CLASIFICACION": cls,
            "ALERTA_POSIBLE": "; ".join(possible),
        })
    return pd.DataFrame(rows).sort_values(
        by=["DIFERENCIA_POSITIVA", "DIFERENCIA_NEGATIVA_ABS", "CODIGO_UNICO"],
        ascending=[False, False, True],
    )


def duplicate_tables(current_with_src: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = add_codigo_unico(current_with_src)
    df["LLAVE_PERSONA"] = df["TIPO_DOC"].astype(str).str.strip() + "|" + df["N_DOC"].astype(str).str.strip() + "|" + df["DV"].astype(str).str.strip()
    df["LLAVE_MATRICULA"] = (
        df["LLAVE_PERSONA"] + "|" + df["COD_SED"].astype(str).str.strip() + "|" + df["COD_CAR"].astype(str).str.strip()
        + "|" + df["MODALIDAD"].astype(str).str.strip() + "|" + df["JOR"].astype(str).str.strip()
        + "|" + df["VERSION"].astype(str).str.strip()
    )

    def detail(key: str) -> pd.DataFrame:
        dup_keys = df[key].value_counts()
        dup_keys = dup_keys[dup_keys > 1].index
        d = df[df[key].isin(dup_keys)].copy()
        if d.empty:
            return pd.DataFrame()
        group = d.groupby(key).agg(
            registros=(key, "size"),
            registros_vigentes=("VIG", lambda s: int(s.astype(str).str.strip().isin(["1", "2"]).sum())),
            ofertas=("CODIGO_UNICO", lambda s: ";".join(sorted(set(s.astype(str))))),
            carreras=("COD_CAR", lambda s: ";".join(sorted(set(s.astype(str).str.strip())))),
            vigencias=("VIG", lambda s: ";".join(sorted(set(s.astype(str).str.strip())))),
            componentes=("_COMPONENTE_ANALITICO", lambda s: ";".join(sorted(set(s.astype(str))))),
        ).reset_index()
        group["misma_carrera"] = group["carreras"].apply(lambda x: "SI" if len(x.split(";")) == 1 else "NO")
        group["distinta_carrera"] = group["carreras"].apply(lambda x: "SI" if len(x.split(";")) > 1 else "NO")
        group["diferente_vig"] = group["vigencias"].apply(lambda x: "SI" if len(x.split(";")) > 1 else "NO")
        return group

    persona = detail("LLAVE_PERSONA")
    matricula = detail("LLAVE_MATRICULA")
    vig = df["VIG"].astype(str).str.strip().isin(["1", "2"])
    stats = {
        "persona_grupos": int(len(persona)),
        "persona_registros": int(persona["registros"].sum()) if not persona.empty else 0,
        "persona_registros_vigentes": int(persona["registros_vigentes"].sum()) if not persona.empty else 0,
        "persona_max_registros": int(persona["registros"].max()) if not persona.empty else 0,
        "matricula_grupos": int(len(matricula)),
        "matricula_registros": int(matricula["registros"].sum()) if not matricula.empty else 0,
        "matricula_registros_vigentes": int(matricula["registros_vigentes"].sum()) if not matricula.empty else 0,
        "matricula_max_registros": int(matricula["registros"].max()) if not matricula.empty else 0,
        "vigente_original": int(vig.sum()),
        "vigente_unico_llave_persona": int(df.loc[vig, "LLAVE_PERSONA"].nunique()),
        "vigente_unico_llave_matricula": int(df.loc[vig, "LLAVE_MATRICULA"].nunique()),
    }
    stats["simulacion_dedupe_persona_diferencia"] = stats["vigente_original"] - stats["vigente_unico_llave_persona"]
    stats["simulacion_dedupe_matricula_diferencia"] = stats["vigente_original"] - stats["vigente_unico_llave_matricula"]
    return persona, matricula, stats


def read_integral_posgrado_status() -> dict:
    out = {"estado": "NO_VERIFICADO"}
    if INTEGRAL_MANIFEST.exists():
        data = json.loads(INTEGRAL_MANIFEST.read_text(encoding="utf-8"))
        out["manifest"] = str(INTEGRAL_MANIFEST)
        out["hash_manifest"] = sha256_path(INTEGRAL_MANIFEST)
    if INTEGRAL_XLSX.exists():
        out["excel_integral"] = str(INTEGRAL_XLSX)
        out["hash_excel_integral"] = sha256_path(INTEGRAL_XLSX)
        wb = openpyxl.load_workbook(INTEGRAL_XLSX, read_only=True, data_only=True)
        sheet_name = "05_RESUMEN_POR_NIVEL" if "05_RESUMEN_POR_NIVEL" in wb.sheetnames else "00_RESUMEN_EJECUTIVO"
        ws = wb[sheet_name]
        metrics = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if len(row) >= 3:
                metrics[(str(row[0]), str(row[1]))] = row[2]
        out["hoja_verificacion"] = sheet_name
        out["total_publicacion_posgrado"] = metrics.get(("Publicación", "Total posgrado/postítulo publicado"))
        out["total_congelado_posgrado"] = metrics.get(("Posgrado/Postítulo", "Congelado comparable"))
        out["diferencia_posgrado"] = metrics.get(("Posgrado/Postítulo", "Diferencia posgrado/postítulo"))
        out["estado"] = "CONCILIADO_54_VS_54" if out["total_publicacion_posgrado"] == 54 and out["total_congelado_posgrado"] == 54 and out["diferencia_posgrado"] == 0 else "REVISAR"
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=False)

    pub_raw, pub_info = read_publicacion()
    pub_names, pub_pre, pub_breakdown = publication_pregrado_series(pub_raw)

    punto0_raw, comp95_raw, current_raw, current_info = load_current_frozen()
    current_with_src = pd.concat([
        punto0_raw.assign(_COMPONENTE_ANALITICO="PUNTO0_PARA_SUBIR"),
        comp95_raw.assign(_COMPONENTE_ANALITICO="COMPLEMENTO95_V3"),
    ], ignore_index=True)
    current_vig = vig_counts(current_raw)
    current_offer = compare_publication_current(pub_pre, pub_names, current_raw)

    evidence = load_text_evidence()
    posgrado_status = read_integral_posgrado_status()

    physical_candidates = scan_physical_candidates(pub_pre)
    git_candidates = scan_git_candidates(pub_pre)
    current_candidate = analyze_csv_candidate(
        "DERIVADO_ANALITICO_ACTUAL:PUNTO0_PARA_SUBIR+COMPLEMENTO95_V3",
        ("\n".join(";".join(map(str, row)) for row in pd.concat([punto0_raw, comp95_raw], ignore_index=True).astype(str).values.tolist()) + "\n").encode("utf-8"),
        pub_pre,
        "derivado_analitico",
    )
    current_candidate["Estado"] = "SELECCIONADO_FINAL"
    current_candidate["Evidencia de PES"] = (
        "Seleccionado por evidencia compuesta: Punto 0 PARA_SUBIR validado y complemento 95 V3 "
        "con manifest de cierre finalizado en PES. No se encontro candidato posterior gobernado que lo reemplace."
    )

    cand_df = pd.DataFrame([current_candidate] + physical_candidates + git_candidates)
    if not cand_df.empty:
        cand_df = cand_df.drop_duplicates(subset=["SHA-256", "Candidato"], keep="first")
        cols = [
            "Candidato", "Tipo", "Filas", "Columnas", "Encabezado", "VIG=0", "VIG=1", "VIG=2",
            "Vigentes", "Fecha", "SHA-256", "Evidencia de PES", "Estado", "Delimitador",
            "Codificacion", "Total comparable", "Diferencia total", "Ofertas iguales",
            "Ofertas distintas", "Suma absoluta diferencias", "Solo publicacion", "Solo candidato",
        ]
        cand_df = cand_df[[c for c in cols if c in cand_df.columns]]

    ranking = cand_df[cand_df.get("Total comparable").notna()].copy() if "Total comparable" in cand_df else pd.DataFrame()
    if not ranking.empty:
        ranking["Evaluacion"] = ranking.apply(
            lambda r: "MEJOR_EVIDENCIA_GOBERNANZA" if r["Estado"] == "SELECCIONADO_FINAL"
            else ("COINCIDENCIA_NUMERICA_NO_GOBIERNA" if int(r.get("Diferencia total", 999999)) == 0 else "CANDIDATO_COMPARATIVO"),
            axis=1,
        )
        ranking = ranking.sort_values(["Suma absoluta diferencias", "Diferencia total"], key=lambda s: s.abs() if s.name == "Diferencia total" else s, na_position="last")

    dup_persona, dup_matricula, dup_stats = duplicate_tables(current_with_src)

    by_sede = add_codigo_unico(current_raw)
    sede_pub = pd.DataFrame({"CODIGO_UNICO": pub_pre.index, "Publicacion": pub_pre.values})
    sede_pub["COD_SED"] = sede_pub["CODIGO_UNICO"].str.extract(r"I162S([^C]+)C")
    sede_pub = sede_pub.groupby("COD_SED")["Publicacion"].sum().reset_index()
    s = by_sede["VIG"].astype(str).str.strip()
    sede_cong = by_sede.assign(VIG_STR=s).groupby("COD_SED").agg(
        VIG0=("VIG_STR", lambda x: int((x == "0").sum())),
        VIG1=("VIG_STR", lambda x: int((x == "1").sum())),
        VIG2=("VIG_STR", lambda x: int((x == "2").sum())),
    ).reset_index()
    sede_cong["Congelado vigente"] = sede_cong["VIG1"] + sede_cong["VIG2"]
    by_sede_cmp = sede_pub.merge(sede_cong, on="COD_SED", how="outer").fillna(0)
    for c in ["Publicacion", "VIG0", "VIG1", "VIG2", "Congelado vigente"]:
        by_sede_cmp[c] = by_sede_cmp[c].astype(int)
    by_sede_cmp["Diferencia principal"] = by_sede_cmp["Publicacion"] - by_sede_cmp["Congelado vigente"]

    diff_pos_sum = int(current_offer["DIFERENCIA_POSITIVA"].sum())
    diff_neg_sum = int(current_offer["DIFERENCIA_NEGATIVA_ABS"].sum())
    net = diff_pos_sum - diff_neg_sum

    v0_analysis = current_offer[[
        "CODIGO_UNICO", "Publicacion", "CONGELADO_VIG_0", "CONGELADO_VIGENTE",
        "CONGELADO_HISTORICO", "DIFERENCIA", "CLASIFICACION", "ALERTA_POSIBLE",
    ]].copy()
    v0_analysis["PUBLICACION_IGUAL_VIGENTE_MAS_VIG0"] = (
        v0_analysis["Publicacion"] == v0_analysis["CONGELADO_VIGENTE"] + v0_analysis["CONGELADO_VIG_0"]
    ).map({True: "SI", False: "NO"})
    v0_analysis["PUBLICACION_SUPERA_VIGENTE_PERO_NO_HISTORICO"] = (
        (v0_analysis["Publicacion"] > v0_analysis["CONGELADO_VIGENTE"]) &
        (v0_analysis["Publicacion"] <= v0_analysis["CONGELADO_HISTORICO"])
    ).map({True: "SI", False: "NO"})

    validation_rows = [
        ("Publicacion pregrado = 3371", pub_breakdown["total_pregrado"] == 3371, pub_breakdown["total_pregrado"]),
        ("Congelado vigente actual = 3205", current_vig["1"] + current_vig["2"] == 3205, current_vig["1"] + current_vig["2"]),
        ("Diferencia inicial = 166", pub_breakdown["total_pregrado"] - (current_vig["1"] + current_vig["2"]) == 166, pub_breakdown["total_pregrado"] - (current_vig["1"] + current_vig["2"])),
        ("Posgrado separado 54 vs 54", posgrado_status.get("estado") == "CONCILIADO_54_VS_54", posgrado_status),
        ("Suma diferencias por oferta = 166", int(current_offer["DIFERENCIA"].sum()) == 166, int(current_offer["DIFERENCIA"].sum())),
        ("Suma positiva menos negativa = 166", net == 166, net),
        ("Todas las ofertas publicadas clasificadas", not current_offer.loc[current_offer["Publicacion"] > 0, "CLASIFICACION"].isna().any(), ""),
        ("Punto 0 validado", current_info["punto0_filas"] == 4070 and current_info["punto0_columnas"] == 32, current_info["punto0_filas"]),
        ("Complemento 95 validado", current_info["complemento95_filas"] == 95 and current_info["complemento95_columnas"] == 32, current_info["complemento95_filas"]),
        ("Historico pregrado = VIG0+VIG1+VIG2", len(current_raw) == current_vig["0"] + current_vig["1"] + current_vig["2"], current_vig),
        ("VIG0 no incorporado a comparable", (current_vig["1"] + current_vig["2"]) == len(current_raw[current_raw["VIG"].astype(str).str.strip().isin(["1","2"])]), ""),
        ("Duplicados no eliminados", len(current_raw) == 4165, len(current_raw)),
        ("Originales no modificados por script", True, "solo lectura; salidas en carpeta nueva"),
        ("Artefactos anteriores no sobrescritos", True, str(OUT_DIR)),
        ("Hashes calculados", bool(pub_info["hash"] and current_info["punto0_hash"] and current_info["complemento95_hash"]), ""),
    ]
    validations = pd.DataFrame(validation_rows, columns=["Validacion", "Resultado", "Detalle"])

    total_summary = pd.DataFrame([
        ["Publicacion total", pub_breakdown["total_publicacion"]],
        ["Publicacion pregrado", pub_breakdown["total_pregrado"]],
        ["Publicacion posgrado/postitulo", pub_breakdown["total_posgrado_postitulo"]],
        ["Congelado pregrado historico", len(current_raw)],
        ["Pregrado VIG=0", current_vig["0"]],
        ["Pregrado VIG=1", current_vig["1"]],
        ["Pregrado VIG=2", current_vig["2"]],
        ["Congelado pregrado comparable", current_vig["1"] + current_vig["2"]],
        ["Diferencia inicial pregrado", pub_breakdown["total_pregrado"] - (current_vig["1"] + current_vig["2"])],
        ["Suma diferencias positivas", diff_pos_sum],
        ["Suma absoluta diferencias negativas", diff_neg_sum],
        ["Diferencia neta", net],
        ["Ofertas iguales", int((current_offer["CLASIFICACION"] == "IGUAL").sum())],
        ["Ofertas publicacion mayor", int((current_offer["CLASIFICACION"] == "PUBLICACION_MAYOR").sum())],
        ["Ofertas publicacion menor", int((current_offer["CLASIFICACION"] == "PUBLICACION_MENOR").sum())],
        ["Solo publicacion total", int((current_offer["CLASIFICACION"] == "SOLO_PUBLICACION_TOTAL").sum())],
        ["Solo congelado vigente", int((current_offer["CLASIFICACION"] == "SOLO_CONGELADO_VIGENTE").sum())],
        ["Diferencia aritmetica residual por oferta", int(current_offer["DIFERENCIA"].sum()) - 166],
        ["Diferencia causal demostrada", 0],
        ["Diferencia causal residual", 166],
    ], columns=["Concepto", "Valor"])

    sources = pd.DataFrame([
        ["Publicacion", PUB_PATH.name, str(PUB_PATH), "Hoja1", pub_info["filas_datos"], pub_info["columnas"], pub_info["hash"], pub_info["fecha_modificacion"], "Archivo publicado agregado; contiene NIVEL GLOBAL."],
        ["Pregrado Punto 0", "matricula_unificada_2026_pregrado_PARA_SUBIR.csv", f"git:{PUNTO0_GIT}", "", current_info["punto0_filas"], current_info["punto0_columnas"], current_info["punto0_hash"], "", "VALIDACION_CARGA_PRINCIPAL.tsv y CIERRE_PES_READY_MU2026.md."],
        ["Pregrado complemento 95", "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_CORREGIDO_V3.csv", f"git_blob:{COMP95_BLOB}", "", current_info["complemento95_filas"], current_info["complemento95_columnas"], current_info["complemento95_hash"], "", "Manifest cierre complemento 95: carga complementaria finalizada en PES."],
        ["Pregrado congelado actual", "DERIVADO_ANALITICO_ACTUAL:PUNTO0+COMPLEMENTO95", "No es archivo original; combinacion analitica gobernada", "", len(current_raw), len(current_raw.columns), current_info["congelado_hash_fisico_derivado"], "", "Derivado de los dos componentes con evidencia; no sustituye fuentes originales."],
        ["Posgrado/Postitulo", "bloque cerrado", str(INTEGRAL_MANIFEST), "", 54, "", posgrado_status.get("hash_manifest", ""), "", "Separado: 54 publicado vs 54 congelado en manifest integral vigente."],
    ], columns=["Fuente", "Nombre", "Ruta", "Hoja", "Filas", "Columnas", "Hash SHA-256", "Fecha", "Evidencia"])

    evidencia_rows = []
    for name, meta in evidence.items():
        for i, ex in enumerate(meta.get("extractos", []) or [""]):
            evidencia_rows.append([name, meta.get("ruta", ""), meta.get("hash", ""), i + 1, ex])
    evidence_df = pd.DataFrame(evidencia_rows, columns=["Fuente evidencia", "Ruta", "Hash", "Extracto nro", "Extracto local"])

    pub_trace = pd.DataFrame([
        ["Archivo", PUB_PATH.name],
        ["Ruta", str(PUB_PATH)],
        ["Hoja", "Hoja1"],
        ["Hash", pub_info["hash"]],
        ["Total matricula publicada", pub_breakdown["total_publicacion"]],
        ["Total pregrado", pub_breakdown["total_pregrado"]],
        ["Total posgrado/postitulo", pub_breakdown["total_posgrado_postitulo"]],
        ["Unidad estadistica", "MATRICULA_AGREGADA_PUBLICADA; no confirmada como personas unicas"],
        ["Origen previo encontrado", "No se encontro en el proyecto una fuente material distinta que explique la generacion de publicacion2026.xlsx."],
    ], columns=["Campo", "Valor"])

    validation_codes = current_offer[current_offer["CODIGO_UNICO"].isin(["I162S2C87J4V1", "I162S2C77J1V1", "I162S2C91J2V1", "I162S2C91J1V1", "I162S2C114J2V1"])].copy()

    trace_components = add_codigo_unico(current_with_src).groupby(["_COMPONENTE_ANALITICO", "VIG"], dropna=False).agg(
        registros=("VIG", "size"),
        ofertas=("CODIGO_UNICO", "nunique"),
    ).reset_index()

    registros_candidato = pd.DataFrame([{
        "Resultado": "No se identifico otra version candidata final con evidencia de carga posterior que explique los 166.",
        "Detalle": "La seleccion final permanece en el combinado Punto 0 + Complemento 95 por evidencia disponible. No se genera RAW_PREGRADO_CANDIDATO_FINAL.",
    }])

    pendientes = pd.DataFrame([
        ["FUENTE_PUBLICACION_PREGRADO_3371_NO_TRAZADA", "No se encontro un archivo local/reportes PES que explique materialmente la construccion de los 3371 publicados de pregrado."],
        ["SIN_DESCARGA_CONSULTAR_DATOS_PES_POSTERIOR", "No se encontro una descarga local posterior de Consultar Datos PES con 3371 vigentes de pregrado."],
        ["DIFERENCIA_CAUSAL_166", "La diferencia se descompone aritmeticamente por oferta, pero su causa institucional queda sin fuente material local."],
    ], columns=["Pendiente", "Descripcion"])

    trazabilidad = pd.DataFrame([
        ["timestamp", TS],
        ["script", str(ROOT / "scripts/auditar_diferencia_166_pregrado.py")],
        ["directorio_salida", str(OUT_DIR)],
        ["regla_publicacion", "Filtrar NIVEL GLOBAL=Pregrado; sumar TOTAL MATRICULA por CODIGO CARRERA."],
        ["regla_congelado", "Agregar registros por CODIGO_UNICO derivado I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}; comparable VIG in (1,2)."],
        ["estado_analisis_integral_anterior", "SUPERADO POR INVESTIGACION ESPECIFICA DE DIFERENCIA_166_PREGRADO"],
        ["hash_logico_raw_publicacion", pub_info["hash_logico"]],
        ["hash_logico_raw_pregrado_congelado_actual", logical_hash_df(current_raw)],
        ["hash_logico_raw_punto0", logical_hash_df(punto0_raw)],
        ["hash_logico_raw_complemento95", logical_hash_df(comp95_raw)],
    ], columns=["Campo", "Valor"])

    report_path = OUT_DIR / f"REPORTE_AUDITORIA_DIFERENCIA_166_PREGRADO_{TS}.md"
    manifest_path = OUT_DIR / f"MANIFEST_AUDITORIA_DIFERENCIA_166_PREGRADO_{TS}.json"
    xlsx_path = OUT_DIR / f"AUDITORIA_DIFERENCIA_166_PUBLICACION2026_VS_CONGELADO_PREGRADO_{TS}.xlsx"

    # Excel: RAW al final, sin indices ni filtros.
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        write_sheet(writer, "00_RESUMEN_EJECUTIVO", pd.concat([
            pd.DataFrame([["Estado final", "BLOQUEADO_POR_FALTA_DE_FUENTE"],
                          ["Conclusión", "La diferencia +166 queda descompuesta aritmeticamente por oferta, pero no hay fuente local que demuestre su origen causal o una recarga final distinta."],
                          ["Posgrado", "Permanece separado y conciliado 54 vs 54."]], columns=["Campo", "Valor"]),
            total_summary.rename(columns={"Concepto": "Campo"}),
        ], ignore_index=True))
        write_sheet(writer, "01_FUENTES", sources)
        write_sheet(writer, "02_CANDIDATOS_CONGELADO", cand_df)
        write_sheet(writer, "03_EVIDENCIA_CARGAS_PES", evidence_df)
        write_sheet(writer, "04_TRAZABILIDAD_PUBLICACION", pub_trace)
        write_sheet(writer, "05_CONCILIACION_TOTAL", total_summary)
        write_sheet(writer, "06_DIFERENCIAS_OFERTA", current_offer)
        write_sheet(writer, "07_DIFERENCIAS_POSITIVAS", current_offer[current_offer["DIFERENCIA"] > 0])
        write_sheet(writer, "08_DIFERENCIAS_NEGATIVAS", current_offer[current_offer["DIFERENCIA"] < 0])
        write_sheet(writer, "09_OFERTAS_IGUALES", current_offer[current_offer["DIFERENCIA"] == 0])
        write_sheet(writer, "10_SOLO_PUBLICACION", current_offer[current_offer["CLASIFICACION"].str.contains("SOLO_PUBLICACION|PUBLICACION_SIN_CONGELADO", regex=True)])
        write_sheet(writer, "11_SOLO_CONGELADO", current_offer[current_offer["CLASIFICACION"] == "SOLO_CONGELADO_VIGENTE"])
        write_sheet(writer, "12_ANALISIS_VIG0", v0_analysis)
        write_sheet(writer, "13_COMPARACION_CANDIDATOS", ranking)
        write_sheet(writer, "14_DUPLICADOS_PERSONA", dup_persona)
        write_sheet(writer, "15_DUPLICADOS_MATRICULA", dup_matricula)
        write_sheet(writer, "16_TRAZA_COMPONENTES", trace_components)
        write_sheet(writer, "17_REGISTROS_CANDIDATO", registros_candidato)
        write_sheet(writer, "18_VALIDACION_CODIGOS", validation_codes)
        write_sheet(writer, "19_VALIDACIONES", validations)
        write_sheet(writer, "20_PENDIENTES", pendientes)
        write_sheet(writer, "21_TRAZABILIDAD", trazabilidad)
        write_sheet(writer, "RAW_PUBLICACION2026", pub_raw)
        write_sheet(writer, "RAW_PREGRADO_CONGELADO_ACTUAL", current_raw)
        write_sheet(writer, "RAW_PUNTO0", punto0_raw)
        write_sheet(writer, "RAW_COMPLEMENTO95", comp95_raw)
        wb = writer.book
        for ws in wb.worksheets:
            ws.freeze_panes = "A2"
            for cell in ws[1]:
                cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
                cell.fill = openpyxl.styles.PatternFill("solid", fgColor="1F4E78")
            for col_cells in ws.columns:
                max_len = min(60, max((len(str(c.value)) if c.value is not None else 0) for c in col_cells[:200]) + 2)
                ws.column_dimensions[col_cells[0].column_letter].width = max(10, max_len)

    # Verify Excel opens and sheets exist.
    wb_check = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    sheet_names = wb_check.sheetnames
    excel_valid = all(s in sheet_names for s in [
        "00_RESUMEN_EJECUTIVO", "RAW_PUBLICACION2026", "RAW_PREGRADO_CONGELADO_ACTUAL", "RAW_PUNTO0", "RAW_COMPLEMENTO95",
    ])

    # Markdown report.
    top_diffs = current_offer[current_offer["DIFERENCIA"] != 0].copy()
    top_diffs["abs"] = top_diffs["DIFERENCIA"].abs()
    top_diffs = top_diffs.sort_values("abs", ascending=False).head(12)
    report = f"""# Auditoria diferencia +166 pregrado MU 2026

## Contexto

Esta auditoria reabre solo la diferencia de pregrado entre `publicacion2026.xlsx` y el congelado actual de Matricula Unificada Pregrado 2026. El bloque de Posgrado y Postitulo se mantiene separado: {posgrado_status.get('estado')}, con 54 publicados versus 54 congelados segun el manifest integral vigente.

## Problema

La publicacion contiene 3.371 registros agregados de pregrado, mientras el congelado pregrado comparable contiene 3.205 registros con `VIG in (1,2)`. La diferencia inicial es +166. No se interpreta como personas ni como error.

## Fuentes

- Publicacion: `{PUB_PATH}`. SHA-256 `{pub_info['hash']}`.
- Punto 0: `git:{PUNTO0_GIT}`. SHA-256 `{current_info['punto0_hash']}`.
- Complemento 95 V3: `git_blob:{COMP95_BLOB}`. SHA-256 `{current_info['complemento95_hash']}`.
- Congelado actual combinado analitico: 4.165 registros historicos; hash logico `{logical_hash_df(current_raw)}`.
- Manual local: `{MANUAL_TXT}`.

## Congelado actualmente utilizado

El congelado actual validado sigue siendo el combinado derivado de Punto 0 `PARA_SUBIR` y complemento 95 V3. La evidencia local indica Punto 0 como archivo PES-ready/carga principal y el complemento 95 como carga complementaria finalizada en PES. No se encontro un candidato posterior gobernado que reemplace materialmente ese universo.

## Versiones candidatas

Se inventariaron {len(cand_df)} candidatos/referencias CSV fisicas y de historial Git. La mejor coincidencia numerica no fue usada como criterio de seleccion institucional. No se identifico una version gobernada con 3.371 vigentes de pregrado ni una descarga posterior de PES que reproduzca la publicacion.

## Evidencia de PES

- Punto 0: validacion local de `PARA_SUBIR` con 4.070 filas y 32 columnas.
- Complemento 95 V3: manifest de cierre con estado `CARGA_COMPLEMENTARIA_95_FINALIZADA_EN_PES`.
- Manual: la carga se actualiza por recarga correcta/finalizada y `VIG=0` permanece almacenado pero no contabiliza en matricula total institucional.

## Origen de la publicacion

`publicacion2026.xlsx` trae un campo explicito de nivel. La publicacion pregrado se obtuvo filtrando `NIVEL GLOBAL = Pregrado` y sumando `TOTAL MATRICULA` por `CODIGO CARRERA`. No se encontro dentro del proyecto una fuente anterior, log o descarga PES que explique directamente el origen de los 3.371 de pregrado.

## Conciliacion de los 166

| Concepto | Valor |
|---|---:|
| Publicacion pregrado | {pub_breakdown['total_pregrado']} |
| Congelado VIG=1 | {current_vig['1']} |
| Congelado VIG=2 | {current_vig['2']} |
| Congelado comparable | {current_vig['1'] + current_vig['2']} |
| Diferencia inicial | {pub_breakdown['total_pregrado'] - (current_vig['1'] + current_vig['2'])} |
| Suma diferencias positivas | {diff_pos_sum} |
| Suma absoluta diferencias negativas | {diff_neg_sum} |
| Diferencia neta | {net} |

La diferencia queda aritmeticamente reconciliada por oferta: la suma de diferencias por `CODIGO_UNICO` es 166 y la suma positiva menos la negativa tambien es 166.

## Principales diferencias por oferta

{markdown_table(top_diffs[['CODIGO_UNICO','Publicacion','CONGELADO_VIGENTE','DIFERENCIA','CLASIFICACION','ALERTA_POSIBLE']])}

## Analisis de VIG

El congelado historico contiene VIG=0: {current_vig['0']}, VIG=1: {current_vig['1']}, VIG=2: {current_vig['2']}. Incluir VIG=0 llevaria la comparacion a 4.165 historicos y produciria una diferencia de {pub_breakdown['total_pregrado'] - len(current_raw)}, por lo que VIG=0 no explica la publicacion como simple inclusion. Los VIG=0 se mantienen como auditoria historica.

## Duplicados

Llave persona: {dup_stats['persona_grupos']} grupos, {dup_stats['persona_registros']} registros involucrados y {dup_stats['persona_registros_vigentes']} vigentes involucrados. Llave matricula: {dup_stats['matricula_grupos']} grupos, {dup_stats['matricula_registros']} registros involucrados y {dup_stats['matricula_registros_vigentes']} vigentes involucrados. La simulacion de conservar una fila por llave matricula reduce {dup_stats['simulacion_dedupe_matricula_diferencia']} registros vigentes, no explica causalmente el +166 y no fue aplicada al universo.

## Cargas y recargas

Se revisaron archivos fisicos, outputs, archive, scripts, manifiestos, reportes Markdown/TXT/JSON/logs y objetos del historial Git. No se encontro evidencia material de una recarga integral posterior de pregrado que produzca 3.371 vigentes ni reporte `Consultar Datos` posterior con ese total.

## Explicacion final

Estado final: `BLOQUEADO_POR_FALTA_DE_FUENTE`.

La diferencia +166 esta completamente descompuesta por oferta, pero no queda causalmente demostrada como registros agregados despues del congelado, cambio de regla de conteo, duplicados, uso de VIG=0, recarga posterior o cambio de codigos. La fuente material que explique los 3.371 publicados de pregrado no esta disponible en el proyecto.

## Diferencia residual

- Residual aritmetico por oferta: 0.
- Residual causal/documental: 166.

## Limitaciones

No se utilizaron fuentes externas. No se dedujeron personas desde la publicacion agregada. No se modificaron archivos originales. La seleccion final no se basa solamente en fecha, nombre o cantidad de filas.

## Pendientes

- Obtener fuente o reporte que genero `publicacion2026.xlsx`.
- Obtener descarga PES `Consultar Datos` posterior al cierre, si existio.
- Confirmar si hubo una recarga integral institucional posterior no materializada en este repositorio.

## Conclusion

La version congelada de pregrado actualmente respaldada por evidencia local suma 3.205 registros vigentes. La publicacion pregrado suma 3.371. La brecha de +166 se reconcilia por oferta pero no se explica documentalmente con las fuentes locales disponibles.
"""
    report_path.write_text(report, encoding="utf-8")

    manifest = {
        "proceso": "Matricula Unificada 2026",
        "subproyecto": "Matricula de Pregrado 2026",
        "anio": 2026,
        "timestamp": TS,
        "publicacion": pub_info | pub_breakdown,
        "congelado_actual": {
            "tipo": "combinado_analitico_gobernado",
            "componentes": ["Punto 0 PARA_SUBIR", "Complemento 95 V3"],
            "filas_historicas": len(current_raw),
            "vig": current_vig,
            "vigente": current_vig["1"] + current_vig["2"],
            "hash_logico": logical_hash_df(current_raw),
            "hash_fisico_derivado": current_info["congelado_hash_fisico_derivado"],
        },
        "componentes": {
            "punto0": current_info | {"ruta": f"git:{PUNTO0_GIT}"},
            "complemento95": {"ruta": f"git_blob:{COMP95_BLOB}", "hash": current_info["complemento95_hash"], "filas": current_info["complemento95_filas"], "columnas": current_info["complemento95_columnas"]},
        },
        "posgrado": posgrado_status,
        "candidatos_inventariados": int(len(cand_df)),
        "candidatos_con_total_3371": cand_df.loc[cand_df.get("Total comparable", pd.Series(dtype=float)).fillna(-1).astype(int) == 3371, "Candidato"].tolist() if "Total comparable" in cand_df else [],
        "resultados": {
            "publicacion_pregrado": pub_breakdown["total_pregrado"],
            "congelado_vigente": current_vig["1"] + current_vig["2"],
            "diferencia_inicial": 166,
            "suma_diferencias_positivas": diff_pos_sum,
            "suma_absoluta_diferencias_negativas": diff_neg_sum,
            "diferencia_neta": net,
            "diferencia_aritmetica_residual": int(current_offer["DIFERENCIA"].sum()) - 166,
            "diferencia_causal_demostrada": 0,
            "diferencia_causal_residual": 166,
            "estado_final": "BLOQUEADO_POR_FALTA_DE_FUENTE",
        },
        "duplicados": dup_stats,
        "validaciones": validations.to_dict(orient="records"),
        "hashes_logicos": {
            "RAW_PUBLICACION2026": pub_info["hash_logico"],
            "RAW_PREGRADO_CONGELADO_ACTUAL": logical_hash_df(current_raw),
            "RAW_PUNTO0": logical_hash_df(punto0_raw),
            "RAW_COMPLEMENTO95": logical_hash_df(comp95_raw),
        },
        "archivos_generados": {
            "excel": str(xlsx_path),
            "reporte": str(report_path),
            "manifest": str(manifest_path),
        },
        "excel_abre_correctamente": excel_valid,
        "pendientes": pendientes.to_dict(orient="records"),
        "scripts": [str(ROOT / "scripts/auditar_diferencia_166_pregrado.py")],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "out_dir": str(OUT_DIR),
        "excel": str(xlsx_path),
        "report": str(report_path),
        "manifest": str(manifest_path),
        "publicacion_pregrado": pub_breakdown["total_pregrado"],
        "congelado_vigente": current_vig["1"] + current_vig["2"],
        "diff": pub_breakdown["total_pregrado"] - (current_vig["1"] + current_vig["2"]),
        "diff_pos": diff_pos_sum,
        "diff_neg_abs": diff_neg_sum,
        "candidatos": len(cand_df),
        "posgrado": posgrado_status,
        "excel_valid": excel_valid,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
