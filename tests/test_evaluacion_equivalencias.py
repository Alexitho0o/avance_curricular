"""Evita acreditaciones por coincidencia superficial, fecha o unidad incompatible."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common.evaluacion_equivalencias import (
    CAMPOS_MRUN, clave_contexto, comparar_literal, conciliar_oferta_mrun, evaluar_candidato,
)

ROOT = Path(__file__).resolve().parents[1]


class EvaluacionTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {'id': 'CP-test', 'ambito_candidato': 2026, 'codcarpr': 'CILOG',
                          'plan_umas': 'CILOG20241', 'sede_umas': 'RE', 'jornada_umas': 'O',
                          'nombre_interno': 'CONTINUIDAD INGENIERIA LOGISTICA',
                          'codigo_unico': 'I162S2C77J4V2',
                          'componentes_sies': {'sede': '2', 'jornada': '4'},
                          'equivalencias_ids': ['EP-test']}
        self.plan = {'nombres_carrera': ['CONTINUIDAD INGENIERIA LOGISTICA'],
                     'niveles_observados': ['1', '2', '3', '4', '5', '6']}
        self.observations = [{'PLAN_DE_ESTUDIO': 'CILOG20241', 'CODCARR': 'CILOG',
                              'JORNADA': 'O', 'ANO': '2025', 'REGIMEN': 'TRIMESTRAL', 'fila_tsv': 2},
                             {'PLAN_DE_ESTUDIO': 'CILOG20241', 'CODCARR': 'CILOG',
                              'JORNADA': 'O', 'ANO': '2026', 'REGIMEN': 'TRIMESTRAL', 'fila_tsv': 3}]
        self.offer = {'anio': 2026, 'codigo_unico': 'I162S2C77J4V2', 'registro_csv': 100,
                      'campos_originales': {k: '' for k in CAMPOS_MRUN}}
        self.offer['campos_originales'].update({'Régimen': '1', 'Duración formal del Régimen': '4',
                                                'Duración Estudios': '4', 'Tipo Carrera': 'Plan Regular de Continuidad'})
        self.maps = {'sedes': {'RE': '2'}, 'jornadas': {'O': '4'}}
        self.start = {'anio_inicio_diccionario': 2025}

    def evaluate(self):
        return evaluar_candidato(self.candidate, self.plan, self.observations,
                                  self.offer, self.start, self.maps)

    def test_ausencias_no_son_coincidencias(self):
        for a, b in [('', ''), (None, None), ('NULL', 'NULL'), ('', 'Presencial')]:
            self.assertEqual(comparar_literal(a, b), 'DESCONOCIDO')

    def test_claves_no_colisionan_por_concatenacion(self):
        a = dict(self.candidate, codcarpr='A|B', plan_umas='C')
        b = dict(self.candidate, codcarpr='A', plan_umas='B|C')
        self.assertNotEqual(clave_contexto(a), clave_contexto(b))

    def test_no_infiere_perfil_de_nombre_o_jornada(self):
        result = self.evaluate()
        for key in ('tipo_plan', 'modalidad_programa', 'nivel_programa'):
            self.assertIsNone(result['perfil_umas'][key])
        self.assertFalse(result['habilitada_para_resolver'])

    def test_no_convierte_niveles_en_semestres(self):
        result = self.evaluate()
        self.assertEqual(result['comparacion_perfil']['regimen_2026'], 'DIFERENTE')
        self.assertEqual(result['comparacion_perfil']['duracion'],
                         'NO_COMPARABLE_SIN_DEFINICION_NIVEL_Y_CONVERSION')

    def test_no_usa_anio_del_identificador(self):
        result = self.evaluate()
        self.assertEqual(result['cronologia']['inicio_oferta_codigo'], 2025)
        self.assertEqual(result['cronologia']['anios_actividad_observada'], [2025, 2026])
        self.assertIsNone(result['cronologia']['vigencia_equivalencia'])

    def test_actividad_anterior_no_habilita_ni_descarta(self):
        self.start['anio_inicio_diccionario'] = 2026
        result = self.evaluate()
        self.assertTrue(result['cronologia']['actividad_anterior_a_primera_oferta'])
        self.assertEqual(result['estado'], 'CANDIDATA_PENDIENTE_EVIDENCIA')

    def test_jornada_tres_no_se_equipara_a_cuatro(self):
        self.candidate['componentes_sies']['jornada'] = '3'
        self.assertEqual(self.evaluate()['identidad_2026']['jornada'], 'DIFERENTE')

    def test_no_traslada_regimen_de_otra_jornada_o_anio(self):
        self.observations[1]['JORNADA'] = 'V'
        result = self.evaluate()
        self.assertEqual(result['perfil_umas']['regimenes_observados_2026'], [])
        self.assertEqual(result['comparacion_perfil']['regimen_2026'], 'DESCONOCIDO')

    def test_rechaza_otro_anio_y_codigo(self):
        self.offer['anio'] = 2027
        with self.assertRaises(ValueError):
            self.evaluate()
        self.offer['anio'] = 2026
        self.offer['codigo_unico'] = 'I162S2C77J4V1'
        with self.assertRaises(ValueError):
            self.evaluate()

    def test_mrun_y_oferta_se_unen_por_codigo_y_anio(self):
        mrun = {'cat_periodo': '2025', 'codigo_unico': self.offer['codigo_unico']}
        result = conciliar_oferta_mrun([self.offer], [mrun])
        self.assertEqual([r['presencia'] for r in result], ['SOLO_MRUN', 'SOLO_OFERTA'])
        self.assertTrue(all(not r['campos'] for r in result))

    def test_conserva_perfiles_mrun_discrepantes(self):
        a = {'cat_periodo': '2026', 'codigo_unico': self.offer['codigo_unico'],
             **{k: '' for k in CAMPOS_MRUN.values()}, 'dur_estudio_carr': '4'}
        b = dict(a, dur_estudio_carr='8')
        result = conciliar_oferta_mrun([self.offer], [a, b])[0]
        self.assertEqual(result['campos']['Duración Estudios']['estado'], 'DIFERENTE')
        self.assertEqual(len(result['campos']['Duración Estudios']['comparaciones']), 2)
        self.assertEqual(result['campos']['Modalidad']['estado'], 'DESCONOCIDO')

    def test_rechaza_oferta_duplicada(self):
        with self.assertRaises(ValueError):
            conciliar_oferta_mrun([self.offer, copy.deepcopy(self.offer)], [])


class UniversoRealTests(unittest.TestCase):
    def test_rechaza_maestro_alterado_antes_de_procesar(self):
        from scripts import evaluar_equivalencias_historicas as runner
        original = Path.read_bytes
        master = ROOT / 'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json'
        def changed(path):
            raw = original(path)
            return raw + b' ' if path == master else raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'Fuente alterada'):
            runner.build()

    def test_salida_distinta_no_se_sobrescribe_ni_escribe_parcial(self):
        from scripts import evaluar_equivalencias_historicas as runner
        with tempfile.TemporaryDirectory(dir=ROOT / 'data/versiones_historicas_sies_umas') as temporary:
            target = Path(temporary)
            (target / 'resumen.json').write_text('conservar')
            with patch.object(runner, 'OUT', target), patch.object(runner, 'build',
                    return_value={'nuevo.json': [], 'resumen.json': {}}), patch('sys.argv', ['evaluar']):
                with self.assertRaisesRegex(ValueError, 'Salida existente distinta'):
                    runner.main()
            self.assertEqual((target / 'resumen.json').read_text(), 'conservar')
            self.assertFalse((target / 'nuevo.json').exists())

    def test_preserva_todos_los_codigos_planes_y_candidatos(self):
        root = ROOT / 'data/versiones_historicas_sies_umas'
        master = json.loads((root / 'fase_5_20261015/maestro.json').read_text())
        out = root / 'fase_b_20261015'
        candidates = json.loads((out / 'evaluacion_candidatos.json').read_text())
        self.assertEqual({r['id_candidato_h5'] for r in candidates},
                         {r['id'] for r in master['candidatos_plan_sies']})
        self.assertEqual({r['codigo_unico'] for r in json.loads((out / 'cobertura_sies.json').read_text())},
                         {r['codigo_unico'] for r in master['universo_sies']})
        self.assertEqual({r['plan_umas'] for r in json.loads((out / 'cobertura_umas.json').read_text())},
                         {r['CODPESTUD'] for r in master['planes_umas']})
        self.assertTrue(all(r['habilitada_para_resolver'] is False and r['brechas'] for r in candidates))

    def test_logistica_separada_y_caso_historico_preservado(self):
        out = ROOT / 'data/versiones_historicas_sies_umas/fase_b_20261015'
        codes = {r['codigo_unico']: r for r in json.loads((out / 'cobertura_sies.json').read_text())}
        self.assertEqual(codes['I162S2C77J4V1']['inicio']['anio_inicio_diccionario'], 2024)
        self.assertEqual(codes['I162S2C77J4V2']['inicio']['anio_inicio_diccionario'], 2025)
        changes = json.loads((out / 'cambios_atributos_codigo.json').read_text())
        selected = [r for r in changes if r['codigo_unico'] == 'I162S2C35J4V1' and r['anios_observados'] == [2018, 2019]]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['cambios']['Duración Estudios'], ['5', '6'])
        self.assertEqual(selected[0]['causa'], 'NO_ACREDITADA')


if __name__ == '__main__':
    unittest.main()
