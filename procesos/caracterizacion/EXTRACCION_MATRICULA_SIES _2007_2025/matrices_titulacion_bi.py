#!/usr/bin/env python3
"""Genera matrices agregadas de titulados IPSS 162 para Power BI."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "salida" / "titulados_ipss_162.xlsx"
DEFAULT_OUTPUT = BASE_DIR / "salida" / "Matrices_Titulacion_IPSS_162.xlsx"


def normalizar(texto: object) -> str:
    return " ".join(str(texto).strip().split()).casefold()


def buscar(df: pd.DataFrame, opciones: tuple[str, ...]) -> str | None:
    return next((c for c in df.columns if normalizar(c) in {normalizar(x) for x in opciones}), None)


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    anio = buscar(df, ("Año", "Año del Proceso"))
    codigo = buscar(df, ("Código Institución",))
    if not anio or not codigo:
        raise ValueError("La tabla procesada no contiene Año y Código Institución.")
    df = df.copy()
    df[anio] = pd.to_numeric(df[anio], errors="coerce").round().astype("Int64")
    return df


def agregar_metricas(df: pd.DataFrame, grupo: list[str]) -> pd.DataFrame:
    candidatos = {
        "total_titulaciones": ("Total Titulaciones", "Total de Titulaciones"),
        "titulaciones_mujeres": ("Titulaciones Mujeres por Programa", "Titulaciones Mujeres"),
        "titulaciones_hombres": ("Titulaciones Hombres por Programa", "Titulaciones Hombres"),
        "titulaciones_nb_indefinido": ("Titulaciones NB e Indefinido por Programa", "Titulaciones NB"),
    }
    agregaciones = {}
    for salida, opciones in candidatos.items():
        col = buscar(df, opciones)
        if col:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            agregaciones[salida] = (col, "sum")
    if not agregaciones:
        raise ValueError("No se encontraron contadores de titulaciones en la fuente.")
    return df.groupby(grupo, dropna=False, as_index=False).agg(**agregaciones)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    df = preparar(pd.read_excel(args.entrada, sheet_name=0, dtype="string"))
    anio = buscar(df, ("Año", "Año del Proceso"))
    sede = buscar(df, ("Nombre Sede", "Nombre de Sede"))
    carrera = buscar(df, ("Nombre Carrera", "Nombre de Carrera"))
    programa = buscar(df, ("Código Programa", "Código Único", "Código Unico"))
    if not anio or not sede or not carrera or not programa:
        raise ValueError("Faltan dimensiones requeridas: año, sede, carrera o programa.")
    matrices = {
        "Matriz_Titulados_Anual": agregar_metricas(df, [anio]),
        "Matriz_Titulados_Sede": agregar_metricas(df, [anio, sede]),
        "Matriz_Titulados_Carrera": agregar_metricas(df, [anio, carrera]),
        "Matriz_Titulados_Programa": agregar_metricas(df, [anio, carrera, programa]),
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(args.salida, engine="openpyxl") as writer:
        for nombre, matriz in matrices.items():
            matriz.to_excel(writer, sheet_name=nombre, index=False)
            logging.info("%s: %s filas x %s columnas", nombre, len(matriz), len(matriz.columns))
    logging.info("Matrices exportadas: %s", args.salida)


if __name__ == "__main__":
    main()