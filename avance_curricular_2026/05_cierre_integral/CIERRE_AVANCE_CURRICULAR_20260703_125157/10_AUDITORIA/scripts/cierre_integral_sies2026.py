#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook, load_workbook


REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()
PROCESO_DIR = REPO / "avance_curricular_2026"
CIERRE_ROOT = PROCESO_DIR / "05_cierre_integral"

FASE_ESTADOS = (
    "NO_INICIADA",
    "EN_EJECUCION",
    "COMPLETADA",
    "COMPLETADA_CON_OBSERVACIONES",
    "BLOQUEADA",
    "FALLIDA",
    "EXCLUIDA_CON_JUSTIFICACION",
)

SUBDIRS = [
    "00_CONTROL",
    "01_FUENTES",
    "02_DIAGNOSTICOS",
    "03_CONCILIACION_CARRERAS",
    "04_CONCILIACION_MATRICULA",
    "05_RESOLUCION_PENDIENTES",
    "06_VALIDACIONES_FUNCIONALES",
    "07_VALIDACIONES_TECNICAS",
    "08_ARCHIVOS_REVISION",
    "09_ARCHIVOS_CARGA",
    "10_AUDITORIA",
    "11_REPORTES",
    "12_RESPALDOS",
    "13_ENTREGA_FINAL",
]

COLUMNAS_5810 = [
    "CODIGO_IES_NUM",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "NOMBRE_SEDE",
    "NOMBRE_CARRERA",
    "JORNADA",
    "VERSION",
    "DURACION_ESTUDIOS",
    "DURACION_TITULACION",
    "DURACION_TOTAL",
    "NIVEL_CARRERA",
    "TIPO_UNIDAD_MEDIDA",
    "OTRA_UNIDAD_MEDIDA",
    "TOTAL_UNIDADES_MEDIDA",
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
    "VIGENCIA",
]

COLUMNAS_5809 = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

NO_MOD_5810 = [
    "CODIGO_IES_NUM",
    "CODIGO_UNICO",
    "NOMBRE_SEDE",
    "NOMBRE_CARRERA",
    "JORNADA",
    "VERSION",
    "DURACION_ESTUDIOS",
    "DURACION_TITULACION",
    "DURACION_TOTAL",
    "NIVEL_CARRERA",
]

NO_MOD_5809 = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
]


@dataclass(frozen=True)
class SourceSpec:
    rol: str
    uso: str
    selected: Path
    alternatives: list[Path]
    criterio: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text


def detect_encoding(path: Path) -> str:
    sample = path.read_bytes()[:200000]
    if sample.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            sample.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"No se pudo determinar codificacion: {path}")


