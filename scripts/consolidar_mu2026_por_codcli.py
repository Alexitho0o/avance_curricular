from __future__ import annotations

from pathlib import Path
from typing import Iterable
from datetime import datetime
import hashlib
import json
import shutil
import sys
import unicodedata

import pandas as pd


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
)

ARCHIVO_4070 = (
    RAIZ
    / "control"
    / "punto_0_carga_principal_mu2026"
    / "archivos_congelados"
    / "PARA_SUBIR_DESKTOP__matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
)

CARPETA_RECONSTRUIDA = (
    RAIZ
    / "resultados"
    / "auditoria_multicodcli_mu2026_reconstruida_desde_cero"
)

ARCHIVO_30 = (
    CARPETA_RECONSTRUIDA
    / "03_archivos_rectificacion"
    / "RECTIFICACION_MU2026_RECONSTRUIDA_DESDE_CERO.csv"
)

SALIDA_DIR = (
    CARPETA_RECONSTRUIDA
    / "03_archivos_rectificacion"
    / "consolidacion_codcli"
)

ARCHIVO_FINAL = (
    SALIDA_DIR
    / "MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_POR_CODCLI.csv"
)

ARCHIVO_EXCEL = (
    SALIDA_DIR
    / "MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_POR_CODCLI_AUDITABLE.xlsx"
)

ARCHIVO_MANIFIESTO = (
    SALIDA_DIR
    / "MANIFIESTO_CONSOLIDACION_POR_CODCLI.json"
)

ARCHIVO_LOG = (
    SALIDA_DIR
    / "LOG_CONSOLIDACION_POR_CODCLI.txt"
)

ESCRITORIO = Path.home() / "Desktop"

COLUMNAS_MU = [
    "TIPO_DOC",
    "N_DOC",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRE",
    "SEXO",
    "FECH_NAC",
    "NAC",
    "PAIS_EST_SEC",
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "FOR_ING_ACT",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ANIO_ING_ORI",
    "SEM_ING_ORI",
    "ASI_INS_ANT",
    "ASI_APR_ANT",
    "PROM_PRI_SEM",
    "PROM_SEG_SEM",
    "ASI_INS_HIS",
    "ASI_APR_HIS",
    "NIV_ACA",
    "SIT_FON_SOL",
    "SUS_PRE",
    "FECHA_MATRICULA",
    "REINCORPORACION",
    "VIG",
]

EXTENSIONES_CATALOGO = {
    ".csv",
    ".xlsx",
    ".xlsm",
}

PALABRAS_PRIORITARIAS_CATALOGO = [
    "codcli",
    "multicodcli",
    "rectificacion",
    "duplicado",
    "comparacion",
    "decision",
    "auditoria",
    "matricula",
    "promedio",
    "matriz",
]


# ============================================================
# LOG
# ============================================================

MENSAJES_LOG: list[str] = []


def log(texto: str = "") -> None:
    texto = str(texto)
    print(texto)
    MENSAJES_LOG.append(texto)


# ============================================================
# UTILIDADES GENERALES
# ============================================================

def sha256(ruta: Path) -> str:
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def quitar_tildes(texto: str) -> str:
    texto = str(texto or "")

    return "".join(
        caracter
        for caracter in unicodedata.normalize(
            "NFKD",
            texto,
        )
        if not unicodedata.combining(caracter)
    )


def normalizar_nombre_columna(nombre: str) -> str:
    nombre = quitar_tildes(nombre)
    nombre = nombre.upper().strip()

    for caracter in [
        " ",
        "-",
        ".",
        "/",
        "\\",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        ":",
        ";",
    ]:
        nombre = nombre.replace(caracter, "_")

    while "__" in nombre:
        nombre = nombre.replace("__", "_")

    return nombre.strip("_")


def normalizar_texto(valor) -> str:
    """
    Convierte un valor potencialmente escalar o compuesto
    en un texto limpio.

    Algunas fuentes pueden contener columnas cuyos nombres,
    después de ser normalizados, quedan duplicados. En esos
    casos pandas puede devolver una Series en fila.get(...).
    Se toma el primer valor no vacío de manera determinística.
    """

    if isinstance(valor, pd.DataFrame):
        valores = valor.to_numpy().ravel().tolist()

        for elemento in valores:
            texto = normalizar_texto(elemento)

            if texto:
                return texto

        return ""

    if isinstance(valor, pd.Series):
        for elemento in valor.tolist():
            texto = normalizar_texto(elemento)

            if texto:
                return texto

        return ""

    if isinstance(valor, (list, tuple, set)):
        for elemento in valor:
            texto = normalizar_texto(elemento)

            if texto:
                return texto

        return ""

    if valor is None:
        return ""

    try:
        es_nulo = pd.isna(valor)

        if isinstance(es_nulo, bool) and es_nulo:
            return ""

    except (TypeError, ValueError):
        pass

    texto = str(valor).strip()

    if texto.lower() in {
        "",
        "nan",
        "none",
        "null",
        "<na>",
        "nat",
    }:
        return ""

    return texto


def normalizar_numero_codigo(valor) -> str:
    texto = normalizar_texto(valor)

    if texto.endswith(".0"):
        parte = texto[:-2]

        if parte.isdigit():
            texto = parte

    return texto.strip()


def normalizar_rut(numero, dv="") -> str:
    numero = normalizar_texto(numero).upper()
    dv = normalizar_texto(dv).upper()

    numero = (
        numero.replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )

    dv = (
        dv.replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )

    if not numero:
        return ""

    if dv:
        return f"{numero}-{dv}"

    if len(numero) >= 2:
        posible_dv = numero[-1]
        cuerpo = numero[:-1]

        if cuerpo.isdigit() and (
            posible_dv.isdigit()
            or posible_dv == "K"
        ):
            return f"{cuerpo}-{posible_dv}"

    return numero


def normalizar_codcli(valor) -> str:
    return (
        normalizar_texto(valor)
        .upper()
        .replace(" ", "")
    )


def construir_oferta_desde_valores(
    sede,
    carrera,
    modalidad,
    jornada,
    version,
) -> str:
    sede = normalizar_numero_codigo(sede)
    carrera = normalizar_numero_codigo(carrera)
    modalidad = normalizar_numero_codigo(modalidad)
    jornada = normalizar_numero_codigo(jornada)
    version = normalizar_numero_codigo(version)

    if not all(
        [
            sede,
            carrera,
            modalidad,
            jornada,
            version,
        ]
    ):
        return ""

    return (
        f"S{sede}"
        f"C{carrera}"
        f"M{modalidad}"
        f"J{jornada}"
        f"V{version}"
    ).upper()


def construir_oferta(df: pd.DataFrame) -> pd.Series:
    return pd.Series(
        [
            construir_oferta_desde_valores(
                sede,
                carrera,
                modalidad,
                jornada,
                version,
            )
            for sede, carrera, modalidad, jornada, version
            in zip(
                df["COD_SED"],
                df["COD_CAR"],
                df["MODALIDAD"],
                df["JOR"],
                df["VERSION"],
            )
        ],
        index=df.index,
        dtype="string",
    )


def primera_columna_existente(
    columnas: Iterable[str],
    candidatos: Iterable[str],
) -> str | None:
    conjunto = {
        normalizar_nombre_columna(columna)
        for columna in columnas
    }

    for candidato in candidatos:
        candidato_normalizado = (
            normalizar_nombre_columna(candidato)
        )

        if candidato_normalizado in conjunto:
            return candidato_normalizado

    return None


# ============================================================
# LECTURA DE ARCHIVOS OPERATIVOS DE 32 COLUMNAS
# ============================================================

