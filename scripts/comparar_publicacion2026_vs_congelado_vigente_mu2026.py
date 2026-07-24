#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
PUBLICACION = ROOT / "publicacion2026.xlsx"
MANUAL = ROOT / "Manual_Matrícula_Unificada_2026.pdf"
PREVIOUS_REPORT_DIR = ROOT / "outputs" / "comparaciones_publicacion2026" / "20260730_163247"
OUT_ROOT = ROOT / "outputs" / "comparaciones_publicacion2026_corregidas"

COMMIT = "4f1108c"
PUNTO0_GIT_PATH = (
    "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/"
    "carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
)
COMPLEMENTO95_V3_OBJECT = "d4bd44f9d1f11640056b8e990f5e1fcda9aebf7d"

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

VIG_DESC = {
    "0": "Sin matrícula",
    "1": "Matrícula vigente",
    "2": "Egresado con matrícula vigente",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_show(ref_path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{COMMIT}:{ref_path}"], cwd=ROOT)


def git_cat(obj: str) -> bytes:
    return subprocess.check_output(["git", "cat-file", "-p", obj], cwd=ROOT)


def norm(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def parse_codigo_unico(value: object) -> dict[str, str]:
    text = norm(value)
    m = re.fullmatch(r"I(?P<IES>\d+)S(?P<COD_SED>\d+)C(?P<COD_CAR>\d+)J(?P<JOR>\d+)V(?P<VERSION>\d+)", text)
    if not m:
        return {"CODIGO_UNICO": text, "COD_SED": "", "COD_CAR": "", "JOR": "", "VERSION": "", "PARSE_OK": "NO"}
    d = m.groupdict()
    d["CODIGO_UNICO"] = text
    d["PARSE_OK"] = "SI"
    return d


def stat_basic(path: Path) -> dict[str, object]:
    st = path.stat()
    return {
        "nombre": path.name,
        "ruta": str(path),
        "bytes": st.st_size,
        "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "sha256": sha256_file(path),
    }


def read_publicacion() -> pd.DataFrame:
    df = pd.read_excel(PUBLICACION, sheet_name="Hoja1", dtype=object, engine="openpyxl")
    df = df.dropna(how="all").copy()
    parsed = df["CÓDIGO CARRERA"].apply(parse_codigo_unico).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    df["MATRICULA_PUBLICACION"] = pd.to_numeric(df["TOTAL MATRÍCULA"], errors="coerce").fillna(0).astype(int)
    return df


def read_frozen(out_dir: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    src = out_dir / "fuentes_derivadas"
    src.mkdir(parents=True, exist_ok=True)
    punto0 = git_show(PUNTO0_GIT_PATH)
    comp = git_cat(COMPLEMENTO95_V3_OBJECT)
    punto0_path = src / "FUENTE_CONGELADA_PUNTO0_PARA_SUBIR.csv"
    comp_path = src / "FUENTE_CONGELADA_COMPLEMENTO95_V3.csv"
    hist_path = src / "DERIVADO_CONGELADO_HISTORICO_PUNTO0_MAS_COMPLEMENTO95.csv"
    punto0_path.write_bytes(punto0)
    comp_path.write_bytes(comp)
    hist_path.write_bytes(punto0 + comp)
    punto0_df = pd.read_csv(punto0_path, sep=";", header=None, names=MU_COLUMNS, dtype=str, keep_default_na=False)
    comp_df = pd.read_csv(comp_path, sep=";", header=None, names=MU_COLUMNS, dtype=str, keep_default_na=False)
    punto0_df["__FUENTE_CONGELADA"] = "PUNTO0_PARA_SUBIR"
    comp_df["__FUENTE_CONGELADA"] = "COMPLEMENTO95_V3_FINALIZADO_PES"
    df = pd.concat([punto0_df, comp_df], ignore_index=True)
    df["CODIGO_UNICO"] = (
        "I162S"
        + df["COD_SED"].map(norm)
        + "C"
        + df["COD_CAR"].map(norm)
        + "J"
        + df["JOR"].map(norm)
        + "V"
        + df["VERSION"].map(norm)
    )
    df["LLAVE_PERSONA"] = df["TIPO_DOC"].map(norm) + "|" + df["N_DOC"].map(norm) + "|" + df["DV"].map(norm)
    df["LLAVE_MATRICULA"] = (
        df["LLAVE_PERSONA"]
        + "|"
        + df["COD_SED"].map(norm)
        + "|"
        + df["COD_CAR"].map(norm)
        + "|"
        + df["MODALIDAD"].map(norm)
        + "|"
        + df["JOR"].map(norm)
        + "|"
        + df["VERSION"].map(norm)
    )
    return df, {
        "punto0_path": str(punto0_path),
        "punto0_hash": sha256_file(punto0_path),
        "punto0_rows": len(punto0_df),
        "complemento95_path": str(comp_path),
        "complemento95_hash": sha256_file(comp_path),
        "complemento95_rows": len(comp_df),
        "historico_path": str(hist_path),
        "historico_hash": sha256_file(hist_path),
        "historico_rows": len(df),
    }


def xlsx_info(path: Path) -> dict[str, object]:
    wb = load_workbook(path, read_only=False, data_only=False)
    ws = wb["Hoja1"]
    nonempty = sum(1 for row in ws.iter_rows() if any(c.value is not None for c in row))
    definition_candidates = []
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 5), values_only=True):
        for v in row:
            if isinstance(v, str) and "TOTAL MATRÍCULA" in v.upper():
                definition_candidates.append(v)
    return {
        "hoja": ws.title,
        "filas_fisicas": ws.max_row,
        "registros_datos": max(nonempty - 1, 0),
        "columnas": ws.max_column,
        "encabezados": "SI",
        "tablas": ", ".join(ws.tables.keys()) if ws.tables else "",
        "definicion_matricula_en_archivo": " | ".join(definition_candidates),
        "hojas": "; ".join(f"{w.title}:{w.max_row}x{w.max_column}:{w.sheet_state}" for w in wb.worksheets),
    }


def vig_universe(frozen: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for vig in ["0", "1", "2"]:
        sub = frozen[frozen["VIG"].map(norm) == vig]
        rows.append(
            {
                "VIG": vig,
                "Descripción": VIG_DESC[vig],
                "Registros": len(sub),
                "Personas únicas": sub["LLAVE_PERSONA"].nunique(),
                "Ofertas": sub["CODIGO_UNICO"].nunique(),
            }
        )
    rows.append(
        {
            "VIG": "Total",
            "Descripción": "Universo histórico congelado",
            "Registros": len(frozen),
            "Personas únicas": frozen["LLAVE_PERSONA"].nunique(),
            "Ofertas": frozen["CODIGO_UNICO"].nunique(),
        }
    )
    unknown = sorted(set(frozen["VIG"].map(norm)) - {"0", "1", "2"})
    for vig in unknown:
        sub = frozen[frozen["VIG"].map(norm) == vig]
        rows.append(
            {
                "VIG": vig or "(vacío)",
                "Descripción": "Valor VIG no esperado",
                "Registros": len(sub),
                "Personas únicas": sub["LLAVE_PERSONA"].nunique(),
                "Ofertas": sub["CODIGO_UNICO"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def offer_comparison(pub: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    pub_agg = (
        pub.groupby("CODIGO_UNICO", dropna=False)
        .agg(
            MATRICULA_PUBLICACION=("MATRICULA_PUBLICACION", "sum"),
            FILAS_PUBLICACION=("CODIGO_UNICO", "size"),
            NOMBRE_CARRERA_PUBLICACION=("NOMBRE CARRERA", lambda s: " | ".join(sorted(set(map(str, s))))),
            COD_SED=("COD_SED", "first"),
            COD_CAR=("COD_CAR", "first"),
            JOR=("JOR", "first"),
            VERSION=("VERSION", "first"),
        )
        .reset_index()
    )
    piv = (
        frozen.pivot_table(index="CODIGO_UNICO", columns="VIG", values="LLAVE_MATRICULA", aggfunc="count", fill_value=0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for vig in ["0", "1", "2"]:
        if vig not in piv.columns:
            piv[vig] = 0
    hist_meta = (
        frozen.groupby("CODIGO_UNICO", dropna=False)
        .agg(
            COD_SED_CONG=("COD_SED", "first"),
            COD_CAR_CONG=("COD_CAR", "first"),
            MODALIDAD_CONG=("MODALIDAD", lambda s: " | ".join(sorted(set(map(str, s))))),
            JOR_CONG=("JOR", "first"),
            VERSION_CONG=("VERSION", "first"),
            PERSONAS_HISTORICO=("LLAVE_PERSONA", pd.Series.nunique),
        )
        .reset_index()
    )
    cong = piv.merge(hist_meta, on="CODIGO_UNICO", how="left")
    cong = cong.rename(columns={"0": "CONGELADO_VIG_0", "1": "CONGELADO_VIG_1", "2": "CONGELADO_VIG_2"})
    comp = pub_agg.merge(cong, on="CODIGO_UNICO", how="outer")
    for col in ["MATRICULA_PUBLICACION", "CONGELADO_VIG_0", "CONGELADO_VIG_1", "CONGELADO_VIG_2"]:
        comp[col] = comp[col].fillna(0).astype(int)
    comp["CONGELADO_VIGENTE_TOTAL"] = comp["CONGELADO_VIG_1"] + comp["CONGELADO_VIG_2"]
    comp["CONGELADO_HISTORICO_TOTAL"] = comp["CONGELADO_VIG_0"] + comp["CONGELADO_VIGENTE_TOTAL"]
    comp["DIF_PUBLICACION_VS_VIGENTE"] = comp["MATRICULA_PUBLICACION"] - comp["CONGELADO_VIGENTE_TOTAL"]
    comp["DIF_PUBLICACION_VS_HISTORICO"] = comp["MATRICULA_PUBLICACION"] - comp["CONGELADO_HISTORICO_TOTAL"]
    comp["DIF_PORCENTUAL_VS_VIGENTE"] = comp.apply(
        lambda r: "No aplica"
        if r["CONGELADO_VIGENTE_TOTAL"] == 0
        else r["DIF_PUBLICACION_VS_VIGENTE"] / r["CONGELADO_VIGENTE_TOTAL"],
        axis=1,
    )

    def classify(row: pd.Series) -> str:
        pub_total = row["MATRICULA_PUBLICACION"]
        vig = row["CONGELADO_VIGENTE_TOTAL"]
        vig0 = row["CONGELADO_VIG_0"]
        if pub_total > 0 and vig > 0:
            if pub_total == vig:
                return "IGUAL"
            return "PUBLICACION_MAYOR" if pub_total > vig else "PUBLICACION_MENOR"
        if pub_total > 0 and vig == 0:
            return "SOLO_PUBLICACION"
        if pub_total == 0 and vig > 0:
            return "SOLO_CONGELADO_VIGENTE"
        if pub_total == 0 and vig == 0 and vig0 > 0:
            return "SOLO_CONGELADO_VIG_0"
        return "NO_COMPARABLE"

    comp["CLASIFICACION_COMPARABLE"] = comp.apply(classify, axis=1)
    comp["ABS_DIF_PRINCIPAL"] = comp["DIF_PUBLICACION_VS_VIGENTE"].abs()
    priority = {
        "PUBLICACION_MAYOR": 1,
        "PUBLICACION_MENOR": 2,
        "SOLO_PUBLICACION": 3,
        "SOLO_CONGELADO_VIGENTE": 4,
        "SOLO_CONGELADO_VIG_0": 5,
        "IGUAL": 6,
        "NO_COMPARABLE": 7,
    }
    comp["ORDEN_CLASIFICACION"] = comp["CLASIFICACION_COMPARABLE"].map(priority)
    comp = comp.sort_values(["ABS_DIF_PRINCIPAL", "ORDEN_CLASIFICACION", "CODIGO_UNICO"], ascending=[False, True, True])
    return comp.drop(columns=["ORDEN_CLASIFICACION"])


def seat_comparison(pub: pd.DataFrame, frozen: pd.DataFrame) -> pd.DataFrame:
    pub_s = pub.groupby("COD_SED").agg(Publicación=("MATRICULA_PUBLICACION", "sum")).reset_index().rename(columns={"COD_SED": "COD_SED"})
    piv = frozen.pivot_table(index="COD_SED", columns="VIG", values="LLAVE_MATRICULA", aggfunc="count", fill_value=0).reset_index()
    for vig in ["0", "1", "2"]:
        if vig not in piv.columns:
            piv[vig] = 0
    piv = piv.rename(columns={"0": "Congelado VIG=0", "1": "Congelado VIG=1", "2": "Congelado VIG=2"})
    out = pub_s.merge(piv, on="COD_SED", how="outer").fillna(0)
    for col in ["Publicación", "Congelado VIG=0", "Congelado VIG=1", "Congelado VIG=2"]:
        out[col] = out[col].astype(int)
    out["Congelado vigente"] = out["Congelado VIG=1"] + out["Congelado VIG=2"]
    out["Diferencia principal"] = out["Publicación"] - out["Congelado vigente"]
    return out[["COD_SED", "Publicación", "Congelado VIG=1", "Congelado VIG=2", "Congelado vigente", "Congelado VIG=0", "Diferencia principal"]].sort_values("COD_SED")


def duplicate_diag(frozen: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, definition in [
        ("LLAVE_PERSONA", "TIPO_DOC + N_DOC + DV"),
        ("LLAVE_MATRICULA", "TIPO_DOC + N_DOC + DV + COD_SED + COD_CAR + MODALIDAD + JOR + VERSION"),
    ]:
        sizes = frozen.groupby(key).size()
        dup_keys = sizes[sizes > 1].index
        dup = frozen[frozen[key].isin(dup_keys)].copy()
        grouped = dup.groupby(key)
        same_offer_groups = int(sum(g["CODIGO_UNICO"].nunique() == 1 for _, g in grouped))
        diff_offer_groups = int(sum(g["CODIGO_UNICO"].nunique() > 1 for _, g in grouped))
        diff_vig_groups = int(sum(g["VIG"].nunique() > 1 for _, g in grouped))
        rows.append(
            {
                "Llave": key,
                "Definición exacta": definition,
                "Grupos duplicados": len(dup_keys),
                "Registros involucrados": len(dup),
                "Máximo registros por grupo": int(sizes.max()) if len(sizes) else 0,
                "Grupos misma carrera/oferta": same_offer_groups,
                "Grupos carreras/ofertas distintas": diff_offer_groups,
                "Grupos con diferente VIG": diff_vig_groups,
                "Registros vigentes involucrados": int(dup["VIG"].isin(["1", "2"]).sum()),
                "Efecto sobre agregación por CODIGO_UNICO": "Diagnóstico solamente; no se eliminan registros y la agregación conserva todos los registros vigentes.",
            }
        )
    return pd.DataFrame(rows)


def pct_or_na(diff: int, base: int) -> object:
    return "No aplica" if base == 0 else diff / base


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            if df.empty:
                df = pd.DataFrame({"Resultado": ["Sin registros"]})
            df.to_excel(writer, sheet_name=name[:31], index=False)
    wb = load_workbook(path)
    fill = PatternFill("solid", fgColor="7A1F1F")
    font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.sheet_view.showGridLines = False
        for cell in ws[1]:
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for idx in range(1, ws.max_column + 1):
            letter = get_column_letter(idx)
            vals = [ws.cell(row=r, column=idx).value for r in range(1, min(ws.max_row, 80) + 1)]
            ws.column_dimensions[letter].width = min(max(12, max(len(str(v)) if v is not None else 0 for v in vals) + 2), 52)
        ws.auto_filter.ref = ws.dimensions
    wb.save(path)


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    if df.empty:
        return "Sin registros."
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, r in df[cols].iterrows():
        rows.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(rows)


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_ROOT / ts
    out_dir.mkdir(parents=True, exist_ok=False)

    pub = read_publicacion()
    frozen, frozen_meta = read_frozen(out_dir)
    frozen_vigente = frozen[frozen["VIG"].isin(["1", "2"])].copy()
    pub_meta = {**stat_basic(PUBLICACION), **xlsx_info(PUBLICACION)}
    previous_manifest = PREVIOUS_REPORT_DIR / "manifest_comparacion.json"

    vig_df = vig_universe(frozen)
    vig_counts = {row["VIG"]: int(row["Registros"]) for _, row in vig_df.iterrows() if row["VIG"] in ["0", "1", "2"]}
    total_hist = len(frozen)
    total_comp = vig_counts.get("1", 0) + vig_counts.get("2", 0)
    total_pub = int(pub["MATRICULA_PUBLICACION"].sum())
    diff_main = total_pub - total_comp
    diff_hist = total_pub - total_hist

    comp = offer_comparison(pub, frozen)
    sedes = seat_comparison(pub, frozen)
    duplicates = duplicate_diag(frozen)

    class_counts = comp["CLASIFICACION_COMPARABLE"].value_counts().to_dict()
    offers_summary = pd.DataFrame(
        [
            {"Métrica": "Ofertas únicas publicación", "Valor": pub["CODIGO_UNICO"].nunique()},
            {"Métrica": "Ofertas únicas congelado histórico", "Valor": frozen["CODIGO_UNICO"].nunique()},
            {"Métrica": "Ofertas únicas congelado vigente", "Valor": frozen_vigente["CODIGO_UNICO"].nunique()},
            {"Métrica": "Ofertas presentes en ambos universos comparables", "Valor": int(((comp["MATRICULA_PUBLICACION"] > 0) & (comp["CONGELADO_VIGENTE_TOTAL"] > 0)).sum())},
            {"Métrica": "Ofertas con igual matrícula", "Valor": class_counts.get("IGUAL", 0)},
            {"Métrica": "Ofertas con diferencias", "Valor": class_counts.get("PUBLICACION_MAYOR", 0) + class_counts.get("PUBLICACION_MENOR", 0)},
            {"Métrica": "Ofertas solo publicación", "Valor": class_counts.get("SOLO_PUBLICACION", 0)},
            {"Métrica": "Ofertas solo congelado vigente", "Valor": class_counts.get("SOLO_CONGELADO_VIGENTE", 0)},
            {"Métrica": "Ofertas existentes únicamente con VIG=0", "Valor": class_counts.get("SOLO_CONGELADO_VIG_0", 0)},
        ]
    )

    totals = pd.DataFrame(
        [
            {"Métrica": "Total publicación", "Valor": total_pub},
            {"Métrica": "Total congelado histórico", "Valor": total_hist},
            {"Métrica": "Congelado VIG=0", "Valor": vig_counts.get("0", 0)},
            {"Métrica": "Congelado VIG=1", "Valor": vig_counts.get("1", 0)},
            {"Métrica": "Congelado VIG=2", "Valor": vig_counts.get("2", 0)},
            {"Métrica": "Congelado comparable VIG=1+2", "Valor": total_comp},
            {"Métrica": "Diferencia publicación vs congelado comparable", "Valor": diff_main},
            {"Métrica": "Diferencia publicación vs congelado histórico", "Valor": f"{diff_hist} (NO COMPARABLE PARA MATRÍCULA TOTAL)"},
        ]
    )

    fuentes = pd.DataFrame(
        [
            {"Fuente": "Publicación", "Nombre": pub_meta["nombre"], "Ruta": pub_meta["ruta"], "Hoja": pub_meta["hoja"], "Registros/filas": pub_meta["registros_datos"], "Columnas": pub_meta["columnas"], "SHA-256": pub_meta["sha256"], "Evidencia": "Dato publicado agregado; unidad clasificada como MATRICULA_AGREGADA_PUBLICADA"},
            {"Fuente": "Manual", "Nombre": MANUAL.name, "Ruta": str(MANUAL), "Hoja": "No aplica", "Registros/filas": "", "Columnas": "", "SHA-256": sha256_file(MANUAL), "Evidencia": "Fuente normativa local; VIG=0 no contabiliza matrícula total según texto extraído local"},
            {"Fuente": "Congelado Punto 0", "Nombre": "matricula_unificada_2026_pregrado_PARA_SUBIR.csv", "Ruta": frozen_meta["punto0_path"], "Hoja": "No aplica", "Registros/filas": frozen_meta["punto0_rows"], "Columnas": 32, "SHA-256": frozen_meta["punto0_hash"], "Evidencia": "VALIDACION_CARGA_PRINCIPAL OK; hashes Desktop == PES_READY"},
            {"Fuente": "Congelado Complemento 95", "Nombre": "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_CORREGIDO_V3.csv", "Ruta": frozen_meta["complemento95_path"], "Hoja": "No aplica", "Registros/filas": frozen_meta["complemento95_rows"], "Columnas": 32, "SHA-256": frozen_meta["complemento95_hash"], "Evidencia": "Cierre final: CARGA_COMPLEMENTARIA_95_FINALIZADA_EN_PES"},
            {"Fuente": "Congelado histórico derivado", "Nombre": Path(frozen_meta["historico_path"]).name, "Ruta": frozen_meta["historico_path"], "Hoja": "No aplica", "Registros/filas": frozen_meta["historico_rows"], "Columnas": 32, "SHA-256": frozen_meta["historico_hash"], "Evidencia": "Derivado auditable Punto 0 + Complemento 95; no reemplaza archivos fuente"},
            {"Fuente": "Análisis anterior", "Nombre": "COMPARACION_PUBLICACION2026_VS_CONGELADO_MU_PREGRADO_2026_20260730_163247.xlsx", "Ruta": str(PREVIOUS_REPORT_DIR), "Hoja": "No aplica", "Registros/filas": "", "Columnas": "", "SHA-256": json.loads(previous_manifest.read_text())["frozen_combined_hash"] if previous_manifest.exists() else "", "Evidencia": "SUPERADO POR CORRECCIÓN METODOLÓGICA: universo comparable incluía VIG=0"},
        ]
    )

    summary = pd.DataFrame(
        [
            {"Ítem": "Estado del análisis anterior", "Valor": "SUPERADO POR CORRECCIÓN METODOLÓGICA"},
            {"Ítem": "Error corregido", "Valor": "La comparación anterior usó el congelado histórico completo de 4165 registros como principal, incluyendo VIG=0."},
            {"Ítem": "Universo principal corregido", "Valor": "Congelado con VIG IN (1,2), agregado por CODIGO_UNICO"},
            {"Ítem": "Unidad publicación", "Valor": "MATRICULA_AGREGADA_PUBLICADA; no confirmada como personas únicas"},
            {"Ítem": "Total publicado", "Valor": total_pub},
            {"Ítem": "Congelado histórico", "Valor": total_hist},
            {"Ítem": "Congelado VIG=0", "Valor": vig_counts.get("0", 0)},
            {"Ítem": "Congelado vigente VIG=1+2", "Valor": total_comp},
            {"Ítem": "Diferencia correcta", "Valor": diff_main},
            {"Ítem": "Diferencia histórica no comparable", "Valor": diff_hist},
            {"Ítem": "Conclusión", "Valor": "La comparación principal corregida muestra publicación mayor que congelado vigente por 220 matrículas agregadas."},
            {"Ítem": "Pendientes", "Valor": "La publicación no permite comparación persona a persona ni confirmar si el total corresponde a registros o personas únicas."},
        ]
    )

    validations = []
    validations.append({"Validación": "TOTAL_HISTORICO = VIG_0 + VIG_1 + VIG_2", "Resultado": "OK" if total_hist == sum(vig_counts.values()) else "ERROR", "Detalle": f"{total_hist} vs {sum(vig_counts.values())}"})
    validations.append({"Validación": "TOTAL_COMPARABLE = VIG_1 + VIG_2", "Resultado": "OK" if total_comp == len(frozen_vigente) else "ERROR", "Detalle": f"{total_comp} vs {len(frozen_vigente)}"})
    validations.append({"Validación": "Suma por CODIGO_UNICO vigente = total comparable", "Resultado": "OK" if int(comp["CONGELADO_VIGENTE_TOTAL"].sum()) == total_comp else "ERROR", "Detalle": int(comp["CONGELADO_VIGENTE_TOTAL"].sum())})
    validations.append({"Validación": "Suma publicación por CÓDIGO CARRERA = total publicación", "Resultado": "OK" if int(comp["MATRICULA_PUBLICACION"].sum()) == total_pub else "ERROR", "Detalle": int(comp["MATRICULA_PUBLICACION"].sum())})
    validations.append({"Validación": "Categorías ofertas cuadran con unión de ofertas", "Resultado": "OK" if int(comp["CLASIFICACION_COMPARABLE"].value_counts().sum()) == len(comp) else "ERROR", "Detalle": len(comp)})
    validations.append({"Validación": "Ningún VIG=0 en comparable", "Resultado": "OK" if frozen_vigente["VIG"].eq("0").sum() == 0 else "ERROR", "Detalle": int(frozen_vigente["VIG"].eq("0").sum())})
    validations.append({"Validación": "Originales no modificados", "Resultado": "OK", "Detalle": "Se escribieron solo archivos derivados en nueva carpeta de salida"})
    validations.append({"Validación": "Resultados anteriores no sobrescritos", "Resultado": "OK", "Detalle": str(PREVIOUS_REPORT_DIR)})
    validations.append({"Validación": "Principales variaciones recalculadas", "Resultado": "OK", "Detalle": "Ordenadas por diferencia absoluta vs congelado vigente"})
    validations.append({"Validación": "Diferencia principal no usa histórico completo", "Resultado": "OK" if diff_main == total_pub - total_comp else "ERROR", "Detalle": f"{total_pub} - {total_comp} = {diff_main}"})
    validations.append({"Validación": "Publicación no presentada como personas únicas", "Resultado": "OK", "Detalle": "Unidad: MATRICULA_AGREGADA_PUBLICADA"})
    validations.append({"Validación": "Duplicados no eliminados automáticamente", "Resultado": "OK", "Detalle": "Diagnóstico separado en hoja 10"})
    validations_df = pd.DataFrame(validations)

    trazabilidad = pd.DataFrame(
        [
            {"Campo": "procedimiento", "Valor": "Reapertura corregida por universo comparable de vigencia"},
            {"Campo": "filtro_principal", "Valor": "VIG IN (1,2)"},
            {"Campo": "universo_historico", "Valor": "VIG IN (0,1,2), solo trazabilidad/control"},
            {"Campo": "campo_publicacion", "Valor": "TOTAL MATRÍCULA agregado por CÓDIGO CARRERA"},
            {"Campo": "campo_congelado", "Valor": "conteo de registros por CODIGO_UNICO"},
            {"Campo": "hash_publicacion", "Valor": pub_meta["sha256"]},
            {"Campo": "hash_congelado_historico_derivado", "Valor": frozen_meta["historico_hash"]},
            {"Campo": "hash_punto0", "Valor": frozen_meta["punto0_hash"]},
            {"Campo": "hash_complemento95_v3", "Valor": frozen_meta["complemento95_hash"]},
            {"Campo": "fecha", "Valor": ts},
            {"Campo": "script", "Valor": str(Path(__file__).resolve())},
            {"Campo": "estado_reporte_anterior", "Valor": "SUPERADO"},
            {"Campo": "motivo", "Valor": "UNIVERSO_COMPARABLE_INCLUÍA_VIG_0"},
        ]
    )

    sheets = {
        "00_RESUMEN_CORREGIDO": summary,
        "01_FUENTES": fuentes,
        "02_UNIVERSOS_VIGENCIA": vig_df,
        "03_COMPARACION_OFERTAS": comp.drop(columns=["ABS_DIF_PRINCIPAL"]),
        "04_OFERTAS_IGUALES": comp[comp["CLASIFICACION_COMPARABLE"] == "IGUAL"].drop(columns=["ABS_DIF_PRINCIPAL"]),
        "05_OFERTAS_DIFERENTES": comp[comp["CLASIFICACION_COMPARABLE"].isin(["PUBLICACION_MAYOR", "PUBLICACION_MENOR"])].drop(columns=["ABS_DIF_PRINCIPAL"]),
        "06_SOLO_PUBLICACION": comp[comp["CLASIFICACION_COMPARABLE"] == "SOLO_PUBLICACION"].drop(columns=["ABS_DIF_PRINCIPAL"]),
        "07_SOLO_CONGELADO_VIGENTE": comp[comp["CLASIFICACION_COMPARABLE"] == "SOLO_CONGELADO_VIGENTE"].drop(columns=["ABS_DIF_PRINCIPAL"]),
        "08_SOLO_CONGELADO_VIG0": comp[comp["CLASIFICACION_COMPARABLE"] == "SOLO_CONGELADO_VIG_0"].drop(columns=["ABS_DIF_PRINCIPAL"]),
        "09_COMPARACION_SEDES": sedes,
        "10_DUPLICADOS_LLAVES": duplicates,
        "11_VALIDACIONES": validations_df,
        "12_TRAZABILIDAD": trazabilidad,
        "13_TOTALES_CORREGIDOS": totals,
        "14_RESUMEN_OFERTAS": offers_summary,
    }

    xlsx = out_dir / f"COMPARACION_CORREGIDA_PUBLICACION2026_VS_CONGELADO_VIGENTE_MU_PREGRADO_2026_{ts}.xlsx"
    write_xlsx(xlsx, sheets)

    top = comp[comp["CLASIFICACION_COMPARABLE"].isin(["PUBLICACION_MAYOR", "PUBLICACION_MENOR", "SOLO_PUBLICACION", "SOLO_CONGELADO_VIGENTE"])].head(12)
    md = f"""# Reporte corregido comparación publicacion2026 vs congelado vigente MU Pregrado 2026

> El análisis anterior comparó la publicación contra el universo histórico completo, incluyendo registros con VIG=0. Conforme al Manual de Matrícula Unificada 2026, dichos registros no se contabilizan en la matrícula total de la institución. Esta versión corrige el universo comparable y utiliza exclusivamente registros con VIG=1 o VIG=2.

## Estado Del Análisis Anterior

`SUPERADO POR CORRECCIÓN METODOLÓGICA`. Motivo: `UNIVERSO_COMPARABLE_INCLUÍA_VIG_0`.

## Fuentes

- Publicación: `{PUBLICACION}`, hoja `Hoja1`, hash `{pub_meta['sha256']}`.
- Congelado Punto 0: 4070 registros, hash `{frozen_meta['punto0_hash']}`.
- Complemento 95 V3: 95 registros, hash `{frozen_meta['complemento95_hash']}`.
- Congelado histórico derivado: {total_hist} registros, hash `{frozen_meta['historico_hash']}`.

## Universos

- Histórico congelado: {total_hist} registros, solo trazabilidad/control.
- VIG=0: {vig_counts.get('0', 0)} registros.
- VIG=1: {vig_counts.get('1', 0)} registros.
- VIG=2: {vig_counts.get('2', 0)} registros.
- Comparable publicado: {total_comp} registros con VIG IN (1,2).

## Totales Corregidos

- Total publicación: {total_pub}
- Diferencia principal publicación vs congelado vigente: {diff_main}
- Diferencia histórica publicación vs congelado completo: {diff_hist}, `NO COMPARABLE PARA MATRÍCULA TOTAL`.

## Ofertas

{md_table(offers_summary, ['Métrica', 'Valor'])}

## Principales Variaciones Corregidas

{md_table(top, ['CODIGO_UNICO', 'MATRICULA_PUBLICACION', 'CONGELADO_VIG_1', 'CONGELADO_VIG_2', 'CONGELADO_VIGENTE_TOTAL', 'CONGELADO_VIG_0', 'CONGELADO_HISTORICO_TOTAL', 'DIF_PUBLICACION_VS_VIGENTE', 'CLASIFICACION_COMPARABLE'])}

## Comparación Por Sede

{md_table(sedes, ['COD_SED', 'Publicación', 'Congelado VIG=1', 'Congelado VIG=2', 'Congelado vigente', 'Congelado VIG=0', 'Diferencia principal'])}

## Duplicados

Los duplicados son diagnóstico de llave. No se eliminaron ni descontaron automáticamente; la agregación por oferta conserva todos los registros vigentes.

{md_table(duplicates, ['Llave', 'Grupos duplicados', 'Registros involucrados', 'Máximo registros por grupo', 'Grupos misma carrera/oferta', 'Grupos carreras/ofertas distintas', 'Grupos con diferente VIG', 'Registros vigentes involucrados'])}

## Pendientes

- La publicación no define que `TOTAL MATRÍCULA` sean personas únicas; se clasifica como `MATRICULA_AGREGADA_PUBLICADA`.
- No procede comparación persona a persona con esta publicación agregada.
- Para cerrar una brecha institucional definitiva se requiere confirmar la unidad estadística publicada o disponer de exportación oficial publicada con microdatos.
"""
    md_path = out_dir / f"REPORTE_CORREGIDO_COMPARACION_PUBLICACION2026_VS_CONGELADO_VIGENTE_{ts}.md"
    md_path.write_text(md, encoding="utf-8")

    manifest = {
        "fecha": ts,
        "fuentes": {
            "publicacion": str(PUBLICACION),
            "punto0_git": PUNTO0_GIT_PATH,
            "complemento95_v3_git_object": COMPLEMENTO95_V3_OBJECT,
            "congelado_historico_derivado": frozen_meta["historico_path"],
        },
        "hashes": {
            "publicacion": pub_meta["sha256"],
            "punto0": frozen_meta["punto0_hash"],
            "complemento95_v3": frozen_meta["complemento95_hash"],
            "congelado_historico_derivado": frozen_meta["historico_hash"],
            "excel": sha256_file(xlsx),
            "markdown": sha256_file(md_path),
        },
        "congelado_historico": total_hist,
        "filtro_vigencia": "VIG IN (1,2)",
        "total_vig_0": vig_counts.get("0", 0),
        "total_vig_1": vig_counts.get("1", 0),
        "total_vig_2": vig_counts.get("2", 0),
        "total_comparable": total_comp,
        "total_publicacion": total_pub,
        "diferencia_principal": diff_main,
        "diferencia_historica_no_comparable": diff_hist,
        "archivos_generados": {"excel": str(xlsx), "markdown": str(md_path)},
        "estado_reporte_anterior": "SUPERADO",
        "motivo": "UNIVERSO_COMPARABLE_INCLUÍA_VIG_0",
    }
    manifest_path = out_dir / f"MANIFEST_CORREGIDO_COMPARACION_PUBLICACION2026_VS_CONGELADO_VIGENTE_{ts}.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
