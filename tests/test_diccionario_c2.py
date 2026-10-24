"""Paridad real de comandos y controles de consumo C2."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from common.diccionario_c2 import DiccionarioC2, DESCRIPTOR
ROOT=Path(__file__).resolve().parents[1]

class TestC2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=DiccionarioC2()
        cls.queries=[{'modelo':r['modelo'],'entrada':{k:v for k,v in r['entrada'].items()
                     if k in cls.client.motor.BASE+cls.client.motor.EXTRAS[r['modelo']]}}
                     for r in cls.client.registro]

    def test_paridad_completa_comandos_y_c1(self):
        expected=self.client.consultar_lote(self.queries)
        c1=json.loads((ROOT/'data/diccionario_c1/20261016/libro_c1.json').read_text())
        self.assertEqual(c1['rules'],self.client.registro)
        for query,result in zip(self.queries,expected):
            self.assertEqual(result['resultado'],self.client.motor.consultar(self.client.registro,query['entrada'],query['modelo']))
            self.assertFalse(result['resultado']['habilitada_para_resolver'])
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'queries.json';f.write_text(json.dumps(self.queries))
            outputs=[]
            for cmd in ('scripts/consultar_diccionario_c2.py','procesos/caracterizacion/scripts/consultar_diccionario_c2.py'):
                p=subprocess.run([sys.executable,'-I',str(ROOT/cmd),'--lote',str(f)],cwd=folder,capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                self.assertEqual(json.loads(p.stdout),expected);outputs.append(p.stdout)
            self.assertEqual(*outputs)

    def test_fronteras_y_aislamiento(self):
        q=copy.deepcopy(self.queries[0]);r=self.client.consultar_lote([q,q])
        r[0]['resultado']['candidatos'].clear();r[0]['evidencia']['estado']='CAMBIADO'
        self.assertTrue(r[1]['resultado']['candidatos'])
        self.assertNotEqual(self.client.consultar_lote([q])[0]['evidencia']['estado'],'CAMBIADO')
        self.assertEqual(self.client.consultar({},'K0')['resultado']['estado'],'ENTRADA_INCOMPLETA')
        q['entrada']['anio']=2027
        self.assertEqual(self.client.consultar_lote([q])[0]['resultado']['estado'],'SIN_REGLA_OBSERVADA')
        for bad in ({'rut':'123'}, {'anio':True},{'planes':['Z','A']},{'planes':['A','A']},{'anio':'2020'}):
            with self.assertRaises(ValueError):self.client.consultar(bad,'K0')
        with self.assertRaises(ValueError):self.client.consultar({},'K4')
        with self.assertRaises(ValueError):self.client.consultar_lote([{'entrada':{}}])

    def test_portabilidad_integridad_y_rutas(self):
        descriptor=json.loads((ROOT/DESCRIPTOR).read_text())
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            paths=[DESCRIPTOR,*descriptor['componentes_sha256'],'common/diccionario_c2.py',
                   'scripts/consultar_diccionario_c2.py','procesos/caracterizacion/scripts/consultar_diccionario_c2.py']
            for name in paths:
                dest=base/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
            q=base/'q.json';q.write_text(json.dumps(self.queries[:2]))
            proc=subprocess.run([sys.executable,'-I',str(base/'procesos/caracterizacion/scripts/consultar_diccionario_c2.py'),'--lote',str(q)],cwd=folder,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(json.loads(proc.stdout),self.client.consultar_lote(self.queries[:2]))
            for name in [DESCRIPTOR,*descriptor['componentes_sha256']]:
                path=base/name;original=path.read_bytes();path.write_bytes(original+b' ')
                with self.assertRaises(ValueError):DiccionarioC2(base)
                path.write_bytes(original);path.unlink()
                with self.assertRaises(OSError):DiccionarioC2(base)
                path.write_bytes(original)
            name=descriptor['registro'];p=base/name;p.unlink();p.symlink_to(ROOT/name)
            with self.assertRaises(ValueError):DiccionarioC2(base)

    def test_preservacion_reversion(self):
        # La reversión es aditiva: los archivos previos deben conservar sus bytes.
        refs=json.loads((ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json').read_text())['referencias_sha256']
        for name,digest in refs.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        c1=json.loads((ROOT/'data/diccionario_c1/20261016/entrega.json').read_text())
        for name,digest in c1['archivos_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

if __name__=='__main__':unittest.main()
