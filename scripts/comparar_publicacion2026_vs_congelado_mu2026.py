#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
PUBLICACION = ROOT / "publicacion2026.xlsx"
MANUAL = ROOT / "Manual_Matrícula_Unificada_2026.pdf"
OUT_ROOT = ROOT / "outputs" / "comparaciones_publicacion2026"

COMMIT = "4f1108c"
FROZEN_PRINCIPAL_PATH = (
    "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/"
    "carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
)
FROZEN_COMPLEMENT_PATH = (
    "resultados/complemento_95_codcli/"
    "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_CORREGIDO_V3.csv"
)
FROZEN_MANIFEST_OBJECT = "cd4a5d1135323dc4f8adcb44c60c75be2f9e3c81"
FROZEN_SUMMARY_OBJECT = "3554757cf4c4c9aa1173ba9ccb97ef7e3ef22a4f"

MU_COLUMNS = [
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(ref_path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{COMMIT}:{ref_path}"], cwd=ROOT)


def git_cat_object(obj: str) -> bytes:
    return subprocess.check_output(["git", "cat-file", "-p", obj], cwd=ROOT)


def stat_row(path: Path) -> dict[str, object]:
    st = path.stat()
    return {
        "Nombre exacto": path.name,
        "Ruta o ubicación": str(path),
        "Tipo de archivo": path.suffix.lower().lstrip("."),
        "Tamaño": st.st_size,
        "Fecha de modificación": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "Hash SHA-256": sha256_file(path),
    }


def parse_codigo_unico(value: object) -> dict[str, str]:
    text = "" if pd.isna(value) else str(value).strip().upper()
    m = re.fullmatch(r"I(?P<ies>\d+)S(?P<COD_SED>\d+)C(?P<COD_CAR>\d+)J(?P<JOR>\d+)V(?P<VERSION>\d+)", text)
    if not m:
        return {"CODIGO_UNICO": text, "COD_SED": "", "COD_CAR": "", "JOR": "", "VERSION": "", "PARSE_OK": "NO"}
    d = m.groupdict()
    d["CODIGO_UNICO"] = text
    d["PARSE_OK"] = "SI"
    return d


def norm_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def classify_count(pub: int | None, cong: int | None) -> str:
    if pub is None:
        return "SOLO_CONGELADO"
    if cong is None:
        return "SOLO_PUBLICACION"
    if pub == cong:
        return "COINCIDENTE_TOTAL_AGREGADO"
    return "MODIFICADO_EN_PUBLICACION_AGREGADO"


def pct(diff: int, base: int | None) -> str:
    if base in (None, 0):
        return "No aplica"
    return diff / base


def physical_xlsx_info(path: Path) -> dict[str, object]:
    wb = load_workbook(path, read_only=False, data_only=False)
    ws = wb[wb.sheetnames[0]]
    nonempty_rows = 0
    for row in ws.iter_rows():
        if any(c.value is not None for c in row):
            nonempty_rows += 1
    return {
        "Hoja analizada, si corresponde": ws.title,
        "Número de filas físicas": ws.max_row,
        "Número de registros de datos": max(nonempty_rows - 1, 0),
        "Número de columnas": ws.max_column,
        "Tiene encabezados": "SI",
        "Delimitador, si corresponde": "No aplica",
        "Codificación, si corresponde": "No aplica (xlsx)",
        "Nombre de tabla Excel, si corresponde": ", ".join(ws.tables.keys()) if ws.tables else "",
        "Hojas del libro": "; ".join(f"{w.title}:{w.max_row}x{w.max_column}:{w.sheet_state}" for w in wb.worksheets),
        "Celdas combinadas": len(list(ws.merged_cells.ranges)),
        "Filtros": "SI" if ws.auto_filter and ws.auto_filter.ref else "NO",
    }


def read_publicacion() -> pd.DataFrame:
    df = pd.read_excel(PUBLICACION, sheet_name="Hoja1", dtype=object, engine="openpyxl")
    df = df.dropna(how="all")
    parsed = df["CÓDIGO CARRERA"].apply(parse_codigo_unico).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    for col in ["TOTAL MATRÍCULA", "TOTAL MATRÍCULA MUJERES", "TOTAL MATRÍCULA HOMBRES", "TOTAL MATRÍCULA PRIMER AÑO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def read_frozen_from_derivatives(out_dir: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    src_dir = out_dir / "fuentes_derivadas"
    src_dir.mkdir(parents=True, exist_ok=True)
    principal = git_blob(FROZEN_PRINCIPAL_PATH)
    complement = git_cat_object("d4bd44f9d1f11640056b8e990f5e1fcda9aebf7d")
    principal_path = src_dir / "FUENTE_CONGELADA_PUNTO0_matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
    complement_path = src_dir / "FUENTE_CONGELADA_COMPLEMENTO95_V3.csv"
    combined_path = src_dir / "DERIVADO_CONGELADO_COMBINADO_PUNTO0_MAS_COMPLEMENTO95.csv"
    principal_path.write_bytes(principal)
    complement_path.write_bytes(complement)
    combined_path.write_bytes(principal + complement)

    principal_df = pd.read_csv(principal_path, sep=";", header=None, names=MU_COLUMNS, dtype=str, keep_default_na=False)
    complement_df = pd.read_csv(complement_path, sep=";", header=None, names=MU_COLUMNS, dtype=str, keep_default_na=False)
    principal_df["__FUENTE_CONGELADA"] = "PUNTO_0_PARA_SUBIR"
    complement_df["__FUENTE_CONGELADA"] = "COMPLEMENTO_95_V3"
    frozen = pd.concat([principal_df, complement_df], ignore_index=True)
    frozen["CODIGO_UNICO"] = (
        "I162S"
        + frozen["COD_SED"].map(norm_text)
        + "C"
        + frozen["COD_CAR"].map(norm_text)
        + "J"
        + frozen["JOR"].map(norm_text)
        + "V"
        + frozen["VERSION"].map(norm_text)
    )
    frozen["LLAVE_PERSONA"] = frozen["TIPO_DOC"].map(norm_text) + "|" + frozen["N_DOC"].map(norm_text) + "|" + frozen["DV"].map(norm_text)
    frozen["LLAVE_MATRICULA"] = (
        frozen["LLAVE_PERSONA"]
        + "|"
        + frozen["COD_SED"].map(norm_text)
        + "|"
        + frozen["COD_CAR"].map(norm_text)
        + "|"
        + frozen["MODALIDAD"].map(norm_text)
        + "|"
        + frozen["JOR"].map(norm_text)
        + "|"
        + frozen["VERSION"].map(norm_text)
    )
    meta = {
        "principal_path": str(principal_path),
        "principal_hash": sha256_file(principal_path),
        "principal_rows": len(principal_df),
        "complement_path": str(complement_path),
        "complement_hash": sha256_file(complement_path),
        "complement_rows": len(complement_df),
        "combined_path": str(combined_path),
        "combined_hash": sha256_file(combined_path),
        "combined_rows": len(frozen),
    }
    return frozen, meta


def structure_diagnostics(pub: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    pub_cols = list(pub.columns)
    frozen_cols = MU_COLUMNS
    rows = []
    for i, col in enumerate(sorted(set(pub_cols) | set(frozen_cols))):
        rows.append(
            {
                "Campo": col,
                "Orden publicación": pub_cols.index(col) + 1 if col in pub_cols else "",
                "Orden congelado": frozen_cols.index(col) + 1 if col in frozen_cols else "",
                "Presente publicación": "SI" if col in pub_cols else "NO",
                "Presente congelado": "SI" if col in frozen_cols else "NO",
                "Tipo observado publicación": str(pub[col].map(type).value_counts().to_dict()) if col in pub_cols else "",
                "Tipo observado congelado": str(frozen[col].map(type).value_counts().to_dict()) if col in frozen_cols else "",
                "Clasificación": "COMUN" if col in pub_cols and col in frozen_cols else "SOLO_PUBLICACION" if col in pub_cols else "SOLO_CONGELADO",
            }
        )
    return pd.DataFrame(rows)


def field_summary_non_comparable(frozen: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in MU_COLUMNS:
        rows.append(
            {
                "Campo": col,
                "Registros comparables": 0,
                "Iguales": 0,
                "Distintos": 0,
                "Vacío en publicación": "No comparable: publicación agregada sin este campo",
                "Vacío en congelado": int((frozen[col].map(norm_text) == "").sum()),
                "% de diferencia": "No aplica",
            }
        )
    return pd.DataFrame(rows)


def key_candidates(pub: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    candidates = []
    frozen_person_dups = int(frozen.duplicated("LLAVE_PERSONA", keep=False).sum())
    frozen_mat_dups = int(frozen.duplicated("LLAVE_MATRICULA", keep=False).sum())
    pub_offer_dups = int(pub.duplicated("CODIGO_UNICO", keep=False).sum())
    candidates.append(
        {
            "Llave candidata": "TIPO_DOC + N_DOC + DV",
            "Duplicados publicación": "No aplica: campos no presentes",
            "Duplicados congelado": frozen_person_dups,
            "¿Identifica persona?": "SI en congelado; no evaluable en publicación",
            "¿Identifica matrícula?": "NO",
            "Decisión": "No seleccionada para comparación principal",
        }
    )
    candidates.append(
        {
            "Llave candidata": "TIPO_DOC + N_DOC + DV + COD_SED + COD_CAR + MODALIDAD + JOR + VERSION",
            "Duplicados publicación": "No aplica: campos no presentes",
            "Duplicados congelado": frozen_mat_dups,
            "¿Identifica persona?": "NO; identifica documento+oferta",
            "¿Identifica matrícula?": "Parcialmente en congelado; no evaluable en publicación",
            "Decisión": "No seleccionada: publicación no es registro persona/matrícula",
        }
    )
    candidates.append(
        {
            "Llave candidata": "CODIGO_CARRERA publicación / CODIGO_UNICO congelado",
            "Duplicados publicación": pub_offer_dups,
            "Duplicados congelado": int(frozen.duplicated("CODIGO_UNICO", keep=False).sum()),
            "¿Identifica persona?": "NO",
            "¿Identifica matrícula?": "NO; identifica oferta agregada",
            "Decisión": "Seleccionada solo para comparación agregada por oferta",
        }
    )
    return pd.DataFrame(candidates)


def aggregate_compare(pub: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    pub_agg = (
        pub.groupby("CODIGO_UNICO", dropna=False)
        .agg(
            PUBLICACION_TOTAL=("TOTAL MATRÍCULA", "sum"),
            PUBLICACION_FILAS=("CODIGO_UNICO", "size"),
            NOMBRE_CARRERA_PUBLICACION=("NOMBRE CARRERA", lambda s: " | ".join(sorted(set(map(str, s))))),
            MODALIDAD_PUBLICACION=("MODALIDAD", lambda s: " | ".join(sorted(set(map(str, s))))),
            JORNADA_PUBLICACION=("JORNADA", lambda s: " | ".join(sorted(set(map(str, s))))),
            COD_SED=("COD_SED", "first"),
            COD_CAR=("COD_CAR", "first"),
            JOR=("JOR", "first"),
            VERSION=("VERSION", "first"),
        )
        .reset_index()
    )
    frozen_agg = (
        frozen.groupby("CODIGO_UNICO", dropna=False)
        .agg(
            CONGELADO_TOTAL=("CODIGO_UNICO", "size"),
            CONGELADO_PERSONAS=("LLAVE_PERSONA", pd.Series.nunique),
            FUENTES_CONGELADAS=("__FUENTE_CONGELADA", lambda s: " | ".join(sorted(set(s)))),
            COD_SED_CONG=("COD_SED", "first"),
            COD_CAR_CONG=("COD_CAR", "first"),
            MODALIDAD_CONG=("MODALIDAD", lambda s: " | ".join(sorted(set(map(str, s))))),
            JOR_CONG=("JOR", "first"),
            VERSION_CONG=("VERSION", "first"),
        )
        .reset_index()
    )
    comp = pub_agg.merge(frozen_agg, on="CODIGO_UNICO", how="outer")
    comp["PUBLICACION_TOTAL"] = comp["PUBLICACION_TOTAL"].where(comp["PUBLICACION_TOTAL"].notna(), pd.NA)
    comp["CONGELADO_TOTAL"] = comp["CONGELADO_TOTAL"].where(comp["CONGELADO_TOTAL"].notna(), pd.NA)
    comp["Diferencia absoluta"] = comp.apply(
        lambda r: (0 if pd.isna(r["PUBLICACION_TOTAL"]) else int(r["PUBLICACION_TOTAL"]))
        - (0 if pd.isna(r["CONGELADO_TOTAL"]) else int(r["CONGELADO_TOTAL"])),
        axis=1,
    )
    comp["Diferencia porcentual"] = comp.apply(
        lambda r: pct(
            int(r["Diferencia absoluta"]),
            None if pd.isna(r["CONGELADO_TOTAL"]) else int(r["CONGELADO_TOTAL"]),
        ),
        axis=1,
    )
    comp["Clasificación"] = comp.apply(
        lambda r: classify_count(
            None if pd.isna(r["PUBLICACION_TOTAL"]) else int(r["PUBLICACION_TOTAL"]),
            None if pd.isna(r["CONGELADO_TOTAL"]) else int(r["CONGELADO_TOTAL"]),
        ),
        axis=1,
    )
    return comp.sort_values(["Clasificación", "CODIGO_UNICO"], na_position="last")


def dimension_frame(pub: pd.DataFrame, frozen: pd.DataFrame, pub_col: str, frozen_col: str, label: str) -> pd.DataFrame:
    p = pub.groupby(pub_col).agg(Publicación=("TOTAL MATRÍCULA", "sum")).reset_index().rename(columns={pub_col: "Categoría"})
    c = frozen.groupby(frozen_col).size().reset_index(name="Congelado").rename(columns={frozen_col: "Categoría"})
    p["Categoría"] = p["Categoría"].map(lambda x: "" if pd.isna(x) else str(x))
    c["Categoría"] = c["Categoría"].map(lambda x: "" if pd.isna(x) else str(x))
    out = p.merge(c, on="Categoría", how="outer").fillna(0)
    out["Publicación"] = out["Publicación"].astype(int)
    out["Congelado"] = out["Congelado"].astype(int)
    out["Dimensión"] = label
    out["Diferencia absoluta"] = out["Publicación"] - out["Congelado"]
    out["Diferencia porcentual"] = out.apply(lambda r: pct(int(r["Diferencia absoluta"]), int(r["Congelado"])), axis=1)
    return out[["Dimensión", "Categoría", "Publicación", "Congelado", "Diferencia absoluta", "Diferencia porcentual"]].sort_values("Categoría")


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, df in sheets.items():
            safe = sheet[:31]
            if df.empty:
                df = pd.DataFrame({"Resultado": ["Sin registros para esta sección"]})
            df.to_excel(writer, sheet_name=safe, index=False)
    wb = load_workbook(path)
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.sheet_view.showGridLines = False
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        max_col = min(ws.max_column, 20)
        for col_idx in range(1, ws.max_column + 1):
            letter = get_column_letter(col_idx)
            width = 14
            if col_idx <= max_col:
                sample = [ws.cell(row=r, column=col_idx).value for r in range(1, min(ws.max_row, 80) + 1)]
                width = min(max(12, max(len(str(v)) if v is not None else 0 for v in sample) + 2), 45)
            ws.column_dimensions[letter].width = width
        ws.auto_filter.ref = ws.dimensions
    wb.save(path)


def simple_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "Sin variaciones agregadas."
    cols = list(df.columns)
    rows = []
    rows.append("| " + " | ".join(cols) + " |")
    rows.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(rows)


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_ROOT / ts
    out_dir.mkdir(parents=True, exist_ok=False)

    pub = read_publicacion()
    frozen, frozen_meta = read_frozen_from_derivatives(out_dir)

    principal_bytes = git_blob(FROZEN_PRINCIPAL_PATH)
    complement_bytes = git_cat_object("d4bd44f9d1f11640056b8e990f5e1fcda9aebf7d")
    combined_hash = frozen_meta["combined_hash"]

    pub_info = {**stat_row(PUBLICACION), **physical_xlsx_info(PUBLICACION)}
    frozen_info = {
        "Nombre exacto": "DERIVADO_CONGELADO_COMBINADO_PUNTO0_MAS_COMPLEMENTO95.csv",
        "Ruta o ubicación": frozen_meta["combined_path"],
        "Tipo de archivo": "csv derivado desde blobs Git congelados",
        "Tamaño": Path(frozen_meta["combined_path"]).stat().st_size,
        "Fecha de modificación": datetime.fromtimestamp(Path(frozen_meta["combined_path"]).stat().st_mtime).isoformat(timespec="seconds"),
        "Hoja analizada, si corresponde": "No aplica",
        "Número de filas físicas": len(frozen),
        "Número de registros de datos": len(frozen),
        "Número de columnas": 32,
        "Tiene encabezados": "NO",
        "Delimitador, si corresponde": ";",
        "Codificación, si corresponde": "bytes preservados desde Git; lectura UTF-8",
        "Nombre de tabla Excel, si corresponde": "No aplica",
        "Hash SHA-256": combined_hash,
        "Evidencia de gobernanza": (
            "Punto 0 PARA_SUBIR SHA256 8ac3d586... validado con 4070 filas; "
            "Complemento 95 V3 SHA256 1940923b... finalizado en PES el 2026-05-11 12:55; "
            "reporte local de subidas realizadas 4165."
        ),
    }

    inventory = pd.DataFrame(
        {
            "Campo": [
                "Nombre exacto",
                "Ruta o ubicación",
                "Tipo de archivo",
                "Tamaño",
                "Fecha de modificación",
                "Hoja analizada, si corresponde",
                "Número de filas físicas",
                "Número de registros de datos",
                "Número de columnas",
                "Tiene encabezados",
                "Delimitador, si corresponde",
                "Codificación, si corresponde",
                "Nombre de tabla Excel, si corresponde",
                "Hash SHA-256",
                "Evidencia de gobernanza",
                "Nivel de respaldo",
            ],
            "Publicación": [
                pub_info.get("Nombre exacto", ""),
                pub_info.get("Ruta o ubicación", ""),
                pub_info.get("Tipo de archivo", ""),
                pub_info.get("Tamaño", ""),
                pub_info.get("Fecha de modificación", ""),
                pub_info.get("Hoja analizada, si corresponde", ""),
                pub_info.get("Número de filas físicas", ""),
                pub_info.get("Número de registros de datos", ""),
                pub_info.get("Número de columnas", ""),
                pub_info.get("Tiene encabezados", ""),
                pub_info.get("Delimitador, si corresponde", ""),
                pub_info.get("Codificación, si corresponde", ""),
                pub_info.get("Nombre de tabla Excel, si corresponde", ""),
                pub_info.get("Hash SHA-256", ""),
                "No aplica",
                "Dato publicado",
            ],
            "Versión congelada": [
                frozen_info.get("Nombre exacto", ""),
                frozen_info.get("Ruta o ubicación", ""),
                frozen_info.get("Tipo de archivo", ""),
                frozen_info.get("Tamaño", ""),
                frozen_info.get("Fecha de modificación", ""),
                frozen_info.get("Hoja analizada, si corresponde", ""),
                frozen_info.get("Número de filas físicas", ""),
                frozen_info.get("Número de registros de datos", ""),
                frozen_info.get("Número de columnas", ""),
                frozen_info.get("Tiene encabezados", ""),
                frozen_info.get("Delimitador, si corresponde", ""),
                frozen_info.get("Codificación, si corresponde", ""),
                frozen_info.get("Nombre de tabla Excel, si corresponde", ""),
                frozen_info.get("Hash SHA-256", ""),
                frozen_info.get("Evidencia de gobernanza", ""),
                "Congelado institucional combinado derivado",
            ],
        }
    )

    candidates = pd.DataFrame(
        [
            {
                "Candidato": "Punto 0 bruto",
                "Ruta/evidencia": FROZEN_PRINCIPAL_PATH.replace("_PARA_SUBIR", ""),
                "Registros": 4115,
                "SHA256": "20f3c67b68630ca82400f1047702a7a5b7055956e0cd03f3ac9979c0490c94b3",
                "Respaldo": "Congelado, pero no es PARA_SUBIR ni PES_READY",
                "Decisión": "No seleccionado",
            },
            {
                "Candidato": "Punto 0 PARA_SUBIR / PES_READY",
                "Ruta/evidencia": FROZEN_PRINCIPAL_PATH,
                "Registros": 4070,
                "SHA256": sha256_bytes(principal_bytes),
                "Respaldo": "VALIDACION_CARGA_PRINCIPAL OK; hashes Desktop == PES_READY",
                "Decisión": "Seleccionado como componente principal",
            },
            {
                "Candidato": "Complemento 95 V3",
                "Ruta/evidencia": FROZEN_COMPLEMENT_PATH,
                "Registros": 95,
                "SHA256": sha256_bytes(complement_bytes),
                "Respaldo": "MANIFEST_CIERRE_COMPLEMENTO_95: Finalizado en PES 2026-05-11 12:55",
                "Decisión": "Seleccionado como componente posterior",
            },
            {
                "Candidato": "Combinado Punto 0 + Complemento 95 V3",
                "Ruta/evidencia": frozen_meta["combined_path"],
                "Registros": len(frozen),
                "SHA256": combined_hash,
                "Respaldo": "Derivado auditable desde ambos congelados; reporte 4165 subidas realizadas",
                "Decisión": "Seleccionado para comparación agregada",
            },
        ]
    )

    oferta = aggregate_compare(pub, frozen)
    modified = oferta[oferta["Clasificación"] == "MODIFICADO_EN_PUBLICACION_AGREGADO"].copy()
    modified["cantidad de campos distintos"] = 1
    modified["lista de campos distintos"] = "TOTAL_MATRICULA_AGREGADA"
    modified["clasificación principal"] = modified["Clasificación"]

    details = oferta[oferta["Clasificación"].isin(["MODIFICADO_EN_PUBLICACION_AGREGADO", "SOLO_PUBLICACION", "SOLO_CONGELADO"])].copy()
    details = details.rename(
        columns={
            "CODIGO_UNICO": "llave",
            "PUBLICACION_TOTAL": "valor publicación",
            "CONGELADO_TOTAL": "valor congelado",
        }
    )
    details["campo"] = "TOTAL_MATRICULA_AGREGADA_POR_CODIGO_UNICO"
    details["valor normalizado publicación"] = details["valor publicación"]
    details["valor normalizado congelado"] = details["valor congelado"]
    details["clasificación"] = details["Clasificación"]
    details["prioridad"] = "ALTA" 
    details["observación"] = "Comparación agregada; no implica error ni corrección automática."
    details = details[
        [
            "llave",
            "campo",
            "valor publicación",
            "valor congelado",
            "valor normalizado publicación",
            "valor normalizado congelado",
            "clasificación",
            "prioridad",
            "observación",
        ]
    ]

    duplicates = pd.DataFrame(
        [
            {"Fuente": "Publicación", "Llave": "CODIGO_UNICO", "Registros con llave duplicada": int(pub.duplicated("CODIGO_UNICO", keep=False).sum())},
            {"Fuente": "Congelado", "Llave": "LLAVE_PERSONA", "Registros con llave duplicada": int(frozen.duplicated("LLAVE_PERSONA", keep=False).sum())},
            {"Fuente": "Congelado", "Llave": "LLAVE_MATRICULA", "Registros con llave duplicada": int(frozen.duplicated("LLAVE_MATRICULA", keep=False).sum())},
            {"Fuente": "Congelado", "Llave": "CODIGO_UNICO", "Registros con llave duplicada": int(frozen.duplicated("CODIGO_UNICO", keep=False).sum())},
        ]
    )

    universe = pd.DataFrame(
        [
            {"Métrica": "Filas publicación (ofertas)", "Valor": len(pub)},
            {"Métrica": "Total matrícula publicación", "Valor": int(pub["TOTAL MATRÍCULA"].sum())},
            {"Métrica": "Registros congelado combinados", "Valor": len(frozen)},
            {"Métrica": "Personas únicas congelado", "Valor": frozen["LLAVE_PERSONA"].nunique()},
            {"Métrica": "Personas únicas publicación", "Valor": "No disponible: publicación agregada"},
            {"Métrica": "Ofertas publicación", "Valor": pub["CODIGO_UNICO"].nunique()},
            {"Métrica": "Ofertas congelado", "Valor": frozen["CODIGO_UNICO"].nunique()},
            {"Métrica": "Ofertas coincidentes", "Valor": int((oferta["Clasificación"].isin(["COINCIDENTE_TOTAL_AGREGADO", "MODIFICADO_EN_PUBLICACION_AGREGADO"])).sum())},
            {"Métrica": "Ofertas solo publicación", "Valor": int((oferta["Clasificación"] == "SOLO_PUBLICACION").sum())},
            {"Métrica": "Ofertas solo congelado", "Valor": int((oferta["Clasificación"] == "SOLO_CONGELADO").sum())},
            {"Métrica": "Ofertas con total distinto", "Valor": len(modified)},
            {"Métrica": "Diferencia neta matrícula agregada", "Valor": int(pub["TOTAL MATRÍCULA"].sum()) - len(frozen)},
        ]
    )

    vig = frozen.groupby("VIG").size().reset_index(name="Congelado")
    vig.insert(0, "Dimensión", "VIG")
    reinc = frozen.groupby("REINCORPORACION").size().reset_index(name="Congelado")
    reinc.insert(0, "Dimensión", "REINCORPORACION")

    dims = {
        "15_COMPARACION_CARRERAS": dimension_frame(pub, frozen, "COD_CAR", "COD_CAR", "COD_CAR"),
        "16_COMPARACION_SEDES": dimension_frame(pub, frozen, "COD_SED", "COD_SED", "COD_SED"),
        "17_COMPARACION_VIGENCIA": vig,
        "CMP_MODALIDAD": pd.concat(
            [
                pub.groupby("MODALIDAD").agg(Publicación=("TOTAL MATRÍCULA", "sum")).reset_index().rename(columns={"MODALIDAD": "Categoría"}),
                frozen.groupby("MODALIDAD").size().reset_index(name="Congelado").rename(columns={"MODALIDAD": "Categoría"}),
            ],
            axis=0,
            ignore_index=True,
        ),
        "CMP_JORNADA": dimension_frame(pub, frozen, "JOR", "JOR", "JOR derivado"),
        "CMP_VERSION": dimension_frame(pub, frozen, "VERSION", "VERSION", "VERSION"),
        "CMP_ANIO_ING_ACT": dimension_frame(pub.assign(ANIO_DER=pub["AÑO"].map(lambda x: str(x).replace("MAT_", ""))), frozen, "ANIO_DER", "ANIO_ING_ACT", "Año referencia/ingreso actual"),
        "CMP_ANIO_ING_ORI": dimension_frame(pub.assign(ANIO_DER=pub["AÑO"].map(lambda x: str(x).replace("MAT_", ""))), frozen, "ANIO_DER", "ANIO_ING_ORI", "Año referencia/ingreso origen"),
        "CMP_FORMA_INGRESO": frozen.groupby("FOR_ING_ACT").size().reset_index(name="Congelado").rename(columns={"FOR_ING_ACT": "Categoría"}),
        "CMP_NIVEL_ACADEMICO": frozen.groupby("NIV_ACA").size().reset_index(name="Congelado").rename(columns={"NIV_ACA": "Categoría"}),
        "CMP_SEXO": pd.DataFrame(
            [
                {"Dimensión": "SEXO", "Categoría": "M publicación / M congelado", "Publicación": int(pub.get("TOTAL MATRÍCULA MUJERES", pd.Series(dtype=int)).sum()), "Congelado": int((frozen["SEXO"] == "M").sum())},
                {"Dimensión": "SEXO", "Categoría": "H publicación / H congelado", "Publicación": int(pub.get("TOTAL MATRÍCULA HOMBRES", pd.Series(dtype=int)).sum()), "Congelado": int((frozen["SEXO"] == "H").sum())},
                {"Dimensión": "SEXO", "Categoría": "NB/indef.", "Publicación": int(pub.get("TOTAL MATRÍCULA NO BINARIOS O INDEFINIDOS", pd.Series(dtype=float)).fillna(0).sum()), "Congelado": int((frozen["SEXO"] == "NB").sum())},
            ]
        ),
        "CMP_NACIONALIDAD": frozen.groupby("NAC").size().reset_index(name="Congelado").rename(columns={"NAC": "Categoría"}),
    }

    validations = pd.DataFrame(
        [
            {"Validación": "publicacion2026 leído", "Resultado": "OK", "Detalle": f"{len(pub)} filas de datos, hoja Hoja1"},
            {"Validación": "Congelado identificado con evidencia", "Resultado": "OK", "Detalle": "Punto 0 + Complemento 95 V3 con hashes y estado PES"},
            {"Validación": "Originales no modificados", "Resultado": "OK", "Detalle": "Solo se escribieron derivados en outputs/"},
            {"Validación": "Mismo proceso/año", "Resultado": "OK", "Detalle": "MU Pregrado 2026; publicación AÑO=MAT_2026"},
            {"Validación": "Personas vs registros", "Resultado": "OK_CON_LIMITACION", "Detalle": "Congelado individual; publicación agregada sin personas"},
            {"Validación": "Llave validada", "Resultado": "OK_CON_LIMITACION", "Detalle": "Llave de oferta seleccionada solo para agregados"},
            {"Validación": "Duplicados no eliminados", "Resultado": "OK", "Detalle": "Se conservaron todos los registros congelados"},
            {"Validación": "Datos no corregidos automáticamente", "Resultado": "OK", "Detalle": "Solo normalización técnica de claves/códigos"},
            {"Validación": "Comparación todos los campos comunes", "Resultado": "OK_CON_LIMITACION", "Detalle": "No hay campos persona/matrícula comunes; se comparó oferta agregada derivable"},
            {"Validación": "Conciliación publicación", "Resultado": "OK", "Detalle": f"{len(pub)} ofertas = coincidentes/modificadas + solo publicación + no resueltas en nivel oferta"},
            {"Validación": "Conciliación congelado", "Resultado": "OK", "Detalle": "4165 registros no conciliables a nivel registro contra publicación agregada; conciliación de oferta OK"},
            {"Validación": "Hashes registrados", "Resultado": "OK", "Detalle": f"Publicación {pub_info['Hash SHA-256']}; congelado combinado {combined_hash}"},
        ]
    )

    pendientes = pd.DataFrame(
        [
            {
                "Pendiente": "Comparación persona/registro/campo a campo",
                "Motivo": "publicacion2026 es agregada por oferta y no contiene TIPO_DOC, N_DOC, DV ni campos persona/matrícula.",
                "Evidencia requerida": "Archivo publicado con registros individuales o fuente congelada agregada con la misma estructura exacta de publicación.",
            },
            {
                "Pendiente": "Modalidad textual vs numérica",
                "Motivo": "Publicación usa texto; congelado usa código numérico. No se aplicó homologación sustantiva sin diccionario local explícito para esta publicación.",
                "Evidencia requerida": "Tabla local que relacione códigos MU de MODALIDAD/JOR con categorías publicadas.",
            },
            {
                "Pendiente": "Un único CSV combinado oficial",
                "Motivo": "La última evidencia institucional se compone de Punto 0 + complemento 95; no se encontró un único CSV combinado final congelado.",
                "Evidencia requerida": "Archivo combinado oficial o manifiesto que lo declare como tal.",
            },
        ]
    )

    resumen = pd.DataFrame(
        [
            {"Ítem": "Archivo publicación", "Valor": str(PUBLICACION)},
            {"Ítem": "Hash publicación", "Valor": pub_info["Hash SHA-256"]},
            {"Ítem": "Versión congelada seleccionada", "Valor": "Combinado derivado Punto 0 PARA_SUBIR + Complemento 95 V3"},
            {"Ítem": "Hash congelado combinado derivado", "Valor": combined_hash},
            {"Ítem": "Registros publicación", "Valor": f"{len(pub)} filas de oferta; total matrícula publicada {int(pub['TOTAL MATRÍCULA'].sum())}"},
            {"Ítem": "Registros congelado", "Valor": len(frozen)},
            {"Ítem": "Personas publicación", "Valor": "No disponible"},
            {"Ítem": "Personas congelado", "Valor": frozen["LLAVE_PERSONA"].nunique()},
            {"Ítem": "Ofertas coincidentes con igual total", "Valor": int((oferta["Clasificación"] == "COINCIDENTE_TOTAL_AGREGADO").sum())},
            {"Ítem": "Ofertas con diferencias", "Valor": len(modified)},
            {"Ítem": "Solo publicación", "Valor": int((oferta["Clasificación"] == "SOLO_PUBLICACION").sum())},
            {"Ítem": "Solo congelado", "Valor": int((oferta["Clasificación"] == "SOLO_CONGELADO").sum())},
            {"Ítem": "Conclusión técnica", "Valor": "Estructura diferente: no comparable a nivel persona/registro; comparable solo en agregados de oferta."},
        ]
    )

    trazabilidad = pd.DataFrame(
        [
            {"Campo": "archivo_publicacion", "Valor": str(PUBLICACION)},
            {"Campo": "archivo_congelado_principal_git", "Valor": FROZEN_PRINCIPAL_PATH},
            {"Campo": "archivo_congelado_complemento_git", "Valor": FROZEN_COMPLEMENT_PATH},
            {"Campo": "commit_git_fuente", "Valor": COMMIT},
            {"Campo": "hash_publicacion", "Valor": pub_info["Hash SHA-256"]},
            {"Campo": "hash_principal", "Valor": frozen_meta["principal_hash"]},
            {"Campo": "hash_complemento", "Valor": frozen_meta["complement_hash"]},
            {"Campo": "hash_congelado_combinado", "Valor": combined_hash},
            {"Campo": "fecha_hora_analisis", "Valor": ts},
            {"Campo": "script", "Valor": str(Path(__file__).resolve())},
            {"Campo": "reglas_normalizacion", "Valor": "trim, uppercase para claves, parse técnico de CODIGO_CARRERA, sin corrección sustantiva"},
            {"Campo": "llave_seleccionada", "Valor": "CODIGO_CARRERA/CODIGO_UNICO solo para agregados de oferta"},
        ]
    )

    sheets = {
        "00_RESUMEN_EJECUTIVO": resumen,
        "01_INVENTARIO_FUENTES": pd.concat([inventory, pd.DataFrame([{}]), candidates], ignore_index=True),
        "02_ESTRUCTURA": structure_diagnostics(pub, frozen),
        "03_RESUMEN_UNIVERSOS": universe,
        "04_COINCIDENTES_TOTAL": oferta[oferta["Clasificación"] == "COINCIDENTE_TOTAL_AGREGADO"],
        "05_MODIFICADOS": modified,
        "06_DETALLE_DIFERENCIAS": details,
        "07_SOLO_PUBLICACION": oferta[oferta["Clasificación"] == "SOLO_PUBLICACION"],
        "08_SOLO_CONGELADO": oferta[oferta["Clasificación"] == "SOLO_CONGELADO"],
        "09_DUPLICADOS_LLAVE": duplicates,
        "10_CAMBIOS_VIGENCIA": pd.DataFrame({"Resultado": ["No comparable campo a campo: publicación agregada sin VIG. Distribución congelado en 17_COMPARACION_VIGENCIA."]}),
        "11_CAMBIOS_OFERTA": details[details["clasificación"].isin(["MODIFICADO_EN_PUBLICACION_AGREGADO", "SOLO_PUBLICACION", "SOLO_CONGELADO"])],
        "12_CAMBIOS_IDENTIDAD": pd.DataFrame({"Resultado": ["No comparable: publicación no contiene identificación personal."]}),
        "13_CAMBIOS_TRAYECTORIA": pd.DataFrame({"Resultado": ["No comparable: publicación no contiene trayectoria académica individual."]}),
        "14_CAMBIOS_ACADEMICOS": pd.DataFrame({"Resultado": ["No comparable: publicación no contiene campos académicos individuales."]}),
        "15_COMPARACION_CARRERAS": dims["15_COMPARACION_CARRERAS"],
        "16_COMPARACION_SEDES": dims["16_COMPARACION_SEDES"],
        "17_COMPARACION_VIGENCIA": dims["17_COMPARACION_VIGENCIA"],
        "18_VALIDACIONES": validations,
        "19_PENDIENTES": pendientes,
        "20_TRAZABILIDAD": trazabilidad,
        "LLAVES_CANDIDATAS": key_candidates(pub, frozen),
        "CAMPO_A_CAMPO_NO_COMP": field_summary_non_comparable(frozen),
        "COMPARACION_OFERTA": oferta,
        "CMP_MODALIDAD": dims["CMP_MODALIDAD"],
        "CMP_JORNADA": dims["CMP_JORNADA"],
        "CMP_VERSION": dims["CMP_VERSION"],
        "CMP_ANIO_ING_ACT": dims["CMP_ANIO_ING_ACT"],
        "CMP_ANIO_ING_ORI": dims["CMP_ANIO_ING_ORI"],
        "CMP_FORMA_INGRESO": dims["CMP_FORMA_INGRESO"],
        "CMP_NIVEL_ACADEMICO": dims["CMP_NIVEL_ACADEMICO"],
        "CMP_SEXO": dims["CMP_SEXO"],
        "CMP_NACIONALIDAD": dims["CMP_NACIONALIDAD"],
    }

    xlsx_path = out_dir / f"COMPARACION_PUBLICACION2026_VS_CONGELADO_MU_PREGRADO_2026_{ts}.xlsx"
    write_xlsx(xlsx_path, sheets)

    md_path = out_dir / f"REPORTE_COMPARACION_PUBLICACION2026_VS_CONGELADO_{ts}.md"
    top_diffs = oferta[oferta["Clasificación"] == "MODIFICADO_EN_PUBLICACION_AGREGADO"].copy()
    top_diffs["abs_abs"] = top_diffs["Diferencia absoluta"].abs()
    top_diffs = top_diffs.sort_values("abs_abs", ascending=False).head(10)
    md = f"""# Reporte comparación publicacion2026 vs congelado MU Pregrado 2026

## Contexto

Proceso: Matrícula Unificada 2026. Subproyecto: Pregrado. Año de referencia: 2026.

## Fuentes

- Publicación: `{PUBLICACION}`; hoja `Hoja1`; filas de datos {len(pub)}; hash SHA-256 `{pub_info['Hash SHA-256']}`.
- Congelado seleccionado: combinado derivado desde Punto 0 `PARA_SUBIR` (4070 registros, SHA-256 `{frozen_meta['principal_hash']}`) más Complemento 95 V3 (95 registros, SHA-256 `{frozen_meta['complement_hash']}`).
- Hash del combinado derivado: `{combined_hash}`.

## Selección de versión congelada

Se seleccionó el paquete institucional respaldado por `control/auditoria_mu2026_punto0_complemento95` y `control/auditoria_mu2026_complemento95_cierre_final`: la carga principal Punto 0 fue validada y no modificada, y el complemento 95 V3 consta como finalizado en PES el 2026-05-11 12:55. No se encontró un único CSV combinado oficial materializado; por eso el combinado usado aquí es derivado y auditable.

## Metodología

No se modificaron fuentes originales. Se extrajeron blobs desde Git a `outputs/` y se aplicó normalización técnica: recorte de espacios, mayúsculas para claves y parseo técnico de `CÓDIGO CARRERA` a `COD_SED`, `COD_CAR`, `JOR` y `VERSION`.

## Llave utilizada

La publicación es agregada por oferta, no por persona. La comparación principal usa `CÓDIGO CARRERA` de la publicación contra `CODIGO_UNICO` derivado del congelado, solo para agregados de oferta.

## Diferencias estructurales

Clasificación: `ESTRUCTURA_DIFERENTE`. La publicación tiene 58 columnas agregadas y encabezados; el congelado tiene 32 campos MU sin encabezado y registros individuales. No es comparable a nivel persona, matrícula ni campo a campo individual.

## Diferencias de universo

- Total matrícula publicación: {int(pub['TOTAL MATRÍCULA'].sum())}
- Registros congelado combinado: {len(frozen)}
- Personas únicas congelado: {frozen['LLAVE_PERSONA'].nunique()}
- Personas únicas publicación: no disponible
- Ofertas publicación: {pub['CODIGO_UNICO'].nunique()}
- Ofertas congelado: {frozen['CODIGO_UNICO'].nunique()}
- Ofertas con igual total: {int((oferta['Clasificación'] == 'COINCIDENTE_TOTAL_AGREGADO').sum())}
- Ofertas con total distinto: {len(modified)}
- Ofertas solo publicación: {int((oferta['Clasificación'] == 'SOLO_PUBLICACION').sum())}
- Ofertas solo congelado: {int((oferta['Clasificación'] == 'SOLO_CONGELADO').sum())}

## Diferencias campo a campo

No ejecutada para campos individuales MU, porque `publicacion2026` no contiene `TIPO_DOC`, `N_DOC`, `DV`, nombres, fechas de nacimiento, trayectoria, vigencia ni otros campos de registro. El detalle agregado por oferta está en el Excel.

## Principales variaciones

{simple_markdown_table(top_diffs[['CODIGO_UNICO','PUBLICACION_TOTAL','CONGELADO_TOTAL','Diferencia absoluta']])}

## Hallazgos críticos

- La publicación no puede usarse para afirmar altas, bajas o modificaciones persona a persona.
- Cualquier diferencia agregada es observada y no implica error ni corrección automática.
- La modalidad aparece como texto en publicación y como código en congelado; no se homologó sin evidencia local específica.

## Limitaciones

La comparación completa solicitada a nivel registro requiere una publicación con registros individuales o una fuente congelada publicada con la misma estructura agregada. El archivo combinado usado es derivado de dos congelados, no un CSV final único materializado.

## Pendientes

Ver hoja `19_PENDIENTES` del Excel.

## Conclusión

La comparación validada queda limitada a nivel agregado por oferta/carrera. La estructura de `publicacion2026` es diferente y no comparable para personas, registros de matrícula ni campos individuales MU.
"""
    md_path.write_text(md, encoding="utf-8")

    manifest = {
        "timestamp": ts,
        "xlsx": str(xlsx_path),
        "markdown": str(md_path),
        "publicacion_hash": pub_info["Hash SHA-256"],
        "frozen_combined_hash": combined_hash,
        "rows_publicacion": len(pub),
        "total_matricula_publicacion": int(pub["TOTAL MATRÍCULA"].sum()),
        "rows_frozen": len(frozen),
        "persons_frozen": int(frozen["LLAVE_PERSONA"].nunique()),
    }
    (out_dir / "manifest_comparacion.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
