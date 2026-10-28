"""Pruebas sintéticas; no ejecutan el contraste sobre fuentes reales 2026."""
import unittest
from metodo_mu2026 import clasificar,contrastar_fuente,codigos_con_diferencia,diagnosticar_mrun,diagnosticar_inverso_mrun

class PruebasMetodo2026(unittest.TestCase):
    def mu(self,n,vig):
        return {'ANIO_INFORMADO':2026,'TIPO_DOC':'R','N_DOC':str(n),'DV':0,'COD_SED':2,'COD_CAR':1,'JOR':4,'VERSION':2,'VIG':vig}
    def sies(self,n):
        return {'TIPO_DOCUMENTO':'R','NUM_DOCUMENTO':str(n),'DV':0,'CODIGO_UNICO':'I162S2C1J4V2'}
    def test_cero_y_tres_clases(self):
        s=[self.sies(i) for i in range(1,4)];m=[self.mu(1,1),self.mu(2,0)]
        r,_=clasificar(s,m,{'I162S2C1J4V2'})
        self.assertEqual(r['por_codigo'][0],{'codigo_sies':'I162S2C1J4V2','vig1_nuestra':1,'vig0_nuestra':1,'no_esta_en_nuestra_base':1})
    def test_deduplicacion_y_fuera_foco(self):
        s=self.sies(1);out=dict(s,CODIGO_UNICO='I162S2C2J4V1')
        r,_=clasificar([s,s,out],[self.mu(1,0)],{'I162S2C1J4V2'})
        self.assertEqual((r['matriculas_foco'],r['filas_duplicadas_foco'],r['filas_fuera_foco']),(1,1,1))
    def test_conflicto_no_se_fuerza(self):
        with self.assertRaises(ValueError):clasificar([self.sies(1)],[self.mu(1,0),self.mu(1,1)],{'I162S2C1J4V2'})
    def test_fuente_ausente_no_ejecuta(self):
        with self.assertRaises(FileNotFoundError):contrastar_fuente('/ruta/no_existente', 'sin_hash',[],anio_matricula=2026,campos={},encoding='latin1',detalle_privado='/Users/alexi/.local/share/ipss/no_generado.json')
    def test_foco_gobernado(self):self.assertEqual(len(codigos_con_diferencia()),48)

class PruebasAdaptadorMrun(unittest.TestCase):
    code='I162S2C1J4V1'
    def mu(self,n=1,vig=0,version=2,sexo='H'):
        return {'ANIO_INFORMADO':2026,'TIPO_DOC':'R','N_DOC':str(n),'DV':0,'COD_SED':2,'COD_CAR':1,'JOR':4,'VERSION':version,'VIG':vig,'FECH_NAC':'01/02/2000','SEXO':sexo}
    def mr(self,**kwargs):
        return dict({'cat_periodo':'2026','cod_inst':'162','codigo_unico':self.code,'gen_alu':'1','fec_nac_alu':'200002','tipo_plan_carr':'Plan Regular'},**kwargs)
    def groups(self,types=('1',)):
        return [{'familias':['I162S2C1J4'],'perfiles_duracion_tipo':[['8',t] for t in types]}]
    def run_case(self,mr=None,mu=None,groups=None):
        return diagnosticar_mrun([self.mr()] if mr is None else mr,[self.mu()] if mu is None else mu,self.groups() if groups is None else groups,{self.code})
    def test_dv0_vig0_version_libre_y_tipo_normalizado(self):
        r=self.run_case();row=r['por_codigo'][0]
        self.assertEqual(row['vig0_candidata_unica'],1)
        self.assertEqual(row['unicos_con_version_distinta'],1)
        self.assertFalse(r['vinculos_rut_mrun_persistidos'])
    def test_tipo_unanime_incompatible_no_pasa(self):
        r=self.run_case(mr=[self.mr(tipo_plan_carr='Plan Regular de Continuidad')])
        self.assertEqual(r['etapas']['B_mas_familia_ISCJ'][0]['vig0_candidata_unica'],1)
        self.assertEqual(r['por_codigo'][0]['sin_candidato'],1)
    def test_tipo_no_unanime_conserva_b(self):
        r=self.run_case(mr=[self.mr(tipo_plan_carr='Plan Regular de Continuidad')],groups=self.groups(('1','3')))
        self.assertEqual(r['por_codigo'][0]['vig0_candidata_unica'],1)
    def test_sin_fecha_no_se_enlaza(self):
        r=self.run_case(mr=[self.mr(fec_nac_alu='190001')])
        self.assertEqual(r['por_codigo'][0]['sin_candidato'],1)
    def test_sexo_fuera_de_comparacion_no_se_infiere(self):
        r=self.run_case(mu=[self.mu(sexo='NB')])
        self.assertEqual(r['por_codigo'][0]['sin_candidato'],1)
    def test_ambiguos_no_se_resuelven_por_vig(self):
        r=self.run_case(mu=[self.mu(),self.mu(2,1,1)])
        self.assertEqual(r['por_codigo'][0]['varios_mixtos_vig1_vig0'],1)
        self.assertEqual(r['por_codigo'][0]['vig0_candidata_unica'],0)
    def test_sin_perfil_no_filtra_por_tipo(self):
        r=self.run_case(groups=[{'familias':['I162S2C1J4'],'perfiles_duracion_tipo':[]}])
        self.assertEqual(r['por_codigo'][0]['vig0_candidata_unica'],1)


    def test_inversa_perfil_otra_familia_no_certifica(self):
        r=diagnosticar_inverso_mrun([self.mr()],[dict(self.mu(vig=1),COD_CAR=2)],self.groups(),{self.code})
        self.assertEqual(r['resumen']['A_solo_otra_familia'],1)
        self.assertEqual(r['resumen']['A_solo_vig1'],1)
        self.assertFalse(r['vinculos_rut_mrun_persistidos'])
    def test_inversa_preserva_version_libre_y_sensibilidad_fuera_foco(self):
        code2='I162S2C1J4V2'
        r=diagnosticar_inverso_mrun([self.mr()],[self.mu(vig=1)],self.groups(),{code2})
        self.assertEqual(r['resumen']['inversa']['todo_IPSS']['C']['con_candidato'],1)
        self.assertEqual(r['resumen']['inversa']['solo_48_codigos']['C']['sin_candidato'],1)
    def test_inversa_tipo_incompatible_distingue_misma_familia(self):
        r=diagnosticar_inverso_mrun([self.mr(tipo_plan_carr='Plan Especial')],[self.mu()],self.groups(),{self.code})
        self.assertEqual(r['resumen']['A_solo_misma_familia'],1)
        self.assertEqual(r['resumen']['A_solo_vig0'],1)

if __name__=='__main__':unittest.main()
