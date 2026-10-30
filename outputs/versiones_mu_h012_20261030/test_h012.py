import unittest
from resolver import vote,reference_year

class Reglas(unittest.TestCase):
    def test_tres_personas(self):
        self.assertEqual(vote({i:{'V1'} for i in range(3)})[0],'V1')
    def test_ocultar_todas_las_filas_de_la_persona(self):
        pool={0:{'V1','V2'},1:{'V1'},2:{'V1'},3:{'V1'}}
        self.assertEqual(vote(pool,0),('V1','UNANIME',{'V1':3}))
        self.assertEqual(vote(pool,3)[1],'NO_UNANIME')
    def test_dos_insuficientes(self):
        self.assertEqual(vote({i:{'V1'} for i in range(3)},2)[1],'MENOS_DE_TRES_PERSONAS')
    def test_anio_en_orden(self):
        self.assertEqual(reference_year([2019,2021,2024],2020),2021)
        self.assertEqual(reference_year([2019,2021,2024],2021),2021)
        self.assertEqual(reference_year([2019,2021,2024],2026),2024)
    def test_sin_documentales(self):
        self.assertIsNone(reference_year([],2026))
