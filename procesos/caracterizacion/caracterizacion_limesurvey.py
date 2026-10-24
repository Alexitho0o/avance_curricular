#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seleccion y validacion trazable de archivos de entrada."""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import pandas as pd
from caracterizacion_archivos import InputFileValidationError, validate_input_file


TOKEN_ID_RE = re.compile(r"tokens[^0-9]*(?P<survey_id>\d{4,})", re.IGNORECASE)
RESULTS_ID_RE = re.compile(r"results[-_\s]*survey[^0-9]*(?P<survey_id>\d{4,})", re.IGNORECASE)


# Catálogo institucional único para decidir si una celda de respuesta aporta
# información. La comparación se realiza después de ``strip()`` y ``lower()``;
# los nulos reales de pandas se gobiernan antes de convertir el valor a texto.
RESPUESTAS_INVALIDAS_NORMALIZADAS = frozenset({
    "",
    "-",
    "--",
    ".",
    "n/a",
    "n / a",
    "n.a.",
    "na",
    "no aplica",
    "nan",
    "null",
    "none",
    "sin info",
    "sin informacion",
    "sin información",
})

LIMESURVEY_DEDUP_AUDIT_COLUMNS = (
    "token",
    "cantidad_registros",
    "registros_completos",
    "registros_incompletos",
    "ID seleccionado",
    "fecha seleccionada",
    "criterio de selección",
    "IDs descartados",
    "estado final",
    "observación",
)

LIMESURVEY_DEDUP_DISCARD_COLUMNS = (
    "token",
    "ID seleccionado",
    "ID descartado",
    "fila física seleccionada",
    "fila física descartada",
    "submitdate seleccionado",
    "submitdate descartado",
    "datestamp seleccionado",
    "datestamp descartado",
    "estado seleccionado",
    "estado descartado",
    "criterio de selección",
    "motivo descarte",
)

TOKEN_SIGNATURE_ALIASES = {
    "token", "firstname", "lastname", "email", "emailstatus", "completed",
    "usesleft", "validfrom", "validuntil", "tid", "language", "invited",
    "reminded", "remindercount",
}
RESULTS_SIGNATURE_ALIASES = {
    "submitdate", "datestamp", "lastpage", "startdate", "startlanguage",
    "seed", "ipaddr", "refurl",
}

KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "token": (
        "token", "participanttoken", "participant_token", "tokenparticipante",
        "tokencol", "survey_token",
    ),
    "document": (
        "rut", "run", "nrodoc", "nro_doc", "documento", "nrodocumento",
        "numero_documento", "numdocumento", "nro_docum", "nro_docume",
        "nrodocument", "document",
    ),
    "email": (
        "email", "mail", "correo", "correoelectronico", "e-mail",
        "correo_electronico",
    ),
    "id": (
        "id", "participantid", "participant_id", "tid", "sid", "responseid",
        "response_id",
    ),
}

KEY_PRIORITY = {"token": 4, "document": 3, "email": 2, "id": 1}

MATRICULA_EXPECTED_BY_POSITION = {
    1: ("CODCLI",),
    2: ("CODCARPR",),
    3: ("NOMBRE_L", "NOMBREL"),
    4: ("ANOMATRICULA",),
    5: ("PERIODOMATRICULA",),
    6: ("ANOINGRESO",),
    7: ("PERIODOINGRESO",),
    8: ("FECHAMATRICULA",),
    9: ("JORNADA",),
    10: ("RUT",),
    11: ("NOMBRE",),
    12: ("SEXO",),
    22: ("FONOACTUAL", "FONO"),
    23: ("MAIL",),
    24: ("MAIL_INST", "MAILINST"),
    56: ("ESTADOACADEMICO",),
    57: ("SITUACION",),
    59: ("NIVEL",),
    61: ("CON_FIRMA", "CONFIRMA"),
    63: ("SEDE",),
}


class LimeSurveySelectionError(ValueError):
    """Error recuperable al seleccionar entradas."""


class LimeSurveyCoherenceError(ValueError):
    """Error recuperable de coherencia entre matricula, tokens y resultados."""


class LimeSurveyDeduplicationError(ValueError):
    """Error estructural al reducir resultados LimeSurvey a una fila por token."""


def es_respuesta_valida(valor: Any) -> bool:
    """Indica si ``valor`` contiene una respuesta institucionalmente utilizable.

    Los nulos reales se evalúan antes de convertir a texto para evitar la
    regresión observada con pandas 3, donde ``astype(str)`` puede conservar un
    escalar NaN que luego se interpreta erróneamente como texto no vacío.
    """
    if valor is None:
        return False
    try:
        if bool(pd.isna(valor)):
            return False
    except (TypeError, ValueError):
        # El contrato es escalar. Para objetos no escalares, su representación
        # textual solo se considerará válida si no pertenece al catálogo.
        pass
    normalizado = str(valor).strip().lower()
    return normalizado not in RESPUESTAS_INVALIDAS_NORMALIZADAS


def mascara_respuestas_validas(serie: pd.Series) -> pd.Series:
    """Vectoriza :func:`es_respuesta_valida` conservando el índice original."""
    if not isinstance(serie, pd.Series):
        raise TypeError("mascara_respuestas_validas requiere una Series de pandas.")
    return serie.map(es_respuesta_valida).astype(bool)


@dataclass(frozen=True)
class KeyCandidate:
    column: str
    canonical: str
    unique_count: int
    non_empty_count: int
    priority: int


@dataclass(frozen=True)
class ContentFile:
    path: Path
    kind: str
    name_id: str | None
    mtime: float
    size: int
    rows: int
    columns: tuple[str, ...]
    key_candidates: tuple[KeyCandidate, ...] = ()
    response_date_col: str | None = None
    score: int = 0
    reason: str = ""

    def best_key(self) -> KeyCandidate | None:
        if not self.key_candidates:
            return None
        return sorted(
            self.key_candidates,
            key=lambda k: (k.priority, k.unique_count, k.non_empty_count, len(k.column)),
            reverse=True,
        )[0]


