"""Pruebas de unidades y combinación de vías, con opciones ficticias."""
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cuadrar_totales_h002d import count,combine,compatible_profile


class TotalesH002d(unittest.TestCase):
    def test_blanco_no_es_cero(self):
        self.assertIsNone(count(''))
        self.assertEqual(count(0),0)

    def test_dos_vias_concordantes(self):
        self.assertEqual(combine([],['OPCION_A'],['OPCION_A']),'CALCE_UNICO')

    def test_tercera_via_contradice(self):
        self.assertEqual(combine(['OPCION_B'],['OPCION_A'],['OPCION_A']),'CONFLICTO')

    def test_una_via_no_resuelve(self):
        self.assertEqual(combine([],[],['OPCION_A']),'CALCE_DEBIL')

    def test_varios_archivos_una_sola_via(self):
        self.assertEqual(combine([],[],['OPCION_A','OPCION_A','OPCION_A']),'CALCE_DEBIL')

    def test_ambigua_no_es_segundo_voto_univoco(self):
        self.assertEqual(combine([],['OPCION_A'],['OPCION_A','OPCION_B']),'CALCE_DEBIL')

    def test_ninguna_via(self):
        self.assertEqual(combine([],[],[]),'SIN_CALCE')

    def test_conteo_no_admite_fraccion_ni_negativo(self):
        with self.assertRaises(ValueError):count('1.5')
        with self.assertRaises(ValueError):count('-1')

    def test_igualdad_de_total_no_vence_perfil_contrario(self):
        self.assertFalse(compatible_profile([['8','1']],['4','3']))

    def test_perfil_desconocido_no_se_inventa(self):
        self.assertTrue(compatible_profile([],['4','3']))


if __name__=='__main__':unittest.main(verbosity=2)
