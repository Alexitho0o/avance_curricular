#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoría HITO 4C-P: separación Caracterización/SIES/Longitudinal."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from caracterizacion_sies_historico import (  # noqa: E402
    SIES_AGREGADOS_PATH,
    SIES_MANIFEST_PATH,
    SIES_REQUIRED_MANIFEST_FIELDS,
    cargar_repositorio_sies_versionado,
)


def _extract_bloque_10quater() -> str:
    source = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")
    start = source.index("def _ejecutar_bloque_10quater():")
    end = source.index("\n_ejecutar_bloque_10quater()\n", start)
    return source[start:end]


def _audit_source_contracts() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    source = (ROOT / "caracterizacion.py").read_text(encoding="utf-8")
    body = _extract_bloque_10quater()
    checks = {
        "LONGITUDINAL_SIN_IMPORT_TOP_LEVEL": "from caracterizacion_retencion import calcular_retencion_longitudinal" not in source,
        "LONGITUDINAL_OPT_IN": "CARACTERIZACION_EJECUTAR_LONGITUDINAL" in source,
        "B10BIS_LONGITUDINAL_NO_EJECUTADO_DEFAULT": "LONGITUDINAL_NO_EJECUTADO" in source
        and "Continuidad/retención omitidas en Caracterización normal" in source,
        "SIES_USA_REPOSITORIO_VERSIONADO": "cargar_repositorio_sies_versionado" in body,
        "SIES_NO_RECONSTRUYE_FUENTE": "reporte_matricula_ip_san_sebastian" not in body and "EXTRACCION_MATRICULA_SIES" not in body,
        "SIES_SIN_LLAVES_INDIVIDUALES": not any(
            re.search(pattern, body)
            for pattern in [r"\bMRUN\b", r"\bmrun\b", r"\bRUT\b", r"RUT_", r"_RUT", r"CRUCE_SIES_PERSONA"]
        ),
    }
    for name, ok in checks.items():
        results.append({"control": name, "resultado": "OK" if ok else "ERROR"})
    return results


def _audit_sies_repository() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    try:
        repo = cargar_repositorio_sies_versionado()
    except Exception as exc:  # pragma: no cover - diagnostic path
        return [{"control": "SIES_REPOSITORIO_CARGA", "resultado": "ERROR", "detalle": str(exc)}]
    faltantes = [field for field in SIES_REQUIRED_MANIFEST_FIELDS if field not in repo.manifest]
    results.append({
        "control": "SIES_MANIFEST_CAMPOS_OBLIGATORIOS",
        "resultado": "OK" if not faltantes else "ERROR",
        "detalle": ",".join(faltantes),
    })
    total_manifest = int(repo.manifest.get("TOTAL_REGISTROS", -1))
    total_agregado = int(pd.to_numeric(repo.agregados.get("REGISTROS_SIES", pd.Series(dtype=int)), errors="coerce").fillna(0).sum())
    results.append({
        "control": "SIES_TOTAL_RECONCILIA",
        "resultado": "OK" if total_manifest == total_agregado else "ERROR",
        "detalle": f"manifest={total_manifest};agregado={total_agregado}",
    })
    columnas_identidad = [c for c in repo.agregados.columns if re.search(r"(MRUN|RUT|TOKEN|CODCLI)", c, re.I)]
    results.append({
        "control": "SIES_AGREGADO_SIN_COLUMNAS_IDENTIDAD",
        "resultado": "OK" if not columnas_identidad else "ERROR",
        "detalle": ",".join(columnas_identidad),
    })
    results.append({
        "control": "SIES_ARTEFACTOS_EXISTEN",
        "resultado": "OK" if SIES_MANIFEST_PATH.exists() and SIES_AGREGADOS_PATH.exists() else "ERROR",
        "detalle": f"{SIES_MANIFEST_PATH};{SIES_AGREGADOS_PATH}",
    })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    results = _audit_source_contracts() + _audit_sies_repository()
    status = "OK" if all(row["resultado"] == "OK" for row in results) else "ERROR"
    payload = {"hito": "HITO 4C-P", "estado": status, "controles": results}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
