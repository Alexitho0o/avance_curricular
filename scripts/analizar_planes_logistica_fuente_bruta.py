from pathlib import Path
from datetime import datetime
import json
import hashlib
import unicodedata
import re

import pandas as pd


BASE = Path("/Users/alexi/Documents/GitHub/avance_curricular")

ENTRADA = (
    BASE
    / "avance_curricular_2026/01_fuentes_institucionales/planes_estudio"
    / "Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx"
)

CARPETA_AUDITORIA = (
    BASE
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias"
)

PLANES = ["TLOG20241", "ILOG20241", "CILOG20241"]

TOTALES_ANTERIORES = {
    "TLOG20241": 26,
    "ILOG20241": 30,
    "CILOG20241": 17,
}


def normalizar_columna(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    return texto.strip("_")


def texto_limpio(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def nivel_limpio(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if re.fullmatch(r"\d+\.0", texto):
        return texto[:-2]
    return texto


def sha256(ruta):
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


if not ENTRADA.exists():
    raise SystemExit(f"NO EXISTE LA FUENTE:\n{ENTRADA}")

marca = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    CARPETA_AUDITORIA
    / f"ANALISIS_FUENTE_BRUTA_PLANES_LOGISTICA_{marca}"
)

for subcarpeta in [
    "00_CONTROL",
    "01_INTERMEDIOS",
    "02_RESULTADOS",
    "03_AUDITORIA",
]:
    (SALIDA / subcarpeta).mkdir(parents=True, exist_ok=False)

xls = pd.ExcelFile(ENTRADA)

if "BBDD Bruta" not in xls.sheet_names:
    raise SystemExit(
        "BLOQUEO: no existe la hoja exacta 'BBDD Bruta'.\n"
        f"Hojas observadas: {xls.sheet_names}"
    )

df_original = pd.read_excel(
    ENTRADA,
    sheet_name="BBDD Bruta",
    dtype=str,
)

columnas_originales = list(df_original.columns)
df_original.columns = [
    normalizar_columna(c)
    for c in df_original.columns
]

requeridas = {
    "CODPESTUD",
    "CODRAMO",
    "NOMBRE",
    "NIVEL",
}

faltantes = sorted(requeridas - set(df_original.columns))

if faltantes:
    raise SystemExit(
        "BLOQUEO: faltan columnas requeridas: "
        + ", ".join(faltantes)
    )

for columna in df_original.columns:
    df_original[columna] = (
        df_original[columna]
        .map(texto_limpio)
    )

df_original["CODPESTUD"] = (
    df_original["CODPESTUD"].str.upper()
)

df_original["CODRAMO"] = (
    df_original["CODRAMO"].str.upper()
)

df_original["NIVEL"] = (
    df_original["NIVEL"].map(nivel_limpio)
)

filtrado = df_original[
    df_original["CODPESTUD"].isin(PLANES)
].copy()

if filtrado.empty:
    raise SystemExit(
        "BLOQUEO: no se encontraron los planes "
        + ", ".join(PLANES)
    )

filtrado.insert(
    0,
    "FILA_EXCEL_ORIGINAL",
    filtrado.index + 2,
)

filtrado["LLAVE_PLAN_RAMO_NIVEL"] = (
    filtrado["CODPESTUD"]
    + "||"
    + filtrado["CODRAMO"]
    + "||"
    + filtrado["NIVEL"]
)

sin_codigo = filtrado[
    filtrado["CODRAMO"].eq("")
].copy()

duplicados = filtrado[
    filtrado.duplicated(
        subset=["CODPESTUD", "CODRAMO", "NIVEL"],
        keep=False,
    )
].copy()

duplicados = duplicados.sort_values(
    ["CODPESTUD", "NIVEL", "CODRAMO", "FILA_EXCEL_ORIGINAL"]
)

canonico = (
    filtrado
    .sort_values(
        ["CODPESTUD", "NIVEL", "CODRAMO", "FILA_EXCEL_ORIGINAL"]
    )
    .drop_duplicates(
        subset=["CODPESTUD", "CODRAMO", "NIVEL"],
        keep="first",
    )
    .copy()
)

conteo_nivel = (
    canonico
    .groupby(
        ["CODPESTUD", "NIVEL"],
        dropna=False,
    )
    .agg(
        ASIGNATURAS=("CODRAMO", "size"),
        CODIGOS=("CODRAMO", lambda s: "; ".join(s)),
        NOMBRES=("NOMBRE", lambda s: "; ".join(s)),
    )
    .reset_index()
)

tabla_niveles = (
    conteo_nivel
    .pivot(
        index="NIVEL",
        columns="CODPESTUD",
        values="ASIGNATURAS",
    )
    .fillna(0)
    .astype(int)
    .reset_index()
)

for plan in PLANES:
    if plan not in tabla_niveles.columns:
        tabla_niveles[plan] = 0

def clave_nivel(valor):
    texto = str(valor)
    if texto.isdigit():
        return (0, int(texto))
    return (1, texto)

tabla_niveles["_ORDEN"] = (
    tabla_niveles["NIVEL"].map(clave_nivel)
)

tabla_niveles = (
    tabla_niveles
    .sort_values("_ORDEN")
    .drop(columns="_ORDEN")
)

totales_observados = (
    canonico
    .groupby("CODPESTUD")
    .size()
    .reindex(PLANES, fill_value=0)
)

comparacion = pd.DataFrame({
    "CODPESTUD": PLANES,
    "TOTAL_ANTERIOR": [
        TOTALES_ANTERIORES[p]
        for p in PLANES
    ],
    "TOTAL_FUENTE_BRUTA_DEPURADO": [
        int(totales_observados[p])
        for p in PLANES
    ],
})

comparacion["DIFERENCIA"] = (
    comparacion["TOTAL_FUENTE_BRUTA_DEPURADO"]
    - comparacion["TOTAL_ANTERIOR"]
)

comparacion["ESTADO"] = comparacion["DIFERENCIA"].map(
    lambda x: (
        "COINCIDE"
        if x == 0
        else "REQUIERE_CONCILIACION"
    )
)

resumen = pd.DataFrame([
    {
        "INDICADOR": "Filas fuente completa",
        "VALOR": len(df_original),
    },
    {
        "INDICADOR": "Filas brutas tres planes",
        "VALOR": len(filtrado),
    },
    {
        "INDICADOR": "Filas canónicas depuradas",
        "VALOR": len(canonico),
    },
    {
        "INDICADOR": "Filas duplicadas por llave",
        "VALOR": len(duplicados),
    },
    {
        "INDICADOR": "Filas sin código de ramo",
        "VALOR": len(sin_codigo),
    },
    {
        "INDICADOR": "Planes analizados",
        "VALOR": 3,
    },
    {
        "INDICADOR": "Nivel de respaldo",
        "VALOR": "DATO_OBSERVADO",
    },
    {
        "INDICADOR": "Apto para carga",
        "VALOR": "NO",
    },
])

filtrado.to_csv(
    SALIDA / "01_INTERMEDIOS/01_LOGISTICA_BRUTO_FILTRADO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

canonico.to_csv(
    SALIDA / "02_RESULTADOS/01_LOGISTICA_CANONICO_DEPURADO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

conteo_nivel.to_csv(
    SALIDA / "02_RESULTADOS/02_CONTEO_DETALLADO_POR_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

tabla_niveles.to_csv(
    SALIDA / "02_RESULTADOS/03_TABLA_ASIGNATURAS_POR_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

comparacion.to_csv(
    SALIDA / "02_RESULTADOS/04_COMPARACION_TOTALES_ANTERIORES.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

duplicados.to_csv(
    SALIDA / "03_AUDITORIA/01_DUPLICADOS_PLAN_RAMO_NIVEL.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

sin_codigo.to_csv(
    SALIDA / "03_AUDITORIA/02_FILAS_SIN_CODIGO_RAMO.tsv",
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

excel_salida = (
    SALIDA
    / "02_RESULTADOS/05_ANALISIS_PLANES_LOGISTICA_FUENTE_BRUTA.xlsx"
)

with pd.ExcelWriter(
    excel_salida,
    engine="openpyxl",
) as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    tabla_niveles.to_excel(
        writer,
        sheet_name="ASIGNATURAS_POR_NIVEL",
        index=False,
    )

    comparacion.to_excel(
        writer,
        sheet_name="COMPARACION_TOTALES",
        index=False,
    )

    conteo_nivel.to_excel(
        writer,
        sheet_name="DETALLE_POR_NIVEL",
        index=False,
    )

    canonico.to_excel(
        writer,
        sheet_name="CANONICO_DEPURADO",
        index=False,
    )

    duplicados.to_excel(
        writer,
        sheet_name="DUPLICADOS",
        index=False,
    )

    sin_codigo.to_excel(
        writer,
        sheet_name="SIN_CODIGO_RAMO",
        index=False,
    )

    for hoja in writer.book.worksheets:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for columna in hoja.columns:
            letra = columna[0].column_letter
            ancho = max(
                len(str(celda.value or ""))
                for celda in columna[:1000]
            )
            hoja.column_dimensions[letra].width = min(
                max(ancho + 2, 12),
                55,
            )

manifiesto = {
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Conciliación planes Logística",
    "fuente": str(ENTRADA),
    "hash_sha256": sha256(ENTRADA),
    "hoja": "BBDD Bruta",
    "columnas_originales": columnas_originales,
    "planes": PLANES,
    "llave_depuracion": [
        "CODPESTUD",
        "CODRAMO",
        "NIVEL",
    ],
    "nivel_respaldo": "DATO_OBSERVADO",
    "original_modificado": False,
    "precarga_generada": False,
    "pes_generado": False,
    "apto_para_carga": False,
}

with (
    SALIDA / "00_CONTROL/manifiesto.json"
).open("w", encoding="utf-8") as f:
    json.dump(
        manifiesto,
        f,
        ensure_ascii=False,
        indent=2,
    )

print()
print("ANÁLISIS FUENTE BRUTA LOGÍSTICA COMPLETADO")
print("=" * 72)
print(f"Fuente: {ENTRADA}")
print(f"Salida: {SALIDA}")
print()

print("ASIGNATURAS POR NIVEL")
print(
    tabla_niveles.to_string(
        index=False
    )
)

print()
print("COMPARACIÓN DE TOTALES")
print(
    comparacion.to_string(
        index=False
    )
)

print()
print(f"Filas brutas filtradas: {len(filtrado)}")
print(f"Filas depuradas: {len(canonico)}")
print(f"Duplicados auditados: {len(duplicados)}")
print(f"Filas sin código de ramo: {len(sin_codigo)}")
print()
print(f"Excel: {excel_salida}")
print("Original modificado: NO")
print("Precarga generada: NO")
print("PES generado: NO")
print("Apto para carga: NO")
