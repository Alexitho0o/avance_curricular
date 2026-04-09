#!/usr/bin/env python3
"""
Tests de regresión: prioridad NIV_ACA (DA_NIVEL > Hoja1.NIVEL).

Caso trigger: RUT 16197084 / CODCLI 20251TLOG039
- Hoja1.NIVEL = {1,2,3,4,5} (nivel del ramo en malla, NO del alumno)
- DatosAlumnos.NIVEL = 4 (nivel académico real del alumno)
- Antes del fix: NIV_ACA=3 (tomaba Hoja1.NIVEL arbitrario)
- Después del fix: NIV_ACA=4 (toma DA_NIVEL correcto)

Uso:
    python scripts/test_niv_aca_priority.py --output-dir resultados
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def _load(output_dir: Path):
    xls = output_dir / "archivo_listo_para_sies.xlsx"
    if not xls.exists():
        sys.exit(f"FATAL: {xls} no existe. Ejecutar pipeline primero.")
    mu32 = pd.read_excel(xls, sheet_name="MATRICULA_UNIFICADA_32")
    arch = pd.read_excel(xls, sheet_name="ARCHIVO_LISTO_SUBIDA")
    return mu32, arch


# ── Test 1: caso concreto RUT 16197084 CODCLI 20251TLOG039 ───────────
def test_niv_aca_rut_16197084_tlog039(mu32: pd.DataFrame, arch: pd.DataFrame):
    """CODCLI 20251TLOG039 debe tener NIV_ACA=4 (DA_NIVEL), no 3 (Hoja1)."""
    rows = mu32[
        (mu32["N_DOC"].astype(str).str.strip() == "16197084")
        & (mu32["COD_CAR"] == 79)
    ]
    assert len(rows) == 1, f"Esperaba 1 fila COD_CAR=79, encontré {len(rows)}"
    niv = int(rows.iloc[0]["NIV_ACA"])
    assert niv == 4, f"NIV_ACA esperado 4, obtenido {niv}"

    # Verificar fuente en ARCHIVO_LISTO_SUBIDA
    tlog = arch[
        (arch["CODCLI"] == "20251TLOG039")
        & (arch["ESTADO_CARGA_PREGRADO"] == "OK_CARGA_PREGRADO")
    ]
    assert len(tlog) == 1, f"Esperaba 1 fila OK_CARGA para TLOG039, encontré {len(tlog)}"
    assert tlog.iloc[0]["NIV_ACA_FUENTE_FINAL"] == "DA_NIVEL", \
        f"Fuente esperada DA_NIVEL, obtenida {tlog.iloc[0]['NIV_ACA_FUENTE_FINAL']}"
    assert tlog.iloc[0]["NIV_ACA_METODO_FINAL"] == "PRIMARY_DATOS_ALUMNOS", \
        f"Método esperado PRIMARY_DATOS_ALUMNOS, obtenido {tlog.iloc[0]['NIV_ACA_METODO_FINAL']}"
    print("  PASS test_niv_aca_rut_16197084_tlog039")


# ── Test 2: global — DA_NIVEL siempre prioritario sobre INPUT ────────
def test_niv_aca_da_takes_priority_global(arch: pd.DataFrame):
    """Cuando DA_NIVEL existe, debe ser PRIMARY_DATOS_ALUMNOS, no SOURCE_INPUT."""
    ok = arch[arch["ESTADO_CARGA_PREGRADO"] == "OK_CARGA_PREGRADO"]
    # Filas con DA_NIVEL disponible deben tener PRIMARY_DATOS_ALUMNOS
    with_da = ok[ok["NIV_ACA_FUENTE_FINAL"] == "DA_NIVEL"]
    bad = with_da[with_da["NIV_ACA_METODO_FINAL"] != "PRIMARY_DATOS_ALUMNOS"]
    assert len(bad) == 0, f"{len(bad)} filas con DA_NIVEL pero método != PRIMARY_DATOS_ALUMNOS"
    print(f"  PASS test_niv_aca_da_takes_priority_global ({len(with_da)} filas DA_NIVEL)")


# ── Test 3: no debe haber SOURCE_INPUT cuando DA_NIVEL está disponible ──
def test_no_source_input_when_da_available(arch: pd.DataFrame):
    """El antiguo SOURCE_INPUT ya no debe aparecer cuando DA_NIVEL existe."""
    ok = arch[arch["ESTADO_CARGA_PREGRADO"] == "OK_CARGA_PREGRADO"]
    source_input = ok[ok["NIV_ACA_METODO_FINAL"] == "SOURCE_INPUT"]
    if len(source_input) > 0:
        # Verificar que ninguno de estos tenía DA_NIVEL disponible
        with_da = source_input[source_input["NIV_ACA_FUENTE_FINAL"] == "DA_NIVEL"]
        assert len(with_da) == 0, \
            f"{len(with_da)} filas usan SOURCE_INPUT teniendo DA_NIVEL"
    print(f"  PASS test_no_source_input_when_da_available ({len(source_input)} SOURCE_INPUT restantes)")


# ── Test 4: multicarrera mismo RUT — NIV_ACA independiente por CODCLI ──
def test_multicarrera_niv_aca_independent(mu32: pd.DataFrame):
    """
    RUT 16197084 tiene 2 carreras. Cada una puede tener NIV_ACA distinto,
    pero ninguna debe tener NIV_ACA=10 (que era el NIVEL de un ramo TITULADO).
    """
    rut = mu32[mu32["N_DOC"].astype(str).str.strip() == "16197084"]
    assert len(rut) == 2, f"Esperaba 2 carreras para RUT 16197084, encontré {len(rut)}"
    for _, row in rut.iterrows():
        niv = int(row["NIV_ACA"])
        assert niv != 10, f"COD_CAR={row['COD_CAR']} tiene NIV_ACA=10 (bug ramo Hoja1)"
        assert 1 <= niv <= 5, f"COD_CAR={row['COD_CAR']} NIV_ACA={niv} fuera de rango 1-5"
    print("  PASS test_multicarrera_niv_aca_independent")


def main():
    parser = argparse.ArgumentParser(description="Tests regresión NIV_ACA")
    parser.add_argument("--output-dir", default="resultados")
    args = parser.parse_args()
    out = Path(args.output_dir)
    mu32, arch = _load(out)

    passed = 0
    failed = 0
    tests = [
        ("test_niv_aca_rut_16197084_tlog039", lambda: test_niv_aca_rut_16197084_tlog039(mu32, arch)),
        ("test_niv_aca_da_takes_priority_global", lambda: test_niv_aca_da_takes_priority_global(arch)),
        ("test_no_source_input_when_da_available", lambda: test_no_source_input_when_da_available(arch)),
        ("test_multicarrera_niv_aca_independent", lambda: test_multicarrera_niv_aca_independent(mu32)),
    ]
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL {name}: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"  Resultados: {passed} PASS, {failed} FAIL de {len(tests)} tests")
    print(f"{'=' * 60}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