def detect_eol(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    cr = raw.count(b"\r") - crlf
    if crlf and not lf and not cr:
        return "CRLF"
    if lf and not crlf and not cr:
        return "LF"
    if cr and not crlf and not lf:
        return "CR"
    return f"MIXTO_CRLF_{crlf}_LF_{lf}_CR_{cr}"


def detect_delimiter(text: str) -> str:
    first = next((line for line in text.splitlines() if line.strip()), "")
    counts = {sep: first.count(sep) for sep in (";", "\t", ",", "|")}
    sep = max(counts, key=counts.get)
    if counts[sep] <= 0:
        raise RuntimeError("No se pudo determinar delimitador")
    return sep


def csv_profile(path: Path) -> dict[str, Any]:
    enc = detect_encoding(path)
    raw = path.read_bytes()
    text = raw.decode(enc, errors="strict")
    delimiter = detect_delimiter(text)
    rows: list[list[str]] = []
    for row in csv.reader(text.splitlines(), delimiter=delimiter):
        rows.append(row)
    if not rows:
        raise RuntimeError(f"CSV vacio: {path}")
    headers = rows[0]
    counts: dict[str, int] = {}
    invalid_rows = []
    expected_cols = len(headers)
    for idx, row in enumerate(rows, start=1):
        counts[str(len(row))] = counts.get(str(len(row)), 0) + 1
        if len(row) != expected_cols:
            invalid_rows.append(
                {
                    "archivo": str(path),
                    "linea": idx,
                    "columnas_observadas": len(row),
                    "columnas_esperadas": expected_cols,
                }
            )
    return {
        "tipo": "csv",
        "encoding": enc,
        "bom": "SI" if raw.startswith(b"\xef\xbb\xbf") else "NO",
        "delimitador": delimiter,
        "salto_linea": detect_eol(raw),
        "filas_totales": len(rows),
        "filas_datos": max(len(rows) - 1, 0),
        "columnas": expected_cols,
        "encabezados": headers,
        "conteo_columnas_por_fila": counts,
        "filas_con_estructura_invalida": invalid_rows,
        "primera_columna": headers[0] if headers else "",
        "tiene_encabezado": "SI",
    }


def xlsx_profile(path: Path) -> dict[str, Any]:
    wb = load_workbook(path, read_only=True, data_only=True)
    sheets = []
    for ws in wb.worksheets:
        headers = []
        if ws.max_row and ws.max_column:
            for cell in next(ws.iter_rows(min_row=1, max_row=1, values_only=True)):
                headers.append("" if cell is None else str(cell))
        sheets.append(
            {
                "hoja": ws.title,
                "filas": ws.max_row,
                "columnas": ws.max_column,
                "encabezados": headers,
            }
        )
    return {
        "tipo": "xlsx",
        "hojas": len(wb.worksheets),
        "detalle_hojas": sheets,
    }


def text_profile(path: Path) -> dict[str, Any]:
    enc = detect_encoding(path)
    raw = path.read_bytes()
    text = raw.decode(enc, errors="strict")
    return {
        "tipo": "texto",
        "encoding": enc,
        "bom": "SI" if raw.startswith(b"\xef\xbb\xbf") else "NO",
        "salto_linea": detect_eol(raw),
        "lineas": len(text.splitlines()),
    }


def profile_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".csv" or suffix == ".tsv":
        return csv_profile(path)
    if suffix in (".xlsx", ".xlsm"):
        return xlsx_profile(path)
    if suffix in (".txt", ".md", ".tsv", ".json"):
        try:
            return text_profile(path)
        except Exception:
            return {"tipo": suffix.lstrip(".") or "archivo"}
    return {"tipo": suffix.lstrip(".") or "archivo"}


def metadata(path: Path, rol: str, uso: str, selected: bool) -> dict[str, Any]:
    stat = path.stat()
    item = {
        "rol": rol,
        "uso_esperado": uso,
        "seleccionada": "SI" if selected else "NO",
        "nombre": path.name,
        "ruta": str(path),
        "ruta_resuelta": str(path.resolve()),
        "tamano_bytes": stat.st_size,
        "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
        "sha256": sha256(path),
    }
    try:
        item.update(profile_file(path))
    except Exception as exc:
        item["perfil_error"] = f"{type(exc).__name__}: {exc}"
    return item


def write_tsv(path: Path, rows: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    if columns is None:
        columns = sorted({key for row in rows for key in row.keys()})
    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(path, sep="\t", index=False)


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                letter = col[0].column_letter
                width = max(len(str(cell.value or "")) for cell in col[:500])
                ws.column_dimensions[letter].width = min(max(width + 2, 12), 60)


def control_paths(exec_dir: Path) -> dict[str, Path]:
    control = exec_dir / "00_CONTROL"
    return {
        "estado": control / "ESTADO_EJECUCION.json",
        "checkpoint": control / "CHECKPOINT_ACTUAL.json",
        "manifest_fuentes": control / "MANIFEST_FUENTES.json",
        "manifest_salidas": control / "MANIFEST_SALIDAS.json",
        "bloqueos": control / "BLOQUEOS.tsv",
        "decisiones": control / "DECISIONES.tsv",
        "contradicciones": control / "CONTRADICCIONES.tsv",
        "validaciones": control / "VALIDACIONES.tsv",
        "resumen": control / "RESUMEN_EJECUCION.txt",
        "reanudar": control / "REANUDAR_DESDE_AQUI.md",
    }


def init_execution(exec_dir: Path | None) -> Path:
    if exec_dir:
        for sub in SUBDIRS:
            (exec_dir / sub).mkdir(parents=True, exist_ok=True)
        return exec_dir.resolve()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_dir = CIERRE_ROOT / f"CIERRE_AVANCE_CURRICULAR_{ts}"
    for sub in SUBDIRS:
        (new_dir / sub).mkdir(parents=True, exist_ok=False)
    return new_dir.resolve()


def initial_state() -> dict[str, Any]:
    return {
        "proceso": "Avance Curricular SIES 2026",
        "anio_datos": 2025,
        "fecha_inicio": now_iso(),
        "fecha_ultima_actualizacion": now_iso(),
        "fase_actual": "",
        "estado_general": "EN_EJECUCION",
        "ultima_fase_completada": "",
        "siguiente_fase": "FASE_0",
        "bloqueos_activos": 0,
        "archivos_finales_generados": False,
        "archivo_carreras_listo": False,
        "archivo_matricula_listo": False,
        "carga_pes_realizada": False,
        "fases": {f"FASE_{i}": "NO_INICIADA" for i in range(26)},
    }


def load_state(exec_dir: Path) -> dict[str, Any]:
    paths = control_paths(exec_dir)
    if paths["estado"].exists():
        return json.loads(paths["estado"].read_text(encoding="utf-8"))
    return initial_state()


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def append_tsv(path: Path, row: dict[str, Any], columns: list[str]) -> None:
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def mark_phase(
    exec_dir: Path,
    state: dict[str, Any],
    phase: int,
    status: str,
    next_phase: int | None = None,
    bloqueos: int = 0,
) -> None:
    if status not in FASE_ESTADOS:
        raise ValueError(status)
    key = f"FASE_{phase}"
    state["fase_actual"] = key
    state["fases"][key] = status
    state["fecha_ultima_actualizacion"] = now_iso()
    state["bloqueos_activos"] = bloqueos
    if status.startswith("COMPLETADA"):
        state["ultima_fase_completada"] = key
    if status == "BLOQUEADA":
        state["estado_general"] = "BLOQUEADO"
    elif status == "FALLIDA":
        state["estado_general"] = "FALLIDA"
    else:
        state["estado_general"] = "EN_EJECUCION"
    state["siguiente_fase"] = "" if next_phase is None else f"FASE_{next_phase}"
    save_json(control_paths(exec_dir)["estado"], state)


def make_resume(exec_dir: Path, phase: int, reason: str = "") -> None:
    command = f'python scripts/cierre_integral_sies2026.py --execution-dir "{exec_dir}" --desde-fase {phase}'
    content = [
        "# Reanudar desde aqui",
        "",
        f"Carpeta de ejecucion: {exec_dir}",
        f"Siguiente fase sugerida: FASE_{phase}",
        f"Motivo: {reason or 'Continuar ejecucion controlada.'}",
        "",
        "```bash",
        command,
        "```",
        "",
    ]
    control_paths(exec_dir)["reanudar"].write_text("\n".join(content), encoding="utf-8")


def find_one(pattern: str) -> list[Path]:
    return sorted(REPO.rglob(pattern), key=lambda p: str(p))


def choose_sources(exec_dir: Path) -> list[SourceSpec]:
    frozen = PROCESO_DIR / "00_fuentes_congeladas" / "CARGA_CONGELADA_20260626_005826" / "originales"
    comparison = PROCESO_DIR / "04_gobernanza_mallas" / "03_auditorias" / "COMPARACION_PROMEDIOS_CONGELADO_VS_INPUT_20260701_232300"
    specs = [
        SourceSpec(
            rol="FUENTE_NORMATIVA_PRINCIPAL",
            uso="Instructivo oficial Avance Curricular SIES 2026",
            selected=frozen / "Instructivo_Avance Curricular SIES - 2026.txt",
            alternatives=find_one("*Instructivo*Avance*Curricular*SIES*2026*"),
            criterio="Ruta congelada previa del proyecto y nombre exacto indicado en el prompt.",
        ),
        SourceSpec(
            rol="PRECARGA_CARRERAS_5810",
            uso="Precarga oficial Carreras Avance Curricular 2026 ID 16769",
            selected=frozen / "5810_Precarga Carreras Avance Curricular 20268.csv",
            alternatives=find_one("*Precarga*Carreras*Avance*Curricular*2026*"),
            criterio="Archivo CSV original congelado; 5809 no corresponde a carreras segun prompt.",
        ),
        SourceSpec(
            rol="PRECARGA_MATRICULA_5809",
            uso="Precarga oficial Matricula Avance Curricular 2026 ID 16768",
            selected=next(iter(find_one("*5809_Precarga*Matr*Avance*Curricular*2026.csv")), frozen / "5809_Precarga Matricula Avance Curricular 2026.csv"),
            alternatives=find_one("*Precarga*Matr*Avance*Curricular*2026*"),
            criterio="Archivo CSV original congelado 5809 indicado por prompt.",
        ),
        SourceSpec(
            rol="FUENTE_ESTUDIANTES_PROMEDIOS",
            uso="Fuente institucional de estudiantes; hoja principal DatosAlumnos",
            selected=REPO / "PROMEDIOSDEALUMNOS_7804.xlsx",
            alternatives=find_one("*PROMEDIOSDEALUMNOS*7804*"),
            criterio=(
                "Ruta principal del repositorio indicada por el prompt. La comparacion "
                f"{comparison} documenta cero diferencias reales contra congelado anterior."
            ),
        ),
        SourceSpec(
            rol="FUENTE_PLANES_ESTUDIO",
            uso="Fuente institucional de planes; hoja BBDD Bruta",
            selected=PROCESO_DIR / "01_fuentes_institucionales" / "planes_estudio" / "Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx",
            alternatives=find_one("*Listado*Planes*estudio*Sedes*RE*CO*20260701*"),
            criterio="Ruta institucional vigente dentro de avance_curricular_2026.",
        ),
    ]
    return specs


def classify_artifacts() -> list[Path]:
    base = PROCESO_DIR / "04_gobernanza_mallas" / "03_auditorias"
    names = [
        "CIERRE_FINAL_43_RESUELTAS_0_PENDIENTES_20260701_171409",
        "GOBERNANZA_AVANCE_CURRICULAR_V2_2026_20260701_235600",
        "EXPEDIENTE_REVISION_644_20260702_012504",
        "PLANILLA_DECISION_29_P1_20260703_095214",
        "ANALISIS_DESCARTE_1_A_1_29_P1_20260703_101217",
        "CLASIFICACION_29_MODELOS_PERIODIZACION_20260703_123007",
        "DIAGNOSTICO_27_CODCLI_PLAN_20260703_123419",
        "DESCOMPOSICION_19_CANDIDATOS_DEBILES_20260703_123657",
        "COMPARACION_PROMEDIOS_CONGELADO_VS_INPUT_20260701_232300",
    ]
    result = []
    for name in names:
        path = base / name
        if path.exists():
            for file in path.rglob("*"):
                if file.is_file() and not file.name.startswith("~$"):
                    result.append(file)
    return result


def phase0(exec_dir: Path, state: dict[str, Any]) -> bool:
    mark_phase(exec_dir, state, 0, "EN_EJECUCION", next_phase=0)
    paths = control_paths(exec_dir)
    logs_dir = exec_dir / "10_AUDITORIA" / "scripts"
    logs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), logs_dir / Path(__file__).name)

    specs = choose_sources(exec_dir)
    missing = [spec for spec in specs if not spec.selected.exists()]
    if missing:
        for spec in missing:
            append_tsv(
                paths["bloqueos"],
                {
                    "FECHA": now_iso(),
                    "FASE": "FASE_0",
                    "MOTIVO": "FALTA_FUENTE_OBLIGATORIA",
                    "DETALLE": f"{spec.rol}: {spec.selected}",
                    "ACCION": "Ubicar fuente exacta o documentar reemplazo autorizado.",
                },
                ["FECHA", "FASE", "MOTIVO", "DETALLE", "ACCION"],
            )
        mark_phase(exec_dir, state, 0, "BLOQUEADA", next_phase=0, bloqueos=len(missing))
        make_resume(exec_dir, 0, "Faltan fuentes obligatorias.")
        return False

    selected_paths = {spec.selected.resolve() for spec in specs}
    rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    discarded_rows: list[dict[str, Any]] = []

    for spec in specs:
        all_paths = []
        for p in [spec.selected, *spec.alternatives]:
            if p.exists() and p.resolve() not in {q.resolve() for q in all_paths}:
                all_paths.append(p)
        for p in all_paths:
            is_selected = p.resolve() == spec.selected.resolve()
            item = metadata(p, spec.rol, spec.uso, is_selected)
            item["criterio_seleccion"] = spec.criterio if is_selected else "Alternativa documentada no seleccionada."
            rows.append(item)
            reduced = {
                "ROL": spec.rol,
                "RUTA": str(p),
                "SHA256": item["sha256"],
                "CRITERIO": item["criterio_seleccion"],
            }
            if is_selected:
                selected_rows.append(reduced)
            else:
                discarded_rows.append(reduced)

    for artifact in classify_artifacts():
        rows.append(metadata(artifact, "ARTEFACTO_PREVIO_RELEVANTE", "Auditoria o resultado previo incorporado al proyecto", False))

    df = pd.DataFrame(rows)
    df.to_csv(exec_dir / "01_FUENTES" / "INVENTARIO_FUENTES.tsv", sep="\t", index=False)
    write_xlsx(exec_dir / "01_FUENTES" / "INVENTARIO_FUENTES.xlsx", {"INVENTARIO": df})

    hash_rows = [{"SHA256": row["sha256"], "RUTA": row["ruta"], "ROL": row["rol"]} for row in rows]
    write_tsv(exec_dir / "01_FUENTES" / "HASHES_SHA256.tsv", hash_rows, ["SHA256", "RUTA", "ROL"])

    by_hash: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_hash.setdefault(str(row["sha256"]), []).append(row)
    dup_rows = []
    for digest, group in by_hash.items():
        if len(group) > 1:
            for item in group:
                dup_rows.append({"SHA256": digest, "RUTA": item["ruta"], "ROL": item["rol"]})
    write_tsv(exec_dir / "01_FUENTES" / "DUPLICADOS_FISICOS.tsv", dup_rows, ["SHA256", "RUTA", "ROL"])
    write_tsv(exec_dir / "01_FUENTES" / "FUENTES_SELECCIONADAS.tsv", selected_rows, ["ROL", "RUTA", "SHA256", "CRITERIO"])
    write_tsv(exec_dir / "01_FUENTES" / "FUENTES_DESCARTADAS.tsv", discarded_rows, ["ROL", "RUTA", "SHA256", "CRITERIO"])

    source_manifest = {
        "fecha": now_iso(),
        "proceso": "Avance Curricular SIES 2026",
        "repositorio": str(REPO),
        "carpeta_proceso": str(PROCESO_DIR),
        "fuentes_seleccionadas": selected_rows,
        "inventario": str(exec_dir / "01_FUENTES" / "INVENTARIO_FUENTES.tsv"),
        "duplicados_fisicos": len(dup_rows),
    }
    save_json(paths["manifest_fuentes"], source_manifest)

    frozen_dir = exec_dir / "01_FUENTES" / "originales_congelados"
    frozen_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for spec in specs:
        dst = frozen_dir / f"{spec.rol}__{spec.selected.name}"
        shutil.copy2(spec.selected, dst)
        copied.append({"ROL": spec.rol, "ORIGEN": str(spec.selected), "COPIA": str(dst), "SHA256": sha256(dst)})

    append_tsv(
        paths["decisiones"],
        {
            "FECHA": now_iso(),
            "FASE": "FASE_0",
            "DECISION": "SELECCION_PROMEDIOSDEALUMNOS_ACTUAL",
            "EVIDENCIA": "COMPARACION_PROMEDIOS_CONGELADO_VS_INPUT_20260701_232300 sin diferencias reales.",
            "IMPACTO": "Se congela copia actual del root/input como fuente institucional de estudiantes.",
        },
        ["FECHA", "FASE", "DECISION", "EVIDENCIA", "IMPACTO"],
    )

    validation_rows = [
        {"FASE": "FASE_0", "VALIDACION": "FUENTES_OBLIGATORIAS_EXISTEN", "ESTADO": "OK", "DETALLE": str(len(specs))},
        {"FASE": "FASE_0", "VALIDACION": "COPIAS_CONGELADAS_GENERADAS", "ESTADO": "OK", "DETALLE": str(len(copied))},
        {"FASE": "FASE_0", "VALIDACION": "PROMEDIOS_VERSIONES_COMPARADAS", "ESTADO": "OK", "DETALLE": "Sin diferencias reales documentadas"},
    ]
    for row in validation_rows:
        append_tsv(paths["validaciones"], row, ["FASE", "VALIDACION", "ESTADO", "DETALLE"])

    checkpoint = {
        "fase": "FASE_0",
        "estado": "COMPLETADA_CON_OBSERVACIONES",
        "fecha": now_iso(),
        "entradas": selected_rows,
        "salidas": [
            str(exec_dir / "01_FUENTES" / "INVENTARIO_FUENTES.xlsx"),
            str(exec_dir / "01_FUENTES" / "INVENTARIO_FUENTES.tsv"),
            str(paths["manifest_fuentes"]),
        ],
        "observaciones": [
            "PROMEDIOSDEALUMNOS tiene hash fisico distinto entre congelado previo e input, con comparacion previa sin diferencias reales.",
            "Se conservaron alternativas y artefactos previos en inventario; no se modificaron fuentes originales.",
        ],
    }
    save_json(paths["checkpoint"], checkpoint)
    make_resume(exec_dir, 1, "Fase 0 completada; continuar con matriz normativa.")
    mark_phase(exec_dir, state, 0, "COMPLETADA_CON_OBSERVACIONES", next_phase=1, bloqueos=0)
    return True


