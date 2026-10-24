"""Comprueba conciliación, causas y vínculos del inventario académico D1."""
import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/cierre_d1/20261016'
def load(path):return json.loads(path.read_text())
class TestD1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=load(BASE/'inventario.json')
        cls.by_kind={k:{r['id']:r for r in cls.rows if r['universo']==k} for k in ('CONTEXTO','CODIGO_SIES','PLAN_UMAS')}
    def test_cobertura_y_causas(self):
        criteria={r['id'] for r in load(BASE/'criterios.json')}
        self.assertEqual({k:len(v) for k,v in self.by_kind.items()},{'CONTEXTO':1986,'CODIGO_SIES':141,'PLAN_UMAS':236})
        self.assertEqual(len(self.rows),2363)
        for r in self.rows:
            self.assertTrue(r['causas_pendientes'])
            self.assertTrue(set(r['criterios'])<=criteria)
            self.assertFalse(r['asignacion_habilitada'])
        self.assertEqual(set(self.by_kind['CONTEXTO']),{r['contexto'] for r in load(ROOT/'data/matriz_academica_b4/20261016/matriz_contextos.json')})
    def test_referencias_bidireccionales(self):
        for cid,c in self.by_kind['CONTEXTO'].items():
            for code in c['vinculos']['codigos_observados']:
                self.assertIn(cid,self.by_kind['CODIGO_SIES'][code]['vinculos']['contextos_observados'])
            for code in c['vinculos']['codigos_candidatos_h5_ambito_2026']:
                self.assertIn(cid,self.by_kind['CODIGO_SIES'][code]['vinculos']['contextos_candidatura_h5_2026'])
            for plan in c['vinculos']['planes_observados']:
                self.assertIn(cid,self.by_kind['PLAN_UMAS'][plan]['vinculos']['contextos_observados'])
        for p in self.by_kind['PLAN_UMAS'].values():
            self.assertEqual(len(p['vinculos']['contextos_observados']),p['fuente_original']['contextos_observados_b4'])
    def test_prioridad_deduplicada(self):
        queue=load(BASE/'cola_prioridad_1.json')
        self.assertEqual(len(queue),len({r['expediente'] for r in queue}))
        rules=load(ROOT/'data/reglas_historicas_b5/20261016/reglas_observadas.json')
        bad={r['id'] for r in rules if r['modelo']=='K0' and r['estado'] in ('CONFLICTO_CONSTRUCCION','CONTRADICCION_EN_RESERVA')}
        self.assertEqual(bad,{rid for r in queue for rid in r['reglas_k0_problematicas']})
        self.assertEqual({r['expediente'] for r in queue},{r['id'] for r in self.rows if r['universo']=='CONTEXTO' and 'CONFLICTO' in r['causas_pendientes']})
    def test_no_promueve_malla_ni_inicio(self):
        for c in self.by_kind['CONTEXTO'].values():
            if not c['vinculos']['planes_observados']:
                self.assertIn('SIN_PLAN_OBSERVADO',c['causas_pendientes'])
                self.assertEqual(c['vinculos']['nivel_observacion'],'PROGRAMA_SIN_PLAN')
            self.assertIn('PRIMERA_OBSERVACION_NO_ES_INGRESO',c['causas_pendientes'])
        for c in self.by_kind['CODIGO_SIES'].values():
            if c['fuente_original']['inicio']['coincide_limite_inferior_fuente']:
                self.assertIn('OFERTA_EN_LIMITE_2010',c['causas_pendientes'])
    def test_integridad(self):
        m=load(BASE/'manifest.json')
        for name,digest in m['fuentes_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        for name,digest in m['salidas_sha256'].items():self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),digest,name)
if __name__=='__main__':unittest.main()
