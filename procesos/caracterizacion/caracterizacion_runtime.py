#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Administracion trazable de ejecuciones de caracterizacion.py."""

from __future__ import annotations

import atexit
import csv
import hashlib
import json
import os
import shutil
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from caracterizacion_limesurvey_policy import POLITICA_PENDIENTES_LIMESURVEY_ID

TZ_NAME = "America/Santiago"
TZ = ZoneInfo(TZ_NAME)
DEFAULT_ARCHIVO_BASE = Path(
    "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion"
)
OUTPUT_EXTENSIONS = {".csv", ".xlsx", ".xls", ".docx", ".txt", ".json", ".html", ".pdf"}
DELIVERY_EXCEL_PREFIXES_2027 = (
    'Lista_tokens_categorias_SI_', 'VCM_Emprendimientos_formalizados_', 'financiamiento_',
    'BD_Comunicaciones_', 'Consolidado_eliminados_reporte_',
    'Actualmente_eliminados_matricula_en_ventana_',
    'Conflictos_tokens_duplicados_vigentes_',
)
AUDIT_HINTS = (
    "AUDITORIA",
    "AUDIT",
    "DIFERENCIA",
    "DIFERENCIAS",
    "CONFLICTO",
    "CONFLICTOS",
    "VALIDACION",
    "VALIDACIONES",
    "MANIFEST",
    "RESUMEN_EJECUCION",
)


class TeeStream:
    def __init__(self, original: Any, log_file: Any) -> None:
        self.original = original
        self.log_file = log_file

    def write(self, data: str) -> int:
        self.original.write(data)
        self.log_file.write(data)
        return len(data)

    def flush(self) -> None:
        self.original.flush()
        self.log_file.flush()

    def isatty(self) -> bool:
        return bool(getattr(self.original, "isatty", lambda: False)())


class BufferStream:
    def __init__(self, original: Any, buffer: list[str]) -> None:
        self.original = original
        self.buffer = buffer

    def write(self, data: str) -> int:
        self.original.write(data)
        self.buffer.append(data)
        return len(data)

    def flush(self) -> None:
        self.original.flush()

    def isatty(self) -> bool:
        return bool(getattr(self.original, "isatty", lambda: False)())


@dataclass
class RunContext:
    anio: int
    periodo: int
    inicio: datetime
    run_dir: Path
    input_dir: Path
    output_dir: Path
    log_dir: Path
    audit_dir: Path
    log_path: Path
    entradas: list[dict[str, Any]] = field(default_factory=list)
    decisiones_salidas_condicionales: dict[str, dict[str, Any]] = field(default_factory=dict)
    error: str | None = None
    estado: str = "OK"
    codigo_salida: int = 0
    _log_handle: Any = None
    _stdout_original: Any = None
    _stderr_original: Any = None
    _finalized: bool = False
    _known_outputs_at_start: set[Path] = field(default_factory=set)
    desktop_dir: Path | None = None
    desktop_copy_status: str = "NO_APLICA"
    desktop_copy_warning: str | None = None

    @property
    def analysis_dir(self) -> Path:
        return self.run_dir / "05_ANALISIS"


ACTIVE_CONTEXT: RunContext | None = None
_PREINIT_ACTIVE = False
_PREINIT_STDOUT_ORIGINAL: Any = None
_PREINIT_STDERR_ORIGINAL: Any = None
_PREINIT_BUFFER: list[str] = []


def now_scl() -> datetime:
    return datetime.now(TZ)


def start_preinit_capture() -> None:
    global _PREINIT_ACTIVE, _PREINIT_STDOUT_ORIGINAL, _PREINIT_STDERR_ORIGINAL
    if _PREINIT_ACTIVE:
        return
    _PREINIT_ACTIVE = True
    _PREINIT_STDOUT_ORIGINAL = sys.stdout
    _PREINIT_STDERR_ORIGINAL = sys.stderr
    sys.stdout = BufferStream(sys.stdout, _PREINIT_BUFFER)
    sys.stderr = BufferStream(sys.stderr, _PREINIT_BUFFER)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for i in range(1, 10000):
        candidate = parent / f"{stem}_{i:03d}{suffix}"
        if not candidate.exists():
            return candidate
    return parent / f"{stem}_{now_scl().strftime('%H%M%S_%f')}{suffix}"


