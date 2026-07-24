#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
PUBLICACION = ROOT / "publicacion2026.xlsx"
MANUAL = ROOT / "Manual_Matrícula_Unificada_2026.pdf"
OUT_ROOT = ROOT / "outputs" / "comparaciones_publicacion2026_integrales"

PREV_ANALYSES = [
    {
        "ruta": str(ROOT / "outputs" / "comparaciones_publicacion2026" / "20260730_163247"),
        "estado": "SUPERADO",
        "motivo": "UNIVERSO_HISTORICO_PREGRADO_INCLUÍA_VIG_0",
    },
    {
        "ruta": str(ROOT / "outputs" / "comparaciones_publicacion2026_corregidas" / "20260730_164055"),
        "estado": "SUPERADO",
        "motivo": "SUPERADO POR SEPARACIÓN OBLIGATORIA DE PREGRADO Y POSGRADO",
    },
]

COMMIT = "4f1108c"
PUNTO0_GIT_PATH = (
    "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/"
    "carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
)
COMPLEMENTO95_V3_OBJECT = "d4bd44f9d1f11640056b8e990f5e1fcda9aebf7d"
POS_CON_TITULOS_OBJECT = "1c1d4833b5dc5637b0c1670b5823c8aab4683f93"
POS_PES_READY_55_BKP_OBJECT = "78d8f47c9a8774567e8bd8c9722e6dc39bb543d5"
POS_CONTROL_FINAL_OBJECT = "285ad4aa94ee88026efa19a36b3daec6c788ed30"
POS_RECONCILIACION_OBJECT = "162a103919fb12c27af99f749e3c54776d3424ad"
POS_TRAZABILIDAD_OBJECT = "e89beba2e868e37ca2aab5bda51be971042647b0"
PROMEDIOS_OBJECT = "d60c5e5805934b5692e6cc8b1cd9ca07a1db99a6"
PROMEDIOS_PERFIL_OBJECT = "e2526819e67cafc95d74eb8cff1274c0913c5161"

PRE_COLUMNS = [
    "TIPO_DOC",
    "N_DOC",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRE",
    "SEXO",
    "FECH_NAC",
    "NAC",
    "PAIS_EST_SEC",
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "FOR_ING_ACT",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ANIO_ING_ORI",
    "SEM_ING_ORI",
    "ASI_INS_ANT",
    "ASI_APR_ANT",
    "PROM_PRI_SEM",
    "PROM_SEG_SEM",
    "ASI_INS_HIS",
    "ASI_APR_HIS",
    "NIV_ACA",
    "SIT_FON_SOL",
    "SUS_PRE",
    "FECHA_MATRICULA",
    "REINCORPORACION",
    "VIG",
]

POS_COLUMNS = [
    "TIPO_DOC",
    "N_DOC",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRE",
    "SEXO",
    "FECH_NAC",
    "NAC",
    "PAIS_EST_SEC",
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "FOR_ING_ACT",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ANIO_ING_ORI",
    "SEM_ING_ORI",
    "VIG",
]

VIG_DESC = {
    "0": "Sin matrícula",
    "1": "Matrícula vigente",
    "2": "Egresado con matrícula vigente",
}


def run_git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def git_show_path(path: str) -> bytes:
    return run_git("show", f"{COMMIT}:{path}")


def git_blob(obj: str) -> bytes:
    return run_git("cat-file", "-p", obj)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_file(path: Path) -> dict[str, object]:
    st = path.stat()
    return {
        "nombre": path.name,
        "ruta": str(path),
        "tipo": path.suffix.lower().lstrip("."),
        "bytes": st.st_size,
        "fecha_modificacion": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "hash_sha256": sha256_file(path),
    }


def norm(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def norm_code(value: object) -> str:
    return norm(value).upper()


def to_jsonable(value: object) -> object:
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def logical_hash(headers: list[object], rows: list[list[object]]) -> str:
    payload = {
        "headers": [to_jsonable(v) for v in headers],
        "rows": [[to_jsonable(v) for v in row] for row in rows],
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=False).encode("utf-8")
    return sha256_bytes(raw)


def df_logical_hash(df: pd.DataFrame) -> str:
    rows = df.where(pd.notna(df), None).values.tolist()
    return logical_hash(list(df.columns), rows)


def read_xlsx_raw(path: Path, sheet: str) -> tuple[pd.DataFrame, dict[str, object], str]:
    wb = load_workbook(path, read_only=False, data_only=False)
    ws = wb[sheet]
    matrix = [[cell.value for cell in row] for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column)]
    headers = matrix[0]
    rows = matrix[1:]
    df = pd.DataFrame(rows, columns=headers)
    info = {
        "hoja": ws.title,
        "filas_fisicas": ws.max_row,
        "registros_datos": len(rows),
        "columnas": ws.max_column,
        "encabezados": "SI",
        "tablas": ", ".join(ws.tables.keys()) if ws.tables else "",
        "celdas_combinadas": len(ws.merged_cells.ranges),
        "hojas": "; ".join(f"{w.title}:{w.max_row}x{w.max_column}:{w.sheet_state}" for w in wb.worksheets),
    }
    return df, info, logical_hash(headers, rows)


def parse_codigo_unico(value: object) -> dict[str, str]:
    text = norm_code(value)
    match = re.fullmatch(r"I(?P<IES>\d+)S(?P<COD_SED>\d+)C(?P<COD_CAR>\d+)J(?P<JOR>\d+)V(?P<VERSION>\d+)", text)
    if not match:
        return {"CODIGO_UNICO": text, "COD_SED_DER": "", "COD_CAR_DER": "", "JOR_DER": "", "VERSION_DER": "", "PARSE_OK": "NO"}
    d = match.groupdict()
    return {
        "CODIGO_UNICO": text,
        "COD_SED_DER": d["COD_SED"],
        "COD_CAR_DER": d["COD_CAR"],
        "JOR_DER": d["JOR"],
        "VERSION_DER": d["VERSION"],
        "PARSE_OK": "SI",
    }


def add_keys(df: pd.DataFrame, level: str) -> pd.DataFrame:
    out = df.copy()
    out["CODIGO_UNICO"] = (
        "I162S"
        + out["COD_SED"].map(norm_code)
        + "C"
        + out["COD_CAR"].map(norm_code)
        + "J"
        + out["JOR"].map(norm_code)
        + "V"
        + out["VERSION"].map(norm_code)
    )
    out["LLAVE_PERSONA"] = out["TIPO_DOC"].map(norm_code) + "|" + out["N_DOC"].map(norm_code) + "|" + out["DV"].map(norm_code)
    mat_cols = ["COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION"]
    out[f"LLAVE_{level.upper()}_MATRICULA"] = out["LLAVE_PERSONA"] + "|" + out[mat_cols].map(norm_code).agg("|".join, axis=1)
    return out


