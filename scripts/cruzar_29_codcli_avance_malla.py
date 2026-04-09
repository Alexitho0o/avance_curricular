#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


# ============================================================
# CONTEXTO
# ============================================================

RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

CASOS_29 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "EXTRACCION_RUT_CODCLI_29_20260703_104251"
    / "02_RESULTADOS"
    / "01_REVISION_RUT_CODCLI_29.tsv"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"CRUCE_29_CODCLI_AVANCE_MALLA_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in (RESULTADOS, AUDITORIAS, REPORTES):
    carpeta.mkdir(parents=True, exist_ok=True)


# ============================================================
# UTILIDADES
# ============================================================

def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def norm_col(valor):
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(
        r"[^A-Z0-9]+",
        "_",
        texto,
    ).strip("_")


def norm_codigo(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"\s+", "", texto)


def norm_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(
        r"[^A-Z0-9]+",
        "",
        texto,
    )


def buscar_columna(df, opciones):
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    for opcion in opciones:
        clave = norm_col(opcion)

        if clave in mapa:
            return mapa[clave]

    return None


def unir_unicos(serie, normalizador=norm_codigo):
    valores = sorted({
        normalizador(valor)
        for valor in serie
        if normalizador(valor)
    })

    return " | ".join(valores)


def contar_unicos(serie, normalizador=norm_codigo):
    return len({
        normalizador(valor)
        for valor in serie
        if normalizador(valor)
    })


# ============================================================
# 1. LOCALIZAR LOS DOS ARCHIVOS XLS
# ============================================================

directorios_busqueda = [
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    RAIZ,
]

candidatos_xls = []

for directorio in directorios_busqueda:
    if not directorio.exists():
        continue

    candidatos_xls.extend(
        directorio.glob(
            "Avance de Malla03-07-2026*.xls"
        )
    )

# Resolver, eliminar duplicados y excluir archivos temporales.
archivos_xls = sorted({
    ruta.resolve()
    for ruta in candidatos_xls
    if ruta.is_file()
    and not ruta.name.startswith("~$")
})

if len(archivos_xls) < 2:
    raise RuntimeError(
        "No se localizaron los dos archivos XLS. "
        "Deben estar en Downloads, Desktop o dentro del "
        "repositorio con nombres que comiencen por "
        "'Avance de Malla03-07-2026'. "
        f"Encontrados: {len(archivos_xls)}"
    )

if len(archivos_xls) > 2:
    print(
        "Advertencia: se encontraron más de dos candidatos. "
        "Se utilizarán los dos archivos más recientes."
    )

archivos_xls = sorted(
    archivos_xls,
    key=lambda ruta: ruta.stat().st_mtime,
    reverse=True,
)[:2]

archivos_xls = sorted(
    archivos_xls,
    key=lambda ruta: ruta.name,
)


# ============================================================
# 2. VALIDAR FUENTE DE LOS 29 CASOS
# ============================================================

if not CASOS_29.exists():
    raise RuntimeError(
        f"No existe la fuente de los 29 casos: {CASOS_29}"
    )

