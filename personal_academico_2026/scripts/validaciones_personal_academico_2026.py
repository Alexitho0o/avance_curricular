"""Utilidades de normalizacion y validacion para Personal Academico SIES 2026."""

from __future__ import annotations

from datetime import date, datetime
import math
import re
import unicodedata
from typing import Any, Iterable

import pandas as pd


FUENTE_NORMATIVA = "REGLA_NORMATIVA"
FUENTE_ESTRUCTURA = "ESTRUCTURA_OFICIAL"
FUENTE_PREVENTIVA = "VALIDACION_TECNICA_PREVENTIVA"
FUENTE_PENDIENTE = "PENDIENTE_CONFIRMACION"
FECHA_REFERENCIA_PREVENTIVA = date(2026, 6, 11)
VALORES_NO_DISPONIBLES_PREVENTIVOS = {"#N/A", "#N/D", "N/A", "NA", "NO APLICA"}

COLUMNAS_REPORTE = [
    "tipo_archivo",
    "archivo",
    "severidad",
    "regla",
    "estado",
    "columna",
    "fila",
    "valor",
    "mensaje",
    "fuente_regla",
]


def _es_nulo(valor: Any) -> bool:
    if valor is None:
        return True
    try:
        if pd.isna(valor):
            return True
    except TypeError:
        pass
    if isinstance(valor, float) and math.isnan(valor):
        return True
    return False


def _limpiar_tildes_preservando_enie(texto: str) -> str:
    placeholder_mayus = "__CODPA_ENIE_MAYUS__"
    placeholder_minus = "__CODPA_ENIE_MINUS__"
    texto = texto.replace("Ñ", placeholder_mayus).replace("ñ", placeholder_minus)
    texto = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )
    texto = texto.replace(placeholder_mayus, "Ñ").replace(placeholder_minus, "ñ")
    return unicodedata.normalize("NFC", texto)


def _evento(
    *,
    severidad: str,
    regla: str,
    estado: str,
    mensaje: str,
    fuente_regla: str,
    columna: str = "",
    fila: Any = "",
    valor: Any = "",
) -> dict[str, Any]:
    return {
        "severidad": severidad,
        "regla": regla,
        "estado": estado,
        "columna": columna,
        "fila": fila,
        "valor": "" if _es_nulo(valor) else valor,
        "mensaje": mensaje,
        "fuente_regla": fuente_regla,
    }


def _resultado(nombre: str, eventos: list[dict[str, Any]], resumen: dict[str, Any]) -> dict[str, Any]:
    errores = [e for e in eventos if e["severidad"] == "ERROR"]
    advertencias = [e for e in eventos if e["severidad"] == "ADVERTENCIA"]
    return {
        "validacion": nombre,
        "ok": not errores,
        "errores": errores,
        "advertencias": advertencias,
        "resumen": resumen,
        "eventos": eventos,
    }


def _fila_archivo(indice: Any) -> Any:
    if isinstance(indice, int):
        return indice + 2
    return indice


def normalizar_texto_basico(valor: Any) -> str:
    """Normaliza texto para controles preventivos, sin afirmar regla normativa."""
    if _es_nulo(valor):
        return ""
    texto = str(valor)
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = _limpiar_tildes_preservando_enie(texto)
    return texto.upper()


def limpiar_numero_documento(valor: Any) -> str:
    """Limpia caracteres habituales de documento sin asumir tipo RUT."""
    if _es_nulo(valor):
        return ""
    texto = str(valor).strip()
    texto = texto.replace(".", "").replace("-", "").replace(" ", "")
    texto = re.sub(r"[^0-9A-Za-z]", "", texto)
    return texto.upper()


def calcular_dv_rut_chileno(numero: Any) -> str | None:
    """Calcula DV de RUT chileno. Devuelve None si no hay numero valido."""
    numero_limpio = limpiar_numero_documento(numero)
    if not numero_limpio.isdigit():
        return None
    numero_int = int(numero_limpio)
    if numero_int <= 0:
        return None
    suma = 0
    multiplicador = 2
    for digito in reversed(str(numero_int)):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar_dv_rut_chileno(numero: Any, dv: Any) -> dict[str, Any]:
    esperado = calcular_dv_rut_chileno(numero)
    recibido = normalizar_texto_basico(dv)
    if esperado is None:
        return {
            "ok": False,
            "esperado": None,
            "recibido": recibido,
            "mensaje": "No se pudo calcular DV para el numero informado.",
        }
    ok = esperado == recibido
    return {
        "ok": ok,
        "esperado": esperado,
        "recibido": recibido,
        "mensaje": "DV correcto." if ok else "DV no coincide con el numero informado.",
    }