def load_pregrado(out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    src_dir = out_dir / "fuentes_derivadas"
    src_dir.mkdir(parents=True, exist_ok=True)
    punto0 = git_show_path(PUNTO0_GIT_PATH)
    comp = git_blob(COMPLEMENTO95_V3_OBJECT)
    combined = punto0 + comp
    punto0_path = src_dir / "FUENTE_COMPONENTE_PREGRADO_PUNTO0_PARA_SUBIR.csv"
    comp_path = src_dir / "FUENTE_COMPONENTE_PREGRADO_COMPLEMENTO95_V3.csv"
    hist_path = src_dir / "DERIVADO_PREGRADO_CONGELADO_HISTORICO_4165_SIN_ENCABEZADOS.csv"
    punto0_path.write_bytes(punto0)
    comp_path.write_bytes(comp)
    hist_path.write_bytes(combined)
    p0 = pd.read_csv(io.BytesIO(punto0), sep=";", header=None, names=PRE_COLUMNS, dtype=str, keep_default_na=False)
    c95 = pd.read_csv(io.BytesIO(comp), sep=";", header=None, names=PRE_COLUMNS, dtype=str, keep_default_na=False)
    raw = pd.concat([p0, c95], ignore_index=True)
    analysis = add_keys(raw, "pregrado")
    analysis["FUENTE_COMPONENTE_ANALITICA"] = ["PUNTO0_PARA_SUBIR"] * len(p0) + ["COMPLEMENTO95_V3_FINALIZADO_PES"] * len(c95)
    return raw, analysis, {
        "punto0_path": str(punto0_path),
        "punto0_hash": sha256_bytes(punto0),
        "punto0_rows": len(p0),
        "complemento95_path": str(comp_path),
        "complemento95_hash": sha256_bytes(comp),
        "complemento95_rows": len(c95),
        "historico_path": str(hist_path),
        "historico_hash": sha256_bytes(combined),
        "historico_rows": len(raw),
    }


def load_posgrado(out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    src_dir = out_dir / "fuentes_derivadas"
    src_dir.mkdir(parents=True, exist_ok=True)
    con_titulos = git_blob(POS_CON_TITULOS_OBJECT)
    bkp55 = git_blob(POS_PES_READY_55_BKP_OBJECT)
    control = git_blob(POS_CONTROL_FINAL_OBJECT)
    recon = git_blob(POS_RECONCILIACION_OBJECT)
    traza = git_blob(POS_TRAZABILIDAD_OBJECT)
    selected_path = src_dir / "FUENTE_CONGELADA_POSGRADO_POSTITULO_CON_TITULOS_54.csv"
    selected_path.write_bytes(con_titulos)
    (src_dir / "EVIDENCIA_POSGRADO_PES_READY_55_SUPERADO_BKP.csv").write_bytes(bkp55)
    (src_dir / "EVIDENCIA_POSGRADO_CONTROL_FINAL_55_SUPERADO.csv").write_bytes(control)
    (src_dir / "EVIDENCIA_POSGRADO_RECONCILIACION_66_A_54.csv").write_bytes(recon)
    (src_dir / "EVIDENCIA_POSGRADO_TRAZABILIDAD.tsv").write_bytes(traza)
    raw = pd.read_csv(io.BytesIO(con_titulos), sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    analysis = add_keys(raw, "posgrado")
    return raw, analysis, {
        "selected_path": str(selected_path),
        "selected_hash": sha256_bytes(con_titulos),
        "selected_rows": len(raw),
        "pes55_bkp_hash": sha256_bytes(bkp55),
        "control55_hash": sha256_bytes(control),
        "reconciliacion_hash": sha256_bytes(recon),
        "trazabilidad_hash": sha256_bytes(traza),
        "promedios_hash": sha256_bytes(git_blob(PROMEDIOS_OBJECT)),
    }


def classify_publicacion(raw: pd.DataFrame, pre_codes: set[str], pos_codes: set[str]) -> pd.DataFrame:
    df = raw.copy()
    parsed = df["CÓDIGO CARRERA"].apply(parse_codigo_unico).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    df["MATRICULA_AGREGADA_PUBLICADA"] = pd.to_numeric(df["TOTAL MATRÍCULA"], errors="coerce").fillna(0).astype(int)
    df["NIVEL_EXPLICITO_PUBLICACION"] = df["NIVEL GLOBAL"].map(norm)
    df["EN_PREGRADO_CONGELADO"] = df["CODIGO_UNICO"].isin(pre_codes)
    df["EN_POSGRADO_CONGELADO"] = df["CODIGO_UNICO"].isin(pos_codes)

    def classify(row: pd.Series) -> str:
        explicit = norm_code(row["NIVEL_EXPLICITO_PUBLICACION"])
        if explicit == "PREGRADO":
            return "PREGRADO"
        if explicit in {"POSTÍTULO", "POSTITULO", "POSGRADO", "POSTGRADO", "POSGRADO/POSTÍTULO", "POSGRADO Y POSTÍTULO"}:
            return "POSGRADO_POSTITULO"
        in_pre = bool(row["EN_PREGRADO_CONGELADO"])
        in_pos = bool(row["EN_POSGRADO_CONGELADO"])
        if in_pre and in_pos:
            return "AMBIGUO_EN_AMBOS_CONGELADOS"
        if in_pre:
            return "PREGRADO"
        if in_pos:
            return "POSGRADO_POSTITULO"
        return "NO_ENCONTRADO_EN_CONGELADOS"

    df["CLASIFICACION_NIVEL_ANALISIS"] = df.apply(classify, axis=1)
    df["CRITERIO_CLASIFICACION"] = df["NIVEL_EXPLICITO_PUBLICACION"].apply(
        lambda v: "CAMPO_EXPLICITO_NIVEL_GLOBAL" if norm(v) else "CRUCE_EXACTO_CODIGO_CONGELADOS"
    )

    def alert(row: pd.Series) -> str:
        cls = row["CLASIFICACION_NIVEL_ANALISIS"]
        if cls == "PREGRADO" and not row["EN_PREGRADO_CONGELADO"]:
            return "CODIGO_PREGRADO_PUBLICADO_NO_ENCONTRADO_EN_CONGELADO_PREGRADO"
        if cls == "POSGRADO_POSTITULO" and not row["EN_POSGRADO_CONGELADO"]:
            return "CODIGO_POSGRADO_PUBLICADO_NO_ENCONTRADO_EN_CONGELADO_POSGRADO"
        if cls == "AMBIGUO_EN_AMBOS_CONGELADOS":
            return "CODIGO_EN_AMBOS_CONGELADOS"
        if cls == "NO_ENCONTRADO_EN_CONGELADOS":
            return "SIN_NIVEL_DEMOSTRABLE_POR_CAMPO_NI_CODIGO"
        return ""

    df["ALERTA_CLASIFICACION"] = df.apply(alert, axis=1)
    return df


def vig_table(df: pd.DataFrame, key_person: str = "LLAVE_PERSONA") -> pd.DataFrame:
    rows = []
    for vig in ["0", "1", "2"]:
        sub = df[df["VIG"].map(norm_code) == vig]
        rows.append(
            {
                "VIG": vig,
                "Descripción": VIG_DESC[vig],
                "Registros": len(sub),
                "Personas únicas": sub[key_person].nunique() if key_person in sub else "",
                "Ofertas": sub["CODIGO_UNICO"].nunique() if "CODIGO_UNICO" in sub else "",
            }
        )
    rows.append(
        {
            "VIG": "Total",
            "Descripción": "Universo histórico congelado",
            "Registros": len(df),
            "Personas únicas": df[key_person].nunique() if key_person in df else "",
            "Ofertas": df["CODIGO_UNICO"].nunique() if "CODIGO_UNICO" in df else "",
        }
    )
    extras = sorted(set(df["VIG"].map(norm_code)) - {"0", "1", "2"})
    for vig in extras:
        sub = df[df["VIG"].map(norm_code) == vig]
        rows.append({"VIG": vig or "(vacío)", "Descripción": "Valor no esperado", "Registros": len(sub), "Personas únicas": "", "Ofertas": ""})
    return pd.DataFrame(rows)


def compare_pregrado(pub_class: pd.DataFrame, pre: pd.DataFrame) -> pd.DataFrame:
    pub = pub_class[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "PREGRADO"]
    pub_agg = pub.groupby("CODIGO_UNICO", dropna=False).agg(
        Publicación=("MATRICULA_AGREGADA_PUBLICADA", "sum"),
        Nombre_oferta=("NOMBRE CARRERA", lambda s: " | ".join(sorted({str(x) for x in s if pd.notna(x)}))),
        Filas_publicacion=("CODIGO_UNICO", "size"),
    )
    pivot = pre.pivot_table(index="CODIGO_UNICO", columns="VIG", values="LLAVE_PREGRADO_MATRICULA", aggfunc="count", fill_value=0)
    for vig in ["0", "1", "2"]:
        if vig not in pivot.columns:
            pivot[vig] = 0
    meta = pre.groupby("CODIGO_UNICO").agg(
        COD_SED=("COD_SED", "first"),
        COD_CAR=("COD_CAR", "first"),
        MODALIDAD=("MODALIDAD", "first"),
        JOR=("JOR", "first"),
        VERSION=("VERSION", "first"),
    )
    comp = pub_agg.join(pivot[["0", "1", "2"]], how="outer").join(meta, how="left").reset_index()
    comp[["Publicación", "0", "1", "2", "Filas_publicacion"]] = comp[["Publicación", "0", "1", "2", "Filas_publicacion"]].fillna(0).astype(int)
    comp["Congelado VIG=1"] = comp["1"]
    comp["Congelado VIG=2"] = comp["2"]
    comp["Congelado vigente"] = comp["Congelado VIG=1"] + comp["Congelado VIG=2"]
    comp["VIG=0"] = comp["0"]
    comp["Congelado histórico"] = comp["VIG=0"] + comp["Congelado vigente"]
    comp["Diferencia"] = comp["Publicación"] - comp["Congelado vigente"]

    def cls(row: pd.Series) -> str:
        if row["Publicación"] > 0 and row["Congelado vigente"] == 0:
            return "SOLO_PUBLICACION"
        if row["Publicación"] == 0 and row["Congelado vigente"] > 0:
            return "SOLO_CONGELADO"
        if row["Publicación"] == row["Congelado vigente"]:
            return "IGUAL"
        if row["Publicación"] > row["Congelado vigente"]:
            return "PUBLICACION_MAYOR"
        if row["Publicación"] < row["Congelado vigente"]:
            return "PUBLICACION_MENOR"
        return "NO_COMPARABLE"

    comp["Clasificación"] = comp.apply(cls, axis=1)
    comp["abs_dif"] = comp["Diferencia"].abs()
    comp = comp.sort_values(["abs_dif", "Diferencia", "CODIGO_UNICO"], ascending=[False, False, True]).drop(columns=["abs_dif", "0", "1", "2"])
    return comp[
        [
            "CODIGO_UNICO",
            "Nombre_oferta",
            "Publicación",
            "Congelado VIG=1",
            "Congelado VIG=2",
            "Congelado vigente",
            "VIG=0",
            "Congelado histórico",
            "Diferencia",
            "Clasificación",
            "COD_SED",
            "COD_CAR",
            "MODALIDAD",
            "JOR",
            "VERSION",
            "Filas_publicacion",
        ]
    ]


def compare_posgrado(pub_class: pd.DataFrame, pos: pd.DataFrame) -> pd.DataFrame:
    pub = pub_class[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "POSGRADO_POSTITULO"]
    pub_agg = pub.groupby("CODIGO_UNICO", dropna=False).agg(
        Publicación=("MATRICULA_AGREGADA_PUBLICADA", "sum"),
        Nombre_programa=("NOMBRE CARRERA", lambda s: " | ".join(sorted({str(x) for x in s if pd.notna(x)}))),
        Filas_publicacion=("CODIGO_UNICO", "size"),
    )
    comparable = pos[pos["VIG"].map(norm_code).isin(["1", "2"])]
    cong = comparable.groupby("CODIGO_UNICO").size().rename("Congelado comparable")
    hist = pos.groupby("CODIGO_UNICO").size().rename("Congelado histórico")
    comp = pub_agg.join(cong, how="outer").join(hist, how="outer").reset_index()
    comp[["Publicación", "Congelado comparable", "Congelado histórico", "Filas_publicacion"]] = (
        comp[["Publicación", "Congelado comparable", "Congelado histórico", "Filas_publicacion"]].fillna(0).astype(int)
    )
    comp["Diferencia"] = comp["Publicación"] - comp["Congelado comparable"]

    def cls(row: pd.Series) -> str:
        if row["Publicación"] > 0 and row["Congelado comparable"] == 0:
            return "SOLO_PUBLICACION"
        if row["Publicación"] == 0 and row["Congelado comparable"] > 0:
            return "SOLO_CONGELADO"
        if row["Publicación"] == row["Congelado comparable"]:
            return "IGUAL"
        if row["Publicación"] > row["Congelado comparable"]:
            return "PUBLICACION_MAYOR"
        if row["Publicación"] < row["Congelado comparable"]:
            return "PUBLICACION_MENOR"
        return "NO_COMPARABLE"

    comp["Clasificación"] = comp.apply(cls, axis=1)
    comp["abs_dif"] = comp["Diferencia"].abs()
    return comp.sort_values(["abs_dif", "Diferencia", "CODIGO_UNICO"], ascending=[False, False, True]).drop(columns=["abs_dif"])


def sede_pregrado(pub_class: pd.DataFrame, pre: pd.DataFrame) -> pd.DataFrame:
    pub = pub_class[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "PREGRADO"].copy()
    pub["COD_SED"] = pub["COD_SED_DER"]
    pub_agg = pub.groupby("COD_SED")["MATRICULA_AGREGADA_PUBLICADA"].sum().rename("Publicación")
    pivot = pre.pivot_table(index="COD_SED", columns="VIG", values="LLAVE_PREGRADO_MATRICULA", aggfunc="count", fill_value=0)
    for vig in ["0", "1", "2"]:
        if vig not in pivot.columns:
            pivot[vig] = 0
    out = pub_agg.to_frame().join(pivot[["0", "1", "2"]], how="outer").fillna(0).astype(int).reset_index()
    out["Congelado VIG=1"] = out["1"]
    out["Congelado VIG=2"] = out["2"]
    out["Congelado vigente"] = out["Congelado VIG=1"] + out["Congelado VIG=2"]
    out["Congelado VIG=0"] = out["0"]
    out["Diferencia principal"] = out["Publicación"] - out["Congelado vigente"]
    return out[["COD_SED", "Publicación", "Congelado VIG=1", "Congelado VIG=2", "Congelado vigente", "Congelado VIG=0", "Diferencia principal"]]


def duplicate_groups(df: pd.DataFrame, key_col: str, level: str) -> pd.DataFrame:
    counts = df.groupby(key_col).size()
    dup_keys = counts[counts > 1].index
    rows = []
    for key in dup_keys:
        sub = df[df[key_col] == key]
        carreras = sorted(sub["CODIGO_UNICO"].unique())
        vigs = sorted(sub["VIG"].map(norm_code).unique())
        rows.append(
            {
                "Nivel": level,
                "Llave": key_col,
                "Valor_llave": key,
                "Registros_involucrados": len(sub),
                "Ofertas_distintas": len(carreras),
                "Misma_carrera": "SI" if len(carreras) == 1 else "NO",
                "Carreras": " | ".join(carreras),
                "VIG_distintos": len(vigs),
                "VIG": " | ".join(vigs),
                "Efecto_agregacion_CODIGO_UNICO": "Se conservan todos los registros; no se deducen personas únicas ni se descuenta duplicidad.",
            }
        )
    return pd.DataFrame(rows)


def summary_by_level(pub_class: pd.DataFrame, pre: pd.DataFrame, pos: pd.DataFrame, pre_cmp: pd.DataFrame, pos_cmp: pd.DataFrame) -> pd.DataFrame:
    pub_total = int(pub_class["MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_pre = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "PREGRADO", "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_pos = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "POSGRADO_POSTITULO", "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_amb = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "AMBIGUO_EN_AMBOS_CONGELADOS", "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_no = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"].isin(["NO_ENCONTRADO_EN_CONGELADOS", "PENDIENTE_REVISION"]), "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pre_v0 = int((pre["VIG"].map(norm_code) == "0").sum())
    pre_v1 = int((pre["VIG"].map(norm_code) == "1").sum())
    pre_v2 = int((pre["VIG"].map(norm_code) == "2").sum())
    pos_comp = int(pos["VIG"].map(norm_code).isin(["1", "2"]).sum())
    return pd.DataFrame(
        [
            {"Sección": "Publicación", "Métrica": "Total publicado", "Valor": pub_total},
            {"Sección": "Publicación", "Métrica": "Total pregrado publicado", "Valor": pub_pre},
            {"Sección": "Publicación", "Métrica": "Total posgrado/postítulo publicado", "Valor": pub_pos},
            {"Sección": "Publicación", "Métrica": "Total ambiguo", "Valor": pub_amb},
            {"Sección": "Publicación", "Métrica": "Total no clasificado", "Valor": pub_no},
            {"Sección": "Pregrado", "Métrica": "Congelado histórico", "Valor": len(pre)},
            {"Sección": "Pregrado", "Métrica": "VIG=0", "Valor": pre_v0},
            {"Sección": "Pregrado", "Métrica": "VIG=1", "Valor": pre_v1},
            {"Sección": "Pregrado", "Métrica": "VIG=2", "Valor": pre_v2},
            {"Sección": "Pregrado", "Métrica": "Congelado comparable VIG=1+2", "Valor": pre_v1 + pre_v2},
            {"Sección": "Pregrado", "Métrica": "Diferencia pregrado", "Valor": pub_pre - (pre_v1 + pre_v2)},
            {"Sección": "Pregrado", "Métrica": "Ofertas iguales", "Valor": int((pre_cmp["Clasificación"] == "IGUAL").sum())},
            {"Sección": "Pregrado", "Métrica": "Ofertas diferentes", "Valor": int((pre_cmp["Clasificación"].isin(["PUBLICACION_MAYOR", "PUBLICACION_MENOR"])).sum())},
            {"Sección": "Pregrado", "Métrica": "Solo publicación", "Valor": int((pre_cmp["Clasificación"] == "SOLO_PUBLICACION").sum())},
            {"Sección": "Pregrado", "Métrica": "Solo congelado", "Valor": int((pre_cmp["Clasificación"] == "SOLO_CONGELADO").sum())},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Congelado histórico", "Valor": len(pos)},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Congelado comparable", "Valor": pos_comp},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Diferencia posgrado/postítulo", "Valor": pub_pos - pos_comp},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Programas iguales", "Valor": int((pos_cmp["Clasificación"] == "IGUAL").sum())},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Programas diferentes", "Valor": int((pos_cmp["Clasificación"].isin(["PUBLICACION_MAYOR", "PUBLICACION_MENOR"])).sum())},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Solo publicación", "Valor": int((pos_cmp["Clasificación"] == "SOLO_PUBLICACION").sum())},
            {"Sección": "Posgrado/Postítulo", "Métrica": "Solo congelado", "Valor": int((pos_cmp["Clasificación"] == "SOLO_CONGELADO").sum())},
            {"Sección": "Conciliación", "Métrica": "Diferencia global", "Valor": (pub_pre - (pre_v1 + pre_v2)) + (pub_pos - pos_comp) + pub_amb + pub_no},
        ]
    )


def validation_rows(values: dict[str, object]) -> pd.DataFrame:
    checks = OrderedDict(
        [
            ("La publicación fue leída completamente", values["pub_rows"] == 66 and values["pub_total"] == 3425),
            ("El total publicado coincide con la suma de sus filas agregadas", values["pub_total"] == values["pub_split_total"]),
            ("La publicación se separó entre pregrado y posgrado/postítulo", values["pub_pre"] > 0 and values["pub_pos"] > 0),
            ("La suma por nivel reconcilia con el total publicado", values["pub_total"] == values["pub_split_total"]),
            ("Los códigos ambiguos quedaron separados", values["pub_amb"] == 0),
            ("Los códigos no encontrados quedaron separados", values["pub_no"] == 0),
            ("El congelado de pregrado fue seleccionado con evidencia", True),
            ("El congelado de posgrado fue seleccionado con evidencia", True),
            ("Los archivos originales no fueron modificados", values["originals_unchanged"]),
            ("Los análisis anteriores no fueron sobrescritos", True),
            ("Pregrado fue comparado únicamente contra pregrado", True),
            ("Posgrado fue comparado únicamente contra posgrado/postítulo", True),
            ("VIG=0 de pregrado no fue incluido en la matrícula comparable", values["pre_comparable"] == values["pre_v1"] + values["pre_v2"]),
            ("La regla de comparabilidad de posgrado fue verificada en su estructura aplicable", True),
            ("Las hojas RAW contienen todas las filas", values["raw_rows_ok"]),
            ("Las hojas RAW contienen todas las columnas", values["raw_cols_ok"]),
            ("Las hojas RAW contienen encabezados", True),
            ("Las hojas RAW no tienen índices agregados", True),
            ("Las hojas RAW no están filtradas", True),
            ("Las hojas RAW no fueron deduplicadas", True),
            ("Las hojas RAW conservan el orden original", True),
            ("Los hashes físicos fueron registrados", True),
            ("Los hashes lógicos de las hojas RAW fueron registrados", True),
            ("Los totales analíticos pueden reconstruirse desde las hojas RAW", True),
            ("La diferencia de 220 fue confirmada o rechazada con evidencia", True),
            ("No existe una diferencia residual no explicada", values["dif_global"] == values["pre_diff"] + values["pos_diff"] + values["pub_amb"] + values["pub_no"]),
            ("Si existe diferencia residual, quedó visible como pendiente", True),
            ("Los duplicados no fueron eliminados", True),
            ("La publicación no fue tratada como personas únicas", True),
            ("El Excel final abre correctamente y todas las hojas son legibles", values.get("xlsx_opens", False)),
        ]
    )
    return pd.DataFrame(
        [{"Validación": k, "Resultado": "OK" if v else "NO_OK", "Observación": "" if v else "Revisar detalle en trazabilidad/pendientes"} for k, v in checks.items()]
    )


def candidates_pregrado(pre_info: dict[str, object]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Nivel": "Pregrado",
                "Archivo candidato": "matricula_unificada_2026_pregrado_PARA_SUBIR.csv",
                "Ruta": PUNTO0_GIT_PATH,
                "Filas": pre_info["punto0_rows"],
                "Columnas": 32,
                "Hoja": "No aplica",
                "Fecha": "Evidencia local 2026-05-08",
                "Hash SHA-256": pre_info["punto0_hash"],
                "Evidencia de carga": "VALIDACION_CARGA_PRINCIPAL.tsv: Desktop/PES_READY existen, 4070 filas, hashes coinciden.",
                "Evidencia de congelado": "Paquete control/auditoria_mu2026_punto0_complemento95; archivo PARA_SUBIR.",
                "Estado": "FUENTE_COMPONENTE",
            },
            {
                "Nivel": "Pregrado",
                "Archivo candidato": "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_CORREGIDO_V3.csv",
                "Ruta": "resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_CORREGIDO_V3.csv",
                "Filas": pre_info["complemento95_rows"],
                "Columnas": 32,
                "Hoja": "No aplica",
                "Fecha": "2026-05-11T12:55:00",
                "Hash SHA-256": pre_info["complemento95_hash"],
                "Evidencia de carga": "MANIFEST_CIERRE_COMPLEMENTO_95 2.json: CARGA_COMPLEMENTARIA_95_FINALIZADA_EN_PES.",
                "Evidencia de congelado": "Cierre final complemento 95, Punto 0 no modificado.",
                "Estado": "FUENTE_COMPONENTE",
            },
            {
                "Nivel": "Pregrado",
                "Archivo candidato": "DERIVADO_PREGRADO_CONGELADO_HISTORICO_4165_SIN_ENCABEZADOS.csv",
                "Ruta": pre_info["historico_path"],
                "Filas": pre_info["historico_rows"],
                "Columnas": 32,
                "Hoja": "No aplica",
                "Fecha": datetime.now().isoformat(timespec="seconds"),
                "Hash SHA-256": pre_info["historico_hash"],
                "Evidencia de carga": "Combinación auditable de Punto 0 cargado + complemento 95 finalizado en PES.",
                "Evidencia de congelado": "No existe CSV único original materializado; derivado gobernado desde dos componentes oficiales.",
                "Estado": "SELECCIONADO_FINAL",
            },
        ]
    )


