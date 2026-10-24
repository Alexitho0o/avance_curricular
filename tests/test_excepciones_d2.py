"""Contrastes de cobertura e inferencia para el cierre D2."""
import json,unittest
from pathlib import Path
from scripts.investigar_excepciones_d2 import admision
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/cierre_d2/20261016'
def load(n):return json.loads((BASE/n).read_text())
class TestD2(unittest.TestCase):
    def test_admision_es_anual_no_intervalo(self):
        o={(2025,'X'):{'vigencia':'Vigente con estudiantes nuevos'},(2026,'X'):{'vigencia':'Vigente sin estudiantes nuevos'}}
        self.assertEqual(admision(o,2025,'X'),'ADMITE_NUEVOS')
        self.assertEqual(admision(o,2026,'X'),'SOLO_ANTIGUOS')
        self.assertEqual(admision(o,2024,'X'),'SIN_OFERTA_ANUAL')
        self.assertEqual(admision(o,None,'X'),'SIN_OFERTA_ANUAL')
    def test_contextos_y_cobertura(self):
        q=json.loads((ROOT/'data/cierre_d1/20261016/cola_prioridad_1.json').read_text());r=load('expedientes_16.json')
        self.assertEqual({x['expediente'] for x in q},{x['contexto'] for x in r})
        for x in r:
            self.assertEqual(x['personas_contexto'],x['personas_con_reporte_atribuible']+x['personas_sin_reporte_atribuible'])
            self.assertTrue(x['estado_umas_es_actual_no_historico']);self.assertFalse(x['asignacion_habilitada'])
    def test_cilog_no_mezcla_perfiles_ni_identidad(self):
        c=load('cilog.json')
        self.assertNotEqual(c['perfil_cilog']['tipo_plan'],c['perfil_ilog_online']['tipo_plan'])
        self.assertEqual(sum(x['filas'] for x in c['estratos']),c['filas_hasta_2026'])
        self.assertFalse(c['procedencia_externa_certificada']);self.assertFalse(c['inicio_efectivo_confirmado'])
        self.assertEqual(len(c['contextos_b4']),8)
    def test_limites_fuentes(self):
        r=load('revision_fuentes_candidatas.json')
        self.assertFalse(r['catalogo_planes']['fechas_vigencia_explicitamente_localizadas'])
        self.assertEqual(r['extracto_11248']['corte_temporal'],'NO_ACREDITADO_POR_NOMBRE_DE_ARCHIVO')
        self.assertNotIn('CODIGO_UNICO',r['reporte_4262_2025']['columnas'])
    def test_incidencia_continuidad_2026(self):
        rows=[r for r in load('logistica_mrun_cohortes.json') if r['codigo']=='I162S2C77J4V2' and r['anio']==2026]
        self.assertEqual(sum(r['filas_mrun'] for r in rows if r['admision_ingreso_actual']=='SOLO_ANTIGUOS'),21)
        self.assertEqual(sum(r['filas_mrun'] for r in rows if r['admision_ingreso_actual']=='ADMITE_NUEVOS'),11)
        self.assertTrue(all(r['admision_anio_observado']=='SOLO_ANTIGUOS' for r in rows))
if __name__=='__main__':unittest.main()
