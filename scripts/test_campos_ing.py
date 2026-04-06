#!/usr/bin/env python3
"""
Test suite — Motor Campos ING (ANIO_ING_ACT, SEM_ING_ACT, ANIO_ING_ORI, SEM_ING_ORI)
Ejecutar: python3 -m pytest scripts/test_campos_ing.py -v
"""
import json
import unittest
from pathlib import Path

import pandas as pd
import numpy as np

# Importar funciones del motor
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from motor_campos_ing import (
    derive_anio_ing_act,
    derive_sem_ing_act,
    derive_campos_ori,
    run_validations,
    _lookup_programa_anterior,
    _lookup_tns_periodo,
    SEM_ACT_MAPEO,
    ANIO_ACT_RANGE,
    SEM_ACT_CATALOGO,
    SEM_ORI_CATALOGO,
)

BASE = Path(__file__).resolve().parent.parent
GOLDEN = BASE / "control" / "campos_ing_golden_cases.json"
TRACE  = BASE / "control" / "campos_ing_trace_long.tsv"


def _make_row(**kwargs):
    """Helper: crea un DataFrame de 1 fila con defaults."""
    defaults = {
        "CODCLI": "TEST001",
        "_RUT_NUM": 12345678,
        "ANOINGRESO": 2026,
        "PERIODOINGRESO": 1,
        "ANOMATRICULA": 2026,
        "PERIODOMATRICULA": 1,
        "CODCARPR": "IINF",
        "FOR_ING_ACT": 1,
        "TIENE_TNS_PREV_DA": 0,
        "TNS_PREV_MIN_ANO_DA": pd.NA,
        "TNS_PREV_CODCLI_EJEMPLO_DA": "",
    }
    defaults.update(kwargs)
    return pd.DataFrame([defaults])


class TestAnioIngAct(unittest.TestCase):
    """Tests para derivación ANIO_ING_ACT."""

    def test_01_anoingreso_directo(self):
        """R_ACT_01: ANOINGRESO válido → directo."""
        df = _make_row(ANOINGRESO=2025)
        df = derive_anio_ing_act(df)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT"], 2025)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT_REGLA"], "R_ACT_01")

    def test_02_anoingreso_1990(self):
        """R_ACT_01: Límite inferior rango."""
        df = _make_row(ANOINGRESO=1990)
        df = derive_anio_ing_act(df)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT"], 1990)

    def test_03_anoingreso_2026(self):
        """R_ACT_01: Límite superior rango."""
        df = _make_row(ANOINGRESO=2026)
        df = derive_anio_ing_act(df)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT"], 2026)

    def test_04_anoingreso_nulo_codcli_fallback(self):
        """R_ACT_03: ANOINGRESO nulo → inferir desde CODCLI."""
        df = _make_row(ANOINGRESO=pd.NA, CODCLI="20251IINF099")
        df = derive_anio_ing_act(df)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT"], 2025)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT_REGLA"], "R_ACT_03")

    def test_05_todo_nulo_default(self):
        """R_ACT_04: Sin fuente → default 2026."""
        df = _make_row(ANOINGRESO=pd.NA, CODCLI="XXXX")
        df = derive_anio_ing_act(df)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT"], 2026)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT_REGLA"], "R_ACT_04")

    def test_06_anoingreso_fuera_rango_fallback(self):
        """R_ACT_03: ANOINGRESO fuera de rango → intenta CODCLI."""
        df = _make_row(ANOINGRESO=1900, CODCLI="20241ICIB001")
        df = derive_anio_ing_act(df)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT"], 2024)
        self.assertEqual(df.iloc[0]["ANIO_ING_ACT_REGLA"], "R_ACT_03")


class TestSemIngAct(unittest.TestCase):
    """Tests para derivación SEM_ING_ACT."""

    def test_01_periodo_1(self):
        """R_SEM_01: PERIODOINGRESO=1 → SEM=1."""
        df = _make_row(PERIODOINGRESO=1)
        df = derive_sem_ing_act(df)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT"], 1)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT_REGLA"], "R_SEM_01")

    def test_02_periodo_2(self):
        """R_SEM_02: PERIODOINGRESO=2 → SEM=2."""
        df = _make_row(PERIODOINGRESO=2)
        df = derive_sem_ing_act(df)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT"], 2)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT_REGLA"], "R_SEM_02")

    def test_03_periodo_3_normalizado(self):
        """R_SEM_02: PERIODOINGRESO=3 → SEM=2 (normalización)."""
        df = _make_row(PERIODOINGRESO=3)
        df = derive_sem_ing_act(df)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT"], 2)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT_REGLA"], "R_SEM_02")

    def test_04_periodo_nulo_default(self):
        """R_SEM_04: PERIODOINGRESO nulo → default 1."""
        df = _make_row(PERIODOINGRESO=pd.NA)
        df = derive_sem_ing_act(df)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT"], 1)
        self.assertEqual(df.iloc[0]["SEM_ING_ACT_REGLA"], "R_SEM_04")

    def test_05_mapeo_coverage(self):
        """Verifica que el mapeo cubre valores 1, 2, 3."""
        self.assertEqual(SEM_ACT_MAPEO[1], 1)
        self.assertEqual(SEM_ACT_MAPEO[2], 2)
        self.assertEqual(SEM_ACT_MAPEO[3], 2)


