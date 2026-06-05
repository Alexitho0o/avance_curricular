"""Hito 4 CNED: auditar base operativa preliminar para pre-subida.

Audita profundamente la base recomendada por Hito 3, identifica la hoja
principal, perfila columnas, valida registros y genera una base operativa
auditada segmentada. No declara carga definitiva CNED.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover
    raise SystemExit("ERROR: falta pandas para ejecutar Hito 4 CNED.") from exc

try:
    from openpyxl import load_workbook
except ImportError as exc:  # pragma: no cover
    raise SystemExit("ERROR: falta openpyxl para ejecutar Hito 4 CNED.") from exc


LOGGER = logging.getLogger("hito4_cned")

BASE_RELATIVE = Path(
    "cned/data/input/recuperacion_controlada/"
    "01__CNED_ARCHIVO_OPERATIVO_TRABAJO_MANUAL_FINAL_SANEADO_20260604_225138.xlsx"
)

KEY_EQUIVALENCES = {
    "codigo_unico": ["CODIGO_UNICO", "COD_UNICO"],
    "codigo_ies": ["CODIGO_IES", "CODIGO_IES_NUM", "COD_IES"],
    "sede": ["CODIGO_SEDE", "COD_SED", "COD_SEDE", "NOMBRE_SEDE", "SEDE"],
    "codigo_sede": ["CODIGO_SEDE", "COD_SED", "COD_SEDE"],
    "nombre_sede": ["NOMBRE_SEDE", "SEDE"],
    "carrera": ["CODIGO_CARRERA", "COD_CARRERA", "COD_CAR", "CARRERA", "NOMBRE_CARRERA"],
    "codigo_carrera": ["CODIGO_CARRERA", "COD_CARRERA", "COD_CAR", "COD_CARRERA_DERIVADO"],
    "nombre_carrera": ["NOMBRE_CARRERA", "CARRERA", "NOMBRE", "NOMBRE_CARRERA_ORIGINAL", "NOMBRE_CARRERA_NORMALIZADO"],
    "modalidad": ["MODALIDAD", "CODIGO_MODALIDAD", "COD_MODALIDAD", "MODALIDAD_ORIGINAL", "MODALIDAD_DEL_PROGRAMA"],
    "jornada": ["JORNADA", "CODIGO_JORNADA", "COD_JORNADA", "JOR"],
    "version": ["VERSION", "VERSION_CARRERA", "VERSION_DERIVADA"],
    "tipo_carrera": ["TIPO_CARRERA", "CODIGO_TIPO_CARRERA", "CARACTERISTICAS_TIPO_PLAN"],
    "duracion": ["DURACION_TOTAL", "DURACION_ESTUDIOS", "DURACION_ESTUDIO", "DURACION_TITULACION", "DURACION_DEL_PROGRAMA_EN_SEMESTRES"],
    "duracion_total": ["DURACION_TOTAL"],
    "duracion_estudios": ["DURACION_ESTUDIOS", "DURACION_ESTUDIO"],
    "vigencia": ["VIGENCIA", "VIGENCIA_CARRERA"],
    "regimen": ["REGIMEN", "DURACION_REGIMEN"],
    "titulo": ["NOMBRE_TITULO", "TITULO_QUE_OTORGA_EL_PROGRAMA"],
    "nivel_global": ["CODIGO_NIVEL_GLOBAL", "NIVEL_GLOBAL"],
    "nivel_carrera": ["CODIGO_NIVEL_CARRERA", "NIVEL_CARRERA"],
    "anio_inicio": ["ANIO_INICIO", "AÑO_INICIO", "ANO_INICIO", "AÑO_DE_INICIO_DE_ACTIVIDADES", "ANO_DE_INICIO_DE_ACTIVIDADES"],
    "acreditacion": ["ACREDITACION"],
    "requisito_ingreso": ["REQUISITO_INGRESO"],
    "semestres_reconocidos": ["SEMESTRES_RECONOCIDOS"],
    "area": ["AREA", "AREA_ACTUAL", "AREA_DEL_CONOCIMIENTO"],
}

CRITICAL_FIELDS = [
    "codigo_carrera",
    "nombre_carrera",
    "sede",
    "modalidad",
    "jornada",
    "version",
    "vigencia",
    "duracion",
]

NUMERIC_EXPECTED = [
    "codigo_ies",
    "codigo_sede",
    "codigo_carrera",
    "modalidad",
    "jornada",
    "version",
    "duracion",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_header(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip().upper()
    text = "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )
    for char in [" ", ".", "/", "\\", "-", "(", ")", "[", "]", "\n", "\r", "\t", ":"]:
        text = text.replace(char, "_")
    text = re.sub(r"[^A-Z0-9_]+", "_", text)
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")


def normalize_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        try:
            return str(int(float(text)))
        except ValueError:
            return text
    return text


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_guardrail(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [str(root / ".venv" / "bin" / "python"), "cned/scripts/check_no_tocar_mu2026.py"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def git_status(root: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def read_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, dtype=str, keep_default_na=False)


def colmap(df: pd.DataFrame) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for col in df.columns:
        norm = normalize_header(col)
        if norm and norm not in mapping:
            mapping[norm] = col
    return mapping


def find_column(df: pd.DataFrame, key: str) -> str | None:
    mapping = colmap(df)
    for candidate in KEY_EQUIVALENCES.get(key, []):
        norm = normalize_header(candidate)
        if norm in mapping:
            return mapping[norm]
    return None


def series_for(df: pd.DataFrame, key: str) -> pd.Series | None:
    col = find_column(df, key)
    if col is None:
        return None
    return df[col].map(normalize_value)


def non_empty_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace("", pd.NA).dropna(how="all")


def sheet_profile(path: Path, sheet_name: str) -> tuple[dict[str, Any], pd.DataFrame | None, str | None]:
    try:
        df = read_sheet(path, sheet_name)
    except Exception as exc:  # noqa: BLE001 - keep audit going per sheet
        return {
            "hoja": sheet_name,
            "error": str(exc),
            "filas_totales": 0,
            "columnas_totales": 0,
            "filas_no_vacias": 0,
            "columnas_no_vacias": 0,
            "score_hoja": -999,
        }, None, str(exc)

    normalized_headers = [normalize_header(col) for col in df.columns]
    unnamed = sum(1 for col in normalized_headers if not col or col.startswith("UNNAMED"))
    duplicate_headers = sum(count - 1 for count in Counter(normalized_headers).values() if count > 1)
    empty_rows = int(df.replace("", pd.NA).isna().all(axis=1).sum())
    empty_cols = int(df.replace("", pd.NA).isna().all(axis=0).sum())
    non_empty = non_empty_frame(df)
    non_empty_cols = int(df.replace("", pd.NA).dropna(how="all", axis=1).shape[1])
    total_cells = max(df.shape[0] * df.shape[1], 1)
    filled_cells = int((df.replace("", pd.NA).notna()).sum().sum())
    completion = round(filled_cells / total_cells * 100, 2)

    completion_by_col = {
        str(col): round((df[col].map(normalize_value) != "").sum() / max(len(df), 1) * 100, 2)
        for col in df.columns
    }
    cols_100 = [col for col, pct in completion_by_col.items() if pct == 100]
    cols_0 = [col for col, pct in completion_by_col.items() if pct == 0]
    cols_lt_50 = [col for col, pct in completion_by_col.items() if pct < 50]
    key_detected = sorted(
        norm for norm in set(normalized_headers)
        if any(norm == normalize_header(x) for vals in KEY_EQUIVALENCES.values() for x in vals)
    )

    name_norm = normalize_header(sheet_name)
    score = 0
    score += min(int(non_empty.shape[0] / 10), 80)
    score += min(non_empty_cols, 80)
    score += len(key_detected) * 8
    if find_column(df, "codigo_unico"):
        score += 40
    for key in ["carrera", "sede", "jornada", "modalidad", "version", "vigencia", "duracion"]:
        if find_column(df, key):
            score += 20
    if "PROGRAMAS_FALTANTES" in name_norm:
        score += 140
    if "CARGA" in name_norm or "BASE" in name_norm:
        score += 35
    for marker, penalty in [
        ("AUDITORIA", 100),
        ("CONTROL", 90),
        ("RESUMEN", 75),
        ("DICCIONARIO", 70),
        ("DECISION", 65),
        ("CONFLICTO", 60),
        ("CAMBIOS", 50),
    ]:
        if marker in name_norm:
            score -= penalty
    if df.shape[1] and unnamed / df.shape[1] > 0.3:
        score -= 40

    sample = non_empty.head(5).astype(str).to_dict(orient="records")
    profile = {
        "hoja": sheet_name,
        "error": "",
        "filas_totales": int(df.shape[0]),
        "columnas_totales": int(df.shape[1]),
        "filas_completamente_vacias": empty_rows,
        "columnas_completamente_vacias": empty_cols,
        "filas_no_vacias": int(non_empty.shape[0]),
        "columnas_no_vacias": non_empty_cols,
        "encabezados_originales": list(map(str, df.columns)),
        "encabezados_normalizados": normalized_headers,
        "columnas_sin_nombre": unnamed,
        "columnas_duplicadas": duplicate_headers,
        "porcentaje_completitud_general": completion,
        "columnas_completitud_100": cols_100,
        "columnas_completitud_0": cols_0,
        "columnas_completitud_menor_50": cols_lt_50,
        "muestra_5_filas_no_vacias": sample,
        "campos_clave_detectados": key_detected,
        "score_hoja": score,
    }
    return profile, df, None


def infer_column_type(values: pd.Series) -> str:
    non_empty = values.map(normalize_value)
    non_empty = non_empty[non_empty != ""]
    if non_empty.empty:
        return "VACIA"
    numeric = pd.to_numeric(non_empty, errors="coerce").notna().mean()
    date_like = non_empty.str.match(r"^\d{4}-\d{1,2}-\d{1,2}$|^\d{1,2}/\d{1,2}/\d{4}$", na=False).mean()
    avg_len = non_empty.str.len().mean()
    if numeric >= 0.9:
        return "NUMERICA"
    if date_like >= 0.5:
        return "FECHA_POSIBLE"
    if avg_len >= 80:
        return "TEXTO_LARGO"
    return "TEXTO_CATEGORICO"


def profile_columns(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    n = max(len(df), 1)
    for col in df.columns:
        raw = df[col].map(normalize_value)
        non_null = int((raw != "").sum())
        nulls = int(n - non_null)
        completion = round(non_null / n * 100, 2)
        unique_values = sorted(v for v in raw.unique().tolist() if v != "")
        norm = normalize_header(col)
        inferred = infer_column_type(df[col])
        max_len = max((len(v) for v in raw.tolist()), default=0)
        alerts = []
        if completion == 0:
            alerts.append("COLUMNA_VACIA")
        if completion < 80:
            alerts.append("COMPLETITUD_MENOR_80")
        if any(marker in norm for marker in ["MATCH", "AUDITORIA", "CONTROL", "FUENTE", "OBSERVACION_AUDITORIA"]):
            alerts.append("PARECE_AUXILIAR_NO_OFICIAL")
        if "CODIGO_UNICO" in norm and len(unique_values) < non_null:
            alerts.append("IDENTIFICADOR_CON_VALORES_REPETIDOS")
        if inferred == "TEXTO_CATEGORICO" and len(unique_values) > 200:
            alerts.append("MUCHOS_VALORES_UNICOS")
        if inferred == "NUMERICA" and len(unique_values) <= 3 and any(k in norm for k in ["CODIGO_UNICO", "NOMBRE"]):
            alerts.append("POCOS_VALORES_UNICOS_EN_CAMPO_IDENTIFICADOR")
        rows.append({
            "nombre_original": str(col),
            "nombre_normalizado": norm,
            "tipo_inferido": inferred,
            "valores_no_nulos": non_null,
            "valores_nulos": nulls,
            "porcentaje_completitud": completion,
            "valores_unicos": len(unique_values),
            "ejemplos_valores_unicos": " | ".join(unique_values[:10]),
            "largo_maximo": max_len,
            "contiene_posibles_codigos": "SI" if re.search(r"COD|CODIGO|ID", norm) else "NO",
            "contiene_posibles_textos_largos": "SI" if inferred == "TEXTO_LARGO" else "NO",
            "contiene_posibles_fechas": "SI" if inferred == "FECHA_POSIBLE" else "NO",
            "contiene_posibles_numericos": "SI" if inferred == "NUMERICA" else "NO",
            "alertas_columna": " | ".join(alerts),
        })
    return rows


def parse_codigo_unico(value: str) -> dict[str, str] | None:
    match = re.fullmatch(r"I162S(?P<sede>\d+)C(?P<carrera>\d+)J(?P<jornada>\d+)V(?P<version>\d+)", value)
    return match.groupdict() if match else None


def first_value(row: pd.Series, df: pd.DataFrame, key: str) -> str:
    col = find_column(df, key)
    return normalize_value(row[col]) if col is not None else ""


def is_positive_number(value: str) -> bool:
    try:
        return float(value) > 0
    except ValueError:
        return False


def is_numeric_like(value: str) -> bool:
    if value == "":
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False


def audit_records(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    audited = df.copy()
    code_col = find_column(df, "codigo_unico")
    duplicate_codes = set()
    if code_col:
        codes = df[code_col].map(normalize_value)
        duplicate_codes = set(codes[(codes != "") & codes.duplicated(keep=False)].tolist())

    combo_cols = [
        find_column(df, "codigo_sede"),
        find_column(df, "codigo_carrera"),
        find_column(df, "modalidad"),
        find_column(df, "jornada"),
        find_column(df, "version"),
    ]
    combo_cols = [col for col in combo_cols if col]
    duplicate_combo_index = set()
    if len(combo_cols) >= 4:
        duplicate_combo_index = set(
            df[df.duplicated(subset=combo_cols, keep=False)].index.tolist()
        )

    codigo_unico_issues: list[dict[str, Any]] = []
    record_rows: list[dict[str, Any]] = []
    codigo_carrera_name_map: defaultdict[str, set[str]] = defaultdict(set)
    carrera_col = find_column(df, "codigo_carrera")
    nombre_col = find_column(df, "nombre_carrera")
    if carrera_col and nombre_col:
        for _, row in df.iterrows():
            code = normalize_value(row[carrera_col])
            name = normalize_value(row[nombre_col])
            if code and name:
                codigo_carrera_name_map[code].add(name)

    for idx, row in df.iterrows():
        alerts: list[str] = []
        critical: list[str] = []
        codigo_unico = first_value(row, df, "codigo_unico")
        if code_col and codigo_unico in duplicate_codes:
            alerts.append("CODIGO_UNICO_DUPLICADO")
            critical.append("CODIGO_UNICO_DUPLICADO")
        if idx in duplicate_combo_index:
            alerts.append("DUPLICADO_COMBINACION_SEDE_CARRERA_MODALIDAD_JORNADA_VERSION")

        for key in CRITICAL_FIELDS:
            value = first_value(row, df, key)
            if value == "":
                alerts.append(f"FALTA_{key.upper()}")
                critical.append(f"FALTA_{key.upper()}")

        dur = first_value(row, df, "duracion")
        dur_est = first_value(row, df, "duracion_estudios")
        if dur and not is_positive_number(dur):
            alerts.append("DURACION_INVALIDA")
            critical.append("DURACION_INVALIDA")
        if dur_est and not is_positive_number(dur_est):
            alerts.append("DURACION_ESTUDIOS_INVALIDA")

        for key in NUMERIC_EXPECTED:
            value = first_value(row, df, key)
            if value and not is_numeric_like(value):
                alerts.append(f"CODIGO_NO_NUMERICO_{key.upper()}")

        nombre = first_value(row, df, "nombre_carrera")
        if nombre == "":
            alerts.append("NOMBRE_CARRERA_VACIO")
            critical.append("NOMBRE_CARRERA_VACIO")
        if any(token in nombre.upper() for token in ["PRUEBA", "TEST", "DESCART"]):
            alerts.append("POSIBLE_REGISTRO_PRUEBA_O_DESCARTABLE")

        parsed = parse_codigo_unico(codigo_unico) if codigo_unico else None
        if codigo_unico and parsed is None:
            alerts.append("CODIGO_UNICO_MALFORMADO")
            critical.append("CODIGO_UNICO_MALFORMADO")
        if parsed:
            comparisons = {
                "sede": first_value(row, df, "codigo_sede"),
                "carrera": first_value(row, df, "codigo_carrera"),
                "jornada": first_value(row, df, "jornada"),
                "version": first_value(row, df, "version"),
            }
            for component, separate_value in comparisons.items():
                if separate_value and parsed[component] != separate_value:
                    issue = f"CODIGO_UNICO_INCONSISTENTE_{component.upper()}"
                    alerts.append(issue)
                    critical.append(issue)
                    codigo_unico_issues.append({
                        "fila_excel_aproximada": idx + 2,
                        "codigo_unico": codigo_unico,
                        "componente": component,
                        "valor_codigo_unico": parsed[component],
                        "valor_columna": separate_value,
                    })

        codigo_carrera = first_value(row, df, "codigo_carrera")
        if codigo_carrera and len(codigo_carrera_name_map.get(codigo_carrera, set())) > 1:
            alerts.append("MISMO_CODIGO_CARRERA_CON_MULTIPLES_NOMBRES")

        vigencia = first_value(row, df, "vigencia")
        if codigo_unico and not vigencia:
            alerts.append("CODIGO_UNICO_SIN_VIGENCIA")
            critical.append("CODIGO_UNICO_SIN_VIGENCIA")

        non_empty_count = sum(1 for value in row.map(normalize_value).tolist() if value)
        if non_empty_count < 4:
            alerts.append("FILA_SIN_ESTRUCTURA_SUFICIENTE")
            critical.append("FILA_SIN_ESTRUCTURA_SUFICIENTE")

        row_values = [normalize_value(value).upper() for value in row.tolist()]
        technical_markers = [
            value for value in row_values
            if value == "REVISAR"
            or value.startswith("REVISAR_")
            or value.startswith("CONFLICTO_")
            or value.startswith("DECISION_")
        ]
        if technical_markers:
            alerts.append("CONTIENE_MARCAS_TECNICAS_DE_REVISION")

        if critical:
            estado = "NO"
            estado_auditoria = "NO_SUBIR_ALERTA_CRITICA"
        elif alerts:
            estado = "REVISAR"
            estado_auditoria = "REQUIERE_REVISION"
        else:
            estado = "SI"
            estado_auditoria = "SIN_ALERTAS_CRITICAS"

        record_rows.append({
            "fila_excel_aproximada": idx + 2,
            "CODIGO_UNICO": codigo_unico,
            "NOMBRE_CARRERA": nombre,
            "CNED_ESTADO_AUDITORIA": estado_auditoria,
            "CNED_ALERTAS": " | ".join(sorted(set(alerts))),
            "CNED_PUEDE_SUBIR_PRELIMINAR": estado,
        })

    audited["CNED_ESTADO_AUDITORIA"] = [row["CNED_ESTADO_AUDITORIA"] for row in record_rows]
    audited["CNED_ALERTAS"] = [row["CNED_ALERTAS"] for row in record_rows]
    audited["CNED_PUEDE_SUBIR_PRELIMINAR"] = [row["CNED_PUEDE_SUBIR_PRELIMINAR"] for row in record_rows]

    duplicates_rows: list[dict[str, Any]] = []
    if code_col and duplicate_codes:
        dup_df = df[df[code_col].map(normalize_value).isin(duplicate_codes)]
        for idx, row in dup_df.iterrows():
            duplicates_rows.append({
                "tipo": "CODIGO_UNICO",
                "fila_excel_aproximada": idx + 2,
                "codigo_unico": normalize_value(row[code_col]),
                "detalle": "Codigo unico duplicado",
            })
    if duplicate_combo_index:
        for idx in sorted(duplicate_combo_index):
            row = df.loc[idx]
            duplicates_rows.append({
                "tipo": "COMBINACION_ESTRUCTURAL",
                "fila_excel_aproximada": idx + 2,
                "codigo_unico": first_value(row, df, "codigo_unico"),
                "detalle": "Duplicado por sede/carrera/modalidad/jornada/version",
            })

    return (
        audited,
        pd.DataFrame(record_rows),
        pd.DataFrame(duplicates_rows),
    ), pd.DataFrame(codigo_unico_issues), pd.DataFrame(record_rows)


def safe_sheet(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy().astype(str)


def write_csv(path: Path, df: pd.DataFrame, sep: str = ",") -> None:
    df.to_csv(path, index=False, sep=sep, quoting=csv.QUOTE_MINIMAL)


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> list[str]:
    subset = df.loc[:, [c for c in columns if c in df.columns]].head(max_rows).copy()
    if subset.empty:
        return ["_Sin datos._"]
    headers = list(subset.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in subset.iterrows():
        values = [str(row[col]).replace("|", "/") for col in headers]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = repo_root()
    guard_ok, guard_output = run_guardrail(root)
    if not guard_ok:
        print(guard_output)
        return 2

    base_path = root / BASE_RELATIVE
    if not base_path.exists():
        LOGGER.error("No existe base operativa: %s", base_path)
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_xlsx = root / "cned" / "resultados" / "archivos_subida" / f"CNED_BASE_OPERATIVA_AUDITADA_PRE_SUBIDA_{timestamp}.xlsx"
    out_md = root / "cned" / "resultados" / "reportes" / f"CNED_HITO4_AUDITORIA_BASE_OPERATIVA_{timestamp}.md"
    out_records_csv = root / "cned" / "resultados" / "auditorias" / f"CNED_HITO4_AUDITORIA_REGISTROS_{timestamp}.csv"
    out_columns_csv = root / "cned" / "resultados" / "auditorias" / f"CNED_HITO4_DICCIONARIO_COLUMNAS_{timestamp}.csv"
    out_json = root / "cned" / "resultados" / "auditorias" / f"CNED_HITO4_RESUMEN_AUDITORIA_{timestamp}.json"
    out_subir_csv = root / "cned" / "resultados" / "archivos_subida" / f"CNED_CANDIDATO_SOLO_PUEDE_SUBIR_{timestamp}.csv"
    out_subir_tsv = root / "cned" / "resultados" / "archivos_subida" / f"CNED_CANDIDATO_SOLO_PUEDE_SUBIR_{timestamp}.tsv"
    for path in [out_xlsx, out_md, out_records_csv, out_columns_csv, out_json, out_subir_csv, out_subir_tsv]:
        path.parent.mkdir(parents=True, exist_ok=True)

    try:
        workbook = load_workbook(base_path, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("No se pudo leer la base 01.")
        return 1

    sheet_profiles: list[dict[str, Any]] = []
    sheet_dfs: dict[str, pd.DataFrame] = {}
    for sheet in workbook.sheetnames:
        profile, df, error = sheet_profile(base_path, sheet)
        sheet_profiles.append(profile)
        if df is not None:
            sheet_dfs[sheet] = df
        if error:
            LOGGER.warning("Error leyendo hoja %s: %s", sheet, error)

    if not sheet_dfs:
        LOGGER.error("No se pudo leer ninguna hoja util.")
        return 1

    ranked_sheets = sorted(sheet_profiles, key=lambda item: item.get("score_hoja", -999), reverse=True)
    main_sheet = ranked_sheets[0]["hoja"]
    main_df = sheet_dfs[main_sheet]
    LOGGER.info("Hoja principal recomendada: %s", main_sheet)

    column_rows = profile_columns(main_df)
    columns_df = pd.DataFrame(column_rows)
    (audited_df, audit_records_df, duplicates_df), codigo_issues_df, record_audit_df = audit_records(main_df)

    puede_df = audited_df[audited_df["CNED_PUEDE_SUBIR_PRELIMINAR"] == "SI"].copy()
    revisar_df = audited_df[audited_df["CNED_PUEDE_SUBIR_PRELIMINAR"] == "REVISAR"].copy()
    no_subir_df = audited_df[audited_df["CNED_PUEDE_SUBIR_PRELIMINAR"] == "NO"].copy()
    total = len(audited_df)
    puede = len(puede_df)
    revisar = len(revisar_df)
    no_subir = len(no_subir_df)
    duplicate_count = len(duplicates_df)
    inconsistency_count = len(codigo_issues_df)

    critical_missing = int((audit_records_df["CNED_PUEDE_SUBIR_PRELIMINAR"] == "NO").sum())
    if duplicate_count or inconsistency_count > max(total * 0.1, 10) or critical_missing > max(total * 0.1, 10):
        semaforo = "ROJO"
        recomendacion = "no subir; requiere saneamiento previo"
    elif total and puede / total >= 0.95 and revisar == 0 and no_subir == 0:
        semaforo = "VERDE"
        recomendacion = "base lista para validacion institucional final antes de subida"
    else:
        semaforo = "AMARILLO"
        recomendacion = "base usable, pero requiere resolver observaciones antes de subida"

    sheet_summary_df = pd.DataFrame([
        {
            "hoja": p["hoja"],
            "score_hoja": p["score_hoja"],
            "filas_totales": p["filas_totales"],
            "columnas_totales": p["columnas_totales"],
            "filas_no_vacias": p["filas_no_vacias"],
            "columnas_no_vacias": p["columnas_no_vacias"],
            "columnas_sin_nombre": p["columnas_sin_nombre"],
            "columnas_duplicadas": p["columnas_duplicadas"],
            "porcentaje_completitud_general": p["porcentaje_completitud_general"],
            "campos_clave_detectados": " | ".join(p["campos_clave_detectados"]),
            "columnas_completitud_0": " | ".join(p["columnas_completitud_0"][:30]),
            "columnas_completitud_menor_50": " | ".join(p["columnas_completitud_menor_50"][:30]),
            "error": p.get("error", ""),
        }
        for p in ranked_sheets
    ])

    resumen_df = pd.DataFrame([
        {"campo": "fecha_ejecucion", "valor": datetime.now().isoformat(timespec="seconds")},
        {"campo": "archivo_base", "valor": str(BASE_RELATIVE)},
        {"campo": "sha256_base", "valor": sha256(base_path)},
        {"campo": "hoja_principal_recomendada", "valor": main_sheet},
        {"campo": "total_registros_hoja_principal", "valor": total},
        {"campo": "puede_subir_preliminar", "valor": puede},
        {"campo": "requiere_revision", "valor": revisar},
        {"campo": "no_subir", "valor": no_subir},
        {"campo": "duplicados_detectados", "valor": duplicate_count},
        {"campo": "inconsistencias_codigo_unico", "valor": inconsistency_count},
        {"campo": "semaforo", "valor": semaforo},
        {"campo": "recomendacion_operativa", "valor": recomendacion},
        {"campo": "advertencia", "valor": "No se declara archivo final CNED mientras no se confirme instructivo/estructura oficial de carga."},
    ])

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        safe_sheet(audited_df).to_excel(writer, sheet_name="BASE_AUDITADA", index=False)
        safe_sheet(puede_df).to_excel(writer, sheet_name="SOLO_PUEDE_SUBIR", index=False)
        safe_sheet(revisar_df).to_excel(writer, sheet_name="REQUIERE_REVISION", index=False)
        safe_sheet(no_subir_df).to_excel(writer, sheet_name="NO_SUBIR", index=False)
        safe_sheet(columns_df).to_excel(writer, sheet_name="DICCIONARIO_COLUMNAS", index=False)
        safe_sheet(sheet_summary_df).to_excel(writer, sheet_name="RESUMEN_HOJAS", index=False)
        safe_sheet(duplicates_df if not duplicates_df.empty else pd.DataFrame(columns=["tipo", "fila_excel_aproximada", "codigo_unico", "detalle"])).to_excel(writer, sheet_name="DUPLICADOS", index=False)
        safe_sheet(codigo_issues_df if not codigo_issues_df.empty else pd.DataFrame(columns=["fila_excel_aproximada", "codigo_unico", "componente", "valor_codigo_unico", "valor_columna"])).to_excel(writer, sheet_name="INCONSISTENCIAS_CODIGO_UNICO", index=False)
        safe_sheet(resumen_df).to_excel(writer, sheet_name="RESUMEN_EJECUTIVO", index=False)

    if puede:
        write_csv(out_subir_csv, puede_df)
        write_csv(out_subir_tsv, puede_df, sep="\t")

    write_csv(out_records_csv, record_audit_df)
    write_csv(out_columns_csv, columns_df)

    low_completion = columns_df[columns_df["porcentaje_completitud"] < 80].copy()
    empty_columns = columns_df[columns_df["porcentaje_completitud"] == 0].copy()
    alert_counter = Counter()
    for value in audit_records_df["CNED_ALERTAS"].tolist():
        for alert in str(value).split(" | "):
            if alert:
                alert_counter[alert] += 1

    json_payload = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "git_status_inicial": git_status(root),
        "archivo_base": str(BASE_RELATIVE),
        "sha256_base": sha256(base_path),
        "hoja_principal_recomendada": main_sheet,
        "total_registros": total,
        "puede_subir_preliminar": puede,
        "requiere_revision": revisar,
        "no_subir": no_subir,
        "duplicados_detectados": duplicate_count,
        "inconsistencias_codigo_unico": inconsistency_count,
        "semaforo": semaforo,
        "recomendacion_operativa": recomendacion,
        "archivos_generados": {
            "excel_operativo_auditado": str(out_xlsx),
            "csv_auditoria_registros": str(out_records_csv),
            "csv_diccionario_columnas": str(out_columns_csv),
            "json_resumen": str(out_json),
            "csv_solo_puede_subir": str(out_subir_csv) if puede else None,
            "tsv_solo_puede_subir": str(out_subir_tsv) if puede else None,
        },
        "resumen_hojas": sheet_summary_df.to_dict(orient="records"),
        "alertas_principales": alert_counter.most_common(20),
        "guardrail_mu2026": guard_output,
        "advertencia": "No se declara archivo final CNED mientras no se confirme instructivo/estructura oficial de carga.",
    }
    out_json.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# CNED Hito 4 - Auditoria base operativa preliminar",
        "",
        f"- Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"- Archivo base auditado: `{BASE_RELATIVE}`",
        f"- SHA256 base: `{sha256(base_path)}`",
        f"- Hoja principal recomendada: `{main_sheet}`",
        f"- Semaforo: **{semaforo}**",
        f"- Recomendacion operativa: {recomendacion}",
        "",
        "## Estado Git inicial",
        "",
        "```text",
        git_status(root),
        "```",
        "",
        "## Resumen por hoja",
        "",
        *markdown_table(sheet_summary_df, ["hoja", "score_hoja", "filas_no_vacias", "columnas_no_vacias", "porcentaje_completitud_general", "campos_clave_detectados"], 30),
        "",
        "## Totales hoja principal",
        "",
        f"- Total registros: {total}",
        f"- Puede subir preliminar: {puede}",
        f"- Requiere revision: {revisar}",
        f"- No subir: {no_subir}",
        f"- Duplicados detectados: {duplicate_count}",
        f"- Inconsistencias CODIGO_UNICO: {inconsistency_count}",
        "",
        "## Columnas con baja completitud",
        "",
        *markdown_table(low_completion, ["nombre_original", "porcentaje_completitud", "alertas_columna"], 40),
        "",
        "## Columnas vacias",
        "",
        *markdown_table(empty_columns, ["nombre_original", "porcentaje_completitud", "alertas_columna"], 40),
        "",
        "## Alertas principales por registro",
        "",
    ]
    if alert_counter:
        md_lines.extend(f"- {alert}: {count}" for alert, count in alert_counter.most_common(20))
    else:
        md_lines.append("- Sin alertas por registro.")
    md_lines.extend([
        "",
        "## Archivos generados",
        "",
        f"- Excel operativo auditado: `{out_xlsx.relative_to(root)}`",
        f"- CSV auditoria registros: `{out_records_csv.relative_to(root)}`",
        f"- CSV diccionario columnas: `{out_columns_csv.relative_to(root)}`",
        f"- JSON resumen: `{out_json.relative_to(root)}`",
        f"- CSV candidato solo puede subir: `{out_subir_csv.relative_to(root) if puede else 'NO_GENERADO_SIN_REGISTROS_SI'}`",
        f"- TSV candidato solo puede subir: `{out_subir_tsv.relative_to(root) if puede else 'NO_GENERADO_SIN_REGISTROS_SI'}`",
        "",
        "## Guardrail MU2026/PES_READY",
        "",
        "```text",
        guard_output,
        "```",
        "",
        "> Advertencia: No se declara archivo final CNED mientras no se confirme instructivo/estructura oficial de carga.",
        "",
        "## Dictamen",
        "",
        "DICTAMEN_FINAL: HITO4_BASE_OPERATIVA_AUDITADA_PRE_SUBIDA_GENERADA",
    ])
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    expected_sheets = {
        "BASE_AUDITADA",
        "SOLO_PUEDE_SUBIR",
        "REQUIERE_REVISION",
        "NO_SUBIR",
        "DICCIONARIO_COLUMNAS",
        "RESUMEN_HOJAS",
        "DUPLICADOS",
        "INCONSISTENCIAS_CODIGO_UNICO",
        "RESUMEN_EJECUTIVO",
    }
    generated_wb = load_workbook(out_xlsx, read_only=True, data_only=True)
    self_errors = []
    if set(generated_wb.sheetnames) != expected_sheets:
        self_errors.append("Hojas generadas no coinciden con las esperadas.")
    if generated_wb["BASE_AUDITADA"].max_row - 1 != total:
        self_errors.append("BASE_AUDITADA no coincide con total leido.")
    if puede + revisar + no_subir != total:
        self_errors.append("Segmentos no suman total.")
    for output_path in [out_xlsx, out_md, out_records_csv, out_columns_csv, out_json]:
        if not output_path.exists():
            self_errors.append(f"No existe archivo generado: {output_path}")
        try:
            output_path.relative_to(root / "cned")
        except ValueError:
            self_errors.append(f"Archivo escrito fuera de cned/: {output_path}")
    guard_ok_after, guard_after_output = run_guardrail(root)
    if not guard_ok_after:
        self_errors.append("Guardrail MU2026 fallo al final.")

    print("======================================================================")
    print("HITO 4 CNED - AUDITORIA BASE OPERATIVA")
    print("======================================================================")
    print(f"Archivo base: {BASE_RELATIVE}")
    print(f"Hoja principal recomendada: {main_sheet}")
    print(f"Total registros: {total}")
    print(f"Puede subir preliminar: {puede}")
    print(f"Requiere revision: {revisar}")
    print(f"No subir: {no_subir}")
    print(f"Duplicados detectados: {duplicate_count}")
    print(f"Inconsistencias CODIGO_UNICO: {inconsistency_count}")
    print(f"Semaforo: {semaforo}")
    print(f"Excel auditado: {out_xlsx}")
    print(f"Reporte Markdown: {out_md}")
    print(f"CSV auditoria registros: {out_records_csv}")
    print(f"CSV diccionario columnas: {out_columns_csv}")
    print(f"JSON resumen: {out_json}")
    print(f"Guardrail final: {guard_after_output}")
    if self_errors:
        print("AUTOAUDITORIA: ERROR")
        for error in self_errors:
            print(f"- {error}")
        return 1
    print("AUTOAUDITORIA: OK")
    print("DICTAMEN_FINAL: HITO4_BASE_OPERATIVA_AUDITADA_PRE_SUBIDA_GENERADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
