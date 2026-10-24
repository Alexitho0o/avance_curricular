"""Regressions for separated 2027 P1 communication and internal monitoring."""
from copy import deepcopy
from datetime import date
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import pandas as pd
from docx import Document
from docx.shared import Inches, Pt

from caracterizacion_financiamiento import (
    CODIGOS_FINANCIAMIENTO_G01Q19, DETALLES_FINANCIAMIENTO_G01Q19,
)
from caracterizacion_reportes_2027 import (
    build_email_report, build_internal_report, extract_ordered_document,
    ordered_document_text, percentage,
)


def context(eligible=3, responses=True):
    return {
        'year':2027, 'period':1, 'cutoff':date(2026,10,13),
        'counts':{'VIGENTES_ELEGIBLES':eligible},
        'participation':{'eligible':eligible,'complete':int(eligible > 0),
                         'incomplete':0,'not_started':max(0,eligible-1)},
        'source_flags':{'responses_available':responses},
        'jornadas':[{'jornada':'ONLINE','total':eligible}] if eligible else [],
        'sedes':[{'codigo':'RE','nombre':'Santiago','total':max(0,eligible-1),'known':True},
                 {'codigo':'PTG','nombre':'','total':1,'known':False}] if eligible else [],
        'categories':[{'categoria':'NEE','detalle':'Detalle gobernado','total':1},
                      {'categoria':'NEE','detalle':'Sin selección','total':0},
                      {'categoria':'Financiamiento','detalle':'Ingresos propios','total':1}],
        'financing':[{'codigo':code,'total':int(code==CODIGOS_FINANCIAMIENTO_G01Q19[0])}
                     for code in CODIGOS_FINANCIAMIENTO_G01Q19],
        'trajectory':{'candidates_before':eligible+2, 'first_entry':eligible,
                      'prior_trajectory':2,'technical_duplicates':1},
    }


def plan():
    return SimpleNamespace(
        counts={'VIGENTES_ELEGIBLES':3, 'VIGENTES_CON_TOKEN':1, 'VIGENTES_SIN_TOKEN':2,
                'CORREOS_VALIDOS_INCORPORACION':1, 'PENDIENTES_CORREO_INSTITUCIONAL':1,
                'PENDIENTES_FIRMA_PERSONAS':1,'PENDIENTES_FIRMA_FUERA_ELEGIBLES':1,
                'PENDIENTES_FIRMA_TAMBIEN_ELEGIBLES':0,'PENDIENTES_FIRMA_Y_CORREO':1,
                'VIGENTES_SIN_FIRMA':2,'MATRICULA_PERIODO':7},
        daily=pd.DataFrame([{'TOKEN':'not-real'}]), backlog=pd.DataFrame(), temporal=pd.DataFrame(),
        missing=pd.DataFrame({'PENDIENTE_FECHA':[False,True]}),
        pending_email=pd.DataFrame({'PENDIENTE_FECHA':[True]}), signature=pd.DataFrame([{},{}]),
        today=date(2026,10,13),window=(date(2026,10,9),date(2026,10,12)),
    )


