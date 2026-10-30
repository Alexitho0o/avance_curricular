import unittest
from resolver_h010b import escoger
from construir import profile_check,txt
class Decisiones(unittest.TestCase):
 def test_unico(self):self.assertEqual(escoger({'CODIGO_A':{'Vigente sólo con estudiantes antiguos'}})[0],'CODIGO_A')
 def test_d2_exige_nuevos(self):self.assertEqual(escoger({'CODIGO_A':{'Vigente sólo con estudiantes antiguos'}},True)[1],'SIN_VIGENCIA_1_COMPATIBLE')
 def test_d3_desempata_vigencia(self):self.assertEqual(escoger({'CODIGO_A':{'Vigente sólo con estudiantes antiguos'},'CODIGO_B':{'Vigente con estudiantes nuevos'}})[0],'CODIGO_B')
 def test_ambiguo(self):self.assertEqual(escoger({'CODIGO_A':{'Vigente con estudiantes nuevos'},'CODIGO_B':{'Vigente con estudiantes nuevos'}},True)[1],'VARIAS_VIGENCIA_1_COMPATIBLES')
 def test_sin_oferta(self):self.assertEqual(escoger({})[1],'SIN_CODIGO_ANUAL_COMPATIBLE')
 def test_vigencia_inconsistente(self):self.assertEqual(escoger({'CODIGO_A':{'Vigente con estudiantes nuevos','Sin estudiantes nuevos ni antiguos'}},True)[0],'')
 def test_tipo_regular_continuidad(self):self.assertFalse(profile_check([{'tipo_codigo':'1','duracion_diagnostica_semestres':8}],[{'tipo_plan_sies':'Plan Regular de Continuidad','duracion_estudios':8}])[0])
 def test_duracion(self):self.assertFalse(profile_check([{'tipo_codigo':'3','duracion_diagnostica_semestres':4}],[{'tipo_plan_sies':'Plan Regular de Continuidad','duracion_estudios':8}])[0])
 def test_perfil_E(self):self.assertFalse(profile_check([{'tipo_codigo':'E','duracion_diagnostica_semestres':4}],[])[0])
 def test_compatibilidad(self):self.assertTrue(profile_check([{'tipo_codigo':'3','duracion_diagnostica_semestres':4}],[{'tipo_plan_sies':'Plan Regular de Continuidad','duracion_estudios':4}])[0])
 def test_cero(self):self.assertEqual(txt(0),'0')
if __name__=='__main__':unittest.main()
