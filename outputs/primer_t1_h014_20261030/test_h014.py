import unittest
from construir_v22 import evaluar
class D10(unittest.TestCase):
    dims=('PLAN_FICTICIO','2','4')
    def check(self,timeline,offers,p=True):
        return evaluar(timeline,2025,self.dims,p,lambda t:{'tipo':'REGULAR','duracion_control':8},offers)[2]
    def test_oferta_solo_del_anio_t1(self):
        self.assertEqual(self.check({2026:{('V2',self.dims)}},{(2026,'V2'):{('REGULAR','8')}}),'OFERTA_AÑO_T1')
    def test_no_usar_oferta_anterior(self):
        self.assertEqual(self.check({2026:{('V2',self.dims)}},{(2025,'V2'):{('REGULAR','8')}}),'SIN_OFERTA_ANIO_T1')
    def test_ausencia_individual(self):
        self.assertEqual(self.check({},{}),'SIN_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN')
    def test_no_saltar_primer_anio(self):
        self.assertEqual(self.check({2026:{('V1',self.dims),('V2',self.dims)},2027:{('V2',self.dims)}},{}),'PRIMER_T1_NO_UNICO')
    def test_tipo_duracion(self):
        self.assertEqual(self.check({2026:{('V2',self.dims)}},{(2026,'V2'):{('CONTINUIDAD','4')}}),'TIPO_O_DURACION_NO_COINCIDE')
    def test_sede(self):
        self.assertEqual(self.check({2026:{('V2',('PLAN_FICTICIO','3','4'))}},{}),'DIMENSIONES_DISTINTAS')
