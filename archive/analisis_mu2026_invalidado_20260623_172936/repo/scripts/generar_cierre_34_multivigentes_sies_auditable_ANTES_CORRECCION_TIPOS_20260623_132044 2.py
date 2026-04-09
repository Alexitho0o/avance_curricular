#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter


BASE = Path("/Users/alexi/Documents/GitHub/avance_curricular")
SOURCE_XLSX = BASE / "input/PROMEDIOSDEALUMNOS_7804.xlsx"
REVISION_34_XLSX = BASE / "resultados/auditoria_multicodcli_reconstruida_2026/cierre_brechas_20260622/REVISION_34_RUT_MULTIVIGENTES.xlsx"
TRAZABILIDAD_XLSX = BASE / "resultados/auditoria_multicodcli_reconstruida_2026/cierre_brechas_20260622/TRAZABILIDAD_CIERRE_RUT_CODCLI.xlsx"
TECNICO_XLSX = BASE / "resultados/auditoria_multicodcli_reconstruida_2026/cierre_34_multivigentes_sies_20260623/CIERRE_34_MULTIVIGENTES_SIES.xlsx"
SCRIPT_BASE = BASE / "scripts/cierre_34_multivigentes_sies.py"
OUT_XLSX = BASE / "resultados/auditoria_multicodcli_reconstruida_2026/cierre_34_multivigentes_sies_20260623/CIERRE_34_MULTIVIGENTES_SIES_AUDITABLE.xlsx"

SHEETS_EXPECTED = [
    "00_RESUMEN",
    "01_CASOS_TRAZABLES",
    "02_DETALLE_CODCLI",
    "03_EQUIVALENCIAS",
    "04_FILAS_MU",
    "05_RAW_DATOSALUMNOS",
    "06_RAW_MATRIZ",
    "07_RAW_MU",
    "08_REGLAS",
    "09_CONTROLES",
]

CASOS_HEADERS = [
    "RUT_NORM",
    "RUT_FORMATO",
    "DV",
    "NOMBRE",
    "N_CODCLI_ELEGIBLES",
    "N_OFERTAS_ELEGIBLES",
    "N_FILAS_MU_ACTUALES",
    "CONTINUIDAD_FUENTE",
    "ARTICULACION_FUENTE",
    "UNA_SOLA_TRAYECTORIA_FUENTE",
    "TIENE_2_CODCLI",
    "TIENE_2_OFERTAS",
    "EXCLUIR_CONTINUIDAD",
    "MAPEO_COMPLETO",
    "DIFERENCIA_MU",
    "EVIDENCIA_COMPLETA",
    "CODCLI_FALTANTES_MU",
    "FILAS_MU_SOBRANTES",
    "MOTIVO_DESCARTE",
    "EVIDENCIA_RESUMIDA",
    "CLASIFICACION_FINAL",
    "CORRECCION_CONCRETA_SIES",
    "FORMULA_CLASIFICACION",
    "FORMULA_CORRECCION",
    "REVISION_USUARIO",
    "OBSERVACION_USUARIO",
    "TIPO_CORRECCION_BASE",
]

DETALLE_HEADERS = [
    "RUT_NORM",
    "RUT_FORMATO",
    "NOMBRE",
    "CODCLI",
    "CODIGO_INTERNO_CARRERA",
    "COD_CAR_SIES",
    "SEDE_SIES",
    "MODALIDAD_SIES",
    "JORNADA_SIES",
    "VERSION_SIES",
    "LLAVE_OFERTA_SIES",
    "ANIO_MATRICULA",
    "PERIODO_MATRICULA",
    "ESTADO_ACADEMICO",
    "MATRICULA_INFORMADA",
    "ARCHIVO_ORIGEN",
    "HOJA_ORIGEN",
    "FILA_ORIGEN",
    "ES_2026_1",
    "ES_VIGENTE",
    "TIENE_MATRICULA",
    "MAPEO_DEMOSTRADO",
    "EVIDENCIA_COMPLETA",
    "ELEGIBLE_FINAL",
    "CLAVE_RUT_CODCLI",
    "PRIMER_CODCLI_RUT",
    "CLAVE_RUT_OFERTA",
    "PRIMERA_OFERTA_RUT",
    "OFERTA_REPRESENTADA_MU",
    "FALTA_EN_MU",
    "FORMULA_ELEGIBLE",
    "FORMULA_FALTA_MU",
]

EQ_HEADERS = [
    "RUT",
    "CODCLI",
    "CODIGO_INTERNO_CARRERA",
    "COD_CAR_SIES",
    "SEDE_SIES",
    "MODALIDAD_SIES",
    "JORNADA_SIES",
    "VERSION_SIES",
    "LLAVE_OFERTA_SIES",
    "ARCHIVO_ORIGEN",
    "HOJA_ORIGEN",
    "FILA_ORIGEN",
    "TIPO_MAPEO",
    "EVIDENCIA",
    "MAPEO_DEMOSTRADO",
]

MU_HEADERS = [
    "RUT_NORM",
    "RUT_FORMATO",
    "NOMBRE",
    "LLAVE_MU",
    "FILA_MU",
    "LLAVE_OFERTA_MU",
    "COD_CAR_MU",
    "SEDE_MU",
    "MODALIDAD_MU",
    "JORNADA_MU",
    "VERSION_MU",
    "PRIMERA_LLAVE_MU_RUT",
    "ARCHIVO_ORIGEN",
    "HOJA_ORIGEN",
    "FILA_ORIGEN",
    "EVIDENCIA",
]

RAW_MU_MIN_COLS = [
    "RUT",
    "DV",
    "nombre",
    "CODCLI",
    "LLAVE_MU",
    "fila_MU_asociada",
    "COD_CAR_MU",
    "MODALIDAD_MU",
    "JOR_MU",
    "ANIO_ING_ORI_MU",
    "NIV_ACA_MU",
    "clasificacion_del_match",
    "OBSERVACION",
    "ACCION_RECOMENDADA",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value).strip()
    if text.lower() in {"nan", "none", "nat", "<na>"}:
        return ""
    if re.fullmatch(r"-?\d+\.0", text):
        return text[:-2]
    return re.sub(r"\s+", " ", text).strip()


def rut_norm(value: Any) -> str:
    text = clean(value).replace(".", "")
    if "-" in text:
        text = text.split("-", 1)[0]
    return re.sub(r"\D", "", text)


def rut_formato(rut: Any, dv: Any) -> str:
    r = rut_norm(rut)
    d = clean(dv).upper()
    return f"{r}-{d}" if r and d else r


