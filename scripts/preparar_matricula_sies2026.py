#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook


REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()
PROCESO_DIR = REPO / "avance_curricular_2026"
EXEC_DEFAULT = (
    PROCESO_DIR
    / "05_cierre_integral"
    / "CIERRE_AVANCE_CURRICULAR_20260703_125157"
)

SUBDIRS = [
    "00_CONTROL",
    "01_UNIVERSO",
    "02_IDENTIFICADORES",
    "03_LLAVES_DUPLICADOS",
    "04_PLANES",
    "05_PERIODIZACIONES",
    "06_CAMPOS_MODIFICABLES",
    "07_VALIDACIONES",
    "08_AUDITORIA",
    "09_REPORTES",
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

MODIFICABLES = [
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "PLAN_ESTUDIOS",
    "VIGENCIA",
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    if re.fullmatch(r"-?\d+\.0", text):
        text = text[:-2]
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", "", text)


def norm_doc(value: Any) -> str:
    return re.sub(r"[^0-9K]", "", norm(value))


def split_rut(value: Any) -> tuple[str, str]:
    text = norm(value)
    if "-" in text:
        body, dv = text.rsplit("-", 1)
        return norm_doc(body), norm_doc(dv)
    clean = norm_doc(text)
    if len(clean) > 1 and clean[-1] in "0123456789K":
        return clean[:-1], clean[-1]
    return clean, ""


def join_unique(values: pd.Series | list[Any], limit: int | None = None) -> str:
    result = []
    seen = set()
    for value in values:
        text = "" if pd.isna(value) else str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    result = sorted(result)
    if limit is not None and len(result) > limit:
        return " | ".join(result[:limit]) + f" | ...(+{len(result) - limit})"
    return " | ".join(result)


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
    text = raw.decode(enc)
    sep = detect_delimiter(text)
    rows = list(csv.reader(text.splitlines(), delimiter=sep))
    if not rows:
        raise RuntimeError(f"CSV vacio: {path}")
    headers = rows[0]
    expected = len(headers)
    invalid = []
    count_by_cols: dict[str, int] = {}
    for line, row in enumerate(rows, start=1):
        count_by_cols[str(len(row))] = count_by_cols.get(str(len(row)), 0) + 1
        if len(row) != expected:
            invalid.append(
                {
                    "LINEA": line,
                    "COLUMNAS_OBSERVADAS": len(row),
                    "COLUMNAS_ESPERADAS": expected,
                }
            )
    df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str, keep_default_na=False)
    vacios = [
        {"COLUMNA": col, "VACIOS": int(df[col].astype(str).str.strip().eq("").sum())}
        for col in df.columns
    ]
    tipos = []
    for col in df.columns:
        serie = df[col].astype(str).str.strip()
        observed = set()
        if serie.eq("").any():
            observed.add("VACIO")
        nonempty = serie[serie.ne("")]
        if nonempty.str.fullmatch(r"-?\d+").all() and not nonempty.empty:
            observed.add("ENTERO_TEXTO")
        elif nonempty.str.fullmatch(r"-?\d+(?:[,.]\d+)?").all() and not nonempty.empty:
            observed.add("NUMERICO_TEXTO")
        elif not nonempty.empty:
            observed.add("TEXTO")
        tipos.append({"COLUMNA": col, "TIPOS_OBSERVADOS": " | ".join(sorted(observed))})
    return {
        "archivo": str(path),
        "codificacion": enc,
        "bom": "SI" if raw.startswith(b"\xef\xbb\xbf") else "NO",
        "delimitador": sep,
        "salto_linea": detect_eol(raw),
        "tiene_encabezado": "SI",
        "primera_columna": headers[0] if headers else "",
        "columnas": expected,
        "encabezados": headers,
        "filas_totales_incluye_encabezado": len(rows),
        "filas_datos": len(df),
        "conteo_columnas_por_fila": count_by_cols,
        "filas_con_distinto_numero_campos": invalid,
        "valores_vacios": vacios,
        "tipos_observados": tipos,
    }


def xlsx_profile(path: Path) -> dict[str, Any]:
    wb = load_workbook(path, read_only=True, data_only=True)
    sheets = []
    for ws in wb.worksheets:
        headers = []
        if ws.max_row > 0:
            headers = ["" if value is None else str(value) for value in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
        sheets.append(
            {
                "HOJA": ws.title,
                "FILAS": ws.max_row,
                "COLUMNAS": ws.max_column,
                "ENCABEZADOS": " | ".join(headers),
            }
        )
    return {"hojas": len(sheets), "detalle_hojas": sheets}


def file_meta(path: Path, rol: str, uso: str) -> dict[str, Any]:
    stat = path.stat()
    row = {
        "ROL": rol,
        "USO": uso,
        "NOMBRE": path.name,
        "RUTA": str(path),
        "TAMANO_BYTES": stat.st_size,
        "FECHA_MODIFICACION": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
        "SHA256": sha256(path),
    }
    try:
        if path.suffix.lower() == ".csv":
            prof = csv_profile(path)
            row.update(
                {
                    "FILAS": prof["filas_datos"],
                    "COLUMNAS": prof["columnas"],
                    "HOJAS": "",
                    "ESTRUCTURA": "CSV " + prof["delimitador"],
                }
            )
        elif path.suffix.lower() in (".xlsx", ".xlsm"):
            prof = xlsx_profile(path)
            row.update(
                {
                    "FILAS": "",
                    "COLUMNAS": "",
                    "HOJAS": prof["hojas"],
                    "ESTRUCTURA": "XLSX",
                }
            )
        else:
            row.update({"FILAS": "", "COLUMNAS": "", "HOJAS": "", "ESTRUCTURA": path.suffix.lower().lstrip(".")})
    except Exception as exc:
        row["ESTRUCTURA"] = f"ERROR_PERFIL: {type(exc).__name__}: {exc}"
    return row


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_tsv(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            sheet = re.sub(r"[\[\]\*\?/\\:]", "_", name)[:31]
            df.to_excel(writer, sheet_name=sheet, index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                letter = col[0].column_letter
                width = max(len(str(cell.value or "")) for cell in col[:1000])
                ws.column_dimensions[letter].width = min(max(width + 2, 12), 60)


def append_control(path: Path, row: dict[str, Any], columns: list[str]) -> None:
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def init_prep(base_exec: Path, prep_dir: Path | None = None) -> Path:
    if prep_dir is None:
        prep_dir = base_exec / "04_CONCILIACION_MATRICULA" / f"PREPARACION_MATRICULA_{timestamp()}"
    for sub in SUBDIRS:
        (prep_dir / sub).mkdir(parents=True, exist_ok=True)
    return prep_dir.resolve()


def control_paths(prep: Path) -> dict[str, Path]:
    c = prep / "00_CONTROL"
    return {
        "estado": c / "ESTADO_PREPARACION_MATRICULA.json",
        "checkpoint": c / "CHECKPOINT_PREPARACION.json",
        "manifest_fuentes": c / "MANIFEST_FUENTES.json",
        "manifest_salidas": c / "MANIFEST_SALIDAS.json",
        "bloqueos": c / "BLOQUEOS.tsv",
        "decisiones": c / "DECISIONES.tsv",
        "contradicciones": c / "CONTRADICCIONES.tsv",
        "validaciones": c / "VALIDACIONES.tsv",
        "reanudar": c / "REANUDAR_DESDE_AQUI.md",
    }


def load_sources(base_exec: Path) -> dict[str, Path]:
    manifest = json.loads((base_exec / "00_CONTROL" / "MANIFEST_FUENTES.json").read_text(encoding="utf-8"))
    by_role = {row["ROL"]: Path(row["RUTA"]) for row in manifest["fuentes_seleccionadas"]}
    audit = PROCESO_DIR / "04_gobernanza_mallas" / "03_auditorias"
    sources = {
        "INSTRUCTIVO": by_role["FUENTE_NORMATIVA_PRINCIPAL"],
        "PRECARGA_5809": by_role["PRECARGA_MATRICULA_5809"],
        "PROMEDIOS": by_role["FUENTE_ESTUDIANTES_PROMEDIOS"],
        "CONCILIACION_CARRERAS": base_exec / "03_CONCILIACION_CARRERAS" / "MAPEO_CODIGO_UNICO_PLAN.tsv",
        "PLANES_DISTRIBUCION_NO_DEMOSTRADA": base_exec / "03_CONCILIACION_CARRERAS" / "PLANES_DISTRIBUCION_NO_DEMOSTRADA.tsv",
        "CLASIFICACION_29": audit / "CLASIFICACION_29_MODELOS_PERIODIZACION_20260703_123007" / "02_RESULTADOS" / "CLASIFICACION_29_MODELOS_PERIODIZACION.xlsx",
        "DIAGNOSTICO_27": audit / "DIAGNOSTICO_27_CODCLI_PLAN_20260703_123419" / "02_RESULTADOS" / "01_DIAGNOSTICO_27_PENDIENTES.tsv",
        "DESCOMP_14": audit / "DESCOMPOSICION_19_CANDIDATOS_DEBILES_20260703_123657" / "02_RESULTADOS" / "04_PENDIENTES_INTERMEDIOS.tsv",
        "DESCOMP_5": audit / "DESCOMPOSICION_19_CANDIDATOS_DEBILES_20260703_123657" / "02_RESULTADOS" / "05_PENDIENTES_DEBILES_O_SIN_MODELO.tsv",
    }
    return sources


def read_5809(path: Path, profile: dict[str, Any] | None = None) -> pd.DataFrame:
    if profile is None:
        profile = csv_profile(path)
    df = pd.read_csv(path, sep=profile["delimitador"], encoding=profile["codificacion"], dtype=str, keep_default_na=False)
    if list(df.columns) != COLUMNAS_5809:
        raise RuntimeError("La precarga 5809 no conserva el orden oficial de columnas.")
    df.insert(0, "ID_FILA_5809", range(1, len(df) + 1))
    df["DOC_PRECARGA_BODY"] = df["NUM_DOCUMENTO"].map(norm_doc)
    df["DV_PRECARGA_NORM"] = df["DV"].map(norm_doc)
    df["DOC_PRECARGA_FULL"] = df["DOC_PRECARGA_BODY"] + df["DV_PRECARGA_NORM"]
    return df


def row_hash(row: pd.Series, columns: list[str]) -> str:
    payload = "\x1f".join("" if pd.isna(row[col]) else str(row[col]) for col in columns)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def set_checkpoint(prep: Path, phase: str, status: str, outputs: list[Path], next_phase: str) -> None:
    cp = {
        "fase": phase,
        "estado": status,
        "fecha": now_iso(),
        "salidas": [str(p) for p in outputs],
        "siguiente_fase": next_phase,
    }
    write_json(control_paths(prep)["checkpoint"], cp)
    command = f'python3 scripts/preparar_matricula_sies2026.py --execution-dir "{EXEC_DEFAULT}" --prep-dir "{prep}" --desde-fase {next_phase}'
    control_paths(prep)["reanudar"].write_text(
        "\n".join(
            [
                "# Reanudar preparacion de Matricula",
                "",
                f"Carpeta: {prep}",
                f"Siguiente fase sugerida: {next_phase}",
                "",
                "```bash",
                command,
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


class PrepRunner:
    def __init__(self, base_exec: Path, prep: Path):
        self.base_exec = base_exec
        self.prep = prep
        self.paths = control_paths(prep)
        self.sources = load_sources(base_exec)
        self.state = {
            "proceso": "Avance Curricular SIES 2026",
            "subproceso": "Matricula Avance Curricular 2026",
            "anio_proceso": 2026,
            "anio_datos": 2025,
            "fecha_inicio": now_iso(),
            "fecha_ultima_actualizacion": now_iso(),
            "estado": "EN_EJECUCION",
            "fase_actual": "M0",
            "fases": {f"M{i}": "NO_INICIADA" for i in range(11)},
            "archivos_sies_ready_generados": False,
            "csv_carga_generado": False,
            "carga_pes_realizada": False,
        }

    def mark(self, phase: str, status: str) -> None:
        self.state["fase_actual"] = phase
        self.state["fases"][phase] = status
        self.state["fecha_ultima_actualizacion"] = now_iso()
        if status.startswith("PREPARACION_MATRICULA"):
            self.state["estado"] = status
        elif status == "BLOQUEADA":
            self.state["estado"] = "PREPARACION_MATRICULA_BLOQUEADA"
        else:
            self.state["estado"] = "EN_EJECUCION"
        write_json(self.paths["estado"], self.state)

    def validation(self, phase: str, name: str, status: str, detail: str) -> None:
        append_control(
            self.paths["validaciones"],
            {"FASE": phase, "VALIDACION": name, "ESTADO": status, "DETALLE": detail},
            ["FASE", "VALIDACION", "ESTADO", "DETALLE"],
        )

    def decision(self, phase: str, decision: str, evidence: str, impact: str) -> None:
        append_control(
            self.paths["decisiones"],
            {"FECHA": now_iso(), "FASE": phase, "DECISION": decision, "EVIDENCIA": evidence, "IMPACTO": impact},
            ["FECHA", "FASE", "DECISION", "EVIDENCIA", "IMPACTO"],
        )

    def block(self, phase: str, kind: str, detail: str, action: str) -> None:
        append_control(
            self.paths["bloqueos"],
            {"FECHA": now_iso(), "FASE": phase, "TIPO": kind, "DETALLE": detail, "ACCION_REQUERIDA": action},
            ["FECHA", "FASE", "TIPO", "DETALLE", "ACCION_REQUERIDA"],
        )

    def m0(self) -> None:
        self.mark("M0", "EN_EJECUCION")
        missing = [name for name, path in self.sources.items() if not path.exists()]
        if missing:
            for name in missing:
                self.block("M0", "FALTA_FUENTE", f"{name}: {self.sources[name]}", "Ubicar fuente requerida.")
            raise RuntimeError("Faltan fuentes obligatorias: " + ", ".join(missing))
        roles = {
            "INSTRUCTIVO": "Fuente normativa oficial",
            "PRECARGA_5809": "Precarga Matricula Avance Curricular 2026",
            "PROMEDIOS": "Fuente institucional PROMEDIOSDEALUMNOS hoja DatosAlumnos",
            "CONCILIACION_CARRERAS": "Conciliacion de Carreras de ejecucion vigente",
            "PLANES_DISTRIBUCION_NO_DEMOSTRADA": "Dependencias de Carreras por distribucion anual",
            "CLASIFICACION_29": "Clasificacion de 29 casos de periodizacion",
            "DIAGNOSTICO_27": "Diagnostico de 27 pendientes",
            "DESCOMP_14": "Descomposicion 14 familia CODCLI + carrera",
            "DESCOMP_5": "Descomposicion 5 solo carrera",
        }
        inventory = pd.DataFrame([file_meta(path, name, roles.get(name, "")) for name, path in self.sources.items()])
        hashes = inventory[["ROL", "RUTA", "SHA256"]].copy()
        write_tsv(self.prep / "00_CONTROL" / "INVENTARIO_FUENTES_MATRICULA.tsv", inventory)
        write_tsv(self.prep / "00_CONTROL" / "HASHES_FUENTES_MATRICULA.tsv", hashes)
        write_json(
            self.paths["manifest_fuentes"],
            {
                "fecha": now_iso(),
                "fuentes": inventory.to_dict(orient="records"),
                "versiones_alternativas": "Se usan fuentes registradas en MANIFEST_FUENTES de la ejecucion vigente; no se sustituyen fuentes.",
            },
        )
        shutil.copy2(Path(__file__), self.prep / "08_AUDITORIA" / Path(__file__).name)
        self.validation("M0", "FUENTES_EXISTEN", "OK", str(len(self.sources)))
        self.mark("M0", "COMPLETADA")
        set_checkpoint(self.prep, "M0", "COMPLETADA", [self.paths["manifest_fuentes"]], "M1")

    def m1(self) -> dict[str, Any]:
        self.mark("M1", "EN_EJECUCION")
        prof = csv_profile(self.sources["PRECARGA_5809"])
        write_json(self.prep / "01_UNIVERSO" / "PERFIL_FISICO_5809.json", prof)
        cols = pd.DataFrame({"ORDEN": range(1, len(prof["encabezados"]) + 1), "COLUMNA": prof["encabezados"]})
        vacios = pd.DataFrame(prof["valores_vacios"])
        tipos = pd.DataFrame(prof["tipos_observados"])
        estructura = pd.DataFrame(prof["filas_con_distinto_numero_campos"])
        if estructura.empty:
            estructura = pd.DataFrame(columns=["LINEA", "COLUMNAS_OBSERVADAS", "COLUMNAS_ESPERADAS"])
        write_tsv(self.prep / "01_UNIVERSO" / "COLUMNAS_5809.tsv", cols)
        write_tsv(self.prep / "01_UNIVERSO" / "CONTROL_ESTRUCTURA_5809.tsv", estructura)
        write_tsv(self.prep / "01_UNIVERSO" / "VALORES_VACIOS_5809.tsv", vacios.merge(tipos, on="COLUMNA", how="left"))
        if prof["encabezados"] != COLUMNAS_5809 or prof["filas_con_distinto_numero_campos"]:
            self.block("M1", "ESTRUCTURA_5809_INVALIDA", "Columnas o filas invalidas en precarga 5809.", "Revisar fuente 5809 congelada.")
            raise RuntimeError("Estructura 5809 invalida.")
        self.validation("M1", "PERFIL_5809_OK", "OK", f"{prof['filas_datos']} filas, {prof['columnas']} columnas")
        self.mark("M1", "COMPLETADA")
        set_checkpoint(self.prep, "M1", "COMPLETADA", [self.prep / "01_UNIVERSO" / "PERFIL_FISICO_5809.json"], "M2")
        return prof

    def m2(self, prof: dict[str, Any]) -> pd.DataFrame:
        self.mark("M2", "EN_EJECUCION")
        df = read_5809(self.sources["PRECARGA_5809"], prof)
        official_key = ["CODIGO_IES_NUM", "TIPO_DOCUMENTO", "NUM_DOCUMENTO", "CODIGO_UNICO"]
        exact_dups = df[df.duplicated(COLUMNAS_5809, keep=False)].copy()
        partial_key_doc_carrera = ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO"]
        partial_dups = df[df.duplicated(partial_key_doc_carrera, keep=False)].copy()
        multiples_carreras = (
            df.groupby(["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"], dropna=False)
            .agg(FILAS=("ID_FILA_5809", "count"), CARRERAS=("CODIGO_UNICO", "nunique"), LISTA_CARRERAS=("CODIGO_UNICO", join_unique))
            .reset_index()
        )
        multiples_carreras = multiples_carreras[multiples_carreras["CARRERAS"].gt(1)].copy()
        multiples_planes = (
            df.groupby(["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO"], dropna=False)
            .agg(FILAS=("ID_FILA_5809", "count"), PLANES=("PLAN_ESTUDIOS", "nunique"), LISTA_PLANES=("PLAN_ESTUDIOS", join_unique))
            .reset_index()
        )
        multiples_planes = multiples_planes[multiples_planes["PLANES"].gt(1)].copy()
        multiples_filas = (
            df.groupby(["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"], dropna=False)
            .agg(FILAS=("ID_FILA_5809", "count"), ID_FILAS=("ID_FILA_5809", lambda s: join_unique(s.astype(str))))
            .reset_index()
        )
        multiples_filas = multiples_filas[multiples_filas["FILAS"].gt(1)].copy()
        resumen = pd.DataFrame(
            [
                ["FILAS_5809", len(df)],
                ["PERSONAS_UNICAS_TIPO_DOC_NUM_DV", df[["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV"]].drop_duplicates().shape[0]],
                ["DOCUMENTOS_UNICOS_NUM_DV", df[["NUM_DOCUMENTO", "DV"]].drop_duplicates().shape[0]],
                ["COMBINACIONES_DOCUMENTO_CARRERA", df[partial_key_doc_carrera].drop_duplicates().shape[0]],
                ["COMBINACIONES_DOCUMENTO_CARRERA_PLAN", df[partial_key_doc_carrera + ["PLAN_ESTUDIOS"]].drop_duplicates().shape[0]],
                ["LLAVE_OFICIAL_DISTINTA", df[official_key].drop_duplicates().shape[0]],
                ["DUPLICADOS_EXACTOS", len(exact_dups)],
                ["DUPLICADOS_PARCIALES_DOCUMENTO_CARRERA", len(partial_dups)],
                ["PERSONAS_MULTIPLES_CARRERAS", len(multiples_carreras)],
                ["PERSONAS_MULTIPLES_PLANES", len(multiples_planes)],
                ["PERSONAS_MULTIPLES_FILAS", len(multiples_filas)],
            ],
            columns=["INDICADOR", "VALOR"],
        )
        write_tsv(self.prep / "01_UNIVERSO" / "RESUMEN_UNIVERSO.tsv", resumen)
        write_tsv(self.prep / "03_LLAVES_DUPLICADOS" / "DUPLICADOS_EXACTOS.tsv", exact_dups)
        write_tsv(self.prep / "03_LLAVES_DUPLICADOS" / "DUPLICADOS_PARCIALES.tsv", partial_dups)
        write_tsv(self.prep / "03_LLAVES_DUPLICADOS" / "MULTIPLES_CARRERAS.tsv", multiples_carreras)
        write_tsv(self.prep / "03_LLAVES_DUPLICADOS" / "MULTIPLES_PLANES.tsv", multiples_planes)
        write_tsv(self.prep / "03_LLAVES_DUPLICADOS" / "MULTIPLES_FILAS_PERSONA.tsv", multiples_filas)
        write_xlsx(
            self.prep / "01_UNIVERSO" / "UNIVERSO_MATRICULA.xlsx",
            {
                "RESUMEN": resumen,
                "UNIVERSO_5809": df,
                "MULTIPLES_CARRERAS": multiples_carreras,
                "MULTIPLES_PLANES": multiples_planes,
                "MULTIPLES_FILAS": multiples_filas,
            },
        )
        if len(df) != 2371:
            self.block("M2", "UNIVERSO_CAMBIO", f"Filas observadas: {len(df)}", "Revisar precarga 5809.")
            raise RuntimeError("Cambio universo 5809.")
        self.validation("M2", "UNIVERSO_5809_CONSERVADO", "OK", "2371 filas")
        self.mark("M2", "COMPLETADA")
        set_checkpoint(self.prep, "M2", "COMPLETADA", [self.prep / "01_UNIVERSO" / "UNIVERSO_MATRICULA.xlsx"], "M3")
        return df

    def m3(self, df: pd.DataFrame) -> pd.DataFrame:
        self.mark("M3", "EN_EJECUCION")
        baseline = df[["ID_FILA_5809", *NO_MOD_5809]].copy()
        baseline["HASH_NO_MODIFICABLES"] = df.apply(lambda row: row_hash(row, NO_MOD_5809), axis=1)
        hashes = baseline[["ID_FILA_5809", "HASH_NO_MODIFICABLES"]].copy()
        dicc = pd.DataFrame(
            {
                "CAMPO": NO_MOD_5809,
                "FUENTE": "Instructivo Anexo II",
                "CONDICION": "Dato Precargado No Modificable",
            }
        )
        write_tsv(self.prep / "02_IDENTIFICADORES" / "BASELINE_NO_MODIFICABLES_MATRICULA.tsv", baseline)
        write_tsv(self.prep / "02_IDENTIFICADORES" / "HASH_FILA_NO_MODIFICABLES.tsv", hashes)
        write_tsv(self.prep / "02_IDENTIFICADORES" / "DICCIONARIO_CAMPOS_NO_MODIFICABLES.tsv", dicc)
        self.validation("M3", "BASELINE_NO_MODIFICABLES_GENERADO", "OK", str(len(baseline)))
        self.mark("M3", "COMPLETADA")
        set_checkpoint(self.prep, "M3", "COMPLETADA", [self.prep / "02_IDENTIFICADORES" / "BASELINE_NO_MODIFICABLES_MATRICULA.tsv"], "M4")
        return baseline

    def datos_alumnos_index(self) -> pd.DataFrame:
        datos = pd.read_excel(self.sources["PROMEDIOS"], sheet_name="DatosAlumnos", dtype=str, keep_default_na=False)
        datos = datos.dropna(axis=0, how="all").dropna(axis=1, how="all")
        datos["RUT_INST_BODY"] = datos["RUT"].map(lambda v: split_rut(v)[0])
        datos["DV_INST"] = datos["RUT"].map(lambda v: split_rut(v)[1])
        datos["CODCLI_NORM"] = datos["CODCLI"].map(norm)
        datos["CODCARPR_NORM"] = datos["CODCARPR"].map(norm)
        return datos

    def m4(self, df: pd.DataFrame) -> pd.DataFrame:
        self.mark("M4", "EN_EJECUCION")
        datos = self.datos_alumnos_index()
        carrera_map = pd.read_csv(self.sources["CONCILIACION_CARRERAS"], sep="\t", dtype=str, keep_default_na=False)
        codcarr_by_codigo = carrera_map.set_index("CODIGO_UNICO")["CODCARR_PLAN_INSTITUCIONAL"].to_dict()
        grouped = (
            datos.groupby("RUT_INST_BODY", dropna=False)
            .agg(
                N_REGISTROS_DATOS=("CODCLI_NORM", "size"),
                N_CODCLI=("CODCLI_NORM", "nunique"),
                CODCLI_LISTA=("CODCLI_NORM", join_unique),
                N_CODCARPR=("CODCARPR_NORM", "nunique"),
                CODCARPR_LISTA=("CODCARPR_NORM", join_unique),
                NIVELES_DATOS=("NIVEL", join_unique),
                RUT_INSTITUCIONAL=("RUT", join_unique),
                DV_INSTITUCIONAL=("DV_INST", join_unique),
                NOMBRES_DATOS=("NOMBRES", join_unique),
                APELLIDO_PATERNO_DATOS=("APELLIDO PATERNO", join_unique),
                APELLIDO_MATERNO_DATOS=("APELLIDO MATERNO", join_unique),
            )
            .reset_index()
        )
        ident = df.merge(grouped, left_on="DOC_PRECARGA_BODY", right_on="RUT_INST_BODY", how="left")
        for col in ["N_REGISTROS_DATOS", "N_CODCLI", "N_CODCARPR"]:
            ident[col] = pd.to_numeric(ident[col], errors="coerce").fillna(0).astype(int)
        ident["CODCARR_ESPERADO_SEGUN_CARRERAS"] = ident["CODIGO_UNICO"].map(codcarr_by_codigo).fillna("")
        ident["COINCIDE_DV_INSTITUCIONAL"] = ident.apply(
            lambda r: "SIN_MATCH" if r["N_REGISTROS_DATOS"] == 0 else ("SI" if r["DV_PRECARGA_NORM"] in str(r["DV_INSTITUCIONAL"]).split(" | ") else "NO"),
            axis=1,
        )
        ident["CODCARR_ESPERADO_EN_DATOS"] = ident.apply(
            lambda r: "SIN_MATCH" if r["N_REGISTROS_DATOS"] == 0 else ("SI" if r["CODCARR_ESPERADO_SEGUN_CARRERAS"] and r["CODCARR_ESPERADO_SEGUN_CARRERAS"] in str(r["CODCARPR_LISTA"]).split(" | ") else "NO"),
            axis=1,
        )

        def classify(row: pd.Series) -> str:
            if row["N_REGISTROS_DATOS"] == 0:
                return "SIN_IDENTIDAD"
            if row["COINCIDE_DV_INSTITUCIONAL"] == "NO":
                return "CONTRADICCION_DOCUMENTO"
            if row["N_CODCLI"] > 1:
                return "MULTIPLES_CODCLI"
            if row["N_CODCARPR"] > 1:
                return "MULTIPLES_TRAYECTORIAS"
            if row["CODCARR_ESPERADO_EN_DATOS"] == "NO":
                return "CONTRADICCION_CARRERA"
            return "IDENTIDAD_EXACTA"

        ident["CLASIFICACION_IDENTIDAD"] = ident.apply(classify, axis=1)
        rut_hist = ident[ident["COINCIDE_DV_INSTITUCIONAL"].eq("NO")].copy()
        multiples_codcli = ident[ident["CLASIFICACION_IDENTIDAD"].eq("MULTIPLES_CODCLI")].copy()
        sin_identidad = ident[ident["CLASIFICACION_IDENTIDAD"].eq("SIN_IDENTIDAD")].copy()
        contrad = ident[ident["CLASIFICACION_IDENTIDAD"].str.startswith("CONTRADICCION")].copy()
        write_tsv(self.prep / "02_IDENTIFICADORES" / "MAPEO_FILA_5809_IDENTIDAD.tsv", ident)
        write_tsv(self.prep / "02_IDENTIFICADORES" / "RUT_ACTUAL_VS_HISTORICO.tsv", rut_hist)
        write_tsv(self.prep / "02_IDENTIFICADORES" / "MULTIPLES_CODCLI.tsv", multiples_codcli)
        write_tsv(self.prep / "02_IDENTIFICADORES" / "CASOS_SIN_IDENTIDAD.tsv", sin_identidad)
        write_tsv(self.prep / "02_IDENTIFICADORES" / "CONTRADICCIONES_IDENTIDAD.tsv", contrad)
        write_xlsx(
            self.prep / "02_IDENTIFICADORES" / "MAPEO_IDENTIDAD_CODCLI.xlsx",
            {
                "RESUMEN": ident["CLASIFICACION_IDENTIDAD"].value_counts().rename_axis("CLASIFICACION").reset_index(name="CASOS"),
                "MAPEO": ident,
                "MULTIPLES_CODCLI": multiples_codcli,
                "SIN_IDENTIDAD": sin_identidad,
                "CONTRADICCIONES": contrad,
            },
        )
        if not contrad.empty:
            write_tsv(self.paths["contradicciones"], contrad[["ID_FILA_5809", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "CLASIFICACION_IDENTIDAD", "CODCLI_LISTA", "CODCARPR_LISTA"]])
            self.validation("M4", "CONTRADICCIONES_IDENTIDAD", "ADVERTENCIA_CONTROLADA", str(len(contrad)))
        self.validation("M4", "MAPEO_IDENTIDAD_GENERADO", "OK", f"{len(ident)} filas")
        self.mark("M4", "COMPLETADA_CON_OBSERVACIONES")
        set_checkpoint(self.prep, "M4", "COMPLETADA_CON_OBSERVACIONES", [self.prep / "02_IDENTIFICADORES" / "MAPEO_IDENTIDAD_CODCLI.xlsx"], "M5")
        return ident

    def m5(self, df: pd.DataFrame) -> pd.DataFrame:
        self.mark("M5", "EN_EJECUCION")
        mapeo = pd.read_csv(self.sources["CONCILIACION_CARRERAS"], sep="\t", dtype=str, keep_default_na=False)
        deps = pd.read_csv(self.sources["PLANES_DISTRIBUCION_NO_DEMOSTRADA"], sep="\t", dtype=str, keep_default_na=False)
        dep_codes = set(deps["CODIGO_UNICO"].astype(str))
        plan_counts = mapeo.groupby("CODIGO_UNICO")["PLAN_ESTUDIOS"].nunique().to_dict()
        plan = df[["ID_FILA_5809", "TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "PLAN_ESTUDIOS"]].merge(
            mapeo[["CODIGO_UNICO", "PLAN_ESTUDIOS", "CODPESTUD_PLAN_INSTITUCIONAL", "CODCARR_PLAN_INSTITUCIONAL"]],
            on=["CODIGO_UNICO", "PLAN_ESTUDIOS"],
            how="left",
        )
        plan["N_PLANES_CONCILIACION_CARRERA"] = plan["CODIGO_UNICO"].map(plan_counts).fillna(0).astype(int)
        plan["DEPENDENCIA_CARRERAS"] = plan["CODIGO_UNICO"].isin(dep_codes).map({True: "SI", False: "NO"})

        def plan_status(row: pd.Series) -> str:
            if not str(row["CODPESTUD_PLAN_INSTITUCIONAL"]).strip():
                return "PLAN_NO_ENCONTRADO"
            if row["N_PLANES_CONCILIACION_CARRERA"] > 1:
                return "PLAN_AMBIGUO"
            if row["DEPENDENCIA_CARRERAS"] == "SI":
                return "PLAN_DEPENDIENTE_CONFIRMACION_PERIODIZACION"
            return "PLAN_IDENTIFICADO_UNICO"

        plan["CLASIFICACION_PLAN"] = plan.apply(plan_status, axis=1)
        write_tsv(self.prep / "04_PLANES" / "PLAN_UNICO.tsv", plan[plan["CODPESTUD_PLAN_INSTITUCIONAL"].astype(str).str.strip().ne("")])
        write_tsv(self.prep / "04_PLANES" / "PLAN_AMBIGUO.tsv", plan[plan["CLASIFICACION_PLAN"].eq("PLAN_AMBIGUO")])
        write_tsv(self.prep / "04_PLANES" / "PLAN_NO_ENCONTRADO.tsv", plan[plan["CLASIFICACION_PLAN"].eq("PLAN_NO_ENCONTRADO")])
        write_tsv(self.prep / "04_PLANES" / "DEPENDENCIAS_CARRERAS.tsv", plan[plan["DEPENDENCIA_CARRERAS"].eq("SI")])
        write_xlsx(
            self.prep / "04_PLANES" / "ASIGNACION_PREPARATORIA_PLAN.xlsx",
            {
                "RESUMEN": plan["CLASIFICACION_PLAN"].value_counts().rename_axis("CLASIFICACION").reset_index(name="CASOS"),
                "ASIGNACION": plan,
                "DEPENDENCIAS_CARRERAS": plan[plan["DEPENDENCIA_CARRERAS"].eq("SI")],
            },
        )
        if plan["CLASIFICACION_PLAN"].isin(["PLAN_NO_ENCONTRADO", "PLAN_AMBIGUO"]).any():
            self.block("M5", "BLOQUEO_PLAN", "Existen planes no encontrados o ambiguos.", "Resolver conciliacion Carreras.")
        self.validation("M5", "PLANES_PREPARATORIOS", "OK", plan["CLASIFICACION_PLAN"].value_counts().to_dict().__repr__())
        self.mark("M5", "COMPLETADA_CON_DEPENDENCIAS")
        set_checkpoint(self.prep, "M5", "COMPLETADA_CON_DEPENDENCIAS", [self.prep / "04_PLANES" / "ASIGNACION_PREPARATORIA_PLAN.xlsx"], "M6")
        return plan

    def m6(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        self.mark("M6", "EN_EJECUCION")
        all29 = pd.read_excel(self.sources["CLASIFICACION_29"], sheet_name="CLASIFICACION_29", dtype=str, keep_default_na=False)
        diag27 = pd.read_csv(self.sources["DIAGNOSTICO_27"], sep="\t", dtype=str, keep_default_na=False)
        inter14 = pd.read_csv(self.sources["DESCOMP_14"], sep="\t", dtype=str, keep_default_na=False)
        weak5 = pd.read_csv(self.sources["DESCOMP_5"], sep="\t", dtype=str, keep_default_na=False)
        direct = all29[all29["ESTADO_ASOCIACION_MODELO"].eq("MODELO_CONFIRMADO_POR_CODCLI")].copy()
        pending = all29[~all29["ESTADO_ASOCIACION_MODELO"].eq("MODELO_CONFIRMADO_POR_CODCLI")].copy()
        expected = {
            "1885": ("20181IECIREOL015", "19", "4"),
            "2050": ("20241TCIB027", "2", "1"),
        }
        direct["ANIO_CURRICULAR_DERIVADO"] = ""
        for idx, row in direct.iterrows():
            exp = expected.get(str(row["ID_FILA_5809"]))
            if not exp or row["CODCLI"] != exp[0] or str(row["NIVEL_EVIDENCIA"]) != exp[1]:
                self.block("M6", "CASO_DIRECTO_NO_COINCIDE", str(row.to_dict()), "Revisar expediente de 29 periodizaciones.")
                raise RuntimeError("Caso directo no coincide con esperado.")
            direct.loc[idx, "ANIO_CURRICULAR_DERIVADO"] = exp[2]
        if len(all29) != 29 or len(direct) != 2 or len(pending) != 27 or len(inter14) != 14 or len(weak5) != 5 or len(diag27[diag27["ESTADO_DIAGNOSTICO_27"].eq("SIN_MODELO_DEMOSTRADO")]) != 8:
            self.block("M6", "CONTEO_PERIODIZACION_NO_REPRODUCIBLE", "No coinciden 29/2/27/14/5/8.", "Revisar artefactos previos.")
            raise RuntimeError("Conteos periodizacion no reproducibles.")
        pending["CLASIFICACION_PREPARATORIA"] = pending["ID_FILA_5809"].map(
            {**{str(v): "FAMILIA_CODCLI_MAS_CARRERA" for v in inter14["ID_FILA_5809"]}, **{str(v): "SOLO_CARRERA" for v in weak5["ID_FILA_5809"]}}
        ).fillna("SIN_MODELO_DEMOSTRADO")
        trace = pd.concat(
            [
                direct.assign(ESTADO_PREPARATORIO="RESUELTO_POR_EVIDENCIA_DIRECTA"),
                pending.assign(ESTADO_PREPARATORIO="PENDIENTE_SIN_CONVERSION"),
            ],
            ignore_index=True,
        )
        write_tsv(self.prep / "05_PERIODIZACIONES" / "CASOS_ADECUADOS_2.tsv", direct)
        write_tsv(self.prep / "05_PERIODIZACIONES" / "CASOS_PENDIENTES_27.tsv", pending)
        write_tsv(self.prep / "05_PERIODIZACIONES" / "TRAZABILIDAD_PERIODIZACIONES.tsv", trace)
        write_xlsx(
            self.prep / "05_PERIODIZACIONES" / "CONSOLIDADO_29_PERIODIZACIONES.xlsx",
            {
                "RESUMEN": pd.DataFrame(
                    [
                        ["TOTAL_29", len(all29)],
                        ["ADECUADOS_DIRECTOS", len(direct)],
                        ["PENDIENTES_27", len(pending)],
                        ["FAMILIA_CODCLI_MAS_CARRERA", int(pending["CLASIFICACION_PREPARATORIA"].eq("FAMILIA_CODCLI_MAS_CARRERA").sum())],
                        ["SOLO_CARRERA", int(pending["CLASIFICACION_PREPARATORIA"].eq("SOLO_CARRERA").sum())],
                        ["SIN_MODELO_DEMOSTRADO", int(pending["CLASIFICACION_PREPARATORIA"].eq("SIN_MODELO_DEMOSTRADO").sum())],
                    ],
                    columns=["INDICADOR", "VALOR"],
                ),
                "ADECUADOS_2": direct,
                "PENDIENTES_27": pending,
                "TRAZABILIDAD": trace,
            },
        )
        self.validation("M6", "PERIODIZACIONES_29_REPRODUCIDAS", "OK", "2 directos; 27 pendientes; 14/5/8 verificados")
        self.mark("M6", "COMPLETADA")
        set_checkpoint(self.prep, "M6", "COMPLETADA", [self.prep / "05_PERIODIZACIONES" / "CONSOLIDADO_29_PERIODIZACIONES.xlsx"], "M7")
        return direct, pending

    def m7(self, df: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
        self.mark("M7", "EN_EJECUCION")
        total = len(df)
        rows = []
        for field in MODIFICABLES:
            complete = int(df[field].astype(str).str.strip().ne("").sum()) if field in df.columns else 0
            if field == "PLAN_ESTUDIOS":
                source_available = "Precarga 5809 + conciliacion Carreras 43/0"
                source_missing = "Confirmacion distribucion anual de Carreras para cierre final"
                dependency = "BLOQUEO_DEPENDENCIA_CARRERAS"
                possibility = "SOLO_PREPARATORIO"
            elif field == "VIGENCIA":
                source_available = "Instructivo oficial: mantener 1 para universo correspondiente"
                source_missing = "Expediente si algun registro requiere VIGENCIA=0"
                dependency = "NO"
                possibility = "COMPLETABLE_PREPARATORIO_NO_MATERIALIZADO"
            else:
                source_available = "PROMEDIOS Hoja1/DatosAlumnos disponible para diagnostico"
                source_missing = "Regla operacional demostrada por carrera/plan para presencia y unidades 2025/acumuladas; confirmacion de Carreras"
                dependency = "BLOQUEO_DEPENDENCIA_CARRERAS;BLOQUEO_FUENTE_AVANCE"
                possibility = "NO_COMPLETAR_SIN_EVIDENCIA"
            rows.append(
                {
                    "CAMPO": field,
                    "FUENTE_DISPONIBLE": source_available,
                    "FUENTE_FALTANTE": source_missing,
                    "COMPLETOS_ACTUALES": complete,
                    "PENDIENTES_ACTUALES": total - complete,
                    "PORCENTAJE_COMPLETO": round(complete / total * 100, 2),
                    "PORCENTAJE_PENDIENTE": round((total - complete) / total * 100, 2),
                    "REGLA_OFICIAL": "Instructivo Anexo II",
                    "DEPENDENCIA_CARRERAS": dependency,
                    "POSIBILIDAD_COMPLETAR": possibility,
                    "BLOQUEO": "NO" if field == "VIGENCIA" else "SI",
                }
            )
        matrix = pd.DataFrame(rows)
        write_tsv(self.prep / "06_CAMPOS_MODIFICABLES" / "FUENTES_POR_CAMPO.tsv", matrix)
        write_tsv(self.prep / "06_CAMPOS_MODIFICABLES" / "CAMPOS_BLOQUEADOS.tsv", matrix[matrix["BLOQUEO"].eq("SI")])
        write_tsv(self.prep / "06_CAMPOS_MODIFICABLES" / "CAMPOS_COMPLETABLES.tsv", matrix[matrix["BLOQUEO"].eq("NO")])
        write_xlsx(self.prep / "06_CAMPOS_MODIFICABLES" / "MATRIZ_COMPLETITUD_CAMPOS.xlsx", {"MATRIZ": matrix})
        self.validation("M7", "MATRIZ_CAMPOS_MODIFICABLES", "OK", f"{len(matrix)} campos")
        self.mark("M7", "COMPLETADA_CON_DEPENDENCIAS")
        set_checkpoint(self.prep, "M7", "COMPLETADA_CON_DEPENDENCIAS", [self.prep / "06_CAMPOS_MODIFICABLES" / "MATRIZ_COMPLETITUD_CAMPOS.xlsx"], "M8")
        return matrix

    def m8(self, df: pd.DataFrame, ident: pd.DataFrame, plan: pd.DataFrame, pending27: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        self.mark("M8", "EN_EJECUCION")
        errors = []
        warnings = []
        deps = [
            {"VALIDACION_NO_EJECUTADA": "TOLERANCIA_FINAL_PLAN", "MOTIVO": "Depende de Carreras final y distribucion anual confirmada."},
            {"VALIDACION_NO_EJECUTADA": "INTEGRIDAD_FINAL_CARRERAS_MATRICULA", "MOTIVO": "No existe candidato final Carreras."},
            {"VALIDACION_NO_EJECUTADA": "GENERACION_FISICA_CSV", "MOTIVO": "Prohibida en esta etapa preparatoria."},
            {"VALIDACION_NO_EJECUTADA": "VALIDACION_UNIDADES_POR_ANIO", "MOTIVO": "Distribucion anual de 15 planes no confirmada."},
        ]
        if len(df) != 2371:
            errors.append({"ERROR": "UNIVERSO_CAMBIO", "DETALLE": len(df)})
        if plan["CLASIFICACION_PLAN"].eq("PLAN_NO_ENCONTRADO").any():
            errors.append({"ERROR": "PLAN_NO_ENCONTRADO", "DETALLE": int(plan["CLASIFICACION_PLAN"].eq("PLAN_NO_ENCONTRADO").sum())})
        if len(pending27) != 27:
            errors.append({"ERROR": "PENDIENTES_27_CAMBIO", "DETALLE": len(pending27)})
        if ident["CLASIFICACION_IDENTIDAD"].isin(["SIN_IDENTIDAD", "MULTIPLES_CODCLI", "MULTIPLES_TRAYECTORIAS", "CONTRADICCION_DOCUMENTO", "CONTRADICCION_CARRERA"]).any():
            warnings.append(
                {
                    "ADVERTENCIA": "IDENTIDAD_REQUIERE_REVISION",
                    "DETALLE": ident["CLASIFICACION_IDENTIDAD"].value_counts().to_dict().__repr__(),
                }
            )
        if plan["DEPENDENCIA_CARRERAS"].eq("SI").any():
            warnings.append({"ADVERTENCIA": "DEPENDENCIA_CARRERAS", "DETALLE": int(plan["DEPENDENCIA_CARRERAS"].eq("SI").sum())})
        err_df = pd.DataFrame(errors, columns=["ERROR", "DETALLE"])
        warn_df = pd.DataFrame(warnings, columns=["ADVERTENCIA", "DETALLE"])
        dep_df = pd.DataFrame(deps)
        validations = pd.DataFrame(
            [
                ["UNIVERSO_CONSERVADO", "OK" if len(df) == 2371 else "ERROR", len(df)],
                ["NO_MODIFICABLES_BASELINE_EXISTE", "OK", "Generado M3"],
                ["IDENTIDAD_DIAGNOSTICADA", "OK", len(ident)],
                ["PLAN_PREPARATORIO_DIAGNOSTICADO", "OK", len(plan)],
                ["PERIODIZACIONES_2_Y_27", "OK" if len(pending27) == 27 else "ERROR", len(pending27)],
            ],
            columns=["VALIDACION", "ESTADO", "DETALLE"],
        )
        write_tsv(self.prep / "07_VALIDACIONES" / "ERRORES_CRITICOS_PREPARATORIOS.tsv", err_df)
        write_tsv(self.prep / "07_VALIDACIONES" / "ADVERTENCIAS_PREPARATORIAS.tsv", warn_df)
        write_tsv(self.prep / "07_VALIDACIONES" / "DEPENDENCIAS_NO_EJECUTADAS.tsv", dep_df)
        write_xlsx(
            self.prep / "07_VALIDACIONES" / "VALIDACIONES_PREPARATORIAS_MATRICULA.xlsx",
            {
                "VALIDACIONES": validations,
                "ERRORES": err_df,
                "ADVERTENCIAS": warn_df,
                "DEPENDENCIAS_NO_EJECUTADAS": dep_df,
            },
        )
        self.validation("M8", "VALIDACIONES_PREPARATORIAS", "OK" if err_df.empty else "ERROR", f"errores={len(err_df)} advertencias={len(warn_df)}")
        if not err_df.empty:
            raise RuntimeError("Errores criticos preparatorios.")
        self.mark("M8", "COMPLETADA_CON_OBSERVACIONES")
        set_checkpoint(self.prep, "M8", "COMPLETADA_CON_OBSERVACIONES", [self.prep / "07_VALIDACIONES" / "VALIDACIONES_PREPARATORIAS_MATRICULA.xlsx"], "M9")
        return err_df, warn_df, dep_df

    def m9(self, df: pd.DataFrame, ident: pd.DataFrame, plan: pd.DataFrame, pending27: pd.DataFrame) -> pd.DataFrame:
        self.mark("M9", "EN_EJECUCION")
        blocks = []
        info = df[["ID_FILA_5809", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "PLAN_ESTUDIOS"]].copy()
        id_by_row = ident.set_index("ID_FILA_5809").to_dict(orient="index")
        plan_by_row = plan.set_index("ID_FILA_5809").to_dict(orient="index")
        for _, row in info.iterrows():
            rid = row["ID_FILA_5809"]
            ident_row = id_by_row.get(rid, {})
            plan_row = plan_by_row.get(rid, {})
            if plan_row.get("DEPENDENCIA_CARRERAS") == "SI":
                blocks.append(
                    {
                        "TIPO": "BLOQUEO_DEPENDENCIA_CARRERAS",
                        "ID_FILA_5809": rid,
                        "CAMPO_AFECTADO": "PLAN_ESTUDIOS;UNIDADES_*",
                        "MOTIVO": "Plan identificado pero distribucion anual de Carreras pendiente.",
                        "FUENTE_FALTANTE": "Confirmacion institucional/documental de periodizacion Carreras.",
                        "DEPENDENCIA": "FASE_4B_CARRERAS",
                    }
                )
            if str(ident_row.get("CLASIFICACION_IDENTIDAD", "")) in {"SIN_IDENTIDAD", "MULTIPLES_CODCLI", "CONTRADICCION_DOCUMENTO", "CONTRADICCION_CARRERA"}:
                blocks.append(
                    {
                        "TIPO": "BLOQUEO_IDENTIDAD",
                        "ID_FILA_5809": rid,
                        "CAMPO_AFECTADO": "IDENTIDAD_CODCLI",
                        "MOTIVO": str(ident_row.get("CLASIFICACION_IDENTIDAD", "")),
                        "FUENTE_FALTANTE": "Validacion institucional de identidad/CODCLI.",
                        "DEPENDENCIA": "M4_IDENTIDAD",
                    }
                )
            blocks.append(
                {
                    "TIPO": "BLOQUEO_FUENTE_AVANCE",
                    "ID_FILA_5809": rid,
                    "CAMPO_AFECTADO": "CURSO_1ER_SEM;CURSO_2DO_SEM;UNIDADES_CURSADAS;UNIDADES_APROBADAS;UNID_CURSADAS_TOTAL;UNID_APROBADAS_TOTAL",
                    "MOTIVO": "Campos obligatorios no completados en etapa preparatoria.",
                    "FUENTE_FALTANTE": "Regla operacional validada de presencia, unidades 2025 y acumulados por plan.",
                    "DEPENDENCIA": "M12_MATRICULA_POST_CARRERAS",
                }
            )
        for _, row in pending27.iterrows():
            blocks.append(
                {
                    "TIPO": "BLOQUEO_PERIODIZACION",
                    "ID_FILA_5809": row["ID_FILA_5809"],
                    "CAMPO_AFECTADO": "ANIO_CURRICULAR_DERIVADO_EVIDENCIA",
                    "MOTIVO": "Caso de los 27 pendientes no convertible sin reporte individual/tabla institucional.",
                    "FUENTE_FALTANTE": "Avance de Malla individual o tabla institucional de periodizacion.",
                    "DEPENDENCIA": "M6_PERIODIZACION",
                }
            )
        bdf = pd.DataFrame(blocks)
        bdf.insert(0, "ID_BLOQUEO", [f"BM{i:06d}" for i in range(1, len(bdf) + 1)])
        bdf = bdf.merge(info, on="ID_FILA_5809", how="left")
        bdf["DOCUMENTO"] = bdf["NUM_DOCUMENTO"].fillna("") + "-" + bdf["DV"].fillna("")
        bdf["CODCLI"] = bdf["ID_FILA_5809"].map(lambda x: id_by_row.get(x, {}).get("CODCLI_LISTA", ""))
        bdf["PLAN"] = bdf["PLAN_ESTUDIOS"]
        bdf["FUENTE_DISPONIBLE"] = "Precarga 5809; PROMEDIOS; conciliaciones previas"
        bdf["ACCION_REQUERIDA"] = bdf["FUENTE_FALTANTE"].map(lambda s: "Aportar " + str(s).lower())
        bdf["ESTADO"] = "PENDIENTE"
        bdf["FASE_QUE_DESBLOQUEA"] = bdf["DEPENDENCIA"]
        bdf["IMPACTO_EN_CARGA"] = "Impide archivo final de Matricula o validacion final."
        cols = [
            "ID_BLOQUEO",
            "TIPO",
            "ID_FILA_5809",
            "DOCUMENTO",
            "CODCLI",
            "CODIGO_UNICO",
            "PLAN",
            "CAMPO_AFECTADO",
            "MOTIVO",
            "FUENTE_DISPONIBLE",
            "FUENTE_FALTANTE",
            "DEPENDENCIA",
            "ACCION_REQUERIDA",
            "ESTADO",
            "FASE_QUE_DESBLOQUEA",
            "IMPACTO_EN_CARGA",
        ]
        bdf = bdf[cols]
        resumen = bdf.groupby("TIPO", dropna=False).size().reset_index(name="CASOS")
        write_tsv(self.prep / "08_AUDITORIA" / "BLOQUEOS_MATRICULA.tsv", bdf)
        write_tsv(self.prep / "08_AUDITORIA" / "RESUMEN_BLOQUEOS.tsv", resumen)
        write_xlsx(self.prep / "08_AUDITORIA" / "EXPEDIENTE_BLOQUEOS_MATRICULA.xlsx", {"RESUMEN": resumen, "BLOQUEOS": bdf})
        self.validation("M9", "EXPEDIENTE_BLOQUEOS", "OK", f"{len(bdf)} bloqueos registrados")
        self.mark("M9", "COMPLETADA_CON_DEPENDENCIAS")
        set_checkpoint(self.prep, "M9", "COMPLETADA_CON_DEPENDENCIAS", [self.prep / "08_AUDITORIA" / "EXPEDIENTE_BLOQUEOS_MATRICULA.xlsx"], "M10")
        return bdf

    def m10(self, df: pd.DataFrame, ident: pd.DataFrame, plan: pd.DataFrame, direct: pd.DataFrame, pending: pd.DataFrame, blocks: pd.DataFrame) -> None:
        self.mark("M10", "EN_EJECUCION")
        outputs = []
        for sub in SUBDIRS:
            for path in (self.prep / sub).rglob("*"):
                if path.is_file():
                    outputs.append({"RUTA": str(path), "SHA256": sha256(path), "TAMANO_BYTES": path.stat().st_size})
        outputs_df = pd.DataFrame(outputs)
        write_json(self.paths["manifest_salidas"], {"fecha": now_iso(), "salidas": outputs})
        resumen = pd.DataFrame(
            [
                ["ESTADO_FINAL", "PREPARACION_MATRICULA_COMPLETADA_CON_DEPENDENCIAS"],
                ["UNIVERSO_5809", len(df)],
                ["IDENTIDAD_RESUMEN", ident["CLASIFICACION_IDENTIDAD"].value_counts().to_dict().__repr__()],
                ["PLAN_RESUMEN", plan["CLASIFICACION_PLAN"].value_counts().to_dict().__repr__()],
                ["CASOS_ADECUADOS", len(direct)],
                ["CASOS_PENDIENTES_PERIODIZACION", len(pending)],
                ["BLOQUEOS_REGISTRADOS", len(blocks)],
                ["CSV_CARGA_GENERADO", "NO"],
                ["SIES_READY", "NO"],
            ],
            columns=["INDICADOR", "VALOR"],
        )
        report = [
            "# Informe Preparacion Matricula Avance Curricular SIES 2026",
            "",
            "Estado final: PREPARACION_MATRICULA_COMPLETADA_CON_DEPENDENCIAS",
            "",
            f"Carpeta: `{self.prep}`",
            f"Universo 5809: {len(df)} filas.",
            "",
            "## Resultados principales",
            "",
            f"- Identidad: {ident['CLASIFICACION_IDENTIDAD'].value_counts().to_dict()}",
            f"- Plan preparatorio: {plan['CLASIFICACION_PLAN'].value_counts().to_dict()}",
            f"- Casos adecuados: {len(direct)} (ID 1885 y 2050).",
            f"- Casos pendientes de periodizacion: {len(pending)}.",
            f"- Bloqueos registrados: {len(blocks)}.",
            "",
            "## Restricciones respetadas",
            "",
            "- No se reanudo construccion final de Carreras.",
            "- No se genero archivo final de Matricula.",
            "- No se genero CSV de carga.",
            "- No se marco ningun archivo como SIES_READY.",
            "- No se ejecuto carga PES.",
            "",
            "## Dependencias",
            "",
            "- Confirmacion institucional/documental de distribucion anual de Carreras.",
            "- Regla operacional validada para presencia y unidades 2025/acumuladas.",
            "- Reporte individual o tabla institucional para los 27 casos pendientes de periodizacion.",
            "",
            "## Artefactos",
            "",
            f"- Manifest salidas: `{self.paths['manifest_salidas']}`",
            f"- Expediente bloqueos: `{self.prep / '08_AUDITORIA' / 'EXPEDIENTE_BLOQUEOS_MATRICULA.xlsx'}`",
            f"- Validaciones: `{self.prep / '07_VALIDACIONES' / 'VALIDACIONES_PREPARATORIAS_MATRICULA.xlsx'}`",
        ]
        (self.prep / "09_REPORTES" / "INFORME_PREPARACION_MATRICULA.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        write_xlsx(
            self.prep / "09_REPORTES" / "INFORME_PREPARACION_MATRICULA.xlsx",
            {
                "RESUMEN": resumen,
                "SALIDAS": outputs_df,
                "BLOQUEOS_RESUMEN": blocks.groupby("TIPO").size().reset_index(name="CASOS"),
            },
        )
        self.mark("M10", "PREPARACION_MATRICULA_COMPLETADA_CON_DEPENDENCIAS")
        set_checkpoint(
            self.prep,
            "M10",
            "PREPARACION_MATRICULA_COMPLETADA_CON_DEPENDENCIAS",
            [self.prep / "09_REPORTES" / "INFORME_PREPARACION_MATRICULA.md", self.prep / "09_REPORTES" / "INFORME_PREPARACION_MATRICULA.xlsx"],
            "M10",
        )

    def run(self) -> None:
        self.m0()
        prof = self.m1()
        df = self.m2(prof)
        self.m3(df)
        ident = self.m4(df)
        plan = self.m5(df)
        direct, pending = self.m6()
        self.m7(df, plan)
        self.m8(df, ident, plan, pending)
        blocks = self.m9(df, ident, plan, pending)
        self.m10(df, ident, plan, direct, pending, blocks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-dir", type=Path, default=EXEC_DEFAULT)
    parser.add_argument("--prep-dir", type=Path)
    parser.add_argument("--desde-fase", default="M0")
    args = parser.parse_args()
    prep = init_prep(args.execution_dir.resolve(), args.prep_dir)
    runner = PrepRunner(args.execution_dir.resolve(), prep)
    runner.run()
    print(f"PREPARACION_MATRICULA_COMPLETADA_CON_DEPENDENCIAS")
    print(f"Carpeta: {prep}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