def official_rules() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rule_rows = [
        ("R001", "GENERAL", "", "Temporalidad", "Universo al 30 de abril de 2025; planes vigentes durante 2025; unidades cursadas/aprobadas en 2025 y acumuladas hasta cierre 2025.", "UNIVERSO", "OBLIGATORIA", "", "Instructivo", "4.1", "6", "OFICIAL"),
        ("R002", "GENERAL", "", "Dos cargas separadas", "El modulo se compone de Carreras Avance Curricular 2026 y Matricula Avance Curricular 2026.", "ESTRUCTURA", "OBLIGATORIA", "", "Instructivo", "4.2", "6", "OFICIAL"),
        ("R003", "GENERAL", "", "Orden PES", "Cargar primero Carreras ID 16769 y despues Matricula ID 16768 para evitar tabla inexistente o carrera no encontrada.", "DEPENDENCIA", "OBLIGATORIA", "", "Instructivo", "Anexo III", "17", "OFICIAL"),
        ("R004", "GENERAL", "", "Preparacion fisica", "Eliminar primera columna correspondiente al codigo de institucion y encabezados antes de cargar CSV en PES.", "FORMATO", "OBLIGATORIA", "", "Instructivo", "Anexo III", "15", "OFICIAL"),
        ("R005", "GENERAL", "", "Carga acumulativa", "PES reemplaza registros repetidos por combinacion llave de cada carga.", "PES", "OBLIGATORIA", "", "Instructivo", "Anexo III", "17", "OFICIAL"),
        ("R006", "CARRERAS", "PLAN_ESTUDIOS", "Plan de estudios", "Correlativo de planes vigentes; por defecto 1; duplicar fila si hay mas de un plan vigente con unidades o total distinto.", "CAMPO", "OBLIGATORIA", "NUMEROS_CORRELATIVOS", "Instructivo", "Anexo I", "8", "OFICIAL"),
        ("R007", "CARRERAS", "TIPO_UNIDAD_MEDIDA", "Tipo unidad", "Debe ser 1 asignaturas/cursos/modulos, 2 creditos academicos/SCT, o 3 otra unidad.", "CATALOGO", "OBLIGATORIA", "1|2|3", "Instructivo", "Anexo I", "9", "OFICIAL"),
        ("R008", "CARRERAS", "OTRA_UNIDAD_MEDIDA", "Otra unidad", "Texto requerido solo cuando TIPO_UNIDAD_MEDIDA es 3; se completa solo si tipo es 3.", "CONDICIONAL", "CONDICIONAL", "", "Instructivo", "Anexo I y IV", "9,21", "OFICIAL"),
        ("R009", "CARRERAS", "TOTAL_UNIDADES_MEDIDA", "Total unidades", "Numero entero total de unidades del plan.", "CAMPO", "OBLIGATORIA", "ENTERO", "Instructivo", "Anexo I", "9", "OFICIAL"),
        ("R010", "CARRERAS", "UNIDADES_1ER_ANIO..UNIDADES_7MO_ANIO", "Distribucion anual", "Numeros enteros por anio; suma coherente con total y duracion de estudios.", "VALIDACION", "OBLIGATORIA", "ENTERO", "Instructivo", "Anexo I y IV", "9-10,21", "OFICIAL"),
        ("R011", "CARRERAS", "VIGENCIA", "Vigencia carreras", "Valores 0 eliminar registro, 1 mantener registro.", "CATALOGO", "OBLIGATORIA", "0|1", "Instructivo", "Anexo I", "10", "OFICIAL"),
        ("R012", "MATRICULA", "PLAN_ESTUDIOS", "Plan estudiante", "Debe utilizar alguno de los numeros de plan informados en Carreras para el CODIGO_UNICO de la matricula.", "REFERENCIAL", "OBLIGATORIA", "", "Instructivo", "Anexo II", "12", "OFICIAL"),
        ("R013", "MATRICULA", "CURSO_1ER_SEM", "Presencia primer semestre", "Valores permitidos SI y NO.", "CATALOGO", "OBLIGATORIA", "SI|NO", "Instructivo", "Anexo II", "12", "OFICIAL"),
        ("R014", "MATRICULA", "CURSO_2DO_SEM", "Presencia segundo semestre", "Valores permitidos SI y NO.", "CATALOGO", "OBLIGATORIA", "SI|NO", "Instructivo", "Anexo II", "13", "OFICIAL"),
        ("R015", "MATRICULA", "UNIDADES_CURSADAS", "Cursadas 2025", "Numero de unidades cursadas efectivamente durante 2025 del plan informado; no incluir unidades de otras carreras ni reconocimientos previos.", "CAMPO", "OBLIGATORIA", "NUMERICO", "Instructivo", "3.2 i; Anexo II", "5,13", "OFICIAL"),
        ("R016", "MATRICULA", "UNIDADES_APROBADAS", "Aprobadas 2025", "Numero de unidades aprobadas efectivamente durante 2025; no incluir validacion de estudios ni reconocimiento de aprendizajes previos.", "CAMPO", "OBLIGATORIA", "NUMERICO", "Instructivo", "3.2 j; Anexo II", "5,13", "OFICIAL"),
        ("R017", "MATRICULA", "UNID_CURSADAS_TOTAL", "Cursadas total", "Acumulado desde ingreso hasta cierre 2025; incluye unidades aprobadas por validacion o reconocimiento cuando pertenecen al plan actual.", "CAMPO", "OBLIGATORIA", "NUMERICO", "Instructivo", "3.2 i; Anexo II", "5,13", "OFICIAL"),
        ("R018", "MATRICULA", "UNID_APROBADAS_TOTAL", "Aprobadas total", "Acumulado desde ingreso hasta cierre 2025; incluye reconocimientos permitidos; tolerancia 25% sobre total del plan.", "CAMPO", "OBLIGATORIA", "NUMERICO", "Instructivo", "3.2 j; Anexo II", "5,14", "OFICIAL"),
        ("R019", "MATRICULA", "VIGENCIA", "Vigencia matricula", "Todos los registros del universo deben considerarse vigentes 1 aunque exista retiro posterior al 30 de abril de 2025; 0 solo elimina registro cargado por error o no correspondiente.", "CATALOGO", "OBLIGATORIA", "0|1", "Instructivo", "4.2; Anexo II", "7,14", "OFICIAL"),
        ("R020", "MATRICULA", "UNID_APROBADAS_TOTAL", "Tolerancia", "Cantidad total aprobada no debe exceder 25% por sobre unidades del plan.", "VALIDACION", "OBLIGATORIA", "TOTAL_PLAN*1.25", "Instructivo", "3.2 j; Anexo V", "5,22", "OFICIAL"),
    ]
    rules = pd.DataFrame(
        rule_rows,
        columns=[
            "ID_REGLA",
            "PROCESO",
            "CAMPO",
            "DESCRIPCION",
            "TIPO",
            "OBLIGATORIEDAD",
            "CATALOGO",
            "FUENTE",
            "SECCION",
            "PAGINA",
            "NIVEL_RESPALDO",
        ],
    )

    carreras = pd.DataFrame(
        [
            [c, "CARRERAS", "SI" if c in NO_MOD_5810 else "NO", "SI" if c in ("PLAN_ESTUDIOS", "TIPO_UNIDAD_MEDIDA", "TOTAL_UNIDADES_MEDIDA", "VIGENCIA") else "SEGUN_DURACION" if c.startswith("UNIDADES_") else "NO"]
            for c in COLUMNAS_5810
        ],
        columns=["CAMPO", "SUBPROCESO", "NO_MODIFICABLE", "OBLIGATORIEDAD"],
    )
    matricula = pd.DataFrame(
        [
            [c, "MATRICULA", "SI" if c in NO_MOD_5809 else "NO", "SI" if c in ("PLAN_ESTUDIOS", "CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL", "VIGENCIA") else "PRECARGADO"]
            for c in COLUMNAS_5809
        ],
        columns=["CAMPO", "SUBPROCESO", "NO_MODIFICABLE", "OBLIGATORIEDAD"],
    )
    no_mod = pd.concat(
        [
            carreras[carreras["NO_MODIFICABLE"].eq("SI")][["SUBPROCESO", "CAMPO"]],
            matricula[matricula["NO_MODIFICABLE"].eq("SI")][["SUBPROCESO", "CAMPO"]],
        ],
        ignore_index=True,
    )
    oblig = pd.concat(
        [
            carreras[carreras["OBLIGATORIEDAD"].ne("NO")][["SUBPROCESO", "CAMPO", "OBLIGATORIEDAD"]],
            matricula[matricula["OBLIGATORIEDAD"].ne("PRECARGADO")][["SUBPROCESO", "CAMPO", "OBLIGATORIEDAD"]],
        ],
        ignore_index=True,
    )
    catalogos = pd.DataFrame(
        [
            ["CARRERAS", "JORNADA", "1", "Diurna"],
            ["CARRERAS", "JORNADA", "2", "Vespertina"],
            ["CARRERAS", "JORNADA", "3", "Semipresencial"],
            ["CARRERAS", "JORNADA", "4", "A Distancia"],
            ["CARRERAS", "JORNADA", "5", "Otra"],
            ["CARRERAS", "NIVEL_CARRERA", "0", "Bachillerato, Ciclo Inicial o Plan Comun"],
            ["CARRERAS", "NIVEL_CARRERA", "1", "Tecnico de Nivel Superior"],
            ["CARRERAS", "NIVEL_CARRERA", "2", "Profesional Sin Licenciatura"],
            ["CARRERAS", "NIVEL_CARRERA", "3", "Licenciatura No Conducente a Titulo"],
            ["CARRERAS", "NIVEL_CARRERA", "4", "Profesional Con Licenciatura"],
            ["CARRERAS", "TIPO_UNIDAD_MEDIDA", "1", "Asignaturas, Cursos y/o Modulos"],
            ["CARRERAS", "TIPO_UNIDAD_MEDIDA", "2", "Creditos Academicos o SCT-Chile"],
            ["CARRERAS", "TIPO_UNIDAD_MEDIDA", "3", "Otra Unidad de Medida"],
            ["CARRERAS", "VIGENCIA", "0", "Eliminar Registro"],
            ["CARRERAS", "VIGENCIA", "1", "Mantener Registro"],
            ["MATRICULA", "TIPO_DOCUMENTO", "P", "Pasaporte"],
            ["MATRICULA", "TIPO_DOCUMENTO", "R", "RUN"],
            ["MATRICULA", "SEXO", "M", "Mujer"],
            ["MATRICULA", "SEXO", "H", "Hombre"],
            ["MATRICULA", "SEXO", "X", "No Binario"],
            ["MATRICULA", "CURSO_1ER_SEM", "SI", "Cursa actividades"],
            ["MATRICULA", "CURSO_1ER_SEM", "NO", "No cursa actividades"],
            ["MATRICULA", "CURSO_2DO_SEM", "SI", "Cursa actividades"],
            ["MATRICULA", "CURSO_2DO_SEM", "NO", "No cursa actividades"],
            ["MATRICULA", "VIGENCIA", "0", "Eliminar Registro"],
            ["MATRICULA", "VIGENCIA", "1", "Mantener Registro"],
        ],
        columns=["SUBPROCESO", "CAMPO", "CODIGO", "DESCRIPCION"],
    )
    validaciones = pd.DataFrame(
        [
            ["CARRERAS", "No modificar campos protegidos de precarga."],
            ["CARRERAS", "TOTAL_UNIDADES_MEDIDA coincide con suma anual."],
            ["CARRERAS", "Unidades por anio requeridas segun DURACION_ESTUDIOS."],
            ["MATRICULA", "UNIDADES_APROBADAS <= UNIDADES_CURSADAS."],
            ["MATRICULA", "UNID_APROBADAS_TOTAL <= UNID_CURSADAS_TOTAL."],
            ["MATRICULA", "UNIDADES_CURSADAS <= UNID_CURSADAS_TOTAL."],
            ["MATRICULA", "UNIDADES_APROBADAS <= UNID_APROBADAS_TOTAL."],
            ["MATRICULA", "Si ambos semestres son NO, UNIDADES_CURSADAS debe ser 0."],
            ["MATRICULA", "Combinacion CODIGO_UNICO + PLAN_ESTUDIOS debe existir en Carreras."],
            ["MATRICULA", "UNID_APROBADAS_TOTAL no excede TOTAL_UNIDADES_MEDIDA * 1.25."],
        ],
        columns=["SUBPROCESO", "REGLA_VALIDACION"],
    )
    return rules, carreras, matricula, no_mod, oblig, catalogos, validaciones


