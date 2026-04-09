#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import re

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


def buscar_ultima_matriz():
    carpetas = sorted(
        BASE_AUDITORIAS.glob("PREPARACION_ARCHIVO_SIES_DESDE_GOBERNANZA_29_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not carpetas:
        raise SystemExit(
            "No se encontró carpeta PREPARACION_ARCHIVO_SIES_DESDE_GOBERNANZA_29_*"
        )

    matriz = (
        carpetas[0]
        / "02_RESULTADOS"
        / "MATRIZ_PROBLEMA_SOLUCION_PREPARACION_SIES_29.xlsx"
    )

    if not matriz.exists():
        raise SystemExit(f"No existe matriz de preparación: {matriz}")

    return carpetas[0], matriz


CARPETA_MATRIZ, MATRIZ_29 = buscar_ultima_matriz()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    BASE_AUDITORIAS
    / f"APLICACION_GOBERNANZA_29_SOBRE_5809_{timestamp}"
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


def norm(valor):
    texto = str(valor or "").strip()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    return texto


def detectar_csv(path):
    raw = path.read_bytes()

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",
    ]

    encoding_ok = None
    texto = None

    for enc in codificaciones:
        try:
            texto = raw.decode(enc)
            encoding_ok = enc
            break
        except UnicodeDecodeError:
            continue

    if encoding_ok is None:
        raise RuntimeError("No se pudo detectar codificación del CSV.")

    muestra = texto[:10000]

    try:
        dialecto = csv.Sniffer().sniff(
            muestra,
            delimiters=[";", ",", "\t", "|"],
        )
        delimitador = dialecto.delimiter
    except Exception:
        delimitador = ";"

    lineas = texto.splitlines()

    return {
        "encoding": encoding_ok,
        "delimiter": delimitador,
        "lineas": lineas,
        "texto": texto,
    }


def leer_5809(path):
    perfil = detectar_csv(path)

    # Se lee sin asumir encabezado normativo.
    df_sin_header = pd.read_csv(
        path,
        sep=perfil["delimiter"],
        encoding=perfil["encoding"],
        dtype=str,
        keep_default_na=False,
        header=None,
        engine="python",
    )

    df_sin_header.insert(
        0,
        "FILA_FISICA_CSV_1_BASE",
        range(1, len(df_sin_header) + 1),
    )

    return perfil, df_sin_header


perfil_5809, df_5809 = leer_5809(FUENTE_5809)

matriz = pd.read_excel(
    MATRIZ_29,
    sheet_name="MATRIZ_29",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if len(matriz) != 29:
    raise SystemExit(
        f"Se esperaban 29 casos en MATRIZ_29 y se encontraron {len(matriz)}."
    )

matriz["ID_FILA_5809"] = matriz["ID_FILA_5809"].map(norm)

if matriz["ID_FILA_5809"].duplicated().any():
    duplicados = matriz.loc[
        matriz["ID_FILA_5809"].duplicated(keep=False),
        "ID_FILA_5809",
    ].tolist()

    raise SystemExit(
        "ID_FILA_5809 duplicados en matriz: "
        + " | ".join(sorted(set(duplicados)))
    )


preparables = matriz[
    matriz["PUEDE_PREPARARSE_EN_CANDIDATO"].eq("SI")
].copy()

bloqueados = matriz[
    matriz["BLOQUEA_ARCHIVO_FINAL"].eq("SI")
].copy()

if len(preparables) != 2:
    raise SystemExit(
        f"Se esperaban 2 casos preparables y se encontraron {len(preparables)}."
    )

if len(bloqueados) != 27:
    raise SystemExit(
        f"Se esperaban 27 casos bloqueados y se encontraron {len(bloqueados)}."
    )


# -------------------------------------------------------------------
# Extraer filas físicas de 5809 por ID_FILA_5809.
# Nota metodológica:
# ID_FILA_5809 se trata como identificador de fila de gobernanza.
# No se sobrescribe la precarga ni se genera CSV de carga.
# -------------------------------------------------------------------

filas_5809 = []

for _, caso in matriz.iterrows():
    id_fila = caso["ID_FILA_5809"]

    fila_num = pd.to_numeric(
        pd.Series([id_fila]),
        errors="coerce",
    ).iloc[0]

    if pd.isna(fila_num):
        estado_fila = "ID_FILA_NO_NUMERICO"
        fila_extraida = pd.DataFrame()
    else:
        fila_num = int(fila_num)

        fila_extraida = df_5809[
            df_5809["FILA_FISICA_CSV_1_BASE"].eq(fila_num)
        ].copy()

        estado_fila = (
            "FILA_5809_EXTRAIDA"
            if not fila_extraida.empty
            else "FILA_5809_NO_ENCONTRADA"
        )

    if fila_extraida.empty:
        registro = {
            "ID_FILA_5809": id_fila,
            "ESTADO_EXTRACCION_5809": estado_fila,
        }
    else:
        registro = fila_extraida.iloc[0].to_dict()
        registro["ID_FILA_5809"] = id_fila
        registro["ESTADO_EXTRACCION_5809"] = estado_fila

    filas_5809.append(registro)


filas_5809_df = pd.DataFrame(filas_5809)


aplicacion = matriz.merge(
    filas_5809_df,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

aplicacion["TIPO_APLICACION"] = ""

aplicacion.loc[
    aplicacion["PUEDE_PREPARARSE_EN_CANDIDATO"].eq("SI"),
    "TIPO_APLICACION",
] = "APLICAR_EN_CANDIDATO_DE_TRABAJO"

aplicacion.loc[
    aplicacion["BLOQUEA_ARCHIVO_FINAL"].eq("SI"),
    "TIPO_APLICACION",
] = "NO_APLICAR_MANTENER_BLOQUEADO"

aplicacion["VALOR_A_INCORPORAR"] = ""

aplicacion.loc[
    aplicacion["PUEDE_PREPARARSE_EN_CANDIDATO"].eq("SI"),
    "VALOR_A_INCORPORAR",
] = aplicacion["ANIO_CURRICULAR_ADECUADO"]

aplicacion["CAMPO_DESTINO_SIES"] = "PENDIENTE_CONFIRMAR_CON_ESTRUCTURA_5809"

aplicacion["OBSERVACION_APLICACION"] = ""

aplicacion.loc[
    aplicacion["PUEDE_PREPARARSE_EN_CANDIDATO"].eq("SI"),
    "OBSERVACION_APLICACION",
] = (
    "Caso con solución demostrada. Puede incorporarse a candidato de trabajo, "
    "conservando nivel original y usando año curricular adecuado. No genera SIES_READY."
)

aplicacion.loc[
    aplicacion["BLOQUEA_ARCHIVO_FINAL"].eq("SI"),
    "OBSERVACION_APLICACION",
] = (
    "Caso pendiente. No aplicar conversión. Requiere evidencia adicional antes de carga."
)


resumen = pd.DataFrame([
    {
        "INDICADOR": "Filas totales precarga 5809 leídas sin encabezado",
        "VALOR": len(df_5809),
    },
    {
        "INDICADOR": "Casos gobernanza 29",
        "VALOR": len(matriz),
    },
    {
        "INDICADOR": "Casos aplicables a candidato de trabajo",
        "VALOR": len(preparables),
    },
    {
        "INDICADOR": "Casos bloqueados",
        "VALOR": len(bloqueados),
    },
    {
        "INDICADOR": "Archivo SIES_READY generado",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "CSV de carga generado",
        "VALOR": "NO",
    },
    {
        "INDICADOR": "Fuentes originales modificadas",
        "VALOR": "NO",
    },
])


resumen_aplicacion = (
    aplicacion["TIPO_APLICACION"]
    .value_counts(dropna=False)
    .rename_axis("TIPO_APLICACION")
    .reset_index(name="CASOS")
)

control_extraccion = (
    aplicacion["ESTADO_EXTRACCION_5809"]
    .value_counts(dropna=False)
    .rename_axis("ESTADO_EXTRACCION_5809")
    .reset_index(name="CASOS")
)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_GOBERNANZA_29",
        "RESULTADO": "OK" if len(aplicacion) == 29 else "ERROR",
        "DETALLE": len(aplicacion),
    },
    {
        "VALIDACION": "CASOS_APLICABLES_CANDIDATO",
        "RESULTADO": "OK" if len(preparables) == 2 else "REVISAR",
        "DETALLE": len(preparables),
    },
    {
        "VALIDACION": "CASOS_BLOQUEADOS",
        "RESULTADO": "OK" if len(bloqueados) == 27 else "REVISAR",
        "DETALLE": len(bloqueados),
    },
    {
        "VALIDACION": "FILAS_5809_EXTRAIDAS",
        "RESULTADO": (
            "OK"
            if aplicacion["ESTADO_EXTRACCION_5809"].eq("FILA_5809_EXTRAIDA").all()
            else "REVISAR"
        ),
        "DETALLE": int(
            aplicacion["ESTADO_EXTRACCION_5809"].eq("FILA_5809_EXTRAIDA").sum()
        ),
    },
    {
        "VALIDACION": "ARCHIVO_SIES_READY_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "CSV_CARGA_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


aplicacion.to_csv(
    RESULTADOS / "01_APLICACION_GOBERNANZA_29_SOBRE_5809.tsv",
    sep="\t",
    index=False,
)

aplicacion[
    aplicacion["TIPO_APLICACION"].eq("APLICAR_EN_CANDIDATO_DE_TRABAJO")
].to_csv(
    RESULTADOS / "02_APLICABLES_CANDIDATO_TRABAJO_2.tsv",
    sep="\t",
    index=False,
)

aplicacion[
    aplicacion["TIPO_APLICACION"].eq("NO_APLICAR_MANTENER_BLOQUEADO")
].to_csv(
    RESULTADOS / "03_BLOQUEADOS_27.tsv",
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
        "FUENTE": "MATRIZ_PROBLEMA_SOLUCION_29",
        "RUTA": str(MATRIZ_29),
        "SHA256": sha256(MATRIZ_29),
    },
    {
        "FUENTE": "PRECARGA_5809",
        "RUTA": str(FUENTE_5809),
        "SHA256": sha256(FUENTE_5809),
    },
])

fuentes.to_csv(
    AUDITORIA / "02_FUENTES.tsv",
    sep="\t",
    index=False,
)

perfil = {
    "fuente_5809": str(FUENTE_5809),
    "encoding_detectado": perfil_5809["encoding"],
    "delimitador_detectado": perfil_5809["delimiter"],
    "filas_leidas_sin_header": len(df_5809),
    "columnas_leidas_sin_header_incluye_control": len(df_5809.columns),
    "fuente_original_modificada": False,
}

(AUDITORIA / "03_PERFIL_5809.json").write_text(
    json.dumps(perfil, ensure_ascii=False, indent=2),
    encoding="utf-8",
)


excel = RESULTADOS / "APLICACION_GOBERNANZA_29_SOBRE_5809_PREPARACION.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resumen_aplicacion.to_excel(
        writer,
        sheet_name="RESUMEN_APLICACION",
        index=False,
    )

    control_extraccion.to_excel(
        writer,
        sheet_name="CONTROL_EXTRACCION_5809",
        index=False,
    )

    aplicacion.to_excel(
        writer,
        sheet_name="APLICACION_29",
        index=False,
    )

    aplicacion[
        aplicacion["TIPO_APLICACION"].eq("APLICAR_EN_CANDIDATO_DE_TRABAJO")
    ].to_excel(
        writer,
        sheet_name="APLICABLES_2",
        index=False,
    )

    aplicacion[
        aplicacion["TIPO_APLICACION"].eq("NO_APLICAR_MANTENER_BLOQUEADO")
    ].to_excel(
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


informe = REPORTES / "INFORME_APLICACION_GOBERNANZA_29_SOBRE_5809.md"

lineas = []
lineas.append("# Informe — Aplicación de gobernanza 29 sobre matriz 5809")
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("- Propósito: preparar capa de aplicación sobre la precarga 5809")
lineas.append("")
lineas.append("## Resultado")
lineas.append("")
lineas.append(f"- Casos de gobernanza revisados: **{len(aplicacion)}**")
lineas.append(f"- Casos aplicables a candidato de trabajo: **{len(preparables)}**")
lineas.append(f"- Casos bloqueados: **{len(bloqueados)}**")
lineas.append("- Archivo SIES_READY generado: **NO**")
lineas.append("- CSV de carga generado: **NO**")
lineas.append("")
lineas.append("## Interpretación")
lineas.append("")
lineas.append(
    "La gobernanza permite incorporar 2 casos a un candidato de trabajo, "
    "pero no permite construir el archivo final para SIES porque 27 casos "
    "siguen bloqueados por falta de evidencia de periodización."
)
lineas.append("")
lineas.append("## Archivos")
lineas.append("")
lineas.append(f"- Excel: `{excel}`")
lineas.append(f"- TSV aplicación: `{RESULTADOS / '01_APLICACION_GOBERNANZA_29_SOBRE_5809.tsv'}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

informe.write_text(
    "\n".join(lineas) + "\n",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_aplicacion_gobernanza_29.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "fuente_5809": str(FUENTE_5809),
            "matriz_gobernanza": str(MATRIZ_29),
            "casos_gobernanza": len(aplicacion),
            "casos_aplicables_candidato": len(preparables),
            "casos_bloqueados": len(bloqueados),
            "archivo_sies_ready_generado": False,
            "csv_carga_generado": False,
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
print("APLICACIÓN DE GOBERNANZA 29 SOBRE MATRIZ 5809 — PREPARACIÓN")
print("=" * 120)
print(f"Precarga 5809: {FUENTE_5809}")
print(f"Matriz gobernanza: {MATRIZ_29}")
print(f"Casos revisados: {len(aplicacion)}")
print(f"Casos aplicables a candidato de trabajo: {len(preparables)}")
print(f"Casos bloqueados: {len(bloqueados)}")
print("Archivo SIES_READY generado: NO")
print("CSV de carga generado: NO")
print()

print("RESUMEN APLICACIÓN")
print("-" * 120)
print(resumen_aplicacion.to_string(index=False))
print()

print("CONTROL EXTRACCIÓN 5809")
print("-" * 120)
print(control_extraccion.to_string(index=False))
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
