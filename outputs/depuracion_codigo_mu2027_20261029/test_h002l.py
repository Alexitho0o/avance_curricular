"""Pruebas sintéticas de la corrección D; sin identificadores personales."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.codigo_sies_mu2027 import resolver,leer_fijado,cargar_contexto
class Regla(unittest.TestCase):
    def setUp(self):
        self.fam='I162S2C999J4';self.code=self.fam+'V1';self.other=self.fam+'V2'
        self.plans={('REG','PLAN_FICTICIO','RE'):'1'}
        self.offer=[{'codigo_unico':self.code,'tipo_plan_codigo':'1','vigencia_2027':'1','estado':'CONTINUA',
            'resoluciones_grupo':[{'codcarpr':'REG','sede_umas':'RE','planes_catalogados_candidatos':['PLAN_FICTICIO']}]}]
        self.old={2:{'codcarpr':'REG','plan':'PLAN_FICTICIO','sede_umas':'RE','real':self.code,'vig':0,'dv':0}}
        self.anc={'anio':2027,'via_solicitada':'ANTIGUO','fila_mu2026':2}
        self.new={'anio':2027,'cohorte':2027,'via_solicitada':'NUEVO','familia':self.fam,'codcarpr':'REG','plan_umas':'PLAN_FICTICIO','sede_umas':'RE'}
    def runrow(self,r):return resolver(r,self.plans,self.offer,self.old,[])
    def test_antiguo_tipo_E_conserva(self):
        self.plans={};q=self.runrow(self.anc);self.assertEqual(q['codigo'],self.code);self.assertIn('ANTIGUO_TIPO_E_INFORMATIVO',q['marcas_informativas'])
    def test_antiguo_sin_datos_plan_conserva(self):
        self.old={2:{'real':self.code}};self.assertEqual(self.runrow(self.anc)['via'],'ANTIGUO')
    def test_antiguo_plan_no_observado_informativo(self):
        self.old[2]['plan']='PLAN_NO_OBSERVADO';q=self.runrow(self.anc);self.assertEqual(q['codigo'],self.code);self.assertIn('PLAN_NO_OBSERVADO_INFORMATIVO',q['marcas_informativas'])
    def test_antiguo_motivo_1_fila_ausente(self):
        self.anc.pop('fila_mu2026');self.assertEqual(self.runrow(self.anc)['motivo'],'ANTIGUO_1_CODIGO_O_FILA_NO_RESUELTA')
    def test_antiguo_motivo_1_codigo_ausente(self):
        self.old[2].pop('real');self.assertEqual(self.runrow(self.anc)['motivo'],'ANTIGUO_1_CODIGO_O_FILA_NO_RESUELTA')
    def test_antiguo_fila_invalida(self):
        self.anc['fila_mu2026']=[];self.assertIsNone(self.runrow(self.anc)['codigo'])
    def test_antiguo_motivo_2(self):
        self.offer=[];self.assertEqual(self.runrow(self.anc)['motivo'],'ANTIGUO_2_CODIGO_SIN_OFERTA_2027')
    def test_antiguo_motivo_3(self):
        self.offer[0]['vigencia_2027']='3';self.assertEqual(self.runrow(self.anc)['motivo'],'ANTIGUO_3_VIGENCIA_3')
    def test_antiguo_vigencia_2_conserva(self):
        self.offer[0]['vigencia_2027']='2';self.assertEqual(self.runrow(self.anc)['codigo'],self.code)
    def test_antiguo_inconsistente_conserva(self):
        self.offer[0]['tipo_plan_codigo']='3';self.assertEqual(self.runrow(self.anc)['codigo'],self.code)
    def test_antiguo_vig_DV_cero_no_bloquean(self):self.assertEqual(self.runrow(self.anc)['codigo'],self.code)
    def test_vigencia_invalida_falla_configuracion(self):
        self.offer[0]['vigencia_2027']='E'
        with self.assertRaises(ValueError):self.runrow(self.anc)
    def test_nuevo_unico(self):self.assertEqual(self.runrow(self.new)['codigo'],self.code)
    def test_nuevo_familia_sin_admision(self):
        self.offer[0]['vigencia_2027']='2';q=self.runrow(self.new);self.assertEqual(q['via'],'INFORMATIVO');self.assertIsNone(q['codigo'])
    def test_tipo_E_familia_sin_admision(self):
        self.plans={};self.offer[0]['vigencia_2027']='2';q=self.runrow(self.new);self.assertEqual(q['via'],'INFORMATIVO');self.assertTrue(q['tipo_E'])
    def test_tipo_E_familia_admite(self):
        self.plans={};self.assertEqual(self.runrow(self.new)['motivo'],'NUEVO_TIPO_E_CON_ADMISION')
    def test_familia_admite_otro_tipo_revision_real(self):
        self.offer[0]['tipo_plan_codigo']='3';q=self.runrow(self.new);self.assertEqual(q['motivo'],'REVISION_REAL_TIPO_SIN_VERSION_EN_FAMILIA_CON_ADMISION')
    def test_ambiguedad_real(self):
        self.offer.append({**self.offer[0],'codigo_unico':self.other});self.assertEqual(self.runrow(self.new)['motivo'],'VARIAS_VERSIONES_VIGENTES_MISMO_TIPO')
    def test_codigo_nuevo_sin_plan(self):
        self.new['codigo_solicitado']=self.code;self.assertEqual(resolver(self.new,self.plans,self.offer,self.old,[self.code])['motivo'],'CODIGO_NUEVO_SIN_PLAN')
    def test_familia_ausente_no_asume_sin_admision(self):
        self.offer=[];self.assertEqual(self.runrow(self.new)['motivo'],'FAMILIA_SIN_OFERTA')
    def test_OTRO_no_convertido_en_antiguo(self):
        self.anc['via_solicitada']='OTRO';self.assertEqual(self.runrow(self.anc)['via'],'REVISION_MANUAL')
    def test_FORe_ingreso_no_elige_tipo(self):
        self.new['FOR_ING_ACT']=11;self.assertEqual(self.runrow(self.new)['codigo'],self.code)
    def test_nuevo_no_inventa_equivalencia(self):
        self.offer[0]['resoluciones_grupo']=[];self.assertEqual(self.runrow(self.new)['motivo'],'PLAN_FAMILIA_SIN_CORRESPONDENCIA')
    def test_fuente_alterada(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'ejemplo.json';p.write_text('{}')
            with self.assertRaises(ValueError):leer_fijado({'ruta':str(p),'sha256':'0'*64})
    def test_no_mutacion(self):
        before=copy.deepcopy([self.anc,self.new,self.plans,self.offer,self.old]);self.runrow(self.anc);self.runrow(self.new);self.assertEqual(before,[self.anc,self.new,self.plans,self.offer,self.old])
class Integracion(unittest.TestCase):
    def test_reproduccion_y_unidades(self):
        sys.path.insert(0,str(Path(__file__).parent));import construir
        built,manual,info,t=construir.construir()
        self.assertEqual(t['antiguos']['total'],4105);self.assertEqual(t['nuevos']['total'],223)
        self.assertEqual(t['antiguos']['revision_H002l'],0);self.assertEqual(len(info),1046)
        for path,raw in built.items():self.assertEqual((ROOT/path).read_bytes(),raw,path)
    def test_catalogo_H002_inalterado(self):
        import subprocess
        for suffix in ['csv','json']:
            p='data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.'+suffix
            self.assertEqual((ROOT/p).read_bytes(),subprocess.check_output(['git','show','82cb49c:'+p],cwd=ROOT))
if __name__=='__main__':unittest.main()
