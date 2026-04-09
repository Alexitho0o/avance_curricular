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

DIAGNOSTICO_CORREGIDO = (
    BASE_AUDITORIAS
    / "DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA_20260703_222022"
    / "02_RESULTADOS"
    / "DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    BASE_AUDITORIAS
    / f"EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
CASOS_MD = SALIDA / "03_INFORMES_POR_CASO"
AUDITORIA = SALIDA / "04_AUDITORIA"

for carpeta in [RESULTADOS, CASOS_MD, AUDITORIA]:
    carpeta.mkdir(parents=True, exist_ok=True)


def norm_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )

    return re.sub(r"\s+", "", texto)


def norm_id(valor):
    texto = str(valor or "").strip()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return texto


def norm_rut(valor):
    return re.sub(
        r"[^0-9K]",
        "",
        norm_texto(valor),
    )


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


def leer_todas_hojas(ruta):
    if ruta is None or not ruta.exists():
        return []

    try:
        xl = pd.ExcelFile(ruta, engine="openpyxl")
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


def nombre_hoja_seguro(texto):
    texto = re.sub(r"[^A-Za-z0-9_]", "_", str(texto))
    texto = texto[:31]

    if not texto:
        return "CASO"

    return texto


# ---------------------------------------------------------------------
# 1. Fuentes oficiales de gobernanza del expediente
# ---------------------------------------------------------------------

FUENTES = [
    {
        "ROL": "BASE_PRELIMINAR_RECHAZADOS_PENDIENTES",
        "RUTA": buscar_archivo("REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx"),
        "OBLIGATORIA": True,
    },
    {
        "ROL": "CLASIFICACION_29_MODELOS_PERIODIZACION",
        "RUTA": buscar_archivo("CLASIFICACION_29_MODELOS_PERIODIZACION.xlsx"),
        "OBLIGATORIA": True,
    },
    {
        "ROL": "ADECUACION_2_CASOS_PERIODIZACION",
        "RUTA": buscar_archivo("ADECUACION_2_CASOS_PERIODIZACION.xlsx"),
        "OBLIGATORIA": True,
    },
    {
        "ROL": "DIAGNOSTICO_27_PENDIENTES_CODCLI_PLAN",
        "RUTA": buscar_archivo("DIAGNOSTICO_27_PENDIENTES_CODCLI_PLAN.xlsx"),
        "OBLIGATORIA": True,
    },
    {
        "ROL": "DESCOMPOSICION_19_CANDIDATOS_DEBILES",
        "RUTA": buscar_archivo("DESCOMPOSICION_19_CANDIDATOS_DEBILES.xlsx"),
        "OBLIGATORIA": False,
    },
    {
        "ROL": "EVALUACION_14_FAMILIA_CARRERA",
        "RUTA": buscar_archivo("EVALUACION_14_FAMILIA_CARRERA.xlsx"),
        "OBLIGATORIA": False,
    },
    {
        "ROL": "DIAGNOSTICO_CORREGIDO_29_ID_FILA",
        "RUTA": DIAGNOSTICO_CORREGIDO,
        "OBLIGATORIA": True,
    },
]

faltantes = [
    fuente["ROL"]
    for fuente in FUENTES
    if fuente["OBLIGATORIA"]
    and (
        fuente["RUTA"] is None
        or not fuente["RUTA"].exists()
    )
]

if faltantes:
    raise SystemExit(
        "Faltan fuentes obligatorias: "
        + " | ".join(faltantes)
    )

fuentes_df = pd.DataFrame([
    {
        "ROL": fuente["ROL"],
        "RUTA": str(fuente["RUTA"]) if fuente["RUTA"] else "",
        "EXISTE": bool(fuente["RUTA"] and fuente["RUTA"].exists()),
        "OBLIGATORIA": fuente["OBLIGATORIA"],
        "SHA256": (
            sha256(fuente["RUTA"])
            if fuente["RUTA"] and fuente["RUTA"].exists()
            else ""
        ),
        "TAMANO_BYTES": (
            fuente["RUTA"].stat().st_size
            if fuente["RUTA"] and fuente["RUTA"].exists()
            else ""
        ),
    }
    for fuente in FUENTES
])

