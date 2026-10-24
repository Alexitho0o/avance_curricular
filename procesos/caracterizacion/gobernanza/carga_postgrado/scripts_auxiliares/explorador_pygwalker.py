#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Explorador visual interno con PyGWalker para CARACTERIZACIÓN.

Este módulo es auxiliar y no altera el flujo productivo de `caracterizacion.py`.
Su foco es explorar de forma dinámica archivos Excel finales ya generados.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_EXPLORER_DIR = PROJECT_ROOT / "outputs" / "pygwalker"

FINAL_EXCEL_PRIORITY_PATTERNS = [
    "PREGRADO_TRAYECTORIA_CARACTERIZACION",
    "POSGRADO_DIPLOMADOS",
    "ENCUESTA_CARACTERIZACION",
    "CRUCE_SIES",
    "KPI_ACADEMICOS",
    "BD_Comunicaciones",
    "Estudiantes_pendientes",
    "Consolidado_eliminados_reporte",
    "Estudiantes_matriculados_Periodo",
]

SEARCH_DIR_PRIORITY = [
    "resultados",
    "output",
    "outputs",
    "reportes",
    "exportaciones",
    "informes",
    "archivos_generados",
]

SHEET_EXCLUDE_HINTS = {
    "readme",
    "auditoria",
    "auditoria_",
    "dashboard",
    "graficos",
    "graficos_",
    "imagenes",
    "instrucciones",
    "resumen visual",
    "portada",
    "configuracion",
    "control",
    "log",
}


@dataclass
class ExcelDetectionResult:
    ruta_excel: Optional[Path]
    nombre_archivo: Optional[str]
    carpeta: Optional[Path]
    fecha_modificacion: Optional[str]
    advertencias: list[str]
    motivo_seleccion: str
    candidatos: list[dict[str, Any]]


@dataclass
class SheetInfo:
    nombre_hoja: str
    filas: int
    columnas: int
    posible_tipo_hoja: str
    recomendada_para_pygwalker: bool
    motivo: str
    porcentaje_no_vacio_aprox: float
    advertencias: list[str]


