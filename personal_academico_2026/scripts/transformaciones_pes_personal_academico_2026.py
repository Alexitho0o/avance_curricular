"""Transformaciones tecnicas de salida para archivos PES/SIES 2026.

Estas funciones no modifican la base general. Solo preparan filas candidatas de
exportacion y devuelven eventos auditables.
"""

from __future__ import annotations

from copy import copy
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import re
import unicodedata


FECHA_REFERENCIA = date(2026, 6, 11)
FECHA_CORTE_ESPECIALIDAD = date(2026, 5, 31)
FUENTE_PREVENTIVA = "VALIDACION_TECNICA_PREVENTIVA"
FUENTE_PENDIENTE = "PENDIENTE_CONFIRMACION"

COLUMNAS_FECHA = {
    "en_institucion": [
        "FECHA_NACIMIENTO",
        "FECHA_OBT_TIT_O_GRADO",
        "FECHA_OBTENCION_ESPECIALIDAD",
    ],
    "fuera_institucion": [
        "FECHA_NACIMIENTO",
        "FECHA_OBT_TIT_O_GRADO",
        "FECHA_OBTENCION_ESPECIALIDAD",
        "FECHA_INICIO_PROGRAMA_ESTUDIOS",
    ],
}

COLUMNAS_HORAS = {
    "en_institucion": [
        "TOTAL_HORAS_PRINCIPAL_PROGRAMA",
        "NUM_HORAS_PLANTA",
        "NUM_HORAS_CONTRATA",
        "NUM_HORAS_HONORARIOS",
    ],
    "fuera_institucion": ["TOTAL_HORAS_CONTRATADAS"],
}

HORAS_OBLIGATORIAS_EN_INSTITUCION = [
    "NUM_HORAS_PLANTA",
    "NUM_HORAS_CONTRATA",
    "NUM_HORAS_HONORARIOS",
]

BLOQUE_ESPECIALIDAD = [
    "NIVEL_FORMACION_ESPECIALIDAD",
    "TIPO_ESPECIALIDAD",
    "NOMBRE_ESPECIALIDAD",
    "NOMBRE_INST_OBT_ESPECIALIDAD",
    "PAIS_OBTENCION_ESPECIALIDAD",
    "FECHA_OBTENCION_ESPECIALIDAD",
]

DEPENDIENTES_ESPECIALIDAD = [
    "TIPO_ESPECIALIDAD",
    "NOMBRE_ESPECIALIDAD",
    "NOMBRE_INST_OBT_ESPECIALIDAD",
    "PAIS_OBTENCION_ESPECIALIDAD",
    "FECHA_OBTENCION_ESPECIALIDAD",
]

CAMPOS_ESTRUCTURADOS_NO_CARGABLES = {
    "NIVEL_FORMACION_ACADEMICO",
    "PAIS_OBTENCION_TIT_O_GRADO",
    "FECHA_OBT_TIT_O_GRADO",
    "NACIONALIDAD",
    "SEXO",
    "CARGO_NORMALIZADO",
    "VIGENCIA",
}

VALORES_NO_CARGABLES = {"#N/A", "#N/D", "N/A", "NA"}


def _normalizar_token(valor: object) -> str:
    return re.sub(r"\s+", " ", "" if valor is None else str(valor).strip()).upper()


def detectar_valor_no_cargable(valor: object) -> bool:
    return _normalizar_token(valor) in VALORES_NO_CARGABLES