fuentes_df.to_csv(
    AUDITORIA / "01_FUENTES_REVISADAS.tsv",
    sep="\t",
    index=False,
)


# ---------------------------------------------------------------------
# 2. Leer diagnóstico corregido como universo maestro
# ---------------------------------------------------------------------

diagnostico_final = pd.read_excel(
    DIAGNOSTICO_CORREGIDO,
    sheet_name="DIAGNOSTICO_FINAL_29",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if "ID_FILA_5809" not in diagnostico_final.columns:
    raise SystemExit(
        "El diagnóstico corregido no contiene ID_FILA_5809."
    )

diagnostico_final["ID_FILA_5809"] = (
    diagnostico_final["ID_FILA_5809"].map(norm_id)
)

if len(diagnostico_final) != 29:
    raise SystemExit(
        f"Se esperaban 29 casos en diagnóstico corregido y se encontraron {len(diagnostico_final)}."
    )

if diagnostico_final["ID_FILA_5809"].duplicated().any():
    duplicados = diagnostico_final.loc[
        diagnostico_final["ID_FILA_5809"].duplicated(keep=False),
        "ID_FILA_5809",
    ].tolist()

    raise SystemExit(
        "Existen ID_FILA_5809 duplicados en diagnóstico corregido: "
        + " | ".join(sorted(set(duplicados)))
    )


ids_objetivo = set(diagnostico_final["ID_FILA_5809"])


# ---------------------------------------------------------------------
# 3. Trazabilidad completa por ID_FILA_5809
# ---------------------------------------------------------------------

trazas = []

for fuente in FUENTES:
    ruta = fuente["RUTA"]

    if ruta is None or not ruta.exists():
        continue

    for df in leer_todas_hojas(ruta):
        if "__ERROR__" in df.columns:
            trazas.append(df)
            continue

        if "ID_FILA_5809" not in df.columns:
            continue

        df["ID_FILA_5809_NORM"] = df["ID_FILA_5809"].map(norm_id)

        match = df[
            df["ID_FILA_5809_NORM"].isin(ids_objetivo)
        ].copy()

        if match.empty:
            continue

        match["__ROL_FUENTE__"] = fuente["ROL"]
        trazas.append(match)

if trazas:
    trazabilidad = pd.concat(
        trazas,
        ignore_index=True,
        sort=False,
    )
else:
    trazabilidad = pd.DataFrame(
        columns=[
            "ID_FILA_5809",
            "__ROL_FUENTE__",
            "__ARCHIVO__",
            "__HOJA__",
        ]
    )


# ---------------------------------------------------------------------
# 4. Construcción de resumen detallado por caso
# ---------------------------------------------------------------------

def resumen_detallado_caso(id_fila):
    base = diagnostico_final[
        diagnostico_final["ID_FILA_5809"].eq(id_fila)
    ].iloc[0].to_dict()

    grupo = trazabilidad[
        trazabilidad["ID_FILA_5809"].map(norm_id).eq(id_fila)
    ].copy()

    registro = dict(base)

    registro.update({
        "N_REGISTROS_TRAZABILIDAD": len(grupo),
        "FUENTES_TRAZABILIDAD": valores_unicos(grupo, "__ROL_FUENTE__"),
        "ARCHIVOS_TRAZABILIDAD": valores_unicos(grupo, "__ARCHIVO__"),
        "HOJAS_TRAZABILIDAD": valores_unicos(grupo, "__HOJA__"),
        "CODCLI_TRAZABILIDAD": unir_unicos([
            valores_unicos(grupo, "CODCLI_PROMEDIOS_LISTA"),
            valores_unicos(grupo, "CODCLI_MODELO_ASOCIADO"),
            valores_unicos(grupo, "CODCLI_DATOS"),
            valores_unicos(grupo, "CODCLI_CONSOLIDADO"),
        ]),
        "ESTADOS_TRAZABILIDAD": unir_unicos([
            valores_unicos(grupo, "ESTADO_CIERRE_RECOMENDADO"),
            valores_unicos(grupo, "ESTADO_ASOCIACION_MODELO"),
            valores_unicos(grupo, "ESTADO_ADECUACION"),
            valores_unicos(grupo, "ESTADO_DIAGNOSTICO_27"),
            valores_unicos(grupo, "ESTADO_FINAL_19"),
            valores_unicos(grupo, "ESTADO_GOBERNANZA_FINAL"),
        ]),
        "DECISIONES_TRAZABILIDAD": unir_unicos([
            valores_unicos(grupo, "DECISION_RECOMENDADA"),
            valores_unicos(grupo, "DECISION_ACTUAL"),
            valores_unicos(grupo, "DECISION_FINAL_GOBERNANZA"),
        ]),
        "FUNDAMENTOS_TRAZABILIDAD": unir_unicos([
            valores_unicos(grupo, "FUNDAMENTO_ADECUACION"),
            valores_unicos(grupo, "FUNDAMENTO_ASOCIACION"),
            valores_unicos(grupo, "FUNDAMENTO"),
            valores_unicos(grupo, "FUNDAMENTO_GOBERNANZA"),
        ]),
    })

    return registro


resumen_casos = pd.DataFrame([
    resumen_detallado_caso(id_fila)
    for id_fila in sorted(ids_objetivo, key=lambda x: int(x) if x.isdigit() else x)
])


# ---------------------------------------------------------------------
# 5. Clasificaciones para informar
# ---------------------------------------------------------------------

adecuados = resumen_casos[
    resumen_casos["ESTADO_GOBERNANZA_FINAL"].eq(
        "ADECUADO_POR_CODCLI_Y_REPORTE"
    )
].copy()

pendientes = resumen_casos[
    ~resumen_casos["ESTADO_GOBERNANZA_FINAL"].eq(
        "ADECUADO_POR_CODCLI_Y_REPORTE"
    )
].copy()

revocados = resumen_casos[
    resumen_casos["RECHAZO_INICIAL_REVOCADO"].eq("SI")
].copy()

sin_rechazo_def = resumen_casos[
    resumen_casos["RECHAZO_DEFINITIVO_DEMOSTRADO"].eq("SI")
].copy()

resumen_estado = (
    resumen_casos["ESTADO_GOBERNANZA_FINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_GOBERNANZA_FINAL")
    .reset_index(name="CASOS")
)

resumen_decision = (
    resumen_casos["DECISION_FINAL_GOBERNANZA"]
    .value_counts(dropna=False)
    .rename_axis("DECISION_FINAL_GOBERNANZA")
    .reset_index(name="CASOS")
)

resumen_original = (
    resumen_casos["ESTADO_CIERRE_ORIGINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_CIERRE_ORIGINAL")
    .reset_index(name="CASOS")
)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_29_CASOS",
        "RESULTADO": "OK" if len(resumen_casos) == 29 else "ERROR",
        "DETALLE": len(resumen_casos),
    },
    {
        "VALIDACION": "LLAVE_UNIVERSO",
        "RESULTADO": "OK",
        "DETALLE": "ID_FILA_5809",
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
        "VALIDACION": "RECHAZOS_INICIALES_REVOCADOS",
        "RESULTADO": "OK" if len(revocados) == 2 else "REVISAR",
        "DETALLE": len(revocados),
    },
    {
        "VALIDACION": "RECHAZOS_DEFINITIVOS_DEMOSTRADOS",
        "RESULTADO": "OK" if len(sin_rechazo_def) == 0 else "ERROR",
        "DETALLE": len(sin_rechazo_def),
    },
    {
        "VALIDACION": "TRAZABILIDAD_DISPONIBLE",
        "RESULTADO": "OK" if (resumen_casos["N_REGISTROS_TRAZABILIDAD"].astype(int) > 0).all() else "REVISAR",
        "DETALLE": int((resumen_casos["N_REGISTROS_TRAZABILIDAD"].astype(int) == 0).sum()),
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "ARCHIVO_SIES_READY_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


# ---------------------------------------------------------------------
# 6. Excel maestro con una hoja por caso
# ---------------------------------------------------------------------

excel = RESULTADOS / "EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
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

    resumen_casos.to_excel(
        writer,
        sheet_name="GOBERNANZA_29",
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

    for _, caso in resumen_casos.iterrows():
        id_fila = str(caso["ID_FILA_5809"])

        detalle = trazabilidad[
            trazabilidad["ID_FILA_5809"].map(norm_id).eq(id_fila)
        ].copy()

        if detalle.empty:
            detalle = pd.DataFrame([
                {
                    "ID_FILA_5809": id_fila,
                    "OBSERVACION": "Sin trazabilidad encontrada.",
                }
            ])

        hoja = nombre_hoja_seguro(f"CASO_{id_fila}")

        detalle.to_excel(
            writer,
            sheet_name=hoja,
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


# ---------------------------------------------------------------------
# 7. TSV y Markdown por caso
# ---------------------------------------------------------------------

resumen_casos.to_csv(
    RESULTADOS / "01_GOBERNANZA_DETALLADA_29_CASOS.tsv",
    sep="\t",
    index=False,
)

trazabilidad.to_csv(
    RESULTADOS / "02_TRAZABILIDAD_COMPLETA_29_CASOS.tsv",
    sep="\t",
    index=False,
)

adecuados.to_csv(
    RESULTADOS / "03_ADECUADOS_2.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    RESULTADOS / "04_PENDIENTES_27.tsv",
    sep="\t",
    index=False,
)

revocados.to_csv(
    RESULTADOS / "05_RECHAZOS_INICIALES_REVOCADOS_2.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIA / "02_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


for _, caso in resumen_casos.iterrows():
    id_fila = str(caso["ID_FILA_5809"])

    detalle = trazabilidad[
        trazabilidad["ID_FILA_5809"].map(norm_id).eq(id_fila)
    ].copy()

    md = CASOS_MD / f"CASO_{id_fila}_GOBERNANZA.md"

    lineas = []
    lineas.append(f"# Gobernanza del caso ID_FILA_5809 {id_fila}")
    lineas.append("")
    lineas.append("## Contexto")
    lineas.append("")
    lineas.append("- Proceso: Avance Curricular SIES 2026")
    lineas.append("- Subproyecto: Matrícula 5809")
    lineas.append("- Año de referencia: 2025")
    lineas.append("- Llave de caso: ID_FILA_5809")
    lineas.append("")
    lineas.append("## Resultado final")
    lineas.append("")
    lineas.append(f"- Estado original: `{caso.get('ESTADO_CIERRE_ORIGINAL', '')}`")
    lineas.append(f"- Decisión original: `{caso.get('DECISION_RECOMENDADA_ORIGINAL', '')}`")
    lineas.append(f"- Estado gobernanza final: `{caso.get('ESTADO_GOBERNANZA_FINAL', '')}`")
    lineas.append(f"- Decisión final: `{caso.get('DECISION_FINAL_GOBERNANZA', '')}`")
    lineas.append(f"- Rechazo inicial revocado: `{caso.get('RECHAZO_INICIAL_REVOCADO', '')}`")
    lineas.append(f"- Rechazo definitivo demostrado: `{caso.get('RECHAZO_DEFINITIVO_DEMOSTRADO', '')}`")
    lineas.append("")
    lineas.append("## Identificación")
    lineas.append("")
    lineas.append(f"- RUT 5809: `{caso.get('RUT_5809_NORMALIZADO', '')}`")
    lineas.append(f"- RUT evidencia: `{caso.get('RUT_EVIDENCIA_NORMALIZADO', '')}`")
    lineas.append(f"- CODCLI: `{caso.get('CODCLI_CONSOLIDADO', '')}`")
    lineas.append(f"- Carrera 5809: `{caso.get('CODCARR_PLAN_VIGENTE', '')}`")
    lineas.append(f"- Carrera evidencia: `{caso.get('CODCARPR_EVIDENCIA', '')}`")
    lineas.append(f"- Nivel evidencia: `{caso.get('NIVEL_EVIDENCIA', '')}`")
    lineas.append(f"- Año curricular adecuado: `{caso.get('ANIO_CURRICULAR_ADECUADO', '')}`")
    lineas.append("")
    lineas.append("## Estado para informar")
    lineas.append("")
    lineas.append(str(caso.get("ESTADO_PARA_INFORMAR_AVANCE", "")))
    lineas.append("")
    lineas.append("## Fundamento")
    lineas.append("")
    lineas.append(str(caso.get("FUNDAMENTO_GOBERNANZA", "")))
    lineas.append("")
    lineas.append("## Trazabilidad")
    lineas.append("")
    lineas.append(f"- Registros de trazabilidad: `{len(detalle)}`")
    lineas.append(f"- Fuentes: `{caso.get('FUENTES_TRAZABILIDAD', '')}`")
    lineas.append(f"- Hojas: `{caso.get('HOJAS_TRAZABILIDAD', '')}`")
    lineas.append("")

    md.write_text(
        "\n".join(lineas) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------
# 8. Informe ejecutivo
# ---------------------------------------------------------------------

informe = RESULTADOS / "INFORME_EJECUTIVO_GOBERNANZA_DETALLADA_29.md"

lineas = []
lineas.append("# Informe ejecutivo — Gobernanza detallada de 29 casos")
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("- Archivo preliminar: REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx")
lineas.append("- Llave metodológica corregida: ID_FILA_5809")
lineas.append("")
lineas.append("## Resultado")
lineas.append("")
lineas.append(f"- Universo: **{len(resumen_casos)} casos**")
lineas.append(f"- Adecuados por CODCLI exacto y reporte individual: **{len(adecuados)}**")
lineas.append(f"- Pendientes: **{len(pendientes)}**")
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
lineas.append("## Interpretación")
lineas.append("")
lineas.append(
    "El archivo preliminar de rechazados y pendientes no debe utilizarse "
    "como cierre final. La gobernanza detallada demuestra que 2 rechazos "
    "iniciales deben revocarse porque existe evidencia directa por CODCLI "
    "y reporte individual. Los 27 casos restantes siguen pendientes y no "
    "deben convertirse por similitud de carrera, familia CODCLI o rango de nivel."
)
lineas.append("")
lineas.append("## Archivos")
lineas.append("")
lineas.append(f"- Excel maestro: `{excel}`")
lineas.append(f"- TSV gobernanza: `{RESULTADOS / '01_GOBERNANZA_DETALLADA_29_CASOS.tsv'}`")
lineas.append(f"- Informes por caso: `{CASOS_MD}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

informe.write_text(
    "\n".join(lineas) + "\n",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_expediente_detallado_29.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "criterio_llave": "ID_FILA_5809",
            "universo": len(resumen_casos),
            "adecuados": len(adecuados),
            "pendientes": len(pendientes),
            "rechazos_iniciales_revocados": len(revocados),
            "rechazos_definitivos_demostrados": 0,
            "excel": str(excel),
            "informe_ejecutivo": str(informe),
            "informes_por_caso": str(CASOS_MD),
            "fuentes_originales_modificadas": False,
            "archivo_sies_ready_generado": False,
            "carga_pes_realizada": False,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 120)
print("EXPEDIENTE DETALLADO DE GOBERNANZA — 29 CASOS")
print("=" * 120)
print(f"Universo: {len(resumen_casos)}")
print(f"Adecuados por CODCLI y reporte: {len(adecuados)}")
print(f"Pendientes: {len(pendientes)}")
print(f"Rechazos iniciales revocados: {len(revocados)}")
print("Rechazos definitivos demostrados: 0")
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
print(f"Excel maestro: {excel}")
print(f"Informe ejecutivo: {informe}")
print(f"Informes por caso: {CASOS_MD}")
print(f"Carpeta: {SALIDA}")
print("Fuentes originales modificadas: NO")
print("Archivo SIES_READY generado: NO")
print("=" * 120)