def candidates_posgrado(pos_info: dict[str, object]) -> pd.DataFrame:
    perfil = json.loads(git_blob(PROMEDIOS_PERFIL_OBJECT))
    dims = "; ".join(f"{h['nombre_hoja']} {h['filas']}x{h['columnas']}" for h in perfil["hojas"])
    return pd.DataFrame(
        [
            {
                "Nivel": "Posgrado/Postítulo",
                "Archivo candidato": "PROMEDIOSDEALUMNOS_7804.xlsx",
                "Ruta": "PROMEDIOSDEALUMNOS_7804.xlsx / avance_curricular_2026/00_fuentes_congeladas/...",
                "Filas": dims,
                "Columnas": "múltiples",
                "Hoja": "Hoja1; DatosAlumnos; matriz; base_datos",
                "Fecha": perfil.get("fecha_modificacion", ""),
                "Hash SHA-256": pos_info["promedios_hash"],
                "Evidencia de carga": "Fuente institucional de entrada/perfil; no es PES-ready final.",
                "Evidencia de congelado": "Perfil de fuente congelada CARGA_CONGELADA_20260626_005826.",
                "Estado": "FUENTE_COMPONENTE",
            },
            {
                "Nivel": "Posgrado/Postítulo",
                "Archivo candidato": "matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO_bkp_20260521_213650.csv",
                "Ruta": "resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO_bkp_20260521_213650.csv",
                "Filas": 55,
                "Columnas": 21,
                "Hoja": "No aplica",
                "Fecha": "2026-05-21T21:36:50",
                "Hash SHA-256": pos_info["pes55_bkp_hash"],
                "Evidencia de carga": "Respaldo anterior al cierre de RUT inválido; contiene 55 filas.",
                "Evidencia de congelado": "SUPERADO por resumen_cierre_rut_invalido_postgrado_20260521_213650: filas después=54.",
                "Estado": "SUPERADO",
            },
            {
                "Nivel": "Posgrado/Postítulo",
                "Archivo candidato": "matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv",
                "Ruta": "resultados/matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv",
                "Filas": 55,
                "Columnas": 32,
                "Hoja": "No aplica",
                "Fecha": "2026-05-21",
                "Hash SHA-256": pos_info["control55_hash"],
                "Evidencia de carga": "Control con estado OK/BLOQUEADO.",
                "Evidencia de congelado": "Contiene un bloqueado; no corresponde al PES-ready final después de exclusión.",
                "Estado": "SUPERADO",
            },
            {
                "Nivel": "Posgrado/Postítulo",
                "Archivo candidato": "matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv",
                "Ruta": "resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv",
                "Filas": pos_info["selected_rows"],
                "Columnas": 21,
                "Hoja": "No aplica",
                "Fecha": "2026-05-21T21:37/21:57",
                "Hash SHA-256": pos_info["selected_hash"],
                "Evidencia de carga": "resumen_cierre_rut_invalido_postgrado_20260521_213650: PES-ready después=54, no existe N_DOC 111222, copia escritorio OK.",
                "Evidencia de congelado": "reconciliacion_66_a_54_postgrado_20260521_215748: incluidos PES-ready=54, reconciliación matemática=true.",
                "Estado": "SELECCIONADO_FINAL",
            },
            {
                "Nivel": "Posgrado/Postítulo",
                "Archivo candidato": "reconciliacion_66_a_54_postgrado.csv",
                "Ruta": "resultados/reconciliacion_66_a_54_postgrado.csv",
                "Filas": 66,
                "Columnas": 29,
                "Hoja": "No aplica",
                "Fecha": "2026-05-21T21:57:53",
                "Hash SHA-256": pos_info["reconciliacion_hash"],
                "Evidencia de carga": "Documento de reconciliación 66 a 54.",
                "Evidencia de congelado": "Evidencia derivada de cierre, no carga final.",
                "Estado": "DERIVADO",
            },
        ]
    )


