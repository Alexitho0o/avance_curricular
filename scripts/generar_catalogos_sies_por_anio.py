#!/usr/bin/env python3
"""Materializa catalogos no personales 2026/2027 sin ejecutar MU ni alterar fuentes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.catalogos_sies import (DATA, MODALIDADES, componentes, escribir_inmutables,
                                   json_bytes, normalizar, sha256, verificar_fuente)


def leer(path: Path, *, delimiter: str, encoding: str) -> list[dict]:
    with path.open(encoding=encoding, newline="") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Encabezados ausentes o duplicados")
        rows = list(reader)
    if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("Fuente vacia o filas con estructura irregular")
    return rows


def convertir(row: dict, numero: int, year: int) -> dict:
    if year not in {2026, 2027}:
        raise ValueError("Ano sin esquema de fuente gobernado")
    if row["CODIGO_IES_NUM"] != "162":
        raise ValueError(f"Institucion ajena a IPSS, fila {numero}")
    if year == 2026:
        code, jornada, carrera = row["CODIGO_UNICO"], row["JORNADA"], row["CODIGO_CARRERA"]
        plan, vigencia, nombre_sede = row["TIPO_PLAN_CARRERA"], row["VIGENCIA"], row["NOMBRE_SEDE"]
    else:
        jornada, carrera = row["COD_JORNADA"], row["COD_CARRERA"]
        code = f"I{row['CODIGO_IES_NUM']}S{row['COD_SEDE']}C{carrera}J{jornada}V{row['VERSION']}"
        plan, vigencia, nombre_sede = row["COD_TIPO_PLAN_CARRERA"], row["VIGENCIA_CARRERA"], row["NOMBRE_SEDE"]
    parts = componentes(code)
    if (parts["sede"], parts["jornada"], parts["carrera"]) != (row["COD_SEDE"], jornada, carrera):
        raise ValueError(f"Campos y codigo contradictorios, fila {numero}")
    if year == 2027 and parts["version"] != row["VERSION"]:
        raise ValueError(f"Version contradictoria, fila {numero}")
    modalidad = row["MODALIDAD"]
    if modalidad not in MODALIDADES or jornada not in {"1", "2", "3", "4", "5"} or vigencia not in {"1", "2", "3"}:
        raise ValueError(f"Dominio desconocido en fila {numero}")
    for field in ("NOMBRE_CARRERA", "DURACION_ESTUDIOS", "DURACION_TOTAL"):
        if not row[field].strip():
            raise ValueError(f"Falta {field}, fila {numero}")
    return {
        "codigo_unico": code, "sede": parts["sede"], "nombre_sede": nombre_sede,
        "carrera": carrera, "jornada": jornada, "version": parts["version"],
        "modalidad_codigo": modalidad, "modalidad": MODALIDADES[modalidad],
        "plan": plan, "vigencia": vigencia, "duracion_estudios": row["DURACION_ESTUDIOS"],
        "duracion_total": row["DURACION_TOTAL"], "nombres_fuente": [row["NOMBRE_CARRERA"]],
        "filas_fuente": [numero], "equivalencias": [],
    }


def construir_oferta(rows: list[dict], year: int, source: dict) -> dict:
    catalog = {}
    for numero, row in enumerate(rows, 2):
        item = convertir(row, numero, year)
        code = item["codigo_unico"]
        if code in catalog:
            if year != 2026:
                raise ValueError(f"Codigo duplicado en oferta {year}: {code}")
            old = catalog[code]
            excluded = {"nombres_fuente", "filas_fuente", "equivalencias"}
            if any(old[k] != item[k] for k in item if k not in excluded):
                raise ValueError(f"Atributos contradictorios: {code}")
            old["nombres_fuente"] = sorted(set(old["nombres_fuente"] + item["nombres_fuente"]))
            old["filas_fuente"].append(numero)
        else:
            catalog[code] = item
        if year == 2026:
            aliases = [row["CODCARPR_CANONICO"], *row["CODCARPR_ALIAS_LIST"].split("|")]
            for alias in sorted({normalizar(a) for a in aliases} - {"", "NAN", "NONE", "NULL"}):
                catalog[code]["equivalencias"].append({
                    "codcarpr": alias, "nombre_interno": row["NOMBRE_CARRERA"],
                    "metodo": "CATALOGO_MU2026", "fila_fuente": numero,
                    "fuente": {"path": source["path"], "sha256": source["sha256"]},
                })
    return catalog


def aplicar_equivalencias(oferta: dict, document: dict, root: Path) -> None:
    if document["anio"] != 2027 or document["schema_version"] != 1:
        raise ValueError("Equivalencias de otro ano o esquema")
    seen = set()
    for entry in document["equivalencias"]:
        code = entry["codigo_unico"]
        if code not in oferta:
            raise ValueError(f"Equivalencia fuera de oferta: {code}")
        alias = normalizar(entry["codcarpr"])
        name = entry["nombre_interno"].strip()
        if not alias or not name or not entry.get("localizador", "").strip():
            raise ValueError("Equivalencia incompleta")
        key = (code, alias, normalizar(name))
        if key in seen:
            raise ValueError("Equivalencia repetida")
        seen.add(key)
        evidence = {"path": entry["evidencia_path"], "sha256": entry["evidencia_sha256"]}
        verificar_fuente(root, evidence)
        oferta[code]["equivalencias"].append({
            "codcarpr": alias, "nombre_interno": name,
            "metodo": "EQUIVALENCIA_EXPLICITA_2027", "fuente": evidence,
            "localizador": entry["localizador"],
        })


def construir(root: Path = ROOT, output: Path = DATA) -> dict:
    inputs = root / "data/catalogos_sies"
    contract = json.loads((inputs / "fuentes.json").read_text(encoding="utf-8"))
    for path, digest in contract["referencias_2026"].items():
        verificar_fuente(root, {"path": path, "sha256": digest})
    old_path = verificar_fuente(root, contract["2026"])
    new_path = verificar_fuente(root, contract["2027"])
    old = construir_oferta(leer(old_path, delimiter="\t", encoding="utf-8-sig"), 2026, contract["2026"])
    new = construir_oferta(leer(new_path, delimiter=";", encoding="latin-1"), 2027, contract["2027"])
    for code in new.keys() & old.keys():
        new[code]["equivalencias"] = [dict(a, metodo="HEREDADA_MISMO_CODIGO_UNICO_2026")
                                      for a in old[code]["equivalencias"]]
    eq_path = inputs / "equivalencias_2027.json"
    aplicar_equivalencias(new, json.loads(eq_path.read_text(encoding="utf-8")), root)
    files, registry = {}, {"schema_version": 1, "catalogos": {}}
    for year, offer in [(2026, old), (2027, new)]:
        source = contract[str(year)]
        pending = [r for r in offer.values() if not r["equivalencias"]]
        payload = {
            "schema_version": 1, "anio": year, "version": source["version"], "fuente": source,
            "sedes_internas": {"RE": "2", "CO": "3", **({"PTG": "4"} if year == 2027 else {})},
            "regla_sedes": "RE/CO: gobernanza_sede.tsv; PTG solo 2027: sede 4 Patagonia en 5910 y decision institucional 2026-10-13",
            "oferta": [offer[k] for k in sorted(offer)],
            "resumen": {"codigos": len(offer), "con_equivalencia": len(offer) - len(pending),
                        "sin_equivalencia": len(pending), "por_modalidad": dict(Counter(r["modalidad"] for r in offer.values())),
                        "por_sede": dict(Counter(r["sede"] for r in offer.values()))},
            "estado": "OFERTA_DISPONIBLE_CON_EQUIVALENCIAS_PENDIENTES" if pending else "OFERTA_Y_EQUIVALENCIAS_DISPONIBLES",
            "habilita_carga_mu": False,
        }
        if year == 2027:
            payload["fuente_equivalencias_heredadas"] = contract["2026"]
            payload["equivalencias_explicitas"] = {"path": str(eq_path.relative_to(root)), "sha256": sha256(eq_path)}
        path = Path(str(year)) / source["version"] / "catalogo.json"
        raw = json_bytes(payload)
        files[output / path] = raw
        registry["catalogos"][str(year)] = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
    pending = [{"codigo_unico": r["codigo_unico"], "nombres": r["nombres_fuente"],
                "sede": r["sede"], "jornada": r["jornada"], "modalidad": r["modalidad"],
                "version": r["version"], "estado": "PENDIENTE_EQUIVALENCIA_CODCARPR",
                "origen_brecha": "CODIGO_NUEVO_2027" if r["codigo_unico"] not in old else "SIN_EQUIVALENCIA_DESDE_2026",
                "accion": "Registrar codigo interno y nombre con evidencia; no inferir por similitud"}
               for r in new.values() if not r["equivalencias"]]
    report = {
        "anio": 2027, "codigos_2027": len(new), "codigos_comunes_2026_2027": len(new.keys() & old.keys()),
        "codigos_nuevos_2027": sorted(new.keys() - old.keys()),
        "codigos_2026_ausentes_2027_no_eliminar_historicos": sorted(old.keys() - new.keys()),
        "pendientes_equivalencia": pending, "referencias_2026_verificadas": contract["referencias_2026"],
        "pendientes_por_origen": dict(Counter(r["origen_brecha"] for r in pending)),
        "carga_mu2027_habilitada": False,
    }
    files[output / "CONCILIACION_OFERTA_2026_2027.json"] = json_bytes(report)
    files[output / "REGISTRO.json"] = json_bytes(registry)
    escribir_inmutables(files)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=DATA)
    args = parser.parse_args()
    report = construir(output=args.salida)
    print(json.dumps({"oferta_2027": report["codigos_2027"],
                      "nuevos_codigos": len(report["codigos_nuevos_2027"]),
                      "pendientes_equivalencia": len(report["pendientes_equivalencia"]),
                      "fuentes_2026_intactas": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
