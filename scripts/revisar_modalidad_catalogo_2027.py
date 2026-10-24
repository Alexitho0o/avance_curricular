#!/usr/bin/env python3
"""Versiona la separacion de modalidad/codigo SIES sin regenerar los historicos."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.catalogos_sies import DATA, escribir_inmutables, json_bytes, sha256, verificar_fuente

BASE_VERSION = "5910_20260907_6047_20261013"
VERSION = BASE_VERSION + "_modalidad_v2"


def generar(*, promover=False):
    contract = json.loads((DATA / "fuentes.json").read_text(encoding="utf-8"))
    for path, digest in contract["referencias_2026"].items():
        verificar_fuente(ROOT, {"path": path, "sha256": digest})
    base = DATA / "2027" / BASE_VERSION
    output = DATA / "2027" / VERSION
    catalog = deepcopy(json.loads((base / "catalogo.json").read_text(encoding="utf-8")))
    policy = {"anio": 2027, "version": 2, "decision_fecha": "2026-10-13",
              "codigo_sies": "Solo candidato unico; no escoger version",
              "modalidad": "Unanimidad de modalidad valida entre candidatos respaldados",
              "estado_cruce_sies": "Alias compatible de estado_codigo_sies",
              "sp": "Pendiente de respaldo institucional; no inferir desde sufijo o V",
              "no_cambia": ["elegibilidad", "fuentes", "proceso_2026", "carga_PES"],
              "contrato": "docs/RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md"}
    catalog.update(version=VERSION, catalogo_anterior={"path": f"2027/{BASE_VERSION}/catalogo.json", "sha256": sha256(base / "catalogo.json")},
                   revision_modalidad=policy)
    files = {output / "catalogo.json": json_bytes(catalog), output / "POLITICA_MODALIDAD.json": json_bytes(policy)}
    for name in ("EVIDENCIA_DIMENSIONES.json", "REVISION_EQUIVALENCIAS.json"):
        files[output / name] = (base / name).read_bytes()
    registry_path = DATA / "REGISTRO.json"
    registry_raw = registry_path.read_bytes()
    registry = json.loads(registry_raw)
    entry = {"path": f"2027/{VERSION}/catalogo.json", "sha256": hashlib.sha256(files[output / "catalogo.json"]).hexdigest()}
    change = promover and registry["catalogos"]["2027"] != entry
    if change:
        expected = {"path": f"2027/{BASE_VERSION}/catalogo.json", "sha256": sha256(base / "catalogo.json")}
        if registry["catalogos"]["2027"] != expected:
            raise ValueError("Otra revision activa; no promover sin conciliar")
        files[output / "REGISTRO_ANTERIOR.json"] = registry_raw
    escribir_inmutables(files)
    if change:
        if registry_path.read_bytes() != registry_raw:
            raise ValueError("El registro cambio durante la revision")
        registry["catalogos"]["2027"] = entry
        staging = registry_path.with_suffix(".tmp")
        with staging.open("xb") as stream:
            stream.write(json_bytes(registry))
        staging.replace(registry_path)
    return {"version": VERSION, "codigos": len(catalog["oferta"]), "promovida": promover}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--promover", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generar(promover=args.promover)))