def validar_columnas_exactas(df: pd.DataFrame, columnas_esperadas: Iterable[str]) -> dict[str, Any]:
    esperadas = list(columnas_esperadas)
    actuales = list(df.columns)
    eventos: list[dict[str, Any]] = []

    faltantes = [col for col in esperadas if col not in actuales]
    adicionales = [col for col in actuales if col not in esperadas]
    fuera_orden = [
        {"posicion": i + 1, "esperada": exp, "actual": actuales[i] if i < len(actuales) else None}
        for i, exp in enumerate(esperadas)
        if i >= len(actuales) or actuales[i] != exp
    ]

    if len(actuales) != len(esperadas):
        eventos.append(
            _evento(
                severidad="ERROR",
                regla="cantidad_exacta_columnas",
                estado="FALLA",
                columna="*",
                valor=len(actuales),
                mensaje=f"Cantidad de columnas {len(actuales)}; esperadas {len(esperadas)}.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )
    if faltantes:
        eventos.append(
            _evento(
                severidad="ERROR",
                regla="columnas_faltantes",
                estado="FALLA",
                columna="*",
                valor=", ".join(faltantes),
                mensaje="Existen columnas oficiales faltantes.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )
    if adicionales:
        eventos.append(
            _evento(
                severidad="ERROR",
                regla="columnas_adicionales",
                estado="FALLA",
                columna="*",
                valor=", ".join(adicionales),
                mensaje="Existen columnas no oficiales.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )
    if fuera_orden and not faltantes and not adicionales and len(actuales) == len(esperadas):
        eventos.append(
            _evento(
                severidad="ERROR",
                regla="orden_exacto_columnas",
                estado="FALLA",
                columna="*",
                valor=str(fuera_orden),
                mensaje="Las columnas existen, pero no respetan el orden oficial.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )

    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="estructura_exacta",
                estado="OK",
                mensaje="Cantidad, nombres y orden de columnas coinciden con la estructura oficial.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )

    return _resultado(
        "validar_columnas_exactas",
        eventos,
        {
            "columnas_actuales": len(actuales),
            "columnas_esperadas": len(esperadas),
            "faltantes": faltantes,
            "adicionales": adicionales,
            "fuera_orden": fuera_orden,
        },
    )


def validar_sin_columnas_adicionales(
    df: pd.DataFrame, columnas_esperadas: Iterable[str]
) -> dict[str, Any]:
    esperadas = set(columnas_esperadas)
    adicionales = [col for col in df.columns if col not in esperadas]
    eventos = []
    for columna in adicionales:
        eventos.append(
            _evento(
                severidad="ERROR",
                regla="sin_columnas_adicionales",
                estado="FALLA",
                columna=columna,
                mensaje="Columna no oficial detectada.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="sin_columnas_adicionales",
                estado="OK",
                mensaje="No se detectaron columnas adicionales.",
                fuente_regla=FUENTE_ESTRUCTURA,
            )
        )
    return _resultado(
        "validar_sin_columnas_adicionales",
        eventos,
        {"adicionales": adicionales},
    )


def validar_campos_obligatorios_basicos(
    df: pd.DataFrame, columnas_obligatorias: Iterable[str]
) -> dict[str, Any]:
    """Valida una lista preventiva; no inventa obligatoriedad normativa."""
    eventos: list[dict[str, Any]] = []
    for columna in columnas_obligatorias:
        if columna not in df.columns:
            eventos.append(
                _evento(
                    severidad="ADVERTENCIA",
                    regla="campo_obligatorio_basico_preventivo",
                    estado="NO_EVALUADO",
                    columna=columna,
                    mensaje="Columna no existe; la estructura exacta debe reportar este error.",
                    fuente_regla=FUENTE_PREVENTIVA,
                )
            )
            continue
        vacios = df[columna].isna() | (df[columna].astype(str).str.strip() == "")
        for idx, valor in df.loc[vacios, columna].items():
            eventos.append(
                _evento(
                    severidad="ERROR",
                    regla="campo_obligatorio_basico_preventivo",
                    estado="FALLA",
                    columna=columna,
                    fila=_fila_archivo(idx),
                    valor=valor,
                    mensaje=(
                        "Campo vacio en lista obligatoria basica. "
                        "VALIDACION TECNICA PREVENTIVA."
                    ),
                    fuente_regla=FUENTE_PREVENTIVA,
                )
            )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="campo_obligatorio_basico_preventivo",
                estado="OK",
                mensaje="Campos obligatorios basicos preventivos presentes.",
                fuente_regla=FUENTE_PREVENTIVA,
            )
        )
    return _resultado(
        "validar_campos_obligatorios_basicos",
        eventos,
        {"columnas_evaluadas": list(columnas_obligatorias)},
    )


def _normalizar_disponibilidad(valor: Any) -> str:
    return re.sub(r"\s+", " ", str(valor).strip()).upper()


def _parse_fecha(valor: Any) -> tuple[bool, str, str]:
    if _es_nulo(valor) or str(valor).strip() == "":
        return True, "VACIA", ""
    texto = str(valor).strip()
    if _normalizar_disponibilidad(texto) in VALORES_NO_DISPONIBLES_PREVENTIVOS:
        return True, "NO_DISPONIBLE", texto
    formatos = [
        ("%d-%m-%Y", "DD-MM-AAAA"),
        ("%Y-%m-%d", "AAAA-MM-DD"),
        ("%d/%m/%Y", "DD/MM/AAAA"),
        ("%Y/%m/%d", "AAAA/MM/DD"),
        ("%d-%m-%y", "DD-MM-AA"),
        ("%d/%m/%y", "DD/MM/AA"),
    ]
    for formato, etiqueta in formatos:
        try:
            fecha = datetime.strptime(texto, formato).date()
            if fecha > FECHA_REFERENCIA_PREVENTIVA:
                return True, "FUTURA", texto
            if etiqueta in {"DD-MM-AA", "DD/MM/AA"}:
                return True, "AMBIGUA", texto
            return True, etiqueta, ""
        except ValueError:
            continue
    return False, "INVALIDA", texto


def validar_fechas_formato(df: pd.DataFrame, columnas_fecha: Iterable[str]) -> dict[str, Any]:
    eventos: list[dict[str, Any]] = []
    for columna in columnas_fecha:
        if columna not in df.columns:
            continue
        for idx, valor in df[columna].items():
            ok, formato, texto = _parse_fecha(valor)
            if not ok:
                eventos.append(
                    _evento(
                        severidad="ERROR",
                        regla="fecha_formato",
                        estado="FALLA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=texto,
                        mensaje="Fecha imposible o formato no reconocido.",
                        fuente_regla=FUENTE_NORMATIVA,
                    )
                )
            elif formato == "NO_DISPONIBLE":
                eventos.append(
                    _evento(
                        severidad="ADVERTENCIA",
                        regla="fecha_no_disponible",
                        estado="ADVERTENCIA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=texto,
                        mensaje=(
                            "Valor de fecha no disponible preservado; no se clasifica "
                            "como error de formato."
                        ),
                        fuente_regla=FUENTE_PREVENTIVA,
                    )
                )
            elif formato == "VACIA" and columna == "FECHA_NACIMIENTO":
                eventos.append(
                    _evento(
                        severidad="ADVERTENCIA",
                        regla="fecha_vacia",
                        estado="ADVERTENCIA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor="",
                        mensaje="Campo de fecha vacio evaluado preventivamente.",
                        fuente_regla=FUENTE_PREVENTIVA,
                    )
                )
            elif formato == "AMBIGUA":
                eventos.append(
                    _evento(
                        severidad="ADVERTENCIA",
                        regla="fecha_ambigua",
                        estado="ADVERTENCIA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=texto,
                        mensaje=(
                            "Fecha interpretable con anio de dos digitos; no se inventa "
                            "siglo ni se normaliza automaticamente."
                        ),
                        fuente_regla=FUENTE_PREVENTIVA,
                    )
                )
            elif formato == "FUTURA":
                eventos.append(
                    _evento(
                        severidad="ERROR",
                        regla="fecha_futura",
                        estado="FALLA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=texto,
                        mensaje="Fecha futura respecto a 2026-06-11.",
                        fuente_regla=FUENTE_PREVENTIVA,
                    )
                )
            elif formato == "AAAA-MM-DD":
                eventos.append(
                    _evento(
                        severidad="ADVERTENCIA",
                        regla="fecha_tolerancia_iso",
                        estado="ADVERTENCIA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=valor,
                        mensaje=(
                            "Formato AAAA-MM-DD aceptado solo como tolerancia tecnica; "
                            "el instructivo declara DD-MM-AAAA."
                        ),
                        fuente_regla=FUENTE_PREVENTIVA,
                    )
                )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="fecha_formato",
                estado="OK",
                mensaje="No se detectaron fechas invalidas en columnas evaluadas.",
                fuente_regla=FUENTE_NORMATIVA,
            )
        )
    return _resultado(
        "validar_fechas_formato",
        eventos,
        {"columnas_evaluadas": list(columnas_fecha)},
    )


def _parse_hora(valor: Any) -> tuple[bool, float | None]:
    if _es_nulo(valor) or str(valor).strip() == "":
        return True, None
    texto = str(valor).strip().replace(",", ".")
    try:
        return True, float(texto)
    except ValueError:
        return False, None


def validar_horas_numericas(df: pd.DataFrame, columnas_horas: Iterable[str]) -> dict[str, Any]:
    eventos: list[dict[str, Any]] = []
    for columna in columnas_horas:
        if columna not in df.columns:
            continue
        for idx, valor in df[columna].items():
            ok, numero = _parse_hora(valor)
            if not ok:
                eventos.append(
                    _evento(
                        severidad="ERROR",
                        regla="horas_numericas",
                        estado="FALLA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=valor,
                        mensaje="Valor de horas no numerico.",
                        fuente_regla=FUENTE_NORMATIVA,
                    )
                )
            elif numero is not None and numero < 0:
                eventos.append(
                    _evento(
                        severidad="ERROR",
                        regla="horas_no_negativas",
                        estado="FALLA",
                        columna=columna,
                        fila=_fila_archivo(idx),
                        valor=valor,
                        mensaje="Valor de horas negativo.",
                        fuente_regla=FUENTE_PREVENTIVA,
                    )
                )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="horas_numericas",
                estado="OK",
                mensaje="No se detectaron horas no numericas ni negativas.",
                fuente_regla=FUENTE_NORMATIVA,
            )
        )
    return _resultado(
        "validar_horas_numericas",
        eventos,
        {"columnas_evaluadas": list(columnas_horas)},
    )


def validar_duplicados_documento(df: pd.DataFrame) -> dict[str, Any]:
    columnas = ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"]
    eventos: list[dict[str, Any]] = []
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        eventos.append(
            _evento(
                severidad="ADVERTENCIA",
                regla="duplicados_documento",
                estado="NO_EVALUADO",
                columna="*",
                valor=", ".join(faltantes),
                mensaje="No se pudo evaluar duplicados por columnas faltantes.",
                fuente_regla=FUENTE_NORMATIVA,
            )
        )
        return _resultado("validar_duplicados_documento", eventos, {"duplicados": 0})

    claves = df[columnas].fillna("").astype(str).apply(
        lambda row: tuple(normalizar_texto_basico(v) for v in row), axis=1
    )
    duplicados_mask = claves.duplicated(keep=False)
    for idx in df.index[duplicados_mask]:
        eventos.append(
            _evento(
                severidad="ERROR",
                regla="duplicados_documento",
                estado="FALLA",
                columna="TIPO_DOCUMENTO+NUM_DOCUMENTO+DV",
                fila=_fila_archivo(idx),
                valor="|".join(claves.loc[idx]),
                mensaje="Registro duplicado por documento; el instructivo exige evitar duplicidades.",
                fuente_regla=FUENTE_NORMATIVA,
            )
        )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="duplicados_documento",
                estado="OK",
                mensaje="No se detectaron duplicados por documento.",
                fuente_regla=FUENTE_NORMATIVA,
            )
        )
    return _resultado(
        "validar_duplicados_documento",
        eventos,
        {"duplicados": int(duplicados_mask.sum())},
    )


