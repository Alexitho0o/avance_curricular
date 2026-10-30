"""Pruebas sintéticas: no usar el código para sortear ausencia de evidencia."""
import unittest
from construir import profile_check,txt,aggregate
class Tests(unittest.TestCase):
 def p(self,t='3',d=4):return [{'tipo_codigo':t,'duracion_diagnostica_semestres':d}]
 def o(self,t='Plan Regular de Continuidad',d='4'):return [{'tipo_plan_sies':t,'duracion_estudios':d}]
 def test_coincide(self):self.assertTrue(profile_check(self.p(),self.o())[0])
 def test_tipo_cruzado(self):self.assertFalse(profile_check(self.p(),self.o('Plan Regular'))[0])
 def test_duracion_cruzada(self):self.assertFalse(profile_check(self.p(),self.o(d='8'))[0])
 def test_sin_fuente(self):self.assertFalse(profile_check([],self.o())[0]);self.assertFalse(profile_check(self.p(),[])[0])
 def test_tipo_e(self):self.assertFalse(profile_check(self.p('E'),self.o())[0])
 def test_perfil_multiple(self):self.assertFalse(profile_check(self.p()+self.p('1',8),self.o())[0])
 def test_dv_vig_cero(self):self.assertEqual(txt(0),'0');self.assertEqual(txt(None),'')
 def test_unidad_sin_sumar_personas(self):self.assertEqual(aggregate([{'a':1},{'a':1}],['a']),[{'a':1,'n':2}])
if __name__=='__main__':unittest.main()