def desktop_copy_base() -> Path:
    override = os.environ.get("CARACTERIZACION_DESKTOP_BASE")
    if override:
        return Path(override).expanduser()
    return Path.home() / "Desktop"


def desktop_copy_target(ctx: RunContext, termino: datetime | None = None) -> Path:
    termino = termino or now_scl()
    name = f"Caracterizacion_{termino.strftime('%Y-%m-%d')}_{ctx.anio}_P{ctx.periodo}_{termino.strftime('%H%M%S')}"
    return unique_path(desktop_copy_base() / name)


def _directory_file_set(base: Path) -> set[Path]:
    if not base.exists():
        return set()
    return {path.relative_to(base) for path in base.rglob("*") if path.is_file()}


def validate_directory_copy(source: Path, target: Path) -> dict[str, int]:
    source = source.resolve()
    target = target.resolve()
    src_files = _directory_file_set(source)
    dst_files = _directory_file_set(target)
    missing = sorted(src_files - dst_files, key=str)
    extra = sorted(dst_files - src_files, key=str)
    if missing or extra:
        raise RuntimeError(
            "La copia al Escritorio no conserva el conjunto de archivos: "
            f"faltantes={len(missing)} extras={len(extra)}"
        )

    total_bytes = 0
    checked = 0
    for rel in sorted(src_files, key=str):
        src = source / rel
        dst = target / rel
        src_size = src.stat().st_size
        dst_size = dst.stat().st_size
        if src_size != dst_size:
            raise RuntimeError(f"Tamano distinto en copia de Escritorio: {rel} ({src_size} != {dst_size})")
        src_sha = sha256_file(src)
        dst_sha = sha256_file(dst)
        if src_sha != dst_sha:
            raise RuntimeError(f"SHA-256 distinto en copia de Escritorio: {rel}")
        total_bytes += int(src_size)
        checked += 1
    return {"archivos_verificados": checked, "bytes_verificados": total_bytes}


def is_audit_filename(name: str) -> bool:
    upper = name.upper()
    return any(hint in upper for hint in AUDIT_HINTS)


def build_run_dir(anio: int, periodo: int, start: datetime | None = None) -> Path:
    start = start or now_scl()
    env_run_dir = os.environ.get("CARACTERIZACION_RUN_DIR", "").strip()
    if env_run_dir:
        return Path(env_run_dir).expanduser()
    base = Path(os.environ.get("CARACTERIZACION_ARCHIVO_BASE", str(DEFAULT_ARCHIVO_BASE))).expanduser()
    return base / start.strftime("%Y-%m-%d") / f"{anio}_P{periodo}_{start.strftime('%H%M%S')}"


def prepare_run_context(
    anio: int,
    periodo: int,
    *,
    external_tee: bool = False,
    start: datetime | None = None,
) -> RunContext:
    global ACTIVE_CONTEXT
    if ACTIVE_CONTEXT is not None:
        return ACTIVE_CONTEXT

    inicio = start or now_scl()
    run_dir = build_run_dir(anio, periodo, inicio)
    input_dir = run_dir / "01_ENTRADAS"
    output_dir = run_dir / "02_SALIDAS"
    log_dir = run_dir / "03_LOGS"
    audit_dir = run_dir / "04_AUDITORIA"
    for path in (input_dir, output_dir, log_dir, audit_dir):
        path.mkdir(parents=True, exist_ok=True)
    if (int(anio), int(periodo)) == (2027, 1):
        (run_dir / "05_ANALISIS").mkdir(parents=True, exist_ok=True)

    env_log_path = os.environ.get("CARACTERIZACION_LOG_PATH", "").strip()
    if env_log_path:
        log_path = Path(env_log_path).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        log_path = log_dir / f"run_financiamiento_{anio}_P{periodo}_{inicio.strftime('%Y%m%d_%H%M%S')}.log"
        log_path = unique_path(log_path)
    ctx = RunContext(
        anio=int(anio),
        periodo=int(periodo),
        inicio=inicio,
        run_dir=run_dir,
        input_dir=input_dir,
        output_dir=output_dir,
        log_dir=log_dir,
        audit_dir=audit_dir,
        log_path=log_path,
    )
    ctx._known_outputs_at_start = _scan_generated_files(ctx)
    ACTIVE_CONTEXT = ctx

    if not external_tee:
        ctx._log_handle = log_path.open("a", encoding="utf-8")
        if _PREINIT_ACTIVE:
            ctx._stdout_original = _PREINIT_STDOUT_ORIGINAL
            ctx._stderr_original = _PREINIT_STDERR_ORIGINAL
            ctx._log_handle.write("".join(_PREINIT_BUFFER))
            ctx._log_handle.flush()
        else:
            ctx._stdout_original = sys.stdout
            ctx._stderr_original = sys.stderr
        sys.stdout = TeeStream(ctx._stdout_original, ctx._log_handle)
        sys.stderr = TeeStream(ctx._stderr_original, ctx._log_handle)
    else:
        log_path.touch(exist_ok=True)

    print(f"[RUN] Inicio: {inicio.isoformat()}", flush=True)
    print(f"[RUN] Zona horaria: {TZ_NAME}", flush=True)
    print(f"[RUN] Año/periodo: {anio} P{periodo}", flush=True)
    print(f"[RUN] Carpeta de ejecución: {run_dir}", flush=True)
    return ctx


