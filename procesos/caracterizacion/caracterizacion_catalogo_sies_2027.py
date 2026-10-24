"""Enriquecimiento SIES 2027 portable, sin tocar elegibilidad ni originales."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd
from ubicacion_proyecto import recurso_comun

ROOT = Path(__file__).resolve().parent
DIRECTORY = recurso_comun('sies_anual_2027')
OUTPUT_COLUMNS = ("CODIGO_UNICO_SIES", "MODALIDAD_CARRERA", "ESTADO_CRUCE_SIES",
                  "CANDIDATOS_SIES", "FUENTE_MODALIDAD", "VERSION_CATALOGO_SIES",
                  "ESTADO_CODIGO_SIES", "ESTADO_MODALIDAD")


def load_package(directory=DIRECTORY):
    directory = Path(directory).resolve()
    descriptor = json.loads((directory / "ACTIVO_2027.json").read_text(encoding="utf-8"))
    if descriptor["anio"] != 2027 or descriptor["schema_version"] != 1:
        raise ValueError("Paquete SIES de otro ano o esquema")
    paths = {}
    for name, meta in descriptor["archivos"].items():
        path = (directory / meta["path"]).resolve()
        if not path.is_relative_to(directory) or hashlib.sha256(path.read_bytes()).hexdigest() != meta["sha256"]:
            raise ValueError(f"Cambio el paquete SIES gobernado: {name}")
        paths[name] = path
    required = {"catalogo.json", "resolutor.py", "EVIDENCIA_DIMENSIONES.json", "REVISION_EQUIVALENCIAS.json", "POLITICA_MODALIDAD.json"}
    if not required.issubset(paths):
        raise ValueError("Paquete SIES incompleto")
    catalog = json.loads(paths["catalogo.json"].read_text(encoding="utf-8"))
    if catalog["anio"] != 2027 or catalog["version"] != descriptor["version"]:
        raise ValueError("Catalogo y descriptor SIES no concuerdan")
    if catalog.get("revision_modalidad") != json.loads(paths["POLITICA_MODALIDAD.json"].read_text(encoding="utf-8")):
        raise ValueError("La politica de modalidad no coincide con el catalogo")
    if len({r["codigo_unico"] for r in catalog["oferta"]}) != len(catalog["oferta"]):
        raise ValueError("Codigos SIES duplicados")
    spec = importlib.util.spec_from_file_location("sies_runtime_gobernado", paths["resolutor.py"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return catalog, descriptor, module.resolver_catalogo


def enrich_frame(frame, *, anio, periodo, directory=DIRECTORY):
    if int(anio) != 2027 or int(periodo) not in (1, 2, 3):
        raise ValueError("El enriquecimiento SIES es exclusivo del analisis 2027")
    if set(OUTPUT_COLUMNS) & set(frame.columns):
        raise ValueError("La entrada ya contiene columnas SIES; no sobrescribirlas silenciosamente")
    for field, expected in (("ANOMATRICULA", int(anio)), ("PERIODOMATRICULA", int(periodo))):
        if field in frame and not pd.to_numeric(frame[field], errors="coerce").eq(expected).all():
            raise ValueError(f"La entrada mezcla anos/periodos en {field}; no enriquecer historicos")
    catalog, descriptor, resolve = load_package(directory)
    output = frame.copy(deep=True)
    values = []
    for _, row in frame.iterrows():
        def text(key):
            value = row.get(key, "")
            return "" if pd.isna(value) else str(value).strip()
        args = {"codcarpr": text("CODCARPR"), "sede": text("SEDE"), "jornada": text("JORNADA")}
        if not all(args.values()):
            result = {"estado": "DATOS_INSUFICIENTES", "codigo_unico": "", "modalidad": "No determinada", "candidatos": [],
                      "estado_codigo_sies": "DATOS_INSUFICIENTES", "estado_modalidad": "DATOS_INSUFICIENTES"}
        else:
            result = resolve(catalog, **args)
            if result["estado"] == "AMBIGUO" and text("NOMBRE_L"):
                narrow = resolve(catalog, **args, nombre=text("NOMBRE_L"))
                if narrow["estado"] != "SIN_EQUIVALENCIA":
                    result = narrow
        values.append([result["codigo_unico"], result["modalidad"], result["estado"],
                       ";".join(result["candidatos"]), descriptor["archivos"]["catalogo.json"]["path"], catalog["version"],
                       result["estado_codigo_sies"], result["estado_modalidad"]])
    for i, name in enumerate(OUTPUT_COLUMNS):
        output[name] = [v[i] for v in values]
    states = dict(Counter(v[2] for v in values))
    modality_states = dict(Counter(v[7] for v in values))
    summary = {"anio": int(anio), "periodo": int(periodo), "registros": len(frame),
               "estados": states, "estados_codigo_sies": states, "estados_modalidad": modality_states,
               "modalidades": dict(Counter(v[1] for v in values)),
               "version": catalog["version"], "paquete": descriptor,
               "conciliacion_registros": sum(states.values()) == sum(modality_states.values()) == len(frame),
               "cambia_elegibilidad": False, "datos_personales_incluidos": False}
    return output, summary
