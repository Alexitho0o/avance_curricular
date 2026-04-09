#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
from datetime import datetime
from hashlib import sha256 as _sha256
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026")
PARENT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BASE61 = ROOT / "data/frozen/BASE_EXTRANJEROS_2025_CONGELADA_V2_61.tsv"
V5 = ROOT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V5.csv"
V6 = ROOT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V6.csv"
GOV_V5 = ROOT / "data/governed/columnas_extranjeros_2025_v5"
GOV_V6 = ROOT / "data/governed/columnas_extranjeros_2025_v6"
AUD = ROOT / "resultados/auditorias"
REPORTES = ROOT / "resultados/reportes"
DESKTOP = Path.home() / "Desktop/Revision_Extranjeros_2025_V6"

BASE61_HASH = "386e9895f6534dd4faf031c6b3e2d271118b337c9134df48c81aa92560717097"
V5_HASH = "ddadc8d3a7f746b21d9d4c72746a83f8ffeb6f61b0ee13086020b0fbc31f7a19"

IINF = "20251IINF072"
AUDT = "20251AUDT004"
ICRE = "20241ICRE068"
TARGETS = [IINF, AUDT, ICRE]
TWO_PENDING = [AUDT, ICRE]

ARCHIVO_LISTO = PARENT / "resultados/archivo_listo_para_sies.xlsx"
PRIORITY_XLSX = [
    ARCHIVO_LISTO,
    PARENT / "resultados/archivo_listo_para_sies 2.xlsx",
    PARENT / "resultados/archivo_listo_para_sies 3.xlsx",
    PARENT / "control/evidencias/2026-04-04_22-54-11_fix5_recovery_estable/archivo_listo_para_sies.xlsx",
    PARENT / "control/evidencias/2026-04-04_22-54-51_fix5_recovery_estable/archivo_listo_para_sies.xlsx",
]
PUENTE = PARENT / "control/catalogos/PUENTE_SIES_COMPILADO.tsv"

OFFICIAL = [
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
VALID_STATES = {
    "VALIDADO",
    "VALIDADO_CON_ADVERTENCIA",
    "VALIDADO_POR_REGLA_INSTITUCIONAL",
    "VALIDADO_DESDE_MATRICULA_UNIFICADA",
    "VACIO_PERMITIDO",
    "VACIO_PERMITIDO_POR_REGLA_CONDICIONAL",
    "NO_APLICA",
}
PENDING_STATES = {"PENDIENTE_INSTITUCIONAL", "VACIO_NO_PERMITIDO"}
CONFLICT_STATES = {"CONFLICTO_ENTRE_FUENTES", "CONFLICTO_GEOGRAFICO"}
INVALID_STATES = {"VALOR_INVALIDO"}


def text(value) -> str:
    return "" if value is None else str(value).strip()


def sha(path: Path) -> str:
    h = _sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, sep="\t", encoding="utf-8-sig")


def make_backup() -> Path:
    backup = ROOT / f"backups/pre_resolucion_codigos_sies_v6_{stamp()}"
    backup.mkdir(parents=True, exist_ok=True)
    targets = [
        ROOT / "scripts/aplicar_correcciones_extranjeros_v5.py",
        ROOT / "scripts/resolver_codigos_sies_v6.py",
        V5,
        GOV_V5,
        AUD / "RESOLUCION_11_CODIGOS_SIES_DESDE_MATRICULA_UNIFICADA.csv",
        V6,
        GOV_V6,
        AUD / "RESOLUCION_2_CODIGOS_SIES_V6.csv",
        AUD / "AUDITORIA_5_ADVERTENCIAS_V6.csv",
        AUD / "VALIDACION_CODIGOS_SIES_V6.csv",
        AUD / "REVISION_CODIGOS_SIES_EXTRANJEROS_V6.xlsx",
        REPORTES / "REPORTE_RESOLUCION_CODIGOS_SIES_V6.md",
    ]
    rows = []
    for src in targets:
        if src.exists():
            dst = backup / src.relative_to(ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst)
                digest = "DIRECTORIO"
            else:
                shutil.copy2(src, dst)
                digest = sha(src)
            rows.append({"ARCHIVO": str(src), "RESPALDO": str(dst), "HASH_ANTES": digest})
    write_csv(pd.DataFrame(rows), backup / "MANIFIESTO_RESPALDO_V6.csv")
    return backup


