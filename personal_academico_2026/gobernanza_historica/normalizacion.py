"""Normalizacion restringida de fuentes congeladas."""

from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Sequence

import pandas as pd

from .configuracion import TRANSFORMER_VERSION
from .homologacion import build_column_mapping, homologation_records, read_source_frame


def normalized_root(project_root: Path) -> Path:
    """Ruta de fuentes normalizadas restringidas."""

    return project_root / "data" / "normalized_restricted"


def normalize_value(value: object) -> str:
    """Normaliza valor escalar para campos internos."""

    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.upper() in {"NAN", "NONE", "NULL"} else text


def normalize_document(tipo: object, numero: object, dv: object) -> str:
    """Construye clave documental interna."""

    tipo_text = normalize_value(tipo).upper()
    number = normalize_value(numero)
    check = normalize_value(dv).upper()
    if tipo_text == "R":
        number = "".join(ch for ch in number if ch.isdigit())
        check = check.replace(".", "").replace("-", "").replace(" ", "")
    if tipo_text == "P":
        number = number.replace(" ", "")
        check = ""
    if tipo_text == "" or number == "":
        return ""
    return f"{tipo_text}|{number}|{check}"


def parse_number(value: object) -> float | None:
    """Convierte numero historico a float cuando es posible."""

    text = normalize_value(value)
    if text == "":
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def parquet_available() -> bool:
    """Indica si el entorno posee motor Parquet."""

    return importlib.util.find_spec("pyarrow") is not None or importlib.util.find_spec("fastparquet") is not None


def add_internal_columns(
    frame: pd.DataFrame,
    mapping: dict[str, str],
    source: pd.Series,
    normalized_at: str,
) -> pd.DataFrame:
    """Agrega columnas internas sin eliminar columnas originales."""

    output = frame.copy()
    homologated_values: dict[str, pd.Series] = {}
    for original, homologated in mapping.items():
        homologated_values[homologated] = output[original].astype(str)
        output[f"INTERNO_H_{homologated}"] = output[original].astype(str)
    for required in ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "VIGENCIA"]:
        if required not in homologated_values:
            homologated_values[required] = pd.Series([""] * len(output), index=output.index)
            output[f"INTERNO_H_{required}"] = ""
    output["INTERNO_CLAVE_DOCUMENTAL"] = [
        normalize_document(tipo, numero, dv)
        for tipo, numero, dv in zip(
            homologated_values["TIPO_DOCUMENTO"],
            homologated_values["NUM_DOCUMENTO"],
            homologated_values["DV"],
            strict=False,
        )
    ]
    output["INTERNO_VIGENCIA_NORMALIZADA"] = homologated_values["VIGENCIA"].map(lambda value: normalize_value(value))
    hour_columns = [
        homologated_values.get("NUM_HORAS_PLANTA"),
        homologated_values.get("NUM_HORAS_CONTRATA"),
        homologated_values.get("NUM_HORAS_HONORARIOS"),
    ]
    if all(column is not None for column in hour_columns):
        output["INTERNO_TOTAL_HORAS"] = [
            sum(parse_number(value) or 0.0 for value in values)
            for values in zip(*hour_columns, strict=False)
        ]
    else:
        output["INTERNO_TOTAL_HORAS"] = pd.NA
    output["INTERNO_ANIO"] = int(source["anio"])
    output["INTERNO_RUTA_ORIGEN"] = str(source["ruta_original"])
    output["INTERNO_NOMBRE_ARCHIVO_ORIGEN"] = str(source["archivo"])
    output["INTERNO_SHA256_ORIGEN"] = str(source["sha256_original"])
    output["INTERNO_FECHA_NORMALIZACION"] = normalized_at
    output["INTERNO_VERSION_TRANSFORMADOR"] = TRANSFORMER_VERSION
    output["INTERNO_ES_DUPLICADO_CLAVE"] = output["INTERNO_CLAVE_DOCUMENTAL"].duplicated(keep=False)
    return output


def write_normalized(frame: pd.DataFrame, target_stem: Path) -> tuple[Path, str, str]:
    """Escribe normalizacion en Parquet si hay motor, o CSV gobernado si no."""

    if parquet_available():
        path = target_stem.with_suffix(".parquet")
        frame.to_parquet(path, index=False)
        return path, "parquet", "OK"
    path = target_stem.with_suffix(".csv")
    frame.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
    return path, "csv_fallback", "PARQUET_NO_DISPONIBLE_EN_ENTORNO"


def normalize_sources(
    project_root: Path,
    frozen_sources: pd.DataFrame,
    official_headers: Sequence[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normaliza fuentes congeladas y genera diccionario de homologacion."""

    root = normalized_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    normalized_at = datetime.now().replace(microsecond=0).isoformat()
    manifest_rows: list[dict[str, object]] = []
    homologation_rows: list[dict[str, object]] = []
    for _index, source in frozen_sources.iterrows():
        governed_path = Path(str(source["ruta_gobernada"]))
        frame, profile = read_source_frame(governed_path, official_headers, str(source.get("hoja_seleccionada", "")))
        mapping = build_column_mapping(frame.columns, official_headers)
        normalized = add_internal_columns(frame, mapping, source, normalized_at)
        valid_key = normalized["INTERNO_CLAVE_DOCUMENTAL"].astype(str).str.len() > 0
        invalid_key_count = int((~valid_key).sum())
        duplicate_count = int(normalized.loc[valid_key, "INTERNO_CLAVE_DOCUMENTAL"].duplicated(keep=False).sum())
        normalized = normalized[valid_key].drop_duplicates("INTERNO_CLAVE_DOCUMENTAL", keep="first").reset_index(drop=True)
        target_stem = root / f"personal_academico_{int(source['anio'])}"
        output_path, format_name, parquet_status = write_normalized(normalized, target_stem)
        manifest_rows.append(
            {
                "anio": int(source["anio"]),
                "ruta_normalizada": str(output_path),
                "formato": format_name,
                "estado_parquet": parquet_status,
                "filas_normalizadas": len(normalized),
                "columnas_normalizadas": len(normalized.columns),
                "duplicados_clave_detectados": duplicate_count,
                "filas_sin_clave_excluidas": invalid_key_count,
                "tipo_lectura": profile.get("tipo", ""),
                "encoding": profile.get("encoding", ""),
                "delimitador": profile.get("delimitador", ""),
                "fecha_normalizacion": normalized_at,
                "version_transformador": TRANSFORMER_VERSION,
            }
        )
        homologation_rows.extend(homologation_records(int(source["anio"]), frame.columns, official_headers))
    return pd.DataFrame(manifest_rows), pd.DataFrame(homologation_rows)
