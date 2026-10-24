#!/usr/bin/env python3
"""Busca fuentes masivas SIES/IPSS y audita filas y candidatos de origen."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path("/Users/alexi/Documents/GitHub/CARACTERIZACIÓN")
KEYWORDS = ("matricula", "mrun", "retencion", "sies", "ipss", "historico")
EXTENSIONS = {".csv", ".parquet", ".xlsx", ".xls", ".zip", ".gz"}


def count_rows(path: Path) -> int | None:
    if path.suffix.lower() != ".csv":
        return None
    try:
        with path.open("rb") as stream:
            return max(sum(1 for _ in stream) - 1, 0)
    except OSError:
        return None


def main() -> None:
    candidates = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in EXTENSIONS:
            continue
        size = path.stat().st_size
        name_match = any(keyword in path.name.casefold() for keyword in KEYWORDS)
        if size > 1_000_000 or name_match:
            candidates.append((size, path, count_rows(path)))
    candidates.sort(reverse=True, key=lambda item: item[0])
    print(f"CANDIDATOS={len(candidates)}")
    for size, path, rows in candidates:
        print(f"{size}\t{rows if rows is not None else '-'}\t{path}")


if __name__ == "__main__":
    main()