def leer_csv_32(ruta: Path) -> tuple[pd.DataFrame, str]:
    errores = []

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]:
        try:
            df = pd.read_csv(
                ruta,
                sep=";",
                header=None,
                dtype=str,
                encoding=encoding,
                keep_default_na=False,
                na_filter=False,
            )

            if df.shape[1] != 32:
                errores.append(
                    f"{encoding}: "
                    f"{df.shape[1]} columnas"
                )
                continue

            df.columns = COLUMNAS_MU

            for columna in COLUMNAS_MU:
                df[columna] = (
                    df[columna]
                    .astype(str)
                    .str.strip()
                )

            df["RUT_NORM"] = [
                normalizar_rut(numero, dv)
                for numero, dv in zip(
                    df["N_DOC"],
                    df["DV"],
                )
            ]

            df["OFERTA_SIES"] = construir_oferta(df)

            df["LLAVE_RUT_OFERTA"] = (
                df["RUT_NORM"].astype(str)
                + "|"
                + df["OFERTA_SIES"].astype(str)
            )

            df["FILA_32"] = (
                df[COLUMNAS_MU]
                .astype(str)
                .agg("|".join, axis=1)
            )

            return df, encoding

        except Exception as exc:
            errores.append(
                f"{encoding}: "
                f"{type(exc).__name__}: {exc}"
            )

    raise RuntimeError(
        f"No fue posible leer correctamente:\n{ruta}\n\n"
        + "\n".join(errores)
    )


# ============================================================
# LOCALIZACIÓN CONTROLADA DEL COMPLEMENTO DE 95 REGISTROS
# ============================================================

def buscar_archivos_95() -> list[Path]:
    patrones = [
        "*95*CODCLI*.csv",
        "*95*codcli*.csv",
        "*COMPLEMENTO*95*.csv",
        "*complemento*95*.csv",
        "*95*PARA_SUBIR*.csv",
        "*95*para_subir*.csv",
        "*95*.csv",
    ]

    candidatos: set[Path] = set()

    for patron in patrones:
        for ruta in RAIZ.rglob(patron):
            texto = str(ruta).lower()

            if not ruta.is_file():
                continue

            if ruta == ARCHIVO_30:
                continue

            if ruta == ARCHIVO_4070:
                continue

            if "/.git/" in texto:
                continue

            if "/archive/" in texto:
                continue

            if "invalidado" in texto:
                continue

            if "consolidada_por_codcli" in texto:
                continue

            candidatos.add(ruta)

    validos = []

    for ruta in sorted(candidatos):
        try:
            df, _ = leer_csv_32(ruta)

            if len(df) == 95:
                validos.append(ruta)

        except Exception:
            continue

    return sorted(
        validos,
        key=lambda ruta: (
            ruta.stat().st_mtime,
            ruta.stat().st_size,
            str(ruta),
        ),
        reverse=True,
    )


# ============================================================
# LECTURA GENÉRICA PARA CONSTRUIR CATÁLOGO CODCLI
# ============================================================

def leer_tablas_fuente(ruta: Path) -> list[pd.DataFrame]:
    tablas: list[pd.DataFrame] = []

    if ruta.suffix.lower() == ".csv":
        intentos = []

        for separador in [
            ";",
            ",",
            "\t",
            "|",
        ]:
            for encoding in [
                "utf-8-sig",
                "utf-8",
                "cp1252",
                "latin-1",
            ]:
                try:
                    df = pd.read_csv(
                        ruta,
                        sep=separador,
                        dtype=str,
                        encoding=encoding,
                        keep_default_na=False,
                        na_filter=False,
                        low_memory=False,
                    )

                    if df.shape[1] < 2:
                        continue

                    if df.empty:
                        continue

                    df.columns = [
                        normalizar_nombre_columna(columna)
                        for columna in df.columns
                    ]

                    df["__ARCHIVO_ORIGEN"] = str(ruta)
                    df["__HOJA_ORIGEN"] = "CSV"
                    df["__SEPARADOR_ORIGEN"] = separador
                    df["__ENCODING_ORIGEN"] = encoding

                    tablas.append(df)
                    return tablas

                except Exception as exc:
                    intentos.append(
                        f"{separador}/{encoding}: {exc}"
                    )

    elif ruta.suffix.lower() in {
        ".xlsx",
        ".xlsm",
    }:
        try:
            hojas = pd.read_excel(
                ruta,
                sheet_name=None,
                dtype=str,
                engine="openpyxl",
            )

            for nombre_hoja, df in hojas.items():
                if df is None:
                    continue

                if df.empty:
                    continue

                df = df.fillna("")

                df.columns = [
                    normalizar_nombre_columna(columna)
                    for columna in df.columns
                ]

                df["__ARCHIVO_ORIGEN"] = str(ruta)
                df["__HOJA_ORIGEN"] = str(nombre_hoja)
                df["__SEPARADOR_ORIGEN"] = ""
                df["__ENCODING_ORIGEN"] = ""

                tablas.append(df)

        except Exception:
            return []

    return tablas


def descubrir_fuentes_codcli() -> list[Path]:
    rutas_prioritarias: list[Path] = []
    otras_rutas: list[Path] = []

    for ruta in RAIZ.rglob("*"):
        if not ruta.is_file():
            continue

        if ruta.suffix.lower() not in EXTENSIONES_CATALOGO:
            continue

        texto = str(ruta).lower()
        nombre = ruta.name.lower()

        if "/.git/" in texto:
            continue

        if "/archive/" in texto:
            continue

        if "invalidado" in texto:
            continue

        if "consolidacion_codcli" in texto:
            continue

        if ruta in {
            ARCHIVO_4070,
            ARCHIVO_30,
        }:
            continue

        if any(
            palabra in nombre
            for palabra in PALABRAS_PRIORITARIAS_CATALOGO
        ):
            rutas_prioritarias.append(ruta)
        else:
            otras_rutas.append(ruta)

    rutas = []

    for ruta in (
        sorted(rutas_prioritarias)
        + sorted(otras_rutas)
    ):
        if ruta not in rutas:
            rutas.append(ruta)

    return rutas


# ============================================================
# CONSTRUCCIÓN DEL CATÁLOGO CODCLI
# ============================================================

