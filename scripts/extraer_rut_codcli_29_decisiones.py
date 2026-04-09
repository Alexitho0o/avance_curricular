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

RECOMENDACIONES_29 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "RECOMENDACION_DECISION_29_P1_20260703_102618"
    / "01_RECOMENDACION_DECISION_29_P1.tsv"
)

EXPEDIENTE_644 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "EXPEDIENTE_REVISION_644_20260702_012504"
    / "02_RESULTADOS"
    / "01_EXPEDIENTE_COMPLETO_644.tsv"
)

DIAGNOSTICO_IDENTIDAD = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "DIAGNOSTICO_124_POR_IDENTIDAD_20260702_002433"
    / "01_DIAGNOSTICO_COMPLETO_124_IDENTIDAD.tsv"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"EXTRACCION_RUT_CODCLI_29_{timestamp}"
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


def norm_rut(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"\d+\.0", texto):
        texto = texto[:-2]

    return re.sub(r"[^0-9K]", "", texto)


def rut_formateado(valor):
    rut = norm_rut(valor)

    if len(rut) < 2:
        return rut

    cuerpo = rut[:-1]
    dv = rut[-1]

    if not cuerpo.isdigit():
        return rut

    cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")

    return f"{cuerpo_formateado}-{dv}"


def valores_unicos(valor, normalizador=norm_codigo):
    if pd.isna(valor):
        return []

    partes = re.split(
        r"\s*\|\s*|\s*;\s*|,\s*",
        str(valor),
    )

    return sorted({
        normalizador(parte)
        for parte in partes
        if normalizador(parte)
    })


def unir_series_no_vacias(*series):
    if not series:
        raise ValueError("Se requiere al menos una serie.")

    salida = pd.Series(
        "",
        index=series[0].index,
        dtype="string",
    )

    for serie in series:
        valores = (
            serie.fillna("")
            .astype(str)
            .str.strip()
        )

        mask = salida.fillna("").eq("") & valores.ne("")
        salida.loc[mask] = valores.loc[mask]

    return salida.fillna("").astype(str)


def obtener_serie(df, candidatas):
    mapa = {
        norm_col(columna): columna
        for columna in df.columns
    }

    series = []
    usadas = []

    for candidata in candidatas:
        clave = norm_col(candidata)

        if clave in mapa:
            original = mapa[clave]

            if original not in usadas:
                usadas.append(original)
                series.append(df[original])

    if not series:
        return (
            pd.Series(
                "",
                index=df.index,
                dtype="string",
            ),
            [],
        )

    return unir_series_no_vacias(*series), usadas


# ============================================================
# 1. VALIDAR FUENTES
# ============================================================

fuentes = {
    "RECOMENDACIONES_29": RECOMENDACIONES_29,
    "EXPEDIENTE_644": EXPEDIENTE_644,
    "DIAGNOSTICO_IDENTIDAD": DIAGNOSTICO_IDENTIDAD,
}

for nombre, ruta in fuentes.items():
    if not ruta.exists():
        raise RuntimeError(
            f"No existe la fuente {nombre}: {ruta}"
        )


# ============================================================
# 2. LEER FUENTES
# ============================================================

