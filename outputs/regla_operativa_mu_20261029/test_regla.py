"""Pruebas ficticias: clasificación, predicción ciega y denominadores."""
import unittest
import construir as m

class ReglaTest(unittest.TestCase):
    def test_antiguo_precede_nuevo(self):
        self.assertEqual(m.classify({'COD_A'},2025,2025),'ANTIGUO')
    def test_nuevo(self):
        self.assertEqual(m.classify(set(),2025,2025),'NUEVO')
    def test_reingreso_otro(self):
        self.assertEqual(m.classify(set(),2023,2025),'OTRO')
    def test_otro_sin_ingreso(self):
        self.assertEqual(m.classify(set(),None,2025),'OTRO')
    def test_antiguo_unico(self):
        self.assertEqual(m.predict('ANTIGUO',{'COD_A'},[],set()),('COD_A','CODIGO_PREVIO_UNICO'))
    def test_antiguo_ambiguo(self):
        self.assertIsNone(m.predict('ANTIGUO',{'COD_A','COD_B'},[],set())[0])
    def test_otro_no_predice(self):
        self.assertEqual(m.predict('OTRO',set(),[('COD_A','1','1')],{'1'}),(None,'FUERA_REGLA'))
    def test_sin_oferta(self):
        self.assertEqual(m.predict('NUEVO',set(),[],{'1'})[1],'OFERTA_FALTANTE')
    def test_sin_vigencia(self):
        self.assertEqual(m.predict('NUEVO',set(),[('COD_A','1','2')],{'1'})[1],'SIN_VERSION_VIGENCIA_1')
    def test_oferta_unica_no_exige_actividad(self):
        self.assertEqual(m.predict('NUEVO',set(),[('COD_A','1','1')],set())[0],'COD_A')
    def test_tipo_desambigua(self):
        self.assertEqual(m.predict('NUEVO',set(),[('COD_A','1','1'),('COD_B','3','1')],{'3'})[0],'COD_B')
    def test_sin_tipo_no_inventa(self):
        self.assertEqual(m.predict('NUEVO',set(),[('COD_A','1','1'),('COD_B','3','1')],set())[1],'TIPO_PLAN_NO_DETERMINABLE')
    def test_empate_tipo(self):
        self.assertEqual(m.predict('NUEVO',set(),[('COD_A','1','1'),('COD_B','1','1')],{'1'})[1],'AMBIGUO_OFERTA')
    def test_tipo_incompatible(self):
        self.assertEqual(m.predict('NUEVO',set(),[('COD_A','1','1'),('COD_B','1','1')],{'3'})[1],'TIPO_PLAN_SIN_OFERTA_COMPATIBLE')
    def test_causa_antiguo(self):
        self.assertEqual(m.cause('ANTIGUO','COD_A','COD_B','',[]),'CAMBIO_DE_CODIGO_DEL_ALUMNO')
    def test_causa_vigencia(self):
        self.assertEqual(m.cause('NUEVO','COD_A','COD_B','',[('COD_A','1','1'),('COD_B','1','2')]),'VERSION_NUEVA_NO_DECLARADA')
    def test_suma_suma_y_no_predichos(self):
        rows=[{'anio':2025,'predicho':'COD_A','acierto':True}]+[{'anio':2025,'predicho':None,'acierto':False}]*3
        r=m.metrics(rows,['anio'])[0]
        self.assertEqual((r['filas_mu'],r['acierto_pct'],r['acierto_entre_predicciones_pct']),(4,25,100))
    def test_cero_no_vacio(self):
        self.assertEqual(m.txt(0),'0')
        self.assertEqual(m.ident('P','DOCUMENTO_FICTICIO',0),('P','DOCUMENTO_FICTICIO','0'))
    def test_familia_conserva_sede_jornada(self):
        self.assertEqual(m.family('I162S3C91J2V1'),'I162S3C91J2')
    def test_pct_sin_denominador(self):
        self.assertIsNone(m.pct(0,0))

if __name__=='__main__':unittest.main()