class TestCamposOri(unittest.TestCase):
    """Tests para derivación ANIO_ING_ORI + SEM_ING_ORI."""

    def _derive_full(self, **row_kwargs):
        """Helper: ejecuta cadena completa ACT + ORI."""
        df = _make_row(**row_kwargs)
        df = derive_anio_ing_act(df)
        df = derive_sem_ing_act(df)
        # Mock trace FOR
        trace_for = pd.DataFrame([{
            "CODCLI": row_kwargs.get("CODCLI", "TEST001"),
            "FOR_ING_ACT": row_kwargs.get("FOR_ING_ACT", 1),
            "TIENE_TNS_PREV_DA": row_kwargs.get("TIENE_TNS_PREV_DA", 0),
            "TNS_PREV_MIN_ANO_DA": row_kwargs.get("TNS_PREV_MIN_ANO_DA", pd.NA),
            "TNS_PREV_CODCLI_EJEMPLO_DA": row_kwargs.get("TNS_PREV_CODCLI_EJEMPLO_DA", ""),
        }])
        h1 = pd.DataFrame(columns=["CODCLI", "_RUT_NUM", "CODCARR", "ANO", "PERIODO"])
        df = derive_campos_ori(df, h1, trace_for)
        return df

    def test_01_for1_copia(self):
        """FOR=1 → ORI = ACT."""
        df = self._derive_full(FOR_ING_ACT=1, ANOINGRESO=2024, PERIODOINGRESO=1)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], r["ANIO_ING_ACT"])
        self.assertEqual(r["SEM_ING_ORI"], r["SEM_ING_ACT"])
        self.assertEqual(r["ANIO_ING_ORI_REGLA"], "R_ORI_A01")

    def test_02_for11_tns(self):
        """FOR=11 con TNS → ORI = TNS año."""
        df = self._derive_full(FOR_ING_ACT=11, ANOINGRESO=2026,
                               TIENE_TNS_PREV_DA=1, TNS_PREV_MIN_ANO_DA=2021)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], 2021)
        self.assertEqual(r["ANIO_ING_ORI_REGLA"], "R_ORI_A02")

    def test_03_for11_sin_tns(self):
        """FOR=11 sin TNS → ORI = 1900/0."""
        df = self._derive_full(FOR_ING_ACT=11, ANOINGRESO=2026,
                               TIENE_TNS_PREV_DA=1, TNS_PREV_MIN_ANO_DA=pd.NA)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], 1900)
        self.assertEqual(r["SEM_ING_ORI"], 0)

    def test_04_for2_1900(self):
        """FOR=2 → ORI = 1900/0."""
        df = self._derive_full(FOR_ING_ACT=2, ANOINGRESO=2025)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], 1900)
        self.assertEqual(r["SEM_ING_ORI"], 0)
        self.assertEqual(r["ANIO_ING_ORI_REGLA"], "R_ORI_A04")

    def test_05_for3_sin_prev(self):
        """FOR=3 sin programa anterior → ORI = 1900/0."""
        df = self._derive_full(FOR_ING_ACT=3, ANOINGRESO=2025)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], 1900)
        self.assertEqual(r["SEM_ING_ORI"], 0)
        self.assertEqual(r["ANIO_ING_ORI_REGLA"], "R_ORI_A06")

    def test_06_for4_bloqueado(self):
        """FOR=4 → ORI = 1900/0."""
        df = self._derive_full(FOR_ING_ACT=4, ANOINGRESO=2026)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], 1900)
        self.assertEqual(r["SEM_ING_ORI"], 0)

    def test_07_coherencia_1900_sem0(self):
        """Invariante: ANIO_ORI=1900 → SEM_ORI=0."""
        df = self._derive_full(FOR_ING_ACT=2, ANOINGRESO=2026)
        r = df.iloc[0]
        self.assertEqual(r["ANIO_ING_ORI"], 1900)
        self.assertEqual(r["SEM_ING_ORI"], 0)


