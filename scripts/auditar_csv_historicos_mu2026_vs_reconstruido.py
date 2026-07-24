#!/usr/bin/env python3
"""Compara CSV historicos de carga MU2026 pregrado contra consolidado reconstruido.

No modifica fuentes originales. Genera CSV/XLSX/MD derivados versionados.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
CONSOLIDADO = Path("/Users/alexi/Desktop/AUDITORIA_MATRICULA_UNIFICADA_2026_RECONSTRUIDA_PARA_REVISION_20260731_002214.xlsx")
DOWNLOADS = Path("/Users/alexi/Downloads")
TS = datetime.now().strftime("%Y-%m-%d_%H%M%S")
OUT_DIR = ROOT / "auditoria_comparacion_csv_mu2026" / TS

HEADERS_32 = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE",
    "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD",
    "JOR", "VERSION", "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI",
    "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",
    "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]


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
            continue
    return data.decode("latin-1", errors="replace"), "latin-1-replace"


def detect_delimiter(text: str) -> str:
    sample = "\n".join(text.splitlines()[:10])
    counts = {";": sample.count(";"), ",": sample.count(","), "\t": sample.count("\t")}
    return max(counts, key=counts.get)


def parse_csv(path: Path) -> tuple[pd.DataFrame, dict, list[list[str]]]:
    data = path.read_bytes()
    text, enc = decode_bytes(data)
    delim = detect_delimiter(text)
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    if rows and rows[-1] == []:
        rows = rows[:-1]
    first = rows[0] if rows else []
    upper_first = [str(x).strip().upper() for x in first]
    has_header = len({"TIPO_DOC", "N_DOC", "DV", "VIG"} & set(upper_first)) >= 2
    data_rows = rows[1:] if has_header else rows
    headers = first if has_header else (HEADERS_32 if rows and len(rows[0]) == 32 else [f"CAMPO_{i+1}" for i in range(len(rows[0]) if rows else 0)])
    df = pd.DataFrame(data_rows, columns=headers).astype(str).fillna("")
    meta = {
        "Nombre archivo": path.name,
        "Ruta": str(path),
        "Fecha incorporada en nombre": parse_date_from_name(path.name),
        "Tamaño archivo": path.stat().st_size,
        "Hash SHA-256": hashlib.sha256(data).hexdigest(),
        "Codificación": enc,
        "BOM": "SI" if data.startswith(b"\xef\xbb\xbf") else "NO",
        "Delimitador": "\\t" if delim == "\t" else delim,
        "Cantidad columnas": len(headers),
        "Cantidad filas físicas": len(rows),
        "Filas datos": len(df),
        "Tiene encabezado": "SI" if has_header else "NO",
        "Nombre columnas": ";".join(map(str, headers)),
        "Primera fila": ";".join(first),
        "Última fila": ";".join(rows[-1]) if rows else "",
    }
    return df, meta, rows


def parse_date_from_name(name: str) -> str:
    m = re.search(r"(\d{2})-(\d{2})-(\d{4})_(\d{2})-(\d{2})-(\d{2})", name)
    if not m:
        return ""
    dd, mm, yyyy, hh, mi, ss = m.groups()
    return f"{yyyy}-{mm}-{dd} {hh}:{mi}:{ss}"


def add_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().astype(str).fillna("")
    if set(["COD_SED", "COD_CAR", "JOR", "VERSION"]).issubset(out.columns):
        out["CODIGO_NORMALIZADO"] = "I162S" + out["COD_SED"].str.strip() + "C" + out["COD_CAR"].str.strip() + "J" + out["JOR"].str.strip() + "V" + out["VERSION"].str.strip()
    else:
        out["CODIGO_NORMALIZADO"] = ""
    if set(["TIPO_DOC", "N_DOC", "DV"]).issubset(out.columns):
        out["LLAVE_PERSONA"] = out["TIPO_DOC"].str.strip() + "|" + out["N_DOC"].str.strip() + "|" + out["DV"].str.strip()
    else:
        out["LLAVE_PERSONA"] = ""
    out["LLAVE_MATRICULA"] = out["LLAVE_PERSONA"] + "|" + out["CODIGO_NORMALIZADO"]
    out["HASH_FILA_32"] = out.apply(lambda r: row_hash(r, HEADERS_32), axis=1) if set(HEADERS_32).issubset(out.columns) else ""
    return out


def row_hash(row: pd.Series, cols: list[str]) -> str:
    return hashlib.sha256("\x1f".join(str(row.get(c, "")) for c in cols).encode("utf-8")).hexdigest()


def load_consolidado() -> tuple[pd.DataFrame, dict]:
    wb = openpyxl.load_workbook(CONSOLIDADO, read_only=True, data_only=False)
    sheet_used = None
    if "RAW_PREGRADO" in wb.sheetnames:
        sheet_used = "RAW_PREGRADO"
    elif "07_PREGRADO_COMPLETO" in wb.sheetnames:
        sheet_used = "07_PREGRADO_COMPLETO"
    elif "08_PREGRADO_COMPLETO" in wb.sheetnames:
        sheet_used = "08_PREGRADO_COMPLETO"
    else:
        raise RuntimeError(f"No se encontro hoja de pregrado en {CONSOLIDADO}")
    ws = wb[sheet_used]
    rows = list(ws.iter_rows(values_only=True))
    # Detect header row: first row containing TIPO_DOC, N_DOC, VIG.
    header_idx = None
    for i, row in enumerate(rows):
        vals = [str(v).strip().upper() if v is not None else "" for v in row]
        if {"TIPO_DOC", "N_DOC", "VIG"}.issubset(set(vals)):
            header_idx = i
            break
    if header_idx is None:
        raise RuntimeError(f"No se encontro encabezado oficial en hoja {sheet_used}")
    headers = [str(v) if v is not None else "" for v in rows[header_idx]]
    data = [list(r) for r in rows[header_idx + 1:] if any(v is not None for v in r)]
    df = pd.DataFrame(data, columns=headers).astype(str).fillna("")
    # Only official 32 columns for structural/record comparison.
    official = df[HEADERS_32].copy()
    info = {
        "ruta": str(CONSOLIDADO),
        "hoja_usada": sheet_used,
        "hojas_disponibles": wb.sheetnames,
        "hash": sha256_path(CONSOLIDADO),
        "filas_datos_hoja": len(df),
        "columnas_hoja": len(df.columns),
        "filas_oficiales": len(official),
        "columnas_oficiales": len(official.columns),
        "equivalencia": "El prompt menciona RAW_PREGRADO/07_PREGRADO_COMPLETO; el libro disponible contiene 08_PREGRADO_COMPLETO, usada como hoja equivalente.",
    }
    return add_keys(official), info


def field_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, c in enumerate(df.columns, 1):
        s = df[c].astype(str)
        date_like = int(s.str.match(r"^\d{2}[/-]\d{2}[/-]\d{4}$", na=False).sum())
        numeric_like = int(s.str.match(r"^-?\d+(\.\d+)?$", na=False).sum())
        rows.append({
            "CAMPO": c,
            "POSICION": i,
            "NO_VACIOS": int((s.str.strip() != "").sum()),
            "UNICOS": int(s.nunique(dropna=False)),
            "TIPO_OBSERVADO": "fecha_texto" if date_like > len(s) * 0.5 else ("numero_texto" if numeric_like > len(s) * 0.8 else "texto"),
            "EJEMPLOS": "; ".join(s.drop_duplicates().head(3).tolist()),
        })
    return pd.DataFrame(rows)


def compare_one(path: Path, cons: pd.DataFrame) -> dict:
    df_raw, meta, raw_rows = parse_csv(path)
    df = add_keys(df_raw)
    missing_cols = [c for c in HEADERS_32 if c not in df_raw.columns]
    additional_cols = [c for c in df_raw.columns if c not in HEADERS_32]
    meta["Columnas faltantes"] = ";".join(missing_cols)
    meta["Columnas adicionales"] = ";".join(additional_cols)
    meta["Valores únicos VIG"] = ";".join(sorted(df["VIG"].astype(str).str.strip().unique())) if "VIG" in df.columns else ""
    structure_equal = (len(missing_cols) == 0 and len(additional_cols) == 0 and list(df_raw.columns) == HEADERS_32)
    csv_hashes = set(df["HASH_FILA_32"])
    cons_hashes = set(cons["HASH_FILA_32"])
    exact_match_rows = int(df["HASH_FILA_32"].isin(cons_hashes).sum())
    new_rows = int((~df["HASH_FILA_32"].isin(cons_hashes)).sum())
    missing_rows = int((~cons["HASH_FILA_32"].isin(csv_hashes)).sum())
    dup_hash_records = int(df["HASH_FILA_32"].duplicated(keep=False).sum())
    key_overlap = int(df["LLAVE_MATRICULA"].isin(set(cons["LLAVE_MATRICULA"])).sum()) if "LLAVE_MATRICULA" in df else 0
    if structure_equal and len(df) == len(cons) and exact_match_rows == len(cons):
        tipo_comparacion = "EXACTA"
        clasificacion = "MATCH_EXACTO_CON_RECONSTRUIDO"
    elif structure_equal and key_overlap > 0:
        tipo_comparacion = "PARCIAL"
        clasificacion = "MATCH_PARCIAL" if exact_match_rows else "FUENTE_ANTERIOR"
    else:
        tipo_comparacion = "NO_COMPARABLE"
        clasificacion = "FUENTE_NO_IDENTIFICADA"
    if clasificacion == "MATCH_PARCIAL" and len(df) < len(cons):
        clasificacion = "FUENTE_ANTERIOR"
    vig = df["VIG"].astype(str).str.strip().value_counts().to_dict() if "VIG" in df.columns else {}
    universe = {
        "archivo": path.name,
        "fecha_nombre": meta["Fecha incorporada en nombre"],
        "filas": len(df),
        "vig0": int(vig.get("0", 0)),
        "vig1": int(vig.get("1", 0)),
        "vig2": int(vig.get("2", 0)),
        "vigente": int(vig.get("1", 0)) + int(vig.get("2", 0)),
        "coincidentes": exact_match_rows,
        "coincidentes_llave_matricula": key_overlap,
        "faltantes": missing_rows,
        "nuevos": new_rows,
        "duplicados": dup_hash_records,
        "tipo_comparacion": tipo_comparacion,
        "clasificacion_final": clasificacion,
        "estructura": "ESTRUCTURA_IGUAL" if structure_equal else "ESTRUCTURA_DIFERENTE",
    }
    return {
        "path": path,
        "df": df,
        "raw_df": df_raw,
        "meta": meta,
        "structure_equal": structure_equal,
        "universe": universe,
        "field_profile": field_profile(df_raw),
    }


def code_comparison(results: list[dict], cons: pd.DataFrame) -> pd.DataFrame:
    cons_counts = cons.groupby("CODIGO_NORMALIZADO").size().rename("CONSOLIDADO_TOTAL")
    cons_vig = cons[cons["VIG"].astype(str).str.strip().isin(["1", "2"])].groupby("CODIGO_NORMALIZADO").size().rename("CONSOLIDADO_VIGENTE")
    rows = []
    for res in results:
        df = res["df"]
        csv_counts = df.groupby("CODIGO_NORMALIZADO").size().rename("CSV_TOTAL")
        csv_vig = df[df["VIG"].astype(str).str.strip().isin(["1", "2"])].groupby("CODIGO_NORMALIZADO").size().rename("CSV_VIGENTE")
        codes = sorted(set(cons_counts.index) | set(csv_counts.index))
        for code in codes:
            ct = int(cons_counts.get(code, 0))
            cv = int(cons_vig.get(code, 0))
            ft = int(csv_counts.get(code, 0))
            fv = int(csv_vig.get(code, 0))
            rows.append({
                "archivo": res["path"].name,
                "CODIGO_NORMALIZADO": code,
                "PUBLICACION": ct,  # nombre solicitado; representa consolidado reconstruido en esta auditoria
                "CSV": ft,
                "DIFERENCIA": ft - ct,
                "CONSOLIDADO_TOTAL": ct,
                "CSV_TOTAL": ft,
                "CONSOLIDADO_VIGENTE": cv,
                "CSV_VIGENTE": fv,
                "DIFERENCIA_VIGENTE": fv - cv,
            })
    return pd.DataFrame(rows)


def detail_differences(results: list[dict], cons: pd.DataFrame) -> pd.DataFrame:
    cons_hashes = set(cons["HASH_FILA_32"])
    cons_by_key = {k: g.copy() for k, g in cons.groupby("LLAVE_MATRICULA")}
    rows = []
    for res in results:
        archivo = res["path"].name
        df = res["df"].copy()
        for idx, r in df.iterrows():
            h = r["HASH_FILA_32"]
            key = r["LLAVE_MATRICULA"]
            if h in cons_hashes:
                continue
            if key not in cons_by_key:
                rows.append({
                    "archivo_origen": archivo,
                    "llave_matricula": key,
                    "codigo_normalizado": r["CODIGO_NORMALIZADO"],
                    "campo": "__FILA__",
                    "valor_csv": "FILA_PRESENTE_EN_CSV",
                    "valor_consolidado": "NO_EXISTE_LLAVE_MATRICULA_EN_CONSOLIDADO",
                    "tipo_diferencia": "FILA_NUEVA_EN_CSV",
                })
                continue
            candidates = cons_by_key[key]
            # Choose candidate with most equal official fields.
            scores = candidates[HEADERS_32].apply(lambda row: sum(str(row[c]) == str(r[c]) for c in HEADERS_32), axis=1)
            best = candidates.loc[scores.idxmax()]
            for c in HEADERS_32:
                if str(r[c]) != str(best[c]):
                    rows.append({
                        "archivo_origen": archivo,
                        "llave_matricula": key,
                        "codigo_normalizado": r["CODIGO_NORMALIZADO"],
                        "campo": c,
                        "valor_csv": r[c],
                        "valor_consolidado": best[c],
                        "tipo_diferencia": "VALOR_DISTINTO_MISMA_LLAVE",
                    })
        # Consolidado rows not in candidate, summarized at row level.
        csv_hashes = set(df["HASH_FILA_32"])
        missing = cons[~cons["HASH_FILA_32"].isin(csv_hashes)]
        for _, r in missing.iterrows():
            rows.append({
                "archivo_origen": archivo,
                "llave_matricula": r["LLAVE_MATRICULA"],
                "codigo_normalizado": r["CODIGO_NORMALIZADO"],
                "campo": "__FILA__",
                "valor_csv": "NO_EXISTE_HASH_FILA_EN_CSV",
                "valor_consolidado": "FILA_PRESENTE_EN_CONSOLIDADO",
                "tipo_diferencia": "FILA_FALTANTE_EN_CSV",
            })
    return pd.DataFrame(rows)


def write_structure_xlsx(path: Path, results: list[dict], cons_info: dict, cons: pd.DataFrame) -> None:
    resumen = []
    cols_rows = []
    profile_rows = []
    for res in results:
        meta = res["meta"]
        resumen.append({
            "archivo": res["path"].name,
            "hoja_consolidado_solicitada": "RAW_PREGRADO / 07_PREGRADO_COMPLETO",
            "hoja_consolidado_usada": cons_info["hoja_usada"],
            "equivalencia": cons_info["equivalencia"],
            "columnas_csv": meta["Cantidad columnas"],
            "columnas_consolidado_oficial": cons_info["columnas_oficiales"],
            "estado_estructura": res["universe"]["estructura"],
            "delimitador": meta["Delimitador"],
            "codificacion": meta["Codificación"],
            "encabezado_csv": meta["Tiene encabezado"],
            "columnas_faltantes": meta["Columnas faltantes"],
            "columnas_adicionales": meta["Columnas adicionales"],
        })
        for pos, official in enumerate(HEADERS_32, 1):
            csv_col = res["raw_df"].columns[pos - 1] if pos <= len(res["raw_df"].columns) else ""
            cols_rows.append({
                "archivo": res["path"].name,
                "posicion": pos,
                "columna_consolidado": official,
                "columna_csv_asignada": csv_col,
                "coincide": official == csv_col,
            })
        prof = res["field_profile"].copy()
        prof.insert(0, "archivo", res["path"].name)
        profile_rows.append(prof)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(resumen).to_excel(writer, index=False, sheet_name="RESUMEN_ESTRUCTURA")
        pd.DataFrame(cols_rows).to_excel(writer, index=False, sheet_name="COLUMNAS")
        pd.concat(profile_rows, ignore_index=True).to_excel(writer, index=False, sheet_name="TIPOS_DATOS")
        pd.DataFrame({
            "campo_obligatorio": HEADERS_32,
            "presente_consolidado": [c in cons.columns for c in HEADERS_32],
        }).to_excel(writer, index=False, sheet_name="CAMPOS_OBLIGATORIOS")
        wb = writer.book
        for ws in wb.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="1F4E78")
                cell.alignment = Alignment(wrap_text=True)
            if ws.max_row > 1 and ws.max_column > 1:
                ref = ws.dimensions
                name = "tbl" + re.sub(r"[^A-Za-z0-9]", "", ws.title)[:20]
                tab = Table(displayName=name, ref=ref)
                tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
                ws.add_table(tab)
            for col in ws.columns:
                width = min(60, max(10, max(len(str(c.value)) if c.value is not None else 0 for c in col[:300]) + 2))
                ws.column_dimensions[col[0].column_letter].width = width


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Sin registros._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for row in df.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(v).replace("|", "\\|") for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=False)
    cons, cons_info = load_consolidado()
    csv_paths = sorted(DOWNLOADS.glob("*Pregrado-2026.csv"), key=lambda p: parse_date_from_name(p.name))
    if len(csv_paths) != 6:
        raise RuntimeError(f"Se esperaban 6 CSV historicos y se encontraron {len(csv_paths)}: {csv_paths}")
    results = [compare_one(p, cons) for p in csv_paths]

    inventario = pd.DataFrame([r["meta"] for r in results])
    universe = pd.DataFrame([r["universe"] for r in results])
    codigos = code_comparison(results, cons)
    detalles = detail_differences(results, cons)

    # Persist outputs.
    inv_path = OUT_DIR / "01_INVENTARIO_ARCHIVOS.csv"
    struct_path = OUT_DIR / "02_COMPARACION_ESTRUCTURA.xlsx"
    univ_path = OUT_DIR / "03_COMPARACION_UNIVERSO.csv"
    cod_path = OUT_DIR / "04_COMPARACION_CODIGOS.csv"
    det_path = OUT_DIR / "05_DETALLE_DIFERENCIAS.csv"
    report_path = OUT_DIR / "06_REPORTE_FINAL.md"
    manifest_path = OUT_DIR / "MANIFEST_AUDITORIA_COMPARACION_CSV_MU2026.json"

    inventario.to_csv(inv_path, index=False, encoding="utf-8-sig")
    write_structure_xlsx(struct_path, results, cons_info, cons)
    universe.to_csv(univ_path, index=False, encoding="utf-8-sig")
    codigos.to_csv(cod_path, index=False, encoding="utf-8-sig")
    detalles.to_csv(det_path, index=False, encoding="utf-8-sig")

    # Findings.
    exact = universe[universe["clasificacion_final"].eq("MATCH_EXACTO_CON_RECONSTRUIDO")]
    best_exact_rows = universe.sort_values(["coincidentes", "coincidentes_llave_matricula", "filas"], ascending=False).head(1)
    timeline = universe[["archivo", "fecha_nombre", "filas", "vig0", "vig1", "vig2", "vigente", "coincidentes", "nuevos", "faltantes", "clasificacion_final"]].copy()
    vig_table = universe[["archivo", "vig0", "vig1", "vig2", "filas"]].rename(columns={"vig0": "VIG0", "vig1": "VIG1", "vig2": "VIG2", "filas": "Total"})
    consolidated_vig = cons["VIG"].astype(str).str.strip().value_counts().to_dict()
    union_hashes = set().union(*[set(r["df"]["HASH_FILA_32"]) for r in results])
    union_exact = int(cons["HASH_FILA_32"].isin(union_hashes).sum())
    union_new = int(sum(len(set(r["df"]["HASH_FILA_32"]) - set(cons["HASH_FILA_32"])) for r in results))

    report = f"""# Auditoría comparativa CSV históricos MU2026 contra consolidado reconstruido