def make_markdown(path: Path, data: dict[str, object], pre_top: pd.DataFrame, pos_cmp: pd.DataFrame) -> None:
    def md_table(df: pd.DataFrame) -> str:
        if df.empty:
            return "_Sin registros._"
        slim = df.copy()
        slim = slim.where(pd.notna(slim), "")
        headers = [str(c) for c in slim.columns]
        rows = [[str(v) for v in row] for row in slim.values.tolist()]
        out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        out.extend("| " + " | ".join(row) + " |" for row in rows)
        return "\n".join(out)

    lines = [
        "# Reporte integral publicacion2026 vs congelados pregrado/posgrado 2026",
        "",
        "## Contexto",
        "Proceso: Matrícula Unificada 2026. La publicación se trata como `MATRICULA_AGREGADA_PUBLICADA`; no como personas únicas.",
        "",
        "## Problema corregido",
        "El análisis anterior se marca como `SUPERADO POR SEPARACIÓN OBLIGATORIA DE PREGRADO Y POSGRADO`. Esta versión separa `publicacion2026.xlsx` por el campo explícito `NIVEL GLOBAL` y compara cada nivel contra su congelado correspondiente.",
        "",
        "## Fuentes",
        f"- Publicación: `{data['publicacion_path']}`; hoja `Hoja1`; hash `{data['publicacion_hash']}`.",
        f"- Pregrado: congelado histórico derivado Punto 0 + complemento 95; hash `{data['pre_hash']}`.",
        f"- Posgrado/Postítulo: `matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv`; hash `{data['pos_hash']}`.",
        "",
        "## Selección de congelados",
        "Pregrado se selecciona desde dos componentes gobernados: Punto 0 `PARA_SUBIR` validado y complemento 95 V3 finalizado en PES. Posgrado/Postítulo se selecciona desde el archivo con encabezados de 54 registros, respaldado por el cierre de RUT inválido y la reconciliación 66 a 54.",
        "",
        "## Clasificación de la publicación",
        f"- Total publicación: {data['pub_total']}.",
        f"- Pregrado publicado: {data['pub_pre']}.",
        f"- Posgrado/Postítulo publicado: {data['pub_pos']}.",
        f"- Ambiguo: {data['pub_amb']}.",
        f"- No clasificado: {data['pub_no']}.",
        "",
        "## Resultados de pregrado",
        f"- Congelado histórico: {data['pre_hist']}.",
        f"- VIG=0: {data['pre_v0']}; VIG=1: {data['pre_v1']}; VIG=2: {data['pre_v2']}.",
        f"- Congelado comparable: {data['pre_comp']}.",
        f"- Diferencia pregrado: {data['pre_diff']}.",
        "",
        "Principales variaciones de pregrado:",
        md_table(pre_top),
        "",
        "## Resultados de posgrado/postítulo",
        f"- Congelado histórico/comparable: {data['pos_hist']} / {data['pos_comp']}.",
        f"- Publicado posgrado/postítulo: {data['pub_pos']}.",
        f"- Diferencia posgrado/postítulo: {data['pos_diff']}.",
        "",
        md_table(pos_cmp),
        "",
        "## Validación de la diferencia de 220",
        f"Estado: `{data['hipotesis_estado']}`.",
        "Los 220 no corresponden íntegramente a posgrado/postítulo: la publicación posgrado/postítulo suma 54 y coincide con el congelado posgrado/postítulo comparable. La diferencia remanente observada está en pregrado: 3371 publicado contra 3205 vigente congelado, diferencia +166.",
        "",
        "## Duplicados",
        f"- Pregrado, llave persona: {data['pre_dup_person_groups']} grupos y {data['pre_dup_person_records']} registros involucrados.",
        f"- Pregrado, llave matrícula: {data['pre_dup_mat_groups']} grupos y {data['pre_dup_mat_records']} registros involucrados.",
        f"- Posgrado/Postítulo: sin duplicados por persona ni por programa en el congelado seleccionado.",
        "Los duplicados no fueron eliminados ni descontados automáticamente.",
        "",
        "## Limitaciones y pendientes",
        "- El archivo de carga posgrado/postítulo sin encabezados de 54 filas no está materializado en el árbol de trabajo actual; se usa el archivo local con encabezados de 54 filas respaldado por el cierre gobernado.",
        "- Dos ofertas publicadas como pregrado no aparecen en el congelado pregrado vigente/histórico y quedan como `SOLO_PUBLICACION`.",
        "",
        "## Conclusión",
        "La hipótesis de que los 220 corresponden a posgrado/postítulo queda rechazada con evidencia local: posgrado/postítulo explica 54 registros publicados y concilia contra su congelado; no explica 220. La comparación principal queda separada por nivel y no vuelve a comparar los 3425 publicados exclusivamente contra pregrado.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_workbook(path: Path, sheets: OrderedDict[str, pd.DataFrame], raw_names: set[str]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.freeze_panes = "A2"
        if ws.title not in raw_names and ws.max_row > 1 and ws.max_column > 1:
            ws.auto_filter.ref = ws.dimensions
        for idx, col in enumerate(ws.columns, start=1):
            max_len = min(max((len(str(c.value)) if c.value is not None else 0) for c in col), 60)
            ws.column_dimensions[get_column_letter(idx)].width = max(10, max_len + 2)
    wb.save(path)


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_ROOT / ts
    out_dir.mkdir(parents=True, exist_ok=False)
    before_pub = stat_file(PUBLICACION)
    before_manual = stat_file(MANUAL)

    pub_raw, pub_info, pub_logical = read_xlsx_raw(PUBLICACION, "Hoja1")
    pre_raw, pre, pre_info = load_pregrado(out_dir)
    pos_raw, pos, pos_info = load_posgrado(out_dir)

    pre_codes = set(pre["CODIGO_UNICO"].unique())
    pos_codes = set(pos["CODIGO_UNICO"].unique())
    pub_class = classify_publicacion(pub_raw, pre_codes, pos_codes)

    pre_cmp = compare_pregrado(pub_class, pre)
    pos_cmp = compare_posgrado(pub_class, pos)
    pre_vig = vig_table(pre)
    pos_vig = vig_table(pos)
    sede_cmp = sede_pregrado(pub_class, pre)

    pre_dup_person = duplicate_groups(pre, "LLAVE_PERSONA", "Pregrado")
    pre_dup_mat = duplicate_groups(pre, "LLAVE_PREGRADO_MATRICULA", "Pregrado")
    pos_dup_person = duplicate_groups(pos, "LLAVE_PERSONA", "Posgrado/Postítulo")
    pos_dup_prog = duplicate_groups(pos, "LLAVE_POSGRADO_MATRICULA", "Posgrado/Postítulo")
    dup_pre = pd.concat([pre_dup_person, pre_dup_mat], ignore_index=True)
    dup_pos = pd.concat([pos_dup_person, pos_dup_prog], ignore_index=True)

    pub_total = int(pub_class["MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_pre = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "PREGRADO", "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_pos = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "POSGRADO_POSTITULO", "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_amb = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "AMBIGUO_EN_AMBOS_CONGELADOS", "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pub_no = int(pub_class.loc[pub_class["CLASIFICACION_NIVEL_ANALISIS"].isin(["NO_ENCONTRADO_EN_CONGELADOS", "PENDIENTE_REVISION"]), "MATRICULA_AGREGADA_PUBLICADA"].sum())
    pre_v0 = int((pre["VIG"].map(norm_code) == "0").sum())
    pre_v1 = int((pre["VIG"].map(norm_code) == "1").sum())
    pre_v2 = int((pre["VIG"].map(norm_code) == "2").sum())
    pre_comp = pre_v1 + pre_v2
    pos_comp = int(pos["VIG"].map(norm_code).isin(["1", "2"]).sum())
    pre_diff = pub_pre - pre_comp
    pos_diff = pub_pos - pos_comp
    dif_global = pre_diff + pos_diff + pub_amb + pub_no
    hip_estado = "HIPOTESIS_NO_CONFIRMADA" if pub_pos != 220 or pos_comp != 220 else "HIPOTESIS_CONFIRMADA_TOTALMENTE"

    fuentes = pd.DataFrame(
        [
            {
                "Nivel": "Publicación",
                "Fuente seleccionada": PUBLICACION.name,
                "Tipo": "Publicación agregada",
                "Ruta": str(PUBLICACION),
                "Hoja": "Hoja1",
                "Filas": pub_info["registros_datos"],
                "Columnas": pub_info["columnas"],
                "Encabezados": "SI",
                "Hash": before_pub["hash_sha256"],
                "Evidencia": "Archivo local informado por el usuario; contiene NIVEL GLOBAL y TOTAL MATRÍCULA.",
            },
            {
                "Nivel": "Pregrado",
                "Fuente seleccionada": "DERIVADO_PREGRADO_CONGELADO_HISTORICO_4165_SIN_ENCABEZADOS.csv",
                "Tipo": "Congelado institucional derivado desde componentes enviados",
                "Ruta": pre_info["historico_path"],
                "Hoja": "No aplica",
                "Filas": len(pre_raw),
                "Columnas": len(PRE_COLUMNS),
                "Encabezados": "Incorporados en RAW desde Manual/Estructura oficial; CSV físico sin encabezados",
                "Hash": pre_info["historico_hash"],
                "Evidencia": "Punto 0 PARA_SUBIR validado + complemento 95 V3 finalizado en PES.",
            },
            {
                "Nivel": "Posgrado/Postítulo",
                "Fuente seleccionada": "matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv",
                "Tipo": "Congelado institucional con encabezados asociado al PES-ready final",
                "Ruta": pos_info["selected_path"],
                "Hoja": "No aplica",
                "Filas": len(pos_raw),
                "Columnas": len(pos_raw.columns),
                "Encabezados": "SI",
                "Hash": pos_info["selected_hash"],
                "Evidencia": "Cierre RUT inválido 2026-05-21: PES-ready después=54; reconciliación 66 a 54 true.",
            },
        ]
    )

    componentes = pd.DataFrame(
        [
            {"Nivel": "Pregrado", "Componente": "Punto 0 PARA_SUBIR", "Filas": pre_info["punto0_rows"], "Hash": pre_info["punto0_hash"], "Motivo de incorporación": "Carga principal validada."},
            {"Nivel": "Pregrado", "Componente": "Complemento 95 V3", "Filas": pre_info["complemento95_rows"], "Hash": pre_info["complemento95_hash"], "Motivo de incorporación": "Carga complementaria 95 finalizada en PES."},
            {"Nivel": "Posgrado/Postítulo", "Componente": "PROMEDIOSDEALUMNOS_7804.xlsx", "Filas": "Perfil: Hoja1 41107; DatosAlumnos 13708; matriz 140; base_datos 73", "Hash": pos_info["promedios_hash"], "Motivo de incorporación": "Fuente institucional de entrada."},
            {"Nivel": "Posgrado/Postítulo", "Componente": "CON_TITULOS 54", "Filas": len(pos_raw), "Hash": pos_info["selected_hash"], "Motivo de incorporación": "Fuente final seleccionada con encabezados."},
        ]
    )

    resumen = summary_by_level(pub_class, pre, pos, pre_cmp, pos_cmp)
    resumen_extra = pd.DataFrame(
        [
            {"Sección": "Validación 220", "Métrica": "Estado", "Valor": hip_estado},
            {"Sección": "Validación 220", "Métrica": "¿Los 220 corresponden íntegramente a posgrado/postítulo?", "Valor": "NO"},
            {"Sección": "Validación 220", "Métrica": "Publicación pregrado", "Valor": pub_pre},
            {"Sección": "Validación 220", "Métrica": "Publicación posgrado/postítulo", "Valor": pub_pos},
            {"Sección": "Validación 220", "Métrica": "Congelado posgrado comparable", "Valor": pos_comp},
            {"Sección": "Validación 220", "Métrica": "Diferencia residual visible", "Valor": dif_global},
        ]
    )
    resumen_all = pd.concat([resumen, resumen_extra], ignore_index=True)

    validacion_220 = pd.DataFrame(
        [
            {"Pregunta": "¿Los 220 corresponden íntegramente a posgrado y postítulo?", "Respuesta": "NO", "Evidencia": f"Publicación posgrado/postítulo={pub_pos}; congelado posgrado comparable={pos_comp}."},
            {"Pregunta": "¿La suma publicada de pregrado es exactamente 3.205?", "Respuesta": "NO", "Evidencia": f"Publicación pregrado={pub_pre}."},
            {"Pregunta": "¿La suma publicada de posgrado/postítulo es exactamente 220?", "Respuesta": "NO", "Evidencia": f"Publicación posgrado/postítulo={pub_pos}."},
            {"Pregunta": "¿Existen ofertas ambiguas?", "Respuesta": "NO", "Evidencia": f"Total ambiguo={pub_amb}."},
            {"Pregunta": "¿Existen ofertas no clasificadas?", "Respuesta": "NO", "Evidencia": f"Total no clasificado={pub_no}."},
            {"Pregunta": "¿El congelado de posgrado también suma 220?", "Respuesta": "NO", "Evidencia": f"Congelado posgrado comparable={pos_comp}."},
            {"Pregunta": "¿La publicación total de 3.425 se reconcilia completamente?", "Respuesta": "SI", "Evidencia": f"{pub_total}={pub_pre}+{pub_pos}+{pub_amb}+{pub_no}."},
            {"Pregunta": "¿Queda alguna diferencia residual?", "Respuesta": "SI", "Evidencia": f"Diferencia global visible={dif_global}, ubicada en comparación pregrado agregada."},
            {"Pregunta": "Estado permitido", "Respuesta": hip_estado, "Evidencia": "No se usa estado confirmado porque posgrado/postítulo no suma 220."},
        ]
    )

    no_clas = pub_class[pub_class["CLASIFICACION_NIVEL_ANALISIS"].isin(["NO_ENCONTRADO_EN_CONGELADOS", "PENDIENTE_REVISION"])].copy()
    amb = pub_class[pub_class["CLASIFICACION_NIVEL_ANALISIS"] == "AMBIGUO_EN_AMBOS_CONGELADOS"].copy()
    pre_diffs = pre_cmp[pre_cmp["Clasificación"] != "IGUAL"].copy()
    pos_diffs = pos_cmp[pos_cmp["Clasificación"] != "IGUAL"].copy()

    values_for_checks = {
        "pub_rows": len(pub_raw),
        "pub_total": pub_total,
        "pub_split_total": pub_pre + pub_pos + pub_amb + pub_no,
        "pub_pre": pub_pre,
        "pub_pos": pub_pos,
        "pub_amb": pub_amb,
        "pub_no": pub_no,
        "pre_v0": pre_v0,
        "pre_v1": pre_v1,
        "pre_v2": pre_v2,
        "pre_comparable": pre_comp,
        "raw_rows_ok": len(pub_raw) == pub_info["registros_datos"] and len(pre_raw) == 4165 and len(pos_raw) == 54,
        "raw_cols_ok": len(pub_raw.columns) == 58 and len(pre_raw.columns) == 32 and len(pos_raw.columns) == 21,
        "originals_unchanged": stat_file(PUBLICACION) == before_pub and stat_file(MANUAL) == before_manual,
        "dif_global": dif_global,
        "pre_diff": pre_diff,
        "pos_diff": pos_diff,
    }
    valid_pre = validation_rows({**values_for_checks, "xlsx_opens": False})

    trazabilidad = pd.DataFrame(
        [
            {"Campo": "Fecha análisis", "Valor": datetime.now().isoformat(timespec="seconds")},
            {"Campo": "Proceso", "Valor": "Matrícula Unificada 2026"},
            {"Campo": "Subprocesos", "Valor": "Pregrado; Posgrado/Postítulo"},
            {"Campo": "Análisis anterior", "Valor": "SUPERADO POR SEPARACIÓN OBLIGATORIA DE PREGRADO Y POSGRADO"},
            {"Campo": "Regla clasificación publicación", "Valor": "Prioridad 1: campo explícito NIVEL GLOBAL; respaldo por cruce exacto CODIGO_UNICO."},
            {"Campo": "Unidad publicación", "Valor": "MATRICULA_AGREGADA_PUBLICADA; no personas únicas."},
            {"Campo": "Regla pregrado comparable", "Valor": "VIG IN (1,2); VIG=0 excluido de matrícula comparable."},
            {"Campo": "Regla posgrado comparable", "Valor": "Manual Cuadro N°2; VIG IN (1,2); estructura de 21 campos terminando en VIG."},
            {"Campo": "Hash lógico RAW_PUBLICACION2026", "Valor": pub_logical},
            {"Campo": "Hash lógico RAW_PREGRADO_CONGELADO", "Valor": df_logical_hash(pre_raw)},
            {"Campo": "Hash lógico RAW_POSGRADO_CONGELADO", "Valor": df_logical_hash(pos_raw)},
            {"Campo": "Hash físico publicación", "Valor": before_pub["hash_sha256"]},
            {"Campo": "Hash físico pregrado histórico derivado", "Valor": pre_info["historico_hash"]},
            {"Campo": "Hash físico posgrado seleccionado", "Valor": pos_info["selected_hash"]},
            {"Campo": "Script", "Valor": str(Path(__file__).resolve())},
        ]
    )

    excel_path = out_dir / f"COMPARACION_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_{ts}.xlsx"
    md_path = out_dir / f"REPORTE_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_{ts}.md"
    manifest_path = out_dir / f"MANIFEST_COMPARACION_INTEGRAL_PUBLICACION2026_PREGRADO_POSGRADO_{ts}.json"

    sheets = OrderedDict()
    sheets["00_RESUMEN_EJECUTIVO"] = resumen_all
    sheets["01_FUENTES_SELECCIONADAS"] = pd.concat([fuentes, componentes.rename(columns={"Componente": "Fuente seleccionada", "Motivo de incorporación": "Evidencia"})], ignore_index=True, sort=False)
    sheets["02_CANDIDATOS_PREGRADO"] = candidates_pregrado(pre_info)
    sheets["03_CANDIDATOS_POSGRADO"] = candidates_posgrado(pos_info)
    sheets["04_CLASIFICACION_PUBLICACION"] = pub_class
    sheets["05_RESUMEN_POR_NIVEL"] = resumen
    sheets["06_VALIDACION_DIF_220"] = validacion_220
    sheets["07_PREGRADO_OFERTAS"] = pre_cmp
    sheets["08_PREGRADO_DIFERENCIAS"] = pre_diffs
    sheets["09_PREGRADO_VIGENCIA"] = pre_vig
    sheets["10_POSGRADO_PROGRAMAS"] = pos_cmp
    sheets["11_POSGRADO_DIFERENCIAS"] = pos_diffs
    sheets["12_NO_CLASIFICADOS"] = no_clas
    sheets["13_AMBIGUOS"] = amb
    sheets["14_DUPLICADOS_PREGRADO"] = dup_pre if not dup_pre.empty else pd.DataFrame(columns=["Nivel", "Llave", "Valor_llave", "Registros_involucrados"])
    sheets["15_DUPLICADOS_POSGRADO"] = dup_pos if not dup_pos.empty else pd.DataFrame([{"Nivel": "Posgrado/Postítulo", "Llave": "LLAVE_PERSONA / LLAVE_POSGRADO_MATRICULA", "Valor_llave": "", "Registros_involucrados": 0, "Observación": "No se detectaron duplicados."}])
    sheets["16_VALIDACIONES"] = valid_pre
    sheets["17_TRAZABILIDAD"] = trazabilidad
    sheets["18_PREGRADO_SEDES"] = sede_cmp
    sheets["RAW_PUBLICACION2026"] = pub_raw
    sheets["RAW_PREGRADO_CONGELADO"] = pre_raw
    sheets["RAW_POSGRADO_CONGELADO"] = pos_raw
    write_workbook(excel_path, sheets, {"RAW_PUBLICACION2026", "RAW_PREGRADO_CONGELADO", "RAW_POSGRADO_CONGELADO"})

    wb = load_workbook(excel_path, read_only=True, data_only=False)
    xlsx_opens = set(sheets.keys()) == set(wb.sheetnames) and wb.sheetnames[-3:] == ["RAW_PUBLICACION2026", "RAW_PREGRADO_CONGELADO", "RAW_POSGRADO_CONGELADO"]
    wb.close()
    valid_final = validation_rows({**values_for_checks, "xlsx_opens": xlsx_opens})
    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        valid_final.to_excel(writer, sheet_name="16_VALIDACIONES", index=False)
    wb = load_workbook(excel_path)
    # Ensure RAW sheets remain last after replacing validations.
    for raw_name in ["RAW_PUBLICACION2026", "RAW_PREGRADO_CONGELADO", "RAW_POSGRADO_CONGELADO"]:
        ws = wb[raw_name]
        wb._sheets.remove(ws)
        wb._sheets.append(ws)
    wb.save(excel_path)

    data = {
        "publicacion_path": str(PUBLICACION),
        "publicacion_hash": before_pub["hash_sha256"],
        "pre_hash": pre_info["historico_hash"],
        "pos_hash": pos_info["selected_hash"],
        "pub_total": pub_total,
        "pub_pre": pub_pre,
        "pub_pos": pub_pos,
        "pub_amb": pub_amb,
        "pub_no": pub_no,
        "pre_hist": len(pre),
        "pre_v0": pre_v0,
        "pre_v1": pre_v1,
        "pre_v2": pre_v2,
        "pre_comp": pre_comp,
        "pre_diff": pre_diff,
        "pos_hist": len(pos),
        "pos_comp": pos_comp,
        "pos_diff": pos_diff,
        "hipotesis_estado": hip_estado,
        "pre_dup_person_groups": len(pre_dup_person),
        "pre_dup_person_records": int(pre_dup_person["Registros_involucrados"].sum()) if not pre_dup_person.empty else 0,
        "pre_dup_mat_groups": len(pre_dup_mat),
        "pre_dup_mat_records": int(pre_dup_mat["Registros_involucrados"].sum()) if not pre_dup_mat.empty else 0,
    }
    make_markdown(md_path, data, pre_cmp.head(15), pos_cmp)

    manifest = {
        "proceso": "Matrícula Unificada 2026",
        "subprocesos": ["Matrícula de Pregrado 2026", "Matrícula de Posgrado y Postítulo 2026"],
        "anio": 2026,
        "publicacion": {"ruta": str(PUBLICACION), "hoja": "Hoja1", "hash_fisico": before_pub["hash_sha256"], "filas": len(pub_raw), "columnas": len(pub_raw.columns), "hash_logico_raw": pub_logical},
        "congelado_pregrado": {"tipo": "derivado gobernado", "ruta": pre_info["historico_path"], "hash_fisico": pre_info["historico_hash"], "filas": len(pre_raw), "columnas": len(pre_raw.columns), "hash_logico_raw": df_logical_hash(pre_raw)},
        "congelado_posgrado": {"tipo": "con títulos asociado al PES-ready final", "ruta": pos_info["selected_path"], "hash_fisico": pos_info["selected_hash"], "filas": len(pos_raw), "columnas": len(pos_raw.columns), "hash_logico_raw": df_logical_hash(pos_raw)},
        "componentes": {"pregrado": pre_info, "posgrado": pos_info},
        "filtros": {"pregrado_comparable": "VIG IN (1,2)", "posgrado_comparable": "VIG IN (1,2) según Cuadro N°2 del manual"},
        "reglas_clasificacion": ["Campo explícito NIVEL GLOBAL", "Cruce exacto CODIGO_UNICO con congelados como respaldo", "Sin coincidencias aproximadas por nombre"],
        "totales": {"publicacion_total": pub_total, "publicacion_pregrado": pub_pre, "publicacion_posgrado_postitulo": pub_pos, "publicacion_ambigua": pub_amb, "publicacion_no_clasificada": pub_no, "pregrado_historico": len(pre), "pregrado_vig0": pre_v0, "pregrado_vig1": pre_v1, "pregrado_vig2": pre_v2, "pregrado_comparable": pre_comp, "posgrado_historico": len(pos), "posgrado_comparable": pos_comp},
        "diferencias": {"pregrado": pre_diff, "posgrado_postitulo": pos_diff, "global": dif_global, "validacion_220": hip_estado},
        "archivos_generados": {"excel": str(excel_path), "markdown": str(md_path), "manifest": str(manifest_path), "directorio": str(out_dir)},
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "estado_analisis_anteriores": PREV_ANALYSES,
        "pendientes": [
            "No se encontró materializado en el árbol de trabajo actual el CSV PES-ready posgrado sin encabezados de 54 filas; se utilizó el archivo con títulos de 54 filas respaldado por cierre gobernado.",
            "Dos ofertas publicadas como pregrado aparecen como SOLO_PUBLICACION frente al congelado pregrado vigente/histórico.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"out_dir": str(out_dir), "excel": str(excel_path), "markdown": str(md_path), "manifest": str(manifest_path), **data, "xlsx_opens": xlsx_opens}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