class TestValidations(unittest.TestCase):
    """Tests para validaciones normativas."""

    def _build_validated(self, **kwargs):
        df = _make_row(**kwargs)
        df = derive_anio_ing_act(df)
        df = derive_sem_ing_act(df)
        trace_for = pd.DataFrame([{
            "CODCLI": kwargs.get("CODCLI", "TEST001"),
            "FOR_ING_ACT": kwargs.get("FOR_ING_ACT", 1),
            "TIENE_TNS_PREV_DA": 0,
            "TNS_PREV_MIN_ANO_DA": pd.NA,
            "TNS_PREV_CODCLI_EJEMPLO_DA": "",
        }])
        h1 = pd.DataFrame(columns=["CODCLI", "_RUT_NUM", "CODCARR", "ANO", "PERIODO"])
        df = derive_campos_ori(df, h1, trace_for)
        return df

    def test_01_sin_errores(self):
        """Registro FOR=1 estándar no genera bloqueantes."""
        df = self._build_validated(ANOINGRESO=2026, PERIODOINGRESO=1, FOR_ING_ACT=1)
        findings = run_validations(df)
        bloq = [f for f in findings if f["severidad"] == "BLOQUEANTE"]
        self.assertEqual(len(bloq), 0)

    def test_02_for1_coherencia_ok(self):
        """FOR=1 → ORI == ACT no genera error."""
        df = self._build_validated(ANOINGRESO=2025, PERIODOINGRESO=2, FOR_ING_ACT=1)
        findings = run_validations(df)
        for1_err = [f for f in findings if f["id"] == "V_COHERENCIA_FOR1"]
        self.assertEqual(len(for1_err), 0)

    def test_03_catalogos_ok(self):
        """SEM_ING_ACT y SEM_ING_ORI en catálogo."""
        df = self._build_validated(ANOINGRESO=2026, PERIODOINGRESO=1, FOR_ING_ACT=1)
        r = df.iloc[0]
        self.assertIn(int(r["SEM_ING_ACT"]), SEM_ACT_CATALOGO)
        self.assertIn(int(r["SEM_ING_ORI"]), SEM_ORI_CATALOGO)


class TestGoldenCases(unittest.TestCase):
    """Verificación contra trace real si existe."""

    @classmethod
    def setUpClass(cls):
        if TRACE.exists():
            cls.trace = pd.read_csv(TRACE, sep="\t")
        else:
            cls.trace = None
        if GOLDEN.exists():
            with open(GOLDEN) as f:
                cls.golden = json.load(f)
        else:
            cls.golden = []

    def test_golden_against_trace(self):
        """Verifica golden cases contra trace real."""
        if self.trace is None or not self.golden:
            self.skipTest("No trace o golden cases disponible")

        for gc in self.golden:
            if gc.get("tipo"):
                continue  # skip reglas sintéticas
            codcli = gc.get("CODCLI")
            if not codcli:
                continue
            row = self.trace[self.trace["CODCLI"] == codcli]
            if len(row) == 0:
                continue
            r = row.iloc[0]
            for campo, val in gc["expected"].items():
                actual = r.get(campo)
                if pd.notna(actual):
                    self.assertEqual(int(actual), val,
                                     f"Golden {gc['id']}: {campo} esperado={val} real={int(actual)}")

    def test_regla_1900(self):
        """Invariante global: ANIO_ORI=1900 → SEM_ORI=0."""
        if self.trace is None:
            self.skipTest("No trace disponible")
        ori_1900 = self.trace[self.trace["ANIO_ING_ORI"] == 1900]
        bad = ori_1900[ori_1900["SEM_ING_ORI"] != 0]
        self.assertEqual(len(bad), 0, f"Hay {len(bad)} registros 1900 con SEM≠0")

    def test_for1_coherencia(self):
        """FOR=1 → ORI == ACT en todo el trace."""
        if self.trace is None:
            self.skipTest("No trace disponible")
        for1 = self.trace[self.trace["FOR_ING_ACT"] == 1]
        bad_anio = for1[for1["ANIO_ING_ORI"] != for1["ANIO_ING_ACT"]]
        bad_sem = for1[for1["SEM_ING_ORI"] != for1["SEM_ING_ACT"]]
        self.assertEqual(len(bad_anio), 0, f"{len(bad_anio)} FOR=1 con ANIO_ORI≠ANIO_ACT")
        self.assertEqual(len(bad_sem), 0, f"{len(bad_sem)} FOR=1 con SEM_ORI≠SEM_ACT")

    def test_sem_act_catalogo(self):
        """SEM_ING_ACT ∈ {1,2} en todo el trace."""
        if self.trace is None:
            self.skipTest("No trace disponible")
        bad = self.trace[~self.trace["SEM_ING_ACT"].isin([1, 2])]
        self.assertEqual(len(bad), 0, f"{len(bad)} con SEM_ACT fuera de catalogo")

    def test_sem_ori_catalogo(self):
        """SEM_ING_ORI ∈ {0,1,2} en todo el trace."""
        if self.trace is None:
            self.skipTest("No trace disponible")
        bad = self.trace[~self.trace["SEM_ING_ORI"].isin([0, 1, 2])]
        self.assertEqual(len(bad), 0, f"{len(bad)} con SEM_ORI fuera de catalogo")


if __name__ == "__main__":
    unittest.main()
