#!/usr/bin/env python3
"""Explora fuentes SIES/IPSS y scripts de procesamiento en el workspace."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pandas as pd


PROYECTO = Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025")
RAICES = [PROYECTO, PROYECTO.parent / "_NO_GIT_ARCHIVOS_PESADOS", PROYECTO.parent]
EXTENSIONES = {".csv", ".parquet", ".xlsx", ".py"}
PALABRAS_CLAVE = ("matricula", "matrícula", "titulados", "titulado", "sies", "ipss", "historico", "histórico")
UMBRAL_BYTES = 500 * 1024
COLUMNAS_CLAVE = ("cod_inst", "codigo_inst", "mrun", "anio", "año", "cat_periodo", "codigo_unico", "cod_carrera")


def es_ignorado(path: Path) -> bool:
    return ".git" in path.parts or "__pycache__" in path.parts


def filas_csv(path: Path) -> int | None:
    try:
        with path.open("rb") as stream:
            filas = 0
            for _ in stream:
                filas += 1
        return max(filas - 1, 0)
    except (OSError, UnicodeError):
        return None


def inspeccionar(path: Path) -> tuple[int | None, list[str], str]:
    extension = path.suffix.lower()
    if extension == ".csv":
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                muestra = stream.read(8192)
                stream.seek(0)
                dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t|")
                reader = csv.reader(stream, dialecto)
                columnas = next(reader, [])
            return filas_csv(path), columnas, f"CSV sep={dialecto.delimiter!r}"
        except Exception:
            return filas_csv(path), [], "CSV no inspeccionado"
    if extension == ".parquet":
        try:
            frame = pd.read_parquet(path, engine="pyarrow")
            return len(frame), list(frame.columns), "Parquet"
        except Exception as error:
            return None, [], f"Parquet no inspeccionado: {type(error).__name__}"
    if extension in {".xlsx", ".xls"}:
        try:
            excel = pd.ExcelFile(path)
            columnas = []
            filas = None
            for hoja in excel.sheet_names[:3]:
                frame = pd.read_excel(excel, sheet_name=hoja, nrows=5, header=None)
                filas = filas or None
                columnas.extend(str(value).strip() for value in frame.astype(str).values.ravel() if value != "nan")
            return filas, sorted(set(columnas)), f"Excel hojas={len(excel.sheet_names)}"
        except Exception as error:
            return None, [], f"Excel no inspeccionado: {type(error).__name__}"
    if extension == ".py":
        return None, [], "Python"
    return None, [], ""


def main() -> None:
    encontrados: dict[Path, tuple[int, list[str], str]] = {}
    for raiz in RAICES:
        if not raiz.exists():
            continue
        for root, dirs, files in os.walk(raiz):
            dirs[:] = [name for name in dirs if name not in {".git", "__pycache__"}]
            for name in files:
                path = Path(root) / name
                if path.suffix.lower() not in EXTENSIONES or es_ignorado(path):
                    continue
                size = path.stat().st_size
                if size <= UMBRAL_BYTES and not any(word in name.casefold() for word in PALABRAS_CLAVE):
                    continue
                filas, columnas, tipo = inspeccionar(path)
                encontrados[path.resolve()] = (size, columnas, tipo)

    print("ruta_absoluta\ttipo\ttamano_bytes\tfilas\tcolumnas_clave")
    for path, (size, columnas, tipo) in sorted(encontrados.items(), key=lambda item: item[1][0], reverse=True):
        claves = sorted({col.casefold() for col in columnas} & set(COLUMNAS_CLAVE))
        filas = filas_csv(path) if path.suffix.lower() == ".csv" else "-"
        print(f"{path}\t{tipo}\t{size}\t{filas}\t{','.join(claves) or '-'}")
    print(f"\nTOTAL_CANDIDATOS={len(encontrados)}")


if __name__ == "__main__":
    main()
