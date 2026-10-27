"""Casos sintéticos de último período, reingreso y empates ambiguos."""
import unittest
from capa_v11_ultimo_estado import persona,ultimo
class UltimoObservado(unittest.TestCase):
 def test_reingreso_no_propaga_estado_anterior(self):
  x=ultimo({(2020,1):{'VIGENTE'},(2022,2):{'ELIMINADO'},(2023,1):{'VIGENTE'}})
  self.assertEqual((x['ano'],x['periodo'],x['estado']),(2023,1,'VIGENTE'))
 def test_mismo_periodo_conflictivo_no_escoge_primero(self):
  x=ultimo({(2026,3):{'VIGENTE','ELIMINADO'}});self.assertIsNone(x['estado']);self.assertEqual(x['resultado'],'ESTADO_VACIO_O_CONFLICTIVO')
 def test_ultimo_vacio_no_retrocede(self):
  x=ultimo({(2026,2):{'VIGENTE'},(2026,3):{''}});self.assertIsNone(x['estado']);self.assertEqual(x['periodo'],3)
 def test_estado_y_vacio_es_conflictivo(self):
  self.assertIsNone(ultimo({(2026,3):{'VIGENTE',''}})['estado'])
 def test_sin_actividad(self):self.assertEqual(ultimo({})['resultado'],'SIN_ACTIVIDAD_OBSERVADA')
 def test_identidad_sin_dv_no_se_infiere(self):self.assertEqual(persona('12345678',''),'')
if __name__=='__main__':unittest.main()