recomendaciones = pd.read_csv(
    RECOMENDACIONES_29,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

expediente = pd.read_csv(
    EXPEDIENTE_644,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

identidad = pd.read_csv(
    DIAGNOSTICO_IDENTIDAD,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

for nombre, df in {
    "recomendaciones": recomendaciones,
    "expediente": expediente,
    "identidad": identidad,
}.items():
    if "ID_FILA_5809" not in df.columns:
        raise RuntimeError(
            f"Falta ID_FILA_5809 en {nombre}."
        )

    if df["ID_FILA_5809"].duplicated().any():
        raise RuntimeError(
            f"ID_FILA_5809 duplicado en {nombre}."
        )


if len(recomendaciones) != 29:
    raise RuntimeError(
        f"Se esperaban 29 recomendaciones y se encontraron "
        f"{len(recomendaciones)}."
    )


# ============================================================
# 3. PREPARAR APORTES SIN COLISIONES
# ============================================================

exp_cols = [
    columna
    for columna in expediente.columns
    if columna != "ID_FILA_5809"
]

id_cols = [
    columna
    for columna in identidad.columns
    if columna != "ID_FILA_5809"
]

exp_aporte = expediente[
    ["ID_FILA_5809"] + exp_cols
].copy()

exp_aporte = exp_aporte.rename(
    columns={
        columna: f"EXP__{columna}"
        for columna in exp_cols
    }
)

id_aporte = identidad[
    ["ID_FILA_5809"] + id_cols
].copy()

id_aporte = id_aporte.rename(
    columns={
        columna: f"ID__{columna}"
        for columna in id_cols
    }
)

base = recomendaciones.merge(
    exp_aporte,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

base = base.merge(
    id_aporte,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

if len(base) != 29:
    raise RuntimeError(
        "La consolidación alteró el universo de 29 casos."
    )


# ============================================================
# 4. EXTRAER IDENTIFICADORES
# ============================================================

rut_5809, columnas_rut_5809 = obtener_serie(
    base,
    [
        "DOCUMENTO",
        "DOCUMENTO_NORM",
        "NUM_DOCUMENTO",
        "RUT",
        "EXP__DOCUMENTO_NORM",
        "EXP__NUM_DOCUMENTO",
        "EXP__RUT",
        "ID__DOCUMENTO_NORM",
        "ID__NUM_DOCUMENTO",
    ],
)

rut_evidencia, columnas_rut_evidencia = obtener_serie(
    base,
    [
        "RUT_EVIDENCIA_IDENTIDAD",
        "RUT_DATOS_IDENTIDAD",
        "EXP__RUT_DATOS_IDENTIDAD",
        "ID__RUT_DATOS_IDENTIDAD",
        "ID__RUT_DATOS_NORM",
    ],
)

codcli, columnas_codcli = obtener_serie(
    base,
    [
        "CODCLI_EVIDENCIA_IDENTIDAD",
        "CODCLI_DATOS_IDENTIDAD",
        "CODCLI_HISTORICOS_DOCUMENTO",
        "CODCLI_DATOS_DOCUMENTO",
        "CODCLI_HOJA1",
        "CODCLI_DOCUMENTO",
        "CODCLI_DATOS",
        "EXP__CODCLI_DATOS_IDENTIDAD",
        "EXP__CODCLI_HISTORICOS_DOCUMENTO",
        "EXP__CODCLI_DATOS_DOCUMENTO",
        "EXP__CODCLI_HOJA1",
        "EXP__CODCLI_DOCUMENTO",
        "EXP__CODCLI_DATOS",
        "ID__CODCLI_DATOS_IDENTIDAD",
        "ID__CODCLI_DATOS_NORM",
    ],
)

nombres, columnas_nombres = obtener_serie(
    base,
    [
        "NOMBRES",
        "EXP__NOMBRES",
        "ID__NOMBRES",
    ],
)

primer_apellido, columnas_paterno = obtener_serie(
    base,
    [
        "PRIMER_APELLIDO",
        "EXP__PRIMER_APELLIDO",
        "ID__PRIMER_APELLIDO",
    ],
)

segundo_apellido, columnas_materno = obtener_serie(
    base,
    [
        "SEGUNDO_APELLIDO",
        "EXP__SEGUNDO_APELLIDO",
        "ID__SEGUNDO_APELLIDO",
    ],
)

codpestud, columnas_plan = obtener_serie(
    base,
    [
        "CODPESTUD_VIGENTE",
        "CODPESTUD_RESUELTO",
        "EXP__CODPESTUD_RESUELTO",
        "ID__CODPESTUD_RESUELTO",
    ],
)

codigo_unico, columnas_codigo_unico = obtener_serie(
    base,
    [
        "CODIGO_UNICO_5809",
        "CODIGO_UNICO",
        "EXP__CODIGO_UNICO",
        "ID__CODIGO_UNICO",
    ],
)

carrera_plan, columnas_carrera_plan = obtener_serie(
    base,
    [
        "CODCARR_PLAN_VIGENTE",
        "CODCARR_PLAN_NORM",
        "EXP__CODCARR_PLAN_NORM",
        "ID__CODCARR_PLAN",
        "ID__CODCARR_PLAN_DIAG",
    ],
)

carrera_evidencia, columnas_carrera_evidencia = obtener_serie(
    base,
    [
        "CODCARPR_EVIDENCIA",
        "CODCARPR_DATOS_NORM",
        "CARRERAS_DATOS_IDENTIDAD",
        "EXP__CODCARPR_DATOS_NORM",
        "EXP__CARRERAS_DATOS_IDENTIDAD",
        "ID__CARRERAS_DATOS_IDENTIDAD",
    ],
)

nivel_evidencia, columnas_nivel = obtener_serie(
    base,
    [
        "NIVEL_EVIDENCIA",
        "NIVEL_CANDIDATO_IDENTIDAD",
        "NIVEL_CANDIDATO_NUM",
        "NIVELES_DATOS_IDENTIDAD",
        "EXP__NIVEL_CANDIDATO_IDENTIDAD",
        "EXP__NIVEL_CANDIDATO_NUM",
        "EXP__NIVELES_DATOS_IDENTIDAD",
        "ID__NIVEL_CANDIDATO_IDENTIDAD",
        "ID__NIVELES_DATOS_IDENTIDAD",
    ],
)

nivel_max_plan, columnas_nivel_max = obtener_serie(
    base,
    [
        "NIVEL_MAX_PLAN",
        "NIVEL_MAX_PLAN_NUM",
        "NIVEL_MAX_PLAN_DIAG",
        "EXP__NIVEL_MAX_PLAN_NUM",
        "EXP__NIVEL_MAX_PLAN_DIAG",
        "ID__NIVEL_MAX_PLAN_DIAG",
    ],
)


# ============================================================
# 5. CONSTRUIR PLANILLA DE REVISIÓN
# ============================================================

resultado = pd.DataFrame({
    "N_ORDEN_REVISION":
    base.get(
        "N_ORDEN_REVISION",
        pd.Series(
            range(1, len(base) + 1),
            index=base.index,
        ),
    ),

    "ID_FILA_5809":
    base["ID_FILA_5809"],

    "DECISION_RECOMENDADA":
    base["DECISION_RECOMENDADA"],

    "ESTADO_CIERRE_RECOMENDADO":
    base["ESTADO_CIERRE_RECOMENDADO"],

    "CATEGORIA_REVISION":
    base["CATEGORIA_REVISION"],

    "RUT_5809_NORMALIZADO":
    rut_5809.map(norm_rut),

    "RUT_5809_FORMATEADO":
    rut_5809.map(rut_formateado),

    "RUT_EVIDENCIA_NORMALIZADO":
    rut_evidencia.map(norm_rut),

    "RUT_EVIDENCIA_FORMATEADO":
    rut_evidencia.map(rut_formateado),

    "COINCIDE_RUT":
    [
        (
            "SI"
            if norm_rut(rut_a)
            and norm_rut(rut_b)
            and norm_rut(rut_a) == norm_rut(rut_b)
            else (
                "NO"
                if norm_rut(rut_a) and norm_rut(rut_b)
                else "SIN_COMPARADOR"
            )
        )
        for rut_a, rut_b in zip(
            rut_5809,
            rut_evidencia,
        )
    ],

    "CODCLI":
    codcli.map(norm_codigo),

    "NOMBRES":
    nombres,

    "PRIMER_APELLIDO":
    primer_apellido,

    "SEGUNDO_APELLIDO":
    segundo_apellido,

    "CODIGO_UNICO_5809":
    codigo_unico.map(norm_codigo),

    "CODPESTUD_VIGENTE":
    codpestud.map(norm_codigo),

    "CODCARR_PLAN_VIGENTE":
    carrera_plan.map(norm_codigo),

    "CODCARPR_EVIDENCIA":
    carrera_evidencia.map(norm_codigo),

    "NIVEL_EVIDENCIA":
    nivel_evidencia,

    "NIVEL_MAX_PLAN":
    nivel_max_plan,

    "FUNDAMENTO_RECOMENDADO":
    base["FUNDAMENTO_RECOMENDADO"],

    "REQUIERE_FUENTE_ADICIONAL":
    base["REQUIERE_FUENTE_ADICIONAL"],

    "ESTADO_REVISION_MANUAL":
    "PENDIENTE_REVISION_INDIVIDUAL",

    "DECISION_FINAL_REVISOR":
    "",

    "FUENTE_VERIFICADA":
    "",

    "OBSERVACION_REVISOR":
    "",
})


# ============================================================
# 6. SEPARAR RECHAZADOS Y PENDIENTES
# ============================================================

rechazados = resultado[
    resultado["DECISION_RECOMENDADA"].eq(
        "RECHAZAR_NIVEL"
    )
].copy()

pendientes = resultado[
    resultado["DECISION_RECOMENDADA"].eq(
        "MANTENER_PENDIENTE"
    )
].copy()

if len(rechazados) != 15:
    raise RuntimeError(
        f"Rechazados inesperados: {len(rechazados)}; "
        "esperados: 15."
    )

if len(pendientes) != 14:
    raise RuntimeError(
        f"Pendientes inesperados: {len(pendientes)}; "
        "esperados: 14."
    )


# ============================================================
# 7. CONTROL DE IDENTIFICADORES
# ============================================================

resultado["TIENE_RUT_5809"] = (
    resultado["RUT_5809_NORMALIZADO"]
    .ne("")
    .map({
        True: "SI",
        False: "NO",
    })
)

resultado["TIENE_RUT_EVIDENCIA"] = (
    resultado["RUT_EVIDENCIA_NORMALIZADO"]
    .ne("")
    .map({
        True: "SI",
        False: "NO",
    })
)

resultado["TIENE_CODCLI"] = (
    resultado["CODCLI"]
    .ne("")
    .map({
        True: "SI",
        False: "NO",
    })
)

resultado["IDENTIFICADOR_DISPONIBLE"] = (
    resultado[
        [
            "RUT_5809_NORMALIZADO",
            "RUT_EVIDENCIA_NORMALIZADO",
            "CODCLI",
        ]
    ]
    .ne("")
    .any(axis=1)
    .map({
        True: "SI",
        False: "NO",
    })
)

sin_identificador = resultado[
    resultado["IDENTIFICADOR_DISPONIBLE"].eq("NO")
].copy()

sin_rut_o_codcli = resultado[
    (
        resultado["RUT_5809_NORMALIZADO"].eq("")
        | resultado["CODCLI"].eq("")
    )
].copy()


# ============================================================
# 8. RESÚMENES
# ============================================================

resumen_decision = (
    resultado["DECISION_RECOMENDADA"]
    .value_counts()
    .rename_axis("DECISION")
    .reset_index(name="CASOS")
)

resumen_identificadores = pd.DataFrame([
    {
        "INDICADOR": "Casos totales",
        "VALOR": len(resultado),
    },
    {
        "INDICADOR": "Rechazados recomendados",
        "VALOR": len(rechazados),
    },
    {
        "INDICADOR": "Pendientes recomendados",
        "VALOR": len(pendientes),
    },
    {
        "INDICADOR": "Con RUT 5809",
        "VALOR": int(
            resultado["TIENE_RUT_5809"].eq("SI").sum()
        ),
    },
    {
        "INDICADOR": "Con RUT de evidencia",
        "VALOR": int(
            resultado["TIENE_RUT_EVIDENCIA"].eq("SI").sum()
        ),
    },
    {
        "INDICADOR": "Con CODCLI",
        "VALOR": int(
            resultado["TIENE_CODCLI"].eq("SI").sum()
        ),
    },
    {
        "INDICADOR": "Sin ningún identificador",
        "VALOR": len(sin_identificador),
    },
])


# ============================================================
# 9. TRAZABILIDAD DE COLUMNAS
# ============================================================

trazabilidad_columnas = pd.DataFrame([
    {
        "CAMPO_SALIDA": "RUT_5809",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_rut_5809
        ),
    },
    {
        "CAMPO_SALIDA": "RUT_EVIDENCIA",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_rut_evidencia
        ),
    },
    {
        "CAMPO_SALIDA": "CODCLI",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_codcli
        ),
    },
    {
        "CAMPO_SALIDA": "NOMBRES",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_nombres
        ),
    },
    {
        "CAMPO_SALIDA": "PRIMER_APELLIDO",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_paterno
        ),
    },
    {
        "CAMPO_SALIDA": "SEGUNDO_APELLIDO",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_materno
        ),
    },
    {
        "CAMPO_SALIDA": "CODPESTUD_VIGENTE",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_plan
        ),
    },
    {
        "CAMPO_SALIDA": "CODIGO_UNICO_5809",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_codigo_unico
        ),
    },
    {
        "CAMPO_SALIDA": "CODCARR_PLAN_VIGENTE",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_carrera_plan
        ),
    },
    {
        "CAMPO_SALIDA": "CODCARPR_EVIDENCIA",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_carrera_evidencia
        ),
    },
    {
        "CAMPO_SALIDA": "NIVEL_EVIDENCIA",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_nivel
        ),
    },
    {
        "CAMPO_SALIDA": "NIVEL_MAX_PLAN",
        "COLUMNAS_CONSULTADAS": " | ".join(
            columnas_nivel_max
        ),
    },
])