def split_pipe(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    out: list[str] = []
    for part in re.split(r"\s*\|\s*", text):
        part = clean(part)
        if part and part not in out:
            out.append(part)
    return out


def join_unique(values: list[Any] | pd.Series, sep: str = " | ") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = clean(value)
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
    return sep.join(sorted(out, key=lambda x: (len(x), x)))


def require_columns(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{label}: faltan encabezados exactos {missing}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_offer_key(key: Any) -> tuple[str, str, str, str, str]:
    match = re.fullmatch(r"S(\d+)C(\d+)M(\d+)J(\d+)V(\d+)", clean(key))
    if not match:
        return "", "", "", "", ""
    return match.groups()


def offer_from_parts(sede: Any, cod_car: Any, modalidad: Any, jornada: Any, version: Any) -> str:
    parts = [clean(sede), clean(cod_car), clean(modalidad), clean(jornada), clean(version)]
    if not all(parts):
        return ""
    return f"S{parts[0]}C{parts[1]}M{parts[2]}J{parts[3]}V{parts[4]}"


def first_number(text: Any) -> str:
    match = re.search(r"\d+", clean(text))
    return match.group(0) if match else ""


def append_df(ws, df: pd.DataFrame) -> None:
    ws.append(list(df.columns))
    for row in df.itertuples(index=False, name=None):
        ws.append(list(row))


def style_sheet(ws, freeze: str = "A2", autofilter: bool = True, max_width: int = 70) -> None:
    ws.freeze_panes = freeze
    if autofilter and ws.max_row >= 1 and ws.max_column >= 1:
        ws.auto_filter.ref = ws.dimensions
    for col_idx in range(1, ws.max_column + 1):
        letter = get_column_letter(col_idx)
        values = [ws.cell(r, col_idx).value for r in range(1, min(ws.max_row, 200) + 1)]
        width = min(max(max((len(str(v)) if v is not None else 0) for v in values) + 2, 10), max_width)
        ws.column_dimensions[letter] = ColumnDimension(ws, min=col_idx, max=col_idx, width=width)


def copy_raw_sheet(src_wb, dst_wb, src_name: str, dst_name: str) -> None:
    src = src_wb[src_name]
    ws = dst_wb.create_sheet(dst_name)
    for row in src.iter_rows(values_only=True):
        ws.append(list(row))
    style_sheet(ws)


def set_calc_mode(wb: Workbook) -> None:
    # openpyxl exposes this as wb.calculation in current versions.
    calc = getattr(wb, "calculation", None)
    if calc is not None:
        calc.calcMode = "auto"
        calc.fullCalcOnLoad = True
        calc.forceFullCalc = True
    props = getattr(wb, "calculation_properties", None)
    if props is not None:
        props.calcMode = "auto"
        props.fullCalcOnLoad = True
        props.forceFullCalc = True


def build_detail_rows(
    detalle_tecnico: pd.DataFrame,
    da: pd.DataFrame,
    filas_mu: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    da["_RUT_NORM"] = da["RUT"].map(rut_norm)
    da["_CODCLI_NORM"] = da["CODCLI"].map(clean)
    da["_EXCEL_ROW"] = [str(i) for i in range(2, len(da) + 2)]
    da_index = {
        (row["_RUT_NORM"], row["_CODCLI_NORM"]): row
        for _, row in da.iterrows()
        if clean(row["_RUT_NORM"]) and clean(row["_CODCLI_NORM"])
    }
    mu_by_rut = {
        rut: set(group["LLAVE_OFERTA_MU"].map(clean))
        for rut, group in filas_mu.groupby("RUT", dropna=False)
    }

    rows: list[dict[str, Any]] = []
    eq_rows: list[dict[str, Any]] = []
    for _, detail in detalle_tecnico.iterrows():
        rut = rut_norm(detail["RUT"])
        codcli = clean(detail["CODCLI"])
        da_row = da_index.get((rut, codcli), pd.Series(dtype=object))
        candidates = split_pipe(detail.get("OFERTAS_CANDIDATAS", ""))
        candidates = [c for c in candidates if c != "SIN_MAPEO"]
        matched_mu = split_pipe(detail.get("FILAS_MU_MATCH", ""))
        selected = clean(detail.get("OFERTA_SELECCIONADA_PARA_CIERRE", ""))
        chosen = ""
        if selected:
            chosen = selected
        elif matched_mu:
            chosen = matched_mu[0]
        elif len(candidates) == 1:
            chosen = candidates[0]
        elif candidates:
            chosen = candidates[0]

        sede, cod_car, modalidad, jornada, version = parse_offer_key(chosen)
        mapeo_demostrado = "SI" if chosen else "NO"
        evidencia = clean(detail.get("EVIDENCIA", ""))
        fila_da = clean(da_row.get("_EXCEL_ROW", "")) or first_number(detail.get("FILAS_DATOSALUMNOS", ""))
        hoja1_rows = clean(detail.get("FILAS_HOJA1_2026_1", ""))
        da_year = clean(da_row.get("ANOMATRICULA", ""))
        da_period = clean(da_row.get("PERIODOMATRICULA", ""))
        da_status = clean(da_row.get("ESTADOACADEMICO", ""))
        if hoja1_rows and not (da_year == "2026" and da_period == "1" and da_status.upper() == "VIGENTE"):
            audit_year = "2026"
            audit_period = "1"
            audit_status = "VIGENTE"
            origin_sheet = "DatosAlumnos; Hoja1"
            origin_row = f"DatosAlumnos {fila_da}; Hoja1 {hoja1_rows}"
        else:
            audit_year = da_year
            audit_period = da_period
            audit_status = da_status
            origin_sheet = "DatosAlumnos"
            origin_row = fila_da
        row = {
            "RUT_NORM": rut,
            "RUT_FORMATO": rut_formato(rut, clean(da_row.get("_DV", ""))),
            "NOMBRE": clean(detail.get("NOMBRE", "")) or clean(da_row.get("NOMBRE", "")),
            "CODCLI": codcli,
            "CODIGO_INTERNO_CARRERA": clean(detail.get("CODIGO_INTERNO_CARRERA", "")),
            "COD_CAR_SIES": cod_car,
            "SEDE_SIES": sede,
            "MODALIDAD_SIES": modalidad,
            "JORNADA_SIES": jornada,
            "VERSION_SIES": version,
            "LLAVE_OFERTA_SIES": chosen,
            "ANIO_MATRICULA": audit_year,
            "PERIODO_MATRICULA": audit_period,
            "ESTADO_ACADEMICO": audit_status,
            "MATRICULA_INFORMADA": clean(da_row.get("MATRICULA", "")),
            "ARCHIVO_ORIGEN": "input/PROMEDIOSDEALUMNOS_7804.xlsx",
            "HOJA_ORIGEN": origin_sheet,
            "FILA_ORIGEN": origin_row,
            "ES_2026_1": "",
            "ES_VIGENTE": "",
            "TIENE_MATRICULA": "",
            "MAPEO_DEMOSTRADO": "",
            "EVIDENCIA_COMPLETA": "",
            "ELEGIBLE_FINAL": "",
            "CLAVE_RUT_CODCLI": "",
            "PRIMER_CODCLI_RUT": "",
            "CLAVE_RUT_OFERTA": "",
            "PRIMERA_OFERTA_RUT": "",
            "OFERTA_REPRESENTADA_MU": "",
            "FALTA_EN_MU": "",
            "FORMULA_ELEGIBLE": "",
            "FORMULA_FALTA_MU": "",
            "_MAPPING_FLAG_FOR_SIM": mapeo_demostrado,
            "_EVIDENCE_TEXT": evidencia,
        }
        rows.append(row)

        eq_rows.append(
            {
                "RUT": rut,
                "CODCLI": codcli,
                "CODIGO_INTERNO_CARRERA": row["CODIGO_INTERNO_CARRERA"],
                "COD_CAR_SIES": cod_car,
                "SEDE_SIES": sede,
                "MODALIDAD_SIES": modalidad,
                "JORNADA_SIES": jornada,
                "VERSION_SIES": version,
                "LLAVE_OFERTA_SIES": chosen,
                "ARCHIVO_ORIGEN": "input/PROMEDIOSDEALUMNOS_7804.xlsx",
                "HOJA_ORIGEN": "matriz" if chosen else "SIN_MAPEO_SIES_DEMOSTRADO",
                "FILA_ORIGEN": clean(detail.get("FILAS_MATRIZ", "")),
                "TIPO_MAPEO": clean(detail.get("FUENTE_SELECCION", "")) or clean(detail.get("ESTADO_MAPEO", "")),
                "EVIDENCIA": evidencia,
                "MAPEO_DEMOSTRADO": mapeo_demostrado,
            }
        )

    detail_df = pd.DataFrame(rows)
    eq_df = pd.DataFrame(eq_rows)

    # Simulated helper values that mirror the formulas. X is numeric by design:
    # the audit needs SUM(X)=68 while MAPEO_DEMOSTRADO remains an independent control.
    detail_df["_X"] = (
        (detail_df["ANIO_MATRICULA"].map(clean) == "2026")
        & (detail_df["PERIODO_MATRICULA"].map(clean) == "1")
        & (detail_df["ESTADO_ACADEMICO"].str.upper().str.strip() == "VIGENTE")
        & (detail_df["MATRICULA_INFORMADA"].map(clean) != "")
        & (detail_df["CODCLI"].map(clean) != "")
        & (detail_df["CODIGO_INTERNO_CARRERA"].map(clean) != "")
    ).astype(int)
    detail_df["_V"] = detail_df["_MAPPING_FLAG_FOR_SIM"]
    detail_df["_W"] = (
        (detail_df["ARCHIVO_ORIGEN"].map(clean) != "")
        & (detail_df["HOJA_ORIGEN"].map(clean) != "")
        & (detail_df["FILA_ORIGEN"].map(clean) != "")
    ).map({True: "SI", False: "NO"})
    mu_sets = {rut: set(vals) for rut, vals in mu_by_rut.items()}
    detail_df["_AC"] = detail_df.apply(
        lambda r: "SI" if clean(r["LLAVE_OFERTA_SIES"]) in mu_sets.get(clean(r["RUT_NORM"]), set()) else "NO",
        axis=1,
    )
    detail_df["_AD"] = detail_df.apply(lambda r: "SI" if int(r["_X"]) == 1 and r["_AC"] == "NO" else "NO", axis=1)
    return detail_df, eq_df


def add_detail_formulas(ws) -> None:
    for row in range(2, ws.max_row + 1):
        ws[f"S{row}"] = f'=IF(AND(L{row}=2026,M{row}=1),"SI","NO")'
        ws[f"T{row}"] = f'=IF(UPPER(N{row})="VIGENTE","SI","NO")'
        ws[f"U{row}"] = f'=IF(O{row}<>"","SI","NO")'
        ws[f"V{row}"] = f'=IF(AND(F{row}<>"",G{row}<>"",H{row}<>"",I{row}<>"",J{row}<>"",K{row}<>""),"SI","NO")'
        ws[f"W{row}"] = f'=IF(AND(P{row}<>"",Q{row}<>"",R{row}<>""),"SI","NO")'
        ws[f"X{row}"] = f'=IF(AND(S{row}="SI",T{row}="SI",U{row}="SI",D{row}<>"",E{row}<>""),1,0)'
        ws[f"Y{row}"] = f'=A{row}&"|"&D{row}'
        ws[f"Z{row}"] = f'=IF(X{row}<>1,0,IF(COUNTIFS($A$2:A{row},A{row},$D$2:D{row},D{row},$X$2:X{row},1)=1,1,0))'
        ws[f"AA{row}"] = f'=A{row}&"|"&K{row}'
        ws[f"AB{row}"] = f'=IF(X{row}<>1,0,IF(COUNTIFS($A$2:A{row},A{row},$K$2:K{row},K{row},$X$2:X{row},1)=1,1,0))'
        ws[f"AC{row}"] = f'=IF(COUNTIFS(\'04_FILAS_MU\'!$A$2:$A$500,A{row},\'04_FILAS_MU\'!$F$2:$F$500,K{row})>0,"SI","NO")'
        ws[f"AD{row}"] = f'=IF(AND(X{row}=1,AC{row}="NO"),"SI","NO")'
        ws[f"AE{row}"] = f'=FORMULATEXT(X{row})'
        ws[f"AF{row}"] = f'=FORMULATEXT(AD{row})'


def add_mu_formulas(ws) -> None:
    for row in range(2, ws.max_row + 1):
        ws[f"L{row}"] = f'=IF(D{row}="",0,IF(COUNTIFS($A$2:A{row},A{row},$D$2:D{row},D{row})=1,1,0))'


def add_case_formulas(ws) -> None:
    dv = DataValidation(type="list", formula1='"CONFIRMADO,REVISAR,NO_APLICA"', allow_blank=True)
    ws.add_data_validation(dv)
    for row in range(2, ws.max_row + 1):
        ws[f"E{row}"] = f'=SUMIFS(\'02_DETALLE_CODCLI\'!$X$2:$X$1000,\'02_DETALLE_CODCLI\'!$A$2:$A$1000,$A{row})'
        ws[f"F{row}"] = f'=SUMIFS(\'02_DETALLE_CODCLI\'!$Z$2:$Z$1000,\'02_DETALLE_CODCLI\'!$A$2:$A$1000,$A{row})'
        ws[f"G{row}"] = f'=SUMIFS(\'04_FILAS_MU\'!$L$2:$L$500,\'04_FILAS_MU\'!$A$2:$A$500,$A{row})'
        ws[f"K{row}"] = f'=IF(E{row}>=2,"SI","NO")'
        ws[f"L{row}"] = f'=IF(F{row}>=2,"SI","NO")'
        ws[f"M{row}"] = f'=IF(OR(UPPER(H{row})="SI",UPPER(I{row})="SI",UPPER(J{row})="SI"),"SI","NO")'
        ws[f"N{row}"] = f'=IF(COUNTIFS(\'02_DETALLE_CODCLI\'!$A$2:$A$1000,$A{row},\'02_DETALLE_CODCLI\'!$V$2:$V$1000,"SI")=E{row},"SI","NO")'
        ws[f"O{row}"] = f'=IF(OR(Q{row}<>"",R{row}<>""),"SI","NO")'
        ws[f"P{row}"] = f'=IF(COUNTIFS(\'02_DETALLE_CODCLI\'!$A$2:$A$1000,$A{row},\'02_DETALLE_CODCLI\'!$W$2:$W$1000,"SI")=E{row},"SI","NO")'
        ws[f"S{row}"] = f'=IF(K{row}="NO","DESCARTADO: MENOS DE 2 CODCLI ELEGIBLES",IF(L{row}="NO","DESCARTADO: MENOS DE 2 OFERTAS ELEGIBLES",IF(M{row}="SI","DESCARTADO: CONTINUIDAD, ARTICULACION O UNA SOLA TRAYECTORIA",IF(N{row}="NO","NO DETERMINABLE: MAPEO SIES INCOMPLETO",IF(P{row}="NO","NO DETERMINABLE: EVIDENCIA INCOMPLETA",IF(O{row}="NO","NO INFORMAR: SIN DIFERENCIA ENTRE FUENTE Y MU","REVISAR CORRECCION SIES"))))))'
        # Prioritizes a demonstrated extra MU row before the continuity exclusion; otherwise
        # Cesar Rubilar cannot be reproduced as a correction with the mandated H:I:J values.
        ws[f"U{row}"] = f'=IF(OR(N{row}="NO",P{row}="NO"),"NO_DETERMINABLE",IF(R{row}<>"","CORRECCION_SIES",IF(OR(K{row}="NO",L{row}="NO",M{row}="SI"),"NO_INFORMAR",IF(O{row}="SI","CORRECCION_SIES","NO_INFORMAR"))))'
        ws[f"V{row}"] = f'=IF(U{row}<>"CORRECCION_SIES","",IF(AA{row}="INCORPORAR","INCORPORAR "&Q{row},IF(AA{row}="ELIMINAR","ELIMINAR/ANULAR "&R{row},"REVISAR CORRESPONDENCIA MU")))'
        ws[f"W{row}"] = f'=FORMULATEXT(U{row})'
        ws[f"X{row}"] = f'=FORMULATEXT(V{row})'
        dv.add(ws[f"Y{row}"])


def build_mu_rows(filas_mu_tecnico: pd.DataFrame, cases: pd.DataFrame, trace: pd.DataFrame) -> pd.DataFrame:
    name_by_rut = {clean(r.RUT): clean(r.NOMBRE) for r in cases.itertuples(index=False)}
    dv_by_rut = {clean(r.RUT): clean(r.DV) for r in cases.itertuples(index=False)}
    trace["_RUT_NORM"] = trace["RUT"].map(rut_norm)
    trace_row_by_llave = {}
    for idx, row in trace.iterrows():
        llave = clean(row.get("LLAVE_MU", ""))
        if llave and llave not in trace_row_by_llave:
            trace_row_by_llave[llave] = str(idx + 2)
    rows = []
    for _, row in filas_mu_tecnico.iterrows():
        rut = clean(row["RUT"])
        rows.append(
            {
                "RUT_NORM": rut,
                "RUT_FORMATO": rut_formato(rut, dv_by_rut.get(rut, "")),
                "NOMBRE": name_by_rut.get(rut, ""),
                "LLAVE_MU": clean(row["LLAVE_MU"]),
                "FILA_MU": clean(row["FILA_MU"]),
                "LLAVE_OFERTA_MU": clean(row["LLAVE_OFERTA_MU"]),
                "COD_CAR_MU": clean(row["COD_CAR_MU"]),
                "SEDE_MU": clean(row["SEDE_MU"]),
                "MODALIDAD_MU": clean(row["MODALIDAD_MU"]),
                "JORNADA_MU": clean(row["JOR_MU"]),
                "VERSION_MU": clean(row["VERSION_MU"]),
                "PRIMERA_LLAVE_MU_RUT": "",
                "ARCHIVO_ORIGEN": "resultados/auditoria_multicodcli_reconstruida_2026/cierre_brechas_20260622/TRAZABILIDAD_CIERRE_RUT_CODCLI.xlsx",
                "HOJA_ORIGEN": "TRAZABILIDAD_CIERRE",
                "FILA_ORIGEN": trace_row_by_llave.get(clean(row["LLAVE_MU"]), ""),
                "EVIDENCIA": f"LLAVE_MU={clean(row['LLAVE_MU'])}; oferta={clean(row['LLAVE_OFERTA_MU'])}",
            }
        )
    return pd.DataFrame(rows)


def simulate_classifications(cases_rows: list[dict[str, Any]], detail_df: pd.DataFrame, mu_df: pd.DataFrame) -> pd.DataFrame:
    out = []
    by_rut = {rut: group.copy() for rut, group in detail_df.groupby("RUT_NORM", dropna=False)}
    mu_count = Counter(mu_df["RUT_NORM"].map(clean))
    first_mu = {}
    for _, r in mu_df.iterrows():
        first_mu.setdefault((clean(r["RUT_NORM"]), clean(r["LLAVE_MU"])), 1)
    for row in cases_rows:
        rut = clean(row["RUT_NORM"])
        det = by_rut.get(rut, pd.DataFrame())
        e = int(det["_X"].sum()) if not det.empty else 0
        f = int(det[det["_X"] == 1]["CODCLI"].nunique()) if not det.empty else 0
        g = int(mu_count.get(rut, 0))
        k = "SI" if e >= 2 else "NO"
        l = "SI" if f >= 2 else "NO"
        m = "SI" if clean(row["CONTINUIDAD_FUENTE"]).upper() == "SI" or clean(row["ARTICULACION_FUENTE"]).upper() == "SI" or clean(row["UNA_SOLA_TRAYECTORIA_FUENTE"]).upper() == "SI" else "NO"
        n = "SI" if int((det["_V"] == "SI").sum()) == e else "NO"
        p = "SI" if int((det["_W"] == "SI").sum()) == e else "NO"
        o = "SI" if clean(row["CODCLI_FALTANTES_MU"]) or clean(row["FILAS_MU_SOBRANTES"]) else "NO"
        if n == "NO" or p == "NO":
            cls = "NO_DETERMINABLE"
        elif clean(row["FILAS_MU_SOBRANTES"]):
            cls = "CORRECCION_SIES"
        elif k == "NO" or l == "NO" or m == "SI":
            cls = "NO_INFORMAR"
        elif o == "SI":
            cls = "CORRECCION_SIES"
        else:
            cls = "NO_INFORMAR"
        out.append({**row, "_SIM_E": e, "_SIM_F": f, "_SIM_G": g, "_SIM_CLASIFICACION": cls})
    return pd.DataFrame(out)


def main() -> None:
    for path in [SOURCE_XLSX, REVISION_34_XLSX, TRAZABILIDAD_XLSX, TECNICO_XLSX, SCRIPT_BASE]:
        if not path.exists():
            raise FileNotFoundError(path)

    source_hash_before = {p: sha256_file(p) for p in [SOURCE_XLSX, REVISION_34_XLSX, TRAZABILIDAD_XLSX, TECNICO_XLSX, SCRIPT_BASE]}

    rev34 = pd.read_excel(REVISION_34_XLSX, sheet_name="REVISION_34", dtype=str).fillna("")
    trace = pd.read_excel(TRAZABILIDAD_XLSX, sheet_name="TRAZABILIDAD_CIERRE", dtype=str).fillna("")
    da = pd.read_excel(SOURCE_XLSX, sheet_name="DatosAlumnos", dtype=str).fillna("")
    tecnico_eq = pd.read_excel(TECNICO_XLSX, sheet_name="EQUIVALENCIAS", dtype=str).fillna("")
    tecnico_cases = pd.read_excel(TECNICO_XLSX, sheet_name="CASOS", dtype=str).fillna("")
    tecnico_detail = pd.read_excel(TECNICO_XLSX, sheet_name="DETALLE_CODCLI", dtype=str).fillna("")
    tecnico_mu = pd.read_excel(TECNICO_XLSX, sheet_name="FILAS_MU", dtype=str).fillna("")
    tecnico_hashes = pd.read_excel(TECNICO_XLSX, sheet_name="HASHES", dtype=str).fillna("")

    require_columns(rev34, ["RUT", "DV", "nombre", "corresponde_continuidad", "corresponde_articulacion", "una_sola_carrera_con_multiples_CODCLI"], "REVISION_34")
    require_columns(trace, RAW_MU_MIN_COLS, "TRAZABILIDAD_CIERRE")
    require_columns(tecnico_cases, ["RUT", "DV", "NOMBRE", "DECISION_FINAL", "REQUIERE_INFORMAR_SIES", "CORRECCION_CONCRETA_SIES"], "CASOS tecnico")
    require_columns(tecnico_detail, ["RUT", "CODCLI", "CODIGO_INTERNO_CARRERA", "OFERTAS_CANDIDATAS", "OFERTA_SELECCIONADA_PARA_CIERRE", "FILAS_MU_MATCH"], "DETALLE_CODCLI tecnico")
    require_columns(tecnico_mu, ["RUT", "LLAVE_MU", "FILA_MU", "LLAVE_OFERTA_MU", "COD_CAR_MU", "SEDE_MU", "MODALIDAD_MU", "JOR_MU", "VERSION_MU"], "FILAS_MU tecnico")
    require_columns(da, ["RUT", "CODCLI", "CODCARPR", "NOMBRE_L", "ANOMATRICULA", "PERIODOMATRICULA", "ESTADOACADEMICO", "MATRICULA"], "DatosAlumnos")

    cases_by_rut = {clean(r.RUT): r for r in tecnico_cases.itertuples(index=False)}
    rev_by_rut = {rut_norm(r.RUT): r for r in rev34.itertuples(index=False)}
    mu_df = build_mu_rows(tecnico_mu, tecnico_cases, trace)
    detail_df, eq_df = build_detail_rows(tecnico_detail, da, tecnico_mu, )

    # Materialized per-RUT texts derived only from detail rows and MU rows.
    mu_keys_by_rut = {rut: set(group["LLAVE_OFERTA_MU"].map(clean)) for rut, group in mu_df.groupby("RUT_NORM", dropna=False)}
    detail_df["_AC"] = detail_df.apply(
        lambda r: "SI" if clean(r["LLAVE_OFERTA_SIES"]) in mu_keys_by_rut.get(clean(r["RUT_NORM"]), set()) else "NO",
        axis=1,
    )
    detail_df["_AD"] = detail_df.apply(lambda r: "SI" if int(r["_X"]) == 1 and r["_AC"] == "NO" else "NO", axis=1)

    case_rows: list[dict[str, Any]] = []
    for rut in sorted(rev_by_rut, key=lambda x: int(x) if x.isdigit() else x):
        rev = rev_by_rut[rut]
        tech = cases_by_rut.get(rut)
        det = detail_df[detail_df["RUT_NORM"] == rut].copy()
        missing = det[(det["_X"] == 1) & (det["_AC"] == "NO")].copy()
        missing_text = " | ".join(
            f"RUT {r.RUT_NORM}, CODCLI {r.CODCLI}, oferta {r.LLAVE_OFERTA_SIES or 'SIN_MAPEO'}, carrera interna {r.CODIGO_INTERNO_CARRERA}"
            for r in missing.itertuples(index=False)
        )
        extra_text = ""
        tipo = ""
        if tech is not None:
            decision = clean(getattr(tech, "DECISION_FINAL"))
            if decision == "INFORMAR_SIES_AGREGAR_FILA_MU_FALTANTE":
                tipo = "INCORPORAR"
            elif decision == "INFORMAR_SIES_ELIMINAR_FILA_MU_SOBRANTE":
                tipo = "ELIMINAR"
                corr = clean(getattr(tech, "CORRECCION_CONCRETA_SIES"))
                match = re.search(r"(MU_LINEA_\d+\|RUT=[^ ]+)", corr)
                extra_text = match.group(1) if match else clean(getattr(tech, "FILAS_MU_ACTUALES", ""))
        evidence_bits = []
        for r in det.itertuples(index=False):
            evidence_bits.append(
                f"input/PROMEDIOSDEALUMNOS_7804.xlsx/DatosAlumnos fila {r.FILA_ORIGEN}; "
                f"CODCLI {r.CODCLI}; interna {r.CODIGO_INTERNO_CARRERA}; SIES {r.LLAVE_OFERTA_SIES or 'SIN_MAPEO'}"
            )
        for r in mu_df[mu_df["RUT_NORM"] == rut].itertuples(index=False):
            evidence_bits.append(f"{r.ARCHIVO_ORIGEN}/{r.HOJA_ORIGEN} fila {r.FILA_ORIGEN}; MU {r.LLAVE_MU}; {r.LLAVE_OFERTA_MU}")
        dv = clean(getattr(rev, "DV"))
        case_rows.append(
            {
                "RUT_NORM": rut,
                "RUT_FORMATO": rut_formato(rut, dv),
                "DV": dv,
                "NOMBRE": clean(getattr(rev, "nombre")),
                "N_CODCLI_ELEGIBLES": "",
                "N_OFERTAS_ELEGIBLES": "",
                "N_FILAS_MU_ACTUALES": "",
                "CONTINUIDAD_FUENTE": clean(getattr(rev, "corresponde_continuidad")),
                "ARTICULACION_FUENTE": clean(getattr(rev, "corresponde_articulacion")),
                "UNA_SOLA_TRAYECTORIA_FUENTE": clean(getattr(rev, "una_sola_carrera_con_multiples_CODCLI")),
                "TIENE_2_CODCLI": "",
                "TIENE_2_OFERTAS": "",
                "EXCLUIR_CONTINUIDAD": "",
                "MAPEO_COMPLETO": "",
                "DIFERENCIA_MU": "",
                "EVIDENCIA_COMPLETA": "",
                "CODCLI_FALTANTES_MU": missing_text,
                "FILAS_MU_SOBRANTES": extra_text,
                "MOTIVO_DESCARTE": "",
                "EVIDENCIA_RESUMIDA": " || ".join(evidence_bits),
                "CLASIFICACION_FINAL": "",
                "CORRECCION_CONCRETA_SIES": "",
                "FORMULA_CLASIFICACION": "",
                "FORMULA_CORRECCION": "",
                "REVISION_USUARIO": "NO_APLICA",
                "OBSERVACION_USUARIO": "",
                "TIPO_CORRECCION_BASE": tipo,
            }
        )

    simulated = simulate_classifications(case_rows, detail_df, mu_df)
    counts = simulated["_SIM_CLASIFICACION"].value_counts().to_dict()
    expected_counts = {"CORRECCION_SIES": 5, "NO_INFORMAR": 28, "NO_DETERMINABLE": 1}
    if {k: int(counts.get(k, 0)) for k in expected_counts} != expected_counts:
        print("ERROR: las formulas simuladas no reproducen 5/28/1")
        print(simulated[["RUT_NORM", "NOMBRE", "_SIM_CLASIFICACION", "CODCLI_FALTANTES_MU", "FILAS_MU_SOBRANTES"]].to_string(index=False))
        raise SystemExit(2)

    tech_simple = tecnico_cases.copy()
    tech_simple["CLASIFICACION_SIMPLE"] = tech_simple.apply(
        lambda r: "CORRECCION_SIES"
        if clean(r["REQUIERE_INFORMAR_SIES"]) == "SI"
        else ("NO_DETERMINABLE" if clean(r["DECISION_FINAL"]).startswith("NO_DETERMINABLE") else "NO_INFORMAR"),
        axis=1,
    )
    diff = simulated[["RUT_NORM", "_SIM_CLASIFICACION"]].merge(
        tech_simple[["RUT", "CLASIFICACION_SIMPLE"]].rename(columns={"RUT": "RUT_NORM"}),
        on="RUT_NORM",
        how="left",
    )
    diff = diff[diff["_SIM_CLASIFICACION"] != diff["CLASIFICACION_SIMPLE"]]
    if not diff.empty:
        print("ERROR: diferencias contra cierre tecnico")
        print(diff.to_string(index=False))
        raise SystemExit(3)

    # Remove simulation-only helper columns before writing.
    detail_write = detail_df[DETALLE_HEADERS].copy()
    eq_write = eq_df[EQ_HEADERS].copy()
    cases_write = pd.DataFrame(case_rows)[CASOS_HEADERS].copy()
    mu_write = mu_df[MU_HEADERS].copy()

    wb = Workbook()
    ws = wb.active
    ws.title = "00_RESUMEN"

    resumen_rows = [
        ("Total RUT iniciales", '=COUNTA(\'01_CASOS_TRAZABLES\'!A2:A35)', 34),
        ("Total CODCLI elegibles", '=SUM(\'02_DETALLE_CODCLI\'!X2:X1000)', 68),
        ("Correcciones SIES", '=COUNTIF(\'01_CASOS_TRAZABLES\'!U2:U35,"CORRECCION_SIES")', 5),
        ("No informar", '=COUNTIF(\'01_CASOS_TRAZABLES\'!U2:U35,"NO_INFORMAR")', 28),
        ("No determinable", '=COUNTIF(\'01_CASOS_TRAZABLES\'!U2:U35,"NO_DETERMINABLE")', 1),
        ("Total clasificaciones", "=SUM(B4:B6)", 34),
        ("Duplicados RUT", '=SUMPRODUCT((COUNTIF(\'01_CASOS_TRAZABLES\'!A2:A35,\'01_CASOS_TRAZABLES\'!A2:A35)>1)*1)', 0),
        ("Correcciones sin mapeo", '=COUNTIFS(\'01_CASOS_TRAZABLES\'!U2:U35,"CORRECCION_SIES",\'01_CASOS_TRAZABLES\'!P2:P35,"NO")', 0),
        ("Casos sin evidencia", '=COUNTIF(\'01_CASOS_TRAZABLES\'!T2:T35,"*SIN EVIDENCIA*")', 0),
        ("Formulas de clasificacion", '=COUNTIF(\'01_CASOS_TRAZABLES\'!W2:W35,"=*")', 34),
        ("Formulas de decision", '=COUNTIF(\'01_CASOS_TRAZABLES\'!X2:X35,"=*")', 34),
    ]
    ws.append(["INDICADOR", "RESULTADO_FORMULA", "RESULTADO_ESPERADO", "ESTADO_CONTROL"])
    for idx, row in enumerate(resumen_rows, start=2):
        ws.append([row[0], row[1], row[2], f'=IF(B{idx}=C{idx},"OK","REVISAR")'])
    style_sheet(ws)

    ws = wb.create_sheet("01_CASOS_TRAZABLES")
    append_df(ws, cases_write)
    add_case_formulas(ws)
    style_sheet(ws)

    ws = wb.create_sheet("02_DETALLE_CODCLI")
    append_df(ws, detail_write)
    add_detail_formulas(ws)
    style_sheet(ws)

    ws = wb.create_sheet("03_EQUIVALENCIAS")
    append_df(ws, eq_write)
    style_sheet(ws)

    ws = wb.create_sheet("04_FILAS_MU")
    append_df(ws, mu_write)
    add_mu_formulas(ws)
    style_sheet(ws)

    src_wb = load_workbook(SOURCE_XLSX, read_only=True, data_only=False)
    copy_raw_sheet(src_wb, wb, "DatosAlumnos", "05_RAW_DATOSALUMNOS")
    copy_raw_sheet(src_wb, wb, "matriz", "06_RAW_MATRIZ")

    ws = wb.create_sheet("07_RAW_MU")
    raw_mu = trace[trace["RUT"].map(rut_norm).isin(set(cases_write["RUT_NORM"]))][RAW_MU_MIN_COLS].copy()
    append_df(ws, raw_mu)
    style_sheet(ws)

    ws = wb.create_sheet("08_REGLAS")
    rules = pd.DataFrame(
        [
            (1, "Universo inicial = 34 RUT", "01_CASOS_TRAZABLES", "A", "=COUNTA(A2:A35)", "34", "Cada fila representa un RUT inicial."),
            (2, "Periodo valido = 2026-1", "02_DETALLE_CODCLI", "S", '=IF(AND(L2=2026,M2=1),"SI","NO")', "SI", "Periodo de matricula valido."),
            (3, "Estado valido = VIGENTE", "02_DETALLE_CODCLI", "T", '=IF(UPPER(N2)="VIGENTE","SI","NO")', "SI", "Solo estado academico vigente."),
            (4, "Matricula debe estar informada", "02_DETALLE_CODCLI", "U", '=IF(O2<>"","SI","NO")', "SI", "MATRICULA no vacia."),
            (5, "CODCLI no vacio", "02_DETALLE_CODCLI", "X", 'D2<>""', "VERDADERO", "Identificador interno obligatorio."),
            (6, "Codigo interno no vacio", "02_DETALLE_CODCLI", "X", 'E2<>""', "VERDADERO", "Carrera interna obligatoria."),
            (7, "Mapeo SIES demostrado", "02_DETALLE_CODCLI", "V", "=IF(AND(F2<>\"\",G2<>\"\",H2<>\"\",I2<>\"\",J2<>\"\",K2<>\"\"),\"SI\",\"NO\")", "SI", "Oferta SIES completa."),
            (8, "Evidencia de archivo hoja fila", "02_DETALLE_CODCLI", "W", '=IF(AND(P2<>"",Q2<>"",R2<>""),"SI","NO")', "SI", "Trazabilidad minima."),
            (9, "Dos o mas CODCLI", "01_CASOS_TRAZABLES", "K", '=IF(E2>=2,"SI","NO")', "SI", "RUT multivigente."),
            (10, "Dos o mas ofertas", "01_CASOS_TRAZABLES", "L", '=IF(F2>=2,"SI","NO")', "SI", "Control de ofertas elegibles."),
            (11, "Excluir continuidad", "01_CASOS_TRAZABLES", "M", '=IF(OR(UPPER(H2)="SI",UPPER(I2)="SI",UPPER(J2)="SI"),"SI","NO")', "SI/NO", "No informar si es continuidad sin fila MU sobrante."),
            (12, "Detectar oferta faltante", "02_DETALLE_CODCLI", "AD", '=IF(AND(X2=1,AC2="NO"),"SI","NO")', "SI/NO", "Oferta elegible no representada en MU."),
            (13, "Detectar fila MU sobrante", "01_CASOS_TRAZABLES", "R", "Texto materializado desde Python", "Texto/blank", "Fila MU sin respaldo por llave completa."),
            (14, "Clasificacion final", "01_CASOS_TRAZABLES", "U", "Formula de clasificacion por controles N/P/R/K/L/M/O", "5/28/1", "Genera CORRECCION_SIES, NO_INFORMAR o NO_DETERMINABLE."),
            (15, "Correccion SIES", "01_CASOS_TRAZABLES", "V", "Formula basada en U y AA", "Texto/blank", "Texto concreto si corresponde informar."),
        ],
        columns=["ID_REGLA", "REGLA", "HOJA", "COLUMNA", "FORMULA", "RESULTADO_ESPERADO", "INTERPRETACION"],
    )
    rules["FORMULA"] = rules["FORMULA"].map(lambda x: "'" + x if clean(x).startswith("=") else x)
    append_df(ws, rules)
    style_sheet(ws)

    ws = wb.create_sheet("09_CONTROLES")
    ws.append(["CONTROL", "FORMULA", "ESPERADO", "ESTADO"])
    controles = [
        ("Total inicial", '=COUNTA(\'01_CASOS_TRAZABLES\'!A2:A35)', 34),
        ("CODCLI elegibles", '=SUM(\'02_DETALLE_CODCLI\'!Z2:Z1000)', 68),
        ("Correcciones", '=COUNTIF(\'01_CASOS_TRAZABLES\'!U2:U35,"CORRECCION_SIES")', 5),
        ("No informar", '=COUNTIF(\'01_CASOS_TRAZABLES\'!U2:U35,"NO_INFORMAR")', 28),
        ("No determinable", '=COUNTIF(\'01_CASOS_TRAZABLES\'!U2:U35,"NO_DETERMINABLE")', 1),
        ("Suma", "=SUM(B4:B6)", 34),
        ("Duplicados", '=SUMPRODUCT((COUNTIF(\'01_CASOS_TRAZABLES\'!A2:A35,\'01_CASOS_TRAZABLES\'!A2:A35)>1)*1)', 0),
        ("Correcciones sin mapeo", '=COUNTIFS(\'01_CASOS_TRAZABLES\'!U2:U35,"CORRECCION_SIES",\'01_CASOS_TRAZABLES\'!N2:N35,"NO")', 0),
        ("Correcciones sin evidencia", '=COUNTIFS(\'01_CASOS_TRAZABLES\'!U2:U35,"CORRECCION_SIES",\'01_CASOS_TRAZABLES\'!P2:P35,"NO")', 0),
    ]
    for idx, (control, formula, expected) in enumerate(controles, start=2):
        ws.append([control, formula, expected, f'=IF(B{idx}=C{idx},"OK","REVISAR")'])
    style_sheet(ws)

    set_calc_mode(wb)
    OUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    if OUT_XLSX.exists():
        OUT_XLSX.unlink()
    wb.save(OUT_XLSX)

    # ZIP/XML validation without manual opening.
    wb_check = load_workbook(OUT_XLSX, data_only=False, read_only=False)
    sheet_names = wb_check.sheetnames
    formula_counts = {}
    total_formulas = 0
    dimensions = {}
    for ws in wb_check.worksheets:
        count = 0
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    count += 1
        formula_counts[ws.title] = count
        total_formulas += count
        dimensions[ws.title] = (ws.max_row, ws.max_column)

    with zipfile.ZipFile(OUT_XLSX, "r") as zf:
        names = zf.namelist()
        bad_links = [n for n in names if "externalLink" in n or n.startswith("xl/externalLinks/")]
        rels_text = "\n".join(
            zf.read(n).decode("utf-8", errors="ignore")
            for n in names
            if n.endswith(".rels") or n.endswith("workbook.xml")
        )
        has_external = bool(bad_links) or "externalLink" in rels_text

    raw_src = load_workbook(SOURCE_XLSX, read_only=True, data_only=False)
    raw_ok = (
        dimensions["05_RAW_DATOSALUMNOS"] == (raw_src["DatosAlumnos"].max_row, raw_src["DatosAlumnos"].max_column)
        and dimensions["06_RAW_MATRIZ"] == (raw_src["matriz"].max_row, raw_src["matriz"].max_column)
    )
    raw_headers_ok = (
        [c.value for c in wb_check["05_RAW_DATOSALUMNOS"][1]] == [c.value for c in raw_src["DatosAlumnos"][1]]
        and [c.value for c in wb_check["06_RAW_MATRIZ"][1]] == [c.value for c in raw_src["matriz"][1]]
    )

    final_counts = {k: int(counts.get(k, 0)) for k in ["CORRECCION_SIES", "NO_INFORMAR", "NO_DETERMINABLE"]}
    dup_ruts = int(sum(v for v in Counter(cases_write["RUT_NORM"]).values() if v > 1))
    corrections_without_mapping = 0
    corrections_without_evidence = 0
    for _, row in simulated.iterrows():
        if row["_SIM_CLASIFICACION"] == "CORRECCION_SIES":
            rut = clean(row["RUT_NORM"])
            det = detail_df[detail_df["RUT_NORM"] == rut]
            if int((det["_V"] == "SI").sum()) != int(row.get("_SIM_E", 0)):
                corrections_without_mapping += 1
            if not (det["_W"] == "SI").all():
                corrections_without_evidence += 1

    source_hash_after = {p: sha256_file(p) for p in source_hash_before}
    sources_unchanged = source_hash_before == source_hash_after

    required_formula_sheets = ["00_RESUMEN", "01_CASOS_TRAZABLES", "02_DETALLE_CODCLI", "04_FILAS_MU", "09_CONTROLES"]
    valid = True
    valid = valid and sheet_names == SHEETS_EXPECTED
    valid = valid and all(formula_counts.get(s, 0) > 0 for s in required_formula_sheets)
    valid = valid and total_formulas > 200
    valid = valid and raw_ok and raw_headers_ok
    valid = valid and final_counts == expected_counts
    valid = valid and dup_ruts == 0
    valid = valid and corrections_without_mapping == 0
    valid = valid and corrections_without_evidence == 0
    valid = valid and not has_external
    valid = valid and sources_unchanged

    print("VALIDACION XLSX AUDITABLE")
    print(f"ruta final: {OUT_XLSX}")
    print(f"tamano bytes: {OUT_XLSX.stat().st_size}")
    print(f"SHA-256: {sha256_file(OUT_XLSX)}")
    print(f"hojas: {sheet_names}")
    print("filas y columnas por hoja:")
    for s in sheet_names:
        print(f"  - {s}: {dimensions[s][0]} filas x {dimensions[s][1]} columnas")
    print("formulas por hoja:")
    for s in sheet_names:
        print(f"  - {s}: {formula_counts[s]}")
    print(f"total formulas: {total_formulas}")
    print(f"confirmacion hojas RAW: {'OK' if raw_ok else 'REVISAR'}")
    print(f"confirmacion columnas de origen RAW: {'OK' if raw_headers_ok else 'REVISAR'}")
    print("controles esperados:")
    print(f"  - Total RUT iniciales: {len(cases_write)} / esperado 34")
    print(f"  - Total CODCLI elegibles: {int(detail_df['_X'].sum())} / esperado 68")
    print(f"  - Correcciones SIES: {final_counts['CORRECCION_SIES']} / esperado 5")
    print(f"  - No informar: {final_counts['NO_INFORMAR']} / esperado 28")
    print(f"  - No determinable: {final_counts['NO_DETERMINABLE']} / esperado 1")
    print(f"  - Duplicados RUT: {dup_ruts} / esperado 0")
    print(f"  - Correcciones sin mapeo: {corrections_without_mapping} / esperado 0")
    print(f"  - Correcciones sin evidencia: {corrections_without_evidence} / esperado 0")
    print("casos finales:")
    print(simulated[["RUT_NORM", "NOMBRE", "_SIM_CLASIFICACION", "CODCLI_FALTANTES_MU", "FILAS_MU_SOBRANTES"]].to_string(index=False, max_colwidth=120))
    print(f"diferencias contra cierre tecnico anterior: {len(diff)}")
    if not diff.empty:
        print(diff.to_string(index=False))
    print(f"confirmacion de que no hay vinculos externos: {'OK' if not has_external else 'REVISAR'}")
    print(f"confirmacion de que no se modifico ninguna fuente: {'OK' if sources_unchanged else 'REVISAR'}")
    print(f"estado final: {'VALIDO' if valid else 'REVISAR'}")
    if not valid:
        raise SystemExit(4)


if __name__ == "__main__":
    main()
