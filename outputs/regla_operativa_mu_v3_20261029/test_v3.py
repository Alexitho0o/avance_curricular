"""Pruebas de evidencia independiente, cobertura y denominadores H002m."""
import copy,json,unittest
from pathlib import Path
import construir_v3 as m
class Evidencia(unittest.TestCase):
 def test_dos_fuentes_regular(self):self.assertEqual(m.classify_type(8,{(8,'1'),(4,'3')},set(),{'1'},2)[:3],('REGULAR','1','C'))
 def test_dos_fuentes_continuidad(self):self.assertEqual(m.classify_type(4,{(8,'1'),(4,'3')},set(),set(),2)[0],'CONTINUIDAD')
 def test_regular_corto(self):self.assertEqual(m.classify_type(4,{(4,'1')},set(),{'1'},2)[0],'REGULAR')
 def test_una_fuente_no_desempata(self):self.assertEqual(m.classify_type(8,{(8,'1')},set(),set(),1)[:2],('DEBIL','E'))
 def test_solo_apoyo(self):self.assertEqual(m.classify_type(None,set(),set(),{'3'},0)[:2],('DEBIL','E'))
 def test_sin_evidencia(self):self.assertEqual(m.classify_type(None,set(),set(),set(),0)[0],'E')
 def test_minoritaria_contradiccion_no_mayoria(self):self.assertEqual(m.classify_type(8,{(8,'1')},set(),{'1','3'},2)[0],'CONFLICTO')
 def test_duracion_contradictoria(self):self.assertEqual(m.classify_type(5,{(8,'1')},set(),set(),1)[0],'CONFLICTO')
 def test_dos_tipos_misma_duracion(self):self.assertEqual(m.classify_type(4,{(4,'1'),(4,'3')},set(),set(),2)[0],'CONFLICTO')
 def test_cohorte_texto_y_numero_iguales(self):self.assertEqual(m.cohort_key([2025,'1']),m.cohort_key(['2025',1]))
 def test_cohorte_ausente_no_cero(self):self.assertEqual(m.cohort_key([None,None]),(None,None))
 def test_cero_documento_DV_no_vacio(self):self.assertEqual(m.txt(0),'0')
 def test_vig_persona_cero_no_vigencia_carrera(self):self.assertEqual(m.vig(0),'E')
 def test_vigencia_texto(self):self.assertEqual(m.vig('VIGENTE SIN ALUMNOS NUEVOS'),'2')
 def test_tipo_continuidad(self):self.assertEqual(m.ctype('Plan Regular de Continuidad'),'3')
 def test_antiguo_no_depende_tipo(self):self.assertEqual(m.predict_registered('ANTIGUO',{'COD_A'},[('COD_B','3','1')],{'3'})[0],'COD_A')
 def test_ausencia_micro_no_cierre(self):self.assertIsNone(m.predict_registered('NUEVO',set(),[('COD_A','1','1')],{'1'},True,True)[0])
 def test_estricto_no_bloquea_antiguo(self):self.assertEqual(m.predict_registered('ANTIGUO',{'COD_A'},[],set(),True,True)[0],'COD_A')
 def test_ambiguo_se_conserva(self):self.assertIsNone(m.predict_registered('NUEVO',set(),[('COD_A','1','1'),('COD_B','1','1')],{'1'})[0])
 def test_OTRO_sin_prediccion(self):self.assertIsNone(m.predict_registered('OTRO',set(),[('COD_A','1','1')],{'1'})[0])
 def test_una_forma_no_explicacion(self):self.assertFalse(m.is_deterministic([{'form':'1','code':'A'},{'form':'1','code':'B'}],'form'))
 def test_formas_separan(self):self.assertTrue(m.is_deterministic([{'form':'1','code':'A'},{'form':'11','code':'B'}],'form'))
 def test_forma_faltante(self):self.assertFalse(m.is_deterministic([{'form':None,'code':'A'},{'form':'11','code':'B'}],'form'))
 def test_particiones_inversas_no_explican(self):
  a=[{'form':'1','code':'A'},{'form':'11','code':'B'}];b=[{'form':'1','code':'B'},{'form':'11','code':'A'}]
  self.assertFalse(m.same_partition(a,b,'form'));self.assertTrue(m.same_partition(a,copy.deepcopy(a),'form'))
class Integracion(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.results=m.read(m.OUT/'RESULTADOS.json');cls.cat=m.read(m.DATA/'TIPO_PLAN_POR_PLAN_UMAS_v3.json')
 def test_denominadores_originales(self):
  self.assertEqual([r['filas_mu'] for r in self.results['totales']],[1042,1433,2313,3880])
 def test_102_y_121(self):
  self.assertEqual(sum(r['tipo_anterior']=='E' for r in self.cat),102)
  for r in self.cat:
   if r['tipo_anterior']!='E':self.assertEqual(r['tipo_anterior'],r['clasificacion'])
 def test_diagnosticos_disjuntos_cuentan(self):
  for count in (253,212):
   d=m.read(m.OUT/f'DIAGNOSTICO_{count}.json');self.assertEqual(sum(r['matriculas'] for r in d['casos_agregados']),count)
 def test_no_errors_certificados(self):self.assertEqual(self.results['errores_individuales_oficiales_certificados'],0)
 def test_no_identidad_en_diagnosticos(self):
  for n in (253,212):
   rows=m.read(m.OUT/f'DIAGNOSTICO_{n}.json')['casos_agregados']
   for r in rows:self.assertFalse(set(r)&{'identidad','expediente','mrun','rut','dv','fila_mu'})
 def test_ninguna_promocion_debil_conflicto(self):
  for r in self.cat:
   if r['clasificacion'] in {'DEBIL','CONFLICTO','E'}:self.assertEqual(r['tipo_codigo'],'E')
 def test_h002_sigue_igual_por_fuente(self):
  ref=next(r for r in m.read(m.OUT/'FUENTES.json') if r['id']=='data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json');self.assertEqual(m.sha(ref['ruta']),ref['sha256'])
 def test_vigencia_registro_no_cambia_valores_comparables(self):
  rows=m.read(m.DATA/'CONTRASTE_VIGENCIAS.json');self.assertFalse(any(x['clasificacion']=='DIFIERE_VIGENCIA_REGISTRADA' for x in rows))
 def test_suma_por_anyo(self):
  groups=self.results['por_grupo'];expected={2023:1145,2024:1541,2025:2371,2026:4105}
  for y,n in expected.items():self.assertEqual(sum(x['filas_mu'] for x in groups if x['anio']==y),n)
if __name__=='__main__':unittest.main()
