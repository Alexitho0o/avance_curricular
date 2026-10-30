import unittest
from qa_graficos_filtros import validar_aux

class Graficos(unittest.TestCase):
 def test_cero_observado_no_relleno(self):
  q=validar_aux([[None,None,2,None,None],['A',0,1,'A',0],['B',.5,2,'B',.5]])
  self.assertTrue(q['orden']);self.assertEqual(q['ceros_observados'],1)
 def test_modalidad_ausente_y_categoria_sin_datos(self):
  q=validar_aux([[None,None,1,None,None,None],['A',.5,1,'A',.5,'#N/A'],['B','','','','#N/A','#N/A']])
  self.assertTrue(q['cantidad_correcta']);self.assertTrue(q['sin_etiquetas_vacias']);self.assertEqual(q['series_ausentes'],1)
 def test_detecta_desorden(self):
  q=validar_aux([[None,None,2,None,None],['B',.5,2,'B',.5],['A',.2,1,'A',.2]])
  self.assertFalse(q['orden'])
 def test_desempate_alfabetico(self):
  q=validar_aux([[None,None,2,None,None],['B',.5,2,'A',.5],['A',.5,1,'B',.5]])
  self.assertTrue(q['orden'])
if __name__=='__main__':unittest.main()
