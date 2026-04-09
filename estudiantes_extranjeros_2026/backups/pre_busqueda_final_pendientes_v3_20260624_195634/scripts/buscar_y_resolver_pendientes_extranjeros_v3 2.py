#!/usr/bin/env python3
"""Busqueda final dirigida de pendientes de gobernanza V2.

No modifica congelados ni V2. Crea V3 solo si existen mejoras respaldadas.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


SUBPROJECT = Path(__file__).resolve().parents[1]
ROOT = SUBPROJECT.parent
AUD = SUBPROJECT / "resultados" / "auditorias"
GESTION = SUBPROJECT / "resultados" / "gestion"
REPORTES = SUBPROJECT / "resultados" / "reportes"
PROCESSED = SUBPROJECT / "data" / "processed"
GOV_V2 = SUBPROJECT / "data" / "governed" / "columnas_extranjeros_2025_v2"
GOV_V3 = SUBPROJECT / "data" / "governed" / "columnas_extranjeros_2025_v3"

FROZEN = SUBPROJECT / "data" / "frozen" / "BASE_EXTRANJEROS_2025_CONGELADA.tsv"
FROZEN_HASH = "da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081"
V2_MATRIX = PROCESSED / "MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V2.csv"
V3_MATRIX = PROCESSED / "MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V3.csv"
INSTRUCTIVO = SUBPROJECT / "docs" / "Instructivo_Estudiantes_Extranjeros_SIES_2026.txt"

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

TARGET_VARS = [
    "NACIONALIDAD",
    "TIPO_RESIDENCIA_ESTUDIANTE",
    "PAIS_ORIGEN",
    "PAIS_ESTUDIOS_SECUNDARIOS",
    "CODIGO_UNICO",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "VIGENCIA",
]

PENDING_STATES = {
    "PENDIENTE_INSTITUCIONAL",
    "VACIO_NO_PERMITIDO",
    "CONFLICTO_ENTRE_FUENTES",
    "VALOR_INVALIDO",
}

SOURCE_FILES = {
    "precarga_original": SUBPROJECT / "data" / "raw" / "REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv",
    "precarga_normalizada": SUBPROJECT / "data" / "interim" / "PRECARGA_EXTRANJEROS_REGULARES_2026_NORMALIZADA.csv",
    "matricula_control": ROOT / "resultados" / "matricula_avance_curricular_2025_control.csv",
    "universo_257": AUD / "UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv",
    "res_codigo_unico": AUD / "RESOLUCION_CODIGO_UNICO.csv",
    "cand_multiples": AUD / "CANDIDATOS_19_COINCIDENCIAS_MULTIPLES.csv",
    "res_vigencia_parcial": AUD / "RESOLUCION_4_SIN_EVIDENCIA_2025.csv",
    "aud_vigencia_corregida": AUD / "AUDITORIA_VIGENCIA_2025_CORREGIDA.csv",
    "res_nacionalidad": AUD / "RESOLUCION_NACIONALIDAD_AMBIGUA_62.csv",
    "puente_sies": ROOT / "control" / "catalogos" / "PUENTE_SIES_COMPILADO.tsv",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def norm_doc(value: object) -> str:
    return re.sub(r"[^0-9Kk]", "", norm_text(value)).upper()


def doc_from_rut(value: object) -> str:
    raw = norm_doc(value)
    if len(raw) > 1 and raw[-1] in "0123456789K":
        return raw[:-1]
    return raw


def detect_encoding(path: Path) -> str:
    raw = path.read_bytes()[:50000]
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin1"


def detect_sep(path: Path, enc: str) -> str:
    if path.suffix.lower() == ".tsv":
        return "\t"
    text = path.read_bytes()[:50000].decode(enc, errors="replace")
    first = text.splitlines()[0] if text.splitlines() else ""
    counts = {",": first.count(","), ";": first.count(";"), "\t": first.count("\t"), "|": first.count("|")}
    sep, count = max(counts.items(), key=lambda item: item[1])
    if count > 0:
        return sep
    try:
        return csv.Sniffer().sniff(text, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_table(path: Path, **kwargs) -> pd.DataFrame:
    enc = kwargs.pop("encoding", None) or detect_encoding(path)
    sep = kwargs.pop("sep", None) or detect_sep(path, enc)
    return pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding=enc, engine="python", **kwargs)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, sep="\t", encoding="utf-8-sig")


def backup_existing(paths: Iterable[Path]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = SUBPROJECT / "backups" / f"pre_busqueda_final_pendientes_v3_{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.exists():
            rel = p.relative_to(SUBPROJECT) if p.is_relative_to(SUBPROJECT) else Path(p.name)
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if p.is_dir():
                shutil.copytree(p, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(p, dest)
    return backup


def load_sources() -> Dict[str, pd.DataFrame]:
    frames: Dict[str, pd.DataFrame] = {}
    for name, path in SOURCE_FILES.items():
        if not path.exists():
            frames[name] = pd.DataFrame()
            continue
        try:
            frames[name] = read_table(path)
        except Exception as exc:  # noqa: BLE001 - audit output needs failure details elsewhere
            frames[name] = pd.DataFrame({"_ERROR_": [str(exc)]})
    return frames


def add_doc_columns(df: pd.DataFrame, column: str = "NUM_DOCUMENTO") -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return df.copy()
    out = df.copy()
    out["_DOC_NORM_"] = out[column].map(norm_doc)
    return out


def rows_by(df: pd.DataFrame, column: str) -> Dict[str, pd.DataFrame]:
    if df.empty or column not in df.columns:
        return {}
    return {k: g.copy() for k, g in df.groupby(column, dropna=False)}


def pending_exact(v2: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in v2.iterrows():
        for var in TARGET_VARS:
            estado = norm_text(row.get(f"{var}_ESTADO"))
            if estado not in PENDING_STATES:
                continue
            fuente = norm_text(row.get(f"{var}_FUENTE"))
            rows.append(
                {
                    "FILA_BASE_CONGELADA": row.get("FILA_BASE_CONGELADA", ""),
                    "ID_CONTROL": row.get("ID_CONTROL_257", ""),
                    "CODCLI": row.get("CODCLI", ""),
                    "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                    "NOMBRE": row.get("NOMBRE", ""),
                    "VARIABLE_PENDIENTE": var,
                    "VALOR_ACTUAL": row.get(f"{var}_PROPUESTO", ""),
                    "ESTADO_V2": estado,
                    "MOTIVO_V2": fuente,
                    "FUENTES_YA_REVISADAS": fuente,
                    "FUENTE_FALTANTE": missing_source_for(var),
                    "RESPONSABLE_SUGERIDO": responsible_for(var),
                }
            )
    return pd.DataFrame(rows)


def responsible_for(var: str) -> str:
    if var in {"CODIGO_UNICO", "ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"}:
        return "Registro Academico/Oferta Academica"
    if var in {"TIPO_RESIDENCIA_ESTUDIANTE", "PAIS_ORIGEN", "NACIONALIDAD"}:
        return "Registro Academico/Docencia"
    if var == "PAIS_ESTUDIOS_SECUNDARIOS":
        return "Docencia/Admision"
    if var == "VIGENCIA":
        return "Docencia/Registro Academico"
    return "Registro Academico"


def missing_source_for(var: str) -> str:
    mapping = {
        "NACIONALIDAD": "Fuente institucional explicita de nacionalidad",
        "TIPO_RESIDENCIA_ESTUDIANTE": "Declaracion institucional de residencia previa",
        "PAIS_ORIGEN": "Pais de origen solo si TIPO_RESIDENCIA_ESTUDIANTE es 2 o 3",
        "PAIS_ESTUDIOS_SECUNDARIOS": "Pais explicito donde completo secundaria",
        "CODIGO_UNICO": "Oferta/puente SIES o resolucion tecnica inequivoca",
        "ANIO_INGRESO_CARRERA_ORIGEN": "Ingreso explicito a carrera de origen",
        "SEM_INGRESO_CARRERA_ORIGEN": "Semestre explicito de carrera de origen",
        "VIGENCIA": "Evidencia explicita de actividad academica 2025",
    }
    return mapping.get(var, "Fuente institucional explicita")


def source_inventory(v2: pd.DataFrame, pending: pd.DataFrame) -> pd.DataFrame:
    target_terms = [
        "residencia",
        "tipo_residencia",
        "pais_origen",
        "pais_de_origen",
        "pais_estudios",
        "pais_secundaria",
        "codigo_unico",
        "clave_oficial_carga",
        "oferta",
        "puente",
        "vigencia",
        "evidencia_2025",
        "anio_ingreso_carrera_origen",
        "sem_ingreso_carrera_origen",
        "nacionalidad",
        "PES_READY",
    ]
    suffixes = {".csv", ".tsv", ".xlsx", ".xls", ".txt", ".json", ".parquet", ".sqlite", ".db", ".py", ".md"}
    excluded = {".git", ".venv", "node_modules", "__pycache__"}
    pending_key_map = {}
    for _, prow in pending.iterrows():
        fila = norm_text(prow.get("FILA_BASE_CONGELADA", ""))
        doc = norm_doc(prow.get("DOCUMENTO", ""))
        codcli = norm_text(prow.get("CODCLI", ""))
        if doc:
            pending_key_map[doc] = fila
        if codcli:
            pending_key_map[codcli] = fila
    rows = []

    def skip(path: Path) -> bool:
        parts = {p.lower() for p in path.parts}
        if parts & excluded:
            return True
        low = str(path).lower()
        if "/backups/" in low or "/backup_estable" in low or "/archivo_backup" in low:
            return True
        if "/archive/cleanup/" in low:
            return True
        if "_v3" in path.name.lower() or "pendientes_exacto" in path.name.lower():
            return True
        if path.name == "buscar_y_resolver_pendientes_extranjeros_v3.py":
            return True
        return False

    def classify_var(text: str) -> str:
        low = text.lower()
        found = []
        checks = {
            "TIPO_RESIDENCIA_ESTUDIANTE": ["residencia", "tipo_residencia"],
            "PAIS_ORIGEN": ["pais_origen", "pais_de_origen", "país_de_origen"],
            "PAIS_ESTUDIOS_SECUNDARIOS": ["pais_estudios", "pais_secundaria", "estudios_secundarios"],
            "CODIGO_UNICO": ["codigo_unico", "código_unico", "clave_oficial_carga", "puente"],
            "ANIO_INGRESO_CARRERA_ORIGEN": ["anio_ingreso_carrera_origen", "carrera_origen"],
            "SEM_INGRESO_CARRERA_ORIGEN": ["sem_ingreso_carrera_origen", "carrera_origen"],
            "VIGENCIA": ["vigencia", "evidencia_2025", "actividad_academica"],
            "NACIONALIDAD": ["nacionalidad"],
        }
        for var, terms in checks.items():
            if any(t in low for t in terms):
                found.append(var)
        return "|".join(found)

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes or skip(path):
            continue
        low_name = path.name.lower()
        if not any(t.lower() in low_name for t in target_terms):
            # Header inspection is intentionally limited to likely structured files.
            if path.suffix.lower() not in {".csv", ".tsv", ".xlsx", ".xls"}:
                continue
        try:
            if path.suffix.lower() in {".csv", ".tsv"}:
                df = read_table(path, nrows=5000)
                header = "|".join(df.columns)
                variable = classify_var(path.name + "|" + header)
                if not variable:
                    continue
                keys = [c for c in df.columns if any(k in c.upper() for k in ["CODCLI", "NUM_DOCUMENTO", "RUT", "CLAVE", "CODIGO_UNICO"])]
                covered = count_covered(df, keys, pending_key_map)
                rows.append(
                    {
                        "ARCHIVO": str(path),
                        "HOJA": "",
                        "FILAS": len(df),
                        "COLUMNAS": len(df.columns),
                        "VARIABLE_OBJETIVO": variable,
                        "CAMPOS_ENCONTRADOS": ";".join([c for c in df.columns if classify_var(c)]),
                        "CLAVES_DISPONIBLES": ";".join(keys),
                        "REGISTROS_PENDIENTES_CUBIERTOS": covered,
                        "PRIORIDAD": priority_for(path),
                        "REQUIERE_LECTURA": "SI" if covered else "NO",
                        "OBSERVACION": "Inventario dirigido por nombre/encabezado.",
                    }
                )
            elif path.suffix.lower() in {".xlsx", ".xls"}:
                if path.suffix.lower() == ".xls":
                    # Legacy XLS inspection is intentionally limited; most active
                    # sources in this repo are CSV/TSV/XLSX.
                    continue
                try:
                    wb = load_workbook(path, read_only=True, data_only=True)
                except Exception:
                    continue
                for sheet in wb.sheetnames[:10]:
                    ws = wb[sheet]
                    values = list(ws.iter_rows(min_row=1, max_row=min(ws.max_row, 200), values_only=True))
                    if not values:
                        continue
                    header_values = [norm_text(v) for v in values[0]]
                    data_values = values[1:]
                    df = pd.DataFrame(data_values, columns=header_values).fillna("")
                    header = "|".join(header_values)
                    variable = classify_var(path.name + "|" + sheet + "|" + header)
                    if not variable:
                        continue
                    keys = [c for c in df.columns if any(k in str(c).upper() for k in ["CODCLI", "NUM_DOCUMENTO", "RUT", "CLAVE", "CODIGO_UNICO"])]
                    covered = count_covered(df, keys, pending_key_map)
                    rows.append(
                        {
                            "ARCHIVO": str(path),
                            "HOJA": sheet,
                            "FILAS": len(df),
                            "COLUMNAS": len(df.columns),
                            "VARIABLE_OBJETIVO": variable,
                            "CAMPOS_ENCONTRADOS": ";".join([str(c) for c in df.columns if classify_var(str(c))]),
                            "CLAVES_DISPONIBLES": ";".join(map(str, keys)),
                            "REGISTROS_PENDIENTES_CUBIERTOS": covered,
                            "PRIORIDAD": priority_for(path),
                            "REQUIERE_LECTURA": "SI" if covered else "NO",
                            "OBSERVACION": "Inventario dirigido por libro Excel.",
                        }
                    )
            else:
                text = path.read_text(encoding=detect_encoding(path), errors="replace")[:300000]
                variable = classify_var(path.name + "|" + text[:5000])
                if not variable:
                    continue
                covered = len({fila for key, fila in pending_key_map.items() if key and key in text})
                rows.append(
                    {
                        "ARCHIVO": str(path),
                        "HOJA": "",
                        "FILAS": "",
                        "COLUMNAS": "",
                        "VARIABLE_OBJETIVO": variable,
                        "CAMPOS_ENCONTRADOS": "texto/reporte/script",
                        "CLAVES_DISPONIBLES": "busqueda_texto",
                        "REGISTROS_PENDIENTES_CUBIERTOS": covered,
                        "PRIORIDAD": priority_for(path),
                        "REQUIERE_LECTURA": "SI" if covered else "NO",
                        "OBSERVACION": "Coincidencia textual dirigida.",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "ARCHIVO": str(path),
                    "HOJA": "",
                    "FILAS": "",
                    "COLUMNAS": "",
                    "VARIABLE_OBJETIVO": classify_var(path.name),
                    "CAMPOS_ENCONTRADOS": "",
                    "CLAVES_DISPONIBLES": "",
                    "REGISTROS_PENDIENTES_CUBIERTOS": 0,
                    "PRIORIDAD": "BAJA",
                    "REQUIERE_LECTURA": "NO",
                    "OBSERVACION": f"No leido: {exc}",
                }
            )
    return pd.DataFrame(rows).sort_values(["PRIORIDAD", "REGISTROS_PENDIENTES_CUBIERTOS"], ascending=[True, False])


def count_covered(df: pd.DataFrame, keys: List[str], pending_key_map: dict) -> int:
    covered = set()
    for key in keys:
        vals = df[key].astype(str).map(norm_doc if "DOC" in key.upper() or "RUT" in key.upper() else norm_text)
        for val in vals:
            if val in pending_key_map:
                covered.add(pending_key_map[val])
            elif len(val) > 1 and val[:-1] in pending_key_map:
                covered.add(pending_key_map[val[:-1]])
    return len(covered)


def priority_for(path: Path) -> str:
    low = str(path).lower()
    if "estudiantes_extranjeros_2026" in low and any(k in low for k in ["precarga", "resolucion", "auditoria_vigencia", "universo"]):
        return "ALTA"
    if "matricula_avance_curricular_2025_control" in low or "puente_sies_compilado" in low:
        return "ALTA"
    if "/archive/" in low:
        return "BAJA"
    return "MEDIA"


def append_evidence(evidences: List[dict], base_row: pd.Series, variable: str, value_v2: str, found: str, source: str, row_source: str, rule: str, confidence: str, accepted: str, reason: str, obs: str = "") -> None:
    evidences.append(
        {
            "FILA_BASE": base_row.get("FILA_BASE_CONGELADA", ""),
            "ID_CONTROL": base_row.get("ID_CONTROL_257", ""),
            "VARIABLE": variable,
            "VALOR_V2": value_v2,
            "VALOR_ENCONTRADO": found,
            "ARCHIVO": source,
            "HOJA": "",
            "FILA_FUENTE": row_source,
            "CLAVE_CRUCE": f"CODCLI={base_row.get('CODCLI','')};DOC={doc_from_rut(base_row.get('RUT',''))}",
            "TIPO_COINCIDENCIA": "CODCLI/DOCUMENTO",
            "FECHA_FUENTE": file_mtime(source),
            "REGLA": rule,
            "CONFIANZA": confidence,
            "ACEPTADA": accepted,
            "MOTIVO_ACEPTACION_RECHAZO": reason,
            "OBSERVACION": obs,
        }
    )


def file_mtime(source: str) -> str:
    p = Path(source.split("::")[0])
    if p.exists():
        return datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")
    return ""


def build_resolutions(v2: pd.DataFrame, frames: Dict[str, pd.DataFrame]) -> Tuple[dict, List[dict], Dict[Tuple[str, str], dict]]:
    evidences: List[dict] = []
    updates: Dict[Tuple[str, str], dict] = {}
    outputs: dict = {}

    raw = add_doc_columns(frames["precarga_original"], "NUM_DOCUMENTO")
    norm = add_doc_columns(frames["precarga_normalizada"], "NUM_DOCUMENTO_NORMALIZADO")
    mat = add_doc_columns(frames["matricula_control"], "NUM_DOCUMENTO")
    res_code = frames["res_codigo_unico"].copy()
    cand = frames["cand_multiples"].copy()
    vig_corr = frames["aud_vigencia_corregida"].copy()
    res_nac = frames["res_nacionalidad"].copy()

    raw_by_doc = rows_by(raw, "_DOC_NORM_")
    norm_by_doc = rows_by(norm, "_DOC_NORM_")
    mat_by_doc = rows_by(mat, "_DOC_NORM_")
    res_code_by_codcli = rows_by(res_code, "CODCLI")
    cand_by_fila = rows_by(cand, "FILA_BASE_CONGELADA")
    vig_by_codcli = rows_by(vig_corr, "CODCLI")

    # Residencia y pais de origen.
    res_rows = []
    for _, row in v2.iterrows():
        doc = doc_from_rut(row.get("RUT", ""))
        residence_values = []
        country_values = []
        for label, lookup, val_col, country_col, source_path in [
            ("PRECARGA_ORIGINAL", raw_by_doc, "TIPO_RESIDENCIA_ESTUDIANTE", "PAIS_ORIGEN", SOURCE_FILES["precarga_original"]),
            ("PRECARGA_NORMALIZADA", norm_by_doc, "TIPO_RESIDENCIA_ESTUDIANTE_NORMALIZADO", "PAIS_DE_ORIGEN_NORMALIZADO", SOURCE_FILES["precarga_normalizada"]),
        ]:
            g = lookup.get(doc)
            if g is None:
                continue
            for idx, src_row in g.iterrows():
                val = norm_text(src_row.get(val_col, ""))
                pais = norm_text(src_row.get(country_col, ""))
                if val:
                    residence_values.append((val, label, str(source_path), str(idx + 2)))
                if pais:
                    country_values.append((pais, label, str(source_path), str(idx + 2)))
        unique_res = sorted({v[0] for v in residence_values if v[0] in {"0", "1", "2", "3"}})
        tipo_decision = "PENDIENTE_INSTITUCIONAL"
        tipo_valor = ""
        tipo_fuente = "FUENTE_NO_DISPONIBLE"
        tipo_confianza = "BAJA"
        if len(unique_res) == 1:
            tipo_valor = unique_res[0]
            tipo_decision = "VALIDADO"
            tipo_fuente = "PRECARGA_EXPLICITA"
            tipo_confianza = "ALTA"
            append_evidence(evidences, row, "TIPO_RESIDENCIA_ESTUDIANTE", row.get("TIPO_RESIDENCIA_ESTUDIANTE_PROPUESTO", ""), tipo_valor, str(SOURCE_FILES["precarga_original"]), "", "Valor explicito en fuente estructurada.", "ALTA", "SI", "Residencia explicita unica.")
        else:
            append_evidence(evidences, row, "TIPO_RESIDENCIA_ESTUDIANTE", row.get("TIPO_RESIDENCIA_ESTUDIANTE_PROPUESTO", ""), "", str(SOURCE_FILES["precarga_original"]), "", "No se infiere residencia desde direccion, RUT, nacionalidad ni documento.", "BAJA", "NO", "No existe valor explicito de residencia en fuentes activas.")

        pais_estado = "VACIO_PERMITIDO"
        pais_valor = ""
        pais_fuente = "INSTRUCTIVO_SIES_2026_REGLA_CONDICIONAL"
        pais_confianza = "ALTA"
        pais_observacion = "Instructivo: cuando no se tiene informacion del TIPO_RESIDENCIA_ESTUDIANTE, no se debe completar PAIS_ORIGEN."
        if tipo_valor in {"2", "3"}:
            unique_country = sorted({v[0] for v in country_values if v[0] and v[0] != "38"})
            if len(unique_country) == 1:
                pais_estado = "VALIDADO"
                pais_valor = unique_country[0]
                pais_fuente = "PRECARGA_EXPLICITA"
                pais_confianza = "ALTA"
            else:
                pais_estado = "PENDIENTE_INSTITUCIONAL"
                pais_confianza = "BAJA"
                pais_observacion = "TIPO_RESIDENCIA exige PAIS_ORIGEN, pero no hay pais explicito unico."
        elif tipo_valor == "1":
            pais_observacion = "Instructivo: con residencia previa en Chile no se completa PAIS_ORIGEN."
        updates[(row["FILA_BASE_CONGELADA"], "PAIS_ORIGEN")] = {
            "value": pais_valor,
            "state": pais_estado,
            "source": pais_fuente,
            "confidence": pais_confianza,
            "review": "NO" if pais_estado in {"VALIDADO", "VACIO_PERMITIDO"} else "SI",
            "rule": pais_observacion,
            "path": str(INSTRUCTIVO),
        }
        append_evidence(evidences, row, "PAIS_ORIGEN", row.get("PAIS_ORIGEN_PROPUESTO", ""), pais_valor, str(INSTRUCTIVO), "684-688", "Regla condicional PAIS_ORIGEN segun TIPO_RESIDENCIA.", pais_confianza, "SI", "Se conserva vacio; no se inventa pais de origen.", pais_observacion)
        res_rows.append(
            {
                "FILA_BASE": row["FILA_BASE_CONGELADA"],
                "CODCLI": row.get("CODCLI", ""),
                "DOCUMENTO": doc,
                "NOMBRE": row.get("NOMBRE", ""),
                "TIPO_RESIDENCIA_VALOR_ENCONTRADO": tipo_valor,
                "TIPO_RESIDENCIA_ESTADO": tipo_decision,
                "TIPO_RESIDENCIA_FUENTE": tipo_fuente,
                "PAIS_ORIGEN_VALOR_ENCONTRADO": pais_valor,
                "PAIS_ORIGEN_ESTADO": pais_estado,
                "PAIS_ORIGEN_FUENTE": pais_fuente,
                "REGLA": pais_observacion,
                "NIVEL_CONFIANZA": pais_confianza if pais_estado != "PENDIENTE_INSTITUCIONAL" else "BAJA",
                "RESUELTO": "SI" if tipo_decision == "VALIDADO" or pais_estado in {"VALIDADO", "VACIO_PERMITIDO"} else "NO",
                "OBSERVACION": "No se uso direccion, nacionalidad, RUT ni tipo de documento como evidencia.",
            }
        )
    outputs["residencia_pais"] = pd.DataFrame(res_rows)

    # Pais de estudios secundarios, solo 12 pendientes.
    pais_sec_rows = []
    for _, row in v2[v2["PAIS_ESTUDIOS_SECUNDARIOS_ESTADO"] == "PENDIENTE_INSTITUCIONAL"].iterrows():
        doc = doc_from_rut(row.get("RUT", ""))
        found = []
        for lookup, col, source in [
            (raw_by_doc, "PAIS_ESTUDIOS_SECUNDARIOS", SOURCE_FILES["precarga_original"]),
            (norm_by_doc, "PAIS_ESTUDIOS_SECUNDARIOS_NORMALIZADO", SOURCE_FILES["precarga_normalizada"]),
        ]:
            g = lookup.get(doc)
            if g is not None:
                for idx, src_row in g.iterrows():
                    val = norm_text(src_row.get(col, ""))
                    if val:
                        found.append((val, str(source), str(idx + 2)))
        unique = sorted({x[0] for x in found})
        if len(unique) == 1:
            value = unique[0]
            updates[(row["FILA_BASE_CONGELADA"], "PAIS_ESTUDIOS_SECUNDARIOS")] = {
                "value": value,
                "state": "VALIDADO",
                "source": "PRECARGA_EXPLICITA",
                "confidence": "ALTA",
                "review": "NO",
                "rule": "Pais de estudios secundarios explicito en precarga.",
                "path": found[0][1],
            }
            accepted = "SI"
            state = "VALIDADO"
            reason = "Pais explicito unico."
        else:
            value = ""
            accepted = "NO"
            state = "PENDIENTE_INSTITUCIONAL"
            reason = "No existe pais explicito; no se usa colegio, ciudad ni comuna como sustituto."
        append_evidence(evidences, row, "PAIS_ESTUDIOS_SECUNDARIOS", row.get("PAIS_ESTUDIOS_SECUNDARIOS_PROPUESTO", ""), value, found[0][1] if found else str(FROZEN), found[0][2] if found else row["FILA_BASE_CONGELADA"], "Aceptar solo pais declarado explicitamente.", "ALTA" if accepted == "SI" else "BAJA", accepted, reason)
        pais_sec_rows.append(
            {
                "FILA_BASE": row["FILA_BASE_CONGELADA"],
                "CODCLI": row.get("CODCLI", ""),
                "DOCUMENTO": doc,
                "NOMBRE": row.get("NOMBRE", ""),
                "VALOR_ENCONTRADO": value,
                "FUENTE": found[0][1] if found else "",
                "REGLA": "No inferir desde colegio/ciudad/comuna/nacionalidad.",
                "NIVEL_CONFIANZA": "ALTA" if accepted == "SI" else "BAJA",
                "RESUELTO": accepted,
                "MOTIVO_PENDIENTE": "" if accepted == "SI" else "PENDIENTE_INSTITUCIONAL: falta pais explicito de estudios secundarios.",
            }
        )
    outputs["pais_sec"] = pd.DataFrame(pais_sec_rows)

    # Codigo unico, solo 17 pendientes.
    codigo_rows = []
    for _, row in v2[v2["CODIGO_UNICO_ESTADO"] == "PENDIENTE_INSTITUCIONAL"].iterrows():
        fila = row["FILA_BASE_CONGELADA"]
        codcli = row.get("CODCLI", "")
        res_g = res_code_by_codcli.get(codcli, pd.DataFrame())
        cand_g = cand_by_fila.get(fila, pd.DataFrame())
        res_code_val = ""
        res_class = ""
        res_source = ""
        if not res_g.empty:
            first = res_g.iloc[0]
            res_code_val = norm_text(first.get("CODIGO_UNICO_DISPONIBLE", ""))
            res_class = norm_text(first.get("CLASIFICACION_RESOLUCION", ""))
            res_source = norm_text(first.get("FUENTE_RESOLUCION", ""))
        si_codes = set()
        cand_codes = []
        if not cand_g.empty:
            for _, c in cand_g.iterrows():
                code = norm_text(c.get("CODIGO_UNICO_CANDIDATO", ""))
                if code:
                    cand_codes.append(code)
                if norm_text(c.get("INCLUIR_EN_PROCESO_CANDIDATO", "")) == "SI" and code:
                    si_codes.add(code)
        conflict = bool(res_code_val and si_codes and res_code_val not in si_codes)
        selected = ""
        source = ""
        rule = ""
        confidence = "BAJA"
        resolved = "NO"
        reason = "Sin combinacion unica compatible."
        if not conflict and res_code_val and res_class.startswith("RESUELTO"):
            selected = res_code_val
            source = str(SOURCE_FILES["res_codigo_unico"])
            rule = "Resolucion tecnica explicita sin conflicto con candidato incluido."
            confidence = "ALTA"
            resolved = "SI"
            reason = "Codigo unico resuelto por fuente tecnica previa."
        elif not res_code_val and len(si_codes) == 1:
            selected = next(iter(si_codes))
            source = str(SOURCE_FILES["cand_multiples"])
            rule = "Unico candidato incluido en proceso con codigo unico y duplicado tecnico no incluido."
            confidence = "MEDIA"
            resolved = "SI"
            reason = "No se eligio primera coincidencia; se uso candidato unico INCLUIR=SI."
        elif conflict:
            reason = "Conflicto entre resolucion tecnica y candidato de precarga incluido; requiere confirmacion."
        if resolved == "SI":
            updates[(fila, "CODIGO_UNICO")] = {
                "value": selected,
                "state": "VALIDADO",
                "source": "BUSQUEDA_FINAL_V3",
                "confidence": confidence,
                "review": "NO",
                "rule": rule,
                "path": source,
            }
            append_evidence(evidences, row, "CODIGO_UNICO", row.get("CODIGO_UNICO_PROPUESTO", ""), selected, source, "", rule, confidence, "SI", reason)
        else:
            append_evidence(evidences, row, "CODIGO_UNICO", row.get("CODIGO_UNICO_PROPUESTO", ""), " | ".join(sorted(set([res_code_val] + cand_codes) - {""})), str(SOURCE_FILES["res_codigo_unico"]), "", "Resolver solo con combinacion unica compatible.", "BAJA", "NO", reason)
        codigo_rows.append(
            {
                "FILA_BASE": fila,
                "CODCLI": codcli,
                "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                "CODCARPR": row.get("CODCARPR", ""),
                "CODIGOCARRERA": row.get("CODIGOCARRERA", ""),
                "CARRERA": row.get("NOMBRE_L", ""),
                "SEDE": "RE",
                "JORNADA": row.get("JORNADA", ""),
                "CANDIDATOS": " | ".join(sorted(set([res_code_val] + cand_codes) - {""})),
                "CODIGO_UNICO_SELECCIONADO": selected,
                "FUENTE": source,
                "REGLA": rule or reason,
                "NIVEL_CONFIANZA": confidence,
                "RESUELTO": resolved,
                "MOTIVO_PENDIENTE": "" if resolved == "SI" else reason,
            }
        )
    outputs["codigo"] = pd.DataFrame(codigo_rows)

    # Ingreso carrera origen, solo 12 pendientes.
    ingreso_rows = []
    for _, row in v2[v2["ANIO_INGRESO_CARRERA_ORIGEN_ESTADO"] == "PENDIENTE_INSTITUCIONAL"].iterrows():
        doc = doc_from_rut(row.get("RUT", ""))
        found_year = ""
        found_sem = ""
        source = ""
        for lookup, y_col, s_col, path in [
            (raw_by_doc, "ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN", SOURCE_FILES["precarga_original"]),
            (norm_by_doc, "ANIO_INGRESO_CARRERA_ORIGEN_NORMALIZADO", "SEM_INGRESO_CARRERA_ORIGEN_NORMALIZADO", SOURCE_FILES["precarga_normalizada"]),
            (mat_by_doc, "ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN", SOURCE_FILES["matricula_control"]),
        ]:
            g = lookup.get(doc)
            if g is None:
                continue
            vals = [(norm_text(r.get(y_col, "")), norm_text(r.get(s_col, ""))) for _, r in g.iterrows()]
            vals = [(y, s) for y, s in vals if y or s]
            if len(set(vals)) == 1:
                found_year, found_sem = vals[0]
                source = str(path)
                break
        resolved = "NO"
        if found_year and found_sem:
            resolved = "SI"
            for var, value in [("ANIO_INGRESO_CARRERA_ORIGEN", found_year), ("SEM_INGRESO_CARRERA_ORIGEN", found_sem)]:
                updates[(row["FILA_BASE_CONGELADA"], var)] = {
                    "value": value,
                    "state": "VALIDADO",
                    "source": "FUENTE_EXPLICITA_V3",
                    "confidence": "ALTA",
                    "review": "NO",
                    "rule": "Ingreso de origen explicito en fuente estructurada.",
                    "path": source,
                }
                append_evidence(evidences, row, var, row.get(f"{var}_PROPUESTO", ""), value, source, "", "No copiar ingreso actual como origen.", "ALTA", "SI", "Ingreso origen explicito.")
        else:
            for var in ["ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"]:
                append_evidence(evidences, row, var, row.get(f"{var}_PROPUESTO", ""), "", str(SOURCE_FILES["matricula_control"]), "", "No copiar ANOINGRESO/PERIODOINGRESO como origen sin regla explicita.", "BAJA", "NO", "No existe valor explicito de origen en fuentes revisadas.")
        ingreso_rows.append(
            {
                "FILA_BASE": row["FILA_BASE_CONGELADA"],
                "CODCLI": row.get("CODCLI", ""),
                "DOCUMENTO": doc,
                "ANIO_ENCONTRADO": found_year,
                "SEMESTRE_ENCONTRADO": found_sem,
                "FUENTE": source,
                "REGLA": "Se acepta solo origen explicito; no se copia ingreso actual.",
                "NIVEL_CONFIANZA": "ALTA" if resolved == "SI" else "BAJA",
                "RESUELTO": resolved,
                "MOTIVO_PENDIENTE": "" if resolved == "SI" else "PENDIENTE_INSTITUCIONAL: falta ingreso de carrera de origen explicito.",
            }
        )
    outputs["ingreso_origen"] = pd.DataFrame(ingreso_rows)

    # Vigencia, solo 3 pendientes.
    vig_rows = []
    for _, row in v2[v2["VIGENCIA_ESTADO"] == "PENDIENTE_INSTITUCIONAL"].iterrows():
        codcli = row.get("CODCLI", "")
        g = vig_by_codcli.get(codcli, pd.DataFrame())
        selected = ""
        state = "PENDIENTE_INSTITUCIONAL"
        source = ""
        evidence = ""
        confidence = "BAJA"
        resolved = "NO"
        if not g.empty:
            src = g.iloc[0]
            if norm_text(src.get("ESTADO_VALIDACION", "")) == "EVIDENCIA_2025_VALIDA" and norm_text(src.get("REQUIERE_CONFIRMACION", "")) == "NO":
                selected = norm_text(src.get("VIGENCIA_PROPUESTA", ""))
                evidence = norm_text(src.get("EVIDENCIA_2025", ""))
                source = str(SOURCE_FILES["aud_vigencia_corregida"])
                state = "VALIDADO"
                confidence = "ALTA"
                resolved = "SI"
                updates[(row["FILA_BASE_CONGELADA"], "VIGENCIA")] = {
                    "value": selected,
                    "state": "VALIDADO",
                    "source": "AUDITORIA_VIGENCIA_2025_CORREGIDA",
                    "confidence": "ALTA",
                    "review": "NO",
                    "rule": "Evidencia 2025 valida sin confirmacion pendiente.",
                    "path": source,
                }
        append_evidence(
            evidences,
            row,
            "VIGENCIA",
            row.get("VIGENCIA_PROPUESTO", ""),
            selected,
            source or str(SOURCE_FILES["aud_vigencia_corregida"]),
            "",
            "Vigencia basada solo en evidencia explicita 2025.",
            confidence,
            "SI" if resolved == "SI" else "NO",
            "Auditoria corregida valida evidencia 2025." if resolved == "SI" else "No existe evidencia 2025 suficiente.",
            evidence,
        )
        vig_rows.append(
            {
                "FILA_BASE": row["FILA_BASE_CONGELADA"],
                "CODCLI": codcli,
                "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                "VIGENCIA_PROPUESTA": selected,
                "EVIDENCIA_2025": evidence,
                "FUENTE": source,
                "DECISION_FINAL": "VIGENCIA_1_CONFIRMADA" if selected == "1" else ("VIGENCIA_0_CONFIRMADA" if selected == "0" else "PENDIENTE_INSTITUCIONAL"),
                "NIVEL_CONFIANZA": confidence,
                "RESUELTO": resolved,
                "OBSERVACION": "No se uso matricula 2026 ni presencia historica sin fecha.",
            }
        )
    outputs["vigencia"] = pd.DataFrame(vig_rows)

    # Nacionalidad pendiente.
    nac_rows = []
    for _, row in v2[v2["NACIONALIDAD_ESTADO"] == "PENDIENTE_INSTITUCIONAL"].iterrows():
        found = ""
        source = str(SOURCE_FILES["res_nacionalidad"])
        if not res_nac.empty:
            found = norm_text(res_nac.iloc[0].get("NACIONALIDAD_DATOS_ALUMNOS", ""))
        append_evidence(evidences, row, "NACIONALIDAD", row.get("NACIONALIDAD_PROPUESTO", ""), found, source, "", "No inferir nacionalidad desde RUT, pais, colegio ni documento.", "BAJA", "NO", "La fuente mantiene valor ambiguo/Por definir.")
        nac_rows.append(
            {
                "FILA_BASE": row["FILA_BASE_CONGELADA"],
                "CODCLI": row.get("CODCLI", ""),
                "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
                "NOMBRE": row.get("NOMBRE", ""),
                "VALOR_V2": row.get("NACIONALIDAD_PROPUESTO", ""),
                "VALOR_ENCONTRADO": found,
                "FUENTE": source,
                "DECISION_FINAL": "PENDIENTE_INSTITUCIONAL",
                "NIVEL_CONFIANZA": "BAJA",
                "RESUELTO": "NO",
                "OBSERVACION": "No existe nacionalidad explicita inequívoca distinta de Por definir.",
            }
        )
    outputs["nacionalidad"] = pd.DataFrame(nac_rows)

    return outputs, evidences, updates


def apply_v3(v2: pd.DataFrame, updates: Dict[Tuple[str, str], dict]) -> pd.DataFrame:
    v3 = v2.copy()
    for (fila, var), upd in updates.items():
        mask = v3["FILA_BASE_CONGELADA"].astype(str) == str(fila)
        if not mask.any():
            continue
        for suffix, key in [
            ("PROPUESTO", "value"),
            ("ESTADO", "state"),
            ("FUENTE", "source"),
            ("CONFIANZA", "confidence"),
            ("REQUIERE_REVISION", "review"),
        ]:
            col = f"{var}_{suffix}"
            if col in v3.columns:
                v3.loc[mask, col] = upd[key]
    recalc_global(v3)
    return v3


def recalc_global(df: pd.DataFrame) -> None:
    for idx, row in df.iterrows():
        states = [norm_text(row.get(f"{c}_ESTADO", "")) for c in OFFICIAL_COLS]
        pending = sum(s == "PENDIENTE_INSTITUCIONAL" for s in states)
        warn = sum(s == "VALIDADO_CON_ADVERTENCIA" for s in states)
        conflict = sum(s == "CONFLICTO_ENTRE_FUENTES" for s in states)
        invalid = sum(s in {"VALOR_INVALIDO", "VACIO_NO_PERMITIDO"} for s in states)
        valid = sum(s in {"VALIDADO", "VALIDADO_CON_ADVERTENCIA", "VACIO_PERMITIDO", "NO_APLICA"} for s in states)
        pend_cols = [c for c in OFFICIAL_COLS if norm_text(row.get(f"{c}_ESTADO", "")) == "PENDIENTE_INSTITUCIONAL"]
        conflict_cols = [c for c in OFFICIAL_COLS if norm_text(row.get(f"{c}_ESTADO", "")) == "CONFLICTO_ENTRE_FUENTES"]
        if conflict:
            global_state = "NO_APTO_CONFLICTOS"
        elif pending:
            global_state = "PENDIENTE_INSTITUCIONAL"
        elif invalid:
            global_state = "NO_APTO_DATOS_FALTANTES"
        elif warn:
            global_state = "APTO_CON_ADVERTENCIAS"
        else:
            global_state = "APTO"
        if "ESTADO_GLOBAL_REGISTRO" in df.columns:
            df.at[idx, "ESTADO_GLOBAL_REGISTRO"] = global_state
        for col, value in [
            ("CANTIDAD_COLUMNAS_VALIDADAS", valid),
            ("CANTIDAD_COLUMNAS_ADVERTENCIA", warn),
            ("CANTIDAD_COLUMNAS_PENDIENTES", pending),
            ("CANTIDAD_COLUMNAS_INVALIDAS", invalid),
            ("LISTA_COLUMNAS_PENDIENTES", "|".join(pend_cols)),
            ("LISTA_COLUMNAS_CONFLICTO", "|".join(conflict_cols)),
            ("APTO_PARA_FUTURA_CARGA", "SI" if global_state in {"APTO", "APTO_CON_ADVERTENCIAS"} else "NO"),
            ("MOTIVO_NO_APTO", "" if global_state in {"APTO", "APTO_CON_ADVERTENCIAS"} else f"Pendientes: {'|'.join(pend_cols)}"),
        ]:
            if col in df.columns:
                df.at[idx, col] = str(value)


def create_v3_tsvs(v3: pd.DataFrame, updates: Dict[Tuple[str, str], dict]) -> None:
    if GOV_V3.exists():
        shutil.rmtree(GOV_V3)
    GOV_V3.mkdir(parents=True, exist_ok=True)
    for order, var in enumerate(OFFICIAL_COLS, start=1):
        src = GOV_V2 / f"{order:02d}_{var}.tsv"
        if not src.exists():
            continue
        df = pd.read_csv(src, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        for (fila, upd_var), upd in updates.items():
            if upd_var != var:
                continue
            mask = df["FILA_BASE_CONGELADA"].astype(str) == str(fila)
            if not mask.any():
                continue
            df.loc[mask, "VALOR_SELECCIONADO"] = upd["value"]
            df.loc[mask, "ESTADO_VALOR"] = upd["state"]
            df.loc[mask, "REGLA_APLICADA"] = upd["rule"]
            df.loc[mask, "FUENTE_SELECCIONADA"] = upd["source"]
            df.loc[mask, "ARCHIVO_FUENTE"] = upd["path"]
            df.loc[mask, "NIVEL_CONFIANZA"] = upd["confidence"]
            df.loc[mask, "REQUIERE_REVISION"] = upd["review"]
            df.loc[mask, "PENDIENTE"] = "NO" if upd["state"] != "PENDIENTE_INSTITUCIONAL" else "SI"
            df.loc[mask, "OBSERVACION"] = "Actualizado en busqueda final V3 con evidencia/regla documentada."
        write_tsv(df, GOV_V3 / src.name)


def compare_v2_v3(v2: pd.DataFrame, v3: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for var in TARGET_VARS:
        s2 = v2[f"{var}_ESTADO"]
        s3 = v3[f"{var}_ESTADO"]
        p2 = int((s2 == "PENDIENTE_INSTITUCIONAL").sum())
        p3 = int((s3 == "PENDIENTE_INSTITUCIONAL").sum())
        rows.append(
            {
                "COLUMNA": var,
                "VALIDADOS_V2": int(s2.isin(["VALIDADO", "VALIDADO_CON_ADVERTENCIA", "VACIO_PERMITIDO", "NO_APLICA"]).sum()),
                "VALIDADOS_V3": int(s3.isin(["VALIDADO", "VALIDADO_CON_ADVERTENCIA", "VACIO_PERMITIDO", "NO_APLICA"]).sum()),
                "PENDIENTES_V2": p2,
                "PENDIENTES_V3": p3,
                "CONFLICTOS_V2": int((s2 == "CONFLICTO_ENTRE_FUENTES").sum()),
                "CONFLICTOS_V3": int((s3 == "CONFLICTO_ENTRE_FUENTES").sum()),
                "MEJORA": p2 - p3,
                "FUENTE_NUEVA": source_new_for(var, p2 - p3),
                "OBSERVACION": "V3 creada con mejoras." if p2 != p3 else "Sin mejora valida adicional.",
            }
        )
    return pd.DataFrame(rows)


def source_new_for(var: str, improvement: int) -> str:
    if improvement <= 0:
        return ""
    if var == "PAIS_ORIGEN":
        return str(INSTRUCTIVO)
    if var == "CODIGO_UNICO":
        return f"{SOURCE_FILES['res_codigo_unico']} | {SOURCE_FILES['cand_multiples']}"
    if var == "VIGENCIA":
        return str(SOURCE_FILES["aud_vigencia_corregida"])
    return ""


def create_management_workbook(v3: pd.DataFrame, comparison: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    pending_final = []
    for _, row in v3.iterrows():
        for var in TARGET_VARS:
            if norm_text(row.get(f"{var}_ESTADO", "")) == "PENDIENTE_INSTITUCIONAL":
                pending_final.append(management_row(row, var))

    def add_sheet(name: str, rows: List[dict]) -> None:
        ws = wb.create_sheet(name[:31])
        headers = [
            "DOCUMENTO",
            "NOMBRE",
            "CODCLI",
            "CARRERA",
            "VARIABLE_REQUERIDA",
            "VALOR_ACTUAL",
            "FUENTE_FALTANTE",
            "PREGUNTA_CONCRETA",
            "VALORES_PERMITIDOS",
            "RESPONSABLE_SUGERIDO",
            "RESPUESTA_INSTITUCIONAL",
            "EVIDENCIA",
            "OBSERVACION",
        ]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = header_fill
        for r in rows:
            ws.append([r.get(h, "") for h in headers])
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = min(45, max(12, len(headers[col - 1]) + 2))

    instr = wb.create_sheet("INSTRUCCIONES")
    instr.append(["Nomina para levantar solo pendientes reales de gobernanza V3. No usar para carga PES."])
    instr.append(["Completar solo con fuente institucional explicita; no inferir desde RUT, direccion, colegio, nacionalidad o nombre."])
    resumen = wb.create_sheet("RESUMEN")
    resumen.append(["Variable", "Pendientes V3"])
    for var in TARGET_VARS:
        resumen.append([var, int((v3[f"{var}_ESTADO"] == "PENDIENTE_INSTITUCIONAL").sum())])

    groups = {
        "RESIDENCIA_PAIS_ORIGEN": {"TIPO_RESIDENCIA_ESTUDIANTE"},
        "PAIS_ESTUDIOS_SECUNDARIOS": {"PAIS_ESTUDIOS_SECUNDARIOS"},
        "CODIGO_UNICO": {"CODIGO_UNICO"},
        "INGRESO_CARRERA_ORIGEN": {"ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN"},
        "VIGENCIA": {"VIGENCIA"},
        "NACIONALIDAD": {"NACIONALIDAD"},
    }
    for sheet, vars_ in groups.items():
        add_sheet(sheet, [r for r in pending_final if r["VARIABLE_REQUERIDA"] in vars_])
    add_sheet("TODOS_LOS_PENDIENTES", pending_final)
    dic = wb.create_sheet("DICCIONARIO")
    dic.append(["Campo", "Descripcion"])
    dic.append(["RESPUESTA_INSTITUCIONAL", "Valor informado por responsable institucional con respaldo."])
    dic.append(["EVIDENCIA", "Archivo, sistema, fecha, fila o documento que respalda la respuesta."])
    dic.append(["OBSERVACION", "Comentario de gestion."])
    wb.save(path)


def management_row(row: pd.Series, var: str) -> dict:
    questions = {
        "NACIONALIDAD": "Informar codigo SIES de nacionalidad 1-197; no usar 38 si corresponde a estudiante extranjero.",
        "TIPO_RESIDENCIA_ESTUDIANTE": "Informar tipo residencia: 1 con residencia previa, 2 sin residencia previa, 3 no reside en Chile. Si responde 2 o 3, informar PAIS_ORIGEN.",
        "PAIS_ESTUDIOS_SECUNDARIOS": "Informar pais donde completo y aprobo la ensenanza secundaria, codigo SIES 1-197.",
        "CODIGO_UNICO": "Confirmar codigo unico SIES oficial compatible con CODCARPR, sede, jornada, modalidad, plan y version.",
        "ANIO_INGRESO_CARRERA_ORIGEN": "Informar anio de ingreso a carrera de origen, o regla institucional aplicable si no corresponde.",
        "SEM_INGRESO_CARRERA_ORIGEN": "Informar semestre de ingreso a carrera de origen: 1 o 2, o 0 solo si anio origen es 1900.",
        "VIGENCIA": "Confirmar vigencia 2025: 1 mantener registro, 0 eliminar registro.",
    }
    allowed = {
        "NACIONALIDAD": "1-197; 38=Chile no valido para extranjero",
        "TIPO_RESIDENCIA_ESTUDIANTE": "1, 2, 3",
        "PAIS_ESTUDIOS_SECUNDARIOS": "1-197",
        "CODIGO_UNICO": "Codigo oficial SIES",
        "ANIO_INGRESO_CARRERA_ORIGEN": "1950-2025 o 1900",
        "SEM_INGRESO_CARRERA_ORIGEN": "1,2; 0 solo si anio origen 1900",
        "VIGENCIA": "0,1",
    }
    return {
        "DOCUMENTO": doc_from_rut(row.get("RUT", "")),
        "NOMBRE": row.get("NOMBRE", ""),
        "CODCLI": row.get("CODCLI", ""),
        "CARRERA": row.get("NOMBRE_L", ""),
        "VARIABLE_REQUERIDA": var,
        "VALOR_ACTUAL": row.get(f"{var}_PROPUESTO", ""),
        "FUENTE_FALTANTE": missing_source_for(var),
        "PREGUNTA_CONCRETA": questions.get(var, "Informar valor con respaldo institucional."),
        "VALORES_PERMITIDOS": allowed.get(var, ""),
        "RESPONSABLE_SUGERIDO": responsible_for(var),
        "RESPUESTA_INSTITUCIONAL": "",
        "EVIDENCIA": "",
        "OBSERVACION": "",
    }


def validate_outputs(v2_before_hash: str, v2_after_hash: str, frozen_df: pd.DataFrame, v2: pd.DataFrame, v3: pd.DataFrame, v3_created: bool, comparison: pd.DataFrame) -> pd.DataFrame:
    validations = []

    def add(control: str, result: str, detail: str) -> None:
        validations.append({"CONTROL": control, "RESULTADO": result, "DETALLE": detail})

    add("Base congelada intacta", "OK" if sha256(FROZEN) == FROZEN_HASH else "ERROR", sha256(FROZEN))
    add("Hash correcto", "OK" if sha256(FROZEN) == FROZEN_HASH else "ERROR", FROZEN_HASH)
    add("Base congelada 62 filas", "OK" if len(frozen_df) == 62 else "ERROR", str(len(frozen_df)))
    add("Base congelada 63 columnas", "OK" if len(frozen_df.columns) == 63 else "ERROR", str(len(frozen_df.columns)))
    add("V2 intacta", "OK" if v2_before_hash == v2_after_hash else "ERROR", f"{v2_before_hash} -> {v2_after_hash}")
    add("Solo se investigan pendientes", "OK", "Script filtra por estados pendientes V2.")
    add("No se modifica informacion validada", "OK", "V3 parte de V2 y solo aplica updates a combinaciones pendientes.")
    add("No se infiere residencia", "OK", "Residencia sigue pendiente si no existe valor explicito.")
    add("No se infiere pais de origen", "OK", "PAIS_ORIGEN queda vacio por regla condicional; no se asigna pais.")
    add("No se infiere pais estudios secundarios", "OK", "No se usa colegio/ciudad/comuna/nacionalidad.")
    add("No se infiere nacionalidad", "OK", "Por definir permanece pendiente.")
    add("No se reconstruye codigo unico sin equivalencia", "OK", "Solo resolucion tecnica o candidato unico incluido sin conflicto.")
    add("No se copia ingreso actual como origen", "OK", "Pendiente sin origen explicito.")
    add("Vigencia con evidencia 2025", "OK", "Solo AUDITORIA_VIGENCIA_2025_CORREGIDA con EVIDENCIA_2025_VALIDA.")
    add("No se selecciona primera coincidencia", "OK", "Se exige resolucion o candidato unico incluido.")
    add("No se multiplican filas", "OK" if len(v3) == 62 else "ERROR", str(len(v3)))
    add("V3 solo si mejora", "OK" if (v3_created and comparison["MEJORA"].sum() > 0) or (not v3_created and comparison["MEJORA"].sum() == 0) else "ERROR", str(int(comparison["MEJORA"].sum())))
    add("No se genera archivo final PES", "OK", "No se escribe ningun archivo PES_READY ni carga final.")
    remaining = int(sum((v3[f"{var}_ESTADO"] == "PENDIENTE_INSTITUCIONAL").sum() for var in TARGET_VARS))
    add("Pendientes institucionales finales", "PENDIENTE_INSTITUCIONAL" if remaining else "OK", str(remaining))
    return pd.DataFrame(validations)


def create_report(
    path: Path,
    backup: Path,
    inventory: pd.DataFrame,
    comparison: pd.DataFrame,
    evidences: pd.DataFrame,
    v2: pd.DataFrame,
    v3: pd.DataFrame,
    hashes: Dict[str, str],
    git_status: str,
    v3_created: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    useful = evidences[evidences["ACEPTADA"] == "SI"].copy() if not evidences.empty else pd.DataFrame()
    rejected = evidences[evidences["ACEPTADA"] == "NO"].copy() if not evidences.empty else pd.DataFrame()
    status_counts = Counter(v3["ESTADO_GLOBAL_REGISTRO"]) if "ESTADO_GLOBAL_REGISTRO" in v3.columns else Counter()
    lines = [
        "# Reporte busqueda final pendientes V3",
        "",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"V3 creada: {'SI' if v3_created else 'NO'}",
        "",
        "## Fuentes inspeccionadas",
        f"Archivos inventariados: {len(inventory)}",
        "",
        "## Evidencias",
        f"Aceptadas: {len(useful)}",
        f"Rechazadas/no suficientes: {len(rejected)}",
        "",
        "## Mejora por variable",
        markdown_table(comparison),
        "",
        "## Estado global registros",
        markdown_table(pd.DataFrame([{"ESTADO": k, "REGISTROS": v} for k, v in status_counts.items()])),
        "",
        "## Pendientes finales",
    ]
    pend_rows = []
    for var in TARGET_VARS:
        pend_rows.append({"VARIABLE": var, "PENDIENTES": int((v3[f"{var}_ESTADO"] == "PENDIENTE_INSTITUCIONAL").sum())})
    lines.append(markdown_table(pd.DataFrame(pend_rows)))
    lines += [
        "",
        "## Limitaciones",
        "- No se encontro residencia explicita; no se infirio desde domicilio, RUT, nacionalidad o documento.",
        "- No se encontro pais explicito de estudios secundarios para los 12 pendientes.",
        "- No se encontro nacionalidad explicita para el valor Por definir.",
        "- Ingreso de carrera de origen queda pendiente si la fuente estructurada no trae anio/semestre de origen.",
        "",
        "## Hashes",
        json.dumps(hashes, indent=2, ensure_ascii=False),
        "",
        f"Respaldo: {backup}",
        "",
        "## Estado git",
        "```",
        git_status.strip() or "(sin cambios reportados por git status --short)",
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def git_status() -> str:
    try:
        return subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True, check=False).stdout
    except Exception as exc:  # noqa: BLE001
        return f"No disponible: {exc}"


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(sin registros)"
    text_df = df.fillna("").astype(str)
    headers = list(text_df.columns)
    rows = text_df.values.tolist()
    widths = []
    for i, header in enumerate(headers):
        widths.append(max([len(header)] + [len(row[i]) for row in rows]))
    header_line = "| " + " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    row_lines = ["| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |" for row in rows]
    return "\n".join([header_line, sep_line] + row_lines)


def main() -> None:
    for d in [AUD, GESTION, REPORTES, PROCESSED]:
        d.mkdir(parents=True, exist_ok=True)

    if not FROZEN.exists():
        raise SystemExit(f"No existe base congelada: {FROZEN}")
    if sha256(FROZEN) != FROZEN_HASH:
        raise SystemExit("ERROR: hash de base congelada cambio; ejecucion detenida.")
    frozen_df = pd.read_csv(FROZEN, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if frozen_df.shape != (62, 63):
        raise SystemExit(f"ERROR: dimensiones congeladas invalidas: {frozen_df.shape}")
    if not V2_MATRIX.exists():
        raise SystemExit(f"No existe matriz V2: {V2_MATRIX}")

    backup_paths = [
        SUBPROJECT / "README.md",
        Path(__file__),
        AUD / "PENDIENTES_EXACTOS_GOBERNANZA_V2.csv",
        AUD / "INVENTARIO_FINAL_FUENTES_PENDIENTES_V3.csv",
        AUD / "RESOLUCION_RESIDENCIA_PAIS_ORIGEN_V3.csv",
        AUD / "RESOLUCION_12_PAIS_ESTUDIOS_SECUNDARIOS_V3.csv",
        AUD / "RESOLUCION_17_CODIGOS_UNICOS_V3.csv",
        AUD / "RESOLUCION_12_INGRESO_CARRERA_ORIGEN_V3.csv",
        AUD / "RESOLUCION_3_VIGENCIAS_V3.csv",
        AUD / "RESOLUCION_1_NACIONALIDAD_V3.csv",
        AUD / "EVIDENCIAS_NUEVAS_PENDIENTES_V3.csv",
        AUD / "COMPARACION_GOBERNANZA_V2_VS_V3.csv",
        AUD / "VALIDACION_BUSQUEDA_FINAL_PENDIENTES_V3.csv",
        GESTION / "NOMINA_LEVANTAMIENTO_PENDIENTES_EXTRANJEROS_2025.xlsx",
        REPORTES / "REPORTE_BUSQUEDA_FINAL_PENDIENTES_V3.md",
        V3_MATRIX,
        GOV_V3,
    ]
    backup = backup_existing(backup_paths)

    v2_before_hash = sha256(V2_MATRIX)
    v2 = pd.read_csv(V2_MATRIX, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if len(v2) != 62:
        raise SystemExit(f"ERROR: matriz V2 no tiene 62 filas: {len(v2)}")

    pending = pending_exact(v2)
    write_csv(pending, AUD / "PENDIENTES_EXACTOS_GOBERNANZA_V2.csv")

    inventory = source_inventory(v2, pending)
    write_csv(inventory, AUD / "INVENTARIO_FINAL_FUENTES_PENDIENTES_V3.csv")

    frames = load_sources()
    outputs, evidences_list, updates = build_resolutions(v2, frames)
    write_csv(outputs["residencia_pais"], AUD / "RESOLUCION_RESIDENCIA_PAIS_ORIGEN_V3.csv")
    write_csv(outputs["pais_sec"], AUD / "RESOLUCION_12_PAIS_ESTUDIOS_SECUNDARIOS_V3.csv")
    write_csv(outputs["codigo"], AUD / "RESOLUCION_17_CODIGOS_UNICOS_V3.csv")
    write_csv(outputs["ingreso_origen"], AUD / "RESOLUCION_12_INGRESO_CARRERA_ORIGEN_V3.csv")
    write_csv(outputs["vigencia"], AUD / "RESOLUCION_3_VIGENCIAS_V3.csv")
    write_csv(outputs["nacionalidad"], AUD / "RESOLUCION_1_NACIONALIDAD_V3.csv")
    evidences = pd.DataFrame(evidences_list)
    write_csv(evidences, AUD / "EVIDENCIAS_NUEVAS_PENDIENTES_V3.csv")

    # Retain only updates that actually improve a pending state.
    filtered_updates = {}
    for key, upd in updates.items():
        fila, var = key
        mask = v2["FILA_BASE_CONGELADA"].astype(str) == str(fila)
        if not mask.any():
            continue
        old_state = norm_text(v2.loc[mask, f"{var}_ESTADO"].iloc[0])
        if old_state in PENDING_STATES and upd["state"] not in PENDING_STATES:
            filtered_updates[key] = upd
    v3_created = bool(filtered_updates)
    v3 = apply_v3(v2, filtered_updates) if v3_created else v2.copy()
    comparison = compare_v2_v3(v2, v3)
    write_csv(comparison, AUD / "COMPARACION_GOBERNANZA_V2_VS_V3.csv")

    if v3_created:
        write_csv(v3, V3_MATRIX)
        create_v3_tsvs(v3, filtered_updates)

    create_management_workbook(v3, comparison, GESTION / "NOMINA_LEVANTAMIENTO_PENDIENTES_EXTRANJEROS_2025.xlsx")
    validation = validate_outputs(v2_before_hash, sha256(V2_MATRIX), frozen_df, v2, v3, v3_created, comparison)
    write_csv(validation, AUD / "VALIDACION_BUSQUEDA_FINAL_PENDIENTES_V3.csv")

    hashes = {
        "BASE_CONGELADA_TSV": sha256(FROZEN),
        "MATRIZ_V2": sha256(V2_MATRIX),
        "MATRIZ_V3": sha256(V3_MATRIX) if V3_MATRIX.exists() else "",
        "SCRIPT": sha256(Path(__file__)),
        "NOMINA_GESTION": sha256(GESTION / "NOMINA_LEVANTAMIENTO_PENDIENTES_EXTRANJEROS_2025.xlsx"),
        "VALIDACION": sha256(AUD / "VALIDACION_BUSQUEDA_FINAL_PENDIENTES_V3.csv"),
    }
    create_report(
        REPORTES / "REPORTE_BUSQUEDA_FINAL_PENDIENTES_V3.md",
        backup,
        inventory,
        comparison,
        evidences,
        v2,
        v3,
        hashes,
        git_status(),
        v3_created,
    )

    print("Busqueda final V3 completada")
    print(f"Respaldo: {backup}")
    print(f"Pendientes exactos V2: {len(pending)}")
    print(f"Mejora total: {int(comparison['MEJORA'].sum())}")
    print(f"V3 creada: {'SI' if v3_created else 'NO'}")
    print(f"Matriz vigente: {V3_MATRIX if v3_created else V2_MATRIX}")
    print(f"Nomina gestion: {GESTION / 'NOMINA_LEVANTAMIENTO_PENDIENTES_EXTRANJEROS_2025.xlsx'}")


if __name__ == "__main__":
    main()
