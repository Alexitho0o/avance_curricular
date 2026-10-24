#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EXTRACCIÓN DE MATRÍCULA SIES DESDE ARCHIVOS CSV/XLSX/XLS

Lee todos los archivos ubicados en la carpeta `datos` (o en la misma carpeta
si el script se guarda dentro de `datos`), extrae TODAS las columnas reales
del archivo, filtra textualmente por institución `IP SAN SEBASTIAN`
en la columna `nomb_inst`, y exporta el resultado a Excel en Descargas
y a CSV en la carpeta de salida del proyecto.

Requisitos:
    pip install pandas openpyxl
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


# ================================================
# BLOQUE 1 · Rutas del proyecto
# ================================================
BASE_DIR = Path(__file__).resolve().parent

if (BASE_DIR / "datos").exists() and (BASE_DIR / "datos").is_dir():
    DATOS_DIR = BASE_DIR / "datos"
    PROYECTO_DIR = BASE_DIR
elif BASE_DIR.name.lower() == "datos":
    DATOS_DIR = BASE_DIR
    PROYECTO_DIR = BASE_DIR.parent
else:
    DATOS_DIR = BASE_DIR / "datos"
    PROYECTO_DIR = BASE_DIR

SALIDA_DIR = PROYECTO_DIR / "salida"
SALIDA_DIR.mkdir(parents=True, exist_ok=True)

DESCARGAS_DIR = Path.home() / "Downloads"
DESCARGAS_DIR.mkdir(parents=True, exist_ok=True)


# ================================================
# BLOQUE 2 · Configuración general
# ================================================
EXTENSIONES_PERMITIDAS = {".csv", ".xlsx", ".xls"}
ARCHIVO_SALIDA_XLSX = DESCARGAS_DIR / "reporte_matricula_ip_san_sebastian.xlsx"
ARCHIVO_SALIDA_CSV = SALIDA_DIR / "reporte_matricula_ip_san_sebastian.csv"
MAX_FILAS_POR_HOJA = 1_000_000
MOSTRAR_PRIMERAS_FILAS = 10

ENCODINGS_CSV = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
DELIMITADORES_CSV = ",;\t|"


# ================================================
# BLOQUE 3 · Columnas objetivo SIES (por nombre)
# ================================================
# None = leer TODAS las columnas disponibles del archivo.
COLUMNAS_OBJETIVO: Optional[List[str]] = None

# Si True, falla cuando falta alguna columna solicitada en un archivo.
# Si False, toma solo las que existan y sigue.
EXIGIR_TODAS_LAS_COLUMNAS_OBJETIVO = False


# ================================================
# BLOQUE 4 · Filtros configurables
# ================================================
# Requisito explícito del usuario:
# filtrar textualmente por IP SAN SEBASTIAN.
#
# Esto exige coincidencia exacta, después de normalizar espacios y BOM.
FILTROS_EXACTOS: Dict[str, List[str]] = {
    "nomb_inst": ["IP SAN SEBASTIAN"],
}

FILTROS_CONTAINS: Dict[str, List[str]] = {}

# None = exportar TODAS las columnas disponibles tras lectura/filtros.
COLUMNAS_EXPORTAR: Optional[List[str]] = None


# ================================================
# BLOQUE 5 · Utilidades
# ================================================
def normalizar_texto(valor: object) -> str:
    """Normaliza texto para comparar sin ruido."""
    if valor is None:
        return ""
    if pd.isna(valor):
        return ""
    return str(valor).replace("\ufeff", "").replace("\u200b", "").strip()


def normalizar_nombre_columna(nombre: object) -> str:
    """Normaliza nombres de columna sin cambiar su semántica."""
    return normalizar_texto(nombre)


def detectar_delimitador_csv(ruta: Path) -> str:
    """Intenta detectar si el CSV usa coma, punto y coma, tab o pipe."""
    for encoding in ENCODINGS_CSV:
        try:
            with open(ruta, "r", encoding=encoding, newline="") as f:
                muestra = f.read(4096)

            if not muestra.strip():
                return ";"

            dialecto = csv.Sniffer().sniff(muestra, delimiters=DELIMITADORES_CSV)
            return dialecto.delimiter
        except Exception:
            continue

    # En tus archivos reales el separador detectado fue ';'
    return ";"


