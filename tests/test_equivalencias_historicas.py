"""Pruebas H5 sintéticas: no confundir candidato, equivalencia y asignación."""
from copy import deepcopy
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SPEC = spec_from_file_location('equivalencias_historicas', ROOT / 'common/equivalencias_historicas.py')
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)

V1, V2 = 'I162S2C77J4V1', 'I162S2C77J4V2'
NAME = 'INGENIERÍA EN LOGÍSTICA'
PLACEHOLDER_HASH = 'a' * 64


def offer(year=2026, code=V1):
    return {
        'anio': year, 'codigo_unico': code,
        'componentes_sies': {'institucion': '162', 'sede': '2', 'carrera': '77',
                            'jornada': '4', 'version': code.rsplit('V', 1)[1]},
        'nombre_carrera': NAME, 'nombre_oferta_2026': NAME,
        'modalidad': 'No Presencial', 'tipo_plan_sies': 'Plan Regular',
        'fuente': {'id': 'oferta', 'localizador': {'hoja': 'SINTETICA', 'fila': 2}},
    }


def candidate(code=V1):
    return {
        'codcarpr': 'LOG', 'nombre_interno': NAME, 'nombre_plan_catalogo': [NAME],
        'plan_umas': 'PLAN20201', 'sede_umas': 'RE', 'jornada_umas': 'O',
        'codigo_unico': code, 'ambito_candidato': 2026,
        'estado': 'PENDIENTE_EQUIVALENCIA_PLAN_Y_AMBITO_TEMPORAL',
        'equivalencias_ids': ['EP-SINTETICA'], 'presencia_oferta_2026': True,
    }


def maestro():
    return {
        'schema_version': 1, 'periodo_objetivo': [2007, 2026],
        'fuentes': {
            'oferta': {'path': 'oferta_sintetica.tsv', 'sha256': PLACEHOLDER_HASH, 'role': 'sintetica'},
            'acreditacion': {'path': 'evidencia.txt', 'sha256': PLACEHOLDER_HASH, 'role': 'sintetica'},
        },
        'oferta_anual': [offer()], 'mrun_anual': [], 'universo_sies': [],
        'planes_umas': [], 'equivalencias_programa_2026': [],
        'candidatos_plan_sies': [], 'reglas_efectivas': [],
    }


def rule(rule_id='RE-SINTETICA', code=V1, periods=None):
    return {
        'id': rule_id, 'estado': 'ACREDITADA', 'codcarpr': 'LOG',
        'nombre_interno': NAME, 'plan_umas': 'PLAN20201', 'sede_umas': 'RE',
        'jornada_umas': 'O', 'codigo_unico': code,
        'componentes_sies': offer(code=code)['componentes_sies'],
        'periodos': periods if periods is not None else [{'anio': 2026, 'periodo': '2', 'regimen': 'T'}],
        'evidencias': [
            {'tipo': kind, 'path': 'evidencia.txt', 'sha256': PLACEHOLDER_HASH,
             'localizador': 'Cláusula sintética ' + str(n)}
            for n, kind in enumerate(('EQUIVALENCIA_PLAN_SIES', 'AMBITO_TEMPORAL'), 1)
        ],
    }


def query(data, **overrides):
    values = dict(anio=2026, periodo='2', regimen='T', codcarpr='LOG', nombre_interno=NAME,
                  plan_umas='PLAN20201', sede_umas='RE', jornada_umas='O')
    values.update(overrides)
    return M.resolver_umas(data, **values)


def write_master(folder, data, with_evidence=False):
    data = deepcopy(data)
    if with_evidence:
        (folder / 'evidencia.txt').write_text('Respaldo sintético de prueba.\n')
        digest = hashlib.sha256((folder / 'evidencia.txt').read_bytes()).hexdigest()
        data['fuentes']['acreditacion']['sha256'] = digest
        for item in data['reglas_efectivas']:
            for evidence in item['evidencias']:
                evidence['sha256'] = digest
    path = folder / 'maestro.json'
    raw = (json.dumps(data, ensure_ascii=False, sort_keys=True) + '\n').encode()
    path.write_bytes(raw)
    (folder / 'manifest.json').write_text(json.dumps({'outputs': {'maestro.json': hashlib.sha256(raw).hexdigest()}}))
    return path


