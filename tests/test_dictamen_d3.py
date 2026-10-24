"""Validación de contratos, paridad y límites históricos D3."""
import copy,hashlib,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from common.consulta_dictamen_d3 import ConsultaD3,DESCRIPTOR
from common.reglas_dictamen_d3 import evaluar_contexto,vigencia_anual,control_variante
ROOT=Path(__file__).resolve().parents[1]
class TestD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.client=ConsultaD3()
    def test_paridad_completa_y_regresion_b5(self):
        queries=[]
        for r in self.client.c2.registro:
            q={'modelo':r['modelo'],'entrada':r['entrada']};queries.append(q)
            self.assertEqual(self.client.consultar(**q)['c2'],self.client.c2.consultar(**q))
        queries += [{'tipo':'CONTEXTO','id':i} for i in self.client.contexts]
        queries += [{'tipo':'CODIGO_SIES','id':i} for i in self.client.codes]
        queries += [{'tipo':'PLAN_UMAS','id':i} for i in self.client.plans]
        expected=self.client.consultar_lote(queries)
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'lote.json';file.write_text(json.dumps(queries));outputs=[]
            for cmd in ('scripts/consultar_dictamen_d3.py','procesos/caracterizacion/scripts/consultar_dictamen_d3.py'):
                p=subprocess.run([sys.executable,'-I',str(ROOT/cmd),'--lote',str(file)],cwd=folder,capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout),expected);outputs.append(hashlib.sha256(p.stdout.encode()).hexdigest())
            self.assertEqual(*outputs)
        self.assertEqual(len(queries),4712)
    def test_conflicto_no_se_sanea_con_modelo(self):
        r=next(r for r in self.client.c2.registro if r['modelo']=='K0' and r['estado']=='CONTRADICCION_EN_RESERVA')
        result=self.client.consultar(r['entrada'],'K0');self.assertEqual(result['dictamen_d3']['estado'],'ABSTENCION_CONFLICTO')
        self.assertIsNone(result['codigo_asignado']);self.assertFalse(result['habilitada_para_resolver'])
        for state in ('CONFLICTO_CONSTRUCCION','CONTRADICCION_EN_RESERVA'):self.assertEqual(control_variante(state),'ABSTENCION_CONFLICTO_VARIANTE')
        self.assertEqual(control_variante('DATO_POSTERIOR_AL_CONTEXTO'),'ABSTENCION_DATO_POSTERIOR')
    def test_clave_sin_extrapolacion_y_entradas(self):
        r=copy.deepcopy(self.client.c2.registro[0]['entrada']);r['anio']=2027
        self.assertIsNone(self.client.consultar(r,'K0')['dictamen_d3'])
        self.assertEqual(self.client.consultar({},'K0')['c2']['resultado']['estado'],'ENTRADA_INCOMPLETA')
        with self.assertRaises(ValueError):self.client.consultar({'rut':'123'},'K0')
        with self.assertRaises(ValueError):self.client.consultar_lote([{'tipo':'CONTEXTO','id':'X','rut':'123'}])
        self.assertEqual(self.client.consultar_elemento('CONTEXTO','INEXISTENTE')['estado'],'SIN_ELEMENTO_EN_EDICION')
    def test_perfiles_cilog_sin_fallback_regular(self):
        c=self.client.contexts['B4-00138'];comparison=c['comparacion_oferta_perfil']
        v1=next(x for x in comparison if x['codigo']=='I162S2C77J4V1')
        self.assertFalse(v1['compatible_perfil_referencia']);self.assertIsNone(c['codigo_asignado'])
        # En 2026 solo antiguos no se convierte por sí mismo en conflicto para todos.
        c=self.client.contexts['B4-00145'];v2=next(x for x in c['comparacion_oferta_perfil'] if x['codigo']=='I162S2C77J4V2')
        self.assertTrue(v2['compatible_perfil_referencia']);self.assertEqual(v2['vigencia'],'SOLO_ANTIGUOS')
        self.assertEqual(c['estado'],'SIN_EVIDENCIA_ATRIBUIBLE')
        self.assertEqual(vigencia_anual(None),'SIN_OFERTA_ANUAL')
    def test_nombres_y_sectores_c1(self):
        import openpyxl
        w=openpyxl.load_workbook(ROOT/'data/diccionario_c1/20261016/fuente_usuario.xlsx',read_only=True,data_only=False)
        for row in w['Diccionario SIES'].iter_rows(min_row=6,max_row=146,values_only=True):
            d=self.client.codes[row[0]]['atributos_c1_referencia_2026']
            for key,index in [('nombre_oficial_2026',1),('jornada_2026',9),('modalidad_2026',10),('sector_ipss_2026',18),('estado_sector',19),('evidencia_sector',20)]:self.assertEqual(d[key],row[index])
        w.close()
    def test_mutabilidad_y_multiejecucion(self):
        q={'tipo':'CONTEXTO','id':'B4-00362'};a=self.client.consultar_lote([q,q]);a[0]['resultado']['codigos_observados'].clear()
        self.assertTrue(a[1]['resultado']['codigos_observados']);self.assertTrue(self.client.consultar_lote([q])[0]['resultado']['codigos_observados'])
    def test_portable_integridad_y_aislamiento(self):
        d=json.loads((ROOT/DESCRIPTOR).read_text());c2d='data/consumo_comun_c2/20261016/descriptor.json';old=json.loads((ROOT/c2d).read_text())
        files=[DESCRIPTOR,*d['archivos_sha256'],c2d,*old['componentes_sha256'],'common/diccionario_c2.py','common/consulta_dictamen_d3.py','common/reglas_dictamen_d3.py','scripts/consultar_dictamen_d3.py','procesos/caracterizacion/scripts/consultar_dictamen_d3.py']
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for n in set(files):p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
            q=root/'lote.json';q.write_text('[{"tipo":"CONTEXTO","id":"B4-00145"}]')
            p=subprocess.run([sys.executable,'-I',str(root/'procesos/caracterizacion/scripts/consultar_dictamen_d3.py'),'--lote',str(q)],cwd=folder,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout),self.client.consultar_lote(json.loads(q.read_text())))
            for n in [DESCRIPTOR,*d['archivos_sha256'],'common/reglas_dictamen_d3.py']:
                p=root/n;original=p.read_bytes();p.write_bytes(original+b' ')
                with self.assertRaises(ValueError):ConsultaD3(root)
                p.write_bytes(original);p.unlink()
                with self.assertRaises(OSError):ConsultaD3(root)
                p.write_bytes(original)
            n='data/validacion_d3/20261016/dictamenes.json';p=root/n;p.unlink();p.symlink_to(ROOT/n)
            with self.assertRaises(ValueError):ConsultaD3(root)
if __name__=='__main__':unittest.main()
