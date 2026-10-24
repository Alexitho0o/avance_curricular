#!/usr/bin/env python3
"""Procesa el archivo oficial de titulados y filtra IPSS (codigo 162)."""

from __future__ import annotations

import argparse
import logging
import unicodedata
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "TITULADO_2025_web_27_05_2026_E.xlsx"
DEFAULT_OUTPUT = BASE_DIR / "salida" / "titulados_ipss_162.xlsx"


def clave(value: object) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(value).casefold()) if unicodedata.category(c) != "Mn")


def nombre_formal(value: object) -> str:
    return " ".join(str(value).strip().split())


def cargar(ruta: Path) -> pd.DataFrame:
    logging.info("Leyendo fuente oficial: %s", ruta)
    excel = pd.ExcelFile(ruta)
    hoja = "in" if "in" in excel.sheet_names else excel.sheet_names[0]
    logging.info("Hoja utilizada: %s", hoja)
    df = pd.read_excel(excel, sheet_name=hoja, dtype="string")
    df.columns = [nombre_formal(c) for c in df.columns]
    return df


def localizar_columnas(df: pd.DataFrame) -> dict[str, str]:
    aliases = {
        "anio": ("ano", "año"),
        "codigo_institucion": ("codigo institucion", "cod institucion"),
        "nombre_institucion": ("nombre institucion",),
    }
    result = {}
    for destino, opciones in aliases.items():
        encontrada = next((col for col in df.columns if clave(col) in {clave(x) for x in opciones}), None)
        if encontrada is None:
            raise ValueError(f"No se encontró columna para {destino}; columnas: {list(df.columns)}")
        result[destino] = encontrada
    return result


def limpiar_y_filtrar(df: pd.DataFrame) -> pd.DataFrame:
    columnas = localizar_columnas(df)
    df = df.copy()
    codigo = df[columnas["codigo_institucion"]].astype("string").str.replace(r"\.0$", "", regex=True).str.strip()
    df = df[codigo.eq("162")].copy()
    logging.info("Registros IPSS 162: %s", f"{len(df):,}".replace(",", "."))
    rename = {col: nombre_formal(col) for col in df.columns}
    df = df.rename(columns=rename)
    for col in df.columns:
        if clave(col) == "ano" or clave(col).startswith("ano "):
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")
    return df.replace({pd.NA: None})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    if not args.entrada.exists():
        raise FileNotFoundError(f"No existe la fuente: {args.entrada}")
    resultado = limpiar_y_filtrar(cargar(args.entrada))
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_excel(args.salida, sheet_name="Titulados_IPSS_162", index=False)
    logging.info("Exportación exitosa: %s (%s filas x %s columnas)", args.salida, len(resultado), len(resultado.columns))


if __name__ == "__main__":
    main()