#!/usr/bin/env python3
"""Integracion auditable de identidad de carreras para Avance Curricular 2026."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
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