def construir_catalogo_codcli(
    fuentes: list[Path],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    registros = []
    inventario = []

    candidatos_codcli = [
        "CODCLI",
        "COD_CLI",
        "CODIGO_CLIENTE",
        "CODIGO_ALUMNO",
        "CODIGO_MATRICULA",
        "CODIGO_INSCRIPCION",
    ]

    candidatos_rut = [
        "RUT_NORM",
        "RUT",
        "RUN",
        "NUM_DOCUMENTO",
        "NUMERO_DOCUMENTO",
        "N_DOCUMENTO",
        "N_DOC",
        "DOCUMENTO",
    ]

    candidatos_dv = [
        "DV",
        "DIGITO_VERIFICADOR",
        "DIG_VERIFICADOR",
    ]

    candidatos_oferta = [
        "OFERTA_SIES",
        "OFERTA_ESPERADA",
        "OFERTA_MU",
        "LLAVE_OFERTA",
        "LLAVE_SIES",
        "CODIGO_OFERTA",
    ]

    candidatos_sede = [
        "COD_SED",
        "CODIGO_SEDE",
        "SEDE_SIES",
        "CODSEDE",
    ]

    candidatos_carrera = [
        "COD_CAR",
        "CODIGO_CARRERA",
        "CARRERA_SIES",
        "CODIGO_UNICO",
        "CODCARRERA",
    ]

    candidatos_modalidad = [
        "MODALIDAD",
        "COD_MODALIDAD",
        "CODMODALIDAD",
    ]

    candidatos_jornada = [
        "JOR",
        "JORNADA",
        "COD_JORNADA",
        "CODJORNADA",
    ]

    candidatos_version = [
        "VERSION",
        "VERSION_CARRERA",
        "COD_VERSION",
        "CODVERSION",
    ]

    total_fuentes = len(fuentes)

    for numero_fuente, ruta in enumerate(
        fuentes,
        start=1,
    ):
        if numero_fuente == 1 or numero_fuente % 25 == 0:
            log(
                f"Revisando fuentes CODCLI: "
                f"{numero_fuente}/{total_fuentes}"
            )

        tablas = leer_tablas_fuente(ruta)

        if not tablas:
            continue

        for tabla in tablas:
            if tabla is None:
                continue

            if tabla.empty:
                inventario.append(
                    {
                        "ARCHIVO": str(ruta),
                        "HOJA": "",
                        "FILAS": 0,
                        "COLUMNAS": len(tabla.columns),
                        "TIENE_CODCLI": "NO",
                        "COLUMNA_CODCLI": "",
                        "OBSERVACION": (
                            "TABLA_SIN_FILAS_EXCLUIDA"
                        ),
                    }
                )
                continue

            columnas = list(tabla.columns)

            col_codcli = primera_columna_existente(
                columnas,
                candidatos_codcli,
            )

            hoja_origen = ""

            if "__HOJA_ORIGEN" in tabla.columns:
                serie_hoja = tabla[
                    "__HOJA_ORIGEN"
                ].dropna()

                if not serie_hoja.empty:
                    hoja_origen = normalizar_texto(
                        serie_hoja.iloc[0]
                    )

            inventario.append(
                {
                    "ARCHIVO": str(ruta),
                    "HOJA": hoja_origen,
                    "FILAS": len(tabla),
                    "COLUMNAS": len(tabla.columns),
                    "TIENE_CODCLI": (
                        "SI" if col_codcli else "NO"
                    ),
                    "COLUMNA_CODCLI": col_codcli or "",
                    "OBSERVACION": "",
                }
            )

            if not col_codcli:
                continue

            col_rut = primera_columna_existente(
                columnas,
                candidatos_rut,
            )

            col_dv = primera_columna_existente(
                columnas,
                candidatos_dv,
            )

            col_oferta = primera_columna_existente(
                columnas,
                candidatos_oferta,
            )

            col_sede = primera_columna_existente(
                columnas,
                candidatos_sede,
            )

            col_carrera = primera_columna_existente(
                columnas,
                candidatos_carrera,
            )

            col_modalidad = primera_columna_existente(
                columnas,
                candidatos_modalidad,
            )

            col_jornada = primera_columna_existente(
                columnas,
                candidatos_jornada,
            )

            col_version = primera_columna_existente(
                columnas,
                candidatos_version,
            )

            for indice, fila in tabla.iterrows():
                codcli = normalizar_codcli(
                    fila.get(col_codcli, "")
                )

                if not codcli:
                    continue

                rut = ""

                if col_rut:
                    valor_rut = fila.get(
                        col_rut,
                        "",
                    )

                    if col_dv:
                        rut = normalizar_rut(
                            valor_rut,
                            fila.get(col_dv, ""),
                        )
                    else:
                        rut = normalizar_rut(
                            valor_rut
                        )

                oferta = ""

                if col_oferta:
                    oferta = (
                        normalizar_texto(
                            fila.get(col_oferta, "")
                        )
                        .upper()
                        .replace(" ", "")
                    )

                if not oferta:
                    oferta = construir_oferta_desde_valores(
                        fila.get(col_sede, "")
                        if col_sede else "",
                        fila.get(col_carrera, "")
                        if col_carrera else "",
                        fila.get(col_modalidad, "")
                        if col_modalidad else "",
                        fila.get(col_jornada, "")
                        if col_jornada else "",
                        fila.get(col_version, "")
                        if col_version else "",
                    )

                registros.append(
                    {
                        "CODCLI": codcli,
                        "RUT_NORM": rut,
                        "OFERTA_SIES": oferta,
                        "ARCHIVO_CODCLI": fila.get(
                            "__ARCHIVO_ORIGEN",
                            str(ruta),
                        ),
                        "HOJA_CODCLI": fila.get(
                            "__HOJA_ORIGEN",
                            "",
                        ),
                        "FILA_CODCLI": int(indice) + 2,
                        "COLUMNA_CODCLI": col_codcli,
                        "COLUMNA_RUT": col_rut or "",
                        "COLUMNA_OFERTA": col_oferta or "",
                    }
                )

    if not registros:
        raise SystemExit(
            "\nERROR: no se encontró ninguna fuente activa "
            "que contenga una columna CODCLI utilizable."
        )

    catalogo = pd.DataFrame(registros)

    for columna in [
        "CODCLI",
        "RUT_NORM",
        "OFERTA_SIES",
    ]:
        catalogo[columna] = (
            catalogo[columna]
            .astype(str)
            .str.strip()
        )

    catalogo = (
        catalogo.drop_duplicates()
        .reset_index(drop=True)
    )

    inventario_df = pd.DataFrame(inventario)

    return catalogo, inventario_df


# ============================================================
# ASIGNACIÓN DE CODCLI A LOS ARCHIVOS OPERATIVOS
# ============================================================

def asignar_codcli(
    operativo: pd.DataFrame,
    catalogo: pd.DataFrame,
    nombre_origen: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    asignados = []
    conflictos = []

    for indice, fila in operativo.iterrows():
        rut = fila["RUT_NORM"]
        oferta = fila["OFERTA_SIES"]

        candidatos_exactos = catalogo.loc[
            catalogo["RUT_NORM"].eq(rut)
            & catalogo["OFERTA_SIES"].eq(oferta)
        ].copy()

        codcli_exactos = sorted(
            candidatos_exactos.loc[
                candidatos_exactos["CODCLI"].ne(""),
                "CODCLI",
            ]
            .drop_duplicates()
            .tolist()
        )

        if len(codcli_exactos) == 1:
            codcli = codcli_exactos[0]

            evidencia = candidatos_exactos.loc[
                candidatos_exactos["CODCLI"].eq(
                    codcli
                )
            ].iloc[0]

            registro = fila.to_dict()

            registro.update(
                {
                    "CODCLI": codcli,
                    "METODO_ASIGNACION_CODCLI": (
                        "RUT_MAS_OFERTA_SIES_EXACTA"
                    ),
                    "ARCHIVO_EVIDENCIA_CODCLI": (
                        evidencia["ARCHIVO_CODCLI"]
                    ),
                    "HOJA_EVIDENCIA_CODCLI": (
                        evidencia["HOJA_CODCLI"]
                    ),
                    "FILA_EVIDENCIA_CODCLI": (
                        evidencia["FILA_CODCLI"]
                    ),
                    "ORIGEN_CARGA": nombre_origen,
                }
            )

            asignados.append(registro)
            continue

        candidatos_rut = catalogo.loc[
            catalogo["RUT_NORM"].eq(rut)
        ].copy()

        codcli_rut = sorted(
            candidatos_rut.loc[
                candidatos_rut["CODCLI"].ne(""),
                "CODCLI",
            ]
            .drop_duplicates()
            .tolist()
        )

        ofertas_rut = sorted(
            candidatos_rut.loc[
                candidatos_rut["OFERTA_SIES"].ne(""),
                "OFERTA_SIES",
            ]
            .drop_duplicates()
            .tolist()
        )

        if len(codcli_exactos) > 1:
            motivo = (
                "MAS_DE_UN_CODCLI_PARA_EL_MISMO_RUT_Y_OFERTA"
            )

        elif len(codcli_rut) == 1:
            motivo = (
                "CODCLI_UNICO_POR_RUT_PERO_OFERTA_NO_COINCIDE"
            )

        elif len(codcli_rut) > 1:
            motivo = (
                "VARIOS_CODCLI_POR_RUT_SIN_COINCIDENCIA_EXACTA"
            )

        else:
            motivo = "SIN_CODCLI_EN_CATALOGO"

        conflictos.append(
            {
                "ORIGEN_CARGA": nombre_origen,
                "FILA_OPERATIVA": int(indice) + 1,
                "RUT_NORM": rut,
                "OFERTA_SIES_OPERATIVA": oferta,
                "CODCLI_EXACTOS": " || ".join(
                    codcli_exactos
                ),
                "CODCLI_DEL_RUT": " || ".join(
                    codcli_rut
                ),
                "OFERTAS_DEL_RUT_EN_CATALOGO": (
                    " || ".join(ofertas_rut)
                ),
                "MOTIVO": motivo,
            }
        )

    asignados_df = pd.DataFrame(asignados)
    conflictos_df = pd.DataFrame(conflictos)

    return asignados_df, conflictos_df


# ============================================================
# VALIDACIONES DE CODCLI
# ============================================================

def validar_codcli_interno(
    df: pd.DataFrame,
    nombre: str,
) -> pd.DataFrame:
    resumen = (
        df.groupby(
            "CODCLI",
            dropna=False,
        )
        .agg(
            FILAS=("CODCLI", "size"),
            RUT_DISTINTOS=("RUT_NORM", "nunique"),
            OFERTAS_DISTINTAS=(
                "OFERTA_SIES",
                "nunique",
            ),
        )
        .reset_index()
    )

    conflictivos = resumen.loc[
        (resumen["CODCLI"].eq(""))
        | (resumen["FILAS"] > 1)
        | (resumen["RUT_DISTINTOS"] > 1)
        | (resumen["OFERTAS_DISTINTAS"] > 1)
    ].copy()

    if not conflictivos.empty:
        log()
        log(
            f"ERROR: {nombre} contiene CODCLI "
            "vacíos, repetidos o conflictivos."
        )
        log(
            conflictivos.to_string(
                index=False
            )
        )

    return conflictivos


# ============================================================
# INICIO
# ============================================================

inicio = datetime.now()

log("=" * 120)
log("CONSOLIDACIÓN MATRÍCULA UNIFICADA 2026 POR CODCLI")
log("=" * 120)
log(f"Inicio: {inicio.isoformat()}")
log(f"Repositorio: {RAIZ}")
log()


# ============================================================
# VALIDACIÓN DE FUENTES OBLIGATORIAS
# ============================================================

for ruta in [
    ARCHIVO_4070,
    ARCHIVO_30,
]:
    if not ruta.exists():
        raise SystemExit(
            f"\nERROR: no existe la fuente requerida:\n{ruta}"
        )

ARCHIVO_95 = (
    RAIZ
    / "control"
    / "auditoria_mu2026_punto0_complemento95"
    / "archivos_congelados"
    / "complemento_95"
    / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
)

HASH_ARCHIVO_95_ESPERADO = (
    "9a6bc998c19282da421d6e9aa51606d94"
    "d886a87bcf958f74efb40109be62c6d"
)

if not ARCHIVO_95.exists():
    raise SystemExit(
        "\nERROR: no existe el complemento congelado "
        "del punto de control:\n"
        f"{ARCHIVO_95}"
    )

hash_archivo_95_real = sha256(
    ARCHIVO_95
)

if hash_archivo_95_real != HASH_ARCHIVO_95_ESPERADO:
    raise SystemExit(
        "\nERROR: el complemento congelado no coincide "
        "con el hash de evidencia.\n\n"
        f"Esperado: {HASH_ARCHIVO_95_ESPERADO}\n"
        f"Obtenido: {hash_archivo_95_real}\n"
        f"Archivo: {ARCHIVO_95}"
    )

log(
    "Complemento de 95 seleccionado desde el "
    "punto de control congelado."
)
log(f"Ruta: {ARCHIVO_95}")
log(f"SHA-256: {hash_archivo_95_real}")
log()

log("Fuentes operativas localizadas:")
log(f"1. Carga principal:\n   {ARCHIVO_4070}")
log(f"2. Complemento 95:\n   {ARCHIVO_95}")
log(f"3. Rectificación 30:\n   {ARCHIVO_30}")
log()


# ============================================================
# LECTURA DE FUENTES OPERATIVAS
# ============================================================

df_4070, encoding_4070 = leer_csv_32(
    ARCHIVO_4070
)

df_95, encoding_95 = leer_csv_32(
    ARCHIVO_95
)

df_30, encoding_30 = leer_csv_32(
    ARCHIVO_30
)

if len(df_4070) != 4070:
    raise SystemExit(
        f"\nERROR: la carga principal contiene "
        f"{len(df_4070)} filas y no 4.070."
    )

if len(df_95) != 95:
    raise SystemExit(
        f"\nERROR: el complemento contiene "
        f"{len(df_95)} filas y no 95."
    )

if len(df_30) != 30:
    raise SystemExit(
        f"\nERROR: la rectificación contiene "
        f"{len(df_30)} filas y no 30."
    )

log("Lectura de fuentes operativas completada:")
log(
    f" - Principal: {len(df_4070)} filas, "
    f"{df_4070.shape[1] - 4} columnas MU, "
    f"encoding {encoding_4070}"
)
log(
    f" - Complemento: {len(df_95)} filas, "
    f"{df_95.shape[1] - 4} columnas MU, "
    f"encoding {encoding_95}"
)
log(
    f" - Rectificación: {len(df_30)} filas, "
    f"{df_30.shape[1] - 4} columnas MU, "
    f"encoding {encoding_30}"
)
log()


# ============================================================
# DESCUBRIMIENTO DE FUENTES CODCLI
# ============================================================

log("Descubriendo fuentes activas para reconstruir CODCLI...")

fuentes_codcli = descubrir_fuentes_codcli()

log(
    f"Archivos candidatos para catálogo CODCLI: "
    f"{len(fuentes_codcli)}"
)

catalogo_codcli, inventario_fuentes = (
    construir_catalogo_codcli(
        fuentes_codcli
    )
)

log(
    f"Registros de evidencia CODCLI encontrados: "
    f"{len(catalogo_codcli)}"
)

log(
    f"CODCLI distintos en catálogo: "
    f"{catalogo_codcli['CODCLI'].nunique()}"
)

log(
    f"RUT distintos con evidencia CODCLI: "
    f"{catalogo_codcli.loc[
        catalogo_codcli['RUT_NORM'].ne(''),
        'RUT_NORM'
    ].nunique()}"
)