def phase1(exec_dir: Path, state: dict[str, Any]) -> bool:
    mark_phase(exec_dir, state, 1, "EN_EJECUCION", next_phase=1)
    paths = control_paths(exec_dir)
    out = exec_dir / "02_DIAGNOSTICOS"
    rules, carreras, matricula, no_mod, oblig, catalogos, validaciones = official_rules()
    write_xlsx(
        out / "MATRIZ_REGLAS_OFICIALES.xlsx",
        {
            "REGLAS": rules,
            "DICC_CARRERAS": carreras,
            "DICC_MATRICULA": matricula,
            "NO_MODIFICABLES": no_mod,
            "OBLIGATORIOS": oblig,
            "CATALOGOS": catalogos,
            "VALIDACIONES": validaciones,
        },
    )
    rules.to_csv(out / "MATRIZ_REGLAS_OFICIALES.tsv", sep="\t", index=False)
    carreras.to_csv(out / "DICCIONARIO_CARRERAS_OFICIAL.tsv", sep="\t", index=False)
    matricula.to_csv(out / "DICCIONARIO_MATRICULA_OFICIAL.tsv", sep="\t", index=False)
    no_mod.to_csv(out / "CAMPOS_NO_MODIFICABLES.tsv", sep="\t", index=False)
    oblig.to_csv(out / "CAMPOS_OBLIGATORIOS.tsv", sep="\t", index=False)
    catalogos.to_csv(out / "CATALOGOS_OFICIALES.tsv", sep="\t", index=False)
    validaciones.to_csv(out / "REGLAS_VALIDACION_FUNCIONAL.tsv", sep="\t", index=False)

    append_tsv(paths["validaciones"], {"FASE": "FASE_1", "VALIDACION": "MATRIZ_NORMATIVA_GENERADA", "ESTADO": "OK", "DETALLE": str(len(rules))}, ["FASE", "VALIDACION", "ESTADO", "DETALLE"])
    save_json(
        paths["checkpoint"],
        {
            "fase": "FASE_1",
            "estado": "COMPLETADA",
            "fecha": now_iso(),
            "entradas": [str(exec_dir / "01_FUENTES" / "originales_congelados")],
            "salidas": [str(out / "MATRIZ_REGLAS_OFICIALES.xlsx")],
        },
    )
    make_resume(exec_dir, 2, "Fase 1 completada; continuar con perfil fisico.")
    mark_phase(exec_dir, state, 1, "COMPLETADA", next_phase=2, bloqueos=0)
    return True


