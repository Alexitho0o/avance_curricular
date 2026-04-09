#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()

BASE_AVANCE = RAIZ / "avance_curricular_2026"

BASE_AUDITORIAS = (
    BASE_AVANCE
    / "04_gobernanza_mallas"
    / "03_auditorias"
)

FUENTE_5809 = (
    BASE_AVANCE
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "5809_Precarga Matrícula Avance Curricular 2026.csv"
)

INSTRUCTIVO = (
    RAIZ
    / "Instructivo_Avance Curricular SIES - 2026.txt"
)

if not FUENTE_5809.exists():
    encontrados = sorted(
        BASE_AVANCE.rglob("5809_Precarga Matrícula Avance Curricular 2026.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if encontrados:
        FUENTE_5809 = encontrados[0]
    else:
        raise SystemExit("No se encontró la precarga 5809.")

if not INSTRUCTIVO.exists():
    encontrados = sorted(
        RAIZ.rglob("Instructivo_Avance Curricular SIES - 2026.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if encontrados:
        INSTRUCTIVO = encontrados[0]
    else:
        raise SystemExit("No se encontró el instructivo oficial de Avance Curricular.")


def buscar_ultima_aplicacion():
    carpetas = sorted(
        BASE_AUDITORIAS.glob("APLICACION_GOBERNANZA_29_SOBRE_5809_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not carpetas:
        raise SystemExit(
            "No se encontró carpeta APLICACION_GOBERNANZA_29_SOBRE_5809_*"
        )

    excel = (
        carpetas[0]
        / "02_RESULTADOS"
        / "APLICACION_GOBERNANZA_29_SOBRE_5809_PREPARACION.xlsx"
    )

    if not excel.exists():
        raise SystemExit(f"No existe Excel de aplicación: {excel}")

    return carpetas[0], excel


CARPETA_APLICACION, EXCEL_APLICACION = buscar_ultima_aplicacion()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    BASE_AUDITORIAS
    / f"IDENTIFICACION_CAMPO_DESTINO_5809_GOBERNANZA_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in [RESULTADOS, AUDITORIA, REPORTES]:
    carpeta.mkdir(parents=True, exist_ok=True)


def sha256(ruta):
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def norm_col(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    return texto.strip("_")


def detectar_csv(path):
    raw = path.read_bytes()

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",
    ]

    texto = None
    encoding_ok = None

    for enc in codificaciones:
        try:
            texto = raw.decode(enc)
            encoding_ok = enc
            break
        except UnicodeDecodeError:
            continue

    if texto is None:
        raise RuntimeError("No se pudo detectar codificación.")

    muestra = texto[:10000]

    try:
        dialecto = csv.Sniffer().sniff(
            muestra,
            delimiters=[";", ",", "\t", "|"],
        )
        delimitador = dialecto.delimiter
    except Exception:
        delimitador = ";"

    return {
        "encoding": encoding_ok,
        "delimiter": delimitador,
        "texto": texto,
        "lineas": texto.splitlines(),
    }


def leer_csv_sin_header(path, perfil):
    df = pd.read_csv(
        path,
        sep=perfil["delimiter"],
        encoding=perfil["encoding"],
        header=None,
        dtype=str,
        keep_default_na=False,
        engine="python",
    )

    df.insert(
        0,
        "FILA_FISICA_CSV_1_BASE",
        range(1, len(df) + 1),
    )

    return df


perfil = detectar_csv(FUENTE_5809)
df_5809 = leer_csv_sin_header(FUENTE_5809, perfil)

aplicacion = pd.read_excel(
    EXCEL_APLICACION,
    sheet_name="APLICACION_29",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if len(aplicacion) != 29:
    raise SystemExit(
        f"Se esperaban 29 casos en aplicación y se encontraron {len(aplicacion)}."
    )

aplicables = aplicacion[
    aplicacion["TIPO_APLICACION"].eq("APLICAR_EN_CANDIDATO_DE_TRABAJO")
].copy()

bloqueados = aplicacion[
    aplicacion["TIPO_APLICACION"].eq("NO_APLICAR_MANTENER_BLOQUEADO")
].copy()

if len(aplicables) != 2:
    raise SystemExit(
        f"Se esperaban 2 aplicables y se encontraron {len(aplicables)}."
    )

if len(bloqueados) != 27:
    raise SystemExit(
        f"Se esperaban 27 bloqueados y se encontraron {len(bloqueados)}."
    )


texto_instructivo = INSTRUCTIVO.read_text(
    encoding="utf-8",
    errors="replace",
)

# -------------------------------------------------------------------
# 1. Detectar posible fila de encabezado dentro de 5809.
# -------------------------------------------------------------------

tokens_campo = [
    "PLAN",
    "ESTUDIO",
    "CURSO",
    "SEM",
    "SEMESTRE",
    "UNIDAD",
    "CURSADA",
    "APROBADA",
    "TOTAL",
    "VIGENCIA",
    "NIVEL",
    "ANIO",
    "AÑO",
    "AVANCE",
]

filas_candidatas = []

for idx, fila in df_5809.iterrows():
    valores = [
        str(v)
        for k, v in fila.items()
        if k != "FILA_FISICA_CSV_1_BASE"
    ]

    texto_fila = " ".join(valores).upper()

    score = sum(
        1
        for token in tokens_campo
        if token in texto_fila
    )

    no_numericos = sum(
        1
        for valor in valores
        if valor and not re.fullmatch(r"-?\d+(\.\d+)?", valor.strip())
    )

    filas_candidatas.append({
        "FILA_FISICA_CSV_1_BASE": fila["FILA_FISICA_CSV_1_BASE"],
        "SCORE_TOKENS": score,
        "NO_NUMERICOS": no_numericos,
        "MUESTRA": " | ".join(valores[:20]),
    })

candidatas_df = pd.DataFrame(filas_candidatas)

candidatas_df = candidatas_df.sort_values(
    ["SCORE_TOKENS", "NO_NUMERICOS"],
    ascending=False,
)

fila_encabezado_probable = None

if (
    not candidatas_df.empty
    and int(candidatas_df.iloc[0]["SCORE_TOKENS"]) >= 3
):
    fila_encabezado_probable = int(
        candidatas_df.iloc[0]["FILA_FISICA_CSV_1_BASE"]
    )


# -------------------------------------------------------------------
# 2. Construir diccionario de columnas.
# -------------------------------------------------------------------

columnas = []

if fila_encabezado_probable:
    fila_header = df_5809[
        df_5809["FILA_FISICA_CSV_1_BASE"].eq(fila_encabezado_probable)
    ].iloc[0]

    nombres = []

    for col in df_5809.columns:
        if col == "FILA_FISICA_CSV_1_BASE":
            continue

        valor = str(fila_header[col]).strip()

        if valor:
            nombres.append(valor)
        else:
            nombres.append(f"COLUMNA_{col}")

    datos_desde = fila_encabezado_probable + 1

else:
    nombres = [
        f"COLUMNA_{i + 1}"
        for i in range(len(df_5809.columns) - 1)
    ]

    datos_desde = 1


for i, nombre in enumerate(nombres, start=1):
    serie = df_5809.iloc[:, i]  # +1 por columna control al inicio

    valores_no_vacios = serie[
        serie.astype(str).str.strip().ne("")
    ]

    muestra = " | ".join(
        valores_no_vacios.astype(str).head(10).tolist()
    )

    columnas.append({
        "ORDEN_CSV_1_BASE": i,
        "NOMBRE_DETECTADO": nombre,
        "NOMBRE_NORM": norm_col(nombre),
        "NO_VACIOS": len(valores_no_vacios),
        "VACIOS": len(serie) - len(valores_no_vacios),
        "MUESTRA_VALORES": muestra,
    })

diccionario = pd.DataFrame(columnas)


# -------------------------------------------------------------------
# 3. Evaluar columnas candidatas como destino.
# -------------------------------------------------------------------

tokens_destino = [
    "ANIO",
    "ANO",
    "AÑO",
    "CURRICULAR",
    "NIVEL",
    "PERIODO",
    "SEMESTRE",
    "PLAN",
    "ESTUDIOS",
    "AVANCE",
]

campos_oficiales_esperados = [
    "PLAN_ESTUDIOS",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

candidatos = []

for _, col in diccionario.iterrows():
    nombre = str(col["NOMBRE_DETECTADO"])
    nombre_norm = str(col["NOMBRE_NORM"])

    score_nombre = sum(
        1
        for token in tokens_destino
        if token in nombre_norm
    )

    apariciones_instructivo = 0

    for campo in campos_oficiales_esperados:
        if campo in texto_instructivo:
            apariciones_instructivo += int(campo in nombre_norm)

    # Búsqueda más amplia por nombre detectado.
    aparece_nombre_en_instructivo = (
        nombre.strip()
        and nombre.strip() in texto_instructivo
    )

    # Penalización: campos conocidos que no son año curricular.
    es_campo_no_destino = nombre_norm in {
        "PLAN_ESTUDIOS",
        "CURSO_1ER_SEM",
        "CURSO_2DO_SEM",
        "UNIDADES_CURSADAS",
        "UNIDADES_APROBADAS",
        "UNID_CURSADAS_TOTAL",
        "UNID_APROBADAS_TOTAL",
        "VIGENCIA",
    }

    candidato = "NO"
    motivo = ""

    if "ANIO" in nombre_norm or "ANO" in nombre_norm:
        candidato = "SI"
        motivo = "Nombre contiene ANIO/ANO."

    elif "NIVEL" in nombre_norm:
        candidato = "REVISAR"
        motivo = "Nombre contiene NIVEL; requiere confirmar si es campo de origen o destino."

    elif "PERIODO" in nombre_norm or "SEMESTRE" in nombre_norm:
        candidato = "REVISAR"
        motivo = "Nombre contiene PERIODO/SEMESTRE; no equivale automáticamente a año curricular."

    elif es_campo_no_destino:
        candidato = "NO"
        motivo = "Campo oficial observado, pero no es destino directo para año curricular adecuado."

    elif score_nombre > 0:
        candidato = "REVISAR"
        motivo = "Nombre contiene token relacionado, pero no demuestra destino."

    else:
        candidato = "NO"
        motivo = "No contiene tokens relacionados con año/nivel/periodización."

    candidatos.append({
        **col.to_dict(),
        "SCORE_DESTINO": score_nombre,
        "APARECE_NOMBRE_EN_INSTRUCTIVO": (
            "SI" if aparece_nombre_en_instructivo else "NO"
        ),
        "CANDIDATO_CAMPO_DESTINO": candidato,
        "MOTIVO_CLASIFICACION": motivo,
    })

candidatos_df = pd.DataFrame(candidatos)

candidatos_revisar = candidatos_df[
    candidatos_df["CANDIDATO_CAMPO_DESTINO"].isin(["SI", "REVISAR"])
].copy()


# -------------------------------------------------------------------
# 4. Decisión técnica controlada.
# -------------------------------------------------------------------

# No se autoriza escribir si no hay un campo explícito tipo año curricular.
campos_si = candidatos_df[
    candidatos_df["CANDIDATO_CAMPO_DESTINO"].eq("SI")
].copy()

if len(campos_si) == 1:
    campo_destino_estado = "CAMPO_DESTINO_CANDIDATO_UNICO_REQUIERE_VALIDACION_FUNCIONAL"
    campo_destino = campos_si.iloc[0]["NOMBRE_DETECTADO"]
    puede_aplicar = "NO_HASTA_VALIDAR_FUNCIONALMENTE"

elif len(campos_si) > 1:
    campo_destino_estado = "MULTIPLES_CAMPOS_DESTINO_CANDIDATOS"
    campo_destino = " | ".join(campos_si["NOMBRE_DETECTADO"].astype(str).tolist())
    puede_aplicar = "NO"

else:
    campo_destino_estado = "NO_EXISTE_CAMPO_DESTINO_EXPLICITO_DETECTADO"
    campo_destino = ""
    puede_aplicar = "NO"


decision = pd.DataFrame([
    {
        "DECISION": "IDENTIFICACION_CAMPO_DESTINO",
        "ESTADO": campo_destino_estado,
        "CAMPO_DESTINO_CANDIDATO": campo_destino,
        "PUEDE_APLICAR_2_CASOS_A_CANDIDATO": puede_aplicar,
        "FUNDAMENTO": (
            "La gobernanza demostró 2 casos aplicables, pero la escritura en 5809 "
            "requiere confirmar el campo destino exacto en la estructura de carga. "
            "No se modifica la precarga ni se genera candidato hasta validar funcionalmente."
        ),
    }
])


resumen = pd.DataFrame([
    {
        "INDICADOR": "Filas precarga 5809 leídas",
        "VALOR": len(df_5809),
    },
    {
        "INDICADOR": "Columnas precarga 5809",
        "VALOR": len(df_5809.columns) - 1,
    },
    {
        "INDICADOR": "Fila de encabezado probable",
        "VALOR": fila_encabezado_probable if fila_encabezado_probable else "NO_DETECTADA",
    },
    {
        "INDICADOR": "Casos aplicables por gobernanza",
        "VALOR": len(aplicables),
    },
    {
        "INDICADOR": "Casos bloqueados por gobernanza",
        "VALOR": len(bloqueados),
    },
    {
        "INDICADOR": "Campo destino confirmado",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "Candidato de trabajo generado",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "SIES_READY generado",
        "VALOR": "NO",
    },
])


validaciones = pd.DataFrame([
    {
        "VALIDACION": "PRECARGA_5809_LEIDA",
        "RESULTADO": "OK",
        "DETALLE": len(df_5809),
    },
    {
        "VALIDACION": "APLICACION_29_LEIDA",
        "RESULTADO": "OK" if len(aplicacion) == 29 else "ERROR",
        "DETALLE": len(aplicacion),
    },
    {
        "VALIDACION": "CASOS_APLICABLES",
        "RESULTADO": "OK" if len(aplicables) == 2 else "REVISAR",
        "DETALLE": len(aplicables),
    },
    {
        "VALIDACION": "CASOS_BLOQUEADOS",
        "RESULTADO": "OK" if len(bloqueados) == 27 else "REVISAR",
        "DETALLE": len(bloqueados),
    },
    {
        "VALIDACION": "CAMPO_DESTINO_CONFIRMADO",
        "RESULTADO": "NO",
        "DETALLE": campo_destino_estado,
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "CANDIDATO_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "SIES_READY_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


diccionario.to_csv(
    RESULTADOS / "01_DICCIONARIO_COLUMNAS_5809.tsv",
    sep="\t",
    index=False,
)

candidatos_df.to_csv(
    RESULTADOS / "02_CLASIFICACION_COLUMNAS_DESTINO.tsv",
    sep="\t",
    index=False,
)

candidatos_revisar.to_csv(
    RESULTADOS / "03_COLUMNAS_CANDIDATAS_REVISAR.tsv",
    sep="\t",
    index=False,
)

decision.to_csv(
    RESULTADOS / "04_DECISION_CAMPO_DESTINO.tsv",
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
        "FUENTE": "PRECARGA_5809",
        "RUTA": str(FUENTE_5809),
        "SHA256": sha256(FUENTE_5809),
    },
    {
        "FUENTE": "INSTRUCTIVO_AVANCE_CURRICULAR",
        "RUTA": str(INSTRUCTIVO),
        "SHA256": sha256(INSTRUCTIVO),
    },
    {
        "FUENTE": "APLICACION_GOBERNANZA_29",
        "RUTA": str(EXCEL_APLICACION),
        "SHA256": sha256(EXCEL_APLICACION),
    },
])

fuentes.to_csv(
    AUDITORIA / "02_FUENTES.tsv",
    sep="\t",
    index=False,
)

perfil_json = {
    "fuente_5809": str(FUENTE_5809),
    "encoding": perfil["encoding"],
    "delimiter": perfil["delimiter"],
    "filas_leidas": len(df_5809),
    "columnas_sin_control": len(df_5809.columns) - 1,
    "fila_encabezado_probable": fila_encabezado_probable,
    "fuentes_originales_modificadas": False,
}

(AUDITORIA / "03_PERFIL_5809.json").write_text(
    json.dumps(perfil_json, ensure_ascii=False, indent=2),
    encoding="utf-8",
)


excel = RESULTADOS / "IDENTIFICACION_CAMPO_DESTINO_5809_GOBERNANZA.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    decision.to_excel(
        writer,
        sheet_name="DECISION",
        index=False,
    )

    diccionario.to_excel(
        writer,
        sheet_name="DICCIONARIO_5809",
        index=False,
    )

    candidatos_df.to_excel(
        writer,
        sheet_name="CLASIFICACION_COLUMNAS",
        index=False,
    )

    candidatos_revisar.to_excel(
        writer,
        sheet_name="COLUMNAS_REVISAR",
        index=False,
    )

    candidatas_df.head(20).to_excel(
        writer,
        sheet_name="ENCABEZADO_PROBABLE",
        index=False,
    )

    aplicacion.to_excel(
        writer,
        sheet_name="APLICACION_29",
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


informe = REPORTES / "INFORME_IDENTIFICACION_CAMPO_DESTINO_5809.md"

lineas = []
lineas.append("# Informe — Identificación de campo destino en 5809")
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("- Objetivo: identificar campo destino para aplicar los 2 casos gobernados")
lineas.append("")
lineas.append("## Resultado")
lineas.append("")
lineas.append(f"- Estado: **{campo_destino_estado}**")
lineas.append(f"- Campo destino candidato: `{campo_destino}`")
lineas.append(f"- Puede aplicar los 2 casos: `{puede_aplicar}`")
lineas.append("- Candidato de trabajo generado: **NO**")
lineas.append("- Archivo SIES_READY generado: **NO**")
lineas.append("")
lineas.append("## Interpretación")
lineas.append("")
lineas.append(
    "La gobernanza de los 29 casos permite preparar 2 casos, pero la estructura "
    "5809 debe confirmar el campo destino exacto antes de escribir cualquier valor. "
    "Esta fase no modifica la precarga y no genera archivo de carga."
)
lineas.append("")
lineas.append("## Archivos")
lineas.append("")
lineas.append(f"- Excel: `{excel}`")
lineas.append(f"- Decisión: `{RESULTADOS / '04_DECISION_CAMPO_DESTINO.tsv'}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

informe.write_text(
    "\n".join(lineas) + "\n",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_identificacion_campo_destino.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "fuente_5809": str(FUENTE_5809),
            "instructivo": str(INSTRUCTIVO),
            "aplicacion_gobernanza": str(EXCEL_APLICACION),
            "campo_destino_estado": campo_destino_estado,
            "campo_destino_candidato": campo_destino,
            "puede_aplicar_2_casos": puede_aplicar,
            "candidato_generado": False,
            "sies_ready_generado": False,
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
print("IDENTIFICACIÓN CAMPO DESTINO 5809 — GOBERNANZA")
print("=" * 120)
print(f"Precarga 5809: {FUENTE_5809}")
print(f"Instructivo: {INSTRUCTIVO}")
print(f"Aplicación gobernanza: {EXCEL_APLICACION}")
print(f"Filas 5809 leídas: {len(df_5809)}")
print(f"Columnas 5809: {len(df_5809.columns) - 1}")
print(f"Fila encabezado probable: {fila_encabezado_probable if fila_encabezado_probable else 'NO_DETECTADA'}")
print()
print(f"Estado campo destino: {campo_destino_estado}")
print(f"Campo destino candidato: {campo_destino if campo_destino else 'NO_CONFIRMADO'}")
print(f"Puede aplicar 2 casos: {puede_aplicar}")
print("Candidato de trabajo generado: NO")
print("Archivo SIES_READY generado: NO")
print()

print("COLUMNAS A REVISAR")
print("-" * 120)

if candidatos_revisar.empty:
    print("No se detectaron columnas candidatas explícitas.")
else:
    print(
        candidatos_revisar[
            [
                "ORDEN_CSV_1_BASE",
                "NOMBRE_DETECTADO",
                "CANDIDATO_CAMPO_DESTINO",
                "MOTIVO_CLASIFICACION",
                "MUESTRA_VALORES",
            ]
        ].to_string(index=False)
    )

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
