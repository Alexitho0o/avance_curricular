from datetime import date
import unittest
import pandas as pd

from caracterizacion_seguimiento_opciones_2027 import (
    monitoring_definitions, positive_value, compute_followup, workbook_payload, column_code,
    COMPANY_RESPONSE_FIELD, COMPANY_STATUS_FIELD, company_name_context)


class OptionFollowupTests(unittest.TestCase):
    def target(self, tokens=('1',)):
        return pd.DataFrame({'TOKEN':list(tokens),'RUT':[v+'-1' for v in tokens],
            'NOMBRE':['Fixture']*len(tokens),'NOMBRE_L':['Carrera']*len(tokens),
            'Mail_Inst':['fixture@example.invalid']*len(tokens),'FECHAMATRICULA':['13-10-2026']*len(tokens)})

    def definition(self, code):
        return next(d for d in monitoring_definitions() if d['column'].upper()==code.upper())

    def test_current_catalog_excludes_removed_questions_and_identifies_vcm_answer(self):
        defs=monitoring_definitions()
        self.assertEqual(len(defs),33)
        self.assertTrue({'G01Q31','G06Q66','G01Q06'}.isdisjoint({d['column'] for d in defs}))
        option=self.definition('G02Q95')
        self.assertEqual(option['answer_code'],'AO05')
        self.assertEqual(option['id'],'G02Q95::AO05')
        self.assertEqual(option['rule'],'answer')

    def test_severity_options_are_not_treated_as_yes_no(self):
        item=self.definition('G01Q17[SQ001]')
        for value in ['Leve','Moderada','Severa','AO01','AO02','AO03']:
            self.assertTrue(positive_value(value,item))
        for value in ['No presento esta discapacidad','AO04',None,'']:
            self.assertFalse(positive_value(value,item))
        with self.assertRaises(ValueError): positive_value('unknown',item)

    def test_vcm_only_selected_option_counts_other_employment_is_not_negative_evidence(self):
        item=self.definition('G02Q95')
        for value in ['AO05','Tengo un emprendimiento formalizado']:
            self.assertTrue(positive_value(value,item))
        for value in ['AO01','AO02','AO03','AO04',None]:
            self.assertFalse(positive_value(value,item))
        with self.assertRaises(ValueError): positive_value('AO99',item)

    def test_today_uses_submitdate_not_enrollment_or_last_action(self):
        source=pd.DataFrame({'token':['1','2'],'submitdate':['2026-10-12 10:00:00','2026-10-13 09:00:00'],
            'datestamp':['2026-10-13 11:00:00','2026-10-13 12:00:00'], 'G02Q95':['AO05','AO05']})
        result=compute_followup(self.target(('1','2')),source,date(2026,10,13))
        metric=next(m for m in result['metrics'] if m['column']=='G02Q95')
        self.assertEqual((metric['total'],metric['today']),(2,1))
        self.assertEqual(len(result['vcm']),2)
        self.assertEqual(result['vcm'].RESPONDIO_HOY.tolist(),[0,1])

    def test_timezone_offsets_are_converted_to_santiago(self):
        source=pd.DataFrame({'token':['1'],'submitdate':['2026-10-14T02:30:00+00:00'],'G02Q95':['AO05']})
        result=compute_followup(self.target(),source,date(2026,10,13))
        self.assertEqual(next(m for m in result['metrics'] if m['column']=='G02Q95')['today'],1)
        self.assertEqual(result['raw'].iloc[0].FECHA_ENVIO,'2026-10-13T23:30:00')
        self.assertEqual(result['raw'].iloc[0].SUBMITDATE_ORIGINAL,'2026-10-14T02:30:00+00:00')

    def test_partial_without_submitdate_keeps_selection_but_is_not_today(self):
        source=pd.DataFrame({'token':['1'],'submitdate':[None],'datestamp':['2026-10-13 10:00:00'],'G02Q95':['AO05']})
        result=compute_followup(self.target(),source,date(2026,10,13))
        self.assertEqual(next(m for m in result['metrics'] if m['column']=='G02Q95')['today'],0)
        self.assertIsNone(result['vcm'].iloc[0].FECHA_ENVIO)

    def test_outside_target_is_not_counted_and_duplicate_canonical_tokens_block(self):
        source=pd.DataFrame({'token':['outside'],'submitdate':['2026-10-13'],'G02Q95':['AO05']})
        result=compute_followup(self.target(),source,date(2026,10,13))
        self.assertEqual(next(m for m in result['metrics'] if m['column']=='G02Q95')['total'],0)
        with self.assertRaisesRegex(ValueError,'canonicas'):
            compute_followup(self.target(),pd.DataFrame({'token':['1','1'],'submitdate':['2026-10-13']*2}),date(2026,10,13))

    def test_missing_column_is_not_reported_as_zero(self):
        result=compute_followup(self.target(),pd.DataFrame({'token':['1'],'submitdate':['2026-10-13']}),date(2026,10,13))
        metric=next(m for m in result['metrics'] if m['column']=='G02Q95')
        self.assertIsNone(metric['total'])
        self.assertEqual(metric['state'],'COLUMNA_AUSENTE')
        self.assertEqual(len(result['changes']),36)

    def test_headers_do_not_confuse_question_timing_with_question_value(self):
        self.assertEqual(column_code('G02Q95. Texto'),'G02Q95')
        self.assertIsNone(column_code('G02Q95Time. Temporizacion'))
        self.assertEqual(column_code('G01Q65[other]'),'G01Q65[OTHER]')

    def test_workbooks_keep_raw_answers_codes_and_separate_vcm(self):
        source=pd.DataFrame({'token':['1'],'submitdate':['2026-10-13'],'G02Q95':['AO05']})
        result=compute_followup(self.target(),source,date(2026,10,13))
        before=source.copy(deep=True)
        categories=workbook_payload(result)
        vcm=workbook_payload(result,True)
        pd.testing.assert_frame_equal(source,before)
        self.assertEqual([s['name'] for s in categories['sheets']],['Resumen','Detalle','Respuestas fuente','Mapa 2027'])
        self.assertEqual([s['name'] for s in vcm['sheets']],['Resumen','Emprendimientos','Respuestas fuente'])
        self.assertEqual(len(vcm['sheets'][0]['rows']),1)
        self.assertEqual(vcm['sheets'][0]['rows'][0][2:4],['G02Q95','AO05'])
        for payload in (categories,vcm):
            raw=next(s for s in payload['sheets'] if s['name']=='Respuestas fuente')
            self.assertEqual(raw['headers'][:3],['TOKEN','SUBMITDATE_ORIGINAL','FECHA_ENVIO'])
            self.assertEqual(raw['date_columns'],[2])
            self.assertEqual(raw['rows'][0][1],'2026-10-13')

    def test_future_response_dates_do_not_silently_enter_historical_cut(self):
        with self.assertRaisesRegex(ValueError,'posteriores'):
            compute_followup(self.target(),pd.DataFrame({'token':['1'],'submitdate':['2026-10-14'],'G02Q95':['AO05']}),date(2026,10,13))

    def test_employer_is_never_relabelled_as_confirmed_venture_name(self):
        source=pd.DataFrame({'token':['1','2'],'submitdate':['2026-10-13']*2,
            'G02Q95':['AO01','AO05'], 'G02Q27':['  Empresa declarada  ','Respuesta mixta'],
            'G01Q82':['Si','No']})
        before=source.copy(deep=True)
        result=compute_followup(self.target(('1','2')),source,date(2026,10,13))
        self.assertNotIn('NOMBRE_EMPRENDIMIENTO',result['detail'])
        self.assertEqual(result['detail'].set_index('TOKEN').loc['1',COMPANY_RESPONSE_FIELD],'  Empresa declarada  ')
        self.assertEqual(result['vcm'][COMPANY_RESPONSE_FIELD].tolist(),['Respuesta mixta'])
        self.assertEqual(result['vcm'][COMPANY_STATUS_FIELD].tolist(),['NO_CONFIRMADO_PREGUNTA_MIXTA'])
        self.assertEqual(result['raw']['G02Q27'].tolist(),source['G02Q27'].tolist())
        pd.testing.assert_frame_equal(source,before)

    def test_blank_name_and_missing_column_are_distinct_and_do_not_drop_vcm(self):
        for value in [None,'','  ','N/A']:
            with self.subTest(value=value):
                source=pd.DataFrame({'token':['1'],'submitdate':['2026-10-13'],
                    'G02Q95':['AO05'],'G02Q27':[value]})
                result=compute_followup(self.target(),source,date(2026,10,13))
                self.assertEqual(result['vcm_name_status_counts'],{'SIN_RESPUESTA_G02Q27':1})
                self.assertEqual(result['vcm'].RESPONDIO_HOY.tolist(),[1])
                without=compute_followup(self.target(),source.drop(columns='G02Q27'),date(2026,10,13))
                self.assertEqual(without['vcm_name_status_counts'],{'COLUMNA_AUSENTE':1})

    def test_company_source_is_exact_question_not_timing_or_administrative_employer(self):
        target=self.target()
        target['NOMBREEMPRESA']='Dato administrativo ajeno'
        source=pd.DataFrame({'token':['1'],'submitdate':['2026-10-13'],'G02Q95':['AO05'],
            'G02Q27Time. Tiempo':['123'], 'G02Q27. Pregunta mixta':['Respuesta literal']})
        result=compute_followup(target,source,date(2026,10,13))
        self.assertEqual(result['vcm'][COMPANY_RESPONSE_FIELD].tolist(),['Respuesta literal'])
        without=compute_followup(target,source.drop(columns='G02Q27. Pregunta mixta'),date(2026,10,13))
        self.assertTrue(without['vcm'][COMPANY_RESPONSE_FIELD].isna().all())

    def test_vcm_raw_retains_mixed_question_and_explains_unconfirmed_name(self):
        source=pd.DataFrame({'token':['1'],'submitdate':['2026-10-13'],
            'G02Q95':['AO05'],'G02Q27':['Literal']})
        result=compute_followup(self.target(),source,date(2026,10,13))
        payload=workbook_payload(result,True)
        raw=next(s for s in payload['sheets'] if s['name']=='Respuestas fuente')
        self.assertEqual(raw['headers'][-1],'G02Q27')
        self.assertEqual(raw['rows'][0][-1],'Literal')
        self.assertIn('no confirma',raw['source_notes'][1])
        self.assertEqual(payload['sheets'][1]['headers'][7],'ID_SEGUIMIENTO')
        self.assertEqual(payload['sheets'][1]['headers'][15],'RESPONDIO_HOY')

    def test_archived_mixed_question_is_institutional_and_excludes_ao05(self):
        from scripts.gobernanza.auditar_grupos_fcu_2027 import question_origins
        context=company_name_context()
        self.assertEqual(question_origins()['G02Q27'],'INSTITUCIONAL')
        self.assertEqual(context['type'],'S')
        self.assertIn('empresa',context['question'])
        self.assertIn('emprendimiento',context['question'])
        self.assertIn('AO01',context['relevance'])
        self.assertIn('AO02',context['relevance'])
        self.assertNotIn('AO05',context['relevance'])
        self.assertFalse(context['confirms_business_name'])

    def test_governed_name_contract_matches_exported_semantics(self):
        import json
        from caracterizacion_seguimiento_opciones_2027 import ROOT
        path=ROOT/'gobernanza/FCU/2027/preparacion/json/PREGUNTAS_INSTITUCIONALES_2027.json'
        rule=json.loads(path.read_text())['company_name_followup']
        context=company_name_context()
        self.assertEqual(rule['limesurvey_code'],context['code'])
        self.assertEqual(rule['text'],context['question'])
        self.assertEqual(rule['observed_relevance'],context['relevance'])
        self.assertEqual(rule['output_field'],COMPANY_RESPONSE_FIELD)
        self.assertEqual(rule['status_field'],COMPANY_STATUS_FIELD)


if __name__=='__main__': unittest.main()
