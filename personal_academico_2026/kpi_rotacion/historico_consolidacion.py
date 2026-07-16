"""Homologacion, seleccion anual y calculo historico multianual."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd

from .historico_fuentes import normalize_text
from .lectura import detect_delimiter, parse_line, read_first_line
from .validacion import (
    build_identifier_series,
    compute_rut_dv,
    normalize_document_number,
    normalize_dv,
    normalize_value,
    normalized_upper,
    parse_number,
)


AUDIT_COLUMNS = [
    "ANIO",
    "FUENTE_ID",
    "FUENTE_RUTA",
    "FUENTE_SHA256",
    "LINEA_ORIGEN",
    "HOJA_ORIGEN",
    "CLAVE_DOCUMENTAL",
    "NOMBRE_COMPLETO_NORMALIZADO",
    "TOTAL_HORAS_CONTRACTUALES",
    "ES_VIGENTE",
    "ESTADO_VALIDACION",
    "ADVERTENCIAS",
    "ERRORES",
    "ES_FUENTE_OFICIAL_ANUAL",
    "ESTADO_FUENTE_ANUAL",
]


@dataclass(frozen=True)
class HistoricalTables:
    """Tablas generadas para el paquete historico."""

    inventory: pd.DataFrame
    source_decisions: pd.DataFrame
    candidate_comparison: pd.DataFrame
    longitudinal: pd.DataFrame
    panel: pd.DataFrame
    kpi: pd.DataFrame
    detail: pd.DataFrame
    permanecen: pd.DataFrame
    rotan: pd.DataFrame
    nuevos: pd.DataFrame
    reingresos: pd.DataFrame
    cambios: pd.DataFrame
    desagregaciones: dict[str, pd.DataFrame]
    identidad: pd.DataFrame
    duplicados: pd.DataFrame
    conflictos: pd.DataFrame
    comparability: pd.DataFrame
    resumen: dict[str, object]


def normalize_header(value: object) -> str:
    """Normaliza encabezados historicos a una forma comparable."""

    text = normalize_text(value)
    text = re.sub(r"[^A-Z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def canonical_header_map(official_headers: Sequence[str]) -> dict[str, str]:
    """Crea un mapa de encabezados normalizados a encabezados oficiales."""

    mapping = {normalize_header(header): header for header in official_headers}
    aliases = {
        "NUM_HORAS_HONORARIO": "NUM_HORAS_HONORARIOS",
        "HORAS_HONORARIO": "NUM_HORAS_HONORARIOS",
        "TOTAL_HORAS": "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
        "TIPO_ESPECIALIDAD": "TIPO_ESPECIALIDAD",
    }
    mapping.update(aliases)
    return mapping


def dataframe_from_text(path: Path, official_headers: Sequence[str]) -> tuple[pd.DataFrame, str, str, bool]:
    """Lee una fuente textual historica y devuelve datos crudos."""

    first_line, encoding = read_first_line(path, ["utf-8-sig", "cp1252", "latin1"])
    delimiter = detect_delimiter(first_line)
    first_values = parse_line(first_line, delimiter)
    normalized_first = [normalize_header(value) for value in first_values]
    official_norm = {normalize_header(value) for value in official_headers}
    has_header = "TIPO_DOCUMENTO" in normalized_first or len(set(normalized_first) & official_norm) >= 5
    if has_header:
        frame = pd.read_csv(path, sep=delimiter, encoding=encoding, dtype=str, keep_default_na=False)
    else:
        rows: list[list[str]] = []
        with path.open("r", encoding=encoding, errors="replace", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            for row in reader:
                rows.append(row)
        if not rows:
            frame = pd.DataFrame()
        elif len(rows[0]) == len(official_headers):
            frame = pd.DataFrame(rows, columns=list(official_headers), dtype=str)
        else:
            frame = pd.DataFrame(rows, dtype=str)
    return frame.fillna(""), encoding, delimiter, has_header


def dataframe_from_excel(path: Path, sheet_name: str) -> pd.DataFrame:
    """Lee una hoja Excel historica con todos sus valores como texto."""

    return pd.read_excel(path, sheet_name=sheet_name or 0, dtype=str, keep_default_na=False).fillna("")


def homologate_frame(
    raw: pd.DataFrame,
    official_headers: Sequence[str],
    source_row: pd.Series,
) -> pd.DataFrame:
    """Homologa columnas historicas existentes al esquema oficial disponible."""

    mapping = canonical_header_map(official_headers)
    output = pd.DataFrame(index=raw.index)
    for official in official_headers:
        output[official] = f"NO_DISPONIBLE_EN_ESTRUCTURA_{int(source_row['anio_fuente'])}"
    used_columns: set[str] = set()
    for column in raw.columns:
        key = normalize_header(column)
        official = mapping.get(key)
        if official and official in output.columns and column not in used_columns:
            output[official] = raw[column].astype(str)
            used_columns.add(str(column))
    if not used_columns and len(raw.columns) == len(official_headers):
        output = raw.copy()
        output.columns = list(official_headers)
    return output.fillna("")


def load_homologated_source(source_row: pd.Series, official_headers: Sequence[str]) -> pd.DataFrame:
    """Carga y homologa una fuente candidata anual."""

    path = Path(str(source_row["path"]))
    if path.suffix.lower() in {".csv", ".txt"}:
        raw, _encoding, _delimiter, has_header = dataframe_from_text(path, official_headers)
        sheet_name = ""
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        sheet_name = str(source_row.get("selected_sheet", ""))
        raw = dataframe_from_excel(path, sheet_name)
        has_header = True
    else:
        return pd.DataFrame()
    if raw.empty:
        return raw
    if not has_header and len(raw.columns) == len(official_headers):
        raw.columns = list(official_headers)
    homologated = homologate_frame(raw, official_headers, source_row)
    homologated["LINEA_ORIGEN"] = [int(index) + (2 if has_header else 1) for index in range(len(homologated))]
    homologated["HOJA_ORIGEN"] = sheet_name
    return homologated


def total_hours_row(row: pd.Series) -> float | None:
    """Calcula la suma contractual para una fila historica."""

    values = [
        parse_number(row.get("NUM_HORAS_PLANTA", "")),
        parse_number(row.get("NUM_HORAS_CONTRATA", "")),
        parse_number(row.get("NUM_HORAS_HONORARIOS", "")),
    ]
    if any(value is None for value in values):
        return None
    return sum(value or 0.0 for value in values)


def predominant_contract(row: pd.Series) -> str:
    """Clasifica el tipo contractual predominante como KPI institucional."""

    values = {
        "PLANTA": parse_number(row.get("NUM_HORAS_PLANTA", "")),
        "CONTRATA": parse_number(row.get("NUM_HORAS_CONTRATA", "")),
        "HONORARIOS": parse_number(row.get("NUM_HORAS_HONORARIOS", "")),
    }
    if any(value is None for value in values.values()):
        return "SIN_HORAS_VALIDAS"
    positives = {key: value or 0.0 for key, value in values.items() if (value or 0.0) > 0}
    if not positives:
        return "SIN_HORAS_VALIDAS"
    max_value = max(positives.values())
    winners = [key for key, value in positives.items() if value == max_value]
    return winners[0] if len(winners) == 1 else "MIXTO_EMPATE"


def hour_band(row: pd.Series) -> str:
    """Clasifica tramo horario institucional usando suma contractual base."""

    total = total_hours_row(row)
    if total is None or total <= 0:
        return "HORAS_NO_VALIDAS"
    if total < 11:
        return "MENOS_DE_11"
    if total <= 22:
        return "11_A_22"
    if total <= 38:
        return "23_A_38"
    return "39_O_MAS"


def row_validation(row: pd.Series) -> tuple[str, str, str]:
    """Valida identidad y vigencia de una fila longitudinal."""

    warnings: list[str] = []
    errors: list[str] = []
    tipo = normalized_upper(row.get("TIPO_DOCUMENTO", ""))
    numero = normalize_document_number(tipo, row.get("NUM_DOCUMENTO", ""))
    dv = normalize_dv(tipo, row.get("DV", ""))
    if tipo not in {"R", "P"} or not numero:
        errors.append("DOCUMENTO_VACIO_O_TIPO_INVALIDO")
    if tipo == "R":
        expected = compute_rut_dv(numero)
        if expected is None:
            errors.append("RUT_FORMATO_INVALIDO")
        elif dv != expected:
            errors.append("RUT_DV_INVALIDO")
    if tipo == "P" and dv:
        warnings.append("PASAPORTE_CON_DV_NORMALIZADO_A_VACIO")
    if normalize_value(row.get("VIGENCIA", "")) not in {"0", "1"}:
        errors.append("VIGENCIA_INVALIDA")
    status = "ERROR" if errors else ("ADVERTENCIA" if warnings else "OK")
    return status, ";".join(warnings), ";".join(errors)


def build_longitudinal(
    source_decisions: pd.DataFrame,
    inventory: pd.DataFrame,
    official_headers: Sequence[str],
) -> pd.DataFrame:
    """Construye la tabla maestra longitudinal desde fuentes seleccionadas."""

    rows: list[pd.DataFrame] = []
    selected = source_decisions[source_decisions["archivo_seleccionado"].astype(str).ne("")]
    for _index, decision in selected.iterrows():
        source = inventory[inventory["fuente_id"].eq(decision["fuente_id"])].iloc[0].copy()
        source["anio_fuente"] = int(decision["anio"])
        frame = load_homologated_source(source, official_headers)
        if frame.empty:
            continue
        frame["ANIO"] = int(decision["anio"])
        frame["FUENTE_ID"] = decision["fuente_id"]
        frame["FUENTE_RUTA"] = source["path"]
        frame["FUENTE_SHA256"] = source["sha256"]
        frame["CLAVE_DOCUMENTAL"] = build_identifier_series(frame)
        frame["NOMBRE_COMPLETO_NORMALIZADO"] = (
            frame.get("NOMBRES", "").map(normalized_upper)
            + " "
            + frame.get("PRIMER_APELLIDO", "").map(normalized_upper)
            + " "
            + frame.get("SEGUNDO_APELLIDO", "").map(normalized_upper)
        ).str.strip()
        frame["TOTAL_HORAS_CONTRACTUALES"] = frame.apply(total_hours_row, axis=1)
        frame["TIPO_CONTRATO_PREDOMINANTE"] = frame.apply(predominant_contract, axis=1)
        frame["TRAMO_HORAS"] = frame.apply(hour_band, axis=1)
        frame["ES_VIGENTE"] = frame["VIGENCIA"].map(lambda value: normalize_value(value) == "1")
        validations = frame.apply(row_validation, axis=1)
        frame["ESTADO_VALIDACION"] = [item[0] for item in validations]
        frame["ADVERTENCIAS"] = [item[1] for item in validations]
        frame["ERRORES"] = [item[2] for item in validations]
        frame["ES_FUENTE_OFICIAL_ANUAL"] = True
        frame["ESTADO_FUENTE_ANUAL"] = decision["estado"]
        ordered = AUDIT_COLUMNS + list(official_headers) + ["TIPO_CONTRATO_PREDOMINANTE", "TRAMO_HORAS"]
        rows.append(frame[[column for column in ordered if column in frame.columns]])
    if not rows:
        return pd.DataFrame(columns=AUDIT_COLUMNS + list(official_headers))
    return pd.concat(rows, ignore_index=True)


def source_score(row: pd.Series) -> int:
    """Puntua una fuente candidata anual con criterios conservadores."""

    text = normalize_text(f"{row.get('relative_path', '')} {row.get('name', '')} {row.get('selected_sheet', '')}")
    score = 0
    if row.get("preliminary_classification") in {"POSIBLE_ARCHIVO_ENVIADO", "CANDIDATO_OFICIAL"}:
        score += 40
    if "OFICIAL" in text:
        score += 45
    if "PES_READY" in text:
        score += 35
    if "CARGA_IPSSVF" in text:
        score += 30
    if "PAC_IP_CIISA" in text:
        score += 25
    if "BACKUP" in text or "RESPALDO" in text:
        score -= 15
    if "PROBLEMA" in text or "ERROR" in text or "FALTANTE" in text:
        score -= 80
    if "ESTRUCTURA" in text or "INSTRUCTIVO" in text:
        score -= 100
    if int(row.get("personas_unicas", 0) or 0) > 0:
        score += 25
    if int(row.get("registros_vigentes", 0) or 0) > 0:
        score += 25
    if str(row.get("relative_path", "")).count("/") == 1:
        score += 10
    return score


def classify_source_state(best: pd.Series, ambiguous: bool) -> tuple[str, str, str, str]:
    """Asigna estado, confianza, aptitud y observacion a una fuente anual."""

    if ambiguous:
        return (
            "CANDIDATA_PENDIENTE_EVIDENCIA",
            "MEDIA",
            "NO_APTO_PARA_PUBLICACION",
            "Existen fuentes plausibles con puntaje equivalente; requiere revision humana.",
        )
    text = normalize_text(f"{best.get('relative_path', '')} {best.get('name', '')}")
    if "OFICIAL" in text:
        return (
            "OFICIAL_CONFIRMADA",
            "ALTA",
            "APTO_CON_ADVERTENCIAS",
            "Evidencia textual de oficialidad en nombre/ruta; verificar respaldo PES finalizado.",
        )
    if best.get("evidence_pes") == "SI" and best.get("evidence_finalized") == "SI":
        return (
            "OFICIAL_PROBABLE",
            "MEDIA_ALTA",
            "NO_APTO_PARA_PUBLICACION",
            "Fuente probable por ruta Enviados/PES_READY/VF, sin evidencia PES finalizada independiente.",
        )
    return (
        "CANDIDATA_PENDIENTE_EVIDENCIA",
        "MEDIA",
        "NO_APTO_PARA_PUBLICACION",
        "Fuente candidata sin evidencia suficiente de finalizacion PES.",
    )


def select_sources_by_year(inventory: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Selecciona una fuente anual y conserva comparacion de candidatos."""

    if inventory.empty:
        return pd.DataFrame(), pd.DataFrame()
    candidates = inventory.copy()
    candidates["anio"] = candidates[["year_from_path", "year_from_name", "year_from_content"]].bfill(axis=1).iloc[:, 0]
    candidates = candidates[candidates["anio"].notna()].copy()
    candidates["anio"] = candidates["anio"].astype(int)
    candidates["score"] = candidates.apply(source_score, axis=1)
    useful = candidates[candidates["score"] > 0].copy()
    comparisons = useful.sort_values(["anio", "score", "modified_at"], ascending=[True, False, False])
    decisions: list[dict[str, object]] = []
    for year, group in comparisons.groupby("anio"):
        group = group.sort_values(["score", "modified_at"], ascending=[False, False])
        best = group.iloc[0]
        second_score = int(group.iloc[1]["score"]) if len(group) > 1 else -9999
        ambiguous = len(group) > 1 and int(best["score"]) - second_score <= 5
        state, confidence, aptitude, observation = classify_source_state(best, ambiguous)
        decisions.append(
            {
                "anio": int(year),
                "fuente_id": best["fuente_id"],
                "archivo_seleccionado": best["path"],
                "hash": best["sha256"],
                "personas_vigentes": int(best.get("personas_unicas_vigentes", best.get("personas_unicas", 0)) or 0),
                "evidencia_principal": best["preliminary_classification"],
                "evidencia_secundaria": f"PES={best['evidence_pes']}; FINALIZADO={best['evidence_finalized']}; SCORE={best['score']}",
                "observaciones": observation,
                "nivel_confianza": confidence,
                "estado": state,
                "aptitud_kpi": aptitude,
            }
        )
    return pd.DataFrame(decisions), comparisons


