import copy
import json
from pathlib import Path
import unittest

from common.versiones_por_cohorte import clave_grupo, resolver_cohorte

ROOT = Path(__file__).resolve().parents[1]


def history(version, start, duration='8', tipo='1'):
    return {'codigo_unico': 'I162S2C77J4V'+str(version), 'familia': 'I162S2C77J4',
            'inicio_oferta': start, 'anual': [{'anio': start, 'duracion_total': duration,
                                             'tipo_plan': tipo, 'registro_csv': 2}]}


class CohorteTests(unittest.TestCase):
    def setUp(self):
        self.group = {'familias': ['I162S2C77J4'], 'perfiles_duracion_tipo': [['8','1']]}

    def test_regular_y_continuidad_no_compiten_por_fecha(self):
        histories = [history(1,2024),history(2,2025,'4','3')]
        regular = resolver_cohorte(self.group,histories,anoingreso=2025)
        self.assertEqual(regular['codigo_propuesto'],'I162S2C77J4V1')
        self.group['perfiles_duracion_tipo'] = [['4','3']]
        continuity = resolver_cohorte(self.group,histories,anoingreso=2025)
        self.assertEqual(continuity['codigo_propuesto'],'I162S2C77J4V2')
        self.assertEqual(continuity['estado'],'COINCIDENCIA_INICIO')

    def test_nombres_distintos_no_bloquean(self):
        original = resolver_cohorte(self.group,[history(1,2024)],anoingreso=2024)
        other = dict(self.group,nombre_interno='CONTINUIDAD OTRO TEXTO',nombre_sies='NOMBRE FORMAL')
        self.assertEqual(original,resolver_cohorte(other,[history(1,2024)],anoingreso=2024))

    def test_no_elige_numero_de_version_maximo(self):
        result = resolver_cohorte(self.group,[history(9,2018),history(2,2020)],anoingreso=2021)
        self.assertEqual(result['codigo_propuesto'],'I162S2C77J4V2')
        self.assertEqual(result['estado'],'INTERVALO_PROPUESTO')

    def test_empate_no_elige_primera_fila(self):
        candidates = [history(1,2019),history(2,2019)]
        a=resolver_cohorte(self.group,candidates,anoingreso=2020)
        b=resolver_cohorte(self.group,candidates[::-1],anoingreso=2020)
        self.assertEqual(a['estado'],'EMPATE_PRIMERA_OFERTA')
        self.assertIsNone(a['codigo_propuesto'])
        self.assertEqual(a['candidatos_fecha'],b['candidatos_fecha'])

    def test_no_completa_antes_de_cobertura(self):
        result=resolver_cohorte(self.group,[history(1,2010)],anoingreso=2008)
        self.assertEqual(result['estado'],'COHORTE_ANTERIOR_COBERTURA_OFERTA')
        self.assertIsNone(result['codigo_propuesto'])

    def test_cohorte_previa_no_se_cambia_a_regular(self):
        self.group['perfiles_duracion_tipo']=[['4','3']]
        result=resolver_cohorte(self.group,[history(1,2024),history(2,2025,'4','3')],anoingreso=2024)
        self.assertEqual(result['estado'],'COHORTE_ANTERIOR_INICIO_OFERTA')

    def test_perfil_del_anio_no_del_corte_actual(self):
        candidate=history(1,2010,'8')
        candidate['anual'].append({'anio':2020,'duracion_total':'6','tipo_plan':'1','registro_csv':3})
        self.assertEqual(resolver_cohorte(self.group,[candidate],anoingreso=2020)['estado'],
                         'SIN_VERSION_DEL_PERFIL_EN_OFERTA')

    def test_perfil_ausente_no_se_deduce_del_nombre(self):
        self.group['perfiles_duracion_tipo']=[]
        self.group['nombre']='CONTINUIDAD'
        self.assertEqual(resolver_cohorte(self.group,[history(1,2020)],anoingreso=2020)['estado'],
                         'PERFIL_DURACION_NO_DETERMINADO_EN_GRUPO')

    def test_perfiles_distintos_no_se_deciden_por_fecha(self):
        self.group['perfiles_duracion_tipo']=[['8','1'],['4','3']]
        result=resolver_cohorte(self.group,[history(1,2024),history(2,2025,'4','3')],anoingreso=2025)
        self.assertEqual(result['estado'],'AMBIGUEDAD_PERFIL_DURACION')

    def test_dato_invalido_y_fuera_ambito(self):
        self.assertEqual(resolver_cohorte(self.group,[],anoingreso=None)['estado'],'ANOINGRESO_AUSENTE_O_INVALIDO')
        self.assertEqual(resolver_cohorte(self.group,[],anoingreso=2027)['estado'],'FUERA_AMBITO_2007_2026')

    def test_clave_sin_colisiones(self):
        self.assertNotEqual(clave_grupo('A|B','C','O'),clave_grupo('A','B|C','O'))


class RealTests(unittest.TestCase):
    def test_conserva_equivalencias_y_combinaciones(self):
        base=ROOT/'data/versiones_por_cohorte/20261016'
        groups=json.loads((base/'grupos_existentes.json').read_text())
        results=json.loads((base/'resultados_cohortes.json').read_text())
        master=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json').read_text())
        source=json.loads((ROOT/'data/diccionario_sies_umas/20261015/evidencia/ejemplos_umas.json').read_text())
        self.assertEqual({x for g in groups for x in g['equivalencias_h5']},
                         {r['id'] for r in master['equivalencias_programa_2026']})
        self.assertEqual(len(results),len(source['combinaciones_unicas']))
        for actual, original in zip(results,source['combinaciones_unicas']):
            self.assertEqual(actual['datos_alumnos']['ANOINGRESO'],original['ANOINGRESO'])
            self.assertEqual(actual['datos_alumnos']['ANOMATRICULA'],original['ANOMATRICULA'])

    def test_anoingreso_diferente_de_anomatricula(self):
        results=json.loads((ROOT/'data/versiones_por_cohorte/20261016/resultados_cohortes.json').read_text())
        selected=[r for r in results if r['datos_alumnos']['CODCARPR']=='CILOG'
                  and r['datos_alumnos']['ANOMATRICULA']=='2026' and r['datos_alumnos']['ANOINGRESO']=='2025']
        self.assertTrue(selected)
        self.assertTrue(all(r['resolucion']['estado']=='COINCIDENCIA_INICIO' for r in selected))
        self.assertTrue(all(r['resolucion']['codigo_propuesto']=='I162S2C77J4V2' for r in selected))


if __name__=='__main__': unittest.main()
