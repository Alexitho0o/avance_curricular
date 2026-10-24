#!/usr/bin/env python3
"""Audita y genera benchmarking interno desde un informe SIES en Excel."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "Informe_Retencion_SIES_2025.xlsx"
DEFAULT_OUTPUT = BASE_DIR / "Analisis_Retencion_Interna_IPSS.xlsx"
REQUIRED = {
    "anio_cohorte",
    "nivel",
    "tamano_cohorte",
    "retenidos",
    "tasa_retencion_pct",
}


def entero(value: object) -> str:
    """Formatea un conteo con punto como separador de miles."""
    if pd.isna(value):
        return "-"
    return f"{int(round(float(value))):,}".replace(",", ".")


def decimal(value: object) -> str:
    """Formatea un decimal con miles punto y decimales coma."""
    if pd.isna(value):
        return "-"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def configurar_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def leer_informe(ruta: Path) -> pd.DataFrame:
    """Lee todas las hojas y conserva el nombre de origen."""
    logging.info("Cargando informe: %s", ruta)
    hojas = pd.read_excel(ruta, sheet_name=None)
    if not hojas:
        raise ValueError("El archivo no contiene hojas.")
    tablas = []
    for nombre, tabla in hojas.items():
        tabla = tabla.copy()
        tabla.columns = [str(col).strip().lower() for col in tabla.columns]
        tabla["hoja_origen"] = nombre
        tablas.append(tabla)
        logging.info("Hoja %s: %s filas", nombre, entero(len(tabla)))
    datos = pd.concat(tablas, ignore_index=True, sort=False)
    faltantes = sorted(REQUIRED - set(datos.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")
    return datos


def limpiar_datos(datos: pd.DataFrame) -> pd.DataFrame:
    """Normaliza niveles, conteos y tasas; booleanos se convierten a 0/1."""
    datos = datos.copy()
    datos["nivel"] = datos["nivel"].astype("string").str.strip().str.casefold()
    datos["anio_cohorte"] = pd.to_numeric(datos["anio_cohorte"], errors="coerce")
    datos["tasa_retencion_pct"] = pd.to_numeric(datos["tasa_retencion_pct"], errors="coerce")
    for columna in ("tamano_cohorte", "retenidos"):
        datos[columna] = datos[columna].map(
            lambda value: int(value) if isinstance(value, bool) else value
        )
        datos[columna] = (
            pd.to_numeric(datos[columna], errors="coerce")
            .fillna(0)
            .round()
            .astype("int64")
        )
    logging.info("Filas limpias: %s", entero(len(datos)))
    return datos


def auditar_cuadratura(datos: pd.DataFrame) -> pd.DataFrame:
    """Compara la suma del nivel carrera con el nivel institucional por año."""
    institucional = (
        datos[datos["nivel"] == "institucional"]
        .groupby("anio_cohorte", as_index=False)
        .agg(
            tamano_institucional=("tamano_cohorte", "sum"),
            retenidos_institucional=("retenidos", "sum"),
        )
    )
    carreras = (
        datos[datos["nivel"] == "carrera"]
        .groupby("anio_cohorte", as_index=False)
        .agg(
            tamano_suma_carreras=("tamano_cohorte", "sum"),
            retenidos_suma_carreras=("retenidos", "sum"),
        )
    )
    result = institucional.merge(carreras, on="anio_cohorte", how="outer").fillna(0)
    result["diferencia_tamano"] = (
        result["tamano_institucional"] - result["tamano_suma_carreras"]
    )
    result["diferencia_retenidos"] = (
        result["retenidos_institucional"] - result["retenidos_suma_carreras"]
    )
    result["cuadra"] = result["diferencia_tamano"].eq(0) & result["diferencia_retenidos"].eq(0)
    discrepancias = int((~result["cuadra"]).sum())
    logging.info("Años auditados: %s | discrepancias: %s", entero(len(result)), entero(discrepancias))
    return result.sort_values("anio_cohorte")


def obtener_estandar_2024(datos: pd.DataFrame) -> float:
    """Obtiene el estándar institucional 2024 y valida duplicados."""
    filas = datos[(datos["nivel"] == "institucional") & datos["anio_cohorte"].eq(2024)]
    tasas = filas["tasa_retencion_pct"].dropna().unique()
    if len(tasas) == 0:
        raise ValueError("No existe tasa institucional para la cohorte 2024.")
    if len(tasas) > 1:
        raise ValueError(f"Hay múltiples estándares institucionales para 2024: {tasas.tolist()}")
    estandar = float(tasas[0])
    logging.info("Estándar institucional 2024: %s", decimal(estandar))
    return estandar


def ranking_2024(datos: pd.DataFrame, estandar: float) -> pd.DataFrame:
    """Calcula delta contra el estándar y ordena carreras de mayor a menor."""
    carreras = datos[(datos["nivel"] == "carrera") & datos["anio_cohorte"].eq(2024)].copy()
    if carreras.empty:
        raise ValueError("No existen filas de carreras para la cohorte 2024.")
    carreras["Delta_Interno_pct"] = carreras["tasa_retencion_pct"] - estandar
    carreras["Estándar_Institucional_pct"] = estandar
    carreras = carreras.sort_values(
        ["tasa_retencion_pct", "cod_carrera"], ascending=[False, True], na_position="last"
    )
    carreras["ranking"] = range(1, len(carreras) + 1)
    logging.info("Carreras ordenadas para 2024: %s", entero(len(carreras)))
    return carreras


def exportar(cuadratura: pd.DataFrame, ranking: pd.DataFrame, ruta: Path) -> None:
    """Exporta hojas con formatos regionales visibles en Excel."""
    logging.info("Exportando resultados: %s", ruta)
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        cuadratura.to_excel(writer, sheet_name="Cuadratura_Anual", index=False)
        ranking.to_excel(writer, sheet_name="Ranking_Carreras_2024", index=False)
    book = load_workbook(ruta)
    relleno = PatternFill("solid", fgColor="1F497D")
    for hoja in book.worksheets:
        hoja.sheet_view.showGridLines = True
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions
        for celda in hoja[1]:
            celda.fill = relleno
            celda.font = Font(color="FFFFFF", bold=True)
        encabezados = {str(c.value).lower(): c.column for c in hoja[1]}
        for encabezado, columna in encabezados.items():
            if any(palabra in encabezado for palabra in ("tamano", "retenidos", "diferencia", "ranking")):
                for fila in range(2, hoja.max_row + 1):
                    hoja.cell(fila, columna).number_format = "#.##0"
            if any(palabra in encabezado for palabra in ("tasa", "delta", "estándar")):
                for fila in range(2, hoja.max_row + 1):
                    hoja.cell(fila, columna).number_format = "0,00"
        for columna in hoja.columns:
            letra = columna[0].column_letter
            ancho = min(max(len(str(c.value or "")) for c in columna) + 3, 55)
            hoja.column_dimensions[letra].width = max(ancho, 10)
    book.save(ruta)
    logging.info("Exportación exitosa: %s", ruta)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    configurar_logging()
    datos = limpiar_datos(leer_informe(args.entrada))
    cuadratura = auditar_cuadratura(datos)
    estandar = obtener_estandar_2024(datos)
    ranking = ranking_2024(datos, estandar)
    exportar(cuadratura, ranking, args.salida)


if __name__ == "__main__":
    main()