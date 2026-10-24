#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repositorio histórico SIES versionado.

Este módulo separa SIES del proceso dinámico de Caracterización. La ejecución
normal solo consume artefactos versionados ya materializados; la actualización
del histórico es una acción explícita y fuera del pipeline corriente.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent
SIES_REPOSITORY_DIR = REPO_ROOT / "gobernanza" / "sies"
SIES_MANIFEST_PATH = SIES_REPOSITORY_DIR / "HISTORICO_SIES_MANIFEST.json"
SIES_AGREGADOS_PATH = SIES_REPOSITORY_DIR / "HISTORICO_SIES_AGREGADOS.csv"
SIES_REQUIRED_MANIFEST_FIELDS = [
    "AÑO_INICIO_HISTORICO",
    "AÑO_FIN_HISTORICO",
    "VERSION_HISTORICA",
    "FECHA_ACTUALIZACION",
    "ARCHIVO_ORIGEN",
    "SHA256",
    "TOTAL_REGISTROS",
    "TOTAL_CARRERAS",
    "ESTADO",
]


@dataclass(frozen=True)
class SiesRepositorio:
    manifest: dict[str, Any]
    agregados: pd.DataFrame

    @property
    def version(self) -> str:
        return str(self.manifest.get("VERSION_HISTORICA", ""))


def norm_text_sies(value: Any) -> str:
    if value is None:
        return ""
    try:
        if bool(pd.isna(value)):
            return ""
    except (TypeError, ValueError):
        pass
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", str(value))
        if not unicodedata.combining(ch)
    ).upper().strip()
    return re.sub(r"\s+", " ", text)


def normalizar_codigo_sies(value: Any) -> str:
    text = norm_text_sies(value)
    if re.fullmatch(r"-?\d+\.0+", text):
        text = text.split(".", 1)[0]
    return re.sub(r"[^A-Z0-9]", "", text)


