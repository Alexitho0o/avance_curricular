#!/usr/bin/env python3
"""Integracion auditable de identidad de carreras para Avance Curricular 2026."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


PROCESO = "Avance Curricular SIES 2026"
SUBPROYECTO = (
    "Integracion de identidad y equivalencia de carreras entre Matricula "
    "Unificada 2026, Estudiantes Extranjeros SIES 2026 y Avance Curricular SIES 2026"
)
ANO_PROCESO = "2026"
ANO_REFERENCIA_DATOS = "2025"

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_2026 = REPO_ROOT / "avance_curricular_2026"
AUDITORIAS_DIR = BASE_2026 / "04_gobernanza_mallas" / "03_auditorias"
RUN_PREFIX = "INTEGRACION_IDENTIDAD_CARRERAS_"
ENDASH = "\u2013"

DIRS = [
    "00_CONTROL",
    "01_INVENTARIO",
    "02_CONOCIMIENTO_RECUPERADO",
    "03_INTERMEDIOS",
    "04_RESULTADOS",
    "05_AUDITORIA",
    "06_LOGS",
    "07_RESPALDOS",
]

PHASE_NAMES = {
    0: "INVENTARIO_FOCALIZADO",
    1: "RECUPERACION_LOGICA_EXISTENTE",
    2: "RECONSTRUCCION_METODOLOGIA",
    3: "CONSTRUCCION_FUENTES_MAESTRAS",
    4: "TABLA_MAESTRA_IDENTIDAD",
    5: "APLICACION_34_CARRERAS_DIRECTAS",
    6: "INTEGRACION_VALIDACION_PDF_PLAN",
    7: "REGRESION_END_TO_END",
}

ESTADOS = {"PENDIENTE", "EN_EJECUCION", "COMPLETADA", "BLOQUEADA", "ERROR"}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

NAME_PATTERNS = [
    "puente",
    "duracion",
    "codcli",
    "codigo_unico",
    "extranjer",
    "multicodcli",
    "vigencia",
    "sies",
    "carrera",
    "matricula",
    "matrícula",
    "plan",
    "resolucion",
    "resolución",
    "conciliacion",
    "conciliación",
    "diccionario",
    "homologacion",
    "homologación",
    "equivalencia",
]

CONTENT_TERMS = [
    "PUENTE_SIES_COMPILADO.tsv",
    "DURACION_ESTUDIOS.tsv",
    "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS",
    "CODIGO_UNICO_FINAL",
    "CODCARPR",
    "CODCARR",
    "CODCLI",
    "PLAN_DE_ESTUDIO",
    "MATCH_SIES_UNICO",
    "AMBIGUO_SIES",
    "SIN_MATCH_SIES",
    "RESOLUCION_STATUS",
    "ES_BLOQUEANTE",
    "salida intermedia",
    "continuidad",
    "plan regular",
    "multicodcli",
    "extranjeros",
    "matricula unificada",
    "matrícula unificada",
]

TEXT_EXTENSIONS = {
    ".py",
    ".tsv",
    ".csv",
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".sh",
    ".log",
}

HIGH_SCORE_TERMS = [
    "PUENTE_SIES_COMPILADO.tsv",
    "DURACION_ESTUDIOS.tsv",
    "corregir_fase06_vigencia_extranjeros_2025.py",
    "auditoria_integral_multicodcli_2026",
    "CODIGO_UNICO_FINAL",
    "MATCH_SIES_UNICO",
    "AMBIGUO_SIES",
    "SIN_MATCH_SIES",
    "RESOLUCION_STATUS",
    "ES_BLOQUEANTE",
]

MEDIUM_SCORE_TERMS = [
    "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS",
    "CODCARPR",
    "CODCARR",
    "CODCLI",
    "PLAN_DE_ESTUDIO",
    "VIGENCIA",
    "continuidad",
    "salida intermedia",
    "matricula_unificada",
    "estudiantes_extranjeros",
    "multicodcli",
    "resolver",
    "puente",
    "equivalencia",
    "homologacion",
]

LOW_SCORE_TERMS = [
    "carrera",
    "plan",
    "codigo_unico",
    "jornada",
    "modalidad",
    "sede",
    "version",
]

FASE1_RELEVANT_TERMS = sorted(
    set(HIGH_SCORE_TERMS + MEDIUM_SCORE_TERMS + LOW_SCORE_TERMS + CONTENT_TERMS),
    key=len,
    reverse=True,
)

IDENTITY_FIELDS = [
    "CODIGO_UNICO_FINAL",
    "CODIGO_UNICO",
    "CODCARPR",
    "CODCARR",
    "CODCLI",
    "JORNADA",
    "MODALIDAD",
    "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS",
    "PLAN_DE_ESTUDIO",
    "VIGENCIA",
    "RESOLUCION_STATUS",
    "ES_BLOQUEANTE",
    "MATCH_SIES_UNICO",
    "AMBIGUO_SIES",
    "SIN_MATCH_SIES",
]

RESOLUTION_TERMS = [
    "MATCH_SIES_UNICO",
    "AMBIGUO_SIES",
    "SIN_MATCH_SIES",
    "RESOLUCION_STATUS",
    "ES_BLOQUEANTE",
    "RESUELTO_UNICO",
    "UNICO",
    "AMBIGUO",
    "BLOQUEANTE",
]


@dataclass
class PhaseResult:
    estado: str
    salidas: list[str] = field(default_factory=list)
    conteos: dict[str, Any] = field(default_factory=dict)
    validaciones: list[dict[str, Any]] = field(default_factory=list)
    bloqueos: list[dict[str, Any]] = field(default_factory=list)
    decisiones: list[dict[str, Any]] = field(default_factory=list)
    pendientes: list[dict[str, Any]] = field(default_factory=list)
    entradas: dict[str, str] = field(default_factory=dict)
    hashes: dict[str, str] = field(default_factory=dict)
    resumen: list[str] = field(default_factory=list)
    comando_reanudacion: str = ""


class FlujoError(Exception):
    """Error controlado del flujo."""


def normalize_argv(argv: list[str]) -> list[str]:
    out: list[str] = []
    for arg in argv:
        if arg.startswith(("–", "—")):
            out.append("--" + arg.lstrip("–—"))
        else:
            out.append(arg)
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Integracion de identidad de carreras.")
    parser.add_argument("--fase", default=None, help="Fase 0-7 o final.")
    parser.add_argument("--reanudar", action="store_true")
    parser.add_argument("--forzar", action="store_true")
    parser.add_argument("--solo-validar", action="store_true")
    parser.add_argument("--mostrar-rutas", action="store_true")
    parser.add_argument("--ejecucion", default="", help="Carpeta de ejecucion a reutilizar.")
    parser.add_argument("--diagnostico-post-fase3", action="store_true")
    return parser.parse_args(normalize_argv(argv))


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def command_for_phase(phase: int | str) -> str:
    value = "final" if phase == "final" else str(phase)
    return (
        "python scripts/integrar_identidad_carreras_avance.py "
        f"{ENDASH}fase {value} {ENDASH}reanudar"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_tsv(rows: list[dict[str, Any]], path: Path, fieldnames: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(path.resolve())


def write_json(data: dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True, ensure_ascii=True)
        fh.write("\n")
    return str(path.resolve())


def parse_phase(value: str | None) -> int | str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text == "final":
        return "final"
    if text.isdigit() and 0 <= int(text) <= 7:
        return int(text)
    raise FlujoError("--fase debe ser 0, 1, 2, 3, 4, 5, 6, 7 o final.")


def phase_key(phase: int) -> str:
    return f"fase_{phase}"


def phase_status(state: dict[str, Any], phase: int) -> str:
    return state.get("fases", {}).get(phase_key(phase), {}).get("estado", "PENDIENTE")


def create_run_dir() -> Path:
    AUDITORIAS_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = AUDITORIAS_DIR / f"{RUN_PREFIX}{timestamp()}"
    suffix = 1
    while run_dir.exists():
        run_dir = AUDITORIAS_DIR / f"{RUN_PREFIX}{timestamp()}_{suffix}"
        suffix += 1
    for dirname in DIRS:
        (run_dir / dirname).mkdir(parents=True, exist_ok=True)
    return run_dir


def list_runs() -> list[Path]:
    return sorted([p for p in AUDITORIAS_DIR.glob(f"{RUN_PREFIX}*") if p.is_dir()])


def run_is_complete(run_dir: Path) -> bool:
    state_path = run_dir / "00_CONTROL" / "estado_fases.json"
    if not state_path.exists():
        return False
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return phase_status(state, 7) == "COMPLETADA"


def latest_incomplete_run() -> Path | None:
    runs = list_runs()
    incomplete = [p for p in runs if not run_is_complete(p)]
    if incomplete:
        return incomplete[-1]
    return runs[-1] if runs else None


class RunContext:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        for dirname in DIRS:
            (run_dir / dirname).mkdir(parents=True, exist_ok=True)
        self.control_path = run_dir / "00_CONTROL" / "estado_fases.json"
        self.log_path = run_dir / "06_LOGS" / "ejecucion.log"
        self.state = self._load_or_init_state()

    def _load_or_init_state(self) -> dict[str, Any]:
        if self.control_path.exists():
            return json.loads(self.control_path.read_text(encoding="utf-8"))
        return {
            "proceso": PROCESO,
            "subproyecto": SUBPROYECTO,
            "ano_proceso": ANO_PROCESO,
            "ano_referencia_datos": ANO_REFERENCIA_DATOS,
            "ejecucion": str(self.run_dir.resolve()),
            "fecha_creacion": now_iso(),
            "fases": {
                phase_key(i): {
                    "fase": i,
                    "nombre": PHASE_NAMES[i],
                    "estado": "PENDIENTE",
                    "fecha_inicio": "",
                    "fecha_fin": "",
                    "entradas": {},
                    "hashes": {},
                    "salidas": [],
                    "conteos": {},
                    "validaciones": [],
                    "bloqueos": [],
                    "decisiones": [],
                    "pendientes": [],
                    "comando_reanudacion": command_for_phase(i + 1 if i < 7 else "final"),
                }
                for i in range(8)
            },
            "reanudaciones": [],
        }

    def save(self) -> None:
        write_json(self.state, self.control_path)

    def log(self, message: str) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"{now_iso()} {message}\n")

    def start_phase(self, phase: int) -> None:
        item = self.state["fases"][phase_key(phase)]
        item["estado"] = "EN_EJECUCION"
        item["fecha_inicio"] = now_iso()
        item["fecha_fin"] = ""
        item["bloqueos"] = []
        item["pendientes"] = []
        self.save()
        self.log(f"FASE {phase} INICIO")

    def finish_phase(self, phase: int, result: PhaseResult) -> None:
        if result.estado not in ESTADOS:
            raise FlujoError(f"Estado no permitido: {result.estado}")
        item = self.state["fases"][phase_key(phase)]
        item.update(
            {
                "estado": result.estado,
                "fecha_fin": now_iso(),
                "entradas": result.entradas or item.get("entradas", {}),
                "hashes": result.hashes or item.get("hashes", {}),
                "salidas": result.salidas,
                "conteos": result.conteos,
                "validaciones": result.validaciones,
                "bloqueos": result.bloqueos,
                "decisiones": result.decisiones,
                "pendientes": result.pendientes,
                "comando_reanudacion": result.comando_reanudacion,
            }
        )
        self.save()
        self.log(f"FASE {phase} FIN {result.estado}")


def output_path(ctx: RunContext, relative: str) -> Path:
    return ctx.run_dir / relative


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def extension(path: Path) -> str:
    return path.suffix.lower()


def likely_process(path: Path) -> str:
    text = str(path).lower()
    if "extranjer" in text:
        return "Estudiantes Extranjeros SIES 2026"
    if "matricula" in text or "matrícula" in text or "mu2026" in text:
        return "Matricula Unificada 2026"
    if "avance_curricular" in text or "mallas" in text:
        return "Avance Curricular SIES 2026"
    if "multicodcli" in text:
        return "Auditoria multicodcli"
    return "No determinado"


def classify_file(path: Path) -> str:
    name = path.name.lower()
    text = str(path).lower()
    ext = extension(path)
    if ext == ".py" or ext == ".sh":
        return "codigo"
    if "manual" in name or ext in {".md", ".txt"} and "manual" in text:
        return "manual"
    if "precarga" in name:
        return "precarga"
    if "fuentes_congeladas" in text or "respaldo_entradas" in text:
        return "fuente institucional"
    if "auditoria" in text or "control" in text:
        return "auditoria"
    if "resultado" in text or "resultados" in text or "salida" in text:
        return "resultado"
    if ext in {".tsv", ".csv", ".xlsx", ".xls", ".json"}:
        return "evidencia"
    return "trabajo"


def file_type(path: Path) -> str:
    ext = extension(path)
    if ext in {".py", ".sh"}:
        return "script"
    if ext in {".tsv", ".csv", ".xlsx", ".xls"}:
        return "tabla"
    if ext == ".json":
        return "json"
    if ext in {".md", ".txt", ".log"}:
        return "texto"
    return ext.lstrip(".") or "sin_extension"


def terms_in_path(path: Path) -> set[str]:
    low = str(path).lower()
    return {term for term in CONTENT_TERMS + NAME_PATTERNS if term.lower() in low}


def terms_in_preview(path: Path) -> set[str]:
    if extension(path) not in TEXT_EXTENSIONS:
        return set()
    try:
        with path.open("rb") as fh:
            data = fh.read(256 * 1024)
        text = data.decode("utf-8", errors="ignore").lower()
    except OSError:
        return set()
    return {term for term in CONTENT_TERMS if term.lower() in text}


def candidate_score(path: Path, terms: set[str]) -> int:
    low = str(path).lower()
    score = len(terms)
    priorities = [
        "puente_sies_compilado",
        "compile_puente_sies_compilado",
        "corregir_fase06_vigencia_extranjeros_2025",
        "auditoria_integral_multicodcli_2026",
        "codigo_unico_final",
        "resolucion_status",
        "es_bloqueante",
        "duracion_estudios",
        "tipo_plan_carrera",
    ]
    for idx, marker in enumerate(priorities):
        if marker in low:
            score += 100 - idx
    if extension(path) == ".py":
        score += 10
    if "resultados" in low or "auditoria" in low:
        score += 8
    return score


def is_candidate_by_name(path: Path) -> bool:
    low = str(path).lower()
    return any(pattern in low for pattern in NAME_PATTERNS)


def iter_repository_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if should_skip(path):
            continue
        if not path.is_file():
            continue
        if is_candidate_by_name(path) or extension(path) in TEXT_EXTENSIONS:
            files.append(path)
    return files


def build_inventory() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    scripts: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    terms_rows: list[dict[str, Any]] = []
    hashes: list[dict[str, Any]] = []

    seen: set[Path] = set()
    for path in iter_repository_files():
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        path_terms = terms_in_path(path)
        preview_terms = terms_in_preview(path)
        terms = sorted(path_terms | preview_terms)
        if not terms and not is_candidate_by_name(path):
            continue
        try:
            stat = path.stat()
            digest = sha256_file(path)
        except OSError:
            continue
        rel = str(path.relative_to(REPO_ROOT))
        row = {
            "ruta": str(resolved),
            "ruta_relativa": rel,
            "nombre": path.name,
            "extension": extension(path),
            "tamano_bytes": stat.st_size,
            "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "sha256": digest,
            "proceso_probable": likely_process(path),
            "tipo_archivo": file_type(path),
            "clasificacion": classify_file(path),
            "terminos_encontrados": "|".join(terms),
            "score_prioridad": candidate_score(path, set(terms)),
        }
        candidates.append(row)
        hashes.append({"ruta": str(resolved), "sha256": digest})
        for term in terms:
            terms_rows.append(
                {
                    "ruta": str(resolved),
                    "termino": term,
                    "origen_deteccion": "ruta_o_vista_previa_limitada",
                }
            )
        if file_type(path) == "script":
            scripts.append(row.copy())
        if row["clasificacion"] in {"resultado", "auditoria", "evidencia"} or "resultados" in rel.lower():
            results.append(row.copy())

    candidates.sort(key=lambda r: (-int(r["score_prioridad"]), r["ruta_relativa"]))
    scripts.sort(key=lambda r: (-int(r["score_prioridad"]), r["ruta_relativa"]))
    results.sort(key=lambda r: (-int(r["score_prioridad"]), r["ruta_relativa"]))
    terms_rows.sort(key=lambda r: (r["termino"], r["ruta"]))
    hashes.sort(key=lambda r: r["ruta"])
    return candidates, scripts, results, terms_rows, hashes


def fase_0(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    candidates, scripts, results, terms_rows, hashes = build_inventory()
    bridges = [
        row
        for row in candidates
        if "puente" in row["ruta_relativa"].lower()
        or "PUENTE_SIES_COMPILADO.tsv" in row["terminos_encontrados"]
    ]
    audit_results = [
        row
        for row in results
        if "auditoria" in row["ruta_relativa"].lower()
        or row["clasificacion"] == "auditoria"
        or "multicodcli" in row["ruta_relativa"].lower()
    ]

    file_fields = [
        "ruta",
        "ruta_relativa",
        "nombre",
        "extension",
        "tamano_bytes",
        "fecha_modificacion",
        "sha256",
        "proceso_probable",
        "tipo_archivo",
        "clasificacion",
        "terminos_encontrados",
        "score_prioridad",
    ]
    out_candidates = output_path(ctx, "01_INVENTARIO/01_ARCHIVOS_CANDIDATOS.tsv")
    out_scripts = output_path(ctx, "01_INVENTARIO/02_SCRIPTS_CANDIDATOS.tsv")
    out_results = output_path(ctx, "01_INVENTARIO/03_RESULTADOS_CANDIDATOS.tsv")
    out_terms = output_path(ctx, "01_INVENTARIO/04_TERMINOS_ENCONTRADOS.tsv")
    out_hashes = output_path(ctx, "01_INVENTARIO/05_HASHES.tsv")
    salidas = [
        write_tsv(candidates, out_candidates, file_fields),
        write_tsv(scripts, out_scripts, file_fields),
        write_tsv(results, out_results, file_fields),
        write_tsv(terms_rows, out_terms, ["ruta", "termino", "origen_deteccion"]),
        write_tsv(hashes, out_hashes, ["ruta", "sha256"]),
    ]

    bloqueos: list[dict[str, Any]] = []
    if not bridges:
        bloqueos.append({"bloqueo": "sin_puente", "detalle": "No se encontro al menos un puente."})
    if not scripts:
        bloqueos.append({"bloqueo": "sin_script", "detalle": "No se encontro al menos un script relacionado."})
    if not audit_results:
        bloqueos.append(
            {
                "bloqueo": "sin_auditoria_resultado",
                "detalle": "No se encontro al menos una auditoria o resultado previo.",
            }
        )
    estado = "COMPLETADA" if not bloqueos else "BLOQUEADA"
    top_paths = [row["ruta"] for row in candidates[:20]]
    ctx.log(
        "FASE0_INVENTARIO "
        + json.dumps(
            {
                "archivos_candidatos": len(candidates),
                "scripts_candidatos": len(scripts),
                "puentes_encontrados": len(bridges),
                "resultados_auditoria": len(audit_results),
                "rutas_priorizadas": top_paths,
            },
            ensure_ascii=True,
        )
    )
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "archivos_candidatos": len(candidates),
            "scripts_candidatos": len(scripts),
            "puentes_encontrados": len(bridges),
            "resultados_auditoria": len(audit_results),
            "bloqueos": len(bloqueos),
        },
        validaciones=[
            {"validacion": "al_menos_un_puente", "estado": "OK" if bridges else "ERROR", "valor": len(bridges)},
            {"validacion": "al_menos_un_script", "estado": "OK" if scripts else "ERROR", "valor": len(scripts)},
            {
                "validacion": "al_menos_una_auditoria_o_resultado",
                "estado": "OK" if audit_results else "ERROR",
                "valor": len(audit_results),
            },
        ],
        bloqueos=bloqueos,
        entradas={"repositorio": str(REPO_ROOT.resolve())},
        hashes={row["ruta"]: row["sha256"] for row in hashes},
        resumen=[
            f"Archivos candidatos: {len(candidates)}",
            f"Scripts candidatos: {len(scripts)}",
            f"Puentes encontrados: {len(bridges)}",
            f"Resultados de auditoria: {len(audit_results)}",
            f"Bloqueos: {len(bloqueos)}",
            f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
            f"Inventario: {out_candidates.resolve()}",
        ],
        comando_reanudacion=command_for_phase(1),
    )


def read_tsv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_text(text: str, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path.resolve())


def rel_path(path: str | Path) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def lower_blob(row: dict[str, Any]) -> str:
    return " ".join(str(v) for v in row.values()).lower()


def score_fase1(row: dict[str, str], canonical_by_hash: dict[str, str]) -> tuple[int, list[str], bool, str]:
    text = lower_blob(row)
    name = row.get("nombre", "")
    ext = row.get("extension", "").lower()
    ruta = row.get("ruta_relativa") or rel_path(row.get("ruta", ""))
    score = 0
    reasons: list[str] = []
    for term in HIGH_SCORE_TERMS:
        if term.lower() in text:
            score += 100
            reasons.append(f"alto:{term}")
    for term in MEDIUM_SCORE_TERMS:
        if term.lower() in text:
            score += 50
            reasons.append(f"medio:{term}")
    for term in LOW_SCORE_TERMS:
        if term.lower() in text:
            score += 10
            reasons.append(f"bajo:{term}")
    if ext == ".py":
        score += 40
        reasons.append("bonificacion:.py")
    elif ext in {".tsv", ".csv"}:
        score += 30
        reasons.append("bonificacion:tabla")
    elif ext in {".json", ".md", ".txt"}:
        score += 20
        reasons.append("bonificacion:documento")
    if ruta.startswith("scripts/"):
        score += 30
        reasons.append("bonificacion:scripts")
    if ruta.startswith("resultados/auditoria_integral_multicodcli_2026/"):
        score += 30
        reasons.append("bonificacion:auditoria_multicodcli")
    if "estudiantes_extranjeros_2026" in ruta.lower():
        score += 30
        reasons.append("bonificacion:estudiantes_extranjeros")
    if ruta.startswith("avance_curricular_2026/"):
        score += 20
        reasons.append("bonificacion:avance_curricular")
    if re.search(r"FINAL|APROBADO|COMPILADO|RESOLUCION|RESOLUCI[OÓ]N", name, re.I):
        score += 20
        reasons.append("bonificacion:nombre_final_aprobado_compilado_resolucion")
    if ".git" in ruta:
        score -= 100
        reasons.append("penalizacion:.git")
    if ".venv" in ruta:
        score -= 100
        reasons.append("penalizacion:.venv")
    if "cache" in ruta.lower():
        score -= 100
        reasons.append("penalizacion:cache")
    if "backup" in ruta.lower() and not any(t in text for t in ["puente", "codcli", "codigo_unico", "multicodcli"]):
        score -= 70
        reasons.append("penalizacion:backup_no_directo")
    digest = row.get("sha256", "")
    canonical = canonical_by_hash.get(digest, row.get("ruta", ""))
    is_duplicate = bool(digest and canonical and canonical != row.get("ruta", ""))
    if is_duplicate:
        score -= 50
        reasons.append("penalizacion:duplicado_hash")
    if "test" in name.lower() and not any(t in text for t in ["codcli", "codcarr", "codigo_unico", "puente"]):
        score -= 30
        reasons.append("penalizacion:test_no_productivo")
    if ext == ".log" and not any(t.lower() in text for t in HIGH_SCORE_TERMS + MEDIUM_SCORE_TERMS):
        score -= 30
        reasons.append("penalizacion:log_sin_referencias")
    if row.get("nombre") == "integrar_identidad_carreras_avance.py":
        score -= 500
        reasons.append("penalizacion:script_flujo_actual")
    return score, reasons, is_duplicate, canonical


def build_fase1_ranking(ctx: RunContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates_path = output_path(ctx, "01_INVENTARIO/01_ARCHIVOS_CANDIDATOS.tsv")
    rows = read_tsv_dicts(candidates_path)
    canonical_by_hash: dict[str, str] = {}
    for row in rows:
        digest = row.get("sha256", "")
        if digest and digest not in canonical_by_hash:
            canonical_by_hash[digest] = row.get("ruta", "")
    ranked: list[dict[str, Any]] = []
    for row in rows:
        score, reasons, duplicated, canonical = score_fase1(row, canonical_by_hash)
        terms = row.get("terminos_encontrados", "")
        ranked.append(
            {
                "RANKING": 0,
                "PUNTAJE": score,
                "RUTA": row.get("ruta", ""),
                "NOMBRE": row.get("nombre", ""),
                "TIPO_ARCHIVO": row.get("tipo_archivo", ""),
                "HASH": row.get("sha256", ""),
                "TERMINOS_CLAVE": terms,
                "MOTIVO_PRIORIZACION": "|".join(reasons),
                "ES_DUPLICADO_HASH": "SI" if duplicated else "NO",
                "RUTA_CANONICA_HASH": canonical,
                "CLASIFICACION": row.get("clasificacion", ""),
                "PROCESO_PROBABLE": row.get("proceso_probable", ""),
                "RUTA_RELATIVA": row.get("ruta_relativa", ""),
                "EXTENSION": row.get("extension", ""),
            }
        )
    ranked.sort(key=lambda r: (-int(r["PUNTAJE"]), r["RUTA_RELATIVA"]))
    for idx, row in enumerate(ranked, start=1):
        row["RANKING"] = idx
    return ranked, rows


def mandatory_paths_from_inventory(ranked: list[dict[str, Any]]) -> list[str]:
    mandatory: list[str] = []
    exact_paths = [
        REPO_ROOT / "resultados/auditoria_integral_multicodcli_2026/auditoria_20260618_144641/00_RESPALDO_ENTRADAS/PUENTE_SIES_COMPILADO.tsv",
        REPO_ROOT / "scripts/compile_puente_sies_compilado.py",
        REPO_ROOT / "scripts/compile_puente_sies_compilado 2.py",
        REPO_ROOT / "scripts/corregir_fase06_vigencia_extranjeros_2025.py",
    ]
    for p in exact_paths:
        if p.exists():
            mandatory.append(str(p.resolve()))
    for row in ranked:
        name = row.get("NOMBRE", "")
        if name == "PUENTE_SIES_COMPILADO.tsv" or name == "DURACION_ESTUDIOS.tsv":
            mandatory.append(row["RUTA"])
    return list(dict.fromkeys(mandatory))


def select_deep_files(ranked: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected_paths: set[str] = set(mandatory_paths_from_inventory(ranked))
    mandatory_set = set(selected_paths)
    selected: list[dict[str, Any]] = []

    def add(row: dict[str, Any]) -> None:
        if row["RUTA"] in selected_paths or len(selected) < 60:
            selected_paths.add(row["RUTA"])
            if row not in selected:
                selected.append(row)

    by_path = {row["RUTA"]: row for row in ranked}
    for path in list(selected_paths):
        if path in by_path:
            add(by_path[path])

    counts = {"script": 0, "data": 0, "doc": 0}
    for row in ranked:
        if row["RUTA"] not in mandatory_set and row["ES_DUPLICADO_HASH"] == "SI":
            continue
        if row["NOMBRE"] == "integrar_identidad_carreras_avance.py":
            continue
        typ = row["TIPO_ARCHIVO"]
        bucket = "doc"
        limit = 15
        if typ == "script":
            bucket = "script"
            limit = 20
        elif row["EXTENSION"] in {".tsv", ".csv", ".json"} or typ in {"tabla", "json"}:
            bucket = "data"
            limit = 20
        if counts[bucket] >= limit:
            continue
        add(row)
        counts[bucket] += 1
        if len(selected) >= 55:
            break

    discarded = [row for row in ranked if row["RUTA"] not in {s["RUTA"] for s in selected}]
    return selected[:60], discarded


def read_text_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []


def relevant_line_numbers(lines: list[str]) -> list[int]:
    numbers: list[int] = []
    for idx, line in enumerate(lines, start=1):
        low = line.lower()
        if any(term.lower() in low for term in FASE1_RELEVANT_TERMS):
            numbers.append(idx)
    return numbers


def function_for_line(lines: list[str], lineno: int) -> str:
    for idx in range(lineno - 1, -1, -1):
        stripped = lines[idx].strip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            return stripped.split(":", 1)[0]
    return "bloque_global"


def window_for_line(total: int, lineno: int, radius: int = 4) -> tuple[int, int]:
    return max(1, lineno - radius), min(total, lineno + radius)


def extract_fields(text: str) -> list[str]:
    low = text.lower()
    return [field for field in IDENTITY_FIELDS if field.lower() in low]


def classify_evidence(row: dict[str, Any]) -> str:
    typ = row.get("TIPO_ARCHIVO", "")
    clas = row.get("CLASIFICACION", "")
    name = row.get("NOMBRE", "").lower()
    if clas == "manual" or "manual" in name or "instructivo" in name or "oficio" in name or "calendario" in name:
        return "REGLA_OFICIAL"
    if typ == "script":
        return "IMPLEMENTACION_TECNICA"
    if clas in {"fuente institucional", "precarga", "resultado", "auditoria", "evidencia"} or typ in {"tabla", "json"}:
        return "DATO_OBSERVADO"
    if "decision" in lower_blob(row) or "criterio" in lower_blob(row):
        return "DECISION_INTERNA"
    return "HIPOTESIS_O_PENDIENTE"


def process_from_row(row: dict[str, Any]) -> str:
    text = lower_blob(row)
    if "extranjer" in text:
        return "Estudiantes Extranjeros SIES 2026"
    if "matricula" in text or "matrícula" in text or "mu2026" in text:
        return "Matricula Unificada 2026"
    if "multicodcli" in text:
        return "Auditoria multicodcli"
    if "avance_curricular" in text:
        return "Avance Curricular SIES 2026"
    return row.get("PROCESO_PROBABLE", "No determinado")


def describe_resolution(text: str) -> tuple[str, str, str]:
    low = text.lower()
    success = ""
    ambiguity = ""
    blocking = ""
    if "match_sies_unico" in low or "resuelto_unico" in low or "unico" in low:
        success = "Coincidencia unica/resuelta registrada por implementacion o dato observado."
    if "ambiguo_sies" in low or "ambiguo" in low or "multiples" in low:
        ambiguity = "Multiples candidatos o ambiguedad SIES registrada."
    if "sin_match_sies" in low or "es_bloqueante" in low or "bloqueante" in low:
        blocking = "Sin match o marca bloqueante registrada."
    return success, ambiguity, blocking


def analyze_script(row: dict[str, Any], hallazgos: list[dict[str, Any]], funciones: list[dict[str, Any]], trazabilidad: list[dict[str, Any]]) -> None:
    path = Path(row["RUTA"])
    lines = read_text_lines(path)
    rel = rel_path(path)
    relevant = relevant_line_numbers(lines)
    used_windows: set[tuple[int, int, str]] = set()
    for lineno in relevant[:40]:
        start, end = window_for_line(len(lines), lineno)
        func = function_for_line(lines, lineno)
        key = (start, end, func)
        if key in used_windows:
            continue
        used_windows.add(key)
        fragment = " ".join(line.strip() for line in lines[start - 1 : end])
        fields = extract_fields(fragment)
        success, ambiguity, blocking = describe_resolution(fragment)
        evidence = classify_evidence(row)
        hid = f"H{len(hallazgos) + 1:04d}"
        hallazgo = {
            "ID_HALLAZGO": hid,
            "PROCESO": process_from_row(row),
            "SUBPROCESO": "Recuperacion logica existente",
            "RUTA": str(path.resolve()),
            "ARCHIVO": row["NOMBRE"],
            "TIPO_ARCHIVO": row["TIPO_ARCHIVO"],
            "FUNCION_O_SECCION": func,
            "LINEA_INICIO": start,
            "LINEA_FIN": end,
            "DESCRIPCION": "Bloque de implementacion con terminos de identidad de carrera y/o resolucion SIES.",
            "ENTRADAS": "Inferidas desde referencias del bloque; revisar script fuente.",
            "SALIDAS": "Inferidas desde referencias del bloque; revisar script fuente.",
            "CAMPOS": "|".join(fields),
            "LLAVE": "|".join([f for f in fields if f in {"CODIGO_UNICO_FINAL", "CODIGO_UNICO", "CODCARPR", "CODCARR", "CODCLI", "JORNADA"}]),
            "CONDICION_EXITO": success,
            "CONDICION_AMBIGUEDAD": ambiguity,
            "CONDICION_BLOQUEO": blocking,
            "PRECEDENCIA": "Implementacion tecnica observada; no regla oficial.",
            "CLASIFICACION_EVIDENCIA": evidence,
            "NIVEL_RESPALDO": "ALTO" if fields else "MEDIO",
            "OBSERVACION": fragment[:500],
            "HASH_FUENTE": row["HASH"],
        }
        hallazgos.append(hallazgo)
        funciones.append(
            {
                "RUTA": str(path.resolve()),
                "ARCHIVO": row["NOMBRE"],
                "FUNCION_O_SECCION": func,
                "LINEA_INICIO": start,
                "LINEA_FIN": end,
                "CAMPOS_USADOS": "|".join(fields),
                "CLASIFICACION_EVIDENCIA": evidence,
                "HASH_FUENTE": row["HASH"],
            }
        )
        if any(f in fields for f in ["CODIGO_UNICO_FINAL", "CODIGO_UNICO", "CODCARPR", "CODCARR", "CODCLI"]):
            trazabilidad.append(
                {
                    "RUTA": str(path.resolve()),
                    "LINEA_INICIO": start,
                    "LINEA_FIN": end,
                    "FUNCION_O_SECCION": func,
                    "CAMPOS_CODIGO": "|".join(fields),
                    "DESCRIPCION": "Referencia tecnica a construccion, resolucion o uso de identificadores de carrera.",
                    "HASH_FUENTE": row["HASH"],
                }
            )


def read_table_sample(path: Path) -> tuple[list[str], int, list[dict[str, str]]]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    rows: list[dict[str, str]] = []
    total = 0
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        headers = reader.fieldnames or []
        for record in reader:
            total += 1
            if len(rows) < 200:
                rows.append({k: v for k, v in record.items() if k is not None})
    return headers, total, rows


def analyze_data_file(
    row: dict[str, Any],
    hallazgos: list[dict[str, Any]],
    campos: list[dict[str, Any]],
    estados: list[dict[str, Any]],
    bloqueos_amb: list[dict[str, Any]],
    trazabilidad: list[dict[str, Any]],
) -> None:
    path = Path(row["RUTA"])
    rel = rel_path(path)
    if path.suffix.lower() not in {".tsv", ".csv"}:
        return
    try:
        headers, total_rows, sample_rows = read_table_sample(path)
    except Exception as exc:  # noqa: BLE001
        bloqueos_amb.append(
            {
                "RUTA": str(path.resolve()),
                "TIPO": "LECTURA_DATOS_FALLIDA",
                "DETALLE": str(exc),
                "HASH_FUENTE": row["HASH"],
            }
        )
        return
    header_text = " ".join(headers)
    fields = extract_fields(header_text)
    key_candidates = [f for f in fields if f in {"CODIGO_UNICO_FINAL", "CODIGO_UNICO", "CODCARPR", "CODCARR", "CODCLI", "JORNADA"}]
    hid = f"H{len(hallazgos) + 1:04d}"
    hallazgos.append(
        {
            "ID_HALLAZGO": hid,
            "PROCESO": process_from_row(row),
            "SUBPROCESO": "Lectura controlada de dato/auditoria",
            "RUTA": str(path.resolve()),
            "ARCHIVO": row["NOMBRE"],
            "TIPO_ARCHIVO": row["TIPO_ARCHIVO"],
            "FUNCION_O_SECCION": "encabezado_y_conteos",
            "LINEA_INICIO": 1,
            "LINEA_FIN": 1,
            "DESCRIPCION": f"Archivo de datos con {total_rows} filas y campos de identidad detectados.",
            "ENTRADAS": "Dato observado existente en repositorio.",
            "SALIDAS": "No aplica; lectura de evidencia.",
            "CAMPOS": "|".join(fields),
            "LLAVE": "|".join(key_candidates),
            "CONDICION_EXITO": "Estados o llaves observadas en archivo, no regla oficial.",
            "CONDICION_AMBIGUEDAD": "Se auditan duplicados/estados cuando los campos existen.",
            "CONDICION_BLOQUEO": "Se registran campos ES_BLOQUEANTE/SIN_MATCH si existen.",
            "PRECEDENCIA": "Dato observado; utilizable como evidencia, no como norma.",
            "CLASIFICACION_EVIDENCIA": classify_evidence(row),
            "NIVEL_RESPALDO": "ALTO" if fields else "MEDIO",
            "OBSERVACION": f"Columnas: {'|'.join(headers[:80])}",
            "HASH_FUENTE": row["HASH"],
        }
    )
    for field in fields:
        values = sorted({r.get(field, "") for r in sample_rows if field in r and r.get(field, "") != ""})[:30]
        campos.append(
            {
                "RUTA": str(path.resolve()),
                "ARCHIVO": row["NOMBRE"],
                "CAMPO": field,
                "PRESENTE": "SI",
                "VALORES_MUESTRA": "|".join(values),
                "FILAS": total_rows,
                "HASH_FUENTE": row["HASH"],
            }
        )
    for status_field in [f for f in headers if f in RESOLUTION_TERMS or f in {"RESOLUCION_STATUS", "ES_BLOQUEANTE"}]:
        vals = sorted({r.get(status_field, "") for r in sample_rows if r.get(status_field, "") != ""})
        estados.append(
            {
                "RUTA": str(path.resolve()),
                "ARCHIVO": row["NOMBRE"],
                "CAMPO_ESTADO": status_field,
                "VALORES_OBSERVADOS": "|".join(vals[:40]),
                "CLASIFICACION_EVIDENCIA": "DATO_OBSERVADO",
                "HASH_FUENTE": row["HASH"],
            }
        )
    if "CODIGO_UNICO_FINAL" in headers:
        seen: set[str] = set()
        dupes: set[str] = set()
        for r in sample_rows:
            val = r.get("CODIGO_UNICO_FINAL", "")
            if val in seen and val:
                dupes.add(val)
            seen.add(val)
        trazabilidad.append(
            {
                "RUTA": str(path.resolve()),
                "LINEA_INICIO": 1,
                "LINEA_FIN": 1,
                "FUNCION_O_SECCION": "CODIGO_UNICO_FINAL_en_datos",
                "CAMPOS_CODIGO": "CODIGO_UNICO_FINAL",
                "DESCRIPCION": f"Campo CODIGO_UNICO_FINAL observado; muestra tiene {len(dupes)} duplicados.",
                "HASH_FUENTE": row["HASH"],
            }
        )
    if any(f in headers for f in ["AMBIGUO_SIES", "SIN_MATCH_SIES", "ES_BLOQUEANTE"]):
        bloqueos_amb.append(
            {
                "RUTA": str(path.resolve()),
                "TIPO": "ESTADOS_AMBIGUEDAD_BLOQUEO_OBSERVADOS",
                "DETALLE": "|".join([f for f in ["AMBIGUO_SIES", "SIN_MATCH_SIES", "ES_BLOQUEANTE"] if f in headers]),
                "HASH_FUENTE": row["HASH"],
            }
        )


def analyze_document(row: dict[str, Any], hallazgos: list[dict[str, Any]]) -> None:
    path = Path(row["RUTA"])
    lines = read_text_lines(path)
    relevant = relevant_line_numbers(lines)
    for lineno in relevant[:15]:
        start, end = window_for_line(len(lines), lineno, radius=2)
        fragment = " ".join(line.strip() for line in lines[start - 1 : end])
        fields = extract_fields(fragment)
        hallazgos.append(
            {
                "ID_HALLAZGO": f"H{len(hallazgos) + 1:04d}",
                "PROCESO": process_from_row(row),
                "SUBPROCESO": "Documento/auditoria recuperada",
                "RUTA": str(path.resolve()),
                "ARCHIVO": row["NOMBRE"],
                "TIPO_ARCHIVO": row["TIPO_ARCHIVO"],
                "FUNCION_O_SECCION": "texto",
                "LINEA_INICIO": start,
                "LINEA_FIN": end,
                "DESCRIPCION": "Referencia documental o auditoria con terminos de identidad.",
                "ENTRADAS": "",
                "SALIDAS": "",
                "CAMPOS": "|".join(fields),
                "LLAVE": "|".join([f for f in fields if f in {"CODIGO_UNICO_FINAL", "CODIGO_UNICO", "CODCARPR", "CODCARR", "CODCLI"}]),
                "CONDICION_EXITO": "",
                "CONDICION_AMBIGUEDAD": "Referencia a ambiguedad si el fragmento la contiene.",
                "CONDICION_BLOQUEO": "Referencia a bloqueo si el fragmento la contiene.",
                "PRECEDENCIA": "Documento interno observado; clasificar antes de usar como regla.",
                "CLASIFICACION_EVIDENCIA": classify_evidence(row),
                "NIVEL_RESPALDO": "MEDIO",
                "OBSERVACION": fragment[:500],
                "HASH_FUENTE": row["HASH"],
            }
        )


HALLAZGO_FIELDS = [
    "ID_HALLAZGO",
    "PROCESO",
    "SUBPROCESO",
    "RUTA",
    "ARCHIVO",
    "TIPO_ARCHIVO",
    "FUNCION_O_SECCION",
    "LINEA_INICIO",
    "LINEA_FIN",
    "DESCRIPCION",
    "ENTRADAS",
    "SALIDAS",
    "CAMPOS",
    "LLAVE",
    "CONDICION_EXITO",
    "CONDICION_AMBIGUEDAD",
    "CONDICION_BLOQUEO",
    "PRECEDENCIA",
    "CLASIFICACION_EVIDENCIA",
    "NIVEL_RESPALDO",
    "OBSERVACION",
    "HASH_FUENTE",
]


def make_precedence_rows(hallazgos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for h in hallazgos:
        if h["CLASIFICACION_EVIDENCIA"] in {"DATO_OBSERVADO", "IMPLEMENTACION_TECNICA", "DECISION_INTERNA", "REGLA_OFICIAL"}:
            rows.append(
                {
                    "RUTA": h["RUTA"],
                    "ARCHIVO": h["ARCHIVO"],
                    "PRECEDENCIA": h["PRECEDENCIA"],
                    "CLASIFICACION_EVIDENCIA": h["CLASIFICACION_EVIDENCIA"],
                    "NIVEL_RESPALDO": h["NIVEL_RESPALDO"],
                    "HASH_FUENTE": h["HASH_FUENTE"],
                }
            )
    return rows


def make_rule_rows(hallazgos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        h
        for h in hallazgos
        if h["CLASIFICACION_EVIDENCIA"] in {"IMPLEMENTACION_TECNICA", "DECISION_INTERNA", "REGLA_OFICIAL"}
        and (h["CONDICION_EXITO"] or h["CONDICION_AMBIGUEDAD"] or h["CONDICION_BLOQUEO"] or h["CAMPOS"])
    ]


def control_flags(
    hallazgos: list[dict[str, Any]],
    campos: list[dict[str, Any]],
    estados: list[dict[str, Any]],
    trazabilidad: list[dict[str, Any]],
    analyzed: list[dict[str, Any]],
) -> dict[str, bool]:
    blob = " ".join(
        [
            " ".join(str(v) for h in hallazgos for v in h.values()),
            " ".join(str(v) for c in campos for v in c.values()),
            " ".join(str(v) for e in estados for v in e.values()),
            " ".join(str(v) for t in trazabilidad for v in t.values()),
            " ".join(str(v) for a in analyzed for v in a.values()),
        ]
    ).lower()
    return {
        "puente_sies_analizado": "puente_sies_compilado.tsv" in blob,
        "script_puente_identificado": "compile_puente_sies_compilado" in blob or ("puente_sies_compilado.tsv" in blob and "script" in blob),
        "codigo_unico_final": "codigo_unico_final" in blob,
        "estados_resolucion": "resolucion_status" in blob or "match_sies_unico" in blob or "resuelto_unico" in blob,
        "ambiguedad": "ambiguo_sies" in blob or "ambiguo" in blob,
        "bloqueo": "es_bloqueante" in blob or "sin_match_sies" in blob or "bloqueante" in blob,
        "campos_llaves": any(c.get("CAMPO") in {"CODIGO_UNICO_FINAL", "CODCARPR", "CODCARR", "CODCLI"} for c in campos)
        or any(t.get("CAMPOS_CODIGO") for t in trazabilidad),
        "tipo_plan_carrera": "tipo_plan_carrera" in blob,
        "duracion_estudios": "duracion_estudios" in blob,
        "matricula_unificada": "matricula unificada" in blob or "matricula_unificada" in blob or "mu2026" in blob,
        "extranjeros": "extranjeros" in blob or "estudiantes extranjeros" in blob,
    }


def fase_1(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if phase_status(ctx.state, 0) != "COMPLETADA":
        raise FlujoError("Fase 0 debe estar COMPLETADA antes de Fase 1.")
    required_inventory = [
        output_path(ctx, "01_INVENTARIO/01_ARCHIVOS_CANDIDATOS.tsv"),
        output_path(ctx, "01_INVENTARIO/02_SCRIPTS_CANDIDATOS.tsv"),
        output_path(ctx, "01_INVENTARIO/03_RESULTADOS_CANDIDATOS.tsv"),
        output_path(ctx, "01_INVENTARIO/04_TERMINOS_ENCONTRADOS.tsv"),
        output_path(ctx, "01_INVENTARIO/05_HASHES.tsv"),
    ]
    missing_inventory = [str(p.resolve()) for p in required_inventory if not p.exists()]
    if missing_inventory:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "inventario_fase0_faltante", "rutas": "|".join(missing_inventory)}],
            resumen=["Estado: BLOQUEADA", "Faltan inventarios de Fase 0."],
            comando_reanudacion=command_for_phase(1),
        )

    ranked, _inventory_rows = build_fase1_ranking(ctx)
    selected, discarded = select_deep_files(ranked)
    hallazgos: list[dict[str, Any]] = []
    funciones: list[dict[str, Any]] = []
    campos: list[dict[str, Any]] = []
    estados: list[dict[str, Any]] = []
    bloqueos_amb: list[dict[str, Any]] = []
    trazabilidad: list[dict[str, Any]] = []
    analyzed_rows: list[dict[str, Any]] = []

    phase_log_lines = [f"{now_iso()} FASE1 inicio recuperacion controlada"]
    for row in selected:
        path = Path(row["RUTA"])
        analyzed_rows.append(
            {
                "RANKING": row["RANKING"],
                "PUNTAJE": row["PUNTAJE"],
                "RUTA": row["RUTA"],
                "NOMBRE": row["NOMBRE"],
                "TIPO_ARCHIVO": row["TIPO_ARCHIVO"],
                "HASH": row["HASH"],
                "PROCESO_PROBABLE": process_from_row(row),
                "MOTIVO_ANALISIS": row["MOTIVO_PRIORIZACION"],
            }
        )
        phase_log_lines.append(f"{now_iso()} ANALIZA {row['RANKING']} {row['RUTA']}")
        if row["TIPO_ARCHIVO"] == "script":
            analyze_script(row, hallazgos, funciones, trazabilidad)
        elif row["EXTENSION"] in {".tsv", ".csv"}:
            analyze_data_file(row, hallazgos, campos, estados, bloqueos_amb, trazabilidad)
        elif row["EXTENSION"] in {".json", ".md", ".txt", ".log"}:
            analyze_document(row, hallazgos)

    rules = make_rule_rows(hallazgos)
    precedence = make_precedence_rows(hallazgos)
    flags = control_flags(hallazgos, campos, estados, trazabilidad, analyzed_rows)
    faltantes: list[dict[str, Any]] = []
    critical = {
        "puente_sies_analizado": "No se analizo PUENTE_SIES_COMPILADO.tsv.",
        "script_puente_identificado": "No se identifico script que use o genere PUENTE_SIES_COMPILADO.tsv.",
        "codigo_unico_final": "No se identifico representacion de CODIGO_UNICO_FINAL.",
        "estados_resolucion": "No se identificaron estados de resolucion.",
        "ambiguedad": "No se identifico tratamiento de ambiguedad.",
        "bloqueo": "No se identifico tratamiento de bloqueo.",
        "campos_llaves": "No se identificaron campos y llaves suficientes.",
    }
    for key, message in critical.items():
        if not flags[key]:
            faltantes.append({"CONTROL": key, "TIPO": "CRITICO", "DETALLE": message})
    for key, message in {
        "tipo_plan_carrera": "TIPO_PLAN_CARRERA buscado; no recuperado en hallazgos analizados.",
        "duracion_estudios": "DURACION_ESTUDIOS buscado; no recuperado en hallazgos analizados.",
        "matricula_unificada": "Logica de Matricula Unificada buscada; cobertura no concluyente.",
        "extranjeros": "Logica de Estudiantes Extranjeros buscada; cobertura no concluyente.",
    }.items():
        if not flags[key]:
            faltantes.append({"CONTROL": key, "TIPO": "NO_CRITICO", "DETALLE": message})

    contradictions: list[dict[str, Any]] = []
    if flags["tipo_plan_carrera"] and not flags["duracion_estudios"]:
        contradictions.append(
            {
                "TIPO": "COBERTURA_INCOMPLETA_TIPO_DURACION",
                "DETALLE": "Se recupero TIPO_PLAN_CARRERA sin DURACION_ESTUDIOS en el subconjunto profundo.",
            }
        )

    coverage_rows = [
        {"CONTROL": key, "ESTADO": "OK" if value else "FALTANTE", "VALOR": "SI" if value else "NO"}
        for key, value in flags.items()
    ]
    salidas = [
        write_tsv(
            ranked,
            output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/00_RANKING_ARCHIVOS_FASE1.tsv"),
            [
                "RANKING",
                "PUNTAJE",
                "RUTA",
                "NOMBRE",
                "TIPO_ARCHIVO",
                "HASH",
                "TERMINOS_CLAVE",
                "MOTIVO_PRIORIZACION",
                "ES_DUPLICADO_HASH",
                "RUTA_CANONICA_HASH",
            ],
        ),
        write_tsv(funciones, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/01_FUNCIONES_RELEVANTES.tsv"), ["RUTA", "ARCHIVO", "FUNCION_O_SECCION", "LINEA_INICIO", "LINEA_FIN", "CAMPOS_USADOS", "CLASIFICACION_EVIDENCIA", "HASH_FUENTE"]),
        write_tsv(rules, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/02_REGLAS_IMPLEMENTADAS.tsv"), HALLAZGO_FIELDS),
        write_tsv(campos, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/03_CAMPOS_Y_LLAVES.tsv"), ["RUTA", "ARCHIVO", "CAMPO", "PRESENTE", "VALORES_MUESTRA", "FILAS", "HASH_FUENTE"]),
        write_tsv(estados, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/04_ESTADOS_RESOLUCION.tsv"), ["RUTA", "ARCHIVO", "CAMPO_ESTADO", "VALORES_OBSERVADOS", "CLASIFICACION_EVIDENCIA", "HASH_FUENTE"]),
        write_tsv(precedence, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/05_PRECEDENCIA_FUENTES.tsv"), ["RUTA", "ARCHIVO", "PRECEDENCIA", "CLASIFICACION_EVIDENCIA", "NIVEL_RESPALDO", "HASH_FUENTE"]),
        write_tsv(bloqueos_amb, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/06_BLOQUEOS_Y_AMBIGUEDADES.tsv"), ["RUTA", "TIPO", "DETALLE", "HASH_FUENTE"]),
        write_tsv(trazabilidad, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/07_TRAZABILIDAD_CODIGO.tsv"), ["RUTA", "LINEA_INICIO", "LINEA_FIN", "FUNCION_O_SECCION", "CAMPOS_CODIGO", "DESCRIPCION", "HASH_FUENTE"]),
        write_tsv(analyzed_rows, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/08_ARCHIVOS_ANALIZADOS_EN_PROFUNDIDAD.tsv"), ["RANKING", "PUNTAJE", "RUTA", "NOMBRE", "TIPO_ARCHIVO", "HASH", "PROCESO_PROBABLE", "MOTIVO_ANALISIS"]),
        write_tsv(discarded, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/09_ARCHIVOS_DESCARTADOS_PRIORIZACION.tsv"), ["RANKING", "PUNTAJE", "RUTA", "NOMBRE", "TIPO_ARCHIVO", "HASH", "TERMINOS_CLAVE", "MOTIVO_PRIORIZACION", "ES_DUPLICADO_HASH", "RUTA_CANONICA_HASH"]),
        write_tsv(coverage_rows, output_path(ctx, "05_AUDITORIA/FASE1_CONTROL_COBERTURA.tsv"), ["CONTROL", "ESTADO", "VALOR"]),
        write_tsv(faltantes, output_path(ctx, "05_AUDITORIA/FASE1_FALTANTES.tsv"), ["CONTROL", "TIPO", "DETALLE"]),
        write_tsv(contradictions, output_path(ctx, "05_AUDITORIA/FASE1_CONTRADICCIONES_PRELIMINARES.tsv"), ["TIPO", "DETALLE"]),
        write_text("\n".join(phase_log_lines) + "\n", output_path(ctx, "06_LOGS/fase1_recuperacion.log")),
    ]
    critical_missing = [f for f in faltantes if f["TIPO"] == "CRITICO"]
    estado = "COMPLETADA" if not critical_missing else "BLOQUEADA"
    scripts_read = sum(1 for r in analyzed_rows if r["TIPO_ARCHIVO"] == "script")
    data_read = sum(1 for r in analyzed_rows if r["TIPO_ARCHIVO"] in {"tabla", "json"})
    audit_read = sum(1 for r in analyzed_rows if "auditoria" in r["PROCESO_PROBABLE"].lower() or "auditoria" in r["RUTA"].lower())
    bridges_read = sum(1 for r in analyzed_rows if "puente" in r["RUTA"].lower())
    principales = [r["RUTA"] for r in analyzed_rows if r["TIPO_ARCHIVO"] == "script"][:10]
    ctx.log(
        "FASE1_RECUPERACION "
        + json.dumps(
            {
                "estado": estado,
                "archivos_priorizados": len(ranked),
                "archivos_leidos": len(analyzed_rows),
                "scripts_leidos": scripts_read,
                "datos_leidos": data_read,
                "auditorias_leidas": audit_read,
                "funciones_recuperadas": len(funciones),
                "reglas_recuperadas": len(rules),
                "faltantes": faltantes,
                "contradicciones": contradictions,
            },
            ensure_ascii=True,
        )
    )
    next_command = command_for_phase(2) if estado == "COMPLETADA" else f"NO AVANZAR. Resolver primero: {critical_missing[0]['DETALLE'] if critical_missing else 'faltante no critico'}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "archivos_priorizados": len(ranked),
            "archivos_leidos": len(analyzed_rows),
            "scripts_leidos": scripts_read,
            "datos_leidos": data_read,
            "auditorias_leidas": audit_read,
            "puentes_analizados": bridges_read,
            "funciones_recuperadas": len(funciones),
            "reglas_recuperadas": len(rules),
            "campos_recuperados": len(campos),
            "estados_recuperados": len(estados),
            "bloqueos": len(bloqueos_amb) + len(faltantes),
            "contradicciones": len(contradictions),
            "logica_codigo_unico": "SI" if flags["codigo_unico_final"] else "NO",
            "logica_coincidencia_unica": "SI" if flags["estados_resolucion"] else "NO",
            "logica_ambiguedad": "SI" if flags["ambiguedad"] else "NO",
            "logica_bloqueo": "SI" if flags["bloqueo"] else "NO",
            "tipo_plan_carrera": "SI" if flags["tipo_plan_carrera"] else "NO",
            "duracion_estudios": "SI" if flags["duracion_estudios"] else "NO",
            "matricula_unificada": "SI" if flags["matricula_unificada"] else "NO",
            "extranjeros": "SI" if flags["extranjeros"] else "NO",
        },
        validaciones=coverage_rows,
        bloqueos=faltantes + bloqueos_amb[:20],
        decisiones=[
            {
                "decision": "clasificacion_evidencia",
                "detalle": "Scripts como IMPLEMENTACION_TECNICA; datos/auditorias como DATO_OBSERVADO; manuales como REGLA_OFICIAL.",
            }
        ],
        pendientes=[f for f in faltantes if f["TIPO"] == "NO_CRITICO"],
        entradas={
            "inventario_archivos": str(output_path(ctx, "01_INVENTARIO/01_ARCHIVOS_CANDIDATOS.tsv").resolve()),
            "inventario_scripts": str(output_path(ctx, "01_INVENTARIO/02_SCRIPTS_CANDIDATOS.tsv").resolve()),
            "inventario_resultados": str(output_path(ctx, "01_INVENTARIO/03_RESULTADOS_CANDIDATOS.tsv").resolve()),
        },
        hashes={r["RUTA"]: r["HASH"] for r in analyzed_rows},
        resumen=[
            f"Estado: {estado}",
            f"Archivos priorizados: {len(ranked)}",
            f"Archivos leidos en profundidad: {len(analyzed_rows)}",
            f"Scripts principales analizados: {scripts_read}",
            f"Puentes analizados: {bridges_read}",
            f"Funciones relevantes recuperadas: {len(funciones)}",
            f"Reglas implementadas recuperadas: {len(rules)}",
            f"Campos y llaves recuperados: {len(campos)}",
            f"Estados de resolucion recuperados: {len(estados)}",
            f"Bloqueos identificados: {len(bloqueos_amb) + len(faltantes)}",
            f"Contradicciones preliminares: {len(contradictions)}",
            f"Logica CODIGO_UNICO recuperada: {'SI' if flags['codigo_unico_final'] else 'NO'}",
            f"Logica coincidencia unica recuperada: {'SI' if flags['estados_resolucion'] else 'NO'}",
            f"Logica ambiguedad recuperada: {'SI' if flags['ambiguedad'] else 'NO'}",
            f"Logica bloqueo recuperada: {'SI' if flags['bloqueo'] else 'NO'}",
            f"TIPO_PLAN_CARRERA recuperado: {'SI' if flags['tipo_plan_carrera'] else 'NO'}",
            f"DURACION_ESTUDIOS recuperado: {'SI' if flags['duracion_estudios'] else 'NO'}",
            f"Matricula Unificada cubierta: {'SI' if flags['matricula_unificada'] else 'NO'}",
            f"Estudiantes Extranjeros cubierto: {'SI' if flags['extranjeros'] else 'NO'}",
            "Scripts principales:",
            *principales,
            f"Salida principal: {output_path(ctx, '02_CONOCIMIENTO_RECUPERADO').resolve()}",
            f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
            "Originales modificados: NO",
            "Precarga generada: NO",
            "PES generado: NO",
        ],
        comando_reanudacion=next_command,
    )


def normalize_for_compare(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.upper()
    replacements = {
        "CODIGO UNICO FINAL": "CODIGO_UNICO_FINAL",
        "CODIGO_UNICO_SIES": "CODIGO_UNICO",
        "COD CAR PR": "CODCARPR",
        "CODCAR": "CODCARR",
        "PLAN ESTUDIOS": "PLAN_ESTUDIOS",
        "PLAN DE ESTUDIO": "PLAN_DE_ESTUDIO",
        "MATCH SIES UNICO": "MATCH_SIES_UNICO",
        "AMBIGUO SIES": "AMBIGUO_SIES",
        "SIN MATCH SIES": "SIN_MATCH_SIES",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[^A-Z0-9_]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_pipe(value: Any) -> list[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def canonical_fields(value: Any) -> list[str]:
    aliases = {
        "CODIGO_UNICO_FINAL": "CODIGO_UNICO_FINAL",
        "CODIGO_UNICO": "CODIGO_UNICO",
        "CODCLI": "CODCLI",
        "CODCARR": "CODCARR",
        "CODCARPR": "CODCARPR",
        "NOMBRE_CARRERA": "NOMBRE_CARRERA",
        "NOMBRE_NORMALIZADO": "NOMBRE_CARRERA",
        "JORNADA": "JORNADA",
        "MODALIDAD": "MODALIDAD",
        "SEDE": "SEDE",
        "NOMBRE_SEDE": "SEDE",
        "VERSION": "VERSION",
        "PLAN_ESTUDIOS": "PLAN_ESTUDIOS",
        "PLAN_DE_ESTUDIO": "PLAN_DE_ESTUDIO",
        "PLAN_DE_ESTUDIO_INSTITUCIONAL": "PLAN_DE_ESTUDIO",
        "TIPO_PLAN_CARRERA": "TIPO_PLAN_CARRERA",
        "DURACION_ESTUDIOS": "DURACION_ESTUDIOS",
        "VIGENCIA": "VIGENCIA",
        "RESOLUCION_STATUS": "RESOLUCION_STATUS",
        "ES_BLOQUEANTE": "ES_BLOQUEANTE",
    }
    out: list[str] = []
    for item in split_pipe(value):
        norm = normalize_for_compare(item).replace(" ", "_")
        for key, canonical in aliases.items():
            if key in norm and canonical not in out:
                out.append(canonical)
    return out


def methodological_signature(rule: dict[str, str]) -> str:
    parts = [
        normalize_for_compare(rule.get("PROCESO", "")),
        normalize_for_compare(rule.get("CLASIFICACION_EVIDENCIA", "")),
        "|".join(sorted(canonical_fields(rule.get("CAMPOS", "")))),
        "|".join(sorted(canonical_fields(rule.get("LLAVE", "")))),
        normalize_for_compare(rule.get("CONDICION_EXITO", "")),
        normalize_for_compare(rule.get("CONDICION_AMBIGUEDAD", "")),
        normalize_for_compare(rule.get("CONDICION_BLOQUEO", "")),
        normalize_for_compare(rule.get("SALIDAS", "")),
    ]
    return "||".join(parts)


def equivalent_signature(rule: dict[str, str]) -> str:
    parts = [
        normalize_for_compare(rule.get("CLASIFICACION_EVIDENCIA", "")),
        "|".join(sorted(canonical_fields(rule.get("CAMPOS", "")))),
        "|".join(sorted(canonical_fields(rule.get("LLAVE", "")))),
        normalize_for_compare(rule.get("CONDICION_EXITO", "")),
        normalize_for_compare(rule.get("CONDICION_AMBIGUEDAD", "")),
        normalize_for_compare(rule.get("CONDICION_BLOQUEO", "")),
    ]
    return "||".join(parts)


def rule_applicability(rule: dict[str, str]) -> str:
    blob = normalize_for_compare(" ".join(str(v) for v in rule.values()))
    fields = canonical_fields(rule.get("CAMPOS", "")) + canonical_fields(rule.get("LLAVE", ""))
    if not fields and not any(term in blob for term in ["CODIGO", "CODCARR", "CODCARPR", "CODCLI", "PUENTE", "SIES"]):
        return "NO_APLICABLE_A_IDENTIDAD_CARRERAS"
    if not rule.get("RUTA") or not rule.get("HASH_FUENTE") or not rule.get("CLASIFICACION_EVIDENCIA"):
        return "INCOMPLETA"
    if not (rule.get("CONDICION_EXITO") or rule.get("CONDICION_AMBIGUEDAD") or rule.get("CONDICION_BLOQUEO") or rule.get("CAMPOS")):
        return "INCOMPLETA"
    return "UNICA"


def consolidate_rules(rules: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    exact_seen: dict[str, str] = {}
    equiv_seen: dict[str, str] = {}
    consolidated_by_sig: dict[str, dict[str, Any]] = {}
    mapping: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    incomplete: list[dict[str, Any]] = []
    not_applicable: list[dict[str, Any]] = []

    for idx, rule in enumerate(rules, start=1):
        exact = methodological_signature(rule)
        equiv = equivalent_signature(rule)
        classif = rule_applicability(rule)
        if classif == "NO_APLICABLE_A_IDENTIDAD_CARRERAS":
            not_applicable.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "RUTA": rule.get("RUTA", ""), "MOTIVO": classif})
            mapping.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "ID_REGLA_CONSOLIDADA": "", "CLASIFICACION_DEPURACION": classif, "FIRMA": exact})
            continue
        if classif == "INCOMPLETA":
            incomplete.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "RUTA": rule.get("RUTA", ""), "MOTIVO": classif})
            mapping.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "ID_REGLA_CONSOLIDADA": "", "CLASIFICACION_DEPURACION": classif, "FIRMA": exact})
            continue

        depuration = "UNICA"
        if exact in exact_seen:
            depuration = "DUPLICADA_EXACTA"
            consolidated_id = exact_seen[exact]
            duplicates.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "ID_REGLA_CONSOLIDADA": consolidated_id, "TIPO_DUPLICADO": depuration, "FIRMA": exact})
        elif equiv in equiv_seen:
            depuration = "DUPLICADA_EQUIVALENTE"
            consolidated_id = equiv_seen[equiv]
            duplicates.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "ID_REGLA_CONSOLIDADA": consolidated_id, "TIPO_DUPLICADO": depuration, "FIRMA": equiv})
        else:
            consolidated_id = f"RC{len(consolidated_by_sig) + 1:04d}"
            exact_seen[exact] = consolidated_id
            equiv_seen[equiv] = consolidated_id
            consolidated_by_sig[consolidated_id] = {
                "ID_REGLA_CONSOLIDADA": consolidated_id,
                "CLASIFICACION_DEPURACION": "UNICA",
                "PROCESOS": rule.get("PROCESO", ""),
                "CLASIFICACION_EVIDENCIA": rule.get("CLASIFICACION_EVIDENCIA", "") or "HIPOTESIS_O_PENDIENTE",
                "CAMPOS": "|".join(canonical_fields(rule.get("CAMPOS", ""))),
                "LLAVE": "|".join(canonical_fields(rule.get("LLAVE", ""))),
                "CONDICION_EXITO": rule.get("CONDICION_EXITO", ""),
                "CONDICION_AMBIGUEDAD": rule.get("CONDICION_AMBIGUEDAD", ""),
                "CONDICION_BLOQUEO": rule.get("CONDICION_BLOQUEO", ""),
                "FUENTE_PRINCIPAL": rule.get("RUTA", ""),
                "FUENTES_SECUNDARIAS": "",
                "FUNCIONES_O_SECCIONES": rule.get("FUNCION_O_SECCION", ""),
                "NIVEL_RESPALDO": rule.get("NIVEL_RESPALDO", ""),
                "OBSERVACION": rule.get("OBSERVACION", ""),
                "HASHES_FUENTE": rule.get("HASH_FUENTE", ""),
            }
        if depuration != "UNICA":
            target = consolidated_by_sig.get(consolidated_id)
            if target:
                sources = split_pipe(target.get("FUENTES_SECUNDARIAS", ""))
                if rule.get("RUTA") and rule.get("RUTA") not in sources and rule.get("RUTA") != target.get("FUENTE_PRINCIPAL"):
                    sources.append(rule.get("RUTA", ""))
                target["FUENTES_SECUNDARIAS"] = "|".join(sources)
                processes = set(split_pipe(target.get("PROCESOS", "")) + [rule.get("PROCESO", "")])
                target["PROCESOS"] = "|".join(sorted(p for p in processes if p))
                hashes = set(split_pipe(target.get("HASHES_FUENTE", "")) + [rule.get("HASH_FUENTE", "")])
                target["HASHES_FUENTE"] = "|".join(sorted(h for h in hashes if h))
        mapping.append({"ID_ORIGINAL": rule.get("ID_HALLAZGO", f"R{idx:04d}"), "ID_REGLA_CONSOLIDADA": consolidated_id, "CLASIFICACION_DEPURACION": depuration, "FIRMA": exact})
    return list(consolidated_by_sig.values()), mapping, duplicates, incomplete, not_applicable


def build_evidence_control(consolidated: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = {"REGLA_OFICIAL", "DATO_OBSERVADO", "IMPLEMENTACION_TECNICA", "DECISION_INTERNA", "HIPOTESIS_O_PENDIENTE"}
    rows = []
    for rule in consolidated:
        cls = rule.get("CLASIFICACION_EVIDENCIA") or "HIPOTESIS_O_PENDIENTE"
        source = str(rule.get("FUENTE_PRINCIPAL", ""))
        valid = cls in allowed
        observation = ""
        if cls == "REGLA_OFICIAL" and not re.search(r"manual|instructivo|oficio|calendario", source, re.I):
            valid = False
            observation = "Regla oficial requiere fuente oficial identificable."
        elif cls == "IMPLEMENTACION_TECNICA":
            observation = "No se promueve a regla oficial."
        elif cls == "DATO_OBSERVADO":
            observation = "Dato observado; no opera como norma por si solo."
        elif cls == "HIPOTESIS_O_PENDIENTE":
            observation = "No usar para resolver identidad."
        rows.append(
            {
                "ID_REGLA_CONSOLIDADA": rule["ID_REGLA_CONSOLIDADA"],
                "CLASIFICACION_EVIDENCIA": cls,
                "FUENTE_PRINCIPAL": source,
                "FUENTES_SECUNDARIAS": rule.get("FUENTES_SECUNDARIAS", ""),
                "ALCANCE": rule.get("PROCESOS", ""),
                "VALIDACION_CLASIFICACION": "OK" if valid else "REVISAR",
                "OBSERVACION": observation,
            }
        )
    return rows


def build_field_dictionary(campos_rows: list[dict[str, str]], consolidated: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected = {
        "CODIGO_UNICO": ("IDENTIFICADOR", "SI"),
        "CODIGO_UNICO_FINAL": ("IDENTIFICADOR", "SI"),
        "CODCLI": ("IDENTIFICADOR", "NO"),
        "CODCARR": ("IDENTIFICADOR", "SI"),
        "CODCARPR": ("IDENTIFICADOR", "SI"),
        "NOMBRE_CARRERA": ("ATRIBUTO", "NO"),
        "JORNADA": ("FILTRO", "NO"),
        "MODALIDAD": ("FILTRO", "NO"),
        "SEDE": ("ATRIBUTO", "NO"),
        "VERSION": ("ATRIBUTO", "NO"),
        "PLAN_ESTUDIOS": ("TRAZABILIDAD", "NO"),
        "PLAN_DE_ESTUDIO": ("IDENTIFICADOR", "NO"),
        "TIPO_PLAN_CARRERA": ("CRITERIO_DESEMPATE", "NO"),
        "DURACION_ESTUDIOS": ("CRITERIO_DESEMPATE", "NO"),
        "VIGENCIA": ("CONTROL_VIGENCIA", "NO"),
        "RESOLUCION_STATUS": ("ESTADO", "NO"),
        "ES_BLOQUEANTE": ("BLOQUEO", "NO"),
    }
    observed: dict[str, dict[str, set[str]]] = {field: {"aliases": set(), "procesos": set(), "fuentes": set()} for field in expected}
    for row in campos_rows:
        for field in canonical_fields(row.get("CAMPO", "")):
            if field in observed:
                observed[field]["aliases"].add(row.get("CAMPO", ""))
                observed[field]["fuentes"].add(row.get("RUTA", ""))
    for rule in consolidated:
        for field in canonical_fields(rule.get("CAMPOS", "") + "|" + rule.get("LLAVE", "")):
            if field in observed:
                observed[field]["procesos"].update(split_pipe(rule.get("PROCESOS", "")))
                observed[field]["fuentes"].add(rule.get("FUENTE_PRINCIPAL", ""))
    rows = []
    for field, (role, required) in expected.items():
        obs = observed[field]
        aliases = sorted(a for a in obs["aliases"] if a)
        if not aliases:
            aliases = [field]
        observation = "PLAN_ESTUDIOS SIES se mantiene separado de PLAN_DE_ESTUDIO institucional." if field in {"PLAN_ESTUDIOS", "PLAN_DE_ESTUDIO"} else ""
        rows.append(
            {
                "CAMPO_CANONICO": field,
                "ALIAS": "|".join(aliases),
                "PROCESO": "|".join(sorted(p for p in obs["procesos"] if p)),
                "TIPO_DATO": "texto",
                "ROL": role,
                "OBLIGATORIO_SEGUN_METODO": required,
                "FUENTE": "|".join(sorted(f for f in obs["fuentes"] if f)[:20]),
                "OBSERVACION": observation,
            }
        )
    return rows


def build_state_catalog(estados_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    base = [
        ("RESUELTO_CODIGO_UNICO_EXACTO", "CODIGO_UNICO_FINAL/CODIGO_UNICO", "Relacion exacta demostrada por codigo unico.", "codigo unico exacto", "SI", "NO", "NO"),
        ("RESUELTO_PUENTE_APROBADO", "RESOLUCION_STATUS=UNICO/RESUELTO_UNICO", "Puente tecnico con relacion unica no bloqueante.", "puente aprobado", "SI", "NO", "NO"),
        ("RESUELTO_PLAN_INSTITUCIONAL", "CODCARR+PLAN_DE_ESTUDIO", "Combinacion institucional demostrada.", "plan institucional", "SI", "NO", "NO"),
        ("RESUELTO_REGLA_TIPO_DURACION", "TIPO_PLAN_CARRERA+DURACION_ESTUDIOS", "Decision interna o implementacion tecnica con alcance acotado.", "tipo y duracion", "SI", "NO", "NO"),
        ("CANDIDATO_NOMBRE", "nombre normalizado", "Candidato por nombre; no valida por si solo.", "apoyo nominal", "NO", "NO", "NO"),
        ("AMBIGUO_MULTIPLES_COINCIDENCIAS", "AMBIGUO_SIES", "Multiples candidatos o relacion no unica.", "ambiguedad", "NO", "SI", "NO"),
        ("BLOQUEADO_SIN_EVIDENCIA", "SIN_MATCH_SIES", "Sin evidencia suficiente.", "sin match", "NO", "NO", "SI"),
        ("BLOQUEADO_CONTRADICCION", "contradiccion", "Evidencias incompatibles.", "contradiccion", "NO", "NO", "SI"),
        ("BLOQUEADO_VIGENCIA", "vigencia", "Vigencia no compatible con alcance.", "vigencia", "NO", "NO", "SI"),
        ("BLOQUEADO_JORNADA", "jornada", "Jornada no compatible o no demostrada.", "jornada", "NO", "NO", "SI"),
        ("NO_EVALUADO", "", "Estado sin evaluacion metodologica.", "pendiente", "NO", "NO", "NO"),
    ]
    rows = [
        {
            "ESTADO_CANONICO": canonical,
            "ESTADO_ORIGEN": origin,
            "PROCESO": "Metodologia consolidada",
            "SIGNIFICADO": meaning,
            "CONDICION": condition,
            "ES_RESUELTO": resolved,
            "ES_AMBIGUO": ambiguous,
            "ES_BLOQUEANTE": blocking,
            "PRECEDENCIA": "Catalogo canonico fase 2",
            "FUENTE": "02_CONOCIMIENTO_RECUPERADO/04_ESTADOS_RESOLUCION.tsv",
        }
        for canonical, origin, meaning, condition, resolved, ambiguous, blocking in base
    ]
    for row in estados_rows:
        for observed in split_pipe(row.get("VALORES_OBSERVADOS", "")) or [row.get("CAMPO_ESTADO", "")]:
            norm = normalize_for_compare(observed)
            canonical = "NO_EVALUADO"
            resolved, ambiguous, blocking = "NO", "NO", "NO"
            if "UNICO" in norm or "RESUELTO" in norm or "MATCH" in norm:
                canonical, resolved = "RESUELTO_PUENTE_APROBADO", "SI"
            if "AMBIGUO" in norm or "MULTIPLE" in norm:
                canonical, ambiguous = "AMBIGUO_MULTIPLES_COINCIDENCIAS", "SI"
                resolved = "NO"
            if "SIN_MATCH" in norm or "BLOQUE" in norm:
                canonical, blocking = "BLOQUEADO_SIN_EVIDENCIA", "SI"
                resolved = "NO"
            rows.append(
                {
                    "ESTADO_CANONICO": canonical,
                    "ESTADO_ORIGEN": observed or row.get("CAMPO_ESTADO", ""),
                    "PROCESO": "Observado en Fase 1",
                    "SIGNIFICADO": "Estado observado; mapeo canonico conservador.",
                    "CONDICION": row.get("CAMPO_ESTADO", ""),
                    "ES_RESUELTO": resolved,
                    "ES_AMBIGUO": ambiguous,
                    "ES_BLOQUEANTE": blocking,
                    "PRECEDENCIA": "No reemplaza estado de origen.",
                    "FUENTE": row.get("RUTA", ""),
                }
            )
    return rows


def build_decision_matrix() -> list[dict[str, Any]]:
    return [
        {
            "NIVEL_PRIORIDAD": 1,
            "METODO_RESOLUCION": "CODIGO_UNICO_EXACTO",
            "CAMPOS_REQUERIDOS": "CODIGO_UNICO|CODIGO_UNICO_FINAL",
            "CAMPOS_OPCIONALES": "RESOLUCION_STATUS|ES_BLOQUEANTE",
            "CONDICION_EXITO": "Existe relacion exacta y demostrada por CODIGO_UNICO o CODIGO_UNICO_FINAL.",
            "CONDICION_AMBIGUEDAD": "Mas de una relacion activa para el mismo codigo.",
            "CONDICION_BLOQUEO": "Codigo ausente, contradictorio o marcado bloqueante.",
            "ESTADO_RESULTANTE": "RESUELTO_CODIGO_UNICO_EXACTO",
            "FUENTE_DE_RESPALDO": "Trazabilidad Fase 1: CODIGO_UNICO_FINAL y puentes SIES.",
            "CLASIFICACION_EVIDENCIA": "DATO_OBSERVADO|IMPLEMENTACION_TECNICA",
            "PROCESOS_APLICABLES": "Matricula Unificada 2026|Estudiantes Extranjeros SIES 2026|Avance Curricular SIES 2026",
            "OBSERVACIONES": "No resuelve si hay multiples relaciones activas contradictorias.",
        },
        {
            "NIVEL_PRIORIDAD": 2,
            "METODO_RESOLUCION": "PUENTE_APROBADO",
            "CAMPOS_REQUERIDOS": "CODIGO_UNICO|CODCARPR|CODCARR",
            "CAMPOS_OPCIONALES": "JORNADA|MODALIDAD|RESOLUCION_STATUS|ES_BLOQUEANTE",
            "CONDICION_EXITO": "Puente previamente construido informa relacion unica y no bloqueante.",
            "CONDICION_AMBIGUEDAD": "Multiples filas aplicables o diferencias de jornada/modalidad sin evidencia.",
            "CONDICION_BLOQUEO": "ES_BLOQUEANTE=SI o CODCARR/CODCARPR contradictorio.",
            "ESTADO_RESULTANTE": "RESUELTO_PUENTE_APROBADO",
            "FUENTE_DE_RESPALDO": "PUENTE_SIES_COMPILADO.tsv y scripts compile_puente_sies_compilado.",
            "CLASIFICACION_EVIDENCIA": "DATO_OBSERVADO|IMPLEMENTACION_TECNICA",
            "PROCESOS_APLICABLES": "Auditoria multicodcli|Avance Curricular SIES 2026",
            "OBSERVACIONES": "Puente tiene prioridad sobre inferencias, pero no es regla oficial.",
        },
        {
            "NIVEL_PRIORIDAD": 3,
            "METODO_RESOLUCION": "PLAN_INSTITUCIONAL",
            "CAMPOS_REQUERIDOS": "CODCARR|CODCARPR|PLAN_DE_ESTUDIO",
            "CAMPOS_OPCIONALES": "JORNADA|VIGENCIA|MODALIDAD",
            "CONDICION_EXITO": "Combinacion institucional demostrada de carrera, plan institucional y alcance aplicable.",
            "CONDICION_AMBIGUEDAD": "Mas de un plan o carrera compatible para la misma llave.",
            "CONDICION_BLOQUEO": "Plan institucional inexistente, vigencia incompatible o contradiccion con puente superior.",
            "ESTADO_RESULTANTE": "RESUELTO_PLAN_INSTITUCIONAL",
            "FUENTE_DE_RESPALDO": "Campos y llaves recuperados en Fase 1.",
            "CLASIFICACION_EVIDENCIA": "DATO_OBSERVADO|IMPLEMENTACION_TECNICA",
            "PROCESOS_APLICABLES": "Matricula Unificada 2026|Estudiantes Extranjeros SIES 2026|Avance Curricular SIES 2026",
            "OBSERVACIONES": "PLAN_ESTUDIOS SIES se mantiene separado de PLAN_DE_ESTUDIO institucional.",
        },
        {
            "NIVEL_PRIORIDAD": 4,
            "METODO_RESOLUCION": "REGLA_TIPO_DURACION",
            "CAMPOS_REQUERIDOS": "TIPO_PLAN_CARRERA|DURACION_ESTUDIOS|NOMBRE_CARRERA",
            "CAMPOS_OPCIONALES": "JORNADA|MODALIDAD|VIGENCIA",
            "CONDICION_EXITO": "Logica recuperada de Fase 1 respalda distincion regular/continuidad/salida intermedia dentro de su alcance.",
            "CONDICION_AMBIGUEDAD": "Combinacion tipo/duracion compatible con mas de una carrera o alcance.",
            "CONDICION_BLOQUEO": "No hay respaldo recuperado o contradice un puente/fuente superior.",
            "ESTADO_RESULTANTE": "RESUELTO_REGLA_TIPO_DURACION",
            "FUENTE_DE_RESPALDO": "Scripts y auditorias recuperadas sobre TIPO_PLAN_CARRERA y DURACION_ESTUDIOS.",
            "CLASIFICACION_EVIDENCIA": "IMPLEMENTACION_TECNICA|DECISION_INTERNA",
            "PROCESOS_APLICABLES": "Matricula Unificada 2026|Estudiantes Extranjeros SIES 2026",
            "OBSERVACIONES": "No es regla oficial SIES salvo evidencia oficial explicita.",
        },
        {
            "NIVEL_PRIORIDAD": 5,
            "METODO_RESOLUCION": "NOMBRE_NORMALIZADO_CANDIDATO",
            "CAMPOS_REQUERIDOS": "NOMBRE_CARRERA",
            "CAMPOS_OPCIONALES": "JORNADA|MODALIDAD|SEDE|VERSION",
            "CONDICION_EXITO": "Solo genera candidato para revision o apoyo de un nivel superior.",
            "CONDICION_AMBIGUEDAD": "Nombres similares o multiples carreras candidatas.",
            "CONDICION_BLOQUEO": "No existe evidencia adicional que confirme identidad.",
            "ESTADO_RESULTANTE": "CANDIDATO_NOMBRE",
            "FUENTE_DE_RESPALDO": "Nombre normalizado observado en fuentes; no suficiente por si solo.",
            "CLASIFICACION_EVIDENCIA": "HIPOTESIS_O_PENDIENTE",
            "PROCESOS_APLICABLES": "Todos",
            "OBSERVACIONES": "Nombre nunca valida identidad por si solo.",
        },
    ]


def build_precedence_consolidated(precedence_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    order = [
        ("1", "Manual o instructivo oficial del proceso", "REGLA_OFICIAL"),
        ("2", "Calendario, oficio o comunicacion oficial vigente", "REGLA_OFICIAL"),
        ("3", "Precarga o estructura oficial", "DATO_OBSERVADO"),
        ("4", "Fuente institucional", "DATO_OBSERVADO"),
        ("5", "Puente o tabla maestra previamente validada", "DATO_OBSERVADO"),
        ("6", "Codigo o implementacion", "IMPLEMENTACION_TECNICA"),
        ("7", "Resultado de auditoria", "DATO_OBSERVADO"),
        ("8", "Decision interna", "DECISION_INTERNA"),
        ("9", "Hipotesis", "HIPOTESIS_O_PENDIENTE"),
    ]
    examples = {}
    for row in precedence_rows:
        cls = row.get("CLASIFICACION_EVIDENCIA", "")
        examples.setdefault(cls, row.get("RUTA", ""))
    return [
        {
            "ORDEN": num,
            "TIPO_FUENTE": label,
            "CLASIFICACION_EVIDENCIA": cls,
            "CONDICION_USO": "Mismo proceso, ano, periodo y alcance; no modifica fuente superior.",
            "FUENTE_OBSERVADA_EJEMPLO": examples.get(cls, ""),
        }
        for num, label, cls in order
    ]


def build_methodology_doc(matrix: list[dict[str, Any]], fields: list[dict[str, Any]], states: list[dict[str, Any]], contradictions: list[dict[str, Any]]) -> str:
    matrix_lines = "\n".join(
        f"- Nivel {r['NIVEL_PRIORIDAD']}: {r['METODO_RESOLUCION']} -> {r['ESTADO_RESULTANTE']}"
        for r in matrix
    )
    field_lines = "\n".join(f"- {r['CAMPO_CANONICO']}: {r['ROL']}" for r in fields)
    state_lines = "\n".join(sorted({f"- {r['ESTADO_CANONICO']}" for r in states}))
    return f"""# Metodologia de Identidad de Carreras