log()


# ============================================================
# ASIGNACIÓN CODCLI A LOS 95 Y LOS 30
# ============================================================

log(
    "Asignando CODCLI al complemento de 95 "
    "mediante RUT + oferta SIES exacta..."
)

asignados_95, conflictos_95 = asignar_codcli(
    df_95,
    catalogo_codcli,
    "COMPLEMENTO_95",
)

log(
    "Asignando CODCLI a la rectificación de 30 "
    "mediante RUT + oferta SIES exacta..."
)

asignados_30, conflictos_30 = asignar_codcli(
    df_30,
    catalogo_codcli,
    "RECTIFICACION_30",
)

conflictos_asignacion = pd.concat(
    [
        conflictos_95,
        conflictos_30,
    ],
    ignore_index=True,
)

SALIDA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

if not conflictos_asignacion.empty:
    archivo_conflictos = (
        SALIDA_DIR
        / "CONFLICTOS_ASIGNACION_CODCLI.xlsx"
    )

    with pd.ExcelWriter(
        archivo_conflictos,
        engine="openpyxl",
    ) as writer:
        conflictos_asignacion.to_excel(
            writer,
            sheet_name="CONFLICTOS",
            index=False,
        )

        catalogo_codcli.to_excel(
            writer,
            sheet_name="CATALOGO_CODCLI",
            index=False,
        )

        inventario_fuentes.to_excel(
            writer,
            sheet_name="FUENTES_REVISADAS",
            index=False,
        )

    log()
    log("=" * 120)
    log("BLOQUEO: EXISTEN FILAS SIN CODCLI DEMOSTRADO")
    log("=" * 120)
    log(
        conflictos_asignacion.to_string(
            index=False
        )
    )
    log()
    log(f"Archivo de revisión:\n{archivo_conflictos}")

    ARCHIVO_LOG.write_text(
        "\n".join(MENSAJES_LOG),
        encoding="utf-8",
    )

    raise SystemExit(
        "\nNo se creó el consolidado. "
        "Primero deben resolverse los conflictos CODCLI."
    )

log(
    f"CODCLI asignados al complemento: "
    f"{len(asignados_95)}/{len(df_95)}"
)

log(
    f"CODCLI asignados a la rectificación: "
    f"{len(asignados_30)}/{len(df_30)}"
)

log()


# ============================================================
# VALIDACIÓN INTERNA DE CODCLI
# ============================================================

