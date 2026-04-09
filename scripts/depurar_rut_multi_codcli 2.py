"""
Depuración provisoria RUT ↔ CODCLI — MU 2026
==============================================
Regla provisoria (pre-pipeline): para cada RUT con múltiples CODCLI,
conservar únicamente el CODCLI con el mayor año de cohorte administrativa
(primeros 4 dígitos del CODCLI) y excluir todos los demás.

Se aplica ANTES de cualquier cálculo de FOR_ING_ACT, continuidad,
vigencia, cruces CODCARPR o auditoría MU.

Genera un TSV de control en resultados/ con toda la trazabilidad.
No agrega columnas al dataframe regulatorio.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

_MOTIVO = "Regla provisoria: se conserva mayor cohorte por RUT"


def _parse_ano_cohorte(codcli: object) -> float:
    """Extrae año de cohorte de los primeros 4 dígitos numéricos del CODCLI."""
    if pd.isna(codcli):
        return float("nan")
    text = re.sub(r"\D", "", str(codcli))
    if len(text) >= 4:
        year = int(text[:4])
        if 1900 <= year <= 2100:
            return float(year)
    return float("nan")


def depurar_rut_multi_codcli(
    src: pd.DataFrame,
    col_rut: str,
    col_codcli: str,
    output_dir: Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Depura el dataframe fuente conservando un único CODCLI por RUT.

    Para cada RUT con más de un CODCLI distinto, conserva el que tenga
    el mayor año de cohorte (primeros 4 dígitos del CODCLI).
    En caso de empate, conserva uno y marca EMPATE=SI sin resolución automática.

    Parameters
    ----------
    src : pd.DataFrame
        DataFrame fuente recién cargado desde el Excel de entrada.
    col_rut : str
        Nombre de la columna que contiene el RUT del estudiante.
    col_codcli : str
        Nombre de la columna que contiene el CODCLI.
    output_dir : Path | None
        Directorio donde escribir el TSV de control. Si es None no se escribe.

    Returns
    -------
    (src_filtrado, stats)
        src_filtrado: DataFrame sin las filas de CODCLI excluidos.
        stats: Diccionario con métricas de la depuración.
    """
    total_rut = src[col_rut].nunique()
    total_filas_antes = len(src)

    # Parsear año de cohorte
    src = src.copy()
    src["_ANO_COHORTE_TMP"] = src[col_codcli].apply(_parse_ano_cohorte)

    # Identificar RUTs con >1 CODCLI distinto
    rut_codcli = src[[col_rut, col_codcli]].drop_duplicates()
    rut_counts = rut_codcli.groupby(col_rut)[col_codcli].nunique()
    ruts_multi = set(rut_counts[rut_counts > 1].index)

    if not ruts_multi:
        src.drop(columns=["_ANO_COHORTE_TMP"], inplace=True)
        stats = {
            "total_rut": total_rut,
            "rut_multi_codcli": 0,
            "codcli_excluidos": 0,
            "filas_excluidas": 0,
        }
        print(f"  ✅ Depuración RUT↔CODCLI: 0 RUT con múltiples CODCLI — sin cambios")
        return src, stats

    # Para cada RUT multi-CODCLI, seleccionar el CODCLI ganador
    audit_rows: list[dict] = []
    codcli_excluir: set[str] = set()

    multi_df = src[src[col_rut].isin(ruts_multi)].copy()

    for rut, grupo in multi_df.groupby(col_rut):
        # Tabla de CODCLI distintos con su año máximo por CODCLI
        codclis = (
            grupo[[col_codcli, "_ANO_COHORTE_TMP"]]
            .drop_duplicates(subset=[col_codcli])
            .copy()
        )
        codclis["_codcli_str"] = codclis[col_codcli].astype(str).str.strip()

        max_ano = codclis["_ANO_COHORTE_TMP"].max()
        ganadores = codclis[codclis["_ANO_COHORTE_TMP"] == max_ano]
        empate = len(ganadores) > 1

        # Elegir el primero como ganador en caso de empate
        ganador_row = ganadores.iloc[0]
        codcli_ganador = ganador_row["_codcli_str"]
        ano_ganador = ganador_row["_ANO_COHORTE_TMP"]

        # Excluir los demás
        perdedores = codclis[codclis["_codcli_str"] != codcli_ganador]
        for _, p in perdedores.iterrows():
            codcli_excluir.add(p["_codcli_str"])
            audit_rows.append({
                "RUT": rut,
                "CODCLI_CONSERVADO": codcli_ganador,
                "ANO_COHORTE_CONSERVADO": int(ano_ganador) if pd.notna(ano_ganador) else "",
                "CODCLI_EXCLUIDO": p["_codcli_str"],
                "ANO_COHORTE_EXCLUIDO": int(p["_ANO_COHORTE_TMP"]) if pd.notna(p["_ANO_COHORTE_TMP"]) else "",
                "MOTIVO": _MOTIVO,
                "EMPATE": "SI" if empate else "NO",
            })

    # Filtrar filas cuyos CODCLI están en el set de excluidos
    mask_excluir = src[col_codcli].astype(str).str.strip().isin(codcli_excluir)
    filas_excluidas = int(mask_excluir.sum())
    src_filtrado = src[~mask_excluir].reset_index(drop=True)
    src_filtrado.drop(columns=["_ANO_COHORTE_TMP"], inplace=True)

    # Escribir TSV de control
    audit_df = pd.DataFrame(audit_rows)
    if output_dir is not None and len(audit_df) > 0:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        tsv_path = output_dir / "EXCLUSIONES_PROVISORIAS_RUT_MULTI_CODCLI.tsv"
        audit_df.to_csv(tsv_path, sep="\t", index=False)
        print(f"  📝 TSV de control: {tsv_path} ({len(audit_df)} filas)")

    stats = {
        "total_rut": total_rut,
        "rut_multi_codcli": len(ruts_multi),
        "codcli_excluidos": len(codcli_excluir),
        "filas_excluidas": filas_excluidas,
    }

    print(f"  🔧 Depuración provisoria RUT↔CODCLI:")
    print(f"     Total RUT procesados:       {stats['total_rut']}")
    print(f"     RUT con múltiples CODCLI:   {stats['rut_multi_codcli']}")
    print(f"     CODCLI excluidos:           {stats['codcli_excluidos']}")
    print(f"     Filas excluidas:            {stats['filas_excluidas']}")
    print(f"     Filas restantes:            {len(src_filtrado)} (de {total_filas_antes})")

    return src_filtrado, stats
