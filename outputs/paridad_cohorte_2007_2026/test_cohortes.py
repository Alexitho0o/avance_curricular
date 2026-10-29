import unittest
from construir_cohortes import cohort,transition,solve,choose_da,resolve_da,origin_observed,ident
class Cohortes(unittest.TestCase):
    def test_ausente_no_origen(self):self.assertEqual(cohort('',1,2020),(None,'SIN_DATO'))
    def test_futura_no_admitida(self):self.assertEqual(cohort(2026,1,2025),(None,'SIN_DATO'))
    def test_cero_no_cohorte(self):self.assertEqual(cohort(0,1,2020),(None,'SIN_DATO'))
    def test_semestre_4_no_convertido(self):self.assertEqual(cohort(2020,4,2020),(None,'SIN_DATO'))
    def test_sin_salto_version(self):self.assertEqual(transition({'V1'},{'V1'}),'MANTIENE')
    def test_cambio(self):self.assertEqual(transition({'V1'},{'V2'}),'CAMBIA')
    def test_multiples_no_simular_cambio(self):self.assertEqual(transition({'V1','V2'},{'V2'}),'MULTIPLE_E')
    def test_exacto(self):self.assertEqual(solve({'A':3},{'V1':3},{'A':['V1']})[0],'CUADRA_EXACTO')
    def test_no_dividir_plan(self):self.assertEqual(solve({'A':6},{'V1':3,'V2':3},{'A':['V1','V2']})[0],'NO_CUADRA')
    def test_ambiguedad(self):self.assertEqual(solve({'A':3,'B':3},{'V1':3,'V2':3},{'A':['V1','V2'],'B':['V1','V2']})[0],'AMBIGUA')
    def test_limite_diez(self):self.assertEqual(solve({'A':9},{'V1':10},{'A':['V1']})[0],'APROXIMA')
    def test_fuera_diez(self):self.assertEqual(solve({'A':8},{'V1':10},{'A':['V1']})[0],'NO_CUADRA')
    def test_todos_codigos_controlados(self):self.assertEqual(solve({'A':3},{'V1':3,'V2':1},{'A':['V1']})[0],'NO_CUADRA')
    def test_sin_candidatos(self):self.assertEqual(solve({'A':3},{'V1':3},{'A':[]})[0],'NO_CUADRA')
    def test_unico_sin_actividad(self):
        ctx=('EXP_A','PROGRAMA','RE','O',2024,'1');self.assertEqual(choose_da({ctx},2024,'1',2025),ctx)
    def test_desempate_ingreso(self):
        a=('EXP_A','PROGRAMA','RE','O',2023,'1');b=('EXP_B','PROGRAMA','RE','O',2024,'1');self.assertEqual(choose_da({a,b},2024,'1',2025),b)
    def test_no_convertir_historico(self):
        a=('EXP_A','PROGRAMA','RE','O',2024,'1');b=('EXP_B','PROGRAMA','RE','O',2024,'3');self.assertIsNone(choose_da({a,b},2024,'2',2025));self.assertEqual(choose_da({a,b},2024,'2',2026),b)
    def test_no_primer_expediente(self):
        a=('EXP_A','PROGRAMA','RE','O',2024,'1');b=('EXP_B','PROGRAMA','RE','O',2024,'1');self.assertIsNone(choose_da({a,b},2024,'1',2025))
    def test_actividad_no_requisito(self):
        a=('EXP_A','PROGRAMA','RE','O',2024,'1');self.assertEqual(resolve_da({a},2024,'1',2025,set())[0],a)
    def test_actividad_desempata_no_mayoria(self):
        a=('EXP_A','PROGRAMA','RE','O',2024,'1');b=('EXP_B','PROGRAMA','RE','O',2024,'1');self.assertEqual(resolve_da({a,b},2024,'1',2025,{('EXP_B','PROGRAMA')})[0],b)
    def test_actividad_multiple_sigue_E(self):
        a=('EXP_A','PROGRAMA','RE','O',2024,'1');b=('EXP_B','PROGRAMA','RE','O',2024,'1');self.assertIsNone(resolve_da({a,b},2024,'1',2025,{('EXP_A','PROGRAMA'),('EXP_B','PROGRAMA')})[0])
    def test_origen_semestre_cero_visible(self):self.assertEqual(origin_observed(2007,0),(2007,'0'))
    def test_origen_especial_no_rellena_actual(self):self.assertEqual(origin_observed(1900,0),(1900,'0'));self.assertEqual(cohort(1900,0,2020),(None,'SIN_DATO'))
    def test_dv_cero_preservado(self):self.assertEqual(ident('R',str(6*10**6),0),ident('R',str(6*10**6),'0'))
if __name__=='__main__':unittest.main()
