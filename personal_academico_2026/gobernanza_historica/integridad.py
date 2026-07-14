"""Validaciones de integridad de fuentes gobernadas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .descubrimiento_fuentes import sha256_file


def validate_governance(
    approved: pd.DataFrame,
    frozen: pd.DataFrame,
    normalized: pd.DataFrame,
    expected_years: list[int],
) -> pd.DataFrame:
    """Valida criterios de gobernanza sin detener la ejecucion."""

    issues: list[dict[str, object]] = []
    selected_counts = approved.groupby("anio").size().to_dict() if not approved.empty else {}
    for year in expected_years:
        count = int(selected_counts.get(year, 0))
        issues.append(
            {
                "anio": year,
                "codigo": "FUENTE_UNICA_POR_ANIO",
                "severidad": "OK" if count == 1 else "ERROR",
                "detalle": f"fuentes_configuradas={count}",
            }
        )
    for _index, source in frozen.iterrows():
        year = int(source["anio"])
        original = Path(str(source["ruta_original"]))
        governed = Path(str(source["ruta_gobernada"]))
        original_hash = sha256_file(original) if original.exists() else ""
        governed_hash = sha256_file(governed) if governed.exists() else ""
        issues.append(
            {
                "anio": year,
                "codigo": "HASH_ORIGINAL_GOBERNADO",
                "severidad": "OK" if original_hash and original_hash == governed_hash else "ERROR",
                "detalle": "hashes iguales" if original_hash == governed_hash else "hash distinto o archivo faltante",
            }
        )
        for field in ["sha256_original", "estado", "responsable"]:
            value = str(source.get(field, ""))
            issues.append(
                {
                    "anio": year,
                    "codigo": f"CAMPO_OBLIGATORIO_{field.upper()}",
                    "severidad": "OK" if value else "ERROR",
                    "detalle": "presente" if value else "faltante",
                }
            )
    hashes = frozen["sha256_original"].astype(str) if "sha256_original" in frozen.columns else pd.Series(dtype=str)
    repeated = set(hashes[hashes.duplicated(keep=False)])
    issues.append(
        {
            "anio": None,
            "codigo": "SHA_REPETIDO_ENTRE_ANIOS",
            "severidad": "OK" if not repeated else "ADVERTENCIA",
            "detalle": "sin repetidos" if not repeated else f"hashes_repetidos={len(repeated)}",
        }
    )
    normalized_years = set(normalized["anio"].astype(int)) if not normalized.empty else set()
    for year in expected_years:
        issues.append(
            {
                "anio": year,
                "codigo": "VERSION_NORMALIZADA_EXISTE",
                "severidad": "OK" if year in normalized_years else "ERROR",
                "detalle": "presente" if year in normalized_years else "faltante",
            }
        )
    return pd.DataFrame(issues)
