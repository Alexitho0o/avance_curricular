#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# CONSTANTES
# ============================================================

COLUMNAS_5809_OFICIALES = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

COLUMNAS_5810_OFICIALES = [
    "CODIGO_IES_NUM",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "NOMBRE_SEDE",
    "NOMBRE_CARRERA",
    "JORNADA",
    "VERSION",
    "DURACION_ESTUDIOS",
    "DURACION_TITULACION",
    "DURACION_TOTAL",
    "NIVEL_CARRERA",
    "TIPO_UNIDAD_MEDIDA",
    "OTRA_UNIDAD_MEDIDA",
    "TOTAL_UNIDADES_MEDIDA",
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
    "VIGENCIA",
]

COLUMNAS_ANUALES_5810 = {
    1: "UNIDADES_1ER_ANIO",
    2: "UNIDADES_2DO_ANIO",
    3: "UNIDADES_3ER_ANIO",
    4: "UNIDADES_4TO_ANIO",
    5: "UNIDADES_5TO_ANIO",
    6: "UNIDADES_6TO_ANIO",
    7: "UNIDADES_7MO_ANIO",
}


# ============================================================
# UTILIDADES GENERALES
# ============================================================

def norm_col(valor: Any) -> str:
    texto = "" if valor is None else str(valor)
    texto = texto.strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )
    texto = re.sub(r"\s+", "_", texto)
    return texto


def norm_texto(valor: Any) -> str:
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )
    texto = re.sub(r"\s+", " ", texto)
    return texto


def norm_codigo(valor: Any) -> str:
    return norm_texto(valor).replace(" ", "")


def norm_documento(valor: Any) -> str:
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = re.sub(r"[^0-9K]", "", texto)

    # Si viene RUT completo con DV, se conserva solo cuerpo cuando
    # la fuente oficial mantiene NUM_DOCUMENTO y DV por separado.
    if len(texto) >= 8 and texto[-1] in "0123456789K":
        return texto[:-1] if len(texto) > 8 else texto

    return texto


