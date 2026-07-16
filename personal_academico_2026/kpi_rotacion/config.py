"""Configuracion y resolucion de fuentes oficiales para KPI de rotacion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal


TipoArchivo = Literal["en_institucion", "fuera_institucion"]


@dataclass(frozen=True)
class OfficialSources:
    """Rutas de documentos oficiales usados como fuente unica de verdad."""

    instructivo: Path
    estructura_en_institucion: Path
    estructura_fuera_institucion: Path


@dataclass(frozen=True)
class RunConfig:
    """Parametros completos de una ejecucion anual de rotacion."""

    input_base: Path
    input_comparacion: Path
    anio_base: int
    anio_comparacion: int
    output_dir: Path
    tipo_archivo: TipoArchivo
    sources: OfficialSources


def module_version() -> str:
    """Entrega la version semantica local del modulo de rotacion."""

    return "0.1.0"


def project_root() -> Path:
    """Resuelve la raiz del repositorio desde la ubicacion de este modulo."""

    return Path(__file__).resolve().parents[2]


def personal_project_root() -> Path:
    """Resuelve la raiz del subproyecto de Personal Academico 2026."""

    return project_root() / "personal_academico_2026"


def default_output_dir() -> Path:
    """Entrega la carpeta oficial de salida para el hito de rotacion."""

    return personal_project_root() / "outputs" / "KPI_ROTACION"


def first_existing(paths: Iterable[Path]) -> Path | None:
    """Retorna la primera ruta existente dentro de una secuencia de candidatos."""

    for path in paths:
        if path.exists():
            return path
    return None


def first_glob(root: Path, pattern: str) -> Path | None:
    """Busca el primer archivo que cumple un patron glob bajo una raiz."""

    matches = sorted(path for path in root.glob(pattern) if path.is_file())
    if not matches:
        return None
    return matches[0]


def default_instructivo_candidates() -> list[Path]:
    """Construye rutas candidatas conocidas para el instructivo oficial 2026."""

    home = Path.home()
    return [
        home
        / "Library"
        / "CloudStorage"
        / "OneDrive-InstitutoProfesionalSanSebastián"
        / "Datos DAI (RAW) - 1.1 Datos crudos"
        / "1.2.1 Datos Institucionales"
        / "1.2.1.1 SIES"
        / "Enviados"
        / "Personal Académico"
        / "2026"
        / "otros"
        / "Personal Académico SIES - Instructivo 2026.txt",
        home
        / "Library"
        / "CloudStorage"
        / "OneDrive-InstitutoProfesionalSanSebastián"
        / "Archivos de chat de Microsoft Teams"
        / "Personal Académico SIES - Instructivo 2026.txt",
    ]


def resolve_default_sources(
    instructivo: Path | None = None,
    estructura_en_institucion: Path | None = None,
    estructura_fuera_institucion: Path | None = None,
) -> OfficialSources:
    """Resuelve las tres fuentes oficiales requeridas por la especificacion."""

    root = project_root()
    resolved_en = estructura_en_institucion or first_glob(
        root, "*Estructura_Personal_Acad*en_Institucio*n_2026.csv"
    )
    resolved_fuera = estructura_fuera_institucion or first_glob(
        root, "*Estructura_Personal_Acad*Fuera_Institucio*n_2026.csv"
    )
    resolved_instructivo = instructivo or first_existing(default_instructivo_candidates())

    missing = []
    if resolved_instructivo is None:
        missing.append("Personal Academico SIES - Instructivo 2026.txt")
    if resolved_en is None:
        missing.append("20260420_Estructura_Personal_Academico_en_Institucion_2026.csv")
    if resolved_fuera is None:
        missing.append("20260420_Estructura_Personal_Academico_Fuera_Institucion_2026.csv")
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(f"No se encontraron fuentes oficiales requeridas: {joined}")

    return OfficialSources(
        instructivo=resolved_instructivo,
        estructura_en_institucion=resolved_en,
        estructura_fuera_institucion=resolved_fuera,
    )


def structure_path_for_type(sources: OfficialSources, tipo_archivo: TipoArchivo) -> Path:
    """Selecciona la estructura oficial segun el tipo de archivo academico."""

    if tipo_archivo == "en_institucion":
        return sources.estructura_en_institucion
    return sources.estructura_fuera_institucion