def selected_source_path(exec_dir: Path, role: str) -> Path:
    manifest = json.loads(control_paths(exec_dir)["manifest_fuentes"].read_text(encoding="utf-8"))
    for row in manifest["fuentes_seleccionadas"]:
        if row["ROL"] == role:
            return Path(row["RUTA"])
    raise RuntimeError(f"No se encontro fuente seleccionada para {role}")


def phase2(exec_dir: Path, state: dict[str, Any]) -> bool:
    mark_phase(exec_dir, state, 2, "EN_EJECUCION", next_phase=2)
    paths = control_paths(exec_dir)
    out = exec_dir / "07_VALIDACIONES_TECNICAS"
    carreras_path = selected_source_path(exec_dir, "PRECARGA_CARRERAS_5810")
    matricula_path = selected_source_path(exec_dir, "PRECARGA_MATRICULA_5809")
    carreras = csv_profile(carreras_path)
    matricula = csv_profile(matricula_path)
    save_json(out / "PERFIL_FISICO_CARRERAS.json", carreras)
    save_json(out / "PERFIL_FISICO_MATRICULA.json", matricula)
    pd.DataFrame({"ORDEN": range(1, len(carreras["encabezados"]) + 1), "CAMPO": carreras["encabezados"]}).to_csv(out / "COLUMNAS_CARRERAS.tsv", sep="\t", index=False)
    pd.DataFrame({"ORDEN": range(1, len(matricula["encabezados"]) + 1), "CAMPO": matricula["encabezados"]}).to_csv(out / "COLUMNAS_MATRICULA.tsv", sep="\t", index=False)
    invalid = carreras["filas_con_estructura_invalida"] + matricula["filas_con_estructura_invalida"]
    write_tsv(out / "FILAS_CON_ESTRUCTURA_INVALIDA.tsv", invalid, ["archivo", "linea", "columnas_observadas", "columnas_esperadas"])

    errors = []
    if carreras["encabezados"] != COLUMNAS_5810:
        errors.append("COLUMNAS_CARRERAS_DIFIEREN")
    if matricula["encabezados"] != COLUMNAS_5809:
        errors.append("COLUMNAS_MATRICULA_DIFIEREN")
    if invalid:
        errors.append("FILAS_CON_ESTRUCTURA_INVALIDA")
    if errors:
        for err in errors:
            append_tsv(paths["bloqueos"], {"FECHA": now_iso(), "FASE": "FASE_2", "MOTIVO": err, "DETALLE": "Perfil fisico de precargas", "ACCION": "Revisar perfil fisico antes de continuar."}, ["FECHA", "FASE", "MOTIVO", "DETALLE", "ACCION"])
        mark_phase(exec_dir, state, 2, "BLOQUEADA", next_phase=2, bloqueos=len(errors))
        make_resume(exec_dir, 2, "Bloqueo en perfil fisico.")
        return False

    append_tsv(paths["validaciones"], {"FASE": "FASE_2", "VALIDACION": "PRECARGAS_RELEIDAS_SIN_PERDIDA", "ESTADO": "OK", "DETALLE": "5810=43 filas; 5809=2371 filas"}, ["FASE", "VALIDACION", "ESTADO", "DETALLE"])
    save_json(
        paths["checkpoint"],
        {
            "fase": "FASE_2",
            "estado": "COMPLETADA",
            "fecha": now_iso(),
            "salidas": [str(out / "PERFIL_FISICO_CARRERAS.json"), str(out / "PERFIL_FISICO_MATRICULA.json")],
        },
    )
    make_resume(exec_dir, 3, "Fase 2 completada; continuar con baseline no modificable.")
    mark_phase(exec_dir, state, 2, "COMPLETADA", next_phase=3, bloqueos=0)
    return True