def enrich_inventory_metrics(inventory: pd.DataFrame, official_headers: Sequence[str]) -> pd.DataFrame:
    """Agrega metricas tabulares y de personas al inventario."""

    enriched = inventory.copy()
    count_metric_columns = [
        "registros_vigentes",
        "registros_no_vigentes",
        "personas_unicas",
        "personas_unicas_vigentes",
        "duplicados",
        "presencia_planta",
        "presencia_contrata",
        "presencia_honorarios",
        "presencia_fuera_institucion",
    ]
    hour_metric_columns = [
        "suma_horas_planta",
        "suma_horas_contrata",
        "suma_horas_honorarios",
        "suma_horas_contractuales",
    ]
    for column in count_metric_columns:
        enriched[column] = 0
    for column in hour_metric_columns:
        enriched[column] = 0.0
    for index, row in enriched.iterrows():
        if row["preliminary_classification"] in {"REPORTE_ERROR_PES", "ARCHIVO_NO_APTO", "ESTRUCTURA_VACIA"}:
            continue
        temp = row.copy()
        temp["anio_fuente"] = int(row["year_from_path"] or row["year_from_name"] or row["year_from_content"] or 0)
        try:
            frame = load_homologated_source(temp, official_headers)
        except Exception:  # noqa: BLE001
            continue
        if frame.empty or "TIPO_DOCUMENTO" not in frame.columns:
            continue
        identifiers = build_identifier_series(frame)
        vigentes = frame["VIGENCIA"].map(lambda value: normalize_value(value) == "1") if "VIGENCIA" in frame.columns else pd.Series([False] * len(frame))
        enriched.loc[index, "registros_vigentes"] = int(vigentes.sum())
        enriched.loc[index, "registros_no_vigentes"] = int((~vigentes).sum())
        enriched.loc[index, "personas_unicas"] = int(identifiers[identifiers.str.strip().ne("||")].nunique())
        enriched.loc[index, "personas_unicas_vigentes"] = int(identifiers[vigentes].nunique())
        enriched.loc[index, "duplicados"] = int(identifiers.duplicated(keep=False).sum())
        for source_col, target_col in [
            ("NUM_HORAS_PLANTA", "suma_horas_planta"),
            ("NUM_HORAS_CONTRATA", "suma_horas_contrata"),
            ("NUM_HORAS_HONORARIOS", "suma_horas_honorarios"),
        ]:
            if source_col in frame.columns:
                values = [parse_number(value) or 0.0 for value in frame[source_col]]
                enriched.loc[index, target_col] = round(sum(values), 4)
        enriched.loc[index, "suma_horas_contractuales"] = round(
            float(enriched.loc[index, "suma_horas_planta"])
            + float(enriched.loc[index, "suma_horas_contrata"])
            + float(enriched.loc[index, "suma_horas_honorarios"]),
            4,
        )
        enriched.loc[index, "presencia_planta"] = int(float(enriched.loc[index, "suma_horas_planta"]) > 0)
        enriched.loc[index, "presencia_contrata"] = int(float(enriched.loc[index, "suma_horas_contrata"]) > 0)
        enriched.loc[index, "presencia_honorarios"] = int(float(enriched.loc[index, "suma_horas_honorarios"]) > 0)
        enriched.loc[index, "presencia_fuera_institucion"] = int("FUERA" in normalize_text(row["path"]))
    return enriched