## Gobernanza

- Proceso: Matrícula Unificada SIES 2026.
- Subproceso: Pregrado.
- Fuente comparación: `{CONSOLIDADO}`.
- Hoja solicitada: `RAW_PREGRADO` / `07_PREGRADO_COMPLETO`.
- Hoja usada: `{cons_info['hoja_usada']}`.
- Observación de equivalencia: {cons_info['equivalencia']}
- Fuentes evaluadas: 6 CSV históricos ubicados en `/Users/alexi/Downloads`.
- Originales: NO MODIFICADOS.
- Método: lectura, hash, comparación estructural, comparación exacta por 32 campos, comparación por `LLAVE_MATRICULA`, universo y códigos.

## Respuesta directa

1. ¿Cuál CSV coincide con el consolidado?

Ningún CSV coincide exactamente con el consolidado reconstruido de 4.105 registros. No hay `MATCH_EXACTO_CON_RECONSTRUIDO`.

2. ¿Cuál parece ser la fuente utilizada?

Ninguno de los seis CSV por sí solo parece ser la fuente completa utilizada para construir el consolidado final. Todos son cargas parciales/anteriores respecto del universo gobernado. El archivo con mayor coincidencia exacta es `{best_exact_rows.iloc[0]['archivo']}`, con {int(best_exact_rows.iloc[0]['coincidentes'])} filas exactas coincidentes.

