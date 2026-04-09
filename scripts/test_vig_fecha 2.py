#!/usr/bin/env python3
"""Tests for motor_vig_fecha.py — VIG + FECHA_MATRICULA derivation."""
import unittest
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.motor_vig_fecha import derive_vig, derive_fecha_matricula, run_validations


def _make_row(**kw):
    """Helper: crea un DataFrame de 1 fila con defaults razonables."""
    defaults = {
        "CODCLI": "20261TEST001",
        "_RUT_NUM": 12345678,
        "ESTADOACADEMICO": "VIGENTE",
        "SITUACION": "1 - ALUMNO REGULAR",
        "FECHAMATRICULA": "15/01/2026",
        "ANOINGRESO": 2026,
        "PERIODOINGRESO": 1,
        "ANOMATRICULA": 2026,
        "PERIODOMATRICULA": 1,
    }
    defaults.update(kw)
    return pd.DataFrame([defaults])


# ═══════════════════════════════════════════════════════════════════════════
# Test VIG derivation
# ═══════════════════════════════════════════════════════════════════════════

class TestVig(unittest.TestCase):
    """Tests for derive_vig()."""

    def test_vigente_gives_1(self):
        da = _make_row(ESTADOACADEMICO="VIGENTE")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 1)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_01")

    def test_eliminado_gives_0(self):
        da = _make_row(ESTADOACADEMICO="ELIMINADO")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 0)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_02")

    def test_suspendido_gives_0(self):
        da = _make_row(ESTADOACADEMICO="SUSPENDIDO")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 0)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_03")

    def test_egresado_gives_2(self):
        da = _make_row(ESTADOACADEMICO="EGRESADO")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 2)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_04")

    def test_titulado_gives_0(self):
        da = _make_row(ESTADOACADEMICO="TITULADO")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 0)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_05")

    def test_null_estadoacademico_fallback_1(self):
        da = _make_row(ESTADOACADEMICO=None)
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 1)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_10")

    def test_empty_string_fallback_1(self):
        da = _make_row(ESTADOACADEMICO="")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 1)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_10")

    def test_unknown_value_fallback_1(self):
        da = _make_row(ESTADOACADEMICO="DESCONOCIDO_XYZ")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 1)
        self.assertEqual(da.iloc[0]["VIG_REGLA"], "R_VIG_11")

    def test_case_insensitive(self):
        da = _make_row(ESTADOACADEMICO="vigente")
        da = derive_vig(da)
        self.assertEqual(da.iloc[0]["VIG"], 1)

    def test_vig_in_catalogo(self):
        """VIG must always be 0, 1, or 2."""
        for ea in ["VIGENTE", "ELIMINADO", "SUSPENDIDO", "EGRESADO", "TITULADO", None, ""]:
            da = _make_row(ESTADOACADEMICO=ea)
            da = derive_vig(da)
            self.assertIn(da.iloc[0]["VIG"], [0, 1, 2], f"ESTADOACADEMICO={ea}")


# ═══════════════════════════════════════════════════════════════════════════
# Test FECHA_MATRICULA derivation
# ═══════════════════════════════════════════════════════════════════════════

class TestFechaMatricula(unittest.TestCase):
    """Tests for derive_fecha_matricula()."""

    def test_valid_date_formatted(self):
        da = _make_row(FECHAMATRICULA="15-01-2026")
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "15/01/2026")
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA_REGLA"], "R_FM_01")

    def test_valid_date_slash_format(self):
        da = _make_row(FECHAMATRICULA="31/12/2025")
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "31/12/2025")

    def test_null_date_fallback_1900(self):
        da = _make_row(FECHAMATRICULA=None)
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "01/01/1900")
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA_REGLA"], "R_FM_03")

    def test_nan_date_fallback_1900(self):
        da = _make_row(FECHAMATRICULA=np.nan)
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "01/01/1900")

    def test_invalid_string_fallback_1900(self):
        da = _make_row(FECHAMATRICULA="INVALIDO")
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "01/01/1900")
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA_REGLA"], "R_FM_03")

    def test_format_dd_mm_yyyy(self):
        """Output format must always be dd/mm/yyyy."""
        import re
        pat = re.compile(r"^\d{2}/\d{2}/\d{4}$")
        for fecha in ["15-01-2026", "2025-12-31", "01/03/2026", None]:
            da = _make_row(FECHAMATRICULA=fecha)
            da = derive_fecha_matricula(da)
            val = da.iloc[0]["FECHA_MATRICULA"]
            self.assertTrue(pat.match(val), f"Format mismatch: {val} from {fecha}")


# ═══════════════════════════════════════════════════════════════════════════
# Test Validations
# ═══════════════════════════════════════════════════════════════════════════

class TestValidations(unittest.TestCase):
    """Tests for run_validations()."""

    def _make_derived(self, **kw):
        da = _make_row(**kw)
        da = derive_vig(da)
        da = derive_fecha_matricula(da)
        return da

    def test_clean_no_bloqueantes(self):
        da = self._make_derived()
        findings = run_validations(da)
        bloq = [f for f in findings if f["severidad"] == "BLOQUEANTE"]
        self.assertEqual(len(bloq), 0)

    def test_vig0_info(self):
        da = self._make_derived(ESTADOACADEMICO="ELIMINADO")
        findings = run_validations(da)
        info = [f for f in findings if f["id"] == "V_VIG0_MARCADO_ROJO"]
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0]["n"], 1)

    def test_coherencia_vig_estado(self):
        """If we manually set VIG wrong, coherence check should catch it."""
        da = _make_row(ESTADOACADEMICO="ELIMINADO")
        da = derive_vig(da)
        da = derive_fecha_matricula(da)
        # VIG should be 0 for ELIMINADO; force wrong value
        da.at[da.index[0], "VIG"] = 1
        findings = run_validations(da)
        coherence = [f for f in findings if f["id"] == "V_COHERENCIA_VIG_ESTADO"]
        self.assertEqual(len(coherence), 1)
        self.assertEqual(coherence[0]["severidad"], "BLOQUEANTE")


# ═══════════════════════════════════════════════════════════════════════════
# Test Golden Cases (from real data)
# ═══════════════════════════════════════════════════════════════════════════

class TestGoldenCases(unittest.TestCase):
    """Tests verifying golden cases against expected values."""

    def test_gc01_vigente(self):
        da = _make_row(CODCLI="20171NETMRE016", ESTADOACADEMICO="VIGENTE",
                       FECHAMATRICULA="02/03/2026")
        da = derive_vig(da)
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["VIG"], 1)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "02/03/2026")

    def test_gc02_eliminado(self):
        da = _make_row(CODCLI="20241TCIB050", ESTADOACADEMICO="ELIMINADO",
                       FECHAMATRICULA="30/12/2025")
        da = derive_vig(da)
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["VIG"], 0)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "30/12/2025")

    def test_gc03_suspendido(self):
        da = _make_row(CODCLI="20251CIINF029", ESTADOACADEMICO="SUSPENDIDO",
                       FECHAMATRICULA="26/02/2026")
        da = derive_vig(da)
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["VIG"], 0)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "26/02/2026")

    def test_gc06_eliminado_2026(self):
        da = _make_row(CODCLI="20251TCDA017", ESTADOACADEMICO="ELIMINADO",
                       FECHAMATRICULA="15/01/2026")
        da = derive_vig(da)
        da = derive_fecha_matricula(da)
        self.assertEqual(da.iloc[0]["VIG"], 0)
        self.assertEqual(da.iloc[0]["FECHA_MATRICULA"], "15/01/2026")


if __name__ == "__main__":
    unittest.main()
