#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

MAX_SIES_CODES_PER_KEY = 5
INVALID_TOKEN_VALUES = {"", "NAN", "NONE", "NULL", "<NA>"}


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


def _extract_alpha_prefix(value: object) -> str:
    text = _normalize_text(value)
    m = re.match(r"^([A-Z]+)", text)
    return m.group(1) if m else ""


def _build_key_3(jornada: object, codcarpr: object, nombre: object) -> str:
    return f"{_normalize_text(jornada)}|{_normalize_text(codcarpr)}|{_normalize_text(nombre)}"


def _build_key_no_jornada(codcarpr: object, nombre: object) -> str:
    return f"|{_normalize_text(codcarpr)}|{_normalize_text(nombre)}"


def _jornada_to_letter(value: object) -> str:
    raw = _normalize_text(value)
    if raw in {"1", "D"}:
        return "D"
    if raw in {"2", "V"}:
        return "V"
    if raw in {"3", "4", "O"}:
        return "O"
    return raw


def _split_codcarpr_candidates(canon: object, aliases: object) -> list[str]:
    out: set[str] = set()
    for token in [canon, *str(aliases or "").split("|")]:
        value = _normalize_text(token)
        if value in INVALID_TOKEN_VALUES:
            continue
        out.add(value)
    return sorted(out)


def _extract_cod_carrera_from_sies(code: str) -> int | None:
    m = re.match(r"^I\d+S\d+C(?P<cod>\d+)J\d+V\d+$", str(code).strip().upper())
    if not m:
        return None
    return int(m.group("cod"))