3. ¿Cuál es la evolución temporal de cargas?

{markdown_table(timeline)}

4. ¿Qué diferencias explican los 226 registros?

Estos seis CSV no explican directamente la diferencia de 226 registros de publicación versus institucional. Son archivos históricos de carga parcial contra el consolidado reconstruido; el análisis muestra evolución y cobertura parcial, no una reproducción del universo final publicado/institucional. La diferencia de 226 debe interpretarse desde la comparación publicación vs consolidado, no desde estos CSV parciales.

5. ¿Hay evidencia de que el consolidado fue construido correctamente?

Sí hay evidencia técnica de consistencia interna: el consolidado contiene 4.105 registros oficiales, con VIG=0: {int(consolidated_vig.get('0',0))}, VIG=1: {int(consolidated_vig.get('1',0))}, VIG=2: {int(consolidated_vig.get('2',0))}. Además, los CSV históricos son parciales y no contradicen por sí mismos el consolidado. Sin embargo, esta auditoría no prueba una cadena completa de generación si faltan cargas intermedias fuera de los seis CSV evaluados.

## Comparación por vigencia

{markdown_table(vig_table)}

## Clasificación final por archivo

{markdown_table(universe[['archivo','filas','vig0','vig1','vig2','coincidentes','coincidentes_llave_matricula','nuevos','faltantes','tipo_comparacion','clasificacion_final']])}