def get_context() -> RunContext:
    if ACTIVE_CONTEXT is None:
        raise RuntimeError("RunContext no inicializado.")
    return ACTIVE_CONTEXT


def output_path(filename: str | Path, *, audit: bool | None = None, analysis: bool = False) -> Path:
    ctx = get_context()
    name = Path(filename).name
    if analysis:
        if (ctx.anio, ctx.periodo) != (2027, 1):
            raise ValueError("05_ANALISIS esta habilitado exclusivamente para 2027 P1.")
        target_dir = ctx.analysis_dir
    else:
        target_dir = ctx.audit_dir if (is_audit_filename(name) if audit is None else audit) else ctx.output_dir
        if ((ctx.anio, ctx.periodo) == (2027, 1) and target_dir == ctx.output_dir
                and Path(name).suffix.lower() in {'.xlsx', '.xls'}
                and not name.startswith(DELIVERY_EXCEL_PREFIXES_2027)):
            target_dir = ctx.analysis_dir
    return unique_path(target_dir / name).resolve()


def analysis_path(filename: str | Path) -> Path:
    return output_path(filename, analysis=True)


def record_conditional_output(path: str | Path, *, rows: int, columns: int, purpose: str) -> dict[str, Any]:
    ctx = get_context()
    if (ctx.anio, ctx.periodo) != (2027, 1):
        raise ValueError('El registro de salidas condicionales es exclusivo de 2027 P1.')
    target = Path(path).resolve()
    if target.parent != ctx.output_dir.resolve() or rows < 0 or columns < 0:
        raise ValueError('Metadatos invalidos de salida condicional.')
    if bool(rows) != target.is_file():
        raise ValueError(f'{target.name}: la presencia del archivo no coincide con sus {rows} casos.')
    decision = {'nombre':target.name, 'ruta':str(target),
        'regla':'GENERAR_SOLO_CON_CASOS', 'estado':'GENERADO' if rows else 'OMITIDO_SIN_CASOS',
        'filas':int(rows), 'columnas':int(columns), 'proposito':purpose,
        'motivo':'CASOS_PRESENTES' if rows else 'CERO_CASOS_EN_EL_CORTE'}
    ctx.decisiones_salidas_condicionales[target.name] = decision
    return decision


def register_error(exc_type: Any, exc: BaseException, tb: Any, *, code: int = 1) -> None:
    if ACTIVE_CONTEXT is None:
        return
    ACTIVE_CONTEXT.estado = "ERROR"
    ACTIVE_CONTEXT.codigo_salida = int(code or 1)
    ACTIVE_CONTEXT.error = "".join(traceback.format_exception(exc_type, exc, tb))


def install_exception_hook() -> None:
    original_hook = sys.excepthook

    def _hook(exc_type: Any, exc: BaseException, tb: Any) -> None:
        code = int(getattr(exc, "code", 1) or 0) if exc_type is SystemExit else 1
        if code != 0:
            register_error(exc_type, exc, tb, code=code)
        original_hook(exc_type, exc, tb)

    sys.excepthook = _hook


