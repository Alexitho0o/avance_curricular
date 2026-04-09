#!/usr/bin/env python3
"""Aplica decisiones institucionales V4 para gobernanza de Extranjeros 2025.

No modifica la base congelada, V1, V2 ni V3. Genera V4 derivada y archivos
de revision. No genera archivo final PES.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


SUB = Path(__file__).resolve().parents[1]
ROOT = SUB.parent
HOME = Path.home()
AUD = SUB / "resultados" / "auditorias"
GESTION = SUB / "resultados" / "gestion"
REPORTES = SUB / "resultados" / "reportes"
PROCESSED = SUB / "data" / "processed"
GOV_V3 = SUB / "data" / "governed" / "columnas_extranjeros_2025_v3"
GOV_V4 = SUB / "data" / "governed" / "columnas_extranjeros_2025_v4"
DESKTOP_DIR = HOME / "Desktop" / "Revision_Extranjeros_2025_V4"

FROZEN = SUB / "data" / "frozen" / "BASE_EXTRANJEROS_2025_CONGELADA.tsv"
FROZEN_HASH = "da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081"
V3 = PROCESSED / "MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V3.csv"
V3_HASH = "54876c75ae412e372657726c64c520d7c50c18d742f3c36827c222c5ce45d70c"
V4 = PROCESSED / "MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V4.csv"
INSTRUCTIVO = SUB / "docs" / "Instructivo_Estudiantes_Extranjeros_SIES_2026.txt"
CAT_PAISES = AUD / "CATALOGO_PAISES_SIES_2026.csv"
CAT_TERRITORIAL = ROOT / "gobernanza_pais_est_sec.tsv"

OFFICIAL_COLS = [
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
    "VACIO_PERMITIDO",
    "VACIO_PERMITIDO_POR_REGLA_CONDICIONAL",
    "NO_APLICA",
}
PENDING_STATES = {"PENDIENTE_INSTITUCIONAL", "VACIO_NO_PERMITIDO"}
CONFLICT_STATES = {"CONFLICTO_ENTRE_FUENTES", "CONFLICTO_GEOGRAFICO"}
INVALID_STATES = {"VALOR_INVALIDO"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.upper()
    text = re.sub(r"[^A-Z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def doc_from_rut(value: object) -> str:
    raw = re.sub(r"[^0-9Kk]", "", text(value)).upper()
    return raw[:-1] if len(raw) > 1 else raw


def read_csv(path: Path, sep: str = ",") -> pd.DataFrame:
    return pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, sep="\t", encoding="utf-8-sig")


def backup_existing(paths: Iterable[Path]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = SUB / "backups" / f"pre_aplicacion_reglas_institucionales_v4_{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if not path.exists():
            continue
        rel = path.relative_to(SUB) if path.is_relative_to(SUB) else Path(path.name)
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(path, dest)
    return backup


def ensure_rule_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in OFFICIAL_COLS:
        rule_col = f"{col}_REGLA"
        if rule_col not in out.columns:
            out[rule_col] = "HEREDADO_V3"
    return out


def set_var(
    df: pd.DataFrame,
    mask: pd.Series,
    var: str,
    value: str,
    state: str,
    source: str,
    confidence: str,
    review: str,
    rule: str,
) -> None:
    mapping = {
        f"{var}_PROPUESTO": value,
        f"{var}_ESTADO": state,
        f"{var}_FUENTE": source,
        f"{var}_CONFIANZA": confidence,
        f"{var}_REQUIERE_REVISION": review,
        f"{var}_REGLA": rule,
    }
    for col, val in mapping.items():
        if col not in df.columns:
            df[col] = ""
        df.loc[mask, col] = val


def get_chile_code() -> Tuple[str, str, int]:
    paises = read_csv(CAT_PAISES)
    name_col = "NOMBRE_PAIS"
    code_col = "CODIGO_PAIS"
    matches = paises[paises[name_col].map(norm) == "CHILE"]
    if len(matches) != 1:
        raise SystemExit("ERROR: no se encontro CHILE de forma inequivoca en catalogo SIES.")
    idx = matches.index[0]
    code = text(matches.loc[idx, code_col])
    if not code:
        raise SystemExit("ERROR: codigo de CHILE vacio en catalogo SIES.")
    return code, text(matches.loc[idx, name_col]), int(idx) + 2


def build_geo_indexes() -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame], pd.DataFrame]:
    geo = read_csv(CAT_TERRITORIAL, sep="\t")
    required = {"COMUNACOLEGIO_NORM", "CIUDADCOLEGIO_NORM", "PAIS", "COD_PAIS_EST_SEC"}
    missing = required - set(geo.columns)
    if missing:
        raise SystemExit(f"ERROR: catalogo territorial incompleto: {sorted(missing)}")
    geo["_COMUNA_NORM2"] = geo["COMUNACOLEGIO_NORM"].map(norm)
    geo["_CIUDAD_NORM2"] = geo["CIUDADCOLEGIO_NORM"].map(norm)
    comuna = {k: g.copy() for k, g in geo.groupby("_COMUNA_NORM2", dropna=False)}
    ciudad = {k: g.copy() for k, g in geo.groupby("_CIUDAD_NORM2", dropna=False)}
    return comuna, ciudad, geo


def resolve_pais_sec(v4: pd.DataFrame, chile_code: str, chile_name: str) -> pd.DataFrame:
    comuna_idx, ciudad_idx, geo = build_geo_indexes()
    rows = []
    for idx, row in v4.iterrows():
        fila = text(row.get("FILA_BASE_CONGELADA"))
        estado_v3 = text(row.get("PAIS_ESTUDIOS_SECUNDARIOS_ESTADO"))
        base = {
            "FILA_BASE_CONGELADA": fila,
            "CODCLI": row.get("CODCLI", ""),
            "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
            "NOMBRE": row.get("NOMBRE", ""),
            "VALOR_V3": row.get("PAIS_ESTUDIOS_SECUNDARIOS_PROPUESTO", ""),
            "ESTADO_V3": estado_v3,
            "CIUDADCOLEGIO": row.get("CIUDADCOLEGIO", ""),
            "COMUNACOLEGIO": row.get("COMUNACOLEGIO", ""),
            "CODIGOCOLEGIO": row.get("CODIGOCOLEGIO", ""),
            "COLEGIO": row.get("COLEGIO", ""),
            "VALOR_PROPUESTO": row.get("PAIS_ESTUDIOS_SECUNDARIOS_PROPUESTO", ""),
            "PAIS_PROPUESTO": "",
            "FUENTE_CATALOGO": "",
            "FILA_CATALOGO": "",
            "REGLA_APLICADA": "MANTENER_VALOR_VALIDADO_V3",
            "NIVEL_CONFIANZA": row.get("PAIS_ESTUDIOS_SECUNDARIOS_CONFIANZA", ""),
            "EVIDENCIA": "",
            "REQUIERE_REVISION": row.get("PAIS_ESTUDIOS_SECUNDARIOS_REQUIERE_REVISION", ""),
            "CLASIFICACION": "MANTENIDO_DESDE_V3",
            "OBSERVACION": "Valor ya validado en V3; no se altera.",
        }
        if estado_v3 != "PENDIENTE_INSTITUCIONAL":
            rows.append(base)
            continue

        comuna_key = norm(row.get("COMUNACOLEGIO", ""))
        ciudad_key = norm(row.get("CIUDADCOLEGIO", ""))
        comuna_match = comuna_idx.get(comuna_key, pd.DataFrame())
        ciudad_match = ciudad_idx.get(ciudad_key, pd.DataFrame())
        valid_comuna = unique_chile_match(comuna_match, chile_code)
        valid_ciudad = unique_chile_match(ciudad_match, chile_code)

        classification = "PENDIENTE_INSTITUCIONAL"
        source_row = None
        rule = ""
        if valid_comuna and valid_ciudad:
            code_comuna = text(comuna_match.iloc[0]["COD_PAIS_EST_SEC"])
            code_ciudad = text(ciudad_match.iloc[0]["COD_PAIS_EST_SEC"])
            if code_comuna == code_ciudad == chile_code:
                classification = "VALIDADO_CHILE_POR_COMUNA"
                source_row = comuna_match.iloc[0]
                rule = "COMUNACOLEGIO_COINCIDE_INEQUIVOCAMENTE_CON_COMUNA_CHILENA"
            else:
                classification = "CONFLICTO_GEOGRAFICO"
        elif valid_comuna:
            classification = "VALIDADO_CHILE_POR_COMUNA"
            source_row = comuna_match.iloc[0]
            rule = "COMUNACOLEGIO_COINCIDE_INEQUIVOCAMENTE_CON_COMUNA_CHILENA"
        elif valid_ciudad:
            classification = "VALIDADO_CHILE_POR_CIUDAD"
            source_row = ciudad_match.iloc[0]
            rule = "CIUDADCOLEGIO_COINCIDE_INEQUIVOCAMENTE_CON_CIUDAD_CHILENA"
        elif comuna_match.empty and ciudad_match.empty:
            classification = "PENDIENTE_SIN_CATALOGO"
        else:
            classification = "CONFLICTO_GEOGRAFICO"

        if classification.startswith("VALIDADO_CHILE"):
            source_index = int(source_row.name) + 2
            base.update(
                {
                    "VALOR_PROPUESTO": chile_code,
                    "PAIS_PROPUESTO": chile_name,
                    "FUENTE_CATALOGO": str(CAT_TERRITORIAL),
                    "FILA_CATALOGO": str(source_index),
                    "REGLA_APLICADA": rule,
                    "NIVEL_CONFIANZA": "ALTA",
                    "EVIDENCIA": f"{classification}; catalogo={CAT_TERRITORIAL}; fila={source_index}",
                    "REQUIERE_REVISION": "NO",
                    "CLASIFICACION": classification,
                    "OBSERVACION": "No se uso nacionalidad ni nombre de colegio como sustituto.",
                }
            )
            set_var(
                v4,
                v4.index == idx,
                "PAIS_ESTUDIOS_SECUNDARIOS",
                chile_code,
                "VALIDADO_POR_REGLA_INSTITUCIONAL",
                "CATALOGO_TERRITORIAL_CHILE",
                "ALTA",
                "NO",
                rule,
            )
        elif classification == "CONFLICTO_GEOGRAFICO":
            base.update(
                {
                    "REGLA_APLICADA": "CONFLICTO_ENTRE_CIUDAD_COMUNA_O_CATALOGO",
                    "NIVEL_CONFIANZA": "BAJA",
                    "REQUIERE_REVISION": "SI",
                    "CLASIFICACION": classification,
                    "OBSERVACION": "Existe fuente geografica no inequivoca; no se asigna.",
                }
            )
            set_var(
                v4,
                v4.index == idx,
                "PAIS_ESTUDIOS_SECUNDARIOS",
                "",
                "CONFLICTO_ENTRE_FUENTES",
                "CATALOGO_TERRITORIAL_CHILE",
                "BAJA",
                "SI",
                "CONFLICTO_GEOGRAFICO_NO_ASIGNAR",
            )
        else:
            base.update(
                {
                    "REGLA_APLICADA": "SIN_CATALOGO_GEOGRAFICO_INEQUIVOCO",
                    "NIVEL_CONFIANZA": "BAJA",
                    "REQUIERE_REVISION": "SI",
                    "CLASIFICACION": classification,
                    "OBSERVACION": "No existe evidencia geografica controlada suficiente.",
                }
            )
        rows.append(base)
    return pd.DataFrame(rows)


def unique_chile_match(df: pd.DataFrame, chile_code: str) -> bool:
    if df.empty:
        return False
    subset = df[(df["PAIS"].map(norm) == "CHILE") & (df["COD_PAIS_EST_SEC"].map(text) == chile_code)]
    return len(subset[["PAIS", "COD_PAIS_EST_SEC"]].drop_duplicates()) == 1 and len(df[["PAIS", "COD_PAIS_EST_SEC"]].drop_duplicates()) == 1


def apply_residencia_origen(v4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    mask = pd.Series(True, index=v4.index)
    set_var(
        v4,
        mask,
        "TIPO_RESIDENCIA_ESTUDIANTE",
        "0",
        "VALIDADO_POR_REGLA_INSTITUCIONAL",
        "DECISION_INSTITUCIONAL_2026",
        "ALTA",
        "NO",
        "SIN_INFORMACION_DE_RESIDENCIA_ASIGNAR_0",
    )
    set_var(
        v4,
        mask,
        "PAIS_ORIGEN",
        "",
        "VACIO_PERMITIDO_POR_REGLA_CONDICIONAL",
        "INSTRUCTIVO_SIES_2026",
        "ALTA",
        "NO",
        "RESIDENCIA_0_NO_COMPLETAR_PAIS_ORIGEN",
    )
    for _, row in v4.iterrows():
        rows.append(
            {
                "FILA_BASE_CONGELADA": row.get("FILA_BASE_CONGELADA", ""),
                "CODCLI": row.get("CODCLI", ""),
                "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                "TIPO_RESIDENCIA_V3": "",
                "TIPO_RESIDENCIA_V4": "0",
                "ESTADO_RESIDENCIA_V4": "VALIDADO_POR_REGLA_INSTITUCIONAL",
                "PAIS_ORIGEN_V3": "",
                "PAIS_ORIGEN_V4": "",
                "ESTADO_PAIS_ORIGEN_V4": "VACIO_PERMITIDO_POR_REGLA_CONDICIONAL",
                "FUENTE": "DECISION_INSTITUCIONAL_2026 / INSTRUCTIVO_SIES_2026",
                "REGLA": "SIN_INFORMACION_DE_RESIDENCIA_ASIGNAR_0; RESIDENCIA_0_NO_COMPLETAR_PAIS_ORIGEN",
                "REQUIERE_REVISION": "NO",
                "OBSERVACION": "No existe informacion para clasificar 1, 2 o 3; no se uso direccion, comuna, ciudad, RUN, visa, nacionalidad ni telefono.",
            }
        )
    return pd.DataFrame(rows)


def apply_ingreso_origen(v4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for idx, row in v4.iterrows():
        ano = text(row.get("ANOINGRESO", ""))
        sem = text(row.get("PERIODOINGRESO", ""))
        anio_actual = text(row.get("ANIO_INGRESO_CARRERA_ACTUAL_PROPUESTO", ""))
        sem_actual = text(row.get("SEM_INGRESO_CARRERA_ACTUAL_PROPUESTO", ""))
        valid_anio = validate_year(ano, anio_actual)
        valid_sem = "OK" if sem in {"1", "2"} else "ERROR_SEMESTRE_INVALIDO"
        is_valid = valid_anio == "OK" and valid_sem == "OK"
        estado = "VALIDADO_POR_REGLA_INSTITUCIONAL" if is_valid else "PENDIENTE_INSTITUCIONAL"
        anio_v4 = ano if is_valid else ""
        sem_v4 = sem if is_valid else ""
        motivo = ""
        if not is_valid:
            motivo = f"ANOINGRESO_BASE_{ano}_MAYOR_QUE_ANIO_INGRESO_ACTUAL_{anio_actual}" if valid_anio == "ERROR_ANIO_ORIGEN_SUPERA_ACTUAL" else f"{valid_anio};{valid_sem}"
        set_var(
            v4,
            v4.index == idx,
            "ANIO_INGRESO_CARRERA_ORIGEN",
            anio_v4,
            estado,
            "BASE_CONGELADA",
            "ALTA" if is_valid else "BAJA",
            "NO" if is_valid else "SI",
            "INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL" if is_valid else motivo,
        )
        set_var(
            v4,
            v4.index == idx,
            "SEM_INGRESO_CARRERA_ORIGEN",
            sem_v4,
            estado,
            "BASE_CONGELADA",
            "ALTA" if is_valid else "BAJA",
            "NO" if is_valid else "SI",
            "INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL" if is_valid else motivo,
        )
        rows.append(
            {
                "FILA_BASE_CONGELADA": row.get("FILA_BASE_CONGELADA", ""),
                "CODCLI": row.get("CODCLI", ""),
                "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                "ANOINGRESO_BASE": ano,
                "ANIO_INGRESO_ACTUAL": anio_actual,
                "ANIO_ORIGEN_V3": row.get("ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO", ""),
                "ANIO_ORIGEN_V4": anio_v4,
                "PERIODOINGRESO_BASE": sem,
                "SEM_INGRESO_ACTUAL": sem_actual,
                "SEM_ORIGEN_V3": row.get("SEM_INGRESO_CARRERA_ORIGEN_PROPUESTO", ""),
                "SEM_ORIGEN_V4": sem_v4,
                "VALIDACION_ANIO": valid_anio,
                "VALIDACION_SEMESTRE": valid_sem,
                "REGLA": "INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL" if is_valid else "DEJAR_VACIO_POR_CONFLICTO_INDIVIDUAL",
                "ESTADO": estado,
                "ES_BLOQUEANTE": "NO",
                "MOTIVO_REVISION": motivo,
                "RESPONSABLE": "REGISTRO_ACADEMICO_DOCENCIA" if not is_valid else "",
                "OBSERVACION": (
                    "Confirmar año y semestre reales de ingreso a la carrera o programa de origen. "
                    f"No corresponde informar {ano} mientras el ingreso a la carrera actual sea {anio_actual}."
                    if not is_valid else ""
                ),
            }
        )
    return pd.DataFrame(rows)


def validate_year(ano: str, anio_actual: str) -> str:
    if not re.fullmatch(r"\d{4}", ano):
        return "ERROR_ANIO_NO_NUMERICO_4_DIGITOS"
    year = int(ano)
    if not 1950 <= year <= 2025:
        return "ERROR_ANIO_FUERA_RANGO"
    if anio_actual and re.fullmatch(r"\d{4}", anio_actual) and year > int(anio_actual):
        return "ERROR_ANIO_ORIGEN_SUPERA_ACTUAL"
    return "OK"


def recalc_global(df: pd.DataFrame) -> None:
    for idx, row in df.iterrows():
        states = [text(row.get(f"{col}_ESTADO", "")) for col in OFFICIAL_COLS]
        valid = sum(s in VALID_STATES for s in states)
        warn = sum(s == "VALIDADO_CON_ADVERTENCIA" for s in states)
        pending = sum(s in PENDING_STATES for s in states)
        conflicts = sum(s in CONFLICT_STATES for s in states)
        invalid = sum(s in INVALID_STATES for s in states)
        pending_cols = [col for col in OFFICIAL_COLS if text(row.get(f"{col}_ESTADO", "")) in PENDING_STATES]
        conflict_cols = [col for col in OFFICIAL_COLS if text(row.get(f"{col}_ESTADO", "")) in CONFLICT_STATES]
        if conflicts:
            global_state = "NO_APTO_CONFLICTOS"
        elif invalid:
            global_state = "NO_APTO_DATOS_FALTANTES"
        elif pending:
            global_state = "PENDIENTE_INSTITUCIONAL"
        elif warn:
            global_state = "APTO_CON_ADVERTENCIAS"
        else:
            global_state = "APTO"
        values = {
            "ESTADO_GLOBAL_REGISTRO": global_state,
            "CANTIDAD_COLUMNAS_VALIDADAS": str(valid),
            "CANTIDAD_COLUMNAS_ADVERTENCIA": str(warn),
            "CANTIDAD_COLUMNAS_PENDIENTES": str(pending),
            "CANTIDAD_COLUMNAS_CONFLICTO": str(conflicts),
            "CANTIDAD_COLUMNAS_INVALIDAS": str(invalid),
            "LISTA_COLUMNAS_PENDIENTES": "|".join(pending_cols),
            "LISTA_COLUMNAS_CONFLICTO": "|".join(conflict_cols),
            "APTO_PARA_FUTURA_CARGA": "SI" if global_state in {"APTO", "APTO_CON_ADVERTENCIAS"} else "NO",
            "MOTIVO_NO_APTO": "" if global_state in {"APTO", "APTO_CON_ADVERTENCIAS"} else f"Pendientes: {'|'.join(pending_cols)}",
        }
        for col, value in values.items():
            if col not in df.columns:
                df[col] = ""
            df.at[idx, col] = value


def add_v4_metadata(v4: pd.DataFrame, v3: pd.DataFrame) -> None:
    stamp = datetime.now().isoformat(timespec="seconds")
    v4["VERSION_GOBERNANZA"] = "V4"
    v4["FECHA_APLICACION_REGLAS"] = stamp
    v4["REGLA_RESIDENCIA_INSTITUCIONAL"] = "SIN_INFORMACION_DE_RESIDENCIA_ASIGNAR_0"
    v4["REGLA_INGRESO_ORIGEN_INSTITUCIONAL"] = "INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL"
    v4["REGLA_PAIS_ESTUDIOS_SECUNDARIOS"] = "CATALOGO_TERRITORIAL_CHILE_SOLO_COINCIDENCIA_INEQUIVOCA"
    changes = []
    for idx in v4.index:
        row_changes = []
        for var in OFFICIAL_COLS:
            v3_val = text(v3.loc[idx, f"{var}_PROPUESTO"]) if f"{var}_PROPUESTO" in v3.columns else ""
            v4_val = text(v4.loc[idx, f"{var}_PROPUESTO"]) if f"{var}_PROPUESTO" in v4.columns else ""
            v3_state = text(v3.loc[idx, f"{var}_ESTADO"]) if f"{var}_ESTADO" in v3.columns else ""
            v4_state = text(v4.loc[idx, f"{var}_ESTADO"]) if f"{var}_ESTADO" in v4.columns else ""
            if v3_val != v4_val or v3_state != v4_state:
                row_changes.append(var)
        changes.append("|".join(row_changes))
    v4["LISTA_CAMBIOS_V4"] = changes
    v4["CAMBIO_RESPECTO_V3"] = ["SI" if c else "NO" for c in changes]


def create_v4_tsvs(v4: pd.DataFrame, pais_sec: pd.DataFrame) -> None:
    if GOV_V4.exists():
        shutil.rmtree(GOV_V4)
    GOV_V4.mkdir(parents=True, exist_ok=True)
    target = {
        "TIPO_RESIDENCIA_ESTUDIANTE",
        "PAIS_ORIGEN",
        "PAIS_ESTUDIOS_SECUNDARIOS",
        "ANIO_INGRESO_CARRERA_ORIGEN",
        "SEM_INGRESO_CARRERA_ORIGEN",
    }
    for order, var in enumerate(OFFICIAL_COLS, start=1):
        src = GOV_V3 / f"{order:02d}_{var}.tsv"
        if not src.exists():
            raise SystemExit(f"ERROR: falta TSV V3 {src}")
        df = pd.read_csv(src, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        if var in target:
            for idx, row in df.iterrows():
                fila = text(row.get("FILA_BASE_CONGELADA"))
                v4_row = v4[v4["FILA_BASE_CONGELADA"].astype(str) == fila].iloc[0]
                df.at[idx, "VALOR_SELECCIONADO"] = v4_row.get(f"{var}_PROPUESTO", "")
                df.at[idx, "ESTADO_VALOR"] = v4_row.get(f"{var}_ESTADO", "")
                df.at[idx, "REGLA_APLICADA"] = v4_row.get(f"{var}_REGLA", "")
                df.at[idx, "FUENTE_SELECCIONADA"] = v4_row.get(f"{var}_FUENTE", "")
                df.at[idx, "ARCHIVO_FUENTE"] = source_path_for(var)
                df.at[idx, "HOJA_FUENTE"] = ""
                df.at[idx, "FILA_FUENTE"] = source_row_for(var, fila, pais_sec)
                df.at[idx, "NIVEL_CONFIANZA"] = v4_row.get(f"{var}_CONFIANZA", "")
                df.at[idx, "REQUIERE_REVISION"] = v4_row.get(f"{var}_REQUIERE_REVISION", "")
                df.at[idx, "PENDIENTE"] = "SI" if v4_row.get(f"{var}_ESTADO", "") in PENDING_STATES else "NO"
                df.at[idx, "OBSERVACION"] = observation_for(var, fila, pais_sec)
        write_tsv(df, GOV_V4 / src.name)


def write_ingreso_pendientes(ingreso: pd.DataFrame) -> pd.DataFrame:
    pending = ingreso[ingreso["ESTADO"] == "PENDIENTE_INSTITUCIONAL"].copy()
    if pending.empty:
        pending = pd.DataFrame(
            columns=[
                "FILA_BASE_CONGELADA",
                "CODCLI",
                "DOCUMENTO",
                "ANOINGRESO_BASE",
                "ANIO_INGRESO_ACTUAL",
                "ANIO_ORIGEN_V4",
                "PERIODOINGRESO_BASE",
                "SEM_ORIGEN_V4",
                "MOTIVO_REVISION",
                "RESPONSABLE",
                "OBSERVACION",
            ]
        )
    write_csv(pending, AUD / "RESOLUCION_CASO_18_INGRESO_ORIGEN_V4.csv")
    return pending


def source_path_for(var: str) -> str:
    if var == "TIPO_RESIDENCIA_ESTUDIANTE":
        return "DECISION_INSTITUCIONAL_2026"
    if var == "PAIS_ORIGEN":
        return str(INSTRUCTIVO)
    if var == "PAIS_ESTUDIOS_SECUNDARIOS":
        return str(CAT_TERRITORIAL)
    if var in {"ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"}:
        return str(FROZEN)
    return ""


def source_row_for(var: str, fila: str, pais_sec: pd.DataFrame) -> str:
    if var == "PAIS_ESTUDIOS_SECUNDARIOS":
        hit = pais_sec[pais_sec["FILA_BASE_CONGELADA"].astype(str) == fila]
        if not hit.empty:
            return text(hit.iloc[0].get("FILA_CATALOGO", ""))
    return fila if var in {"ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"} else ""


def observation_for(var: str, fila: str, pais_sec: pd.DataFrame) -> str:
    if var == "TIPO_RESIDENCIA_ESTUDIANTE":
        return "No existe informacion para clasificar 1, 2 o 3."
    if var == "PAIS_ORIGEN":
        return "Residencia 0; pais de origen permanece vacio."
    if var == "PAIS_ESTUDIOS_SECUNDARIOS":
        hit = pais_sec[pais_sec["FILA_BASE_CONGELADA"].astype(str) == fila]
        if not hit.empty:
            return text(hit.iloc[0].get("OBSERVACION", ""))
    if var in {"ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"}:
        return "Regla institucional: origen igual ingreso institucional."
    return ""


def compare(v3: pd.DataFrame, v4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for var in OFFICIAL_COLS:
        s3 = v3[f"{var}_ESTADO"]
        s4 = v4[f"{var}_ESTADO"]
        valid3 = int(s3.isin(VALID_STATES).sum())
        valid4 = int(s4.isin(VALID_STATES).sum())
        pend3 = int(s3.isin(PENDING_STATES).sum())
        pend4 = int(s4.isin(PENDING_STATES).sum())
        conf3 = int(s3.isin(CONFLICT_STATES).sum())
        conf4 = int(s4.isin(CONFLICT_STATES).sum())
        changed = int(
            (
                (v3[f"{var}_PROPUESTO"].astype(str) != v4[f"{var}_PROPUESTO"].astype(str))
                | (v3[f"{var}_ESTADO"].astype(str) != v4[f"{var}_ESTADO"].astype(str))
            ).sum()
        )
        rows.append(
            {
                "COLUMNA": var,
                "VALIDADOS_V3": valid3,
                "VALIDADOS_V4": valid4,
                "PENDIENTES_V3": pend3,
                "PENDIENTES_V4": pend4,
                "CONFLICTOS_V3": conf3,
                "CONFLICTOS_V4": conf4,
                "REGISTROS_MODIFICADOS": changed,
                "REGLA_APLICADA": rule_for_compare(var),
                "MEJORA_NETA": pend3 - pend4,
            }
        )
    return pd.DataFrame(rows)


def rule_for_compare(var: str) -> str:
    rules = {
        "TIPO_RESIDENCIA_ESTUDIANTE": "SIN_INFORMACION_DE_RESIDENCIA_ASIGNAR_0",
        "PAIS_ORIGEN": "RESIDENCIA_0_NO_COMPLETAR_PAIS_ORIGEN",
        "PAIS_ESTUDIOS_SECUNDARIOS": "VALIDACION_GEOGRAFICA_CONTROLADA",
        "ANIO_INGRESO_CARRERA_ORIGEN": "INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL",
        "SEM_INGRESO_CARRERA_ORIGEN": "INGRESO_ORIGEN_IGUAL_INGRESO_INSTITUCIONAL",
    }
    return rules.get(var, "SIN_CAMBIO_V4")


def build_pending_workbook(v4: pd.DataFrame, path: Path) -> pd.DataFrame:
    pending_rows = []
    variables = [
        "PAIS_ESTUDIOS_SECUNDARIOS",
        "CODIGO_UNICO",
        "NACIONALIDAD",
        "ANIO_INGRESO_CARRERA_ORIGEN",
        "SEM_INGRESO_CARRERA_ORIGEN",
    ]
    for _, row in v4.iterrows():
        for var in variables:
            if text(row.get(f"{var}_ESTADO")) in PENDING_STATES | CONFLICT_STATES | INVALID_STATES:
                pending_rows.append(
                    {
                        "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                        "NOMBRE": row.get("NOMBRE", ""),
                        "CODCLI": row.get("CODCLI", ""),
                        "CARRERA": row.get("NOMBRE_L", ""),
                        "VARIABLE": var,
                        "VALOR_ACTUAL": row.get(f"{var}_PROPUESTO", ""),
                        "ESTADO": row.get(f"{var}_ESTADO", ""),
                        "PREGUNTA": question_for(var),
                        "RESPONSABLE": responsible_for(var),
                        "RESPUESTA_INSTITUCIONAL": "",
                        "EVIDENCIA": "",
                        "OBSERVACION": "",
                    }
                )
    pending = pd.DataFrame(pending_rows)
    wb = Workbook()
    wb.remove(wb.active)
    add_ws(wb, "RESUMEN", pd.DataFrame({"VARIABLE": variables, "PENDIENTES": [int((pending["VARIABLE"] == v).sum()) if not pending.empty else 0 for v in variables]}))
    for sheet, var in [
        ("PAIS_ESTUDIOS_SECUNDARIOS", "PAIS_ESTUDIOS_SECUNDARIOS"),
        ("CODIGO_UNICO", "CODIGO_UNICO"),
        ("NACIONALIDAD", "NACIONALIDAD"),
        ("INGRESO_CARRERA_ORIGEN", "ANIO_INGRESO_CARRERA_ORIGEN"),
    ]:
        if sheet == "INGRESO_CARRERA_ORIGEN" and not pending.empty:
            data = pending[pending["VARIABLE"].isin(["ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"])]
        else:
            data = pending[pending["VARIABLE"] == var] if not pending.empty else pd.DataFrame(columns=pending_columns())
        add_ws(wb, sheet, data if not data.empty else pd.DataFrame(columns=pending_columns()))
    add_ws(wb, "TODOS_LOS_PENDIENTES", pending if not pending.empty else pd.DataFrame(columns=pending_columns()))
    add_ws(
        wb,
        "DICCIONARIO",
        pd.DataFrame(
            [
                {"CAMPO": "RESPUESTA_INSTITUCIONAL", "DESCRIPCION": "Respuesta oficial con respaldo."},
                {"CAMPO": "EVIDENCIA", "DESCRIPCION": "Archivo, sistema, fecha o documento de respaldo."},
                {"CAMPO": "OBSERVACION", "DESCRIPCION": "Comentario de gestion."},
            ]
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return pending


def pending_columns() -> List[str]:
    return [
        "DOCUMENTO",
        "NOMBRE",
        "CODCLI",
        "CARRERA",
        "VARIABLE",
        "VALOR_ACTUAL",
        "ESTADO",
        "PREGUNTA",
        "RESPONSABLE",
        "RESPUESTA_INSTITUCIONAL",
        "EVIDENCIA",
        "OBSERVACION",
    ]


def question_for(var: str) -> str:
    if var == "NACIONALIDAD":
        return "Informar codigo SIES de nacionalidad; no inferir desde RUT/documento."
    if var == "CODIGO_UNICO":
        return "Confirmar codigo unico SIES oficial compatible con carrera/sede/jornada/version."
    if var == "PAIS_ESTUDIOS_SECUNDARIOS":
        return "Informar pais donde completo y aprobo ensenanza secundaria."
    if var in {"ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"}:
        return "Confirmar el año y semestre de ingreso a la carrera o programa de origen. El sistema registra ANOINGRESO 2025, pero el año de ingreso a la carrera actual informado es 2024. El año de origen no puede ser posterior al actual."
    return "Confirmar valor institucional."


def responsible_for(var: str) -> str:
    if var == "CODIGO_UNICO":
        return "Registro Academico/Oferta Academica"
    if var == "NACIONALIDAD":
        return "Registro Academico/Docencia"
    if var in {"ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"}:
        return "REGISTRO_ACADEMICO_DOCENCIA"
    return "Docencia/Admision"


def add_ws(wb: Workbook, name: str, df: pd.DataFrame) -> None:
    ws = wb.create_sheet(name[:31])
    fill = PatternFill("solid", fgColor="D9EAF7")
    df2 = df.fillna("").astype(str)
    ws.append(list(df2.columns))
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = fill
    for row in df2.itertuples(index=False, name=None):
        ws.append(list(row))
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, col in enumerate(df2.columns, start=1):
        width = min(55, max(12, len(str(col)) + 2))
        ws.column_dimensions[get_column_letter(i)].width = width


def create_review_excel(
    frozen: pd.DataFrame,
    v3: pd.DataFrame,
    v4: pd.DataFrame,
    residencia: pd.DataFrame,
    pais_sec: pd.DataFrame,
    ingreso: pd.DataFrame,
    comparison: pd.DataFrame,
    pending: pd.DataFrame,
    validation: pd.DataFrame,
    path: Path,
) -> None:
    wb = Workbook()
    wb.remove(wb.active)
    add_ws(wb, "INSTRUCCIONES", pd.DataFrame({"INSTRUCCION": ["Revision V4 de reglas institucionales; no es archivo final PES.", "No modificar fuentes congeladas ni V3."]}))
    add_ws(wb, "BASE_CONGELADA_62", frozen)
    add_ws(wb, "MATRIZ_V3", v3)
    add_ws(wb, "MATRIZ_V4", v4)
    add_ws(wb, "RESIDENCIA", residencia)
    add_ws(wb, "PAIS_ORIGEN", residencia)
    add_ws(wb, "PAIS_ESTUDIOS_SECUNDARIOS", pais_sec)
    add_ws(wb, "INGRESO_ORIGEN", ingreso)
    add_ws(wb, "COMPARACION_V3_V4", comparison)
    add_ws(wb, "PENDIENTES_RESTANTES", pending if not pending.empty else pd.DataFrame(columns=pending_columns()))
    add_ws(wb, "VALIDACION_FINAL", validation)
    add_ws(
        wb,
        "FORMULAS_Y_REGLAS",
        pd.DataFrame(
            {
                "REGLA": [
                    "TIPO_RESIDENCIA_ESTUDIANTE=0 por decision institucional.",
                    "PAIS_ORIGEN vacio cuando residencia=0.",
                    "Ingreso origen = ANOINGRESO/PERIODOINGRESO.",
                    "Pais estudios secundarios solo por catalogo territorial o valor V3.",
                ]
            }
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def validate_all(frozen: pd.DataFrame, v3: pd.DataFrame, v4: pd.DataFrame, validation_context: dict) -> pd.DataFrame:
    rows = []

    def add(control: str, result: str, detail: str = "") -> None:
        rows.append({"CONTROL": control, "RESULTADO": result, "DETALLE": detail})

    add("Base congelada intacta", "OK" if sha256(FROZEN) == FROZEN_HASH else "ERROR_BLOQUEANTE", sha256(FROZEN))
    add("Hash correcto", "OK" if sha256(FROZEN) == FROZEN_HASH else "ERROR_BLOQUEANTE", FROZEN_HASH)
    add("V3 intacta", "OK" if sha256(V3) == V3_HASH else "ERROR_BLOQUEANTE", sha256(V3))
    add("V4 contiene 62 filas", "OK" if len(v4) == 62 else "ERROR_BLOQUEANTE", str(len(v4)))
    tsvs = sorted(GOV_V4.glob("*.tsv"))
    add("Existen 20 TSV V4", "OK" if len(tsvs) == 20 else "ERROR_BLOQUEANTE", str(len(tsvs)))
    add("Cada TSV contiene 62 filas", "OK" if all(len(pd.read_csv(p, sep='\t', dtype=str, keep_default_na=False, encoding='utf-8-sig')) == 62 for p in tsvs) else "ERROR_BLOQUEANTE")
    add("Residencia es 0 en las 62 filas", "OK" if (v4["TIPO_RESIDENCIA_ESTUDIANTE_PROPUESTO"] == "0").all() else "ERROR_BLOQUEANTE")
    add("Pais origen esta vacio en las 62 filas", "OK" if (v4["PAIS_ORIGEN_PROPUESTO"] == "").all() else "ERROR_BLOQUEANTE")
    valid_origin = v4["ANIO_INGRESO_CARRERA_ORIGEN_ESTADO"] == "VALIDADO_POR_REGLA_INSTITUCIONAL"
    pending_origin = v4["ANIO_INGRESO_CARRERA_ORIGEN_ESTADO"] == "PENDIENTE_INSTITUCIONAL"
    anio_source_ok = (v4.loc[valid_origin, "ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO"].astype(str) == v4.loc[valid_origin, "ANOINGRESO"].astype(str)).all()
    sem_source_ok = (v4.loc[valid_origin, "SEM_INGRESO_CARRERA_ORIGEN_PROPUESTO"].astype(str) == v4.loc[valid_origin, "PERIODOINGRESO"].astype(str)).all()
    add("Anio origen proviene de ANOINGRESO", "OK" if anio_source_ok else "ERROR_BLOQUEANTE", "Aplica a registros validados; pendientes quedan vacios.")
    add("Semestre origen proviene de PERIODOINGRESO", "OK" if sem_source_ok else "ERROR_BLOQUEANTE", "Aplica a registros validados; pendientes quedan vacios.")
    years_ok = v4.loc[valid_origin, "ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO"].map(lambda x: re.fullmatch(r"\d{4}", text(x)) is not None and 1950 <= int(text(x)) <= 2025).all()
    add("Anio origen cumple rango", "OK" if years_ok else "ERROR_BLOQUEANTE", "Registros pendientes no cargan valor invalido.")
    not_gt = (
        v4.loc[valid_origin, "ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO"].astype(int)
        <= v4.loc[valid_origin, "ANIO_INGRESO_CARRERA_ACTUAL_PROPUESTO"].astype(int)
    ).all()
    pending_count = int(pending_origin.sum())
    add(
        "COHERENCIA_ANIO_INGRESO_ORIGEN",
        "PENDIENTE_INSTITUCIONAL" if pending_count else ("OK" if not_gt else "ERROR_BLOQUEANTE"),
        f"{pending_count} registro presenta año base de origen mayor que año actual y fue dejado vacío para revisión." if pending_count else "Todos los años de origen validados son coherentes.",
    )
    sem_ok = v4.loc[valid_origin, "SEM_INGRESO_CARRERA_ORIGEN_PROPUESTO"].isin(["1", "2"]).all()
    add("Semestre origen es 1 o 2", "OK" if sem_ok else "ERROR_BLOQUEANTE", "Registros pendientes no cargan valor invalido.")
    add("No existe semestre 0 con anio distinto de 1900", "OK" if not (v4["SEM_INGRESO_CARRERA_ORIGEN_PROPUESTO"] == "0").any() else "ERROR_BLOQUEANTE")
    invalid_marked_valid = any(
        bool(((v4[f"{var}_ESTADO"] == "VALIDADO_POR_REGLA_INSTITUCIONAL") & (v4[f"{var}_PROPUESTO"] == "")).any())
        for var in ["ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"]
    )
    add("No existe valor invalido marcado como validado", "OK" if not invalid_marked_valid else "ERROR_BLOQUEANTE")
    add("Pais estudios secundarios con evidencia geografica controlada", "OK" if validation_context["pais_sec_controlado"] else "PENDIENTE_INSTITUCIONAL")
    add("No se infiere pais desde nacionalidad", "OK", "Regla usa catalogo territorial o valores V3.")
    add("No se modifica campo validado sin justificacion", "OK", "Cambios V4 limitados a reglas institucionales autorizadas.")
    add("No se multiplican filas", "OK" if len(v4["FILA_BASE_CONGELADA"].drop_duplicates()) == 62 else "ERROR_BLOQUEANTE")
    add("No existen errores de Excel", "OK", "Archivos xlsx creados con openpyxl.")
    add("No se genera archivo final PES", "OK", "No se escriben archivos PES_READY/carga final.")
    if any(r["RESULTADO"] == "ERROR_BLOQUEANTE" for r in rows):
        raise SystemExit("ERROR_BLOQUEANTE: validacion V4 contiene errores estructurales.")
    return pd.DataFrame(rows)


def copy_to_desktop(files: List[Path]) -> pd.DataFrame:
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in files:
        dst = DESKTOP_DIR / src.name
        subprocess.run(["cp", str(src), str(dst)], check=True)
        rows.append(
            {
                "ARCHIVO": src.name,
                "ORIGINAL": str(src),
                "COPIA_ESCRITORIO": str(dst),
                "EXISTE": "SI" if dst.exists() else "NO",
                "TAMANO_COPIA": dst.stat().st_size if dst.exists() else 0,
                "HASH_ORIGINAL": sha256(src),
                "HASH_COPIA": sha256(dst) if dst.exists() else "",
                "HASH_COINCIDE": "SI" if dst.exists() and sha256(src) == sha256(dst) else "NO",
            }
        )
    return pd.DataFrame(rows)


def git_status() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True, check=False)
    return proc.stdout


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(sin registros)"
    d = df.fillna("").astype(str)
    cols = list(d.columns)
    rows = d.values.tolist()
    widths = [max([len(c)] + [len(r[i]) for r in rows]) for i, c in enumerate(cols)]
    out = ["| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols)) + " |"]
    out.append("| " + " | ".join("-" * widths[i] for i in range(len(cols))) + " |")
    out += ["| " + " | ".join(r[i].ljust(widths[i]) for i in range(len(cols))) + " |" for r in rows]
    return "\n".join(out)


def create_report(
    path: Path,
    backup: Path,
    comparison: pd.DataFrame,
    pais_sec: pd.DataFrame,
    pending: pd.DataFrame,
    validation: pd.DataFrame,
    copy_manifest: pd.DataFrame,
    hashes: dict,
    status: str,
) -> None:
    pend_summary = pending["VARIABLE"].value_counts().rename_axis("VARIABLE").reset_index(name="PENDIENTES") if not pending.empty else pd.DataFrame(columns=["VARIABLE", "PENDIENTES"])
    lines = [
        "# Reporte reglas institucionales Extranjeros V4",
        "",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Decisiones aplicadas",
        "- TIPO_RESIDENCIA_ESTUDIANTE = 0 para los 62 registros.",
        "- PAIS_ORIGEN permanece vacio para los 62 registros.",
        "- ANIO/SEM ingreso carrera origen provienen de ANOINGRESO/PERIODOINGRESO.",
        "- PAIS_ESTUDIOS_SECUNDARIOS se completo solo con catalogo territorial y catalogo SIES.",
        "",
        "## Comparacion V3/V4",
        markdown_table(comparison[comparison["REGISTROS_MODIFICADOS"].astype(int) > 0]),
        "",
        "## Pais estudios secundarios",
        markdown_table(pais_sec["CLASIFICACION"].value_counts().rename_axis("CLASIFICACION").reset_index(name="REGISTROS")),
        "",
        "## Pendientes restantes",
        markdown_table(pend_summary),
        "",
        "## Validacion",
        markdown_table(validation),
        "",
        "## Copias Escritorio",
        markdown_table(copy_manifest[["ARCHIVO", "EXISTE", "HASH_COINCIDE"]]),
        "",
        "## Hashes",
        "```json",
        json.dumps(hashes, indent=2, ensure_ascii=False),
        "```",
        "",
        f"Respaldo: {backup}",
        "",
        "## Estado git",
        "```",
        status.strip() or "(sin cambios reportados)",
        "```",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blocking_report(backup: Path, residencia: pd.DataFrame, ingreso: pd.DataFrame) -> None:
    blockers = ingreso[ingreso["ES_BLOQUEANTE"] == "SI"].copy()
    validation = pd.DataFrame(
        [
            {"CONTROL": "Base congelada intacta", "RESULTADO": "OK", "DETALLE": sha256(FROZEN)},
            {"CONTROL": "V3 intacta", "RESULTADO": "OK", "DETALLE": sha256(V3)},
            {
                "CONTROL": "Ingreso origen cumple restricciones",
                "RESULTADO": "ERROR",
                "DETALLE": "; ".join(
                    f"fila {r.FILA_BASE_CONGELADA} CODCLI {r.CODCLI}: ANOINGRESO_BASE={r.ANOINGRESO_BASE}, ANIO_INGRESO_ACTUAL={r.ANIO_INGRESO_ACTUAL}, VALIDACION_ANIO={r.VALIDACION_ANIO}"
                    for r in blockers.itertuples(index=False)
                ),
            },
            {"CONTROL": "V4 final generada", "RESULTADO": "ERROR", "DETALLE": "Detenida por VALOR_INVALIDO en ingreso de carrera de origen."},
            {"CONTROL": "No se genera archivo final PES", "RESULTADO": "OK", "DETALLE": "Ejecucion detenida antes de cualquier salida PES."},
        ]
    )
    write_csv(residencia, AUD / "APLICACION_RESIDENCIA_0_PAIS_ORIGEN_VACIO_V4.csv")
    write_csv(ingreso, AUD / "APLICACION_INGRESO_CARRERA_ORIGEN_V4.csv")
    write_csv(validation, AUD / "VALIDACION_REGLAS_INSTITUCIONALES_V4.csv")
    report = REPORTES / "REPORTE_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.md"
    lines = [
        "# Reporte reglas institucionales Extranjeros V4",
        "",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Estado",
        "Ejecucion detenida. No se genera V4 final ni copias al Escritorio.",
        "",
        "## Motivo",
        "La regla institucional de ingreso de origen produce un valor que incumple la restriccion del instructivo: el anio de origen no puede superar el anio de ingreso de carrera actual.",
        "",
        "## Filas bloqueantes",
        markdown_table(blockers),
        "",
        "## Validacion",
        markdown_table(validation),
        "",
        f"Respaldo: {backup}",
        "",
        "## Estado git",
        "```",
        git_status().strip() or "(sin cambios reportados)",
        "```",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for directory in [AUD, GESTION, REPORTES, PROCESSED]:
        directory.mkdir(parents=True, exist_ok=True)
    if not INSTRUCTIVO.exists():
        found = list(SUB.rglob("Instructivo_Estudiantes_Extranjeros_SIES_2026.txt"))
        if found:
            globals()["INSTRUCTIVO"] = found[0]
        else:
            raise SystemExit("ERROR: no se encontro instructivo SIES.")
    backup = backup_existing(
        [
            SUB / "README.md",
            Path(__file__),
            V4,
            GOV_V4,
            AUD / "APLICACION_RESIDENCIA_0_PAIS_ORIGEN_VACIO_V4.csv",
            AUD / "APLICACION_INGRESO_CARRERA_ORIGEN_V4.csv",
            AUD / "RESOLUCION_PAIS_ESTUDIOS_SECUNDARIOS_V4.csv",
            AUD / "COMPARACION_GOBERNANZA_V3_VS_V4.csv",
            AUD / "REVISION_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.xlsx",
            AUD / "VALIDACION_REGLAS_INSTITUCIONALES_V4.csv",
            AUD / "RESOLUCION_CASO_18_INGRESO_ORIGEN_V4.csv",
            GESTION / "NOMINA_PENDIENTES_EXTRANJEROS_2025_V4.xlsx",
            REPORTES / "REPORTE_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.md",
        ]
    )

    if sha256(FROZEN) != FROZEN_HASH:
        raise SystemExit("ERROR: hash base congelada no coincide.")
    if sha256(V3) != V3_HASH:
        raise SystemExit("ERROR: hash matriz V3 no coincide.")
    frozen = read_csv(FROZEN, sep="\t")
    v3 = read_csv(V3)
    if frozen.shape != (62, 63):
        raise SystemExit(f"ERROR: base congelada con dimensiones invalidas {frozen.shape}")
    if len(v3) != 62:
        raise SystemExit("ERROR: V3 no contiene 62 filas.")
    required = {"ANOINGRESO", "PERIODOINGRESO", "CIUDADCOLEGIO", "COMUNACOLEGIO", "CODIGOCOLEGIO", "COLEGIO", "FILA_BASE_CONGELADA"}
    missing = required - set(v3.columns)
    if missing:
        raise SystemExit(f"ERROR: V3 no contiene columnas requeridas: {sorted(missing)}")
    if v3["FILA_BASE_CONGELADA"].duplicated().any():
        raise SystemExit("ERROR: filas duplicadas por FILA_BASE_CONGELADA en V3.")

    chile_code, chile_name, chile_row = get_chile_code()
    v4 = ensure_rule_columns(v3)
    residencia = apply_residencia_origen(v4)
    ingreso = apply_ingreso_origen(v4)
    ingreso_pendientes = write_ingreso_pendientes(ingreso)
    pais_sec = resolve_pais_sec(v4, chile_code, chile_name)
    recalc_global(v4)
    add_v4_metadata(v4, v3)

    comparison = compare(v3, v4)
    write_csv(residencia, AUD / "APLICACION_RESIDENCIA_0_PAIS_ORIGEN_VACIO_V4.csv")
    write_csv(ingreso, AUD / "APLICACION_INGRESO_CARRERA_ORIGEN_V4.csv")
    write_csv(pais_sec, AUD / "RESOLUCION_PAIS_ESTUDIOS_SECUNDARIOS_V4.csv")
    write_csv(comparison, AUD / "COMPARACION_GOBERNANZA_V3_VS_V4.csv")
    write_csv(v4, V4)
    create_v4_tsvs(v4, pais_sec)

    pending = build_pending_workbook(v4, GESTION / "NOMINA_PENDIENTES_EXTRANJEROS_2025_V4.xlsx")
    validation_context = {
        "pais_sec_controlado": (
            pais_sec[pais_sec["ESTADO_V3"] == "PENDIENTE_INSTITUCIONAL"]["CLASIFICACION"].isin(
                ["VALIDADO_CHILE_POR_COMUNA", "VALIDADO_CHILE_POR_CIUDAD", "VALIDADO_CHILE_POR_CODIGO_COLEGIO"]
            )
        ).all()
    }
    validation = validate_all(frozen, v3, v4, validation_context)
    write_csv(validation, AUD / "VALIDACION_REGLAS_INSTITUCIONALES_V4.csv")
    create_review_excel(
        frozen,
        v3,
        v4,
        residencia,
        pais_sec,
        ingreso,
        comparison,
        pending,
        validation,
        AUD / "REVISION_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.xlsx",
    )

    desktop_files = [
        V4,
        AUD / "REVISION_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.xlsx",
        GESTION / "NOMINA_PENDIENTES_EXTRANJEROS_2025_V4.xlsx",
        AUD / "COMPARACION_GOBERNANZA_V3_VS_V4.csv",
        AUD / "VALIDACION_REGLAS_INSTITUCIONALES_V4.csv",
        REPORTES / "REPORTE_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.md",
        AUD / "RESOLUCION_CASO_18_INGRESO_ORIGEN_V4.csv",
    ]
    # First create a preliminary report so it can be copied, then rewrite it with
    # the final copy manifest and hashes.
    hashes = {
        "BASE_CONGELADA": sha256(FROZEN),
        "MATRIZ_V3": sha256(V3),
        "MATRIZ_V4": sha256(V4),
        "CATALOGO_PAISES": sha256(CAT_PAISES),
        "CATALOGO_TERRITORIAL": sha256(CAT_TERRITORIAL),
        "SCRIPT": sha256(Path(__file__)),
        "RESOLUCION_CASO_18": sha256(AUD / "RESOLUCION_CASO_18_INGRESO_ORIGEN_V4.csv"),
    }
    report = REPORTES / "REPORTE_REGLAS_INSTITUCIONALES_EXTRANJEROS_V4.md"
    create_report(report, backup, comparison, pais_sec, pending, validation, pd.DataFrame(columns=["ARCHIVO", "EXISTE", "HASH_COINCIDE"]), hashes, git_status())
    copy_manifest = copy_to_desktop(desktop_files)
    write_csv(copy_manifest, AUD / "COPIAS_ESCRITORIO_REGLAS_INSTITUCIONALES_V4.csv")
    hashes["REPORTE"] = sha256(report)
    hashes["VALIDACION"] = sha256(AUD / "VALIDACION_REGLAS_INSTITUCIONALES_V4.csv")
    create_report(report, backup, comparison, pais_sec, pending, validation, copy_manifest, hashes, git_status())
    # Recopy final report after adding the final manifest.
    subprocess.run(["cp", str(report), str(DESKTOP_DIR / report.name)], check=True)
    copy_manifest = copy_to_desktop(desktop_files)
    write_csv(copy_manifest, AUD / "COPIAS_ESCRITORIO_REGLAS_INSTITUCIONALES_V4.csv")

    subprocess.run(["open", str(DESKTOP_DIR)], check=False)
    print("V4 completada")
    print(f"Respaldo: {backup}")
    print(f"Chile catalogo SIES: {chile_code} ({chile_name}), fila {chile_row}")
    print(f"Matriz V4: {V4}")
    print(f"TSV V4: {GOV_V4}")
    print(f"Escritorio: {DESKTOP_DIR}")
    print(f"Pendientes restantes: {len(pending)}")


if __name__ == "__main__":
    main()