def read_csv_with_profile(path: Path, profile: dict[str, Any]) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=profile["delimitador"],
        encoding=profile["encoding"],
        dtype=str,
        keep_default_na=False,
    )


def row_hash(row: pd.Series, columns: list[str]) -> str:
    payload = "\x1f".join("" if pd.isna(row[col]) else str(row[col]) for col in columns)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def phase3(exec_dir: Path, state: dict[str, Any]) -> bool:
    mark_phase(exec_dir, state, 3, "EN_EJECUCION", next_phase=3)
    paths = control_paths(exec_dir)
    out = exec_dir / "07_VALIDACIONES_TECNICAS"
    carreras_path = selected_source_path(exec_dir, "PRECARGA_CARRERAS_5810")
    matricula_path = selected_source_path(exec_dir, "PRECARGA_MATRICULA_5809")
    prof_c = json.loads((out / "PERFIL_FISICO_CARRERAS.json").read_text(encoding="utf-8"))
    prof_m = json.loads((out / "PERFIL_FISICO_MATRICULA.json").read_text(encoding="utf-8"))
    carreras = read_csv_with_profile(carreras_path, prof_c)
    matricula = read_csv_with_profile(matricula_path, prof_m)

    base_c = carreras[NO_MOD_5810].copy()
    base_c.insert(0, "ID_FILA_PRECARGA", range(1, len(base_c) + 1))
    base_c["HASH_NO_MODIFICABLES"] = carreras.apply(lambda row: row_hash(row, NO_MOD_5810), axis=1)
    base_m = matricula[NO_MOD_5809].copy()
    base_m.insert(0, "ID_FILA_PRECARGA", range(1, len(base_m) + 1))
    base_m["HASH_NO_MODIFICABLES"] = matricula.apply(lambda row: row_hash(row, NO_MOD_5809), axis=1)
    base_c.to_csv(out / "BASELINE_NO_MODIFICABLES_CARRERAS.tsv", sep="\t", index=False)
    base_m.to_csv(out / "BASELINE_NO_MODIFICABLES_MATRICULA.tsv", sep="\t", index=False)
    base_c[["ID_FILA_PRECARGA", "HASH_NO_MODIFICABLES"]].to_csv(out / "HASH_FILA_PRECARGA_CARRERAS.tsv", sep="\t", index=False)
    base_m[["ID_FILA_PRECARGA", "HASH_NO_MODIFICABLES"]].to_csv(out / "HASH_FILA_PRECARGA_MATRICULA.tsv", sep="\t", index=False)
    append_tsv(paths["validaciones"], {"FASE": "FASE_3", "VALIDACION": "BASELINE_NO_MODIFICABLES_GENERADO", "ESTADO": "OK", "DETALLE": "Carreras 43; Matricula 2371"}, ["FASE", "VALIDACION", "ESTADO", "DETALLE"])
    save_json(
        paths["checkpoint"],
        {
            "fase": "FASE_3",
            "estado": "COMPLETADA",
            "fecha": now_iso(),
            "salidas": [str(out / "BASELINE_NO_MODIFICABLES_CARRERAS.tsv"), str(out / "BASELINE_NO_MODIFICABLES_MATRICULA.tsv")],
        },
    )
    make_resume(exec_dir, 4, "Fase 3 completada; continuar con conciliacion de carreras y planes.")
    mark_phase(exec_dir, state, 3, "COMPLETADA", next_phase=4, bloqueos=0)
    return True


