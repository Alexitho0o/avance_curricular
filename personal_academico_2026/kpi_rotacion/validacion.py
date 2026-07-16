"""Validaciones no bloqueantes para la rotacion academica SIES."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

import pandas as pd

from .lectura import AcademicDataset


@dataclass(frozen=True)
class ValidationIssue:
    """Describe una advertencia o error detectado durante la ejecucion."""

    archivo: str
    anio: int | None
    severidad: str
    codigo: str
    mensaje: str
    fila: int | None = None
    identificador: str | None = None
    campo: str | None = None
    valor: str | None = None


def issue_to_dict(issue: ValidationIssue) -> dict[str, object]:
    """Convierte un hallazgo de validacion a diccionario serializable."""

    return asdict(issue)


def issues_to_frame(issues: Sequence[ValidationIssue]) -> pd.DataFrame:
    """Convierte los hallazgos de validacion en una tabla exportable."""

    if not issues:
        return pd.DataFrame(
            columns=[
                "archivo",
                "anio",
                "severidad",
                "codigo",
                "mensaje",
                "fila",
                "identificador",
                "campo",
                "valor",
            ]
        )
    return pd.DataFrame([issue_to_dict(issue) for issue in issues])


def normalize_value(value: object) -> str:
    """Normaliza un valor tabular para comparaciones controladas."""

    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.upper() in {"NAN", "NONE", "NULL", "NO APLICA"}:
        return ""
    return text


def normalized_upper(value: object) -> str:
    """Normaliza un valor a mayusculas sin alterar el dato fuente."""

    return normalize_value(value).upper()


def parse_number(value: object) -> float | None:
    """Convierte numeros SIES con coma o punto decimal a float."""

    text = normalize_value(value)
    if text == "":
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def normalize_document_number(tipo_documento: object, num_documento: object) -> str:
    """Normaliza el numero documental sin corregir datos fuente."""

    tipo = normalized_upper(tipo_documento)
    text = normalize_value(num_documento)
    if tipo == "R":
        return "".join(character for character in text if character.isdigit())
    return text.replace(" ", "").replace("\t", "")


def normalize_dv(tipo_documento: object, dv: object) -> str:
    """Normaliza el digito verificador segun tipo documental."""

    tipo = normalized_upper(tipo_documento)
    if tipo == "P":
        return ""
    return normalized_upper(dv).replace(".", "").replace("-", "").replace(" ", "")


def row_number(index: object, has_header: bool) -> int:
    """Calcula la linea fisica aproximada para una fila de datos."""

    base = 2 if has_header else 1
    return int(index) + base


def compute_rut_dv(num_documento: str) -> str | None:
    """Calcula el digito verificador chileno para un cuerpo RUT numerico."""

    if not num_documento.isdigit():
        return None
    reversed_digits = reversed(num_documento)
    factors = [2, 3, 4, 5, 6, 7]
    total = 0
    for position, digit in enumerate(reversed_digits):
        total += int(digit) * factors[position % len(factors)]
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def identifier_from_values(tipo_documento: object, num_documento: object, dv: object) -> str:
    """Construye el identificador oficial de comparacion SIES."""

    tipo = normalized_upper(tipo_documento)
    return "|".join(
        [
            tipo,
            normalize_document_number(tipo, num_documento),
            normalize_dv(tipo, dv),
        ]
    )


def build_identifier_series(frame: pd.DataFrame) -> pd.Series:
    """Construye identificadores oficiales para todas las filas de un DataFrame."""

    required = ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"]
    for column in required:
        if column not in frame.columns:
            return pd.Series([""] * len(frame), index=frame.index, dtype=str)
    return frame.apply(
        lambda row: identifier_from_values(
            row["TIPO_DOCUMENTO"],
            row["NUM_DOCUMENTO"],
            row["DV"],
        ),
        axis=1,
    )


def has_valid_identifier(row: pd.Series) -> bool:
    """Indica si una fila posee llave minima utilizable para comparar."""

    tipo = normalized_upper(row.get("TIPO_DOCUMENTO", ""))
    numero = normalize_document_number(tipo, row.get("NUM_DOCUMENTO", ""))
    dv = normalize_dv(tipo, row.get("DV", ""))
    if tipo not in {"R", "P"} or numero == "":
        return False
    if tipo == "R" and dv == "":
        return False
    return True


def append_issue(
    issues: list[ValidationIssue],
    dataset: AcademicDataset,
    anio: int | None,
    severidad: str,
    codigo: str,
    mensaje: str,
    fila: int | None = None,
    identificador: str | None = None,
    campo: str | None = None,
    valor: object | None = None,
) -> None:
    """Agrega un hallazgo al acumulador de validaciones."""

    issues.append(
        ValidationIssue(
            archivo=str(dataset.path),
            anio=anio,
            severidad=severidad,
            codigo=codigo,
            mensaje=mensaje,
            fila=fila,
            identificador=identificador,
            campo=campo,
            valor=None if valor is None else str(valor),
        )
    )


def validate_structure(
    dataset: AcademicDataset,
    official_headers: Sequence[str],
    anio: int | None,
) -> list[ValidationIssue]:
    """Valida cantidad de columnas y uso de encabezado contra estructura oficial."""

    issues: list[ValidationIssue] = []
    if dataset.columns != len(official_headers):
        append_issue(
            issues,
            dataset,
            anio,
            "ERROR",
            "CANTIDAD_COLUMNAS_INVALIDA",
            "La cantidad de columnas no coincide con la estructura oficial.",
            valor=dataset.columns,
        )
    if list(dataset.frame.columns) != list(official_headers):
        append_issue(
            issues,
            dataset,
            anio,
            "ERROR",
            "ENCABEZADOS_INVALIDOS",
            "Los encabezados asignados no coinciden con la estructura oficial.",
        )
    if not dataset.has_header:
        append_issue(
            issues,
            dataset,
            anio,
            "ADVERTENCIA",
            "ARCHIVO_SIN_ENCABEZADO",
            "El archivo no trae encabezado; se asigno la estructura oficial SIES.",
        )
    for field_error in dataset.field_count_errors:
        append_issue(
            issues,
            dataset,
            anio,
            "ERROR",
            "FILA_CON_CANTIDAD_COLUMNAS_INVALIDA",
            "La fila no tiene la cantidad de columnas esperada.",
            fila=int(field_error["linea"]),
            valor=field_error,
        )
    return issues


def validate_document_fields(dataset: AcademicDataset, anio: int | None) -> list[ValidationIssue]:
    """Valida tipo de documento, numero, DV y RUT cuando corresponde."""

    issues: list[ValidationIssue] = []
    frame = dataset.frame
    identifiers = build_identifier_series(frame)
    for index, row in frame.iterrows():
        tipo = normalized_upper(row.get("TIPO_DOCUMENTO", ""))
        numero = normalize_document_number(tipo, row.get("NUM_DOCUMENTO", ""))
        dv = normalize_dv(tipo, row.get("DV", ""))
        ident = identifiers.loc[index]
        line = row_number(index, dataset.has_header)
        if tipo == "" or numero == "":
            append_issue(
                issues,
                dataset,
                anio,
                "ERROR",
                "REGISTRO_SIN_DOCUMENTO",
                "El registro no contiene tipo o numero de documento.",
                fila=line,
                identificador=ident,
            )
        if tipo not in {"R", "P"}:
            append_issue(
                issues,
                dataset,
                anio,
                "ERROR",
                "TIPO_DOCUMENTO_INVALIDO",
                "Los valores permitidos para TIPO_DOCUMENTO son R y P.",
                fila=line,
                identificador=ident,
                campo="TIPO_DOCUMENTO",
                valor=tipo,
            )
        if tipo == "R":
            if not numero.isdigit() or numero.startswith("0"):
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "DOCUMENTO_INVALIDO",
                    "NUM_DOCUMENTO tipo R debe ser numerico y no iniciar con 0.",
                    fila=line,
                    identificador=ident,
                    campo="NUM_DOCUMENTO",
                    valor=numero,
                )
            if dv not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "K"}:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "DV_INVALIDO",
                    "DV tipo R debe ser 0-9 o K.",
                    fila=line,
                    identificador=ident,
                    campo="DV",
                    valor=dv,
                )
            expected_dv = compute_rut_dv(numero)
            if expected_dv is not None and dv in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "K"}:
                if dv != expected_dv:
                    append_issue(
                        issues,
                        dataset,
                        anio,
                        "ERROR",
                        "RUT_DV_NO_CORRESPONDE",
                        "El RUT y el digito verificador no corresponden.",
                        fila=line,
                        identificador=ident,
                        campo="DV",
                        valor=dv,
                    )
        if tipo == "P" and dv != "":
            append_issue(
                issues,
                dataset,
                anio,
                "ERROR",
                "DV_PASAPORTE_NO_NULO",
                "El DV debe ser nulo cuando TIPO_DOCUMENTO es P.",
                fila=line,
                identificador=ident,
                campo="DV",
                valor=dv,
            )
    return issues


def validate_duplicates(dataset: AcademicDataset, anio: int | None) -> list[ValidationIssue]:
    """Detecta duplicados de identificador y documentos con DV distinto."""

    issues: list[ValidationIssue] = []
    frame = dataset.frame.copy()
    frame["IDENTIFICADOR_SIES"] = build_identifier_series(frame)
    duplicated = frame[frame["IDENTIFICADOR_SIES"].duplicated(keep=False)]
    for index, row in duplicated.iterrows():
        append_issue(
            issues,
            dataset,
            anio,
            "ERROR",
            "DUPLICADO_IDENTIFICADOR",
            "El identificador oficial TIPO_DOCUMENTO+NUM_DOCUMENTO+DV esta duplicado.",
            fila=row_number(index, dataset.has_header),
            identificador=row["IDENTIFICADOR_SIES"],
        )
    if {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"}.issubset(frame.columns):
        grouped = frame.groupby(["TIPO_DOCUMENTO", "NUM_DOCUMENTO"], dropna=False)["DV"].nunique()
        repeated = grouped[grouped > 1]
        for (tipo, numero), _count in repeated.items():
            append_issue(
                issues,
                dataset,
                anio,
                "ERROR",
                "DOCUMENTO_REPETIDO_DV_DISTINTO",
                "Existe el mismo TIPO_DOCUMENTO+NUM_DOCUMENTO con DV distinto.",
                identificador=f"{tipo}|{numero}",
            )
    return issues


def hour_columns(frame: pd.DataFrame) -> list[str]:
    """Lista las columnas oficiales de horas que existen en el archivo."""

    candidates = [
        "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
        "NUM_HORAS_PLANTA",
        "NUM_HORAS_CONTRATA",
        "NUM_HORAS_HONORARIOS",
        "TOTAL_HORAS_CONTRATADAS",
    ]
    return [column for column in candidates if column in frame.columns]


def validate_hours(dataset: AcademicDataset, anio: int | None) -> list[ValidationIssue]:
    """Valida horas nulas, negativas, no numericas y mayores al maximo oficial."""

    issues: list[ValidationIssue] = []
    frame = dataset.frame
    identifiers = build_identifier_series(frame)
    for column in hour_columns(frame):
        for index, value in frame[column].items():
            ident = identifiers.loc[index]
            line = row_number(index, dataset.has_header)
            parsed = parse_number(value)
            if normalize_value(value) == "":
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "HORAS_NULAS",
                    "La columna de horas no puede quedar nula en el control de rotacion.",
                    fila=line,
                    identificador=ident,
                    campo=column,
                    valor=value,
                )
                continue
            if parsed is None:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "HORAS_NO_NUMERICAS",
                    "La columna de horas debe ser numerica.",
                    fila=line,
                    identificador=ident,
                    campo=column,
                    valor=value,
                )
                continue
            if parsed < 0:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "HORAS_NEGATIVAS",
                    "La columna de horas no puede ser negativa.",
                    fila=line,
                    identificador=ident,
                    campo=column,
                    valor=value,
                )
            if parsed > 56:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "HORAS_MAYORES_MAXIMO",
                    "Las horas no pueden superar 56 horas semanales.",
                    fila=line,
                    identificador=ident,
                    campo=column,
                    valor=value,
                )
    sum_columns = [column for column in ["NUM_HORAS_PLANTA", "NUM_HORAS_CONTRATA", "NUM_HORAS_HONORARIOS"] if column in frame.columns]
    if sum_columns:
        for index, row in frame.iterrows():
            parsed_values = [parse_number(row.get(column, "")) for column in sum_columns]
            if any(value is None for value in parsed_values):
                continue
            total = sum(value or 0.0 for value in parsed_values)
            if total > 56:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "SUMA_HORAS_MAYOR_56",
                    "La suma Planta+Contrata+Honorarios supera 56 horas.",
                    fila=row_number(index, dataset.has_header),
                    identificador=identifiers.loc[index],
                    campo="+".join(sum_columns),
                    valor=total,
                )
            if total <= 0:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "SUMA_HORAS_NO_POSITIVA",
                    "La suma Planta+Contrata+Honorarios debe ser mayor a 0.",
                    fila=row_number(index, dataset.has_header),
                    identificador=identifiers.loc[index],
                    campo="+".join(sum_columns),
                    valor=total,
                )
    return issues


def validate_required_business_fields(dataset: AcademicDataset, anio: int | None) -> list[ValidationIssue]:
    """Valida campos de cargo, programa y vigencia pedidos por el hito."""

    issues: list[ValidationIssue] = []
    frame = dataset.frame
    identifiers = build_identifier_series(frame)
    checks = [
        ("PRINCIPAL_CARGO_ACADEMICO", "CARGO_VACIO", "El cargo principal no puede estar vacio."),
        ("CARGO_NORMALIZADO", "CARGO_NORMALIZADO_VACIO", "El cargo normalizado no puede estar vacio."),
        ("NOMBRE_PRINCIPAL_PROGRAMA", "PROGRAMA_VACIO", "El programa principal no puede estar vacio."),
    ]
    for column, code, message in checks:
        if column not in frame.columns:
            continue
        for index, value in frame[column].items():
            if normalize_value(value) == "":
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    code,
                    message,
                    fila=row_number(index, dataset.has_header),
                    identificador=identifiers.loc[index],
                    campo=column,
                    valor=value,
                )
    if "VIGENCIA" in frame.columns:
        for index, value in frame["VIGENCIA"].items():
            normalized = normalize_value(value)
            if normalized not in {"0", "1"}:
                append_issue(
                    issues,
                    dataset,
                    anio,
                    "ERROR",
                    "VIGENCIA_INVALIDA",
                    "Los valores permitidos para VIGENCIA son 0 y 1.",
                    fila=row_number(index, dataset.has_header),
                    identificador=identifiers.loc[index],
                    campo="VIGENCIA",
                    valor=value,
                )
    return issues


def validate_dataset(
    dataset: AcademicDataset,
    official_headers: Sequence[str],
    anio: int | None,
) -> list[ValidationIssue]:
    """Ejecuta todas las validaciones de un archivo anual sin detener."""

    issues: list[ValidationIssue] = []
    issues.extend(validate_structure(dataset, official_headers, anio))
    issues.extend(validate_document_fields(dataset, anio))
    issues.extend(validate_duplicates(dataset, anio))
    issues.extend(validate_hours(dataset, anio))
    issues.extend(validate_required_business_fields(dataset, anio))
    return issues


def compare_text_fields(
    base: pd.DataFrame,
    comparison: pd.DataFrame,
    fields: Iterable[tuple[str, str]],
) -> list[tuple[int, str, str, str, str]]:
    """Compara campos textuales para identificadores presentes en ambos anos."""

    merged = base.merge(comparison, on="IDENTIFICADOR_SIES", suffixes=("_BASE", "_COMPARACION"))
    differences: list[tuple[int, str, str, str, str]] = []
    for index, row in merged.iterrows():
        ident = normalize_value(row["IDENTIFICADOR_SIES"])
        for field, code in fields:
            base_value = normalize_value(row.get(f"{field}_BASE", ""))
            comp_value = normalize_value(row.get(f"{field}_COMPARACION", ""))
            if base_value != comp_value:
                differences.append((int(index), ident, code, base_value, comp_value))
    return differences


def validate_cross_year_consistency(
    base_dataset: AcademicDataset,
    comparison_dataset: AcademicDataset,
    anio_base: int,
    anio_comparacion: int,
) -> list[ValidationIssue]:
    """Detecta inconsistencias de identidad observadas entre ambos anos."""

    issues: list[ValidationIssue] = []
    base = base_dataset.frame.copy()
    comparison = comparison_dataset.frame.copy()
    base["IDENTIFICADOR_SIES"] = build_identifier_series(base)
    comparison["IDENTIFICADOR_SIES"] = build_identifier_series(comparison)

    if {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"}.issubset(base.columns) and {"TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"}.issubset(comparison.columns):
        merged_doc = base.merge(
            comparison,
            on=["TIPO_DOCUMENTO", "NUM_DOCUMENTO"],
            suffixes=("_BASE", "_COMPARACION"),
        )
        for _index, row in merged_doc.iterrows():
            if normalized_upper(row.get("DV_BASE", "")) != normalized_upper(row.get("DV_COMPARACION", "")):
                issues.append(
                    ValidationIssue(
                        archivo=f"{base_dataset.path} | {comparison_dataset.path}",
                        anio=None,
                        severidad="ERROR",
                        codigo="DV_DISTINTO_ENTRE_ANIOS",
                        mensaje="El mismo TIPO_DOCUMENTO+NUM_DOCUMENTO tiene DV distinto entre anos.",
                        identificador=f"{row.get('TIPO_DOCUMENTO')}|{row.get('NUM_DOCUMENTO')}",
                        campo="DV",
                        valor=f"{anio_base}:{row.get('DV_BASE')} | {anio_comparacion}:{row.get('DV_COMPARACION')}",
                    )
                )

    field_checks = [
        ("SEXO", "SEXO_DISTINTO_ENTRE_ANIOS", "CRITICO"),
        ("FECHA_NACIMIENTO", "FECHA_NACIMIENTO_DISTINTA_ENTRE_ANIOS", "CRITICO"),
        ("NOMBRES", "NOMBRE_DISTINTO_ENTRE_ANIOS", "ADVERTENCIA"),
        ("PRIMER_APELLIDO", "APELLIDO_DISTINTO_ENTRE_ANIOS", "ADVERTENCIA"),
        ("SEGUNDO_APELLIDO", "APELLIDO_DISTINTO_ENTRE_ANIOS", "ADVERTENCIA"),
    ]
    severities = {code: severity for _field, code, severity in field_checks}
    existing_checks = [
        (field, code)
        for field, code, _severity in field_checks
        if field in base.columns and field in comparison.columns
    ]
    for _index, ident, code, base_value, comp_value in compare_text_fields(base, comparison, existing_checks):
        issues.append(
            ValidationIssue(
                archivo=f"{base_dataset.path} | {comparison_dataset.path}",
                anio=None,
                severidad=severities.get(code, "ADVERTENCIA"),
                codigo=code,
                mensaje="El campo de identidad cambio entre los anos comparados.",
                identificador=ident,
                valor=f"{anio_base}:{base_value} | {anio_comparacion}:{comp_value}",
            )
        )
    return issues
