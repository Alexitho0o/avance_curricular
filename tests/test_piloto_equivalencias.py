"""Pruebas sintéticas H6 de adaptación, pesos y límites de la evidencia."""
from collections import defaultdict
from copy import deepcopy
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
SPEC = spec_from_file_location('piloto_equivalencias', ROOT / 'scripts/validar_piloto_equivalencias.py')
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)

NAME = 'INGENIERÍA SINTÉTICA'
CODE = 'I162S2C77J4V1'


def plan(code='PLAN20241', contexts=None):
    return {
        'CODPESTUD': code,
        'contextos_catalogo': contexts if contexts is not None else [{'Codcarr': 'SINT', 'Sede': 'RE'}],
        'presencia': 'CATALOGO_Y_PROMEDIOS', 'anios_actividad_observada': [2026],
        'candidatos_plan_sies': 1,
    }


def offer(year=2026, code=CODE):
    return {
        'anio': year, 'codigo_unico': code,
        'componentes_sies': {'institucion': '162', 'sede': '2', 'carrera': '77', 'jornada': '4', 'version': '1'},
        'nombre_carrera': NAME, 'nombre_oferta_2026': NAME, 'modalidad': 'No Presencial',
        'tipo_plan_sies': 'Plan Regular', 'vigencia': 'Vigente con estudiantes nuevos',
        'fuente': {'id': 'oferta', 'localizador': {'hoja': 'SINTETICA', 'fila': 2}},
    }


def master():
    return {
        'schema_version': 1, 'periodo_objetivo': [2007, 2026],
        'fuentes': {'oferta': {'path': 'oferta_sintetica.tsv', 'sha256': 'a' * 64, 'role': 'prueba'}},
        'oferta_anual': [offer()], 'mrun_anual': [],
        'universo_sies': [{'codigo_unico': CODE, 'presencia': 'SOLO_OFERTA',
                          'nombre_literal_oferta_2026': NAME, 'nombre_2026_estado': 'OFERTA_2026_LITERAL'}],
        'planes_umas': [plan()], 'equivalencias_programa_2026': [],
        'candidatos_plan_sies': [{
            'id': 'CP-SINTETICO', 'codcarpr': 'SINT', 'nombre_interno': NAME,
            'nombre_plan_catalogo': [NAME], 'plan_umas': 'PLAN20241', 'sede_umas': 'RE',
            'jornada_umas': 'O', 'codigo_unico': CODE, 'ambito_candidato': 2026,
            'estado': 'PENDIENTE_EQUIVALENCIA_PLAN_Y_AMBITO_TEMPORAL',
            'equivalencias_ids': ['EP-SINTETICA'], 'presencia_oferta_2026': True,
        }],
        'reglas_efectivas': [],
    }


def context(**overrides):
    row = {
        'PLAN_DE_ESTUDIO': 'PLAN20241', 'CODCARR': 'SINT', 'CARRERA': NAME,
        'JORNADA': 'O', 'ANO': '2026', 'PERIODO': '2', 'REGIMEN': 'TRIMESTRAL',
        'estado_observacion': 'OBSERVACION_CON_ANIO', 'estado_plan_catalogo': 'PLAN_CONTEXTO_UNICO',
        'carrera_plan_vs_promedios': 'IGUAL', 'CODCARR_LISTADO': 'SINT', 'SEDE_LISTADO': 'RE',
        'estado_ramo': 'RAMO_EN_PLAN', 'estado_datos_alumnos': 'CONTEXTO_UNICO_DEL_REPORTE',
        'carrera_da_vs_promedios': 'IGUAL', 'jornada_da_vs_promedios': 'IGUAL',
        'sede_da_vs_plan': 'IGUAL', 'ambito_anio_matricula_da': 'DENTRO_AMBITO',
        'CODCARPR_DA': 'SINT', 'JORNADA_DA': 'O', 'SEDE_DA': 'RE',
        'ANOMATRICULA_DA': '2026', 'ANOINGRESO_DA': '2024',
        'filas_reporte': '3', 'fila_promedios_ejemplo': '10',
        'fila_alumnos_ejemplo': '20', 'fila_plan_ejemplo': '2',
        'identificadores_internos_distintos': '2',
    }
    row.update(overrides)
    return row


