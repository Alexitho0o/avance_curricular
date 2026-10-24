"""Consulta de oferta SIES versionada. No importa ni ejecuta el motor MU2026."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "catalogos_sies"
MODALIDADES = {"1": "Presencial", "2": "Semipresencial", "3": "No presencial"}
CODE_RE = re.compile(r"I(?P<ies>\d+)S(?P<sede>\d+)C(?P<carrera>\d+)J(?P<jornada>\d+)V(?P<version>\d+)")


def normalizar(value: object) -> str:
    value = "" if value is None else str(value)
    value = unicodedata.normalize("NFKD", value.strip().upper())
    return " ".join("".join(c for c in value if not unicodedata.combining(c)).split())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def componentes(code: str) -> dict[str, str]:
    match = CODE_RE.fullmatch(code)
    if not match or match["ies"] != "162":
        raise ValueError(f"Codigo unico IPSS invalido: {code!r}")
    return match.groupdict()


def verificar_fuente(root: Path, metadata: dict) -> Path:
    path = (root / metadata["path"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Fuente fuera del repositorio")
    if sha256(path) != metadata["sha256"]:
        raise ValueError(f"Cambio la fuente gobernada: {metadata['path']}")
    return path


def escribir_inmutables(files: dict[Path, bytes]) -> None:
    # Preflight de todos los destinos antes de escribir cualquiera de ellos.
    for path, content in files.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"No sobrescribir snapshot diferente: {path}")
    for path, content in files.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(content)


def cargar_catalogo(anio: int, directory: Path = DATA) -> dict:
    registry = json.loads((directory / "REGISTRO.json").read_text(encoding="utf-8"))
    try:
        metadata = registry["catalogos"][str(anio)]
    except KeyError as exc:
        raise ValueError(f"No existe catalogo gobernado para {anio}; no usar otro ano") from exc
    path = verificar_fuente(directory, metadata)
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog["anio"] != anio:
        raise ValueError("Ano del catalogo distinto del solicitado")
    if len({r["codigo_unico"] for r in catalog["oferta"]}) != len(catalog["oferta"]):
        raise ValueError("Codigos duplicados en catalogo")
    return catalog


def resolver_catalogo(catalog: dict, *, codigo_unico: str = "", codcarpr: str = "",
                      sede: str = "", jornada: str = "", version: str = "",
                      nombre: str = "") -> dict:
    """Resuelve solo coincidencias unicas; nunca elige version mayor o primera fila."""
    code, codcarpr = normalizar(codigo_unico), normalizar(codcarpr)
    if bool(code) == bool(codcarpr):
        raise ValueError("Indicar codigo_unico o codcarpr, no ambos")
    sede, jornada, version, nombre = map(normalizar, (sede, jornada, version, nombre))
    sedes = catalog["sedes_internas"]
    sede = sedes.get(sede, sede)
    jornada = {"D": "1", "V": "2", "O": "4"}.get(jornada, jornada)
    if not code and (not sede or not jornada):
        raise ValueError("El cruce interno exige sede y jornada")
    if code:
        componentes(code)
    constraints = []
    if codcarpr and catalog["anio"] == 2027:
        constraints = [b for b in catalog.get("ambiguedades_cruce", [])
                       if b["codcarpr"] == codcarpr and b["sede"] == sede
                       and b["jornada"] == jornada
                       and (not nombre or normalizar(b["nombre_interno"]) == nombre)]
    constrained_codes = {c for b in constraints for c in b["candidatos"]}
    candidates = []
    for row in catalog["oferta"]:
        if code and row["codigo_unico"] != code:
            continue
        if any(v and row[k] != v for k, v in [("sede", sede), ("jornada", jornada), ("version", version)]):
            continue
        if constrained_codes and row["codigo_unico"] not in constrained_codes:
            continue
        if codcarpr and not constrained_codes and not any(a["codcarpr"] == codcarpr and
                               (not nombre or normalizar(a["nombre_interno"]) == nombre)
                               for a in row["equivalencias"]):
            continue
        candidates.append(row)
    result = {
        "anio": catalog["anio"], "version_catalogo": catalog["version"],
        "estado": "RESUELTO" if len(candidates) == 1 else "AMBIGUO" if candidates else "SIN_EQUIVALENCIA",
        "codigo_unico": "", "modalidad": "No determinada", "modalidad_codigo": "",
        "candidatos": sorted(r["codigo_unico"] for r in candidates),
        "fuente": catalog["fuente"],
    }
    if constraints:
        result["evidencia_ambiguedad"] = constraints
    if len(candidates) == 1:
        row = candidates[0]
        result.update(codigo_unico=row["codigo_unico"], modalidad=row["modalidad"],
                      modalidad_codigo=row["modalidad_codigo"], filas_fuente=row["filas_fuente"],
                      metodo="OFERTA_ANUAL_CODIGO_UNICO" if code else "CRUCE_ANUAL_CODCARPR_SEDE_JORNADA",
                      equivalencias=row["equivalencias"],
                      vigencia_oferta=row["vigencia"])
        if codcarpr:
            result["equivalencias_utilizadas"] = [a for a in row["equivalencias"] if a["codcarpr"] == codcarpr
                                                  and (not nombre or normalizar(a["nombre_interno"]) == nombre)]
    return result


def resolver(anio: int, *, directory: Path = DATA, **kwargs) -> dict:
    return resolver_catalogo(cargar_catalogo(anio, directory), **kwargs)