def validar_valores_basicos_preventivos(df: pd.DataFrame) -> dict[str, Any]:
    columnas = [
        "SEXO",
        "VIGENCIA",
        "NACIONALIDAD",
        "NIVEL_FORMACION_ACADEMICO",
        "TIPO_DOCUMENTO",
    ]
    eventos: list[dict[str, Any]] = []
    for columna in columnas:
        if columna not in df.columns:
            continue
        vacios = df[columna].isna() | (df[columna].astype(str).str.strip() == "")
        for idx, valor in df.loc[vacios, columna].items():
            eventos.append(
                _evento(
                    severidad="ERROR",
                    regla="valor_basico_no_vacio_preventivo",
                    estado="FALLA",
                    columna=columna,
                    fila=_fila_archivo(idx),
                    valor=valor,
                    mensaje="Valor basico vacio. VALIDACION TECNICA PREVENTIVA.",
                    fuente_regla=FUENTE_PREVENTIVA,
                )
            )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="valor_basico_no_vacio_preventivo",
                estado="OK",
                mensaje="Valores basicos preventivos no vacios.",
                fuente_regla=FUENTE_PREVENTIVA,
            )
        )
    return _resultado(
        "validar_valores_basicos_preventivos",
        eventos,
        {"columnas_evaluadas": columnas},
    )


