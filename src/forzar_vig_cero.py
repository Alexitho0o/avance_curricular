"""
src/forzar_vig_cero.py
======================
Regla institucional: forzar VIG = 0 para nómina manual MU2026.

Criterio normativo (Manual de Proceso Matrícula Unificada 2026):
    VIG = 0 → Estudiante sin matrícula. Debe permanecer en el archivo con todos
    los campos obligatorios completos, pero NO se contabiliza en la matrícula
    total ni en la asignación de beneficios estudiantiles.

Esta función se aplica justo antes de exportar el CSV oficial PES_READY,
después de que pes_df ya tiene exactamente MATRICULA_UNIFICADA_COLUMNS.

Llamada desde _generar_pes_ready_y_copiar() en codigo_gobernanza_v2.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Normalización de claves
# ---------------------------------------------------------------------------

def _norm_ndoc(val: object) -> str:
    """Elimina puntos, guiones y espacios del N_DOC; devuelve solo dígitos."""
    s = re.sub(r"[\.\-\s]", "", str(val).strip())
    return s


def _norm_dv(val: object) -> str:
    """Elimina puntos, guiones y espacios del DV; convierte a mayúscula."""
    s = re.sub(r"[\.\-\s]", "", str(val).strip())
    return s.upper()


def _clave_rut(ndoc: object, dv: object) -> str:
    return f"{_norm_ndoc(ndoc)}-{_norm_dv(dv)}"


# ---------------------------------------------------------------------------
# Carga y validación de la nómina
# ---------------------------------------------------------------------------

def _cargar_nomina(tsv_path: Path) -> tuple[set[str], list[dict[str, str]]]:
    """
    Lee el TSV con cabecera N_DOC / DV.
    Devuelve (set_claves_unicas, lista_de_filas_para_auditoria).
    Imprime advertencia si hay duplicados en la nómina.
    """
    df = pd.read_csv(
        tsv_path, sep="\t", dtype=str,
        keep_default_na=False, encoding="utf-8",
    )
    df.columns = [c.strip() for c in df.columns]
    if "N_DOC" not in df.columns or "DV" not in df.columns:
        raise ValueError(
            f"El TSV '{tsv_path}' debe tener columnas N_DOC y DV. "
            f"Columnas encontradas: {list(df.columns)}"
        )

    filas: list[dict[str, str]] = []
    claves: list[str] = []
    for _, row in df.iterrows():
        clave = _clave_rut(row["N_DOC"], row["DV"])
        claves.append(clave)
        filas.append({
            "N_DOC": str(row["N_DOC"]).strip(),
            "DV": str(row["DV"]).strip(),
            "CLAVE_RUT_DV": clave,
        })

    # Detectar duplicados en la nómina
    from collections import Counter
    conteo = Counter(claves)
    duplicados = {k: v for k, v in conteo.items() if v > 1}
    if duplicados:
        print(
            f"  ⚠️  Nómina VIG=0: {len(duplicados)} clave(s) duplicada(s) — "
            "se procesarán de igual forma, sin detener el proceso:"
        )
        for dup, cnt in duplicados.items():
            print(f"       {dup}  ({cnt} veces en nómina)")

    return set(claves), filas


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def aplicar_nomina_vig_cero(
    pes_df: pd.DataFrame,
    nomina_path: Path,
    output_dir: Path,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """
    Fuerza VIG = '0' en *pes_df* para todos los N_DOC+DV de la nómina manual.

    Restricciones:
      * No elimina filas.
      * No crea filas nuevas si el RUT no existe.
      * Solo modifica la columna VIG.
      * Conserva orden de filas y cantidad/orden de columnas.
      * Funciona con N_DOC como número, texto, con puntos/guiones/espacios.
      * Funciona con DV en minúscula, mayúscula, con espacios.

    Genera auditoría en output_dir / 'auditoria_ruts_forzados_vigencia_0.csv'.

    Retorna (pes_df_modificado, reporte_dict).
    """
    claves_nomina, filas_nomina = _cargar_nomina(nomina_path)

    n_nomina_total = len(filas_nomina)
    n_nomina_unicas = len(claves_nomina)

    filas_antes = len(pes_df)
    cols_antes = list(pes_df.columns)

    # Trabajo sobre copia — conserva orden de filas
    df = pes_df.copy()

    # Claves normalizadas del dataframe
    clave_serie = (
        df["N_DOC"].apply(_norm_ndoc) + "-" + df["DV"].apply(_norm_dv)
    )
    clave_serie.index = df.index  # garantía explícita

    # Máscara de coincidencia
    mask_en_nomina = clave_serie.isin(claves_nomina)

    # --- Aplicar VIG = '0' y construir auditoría por fila del dataframe ----
    audit_rows: list[dict[str, object]] = []
    claves_encontradas: set[str] = set()
    total_forzados = 0
    total_ya_vig0 = 0

    for idx in df.index[mask_en_nomina]:
        clave = clave_serie.at[idx]
        claves_encontradas.add(clave)
        vig_antes = str(df.at[idx, "VIG"]).strip()

        if vig_antes == "0":
            accion = "YA_ESTABA_VIG_0"
            total_ya_vig0 += 1
            vig_despues = "0"
        else:
            df.at[idx, "VIG"] = "0"
            accion = "FORZADO_A_VIG_0"
            total_forzados += 1
            vig_despues = "0"

        audit_rows.append({
            "N_DOC": df.at[idx, "N_DOC"],
            "DV": df.at[idx, "DV"],
            "CLAVE_RUT_DV": clave,
            "ENCONTRADO_EN_ARCHIVO": "SI",
            "VIG_ANTES": vig_antes,
            "VIG_DESPUES": vig_despues,
            "ACCION": accion,
            "OBSERVACION": "",
        })

    # --- Registrar RUT/DV de nómina no encontrados (sin duplicar) -----------
    claves_no_encontradas = claves_nomina - claves_encontradas
    # Una sola fila de auditoría por clave no encontrada (primer occurrence)
    vistas_nf: set[str] = set()
    for fila_nom in filas_nomina:
        c = fila_nom["CLAVE_RUT_DV"]
        if c in claves_no_encontradas and c not in vistas_nf:
            vistas_nf.add(c)
            audit_rows.append({
                "N_DOC": fila_nom["N_DOC"],
                "DV": fila_nom["DV"],
                "CLAVE_RUT_DV": c,
                "ENCONTRADO_EN_ARCHIVO": "NO",
                "VIG_ANTES": "",
                "VIG_DESPUES": "",
                "ACCION": "NO_ENCONTRADO_EN_ARCHIVO",
                "OBSERVACION": "RUT/DV de nómina no encontrado en dataframe final",
            })

    # --- Guardar auditoría --------------------------------------------------
    audit_path = output_dir / "auditoria_ruts_forzados_vigencia_0.csv"
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False, encoding="utf-8")

    # --- Validaciones post-aplicación ---------------------------------------
    filas_despues = len(df)
    cols_despues = list(df.columns)
    sin_cambio_filas = filas_antes == filas_despues
    sin_cambio_cols = cols_antes == cols_despues

    # Verificar que todos los encontrados quedaron con VIG = '0'
    mask_post = clave_serie.isin(claves_encontradas)
    vig_post_vals = df.loc[mask_post, "VIG"].astype(str).str.strip()
    n_no_cero_post = int((vig_post_vals != "0").sum())

    # --- Resumen por consola ------------------------------------------------
    sep = "  " + "─" * 61
    print(sep)
    print("  Regla VIG=0 · nómina institucional MU2026")
    print(sep)
    print(f"  Total RUT/DV en nómina manual        : {n_nomina_total}"
          f" ({n_nomina_unicas} únicas)")
    print(f"  Total encontrados en dataframe final : {len(claves_encontradas)}")
    print(f"  Total no encontrados                 : {len(claves_no_encontradas)}")
    print(f"  Total forzados a VIG = 0             : {total_forzados}")
    print(f"  Total que ya venían con VIG = 0      : {total_ya_vig0}")
    print(f"  Total de filas antes de aplicar      : {filas_antes}")
    print(f"  Total de filas después de aplicar    : {filas_despues}")
    print(f"  Sin eliminación de filas             : "
          f"{'✅ Confirmado' if sin_cambio_filas else '❌ ERROR — filas eliminadas'}")
    print(f"  Sin cambio en columnas               : "
          f"{'✅ Confirmado' if sin_cambio_cols else '❌ ERROR — columnas alteradas'}")
    print(f"  Todos los encontrados con VIG = 0    : "
          f"{'✅ Confirmado' if n_no_cero_post == 0 else f'❌ ERROR — {n_no_cero_post} filas sin VIG=0'}")
    print(f"  Auditoría generada en                : {audit_path}")
    print(sep)

    if not sin_cambio_filas:
        raise RuntimeError(
            f"[forzar_vig_cero] Se eliminaron filas: {filas_antes} → {filas_despues}. ABORTANDO."
        )
    if not sin_cambio_cols:
        raise RuntimeError(
            f"[forzar_vig_cero] Columnas alteradas. ABORTANDO."
        )

    report: dict[str, object] = {
        "n_nomina_total": n_nomina_total,
        "n_nomina_unicas": n_nomina_unicas,
        "n_encontrados": len(claves_encontradas),
        "n_no_encontrados": len(claves_no_encontradas),
        "total_forzados": total_forzados,
        "total_ya_vig0": total_ya_vig0,
        "filas_antes": filas_antes,
        "filas_despues": filas_despues,
        "columnas_sin_cambio": sin_cambio_cols,
        "filas_sin_cambio": sin_cambio_filas,
        "todos_encontrados_con_vig0": n_no_cero_post == 0,
        "audit_path": str(audit_path),
    }

    return df, report
