from __future__ import annotations

import unittest
from datetime import date

from caracterizacion_limesurvey_policy import (
    CATEGORIA_EN_VENTANA,
    CATEGORIA_FECHA_INVALIDA,
    CATEGORIA_FECHA_POSTERIOR,
    CATEGORIA_NO_OBJETIVO_ANOINGRESO,
    CATEGORIA_REZAGADO,
    clasificar_pendiente_limesurvey,
)


class ClasificacionPendienteLimeSurveyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inicio = date(2026, 8, 26)
        self.fin = date(2026, 8, 27)

    def clasificar(self, fecha: date | None, ano_ingreso: object = 2026):
        return clasificar_pendiente_limesurvey(
            fecha,
            ano_ingreso=ano_ingreso,
            anio_objetivo=2026,
            ventana_inicio=self.inicio,
            ventana_fin=self.fin,
        )

    def test_fecha_en_ventana_es_diaria(self):
        resultado = self.clasificar(date(2026, 8, 26))

        self.assertEqual(resultado.categoria, CATEGORIA_EN_VENTANA)
        self.assertTrue(resultado.es_objetivo)
        self.assertTrue(resultado.en_ventana)
        self.assertFalse(resultado.es_rezagado)

    def test_fecha_anterior_es_rezagada_dentro_del_ano_objetivo(self):
        resultado = self.clasificar(date(2026, 8, 12))

        self.assertEqual(resultado.categoria, CATEGORIA_REZAGADO)
        self.assertFalse(resultado.en_ventana)
        self.assertTrue(resultado.es_rezagado)

    def test_anoingreso_anterior_no_es_poblacion_objetivo(self):
        resultado = self.clasificar(date(2026, 8, 26), ano_ingreso=2025)

        self.assertEqual(resultado.categoria, CATEGORIA_NO_OBJETIVO_ANOINGRESO)
        self.assertFalse(resultado.es_objetivo)
        self.assertFalse(resultado.en_ventana)
        self.assertFalse(resultado.es_rezagado)

    def test_fecha_invalida_queda_visible_fuera_de_la_particion_temporal(self):
        resultado = self.clasificar(None)

        self.assertEqual(resultado.categoria, CATEGORIA_FECHA_INVALIDA)
        self.assertFalse(resultado.en_ventana)
        self.assertFalse(resultado.es_rezagado)

    def test_fecha_posterior_no_se_clasifica_como_rezagada(self):
        resultado = self.clasificar(date(2026, 8, 28))

        self.assertEqual(resultado.categoria, CATEGORIA_FECHA_POSTERIOR)
        self.assertFalse(resultado.en_ventana)
        self.assertFalse(resultado.es_rezagado)

    def test_ventana_invertida_falla(self):
        with self.assertRaises(ValueError):
            clasificar_pendiente_limesurvey(
                date(2026, 8, 26),
                ano_ingreso=2026,
                anio_objetivo=2026,
                ventana_inicio=self.fin,
                ventana_fin=self.inicio,
            )


if __name__ == "__main__":
    unittest.main()
