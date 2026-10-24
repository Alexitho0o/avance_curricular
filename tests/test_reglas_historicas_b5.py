import unittest
from common.reglas_historicas_b5 import clave,estado,consultar
class TestReglas(unittest.TestCase):
    def setUp(self):
        self.r=dict(codcarpr='X',sede='RE',jornada='D',anio=2019,ingreso_original='2018',primera_observacion=2018,planes=['PLAN_NO_OBSERVADO'])
    def test_clave_anual_no_extrapola(self):
        self.assertNotEqual(clave(self.r,'K0'),clave(dict(self.r,anio=2020),'K0'))
        self.assertEqual(clave(self.r,'K0',True),clave(dict(self.r,anio=2020),'K0',True))
    def test_campos_obligatorios(self):
        self.assertIsNone(clave(self.r,'K1'))
        self.assertIsNotNone(clave(dict(self.r,periodo_ingreso='1'),'K1'))
    def test_conflicto_y_reserva(self):
        self.assertEqual(estado({'a','b'},True,10,0),'CONFLICTO_CONSTRUCCION')
        self.assertEqual(estado({'a'},True,10,1),'CONTRADICCION_EN_RESERVA')
        self.assertEqual(estado({'a'},True,1,0),'CORROBORADA_EN_RESERVA')
    def test_dato_posterior_no_gobierna_historia(self):
        self.assertEqual(estado({'a'},True,10,0,True),'DATO_POSTERIOR_AL_CONTEXTO')
    def test_no_habilita(self):
        registry=[{'modelo':'K0','clave':clave(self.r,'K0'),'codigos_construccion':['a'],'estado':'CORROBORADA_EN_RESERVA','id':'R1'}]
        self.assertFalse(consultar(registry,self.r)['habilitada_para_resolver'])
        self.assertEqual(consultar(registry,dict(self.r,anio=2020))['estado'],'SIN_REGLA_OBSERVADA')
if __name__=='__main__':unittest.main()
