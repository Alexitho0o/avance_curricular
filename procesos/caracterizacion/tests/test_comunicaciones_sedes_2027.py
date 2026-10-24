import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import caracterizacion_runtime as rt
from caracterizacion_comunicaciones_2027 import (
    normalize_communications, partition_communications, patagonia_payload, publish_communications)
from caracterizacion_financiamiento_2027 import adapted_source
from caracterizacion_sedes_2027 import communication_sede


class CommunicationSedeTests(unittest.TestCase):
    def fake_legacy_export(self,frame,name,title):
        rt.output_path(name,audit=False).touch()

    def fake_native_export(self,payload,path,evidence,**kwargs):
        path.touch()
        return str(path)

    def frame(self):
        return pd.DataFrame({'RUT':['1-1','2-2','3-3','4-4'],
            'firstname':['Fixture']*4,'lastname':['Test']*4,
            'email':['fixture@example.invalid']*4,'Email':['inst@example.invalid']*4,
            'Fono':['001']*4,'token':['1','2','3','4'],'Responden':['NO']*4,
            'NUEVO':['','NUEVO','',''],'SITUACION_LABORAL':['']*4,'SEDE':['OTRA']*4})

    def test_catalog_recognizes_patagonia_and_keeps_unknown_codes(self):
        self.assertEqual(communication_sede(' ptg '),'PATAGONIA')
        self.assertEqual(communication_sede('RE'),'SANTIAGO')
        self.assertEqual(communication_sede('CO'),'CONCEPCION')
        self.assertEqual(communication_sede('UNKNOWN'),'UNKNOWN')
        self.assertEqual(communication_sede(None),'SIN_CODIGO')

    def test_source_alignment_is_required(self):
        with self.assertRaisesRegex(ValueError,'alinea'):
            normalize_communications(self.frame(),pd.Series(['PTG']*4,index=[9,10,11,12]))

    def test_three_partitions_are_disjoint_and_unknown_remains_in_general(self):
        original=self.frame()
        normalized=normalize_communications(original,pd.Series(['RE','CO','PTG','X']))
        partitions,unknown=partition_communications(normalized)
        self.assertEqual(normalized.SEDE.tolist(),['SANTIAGO','CONCEPCION','PATAGONIA','X'])
        self.assertEqual(partitions['PATAGONIA'].token.tolist(),['3'])
        self.assertEqual(unknown.token.tolist(),['4'])
        self.assertEqual(sum(len(p) for p in partitions.values())+len(unknown),4)
        pd.testing.assert_frame_equal(original.drop(columns='SEDE'),normalized.drop(columns='SEDE'))
        self.assertTrue(original.SEDE.eq('OTRA').all())

    def test_duplicate_or_missing_tokens_do_not_pass_partition_control(self):
        frame=self.frame()
        for value in ['1','']:
            frame.loc[1,'token']=value
            with self.assertRaisesRegex(ValueError,'unico'):
                partition_communications(frame)

    def test_patagonia_schema_preserves_identifiers_email_and_existing_highlight(self):
        frame=normalize_communications(self.frame(),pd.Series(['PTG']*4))
        payload=patagonia_payload(frame,year=2027,period=1,source='fixture.xlsx')
        self.assertEqual(payload['headers'][3:5],['EMAIL','EMAIL__2'])
        self.assertEqual(payload['rows'][0][5],'001')
        self.assertEqual(payload['rows'][1][8],'NUEVO')
        self.assertTrue(all(row[-1]=='PATAGONIA' for row in payload['rows']))
        with self.assertRaisesRegex(ValueError,'otra sede'):
            patagonia_payload(self.frame(),year=2027,period=1,source='fixture.xlsx')

    def test_selected_delivery_files_route_to_outputs_and_internal_files_do_not(self):
        old=rt.ACTIVE_CONTEXT;rt.ACTIVE_CONTEXT=None
        try:
            with tempfile.TemporaryDirectory() as temp,patch.dict(os.environ,{'CARACTERIZACION_RUN_DIR':temp}):
                ctx=rt.prepare_run_context(2027,1,external_tee=True)
                names=['Actualmente_eliminados_matricula_en_ventana_2027_P1_20261013.xlsx',
                    'Consolidado_eliminados_reporte_2027_P1_20261013.xlsx',
                    'BD_Comunicaciones_2027_P1_20261013.xlsx',
                    'BD_Comunicaciones_Santiago_2027_P1_20261013.xlsx',
                    'BD_Comunicaciones_Concepcion_2027_P1_20261013.xlsx',
                    'BD_Comunicaciones_Patagonia_2027_P1_20261013.xlsx']
                for name in names:
                    self.assertEqual(rt.output_path(name).parent,ctx.output_dir.resolve())
                self.assertEqual(rt.output_path('Seguimiento_incorporacion_LimeSurvey.xlsx').parent,ctx.analysis_dir.resolve())
                self.assertEqual(rt.output_path('AUDITORIA_SEDES.xlsx').parent,ctx.audit_dir.resolve())
                ctx._finalized=True
        finally:rt.ACTIVE_CONTEXT=old

    def test_empty_patagonia_does_not_create_a_workbook(self):
        old=rt.ACTIVE_CONTEXT;rt.ACTIVE_CONTEXT=None
        try:
            with tempfile.TemporaryDirectory() as temp,patch.dict(os.environ,{'CARACTERIZACION_RUN_DIR':temp}):
                ctx=rt.prepare_run_context(2027,1,external_tee=True)
                with patch('caracterizacion_comunicaciones_2027.export_artifact_workbook') as author:
                    frame=normalize_communications(self.frame(),pd.Series(['RE']*4))
                    namespace={'df_bd_export':frame,'str_yyyymmdd_scl':lambda:'20261013',
                        '_exportar_bd_comunicaciones':self.fake_legacy_export,'log_avance':lambda message:None}
                    outputs=publish_communications(namespace)
                    self.assertFalse(author.called)
                    self.assertEqual(set(outputs),{'GENERAL','SANTIAGO'})
                    self.assertEqual(namespace['COMUNICACIONES_SEDES_2027']['general'],4)
                ctx._finalized=True
        finally:rt.ACTIVE_CONTEXT=old

    def test_adapter_replaces_only_the_2027_communication_block(self):
        original=Path(__file__).resolve().parents[1].joinpath('caracterizacion.py').read_text()
        adapted=adapted_source(original)
        compile(adapted,'communication_adapter_test','exec')
        block=adapted[adapted.index('# BLOQUE 5 ·'):adapted.index('# BLOQUE 6 -')]
        self.assertIn('publish_communications(globals())',block)
        self.assertIn('INCORPORACION_PLAN.columns["SEDE"]',block)
        self.assertNotIn('= "OTRA"',block)
        self.assertIn('df_bd_export.loc[~df_bd_export["SEDE"].isin(["SANTIAGO", "CONCEPCION"]), "SEDE"] = "OTRA"',original)

    def test_patagonia_publication_uses_current_source_and_output_folder(self):
        old=rt.ACTIVE_CONTEXT;rt.ACTIVE_CONTEXT=None
        try:
            with tempfile.TemporaryDirectory() as temp,patch.dict(os.environ,{'CARACTERIZACION_RUN_DIR':temp}):
                ctx=rt.prepare_run_context(2027,1,external_tee=True)
                with patch('caracterizacion_comunicaciones_2027.export_artifact_workbook',
                           side_effect=self.fake_native_export) as author:
                    namespace={'df_bd_export':normalize_communications(self.frame(),pd.Series(['PTG']*4)),
                        'str_yyyymmdd_scl':lambda:'20261013','ruta_matricula':'/fixture/DATOSDEALUMNOS_11941.xlsx',
                        '_exportar_bd_comunicaciones':self.fake_legacy_export,'log_avance':lambda message:None}
                    outputs=publish_communications(namespace)
                    self.assertEqual(set(outputs),{'GENERAL','PATAGONIA'})
                    payload,path,_=author.call_args.args
                    self.assertEqual(payload['source'],'DATOSDEALUMNOS_11941.xlsx')
                    self.assertEqual(path.parent,ctx.output_dir.resolve())
                    self.assertEqual(namespace['COMUNICACIONES_SEDES_2027']['sedes']['PATAGONIA'],4)
                ctx._finalized=True
        finally:rt.ACTIVE_CONTEXT=old


if __name__=='__main__':unittest.main()
