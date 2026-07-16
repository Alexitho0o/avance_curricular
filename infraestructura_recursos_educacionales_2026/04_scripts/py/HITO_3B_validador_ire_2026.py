#!/usr/bin/env python3
"""Validador tecnico-funcional para archivos candidatos IRE 2026.

Solo lee el archivo validado. No corrige datos ni genera archivos de carga PES.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


__version__ = "1.0.0"

SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[2]
DEFAULT_STRUCTURE = PROJECT_ROOT / "01_fuentes_oficiales/estructuras_tecnicas/20260706_89535_Estructura_IRE_ID_16770.csv"
DEFAULT_MATRIX = PROJECT_ROOT / "06_validaciones/reglas_funcionales/HITO_2C_MATRIZ_LARGA_CAMPO_TIPO_INFRAESTRUCTURA_IRE_2026_20260709_235255.csv"
DEFAULT_RULES = PROJECT_ROOT / "06_validaciones/reglas_funcionales/HITO_3A_REGLAS_VALIDACION_IRE_2026_20260710_000222.csv"
DEFAULT_CONFIG = SCRIPT_PATH.with_name("HITO_3B_config_validador_ire_2026.json")
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "06_validaciones/contenido"
DEFAULT_LOG_DIR = PROJECT_ROOT / "08_logs/ejecuciones"

SEVERITIES = {"BLOQUEANTE", "ADVERTENCIA", "INFORMATIVA", "PENDIENTE_CONFIRMACION"}
DICTAMENS = {"APTO_TECNICAMENTE", "APTO_CON_ADVERTENCIAS", "NO_APTO_BLOQUEANTES", "NO_EVALUABLE"}
TRUE_VALUES = {"true", "1", "yes", "si", "sí"}
FALSE_VALUES = {"false", "0", "no"}


class ValidationAbort(Exception):
    """Stops validation when the input cannot be evaluated safely."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bool_or_auto(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized == "auto":
        return None
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise argparse.ArgumentTypeError("Use true, false o auto.")


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise argparse.ArgumentTypeError("Use true o false.")


def normalize_delimiter(value: str) -> str:
    if value == "\\t":
        return "\t"
    if value == "auto":
        return value
    if len(value) != 1:
        raise argparse.ArgumentTypeError("El delimitador debe ser auto o un unico caracter.")
    return value


def detect_encoding(path: Path, candidates: Iterable[str]) -> tuple[str, str]:
    data = path.read_bytes()
    ordered_candidates = list(candidates)
    if not data.startswith(b"\xef\xbb\xbf"):
        ordered_candidates = [encoding for encoding in ordered_candidates if encoding != "utf-8-sig"]
    for encoding in ordered_candidates:
        try:
            return encoding, data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValidationAbort("No fue posible decodificar el archivo con las codificaciones configuradas.")


def detect_delimiter(text: str, candidates: list[str]) -> str:
    sample = "\n".join(text.splitlines()[:20])
    if not sample:
        raise ValidationAbort("El archivo esta vacio.")
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(candidates)).delimiter
    except csv.Error:
        counts = {candidate: sample.count(candidate) for candidate in candidates}
        selected, count = max(counts.items(), key=lambda item: item[1])
        if count == 0:
            raise ValidationAbort("No fue posible detectar el delimitador de forma controlada.")
        return selected


def load_semicolon_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def load_official_headers(path: Path, encodings: list[str], delimiters: list[str]) -> list[str]:
    encoding, text = detect_encoding(path, encodings)
    del encoding
    delimiter = detect_delimiter(text, delimiters)
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    if not rows:
        raise ValidationAbort("La estructura tecnica no contiene encabezados.")
    headers = [value.strip().lstrip("\ufeff") for value in rows[0]]
    if len(headers) != 54:
        raise ValidationAbort(f"La estructura tecnica contiene {len(headers)} columnas, no 54.")
    return headers


def split_related(value: str) -> list[str]:
    return [item.strip() for item in value.split(" | ") if item.strip()]


def as_decimal(value: str) -> Decimal | None:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return Decimal(stripped.replace(",", "."))
    except InvalidOperation:
        return None


def valid_year_month(value: str) -> bool:
    match = re.fullmatch(r"(\d{4})-(\d{2})", value.strip())
    return bool(match and 1 <= int(match.group(2)) <= 12)


def month_key(value: str) -> tuple[int, int] | None:
    if not valid_year_month(value):
        return None
    year, month = value.split("-")
    return int(year), int(month)


def has_accents(value: str) -> bool:
    decomposed = unicodedata.normalize("NFD", value)
    return any(unicodedata.category(char) == "Mn" for char in decomposed)


