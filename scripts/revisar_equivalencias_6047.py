#!/usr/bin/env python3
"""Revisa oferta/codigos internos con evidencia exacta, sin ejecutar Matricula."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.catalogos_sies import (escribir_inmutables, json_bytes, normalizar,
                                   sha256, verificar_fuente)
from scripts.generar_catalogos_sies_por_anio import construir_oferta, leer

DATA = ROOT / "data/catalogos_sies"
VERSION = "5910_20260907_6047_20261013"
REVISION = DATA / "2027" / VERSION
DA_FIELDS = ["CODCARPR", "CODIGOCARRERA", "NOMBRE_L", "SEDE", "JORNADA", "ANOMATRICULA"]


def dimensiones(path: Path) -> tuple[list[dict], dict]:
    frame = pd.read_excel(path, sheet_name="Hoja1", usecols=DA_FIELDS, dtype=str, keep_default_na=False)
    groups = defaultdict(Counter)
    for row in frame.to_dict("records"):
        key = tuple(normalizar(row[k]) for k in ("CODCARPR", "NOMBRE_L", "SEDE", "JORNADA"))
        groups[key][normalizar(row["ANOMATRICULA"])] += 1
    result = []
    for i, (key, years) in enumerate(sorted(groups.items()), 1):
        alias, name, sede, jornada = key
        result.append({"dimension_id": i, "codcarpr": alias, "nombre_interno": name,
                       "sede_interna": sede, "jornada_interna": jornada,
                       "sede": {"RE": "2", "CO": "3", "PTG": "4"}.get(sede, ""),
                       "jornada": {"D": "1", "V": "2", "O": "4"}.get(jornada, ""),
                       "registros_por_ano_matricula": dict(sorted(years.items()))})
    return result, {"registros_fuente": len(frame), "dimensiones": len(result),
                    "codigocarrera_igual_codcarpr": int(frame.CODIGOCARRERA.eq(frame.CODCARPR).sum())}


def cruzar(base: dict, report: dict, dims: list[dict], evidence: dict) -> tuple[dict, dict]:
    updated = deepcopy(base)
    offer = {r["codigo_unico"]: r for r in updated["oferta"]}
    if updated["anio"] != 2027 or len(offer) != len(updated["oferta"]):
        raise ValueError("Revision solo 2027, sin codigos duplicados")
    attributes = ("sede", "carrera", "jornada", "version", "modalidad_codigo", "plan", "vigencia",
                  "duracion_estudios", "duracion_total", "nombres_fuente")
    for code, row in offer.items():
        if code not in report or any(row[k] != report[code][k] for k in attributes):
            raise ValueError(f"6047 no corrobora el catalogo base: {code}")
    extra = sorted(report.keys() - offer.keys())
    if any(not all(normalizar(n).startswith("DIPLOMADO ") for n in report[c]["nombres_fuente"]) for c in extra):
        raise ValueError("Hay programas adicionales no diplomados; revisar el alcance antes de publicar")
    by_key = defaultdict(list)
    for code, row in offer.items():
        for name in row["nombres_fuente"]:
            by_key[(normalizar(name), row["sede"], row["jornada"])].append(code)
    added, ambiguous = [], []
    initial_pending = {code for code, row in offer.items() if not row["equivalencias"]}
    for dimension in dims:
        alias, name, sede, jornada = (dimension[k] for k in ("codcarpr", "nombre_interno", "sede", "jornada"))
        if not all((alias, name, sede, jornada)):
            continue
        candidates = sorted(set(by_key.get((name, sede, jornada), [])))
        trace = {"fuente": evidence, "localizador": f"dimensiones[{dimension['dimension_id']}]"}
        if len(candidates) > 1:
            ambiguous.append({"codcarpr": alias, "nombre_interno": name, "sede": sede,
                              "jornada": jornada, "candidatos": candidates, **trace})
        elif len(candidates) == 1:
            code = candidates[0]
            old = offer[code]["equivalencias"]
            if any(a["codcarpr"] == alias and normalizar(a["nombre_interno"]) == name for a in old):
                continue
            entry = {"codcarpr": alias, "nombre_interno": name, **trace,
                     "metodo": "NOMBRE_SEDE_JORNADA_EXACTOS_CANDIDATO_UNICO_6047_DA",
                     "filas_reporte_6047": report[code]["filas_fuente"]}
            old.append(entry)
            added.append({"codigo_unico": code, **entry})
    updated["ambiguedades_cruce"] = ambiguous
    pending = []
    for code in sorted(initial_pending):
        row = offer[code]
        blocks = [b for b in ambiguous if code in b["candidatos"]]
        pending.append({"codigo_unico": code, "nombres": row["nombres_fuente"],
                        "sede": row["sede"], "jornada": row["jornada"], "version": row["version"],
                        "codcarpr_respaldados": sorted({a["codcarpr"] for a in row["equivalencias"]}),
                        "estado": "COMPLETADA" if row["equivalencias"] else
                                  "PENDIENTE_VERSION_AMBIGUA" if blocks else "PENDIENTE_SIN_CRUCE_EXACTO"})
    with_alias = sum(bool(r["equivalencias"]) for r in offer.values())
    updated["resumen"].update(con_equivalencia=with_alias, sin_equivalencia=len(offer) - with_alias)
    updated["resumen"]["dimensiones_con_ambiguedad"] = len(ambiguous)
    return updated, {"codigos_oferta": len(offer), "codigos_reporte_6047": len(report),
                     "diplomados_fuera_de_alcance": extra, "equivalencias_agregadas": added,
                     "revision_52_originales": pending, "ambiguedades": ambiguous,
                     "resumen_revision": dict(Counter(r["estado"] for r in pending))}


def generar(reporte: Path, alumnos: Path, *, output: Path = REVISION) -> dict:
    contract = json.loads((DATA / "fuentes.json").read_text(encoding="utf-8"))
    for path, digest in contract["referencias_2026"].items():
        verificar_fuente(ROOT, {"path": path, "sha256": digest})
    base_path = DATA / "2027/5910_20260907/catalogo.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    hashes = {"reporte_6047": sha256(reporte), "datosalumnos": sha256(alumnos)}
    report_source = {"archivo": reporte.name, "sha256": hashes["reporte_6047"]}
    rows = leer(reporte, delimiter=";", encoding="latin-1")
    report = construir_oferta(rows, 2027, {"path": reporte.name, **report_source})
    dims, counts = dimensiones(alumnos)
    evidence_payload = {"fuentes": {"reporte_6047": report_source,
                                   "datosalumnos": {"archivo": alumnos.name, "sha256": hashes["datosalumnos"], "hoja": "Hoja1"}},
                        "columnas_leidas_datosalumnos": DA_FIELDS, "conteos": counts,
                        "dimensiones": dims, "oferta_6047_reducida": list(report.values()),
                        "datos_personales_incluidos": False}
    evidence_raw = json_bytes(evidence_payload)
    evidence = {"path": f"2027/{VERSION}/EVIDENCIA_DIMENSIONES.json",
                "sha256": hashlib.sha256(evidence_raw).hexdigest()}
    catalog, audit = cruzar(base, report, dims, evidence)
    catalog["version"] = VERSION
    catalog["revision_equivalencias"] = evidence
    catalog["catalogo_base"] = {"path": "2027/5910_20260907/catalogo.json", "sha256": sha256(base_path)}
    audit.update(anio=2027, version=VERSION, evidencia=evidence, referencias_2026_verificadas=contract["referencias_2026"])
    catalog_raw = json_bytes(catalog)
    if sha256(reporte) != hashes["reporte_6047"] or sha256(alumnos) != hashes["datosalumnos"]:
        raise ValueError("Las fuentes cambiaron durante el cruce")
    escribir_inmutables({output / "EVIDENCIA_DIMENSIONES.json": evidence_raw,
                        output / "catalogo.json": catalog_raw,
                        output / "REVISION_EQUIVALENCIAS.json": json_bytes(audit)})
    return audit


def promover(output: Path = REVISION) -> None:
    registry_path = DATA / "REGISTRO.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    catalog_path = output / "catalogo.json"
    metadata = {"path": str(catalog_path.relative_to(DATA)), "sha256": sha256(catalog_path)}
    if registry["catalogos"]["2027"] == metadata:
        return
    if registry["catalogos"]["2027"]["path"] != "2027/5910_20260907/catalogo.json":
        raise ValueError("Hay otra revision activa; no sustituir sin conciliar")
    escribir_inmutables({output / "REGISTRO_ANTERIOR.json": registry_path.read_bytes()})
    registry["catalogos"]["2027"] = metadata
    staging = registry_path.with_suffix(".tmp")
    with staging.open("xb") as stream:
        stream.write(json_bytes(registry))
    staging.replace(registry_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reporte", type=Path, required=True)
    parser.add_argument("--alumnos", type=Path, required=True)
    parser.add_argument("--promover", action="store_true")
    args = parser.parse_args()
    audit = generar(args.reporte, args.alumnos)
    if args.promover:
        promover()
    print(json.dumps(audit["resumen_revision"]))


if __name__ == "__main__":
    main()
