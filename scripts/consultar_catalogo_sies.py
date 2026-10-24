#!/usr/bin/env python3
"""Consulta trazable por ano, sin ejecutar Matricula Unificada."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.catalogos_sies import resolver


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anio", type=int, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--codigo-unico", default="")
    group.add_argument("--codcarpr", default="")
    for field in ("sede", "jornada", "version", "nombre"):
        parser.add_argument(f"--{field}", default="")
    result = resolver(**vars(parser.parse_args()))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["estado"] == "RESUELTO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