def normalizar_texto_pes(valor: object) -> str:
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKC", texto)
    texto = re.sub(r"[\r\n\t;]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip().upper()
    texto = texto.replace("Ñ", "N").replace("ñ", "n")
    texto = "".join(
        ch
        for ch in unicodedata.normalize("NFD", texto)
        if unicodedata.category(ch) != "Mn"
    )
    texto = unicodedata.normalize("NFC", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch)[0] != "C")
    texto = re.sub(r"[^A-Z0-9 .,/()\\-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_solo_letras_az_pes(valor: object) -> str:
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("Ñ", "N").replace("ñ", "n")
    texto = "".join(
        ch
        for ch in unicodedata.normalize("NFD", texto)
        if unicodedata.category(ch) != "Mn"
    )
    texto = unicodedata.normalize("NFC", texto).upper()
    texto = re.sub(r"[^A-Z]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _parse_fecha(valor: str) -> date | None:
    texto = valor.strip()
    if not texto or detectar_valor_no_cargable(texto) or _normalizar_token(texto) == "NO APLICA":
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


def convertir_fecha_pes_ddmmaaaa(valor: object) -> str:
    texto = "" if valor is None else str(valor).strip()
    fecha = _parse_fecha(texto)
    if fecha is None:
        return texto
    return fecha.strftime("%d-%m-%Y")


def es_fecha_futura(valor: object) -> bool:
    fecha = _parse_fecha("" if valor is None else str(valor))
    return bool(fecha and fecha > FECHA_REFERENCIA)


def normalizar_hora_pes(valor: object) -> str:
    texto = "" if valor is None else str(valor).strip()
    if not texto or detectar_valor_no_cargable(texto):
        return texto
    normalizado = texto.replace(",", ".")
    try:
        numero = Decimal(normalizado)
    except InvalidOperation:
        return texto
    if "." not in normalizado:
        return texto
    cuantizado = numero.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    salida = format(cuantizado, "f").rstrip("0").rstrip(".")
    return salida if salida else "0"


def _es_numero_pes(valor: object) -> bool:
    texto = "" if valor is None else str(valor).strip().replace(",", ".")
    if not texto:
        return False
    try:
        Decimal(texto)
        return True
    except InvalidOperation:
        return False


def normalizar_horas_obligatorias_pes(row: dict[str, str], header: list[str]) -> tuple[dict[str, str], list[dict[str, str]]]:
    nueva = copy(row)
    eventos: list[dict[str, str]] = []
    for campo in HORAS_OBLIGATORIAS_EN_INSTITUCION:
        if campo not in header:
            continue
        original = nueva.get(campo, "")
        if not original.strip() or detectar_valor_no_cargable(original):
            convertido = "0"
            mensaje = "Hora obligatoria vacia o no cargable completada con 0 para PES."
            tipo_evento = "HORA_OBLIGATORIA_COMPLETADA_CERO"
        else:
            convertido = normalizar_hora_pes(original)
            mensaje = "Hora obligatoria normalizada para PES."
            tipo_evento = "HORA_OBLIGATORIA_NORMALIZADA"
        if convertido != original:
            nueva[campo] = convertido
            eventos.append(
                {
                    "tipo_evento": tipo_evento,
                    "severidad": "INFO",
                    "columna": campo,
                    "valor_original": original,
                    "valor_transformado": convertido,
                    "mensaje": mensaje,
                    "fuente_regla": FUENTE_PREVENTIVA,
                }
            )
    return nueva, eventos


def _valor_cargable(valor: object) -> bool:
    texto = "" if valor is None else str(valor).strip()
    return bool(texto) and not detectar_valor_no_cargable(texto) and _normalizar_token(texto) != "NO APLICA"


def _limpiar_campos(
    row: dict[str, str],
    campos: list[str],
    motivo: str,
    tipo_evento: str,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    nueva = copy(row)
    eventos: list[dict[str, str]] = []
    for campo in campos:
        original = nueva.get(campo, "")
        if original != "":
            nueva[campo] = ""
            eventos.append(
                {
                    "tipo_evento": tipo_evento,
                    "severidad": "WARN",
                    "columna": campo,
                    "valor_original": original,
                    "valor_transformado": "",
                    "mensaje": motivo,
                    "fuente_regla": FUENTE_PREVENTIVA,
                }
            )
    return nueva, eventos


def normalizar_bloque_especialidad_pes(row: dict[str, str], header: list[str]) -> tuple[dict[str, str], list[dict[str, str]]]:
    nueva = copy(row)
    eventos: list[dict[str, str]] = []
    nivel_academico = _normalizar_token(nueva.get("NIVEL_FORMACION_ACADEMICO", ""))
    campos_bloque = [campo for campo in BLOQUE_ESPECIALIDAD if campo in header]
    dependientes = [campo for campo in DEPENDIENTES_ESPECIALIDAD if campo in header]

    if nivel_academico in {"5", "6", "7", "8"}:
        nueva, nuevos_eventos = _limpiar_campos(
            nueva,
            campos_bloque,
            "Bloque de especialidad limpiado para PES porque NIVEL_FORMACION_ACADEMICO es 5, 6, 7 u 8.",
            "BLOQUE_ESPECIALIDAD_LIMPIADO_NIVEL_ACADEMICO",
        )
        eventos.extend(nuevos_eventos)
        return nueva, eventos

    nivel_especialidad = nueva.get("NIVEL_FORMACION_ESPECIALIDAD", "")
    fecha_especialidad = nueva.get("FECHA_OBTENCION_ESPECIALIDAD", "")
    fecha = _parse_fecha(fecha_especialidad)
    fecha_no_cargable = (
        detectar_valor_no_cargable(fecha_especialidad)
        or _normalizar_token(fecha_especialidad) == "NO APLICA"
    )

    if not _valor_cargable(nivel_especialidad):
        nueva, nuevos_eventos = _limpiar_campos(
            nueva,
            dependientes,
            "Campos dependientes de especialidad limpiados porque NIVEL_FORMACION_ESPECIALIDAD no tiene valor cargable.",
            "BLOQUE_ESPECIALIDAD_DEPENDIENTE_LIMPIADO_SIN_NIVEL",
        )
        eventos.extend(nuevos_eventos)
        return nueva, eventos

    if fecha_no_cargable:
        nueva, nuevos_eventos = _limpiar_campos(
            nueva,
            ["FECHA_OBTENCION_ESPECIALIDAD"],
            "Fecha de especialidad no cargable limpiada para PES.",
            "FECHA_ESPECIALIDAD_LIMPIADA_NO_CARGABLE",
        )
        eventos.extend(nuevos_eventos)
    elif fecha and fecha > FECHA_CORTE_ESPECIALIDAD and not _valor_cargable(nivel_especialidad):
        nueva, nuevos_eventos = _limpiar_campos(
            nueva,
            dependientes,
            "Bloque de especialidad limpiado por fecha posterior a 31-05-2026 sin nivel valido.",
            "BLOQUE_ESPECIALIDAD_LIMPIADO_FECHA_FUTURA_SIN_NIVEL",
        )
        eventos.extend(nuevos_eventos)
    return nueva, eventos


def completar_comuna_mayor_funcion(row: dict[str, str], header: list[str]) -> tuple[dict[str, str], list[dict[str, str]]]:
    nueva = copy(row)
    eventos: list[dict[str, str]] = []
    if "COMUNA_MAYOR_FUNCION" not in header:
        return nueva, eventos
    actual = nueva.get("COMUNA_MAYOR_FUNCION", "").strip()
    fallback = nueva.get("COMUNA_PRINCIPAL_PROGRAMA", "").strip()
    if not actual and fallback:
        nueva["COMUNA_MAYOR_FUNCION"] = fallback
        eventos.append(
            {
                "tipo_evento": "COMUNA_MAYOR_FUNCION_COMPLETADA",
                "severidad": "WARN",
                "columna": "COMUNA_MAYOR_FUNCION",
                "valor_original": actual,
                "valor_transformado": fallback,
                "mensaje": "Comuna mayor funcion completada desde COMUNA_PRINCIPAL_PROGRAMA solo para exportacion.",
                "fuente_regla": FUENTE_PREVENTIVA,
            }
        )
    return nueva, eventos


def detectar_registro_no_cargable(row: dict[str, str], header: list[str], tipo_archivo: str) -> list[str]:
    motivos: list[str] = []
    for campo in CAMPOS_ESTRUCTURADOS_NO_CARGABLES:
        if campo in header and detectar_valor_no_cargable(row.get(campo, "")):
            motivos.append(f"{campo}=VALOR_NO_CARGABLE")
    if "COMUNA_MAYOR_FUNCION" in header:
        comuna = row.get("COMUNA_MAYOR_FUNCION", "").strip()
        fallback = row.get("COMUNA_PRINCIPAL_PROGRAMA", "").strip()
        if not comuna and not fallback:
            motivos.append("COMUNA_MAYOR_FUNCION_SIN_VALOR_NI_FALLBACK")
    for campo in COLUMNAS_FECHA.get(tipo_archivo, []):
        if campo in header and es_fecha_futura(row.get(campo, "")):
            motivos.append(f"{campo}=FECHA_FUTURA")
    fecha_esp = row.get("FECHA_OBTENCION_ESPECIALIDAD", "")
    nivel_esp = row.get("NIVEL_FORMACION_ESPECIALIDAD", "")
    fecha = _parse_fecha(fecha_esp)
    if fecha and fecha > FECHA_CORTE_ESPECIALIDAD and _valor_cargable(nivel_esp):
        motivos.append("FECHA_OBTENCION_ESPECIALIDAD=POSTERIOR_31_05_2026")
    for campo in HORAS_OBLIGATORIAS_EN_INSTITUCION:
        if campo in header and not _es_numero_pes(row.get(campo, "")):
            motivos.append(f"{campo}=HORA_OBLIGATORIA_NO_NUMERICA")
    return motivos


def transformar_fila_para_pes(
    row: dict[str, str],
    header: list[str],
    tipo_archivo: str,
    *,
    formato_fecha_pes: bool = True,
    normalizar_texto: bool = True,
    completar_comuna: bool = True,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    nueva = copy(row)
    eventos: list[dict[str, str]] = []

    if normalizar_texto:
        for campo in header:
            original = nueva.get(campo, "")
            if campo == "NOMBRE_TITULO_O_GRADO":
                convertido = normalizar_solo_letras_az_pes(original)
                tipo_evento = "NOMBRE_TITULO_SOLO_A_Z"
                mensaje = (
                    "Motivo PES: El NOMBRE_TITULO_O_GRADO debe contener letras "
                    "mayusculas de la A a la Z."
                )
            else:
                convertido = normalizar_texto_pes(original)
                tipo_evento = "TEXTO_NORMALIZADO_PES"
                mensaje = "Texto normalizado a caracteres seguros PES: A-Z, 0-9, espacio y signos permitidos."
            if convertido != original:
                nueva[campo] = convertido
                eventos.append(
                    {
                        "tipo_evento": tipo_evento,
                        "severidad": "INFO",
                        "columna": campo,
                        "valor_original": original,
                        "valor_transformado": convertido,
                        "mensaje": mensaje,
                        "fuente_regla": FUENTE_PREVENTIVA,
                    }
                )

    for campo in COLUMNAS_FECHA.get(tipo_archivo, []):
        if campo in header and formato_fecha_pes:
            original = nueva.get(campo, "")
            convertido = convertir_fecha_pes_ddmmaaaa(original)
            if convertido != original:
                nueva[campo] = convertido
                eventos.append(
                    {
                        "tipo_evento": "FECHA_FORMATO_PES",
                        "severidad": "INFO",
                        "columna": campo,
                        "valor_original": original,
                        "valor_transformado": convertido,
                        "mensaje": "Fecha convertida a DD-MM-AAAA para PES.",
                        "fuente_regla": FUENTE_PREVENTIVA,
                    }
                )

    if completar_comuna:
        nueva, comuna_eventos = completar_comuna_mayor_funcion(nueva, header)
        eventos.extend(comuna_eventos)

    nueva, especialidad_eventos = normalizar_bloque_especialidad_pes(nueva, header)
    eventos.extend(especialidad_eventos)

    nueva, horas_obligatorias_eventos = normalizar_horas_obligatorias_pes(nueva, header)
    eventos.extend(horas_obligatorias_eventos)

    for campo in COLUMNAS_HORAS.get(tipo_archivo, []):
        if campo in header:
            original = nueva.get(campo, "")
            convertido = normalizar_hora_pes(original)
            if convertido != original:
                nueva[campo] = convertido
                eventos.append(
                    {
                        "tipo_evento": "HORA_DECIMAL_NORMALIZADA",
                        "severidad": "INFO",
                        "columna": campo,
                        "valor_original": original,
                        "valor_transformado": convertido,
                        "mensaje": "Hora numerica normalizada a maximo 2 decimales para PES.",
                        "fuente_regla": FUENTE_PREVENTIVA,
                    }
                )

    return nueva, eventos


def generar_auditoria_transformaciones(path: Path, eventos: list[dict[str, object]]) -> None:
    fields = [
        "timestamp",
        "tipo_evento",
        "severidad",
        "fila_origen",
        "columna",
        "valor_original",
        "valor_transformado",
        "accion",
        "mensaje",
        "fuente_regla",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(eventos)
