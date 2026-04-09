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
        result = fase_0(ctx, args) if phase == 0 else fase_pendiente(ctx, phase)
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