conflictos_internos_95 = validar_codcli_interno(
    asignados_95,
    "COMPLEMENTO_95",
)

conflictos_internos_30 = validar_codcli_interno(
    asignados_30,
    "RECTIFICACION_30",
)

if (
    not conflictos_internos_95.empty
    or not conflictos_internos_30.empty
):
    archivo_conflictos_internos = (
        SALIDA_DIR
        / "CONFLICTOS_CODCLI_INTERNOS.xlsx"
    )

    with pd.ExcelWriter(
        archivo_conflictos_internos,
        engine="openpyxl",
    ) as writer:
        conflictos_internos_95.to_excel(
            writer,
            sheet_name="CONFLICTOS_95",
            index=False,
        )

        conflictos_internos_30.to_excel(
            writer,
            sheet_name="CONFLICTOS_30",
            index=False,
        )

        asignados_95.to_excel(
            writer,
            sheet_name="DETALLE_95",
            index=False,
        )

        asignados_30.to_excel(
            writer,
            sheet_name="DETALLE_30",
            index=False,
        )

    ARCHIVO_LOG.write_text(
        "\n".join(MENSAJES_LOG),
        encoding="utf-8",
    )

    raise SystemExit(
        "\nNo se creó el consolidado porque existen "
        "CODCLI internos repetidos o conflictivos."
    )


# ============================================================
# COMPARACIÓN DE LOS 30 CONTRA LOS 95
# ============================================================

codcli_95 = set(
    asignados_95["CODCLI"]
    .astype(str)
    .str.strip()
)

llaves_95 = set(
    asignados_95["LLAVE_RUT_OFERTA"]
    .astype(str)
    .str.strip()
)

filas_95 = set(
    asignados_95["FILA_32"]
    .astype(str)
)

mapa_95_por_codcli = (
    asignados_95[
        [
            "CODCLI",
            "RUT_NORM",
            "OFERTA_SIES",
            "LLAVE_RUT_OFERTA",
            "FILA_32",
            "VIG",
        ]
    ]
    .drop_duplicates(
        subset=["CODCLI"]
    )
    .set_index("CODCLI")
    .to_dict("index")
)

comparacion_30 = asignados_30.copy()

comparacion_30["CODCLI_YA_EN_95"] = (
    comparacion_30["CODCLI"]
    .isin(codcli_95)
)

comparacion_30["RUT_OFERTA_YA_EN_95"] = (
    comparacion_30["LLAVE_RUT_OFERTA"]
    .isin(llaves_95)
)

comparacion_30["FILA_EXACTA_YA_EN_95"] = (
    comparacion_30["FILA_32"]
    .isin(filas_95)
)

comparacion_30[
    "CODCLI_MISMO_RUT_EN_95"
] = False

comparacion_30[
    "CODCLI_MISMA_OFERTA_EN_95"
] = False

comparacion_30[
    "CODCLI_MISMA_FILA_EN_95"
] = False

comparacion_30[
    "RUT_EN_95_DEL_CODCLI"
] = ""

comparacion_30[
    "OFERTA_EN_95_DEL_CODCLI"
] = ""

comparacion_30[
    "VIG_EN_95_DEL_CODCLI"
] = ""

for indice, fila in comparacion_30.iterrows():
    codcli = fila["CODCLI"]

    if codcli not in mapa_95_por_codcli:
        continue

    evidencia_95 = mapa_95_por_codcli[codcli]

    comparacion_30.at[
        indice,
        "CODCLI_MISMO_RUT_EN_95",
    ] = (
        evidencia_95["RUT_NORM"]
        == fila["RUT_NORM"]
    )

    comparacion_30.at[
        indice,
        "CODCLI_MISMA_OFERTA_EN_95",
    ] = (
        evidencia_95["OFERTA_SIES"]
        == fila["OFERTA_SIES"]
    )

    comparacion_30.at[
        indice,
        "CODCLI_MISMA_FILA_EN_95",
    ] = (
        evidencia_95["FILA_32"]
        == fila["FILA_32"]
    )

    comparacion_30.at[
        indice,
        "RUT_EN_95_DEL_CODCLI",
    ] = evidencia_95["RUT_NORM"]

    comparacion_30.at[
        indice,
        "OFERTA_EN_95_DEL_CODCLI",
    ] = evidencia_95["OFERTA_SIES"]

    comparacion_30.at[
        indice,
        "VIG_EN_95_DEL_CODCLI",
    ] = evidencia_95["VIG"]


# ============================================================
# COMPARACIÓN CONTRA LOS 4.070
# ============================================================

llaves_4070 = set(
    df_4070["LLAVE_RUT_OFERTA"]
    .astype(str)
    .str.strip()
)

filas_4070 = set(
    df_4070["FILA_32"]
    .astype(str)
)

ruts_4070 = set(
    df_4070["RUT_NORM"]
    .astype(str)
    .str.strip()
)

comparacion_30[
    "RUT_YA_EN_4070"
] = comparacion_30[
    "RUT_NORM"
].isin(ruts_4070)

comparacion_30[
    "RUT_OFERTA_YA_EN_4070"
] = comparacion_30[
    "LLAVE_RUT_OFERTA"
].isin(llaves_4070)

comparacion_30[
    "FILA_EXACTA_YA_EN_4070"
] = comparacion_30[
    "FILA_32"
].isin(filas_4070)


# ============================================================
# CLASIFICACIÓN METODOLÓGICA DE LOS 30
# ============================================================

def clasificar_fila_30(fila: pd.Series) -> str:
    if fila["CODCLI_YA_EN_95"]:
        if not fila["CODCLI_MISMO_RUT_EN_95"]:
            return (
                "CONFLICTO_CODCLI_YA_EN_95_CON_RUT_DISTINTO"
            )

        if not fila["CODCLI_MISMA_OFERTA_EN_95"]:
            return (
                "CONFLICTO_CODCLI_YA_EN_95_CON_OFERTA_DISTINTA"
            )

        if fila["CODCLI_MISMA_FILA_EN_95"]:
            return (
                "CODCLI_YA_INCLUIDO_EXACTAMENTE_EN_95"
            )

        return (
            "CODCLI_YA_EN_95_CON_MISMO_RUT_Y_OFERTA "
            "PERO_OTROS_DATOS_DISTINTOS"
        )

    if fila["RUT_OFERTA_YA_EN_95"]:
        return (
            "CODCLI_DISTINTO_PERO_RUT_Y_OFERTA_YA_EN_95"
        )

    if fila["RUT_OFERTA_YA_EN_4070"]:
        return (
            "CODCLI_NUEVO_PERO_RUT_Y_OFERTA_YA_REPRESENTADOS "
            "EN_LA_CARGA_4070"
        )

    return (
        "CODCLI_NUEVO_Y_OFERTA_NO_REPRESENTADA"
    )


comparacion_30["CLASIFICACION"] = (
    comparacion_30.apply(
        clasificar_fila_30,
        axis=1,
    )
)


# ============================================================
# BLOQUEO DE CONFLICTOS MATERIALES
# ============================================================

clasificaciones_conflictivas = {
    "CONFLICTO_CODCLI_YA_EN_95_CON_RUT_DISTINTO",
    "CONFLICTO_CODCLI_YA_EN_95_CON_OFERTA_DISTINTA",
    (
        "CODCLI_YA_EN_95_CON_MISMO_RUT_Y_OFERTA "
        "PERO_OTROS_DATOS_DISTINTOS"
    ),
}

conflictos_codcli_95_30 = comparacion_30.loc[
    comparacion_30["CLASIFICACION"].isin(
        clasificaciones_conflictivas
    )
].copy()