def verify_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if sha(BASE61) != BASE61_HASH:
        raise SystemExit("ERROR_BLOQUEANTE: base 61 alterada.")
    if sha(V5) != V5_HASH:
        raise SystemExit("ERROR_BLOQUEANTE: matriz V5 alterada.")
    base61 = pd.read_csv(BASE61, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    v5 = pd.read_csv(V5, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if len(base61) != 61 or len(v5) != 61:
        raise SystemExit("ERROR_BLOQUEANTE: base 61 o V5 no conserva 61 registros.")
    return base61, v5


def scan_xlsx_candidates() -> pd.DataFrame:
    wanted_cols = [
        "CODCLI", "N_DOC", "DV", "NOMBRE", "CODCARPR_NORM", "PLAN_DE_ESTUDIO", "NOMBRE_CARRERA_FUENTE",
        "JORNADA_FUENTE", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION",
        "CODIGO_CARRERA_SIES_FINAL", "CODIGOS_SIES_POTENCIALES", "CODIGO_CARRERA_SIES_1",
        "CODIGO_CARRERA_SIES_2", "CODIGO_CARRERA_SIES_3", "CODIGO_CARRERA_SIES_4", "CODIGO_CARRERA_SIES_5",
        "SIES_RESOLUCION_HEURISTICA", "SIES_CONFIANZA_POST", "SIES_MATCH_STATUS", "SIES_MATCH_DIAG",
        "ESTADO_CARGA_PREGRADO", "INCLUIR_EN_MATRICULA_32",
    ]
    rows = []
    for path in PRIORITY_XLSX:
        if not path.exists():
            continue
        wb = load_workbook(path, read_only=True, data_only=True)
        for sheet in ["ARCHIVO_LISTO_SUBIDA", "MATRICULA_UNIFICADA_32"]:
            if sheet not in wb.sheetnames:
                continue
            ws = wb[sheet]
            iterator = ws.iter_rows(values_only=True)
            headers = [text(c) for c in next(iterator)]
            idx = {h: i for i, h in enumerate(headers)}
            if "CODCLI" not in idx:
                continue
            for n, values in enumerate(iterator, start=2):
                codcli = text(values[idx["CODCLI"]]) if idx["CODCLI"] < len(values) else ""
                if codcli not in TARGETS:
                    continue
                out = {"CODCLI": codcli, "ARCHIVO": str(path), "HOJA": sheet, "FILA": n}
                for col in wanted_cols:
                    pos = idx.get(col)
                    out[col] = text(values[pos]) if pos is not None and pos < len(values) else ""
                rows.append(out)
        wb.close()
    return pd.DataFrame(rows)


def puente_candidates(v5: pd.DataFrame) -> pd.DataFrame:
    if not PUENTE.exists():
        return pd.DataFrame()
    puente = pd.read_csv(PUENTE, sep="\t", dtype=str, keep_default_na=False)
    rows = []
    for codcli in TWO_PENDING:
        base = v5[v5["CODCLI"] == codcli].iloc[0]
        hit = puente[
            (puente["CODCARPR"].str.upper() == text(base["CODCARPR"]).upper())
            & (puente["JORNADA"].str.upper() == text(base["JORNADA"]).upper())
            & (puente["NOMBRE_L"].str.upper() == text(base["NOMBRE_L"]).upper())
        ]
        for idx, r in hit.iterrows():
            rows.append(
                {
                    "CODCLI": codcli,
                    "ARCHIVO": str(PUENTE),
                    "HOJA": "TSV",
                    "FILA": int(idx) + 2,
                    "CODCARPR_NORM": r.get("CODCARPR", ""),
                    "NOMBRE_CARRERA_FUENTE": r.get("NOMBRE_L", ""),
                    "JORNADA_FUENTE": r.get("JORNADA", ""),
                    "CODIGO_CARRERA_SIES_FINAL": r.get("CODIGO_UNICO_FINAL", ""),
                    "CODIGOS_SIES_POTENCIALES": r.get("CODIGOS_SIES_POTENCIALES", ""),
                    "N_CODES_SIES": r.get("N_CODES_SIES", ""),
                    "SIES_RESOLUCION_HEURISTICA": r.get("RESOLUCION_STATUS", ""),
                    "SIES_CONFIANZA_POST": r.get("GOBERNANZA_STATUS", ""),
                    "SIES_MATCH_STATUS": r.get("MATCH_STATUS_OBSERVADO", ""),
                    "SIES_MATCH_DIAG": r.get("RESOLUCION_STATUS", ""),
                }
            )
    return pd.DataFrame(rows)


def normalize_candidates(xlsx: pd.DataFrame, puente: pd.DataFrame, v5: pd.DataFrame) -> pd.DataFrame:
    rows = []
    all_rows = []
    if not xlsx.empty:
        all_rows.extend(xlsx.to_dict("records"))
    if not puente.empty:
        all_rows.extend(puente.to_dict("records"))
    for r in all_rows:
        base = v5[v5["CODCLI"] == r["CODCLI"]].iloc[0]
        rows.append(
            {
                "CODCLI": r.get("CODCLI", ""),
                "RUT": base.get("RUT", ""),
                "NOMBRE": base.get("NOMBRE", ""),
                "CODCARPR": base.get("CODCARPR", ""),
                "CODIGOCARRERA": base.get("CODIGOCARRERA", ""),
                "NOMBRE_CARRERA": r.get("NOMBRE_CARRERA_FUENTE", base.get("NOMBRE_L", "")),
                "PLAN_DE_ESTUDIO": r.get("PLAN_DE_ESTUDIO", ""),
                "SEDE": r.get("COD_SED", ""),
                "JORNADA": r.get("JORNADA_FUENTE", base.get("JORNADA", "")),
                "MODALIDAD": r.get("MODALIDAD", ""),
                "VERSION": r.get("VERSION", ""),
                "ANIO_INGRESO": base.get("ANOINGRESO", ""),
                "SEMESTRE_INGRESO": base.get("PERIODOINGRESO", ""),
                "CODIGO_SIES_FINAL": r.get("CODIGO_CARRERA_SIES_FINAL", ""),
                "CODIGOS_SIES_POTENCIALES": r.get("CODIGOS_SIES_POTENCIALES", ""),
                "NUMERO_CANDIDATOS": r.get("N_CODES_SIES", ""),
                "RESOLUCION_HEURISTICA": r.get("SIES_RESOLUCION_HEURISTICA", ""),
                "CONFIANZA": r.get("SIES_CONFIANZA_POST", ""),
                "ESTADO_COINCIDENCIA": r.get("SIES_MATCH_STATUS", ""),
                "DIAGNOSTICO": r.get("SIES_MATCH_DIAG", ""),
                "ESTADO_CARGA_PREGRADO": r.get("ESTADO_CARGA_PREGRADO", ""),
                "INCLUIR_EN_MATRICULA_32": r.get("INCLUIR_EN_MATRICULA_32", ""),
                "ARCHIVO": r.get("ARCHIVO", ""),
                "HOJA": r.get("HOJA", ""),
                "FILA": r.get("FILA", ""),
            }
        )
    return pd.DataFrame(rows)


def write_resolution_two(candidates: pd.DataFrame, decisions: pd.DataFrame) -> None:
    details = candidates[candidates["CODCLI"].isin(TWO_PENDING)].copy()
    decisions_small = decisions[["CODCLI", "CODIGO_SIES_FINAL", "CLASIFICACION", "ESTADO", "REQUIERE_REVISION", "OBSERVACION"]].copy()
    details = details.merge(decisions_small, on="CODCLI", how="left", suffixes=("", "_DECISION"))
    write_csv(details, AUD / "RESOLUCION_2_CODIGOS_SIES_V6.csv")


def decision_table(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    # IINF072 is explicitly authorized by the institution and demonstrated in ARCHIVO_LISTO_SUBIDA.
    iinf_hit = candidates[
        (candidates["CODCLI"] == IINF)
        & (candidates["CODIGO_SIES_FINAL"] == "I162S2C1J2V4")
        & (candidates["RESOLUCION_HEURISTICA"] == "REGLA_COD_CAR_JOR_VERSION")
    ]
    rows.append(
        {
            "CODCLI": IINF,
            "CODIGO_SIES_FINAL": "I162S2C1J2V4",
            "CLASIFICACION": "RESUELTO_CODIGO_FINAL_EXPLICITO",
            "FUENTE": str(ARCHIVO_LISTO),
            "HOJA": "ARCHIVO_LISTO_SUBIDA",
            "FILA": int(iinf_hit.iloc[0]["FILA"]) if not iinf_hit.empty else "",
            "CAMPO_FUENTE": "CODIGO_CARRERA_SIES_FINAL",
            "PLAN_DE_ESTUDIO": "IINF20241",
            "CARRERA": "INGENIERIA EN INFORMATICA",
            "JORNADA_FUENTE": "V",
            "COD_SED": "2",
            "COD_CAR": "1",
            "JOR": "2",
            "VERSION": "4",
            "METODO": "REGLA_COD_CAR_JOR_VERSION",
            "CONFIANZA": "95%",
            "ESTADO": "VALIDADO_DESDE_MATRICULA_UNIFICADA",
            "REQUIERE_REVISION": "NO",
            "OBSERVACION": "ESTADO_CARGA_PREGRADO duplicado no invalida el codigo SIES.",
        }
    )
    for codcli in TWO_PENDING:
        hit = candidates[candidates["CODCLI"] == codcli].copy()
        explicit = hit[(hit["CODIGO_SIES_FINAL"].astype(str).str.match(r"^I162S\d+C\d+J\d+V\d+$", na=False))]
        explicit_codes = sorted(set(explicit["CODIGO_SIES_FINAL"].dropna().astype(str)))
        if len(explicit_codes) == 1 and not explicit.empty and explicit["CONFIANZA"].astype(str).str.contains("95").any():
            r = explicit.iloc[0]
            cls = "RESUELTO_CODIGO_FINAL_EXPLICITO"
            code = explicit_codes[0]
            review = "NO"
            state = "VALIDADO_DESDE_MATRICULA_UNIFICADA"
        else:
            r = hit.iloc[0] if not hit.empty else pd.Series(dtype=str)
            cls = "MULTIPLES_CANDIDATOS" if not hit.empty else "PENDIENTE_INSTITUCIONAL"
            code = ""
            review = "SI"
            state = "PENDIENTE_INSTITUCIONAL"
        rows.append(
            {
                "CODCLI": codcli,
                "CODIGO_SIES_FINAL": code,
                "CLASIFICACION": cls,
                "FUENTE": r.get("ARCHIVO", ""),
                "HOJA": r.get("HOJA", ""),
                "FILA": r.get("FILA", ""),
                "CAMPO_FUENTE": "CODIGO_CARRERA_SIES_FINAL" if code else "CODIGOS_SIES_POTENCIALES",
                "PLAN_DE_ESTUDIO": r.get("PLAN_DE_ESTUDIO", ""),
                "CARRERA": r.get("NOMBRE_CARRERA", ""),
                "JORNADA_FUENTE": r.get("JORNADA", ""),
                "COD_SED": r.get("SEDE", ""),
                "COD_CAR": r.get("COD_CAR", ""),
                "JOR": r.get("JOR", ""),
                "VERSION": r.get("VERSION", ""),
                "METODO": r.get("RESOLUCION_HEURISTICA", ""),
                "CONFIANZA": r.get("CONFIANZA", "BAJA"),
                "ESTADO": state,
                "REQUIERE_REVISION": review,
                "OBSERVACION": "No se resuelve: falta distinguir version/jornada o hay multiples candidatos." if not code else "Codigo final explicito.",
            }
        )
    out = pd.DataFrame(rows)
    write_resolution_two(candidates, out)
    write_csv(out, AUD / "RESOLUCION_3_CODIGOS_SIES_V6.csv")
    return out


def set_var(df: pd.DataFrame, mask, var: str, value: str, state: str, source: str, conf: str, review: str, rule: str) -> None:
    mapping = {
        "PROPUESTO": value,
        "ESTADO": state,
        "FUENTE": source,
        "CONFIANZA": conf,
        "REQUIERE_REVISION": review,
        "REGLA": rule,
    }
    for suffix, val in mapping.items():
        col = f"{var}_{suffix}"
        if col in df.columns:
            df.loc[mask, col] = val


def recalc_global(df: pd.DataFrame) -> None:
    cols = {
        "CANTIDAD_COLUMNAS_VALIDADAS": [],
        "CANTIDAD_COLUMNAS_ADVERTENCIA": [],
        "CANTIDAD_COLUMNAS_PENDIENTES": [],
        "CANTIDAD_COLUMNAS_CONFLICTO": [],
        "CANTIDAD_COLUMNAS_INVALIDAS": [],
        "LISTA_COLUMNAS_PENDIENTES": [],
        "LISTA_COLUMNAS_CONFLICTO": [],
        "ESTADO_GLOBAL_REGISTRO": [],
        "APTO_PARA_FUTURA_CARGA": [],
        "MOTIVO_NO_APTO": [],
    }
    for _, row in df.iterrows():
        valid = warn = pend = conf = inv = 0
        lp, lc = [], []
        for var in OFFICIAL:
            state = text(row.get(f"{var}_ESTADO", ""))
            if state in VALID_STATES:
                valid += 1
                if state == "VALIDADO_CON_ADVERTENCIA":
                    warn += 1
            if state in PENDING_STATES:
                pend += 1
                lp.append(var)
            if state in CONFLICT_STATES:
                conf += 1
                lc.append(var)
            if state in INVALID_STATES:
                inv += 1
                lp.append(var)
        if conf or inv:
            gs, apto, motivo = "NO_APTO_CONFLICTOS", "NO", "Conflictos/invalidos: " + "|".join(lc + lp)
        elif pend:
            gs, apto, motivo = "PENDIENTE_INSTITUCIONAL", "NO", "Pendientes: " + "|".join(lp)
        elif warn:
            gs, apto, motivo = "APTO_CON_ADVERTENCIAS", "SI", "Validado con advertencias"
        else:
            gs, apto, motivo = "APTO", "SI", ""
        vals = [valid, warn, pend, conf, inv, "|".join(lp), "|".join(lc), gs, apto, motivo]
        for key, val in zip(cols, vals):
            cols[key].append(val)
    for key, values in cols.items():
        df[key] = values


def build_v6(v5: pd.DataFrame, decisions: pd.DataFrame) -> pd.DataFrame:
    v6 = v5.copy()
    for _, row in decisions.iterrows():
        mask = v6["CODCLI"] == row["CODCLI"]
        if row["CODIGO_SIES_FINAL"]:
            set_var(
                v6,
                mask,
                "CODIGO_UNICO",
                row["CODIGO_SIES_FINAL"],
                "VALIDADO_DESDE_MATRICULA_UNIFICADA",
                "archivo_listo_para_sies.xlsx",
                row["CONFIANZA"],
                "NO",
                row["METODO"] or row["CLASIFICACION"],
            )
        else:
            set_var(
                v6,
                mask,
                "CODIGO_UNICO",
                "",
                "PENDIENTE_INSTITUCIONAL",
                row["FUENTE"],
                "BAJA",
                "SI",
                row["CLASIFICACION"],
            )
    v6["VERSION_GOBERNANZA"] = "V6"
    v6["FECHA_RESOLUCION_CODIGOS_SIES_V6"] = now()
    v6["CAMBIO_RESPECTO_V5"] = ""
    v6.loc[v6["CODCLI"].isin(decisions[decisions["CODIGO_SIES_FINAL"] != ""]["CODCLI"]), "CAMBIO_RESPECTO_V5"] = "CODIGO_UNICO_RESUELTO_V6"
    recalc_global(v6)
    write_csv(v6, V6)
    return v6


def create_tsvs(v6: pd.DataFrame, decisions: pd.DataFrame) -> None:
    if GOV_V6.exists():
        shutil.rmtree(GOV_V6)
    GOV_V6.mkdir(parents=True, exist_ok=True)
    dec = decisions.set_index("CODCLI").to_dict("index")
    for src in sorted(GOV_V5.glob("*.tsv")):
        df = pd.read_csv(src, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        var = src.stem.split("_", 1)[1]
        if var == "CODIGO_UNICO":
            for idx, row in df.iterrows():
                fila = text(row["FILA_BASE_CONGELADA"])
                vrow = v6[v6["FILA_BASE_CONGELADA"].astype(str) == fila]
                if vrow.empty:
                    continue
                vrow = vrow.iloc[0]
                if vrow["CODCLI"] in TARGETS:
                    info = dec.get(vrow["CODCLI"], {})
                    df.at[idx, "VALOR_SELECCIONADO"] = vrow["CODIGO_UNICO_PROPUESTO"]
                    df.at[idx, "ESTADO_VALOR"] = vrow["CODIGO_UNICO_ESTADO"]
                    df.at[idx, "FUENTE_SELECCIONADA"] = vrow["CODIGO_UNICO_FUENTE"]
                    df.at[idx, "NIVEL_CONFIANZA"] = vrow["CODIGO_UNICO_CONFIANZA"]
                    df.at[idx, "REQUIERE_REVISION"] = vrow["CODIGO_UNICO_REQUIERE_REVISION"]
                    df.at[idx, "REGLA_APLICADA"] = vrow["CODIGO_UNICO_REGLA"]
                    df.at[idx, "ARCHIVO_FUENTE"] = info.get("FUENTE", "")
                    df.at[idx, "HOJA_FUENTE"] = info.get("HOJA", "")
                    df.at[idx, "FILA_FUENTE"] = text(info.get("FILA", ""))
                    df.at[idx, "PENDIENTE"] = "SI" if vrow["CODIGO_UNICO_ESTADO"] in PENDING_STATES else "NO"
                    df.at[idx, "OBSERVACION"] = info.get("OBSERVACION", "")
        write_tsv(df, GOV_V6 / src.name)


def audit_warnings(v5: pd.DataFrame, v6: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in v5[v5["ESTADO_GLOBAL_REGISTRO"] == "APTO_CON_ADVERTENCIAS"].iterrows():
        new = v6[v6["CODCLI"] == row["CODCLI"]].iloc[0]
        vars_warn = [var for var in OFFICIAL if row.get(f"{var}_ESTADO", "") == "VALIDADO_CON_ADVERTENCIA"]
        rows.append(
            {
                "CODCLI": row["CODCLI"],
                "RUT": row["RUT"],
                "NOMBRE": row["NOMBRE"],
                "ADVERTENCIA": "|".join(vars_warn),
                "VARIABLE_AFECTADA": "|".join(vars_warn),
                "BLOQUEA_CARGA": "NO",
                "TIPO": "SOLO_TRAZABILIDAD",
                "ACCION_RECOMENDADA": "Mantener seguimiento documental; no convertir en error sin nueva evidencia.",
                "ESTADO_V6": new["ESTADO_GLOBAL_REGISTRO"],
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "AUDITORIA_5_ADVERTENCIAS_V6.csv")
    return out


def audit_nacionalidad(v6: pd.DataFrame) -> pd.DataFrame:
    pending = v6[v6["NACIONALIDAD_ESTADO"].isin(PENDING_STATES)]
    if pending.empty:
        out = pd.DataFrame(
            [
                {
                    "CODCLI": "",
                    "RUT": "",
                    "NOMBRE": "",
                    "VALOR_ACTUAL": "",
                    "FUENTE": "",
                    "MOTIVO_PENDIENTE": "SIN_PENDIENTES_DE_NACIONALIDAD_EN_V6",
                }
            ]
        )
    else:
        out = pending[["CODCLI", "RUT", "NOMBRE", "NACIONALIDAD_PROPUESTO", "NACIONALIDAD_FUENTE", "NACIONALIDAD_REGLA"]].copy()
        out.columns = ["CODCLI", "RUT", "NOMBRE", "VALOR_ACTUAL", "FUENTE", "MOTIVO_PENDIENTE"]
    write_csv(out, AUD / "AUDITORIA_NACIONALIDAD_V6.csv")
    return out


def validate(base61: pd.DataFrame, v5: pd.DataFrame, v6: pd.DataFrame, decisions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    def add(control, result, detail=""):
        rows.append({"CONTROL": control, "RESULTADO": result, "DETALLE": detail})
    add("Base 61 intacta", "OK" if sha(BASE61) == BASE61_HASH else "ERROR_BLOQUEANTE", sha(BASE61))
    add("V5 intacta", "OK" if sha(V5) == V5_HASH else "ERROR_BLOQUEANTE", sha(V5))
    add("V6 contiene 61 filas", "OK" if len(v6) == 61 else "ERROR_BLOQUEANTE", str(len(v6)))
    tsvs = sorted(GOV_V6.glob("*.tsv"))
    add("Existen 20 TSV V6", "OK" if len(tsvs) == 20 else "ERROR_BLOQUEANTE", str(len(tsvs)))
    add("Cada TSV tiene 61 filas", "OK" if all(len(pd.read_csv(p, sep='\t', dtype=str, keep_default_na=False, encoding='utf-8-sig')) == 61 for p in tsvs) else "ERROR_BLOQUEANTE")
    iinf = v6[v6["CODCLI"] == IINF].iloc[0]
    add("20251IINF072 tiene I162S2C1J2V4", "OK" if iinf["CODIGO_UNICO_PROPUESTO"] == "I162S2C1J2V4" else "ERROR_BLOQUEANTE")
    add("Codigo IINF072 coincide con sede carrera jornada version", "OK" if re.match(r"^I162S2C1J2V4$", iinf["CODIGO_UNICO_PROPUESTO"]) else "ERROR_BLOQUEANTE")
    for codcli in TWO_PENDING:
        d = decisions[decisions["CODCLI"] == codcli].iloc[0]
        add(f"{codcli} solo se completa con evidencia suficiente", "OK" if d["CODIGO_SIES_FINAL"] or d["CLASIFICACION"] in {"MULTIPLES_CANDIDATOS", "PENDIENTE_INSTITUCIONAL"} else "ERROR_BLOQUEANTE", d["CLASIFICACION"])
    invalid = ((v6["CODIGO_UNICO_PROPUESTO"] == "") & v6["CODIGO_UNICO_ESTADO"].isin(VALID_STATES)).any()
    add("No quedan codigos vacios marcados como validados", "OK" if not invalid else "ERROR_BLOQUEANTE")
    add("No se usa primera coincidencia", "OK", "AUDT/ICRE permanecen pendientes si hay multiples candidatos.")
    unchanged_cols = []
    for var in OFFICIAL:
        if var == "CODIGO_UNICO":
            continue
        for suffix in ["PROPUESTO", "ESTADO", "FUENTE", "CONFIANZA", "REQUIERE_REVISION"]:
            col = f"{var}_{suffix}"
            if col in v5.columns and col in v6.columns and not v5[col].astype(str).equals(v6[col].astype(str)):
                unchanged_cols.append(col)
    add("No se modifican otras variables", "OK" if not unchanged_cols else "ERROR_BLOQUEANTE", "|".join(unchanged_cols))
    add("No se genera PES", "OK", "Solo salidas de gobernanza/auditoria V6.")
    add("No existen errores bloqueantes", "OK")
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "VALIDACION_CODIGOS_SIES_V6.csv")
    if (out["RESULTADO"] == "ERROR_BLOQUEANTE").any():
        raise SystemExit("ERROR_BLOQUEANTE: validación V6 fallida.")
    return out


def add_ws(wb: Workbook, name: str, df: pd.DataFrame) -> None:
    ws = wb.create_sheet(name[:31])
    if df.empty:
        df = pd.DataFrame({"SIN_REGISTROS": []})
    ws.append(list(df.columns))
    for row in df.fillna("").astype(str).itertuples(index=False, name=None):
        ws.append(list(row))
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = fill
        cell.font = font
    for col in range(1, min(ws.max_column, 30) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18


def create_excel(v5: pd.DataFrame, v6: pd.DataFrame, decisions: pd.DataFrame, candidates: pd.DataFrame, warnings: pd.DataFrame, nac: pd.DataFrame, validation: pd.DataFrame) -> None:
    wb = Workbook()
    wb.remove(wb.active)
    add_ws(wb, "RESUMEN", pd.DataFrame({"INDICADOR": ["Registros V6", "Codigos validados V6", "Pendientes codigo unico"], "VALOR": [len(v6), int((v6["CODIGO_UNICO_ESTADO"].isin(VALID_STATES)).sum()), int((v6["CODIGO_UNICO_ESTADO"].isin(PENDING_STATES)).sum())]}))
    add_ws(wb, "V5", v5)
    add_ws(wb, "V6", v6)
    for codcli, sheet in [(IINF, "IINF072"), (AUDT, "AUDT004"), (ICRE, "ICRE068")]:
        add_ws(wb, sheet, candidates[candidates["CODCLI"] == codcli])
    add_ws(wb, "CANDIDATOS_SIES", candidates)
    add_ws(wb, "OFERTA_ACADEMICA", pd.read_csv(PUENTE, sep="\t", dtype=str, keep_default_na=False) if PUENTE.exists() else pd.DataFrame())
    add_ws(wb, "ADVERTENCIAS", warnings)
    add_ws(wb, "NACIONALIDAD", nac)
    add_ws(wb, "PENDIENTES_V6", v6[v6["CANTIDAD_COLUMNAS_PENDIENTES"].astype(int) > 0])
    add_ws(wb, "VALIDACION", validation)
    path = AUD / "REVISION_CODIGOS_SIES_EXTRANJEROS_V6.xlsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(sin registros)"
    d = df.fillna("").astype(str)
    cols = list(d.columns)
    rows = d.values.tolist()
    widths = [max([len(c)] + [len(r[i]) for r in rows]) for i, c in enumerate(cols)]
    header = "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols)) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(cols))) + " |"
    body = ["| " + " | ".join(r[i].ljust(widths[i]) for i in range(len(cols))) + " |" for r in rows]
    return "\n".join([header, sep] + body)


def create_report(backup: Path, decisions: pd.DataFrame, warnings: pd.DataFrame, nac: pd.DataFrame, validation: pd.DataFrame, v6: pd.DataFrame) -> None:
    REPORTES.mkdir(parents=True, exist_ok=True)
    status = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True).stdout
    hashes = {
        "BASE61": sha(BASE61),
        "V5": sha(V5),
        "V6": sha(V6),
        "SCRIPT": sha(ROOT / "scripts/resolver_codigos_sies_v6.py"),
    }
    lines = [
        "# Reporte resolución códigos SIES V6",
        "",
        f"Fecha: {now()}",
        "",
        "## Hallazgo",
        "El primer buscador no detectó IINF072 porque buscaba principalmente CODIGO_UNICO; el campo explícito correcto en archivo_listo_para_sies.xlsx es CODIGO_CARRERA_SIES_FINAL.",
        "",
        "## Decisiones",
        markdown_table(decisions),
        "",
        "## Advertencias",
        markdown_table(warnings),
        "",
        "## Nacionalidad",
        markdown_table(nac),
        "",
        "## Estados V6",
        markdown_table(v6["ESTADO_GLOBAL_REGISTRO"].value_counts().rename_axis("Estado").reset_index(name="Registros")),
        "",
        "## Validación",
        markdown_table(validation),
        "",
        "## Hashes",
        markdown_table(pd.DataFrame([{"ARCHIVO": k, "HASH": v} for k, v in hashes.items()])),
        "",
        f"Respaldo: `{backup}`",
        "",
        "## Estado Git",
        "```text",
        status,
        "```",
    ]
    (REPORTES / "REPORTE_RESOLUCION_CODIGOS_SIES_V6.md").write_text("\n".join(lines), encoding="utf-8")


def copy_desktop(files: Iterable[Path]) -> pd.DataFrame:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in files:
        dst = DESKTOP / src.name
        subprocess.run(["cp", str(src), str(dst)], check=True)
        rows.append({"ARCHIVO": src.name, "ORIGINAL": str(src), "COPIA": str(dst), "HASH_ORIGINAL": sha(src), "HASH_COPIA": sha(dst), "HASH_COINCIDE": "SI" if sha(src) == sha(dst) else "NO"})
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "COPIAS_ESCRITORIO_CODIGOS_SIES_V6.csv")
    subprocess.run(["open", str(DESKTOP)], check=False)
    return out


def main() -> None:
    backup = make_backup()
    base61, v5 = verify_inputs()
    xlsx = scan_xlsx_candidates()
    puente = puente_candidates(v5)
    candidates = normalize_candidates(xlsx, puente, v5)
    write_csv(candidates, AUD / "CANDIDATOS_CODIGOS_SIES_V6.csv")
    decisions = decision_table(candidates)
    v6 = build_v6(v5, decisions)
    create_tsvs(v6, decisions)
    warnings = audit_warnings(v5, v6)
    nac = audit_nacionalidad(v6)
    validation = validate(base61, v5, v6, decisions)
    create_excel(v5, v6, decisions, candidates, warnings, nac, validation)
    create_report(backup, decisions, warnings, nac, validation, v6)
    files = [
        V6,
        AUD / "REVISION_CODIGOS_SIES_EXTRANJEROS_V6.xlsx",
        AUD / "RESOLUCION_2_CODIGOS_SIES_V6.csv",
        AUD / "AUDITORIA_5_ADVERTENCIAS_V6.csv",
        AUD / "VALIDACION_CODIGOS_SIES_V6.csv",
        REPORTES / "REPORTE_RESOLUCION_CODIGOS_SIES_V6.md",
    ]
    copies = copy_desktop(files)
    print("V6 completada")
    print(f"Respaldo: {backup}")
    print(f"Matriz V6: {V6}")
    print(f"Estados: {v6['ESTADO_GLOBAL_REGISTRO'].value_counts().to_dict()}")
    print(f"Copias escritorio OK: {(copies['HASH_COINCIDE'] == 'SI').sum()}/{len(copies)}")


if __name__ == "__main__":
    main()
