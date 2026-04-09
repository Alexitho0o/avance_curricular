#!/usr/bin/env python3
"""Build governed column-by-column artifacts for SIES 5809 Avance Curricular 2026.

This script is intentionally conservative: it documents rules, sources, joins,
validations, decisions and blockers. It does not create SIES_READY files and it
does not alter frozen sources.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


TZ = ZoneInfo("America/Santiago")
BASE = Path("/Users/alexi/Documents/GitHub/avance_curricular")
ROOT_OUT = BASE / "avance_curricular_2026" / "06_gobernanza_columnas_5809"
FUENTES = BASE / "avance_curricular_2026" / "00_fuentes_congeladas" / "CARGA_CONGELADA_20260626_005826" / "originales"

INSTRUCTIVO = FUENTES / "Instructivo_Avance Curricular SIES - 2026.txt"
PRECARGA_5810 = FUENTES / "5810_Precarga Carreras Avance Curricular 20268.csv"
PROMEDIOS = FUENTES / "PROMEDIOSDEALUMNOS_7804.xlsx"
PLANES = BASE / "avance_curricular_2026" / "01_fuentes_institucionales" / "planes_estudio" / "Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx"

CIERRE = BASE / "avance_curricular_2026" / "05_cierre_integral" / "CIERRE_AVANCE_CURRICULAR_20260703_125157"
PREP = CIERRE / "04_CONCILIACION_MATRICULA" / "PREPARACION_MATRICULA_20260703_141254"
DIAG = CIERRE / "05_RESOLUCION_PENDIENTES" / "DIAGNOSTICO_FUENTES_AVANCE_20260703_142658"

GOB_29_DIR = BASE / "avance_curricular_2026" / "04_gobernanza_mallas" / "03_auditorias"
EXP_29 = GOB_29_DIR / "EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS_20260703_222737" / "02_RESULTADOS" / "EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS.xlsx"
INF_29 = GOB_29_DIR / "EXPEDIENTE_DETALLADO_GOBERNANZA_29_CASOS_20260703_222737" / "02_RESULTADOS" / "INFORME_EJECUTIVO_GOBERNANZA_DETALLADA_29.md"
MATRIZ_29 = GOB_29_DIR / "PREPARACION_ARCHIVO_SIES_DESDE_GOBERNANZA_29_20260703_223721" / "02_RESULTADOS" / "MATRIZ_PROBLEMA_SOLUCION_PREPARACION_SIES_29.xlsx"
APLICACION_29 = GOB_29_DIR / "APLICACION_GOBERNANZA_29_SOBRE_5809_20260703_223944" / "02_RESULTADOS" / "APLICACION_GOBERNANZA_29_SOBRE_5809_PREPARACION.xlsx"
CAMPO_DESTINO = GOB_29_DIR / "IDENTIFICACION_CAMPO_DESTINO_5809_GOBERNANZA_20260703_224234" / "02_RESULTADOS" / "IDENTIFICACION_CAMPO_DESTINO_5809_GOBERNANZA.xlsx"
LECTURA_5809 = GOB_29_DIR / "LECTURA_ENCABEZADO_Y_FILAS_5809_20260703_224524" / "LECTURA_ENCABEZADO_Y_FILAS_5809.xlsx"

IDENTIDAD = PREP / "02_IDENTIFICADORES" / "MAPEO_FILA_5809_IDENTIDAD.tsv"
PLAN_UNICO = PREP / "04_PLANES" / "PLAN_UNICO.tsv"
PLAN_AMBIGUO = PREP / "04_PLANES" / "PLAN_AMBIGUO.tsv"
PLAN_NO_ENCONTRADO = PREP / "04_PLANES" / "PLAN_NO_ENCONTRADO.tsv"
DEPENDENCIAS_CARRERAS = PREP / "04_PLANES" / "DEPENDENCIAS_CARRERAS.tsv"
PREP_INFORME = PREP / "09_REPORTES" / "INFORME_PREPARACION_MATRICULA.md"
DIAG_INFORME = DIAG / "10_REPORTES" / "INFORME_DIAGNOSTICO_FUENTES_AVANCE.md"
DIAG_BRECHAS = DIAG / "07_BRECHAS" / "EXPEDIENTE_BRECHAS_COMPLETO.xlsx"

ORDERED_COLUMNS = [
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

BLOCKS = {
    "01": ORDERED_COLUMNS[0:5],
    "02": ORDERED_COLUMNS[5:10],
    "03": ORDERED_COLUMNS[10:15],
    "04": ORDERED_COLUMNS[15:17],
    "05": ORDERED_COLUMNS[17:19],
    "06": ORDERED_COLUMNS[19:21],
    "07": ORDERED_COLUMNS[21:22],
}

NO_MODIFICABLES = {
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
}

FIELD_RULES: dict[str, dict[str, str]] = {
    "CODIGO_IES_NUM": {
        "definicion": "Codigo de la institucion; dato precargado no modificable.",
        "regla": "Dato precargado no modificable; editarlo genera error por atributo no modificable.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "Debe mantenerse identico a la precarga.",
    },
    "TIPO_DOCUMENTO": {
        "definicion": "Tipo de documento del estudiante.",
        "regla": "Valores permitidos: R: RUT y P: Pasaporte. Dato precargado no modificable.",
        "fuente": "Precarga 5809; contraste identidad/CODCLI solo para auditoria.",
        "llave": "NUM_DOCUMENTO + DV",
        "validacion": "R/P; si R debe existir DV; si P no debe completarse DV.",
    },
    "NUM_DOCUMENTO": {
        "definicion": "Numero de documento informado en la precarga.",
        "regla": "Dato precargado no modificable; para RUT no puede contener letras.",
        "fuente": "Precarga 5809; DatosAlumnos para auditoria.",
        "llave": "NUM_DOCUMENTO + DV",
        "validacion": "No modificar; documentar contradicciones.",
    },
    "DV": {
        "definicion": "Digito verificador cuando TIPO_DOCUMENTO es R.",
        "regla": "Si tipo R, completar DV; si tipo P, no completar. DV numerico o K.",
        "fuente": "Precarga 5809; DatosAlumnos para auditoria.",
        "llave": "NUM_DOCUMENTO + DV",
        "validacion": "Formato y consistencia documental.",
    },
    "PRIMER_APELLIDO": {
        "definicion": "Primer apellido del estudiante.",
        "regla": "Dato precargado no modificable; valores permitidos con letras mayusculas y caracteres aceptados.",
        "fuente": "Precarga 5809; DatosAlumnos solo auditoria.",
        "llave": "Documento, no nombre.",
        "validacion": "No usar como llave principal ni corregir por supuesto.",
    },
    "SEGUNDO_APELLIDO": {
        "definicion": "Segundo apellido del estudiante.",
        "regla": "Dato precargado no modificable; valores permitidos con letras mayusculas y caracteres aceptados.",
        "fuente": "Precarga 5809; DatosAlumnos solo auditoria.",
        "llave": "Documento, no nombre.",
        "validacion": "Diferencia de apellido se documenta, no se corrige automaticamente.",
    },
    "NOMBRES": {
        "definicion": "Nombres del estudiante.",
        "regla": "Dato precargado no modificable; valores permitidos con letras mayusculas y caracteres aceptados.",
        "fuente": "Precarga 5809; DatosAlumnos solo auditoria.",
        "llave": "Documento, no nombre.",
        "validacion": "No usar nombre como llave principal.",
    },
    "SEXO": {
        "definicion": "Sexo informado.",
        "regla": "Valores permitidos: H, M, X. Dato precargado no modificable.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "H/M/X; cambios requieren canal institucional, no este proceso.",
    },
    "FECHA_NACIMIENTO": {
        "definicion": "Fecha de nacimiento del estudiante.",
        "regla": "Dato precargado no modificable; error si inconsistente con edad minima.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "Formato fecha y edad razonable; no corregir por supuesto.",
    },
    "CODIGO_UNICO": {
        "definicion": "Codigo unico de la carrera que esta estudiando.",
        "regla": "Dato precargado no modificable; debe existir en Carreras 5810.",
        "fuente": "Precarga 5809; Precarga Carreras 5810.",
        "llave": "CODIGO_UNICO",
        "validacion": "CODIGO_UNICO debe existir en 5810.",
    },
    "PLAN_ESTUDIOS": {
        "definicion": "Correlativo del plan de estudios en que esta matriculado el estudiante.",
        "regla": "Usar numeros de plan informados en Carreras para el CODIGO_UNICO; obligatorio.",
        "fuente": "Carreras 5810, conciliacion planes, fuente planes institucional.",
        "llave": "CODIGO_UNICO + PLAN_ESTUDIOS",
        "validacion": "La combinacion debe existir en carga Carreras; bloqueado por planes sin semantica confirmada.",
    },
    "ANIO_INGRESO_CARRERA_ACTUAL": {
        "definicion": "Ano de ingreso a la carrera actual.",
        "regla": "Dato precargado no modificable; no puede ser mayor a 2025.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "No usar como destino de anio curricular adecuado.",
    },
    "SEM_INGRESO_CARRERA_ACTUAL": {
        "definicion": "Semestre de ingreso a la carrera actual.",
        "regla": "Dato precargado no modificable; valores 1 o 2.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "Valores 1/2.",
    },
    "ANIO_INGRESO_CARRERA_ORIGEN": {
        "definicion": "Ano de ingreso a la carrera de origen o primer ano.",
        "regla": "Dato precargado no modificable; no puede ser mayor a 2025.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "No usar como destino de anio curricular adecuado; origen no mayor que actual.",
    },
    "SEM_INGRESO_CARRERA_ORIGEN": {
        "definicion": "Semestre de ingreso a la carrera de origen o primer ano.",
        "regla": "Dato precargado no modificable; valores 1 o 2.",
        "fuente": "Precarga 5809",
        "llave": "Registro 5809",
        "validacion": "Valores 1/2.",
    },
    "CURSO_1ER_SEM": {
        "definicion": "Indica si curso actividades academicas exigidas en el plan durante el primer semestre de 2025.",
        "regla": "Valores SI/NO; obligatorio; si SI, UNIDADES_CURSADAS debe ser mayor a 0.",
        "fuente": "Fuente academica 2025 por estudiante/carrera/plan/periodo.",
        "llave": "Documento -> CODCLI -> carrera/plan -> periodo 2025-1.",
        "validacion": "No convertir niveles historicos sin reporte individual o regla demostrada.",
    },
    "CURSO_2DO_SEM": {
        "definicion": "Indica si curso actividades academicas exigidas en el plan durante el segundo semestre de 2025.",
        "regla": "Valores SI/NO; obligatorio; si SI, UNIDADES_CURSADAS debe ser mayor a 0.",
        "fuente": "Fuente academica 2025 por estudiante/carrera/plan/periodo.",
        "llave": "Documento -> CODCLI -> carrera/plan -> periodo 2025-2.",
        "validacion": "Si ambos semestres son NO, UNIDADES_CURSADAS debe ser 0.",
    },
    "UNIDADES_CURSADAS": {
        "definicion": "Unidades de medida cursadas efectivamente durante 2025 y pertenecientes al plan informado.",
        "regla": "Usar solo numeros; no incluir validacion de estudios ni reconocimiento de aprendizajes previos; obligatorio.",
        "fuente": "Fuente academica 2025 con estados de actividad/asignatura.",
        "llave": "CODCLI + carrera/plan + anio 2025 + unidad academica.",
        "validacion": "No negativos; anual, no acumulado; si curso SI debe ser mayor a 0.",
    },
    "UNIDADES_APROBADAS": {
        "definicion": "Unidades de medida aprobadas efectivamente durante 2025 y pertenecientes al plan informado.",
        "regla": "Usar solo numeros; no incluir validacion de estudios ni reconocimiento de aprendizajes previos; obligatorio.",
        "fuente": "Fuente academica 2025 con estados aprobatorios.",
        "llave": "CODCLI + carrera/plan + anio 2025 + unidad academica.",
        "validacion": "UNIDADES_APROBADAS <= UNIDADES_CURSADAS; anual, no acumulado.",
    },
    "UNID_CURSADAS_TOTAL": {
        "definicion": "Unidades cursadas desde ingreso a la carrera hasta fin de 2025.",
        "regla": "Usar solo numeros; incluir validacion de estudios o reconocimiento de aprendizajes previos; obligatorio.",
        "fuente": "Historico academico acumulado + fuente 2025 + plan/malla.",
        "llave": "CODCLI + carrera/plan + historia academica hasta 2025.",
        "validacion": "Acumulado coherente con anual; no mezclar sin trazabilidad.",
    },
    "UNID_APROBADAS_TOTAL": {
        "definicion": "Unidades aprobadas desde ingreso a la carrera hasta fin de 2025.",
        "regla": "Usar solo numeros; incluir validacion/reconocimiento; limite de referencia: total plan con tolerancia 25%.",
        "fuente": "Historico academico acumulado + fuente 2025 + plan/malla.",
        "llave": "CODCLI + carrera/plan + historia academica hasta 2025.",
        "validacion": "UNID_APROBADAS_TOTAL <= UNID_CURSADAS_TOTAL y no exceder plan+tolerancia sin evidencia.",
    },
    "VIGENCIA": {
        "definicion": "Variable para mantener o eliminar un registro cargado.",
        "regla": "Valores permitidos 0 eliminar, 1 mantener; obligatorio; no mezclar con otros procesos.",
        "fuente": "Instructivo oficial y precarga 5809.",
        "llave": "Registro 5809",
        "validacion": "Solo 0/1; no derivar de Matricula Unificada ni otros procesos.",
    },
}


@dataclass
class Paths:
    run: Path
    control: Path
    audit: Path


def now_stamp() -> str:
    return datetime.now(TZ).strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False, encoding="utf-8", lineterminator="\n")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            sheet = name[:31] or "Hoja"
            df.to_excel(writer, sheet_name=sheet, index=False)


def read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def find_5809() -> Path:
    matches = sorted(FUENTES.glob("5809_Precarga*2026.csv"))
    if not matches:
        raise FileNotFoundError("No se encontro la precarga 5809 congelada.")
    return matches[0]


def read_precarga(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="latin-1", dtype=str, keep_default_na=False)


def split_rut(value: str) -> tuple[str, str]:
    text = "".join(ch for ch in str(value).upper().strip() if ch.isalnum())
    if len(text) <= 1:
        return text, ""
    return text[:-1], text[-1]


class Gobernanza5809:
    def __init__(self, paths: Paths, source_5809: Path) -> None:
        self.paths = paths
        self.source_5809 = source_5809
        self.control_rows: list[dict[str, Any]] = []
        self.generated: list[Path] = []
        self.df5809 = read_precarga(source_5809)
        self.df5810 = read_precarga(PRECARGA_5810)
        self.identity = read_tsv(IDENTIDAD)
        self.plan_unico = read_tsv(PLAN_UNICO)
        self.plan_ambiguo = read_tsv(PLAN_AMBIGUO)
        self.plan_no = read_tsv(PLAN_NO_ENCONTRADO)
        self.dep_carreras = read_tsv(DEPENDENCIAS_CARRERAS)
        self.dictionary = pd.DataFrame()
        self.block_logics: list[pd.DataFrame] = []
        self.master = pd.DataFrame()

    def register(self, *paths: Path) -> None:
        for path in paths:
            self.generated.append(path)

    def control(
        self,
        fase: str,
        estado: str,
        archivos_usados: list[Path],
        archivos_generados: list[Path],
        registros: int,
        errores: int,
        bloqueos: int,
        proxima: str,
        detalle: str = "",
    ) -> None:
        self.control_rows.append(
            {
                "FECHA": now_iso(),
                "PROCESO": "Avance Curricular SIES 2026",
                "SUBPROYECTO": "Matricula 5809",
                "ANIO_PROCESO": "2026",
                "ANIO_DATOS": "2025",
                "FUENTE_OFICIAL": str(INSTRUCTIVO),
                "FASE": fase,
                "ARCHIVOS_USADOS": " | ".join(str(p) for p in archivos_usados),
                "ARCHIVOS_GENERADOS": " | ".join(str(p) for p in archivos_generados),
                "FUENTES_ORIGINALES_MODIFICADAS": "NO",
                "CSV_CARGA_GENERADO": "NO",
                "SIES_READY_GENERADO": "NO",
                "REGISTROS_ANALIZADOS": registros,
                "ERRORES_CRITICOS": errores,
                "BLOQUEOS": bloqueos,
                "ESTADO_FASE": estado,
                "PROXIMA_FASE_RECOMENDADA": proxima,
                "DETALLE": detalle,
            }
        )
        write_tsv(self.paths.control / "CONTROL_FASES.tsv", pd.DataFrame(self.control_rows))

    def source_inventory(self) -> list[dict[str, Any]]:
        items = [
            ("FUENTE_OFICIAL", INSTRUCTIVO, "Regla oficial SIES"),
            ("PRECARGA_5809", self.source_5809, "Base estructural Matricula"),
            ("PRECARGA_5810", PRECARGA_5810, "Base estructural Carreras"),
            ("FUENTE_PERSONAS_ACADEMICA", PROMEDIOS, "DatosAlumnos / avance parcial"),
            ("FUENTE_PLANES", PLANES, "Planes/malla institucional"),
            ("GOBERNANZA_29_EXCEL", EXP_29, "Gobernanza detallada 29 casos"),
            ("GOBERNANZA_29_INFORME", INF_29, "Informe ejecutivo 29 casos"),
            ("MATRIZ_29", MATRIZ_29, "Matriz problema/solucion"),
            ("APLICACION_29_5809", APLICACION_29, "Aplicacion 29 sobre 5809"),
            ("CAMPO_DESTINO", CAMPO_DESTINO, "Identificacion campo destino"),
            ("LECTURA_5809", LECTURA_5809, "Lectura encabezado/filas 1885 y 2050"),
            ("IDENTIDAD_PREP", IDENTIDAD, "Mapeo identidad CODCLI"),
            ("PLAN_UNICO", PLAN_UNICO, "Planes unicos preparatorios"),
            ("PLAN_AMBIGUO", PLAN_AMBIGUO, "Planes ambiguos preparatorios"),
            ("PLAN_NO_ENCONTRADO", PLAN_NO_ENCONTRADO, "Planes no encontrados preparatorios"),
            ("DEPENDENCIAS_CARRERAS", DEPENDENCIAS_CARRERAS, "Dependencias Carreras"),
            ("PREPARACION_MATRICULA", PREP_INFORME, "Informe preparacion Matricula"),
            ("DIAGNOSTICO_FUENTES", DIAG_INFORME, "Informe diagnostico fuentes avance"),
            ("BRECHAS_DIAGNOSTICO", DIAG_BRECHAS, "Expediente brechas"),
        ]
        rows = []
        for tipo, path, uso in items:
            exists = path.exists()
            rows.append(
                {
                    "TIPO_INSUMO": tipo,
                    "RUTA": str(path),
                    "EXISTE": "SI" if exists else "NO",
                    "TAMANO_BYTES": path.stat().st_size if exists else "",
                    "FECHA_MODIFICACION": datetime.fromtimestamp(path.stat().st_mtime, TZ).isoformat(timespec="seconds") if exists else "",
                    "SHA256": sha256(path) if exists and path.is_file() else "",
                    "USO_EN_GOBERNANZA": uso,
                    "SE_REUTILIZA": "SI" if exists else "NO",
                    "NO_RECALCULAR": "SI" if exists and tipo.startswith(("GOBERNANZA_29", "MATRIZ_29", "APLICACION_29", "CAMPO_DESTINO", "LECTURA_5809")) else "NO",
                }
            )
        return rows

    def a0(self) -> None:
        rows = self.source_inventory()
        df = pd.DataFrame(rows)
        missing = df[df["EXISTE"].eq("NO")]
        if not missing.empty:
            p = self.paths.control / "00_CONTROL_INSUMOS.tsv"
            write_tsv(p, df)
            self.register(p)
            raise FileNotFoundError("Faltan insumos obligatorios: " + ", ".join(missing["TIPO_INSUMO"].tolist()))
        p_control = self.paths.control / "00_CONTROL_INSUMOS.tsv"
        p_hash = self.paths.control / "00_HASHES_INSUMOS.tsv"
        p_manifest = self.paths.control / "00_MANIFEST_GOBERNANZA_COLUMNAS.json"
        p_report = self.paths.control / "00_INFORME_REUTILIZACION_INSUMOS.md"
        write_tsv(p_control, df)
        write_tsv(p_hash, df[["TIPO_INSUMO", "RUTA", "SHA256", "TAMANO_BYTES", "FECHA_MODIFICACION"]])
        write_json(
            p_manifest,
            {
                "proceso": "Avance Curricular SIES 2026",
                "subproyecto": "Matricula 5809",
                "fecha": now_iso(),
                "run_dir": str(self.paths.run),
                "insumos": rows,
                "csv_carga_generado": False,
                "sies_ready_generado": False,
            },
        )
        write_md(
            p_report,
            [
                "# Reutilizacion de insumos",
                "",
                "Se reutilizan los expedientes ya validados de gobernanza 29, preparacion Matricula y diagnostico de fuentes.",
                "No se recalculan los 29 casos, la estructura 5809 ni la decision sobre ANIO_INGRESO_*.",
                "Se construye desde cero la gobernanza columna por columna en esta ejecucion.",
                "",
                f"Insumos verificados: {len(df)}.",
            ],
        )
        self.register(p_control, p_hash, p_manifest, p_report)
        self.control("Fase 0", "COMPLETADA", [Path(r["RUTA"]) for r in rows], [p_control, p_hash, p_manifest, p_report], len(self.df5809), 0, 0, "Fase 1")

    def column_block(self, col: str) -> str:
        for block, cols in BLOCKS.items():
            if col in cols:
                return block
        return ""

    def tipo_campo(self, col: str) -> str:
        if col in NO_MODIFICABLES:
            return "NO_MODIFICABLE_PRECARGA"
        if col == "PLAN_ESTUDIOS":
            return "PLAN_MODIFICABLE_CONTROLADO"
        if col.startswith("CURSO"):
            return "ACADEMICO_SEMESTRAL_OBLIGATORIO"
        if col in {"UNIDADES_CURSADAS", "UNIDADES_APROBADAS"}:
            return "ACADEMICO_ANUAL_OBLIGATORIO"
        if col in {"UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"}:
            return "ACADEMICO_ACUMULADO_OBLIGATORIO"
        if col == "VIGENCIA":
            return "VIGENCIA_OBLIGATORIA"
        return "NO_CLASIFICADO"

    def estado_columna(self, col: str) -> tuple[str, str]:
        if col in NO_MODIFICABLES:
            return "NO_MODIFICABLE_PRECARGA", ""
        if col == "PLAN_ESTUDIOS":
            return "BLOQUEADO_POR_PLAN", "BLOQUEO_PLAN"
        if col in {"CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS"}:
            return "BLOQUEADO_POR_FUENTE", "BLOQUEO_FUENTE_AVANCE"
        if col in {"UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"}:
            return "BLOQUEADO_POR_REGLA_NO_CONFIRMADA", "BLOQUEO_FUENTE_AVANCE_PLAN_MALLA"
        if col == "VIGENCIA":
            return "LISTO_CON_ADVERTENCIA", "NO_MATERIALIZADO_POR_BLOQUEOS_INTEGRALES"
        return "PENDIENTE_REVISION_INSTITUCIONAL", "NO_CLASIFICADO"

    def a1(self) -> None:
        rows = []
        for idx, col in enumerate(ORDERED_COLUMNS, 1):
            non_empty = int(self.df5809[col].astype(str).str.strip().ne("").sum()) if col in self.df5809.columns else 0
            empty = len(self.df5809) - non_empty
            estado, bloqueo = self.estado_columna(col)
            rows.append(
                {
                    "ORDEN_COLUMNA": idx,
                    "CAMPO_5809": col,
                    "BLOQUE": self.column_block(col),
                    "TIPO_CAMPO": self.tipo_campo(col),
                    "VIENE_PRECARGADO": "SI" if non_empty else "NO",
                    "SE_MODIFICA": "NO" if col in NO_MODIFICABLES else "SI_CONTROLADO",
                    "NO_VACIOS_5809": non_empty,
                    "VACIOS_5809": empty,
                    "VALORES_DISTINTOS_MUESTRA": " | ".join(self.df5809[col].drop_duplicates().astype(str).head(10).tolist()) if col in self.df5809.columns else "",
                    "FUENTE_OFICIAL": str(INSTRUCTIVO),
                    "DEFINICION_GOBERNADA": FIELD_RULES[col]["definicion"],
                    "REGLA_OFICIAL": FIELD_RULES[col]["regla"],
                    "ESTADO_COLUMNA": estado,
                    "BLOQUEO": bloqueo,
                    "EVIDENCIA": str(LECTURA_5809),
                }
            )
        self.dictionary = pd.DataFrame(rows)
        p_tsv = self.paths.run / "01_DICCIONARIO_MAESTRO_5809.tsv"
        p_xlsx = self.paths.run / "01_DICCIONARIO_MAESTRO_5809.xlsx"
        p_md = self.paths.run / "01_INFORME_DICCIONARIO_MAESTRO_5809.md"
        write_tsv(p_tsv, self.dictionary)
        write_xlsx(p_xlsx, {"DICCIONARIO": self.dictionary})
        write_md(
            p_md,
            [
                "# Diccionario maestro 5809",
                "",
                f"Columnas gobernadas: {len(self.dictionary)}.",
                f"No modificables de precarga: {int(self.dictionary['ESTADO_COLUMNA'].eq('NO_MODIFICABLE_PRECARGA').sum())}.",
                f"Bloqueadas: {int(self.dictionary['BLOQUEO'].astype(str).str.startswith('BLOQUEO').sum())}.",
                "Se confirma que ANIO_INGRESO_* y SEM_INGRESO_* son campos de ingreso, no destino de avance curricular.",
            ],
        )
        self.register(p_tsv, p_xlsx, p_md)
        self.control("Fase 1", "COMPLETADA_CON_ADVERTENCIAS", [self.source_5809, LECTURA_5809, CAMPO_DESTINO], [p_tsv, p_xlsx, p_md], len(self.df5809), 0, int(self.dictionary["BLOQUEO"].astype(str).str.startswith("BLOQUEO").sum()), "Fase 2")

    def logic_row(self, order: int, col: str, block: str) -> dict[str, Any]:
        estado, bloqueo = self.estado_columna(col)
        rule = FIELD_RULES[col]
        dependencia_codcli = "SI" if col in {"CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"} else ("AUDITORIA" if col in {"NUM_DOCUMENTO", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRES"} else "NO")
        dependencia_plan = "SI" if col in {"PLAN_ESTUDIOS", "CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"} else "NO"
        dependencia_malla = "SI" if col in {"UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"} else "NO"
        fuente_sec = ""
        if col in {"CODIGO_UNICO", "PLAN_ESTUDIOS"}:
            fuente_sec = str(PRECARGA_5810)
        elif dependencia_codcli != "NO":
            fuente_sec = str(PROMEDIOS)
        elif dependencia_malla == "SI":
            fuente_sec = str(PLANES)
        evidencia = [str(INSTRUCTIVO), str(self.source_5809)]
        if col in {"CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"}:
            evidencia += [str(DIAG_INFORME), str(EXP_29), str(MATRIZ_29)]
        if col == "PLAN_ESTUDIOS":
            evidencia += [str(PRECARGA_5810), str(PLANES), str(DEPENDENCIAS_CARRERAS)]
        if col in {"ANIO_INGRESO_CARRERA_ACTUAL", "ANIO_INGRESO_CARRERA_ORIGEN"}:
            evidencia += [str(CAMPO_DESTINO)]
        return {
            "ORDEN_COLUMNA": order,
            "CAMPO_5809": col,
            "BLOQUE": block,
            "TIPO_CAMPO": self.tipo_campo(col),
            "SE_MODIFICA": "NO" if col in NO_MODIFICABLES else "SI_CONTROLADO",
            "FUENTE_OFICIAL": str(INSTRUCTIVO),
            "REGLA_OFICIAL": rule["regla"],
            "FUENTE_DATO_PRIMARIA": rule["fuente"],
            "FUENTE_DATO_SECUNDARIA": fuente_sec,
            "LLAVE_CRUCE": rule["llave"],
            "FILTRO_TEMPORAL": "2025" if col in {"CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"} else "No aplica",
            "FORMULA_O_LOGICA": self.formula(col),
            "INCLUYE_CONVALIDACIONES": self.convalidaciones(col),
            "DEPENDENCIA_CODCLI": dependencia_codcli,
            "DEPENDENCIA_PLAN": dependencia_plan,
            "DEPENDENCIA_MALLA": dependencia_malla,
            "DEPENDENCIA_CARRERAS_5810": "SI" if col in {"CODIGO_UNICO", "PLAN_ESTUDIOS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"} else "NO",
            "VALIDACION_FUNCIONAL": rule["validacion"],
            "VALIDACION_TECNICA": self.validacion_tecnica(col),
            "CASOS_ESPECIALES_APLICAN": self.casos_especiales(col),
            "ACCION_ANTE_PROBLEMA": self.accion_problema(col),
            "ESTADO_COLUMNA": estado,
            "BLOQUEO": bloqueo,
            "EVIDENCIA": " | ".join(evidencia),
            "SCRIPT": str(Path(__file__).resolve()),
            "SALIDA": f"BLOQUE_{block}_RESULTADO.xlsx",
        }

    def formula(self, col: str) -> str:
        if col in NO_MODIFICABLES:
            return "Conservar valor de precarga; comparar hash/estructura si se genera derivado."
        if col == "PLAN_ESTUDIOS":
            return "Validar CODIGO_UNICO+PLAN contra 5810 y conciliacion planes; no materializar si Carreras sigue bloqueada."
        if col == "CURSO_1ER_SEM":
            return "Derivar SI/NO desde actividad academica exigida en plan durante semestre 1 de 2025; no usar nivel como sustituto."
        if col == "CURSO_2DO_SEM":
            return "Derivar SI/NO desde actividad academica exigida en plan durante semestre 2 de 2025; no usar nivel como sustituto."
        if col == "UNIDADES_CURSADAS":
            return "Sumar unidades cursadas efectivamente en 2025 del plan informado, excluyendo validaciones/reconocimientos."
        if col == "UNIDADES_APROBADAS":
            return "Sumar unidades aprobadas efectivamente en 2025 del plan informado, excluyendo validaciones/reconocimientos."
        if col == "UNID_CURSADAS_TOTAL":
            return "Sumar historico cursado hasta fin 2025, incluyendo validaciones/reconocimientos segun instructivo."
        if col == "UNID_APROBADAS_TOTAL":
            return "Sumar historico aprobado hasta fin 2025, incluyendo validaciones/reconocimientos y controlando total plan+tolerancia."
        if col == "VIGENCIA":
            return "Mantener 1 si el registro se conserva; 0 solo para eliminar registro cargado por error con respaldo."
        return ""

    def convalidaciones(self, col: str) -> str:
        if col in {"UNIDADES_CURSADAS", "UNIDADES_APROBADAS"}:
            return "NO; el instructivo excluye validacion de estudios/reconocimiento de aprendizajes previos para anual."
        if col in {"UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"}:
            return "SI; el instructivo indica incluir validacion/reconocimiento en total acumulado."
        return "NO_APLICA"

    def validacion_tecnica(self, col: str) -> str:
        validations = {
            "TIPO_DOCUMENTO": "set(TIPO_DOCUMENTO) subset {R,P}; reglas DV por tipo.",
            "DV": "DV numerico o K cuando tipo R; vacio cuando tipo P.",
            "SEXO": "set(SEXO) subset {H,M,X}.",
            "FECHA_NACIMIENTO": "Parseo fecha; edad minima segun error de carga.",
            "CODIGO_UNICO": "CODIGO_UNICO in precarga 5810.",
            "PLAN_ESTUDIOS": "(CODIGO_UNICO, PLAN_ESTUDIOS) in 5810 y conciliacion Carreras.",
            "ANIO_INGRESO_CARRERA_ACTUAL": "Entero <= 2025.",
            "SEM_INGRESO_CARRERA_ACTUAL": "Valor 1 o 2.",
            "ANIO_INGRESO_CARRERA_ORIGEN": "Entero <= 2025 y <= actual.",
            "SEM_INGRESO_CARRERA_ORIGEN": "Valor 1 o 2.",
            "CURSO_1ER_SEM": "Valor SI/NO; si SI entonces UNIDADES_CURSADAS > 0.",
            "CURSO_2DO_SEM": "Valor SI/NO; si SI entonces UNIDADES_CURSADAS > 0; si ambos NO, unidades cursadas=0.",
            "UNIDADES_CURSADAS": "Numero >=0; anual; no mayor que total cursado.",
            "UNIDADES_APROBADAS": "Numero >=0; <= UNIDADES_CURSADAS; <= total aprobado.",
            "UNID_CURSADAS_TOTAL": "Numero >=0; >= anual cursado.",
            "UNID_APROBADAS_TOTAL": "Numero >=0; <= UNID_CURSADAS_TOTAL; limite total plan +25%.",
            "VIGENCIA": "Valor en {0,1}.",
        }
        return validations.get(col, "Conservar estructura y hash de no modificables.")

    def casos_especiales(self, col: str) -> str:
        if col in {"CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"}:
            return "29 casos: 2 adecuados con CODCLI exacto/reporte individual; 27 pendientes; convalidaciones observadas; planes sin semantica nivel."
        if col in {"NUM_DOCUMENTO", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRES", "CODIGO_UNICO"}:
            return "Multiples CODCLI, contradiccion documento, contradiccion carrera, sin identidad."
        if col == "PLAN_ESTUDIOS":
            return "15 planes/42 filas con semantica NIVEL no confirmada; plan multiple/no encontrado si aparece."
        return "No aplica o solo revision institucional si falla catalogo."

    def accion_problema(self, col: str) -> str:
        if col in NO_MODIFICABLES:
            return "Documentar y bloquear si hay contradiccion; no corregir automaticamente."
        if col == "PLAN_ESTUDIOS":
            return "Bloquear por plan/Carreras hasta confirmacion; no inventar correlativo."
        if col in {"CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL"}:
            return "Bloquear por fuente/regla; no completar por similitud ni por nivel historico no demostrado."
        if col == "VIGENCIA":
            return "Bloquear/revisar si no es 0/1 o deriva de otro proceso."
        return "Revision institucional."

    def block_validations(self, block: str, cols: list[str]) -> pd.DataFrame:
        rows = []
        df = self.df5809
        if block == "01":
            rows.extend(
                [
                    {"VALIDACION": "TIPO_DOCUMENTO_R_P", "RESULTADO": "OK" if set(df["TIPO_DOCUMENTO"].unique()).issubset({"R", "P"}) else "BLOQUEA", "CASOS": int((~df["TIPO_DOCUMENTO"].isin(["R", "P"])).sum()), "DETALLE": "Catalogo R/P."},
                    {"VALIDACION": "DV_RUT_OBLIGATORIO", "RESULTADO": "OK" if int(((df["TIPO_DOCUMENTO"] == "R") & (df["DV"].str.strip() == "")).sum()) == 0 else "BLOQUEA", "CASOS": int(((df["TIPO_DOCUMENTO"] == "R") & (df["DV"].str.strip() == "")).sum()), "DETALLE": "DV requerido para RUT."},
                    {"VALIDACION": "IDENTIDAD_PREPARATORIA", "RESULTADO": "ADVERTENCIA", "CASOS": self.count_identity_blockers(), "DETALLE": "Reutiliza expediente identidad; no modifica documentos."},
                ]
            )
        elif block == "02":
            missing_codes = self.missing_codigo_unico()
            rows.extend(
                [
                    {"VALIDACION": "SEXO_H_M_X", "RESULTADO": "OK" if set(df["SEXO"].unique()).issubset({"H", "M", "X"}) else "BLOQUEA", "CASOS": int((~df["SEXO"].isin(["H", "M", "X"])).sum()), "DETALLE": "Catalogo H/M/X."},
                    {"VALIDACION": "CODIGO_UNICO_EXISTE_5810", "RESULTADO": "OK" if missing_codes == 0 else "BLOQUEA", "CASOS": missing_codes, "DETALLE": "CODIGO_UNICO de 5809 contra 5810."},
                    {"VALIDACION": "NOMBRES_NO_LLAVE_PRINCIPAL", "RESULTADO": "OK", "CASOS": 0, "DETALLE": "Decision reutilizada: no usar nombre para resolver identidad."},
                ]
            )
        elif block == "03":
            combo_missing = self.missing_combo_plan()
            rows.extend(
                [
                    {"VALIDACION": "PLAN_COMBO_EXISTE_5810", "RESULTADO": "OK" if combo_missing == 0 else "BLOQUEA", "CASOS": combo_missing, "DETALLE": "CODIGO_UNICO+PLAN_ESTUDIOS contra 5810."},
                    {"VALIDACION": "ANIO_INGRESO_ACTUAL_MAYOR_2025", "RESULTADO": "OK" if self.year_gt("ANIO_INGRESO_CARRERA_ACTUAL", 2025) == 0 else "BLOQUEA", "CASOS": self.year_gt("ANIO_INGRESO_CARRERA_ACTUAL", 2025), "DETALLE": "Regla instructivo."},
                    {"VALIDACION": "ANIO_INGRESO_ORIGEN_MAYOR_2025", "RESULTADO": "OK" if self.year_gt("ANIO_INGRESO_CARRERA_ORIGEN", 2025) == 0 else "BLOQUEA", "CASOS": self.year_gt("ANIO_INGRESO_CARRERA_ORIGEN", 2025), "DETALLE": "Regla instructivo."},
                    {"VALIDACION": "ANIO_CURRICULAR_NO_ES_DESTINO", "RESULTADO": "OK", "CASOS": 0, "DETALLE": "Decision validada en identificacion campo destino."},
                    {"VALIDACION": "DEPENDENCIA_CARRERAS_PLANES", "RESULTADO": "BLOQUEA", "CASOS": 15, "DETALLE": "15 planes con semantica/distribucion anual pendiente."},
                ]
            )
        elif block == "04":
            rows.extend(
                [
                    {"VALIDACION": "CURSO_VALORES_SI_NO", "RESULTADO": "BLOQUEA", "CASOS": len(df), "DETALLE": "Campos vacios; fuente academica 2025 no materializada."},
                    {"VALIDACION": "GOBERNANZA_29", "RESULTADO": "ADVERTENCIA", "CASOS": 29, "DETALLE": "2 adecuados, 27 pendientes; no extender regla."},
                ]
            )
        elif block == "05":
            rows.extend(
                [
                    {"VALIDACION": "UNIDADES_ANUALES_OBLIGATORIAS", "RESULTADO": "BLOQUEA", "CASOS": len(df), "DETALLE": "Campos vacios; fuente anual 2025 parcial/no materializada."},
                    {"VALIDACION": "CONVALIDACIONES_EXCLUIDAS_ANUAL", "RESULTADO": "BLOQUEA", "CASOS": 5000, "DETALLE": "Convalidaciones observadas requieren regla operacional para fuente; anual las excluye segun instructivo."},
                ]
            )
        elif block == "06":
            rows.extend(
                [
                    {"VALIDACION": "ACUMULADOS_OBLIGATORIOS", "RESULTADO": "BLOQUEA", "CASOS": len(df), "DETALLE": "Campos vacios; historico acumulado y malla no materializados."},
                    {"VALIDACION": "LIMITE_TOTAL_PLAN_TOLERANCIA", "RESULTADO": "BLOQUEA", "CASOS": 15, "DETALLE": "Plan/malla y semantica de nivel pendientes para control de limites."},
                ]
            )
        elif block == "07":
            invalid = int((~df["VIGENCIA"].isin(["0", "1"])).sum())
            rows.extend(
                [
                    {"VALIDACION": "VIGENCIA_0_1", "RESULTADO": "OK" if invalid == 0 else "BLOQUEA", "CASOS": invalid, "DETALLE": "Catalogo 0/1."},
                    {"VALIDACION": "NO_MEZCLAR_OTROS_PROCESOS", "RESULTADO": "OK", "CASOS": 0, "DETALLE": "Gobernanza limitada a Avance Curricular."},
                ]
            )
        return pd.DataFrame(rows)

    def count_identity_blockers(self) -> int:
        if self.identity.empty or "CLASIFICACION_IDENTIDAD" not in self.identity.columns:
            return 0
        return int((~self.identity["CLASIFICACION_IDENTIDAD"].eq("IDENTIDAD_EXACTA")).sum())

    def missing_codigo_unico(self) -> int:
        return int((~self.df5809["CODIGO_UNICO"].isin(set(self.df5810["CODIGO_UNICO"]))).sum())

    def missing_combo_plan(self) -> int:
        combos5810 = set(zip(self.df5810["CODIGO_UNICO"], self.df5810["PLAN_ESTUDIOS"]))
        return int(sum((cu, pl) not in combos5810 for cu, pl in zip(self.df5809["CODIGO_UNICO"], self.df5809["PLAN_ESTUDIOS"])))

    def year_gt(self, col: str, limit: int) -> int:
        vals = pd.to_numeric(self.df5809[col], errors="coerce")
        return int((vals > limit).sum())

    def block_sources(self, block: str, cols: list[str]) -> pd.DataFrame:
        rows = []
        for col in cols:
            rule = FIELD_RULES[col]
            rows.append(
                {
                    "CAMPO_5809": col,
                    "REGLA_OFICIAL": str(INSTRUCTIVO),
                    "DATO_OBSERVADO": rule["fuente"],
                    "IMPLEMENTACION_TECNICA": "Cruces y validaciones documentadas en este bloque; no se materializan valores finales.",
                    "DECISION_INTERNA": self.accion_problema(col),
                    "HIPOTESIS_O_PENDIENTE": self.estado_columna(col)[1],
                    "RUTA_EVIDENCIA_PRIMARIA": str(self.source_5809),
                    "RUTA_EVIDENCIA_SECUNDARIA": str(PROMEDIOS if "academ" in rule["fuente"].lower() else PRECARGA_5810 if col in {"CODIGO_UNICO", "PLAN_ESTUDIOS"} else INSTRUCTIVO),
                }
            )
        return pd.DataFrame(rows)

    def block_rules(self, block: str, cols: list[str]) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "CAMPO_5809": col,
                    "DEFINICION": FIELD_RULES[col]["definicion"],
                    "REGLA_OFICIAL": FIELD_RULES[col]["regla"],
                    "VALIDACION_OFICIAL_O_MENSAJE_ERROR": FIELD_RULES[col]["validacion"],
                    "REFERENCIA": "Instructivo paginas 12-14 y Anexo V; ver hashes en fase 0.",
                }
                for col in cols
            ]
        )

    def block_crosses(self, block: str, cols: list[str]) -> pd.DataFrame:
        rows = []
        for col in cols:
            rows.append(
                {
                    "CAMPO_5809": col,
                    "LLAVE_CRUCE": FIELD_RULES[col]["llave"],
                    "FUENTE_CRUCE": FIELD_RULES[col]["fuente"],
                    "USO_CRUCE": "Validacion" if col in NO_MODIFICABLES else "Preparacion controlada",
                    "ESTADO_CRUCE": "VALIDADO_ESTRUCTURALMENTE" if self.estado_columna(col)[0] in {"NO_MODIFICABLE_PRECARGA", "LISTO_CON_ADVERTENCIA"} else "BLOQUEADO_O_PARCIAL",
                    "NO_USAR": "Nombre como llave principal; similitud de carrera como conversion; ANIO_INGRESO como anio curricular.",
                }
            )
        return pd.DataFrame(rows)

    def block_breaches(self, logic: pd.DataFrame) -> pd.DataFrame:
        blocked = logic[logic["BLOQUEO"].astype(str).ne("")].copy()
        if blocked.empty:
            return pd.DataFrame(columns=["CAMPO_5809", "TIPO_BRECHA", "MOTIVO", "ACCION_REQUERIDA", "ESTADO"])
        return pd.DataFrame(
            [
                {
                    "CAMPO_5809": r["CAMPO_5809"],
                    "TIPO_BRECHA": r["BLOQUEO"],
                    "MOTIVO": r["ACCION_ANTE_PROBLEMA"],
                    "ACCION_REQUERIDA": "Resolver fuente/identidad/plan/regla indicada antes de carga final.",
                    "ESTADO": "PENDIENTE" if str(r["BLOQUEO"]).startswith("BLOQUEO") else "ADVERTENCIA",
                }
                for _, r in blocked.iterrows()
            ]
        )

    def block_decisions(self, block: str, cols: list[str]) -> pd.DataFrame:
        decisions = [
            {
                "DECISION": "Separar regla oficial, dato observado, implementacion tecnica, decision interna e hipotesis.",
                "FUNDAMENTO": "Prompt maestro y trazabilidad de cierre.",
                "APLICA_A": "Todos los campos del bloque.",
                "ESTADO": "VIGENTE",
            }
        ]
        if block == "03":
            decisions.append(
                {
                    "DECISION": "No escribir ANIO_CURRICULAR_ADECUADO en ANIO_INGRESO_*.",
                    "FUNDAMENTO": str(CAMPO_DESTINO),
                    "APLICA_A": "ANIO_INGRESO_CARRERA_ACTUAL; ANIO_INGRESO_CARRERA_ORIGEN",
                    "ESTADO": "VIGENTE",
                }
            )
        if block in {"04", "05", "06"}:
            decisions.append(
                {
                    "DECISION": "No extender los 2 casos adecuados a los 27 pendientes.",
                    "FUNDAMENTO": str(EXP_29),
                    "APLICA_A": "Campos academicos y periodizacion especial",
                    "ESTADO": "VIGENTE",
                }
            )
        return pd.DataFrame(decisions)

    def block_specials(self, block: str, cols: list[str]) -> pd.DataFrame:
        rows = []
        specials = self.special_catalog_rows()
        for sp in specials:
            applies = "NO"
            if block in {"04", "05", "06"} and sp["TIPO_CASO"] in {
                "Nivel historico con CODCLI exacto y reporte individual",
                "Nivel historico sin reporte individual",
                "Familia CODCLI + carrera, sin evidencia directa",
                "Solo carrera similar",
                "Sin modelo demostrado",
                "Convalidacion observada sin regla confirmada",
                "Plan/malla sin semantica de nivel",
                "Avance anual no demostrable",
                "Acumulado no demostrable",
            }:
                applies = "SI"
            if block in {"01", "02"} and sp["TIPO_CASO"] in {"Contradiccion documento", "Contradiccion carrera", "Multiples CODCLI"}:
                applies = "SI"
            if block == "03" and sp["TIPO_CASO"] in {"Plan multiple", "Plan/malla sin semantica de nivel"}:
                applies = "SI"
            if applies == "SI":
                row = sp.copy()
                row["BLOQUE"] = block
                row["CAMPOS_AFECTADOS"] = " | ".join(cols)
                rows.append(row)
        return pd.DataFrame(rows)

    def run_blocks(self) -> None:
        phase_map = {"01": "Fase 2", "02": "Fase 3", "03": "Fase 4", "04": "Fase 5", "05": "Fase 6", "06": "Fase 7", "07": "Fase 8"}
        next_map = {"01": "Fase 3", "02": "Fase 4", "03": "Fase 5", "04": "Fase 6", "05": "Fase 7", "06": "Fase 8", "07": "Fase 9"}
        for block, cols in BLOCKS.items():
            block_dir = self.paths.run / f"BLOQUE_{block}_{self.paths.run.name.split('_')[-2]}_{self.paths.run.name.split('_')[-1]}"
            block_dir.mkdir(parents=True, exist_ok=True)
            logic = pd.DataFrame([self.logic_row(ORDERED_COLUMNS.index(col) + 1, col, block) for col in cols])
            fuentes = self.block_sources(block, cols)
            reglas = self.block_rules(block, cols)
            cruces = self.block_crosses(block, cols)
            validaciones = self.block_validations(block, cols)
            brechas = self.block_breaches(logic)
            decisiones = self.block_decisions(block, cols)
            especiales = self.block_specials(block, cols)
            outputs = {
                f"BLOQUE_{block}_LOGICA_COLUMNAS.tsv": logic,
                f"BLOQUE_{block}_FUENTES.tsv": fuentes,
                f"BLOQUE_{block}_REGLAS_MANUAL.tsv": reglas,
                f"BLOQUE_{block}_CRUCES.tsv": cruces,
                f"BLOQUE_{block}_VALIDACIONES.tsv": validaciones,
                f"BLOQUE_{block}_BRECHAS.tsv": brechas,
                f"BLOQUE_{block}_DECISIONES.tsv": decisiones,
                f"BLOQUE_{block}_GOBERNANZA_CASOS_ESPECIALES.tsv": especiales,
            }
            generated_paths = []
            for name, df in outputs.items():
                path = block_dir / name
                write_tsv(path, df)
                generated_paths.append(path)
            result = block_dir / f"BLOQUE_{block}_RESULTADO.xlsx"
            write_xlsx(
                result,
                {
                    "LOGICA": logic,
                    "FUENTES": fuentes,
                    "REGLAS": reglas,
                    "CRUCES": cruces,
                    "VALIDACIONES": validaciones,
                    "BRECHAS": brechas,
                    "DECISIONES": decisiones,
                    "CASOS_ESPECIALES": especiales,
                },
            )
            report = block_dir / f"BLOQUE_{block}_INFORME.md"
            write_md(
                report,
                [
                    f"# Gobernanza Bloque {block}",
                    "",
                    f"Columnas: {', '.join(cols)}.",
                    f"Estado dominante: {self.phase_status_from_breaches(brechas)}.",
                    f"Bloqueos registrados: {len(brechas)}.",
                    "",
                    "No se modificaron fuentes originales. No se genero CSV de carga ni SIES_READY.",
                ],
            )
            generated_paths.extend([result, report])
            manifest = block_dir / f"manifest_bloque_{block.lower()}.json"
            write_json(
                manifest,
                {
                    "bloque": block,
                    "fecha": now_iso(),
                    "columnas": cols,
                    "estado": self.phase_status_from_breaches(brechas),
                    "salidas": [{"ruta": str(p), "sha256": sha256(p), "tamano_bytes": p.stat().st_size} for p in generated_paths],
                    "csv_carga_generado": False,
                    "sies_ready_generado": False,
                },
            )
            generated_paths.append(manifest)
            self.register(*generated_paths)
            self.block_logics.append(logic)
            self.control(phase_map[block], self.phase_status_from_breaches(brechas), [self.source_5809, INSTRUCTIVO, IDENTIDAD, PRECARGA_5810, EXP_29], generated_paths, len(self.df5809), int((validaciones["RESULTADO"] == "BLOQUEA").sum()) if not validaciones.empty else 0, len(brechas), next_map[block])

    def phase_status_from_breaches(self, brechas: pd.DataFrame) -> str:
        if brechas.empty:
            return "COMPLETADA"
        blockers = brechas["TIPO_BRECHA"].astype(str).tolist()
        if any("PLAN" in b for b in blockers):
            return "BLOQUEADA_POR_PLAN"
        if any("IDENTIDAD" in b for b in blockers):
            return "BLOQUEADA_POR_IDENTIDAD"
        if any("FUENTE" in b for b in blockers):
            return "BLOQUEADA_POR_FUENTE"
        if any("REGLA" in b for b in blockers):
            return "BLOQUEADA_POR_EVIDENCIA_FALTANTE"
        return "COMPLETADA_CON_ADVERTENCIAS"

    def a9(self) -> None:
        self.master = pd.concat(self.block_logics, ignore_index=True)
        p_tsv = self.paths.run / "09_MATRIZ_MAESTRA_GOBERNANZA_5809.tsv"
        p_xlsx = self.paths.run / "09_MATRIZ_MAESTRA_GOBERNANZA_5809.xlsx"
        p_md = self.paths.run / "09_INFORME_MATRIZ_MAESTRA_GOBERNANZA_5809.md"
        write_tsv(p_tsv, self.master)
        write_xlsx(p_xlsx, {"MATRIZ_MAESTRA": self.master})
        blocked = int(self.master["BLOQUEO"].astype(str).str.startswith("BLOQUEO").sum())
        ready = int(self.master["ESTADO_COLUMNA"].isin(["LISTO_PARA_CANDIDATO", "LISTO_CON_ADVERTENCIA"]).sum())
        write_md(
            p_md,
            [
                "# Matriz maestra gobernanza 5809",
                "",
                f"Columnas gobernadas: {len(self.master)}.",
                f"Columnas listas o listas con advertencia: {ready}.",
                f"Columnas bloqueadas: {blocked}.",
                "La matriz es la fuente interna principal para futuras consultas del archivo 5809.",
            ],
        )
        self.register(p_tsv, p_xlsx, p_md)
        self.control("Fase 9", "COMPLETADA_CON_ADVERTENCIAS", [self.source_5809], [p_tsv, p_xlsx, p_md], len(self.df5809), 0, blocked, "Fase 10")

    def a10(self) -> None:
        rows = []
        for _, r in self.master.iterrows():
            rows.append(
                {
                    "COLUMNA": r["CAMPO_5809"],
                    "DEFINICION": FIELD_RULES[r["CAMPO_5809"]]["definicion"],
                    "REGLA_OFICIAL": r["REGLA_OFICIAL"],
                    "INTERPRETACION_FUNCIONAL": r["FORMULA_O_LOGICA"],
                    "FUENTE_DATO": r["FUENTE_DATO_PRIMARIA"],
                    "LLAVE_CRUCE": r["LLAVE_CRUCE"],
                    "FORMULA_O_LOGICA": r["FORMULA_O_LOGICA"],
                    "VALIDACIONES": r["VALIDACION_FUNCIONAL"] + " / " + r["VALIDACION_TECNICA"],
                    "CASOS_ESPECIALES": r["CASOS_ESPECIALES_APLICAN"],
                    "ACCION_ANTE_PROBLEMA": r["ACCION_ANTE_PROBLEMA"],
                    "ESTADO_ACTUAL": r["ESTADO_COLUMNA"],
                    "PENDIENTES": r["BLOQUEO"],
                    "EVIDENCIAS": r["EVIDENCIA"],
                }
            )
        manual_df = pd.DataFrame(rows)
        p_md = self.paths.run / "10_MANUAL_GOBERNADO_5809_AVANCE_CURRICULAR_2026.md"
        p_xlsx = self.paths.run / "10_MANUAL_GOBERNADO_5809_AVANCE_CURRICULAR_2026.xlsx"
        lines = ["# Manual gobernado 5809 Avance Curricular 2026", ""]
        for row in rows:
            lines += [
                f"## {row['COLUMNA']}",
                f"- Definicion: {row['DEFINICION']}",
                f"- Regla oficial: {row['REGLA_OFICIAL']}",
                f"- Fuente de dato: {row['FUENTE_DATO']}",
                f"- Llave de cruce: {row['LLAVE_CRUCE']}",
                f"- Logica: {row['FORMULA_O_LOGICA']}",
                f"- Estado actual: {row['ESTADO_ACTUAL']}",
                f"- Pendientes: {row['PENDIENTES']}",
                "",
            ]
        write_md(p_md, lines)
        write_xlsx(p_xlsx, {"MANUAL": manual_df})
        self.register(p_md, p_xlsx)
        self.control("Fase 10", "COMPLETADA_CON_ADVERTENCIAS", [p for p in self.generated if "BLOQUE_" in str(p)], [p_md, p_xlsx], len(self.df5809), 0, int(self.master["BLOQUEO"].astype(str).str.startswith("BLOQUEO").sum()), "Fase 11")

    def special_catalog_rows(self) -> list[dict[str, Any]]:
        return [
            self.special("Nivel historico con CODCLI exacto y reporte individual", "Nivel fuera de rango con evidencia directa.", "CODCLI exacto + reporte individual.", "Aplicar gobernanza solo al caso evidenciado.", "Generalizar regla a otros casos.", "SI si no esta demostrado.", "Solo candidato interno si evidencia directa.", "Reporte individual + CODCLI.", "ID 1885 e ID 2050", str(EXP_29)),
            self.special("Nivel historico sin reporte individual", "Nivel no interpretable sin fuente directa.", "Expediente 29 / fuente avance.", "Mantener pendiente.", "Convertir por semejanza.", "SI", "NO", "Reporte individual o tabla institucional.", "27 pendientes", str(EXP_29)),
            self.special("Familia CODCLI + carrera, sin evidencia directa", "Coincidencia parcial por familia.", "CODCLI + carrera.", "Solicitar respaldo.", "Convertir por familia.", "SI", "NO", "Evidencia directa por caso.", "14 casos esperados", str(MATRIZ_29)),
            self.special("Solo carrera similar", "Coincidencia solo por carrera.", "Carrera.", "Mantener pendiente.", "Convertir por carrera.", "SI", "NO", "CODCLI/reporte.", "5 casos esperados", str(MATRIZ_29)),
            self.special("Sin modelo demostrado", "No hay modelo de conversion.", "No demostrado.", "Mantener pendiente.", "Eliminar o rechazar definitivo.", "SI", "NO", "Modelo institucional.", "8 casos esperados", str(MATRIZ_29)),
            self.special("Plan multiple", "Mas de un plan posible.", "Conciliacion planes.", "Bloquear por plan.", "Elegir keep first/last.", "SI", "NO", "Confirmacion institucional.", "Plan multiple/no encontrado si aparece", str(PREP)),
            self.special("Contradiccion documento", "Documento institucional no coincide.", "Identidad/CODCLI.", "Bloquear identidad.", "Corregir documento de precarga.", "SI", "NO", "Resolucion institucional.", "21 casos en preparacion", str(IDENTIDAD)),
            self.special("Contradiccion carrera", "Carrera de fuente no coincide.", "Identidad/Carreras.", "Bloquear identidad/carrera.", "Forzar carrera.", "SI", "NO", "Resolucion institucional.", "400 casos en preparacion", str(IDENTIDAD)),
            self.special("Multiples CODCLI", "Persona con varias trayectorias.", "DatosAlumnos.", "Resolver trayectoria.", "Decidir por nombre.", "SI", "NO", "CODCLI vigente/carrera.", "581 casos en preparacion", str(IDENTIDAD)),
            self.special("Fuente academica ausente", "No hay fuente completa para avance.", "Diagnostico fuentes.", "Solicitar fuente avance 2025.", "Inventar valores.", "SI", "NO", "Base academica 2025 validada.", "2371 filas afectadas", str(DIAG_BRECHAS)),
            self.special("Avance anual no demostrable", "No hay cursadas/aprobadas 2025 trazables.", "Fuente avance.", "Bloquear anual.", "Mezclar historico con anual.", "SI", "NO", "Estados academicos 2025.", "Campos 18-19", str(DIAG_INFORME)),
            self.special("Acumulado no demostrable", "No hay historico trazable hasta 2025.", "Historico academico.", "Bloquear acumulado.", "Usar anual como total.", "SI", "NO", "Historico + plan.", "Campos 20-21", str(DIAG_INFORME)),
            self.special("Convalidacion observada sin regla confirmada", "Estados de convalidacion observados.", "Catalogo estados.", "Separar anual/acumulado segun instructivo.", "Incluir anual sin respaldo.", "SI", "NO", "Regla operacional y catalogo.", "5000 casos observados", str(DIAG_BRECHAS)),
            self.special("Plan/malla sin semantica de nivel", "NIVEL no mapeado institucionalmente.", "Carreras 5810/planes.", "Bloquear Carreras/Matricula.", "Convertir nivel por supuesto.", "SI", "NO", "Mapa NIVEL->anio/unidades.", "15 planes/42 filas", str(DEPENDENCIAS_CARRERAS)),
            self.special("Unidades acumuladas fuera de rango", "Acumulado excede plan/tolerancia.", "Plan/malla + acumulado.", "Bloquear salvo evidencia.", "Cargar excedente sin respaldo.", "SI", "NO", "Total plan + tolerancia + evidencia.", "Sin calculo aun", str(PLANES)),
        ]

    def special(self, tipo: str, problema: str, detect: str, permitida: str, prohibida: str, bloquea: str, candidato: str, evidencia: str, ejemplo: str, artefacto: str) -> dict[str, Any]:
        return {
            "TIPO_CASO": tipo,
            "PROBLEMA": problema,
            "COMO_DETECTARLO": detect,
            "FUENTE_NECESARIA": evidencia,
            "ACCION_PERMITIDA": permitida,
            "ACCION_PROHIBIDA": prohibida,
            "BLOQUEA_ARCHIVO_FINAL": bloquea,
            "PUEDE_ENTRAR_CANDIDATO_INTERNO": candidato,
            "EVIDENCIA_MINIMA_REQUERIDA": evidencia,
            "EJEMPLO_DISPONIBLE": ejemplo,
            "ARTEFACTO_RELACIONADO": artefacto,
        }

    def a11(self) -> None:
        catalog = pd.DataFrame(self.special_catalog_rows())
        p_tsv = self.paths.run / "11_CATALOGO_CASOS_ESPECIALES_5809.tsv"
        p_xlsx = self.paths.run / "11_CATALOGO_CASOS_ESPECIALES_5809.xlsx"
        p_md = self.paths.run / "11_MANUAL_CASOS_ESPECIALES_5809.md"
        write_tsv(p_tsv, catalog)
        write_xlsx(p_xlsx, {"CATALOGO": catalog})
        lines = ["# Manual casos especiales 5809", "", "Resultado incorporado: 2 casos adecuados, 27 pendientes, 0 rechazos definitivos.", ""]
        for _, r in catalog.iterrows():
            lines += [
                f"## {r['TIPO_CASO']}",
                f"- Problema: {r['PROBLEMA']}",
                f"- Accion permitida: {r['ACCION_PERMITIDA']}",
                f"- Accion prohibida: {r['ACCION_PROHIBIDA']}",
                f"- Bloquea archivo final: {r['BLOQUEA_ARCHIVO_FINAL']}",
                f"- Evidencia minima: {r['EVIDENCIA_MINIMA_REQUERIDA']}",
                "",
            ]
        write_md(p_md, lines)
        self.register(p_tsv, p_xlsx, p_md)
        self.control("Fase 11", "COMPLETADA_CON_ADVERTENCIAS", [EXP_29, MATRIZ_29, APLICACION_29, DIAG_BRECHAS], [p_tsv, p_xlsx, p_md], 29, 0, int((catalog["BLOQUEA_ARCHIVO_FINAL"] == "SI").sum()), "Fase 12 condicionada")

    def a12_skip(self) -> None:
        p_decision = self.paths.run / "12_DECISION_CANDIDATO_INTERNO_NO_EJECUTADO.md"
        p_valid = self.paths.run / "12_VALIDACIONES_CANDIDATO.tsv"
        p_bloq = self.paths.run / "12_BLOQUEOS_CANDIDATO.tsv"
        blocked_fields = self.master[self.master["BLOQUEO"].astype(str).str.startswith("BLOQUEO")].copy()
        valid = pd.DataFrame(
            [
                {"VALIDACION": "EXISTEN_CAMPOS_OBLIGATORIOS_BLOQUEADOS", "ESTADO": "BLOQUEA", "DETALLE": "PLAN_ESTUDIOS y campos academicos 16-21 no deben materializarse sin evidencia."},
                {"VALIDACION": "NO_GENERAR_CSV_CARGA", "ESTADO": "OK", "DETALLE": "No se genero candidato CSV ni SIES_READY."},
            ]
        )
        write_tsv(p_valid, valid)
        write_tsv(p_bloq, blocked_fields)
        write_md(
            p_decision,
            [
                "# Candidato interno no ejecutado",
                "",
                "Fase 12 no ejecutada porque la matriz maestra conserva campos obligatorios bloqueados por plan, fuente y regla no confirmada.",
                "No se genero XLSX de candidato, no se genero CSV de candidato y no se genero SIES_READY.",
            ],
        )
        self.register(p_decision, p_valid, p_bloq)
        self.control("Fase 12", "BLOQUEADA_POR_EVIDENCIA_FALTANTE", [self.paths.run / "09_MATRIZ_MAESTRA_GOBERNANZA_5809.tsv"], [p_decision, p_valid, p_bloq], len(self.df5809), 1, len(blocked_fields), "Fase 13 preparatoria")

    def a13(self) -> None:
        combos5810 = set(zip(self.df5810["CODIGO_UNICO"], self.df5810["PLAN_ESTUDIOS"]))
        val_rows = [
            {"CONTROL": "CODIGO_UNICO_5809_EXISTE_5810", "ESTADO": "OK" if self.missing_codigo_unico() == 0 else "BLOQUEA", "CASOS": self.missing_codigo_unico(), "DETALLE": "Codigo unico contra precarga Carreras."},
            {"CONTROL": "CODIGO_UNICO_PLAN_5809_EXISTE_5810", "ESTADO": "OK" if self.missing_combo_plan() == 0 else "BLOQUEA", "CASOS": self.missing_combo_plan(), "DETALLE": "Combinacion contra Carreras."},
            {"CONTROL": "PLANES_SEMANTICA_NIVEL", "ESTADO": "BLOQUEA", "CASOS": 15, "DETALLE": "15 planes sin confirmacion de semantica NIVEL/distribucion anual."},
            {"CONTROL": "CAMPOS_OBLIGATORIOS_SIN_FUENTE", "ESTADO": "BLOQUEA", "CASOS": 6, "DETALLE": "Campos 16-21 bloqueados por fuente/regla."},
            {"CONTROL": "CASOS_ESPECIALES_NO_RESUELTOS", "ESTADO": "BLOQUEA", "CASOS": 27, "DETALLE": "Periodizacion individual pendiente."},
        ]
        errors = pd.DataFrame([r for r in val_rows if r["ESTADO"] == "BLOQUEA"])
        warnings = pd.DataFrame([r for r in val_rows if r["ESTADO"] != "BLOQUEA"])
        p_xlsx = self.paths.run / "13_VALIDACION_INTEGRAL_5809_5810.xlsx"
        p_err = self.paths.run / "13_ERRORES_CRITICOS.tsv"
        p_adv = self.paths.run / "13_ADVERTENCIAS.tsv"
        p_md = self.paths.run / "13_INFORME_VALIDACION_INTEGRAL.md"
        write_xlsx(p_xlsx, {"VALIDACIONES": pd.DataFrame(val_rows), "ERRORES": errors, "ADVERTENCIAS": warnings})
        write_tsv(p_err, errors)
        write_tsv(p_adv, warnings)
        write_md(
            p_md,
            [
                "# Validacion integral 5809 + 5810",
                "",
                f"Controles ejecutados: {len(val_rows)}.",
                f"Errores/bloqueos criticos: {len(errors)}.",
                "Carreras debe estar resuelto antes de Matricula; la validacion queda bloqueada por evidencia faltante.",
            ],
        )
        self.register(p_xlsx, p_err, p_adv, p_md)
        self.control("Fase 13", "BLOQUEADA_POR_EVIDENCIA_FALTANTE", [self.source_5809, PRECARGA_5810, DEPENDENCIAS_CARRERAS], [p_xlsx, p_err, p_adv, p_md], len(self.df5809), len(errors), len(errors), "Fase 14")

    def a14(self) -> None:
        rows = [
            {"ID_BLOQUEO": "BLQ001", "TIPO": "FUNCIONAL", "UNIVERSO": "15 planes / 42 filas Carreras", "MOTIVO": "Semantica NIVEL/distribucion anual no confirmada.", "ACCION": "Responder solicitud de periodizacion 15 planes.", "ESTADO": "PENDIENTE", "IMPACTO": "Bloquea Carreras final e integridad Matricula."},
            {"ID_BLOQUEO": "BLQ002", "TIPO": "INSTITUCIONAL", "UNIVERSO": "27 casos", "MOTIVO": "Periodizacion individual pendiente.", "ACCION": "Obtener reporte individual o tabla institucional.", "ESTADO": "PENDIENTE", "IMPACTO": "No permite conversiones especiales."},
            {"ID_BLOQUEO": "BLQ003", "TIPO": "INSTITUCIONAL", "UNIVERSO": "1008 casos identidad / 427 priorizados segun prompt", "MOTIVO": "Multiples CODCLI, contradicciones o sin identidad.", "ACCION": "Resolver trayectoria institucional.", "ESTADO": "PENDIENTE", "IMPACTO": "Puede impedir consulta de avance trazable."},
            {"ID_BLOQUEO": "BLQ004", "TIPO": "FUENTE", "UNIVERSO": "2371 filas", "MOTIVO": "Fuente academica avance 2025 no completamente materializada.", "ACCION": "Solicitar fuente avance 2025 validada.", "ESTADO": "PENDIENTE", "IMPACTO": "Bloquea curso y unidades anuales/acumuladas."},
            {"ID_BLOQUEO": "BLQ005", "TIPO": "TECNICO_FUNCIONAL", "UNIVERSO": "Campos 16-21", "MOTIVO": "Campos academicos vacios en precarga, dependientes de fuente externa.", "ACCION": "Completar solo con evidencia, llaves y reglas gobernadas.", "ESTADO": "PENDIENTE", "IMPACTO": "No permite SIES_READY."},
        ]
        bloqueos = pd.DataFrame(rows)
        decisiones = pd.DataFrame(
            [
                {"DECISION": "No generar SIES_READY", "FUNDAMENTO": "Persisten bloqueos criticos.", "ESTADO": "VIGENTE"},
                {"DECISION": "No generar candidato interno CSV", "FUNDAMENTO": "Campos obligatorios bloqueados; evitar confusion con archivo de carga.", "ESTADO": "VIGENTE"},
                {"DECISION": "Reutilizar gobernanza 29", "FUNDAMENTO": "2 adecuados, 27 pendientes, 0 rechazos definitivos.", "ESTADO": "VIGENTE"},
            ]
        )
        p_xlsx = self.paths.run / "14_EXPEDIENTE_BLOQUEOS_FINAL.xlsx"
        p_dec = self.paths.run / "14_DECISIONES_CIERRE.tsv"
        p_md = self.paths.run / "14_PENDIENTES_INSTITUCIONALES.md"
        write_xlsx(p_xlsx, {"BLOQUEOS": bloqueos, "DECISIONES": decisiones})
        write_tsv(p_dec, decisiones)
        write_md(
            p_md,
            [
                "# Pendientes institucionales",
                "",
                "1. Confirmar semantica NIVEL/distribucion anual de 15 planes.",
                "2. Resolver 27 reportes de periodizacion individual.",
                "3. Resolver identidad/trayectoria de casos priorizados.",
                "4. Entregar fuente academica de avance 2025 e historico acumulado con estados.",
                "5. Confirmar reglas operacionales para convalidaciones/reconocimientos segun anual/acumulado.",
            ],
        )
        self.register(p_xlsx, p_dec, p_md)
        self.control("Fase 14", "BLOQUEADA_POR_EVIDENCIA_FALTANTE", [DIAG_BRECHAS, EXP_29, IDENTIDAD], [p_xlsx, p_dec, p_md], len(self.df5809), len(bloqueos), len(bloqueos), "Fase 15 no ejecutable")

    def a15_skip(self) -> None:
        p_md = self.paths.run / "15_GENERACION_FINAL_NO_EJECUTADA.md"
        p_manifest = self.paths.run / "15_MANIFEST_FINAL_BLOQUEADO.json"
        write_md(
            p_md,
            [
                "# Generacion final no ejecutada",
                "",
                "Estado: BLOQUEADO_POR_EVIDENCIA_FALTANTE.",
                "No se genero 15_SIES_READY_5809.csv.",
                "No se genero 15_SIES_READY_5810.csv.",
                "No se ejecuto carga PES.",
                "",
                "Falta resolver: Carreras 15 planes, 27 periodizaciones, identidad/trayectoria, fuente avance 2025 e historico acumulado.",
            ],
        )
        write_json(
            p_manifest,
            {
                "estado": "BLOQUEADO_POR_EVIDENCIA_FALTANTE",
                "fecha": now_iso(),
                "sies_ready_generado": False,
                "csv_carga_generado": False,
                "carga_pes_realizada": False,
                "motivo": "Bloqueos criticos persistentes en campos obligatorios.",
            },
        )
        self.register(p_md, p_manifest)
        self.control("Fase 15", "BLOQUEADA_POR_EVIDENCIA_FALTANTE", [self.paths.run / "14_EXPEDIENTE_BLOQUEOS_FINAL.xlsx"], [p_md, p_manifest], len(self.df5809), 1, 5, "Resolver pendientes institucionales")

    def finalize(self) -> None:
        shutil.copy2(Path(__file__).resolve(), self.paths.audit / Path(__file__).name)
        self.register(self.paths.audit / Path(__file__).name)
        outputs = []
        for path in sorted(self.paths.run.rglob("*")):
            if path.is_file() and path.name != "MANIFEST_SALIDAS_GOBERNANZA_COLUMNAS.json":
                outputs.append({"RUTA": str(path), "SHA256": sha256(path), "TAMANO_BYTES": path.stat().st_size})
        manifest = self.paths.control / "MANIFEST_SALIDAS_GOBERNANZA_COLUMNAS.json"
        write_json(
            manifest,
            {
                "fecha": now_iso(),
                "estado": "BLOQUEADO_POR_EVIDENCIA_FALTANTE",
                "salidas": outputs,
                "fuentes_originales_modificadas": False,
                "csv_carga_generado": False,
                "sies_ready_generado": False,
            },
        )
        summary = {
            "fecha": now_iso(),
            "estado": "BLOQUEADO_POR_EVIDENCIA_FALTANTE",
            "run_dir": str(self.paths.run),
            "columnas_gobernadas": len(self.master) if not self.master.empty else 0,
            "registros_5809": len(self.df5809),
            "fuentes_originales_modificadas": False,
            "csv_carga_generado": False,
            "sies_ready_generado": False,
        }
        write_json(self.paths.control / "ESTADO_GOBERNANZA_COLUMNAS.json", summary)
        write_md(
            self.paths.control / "REANUDAR_DESDE_AQUI.md",
            [
                "# Reanudar gobernanza columnas 5809",
                "",
                f"Estado: {summary['estado']}",
                f"Ruta: {self.paths.run}",
                "",
                "Siguiente accion: resolver bloqueos institucionales documentados en 14_EXPEDIENTE_BLOQUEOS_FINAL.xlsx antes de ejecutar candidato o SIES_READY.",
            ],
        )
        outputs = []
        for path in sorted(self.paths.run.rglob("*")):
            if path.is_file() and path.name != "MANIFEST_SALIDAS_GOBERNANZA_COLUMNAS.json":
                outputs.append({"RUTA": str(path), "SHA256": sha256(path), "TAMANO_BYTES": path.stat().st_size})
        write_json(manifest, {**json.loads(manifest.read_text(encoding="utf-8")), "salidas": outputs})

    def run(self) -> None:
        self.a0()
        self.a1()
        self.run_blocks()
        self.a9()
        self.a10()
        self.a11()
        self.a12_skip()
        self.a13()
        self.a14()
        self.a15_skip()
        self.finalize()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", default=now_stamp())
    args = parser.parse_args()
    source_5809 = find_5809()
    run = ROOT_OUT / f"GOBERNANZA_COLUMNAS_5809_{args.timestamp}"
    paths = Paths(run=run, control=run / "00_CONTROL", audit=run / "99_AUDITORIA")
    paths.control.mkdir(parents=True, exist_ok=True)
    paths.audit.mkdir(parents=True, exist_ok=True)
    gov = Gobernanza5809(paths, source_5809)
    gov.run()
    print("BLOQUEADO_POR_EVIDENCIA_FALTANTE")
    print(f"Carpeta: {run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