@dataclass(frozen=True)
class PairEvaluation:
    tokens_path: Path
    results_path: Path
    tokens_key: str
    results_key: str
    key_kind: str
    coincidencias: int
    cobertura_pct: float
    tokens_unicos: int
    resultados_unicos: int
    pair_mtime: float


@dataclass(frozen=True)
class LimeSurveyPair:
    tokens: ContentFile
    results: ContentFile
    evaluation: PairEvaluation
    evaluated_pairs: tuple[PairEvaluation, ...] = field(default_factory=tuple)

    @property
    def survey_id(self) -> str:
        if self.tokens.name_id and self.tokens.name_id == self.results.name_id:
            return self.tokens.name_id
        if self.tokens.name_id or self.results.name_id:
            return f"tokens={self.tokens.name_id or 'sin_id'}; resultados={self.results.name_id or 'sin_id'}"
        return "sin_id_en_nombre"

    @property
    def tokens_path(self) -> Path:
        return self.tokens.path

    @property
    def results_path(self) -> Path:
        return self.results.path

    @property
    def tokens_mtime(self) -> float:
        return self.tokens.mtime

    @property
    def results_mtime(self) -> float:
        return self.results.mtime

    @property
    def tokens_key(self) -> str:
        return self.evaluation.tokens_key

    @property
    def results_key(self) -> str:
        return self.evaluation.results_key

    @property
    def key_kind(self) -> str:
        return self.evaluation.key_kind


@dataclass(frozen=True)
class LimeSurveyDedupResult:
    """Resultado canónico de seleccionar una respuesta física por token."""

    resultados_unicos: pd.DataFrame
    auditoria: pd.DataFrame
    descartes: pd.DataFrame
    metricas: dict[str, int]
    token_col: str
    submitdate_col: str | None
    datestamp_col: str | None
    response_id_col: str | None


def _unidecode(value: Any) -> str:
    try:
        from unidecode import unidecode
        return unidecode("" if value is None else str(value))
    except Exception:
        return "" if value is None else str(value)


def _norm_header(value: Any) -> str:
    txt = _unidecode(value).strip().lower()
    return re.sub(r"[^a-z0-9]+", "", txt)


def _norm_header_layout(value: Any) -> str:
    return re.sub(r"[\s_\-]+", "", _unidecode(value).strip().upper())


def extract_survey_id(filename: str | Path, kind: str | None = None) -> str | None:
    """Extrae un ID numerico del nombre solo como metadato informativo."""
    name = Path(filename).name
    patterns: Sequence[re.Pattern[str]]
    if kind == "tokens":
        patterns = (TOKEN_ID_RE,)
    elif kind == "results":
        patterns = (RESULTS_ID_RE,)
    else:
        patterns = (TOKEN_ID_RE, RESULTS_ID_RE)
    for pattern in patterns:
        match = pattern.search(name)
        if match:
            return match.group("survey_id")
    return None