def observations(rows):
    """Proyección académica equivalente a H4, sin sumar personas entre grupos."""
    groups = defaultdict(int)
    for row in rows:
        groups[tuple(row[field] for field in M.OBS_FIELDS)] += int(row['filas_reporte'])
    return [{**dict(zip(M.OBS_FIELDS, values)), 'filas_reporte': str(total)}
            for values, total in sorted(groups.items())]


def plan_index(data=None):
    return {row['CODPESTUD']: row for row in (data or master())['planes_umas']}


def relocation_fixture(folder):
    """Fuentes y manifiestos mínimos de texto; nunca abre archivos reales XLSX."""
    def write(name, content):
        path = folder / name
        path.write_text(content)
        return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    original = write('ruta_original.txt', 'Contenido nuevo distinto del histórico')
    backup = write('respaldo_historico.txt', 'Contenido histórico congelado')
    historical = {'path': original['path'], 'sha256': backup['sha256']}
    h5 = {'schema_version': 1, 'periodo_objetivo': [2007, 2026],
          'sources': {'promedios': dict(historical)}, 'referencias_congeladas': [dict(historical)]}
    sources = {
        'fuentes_h5': write('fuentes_h5.json', json.dumps(h5)),
        'respaldo': backup,
        'contextos_h4': write('contextos_h4.tsv', 'Proyección sintética de contextos'),
        'observaciones_h4': write('observaciones_h4.tsv', 'Proyección sintética de observaciones'),
        'maestro_h5': write('maestro_h5.json', '{}'),
    }
    sources['manifest_h4'] = write('manifest_h4.json', json.dumps({'outputs': {
        'conciliacion_contextos_umas.tsv': sources['contextos_h4']['sha256'],
        'observaciones_plan_periodo.tsv': sources['observaciones_h4']['sha256'],
    }}))
    sources['manifest_h5'] = write('manifest_h5.json', json.dumps({'outputs': {
        'maestro.json': sources['maestro_h5']['sha256'],
        'fuentes.json': sources['fuentes_h5']['sha256'],
    }, 'scripts_sha256': {}}))
    return {'schema_version': 1, 'fase': 6, 'periodo_objetivo': [2007, 2026],
            'sources': sources, 'reubicaciones_fuentes': {original['path']: dict(backup)}}


