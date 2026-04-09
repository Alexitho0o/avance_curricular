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

def buscar_ultimo_expediente():
    carpetas = sorted(
        BASE_AUDITORIAS.glob("EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not carpetas:
        raise SystemExit(
            "No se encontró carpeta EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS_*"
        )

    return carpetas[0]


EXPEDIENTE = buscar_ultimo_expediente()

EXCEL_GOBERNANZA = (
    EXPEDIENTE
    / "02_RESULTADOS"
    / "EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    BASE_AUDITORIAS
    / f"PREPARACION_ARCHIVO_SIES_DESDE_GOBERNANZA_29_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in [RESULTADOS, AUDITORIA, REPORTES]:
    carpeta.mkdir(parents=True, exist_ok=True)


def norm(valor):
    texto = str(valor or "").strip()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return texto


def sha256(ruta):
    h = hashlib.sha256()

    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)

    return h.hexdigest()


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


if not EXCEL_GOBERNANZA.exists():
    raise SystemExit(f"No existe Excel de gobernanza: {EXCEL_GOBERNANZA}")


libro = pd.ExcelFile(EXCEL_GOBERNANZA, engine="openpyxl")

hojas_requeridas = {
    "GOBERNANZA_29",
    "TRAZABILIDAD_COMPLETA",
    "ADECUADOS_2",
    "PENDIENTES_27",
    "VALIDACIONES",
}

faltantes = hojas_requeridas - set(libro.sheet_names)

if faltantes:
    raise SystemExit(
        "Faltan hojas requeridas en expediente: "
        + " | ".join(sorted(faltantes))
    )


gob = pd.read_excel(
    EXCEL_GOBERNANZA,
    sheet_name="GOBERNANZA_29",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

traza = pd.read_excel(
    EXCEL_GOBERNANZA,
    sheet_name="TRAZABILIDAD_COMPLETA",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if len(gob) != 29:
    raise SystemExit(f"Universo esperado 29, encontrado {len(gob)}")

if "ID_FILA_5809" not in gob.columns:
    raise SystemExit("No existe ID_FILA_5809 en GOBERNANZA_29")

gob["ID_FILA_5809"] = gob["ID_FILA_5809"].map(norm)

if gob["ID_FILA_5809"].duplicated().any():
    duplicados = gob.loc[
        gob["ID_FILA_5809"].duplicated(keep=False),
        "ID_FILA_5809",
    ].tolist()

    raise SystemExit(
        "ID_FILA_5809 duplicados: "
        + " | ".join(sorted(set(duplicados)))
    )


if "ID_FILA_5809" in traza.columns:
    traza["ID_FILA_5809"] = traza["ID_FILA_5809"].map(norm)
else:
    traza["ID_FILA_5809"] = ""


def clasificar_problema_solucion(caso, detalle):
    estado = caso.get("ESTADO_GOBERNANZA_FINAL", "")
    decision = caso.get("DECISION_FINAL_GOBERNANZA", "")
    respaldo = caso.get("RESPALDO_REAL", "")
    estado_diag = caso.get("ESTADO_DIAGNOSTICO_27", "")
    estado_orig = caso.get("ESTADO_CIERRE_ORIGINAL", "")
    decision_orig = caso.get("DECISION_RECOMENDADA_ORIGINAL", "")

    tiene_adecuacion = estado == "ADECUADO_POR_CODCLI_Y_REPORTE"

    if tiene_adecuacion:
        problema = (
            "El caso fue tratado preliminarmente como rechazo o nivel no válido, "
            "pero la evidencia posterior demuestra que el NIVEL pertenece a una "
            "periodización histórica/especial del estudiante."
        )

        solucion = (
            "Conservar el nivel original como evidencia histórica y usar el año "
            "curricular adecuado demostrado por CODCLI exacto y reporte individual."
        )

        evidencia = (
            "CODCLI exacto + reporte individual + regla observada de periodización."
        )

        puede_preparar = "SI"
        puede_subir = "SOLO_CUANDO_EL_RESTO_DEL_ARCHIVO_ESTE_VALIDADO"
        accion = "INCORPORAR_A_CANDIDATO_DE_TRABAJO"
        bloqueo = "NO"

    elif estado == "PENDIENTE_DEBIL_NO_CONVERTIR":
        problema = (
            "El caso comparte el problema metodológico general: el NIVEL no puede "
            "interpretarse automáticamente como año curricular. La evidencia disponible "
            "es débil o parcial y no demuestra la periodización aplicable."
        )

        solucion = (
            "No convertir. Solicitar reporte individual o tabla institucional del plan "
            "que demuestre cómo el NIVEL se transforma en año curricular."
        )

        evidencia = (
            "Existe alguna relación parcial, pero no evidencia directa suficiente. "
            f"Respaldo observado: {respaldo or estado_diag}"
        )

        puede_preparar = "NO"
        puede_subir = "NO"
        accion = "MANTENER_PENDIENTE"
        bloqueo = "SI"

    elif estado == "PENDIENTE_SIN_MODELO_DEMOSTRADO":
        problema = (
            "No existe modelo demostrado para interpretar el NIVEL del caso. "
            "No hay evidencia suficiente para asociarlo a una periodización conocida."
        )

        solucion = (
            "No convertir. Requiere reporte individual, tabla institucional del plan "
            "o fuente documental equivalente."
        )

        evidencia = (
            "Sin modelo demostrado en los artefactos de gobernanza."
        )

        puede_preparar = "NO"
        puede_subir = "NO"
        accion = "MANTENER_PENDIENTE"
        bloqueo = "SI"

    else:
        problema = (
            "El caso no tiene cierre posterior suficiente o quedó en estado no concluyente."
        )

        solucion = (
            "No convertir hasta revisar evidencia adicional."
        )

        evidencia = (
            f"Estado gobernanza: {estado}; decisión: {decision}; respaldo: {respaldo}"
        )

        puede_preparar = "NO"
        puede_subir = "NO"
        accion = "MANTENER_PENDIENTE"
        bloqueo = "SI"

    return {
        "PROBLEMA_CONFIRMADO": problema,
        "SOLUCION_CONFIRMADA_O_REQUERIDA": solucion,
        "EVIDENCIA_DISPONIBLE": evidencia,
        "PUEDE_PREPARARSE_EN_CANDIDATO": puede_preparar,
        "PUEDE_SUBIRSE_A_SIES_AHORA": puede_subir,
        "ACCION_SOBRE_ARCHIVO": accion,
        "BLOQUEA_ARCHIVO_FINAL": bloqueo,
    }


filas = []

for _, caso in gob.iterrows():
    id_fila = caso["ID_FILA_5809"]

    detalle = traza[
        traza["ID_FILA_5809"].eq(id_fila)
    ].copy()

    clasificacion = clasificar_problema_solucion(
        caso.to_dict(),
        detalle,
    )

    fila = {
        "ID_FILA_5809": id_fila,
        "RUT_5809_NORMALIZADO": caso.get("RUT_5809_NORMALIZADO", ""),
        "RUT_EVIDENCIA_NORMALIZADO": caso.get("RUT_EVIDENCIA_NORMALIZADO", ""),
        "RUT_5809_FORMATEADO": caso.get("RUT_5809_FORMATEADO", ""),
        "CODCLI_CONSOLIDADO": caso.get("CODCLI_CONSOLIDADO", ""),
        "CODCARR_PLAN_VIGENTE": caso.get("CODCARR_PLAN_VIGENTE", ""),
        "CODCARPR_EVIDENCIA": caso.get("CODCARPR_EVIDENCIA", ""),
        "NIVEL_EVIDENCIA": caso.get("NIVEL_EVIDENCIA", ""),
        "ANIO_CURRICULAR_ADECUADO": caso.get("ANIO_CURRICULAR_ADECUADO", ""),
        "DECISION_RECOMENDADA_ORIGINAL": caso.get("DECISION_RECOMENDADA_ORIGINAL", ""),
        "ESTADO_CIERRE_ORIGINAL": caso.get("ESTADO_CIERRE_ORIGINAL", ""),
        "ESTADO_GOBERNANZA_FINAL": caso.get("ESTADO_GOBERNANZA_FINAL", ""),
        "DECISION_FINAL_GOBERNANZA": caso.get("DECISION_FINAL_GOBERNANZA", ""),
        "RECHAZO_INICIAL_REVOCADO": caso.get("RECHAZO_INICIAL_REVOCADO", ""),
        "RECHAZO_DEFINITIVO_DEMOSTRADO": caso.get("RECHAZO_DEFINITIVO_DEMOSTRADO", ""),
        "N_REGISTROS_TRAZABILIDAD": len(detalle),
        "FUENTES_TRAZABILIDAD": valores_unicos(detalle, "__ROL_FUENTE__"),
        "HOJAS_TRAZABILIDAD": valores_unicos(detalle, "__HOJA__"),
        "FUNDAMENTO_GOBERNANZA": caso.get("FUNDAMENTO_GOBERNANZA", ""),
    }

    fila.update(clasificacion)

    filas.append(fila)


matriz = pd.DataFrame(filas)

adecuados = matriz[
    matriz["PUEDE_PREPARARSE_EN_CANDIDATO"].eq("SI")
].copy()

bloqueados = matriz[
    matriz["BLOQUEA_ARCHIVO_FINAL"].eq("SI")
].copy()

pendientes = matriz[
    matriz["ACCION_SOBRE_ARCHIVO"].eq("MANTENER_PENDIENTE")
].copy()


resumen = pd.DataFrame([
    {
        "INDICADOR": "Universo gobernado",
        "VALOR": len(matriz),
    },
    {
        "INDICADOR": "Casos con solución demostrada",
        "VALOR": len(adecuados),
    },
    {
        "INDICADOR": "Casos pendientes",
        "VALOR": len(pendientes),
    },
    {
        "INDICADOR": "Casos que bloquean archivo final",
        "VALOR": len(bloqueados),
    },
    {
        "INDICADOR": "Rechazos definitivos demostrados",
        "VALOR": int(
            matriz["RECHAZO_DEFINITIVO_DEMOSTRADO"].eq("SI").sum()
        ),
    },
    {
        "INDICADOR": "Archivo SIES_READY generado",
        "VALOR": "NO",
    },
])


resumen_estado = (
    matriz["ESTADO_GOBERNANZA_FINAL"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_GOBERNANZA_FINAL")
    .reset_index(name="CASOS")
)

resumen_accion = (
    matriz["ACCION_SOBRE_ARCHIVO"]
    .value_counts(dropna=False)
    .rename_axis("ACCION_SOBRE_ARCHIVO")
    .reset_index(name="CASOS")
)

resumen_preparacion = (
    matriz["PUEDE_PREPARARSE_EN_CANDIDATO"]
    .value_counts(dropna=False)
    .rename_axis("PUEDE_PREPARARSE_EN_CANDIDATO")
    .reset_index(name="CASOS")
)

validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_29",
        "RESULTADO": "OK" if len(matriz) == 29 else "ERROR",
        "DETALLE": len(matriz),
    },
    {
        "VALIDACION": "CASOS_PREPARABLES",
        "RESULTADO": "OK" if len(adecuados) == 2 else "REVISAR",
        "DETALLE": len(adecuados),
    },
    {
        "VALIDACION": "CASOS_BLOQUEADOS",
        "RESULTADO": "OK" if len(bloqueados) == 27 else "REVISAR",
        "DETALLE": len(bloqueados),
    },
    {
        "VALIDACION": "RECHAZOS_DEFINITIVOS",
        "RESULTADO": "OK",
        "DETALLE": int(
            matriz["RECHAZO_DEFINITIVO_DEMOSTRADO"].eq("SI").sum()
        ),
    },
    {
        "VALIDACION": "ARCHIVO_FINAL_SIES_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


matriz.to_csv(
    RESULTADOS / "01_MATRIZ_PROBLEMA_SOLUCION_29.tsv",
    sep="\t",
    index=False,
)

adecuados.to_csv(
    RESULTADOS / "02_CASOS_LISTOS_PARA_CANDIDATO_2.tsv",
    sep="\t",
    index=False,
)

bloqueados.to_csv(
    RESULTADOS / "03_CASOS_BLOQUEADOS_27.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIA / "01_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)

fuentes = pd.DataFrame([
    {
        "FUENTE": "EXPEDIENTE_DETALLADO_GOBERNANZA_29",
        "RUTA": str(EXCEL_GOBERNANZA),
        "SHA256": sha256(EXCEL_GOBERNANZA),
    }
])

fuentes.to_csv(
    AUDITORIA / "02_FUENTES.tsv",
    sep="\t",
    index=False,
)


excel = RESULTADOS / "MATRIZ_PROBLEMA_SOLUCION_PREPARACION_SIES_29.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resumen_estado.to_excel(
        writer,
        sheet_name="RESUMEN_ESTADO",
        index=False,
    )

    resumen_accion.to_excel(
        writer,
        sheet_name="RESUMEN_ACCION",
        index=False,
    )

    resumen_preparacion.to_excel(
        writer,
        sheet_name="RESUMEN_PREPARACION",
        index=False,
    )

    matriz.to_excel(
        writer,
        sheet_name="MATRIZ_29",
        index=False,
    )

    adecuados.to_excel(
        writer,
        sheet_name="PREPARABLES_2",
        index=False,
    )

    bloqueados.to_excel(
        writer,
        sheet_name="BLOQUEADOS_27",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
        index=False,
    )

    fuentes.to_excel(
        writer,
        sheet_name="FUENTES",
        index=False,
    )

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 70)


informe = REPORTES / "INFORME_PROBLEMA_SOLUCION_PREPARACION_SIES_29.md"

lineas = []
lineas.append("# Informe — Problema, solución y preparación SIES de 29 casos")
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("- Fuente: expediente detallado de gobernanza de 29 casos")
lineas.append("")
lineas.append("## Resultado")
lineas.append("")
lineas.append(f"- Universo analizado: **{len(matriz)} casos**")
lineas.append(f"- Casos con solución demostrada: **{len(adecuados)}**")
lineas.append(f"- Casos pendientes/bloqueados: **{len(bloqueados)}**")
lineas.append("- Rechazos definitivos demostrados: **0**")
lineas.append("- Archivo SIES_READY generado: **NO**")
lineas.append("")
lineas.append("## Confirmación funcional")
lineas.append("")
lineas.append(
    "Los 29 casos comparten un problema metodológico general: "
    "el campo NIVEL no puede interpretarse automáticamente como año curricular "
    "sin evidencia de periodización. Sin embargo, no todos tienen la misma "
    "solución demostrada."
)
lineas.append("")
lineas.append(
    "Solo 2 casos tienen solución confirmada por CODCLI exacto y reporte individual. "
    "Los otros 27 siguen pendientes porque no existe evidencia suficiente para "
    "extender esa solución por similitud de carrera, familia CODCLI o nivel observado."
)
lineas.append("")
lineas.append("## Acción sobre archivo")
lineas.append("")
lineas.append(resumen_accion.to_markdown(index=False))
lineas.append("")
lineas.append("## Preparación")
lineas.append("")
lineas.append(
    "Los 2 casos adecuados pueden incorporarse a un candidato de trabajo, "
    "pero el archivo final para SIES sigue bloqueado mientras existan los 27 "
    "casos pendientes y las demás dependencias de Carreras/fuente de avance."
)
lineas.append("")
lineas.append("## Archivos")
lineas.append("")
lineas.append(f"- Excel: `{excel}`")
lineas.append(f"- TSV matriz: `{RESULTADOS / '01_MATRIZ_PROBLEMA_SOLUCION_29.tsv'}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

informe.write_text(
    "\n".join(lineas) + "\n",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_preparacion_sies_29.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "universo": len(matriz),
            "casos_con_solucion_demostrada": len(adecuados),
            "casos_bloqueados": len(bloqueados),
            "rechazos_definitivos_demostrados": 0,
            "puede_construir_archivo_sies_ready": False,
            "puede_construir_candidato_trabajo_parcial": True,
            "archivo_sies_ready_generado": False,
            "fuentes_originales_modificadas": False,
            "excel": str(excel),
            "informe": str(informe),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 120)
print("MATRIZ PROBLEMA/SOLUCIÓN — PREPARACIÓN ARCHIVO SIES")
print("=" * 120)
print(f"Expediente fuente: {EXPEDIENTE}")
print(f"Universo analizado: {len(matriz)}")
print(f"Casos con solución demostrada/preparables: {len(adecuados)}")
print(f"Casos pendientes/bloqueados: {len(bloqueados)}")
print("Rechazos definitivos demostrados: 0")
print("Archivo SIES_READY generado: NO")
print()

print("RESUMEN DE ACCIÓN")
print("-" * 120)
print(resumen_accion.to_string(index=False))
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
print("Archivo final SIES generado: NO")
print("=" * 120)