class EquivalenceTests(unittest.TestCase):
    def test_single_candidate_does_not_accredit_equivalence(self):
        data = maestro()
        data['candidatos_plan_sies'] = [candidate()]
        result = query(data)
        self.assertEqual(result['estado'], 'PENDIENTE_EVIDENCIA')
        self.assertIsNone(result['codigo_unico'])
        self.assertFalse(result['acredita_asignacion_individual'])
        self.assertEqual(len(result['candidatos']), 1)

    def test_multiple_candidates_do_not_select_max_version(self):
        data = maestro()
        data['oferta_anual'].append(offer(code=V2))
        data['candidatos_plan_sies'] = [candidate(V2), candidate(V1)]
        result = query(data)
        self.assertEqual(result['estado'], 'PENDIENTE_EVIDENCIA')
        self.assertIsNone(result['codigo_unico'])
        self.assertEqual([x['codigo_unico'] for x in result['candidatos']], [V1, V2])

    def test_candidate_scope_does_not_expand_to_plan_year_or_observation_year(self):
        data = maestro()
        data['oferta_anual'].append(offer(2020))
        data['candidatos_plan_sies'] = [{**candidate(), 'anios_actividad_observada_jornada': [2020, 2026]}]
        result = query(data, anio=2020)
        self.assertEqual(result['estado'], 'SIN_EQUIVALENCIA')
        self.assertEqual(result['candidatos'], [])
        self.assertIsNone(result['codigo_unico'])

    def test_every_query_dimension_is_required_and_year_is_not_coerced(self):
        for field in ('anio', 'periodo', 'regimen', 'codcarpr', 'nombre_interno',
                      'plan_umas', 'sede_umas', 'jornada_umas'):
            with self.subTest(field=field):
                result = query(maestro(), **{field: None})
                self.assertEqual(result['estado'], 'ENTRADA_INCOMPLETA')
                self.assertIn(field, result['campos_faltantes_o_invalidos'])
        for invalid in ('2026', True, 2026.0):
            self.assertEqual(query(maestro(), anio=invalid)['estado'], 'ENTRADA_INCOMPLETA')
        self.assertEqual(query(maestro(), anio=2027)['estado'], 'FUERA_AMBITO')

    def test_null_tokens_cannot_be_used_as_accredited_keys(self):
        for field in ('periodo', 'regimen', 'codcarpr', 'nombre_interno', 'plan_umas', 'sede_umas', 'jornada_umas'):
            for token in ('NULL', ' none ', 'NaN'):
                with self.subTest(field=field, token=token):
                    self.assertEqual(query(maestro(), **{field: token})['estado'], 'ENTRADA_INCOMPLETA')
        data = maestro()
        data['reglas_efectivas'] = [rule()]
        data['reglas_efectivas'][0]['plan_umas'] = 'NULL'
        with self.assertRaises(ValueError):
            M.validar_maestro(data)

    def test_catalog_name_is_not_an_automatic_alias(self):
        data = maestro()
        data['candidatos_plan_sies'] = [{**candidate(), 'nombre_plan_catalogo': ['LOGÍSTICA REAL']}]
        result = query(data, nombre_interno='LOGÍSTICA REAL')
        self.assertEqual(result['estado'], 'SIN_EQUIVALENCIA')
        self.assertEqual(result['motivo'], 'NOMBRE_INTERNO_NO_COINCIDE')
        self.assertEqual(result['candidatos'], [])
        self.assertEqual(query(data, nombre_interno=NAME.replace('Í', 'I'))['estado'], 'SIN_EQUIVALENCIA')
        self.assertEqual(query(data, nombre_interno='  ' + NAME + '  ')['estado'], 'PENDIENTE_EVIDENCIA')

    def test_j3_is_not_o_and_program_suffix_is_not_removed(self):
        data = maestro()
        code_j3 = 'I162S2C77J3V1'
        offer_j3 = offer(code=code_j3)
        offer_j3['componentes_sies']['jornada'] = '3'
        data['oferta_anual'].append(offer_j3)
        data['candidatos_plan_sies'] = [{**candidate(code_j3), 'jornada_umas': None}]
        self.assertEqual(query(data)['estado'], 'SIN_EQUIVALENCIA')
        data['candidatos_plan_sies'][0]['jornada_umas'] = 'O'
        with self.assertRaises(ValueError):
            M.validar_maestro(data)
        data['candidatos_plan_sies'] = [candidate()]
        for fields in ({'jornada_umas': '4'}, {'codcarpr': 'LOGSP'}, {'sede_umas': '2'}, {'plan_umas': 'PLAN20201SP'}):
            self.assertEqual(query(data, **fields)['estado'], 'SIN_EQUIVALENCIA')

    def test_accredited_rule_requires_exact_period_regime_year_and_name(self):
        data = maestro()
        data['oferta_anual'].append(offer(2024))
        data['oferta_anual'].append(offer(2025))
        data['reglas_efectivas'] = [rule(periods=[
            {'anio': 2024, 'periodo': '2', 'regimen': 'T'},
            {'anio': 2026, 'periodo': '2', 'regimen': 'T'},
        ])]
        result = query(data)
        self.assertEqual(result['estado'], 'EQUIVALENCIA_ACREDITADA')
        self.assertEqual(result['codigo_unico'], V1)
        self.assertFalse(result['acredita_asignacion_individual'])
        self.assertEqual(result['oferta_anual']['nombre_carrera'], NAME)
        for fields in ({'periodo': '1'}, {'regimen': 'S'}, {'anio': 2025}, {'nombre_interno': 'OTRO'}):
            with self.subTest(fields=fields):
                self.assertEqual(query(data, **fields)['estado'], 'SIN_EQUIVALENCIA')

    def test_conflicting_destinations_block_resolution(self):
        data = maestro()
        data['oferta_anual'].append(offer(code=V2))
        data['reglas_efectivas'] = [rule(), rule('RE-OTRA', V2)]
        result = query(data)
        self.assertEqual(result['estado'], 'CONFLICTO_REGLAS')
        self.assertIsNone(result['codigo_unico'])
        self.assertEqual(result['destinos_en_conflicto'], [V1, V2])
        data['reglas_efectivas'][1]['nombre_interno'] = 'OTRO NOMBRE'
        named = query(data)
        other = query(data, nombre_interno='OTRO NOMBRE')
        self.assertEqual(named['estado'], 'EQUIVALENCIA_ACREDITADA')
        self.assertEqual(other['codigo_unico'], V2)
        self.assertNotEqual(named['clave'], other['clave'])
        self.assertIn(NAME, named['clave'])

    def test_same_destination_accumulates_rules_without_false_conflict(self):
        data = maestro()
        data['reglas_efectivas'] = [rule(), rule('RE-OTRA')]
        data['reglas_efectivas'][1]['evidencias'][0]['localizador'] = 'Cláusula adicional'
        result = query(data)
        self.assertEqual(result['estado'], 'EQUIVALENCIA_ACREDITADA')
        self.assertEqual(result['reglas_ids'], ['RE-OTRA', 'RE-SINTETICA'])
        self.assertEqual(len(result['evidencias']), 3)

    def test_missing_annual_coverage_differs_from_missing_code(self):
        data = maestro()
        early = M.consultar_sies(data, anio=2008, codigo_unico='I162M2008N1')
        absent = M.consultar_sies(data, anio=2026, codigo_unico=V2)
        self.assertEqual((early['estado'], early['motivo']), ('SIN_OFERTA_ANUAL', 'SIN_COBERTURA_ANUAL'))
        self.assertEqual((absent['estado'], absent['motivo']), ('SIN_OFERTA_ANUAL', 'CODIGO_NO_OBSERVADO'))
        data['candidatos_plan_sies'] = [{**candidate(V2), 'presencia_oferta_2026': False}]
        self.assertEqual(query(data)['motivo'], 'CODIGO_NO_OBSERVADO')
        data['candidatos_plan_sies'] = []
        self.assertEqual(query(data)['estado'], 'SIN_EQUIVALENCIA')

    def test_direct_sies_query_preserves_literals_without_umas_claim(self):
        data = maestro()
        data['oferta_anual'][0]['nombre_carrera'] = 'Nombre anual literal'
        data['oferta_anual'][0]['modalidad'] = None
        result = M.consultar_sies(data, anio=2026, codigo_unico=V1)
        self.assertEqual(result['estado'], 'OFERTA_ANUAL_LOCALIZADA')
        self.assertFalse(result['acredita_equivalencia_umas'])
        self.assertFalse(result['acredita_asignacion_individual'])
        self.assertEqual(result['oferta_anual']['nombre_carrera'], 'Nombre anual literal')
        self.assertEqual(result['oferta_anual']['nombre_oferta_2026'], NAME)
        self.assertIsNone(result['oferta_anual']['modalidad'])

    def test_legacy_code_without_offer_retains_exact_annual_mrun_trace(self):
        data = maestro()
        legacy = 'I162M2008N1'
        record = {'cat_periodo': '2008', 'codigo_unico': legacy,
                  'filas_matricula': 4, 'registro_ejemplo': 15, 'nomb_carrera': 'PROGRAMA SINTÉTICO'}
        data['mrun_anual'] = [record, {**record, 'cat_periodo': '2009'},
                             {**record, 'codigo_unico': 'I162M2008N3'}]
        result = M.consultar_sies(data, anio=2008, codigo_unico=legacy)
        self.assertEqual(result['estado'], 'SIN_OFERTA_ANUAL')
        self.assertEqual(result['motivo'], 'SIN_COBERTURA_ANUAL')
        self.assertEqual(result['observaciones_mrun'], [record])
        self.assertIsNone(result['codigo_unico'])
        self.assertFalse(result['acredita_asignacion_individual'])

    def test_invalid_rule_evidence_periods_and_components_are_rejected(self):
        mutations = (
            lambda r: r.update(evidencias=r['evidencias'][:1]),
            lambda r: r['componentes_sies'].update(version='2'),
            lambda r: r['periodos'].append(dict(r['periodos'][0])),
            lambda r: r['periodos'][0].update(anio=2025),
            lambda r: r['periodos'][0].update(periodo=''),
            lambda r: r['evidencias'][0].update(localizador=''),
            lambda r: r['evidencias'][0].update(sha256='incorrecto'),
            lambda r: r['evidencias'][0].update(path='otra_evidencia.txt'),
            lambda r: r.update(estado='PENDIENTE'),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                data = maestro()
                data['reglas_efectivas'] = [rule()]
                mutation(data['reglas_efectivas'][0])
                with self.assertRaises(ValueError):
                    M.validar_maestro(data)

    def test_duplicate_offers_candidates_or_rule_ids_are_rejected(self):
        cases = []
        data = maestro()
        data['oferta_anual'].append(offer())
        cases.append(data)
        data = maestro()
        data['candidatos_plan_sies'] = [candidate(), candidate()]
        cases.append(data)
        data = maestro()
        data['reglas_efectivas'] = [rule(), rule()]
        cases.append(data)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                M.validar_maestro(data)

    def test_loading_verifies_manifest_and_effective_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            data = maestro()
            data['reglas_efectivas'] = [rule()]
            path = write_master(folder, data, with_evidence=True)
            loaded = M.cargar_maestro(path)
            self.assertEqual(query(loaded)['estado'], 'EQUIVALENCIA_ACREDITADA')
            (folder / 'evidencia.txt').write_text('Contenido alterado')
            with self.assertRaisesRegex(ValueError, 'evidencia alterada'):
                M.cargar_maestro(path)

    def test_altered_master_and_missing_manifest_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            path = write_master(folder, maestro())
            path.write_bytes(path.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'maestro distinto'):
                M.cargar_maestro(path)
            (folder / 'manifest.json').unlink()
            with self.assertRaises(OSError):
                M.cargar_maestro(path)

    def test_determinism_and_no_mutation(self):
        data = maestro()
        data['oferta_anual'].append(offer(code=V2))
        data['candidatos_plan_sies'] = [candidate(), candidate(V2)]
        original = deepcopy(data)
        result = query(data)
        self.assertEqual(data, original)
        data['oferta_anual'].reverse()
        data['candidatos_plan_sies'].reverse()
        self.assertEqual(query(data), result)

    def test_cli_distinguishes_pending_from_direct_offer(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            data = maestro()
            data['candidatos_plan_sies'] = [candidate()]
            path = write_master(folder, data)
            command = [sys.executable, str(ROOT / 'scripts/consultar_equivalencias_historicas.py'),
                       '--maestro', str(path), '--anio', '2026']
            direct = subprocess.run(command + ['--codigo-unico', V1], capture_output=True, text=True)
            self.assertEqual(direct.returncode, 0, direct.stderr)
            self.assertEqual(json.loads(direct.stdout)['estado'], 'OFERTA_ANUAL_LOCALIZADA')
            pending = subprocess.run(command + [
                '--codcarpr', 'LOG', '--nombre-interno', NAME, '--plan-umas', 'PLAN20201',
                '--sede-umas', 'RE', '--jornada-umas', 'O', '--periodo', '2', '--regimen', 'T',
            ], capture_output=True, text=True)
            self.assertEqual(pending.returncode, 2, pending.stderr)
            self.assertEqual(json.loads(pending.stdout)['estado'], 'PENDIENTE_EVIDENCIA')
            self.assertIsNone(json.loads(pending.stdout)['codigo_unico'])


if __name__ == '__main__':
    unittest.main()