class PilotTests(unittest.TestCase):
    def test_exclusion_precedence_keeps_invalid_year_and_scope_before_missing_plan(self):
        for year, expected in [('NULL', 'ANIO_NO_VALIDO'), ('20x6', 'ANIO_NO_VALIDO'),
                               ('2027', 'FUERA_AMBITO'), ('2026', 'PLAN_SIN_CONTEXTO_UNICO')]:
            with self.subTest(year=year):
                row = context(ANO=year, PLAN_DE_ESTUDIO='SIN_CATALOGO', SEDE_LISTADO='')
                state, reasons, query = M.adaptar_contexto(row, plan_index())
                self.assertEqual(state, expected)
                self.assertTrue(reasons)
                self.assertIsNone(query)

    def test_h4_observation_state_does_not_replace_eight_dimension_validation(self):
        for field in ('CARRERA', 'JORNADA', 'REGIMEN', 'PERIODO', 'CODCARR', 'SEDE_LISTADO'):
            for value in ('NULL', ' none ', 'NaN', '  ', None):
                with self.subTest(field=field, value=value):
                    row = context(**{field: value})
                    state, _, query = M.adaptar_contexto(row, plan_index())
                    self.assertEqual(row['estado_observacion'], 'OBSERVACION_CON_ANIO')
                    self.assertEqual(state, 'CLAVES_INCOMPLETAS')
                    self.assertIsNone(query)

    def test_plan_context_must_be_corroborated_with_master(self):
        data = master()
        data['planes_umas'][0]['contextos_catalogo'].append({'Codcarr': 'SINT', 'Sede': 'CO'})
        state, _, query = M.adaptar_contexto(context(), plan_index(data))
        self.assertEqual(state, 'PLAN_SIN_CONTEXTO_UNICO')
        self.assertIsNone(query)
        data['planes_umas'][0]['contextos_catalogo'] = []
        self.assertEqual(M.adaptar_contexto(context(), plan_index(data))[0], 'PLAN_SIN_CONTEXTO_UNICO')

    def test_discrepant_career_is_not_repaired_from_catalog_or_student_report(self):
        row = context(CODCARR='OTRA', CODCARPR_DA='SINT', carrera_plan_vs_promedios='IGUAL')
        original = deepcopy(row)
        state, reasons, query = M.adaptar_contexto(row, plan_index())
        self.assertEqual(state, 'CARRERA_PLAN_DISCREPANTE')
        self.assertTrue(reasons)
        self.assertIsNone(query)
        self.assertEqual(row, original)

    def test_missing_campus_is_not_borrowed_and_contradictory_catalog_is_rejected(self):
        row = context(SEDE_LISTADO='', SEDE_DA='RE')
        state, _, query = M.adaptar_contexto(row, plan_index())
        self.assertEqual(state, 'CLAVES_INCOMPLETAS')
        self.assertIsNone(query)
        for fields in ({'SEDE_LISTADO': 'CO'}, {'CODCARR_LISTADO': 'OTRA'}):
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, 'contradice catálogo'):
                M.adaptar_contexto(context(**fields), plan_index())

    def test_datos_alumnos_differences_never_change_the_query(self):
        original = context()
        different = context(CODCARPR_DA='OTRA', JORNADA_DA='V', SEDE_DA='CO',
                            ANOMATRICULA_DA='2027', ANOINGRESO_DA='1999',
                            carrera_da_vs_promedios='DIFERENTE', jornada_da_vs_promedios='DIFERENTE',
                            sede_da_vs_plan='DIFERENTE', ambito_anio_matricula_da='FUERA_AMBITO',
                            estado_ramo='RAMO_NO_LOCALIZADO_EN_PLAN')
        self.assertEqual(M.adaptar_contexto(original, plan_index()), M.adaptar_contexto(different, plan_index()))
        query = M.adaptar_contexto(different, plan_index())[2]
        self.assertEqual((query['anio'], query['periodo'], query['regimen']), (2026, '2', 'TRIMESTRAL'))
        self.assertEqual((query['codcarpr'], query['jornada_umas'], query['sede_umas']), ('SINT', 'O', 'RE'))

    def test_duplicate_queries_preserve_each_context_and_all_report_weight(self):
        rows = [context(filas_reporte='3'),
                context(filas_reporte='7', fila_promedios_ejemplo='11', JORNADA_DA='V',
                        jornada_da_vs_promedios='DIFERENTE')]
        with patch.object(M, 'resolver_umas', wraps=M.resolver_umas) as real_resolver:
            result = M.ejecutar_umas(master(), rows, observations(rows))
            self.assertEqual(real_resolver.call_count, 1)
        self.assertEqual(result['resumen']['contextos_entrada'], 2)
        self.assertEqual(result['resumen']['consultas_unicas'], 1)
        self.assertEqual(result['resumen']['filas_reporte'], 10)
        self.assertEqual(result['resumen']['filas_consultables'], 10)
        self.assertEqual([r['filas_reporte'] for r in result['resultados_contextos']], [3, 7])
        self.assertEqual(result['consultas_unicas'][0]['filas_contextos_h4'], [2, 3])
        self.assertEqual(result['consultas_unicas'][0]['filas_reporte'], 10)
        self.assertTrue(all(result['checks'].values()))

    def test_projection_reconciliation_detects_compensations_at_equal_total(self):
        rows = [context(filas_reporte='3', PERIODO='1'), context(filas_reporte='7', PERIODO='2')]
        reported = observations(rows)
        reported[0]['filas_reporte'], reported[1]['filas_reporte'] = '7', '3'
        self.assertEqual(sum(int(r['filas_reporte']) for r in rows), sum(int(r['filas_reporte']) for r in reported))
        with self.assertRaisesRegex(ValueError, 'dimensiones o peso'):
            M.ejecutar_umas(master(), rows, reported)

    def test_invalid_report_weight_is_never_silently_dropped(self):
        for value in ('0', '-1', '1.5', 'NULL', ''):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Peso de reporte inválido'):
                M.reconcile_projections([context(filas_reporte=value)], [context(filas_reporte=value)])

    def test_unique_candidate_remains_pending_and_person_data_is_not_exported(self):
        rows = [context(CODCLI='IDENTIDAD_SINTETICA_NO_EXPORTAR', RUT='RUT_SINTETICO_NO_EXPORTAR',
                        NOMBRE_ALUMNO='NOMBRE_PERSONA_NO_EXPORTAR', NOTA='NOTA_NO_EXPORTAR')]
        result = M.ejecutar_umas(master(), rows, observations(rows))
        output = result['resultados_contextos'][0]
        self.assertEqual(output['estado_resolucion'], 'PENDIENTE_EVIDENCIA')
        self.assertEqual(output['diagnostico'], 'CANDIDATO_UNICO_SIN_ACREDITAR')
        self.assertEqual(output['numero_destinos_candidatos'], 1)
        self.assertIsNone(output['codigo_unico_resuelto'])
        self.assertFalse(output['acredita_asignacion_individual'])
        self.assertEqual(result['resumen']['filas_con_codigo_acreditado'], 0)
        serialized = json.dumps(result, ensure_ascii=False)
        for forbidden in ('NO_EXPORTAR', 'identificadores_internos_distintos', 'NOMBRE_ALUMNO', 'CODCLI', 'RUT'):
            self.assertNotIn(forbidden, serialized)

    def test_plans_without_activity_and_unconsultable_contexts_remain_in_coverage(self):
        data = master()
        data['planes_umas'].append({**plan('SIN_ACTIVIDAD'), 'presencia': 'SOLO_CATALOGO',
                                   'anios_actividad_observada': [], 'candidatos_plan_sies': 0})
        rows = [context(filas_reporte='3'), context(ANO='NULL', filas_reporte='7')]
        result = M.ejecutar_umas(data, rows, observations(rows))
        self.assertEqual(result['resumen']['filas_reporte'], 10)
        self.assertEqual(result['resumen']['filas_consultables'], 3)
        self.assertEqual(result['resumen']['filas_no_consultadas'], 7)
        inactive = next(p for p in result['cobertura_planes'] if p['plan_umas'] == 'SIN_ACTIVIDAD')
        self.assertEqual(inactive['estado_observacion'], 'SIN_OBSERVACION_EN_REPORTE')
        self.assertEqual(inactive['filas_reporte'], 0)
        self.assertEqual(result['resumen']['planes_cubiertos'], 2)

    def test_catalog_name_is_not_used_to_replace_report_name(self):
        rows = [context(CARRERA='NOMBRE DISTINTO DEL REPORTE')]
        result = M.ejecutar_umas(master(), rows, observations(rows))
        query = result['consultas_unicas'][0]
        self.assertEqual(query['nombre_interno'], 'NOMBRE DISTINTO DEL REPORTE')
        self.assertEqual(query['estado_resolucion'], 'SIN_EQUIVALENCIA')
        self.assertEqual(query['diagnostico'], 'NOMBRE_DISTINTO_SIN_ALIAS')
        self.assertIsNone(query['codigo_unico_resuelto'])

    def test_old_activity_does_not_infer_validity_from_plan_label(self):
        data = master()
        data['oferta_anual'].append(offer(2019))
        rows = [context(ANO='2019')]
        result = M.ejecutar_umas(data, rows, observations(rows))
        query = result['consultas_unicas'][0]
        self.assertEqual(query['anio'], 2019)
        self.assertEqual(query['plan_umas'], 'PLAN20241')
        self.assertEqual(query['estado_resolucion'], 'SIN_EQUIVALENCIA')
        self.assertEqual(query['diagnostico'], 'SIN_REGLA_HISTORICA_ACREDITADA')
        self.assertEqual(query['codigos_candidatos'], [])

    def test_resolver_contract_rejects_unaccredited_code_or_individual_claim(self):
        rows = [context()]
        for response in (
            {'estado': 'PENDIENTE_EVIDENCIA', 'codigo_unico': CODE, 'acredita_asignacion_individual': False},
            {'estado': 'SIN_EQUIVALENCIA', 'codigo_unico': None, 'acredita_asignacion_individual': True},
        ):
            with self.subTest(response=response), patch.object(M, 'resolver_umas', return_value=response), self.assertRaises(ValueError):
                M.ejecutar_umas(master(), rows, observations(rows))

    def test_sies_union_retains_offer_only_and_legacy_mrun_with_literal_names(self):
        data = master()
        historical = offer(2019)
        historical['nombre_carrera'] = 'NOMBRE HISTÓRICO LITERAL'
        data['oferta_anual'].append(historical)
        legacy = 'I162M2008N1'
        data['mrun_anual'] = [
            {'cat_periodo': '2008', 'codigo_unico': legacy, 'filas_matricula': '4',
             'nomb_carrera': 'NOMBRE LEGADO MRUN', 'registro_ejemplo': '15'},
            {'cat_periodo': '2019', 'codigo_unico': CODE, 'filas_matricula': '6',
             'nomb_carrera': 'NOMBRE OBSERVADO MRUN', 'registro_ejemplo': '16'},
        ]
        data['universo_sies'].append({'codigo_unico': legacy, 'presencia': 'SOLO_MRUN',
                                    'nombre_literal_oferta_2026': None, 'nombre_2026_estado': 'SIN_OFERTA_2026_OBSERVADA'})
        result = M.ejecutar_sies(data)
        by_key = {(r['anio'], r['codigo_unico']): r for r in result['resultados']}
        self.assertEqual(len(by_key), 3)
        self.assertEqual(by_key[(2026, CODE)]['presencia'], 'SOLO_OFERTA')
        self.assertEqual(by_key[(2026, CODE)]['registros_mrun'], 0)
        self.assertEqual(by_key[(2008, legacy)]['motivo'], 'SIN_COBERTURA_ANUAL')
        self.assertEqual(by_key[(2008, legacy)]['registros_mrun'], 4)
        self.assertIsNone(by_key[(2008, legacy)]['nombre_anual_oferta'])
        self.assertEqual(by_key[(2019, CODE)]['nombre_anual_oferta'], 'NOMBRE HISTÓRICO LITERAL')
        self.assertEqual(by_key[(2019, CODE)]['nombre_oferta_2026'], NAME)
        self.assertEqual(result['resumen']['registros_mrun'], 10)
        self.assertTrue(all(not row['acredita_equivalencia_umas'] and not row['acredita_asignacion_individual']
                            for row in result['resultados']))

    def test_missing_universe_members_or_duplicate_annual_keys_are_rejected(self):
        data = master()
        data['universo_sies'] = []
        with self.assertRaisesRegex(ValueError, 'Cobertura SIES incompleta'):
            M.ejecutar_sies(data)
        data = master()
        data['oferta_anual'].append(offer())
        with self.assertRaisesRegex(ValueError, 'Clave anual repetida'):
            M.ejecutar_sies(data)
        data = master()
        data['planes_umas'] = []
        rows = [context()]
        with self.assertRaisesRegex(ValueError, 'Plan observado perdido'):
            M.ejecutar_umas(data, rows, observations(rows))

    def test_declared_identical_backup_only_relocates_descriptors_in_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            config = relocation_fixture(Path(directory))
            original_config = deepcopy(config)
            source_path = Path(config['sources']['fuentes_h5']['path'])
            bytes_before = source_path.read_bytes()
            with patch.object(M, 'verify_sources') as verify_h5:
                M.verify(config)
                verify_h5.assert_called_once()
                passed = verify_h5.call_args.args[0]
                expected = config['sources']['respaldo']
                self.assertEqual(passed['sources']['promedios'], expected)
                self.assertEqual(passed['referencias_congeladas'], [expected])
            self.assertEqual(config, original_config)
            self.assertEqual(source_path.read_bytes(), bytes_before)

    def test_relocation_rejects_different_hash_undeclared_or_altered_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            config = relocation_fixture(Path(directory))
            original = next(iter(config['reubicaciones_fuentes']))
            different = deepcopy(config)
            different['reubicaciones_fuentes'][original]['sha256'] = 'b' * 64
            undeclared = deepcopy(config)
            del undeclared['sources']['respaldo']
            unknown_original = deepcopy(config)
            unknown_original['reubicaciones_fuentes']['no_declarado.txt'] = unknown_original['reubicaciones_fuentes'].pop(original)
            for invalid, message in ((different, 'hash histórico'), (undeclared, 'no declarado'),
                                     (unknown_original, 'hash histórico')):
                with self.subTest(message=message), patch.object(M, 'verify_sources') as verify_h5:
                    with self.assertRaisesRegex(ValueError, message):
                        M.verify(invalid)
                    verify_h5.assert_not_called()
            Path(config['sources']['respaldo']['path']).write_text('Respaldo alterado')
            with patch.object(M, 'verify_sources') as verify_h5:
                with self.assertRaisesRegex(ValueError, 'Fuente H6 alterada'):
                    M.verify(config)
                verify_h5.assert_not_called()


if __name__ == '__main__':
    unittest.main()
