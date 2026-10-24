#!/usr/bin/env python3
"""
Validación pospublicación del Bloque 13:
Proveniencia y Trayectorias Formativas.
Principios:
1. No fija cantidades institucionales variables.
2. Deriva el universo desde DETALLE_MATRICULA.
3. Controla cardinalidad, llaves, niveles y hojas derivadas.
4. Verifica QA_COBERTURA y RESUMEN_KPI.
5. No modifica el archivo de origen.
6. No vuelve a ejecutar el pipeline.
7. Genera auditoría reproducible dentro de .local/.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd
REQUIRED_SHEETS = {
    "RESUMEN_KPI",
    "DETALLE_MATRICULA",
    "PROVENIENCIA_EMTP",
    "PROVENIENCIA_CFT",
    "INGRESO_PROFESIONAL",
    "SALIDA_INTERMEDIA",
    "TECNICO_A_PROFESIONAL",
    "DIPLOMADOS",
    "QA_COBERTURA",
    "DEFINICIONES",
}
KEY_CANDIDATES = (
    "_LLAVE_CODCLI",
    "CODCLI",
    "CODCLI_NORMALIZADO",
)
LEVEL_CANDIDATES = (
    "_NIVEL_PROGRAMA",
    "NIVEL_PROGRAMA",
    "CLASIFICACION_NIVEL_PROGRAMA",
    "NIVEL_CARRERA",
    "NIVEL",
)
ALLOWED_LEVELS = {
    "TECNICO",
    "PROFESIONAL",
}
AFFIRMATIVE_VALUES = {
    "SI",
    "SÍ",
    "TRUE",
    "1",
    "1.0",
    "X",
}
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Valida dinámicamente la salida pospublicación "
            "del Bloque 13."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Ruta raíz del repositorio.",
    )
    parser.add_argument(
        "--archivo",
        type=Path,
        help="Ruta explícita al Excel del Bloque 13.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Directorio de una ejecución específica.",
    )
    parser.add_argument(
        "--onedrive-root",
        type=Path,
        help=(
            "Ruta raíz de 0_caracterizacion. "
            "Si se omite, se descubre automáticamente."
        ),
    )
    parser.add_argument(
        "--anio",
        type=int,
        help="Año solicitado.",
    )
    parser.add_argument(
        "--periodo",
        type=int,
        help="Período solicitado.",
    )
    parser.add_argument(
        "--require-clean-git",
        action="store_true",
        help=(
            "Exige repositorio limpio, sincronizado "
            "y sin divergencia."
        ),
    )
    parser.add_argument(
        "--auditoria",
        type=Path,
        help=(
            "Directorio de auditoría explícito. "
            "Si se omite, se genera uno automáticamente."
        ),
    )
    return parser.parse_args()
def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    replacements = {
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "Ü": "U",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"\s+", " ", text)
    return text
def normalize_key(series: pd.Series) -> pd.Series:
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\.0$", "", regex=True)
    )
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)
    return digest.hexdigest()
def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
def discover_onedrive_root() -> Path:
    cloud_root = (
        Path.home()
        / "Library"
        / "CloudStorage"
    )
    candidates = sorted(
        cloud_root.glob(
            "OneDrive-InstitutoProfesionalSanSebasti*/"
            "0_caracterizacion"
        )
    )
    candidates = [
        path
        for path in candidates
        if path.is_dir()
    ]
    if not candidates:
        raise FileNotFoundError(
            "No se encontró automáticamente "
            "0_caracterizacion dentro de OneDrive."
        )
    if len(candidates) > 1:
        rendered = "\n".join(
            f"  - {path}"
            for path in candidates
        )
        raise RuntimeError(
            "Se encontró más de una carpeta candidata:\n"
            f"{rendered}\n"
            "Use --onedrive-root para seleccionar una."
        )
    return candidates[0]
def extract_run_order(path: Path) -> tuple[int, str]:
    run_dir = path.parent.parent
    date_dir = run_dir.parent.name
    run_match = re.fullmatch(
        r"(\d{4})_P(\d+)_(\d{6})",
        run_dir.name,
    )
    date_match = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})",
        date_dir,
    )
    if run_match and date_match:
        date_value = "".join(date_match.groups())
        time_value = run_match.group(3)
        try:
            return (
                int(f"{date_value}{time_value}"),
                str(path),
            )
        except ValueError:
            pass
    try:
        return (
            int(path.stat().st_mtime_ns),
            str(path),
        )
    except OSError:
        return (0, str(path))
def discover_b13_file(
    onedrive_root: Path,
    anio: int | None,
    periodo: int | None,
) -> Path:
    if anio is not None and periodo is not None:
        filename_pattern = (
            "INDICADORES_TRAYECTORIAS_FORMATIVAS_"
            f"{anio}_P{periodo}_*.xlsx"
        )
    elif anio is not None:
        filename_pattern = (
            "INDICADORES_TRAYECTORIAS_FORMATIVAS_"
            f"{anio}_P*_*.xlsx"
        )
    else:
        filename_pattern = (
            "INDICADORES_TRAYECTORIAS_FORMATIVAS_"
            "*_P*_*.xlsx"
        )
    candidates = list(
        onedrive_root.glob(
            f"*/**/02_SALIDAS/{filename_pattern}"
        )
    )
    candidates = [
        path
        for path in candidates
        if path.is_file()
        and not path.name.startswith("~$")
    ]
    if periodo is not None:
        period_token = f"_P{periodo}_"
        candidates = [
            path
            for path in candidates
            if period_token in path.name
        ]
    if not candidates:
        raise FileNotFoundError(
            "No se encontró ningún archivo "
            "INDICADORES_TRAYECTORIAS_FORMATIVAS "
            "para los filtros solicitados."
        )
    return max(
        candidates,
        key=extract_run_order,
    )
def locate_b13_file(
    args: argparse.Namespace,
) -> Path:
    if args.archivo is not None:
        return args.archivo.expanduser().resolve()
    if args.run_dir is not None:
        run_dir = args.run_dir.expanduser().resolve()
        output_dir = run_dir / "02_SALIDAS"
        candidates = sorted(
            output_dir.glob(
                "INDICADORES_TRAYECTORIAS_FORMATIVAS_"
                "*_P*_*.xlsx"
            )
        )
        candidates = [
            path
            for path in candidates
            if path.is_file()
            and not path.name.startswith("~$")
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                "Se esperaba exactamente un archivo "
                f"de Bloque 13 en {output_dir}; "
                f"se encontraron {len(candidates)}."
            )
        return candidates[0].resolve()
    onedrive_root = (
        args.onedrive_root.expanduser().resolve()
        if args.onedrive_root is not None
        else discover_onedrive_root()
    )
    return discover_b13_file(
        onedrive_root=onedrive_root,
        anio=args.anio,
        periodo=args.periodo,
    ).resolve()
def determine_column(
    columns: pd.Index,
    candidates: tuple[str, ...],
    label: str,
) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise KeyError(
        f"No se encontró {label}. "
        f"Columnas disponibles: {list(columns)}"
    )
def identify_child_key(
    child: pd.DataFrame,
    preferred_key: str,
) -> str | None:
    if preferred_key in child.columns:
        return preferred_key
    for candidate in KEY_CANDIDATES:
        if candidate in child.columns:
            return candidate
    return None
def compare_key_subset(
    child: pd.DataFrame,
    child_name: str,
    parent_keys: set[str],
    preferred_key: str,
    errors: list[str],
    warnings: list[str],
    *,
    outside_is_error: bool = True,
    duplicated_is_error: bool = True,
) -> dict[str, Any]:
    child_key = identify_child_key(
        child=child,
        preferred_key=preferred_key,
    )
    if child.empty:
        return {
            "filas": 0,
            "columna_llave": child_key,
            "llaves_no_vacias": 0,
            "llaves_unicas": 0,
            "llaves_vacias": 0,
            "duplicadas": 0,
            "fuera_detalle": 0,
        }
    if child_key is None:
        warnings.append(
            f"{child_name}: no contiene una columna "
            "de llave reconocida; no fue posible validar "
            "pertenencia uno a uno."
        )
        return {
            "filas": len(child),
            "columna_llave": None,
            "llaves_no_vacias": 0,
            "llaves_unicas": 0,
            "llaves_vacias": len(child),
            "duplicadas": 0,
            "fuera_detalle": 0,
        }
    keys = normalize_key(
        child[child_key]
    )
    empty_keys = int(
        keys.eq("").sum()
    )
    non_empty_keys = keys[
        keys.ne("")
    ]
    outside = sorted(
        set(non_empty_keys)
        - parent_keys
    )
    duplicated = int(
        non_empty_keys
        .duplicated()
        .sum()
    )
    if empty_keys:
        errors.append(
            f"{child_name}: contiene "
            f"{empty_keys} llaves vacías."
        )
    if outside:
        destination = (
            errors
            if outside_is_error
            else warnings
        )
        destination.append(
            f"{child_name}: contiene "
            f"{len(outside)} llaves fuera de "
            "DETALLE_MATRICULA."
        )
    if duplicated:
        destination = (
            errors
            if duplicated_is_error
            else warnings
        )
        destination.append(
            f"{child_name}: contiene "
            f"{duplicated} llaves duplicadas."
        )
    return {
        "filas": len(child),
        "columna_llave": child_key,
        "llaves_no_vacias": int(
            non_empty_keys.shape[0]
        ),
        "llaves_unicas": int(
            non_empty_keys.nunique()
        ),
        "llaves_vacias": empty_keys,
        "duplicadas": duplicated,
        "fuera_detalle": len(outside),
    }
def affirmative_count(
    series: pd.Series,
) -> int:
    normalized = series.map(
        normalize_text
    )
    return int(
        normalized.isin(
            {
                normalize_text(value)
                for value in AFFIRMATIVE_VALUES
            }
        ).sum()
    )
def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not (repo / ".git").exists():
        raise RuntimeError(
            f"No parece ser un repositorio Git: {repo}"
        )
    archivo = locate_b13_file(args)
    if not archivo.is_file():
        raise FileNotFoundError(
            f"No existe el archivo B13: {archivo}"
        )
    if archivo.suffix.lower() != ".xlsx":
        raise ValueError(
            "El archivo B13 debe tener extensión .xlsx."
        )
    run_dir = archivo.parent.parent
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    if args.auditoria is not None:
        audit = args.auditoria.expanduser().resolve()
    else:
        audit = (
            repo
            / ".local"
            / "auditorias"
            / "validacion_pospublicacion_b13"
            / f"{run_dir.name}_{timestamp}"
        )
    audit.mkdir(
        parents=True,
        exist_ok=False,
    )
    print("=" * 76)
    print("VALIDACIÓN POSPUBLICACIÓN — BLOQUE 13")
    print("=" * 76)
    print(f"REPOSITORIO={repo}")
    print(f"RUN_DIR={run_dir}")
    print(f"ARCHIVO_B13={archivo}")
    print(f"AUDITORIA={audit}")
    errors: list[str] = []
    warnings: list[str] = []
    workbook = pd.ExcelFile(
        archivo
    )
    sheet_names = set(
        workbook.sheet_names
    )
    missing_sheets = sorted(
        REQUIRED_SHEETS
        - sheet_names
    )
    extra_sheets = sorted(
        sheet_names
        - REQUIRED_SHEETS
    )
    if missing_sheets:
        errors.append(
            "Faltan hojas obligatorias: "
            + ", ".join(missing_sheets)
        )
    if extra_sheets:
        warnings.append(
            "Existen hojas adicionales: "
            + ", ".join(extra_sheets)
        )
    if missing_sheets:
        closure = {
            "archivo_b13": str(archivo),
            "run_dir": str(run_dir),
            "hojas_faltantes": missing_sheets,
            "hojas_adicionales": extra_sheets,
            "errores": errors,
            "advertencias": warnings,
            "dictamen": "B13_REQUIERE_REVISION",
        }
        with (
            audit / "05_MANIFEST.json"
        ).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                closure,
                file,
                ensure_ascii=False,
                indent=2,
            )
        raise RuntimeError(
            "\n".join(errors)
        )
    sheets = {
        name: pd.read_excel(
            archivo,
            sheet_name=name,
        )
        for name in REQUIRED_SHEETS
    }
    detalle = sheets[
        "DETALLE_MATRICULA"
    ]
    key_column = determine_column(
        detalle.columns,
        KEY_CANDIDATES,
        "la llave CODCLI",
    )
    level_column = determine_column(
        detalle.columns,
        LEVEL_CANDIDATES,
        "la clasificación Técnico/Profesional",
    )
    keys = normalize_key(
        detalle[key_column]
    )
    empty_keys = int(
        keys.eq("").sum()
    )
    non_empty_keys = keys[
        keys.ne("")
    ]
    duplicate_keys = int(
        non_empty_keys
        .duplicated()
        .sum()
    )
    unique_keys = int(
        non_empty_keys
        .nunique()
    )
    if empty_keys:
        errors.append(
            "DETALLE_MATRICULA contiene "
            f"{empty_keys} llaves vacías."
        )
    if duplicate_keys:
        errors.append(
            "DETALLE_MATRICULA contiene "
            f"{duplicate_keys} llaves duplicadas."
        )
    if unique_keys != len(detalle):
        errors.append(
            "La cardinalidad de la llave no coincide "
            "con DETALLE_MATRICULA: "
            f"filas={len(detalle)}, "
            f"llaves_unicas={unique_keys}."
        )
    levels = detalle[
        level_column
    ].map(
        normalize_text
    )
    level_counts = (
        levels
        .value_counts(
            dropna=False
        )
        .rename_axis("NIVEL")
        .reset_index(
            name="TOTAL"
        )
    )
    invalid_level_mask = (
        ~levels.isin(
            ALLOWED_LEVELS
        )
    )
    invalid_levels = int(
        invalid_level_mask.sum()
    )
    if invalid_levels:
        invalid_detail = (
            levels[
                invalid_level_mask
            ]
            .value_counts(
                dropna=False
            )
            .to_dict()
        )
        errors.append(
            "Se encontraron niveles no permitidos: "
            f"{invalid_detail}"
        )
    technical = int(
        levels.eq(
            "TECNICO"
        ).sum()
    )
    professional = int(
        levels.eq(
            "PROFESIONAL"
        ).sum()
    )
    if (
        technical
        + professional
        != len(detalle)
    ):
        errors.append(
            "La suma de Técnico y Profesional "
            "no coincide con DETALLE_MATRICULA."
        )
    parent_keys = set(
        non_empty_keys
    )
    derivative_metrics: dict[
        str,
        dict[str, Any],
    ] = {}
    derivative_sheet_names = (
        "PROVENIENCIA_EMTP",
        "PROVENIENCIA_CFT",
        "INGRESO_PROFESIONAL",
        "SALIDA_INTERMEDIA",
        "TECNICO_A_PROFESIONAL",
    )
    for sheet_name in derivative_sheet_names:
        derivative_metrics[
            sheet_name
        ] = compare_key_subset(
            child=sheets[
                sheet_name
            ],
            child_name=sheet_name,
            parent_keys=parent_keys,
            preferred_key=key_column,
            errors=errors,
            warnings=warnings,
        )

    # DIPLOMADOS corresponde a un universo de exclusión y no
    # constituye un subconjunto uno a uno de DETALLE_MATRICULA.
    # Se mantiene su auditoría de llaves, pero la pertenencia al
    # universo sustantivo y la repetición de CODCLI se reportan
    # como advertencias. Las llaves vacías siguen bloqueando.
    derivative_metrics[
        "DIPLOMADOS"
    ] = compare_key_subset(
        child=sheets[
            "DIPLOMADOS"
        ],
        child_name="DIPLOMADOS",
        parent_keys=parent_keys,
        preferred_key=key_column,
        errors=errors,
        warnings=warnings,
        outside_is_error=False,
        duplicated_is_error=False,
    )
    ingreso_profesional = sheets[
        "INGRESO_PROFESIONAL"
    ]
    if (
        len(
            ingreso_profesional
        )
        != professional
    ):
        errors.append(
            "INGRESO_PROFESIONAL no coincide "
            "con el total Profesional: "
            f"filas_hoja={len(ingreso_profesional)}, "
            f"profesionales={professional}."
        )
    transiciones = sheets[
        "TECNICO_A_PROFESIONAL"
    ]
    if len(transiciones) > len(detalle):
        errors.append(
            "TECNICO_A_PROFESIONAL supera "
            "el universo institucional."
        )
    proveniencia_emtp = sheets[
        "PROVENIENCIA_EMTP"
    ]
    proveniencia_cft = sheets[
        "PROVENIENCIA_CFT"
    ]
    if "_PROVIENE_EMTP" in detalle.columns:
        expected_emtp = affirmative_count(
            detalle[
                "_PROVIENE_EMTP"
            ]
        )
        if (
            len(
                proveniencia_emtp
            )
            != expected_emtp
        ):
            warnings.append(
                "PROVENIENCIA_EMTP no coincide "
                "con el conteo afirmativo de "
                "_PROVIENE_EMTP: "
                f"hoja={len(proveniencia_emtp)}, "
                f"detalle={expected_emtp}."
            )
    if "_PROVIENE_CFT" in detalle.columns:
        expected_cft = affirmative_count(
            detalle[
                "_PROVIENE_CFT"
            ]
        )
        if (
            len(
                proveniencia_cft
            )
            != expected_cft
        ):
            warnings.append(
                "PROVENIENCIA_CFT no coincide "
                "con el conteo afirmativo de "
                "_PROVIENE_CFT: "
                f"hoja={len(proveniencia_cft)}, "
                f"detalle={expected_cft}."
            )
    qa = sheets[
        "QA_COBERTURA"
    ]
    if qa.empty:
        errors.append(
            "QA_COBERTURA está vacía."
        )
    resumen = sheets[
        "RESUMEN_KPI"
    ]
    if resumen.empty:
        errors.append(
            "RESUMEN_KPI está vacío."
        )
    head = git(
        repo,
        "rev-parse",
        "HEAD",
    )
    origin_main = git(
        repo,
        "rev-parse",
        "origin/main",
    )
    divergence = " ".join(
        git(
            repo,
            "rev-list",
            "--left-right",
            "--count",
            "origin/main...main",
        ).split()
    )
    status_raw = git(
        repo,
        "status",
        "--porcelain",
        "--untracked-files=all",
    )
    git_status = (
        "LIMPIO"
        if not status_raw
        else "CON_CAMBIOS"
    )
    if args.require_clean_git:
        if head != origin_main:
            errors.append(
                "HEAD y origin/main no coinciden."
            )
        if divergence != "0 0":
            errors.append(
                "Existe divergencia Git: "
                f"{divergence}."
            )
        if status_raw:
            errors.append(
                "El repositorio contiene cambios locales."
            )
    metrics = {
        "DETALLE_MATRICULA": len(
            detalle
        ),
        "CODCLI_NO_VACIOS": int(
            non_empty_keys.shape[0]
        ),
        "CODCLI_UNICOS": unique_keys,
        "CODCLI_VACIOS": empty_keys,
        "DUPLICADOS_CODCLI": duplicate_keys,
        "NIVEL_TECNICO": technical,
        "NIVEL_PROFESIONAL": professional,
        "NO_CLASIFICADO": invalid_levels,
        "INGRESO_PROFESIONAL": len(
            ingreso_profesional
        ),
        "TECNICO_A_PROFESIONAL": len(
            transiciones
        ),
        "PROVENIENCIA_EMTP": len(
            proveniencia_emtp
        ),
        "PROVENIENCIA_CFT": len(
            proveniencia_cft
        ),
        "SALIDA_INTERMEDIA": len(
            sheets[
                "SALIDA_INTERMEDIA"
            ]
        ),
        "DIPLOMADOS": len(
            sheets[
                "DIPLOMADOS"
            ]
        ),
        "QA_COBERTURA_FILAS": len(
            qa
        ),
        "RESUMEN_KPI_FILAS": len(
            resumen
        ),
    }
    sha256 = sha256_file(
        archivo
    )
    pd.DataFrame(
        [
            {
                "INDICADOR": key,
                "VALOR": value,
            }
            for key, value in metrics.items()
        ]
    ).to_excel(
        audit
        / "01_METRICAS_B13.xlsx",
        index=False,
    )
    level_counts.to_excel(
        audit
        / "02_DISTRIBUCION_NIVELES.xlsx",
        index=False,
    )
    qa.to_excel(
        audit
        / "03_QA_COBERTURA.xlsx",
        index=False,
    )
    resumen.to_excel(
        audit
        / "04_RESUMEN_KPI.xlsx",
        index=False,
    )
    manifest = {
        "schema_version": "1.0",
        "hito": "H043",
        "proyecto": "CARACTERIZACIÓN",
        "bloque": 13,
        "fecha_validacion": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),
        "repo": str(repo),
        "run_dir": str(run_dir),
        "archivo_b13": str(archivo),
        "sha256_b13": sha256,
        "hojas": workbook.sheet_names,
        "hojas_faltantes": missing_sheets,
        "hojas_adicionales": extra_sheets,
        "columna_llave": key_column,
        "columna_nivel": level_column,
        "metricas": metrics,
        "metricas_derivadas": derivative_metrics,
        "head": head,
        "origin_main": origin_main,
        "divergencia": divergence,
        "estado_git": git_status,
        "errores": errors,
        "advertencias": warnings,
        "dictamen": (
            "B13_VALIDADO_POSPUBLICACION"
            if not errors
            else "B13_REQUIERE_REVISION"
        ),
    }
    with (
        audit
        / "05_MANIFEST.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            ensure_ascii=False,
            indent=2,
        )
    print()
    print("MÉTRICAS")
    for key, value in metrics.items():
        print(
            f"{key}={value}"
        )
    print()
    print("CONTROL GIT")
    print(f"HEAD={head}")
    print(
        f"ORIGIN_MAIN={origin_main}"
    )
    print(
        f"DIVERGENCIA={divergence}"
    )
    print(
        f"ESTADO_GIT={git_status}"
    )
    if warnings:
        print()
        print("ADVERTENCIAS")
        for warning in warnings:
            print(
                f"  - {warning}"
            )
    if errors:
        print()
        print("HALLAZGOS BLOQUEANTES")
        for error in errors:
            print(
                f"  - {error}"
            )
        closure_lines = [
            "PROYECTO=CARACTERIZACIÓN",
            "HITO=H043",
            "BLOQUE=13",
            f"RUN_DIR={run_dir}",
            f"ARCHIVO_B13={archivo}",
            f"SHA256_B13={sha256}",
            "VALIDACION_FUNCIONAL_B13=ERROR",
            f"ERRORES={len(errors)}",
            f"ADVERTENCIAS={len(warnings)}",
            f"AUDITORIA={audit}",
            "DICTAMEN=B13_REQUIERE_REVISION",
        ]
        (
            audit
            / "06_CIERRE.txt"
        ).write_text(
            "\n".join(
                closure_lines
            )
            + "\n",
            encoding="utf-8",
        )
        print()
        print(
            "DICTAMEN="
            "B13_REQUIERE_REVISION"
        )
        print(
            f"AUDITORIA={audit}"
        )
        return 1
    closure_lines = [
        "PROYECTO=CARACTERIZACIÓN",
        "HITO=H043",
        "BLOQUE=13",
        f"RUN_DIR={run_dir}",
        f"ARCHIVO_B13={archivo}",
        f"SHA256_B13={sha256}",
    ]
    closure_lines.extend(
        f"{key}={value}"
        for key, value in metrics.items()
    )
    closure_lines.extend(
        [
            "VALIDACION_FUNCIONAL_B13=OK",
            "ERRORES=0",
            f"ADVERTENCIAS={len(warnings)}",
            f"HEAD={head}",
            f"ORIGIN_MAIN={origin_main}",
            f"DIVERGENCIA={divergence}",
            f"ESTADO_GIT={git_status}",
            f"AUDITORIA={audit}",
            "DICTAMEN=B13_VALIDADO_POSPUBLICACION",
        ]
    )
    (
        audit
        / "06_CIERRE.txt"
    ).write_text(
        "\n".join(
            closure_lines
        )
        + "\n",
        encoding="utf-8",
    )
    print()
    print("=" * 76)
    print("CIERRE BLOQUE 13")
    print("=" * 76)
    print(
        "VALIDACION_FUNCIONAL_B13=OK"
    )
    print("ERRORES=0")
    print(
        f"ADVERTENCIAS={len(warnings)}"
    )
    print(
        f"AUDITORIA={audit}"
    )
    print(
        "DICTAMEN="
        "B13_VALIDADO_POSPUBLICACION"
    )
    return 0
if __name__ == "__main__":
    try:
        sys.exit(
            main()
        )
    except Exception as exc:
        print()
        print("=" * 76)
        print("ERROR DEL VALIDADOR")
        print("=" * 76)
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print(
            "DICTAMEN="
            "B13_VALIDACION_NO_COMPLETADA"
        )
        sys.exit(1)
