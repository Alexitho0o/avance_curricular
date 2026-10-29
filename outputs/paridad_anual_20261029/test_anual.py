"""Casos sintéticos del enlace conservador y de las unidades H002f."""
import unittest
from construir_anual import ident, umas_ident, selected, choose, classify_group, historical_state, family


class ParidadAnualTests(unittest.TestCase):
    def test_dv_cero(self):
        self.assertEqual(ident('R','12',0),ident('R','12','0'))
        self.assertEqual(umas_ident({'RUT':'12','DIG':0}),ident('R','12','0'))

    def test_sin_dv_no_fabricar(self):
        self.assertIsNone(ident('R','12',None))
        self.assertIsNone(umas_ident({'RUT':'12'}))

    def test_dv_discordante(self):
        self.assertIsNone(umas_ident({'RUT':'12-0','DIG':'K'}))

    def test_tipo_no_fusionado(self):
        self.assertNotEqual(ident('P','DOC_SIMBOLICO',''),ident('R','12','0'))

    def test_vig_cero_explicitamente(self):
        self.assertTrue(selected(2025,0))
        self.assertFalse(selected(2024,0))
        self.assertFalse(selected(2026,0))
        self.assertTrue(selected(2026,1))

    def test_no_mayoria_ni_primera_fila(self):
        a=('CLI_A','CAR','PLAN_A','RE','O');b=('CLI_B','CAR','PLAN_A','RE','O')
        self.assertEqual(choose([a,a,b]),(None,'VARIOS_EXPEDIENTES_COMPATIBLES'))

    def test_dos_planes_no_ultimo(self):
        a=('CLI_A','CAR','PLAN_A','RE','O');b=('CLI_A','CAR','PLAN_B','RE','O')
        self.assertEqual(choose([a,b]),(None,'VARIOS_PLANES_O_CONTEXTOS_ANUALES'))

    def test_extractos_solapados_no_suman(self):
        a=('CLI_A','CAR','PLAN_A','RE','O')
        self.assertEqual(choose([a,a]),(a,''))

    def test_total_no_cuadra_no_confirma(self):
        self.assertEqual(classify_group({'COD_A'},{'COD_A':False}),'UNICO_SIN_CUADRATURA')
        self.assertEqual(classify_group({'COD_A'},{'COD_A':True}),'CUADRA_UNICO')

    def test_repartido_no_oculto(self):
        self.assertEqual(classify_group({'COD_A','COD_B'},{'COD_A':True,'COD_B':True}),'REPARTIDO')

    def test_tolerancia_historica(self):
        self.assertEqual(historical_state(90,100),'APROXIMA')
        self.assertEqual(historical_state(110,100),'APROXIMA')
        self.assertEqual(historical_state(89,100),'NO_CUADRA')
        self.assertEqual(historical_state(100,100),'CUADRA_TOTAL')
        self.assertEqual(historical_state(0,0),'NO_CUADRA')

    def test_familia_conserva_jornada_sede(self):
        self.assertEqual(family('I162S2C83J4V2'),'I162S2C83J4')
        self.assertNotEqual(family('I162S2C83J3V1'),family('I162S2C83J4V1'))


if __name__=='__main__':unittest.main()
