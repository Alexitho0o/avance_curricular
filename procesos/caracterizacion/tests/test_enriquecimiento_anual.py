"""Synthetic annual-only checks; no execution of periods or desktop deliveries."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import enriquecer_analisis_anual as enrichment
import consolidar_analisis_anual as annual
import ejecutar_analisis_anual as runner
from test_analisis_anual_integrado import fixture


def policy():
    return json.loads(enrichment.POLICY_PATH.read_text(encoding='utf-8'))


def catalog():
    return {'anio': 2026, 'version': 'synthetic', 'sedes_internas': {'RE': '2'}, 'oferta': [
        {'codigo_unico': f'I162S2C1J4V{version}', 'sede': '2', 'jornada': '4',
         'modalidad': 'No presencial', 'modalidad_codigo': '3',
         'equivalencias': [{'codcarpr': 'CADMP'}]} for version in (1, 2)]}


def grade_frame():
    return pd.DataFrame([
        ['A','CADMP','2025','1','OLD','1','7','APROBADO','N'],
        ['A','CADMP','2026','1','X','1','4','APROBADO','N'],
        ['A','CADMP','2026','1','X','1','4','APROBADO','N'],
        ['A','CADMP','2026','2','Y','1','7','APROBADO','N'],
        ['A','CADMP','2026','2','Z','1','7','APROBADO','N'],
        ['A','CADMP','2026','3','W','1','2','REPROBADO','N'],
        ['B','CADMP','2026','1','X','1','6','HOMOLOGADO','N'],
        ['B','CADMP','2026','1','Y','1','6','APROBADO','S'],
        ['B','CADMP','2026','1','Z','1','0','REPROBADO','N'],
        ['B','CADMP','2026','1','W','1','8','APROBADO','N'],
        ['B','CADMP','2026','1','V','1','','REPROBADO','N'],
        ['C','CADMP','2026','1','X','1','4','APROBADO','N'],
        ['C','CADMP','2026','1','X','1','6','APROBADO','N'],
        ['D','CADMP','2026','1','X','1','5,5','APROBADO','N'],
        ['D','CADMP','2027','1','Y','1','7','APROBADO','N'],
        ['D','CADMP','2026','4','Z','1','7','APROBADO','N'],
    ], columns=['CODCLI','CODCARR','ANO','PERIODO','CODRAMO','CODSECC',
                'NOTA_FINAL','DESCRIPCION_ESTADO','CONVALIDADO'])


class AnnualEnrichmentTests(unittest.TestCase):
    def test_collect_period_enriches_in_memory_and_preserves_archived_base(self):
        part=fixture()[0]
        base=part['base'].copy()
        base['CODCARPR']='CADMP'
        base['CARRERA']='CONTINUIDAD INGENIERIA ADMINISTRACION PUBLICA'
        base['SECTOR_ACADEMICO']='Sin clasificar'
        base.loc[0,'CODCLI']='A'
        before=base.copy(deep=True)
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            (directory/'02_SALIDAS').mkdir()
            source=directory/'02_SALIDAS/test_ANALISIS_SECTORIZADO_AC.xlsx'
            source.write_bytes(b'archived synthetic base')
            grades=directory/'grades.xlsx'
            grades.write_bytes(b'archived synthetic grades')
            entry={**part['entry'],'snapshot_sources':{'RUTA_RESULTADOS':str(source),'RUTA_PROMEDIOS':str(grades)},
                   'source_hashes':{'RUTA_RESULTADOS':annual.sha(source),'RUTA_PROMEDIOS':annual.sha(grades)}}
            with patch.object(annual,'read_base',return_value=base), \
                 patch.object(annual.pd,'read_excel',side_effect=[part['results'],grade_frame()]), \
                 patch.object(enrichment,'shared_inventory',return_value=part['inventory']):
                result=annual.collect_period(entry,directory)
            self.assertEqual(result['base'].iloc[0]['PROMEDIO_AC_REFERENCIA'],5)
            self.assertEqual(result['base'].iloc[0]['SECTOR_ACADEMICO'],'Administración y Comercio')
            self.assertTrue(result['comparability'].startswith('Comparable'))
            self.assertEqual(len(result['enrichment_audit']),len(base))
            self.assertEqual(source.read_bytes(),b'archived synthetic base')
            pd.testing.assert_frame_equal(base,before)

    def test_portable_sources_are_pinned_and_2026(self):
        rules, source, inventory = enrichment.load_resources()
        self.assertEqual(source['anio'],2026)
        self.assertEqual(source['version'],'mu2026_20261013')
        self.assertEqual(enrichment.digest(inventory),rules['instrumento']['sha256'])
        with self.assertRaisesRegex(ValueError,'alterada'):
            enrichment.verified_resource({'path':rules['catalogo']['path'],'sha256':'wrong'})

    def test_shared_modality_does_not_choose_a_version(self):
        result = enrichment.resolve_modality({'CODCARPR':'CADMP','SEDE':'RE','JORNADA':'O'},catalog())
        self.assertEqual(result[0],'No presencial')
        self.assertEqual(result[1],'AMBIGUO')
        self.assertEqual(len(result[2]),2)
        self.assertEqual(result[3],'COINCIDENCIA_CANDIDATOS')

    def test_different_modalities_are_not_guessed(self):
        source = catalog()
        source['oferta'][1].update(modalidad='Presencial',modalidad_codigo='1')
        result = enrichment.resolve_modality({'CODCARPR':'CADMP','SEDE':'RE','JORNADA':'O'},source)
        self.assertEqual(result[0],'No determinada')
        self.assertEqual(result[3],'MODALIDADES_DIFERENTES')

    def test_missing_keys_or_sp_never_imply_modality(self):
        for row in [{'CODCARPR':'TFARSP','SEDE':'RE','JORNADA':'V','MODALIDAD':'SEMIPRESENCIAL'},
                    {'CODCARPR':'CADMP','SEDE':'RE'}]:
            self.assertEqual(enrichment.resolve_modality(row,catalog())[0],'No determinada')

    def test_corrupt_modality_is_an_integrity_error(self):
        source=catalog()
        source['oferta'][0]['modalidad']='Presencial'
        with self.assertRaisesRegex(ValueError,'contradictoria'):
            enrichment.resolve_modality({'CODCARPR':'CADMP','SEDE':'RE','JORNADA':'O'},source)

    def test_explicit_v_policy_keeps_sies_candidates_and_disagreement(self):
        source = catalog()
        for candidate in source['oferta']:
            candidate.update(jornada='2', modalidad='Semipresencial', modalidad_codigo='2')
        base = fixture()[0]['base'].iloc[1:2].copy()
        base['CODCARPR'] = 'CADMP'
        base['JORNADA'] = ' v '
        before = base.copy(deep=True)
        result, audit = enrichment.enrich_base(base, {'anio':2026,'periodo':1}, source, policy(), {})
        self.assertEqual(result.iloc[0]['MODALIDAD_CARRERA'], 'Presencial')
        self.assertIn('REGLA_INSTITUCIONAL', result.iloc[0]['FUENTE_MODALIDAD_ANUAL'])
        self.assertEqual(audit[0][6], 'AMBIGUO')
        self.assertEqual(audit[0][14:], ['Semipresencial', 'COINCIDENCIA_CANDIDATOS', 'SI'])
        pd.testing.assert_frame_equal(base, before)

    def test_v_without_equivalence_is_presencial_but_never_invents_sies_code(self):
        row = {'CODCARPR':'UNKNOWN','SEDE':'RE','JORNADA':'V'}
        original = enrichment.resolve_modality(row, catalog())
        result = enrichment.apply_modality_policy(row, original, policy())
        self.assertEqual(result, ('Presencial', 'SIN_EQUIVALENCIA', [], 'REGLA_INSTITUCIONAL_JORNADA_V'))
        for jornada in ['D', 'O', '', '2']:
            self.assertEqual(enrichment.apply_modality_policy({'JORNADA':jornada}, original, policy()), original)

    def test_grades_use_current_year_valid_attempts_not_mean_of_means(self):
        raw=grade_frame()
        before=raw.copy(deep=True)
        metrics, quality, periods=enrichment.academic_metrics(raw,policy())
        self.assertEqual(metrics[('A','CADMP')],{'mean':5.0,'n':4,'periods':'1, 2, 3'})
        self.assertEqual(metrics[('D','CADMP')]['mean'],5.5)
        self.assertNotIn(('B','CADMP'),metrics)
        self.assertNotIn(('C','CADMP'),metrics)
        self.assertEqual(dict(quality)['Duplicados exactos colapsados'],1)
        self.assertEqual(dict(quality)['Filas de intentos contradictorios excluidas'],2)
        self.assertEqual(periods,['1','2','3'])
        pd.testing.assert_frame_equal(raw,before)

    def test_missing_grades_are_not_zero_and_other_career_is_not_used(self):
        base=fixture()[0]['base'].iloc[:1].copy()
        base['CODCLI']='A'
        base['CODCARPR']='TFARSP'
        base['CARRERA']='TECNICO EN FARMACIA SP'
        base['SECTOR_ACADEMICO']='Sin clasificar'
        base['PROMEDIO_AC_REFERENCIA']=6.1
        metrics,_,_=enrichment.academic_metrics(grade_frame(),policy())
        before=base.copy(deep=True)
        result,audit=enrichment.enrich_base(base,{'anio':2026,'periodo':3},catalog(),policy(),metrics)
        self.assertTrue(pd.isna(result.iloc[0]['PROMEDIO_AC_REFERENCIA']))
        self.assertEqual(result.iloc[0]['SECTOR_ACADEMICO'],'Salud')
        self.assertEqual(result.iloc[0]['MODALIDAD_CARRERA'],'No determinada')
        self.assertEqual(audit[0][9],6.1)
        self.assertEqual(audit[0][11],0)
        pd.testing.assert_frame_equal(base,before)

    def test_explicit_sector_alias_is_scoped_to_code_and_name(self):
        base=fixture()[0]['base'].iloc[:1].copy()
        base['CODCARPR']='CADMP'
        base['CARRERA']='CONTINUIDAD  INGENIERIA ADMINISTRACION PUBLICA'
        base['SECTOR_ACADEMICO']='Sin clasificar'
        result,_=enrichment.enrich_base(base,{'anio':2026,'periodo':1},catalog(),policy(),{})
        self.assertEqual(result.iloc[0]['SECTOR_ACADEMICO'],'Administración y Comercio')
        base['CARRERA']='OTRO NOMBRE'
        result,_=enrichment.enrich_base(base,{'anio':2026,'periodo':1},catalog(),policy(),{})
        self.assertEqual(result.iloc[0]['SECTOR_ACADEMICO'],'Sin clasificar')
        with self.assertRaisesRegex(ValueError,'otro ano'):
            enrichment.enrich_base(base,{'anio':2027,'periodo':1},catalog(),policy(),{})

    def test_same_headers_use_authorized_inventory_and_changed_headers_block(self):
        headers=['id. ID','G01Q19[SQ001]. Financiamiento [Beca]']
        rules=deepcopy(policy())
        rules['instrumento'].pop('columnas_path')
        size,signature=enrichment.question_signature(headers)
        rules['instrumento'].update(columnas=size,encabezados_sha256=signature)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'inventory.json'
            path.write_text(json.dumps({'instrument':{'survey_id':'443299','groups':[
                {'text':'FAMILIARES','questions':[{'code':'G01Q19','type':'M'}]}]}}))
            for period,sid in [(1,'923565'),(2,'443299'),(3,'967488')]:
                result=enrichment.shared_inventory({'anio':2026,'periodo':period,'survey_id':sid},headers,rules,path)
                self.assertEqual(result['G01Q19']['type'],'M')
                self.assertEqual(result['G01Q19']['group'],'FAMILIARES')
            with self.assertRaisesRegex(ValueError,'Cambio el instrumento'):
                enrichment.shared_inventory({'anio':2026,'periodo':1,'survey_id':'923565'},headers+['G01Q20. Nueva'],rules,path)
            with self.assertRaisesRegex(ValueError,'fuera'):
                enrichment.shared_inventory({'anio':2027,'periodo':1,'survey_id':'141234'},headers,rules,path)

    def test_shared_signature_is_order_independent_not_text_independent(self):
        headers=['G01Q01. Uno','G01Q02[SQ001]. Dos']
        self.assertEqual(enrichment.question_signature(headers),enrichment.question_signature(headers[::-1]))
        self.assertNotEqual(enrichment.question_signature(headers),enrichment.question_signature(['G01Q01. Otro',headers[1]]))

    def test_production_preflight_accepts_governed_code_only_not_changed_text(self):
        rules=policy()
        pairs=json.loads((ROOT/rules['instrumento']['columnas_path']).read_text())
        runner.verify_annual_instrument([code for code,label in pairs])
        runner.verify_annual_instrument([code+'. '+label for code,label in pairs])
        with self.assertRaisesRegex(ValueError,'Cambio el instrumento'):
            runner.verify_annual_instrument([code+'. cambiado' for code,label in pairs])
        with self.assertRaisesRegex(ValueError,'Cambio el instrumento'):
            runner.verify_annual_instrument([code for code,label in pairs[:-1]])

    def test_participation_has_explicit_cross_dimensions_and_unique_people(self):
        model=annual.prepare(fixture())
        payload=annual.make_payload(model)
        table=next(s for s in payload['main'] if s['name']=='Participación')
        self.assertEqual(table['headers'][7:],['Período','Sector IPSS','Modalidad'])
        checks={(s,c):v for s,c,v in payload['expected_cells']}
        row=next(i+7 for i,r in enumerate(table['rows']) if r[0]=='Cruce' and r[7:]==['P1','Salud','Presencial'])
        self.assertEqual(checks['Participación',f'C{row}'],2)
        self.assertEqual(checks['Participación',f'D{row}'],1)
        empty=payload['filter_tests'][-1]
        self.assertTrue(all(v==0 for s,c,v in empty['expected_cells'] if s=='Participación' and c.startswith('C')))

    def test_comparability_is_recorded_not_replaced_with_constant(self):
        parts=fixture()
        for p in parts:
            p['comparability']='Comparable 2026 autorizado'
        model=annual.prepare(parts)
        self.assertTrue(all(row[6]=='Comparable 2026 autorizado' for row in model['dictionary']))


if __name__ == '__main__':
    unittest.main()
