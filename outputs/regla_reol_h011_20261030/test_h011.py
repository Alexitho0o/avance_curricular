import unittest
from fractions import Fraction
from aplicar_h011 import semestres

class Conversion(unittest.TestCase):
    def test_bimestral(self):
        for nivel, exact, sem in [(20,8,8),(15,6,6),(13,Fraction(26,5),5),(12,Fraction(24,5),5),(10,4,4)]:
            self.assertEqual(semestres(nivel,'BIMESTRAL'),(exact,sem,''))
    def test_frontera_inclusiva(self):
        for nivel in (6,9):
            self.assertEqual(semestres(nivel,'BIMESTRAL')[2],'FRONTERA_REDONDEO')
    def test_trimestre(self):
        self.assertEqual(semestres(4,'TRIMESTRAL'),(Fraction(8,3),3,''))
    def test_semestre(self):
        self.assertEqual(semestres(5,'SEMESTRAL'),(5,5,''))
    def test_sin_regimen(self):
        self.assertIsNone(semestres(5,'S')[1])
