"""Resource and source-transport regressions, without using student records."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import consolidar_analisis_anual as annual
from completar_fuentes_excel_anual import complete_source_sheets, source_cell, validate_source_dependencies, NS
from test_analisis_anual_integrado import fixture


def volume_fixture():
    parts=fixture()
    for p,(part,n_base,n_raw) in enumerate(zip(parts,[1622,467,431],[1660,310,268]),1):
        base=[]
        for i in range(n_base):
            item=part['base'].iloc[0].to_dict()
            person=str(10000000+p*100000+i)
            item.update(TOKEN_NORMALIZADO=person,RUT_NORMALIZADO=person+'K',CODCLI=f'SYNTH-{p}-{i}',
                        SECTOR_ACADEMICO=['Administración y Comercio','Salud','Tecnología'][i%3],
                        CARRERA=f'Carrera sintética {i%39:02}',SEDE=['RE','CO','PTG'][i%3],
                        MODALIDAD_CARRERA=['Presencial','Online','Semipresencial'][i%3],
                        ESTADO_RESPUESTA=('INCOMPLETO' if i%7==0 else 'SI') if i<n_raw else 'NO',
                        ID_RESPUESTA_SELECCIONADO=str(i+1) if i<n_raw else '',
                        PROMEDIO_AC_REFERENCIA=str(4+(i%25)/10),TRAMO_NIVEL_AC=f'Nivel {i%3+1}')
            base.append(item)
        data={'id. ID':[str(i+1) for i in range(n_raw)],
              'token. Access code':[str(10000000+p*100000+i) for i in range(n_raw)]}
        inventory={}
        for q in range(1,95):
            code=f'G01Q{q:03}'
            label='Financiamiento sintético' if q==19 else f'Pregunta sintética {q}'
            count=322 if q==1 else 11
            data[f'{code}. {label}']=[f'Opción {i%count:03}' for i in range(n_raw)]
            inventory[code]={'group':f'Grupo sintético {q%7+1}', 'type':'L','type_label':'Selección única'}
        # Dense immutable source fields reproduce the width of the failed export.
        # They are explicitly synthetic metadata, not invented survey questions.
        for c in range(155):
            data[f'Metadata sintética {c}']=[f'Literal {p}-{i}-{c}: á, &, <texto>' for i in range(n_raw)]
        part.update(base=pd.DataFrame(base),results=pd.DataFrame(data),inventory=inventory)
    return parts


class MemoryAnnualTests(unittest.TestCase):
    def test_incremental_transport_preserves_literals_formulas_and_other_members(self):
        payload={'main':[{'name':'Respuestas P1','stream_source_literals':True,
                          'headers':['Literal','Incluida'],
                          'rows':[['=NO_ES_FORMULA & <á>',None],['  espacio  ',None]],
                          'formulas':{'B7':'=1','B8':'=0'}}]}
        sheet=f'''<worksheet xmlns="{NS}">
          <cols><col min="1" max="2" width="24"/></cols><sheetData>
          <row r="6"><c r="A6" t="inlineStr"><is><t>Literal</t></is></c></row>
          <row r="7"><c r="A7" s="3"/><c r="B7" s="3"><f>1</f><v>1</v></c></row>
          <row r="8"><c r="B8" s="3"><f>0</f><v>0</v></c></row>
          </sheetData></worksheet>'''
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'02_SALIDAS').mkdir()
            (root/'04_AUDITORIA').mkdir()
            path=root/'02_SALIDAS/test.xlsx'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('xl/workbook.xml',f'''<workbook xmlns="{NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Respuestas P1" sheetId="1" r:id="rId1"/></sheets></workbook>''')
                archive.writestr('xl/_rels/workbook.xml.rels','''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>''')
                archive.writestr('xl/worksheets/sheet1.xml',sheet)
                archive.writestr('xl/charts/preserved.xml',b'<chart>unchanged</chart>')
            for _ in range(2):
                complete_source_sheets(path,payload)
                with zipfile.ZipFile(path) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(archive.read('xl/charts/preserved.xml'),b'<chart>unchanged</chart>')
                    xml=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
                    cells={c.attrib['r']:c for c in xml.iter(f'{{{NS}}}c')}
                    for address,text in [('A7','=NO_ES_FORMULA & <á>'),('A8','  espacio  ')]:
                        self.assertEqual(cells[address].find(f'{{{NS}}}is/{{{NS}}}t').text,text)
                        self.assertIsNone(cells[address].find(f'{{{NS}}}f'))
                    self.assertEqual(cells['B7'].find(f'{{{NS}}}v').text,'1')
                    self.assertEqual(cells['B8'].find(f'{{{NS}}}f').text,'0')
                    self.assertEqual(xml.find(f'{{{NS}}}autoFilter').attrib['ref'],'A6:B8')
                    self.assertEqual(xml.find(f'{{{NS}}}dimension').attrib['ref'],'A1:B8')
            original=path.read_bytes()
            payload['main'][0]['rows'][0][0]=float('nan')
            with self.assertRaises(ValueError):
                complete_source_sheets(path,payload)
            self.assertEqual(path.read_bytes(),original)
            self.assertFalse(path.with_suffix('.sources.tmp').exists())

    def test_invalid_literals_fail_without_silent_replacement(self):
        for value in [float('nan'),float('inf'),'texto\x01']:
            with self.assertRaises(ValueError):
                source_cell('A7',value,'0')

    def test_deferred_sources_cannot_feed_uncalculated_cells(self):
        payload=annual.make_payload(annual.prepare(fixture()))
        self.assertEqual(len(validate_source_dependencies(payload)),3)
        for formula in ["='Respuestas P1'!$A$7", "=COUNTA('respuestas p1'!a:a)",
                        '=INDIRECT("A7")', "=COUNTA('Respuestas P1'!7:7)"]:
            payload['main'][0]['formulas']['A7']=formula
            with self.assertRaisesRegex(ValueError,'fuente diferida'):
                validate_source_dependencies(payload)

    def test_question_lookup_is_shared_not_repeated_per_value(self):
        payload=annual.make_payload(annual.prepare(fixture()))
        tables={t['name']:t for t in payload['main']}
        self.assertIn('Índices panel',tables)
        self.assertFalse(any('COUNTIF(' in f for a,f in tables['Opciones panel']['formulas'].items() if a.startswith('Q')))
        for address,formula in tables['Explorador preguntas']['formulas'].items():
            if int(''.join(filter(str.isdigit,address)))>=31:
                self.assertNotIn('COUNTIFS(',formula)
                self.assertNotIn('MATCH(',formula)
        self.assertTrue(all(t.get('stream_source_literals') for t in payload['main'] if t['name'].startswith('Respuestas P')))

    @unittest.skipUnless(os.environ.get('ANUAL_STRESS_XLSX')=='1','Explicit volume/export test')
    def test_export_at_incident_volume(self):
        payload=annual.make_payload(annual.prepare(volume_fixture()))
        # Representative recalculation checks; the full small regression suite
        # covers every dimension combination. This test exercises export volume.
        payload['filter_tests']=[payload['filter_tests'][i] for i in (0,1,-1)]
        path=ROOT/'.local/pruebas_anual_volumen'
        path.mkdir(parents=True,exist_ok=True)
        input_path=path/'synthetic.json'
        input_path.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
        self.assertEqual(len(next(t for t in payload['main'] if t['name']=='Base anual')['rows']),2520)
        self.assertGreaterEqual(len(next(t for t in payload['main'] if t['name']=='Conteos personas')['rows']),25000)
        self.assertEqual(len(next(t for t in payload['main'] if t['name']=='Índices panel')['rows']),322)
        annual.render_payload(input_path,path,verify_filters=True)
        evidence=annual.validate_saved_exports(payload,path)
        self.assertTrue(evidence['sourceCellsPreserved'])
        book=annual.load_workbook(path/'02_SALIDAS/Caracterizacion_anual_2026.xlsx',read_only=True,data_only=True)
        try:
            for name,count in [('Respuestas P1',1660),('Respuestas P2',310),('Respuestas P3',268)]:
                self.assertEqual(book[name].max_row,count+6)
                self.assertEqual(book[name].max_column,254)
        finally:
            book.close()


if __name__=='__main__':
    unittest.main()