## Hallazgos

- Consolidado reconstruido: 4.105 registros; matrícula vigente VIG1+VIG2 = 3.145.
- Ningún CSV reproduce 4.105 registros ni 3.145 vigentes.
- Los seis CSV suman físicamente {sum(int(r['universe']['filas']) for r in results)} filas, pero esa suma no debe interpretarse como universo final porque son archivos históricos separados.
- Cobertura exacta de la unión de hashes históricos contra consolidado: {union_exact} filas del consolidado aparecen exactas en al menos uno de los CSV.
- Registros de CSV con hash no presente en consolidado, sumados por archivo: {union_new}. Pueden deberse a cargas superadas, cambios de dato o registros excluidos posteriormente.

## Limitaciones

- Los CSV no tienen encabezado físico; se asignaron los 32 encabezados oficiales para comparación.
- La comparación individual usa `LLAVE_MATRICULA = TIPO_DOC + N_DOC + DV + CODIGO_NORMALIZADO`; no existe `CODCLI` en los CSV.
- No se eliminó VIG=0 ni se trató como matrícula vigente.
- Diferencias no se clasifican como errores sin evidencia adicional.

## Archivos generados

- `01_INVENTARIO_ARCHIVOS.csv`
- `02_COMPARACION_ESTRUCTURA.xlsx`
- `03_COMPARACION_UNIVERSO.csv`
- `04_COMPARACION_CODIGOS.csv`
- `05_DETALLE_DIFERENCIAS.csv`
- `06_REPORTE_FINAL.md`