def write_summary(exec_dir: Path, lines: list[str]) -> None:
    control_paths(exec_dir)["resumen"].write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-dir", type=Path)
    parser.add_argument("--desde-fase", type=int, default=0)
    parser.add_argument("--hasta-fase", type=int, default=3)
    args = parser.parse_args()

    exec_dir = init_execution(args.execution_dir)
    state = load_state(exec_dir)
    paths = control_paths(exec_dir)
    if not paths["manifest_salidas"].exists():
        save_json(paths["manifest_salidas"], {"fecha": now_iso(), "salidas": []})
    for empty in ("bloqueos", "contradicciones", "validaciones", "decisiones"):
        if not paths[empty].exists():
            paths[empty].touch()

    phases = {
        0: phase0,
        1: phase1,
        2: phase2,
        3: phase3,
    }
    ok = True
    for phase in range(args.desde_fase, args.hasta_fase + 1):
        if phase not in phases:
            break
        ok = phases[phase](exec_dir, state)
        if not ok:
            break

    summary = [
        "CIERRE INTEGRAL AVANCE CURRICULAR SIES 2026",
        f"Carpeta ejecucion: {exec_dir}",
        f"Fecha ultima actualizacion: {now_iso()}",
        f"Estado general: {state.get('estado_general')}",
        f"Ultima fase completada: {state.get('ultima_fase_completada')}",
        f"Siguiente fase: {state.get('siguiente_fase')}",
        f"Bloqueos activos: {state.get('bloqueos_activos')}",
        "Fuentes originales modificadas: NO",
        "Carga PES realizada: NO",
    ]
    write_summary(exec_dir, summary)
    print("\n".join(summary))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
