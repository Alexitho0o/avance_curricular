#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


def _must_have(df: pd.DataFrame, cols: list[str], sheet: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"[{sheet}] faltan columnas: {missing}")


def _check_4cols(df: pd.DataFrame, sheet: str) -> list[str]:
    errors: list[str] = []
    req = ["PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "VIG"]
    _must_have(df, req, sheet)

    prom_pri = pd.to_numeric(df["PROM_PRI_SEM"], errors="coerce")
    prom_seg = pd.to_numeric(df["PROM_SEG_SEM"], errors="coerce")
    asi_ins = pd.to_numeric(df["ASI_INS_HIS"], errors="coerce")
    asi_apr = pd.to_numeric(df["ASI_APR_HIS"], errors="coerce")
    vig = pd.to_numeric(df["VIG"], errors="coerce")

    bad_prom_pri = ~((prom_pri == 0) | prom_pri.between(100, 700))
    bad_prom_seg = ~((prom_seg == 0) | prom_seg.between(100, 700))
    bad_asi_ins = ~asi_ins.between(0, 200)
    bad_asi_apr = ~asi_apr.between(0, 200)
    bad_apr_ins = asi_apr > asi_ins

    if int(bad_prom_pri.fillna(False).sum()) > 0:
        errors.append(f"[{sheet}] PROM_PRI_SEM fuera de rango: {int(bad_prom_pri.fillna(False).sum())}")
    if int(bad_prom_seg.fillna(False).sum()) > 0:
        errors.append(f"[{sheet}] PROM_SEG_SEM fuera de rango: {int(bad_prom_seg.fillna(False).sum())}")
    if int(bad_asi_ins.fillna(False).sum()) > 0:
        errors.append(f"[{sheet}] ASI_INS_HIS fuera de rango: {int(bad_asi_ins.fillna(False).sum())}")
    if int(bad_asi_apr.fillna(False).sum()) > 0:
        errors.append(f"[{sheet}] ASI_APR_HIS fuera de rango: {int(bad_asi_apr.fillna(False).sum())}")
    if int(bad_apr_ins.fillna(False).sum()) > 0:
        errors.append(f"[{sheet}] ASI_APR_HIS > ASI_INS_HIS: {int(bad_apr_ins.fillna(False).sum())}")

    vig0 = vig == 0
    bad_vig0 = vig0 & ((prom_pri != 0) | (prom_seg != 0) | (asi_ins != 0) | (asi_apr != 0))
    if int(bad_vig0.fillna(False).sum()) > 0:
        errors.append(f"[{sheet}] regla VIG=0 => 4 columnas=0 incumplida: {int(bad_vig0.fillna(False).sum())}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida 4 columnas MU y regla VIG=0")
    parser.add_argument("--excel", required=True, help="Ruta a archivo_listo_para_sies.xlsx")
    args = parser.parse_args()

    excel_path = Path(args.excel).expanduser().resolve()
    if not excel_path.exists():
        print(f"ERROR: no existe archivo {excel_path}")
        return 2

    arch = pd.read_excel(excel_path, sheet_name="ARCHIVO_LISTO_SUBIDA")
    mu32 = pd.read_excel(excel_path, sheet_name="MATRICULA_UNIFICADA_32")

    errors = []
    errors.extend(_check_4cols(arch, "ARCHIVO_LISTO_SUBIDA"))
    errors.extend(_check_4cols(mu32, "MATRICULA_UNIFICADA_32"))

    if "VIG_ESPERADO_DA" in arch.columns and "FLAG_INCONSISTENCIA_VIG" in arch.columns:
        print("OK: columnas de trazabilidad DA presentes")
    else:
        errors.append("[ARCHIVO_LISTO_SUBIDA] faltan columnas VIG_ESPERADO_DA / FLAG_INCONSISTENCIA_VIG")

    if errors:
        print("VALIDACION: FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("VALIDACION: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