if not conflictos_codcli_95_30.empty:
    archivo_conflictos_95_30 = (
        SALIDA_DIR
        / "CONFLICTOS_CODCLI_95_VS_30.xlsx"
    )

    with pd.ExcelWriter(
        archivo_conflictos_95_30,
        engine="openpyxl",
    ) as writer:
        conflictos_codcli_95_30.to_excel(
            writer,
            sheet_name="CONFLICTOS",
            index=False,
        )

        asignados_95.to_excel(
            writer,
            sheet_name="COMPLEMENTO_95",
            index=False,
        )

        asignados_30.to_excel(
            writer,
            sheet_name="RECTIFICACION_30",
            index=False,
        )

    log()
    log("=" * 120)
    log("BLOQUEO: CONFLICTOS MATERIALES ENTRE LOS 95 Y LOS 30")
    log("=" * 120)
    log(
        conflictos_codcli_95_30[
            [
                "CODCLI",
                "RUT_NORM",
                "OFERTA_SIES",
                "RUT_EN_95_DEL_CODCLI",
                "OFERTA_EN_95_DEL_CODCLI",
                "CLASIFICACION",
            ]
        ].to_string(
            index=False
        )
    )
    log()
    log(
        f"Archivo de revisión:\n"
        f"{archivo_conflictos_95_30}"
    )

    ARCHIVO_LOG.write_text(
        "\n".join(MENSAJES_LOG),
        encoding="utf-8",
    )

    raise SystemExit(
        "\nNo se creó el consolidado porque existen "
        "CODCLI con antecedentes incompatibles."
    )


# ============================================================
# DETERMINACIÓN DE LOS REGISTROS REALMENTE NUEVOS
# ============================================================

clasificacion_inclusion = (
    "CODCLI_NUEVO_Y_OFERTA_NO_REPRESENTADA"
)

nuevos_30 = comparacion_30.loc[
    comparacion_30["CLASIFICACION"].eq(
        clasificacion_inclusion
    )
].copy()

excluidos_30 = comparacion_30.loc[
    ~comparacion_30["CLASIFICACION"].eq(
        clasificacion_inclusion
    )
].copy()

log("=" * 120)
log("CLASIFICACIÓN DE LOS 30 REGISTROS")
log("=" * 120)

resumen_clasificacion = (
    comparacion_30.groupby(
        "CLASIFICACION",
        dropna=False,
    )
    .size()
    .reset_index(name="CANTIDAD")
    .sort_values(
        [
            "CLASIFICACION",
        ],
        kind="stable",
    )
    .reset_index(drop=True)
)

log(
    resumen_clasificacion.to_string(
        index=False
    )
)

log()
log(
    f"Registros de los 30 que serán incluidos: "
    f"{len(nuevos_30)}"
)

log(
    f"Registros de los 30 que serán excluidos: "
    f"{len(excluidos_30)}"
)

log()


# ============================================================
# CONSOLIDACIÓN OPERATIVA
# ============================================================

df_4070_export = df_4070[
    COLUMNAS_MU
].copy()

df_95_export = asignados_95[
    COLUMNAS_MU
].copy()

df_30_export = nuevos_30[
    COLUMNAS_MU
].copy()

consolidado = pd.concat(
    [
        df_4070_export,
        df_95_export,
        df_30_export,
    ],
    ignore_index=True,
)

if consolidado.shape[1] != 32:
    raise SystemExit(
        f"\nERROR: el consolidado tiene "
        f"{consolidado.shape[1]} columnas y no 32."
    )

consolidado_control = consolidado.copy()

for columna in COLUMNAS_MU:
    consolidado_control[columna] = (
        consolidado_control[columna]
        .astype(str)
        .str.strip()
    )

consolidado_control["RUT_NORM"] = [
    normalizar_rut(numero, dv)
    for numero, dv in zip(
        consolidado_control["N_DOC"],
        consolidado_control["DV"],
    )
]

consolidado_control["OFERTA_SIES"] = (
    construir_oferta(
        consolidado_control
    )
)

consolidado_control["LLAVE_RUT_OFERTA"] = (
    consolidado_control["RUT_NORM"]
    + "|"
    + consolidado_control["OFERTA_SIES"]
)

consolidado_control["FILA_32"] = (
    consolidado_control[COLUMNAS_MU]
    .astype(str)
    .agg("|".join, axis=1)
)


# ============================================================
# CONTROLES DEL CONSOLIDADO
# ============================================================

duplicados_exactos_final = (
    consolidado_control.loc[
        consolidado_control.duplicated(
            subset=["FILA_32"],
            keep=False,
        )
    ].copy()
)

duplicados_rut_oferta_final = (
    consolidado_control.loc[
        consolidado_control.duplicated(
            subset=["LLAVE_RUT_OFERTA"],
            keep=False,
        )
    ].copy()
)

if not duplicados_exactos_final.empty:
    archivo_duplicados_exactos = (
        SALIDA_DIR
        / "BLOQUEO_DUPLICADOS_EXACTOS_FINAL.xlsx"
    )

    duplicados_exactos_final.to_excel(
        archivo_duplicados_exactos,
        index=False,
    )

    raise SystemExit(
        f"\nERROR: el consolidado contiene "
        f"{len(duplicados_exactos_final)} filas "
        "involucradas en duplicados exactos.\n"
        f"Revisar:\n{archivo_duplicados_exactos}"
    )

if not duplicados_rut_oferta_final.empty:
    archivo_duplicados_oferta = (
        SALIDA_DIR
        / "BLOQUEO_DUPLICADOS_RUT_OFERTA_FINAL.xlsx"
    )

    duplicados_rut_oferta_final.to_excel(
        archivo_duplicados_oferta,
        index=False,
    )

    raise SystemExit(
        f"\nERROR: el consolidado contiene "
        f"{len(duplicados_rut_oferta_final)} filas "
        "involucradas en duplicados RUT-oferta.\n"
        f"Revisar:\n{archivo_duplicados_oferta}"
    )

valores_vigencia = set(
    consolidado["VIG"]
    .astype(str)
    .str.strip()
)

vigencias_invalidas = sorted(
    valores_vigencia - {"0", "1", "2"}
)

if vigencias_invalidas:
    raise SystemExit(
        "\nERROR: existen valores VIG fuera de "
        "0, 1 y 2:\n"
        + "\n".join(vigencias_invalidas)
    )


# ============================================================
# ESCRITURA DEL CSV FINAL
# ============================================================

consolidado.to_csv(
    ARCHIVO_FINAL,
    sep=";",
    header=False,
    index=False,
    encoding="utf-8",
    lineterminator="\n",
)

relectura, encoding_relectura = leer_csv_32(
    ARCHIVO_FINAL
)

if len(relectura) != len(consolidado):
    raise SystemExit(
        "\nERROR: la relectura física del CSV "
        "cambió la cantidad de filas."
    )

if relectura[COLUMNAS_MU].shape[1] != 32:
    raise SystemExit(
        "\nERROR: la relectura física del CSV "
        "no conserva las 32 columnas."
    )

comparacion_fisica = (
    relectura[COLUMNAS_MU]
    .astype(str)
    .reset_index(drop=True)
    .eq(
        consolidado[COLUMNAS_MU]
        .astype(str)
        .reset_index(drop=True)
    )
)

diferencias_relectura = int(
    (~comparacion_fisica)
    .to_numpy()
    .sum()
)

if diferencias_relectura != 0:
    raise SystemExit(
        f"\nERROR: existen "
        f"{diferencias_relectura} diferencias "
        "entre el consolidado en memoria y el CSV físico."
    )


# ============================================================
# RESÚMENES PARA EL EXCEL AUDITABLE
# ============================================================

