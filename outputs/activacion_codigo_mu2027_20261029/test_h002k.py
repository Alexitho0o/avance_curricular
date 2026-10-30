"""Pruebas de decisión de código: casos ficticios, sin documentos personales."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.codigo_sies_mu2027 import resolver, leer_fijado, cargar_contexto, asignar_codigo_mu2027

class Regla(unittest.TestCase):
    def setUp(self):
        self.fam='I162S2C999J4';self.code=self.fam+'V1';self.other=self.fam+'V2'
        self.plans={('REG','PLAN_FICTICIO','RE'):'1',('CONT','CONT_FICTICIO','RE'):'3'}
        self.offer=[{'codigo_unico':self.code,'tipo_plan_codigo':'1','vigencia_2027':'1','estado':'CONTINUA',
            'resoluciones_grupo':[{'codcarpr':'REG','sede_umas':'RE','planes_catalogados_candidatos':['PLAN_FICTICIO']}]}]
        self.old={2:{'codcarpr':'REG','plan':'PLAN_FICTICIO','sede_umas':'RE','real':self.code,'vig':0,'dv':0}}
        self.new={'anio':2027,'cohorte':2027,'via_solicitada':'NUEVO','familia':self.fam,'codcarpr':'REG','plan_umas':'PLAN_FICTICIO','sede_umas':'RE'}
        self.previous={'anio':2027,'via_solicitada':'ANTIGUO','fila_mu2026':2,'cambio_carrera_o_plan':False}
    def runrow(self,r):return resolver(r,self.plans,self.offer,self.old,[])
    def test_antiguo_retiene_vig_dv_cero(self):self.assertEqual(self.runrow(self.previous)['codigo'],self.code)
    def test_inconsistente_se_conserva(self):
        self.offer[0]['tipo_plan_codigo']='3';a=self.runrow(self.previous);self.assertEqual(a['codigo'],self.code);self.assertEqual(a['motivo'],'CONSERVA_CODIGO_INCONSISTENTE_D')
    def test_antiguo_sin_oferta_retiene(self):
        self.offer=[];self.assertEqual(self.runrow(self.previous)['codigo'],self.code)
    def test_antiguo_E(self):
        self.plans={};self.assertEqual(self.runrow(self.previous)['motivo'],'ANTIGUO_TIPO_E')
    def test_antiguo_referencia_inexistente(self):
        self.previous['fila_mu2026']=99;self.assertEqual(self.runrow(self.previous)['via'],'REVISION_MANUAL')
    def test_antiguo_cambio_no_forzado(self):
        self.previous['cambio_carrera_o_plan']=True;self.assertIsNone(self.runrow(self.previous)['codigo'])
    def test_antiguo_cambio_desconocido(self):
        self.previous.pop('cambio_carrera_o_plan');self.assertIsNone(self.runrow(self.previous)['codigo'])
    def test_nuevo_unico(self):self.assertEqual(self.runrow(self.new)['codigo'],self.code)
    def test_nuevo_tipo_elige_continuidad(self):
        other=copy.deepcopy(self.offer[0]);other.update(codigo_unico=self.other,tipo_plan_codigo='3');other['resoluciones_grupo']=[{'codcarpr':'CONT','sede_umas':'RE','planes_catalogados_candidatos':['CONT_FICTICIO']}];self.offer.append(other)
        self.new.update(codcarpr='CONT',plan_umas='CONT_FICTICIO');self.assertEqual(self.runrow(self.new)['codigo'],self.other)
    def test_tipo_caller_no_reemplaza_catalogo(self):
        self.new['tipo_plan']='3';self.assertEqual(self.runrow(self.new)['codigo'],self.code)
    def test_FOR_no_desempata(self):
        self.new['FOR_ING_ACT']=11;self.assertEqual(self.runrow(self.new)['codigo'],self.code)
    def test_nuevo_tipo_E(self):
        self.plans={};self.assertEqual(self.runrow(self.new)['motivo'],'NUEVO_TIPO_E')
    def test_nuevo_ambiguedad(self):
        self.offer.append({**self.offer[0],'codigo_unico':self.other});self.assertEqual(self.runrow(self.new)['motivo'],'VARIAS_VERSIONES_VIGENTES_MISMO_TIPO')
    def test_nuevo_sin_vigencia_1(self):
        self.offer[0]['vigencia_2027']='2';self.assertIsNone(self.runrow(self.new)['codigo'])
    def test_nuevo_sin_familia(self):
        self.new['familia']='I162S3C999J4';self.assertEqual(self.runrow(self.new)['motivo'],'FAMILIA_SIN_OFERTA')
    def test_nuevo_no_crea_equivalencias(self):
        self.offer[0]['resoluciones_grupo']=[];self.assertEqual(self.runrow(self.new)['motivo'],'PLAN_FAMILIA_SIN_CORRESPONDENCIA')
    def test_nuevo_37(self):
        self.new['codigo_solicitado']=self.code;self.assertEqual(resolver(self.new,self.plans,self.offer,self.old,[self.code])['motivo'],'CODIGO_NUEVO_SIN_PLAN')
    def test_cohorte_otra(self):
        self.new['cohorte']=2026;self.assertIsNone(self.runrow(self.new)['codigo'])
    def test_otro(self):
        self.new['via_solicitada']='OTRO';self.assertEqual(self.runrow(self.new)['via'],'REVISION_MANUAL')
    def test_anio_distinto(self):
        self.new['anio']=2026;self.assertIsNone(self.runrow(self.new)['codigo'])
    def test_fuera_alcance(self):
        self.offer[0]['estado']='FUERA_ALCANCE';self.assertEqual(self.runrow(self.new)['motivo'],'FUERA_ALCANCE')
    def test_fuente_alterada_rechazada(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'ejemplo.json';p.write_text('{}');
            with self.assertRaisesRegex(ValueError,'Fuente alterada'):leer_fijado({'ruta':str(p),'sha256':'0'*64})
    def test_no_mutacion(self):
        before=copy.deepcopy([self.new,self.plans,self.offer,self.old]);self.runrow(self.new);self.assertEqual(before,[self.new,self.plans,self.offer,self.old])

class Integracion(unittest.TestCase):
    def test_aprobaciones_reales_sin_personas(self):
        for c,p,code in [('ADMP','ADMP20251','I162S2C83J4V1'),('CADMP','CADMP20251','I162S2C83J4V2')]:
            a=asignar_codigo_mu2027({'anio':2027,'cohorte':2027,'via_solicitada':'NUEVO','familia':'I162S2C83J4','codcarpr':c,'plan_umas':p,'sede_umas':'RE'})
            self.assertEqual(a['codigo'],code)
    def test_dos_filas_y_reproduccion(self):
        sys.path.insert(0,str(Path(__file__).parent));import construir
        built,detail,qa=construir.construir();self.assertTrue(all(qa['controles'].values()))
        self.assertEqual(len(qa['filas_modificadas']),2)
        for path,raw in built.items():self.assertEqual((ROOT/path).read_bytes(),raw,path)

if __name__=='__main__':unittest.main()