def leer_encabezado_csv(ruta: Path, delimitador: str, encoding: str) -> List[str]:
    """Lee solo el encabezado del CSV para conocer columnas reales."""
    df_header = pd.read_csv(
        ruta,
        sep=delimitador,
        dtype=str,
        encoding=encoding,
        nrows=0,
        engine="python",
    )
    return [normalizar_nombre_columna(c) for c in df_header.columns]


def resolver_columnas_objetivo(columnas_reales: List[str]) -> List[str]:
    """Resuelve qué columnas se usarán realmente en el archivo actual."""
    if COLUMNAS_OBJETIVO is None:
        return columnas_reales

    columnas_reales_set = set(columnas_reales)
    columnas_pedidas = [normalizar_nombre_columna(c) for c in COLUMNAS_OBJETIVO]
    presentes = [c for c in columnas_pedidas if c in columnas_reales_set]
    faltantes = [c for c in columnas_pedidas if c not in columnas_reales_set]

    if faltantes and EXIGIR_TODAS_LAS_COLUMNAS_OBJETIVO:
        raise KeyError(
            "Faltan columnas objetivo en el archivo. "
            f"Faltantes: {faltantes} | Disponibles: {columnas_reales}"
        )

    return presentes


def leer_archivo_csv(ruta: Path) -> pd.DataFrame:
    """Lee un CSV SIES de forma robusta, por nombre de columna real."""
    delimitador = detectar_delimitador_csv(ruta)
    errores: List[str] = []

    for encoding in ENCODINGS_CSV:
        try:
            columnas_reales = leer_encabezado_csv(ruta, delimitador, encoding)
            columnas_usar = resolver_columnas_objetivo(columnas_reales)

            if not columnas_usar:
                raise RuntimeError(
                    "No hay columnas objetivo utilizables para este archivo. "
                    f"Columnas disponibles: {columnas_reales}"
                )

            df = pd.read_csv(
                ruta,
                sep=delimitador,
                dtype=str,
                encoding=encoding,
                usecols=columnas_usar,
                engine="python",
            )

            df.columns = [normalizar_nombre_columna(c) for c in df.columns]

            print(
                f"    [INFO] CSV leído con encoding={encoding} | "
                f"sep='{delimitador}' | columnas_detectadas={len(columnas_reales)} | "
                f"columnas_usadas={len(df.columns)}"
            )

            if COLUMNAS_OBJETIVO is not None:
                faltantes = [c for c in COLUMNAS_OBJETIVO if c not in columnas_reales]
                if faltantes:
                    print(
                        f"    [WARNING] Columnas objetivo ausentes en {ruta.name}: {faltantes}"
                    )

            return df

        except Exception as e:
            errores.append(f"{encoding}: {e}")

    raise RuntimeError(
        f"No se pudo leer el archivo CSV: {ruta.name}\n" + "\n".join(errores)
    )


def leer_archivo_excel(ruta: Path) -> pd.DataFrame:
    """Lee XLSX/XLS por nombre de columna real."""
    try:
        df = pd.read_excel(ruta, dtype=str)
    except Exception as e:
        raise RuntimeError(f"No se pudo leer el archivo Excel {ruta.name}: {e}") from e

    df.columns = [normalizar_nombre_columna(c) for c in df.columns]
    columnas_reales = list(df.columns)
    columnas_usar = resolver_columnas_objetivo(columnas_reales)

    if not columnas_usar:
        raise RuntimeError(
            "No hay columnas objetivo utilizables para este archivo. "
            f"Columnas disponibles: {columnas_reales}"
        )

    print(
        f"    [INFO] Excel leído | columnas_detectadas={len(columnas_reales)} | "
        f"columnas_usadas={len(columnas_usar)}"
    )

    if COLUMNAS_OBJETIVO is not None:
        faltantes = [c for c in COLUMNAS_OBJETIVO if c not in columnas_reales]
        if faltantes:
            print(f"    [WARNING] Columnas objetivo ausentes en {ruta.name}: {faltantes}")

    return df[columnas_usar].copy()


