"""Dashboard and macOS publication regressions. Synthetic inputs only."""
import os
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from test_analisis_anual_integrado import fixture
import consolidar_analisis_anual as annual
import ejecutar_analisis_anual as runner
import paneles_analisis_anual as panels


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.model=annual.prepare(fixture())
        self.payload=annual.make_payload(self.model)
        self.tables={t['name']:t for t in self.payload['main']}

    def test_six_views_precede_unchanged_supporting_tables(self):
        self.assertEqual([t['name'] for t in self.payload['main'][:6]],panels.NAMES)
        for name in ['Resumen','Filtros','Participación','Preguntas','Financiamiento','Rendimiento',
                     'Base anual','Respuestas P1','Respuestas P2','Respuestas P3','Diccionario']:
            self.assertIn(name,self.tables)
        self.assertEqual(self.payload['expected'],[8,5,3,0,2])

    def test_chart_sources_are_formulas_not_pasted_statistics(self):
        self.assertGreaterEqual(sum(len(self.tables[name]['charts']) for name in panels.NAMES),9)
        for name in panels.NAMES:
            table=self.tables[name]
            for chart in table['charts']:
                for _,series,_ in chart['series']:
                    self.assertIn(series.split(':')[0],table['formulas'])

    def test_no_zero_mean_or_person_sums_introduced(self):
        controls={(s,c):v for s,c,v in panels.expected_cells(self.model,{0:{'P3'}})}
        self.assertEqual(controls[('Panel rendimiento','A7')],'Sin notas disponibles al corte')
        self.assertEqual(controls[('Panel rendimiento','D7')],0)
        self.assertEqual(controls[('Panel rendimiento','G7')],0)
        empty={(s,c):v for s,c,v in panels.expected_cells(self.model,{0:set()})}
        self.assertEqual(empty[('Panel rendimiento','G7')],'No aplica')

    def test_group_selector_limits_question_codes(self):
        controls=self.tables['Explorador preguntas']['selectors']
        self.assertEqual(controls[0]['cell'],'C6')
        self.assertEqual(controls[1]['cell'],'J6')
        self.assertIn('OFFSET(',controls[1]['source'])
        self.assertIn('Seleccione un código del grupo',self.tables['Explorador preguntas']['formulas']['A7'])
        self.assertTrue(all('AND(' in formula for address,formula in self.tables['Opciones panel']['formulas'].items() if address.startswith('Q')))

    def test_all_finance_codes_are_retained_in_view(self):
        source_codes={row[2] for row in self.tables['Financiamiento']['rows']}
        panel=self.tables['Panel financiamiento']
        references=[value for address,value in panel['formulas'].items() if address.startswith('A')]
        self.assertGreaterEqual(len(references),len(source_codes))
        self.assertIn('100%',panel['note'])

    def test_decimal_formats_preserve_values(self):
        self.assertEqual(self.tables['Rendimiento']['decimal_columns'],[4])
        self.assertIn(11,self.tables['Base anual']['decimal_columns'])
        self.assertIn(['A7:C8','decimal'],self.tables['Panel rendimiento']['styles'])
        self.assertFalse(any('ROUND(' in f for t in self.payload['main'] for f in t['formulas'].values()))

    def test_panels_checked_under_every_filter_combination(self):
        for case in self.payload['filter_tests']:
            checked={name for name,_,_ in case['expected_cells']}
            self.assertTrue({'Panel ejecutivo','Cobertura','Panel rendimiento','Panel sectorial'} <= checked)

    @unittest.skipUnless(os.environ.get('ANUAL_TEST_XLSX')=='1','Explicit synthetic rendering test')
    def test_long_labels_and_eleven_finance_options(self):
        parts=fixture()
        alternatives=['Recursos propios provenientes de mi trabajo remunerado',
                      'Apoyo económico de mi familia y de otras personas del hogar',
                      'Beca de arancel otorgada por la institución',
                      'Crédito para financiar mis estudios de educación superior',
                      'Ahorros personales destinados al pago de matrícula y arancel',
                      'Apoyo económico de la empresa en la que trabajo',
                      'Beneficio de financiamiento otorgado por un organismo público',
                      'Beca externa de una organización privada',
                      'Ingresos de una actividad independiente',
                      'Préstamo familiar para el pago de los estudios',
                      'Otra fuente de financiamiento declarada por el estudiante']
        for part in parts:
            part['results']=part['results'].drop(columns=['G01Q19. ¿Cómo financias?'])
            part['inventory']['G01Q19']={'group':'ANTECEDENTES FAMILIARES Y SOCIOECONÓMICOS',
                'type':'M','type_label':'Múltiple'}
            part['base']['PROMEDIO_AC_REFERENCIA']=['5.4567' if i%2==0 else '6.1234' for i in range(len(part['base']))]
            for i,label in enumerate(alternatives,1):
                part['results'][f'G01Q19[SQ{i:03}]. ¿Cómo financiarás tus estudios? [{label}]']=[
                    'Y' if (r+i+part['entry']['periodo'])%3==0 else '' for r in range(len(part['results']))]
        payload=annual.make_payload(annual.prepare(parts))
        destination=ROOT/'.local/pruebas_dashboard_etiquetas'
        destination.mkdir(exist_ok=True,parents=True)
        file=destination/'synthetic.json'
        file.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
        annual.render_payload(file,destination,verify_filters=True)
        evidence=annual.validate_saved_exports(payload,destination)
        self.assertTrue(evidence['nativeChartBindingsChecked'])
        book=annual.load_workbook(destination/'02_SALIDAS/Caracterizacion_anual_2026.xlsx',data_only=True)
        try:
            self.assertEqual([book['Panel financiamiento'][f'A{i}'].value for i in range(31,42)],
                             [f'G01Q19[SQ{i:03}]' for i in range(1,12)])
            self.assertEqual([book['Panel financiamiento'][f'C{i}'].value for i in range(31,42)],alternatives)
            self.assertEqual(book['Panel rendimiento']['A7'].number_format,'0.0')
            self.assertAlmostEqual(book['Panel rendimiento']['A7'].value,5.79005)
        finally:
            book.close()
        verification=json.loads((destination/'04_AUDITORIA/validacion_excel.json').read_text())
        self.assertGreaterEqual(verification['localSelectorChecks'],8)
        self.assertFalse(verification['nativeExcelTested'])

    @unittest.skipUnless(sys.platform=='darwin','Finder metadata is macOS-specific')
    def test_finder_visibility_clears_flags_without_changing_source_or_content(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/'delivery'
            directory.mkdir()
            folder=directory/'02_SALIDAS'
            folder.mkdir()
            file=folder/'report.txt'
            file.write_bytes(b'synthetic bytes')
            original=annual.sha(file)
            for path in (directory,folder,file):
                os.chflags(path,path.stat().st_flags|stat.UF_HIDDEN)
            finder=bytearray(32)
            finder[8:10]=(0x4000).to_bytes(2,'big')
            subprocess.run(['/usr/bin/xattr','-wx','com.apple.FinderInfo',finder.hex(),str(folder)],check=True)
            evidence=runner.ensure_delivery_visible(directory)
            self.assertEqual(evidence['status'],'VISIBLE_VERIFICADO')
            self.assertEqual(evidence['paths_checked'],3)
            self.assertEqual(annual.sha(file),original)
            self.assertTrue(all(not p.stat().st_flags&stat.UF_HIDDEN for p in (directory,folder,file)))
            second=runner.ensure_delivery_visible(directory)
            self.assertEqual(second['attributes_cleared'],0)


if __name__=='__main__':
    unittest.main()