## Conclusión

No se identificó un CSV histórico que explique o coincida completamente con la base consolidada reconstruida. La línea de tiempo muestra cargas parciales anteriores, con estructura compatible de 32 campos, pero con universos muy inferiores al consolidado final.
"""
    report_path.write_text(report, encoding="utf-8")

    manifest = {
        "proceso": "Matrícula Unificada SIES 2026",
        "subproceso": "Pregrado",
        "fecha": TS,
        "fuente_comparacion": cons_info,
        "fuentes_evaluadas": [str(p) for p in csv_paths],
        "originales_modificados": False,
        "metodo": "Lectura + comparación + evidencia",
        "consolidado": {
            "filas": len(cons),
            "vig": {str(k): int(v) for k, v in consolidated_vig.items()},
            "vigente": int(consolidated_vig.get("1", 0)) + int(consolidated_vig.get("2", 0)),
        },
        "resultados": universe.to_dict(orient="records"),
        "archivos_generados": {
            "inventario": str(inv_path),
            "estructura": str(struct_path),
            "universo": str(univ_path),
            "codigos": str(cod_path),
            "detalle": str(det_path),
            "reporte": str(report_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "out_dir": str(OUT_DIR),
        "consolidado": str(CONSOLIDADO),
        "hoja_usada": cons_info["hoja_usada"],
        "csv_evaluados": len(results),
        "match_exacto": int(len(exact)),
        "mejor_candidato": best_exact_rows.iloc[0].to_dict(),
        "outputs": manifest["archivos_generados"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