class ReportSeparationTests(unittest.TestCase):
    def test_multiple_enrollment_notice_uses_approved_brief_wording(self):
        for count, expected in [
            (0, None),
            (1, 'A la fecha se detecta 1 conflicto de RUT matriculado en más de una carrera.'),
            (2, 'A la fecha se detectan 2 conflictos de RUT matriculado en más de una carrera.'),
        ]:
            with self.subTest(count=count):
                ctx = context()
                ctx['counts']['RUT_MULTIMATRICULA'] = count
                text = ordered_document_text(build_email_report(ctx))
                if expected:
                    self.assertEqual(text.count(expected), 1)
                    self.assertLess(text.index(expected), text.index('La matrícula vigente'))
                else:
                    self.assertNotIn('conflicto de RUT', text)
                    self.assertNotIn('conflictos de RUT', text)
                self.assertNotIn('matrícula elegible.', text)
                self.assertNotIn('Cada RUT se contabiliza una sola vez', text)
                self.assertNotIn('archivo de seguimiento adjunto', text)

    def test_email_opening_matches_user_template_with_current_values(self):
        ctx = context(307)
        ctx['counts'].update(NUEVOS_DIARIOS=21, NUEVOS_REZAGADOS=3,
                             ELIMINADOS_PERIODO=3, RUT_MULTIMATRICULA=2)
        ctx['participation'].update(complete=16, incomplete=2, not_started=289)
        intro = extract_ordered_document(build_email_report(ctx))[0]['text']
        self.assertEqual(intro,
            'Estimados/as:\n\nJunto con saludar, informo que se incorporaron 21 nuevos estudiantes. '
            'El total acumulado de eliminaciones es de 3 personas. '
            'A la fecha se detectan 2 conflictos de RUT matriculado en más de una carrera. '
            'La matrícula vigente del periodo asciende a 307 estudiantes para el periodo 1.\n\n'
            'En cuanto a la encuesta, el índice de respuesta es 5,2%. '
            'De 307 estudiantes vigentes, 16 ya respondieron, 289 aún no responden '
            'y 2 presentan respuesta incompleta.\n\nDetalle numérico:')

    def test_email_opening_uses_dynamic_zero_and_singular_counts(self):
        ctx = context()
        intro = extract_ordered_document(build_email_report(ctx))[0]['text']
        self.assertIn('se incorporaron 0 nuevos estudiantes.', intro)
        self.assertIn('eliminaciones es de 0 personas.', intro)
        ctx['counts'].update(NUEVOS_DIARIOS=1, ELIMINADOS_PERIODO=1)
        intro = extract_ordered_document(build_email_report(ctx))[0]['text']
        self.assertIn('se incorporó 1 nuevo estudiante.', intro)
        self.assertIn('eliminaciones es de 1 persona.', intro)

    def test_zero_denominator_never_becomes_hundred_percent(self):
        self.assertEqual(percentage(0,0),'No aplica')
        self.assertEqual(percentage(1,1),'100%')
        email=build_email_report(context(0))
        text=ordered_document_text(email)
        self.assertIn('índice de respuesta no aplica',text)
        self.assertNotIn('100%',text)
        self.assertNotIn('TOTAL ANTIGUOS',text)
        self.assertNotIn('Distribución por jornada',text)

    def test_one_jornada_distribution_and_no_old_window_column(self):
        doc=build_email_report(context())
        tables=extract_ordered_document(doc)
        distribution=[b for b in tables if b['type']=='table' and b['rows'][0][0]=='Jornada']
        self.assertEqual(len(distribution),1)
        text=ordered_document_text(doc)
        self.assertNotIn('DE LOS CUALES NUEVOS',text)
        self.assertNotIn('Nuevos:',text)
        self.assertNotIn('estudiantes elegibles de primer ingreso institucional',text)
        self.assertIn('estudiantes para el periodo 1.',text)
        self.assertIn('trayectoria académica previa',text)

    def test_financing_shown_exactly_once_and_all_eleven_kept(self):
        doc=build_email_report(context())
        text=ordered_document_text(doc)
        tables=[b['rows'] for b in extract_ordered_document(doc) if b['type']=='table']
        financing=[t for t in tables if t[0]==['Alternativa','Acumulado','Hoy']]
        self.assertEqual(len(financing),1)
        self.assertEqual(len(financing[0]),13)  # header + eleven + total
        for code in CODIGOS_FINANCIAMIENTO_G01Q19:
            label=DETALLES_FINANCIAMIENTO_G01Q19[code].split('[',1)[1].rsplit(']',1)[0]
            self.assertEqual(text.count(label),1)
        self.assertIn('Total de selecciones | 1',text)

    def test_financing_coverage_and_duplicates_remain_integrity_errors(self):
        ctx=context()
        ctx['financing'].pop()
        with self.assertRaisesRegex(ValueError,'Cobertura'):
            build_email_report(ctx)
        ctx=context()
        ctx['financing'].append(deepcopy(ctx['financing'][0]))
        with self.assertRaisesRegex(ValueError,'duplicadas'):
            build_email_report(ctx)

    def test_zero_and_duplicate_conditions_do_not_produce_empty_or_repeated_blocks(self):
        ctx=context()
        ctx['categories'].append(deepcopy(ctx['categories'][0]))
        text=ordered_document_text(build_email_report(ctx))
        self.assertEqual(text.count('Detalle gobernado'),1)
        self.assertIn('Sin selección | 0 | 0',text)
        ctx['categories']=[]
        text=ordered_document_text(build_email_report(ctx))
        self.assertNotIn('Condiciones reportadas',text)

    def test_unknown_sede_remains_visible_and_complete(self):
        doc=build_email_report(context())
        text=ordered_document_text(doc)
        self.assertIn('PTG · Sin denominación validada | 1',text)
        ctx=context()
        ctx['sedes'].pop()
        with self.assertRaisesRegex(ValueError,'sedes no concilia'):
            build_email_report(ctx)

    def test_all_three_governed_sedes_use_the_same_denominator(self):
        ctx=context()
        ctx['sedes']=[{'codigo':'RE','nombre':'Santiago','total':1,'known':True},
                      {'codigo':'CO','nombre':'Concepción','total':1,'known':True},
                      {'codigo':'PTG','nombre':'Patagonia','total':1,'known':True}]
        doc=build_email_report(ctx)
        table=next(b['rows'] for b in extract_ordered_document(doc)
                   if b['type']=='table' and b['rows'][0][0]=='Código y denominación')
        self.assertEqual(sum(int(row[1]) for row in table[1:]),3)
        self.assertEqual([row[0] for row in table[1:]],
                         ['RE · Santiago','CO · Concepción','PTG · Patagonia'])

    def test_response_state_and_distribution_denominators_must_match(self):
        ctx=context()
        ctx['participation']['complete']=2
        with self.assertRaisesRegex(ValueError,'estados de respuesta'):
            build_email_report(ctx)
        ctx=context()
        ctx['jornadas'][0]['total']=2
        with self.assertRaisesRegex(ValueError,'jornadas no concilia'):
            build_email_report(ctx)

    def test_email_excludes_internal_status_sources_and_operational_directions(self):
        ctx=context()
        ctx['sources']={'matricula':'/private/source.xlsx'}
        email=ordered_document_text(build_email_report(ctx))
        for internal in ['Estado de incorporación','LimeSurvey','Mail_Inst','CSV','Conciliaciones',
                         'firma pendiente','private/source.xlsx','ventana diaria','Sources']:
            self.assertNotIn(internal,email)
        internal=ordered_document_text(build_internal_report(ctx,plan()))
        self.assertIn('Estado de incorporación a LimeSurvey',internal)
        self.assertIn('Pendientes de firma',internal)
        self.assertIn('Conciliaciones',internal)
        self.assertIn('source.xlsx',internal)

    def test_no_responses_omits_survey_results_and_financing(self):
        ctx=context(responses=False)
        # No financing source is required before actual responses exist.
        ctx['financing']=[]
        text=ordered_document_text(build_email_report(ctx))
        self.assertIn('todavía no hay respuestas',text)
        self.assertNotIn('Alternativas de financiamiento',text)
        self.assertNotIn('Condiciones reportadas',text)
        self.assertNotIn('índice de respuesta completa',text)

    def test_internal_partitions_email_signature_and_dates_without_double_counting(self):
        text=ordered_document_text(build_internal_report(context(),plan()))
        self.assertIn('3 elegibles = 1 con token actual + 2 sin token actual.',text)
        self.assertIn('2 sin token actual = 1 con correo válido + 1 pendiente de correo.',text)
        self.assertIn('1 con correo válido = 1 diarios + 0 acumulados + 0 pendientes de fecha.',text)
        self.assertIn('Correo y fecha pendientes simultáneamente: 1 persona',text)
        self.assertIn('no se suman como personas distintas',text)
        self.assertIn('no se considera',text)
        self.assertNotIn('not-real',text)

    def test_internal_rejects_inconsistent_counts_and_trajectory(self):
        broken=plan()
        broken.counts['VIGENTES_ELEGIBLES']=4
        with self.assertRaisesRegex(ValueError,'no concilia'):
            build_internal_report(context(),broken)
        ctx=context()
        ctx['trajectory']['candidates_before']=9
        with self.assertRaisesRegex(ValueError,'trayectoria no concilia'):
            build_internal_report(ctx,plan())

    def test_ordered_extraction_interleaves_paragraphs_and_tables(self):
        doc=build_email_report(context())
        blocks=extract_ordered_document(doc)
        kinds=[b['type'] for b in blocks]
        self.assertTrue(blocks[0]['text'].startswith('Estimados/as:\n\nJunto con saludar, informo'))
        self.assertIn('table',kinds)
        first=kinds.index('table')
        self.assertEqual(blocks[first]['rows'][0],['CONCEPTO','TOTAL'])
        self.assertEqual(sum(b.get('text','').count('Estimados/as:') for b in blocks),1)

    def test_new_report_policy_never_touches_2026(self):
        ctx=context()
        ctx['year']=2026
        with self.assertRaisesRegex(ValueError,'exclusiva de 2027'):
            build_email_report(ctx)
        with self.assertRaisesRegex(ValueError,'exclusiva de 2027'):
            build_internal_report(ctx,plan())

    def test_retained_reference_remains_unchanged_and_its_styles_are_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            reference=Path(directory)/'reference.docx'
            original=Document()
            original.sections[0].left_margin=Inches(1.25)
            original.styles['Normal'].font.name='Calibri'
            original.styles['Normal'].font.size=Pt(11)
            original.styles['Normal'].paragraph_format.space_after=Pt(10)
            original.add_paragraph('Contenido histórico que no debe cambiar')
            original.save(reference)
            before=hashlib.sha256(reference.read_bytes()).hexdigest()
            ctx=context()
            ctx['reference_path']=reference
            report=build_email_report(ctx)
            self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(),before)
            self.assertEqual(report.styles['Normal'].font.name,'Calibri')
            self.assertEqual(report.styles['Normal'].font.size,Pt(11))
            self.assertEqual(report.styles['Normal'].paragraph_format.space_after,Pt(10))
            self.assertEqual(report.sections[0].left_margin,Inches(1.25))
            self.assertNotIn('Contenido histórico',ordered_document_text(report))

    def test_accumulated_and_today_are_restored_for_conditions_and_financing(self):
        ctx=context()
        ctx['categories'][0]['today']=1
        doc=build_email_report(ctx)
        tables=[b['rows'] for b in extract_ordered_document(doc) if b['type']=='table']
        conditions=next(t for t in tables if t[0]==['Categoría','Detalle','Acumulado','Hoy'])
        self.assertIn(['NEE','Detalle gobernado','1','1'],conditions)
        self.assertIn('no a la fecha de matrícula',ordered_document_text(doc))


if __name__=='__main__':
    unittest.main()