def artificial_sample(headers: list[str]) -> list[dict[str, str]]:
    def base(type_code: str, name: str, comuna: str, address: str, vigencia: str = "1") -> dict[str, str]:
        row = {header: "" for header in headers}
        row.update({
            "TIPO_INFRAESTRUCTURA": type_code,
            "NOMBRE_IDENTIFICACION": name,
            "COMUNA": comuna,
            "DIRECCION_INMUEBLE": address,
            "VIGENCIA": vigencia,
        })
        return row

    type_1 = base("1", "MUESTRA ARTIFICIAL INMUEBLE", "SANTIAGO", "CALLE PRUEBA 100")
    type_1.update({
        "SITUACION_TENENCIA": "2", "ANIO_INICIO_USO_INMUEBLE": "2020", "USO_EXCLUSIVO": "2",
        "PORCENTAJE_USO": "50", "NOMBRE_INSTITUCION_COMPARTE": "INSTITUCION DE PRUEBA",
        "FECHA_INICIO_TENENCIA": "2024-01", "FECHA_TERMINO": "2026-13", "FUNCION_DOCENCIA": "X",
        "TOTAL_M2_TERRENO": "500", "TOTAL_M2_EDIFICADOS": "1000", "TOTAL_SALAS_CLASES": "10",
        "CAPACIDAD_SALAS_CLASES": "300", "TOTAL_M2_SALAS_CLASES": "500", "TOTAL_AUDITORIOS": "0",
        "CAPACIDAD_AUDITORIOS": "0", "TOTAL_M2_AUDITORIOS": "0", "TOTAL_LABORATORIOS": "0",
        "TOTAL_M2_LABORATORIOS": "0", "TOTAL_TALLERES": "0", "TOTAL_M2_TALLERES": "0",
        "TOTAL_PC_NB_DISPONIBLE": "0", "TOTAL_M2_CASINOS_CAFETERIAS": "0", "TOTAL_M2_AREAS_VERDES": "-5",
        "SISTEMA_GESTION_APRENDIZAJES": "NO CORRESPONDE",
    })

    type_2 = base("2", "MUESTRA ARTIFICIAL USO RESTRINGIDO", "PROVIDENCIA", "AVENIDA PRUEBA 200")
    type_2.update({
        "UR_DESC_ACTIVIDADES": "ACTIVIDAD DE PRUEBA", "UR_TOTAL_M2_TERRENO": "250",
        "UR_TOTAL_M2_CONSTRUIDOS": "100", "UR_SITUACION_TENENCIA": "2",
    })

    type_3 = base("3", "MUESTRA ARTIFICIAL BIBLIOTECA", "SANTIAGO", "CALLE BIBLIOTECA 300")
    type_3.update({
        "SITUACION_TENENCIA": "1", "TOTAL_M2_BIBLIOTECA": "300", "TOTAL_M2_SALAS_LECTURA": "200",
        "TOTAL_PROFESIONALES_BIBLIOTECA": "3", "HORAS_PERSONAL_BIBLIOTECA": "120",
        "TOTAL_TITULOS_DISPONIBLES": "1000", "TOTAL_VOLUMENES_DISPONIBLES": "1500",
        "TOTAL_SUSCRIPCIONES_REVISTAS": "10",
    })

    type_4 = base("4", "MUESTRA ARTIFICIAL RECURSOS DIGITALES", "SANTIAGO", "CASA CENTRAL 400")
    type_4.update({
        "TOTAL_TITULOS_LIBROS_DIGITALES": "2000", "TOTAL_SUSCRIPCIONES_DIGITALES": "20",
        "TOTAL_BASE_DATOS": "12",
    })

    type_5 = base("5", "MUESTRA ARTIFICIAL PREDIO", "CURICO", "CAMINO RURAL 500", vigencia="9")
    type_5.update({"TOTAL_HECTAREAS_PREDIO": "15.5"})

    type_6 = base("6", "MUESTRA ARTIFICIAL PLATAFORMA", "SANTIAGO", "SEDE CENTRAL 600")
    type_6.update({
        "SISTEMA_GESTION_APRENDIZAJES": "PLATAFORMA LMS", "SISTEMA_VIDEO_CONFERENCIA": "VIDEO PRUEBA",
        "SISTEMA_APLICACION_EVALUACION": "EVALUADOR PRUEBA",
        "DESCRIPCION_PLATAFORMA_VIRTUAL": "MUESTRA ARTIFICIAL SIN DATOS INSTITUCIONALES",
    })

    invalid_type = base("9", "", "SANTIAGO", "DIRECCION TIPO INVALIDO 700")
    duplicate_type_4 = dict(type_4)
    return [type_1, type_2, type_3, type_4, type_5, type_6, invalid_type, duplicate_type_4]


