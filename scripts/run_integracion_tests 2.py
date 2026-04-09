#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
sys.path.insert(0, str(ROOT))
TESTS = [
    ROOT / "tests/test_sies_resolver.py",
    ROOT / "tests/test_integracion_mu_extranjeros.py",
    ROOT / "tests/test_regresion_mu2026.py",
]


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    total = 0
    failures = []
    for path in TESTS:
        module = load_module(path)
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            total += 1
            try:
                fn()
                print(f"OK {path.name}::{name}")
            except Exception as exc:  # noqa: BLE001 - test runner must report all failures
                failures.append((path.name, name, repr(exc)))
                print(f"FAIL {path.name}::{name}: {exc}")
    print(f"tests_total={total} failures={len(failures)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
