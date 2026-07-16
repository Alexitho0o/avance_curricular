"""Carga de fuentes normalizadas gobernadas sin descubrimiento automatico."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from .configuracion import EXPECTED_UNIVERSES, config_frame, ensure_project_local
from .utilidades import (
    contract_type,
    first_value,
    hour_band,
    normalize_document,
    normalize_value,
    parse_number,
    sha256_file,
)


def verify_config_and_sources(config: dict[str, dict[str, object]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Verifica configuracion, integridad local y universos aprobados."""

    cfg = config_frame(config)
    validations: list[dict[str, object]] = []
    rows: list[pd.DataFrame] = []
    for _index, source in cfg.iterrows():
        year = int(source["anio"])
        normalized_path = ensure_project_local(source["ruta_normalizada"])
        governed_path = ensure_project_local(source["ruta_gobernada"])
        source_hash = sha256_file(governed_path)
        validations.append(
            {
                "ANIO": year,
                "CODIGO": "HASH_FUENTE_GOBERNADA",
                "SEVERIDAD": "OK" if source_hash == str(source["sha256"]) else "BLOQUEANTE",
                "DETALLE": "hash coincide" if source_hash == str(source["sha256"]) else "hash no coincide",
            }
        )
        estado = str(source.get("estado", ""))
        validations.append(
            {
                "ANIO": year,
                "CODIGO": "ESTADO_LITERAL_APROBADA",
                "SEVERIDAD": "ADVERTENCIA" if estado != "APROBADA" else "OK",
                "DETALLE": f"estado_config={estado}; Fase 2A usa universo aprobado explicitado por prompt",
            }
        )
        frame = pd.read_csv(normalized_path, sep=";", dtype=str, keep_default_na=False).fillna("")
        expected = EXPECTED_UNIVERSES.get(year)
        unique_people = frame["INTERNO_CLAVE_DOCUMENTAL"].nunique()
        severity = "OK" if expected == unique_people == len(frame) else "BLOQUEANTE"
        validations.append(
            {
                "ANIO": year,
                "CODIGO": "UNIVERSO_APROBADO",
                "SEVERIDAD": severity,
                "DETALLE": f"filas={len(frame)} personas={unique_people} esperado={expected}",
            }
        )
        frame["__ANIO_CONFIG"] = year
        frame["__ARCHIVO_FUENTE"] = str(source["archivo"])
        frame["__SHA_FUENTE"] = str(source["sha256"])
        frame["__ESTADO_FUENTE"] = estado
        frame["__RUTA_GOBERNADA"] = str(governed_path)
        frame["__FECHA_RECONSTRUCCION"] = datetime.now().replace(microsecond=0).isoformat()
        rows.append(frame)
    validation_frame = pd.DataFrame(validations)
    if validation_frame["SEVERIDAD"].eq("BLOQUEANTE").any():
        return pd.DataFrame(), validation_frame
    return pd.concat(rows, ignore_index=True), validation_frame


