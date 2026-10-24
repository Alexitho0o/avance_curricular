from contextlib import contextmanager
from datetime import date
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

import pandas as pd

import caracterizacion_runtime as rt
from caracterizacion_financiamiento_2027 import adapted_source
from caracterizacion_salidas_2027 import publish_eliminated_window


class ConditionalOutputTests(unittest.TestCase):
    @contextmanager
    def context(self,year=2027,period=1):
        old=rt.ACTIVE_CONTEXT;rt.ACTIVE_CONTEXT=None
        try:
            with tempfile.TemporaryDirectory() as temp,patch.dict(os.environ,{'CARACTERIZACION_RUN_DIR':temp}):
                ctx=rt.prepare_run_context(year,period,external_tee=True)
                yield ctx
                ctx._finalized=True
        finally:rt.ACTIVE_CONTEXT=old

    def namespace(self,frame):
        writer=Mock(side_effect=lambda data,path,**kwargs:Path(path).touch())
        return {'df_actualmente_eliminados_matriculados_en_ventana':frame,
            'n_actualmente_eliminados_matriculados_en_ventana':len(frame),
            'hoy_str':'20261013','desde_b3':date(2026,10,9),'hasta_b3':date(2026,10,12),
            'exportar_excel':writer}

    def test_zero_cases_does_not_call_exporter_or_create_file(self):
        with self.context() as ctx:
            namespace=self.namespace(pd.DataFrame(columns=['RUT','SEDE']))
            messages=io.StringIO()
            with patch('sys.stdout',messages):
                result=publish_eliminated_window(namespace)
            self.assertIsNone(result)
            namespace['exportar_excel'].assert_not_called()
            self.assertFalse(list(ctx.output_dir.glob('Actualmente_eliminados*')))
            manifest=rt.manifest_dict(ctx,namespace)
            decision=manifest['decisiones_salidas_condicionales'][0]
            self.assertEqual((decision['estado'],decision['filas']),('OMITIDO_SIN_CASOS',0))
            self.assertEqual(decision['motivo'],'CERO_CASOS_EN_EL_CORTE')
            self.assertNotIn('Archivo generado:',messages.getvalue())
            self.assertIn('NO_ES_FECHA_ELIMINACION',messages.getvalue())
            summary=rt.write_summary(ctx,manifest).read_text()
            self.assertIn('OMITIDO_SIN_CASOS',summary)

    def test_positive_cases_create_file_and_record_real_data_dimensions(self):
        with self.context() as ctx:
            namespace=self.namespace(pd.DataFrame({'RUT':['fixture'],'SEDE':['PTG']}))
            path=publish_eliminated_window(namespace)
            self.assertTrue(Path(path).is_file())
            self.assertEqual(Path(path).parent,ctx.output_dir.resolve())
            namespace['exportar_excel'].assert_called_once()
            self.assertTrue(namespace['exportar_excel'].call_args.kwargs['skip_if_empty'])
            manifest=rt.manifest_dict(ctx,namespace)
            self.assertEqual(manifest['decisiones_salidas_condicionales'][0]['estado'],'GENERADO')
            output=next(s for s in manifest['salidas'] if s['nombre']==Path(path).name)
            self.assertEqual((output['filas'],output['columnas']),(1,2))
            self.assertIn('no es fecha de eliminacion',output['proposito'])

    def test_recording_rejects_an_empty_case_file_or_a_missing_positive_output(self):
        with self.context() as ctx:
            path=ctx.output_dir/'contradiction.xlsx'
            with self.assertRaisesRegex(ValueError,'no coincide'):
                rt.record_conditional_output(path,rows=1,columns=2,purpose='fixture')
            path.touch()
            with self.assertRaisesRegex(ValueError,'no coincide'):
                rt.record_conditional_output(path,rows=0,columns=2,purpose='fixture')

    def test_disagreeing_case_total_blocks_instead_of_silently_omitting(self):
        with self.context():
            namespace=self.namespace(pd.DataFrame(columns=['RUT']))
            namespace['n_actualmente_eliminados_matriculados_en_ventana']=1
            with self.assertRaisesRegex(ValueError,'concilia'):
                publish_eliminated_window(namespace)

    def test_patagonia_is_present_in_manifest_totals(self):
        self.assertEqual(rt.collect_totals({'df_bd_ptg':pd.DataFrame({'token':['1','2']})})['filas_patagonia'],2)

    def test_2026_keeps_its_original_manifest_and_source(self):
        with self.context(2026,2) as ctx:
            manifest=rt.manifest_dict(ctx)
            self.assertNotIn('decisiones_salidas_condicionales',manifest)
            with self.assertRaisesRegex(ValueError,'2027 P1'):
                rt.record_conditional_output(ctx.output_dir/'fixture.xlsx',rows=0,columns=1,purpose='fixture')
        original=Path(__file__).resolve().parents[1].joinpath('caracterizacion.py').read_text()
        self.assertIn('ruta_eliminados_matricula_ventana = os.path.join(DESKTOP, nombre_eliminados_matricula_ventana)',original)
        adapted=adapted_source(original)
        compile(adapted,'conditional_outputs_test','exec')
        self.assertIn('publish_eliminated_window(globals())',adapted)
        self.assertNotIn('ruta_eliminados_matricula_ventana = os.path.join(DESKTOP, nombre_eliminados_matricula_ventana)',adapted)


if __name__=='__main__':unittest.main()
