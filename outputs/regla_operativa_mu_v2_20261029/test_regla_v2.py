"""Casos sintéticos de tipos, residual y aislamiento de la predicción."""
import unittest
import construir_v2 as m

def profile(formal=(),groups=(),duration=8,ramos=False):
    return {'conversion_si_regimen_PROMEDIOS':[] if duration is None else [{'semestres_calculados':duration}],
        'perfil_formal_H112B':[{'semestres':str(d),'tipo_plan_codigo':t} for d,t in formal],
        'perfiles_grupo_gobernado':[{'perfiles':list(groups)}],
        'contraste_ramos_5810':[{'diferencia_listado_menos_5810':0}] if ramos else [],'contraste_ramos_Permanencia':[]}

class TipoTest(unittest.TestCase):
    def test_formal_unico(self):self.assertEqual(m.determine(profile(formal=[(8,'1')]),[])[0],'1')
    def test_formal_continuidad(self):self.assertEqual(m.determine(profile(formal=[(4,'3')],duration=4),[])[0],'3')
    def test_regular_corto_no_es_continuidad(self):self.assertEqual(m.determine(profile(formal=[(4,'1')],duration=4),[])[0],'1')
    def test_formal_mixto_duracion(self):self.assertEqual(m.determine(profile(formal=[(8,'1'),(4,'3')]),[])[0],'1')
    def test_formal_mixto_sin_duracion(self):self.assertEqual(m.determine(profile(formal=[(8,'1'),(4,'3')],duration=None),[])[0],'E')
    def test_formal_contradice_duracion(self):self.assertEqual(m.determine(profile(formal=[(4,'3')]),[])[0],'E')
    def test_grupo(self):self.assertEqual(m.determine(profile(groups=[(4,'3')],duration=4),[])[0],'3')
    def test_grupo_multiple(self):self.assertEqual(m.determine(profile(groups=[(8,'1'),(8,'3')]),[])[0],'E')
    def test_grupo_duracion_desambigua(self):self.assertEqual(m.determine(profile(groups=[(8,'1'),(4,'3')]),[])[0],'1')
    def test_duracion_sin_tipo_no_basta(self):self.assertEqual(m.determine(profile(duration=4),[])[0],'E')
    def test_catalogo_sin_ramos_no_basta(self):self.assertEqual(m.determine(profile(),[{'DURACION_ESTUDIOS':'8','TIPO_PLAN_CARRERA':'1'}])[0],'E')
    def test_catalogo_con_ramos(self):self.assertEqual(m.determine(profile(ramos=True),[{'DURACION_ESTUDIOS':'8','TIPO_PLAN_CARRERA':'1'}])[0],'1')
    def test_catalogo_ambiguo(self):self.assertEqual(m.determine(profile(ramos=True),[{'DURACION_ESTUDIOS':'8','TIPO_PLAN_CARRERA':t} for t in ('1','3')])[0],'E')
    def test_catalogo_duracion_diferente(self):self.assertEqual(m.determine(profile(ramos=True),[{'DURACION_ESTUDIOS':'4','TIPO_PLAN_CARRERA':'3'}])[0],'E')
    def test_prefijo_y_nombre_no_deciden(self):
        p=profile();p.update(codcarpr='C_FICTICIO',nombres_catalogo=['CONTINUIDAD FICTICIA'])
        self.assertEqual(m.determine(p,[])[0],'E')
    def test_mayoria_no_decide(self):
        p=profile();p['mayoria_tipo_apoyo']=['3'];self.assertEqual(m.determine(p,[])[0],'E')
    def test_for_no_decide(self):
        p=profile();p['FOR_ING_ACT']='11';self.assertEqual(m.determine(p,[])[0],'E')
    def test_admp_no_activado(self):
        p=profile();p['codcarpr']='CADMP';self.assertEqual(m.determine(p,[])[0],'E')
    def test_sin_cambio_requiere_evidencia(self):
        r={'grupo':'ANTIGUO','real':'COD_B','predicho':'COD_A'}
        self.assertEqual(m.residual(r,False,False,False,[],'1')[0],'OTRA')
        self.assertEqual(m.residual(r,False,True,False,[],'1')[0],'INCONSISTENCIA_DE_CARGA')
    def test_cambio_precede_inconsistencia(self):
        r={'grupo':'ANTIGUO','real':'COD_B','predicho':'COD_A'}
        self.assertEqual(m.residual(r,True,False,True,[],'1')[0],'CAMBIO_DE_PLAN_REAL')
    def test_reparto_marca_inconsistencia(self):
        r={'grupo':'NUEVO','real':'COD_B','predicho':'COD_A'}
        self.assertIn('INCONSISTENCIA_DE_CARGA',m.residual(r,True,False,False,[('COD_B','1','1')],'1')[1])
    def test_oferta_no_vigente(self):
        r={'grupo':'NUEVO','real':'COD_B','predicho':'COD_A'}
        self.assertEqual(m.residual(r,False,False,False,[('COD_B','1','2')],'1')[0],'OFERTA_HISTORICA_NO_REFLEJA_CARGA')
    def test_tipo_e(self):
        r={'grupo':'NUEVO','real':'COD_B','predicho':None}
        self.assertEqual(m.residual(r,False,False,False,[('COD_B','1','1')],'E')[0],'TIPO_PLAN_E')
    def test_antiguo_no_cambia_por_tipo(self):
        self.assertEqual(m.old.predict('ANTIGUO',{'COD_A'},[('COD_B','3','1')],{'3'})[0],'COD_A')
    def test_cero_no_vacio(self):self.assertEqual(m.txt(0),'0')

if __name__=='__main__':unittest.main()
