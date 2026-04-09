from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd

DEFAULT_SIT_FON_SOL_PATCH_PATH = Path("patches/mu2026/sit_fon_sol_patch_ruts.json")
DEFAULT_RUT_COLUMN_CANDIDATES = ("RUT", "RUT_NUM", "N_DOC", "NUM_DOCUMENTO", "CODCLI")

PATCH_SOURCE_SIT_FON_SOL = "PATCH_JSON_SIT_FON_SOL_MU2026"
PATCH_METHOD_SIT_FON_SOL = "OVERRIDE_POR_RUT_LISTADO"
PATCH_AUDIT_STATUS_SIT_FON_SOL = "PATCH_PROVISORIO_AUDITABLE_APLICADO"


def load_json_patch_payload(path: str | Path) -> dict[str, object]:
    patch_path = Path(path).expanduser().resolve()
    if not patch_path.exists():
        raise FileNotFoundError(f"No se encontró patch JSON: {patch_path}")

    payload = json.loads(patch_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Patch JSON inválido: se esperaba un objeto raíz")
    if "correcciones" not in payload or not isinstance(payload["correcciones"], list):
        raise ValueError("Patch JSON inválido: falta lista 'correcciones'")
    return payload


def _extract_rut_digits(value: object) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _expected_dv_for_rut_body(rut_body: str) -> str:
    digits = [int(ch) for ch in rut_body if ch.isdigit()]
    if not digits:
        return ""
    factors = [2, 3, 4, 5, 6, 7]
    total = 0
    for idx, digit in enumerate(reversed(digits)):
        total += digit * factors[idx % len(factors)]
    dv = 11 - (total % 11)
    if dv == 11:
        return "0"
    if dv == 10:
        return "K"
    return str(dv)


def _normalize_patch_rut(value: object) -> str:
    digits = _extract_rut_digits(value)
    if not digits:
        raise ValueError(f"RUT inválido en patch: {value!r}")
    return digits


def _extract_patch_map(payload: Mapping[str, object]) -> dict[str, int]:
    corrections = payload.get("correcciones")
    if not isinstance(corrections, list):
        raise ValueError("Patch JSON inválido: 'correcciones' debe ser lista")

    patch_map: dict[str, int] = {}
    for idx, item in enumerate(corrections, start=1):
        if not isinstance(item, Mapping):
            raise ValueError(f"Patch JSON inválido: corrección #{idx} no es objeto")

        rut_raw = item.get("rut", item.get("RUT"))
        if rut_raw is None:
            raise ValueError(f"Patch JSON inválido: corrección #{idx} sin campo 'rut'")
        rut_norm = _normalize_patch_rut(rut_raw)

        sit_val_raw = item.get("SIT_FON_SOL")
        if sit_val_raw is None:
            raise ValueError(f"Patch JSON inválido: corrección #{idx} sin campo SIT_FON_SOL")
        try:
            sit_val = int(str(sit_val_raw).strip())
        except ValueError as exc:
            raise ValueError(
                f"Patch JSON inválido: SIT_FON_SOL no numérico en corrección #{idx}: {sit_val_raw!r}"
            ) from exc

        if sit_val not in {0, 1, 2}:
            raise ValueError(
                f"Patch JSON inválido: SIT_FON_SOL fuera de catálogo 0/1/2 en corrección #{idx}: {sit_val}"
            )

        if rut_norm in patch_map and patch_map[rut_norm] != sit_val:
            raise ValueError(
                f"Patch JSON inválido: RUT {rut_norm} tiene valores SIT_FON_SOL conflictivos "
                f"({patch_map[rut_norm]} vs {sit_val})"
            )
        patch_map[rut_norm] = sit_val

    return patch_map


def load_json_patch(path: str | Path) -> dict[str, int]:
    payload = load_json_patch_payload(path)
    return _extract_patch_map(payload)


def _normalize_rut_from_df(value: object, patch_ruts: set[str]) -> str:
    raw = str(value or "").strip().upper()
    if not raw or raw in {"NAN", "NONE", "<NA>"}:
        return ""

    if "-" in raw:
        base_raw = raw.split("-", maxsplit=1)[0]
        base_digits = _extract_rut_digits(base_raw)
        if base_digits:
            return base_digits

    digits = _extract_rut_digits(raw)
    if not digits:
        return ""
    if digits in patch_ruts:
        return digits

    # Caso tipo "80747268" (RUT + DV concatenado): remover DV solo si
    # coincide con dígito verificador válido y ese RUT existe en el patch.
    if len(digits) >= 2:
        candidate_body = digits[:-1]
        candidate_dv = digits[-1]
        if candidate_body and _expected_dv_for_rut_body(candidate_body) == candidate_dv and candidate_body in patch_ruts:
            return candidate_body

    return digits


def resolve_patch_targets(
    df: pd.DataFrame,
    patch_map: Mapping[str, int],
    rut_columns_candidates: Sequence[str] = DEFAULT_RUT_COLUMN_CANDIDATES,
) -> tuple[pd.Series, pd.Series, str, dict[str, int], list[str], list[str]]:
    if df is None:
        raise ValueError("DataFrame no puede ser None")

    patch_ruts = set(patch_map.keys())
    if not patch_ruts:
        empty_series = pd.Series("", index=df.index, dtype="object")
        empty_mask = pd.Series(False, index=df.index)
        return empty_series, empty_mask, "", {}, [], []

    existing_candidates = [col for col in rut_columns_candidates if col in df.columns]
    if not existing_candidates:
        raise ValueError(
            "No se encontró columna compatible de RUT. "
            f"Candidatas evaluadas: {list(rut_columns_candidates)}"
        )

    matches_by_column: dict[str, int] = {}
    normalized_by_column: dict[str, pd.Series] = {}
    for col in existing_candidates:
        norm_col = df[col].map(lambda value: _normalize_rut_from_df(value, patch_ruts)).astype("object")
        normalized_by_column[col] = norm_col
        matches_by_column[col] = int(norm_col.isin(patch_ruts).sum())

    selected_column = max(existing_candidates, key=lambda col: (matches_by_column[col], -existing_candidates.index(col)))
    selected_rut_series = normalized_by_column[selected_column]
    target_mask = selected_rut_series.isin(patch_ruts)

    matched_ruts = sorted(set(selected_rut_series[target_mask].astype(str)))
    missing_patch_ruts = sorted(patch_ruts - set(matched_ruts))
    return selected_rut_series, target_mask, selected_column, matches_by_column, matched_ruts, missing_patch_ruts


def apply_sit_fon_sol_patch(
    df: pd.DataFrame,
    patch_path: str | Path,
    rut_columns_candidates: Sequence[str] = DEFAULT_RUT_COLUMN_CANDIDATES,
    target_col: str = "SIT_FON_SOL",
) -> tuple[pd.DataFrame, dict[str, object]]:
    if target_col not in df.columns:
        raise ValueError(f"No existe columna objetivo '{target_col}' para aplicar patch SIT_FON_SOL")

    patch_payload = load_json_patch_payload(patch_path)
    patch_map = _extract_patch_map(patch_payload)

    out = df.copy()

    rut_series, target_mask, selected_column, matches_by_column, matched_ruts, missing_patch_ruts = resolve_patch_targets(
        out,
        patch_map,
        rut_columns_candidates=rut_columns_candidates,
    )

    out[target_col] = pd.to_numeric(out[target_col], errors="coerce").astype("Int64")
    before_target = out.loc[target_mask, target_col].astype("Int64")
    before_distribution = before_target.astype("string").fillna("<NA>").value_counts(dropna=False).to_dict()

    new_values = rut_series.map(patch_map)
    out.loc[target_mask, target_col] = pd.to_numeric(new_values[target_mask], errors="coerce").astype("Int64")
    after_target = out.loc[target_mask, target_col].astype("Int64")
    after_distribution = after_target.astype("string").fillna("<NA>").value_counts(dropna=False).to_dict()

    rows_affected_mask = target_mask & (before_target.reindex(out.index).astype("Int64") != out[target_col]).fillna(False)
    rows_affected = int(rows_affected_mask.sum())

    stats: dict[str, object] = {
        "patch_path": str(Path(patch_path).expanduser().resolve()),
        "patch_estado": str(patch_payload.get("estado", "")),
        "patch_proposito": str(patch_payload.get("proposito", "")),
        "patch_regla_normativa": str(patch_payload.get("regla_normativa", "")),
        "n_rut_patch": int(len(patch_map)),
        "rut_column_selected": selected_column,
        "rut_columns_evaluated": list(matches_by_column.keys()),
        "rut_matches_by_column": matches_by_column,
        "n_rows_total": int(len(out)),
        "n_rows_targeted": int(target_mask.sum()),
        "n_rows_affected": rows_affected,
        "n_rut_matched": int(len(matched_ruts)),
        "n_rut_missing": int(len(missing_patch_ruts)),
        "rut_missing_sample": missing_patch_ruts[:20],
        "sit_fon_sol_distribution_before_target": {str(k): int(v) for k, v in before_distribution.items()},
        "sit_fon_sol_distribution_after_target": {str(k): int(v) for k, v in after_distribution.items()},
    }

    return out, stats