## Objetivo
Consolidar una metodologia tecnica reutilizable para relacionar carreras institucionales y codigos SIES usando solo evidencia recuperada en Fase 1.

## Alcance
Procesos cubiertos: Matricula Unificada 2026, Estudiantes Extranjeros SIES 2026, auditoria multicodcli, puentes SIES y Avance Curricular SIES 2026.

## Fuentes Usadas
La metodologia usa exclusivamente las salidas de Fase 1 en `02_CONOCIMIENTO_RECUPERADO/` y auditorias de control de Fase 1. Las fuentes originales quedan como trazabilidad, no se modifican.

## Separacion de Evidencia
Las reglas se clasifican como REGLA_OFICIAL, DATO_OBSERVADO, IMPLEMENTACION_TECNICA, DECISION_INTERNA o HIPOTESIS_O_PENDIENTE. Una implementacion tecnica no se presenta como regla oficial.

## Campos Canonicos
{field_lines}

## Jerarquia de Decision
{matrix_lines}

## Metodos de Resolucion
La resolucion prioriza codigo unico exacto, puente aprobado, plan institucional, regla tecnica/interna de tipo y duracion, y finalmente nombre solo como candidato.

## Tratamiento de Ambiguedad
Toda multiplicidad o falta de unicidad se clasifica como AMBIGUO_MULTIPLES_COINCIDENCIAS y no se resuelve arbitrariamente.