def build_panel(
    longitudinal: pd.DataFrame,
    years: Sequence[int],
    source_years: set[int] | None = None,
) -> pd.DataFrame:
    """Construye matriz de presencia por clave documental y anio."""

    keys = sorted(longitudinal["CLAVE_DOCUMENTAL"].dropna().unique()) if not longitudinal.empty else []
    evaluable_years = set(years) if source_years is None else source_years
    rows: list[dict[str, object]] = []
    for key in keys:
        item = {"CLAVE_DOCUMENTAL": key}
        person = longitudinal[longitudinal["CLAVE_DOCUMENTAL"].eq(key)]
        present_years = set(person[person["ES_VIGENTE"]]["ANIO"].astype(int))
        for year in years:
            if year not in evaluable_years:
                item[str(year)] = pd.NA
            else:
                item[str(year)] = 1 if year in present_years else 0
        rows.append(item)
    columns = ["CLAVE_DOCUMENTAL"] + [str(year) for year in years]
    return pd.DataFrame(rows, columns=columns)


def pct(numerator: float, denominator: float) -> float | None:
    """Calcula porcentaje sin redondeo anticipado."""

    if denominator == 0:
        return None
    return (numerator / denominator) * 100


def compare_pair(
    longitudinal: pd.DataFrame,
    decisions: pd.DataFrame,
    year: int,
    next_year: int,
) -> tuple[dict[str, object], pd.DataFrame]:
    """Compara dos anos consecutivos y devuelve resumen y detalle."""

    base = longitudinal[(longitudinal["ANIO"].eq(year)) & (longitudinal["ES_VIGENTE"])].copy()
    comp = longitudinal[(longitudinal["ANIO"].eq(next_year)) & (longitudinal["ES_VIGENTE"])].copy()
    base_keys = set(base["CLAVE_DOCUMENTAL"])
    comp_keys = set(comp["CLAVE_DOCUMENTAL"])
    remain = base_keys & comp_keys
    rotate = base_keys - comp_keys
    new = comp_keys - base_keys
    decision_base = decisions[decisions["anio"].eq(year)]
    decision_comp = decisions[decisions["anio"].eq(next_year)]
    status = "NO_EVALUABLE" if decision_base.empty or decision_comp.empty else "RESULTADO_EXPLORATORIO_NO_PUBLICABLE"
    rows: list[dict[str, object]] = []
    for key in sorted(base_keys | comp_keys):
        state = "PERMANECE" if key in remain else ("ROTA" if key in rotate else "NUEVO_INGRESO")
        rows.append(
            {
                "ANIO_BASE": year,
                "ANIO_COMPARACION": next_year,
                "CLAVE_DOCUMENTAL": key,
                "ESTADO_ROTACION": state,
                "PERMANECE": int(state == "PERMANECE"),
                "ROTA": int(state == "ROTA"),
                "NUEVO": int(state == "NUEVO_INGRESO"),
            }
        )
    detail = pd.DataFrame(rows)
    summary = {
        "ANIO_BASE": year,
        "ANIO_COMPARACION": next_year,
        "DOTACION_BASE": len(base_keys),
        "DOTACION_COMPARACION": len(comp_keys),
        "PERMANECEN": len(remain),
        "ROTAN": len(rotate),
        "NUEVOS_INGRESOS": len(new),
        "TASA_ROTACION_SIES": pct(len(rotate), len(base_keys)),
        "TASA_RETENCION_INSTITUCIONAL": pct(len(remain), len(base_keys)),
        "VARIACION_NETA_DOTACION": len(comp_keys) - len(base_keys),
        "VARIACION_PORCENTUAL_DOTACION": pct(len(comp_keys) - len(base_keys), len(base_keys)),
        "ESTADO_APTITUD": status,
        "ADVERTENCIAS": "No publicar sin evidencia finalizada PES si alguna fuente anual no esta confirmada.",
    }
    if not decision_base.empty:
        summary["FUENTE_BASE"] = decision_base.iloc[0]["archivo_seleccionado"]
        summary["SHA256_FUENTE_BASE"] = decision_base.iloc[0]["hash"]
    if not decision_comp.empty:
        summary["FUENTE_COMPARACION"] = decision_comp.iloc[0]["archivo_seleccionado"]
        summary["SHA256_FUENTE_COMPARACION"] = decision_comp.iloc[0]["hash"]
    return summary, detail


