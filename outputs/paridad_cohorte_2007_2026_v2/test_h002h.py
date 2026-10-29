import unittest
from construir_h002h import derive_cohort, partition, split_classification, fixed_allowed, solve


def row(year=2010, ay='', ase='', oy='', ose=''):
    return dict(cat_periodo=str(year),anio_ing_carr_act=ay,sem_ing_carr_act=ase,anio_ing_carr_ori=oy,sem_ing_carr_ori=ose)


def sample(code, form, title='NO_ACREDITADO_E', n=1):
    return dict(codigo_sies=code,forma_ingreso=form,tecnico_previo_titulado=title,matriculas=n)


class Cohorts(unittest.TestCase):
    def test_actual_priority(self): self.assertEqual(derive_cohort(row(2010,'2009','1','2008','2'),2008),(2009,'1','a'))
    def test_origin_fallback(self): self.assertEqual(derive_cohort(row(2010,'1900','0','2008','2'),2007),(2008,'2','b'))
    def test_first_observation(self): self.assertEqual(derive_cohort(row(),2008),(2008,'NO_OBSERVADO','c'))
    def test_left_censor(self): self.assertEqual(derive_cohort(row(),2007),(None,'NO_OBSERVADO','censurada'))
    def test_future_invalid(self): self.assertEqual(derive_cohort(row(2010,'2011','1'),2009)[2],'c')
    def test_semester_zero_invalid(self): self.assertEqual(derive_cohort(row(2010,'2009',0),2009)[2],'c')
    def test_missing_identity(self): self.assertEqual(derive_cohort(row(),None)[2],'sin_identificador')
    def test_2007_valid_not_censored(self): self.assertEqual(derive_cohort(row(2007,'2006','1'),2007),(2006,'1','a'))
    def test_no_origin_semester_invention(self): self.assertEqual(derive_cohort(row(2010,'','','2008',''),2008)[1],'NO_OBSERVADO')
    def test_future_origin_rejected(self): self.assertEqual(derive_cohort(row(2010,'','','2012','2'),2007)[2],'censurada')


class Explanations(unittest.TestCase):
    def test_forms_separate(self): self.assertEqual(split_classification([sample('V1','1'),sample('V2','11')])[0],'EXPLICADO_POR_FORMA_INGRESO')
    def test_same_form_multiple(self): self.assertEqual(split_classification([sample('V1','1'),sample('V2','1')])[0],'NO_EXPLICADO')
    def test_unknown_not_dropped(self): self.assertFalse(partition([sample('V1','1'),sample('V2','11'),sample('V2','SIN_DATO')],'forma_ingreso')['explicado'])
    def test_partial(self): self.assertEqual(split_classification([sample('V1','1'),sample('V2','1'),sample('V2','11')])[0],'PARCIAL')
    def test_11_not_title(self): self.assertFalse(partition([sample('V1','1'),sample('V2','11')],'tecnico_previo_titulado')['explicado'])
    def test_title_unknown_not_no(self): self.assertFalse(partition([sample('V1','1','SI'),sample('V2','1')],'tecnico_previo_titulado')['explicado'])
    def test_title_counterfactual_complete(self): self.assertEqual(split_classification([sample('V1','1','SI'),sample('V2','1','NO_DOCUMENTADO')])[0],'EXPLICADO_POR_ARTICULACION')
    def test_unknown_weight(self): self.assertEqual(partition([sample('V1','SIN_DATO',n=4)],'forma_ingreso')['sin_dato'],4)
    def test_single_version_not_explanation(self): self.assertFalse(partition([sample('V1','1'),sample('V1','11')],'forma_ingreso')['explicado'])


class Fixation(unittest.TestCase):
    def test_exact_profile(self): self.assertTrue(fixed_allowed('CUADRA_EXACTO',{'CA|PLAN':1},{'CA|PLAN':'PERFIL_FORMAL_COMPATIBLE'},0))
    def test_censorship_blocks(self): self.assertFalse(fixed_allowed('CUADRA_EXACTO',{'CA|PLAN':1},{'CA|PLAN':'PERFIL_FORMAL_COMPATIBLE'},1))
    def test_missing_profile_blocks(self): self.assertFalse(fixed_allowed('CUADRA_EXACTO',{'CA|PLAN':1},{'CA|PLAN':'PERFIL_NO_ACREDITADO'},0))
    def test_missing_plan_blocks(self): self.assertFalse(fixed_allowed('CUADRA_EXACTO',{'CA|PLAN_NO_OBSERVADO':1},{'CA|PLAN_NO_OBSERVADO':'PERFIL_FORMAL_COMPATIBLE'},0))
    def test_near_not_fixed(self): self.assertFalse(fixed_allowed('APROXIMA',{'CA|PLAN':1},{'CA|PLAN':'PERFIL_FORMAL_COMPATIBLE'},0))
    def test_no_splitting_groups(self): self.assertEqual(solve({'P':5},{'V1':2,'V2':3},{'P':['V1','V2']})[0],'NO_CUADRA')
    def test_ambiguous(self): self.assertEqual(solve({'P':2,'Q':2},{'V1':2,'V2':2},{'P':['V1','V2'],'Q':['V1','V2']})[0],'AMBIGUA')

if __name__=='__main__': unittest.main()
