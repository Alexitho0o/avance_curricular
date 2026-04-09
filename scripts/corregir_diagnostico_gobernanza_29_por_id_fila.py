#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()

BASE_AUDITORIAS = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
)

DIAGNOSTICO_ANTERIOR = (
    BASE_AUDITORIAS
    / "DIAGNOSTICO_GOBERNANZA_29_RECHAZADOS_PENDIENTES_20260703_221519"
    / "02_RESULTADOS"
    / "DIAGNOSTICO_GOBERNANZA_29_RECHAZADOS_PENDIENTES.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    BASE_AUDITORIAS
    / f"DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in [RESULTADOS, AUDITORIA, REPORTES]:
    carpeta.mkdir(parents=True, exist_ok=True)


def norm(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return texto.strip()


def norm_rut(valor):
    return re.sub(r"[^0-9Kk]", "", str(valor or "")).upper()


def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)

    return h.hexdigest()


def buscar_archivo(nombre):
    encontrados = sorted(
        BASE_AUDITORIAS.rglob(nombre),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not encontrados:
        return None

    return encontrados[0]


def leer_hoja_si_existe(ruta, hoja):
    xl = pd.ExcelFile(ruta, engine="openpyxl")

    if hoja not in xl.sheet_names:
        return pd.DataFrame()

    return pd.read_excel(
        ruta,
        sheet_name=hoja,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )


def leer_todas_hojas(ruta):
    if ruta is None or not ruta.exists():
        return []

    try:
        xl = pd.ExcelFile(ruta, engine="openpyxl")
    except Exception:
        return []

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

        except Exception:
            pass

    return hojas


def unir_unicos(valores):
    salida = []

    for valor in valores:
        texto = str(valor or "").strip()

        if texto and texto.lower() != "nan" and texto not in salida:
            salida.append(texto)

    return " | ".join(salida)


def valores_unicos(df, columna):
    if columna not in df.columns:
        return ""

    return unir_unicos(df[columna].astype(str).tolist())


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

FUENTES = [
    ("BASE_29", ARCHIVO_BASE_29, True),
    ("CLASIFICACION_29", ARCHIVO_CLASIFICACION_29, True),
    ("ADECUACION_2", ARCHIVO_ADECUACION_2, True),
    ("DIAGNOSTICO_27", ARCHIVO_DIAGNOSTICO_27, True),
    ("DESCOMPOSICION_19", ARCHIVO_DESCOMPOSICION_19, False),
    ("DIAGNOSTICO_ANTERIOR_33", DIAGNOSTICO_ANTERIOR, False),
]

faltantes = [
    rol
    for rol, ruta, obligatoria in FUENTES
    if obligatoria and (ruta is None or not ruta.exists())
]

if faltantes:
    raise SystemExit(
        "Faltan fuentes obligatorias: " + " | ".join(faltantes)
    )


fuentes_df = pd.DataFrame([
    {
        "ROL": rol,
        "RUTA": str(ruta) if ruta else "",
        "EXISTE": bool(ruta and ruta.exists()),
        "OBLIGATORIA": obligatoria,
        "SHA256": sha256(ruta) if ruta and ruta.exists() else "",
        "TAMANO_BYTES": ruta.stat().st_size if ruta and ruta.exists() else "",
    }
    for rol, ruta, obligatoria in FUENTES
])

fuentes_df.to_csv(
    AUDITORIA / "01_FUENTES_REVISADAS.tsv",
    sep="\t",
    index=False,
)


# -------------------------------------------------------------------
# 1. Reconstruir universo base por ID_FILA_5809, no por todos los RUT.
# -------------------------------------------------------------------

registros_base = []

for df in leer_todas_hojas(ARCHIVO_BASE_29):
    if "ID_FILA_5809" not in df.columns:
        continue

    for _, fila in df.iterrows():
        id_fila = norm(fila.get("ID_FILA_5809", ""))

        if not id_fila:
            continue

        registros_base.append({
            "ID_FILA_5809": id_fila,
            "HOJA_ORIGEN_BASE": fila.get("__HOJA__", ""),
            "ARCHIVO_ORIGEN_BASE": fila.get("__ARCHIVO__", ""),
            "N_ORDEN_REVISION": fila.get("N_ORDEN_REVISION", ""),
            "RUT_5809_NORMALIZADO": norm_rut(fila.get("RUT_5809_NORMALIZADO", "")),
            "RUT_EVIDENCIA_NORMALIZADO": norm_rut(fila.get("RUT_EVIDENCIA_NORMALIZADO", "")),
            "RUT_5809_FORMATEADO": fila.get("RUT_5809_FORMATEADO", ""),
            "CODCARR_PLAN_VIGENTE": fila.get("CODCARR_PLAN_VIGENTE", ""),
            "CODCARPR_EVIDENCIA": fila.get("CODCARPR_EVIDENCIA", ""),
            "NIVEL_EVIDENCIA": fila.get("NIVEL_EVIDENCIA", ""),
            "DECISION_RECOMENDADA_ORIGINAL": fila.get("DECISION_RECOMENDADA", ""),
            "ESTADO_CIERRE_ORIGINAL": fila.get("ESTADO_CIERRE_RECOMENDADO", ""),
            "CATEGORIA_REVISION_ORIGINAL": fila.get("CATEGORIA_REVISION", ""),
        })

base_detalle = pd.DataFrame(registros_base)

if base_detalle.empty:
    raise SystemExit("No se pudo reconstruir base por ID_FILA_5809.")

base_unica = (
    base_detalle
    .groupby("ID_FILA_5809", as_index=False)
    .agg(
        ARCHIVOS_ORIGEN_BASE=("ARCHIVO_ORIGEN_BASE", unir_unicos),
        HOJAS_ORIGEN_BASE=("HOJA_ORIGEN_BASE", unir_unicos),
        N_ORDEN_REVISION=("N_ORDEN_REVISION", unir_unicos),
        RUT_5809_NORMALIZADO=("RUT_5809_NORMALIZADO", unir_unicos),
        RUT_EVIDENCIA_NORMALIZADO=("RUT_EVIDENCIA_NORMALIZADO", unir_unicos),
        RUT_5809_FORMATEADO=("RUT_5809_FORMATEADO", unir_unicos),
        CODCARR_PLAN_VIGENTE=("CODCARR_PLAN_VIGENTE", unir_unicos),
        CODCARPR_EVIDENCIA=("CODCARPR_EVIDENCIA", unir_unicos),
        NIVEL_EVIDENCIA=("NIVEL_EVIDENCIA", unir_unicos),
        DECISION_RECOMENDADA_ORIGINAL=("DECISION_RECOMENDADA_ORIGINAL", unir_unicos),
        ESTADO_CIERRE_ORIGINAL=("ESTADO_CIERRE_ORIGINAL", unir_unicos),
        CATEGORIA_REVISION_ORIGINAL=("CATEGORIA_REVISION_ORIGINAL", unir_unicos),
    )
)

universo_id = len(base_unica)


# -------------------------------------------------------------------
# 2. Auditoría de por qué antes aparecieron 33 RUT.
# -------------------------------------------------------------------

auditoria_rut = []

for _, fila in base_unica.iterrows():
    id_fila = fila["ID_FILA_5809"]

    ruts = []

    for campo in [
        "RUT_5809_NORMALIZADO",
        "RUT_EVIDENCIA_NORMALIZADO",
        "RUT_5809_FORMATEADO",
    ]:
        for parte in str(fila.get(campo, "")).split("|"):
            r = norm_rut(parte)

            if r:
                ruts.append({
                    "ID_FILA_5809": id_fila,
                    "CAMPO_RUT": campo,
                    "RUT_NORM": r,
                })

    auditoria_rut.extend(ruts)

auditoria_rut_df = pd.DataFrame(auditoria_rut)

if not auditoria_rut_df.empty:
    rut_por_id = (
        auditoria_rut_df
        .groupby("ID_FILA_5809")
        .agg(
            RUTS_DISTINTOS=("RUT_NORM", lambda s: " | ".join(sorted(set(s)))),
            N_RUTS_DISTINTOS=("RUT_NORM", lambda s: len(set(s))),
        )
        .reset_index()
    )
else:
    rut_por_id = pd.DataFrame(columns=["ID_FILA_5809", "RUTS_DISTINTOS", "N_RUTS_DISTINTOS"])

ids_con_mas_de_un_rut = rut_por_id[
    pd.to_numeric(rut_por_id["N_RUTS_DISTINTOS"], errors="coerce").fillna(0).gt(1)
].copy()


# -------------------------------------------------------------------
# 3. Trazabilidad por ID_FILA_5809 en todos los artefactos.
# -------------------------------------------------------------------

trazas = []

for rol, ruta, _ in FUENTES:
    if ruta is None or not ruta.exists():
        continue

    for df in leer_todas_hojas(ruta):
        if "ID_FILA_5809" not in df.columns:
            continue

        df["ID_FILA_5809_NORM"] = df["ID_FILA_5809"].map(norm)

        match = df[df["ID_FILA_5809_NORM"].isin(set(base_unica["ID_FILA_5809"]))].copy()

        if match.empty:
            continue

        match["__ROL_FUENTE__"] = rol
        trazas.append(match)

if trazas:
    trazabilidad = pd.concat(trazas, ignore_index=True, sort=False)
else:
    trazabilidad = pd.DataFrame(columns=["ID_FILA_5809"])


def resumen_id(id_fila, base_row, grupo):
    estado_original = base_row.get("ESTADO_CIERRE_ORIGINAL", "")
    decision_original = base_row.get("DECISION_RECOMENDADA_ORIGINAL", "")
    categoria_original = base_row.get("CATEGORIA_REVISION_ORIGINAL", "")

    estado_asociacion = valores_unicos(grupo, "ESTADO_ASOCIACION_MODELO")
    estado_adecuacion = valores_unicos(grupo, "ESTADO_ADECUACION")
    estado_diagnostico_27 = valores_unicos(grupo, "ESTADO_DIAGNOSTICO_27")
    estado_final_19 = valores_unicos(grupo, "ESTADO_FINAL_19")
    respaldo_real = valores_unicos(grupo, "RESPALDO_REAL")

    codcli = unir_unicos([
        valores_unicos(grupo, "CODCLI_PROMEDIOS_LISTA"),
        valores_unicos(grupo, "CODCLI_MODELO_ASOCIADO"),
        valores_unicos(grupo, "CODCLI_DATOS"),
    ])

    anio_adecuado = valores_unicos(grupo, "ANIO_CURRICULAR_ADECUADO")

    fundamento = unir_unicos([
        valores_unicos(grupo, "FUNDAMENTO_ADECUACION"),
        valores_unicos(grupo, "FUNDAMENTO_ASOCIACION"),
        valores_unicos(grupo, "FUNDAMENTO"),
    ])

    archivos = valores_unicos(grupo, "__ARCHIVO__")
    hojas = valores_unicos(grupo, "__HOJA__")

    original_rechazo = (
        "RECHAZ" in decision_original.upper()
        or "RECHAZ" in estado_original.upper()
    )

    tiene_adecuacion = (
        "ADECUACION_DEMOSTRADA_POR_CODCLI_Y_REPORTE"
        in estado_adecuacion
    )

    tiene_modelo_codcli = (
        "MODELO_CONFIRMADO_POR_CODCLI"
        in estado_asociacion
    )

    if tiene_adecuacion:
        estado_gobernanza = "ADECUADO_POR_CODCLI_Y_REPORTE"
        decision_final = (
            "REVOCAR_RECHAZO_INICIAL"
            if original_rechazo
            else "MANTENER_ADECUACION"
        )
        estado_informe = (
            "Resuelto: adecuación demostrada por CODCLI exacto y reporte individual."
        )

    elif tiene_modelo_codcli:
        estado_gobernanza = "MODELO_CONFIRMADO_SIN_ADECUACION_FORMAL"
        decision_final = "REVISAR"
        estado_informe = (
            "Modelo confirmado por CODCLI, pero no se encontró adecuación formal."
        )

    elif "CANDIDATO_FUERTE" in estado_diagnostico_27:
        estado_gobernanza = "PENDIENTE_CONFIRMACION_PLAN"
        decision_final = "MANTENER_PENDIENTE"
        estado_informe = "Pendiente: requiere confirmación de plan o periodización."

    elif "CANDIDATO_DEBIL" in estado_diagnostico_27:
        estado_gobernanza = "PENDIENTE_DEBIL_NO_CONVERTIR"
        decision_final = "MANTENER_PENDIENTE"
        estado_informe = "Pendiente: no convertir por similitud."

    elif "SIN_MODELO_DEMOSTRADO" in estado_diagnostico_27:
        estado_gobernanza = "PENDIENTE_SIN_MODELO_DEMOSTRADO"
        decision_final = "MANTENER_PENDIENTE"
        estado_informe = "Pendiente: sin modelo demostrado."

    elif "FAMILIA_Y_CARRERA" in respaldo_real:
        estado_gobernanza = "PENDIENTE_INTERMEDIO_FAMILIA_Y_CARRERA"
        decision_final = "MANTENER_PENDIENTE"
        estado_informe = (
            "Pendiente intermedio: familia CODCLI y carrera coinciden, "
            "pero no autorizan conversión automática."
        )

    elif "SOLO_CARRERA" in respaldo_real:
        estado_gobernanza = "PENDIENTE_SOLO_CARRERA"
        decision_final = "MANTENER_PENDIENTE"
        estado_informe = "Pendiente débil: solo coincide carrera."

    else:
        estado_gobernanza = "PENDIENTE_SIN_CIERRE_POSTERIOR_IDENTIFICADO"
        decision_final = "MANTENER_PENDIENTE"
        estado_informe = "Pendiente: sin cierre posterior suficiente."

    return {
        "ID_FILA_5809": id_fila,
        "RUT_5809_NORMALIZADO": base_row.get("RUT_5809_NORMALIZADO", ""),
        "RUT_EVIDENCIA_NORMALIZADO": base_row.get("RUT_EVIDENCIA_NORMALIZADO", ""),
        "RUT_5809_FORMATEADO": base_row.get("RUT_5809_FORMATEADO", ""),
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
        "ESTADO_PARA_INFORMAR_AVANCE": estado_informe,
        "RECHAZO_INICIAL_REVOCADO": (
            "SI" if original_rechazo and tiene_adecuacion else "NO"
        ),
        "RECHAZO_DEFINITIVO_DEMOSTRADO": "NO",
        "FUENTES_DONDE_APARECE": archivos,
        "HOJAS_DONDE_APARECE": hojas,
        "FUNDAMENTO_GOBERNANZA": fundamento,
    }


filas = []

for _, base_row in base_unica.iterrows():
    id_fila = base_row["ID_FILA_5809"]

    grupo = trazabilidad[
        trazabilidad["ID_FILA_5809"].map(norm).eq(id_fila)
    ].copy()

    filas.append(
        resumen_id(id_fila, base_row, grupo)
    )

final = pd.DataFrame(filas)


resumen_estado = (
    final["ESTADO_GOBERNANZA_FINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_GOBERNANZA_FINAL")
    .reset_index(name="CASOS")
)

resumen_decision = (
    final["DECISION_FINAL_GOBERNANZA"]
    .value_counts(dropna=False)
    .rename_axis("DECISION_FINAL_GOBERNANZA")
    .reset_index(name="CASOS")
)

resumen_original = (
    final["ESTADO_CIERRE_ORIGINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_CIERRE_ORIGINAL")
    .reset_index(name="CASOS")
)

adecuados = final[
    final["ESTADO_GOBERNANZA_FINAL"].eq("ADECUADO_POR_CODCLI_Y_REPORTE")
].copy()

pendientes = final[
    ~final["ESTADO_GOBERNANZA_FINAL"].eq("ADECUADO_POR_CODCLI_Y_REPORTE")
].copy()

revocados = final[
    final["RECHAZO_INICIAL_REVOCADO"].eq("SI")
].copy()


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_BASE_ID_FILA",
        "RESULTADO": "OK" if len(final) == 29 else "REVISAR",
        "DETALLE": len(final),
    },
    {
        "VALIDACION": "UNIVERSO_RUT_INFLADO_PREVIO",
        "RESULTADO": "INFORMATIVO",
        "DETALLE": "El diagnóstico previo por RUT detectó 33 por mezclar RUT 5809/evidencia/formateado.",
    },
    {
        "VALIDACION": "IDS_CON_MAS_DE_UN_RUT",
        "RESULTADO": "INFORMATIVO",
        "DETALLE": len(ids_con_mas_de_un_rut),
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
        "DETALLE": 0,
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


final.to_csv(
    RESULTADOS / "01_DIAGNOSTICO_FINAL_29_POR_ID_FILA.tsv",
    sep="\t",
    index=False,
)

trazabilidad.to_csv(
    RESULTADOS / "02_TRAZABILIDAD_COMPLETA_POR_ID_FILA.tsv",
    sep="\t",
    index=False,
)

base_detalle.to_csv(
    AUDITORIA / "01_BASE_DETALLE_FILAS_ORIGINALES.tsv",
    sep="\t",
    index=False,
)

base_unica.to_csv(
    AUDITORIA / "02_BASE_UNICA_POR_ID_FILA.tsv",
    sep="\t",
    index=False,
)

auditoria_rut_df.to_csv(
    AUDITORIA / "03_AUDITORIA_RUTS_POR_ID.tsv",
    sep="\t",
    index=False,
)

ids_con_mas_de_un_rut.to_csv(
    AUDITORIA / "04_IDS_CON_MAS_DE_UN_RUT.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIA / "05_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


excel = RESULTADOS / "DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    resumen_estado.to_excel(writer, sheet_name="RESUMEN_ESTADO", index=False)
    resumen_decision.to_excel(writer, sheet_name="RESUMEN_DECISION", index=False)
    resumen_original.to_excel(writer, sheet_name="RESUMEN_ORIGINAL", index=False)
    final.to_excel(writer, sheet_name="DIAGNOSTICO_FINAL_29", index=False)
    adecuados.to_excel(writer, sheet_name="ADECUADOS_2", index=False)
    pendientes.to_excel(writer, sheet_name="PENDIENTES_27", index=False)
    revocados.to_excel(writer, sheet_name="RECHAZOS_REVOCADOS", index=False)
    ids_con_mas_de_un_rut.to_excel(writer, sheet_name="IDS_CON_MAS_DE_UN_RUT", index=False)
    trazabilidad.to_excel(writer, sheet_name="TRAZABILIDAD_COMPLETA", index=False)
    fuentes_df.to_excel(writer, sheet_name="FUENTES", index=False)
    validaciones.to_excel(writer, sheet_name="VALIDACIONES", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 60)


informe = REPORTES / "INFORME_GOBERNANZA_29_CORREGIDO_POR_ID_FILA.md"

lineas = []
lineas.append("# Informe de gobernanza corregido por ID_FILA_5809")
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("- Archivo base: REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx")
lineas.append("")
lineas.append("## Corrección metodológica")
lineas.append("")
lineas.append(
    "El diagnóstico anterior por RUT detectó 33 RUT únicos, porque el expediente "
    "contiene distintos campos de RUT: RUT 5809, RUT evidencia y RUT formateado. "
    "Para evitar inflar el universo, el diagnóstico final se reconstruyó usando "
    "`ID_FILA_5809` como llave principal de caso."
)
lineas.append("")
lineas.append("## Resultado ejecutivo")
lineas.append("")
lineas.append(f"- Universo corregido por ID_FILA_5809: **{len(final)} casos**")
lineas.append(f"- Casos adecuados por CODCLI y reporte: **{len(adecuados)}**")
lineas.append(f"- Casos pendientes: **{len(pendientes)}**")
lineas.append(f"- Rechazos iniciales revocados: **{len(revocados)}**")
lineas.append("- Rechazos definitivos demostrados: **0**")
lineas.append("")
lineas.append("## Estados finales")
lineas.append("")
lineas.append(resumen_estado.to_markdown(index=False))
lineas.append("")
lineas.append("## Decisiones finales")
lineas.append("")
lineas.append(resumen_decision.to_markdown(index=False))
lineas.append("")
lineas.append("## Interpretación funcional")
lineas.append("")
lineas.append(
    "El archivo original de rechazados y pendientes debe tratarse como un estado "
    "preliminar. La gobernanza posterior revocó técnicamente los rechazos de los "
    "casos con adecuación demostrada por CODCLI exacto y reporte individual. "
    "Los demás casos permanecen pendientes; no corresponde convertirlos por "
    "similitud de carrera, familia CODCLI o nivel dentro de rango."
)
lineas.append("")
lineas.append("## Archivos")
lineas.append("")
lineas.append(f"- Excel: `{excel}`")
lineas.append(f"- TSV: `{RESULTADOS / '01_DIAGNOSTICO_FINAL_29_POR_ID_FILA.tsv'}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

informe.write_text("\n".join(lineas) + "\n", encoding="utf-8")


manifest = SALIDA / "manifest_gobernanza_29_corregido.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "criterio_universo": "ID_FILA_5809",
            "universo_casos": len(final),
            "casos_adecuados": len(adecuados),
            "casos_pendientes": len(pendientes),
            "rechazos_iniciales_revocados": len(revocados),
            "rechazos_definitivos_demostrados": 0,
            "ids_con_mas_de_un_rut": len(ids_con_mas_de_un_rut),
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


print()
print("=" * 120)
print("DIAGNÓSTICO CORREGIDO — GOBERNANZA 29 POR ID_FILA_5809")
print("=" * 120)
print(f"Universo corregido por ID_FILA_5809: {len(final)}")
print(f"Casos adecuados por CODCLI y reporte: {len(adecuados)}")
print(f"Casos pendientes: {len(pendientes)}")
print(f"Rechazos iniciales revocados: {len(revocados)}")
print("Rechazos definitivos demostrados: 0")
print(f"IDs con más de un RUT observado: {len(ids_con_mas_de_un_rut)}")
print()

print("ESTADOS FINALES")
print("-" * 120)
print(resumen_estado.to_string(index=False))
print()

print("DECISIONES FINALES")
print("-" * 120)
print(resumen_decision.to_string(index=False))
print()

print("VALIDACIONES")
print("-" * 120)
print(validaciones.to_string(index=False))
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