def build_pair_tables(longitudinal: pd.DataFrame, decisions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calcula KPI historico y detalle para pares consecutivos."""

    years = sorted(decisions["anio"].astype(int).unique()) if not decisions.empty else []
    summaries: list[dict[str, object]] = []
    details: list[pd.DataFrame] = []
    for year, next_year in zip(years, years[1:]):
        if next_year != year + 1:
            continue
        summary, detail = compare_pair(longitudinal, decisions, year, next_year)
        summaries.append(summary)
        details.append(detail)
    kpi = pd.DataFrame(summaries)
    detail_columns = [
        "ANIO_BASE",
        "ANIO_COMPARACION",
        "CLAVE_DOCUMENTAL",
        "ESTADO_ROTACION",
        "PERMANECE",
        "ROTA",
        "NUEVO",
    ]
    detail_frame = pd.concat(details, ignore_index=True) if details else pd.DataFrame(columns=detail_columns)
    comparability = kpi[["ANIO_BASE", "ANIO_COMPARACION", "ESTADO_APTITUD", "ADVERTENCIAS"]].copy() if not kpi.empty else pd.DataFrame(columns=["ANIO_BASE", "ANIO_COMPARACION", "ESTADO_APTITUD", "ADVERTENCIAS"])
    if not comparability.empty:
        comparability["COMPARABILIDAD"] = "NO_DETERMINABLE"
    return kpi, detail_frame, comparability


def enrich_pair_detail(detail: pd.DataFrame, longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Agrega atributos de anio base al detalle por par anual."""

    if detail.empty:
        return detail
    base_attrs = longitudinal[
        [
            "ANIO",
            "CLAVE_DOCUMENTAL",
            "SEXO",
            "NIVEL_FORMACION_ACADEMICO",
            "CARGO_NORMALIZADO",
            "JERARQUIA_ACADEMICA_OCDE",
            "NOMBRE_PRINCIPAL_PROGRAMA",
            "NIVEL_SUPERIOR_ADSCRIPCION",
            "NIVEL_SECUNDARIO_ADSCRIPCION",
            "COMUNA_MAYOR_FUNCION",
            "TRAMO_HORAS",
            "TIPO_CONTRATO_PREDOMINANTE",
        ]
    ].rename(columns={"ANIO": "ANIO_BASE"})
    return detail.merge(base_attrs, on=["ANIO_BASE", "CLAVE_DOCUMENTAL"], how="left")


def desaggregate(detail: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    """Calcula rotacion anual por una variable del anio base."""

    output_columns = [
        "VARIABLE",
        "ANIO_BASE",
        "ANIO_COMPARACION",
        "CATEGORIA",
        "DOTACION_BASE",
        "PERMANECEN",
        "ROTAN",
        "TASA_ROTACION",
        "CASOS_DATO_FALTANTE",
        "ESTADO_APTITUD",
    ]
    if detail.empty or column not in detail.columns:
        return pd.DataFrame(columns=output_columns)
    rows: list[dict[str, object]] = []
    base = detail[detail["ESTADO_ROTACION"].isin(["PERMANECE", "ROTA"])].copy()
    for (year, next_year, value), group in base.groupby(["ANIO_BASE", "ANIO_COMPARACION", column], dropna=False):
        total = len(group)
        rotan = int(group["ROTA"].sum())
        rows.append(
            {
                "VARIABLE": label,
                "ANIO_BASE": year,
                "ANIO_COMPARACION": next_year,
                "CATEGORIA": normalize_value(value) or "SIN_DATO_EN_ARCHIVO",
                "DOTACION_BASE": total,
                "PERMANECEN": int(group["PERMANECE"].sum()),
                "ROTAN": rotan,
                "TASA_ROTACION": pct(rotan, total),
                "CASOS_DATO_FALTANTE": int(group[column].map(lambda item: normalize_value(item) == "").sum()),
                "ESTADO_APTITUD": "RESULTADO_EXPLORATORIO_NO_PUBLICABLE",
            }
        )
    return pd.DataFrame(rows, columns=output_columns)


def build_desaggregations(detail: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Construye desagregaciones historicas requeridas."""

    specs = {
        "sexo": ("SEXO", "SEXO"),
        "formacion": ("NIVEL_FORMACION_ACADEMICO", "FORMACION"),
        "tramo_horas": ("TRAMO_HORAS", "TRAMO_HORAS"),
        "cargo": ("CARGO_NORMALIZADO", "CARGO"),
        "jerarquia": ("JERARQUIA_ACADEMICA_OCDE", "JERARQUIA"),
        "programa": ("NOMBRE_PRINCIPAL_PROGRAMA", "PROGRAMA"),
        "adscripcion": ("NIVEL_SUPERIOR_ADSCRIPCION", "ADSCRIPCION"),
    }
    return {key: desaggregate(detail, column, label) for key, (column, label) in specs.items()}


def build_identity_issues(longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Audita cambios de identidad para una misma clave documental."""

    columns = ["CLAVE_DOCUMENTAL", "CODIGO", "SEVERIDAD", "ANIOS", "CAMPO", "VALORES_DISTINTOS"]
    rows: list[dict[str, object]] = []
    if longitudinal.empty:
        return pd.DataFrame(columns=columns)
    for key, group in longitudinal.groupby("CLAVE_DOCUMENTAL"):
        for field, code, severity in [
            ("NOMBRES", "NOMBRE_DISTINTO_ENTRE_ANIOS", "ADVERTENCIA"),
            ("PRIMER_APELLIDO", "APELLIDO_DISTINTO_ENTRE_ANIOS", "ADVERTENCIA"),
            ("SEGUNDO_APELLIDO", "APELLIDO_DISTINTO_ENTRE_ANIOS", "ADVERTENCIA"),
            ("SEXO", "SEXO_DISTINTO_ENTRE_ANIOS", "CRITICO"),
            ("FECHA_NACIMIENTO", "FECHA_NACIMIENTO_DISTINTA_ENTRE_ANIOS", "CRITICO"),
            ("NACIONALIDAD", "NACIONALIDAD_DISTINTA_ENTRE_ANIOS", "ADVERTENCIA"),
        ]:
            if field not in group.columns:
                continue
            normalized = group[field].map(normalized_upper)
            if normalized.nunique(dropna=True) > 1:
                rows.append(
                    {
                        "CLAVE_DOCUMENTAL": key,
                        "CODIGO": code,
                        "SEVERIDAD": severity,
                        "ANIOS": ",".join(map(str, sorted(group["ANIO"].astype(int).unique()))),
                        "CAMPO": field,
                        "VALORES_DISTINTOS": normalized.nunique(dropna=True),
                    }
                )
    return pd.DataFrame(rows, columns=columns)


def build_duplicates(longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Detecta duplicados dentro de cada fuente anual seleccionada."""

    if longitudinal.empty:
        return pd.DataFrame()
    duplicates = longitudinal[longitudinal.duplicated(["ANIO", "CLAVE_DOCUMENTAL"], keep=False)].copy()
    if duplicates.empty:
        return pd.DataFrame(columns=["ANIO", "CLAVE_DOCUMENTAL", "TIPO_DUPLICADO", "FILAS"])
    rows: list[dict[str, object]] = []
    for (year, key), group in duplicates.groupby(["ANIO", "CLAVE_DOCUMENTAL"]):
        tipo = "DUPLICADO_EXACTO" if group.drop(columns=["LINEA_ORIGEN"], errors="ignore").drop_duplicates().shape[0] == 1 else "DUPLICADO_CONFLICTIVO"
        rows.append({"ANIO": year, "CLAVE_DOCUMENTAL": key, "TIPO_DUPLICADO": tipo, "FILAS": len(group)})
    return pd.DataFrame(rows)


def build_conflicts(longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Detecta conflictos documentales por numero y tipo."""

    columns = ["NUM_DOCUMENTO_NORMALIZADO", "CODIGO", "ANIOS"]
    if longitudinal.empty:
        return pd.DataFrame(columns=columns)
    frame = longitudinal.copy()
    frame["NUM_NORM"] = frame.apply(lambda row: normalize_document_number(row.get("TIPO_DOCUMENTO", ""), row.get("NUM_DOCUMENTO", "")), axis=1)
    rows: list[dict[str, object]] = []
    for number, group in frame.groupby("NUM_NORM"):
        if not number:
            continue
        if group["DV"].map(lambda value: normalize_dv("R", value)).nunique(dropna=True) > 1:
            rows.append({"NUM_DOCUMENTO_NORMALIZADO": number, "CODIGO": "CONFLICTO_RUT_DV", "ANIOS": ",".join(map(str, sorted(group["ANIO"].astype(int).unique())))})
        if group["TIPO_DOCUMENTO"].map(normalized_upper).nunique(dropna=True) > 1:
            rows.append({"NUM_DOCUMENTO_NORMALIZADO": number, "CODIGO": "CONFLICTO_TIPO_DOCUMENTO", "ANIOS": ",".join(map(str, sorted(group["ANIO"].astype(int).unique())))})
    return pd.DataFrame(rows, columns=columns)


def build_reentries(panel: pd.DataFrame) -> pd.DataFrame:
    """Identifica reingresos historicos sin alterar rotaciones previas."""

    columns = ["CLAVE_DOCUMENTAL", "ANIO_REINGRESO", "TIPO_EVENTO"]
    if panel.empty:
        return pd.DataFrame(columns=columns)
    year_columns = [column for column in panel.columns if str(column).isdigit()]
    rows: list[dict[str, object]] = []
    for _index, row in panel.iterrows():
        seen_present = False
        seen_absent_after_present = False
        for column in year_columns:
            if pd.isna(row[column]):
                continue
            state = int(row[column])
            if state == 1 and seen_absent_after_present:
                rows.append({"CLAVE_DOCUMENTAL": row["CLAVE_DOCUMENTAL"], "ANIO_REINGRESO": int(column), "TIPO_EVENTO": "REINGRESO"})
                break
            if state == 1:
                seen_present = True
            elif state == 0 and seen_present:
                seen_absent_after_present = True
    return pd.DataFrame(rows, columns=columns)


def build_changes(detail: pd.DataFrame, longitudinal: pd.DataFrame) -> pd.DataFrame:
    """Identifica cambios contractuales y academicos entre pares para permanentes."""

    columns = ["ANIO_BASE", "ANIO_COMPARACION", "CLAVE_DOCUMENTAL", "CAMPOS_CAMBIADOS", "CANTIDAD_CAMBIOS"]
    if detail.empty:
        return pd.DataFrame(columns=columns)
    remain = detail[detail["ESTADO_ROTACION"].eq("PERMANECE")]
    rows: list[dict[str, object]] = []
    fields = [
        "NUM_HORAS_PLANTA",
        "NUM_HORAS_CONTRATA",
        "NUM_HORAS_HONORARIOS",
        "TOTAL_HORAS_CONTRACTUALES",
        "PRINCIPAL_CARGO_ACADEMICO",
        "CARGO_NORMALIZADO",
        "NOMBRE_PRINCIPAL_PROGRAMA",
        "NIVEL_SUPERIOR_ADSCRIPCION",
        "NIVEL_SECUNDARIO_ADSCRIPCION",
        "COMUNA_MAYOR_FUNCION",
        "NIVEL_FORMACION_ACADEMICO",
        "JERARQUIA_ACADEMICA_OCDE",
        "TIPO_CONTRATO_PREDOMINANTE",
    ]
    indexed = longitudinal.set_index(["ANIO", "CLAVE_DOCUMENTAL"], drop=False)
    for _index, item in remain.iterrows():
        base_key = (item["ANIO_BASE"], item["CLAVE_DOCUMENTAL"])
        comp_key = (item["ANIO_COMPARACION"], item["CLAVE_DOCUMENTAL"])
        if base_key not in indexed.index or comp_key not in indexed.index:
            continue
        base = indexed.loc[base_key]
        comp = indexed.loc[comp_key]
        if isinstance(base, pd.DataFrame) or isinstance(comp, pd.DataFrame):
            continue
        changed_fields = [
            field
            for field in fields
            if field in base.index and field in comp.index and normalize_value(base[field]) != normalize_value(comp[field])
        ]
        if changed_fields:
            rows.append(
                {
                    "ANIO_BASE": item["ANIO_BASE"],
                    "ANIO_COMPARACION": item["ANIO_COMPARACION"],
                    "CLAVE_DOCUMENTAL": item["CLAVE_DOCUMENTAL"],
                    "CAMPOS_CAMBIADOS": ";".join(changed_fields),
                    "CANTIDAD_CAMBIOS": len(changed_fields),
                }
            )
    return pd.DataFrame(rows, columns=columns)


def historical_summary(kpi: pd.DataFrame, reingresos: pd.DataFrame, years: Sequence[int]) -> dict[str, object]:
    """Construye metricas agregadas sin reemplazar la tasa anual oficial."""

    if kpi.empty:
        return {"anios": list(years), "promedio_simple_tasas_anuales": None, "tasa_ponderada_historica": None}
    rates = kpi["TASA_ROTACION_SIES"].dropna()
    total_rotan = float(kpi["ROTAN"].sum())
    total_base = float(kpi["DOTACION_BASE"].sum())
    return {
        "anios": list(years),
        "promedio_simple_tasas_anuales": float(rates.mean()) if not rates.empty else None,
        "tasa_ponderada_historica": pct(total_rotan, total_base),
        "total_reingresos": int(len(reingresos)),
    }


def requested_years(decisions: pd.DataFrame, desde_anio: int | None, hasta_anio: int | None) -> list[int]:
    """Determina el rango de anos a representar en panel y resumen."""

    decision_years = sorted(decisions["anio"].astype(int).unique()) if not decisions.empty else []
    if desde_anio is None and hasta_anio is None:
        return decision_years
    lower = desde_anio if desde_anio is not None else (min(decision_years) if decision_years else None)
    upper = hasta_anio if hasta_anio is not None else (max(decision_years) if decision_years else None)
    if lower is None or upper is None:
        return []
    return list(range(int(lower), int(upper) + 1))


def filter_inventory_range(inventory: pd.DataFrame, desde_anio: int | None, hasta_anio: int | None) -> pd.DataFrame:
    """Filtra candidatos por rango anual sin borrar el inventario enriquecido."""

    if inventory.empty or (desde_anio is None and hasta_anio is None):
        return inventory.copy()
    working = inventory.copy()
    years = working[["year_from_path", "year_from_name", "year_from_content"]].bfill(axis=1).iloc[:, 0]
    mask = years.notna()
    if desde_anio is not None:
        mask = mask & (years.astype(float) >= desde_anio)
    if hasta_anio is not None:
        mask = mask & (years.astype(float) <= hasta_anio)
    return working[mask].copy()


def build_historical_tables(
    inventory: pd.DataFrame,
    official_headers: Sequence[str],
    desde_anio: int | None = None,
    hasta_anio: int | None = None,
) -> HistoricalTables:
    """Ejecuta seleccion, longitudinal, panel, KPI y validaciones historicas."""

    enriched_inventory = enrich_inventory_metrics(inventory, official_headers)
    ranged_inventory = filter_inventory_range(enriched_inventory, desde_anio, hasta_anio)
    decisions, candidate_comparison = select_sources_by_year(ranged_inventory)
    longitudinal = build_longitudinal(decisions, enriched_inventory, official_headers)
    decision_years = set(decisions["anio"].astype(int)) if not decisions.empty else set()
    years = requested_years(decisions, desde_anio, hasta_anio)
    panel = build_panel(longitudinal, years, decision_years)
    kpi, detail, comparability = build_pair_tables(longitudinal, decisions)
    detail = enrich_pair_detail(detail, longitudinal)
    permanecen = detail[detail["ESTADO_ROTACION"].eq("PERMANECE")].copy() if not detail.empty else pd.DataFrame()
    rotan = detail[detail["ESTADO_ROTACION"].eq("ROTA")].copy() if not detail.empty else pd.DataFrame()
    nuevos = detail[detail["ESTADO_ROTACION"].eq("NUEVO_INGRESO")].copy() if not detail.empty else pd.DataFrame()
    reingresos = build_reentries(panel)
    cambios = build_changes(detail, longitudinal)
    desagregaciones = build_desaggregations(detail)
    identidad = build_identity_issues(longitudinal)
    duplicados = build_duplicates(longitudinal)
    conflictos = build_conflicts(longitudinal)
    resumen = historical_summary(kpi, reingresos, years)
    return HistoricalTables(
        inventory=enriched_inventory,
        source_decisions=decisions,
        candidate_comparison=candidate_comparison,
        longitudinal=longitudinal,
        panel=panel,
        kpi=kpi,
        detail=detail,
        permanecen=permanecen,
        rotan=rotan,
        nuevos=nuevos,
        reingresos=reingresos,
        cambios=cambios,
        desagregaciones=desagregaciones,
        identidad=identidad,
        duplicados=duplicados,
        conflictos=conflictos,
        comparability=comparability,
        resumen=resumen,
    )