def archive_input(path: str | Path, tipo: str) -> dict[str, Any]:
    ctx = get_context()
    original = Path(path).expanduser().resolve()
    if not original.exists():
        raise FileNotFoundError(f"[ENTRADA FALTANTE] No existe {tipo}: {original}")
    archived = unique_path(ctx.input_dir / original.name)
    shutil.copy2(original, archived)
    original_size = original.stat().st_size
    copied_size = archived.stat().st_size
    if original_size != copied_size:
        raise RuntimeError(
            f"[ENTRADA] Copia con tamaño distinto para {tipo}: {original_size} != {copied_size}"
        )
    sha_original = sha256_file(original)
    sha_copy = sha256_file(archived)
    if sha_original != sha_copy:
        raise RuntimeError(f"[ENTRADA] SHA-256 no coincide para {tipo}: {original}")
    item = {
        "tipo": tipo,
        "ruta_original": str(original),
        "ruta_archivada": str(archived.resolve()),
        "nombre": original.name,
        "tamano_bytes": int(original_size),
        "sha256_original": sha_original,
        "sha256_copia": sha_copy,
    }
    ctx.entradas.append(item)
    print(f"[ENTRADA] {tipo}: {original} -> {archived}", flush=True)
    return item


def _scan_generated_files(ctx: RunContext) -> set[Path]:
    files: set[Path] = set()
    bases = [ctx.output_dir, ctx.audit_dir]
    if (getattr(ctx, "anio", None), getattr(ctx, "periodo", None)) == (2027, 1):
        bases.append(ctx.analysis_dir)
    for base in bases:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in OUTPUT_EXTENSIONS:
                files.add(path.resolve())
    return files


