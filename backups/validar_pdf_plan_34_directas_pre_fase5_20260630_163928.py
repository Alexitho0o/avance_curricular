#!/usr/bin/env python3
"""Flujo auditable para validacion individual PDF-PLAN de 34 carreras directas."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pandas as pd


PROCESO = "Avance Curricular SIES 2026"
SUBPROCESO = "Carreras"
ANO_PROCESO = "2026"
ANO_REFERENCIA_DATOS = "2025"

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_2026 = REPO_ROOT / "avance_curricular_2026"
AUDITORIAS_DIR = BASE_2026 / "04_gobernanza_mallas" / "03_auditorias"
CONCILIACION_DIR = BASE_2026 / "04_gobernanza_mallas" / "02_conciliacion"
EXEC_PREFIX = "VALIDACION_INDIVIDUAL_PDF_PLAN_"
ENDASH = "\u2013"

REQUIRED_INPUTS = {
    "mapeo_seguro_43": {
        "base": "cierre_seguro",
        "filename": "03_MAPEO_SEGURO_43_CARRERAS.tsv",
    },
    "totales_documentales": {
        "base": "cierre_seguro",
        "filename": "02_TOTALES_DOCUMENTALES_CORREGIDOS_POR_PDF.tsv",
    },
    "mapeo_pdf_plan_canonico": {
        "base": "conciliacion",
        "filename": "01_MAPEO_PDF_PLAN_CANONICO.tsv",
    },
    "hoja1_congelada": {
        "path": BASE_2026
        / "00_fuentes_congeladas"
        / "CARGA_CONGELADA_20260626_005826"
        / "derivados_tsv"
        / "PROMEDIOSDEALUMNOS_7804__HOJA_HOJA1.tsv",
    },
    "puente_sies": {
        "path": REPO_ROOT
        / "resultados"
        / "auditoria_integral_multicodcli_2026"
        / "auditoria_20260618_144641"
        / "00_RESPALDO_ENTRADAS"
        / "PUENTE_SIES_COMPILADO.tsv",
    },
}

DIRS = [
    "00_CONTROL",
    "01_ENTRADAS",
    "02_INTERMEDIOS",
    "03_RESULTADOS",
    "04_AUDITORIA",
    "05_LOGS",
]

PHASE_NAMES = {
    0: "DESCUBRIMIENTO_Y_CONTROL_DE_ENTRADAS",
    1: "NORMALIZACION_Y_UNIVERSO_34_DIRECTAS",
    2: "VALIDACION_MAPEO_CANONICO_PDF_PLAN",
    3: "VALIDACION_CODIGO_UNICO_Y_PUENTE",
    4: "VALIDACION_PLAN_EN_MATRIZ",
    5: "CLASIFICACION_INDIVIDUAL",
    6: "INCORPORACION_CONTROLADA_DE_TOTALES",
    7: "VALIDACION_FINAL_Y_CIERRE",
}

VALID_PHASE_STATES = {"PENDIENTE", "EN_EJECUCION", "COMPLETADA", "BLOQUEADA", "ERROR"}
FINAL_STATES = {
    "VALIDADO_DIRECTO_PDF_PLAN",
    "VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ",
    "BLOQUEADO",
}
BLOCK_REASONS = {
    "PDF_NO_INFORMADO",
    "PDF_SIN_MAPEO_CANONICO",
    "PLAN_CANONICO_NO_EXISTE_HOJA1",
    "CODIGO_UNICO_NO_EXISTE_PUENTE",
    "CODIGO_UNICO_MULTIPLE_EN_PUENTE",
    "CODCARR_PUENTE_DIFIERE_CANONICO",
    "PLAN_MATRIZ_DIFIERE_CANONICO",
    "PUENTE_MARCADO_BLOQUEANTE",
    "OTRO_BLOQUEO_DOCUMENTADO",
}

COLUMN_CANDIDATES = {
    "CODIGO_UNICO": [
        "CODIGO_UNICO",
        "CODIGO_UNICO_FINAL",
        "CODIGO_UNICO_SIES",
        "CODIGOS_SIES_POTENCIALES",
    ],
    "PDF": [
        "PDF_CANONICO",
        "ARCHIVO_PDF",
        "PDF_DIRECTO_CANDIDATO",
        "PDF_MALLA_CANDIDATO",
        "PDF",
        "ARCHIVO",
    ],
    "COBERTURA": [
        "COBERTURA_NORMALIZADA",
        "ESTADO_COBERTURA_DOCUMENTAL",
        "COBERTURA",
    ],
    "CARRERA": [
        "NOMBRE_CARRERA",
        "CARRERA",
        "NOMBRE_NORMALIZADO",
        "NOMBRE_L",
    ],
    "JORNADA": [
        "JORNADA",
        "JORNADA_MATRIZ",
    ],
    "PLAN_MATRIZ": [
        "PLAN_ESTUDIOS",
        "PLAN_DE_ESTUDIO",
        "PLAN_DE_ESTUDIO_1",
        "PLAN",
        "PLAN_ESTUDIO",
    ],
    "CODCARR_CANONICO": [
        "CODCARR_CANONICO",
        "CODCARR_CANONICO_VALIDACION",
        "CODCARR_CANONICO_PDF",
        "CODCARR",
        "CODCARPR",
    ],
    "PLAN_CANONICO": [
        "PLAN_DE_ESTUDIO_CANONICO",
        "PLAN_CANONICO_VALIDACION",
        "PLAN_CANONICO",
        "PLAN_DE_ESTUDIO",
    ],
    "EXISTE_EN_HOJA1": [
        "EXISTE_EN_HOJA1",
        "PLAN_EXISTE_EN_HOJA1",
    ],
    "CODIGO_UNICO_PUENTE": [
        "CODIGO_UNICO_FINAL",
        "CODIGO_UNICO",
        "CODIGOS_SIES_POTENCIALES",
    ],
    "CODCARPR": [
        "CODCARPR",
        "FAMILIA_CODCARPR",
    ],
    "RESOLUCION_STATUS": [
        "RESOLUCION_STATUS",
        "GOBERNANZA_STATUS",
    ],
    "ES_BLOQUEANTE": [
        "ES_BLOQUEANTE",
        "BLOQUEANTE",
    ],
    "TOTAL_UNIDADES": [
        "TOTAL_UNIDADES_DOCUMENTALES",
        "TOTAL_UNIDADES",
    ],
}

IDENTIDAD_RUN_DIR = (
    AUDITORIAS_DIR / "INTEGRACION_IDENTIDAD_CARRERAS_20260630_111622"
)
RUTA_IDENTIDAD_34 = IDENTIDAD_RUN_DIR / "04_RESULTADOS/06_IDENTIDAD_APLICADA_34_CARRERAS.tsv"
RUTA_DETALLE_IDENTIDAD_34 = (
    IDENTIDAD_RUN_DIR / "04_RESULTADOS/06A_IDENTIDAD_APLICADA_34_DETALLE_RELACIONES.tsv"
)
RUTA_COMPARACION_IDENTIDAD_PDF_PLAN = (
    IDENTIDAD_RUN_DIR / "05_AUDITORIA/FASE5_COMPARACION_IDENTIDAD_PDF_PLAN.tsv"
)
RUTA_COMPARACION_IDENTIDAD_PUENTE = (
    IDENTIDAD_RUN_DIR / "05_AUDITORIA/FASE5_COMPARACION_PUENTE_PREVIO.tsv"
)
VERSION_LOGICA_FASE4_INTEGRADA = "INTEGRACION_IDENTIDAD_CARRERAS_V1"


@dataclass
class PhaseResult:
    estado: str
    salidas: list[str] = field(default_factory=list)
    conteos: dict[str, Any] = field(default_factory=dict)
    validaciones: list[dict[str, Any]] = field(default_factory=list)
    errores: list[dict[str, Any]] = field(default_factory=list)
    pendientes: list[dict[str, Any]] = field(default_factory=list)
    entradas: dict[str, str] = field(default_factory=dict)
    hashes: dict[str, str] = field(default_factory=dict)
    resumen: list[str] = field(default_factory=list)
    comando_reanudacion: str = ""


class FlujoError(Exception):
    """Error controlado del flujo."""


def normalize_argv(argv: list[str]) -> list[str]:
    normalized: list[str] = []
    for arg in argv:
        if arg.startswith(("–", "—")):
            stripped = arg.lstrip("–—")
            normalized.append("--" + stripped)
        else:
            normalized.append(arg)
    return normalized


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validacion individual PDF-PLAN de 34 carreras directas."
    )
    parser.add_argument("--fase", default=None, help="Fase 0-7 o final.")
    parser.add_argument("--reanudar", action="store_true", help="Reanudar ultima ejecucion.")
    parser.add_argument("--forzar", action="store_true", help="Repetir una fase ya completada.")
    parser.add_argument(
        "--solo-validar",
        action="store_true",
        help="Validar estado y hashes sin ejecutar fases nuevas.",
    )
    parser.add_argument("--mostrar-rutas", action="store_true", help="Mostrar rutas base.")
    return parser.parse_args(normalize_argv(argv))


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def command_for_phase(phase: int | str) -> str:
    value = "final" if phase == "final" else str(phase)
    return (
        f"python scripts/validar_pdf_plan_34_directas.py "
        f"{ENDASH}fase {value} {ENDASH}reanudar"
    )


def normalize_col(name: str) -> str:
    text = unicodedata.normalize("NFKD", str(name))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().upper()).strip("_")
    return text or "COLUMNA_SIN_NOMBRE"


def normalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    used: dict[str, int] = {}
    rename: dict[str, str] = {}
    original_by_normalized: dict[str, str] = {}
    for col in df.columns:
        base = normalize_col(col)
        count = used.get(base, 0)
        normalized = base if count == 0 else f"{base}_{count + 1}"
        used[base] = count + 1
        rename[col] = normalized
        original_by_normalized[normalized] = str(col)
    return df.rename(columns=rename), original_by_normalized


def read_tsv(path: Path, normalize: bool = False) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
    if normalize:
        df, _ = normalize_columns(df)
    return df


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_tsv(df: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False, encoding="utf-8")
    return str(path.resolve())


def write_json(data: dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return str(path.resolve())


def empty_df(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    available = set(columns)
    for candidate in candidates:
        normalized = normalize_col(candidate)
        if normalized in available:
            return normalized
    return None


def required_column(df: pd.DataFrame, logical_name: str) -> str:
    col = first_existing(list(df.columns), COLUMN_CANDIDATES[logical_name])
    if not col:
        raise FlujoError(f"No se detecto columna requerida: {logical_name}")
    return col


def truthy_si(value: Any) -> bool:
    return str(value).strip().upper() in {"SI", "S", "YES", "Y", "TRUE", "1"}


def is_no(value: Any) -> bool:
    return str(value).strip().upper() in {"NO", "N", "FALSE", "0", ""}


def latest_dir(base: Path, pattern: str) -> Path | None:
    candidates = sorted([p for p in base.glob(pattern) if p.is_dir()])
    return candidates[-1] if candidates else None


def list_execution_dirs() -> list[Path]:
    return sorted([p for p in AUDITORIAS_DIR.glob(f"{EXEC_PREFIX}*") if p.is_dir()])


def phase_key(phase: int) -> str:
    return f"fase_{phase}"


def phase_status(state: dict[str, Any], phase: int) -> str:
    return (
        state.get("fases", {})
        .get(phase_key(phase), {})
        .get("estado", "PENDIENTE")
    )


def run_is_complete(run_dir: Path) -> bool:
    state_path = run_dir / "00_CONTROL" / "estado_fases.json"
    if not state_path.exists():
        return False
    try:
        with state_path.open("r", encoding="utf-8") as fh:
            state = json.load(fh)
    except json.JSONDecodeError:
        return False
    return phase_status(state, 7) == "COMPLETADA"


def latest_execution(prefer_incomplete: bool = True) -> Path | None:
    executions = list_execution_dirs()
    if not executions:
        return None
    if prefer_incomplete:
        incomplete = [p for p in executions if not run_is_complete(p)]
        if incomplete:
            return incomplete[-1]
    return executions[-1]


def create_run_dir() -> Path:
    AUDITORIAS_DIR.mkdir(parents=True, exist_ok=True)
    candidate = AUDITORIAS_DIR / f"{EXEC_PREFIX}{timestamp()}"
    suffix = 1
    while candidate.exists():
        candidate = AUDITORIAS_DIR / f"{EXEC_PREFIX}{timestamp()}_{suffix}"
        suffix += 1
    for dirname in DIRS:
        (candidate / dirname).mkdir(parents=True, exist_ok=True)
    return candidate


class RunContext:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        for dirname in DIRS:
            (self.run_dir / dirname).mkdir(parents=True, exist_ok=True)
        self.control_path = self.run_dir / "00_CONTROL" / "estado_fases.json"
        self.log_path = self.run_dir / "05_LOGS" / "ejecucion.log"
        self.state = self._load_or_init_state()

    def _load_or_init_state(self) -> dict[str, Any]:
        if self.control_path.exists():
            with self.control_path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {
            "proceso": PROCESO,
            "subproceso": SUBPROCESO,
            "ano_proceso": ANO_PROCESO,
            "ano_referencia_datos": ANO_REFERENCIA_DATOS,
            "run_dir": str(self.run_dir.resolve()),
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
                    "errores": [],
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

    def input_paths(self) -> dict[str, str]:
        entradas = self.state.get("fases", {}).get("fase_0", {}).get("entradas", {})
        if not entradas:
            raise FlujoError("Fase 0 no tiene entradas registradas.")
        return entradas

    def start_phase(self, phase: int) -> None:
        entry = self.state["fases"][phase_key(phase)]
        entry.update(
            {
                "estado": "EN_EJECUCION",
                "fecha_inicio": now_iso(),
                "fecha_fin": "",
                "errores": [],
                "pendientes": [],
            }
        )
        self.save()
        self.log(f"FASE {phase} INICIO")

    def finish_phase(self, phase: int, result: PhaseResult) -> None:
        if result.estado not in VALID_PHASE_STATES:
            raise FlujoError(f"Estado de fase no permitido: {result.estado}")
        entry = self.state["fases"][phase_key(phase)]
        entry.update(
            {
                "estado": result.estado,
                "fecha_fin": now_iso(),
                "entradas": result.entradas or entry.get("entradas", {}),
                "hashes": result.hashes or entry.get("hashes", {}),
                "salidas": result.salidas,
                "conteos": result.conteos,
                "validaciones": result.validaciones,
                "errores": result.errores,
                "pendientes": result.pendientes,
                "comando_reanudacion": result.comando_reanudacion,
            }
        )
        self.save()
        self.log(f"FASE {phase} FIN {result.estado}")


def output_path(ctx: RunContext, relative: str) -> Path:
    return ctx.run_dir / relative


def print_result(title: str, result: PhaseResult) -> None:
    print()
    print(title)
    for line in result.resumen:
        print(line)
    if result.errores:
        print("Errores o bloqueos relevantes:")
        for err in result.errores[:20]:
            print(f"- {err}")
        if len(result.errores) > 20:
            print(f"- ... {len(result.errores) - 20} casos adicionales en archivos TSV/JSON")
    if result.comando_reanudacion:
        print(f"Comando siguiente: {result.comando_reanudacion}")


def discover_input_paths() -> tuple[dict[str, Path], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    cierre_dir = latest_dir(AUDITORIAS_DIR, "CIERRE_SEGURO_MAPEO_MALLAS_*")
    conciliacion_dir = latest_dir(CONCILIACION_DIR, "CONCILIACION_CANONICA_PDF_HOJA1_*")

    if cierre_dir is None:
        errors.append({"tipo": "CARPETA_NO_ENCONTRADA", "detalle": "CIERRE_SEGURO_MAPEO_MALLAS_*"})
    if conciliacion_dir is None:
        errors.append(
            {"tipo": "CARPETA_NO_ENCONTRADA", "detalle": "CONCILIACION_CANONICA_PDF_HOJA1_*"}
        )

    paths: dict[str, Path] = {}
    for logical, spec in REQUIRED_INPUTS.items():
        if "path" in spec:
            paths[logical] = Path(spec["path"])
        elif spec["base"] == "cierre_seguro" and cierre_dir is not None:
            paths[logical] = cierre_dir / spec["filename"]
        elif spec["base"] == "conciliacion" and conciliacion_dir is not None:
            paths[logical] = conciliacion_dir / spec["filename"]

    if cierre_dir is not None:
        paths["carpeta_cierre_seguro"] = cierre_dir
    if conciliacion_dir is not None:
        paths["carpeta_conciliacion"] = conciliacion_dir
    return paths, errors


def fase_0(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    paths, discovery_errors = discover_input_paths()
    inventory_rows: list[dict[str, Any]] = []
    hash_rows: list[dict[str, str]] = []
    entradas: dict[str, str] = {}
    hashes: dict[str, str] = {}
    errors = discovery_errors[:]

    for logical in REQUIRED_INPUTS:
        path = paths.get(logical)
        row: dict[str, Any] = {
            "entrada": logical,
            "ruta_absoluta": str(path.resolve()) if path else "",
            "existe": "NO",
            "tipo": "TSV",
            "bytes": "",
            "filas": "",
            "columnas": "",
            "legible_utf8_tsv": "NO",
            "error": "",
        }
        if path is None:
            row["error"] = "ruta_no_detectada"
            errors.append({"entrada": logical, "error": "ruta_no_detectada"})
            inventory_rows.append(row)
            continue
        entradas[logical] = str(path.resolve())
        if not path.exists():
            row["error"] = "archivo_no_existe"
            errors.append({"entrada": logical, "ruta": str(path.resolve()), "error": "archivo_no_existe"})
            inventory_rows.append(row)
            continue
        row["existe"] = "SI"
        row["bytes"] = path.stat().st_size
        try:
            df = read_tsv(path)
            row["filas"] = len(df)
            row["columnas"] = len(df.columns)
            row["legible_utf8_tsv"] = "SI"
            digest = sha256_file(path)
            hashes[logical] = digest
            hash_rows.append(
                {
                    "entrada": logical,
                    "ruta_absoluta": str(path.resolve()),
                    "sha256": digest,
                }
            )
        except Exception as exc:  # noqa: BLE001 - debe registrar error concreto de lectura.
            row["error"] = str(exc)
            errors.append({"entrada": logical, "ruta": str(path.resolve()), "error": str(exc)})
        inventory_rows.append(row)

    for logical in ("carpeta_cierre_seguro", "carpeta_conciliacion"):
        if logical in paths:
            entradas[logical] = str(paths[logical].resolve())

    inventory_path = output_path(ctx, "01_ENTRADAS/inventario_entradas.tsv")
    hashes_path = output_path(ctx, "01_ENTRADAS/hashes_entradas.tsv")
    salidas = [
        write_tsv(pd.DataFrame(inventory_rows), inventory_path),
        write_tsv(pd.DataFrame(hash_rows), hashes_path),
        str(ctx.control_path.resolve()),
    ]

    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    resumen = [
        f"Estado: {estado}",
        f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
        f"Entradas requeridas: {len(REQUIRED_INPUTS)}",
        f"Archivos validos: {sum(1 for r in inventory_rows if r['legible_utf8_tsv'] == 'SI')}",
        f"Bloqueos: {len(errors)}",
        f"Inventario: {inventory_path.resolve()}",
        f"Hashes: {hashes_path.resolve()}",
    ]
    if "carpeta_cierre_seguro" in entradas:
        resumen.append(f"Cierre seguro detectado: {entradas['carpeta_cierre_seguro']}")
    if "carpeta_conciliacion" in entradas:
        resumen.append(f"Conciliacion detectada: {entradas['carpeta_conciliacion']}")

    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "entradas_requeridas": len(REQUIRED_INPUTS),
            "archivos_validos": sum(1 for r in inventory_rows if r["legible_utf8_tsv"] == "SI"),
            "bloqueos": len(errors),
        },
        validaciones=[
            {"validacion": "tsv_utf8_dtype_str_keep_default_na_false", "estado": estado},
            {"validacion": "hash_sha256_entradas", "estado": "COMPLETADA" if hashes else "BLOQUEADA"},
        ],
        errores=errors,
        entradas=entradas,
        hashes=hashes,
        resumen=resumen,
        comando_reanudacion=command_for_phase(1),
    )


def fase_1(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    entradas = ctx.input_paths()
    df = read_tsv(Path(entradas["mapeo_seguro_43"]), normalize=True)
    codigo_col = required_column(df, "CODIGO_UNICO")
    pdf_col = first_existing(list(df.columns), ["ARCHIVO_PDF"])
    if not pdf_col:
        pdf_col = required_column(df, "PDF")
    cobertura_col = required_column(df, "COBERTURA")
    carrera_col = first_existing(list(df.columns), COLUMN_CANDIDATES["CARRERA"])
    jornada_col = first_existing(list(df.columns), COLUMN_CANDIDATES["JORNADA"])
    plan_col = first_existing(list(df.columns), ["PLAN_ESTUDIOS", "PLAN_DE_ESTUDIO", "PLAN_ESTUDIO"])

    total = len(df)
    direct = df[df[cobertura_col] == "COBERTURA_DIRECTA_PDF"].copy()
    excluded = df[df[cobertura_col] != "COBERTURA_DIRECTA_PDF"].copy()
    dupes = direct[direct.duplicated(subset=[codigo_col], keep=False)].copy()

    control_rows = [
        {"control": "total_carreras_matriz", "valor": total, "esperado": 43, "estado": "OK" if total == 43 else "ERROR"},
        {"control": "carreras_directas", "valor": len(direct), "esperado": 34, "estado": "OK" if len(direct) == 34 else "ERROR"},
        {"control": "carreras_no_directas_excluidas", "valor": len(excluded), "esperado": 9, "estado": "OK" if len(excluded) == 9 else "ERROR"},
        {"control": "duplicados_codigo_unico", "valor": len(dupes), "esperado": 0, "estado": "OK" if len(dupes) == 0 else "ERROR"},
        {"control": "columna_pdf", "valor": pdf_col or "", "esperado": "detectada", "estado": "OK" if pdf_col else "ERROR"},
        {"control": "columna_cobertura", "valor": cobertura_col or "", "esperado": "detectada", "estado": "OK" if cobertura_col else "ERROR"},
        {"control": "columna_plan_matriz", "valor": plan_col or "", "esperado": "opcional", "estado": "OK"},
        {"control": "columna_carrera", "valor": carrera_col or "", "esperado": "opcional", "estado": "OK" if carrera_col else "ADVERTENCIA"},
        {"control": "columna_jornada", "valor": jornada_col or "", "esperado": "opcional", "estado": "OK" if jornada_col else "ADVERTENCIA"},
    ]

    errors: list[dict[str, Any]] = []
    if total != 43:
        errors.append({"control": "total_carreras_matriz", "valor": total, "esperado": 43})
    if len(direct) != 34:
        errors.append({"control": "carreras_directas", "valor": len(direct), "esperado": 34})
    if len(dupes) > 0:
        errors.append({"control": "duplicados_codigo_unico", "valor": len(dupes), "esperado": 0})
    if not pdf_col:
        errors.append({"control": "columna_pdf", "error": "no_detectada"})
    if not cobertura_col:
        errors.append({"control": "columna_cobertura", "error": "no_detectada"})

    out_universe = output_path(ctx, "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv")
    out_control = output_path(ctx, "04_AUDITORIA/01_CONTROL_UNIVERSO.tsv")
    out_dupes = output_path(ctx, "04_AUDITORIA/02_DUPLICADOS_CODIGO_UNICO.tsv")
    salidas = [
        write_tsv(direct, out_universe),
        write_tsv(pd.DataFrame(control_rows), out_control),
        write_tsv(dupes, out_dupes),
    ]

    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "total_carreras": total,
            "directas": len(direct),
            "excluidas": len(excluded),
            "duplicados_codigo_unico": len(dupes),
        },
        validaciones=control_rows,
        errores=errors,
        resumen=[
            f"Estado: {estado}",
            f"Total carreras: {total}",
            f"Directas: {len(direct)}",
            f"Excluidas: {len(excluded)}",
            f"Duplicados CODIGO_UNICO: {len(dupes)}",
            f"Universo: {out_universe.resolve()}",
        ],
        comando_reanudacion=command_for_phase(2),
    )


def hoja1_plan_values(path: Path) -> set[str]:
    hoja = read_tsv(path, normalize=True)
    plan_cols = [c for c in hoja.columns if c.startswith("PLAN_DE_ESTUDIO") or c in {"PLAN_ESTUDIOS", "PLAN"}]
    values: set[str] = set()
    for col in plan_cols:
        values.update(v for v in hoja[col].astype(str).tolist() if v != "")
    return values


def fase_2(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    entradas = ctx.input_paths()
    universe = read_tsv(output_path(ctx, "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv"), normalize=True)
    mapping = read_tsv(Path(entradas["mapeo_pdf_plan_canonico"]), normalize=True)
    pdf_u = required_column(universe, "PDF")
    pdf_m = required_column(mapping, "PDF")
    codcarr_m = required_column(mapping, "CODCARR_CANONICO")
    plan_m = required_column(mapping, "PLAN_CANONICO")
    existe_m = required_column(mapping, "EXISTE_EN_HOJA1")

    normalized_mapping = mapping.copy()
    direct_pdfs = sorted(set(v for v in universe[pdf_u].astype(str).tolist() if v != ""))
    mapped_pdfs = set(mapping[pdf_m].astype(str).tolist())
    missing_rows = [{"ARCHIVO_PDF": pdf} for pdf in direct_pdfs if pdf not in mapped_pdfs]

    dup_counts = (
        mapping.groupby(pdf_m, dropna=False)
        .size()
        .reset_index(name="N_MAPEOS_CANONICOS")
    )
    multiples = dup_counts[dup_counts["N_MAPEOS_CANONICOS"].astype(int) > 1].copy()

    plans_in_hoja1 = hoja1_plan_values(Path(entradas["hoja1_congelada"]))
    direct_mapping = mapping[mapping[pdf_m].isin(direct_pdfs)].copy()
    bad_plan_rows = []
    for _, row in direct_mapping.iterrows():
        plan = row[plan_m]
        flag_ok = truthy_si(row[existe_m])
        actual_ok = plan in plans_in_hoja1
        if not flag_ok or not actual_ok:
            bad_plan_rows.append(
                {
                    "ARCHIVO_PDF": row[pdf_m],
                    "CODCARR_CANONICO": row[codcarr_m],
                    "PLAN_DE_ESTUDIO_CANONICO": plan,
                    "EXISTE_EN_HOJA1_DECLARADO": row[existe_m],
                    "EXISTE_EN_HOJA1_VERIFICADO": "SI" if actual_ok else "NO",
                }
            )

    out_mapping = output_path(ctx, "02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv")
    out_missing = output_path(ctx, "04_AUDITORIA/03_PDF_SIN_MAPEO.tsv")
    out_multiple = output_path(ctx, "04_AUDITORIA/04_PDF_MAPEO_MULTIPLE.tsv")
    out_bad_plan = output_path(ctx, "04_AUDITORIA/05_PLANES_NO_EXISTENTES_HOJA1.tsv")
    salidas = [
        write_tsv(normalized_mapping, out_mapping),
        write_tsv(pd.DataFrame(missing_rows, columns=["ARCHIVO_PDF"]), out_missing),
        write_tsv(multiples, out_multiple),
        write_tsv(pd.DataFrame(bad_plan_rows), out_bad_plan),
    ]
    errors: list[dict[str, Any]] = []
    if missing_rows:
        errors.append({"control": "pdf_sin_mapeo", "casos": len(missing_rows), "muestra": missing_rows[:20]})
    if len(multiples) > 0:
        errors.append({"control": "pdf_mapeo_multiple", "casos": len(multiples)})
    if bad_plan_rows:
        errors.append({"control": "planes_no_existentes_hoja1", "casos": len(bad_plan_rows), "muestra": bad_plan_rows[:20]})
    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "pdf_directos": len(direct_pdfs),
            "pdf_sin_mapeo": len(missing_rows),
            "pdf_mapeo_multiple": len(multiples),
            "planes_no_existentes_hoja1": len(bad_plan_rows),
        },
        validaciones=[
            {"validacion": "pdf_directo_con_mapeo_unico", "estado": "OK" if not missing_rows and len(multiples) == 0 else "ERROR"},
            {"validacion": "plan_canonico_existe_hoja1", "estado": "OK" if not bad_plan_rows else "ERROR"},
        ],
        errores=errors,
        resumen=[
            f"Estado: {estado}",
            f"PDF directos: {len(direct_pdfs)}",
            f"PDF sin mapeo: {len(missing_rows)}",
            f"PDF con mapeo multiple: {len(multiples)}",
            f"Planes inexistentes en Hoja1: {len(bad_plan_rows)}",
            f"Mapeo normalizado: {out_mapping.resolve()}",
        ],
        comando_reanudacion=command_for_phase(3),
    )


def merge_universe_mapping(universe: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    pdf_u = required_column(universe, "PDF")
    pdf_m = required_column(mapping, "PDF")
    codcarr_m = required_column(mapping, "CODCARR_CANONICO")
    plan_m = required_column(mapping, "PLAN_CANONICO")
    cols = [pdf_m, codcarr_m, plan_m]
    if first_existing(list(mapping.columns), COLUMN_CANDIDATES["EXISTE_EN_HOJA1"]):
        cols.append(required_column(mapping, "EXISTE_EN_HOJA1"))
    universe_for_merge = universe.copy()
    for logical_name in ("CODCARR_CANONICO", "PLAN_CANONICO", "EXISTE_EN_HOJA1"):
        existing = first_existing(list(universe_for_merge.columns), COLUMN_CANDIDATES[logical_name])
        if existing:
            universe_for_merge = universe_for_merge.drop(columns=[existing])
    mapping_for_merge = mapping[cols].drop_duplicates().rename(
        columns={
            codcarr_m: "CODCARR_CANONICO",
            plan_m: "PLAN_DE_ESTUDIO_CANONICO",
            pdf_m: "ARCHIVO_PDF" if pdf_m != "ARCHIVO_PDF" else pdf_m,
        }
    )
    return universe_for_merge.merge(
        mapping_for_merge,
        left_on=pdf_u,
        right_on="ARCHIVO_PDF",
        how="left",
        suffixes=("", "_VALIDACION"),
    )


def validar_regresion_pre_fase3(ctx: RunContext) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    universe = read_tsv(output_path(ctx, "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv"), normalize=True)
    mapping = read_tsv(output_path(ctx, "02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv"), normalize=True)
    codigo_u = required_column(universe, "CODIGO_UNICO")
    pdf_u = required_column(universe, "PDF")
    pdf_m = required_column(mapping, "PDF")
    plan_m = required_column(mapping, "PLAN_CANONICO")
    existe_m = required_column(mapping, "EXISTE_EN_HOJA1")
    direct_pdfs = sorted(set(v for v in universe[pdf_u].astype(str).tolist() if v != ""))
    mapped_pdfs = set(mapping[pdf_m].astype(str).tolist())
    pdf_sin_mapeo = [pdf for pdf in direct_pdfs if pdf not in mapped_pdfs]
    pdf_multiples = (
        mapping[mapping[pdf_m].isin(direct_pdfs)]
        .groupby(pdf_m, dropna=False)
        .size()
        .reset_index(name="N")
    )
    pdf_multiples = pdf_multiples[pdf_multiples["N"].astype(int) > 1]
    planes_no_hoja1 = mapping[
        mapping[pdf_m].isin(direct_pdfs)
        & ((mapping[plan_m] == "") | (~mapping[existe_m].map(truthy_si)))
    ]
    checks = [
        {"validacion": "universo_directo_34", "valor": len(universe), "esperado": 34},
        {
            "validacion": "codigos_unicos_duplicados_0",
            "valor": int(universe[codigo_u].duplicated().sum()),
            "esperado": 0,
        },
        {"validacion": "pdf_directos_11", "valor": len(direct_pdfs), "esperado": 11},
        {"validacion": "pdf_sin_mapeo_0", "valor": len(pdf_sin_mapeo), "esperado": 0},
        {"validacion": "pdf_mapeo_multiple_0", "valor": len(pdf_multiples), "esperado": 0},
        {"validacion": "planes_inexistentes_hoja1_0", "valor": len(planes_no_hoja1), "esperado": 0},
    ]
    errors = [c for c in checks if c["valor"] != c["esperado"]]
    details = {
        "columnas_universo": list(universe.columns),
        "columnas_mapeo_fase2": list(mapping.columns),
        "columna_codigo_carrera_canonico_fase2": required_column(mapping, "CODCARR_CANONICO"),
        "columna_plan_canonico_fase2": plan_m,
        "columna_pdf_fase2": pdf_m,
        "seccion_corregida": "merge_universe_mapping/fase_3",
        "causa_error": "La union previa sufijaba columnas canonicas duplicadas y Fase 3 buscaba CODCARR_CANONICO sin sufijo.",
    }
    return checks, errors, details


def fase_3(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    entradas = ctx.input_paths()
    universe = read_tsv(output_path(ctx, "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv"), normalize=True)
    mapping = read_tsv(output_path(ctx, "02_INTERMEDIOS/02_MAPEO_PDF_PLAN_NORMALIZADO.tsv"), normalize=True)
    bridge = read_tsv(Path(entradas["puente_sies"]), normalize=True)
    regression_checks, regression_errors, diagnostic = validar_regresion_pre_fase3(ctx)
    ctx.log(
        "DIAGNOSTICO_FASE3 "
        + json.dumps(
            {
                "columnas_detectadas": {
                    "universo": diagnostic["columnas_universo"],
                    "mapeo_fase2": diagnostic["columnas_mapeo_fase2"],
                },
                "columna_seleccionada": {
                    "codigo_carrera_canonico": diagnostic["columna_codigo_carrera_canonico_fase2"],
                    "plan_canonico": diagnostic["columna_plan_canonico_fase2"],
                    "pdf": diagnostic["columna_pdf_fase2"],
                },
                "seccion_corregida": diagnostic["seccion_corregida"],
                "causa_error": diagnostic["causa_error"],
            },
            ensure_ascii=True,
        )
    )
    if regression_errors:
        return PhaseResult(
            estado="BLOQUEADA",
            conteos={
                "bloqueos_estructurales": len(regression_errors),
                "carreras_procesadas": 0,
            },
            validaciones=regression_checks,
            errores=regression_errors[:20],
            resumen=[
                "Estado: BLOQUEADA",
                f"Bloqueos estructurales: {len(regression_errors)}",
                "La Fase 3 no se ejecuto porque cambiaron validaciones previas.",
            ],
            comando_reanudacion=command_for_phase(3),
        )
    merged = merge_universe_mapping(universe, mapping)

    codigo_u = required_column(merged, "CODIGO_UNICO")
    pdf_u = required_column(merged, "PDF")
    jornada_u = first_existing(list(merged.columns), COLUMN_CANDIDATES["JORNADA"])
    codcarr_can = required_column(merged, "CODCARR_CANONICO")
    plan_can = required_column(merged, "PLAN_CANONICO")
    codigo_b = required_column(bridge, "CODIGO_UNICO_PUENTE")
    codcarpr_b = required_column(bridge, "CODCARPR")
    jornada_b = first_existing(list(bridge.columns), COLUMN_CANDIDATES["JORNADA"])
    resol_b = required_column(bridge, "RESOLUCION_STATUS")
    bloqueante_b = required_column(bridge, "ES_BLOQUEANTE")

    rows: list[dict[str, Any]] = []
    no_bridge: list[dict[str, Any]] = []
    multiple_bridge_frames: list[pd.DataFrame] = []
    codcarr_diff: list[dict[str, Any]] = []
    blocking_bridge: list[dict[str, Any]] = []

    for _, row in merged.iterrows():
        code = row[codigo_u]
        matches = bridge[bridge[codigo_b] == code].copy()
        out = {
            "CODIGO_UNICO": code,
            "ARCHIVO_PDF": row[pdf_u],
            "JORNADA_MATRIZ": row[jornada_u] if jornada_u else "",
            "CODCARR_CANONICO": row[codcarr_can],
            "PLAN_DE_ESTUDIO_CANONICO": row[plan_can],
            "PUENTE_MATCH_COUNT": len(matches),
            "CODCARPR_PUENTE": "",
            "JORNADA_PUENTE": "",
            "RESOLUCION_STATUS": "",
            "ES_BLOQUEANTE": "",
            "VALIDACION_PUENTE": "",
            "MOTIVOS_PUENTE": "",
        }
        motivos: list[str] = []
        if len(matches) == 0:
            motivos.append("CODIGO_UNICO_NO_EXISTE_PUENTE")
            no_bridge.append({"CODIGO_UNICO": code, "ARCHIVO_PDF": row[pdf_u]})
        elif len(matches) > 1:
            motivos.append("CODIGO_UNICO_MULTIPLE_EN_PUENTE")
            sample = matches.copy()
            sample.insert(0, "CODIGO_UNICO_VALIDADO", code)
            multiple_bridge_frames.append(sample)
        else:
            match = matches.iloc[0]
            out["CODCARPR_PUENTE"] = match[codcarpr_b]
            out["JORNADA_PUENTE"] = match[jornada_b] if jornada_b else ""
            out["RESOLUCION_STATUS"] = match[resol_b]
            out["ES_BLOQUEANTE"] = match[bloqueante_b]
            if match[codcarpr_b] != row[codcarr_can]:
                motivos.append("CODCARR_PUENTE_DIFIERE_CANONICO")
                codcarr_diff.append(
                    {
                        "CODIGO_UNICO": code,
                        "ARCHIVO_PDF": row[pdf_u],
                        "CODCARR_CANONICO": row[codcarr_can],
                        "CODCARPR_PUENTE": match[codcarpr_b],
                    }
                )
            if truthy_si(match[bloqueante_b]):
                motivos.append("PUENTE_MARCADO_BLOQUEANTE")
                blocking_bridge.append(
                    {
                        "CODIGO_UNICO": code,
                        "ARCHIVO_PDF": row[pdf_u],
                        "ES_BLOQUEANTE": match[bloqueante_b],
                        "RESOLUCION_STATUS": match[resol_b],
                    }
                )
        out["VALIDACION_PUENTE"] = "OK" if not motivos else "BLOQUEADO"
        out["MOTIVOS_PUENTE"] = "|".join(motivos)
        rows.append(out)

    multiple_bridge = (
        pd.concat(multiple_bridge_frames, ignore_index=True)
        if multiple_bridge_frames
        else empty_df(["CODIGO_UNICO_VALIDADO"])
    )

    out_validation = output_path(ctx, "02_INTERMEDIOS/03_VALIDACION_PUENTE_34.tsv")
    out_no_bridge = output_path(ctx, "04_AUDITORIA/06_CODIGOS_NO_EN_PUENTE.tsv")
    out_multiple = output_path(ctx, "04_AUDITORIA/07_CODIGOS_MULTIPLES_EN_PUENTE.tsv")
    out_diff = output_path(ctx, "04_AUDITORIA/08_CODCARR_DIFIERE_CANONICO.tsv")
    out_blocking = output_path(ctx, "04_AUDITORIA/09_PUENTE_BLOQUEANTE.tsv")
    salidas = [
        write_tsv(pd.DataFrame(rows), out_validation),
        write_tsv(pd.DataFrame(no_bridge), out_no_bridge),
        write_tsv(multiple_bridge, out_multiple),
        write_tsv(pd.DataFrame(codcarr_diff), out_diff),
        write_tsv(pd.DataFrame(blocking_bridge), out_blocking),
    ]

    return PhaseResult(
        estado="COMPLETADA",
        salidas=salidas,
        conteos={
            "carreras_procesadas": len(rows),
            "codigos_no_en_puente": len(no_bridge),
            "codigos_multiples_en_puente": len(multiple_bridge_frames),
            "codcarr_difiere_canonico": len(codcarr_diff),
            "puente_bloqueante": len(blocking_bridge),
        },
        validaciones=[
            {"validacion": "codigo_unico_existe_puente", "bloqueos": len(no_bridge)},
            {"validacion": "codigo_unico_relacion_unica", "bloqueos": len(multiple_bridge_frames)},
            {"validacion": "codcarpr_coincide_canonico", "bloqueos": len(codcarr_diff)},
            {"validacion": "puente_no_bloqueante", "bloqueos": len(blocking_bridge)},
        ],
        pendientes=[],
        resumen=[
            "Estado: COMPLETADA",
            f"Carreras procesadas: {len(rows)}",
            f"No en puente: {len(no_bridge)}",
            f"Multiples en puente: {len(multiple_bridge_frames)}",
            f"CODCARPR difiere: {len(codcarr_diff)}",
            f"Puente bloqueante: {len(blocking_bridge)}",
            f"Validacion puente: {out_validation.resolve()}",
        ],
        comando_reanudacion=command_for_phase(4),
    )


def fase_4(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    universe = read_tsv(output_path(ctx, "02_INTERMEDIOS/01_UNIVERSO_34_CARRERAS_DIRECTAS.tsv"), normalize=True)
    identity = read_tsv(RUTA_IDENTIDAD_34, normalize=True)
    detail_identity = read_tsv(RUTA_DETALLE_IDENTIDAD_34, normalize=True)
    comparison_pdf = read_tsv(RUTA_COMPARACION_IDENTIDAD_PDF_PLAN, normalize=True)
    comparison_bridge = read_tsv(RUTA_COMPARACION_IDENTIDAD_PUENTE, normalize=True)

    codigo_u = required_column(universe, "CODIGO_UNICO")
    plan_sies_u = first_existing(list(universe.columns), ["PLAN_ESTUDIOS"])
    pdf_u = required_column(universe, "PDF")
    identity_codes = identity["CODIGO_UNICO"].astype(str).tolist()
    errors: list[dict[str, Any]] = []
    if len(identity) != 34:
        errors.append({"control": "identidad_34_filas", "valor": len(identity), "esperado": 34})
    if identity["CODIGO_UNICO"].duplicated().any():
        errors.append({"control": "identidad_codigo_unico_duplicado", "valor": int(identity["CODIGO_UNICO"].duplicated().sum())})
    if set(identity_codes) != set(universe[codigo_u].astype(str)):
        errors.append(
            {
                "control": "identidad_no_coincide_universo",
                "ausentes": sorted(set(universe[codigo_u].astype(str)) - set(identity_codes))[:20],
                "adicionales": sorted(set(identity_codes) - set(universe[codigo_u].astype(str)))[:20],
            }
        )
    invalid_identity = identity[
        identity["ESTADO_APLICACION_34"].isin(
            ["AMBIGUO_IDENTIDAD", "BLOQUEADO_IDENTIDAD", "CONTRADICCION_PDF_PLAN", "CONTRADICCION_PUENTE", "NO_EVALUADO"]
        )
    ].copy()
    if not invalid_identity.empty:
        errors.append({"control": "identidad_no_resuelta", "valor": len(invalid_identity)})

    by_identity = identity.set_index("CODIGO_UNICO").to_dict("index")
    rows: list[dict[str, Any]] = []
    invalid_plan_sies: list[dict[str, Any]] = []
    no_eval: list[dict[str, Any]] = []
    duplicated_plan: list[dict[str, Any]] = []
    contradictions: list[dict[str, Any]] = []
    variants: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []
    seen_code_plan: set[tuple[str, str]] = set()

    for _, row in universe.iterrows():
        code = str(row[codigo_u])
        id_row = by_identity.get(code, {})
        plan_sies = id_row.get("PLAN_ESTUDIOS_SIES_UNIFICADO", "") or (str(row[plan_sies_u]) if plan_sies_u else "")
        pdf = id_row.get("ARCHIVO_PDF", "") or str(row[pdf_u])
        plan_pdf = id_row.get("PLAN_DE_ESTUDIO_CANONICO_PDF", "")
        plan_inst = id_row.get("PLAN_DE_ESTUDIO_INSTITUCIONAL_UNIFICADO", "")
        plans_observed = id_row.get("PLANES_INSTITUCIONALES_OBSERVADOS", "")

        plan_key = (code, plan_sies)
        duplicate_plan = plan_key in seen_code_plan and bool(plan_sies)
        seen_code_plan.add(plan_key)
        is_numeric = str(plan_sies).strip().isdigit()
        is_integer = is_numeric
        is_positive = is_numeric and int(str(plan_sies)) > 0
        if not plan_sies:
            plan_state = "BLOQUEADO_PLAN_ESTUDIOS_SIES_VACIO"
            plan_reason = "PLAN_ESTUDIOS_SIES vacío."
        elif not is_numeric:
            plan_state = "BLOQUEADO_PLAN_ESTUDIOS_SIES_NO_NUMERICO"
            plan_reason = "PLAN_ESTUDIOS_SIES no numérico."
        elif not is_integer:
            plan_state = "BLOQUEADO_PLAN_ESTUDIOS_SIES_NO_ENTERO"
            plan_reason = "PLAN_ESTUDIOS_SIES no entero."
        elif not is_positive:
            plan_state = "BLOQUEADO_PLAN_ESTUDIOS_SIES_NO_POSITIVO"
            plan_reason = "PLAN_ESTUDIOS_SIES no positivo."
        elif duplicate_plan:
            plan_state = "BLOQUEADO_PLAN_ESTUDIOS_SIES_DUPLICADO"
            plan_reason = "Duplicado CODIGO_UNICO + PLAN_ESTUDIOS_SIES."
        else:
            plan_state = "VALIDADO_PLAN_ESTUDIOS_SIES"
            plan_reason = "PLAN_ESTUDIOS_SIES validado como correlativo observado; no comparado contra plan institucional."
        if plan_state != "VALIDADO_PLAN_ESTUDIOS_SIES":
            invalid_plan_sies.append({"CODIGO_UNICO": code, "PLAN_ESTUDIOS_SIES": plan_sies, "ESTADO": plan_state, "MOTIVO": plan_reason})
        if duplicate_plan:
            duplicated_plan.append({"CODIGO_UNICO": code, "PLAN_ESTUDIOS_SIES": plan_sies})

        app_state = id_row.get("ESTADO_APLICACION_34", "")
        if not id_row:
            identity_state = "BLOQUEADO_IDENTIDAD_PREVIA"
            identity_reason = "CODIGO_UNICO sin identidad integrada."
        elif app_state == "VALIDADO_IDENTIDAD_CON_VARIANTES":
            identity_state = "VALIDADO_IDENTIDAD_PDF_PLAN_CON_VARIANTES"
            identity_reason = "Identidad resuelta con variantes legítimas conservadas."
        elif app_state == "VALIDADO_IDENTIDAD_COMPLETA":
            identity_state = "VALIDADO_IDENTIDAD_PDF_PLAN"
            identity_reason = "Identidad resuelta."
        elif app_state == "VALIDADO_IDENTIDAD_SIN_PLAN_INSTITUCIONAL":
            identity_state = "VALIDADO_IDENTIDAD_SIN_PLAN_INSTITUCIONAL"
            identity_reason = "Identidad resuelta sin plan institucional suficiente para comparar."
        elif app_state == "AMBIGUO_IDENTIDAD":
            identity_state = "BLOQUEADO_IDENTIDAD_AMBIGUA"
            identity_reason = "Identidad previa ambigua."
        elif app_state in {"BLOQUEADO_IDENTIDAD", "NO_EVALUADO"}:
            identity_state = "BLOQUEADO_IDENTIDAD_PREVIA"
            identity_reason = "Identidad previa bloqueada o no evaluada."
        elif app_state == "CONTRADICCION_PDF_PLAN":
            identity_state = "BLOQUEADO_CONTRADICCION_PDF_PLAN"
            identity_reason = "Contradicción PDF-plan heredada de identidad."
        else:
            identity_state = "BLOQUEADO_IDENTIDAD_PREVIA"
            identity_reason = f"Estado no válido para integración: {app_state}"

        if not pdf:
            identity_state = "BLOQUEADO_SIN_PDF"
            identity_reason = "PDF no informado."
        elif not plan_pdf:
            identity_state = "BLOQUEADO_SIN_PLAN_CANONICO"
            identity_reason = "Plan canónico PDF no informado."
        elif plans_observed and plan_pdf not in [p for p in str(plans_observed).split("|") if p]:
            identity_state = "BLOQUEADO_CONTRADICCION_PDF_PLAN"
            identity_reason = "Plan canónico PDF no está entre planes institucionales observados."

        if identity_state in {"VALIDADO_IDENTIDAD_SIN_PLAN_INSTITUCIONAL", "BLOQUEADO_IDENTIDAD_PREVIA"}:
            no_eval.append({"CODIGO_UNICO": code, "ARCHIVO_PDF": pdf, "ESTADO": identity_state, "MOTIVO": identity_reason})
        if identity_state == "BLOQUEADO_CONTRADICCION_PDF_PLAN":
            contradictions.append({"CODIGO_UNICO": code, "ARCHIVO_PDF": pdf, "PLAN_DE_ESTUDIO_CANONICO_PDF": plan_pdf, "PLANES_INSTITUCIONALES_OBSERVADOS": plans_observed})
        if id_row.get("TIENE_VARIANTES_LEGITIMAS", "") == "SI":
            variants.append(
                {
                    "CODIGO_UNICO": code,
                    "TIPO_VARIANTE": id_row.get("TIPO_VARIANTE", ""),
                    "JORNADAS_OBSERVADAS": id_row.get("JORNADAS_OBSERVADAS", ""),
                    "FUENTE_IDENTIDAD": id_row.get("FUENTE_PRINCIPAL", ""),
                }
            )
        trace.append(
            {
                "CODIGO_UNICO": code,
                "FUENTE_IDENTIDAD": id_row.get("FUENTE_PRINCIPAL", ""),
                "FUENTES_RESPALDO": id_row.get("FUENTES_RESPALDO", ""),
                "HASH_TRAZABILIDAD_IDENTIDAD": id_row.get("HASH_TRAZABILIDAD_APLICACION", ""),
                "RUTA_IDENTIDAD_34": str(RUTA_IDENTIDAD_34.resolve()),
            }
        )
        rows.append(
            {
                "CODIGO_UNICO": code,
                "ARCHIVO_PDF": pdf,
                "PLAN_DE_ESTUDIO_CANONICO_PDF": plan_pdf,
                "PLAN_ESTUDIOS_SIES": plan_sies,
                "PLAN_DE_ESTUDIO_INSTITUCIONAL_UNIFICADO": plan_inst,
                "PLANES_INSTITUCIONALES_OBSERVADOS": plans_observed,
                "JORNADA_UNIFICADA": id_row.get("JORNADA_UNIFICADA", ""),
                "JORNADAS_OBSERVADAS": id_row.get("JORNADAS_OBSERVADAS", ""),
                "CODCARR_UNIFICADO": id_row.get("CODCARR_UNIFICADO", ""),
                "CODCARPR_UNIFICADO": id_row.get("CODCARPR_UNIFICADO", ""),
                "TIPO_PLAN_CARRERA_UNIFICADO": id_row.get("TIPO_PLAN_CARRERA_UNIFICADO", ""),
                "DURACION_ESTUDIOS_UNIFICADA": id_row.get("DURACION_ESTUDIOS_UNIFICADA", ""),
                "ESTADO_IDENTIDAD": id_row.get("ESTADO_IDENTIDAD", ""),
                "ESTADO_APLICACION_34": app_state,
                "PLAN_ESTUDIOS_SIES_ES_NUMERICO": "SI" if is_numeric else "NO",
                "PLAN_ESTUDIOS_SIES_ES_ENTERO": "SI" if is_integer else "NO",
                "PLAN_ESTUDIOS_SIES_ES_POSITIVO": "SI" if is_positive else "NO",
                "PLAN_ESTUDIOS_SIES_DUPLICADO_POR_CODIGO_UNICO": "SI" if duplicate_plan else "NO",
                "ESTADO_VALIDACION_PLAN_ESTUDIOS_SIES": plan_state,
                "MOTIVO_VALIDACION_PLAN_ESTUDIOS_SIES": plan_reason,
                "ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN": identity_state,
                "MOTIVO_VALIDACION_IDENTIDAD_PDF_PLAN": identity_reason,
                "TIENE_VARIANTES_LEGITIMAS": id_row.get("TIENE_VARIANTES_LEGITIMAS", ""),
                "TIPO_VARIANTE": id_row.get("TIPO_VARIANTE", ""),
                "TIENE_CAMPO_FALTANTE_CRITICO": id_row.get("TIENE_CAMPO_FALTANTE_CRITICO", ""),
                "CAMPOS_FALTANTES": id_row.get("CAMPOS_FALTANTES", ""),
                "ES_BLOQUEANTE": id_row.get("ES_BLOQUEANTE", ""),
                "MOTIVO_BLOQUEO": id_row.get("MOTIVO_BLOQUEO", ""),
                "FUENTE_IDENTIDAD": id_row.get("FUENTE_PRINCIPAL", ""),
                "HASH_TRAZABILIDAD_IDENTIDAD": id_row.get("HASH_TRAZABILIDAD_APLICACION", ""),
                "VERSION_LOGICA_FASE4": VERSION_LOGICA_FASE4_INTEGRADA,
            }
        )

    result_df = pd.DataFrame(rows)
    blockers = result_df[
        (result_df["ESTADO_VALIDACION_PLAN_ESTUDIOS_SIES"] != "VALIDADO_PLAN_ESTUDIOS_SIES")
        | result_df["ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN"].str.startswith("BLOQUEADO", na=False)
    ].copy()
    if not blockers.empty:
        errors.append({"control": "bloqueos_fase4_integrada", "valor": len(blockers)})
    if len(result_df) != 34:
        errors.append({"control": "total_fase4_integrada", "valor": len(result_df), "esperado": 34})
    if result_df["CODIGO_UNICO"].duplicated().any():
        errors.append({"control": "duplicados_codigo_unico", "valor": int(result_df["CODIGO_UNICO"].duplicated().sum())})

    out_validation = output_path(ctx, "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv")
    out_invalid_plan = output_path(ctx, "04_AUDITORIA/10_PLAN_ESTUDIOS_SIES_INVALIDO.tsv")
    out_no_eval = output_path(ctx, "04_AUDITORIA/11_IDENTIDAD_PDF_PLAN_NO_EVALUABLE.tsv")
    out_dups = output_path(ctx, "04_AUDITORIA/12_DUPLICADOS_CODIGO_UNICO_PLAN_ESTUDIOS.tsv")
    out_contra = output_path(ctx, "04_AUDITORIA/13_CONTRADICCIONES_IDENTIDAD_PDF_PLAN.tsv")
    out_variants = output_path(ctx, "04_AUDITORIA/14_VARIANTES_LEGITIMAS_34.tsv")
    out_trace = output_path(ctx, "04_AUDITORIA/15_TRAZABILIDAD_IDENTIDAD_INTEGRADA.tsv")
    out_json = output_path(ctx, "04_AUDITORIA/CORRECCION_FUNCIONAL_FASE4_INTEGRACION_IDENTIDAD.json")
    salidas = [
        write_tsv(result_df, out_validation),
        write_tsv(pd.DataFrame(invalid_plan_sies), out_invalid_plan),
        write_tsv(pd.DataFrame(no_eval), out_no_eval),
        write_tsv(pd.DataFrame(duplicated_plan), out_dups),
        write_tsv(pd.DataFrame(contradictions), out_contra),
        write_tsv(pd.DataFrame(variants), out_variants),
        write_tsv(pd.DataFrame(trace), out_trace),
        write_json(
            {
                "fecha": now_iso(),
                "script_modificado": str(Path(__file__).resolve()),
                "respaldo_script": "backups/validar_pdf_plan_34_directas_pre_integracion_identidad_*.py",
                "causa_raiz": "Comparacion conceptual incorrecta entre PLAN_ESTUDIOS_SIES y PLAN_DE_ESTUDIO_INSTITUCIONAL.",
                "logica_anterior": "PLAN_MATRIZ == PLAN_DE_ESTUDIO_CANONICO",
                "logica_nueva": VERSION_LOGICA_FASE4_INTEGRADA,
                "entrada_identidad": str(RUTA_IDENTIDAD_34.resolve()),
                "hash_entrada_identidad": sha256_file(RUTA_IDENTIDAD_34),
                "carreras_esperadas": 34,
                "carreras_recibidas": len(identity),
                "comparacion_eliminada": "PLAN_ESTUDIOS_SIES_vs_PLAN_DE_ESTUDIO_INSTITUCIONAL",
                "separacion_plan_sies_plan_institucional": True,
                "variantes_conservadas": True,
                "conteos": {
                    "carreras_evaluadas": len(result_df),
                    "identidades_con_variantes": int((result_df["TIENE_VARIANTES_LEGITIMAS"] == "SI").sum()),
                    "multiples_jornadas": int(result_df["JORNADAS_OBSERVADAS"].str.contains(r"\\|", regex=True, na=False).sum()),
                    "contradicciones_pdf_plan": len(contradictions),
                    "bloqueos": len(blockers),
                    "relaciones_detalle_identidad": len(detail_identity),
                    "comparacion_pdf_plan_fase5": len(comparison_pdf),
                    "comparacion_puente_fase5": len(comparison_bridge),
                },
                "originales_modificados": False,
                "precarga_generada": False,
                "pes_generado": False,
            },
            out_json,
        ),
    ]
    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "carreras_procesadas": len(result_df),
            "identidades_resueltas": int(result_df["ESTADO_VALIDACION_IDENTIDAD_PDF_PLAN"].isin(["VALIDADO_IDENTIDAD_PDF_PLAN", "VALIDADO_IDENTIDAD_PDF_PLAN_CON_VARIANTES"]).sum()),
            "identidades_con_variantes": int((result_df["TIENE_VARIANTES_LEGITIMAS"] == "SI").sum()),
            "multiples_jornadas": int(result_df["JORNADAS_OBSERVADAS"].str.contains(r"\\|", regex=True, na=False).sum()),
            "contradicciones_pdf_plan": len(contradictions),
            "bloqueos": len(blockers),
            "version_logica_fase4": VERSION_LOGICA_FASE4_INTEGRADA,
        },
        validaciones=[
            {"validacion": "plan_estudios_sies_separado", "estado": "OK"},
            {"validacion": "plan_institucional_desde_identidad", "estado": "OK"},
            {"validacion": "sin_comparacion_plan_sies_vs_plan_institucional", "estado": "OK"},
            {"validacion": "identidad_34_unica", "estado": "OK" if not errors else "ERROR", "errores": len(errors)},
        ],
        errores=errors,
        entradas={
            "identidad_34": str(RUTA_IDENTIDAD_34.resolve()),
            "detalle_identidad_34": str(RUTA_DETALLE_IDENTIDAD_34.resolve()),
            "comparacion_identidad_pdf_plan": str(RUTA_COMPARACION_IDENTIDAD_PDF_PLAN.resolve()),
            "comparacion_identidad_puente": str(RUTA_COMPARACION_IDENTIDAD_PUENTE.resolve()),
        },
        hashes={
            "identidad_34": sha256_file(RUTA_IDENTIDAD_34),
            "detalle_identidad_34": sha256_file(RUTA_DETALLE_IDENTIDAD_34),
        },
        resumen=[
            f"Estado: {estado}",
            f"Version logica Fase 4: {VERSION_LOGICA_FASE4_INTEGRADA}",
            f"Carreras evaluadas: {len(result_df)}",
            f"Identidades con variantes: {int((result_df['TIENE_VARIANTES_LEGITIMAS'] == 'SI').sum())}",
            f"Multiples jornadas preservadas: {int(result_df['JORNADAS_OBSERVADAS'].str.contains(r'\\|', regex=True, na=False).sum())}",
            f"Contradicciones PDF-plan: {len(contradictions)}",
            f"Bloqueos: {len(blockers)}",
            f"Validacion integrada: {out_validation.resolve()}",
        ],
        comando_reanudacion=command_for_phase(5),
    )


def fase_5(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    bridge_validation = read_tsv(output_path(ctx, "02_INTERMEDIOS/03_VALIDACION_PUENTE_34.tsv"), normalize=True)
    plan_validation = read_tsv(output_path(ctx, "02_INTERMEDIOS/04_VALIDACION_PLAN_MATRIZ.tsv"), normalize=True)
    plan_by_code = plan_validation.set_index("CODIGO_UNICO").to_dict("index")
    rows: list[dict[str, Any]] = []

    for _, row in bridge_validation.iterrows():
        code = row["CODIGO_UNICO"]
        plan_row = plan_by_code.get(code, {})
        reasons: list[str] = []
        if row.get("ARCHIVO_PDF", "") == "":
            reasons.append("PDF_NO_INFORMADO")
        bridge_reasons = [r for r in str(row.get("MOTIVOS_PUENTE", "")).split("|") if r]
        reasons.extend(bridge_reasons)
        plan_status = plan_row.get("ESTADO_VALIDACION_PLAN_MATRIZ", "")
        if plan_status == "PLAN_MATRIZ_DIFIERE_CANONICO":
            reasons.append("PLAN_MATRIZ_DIFIERE_CANONICO")
        reasons = [r if r in BLOCK_REASONS else "OTRO_BLOQUEO_DOCUMENTADO" for r in reasons]
        reasons = list(dict.fromkeys(reasons))

        if reasons:
            estado = "BLOQUEADO"
        elif plan_status == "NO_EVALUABLE":
            estado = "VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ"
        else:
            estado = "VALIDADO_DIRECTO_PDF_PLAN"

        rows.append(
            {
                "CODIGO_UNICO": code,
                "ARCHIVO_PDF": row.get("ARCHIVO_PDF", ""),
                "CODCARR_CANONICO": row.get("CODCARR_CANONICO", ""),
                "PLAN_DE_ESTUDIO_CANONICO": row.get("PLAN_DE_ESTUDIO_CANONICO", ""),
                "ESTADO_VALIDACION": estado,
                "MOTIVOS_BLOQUEO": "|".join(reasons),
                "ESTADO_VALIDACION_PLAN_MATRIZ": plan_status,
                "CODCARPR_PUENTE": row.get("CODCARPR_PUENTE", ""),
                "ES_BLOQUEANTE": row.get("ES_BLOQUEANTE", ""),
                "RESOLUCION_STATUS": row.get("RESOLUCION_STATUS", ""),
            }
        )

    result_df = pd.DataFrame(rows)
    validated = result_df[result_df["ESTADO_VALIDACION"] == "VALIDADO_DIRECTO_PDF_PLAN"].copy()
    partial = result_df[result_df["ESTADO_VALIDACION"] == "VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ"].copy()
    blocked = result_df[result_df["ESTADO_VALIDACION"] == "BLOQUEADO"].copy()
    resumen_estados = (
        result_df.groupby("ESTADO_VALIDACION", dropna=False)
        .size()
        .reset_index(name="TOTAL")
    )
    block_rows: list[dict[str, Any]] = []
    for reason in sorted(BLOCK_REASONS):
        count = blocked["MOTIVOS_BLOQUEO"].str.contains(reason, regex=False).sum() if not blocked.empty else 0
        if count:
            block_rows.append({"MOTIVO_BLOQUEO": reason, "TOTAL": int(count)})

    errors: list[dict[str, Any]] = []
    if len(result_df) != 34:
        errors.append({"control": "total_resultado", "valor": len(result_df), "esperado": 34})
    if result_df["CODIGO_UNICO"].duplicated().any():
        errors.append({"control": "duplicados_codigo_unico", "valor": int(result_df["CODIGO_UNICO"].duplicated().sum())})
    if (result_df["ESTADO_VALIDACION"] == "").any():
        errors.append({"control": "filas_sin_estado", "valor": int((result_df["ESTADO_VALIDACION"] == "").sum())})
    invalid_states = sorted(set(result_df["ESTADO_VALIDACION"]) - FINAL_STATES)
    if invalid_states:
        errors.append({"control": "estado_no_permitido", "valores": invalid_states})
    if len(validated) + len(partial) + len(blocked) != 34:
        errors.append(
            {
                "control": "estados_suman_34",
                "valor": len(validated) + len(partial) + len(blocked),
                "esperado": 34,
            }
        )

    out_all = output_path(ctx, "03_RESULTADOS/01_VALIDACION_INDIVIDUAL_34_DIRECTAS.tsv")
    out_valid = output_path(ctx, "03_RESULTADOS/02_CARRERAS_DIRECTAS_VALIDADAS.tsv")
    out_partial = output_path(ctx, "03_RESULTADOS/03_CARRERAS_VALIDACION_PARCIAL.tsv")
    out_blocked = output_path(ctx, "03_RESULTADOS/04_CARRERAS_DIRECTAS_BLOQUEADAS.tsv")
    out_states = output_path(ctx, "04_AUDITORIA/12_RESUMEN_ESTADOS.tsv")
    out_blocks = output_path(ctx, "04_AUDITORIA/13_RESUMEN_BLOQUEOS.tsv")
    salidas = [
        write_tsv(result_df, out_all),
        write_tsv(validated, out_valid),
        write_tsv(partial, out_partial),
        write_tsv(blocked, out_blocked),
        write_tsv(resumen_estados, out_states),
        write_tsv(pd.DataFrame(block_rows), out_blocks),
    ]
    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "total": len(result_df),
            "validadas": len(validated),
            "parciales": len(partial),
            "bloqueadas": len(blocked),
        },
        validaciones=[
            {"validacion": "estados_suman_34", "estado": "OK" if not errors else "ERROR"},
            {"validacion": "una_fila_por_codigo_unico", "estado": "OK" if not result_df["CODIGO_UNICO"].duplicated().any() else "ERROR"},
        ],
        errores=errors,
        resumen=[
            f"Estado: {estado}",
            f"Total: {len(result_df)}",
            f"Validadas: {len(validated)}",
            f"Parciales: {len(partial)}",
            f"Bloqueadas: {len(blocked)}",
            f"Resultado: {out_all.resolve()}",
        ],
        comando_reanudacion=command_for_phase(6),
    )


def fase_6(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    entradas = ctx.input_paths()
    classified = read_tsv(output_path(ctx, "03_RESULTADOS/01_VALIDACION_INDIVIDUAL_34_DIRECTAS.tsv"), normalize=True)
    totals = read_tsv(Path(entradas["totales_documentales"]), normalize=True)
    pdf_col = required_column(totals, "PDF")
    total_col = required_column(totals, "TOTAL_UNIDADES")

    counts = totals.groupby(pdf_col, dropna=False).size().reset_index(name="N_TOTALES")
    multiple = counts[counts["N_TOTALES"].astype(int) > 1].copy()
    totals_one = totals.drop_duplicates(subset=[pdf_col], keep=False).set_index(pdf_col).to_dict("index")
    rows: list[dict[str, Any]] = []
    missing_total: list[dict[str, Any]] = []

    for _, row in classified.iterrows():
        out = row.to_dict()
        out["TIPO_UNIDAD_MEDIDA_CANDIDATO"] = ""
        out["TOTAL_UNIDADES_CANDIDATO"] = ""
        pdf = row.get("ARCHIVO_PDF", "")
        if row["ESTADO_VALIDACION"] == "VALIDADO_DIRECTO_PDF_PLAN":
            total_row = totals_one.get(pdf)
            if not total_row:
                missing_total.append({"CODIGO_UNICO": row["CODIGO_UNICO"], "ARCHIVO_PDF": pdf})
            else:
                out["TIPO_UNIDAD_MEDIDA_CANDIDATO"] = "1"
                out["TOTAL_UNIDADES_CANDIDATO"] = total_row[total_col]
        rows.append(out)

    result_df = pd.DataFrame(rows)
    out_result = output_path(ctx, "03_RESULTADOS/05_VALIDACION_34_CON_TOTALES_CANDIDATOS.tsv")
    out_missing = output_path(ctx, "04_AUDITORIA/14_PDF_SIN_TOTAL.tsv")
    out_multiple = output_path(ctx, "04_AUDITORIA/15_PDF_CON_TOTALES_MULTIPLES.tsv")
    salidas = [
        write_tsv(result_df, out_result),
        write_tsv(pd.DataFrame(missing_total), out_missing),
        write_tsv(multiple, out_multiple),
    ]
    errors: list[dict[str, Any]] = []
    if missing_total:
        errors.append({"control": "carrera_validada_sin_total_documental_unico", "casos": len(missing_total), "muestra": missing_total[:20]})
    if len(multiple) > 0:
        errors.append({"control": "pdf_con_totales_multiples", "casos": len(multiple)})
    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "filas": len(result_df),
            "pdf_sin_total": len(missing_total),
            "pdf_con_totales_multiples": len(multiple),
            "candidatos_con_total": int((result_df["TOTAL_UNIDADES_CANDIDATO"] != "").sum()),
        },
        validaciones=[
            {"validacion": "solo_validadas_reciben_total", "estado": "OK"},
            {"validacion": "total_documental_unico_para_validadas", "estado": "OK" if not errors else "ERROR"},
        ],
        errores=errors,
        resumen=[
            f"Estado: {estado}",
            f"Filas: {len(result_df)}",
            f"PDF sin total: {len(missing_total)}",
            f"PDF con totales multiples: {len(multiple)}",
            f"Resultado con candidatos: {out_result.resolve()}",
        ],
        comando_reanudacion=command_for_phase(7),
    )


def all_required_outputs(ctx: RunContext) -> list[str]:
    outputs: list[str] = []
    for i in range(7):
        outputs.extend(ctx.state.get("fases", {}).get(phase_key(i), {}).get("salidas", []))
    return outputs


def fase_7(ctx: RunContext, _args: argparse.Namespace) -> PhaseResult:
    entradas = ctx.input_paths()
    matrix = read_tsv(Path(entradas["mapeo_seguro_43"]), normalize=True)
    final_df = read_tsv(output_path(ctx, "03_RESULTADOS/05_VALIDACION_34_CON_TOTALES_CANDIDATOS.tsv"), normalize=True)

    direct_count = int((matrix[required_column(matrix, "COBERTURA")] == "COBERTURA_DIRECTA_PDF").sum())
    total_original = len(matrix)
    excluded = total_original - direct_count
    summary_states = (
        final_df.groupby("ESTADO_VALIDACION", dropna=False)
        .size()
        .reset_index(name="TOTAL")
    )
    resumen_pdf = (
        final_df.groupby(["ARCHIVO_PDF", "ESTADO_VALIDACION"], dropna=False)
        .size()
        .reset_index(name="TOTAL")
    )
    block_rows: list[dict[str, Any]] = []
    blocked = final_df[final_df["ESTADO_VALIDACION"] == "BLOQUEADO"].copy()
    for reason in sorted(BLOCK_REASONS):
        count = blocked["MOTIVOS_BLOQUEO"].str.contains(reason, regex=False).sum() if not blocked.empty else 0
        if count:
            block_rows.append({"MOTIVO_BLOQUEO": reason, "TOTAL": int(count)})

    validations: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    def add_validation(name: str, ok: bool, value: Any = "", expected: Any = "") -> None:
        validations.append(
            {
                "validacion": name,
                "estado": "OK" if ok else "ERROR",
                "valor": value,
                "esperado": expected,
            }
        )
        if not ok:
            errors.append({"control": name, "valor": value, "esperado": expected})

    add_validation("43_carreras_matriz_original", total_original == 43, total_original, 43)
    add_validation("34_directas_procesadas", len(final_df) == 34 and direct_count == 34, f"{len(final_df)}/{direct_count}", 34)
    add_validation("9_no_directas_excluidas", excluded == 9, excluded, 9)
    add_validation("sin_duplicados_codigo_unico", not final_df["CODIGO_UNICO"].duplicated().any(), int(final_df["CODIGO_UNICO"].duplicated().sum()), 0)
    add_validation("estados_suman_34", len(final_df) == 34, len(final_df), 34)

    validated_mask = final_df["ESTADO_VALIDACION"] == "VALIDADO_DIRECTO_PDF_PLAN"
    non_validated_mask = ~validated_mask
    valid_has_totals = (
        (final_df.loc[validated_mask, "TIPO_UNIDAD_MEDIDA_CANDIDATO"] != "")
        & (final_df.loc[validated_mask, "TOTAL_UNIDADES_CANDIDATO"] != "")
    ).all()
    non_valid_empty = (
        (final_df.loc[non_validated_mask, "TIPO_UNIDAD_MEDIDA_CANDIDATO"] == "")
        & (final_df.loc[non_validated_mask, "TOTAL_UNIDADES_CANDIDATO"] == "")
    ).all()
    add_validation("solo_validadas_tienen_candidatos", bool(valid_has_totals), "", "validadas con campos candidatos")
    add_validation("parciales_bloqueadas_sin_totales", bool(non_valid_empty), "", "campos candidatos vacios")

    original_hash_errors: list[dict[str, Any]] = []
    stored_hashes = ctx.state["fases"]["fase_0"].get("hashes", {})
    for logical, old_hash in stored_hashes.items():
        current = sha256_file(Path(entradas[logical]))
        if current != old_hash:
            original_hash_errors.append({"entrada": logical, "hash_original": old_hash, "hash_actual": current})
    add_validation("hash_entradas_se_mantiene", len(original_hash_errors) == 0, len(original_hash_errors), 0)

    generated_files = [str(p.name).upper() for p in ctx.run_dir.rglob("*") if p.is_file()]
    precarga_generated = any("PRECARGA" in name for name in generated_files)
    pes_generated = any(re.search(r"(^|_)PES(_|\\.|$)", name) for name in generated_files)
    add_validation("no_se_genero_precarga", not precarga_generated, "NO" if not precarga_generated else "SI", "NO")
    add_validation("no_se_genero_pes", not pes_generated, "NO" if not pes_generated else "SI", "NO")

    output_rows: list[dict[str, Any]] = []
    unreadable_outputs: list[dict[str, Any]] = []
    for out in all_required_outputs(ctx):
        path = Path(out)
        row = {
            "ruta_absoluta": str(path),
            "existe": "SI" if path.exists() else "NO",
            "legible": "NO",
            "bytes": path.stat().st_size if path.exists() else "",
            "error": "",
        }
        if path.exists() and path.suffix.lower() == ".tsv":
            try:
                _ = read_tsv(path)
                row["legible"] = "SI"
            except Exception as exc:  # noqa: BLE001
                row["error"] = str(exc)
                unreadable_outputs.append({"ruta": str(path), "error": str(exc)})
        elif path.exists():
            row["legible"] = "SI"
        else:
            unreadable_outputs.append({"ruta": str(path), "error": "no_existe"})
        output_rows.append(row)
    add_validation("salidas_existen_y_son_legibles", len(unreadable_outputs) == 0, len(unreadable_outputs), 0)

    integrity_rows = validations + [
        {
            "validacion": "originales_modificados",
            "estado": "OK" if not original_hash_errors else "ERROR",
            "valor": "NO" if not original_hash_errors else "SI",
            "esperado": "NO",
        },
        {
            "validacion": "apto_para_carga",
            "estado": "NO",
            "valor": "NO",
            "esperado": "NO",
        },
    ]

    out_summary = output_path(ctx, "03_RESULTADOS/06_RESUMEN_VALIDACION_34.tsv")
    out_pdf = output_path(ctx, "03_RESULTADOS/07_RESUMEN_VALIDACION_POR_PDF.tsv")
    out_blocks = output_path(ctx, "03_RESULTADOS/08_RESUMEN_BLOQUEOS.tsv")
    out_integrity = output_path(ctx, "04_AUDITORIA/16_CONTROL_INTEGRIDAD_FINAL.tsv")
    out_inventory = output_path(ctx, "04_AUDITORIA/17_INVENTARIO_SALIDAS.tsv")
    salidas = [
        write_tsv(summary_states, out_summary),
        write_tsv(resumen_pdf, out_pdf),
        write_tsv(pd.DataFrame(block_rows), out_blocks),
        write_tsv(pd.DataFrame(integrity_rows), out_integrity),
        write_tsv(pd.DataFrame(output_rows), out_inventory),
    ]

    counts_by_state = {row["ESTADO_VALIDACION"]: int(row["TOTAL"]) for row in summary_states.to_dict("records")}
    manifiesto = {
        "proceso": PROCESO,
        "subproceso": SUBPROCESO,
        "ano_proceso": ANO_PROCESO,
        "ano_referencia_datos": ANO_REFERENCIA_DATOS,
        "run_dir": str(ctx.run_dir.resolve()),
        "fecha_cierre": now_iso(),
        "resumen_estados": counts_by_state,
        "originales_modificados": "NO" if not original_hash_errors else "SI",
        "precarga_modificada": "NO",
        "pes_generado": "NO" if not pes_generated else "SI",
        "apto_para_carga": "NO",
        "validaciones": validations,
        "errores": errors,
    }
    out_manifest = output_path(ctx, "00_CONTROL/manifiesto_final.json")
    salidas.append(write_json(manifiesto, out_manifest))
    salidas.append(str(ctx.log_path.resolve()))

    estado = "COMPLETADA" if not errors else "BLOQUEADA"
    return PhaseResult(
        estado=estado,
        salidas=salidas,
        conteos={
            "VALIDADO_DIRECTO_PDF_PLAN": counts_by_state.get("VALIDADO_DIRECTO_PDF_PLAN", 0),
            "VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ": counts_by_state.get("VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ", 0),
            "BLOQUEADO": counts_by_state.get("BLOQUEADO", 0),
            "TOTAL": len(final_df),
        },
        validaciones=validations,
        errores=errors[:20],
        resumen=[
            f"Estado: {estado}",
            "VALIDACION INDIVIDUAL PDF-PLAN COMPLETADA" if estado == "COMPLETADA" else "VALIDACION FINAL BLOQUEADA",
            f"VALIDADO_DIRECTO_PDF_PLAN: {counts_by_state.get('VALIDADO_DIRECTO_PDF_PLAN', 0)}",
            f"VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ: {counts_by_state.get('VALIDACION_PARCIAL_SIN_PLAN_EN_MATRIZ', 0)}",
            f"BLOQUEADO: {counts_by_state.get('BLOQUEADO', 0)}",
            f"TOTAL = {len(final_df)}",
            f"Originales modificados: {'NO' if not original_hash_errors else 'SI'}",
            "Precarga modificada: NO",
            f"PES generado: {'NO' if not pes_generated else 'SI'}",
            "Apto para carga: NO",
            f"Manifiesto final: {out_manifest.resolve()}",
        ],
        comando_reanudacion="",
    )


PHASE_FUNCS: dict[int, Callable[[RunContext, argparse.Namespace], PhaseResult]] = {
    0: fase_0,
    1: fase_1,
    2: fase_2,
    3: fase_3,
    4: fase_4,
    5: fase_5,
    6: fase_6,
    7: fase_7,
}


def parse_phase(value: str | None) -> int | str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text == "final":
        return "final"
    if text.isdigit() and 0 <= int(text) <= 7:
        return int(text)
    raise FlujoError("--fase debe ser 0, 1, 2, 3, 4, 5, 6, 7 o final.")


def next_incomplete_phase(ctx: RunContext) -> int:
    for i in range(8):
        if phase_status(ctx.state, i) != "COMPLETADA":
            return i
    return 7


def determine_run_dir(args: argparse.Namespace, phase: int | str | None) -> Path:
    if args.reanudar or (isinstance(phase, int) and phase > 0) or phase == "final":
        run = latest_execution(prefer_incomplete=True)
        if run is None:
            if phase in (0, None):
                return create_run_dir()
            raise FlujoError("No existe una carpeta de ejecucion previa para reanudar.")
        return run
    return create_run_dir()


def phases_to_run(args: argparse.Namespace, phase: int | str | None, ctx: RunContext) -> list[int]:
    if phase == "final":
        if args.reanudar:
            start = next_incomplete_phase(ctx)
            return list(range(start, 8))
        return [7]
    if isinstance(phase, int):
        return [phase]
    if args.reanudar:
        return [next_incomplete_phase(ctx)]
    return [0]


def ensure_previous_completed(ctx: RunContext, phase: int, force: bool) -> None:
    if phase == 0:
        return
    previous = phase - 1
    status = phase_status(ctx.state, previous)
    if status != "COMPLETADA":
        raise FlujoError(
            f"No se puede ejecutar fase {phase}: fase {previous} esta en estado {status}."
        )
    if force:
        return


def run_phase(ctx: RunContext, phase: int, args: argparse.Namespace) -> int:
    status = phase_status(ctx.state, phase)
    if status == "COMPLETADA" and not args.forzar:
        result = PhaseResult(
            estado="COMPLETADA",
            resumen=[
                f"Fase {phase} ya estaba completada; no se recalculo.",
                f"Carpeta de ejecucion: {ctx.run_dir.resolve()}",
            ],
            comando_reanudacion=command_for_phase(phase + 1 if phase < 7 else "final"),
        )
        print_result(f"FASE {phase} OMITIDA", result)
        return 0

    ensure_previous_completed(ctx, phase, args.forzar)
    ctx.start_phase(phase)
    try:
        result = PHASE_FUNCS[phase](ctx, args)
    except Exception as exc:  # noqa: BLE001
        result = PhaseResult(
            estado="ERROR",
            errores=[{"error": str(exc)}],
            resumen=[f"Estado: ERROR", f"Detalle: {exc}"],
            comando_reanudacion=command_for_phase(phase),
        )
        ctx.finish_phase(phase, result)
        print_result(f"FASE {phase} ERROR", result)
        return 1

    ctx.finish_phase(phase, result)
    title = f"FASE {phase} COMPLETADA" if result.estado == "COMPLETADA" else f"FASE {phase} BLOQUEADA"
    print_result(title, result)
    return 0 if result.estado == "COMPLETADA" else 2


def solo_validar() -> int:
    run = latest_execution(prefer_incomplete=True)
    if run is None:
        print("No hay ejecuciones VALIDACION_INDIVIDUAL_PDF_PLAN para validar.")
        return 1
    ctx = RunContext(run)
    print(f"Ejecucion: {ctx.run_dir.resolve()}")
    for i in range(8):
        print(f"Fase {i}: {phase_status(ctx.state, i)}")
    try:
        entradas = ctx.input_paths()
        stored_hashes = ctx.state["fases"]["fase_0"].get("hashes", {})
        mismatches = []
        for logical, old_hash in stored_hashes.items():
            current = sha256_file(Path(entradas[logical]))
            if current != old_hash:
                mismatches.append(logical)
        print(f"Hashes de entradas sin cambios: {'SI' if not mismatches else 'NO'}")
        if mismatches:
            print(f"Entradas con hash distinto: {', '.join(mismatches[:20])}")
    except Exception as exc:  # noqa: BLE001
        print(f"No fue posible validar hashes: {exc}")
        return 1
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
            print(f"Carpeta de ejecucion: {ctx.run_dir.resolve()}")
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