resumen_origen = pd.DataFrame(
    [
        {
            "ORIGEN": "CARGA_PRINCIPAL_4070",
            "FILAS_DISPONIBLES": len(df_4070),
            "FILAS_INCLUIDAS": len(df_4070),
            "FILAS_EXCLUIDAS": 0,
            "CODCLI_IDENTIFICADOS": (
                "NO_PRESENTE_EN_CSV_MU"
            ),
        },
        {
            "ORIGEN": "COMPLEMENTO_95",
            "FILAS_DISPONIBLES": len(asignados_95),
            "FILAS_INCLUIDAS": len(asignados_95),
            "FILAS_EXCLUIDAS": 0,
            "CODCLI_IDENTIFICADOS": (
                asignados_95["CODCLI"].nunique()
            ),
        },
        {
            "ORIGEN": "RECTIFICACION_30",
            "FILAS_DISPONIBLES": len(comparacion_30),
            "FILAS_INCLUIDAS": len(nuevos_30),
            "FILAS_EXCLUIDAS": len(excluidos_30),
            "CODCLI_IDENTIFICADOS": (
                comparacion_30["CODCLI"].nunique()
            ),
        },
        {
            "ORIGEN": "TOTAL_CONSOLIDADO",
            "FILAS_DISPONIBLES": (
                len(df_4070)
                + len(asignados_95)
                + len(comparacion_30)
            ),
            "FILAS_INCLUIDAS": len(consolidado),
            "FILAS_EXCLUIDAS": len(excluidos_30),
            "CODCLI_IDENTIFICADOS": "",
        },
    ]
)

resumen_vigencia = (
    consolidado.groupby(
        "VIG",
        dropna=False,
    )
    .size()
    .reset_index(name="FILAS")
    .sort_values(
        "VIG",
        kind="stable",
    )
    .reset_index(drop=True)
)

controles = pd.DataFrame(
    [
        {
            "CONTROL": "FILAS_CARGA_PRINCIPAL",
            "RESULTADO": len(df_4070),
            "ESPERADO": 4070,
            "ESTADO": (
                "OK"
                if len(df_4070) == 4070
                else "ERROR"
            ),
        },
        {
            "CONTROL": "FILAS_COMPLEMENTO_95",
            "RESULTADO": len(asignados_95),
            "ESPERADO": 95,
            "ESTADO": (
                "OK"
                if len(asignados_95) == 95
                else "ERROR"
            ),
        },
        {
            "CONTROL": "FILAS_RECTIFICACION_ANALIZADAS",
            "RESULTADO": len(comparacion_30),
            "ESPERADO": 30,
            "ESTADO": (
                "OK"
                if len(comparacion_30) == 30
                else "ERROR"
            ),
        },
        {
            "CONTROL": "CODCLI_SIN_ASIGNAR_COMPLEMENTO",
            "RESULTADO": len(conflictos_95),
            "ESPERADO": 0,
            "ESTADO": (
                "OK"
                if len(conflictos_95) == 0
                else "ERROR"
            ),
        },
        {
            "CONTROL": "CODCLI_SIN_ASIGNAR_RECTIFICACION",
            "RESULTADO": len(conflictos_30),
            "ESPERADO": 0,
            "ESTADO": (
                "OK"
                if len(conflictos_30) == 0
                else "ERROR"
            ),
        },
        {
            "CONTROL": "REGISTROS_30_REALMENTE_NUEVOS",
            "RESULTADO": len(nuevos_30),
            "ESPERADO": "DINAMICO",
            "ESTADO": "OK",
        },
        {
            "CONTROL": "REGISTROS_30_EXCLUIDOS",
            "RESULTADO": len(excluidos_30),
            "ESPERADO": "DINAMICO",
            "ESTADO": "OK",
        },
        {
            "CONTROL": "TOTAL_FILAS_FINAL",
            "RESULTADO": len(consolidado),
            "ESPERADO": (
                4070
                + 95
                + len(nuevos_30)
            ),
            "ESTADO": (
                "OK"
                if len(consolidado)
                == 4070 + 95 + len(nuevos_30)
                else "ERROR"
            ),
        },
        {
            "CONTROL": "TOTAL_COLUMNAS_FINAL",
            "RESULTADO": consolidado.shape[1],
            "ESPERADO": 32,
            "ESTADO": (
                "OK"
                if consolidado.shape[1] == 32
                else "ERROR"
            ),
        },
        {
            "CONTROL": "DUPLICADOS_EXACTOS_FINAL",
            "RESULTADO": len(
                duplicados_exactos_final
            ),
            "ESPERADO": 0,
            "ESTADO": (
                "OK"
                if duplicados_exactos_final.empty
                else "ERROR"
            ),
        },
        {
            "CONTROL": "DUPLICADOS_RUT_OFERTA_FINAL",
            "RESULTADO": len(
                duplicados_rut_oferta_final
            ),
            "ESPERADO": 0,
            "ESTADO": (
                "OK"
                if duplicados_rut_oferta_final.empty
                else "ERROR"
            ),
        },
        {
            "CONTROL": "DIFERENCIAS_CSV_VS_RELECTURA",
            "RESULTADO": diferencias_relectura,
            "ESPERADO": 0,
            "ESTADO": (
                "OK"
                if diferencias_relectura == 0
                else "ERROR"
            ),
        },
        {
            "CONTROL": "FUENTES_ORIGINALES_MODIFICADAS",
            "RESULTADO": "NO",
            "ESPERADO": "NO",
            "ESTADO": "OK",
        },
    ]
)


# ============================================================
# TRAZABILIDAD FINAL
# ============================================================

trazabilidad_4070 = pd.DataFrame(
    {
        "ORIGEN_CARGA": (
            ["CARGA_PRINCIPAL_4070"]
            * len(df_4070)
        ),
        "CODCLI": [""] * len(df_4070),
        "RUT_NORM": df_4070["RUT_NORM"],
        "OFERTA_SIES": df_4070["OFERTA_SIES"],
        "CLASIFICACION": (
            ["BASE_PRINCIPAL_CONSERVADA"]
            * len(df_4070)
        ),
        "INCLUIDO_FINAL": ["SI"] * len(df_4070),
    }
)

trazabilidad_95 = (
    asignados_95[
        [
            "ORIGEN_CARGA",
            "CODCLI",
            "RUT_NORM",
            "OFERTA_SIES",
        ]
    ]
    .copy()
)

trazabilidad_95["CLASIFICACION"] = (
    "COMPLEMENTO_95_CONSERVADO"
)

trazabilidad_95["INCLUIDO_FINAL"] = "SI"

trazabilidad_30 = (
    comparacion_30[
        [
            "ORIGEN_CARGA",
            "CODCLI",
            "RUT_NORM",
            "OFERTA_SIES",
            "CLASIFICACION",
        ]
    ]
    .copy()
)

trazabilidad_30["INCLUIDO_FINAL"] = (
    trazabilidad_30["CLASIFICACION"]
    .eq(clasificacion_inclusion)
    .map(
        {
            True: "SI",
            False: "NO",
        }
    )
)

trazabilidad_final = pd.concat(
    [
        trazabilidad_4070,
        trazabilidad_95,
        trazabilidad_30,
    ],
    ignore_index=True,
)


# ============================================================
# EXCEL AUDITABLE
# ============================================================