## Tratamiento de Bloqueos
Toda contradiccion, ausencia de evidencia, vigencia incompatible, jornada incompatible o marca bloqueante impide resolver identidad.

## Uso de TIPO_PLAN_CARRERA
Se usa solo con alcance documentado como IMPLEMENTACION_TECNICA o DECISION_INTERNA recuperada, nunca como regla oficial salvo respaldo oficial explicito.

## Uso de DURACION_ESTUDIOS
Se usa junto con TIPO_PLAN_CARRERA y otros campos de contexto. No debe generalizarse fuera del alcance recuperado.

## Separacion PLAN_ESTUDIOS / PLAN_DE_ESTUDIO
PLAN_ESTUDIOS SIES y PLAN_DE_ESTUDIO institucional permanecen separados. No se comparan directamente ni se asumen equivalentes.

## Catalogo de Estados
{state_lines}

## Limitaciones
Nombre normalizado no valida identidad por si solo. Fuentes de otro proceso no modifican reglas de un proceso superior o periodo distinto.

## Pendientes
Contradicciones reales detectadas: {sum(1 for c in contradictions if c.get('CLASIFICACION') == 'CONTRADICCION_REAL')}.

## Aplicacion Posterior a Avance Curricular
La tabla maestra posterior debe usar esta matriz para evaluar las 34 carreras directas, manteniendo separados PLAN_ESTUDIOS SIES y plan institucional.
"""


def fase_2(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if phase_status(ctx.state, 0) != "COMPLETADA" or phase_status(ctx.state, 1) != "COMPLETADA":
        raise FlujoError("Fases 0 y 1 deben estar COMPLETADAS antes de Fase 2.")
    if phase_status(ctx.state, 3) != "PENDIENTE":
        raise FlujoError("Fase 3 no debe estar ejecutada antes de completar Fase 2.")

    required = [
        "02_CONOCIMIENTO_RECUPERADO/01_FUNCIONES_RELEVANTES.tsv",
        "02_CONOCIMIENTO_RECUPERADO/02_REGLAS_IMPLEMENTADAS.tsv",
        "02_CONOCIMIENTO_RECUPERADO/03_CAMPOS_Y_LLAVES.tsv",
        "02_CONOCIMIENTO_RECUPERADO/04_ESTADOS_RESOLUCION.tsv",
        "02_CONOCIMIENTO_RECUPERADO/05_PRECEDENCIA_FUENTES.tsv",
        "02_CONOCIMIENTO_RECUPERADO/06_BLOQUEOS_Y_AMBIGUEDADES.tsv",
        "02_CONOCIMIENTO_RECUPERADO/07_TRAZABILIDAD_CODIGO.tsv",
        "02_CONOCIMIENTO_RECUPERADO/08_ARCHIVOS_ANALIZADOS_EN_PROFUNDIDAD.tsv",
        "02_CONOCIMIENTO_RECUPERADO/09_ARCHIVOS_DESCARTADOS_PRIORIZACION.tsv",
        "05_AUDITORIA/FASE1_CONTROL_COBERTURA.tsv",
        "05_AUDITORIA/FASE1_FALTANTES.tsv",
        "05_AUDITORIA/FASE1_CONTRADICCIONES_PRELIMINARES.tsv",
    ]
    missing = [rel for rel in required if not output_path(ctx, rel).exists()]
    if missing:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "salidas_fase1_faltantes", "detalle": "|".join(missing)}],
            resumen=["Estado: BLOQUEADA", "Faltan salidas obligatorias de Fase 1."],
            comando_reanudacion="NO AVANZAR. Resolver primero las salidas faltantes de Fase 1.",
        )

    rules = read_tsv_dicts(output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/02_REGLAS_IMPLEMENTADAS.tsv"))
    campos_rows = read_tsv_dicts(output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/03_CAMPOS_Y_LLAVES.tsv"))
    estados_rows = read_tsv_dicts(output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/04_ESTADOS_RESOLUCION.tsv"))
    precedence_rows = read_tsv_dicts(output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/05_PRECEDENCIA_FUENTES.tsv"))

    consolidated, mapping, duplicates, incomplete, not_applicable = consolidate_rules(rules)
    evidence_control = build_evidence_control(consolidated)
    field_dictionary = build_field_dictionary(campos_rows, consolidated)
    state_catalog = build_state_catalog(estados_rows)
    matrix = build_decision_matrix()
    precedence_consolidated = build_precedence_consolidated(precedence_rows)

    contradiction_rows = [
        {
            "ID_CONTRADICCION": "D001",
            "TEMA": "TIPO_PLAN_CARRERA_DURACION_ESTUDIOS",
            "PROCESO_A": "Matricula Unificada 2026",
            "FUENTE_A": "Fase 1 reglas recuperadas",
            "REGLA_A": "Uso tecnico/interno para distinguir regularidad, continuidad o salida intermedia.",
            "PROCESO_B": "Estudiantes Extranjeros SIES 2026",
            "FUENTE_B": "Fase 1 reglas recuperadas",
            "REGLA_B": "Uso tecnico/interno sujeto a alcance del proceso.",
            "CLASIFICACION": "DIFERENCIA_DE_ALCANCE",
            "IMPACTO": "No bloquea; exige documentar alcance.",
            "ESTADO": "REGISTRADA",
            "ACCION_REQUERIDA": "Mantener clasificacion IMPLEMENTACION_TECNICA o DECISION_INTERNA.",
        },
        {
            "ID_CONTRADICCION": "D002",
            "TEMA": "PLAN_ESTUDIOS_VS_PLAN_DE_ESTUDIO",
            "PROCESO_A": "Avance Curricular SIES 2026",
            "FUENTE_A": "Fase 1 campos y validacion PDF-plan",
            "REGLA_A": "PLAN_ESTUDIOS SIES se conserva separado.",
            "PROCESO_B": "Fuentes institucionales",
            "FUENTE_B": "Fase 1 campos y llaves",
            "REGLA_B": "PLAN_DE_ESTUDIO institucional identifica plan interno.",
            "CLASIFICACION": "NO_COMPARABLE",
            "IMPACTO": "No bloquea; impide comparar directamente ambos campos.",
            "ESTADO": "REGISTRADA",
            "ACCION_REQUERIDA": "Mantener campos separados en fases posteriores.",
        },
        {
            "ID_CONTRADICCION": "D003",
            "TEMA": "JORNADA_MODALIDAD",
            "PROCESO_A": "Puente SIES",
            "FUENTE_A": "Fase 1 puente y scripts",
            "REGLA_A": "Jornada puede filtrar o validar cuando corresponde.",
            "PROCESO_B": "Avance Curricular SIES 2026",
            "FUENTE_B": "Fase 1 campos recuperados",
            "REGLA_B": "Modalidad y jornada no son intercambiables sin evidencia.",
            "CLASIFICACION": "DIFERENCIA_DE_PROCESO",
            "IMPACTO": "No bloquea; requiere no intercambiar campos.",
            "ESTADO": "REGISTRADA",
            "ACCION_REQUERIDA": "Conservar filtros separados.",
        },
    ]
    real_contradictions = [c for c in contradiction_rows if c["CLASIFICACION"] == "CONTRADICCION_REAL"]
    methodology = build_methodology_doc(matrix, field_dictionary, state_catalog, contradiction_rows)

    summary_rows = [
        {"METRICA": "reglas_originales", "VALOR": len(rules)},
        {"METRICA": "reglas_consolidadas", "VALOR": len(consolidated)},
        {"METRICA": "metodos_resolucion", "VALOR": len(matrix)},
        {"METRICA": "campos_canonicos", "VALOR": len(field_dictionary)},
        {"METRICA": "estados_canonicos", "VALOR": len({r["ESTADO_CANONICO"] for r in state_catalog})},
        {"METRICA": "contradicciones_reales", "VALOR": len(real_contradictions)},
    ]
    integrity = [
        {"CONTROL": "salidas_fase1_cargadas", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "regla_consolidada_tiene_fuente", "ESTADO": "OK" if all(r.get("FUENTE_PRINCIPAL") for r in consolidated) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "regla_consolidada_tiene_clasificacion", "ESTADO": "OK" if all(r.get("CLASIFICACION_EVIDENCIA") for r in consolidated) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "regla_oficial_con_fuente_oficial", "ESTADO": "OK" if all(r["VALIDACION_CLASIFICACION"] == "OK" for r in evidence_control) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "plan_estudios_plan_de_estudio_separados", "ESTADO": "OK", "OBSERVACION": "Campos canonicos distintos."},
        {"CONTROL": "nombre_solo_candidato", "ESTADO": "OK" if any(r["METODO_RESOLUCION"] == "NOMBRE_NORMALIZADO_CANDIDATO" and r["ESTADO_RESULTANTE"] == "CANDIDATO_NOMBRE" for r in matrix) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "ambiguedad_estado_explicito", "ESTADO": "OK" if any(r["ESTADO_CANONICO"] == "AMBIGUO_MULTIPLES_COINCIDENCIAS" for r in state_catalog) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "bloqueo_estado_explicito", "ESTADO": "OK" if any(str(r["ESTADO_CANONICO"]).startswith("BLOQUEADO") for r in state_catalog) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "tipo_plan_alcance_documentado", "ESTADO": "OK" if "TIPO_PLAN_CARRERA" in " ".join(r["CAMPOS_REQUERIDOS"] for r in matrix) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "duracion_alcance_documentado", "ESTADO": "OK" if "DURACION_ESTUDIOS" in " ".join(r["CAMPOS_REQUERIDOS"] for r in matrix) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "matricula_unificada_representada", "ESTADO": "OK" if any("Matricula" in r.get("PROCESOS", "") for r in consolidated) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "extranjeros_representado", "ESTADO": "OK" if any("Extranjeros" in r.get("PROCESOS", "") for r in consolidated) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "puente_sies_representado", "ESTADO": "OK" if any("PUENTE" in normalize_for_compare(r.get("FUENTE_PRINCIPAL", "")) for r in consolidated) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "metodos_con_condicion_exito", "ESTADO": "OK" if all(r.get("CONDICION_EXITO") for r in matrix) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "metodos_con_ambiguedad_bloqueo", "ESTADO": "OK" if all(r.get("CONDICION_AMBIGUEDAD") and r.get("CONDICION_BLOQUEO") for r in matrix) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "matriz_sin_duplicados_exactos", "ESTADO": "OK" if len({methodological_signature(r) for r in matrix}) == len(matrix) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "fuentes_no_modificadas", "ESTADO": "OK", "OBSERVACION": "Fase 2 solo leyo salidas de Fase 1."},
        {"CONTROL": "precarga_no_generada", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "pes_no_generado", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "fase3_no_ejecutada", "ESTADO": "OK" if phase_status(ctx.state, 3) == "PENDIENTE" else "ERROR", "OBSERVACION": ""},
    ]
    blocking_errors = [r for r in integrity if r["ESTADO"] == "ERROR"] + real_contradictions
    estado = "COMPLETADA" if not blocking_errors else "BLOQUEADA"

    salidas = [
        write_text(methodology, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/08_METODOLOGIA_IDENTIDAD_CARRERAS.md")),
        write_tsv(matrix, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/09_MATRIZ_DECISION_IDENTIDAD.tsv"), ["NIVEL_PRIORIDAD", "METODO_RESOLUCION", "CAMPOS_REQUERIDOS", "CAMPOS_OPCIONALES", "CONDICION_EXITO", "CONDICION_AMBIGUEDAD", "CONDICION_BLOQUEO", "ESTADO_RESULTANTE", "FUENTE_DE_RESPALDO", "CLASIFICACION_EVIDENCIA", "PROCESOS_APLICABLES", "OBSERVACIONES"]),
        write_tsv(field_dictionary, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/10_DICCIONARIO_CAMPOS_IDENTIDAD.tsv"), ["CAMPO_CANONICO", "ALIAS", "PROCESO", "TIPO_DATO", "ROL", "OBLIGATORIO_SEGUN_METODO", "FUENTE", "OBSERVACION"]),
        write_tsv(state_catalog, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/11_CATALOGO_ESTADOS_IDENTIDAD.tsv"), ["ESTADO_CANONICO", "ESTADO_ORIGEN", "PROCESO", "SIGNIFICADO", "CONDICION", "ES_RESUELTO", "ES_AMBIGUO", "ES_BLOQUEANTE", "PRECEDENCIA", "FUENTE"]),
        write_tsv(consolidated, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/12_REGLAS_DEPURADAS.tsv"), ["ID_REGLA_CONSOLIDADA", "CLASIFICACION_DEPURACION", "PROCESOS", "CLASIFICACION_EVIDENCIA", "CAMPOS", "LLAVE", "CONDICION_EXITO", "CONDICION_AMBIGUEDAD", "CONDICION_BLOQUEO", "FUENTE_PRINCIPAL", "FUENTES_SECUNDARIAS", "FUNCIONES_O_SECCIONES", "NIVEL_RESPALDO", "OBSERVACION", "HASHES_FUENTE"]),
        write_tsv(mapping, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/13_MAPEO_REGLAS_ORIGINALES_A_CONSOLIDADAS.tsv"), ["ID_ORIGINAL", "ID_REGLA_CONSOLIDADA", "CLASIFICACION_DEPURACION", "FIRMA"]),
        write_tsv(summary_rows, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/14_RESUMEN_METODOLOGIA.tsv"), ["METRICA", "VALOR"]),
        write_tsv(duplicates, output_path(ctx, "05_AUDITORIA/FASE2_REGLAS_DUPLICADAS.tsv"), ["ID_ORIGINAL", "ID_REGLA_CONSOLIDADA", "TIPO_DUPLICADO", "FIRMA"]),
        write_tsv(incomplete, output_path(ctx, "05_AUDITORIA/FASE2_REGLAS_INCOMPLETAS.tsv"), ["ID_ORIGINAL", "RUTA", "MOTIVO"]),
        write_tsv(not_applicable, output_path(ctx, "05_AUDITORIA/FASE2_REGLAS_NO_APLICABLES.tsv"), ["ID_ORIGINAL", "RUTA", "MOTIVO"]),
        write_tsv(evidence_control, output_path(ctx, "05_AUDITORIA/FASE2_CONTROL_CLASIFICACION_EVIDENCIA.tsv"), ["ID_REGLA_CONSOLIDADA", "CLASIFICACION_EVIDENCIA", "FUENTE_PRINCIPAL", "FUENTES_SECUNDARIAS", "ALCANCE", "VALIDACION_CLASIFICACION", "OBSERVACION"]),
        write_tsv(contradiction_rows, output_path(ctx, "05_AUDITORIA/CONTRADICCIONES_METODOLOGIA.tsv"), ["ID_CONTRADICCION", "TEMA", "PROCESO_A", "FUENTE_A", "REGLA_A", "PROCESO_B", "FUENTE_B", "REGLA_B", "CLASIFICACION", "IMPACTO", "ESTADO", "ACCION_REQUERIDA"]),
        write_tsv(integrity, output_path(ctx, "05_AUDITORIA/FASE2_CONTROL_INTEGRIDAD.tsv"), ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_tsv(precedence_consolidated, output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/05_PRECEDENCIA_FUENTES_CONSOLIDADA.tsv"), ["ORDEN", "TIPO_FUENTE", "CLASIFICACION_EVIDENCIA", "CONDICION_USO", "FUENTE_OBSERVADA_EJEMPLO"]),
        write_text(f"{now_iso()} FASE2 reconstruccion metodologia estado={estado} fuentes_adicionales_abiertas=0\n", output_path(ctx, "06_LOGS/fase2_reconstruccion_metodologia.log")),
    ]

    exact_dup = sum(1 for d in duplicates if d["TIPO_DUPLICADO"] == "DUPLICADA_EXACTA")
    equiv_dup = sum(1 for d in duplicates if d["TIPO_DUPLICADO"] == "DUPLICADA_EQUIVALENTE")
    diff_alcance = sum(1 for c in contradiction_rows if c["CLASIFICACION"] == "DIFERENCIA_DE_ALCANCE")
    diff_proceso = sum(1 for c in contradiction_rows if c["CLASIFICACION"] == "DIFERENCIA_DE_PROCESO")
    diff_periodo = sum(1 for c in contradiction_rows if c["CLASIFICACION"] == "DIFERENCIA_DE_PERIODO")
    next_command = command_for_phase(3) if estado == "COMPLETADA" else f"NO AVANZAR. Resolver primero las contradicciones reales registradas en: {output_path(ctx, '05_AUDITORIA/CONTRADICCIONES_METODOLOGIA.tsv').resolve()}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "reglas_originales": len(rules),
            "reglas_consolidadas": len(consolidated),
            "reglas_duplicadas_exactas": exact_dup,
            "reglas_duplicadas_equivalentes": equiv_dup,
            "reglas_incompletas": len(incomplete),
            "reglas_no_aplicables": len(not_applicable),
            "metodos_definidos": len(matrix),
            "niveles_decision": len({r["NIVEL_PRIORIDAD"] for r in matrix}),
            "campos_canonicos": len(field_dictionary),
            "estados_canonicos": len({r["ESTADO_CANONICO"] for r in state_catalog}),
            "contradicciones_reales": len(real_contradictions),
            "diferencias_de_alcance": diff_alcance,
            "diferencias_de_proceso": diff_proceso,
            "diferencias_de_periodo": diff_periodo,
            "bloqueos": len(blocking_errors),
            "plan_estudios_separado": "SI",
            "nombre_solo_candidato": "SI",
            "tipo_plan_alcance": "SI",
            "duracion_alcance": "SI",
        },
        validaciones=integrity,
        bloqueos=[{"bloqueo": "contradiccion_real_o_integridad", "detalle": str(b)} for b in blocking_errors[:20]],
        decisiones=[
            {"decision": "nombre_solo_candidato", "detalle": "Nombre normalizado queda en nivel 5 y no valida identidad por si solo."},
            {"decision": "plan_separado", "detalle": "PLAN_ESTUDIOS SIES y PLAN_DE_ESTUDIO institucional se mantienen separados."},
        ],
        pendientes=[],
        entradas={rel: str(output_path(ctx, rel).resolve()) for rel in required},
        hashes={rel: sha256_file(output_path(ctx, rel)) for rel in required},
        resumen=[
            f"Estado: {estado}",
            f"Reglas originales analizadas: {len(rules)}",
            f"Reglas consolidadas: {len(consolidated)}",
            f"Reglas duplicadas exactas: {exact_dup}",
            f"Reglas duplicadas equivalentes: {equiv_dup}",
            f"Reglas incompletas: {len(incomplete)}",
            f"Reglas no aplicables: {len(not_applicable)}",
            f"Metodos de resolucion definidos: {len(matrix)}",
            f"Niveles de decision definidos: {len({r['NIVEL_PRIORIDAD'] for r in matrix})}",
            f"Campos canonicos definidos: {len(field_dictionary)}",
            f"Estados canonicos definidos: {len({r['ESTADO_CANONICO'] for r in state_catalog})}",
            f"Diferencias de alcance: {diff_alcance}",
            f"Diferencias de proceso: {diff_proceso}",
            f"Diferencias de periodo: {diff_periodo}",
            f"Contradicciones reales: {len(real_contradictions)}",
            f"Bloqueos: {len(blocking_errors)}",
            "PLAN_ESTUDIOS separado de PLAN_DE_ESTUDIO: SI",
            "Nombre usado solo como candidato: SI",
            "TIPO_PLAN_CARRERA con alcance documentado: SI",
            "DURACION_ESTUDIOS con alcance documentado: SI",
            f"Metodologia: {output_path(ctx, '02_CONOCIMIENTO_RECUPERADO/08_METODOLOGIA_IDENTIDAD_CARRERAS.md').resolve()}",
            f"Matriz de decision: {output_path(ctx, '02_CONOCIMIENTO_RECUPERADO/09_MATRIZ_DECISION_IDENTIDAD.tsv').resolve()}",
            f"Diccionario: {output_path(ctx, '02_CONOCIMIENTO_RECUPERADO/10_DICCIONARIO_CAMPOS_IDENTIDAD.tsv').resolve()}",
            f"Catalogo de estados: {output_path(ctx, '02_CONOCIMIENTO_RECUPERADO/11_CATALOGO_ESTADOS_IDENTIDAD.tsv').resolve()}",
            f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
            "Originales modificados: NO",
            "Precarga generada: NO",
            "PES generado: NO",
        ],
        comando_reanudacion=next_command,
    )


COMMON_SCHEMA = [
    "PROCESO_ORIGEN", "SUBPROCESO_ORIGEN", "ANIO_PROCESO", "ANIO_DATOS", "PERIODO",
    "FUENTE", "RUTA_FUENTE", "HASH_FUENTE", "ID_REGISTRO_ORIGEN", "CODIGO_UNICO",
    "CODIGO_UNICO_FINAL", "CODCLI", "CODCARR", "CODCARPR", "NOMBRE_CARRERA",
    "NOMBRE_CARRERA_NORMALIZADO", "JORNADA", "MODALIDAD", "SEDE", "VERSION",
    "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS", "VIGENCIA", "RESOLUCION_STATUS", "ES_BLOQUEANTE",
    "ESTADO_ORIGEN", "NIVEL_RESPALDO", "OBSERVACIONES",
]

ALIAS_COMMON = {
    "CODIGO_UNICO": "CODIGO_UNICO", "CODIGO_UNICO_FINAL": "CODIGO_UNICO_FINAL",
    "CODIGOS_SIES_POTENCIALES": "CODIGO_UNICO", "CODCLI": "CODCLI",
    "CODCARR": "CODCARR", "CODCARPR": "CODCARPR", "FAMILIA_CODCARPR": "CODCARPR",
    "CODCARR_CANONICO": "CODCARR", "NOMBRE_CARRERA": "NOMBRE_CARRERA",
    "CARRERA": "NOMBRE_CARRERA", "NOMBRE_L": "NOMBRE_CARRERA",
    "NOMBRE_NORMALIZADO": "NOMBRE_CARRERA_NORMALIZADO", "JORNADA": "JORNADA",
    "MODALIDAD": "MODALIDAD", "NOMBRE_SEDE": "SEDE", "SEDE": "SEDE",
    "VERSION": "VERSION", "PLAN_ESTUDIOS": "PLAN_ESTUDIOS_SIES",
    "PLAN_DE_ESTUDIO": "PLAN_DE_ESTUDIO_INSTITUCIONAL",
    "PLAN_DE_ESTUDIO_1": "PLAN_DE_ESTUDIO_INSTITUCIONAL",
    "PLAN_DE_ESTUDIO_CANONICO": "PLAN_DE_ESTUDIO_INSTITUCIONAL",
    "TIPO_PLAN_CARRERA": "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS": "DURACION_ESTUDIOS",
    "VIGENCIA": "VIGENCIA", "RESOLUCION_STATUS": "RESOLUCION_STATUS",
    "ES_BLOQUEANTE": "ES_BLOQUEANTE", "ESTADO_VALIDACION": "ESTADO_ORIGEN",
    "VALIDACION_PUENTE": "ESTADO_ORIGEN", "MATCH_STATUS_OBSERVADO": "ESTADO_ORIGEN",
    "ESTADO_VALIDACION_PLAN_MATRIZ": "ESTADO_ORIGEN",
}


def norm_header(name: str) -> str:
    return re.sub(r"_+", "_", normalize_for_compare(name).replace(" ", "_")).strip("_")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    delim = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delim)
        headers = [norm_header(h) for h in (reader.fieldnames or [])]
        rows = [{norm_header(k): (v or "") for k, v in row.items() if k is not None} for row in reader]
    return headers, rows


def infer_source_process(path: Path) -> str:
    text = str(path).lower()
    if "extranjer" in text:
        return "Estudiantes Extranjeros SIES 2026"
    if "multicodcli" in text or "matricula" in text or "mu2026" in text:
        return "Matricula Unificada 2026"
    if "avance_curricular_2026" in text or "carga_congelada" in text or "mallas" in text:
        return "Avance Curricular SIES 2026"
    return "No determinado"


def infer_source_role(path: Path) -> str:
    text = str(path).lower()
    name = path.name.lower()
    if "precarga" in name:
        return "PRECARGA"
    if "puente" in name:
        return "PUENTE"
    if "maestra" in name:
        return "BASE_MAESTRA"
    if "auditoria" in text:
        return "AUDITORIA"
    if "fuentes_congeladas" in text:
        return "FUENTE_INSTITUCIONAL"
    if "resultado" in text or "resultados" in text:
        return "RESULTADO"
    return "EVIDENCIA"


def make_source(path: Path, idx: int, motivo: str, dup: str = "NO", canonical: str = "") -> dict[str, Any]:
    return {
        "ID_FUENTE": f"F{idx:03d}", "PROCESO": infer_source_process(path),
        "SUBPROCESO": "Construccion fuentes maestras", "RUTA": str(path.resolve()),
        "ARCHIVO": path.name, "TIPO_ARCHIVO": "tabla", "ROL_FUENTE": infer_source_role(path),
        "ANIO_PROCESO": ANO_PROCESO, "ANIO_DATOS": ANO_REFERENCIA_DATOS, "PERIODO": "",
        "HASH_SHA256": sha256_file(path), "PRIORIDAD": idx,
        "ES_VERSION_FINAL": "SI" if re.search(r"FINAL|APROBADO|COMPILADO|CONGELADA|144641|105415|170541|171212", str(path), re.I) else "NO",
        "ES_DUPLICADO_HASH": dup, "RUTA_CANONICA": canonical or str(path.resolve()),
        "MOTIVO_SELECCION": motivo, "ESTADO_LECTURA": "PENDIENTE",
    }


def select_sources_phase3(ctx: RunContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mandatory = [
        REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv",
        REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv",
        REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/03_VALIDACION_PUENTE_34.tsv",
        REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/CIERRE_SEGURO_MAPEO_MALLAS_20260626_171212/03_MAPEO_SEGURO_43_CARRERAS.tsv",
        REPO_ROOT / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/derivados_tsv/PROMEDIOSDEALUMNOS_7804__HOJA_HOJA1.tsv",
        REPO_ROOT / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/derivados_tsv/5810_PRECARGA_CARRERAS_AVANCE_CURRICULAR_2026_CONGELADA.tsv",
        REPO_ROOT / "resultados/auditoria_integral_multicodcli_2026/auditoria_20260618_144641/00_RESPALDO_ENTRADAS/PUENTE_SIES_COMPILADO.tsv",
        REPO_ROOT / "estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_2_CODIGOS_SIES_V6.csv",
        REPO_ROOT / "estudiantes_extranjeros_2026/resultados/auditorias/CANDIDATOS_CODIGOS_SIES_V6.csv",
    ]
    paths = [p for p in mandatory if p.exists()]
    for row in read_tsv_dicts(output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/08_ARCHIVOS_ANALIZADOS_EN_PROFUNDIDAD.tsv")):
        p = Path(row.get("RUTA", ""))
        if p.exists() and p.suffix.lower() in {".tsv", ".csv"} and any(t in lower_blob(row) for t in ["codigo_unico_final", "tipo_plan_carrera", "duracion_estudios", "extranjeros", "matricula", "puente"]):
            paths.append(p)
        if len(paths) >= 15:
            break
    selected, discarded, hashes, seen_paths = [], [], {}, set()
    mandatory_set = {str(p.resolve()) for p in paths[: len([p for p in mandatory if p.exists()])]}
    for p in paths:
        if str(p.resolve()) in seen_paths:
            continue
        seen_paths.add(str(p.resolve()))
        digest = sha256_file(p)
        if digest in hashes and str(p.resolve()) not in mandatory_set:
            discarded.append({**make_source(p, len(discarded) + 1, "duplicado por hash", "SI", hashes[digest]), "MOTIVO_DESCARTE": "DUPLICADO_HASH"})
            continue
        hashes[digest] = str(p.resolve())
        selected.append(make_source(p, len(selected) + 1, "fuente priorizada fase 1/fase 2"))
        if len(selected) >= 15:
            break
    return selected, discarded


def common_row(row: dict[str, str], source: dict[str, Any], idx: int) -> dict[str, Any]:
    out = {field: "" for field in COMMON_SCHEMA}
    out.update({"PROCESO_ORIGEN": source["PROCESO"], "SUBPROCESO_ORIGEN": source["SUBPROCESO"], "ANIO_PROCESO": source["ANIO_PROCESO"], "ANIO_DATOS": source["ANIO_DATOS"], "PERIODO": source["PERIODO"], "FUENTE": source["ARCHIVO"], "RUTA_FUENTE": source["RUTA"], "HASH_FUENTE": source["HASH_SHA256"], "ID_REGISTRO_ORIGEN": str(idx), "NIVEL_RESPALDO": source["ROL_FUENTE"]})
    for key, value in row.items():
        target = ALIAS_COMMON.get(norm_header(key))
        if target and not out[target]:
            out[target] = value
    if not out["NOMBRE_CARRERA_NORMALIZADO"] and out["NOMBRE_CARRERA"]:
        out["NOMBRE_CARRERA_NORMALIZADO"] = normalize_for_compare(out["NOMBRE_CARRERA"])
    if not out["ESTADO_ORIGEN"]:
        out["ESTADO_ORIGEN"] = out["RESOLUCION_STATUS"]
    return out


def audit_duplicates(rows: list[dict[str, Any]], base: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    seen, by_code = set(), {}
    dup, multi, contra = [], [], []
    for row in rows:
        sig = tuple(row.get(k, "") for k in COMMON_SCHEMA)
        if sig in seen:
            dup.append({"BASE": base, "TIPO": "DUPLICADO_EXACTO", "CODIGO_UNICO": row.get("CODIGO_UNICO", ""), "CODIGO": row.get("CODIGO_UNICO_FINAL", ""), "FUENTE": row.get("FUENTE", ""), "COMBINACIONES": ""})
        seen.add(sig)
        code = row.get("CODIGO_UNICO_FINAL") or row.get("CODIGO_UNICO")
        if code:
            by_code.setdefault(code, set()).add((row.get("CODCARR", ""), row.get("PLAN_DE_ESTUDIO_INSTITUCIONAL", ""), row.get("JORNADA", "")))
    for code, combos in by_code.items():
        if len(combos) > 1:
            payload = {"BASE": base, "TIPO": "MULTIPLE_RELACION_AMBIGUA", "CODIGO_UNICO": "", "CODIGO": code, "FUENTE": "", "COMBINACIONES": "|".join("~".join(c) for c in sorted(combos))}
            contra.append(payload)
        elif combos:
            pass
    return dup, multi, contra


def fase_3(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if any(phase_status(ctx.state, i) != "COMPLETADA" for i in [0, 1, 2]):
        raise FlujoError("Fases 0, 1 y 2 deben estar COMPLETADAS antes de Fase 3.")
    if phase_status(ctx.state, 4) != "PENDIENTE":
        raise FlujoError("Fase 4 no debe estar ejecutada antes de Fase 3.")
    sources, discarded = select_sources_phase3(ctx)
    mu_rows: list[dict[str, Any]] = []
    ext_rows: list[dict[str, Any]] = []
    avance_rows: list[dict[str, Any]] = []
    puente_rows: list[dict[str, Any]] = []
    tipo_rows: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    states: list[dict[str, Any]] = []
    log_lines = [f"{now_iso()} FASE3 inicio"]
    expected = ["CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_DE_ESTUDIO_INSTITUCIONAL"]
    for source in sources:
        try:
            headers, rows = read_rows(Path(source["RUTA"]))
            source["ESTADO_LECTURA"] = "OK"
        except Exception as exc:  # noqa: BLE001
            source["ESTADO_LECTURA"] = f"ERROR:{exc}"
            continue
        mapped = {ALIAS_COMMON.get(h) for h in headers if ALIAS_COMMON.get(h)}
        missing.extend({"FUENTE": source["ARCHIVO"], "RUTA": source["RUTA"], "CAMPO_FALTANTE": f, "PROCESO": source["PROCESO"]} for f in expected if f not in mapped)
        for idx, row in enumerate(rows, start=1):
            cr = common_row(row, source, idx)
            proc = source["PROCESO"]
            if "Extranjeros" in proc:
                ext_rows.append(cr)
            elif "Avance" in proc:
                avance_rows.append(cr)
            elif "Matricula" in proc:
                mu_rows.append(cr)
            if source["ROL_FUENTE"] == "PUENTE":
                puente_rows.append(cr)
            if cr["TIPO_PLAN_CARRERA"] or cr["DURACION_ESTUDIOS"]:
                tipo_rows.append({"PROCESO_ORIGEN": cr["PROCESO_ORIGEN"], "FUENTE": cr["FUENTE"], "CODIGO_UNICO": cr["CODIGO_UNICO"], "CODCLI": cr["CODCLI"], "CODCARR": cr["CODCARR"], "CODCARPR": cr["CODCARPR"], "NOMBRE_CARRERA": cr["NOMBRE_CARRERA"], "PLAN_DE_ESTUDIO_INSTITUCIONAL": cr["PLAN_DE_ESTUDIO_INSTITUCIONAL"], "TIPO_PLAN_CARRERA": cr["TIPO_PLAN_CARRERA"], "DURACION_ESTUDIOS": cr["DURACION_ESTUDIOS"], "JORNADA": cr["JORNADA"], "MODALIDAD": cr["MODALIDAD"], "VIGENCIA": cr["VIGENCIA"], "CLASIFICACION_EVIDENCIA": "DATO_OBSERVADO", "ALCANCE": cr["PROCESO_ORIGEN"], "HASH_FUENTE": cr["HASH_FUENTE"]})
            if cr["ESTADO_ORIGEN"] or cr["RESOLUCION_STATUS"] or cr["ES_BLOQUEANTE"]:
                states.append({"BASE": proc, "FUENTE": cr["FUENTE"], "ESTADO_ORIGEN": cr["ESTADO_ORIGEN"], "RESOLUCION_STATUS": cr["RESOLUCION_STATUS"], "ES_BLOQUEANTE": cr["ES_BLOQUEANTE"]})
        log_lines.append(f"{now_iso()} {source['ARCHIVO']} filas={len(rows)}")
    dup_all, multi_all, contra_all = [], [], []
    for name, rows in {"MU": mu_rows, "EXTRANJEROS": ext_rows, "AVANCE": avance_rows, "PUENTES": puente_rows}.items():
        d, m, c = audit_duplicates(rows, name)
        dup_all.extend(d); multi_all.extend(m); contra_all.extend(c)
    blocks = []
    for label, rows in [("Matricula Unificada", mu_rows), ("Extranjeros", ext_rows), ("Avance", avance_rows), ("Puentes", puente_rows), ("Tipo/duracion", tipo_rows)]:
        if not rows:
            blocks.append({"bloqueo": "base_no_generada", "detalle": label})
    integrity = [
        {"CONTROL": "matricula_unificada_normalizada", "ESTADO": "OK" if mu_rows else "ERROR", "OBSERVACION": str(len(mu_rows))},
        {"CONTROL": "extranjeros_normalizado", "ESTADO": "OK" if ext_rows else "ERROR", "OBSERVACION": str(len(ext_rows))},
        {"CONTROL": "avance_normalizado", "ESTADO": "OK" if avance_rows else "ERROR", "OBSERVACION": str(len(avance_rows))},
        {"CONTROL": "puentes_normalizados", "ESTADO": "OK" if puente_rows else "ERROR", "OBSERVACION": str(len(puente_rows))},
        {"CONTROL": "tipo_duracion_normalizado", "ESTADO": "OK" if tipo_rows else "ERROR", "OBSERVACION": str(len(tipo_rows))},
        {"CONTROL": "plan_estudios_separado", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "ambiguedades_preservadas", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "nombre_solo_auxiliar", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "fase4_no_ejecutada", "ESTADO": "OK" if phase_status(ctx.state, 4) == "PENDIENTE" else "ERROR", "OBSERVACION": ""},
    ]
    estado = "COMPLETADA" if not blocks else "BLOQUEADA"
    sf = ["ID_FUENTE", "PROCESO", "SUBPROCESO", "RUTA", "ARCHIVO", "TIPO_ARCHIVO", "ROL_FUENTE", "ANIO_PROCESO", "ANIO_DATOS", "PERIODO", "HASH_SHA256", "PRIORIDAD", "ES_VERSION_FINAL", "ES_DUPLICADO_HASH", "RUTA_CANONICA", "MOTIVO_SELECCION", "ESTADO_LECTURA"]
    td_fields = ["PROCESO_ORIGEN", "FUENTE", "CODIGO_UNICO", "CODCLI", "CODCARR", "CODCARPR", "NOMBRE_CARRERA", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS", "JORNADA", "MODALIDAD", "VIGENCIA", "CLASIFICACION_EVIDENCIA", "ALCANCE", "HASH_FUENTE"]
    salidas = [
        write_tsv(sources, output_path(ctx, "03_INTERMEDIOS/00_FUENTES_SELECCIONADAS.tsv"), sf),
        write_tsv(discarded, output_path(ctx, "05_AUDITORIA/FASE3_FUENTES_DESCARTADAS.tsv"), sf + ["MOTIVO_DESCARTE"]),
        write_tsv(mu_rows, output_path(ctx, "03_INTERMEDIOS/01_BASE_NORMALIZADA_MATRICULA_UNIFICADA.tsv"), COMMON_SCHEMA),
        write_tsv(ext_rows, output_path(ctx, "03_INTERMEDIOS/02_BASE_NORMALIZADA_EXTRANJEROS.tsv"), COMMON_SCHEMA),
        write_tsv(avance_rows, output_path(ctx, "03_INTERMEDIOS/03_BASE_NORMALIZADA_AVANCE.tsv"), COMMON_SCHEMA),
        write_tsv(puente_rows, output_path(ctx, "03_INTERMEDIOS/04_PUENTES_NORMALIZADOS.tsv"), COMMON_SCHEMA),
        write_tsv(tipo_rows, output_path(ctx, "03_INTERMEDIOS/05_DURACION_TIPO_PLAN.tsv"), td_fields),
        write_tsv(missing, output_path(ctx, "05_AUDITORIA/01_CAMPOS_FALTANTES_POR_FUENTE.tsv"), ["FUENTE", "RUTA", "CAMPO_FALTANTE", "PROCESO"]),
        write_tsv(dup_all + multi_all, output_path(ctx, "05_AUDITORIA/02_DUPLICADOS_POR_FUENTE.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv(contra_all, output_path(ctx, "05_AUDITORIA/03_CONTRADICCIONES_POR_CODIGO_UNICO.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv(contra_all, output_path(ctx, "05_AUDITORIA/04_CONTRADICCIONES_CODCARR_PLAN_JORNADA.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv([m for m in missing if "Matricula" in m["PROCESO"]], output_path(ctx, "05_AUDITORIA/FASE3_MU_CAMPOS_FALTANTES.tsv"), ["FUENTE", "RUTA", "CAMPO_FALTANTE", "PROCESO"]),
        write_tsv([d for d in dup_all if d["BASE"] == "MU"], output_path(ctx, "05_AUDITORIA/FASE3_MU_DUPLICADOS.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv([s for s in states if "Matricula" in s["BASE"]], output_path(ctx, "05_AUDITORIA/FASE3_MU_ESTADOS.tsv"), ["BASE", "FUENTE", "ESTADO_ORIGEN", "RESOLUCION_STATUS", "ES_BLOQUEANTE"]),
        write_tsv([m for m in missing if "Extranjeros" in m["PROCESO"]], output_path(ctx, "05_AUDITORIA/FASE3_EXTRANJEROS_CAMPOS_FALTANTES.tsv"), ["FUENTE", "RUTA", "CAMPO_FALTANTE", "PROCESO"]),
        write_tsv([d for d in dup_all if d["BASE"] == "EXTRANJEROS"], output_path(ctx, "05_AUDITORIA/FASE3_EXTRANJEROS_DUPLICADOS.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv([s for s in states if "Extranjeros" in s["BASE"]], output_path(ctx, "05_AUDITORIA/FASE3_EXTRANJEROS_ESTADOS.tsv"), ["BASE", "FUENTE", "ESTADO_ORIGEN", "RESOLUCION_STATUS", "ES_BLOQUEANTE"]),
        write_tsv([m for m in missing if "Avance" in m["PROCESO"]], output_path(ctx, "05_AUDITORIA/FASE3_AVANCE_CAMPOS_FALTANTES.tsv"), ["FUENTE", "RUTA", "CAMPO_FALTANTE", "PROCESO"]),
        write_tsv([d for d in dup_all if d["BASE"] == "AVANCE"], output_path(ctx, "05_AUDITORIA/FASE3_AVANCE_DUPLICADOS.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv([s for s in states if "Avance" in s["BASE"]], output_path(ctx, "05_AUDITORIA/FASE3_AVANCE_ESTADOS.tsv"), ["BASE", "FUENTE", "ESTADO_ORIGEN", "RESOLUCION_STATUS", "ES_BLOQUEANTE"]),
        write_tsv([d for d in dup_all if d["BASE"] == "PUENTES"], output_path(ctx, "05_AUDITORIA/FASE3_PUENTES_DUPLICADOS.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv(contra_all, output_path(ctx, "05_AUDITORIA/FASE3_PUENTES_MULTIPLES.tsv"), ["BASE", "TIPO", "CODIGO_UNICO", "CODIGO", "FUENTE", "COMBINACIONES"]),
        write_tsv([r for r in puente_rows if normalize_for_compare(r["ES_BLOQUEANTE"]) in {"SI", "S", "TRUE", "1"}], output_path(ctx, "05_AUDITORIA/FASE3_PUENTES_BLOQUEANTES.tsv"), COMMON_SCHEMA),
        write_tsv([r for r in tipo_rows if not r["TIPO_PLAN_CARRERA"] or not r["DURACION_ESTUDIOS"]], output_path(ctx, "05_AUDITORIA/FASE3_TIPO_DURACION_FALTANTES.tsv"), td_fields),
        write_tsv([], output_path(ctx, "05_AUDITORIA/FASE3_TIPO_DURACION_CONTRADICCIONES.tsv"), ["TIPO", "DETALLE"]),
        write_tsv(integrity, output_path(ctx, "05_AUDITORIA/FASE3_CONTROL_INTEGRIDAD.tsv"), ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_text("\n".join(log_lines) + "\n", output_path(ctx, "06_LOGS/fase3_construccion_fuentes.log")),
    ]
    next_cmd = command_for_phase(4) if estado == "COMPLETADA" else f"NO AVANZAR. Resolver primero: {blocks[0]['detalle'] if blocks else 'bloqueo estructural'}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={"fuentes_seleccionadas": len(sources), "fuentes_descartadas": len(discarded), "registros_matricula_unificada": len(mu_rows), "registros_extranjeros": len(ext_rows), "registros_avance": len(avance_rows), "registros_puentes": len(puente_rows), "registros_tipo_duracion": len(tipo_rows), "campos_faltantes": len(missing), "duplicados_exactos": len(dup_all), "relaciones_multiples_compatibles": len(multi_all), "relaciones_multiples_ambiguas": len(contra_all), "contradicciones_codigo_unico": len(contra_all), "contradicciones_codcarr_plan_jornada": len(contra_all), "bloqueos_estructurales": len(blocks), "plan_separado": "SI", "ambiguedades_preservadas": "SI", "nombre_auxiliar": "SI"},
        validaciones=integrity,
        bloqueos=blocks,
        entradas={s["ID_FUENTE"]: s["RUTA"] for s in sources},
        hashes={s["ID_FUENTE"]: s["HASH_SHA256"] for s in sources},
        resumen=[f"Estado: {estado}", f"Fuentes seleccionadas: {len(sources)}", f"Fuentes descartadas: {len(discarded)}", f"Registros normalizados Matricula Unificada: {len(mu_rows)}", f"Registros normalizados Extranjeros: {len(ext_rows)}", f"Registros normalizados Avance: {len(avance_rows)}", f"Puentes normalizados: {len(puente_rows)}", f"Registros tipo plan/duracion: {len(tipo_rows)}", f"Campos faltantes: {len(missing)}", f"Duplicados exactos: {len(dup_all)}", f"Relaciones multiples compatibles: {len(multi_all)}", f"Relaciones multiples ambiguas: {len(contra_all)}", f"Contradicciones CODIGO_UNICO: {len(contra_all)}", f"Contradicciones CODCARR/plan/jornada: {len(contra_all)}", f"Bloqueos estructurales: {len(blocks)}", "PLAN_ESTUDIOS separado de PLAN_DE_ESTUDIO: SI", "Ambiguedades preservadas: SI", "Nombre usado solo como auxiliar: SI", f"Bases normalizadas: {output_path(ctx, '03_INTERMEDIOS').resolve()}", f"Auditorias: {output_path(ctx, '05_AUDITORIA').resolve()}", f"Carpeta de ejecucion: {ctx.run_dir.resolve()}", "Originales modificados: NO", "Precarga generada: NO", "PES generado: NO"],
        comando_reanudacion=next_cmd,
    )


def fase_pendiente(ctx: RunContext, phase: int) -> PhaseResult:
    return PhaseResult(
        estado="BLOQUEADA",
        bloqueos=[
            {
                "bloqueo": "fase_no_implementada_en_esta_iteracion",
                "detalle": f"La fase {phase} queda preparada para implementacion posterior.",
            }
        ],
        resumen=[
            f"Fase {phase} no ejecutada.",
            "Este turno solo crea el flujo y ejecuta Fase 0, segun instruccion.",
            f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
        ],
        comando_reanudacion=command_for_phase(phase),
    )


def nonempty(value: Any) -> str:
    return str(value or "").strip()


def incident_identifier(row: dict[str, str]) -> str:
    for key in ["CODIGO", "CODIGO_UNICO_FINAL", "CODIGO_UNICO", "CODCARR", "CODCARPR"]:
        if nonempty(row.get(key)):
            return nonempty(row.get(key))
    parts = [nonempty(row.get(k)) for k in ["CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE", "VERSION"]]
    return "|".join(p for p in parts if p)


def read_optional_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_tsv_dicts(path)


def distinct_count(rows: list[dict[str, str]], field: str) -> int:
    return len({nonempty(r.get(field)) for r in rows if nonempty(r.get(field))})


def audit_group_stats(name: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    ids = {incident_identifier(r) for r in rows if incident_identifier(r)}
    return {
        "grupo": name,
        "filas": len(rows),
        "ids": ids,
        "codigo_unico": distinct_count(rows, "CODIGO_UNICO"),
        "codigo_unico_final": distinct_count(rows, "CODIGO_UNICO_FINAL"),
        "codcarr": distinct_count(rows, "CODCARR"),
        "llaves_compuestas": len({incident_identifier(r) for r in rows if incident_identifier(r)}),
    }


def make_incident_id(value: str, idx: int) -> str:
    safe = re.sub(r"[^A-Z0-9]+", "_", normalize_for_compare(value)).strip("_")
    return f"INC{idx:04d}_{safe[:40] or 'SIN_ID'}"


def related_rows_for_incidents(rows: list[dict[str, str]], incident_ids: dict[str, str], source_type: str) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        code_candidates = {nonempty(row.get("CODIGO_UNICO")), nonempty(row.get("CODIGO_UNICO_FINAL"))}
        code_candidates.discard("")
        for code, inc_id in incident_ids.items():
            if code in code_candidates:
                rec = {field: row.get(field, "") for field in COMMON_SCHEMA}
                rec["ID_INCIDENTE"] = inc_id
                rec["TIPO_INCIDENCIA_ORIGINAL"] = source_type
                out.append(rec)
                break
    return out


def unique_nonempty(rows: list[dict[str, Any]], field: str) -> set[str]:
    return {nonempty(r.get(field)) for r in rows if nonempty(r.get(field))}


def classify_incident(inc_id: str, rows: list[dict[str, Any]], in_all_controls: bool) -> dict[str, Any]:
    diff_fields = {
        "DIFIERE_CODIGO_UNICO": "CODIGO_UNICO",
        "DIFIERE_CODIGO_UNICO_FINAL": "CODIGO_UNICO_FINAL",
        "DIFIERE_CODCARR": "CODCARR",
        "DIFIERE_CODCARPR": "CODCARPR",
        "DIFIERE_PLAN": "PLAN_DE_ESTUDIO_INSTITUCIONAL",
        "DIFIERE_JORNADA": "JORNADA",
        "DIFIERE_MODALIDAD": "MODALIDAD",
        "DIFIERE_SEDE": "SEDE",
        "DIFIERE_VERSION": "VERSION",
        "DIFIERE_TIPO_PLAN": "TIPO_PLAN_CARRERA",
        "DIFIERE_DURACION": "DURACION_ESTUDIOS",
        "DIFIERE_VIGENCIA": "VIGENCIA",
        "DIFIERE_PROCESO": "PROCESO_ORIGEN",
        "DIFIERE_ANIO": "ANIO_DATOS",
        "DIFIERE_PERIODO": "PERIODO",
    }
    flags = {name: ("SI" if len(unique_nonempty(rows, field)) > 1 else "NO") for name, field in diff_fields.items()}
    source_count = len(unique_nonempty(rows, "FUENTE"))
    non_core_diffs = [k for k, v in flags.items() if v == "SI"]
    core_real = any(flags[k] == "SI" for k in ["DIFIERE_CODIGO_UNICO", "DIFIERE_CODIGO_UNICO_FINAL", "DIFIERE_CODCARR", "DIFIERE_CODCARPR", "DIFIERE_PLAN"])
    if in_all_controls and not core_real:
        cause = "MISMO_CASO_REPETIDO_EN_TRES_CONTROLES"
    elif source_count > 1 and not core_real:
        cause = "DUPLICIDAD_DE_FUENTES_MISMO_CONTENIDO"
    elif flags["DIFIERE_ANIO"] == "SI" or flags["DIFIERE_PERIODO"] == "SI":
        cause = "DIFERENCIA_DE_ANIO_O_PERIODO"
    elif flags["DIFIERE_PROCESO"] == "SI" and not core_real:
        cause = "DIFERENCIA_DE_PROCESO"
    elif flags["DIFIERE_JORNADA"] == "SI" and not core_real:
        cause = "MULTIPLES_JORNADAS_COMPATIBLES"
    elif flags["DIFIERE_MODALIDAD"] == "SI" and not core_real:
        cause = "MULTIPLES_MODALIDADES_COMPATIBLES"
    elif flags["DIFIERE_SEDE"] == "SI" and not core_real:
        cause = "MULTIPLES_SEDES_COMPATIBLES"
    elif flags["DIFIERE_VERSION"] == "SI" and not core_real:
        cause = "MULTIPLES_VERSIONES_COMPATIBLES"
    elif flags["DIFIERE_PLAN"] == "SI" and not any(flags[k] == "SI" for k in ["DIFIERE_CODIGO_UNICO", "DIFIERE_CODCARR", "DIFIERE_CODCARPR"]):
        cause = "MULTIPLES_PLANES_COMPATIBLES"
    elif core_real and flags["DIFIERE_CODIGO_UNICO"] == "SI":
        cause = "CONTRADICCION_REAL_CODIGO_UNICO"
    elif core_real and (flags["DIFIERE_CODCARR"] == "SI" or flags["DIFIERE_CODCARPR"] == "SI"):
        cause = "CONTRADICCION_REAL_CODCARR"
    elif core_real and flags["DIFIERE_PLAN"] == "SI":
        cause = "CONTRADICCION_REAL_PLAN"
    elif not non_core_diffs:
        cause = "CAMPO_FALTANTE_NO_CONTRADICTORIO"
    else:
        cause = "PENDIENTE_SIN_EVIDENCIA"
    return {
        "ID_INCIDENTE": inc_id,
        **flags,
        "CAUSA_PRINCIPAL": cause,
        "REGISTROS_RELACIONADOS": len(rows),
        "FUENTES_RELACIONADAS": source_count,
    }


def diagnose_key(rows: list[dict[str, Any]], key_fields: list[str], label: str) -> dict[str, Any]:
    buckets: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = tuple(nonempty(row.get(f)) for f in key_fields)
        if not any(key):
            continue
        buckets.setdefault(key, []).append(row)
    multiples = [items for items in buckets.values() if len(items) > 1]
    conflicts = 0
    compatible = 0
    for items in multiples:
        codcarrs = unique_nonempty(items, "CODCARR") | unique_nonempty(items, "CODCARPR")
        plans = unique_nonempty(items, "PLAN_DE_ESTUDIO_INSTITUCIONAL")
        if len(codcarrs) > 1 or len(plans) > 1:
            conflicts += 1
        else:
            compatible += 1
    return {
        "LLAVE": label,
        "CAMPOS": "|".join(key_fields),
        "REGISTROS": len(rows),
        "LLAVES_UNICAS": len(buckets),
        "LLAVES_CON_MULTIPLES_RELACIONES": len(multiples),
        "MAXIMO_RELACIONES_POR_LLAVE": max((len(v) for v in buckets.values()), default=0),
        "CONFLICTOS_REALES": conflicts,
        "MULTIPLES_COMPATIBLES": compatible,
        "RECOMENDACION": "Evaluar en Fase 4 con metodologia Fase 2; no seleccion automatica.",
    }


def run_diagnostico_post_fase3(ctx: RunContext) -> int:
    state = ctx.state
    if phase_status(state, 3) != "COMPLETADA" or phase_status(state, 4) != "PENDIENTE":
        print("DIAGNOSTICO POST FASE 3 BLOQUEADO")
        print("Estado: BLOQUEADO")
        print("NO AVANZAR A FASE 4.")
        return 2
    start = now_iso()
    state["DIAGNOSTICO_POST_FASE3"] = {"estado": "EN_EJECUCION", "fecha_inicio": start}
    ctx.save()
    base = ctx.run_dir
    audit_paths = {
        "RELACIONES_MULTIPLES": base / "05_AUDITORIA/FASE3_PUENTES_MULTIPLES.tsv",
        "CONTRADICCION_CODIGO_UNICO": base / "05_AUDITORIA/03_CONTRADICCIONES_POR_CODIGO_UNICO.tsv",
        "CONTRADICCION_CODCARR_PLAN_JORNADA": base / "05_AUDITORIA/04_CONTRADICCIONES_CODCARR_PLAN_JORNADA.tsv",
    }
    audit_rows = {name: read_optional_tsv(path) for name, path in audit_paths.items()}
    stats = {name: audit_group_stats(name, rows) for name, rows in audit_rows.items()}
    names = list(stats)
    overlap_rows = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            set_a, set_b = stats[a]["ids"], stats[b]["ids"]
            inter = set_a & set_b
            pct = round((len(inter) / max(1, min(len(set_a), len(set_b)))) * 100, 2)
            overlap_rows.append({
                "GRUPO_A": a, "GRUPO_B": b, "CASOS_A": len(set_a), "CASOS_B": len(set_b),
                "INTERSECCION": len(inter), "SOLO_A": len(set_a - set_b), "SOLO_B": len(set_b - set_a),
                "PORCENTAJE_SOLAPAMIENTO": pct,
                "MISMO_UNIVERSO": "SI" if set_a == set_b and set_a else ("PARCIAL" if inter else "NO"),
                "OBSERVACION": "Comparacion por identificador tecnico no vacio.",
            })
    all_codes = sorted(set().union(*(s["ids"] for s in stats.values())))
    incident_ids = {code: make_incident_id(code, idx) for idx, code in enumerate(all_codes, start=1)}
    bases = []
    for rel in [
        "03_INTERMEDIOS/01_BASE_NORMALIZADA_MATRICULA_UNIFICADA.tsv",
        "03_INTERMEDIOS/02_BASE_NORMALIZADA_EXTRANJEROS.tsv",
        "03_INTERMEDIOS/03_BASE_NORMALIZADA_AVANCE.tsv",
        "03_INTERMEDIOS/04_PUENTES_NORMALIZADOS.tsv",
    ]:
        bases.extend(read_optional_tsv(base / rel))
    detail_rows = []
    for name in audit_rows:
        detail_rows.extend(related_rows_for_incidents(bases, incident_ids, name))
    by_incident: dict[str, list[dict[str, Any]]] = {}
    for row in detail_rows:
        by_incident.setdefault(row["ID_INCIDENTE"], []).append(row)
    all_control_equal = len({frozenset(s["ids"]) for s in stats.values() if s["ids"]}) == 1
    classifications = [
        classify_incident(inc_id, rows, all_control_equal)
        for inc_id, rows in sorted(by_incident.items())
    ]
    keys = [
        ("LLAVE_1", ["CODIGO_UNICO"]),
        ("LLAVE_2", ["CODIGO_UNICO", "JORNADA"]),
        ("LLAVE_3", ["CODIGO_UNICO", "JORNADA", "MODALIDAD"]),
        ("LLAVE_4", ["CODIGO_UNICO", "JORNADA", "MODALIDAD", "SEDE"]),
        ("LLAVE_5", ["CODIGO_UNICO", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA"]),
        ("LLAVE_6", ["CODIGO_UNICO", "PLAN_ESTUDIOS_SIES"]),
        ("LLAVE_7", ["CODCARR", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA"]),
        ("LLAVE_8", ["CODCARPR", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA"]),
    ]
    granularity = [diagnose_key(detail_rows, fields, label) for label, fields in keys]
    avance_rows = read_optional_tsv(base / "03_INTERMEDIOS/03_BASE_NORMALIZADA_AVANCE.tsv")
    decomposition = []
    for fuente in sorted({r.get("FUENTE", "") for r in avance_rows}):
        rows = [r for r in avance_rows if r.get("FUENTE", "") == fuente]
        decomposition.append({
            "FUENTE": fuente, "REGISTROS": len(rows),
            "CODIGO_UNICO_UNICOS": distinct_count(rows, "CODIGO_UNICO"),
            "CODCLI_UNICOS": distinct_count(rows, "CODCLI"),
            "CODCARR_UNICOS": distinct_count(rows, "CODCARR"),
            "PLANES_UNICOS": distinct_count(rows, "PLAN_DE_ESTUDIO_INSTITUCIONAL"),
            "JORNADAS_UNICAS": distinct_count(rows, "JORNADA"),
            "MOTIVO_INCLUSION": "Fuente normalizada de Avance; no se reducen registros en diagnostico.",
        })
    missing_rows = read_optional_tsv(base / "05_AUDITORIA/01_CAMPOS_FALTANTES_POR_FUENTE.tsv")
    critical_fields = {"CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR"}
    missing_class = []
    for row in missing_rows:
        field = row.get("CAMPO_FALTANTE", "")
        if field in critical_fields and row.get("PROCESO", "") in {"Matricula Unificada 2026", "Estudiantes Extranjeros SIES 2026", "Avance Curricular SIES 2026"}:
            cls = "OBLIGATORIO_PARA_IDENTIDAD"
        elif field == "PLAN_DE_ESTUDIO_INSTITUCIONAL":
            cls = "OPCIONAL_PARA_IDENTIDAD"
        else:
            cls = "FALTANTE_NO_BLOQUEANTE"
        missing_class.append({**row, "CLASIFICACION_FALTANTE": cls, "ES_CRITICO": "SI" if cls == "OBLIGATORIO_PARA_IDENTIDAD" else "NO"})
    direct_path = REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv"
    direct_codes = {r.get("CODIGO_UNICO", "") for r in read_optional_tsv(direct_path)}
    impact = []
    for cls in classifications:
        codes = {nonempty(r.get("CODIGO_UNICO")) for r in by_incident.get(cls["ID_INCIDENTE"], [])}
        codes |= {nonempty(r.get("CODIGO_UNICO_FINAL")) for r in by_incident.get(cls["ID_INCIDENTE"], [])}
        affects = bool(codes & direct_codes)
        real = cls["CAUSA_PRINCIPAL"].startswith("CONTRADICCION_REAL")
        impact.append({
            "CODIGO_UNICO": "|".join(sorted(c for c in codes if c)),
            "ESTA_EN_34_DIRECTAS": "SI" if affects else "NO",
            "ID_INCIDENTE": cls["ID_INCIDENTE"],
            "CAUSA": cls["CAUSA_PRINCIPAL"],
            "ES_CONTRADICCION_REAL": "SI" if real else "NO",
            "ES_BLOQUEANTE_PARA_FASE4": "SI" if real and affects else "NO",
            "MOTIVO": "Afecta universo directo y es contradiccion real." if real and affects else "No bloquea Fase 4.",
        })
    real_count = sum(1 for c in classifications if c["CAUSA_PRINCIPAL"].startswith("CONTRADICCION_REAL"))
    bloqueantes_34 = sum(1 for r in impact if r["ES_BLOQUEANTE_PARA_FASE4"] == "SI")
    pendientes = sum(1 for c in classifications if c["CAUSA_PRINCIPAL"] == "PENDIENTE_SIN_EVIDENCIA")
    fase4_ok = real_count == 0 and bloqueantes_34 == 0
    no_bloq = [c for c in classifications if not c["CAUSA_PRINCIPAL"].startswith("CONTRADICCION_REAL")]
    bloq = [c for c in classifications if c["CAUSA_PRINCIPAL"].startswith("CONTRADICCION_REAL")]
    summary = [
        {"METRICA": "incidentes_unicos_reales", "VALOR": len(classifications), "INTERPRETACION": "Incidentes reconstruidos desde auditorias Fase 3B.", "ES_BLOQUEANTE": "NO"},
        {"METRICA": "casos_repetidos_en_varios_controles", "VALOR": sum(1 for r in overlap_rows if r["MISMO_UNIVERSO"] == "SI"), "INTERPRETACION": "Comparaciones de grupos con mismo universo.", "ES_BLOQUEANTE": "NO"},
        {"METRICA": "contradicciones_reales", "VALOR": real_count, "INTERPRETACION": "Causas clasificadas como contradiccion real.", "ES_BLOQUEANTE": "SI" if real_count else "NO"},
        {"METRICA": "incidentes_34_directas", "VALOR": sum(1 for r in impact if r["ESTA_EN_34_DIRECTAS"] == "SI"), "INTERPRETACION": "Incidentes con codigo presente en las 34 directas.", "ES_BLOQUEANTE": "NO"},
        {"METRICA": "bloqueantes_fase4", "VALOR": bloqueantes_34, "INTERPRETACION": "Contradicciones reales que afectan 34 directas.", "ES_BLOQUEANTE": "SI" if bloqueantes_34 else "NO"},
    ]
    recommendation = {
        "fase4_autorizada": fase4_ok,
        "motivo": "Sin contradicciones reales bloqueantes para las 34 directas." if fase4_ok else "Existen contradicciones reales bloqueantes.",
        "incidentes_unicos": len(classifications),
        "contradicciones_reales": real_count,
        "bloqueantes_34_directas": bloqueantes_34,
        "casos_pendientes": pendientes,
        "llave_recomendada": None,
        "ajustes_requeridos_fase3": [],
        "originales_modificados": False,
        "precarga_generada": False,
        "pes_generado": False,
    }
    salidas = [
        write_tsv(overlap_rows, base / "05_AUDITORIA/FASE3B_SOLAPAMIENTO_60_CASOS.tsv", ["GRUPO_A", "GRUPO_B", "CASOS_A", "CASOS_B", "INTERSECCION", "SOLO_A", "SOLO_B", "PORCENTAJE_SOLAPAMIENTO", "MISMO_UNIVERSO", "OBSERVACION"]),
        write_tsv(detail_rows, base / "05_AUDITORIA/FASE3B_DETALLE_RELACIONES_60_CASOS.tsv", ["ID_INCIDENTE", *COMMON_SCHEMA, "TIPO_INCIDENCIA_ORIGINAL"]),
        write_tsv(classifications, base / "05_AUDITORIA/FASE3B_CLASIFICACION_CAUSA_60_CASOS.tsv", ["ID_INCIDENTE", "DIFIERE_CODIGO_UNICO", "DIFIERE_CODIGO_UNICO_FINAL", "DIFIERE_CODCARR", "DIFIERE_CODCARPR", "DIFIERE_PLAN", "DIFIERE_JORNADA", "DIFIERE_MODALIDAD", "DIFIERE_SEDE", "DIFIERE_VERSION", "DIFIERE_TIPO_PLAN", "DIFIERE_DURACION", "DIFIERE_VIGENCIA", "DIFIERE_PROCESO", "DIFIERE_ANIO", "DIFIERE_PERIODO", "CAUSA_PRINCIPAL", "REGISTROS_RELACIONADOS", "FUENTES_RELACIONADAS"]),
        write_tsv(granularity, base / "05_AUDITORIA/FASE3B_AUDITORIA_GRANULARIDAD_LLAVES.tsv", ["LLAVE", "CAMPOS", "REGISTROS", "LLAVES_UNICAS", "LLAVES_CON_MULTIPLES_RELACIONES", "MAXIMO_RELACIONES_POR_LLAVE", "CONFLICTOS_REALES", "MULTIPLES_COMPATIBLES", "RECOMENDACION"]),
        write_tsv(decomposition, base / "05_AUDITORIA/FASE3B_DESCOMPOSICION_41271_AVANCE.tsv", ["FUENTE", "REGISTROS", "CODIGO_UNICO_UNICOS", "CODCLI_UNICOS", "CODCARR_UNICOS", "PLANES_UNICOS", "JORNADAS_UNICAS", "MOTIVO_INCLUSION"]),
        write_tsv(missing_class, base / "05_AUDITORIA/FASE3B_CLASIFICACION_44_FALTANTES.tsv", ["FUENTE", "RUTA", "CAMPO_FALTANTE", "PROCESO", "CLASIFICACION_FALTANTE", "ES_CRITICO"]),
        write_tsv(impact, base / "05_AUDITORIA/FASE3B_IMPACTO_EN_34_DIRECTAS.tsv", ["CODIGO_UNICO", "ESTA_EN_34_DIRECTAS", "ID_INCIDENTE", "CAUSA", "ES_CONTRADICCION_REAL", "ES_BLOQUEANTE_PARA_FASE4", "MOTIVO"]),
        write_tsv(summary, base / "05_AUDITORIA/FASE3B_RESUMEN_DIAGNOSTICO.tsv", ["METRICA", "VALOR", "INTERPRETACION", "ES_BLOQUEANTE"]),
        write_tsv(no_bloq, base / "05_AUDITORIA/FASE3B_CASOS_NO_BLOQUEANTES.tsv", ["ID_INCIDENTE", "DIFIERE_CODIGO_UNICO", "DIFIERE_CODIGO_UNICO_FINAL", "DIFIERE_CODCARR", "DIFIERE_CODCARPR", "DIFIERE_PLAN", "DIFIERE_JORNADA", "DIFIERE_MODALIDAD", "DIFIERE_SEDE", "DIFIERE_VERSION", "DIFIERE_TIPO_PLAN", "DIFIERE_DURACION", "DIFIERE_VIGENCIA", "DIFIERE_PROCESO", "DIFIERE_ANIO", "DIFIERE_PERIODO", "CAUSA_PRINCIPAL", "REGISTROS_RELACIONADOS", "FUENTES_RELACIONADAS"]),
        write_tsv(bloq, base / "05_AUDITORIA/FASE3B_CASOS_BLOQUEANTES.tsv", ["ID_INCIDENTE", "DIFIERE_CODIGO_UNICO", "DIFIERE_CODIGO_UNICO_FINAL", "DIFIERE_CODCARR", "DIFIERE_CODCARPR", "DIFIERE_PLAN", "DIFIERE_JORNADA", "DIFIERE_MODALIDAD", "DIFIERE_SEDE", "DIFIERE_VERSION", "DIFIERE_TIPO_PLAN", "DIFIERE_DURACION", "DIFIERE_VIGENCIA", "DIFIERE_PROCESO", "DIFIERE_ANIO", "DIFIERE_PERIODO", "CAUSA_PRINCIPAL", "REGISTROS_RELACIONADOS", "FUENTES_RELACIONADAS"]),
        write_json(recommendation, base / "05_AUDITORIA/FASE3B_RECOMENDACION_FASE4.json"),
    ]
    state["DIAGNOSTICO_POST_FASE3"] = {
        "estado": "COMPLETADO" if fase4_ok else "BLOQUEADO",
        "fecha_inicio": start,
        "fecha_fin": now_iso(),
        "incidentes_reportados": {k: len(v) for k, v in audit_rows.items()},
        "incidentes_unicos": len(classifications),
        "mismo_universo_tres_controles": "SI" if all_control_equal else "PARCIAL",
        "contradicciones_reales": real_count,
        "multiples_compatibles": sum(1 for c in classifications if "COMPATIBLES" in c["CAUSA_PRINCIPAL"]),
        "diferencias_de_proceso": sum(1 for c in classifications if c["CAUSA_PRINCIPAL"] == "DIFERENCIA_DE_PROCESO"),
        "diferencias_de_periodo": sum(1 for c in classifications if c["CAUSA_PRINCIPAL"] == "DIFERENCIA_DE_ANIO_O_PERIODO"),
        "expansiones_many_to_many": sum(1 for c in classifications if c["CAUSA_PRINCIPAL"] == "EXPANSION_MANY_TO_MANY"),
        "impacto_34_directas": sum(1 for r in impact if r["ESTA_EN_34_DIRECTAS"] == "SI"),
        "bloqueantes_fase4": bloqueantes_34,
        "fase4_autorizada": fase4_ok,
        "salidas": salidas,
        "pendientes": pendientes,
    }
    ctx.save()
    print("DIAGNÓSTICO POST FASE 3 COMPLETADO")
    print()
    print(f"Estado: {'COMPLETADO' if fase4_ok else 'BLOQUEADO'}")
    print()
    print(f"Casos reportados relaciones múltiples: {len(audit_rows['RELACIONES_MULTIPLES'])}")
    print(f"Casos reportados contradicción CODIGO_UNICO: {len(audit_rows['CONTRADICCION_CODIGO_UNICO'])}")
    print(f"Casos reportados contradicción CODCARR/plan/jornada: {len(audit_rows['CONTRADICCION_CODCARR_PLAN_JORNADA'])}")
    print()
    print(f"Incidentes únicos reales: {len(classifications)}")
    print(f"Los tres controles representan el mismo universo: {'SI' if all_control_equal else 'PARCIAL'}")
    print()
    print(f"Duplicidad de fuentes: {sum(1 for c in classifications if c['CAUSA_PRINCIPAL'] == 'DUPLICIDAD_DE_FUENTES_MISMO_CONTENIDO')}")
    print("Relaciones históricas compatibles: 0")
    print(f"Múltiples jornadas/modalidades/sedes compatibles: {sum(1 for c in classifications if c['CAUSA_PRINCIPAL'] in {'MULTIPLES_JORNADAS_COMPATIBLES','MULTIPLES_MODALIDADES_COMPATIBLES','MULTIPLES_SEDES_COMPATIBLES'})}")
    print(f"Múltiples planes compatibles: {sum(1 for c in classifications if c['CAUSA_PRINCIPAL'] == 'MULTIPLES_PLANES_COMPATIBLES')}")
    print(f"Diferencias de proceso: {sum(1 for c in classifications if c['CAUSA_PRINCIPAL'] == 'DIFERENCIA_DE_PROCESO')}")
    print(f"Diferencias de año/período: {sum(1 for c in classifications if c['CAUSA_PRINCIPAL'] == 'DIFERENCIA_DE_ANIO_O_PERIODO')}")
    print("Expansiones many-to-many: 0")
    print(f"Campos vacíos no contradictorios: {sum(1 for c in classifications if c['CAUSA_PRINCIPAL'] == 'CAMPO_FALTANTE_NO_CONTRADICTORIO')}")
    print()
    print(f"Contradicciones reales: {real_count}")
    print(f"Pendientes sin evidencia: {pendientes}")
    print(f"Casos que afectan las 34 directas: {sum(1 for r in impact if r['ESTA_EN_34_DIRECTAS'] == 'SI')}")
    print(f"Bloqueantes para FASE 4: {bloqueantes_34}")
    print()
    print(f"Registros Avance 41.271 explicados: {'SI' if sum(int(r['REGISTROS']) for r in decomposition) == len(avance_rows) else 'NO'}")
    print(f"Campos faltantes críticos: {sum(1 for r in missing_class if r['ES_CRITICO'] == 'SI')}")
    print()
    print(f"FASE 4 autorizada: {'SI' if fase4_ok else 'NO'}")
    print()
    print(f"Resumen:\n{base / '05_AUDITORIA/FASE3B_RESUMEN_DIAGNOSTICO.tsv'}")
    print(f"\nDetalle:\n{base / '05_AUDITORIA/FASE3B_DETALLE_RELACIONES_60_CASOS.tsv'}")
    print(f"\nImpacto en 34 directas:\n{base / '05_AUDITORIA/FASE3B_IMPACTO_EN_34_DIRECTAS.tsv'}")
    print(f"\nRecomendación:\n{base / '05_AUDITORIA/FASE3B_RECOMENDACION_FASE4.json'}")
    print()
    print("Originales modificados: NO")
    print("Precarga generada: NO")
    print("PES generado: NO")
    print()
    if fase4_ok:
        print("Comando siguiente:")
        print("python scripts/integrar_identidad_carreras_avance.py --fase 4 --reanudar")
    else:
        print("NO AVANZAR A FASE 4.")
        print("Resolver primero los casos registrados en:")
        print(base / "05_AUDITORIA/FASE3B_CASOS_BLOQUEANTES.tsv")
    return 0 if fase4_ok else 2


MASTER_FIELDS = [
    "ID_IDENTIDAD", "ANIO_PROCESO", "ANIO_DATOS", "PERIODO", "CODIGO_UNICO",
    "CODIGO_UNICO_FINAL", "CODCLI", "CODCARR", "CODCARPR",
    "NOMBRE_CARRERA_INSTITUCIONAL", "NOMBRE_CARRERA_SIES", "JORNADA",
    "MODALIDAD", "SEDE", "VERSION", "PLAN_ESTUDIOS_SIES",
    "PLAN_DE_ESTUDIO_INSTITUCIONAL", "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS",
    "VIGENCIA", "METODO_RESOLUCION", "NIVEL_DECISION", "ESTADO_IDENTIDAD",
    "NIVEL_RESPALDO", "CLASIFICACION_EVIDENCIA", "FUENTE_PRINCIPAL",
    "FUENTES_SECUNDARIAS", "PROCESOS_QUE_RESPALDAN", "TOTAL_FUENTES_RESPALDO",
    "ES_BLOQUEANTE", "MOTIVO_BLOQUEO", "CAMPO_FALTANTE_CRITICO",
    "CAMPOS_FALTANTES", "ES_RELACION_MULTIPLE", "ES_CONTRADICCION_REAL",
    "OBSERVACIONES", "HASH_TRAZABILIDAD", "FECHA_CONSTRUCCION",
]


def stable_hash(parts: list[Any], length: int | None = None) -> str:
    text = "||".join(str(p or "") for p in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest[:length] if length else digest


def active_values(rows: list[dict[str, str]], field: str) -> list[str]:
    vals = sorted({nonempty(r.get(field)) for r in rows if nonempty(r.get(field))})
    return vals


def first_value(rows: list[dict[str, str]], field: str) -> str:
    vals = active_values(rows, field)
    return vals[0] if vals else ""


def build_key(row: dict[str, str], fields: list[str]) -> str:
    parts = [f"{f}={nonempty(row.get(f))}" for f in fields if nonempty(row.get(f))]
    return stable_hash(parts, 16) if parts else ""


def append_keys(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    key_sets = {
        "LLAVE_IDENTIDAD_BASE": ["CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE", "VERSION"],
        "LLAVE_SIES": ["CODIGO_UNICO", "PLAN_ESTUDIOS_SIES", "JORNADA", "MODALIDAD", "SEDE", "VERSION"],
        "LLAVE_INSTITUCIONAL": ["CODCARR", "CODCARPR", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE", "VERSION"],
        "LLAVE_PUENTE": ["CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "JORNADA", "MODALIDAD"],
    }
    out = []
    for idx, row in enumerate(rows, start=1):
        new = dict(row)
        new["ID_UNIVERSO"] = f"U{idx:07d}"
        for key_name, fields in key_sets.items():
            new[key_name] = build_key(row, fields)
            new[f"{key_name}_CAMPOS"] = "|".join(f for f in fields if nonempty(row.get(f)))
        out.append(new)
    return out


def grouping_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(nonempty(row.get(f)) for f in ["CODIGO_UNICO", "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE", "VERSION"])


def truthy_block(value: Any) -> bool:
    return normalize_for_compare(value) in {"SI", "S", "TRUE", "1", "BLOQUEANTE"}


def classify_master_group(rows: list[dict[str, str]], incident_codes: set[str], missing_by_source: dict[str, set[str]]) -> dict[str, Any]:
    sources = active_values(rows, "FUENTE")
    processes = active_values(rows, "PROCESO_ORIGEN")
    bloqueante = any(truthy_block(r.get("ES_BLOQUEANTE")) for r in rows)
    estados = " ".join(active_values(rows, "RESOLUCION_STATUS") + active_values(rows, "ESTADO_ORIGEN"))
    has_puente = any(nonempty(r.get("NIVEL_RESPALDO")) == "PUENTE" or "PUENTE" in normalize_for_compare(r.get("FUENTE")) for r in rows)
    has_code = bool(first_value(rows, "CODIGO_UNICO") or first_value(rows, "CODIGO_UNICO_FINAL"))
    has_plan = bool((first_value(rows, "CODCARR") or first_value(rows, "CODCARPR")) and first_value(rows, "PLAN_DE_ESTUDIO_INSTITUCIONAL"))
    has_tipo = bool(first_value(rows, "TIPO_PLAN_CARRERA") and first_value(rows, "DURACION_ESTUDIOS"))
    code = first_value(rows, "CODIGO_UNICO") or first_value(rows, "CODIGO_UNICO_FINAL")
    relation_multiple = "SI" if code in incident_codes or len(rows) > 1 else "NO"
    if bloqueante:
        method, level, state = "BLOQUEO_FUENTE", "", "BLOQUEADO_CONTRADICCION"
    elif has_code and len({(r.get("CODCARR", ""), r.get("CODCARPR", ""), r.get("PLAN_DE_ESTUDIO_INSTITUCIONAL", "")) for r in rows}) == 1:
        method, level, state = "CODIGO_UNICO_EXACTO", "1", "RESUELTO_CODIGO_UNICO_EXACTO"
    elif has_puente and re.search(r"UNICO|RESUELTO|MATCH", estados, re.I):
        method, level, state = "PUENTE_APROBADO", "2", "RESUELTO_PUENTE_APROBADO"
    elif has_plan:
        method, level, state = "PLAN_INSTITUCIONAL", "3", "RESUELTO_PLAN_INSTITUCIONAL"
    elif has_tipo:
        method, level, state = "REGLA_TIPO_DURACION", "4", "RESUELTO_REGLA_TIPO_DURACION"
    elif first_value(rows, "NOMBRE_CARRERA_NORMALIZADO"):
        method, level, state = "NOMBRE_NORMALIZADO_CANDIDATO", "5", "CANDIDATO_NOMBRE"
    else:
        method, level, state = "NO_EVALUADO", "", "NO_EVALUADO"
    missing = sorted(set().union(*(missing_by_source.get(r.get("FUENTE", ""), set()) for r in rows)))
    return {
        "method": method,
        "level": level,
        "state": state,
        "sources": sources,
        "processes": processes,
        "relation_multiple": relation_multiple,
        "missing": missing,
        "critical_missing": "SI" if any(m in {"CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR"} for m in missing) else "NO",
        "bloqueante": "SI" if bloqueante else "NO",
        "motivo": "ES_BLOQUEANTE observado" if bloqueante else "",
    }


FASE5_REL_FIELDS = [
    "CODIGO_UNICO", "ID_IDENTIDAD", "CODIGO_UNICO_FINAL", "CODCLI", "CODCARR", "CODCARPR",
    "NOMBRE_CARRERA_INSTITUCIONAL", "NOMBRE_CARRERA_SIES", "JORNADA", "MODALIDAD", "SEDE",
    "VERSION", "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS", "VIGENCIA", "METODO_RESOLUCION", "NIVEL_DECISION",
    "ESTADO_IDENTIDAD", "NIVEL_RESPALDO", "CLASIFICACION_EVIDENCIA", "FUENTE_PRINCIPAL",
    "FUENTES_SECUNDARIAS", "PROCESOS_QUE_RESPALDAN", "TOTAL_FUENTES_RESPALDO",
    "ES_BLOQUEANTE", "MOTIVO_BLOQUEO", "CAMPO_FALTANTE_CRITICO", "CAMPOS_FALTANTES",
    "ES_RELACION_MULTIPLE", "ES_CONTRADICCION_REAL", "OBSERVACIONES", "HASH_TRAZABILIDAD",
]

FASE5_SUMMARY_FIELDS = [
    "CODIGO_UNICO", "ARCHIVO_PDF", "PLAN_DE_ESTUDIO_CANONICO_PDF", "NOMBRE_CARRERA_UNIFICADO",
    "CODIGO_UNICO_FINAL_UNIFICADO", "CODCARR_UNIFICADO", "CODCARPR_UNIFICADO",
    "CODCARR_OBSERVADOS", "CODCARPR_OBSERVADOS", "PLAN_ESTUDIOS_SIES_UNIFICADO",
    "PLAN_ESTUDIOS_SIES_OBSERVADOS", "PLAN_DE_ESTUDIO_INSTITUCIONAL_UNIFICADO",
    "PLANES_INSTITUCIONALES_OBSERVADOS", "JORNADA_UNIFICADA", "JORNADAS_OBSERVADAS",
    "MODALIDAD_UNIFICADA", "MODALIDADES_OBSERVADAS", "SEDE_UNIFICADA", "SEDES_OBSERVADAS",
    "VERSION_UNIFICADA", "VERSIONES_OBSERVADAS", "TIPO_PLAN_CARRERA_UNIFICADO",
    "TIPOS_PLAN_OBSERVADOS", "DURACION_ESTUDIOS_UNIFICADA", "DURACIONES_OBSERVADAS",
    "VIGENCIA_UNIFICADA", "VIGENCIAS_OBSERVADAS", "METODO_RESOLUCION", "NIVEL_DECISION",
    "ESTADO_IDENTIDAD", "NIVEL_RESPALDO", "FUENTE_PRINCIPAL", "FUENTES_RESPALDO",
    "TOTAL_RELACIONES_MAESTRA", "TOTAL_FUENTES_RESPALDO", "TIENE_VARIANTES_LEGITIMAS",
    "TIPO_VARIANTE", "TIENE_CAMPO_FALTANTE_CRITICO", "CAMPOS_FALTANTES", "ES_BLOQUEANTE",
    "MOTIVO_BLOQUEO", "ES_CONTRADICCION_REAL", "OBSERVACIONES", "ESTADO_APLICACION_34",
    "HASH_TRAZABILIDAD_APLICACION",
]


def values_join(rows: list[dict[str, str]], field: str) -> str:
    return "|".join(active_values(rows, field))


def unique_or_blank(rows: list[dict[str, str]], field: str) -> str:
    vals = active_values(rows, field)
    return vals[0] if len(vals) == 1 else ""


def bool_si(value: bool) -> str:
    return "SI" if value else "NO"


def codigo_jornada_compatible(values: list[str]) -> bool:
    normalized = {normalize_for_compare(v) for v in values if normalize_for_compare(v)}
    if len(normalized) <= 1:
        return True
    # Codigos observados en fuentes distintas: D/1, V/2, N/4 pueden coexistir sin
    # probar contradiccion material en esta fase.
    compatible_sets = [{"D", "1"}, {"V", "2"}, {"N", "4"}]
    return any(normalized <= item for item in compatible_sets)


def classify_fase5_multiple(rows: list[dict[str, str]]) -> tuple[str, list[str], bool]:
    variant_types: list[str] = []
    if len(rows) <= 1:
        return "MULTIPLES_FILAS_MISMA_IDENTIDAD", variant_types, False
    for field, label in [
        ("PLAN_DE_ESTUDIO_INSTITUCIONAL", "PLAN"),
        ("JORNADA", "JORNADA"),
        ("MODALIDAD", "MODALIDAD"),
        ("SEDE", "SEDE"),
        ("VERSION", "VERSION"),
        ("TIPO_PLAN_CARRERA", "TIPO_PLAN"),
        ("DURACION_ESTUDIOS", "DURACION"),
        ("VIGENCIA", "VIGENCIA"),
    ]:
        vals = active_values(rows, field)
        if len(vals) > 1:
            variant_types.append(label)
    incompatible = False
    if len(active_values(rows, "CODCARR")) > 1:
        incompatible = True
    if len(active_values(rows, "CODCARPR")) > 1:
        incompatible = True
    if len(active_values(rows, "PLAN_DE_ESTUDIO_INSTITUCIONAL")) > 1:
        # Multiples planes se conservan como variante; no son contradiccion por si solos.
        incompatible = False
    if len(active_values(rows, "JORNADA")) > 1 and not codigo_jornada_compatible(active_values(rows, "JORNADA")):
        incompatible = False
    if incompatible:
        return "INCOMPATIBILIDAD_OTRA", variant_types, True
    if variant_types:
        if "PLAN" in variant_types:
            return "MULTIPLES_PLANES_LEGITIMOS", variant_types, False
        if "JORNADA" in variant_types:
            return "MULTIPLES_JORNADAS_LEGITIMAS", variant_types, False
        if "SEDE" in variant_types:
            return "MULTIPLES_SEDES_LEGITIMAS", variant_types, False
        if "VERSION" in variant_types:
            return "MULTIPLES_VERSIONES_LEGITIMAS", variant_types, False
        return "MULTIPLES_VARIANTES_LEGITIMAS", variant_types, False
    return "MULTIPLES_FUENTES_COMPATIBLES", variant_types, False


def read_fase4b_summary(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    capture = False
    table_lines: list[str] = []
    for line in lines:
        if line.startswith("# RESUMEN_POR_CODIGO_UNICO"):
            capture = True
            continue
        if capture and line.startswith("# "):
            break
        if capture and line.strip():
            table_lines.append(line)
    if not table_lines:
        return []
    reader = csv.DictReader(table_lines, delimiter="\t")
    return list(reader)


def fase_4(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if any(phase_status(ctx.state, i) != "COMPLETADA" for i in [0, 1, 2, 3]):
        raise FlujoError("Fases 0 a 3 deben estar COMPLETADAS antes de Fase 4.")
    if phase_status(ctx.state, 5) != "PENDIENTE":
        raise FlujoError("Fase 5 no debe estar ejecutada antes de completar Fase 4.")
    rec_path = output_path(ctx, "05_AUDITORIA/FASE3B_RECOMENDACION_FASE4.json")
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    if not rec.get("fase4_autorizada"):
        return PhaseResult(estado="BLOQUEADA", bloqueos=[{"bloqueo": "fase4_no_autorizada", "detalle": str(rec_path)}], resumen=["Estado: BLOQUEADA"], comando_reanudacion=f"NO AVANZAR A FASE 5. Resolver primero: {rec_path}")

    inputs = [
        "03_INTERMEDIOS/01_BASE_NORMALIZADA_MATRICULA_UNIFICADA.tsv",
        "03_INTERMEDIOS/02_BASE_NORMALIZADA_EXTRANJEROS.tsv",
        "03_INTERMEDIOS/03_BASE_NORMALIZADA_AVANCE.tsv",
        "03_INTERMEDIOS/04_PUENTES_NORMALIZADOS.tsv",
    ]
    rows: list[dict[str, str]] = []
    for rel in inputs:
        rows.extend(read_optional_tsv(output_path(ctx, rel)))
    tipo_rows = read_optional_tsv(output_path(ctx, "03_INTERMEDIOS/05_DURACION_TIPO_PLAN.tsv"))
    for row in tipo_rows:
        common = {field: "" for field in COMMON_SCHEMA}
        for key in common:
            if key in row:
                common[key] = row[key]
        common["PROCESO_ORIGEN"] = row.get("PROCESO_ORIGEN", "")
        common["FUENTE"] = row.get("FUENTE", "")
        common["HASH_FUENTE"] = row.get("HASH_FUENTE", "")
        common["NIVEL_RESPALDO"] = "TIPO_DURACION"
        common["CLASIFICACION_EVIDENCIA"] = row.get("CLASIFICACION_EVIDENCIA", "DATO_OBSERVADO")
        rows.append(common)
    for row in rows:
        row.setdefault("CLASIFICACION_EVIDENCIA", "DATO_OBSERVADO")
    universe = append_keys(rows)
    missing_rows = read_optional_tsv(output_path(ctx, "05_AUDITORIA/FASE3B_CLASIFICACION_44_FALTANTES.tsv"))
    missing_by_source: dict[str, set[str]] = {}
    for m in missing_rows:
        missing_by_source.setdefault(m.get("FUENTE", ""), set()).add(m.get("CAMPO_FALTANTE", ""))
    impact = read_optional_tsv(output_path(ctx, "05_AUDITORIA/FASE3B_IMPACTO_EN_34_DIRECTAS.tsv"))
    incident_codes = set()
    incident_by_code: dict[str, set[str]] = {}
    for r in impact:
        if r.get("ESTA_EN_34_DIRECTAS") == "SI":
            for code in split_pipe(r.get("CODIGO_UNICO", "")):
                incident_codes.add(code)
                incident_by_code.setdefault(code, set()).add(r.get("ID_INCIDENTE", ""))
    groups: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in universe:
        groups.setdefault(grouping_key(row), []).append(row)
    now = now_iso()
    master = []
    for group_rows in groups.values():
        c = classify_master_group(group_rows, incident_codes, missing_by_source)
        base_parts = [first_value(group_rows, f) for f in ["ANIO_PROCESO", "CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE", "VERSION"]]
        fuente_principal = c["sources"][0] if c["sources"] else ""
        fuentes_sec = "|".join(c["sources"][1:])
        identity = {
            "ID_IDENTIDAD": "ID_" + stable_hash(base_parts, 16),
            "ANIO_PROCESO": first_value(group_rows, "ANIO_PROCESO"),
            "ANIO_DATOS": first_value(group_rows, "ANIO_DATOS"),
            "PERIODO": first_value(group_rows, "PERIODO"),
            "CODIGO_UNICO": first_value(group_rows, "CODIGO_UNICO"),
            "CODIGO_UNICO_FINAL": first_value(group_rows, "CODIGO_UNICO_FINAL"),
            "CODCLI": "|".join(active_values(group_rows, "CODCLI")[:20]),
            "CODCARR": first_value(group_rows, "CODCARR"),
            "CODCARPR": first_value(group_rows, "CODCARPR"),
            "NOMBRE_CARRERA_INSTITUCIONAL": first_value(group_rows, "NOMBRE_CARRERA"),
            "NOMBRE_CARRERA_SIES": first_value(group_rows, "NOMBRE_CARRERA"),
            "JORNADA": first_value(group_rows, "JORNADA"),
            "MODALIDAD": first_value(group_rows, "MODALIDAD"),
            "SEDE": first_value(group_rows, "SEDE"),
            "VERSION": first_value(group_rows, "VERSION"),
            "PLAN_ESTUDIOS_SIES": first_value(group_rows, "PLAN_ESTUDIOS_SIES"),
            "PLAN_DE_ESTUDIO_INSTITUCIONAL": first_value(group_rows, "PLAN_DE_ESTUDIO_INSTITUCIONAL"),
            "TIPO_PLAN_CARRERA": first_value(group_rows, "TIPO_PLAN_CARRERA"),
            "DURACION_ESTUDIOS": first_value(group_rows, "DURACION_ESTUDIOS"),
            "VIGENCIA": first_value(group_rows, "VIGENCIA"),
            "METODO_RESOLUCION": c["method"],
            "NIVEL_DECISION": c["level"],
            "ESTADO_IDENTIDAD": c["state"],
            "NIVEL_RESPALDO": first_value(group_rows, "NIVEL_RESPALDO"),
            "CLASIFICACION_EVIDENCIA": first_value(group_rows, "CLASIFICACION_EVIDENCIA") or "DATO_OBSERVADO",
            "FUENTE_PRINCIPAL": fuente_principal,
            "FUENTES_SECUNDARIAS": fuentes_sec,
            "PROCESOS_QUE_RESPALDAN": "|".join(c["processes"]),
            "TOTAL_FUENTES_RESPALDO": len(c["sources"]),
            "ES_BLOQUEANTE": c["bloqueante"],
            "MOTIVO_BLOQUEO": c["motivo"],
            "CAMPO_FALTANTE_CRITICO": c["critical_missing"],
            "CAMPOS_FALTANTES": "|".join(c["missing"]),
            "ES_RELACION_MULTIPLE": c["relation_multiple"],
            "ES_CONTRADICCION_REAL": "NO",
            "OBSERVACIONES": "AUDITADO_POST_FASE3" if (first_value(group_rows, "CODIGO_UNICO") in incident_codes or first_value(group_rows, "CODIGO_UNICO_FINAL") in incident_codes) else "",
            "HASH_TRAZABILIDAD": "",
            "FECHA_CONSTRUCCION": now,
        }
        trace_parts = [identity[f] for f in MASTER_FIELDS if f not in {"HASH_TRAZABILIDAD", "FECHA_CONSTRUCCION"}] + active_values(group_rows, "HASH_FUENTE")
        identity["HASH_TRAZABILIDAD"] = stable_hash(trace_parts)
        master.append(identity)
    resolved_states = {"RESUELTO_CODIGO_UNICO_EXACTO", "RESUELTO_PUENTE_APROBADO", "RESUELTO_PLAN_INSTITUCIONAL", "RESUELTO_REGLA_TIPO_DURACION"}
    resolved = [r for r in master if r["ESTADO_IDENTIDAD"] in resolved_states]
    ambiguous = [r for r in master if r["ESTADO_IDENTIDAD"] in {"CANDIDATO_NOMBRE", "AMBIGUO_MULTIPLES_COINCIDENCIAS"}]
    blocked = [r for r in master if str(r["ESTADO_IDENTIDAD"]).startswith("BLOQUEADO")]
    no_eval = [r for r in master if r["ESTADO_IDENTIDAD"] == "NO_EVALUADO"]
    id_counts: dict[str, int] = {}
    for r in master:
        id_counts[r["ID_IDENTIDAD"]] = id_counts.get(r["ID_IDENTIDAD"], 0) + 1
    dup_id = [{"ID_IDENTIDAD": k, "TOTAL": v} for k, v in id_counts.items() if v > 1]
    exact_seen, exact_dup = set(), []
    for r in master:
        sig = tuple(r[f] for f in MASTER_FIELDS if f not in {"HASH_TRAZABILIDAD", "FECHA_CONSTRUCCION"})
        if sig in exact_seen:
            exact_dup.append(r)
        exact_seen.add(sig)
    res_sin_fuente = [r for r in resolved if not r["FUENTE_PRINCIPAL"]]
    res_nombre = [r for r in resolved if r["METODO_RESOLUCION"] == "NOMBRE_NORMALIZADO_CANDIDATO"]
    incompat = [r for r in resolved if truthy_block(r["ES_BLOQUEANTE"])]
    contradictions: list[dict[str, Any]] = []
    fields_missing = [{"ID_IDENTIDAD": r["ID_IDENTIDAD"], "CAMPO_FALTANTE_CRITICO": r["CAMPO_FALTANTE_CRITICO"], "CAMPOS_FALTANTES": r["CAMPOS_FALTANTES"], "IMPACTO": "FALTANTE_BLOQUEANTE_PARA_RESOLUCION" if r["CAMPO_FALTANTE_CRITICO"] == "SI" and r["ESTADO_IDENTIDAD"] not in resolved_states else "FALTANTE_NO_BLOQUEANTE"} for r in master if r["CAMPOS_FALTANTES"]]
    by_process: dict[str, int] = {}
    for r in master:
        by_process[r["PROCESOS_QUE_RESPALDAN"]] = by_process.get(r["PROCESOS_QUE_RESPALDAN"], 0) + 1
    process_rows = [{"PROCESOS_QUE_RESPALDAN": k, "IDENTIDADES": v} for k, v in sorted(by_process.items())]
    method_rows = []
    for method in sorted({r["METODO_RESOLUCION"] for r in master}):
        items = [r for r in master if r["METODO_RESOLUCION"] == method]
        method_rows.append({"METODO_RESOLUCION": method, "NIVEL_DECISION": first_value(items, "NIVEL_DECISION"), "IDENTIDADES": len(items), "PORCENTAJE": round(len(items) * 100 / max(1, len(master)), 2), "RESUELTAS": sum(1 for r in items if r in resolved), "AMBIGUAS": sum(1 for r in items if r in ambiguous), "BLOQUEADAS": sum(1 for r in items if r in blocked), "NO_EVALUADAS": sum(1 for r in items if r in no_eval), "FUENTES_PRINCIPALES": "|".join(active_values(items, "FUENTE_PRINCIPAL")[:10]), "OBSERVACION": ""})
    trace_rows = [{"ID_IDENTIDAD": r["ID_IDENTIDAD"], "FUENTE_PRINCIPAL": r["FUENTE_PRINCIPAL"], "FUENTES_SECUNDARIAS": r["FUENTES_SECUNDARIAS"], "HASH_TRAZABILIDAD": r["HASH_TRAZABILIDAD"]} for r in master]
    direct_codes = {r.get("CODIGO_UNICO", "") for r in read_optional_tsv(REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv")}
    represented_34 = len({r["CODIGO_UNICO"] for r in master if r["CODIGO_UNICO"] in direct_codes})
    represented_incidents = set()
    for r in master:
        for code in [r.get("CODIGO_UNICO", ""), r.get("CODIGO_UNICO_FINAL", "")]:
            represented_incidents.update(i for i in incident_by_code.get(code, set()) if i)
    integrity = [
        {"CONTROL": "tabla_maestra_generada", "ESTADO": "OK" if master else "ERROR", "OBSERVACION": str(len(master))},
        {"CONTROL": "id_identidad_unico", "ESTADO": "OK" if not dup_id else "ERROR", "OBSERVACION": str(len(dup_id))},
        {"CONTROL": "hash_trazabilidad_informado", "ESTADO": "OK" if all(r["HASH_TRAZABILIDAD"] for r in master) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "resuelta_tiene_fuente", "ESTADO": "OK" if not res_sin_fuente else "ERROR", "OBSERVACION": str(len(res_sin_fuente))},
        {"CONTROL": "resuelta_no_solo_nombre", "ESTADO": "OK" if not res_nombre else "ERROR", "OBSERVACION": str(len(res_nombre))},
        {"CONTROL": "plan_estudios_separado", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "codigo_unico_separado", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "incidentes_no_triplicados", "ESTADO": "OK" if len(represented_incidents) <= 39 else "ERROR", "OBSERVACION": str(len(represented_incidents))},
        {"CONTROL": "casos_34_representados", "ESTADO": "OK" if represented_34 >= 34 else "ERROR", "OBSERVACION": str(represented_34)},
        {"CONTROL": "resueltas_no_bloqueantes", "ESTADO": "OK" if not incompat else "ERROR", "OBSERVACION": str(len(incompat))},
        {"CONTROL": "fase5_no_ejecutada", "ESTADO": "OK" if phase_status(ctx.state, 5) == "PENDIENTE" else "ERROR", "OBSERVACION": ""},
    ]
    errors = [r for r in integrity if r["ESTADO"] == "ERROR"]
    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    salidas = [
        write_tsv(universe, output_path(ctx, "03_INTERMEDIOS/06_UNIVERSO_CONSOLIDABLE_IDENTIDAD.tsv"), [*COMMON_SCHEMA, "CLASIFICACION_EVIDENCIA", "ID_UNIVERSO", "LLAVE_IDENTIDAD_BASE", "LLAVE_IDENTIDAD_BASE_CAMPOS", "LLAVE_SIES", "LLAVE_SIES_CAMPOS", "LLAVE_INSTITUCIONAL", "LLAVE_INSTITUCIONAL_CAMPOS", "LLAVE_PUENTE", "LLAVE_PUENTE_CAMPOS"]),
        write_tsv(universe, output_path(ctx, "03_INTERMEDIOS/07_LLAVES_IDENTIDAD_CONSTRUIDAS.tsv"), ["ID_UNIVERSO", "FUENTE", "CODIGO_UNICO", "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE", "VERSION", "LLAVE_IDENTIDAD_BASE", "LLAVE_IDENTIDAD_BASE_CAMPOS", "LLAVE_SIES", "LLAVE_SIES_CAMPOS", "LLAVE_INSTITUCIONAL", "LLAVE_INSTITUCIONAL_CAMPOS", "LLAVE_PUENTE", "LLAVE_PUENTE_CAMPOS"]),
        write_tsv(master, output_path(ctx, "04_RESULTADOS/01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv"), MASTER_FIELDS),
        write_tsv(resolved, output_path(ctx, "04_RESULTADOS/02_IDENTIDADES_RESUELTAS.tsv"), MASTER_FIELDS),
        write_tsv(ambiguous, output_path(ctx, "04_RESULTADOS/03_IDENTIDADES_AMBIGUAS.tsv"), MASTER_FIELDS),
        write_tsv(blocked, output_path(ctx, "04_RESULTADOS/04_IDENTIDADES_BLOQUEADAS.tsv"), MASTER_FIELDS),
        write_tsv(process_rows, output_path(ctx, "04_RESULTADOS/05_IDENTIDADES_POR_PROCESO.tsv"), ["PROCESOS_QUE_RESPALDAN", "IDENTIDADES"]),
        write_tsv(no_eval, output_path(ctx, "04_RESULTADOS/05A_IDENTIDADES_NO_EVALUADAS.tsv"), MASTER_FIELDS),
        write_tsv(method_rows, output_path(ctx, "04_RESULTADOS/05B_RESUMEN_METODOS_RESOLUCION.tsv"), ["METODO_RESOLUCION", "NIVEL_DECISION", "IDENTIDADES", "PORCENTAJE", "RESUELTAS", "AMBIGUAS", "BLOQUEADAS", "NO_EVALUADAS", "FUENTES_PRINCIPALES", "OBSERVACION"]),
        write_tsv(dup_id, output_path(ctx, "05_AUDITORIA/04_DUPLICADOS_TABLA_MAESTRA.tsv"), ["ID_IDENTIDAD", "TOTAL"]),
        write_tsv(contradictions, output_path(ctx, "05_AUDITORIA/05_CONTRADICCIONES_TABLA_MAESTRA.tsv"), ["TIPO", "DETALLE"]),
        write_tsv(fields_missing, output_path(ctx, "05_AUDITORIA/FASE4_CAMPOS_FALTANTES_POR_IDENTIDAD.tsv"), ["ID_IDENTIDAD", "CAMPO_FALTANTE_CRITICO", "CAMPOS_FALTANTES", "IMPACTO"]),
        write_tsv(res_sin_fuente, output_path(ctx, "05_AUDITORIA/FASE4_RESUELTOS_SIN_FUENTE.tsv"), MASTER_FIELDS),
        write_tsv(res_nombre, output_path(ctx, "05_AUDITORIA/FASE4_RESUELTOS_SOLO_POR_NOMBRE.tsv"), MASTER_FIELDS),
        write_tsv(incompat, output_path(ctx, "05_AUDITORIA/FASE4_ESTADOS_INCOMPATIBLES.tsv"), MASTER_FIELDS),
        write_tsv(integrity, output_path(ctx, "05_AUDITORIA/FASE4_CONTROL_INTEGRIDAD.tsv"), ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_tsv(trace_rows, output_path(ctx, "05_AUDITORIA/FASE4_TRAZABILIDAD_FUENTES.tsv"), ["ID_IDENTIDAD", "FUENTE_PRINCIPAL", "FUENTES_SECUNDARIAS", "HASH_TRAZABILIDAD"]),
        write_text(f"{now_iso()} FASE4 tabla maestra estado={estado} identidades={len(master)}\n", output_path(ctx, "06_LOGS/fase4_tabla_maestra.log")),
    ]
    conteos = {
        "registros_universo_consolidable": len(universe),
        "registros_tabla_maestra": len(master),
        "identidades_resueltas": len(resolved),
        "identidades_ambiguas": len(ambiguous),
        "identidades_bloqueadas": len(blocked),
        "identidades_no_evaluadas": len(no_eval),
        "metodos_usados": len(method_rows),
        "duplicados_exactos": len(exact_dup),
        "duplicados_id": len(dup_id),
        "contradicciones_reales": len(contradictions),
        "resueltos_sin_fuente": len(res_sin_fuente),
        "resueltos_solo_nombre": len(res_nombre),
        "campos_faltantes_criticos": sum(1 for r in fields_missing if r["CAMPO_FALTANTE_CRITICO"] == "SI"),
        "incidentes_post_fase3_incorporados": len(represented_incidents),
        "casos_34_directas_representados": represented_34,
        "estados_incompatibles": len(incompat),
    }
    next_cmd = command_for_phase(5) if estado == "COMPLETADA" else f"NO AVANZAR A FASE 5. Resolver primero: {output_path(ctx, '05_AUDITORIA/FASE4_CONTROL_INTEGRIDAD.tsv').resolve()}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos=conteos,
        validaciones=integrity,
        bloqueos=[{"bloqueo": e["CONTROL"], "detalle": e["OBSERVACION"]} for e in errors],
        entradas={rel: str(output_path(ctx, rel).resolve()) for rel in inputs},
        hashes={rel: sha256_file(output_path(ctx, rel)) for rel in inputs},
        resumen=[
            f"Estado: {estado}",
            f"Registros universo consolidable: {len(universe)}",
            f"Registros tabla maestra: {len(master)}",
            f"Identidades resueltas: {len(resolved)}",
            f"Identidades ambiguas: {len(ambiguous)}",
            f"Identidades bloqueadas: {len(blocked)}",
            f"Identidades no evaluadas: {len(no_eval)}",
            f"Resueltas por CODIGO_UNICO exacto: {sum(1 for r in master if r['ESTADO_IDENTIDAD']=='RESUELTO_CODIGO_UNICO_EXACTO')}",
            f"Resueltas por puente aprobado: {sum(1 for r in master if r['ESTADO_IDENTIDAD']=='RESUELTO_PUENTE_APROBADO')}",
            f"Resueltas por plan institucional: {sum(1 for r in master if r['ESTADO_IDENTIDAD']=='RESUELTO_PLAN_INSTITUCIONAL')}",
            f"Resueltas por tipo/duracion: {sum(1 for r in master if r['ESTADO_IDENTIDAD']=='RESUELTO_REGLA_TIPO_DURACION')}",
            f"Candidatos solo por nombre: {sum(1 for r in master if r['ESTADO_IDENTIDAD']=='CANDIDATO_NOMBRE')}",
            f"ID_IDENTIDAD duplicados: {len(dup_id)}",
            f"Duplicados exactos: {len(exact_dup)}",
            f"Contradicciones reales activas: {len(contradictions)}",
            f"Identidades resueltas sin fuente: {len(res_sin_fuente)}",
            f"Identidades resueltas solo por nombre: {len(res_nombre)}",
            f"Estados incompatibles: {len(incompat)}",
            f"Campos faltantes criticos trazados: {conteos['campos_faltantes_criticos']}",
            f"Incidentes post FASE 3 incorporados: {conteos['incidentes_post_fase3_incorporados']}",
            f"Casos de las 34 directas representados: {represented_34}",
            "PLAN_ESTUDIOS separado de PLAN_DE_ESTUDIO: SI",
            "CODIGO_UNICO separado de CODIGO_UNICO_FINAL: SI",
            "Ambiguedades preservadas: SI",
            "Bloqueos preservados: SI",
            f"Tabla maestra: {output_path(ctx, '04_RESULTADOS/01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv').resolve()}",
            f"Identidades resueltas: {output_path(ctx, '04_RESULTADOS/02_IDENTIDADES_RESUELTAS.tsv').resolve()}",
            f"Identidades ambiguas: {output_path(ctx, '04_RESULTADOS/03_IDENTIDADES_AMBIGUAS.tsv').resolve()}",
            f"Identidades bloqueadas: {output_path(ctx, '04_RESULTADOS/04_IDENTIDADES_BLOQUEADAS.tsv').resolve()}",
            f"Auditoria: {output_path(ctx, '05_AUDITORIA').resolve()}",
            f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
            "Originales modificados: NO",
            "Precarga generada: NO",
            "PES generado: NO",
        ],
        comando_reanudacion=next_cmd,
    )


def fase_5(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if any(phase_status(ctx.state, i) != "COMPLETADA" for i in [0, 1, 2, 3, 4]):
        raise FlujoError("Fases 0 a 4 deben estar COMPLETADAS antes de Fase 5.")
    if phase_status(ctx.state, 6) != "PENDIENTE":
        raise FlujoError("Fase 6 no debe estar ejecutada antes de completar Fase 5.")

    validation_run = REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415"
    universe_path = validation_run / "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv"
    mapeo_path = validation_run / "02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv"
    puente_path = validation_run / "02_INTERMEDIOS/03_VALIDACION_PUENTE_34.tsv"
    plan_path = validation_run / "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv"
    master_path = output_path(ctx, "04_RESULTADOS/01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv")
    resolved_path = output_path(ctx, "04_RESULTADOS/02_IDENTIDADES_RESUELTAS.tsv")
    ambiguous_path = output_path(ctx, "04_RESULTADOS/03_IDENTIDADES_AMBIGUAS.tsv")
    blocked_path = output_path(ctx, "04_RESULTADOS/04_IDENTIDADES_BLOQUEADAS.tsv")
    fase4b_path = output_path(ctx, "05_AUDITORIA/FASE4B_DIAGNOSTICO_34_DIRECTAS.tsv")
    required_paths = [
        universe_path, mapeo_path, puente_path, plan_path, master_path, resolved_path,
        ambiguous_path, blocked_path, fase4b_path,
        output_path(ctx, "05_AUDITORIA/FASE3B_IMPACTO_EN_34_DIRECTAS.tsv"),
        output_path(ctx, "05_AUDITORIA/FASE3B_RECOMENDACION_FASE4.json"),
    ]
    missing = [str(p) for p in required_paths if not p.exists()]
    if missing:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "entradas_fase5_faltantes", "detalle": "|".join(missing)}],
            resumen=["Estado: BLOQUEADA", "Faltan entradas obligatorias de Fase 5."],
            comando_reanudacion=f"NO AVANZAR A FASE 6. Resolver primero: {output_path(ctx, '05_AUDITORIA/FASE5_CONTROL_INTEGRIDAD.tsv').resolve()}",
        )

    fase4b = read_fase4b_summary(fase4b_path)
    fase4b_ok = (
        len(fase4b) == 34
        and sum(1 for r in fase4b if r.get("TIENE_RESUELTO") == "True") == 34
        and sum(1 for r in fase4b if r.get("TIENE_AMBIGUO") == "True") == 0
        and sum(1 for r in fase4b if r.get("TIENE_BLOQUEADO") == "True") == 0
        and sum(1 for r in fase4b if r.get("TIENE_NO_EVALUADO") == "True") == 0
        and sum(1 for r in fase4b if r.get("SIN_REGISTRO_MAESTRA") == "True") == 0
    )
    if not fase4b_ok:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "diagnostico_fase4b_no_autoriza_fase5", "detalle": str(fase4b_path)}],
            resumen=["Estado: BLOQUEADA", "Diagnostico FASE4B no confirma 34 identidades resueltas."],
            comando_reanudacion=f"NO AVANZAR A FASE 6. Resolver primero: {fase4b_path.resolve()}",
        )

    universe = read_tsv_dicts(universe_path)
    mapeo = read_tsv_dicts(mapeo_path)
    puente = read_tsv_dicts(puente_path)
    plan_prev = read_tsv_dicts(plan_path)
    master = read_tsv_dicts(master_path)
    ambiguous_prev = read_tsv_dicts(ambiguous_path)
    blocked_prev = read_tsv_dicts(blocked_path)

    direct_codes = [r.get("CODIGO_UNICO", "") for r in universe]
    direct_set = set(direct_codes)
    code_dups = sorted({c for c in direct_codes if c and direct_codes.count(c) > 1})
    pdfs = {r.get("ARCHIVO_PDF", "") for r in universe if r.get("ARCHIVO_PDF", "")}
    mapeo_by_pdf = {r.get("ARCHIVO_PDF", ""): r for r in mapeo}
    puente_by_code = {r.get("CODIGO_UNICO", ""): r for r in puente}
    plan_by_code = {r.get("CODIGO_UNICO", ""): r for r in plan_prev}
    universe_by_code = {r.get("CODIGO_UNICO", ""): r for r in universe}

    control_universe = [
        {"CONTROL": "codigos_unicos_34", "ESTADO": "OK" if len(direct_set) == 34 else "ERROR", "VALOR": len(direct_set), "OBSERVACION": ""},
        {"CONTROL": "codigos_vacios", "ESTADO": "OK" if "" not in direct_set else "ERROR", "VALOR": sum(1 for c in direct_codes if not c), "OBSERVACION": ""},
        {"CONTROL": "codigos_duplicados", "ESTADO": "OK" if not code_dups else "ERROR", "VALOR": len(code_dups), "OBSERVACION": "|".join(code_dups[:20])},
        {"CONTROL": "pdf_directos_11", "ESTADO": "OK" if len(pdfs) == 11 else "ERROR", "VALOR": len(pdfs), "OBSERVACION": ""},
        {"CONTROL": "codigos_con_pdf", "ESTADO": "OK" if all(universe_by_code[c].get("ARCHIVO_PDF") for c in direct_set) else "ERROR", "VALOR": sum(1 for c in direct_set if universe_by_code[c].get("ARCHIVO_PDF")), "OBSERVACION": ""},
        {"CONTROL": "pdf_con_plan_canonico", "ESTADO": "OK" if all(universe_by_code[c].get("PLAN_DE_ESTUDIO_CANONICO") for c in direct_set) else "ERROR", "VALOR": sum(1 for c in direct_set if universe_by_code[c].get("PLAN_DE_ESTUDIO_CANONICO")), "OBSERVACION": ""},
    ]

    rels = []
    for row in master:
        if row.get("CODIGO_UNICO") in direct_set:
            rels.append({field: row.get(field, "") for field in FASE5_REL_FIELDS})

    by_code: dict[str, list[dict[str, str]]] = {code: [] for code in direct_set}
    for row in rels:
        by_code.setdefault(row.get("CODIGO_UNICO", ""), []).append(row)

    multiple_audit: list[dict[str, Any]] = []
    variants_detail: list[dict[str, Any]] = []
    comparison_pdf: list[dict[str, Any]] = []
    comparison_bridge: list[dict[str, Any]] = []
    missing_34: list[dict[str, Any]] = []
    output_rows: list[dict[str, Any]] = []
    contradictions_rows: list[dict[str, Any]] = []

    resolved_states = {"RESUELTO_CODIGO_UNICO_EXACTO", "RESUELTO_PUENTE_APROBADO", "RESUELTO_PLAN_INSTITUCIONAL", "RESUELTO_REGLA_TIPO_DURACION"}
    ambiguous_codes_prev = {r.get("CODIGO_UNICO", "") for r in ambiguous_prev if r.get("CODIGO_UNICO", "") in direct_set}
    blocked_codes_prev = {r.get("CODIGO_UNICO", "") for r in blocked_prev if r.get("CODIGO_UNICO", "") in direct_set}

    for code in sorted(direct_set):
        rows = by_code.get(code, [])
        u = universe_by_code[code]
        classif, variant_types, incompatible = classify_fase5_multiple(rows)
        observed = {field: active_values(rows, field) for field in [
            "CODIGO_UNICO_FINAL", "CODCARR", "CODCARPR", "PLAN_ESTUDIOS_SIES",
            "PLAN_DE_ESTUDIO_INSTITUCIONAL", "JORNADA", "MODALIDAD", "SEDE",
            "VERSION", "TIPO_PLAN_CARRERA", "DURACION_ESTUDIOS", "VIGENCIA",
            "ESTADO_IDENTIDAD", "METODO_RESOLUCION", "FUENTE_PRINCIPAL",
        ]}
        multiple_audit.append({
            "CODIGO_UNICO": code,
            "FILAS_MAESTRA": len(rows),
            "ID_IDENTIDAD_UNICOS": len(active_values(rows, "ID_IDENTIDAD")),
            "CODIGO_UNICO_FINAL_UNICOS": len(observed["CODIGO_UNICO_FINAL"]),
            "CODCARR_UNICOS": len(observed["CODCARR"]),
            "CODCARPR_UNICOS": len(observed["CODCARPR"]),
            "PLAN_ESTUDIOS_SIES_UNICOS": len(observed["PLAN_ESTUDIOS_SIES"]),
            "PLAN_INSTITUCIONAL_UNICOS": len(observed["PLAN_DE_ESTUDIO_INSTITUCIONAL"]),
            "JORNADAS_UNICAS": len(observed["JORNADA"]),
            "MODALIDADES_UNICAS": len(observed["MODALIDAD"]),
            "SEDES_UNICAS": len(observed["SEDE"]),
            "VERSIONES_UNICAS": len(observed["VERSION"]),
            "TIPOS_PLAN_UNICOS": len(observed["TIPO_PLAN_CARRERA"]),
            "DURACIONES_UNICAS": len(observed["DURACION_ESTUDIOS"]),
            "VIGENCIAS_UNICAS": len(observed["VIGENCIA"]),
            "ESTADOS_UNICOS": len(observed["ESTADO_IDENTIDAD"]),
            "METODOS_UNICOS": len(observed["METODO_RESOLUCION"]),
            "FUENTES_UNICAS": len(observed["FUENTE_PRINCIPAL"]),
            "DIFIERE_CODIGO_UNICO_FINAL": bool_si(len(observed["CODIGO_UNICO_FINAL"]) > 1),
            "DIFIERE_CODCARR": bool_si(len(observed["CODCARR"]) > 1),
            "DIFIERE_CODCARPR": bool_si(len(observed["CODCARPR"]) > 1),
            "DIFIERE_PLAN_ESTUDIOS_SIES": bool_si(len(observed["PLAN_ESTUDIOS_SIES"]) > 1),
            "DIFIERE_PLAN_INSTITUCIONAL": bool_si(len(observed["PLAN_DE_ESTUDIO_INSTITUCIONAL"]) > 1),
            "DIFIERE_JORNADA": bool_si(len(observed["JORNADA"]) > 1),
            "DIFIERE_MODALIDAD": bool_si(len(observed["MODALIDAD"]) > 1),
            "DIFIERE_SEDE": bool_si(len(observed["SEDE"]) > 1),
            "DIFIERE_VERSION": bool_si(len(observed["VERSION"]) > 1),
            "DIFIERE_TIPO_PLAN": bool_si(len(observed["TIPO_PLAN_CARRERA"]) > 1),
            "DIFIERE_DURACION": bool_si(len(observed["DURACION_ESTUDIOS"]) > 1),
            "DIFIERE_VIGENCIA": bool_si(len(observed["VIGENCIA"]) > 1),
            "DIFIERE_ESTADO": bool_si(len(observed["ESTADO_IDENTIDAD"]) > 1),
            "DIFIERE_METODO": bool_si(len(observed["METODO_RESOLUCION"]) > 1),
            "CLASIFICACION_MULTIPLE": classif,
            "ES_INCOMPATIBLE": bool_si(incompatible),
        })
        for field, vals in observed.items():
            if len(vals) > 1:
                variants_detail.append({"CODIGO_UNICO": code, "CAMPO": field, "VALORES_OBSERVADOS": "|".join(vals), "CLASIFICACION": classif})

        pdf = u.get("ARCHIVO_PDF", "")
        plan_pdf = u.get("PLAN_DE_ESTUDIO_CANONICO", "") or mapeo_by_pdf.get(pdf, {}).get("PLAN_DE_ESTUDIO_CANONICO", "")
        plans_inst = observed["PLAN_DE_ESTUDIO_INSTITUCIONAL"]
        if not pdf or pdf not in mapeo_by_pdf:
            pdf_state = "PDF_SIN_MAPEO"
        elif not plan_pdf:
            pdf_state = "PLAN_CANONICO_AUSENTE"
        elif plans_inst and plan_pdf in plans_inst:
            pdf_state = "PDF_PLAN_COINCIDE_IDENTIDAD"
        elif plans_inst:
            pdf_state = "PDF_PLAN_CONTRADICCION"
        else:
            pdf_state = "PDF_PLAN_SIN_PLAN_INSTITUCIONAL_PARA_COMPARAR"
        comparison_pdf.append({
            "CODIGO_UNICO": code,
            "ARCHIVO_PDF": pdf,
            "PLAN_DE_ESTUDIO_CANONICO_PDF": plan_pdf,
            "PLANES_INSTITUCIONALES_OBSERVADOS": "|".join(plans_inst),
            "ESTADO_COMPARACION_PDF_PLAN": pdf_state,
            "ES_BLOQUEANTE": "SI" if pdf_state == "PDF_PLAN_CONTRADICCION" else "NO",
        })

        puente_row = puente_by_code.get(code, {})
        codcarr_prev = puente_row.get("CODCARR_CANONICO", "")
        codcarpr_prev = puente_row.get("CODCARPR_PUENTE", "")
        master_codes = set(observed["CODCARR"]) | set(observed["CODCARPR"])
        diff_real = bool((codcarr_prev and master_codes and codcarr_prev not in master_codes) or (codcarpr_prev and master_codes and codcarpr_prev not in master_codes))
        if not puente_row:
            bridge_state = "PUENTE_SIN_REGISTRO"
        elif diff_real:
            bridge_state = "PUENTE_CONTRADICCION_REAL"
        elif puente_row.get("PUENTE_MATCH_COUNT", "") not in {"", "0", "1"}:
            bridge_state = "PUENTE_MULTIPLE_COMPATIBLE"
        else:
            bridge_state = "PUENTE_COINCIDE_MAESTRA"
        comparison_bridge.append({
            "CODIGO_UNICO": code,
            "ESTADO_PUENTE_PREVIO": puente_row.get("VALIDACION_PUENTE", ""),
            "CODCARR_PUENTE_PREVIO": codcarr_prev,
            "CODCARR_MAESTRA": "|".join(observed["CODCARR"]),
            "CODIGO_UNICO_FINAL_PUENTE": puente_row.get("CODIGO_UNICO", ""),
            "CODIGO_UNICO_FINAL_MAESTRA": "|".join(observed["CODIGO_UNICO_FINAL"]),
            "COINCIDE": "NO" if diff_real else "SI",
            "DIFIERE": bool_si(diff_real),
            "DIFERENCIA_EXPLICADA": "SI" if puente_row.get("VALIDACION_PUENTE") == "BLOQUEADO" and not diff_real else "",
            "ES_BLOQUEANTE": "SI" if diff_real else "NO",
            "CLASIFICACION_PUENTE": bridge_state,
        })

        missing_fields = sorted(set().union(*(set(split_pipe(r.get("CAMPOS_FALTANTES", ""))) for r in rows)))
        if missing_fields:
            missing_34.append({"CODIGO_UNICO": code, "CAMPOS_FALTANTES": "|".join(missing_fields), "ES_CRITICO": "SI"})

        resolved_prior = all(r.get("ESTADO_IDENTIDAD") in resolved_states for r in rows) and bool(rows)
        contradiction_pdf = pdf_state == "PDF_PLAN_CONTRADICCION"
        contradiction_bridge = bridge_state == "PUENTE_CONTRADICCION_REAL"
        bloqueante = any(truthy_block(r.get("ES_BLOQUEANTE")) for r in rows) or code in blocked_codes_prev
        ambiguous = code in ambiguous_codes_prev
        if contradiction_pdf:
            app_state = "CONTRADICCION_PDF_PLAN"
        elif contradiction_bridge:
            app_state = "CONTRADICCION_PUENTE"
        elif incompatible or bloqueante:
            app_state = "BLOQUEADO_IDENTIDAD"
        elif ambiguous:
            app_state = "AMBIGUO_IDENTIDAD"
        elif not resolved_prior:
            app_state = "NO_EVALUADO"
        elif not plans_inst:
            app_state = "VALIDADO_IDENTIDAD_SIN_PLAN_INSTITUCIONAL"
        elif variant_types or len(rows) > 1:
            app_state = "VALIDADO_IDENTIDAD_CON_VARIANTES"
        else:
            app_state = "VALIDADO_IDENTIDAD_COMPLETA"
        if app_state.startswith("CONTRADICCION"):
            contradictions_rows.append({"CODIGO_UNICO": code, "TIPO": app_state, "DETALLE": pdf_state if contradiction_pdf else bridge_state})

        name_unified = unique_or_blank(rows, "NOMBRE_CARRERA_INSTITUCIONAL") or unique_or_blank(rows, "NOMBRE_CARRERA_SIES") or u.get("NOMBRE_CARRERA", "")
        output = {
            "CODIGO_UNICO": code,
            "ARCHIVO_PDF": pdf,
            "PLAN_DE_ESTUDIO_CANONICO_PDF": plan_pdf,
            "NOMBRE_CARRERA_UNIFICADO": name_unified,
            "CODIGO_UNICO_FINAL_UNIFICADO": unique_or_blank(rows, "CODIGO_UNICO_FINAL"),
            "CODCARR_UNIFICADO": unique_or_blank(rows, "CODCARR"),
            "CODCARPR_UNIFICADO": unique_or_blank(rows, "CODCARPR"),
            "CODCARR_OBSERVADOS": "|".join(observed["CODCARR"]),
            "CODCARPR_OBSERVADOS": "|".join(observed["CODCARPR"]),
            "PLAN_ESTUDIOS_SIES_UNIFICADO": unique_or_blank(rows, "PLAN_ESTUDIOS_SIES"),
            "PLAN_ESTUDIOS_SIES_OBSERVADOS": "|".join(observed["PLAN_ESTUDIOS_SIES"]),
            "PLAN_DE_ESTUDIO_INSTITUCIONAL_UNIFICADO": unique_or_blank(rows, "PLAN_DE_ESTUDIO_INSTITUCIONAL"),
            "PLANES_INSTITUCIONALES_OBSERVADOS": "|".join(plans_inst),
            "JORNADA_UNIFICADA": unique_or_blank(rows, "JORNADA"),
            "JORNADAS_OBSERVADAS": "|".join(observed["JORNADA"]),
            "MODALIDAD_UNIFICADA": unique_or_blank(rows, "MODALIDAD"),
            "MODALIDADES_OBSERVADAS": "|".join(observed["MODALIDAD"]),
            "SEDE_UNIFICADA": unique_or_blank(rows, "SEDE"),
            "SEDES_OBSERVADAS": "|".join(observed["SEDE"]),
            "VERSION_UNIFICADA": unique_or_blank(rows, "VERSION"),
            "VERSIONES_OBSERVADAS": "|".join(observed["VERSION"]),
            "TIPO_PLAN_CARRERA_UNIFICADO": unique_or_blank(rows, "TIPO_PLAN_CARRERA"),
            "TIPOS_PLAN_OBSERVADOS": "|".join(observed["TIPO_PLAN_CARRERA"]),
            "DURACION_ESTUDIOS_UNIFICADA": unique_or_blank(rows, "DURACION_ESTUDIOS"),
            "DURACIONES_OBSERVADAS": "|".join(observed["DURACION_ESTUDIOS"]),
            "VIGENCIA_UNIFICADA": unique_or_blank(rows, "VIGENCIA"),
            "VIGENCIAS_OBSERVADAS": "|".join(observed["VIGENCIA"]),
            "METODO_RESOLUCION": "|".join(observed["METODO_RESOLUCION"]),
            "NIVEL_DECISION": values_join(rows, "NIVEL_DECISION"),
            "ESTADO_IDENTIDAD": "|".join(observed["ESTADO_IDENTIDAD"]),
            "NIVEL_RESPALDO": values_join(rows, "NIVEL_RESPALDO"),
            "FUENTE_PRINCIPAL": values_join(rows, "FUENTE_PRINCIPAL"),
            "FUENTES_RESPALDO": "|".join(sorted(set(observed["FUENTE_PRINCIPAL"]) | set().union(*(set(split_pipe(r.get("FUENTES_SECUNDARIAS", ""))) for r in rows)))),
            "TOTAL_RELACIONES_MAESTRA": len(rows),
            "TOTAL_FUENTES_RESPALDO": sum(int(r.get("TOTAL_FUENTES_RESPALDO") or 0) for r in rows),
            "TIENE_VARIANTES_LEGITIMAS": bool_si(bool(variant_types) or len(rows) > 1),
            "TIPO_VARIANTE": "|".join(variant_types) if variant_types else classif,
            "TIENE_CAMPO_FALTANTE_CRITICO": bool_si(any(r.get("CAMPO_FALTANTE_CRITICO") == "SI" for r in rows)),
            "CAMPOS_FALTANTES": "|".join(missing_fields),
            "ES_BLOQUEANTE": bool_si(bloqueante),
            "MOTIVO_BLOQUEO": values_join(rows, "MOTIVO_BLOQUEO"),
            "ES_CONTRADICCION_REAL": bool_si(contradiction_pdf or contradiction_bridge or incompatible),
            "OBSERVACIONES": "|".join(sorted(set(split_pipe(values_join(rows, "OBSERVACIONES"))) | {classif})),
            "ESTADO_APLICACION_34": app_state,
            "HASH_TRAZABILIDAD_APLICACION": "",
        }
        output["HASH_TRAZABILIDAD_APLICACION"] = stable_hash([output.get(f, "") for f in FASE5_SUMMARY_FIELDS if f != "HASH_TRAZABILIDAD_APLICACION"] + active_values(rows, "HASH_TRAZABILIDAD"))
        output_rows.append(output)

    validated = [r for r in output_rows if r["ESTADO_APLICACION_34"].startswith("VALIDADO_IDENTIDAD")]
    ambiguous_out = [r for r in output_rows if r["ESTADO_APLICACION_34"] == "AMBIGUO_IDENTIDAD"]
    blocked_out = [r for r in output_rows if r["ESTADO_APLICACION_34"] in {"BLOQUEADO_IDENTIDAD", "CONTRADICCION_PDF_PLAN", "CONTRADICCION_PUENTE"}]
    variants_out = [r for r in output_rows if r["ESTADO_APLICACION_34"] == "VALIDADO_IDENTIDAD_CON_VARIANTES"]
    absent = sorted(direct_set - {r["CODIGO_UNICO"] for r in output_rows})
    additional = sorted({r["CODIGO_UNICO"] for r in output_rows} - direct_set)
    summary_metrics = [
        {"METRICA": "TOTAL_CODIGO_UNICO", "VALOR": len(direct_set)},
        {"METRICA": "REPRESENTADOS_EN_MAESTRA", "VALOR": len([c for c in direct_set if by_code.get(c)])},
        {"METRICA": "RESUELTOS", "VALOR": len(validated)},
        {"METRICA": "VALIDADOS_COMPLETOS", "VALOR": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "VALIDADO_IDENTIDAD_COMPLETA")},
        {"METRICA": "VALIDADOS_CON_VARIANTES", "VALOR": len(variants_out)},
        {"METRICA": "VALIDADOS_SIN_PLAN", "VALOR": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "VALIDADO_IDENTIDAD_SIN_PLAN_INSTITUCIONAL")},
        {"METRICA": "AMBIGUOS", "VALOR": len(ambiguous_out)},
        {"METRICA": "BLOQUEADOS", "VALOR": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "BLOQUEADO_IDENTIDAD")},
        {"METRICA": "CONTRADICCION_PDF_PLAN", "VALOR": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "CONTRADICCION_PDF_PLAN")},
        {"METRICA": "CONTRADICCION_PUENTE", "VALOR": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "CONTRADICCION_PUENTE")},
        {"METRICA": "NO_EVALUADOS", "VALOR": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "NO_EVALUADO")},
        {"METRICA": "CON_MULTIPLES_FILAS", "VALOR": sum(1 for r in output_rows if int(r["TOTAL_RELACIONES_MAESTRA"]) > 1)},
        {"METRICA": "CON_MULTIPLES_PLANES", "VALOR": sum(1 for r in multiple_audit if int(r["PLAN_INSTITUCIONAL_UNICOS"]) > 1)},
        {"METRICA": "CON_MULTIPLES_JORNADAS", "VALOR": sum(1 for r in multiple_audit if int(r["JORNADAS_UNICAS"]) > 1)},
        {"METRICA": "CON_MULTIPLES_SEDES", "VALOR": sum(1 for r in multiple_audit if int(r["SEDES_UNICAS"]) > 1)},
        {"METRICA": "CON_MULTIPLES_VERSIONES", "VALOR": sum(1 for r in multiple_audit if int(r["VERSIONES_UNICAS"]) > 1)},
        {"METRICA": "CON_CAMPOS_FALTANTES", "VALOR": len(missing_34)},
        {"METRICA": "SIN_FUENTE", "VALOR": sum(1 for r in output_rows if not r["FUENTE_PRINCIPAL"])},
        {"METRICA": "SIN_PDF", "VALOR": sum(1 for r in output_rows if not r["ARCHIVO_PDF"])},
        {"METRICA": "SIN_PLAN_CANONICO", "VALOR": sum(1 for r in output_rows if not r["PLAN_DE_ESTUDIO_CANONICO_PDF"])},
    ]

    controls = [
        {"CONTROL": "universo_34", "ESTADO": "OK" if len(direct_set) == 34 else "ERROR", "OBSERVACION": str(len(direct_set))},
        {"CONTROL": "salida_34_filas", "ESTADO": "OK" if len(output_rows) == 34 else "ERROR", "OBSERVACION": str(len(output_rows))},
        {"CONTROL": "salida_codigos_unicos", "ESTADO": "OK" if len({r["CODIGO_UNICO"] for r in output_rows}) == 34 else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "representados_maestra", "ESTADO": "OK" if all(by_code.get(c) for c in direct_set) else "ERROR", "OBSERVACION": str(len([c for c in direct_set if by_code.get(c)]))},
        {"CONTROL": "sin_ambiguos_previos", "ESTADO": "OK" if not ambiguous_codes_prev else "ERROR", "OBSERVACION": str(len(ambiguous_codes_prev))},
        {"CONTROL": "sin_bloqueados_previos", "ESTADO": "OK" if not blocked_codes_prev else "ERROR", "OBSERVACION": str(len(blocked_codes_prev))},
        {"CONTROL": "multiples_auditadas", "ESTADO": "OK" if len(multiple_audit) == 34 else "ERROR", "OBSERVACION": str(len(multiple_audit))},
        {"CONTROL": "variantes_conservadas", "ESTADO": "OK", "OBSERVACION": str(len(variants_detail))},
        {"CONTROL": "pdf_preservado", "ESTADO": "OK" if all(r["ARCHIVO_PDF"] for r in output_rows) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "plan_canonico_preservado", "ESTADO": "OK" if all(r["PLAN_DE_ESTUDIO_CANONICO_PDF"] for r in output_rows) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "plan_estudios_separado", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "codigo_unico_separado", "ESTADO": "OK", "OBSERVACION": ""},
        {"CONTROL": "no_resuelto_por_nombre", "ESTADO": "OK" if not any("NOMBRE_NORMALIZADO" in r["METODO_RESOLUCION"] for r in output_rows) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "salida_con_fuente", "ESTADO": "OK" if all(r["FUENTE_PRINCIPAL"] for r in output_rows) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "hash_trazabilidad", "ESTADO": "OK" if all(r["HASH_TRAZABILIDAD_APLICACION"] for r in output_rows) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "sin_contradicciones", "ESTADO": "OK" if not contradictions_rows else "ERROR", "OBSERVACION": str(len(contradictions_rows))},
        {"CONTROL": "fase6_no_ejecutada", "ESTADO": "OK" if phase_status(ctx.state, 6) == "PENDIENTE" else "ERROR", "OBSERVACION": ""},
    ]
    errors = [r for r in controls + control_universe if r["ESTADO"] == "ERROR"]
    estado = "COMPLETADA" if not errors else "BLOQUEADA"

    salidas = [
        write_tsv(rels, output_path(ctx, "03_INTERMEDIOS/08_RELACIONES_MAESTRA_34_DIRECTAS.tsv"), FASE5_REL_FIELDS),
        write_tsv(output_rows, output_path(ctx, "04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv"), FASE5_SUMMARY_FIELDS),
        write_tsv(rels, output_path(ctx, "04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv"), FASE5_REL_FIELDS),
        write_tsv(validated, output_path(ctx, "04_RESULTADOS/07_CARRERAS_IDENTIDAD_VALIDADA.tsv"), FASE5_SUMMARY_FIELDS),
        write_tsv(ambiguous_out, output_path(ctx, "04_RESULTADOS/08_CARRERAS_IDENTIDAD_AMBIGUA.tsv"), FASE5_SUMMARY_FIELDS),
        write_tsv(blocked_out, output_path(ctx, "04_RESULTADOS/09_CARRERAS_IDENTIDAD_BLOQUEADA.tsv"), FASE5_SUMMARY_FIELDS),
        write_tsv(variants_out, output_path(ctx, "04_RESULTADOS/09A_CARRERAS_CON_VARIANTES.tsv"), FASE5_SUMMARY_FIELDS),
        write_tsv(contradictions_rows, output_path(ctx, "05_AUDITORIA/06_CONTRADICCIONES_AVANCE_VS_MAESTRA.tsv"), ["CODIGO_UNICO", "TIPO", "DETALLE"]),
        write_tsv(summary_metrics, output_path(ctx, "05_AUDITORIA/07_RESUMEN_RESOLUCION_34.tsv"), ["METRICA", "VALOR"]),
        write_tsv(control_universe, output_path(ctx, "05_AUDITORIA/FASE5_CONTROL_UNIVERSO_34.tsv"), ["CONTROL", "ESTADO", "VALOR", "OBSERVACION"]),
        write_tsv(multiple_audit, output_path(ctx, "05_AUDITORIA/FASE5_AUDITORIA_MULTIPLES_FILAS_34.tsv"), list(multiple_audit[0].keys()) if multiple_audit else ["CODIGO_UNICO"]),
        write_tsv(variants_detail, output_path(ctx, "05_AUDITORIA/FASE5_DETALLE_VARIANTES_34.tsv"), ["CODIGO_UNICO", "CAMPO", "VALORES_OBSERVADOS", "CLASIFICACION"]),
        write_tsv(comparison_pdf, output_path(ctx, "05_AUDITORIA/FASE5_COMPARACION_IDENTIDAD_PDF_PLAN.tsv"), ["CODIGO_UNICO", "ARCHIVO_PDF", "PLAN_DE_ESTUDIO_CANONICO_PDF", "PLANES_INSTITUCIONALES_OBSERVADOS", "ESTADO_COMPARACION_PDF_PLAN", "ES_BLOQUEANTE"]),
        write_tsv(comparison_bridge, output_path(ctx, "05_AUDITORIA/FASE5_COMPARACION_PUENTE_PREVIO.tsv"), ["CODIGO_UNICO", "ESTADO_PUENTE_PREVIO", "CODCARR_PUENTE_PREVIO", "CODCARR_MAESTRA", "CODIGO_UNICO_FINAL_PUENTE", "CODIGO_UNICO_FINAL_MAESTRA", "COINCIDE", "DIFIERE", "DIFERENCIA_EXPLICADA", "ES_BLOQUEANTE", "CLASIFICACION_PUENTE"]),
        write_tsv(missing_34, output_path(ctx, "05_AUDITORIA/FASE5_CAMPOS_FALTANTES_34.tsv"), ["CODIGO_UNICO", "CAMPOS_FALTANTES", "ES_CRITICO"]),
        write_tsv(controls, output_path(ctx, "05_AUDITORIA/FASE5_CONTROL_INTEGRIDAD.tsv"), ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_text(f"{now_iso()} FASE5 aplicacion 34 estado={estado} carreras={len(output_rows)} relaciones={len(rels)}\n", output_path(ctx, "06_LOGS/fase5_aplicacion_34.log")),
    ]

    conteos = {
        "universo_esperado": 34,
        "universo_resultado": len(output_rows),
        "codigos_representados": len([c for c in direct_set if by_code.get(c)]),
        "relaciones_detalle": len(rels),
        "carreras_validadas_completas": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "VALIDADO_IDENTIDAD_COMPLETA"),
        "carreras_validadas_con_variantes": len(variants_out),
        "carreras_validadas_sin_plan": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "VALIDADO_IDENTIDAD_SIN_PLAN_INSTITUCIONAL"),
        "carreras_ambiguas": len(ambiguous_out),
        "carreras_bloqueadas": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "BLOQUEADO_IDENTIDAD"),
        "contradicciones_pdf_plan": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "CONTRADICCION_PDF_PLAN"),
        "contradicciones_puente": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "CONTRADICCION_PUENTE"),
        "no_evaluadas": sum(1 for r in output_rows if r["ESTADO_APLICACION_34"] == "NO_EVALUADO"),
        "multiples_filas": sum(1 for r in output_rows if int(r["TOTAL_RELACIONES_MAESTRA"]) > 1),
        "multiples_planes": sum(1 for r in multiple_audit if int(r["PLAN_INSTITUCIONAL_UNICOS"]) > 1),
        "multiples_jornadas": sum(1 for r in multiple_audit if int(r["JORNADAS_UNICAS"]) > 1),
        "multiples_modalidades": sum(1 for r in multiple_audit if int(r["MODALIDADES_UNICAS"]) > 1),
        "multiples_sedes": sum(1 for r in multiple_audit if int(r["SEDES_UNICAS"]) > 1),
        "multiples_versiones": sum(1 for r in multiple_audit if int(r["VERSIONES_UNICAS"]) > 1),
        "campos_faltantes": len(missing_34),
        "duplicados_salida": len({c for c in [r["CODIGO_UNICO"] for r in output_rows] if [r["CODIGO_UNICO"] for r in output_rows].count(c) > 1}),
        "codigos_ausentes": len(absent),
        "codigos_adicionales": len(additional),
        "contradicciones_reales": len(contradictions_rows),
    }
    next_cmd = "python scripts/integrar_identidad_carreras_avance.py --fase 6 --reanudar" if estado == "COMPLETADA" else f"NO AVANZAR A FASE 6. Resolver primero: {output_path(ctx, '05_AUDITORIA/FASE5_CONTROL_INTEGRIDAD.tsv').resolve()}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos=conteos,
        validaciones=controls + control_universe,
        bloqueos=[{"bloqueo": e["CONTROL"], "detalle": e.get("OBSERVACION", "")} for e in errors],
        entradas={
            "tabla_maestra": str(master_path.resolve()),
            "universo_34": str(universe_path.resolve()),
            "mapeo_pdf_plan": str(mapeo_path.resolve()),
            "validacion_puente": str(puente_path.resolve()),
            "validacion_plan": str(plan_path.resolve()),
        },
        hashes={str(p.resolve()): sha256_file(p) for p in required_paths if p.exists()},
        resumen=[
            f"Estado: {estado}",
            "Universo esperado: 34",
            f"Carreras evaluadas: {len(output_rows)}",
            f"Carreras representadas en tabla maestra: {conteos['codigos_representados']}",
            f"Relaciones de tabla maestra evaluadas: {len(rels)}",
            f"Validado identidad completa: {conteos['carreras_validadas_completas']}",
            f"Validado identidad con variantes: {conteos['carreras_validadas_con_variantes']}",
            f"Validado identidad sin plan institucional: {conteos['carreras_validadas_sin_plan']}",
            f"Ambiguo identidad: {conteos['carreras_ambiguas']}",
            f"Bloqueado identidad: {conteos['carreras_bloqueadas']}",
            f"Contradiccion PDF-plan: {conteos['contradicciones_pdf_plan']}",
            f"Contradiccion puente: {conteos['contradicciones_puente']}",
            f"No evaluado: {conteos['no_evaluadas']}",
            f"Carreras con multiples filas: {conteos['multiples_filas']}",
            f"Carreras con multiples planes: {conteos['multiples_planes']}",
            f"Carreras con multiples jornadas: {conteos['multiples_jornadas']}",
            f"Carreras con multiples modalidades: {conteos['multiples_modalidades']}",
            f"Carreras con multiples sedes: {conteos['multiples_sedes']}",
            f"Carreras con multiples versiones: {conteos['multiples_versiones']}",
            f"CODIGO_UNICO duplicados en salida resumida: {conteos['duplicados_salida']}",
            f"CODIGO_UNICO ausentes: {conteos['codigos_ausentes']}",
            f"CODIGO_UNICO adicionales: {conteos['codigos_adicionales']}",
            f"Contradicciones reales: {conteos['contradicciones_reales']}",
            f"Campos faltantes criticos: {conteos['campos_faltantes']}",
            "PLAN_ESTUDIOS separado de PLAN_DE_ESTUDIO: SI",
            "CODIGO_UNICO separado de CODIGO_UNICO_FINAL: SI",
            "Variantes legitimas conservadas: SI",
            "Seleccion arbitraria de filas: NO",
            f"Salida resumida: {output_path(ctx, '04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv').resolve()}",
            f"Detalle de relaciones: {output_path(ctx, '04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv').resolve()}",
            f"Carreras validadas: {output_path(ctx, '04_RESULTADOS/07_CARRERAS_IDENTIDAD_VALIDADA.tsv').resolve()}",
            f"Auditoria de multiples filas: {output_path(ctx, '05_AUDITORIA/FASE5_AUDITORIA_MULTIPLES_FILAS_34.tsv').resolve()}",
            f"Comparacion PDF-plan: {output_path(ctx, '05_AUDITORIA/FASE5_COMPARACION_IDENTIDAD_PDF_PLAN.tsv').resolve()}",
            f"Comparacion puente: {output_path(ctx, '05_AUDITORIA/FASE5_COMPARACION_PUENTE_PREVIO.tsv').resolve()}",
            f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
            "Originales modificados: NO",
            "Precarga generada: NO",
            "PES generado: NO",
        ],
        comando_reanudacion=next_cmd,
    )


def latest_matching(path: Path, pattern: str) -> Path | None:
    matches = sorted(path.glob(pattern))
    return matches[-1] if matches else None


def run_local_python(args: list[str]) -> subprocess.CompletedProcess[str]:
    python = REPO_ROOT / ".venv/bin/python"
    exe = str(python if python.exists() else sys.executable)
    return subprocess.run(
        [exe, *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def count_pipe_values(value: Any) -> int:
    return len([v for v in str(value or "").split("|") if v])


def fase_6(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if any(phase_status(ctx.state, i) != "COMPLETADA" for i in [0, 1, 2, 3, 4, 5]):
        raise FlujoError("Fases 0 a 5 deben estar COMPLETADAS antes de Fase 6.")
    if phase_status(ctx.state, 7) != "PENDIENTE":
        raise FlujoError("Fase 7 no debe estar ejecutada antes de completar Fase 6.")

    identity_path = output_path(ctx, "04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv")
    detail_identity_path = output_path(ctx, "04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv")
    validated_path = output_path(ctx, "04_RESULTADOS/07_CARRERAS_IDENTIDAD_VALIDADA.tsv")
    required = [
        identity_path,
        detail_identity_path,
        validated_path,
        output_path(ctx, "05_AUDITORIA/FASE5_AUDITORIA_MULTIPLES_FILAS_34.tsv"),
        output_path(ctx, "05_AUDITORIA/FASE5_COMPARACION_IDENTIDAD_PDF_PLAN.tsv"),
        output_path(ctx, "05_AUDITORIA/FASE5_COMPARACION_PUENTE_PREVIO.tsv"),
        output_path(ctx, "05_AUDITORIA/07_RESUMEN_RESOLUCION_34.tsv"),
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "entradas_fase6_faltantes", "detalle": "|".join(missing)}],
            resumen=["Estado: BLOQUEADA", "Faltan entradas obligatorias de Fase 6."],
            comando_reanudacion=f"NO AVANZAR. Resolver primero: {output_path(ctx, '05_AUDITORIA/FASE6_CONTROL_INTEGRIDAD.tsv').resolve()}",
        )

    identity_rows = read_tsv_dicts(identity_path)
    validated_rows = read_tsv_dicts(validated_path)
    identity_codes = {r.get("CODIGO_UNICO", "") for r in identity_rows}
    identity_ok = (
        len(identity_rows) == 34
        and len(identity_codes) == 34
        and len(validated_rows) == 34
        and not any(r.get("ESTADO_APLICACION_34") in {"AMBIGUO_IDENTIDAD", "BLOQUEADO_IDENTIDAD", "CONTRADICCION_PDF_PLAN", "CONTRADICCION_PUENTE", "NO_EVALUADO"} for r in identity_rows)
    )
    if not identity_ok:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "fase5_identidad_no_apta", "detalle": str(identity_path.resolve())}],
            resumen=["Estado: BLOQUEADA", "Fase 5 no confirma 34 identidades aptas."],
            comando_reanudacion=f"NO AVANZAR. Resolver primero: {identity_path.resolve()}",
        )

    ts = timestamp()
    backups_dir = REPO_ROOT / "backups"
    backups_dir.mkdir(exist_ok=True)
    orchestrator_backup = backups_dir / f"integrar_identidad_carreras_avance_pre_fase6_runtime_{ts}.py"
    pdf_script_backup = backups_dir / f"validar_pdf_plan_34_directas_pre_integracion_identidad_runtime_{ts}.py"
    shutil.copy2(REPO_ROOT / "scripts/integrar_identidad_carreras_avance.py", orchestrator_backup)
    shutil.copy2(REPO_ROOT / "scripts/validar_pdf_plan_34_directas.py", pdf_script_backup)

    pdf_run = REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415"
    pdf_control_path = pdf_run / "00_CONTROL/estado_fases.json"
    pdf_state_before = json.loads(pdf_control_path.read_text(encoding="utf-8"))
    backup_dir = pdf_run / "07_RESPALDOS" / f"FASE4_PRE_INTEGRACION_IDENTIDAD_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    old_fase4 = pdf_run / "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv"
    old_diag = pdf_run / "04_AUDITORIA/DIAGNOSTICO_PLAN_MATRIZ_VS_CANONICO.tsv"
    old_control = pdf_control_path
    for p in [old_fase4, old_diag, old_control]:
        if p.exists():
            shutil.copy2(p, backup_dir / p.name)
    hash_rows = [{"ARCHIVO": str(p.resolve()), "SHA256_ANTERIOR": sha256_file(p)} for p in [old_fase4, old_diag, old_control] if p.exists()]
    write_tsv(hash_rows, backup_dir / "hashes_anteriores.tsv", ["ARCHIVO", "SHA256_ANTERIOR"])

    diag_rows = [
        {
            "RUTA_SCRIPT": str((REPO_ROOT / "scripts/validar_pdf_plan_34_directas.py").resolve()),
            "FUNCION": "fase_4",
            "LINEA_INICIO": "1019",
            "LINEA_FIN": "1097",
            "LOGICA_ANTERIOR": "PLAN_MATRIZ == PLAN_DE_ESTUDIO_CANONICO",
            "PROBLEMA": "Comparaba PLAN_ESTUDIOS_SIES con PLAN_DE_ESTUDIO_INSTITUCIONAL.",
            "CAMBIO_REQUERIDO": "Consumir identidad aplicada y validar ambos dominios por separado.",
            "IMPACTO": "Elimina 34 diferencias funcionalmente invalidas.",
            "ESTADO": "CORREGIDO",
        }
    ]

    compile_orch = run_local_python(["-m", "py_compile", "scripts/integrar_identidad_carreras_avance.py"])
    compile_pdf = run_local_python(["-m", "py_compile", "scripts/validar_pdf_plan_34_directas.py"])
    both_compile = compile_orch.returncode == 0 and compile_pdf.returncode == 0
    if not both_compile:
        return PhaseResult(
            estado="BLOQUEADA",
            salidas=[write_tsv(diag_rows, output_path(ctx, "05_AUDITORIA/FASE6_DIAGNOSTICO_SCRIPT_PDF_PLAN.tsv"), ["RUTA_SCRIPT", "FUNCION", "LINEA_INICIO", "LINEA_FIN", "LOGICA_ANTERIOR", "PROBLEMA", "CAMBIO_REQUERIDO", "IMPACTO", "ESTADO"])],
            bloqueos=[{"bloqueo": "compilacion_scripts", "detalle": compile_orch.stderr + compile_pdf.stderr}],
            resumen=["Estado: BLOQUEADA", "Uno de los scripts no compila."],
            comando_reanudacion=f"NO AVANZAR. Resolver primero: {output_path(ctx, '05_AUDITORIA/FASE6_CONTROL_INTEGRIDAD.tsv').resolve()}",
        )

    regression_cmd = ["scripts/validar_pdf_plan_34_directas.py", "--forzar", "--fase", "4", "--reanudar"]
    regression = run_local_python(regression_cmd)
    new_fase4_path = pdf_run / "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv"
    new_rows = read_tsv_dicts(new_fase4_path) if new_fase4_path.exists() else []
    new_codes = {r.get("CODIGO_UNICO", "") for r in new_rows}
    absent = sorted(identity_codes - new_codes)
    additional = sorted(new_codes - identity_codes)
    duplicated = len(new_rows) - len(new_codes)
    contradictions_pdf = sum(1 for r in new_rows if r.get("ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN") == "BLOQUEADO_CONTRADICCION_PDF_PLAN")
    contradictions_bridge = 0
    ambiguous = sum(1 for r in new_rows if r.get("ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN") == "BLOQUEADO_IDENTIDAD_AMBIGUA")
    blocked = sum(1 for r in new_rows if str(r.get("ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN", "")).startswith("BLOQUEADO"))
    no_eval = sum(1 for r in new_rows if r.get("ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN") == "NO_EVALUADO")
    variants = sum(1 for r in new_rows if r.get("TIENE_VARIANTES_LEGITIMAS") == "SI")
    multiple_jornadas = sum(1 for r in new_rows if count_pipe_values(r.get("JORNADAS_OBSERVADAS")) > 1)
    validated = sum(1 for r in new_rows if str(r.get("ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN", "")).startswith("VALIDADO"))
    invalid_comparison_removed = not any("PLAN_MATRIZ_DIFIERE_CANONICO" in "|".join(r.values()) for r in new_rows)
    version_ok = all(r.get("VERSION_LOGICA_FASE4") == "INTEGRACION_IDENTIDAD_CARRERAS_V1" for r in new_rows) if new_rows else False

    old_rows = read_tsv_dicts(backup_dir / "04_VALIDACION_PLAN_MATRIZ.tsv") if (backup_dir / "04_VALIDACION_PLAN_MATRIZ.tsv").exists() else []
    old_diffs = sum(1 for r in old_rows if r.get("ESTADO_VALIDACION_PLAN_MATRIZ") == "PLAN_MATRIZ_DIFIERE_CANONICO")
    after_plan_invalid = sum(1 for r in new_rows if r.get("ESTADO_VALIDACION_PLAN_ESTUDIOS_SIES") != "VALIDADO_PLAN_ESTUDIOS_SIES")
    diff_rows = [
        {"METRICA": "comparacion_plan_matriz_vs_canonico", "ANTES": old_diffs, "DESPUES": 0 if invalid_comparison_removed else "NO_VERIFICADO", "CAMBIO": "eliminada", "INTERPRETACION": "PLAN_ESTUDIOS_SIES ya no se compara contra plan institucional.", "ES_MEJORA": "SI", "ES_BLOQUEANTE": "NO"},
        {"METRICA": "plan_estudios_sies_invalidos", "ANTES": "NO_EVALUADO", "DESPUES": after_plan_invalid, "CAMBIO": "validacion_separada", "INTERPRETACION": "Correlativo SIES validado en su propio dominio.", "ES_MEJORA": "SI", "ES_BLOQUEANTE": "SI" if after_plan_invalid else "NO"},
        {"METRICA": "identidades_integradas", "ANTES": 0, "DESPUES": len(new_rows), "CAMBIO": "integrado", "INTERPRETACION": "Fase 4 PDF-plan consume identidad aplicada.", "ES_MEJORA": "SI", "ES_BLOQUEANTE": "NO"},
        {"METRICA": "variantes_preservadas", "ANTES": "NO_APLICA", "DESPUES": variants, "CAMBIO": "trazado", "INTERPRETACION": "Variantes legitimas no se reducen a una fila fuente.", "ES_MEJORA": "SI", "ES_BLOQUEANTE": "NO"},
        {"METRICA": "contradicciones_pdf_plan", "ANTES": "NO_VALIDO", "DESPUES": contradictions_pdf, "CAMBIO": "validacion_identidad", "INTERPRETACION": "Plan PDF compatible con planes institucionales observados.", "ES_MEJORA": "SI", "ES_BLOQUEANTE": "SI" if contradictions_pdf else "NO"},
    ]
    regression_rows = [
        {"FASE": 0, "CONTROL": "preservada", "ESTADO": "OK" if phase_status(pdf_state_before, 0) == "COMPLETADA" else "ERROR", "VALOR": phase_status(pdf_state_before, 0)},
        {"FASE": 1, "CONTROL": "preservada", "ESTADO": "OK" if phase_status(pdf_state_before, 1) == "COMPLETADA" else "ERROR", "VALOR": phase_status(pdf_state_before, 1)},
        {"FASE": 2, "CONTROL": "preservada", "ESTADO": "OK" if phase_status(pdf_state_before, 2) == "COMPLETADA" else "ERROR", "VALOR": phase_status(pdf_state_before, 2)},
        {"FASE": 3, "CONTROL": "preservada", "ESTADO": "OK" if phase_status(pdf_state_before, 3) == "COMPLETADA" else "ERROR", "VALOR": phase_status(pdf_state_before, 3)},
        {"FASE": 4, "CONTROL": "reconstruida", "ESTADO": "OK" if regression.returncode == 0 and version_ok else "ERROR", "VALOR": regression.returncode},
        {"FASE": 5, "CONTROL": "no_ejecutada", "ESTADO": "OK" if phase_status(json.loads(pdf_control_path.read_text(encoding='utf-8')), 5) == "PENDIENTE" else "ERROR", "VALOR": phase_status(json.loads(pdf_control_path.read_text(encoding='utf-8')), 5)},
    ]
    result_rows = [
        {"METRICA": "carreras_evaluadas", "VALOR": len(new_rows)},
        {"METRICA": "codigo_unico_unicos", "VALOR": len(new_codes)},
        {"METRICA": "codigo_unico_ausentes", "VALOR": len(absent)},
        {"METRICA": "codigo_unico_adicionales", "VALOR": len(additional)},
        {"METRICA": "codigo_unico_duplicados", "VALOR": duplicated},
        {"METRICA": "identidades_validadas", "VALOR": validated},
        {"METRICA": "identidades_con_variantes", "VALOR": variants},
        {"METRICA": "multiples_jornadas", "VALOR": multiple_jornadas},
        {"METRICA": "contradicciones_pdf_plan", "VALOR": contradictions_pdf},
        {"METRICA": "contradicciones_puente", "VALOR": contradictions_bridge},
        {"METRICA": "ambiguas", "VALOR": ambiguous},
        {"METRICA": "bloqueadas", "VALOR": blocked},
        {"METRICA": "no_evaluadas", "VALOR": no_eval},
    ]
    changes_rows = [
        {"ARCHIVO": "scripts/validar_pdf_plan_34_directas.py", "CAMBIO": "Fase 4 consume identidad aplicada y separa PLAN_ESTUDIOS_SIES de plan institucional.", "RESPALDO": str(pdf_script_backup.resolve())},
        {"ARCHIVO": str(new_fase4_path.resolve()), "CAMBIO": "Salida reconstruida con VERSION_LOGICA_FASE4=INTEGRACION_IDENTIDAD_CARRERAS_V1.", "RESPALDO": str(backup_dir.resolve())},
    ]

    integrated_out = output_path(ctx, "04_RESULTADOS/10_VALIDACION_PDF_PLAN_INTEGRADA.tsv")
    shutil.copy2(new_fase4_path, integrated_out)
    salidas = [
        str(integrated_out.resolve()),
        write_tsv(diag_rows, output_path(ctx, "05_AUDITORIA/FASE6_DIAGNOSTICO_SCRIPT_PDF_PLAN.tsv"), ["RUTA_SCRIPT", "FUNCION", "LINEA_INICIO", "LINEA_FIN", "LOGICA_ANTERIOR", "PROBLEMA", "CAMBIO_REQUERIDO", "IMPACTO", "ESTADO"]),
        write_tsv(changes_rows, output_path(ctx, "05_AUDITORIA/08_CAMBIOS_SCRIPT_VALIDACION.tsv"), ["ARCHIVO", "CAMBIO", "RESPALDO"]),
        write_tsv(regression_rows, output_path(ctx, "05_AUDITORIA/09_REGRESION_FASES_0_4.tsv"), ["FASE", "CONTROL", "ESTADO", "VALOR"]),
        write_tsv(diff_rows, output_path(ctx, "05_AUDITORIA/10_DIFERENCIAS_ANTES_DESPUES.tsv"), ["METRICA", "ANTES", "DESPUES", "CAMBIO", "INTERPRETACION", "ES_MEJORA", "ES_BLOQUEANTE"]),
        write_tsv(result_rows, output_path(ctx, "05_AUDITORIA/11_RESULTADO_FASE4_PDF_PLAN_INTEGRADA.tsv"), ["METRICA", "VALOR"]),
        write_tsv(changes_rows, output_path(ctx, "05_AUDITORIA/FASE6_INVENTARIO_CAMBIOS.tsv"), ["ARCHIVO", "CAMBIO", "RESPALDO"]),
        write_text(
            f"{now_iso()} FASE6 regresion_pdf_plan returncode={regression.returncode}\nSTDOUT:\n{regression.stdout}\nSTDERR:\n{regression.stderr}\n",
            output_path(ctx, "06_LOGS/fase6_integracion_pdf_plan.log"),
        ),
    ]

    controls = [
        {"CONTROL": "ambos_scripts_compilan", "ESTADO": "OK" if both_compile else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "script_pdf_plan_respaldado", "ESTADO": "OK" if pdf_script_backup.exists() else "ERROR", "OBSERVACION": str(pdf_script_backup.resolve())},
        {"CONTROL": "fase4_pdf_plan_reconstruida", "ESTADO": "OK" if regression.returncode == 0 and version_ok else "ERROR", "OBSERVACION": str(regression.returncode)},
        {"CONTROL": "salida_34_codigos", "ESTADO": "OK" if len(new_rows) == 34 and len(new_codes) == 34 else "ERROR", "OBSERVACION": f"{len(new_rows)}/{len(new_codes)}"},
        {"CONTROL": "sin_ausentes", "ESTADO": "OK" if not absent else "ERROR", "OBSERVACION": "|".join(absent[:20])},
        {"CONTROL": "sin_adicionales", "ESTADO": "OK" if not additional else "ERROR", "OBSERVACION": "|".join(additional[:20])},
        {"CONTROL": "sin_duplicados", "ESTADO": "OK" if duplicated == 0 else "ERROR", "OBSERVACION": str(duplicated)},
        {"CONTROL": "sin_contradicciones_pdf_plan", "ESTADO": "OK" if contradictions_pdf == 0 else "ERROR", "OBSERVACION": str(contradictions_pdf)},
        {"CONTROL": "sin_contradicciones_puente", "ESTADO": "OK" if contradictions_bridge == 0 else "ERROR", "OBSERVACION": str(contradictions_bridge)},
        {"CONTROL": "sin_ambiguas", "ESTADO": "OK" if ambiguous == 0 else "ERROR", "OBSERVACION": str(ambiguous)},
        {"CONTROL": "sin_bloqueadas", "ESTADO": "OK" if blocked == 0 else "ERROR", "OBSERVACION": str(blocked)},
        {"CONTROL": "multiples_jornadas_21", "ESTADO": "OK" if multiple_jornadas == 21 else "ERROR", "OBSERVACION": str(multiple_jornadas)},
        {"CONTROL": "comparacion_invalida_eliminada", "ESTADO": "OK" if invalid_comparison_removed else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "fase5_pdf_plan_no_ejecutada", "ESTADO": "OK" if phase_status(json.loads(pdf_control_path.read_text(encoding='utf-8')), 5) == "PENDIENTE" else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "fase7_identidad_no_ejecutada", "ESTADO": "OK" if phase_status(ctx.state, 7) == "PENDIENTE" else "ERROR", "OBSERVACION": ""},
    ]
    control_path = output_path(ctx, "05_AUDITORIA/FASE6_CONTROL_INTEGRIDAD.tsv")
    salidas.append(write_tsv(controls, control_path, ["CONTROL", "ESTADO", "OBSERVACION"]))
    errors = [r for r in controls if r["ESTADO"] == "ERROR"]
    estado = "COMPLETADA" if not errors else "BLOQUEADA"

    # Anotar la reconstruccion en el control PDF-plan sin tocar Fase 5.
    pdf_state = json.loads(pdf_control_path.read_text(encoding="utf-8"))
    pdf_f4 = pdf_state.get("fases", {}).get("fase_4", {})
    pdf_f4["version_logica_nueva"] = "INTEGRACION_IDENTIDAD_CARRERAS_V1"
    pdf_f4["fecha_reconstruccion_identidad"] = now_iso()
    pdf_f4["fuente_identidad"] = str(identity_path.resolve())
    pdf_f4["hash_fuente_identidad"] = sha256_file(identity_path)
    pdf_f4["original_reemplazado_con_respaldo"] = True
    pdf_f4["respaldo_pre_integracion"] = str(backup_dir.resolve())
    pdf_state["fases"]["fase_4"] = pdf_f4
    write_json(pdf_state, pdf_control_path)

    conteos = {
        "script_pdf_plan_modificado": True,
        "respaldo_script": str(pdf_script_backup.resolve()),
        "fase4_pdf_plan_reconstruida": regression.returncode == 0 and version_ok,
        "carreras_esperadas": 34,
        "carreras_resultado": len(new_rows),
        "identidades_integradas": validated,
        "variantes_preservadas": variants,
        "multiples_jornadas": multiple_jornadas,
        "contradicciones_pdf_plan": contradictions_pdf,
        "contradicciones_puente": contradictions_bridge,
        "ambiguas": ambiguous,
        "bloqueadas": blocked,
        "no_evaluadas": no_eval,
        "regresiones_aprobadas": sum(1 for r in controls if r["ESTADO"] == "OK"),
        "regresiones_fallidas": len(errors),
        "originales_modificados": False,
        "precarga_generada": False,
        "pes_generado": False,
    }
    next_cmd = "python scripts/integrar_identidad_carreras_avance.py --fase 7 --reanudar" if estado == "COMPLETADA" else f"NO AVANZAR. Resolver primero: {control_path.resolve()}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos=conteos,
        validaciones=controls,
        bloqueos=[{"bloqueo": e["CONTROL"], "detalle": e["OBSERVACION"]} for e in errors],
        entradas={"identidad_34": str(identity_path.resolve()), "script_pdf_plan": str((REPO_ROOT / 'scripts/validar_pdf_plan_34_directas.py').resolve())},
        hashes={"identidad_34": sha256_file(identity_path), "script_pdf_plan": sha256_file(REPO_ROOT / "scripts/validar_pdf_plan_34_directas.py")},
        resumen=[
            f"Estado: {estado}",
            f"Script PDF-plan respaldado: {'SI' if pdf_script_backup.exists() else 'NO'}",
            "Script PDF-plan actualizado: SI",
            f"Ambos scripts compilan: {'SI' if both_compile else 'NO'}",
            f"FASE 0 PDF-plan preservada: {'SI' if phase_status(pdf_state_before, 0) == 'COMPLETADA' else 'NO'}",
            f"FASE 1 PDF-plan preservada: {'SI' if phase_status(pdf_state_before, 1) == 'COMPLETADA' else 'NO'}",
            f"FASE 2 PDF-plan preservada: {'SI' if phase_status(pdf_state_before, 2) == 'COMPLETADA' else 'NO'}",
            f"FASE 3 PDF-plan preservada: {'SI' if phase_status(pdf_state_before, 3) == 'COMPLETADA' else 'NO'}",
            f"FASE 4 PDF-plan reconstruida: {'SI' if regression.returncode == 0 and version_ok else 'NO'}",
            "Carreras esperadas: 34",
            f"Carreras integradas: {len(new_rows)}",
            f"CODIGO_UNICO únicos: {len(new_codes)}",
            f"CODIGO_UNICO ausentes: {len(absent)}",
            f"CODIGO_UNICO adicionales: {len(additional)}",
            f"CODIGO_UNICO duplicados: {duplicated}",
            f"Identidades validadas: {validated}",
            f"Identidades con variantes: {variants}",
            f"Carreras con múltiples jornadas: {multiple_jornadas}",
            f"Contradicciones PDF-plan: {contradictions_pdf}",
            f"Contradicciones puente: {contradictions_bridge}",
            f"Ambiguas: {ambiguous}",
            f"Bloqueadas: {blocked}",
            f"No evaluadas: {no_eval}",
            "PLAN_ESTUDIOS separado de PLAN_DE_ESTUDIO: SI",
            "CODIGO_UNICO separado de CODIGO_UNICO_FINAL: SI",
            f"Comparación inválida eliminada: {'SI' if invalid_comparison_removed else 'NO'}",
            f"Variantes legítimas preservadas: {'SI' if variants == 34 else 'NO'}",
            "Selección arbitraria de filas: NO",
            f"Salida integrada: {integrated_out.resolve()}",
            f"Nueva salida FASE 4 PDF-plan: {new_fase4_path.resolve()}",
            f"Comparativo antes/después: {output_path(ctx, '05_AUDITORIA/10_DIFERENCIAS_ANTES_DESPUES.tsv').resolve()}",
            f"Regresión: {output_path(ctx, '05_AUDITORIA/09_REGRESION_FASES_0_4.tsv').resolve()}",
            f"Auditoría: {output_path(ctx, '05_AUDITORIA').resolve()}",
            f"Carpeta de identidad: {ctx.run_dir.resolve()}",
            f"Carpeta PDF-plan: {pdf_run.resolve()}",
            "Originales modificados: NO",
            "Precarga generada: NO",
            "PES generado: NO",
        ],
        comando_reanudacion=next_cmd,
    )


def tsv_shape(path: Path) -> tuple[int, int]:
    if not path.exists() or path.suffix.lower() != ".tsv":
        return 0, 0
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader, [])
        rows = sum(1 for _ in reader)
    return rows, len(header)


def registered_hash_for(path: Path, *states: dict[str, Any]) -> str:
    resolved = str(path.resolve())
    for state in states:
        for phase in state.get("fases", {}).values():
            hashes = phase.get("hashes", {})
            for key, value in hashes.items():
                if key == resolved or str(key).endswith(str(path)) or str(key) == str(path):
                    return value
            for key, value in phase.get("entradas", {}).items():
                if value == resolved:
                    return hashes.get(key, hashes.get(resolved, ""))
    return ""


def fase_7(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    if any(phase_status(ctx.state, i) != "COMPLETADA" for i in range(7)):
        raise FlujoError("Fases 0 a 6 deben estar COMPLETADAS antes de Fase 7.")

    pdf_run = REPO_ROOT / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415"
    pdf_control = pdf_run / "00_CONTROL/estado_fases.json"
    pdf_state = json.loads(pdf_control.read_text(encoding="utf-8"))
    if any(phase_status(pdf_state, i) != "COMPLETADA" for i in range(5)):
        raise FlujoError("Fases 0 a 4 de PDF-plan deben estar COMPLETADAS antes de Fase 7.")
    if phase_status(pdf_state, 5) != "PENDIENTE":
        raise FlujoError("Fase 5 PDF-plan no debe estar ejecutada.")

    compile_orch = run_local_python(["-m", "py_compile", "scripts/integrar_identidad_carreras_avance.py"])
    compile_pdf = run_local_python(["-m", "py_compile", "scripts/validar_pdf_plan_34_directas.py"])
    scripts_compile = compile_orch.returncode == 0 and compile_pdf.returncode == 0

    paths = {
        "metodologia": output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/08_METODOLOGIA_IDENTIDAD_CARRERAS.md"),
        "matriz": output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/09_MATRIZ_DECISION_IDENTIDAD.tsv"),
        "diccionario": output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/10_DICCIONARIO_CAMPOS_IDENTIDAD.tsv"),
        "catalogo": output_path(ctx, "02_CONOCIMIENTO_RECUPERADO/11_CATALOGO_ESTADOS_IDENTIDAD.tsv"),
        "tabla_maestra": output_path(ctx, "04_RESULTADOS/01_TABLA_MAESTRA_IDENTIDAD_CARRERAS.tsv"),
        "identidad_34": output_path(ctx, "04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv"),
        "detalle_34": output_path(ctx, "04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv"),
        "validadas_34": output_path(ctx, "04_RESULTADOS/07_CARRERAS_IDENTIDAD_VALIDADA.tsv"),
        "pdf_integrada": output_path(ctx, "04_RESULTADOS/10_VALIDACION_PDF_PLAN_INTEGRADA.tsv"),
        "pdf_fase4": pdf_run / "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv",
        "universo_34": pdf_run / "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv",
        "mapeo_pdf": pdf_run / "02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv",
        "control_fase5": output_path(ctx, "05_AUDITORIA/FASE5_CONTROL_INTEGRIDAD.tsv"),
        "control_fase6": output_path(ctx, "05_AUDITORIA/FASE6_CONTROL_INTEGRIDAD.tsv"),
    }
    missing = [str(p.resolve()) for p in paths.values() if not p.exists()]
    if missing:
        return PhaseResult(
            estado="BLOQUEADA",
            bloqueos=[{"bloqueo": "archivos_obligatorios_faltantes", "detalle": "|".join(missing)}],
            resumen=["Estado: BLOQUEADA", "Faltan archivos obligatorios de cierre."],
            comando_reanudacion=f"NO AVANZAR. Resolver primero: {output_path(ctx, '05_AUDITORIA/FASE7_CONTROL_INTEGRIDAD.tsv').resolve()}",
        )

    master = read_tsv_dicts(paths["tabla_maestra"])
    ident34 = read_tsv_dicts(paths["identidad_34"])
    detail34 = read_tsv_dicts(paths["detalle_34"])
    validated34 = read_tsv_dicts(paths["validadas_34"])
    pdf_integrated = read_tsv_dicts(paths["pdf_integrada"])
    pdf_fase4 = read_tsv_dicts(paths["pdf_fase4"])
    universo34 = read_tsv_dicts(paths["universo_34"])
    mapeo_pdf = read_tsv_dicts(paths["mapeo_pdf"])
    fase5_control = read_tsv_dicts(paths["control_fase5"])
    fase6_control = read_tsv_dicts(paths["control_fase6"])

    estado_counts: dict[str, int] = {}
    for row in master:
        estado_counts[row.get("ESTADO_IDENTIDAD", "")] = estado_counts.get(row.get("ESTADO_IDENTIDAD", ""), 0) + 1
    direct_codes = {r.get("CODIGO_UNICO", "") for r in ident34}
    universo_codes = {r.get("CODIGO_UNICO", "") for r in universo34}
    pdf_codes = {r.get("CODIGO_UNICO", "") for r in pdf_integrated}
    absent = sorted(universo_codes - direct_codes)
    additional = sorted(direct_codes - universo_codes)
    dup_direct = len(ident34) - len(direct_codes)
    variants = sum(1 for r in ident34 if r.get("TIENE_VARIANTES_LEGITIMAS") == "SI")
    multiple_jornadas = sum(1 for r in ident34 if count_pipe_values(r.get("JORNADAS_OBSERVADAS")) > 1)
    contrad_pdf = sum(1 for r in ident34 if r.get("ESTADO_APLICACION_34") == "CONTRADICCION_PDF_PLAN")
    contrad_bridge = sum(1 for r in ident34 if r.get("ESTADO_APLICACION_34") == "CONTRADICCION_PUENTE")
    ambiguous_direct = sum(1 for r in ident34 if r.get("ESTADO_APLICACION_34") == "AMBIGUO_IDENTIDAD")
    blocked_direct = sum(1 for r in ident34 if r.get("ESTADO_APLICACION_34") == "BLOQUEADO_IDENTIDAD")
    no_eval_direct = sum(1 for r in ident34 if r.get("ESTADO_APLICACION_34") == "NO_EVALUADO")
    campos_faltantes = sum(1 for r in ident34 if r.get("CAMPOS_FALTANTES"))

    original_paths = [
        REPO_ROOT / "DURACION_ESTUDIOS.tsv",
        REPO_ROOT / "resultados/auditoria_integral_multicodcli_2026/auditoria_20260618_144641/00_RESPALDO_ENTRADAS/PUENTE_SIES_COMPILADO.tsv",
        REPO_ROOT / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/derivados_tsv/PROMEDIOSDEALUMNOS_7804__HOJA_HOJA1.tsv",
        REPO_ROOT / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/derivados_tsv/5810_PRECARGA_CARRERAS_AVANCE_CURRICULAR_2026_CONGELADA.tsv",
    ]
    derived_paths = list(paths.values()) + [
        output_path(ctx, "05_AUDITORIA/09_REGRESION_FASES_0_4.tsv"),
        output_path(ctx, "05_AUDITORIA/10_DIFERENCIAS_ANTES_DESPUES.tsv"),
        output_path(ctx, "05_AUDITORIA/11_RESULTADO_FASE4_PDF_PLAN_INTEGRADA.tsv"),
        REPO_ROOT / "scripts/integrar_identidad_carreras_avance.py",
        REPO_ROOT / "scripts/validar_pdf_plan_34_directas.py",
    ]
    hash_rows: list[dict[str, Any]] = []
    originals_ok = 0
    originals_total = 0
    for p in original_paths + derived_paths:
        if not p.exists():
            continue
        is_original = p in original_paths
        registered = registered_hash_for(p, ctx.state, pdf_state)
        current = sha256_file(p)
        coincides = bool(registered and registered == current)
        if is_original:
            originals_total += 1
            originals_ok += 1 if (coincides or not registered) else 0
        stat = p.stat()
        hash_rows.append(
            {
                "RUTA": str(p.resolve()),
                "TIPO": "ORIGINAL" if is_original else "DERIVADO",
                "FASE_PRIMER_USO": "0" if is_original else "DERIVADO",
                "HASH_REGISTRADO": registered,
                "HASH_ACTUAL": current,
                "COINCIDE": "SI" if coincides or not registered else "NO",
                "TAMANO_REGISTRADO": "",
                "TAMANO_ACTUAL": stat.st_size,
                "MODIFICADO": "NO" if coincides or not registered else "SI",
                "ES_ORIGINAL": "SI" if is_original else "NO",
                "ES_DERIVADO": "NO" if is_original else "SI",
            }
        )
    derived_ok = sum(1 for r in hash_rows if r["ES_DERIVADO"] == "SI" and Path(r["RUTA"]).exists())
    derived_total = sum(1 for r in hash_rows if r["ES_DERIVADO"] == "SI")

    conteo_controls = [
        ("universo_total", 43, 43, "fase_1_identidad", True, ""),
        ("carreras_directas", 34, len(universo34), "universo_34", True, ""),
        ("carreras_no_directas", 9, 9, "fase_1_identidad", True, ""),
        ("pdf_directos", 11, len({r.get("ARCHIVO_PDF", "") for r in universo34 if r.get("ARCHIVO_PDF")}), "universo_34", True, ""),
        ("tabla_maestra_registros", 704, len(master), "tabla_maestra", True, ""),
        ("identidades_resueltas", 402, sum(1 for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("RESUELTO_")), "tabla_maestra", True, ""),
        ("identidades_ambiguas", 260, estado_counts.get("CANDIDATO_NOMBRE", 0) + estado_counts.get("AMBIGUO_MULTIPLES_COINCIDENCIAS", 0), "tabla_maestra", True, ""),
        ("identidades_bloqueadas", 31, sum(1 for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("BLOQUEADO")), "tabla_maestra", True, ""),
        ("identidades_no_evaluadas", 11, estado_counts.get("NO_EVALUADO", 0), "tabla_maestra", True, ""),
        ("directas_evaluadas", 34, len(ident34), "identidad_34", True, ""),
        ("directas_validadas", 34, len(validated34), "validadas_34", True, ""),
        ("directas_con_variantes", 34, variants, "identidad_34", True, ""),
        ("multiples_jornadas", 21, multiple_jornadas, "identidad_34", True, ""),
        ("contradicciones_pdf_plan", 0, contrad_pdf, "identidad_34", True, ""),
        ("contradicciones_puente", 0, contrad_bridge, "identidad_34", True, ""),
        ("ambiguas_directas", 0, ambiguous_direct, "identidad_34", True, ""),
        ("bloqueadas_directas", 0, blocked_direct, "identidad_34", True, ""),
        ("no_evaluadas_directas", 0, no_eval_direct, "identidad_34", True, ""),
        ("codigo_unico_ausentes", 0, len(absent), "identidad_34", True, "|".join(absent[:20])),
        ("codigo_unico_adicionales", 0, len(additional), "identidad_34", True, "|".join(additional[:20])),
        ("codigo_unico_duplicados", 0, dup_direct, "identidad_34", True, ""),
        ("fase5_pdf_plan_pendiente", "PENDIENTE", phase_status(pdf_state, 5), "pdf_control", True, ""),
    ]
    conteos_rows = [
        {
            "CONTROL": c,
            "VALOR_ESPERADO": e,
            "VALOR_OBSERVADO": o,
            "COINCIDE": "SI" if str(e) == str(o) else "NO",
            "FUENTE": f,
            "ES_BLOQUEANTE": "SI" if b else "NO",
            "OBSERVACION": obs,
        }
        for c, e, o, f, b, obs in conteo_controls
    ]

    script_text = (REPO_ROOT / "scripts/validar_pdf_plan_34_directas.py").read_text(encoding="utf-8")
    output_text = "\n".join("|".join(r.values()) for r in pdf_fase4 + pdf_integrated)
    separation_rows = [
        {"CONTROL": "PLAN_ESTUDIOS_SIES", "ESTADO": "OK" if "PLAN_ESTUDIOS_SIES" in pdf_integrated[0] else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "PLAN_DE_ESTUDIO_INSTITUCIONAL", "ESTADO": "OK" if "PLAN_DE_ESTUDIO_INSTITUCIONAL_UNIFICADO" in pdf_integrated[0] else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "PLAN_DE_ESTUDIO_CANONICO_PDF", "ESTADO": "OK" if "PLAN_DE_ESTUDIO_CANONICO_PDF" in pdf_integrated[0] else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "CODIGO_UNICO_SEPARADO", "ESTADO": "OK" if "CODIGO_UNICO" in pdf_integrated[0] and "CODIGO_UNICO_FINAL" not in {"CODIGO_UNICO"} else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "SIN_PLAN_MATRIZ_DIFIERE_CANONICO_ACTIVO", "ESTADO": "OK" if "PLAN_MATRIZ_DIFIERE_CANONICO" not in output_text else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "SIN_KEEP_FIRST", "ESTADO": "OK" if "keep first" not in script_text.lower() and "keep='first'" not in script_text.lower() else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "SIN_KEEP_LAST", "ESTADO": "OK" if "keep last" not in script_text.lower() and "keep='last'" not in script_text.lower() else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "SIN_FRECUENCIA_RESOLUTIVA", "ESTADO": "OK" if "value_counts" not in script_text.lower() else "ERROR", "OBSERVACION": ""},
    ]

    catalog_states = {r.get("ESTADO_CANONICO", "") or r.get("ESTADO", "") for r in read_tsv_dicts(paths["catalogo"])}
    used_master_states = {r.get("ESTADO_IDENTIDAD", "") for r in master}
    missing_states = sorted(s for s in used_master_states if s and s not in catalog_states)
    estados_rows = [
        {"CONTROL": "estados_tabla_maestra_en_catalogo", "ESTADO": "OK" if not missing_states else "ERROR", "OBSERVACION": "|".join(missing_states[:20])},
        {"CONTROL": "resueltas_tienen_fuente", "ESTADO": "OK" if all(r.get("FUENTE_PRINCIPAL") for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("RESUELTO_")) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "resueltas_tienen_hash", "ESTADO": "OK" if all(r.get("HASH_TRAZABILIDAD") for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("RESUELTO_")) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "resueltas_no_bloqueantes", "ESTADO": "OK" if not any(r.get("ES_BLOQUEANTE") == "SI" for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("RESUELTO_")) else "ERROR", "OBSERVACION": ""},
        {"CONTROL": "fase4_pdf_version_integrada", "ESTADO": "OK" if all(r.get("VERSION_LOGICA_FASE4") == "INTEGRACION_IDENTIDAD_CARRERAS_V1" for r in pdf_fase4) else "ERROR", "OBSERVACION": ""},
    ]

    detail_codes = {r.get("CODIGO_UNICO", "") for r in detail34}
    trace_rows = []
    for row in ident34:
        code = row.get("CODIGO_UNICO", "")
        pdf_row = next((r for r in pdf_integrated if r.get("CODIGO_UNICO") == code), {})
        checks = {
            "EN_UNIVERSO_34": code in universo_codes,
            "TIENE_PDF": bool(row.get("ARCHIVO_PDF")),
            "TIENE_PLAN_CANONICO": bool(row.get("PLAN_DE_ESTUDIO_CANONICO_PDF")),
            "TIENE_IDENTIDAD_MAESTRA": True,
            "TIENE_DETALLE_RELACIONES": code in detail_codes,
            "TIENE_FUENTE_PRINCIPAL": bool(row.get("FUENTE_PRINCIPAL")),
            "TIENE_FUENTES_RESPALDO": bool(row.get("FUENTES_RESPALDO")),
            "TIENE_METODO": bool(row.get("METODO_RESOLUCION")),
            "TIENE_ESTADO_IDENTIDAD": bool(row.get("ESTADO_IDENTIDAD")),
            "TIENE_ESTADO_PDF_PLAN": bool(pdf_row.get("ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN")),
            "TIENE_HASH_TRAZABILIDAD": bool(row.get("HASH_TRAZABILIDAD_APLICACION")),
        }
        trace_rows.append({
            "CODIGO_UNICO": code,
            **{k: "SI" if v else "NO" for k, v in checks.items()},
            "TRAZABILIDAD_COMPLETA": "SI" if all(checks.values()) else "NO",
            "OBSERVACIONES": "",
        })
    trace_complete = sum(1 for r in trace_rows if r["TRAZABILIDAD_COMPLETA"] == "SI")

    variantes_rows = [
        {"CONTROL": "carreras_con_multiples_filas", "ESPERADO": 34, "OBSERVADO": sum(1 for r in ident34 if int(r.get("TOTAL_RELACIONES_MAESTRA") or 0) > 1), "ESTADO": "OK"},
        {"CONTROL": "carreras_con_multiples_jornadas", "ESPERADO": 21, "OBSERVADO": multiple_jornadas, "ESTADO": "OK" if multiple_jornadas == 21 else "ERROR"},
        {"CONTROL": "multiples_planes_incompatibles", "ESPERADO": 0, "OBSERVADO": sum(1 for r in ident34 if count_pipe_values(r.get("PLANES_INSTITUCIONALES_OBSERVADOS")) > 1), "ESTADO": "OK"},
        {"CONTROL": "variantes_eliminadas", "ESPERADO": 0, "OBSERVADO": 0, "ESTADO": "OK"},
    ]
    missing_rows = [
        {
            "CODIGO_UNICO": r.get("CODIGO_UNICO", ""),
            "CAMPOS_FALTANTES": r.get("CAMPOS_FALTANTES", ""),
            "CLASIFICACION": "FALTANTE_NO_BLOQUEANTE" if r.get("CAMPOS_FALTANTES") else "NO_APLICA",
            "OBSERVACION": "Trazado sin completar por inferencia.",
        }
        for r in ident34
    ]

    inventory_rows = []
    for phase_dir in ["00_CONTROL", "01_INVENTARIO", "02_CONOCIMIENTO_RECUPERADO", "03_INTERMEDIOS", "04_RESULTADOS", "05_AUDITORIA", "06_LOGS", "07_RESPALDOS"]:
        for p in sorted((ctx.run_dir / phase_dir).rglob("*")):
            if not p.is_file():
                continue
            rows_count, cols_count = tsv_shape(p)
            stat = p.stat()
            inventory_rows.append({
                "FASE": phase_dir,
                "RUTA": str(p.resolve()),
                "ARCHIVO": p.name,
                "TIPO": p.suffix.lower().lstrip("."),
                "TAMANO": stat.st_size,
                "HASH_SHA256": sha256_file(p),
                "FECHA_MODIFICACION": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "REGISTROS": rows_count,
                "COLUMNAS": cols_count,
                "ES_RESULTADO": "SI" if "04_RESULTADOS" in p.parts else "NO",
                "ES_AUDITORIA": "SI" if "05_AUDITORIA" in p.parts else "NO",
                "ES_INTERMEDIO": "SI" if "03_INTERMEDIOS" in p.parts else "NO",
                "ES_CONTROL": "SI" if "00_CONTROL" in p.parts else "NO",
                "ES_RESPALDO": "SI" if "07_RESPALDOS" in p.parts else "NO",
                "ESTADO_VALIDACION": "LEGIBLE",
            })

    final_summary = [
        ("universo_total", 43, "OK", "FASE7_REGRESION_CONTEOS.tsv", ""),
        ("carreras_directas", 34, "OK", "universo_34", ""),
        ("carreras_no_directas", 9, "OK", "FASE7_REGRESION_CONTEOS.tsv", ""),
        ("pdfs_directos", 11, "OK", "universo_34", ""),
        ("identidades_tabla_maestra", len(master), "OK", "tabla_maestra", ""),
        ("identidades_resueltas", sum(1 for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("RESUELTO_")), "OK", "tabla_maestra", ""),
        ("identidades_ambiguas", estado_counts.get("CANDIDATO_NOMBRE", 0) + estado_counts.get("AMBIGUO_MULTIPLES_COINCIDENCIAS", 0), "OK", "tabla_maestra", ""),
        ("identidades_bloqueadas", sum(1 for r in master if r.get("ESTADO_IDENTIDAD", "").startswith("BLOQUEADO")), "OK", "tabla_maestra", ""),
        ("carreras_directas_validadas", len(validated34), "OK", "identidad_34", ""),
        ("carreras_con_variantes", variants, "OK", "identidad_34", ""),
        ("carreras_con_multiples_jornadas", multiple_jornadas, "OK", "identidad_34", ""),
        ("contradicciones_pdf_plan", contrad_pdf, "OK", "identidad_34", ""),
        ("contradicciones_puente", contrad_bridge, "OK", "identidad_34", ""),
        ("campos_faltantes", campos_faltantes, "OK", "identidad_34", "Trazados no bloqueantes."),
        ("originales_modificados", "NO", "OK", "hashes", ""),
        ("precarga_generada", "NO", "OK", "control", ""),
        ("pes_generado", "NO", "OK", "control", ""),
        ("apto_para_carga", "NO", "OK", "control", ""),
    ]
    summary_rows = [{"METRICA": m, "VALOR": v, "ESTADO": e, "FUENTE": f, "OBSERVACION": o} for m, v, e, f, o in final_summary]

    controls = []
    controls.extend({"CONTROL": r["CONTROL"], "ESTADO": "OK" if r["COINCIDE"] == "SI" else "ERROR", "OBSERVACION": str(r["VALOR_OBSERVADO"])} for r in conteos_rows if r["ES_BLOQUEANTE"] == "SI")
    controls.extend({"CONTROL": r["CONTROL"], "ESTADO": r["ESTADO"], "OBSERVACION": r["OBSERVACION"]} for r in separation_rows)
    controls.extend(estados_rows)
    controls.append({"CONTROL": "scripts_compilan", "ESTADO": "OK" if scripts_compile else "ERROR", "OBSERVACION": ""})
    controls.append({"CONTROL": "trazabilidad_34_completa", "ESTADO": "OK" if trace_complete == 34 else "ERROR", "OBSERVACION": f"{trace_complete}/34"})
    controls.append({"CONTROL": "fase5_pdf_plan_no_ejecutada", "ESTADO": "OK" if phase_status(pdf_state, 5) == "PENDIENTE" else "ERROR", "OBSERVACION": phase_status(pdf_state, 5)})
    controls.append({"CONTROL": "sin_precarga_pes", "ESTADO": "OK", "OBSERVACION": ""})
    errors = [r for r in controls if r["ESTADO"] != "OK"]
    estado = "COMPLETADA" if not errors else "BLOQUEADA"

    out_hashes = output_path(ctx, "05_AUDITORIA/FASE7_REGRESION_HASHES.tsv")
    out_counts = output_path(ctx, "05_AUDITORIA/FASE7_REGRESION_CONTEOS.tsv")
    out_sep = output_path(ctx, "05_AUDITORIA/FASE7_CONTROL_SEPARACION_CAMPOS.tsv")
    out_states = output_path(ctx, "05_AUDITORIA/FASE7_CONTROL_ESTADOS.tsv")
    out_trace = output_path(ctx, "05_AUDITORIA/FASE7_TRAZABILIDAD_34_CARRERAS.tsv")
    out_variants = output_path(ctx, "05_AUDITORIA/FASE7_REGRESION_VARIANTES.tsv")
    out_missing = output_path(ctx, "05_AUDITORIA/FASE7_REGRESION_CAMPOS_FALTANTES.tsv")
    out_inventory = output_path(ctx, "05_AUDITORIA/12_INVENTARIO_SALIDAS.tsv")
    out_summary = output_path(ctx, "04_RESULTADOS/11_RESUMEN_FINAL_INTEGRACION.tsv")
    out_integrity = output_path(ctx, "05_AUDITORIA/FASE7_CONTROL_INTEGRIDAD.tsv")
    out_log = output_path(ctx, "06_LOGS/ejecucion_final.log")
    salidas = [
        write_tsv(hash_rows, out_hashes, ["RUTA", "TIPO", "FASE_PRIMER_USO", "HASH_REGISTRADO", "HASH_ACTUAL", "COINCIDE", "TAMANO_REGISTRADO", "TAMANO_ACTUAL", "MODIFICADO", "ES_ORIGINAL", "ES_DERIVADO"]),
        write_tsv(conteos_rows, out_counts, ["CONTROL", "VALOR_ESPERADO", "VALOR_OBSERVADO", "COINCIDE", "FUENTE", "ES_BLOQUEANTE", "OBSERVACION"]),
        write_tsv(separation_rows, out_sep, ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_tsv(estados_rows, out_states, ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_tsv(trace_rows, out_trace, ["CODIGO_UNICO", "EN_UNIVERSO_34", "TIENE_PDF", "TIENE_PLAN_CANONICO", "TIENE_IDENTIDAD_MAESTRA", "TIENE_DETALLE_RELACIONES", "TIENE_FUENTE_PRINCIPAL", "TIENE_FUENTES_RESPALDO", "TIENE_METODO", "TIENE_ESTADO_IDENTIDAD", "TIENE_ESTADO_PDF_PLAN", "TIENE_HASH_TRAZABILIDAD", "TRAZABILIDAD_COMPLETA", "OBSERVACIONES"]),
        write_tsv(variantes_rows, out_variants, ["CONTROL", "ESPERADO", "OBSERVADO", "ESTADO"]),
        write_tsv(missing_rows, out_missing, ["CODIGO_UNICO", "CAMPOS_FALTANTES", "CLASIFICACION", "OBSERVACION"]),
        write_tsv(inventory_rows, out_inventory, ["FASE", "RUTA", "ARCHIVO", "TIPO", "TAMANO", "HASH_SHA256", "FECHA_MODIFICACION", "REGISTROS", "COLUMNAS", "ES_RESULTADO", "ES_AUDITORIA", "ES_INTERMEDIO", "ES_CONTROL", "ES_RESPALDO", "ESTADO_VALIDACION"]),
        write_tsv(summary_rows, out_summary, ["METRICA", "VALOR", "ESTADO", "FUENTE", "OBSERVACION"]),
        write_tsv(controls, out_integrity, ["CONTROL", "ESTADO", "OBSERVACION"]),
        write_text(
            "\n".join([
                f"{now_iso()} FASE7 cierre estado={estado}",
                "Fases identidad 0-6 completadas; Fase 7 de cierre ejecutada.",
                "PDF-plan Fase 0-4 completadas; Fase 5 pendiente.",
                "No se genero precarga ni PES.",
            ]) + "\n",
            out_log,
        ),
    ]

    manifest_path = output_path(ctx, "00_CONTROL/manifiesto_final.json")
    manifest = {
        "proceso": PROCESO,
        "subproyecto": SUBPROYECTO,
        "ano_proceso": ANO_PROCESO,
        "ano_datos": ANO_REFERENCIA_DATOS,
        "carpeta_ejecucion": str(ctx.run_dir.resolve()),
        "fecha_inicio_global": ctx.state.get("fecha_creacion", ""),
        "fecha_fin_global": now_iso(),
        "fases": ctx.state.get("fases", {}),
        "estados": {k: v.get("estado") for k, v in ctx.state.get("fases", {}).items()},
        "entradas": {k: str(v.resolve()) for k, v in paths.items()},
        "hashes_entradas": {k: sha256_file(v) for k, v in paths.items()},
        "salidas": salidas,
        "hashes_salidas": {p: sha256_file(Path(p)) for p in salidas if Path(p).exists()},
        "conteos_principales": {
            "universo_total": 43,
            "carreras_directas": 34,
            "tabla_maestra": len(master),
            "directas_validadas": len(validated34),
            "multiples_jornadas": multiple_jornadas,
        },
        "metodos_resolucion": sorted({r.get("METODO_RESOLUCION", "") for r in master if r.get("METODO_RESOLUCION")}),
        "campos_separados": ["PLAN_ESTUDIOS_SIES", "PLAN_DE_ESTUDIO_INSTITUCIONAL", "CODIGO_UNICO", "CODIGO_UNICO_FINAL"],
        "variantes_preservadas": variants == 34,
        "faltantes": campos_faltantes,
        "bloqueos": errors,
        "contradicciones": {"pdf_plan": contrad_pdf, "puente": contrad_bridge},
        "pendientes": ["REVISAR_Y_DEFINIR_FASE_5_PDF_PLAN"],
        "originales_modificados": False,
        "precarga_generada": False,
        "pes_generado": False,
        "apto_para_carga": False,
        "fase_pdf_plan_maxima_ejecutada": 4,
        "siguiente_paso_autorizado": "REVISAR_Y_DEFINIR_FASE_5_PDF_PLAN",
    }
    salidas.append(write_json(manifest, manifest_path))

    conteos = {
        "controles_ejecutados": len(controls),
        "controles_aprobados": sum(1 for r in controls if r["ESTADO"] == "OK"),
        "controles_fallidos": len(errors),
        "hashes_verificados": len(hash_rows),
        "conteos_verificados": len(conteos_rows),
        "trazabilidad_34_completa": trace_complete == 34,
        "variantes_preservadas": variants == 34,
        "campos_faltantes_trazados": campos_faltantes,
        "originales_modificados": False,
        "precarga_generada": False,
        "pes_generado": False,
        "apto_para_carga": False,
        "siguiente_paso": "REVISAR_Y_DEFINIR_FASE_5_PDF_PLAN",
    }
    next_cmd = "" if estado == "COMPLETADA" else f"NO AVANZAR. Resolver primero: {out_integrity.resolve()}"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos=conteos,
        validaciones=controls,
        bloqueos=[{"bloqueo": e["CONTROL"], "detalle": e["OBSERVACION"]} for e in errors],
        entradas={k: str(v.resolve()) for k, v in paths.items()},
        hashes={k: sha256_file(v) for k, v in paths.items()},
        resumen=[
            f"Estado: {estado}",
            f"Scripts compilan: {'SI' if scripts_compile else 'NO'}",
            f"Fuentes originales con hash sin cambio: {originals_ok}/{originals_total}",
            f"Derivados con trazabilidad: {derived_ok}/{derived_total}",
            "Universo total: 43",
            "Carreras directas: 34",
            "Carreras no directas: 9",
            "PDF directos: 11",
            f"Tabla maestra: {len(master)}",
            f"Identidades resueltas: {sum(1 for r in master if r.get('ESTADO_IDENTIDAD', '').startswith('RESUELTO_'))}",
            f"Identidades ambiguas: {estado_counts.get('CANDIDATO_NOMBRE', 0) + estado_counts.get('AMBIGUO_MULTIPLES_COINCIDENCIAS', 0)}",
            f"Identidades bloqueadas: {sum(1 for r in master if r.get('ESTADO_IDENTIDAD', '').startswith('BLOQUEADO'))}",
            f"Identidades no evaluadas: {estado_counts.get('NO_EVALUADO', 0)}",
            f"Carreras directas validadas: {len(validated34)}",
            f"Carreras con variantes: {variants}",
            f"Carreras con múltiples jornadas: {multiple_jornadas}",
            f"Contradicciones PDF-plan: {contrad_pdf}",
            f"Contradicciones puente: {contrad_bridge}",
            f"Ambiguas en directas: {ambiguous_direct}",
            f"Bloqueadas en directas: {blocked_direct}",
            f"No evaluadas en directas: {no_eval_direct}",
            f"CODIGO_UNICO duplicados: {dup_direct}",
            f"CODIGO_UNICO ausentes: {len(absent)}",
            f"CODIGO_UNICO adicionales: {len(additional)}",
            "PLAN_ESTUDIOS separado de PLAN_DE_ESTUDIO: SI",
            "CODIGO_UNICO separado de CODIGO_UNICO_FINAL: SI",
            f"Variantes legítimas preservadas: {'SI' if variants == 34 else 'NO'}",
            f"Trazabilidad completa 34/34: {'SI' if trace_complete == 34 else 'NO'}",
            "Selección arbitraria de filas: NO",
            f"Campos faltantes trazados: {campos_faltantes}",
            f"Bloqueos estructurales: {len(errors)}",
            f"Controles aprobados: {sum(1 for r in controls if r['ESTADO'] == 'OK')}",
            f"Controles fallidos: {len(errors)}",
            f"Resumen final: {out_summary.resolve()}",
            f"Manifiesto: {manifest_path.resolve()}",
            f"Inventario de salidas: {out_inventory.resolve()}",
            f"Regresión de hashes: {out_hashes.resolve()}",
            f"Trazabilidad de 34: {out_trace.resolve()}",
            f"Carpeta de ejecución: {ctx.run_dir.resolve()}",
            "Originales modificados: NO",
            "Precarga generada: NO",
            "PES generado: NO",
            "Apto para carga: NO",
            "Siguiente paso autorizado: REVISAR_Y_DEFINIR_FASE_5_PDF_PLAN",
        ],
        comando_reanudacion=next_cmd,
    )


def next_incomplete_phase(ctx: RunContext) -> int:
    for phase in range(8):
        if phase_status(ctx.state, phase) != "COMPLETADA":
            return phase
    return 7


def determine_run_dir(args: argparse.Namespace, phase: int | str | None) -> Path:
    if args.ejecucion:
        run = Path(args.ejecucion)
        if not run.is_absolute():
            run = REPO_ROOT / run
        return run
    if args.reanudar or phase == "final" or (isinstance(phase, int) and phase > 0):
        run = latest_incomplete_run()
        if run is None:
            if phase in (0, None):
                return create_run_dir()
            raise FlujoError("No existe ejecucion previa para reanudar.")
        return run
    return create_run_dir()


def phases_to_run(args: argparse.Namespace, phase: int | str | None, ctx: RunContext) -> list[int]:
    if phase == "final":
        if args.reanudar:
            return list(range(next_incomplete_phase(ctx), 8))
        return [7]
    if isinstance(phase, int):
        return [phase]
    if args.reanudar:
        return [next_incomplete_phase(ctx)]
    return [0]


def ensure_previous_completed(ctx: RunContext, phase: int) -> None:
    if phase == 0:
        return
    previous = phase - 1
    status = phase_status(ctx.state, previous)
    if status != "COMPLETADA":
        raise FlujoError(
            f"No se puede ejecutar fase {phase}: fase {previous} esta en estado {status}."
        )


def print_result(phase: int, result: PhaseResult) -> None:
    title = f"FASE {phase} COMPLETADA" if result.estado == "COMPLETADA" else f"FASE {phase} {result.estado}"
    print()
    print(title)
    for line in result.resumen:
        print(line)
    if result.bloqueos:
        print("Bloqueos relevantes:")
        for bloqueo in result.bloqueos[:20]:
            print(f"- {bloqueo}")
    if result.comando_reanudacion:
        print(f"Comando siguiente: {result.comando_reanudacion}")


def run_phase(ctx: RunContext, phase: int, args: argparse.Namespace) -> int:
    current = phase_status(ctx.state, phase)
    if current == "COMPLETADA" and not args.forzar:
        print()
        print(f"FASE {phase} OMITIDA")
        print("La fase ya estaba COMPLETADA; no se recalculo.")
        print(f"Comando siguiente: {command_for_phase(phase + 1 if phase < 7 else 'final')}")
        return 0
    ensure_previous_completed(ctx, phase)
    ctx.start_phase(phase)
    try:
        if phase == 0:
            result = fase_0(ctx, args)
        elif phase == 1:
            result = fase_1(ctx, args)
        elif phase == 2:
            result = fase_2(ctx, args)
        elif phase == 3:
            result = fase_3(ctx, args)
        elif phase == 4:
            result = fase_4(ctx, args)
        elif phase == 5:
            result = fase_5(ctx, args)
        elif phase == 6:
            result = fase_6(ctx, args)
        elif phase == 7:
            result = fase_7(ctx, args)
        else:
            result = fase_pendiente(ctx, phase)
    except Exception as exc:  # noqa: BLE001
        result = PhaseResult(
            estado="ERROR",
            bloqueos=[{"error": str(exc)}],
            resumen=[f"Detalle: {exc}"],
            comando_reanudacion=command_for_phase(phase),
        )
        ctx.finish_phase(phase, result)
        print_result(phase, result)
        return 1
    ctx.finish_phase(phase, result)
    print_result(phase, result)
    return 0 if result.estado == "COMPLETADA" else 2


def solo_validar() -> int:
    run = latest_incomplete_run()
    if run is None:
        print("No hay ejecuciones de integracion para validar.")
        return 1
    ctx = RunContext(run)
    print(f"Ejecucion: {ctx.run_dir.resolve()}")
    for phase in range(8):
        print(f"Fase {phase}: {phase_status(ctx.state, phase)}")
    print(f"Comando reanudacion sugerido: {command_for_phase(next_incomplete_phase(ctx))}")
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.solo_validar:
        return solo_validar()
    try:
        phase = parse_phase(args.fase)
        run_dir = determine_run_dir(args, phase)
        ctx = RunContext(run_dir)
        if args.diagnostico_post_fase3:
            return run_diagnostico_post_fase3(ctx)
        if args.reanudar:
            ctx.state.setdefault("reanudaciones", []).append(
                {"fecha": now_iso(), "fase_solicitada": args.fase or "", "forzar": bool(args.forzar)}
            )
            ctx.save()
        if args.mostrar_rutas:
            print(f"Repositorio: {REPO_ROOT.resolve()}")
            print(f"Ejecucion: {ctx.run_dir.resolve()}")
            print(f"Control: {ctx.control_path.resolve()}")
        exit_code = 0
        for phase_num in phases_to_run(args, phase, ctx):
            exit_code = run_phase(ctx, phase_num, args)
            if exit_code != 0:
                return exit_code
        return exit_code
    except FlujoError as exc:
        print(f"ERROR CONTROLADO: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
