import unittest
from common.indicador_intertrimestral import ratio,agregar,ponderar,normalizar_documento,documento_comparable
class TestIndicador(unittest.TestCase):
 def test_suma_suma(self):self.assertEqual(float(ponderar([(228,332),(934,1434)])),1162/1766)
 def test_persona_una_vez(self):self.assertEqual(agregar([{'persona':'a','estado':'VIG 1'},{'persona':'a','estado':'VIG 1'}]),{'numerador':1,'denominador':1})
 def test_diplomado(self):self.assertEqual(agregar([{'persona':'a','estado':'VIG 1','diplomado':True}]),{'numerador':0,'denominador':0})
 def test_dv_cero(self):self.assertEqual(normalizar_documento('12345',0),'12345-0')
 def test_documento_comparable(self):self.assertEqual(documento_comparable(" 12.345-0 "),"12345-0")
 def test_documento_no_valida_dv(self):self.assertEqual(documento_comparable("12345-K"),"12345-K")
 def test_conflicto(self):
  with self.assertRaises(ValueError):agregar([{'persona':'a','estado':'VIG 1'},{'persona':'a','estado':'NO APLICA'}])
if __name__=='__main__':unittest.main()
