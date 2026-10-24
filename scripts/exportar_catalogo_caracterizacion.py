#!/usr/bin/env python3
"""Empaqueta la revision anual y su resolutor sin fuentes personales ni rutas Mac."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common.catalogos_sies import DATA, cargar_catalogo, escribir_inmutables, json_bytes, sha256


def exportar(destino: Path, *, expected_descriptor_sha256: str | None = None) -> dict:
    catalog = cargar_catalogo(2027)
    version = catalog["version"]
    if "revision_equivalencias" not in catalog:
        raise ValueError("Publicar primero la revision corroborada con 6047")
    relative = Path("2027") / version
    directory = DATA / relative
    target = destino / "gobernanza/sies/anual"
    files, metadata = {}, {}
    sources = {"catalogo.json": directory / "catalogo.json",
                         "EVIDENCIA_DIMENSIONES.json": directory / "EVIDENCIA_DIMENSIONES.json",
                         "REVISION_EQUIVALENCIAS.json": directory / "REVISION_EQUIVALENCIAS.json",
                         "resolutor.py": ROOT / "common/catalogos_sies.py"}
    if "revision_modalidad" in catalog:
        sources["POLITICA_MODALIDAD.json"] = directory / "POLITICA_MODALIDAD.json"
    for name, source in sources.items():
        path = relative / name
        files[target / path] = source.read_bytes()
        metadata[name] = {"path": path.as_posix(), "sha256": sha256(source)}
    descriptor = {"schema_version": 1, "anio": 2027, "version": version,
                  "repositorio_origen": "avance_curricular", "archivos": metadata,
                  "uso": "Enriquecimiento de analisis interno; no elegibilidad ni carga PES"}
    pointer = target / "ACTIVO_2027.json"
    raw = json_bytes(descriptor)
    replacing = pointer.exists() and pointer.read_bytes() != raw
    if replacing:
        if not expected_descriptor_sha256 or sha256(pointer) != expected_descriptor_sha256:
            raise ValueError("La actualizacion requiere el SHA-256 del descriptor anterior")
        old = json.loads(pointer.read_text(encoding="utf-8"))
        if old["anio"] != 2027 or old["version"] == version:
            raise ValueError("No reemplazar un paquete de otro ano ni mutar la misma version")
        files[target / relative / "ACTIVO_ANTERIOR.json"] = pointer.read_bytes()
    else:
        files[pointer] = raw
    escribir_inmutables(files)
    if replacing:
        if sha256(pointer) != expected_descriptor_sha256:
            raise ValueError("El descriptor cambio durante la exportacion")
        staging = pointer.with_suffix(".tmp")
        with staging.open("xb") as stream:
            stream.write(raw)
        staging.replace(pointer)
    return descriptor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", type=Path, required=True)
    parser.add_argument("--reemplazar-descriptor-sha256")
    args = parser.parse_args()
    print(json.dumps(exportar(args.destino, expected_descriptor_sha256=args.reemplazar_descriptor_sha256), ensure_ascii=False))
