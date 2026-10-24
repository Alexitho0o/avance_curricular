import ast
from contextlib import redirect_stdout
from datetime import date
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import caracterizacion_etiquetas_2027 as labels
from caracterizacion_financiamiento_2027 import adapted_source


class Label2027Tests(unittest.TestCase):
    def summary(self, use_window=True):
        return {'nombre_fila':'Financiamiento', 'total_fila':14,
                'de_los_cuales_nuevos':0,'antiguos':14,'sin_clasificar':0,
                'suma_nuevos_antiguos_sin_clasificar':14,'diferencia_vs_total':0,
                'conteo_fuera_de_ventana':14,'conteo_anio_ing_ori_distinto':0,
                'usar_ventana':use_window}

    def test_window_log_does_not_call_previous_dates_old_students(self):
        row = self.summary()
        message = labels.format_matricula_audit(row)
        self.assertIn('fuera_ventana=14', message)
        self.assertIn('COHORTE_Y_VENTANA_MATRICULA', message)
        self.assertNotIn('antiguos', message)
        self.assertNotIn('de_los_cuales_nuevos', message)
        self.assertEqual(row, self.summary())

    def test_cohort_log_identifies_different_control(self):
        self.assertIn('COHORTE_Y_FECHA_VALIDA', labels.format_matricula_audit(self.summary(False)))

    def test_audit_columns_are_precise_and_values_preserved(self):
        details = [{'RUT':'fixture', 'ES_NUEVO_COHORTE_OFICIAL':True,
                    'ES_NUEVO_EN_VENTANA':False, 'MOTIVO_CLASIFICACION':'ANTIGUO_ANIO_ING_ORI_DISTINTO'}]
        summary, detail = labels.matricula_audit_tables([self.summary()], details)
        self.assertNotIn('antiguos', summary)
        self.assertEqual(summary.iloc[0].no_cumplen_control_matricula,14)
        self.assertEqual(summary.iloc[0].suma_control_matricula,14)
        self.assertEqual(detail.iloc[0].MOTIVO_CLASIFICACION,'FUERA_COHORTE_ANIO_INGRESO')
        self.assertTrue(detail.iloc[0].CUMPLE_COHORTE_Y_FECHA_VALIDA)
        self.assertFalse(detail.iloc[0].CUMPLE_COHORTE_Y_VENTANA)
        self.assertIn('ES_NUEVO_COHORTE_OFICIAL',details[0])

    def test_response_lists_distinguish_all_pending_and_review(self):
        source = pd.DataFrame({'token':['1','2','3','4','5'],
                               'Responden':['SI','NO','INCOMPLETO',None,'UNKNOWN']}, index=[10,20,30,40,50])
        before = source.copy(deep=True)
        tracking, pending, counts = labels.response_tracking_frames(source)
        pd.testing.assert_frame_equal(source,before)
        pd.testing.assert_frame_equal(tracking,source)
        self.assertEqual(pending.index.tolist(),[20,30,40])
        self.assertEqual(counts['PENDIENTES_RESPUESTA'],3)
        self.assertEqual(counts['RESPUESTAS_COMPLETAS'],1)
        self.assertEqual(counts['ESTADOS_POR_REVISAR'],1)
        self.assertEqual(counts['ELEGIBLES_TOTALES'],5)

    def test_normalized_complete_answers_are_excluded_without_changing_source(self):
        source = pd.DataFrame({'Responden':[' sí ', 'No', 'incompleto']})
        _, pending, counts = labels.response_tracking_frames(source)
        self.assertEqual(pending.Responden.tolist(),['No','incompleto'])
        self.assertEqual(counts['RESPUESTAS_COMPLETAS'],1)

    def test_empty_or_all_complete_has_no_pending_file(self):
        for source in [pd.DataFrame({'Responden':pd.Series(dtype=str)}),pd.DataFrame({'Responden':['SI']})]:
            with tempfile.TemporaryDirectory() as temp:
                writes = []
                def writer(frame, name, sheet, title):
                    writes.append((frame.copy(),name,sheet,title))
                    return Path(temp)/name
                with patch.object(labels.rt,'output_path',side_effect=lambda name,**kw:Path(temp)/name),redirect_stdout(StringIO()):
                    record = labels.publish_response_tracking(source,'20261013',writer)
                self.assertEqual(len(writes),1)
                self.assertNotIn('pendientes_respuesta',record['outputs'])
                self.assertTrue(writes[0][1].startswith('Seguimiento_respuestas_encuesta_'))

    def test_no_responses_both_lists_preserve_all_students(self):
        tracking, pending, counts=labels.response_tracking_frames(pd.DataFrame({'Responden':['NO','NO']}))
        pd.testing.assert_frame_equal(tracking,pending)
        self.assertEqual(counts['PENDIENTES_RESPUESTA'],2)

    def test_publish_separates_files_counts_and_writes_no_identifiers_to_audit(self):
        source=pd.DataFrame({'RUT':['private_a','private_b','private_c'], 'Responden':['SI','NO','INCOMPLETO']})
        with tempfile.TemporaryDirectory() as temp:
            writes=[]
            def writer(frame,name,sheet,title):
                writes.append((name,frame.copy(),sheet,title))
                return Path(temp)/name
            with patch.object(labels.rt,'output_path',side_effect=lambda name,**kw:Path(temp)/name),redirect_stdout(StringIO()):
                record=labels.publish_response_tracking(source,'20261013',writer)
            self.assertEqual(len(writes),2)
            self.assertEqual(len(writes[0][1]),3)
            self.assertEqual(len(writes[1][1]),2)
            self.assertFalse(writes[1][1].Responden.eq('SI').any())
            self.assertTrue(writes[1][0].startswith('Estudiantes_pendientes_respuesta_'))
            saved=json.loads(next(Path(temp).glob('*.json')).read_text())
            self.assertEqual(saved['counts'],record['counts'])
            self.assertNotIn('private_a',json.dumps(saved))

    def test_missing_response_column_blocks(self):
        with self.assertRaises(ValueError):
            labels.response_tracking_frames(pd.DataFrame({'unrelated':[]}))

    def test_adapter_only_replaces_2027_labels_and_exports(self):
        reference=Path(__file__).resolve().parents[1]/'caracterizacion.py'
        before=reference.read_bytes()
        source=adapted_source(before.decode())
        compile(source,'adapter-labels','exec')
        self.assertEqual(reference.read_bytes(),before)
        self.assertNotIn('[AUDIT B4 PENDIENTES]',source)
        self.assertNotIn('nombre_export = f"Estudiantes_pendientes_{ANIO_ANALISIS}',source)
        self.assertNotIn('f"antiguos={antiguos}',source)
        self.assertIn('export_response_tracking(globals())',source)
        with self.assertRaisesRegex(ValueError,'Ancla'):
            adapted_source(before.decode().replace('def _segmentar_nombre_fallback(', 'def _changed('))

    def test_temporal_audit_computations_remain_identical(self):
        reference=Path(__file__).resolve().parents[1]/'caracterizacion.py'
        source=reference.read_text()
        frames=pd.DataFrame({'RUT':['fixture']*14})
        def run(text):
            node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)
                      and n.name=='_registrar_auditoria_nuevos_informe')
            namespace={'pd':pd,'date':date,'ANIO_ANALISIS':2027,'PERIODO_ANALISIS':1,
                'VENTANA_INICIO_INFORME':date(2026,10,9),'VENTANA_FIN_INFORME':date(2026,10,12),
                'FECHA_REFERENCIA_PROCESO':date(2026,10,13),'FUENTE_FECHA_REFERENCIA':'TEST',
                'AUDIT_NUEVOS_DETALLE':[],'AUDIT_NUEVOS_RESUMEN':[], 'IDX_RUT':0,'IDX_ESTADO':0,
                'token_match_rut':str,'_normalizar_clave_limesurvey':str,
                '_audit_id':lambda *args:'fixture',
                'es_nuevo_mu2026':lambda row,year,**kw:{'es_nuevo':not kw['usar_ventana'],
                    'motivo':'FUERA_DE_VENTANA' if kw['usar_ventana'] else 'NUEVO',
                    'fecha_motivo':'FECHA_OK','fecha_parseada':date(2026,10,8),'anio_ing_ori':2027}}
            exec(compile(ast.Module(body=[node],type_ignores=[]),'audit-function','exec'),namespace)
            stream=StringIO()
            with redirect_stdout(stream):
                result=namespace['_registrar_auditoria_nuevos_informe']('Financiamiento',frames,usar_ventana=True)
            return result,namespace['AUDIT_NUEVOS_DETALLE'],stream.getvalue()
        original=run(source)
        adapted=run(adapted_source(source))
        self.assertEqual(original[0],adapted[0])
        self.assertEqual(original[1],adapted[1])
        self.assertIn('antiguos=14',original[2])
        self.assertIn('fuera_ventana=14',adapted[2])
        self.assertNotIn('antiguos=',adapted[2])


if __name__=='__main__':
    unittest.main()