def _detect_csv_encoding(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            path.read_text(encoding=encoding)
            return encoding
        except Exception:
            continue
    return "utf-8"


def _detect_csv_sep(path: Path, encoding: str) -> str:
    try:
        sample = path.read_text(encoding=encoding, errors="replace")[:20000]
        return csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"]).delimiter
    except Exception:
        return ";"


def read_input_frame(path: str | Path):
    """Lee CSV/XLSX con dtype=str. Importa pandas solo al ejecutar."""
    import pandas as pd

    try:
        p = validate_input_file(path)
    except InputFileValidationError as error:
        raise LimeSurveySelectionError(str(error)) from error
    ext = p.suffix.lower()
    if ext == ".csv":
        enc = _detect_csv_encoding(p)
        sep = _detect_csv_sep(p, enc)
        try:
            return pd.read_csv(p, encoding=enc, sep=sep, dtype=str, on_bad_lines="skip")
        except (OSError, ValueError, pd.errors.EmptyDataError) as error:
            raise LimeSurveySelectionError(f'No se pudo leer el CSV {p.name}: {error}') from error
    if ext in {".xlsx", ".xlsm", ".xls"}:
        engine = "openpyxl" if ext in {".xlsx", ".xlsm"} else None
        try:
            return pd.read_excel(p, engine=engine, dtype=str)
        except Exception as error:
            raise LimeSurveySelectionError(f'No se pudo leer el Excel {p.name}: {error}') from error
    raise LimeSurveySelectionError(f"Extension no soportada para lectura estructural: {p}")


def _name_bias(path: Path, expected: str) -> int:
    name = _norm_header(path.name)
    if expected == "tokens":
        return 2 if "tokens" in name else 0
    if expected == "results":
        return 2 if "resultssurvey" in name or "resultados" in name else 0
    if expected == "matricula":
        return 2 if "datosdealumnos" in name or "matricula" in name else 0
    return 0


def _non_empty_values(df, column: str) -> list[Any]:
    values = []
    for value in df[column].tolist():
        if not es_respuesta_valida(value):
            continue
        values.append(value)
    return values


def normalize_cross_value(value: Any, key_kind: str = "token") -> str:
    """Normaliza valores de cruce segun el tipo de clave detectada."""
    if value is None:
        return ""
    text = _unidecode(value).replace("\ufeff", "").replace("\u200b", "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return ""
    text = text.replace("\u00a0", " ")

    if key_kind == "email":
        return text.lower()

    if key_kind == "document":
        s = text.upper().replace(".", "").replace(" ", "")
        if "-" in s:
            s = s.split("-", 1)[0]
        return re.sub(r"\D", "", s)

    if key_kind in {"token", "id"}:
        s = text.strip()
        if "@" in s:
            return s.lower()
        s = s.replace(".", "").replace(" ", "").replace("\u00a0", "")
        if "-" in s and re.fullmatch(r"[0-9Kk\-]+", s):
            s = s.split("-", 1)[0]
        has_letters = bool(re.search(r"[A-Za-z]", s))
        if not has_letters:
            digits = re.sub(r"\D", "", s)
            return digits
        return re.sub(r"[^A-Za-z0-9]+", "", _unidecode(s).upper())

    return re.sub(r"\s+", " ", text).strip().upper()


def normalized_value_set(values: Iterable[Any], key_kind: str) -> set[str]:
    return {v for v in (normalize_cross_value(value, key_kind) for value in values) if v}


def _find_limesurvey_column(
    df: pd.DataFrame,
    explicit: str | None,
    aliases: Sequence[str],
) -> str | None:
    if explicit:
        if explicit not in df.columns:
            raise LimeSurveyDeduplicationError(
                f"No existe la columna LimeSurvey explícita {explicit!r}."
            )
        return str(explicit)

    normalized_columns = [(str(col), _norm_header(col)) for col in df.columns]
    normalized_aliases = [_norm_header(alias) for alias in aliases if _norm_header(alias)]
    for alias in normalized_aliases:
        for col, normalized in normalized_columns:
            if normalized == alias:
                return col
    for alias in sorted(normalized_aliases, key=len, reverse=True):
        for col, normalized in normalized_columns:
            if (
                (len(alias) <= 3 and normalized.startswith(alias))
                or (len(alias) > 3 and alias in normalized)
            ):
                return col
    return None


def _clean_response_id(value: Any) -> str:
    if value is None:
        return ""
    try:
        if bool(pd.isna(value)):
            return ""
    except (TypeError, ValueError):
        pass
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", str(value)).strip()
    if not text or text.lower() in {"nan", "none", "null", "nat", "<na>"}:
        return ""
    if re.fullmatch(r"-?\d+\.0+", text):
        return text.split(".", 1)[0]
    return text


def _parse_limesurvey_datetime(value: Any) -> pd.Timestamp | Any:
    if value is None:
        return pd.NaT
    try:
        if bool(pd.isna(value)):
            return pd.NaT
    except (TypeError, ValueError):
        pass
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return pd.NaT
    parsed = pd.Timestamp(parsed)
    if parsed.tzinfo is not None:
        # Excel no admite datetimes con zona horaria. Se conserva la hora local
        # declarada en la fuente y se elimina solo la metadata de zona.
        parsed = parsed.tz_localize(None)
    return parsed


def _discard_reason(selected: pd.Series, discarded: pd.Series) -> str:
    selected_complete = bool(selected["_COMPLETA"])
    discarded_complete = bool(discarded["_COMPLETA"])
    if selected_complete and not discarded_complete:
        return "INCOMPLETA_FRENTE_A_COMPLETA"
    if selected_complete and discarded_complete:
        return "COMPLETA_MENOS_PRIORITARIA"
    return "INCOMPLETA_MENOS_RECIENTE"


def deduplicar_resultados_limesurvey(
    resultados: pd.DataFrame,
    *,
    token_col: str | None = None,
    submitdate_col: str | None = None,
    datestamp_col: str | None = None,
    response_id_col: str | None = None,
    key_kind: str = "token",
) -> LimeSurveyDedupResult:
    """Reduce resultados LimeSurvey a exactamente una fila por token.

    La prioridad institucional es, en orden: respuesta completa (submitdate
    válido), submitdate más reciente, datestamp más reciente, ID de respuesta
    mayor como desempate estable y orden físico como último resguardo. Cuando
    no existe respuesta completa, se selecciona la última actividad válida por
    datestamp y se aplican los mismos desempates estables.

    La entrada nunca se modifica. Las filas sin token se excluyen de la tabla
    canónica y quedan registradas tanto en la auditoría como en ``descartes``.
    """
    if not isinstance(resultados, pd.DataFrame):
        raise LimeSurveyDeduplicationError(
            "La fuente de resultados LimeSurvey no es un DataFrame."
        )

    raw = resultados.copy(deep=True).reset_index(drop=True)
    token_col = _find_limesurvey_column(
        raw,
        token_col,
        ("token", "participant token", "codigo de acceso", "access code"),
    )
    if token_col is None:
        raise LimeSurveyDeduplicationError(
            "No se detectó una columna de token en resultados LimeSurvey."
        )
    submitdate_col = _find_limesurvey_column(
        raw,
        submitdate_col,
        ("submitdate", "fecha de envío", "fecha de envio"),
    )
    datestamp_col = _find_limesurvey_column(
        raw,
        datestamp_col,
        ("datestamp", "fecha de la última acción", "fecha de la ultima accion", "ultima accion"),
    )
    response_id_col = _find_limesurvey_column(
        raw,
        response_id_col,
        ("id de respuesta", "response id", "responseid", "id"),
    )

    raw["_TOKEN_RESULTADO"] = raw[token_col].map(
        lambda value: normalize_cross_value(value, key_kind)
    )
    raw["_SUBMITDATE_DT"] = (
        raw[submitdate_col].map(_parse_limesurvey_datetime)
        if submitdate_col is not None
        else pd.Series(pd.NaT, index=raw.index, dtype="datetime64[ns]")
    )
    raw["_DATESTAMP_DT"] = (
        raw[datestamp_col].map(_parse_limesurvey_datetime)
        if datestamp_col is not None
        else pd.Series(pd.NaT, index=raw.index, dtype="datetime64[ns]")
    )
    raw["_COMPLETA"] = raw["_SUBMITDATE_DT"].notna()
    raw["_ORDEN_FISICO"] = pd.RangeIndex(len(raw), dtype="int64")
    if response_id_col is None:
        raw["_ID_ORIGINAL"] = raw["_ORDEN_FISICO"].add(1).astype(str)
    else:
        raw["_ID_ORIGINAL"] = raw[response_id_col].map(_clean_response_id)
    raw["_ID_NUM"] = pd.to_numeric(raw["_ID_ORIGINAL"], errors="coerce")
    raw["_ID_TEXT"] = raw["_ID_ORIGINAL"].astype(str)

    valid = raw[raw["_TOKEN_RESULTADO"].ne("")].copy()
    counts = valid["_TOKEN_RESULTADO"].value_counts()
    duplicate_tokens = set(counts[counts.gt(1)].index)
    selected_rows: list[pd.Series] = []
    audit_rows: list[dict[str, Any]] = []
    discard_rows: list[dict[str, Any]] = []
    multiple_complete_tokens = 0
    mixed_state_tokens = 0

    for token, group in valid.groupby("_TOKEN_RESULTADO", sort=False, dropna=False):
        ordered = group.sort_values(
            [
                "_COMPLETA",
                "_SUBMITDATE_DT",
                "_DATESTAMP_DT",
                "_ID_NUM",
                "_ID_TEXT",
                "_ORDEN_FISICO",
            ],
            ascending=[False, False, False, False, False, False],
            kind="stable",
            na_position="last",
        )
        selected = ordered.iloc[0].copy()
        selected_rows.append(selected)
        completes = int(group["_COMPLETA"].sum())
        incompletes = int(len(group) - completes)
        multiple_complete_tokens += int(completes > 1)
        mixed_state_tokens += int(completes > 0 and incompletes > 0)
        if completes > 1:
            criterion = "COMPLETA_MAS_RECIENTE_SUBMITDATE_DATESTAMP_ID"
        elif completes == 1 and len(group) > 1:
            criterion = "PRIORIZA_COMPLETA_SOBRE_INCOMPLETA"
        elif completes == 1:
            criterion = "UNICO_REGISTRO_COMPLETO"
        elif len(group) > 1:
            criterion = "INCOMPLETA_ULTIMA_ACTIVIDAD_DATESTAMP_ID"
        else:
            criterion = "UNICO_REGISTRO_INCOMPLETO"

        final_state = "SI" if bool(selected["_COMPLETA"]) else "INCOMPLETO"
        selected_date = (
            selected["_SUBMITDATE_DT"]
            if final_state == "SI"
            else selected["_DATESTAMP_DT"]
        )
        discarded_group = ordered.iloc[1:]
        audit_rows.append(
            {
                "token": token,
                "cantidad_registros": int(len(group)),
                "registros_completos": completes,
                "registros_incompletos": incompletes,
                "ID seleccionado": selected["_ID_ORIGINAL"],
                "fecha seleccionada": selected_date,
                "criterio de selección": criterion,
                "IDs descartados": " | ".join(
                    str(value) for value in discarded_group["_ID_ORIGINAL"].tolist()
                ),
                "estado final": final_state,
                "observación": "Selección estable por token normalizado.",
            }
        )
        for _, discarded in discarded_group.iterrows():
            discard_rows.append(
                {
                    "token": token,
                    "ID seleccionado": selected["_ID_ORIGINAL"],
                    "ID descartado": discarded["_ID_ORIGINAL"],
                    "fila física seleccionada": int(selected["_ORDEN_FISICO"]) + 2,
                    "fila física descartada": int(discarded["_ORDEN_FISICO"]) + 2,
                    "submitdate seleccionado": selected["_SUBMITDATE_DT"],
                    "submitdate descartado": discarded["_SUBMITDATE_DT"],
                    "datestamp seleccionado": selected["_DATESTAMP_DT"],
                    "datestamp descartado": discarded["_DATESTAMP_DT"],
                    "estado seleccionado": final_state,
                    "estado descartado": "SI" if bool(discarded["_COMPLETA"]) else "INCOMPLETO",
                    "criterio de selección": criterion,
                    "motivo descarte": _discard_reason(selected, discarded),
                }
            )

    null_token_rows = raw[raw["_TOKEN_RESULTADO"].eq("")]
    for _, row in null_token_rows.iterrows():
        audit_rows.append(
            {
                "token": "",
                "cantidad_registros": 1,
                "registros_completos": int(bool(row["_COMPLETA"])),
                "registros_incompletos": int(not bool(row["_COMPLETA"])),
                "ID seleccionado": "",
                "fecha seleccionada": "",
                "criterio de selección": "NO_SELECCIONABLE_TOKEN_NULO",
                "IDs descartados": row["_ID_ORIGINAL"],
                "estado final": "NO_UTILIZABLE",
                "observación": "Fila excluida del cruce por token nulo.",
            }
        )
        discard_rows.append(
            {
                "token": "",
                "ID seleccionado": "",
                "ID descartado": row["_ID_ORIGINAL"],
                "fila física seleccionada": "",
                "fila física descartada": int(row["_ORDEN_FISICO"]) + 2,
                "submitdate seleccionado": "",
                "submitdate descartado": row["_SUBMITDATE_DT"],
                "datestamp seleccionado": "",
                "datestamp descartado": row["_DATESTAMP_DT"],
                "estado seleccionado": "NO_UTILIZABLE",
                "estado descartado": "SI" if bool(row["_COMPLETA"]) else "INCOMPLETO",
                "criterio de selección": "NO_SELECCIONABLE_TOKEN_NULO",
                "motivo descarte": "TOKEN_NULO",
            }
        )

    unique = (
        pd.DataFrame(selected_rows).reset_index(drop=True)
        if selected_rows
        else raw.iloc[0:0].copy()
    )
    unique["ESTADO_RESPUESTA_RESULTADO"] = unique["_COMPLETA"].map(
        {True: "SI", False: "INCOMPLETO"}
    )
    unique["ID_RESPUESTA_SELECCIONADO"] = unique["_ID_ORIGINAL"]
    unique["FECHA_RESPUESTA_SELECCIONADA"] = unique["_SUBMITDATE_DT"].combine_first(
        unique["_DATESTAMP_DT"]
    )
    if not unique["_TOKEN_RESULTADO"].is_unique:
        raise LimeSurveyDeduplicationError(
            "La tabla deduplicada de resultados no quedó única por token."
        )

    duplicate_discard_count = int(len(valid) - len(unique))
    metrics = {
        "filas_resultados_brutos": int(len(raw)),
        "tokens_resultados_unicos": int(unique["_TOKEN_RESULTADO"].nunique()),
        "filas_resultados_unicos": int(len(unique)),
        "tokens_duplicados_resultados_brutos": int(len(duplicate_tokens)),
        "filas_asociadas_duplicados": int(
            valid["_TOKEN_RESULTADO"].isin(duplicate_tokens).sum()
        ),
        "filas_token_nulo": int(len(null_token_rows)),
        "tokens_completos_unicos": int(
            unique["ESTADO_RESPUESTA_RESULTADO"].eq("SI").sum()
        ),
        "tokens_incompletos_unicos": int(
            unique["ESTADO_RESPUESTA_RESULTADO"].eq("INCOMPLETO").sum()
        ),
        "filas_descartadas_por_duplicacion": duplicate_discard_count,
        "filas_descartadas_totales": int(len(raw) - len(unique)),
        "tokens_con_multiples_completas": int(multiple_complete_tokens),
        "tokens_con_completas_e_incompletas": int(mixed_state_tokens),
    }
    return LimeSurveyDedupResult(
        resultados_unicos=unique,
        auditoria=pd.DataFrame(audit_rows, columns=LIMESURVEY_DEDUP_AUDIT_COLUMNS),
        descartes=pd.DataFrame(discard_rows, columns=LIMESURVEY_DEDUP_DISCARD_COLUMNS),
        metricas=metrics,
        token_col=token_col,
        submitdate_col=submitdate_col,
        datestamp_col=datestamp_col,
        response_id_col=response_id_col,
    )


def _key_candidates(df) -> tuple[KeyCandidate, ...]:
    out: list[KeyCandidate] = []
    seen: set[tuple[str, str]] = set()
    norm_to_cols: dict[str, list[str]] = {}
    for col in df.columns:
        norm_to_cols.setdefault(_norm_header(col), []).append(str(col))

    for canonical, aliases in KEY_ALIASES.items():
        alias_norms = {_norm_header(alias) for alias in aliases}
        for norm_col, columns in norm_to_cols.items():
            exact = norm_col in alias_norms
            contained = any(alias and alias in norm_col for alias in alias_norms if len(alias) >= 5)
            if not exact and not contained:
                continue
            for col in columns:
                key = (col, canonical)
                if key in seen:
                    continue
                seen.add(key)
                values = _non_empty_values(df, col)
                unique = normalized_value_set(values, canonical)
                if not unique:
                    continue
                out.append(
                    KeyCandidate(
                        column=col,
                        canonical=canonical,
                        unique_count=len(unique),
                        non_empty_count=len(values),
                        priority=KEY_PRIORITY.get(canonical, 0),
                    )
                )

    return tuple(sorted(out, key=lambda k: (k.priority, k.unique_count, k.column), reverse=True))


def _signature_count(df, aliases: set[str]) -> int:
    cols = {_norm_header(c) for c in df.columns}
    return sum(1 for alias in aliases if _norm_header(alias) in cols)


def _question_like_count(df) -> int:
    count = 0
    for col in df.columns:
        norm = _norm_header(col).upper()
        if re.match(r"^G\d+Q\d+", norm):
            count += 1
        elif re.match(r"^\d{5,}X\d+X\d+", norm):
            count += 1
    return count


def inspect_tokens_file(path: str | Path) -> ContentFile:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise LimeSurveySelectionError(f"No existe archivo tokens: {p}")
    if p.suffix.lower() not in {".csv", ".xlsx", ".xlsm"}:
        raise LimeSurveySelectionError(f"Tokens debe ser CSV/XLSX: {p.name}")
    df = read_input_frame(p)
    keys = _key_candidates(df)
    signature = _signature_count(df, TOKEN_SIGNATURE_ALIASES)
    score = signature + _name_bias(p, "tokens")
    if len(df) <= 0:
        raise LimeSurveySelectionError(f"Archivo tokens vacio: {p.name}")
    if signature < 4:
        raise LimeSurveySelectionError(
            f"Estructura tokens insuficiente en {p.name}: columnas LimeSurvey detectadas={signature}"
        )
    if not keys:
        raise LimeSurveySelectionError(f"No se pudo identificar clave de cruce en tokens: {p.name}")
    stat = p.stat()
    return ContentFile(
        path=p,
        kind="tokens",
        name_id=extract_survey_id(p.name, "tokens"),
        mtime=stat.st_mtime,
        size=stat.st_size,
        rows=int(len(df)),
        columns=tuple(str(c) for c in df.columns),
        key_candidates=keys,
        score=score,
        reason=f"signature={signature}",
    )


def inspect_results_file(path: str | Path) -> ContentFile:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise LimeSurveySelectionError(f"No existe archivo resultados: {p}")
    if p.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise LimeSurveySelectionError(f"Resultados debe ser XLSX: {p.name}")
    df = read_input_frame(p)
    keys = _key_candidates(df)
    signature = _signature_count(df, RESULTS_SIGNATURE_ALIASES)
    questions = _question_like_count(df)
    score = signature + min(questions, 5) + _name_bias(p, "results")
    if len(df) <= 0:
        raise LimeSurveySelectionError(f"Archivo resultados vacio: {p.name}")
    if signature < 1 and questions < 1:
        raise LimeSurveySelectionError(
            f"Estructura resultados insuficiente en {p.name}: sin columnas de respuesta/encuesta"
        )
    if not keys:
        raise LimeSurveySelectionError(f"No se pudo identificar clave de cruce en resultados: {p.name}")
    response_date = None
    # La completitud institucional depende de submitdate. El orden físico de
    # las columnas no puede hacer que datestamp se interprete como fecha de
    # envío, por lo que cada alternativa se busca en prioridad explícita.
    for target in ("submitdate", "datestamp", "startdate", "lastpage"):
        for col in df.columns:
            normalized = _norm_header(col)
            if normalized == target or normalized.startswith(target):
                response_date = str(col)
                break
        if response_date is not None:
            break
    stat = p.stat()
    return ContentFile(
        path=p,
        kind="results",
        name_id=extract_survey_id(p.name, "results"),
        mtime=stat.st_mtime,
        size=stat.st_size,
        rows=int(len(df)),
        columns=tuple(str(c) for c in df.columns),
        key_candidates=keys,
        response_date_col=response_date,
        score=score,
        reason=f"signature={signature}; questions={questions}",
    )


def _candidate_paths(downloads_dir: str | Path, suffixes: set[str]) -> list[Path]:
    base = Path(downloads_dir).expanduser()
    if not base.exists():
        return []
    return [
        path.resolve()
        for path in base.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes and not path.name.startswith("~$")
    ]


def _inspect_many(paths: Iterable[Path], inspector) -> list[ContentFile]:
    records: list[ContentFile] = []
    for path in paths:
        try:
            records.append(inspector(path))
        except Exception:
            continue
    return records


def _explicit_or_discovered(
    downloads_dir: str | Path,
    explicit_path: str | Path | None,
    suffixes: set[str],
    inspector,
) -> list[ContentFile]:
    if explicit_path:
        return [inspector(explicit_path)]
    return _inspect_many(_candidate_paths(downloads_dir, suffixes), inspector)


def _values_for_key(path: Path, column: str, key_kind: str) -> set[str]:
    df = read_input_frame(path)
    if column not in df.columns:
        return set()
    return normalized_value_set(_non_empty_values(df, column), key_kind)


def evaluate_pair(tokens: ContentFile, results: ContentFile) -> PairEvaluation:
    best: PairEvaluation | None = None
    common_kinds = {k.canonical for k in tokens.key_candidates} & {k.canonical for k in results.key_candidates}
    if common_kinds:
        max_priority = max(KEY_PRIORITY.get(kind, 0) for kind in common_kinds)
        allowed_kinds = {kind for kind in common_kinds if KEY_PRIORITY.get(kind, 0) == max_priority}
    else:
        allowed_kinds = set()
    for token_key in tokens.key_candidates:
        if token_key.canonical not in allowed_kinds:
            continue
        token_values = _values_for_key(tokens.path, token_key.column, token_key.canonical)
        if not token_values:
            continue
        for result_key in results.key_candidates:
            if result_key.canonical != token_key.canonical:
                continue
            result_values = _values_for_key(results.path, result_key.column, result_key.canonical)
            if not result_values:
                continue
            matches = len(token_values & result_values)
            denom = max(1, min(len(token_values), len(result_values)))
            coverage = round(matches / denom * 100.0, 2)
            item = PairEvaluation(
                tokens_path=tokens.path,
                results_path=results.path,
                tokens_key=token_key.column,
                results_key=result_key.column,
                key_kind=token_key.canonical,
                coincidencias=matches,
                cobertura_pct=coverage,
                tokens_unicos=len(token_values),
                resultados_unicos=len(result_values),
                pair_mtime=max(tokens.mtime, results.mtime),
            )
            if best is None or (
                item.coincidencias,
                item.cobertura_pct,
                KEY_PRIORITY.get(item.key_kind, 0),
                item.pair_mtime,
            ) > (
                best.coincidencias,
                best.cobertura_pct,
                KEY_PRIORITY.get(best.key_kind, 0),
                best.pair_mtime,
            ):
                best = item
    if best is None:
        return PairEvaluation(
            tokens_path=tokens.path,
            results_path=results.path,
            tokens_key="",
            results_key="",
            key_kind="",
            coincidencias=0,
            cobertura_pct=0.0,
            tokens_unicos=0,
            resultados_unicos=0,
            pair_mtime=max(tokens.mtime, results.mtime),
        )
    return best


def _min_coverage_threshold() -> float:
    raw = os.environ.get("CARACTERIZACION_LIMESURVEY_COBERTURA_MIN", "").strip()
    if not raw:
        return 1.0
    try:
        value = float(raw.replace(",", "."))
    except Exception:
        return 1.0
    if value <= 1:
        return value * 100.0
    return value


def select_latest_limesurvey_pair(
    downloads_dir: str | Path,
    *,
    tokens_path: str | Path | None = None,
    results_path: str | Path | None = None,
    min_coverage_pct: float | None = None,
) -> LimeSurveyPair:
    """
    Selecciona tokens/results por estructura y compatibilidad real de contenido.

    Los numeros del nombre se conservan como metadato, pero no bloquean ni
    determinan la compatibilidad.
    """
    tokens_records = _explicit_or_discovered(
        downloads_dir,
        tokens_path,
        {".csv", ".xlsx", ".xlsm"},
        inspect_tokens_file,
    )
    results_records = _explicit_or_discovered(
        downloads_dir,
        results_path,
        {".xlsx", ".xlsm"},
        inspect_results_file,
    )
    if not tokens_records:
        raise LimeSurveySelectionError("No se encontro archivo tokens con estructura minima valida.")
    if not results_records:
        raise LimeSurveySelectionError("No se encontro archivo resultados con estructura minima valida.")

    evaluations = tuple(
        evaluate_pair(tokens, results)
        for tokens in tokens_records
        for results in results_records
    )
    if not evaluations:
        raise LimeSurveySelectionError("No fue posible evaluar parejas tokens/resultados.")

    ordered = sorted(
        evaluations,
        key=lambda item: (
            item.coincidencias,
            item.cobertura_pct,
            KEY_PRIORITY.get(item.key_kind, 0),
            item.pair_mtime,
        ),
        reverse=True,
    )
    top = ordered[0]
    threshold = _min_coverage_threshold() if min_coverage_pct is None else min_coverage_pct
    if top.coincidencias == 0:
        raise LimeSurveySelectionError("Todas las parejas tokens/resultados tienen cero coincidencias reales.")
    if top.cobertura_pct < threshold:
        raise LimeSurveySelectionError(
            "Cobertura LimeSurvey anormalmente baja: "
            f"{top.cobertura_pct}% < {threshold}%."
        )
    if len(ordered) > 1:
        second = ordered[1]
        same_score = (
            top.coincidencias == second.coincidencias
            and top.cobertura_pct == second.cobertura_pct
            and KEY_PRIORITY.get(top.key_kind, 0) == KEY_PRIORITY.get(second.key_kind, 0)
            and top.pair_mtime == second.pair_mtime
        )
        if same_score:
            raise LimeSurveySelectionError(
                "Multiples parejas LimeSurvey validas tienen la misma compatibilidad y no se puede resolver."
            )

    tokens_by_path = {item.path: item for item in tokens_records}
    results_by_path = {item.path: item for item in results_records}
    return LimeSurveyPair(
        tokens=tokens_by_path[top.tokens_path],
        results=results_by_path[top.results_path],
        evaluation=top,
        evaluated_pairs=evaluations,
    )


def env_limesurvey_pair(downloads_dir: str | Path) -> LimeSurveyPair:
    tokens_env = os.environ.get("RUTA_INSCRITOS", "").strip().strip('"').strip("'")
    results_env = os.environ.get("RUTA_RESULTADOS", "").strip().strip('"').strip("'")
    return select_latest_limesurvey_pair(
        downloads_dir,
        tokens_path=tokens_env or None,
        results_path=results_env or None,
    )


def format_pair_evaluations(pair: LimeSurveyPair) -> list[str]:
    lines = ["[LIMESURVEY] Parejas evaluadas:"]
    for item in sorted(
        pair.evaluated_pairs,
        key=lambda x: (x.coincidencias, x.cobertura_pct, x.pair_mtime),
        reverse=True,
    ):
        lines.append(
            "- "
            f"{item.tokens_path.name} + {item.results_path.name} -> "
            f"{item.coincidencias} coincidencias, cobertura {item.cobertura_pct}% "
            f"(tokens_key={item.tokens_key or 'N/D'}, results_key={item.results_key or 'N/D'})"
        )
    lines.extend([
        "[LIMESURVEY] Pareja seleccionada:",
        f"{pair.tokens_path.name} + {pair.results_path.name}",
    ])
    return lines


def _codigo_columna_corto(nombre_columna: str) -> str:
    """Acorta encabezados largos de LimeSurvey ("G01Q67[SQ005]. <pregunta completa>")
    al código antes del primer ". " para no ahogar el log con el enunciado completo.
    Columnas sin ese patrón (matrícula, tokens) se devuelven sin cambios. Mismo
    criterio que auto_chequeo_columnas() en caracterizacion.py — no se duplica la
    lógica de recorte, solo se replica el mismo criterio simple en este módulo."""
    texto = str(nombre_columna)
    return texto.split(". ", 1)[0] if ". " in texto else texto


def format_selected_file_log(prefix: str, record: ContentFile, key_column: str, key_kind: str) -> list[str]:
    uniques = _values_for_key(record.path, key_column, key_kind) if key_column else set()
    columnas_cortas = ", ".join(_codigo_columna_corto(c) for c in record.columns)
    return [
        f"[{prefix}] Archivo seleccionado: {record.path}",
        f"[{prefix}] Filas: {record.rows}",
        f"[{prefix}] Columnas detectadas: {columnas_cortas}",
        f"[{prefix}] Identificadores unicos: {len(uniques)}",
    ]


def _matricula_score(path: Path, df) -> tuple[int, int, list[str]]:
    cols = list(df.columns)
    errors: list[str] = []
    ok = 0
    for idx, accepted in MATRICULA_EXPECTED_BY_POSITION.items():
        if idx >= len(cols):
            errors.append(f"indice {idx} fuera de rango")
            continue
        real = _norm_header_layout(cols[idx])
        accepted_norm = {_norm_header_layout(x) for x in accepted}
        if real in accepted_norm:
            ok += 1
        else:
            errors.append(f"pos {idx}: {cols[idx]} != {'/'.join(accepted)}")
    return ok + _name_bias(path, "matricula"), ok, errors


def inspect_matricula_file(path: str | Path) -> ContentFile:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise LimeSurveySelectionError(f"No existe archivo matricula: {p}")
    if p.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise LimeSurveySelectionError(f"Matricula debe ser XLSX: {p.name}")
    df = read_input_frame(p)
    score, structural_ok, errors = _matricula_score(p, df)
    min_required = 14
    if structural_ok < min_required:
        raise LimeSurveySelectionError(
            f"Estructura matricula insuficiente en {p.name}: columnas_validas={structural_ok}; errores={'; '.join(errors[:5])}"
        )
    stat = p.stat()
    return ContentFile(
        path=p,
        kind="matricula",
        name_id=None,
        mtime=stat.st_mtime,
        size=stat.st_size,
        rows=int(len(df)),
        columns=tuple(str(c) for c in df.columns),
        score=score,
        reason=f"score={score}",
    )


def select_latest_matricula_file(
    downloads_dir: str | Path,
    *,
    matricula_path: str | Path | None = None,
) -> ContentFile:
    if matricula_path:
        return inspect_matricula_file(matricula_path)
    records = _inspect_many(_candidate_paths(downloads_dir, {".xlsx", ".xlsm"}), inspect_matricula_file)
    if not records:
        raise LimeSurveySelectionError("No se encontro archivo de matricula XLSX con estructura minima valida.")
    ordered = sorted(records, key=lambda item: (item.score, item.mtime, _name_bias(item.path, "matricula")), reverse=True)
    if len(ordered) > 1:
        top, second = ordered[0], ordered[1]
        if top.score == second.score and top.mtime == second.mtime:
            raise LimeSurveySelectionError(
                "Multiples archivos de matricula validos tienen el mismo score y fecha; no se puede resolver."
            )
    return ordered[0]


def env_matricula_file(downloads_dir: str | Path) -> ContentFile:
    matricula_env = os.environ.get("RUTA_MATRICULA", "").strip().strip('"').strip("'")
    return select_latest_matricula_file(downloads_dir, matricula_path=matricula_env or None)


def _clean_id_set(values: Iterable[object], key_kind: str = "token") -> set[str]:
    return normalized_value_set(values, key_kind)


def build_coherence_report(
    *,
    tokens_survey_id: str,
    results_survey_id: str,
    token_rows: int,
    result_rows: int,
    token_ids: Iterable[object],
    result_ids: Iterable[object],
    matricula_ids: Iterable[object],
    key_kind: str = "token",
    complete_response_rows: int = 0,
    respondents: int = 0,
    historical_respondents: int = 0,
    new_records: int | None = None,
    universe_size: int | None = None,
) -> dict[str, object]:
    token_set = _clean_id_set(token_ids, key_kind)
    result_set = _clean_id_set(result_ids, key_kind)
    matricula_set = _clean_id_set(matricula_ids, key_kind)

    matches_tokens_results = token_set & result_set
    matches_matricula_tokens = matricula_set & token_set
    matches_matricula_results = matricula_set & result_set

    universe = int(universe_size if universe_size is not None else len(matricula_set))
    coverage_tokens = (len(matches_matricula_tokens) / universe * 100.0) if universe > 0 else 0.0
    coverage_results = (len(matches_matricula_results) / universe * 100.0) if universe > 0 else 0.0
    coverage_pair = (len(matches_tokens_results) / max(1, min(len(token_set), len(result_set))) * 100.0)

    report: dict[str, object] = {
        "id_encuesta_tokens": str(tokens_survey_id or ""),
        "id_encuesta_resultados": str(results_survey_id or ""),
        "tipo_clave_cruce": key_kind,
        "filas_tokens": int(token_rows),
        "filas_resultados": int(result_rows),
        "identificadores_unicos_tokens": int(len(token_set)),
        "identificadores_unicos_resultados": int(len(result_set)),
        "identificadores_unicos_matricula": int(len(matricula_set)),
        "coincidencias_tokens_resultados": int(len(matches_tokens_results)),
        "coincidencias_matricula_tokens": int(len(matches_matricula_tokens)),
        "coincidencias_matricula_resultados": int(len(matches_matricula_results)),
        "cobertura_tokens_resultados_pct": round(coverage_pair, 2),
        "cobertura_matricula_tokens_pct": round(coverage_tokens, 2),
        "cobertura_matricula_resultados_pct": round(coverage_results, 2),
        "filas_respuesta_completa_resultados": int(complete_response_rows),
        "respondientes_calculados": int(respondents),
        "respondientes_historicos_max": int(historical_respondents),
    }
    if new_records is not None:
        report["nuevos_inscritos"] = int(new_records)
    if universe_size is not None:
        report["universo_vigente"] = int(universe_size)
    return report


def format_coherence_report(report: dict[str, object]) -> list[str]:
    return [
        f"[LIMESURVEY][COHERENCIA] ID nombre tokens: {report['id_encuesta_tokens'] or 'N/D'}",
        f"[LIMESURVEY][COHERENCIA] ID nombre resultados: {report['id_encuesta_resultados'] or 'N/D'}",
        f"[LIMESURVEY][COHERENCIA] tipo clave cruce: {report['tipo_clave_cruce']}",
        f"[LIMESURVEY][COHERENCIA] filas tokens: {report['filas_tokens']}",
        f"[LIMESURVEY][COHERENCIA] filas resultados: {report['filas_resultados']}",
        f"[LIMESURVEY][COHERENCIA] identificadores unicos tokens: {report['identificadores_unicos_tokens']}",
        f"[LIMESURVEY][COHERENCIA] identificadores unicos resultados: {report['identificadores_unicos_resultados']}",
        f"[LIMESURVEY][COHERENCIA] coincidencias tokens-resultados: {report['coincidencias_tokens_resultados']}",
        f"[LIMESURVEY][COHERENCIA] cobertura tokens-resultados: {report['cobertura_tokens_resultados_pct']}%",
        f"[LIMESURVEY][COHERENCIA] coincidencias matricula-tokens: {report['coincidencias_matricula_tokens']}",
        f"[LIMESURVEY][COHERENCIA] coincidencias matricula-resultados: {report['coincidencias_matricula_resultados']}",
        f"[LIMESURVEY][COHERENCIA] cobertura matricula-tokens: {report['cobertura_matricula_tokens_pct']}%",
        f"[LIMESURVEY][COHERENCIA] cobertura matricula-resultados: {report['cobertura_matricula_resultados_pct']}%",
        f"[LIMESURVEY][COHERENCIA] respondientes calculados: {report['respondientes_calculados']}",
        f"[LIMESURVEY][COHERENCIA] respondientes historicos max: {report['respondientes_historicos_max']}",
    ]


def validate_coherence_report(report: dict[str, object], min_pair_coverage_pct: float | None = None) -> None:
    threshold = _min_coverage_threshold() if min_pair_coverage_pct is None else min_pair_coverage_pct
    if int(report["filas_resultados"]) > 0 and int(report["coincidencias_tokens_resultados"]) == 0:
        raise LimeSurveyCoherenceError(
            "Cero coincidencias reales entre resultados y tokens pese a que resultados tiene filas."
        )

    if float(report["cobertura_tokens_resultados_pct"]) < threshold:
        raise LimeSurveyCoherenceError(
            "Cobertura tokens-resultados anormalmente baja: "
            f"{report['cobertura_tokens_resultados_pct']}% < {threshold}%."
        )

    if int(report.get("identificadores_unicos_matricula", 0)) > 0:
        if int(report["coincidencias_matricula_tokens"]) == 0:
            raise LimeSurveyCoherenceError("Cero coincidencias reales entre matricula y tokens.")
        if int(report["coincidencias_matricula_resultados"]) == 0:
            raise LimeSurveyCoherenceError("Cero coincidencias reales entre matricula y resultados.")

    if int(report["filas_respuesta_completa_resultados"]) > 0 and int(report["respondientes_calculados"]) == 0:
        raise LimeSurveyCoherenceError(
            "Cero respondientes calculados aunque el archivo de resultados contiene respuestas completas."
        )

    if int(report.get("respondientes_historicos_max", 0)) > 0 and int(report["respondientes_calculados"]) == 0:
        raise LimeSurveyCoherenceError(
            "Reduccion abrupta de respondientes historicos a cero: "
            f"historico_max={report['respondientes_historicos_max']} actual=0."
        )


def validate_high_new_records(
    *,
    new_records: int,
    universe_size: int,
    allow_override: bool = False,
    threshold: float = 0.80,
) -> None:
    if universe_size <= 0:
        return
    ratio = new_records / universe_size
    if ratio > threshold and not allow_override:
        raise LimeSurveyCoherenceError(
            "Nuevos inscritos sobrepasan el umbral critico: "
            f"{new_records}/{universe_size} = {ratio:.0%}. "
            "Para ejecutar bajo excepcion explicita define CARACTERIZACION_PERMITIR_NUEVOS_ALTOS=1."
        )