# ============================================================
# 10. VALIDACIONES
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
        "VALIDACION": "RECHAZADOS_15",
        "RESULTADO": (
            "OK" if len(rechazados) == 15 else "ERROR"
        ),
        "DETALLE": len(rechazados),
    },
    {
        "VALIDACION": "PENDIENTES_14",
        "RESULTADO": (
            "OK" if len(pendientes) == 14 else "ERROR"
        ),
        "DETALLE": len(pendientes),
    },
    {
        "VALIDACION": "ID_FILA_UNICO",
        "RESULTADO": (
            "OK"
            if not resultado["ID_FILA_5809"].duplicated().any()
            else "ERROR"
        ),
        "DETALLE": int(
            resultado["ID_FILA_5809"].duplicated().sum()
        ),
    },
    {
        "VALIDACION": "SIN_IDENTIFICADOR",
        "RESULTADO": (
            "OK"
            if len(sin_identificador) == 0
            else "REVISAR"
        ),
        "DETALLE": len(sin_identificador),
    },
    {
        "VALIDACION": "DECISIONES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
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
# 11. EXPORTAR
# ============================================================

resultado.to_csv(
    RESULTADOS / "01_REVISION_RUT_CODCLI_29.tsv",
    sep="\t",
    index=False,
)

rechazados.to_csv(
    RESULTADOS / "02_RECHAZADOS_15_RUT_CODCLI.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    RESULTADOS / "03_PENDIENTES_14_RUT_CODCLI.tsv",
    sep="\t",
    index=False,
)

sin_rut_o_codcli.to_csv(
    AUDITORIAS / "01_CASOS_SIN_RUT_O_CODCLI_COMPLETO.tsv",
    sep="\t",
    index=False,
)

sin_identificador.to_csv(
    AUDITORIAS / "02_CASOS_SIN_NINGUN_IDENTIFICADOR.tsv",
    sep="\t",
    index=False,
)

trazabilidad_columnas.to_csv(
    AUDITORIAS / "03_TRAZABILIDAD_COLUMNAS.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS / "04_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)

fuentes_df = pd.DataFrame([
    {
        "ROL": nombre,
        "RUTA": str(ruta),
        "SHA256": sha256(ruta),
        "TAMANO_BYTES": ruta.stat().st_size,
    }
    for nombre, ruta in fuentes.items()
])

fuentes_df.to_csv(
    AUDITORIAS / "05_FUENTES_Y_HASHES.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# 12. EXCEL
# ============================================================

excel = (
    RESULTADOS
    / "REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_identificadores.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resumen_decision.to_excel(
        writer,
        sheet_name="RESUMEN_DECISION",
        index=False,
    )

    rechazados.to_excel(
        writer,
        sheet_name="RECHAZADOS_15",
        index=False,
    )

    pendientes.to_excel(
        writer,
        sheet_name="PENDIENTES_14",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="REVISION_29",
        index=False,
    )

    sin_rut_o_codcli.to_excel(
        writer,
        sheet_name="SIN_RUT_O_CODCLI",
        index=False,
    )

    trazabilidad_columnas.to_excel(
        writer,
        sheet_name="TRAZABILIDAD_COLUMNAS",
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
# 13. MANIFIESTO Y REPORTE
# ============================================================

manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia_datos": 2025,
    "casos_totales": 29,
    "rechazados_recomendados": 15,
    "pendientes_recomendados": 14,
    "con_rut_5809": int(
        resultado["TIENE_RUT_5809"].eq("SI").sum()
    ),
    "con_rut_evidencia": int(
        resultado["TIENE_RUT_EVIDENCIA"].eq("SI").sum()
    ),
    "con_codcli": int(
        resultado["TIENE_CODCLI"].eq("SI").sum()
    ),
    "sin_identificador": len(sin_identificador),
    "decisiones_modificadas": False,
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

lineas = [
    "EXTRACCIÓN DE RUT Y CODCLI — 29 CASOS P1",
    "=" * 96,
    "Proceso: Avance Curricular SIES 2026",
    "Subproyecto: 5809 Matrícula",
    "Año de referencia: 2025",
    "",
    f"Rechazados recomendados: {len(rechazados)}",
    f"Pendientes recomendados: {len(pendientes)}",
    f"Con RUT 5809: {int(resultado['TIENE_RUT_5809'].eq('SI').sum())}",
    f"Con RUT evidencia: {int(resultado['TIENE_RUT_EVIDENCIA'].eq('SI').sum())}",
    f"Con CODCLI: {int(resultado['TIENE_CODCLI'].eq('SI').sum())}",
    f"Sin identificador: {len(sin_identificador)}",
    "",
    f"Excel: {excel}",
    f"Carpeta: {SALIDA}",
    "",
    "Decisiones modificadas: NO",
    "Fuentes modificadas: NO",
    "Archivo de carga generado: NO",
]

(REPORTES / "RESUMEN_EJECUCION.txt").write_text(
    "\n".join(lineas),
    encoding="utf-8",
)


# ============================================================
# 14. TERMINAL
# ============================================================

print()
print("=" * 100)
print("EXTRACCIÓN DE RUT Y CODCLI — RECHAZADOS Y PENDIENTES")
print("=" * 100)
print(f"Casos totales: {len(resultado)}")
print(f"Rechazados recomendados: {len(rechazados)}")
print(f"Pendientes recomendados: {len(pendientes)}")
print()
print("IDENTIFICADORES")
print("-" * 100)
print(
    "Con RUT 5809: "
    f"{resultado['TIENE_RUT_5809'].eq('SI').sum()}"
)
print(
    "Con RUT de evidencia: "
    f"{resultado['TIENE_RUT_EVIDENCIA'].eq('SI').sum()}"
)
print(
    "Con CODCLI: "
    f"{resultado['TIENE_CODCLI'].eq('SI').sum()}"
)
print(
    "Sin ningún identificador: "
    f"{len(sin_identificador)}"
)
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Decisiones modificadas: NO")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 100)
