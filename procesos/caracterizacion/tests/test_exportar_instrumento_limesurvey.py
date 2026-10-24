from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from exportar_instrumento_limesurvey import parse_exports, workbook_tables, plain, check_profile, check_output_path


class InventoryTests(unittest.TestCase):
    def export(self, path, *, sid='1000', gid='1', order='0', name='Grupo', kind='Y', code='Q1'):
        root=ET.Element('document')
        group=ET.SubElement(ET.SubElement(ET.SubElement(root,'groups'),'rows'),'row')
        for key,value in dict(gid=gid,sid=sid,group_order=order,group_name=name,language='es').items():
            ET.SubElement(group,key).text=value
        question=ET.SubElement(ET.SubElement(ET.SubElement(root,'questions'),'rows'),'row')
        for key,value in dict(qid=gid+'0',gid=gid,sid=sid,parent_qid='0',title=code,type=kind,question_order='0',
                              question='<p>¿Aceptas?</p>',language='es',other='N').items():
            ET.SubElement(question,key).text=value
        ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
        return root

    def test_legacy_inline_text_and_implicit_yes_no(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'old.lsg'
            self.export(path)
            data=parse_exports([path])
            self.assertEqual(data['groups'][0]['questions'][0]['text'],'¿Aceptas?')
            rows=workbook_tables(data)['Detalle']['rows']
            self.assertEqual([r[5] for r in rows],['Y','N'])
            self.assertEqual([r[6] for r in rows],['Sí','No'])

    def test_groups_follow_metadata_not_filename_or_code(self):
        with tempfile.TemporaryDirectory() as temp:
            first,second=Path(temp)/'z.lsg',Path(temp)/'a.lsg'
            self.export(first,gid='9',order='0',name='Primero',code='Q9')
            self.export(second,gid='1',order='1',name='Segundo',code='Q1')
            data=parse_exports([second,first])
            self.assertEqual([g['text'] for g in data['groups']],['Primero','Segundo'])

    def test_duplicate_groups_and_mixed_surveys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            first,second=Path(temp)/'a.lsg',Path(temp)/'b.lsg'
            self.export(first)
            self.export(second)
            with self.assertRaises(ValueError):
                parse_exports([first,second])
            self.export(second,sid='2000',gid='2',code='Q2')
            with self.assertRaises(ValueError):
                parse_exports([first,second])

    def test_native_five_point_scale_and_free_text(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'old.lsg'
            self.export(path,kind='A')
            data=parse_exports([path])
            self.assertEqual([o['code'] for o in data['groups'][0]['questions'][0]['builtin_options']],['1','2','3','4','5'])
            self.export(path,kind='S')
            table=workbook_tables(parse_exports([path]))['Detalle']['rows']
            self.assertEqual(table[0][4],'Entrada libre')
            self.assertEqual(table[0][5],'')

    def test_html_is_read_as_text_and_scripts_are_not_content(self):
        self.assertEqual(plain('<p>Primera&nbsp;línea</p><script>IGNORAR</script><p>Segunda</p>'),'Primera línea\nSegunda')

    def test_registered_profiles_cannot_be_relabelled(self):
        check_profile('443299', 2026, 2)
        check_profile('141234', 2027, 1)
        for sid, year, period in [('443299', 2026, 1), ('141234', 2026, 2)]:
            with self.assertRaises(ValueError):
                check_profile(sid, year, period)

    def test_frozen_outputs_are_protected(self):
        with self.assertRaises(ValueError):
            check_output_path(ROOT / 'gobernanza/FCU/2026/inventario.xlsx')

    def test_modern_localized_question_options_and_subquestion(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'modern.lsg'
            root = self.export(path, kind='F')
            tables = {
                'group_l10ns': [{'gid': '1', 'language': 'es', 'group_name': 'Grupo localizado'}],
                'question_l10ns': [{'qid': '10', 'language': 'es', 'question': 'Pregunta localizada'},
                                   {'qid': '11', 'language': 'es', 'question': 'Texto del item'}],
                'subquestions': [{'qid': '11', 'parent_qid': '10', 'title': 'SQ002', 'question_order': '0', 'scale_id': '0'}],
                'answers': [{'aid': '20', 'qid': '10', 'code': 'A002', 'sortorder': '2', 'scale_id': '0'},
                            {'aid': '21', 'qid': '10', 'code': 'A001', 'sortorder': '1', 'scale_id': '0'}],
                'answer_l10ns': [{'aid': '20', 'language': 'es', 'answer': 'Segunda opcion'},
                                {'aid': '21', 'language': 'es', 'answer': 'Primera opcion'}]}
            for table, items in tables.items():
                node = ET.SubElement(ET.SubElement(root, table), 'rows')
                for item in items:
                    row = ET.SubElement(node, 'row')
                    for key, value in item.items():
                        ET.SubElement(row, key).text = value
            ET.ElementTree(root).write(path, encoding='utf-8')
            model = parse_exports([path])
            question = model['groups'][0]['questions'][0]
            self.assertEqual(question['text'], 'Pregunta localizada')
            self.assertEqual(question['subquestions'][0]['code'], 'SQ002')
            self.assertEqual(question['subquestions'][0]['text'], 'Texto del item')
            self.assertEqual([a['code'] for a in question['options']], ['A001', 'A002'])


if __name__=='__main__':
    unittest.main()
