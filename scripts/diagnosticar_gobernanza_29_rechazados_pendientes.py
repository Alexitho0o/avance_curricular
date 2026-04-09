#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

BASE_AUDITORIAS = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    BASE_AUDITORIAS
    / f"DIAGNOSTICO_GOBERNANZA_29_RECHAZADOS_PENDIENTES_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in [
    RESULTADOS,
    AUDITORIA,
    REPORTES,
]:
    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )


def norm_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )

    return re.sub(r"\s+", "", texto)


def norm_rut(valor):
    return re.sub(
        r"[^0-9K]",
        "",
        norm_texto(valor),
    )


def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as f:
        for bloque in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(bloque)

    return h.hexdigest()


def latest_file(pattern):
    archivos = sorted(
        BASE_AUDITORIAS.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not archivos:
        return None

    return archivos[0]


def buscar_archivo(nombre_objetivo):
    encontrados = sorted(
        BASE_AUDITORIAS.rglob(nombre_objetivo),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if encontrados:
        return encontrados[0]

    return None


def leer_excel_todas_hojas(ruta):
    if not ruta or not ruta.exists():
        return []

    try:
        xl = pd.ExcelFile(
            ruta,
            engine="openpyxl",
        )
    except Exception as exc:
        return [
            pd.DataFrame([
                {
                    "__ARCHIVO__": ruta.name,
                    "__RUTA__": str(ruta),
                    "__HOJA__": "__ERROR_LECTURA__",
                    "__ERROR__": str(exc),
                }
            ])
        ]

    hojas = []

    for hoja in xl.sheet_names:
        try:
            df = pd.read_excel(
                ruta,
                sheet_name=hoja,
                dtype=str,
                keep_default_na=False,
                engine="openpyxl",
            )

            df["__ARCHIVO__"] = ruta.name
            df["__RUTA__"] = str(ruta)
            df["__HOJA__"] = hoja

            hojas.append(df)

        except Exception as exc:
            hojas.append(
                pd.DataFrame([
                    {
                        "__ARCHIVO__": ruta.name,
                        "__RUTA__": str(ruta),
                        "__HOJA__": hoja,
                        "__ERROR__": str(exc),
                    }
                ])
            )

    return hojas


def columnas_rut(df):
    return [
        c for c in df.columns
        if any(
            token in c.upper()
            for token in [
                "RUT",
                "DOCUMENTO",
            ]
        )
    ]


def columnas_codcli(df):
    return [
        c for c in df.columns
        if "CODCLI" in c.upper()
    ]


def primero_no_vacio(fila, columnas):
    for col in columnas:
        if col in fila.index:
            valor = str(fila.get(col, "")).strip()
            if valor and valor.lower() != "nan":
                return valor
    return ""


def unir_no_vacios(valores):
    salida = []

    for valor in valores:
        texto = str(valor or "").strip()
        if texto and texto.lower() != "nan" and texto not in salida:
            salida.append(texto)

    return " | ".join(salida)


# ---------------------------------------------------------------------
# 1. Localización robusta de fuentes
# ---------------------------------------------------------------------

ARCHIVO_BASE_29 = buscar_archivo(
    "REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx"
)

ARCHIVO_CLASIFICACION_29 = buscar_archivo(
    "CLASIFICACION_29_MODELOS_PERIODIZACION.xlsx"
)

ARCHIVO_ADECUACION_2 = buscar_archivo(
    "ADECUACION_2_CASOS_PERIODIZACION.xlsx"
)

ARCHIVO_DIAGNOSTICO_27 = buscar_archivo(
    "DIAGNOSTICO_27_PENDIENTES_CODCLI_PLAN.xlsx"
)

ARCHIVO_DESCOMPOSICION_19 = buscar_archivo(
    "DESCOMPOSICION_19_CANDIDATOS_DEBILES.xlsx"
)

ARCHIVO_EVALUACION_14 = buscar_archivo(
    "EVALUACION_14_FAMILIA_CARRERA.xlsx"
)

FUENTES = [
    {
        "ROL": "BASE_29_RECHAZADOS_PENDIENTES",
        "RUTA": ARCHIVO_BASE_29,
        "OBLIGATORIA": True,
    },
    {
        "ROL": "CLASIFICACION_29_MODELOS",
        "RUTA": ARCHIVO_CLASIFICACION_29,
        "OBLIGATORIA": True,
    },
    {
        "ROL": "ADECUACION_2_CASOS",
        "RUTA": ARCHIVO_ADECUACION_2,
        "OBLIGATORIA": True,
    },
    {
        "ROL": "DIAGNOSTICO_27_CODCLI_PLAN",
        "RUTA": ARCHIVO_DIAGNOSTICO_27,
        "OBLIGATORIA": True,
    },
    {
        "ROL": "DESCOMPOSICION_19",
        "RUTA": ARCHIVO_DESCOMPOSICION_19,
        "OBLIGATORIA": False,
    },
    {
        "ROL": "EVALUACION_14",
        "RUTA": ARCHIVO_EVALUACION_14,
        "OBLIGATORIA": False,
    },
]

faltantes = [
    f["ROL"]
    for f in FUENTES
    if f["OBLIGATORIA"]
    and (
        f["RUTA"] is None
        or not f["RUTA"].exists()
    )
]

if faltantes:
    raise SystemExit(
        "Faltan fuentes obligatorias: "
        + " | ".join(faltantes)
    )


fuentes_df = pd.DataFrame([
    {
        "ROL": f["ROL"],
        "RUTA": str(f["RUTA"]) if f["RUTA"] else "",
        "EXISTE": bool(f["RUTA"] and f["RUTA"].exists()),
        "OBLIGATORIA": f["OBLIGATORIA"],
        "SHA256": (
            sha256(f["RUTA"])
            if f["RUTA"] and f["RUTA"].exists()
            else ""
        ),
        "TAMANO_BYTES": (
            f["RUTA"].stat().st_size
            if f["RUTA"] and f["RUTA"].exists()
            else ""
        ),
    }
    for f in FUENTES
])

fuentes_df.to_csv(
    AUDITORIA / "01_FUENTES_REVISADAS.tsv",
    sep="\t",
    index=False,
)


# ---------------------------------------------------------------------
# 2. Construcción del universo base de los 29
# ---------------------------------------------------------------------

hojas_base = leer_excel_todas_hojas(
    ARCHIVO_BASE_29
)

registros_base = []

for df in hojas_base:
    if "__ERROR__" in df.columns:
        continue

    cols_rut = columnas_rut(df)

    if not cols_rut:
        continue

    for idx, fila in df.iterrows():
        rut = ""

        for col in cols_rut:
            rut_col = norm_rut(
                fila.get(col, "")
            )

            if rut_col:
                rut = rut_col
                break

        if not rut:
            continue

        registros_base.append({
            "RUT_NORM": rut,
            "ARCHIVO_ORIGEN_BASE": fila.get("__ARCHIVO__", ""),
            "HOJA_ORIGEN_BASE": fila.get("__HOJA__", ""),
            "N_ORDEN_REVISION": fila.get("N_ORDEN_REVISION", ""),
            "ID_FILA_5809": fila.get("ID_FILA_5809", ""),
            "RUT_5809_NORMALIZADO": fila.get("RUT_5809_NORMALIZADO", ""),
            "RUT_EVIDENCIA_NORMALIZADO": fila.get("RUT_EVIDENCIA_NORMALIZADO", ""),
            "RUT_5809_FORMATEADO": fila.get("RUT_5809_FORMATEADO", ""),
            "CODCARR_PLAN_VIGENTE": fila.get("CODCARR_PLAN_VIGENTE", ""),
            "CODCARPR_EVIDENCIA": fila.get("CODCARPR_EVIDENCIA", ""),
            "NIVEL_EVIDENCIA": fila.get("NIVEL_EVIDENCIA", ""),
            "DECISION_RECOMENDADA_ORIGINAL": fila.get("DECISION_RECOMENDADA", ""),
            "ESTADO_CIERRE_ORIGINAL": fila.get("ESTADO_CIERRE_RECOMENDADO", ""),
            "CATEGORIA_REVISION_ORIGINAL": fila.get("CATEGORIA_REVISION", ""),
        })

base_df = pd.DataFrame(
    registros_base
)

if base_df.empty:
    raise SystemExit(
        "No se pudieron extraer RUT desde el archivo base de 29."
    )

# Puede haber la misma persona en RECHAZADOS_15 y REVISION_29.
base_unica = (
    base_df.sort_values(
        [
            "RUT_NORM",
            "HOJA_ORIGEN_BASE",
        ]
    )
    .groupby(
        "RUT_NORM",
        as_index=False,
    )
    .agg(
        ARCHIVOS_ORIGEN_BASE=(
            "ARCHIVO_ORIGEN_BASE",
            unir_no_vacios,
        ),
        HOJAS_ORIGEN_BASE=(
            "HOJA_ORIGEN_BASE",
            unir_no_vacios,
        ),
        N_ORDEN_REVISION=(
            "N_ORDEN_REVISION",
            unir_no_vacios,
        ),
        ID_FILA_5809=(
            "ID_FILA_5809",
            unir_no_vacios,
        ),
        RUT_5809_NORMALIZADO=(
            "RUT_5809_NORMALIZADO",
            unir_no_vacios,
        ),
        RUT_EVIDENCIA_NORMALIZADO=(
            "RUT_EVIDENCIA_NORMALIZADO",
            unir_no_vacios,
        ),
        RUT_5809_FORMATEADO=(
            "RUT_5809_FORMATEADO",
            unir_no_vacios,
        ),
        CODCARR_PLAN_VIGENTE=(
            "CODCARR_PLAN_VIGENTE",
            unir_no_vacios,
        ),
        CODCARPR_EVIDENCIA=(
            "CODCARPR_EVIDENCIA",
            unir_no_vacios,
        ),
        NIVEL_EVIDENCIA=(
            "NIVEL_EVIDENCIA",
            unir_no_vacios,
        ),
        DECISION_RECOMENDADA_ORIGINAL=(
            "DECISION_RECOMENDADA_ORIGINAL",
            unir_no_vacios,
        ),
        ESTADO_CIERRE_ORIGINAL=(
            "ESTADO_CIERRE_ORIGINAL",
            unir_no_vacios,
        ),
        CATEGORIA_REVISION_ORIGINAL=(
            "CATEGORIA_REVISION_ORIGINAL",
            unir_no_vacios,
        ),
    )
)

if len(base_unica) != 29:
    print()
    print("ADVERTENCIA: El universo único no es 29.")
    print(f"RUT únicos detectados: {len(base_unica)}")
    print("Se continúa, pero queda registrado en validaciones.")


# ---------------------------------------------------------------------
# 3. Trazabilidad completa en artefactos posteriores
# ---------------------------------------------------------------------

artefactos_df = []

for f in FUENTES:
    ruta = f["RUTA"]

    if not ruta or not ruta.exists():
        continue

    for df in leer_excel_todas_hojas(ruta):
        if "__ERROR__" in df.columns:
            artefactos_df.append(df)
            continue

        cols_r = columnas_rut(df)

        if not cols_r:
            continue

        for idx, fila in df.iterrows():
            ruts_fila = []

            for col in cols_r:
                r = norm_rut(
                    fila.get(col, "")
                )
                if r:
                    ruts_fila.append(r)

            ruts_fila = sorted(set(ruts_fila))

            for rut in ruts_fila:
                if rut in set(base_unica["RUT_NORM"]):
                    registro = fila.to_dict()
                    registro["RUT_NORM"] = rut
                    registro["__ROL_FUENTE__"] = f["ROL"]
                    registro["__COLUMNAS_RUT_REVISADAS__"] = " | ".join(cols_r)
                    artefactos_df.append(
                        pd.DataFrame([registro])
                    )

if artefactos_df:
    trazabilidad = pd.concat(
        artefactos_df,
        ignore_index=True,
        sort=False,
    )
else:
    trazabilidad = pd.DataFrame(
        columns=[
            "RUT_NORM",
            "__ROL_FUENTE__",
            "__ARCHIVO__",
            "__HOJA__",
        ]
    )


# ---------------------------------------------------------------------
# 4. Funciones de resumen por RUT
# ---------------------------------------------------------------------

def contiene_valor(grupo, columna, valor):
    if columna not in grupo.columns:
        return False

    return grupo[columna].astype(str).str.upper().str.contains(
        valor,
        na=False,
        regex=False,
    ).any()


def valores_unicos_grupo(grupo, columna):
    if columna not in grupo.columns:
        return ""

    valores = []

    for valor in grupo[columna].dropna().astype(str):
        texto = valor.strip()
        if texto and texto.lower() != "nan" and texto not in valores:
            valores.append(texto)

    return " | ".join(valores)


def resumen_rut(rut, base_row, grupo):
    estado_original = base_row.get(
        "ESTADO_CIERRE_ORIGINAL",
        "",
    )

    decision_original = base_row.get(
        "DECISION_RECOMENDADA_ORIGINAL",
        "",
    )

    categoria_original = base_row.get(
        "CATEGORIA_REVISION_ORIGINAL",
        "",
    )

    estado_asociacion = valores_unicos_grupo(
        grupo,
        "ESTADO_ASOCIACION_MODELO",
    )

    estado_adecuacion = valores_unicos_grupo(
        grupo,
        "ESTADO_ADECUACION",
    )

    estado_diagnostico_27 = valores_unicos_grupo(
        grupo,
        "ESTADO_DIAGNOSTICO_27",
    )

    estado_final_19 = valores_unicos_grupo(
        grupo,
        "ESTADO_FINAL_19",
    )

    respaldo_real = valores_unicos_grupo(
        grupo,
        "RESPALDO_REAL",
    )

    anio_adecuado = valores_unicos_grupo(
        grupo,
        "ANIO_CURRICULAR_ADECUADO",
    )

    codcli = unir_no_vacios([
        valores_unicos_grupo(
            grupo,
            "CODCLI_PROMEDIOS_LISTA",
        ),
        valores_unicos_grupo(
            grupo,
            "CODCLI_MODELO_ASOCIADO",
        ),
        valores_unicos_grupo(
            grupo,
            "CODCLI_DATOS",
        ),
    ])

    fundamento = unir_no_vacios([
        valores_unicos_grupo(
            grupo,
            "FUNDAMENTO_ADECUACION",
        ),
        valores_unicos_grupo(
            grupo,
            "FUNDAMENTO_ASOCIACION",
        ),
        valores_unicos_grupo(
            grupo,
            "FUNDAMENTO",
        ),
    ])

    archivos = valores_unicos_grupo(
        grupo,
        "__ARCHIVO__",
    )

    hojas = valores_unicos_grupo(
        grupo,
        "__HOJA__",
    )

    tiene_adecuacion = (
        "ADECUACION_DEMOSTRADA_POR_CODCLI_Y_REPORTE"
        in estado_adecuacion
    )

    tiene_modelo_codcli = (
        "MODELO_CONFIRMADO_POR_CODCLI"
        in estado_asociacion
    )

    original_rechazo = (
        "RECHAZ" in decision_original.upper()
        or "RECHAZ" in estado_original.upper()
    )

    if tiene_adecuacion:
        estado_gobernanza = (
            "ADECUADO_POR_CODCLI_Y_REPORTE"
        )

        decision_final = (
            "REVOCAR_RECHAZO_INICIAL_SI_EXISTE"
            if original_rechazo
            else "MANTENER_ADECUACION_DEMOSTRADA"
        )

        estado_para_informar = (
            "RESUELTO: adecuación demostrada. "
            "No corresponde rechazo definitivo."
        )

    elif tiene_modelo_codcli:
        estado_gobernanza = (
            "MODELO_CONFIRMADO_PENDIENTE_ADECUACION_FORMAL"
        )

        decision_final = (
            "REVISAR_ADECUACION_FORMAL"
        )

        estado_para_informar = (
            "Modelo confirmado por CODCLI, requiere verificar "
            "si existe expediente de adecuación."
        )

    elif "CANDIDATO_FUERTE" in estado_diagnostico_27:
        estado_gobernanza = (
            "PENDIENTE_CONFIRMACION_PLAN"
        )

        decision_final = "MANTENER_PENDIENTE"

        estado_para_informar = (
            "Pendiente. Requiere confirmación institucional "
            "de plan o periodización."
        )

    elif "CANDIDATO_DEBIL" in estado_diagnostico_27:
        estado_gobernanza = (
            "PENDIENTE_DEBIL_NO_CONVERTIR"
        )

        decision_final = "MANTENER_PENDIENTE"

        estado_para_informar = (
            "Pendiente. No convertir por similitud."
        )

    elif "SIN_MODELO_DEMOSTRADO" in estado_diagnostico_27:
        estado_gobernanza = (
            "PENDIENTE_SIN_MODELO_DEMOSTRADO"
        )

        decision_final = "MANTENER_PENDIENTE"

        estado_para_informar = (
            "Pendiente. No existe modelo demostrado."
        )

    elif "FAMILIA_Y_CARRERA" in respaldo_real:
        estado_gobernanza = (
            "PENDIENTE_INTERMEDIO_FAMILIA_Y_CARRERA"
        )

        decision_final = "MANTENER_PENDIENTE"

        estado_para_informar = (
            "Pendiente intermedio. Familia CODCLI y carrera "
            "coinciden, pero no autorizan conversión automática."
        )

    elif "SOLO_CARRERA" in respaldo_real:
        estado_gobernanza = (
            "PENDIENTE_SOLO_CARRERA"
        )

        decision_final = "MANTENER_PENDIENTE"

        estado_para_informar = (
            "Pendiente débil. Solo coincide carrera."
        )

    else:
        estado_gobernanza = (
            "PENDIENTE_SIN_CIERRE_POSTERIOR_IDENTIFICADO"
        )

        decision_final = "MANTENER_PENDIENTE"

        estado_para_informar = (
            "Pendiente. No se encontró evidencia posterior "
            "suficiente para cerrar."
        )

    return {
        "RUT_NORM": rut,
        "ID_FILA_5809": base_row.get("ID_FILA_5809", ""),
        "RUT_5809_FORMATEADO": base_row.get("RUT_5809_FORMATEADO", ""),
        "RUT_5809_NORMALIZADO": base_row.get("RUT_5809_NORMALIZADO", ""),
        "RUT_EVIDENCIA_NORMALIZADO": base_row.get("RUT_EVIDENCIA_NORMALIZADO", ""),
        "CODCARR_PLAN_VIGENTE": base_row.get("CODCARR_PLAN_VIGENTE", ""),
        "CODCARPR_EVIDENCIA": base_row.get("CODCARPR_EVIDENCIA", ""),
        "NIVEL_EVIDENCIA": base_row.get("NIVEL_EVIDENCIA", ""),
        "DECISION_RECOMENDADA_ORIGINAL": decision_original,
        "ESTADO_CIERRE_ORIGINAL": estado_original,
        "CATEGORIA_REVISION_ORIGINAL": categoria_original,
        "CODCLI_CONSOLIDADO": codcli,
        "ESTADO_ASOCIACION_MODELO": estado_asociacion,
        "ESTADO_ADECUACION": estado_adecuacion,
        "ANIO_CURRICULAR_ADECUADO": anio_adecuado,
        "ESTADO_DIAGNOSTICO_27": estado_diagnostico_27,
        "ESTADO_FINAL_19": estado_final_19,
        "RESPALDO_REAL": respaldo_real,
        "ESTADO_GOBERNANZA_FINAL": estado_gobernanza,
        "DECISION_FINAL_GOBERNANZA": decision_final,
        "ESTADO_PARA_INFORMAR_AVANCE": estado_para_informar,
        "RECHAZO_INICIAL_REVOCADO": (
            "SI"
            if original_rechazo and tiene_adecuacion
            else "NO"
        ),
        "RECHAZO_DEFINITIVO_DEMOSTRADO": "NO",
        "FUENTES_DONDE_APARECE": archivos,
        "HOJAS_DONDE_APARECE": hojas,
        "FUNDAMENTO_GOBERNANZA": fundamento,
    }


# ---------------------------------------------------------------------
# 5. Resultado final por RUT
# ---------------------------------------------------------------------

filas_finales = []

for _, base_row in base_unica.iterrows():
    rut = base_row["RUT_NORM"]

    grupo = trazabilidad[
        trazabilidad["RUT_NORM"].eq(rut)
    ].copy()

    filas_finales.append(
        resumen_rut(
            rut,
            base_row,
            grupo,
        )
    )

final = pd.DataFrame(
    filas_finales
)

if len(final) != len(base_unica):
    raise RuntimeError(
        "El consolidado final no conserva el universo base."
    )


# ---------------------------------------------------------------------
# 6. Resúmenes
# ---------------------------------------------------------------------

resumen_estado = (
    final[
        "ESTADO_GOBERNANZA_FINAL"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_GOBERNANZA_FINAL")
    .reset_index(name="CASOS")
)

resumen_decision = (
    final[
        "DECISION_FINAL_GOBERNANZA"
    ]
    .value_counts(dropna=False)
    .rename_axis("DECISION_FINAL_GOBERNANZA")
    .reset_index(name="CASOS")
)

resumen_original = (
    final[
        "ESTADO_CIERRE_ORIGINAL"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_CIERRE_ORIGINAL")
    .reset_index(name="CASOS")
)

revocados = final[
    final[
        "RECHAZO_INICIAL_REVOCADO"
    ].eq("SI")
].copy()

adecuados = final[
    final[
        "ESTADO_GOBERNANZA_FINAL"
    ].eq(
        "ADECUADO_POR_CODCLI_Y_REPORTE"
    )
].copy()

pendientes = final[
    ~final[
        "ESTADO_GOBERNANZA_FINAL"
    ].eq(
        "ADECUADO_POR_CODCLI_Y_REPORTE"
    )
].copy()


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_BASE_RUT_UNICOS",
        "RESULTADO": "OK" if len(final) == 29 else "REVISAR",
        "DETALLE": len(final),
    },
    {
        "VALIDACION": "CASOS_ADECUADOS",
        "RESULTADO": "OK" if len(adecuados) == 2 else "REVISAR",
        "DETALLE": len(adecuados),
    },
    {
        "VALIDACION": "CASOS_PENDIENTES",
        "RESULTADO": "OK" if len(pendientes) == 27 else "REVISAR",
        "DETALLE": len(pendientes),
    },
    {
        "VALIDACION": "RECHAZOS_DEFINITIVOS_DEMOSTRADOS",
        "RESULTADO": "OK",
        "DETALLE": int(
            final[
                "RECHAZO_DEFINITIVO_DEMOSTRADO"
            ].eq("SI").sum()
        ),
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


# ---------------------------------------------------------------------
# 7. Salidas
# ---------------------------------------------------------------------

final.to_csv(
    RESULTADOS
    / "01_DIAGNOSTICO_FINAL_GOBERNANZA_29.tsv",
    sep="\t",
    index=False,
)

trazabilidad.to_csv(
    RESULTADOS
    / "02_TRAZABILIDAD_COMPLETA_29.tsv",
    sep="\t",
    index=False,
)

adecuados.to_csv(
    RESULTADOS
    / "03_CASOS_ADECUADOS_2.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    RESULTADOS
    / "04_CASOS_PENDIENTES_27.tsv",
    sep="\t",
    index=False,
)

revocados.to_csv(
    RESULTADOS
    / "05_RECHAZOS_INICIALES_REVOCADOS.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIA
    / "02_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


excel = (
    RESULTADOS
    / "DIAGNOSTICO_GOBERNANZA_29_RECHAZADOS_PENDIENTES.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_estado.to_excel(
        writer,
        sheet_name="RESUMEN_ESTADO",
        index=False,
    )

    resumen_decision.to_excel(
        writer,
        sheet_name="RESUMEN_DECISION",
        index=False,
    )

    resumen_original.to_excel(
        writer,
        sheet_name="RESUMEN_ORIGINAL",
        index=False,
    )

    final.to_excel(
        writer,
        sheet_name="DIAGNOSTICO_FINAL_29",
        index=False,
    )

    adecuados.to_excel(
        writer,
        sheet_name="ADECUADOS_2",
        index=False,
    )

    pendientes.to_excel(
        writer,
        sheet_name="PENDIENTES_27",
        index=False,
    )

    revocados.to_excel(
        writer,
        sheet_name="RECHAZOS_REVOCADOS",
        index=False,
    )

    trazabilidad.to_excel(
        writer,
        sheet_name="TRAZABILIDAD_COMPLETA",
        index=False,
    )

    fuentes_df.to_excel(
        writer,
        sheet_name="FUENTES",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
        index=False,
    )

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(
                len(str(cell.value or ""))
                for cell in col[:2000]
            )
            ws.column_dimensions[letra].width = min(
                max(ancho + 2, 12),
                60,
            )


informe = (
    REPORTES
    / "INFORME_GOBERNANZA_29_RECHAZADOS_PENDIENTES.md"
)

lineas = []

lineas.append(
    "# Informe de gobernanza — 29 rechazados y pendientes"
)
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula Avance Curricular 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("- Archivo base: REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx")
lineas.append("")
lineas.append("## Resultado ejecutivo")
lineas.append("")
lineas.append(f"- Universo base único: **{len(final)} RUT**")
lineas.append(f"- Casos adecuados por CODCLI y reporte: **{len(adecuados)}**")
lineas.append(f"- Casos pendientes: **{len(pendientes)}**")
lineas.append(f"- Rechazos iniciales revocados: **{len(revocados)}**")
lineas.append("- Rechazos definitivos demostrados: **0**")
lineas.append("")
lineas.append("## Estados finales")
lineas.append("")
lineas.append(
    resumen_estado.to_markdown(
        index=False,
    )
)
lineas.append("")
lineas.append("## Decisiones finales")
lineas.append("")
lineas.append(
    resumen_decision.to_markdown(
        index=False,
    )
)
lineas.append("")
lineas.append("## Interpretación funcional")
lineas.append("")
lineas.append(
    "El archivo original de rechazados y pendientes corresponde a un "
    "estado preliminar. La gobernanza posterior demostró que existen "
    "casos inicialmente marcados como rechazo que deben ser revocados "
    "por evidencia directa. En particular, los casos adecuados por "
    "CODCLI y reporte individual no deben tratarse como excluidos ni "
    "rechazos definitivos."
)
lineas.append("")
lineas.append(
    "Los casos que no tienen adecuación demostrada permanecen como "
    "pendientes. No corresponde convertirlos por similitud de carrera, "
    "familia de CODCLI, duración o nivel dentro de rango."
)
lineas.append("")
lineas.append("## Archivos generados")
lineas.append("")
lineas.append(f"- Excel: `{excel}`")
lineas.append(f"- TSV final: `{RESULTADOS / '01_DIAGNOSTICO_FINAL_GOBERNANZA_29.tsv'}`")
lineas.append(f"- Trazabilidad: `{RESULTADOS / '02_TRAZABILIDAD_COMPLETA_29.tsv'}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

informe.write_text(
    "\n".join(lineas) + "\n",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_gobernanza_29.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "universo_rut": len(final),
            "casos_adecuados": len(adecuados),
            "casos_pendientes": len(pendientes),
            "rechazos_iniciales_revocados": len(revocados),
            "rechazos_definitivos_demostrados": 0,
            "excel": str(excel),
            "informe": str(informe),
            "fuentes_originales_modificadas": False,
            "archivo_sies_ready_generado": False,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


# ---------------------------------------------------------------------
# 8. Terminal
# ---------------------------------------------------------------------

print()
print("=" * 120)
print("DIAGNÓSTICO MASIVO DE GOBERNANZA — 29 RECHAZADOS/PENDIENTES")
print("=" * 120)
print(f"Universo base único: {len(final)}")
print(f"Casos adecuados por CODCLI y reporte: {len(adecuados)}")
print(f"Casos pendientes: {len(pendientes)}")
print(f"Rechazos iniciales revocados: {len(revocados)}")
print("Rechazos definitivos demostrados: 0")
print()

print("ESTADOS FINALES")
print("-" * 120)
print(
    resumen_estado.to_string(
        index=False,
    )
)

print()
print("DECISIONES FINALES")
print("-" * 120)
print(
    resumen_decision.to_string(
        index=False,
    )
)

print()
print("VALIDACIONES")
print("-" * 120)
print(
    validaciones.to_string(
        index=False,
    )
)

print()
print("=" * 120)
print("ARCHIVOS GENERADOS")
print("=" * 120)
print(f"Excel: {excel}")
print(f"Informe: {informe}")
print(f"Carpeta: {SALIDA}")
print("Fuentes originales modificadas: NO")
print("Archivo SIES_READY generado: NO")
print("=" * 120)
