"""Regresión agregada del plan v2; no ejecuta consumidores productivos."""
import unittest,csv,json,hashlib
from pathlib import Path
O=Path(__file__).parent
class Regresion(unittest.TestCase):
 def setUp(self):
  self.d=list(csv.DictReader(open(O/'DIMENSIONES_63_V2.csv',encoding='utf-8-sig')));self.s=json.load(open(O/'RESUMEN_EJECUCION.json'))
 def test_universo_y_brecha(self):
  self.assertEqual(len(self.d),63);self.assertEqual(len({(r['carrera'],r['sede'],r['jornada']) for r in self.d}),63)
  self.assertEqual(self.s['brecha_propuestas_antes_n'],24);self.assertEqual(self.s['brecha_propuestas_ahora_n'],24)
 def test_recuperacion_separada(self):
  before=[r for r in self.d if r['estado_previo']=='PENDIENTE_SIN_MATCH'];self.assertEqual(len(before),13)
  self.assertEqual(sum(int(r['personas_match_MU_mas_2019_2021'])>0 for r in before),9)
  self.assertEqual(sum(int(r['personas_match_MU_mas_2019_2021'])==0 for r in before),4)
 def test_historico_fuera_catalogo(self):
  r=next(r for r in self.d if r['carrera']=='NETMRE' and r['jornada']=='2')
  self.assertIn('I162S2C3J2V2',r['otros_codigos_mismo_ano']);self.assertEqual(r['personas_match_MU_mas_2019_2021'],'0')
 def test_no_confundir_ausencia_jornada(self):
  for c,j in [('ICRE','1'),('NETMRE','4'),('TPCRE','4')]:
   r=next(r for r in self.d if r['carrera']==c and r['jornada']==j);self.assertEqual(r['observaciones_PROMEDIOS_jornada'],'0');self.assertEqual(r['estado_actual'],'PENDIENTE')
 def test_no_promocion(self):
  self.assertTrue(all(r['asignacion_aprobada']=='False' for r in self.d));self.assertEqual(self.s['nuevas_equivalencias_aprobadas'],0)
 def test_fuentes_intactas(self):
  for r in json.load(open(O/'FUENTES.json')):
   if r.get('sha256'):self.assertEqual(hashlib.sha256(Path(r['ruta']).read_bytes()).hexdigest(),r['sha256'])
 def test_mu_conservada(self):self.assertEqual(self.s['totales_MU'],{'2022':1038,'2023':1145,'2024':1541,'2025':2371,'2026':4105})
 def test_independencia_y_privacidad_esquema(self):
  self.assertTrue(self.s['qa_sql_agregados']);self.assertFalse(set(self.d[0])&{'RUT','CODCLI','N_DOC','NOMBRE','FECH_NAC'})
if __name__=='__main__':unittest.main()