def write_artificial_sample(path: Path, headers: list[str], delimiter: str, include_header: bool = True) -> None:
    if path.exists():
        raise ValidationAbort(f"La muestra controlada ya existe y no sera sobrescrita: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers, delimiter=delimiter)
        if include_header:
            writer.writeheader()
        writer.writerows(artificial_sample(headers))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Archivo CSV que se validara.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--estructura", type=Path, default=DEFAULT_STRUCTURE)
    parser.add_argument("--matriz-larga", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--reglas", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--delimiter", type=normalize_delimiter, default="auto")
    parser.add_argument("--has-header", type=parse_bool_or_auto, default=None, metavar="true|false|auto")
    parser.add_argument("--modo", choices=["estructura", "muestra", "candidato"], required=True)
    parser.add_argument("--no-completar-severity", choices=sorted(SEVERITIES), default=None)
    parser.add_argument("--apply-internal-rules", type=parse_bool, default=None, metavar="true|false")
    parser.add_argument("--run-id", help="Timestamp YYYYMMDD_HHMMSS para nombres reproducibles.")
    parser.add_argument("--generate-controlled-sample", action="store_true", help="Crea una muestra artificial y luego la valida.")
    parser.add_argument("--fail-on-blocking", action="store_true", help="Retorna codigo 2 si hay bloqueantes.")
    return parser


class Validator:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.started = datetime.now().astimezone()
        self.run_id = args.run_id or self.started.strftime("%Y%m%d_%H%M%S")
        if not re.fullmatch(r"\d{8}_\d{6}", self.run_id):
            raise ValidationAbort("--run-id debe usar formato YYYYMMDD_HHMMSS.")
        self.config = json.loads(args.config.read_text(encoding="utf-8"))
        self.encodings = list(self.config["encoding_candidates"])
        self.delimiter_candidates = ["\t" if item == "\\t" else item for item in self.config["delimiter_candidates"]]
        self.no_complete_severity = args.no_completar_severity or self.config["default_no_completar_severity"]
        self.apply_internal = self.config["apply_internal_rules"] if args.apply_internal_rules is None else args.apply_internal_rules
        self.rules = load_semicolon_csv(args.reglas)
        self.rule_by_name = {row["NOMBRE_REGLA"]: row for row in self.rules}
        self.matrix_rows = load_semicolon_csv(args.matriz_larga)
        self.matrix = {(row["TIPO_INFRAESTRUCTURA_COD"], row["CAMPO"]): row for row in self.matrix_rows}
        self.headers = load_official_headers(args.estructura, self.encodings, self.delimiter_candidates)
        self.findings: list[dict[str, str]] = []
        self.encoding = ""
        self.delimiter = ""
        self.has_header = False
        self.data_rows: list[tuple[int, dict[str, str], list[str]]] = []
        self.input_hash_before = ""
        self.input_hash_after = ""
        self.column_distribution: Counter[int] = Counter()
        self.implemented_rule_ids = {
            row["ID_REGLA"] for row in self.rules
            if row["ESTADO_IMPLEMENTACION"] == "IMPLEMENTABLE_DIRECTO"
            or (self.apply_internal and row["ESTADO_IMPLEMENTACION"] == "IMPLEMENTABLE_CON_DECISION_INTERNA")
        }
        self.not_implemented_rules = [row for row in self.rules if row["ID_REGLA"] not in self.implemented_rule_ids]

    def emit(
        self,
        rule_name: str,
        line: int,
        field: str,
        observed: str,
        message: str,
        type_value: str = "",
        severity: str | None = None,
        observation: str = "",
    ) -> None:
        metadata = self.rule_by_name.get(rule_name)
        if metadata is None:
            raise RuntimeError(f"Regla no encontrada en catalogo HITO 3A: {rule_name}")
        actual_severity = severity or metadata["SEVERIDAD"]
        if actual_severity not in SEVERITIES:
            raise RuntimeError(f"Severidad invalida: {actual_severity}")
        self.findings.append({
            "ID_HALLAZGO": f"HAL-{len(self.findings) + 1:05d}",
            "SEVERIDAD": actual_severity,
            "ID_REGLA": metadata["ID_REGLA"],
            "TIPO_VALIDACION": metadata["TIPO_VALIDACION"],
            "FILA": str(line),
            "CAMPO": field,
            "TIPO_INFRAESTRUCTURA": type_value,
            "VALOR_OBSERVADO": observed,
            "MENSAJE": message,
            "ESTADO_IMPLEMENTACION": metadata["ESTADO_IMPLEMENTACION"],
            "FUENTE_REGLA": metadata["FUENTE_RESPALDO"],
            "OBSERVACION": observation or metadata["OBSERVACIONES"],
        })

    def prepare_input(self) -> None:
        for path, label in [
            (self.args.config, "configuracion"), (self.args.estructura, "estructura"),
            (self.args.matriz_larga, "matriz"), (self.args.reglas, "catalogo de reglas"),
        ]:
            if not path.is_file():
                raise ValidationAbort(f"No existe {label}: {path}")
        if self.args.generate_controlled_sample:
            sample_delimiter = ";" if self.args.delimiter == "auto" else self.args.delimiter
            include_header = self.args.has_header is not False
            write_artificial_sample(self.args.input, self.headers, sample_delimiter, include_header)
        if not self.args.input.is_file():
            raise ValidationAbort(f"No existe el archivo de entrada: {self.args.input}")
        if self.args.input.suffix.lower() != ".csv":
            self.emit("Extension CSV", 0, "ARCHIVO_CANDIDATO", self.args.input.suffix, "El archivo candidato no tiene extension .csv.")
        if self.args.input.suffix.lower() in {".zip", ".gz", ".bz2", ".xz", ".7z"}:
            self.emit("Archivo sin compresion", 0, "ARCHIVO_CANDIDATO", self.args.input.suffix, "El archivo candidato esta comprimido.")
        self.input_hash_before = sha256(self.args.input)

    def read_input(self) -> None:
        self.encoding, text = detect_encoding(self.args.input, self.encodings)
        if not text:
            self.emit("Archivo no vacio", 0, "ARCHIVO_CANDIDATO", "", "El archivo candidato esta vacio.")
            raise ValidationAbort("Archivo vacio.")
        self.delimiter = detect_delimiter(text, self.delimiter_candidates) if self.args.delimiter == "auto" else self.args.delimiter
        rows = list(csv.reader(text.splitlines(), delimiter=self.delimiter))
        if not rows:
            self.emit("Archivo no vacio", 0, "ARCHIVO_CANDIDATO", "", "El archivo candidato esta vacio.")
            raise ValidationAbort("Archivo sin filas.")
        first = [value.strip().lstrip("\ufeff") for value in rows[0]]
        self.has_header = first == self.headers if self.args.has_header is None else self.args.has_header
        if self.has_header:
            if first != self.headers:
                self.emit("Nombres exactos con encabezado", 1, "ENCABEZADO", " | ".join(first), "Los encabezados no coinciden exactamente con la estructura oficial.")
                if len(first) == len(self.headers):
                    self.emit("Orden exacto con encabezado", 1, "ENCABEZADO", " | ".join(first), "El orden de columnas no coincide con la estructura tecnica.")
            data_start = 1
        else:
            data_start = 0
            if self.args.modo == "estructura":
                self.emit("Modo de validacion explicito", 1, "MODO_VALIDACION", self.args.modo, "El modo estructura requiere reconocer el encabezado tecnico.")
        for offset, values in enumerate(rows[data_start:], start=1):
            line_number = data_start + offset
            self.column_distribution[len(values)] += 1
            if len(values) != 54:
                self.emit("Cantidad exacta de columnas", line_number, "FILA_COMPLETA", str(len(values)), f"La fila contiene {len(values)} columnas; se esperaban 54.")
                self.emit("Consistencia de columnas por fila", line_number, "FILA_COMPLETA", str(len(values)), "Cantidad inconsistente de columnas.")
            padded = (values + [""] * 54)[:54]
            row = {header: padded[position].strip() for position, header in enumerate(self.headers)}
            self.data_rows.append((line_number, row, values))

    def validate_common_and_matrix(self, line: int, row: dict[str, str]) -> None:
        type_value = row["TIPO_INFRAESTRUCTURA"]
        for field in ["TIPO_INFRAESTRUCTURA", "NOMBRE_IDENTIFICACION", "COMUNA", "DIRECCION_INMUEBLE", "VIGENCIA"]:
            if not row[field]:
                self.emit(f"Obligatorio transversal {field}", line, field, "", f"El campo obligatorio {field} esta vacio.", type_value)
        if type_value and type_value not in {"1", "2", "3", "4", "5", "6"}:
            self.emit("Dominio tipo infraestructura", line, "TIPO_INFRAESTRUCTURA", type_value, "TIPO_INFRAESTRUCTURA debe pertenecer a 1..6.", type_value)
            return
        if not type_value:
            return
        for field in self.headers:
            matrix_row = self.matrix[(type_value, field)]
            state = matrix_row["ESTADO_FUNCIONAL"]
            value = row[field]
            if state == "COMPLETAR_OBLIGATORIO" and not value:
                rule_name = f"Obligatorio tipo {type_value} - {field}"
                self.emit(rule_name, line, field, value, f"{field} es obligatorio cuando TIPO_INFRAESTRUCTURA={type_value}.", type_value)
            elif state == "NO_COMPLETAR" and value:
                rule_name = f"No completar bloques excluidos tipo {type_value}"
                self.emit(rule_name, line, field, value, f"{field} no debe completarse para TIPO_INFRAESTRUCTURA={type_value}.", type_value, self.no_complete_severity, "Severidad parametrizada; blanco versus cero sigue pendiente.")
            elif state == "CONTRADICCION":
                rule_name = f"Contradiccion {field} tipo {type_value}"
                self.emit(rule_name, line, field, value, self.rule_by_name[rule_name]["MENSAJE_ADVERTENCIA"], type_value, "PENDIENTE_CONFIRMACION")

    def validate_conditionals(self, line: int, row: dict[str, str]) -> None:
        if row["TIPO_INFRAESTRUCTURA"] != "1":
            return
        conditions = [
            ("PORCENTAJE_USO", row["USO_EXCLUSIVO"] == "2"),
            ("NOMBRE_INSTITUCION_COMPARTE", row["USO_EXCLUSIVO"] == "2"),
            ("FECHA_INICIO_TENENCIA", row["SITUACION_TENENCIA"] in {"2", "3", "4", "5", "6"}),
            ("FECHA_TERMINO", row["SITUACION_TENENCIA"] in {"2", "3", "4", "5"}),
            ("DESCRIPCION_OTRA_TENENCIA", row["SITUACION_TENENCIA"] == "6"),
            ("DESC_OTRAS_FUNCIONES", row["FUNCION_OTRAS"] == "X"),
        ]
        for field, active in conditions:
            if active and not row[field]:
                self.emit(f"Condicional {field}", line, field, "", f"No se cumple la condicion obligatoria de {field}.", "1")
        functions = ["FUNCION_DOCENCIA", "FUNCION_INVESTIGACION", "FUNCION_EXTENSION", "FUNCION_ADM_OFICINAS", "FUNCION_OTRAS"]
        for field in functions:
            if not row[field]:
                self.emit(f"Funcion si aplica - {field}", line, field, "", f"Revisar si {field} corresponde al inmueble; el campo esta vacio.", "1")
        if not any(row[field] == "X" for field in functions):
            self.emit("Al menos una funcion principal", line, "FUNCIONES_INMUEBLE", "", "El inmueble tipo 1 no tiene ninguna funcion principal marcada.", "1")

    def validate_domains(self, line: int, row: dict[str, str]) -> None:
        type_value = row["TIPO_INFRAESTRUCTURA"]
        vigencia = row["VIGENCIA"]
        if vigencia and vigencia not in {"0", "1"}:
            self.emit("Dominio vigencia", line, "VIGENCIA", vigencia, "VIGENCIA debe ser 0 o 1.", type_value)
        if type_value == "1":
            domains = [
                ("SITUACION_TENENCIA", {"1", "2", "3", "4", "5", "6"}, "Dominio situacion tenencia"),
                ("USO_EXCLUSIVO", {"1", "2"}, "Dominio uso exclusivo"),
            ]
            for field, allowed, rule_name in domains:
                if row[field] and row[field] not in allowed:
                    self.emit(rule_name, line, field, row[field], f"{field} contiene un valor fuera del dominio oficial.", type_value)
            if row["PORCENTAJE_USO"]:
                value = as_decimal(row["PORCENTAJE_USO"])
                if value is not None and (value < 1 or value > 99 or value != value.to_integral_value()):
                    self.emit("Rango porcentaje uso", line, "PORCENTAJE_USO", row["PORCENTAJE_USO"], "PORCENTAJE_USO debe ser entero entre 1 y 99.", type_value)
            if row["ANIO_INICIO_USO_INMUEBLE"]:
                value = as_decimal(row["ANIO_INICIO_USO_INMUEBLE"])
                if value is None or value != value.to_integral_value() or not (1800 <= value <= 2026):
                    self.emit("Rango ano inicio inmueble", line, "ANIO_INICIO_USO_INMUEBLE", row["ANIO_INICIO_USO_INMUEBLE"], "El ano debe ser entero entre 1800 y 2026.", type_value)
            for field in ["FUNCION_DOCENCIA", "FUNCION_INVESTIGACION", "FUNCION_EXTENSION", "FUNCION_ADM_OFICINAS", "FUNCION_OTRAS"]:
                if row[field] and row[field] != "X":
                    self.emit("Marca valida de funciones", line, field, row[field], "Los campos de funcion solo admiten X o vacio.", type_value)
        elif type_value == "2" and row["UR_SITUACION_TENENCIA"] and row["UR_SITUACION_TENENCIA"] not in {"1", "2"}:
            self.emit("Dominio tenencia uso restringido", line, "UR_SITUACION_TENENCIA", row["UR_SITUACION_TENENCIA"], "UR_SITUACION_TENENCIA debe ser 1 o 2.", type_value)

    def validate_text(self, line: int, row: dict[str, str]) -> None:
        type_value = row["TIPO_INFRAESTRUCTURA"]
        for field in ["NOMBRE_IDENTIFICACION", "COMUNA", "DIRECCION_INMUEBLE", "NOMBRE_INSTITUCION_COMPARTE"]:
            value = row[field]
            if value and (value != value.upper() or has_accents(value)):
                self.emit(f"Patron textual {field}", line, field, value, f"{field} contiene minusculas o acentos fuera del patron esperado.", type_value)
        description = row["DESCRIPCION_PLATAFORMA_VIRTUAL"]
        if description and len(description) > 1000:
            self.emit("Largo descripcion plataforma", line, "DESCRIPCION_PLATAFORMA_VIRTUAL", str(len(description)), "La descripcion supera 1000 caracteres.", type_value)

    def validate_numeric(self, line: int, row: dict[str, str]) -> None:
        type_value = row["TIPO_INFRAESTRUCTURA"]
        numeric_fields = split_related(self.rule_by_name["Tipo numerico cuando corresponde"]["CAMPOS_RELACIONADOS"])
        nonnegative_fields = set(split_related(self.rule_by_name["Valores no negativos"]["CAMPOS_RELACIONADOS"]))
        decimal_fields = set(split_related(self.rule_by_name["Maximo un decimal"]["CAMPOS_RELACIONADOS"]))
        integer_fields = set(split_related(self.rule_by_name["Campos enteros oficiales"]["CAMPOS_RELACIONADOS"]))
        for field in numeric_fields:
            value = row[field]
            if not value:
                continue
            state = self.matrix.get((type_value, field), {}).get("ESTADO_FUNCIONAL")
            if state == "NO_COMPLETAR":
                continue
            number = as_decimal(value)
            if number is None:
                self.emit("Tipo numerico cuando corresponde", line, field, value, f"{field} contiene un valor no numerico.", type_value)
                continue
            if field in nonnegative_fields and number < 0:
                self.emit("Valores no negativos", line, field, value, f"{field} no puede ser negativo.", type_value)
            if field in decimal_fields and max(0, -number.as_tuple().exponent) > 1:
                self.emit("Maximo un decimal", line, field, value, f"{field} contiene mas de un decimal.", type_value)
            if field in integer_fields and number != number.to_integral_value():
                self.emit("Campos enteros oficiales", line, field, value, f"{field} requiere un numero entero.", type_value)

    def validate_dates(self, line: int, row: dict[str, str]) -> None:
        if row["TIPO_INFRAESTRUCTURA"] != "1":
            return
        start = row["FECHA_INICIO_TENENCIA"]
        end = row["FECHA_TERMINO"]
        if start and not valid_year_month(start):
            self.emit("Formato fecha inicio tenencia", line, "FECHA_INICIO_TENENCIA", start, "FECHA_INICIO_TENENCIA no tiene formato AAAA-MM valido.", "1")
        if end and not valid_year_month(end):
            self.emit("Formato fecha termino", line, "FECHA_TERMINO", end, "FECHA_TERMINO no tiene formato AAAA-MM valido.", "1")
        start_key = month_key(start)
        end_key = month_key(end)
        if start_key and start_key >= (2026, 7):
            self.emit("Inicio anterior a julio 2026", line, "FECHA_INICIO_TENENCIA", start, "La fecha de inicio debe ser anterior a julio de 2026.", "1")
        if end_key and end_key <= (2026, 5):
            self.emit("Termino posterior a mayo 2026", line, "FECHA_TERMINO", end, "La fecha de termino debe ser posterior a mayo de 2026.", "1")
        if start_key and end_key and end_key < start_key:
            self.emit("Termino no anterior al inicio", line, "FECHA_TERMINO", end, "FECHA_TERMINO es anterior a FECHA_INICIO_TENENCIA.", "1")
        situation = row["SITUACION_TENENCIA"]
        if situation == "1" and start:
            self.emit("Propio sin fecha inicio", line, "FECHA_INICIO_TENENCIA", start, "No debe completar fecha de inicio cuando el inmueble es propio.", "1")
        if situation == "1" and end:
            self.emit("Propio sin fecha termino", line, "FECHA_TERMINO", end, "No debe completar fecha de termino cuando el inmueble es propio.", "1")
        if situation == "6":
            self.emit("Termino para tenencia Otro", line, "FECHA_TERMINO", end, "FECHA_TERMINO para tenencia Otro no esta explicitada.", "1", "PENDIENTE_CONFIRMACION")

    def validate_coherence(self, line: int, row: dict[str, str]) -> None:
        type_value = row["TIPO_INFRAESTRUCTURA"]
        comparisons = [
            ("TOTAL_M2_SALAS_CLASES", "TOTAL_M2_EDIFICADOS"),
            ("TOTAL_M2_SALAS_LECTURA", "TOTAL_M2_BIBLIOTECA"),
            ("TOTAL_TITULOS_DISPONIBLES", "TOTAL_VOLUMENES_DISPONIBLES"),
        ]
        for left, right in comparisons:
            left_value, right_value = as_decimal(row[left]), as_decimal(row[right])
            if left_value is not None and right_value is not None and left_value > right_value:
                self.emit(f"Coherencia {left} versus {right}", line, left, row[left], f"{left} no puede superar {right}.", type_value)
        if type_value == "1":
            pairs = [
                ("TOTAL_SALAS_CLASES", "TOTAL_M2_SALAS_CLASES"),
                ("TOTAL_AUDITORIOS", "TOTAL_M2_AUDITORIOS"),
                ("TOTAL_LABORATORIOS", "TOTAL_M2_LABORATORIOS"),
                ("TOTAL_TALLERES", "TOTAL_M2_TALLERES"),
            ]
            for count_field, area_field in pairs:
                count, area = as_decimal(row[count_field]), as_decimal(row[area_field])
                if count == 0 and area is not None and area > 0:
                    self.emit(f"Cantidad cero con superficie positiva - {count_field}", line, count_field, row[count_field], f"{count_field}=0 pero {area_field} es positivo.", "1")
                if count is not None and count > 0 and area == 0:
                    self.emit(f"Cantidad positiva sin superficie - {area_field}", line, area_field, row[area_field], f"{count_field} es positivo pero {area_field}=0.", "1")
            for count_field, capacity_field in [("TOTAL_SALAS_CLASES", "CAPACIDAD_SALAS_CLASES"), ("TOTAL_AUDITORIOS", "CAPACIDAD_AUDITORIOS")]:
                count, capacity = as_decimal(row[count_field]), as_decimal(row[capacity_field])
                if count == 0 and capacity is not None and capacity > 0:
                    self.emit(f"Cantidad cero con capacidad positiva - {capacity_field}", line, capacity_field, row[capacity_field], f"{capacity_field} es positiva pero {count_field}=0.", "1")
                if count is not None and count > 0 and capacity == 0:
                    self.emit(f"Cantidad positiva sin capacidad - {capacity_field}", line, capacity_field, row[capacity_field], f"{count_field} es positivo pero {capacity_field}=0.", "1")
            if row["USO_EXCLUSIVO"] == "1" and row["PORCENTAJE_USO"]:
                self.emit("Uso exclusivo sin porcentaje", line, "PORCENTAJE_USO", row["PORCENTAJE_USO"], "No debe completar porcentaje cuando el uso es exclusivo.", "1")
            if row["USO_EXCLUSIVO"] == "1" and row["NOMBRE_INSTITUCION_COMPARTE"]:
                self.emit("Uso exclusivo sin institucion compartida", line, "NOMBRE_INSTITUCION_COMPARTE", row["NOMBRE_INSTITUCION_COMPARTE"], "No debe identificar institucion compartida cuando el uso es exclusivo.", "1")
            if row["SITUACION_TENENCIA"] in {"1", "2", "3", "4", "5"} and row["DESCRIPCION_OTRA_TENENCIA"]:
                self.emit("Descripcion de tenencia solo para Otra", line, "DESCRIPCION_OTRA_TENENCIA", row["DESCRIPCION_OTRA_TENENCIA"], "La descripcion solo corresponde a situacion 6.", "1")
            if not row["FUNCION_OTRAS"] and row["DESC_OTRAS_FUNCIONES"]:
                self.emit("Descripcion de otras funciones sin marca", line, "DESC_OTRAS_FUNCIONES", row["DESC_OTRAS_FUNCIONES"], "La descripcion no corresponde sin FUNCION_OTRAS=X.", "1")
        if type_value == "6":
            systems = [row["SISTEMA_GESTION_APRENDIZAJES"], row["SISTEMA_VIDEO_CONFERENCIA"], row["SISTEMA_APLICACION_EVALUACION"]]
            description = row["DESCRIPCION_PLATAFORMA_VIRTUAL"]
            if description and not any(systems):
                self.emit("Descripcion de plataforma con sistema", line, "DESCRIPCION_PLATAFORMA_VIRTUAL", description, "Existe descripcion sin ningun sistema informado.", "6")
            if sum(bool(value) for value in systems) > 1 and not description:
                self.emit("Sistemas de plataforma con descripcion", line, "DESCRIPCION_PLATAFORMA_VIRTUAL", "", "Se informan multiples sistemas sin descripcion.", "6")

    def validate_duplicates(self) -> None:
        full_seen: dict[tuple[str, ...], int] = {}
        key_seen: dict[tuple[str, ...], int] = {}
        key_fields = ["TIPO_INFRAESTRUCTURA", "NOMBRE_IDENTIFICACION", "COMUNA", "DIRECCION_INMUEBLE", "VIGENCIA"]
        for line, row, _values in self.data_rows:
            full_key = tuple(row[field] for field in self.headers)
            technical_key = tuple(row[field] for field in key_fields)
            type_value = row["TIPO_INFRAESTRUCTURA"]
            if full_key in full_seen:
                self.emit("Fila exactamente duplicada", line, "FILA_COMPLETA", f"igual a fila {full_seen[full_key]}", "Se detecto una fila exactamente duplicada.", type_value)
            else:
                full_seen[full_key] = line
            if all(technical_key) and technical_key in key_seen:
                self.emit("Llave tecnica de auditoria duplicada", line, "LLAVE_TECNICA", " | ".join(technical_key), f"Llave tecnica repetida respecto de fila {key_seen[technical_key]}.", type_value)
            elif all(technical_key):
                key_seen[technical_key] = line

    def validate_rows(self) -> None:
        for line, row, _values in self.data_rows:
            self.validate_common_and_matrix(line, row)
            self.validate_conditionals(line, row)
            self.validate_domains(line, row)
            self.validate_text(line, row)
            self.validate_numeric(line, row)
            self.validate_dates(line, row)
            self.validate_coherence(line, row)
        self.validate_duplicates()

    def technical_dictamen(self) -> str:
        if not self.data_rows:
            return "NO_EVALUABLE"
        counts = Counter(item["SEVERIDAD"] for item in self.findings)
        if counts["BLOQUEANTE"]:
            return "NO_APTO_BLOQUEANTES"
        if counts["ADVERTENCIA"] or counts["PENDIENTE_CONFIRMACION"]:
            return "APTO_CON_ADVERTENCIAS"
        return "APTO_TECNICAMENTE"

    def write_outputs(self) -> tuple[Path, Path, Path, dict[str, Any]]:
        self.args.output_dir.mkdir(parents=True, exist_ok=True)
        self.args.log_dir.mkdir(parents=True, exist_ok=True)
        result_path = self.args.output_dir / f"HITO_3B_RESULTADO_VALIDACION_IRE_2026_{self.run_id}.csv"
        summary_path = self.args.output_dir / f"HITO_3B_RESUMEN_VALIDACION_IRE_2026_{self.run_id}.json"
        log_path = self.args.log_dir / f"HITO_3B_LOG_EJECUCION_{self.run_id}.txt"
        finding_columns = [
            "ID_HALLAZGO", "SEVERIDAD", "ID_REGLA", "TIPO_VALIDACION", "FILA", "CAMPO",
            "TIPO_INFRAESTRUCTURA", "VALOR_OBSERVADO", "MENSAJE", "ESTADO_IMPLEMENTACION",
            "FUENTE_REGLA", "OBSERVACION",
        ]
        with result_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=finding_columns, delimiter=";")
            writer.writeheader()
            writer.writerows(self.findings)
        counts_severity = Counter(item["SEVERIDAD"] for item in self.findings)
        counts_type = Counter(item["TIPO_VALIDACION"] for item in self.findings)
        counts_field = Counter(item["CAMPO"] or "SIN_CAMPO" for item in self.findings)
        counts_rule = Counter(item["ID_REGLA"] for item in self.findings)
        counts_row = Counter(item["FILA"] for item in self.findings)
        counts_infrastructure = Counter(item["TIPO_INFRAESTRUCTURA"] or "NO_DETERMINADO" for item in self.findings)
        dictamen = self.technical_dictamen()
        if dictamen not in DICTAMENS:
            raise RuntimeError("Dictamen invalido.")
        pending = list(self.config["pending_contradictions"])
        summary: dict[str, Any] = {
            "id_hito": "HITO 3B",
            "fecha_hora_ejecucion": self.started.isoformat(),
            "script": str(SCRIPT_PATH),
            "version_script": __version__,
            "archivo_validado": str(self.args.input.resolve()),
            "hash_archivo_validado": self.input_hash_before,
            "modo": self.args.modo,
            "codificacion_lectura": self.encoding,
            "delimitador_usado": "\\t" if self.delimiter == "\t" else self.delimiter,
            "delimitador_parametrizado": "\\t" if self.args.delimiter == "\t" else self.args.delimiter,
            "tiene_encabezado": self.has_header,
            "total_filas": len(self.data_rows),
            "total_columnas": 54,
            "distribucion_columnas_observada": dict(sorted(self.column_distribution.items())),
            "total_hallazgos": len(self.findings),
            "hallazgos_por_severidad": {severity: counts_severity.get(severity, 0) for severity in sorted(SEVERITIES)},
            "hallazgos_por_tipo_validacion": dict(sorted(counts_type.items())),
            "hallazgos_por_campo": dict(sorted(counts_field.items())),
            "hallazgos_por_tipo_infraestructura": dict(sorted(counts_infrastructure.items())),
            "hallazgos_por_regla": dict(sorted(counts_rule.items())),
            "hallazgos_por_fila": dict(sorted(counts_row.items(), key=lambda item: int(item[0]))),
            "dictamen_tecnico": dictamen,
            "no_completar_severidad": self.no_complete_severity,
            "reglas_internas_activas": self.apply_internal,
            "reglas_cargadas": len(self.rules),
            "reglas_implementadas": {"total": len(self.implemented_rule_ids), "ids": sorted(self.implemented_rule_ids)},
            "reglas_no_implementadas": {
                "total": len(self.not_implemented_rules),
                "reglas": [
                    {
                        "id_regla": row["ID_REGLA"],
                        "nombre": row["NOMBRE_REGLA"],
                        "estado_implementacion": row["ESTADO_IMPLEMENTACION"],
                    }
                    for row in self.not_implemented_rules
                ],
            },
            "matriz_cargada": {"ruta": str(self.args.matriz_larga.resolve()), "cruces": len(self.matrix_rows)},
            "catalogo_reglas": {"ruta": str(self.args.reglas.resolve()), "reglas": len(self.rules)},
            "pendientes": pending,
            "archivos_salida": [str(result_path.resolve()), str(summary_path.resolve()), str(log_path.resolve())],
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log_lines = [
            "HITO 3B - EJECUCION VALIDADOR IRE 2026",
            f"Fecha y hora: {self.started.isoformat()}",
            f"Script: {SCRIPT_PATH}",
            f"Version: {__version__}",
            f"Entrada: {self.args.input.resolve()}",
            f"SHA-256 entrada: {self.input_hash_before}",
            f"Modo: {self.args.modo}",
            f"Codificacion detectada: {self.encoding}",
            f"Delimitador usado: {repr(self.delimiter)}",
            f"Encabezado: {self.has_header}",
            f"Filas de datos: {len(self.data_rows)}",
            f"Hallazgos: {len(self.findings)}",
            f"Hallazgos por severidad: {json.dumps(summary['hallazgos_por_severidad'], ensure_ascii=False)}",
            f"Dictamen: {dictamen}",
            f"Reglas cargadas: {len(self.rules)}",
            f"Reglas implementadas/habilitadas: {len(self.implemented_rule_ids)}",
            f"Reglas no implementadas: {len(self.not_implemented_rules)}",
            f"Hash posterior: {self.input_hash_after}",
            f"Integridad solo lectura: {self.input_hash_before == self.input_hash_after}",
            "El dictamen tecnico local no equivale a aceptacion por PES.",
        ]
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return result_path, summary_path, log_path, summary

    def run(self) -> tuple[dict[str, Any], int]:
        self.prepare_input()
        self.read_input()
        self.validate_rows()
        self.input_hash_after = sha256(self.args.input)
        if self.input_hash_before != self.input_hash_after:
            raise RuntimeError("El hash del archivo cambio durante la validacion.")
        _result, _summary, _log, summary = self.write_outputs()
        exit_code = 2 if self.args.fail_on_blocking and summary["dictamen_tecnico"] == "NO_APTO_BLOQUEANTES" else 0
        return summary, exit_code


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        validator = Validator(args)
        summary, exit_code = validator.run()
        print(json.dumps({
            "dictamen_tecnico": summary["dictamen_tecnico"],
            "total_hallazgos": summary["total_hallazgos"],
            "hallazgos_por_severidad": summary["hallazgos_por_severidad"],
            "archivos_salida": summary["archivos_salida"],
        }, ensure_ascii=False, indent=2))
        return exit_code
    except (OSError, csv.Error, json.JSONDecodeError, ValidationAbort, RuntimeError) as error:
        print(f"NO_EVALUABLE: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