def _load_duracion_rows(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    required = {"CODIGO_UNICO", "NOMBRE_CARRERA", "JORNADA", "CODCARPR_CANONICO", "CODCARPR_ALIAS_LIST"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DURACION_ESTUDIOS.tsv inválido: faltan columnas {sorted(missing)}")

    rows: list[dict[str, object]] = []
    for row in df.itertuples(index=False):
        codigo_unico = _normalize_text(getattr(row, "CODIGO_UNICO", ""))
        nombre = _normalize_text(getattr(row, "NOMBRE_CARRERA", ""))
        jornada = _jornada_to_letter(getattr(row, "JORNADA", ""))
        codcarprs = _split_codcarpr_candidates(
            getattr(row, "CODCARPR_CANONICO", ""),
            getattr(row, "CODCARPR_ALIAS_LIST", ""),
        )
        if not codigo_unico or not nombre or not jornada or not codcarprs:
            continue

        for codcarpr in codcarprs:
            pref = _extract_alpha_prefix(codcarpr) or "X"
            rows.append(
                {
                    "GRUPO_TRAZA": f"DUR_{pref}",
                    "JORNADA": jornada,
                    "CODCARPR": codcarpr,
                    "NOMBRE_L": nombre,
                    "CODIGO_CARRERA_SIES": codigo_unico,
                    "FUENTE_FILA": "DURACION_ESTUDIOS",
                }
            )

    if not rows:
        return pd.DataFrame(columns=["GRUPO_TRAZA", "JORNADA", "CODCARPR", "NOMBRE_L", "CODIGO_CARRERA_SIES", "FUENTE_FILA"])

    out = pd.DataFrame(rows)
    out["SOURCE_KEY_3"] = out.apply(lambda r: _build_key_3(r["JORNADA"], r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    out["SOURCE_KEY_NO_JORNADA"] = out.apply(lambda r: _build_key_no_jornada(r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    return out.drop_duplicates().reset_index(drop=True)


def _load_override_rows(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            columns=[
                "GRUPO_TRAZA",
                "JORNADA",
                "CODCARPR",
                "NOMBRE_L",
                "CODIGO_CARRERA_SIES",
                "REGLA_APLICADA",
                "RAZON_GOBERNANZA",
                "FUENTE_FILA",
            ]
        )

    try:
        df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(
            columns=[
                "GRUPO_TRAZA",
                "JORNADA",
                "CODCARPR",
                "NOMBRE_L",
                "CODIGO_CARRERA_SIES",
                "REGLA_APLICADA",
                "RAZON_GOBERNANZA",
                "FUENTE_FILA",
            ]
        )
    required = {"GRUPO_TRAZA", "JORNADA", "CODCARPR", "NOMBRE_L", "CODIGO_CARRERA_SIES"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"puente_sies.tsv inválido: faltan columnas {sorted(missing)}")

    out = df[
        [
            "GRUPO_TRAZA",
            "JORNADA",
            "CODCARPR",
            "NOMBRE_L",
            "CODIGO_CARRERA_SIES",
        ]
    ].copy()
    out["REGLA_APLICADA"] = df["REGLA_APLICADA"].astype(str).str.strip() if "REGLA_APLICADA" in df.columns else ""
    out["RAZON_GOBERNANZA"] = df["RAZON_GOBERNANZA"].astype(str).str.strip() if "RAZON_GOBERNANZA" in df.columns else ""
    out["GRUPO_TRAZA"] = out["GRUPO_TRAZA"].astype(str).str.strip()
    out["JORNADA"] = out["JORNADA"].map(_jornada_to_letter)
    out["CODCARPR"] = out["CODCARPR"].map(_normalize_text)
    out["NOMBRE_L"] = out["NOMBRE_L"].map(_normalize_text)
    out["CODIGO_CARRERA_SIES"] = out["CODIGO_CARRERA_SIES"].map(_normalize_text)
    out = out[
        out["JORNADA"].astype(str).str.strip().ne("")
        & out["CODCARPR"].astype(str).str.strip().ne("")
        & out["NOMBRE_L"].astype(str).str.strip().ne("")
        & out["CODIGO_CARRERA_SIES"].astype(str).str.strip().ne("")
    ].copy()
    # Gobernanza: solo se consumen overrides con justificación explícita.
    reason_mask = out["REGLA_APLICADA"].astype(str).str.strip().ne("") | out["RAZON_GOBERNANZA"].astype(str).str.strip().ne("")
    out = out[reason_mask].copy()
    out["FUENTE_FILA"] = "OVERRIDE_PUENTE_SIES"
    out["SOURCE_KEY_3"] = out.apply(lambda r: _build_key_3(r["JORNADA"], r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    out["SOURCE_KEY_NO_JORNADA"] = out.apply(lambda r: _build_key_no_jornada(r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    return out.drop_duplicates().reset_index(drop=True)


def _load_observed_universe(repo_root: Path, workbook: Path | None) -> dict[str, set[str]]:
    observed: dict[str, set[str]] = {}

    if workbook and workbook.exists():
        df = pd.read_excel(workbook, sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str).fillna("")
        if {"SOURCE_KEY_3", "SIES_MATCH_STATUS"}.issubset(df.columns):
            for key, status in zip(df["SOURCE_KEY_3"], df["SIES_MATCH_STATUS"]):
                k = _normalize_text(key)
                if not k:
                    continue
                observed.setdefault(k, set()).add(_normalize_text(status))

    block_patterns = [
        "resultados/sies_combinaciones_nuevas_bloqueantes.tsv",
        "resultados/*/sies_combinaciones_nuevas_bloqueantes.tsv",
    ]
    for pattern in block_patterns:
        for file_path in repo_root.glob(pattern):
            if not file_path.exists():
                continue
            bdf = pd.read_csv(file_path, sep="\t", dtype=str, keep_default_na=False)
            if "SOURCE_KEY_3" not in bdf.columns:
                continue
            for key in bdf["SOURCE_KEY_3"]:
                k = _normalize_text(key)
                if not k:
                    continue
                observed.setdefault(k, set()).add("BLOQUEANTE_SIN_MATCH_SIES")

    return observed


def _compile_catalog(
    base_rows: pd.DataFrame,
    override_rows: pd.DataFrame,
    observed_status_map: dict[str, set[str]] | None = None,
) -> pd.DataFrame:
    if base_rows.empty and override_rows.empty:
        return pd.DataFrame()

    if override_rows.empty:
        selected = base_rows.copy()
    else:
        override_keys = set(override_rows["SOURCE_KEY_3"])
        selected = pd.concat(
            [
                base_rows.loc[~base_rows["SOURCE_KEY_3"].isin(override_keys)],
                override_rows,
            ],
            ignore_index=True,
        )
    for col in ["REGLA_APLICADA", "RAZON_GOBERNANZA"]:
        if col not in selected.columns:
            selected[col] = ""

    rows: list[dict[str, object]] = []
    for key, sub in selected.groupby("SOURCE_KEY_3", dropna=False):
        codes = (
            sub["CODIGO_CARRERA_SIES"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .drop_duplicates()
            .tolist()
        )
        codes = sorted(codes)
        n_codes = len(codes)
        unique_code = codes[0] if n_codes == 1 else ""
        status = "UNICO" if n_codes == 1 else "AMBIGUO"

        fuentes = sorted(sub["FUENTE_FILA"].dropna().astype(str).drop_duplicates().tolist())
        fuente_compilado = "OVERRIDE_PUENTE_SIES" if "OVERRIDE_PUENTE_SIES" in fuentes else "DURACION_ESTUDIOS"
        observed_status = sorted((observed_status_map or {}).get(_normalize_text(key), set()))
        observado_universo = bool(observed_status)
        if status == "AMBIGUO" and observado_universo:
            gobernanza_status = "PENDIENTE_GOBERNANZA"
        elif status == "AMBIGUO":
            gobernanza_status = "AMBIGUO_NO_OBSERVADO"
        else:
            gobernanza_status = "RESUELTO_UNICO"

        reglas = (
            sub.loc[sub["FUENTE_FILA"].eq("OVERRIDE_PUENTE_SIES"), "REGLA_APLICADA"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        reglas = sorted([v for v in reglas.unique().tolist() if v])
        razones = (
            sub.loc[sub["FUENTE_FILA"].eq("OVERRIDE_PUENTE_SIES"), "RAZON_GOBERNANZA"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        razones = sorted([v for v in razones.unique().tolist() if v])

        row: dict[str, object] = {
            "SOURCE_KEY_3": key,
            "BRIDGE_KEY_3": key,
            "BRIDGE_KEY_NO_JORNADA": sub["SOURCE_KEY_NO_JORNADA"].iloc[0],
            "GRUPO_TRAZA": " | ".join(sub["GRUPO_TRAZA"].dropna().astype(str).drop_duplicates().tolist()),
            "FAMILIA_TRAZA": _extract_alpha_prefix(sub["GRUPO_TRAZA"].iloc[0]),
            "FAMILIA_CODCARPR": _extract_alpha_prefix(sub["CODCARPR"].iloc[0]),
            "JORNADA": sub["JORNADA"].iloc[0],
            "CODCARPR": sub["CODCARPR"].iloc[0],
            "NOMBRE_L": sub["NOMBRE_L"].iloc[0],
            "N_CODES_SIES": n_codes,
            "CODIGOS_SIES_POTENCIALES": " | ".join(codes),
            "CODIGO_UNICO_FINAL": unique_code,
            "RESOLUCION_STATUS": status,
            "FUENTE_COMPILADO": fuente_compilado,
            "FUENTES_DETALLE": " | ".join(fuentes),
            "ES_BLOQUEANTE": "SI" if n_codes > 1 else "NO",
            "OBSERVADO_EN_UNIVERSO": "SI" if observado_universo else "NO",
            "MATCH_STATUS_OBSERVADO": " | ".join(observed_status),
            "GOBERNANZA_STATUS": gobernanza_status,
            "REGLA_APLICADA": " | ".join(reglas),
            "RAZON_GOBERNANZA": " | ".join(razones),
        }

        for idx in range(MAX_SIES_CODES_PER_KEY):
            row[f"CODIGO_CARRERA_SIES_{idx + 1}"] = codes[idx] if idx < len(codes) else ""

        cod_car = _extract_cod_carrera_from_sies(unique_code) if unique_code else None
        row["CODIGO_CARRERA"] = cod_car if cod_car is not None else ""

        rows.append(row)

    out = pd.DataFrame(rows)
    out = out.sort_values(["FUENTE_COMPILADO", "JORNADA", "CODCARPR", "NOMBRE_L"]).reset_index(drop=True)
    return out


def _build_summary(base_rows: pd.DataFrame, override_rows: pd.DataFrame, compiled: pd.DataFrame) -> dict[str, object]:
    total_keys = int(len(compiled)) if not compiled.empty else 0
    keys_unicos = int(compiled["RESOLUCION_STATUS"].eq("UNICO").sum()) if not compiled.empty else 0
    keys_ambiguos = int(compiled["RESOLUCION_STATUS"].eq("AMBIGUO").sum()) if not compiled.empty else 0
    keys_pendientes = int(compiled["GOBERNANZA_STATUS"].eq("PENDIENTE_GOBERNANZA").sum()) if not compiled.empty and "GOBERNANZA_STATUS" in compiled.columns else 0
    cobertura_unica_pct = round((keys_unicos / total_keys) * 100, 2) if total_keys else 0.0
    return {
        "base_rows": int(len(base_rows)),
        "override_rows": int(len(override_rows)),
        "total_source_keys": total_keys,
        "source_keys_unicos": keys_unicos,
        "source_keys_ambiguos": keys_ambiguos,
        "source_keys_bloqueantes": keys_ambiguos,
        "source_keys_pendiente_gobernanza": keys_pendientes,
        "cobertura_llaves_unicas_pct": cobertura_unica_pct,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compila catálogo canónico de cruce SIES por SOURCE_KEY_3")
    p.add_argument("--duracion", default="DURACION_ESTUDIOS.tsv", help="TSV base de duración/oferta")
    p.add_argument("--override", default="", help="TSV opcional de overrides humanos (si se omite, compila solo desde DURACION_ESTUDIOS.tsv)")
    p.add_argument("--output", default="control/catalogos/PUENTE_SIES_COMPILADO.tsv", help="TSV compilado de salida")
    p.add_argument(
        "--observed-workbook",
        default="resultados/archivo_listo_para_sies.xlsx",
        help="Workbook de universo observado para marcar PENDIENTE_GOBERNANZA",
    )
    p.add_argument("--summary-json", default="", help="Ruta opcional para guardar resumen JSON")
    p.add_argument(
        "--fail-on-ambiguo",
        action="store_true",
        help="Si está activo, retorna exit code 1 cuando existan llaves ambiguas",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    duracion_path = (repo_root / args.duracion).resolve() if not Path(args.duracion).is_absolute() else Path(args.duracion)
    override_arg = str(args.override or "").strip()
    if override_arg:
        override_path = (repo_root / override_arg).resolve() if not Path(override_arg).is_absolute() else Path(override_arg)
    else:
        override_path = None
    output_path = (repo_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    observed_workbook = (
        (repo_root / args.observed_workbook).resolve()
        if args.observed_workbook and not Path(args.observed_workbook).is_absolute()
        else (Path(args.observed_workbook) if args.observed_workbook else None)
    )

    if not duracion_path.exists():
        raise FileNotFoundError(f"No se encontró archivo base de duración: {duracion_path}")

    base_rows = _load_duracion_rows(duracion_path)
    override_rows = _load_override_rows(override_path if (override_path and override_path.exists()) else None)
    observed_status_map = _load_observed_universe(repo_root, observed_workbook)
    compiled = _compile_catalog(base_rows, override_rows, observed_status_map=observed_status_map)

    if compiled.empty:
        raise RuntimeError("Compilación vacía: no se generaron llaves SOURCE_KEY_3")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    compiled.to_csv(output_path, sep="\t", index=False, encoding="utf-8")

    summary = _build_summary(base_rows, override_rows, compiled)
    summary.update(
        {
            "duracion_path": str(duracion_path),
            "override_path": str(override_path) if override_path else "",
            "output_path": str(output_path),
        }
    )

    if args.summary_json:
        summary_json_path = (repo_root / args.summary_json).resolve() if not Path(args.summary_json).is_absolute() else Path(args.summary_json)
        summary_json_path.parent.mkdir(parents=True, exist_ok=True)
        summary_json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if args.fail_on_ambiguo and summary["source_keys_ambiguos"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
