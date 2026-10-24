from __future__ import annotations

import unittest

import pandas as pd

from caracterizacion_estado_kpi import es_titulado_kpi, mascara_titulado_kpi


class EsTituladoKpiTests(unittest.TestCase):
    def test_alumno_regular_vigente_no_es_titulado(self):
        self.assertFalse(es_titulado_kpi("VIGENTE", "1 - ALUMNO REGULAR"))

    def test_reincorporacion_de_actividades_no_es_titulado(self):
        # Caso real detectado en 2026 P3: ESTADOACADEMICO=VIGENTE con
        # SITUACION='38 - REINCORPORACION DE ACTIVIDADES'. No debe excluirse
        # como titulado en ninguna sección KPI.
        self.assertFalse(
            es_titulado_kpi("VIGENTE", "38 - REINCORPORACION DE ACTIVIDADES")
        )

    def test_situacion_titulado_aprobado_con_estado_vigente_es_titulado(self):
        # Caso de desfase administrativo que motivó el FIX #1 de la
        # Sección 1.2.C: ESTADOACADEMICO aun dice VIGENTE pero SITUACION ya
        # refleja titulo aprobado.
        self.assertTrue(
            es_titulado_kpi("VIGENTE", "5 - TITULADO APROBADO")
        )

    def test_estado_titulado_es_titulado_sin_importar_situacion(self):
        self.assertTrue(es_titulado_kpi("TITULADO", "1 - ALUMNO REGULAR"))

    def test_valores_nulos_no_son_titulado(self):
        self.assertFalse(es_titulado_kpi(None, None))
        self.assertFalse(es_titulado_kpi(float("nan"), float("nan")))


class MascaraTituladoKpiTests(unittest.TestCase):
    def test_mascara_vectorizada_coincide_con_version_escalar(self):
        estados = pd.Series(
            ["VIGENTE", "VIGENTE", "VIGENTE", "TITULADO", "ELIMINADO"],
            index=[10, 20, 30, 40, 50],
        )
        situaciones = pd.Series(
            [
                "1 - ALUMNO REGULAR",
                "38 - REINCORPORACION DE ACTIVIDADES",
                "5 - TITULADO APROBADO",
                "1 - ALUMNO REGULAR",
                "1 - ALUMNO REGULAR",
            ],
            index=[10, 20, 30, 40, 50],
        )

        esperado = pd.Series(
            [es_titulado_kpi(e, s) for e, s in zip(estados, situaciones)],
            index=estados.index,
        )
        resultado = mascara_titulado_kpi(estados, situaciones)

        pd.testing.assert_series_equal(resultado, esperado, check_names=False)
        self.assertEqual(resultado.index.tolist(), estados.index.tolist())

    def test_mascara_preserva_indice_no_contiguo(self):
        estados = pd.Series(["VIGENTE", "VIGENTE"], index=[7, 99])
        situaciones = pd.Series(
            ["1 - ALUMNO REGULAR", "5 - TITULADO APROBADO"], index=[7, 99]
        )
        resultado = mascara_titulado_kpi(estados, situaciones)
        self.assertFalse(resultado.loc[7])
        self.assertTrue(resultado.loc[99])


if __name__ == "__main__":
    unittest.main()