def leer_archivo_tabular(ruta: Path) -> pd.DataFrame:
    """Lee CSV/XLSX/XLS usando nombres reales de columnas."""
    sufijo = ruta.suffix.lower()

    if sufijo == ".csv":
        return leer_archivo_csv(ruta)

    if sufijo in {".xlsx", ".xls"}:
        return leer_archivo_excel(ruta)

    raise ValueError(f"Extensión no soportada: {ruta.suffix}")


def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica filtros exactos y filtros por contains."""
    resultado = df.copy()

    for columna, valores in FILTROS_EXACTOS.items():
        columna = normalizar_nombre_columna(columna)
        valores_limpios = [normalizar_texto(v) for v in valores if normalizar_texto(v)]
        if not valores_limpios:
            continue
        if columna not in resultado.columns:
            raise KeyError(f"La columna '{columna}' no existe en el DataFrame.")
        serie = resultado[columna].fillna("").map(normalizar_texto)
        resultado = resultado[serie.isin(valores_limpios)]

    for columna, patrones in FILTROS_CONTAINS.items():
        columna = normalizar_nombre_columna(columna)
        patrones_limpios = [normalizar_texto(v) for v in patrones if normalizar_texto(v)]
        if not patrones_limpios:
            continue
        if columna not in resultado.columns:
            raise KeyError(f"La columna '{columna}' no existe en el DataFrame.")
        serie = resultado[columna].fillna("").map(normalizar_texto)
        mascara = pd.Series(False, index=resultado.index)
        for patron in patrones_limpios:
            mascara = mascara | serie.str.contains(
                patron,
                case=False,
                na=False,
                regex=False,
            )
        resultado = resultado[mascara]

    return resultado


def seleccionar_columnas_finales(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve el DataFrame final con el orden de exportación."""
    if not COLUMNAS_EXPORTAR:
        columnas = [c for c in df.columns if c != "ARCHIVO_ORIGEN"]
        columnas.append("ARCHIVO_ORIGEN")
        return df[columnas]

    columnas_exportar_norm = [normalizar_nombre_columna(c) for c in COLUMNAS_EXPORTAR]
    faltantes = [c for c in columnas_exportar_norm if c not in df.columns]
    if faltantes:
        raise KeyError(f"COLUMNAS_EXPORTAR contiene columnas inexistentes: {faltantes}")

    columnas_finales = columnas_exportar_norm.copy()
    if "ARCHIVO_ORIGEN" in df.columns and "ARCHIVO_ORIGEN" not in columnas_finales:
        columnas_finales.append("ARCHIVO_ORIGEN")

    return df[columnas_finales]


def exportar_excel(df: pd.DataFrame, ruta_salida: Path) -> None:
    """Exporta a Excel. Si excede el tamaño de una hoja, divide en varias hojas."""
    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
        if len(df) <= MAX_FILAS_POR_HOJA:
            df.to_excel(writer, sheet_name="resultado", index=False)
            return

        inicio = 0
        hoja = 1
        while inicio < len(df):
            fin = inicio + MAX_FILAS_POR_HOJA
            bloque = df.iloc[inicio:fin]
            bloque.to_excel(writer, sheet_name=f"resultado_{hoja}", index=False)
            inicio = fin
            hoja += 1


