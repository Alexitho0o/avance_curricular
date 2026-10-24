#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "datos"
OUT_DIR = PROJECT_DIR / "salida"
OUT_DIR.mkdir(exist_ok=True)

ENCODINGS = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
DELIMITERS = [";", ",", "\t", "|"]


def read_sample(path: Path, encoding: str, max_lines: int = 5) -> list[str]:
    with path.open("r", encoding=encoding, errors="strict", newline="") as f:
        lines = []
        for _ in range(max_lines):
            line = f.readline()
            if not line:
                break
            lines.append(line.rstrip("\n").rstrip("\r"))
        return lines


def detect_delimiter(sample_lines: list[str]) -> str:
    sample = "\n".join(sample_lines)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter
    except Exception:
        counts = {d: sample.count(d) for d in DELIMITERS}
        return max(counts, key=counts.get)


def analyze_file(path: Path) -> dict:
    result: dict = {
        "archivo": path.name,
        "ruta": str(path),
        "tamano_bytes": path.stat().st_size,
        "encoding_exitoso": None,
        "separador_detectado": None,
        "columnas_detectadas": None,
        "header_preview": None,
        "lineas_muestra": None,
        "estado": "ERROR",
        "detalle": None,
    }

    errors: list[str] = []

    for enc in ENCODINGS:
        try:
            lines = read_sample(path, enc, max_lines=5)
            if not lines:
                result.update(
                    {
                        "encoding_exitoso": enc,
                        "separador_detectado": None,
                        "columnas_detectadas": 0,
                        "header_preview": "",
                        "lineas_muestra": [],
                        "estado": "WARNING",
                        "detalle": "archivo_vacio",
                    }
                )
                return result

            delimiter = detect_delimiter(lines)
            header = lines[0]
            columns = next(csv.reader([header], delimiter=delimiter))
            result.update(
                {
                    "encoding_exitoso": enc,
                    "separador_detectado": "\\t" if delimiter == "\t" else delimiter,
                    "columnas_detectadas": len(columns),
                    "header_preview": header[:500],
                    "lineas_muestra": lines[:3],
                    "estado": "OK",
                    "detalle": None,
                }
            )
            return result
        except Exception as e:
            errors.append(f"{enc}: {type(e).__name__}: {e}")

    result["detalle"] = " | ".join(errors)[:2000]
    return result


def main() -> int:
    if not DATA_DIR.is_dir():
        print(f"[ERROR] No existe la carpeta de datos: {DATA_DIR}", file=sys.stderr)
        return 1

    files = sorted([p for p in DATA_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".csv"])
    if not files:
        print(f"[ERROR] No se encontraron CSV en: {DATA_DIR}", file=sys.stderr)
        return 1

    results = [analyze_file(p) for p in files]

    csv_out = OUT_DIR / "diagnostico_estructura_csv.csv"
    json_out = OUT_DIR / "diagnostico_estructura_csv.json"

    fieldnames = [
        "archivo",
        "ruta",
        "tamano_bytes",
        "encoding_exitoso",
        "separador_detectado",
        "columnas_detectadas",
        "header_preview",
        "lineas_muestra",
        "estado",
        "detalle",
    ]

    with csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            row_copy = row.copy()
            row_copy["lineas_muestra"] = json.dumps(row_copy["lineas_muestra"], ensure_ascii=False)
            writer.writerow(row_copy)

    with json_out.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r["estado"] == "OK")
    warn = sum(1 for r in results if r["estado"] == "WARNING")
    err = sum(1 for r in results if r["estado"] == "ERROR")

    print("======================================================================")
    print("INSPECCIÓN ESTRUCTURAL DE CSV SIES")
    print("======================================================================")
    print(f"Proyecto      : {PROJECT_DIR}")
    print(f"Datos         : {DATA_DIR}")
    print(f"Salida CSV    : {csv_out}")
    print(f"Salida JSON   : {json_out}")
    print("----------------------------------------------------------------------")
    print(f"Archivos OK       : {ok}")
    print(f"Archivos WARNING  : {warn}")
    print(f"Archivos ERROR    : {err}")
    print("----------------------------------------------------------------------")

    for r in results:
        print(f"[{r['estado']}] {r['archivo']}")
        print(f"  encoding   : {r['encoding_exitoso']}")
        print(f"  separador  : {r['separador_detectado']}")
        print(f"  columnas   : {r['columnas_detectadas']}")
        print(f"  header     : {r['header_preview']}")
        if r["detalle"]:
            print(f"  detalle    : {r['detalle']}")
        print("----------------------------------------------------------------------")

    return 0 if ok > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