def _output_type(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    return suffix or "sin_extension"


def _csv_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if header is None:
                return 0, 0
            rows = sum(1 for _ in reader)
            return rows, len(header)
    except Exception:
        return None, None


def _output_dimensions(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() == ".csv":
        return _csv_dimensions(path)
    return None, None


def _output_purpose(name: str) -> str:
    if name.startswith("+ Nuevos inscritos acumulados no incorporados a LimeSurvey_"):
        return (
            "Estudiantes vigentes de la población objetivo que siguen pendientes "
            "fuera de la ventana diaria cerrada; se entrega separado del diario."
        )
    if name.startswith("+ Nuevos inscritos hoy_"):
        return (
            "Estudiantes vigentes no incorporados en LimeSurvey cuya "
            "FECHAMATRICULA pertenece a la ventana hábil diaria."
        )
    if name.startswith("AUDITORIA_REZAGADOS_LIMESURVEY_"):
        return (
            "Estudiantes vigentes del periodo que siguen no incorporados "
            "a LimeSurvey y ya quedaron fuera de la ventana hábil diaria."
        )
    if name.startswith("AUDITORIA_NO_OBJETIVO_LIMESURVEY_ANOINGRESO_"):
        return (
            "Vigentes del periodo sin token excluidos de la encuesta porque "
            "su ANOINGRESO no coincide con el anio analizado."
        )
    return ""


def collect_outputs(ctx: RunContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for path in sorted(_scan_generated_files(ctx), key=lambda p: str(p)):
        if path.name in {"manifest_ejecucion.json", "RESUMEN_EJECUCION.txt"}:
            continue
        if path in seen:
            continue
        seen.add(path)
        filas, columnas = _output_dimensions(path)
        decision = getattr(ctx,'decisiones_salidas_condicionales',{}).get(path.name)
        if decision:
            filas, columnas = decision['filas'], decision['columnas']
        rows.append(
            {
                "nombre": path.name,
                "ruta": str(path),
                "tipo": _output_type(path),
                "tamano_bytes": int(path.stat().st_size),
                "sha256": sha256_file(path),
                "filas": filas,
                "columnas": columnas,
                "proposito": decision['proposito'] if decision else _output_purpose(path.name),
                **({"carpeta":path.relative_to(ctx.run_dir.resolve()).parts[0]} if (ctx.anio,ctx.periodo)==(2027,1) else {}),
            }
        )
    return rows


def collect_totals(namespace: dict[str, Any]) -> dict[str, Any]:
    candidates = {
        "vigentes": "df_vigentes",
        "respondieron": "total_si",
        "incompletos": "total_incompleto",
        "no_respondieron": "total_no",
        "nuevos_inscritos": "n_nuevos",
        "nuevos_inscritos_acumulados": "n_nuevos_acumulados",
        "nuevos_inscritos_ventana": "n_nuevos_ventana_habil",
        "nuevos_inscritos_rezagados_limesurvey": "n_nuevos_rezagados_limesurvey",
        "nuevos_inscritos_otros_fuera_ventana_limesurvey": "n_nuevos_otros_fuera_ventana_limesurvey",
        "no_objetivo_anoingreso_limesurvey": "n_nuevos_no_objetivo_anoingreso_limesurvey",
        "max_dias_rezago_limesurvey": "max_dias_rezago_limesurvey",
        "eliminados_acumulados": "n_elim_reporte_total",
        "eliminados_de_ventana": "n_elim_reporte_ventana",
        "filas_santiago": "df_bd_stgo",
        "filas_concepcion": "df_bd_conce",
        "filas_patagonia": "df_bd_ptg",
    }
    totals: dict[str, Any] = {}
    for key, source in candidates.items():
        if source not in namespace:
            continue
        value = namespace[source]
        try:
            totals[key] = int(len(value)) if hasattr(value, "__len__") and not isinstance(value, (str, bytes)) else int(value)
        except Exception:
            try:
                totals[key] = float(value)
            except Exception:
                totals[key] = str(value)
    return totals


def historical_max_respondents(
    anio: int,
    periodo: int,
    *,
    current_run_dir: str | Path | None = None,
) -> int:
    """Retorna el mayor total historico de respondientes para el mismo anio/periodo."""
    base = Path(os.environ.get("CARACTERIZACION_ARCHIVO_BASE", str(DEFAULT_ARCHIVO_BASE))).expanduser()
    if not base.exists():
        return 0
    current = Path(current_run_dir).resolve() if current_run_dir else None
    max_value = 0
    pattern = f"*/{int(anio)}_P{int(periodo)}_*/04_AUDITORIA/manifest_ejecucion.json"
    for manifest_path in base.glob(pattern):
        try:
            resolved = manifest_path.resolve()
            if current is not None and current in resolved.parents:
                continue
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            if int(payload.get("anio_analisis", -1)) != int(anio):
                continue
            if int(payload.get("periodo", -1)) != int(periodo):
                continue
            value = payload.get("totales", {}).get("respondieron", 0)
            max_value = max(max_value, int(value or 0))
        except Exception:
            continue
    return max_value


def manifest_dict(ctx: RunContext, namespace: dict[str, Any] | None = None) -> dict[str, Any]:
    termino = now_scl()
    ns = namespace or {}
    calendario_feriados = Path(
        os.environ.get(
            "CARACTERIZACION_FERIADOS_CSV",
            str(Path(__file__).resolve().parent / "docs" / "gobernanza" / "FERIADOS_CHILE_2026_2040.csv"),
        )
    ).expanduser()
    calendario_feriados_meta = {
        "ruta": str(calendario_feriados),
        "sha256": sha256_file(calendario_feriados) if calendario_feriados.exists() else None,
        "rango_base": "2026-2040",
        "modo": "archivo_local_versionado_sin_consulta_externa",
    }
    auditoria_universo = ns.get("AUDITORIA_UNIVERSO")
    try:
        alertas_universo = list(getattr(auditoria_universo, "alertas", []) or [])
    except Exception:
        alertas_universo = []
    return {
        "fecha_inicio": ctx.inicio.isoformat(),
        "fecha_termino": termino.isoformat(),
        "zona_horaria": TZ_NAME,
        "anio_analisis": ctx.anio,
        "periodo": ctx.periodo,
        "politica_pendientes_limesurvey": {
            "id": POLITICA_PENDIENTES_LIMESURVEY_ID,
            "archivo_carga_autorizado": "CSV_DIARIO_Y_CSV_ACUMULADO_SEPARADOS",
            "anoingreso_debe_igualar_anio_analisis": True,
            "csv_diario_campo_temporal": "FECHAMATRICULA",
            "csv_acumulado_campo_temporal": "FECHAMATRICULA_FUERA_DE_VENTANA_DIARIA",
        },
        "calendario_feriados_chile": calendario_feriados_meta,
        "directorio_ejecucion": str(ctx.run_dir.resolve()),
        **({"directorio_analisis":str(ctx.analysis_dir.resolve()),
            "politica_separacion":"COMUNICACION_ANALISIS_AUDITORIA_2027_P1-v1",
            "politica_salidas_condicionales":"SALIDAS_CON_CASOS_2027_P1-v1",
            "decisiones_salidas_condicionales":list(ctx.decisiones_salidas_condicionales.values())}
           if (ctx.anio,ctx.periodo)==(2027,1) else {}),
        "estado": ctx.estado,
        "codigo_salida": int(ctx.codigo_salida),
        "entradas": ctx.entradas,
        "salidas": collect_outputs(ctx),
        "totales": collect_totals(ns),
        "sies_historico": {
            "arquitectura": "CARACTERIZACION -> usa -> SIES VERSIONADA -> NO RECONSTRUIDA -> NO DINAMICA",
            "version_utilizada": ns.get("SIES_VERSION_UTILIZADA"),
            "reconstruida_en_pipeline": False,
            "dinamica": False,
            "nivel_analisis": "AGREGADO_PROGRAMA_ANIO",
        },
        "auditoria_universo_alertas": alertas_universo,
        "directorio_escritorio": str(ctx.desktop_dir.resolve()) if ctx.desktop_dir else None,
        "copia_escritorio_estado": ctx.desktop_copy_status,
        "copia_escritorio_advertencia": ctx.desktop_copy_warning,
        "error": ctx.error,
    }


def write_summary(ctx: RunContext, manifest: dict[str, Any]) -> Path:
    path = ctx.audit_dir / "RESUMEN_EJECUCION.txt"
    lines = [
        "RESUMEN DE EJECUCION",
        f"Ejecucion: {manifest['fecha_inicio']} -> {manifest['fecha_termino']}",
        f"Anio y periodo: {ctx.anio} P{ctx.periodo}",
        f"Politica pendientes LimeSurvey: {POLITICA_PENDIENTES_LIMESURVEY_ID}",
        f"Carpeta creada: {ctx.run_dir.resolve()}",
        "",
        "Archivos de entrada:",
    ]
    if manifest["entradas"]:
        lines.extend(f"- {e['tipo']}: {e['nombre']} ({e['ruta_original']})" for e in manifest["entradas"])
    else:
        lines.append("- Sin entradas archivadas.")
    lines.extend(["", "Archivos de salida:"])
    if manifest["salidas"]:
        for salida in manifest["salidas"]:
            detalle = f"- {salida['nombre']} ({salida['tamano_bytes']} bytes)"
            if salida.get("filas") is not None and salida.get("columnas") is not None:
                detalle += f" | filas={salida['filas']} columnas={salida['columnas']}"
            if salida.get("proposito"):
                detalle += f" | proposito={salida['proposito']}"
            lines.append(detalle)
    else:
        lines.append("- Sin salidas generadas.")
    if manifest.get('decisiones_salidas_condicionales'):
        lines.extend(['', 'Decisiones de salidas condicionales:'])
        for decision in manifest['decisiones_salidas_condicionales']:
            lines.append(f"- {decision['nombre']}: {decision['estado']} | casos={decision['filas']} | motivo={decision['motivo']}")
    lines.extend(["", "Principales totales:"])
    if manifest["totales"]:
        lines.extend(f"- {k}: {v}" for k, v in manifest["totales"].items())
    else:
        lines.append("- No disponibles.")
    sies = manifest.get("sies_historico") or {}
    if sies:
        lines.extend([
            "",
            "Histórico SIES:",
            f"- Version utilizada: {sies.get('version_utilizada') or 'NO_DISPONIBLE'}",
            f"- Arquitectura: {sies.get('arquitectura')}",
        ])
    if manifest.get("auditoria_universo_alertas"):
        lines.extend(["", "Alertas auditoria universo:"])
        for alerta in manifest["auditoria_universo_alertas"]:
            try:
                lines.append(f"- {alerta.get('nivel', 'WARN')}: {alerta.get('mensaje', alerta)}")
            except Exception:
                lines.append(f"- {alerta}")
    lines.extend(["", "Copia de Escritorio:"])
    if manifest.get("directorio_escritorio"):
        lines.append(f"- Directorio: {manifest['directorio_escritorio']}")
    else:
        lines.append("- Directorio: no aplica")
    lines.append(f"- Estado: {manifest.get('copia_escritorio_estado', 'NO_APLICA')}")
    if manifest.get("copia_escritorio_advertencia"):
        lines.append(f"- Advertencia: {manifest['copia_escritorio_advertencia']}")
    lines.extend(["", f"Resultado: {manifest['estado']}", f"Codigo de salida: {manifest['codigo_salida']}"])
    if manifest.get("error"):
        lines.extend(["", "Error:", str(manifest["error"])])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_manifest_and_summary(ctx: RunContext, namespace: dict[str, Any] | None = None) -> tuple[Path, Path]:
    manifest = manifest_dict(ctx, namespace)
    manifest_path = ctx.audit_dir / "manifest_ejecucion.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path = write_summary(ctx, manifest)
    return manifest_path, summary_path


def _restore_and_close_log(ctx: RunContext) -> None:
    if ctx._log_handle is not None:
        sys.stdout = ctx._stdout_original
        sys.stderr = ctx._stderr_original
        ctx._log_handle.close()
        ctx._log_handle = None


def _copy_successful_run_to_desktop(ctx: RunContext) -> None:
    target = ctx.desktop_dir or desktop_copy_target(ctx)
    ctx.desktop_dir = target
    ctx.desktop_copy_status = "OK"
    ctx.desktop_copy_warning = None
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ctx.run_dir, target, copy_function=shutil.copy2)
    stats = validate_directory_copy(ctx.run_dir, target)
    print(
        "[RUN] Copia Escritorio OK: "
        f"{target} ({stats['archivos_verificados']} archivos, {stats['bytes_verificados']} bytes verificados)",
        flush=True,
    )


def finalize(namespace: dict[str, Any] | None = None, *, code: int | None = None, error: str | None = None) -> None:
    ctx = ACTIVE_CONTEXT
    if ctx is None or ctx._finalized:
        return
    ctx._finalized = True
    if code is not None:
        ctx.codigo_salida = int(code)
        if int(code) != 0:
            ctx.estado = "ERROR"
    if error:
        ctx.estado = "ERROR"
        ctx.error = error
        if ctx.codigo_salida == 0:
            ctx.codigo_salida = 1
    if ctx.estado != "OK" or ctx.codigo_salida != 0:
        ctx.desktop_copy_status = "NO_APLICA"
    if namespace:
        auditoria_universo = namespace.get("AUDITORIA_UNIVERSO")
        exportar = getattr(auditoria_universo, "exportar", None)
        if callable(exportar):
            try:
                exportar()
            except Exception as exc:
                print(f"[RUN][WARN] No se pudo exportar AUDITORIA_UNIVERSO: {type(exc).__name__}: {exc}", flush=True)
    print(f"[RUN] Termino: {now_scl().isoformat()}", flush=True)
    print(f"[RUN] Estado final: {ctx.estado}", flush=True)
    print(f"[RUN] Codigo de salida: {ctx.codigo_salida}", flush=True)
    if ctx.estado == "OK" and ctx.codigo_salida == 0:
        ctx.desktop_dir = desktop_copy_target(ctx)
        ctx.desktop_copy_status = "OK"
        ctx.desktop_copy_warning = None
    manifest_path, summary_path = _write_manifest_and_summary(ctx, namespace)
    print(f"[RUN] Manifest: {manifest_path}", flush=True)
    print(f"[RUN] Resumen: {summary_path}", flush=True)
    _restore_and_close_log(ctx)

    if ctx.estado == "OK" and ctx.codigo_salida == 0:
        try:
            _copy_successful_run_to_desktop(ctx)
        except Exception as exc:
            ctx.desktop_copy_status = "ERROR"
            ctx.desktop_copy_warning = f"{type(exc).__name__}: {exc}"
            print(f"[RUN][WARN] No se pudo completar la copia al Escritorio: {ctx.desktop_copy_warning}", flush=True)
            _write_manifest_and_summary(ctx, namespace)


def register_atexit(namespace: dict[str, Any]) -> None:
    atexit.register(lambda: finalize(namespace))