with pd.ExcelWriter(
    ARCHIVO_EXCEL,
    engine="openpyxl",
) as writer:
    resumen_origen.to_excel(
        writer,
        sheet_name="00_RESUMEN",
        index=False,
    )

    resumen_vigencia.to_excel(
        writer,
        sheet_name="01_VIGENCIA_FINAL",
        index=False,
    )

    resumen_clasificacion.to_excel(
        writer,
        sheet_name="02_CLASIFICACION_30",
        index=False,
    )

    comparacion_30.to_excel(
        writer,
        sheet_name="03_DETALLE_30",
        index=False,
    )

    nuevos_30.to_excel(
        writer,
        sheet_name="04_30_INCLUIDOS",
        index=False,
    )

    excluidos_30.to_excel(
        writer,
        sheet_name="05_30_EXCLUIDOS",
        index=False,
    )

    asignados_95.to_excel(
        writer,
        sheet_name="06_COMPLEMENTO_95",
        index=False,
    )

    consolidado.to_excel(
        writer,
        sheet_name="07_CONSOLIDADO_32",
        index=False,
    )

    trazabilidad_final.to_excel(
        writer,
        sheet_name="08_TRAZABILIDAD",
        index=False,
    )

    controles.to_excel(
        writer,
        sheet_name="09_CONTROLES",
        index=False,
    )

    catalogo_codcli.to_excel(
        writer,
        sheet_name="10_CATALOGO_CODCLI",
        index=False,
    )

    inventario_fuentes.to_excel(
        writer,
        sheet_name="11_FUENTES_REVISADAS",
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

            hoja.column_dimensions[
                letra
            ].width = min(
                max(ancho + 2, 12),
                50,
            )


# ============================================================
# MANIFIESTO
# ============================================================

fin = datetime.now()

manifiesto = {
    "proceso": "Matrícula Unificada 2026",
    "subproyecto": (
        "Consolidación de carga principal, "
        "complemento y rectificación multicodcli"
    ),
    "fecha_inicio": inicio.isoformat(),
    "fecha_fin": fin.isoformat(),
    "duracion_segundos": (
        fin - inicio
    ).total_seconds(),
    "metodologia": {
        "unidad_principal": "CODCLI",
        "regla_asignacion_codcli": (
            "Coincidencia exacta de RUT normalizado "
            "y oferta SIES"
        ),
        "oferta_sies": (
            "COD_SED + COD_CAR + MODALIDAD + "
            "JOR + VERSION"
        ),
        "regla_inclusion_rectificacion": (
            "CODCLI nuevo y oferta no representada "
            "en la carga principal ni en el complemento"
        ),
        "regla_rut": (
            "Un RUT repetido no se considera por sí "
            "solo un duplicado técnico"
        ),
    },
    "fuentes": {
        "carga_principal": {
            "ruta": str(ARCHIVO_4070),
            "filas": len(df_4070),
            "columnas": 32,
            "encoding": encoding_4070,
            "sha256": sha256(ARCHIVO_4070),
        },
        "complemento_95": {
            "ruta": str(ARCHIVO_95),
            "filas": len(df_95),
            "columnas": 32,
            "encoding": encoding_95,
            "sha256": sha256(ARCHIVO_95),
        },
        "rectificacion_30": {
            "ruta": str(ARCHIVO_30),
            "filas": len(df_30),
            "columnas": 32,
            "encoding": encoding_30,
            "sha256": sha256(ARCHIVO_30),
        },
    },
    "resultado": {
        "filas_carga_principal": len(df_4070),
        "filas_complemento": len(asignados_95),
        "filas_rectificacion_analizadas": (
            len(comparacion_30)
        ),
        "filas_rectificacion_incluidas": (
            len(nuevos_30)
        ),
        "filas_rectificacion_excluidas": (
            len(excluidos_30)
        ),
        "total_final": len(consolidado),
        "columnas_finales": consolidado.shape[1],
        "duplicados_exactos_finales": (
            len(duplicados_exactos_final)
        ),
        "duplicados_rut_oferta_finales": (
            len(duplicados_rut_oferta_final)
        ),
        "diferencias_csv_relectura": (
            diferencias_relectura
        ),
        "encoding_relectura": (
            encoding_relectura
        ),
    },
    "salidas": {
        "csv": {
            "ruta": str(ARCHIVO_FINAL),
            "sha256": sha256(ARCHIVO_FINAL),
        },
        "excel": {
            "ruta": str(ARCHIVO_EXCEL),
            "sha256": sha256(ARCHIVO_EXCEL),
        },
        "log": {
            "ruta": str(ARCHIVO_LOG),
        },
    },
}

ARCHIVO_MANIFIESTO.write_text(
    json.dumps(
        manifiesto,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


# ============================================================
# COPIAS AL ESCRITORIO
# ============================================================

COPIA_CSV_ESCRITORIO = (
    ESCRITORIO
    / ARCHIVO_FINAL.name
)

COPIA_EXCEL_ESCRITORIO = (
    ESCRITORIO
    / ARCHIVO_EXCEL.name
)

COPIA_MANIFIESTO_ESCRITORIO = (
    ESCRITORIO
    / ARCHIVO_MANIFIESTO.name
)

shutil.copy2(
    ARCHIVO_FINAL,
    COPIA_CSV_ESCRITORIO,
)

shutil.copy2(
    ARCHIVO_EXCEL,
    COPIA_EXCEL_ESCRITORIO,
)

shutil.copy2(
    ARCHIVO_MANIFIESTO,
    COPIA_MANIFIESTO_ESCRITORIO,
)

if sha256(ARCHIVO_FINAL) != sha256(
    COPIA_CSV_ESCRITORIO
):
    raise SystemExit(
        "\nERROR: el hash de la copia CSV "
        "del Escritorio no coincide."
    )

if sha256(ARCHIVO_EXCEL) != sha256(
    COPIA_EXCEL_ESCRITORIO
):
    raise SystemExit(
        "\nERROR: el hash de la copia Excel "
        "del Escritorio no coincide."
    )

if sha256(ARCHIVO_MANIFIESTO) != sha256(
    COPIA_MANIFIESTO_ESCRITORIO
):
    raise SystemExit(
        "\nERROR: el hash de la copia del manifiesto "
        "del Escritorio no coincide."
    )


# ============================================================
# RESULTADO FINAL
# ============================================================

log()
log("=" * 120)
log("RESULTADO FINAL")
log("=" * 120)
log(f"Carga principal conservada: {len(df_4070)}")
log(f"Complemento conservado: {len(asignados_95)}")
log(
    f"Rectificación analizada: "
    f"{len(comparacion_30)}"
)
log(
    f"Rectificaciones realmente nuevas incluidas: "
    f"{len(nuevos_30)}"
)
log(
    f"Rectificaciones excluidas por estar "
    f"ya representadas: {len(excluidos_30)}"
)
log(f"TOTAL FINAL: {len(consolidado)}")
log(f"TOTAL COLUMNAS: {consolidado.shape[1]}")
log(
    f"Duplicados exactos finales: "
    f"{len(duplicados_exactos_final)}"
)
log(
    f"Duplicados RUT-oferta finales: "
    f"{len(duplicados_rut_oferta_final)}"
)
log(
    f"Diferencias CSV vs relectura física: "
    f"{diferencias_relectura}"
)
log()

log("=" * 120)
log("ARCHIVOS CREADOS")
log("=" * 120)
log(f"CSV final:\n{ARCHIVO_FINAL}")
log()
log(f"Excel auditable:\n{ARCHIVO_EXCEL}")
log()
log(f"Manifiesto:\n{ARCHIVO_MANIFIESTO}")
log()
log(f"Copia CSV Escritorio:\n{COPIA_CSV_ESCRITORIO}")
log()
log(
    f"Copia Excel Escritorio:\n"
    f"{COPIA_EXCEL_ESCRITORIO}"
)
log()
log(
    f"Copia manifiesto Escritorio:\n"
    f"{COPIA_MANIFIESTO_ESCRITORIO}"
)
log()

log("=" * 120)
log("HASHES")
log("=" * 120)
log(f"CSV: {sha256(ARCHIVO_FINAL)}")
log(f"Excel: {sha256(ARCHIVO_EXCEL)}")
log(f"Manifiesto: {sha256(ARCHIVO_MANIFIESTO)}")
log()

log("=" * 120)
log("CONTROLES SUPERADOS")
log("=" * 120)
log(
    "OK: la consolidación fue controlada por CODCLI."
)
log(
    "OK: el RUT repetido no fue utilizado por sí solo "
    "para excluir una matrícula."
)
log(
    "OK: cada CODCLI del complemento y de la "
    "rectificación fue vinculado a RUT y oferta SIES."
)
log(
    "OK: los 30 registros no fueron agregados "
    "automáticamente."
)
log(
    "OK: solo se incorporaron CODCLI nuevos cuya oferta "
    "no estaba representada."
)
log(
    "OK: el total final fue calculado desde la evidencia."
)
log(
    "OK: el CSV final contiene 32 columnas, "
    "sin encabezados y delimitadas por punto y coma."
)
log(
    "OK: no existen diferencias entre el CSV generado "
    "y su relectura física."
)
log(
    "OK: las fuentes originales no fueron modificadas."
)
log("=" * 120)

ARCHIVO_LOG.write_text(
    "\n".join(MENSAJES_LOG),
    encoding="utf-8",
)
