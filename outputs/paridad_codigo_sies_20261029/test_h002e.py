"""Pruebas de ámbito de decisiones de catálogo; sin identificadores personales."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from aplicar_decisiones_h002e import aplicar


class H002e(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base='2969b638d2a7bf1892783d5eceef4df28316b28e'
        def old(path):return json.loads(subprocess.check_output(['git','show',cls.base+':'+path],cwd=ROOT))
        cls.before=old('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
        cls.groups={g['grupo']:g for g in old('outputs/paridad_codigo_sies_20261029/RESOLUCIONES_POR_GRUPO.json')}
        cls.decision=json.loads((ROOT/'data/paridad_codigo_sies/20261029/DECISIONES_APROBADAS_v2.json').read_text())
        cls.control=json.loads((OUT/'CONTROL_VIGENTES_H002E.json').read_text())
        cls.offers={r['codigo_unico']:{'VIGENCIA_CARRERA':r['vigencia_2027']} for r in cls.before if r['anio']==2027}
        cfg=json.loads((ROOT/'data/paridad_codigo_sies/20261029/FUENTES.json').read_text());refs={x['id']:x for x in cfg['fuentes']}
        def ev(key):return {k:refs[key][k] for k in ['ruta','sha256','clase']}|{'localizador':''}
        cls.ev=ev('decisiones_aprobadas_v2');cls.rev=ev('revision_h002d')

    def build(self,decision=None,control=None):
        rows=deepcopy(self.before);groups=deepcopy(self.groups)
        result=aplicar(rows,groups,deepcopy(decision or self.decision),self.ev,self.rev,deepcopy(control or self.control),self.offers)
        return rows,groups,result

    def test_reaplicacion_desde_base_reproduce_tabla_vigente(self):
        rows,_,_=self.build();current=json.loads((ROOT/'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json').read_text())['filas']
        self.assertEqual(rows,current)

    def test_2026_intacto(self):
        rows,_,_=self.build();self.assertEqual([r for r in rows if r['anio']==2026],[r for r in self.before if r['anio']==2026])

    def test_37_pendientes_intactos(self):
        rows,_,_=self.build();codes=set(self.decision['37_pendientes_sin_cambio'])
        self.assertEqual([r for r in rows if r['anio']==2027 and r['codigo_unico'] in codes],[r for r in self.before if r['anio']==2027 and r['codigo_unico'] in codes])

    def test_seis_grupos_sin_version_asignada(self):
        _,gs,_=self.build();hh=[g for g in gs.values() if g.get('estado_paridad_2027')=='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES']
        self.assertEqual(len(hh),6);self.assertTrue(all(g['ambiguedad_historica']['version_asignada'] is None for g in hh))

    def test_codigo_compartido_no_cerrado(self):
        rows,_,_=self.build();r=next(r for r in rows if r['anio']==2027 and r['codigo_unico']=='I162S2C1J4V3')
        self.assertEqual(r['estado'],'VERSION_MULTIPLE_RESUELTA');self.assertIn('CIINF',r['codcarpr'])

    def test_TAMD_sin_nuevos(self):
        rows,_,_=self.build();r=next(r for r in rows if r['anio']==2027 and r['codigo_unico']=='I162S2C78J2V1')
        self.assertEqual(r['estado'],'APROBADA_D_2027');self.assertEqual(r['version_para_nuevos_2027'],'no')

    def test_rechaza_codigo_fuera_del_grupo(self):
        d=deepcopy(self.decision);d['correspondencias'][0]['codigo_unico']='I162S2C999J4V1'
        with self.assertRaisesRegex(ValueError,'fuera de las opciones'):self.build(decision=d)

    def test_no_retira_grupo_con_vigentes_en_control(self):
        c=deepcopy(self.control);c['grupos'][0]['vigentes_etiqueta_UMAS']=1
        with self.assertRaisesRegex(ValueError,'cero vigentes'):self.build(control=c)

    def test_IECIREOL_no_elige_malla_por_anio(self):
        _,gs,_=self.build();g=next(g for g in gs.values() if g['codcarpr']=='IECIREOL' and g['jornada_umas']=='O')
        self.assertEqual(g['codigo_sies_aprobado'],'I162S2C1J4V2');self.assertEqual(g['planes_explicitos_aprobados'],[])
        self.assertTrue(g['ambito_mallas_cohortes'].startswith('E:'))


if __name__=='__main__':unittest.main(verbosity=2)