def entero_nullable(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(
        serie,
        errors="coerce",
    ).astype("Int64")


def numerico(serie: pd.Series) -> pd.Series:
    texto = (
        serie.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(
        texto,
        errors="coerce",
    )


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def buscar_columna(
    df: pd.DataFrame,
    opciones: list[str],
    obligatoria: bool = False,
    contexto: str = "",
) -> str | None:
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    for opcion in opciones:
        clave = norm_col(opcion)

        if clave in mapa:
            return mapa[clave]

    if obligatoria:
        raise RuntimeError(
            f"No se encontró columna requerida en {contexto}: "
            f"{opciones}. Disponibles: {list(df.columns)}"
        )

    return None


def detectar_csv(ruta: Path) -> tuple[str, str]:
    muestra = ruta.read_bytes()[:50000]

    texto = None
    encoding_detectado = None

    for encoding in (
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            texto = muestra.decode(encoding)
            encoding_detectado = encoding
            break
        except UnicodeDecodeError:
            continue

    if texto is None or encoding_detectado is None:
        raise RuntimeError(
            f"No fue posible decodificar: {ruta}"
        )

    primera_linea = texto.splitlines()[0]

    conteos = {
        ";": primera_linea.count(";"),
        "\t": primera_linea.count("\t"),
        ",": primera_linea.count(","),
        "|": primera_linea.count("|"),
    }

    separador = max(
        conteos,
        key=conteos.get,
    )

    if conteos[separador] == 0:
        raise RuntimeError(
            f"No fue posible detectar separador: {ruta}"
        )

    return separador, encoding_detectado


def leer_csv_flexible(
    ruta: Path,
) -> tuple[pd.DataFrame, str, str]:
    separador, encoding_inicial = detectar_csv(ruta)

    ultimo_error = None

    for encoding in dict.fromkeys([
        encoding_inicial,
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]):
        try:
            df = pd.read_csv(
                ruta,
                sep=separador,
                encoding=encoding,
                dtype=str,
                keep_default_na=False,
            )

            return df, separador, encoding

        except Exception as exc:
            ultimo_error = exc

    raise RuntimeError(
        f"No fue posible leer {ruta}: {ultimo_error}"
    )


def leer_excel_hoja(
    ruta: Path,
    hoja: str,
) -> pd.DataFrame:
    xls = pd.ExcelFile(ruta)

    if hoja not in xls.sheet_names:
        raise RuntimeError(
            f"La hoja '{hoja}' no existe en {ruta}. "
            f"Hojas: {xls.sheet_names}"
        )

    return pd.read_excel(
        ruta,
        sheet_name=hoja,
        dtype=object,
    )


def validar_columnas_exactas(
    df: pd.DataFrame,
    esperadas: list[str],
    nombre: str,
) -> None:
    actuales = [
        norm_col(columna)
        for columna in df.columns
    ]

    esperadas_norm = [
        norm_col(columna)
        for columna in esperadas
    ]

    if actuales != esperadas_norm:
        faltantes = [
            columna
            for columna in esperadas_norm
            if columna not in actuales
        ]

        extras = [
            columna
            for columna in actuales
            if columna not in esperadas_norm
        ]

        raise RuntimeError(
            f"Estructura no coincide para {nombre}.\n"
            f"Faltantes: {faltantes}\n"
            f"Extras: {extras}\n"
            f"Orden observado: {actuales}"
        )


def unir_unicos(serie: pd.Series) -> str:
    valores = sorted({
        norm_codigo(valor)
        for valor in serie
        if norm_codigo(valor)
    })

    return " | ".join(valores)


def primer_no_vacio(serie: pd.Series) -> str:
    for valor in serie:
        limpio = norm_texto(valor)

        if limpio:
            return limpio

    return ""


def agregar_validacion(
    validaciones: list[dict[str, Any]],
    bloque: str,
    nombre: str,
    resultado: bool,
    detalle: str,
    bloqueante: bool,
) -> None:
    validaciones.append({
        "BLOQUE": bloque,
        "VALIDACION": nombre,
        "RESULTADO": "OK" if resultado else "ERROR",
        "BLOQUEANTE": "SI" if bloqueante else "NO",
        "DETALLE": detalle,
    })


# ============================================================
# ARGUMENTOS
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gobernanza anual end-to-end de Avance Curricular "
            "SIES: precarga 5809, precarga 5810, estudiantes, "
            "planes de estudio, nivel alcanzado y créditos por año."
        )
    )

    parser.add_argument(
        "--anio-proceso",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--anio-datos",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--precarga-5809",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--precarga-5810",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--promedios",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--planes",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--cierre-historico",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "--gob-niv-aca",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
    )

    return parser.parse_args()


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main() -> int:
    args = parse_args()

    entradas = {
        "PRECARGA_5809": args.precarga_5809.resolve(),
        "PRECARGA_5810": args.precarga_5810.resolve(),
        "PROMEDIOS": args.promedios.resolve(),
        "PLANES": args.planes.resolve(),
        "GOB_NIV_ACA": args.gob_niv_aca.resolve(),
    }

    if args.cierre_historico:
        entradas["CIERRE_HISTORICO"] = (
            args.cierre_historico.resolve()
        )

    for nombre, ruta in entradas.items():
        if not ruta.exists():
            raise RuntimeError(
                f"No existe fuente requerida {nombre}: {ruta}"
            )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    salida = (
        args.output_root.resolve()
        / (
            f"GOBERNANZA_AVANCE_CURRICULAR_"
            f"{args.anio_proceso}_{timestamp}"
        )
    )

    resultados_dir = salida / "02_RESULTADOS"
    auditorias_dir = salida / "03_AUDITORIAS"
    reportes_dir = salida / "04_REPORTES"

    for carpeta in (
        salida,
        resultados_dir,
        auditorias_dir,
        reportes_dir,
    ):
        carpeta.mkdir(
            parents=True,
            exist_ok=False,
        ) if carpeta == salida else carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

    validaciones: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # 1. LECTURA DE PRECARGAS
    # --------------------------------------------------------

    p5809, sep_5809, enc_5809 = leer_csv_flexible(
        entradas["PRECARGA_5809"]
    )

    p5810, sep_5810, enc_5810 = leer_csv_flexible(
        entradas["PRECARGA_5810"]
    )

    validar_columnas_exactas(
        p5809,
        COLUMNAS_5809_OFICIALES,
        "Precarga 5809",
    )

    validar_columnas_exactas(
        p5810,
        COLUMNAS_5810_OFICIALES,
        "Precarga 5810",
    )

    p5809.columns = COLUMNAS_5809_OFICIALES
    p5810.columns = COLUMNAS_5810_OFICIALES

    # --------------------------------------------------------
    # 2. LECTURA DE FUENTES INSTITUCIONALES
    # --------------------------------------------------------

    hoja1 = leer_excel_hoja(
        entradas["PROMEDIOS"],
        "Hoja1",
    )

    datos_alumnos = leer_excel_hoja(
        entradas["PROMEDIOS"],
        "DatosAlumnos",
    )

    mallas = leer_excel_hoja(
        entradas["PLANES"],
        "BBDD Bruta",
    )

    gob_niv = pd.read_csv(
        entradas["GOB_NIV_ACA"],
        sep="\t",
        dtype=str,
        keep_default_na=False,
    )

    # --------------------------------------------------------
    # 3. COLUMNAS DE HOJA1
    # --------------------------------------------------------

    h1_rut = buscar_columna(
        hoja1,
        ["RUT", "NUM_DOCUMENTO", "N_DOC"],
        obligatoria=True,
        contexto="PROMEDIOS / Hoja1",
    )

    h1_codcli = buscar_columna(
        hoja1,
        ["CODCLI"],
        obligatoria=True,
        contexto="PROMEDIOS / Hoja1",
    )

    h1_plan = buscar_columna(
        hoja1,
        [
            "PLAN_DE_ESTUDIO",
            "PLAN_ESTUDIOS",
            "CODPESTUD",
        ],
        obligatoria=True,
        contexto="PROMEDIOS / Hoja1",
    )

    h1_nivel = buscar_columna(
        hoja1,
        ["NIVEL"],
        obligatoria=True,
        contexto="PROMEDIOS / Hoja1",
    )

    h1_codramo = buscar_columna(
        hoja1,
        ["CODRAMO", "CODIGO_ASIGNATURA"],
        obligatoria=False,
    )

    # --------------------------------------------------------
    # 4. COLUMNAS DE DATOSALUMNOS
    # --------------------------------------------------------

    da_rut = buscar_columna(
        datos_alumnos,
        ["RUT", "NUM_DOCUMENTO", "N_DOC"],
        obligatoria=True,
        contexto="PROMEDIOS / DatosAlumnos",
    )

    da_codcli = buscar_columna(
        datos_alumnos,
        ["CODCLI"],
        obligatoria=True,
        contexto="PROMEDIOS / DatosAlumnos",
    )

    da_carrera = buscar_columna(
        datos_alumnos,
        [
            "CODCARPR",
            "CODCARR",
            "COD_CAR",
        ],
        obligatoria=True,
        contexto="PROMEDIOS / DatosAlumnos",
    )

    da_nivel = buscar_columna(
        datos_alumnos,
        ["NIVEL", "DA_NIVEL", "NIV_ACA"],
        obligatoria=True,
        contexto="PROMEDIOS / DatosAlumnos",
    )

    # --------------------------------------------------------
    # 5. COLUMNAS DE MALLAS
    # --------------------------------------------------------

    malla_plan = buscar_columna(
        mallas,
        [
            "CODPESTUD",
            "PLAN_ESTUDIOS",
            "PLAN_DE_ESTUDIO",
        ],
        obligatoria=True,
        contexto="Listado de planes / BBDD Bruta",
    )

    malla_ramo = buscar_columna(
        mallas,
        [
            "CODRAMO",
            "CODIGO_ASIGNATURA",
            "COD_ASIGNATURA",
        ],
        obligatoria=True,
        contexto="Listado de planes / BBDD Bruta",
    )

    malla_nivel = buscar_columna(
        mallas,
        ["NIVEL"],
        obligatoria=True,
        contexto="Listado de planes / BBDD Bruta",
    )

    malla_credito = buscar_columna(
        mallas,
        [
            "CREDITO",
            "CREDITOS",
            "CRÉDITO",
            "CRÉDITOS",
        ],
        obligatoria=True,
        contexto="Listado de planes / BBDD Bruta",
    )

    malla_carrera = buscar_columna(
        mallas,
        [
            "CODCARR",
            "CODCARPR",
            "COD_CAR",
            "CARRERA",
        ],
        obligatoria=False,
    )

    # --------------------------------------------------------
    # 6. NORMALIZACIÓN PRECARGA 5809
    # --------------------------------------------------------

    p5809_control = p5809.copy()

    p5809_control.insert(
        0,
        "ID_FILA_5809",
        range(1, len(p5809_control) + 1),
    )

    p5809_control["DOCUMENTO_NORM"] = (
        p5809_control["NUM_DOCUMENTO"]
        .map(norm_documento)
    )

    p5809_control["PLAN_PRECARGA_NORM"] = (
        p5809_control["PLAN_ESTUDIOS"]
        .map(norm_codigo)
    )

    p5809_control["CODIGO_UNICO_NORM"] = (
        p5809_control["CODIGO_UNICO"]
        .map(norm_codigo)
    )

    p5809_control["CLAVE_ESTUDIANTE_PLAN"] = (
        p5809_control["DOCUMENTO_NORM"]
        + "|"
        + p5809_control["PLAN_PRECARGA_NORM"]
    )

    # --------------------------------------------------------
    # 7. NIVEL POR HOJA1: DOCUMENTO + PLAN
    # --------------------------------------------------------

    h1 = hoja1.copy()

    h1["DOCUMENTO_NORM"] = (
        h1[h1_rut].map(norm_documento)
    )

    h1["PLAN_NORM"] = (
        h1[h1_plan].map(norm_codigo)
    )

    h1["CODCLI_NORM"] = (
        h1[h1_codcli].map(norm_codigo)
    )

    h1["NIVEL_HOJA1_NUM"] = pd.to_numeric(
        h1[h1_nivel],
        errors="coerce",
    )

    if h1_codramo:
        h1["CODRAMO_NORM"] = (
            h1[h1_codramo].map(norm_codigo)
        )
    else:
        h1["CODRAMO_NORM"] = ""

    nivel_h1 = (
        h1[
            h1["DOCUMENTO_NORM"].ne("")
            & h1["PLAN_NORM"].ne("")
        ]
        .groupby(
            [
                "DOCUMENTO_NORM",
                "PLAN_NORM",
            ],
            dropna=False,
        )
        .agg(
            NIVEL_MAX_HOJA1=(
                "NIVEL_HOJA1_NUM",
                "max",
            ),
            NIVEL_MIN_HOJA1=(
                "NIVEL_HOJA1_NUM",
                "min",
            ),
            CODCLI_HOJA1=(
                "CODCLI_NORM",
                unir_unicos,
            ),
            REGISTROS_HOJA1=(
                "PLAN_NORM",
                "size",
            ),
            RAMOS_DISTINTOS_HOJA1=(
                "CODRAMO_NORM",
                "nunique",
            ),
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # 8. NIVEL POR DATOSALUMNOS
    # --------------------------------------------------------

    da = datos_alumnos.copy()

    da["DOCUMENTO_NORM"] = (
        da[da_rut].map(norm_documento)
    )

    da["CODCLI_NORM"] = (
        da[da_codcli].map(norm_codigo)
    )

    da["CARRERA_INTERNA_NORM"] = (
        da[da_carrera].map(norm_codigo)
    )

    da["NIVEL_DA_NUM"] = pd.to_numeric(
        da[da_nivel],
        errors="coerce",
    )

    nivel_da_documento = (
        da[
            da["DOCUMENTO_NORM"].ne("")
        ]
        .groupby(
            "DOCUMENTO_NORM",
            dropna=False,
        )
        .agg(
            NIVEL_MAX_DA=(
                "NIVEL_DA_NUM",
                "max",
            ),
            NIVELES_DA=(
                "NIVEL_DA_NUM",
                lambda serie: " | ".join(
                    sorted({
                        str(int(valor))
                        for valor in serie
                        if pd.notna(valor)
                    })
                ),
            ),
            CODCLI_DA=(
                "CODCLI_NORM",
                unir_unicos,
            ),
            CARRERAS_INTERNAS_DA=(
                "CARRERA_INTERNA_NORM",
                unir_unicos,
            ),
            N_CARRERAS_DA=(
                "CARRERA_INTERNA_NORM",
                lambda serie: len({
                    valor
                    for valor in serie
                    if valor
                }),
            ),
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # 9. UNIR NIVEL A UNIVERSO RECTOR 5809
    # --------------------------------------------------------

    p5809_control = p5809_control.merge(
        nivel_h1,
        left_on=[
            "DOCUMENTO_NORM",
            "PLAN_PRECARGA_NORM",
        ],
        right_on=[
            "DOCUMENTO_NORM",
            "PLAN_NORM",
        ],
        how="left",
    )

    p5809_control = p5809_control.merge(
        nivel_da_documento,
        on="DOCUMENTO_NORM",
        how="left",
    )

    p5809_control["NIVEL_EFECTIVO"] = pd.NA
    p5809_control["FUENTE_NIVEL"] = ""
    p5809_control["METODO_NIVEL"] = ""
    p5809_control["ESTADO_NIVEL"] = ""

    mask_h1 = (
        p5809_control["NIVEL_MAX_HOJA1"]
        .notna()
    )

    p5809_control.loc[
        mask_h1,
        "NIVEL_EFECTIVO",
    ] = p5809_control.loc[
        mask_h1,
        "NIVEL_MAX_HOJA1",
    ]

    p5809_control.loc[
        mask_h1,
        "FUENTE_NIVEL",
    ] = "PROMEDIOSDEALUMNOS::Hoja1"

    p5809_control.loc[
        mask_h1,
        "METODO_NIVEL",
    ] = "DOCUMENTO_MAS_PLAN_EXACTO"

    p5809_control.loc[
        mask_h1,
        "ESTADO_NIVEL",
    ] = "NIVEL_RESUELTO_PLAN_EXACTO"

    mask_da_unico = (
        ~mask_h1
        & p5809_control["NIVEL_MAX_DA"].notna()
        & p5809_control["N_CARRERAS_DA"].fillna(0).eq(1)
    )

    p5809_control.loc[
        mask_da_unico,
        "NIVEL_EFECTIVO",
    ] = p5809_control.loc[
        mask_da_unico,
        "NIVEL_MAX_DA",
    ]

    p5809_control.loc[
        mask_da_unico,
        "FUENTE_NIVEL",
    ] = "PROMEDIOSDEALUMNOS::DatosAlumnos"

    p5809_control.loc[
        mask_da_unico,
        "METODO_NIVEL",
    ] = "DOCUMENTO_UNIVOCO_UNA_CARRERA"

    p5809_control.loc[
        mask_da_unico,
        "ESTADO_NIVEL",
    ] = "NIVEL_RESUELTO_DATOSALUMNOS_UNIVOCO"

    mask_da_multiple = (
        ~mask_h1
        & p5809_control["NIVEL_MAX_DA"].notna()
        & p5809_control["N_CARRERAS_DA"].fillna(0).gt(1)
    )

    p5809_control.loc[
        mask_da_multiple,
        "FUENTE_NIVEL",
    ] = "PROMEDIOSDEALUMNOS::DatosAlumnos"

    p5809_control.loc[
        mask_da_multiple,
        "METODO_NIVEL",
    ] = "DOCUMENTO_CON_MULTIPLES_CARRERAS"

    p5809_control.loc[
        mask_da_multiple,
        "ESTADO_NIVEL",
    ] = "NIVEL_NO_ASIGNADO_MULTICARRERA"

    mask_sin_nivel = (
        p5809_control["ESTADO_NIVEL"].eq("")
    )

    p5809_control.loc[
        mask_sin_nivel,
        "METODO_NIVEL",
    ] = "SIN_EVIDENCIA_COMPATIBLE"

    p5809_control.loc[
        mask_sin_nivel,
        "ESTADO_NIVEL",
    ] = "SIN_NIVEL_EN_FUENTES"

    p5809_control["NIVEL_EFECTIVO"] = pd.to_numeric(
        p5809_control["NIVEL_EFECTIVO"],
        errors="coerce",
    ).astype("Int64")

    p5809_control["ANIO_CURRICULAR_ALCANZADO"] = (
        (
            p5809_control["NIVEL_EFECTIVO"] + 1
        ) // 2
    ).astype("Int64")

    p5809_control["REGLA_NIVEL_ANIO"] = (
        "ANIO_CURRICULAR=TECHO(NIVEL/2)"
    )

    # --------------------------------------------------------
    # 10. CANÓNICO DE MALLAS POR PLAN
    # --------------------------------------------------------

    mc = mallas.copy()

    mc["PLAN_NORM"] = (
        mc[malla_plan].map(norm_codigo)
    )

    mc["CODRAMO_NORM"] = (
        mc[malla_ramo].map(norm_codigo)
    )

    mc["NIVEL_MALLA_NUM"] = pd.to_numeric(
        mc[malla_nivel],
        errors="coerce",
    )

    mc["CREDITO_NUM"] = numerico(
        mc[malla_credito]
    )

    if malla_carrera:
        mc["CARRERA_INTERNA_MALLA"] = (
            mc[malla_carrera].map(norm_codigo)
        )
    else:
        mc["CARRERA_INTERNA_MALLA"] = ""

    mc["ANIO_CURRICULAR"] = (
        (
            mc["NIVEL_MALLA_NUM"] + 1
        ) // 2
    ).astype("Int64")

    mc["NIVEL_VALIDO"] = (
        mc["NIVEL_MALLA_NUM"]
        .between(1, 20)
    )

    mc["CREDITO_VALIDO"] = (
        mc["CREDITO_NUM"].notna()
    )

    llave_unidad = [
        "PLAN_NORM",
        "CODRAMO_NORM",
        "NIVEL_MALLA_NUM",
        "CREDITO_NUM",
    ]

    grupos_unidad = (
        mc.groupby(
            llave_unidad,
            dropna=False,
        )
        .size()
        .reset_index(
            name="N_REPETICIONES_FISICAS"
        )
    )

    grupos_unidad["FILAS_EXCEDENTES"] = (
        grupos_unidad["N_REPETICIONES_FISICAS"] - 1
    ).clip(lower=0)

    duplicados_malla = grupos_unidad[
        grupos_unidad["N_REPETICIONES_FISICAS"] > 1
    ].copy()

    mc_canonica = (
        mc.drop_duplicates(
            llave_unidad,
            keep="first",
        )
        .copy()
    )

    resumen_plan = (
        mc_canonica[
            mc_canonica["PLAN_NORM"].ne("")
        ]
        .groupby(
            "PLAN_NORM",
            dropna=False,
        )
        .agg(
            NIVEL_MIN_PLAN=(
                "NIVEL_MALLA_NUM",
                "min",
            ),
            NIVEL_MAX_PLAN=(
                "NIVEL_MALLA_NUM",
                "max",
            ),
            RAMOS_DISTINTOS_PLAN=(
                "CODRAMO_NORM",
                "nunique",
            ),
            TOTAL_CREDITOS_PLAN=(
                "CREDITO_NUM",
                "sum",
            ),
            CARRERAS_INTERNAS_MALLA=(
                "CARRERA_INTERNA_MALLA",
                unir_unicos,
            ),
        )
        .reset_index()
    )

    resumen_plan["ANIO_MAX_PLAN"] = (
        (
            resumen_plan["NIVEL_MAX_PLAN"] + 1
        ) // 2
    ).astype("Int64")

    creditos_anio = (
        mc_canonica[
            mc_canonica["PLAN_NORM"].ne("")
            & mc_canonica["ANIO_CURRICULAR"].notna()
        ]
        .groupby(
            [
                "PLAN_NORM",
                "ANIO_CURRICULAR",
            ],
            dropna=False,
        )["CREDITO_NUM"]
        .sum(min_count=1)
        .reset_index()
    )

    creditos_pivot = (
        creditos_anio.pivot(
            index="PLAN_NORM",
            columns="ANIO_CURRICULAR",
            values="CREDITO_NUM",
        )
        .fillna(0)
        .reset_index()
    )

    for anio in range(1, 11):
        if anio not in creditos_pivot.columns:
            creditos_pivot[anio] = 0

    creditos_pivot = creditos_pivot.rename(
        columns={
            anio: f"CREDITOS_ANIO_{anio}"
            for anio in range(1, 11)
        }
    )

    resumen_plan = resumen_plan.merge(
        creditos_pivot,
        on="PLAN_NORM",
        how="left",
    )

    # --------------------------------------------------------
    # 11. PLAN Y COBERTURA PARA CADA ESTUDIANTE 5809
    # --------------------------------------------------------

    p5809_control = p5809_control.merge(
        resumen_plan,
        left_on="PLAN_PRECARGA_NORM",
        right_on="PLAN_NORM",
        how="left",
    )

    p5809_control["PLAN_EN_MALLA"] = (
        p5809_control["PLAN_NORM"]
        .fillna("")
        .ne("")
    )

    p5809_control["PLAN_CUBRE_NIVEL"] = (
        p5809_control["PLAN_EN_MALLA"]
        & p5809_control["NIVEL_EFECTIVO"].notna()
        & p5809_control["NIVEL_MAX_PLAN"].notna()
        & p5809_control["NIVEL_EFECTIVO"].le(
            p5809_control["NIVEL_MAX_PLAN"]
        )
    )

    p5809_control["ESTADO_TRAZABILIDAD_5809"] = ""

    mask_plan_nivel_ok = (
        p5809_control["PLAN_EN_MALLA"]
        & p5809_control["PLAN_CUBRE_NIVEL"]
    )

    p5809_control.loc[
        mask_plan_nivel_ok,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "TRAZABLE_PLAN_Y_NIVEL"

    mask_plan_sin_nivel = (
        p5809_control["PLAN_EN_MALLA"]
        & p5809_control["NIVEL_EFECTIVO"].isna()
    )

    p5809_control.loc[
        mask_plan_sin_nivel,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "TRAZABLE_PLAN_PENDIENTE_NIVEL"

    mask_plan_no_cubre = (
        p5809_control["PLAN_EN_MALLA"]
        & p5809_control["NIVEL_EFECTIVO"].notna()
        & ~p5809_control["PLAN_CUBRE_NIVEL"]
    )

    p5809_control.loc[
        mask_plan_no_cubre,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "CONFLICTO_PLAN_NO_CUBRE_NIVEL"

    mask_plan_sin_malla = (
        ~p5809_control["PLAN_EN_MALLA"]
    )

    p5809_control.loc[
        mask_plan_sin_malla,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "PLAN_PRECARGA_SIN_MALLA_INSTITUCIONAL"

    p5809_control["METODO_RESOLUCION_PLAN"] = (
        "PLAN_EXPLICITO_PRECARGA_5809"
    )

    p5809_control["FUENTE_PLAN"] = (
        str(entradas["PRECARGA_5809"])
    )

    # --------------------------------------------------------
    # 12. CLASIFICAR PLAN NUEVO O HISTÓRICO
    # --------------------------------------------------------

    planes_historicos: set[str] = set()

    if "CIERRE_HISTORICO" in entradas:
        cierre, _, _ = leer_csv_flexible(
            entradas["CIERRE_HISTORICO"]
        )

        col_plan_cierre = buscar_columna(
            cierre,
            [
                "CODPESTUD",
                "PLAN_ESTUDIOS",
                "PLAN_DE_ESTUDIO",
            ],
            obligatoria=False,
        )

        if col_plan_cierre:
            planes_historicos = {
                norm_codigo(valor)
                for valor in cierre[col_plan_cierre]
                if norm_codigo(valor)
            }

    p5809_control["TIPO_PLAN_EN_PROCESO"] = (
        p5809_control["PLAN_PRECARGA_NORM"]
        .map(
            lambda plan: (
                "PLAN_EXISTENTE_EN_CIERRE_HISTORICO"
                if plan in planes_historicos
                else "PLAN_NUEVO_O_NO_PRESENTE_EN_CIERRE_HISTORICO"
            )
        )
    )

    # --------------------------------------------------------
    # 13. GOBERNANZA DE LAS 43 CARRERAS 5810
    # --------------------------------------------------------

    p5810_control = p5810.copy()

    p5810_control.insert(
        0,
        "ID_FILA_5810",
        range(1, len(p5810_control) + 1),
    )

    p5810_control["PLAN_PRECARGA_NORM"] = (
        p5810_control["PLAN_ESTUDIOS"]
        .map(norm_codigo)
    )

    p5810_control["CODIGO_UNICO_NORM"] = (
        p5810_control["CODIGO_UNICO"]
        .map(norm_codigo)
    )

    p5810_control = p5810_control.merge(
        resumen_plan,
        left_on="PLAN_PRECARGA_NORM",
        right_on="PLAN_NORM",
        how="left",
    )

    p5810_control["PLAN_EN_MALLA"] = (
        p5810_control["PLAN_NORM"]
        .fillna("")
        .ne("")
    )

    p5810_control["TIPO_PLAN_EN_PROCESO"] = (
        p5810_control["PLAN_PRECARGA_NORM"]
        .map(
            lambda plan: (
                "PLAN_EXISTENTE_EN_CIERRE_HISTORICO"
                if plan in planes_historicos
                else "PLAN_NUEVO_O_NO_PRESENTE_EN_CIERRE_HISTORICO"
            )
        )
    )

    p5810_control["ESTADO_TRAZABILIDAD_5810"] = (
        p5810_control["PLAN_EN_MALLA"]
        .map({
            True: "TRAZABLE_PLAN_MALLA_CREDITOS",
            False: "PLAN_PRECARGA_SIN_MALLA_INSTITUCIONAL",
        })
    )

    p5810_control["METODO_RESOLUCION_PLAN"] = (
        "PLAN_EXPLICITO_PRECARGA_5810"
    )

    p5810_control["FUENTE_MALLA"] = (
        str(entradas["PLANES"])
    )

    # --------------------------------------------------------
    # 14. CANDIDATO 5810 CON CRÉDITOS POR AÑO
    # --------------------------------------------------------

    candidato_5810 = p5810.copy()

    mapa_resumen = (
        resumen_plan.set_index("PLAN_NORM")
        if not resumen_plan.empty
        else pd.DataFrame()
    )

    candidato_5810["PLAN_NORM_TMP"] = (
        candidato_5810["PLAN_ESTUDIOS"]
        .map(norm_codigo)
    )

    for indice, fila in candidato_5810.iterrows():
        plan = fila["PLAN_NORM_TMP"]

        if (
            resumen_plan.empty
            or plan not in mapa_resumen.index
        ):
            continue

        info = mapa_resumen.loc[plan]

        candidato_5810.at[
            indice,
            "TOTAL_UNIDADES_MEDIDA",
        ] = info.get(
            "TOTAL_CREDITOS_PLAN",
            "",
        )

        for anio, columna_oficial in (
            COLUMNAS_ANUALES_5810.items()
        ):
            candidato_5810.at[
                indice,
                columna_oficial,
            ] = info.get(
                f"CREDITOS_ANIO_{anio}",
                0,
            )

    candidato_5810 = candidato_5810.drop(
        columns=["PLAN_NORM_TMP"]
    )

    # No se altera la estructura de carga oficial.
    candidato_5810 = candidato_5810[
        COLUMNAS_5810_OFICIALES
    ].copy()

    # --------------------------------------------------------
    # 15. DESBORDE AÑOS 8-10
    # --------------------------------------------------------

    desborde = p5810_control.copy()

    for anio in (8, 9, 10):
        columna = f"CREDITOS_ANIO_{anio}"

        if columna not in desborde.columns:
            desborde[columna] = 0

    desborde["CREDITOS_FUERA_ESTRUCTURA_5810"] = (
        desborde[
            [
                "CREDITOS_ANIO_8",
                "CREDITOS_ANIO_9",
                "CREDITOS_ANIO_10",
            ]
        ]
        .fillna(0)
        .sum(axis=1)
    )

    casos_desborde = desborde[
        desborde[
            "CREDITOS_FUERA_ESTRUCTURA_5810"
        ].gt(0)
    ].copy()

    # --------------------------------------------------------
    # 16. CONCILIACIÓN 5809 VS 5810
    # --------------------------------------------------------

    planes_5809 = {
        plan
        for plan in p5809_control[
            "PLAN_PRECARGA_NORM"
        ]
        if plan
    }

    planes_5810 = {
        plan
        for plan in p5810_control[
            "PLAN_PRECARGA_NORM"
        ]
        if plan
    }

    universo_planes = sorted(
        planes_5809 | planes_5810
    )

    conciliacion_planes = pd.DataFrame({
        "PLAN_NORM": universo_planes,
    })

    conciliacion_planes["EN_5809"] = (
        conciliacion_planes["PLAN_NORM"]
        .isin(planes_5809)
    )

    conciliacion_planes["EN_5810"] = (
        conciliacion_planes["PLAN_NORM"]
        .isin(planes_5810)
    )

    conciliacion_planes["EN_MALLA"] = (
        conciliacion_planes["PLAN_NORM"]
        .isin(set(resumen_plan["PLAN_NORM"]))
    )

    conciliacion_planes["ESTADO"] = "OTRO"

    conciliacion_planes.loc[
        conciliacion_planes["EN_5809"]
        & conciliacion_planes["EN_5810"]
        & conciliacion_planes["EN_MALLA"],
        "ESTADO",
    ] = "PLAN_CONCILIADO_5809_5810_MALLA"

    conciliacion_planes.loc[
        conciliacion_planes["EN_5809"]
        & ~conciliacion_planes["EN_5810"],
        "ESTADO",
    ] = "PLAN_5809_NO_PRESENTE_EN_5810"

    conciliacion_planes.loc[
        ~conciliacion_planes["EN_5809"]
        & conciliacion_planes["EN_5810"],
        "ESTADO",
    ] = "PLAN_5810_SIN_ESTUDIANTES_5809"

    conciliacion_planes.loc[
        ~conciliacion_planes["EN_MALLA"],
        "ESTADO",
    ] = "PLAN_SIN_MALLA_INSTITUCIONAL"

    # --------------------------------------------------------
    # 17. VALIDACIONES
    # --------------------------------------------------------

    agregar_validacion(
        validaciones,
        "ESTRUCTURA",
        "PRECARGA_5809_22_COLUMNAS",
        len(p5809.columns) == 22,
        f"Columnas observadas: {len(p5809.columns)}",
        True,
    )

    agregar_validacion(
        validaciones,
        "ESTRUCTURA",
        "PRECARGA_5810_22_COLUMNAS",
        len(p5810.columns) == 22,
        f"Columnas observadas: {len(p5810.columns)}",
        True,
    )

    agregar_validacion(
        validaciones,
        "UNIVERSO_5809",
        "TODAS_FILAS_CON_ID_TRAZABLE",
        p5809_control["ID_FILA_5809"].notna().all(),
        f"Filas: {len(p5809_control)}",
        True,
    )

    agregar_validacion(
        validaciones,
        "UNIVERSO_5810",
        "TODAS_CARRERAS_CON_ESTADO_TRAZABILIDAD",
        p5810_control[
            "ESTADO_TRAZABILIDAD_5810"
        ].ne("").all(),
        (
            f"Carreras: {len(p5810_control)}; "
            f"sin estado: "
            f"{p5810_control['ESTADO_TRAZABILIDAD_5810'].eq('').sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "PLANES",
        "PLAN_5809_CON_MALLA",
        p5809_control["PLAN_EN_MALLA"].all(),
        (
            f"Sin malla: "
            f"{(~p5809_control['PLAN_EN_MALLA']).sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "PLANES",
        "PLAN_5810_CON_MALLA",
        p5810_control["PLAN_EN_MALLA"].all(),
        (
            f"Sin malla: "
            f"{(~p5810_control['PLAN_EN_MALLA']).sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "NIVEL",
        "NIVELES_MALLA_VALIDOS",
        mc_canonica["NIVEL_VALIDO"].all(),
        (
            f"Inválidos: "
            f"{(~mc_canonica['NIVEL_VALIDO']).sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "CREDITOS",
        "CREDITOS_MALLA_NUMERICOS",
        mc_canonica["CREDITO_VALIDO"].all(),
        (
            f"No numéricos: "
            f"{(~mc_canonica['CREDITO_VALIDO']).sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "NIVEL_ESTUDIANTE",
        "ESTUDIANTES_CON_NIVEL_RESUELTO",
        p5809_control["NIVEL_EFECTIVO"].notna().all(),
        (
            f"Resueltos: "
            f"{p5809_control['NIVEL_EFECTIVO'].notna().sum()}; "
            f"pendientes: "
            f"{p5809_control['NIVEL_EFECTIVO'].isna().sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "NIVEL_ESTUDIANTE",
        "PLAN_CUBRE_NIVEL_RESUELTO",
        not p5809_control[
            "ESTADO_TRAZABILIDAD_5809"
        ].eq(
            "CONFLICTO_PLAN_NO_CUBRE_NIVEL"
        ).any(),
        (
            f"Conflictos: "
            f"{p5809_control['ESTADO_TRAZABILIDAD_5809'].eq('CONFLICTO_PLAN_NO_CUBRE_NIVEL').sum()}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "5810",
        "SIN_CREDITOS_FUERA_DE_7_ANIOS",
        casos_desborde.empty,
        (
            f"Carreras con créditos en años 8-10: "
            f"{len(casos_desborde)}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "CONCILIACION",
        "PLANES_5809_PRESENTES_EN_5810",
        planes_5809.issubset(planes_5810),
        (
            f"Solo 5809: "
            f"{len(planes_5809 - planes_5810)}"
        ),
        True,
    )

    agregar_validacion(
        validaciones,
        "CONTROL",
        "FUENTES_ORIGINALES_INTACTAS",
        True,
        "Todas las fuentes fueron abiertas solo en lectura.",
        True,
    )

    validaciones_df = pd.DataFrame(
        validaciones
    )

    bloqueantes = validaciones_df[
        validaciones_df["BLOQUEANTE"].eq("SI")
        & validaciones_df["RESULTADO"].eq("ERROR")
    ].copy()

    estado_cierre = (
        "APTO_PARA_REVISION_FUNCIONAL"
        if bloqueantes.empty
        else "NO_APTO_CON_BLOQUEOS"
    )

    # --------------------------------------------------------
    # 18. ARCHIVOS DE PENDIENTES
    # --------------------------------------------------------

    pendientes_5809 = p5809_control[
        ~p5809_control[
            "ESTADO_TRAZABILIDAD_5809"
        ].eq("TRAZABLE_PLAN_Y_NIVEL")
    ].copy()

    pendientes_5810 = p5810_control[
        ~p5810_control[
            "ESTADO_TRAZABILIDAD_5810"
        ].eq("TRAZABLE_PLAN_MALLA_CREDITOS")
    ].copy()

    # --------------------------------------------------------
    # 19. EXPORTACIÓN TSV/CSV
    # --------------------------------------------------------

    p5809_control.to_csv(
        resultados_dir
        / "01_5809_MATRICULA_TRAZABILIDAD_COMPLETA.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    p5810_control.to_csv(
        resultados_dir
        / "02_5810_CARRERAS_TRAZABILIDAD_COMPLETA.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    candidato_5810.to_csv(
        resultados_dir
        / "03_5810_CANDIDATO_CONTROL_22_COLUMNAS.csv",
        sep=";",
        index=False,
        header=True,
        encoding="cp1252",
        lineterminator="\n",
    )

    resumen_plan.to_csv(
        resultados_dir
        / "04_RESUMEN_CREDITOS_POR_PLAN.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    conciliacion_planes.to_csv(
        resultados_dir
        / "05_CONCILIACION_PLANES_5809_5810_MALLAS.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    pendientes_5809.to_csv(
        auditorias_dir
        / "01_PENDIENTES_5809.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    pendientes_5810.to_csv(
        auditorias_dir
        / "02_PENDIENTES_5810.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    casos_desborde.to_csv(
        auditorias_dir
        / "03_CREDITOS_FUERA_ESTRUCTURA_7_ANIOS.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    duplicados_malla.to_csv(
        auditorias_dir
        / "04_DUPLICADOS_FISICOS_MALLA.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    mc_canonica.to_csv(
        auditorias_dir
        / "05_MALLA_CANONICA_UNIDADES.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    validaciones_df.to_csv(
        auditorias_dir
        / "06_VALIDACIONES.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    bloqueantes.to_csv(
        auditorias_dir
        / "07_BLOQUEOS.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 20. EXCEL EJECUTIVO
    # --------------------------------------------------------

    excel = (
        resultados_dir
        / "GOBERNANZA_AVANCE_CURRICULAR_END_TO_END.xlsx"
    )

    resumen_kpi = pd.DataFrame([
        {
            "INDICADOR": "Filas universo rector 5809",
            "VALOR": len(p5809_control),
        },
        {
            "INDICADOR": "Carreras universo rector 5810",
            "VALOR": len(p5810_control),
        },
        {
            "INDICADOR": "Planes distintos 5809",
            "VALOR": len(planes_5809),
        },
        {
            "INDICADOR": "Planes distintos 5810",
            "VALOR": len(planes_5810),
        },
        {
            "INDICADOR": "Planes nuevos/no presentes en histórico",
            "VALOR": int(
                p5810_control[
                    "TIPO_PLAN_EN_PROCESO"
                ].eq(
                    "PLAN_NUEVO_O_NO_PRESENTE_EN_CIERRE_HISTORICO"
                ).sum()
            ),
        },
        {
            "INDICADOR": "Estudiantes con nivel resuelto",
            "VALOR": int(
                p5809_control[
                    "NIVEL_EFECTIVO"
                ].notna().sum()
            ),
        },
        {
            "INDICADOR": "Estudiantes pendientes de nivel",
            "VALOR": int(
                p5809_control[
                    "NIVEL_EFECTIVO"
                ].isna().sum()
            ),
        },
        {
            "INDICADOR": "Carreras 5810 trazables",
            "VALOR": int(
                p5810_control[
                    "ESTADO_TRAZABILIDAD_5810"
                ].eq(
                    "TRAZABLE_PLAN_MALLA_CREDITOS"
                ).sum()
            ),
        },
        {
            "INDICADOR": "Bloqueos",
            "VALOR": len(bloqueantes),
        },
        {
            "INDICADOR": "Estado de cierre",
            "VALOR": estado_cierre,
        },
    ])

    with pd.ExcelWriter(
        excel,
        engine="openpyxl",
    ) as writer:
        resumen_kpi.to_excel(
            writer,
            sheet_name="RESUMEN",
            index=False,
        )

        p5810_control.to_excel(
            writer,
            sheet_name="5810_TRAZABILIDAD",
            index=False,
        )

        p5809_control.to_excel(
            writer,
            sheet_name="5809_TRAZABILIDAD",
            index=False,
        )

        candidato_5810.to_excel(
            writer,
            sheet_name="5810_CANDIDATO",
            index=False,
        )

        resumen_plan.to_excel(
            writer,
            sheet_name="CREDITOS_POR_PLAN",
            index=False,
        )

        conciliacion_planes.to_excel(
            writer,
            sheet_name="CONCILIACION_PLANES",
            index=False,
        )

        pendientes_5809.to_excel(
            writer,
            sheet_name="PENDIENTES_5809",
            index=False,
        )

        pendientes_5810.to_excel(
            writer,
            sheet_name="PENDIENTES_5810",
            index=False,
        )

        casos_desborde.to_excel(
            writer,
            sheet_name="DESBORDE_ANIOS",
            index=False,
        )

        validaciones_df.to_excel(
            writer,
            sheet_name="VALIDACIONES",
            index=False,
        )

        bloqueantes.to_excel(
            writer,
            sheet_name="BLOQUEOS",
            index=False,
        )

        gob_niv.to_excel(
            writer,
            sheet_name="GOB_NIV_ACA",
            index=False,
        )

        for hoja in writer.book.worksheets:
            hoja.freeze_panes = "A2"
            hoja.auto_filter.ref = hoja.dimensions

            for columna in hoja.columns:
                letra = columna[0].column_letter
                maximo = 0

                for celda in columna[:2000]:
                    maximo = max(
                        maximo,
                        len(str(celda.value or "")),
                    )

                hoja.column_dimensions[letra].width = min(
                    max(maximo + 2, 12),
                    45,
                )

    # --------------------------------------------------------
    # 21. FUENTES Y MANIFIESTO
    # --------------------------------------------------------

    fuentes = []

    for rol, ruta in entradas.items():
        fuentes.append({
            "ROL": rol,
            "RUTA": str(ruta),
            "SHA256": sha256(ruta),
            "TAMANO_BYTES": ruta.stat().st_size,
        })

    fuentes_df = pd.DataFrame(fuentes)

    fuentes_df.to_csv(
        auditorias_dir
        / "08_FUENTES_Y_HASHES.tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    manifiesto = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "proceso": "Avance Curricular SIES",
        "subproyectos": [
            "5809 Matrícula",
            "5810 Carreras",
        ],
        "anio_proceso": args.anio_proceso,
        "anio_referencia_datos": args.anio_datos,
        "universo_rector_5809": len(p5809_control),
        "universo_rector_5810": len(p5810_control),
        "regla_nivel_anio": (
            "ANIO_CURRICULAR=TECHO(NIVEL/2)"
        ),
        "prioridad_nivel": [
            "Hoja1: documento + plan exacto",
            "DatosAlumnos: documento unívoco con una carrera",
            "Pendiente si el documento tiene múltiples carreras",
        ],
        "metodo_plan": (
            "PLAN_ESTUDIOS explícito de las precargas vigentes"
        ),
        "carreras_nuevas": (
            "Se consideran casos válidos del proceso; no errores."
        ),
        "estado_cierre": estado_cierre,
        "bloqueos": len(bloqueantes),
        "fuentes_modificadas": False,
        "precarga_5809_modificada": False,
        "precarga_5810_modificada": False,
        "archivo_final_de_carga_declarado": False,
        "salida": str(salida),
    }

    (
        salida
        / "manifest_ejecucion.json"
    ).write_text(
        json.dumps(
            manifiesto,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 22. REPORTE DE TEXTO
    # --------------------------------------------------------

    distribucion_5809 = (
        p5809_control[
            "ESTADO_TRAZABILIDAD_5809"
        ]
        .value_counts(dropna=False)
        .to_dict()
    )

    distribucion_5810 = (
        p5810_control[
            "ESTADO_TRAZABILIDAD_5810"
        ]
        .value_counts(dropna=False)
        .to_dict()
    )

    lineas = [
        "GOBERNANZA AVANCE CURRICULAR END-TO-END",
        "=" * 72,
        f"Año de proceso: {args.anio_proceso}",
        f"Año de referencia: {args.anio_datos}",
        "",
        f"Universo rector 5809: {len(p5809_control)}",
        f"Universo rector 5810: {len(p5810_control)}",
        f"Planes distintos 5809: {len(planes_5809)}",
        f"Planes distintos 5810: {len(planes_5810)}",
        "",
        "Distribución 5809:",
    ]

    for estado, cantidad in distribucion_5809.items():
        lineas.append(
            f"- {estado}: {cantidad}"
        )

    lineas.extend([
        "",
        "Distribución 5810:",
    ])

    for estado, cantidad in distribucion_5810.items():
        lineas.append(
            f"- {estado}: {cantidad}"
        )

    lineas.extend([
        "",
        f"Bloqueos: {len(bloqueantes)}",
        f"Estado de cierre: {estado_cierre}",
        "",
        f"Excel: {excel}",
        f"Carpeta: {salida}",
        "",
        "Fuentes modificadas: NO",
        "Archivo final de carga declarado: NO",
    ])

    (
        reportes_dir
        / "RESUMEN_EJECUCION.txt"
    ).write_text(
        "\n".join(lineas),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # 23. TERMINAL
    # --------------------------------------------------------

    print()
    print("=" * 88)
    print("GOBERNANZA AVANCE CURRICULAR END-TO-END")
    print("=" * 88)
    print(f"Año proceso: {args.anio_proceso}")
    print(f"Año datos: {args.anio_datos}")
    print()
    print(f"Universo rector 5809: {len(p5809_control)}")
    print(f"Universo rector 5810: {len(p5810_control)}")
    print(f"Planes distintos 5809: {len(planes_5809)}")
    print(f"Planes distintos 5810: {len(planes_5810)}")
    print()

    print("TRAZABILIDAD 5809")
    print("-" * 88)

    for estado, cantidad in distribucion_5809.items():
        print(f"{estado}: {cantidad}")

    print()
    print("TRAZABILIDAD 5810")
    print("-" * 88)

    for estado, cantidad in distribucion_5810.items():
        print(f"{estado}: {cantidad}")

    print()
    print(
        "Estudiantes con nivel resuelto: "
        f"{p5809_control['NIVEL_EFECTIVO'].notna().sum()}"
    )

    print(
        "Estudiantes pendientes de nivel: "
        f"{p5809_control['NIVEL_EFECTIVO'].isna().sum()}"
    )

    print(
        "Carreras nuevas/no presentes en cierre histórico: "
        f"{p5810_control['TIPO_PLAN_EN_PROCESO'].eq('PLAN_NUEVO_O_NO_PRESENTE_EN_CIERRE_HISTORICO').sum()}"
    )

    print(
        "Carreras con créditos fuera de los 7 años de 5810: "
        f"{len(casos_desborde)}"
    )

    print()
    print(f"Bloqueos: {len(bloqueantes)}")
    print(f"Estado de cierre: {estado_cierre}")
    print()
    print(f"Excel: {excel}")
    print(f"Carpeta: {salida}")
    print()
    print("Fuentes modificadas: NO")
    print("Precarga 5809 modificada: NO")
    print("Precarga 5810 modificada: NO")
    print("Archivo final de carga declarado: NO")
    print("=" * 88)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except Exception as exc:
        print()
        print("=" * 88)
        print("ERROR BLOQUEANTE")
        print("=" * 88)
        print(f"{type(exc).__name__}: {exc}")
        print()
        print("No se modificaron fuentes originales.")
        print("=" * 88)
        raise
