#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


COLUMNAS_5809 = [
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

COLUMNAS_5810 = [
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

COLUMNAS_ANUALES = {
    1: "UNIDADES_1ER_ANIO",
    2: "UNIDADES_2DO_ANIO",
    3: "UNIDADES_3ER_ANIO",
    4: "UNIDADES_4TO_ANIO",
    5: "UNIDADES_5TO_ANIO",
    6: "UNIDADES_6TO_ANIO",
    7: "UNIDADES_7MO_ANIO",
}


def norm_col(valor: Any) -> str:
    texto = "" if valor is None else str(valor)
    texto = texto.strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"[^A-Z0-9]+", "_", texto).strip("_")


def norm_codigo(valor: Any) -> str:
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"\s+", "", texto)


def norm_documento(valor: Any) -> str:
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"[^0-9K]", "", texto)


def numerico(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(
        serie.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )


def buscar_columna(
    df: pd.DataFrame,
    opciones: list[str],
    obligatoria: bool = False,
    contexto: str = "",
) -> str | None:
    mapa = {
        norm_col(c): c
        for c in df.columns
    }

    for opcion in opciones:
        clave = norm_col(opcion)

        if clave in mapa:
            return mapa[clave]

    if obligatoria:
        raise RuntimeError(
            f"No se encontró columna para {contexto}: {opciones}. "
            f"Disponibles: {list(df.columns)}"
        )

    return None


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def leer_csv_flexible(
    ruta: Path,
) -> tuple[pd.DataFrame, str, str]:
    muestra = ruta.read_bytes()[:50000]
    texto = None
    encoding_inicial = None

    for encoding in (
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            texto = muestra.decode(encoding)
            encoding_inicial = encoding
            break
        except UnicodeDecodeError:
            continue

    if texto is None or encoding_inicial is None:
        raise RuntimeError(f"No se pudo decodificar: {ruta}")

    primera = texto.splitlines()[0]

    conteos = {
        ";": primera.count(";"),
        "\t": primera.count("\t"),
        ",": primera.count(","),
        "|": primera.count("|"),
    }

    sep = max(conteos, key=conteos.get)

    if conteos[sep] == 0:
        raise RuntimeError(
            f"No se pudo detectar separador: {ruta}"
        )

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
                sep=sep,
                encoding=encoding,
                dtype=str,
                keep_default_na=False,
            )
            return df, sep, encoding

        except Exception as exc:
            ultimo_error = exc

    raise RuntimeError(
        f"No se pudo leer {ruta}: {ultimo_error}"
    )


def validar_columnas(
    df: pd.DataFrame,
    esperadas: list[str],
    nombre: str,
) -> None:
    observadas = [
        norm_col(c)
        for c in df.columns
    ]

    esperadas_norm = [
        norm_col(c)
        for c in esperadas
    ]

    if observadas != esperadas_norm:
        raise RuntimeError(
            f"Estructura inesperada en {nombre}.\n"
            f"Esperadas: {esperadas_norm}\n"
            f"Observadas: {observadas}"
        )


def unir_unicos(serie: pd.Series) -> str:
    return " | ".join(
        sorted({
            norm_codigo(v)
            for v in serie
            if norm_codigo(v)
        })
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--anio-proceso", type=int, required=True)
    parser.add_argument("--anio-datos", type=int, required=True)
    parser.add_argument("--precarga-5809", type=Path, required=True)
    parser.add_argument("--precarga-5810", type=Path, required=True)
    parser.add_argument("--promedios", type=Path, required=True)
    parser.add_argument("--planes", type=Path, required=True)
    parser.add_argument("--cierre-43", type=Path, required=True)
    parser.add_argument("--gob-niv-aca", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    entradas = {
        "PRECARGA_5809": args.precarga_5809.resolve(),
        "PRECARGA_5810": args.precarga_5810.resolve(),
        "PROMEDIOS": args.promedios.resolve(),
        "PLANES": args.planes.resolve(),
        "CIERRE_43": args.cierre_43.resolve(),
        "GOB_NIV_ACA": args.gob_niv_aca.resolve(),
    }

    for nombre, ruta in entradas.items():
        if not ruta.exists():
            raise RuntimeError(
                f"No existe {nombre}: {ruta}"
            )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    salida = (
        args.output_root.resolve()
        / f"GOBERNANZA_AVANCE_CURRICULAR_V2_{args.anio_proceso}_{timestamp}"
    )

    resultados = salida / "02_RESULTADOS"
    auditorias = salida / "03_AUDITORIAS"
    reportes = salida / "04_REPORTES"

    for carpeta in (
        resultados,
        auditorias,
        reportes,
    ):
        carpeta.mkdir(parents=True, exist_ok=True)

    # ========================================================
    # 1. PRECARGAS RECTORAS
    # ========================================================

    p5809, sep5809, enc5809 = leer_csv_flexible(
        entradas["PRECARGA_5809"]
    )

    p5810, sep5810, enc5810 = leer_csv_flexible(
        entradas["PRECARGA_5810"]
    )

    validar_columnas(p5809, COLUMNAS_5809, "5809")
    validar_columnas(p5810, COLUMNAS_5810, "5810")

    p5809.columns = COLUMNAS_5809
    p5810.columns = COLUMNAS_5810

    p5809.insert(
        0,
        "ID_FILA_5809",
        range(1, len(p5809) + 1),
    )

    p5810.insert(
        0,
        "ID_FILA_5810",
        range(1, len(p5810) + 1),
    )

    for df in (p5809, p5810):
        df["CODIGO_UNICO_NORM"] = (
            df["CODIGO_UNICO"].map(norm_codigo)
        )

        df["PLAN_ESTUDIOS_NORM"] = (
            df["PLAN_ESTUDIOS"].map(norm_codigo)
        )

        df["CLAVE_OFERTA_PLAN"] = (
            df["CODIGO_UNICO_NORM"]
            + "|"
            + df["PLAN_ESTUDIOS_NORM"]
        )

    p5809["DOCUMENTO_NORM"] = (
        p5809["NUM_DOCUMENTO"].map(norm_documento)
    )

    # ========================================================
    # 2. MAPA GOBERNADO 43 CARRERAS → CODPESTUD
    # ========================================================

    cierre = pd.read_csv(
        entradas["CIERRE_43"],
        sep="\t",
        dtype=str,
        keep_default_na=False,
    )

    c_codigo = buscar_columna(
        cierre,
        [
            "CODIGO_UNICO",
            "CODIGO_UNICO_NORM",
            "CODIGO_SIES",
            "CODIGO_CARRERA_SIES",
        ],
        obligatoria=True,
        contexto="CODIGO_UNICO en cierre 43",
    )

    c_plan_version = buscar_columna(
        cierre,
        [
            "PLAN_ESTUDIOS",
            "PLAN_ESTUDIOS_NORM",
            "VERSION_PLAN",
            "NUMERO_PLAN",
        ],
        obligatoria=False,
    )

    c_codpestud = buscar_columna(
        cierre,
        [
            "CODPESTUD",
            "CODPESTUD_NORM",
            "PLAN_DE_ESTUDIO",
            "PLAN_INSTITUCIONAL",
            "CODIGO_PLAN_INSTITUCIONAL",
        ],
        obligatoria=True,
        contexto="CODPESTUD en cierre 43",
    )

    mapa = cierre.copy()

    mapa["CODIGO_UNICO_NORM"] = (
        mapa[c_codigo].map(norm_codigo)
    )

    if c_plan_version:
        mapa["PLAN_ESTUDIOS_NORM"] = (
            mapa[c_plan_version].map(norm_codigo)
        )
    else:
        mapa["PLAN_ESTUDIOS_NORM"] = ""

    mapa["CODPESTUD_RESUELTO"] = (
        mapa[c_codpestud].map(norm_codigo)
    )

    mapa = mapa[
        mapa["CODIGO_UNICO_NORM"].ne("")
        & mapa["CODPESTUD_RESUELTO"].ne("")
    ].copy()

    mapa_por_codigo = (
        mapa.groupby(
            "CODIGO_UNICO_NORM",
            dropna=False,
        )
        .agg(
            N_CODPESTUD=(
                "CODPESTUD_RESUELTO",
                "nunique",
            ),
            CODPESTUD_UNICOS=(
                "CODPESTUD_RESUELTO",
                unir_unicos,
            ),
            N_VERSIONES_PRECARGA=(
                "PLAN_ESTUDIOS_NORM",
                "nunique",
            ),
        )
        .reset_index()
    )

    mapa_exacto = pd.DataFrame()

    if c_plan_version:
        mapa_exacto = (
            mapa[
                mapa["PLAN_ESTUDIOS_NORM"].ne("")
            ][
                [
                    "CODIGO_UNICO_NORM",
                    "PLAN_ESTUDIOS_NORM",
                    "CODPESTUD_RESUELTO",
                ]
            ]
            .drop_duplicates()
        )

        ambig_exacto = (
            mapa_exacto.groupby(
                [
                    "CODIGO_UNICO_NORM",
                    "PLAN_ESTUDIOS_NORM",
                ]
            )["CODPESTUD_RESUELTO"]
            .nunique()
            .reset_index(name="N_CODPESTUD")
        )

        ambig_exacto = ambig_exacto[
            ambig_exacto["N_CODPESTUD"] > 1
        ]

        if not ambig_exacto.empty:
            raise RuntimeError(
                "El cierre 43 contiene claves "
                "CODIGO_UNICO+PLAN_ESTUDIOS con más de un CODPESTUD."
            )

    # ========================================================
    # 3. ASIGNAR CODPESTUD A 5810 Y 5809
    # ========================================================

    def asignar_codpestud(
        universo: pd.DataFrame,
    ) -> pd.DataFrame:
        resultado = universo.copy()

        resultado["CODPESTUD_RESUELTO"] = ""
        resultado["METODO_RESOLUCION_CODPESTUD"] = ""
        resultado["ESTADO_MAPEO_CODPESTUD"] = ""

        if not mapa_exacto.empty:
            resultado = resultado.merge(
                mapa_exacto,
                on=[
                    "CODIGO_UNICO_NORM",
                    "PLAN_ESTUDIOS_NORM",
                ],
                how="left",
                suffixes=("", "_EXACTO"),
                validate="many_to_one",
            )

            resultado["CODPESTUD_RESUELTO"] = (
                resultado["CODPESTUD_RESUELTO_EXACTO"]
                .fillna("")
                .map(norm_codigo)
            )

            resultado = resultado.drop(
                columns=["CODPESTUD_RESUELTO_EXACTO"]
            )

            mask = resultado[
                "CODPESTUD_RESUELTO"
            ].ne("")

            resultado.loc[
                mask,
                "METODO_RESOLUCION_CODPESTUD",
            ] = "CIERRE_43_CODIGO_UNICO_MAS_PLAN"

            resultado.loc[
                mask,
                "ESTADO_MAPEO_CODPESTUD",
            ] = "RESUELTO_EXACTO"

        mapa_unico_codigo = mapa_por_codigo[
            mapa_por_codigo["N_CODPESTUD"].eq(1)
        ][
            [
                "CODIGO_UNICO_NORM",
                "CODPESTUD_UNICOS",
            ]
        ].rename(
            columns={
                "CODPESTUD_UNICOS": "CODPESTUD_POR_CODIGO",
            }
        )

        resultado = resultado.merge(
            mapa_unico_codigo,
            on="CODIGO_UNICO_NORM",
            how="left",
            validate="many_to_one",
        )

        mask_fallback = (
            resultado["CODPESTUD_RESUELTO"].eq("")
            & resultado["CODPESTUD_POR_CODIGO"]
            .fillna("")
            .ne("")
        )

        resultado.loc[
            mask_fallback,
            "CODPESTUD_RESUELTO",
        ] = resultado.loc[
            mask_fallback,
            "CODPESTUD_POR_CODIGO",
        ]

        resultado.loc[
            mask_fallback,
            "METODO_RESOLUCION_CODPESTUD",
        ] = "CIERRE_43_CODIGO_UNICO_UNIVOCO"

        resultado.loc[
            mask_fallback,
            "ESTADO_MAPEO_CODPESTUD",
        ] = "RESUELTO_CODIGO_UNIVOCO"

        resultado = resultado.drop(
            columns=["CODPESTUD_POR_CODIGO"]
        )

        codigos_ambiguos = set(
            mapa_por_codigo.loc[
                mapa_por_codigo["N_CODPESTUD"].gt(1),
                "CODIGO_UNICO_NORM",
            ]
        )

        mask_ambiguo = (
            resultado["CODPESTUD_RESUELTO"].eq("")
            & resultado["CODIGO_UNICO_NORM"].isin(
                codigos_ambiguos
            )
        )

        resultado.loc[
            mask_ambiguo,
            "ESTADO_MAPEO_CODPESTUD",
        ] = "CODIGO_UNICO_CON_MULTIPLES_CODPESTUD"

        mask_sin_mapa = (
            resultado["ESTADO_MAPEO_CODPESTUD"].eq("")
        )

        resultado.loc[
            mask_sin_mapa,
            "ESTADO_MAPEO_CODPESTUD",
        ] = "SIN_MAPEO_EN_CIERRE_43"

        resultado.loc[
            mask_sin_mapa,
            "METODO_RESOLUCION_CODPESTUD",
        ] = "PENDIENTE"

        return resultado

    p5810 = asignar_codpestud(p5810)
    p5809 = asignar_codpestud(p5809)

    # Complementar 5809 desde 5810, porque ambas precargas
    # comparten CODIGO_UNICO + PLAN_ESTUDIOS.
    mapa_5810 = (
        p5810[
            p5810["CODPESTUD_RESUELTO"].ne("")
        ][
            [
                "CLAVE_OFERTA_PLAN",
                "CODPESTUD_RESUELTO",
            ]
        ]
        .drop_duplicates()
    )

    validacion_mapa_5810 = (
        mapa_5810.groupby(
            "CLAVE_OFERTA_PLAN"
        )["CODPESTUD_RESUELTO"]
        .nunique()
        .reset_index(name="N")
    )

    if validacion_mapa_5810["N"].gt(1).any():
        raise RuntimeError(
            "La precarga 5810 quedó con más de un CODPESTUD "
            "para una misma CLAVE_OFERTA_PLAN."
        )

    p5809 = p5809.merge(
        mapa_5810.rename(
            columns={
                "CODPESTUD_RESUELTO":
                "CODPESTUD_DESDE_5810"
            }
        ),
        on="CLAVE_OFERTA_PLAN",
        how="left",
        validate="many_to_one",
    )

    mask_desde_5810 = (
        p5809["CODPESTUD_RESUELTO"].eq("")
        & p5809["CODPESTUD_DESDE_5810"]
        .fillna("")
        .ne("")
    )

    p5809.loc[
        mask_desde_5810,
        "CODPESTUD_RESUELTO",
    ] = p5809.loc[
        mask_desde_5810,
        "CODPESTUD_DESDE_5810",
    ]

    p5809.loc[
        mask_desde_5810,
        "METODO_RESOLUCION_CODPESTUD",
    ] = "HEREDADO_DESDE_PRECARGA_5810"

    p5809.loc[
        mask_desde_5810,
        "ESTADO_MAPEO_CODPESTUD",
    ] = "RESUELTO_DESDE_5810"

    p5809 = p5809.drop(
        columns=["CODPESTUD_DESDE_5810"]
    )

    # ========================================================
    # 4. MALLAS CANÓNICAS
    # ========================================================

    mallas = pd.read_excel(
        entradas["PLANES"],
        sheet_name="BBDD Bruta",
        dtype=object,
    )

    m_plan = buscar_columna(
        mallas,
        ["CODPESTUD"],
        obligatoria=True,
        contexto="CODPESTUD en mallas",
    )

    m_ramo = buscar_columna(
        mallas,
        ["CODRAMO"],
        obligatoria=True,
        contexto="CODRAMO en mallas",
    )

    m_nivel = buscar_columna(
        mallas,
        ["NIVEL"],
        obligatoria=True,
        contexto="NIVEL en mallas",
    )

    m_credito = buscar_columna(
        mallas,
        ["CREDITO", "CREDITOS"],
        obligatoria=True,
        contexto="CREDITO en mallas",
    )

    mc = mallas.copy()

    mc["CODPESTUD_NORM"] = (
        mc[m_plan].map(norm_codigo)
    )

    mc["CODRAMO_NORM"] = (
        mc[m_ramo].map(norm_codigo)
    )

    mc["NIVEL_NUM"] = pd.to_numeric(
        mc[m_nivel],
        errors="coerce",
    )

    mc["CREDITO_NUM"] = numerico(
        mc[m_credito]
    )

    mc["ANIO_CURRICULAR"] = (
        (mc["NIVEL_NUM"] + 1) // 2
    ).astype("Int64")

    llave_unidad = [
        "CODPESTUD_NORM",
        "CODRAMO_NORM",
        "NIVEL_NUM",
        "CREDITO_NUM",
    ]

    grupos = (
        mc.groupby(
            llave_unidad,
            dropna=False,
        )
        .size()
        .reset_index(name="N_REPETICIONES")
    )

    grupos["FILAS_EXCEDENTES"] = (
        grupos["N_REPETICIONES"] - 1
    ).clip(lower=0)

    duplicados = grupos[
        grupos["N_REPETICIONES"].gt(1)
    ].copy()

    canonico = mc.drop_duplicates(
        llave_unidad,
        keep="first",
    ).copy()

    resumen_plan = (
        canonico[
            canonico["CODPESTUD_NORM"].ne("")
        ]
        .groupby("CODPESTUD_NORM")
        .agg(
            NIVEL_MIN_PLAN=("NIVEL_NUM", "min"),
            NIVEL_MAX_PLAN=("NIVEL_NUM", "max"),
            RAMOS_DISTINTOS=("CODRAMO_NORM", "nunique"),
            TOTAL_CREDITOS=("CREDITO_NUM", "sum"),
        )
        .reset_index()
    )

    resumen_plan["ANIO_MAX_PLAN"] = (
        (resumen_plan["NIVEL_MAX_PLAN"] + 1) // 2
    ).astype("Int64")

    creditos_anio = (
        canonico.groupby(
            [
                "CODPESTUD_NORM",
                "ANIO_CURRICULAR",
            ],
            dropna=False,
        )["CREDITO_NUM"]
        .sum(min_count=1)
        .reset_index()
    )

    pivot = (
        creditos_anio.pivot(
            index="CODPESTUD_NORM",
            columns="ANIO_CURRICULAR",
            values="CREDITO_NUM",
        )
        .fillna(0)
        .reset_index()
    )

    for anio in range(1, 11):
        if anio not in pivot.columns:
            pivot[anio] = 0

    pivot = pivot.rename(
        columns={
            anio: f"CREDITOS_ANIO_{anio}"
            for anio in range(1, 11)
        }
    )

    resumen_plan = resumen_plan.merge(
        pivot,
        on="CODPESTUD_NORM",
        how="left",
        validate="one_to_one",
    )

    # ========================================================
    # 5. TRAZABILIDAD DE PLAN
    # ========================================================

    p5810 = p5810.merge(
        resumen_plan,
        left_on="CODPESTUD_RESUELTO",
        right_on="CODPESTUD_NORM",
        how="left",
        validate="many_to_one",
    )

    p5809 = p5809.merge(
        resumen_plan,
        left_on="CODPESTUD_RESUELTO",
        right_on="CODPESTUD_NORM",
        how="left",
        validate="many_to_one",
    )

    for df, sufijo in (
        (p5809, "5809"),
        (p5810, "5810"),
    ):
        df["CODPESTUD_EN_MALLA"] = (
            df["CODPESTUD_NORM"]
            .fillna("")
            .ne("")
        )

        df[f"ESTADO_TRAZABILIDAD_{sufijo}"] = ""

        mask_ok = (
            df["CODPESTUD_RESUELTO"].ne("")
            & df["CODPESTUD_EN_MALLA"]
        )

        df.loc[
            mask_ok,
            f"ESTADO_TRAZABILIDAD_{sufijo}",
        ] = "TRAZABLE_CODIGO_PLAN_MALLA"

        mask_sin_resolver = (
            df["CODPESTUD_RESUELTO"].eq("")
        )

        df.loc[
            mask_sin_resolver,
            f"ESTADO_TRAZABILIDAD_{sufijo}",
        ] = "CODPESTUD_PENDIENTE_RESOLUCION"

        mask_sin_malla = (
            df["CODPESTUD_RESUELTO"].ne("")
            & ~df["CODPESTUD_EN_MALLA"]
        )

        df.loc[
            mask_sin_malla,
            f"ESTADO_TRAZABILIDAD_{sufijo}",
        ] = "CODPESTUD_RESUELTO_SIN_MALLA"

    # ========================================================
    # 6. NIVEL DE ESTUDIANTE POR DOCUMENTO + CODPESTUD
    # ========================================================

    hoja1 = pd.read_excel(
        entradas["PROMEDIOS"],
        sheet_name="Hoja1",
        dtype=object,
    )

    h_doc = buscar_columna(
        hoja1,
        ["RUT", "NUM_DOCUMENTO", "N_DOC"],
        obligatoria=True,
        contexto="Documento Hoja1",
    )

    h_plan = buscar_columna(
        hoja1,
        [
            "CODPESTUD",
            "PLAN_DE_ESTUDIO",
            "PLAN_ESTUDIOS",
        ],
        obligatoria=True,
        contexto="Plan Hoja1",
    )

    h_nivel = buscar_columna(
        hoja1,
        ["NIVEL"],
        obligatoria=True,
        contexto="Nivel Hoja1",
    )

    h = hoja1.copy()

    h["DOCUMENTO_NORM"] = h[h_doc].map(
        norm_documento
    )

    h["CODPESTUD_HOJA1"] = h[h_plan].map(
        norm_codigo
    )

    h["NIVEL_HOJA1"] = pd.to_numeric(
        h[h_nivel],
        errors="coerce",
    )

    nivel_exacto = (
        h[
            h["DOCUMENTO_NORM"].ne("")
            & h["CODPESTUD_HOJA1"].ne("")
        ]
        .groupby(
            [
                "DOCUMENTO_NORM",
                "CODPESTUD_HOJA1",
            ]
        )
        .agg(
            NIVEL_MAX_HOJA1=("NIVEL_HOJA1", "max"),
            REGISTROS_HOJA1=("NIVEL_HOJA1", "size"),
        )
        .reset_index()
    )

    p5809 = p5809.merge(
        nivel_exacto,
        left_on=[
            "DOCUMENTO_NORM",
            "CODPESTUD_RESUELTO",
        ],
        right_on=[
            "DOCUMENTO_NORM",
            "CODPESTUD_HOJA1",
        ],
        how="left",
        validate="many_to_one",
    )

    p5809["NIVEL_EFECTIVO"] = pd.to_numeric(
        p5809["NIVEL_MAX_HOJA1"],
        errors="coerce",
    ).astype("Int64")

    p5809["ANIO_CURRICULAR_ALCANZADO"] = (
        (p5809["NIVEL_EFECTIVO"] + 1) // 2
    ).astype("Int64")

    p5809["FUENTE_NIVEL"] = ""

    p5809.loc[
        p5809["NIVEL_EFECTIVO"].notna(),
        "FUENTE_NIVEL",
    ] = "PROMEDIOSDEALUMNOS::Hoja1::DOCUMENTO+CODPESTUD"

    p5809.loc[
        p5809["NIVEL_EFECTIVO"].isna(),
        "FUENTE_NIVEL",
    ] = "PENDIENTE"

    p5809["PLAN_CUBRE_NIVEL"] = (
        p5809["NIVEL_EFECTIVO"].notna()
        & p5809["NIVEL_MAX_PLAN"].notna()
        & p5809["NIVEL_EFECTIVO"].le(
            p5809["NIVEL_MAX_PLAN"]
        )
    )

    mask_trazable_total = (
        p5809["CODPESTUD_EN_MALLA"]
        & p5809["NIVEL_EFECTIVO"].notna()
        & p5809["PLAN_CUBRE_NIVEL"]
    )

    p5809.loc[
        mask_trazable_total,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "TRAZABLE_PLAN_NIVEL"

    mask_pendiente_nivel = (
        p5809["CODPESTUD_EN_MALLA"]
        & p5809["NIVEL_EFECTIVO"].isna()
    )

    p5809.loc[
        mask_pendiente_nivel,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "TRAZABLE_PLAN_PENDIENTE_NIVEL"

    mask_conflicto = (
        p5809["CODPESTUD_EN_MALLA"]
        & p5809["NIVEL_EFECTIVO"].notna()
        & ~p5809["PLAN_CUBRE_NIVEL"]
    )

    p5809.loc[
        mask_conflicto,
        "ESTADO_TRAZABILIDAD_5809",
    ] = "CONFLICTO_PLAN_NO_CUBRE_NIVEL"

    # ========================================================
    # 7. CANDIDATO 5810
    # ========================================================

    candidato_5810 = p5810[
        ["ID_FILA_5810"] + COLUMNAS_5810
    ].copy()

    resumen_indexado = resumen_plan.set_index(
        "CODPESTUD_NORM"
    )

    for indice, fila in p5810.iterrows():
        codpestud = fila["CODPESTUD_RESUELTO"]

        if (
            not codpestud
            or codpestud not in resumen_indexado.index
        ):
            continue

        info = resumen_indexado.loc[codpestud]

        candidato_5810.loc[
            candidato_5810["ID_FILA_5810"].eq(
                fila["ID_FILA_5810"]
            ),
            "TOTAL_UNIDADES_MEDIDA",
        ] = info["TOTAL_CREDITOS"]

        for anio, columna in COLUMNAS_ANUALES.items():
            candidato_5810.loc[
                candidato_5810["ID_FILA_5810"].eq(
                    fila["ID_FILA_5810"]
                ),
                columna,
            ] = info.get(
                f"CREDITOS_ANIO_{anio}",
                0,
            )

    candidato_5810 = candidato_5810.drop(
        columns=["ID_FILA_5810"]
    )[COLUMNAS_5810]

    # ========================================================
    # 8. COBERTURA Y BLOQUEOS
    # ========================================================

    estados_5809 = (
        p5809["ESTADO_TRAZABILIDAD_5809"]
        .value_counts(dropna=False)
        .rename_axis("ESTADO")
        .reset_index(name="CASOS")
    )

    estados_5810 = (
        p5810["ESTADO_TRAZABILIDAD_5810"]
        .value_counts(dropna=False)
        .rename_axis("ESTADO")
        .reset_index(name="CASOS")
    )

    bloqueos = []

    def check(nombre: str, cantidad: int) -> None:
        if cantidad > 0:
            bloqueos.append({
                "BLOQUEO": nombre,
                "CASOS": int(cantidad),
            })

    check(
        "5810_CODPESTUD_PENDIENTE",
        p5810["CODPESTUD_RESUELTO"].eq("").sum(),
    )

    check(
        "5810_CODPESTUD_SIN_MALLA",
        (
            p5810["CODPESTUD_RESUELTO"].ne("")
            & ~p5810["CODPESTUD_EN_MALLA"]
        ).sum(),
    )

    check(
        "5809_CODPESTUD_PENDIENTE",
        p5809["CODPESTUD_RESUELTO"].eq("").sum(),
    )

    check(
        "5809_CODPESTUD_SIN_MALLA",
        (
            p5809["CODPESTUD_RESUELTO"].ne("")
            & ~p5809["CODPESTUD_EN_MALLA"]
        ).sum(),
    )

    check(
        "5809_NIVEL_PENDIENTE",
        p5809["NIVEL_EFECTIVO"].isna().sum(),
    )

    check(
        "5809_PLAN_NO_CUBRE_NIVEL",
        p5809[
            "ESTADO_TRAZABILIDAD_5809"
        ].eq(
            "CONFLICTO_PLAN_NO_CUBRE_NIVEL"
        ).sum(),
    )

    bloqueos_df = pd.DataFrame(
        bloqueos,
        columns=["BLOQUEO", "CASOS"],
    )

    cobertura_5810 = round(
        p5810["ESTADO_TRAZABILIDAD_5810"]
        .eq("TRAZABLE_CODIGO_PLAN_MALLA")
        .mean() * 100,
        2,
    )

    cobertura_plan_5809 = round(
        p5809["CODPESTUD_EN_MALLA"]
        .mean() * 100,
        2,
    )

    cobertura_total_5809 = round(
        p5809["ESTADO_TRAZABILIDAD_5809"]
        .eq("TRAZABLE_PLAN_NIVEL")
        .mean() * 100,
        2,
    )

    # ========================================================
    # 9. EXPORTACIÓN
    # ========================================================

    p5809.to_csv(
        resultados / "01_5809_TRAZABILIDAD.tsv",
        sep="\t",
        index=False,
    )

    p5810.to_csv(
        resultados / "02_5810_TRAZABILIDAD.tsv",
        sep="\t",
        index=False,
    )

    candidato_5810.to_csv(
        resultados / "03_5810_CANDIDATO_CONTROL.csv",
        sep=";",
        encoding="cp1252",
        index=False,
    )

    mapa.to_csv(
        auditorias / "01_MAPA_CIERRE_43_CODPESTUD.tsv",
        sep="\t",
        index=False,
    )

    mapa_por_codigo.to_csv(
        auditorias / "02_RESUMEN_MAPEO_POR_CODIGO_UNICO.tsv",
        sep="\t",
        index=False,
    )

    resumen_plan.to_csv(
        auditorias / "03_RESUMEN_MALLAS_POR_CODPESTUD.tsv",
        sep="\t",
        index=False,
    )

    duplicados.to_csv(
        auditorias / "04_DUPLICADOS_FISICOS_MALLAS.tsv",
        sep="\t",
        index=False,
    )

    canonico.to_csv(
        auditorias / "05_MALLAS_CANONICAS.tsv",
        sep="\t",
        index=False,
    )

    bloqueos_df.to_csv(
        auditorias / "06_BLOQUEOS.tsv",
        sep="\t",
        index=False,
    )

    estados_5809.to_csv(
        auditorias / "07_ESTADOS_5809.tsv",
        sep="\t",
        index=False,
    )

    estados_5810.to_csv(
        auditorias / "08_ESTADOS_5810.tsv",
        sep="\t",
        index=False,
    )

    fuentes = pd.DataFrame([
        {
            "ROL": rol,
            "RUTA": str(ruta),
            "SHA256": sha256(ruta),
        }
        for rol, ruta in entradas.items()
    ])

    fuentes.to_csv(
        auditorias / "09_FUENTES.tsv",
        sep="\t",
        index=False,
    )

    excel = (
        resultados
        / "GOBERNANZA_AVANCE_CURRICULAR_V2.xlsx"
    )

    resumen = pd.DataFrame([
        {
            "INDICADOR": "Universo rector 5809",
            "VALOR": len(p5809),
        },
        {
            "INDICADOR": "Universo rector 5810",
            "VALOR": len(p5810),
        },
        {
            "INDICADOR": "CODIGO_UNICO distintos 5809",
            "VALOR": p5809["CODIGO_UNICO_NORM"].nunique(),
        },
        {
            "INDICADOR": "CODIGO_UNICO distintos 5810",
            "VALOR": p5810["CODIGO_UNICO_NORM"].nunique(),
        },
        {
            "INDICADOR": "CODPESTUD distintos resueltos 5809",
            "VALOR": p5809.loc[
                p5809["CODPESTUD_RESUELTO"].ne(""),
                "CODPESTUD_RESUELTO",
            ].nunique(),
        },
        {
            "INDICADOR": "CODPESTUD distintos resueltos 5810",
            "VALOR": p5810.loc[
                p5810["CODPESTUD_RESUELTO"].ne(""),
                "CODPESTUD_RESUELTO",
            ].nunique(),
        },
        {
            "INDICADOR": "Cobertura de plan 5810",
            "VALOR": f"{cobertura_5810}%",
        },
        {
            "INDICADOR": "Cobertura de plan 5809",
            "VALOR": f"{cobertura_plan_5809}%",
        },
        {
            "INDICADOR": "Cobertura plan+nivel 5809",
            "VALOR": f"{cobertura_total_5809}%",
        },
        {
            "INDICADOR": "Bloqueos",
            "VALOR": len(bloqueos_df),
        },
    ])

    with pd.ExcelWriter(
        excel,
        engine="openpyxl",
    ) as writer:
        resumen.to_excel(
            writer,
            sheet_name="RESUMEN",
            index=False,
        )

        p5810.to_excel(
            writer,
            sheet_name="5810_TRAZABILIDAD",
            index=False,
        )

        p5809.to_excel(
            writer,
            sheet_name="5809_TRAZABILIDAD",
            index=False,
        )

        candidato_5810.to_excel(
            writer,
            sheet_name="5810_CANDIDATO",
            index=False,
        )

        mapa.to_excel(
            writer,
            sheet_name="MAPA_43",
            index=False,
        )

        resumen_plan.to_excel(
            writer,
            sheet_name="MALLAS_POR_PLAN",
            index=False,
        )

        estados_5810.to_excel(
            writer,
            sheet_name="ESTADOS_5810",
            index=False,
        )

        estados_5809.to_excel(
            writer,
            sheet_name="ESTADOS_5809",
            index=False,
        )

        bloqueos_df.to_excel(
            writer,
            sheet_name="BLOQUEOS",
            index=False,
        )

        fuentes.to_excel(
            writer,
            sheet_name="FUENTES",
            index=False,
        )

        for hoja in writer.book.worksheets:
            hoja.freeze_panes = "A2"
            hoja.auto_filter.ref = hoja.dimensions

            for columna in hoja.columns:
                letra = columna[0].column_letter
                ancho = max(
                    len(str(celda.value or ""))
                    for celda in columna[:2000]
                )
                hoja.column_dimensions[letra].width = min(
                    max(ancho + 2, 12),
                    45,
                )

    estado_cierre = (
        "APTO_PARA_REVISION_FUNCIONAL"
        if bloqueos_df.empty
        else "NO_APTO_CON_BLOQUEOS"
    )

    manifiesto = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "proceso": "Avance Curricular SIES",
        "anio_proceso": args.anio_proceso,
        "anio_referencia_datos": args.anio_datos,
        "universo_rector": "Precarga 5809",
        "llave_oferta_plan": (
            "CODIGO_UNICO + PLAN_ESTUDIOS"
        ),
        "plan_institucional": "CODPESTUD",
        "fuente_mapeo_codpestud": str(
            entradas["CIERRE_43"]
        ),
        "regla_anio": (
            "ANIO_CURRICULAR=TECHO(NIVEL/2)"
        ),
        "cobertura_5810": cobertura_5810,
        "cobertura_plan_5809": cobertura_plan_5809,
        "cobertura_total_5809": cobertura_total_5809,
        "bloqueos": len(bloqueos_df),
        "estado_cierre": estado_cierre,
        "fuentes_modificadas": False,
        "archivo_final_carga_declarado": False,
    }

    (
        salida / "manifest_ejecucion.json"
    ).write_text(
        json.dumps(
            manifiesto,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    reporte = [
        "GOBERNANZA AVANCE CURRICULAR V2",
        "=" * 80,
        f"Universo rector 5809: {len(p5809)}",
        f"Universo rector 5810: {len(p5810)}",
        (
            "CODIGO_UNICO distintos 5809: "
            f"{p5809['CODIGO_UNICO_NORM'].nunique()}"
        ),
        (
            "CODIGO_UNICO distintos 5810: "
            f"{p5810['CODIGO_UNICO_NORM'].nunique()}"
        ),
        (
            "CODPESTUD distintos 5809: "
            f"{p5809.loc[p5809['CODPESTUD_RESUELTO'].ne(''), 'CODPESTUD_RESUELTO'].nunique()}"
        ),
        (
            "CODPESTUD distintos 5810: "
            f"{p5810.loc[p5810['CODPESTUD_RESUELTO'].ne(''), 'CODPESTUD_RESUELTO'].nunique()}"
        ),
        f"Cobertura 5810: {cobertura_5810}%",
        f"Cobertura de plan 5809: {cobertura_plan_5809}%",
        (
            "Cobertura plan+nivel 5809: "
            f"{cobertura_total_5809}%"
        ),
        f"Bloqueos: {len(bloqueos_df)}",
        f"Estado: {estado_cierre}",
        f"Excel: {excel}",
        f"Carpeta: {salida}",
        "Fuentes modificadas: NO",
        "Archivo definitivo de carga: NO",
    ]

    (
        reportes / "RESUMEN_EJECUCION.txt"
    ).write_text(
        "\n".join(reporte),
        encoding="utf-8",
    )

    print()
    print("=" * 88)
    print("GOBERNANZA AVANCE CURRICULAR V2")
    print("=" * 88)
    print(f"Universo rector 5809: {len(p5809)}")
    print(f"Universo rector 5810: {len(p5810)}")
    print()
    print(
        "CODIGO_UNICO distintos 5809: "
        f"{p5809['CODIGO_UNICO_NORM'].nunique()}"
    )
    print(
        "CODIGO_UNICO distintos 5810: "
        f"{p5810['CODIGO_UNICO_NORM'].nunique()}"
    )
    print(
        "CODPESTUD distintos resueltos 5809: "
        f"{p5809.loc[p5809['CODPESTUD_RESUELTO'].ne(''), 'CODPESTUD_RESUELTO'].nunique()}"
    )
    print(
        "CODPESTUD distintos resueltos 5810: "
        f"{p5810.loc[p5810['CODPESTUD_RESUELTO'].ne(''), 'CODPESTUD_RESUELTO'].nunique()}"
    )
    print()
    print("TRAZABILIDAD 5810")
    print("-" * 88)

    for _, fila in estados_5810.iterrows():
        print(f"{fila['ESTADO']}: {fila['CASOS']}")

    print()
    print("TRAZABILIDAD 5809")
    print("-" * 88)

    for _, fila in estados_5809.iterrows():
        print(f"{fila['ESTADO']}: {fila['CASOS']}")

    print()
    print(f"Cobertura 5810: {cobertura_5810}%")
    print(f"Cobertura de plan 5809: {cobertura_plan_5809}%")
    print(
        "Cobertura plan+nivel 5809: "
        f"{cobertura_total_5809}%"
    )
    print(f"Bloqueos: {len(bloqueos_df)}")
    print(f"Estado de cierre: {estado_cierre}")
    print()
    print(f"Excel: {excel}")
    print(f"Carpeta: {salida}")
    print()
    print("Fuentes modificadas: NO")
    print("Archivo definitivo de carga: NO")
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
        print("Fuentes modificadas: NO")
        print("=" * 88)
        raise