casos = pd.read_csv(
    CASOS_29,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

if len(casos) != 29:
    raise RuntimeError(
        f"Se esperaban 29 casos y se encontraron "
        f"{len(casos)}."
    )

if casos["ID_FILA_5809"].duplicated().any():
    raise RuntimeError(
        "Existen ID_FILA_5809 duplicados."
    )

if "CODCLI" not in casos.columns:
    raise RuntimeError(
        "La fuente de los 29 casos no contiene CODCLI."
    )

casos["CODCLI_NORM"] = (
    casos["CODCLI"].map(norm_codigo)
)

if casos["CODCLI_NORM"].eq("").any():
    raise RuntimeError(
        "Existen casos sin CODCLI utilizable."
    )


# ============================================================
# 3. LEER TODAS LAS HOJAS DE LOS XLS
# ============================================================

filas_avance = []
inventario_hojas = []
inventario_columnas = []

for archivo in archivos_xls:
    try:
        libro = pd.ExcelFile(archivo)
    except ImportError as error:
        raise RuntimeError(
            "No fue posible leer el formato XLS porque falta "
            "la dependencia xlrd. Ejecuta:\n"
            "pip install xlrd\n"
            "y vuelve a correr el script."
        ) from error
    except Exception as error:
        raise RuntimeError(
            f"No fue posible abrir {archivo}: {error}"
        ) from error

    for hoja in libro.sheet_names:
        try:
            df = pd.read_excel(
                archivo,
                sheet_name=hoja,
                dtype=object,
            )
        except Exception as error:
            inventario_hojas.append({
                "ARCHIVO": str(archivo),
                "HOJA": hoja,
                "FILAS": 0,
                "COLUMNAS": 0,
                "ESTADO": "ERROR_LECTURA",
                "DETALLE": str(error),
            })
            continue

        df = df.dropna(
            axis=0,
            how="all",
        ).dropna(
            axis=1,
            how="all",
        )

        inventario_hojas.append({
            "ARCHIVO": str(archivo),
            "HOJA": hoja,
            "FILAS": len(df),
            "COLUMNAS": len(df.columns),
            "ESTADO": "LEIDA",
            "DETALLE": "",
        })

        for numero, columna in enumerate(
            df.columns,
            start=1,
        ):
            inventario_columnas.append({
                "ARCHIVO": str(archivo),
                "HOJA": hoja,
                "N_ORDEN": numero,
                "COLUMNA_ORIGINAL": str(columna),
                "COLUMNA_NORMALIZADA": norm_col(columna),
            })

        if df.empty:
            continue

        col_codcli = buscar_columna(
            df,
            [
                "CODCLI",
                "CODIGO_ALUMNO",
                "COD_ALUMNO",
                "CODIGO_ESTUDIANTE",
                "COD_ESTUDIANTE",
            ],
        )

        if not col_codcli:
            continue

        col_carrera = buscar_columna(
            df,
            [
                "CODCARPR",
                "CODCARR",
                "CODIGO_CARRERA",
                "COD_CARRERA",
                "CARRERA",
                "NOMBRE_CARRERA",
            ],
        )

        col_plan = buscar_columna(
            df,
            [
                "CODPESTUD",
                "PLAN_ESTUDIOS",
                "PLAN_DE_ESTUDIO",
                "CODIGO_PLAN",
                "PLAN",
            ],
        )

        col_periodo = buscar_columna(
            df,
            [
                "PERIODO",
                "NIVEL",
                "NIVEL_MALLA",
                "PERIODO_MALLA",
                "SEMESTRE",
                "TRIMESTRE",
            ],
        )

        col_anio = buscar_columna(
            df,
            [
                "ANO",
                "ANIO",
                "ANO_CURRICULAR",
                "ANIO_CURRICULAR",
                "ANO_MALLA",
                "ANIO_MALLA",
            ],
        )

        col_asignatura = buscar_columna(
            df,
            [
                "CODRAMO",
                "CODIGO_ASIGNATURA",
                "ASIGNATURA",
                "NOMBRE_ASIGNATURA",
                "RAMO",
            ],
        )

        bloque = pd.DataFrame({
            "FUENTE_ARCHIVO": archivo.name,
            "FUENTE_RUTA": str(archivo),
            "FUENTE_HOJA": hoja,
            "FILA_FUENTE": range(2, len(df) + 2),

            "CODCLI_AVANCE":
            df[col_codcli].map(norm_codigo),

            "CARRERA_AVANCE":
            (
                df[col_carrera].map(norm_codigo)
                if col_carrera
                else ""
            ),

            "PLAN_AVANCE":
            (
                df[col_plan].map(norm_codigo)
                if col_plan
                else ""
            ),

            "PERIODO_NIVEL_AVANCE":
            (
                df[col_periodo]
                if col_periodo
                else ""
            ),

            "ANIO_CURRICULAR_AVANCE":
            (
                df[col_anio]
                if col_anio
                else ""
            ),

            "ASIGNATURA_AVANCE":
            (
                df[col_asignatura].astype(str)
                if col_asignatura
                else ""
            ),
        })

        bloque["COLUMNA_CODCLI_ORIGEN"] = col_codcli
        bloque["COLUMNA_CARRERA_ORIGEN"] = (
            col_carrera or ""
        )
        bloque["COLUMNA_PLAN_ORIGEN"] = (
            col_plan or ""
        )
        bloque["COLUMNA_PERIODO_ORIGEN"] = (
            col_periodo or ""
        )
        bloque["COLUMNA_ANIO_ORIGEN"] = (
            col_anio or ""
        )

        bloque = bloque[
            bloque["CODCLI_AVANCE"].ne("")
        ].copy()

        filas_avance.append(bloque)


if not filas_avance:
    raise RuntimeError(
        "Ninguna hoja de los dos archivos contiene una "
        "columna CODCLI reconocible. No corresponde continuar."
    )

avance = pd.concat(
    filas_avance,
    ignore_index=True,
)

avance["PERIODO_NIVEL_NUM"] = pd.to_numeric(
    avance["PERIODO_NIVEL_AVANCE"],
    errors="coerce",
)

avance["ANIO_CURRICULAR_NUM"] = pd.to_numeric(
    avance["ANIO_CURRICULAR_AVANCE"],
    errors="coerce",
)


# ============================================================
# 4. FILTRAR SOLO LOS 29 CODCLI
# ============================================================

codcli_29 = set(
    casos["CODCLI_NORM"]
)

avance_29 = avance[
    avance["CODCLI_AVANCE"].isin(codcli_29)
].copy()


# ============================================================
# 5. RESUMIR EL AVANCE POR CODCLI
# ============================================================

if avance_29.empty:
    resumen_avance = pd.DataFrame(
        columns=[
            "CODCLI_NORM",
            "REGISTROS_AVANCE",
            "N_CARRERAS_AVANCE",
            "CARRERAS_AVANCE",
            "N_PLANES_AVANCE",
            "PLANES_AVANCE",
            "N_PERIODOS_AVANCE",
            "PERIODOS_AVANCE",
            "PERIODO_MAX_AVANCE",
            "N_ANIOS_AVANCE",
            "ANIOS_AVANCE",
            "ANIO_MAX_AVANCE",
            "FUENTES_AVANCE",
        ]
    )
else:
    resumen_avance = (
        avance_29.groupby(
            "CODCLI_AVANCE",
            dropna=False,
        )
        .agg(
            REGISTROS_AVANCE=(
                "CODCLI_AVANCE",
                "size",
            ),
            N_CARRERAS_AVANCE=(
                "CARRERA_AVANCE",
                contar_unicos,
            ),
            CARRERAS_AVANCE=(
                "CARRERA_AVANCE",
                unir_unicos,
            ),
            N_PLANES_AVANCE=(
                "PLAN_AVANCE",
                contar_unicos,
            ),
            PLANES_AVANCE=(
                "PLAN_AVANCE",
                unir_unicos,
            ),
            N_PERIODOS_AVANCE=(
                "PERIODO_NIVEL_NUM",
                lambda serie: (
                    pd.to_numeric(
                        serie,
                        errors="coerce",
                    )
                    .dropna()
                    .nunique()
                ),
            ),
            PERIODOS_AVANCE=(
                "PERIODO_NIVEL_NUM",
                lambda serie: " | ".join(
                    str(int(valor))
                    for valor in sorted(
                        set(
                            pd.to_numeric(
                                serie,
                                errors="coerce",
                            ).dropna()
                        )
                    )
                ),
            ),
            PERIODO_MAX_AVANCE=(
                "PERIODO_NIVEL_NUM",
                "max",
            ),
            N_ANIOS_AVANCE=(
                "ANIO_CURRICULAR_NUM",
                lambda serie: (
                    pd.to_numeric(
                        serie,
                        errors="coerce",
                    )
                    .dropna()
                    .nunique()
                ),
            ),
            ANIOS_AVANCE=(
                "ANIO_CURRICULAR_NUM",
                lambda serie: " | ".join(
                    str(int(valor))
                    for valor in sorted(
                        set(
                            pd.to_numeric(
                                serie,
                                errors="coerce",
                            ).dropna()
                        )
                    )
                ),
            ),
            ANIO_MAX_AVANCE=(
                "ANIO_CURRICULAR_NUM",
                "max",
            ),
            FUENTES_AVANCE=(
                "FUENTE_ARCHIVO",
                unir_unicos,
            ),
        )
        .reset_index()
        .rename(
            columns={
                "CODCLI_AVANCE": "CODCLI_NORM"
            }
        )
    )


# ============================================================
# 6. CRUCE CODCLI PRIMARIO
# ============================================================

resultado = casos.merge(
    resumen_avance,
    on="CODCLI_NORM",
    how="left",
    validate="one_to_one",
)

if len(resultado) != 29:
    raise RuntimeError(
        "El cruce alteró el universo de 29 estudiantes."
    )

resultado["REGISTROS_AVANCE"] = pd.to_numeric(
    resultado["REGISTROS_AVANCE"],
    errors="coerce",
).fillna(0).astype(int)

resultado["N_CARRERAS_AVANCE"] = pd.to_numeric(
    resultado["N_CARRERAS_AVANCE"],
    errors="coerce",
).fillna(0).astype(int)

resultado["N_PLANES_AVANCE"] = pd.to_numeric(
    resultado["N_PLANES_AVANCE"],
    errors="coerce",
).fillna(0).astype(int)


# ============================================================
# 7. CARRERA COMO SEGUNDA VARIABLE
# ============================================================

resultado["CARRERA_5809_CONTROL"] = (
    resultado["CODCARR_PLAN_VIGENTE"]
    .map(norm_codigo)
)

resultado["CARRERA_EVIDENCIA_CONTROL"] = (
    resultado["CODCARPR_EVIDENCIA"]
    .map(norm_codigo)
)

resultado["CARRERA_AVANCE_CONTROL"] = (
    resultado["CARRERAS_AVANCE"]
    .fillna("")
    .map(norm_codigo)
)

resultado["ESTADO_CRUCE_CODCLI_CARRERA"] = ""
resultado["INTERPRETACION_TECNICA"] = ""
resultado["PUEDE_ADECUARSE_NIVEL"] = "NO"
resultado["MOTIVO_PENDIENTE"] = ""


mask_no_encontrado = (
    resultado["REGISTROS_AVANCE"].eq(0)
)

resultado.loc[
    mask_no_encontrado,
    "ESTADO_CRUCE_CODCLI_CARRERA",
] = "CODCLI_NO_ENCONTRADO_EN_AVANCE"

resultado.loc[
    mask_no_encontrado,
    "MOTIVO_PENDIENTE",
] = (
    "El CODCLI no aparece en ninguno de los dos reportes "
    "de Avance de Malla."
)


mask_encontrado = (
    resultado["REGISTROS_AVANCE"].gt(0)
)

mask_una_carrera = (
    mask_encontrado
    & resultado["N_CARRERAS_AVANCE"].eq(1)
)

mask_varias_carreras = (
    mask_encontrado
    & resultado["N_CARRERAS_AVANCE"].gt(1)
)

mask_carrera_coincide_5809 = (
    mask_una_carrera
    & resultado["CARRERA_5809_CONTROL"].ne("")
    & resultado["CARRERA_AVANCE_CONTROL"].eq(
        resultado["CARRERA_5809_CONTROL"]
    )
)

mask_carrera_coincide_evidencia = (
    mask_una_carrera
    & resultado["CARRERA_EVIDENCIA_CONTROL"].ne("")
    & resultado["CARRERA_AVANCE_CONTROL"].eq(
        resultado["CARRERA_EVIDENCIA_CONTROL"]
    )
)

resultado.loc[
    mask_carrera_coincide_5809,
    "ESTADO_CRUCE_CODCLI_CARRERA",
] = "CODCLI_Y_CARRERA_5809_COINCIDEN"

resultado.loc[
    mask_carrera_coincide_5809,
    "INTERPRETACION_TECNICA",
] = (
    "El avance corresponde al CODCLI y a la carrera vigente "
    "informada en 5809."
)


mask_coincide_evidencia_no_5809 = (
    mask_carrera_coincide_evidencia
    & ~mask_carrera_coincide_5809
)

resultado.loc[
    mask_coincide_evidencia_no_5809,
    "ESTADO_CRUCE_CODCLI_CARRERA",
] = "CODCLI_COINCIDE_CARRERA_EVIDENCIA"

resultado.loc[
    mask_coincide_evidencia_no_5809,
    "INTERPRETACION_TECNICA",
] = (
    "El avance corresponde al CODCLI y coincide con la "
    "carrera histórica observada, pero no con la carrera "
    "vigente informada en 5809."
)


mask_carrera_distinta = (
    mask_una_carrera
    & ~mask_carrera_coincide_5809
    & ~mask_carrera_coincide_evidencia
)

resultado.loc[
    mask_carrera_distinta,
    "ESTADO_CRUCE_CODCLI_CARRERA",
] = "CODCLI_ENCONTRADO_CARRERA_NO_DEMOSTRADA"

resultado.loc[
    mask_carrera_distinta,
    "MOTIVO_PENDIENTE",
] = (
    "El CODCLI aparece en el avance, pero la carrera del "
    "reporte no coincide con las carreras de control."
)


resultado.loc[
    mask_varias_carreras,
    "ESTADO_CRUCE_CODCLI_CARRERA",
] = "CODCLI_CON_MULTIPLES_CARRERAS_EN_AVANCE"

resultado.loc[
    mask_varias_carreras,
    "MOTIVO_PENDIENTE",
] = (
    "El mismo CODCLI aparece asociado a más de una carrera "
    "en los reportes de Avance de Malla."
)


# ============================================================
# 8. VALIDAR SI EXISTE PERIODIZACIÓN EXPLÍCITA
# ============================================================

resultado["TIENE_PERIODO_AVANCE"] = (
    pd.to_numeric(
        resultado["N_PERIODOS_AVANCE"],
        errors="coerce",
    )
    .fillna(0)
    .gt(0)
)

resultado["TIENE_ANIO_EXPLICITO_AVANCE"] = (
    pd.to_numeric(
        resultado["N_ANIOS_AVANCE"],
        errors="coerce",
    )
    .fillna(0)
    .gt(0)
)

mask_adecuable = (
    resultado[
        "ESTADO_CRUCE_CODCLI_CARRERA"
    ].eq("CODCLI_Y_CARRERA_5809_COINCIDEN")
    & resultado["TIENE_PERIODO_AVANCE"]
    & resultado["TIENE_ANIO_EXPLICITO_AVANCE"]
)

resultado.loc[
    mask_adecuable,
    "PUEDE_ADECUARSE_NIVEL",
] = "SI_CON_MAPA_EXPLICITO"

resultado.loc[
    mask_adecuable,
    "INTERPRETACION_TECNICA",
] = (
    resultado.loc[
        mask_adecuable,
        "INTERPRETACION_TECNICA",
    ]
    + " El reporte contiene período y año curricular "
      "explícitos; puede construirse un mapa por CODCLI "
      "y carrera sin usar ceil(nivel/2)."
)


mask_sin_anio = (
    mask_encontrado
    & resultado["TIENE_PERIODO_AVANCE"]
    & ~resultado["TIENE_ANIO_EXPLICITO_AVANCE"]
)

resultado.loc[
    mask_sin_anio,
    "MOTIVO_PENDIENTE",
] = (
    resultado.loc[
        mask_sin_anio,
        "MOTIVO_PENDIENTE",
    ].fillna("")
    + " El reporte contiene período, pero no se detectó "
      "un año curricular explícito. No corresponde inferirlo."
)


# ============================================================
# 9. MAPA OBSERVADO PERÍODO → AÑO POR CODCLI
# ============================================================

mapa_periodizacion = avance_29[
    avance_29["PERIODO_NIVEL_NUM"].notna()
    & avance_29["ANIO_CURRICULAR_NUM"].notna()
].copy()

if not mapa_periodizacion.empty:
    mapa_periodizacion = (
        mapa_periodizacion[
            [
                "CODCLI_AVANCE",
                "CARRERA_AVANCE",
                "PLAN_AVANCE",
                "PERIODO_NIVEL_NUM",
                "ANIO_CURRICULAR_NUM",
                "FUENTE_ARCHIVO",
                "FUENTE_HOJA",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "CODCLI_AVANCE",
                "CARRERA_AVANCE",
                "PERIODO_NIVEL_NUM",
                "ANIO_CURRICULAR_NUM",
            ]
        )
    )

    conflictos_periodizacion = (
        mapa_periodizacion.groupby(
            [
                "CODCLI_AVANCE",
                "CARRERA_AVANCE",
                "PERIODO_NIVEL_NUM",
            ],
            dropna=False,
        )["ANIO_CURRICULAR_NUM"]
        .nunique()
        .reset_index(
            name="N_ANIOS_PARA_MISMO_PERIODO"
        )
    )

    conflictos_periodizacion = (
        conflictos_periodizacion[
            conflictos_periodizacion[
                "N_ANIOS_PARA_MISMO_PERIODO"
            ].gt(1)
        ]
        .copy()
    )
else:
    conflictos_periodizacion = pd.DataFrame(
        columns=[
            "CODCLI_AVANCE",
            "CARRERA_AVANCE",
            "PERIODO_NIVEL_NUM",
            "N_ANIOS_PARA_MISMO_PERIODO",
        ]
    )


# ============================================================
# 10. RESÚMENES
# ============================================================

resumen_estados = (
    resultado[
        "ESTADO_CRUCE_CODCLI_CARRERA"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)

resumen_adecuacion = (
    resultado[
        "PUEDE_ADECUARSE_NIVEL"
    ]
    .value_counts(dropna=False)
    .rename_axis("ADECUACION")
    .reset_index(name="CASOS")
)

resumen_kpi = pd.DataFrame([
    {
        "INDICADOR": "Casos analizados",
        "VALOR": 29,
    },
    {
        "INDICADOR": "CODCLI encontrados en avance",
        "VALOR": int(
            resultado[
                "REGISTROS_AVANCE"
            ].gt(0).sum()
        ),
    },
    {
        "INDICADOR": "CODCLI no encontrados",
        "VALOR": int(
            resultado[
                "REGISTROS_AVANCE"
            ].eq(0).sum()
        ),
    },
    {
        "INDICADOR": "CODCLI y carrera 5809 coinciden",
        "VALOR": int(
            resultado[
                "ESTADO_CRUCE_CODCLI_CARRERA"
            ].eq(
                "CODCLI_Y_CARRERA_5809_COINCIDEN"
            ).sum()
        ),
    },
    {
        "INDICADOR": "Adecuables con mapa explícito",
        "VALOR": int(
            resultado[
                "PUEDE_ADECUARSE_NIVEL"
            ].eq(
                "SI_CON_MAPA_EXPLICITO"
            ).sum()
        ),
    },
    {
        "INDICADOR": "Conflictos período-año",
        "VALOR": len(conflictos_periodizacion),
    },
    {
        "INDICADOR": "Niveles modificados",
        "VALOR": 0,
    },
])


# ============================================================
# 11. VALIDACIONES
# ============================================================

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_29",
        "RESULTADO": (
            "OK" if len(resultado) == 29 else "ERROR"
        ),
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "CODCLI_29_UNICOS",
        "RESULTADO": (
            "OK"
            if not casos[
                "CODCLI_NORM"
            ].duplicated().any()
            else "REVISAR"
        ),
        "DETALLE": int(
            casos[
                "CODCLI_NORM"
            ].duplicated().sum()
        ),
    },
    {
        "VALIDACION": "CONFLICTOS_PERIODO_ANIO",
        "RESULTADO": (
            "OK"
            if len(conflictos_periodizacion) == 0
            else "BLOQUEO"
        ),
        "DETALLE": len(conflictos_periodizacion),
    },
    {
        "VALIDACION": "NIVELES_MODIFICADOS",
        "RESULTADO": "OK",
        "DETALLE": 0,
    },
    {
        "VALIDACION": "FUENTES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "ARCHIVO_CARGA_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


# ============================================================
# 12. EXPORTACIÓN
# ============================================================

resultado.to_csv(
    RESULTADOS
    / "01_CRUCE_29_CODCLI_CARRERA.tsv",
    sep="\t",
    index=False,
)

avance_29.to_csv(
    RESULTADOS
    / "02_DETALLE_AVANCE_29_CODCLI.tsv",
    sep="\t",
    index=False,
)

mapa_periodizacion.to_csv(
    RESULTADOS
    / "03_MAPA_OBSERVADO_PERIODO_ANIO.tsv",
    sep="\t",
    index=False,
)

conflictos_periodizacion.to_csv(
    AUDITORIAS
    / "01_CONFLICTOS_PERIODO_ANIO.tsv",
    sep="\t",
    index=False,
)

pd.DataFrame(inventario_hojas).to_csv(
    AUDITORIAS
    / "02_INVENTARIO_HOJAS_XLS.tsv",
    sep="\t",
    index=False,
)

pd.DataFrame(inventario_columnas).to_csv(
    AUDITORIAS
    / "03_INVENTARIO_COLUMNAS_XLS.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "04_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


fuentes_df = pd.DataFrame([
    {
        "ROL": "CASOS_29",
        "RUTA": str(CASOS_29),
        "SHA256": sha256(CASOS_29),
        "TAMANO_BYTES": CASOS_29.stat().st_size,
    },
    *[
        {
            "ROL": f"AVANCE_MALLA_{numero}",
            "RUTA": str(ruta),
            "SHA256": sha256(ruta),
            "TAMANO_BYTES": ruta.stat().st_size,
        }
        for numero, ruta in enumerate(
            archivos_xls,
            start=1,
        )
    ],
])

fuentes_df.to_csv(
    AUDITORIAS
    / "05_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 13. EXCEL
# ============================================================

excel = (
    RESULTADOS
    / "CRUCE_29_CODCLI_AVANCE_MALLA.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_kpi.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resumen_estados.to_excel(
        writer,
        sheet_name="ESTADOS_CRUCE",
        index=False,
    )

    resumen_adecuacion.to_excel(
        writer,
        sheet_name="ADECUACION",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="CRUCE_29",
        index=False,
    )

    resultado[
        resultado[
            "PUEDE_ADECUARSE_NIVEL"
        ].eq("SI_CON_MAPA_EXPLICITO")
    ].to_excel(
        writer,
        sheet_name="ADECUABLES",
        index=False,
    )

    resultado[
        ~resultado[
            "PUEDE_ADECUARSE_NIVEL"
        ].eq("SI_CON_MAPA_EXPLICITO")
    ].to_excel(
        writer,
        sheet_name="REQUIEREN_REVISION",
        index=False,
    )

    mapa_periodizacion.to_excel(
        writer,
        sheet_name="MAPA_PERIODO_ANIO",
        index=False,
    )

    avance_29.to_excel(
        writer,
        sheet_name="DETALLE_AVANCE",
        index=False,
    )

    conflictos_periodizacion.to_excel(
        writer,
        sheet_name="CONFLICTOS_MAPA",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
        index=False,
    )

    fuentes_df.to_excel(
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
                55,
            )


# ============================================================
# 14. MANIFIESTO
# ============================================================

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "universo": 29,
    "llave_primaria": "CODCLI",
    "variable_secundaria": "CARRERA",
    "archivos_avance": [
        str(ruta)
        for ruta in archivos_xls
    ],
    "codcli_encontrados": int(
        resultado["REGISTROS_AVANCE"].gt(0).sum()
    ),
    "adecuables_mapa_explicito": int(
        resultado[
            "PUEDE_ADECUARSE_NIVEL"
        ].eq("SI_CON_MAPA_EXPLICITO").sum()
    ),
    "niveles_modificados": 0,
    "fuentes_modificadas": False,
    "archivo_final_carga_generado": False,
    "salida": str(SALIDA),
}

(SALIDA / "manifest_ejecucion.json").write_text(
    json.dumps(
        manifiesto,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)


# ============================================================
# 15. TERMINAL
# ============================================================

print()
print("=" * 104)
print("CRUCE DE LOS 29 CASOS CON AVANCE DE MALLA")
print("=" * 104)
print("Llave primaria: CODCLI")
print("Variable secundaria: carrera")
print()
print("ARCHIVOS UTILIZADOS")
print("-" * 104)

for archivo in archivos_xls:
    print(archivo)

print()
print("RESULTADO")
print("-" * 104)

for _, fila in resumen_estados.iterrows():
    print(
        f"{fila['ESTADO']}: "
        f"{fila['CASOS']}"
    )

print()
print(
    "CODCLI encontrados en Avance de Malla: "
    f"{resultado['REGISTROS_AVANCE'].gt(0).sum()}/29"
)
print(
    "Casos adecuables con período y año explícitos: "
    f"{resultado['PUEDE_ADECUARSE_NIVEL'].eq('SI_CON_MAPA_EXPLICITO').sum()}"
)
print(
    "Conflictos de período asociado a más de un año: "
    f"{len(conflictos_periodizacion)}"
)
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Niveles modificados: 0")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 104)
