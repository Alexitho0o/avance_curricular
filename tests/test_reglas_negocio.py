import unittest
from common.reglas_negocio import inicio_codigo_oferta


class InicioOfertaTests(unittest.TestCase):
    def test_programas_regular_y_continuidad_tienen_inicio_separado(self):
        rows = [{'anio': 2024, 'codigo_unico': 'I162S2C77J4V1', 'ano_inicio': 2024},
                {'anio': 2025, 'codigo_unico': 'I162S2C77J4V2', 'ano_inicio': 2024},
                {'anio': 2026, 'codigo_unico': 'I162S2C77J4V2', 'ano_inicio': 2024}]
        self.assertEqual(inicio_codigo_oferta(rows, 'I162S2C77J4V1')['anio_inicio_diccionario'], 2024)
        self.assertEqual(inicio_codigo_oferta(rows, 'I162S2C77J4V2')['anio_inicio_diccionario'], 2025)

    def test_sin_matricula_y_sin_vigencia_actual_conserva_inicio(self):
        rows = [{'anio': 2010, 'codigo_unico': 'otro'},
                {'anio': 2018, 'codigo_unico': 'programa', 'mrun': 0, 'vigencia': 3},
                {'anio': 2026, 'codigo_unico': 'otro'}]
        self.assertEqual(inicio_codigo_oferta(rows, 'programa')['anio_inicio_diccionario'], 2018)

    def test_sin_oferta_no_imputa_anio_mrun(self):
        r = inicio_codigo_oferta([], 'I162M2008N1')
        self.assertIsNone(r['anio_inicio_diccionario'])
        self.assertEqual(r['estado'], 'SIN_OFERTA_EN_FUENTE')

    def test_cobertura_limitada_y_orden_no_alteran_resultado(self):
        rows = [{'anio': 2010, 'codigo_unico': 'x'}, {'anio': 2020, 'codigo_unico': 'x'}]
        self.assertEqual(inicio_codigo_oferta(rows, 'x'), inicio_codigo_oferta(rows[::-1], 'x'))
        self.assertTrue(inicio_codigo_oferta(rows, 'x')['coincide_limite_inferior_fuente'])

    def test_clave_completa_y_validacion_anio(self):
        self.assertIsNone(inicio_codigo_oferta([{'anio': 2024, 'codigo_unico': 'I162S2C77J4V1'}], 'I162S2C77J4')['anio_inicio_diccionario'])
        with self.assertRaises(ValueError):
            inicio_codigo_oferta([{'anio': 'OFE_2024', 'codigo_unico': 'x'}], 'x')


if __name__ == '__main__':
    unittest.main()