def _timestamp_now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _normalize_text(text: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", text)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def _score_excel_candidate(path: Path) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    name = path.name
    parent_str = str(path.parent).lower()

    if name.startswith("~$"):
        return -9999, ["archivo temporal de Excel"]

    for idx, pattern in enumerate(FINAL_EXCEL_PRIORITY_PATTERNS):
        if pattern.lower() in name.lower():
            pattern_score = 100 - idx * 10
            score += pattern_score
            reasons.append(f"patron_prioritario:{pattern}(+{pattern_score})")

    for idx, folder_name in enumerate(SEARCH_DIR_PRIORITY):
        if f"/{folder_name.lower()}" in parent_str:
            folder_score = 30 - idx
            score += folder_score
            reasons.append(f"carpeta_prioritaria:{folder_name}(+{folder_score})")
            break

    if "archive" in parent_str:
        score -= 20
        reasons.append("carpeta_archive(-20)")
    if "backup" in parent_str:
        score -= 20
        reasons.append("carpeta_backup(-20)")

    # Penaliza archivos de extracción/insumo cuando no son libros finales del pipeline.
    if "reporte_filtrado" in name.lower() and not any(
        p.lower() in name.lower() for p in FINAL_EXCEL_PRIORITY_PATTERNS
    ):
        score -= 10
        reasons.append("insumo_auxiliar_probable(-10)")

    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0
    score += int(mtime // 1_000_000)
    reasons.append("preferencia_por_recencia")

    return score, reasons


def _try_open_excel(path: Path) -> tuple[bool, str]:
    """Valida si un archivo Excel es legible por pandas/openpyxl."""
    suffix = path.suffix.lower()
    try:
        if suffix in {".xlsx", ".xlsm"}:
            pd.ExcelFile(path, engine="openpyxl")
        elif suffix == ".xls":
            pd.ExcelFile(path)
        else:
            pd.ExcelFile(path)
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def detectar_excel_final_proyecto(project_root: Path | str | None = None) -> ExcelDetectionResult:
    """Detecta el Excel final más probable dentro del proyecto.

    Prioriza patrones de salida institucional y recencia de modificación.
    """
    root = Path(project_root).resolve() if project_root else PROJECT_ROOT
    advertencias: list[str] = []

    all_candidates = sorted(
        [
            p
            for p in root.rglob("*.xlsx")
            if p.is_file() and not p.name.startswith("~$")
        ]
        + [
            p
            for p in root.rglob("*.xlsm")
            if p.is_file() and not p.name.startswith("~$")
        ]
        + [
            p
            for p in root.rglob("*.xls")
            if p.is_file() and not p.name.startswith("~$")
        ]
    )

    if not all_candidates:
        return ExcelDetectionResult(
            ruta_excel=None,
            nombre_archivo=None,
            carpeta=None,
            fecha_modificacion=None,
            advertencias=[
                "No se encontraron archivos Excel dentro del proyecto.",
                "El flujo principal suele exportar a Desktop; genera una salida y vuelve a ejecutar.",
            ],
            motivo_seleccion="sin_candidatos",
            candidatos=[],
        )

    scored: list[tuple[int, Path, list[str]]] = []
    for path in all_candidates:
        is_ok, reason_open = _try_open_excel(path)
        if not is_ok:
            advertencias.append(f"Se descartó candidato no legible: {path} ({reason_open})")
            continue
        score, reasons = _score_excel_candidate(path)
        if score > -9999:
            scored.append((score, path, reasons))

    if not scored:
        return ExcelDetectionResult(
            ruta_excel=None,
            nombre_archivo=None,
            carpeta=None,
            fecha_modificacion=None,
            advertencias=advertencias + [
                "No hay candidatos Excel legibles dentro del proyecto.",
                "Genera una salida Excel válida del pipeline y vuelve a ejecutar.",
            ],
            motivo_seleccion="sin_candidatos_legibles",
            candidatos=[],
        )

    scored.sort(key=lambda x: x[0], reverse=True)

    top_score, top_path, top_reasons = scored[0]
    top_same = [item for item in scored if item[0] == top_score]

    if len(top_same) > 1:
        advertencias.append(
            f"Hay {len(top_same)} candidatos con el mismo puntaje máximo. Se seleccionó el más reciente por orden de evaluación."
        )

    if len(scored) > 1:
        advertencias.append(f"Se detectaron {len(scored)} candidatos Excel en total.")

    try:
        mtime_str = datetime.fromtimestamp(top_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except OSError:
        mtime_str = "desconocida"

    return ExcelDetectionResult(
        ruta_excel=top_path,
        nombre_archivo=top_path.name,
        carpeta=top_path.parent,
        fecha_modificacion=mtime_str,
        advertencias=advertencias,
        motivo_seleccion="; ".join(top_reasons),
        candidatos=[
            {
                "ruta": str(path),
                "nombre": path.name,
                "puntaje": score,
                "motivos": reasons,
            }
            for score, path, reasons in scored[:20]
        ],
    )


def _infer_sheet_type(sheet_name: str, rows: int, cols: int, non_empty_ratio: float) -> tuple[str, bool, str]:
    normalized = _normalize_text(sheet_name)
    has_exclude_hint = any(hint in normalized for hint in SHEET_EXCLUDE_HINTS)

    is_tabular_shape = rows >= 5 and cols >= 3 and non_empty_ratio >= 0.08

    if has_exclude_hint and not is_tabular_shape:
        return "no_tabular_o_control", False, "Nombre sugiere hoja de control/dashboard y estructura poco tabular"

    if has_exclude_hint and is_tabular_shape:
        return "tabular_con_nombre_sensible", True, "Nombre sugiere control, pero la estructura parece tabular útil"

    if rows == 0 or cols == 0:
        return "vacia", False, "Hoja vacía"

    if not is_tabular_shape:
        return "tabular_debil", False, "Estructura tabular insuficiente para exploración visual"

    return "tabular", True, "Estructura tabular apta para PyGWalker"


def listar_hojas_excel(ruta_excel: Path | str) -> list[SheetInfo]:
    """Lista hojas del Excel y clasifica su aptitud para PyGWalker."""
    path = Path(ruta_excel).expanduser().resolve()
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm"}:
        xls = pd.ExcelFile(path, engine="openpyxl")
    else:
        xls = pd.ExcelFile(path)
    resultado: list[SheetInfo] = []

    for hoja in xls.sheet_names:
        advertencias: list[str] = []
        try:
            if suffix in {".xlsx", ".xlsm"}:
                df = pd.read_excel(path, sheet_name=hoja, engine="openpyxl")
            else:
                df = pd.read_excel(path, sheet_name=hoja)
        except Exception as exc:
            resultado.append(
                SheetInfo(
                    nombre_hoja=hoja,
                    filas=0,
                    columnas=0,
                    posible_tipo_hoja="error_lectura",
                    recomendada_para_pygwalker=False,
                    motivo=f"No se pudo leer la hoja: {exc}",
                    porcentaje_no_vacio_aprox=0.0,
                    advertencias=["Error de lectura de hoja"],
                )
            )
            continue

        filas, columnas = df.shape
        total_celdas = max(1, filas * max(1, columnas))
        celdas_no_vacias = int(df.notna().sum().sum()) if filas and columnas else 0
        non_empty_ratio = round(celdas_no_vacias / total_celdas, 4)

        tipo, recomendada, motivo = _infer_sheet_type(hoja, filas, columnas, non_empty_ratio)

        if filas == 0 or columnas == 0:
            advertencias.append("Hoja sin contenido tabular utilizable")
        if filas < 10:
            advertencias.append("Pocas filas para exploración robusta")

        resultado.append(
            SheetInfo(
                nombre_hoja=hoja,
                filas=filas,
                columnas=columnas,
                posible_tipo_hoja=tipo,
                recomendada_para_pygwalker=recomendada,
                motivo=motivo,
                porcentaje_no_vacio_aprox=non_empty_ratio * 100,
                advertencias=advertencias,
            )
        )

    return resultado


def _choose_best_sheet(sheet_info_list: list[SheetInfo]) -> Optional[SheetInfo]:
    if not sheet_info_list:
        return None

    recommended = [s for s in sheet_info_list if s.recomendada_para_pygwalker]
    pool = recommended if recommended else sheet_info_list

    pool = sorted(
        pool,
        key=lambda s: (s.filas * max(1, s.columnas), s.porcentaje_no_vacio_aprox, s.filas),
        reverse=True,
    )
    return pool[0] if pool else None


def _normalize_columns_in_memory(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    out = df.copy()

    out = out.dropna(axis=0, how="all")
    out = out.dropna(axis=1, how="all")

    new_cols: list[str] = []
    seen: dict[str, int] = {}

    for idx, col in enumerate(out.columns, start=1):
        name = "" if col is None else str(col).strip()
        if not name:
            name = f"COL_{idx}"
            warnings.append("Se normalizaron columnas vacías en memoria")
        name = re.sub(r"\s+", "_", name)
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
            warnings.append("Se normalizaron columnas duplicadas en memoria")
        else:
            seen[name] = 1
        new_cols.append(name)

    out.columns = new_cols
    return out, warnings


def cargar_hoja_para_pygwalker(
    ruta_excel: Path | str,
    hoja: Optional[str] = None,
) -> tuple[pd.DataFrame, str, dict[str, Any]]:
    """Carga una hoja para exploración visual sin alterar el Excel original."""
    path = Path(ruta_excel).expanduser().resolve()
    sheet_info_list = listar_hojas_excel(path)

    if hoja is None:
        best = _choose_best_sheet(sheet_info_list)
        if best is None:
            raise ValueError("No se encontró hoja apta para cargar.")
        hoja_seleccionada = best.nombre_hoja
        criterio = "auto"
    else:
        hoja_seleccionada = hoja
        criterio = "manual"

    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm"}:
        df_raw = pd.read_excel(path, sheet_name=hoja_seleccionada, engine="openpyxl")
    else:
        df_raw = pd.read_excel(path, sheet_name=hoja_seleccionada)
    df_clean, clean_warn = _normalize_columns_in_memory(df_raw)

    reporte = {
        "ruta_excel": str(path),
        "hoja_seleccionada": hoja_seleccionada,
        "criterio_seleccion": criterio,
        "filas_originales": int(df_raw.shape[0]),
        "columnas_originales": int(df_raw.shape[1]),
        "filas_cargadas": int(df_clean.shape[0]),
        "columnas_cargadas": int(df_clean.shape[1]),
        "advertencias": clean_warn,
    }

    return df_clean, hoja_seleccionada, reporte


def detectar_dataframe_principal_desde_codigo(
    ruta_script_principal: Path | str | None = None,
) -> dict[str, Any]:
    """Detección opcional y no intrusiva de DataFrames relevantes desde código.

    No modifica el flujo ni ejecuta el script principal. Solo inspecciona texto.
    """
    script = Path(ruta_script_principal).resolve() if ruta_script_principal else PROJECT_ROOT / "caracterizacion.py"
    if not script.exists():
        return {
            "implementado": False,
            "motivo": "No existe caracterizacion.py en la ruta esperada.",
            "hallazgos": [],
        }

    text = script.read_text(encoding="utf-8", errors="ignore")
    # Heurística simple: asignaciones tipo df_* =
    names = sorted(set(re.findall(r"\b(df_[a-zA-Z0-9_]+)\s*=", text)))
    relevantes = [n for n in names if any(k in n for k in ["kpi", "resumen", "tray", "encuesta", "cruce", "pg", "persona"])]

    return {
        "implementado": True,
        "motivo": "Detección heurística estática (sin ejecutar flujo productivo).",
        "hallazgos": relevantes[:150],
        "total_detectados": len(names),
    }


def perfil_basico_dataframe_para_pygwalker(df: pd.DataFrame) -> dict[str, Any]:
    """Perfila estructura básica del DataFrame para exploración visual."""
    if df.empty:
        return {
            "filas": 0,
            "columnas": 0,
            "tipos": {},
            "nulos_por_columna": {},
            "porcentaje_nulos_por_columna": {},
            "valores_unicos": {},
            "columnas_numericas": [],
            "columnas_categoricas": [],
            "columnas_fecha": [],
            "columnas_binarias": [],
            "columnas_texto_largo": [],
            "columnas_segmentacion_sugeridas": [],
            "columnas_graficos_sugeridas": [],
            "columnas_problematicas": [],
        }

    n_rows = int(df.shape[0])
    n_cols = int(df.shape[1])

    tipos = {c: str(t) for c, t in df.dtypes.items()}
    nulos = {c: int(v) for c, v in df.isna().sum().items()}
    pct_nulos = {c: round((nulos[c] / n_rows) * 100, 2) if n_rows else 0.0 for c in df.columns}
    unicos = {c: int(df[c].nunique(dropna=True)) for c in df.columns}

    numeric_cols = list(df.select_dtypes(include=["number", "float", "int"]).columns)
    datetime_cols = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)

    categorical_cols: list[str] = []
    binary_cols: list[str] = []
    long_text_cols: list[str] = []
    problematic_cols: list[str] = []

    for col in df.columns:
        unique_count = unicos[col]
        ratio_unique = unique_count / n_rows if n_rows else 0

        if unique_count <= 2:
            binary_cols.append(col)

        if col not in numeric_cols and col not in datetime_cols:
            categorical_cols.append(col)

        sample = df[col].dropna().astype(str).head(500)
        mean_len = float(sample.map(len).mean()) if len(sample) else 0.0
        if mean_len >= 80:
            long_text_cols.append(col)

        if ratio_unique > 0.9 and col not in datetime_cols and col not in numeric_cols:
            problematic_cols.append(f"{col}: alta_cardinalidad")
        if col in long_text_cols:
            problematic_cols.append(f"{col}: texto_largo")
        if pct_nulos[col] > 70:
            problematic_cols.append(f"{col}: alto_nulo({pct_nulos[col]}%)")

    segment_suggested = [c for c in categorical_cols if 2 < unicos[c] <= 30]
    chart_suggested = numeric_cols[:]
    chart_suggested.extend([c for c in categorical_cols if 2 <= unicos[c] <= 20][:10])

    return {
        "filas": n_rows,
        "columnas": n_cols,
        "tipos": tipos,
        "nulos_por_columna": nulos,
        "porcentaje_nulos_por_columna": pct_nulos,
        "valores_unicos": unicos,
        "columnas_numericas": numeric_cols,
        "columnas_categoricas": categorical_cols,
        "columnas_fecha": datetime_cols,
        "columnas_binarias": binary_cols,
        "columnas_texto_largo": long_text_cols,
        "columnas_segmentacion_sugeridas": segment_suggested,
        "columnas_graficos_sugeridas": chart_suggested,
        "columnas_problematicas": sorted(set(problematic_cols)),
    }


def seleccionar_muestra_para_pygwalker(df: pd.DataFrame, max_filas: int = 5000) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Devuelve muestra controlada si el DataFrame es grande."""
    total = len(df)
    if total <= max_filas:
        return df.copy(), {
            "se_uso_muestra": False,
            "criterio": "completo",
            "filas_originales": int(total),
            "filas_usadas": int(total),
        }

    sample = df.head(max_filas).copy()
    return sample, {
        "se_uso_muestra": True,
        "criterio": "primeras_filas",
        "filas_originales": int(total),
        "filas_usadas": int(len(sample)),
        "max_filas": int(max_filas),
    }


def explorar_con_pygwalker(df: pd.DataFrame, titulo: Optional[str] = None, max_filas: int = 5000) -> dict[str, Any]:
    """Abre PyGWalker cuando el entorno lo permite (modo analista)."""
    if df.empty:
        return {
            "ok": False,
            "mensaje": "DataFrame vacío. No se abre PyGWalker.",
            "advertencias": ["DataFrame sin filas"],
        }

    try:
        import pygwalker as pyg  # type: ignore
    except Exception as exc:
        return {
            "ok": False,
            "mensaje": "PyGWalker no está instalado. Instala con: pip install pygwalker",
            "advertencias": [str(exc)],
        }

    df_view, sample_info = seleccionar_muestra_para_pygwalker(df, max_filas=max_filas)
    title = titulo or "Exploracion interna CARACTERIZACION"

    # Evita bloquear en terminal no interactiva.
    interactive_shell = bool(getattr(sys, "ps1", None))
    has_ipython = "IPython" in sys.modules
    if not interactive_shell and not has_ipython:
        return {
            "ok": False,
            "mensaje": "Entorno no interactivo detectado. Usa notebook/VS Code interactive para abrir PyGWalker.",
            "advertencias": ["No se abrió interfaz para no bloquear ejecución"],
            "muestra": sample_info,
        }

    try:
        walker_obj = pyg.walk(df_view)
        return {
            "ok": True,
            "mensaje": "PyGWalker abierto en modo analista.",
            "titulo": title,
            "muestra": sample_info,
            "walker_obj": walker_obj,
        }
    except Exception as exc:
        return {
            "ok": False,
            "mensaje": "Error al abrir PyGWalker.",
            "advertencias": [str(exc)],
            "trace": traceback.format_exc(limit=3),
            "muestra": sample_info,
        }


def exportar_pygwalker_html(
    df: pd.DataFrame,
    ruta_salida_html: Optional[Path | str] = None,
    titulo: Optional[str] = None,
    max_filas: int = 5000,
) -> dict[str, Any]:
    """Exporta HTML de PyGWalker cuando la API instalada lo permite."""
    if df.empty:
        return {"ok": False, "mensaje": "DataFrame vacío. No se exporta HTML."}

    try:
        import pygwalker as pyg  # type: ignore
    except Exception as exc:
        return {
            "ok": False,
            "mensaje": "PyGWalker no instalado. No se exporta HTML.",
            "advertencias": [str(exc)],
        }

    out_dir = DEFAULT_EXPLORER_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if ruta_salida_html is None:
        base = re.sub(r"[^A-Za-z0-9_\-]+", "_", (titulo or "exploracion").strip())[:80] or "exploracion"
        html_path = out_dir / f"pygwalker_{base}_{_timestamp_now()}.html"
    else:
        html_path = Path(ruta_salida_html)
        if not html_path.is_absolute():
            html_path = out_dir / html_path
        html_path.parent.mkdir(parents=True, exist_ok=True)

    df_view, sample_info = seleccionar_muestra_para_pygwalker(df, max_filas=max_filas)

    html_text: Optional[str] = None
    warnings: list[str] = []

    # Estrategias tolerantes a diferencias de API entre versiones.
    if hasattr(pyg, "to_html"):
        try:
            html_text = pyg.to_html(df_view)
        except Exception as exc:
            warnings.append(f"pyg.to_html falló: {exc}")

    if html_text is None and hasattr(pyg, "walk"):
        try:
            maybe_html = pyg.walk(df_view, return_html=True)  # algunas versiones lo soportan
            if isinstance(maybe_html, str) and "<html" in maybe_html.lower():
                html_text = maybe_html
        except Exception as exc:
            warnings.append(f"pyg.walk(return_html=True) no disponible: {exc}")

    if html_text is None:
        return {
            "ok": False,
            "mensaje": "La versión instalada de PyGWalker no expone una API HTML compatible.",
            "advertencias": warnings,
            "muestra": sample_info,
        }

    html_path.write_text(html_text, encoding="utf-8")
    return {
        "ok": True,
        "mensaje": "HTML de exploración generado.",
        "ruta_html": str(html_path.resolve()),
        "advertencias": warnings,
        "muestra": sample_info,
    }


def generar_reporte_exploracion_pygwalker(
    *,
    project_root: Path,
    excel_detectado: Optional[Path],
    hoja_explorada: Optional[str],
    perfil_df: dict[str, Any],
    criterios_seleccion: dict[str, Any],
    html_result: Optional[dict[str, Any]] = None,
    advertencias: Optional[list[str]] = None,
    errores: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Genera reporte de auditoría simple de exploración en Markdown y JSON."""
    out_dir = DEFAULT_EXPLORER_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = _timestamp_now()
    md_path = out_dir / f"reporte_exploracion_pygwalker_{ts}.md"
    json_path = out_dir / f"reporte_exploracion_pygwalker_{ts}.json"

    cols_nulos_altos = [
        c for c, p in perfil_df.get("porcentaje_nulos_por_columna", {}).items() if p >= 50
    ]

    payload = {
        "fecha_exploracion": datetime.now().isoformat(timespec="seconds"),
        "ruta_proyecto": str(project_root.resolve()),
        "archivo_explorado": str(excel_detectado.resolve()) if excel_detectado else None,
        "hoja_explorada": hoja_explorada,
        "filas_dataframe": perfil_df.get("filas"),
        "columnas_dataframe": perfil_df.get("columnas"),
        "columnas_detectadas": list(perfil_df.get("tipos", {}).keys()),
        "columnas_numericas": perfil_df.get("columnas_numericas", []),
        "columnas_categoricas": perfil_df.get("columnas_categoricas", []),
        "columnas_fecha": perfil_df.get("columnas_fecha", []),
        "columnas_nulos_altos": cols_nulos_altos,
        "columnas_alta_cardinalidad_o_problematicas": perfil_df.get("columnas_problematicas", []),
        "columnas_excluidas_sugeridas": [
            c for c in perfil_df.get("columnas_problematicas", []) if "alta_cardinalidad" in c or "texto_largo" in c
        ],
        "ruta_html_generado": (html_result or {}).get("ruta_html"),
        "criterios_seleccion": criterios_seleccion,
        "advertencias": advertencias or [],
        "errores_controlados": errores or [],
        "proximos_pasos_sugeridos": [
            "Revisar combinaciones de columnas de segmentación y métricas numéricas.",
            "Usar hallazgos para fortalecer gráficos del Excel final institucional.",
            "No sustituir reportes productivos por salidas PyGWalker.",
        ],
    }

    lines = [
        "# Reporte de Exploración PyGWalker",
        "",
        f"- Fecha: {payload['fecha_exploracion']}",
        f"- Proyecto: {payload['ruta_proyecto']}",
        f"- Archivo explorado: {payload['archivo_explorado']}",
        f"- Hoja explorada: {payload['hoja_explorada']}",
        f"- Filas: {payload['filas_dataframe']}",
        f"- Columnas: {payload['columnas_dataframe']}",
        f"- Ruta HTML generado: {payload['ruta_html_generado']}",
        "",
        "## Columnas detectadas",
        ", ".join(payload["columnas_detectadas"][:200]) if payload["columnas_detectadas"] else "(sin columnas)",
        "",
        "## Advertencias",
    ]

    if payload["advertencias"]:
        lines.extend([f"- {w}" for w in payload["advertencias"]])
    else:
        lines.append("- (sin advertencias)")

    lines.extend([
        "",
        "## Errores controlados",
    ])

    if payload["errores_controlados"]:
        lines.extend([f"- {e}" for e in payload["errores_controlados"]])
    else:
        lines.append("- (sin errores)")

    lines.extend([
        "",
        "## Próximos pasos sugeridos",
    ])
    lines.extend([f"- {s}" for s in payload["proximos_pasos_sugeridos"]])

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ruta_reporte_md": str(md_path.resolve()),
        "ruta_reporte_json": str(json_path.resolve()),
        "payload": payload,
    }


def _sheet_info_to_dataframe(sheet_info: list[SheetInfo]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "nombre_hoja": s.nombre_hoja,
                "filas": s.filas,
                "columnas": s.columnas,
                "posible_tipo_hoja": s.posible_tipo_hoja,
                "recomendada_para_pygwalker": s.recomendada_para_pygwalker,
                "motivo": s.motivo,
                "porcentaje_no_vacio_aprox": s.porcentaje_no_vacio_aprox,
                "advertencias": " | ".join(s.advertencias),
            }
            for s in sheet_info
        ]
    )