def validar_dv_documentos_chilenos(df: pd.DataFrame) -> dict[str, Any]:
    eventos: list[dict[str, Any]] = []
    requeridas = ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"]
    if any(col not in df.columns for col in requeridas):
        return _resultado(
            "validar_dv_documentos_chilenos",
            [
                _evento(
                    severidad="ADVERTENCIA",
                    regla="dv_rut_chileno",
                    estado="NO_EVALUADO",
                    columna="*",
                    mensaje="No se pudo evaluar DV por columnas faltantes.",
                    fuente_regla=FUENTE_PREVENTIVA,
                )
            ],
            {"evaluados": 0},
        )
    evaluados = 0
    for idx, row in df.iterrows():
        tipo = normalizar_texto_basico(row["TIPO_DOCUMENTO"])
        numero = limpiar_numero_documento(row["NUM_DOCUMENTO"])
        dv = normalizar_texto_basico(row["DV"])
        if tipo == "R" or (tipo == "" and numero.isdigit() and dv):
            evaluados += 1
            resultado = validar_dv_rut_chileno(numero, dv)
            if not resultado["ok"]:
                eventos.append(
                    _evento(
                        severidad="ERROR",
                        regla="dv_rut_chileno",
                        estado="FALLA",
                        columna="DV",
                        fila=_fila_archivo(idx),
                        valor=dv,
                        mensaje=resultado["mensaje"],
                        fuente_regla=FUENTE_NORMATIVA,
                    )
                )
        elif tipo not in {"P", ""}:
            eventos.append(
                _evento(
                    severidad="ADVERTENCIA",
                    regla="tipo_documento_no_evaluado_dv",
                    estado="ADVERTENCIA",
                    columna="TIPO_DOCUMENTO",
                    fila=_fila_archivo(idx),
                    valor=tipo,
                    mensaje="Tipo de documento no evaluado para DV.",
                    fuente_regla=FUENTE_PREVENTIVA,
                )
            )
    if not eventos:
        eventos.append(
            _evento(
                severidad="INFO",
                regla="dv_rut_chileno",
                estado="OK",
                mensaje="DV evaluado sin errores cuando correspondio.",
                fuente_regla=FUENTE_NORMATIVA,
            )
        )
    return _resultado(
        "validar_dv_documentos_chilenos",
        eventos,
        {"evaluados": evaluados},
    )


def construir_reporte_validacion(
    nombre_archivo: str, tipo_archivo: str, resultados: Iterable[dict[str, Any]]
) -> pd.DataFrame:
    filas: list[dict[str, Any]] = []
    for resultado in resultados:
        eventos = resultado.get("eventos", [])
        for evento in eventos:
            filas.append(
                {
                    "tipo_archivo": tipo_archivo,
                    "archivo": nombre_archivo,
                    "severidad": evento.get("severidad", ""),
                    "regla": evento.get("regla", ""),
                    "estado": evento.get("estado", ""),
                    "columna": evento.get("columna", ""),
                    "fila": evento.get("fila", ""),
                    "valor": evento.get("valor", ""),
                    "mensaje": evento.get("mensaje", ""),
                    "fuente_regla": evento.get("fuente_regla", ""),
                }
            )
    if not filas:
        filas.append(
            {
                "tipo_archivo": tipo_archivo,
                "archivo": nombre_archivo,
                "severidad": "INFO",
                "regla": "sin_eventos",
                "estado": "OK",
                "columna": "",
                "fila": "",
                "valor": "",
                "mensaje": "No se registraron eventos de validacion.",
                "fuente_regla": FUENTE_PREVENTIVA,
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_REPORTE)
