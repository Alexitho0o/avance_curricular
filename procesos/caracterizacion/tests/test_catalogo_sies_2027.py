"""Pruebas de la conexion portable, aislada del proceso productivo 2026."""
from datetime import date
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pandas as pd

from caracterizacion_catalogo_sies_2027 import DIRECTORY, OUTPUT_COLUMNS, enrich_frame, load_package


def frame():
    return pd.DataFrame([
        {'CODCARPR':'PMTENS','NOMBRE_L':'TECNICO EN ENFERMERIA','SEDE':'PTG','JORNADA':'V'},
        {'CODCARPR':'TAMD','NOMBRE_L':'TECNICO EN ADMINISTRACION DE EMPRESAS','SEDE':'RE','JORNADA':'O'},
        {'CODCARPR':'TENSSP','NOMBRE_L':'TECNICO EN ENFERMERIA SP','SEDE':'RE','JORNADA':'V'},
        {'CODCARPR':'CIFIN','NOMBRE_L':'CONTINUIDAD INGENIERIA FINANZAS','SEDE':'RE','JORNADA':'O'},
    ], index=[10,20,30,40]).assign(ANOMATRICULA=2027, PERIODOMATRICULA=1, MODALIDAD='ESCOLAR', CON_FIRMA='SI')


class CatalogoSiesTests(unittest.TestCase):
    def test_auditoria_real_preserva_cruce_y_separa_modalidad(self):
        directory = Path(__file__).resolve().parents[1]/'docs/gobernanza'
        old = json.loads((directory/'COBERTURA_CATALOGO_SIES_2027_P1_11941_20261013.json').read_text())
        new = json.loads((directory/'COBERTURA_CATALOGO_SIES_2027_P1_11941_20261013_MODALIDAD_V2.json').read_text())
        self.assertEqual(new['fuente'], old['fuente'])
        self.assertEqual(new['registros'], 271)
        self.assertEqual(new['estados_codigo_sies'], old['estados'])
        self.assertEqual(new['estados_modalidad'], {'RESUELTA_CODIGO_UNICO':88,'RESUELTA_COINCIDENCIA_CANDIDATOS':131,'SIN_EQUIVALENCIA':52})
        self.assertEqual(new['modalidades'], {'Presencial':57,'No presencial':162,'No determinada':52})
        identity = ('CODCARPR','NOMBRE_L','SEDE','JORNADA','CODIGO_UNICO_SIES','CANDIDATOS_SIES','registros')
        for rows in (old['dimensiones'],new['dimensiones']):
            self.assertEqual(sum(row['registros'] for row in rows), 271)
        self.assertEqual(sorted(tuple(r[k] for k in identity) for r in old['dimensiones']),
                         sorted(tuple(r[k] for k in identity) for r in new['dimensiones']))

    def test_enriquecimiento_no_muta_fuente_ni_filtra(self):
        original = frame()
        before = original.copy(deep=True)
        output, audit = enrich_frame(original, anio=2027, periodo=1)
        pd.testing.assert_frame_equal(original, before)
        pd.testing.assert_frame_equal(output[original.columns], before)
        self.assertEqual(list(output.index), [10,20,30,40])
        self.assertEqual(output.loc[10,'CODIGO_UNICO_SIES'], 'I162S4C91J2V1')
        self.assertEqual(output.loc[10,'MODALIDAD_CARRERA'], 'Presencial')
        self.assertEqual(output.loc[20,'ESTADO_CRUCE_SIES'], 'AMBIGUO')
        self.assertEqual(output.loc[20,'CODIGO_UNICO_SIES'], '')
        self.assertEqual(output.loc[20,'ESTADO_CODIGO_SIES'], 'AMBIGUO')
        self.assertEqual(output.loc[20,'MODALIDAD_CARRERA'], 'No presencial')
        self.assertEqual(output.loc[20,'ESTADO_MODALIDAD'], 'RESUELTA_COINCIDENCIA_CANDIDATOS')
        self.assertEqual(output.loc[30,'ESTADO_CRUCE_SIES'], 'SIN_EQUIVALENCIA')
        self.assertEqual(output.loc[40,'CODIGO_UNICO_SIES'], 'I162S2C111J4V2')
        self.assertEqual(audit['estados'], {'RESUELTO':2,'AMBIGUO':1,'SIN_EQUIVALENCIA':1})
        self.assertEqual(audit['estados_codigo_sies'], audit['estados'])
        self.assertEqual(audit['estados_modalidad'], {'RESUELTA_CODIGO_UNICO':2,'RESUELTA_COINCIDENCIA_CANDIDATOS':1,'SIN_EQUIVALENCIA':1})
        self.assertTrue(audit['conciliacion_registros'])
        self.assertFalse(audit['cambia_elegibilidad'])

    def test_rechaza_2026_y_cohorte_mezclada(self):
        for year in (2026,2028):
            with self.subTest(year=year), self.assertRaises(ValueError):
                enrich_frame(frame(), anio=year, periodo=1)
        mixed = frame()
        mixed.loc[10,'ANOMATRICULA'] = 2026
        with self.assertRaises(ValueError):
            enrich_frame(mixed, anio=2027, periodo=1)

    def test_columnas_ausentes_y_cero_filas(self):
        output, audit = enrich_frame(pd.DataFrame([{'CODCARPR':'PMTENS'}]), anio=2027, periodo=1)
        self.assertEqual(output.iloc[0].ESTADO_CRUCE_SIES, 'DATOS_INSUFICIENTES')
        self.assertEqual(output.iloc[0].ESTADO_MODALIDAD, 'DATOS_INSUFICIENTES')
        empty, audit = enrich_frame(frame().iloc[:0], anio=2027, periodo=1)
        self.assertEqual(len(empty), 0)
        self.assertTrue(set(OUTPUT_COLUMNS).issubset(empty))
        self.assertEqual(audit['estados'], {})

    def test_no_sobrescribe_modalidad_previa(self):
        with self.assertRaises(ValueError):
            enrich_frame(frame().assign(MODALIDAD_CARRERA='desconocida'), anio=2027, periodo=1)

    def test_paquete_portable_sin_repo_externo(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / 'catalogo'
            shutil.copytree(DIRECTORY, copied)
            output, _ = enrich_frame(frame(), anio=2027, periodo=1, directory=copied)
            self.assertEqual(output.loc[10,'ESTADO_CRUCE_SIES'], 'RESUELTO')

    def test_hash_alterado_o_ano_incorrecto_se_bloquea(self):
        for target in ('catalogo.json','resolutor.py','EVIDENCIA_DIMENSIONES.json','POLITICA_MODALIDAD.json'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / 'catalogo'
                shutil.copytree(DIRECTORY, copied)
                descriptor = json.loads((copied/'ACTIVO_2027.json').read_text())
                (copied/descriptor['archivos'][target]['path']).write_text('alterado')
                with self.assertRaises(ValueError):
                    load_package(copied)

    def test_publicador_real_agrega_campos_y_auditoria(self):
        from caracterizacion_comunicacion_2027 import publish_trajectory_analysis
        detail = frame().assign(TOKEN=['PRUEBA-A','PRUEBA-B','PRUEBA-C','PRUEBA-D'])
        plan = SimpleNamespace(today=date(2026,10,13), trajectory_detail=detail,
                               eligible=detail.iloc[:2], eligible_enrollments=detail.iloc[:2], current_tokens=['PRUEBA-A'],
                               trajectory_evidence=pd.DataFrame(), trajectory_summary={'REGISTROS':4})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch('caracterizacion_comunicacion_2027.rt.analysis_path', side_effect=lambda n:root/n), \
                 patch('caracterizacion_comunicacion_2027.rt.output_path', side_effect=lambda n,**kw:root/n):
                target = publish_trajectory_analysis(plan)
            result = pd.read_excel(target, sheet_name='Matricula periodo')
            self.assertEqual(len(result), 4)
            self.assertTrue(set(OUTPUT_COLUMNS).issubset(result))
            coverage = pd.read_excel(target,sheet_name='Cobertura SIES')
            self.assertEqual(coverage.groupby('Control').Registros.sum().to_dict(),{'Codigo SIES':4,'Modalidad':4})
            audit = json.loads((root/'AUDITORIA_CATALOGO_SIES_2027_P1_20261013.json').read_text())
            self.assertEqual(audit['registros'], 4)
            self.assertNotIn('PRUEBA-A', json.dumps(audit))
            pd.testing.assert_frame_equal(plan.trajectory_detail, detail)


if __name__ == '__main__':
    unittest.main()
