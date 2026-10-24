"""Casos sintéticos que protegen el grano y los límites de la evidencia UMAS."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


SPEC = spec_from_file_location(
    'estructura_planes_umas',
    Path(__file__).parents[1] / 'scripts/estructura_planes_umas.py',
)
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def course(row=2, plan='PLAN_A', code='RAMO_A', **overrides):
    """Fila académica inventada; no contiene personas ni datos institucionales."""
    result = {
        '_fila': row, 'CODPESTUD': plan, 'CODRAMO': code, 'NIVEL': 1,
        'Codcarr': 'CARRERA_A', 'Nombre_L': 'PROGRAMA SINTETICO',
        'NOMPESTUD': plan, 'Sede': 'SEDE_A', 'NOMBRE': 'ASIGNATURA SINTETICA',
        'REGIMEN': 'S', 'TIPO': 'Obl', 'SESIONES': 1, 'PORC_NOTA_PRES': 1,
        'PORC_NOTA_EXam': None, 'CREDITO': 1, 'Clase': 'PREGRADO',
        'ORDENRAMO': 1, 'HOR_TEO': 20, 'HOR_PRAC': None, 'HOR_AYUD': None,
        'Orden': -1, 'RamoEquiv': '   ', 'DescRamoEquiv': '   ',
        'RamoReq': '   ', 'DescRamoReq': '   ', 'RegimenReq': None,
        'TipoReq': None, 'SesionesReq': None, 'SIGLA': plan, 'NroLinea': '1',
    }
    result.update(overrides)
    return result


class CatalogTests(unittest.TestCase):
    def test_expansions_and_headers_are_not_extra_courses(self):
        rows = [
            course(),
            course(3, RamoReq='Requisitos:', DescRamoReq='RAMO_A/', Orden=0, SIGLA=None),
            course(4, RamoReq='RAMO_A', DescRamoReq='ASIGNATURA SINTETICA', Orden=1, SIGLA=None),
            course(5, RamoEquiv='PLAN_A/RAMO_A', DescRamoEquiv='ASIGNATURA SINTETICA', Orden=2, SIGLA=None),
        ]
        result = M.build_catalog(rows)
        self.assertEqual(result['resumen']['asignaturas_plan_ramo_nivel'], 1)
        self.assertEqual(result['resumen']['filas_catalogo'], 4)
        self.assertTrue(result['resumen']['filas_conciliadas'])
        item = result['estructura_asignaturas'][0]
        self.assertEqual(item['filas_base'], [2])
        self.assertEqual(len(item['encabezados_relaciones']), 1)
        self.assertEqual([x['literal'] for x in item['requisitos_detalle']], ['RAMO_A'])
        self.assertEqual([x['literal'] for x in item['equivalencias_detalle']], ['PLAN_A/RAMO_A'])
        self.assertEqual(item['conflictos_atributos_curso'], {})
        self.assertEqual(item['filas_expansion'][0]['RamoReq'], '   ')

    def test_conflicting_academic_attributes_remain_visible(self):
        result = M.build_catalog([
            course(), course(3, HOR_TEO=30, RamoReq='RAMO_A', SIGLA=None, Orden=1),
        ])
        item = result['estructura_asignaturas'][0]
        self.assertEqual(item['conflictos_atributos_curso'], {'HOR_TEO': ['20', '30']})
        self.assertEqual(set(item['atributos_origen']['HOR_TEO']), {20, 30})
        self.assertEqual(item['filas_fuente'], [2, 3])
        self.assertNotIn('SIGLA', item['conflictos_atributos_curso'])
        self.assertEqual(result['catalogo_planes'][0]['grupos_con_conflicto_atributo_curso'], 1)

    def test_three_unlocated_equivalence_targets_are_preserved(self):
        # A reference is qualified by its explicit destination plan. The same
        # course code in another plan cannot repair a missing destination.
        rows = [course(), course(3, plan='PLAN_B', code='RAMO_B')]
        rows.extend(course(n, RamoEquiv='PLAN_B/' + target)
                    for n, target in enumerate(('AUSENTE_1', 'AUSENTE_2', 'AUSENTE_3'), 4))
        rows.extend([
            course(7, RamoEquiv='PLAN_B/RAMO_B'),
            course(8, plan='PLAN_OTRO', code='AUSENTE_1'),
        ])
        result = M.build_catalog(rows)
        self.assertEqual(result['resumen']['equivalencias_estado_destino'], {
            'RAMO_NO_OBSERVADO_EN_PLAN': 3, 'REFERENCIA_OBSERVADA': 1,
        })
        item = next(x for x in result['estructura_asignaturas'] if x['CODPESTUD'] == 'PLAN_A')
        missing = [x for x in item['equivalencias_detalle']
                   if x['estado_destino'] == 'RAMO_NO_OBSERVADO_EN_PLAN']
        self.assertEqual(len(missing), 3)
        self.assertEqual([x['filas_fuente'] for x in missing], [[4], [5], [6]])
        self.assertTrue(all(x['plan_destino'] == 'PLAN_B' for x in missing))
        self.assertTrue(all(x['version_sies_asignada'] is None for x in result['catalogo_planes']))

    def test_identical_structures_do_not_prove_temporal_succession(self):
        result = M.build_catalog([
            course(), course(3, plan='PLAN_B'),
            course(4, plan='PLAN_OTRA_CARRERA', Codcarr='OTRA_CARRERA'),
            course(5, plan='PLAN_OTRA_SEDE', Sede='OTRA_SEDE'),
        ])
        self.assertEqual(len(result['comparaciones_planes']), 1)
        pair = result['comparaciones_planes'][0]
        self.assertTrue(pair['mismos_ramos_niveles'])
        self.assertTrue(pair['mismos_atributos_curso'])
        self.assertTrue(pair['misma_estructura_con_relaciones'])
        self.assertFalse(pair['sucesion_temporal_acreditada'])
        self.assertTrue(all(x['fecha_vigencia_acreditada'] is None for x in result['catalogo_planes']))

    def test_multiple_contexts_are_preserved_without_first_row_selection(self):
        result = M.build_catalog([
            course(), course(3, code='RAMO_B', Codcarr='CARRERA_B', Sede='SEDE_B'),
            course(4, plan='PLAN_B'),
        ])
        plan = next(x for x in result['catalogo_planes'] if x['CODPESTUD'] == 'PLAN_A')
        self.assertEqual(plan['estado_contexto'], 'INCOMPLETO_O_MULTIPLE')
        self.assertEqual(plan['carreras_internas'], ['CARRERA_A', 'CARRERA_B'])
        self.assertEqual(plan['sedes'], ['SEDE_A', 'SEDE_B'])
        self.assertEqual(result['comparaciones_planes'], [])

    def test_incomplete_keys_and_unparsed_references_are_not_filled(self):
        result = M.build_catalog([
            course(plan='', code=''),
            course(3, RamoEquiv='PLAN_NO_OBSERVADO/RAMO_A'),
            course(4, RamoEquiv='PLAN_A/RAMO_A/OTRO'),
        ])
        self.assertEqual(result['resumen']['grupos_con_clave_incompleta'], 1)
        self.assertEqual(result['resumen']['equivalencias_estado_destino'], {
            'FORMATO_NO_DESGLOSADO': 1, 'PLAN_NO_OBSERVADO': 1,
        })
        malformed = next(rel for item in result['estructura_asignaturas']
                         for rel in item['equivalencias_detalle']
                         if rel['estado_destino'] == 'FORMATO_NO_DESGLOSADO')
        self.assertEqual(malformed['literal'], 'PLAN_A/RAMO_A/OTRO')
        self.assertIsNone(malformed['plan_destino'])
        self.assertIsNone(malformed['ramo_destino'])

    def test_output_is_deterministic_and_input_unchanged(self):
        rows = [course(), course(3, plan='PLAN_B'), course(4, RamoReq='RAMO_A')]
        original = deepcopy(rows)
        result = M.build_catalog(rows)
        self.assertEqual(rows, original)
        self.assertEqual(M.build_catalog(list(reversed(rows))), result)

    def test_missing_keys_and_invalid_locators_are_rejected(self):
        missing = course()
        del missing['CODRAMO']
        for rows in ([course(), course()], [missing], [course(row='2')], [course(row=True)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                M.build_catalog(rows)

    def test_empty_catalog_and_unobserved_plans_are_retained(self):
        empty = M.build_catalog([])
        self.assertEqual(empty['catalogo_planes'], [])
        self.assertEqual(empty['estructura_asignaturas'], [])
        self.assertEqual(empty['comparaciones_planes'], [])
        self.assertTrue(empty['resumen']['filas_conciliadas'])
        # No student activity is required to retain a catalog plan.
        catalog = M.build_catalog([course(plan='PLAN_SIN_ACTIVIDAD')])
        self.assertEqual(catalog['catalogo_planes'][0]['CODPESTUD'], 'PLAN_SIN_ACTIVIDAD')
        self.assertEqual(catalog['resumen']['planes'], 1)


if __name__ == '__main__':
    unittest.main()
