"""
Módulo de exclusiones por multi-carrera activa — MU 2026
=========================================================
Lee el TSV de gobernanza y aplica:
  • ELIMINAR  → marca el CODCLI como excluido (ESTADO_CARGA_PREGRADO distinto de OK)
  • MANTENER  → fuerza FOR_ING_ACT al valor indicado

Diseñado para ser invocado desde codigo_gobernanza_v2.py DESPUÉS de
_consolidar_candidatos_por_codcli() y ANTES de asignar ESTADO_CARGA_PREGRADO.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

_CATALOGO_REL = "catalogos/exclusiones_beneficios_estudiantes_con_mas_de_una_carrera_activa.tsv"
_ESTADO_EXCLUIDO = "EXCLUIDO_MULTI_CARRERA_ACTIVA"


def cargar_exclusiones(repo_dir: Path | None = None) -> pd.DataFrame:
    """Carga el TSV de exclusiones.  Devuelve DataFrame vacío si no existe."""
    if repo_dir is None:
        repo_dir = Path(__file__).resolve().parent.parent
    tsv_path = repo_dir / _CATALOGO_REL
    if not tsv_path.exists():
        return pd.DataFrame(columns=["CODCLI", "ACCION", "FOR_ING_ACT_FORZADO", "MOTIVO", "FUENTE", "ESTADO"])
    df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    df = df[df["ESTADO"] == "ACTIVO"].copy()
    return df


def aplicar_exclusiones(
    archivo_subida: pd.DataFrame,
    estado_carga: pd.Series,
    matricula_unificada_32: pd.DataFrame,
    repo_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    """Aplica exclusiones y forzados sobre los DataFrames del pipeline.

    Returns
    -------
    archivo_subida, estado_carga, matricula_unificada_32, auditoria_mc
        auditoria_mc contiene el log de acciones aplicadas (puede estar vacío).
    """
    exc = cargar_exclusiones(repo_dir)
    if exc.empty:
        return archivo_subida, estado_carga, matricula_unificada_32, pd.DataFrame()

    archivo_subida = archivo_subida.copy()
    estado_carga = estado_carga.copy()
    matricula_unificada_32 = matricula_unificada_32.copy()

    # Inicializar columnas de trazabilidad
    archivo_subida["EXCLUSION_MC"] = 0
    archivo_subida["EXCLUSION_MC_MOTIVO"] = ""
    archivo_subida["FOR_ING_ACT_FORZADO_MC"] = pd.NA

    audit_rows: list[dict] = []

    for _, regla in exc.iterrows():
        codcli = str(regla["CODCLI"]).strip()
        accion = str(regla["ACCION"]).strip().upper()
        motivo = str(regla.get("MOTIVO", ""))
        mask = archivo_subida["CODCLI"].astype(str).str.strip() == codcli

        n_match = int(mask.sum())
        if n_match == 0:
            audit_rows.append({
                "CODCLI": codcli, "ACCION": accion, "RESULTADO": "NO_ENCONTRADO",
                "FOR_ORIGINAL": None, "FOR_FORZADO": None, "MOTIVO": motivo,
            })
            continue

        if accion == "ELIMINAR":
            estado_carga.loc[mask] = _ESTADO_EXCLUIDO
            archivo_subida.loc[mask, "EXCLUSION_MC"] = 1
            archivo_subida.loc[mask, "EXCLUSION_MC_MOTIVO"] = motivo
            # Eliminar de matricula_unificada_32 por índice compartido
            idx_to_drop = mask[mask].index.intersection(matricula_unificada_32.index)
            matricula_unificada_32 = matricula_unificada_32.drop(idx_to_drop)
            audit_rows.append({
                "CODCLI": codcli, "ACCION": "ELIMINAR", "RESULTADO": "APLICADO",
                "FOR_ORIGINAL": None, "FOR_FORZADO": None, "MOTIVO": motivo,
            })

        elif accion == "MANTENER":
            for_forzado_raw = regla.get("FOR_ING_ACT_FORZADO", "")
            if pd.notna(for_forzado_raw) and str(for_forzado_raw).strip():
                for_forzado = int(float(str(for_forzado_raw).strip()))
                for_original = archivo_subida.loc[mask, "FOR_ING_ACT"].values[0] if n_match > 0 else None
                archivo_subida.loc[mask, "FOR_ING_ACT"] = for_forzado
                archivo_subida.loc[mask, "EXCLUSION_MC"] = 1
                archivo_subida.loc[mask, "EXCLUSION_MC_MOTIVO"] = motivo
                archivo_subida.loc[mask, "FOR_ING_ACT_FORZADO_MC"] = for_forzado
                # Actualizar en matricula_unificada_32 por índice compartido
                idx_to_update = mask[mask].index.intersection(matricula_unificada_32.index)
                if len(idx_to_update) > 0:
                    matricula_unificada_32.loc[idx_to_update, "FOR_ING_ACT"] = for_forzado
                audit_rows.append({
                    "CODCLI": codcli, "ACCION": "MANTENER_FORZAR_FOR",
                    "RESULTADO": "APLICADO",
                    "FOR_ORIGINAL": for_original, "FOR_FORZADO": for_forzado,
                    "MOTIVO": motivo,
                })
            else:
                audit_rows.append({
                    "CODCLI": codcli, "ACCION": "MANTENER_SIN_CAMBIO",
                    "RESULTADO": "APLICADO",
                    "FOR_ORIGINAL": None, "FOR_FORZADO": None, "MOTIVO": motivo,
                })

    auditoria_mc = pd.DataFrame(audit_rows)
    return archivo_subida, estado_carga, matricula_unificada_32, auditoria_mc