def main() -> int:
    """Entrada CLI para modo analista."""
    parser = argparse.ArgumentParser(
        description="Exploración visual interna con PyGWalker para CARACTERIZACIÓN"
    )
    parser.add_argument("--excel", dest="excel", default=None, help="Ruta de Excel a explorar")
    parser.add_argument("--hoja", dest="hoja", default=None, help="Nombre de hoja a cargar")
    parser.add_argument("--max-filas", dest="max_filas", type=int, default=5000, help="Máximo de filas para exploración")
    parser.add_argument("--abrir", dest="abrir", action="store_true", help="Intenta abrir PyGWalker interactivamente")
    parser.add_argument("--sin-html", dest="sin_html", action="store_true", help="No intentar exportación HTML")
    args = parser.parse_args()

    print("[PyGWalker] Proyecto:", PROJECT_ROOT)

    errores: list[str] = []
    advertencias: list[str] = []

    if args.excel:
        ruta_excel = Path(args.excel).expanduser().resolve()
        detect_res = ExcelDetectionResult(
            ruta_excel=ruta_excel,
            nombre_archivo=ruta_excel.name,
            carpeta=ruta_excel.parent,
            fecha_modificacion=datetime.fromtimestamp(ruta_excel.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if ruta_excel.exists()
            else None,
            advertencias=[],
            motivo_seleccion="forzado_por_parametro_cli",
            candidatos=[{"ruta": str(ruta_excel), "nombre": ruta_excel.name, "puntaje": None}],
        )
    else:
        detect_res = detectar_excel_final_proyecto(PROJECT_ROOT)
        advertencias.extend(detect_res.advertencias)

    if not detect_res.ruta_excel or not detect_res.ruta_excel.exists():
        print("[PyGWalker][WARN] No se detectó Excel apto dentro del proyecto.")
        for w in detect_res.advertencias:
            print(f"[PyGWalker][WARN] {w}")
        # Reporte mínimo aun sin Excel.
        rep = generar_reporte_exploracion_pygwalker(
            project_root=PROJECT_ROOT,
            excel_detectado=None,
            hoja_explorada=None,
            perfil_df={},
            criterios_seleccion={"excel": "sin_candidatos"},
            html_result=None,
            advertencias=advertencias,
            errores=errores,
        )
        print("[PyGWalker] Reporte generado:", rep["ruta_reporte_md"])
        return 0

    print(f"[PyGWalker] Excel detectado: {detect_res.ruta_excel}")
    print(f"[PyGWalker] Motivo selección: {detect_res.motivo_seleccion}")

    try:
        info_hojas = listar_hojas_excel(detect_res.ruta_excel)
    except Exception as exc:
        errores.append(f"Error al listar hojas: {exc}")
        rep = generar_reporte_exploracion_pygwalker(
            project_root=PROJECT_ROOT,
            excel_detectado=detect_res.ruta_excel,
            hoja_explorada=None,
            perfil_df={},
            criterios_seleccion={"excel": detect_res.motivo_seleccion},
            html_result=None,
            advertencias=advertencias,
            errores=errores,
        )
        print("[PyGWalker][ERROR]", exc)
        print("[PyGWalker] Reporte generado:", rep["ruta_reporte_md"])
        return 1

    df_hojas = _sheet_info_to_dataframe(info_hojas)
    print("[PyGWalker] Resumen de hojas (top 10):")
    if not df_hojas.empty:
        print(df_hojas.head(10).to_string(index=False))

    try:
        df, hoja_sel, rep_carga = cargar_hoja_para_pygwalker(detect_res.ruta_excel, hoja=args.hoja)
    except Exception as exc:
        errores.append(f"Error al cargar hoja: {exc}")
        rep = generar_reporte_exploracion_pygwalker(
            project_root=PROJECT_ROOT,
            excel_detectado=detect_res.ruta_excel,
            hoja_explorada=None,
            perfil_df={},
            criterios_seleccion={"excel": detect_res.motivo_seleccion, "hoja": "fallida"},
            html_result=None,
            advertencias=advertencias,
            errores=errores,
        )
        print("[PyGWalker][ERROR]", exc)
        print("[PyGWalker] Reporte generado:", rep["ruta_reporte_md"])
        return 1

    print(f"[PyGWalker] Hoja seleccionada: {hoja_sel}")
    print(f"[PyGWalker] Shape cargado: {df.shape[0]} filas x {df.shape[1]} columnas")

    perfil = perfil_basico_dataframe_para_pygwalker(df)

    html_result: dict[str, Any] | None = None
    if not args.sin_html:
        titulo_html = f"Exploracion_{detect_res.nombre_archivo}_{hoja_sel}"
        html_result = exportar_pygwalker_html(df, titulo=titulo_html, max_filas=args.max_filas)
        if html_result.get("ok"):
            print("[PyGWalker] HTML generado:", html_result.get("ruta_html"))
        else:
            for w in html_result.get("advertencias", []):
                advertencias.append(str(w))
            advertencias.append(str(html_result.get("mensaje", "No se generó HTML")))

    if args.abrir:
        open_result = explorar_con_pygwalker(df, titulo=f"{detect_res.nombre_archivo}::{hoja_sel}", max_filas=args.max_filas)
        if not open_result.get("ok"):
            advertencias.extend(open_result.get("advertencias", []))
            advertencias.append(str(open_result.get("mensaje", "No se abrió PyGWalker")))

    report = generar_reporte_exploracion_pygwalker(
        project_root=PROJECT_ROOT,
        excel_detectado=detect_res.ruta_excel,
        hoja_explorada=hoja_sel,
        perfil_df=perfil,
        criterios_seleccion={
            "excel": detect_res.motivo_seleccion,
            "hoja": rep_carga,
            "candidatos_excel": detect_res.candidatos,
        },
        html_result=html_result,
        advertencias=advertencias,
        errores=errores,
    )

    print("[PyGWalker] Reporte Markdown:", report["ruta_reporte_md"])
    print("[PyGWalker] Reporte JSON:", report["ruta_reporte_json"])

    if not args.abrir:
        print("[PyGWalker] Para abrir interfaz interactiva, ejecuta con --abrir en notebook/entorno compatible.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