# ================================================
# BLOQUE 6 · Descubrimiento de archivos
# ================================================
def obtener_archivos_fuente() -> List[Path]:
    return [
        p for p in sorted(DATOS_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in EXTENSIONES_PERMITIDAS
    ]


# ================================================
# BLOQUE 7 · Proceso principal
# ================================================
def procesar_archivo(ruta: Path) -> pd.DataFrame:
    """Lee un archivo, filtra y devuelve el resultado parcial."""
    df = leer_archivo_tabular(ruta)

    for col in df.columns:
        df[col] = df[col].map(normalizar_texto)

    df = aplicar_filtros(df)
    df["ARCHIVO_ORIGEN"] = ruta.name
    return df


def main() -> None:
    print("=" * 70)
    print("EXTRACCIÓN DE MATRÍCULA SIES")
    print("=" * 70)
    print(f"Script      : {Path(__file__).name}")
    print(f"Proyecto    : {PROYECTO_DIR}")
    print(f"Datos       : {DATOS_DIR}")
    print(f"Salida CSV  : {ARCHIVO_SALIDA_CSV}")
    print(f"Salida XLSX : {ARCHIVO_SALIDA_XLSX}")
    print("-" * 70)
    print("Filtro textual obligatorio:")
    print("  nomb_inst == 'IP SAN SEBASTIAN'")
    print("-" * 70)

    if not DATOS_DIR.exists():
        raise FileNotFoundError(
            f"No existe la carpeta de datos: {DATOS_DIR}\n"
            "Crea la carpeta 'datos' y coloca allí los CSV/XLSX/XLS."
        )

    archivos = obtener_archivos_fuente()
    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos fuente en {DATOS_DIR}\n"
            "Extensiones soportadas: .csv, .xlsx, .xls"
        )

    print(f"Archivos encontrados: {len(archivos)}")
    for archivo in archivos:
        print(f"  - {archivo.name}")

    parciales: List[pd.DataFrame] = []
    errores: List[str] = []

    for i, archivo in enumerate(archivos, start=1):
        print("-" * 70)
        print(f"[{i}/{len(archivos)}] Leyendo: {archivo.name}")
        try:
            parcial = procesar_archivo(archivo)
            print(f"Filas que pasan filtros: {len(parcial):,}")
            parciales.append(parcial)
        except Exception as e:
            mensaje = f"[ERROR] No se pudo procesar {archivo.name}: {e}"
            print(mensaje)
            errores.append(mensaje)

    print("-" * 70)
    print(f"Archivos procesados correctamente: {len(parciales)}")
    print(f"Archivos con error               : {len(errores)}")

    if errores:
        print("Resumen de errores:")
        for err in errores:
            print(f"  - {err}")

    if not parciales:
        raise RuntimeError(
            "Ningún archivo pudo ser procesado correctamente. "
            "Además, con el filtro textual exacto 'IP SAN SEBASTIAN' es posible "
            "que no existan coincidencias si el valor en 'nomb_inst' usa otra forma."
        )

    resultado = pd.concat(parciales, ignore_index=True, sort=False)

    # Normaliza columnas por si distintos archivos aportan subconjuntos distintos
    resultado.columns = [normalizar_nombre_columna(c) for c in resultado.columns]

    resultado = seleccionar_columnas_finales(resultado)

    print("-" * 70)
    print(f"Filas totales exportables: {len(resultado):,}")
    print(f"Columnas finales         : {list(resultado.columns)}")
    print("-" * 70)

    if resultado.empty:
        print(
            "El resultado está vacío. "
            "Con el filtro textual exacto 'IP SAN SEBASTIAN' no hubo coincidencias."
        )
    else:
        print("Vista previa:")
        print(resultado.head(MOSTRAR_PRIMERAS_FILAS).to_string(index=False))

    exportar_excel(resultado, ARCHIVO_SALIDA_XLSX)
    resultado.to_csv(ARCHIVO_SALIDA_CSV, index=False, encoding="utf-8-sig")

    print("-" * 70)
    print(f"Excel generado en Descargas: {ARCHIVO_SALIDA_XLSX}")
    print(f"CSV generado en proyecto   : {ARCHIVO_SALIDA_CSV}")
    print("Proceso terminado correctamente.")


# ================================================
# BLOQUE 8 · Punto de entrada
# ================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProceso cancelado por el usuario.")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR FATAL] {exc}")
        sys.exit(1)