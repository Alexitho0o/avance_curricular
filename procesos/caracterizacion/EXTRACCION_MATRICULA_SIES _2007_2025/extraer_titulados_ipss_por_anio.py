#!/usr/bin/env python3
"""Extrae por chunks los titulados SIES de IPSS 162, un año por ejecución."""

from __future__ import annotations

import argparse
import logging
import re
import unicodedata
from pathlib import Path

import pandas as pd


ONEDRIVE_DIR = Path(
    "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián"
) / "0 BASES DE DATOS" / "TITULACION"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "salida"
CHUNK_SIZE = 100_000
KEYWORDS = ("titulado", "titulados", "titulacion", "titulación", "ed_superior")


def sin_acentos(value: object) -> str:
    text = unicodedata.normalize("NFD", str(value).casefold())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def normalizar_columna(value: object) -> str:
    text = sin_acentos(value)
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def buscar_fuente(anio: int, ruta_explicita: Path | None) -> Path:
    if ruta_explicita is not None:
        if not ruta_explicita.is_file():
            raise FileNotFoundError(f"No existe la fuente indicada: {ruta_explicita}")
        return ruta_explicita
    if not ONEDRIVE_DIR.is_dir():
        raise FileNotFoundError(f"No existe la carpeta OneDrive: {ONEDRIVE_DIR}")
    candidatos = []
    for path in ONEDRIVE_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".csv":
            continue
        nombre = sin_acentos(path.name)
        if str(anio) in nombre and any(keyword in nombre for keyword in KEYWORDS):
            candidatos.append(path)
    if not candidatos:
        raise FileNotFoundError(
            f"No se encontró CSV de titulados para {anio} bajo {ONEDRIVE_DIR}."
        )
    candidatos.sort(key=lambda path: path.stat().st_size, reverse=True)
    if len(candidatos) > 1:
        logging.warning("Se encontraron %s candidatos; se usa el mayor: %s", len(candidatos), candidatos[0])
    return candidatos[0]


def detectar_columna_institucion(columnas: list[str]) -> str:
    opciones = {
        "cod_inst",
        "codigo_institucion",
        "codigo_de_institucion",
        "cod_institucion",
    }
    encontrada = next((col for col in columnas if normalizar_columna(col) in opciones), None)
    if encontrada is None:
        raise ValueError(f"No se detectó código de institución. Columnas: {columnas}")
    return encontrada


def extraer(anio: int, fuente: Path, salida: Path) -> tuple[int, list[str]]:
    logging.info("Año solicitado: %s", anio)
    logging.info("Fuente seleccionada: %s", fuente.resolve())
    encabezado = pd.read_csv(
        fuente,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        nrows=0,
    )
    columnas_originales = list(encabezado.columns)
    columnas_normalizadas = [normalizar_columna(col) for col in columnas_originales]
    columna_inst = detectar_columna_institucion(columnas_normalizadas)
    rename = dict(zip(columnas_originales, columnas_normalizadas))
    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.exists():
        salida.unlink()

    total = 0
    primera_escritura = True
    for numero_bloque, bloque in enumerate(
        pd.read_csv(
            fuente,
            sep=";",
            encoding="utf-8-sig",
            dtype="string",
            chunksize=CHUNK_SIZE,
        ),
        start=1,
    ):
        bloque = bloque.rename(columns=rename)
        codigo = bloque[columna_inst].astype("string").str.strip()
        filtrado = bloque[codigo.eq("162")].copy()
        if filtrado.empty:
            logging.info("Bloque %s: 0 filas IPSS 162", numero_bloque)
            continue
        filtrado.to_csv(
            salida,
            sep=";",
            encoding="utf-8-sig",
            index=False,
            mode="w" if primera_escritura else "a",
            header=primera_escritura,
        )
        primera_escritura = False
        total += len(filtrado)
        logging.info("Bloque %s: %s filas IPSS 162", numero_bloque, f"{len(filtrado):,}".replace(",", "."))

    if primera_escritura:
        pd.DataFrame(columns=columnas_normalizadas).to_csv(
            salida, sep=";", encoding="utf-8-sig", index=False
        )
    logging.info("Total extraído IPSS 162: %s", f"{total:,}".replace(",", "."))
    logging.info("Salida: %s", salida.resolve())
    return total, columnas_normalizadas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anio", type=int, help="Año a procesar, por ejemplo 2025")
    parser.add_argument("--entrada", type=Path, help="Ruta exacta opcional del CSV")
    parser.add_argument("--salida-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    fuente = buscar_fuente(args.anio, args.entrada)
    salida = args.salida_dir / f"titulados_ipss_162_{args.anio}_filtrado.csv"
    total, columnas = extraer(args.anio, fuente, salida)
    print(f"FILAS_IPSS_162={total}")
    print(f"COLUMNAS_MUESTRA={columnas[:12]}")
    print(f"ARCHIVO_SALIDA={salida.resolve()}")
    print(f"BYTES_SALIDA={salida.stat().st_size}")


if __name__ == "__main__":
    main()