def canonical_row(row: pd.Series) -> dict[str, object]:
    """Convierte una fila normalizada en registro longitudinal canonico."""

    tipo = first_value(row, "INTERNO_H_TIPO_DOCUMENTO", "TIPO_DOCUMENTO")
    numero = first_value(row, "INTERNO_H_NUM_DOCUMENTO", "NUM_DOCUMENTO")
    dv = first_value(row, "INTERNO_H_DV", "DV")
    key = first_value(row, "INTERNO_CLAVE_DOCUMENTAL") or normalize_document(tipo, numero, dv)
    planta = parse_number(first_value(row, "INTERNO_H_NUM_HORAS_PLANTA", "NUM_HORAS_PLANTA"))
    contrata = parse_number(first_value(row, "INTERNO_H_NUM_HORAS_CONTRATA", "NUM_HORAS_CONTRATA"))
    honorarios = parse_number(first_value(row, "INTERNO_H_NUM_HORAS_HONORARIOS", "NUM_HORAS_HONORARIOS", "NUM_HORAS_HONORARIO"))
    total = parse_number(first_value(row, "INTERNO_TOTAL_HORAS"))
    if total is None:
        total = sum(value or 0.0 for value in [planta, contrata, honorarios])
    return {
        "ANIO": int(row["__ANIO_CONFIG"]),
        "FUENTE": row["__ARCHIVO_FUENTE"],
        "SHA_FUENTE": row["__SHA_FUENTE"],
        "CLAVE_DOCUMENTAL": key,
        "TIPO_DOCUMENTO": tipo,
        "NUM_DOCUMENTO": numero,
        "DV": "" if tipo.upper() == "P" else normalize_value(dv).upper(),
        "NOMBRES": first_value(row, "INTERNO_H_NOMBRES", "NOMBRES"),
        "PRIMER_APELLIDO": first_value(row, "INTERNO_H_PRIMER_APELLIDO", "PRIMER_APELLIDO"),
        "SEGUNDO_APELLIDO": first_value(row, "INTERNO_H_SEGUNDO_APELLIDO", "SEGUNDO_APELLIDO"),
        "SEXO": first_value(row, "INTERNO_H_SEXO", "SEXO"),
        "FECHA_NACIMIENTO": first_value(row, "INTERNO_H_FECHA_NACIMIENTO", "FECHA_NACIMIENTO"),
        "NACIONALIDAD": first_value(row, "INTERNO_H_NACIONALIDAD", "NACIONALIDAD"),
        "FORMACION": first_value(row, "INTERNO_H_NIVEL_FORMACION_ACADEMICO", "NIVEL_FORMACION_ACADEMICO", "NIVEL_FORMACION_ACADEM"),
        "TITULO": first_value(row, "INTERNO_H_NOMBRE_TITULO_O_GRADO", "NOMBRE_TITULO_O_GRADO", "NOMBRE_TITULO O GRADO"),
        "CARGO": first_value(row, "INTERNO_H_PRINCIPAL_CARGO_ACADEMICO", "PRINCIPAL_CARGO_ACADEMICO"),
        "CARGO_NORMALIZADO": first_value(row, "INTERNO_H_CARGO_NORMALIZADO", "CARGO_NORMALIZADO"),
        "ADSCRIPCION": first_value(row, "INTERNO_H_NIVEL_SUPERIOR_ADSCRIPCION", "NIVEL_SUPERIOR_ADSCRIPCION"),
        "ADSCRIPCION_SECUNDARIA": first_value(row, "INTERNO_H_NIVEL_SECUNDARIO_ADSCRIPCION", "NIVEL_SECUNDARIO_ADSCRIPCION"),
        "PROGRAMA_PRINCIPAL": first_value(row, "INTERNO_H_NOMBRE_PRINCIPAL_PROGRAMA", "NOMBRE_PRINCIPAL_PROGRAMA"),
        "HORAS_PLANTA": planta,
        "HORAS_CONTRATA": contrata,
        "HORAS_HONORARIOS": honorarios,
        "TOTAL_HORAS": total,
        "TRAMO_HORAS": hour_band(total),
        "TIPO_CONTRACTUAL": contract_type(planta, contrata, honorarios),
        "JERARQUIA": first_value(row, "INTERNO_H_JERARQUIA_ACADEMICA", "JERARQUIA_ACADEMICA"),
        "JERARQUIA_OCDE": first_value(row, "INTERNO_H_JERARQUIA_ACADEMICA_OCDE", "JERARQUIA_ACADEMICA_OCDE"),
        "VIGENCIA": first_value(row, "INTERNO_VIGENCIA_NORMALIZADA", "INTERNO_H_VIGENCIA", "VIGENCIA"),
        "ESTADO_FUENTE": row["__ESTADO_FUENTE"],
        "OBSERVACIONES": "",
        "HASH_FUENTE": row["__SHA_FUENTE"],
        "VERSION_HOMOLOGACION": first_value(row, "INTERNO_VERSION_TRANSFORMADOR"),
        "FECHA_NORMALIZACION": first_value(row, "INTERNO_FECHA_NORMALIZACION"),
        "LINEA_ORIGEN": "",
        "HOJA_ORIGEN": "",
    }


def build_longitudinal(raw: pd.DataFrame) -> pd.DataFrame:
    """Construye tabla maestra longitudinal CLAVE_DOCUMENTAL + ANIO."""

    frame = pd.DataFrame([canonical_row(row) for _index, row in raw.iterrows()])
    frame = frame.drop_duplicates(["CLAVE_DOCUMENTAL", "ANIO"], keep="first").sort_values(["ANIO", "CLAVE_DOCUMENTAL"])
    return frame.reset_index(drop=True)