def normalizar_jornada_sies(value: Any) -> str:
    text = norm_text_sies(value)
    if not text:
        return "SIN INFORMACION"
    if "DISTANCIA" in text or text in {"ONLINE", "A DISTANCIA"}:
        return "DISTANCIA"
    if "SEMIPRESENCIAL" in text:
        return "SEMIPRESENCIAL"
    if "VESPERT" in text:
        return "VESPERTINA"
    if "DIUR" in text:
        return "DIURNA"
    return text


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolver_fuente_sies_default() -> Path | None:
    candidatos = [
        REPO_ROOT / "EXTRACCION_MATRICULA_SIES_2007_2025" / "salida" / "reporte_matricula_ip_san_sebastian.csv",
        REPO_ROOT / "EXTRACCION_MATRICULA_SIES _2007_2025" / "salida" / "reporte_matricula_ip_san_sebastian.csv",
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato
    encontrados = sorted(REPO_ROOT.glob("EXTRACCION_MATRICULA_SIES*_2007_2025/salida/reporte_matricula_ip_san_sebastian.csv"))
    return encontrados[0] if encontrados else None


def _serie(df: pd.DataFrame, column: str, default: str = "") -> pd.Series:
    if column in df.columns:
        return df[column]
    return pd.Series(default, index=df.index)


def construir_agregados_sies(df: pd.DataFrame) -> pd.DataFrame:
    work = pd.DataFrame(index=df.index)
    work["ANIO"] = pd.to_numeric(_serie(df, "cat_periodo"), errors="coerce")
    work["CODIGO_UNICO_SIES"] = _serie(df, "codigo_unico").map(normalizar_codigo_sies)
    work["COD_CARRERA_SIES"] = _serie(df, "cod_carrera").map(normalizar_codigo_sies)
    work["CARRERA_SIES"] = _serie(df, "nomb_carrera").map(lambda x: norm_text_sies(x) or "SIN INFORMACION")
    work["JORNADA"] = _serie(df, "jornada").map(normalizar_jornada_sies)
    work["MODALIDAD"] = _serie(df, "modalidad").map(lambda x: norm_text_sies(x) or "SIN INFORMACION")
    work["TIPO_PLAN"] = _serie(df, "tipo_plan_carr").map(lambda x: norm_text_sies(x) or "SIN INFORMACION")
    work["SEDE"] = _serie(df, "nomb_sede").map(lambda x: norm_text_sies(x) or "SIN INFORMACION")
    work["NIVEL_GLOBAL"] = _serie(df, "nivel_global").map(lambda x: norm_text_sies(x) or "SIN INFORMACION")
    work["VIGENCIA_CARRERA"] = _serie(df, "vigencia_carrera").map(lambda x: norm_text_sies(x) or "SIN INFORMACION")
    work = work[work["ANIO"].notna()].copy()
    if work.empty:
        return pd.DataFrame(
            columns=[
                "ANIO",
                "CODIGO_UNICO_SIES",
                "COD_CARRERA_SIES",
                "CARRERA_SIES",
                "JORNADA",
                "MODALIDAD",
                "TIPO_PLAN",
                "SEDE",
                "NIVEL_GLOBAL",
                "VIGENCIA_CARRERA",
                "REGISTROS_SIES",
            ]
        )
    work["ANIO"] = work["ANIO"].astype(int)
    return (
        work.groupby(
            [
                "ANIO",
                "CODIGO_UNICO_SIES",
                "COD_CARRERA_SIES",
                "CARRERA_SIES",
                "JORNADA",
                "MODALIDAD",
                "TIPO_PLAN",
                "SEDE",
                "NIVEL_GLOBAL",
                "VIGENCIA_CARRERA",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="REGISTROS_SIES")
        .sort_values(["ANIO", "CODIGO_UNICO_SIES", "JORNADA"], kind="stable")
        .reset_index(drop=True)
    )


def construir_repositorio_sies_desde_fuente(
    fuente: Path | None = None,
    *,
    version_historica: str | None = None,
    fecha_actualizacion: str | None = None,
    output_dir: Path | None = None,
) -> SiesRepositorio:
    """Materializa una versión histórica SIES.

    No debe llamarse desde el pipeline normal. Se usa únicamente cuando existe
    una actualización oficial SIES.
    """
    fuente = Path(fuente) if fuente is not None else resolver_fuente_sies_default()
    if fuente is None or not fuente.exists():
        raise FileNotFoundError("No se encontró fuente SIES oficial.")
    df = pd.read_csv(fuente, sep=",", encoding="utf-8-sig", dtype=str, keep_default_na=False, low_memory=False)
    agregados = construir_agregados_sies(df)
    anios = pd.to_numeric(df.get("cat_periodo", pd.Series(dtype="object")), errors="coerce").dropna()
    anio_inicio = int(anios.min()) if len(anios) else None
    anio_fin = int(anios.max()) if len(anios) else None
    version = version_historica or f"SIES_{anio_inicio}_{anio_fin}_v1"
    manifest = {
        "AÑO_INICIO_HISTORICO": anio_inicio,
        "AÑO_FIN_HISTORICO": anio_fin,
        "VERSION_HISTORICA": version,
        "FECHA_ACTUALIZACION": fecha_actualizacion or date.today().isoformat(),
        "ARCHIVO_ORIGEN": str(fuente),
        "SHA256": sha256_file(fuente),
        "TOTAL_REGISTROS": int(len(df)),
        "TOTAL_CARRERAS": int(df.get("codigo_unico", pd.Series(dtype="object")).replace("", pd.NA).nunique(dropna=True)),
        "ESTADO": "VIGENTE",
        "TIPO_COMPONENTE": "SIES_VERSIONADA_NO_DINAMICA",
        "NIVEL_ANALISIS": "AGREGADO_PROGRAMA_ANIO",
        "PROHIBE_IDENTIFICACION_PERSONAS": True,
    }
    destino = output_dir or SIES_REPOSITORY_DIR
    destino.mkdir(parents=True, exist_ok=True)
    (destino / SIES_MANIFEST_PATH.name).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    agregados.to_csv(destino / SIES_AGREGADOS_PATH.name, index=False, encoding="utf-8")
    return SiesRepositorio(manifest=manifest, agregados=agregados)


def cargar_repositorio_sies_versionado(
    *,
    manifest_path: Path = SIES_MANIFEST_PATH,
    agregados_path: Path = SIES_AGREGADOS_PATH,
) -> SiesRepositorio:
    manifest_path = Path(manifest_path)
    agregados_path = Path(agregados_path)
    if not manifest_path.exists():
        raise FileNotFoundError(f"No existe manifest histórico SIES versionado: {manifest_path}")
    if not agregados_path.exists():
        raise FileNotFoundError(f"No existe agregado histórico SIES versionado: {agregados_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    faltantes = [field for field in SIES_REQUIRED_MANIFEST_FIELDS if field not in manifest]
    if faltantes:
        raise ValueError(f"Manifest SIES incompleto; faltan campos: {faltantes}")
    agregados = pd.read_csv(agregados_path, dtype=str, keep_default_na=False)
    if "REGISTROS_SIES" in agregados.columns:
        agregados["REGISTROS_SIES"] = pd.to_numeric(agregados["REGISTROS_SIES"], errors="coerce").fillna(0).astype(int)
    if "ANIO" in agregados.columns:
        agregados["ANIO"] = pd.to_numeric(agregados["ANIO"], errors="coerce").astype("Int64")
    return SiesRepositorio(manifest=manifest, agregados=agregados)


def preparar_indicadores_sies(repo: SiesRepositorio) -> dict[str, pd.DataFrame]:
    agregados = repo.agregados.copy()
    total = int(agregados["REGISTROS_SIES"].sum()) if "REGISTROS_SIES" in agregados.columns else 0
    por_anio = (
        agregados.groupby("ANIO", dropna=False)
        .agg(
            REGISTROS_SIES=("REGISTROS_SIES", "sum"),
            CARRERAS_SIES=("CODIGO_UNICO_SIES", "nunique"),
            PROGRAMAS_SIES=("CARRERA_SIES", "nunique"),
        )
        .reset_index()
        if not agregados.empty
        else pd.DataFrame(columns=["ANIO", "REGISTROS_SIES", "CARRERAS_SIES", "PROGRAMAS_SIES"])
    )
    if not por_anio.empty:
        por_anio["PARTICIPACION_HISTORICA_PCT"] = (por_anio["REGISTROS_SIES"] / max(total, 1) * 100).round(2)
        por_anio["CRECIMIENTO_ABS"] = por_anio["REGISTROS_SIES"].diff().fillna(0).astype(int)
        por_anio["CRECIMIENTO_PCT"] = por_anio["REGISTROS_SIES"].pct_change().mul(100).round(2)
    manifest_df = pd.DataFrame(
        [{"CAMPO": key, "VALOR": value} for key, value in repo.manifest.items()]
    )
    indicadores = pd.DataFrame(
        [
            {"INDICADOR": "SIES_VERSION_UTILIZADA", "VALOR": repo.version},
            {"INDICADOR": "TOTAL_REGISTROS", "VALOR": repo.manifest.get("TOTAL_REGISTROS")},
            {"INDICADOR": "TOTAL_CARRERAS", "VALOR": repo.manifest.get("TOTAL_CARRERAS")},
            {"INDICADOR": "AÑO_INICIO_HISTORICO", "VALOR": repo.manifest.get("AÑO_INICIO_HISTORICO")},
            {"INDICADOR": "AÑO_FIN_HISTORICO", "VALOR": repo.manifest.get("AÑO_FIN_HISTORICO")},
            {"INDICADOR": "ESTADO", "VALOR": repo.manifest.get("ESTADO")},
            {"INDICADOR": "NIVEL_ANALISIS", "VALOR": "AGREGADO_PROGRAMA_ANIO"},
            {"INDICADOR": "IDENTIFICACION_PERSONAS", "VALOR": "NO_APLICA"},
        ]
    )
    return {
        "SIES_VERSION": manifest_df,
        "SIES_INDICADORES": indicadores,
        "SIES_AGREGADO_ANUAL": por_anio,
        "SIES_AGREGADO_PROGRAMA": agregados,
    }
