import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from exportar_instrumento_limesurvey import parse_exports, workbook_tables
from registrar_instrumento_limesurvey import register_package, verify_package, sha256


class RegistrationTests(unittest.TestCase):
    def evidence(self, root):
        evidence = root / 'evidence'
        (evidence / 'fuentes').mkdir(parents=True)
        (evidence / 'versiones_codigo').mkdir()
        source = evidence / 'fuentes/group.lsg'
        source.write_text('<document><groups><rows><row><gid>1</gid><sid>1000</sid><group_order>0</group_order><group_name>Grupo</group_name></row></rows></groups><questions><rows><row><qid>2</qid><gid>1</gid><parent_qid>0</parent_qid><title>Q1</title><type>Y</type><question>Pregunta</question><question_order>0</question_order></row></rows></questions></document>')
        model = parse_exports([source])
        model.update(year=2028, period=1, created='20261009')
        (evidence / 'inventory.json').write_text(json.dumps({'instrument': model, 'tables': workbook_tables(model)}))
        code = evidence / 'versiones_codigo/builder.mjs'
        code.write_text('// test fixture')
        workbook = root / 'test.xlsx'
        workbook.write_bytes(b'not-a-real-workbook-test-fixture')
        (evidence / 'manifest.json').write_text(json.dumps({
            'year': 2028, 'period': 1, 'survey_id': '1000', 'date': '20261009',
            'sha256': sha256(workbook), 'counts': {'groups': 1, 'questions': 1, 'subquestions': 0, 'explicit_options': 0},
            'scripts': {'scripts/builder.mjs': sha256(code)}}))
        return evidence, workbook

    def test_portable_archive_and_pending_p1(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, workbook = self.evidence(root)
            archive = root / 'archive'
            package = register_package(evidence, workbook, archive)
            self.assertEqual(verify_package(package)['survey_id'], '1000')
            model = json.loads((package / 'inventory.json').read_text())
            self.assertEqual(model['instrument']['sources'][0]['path'], 'fuentes/group.lsg')
            self.assertNotIn(str(evidence), (package / 'inventory.json').read_text())
            registry = json.loads((archive / 'REGISTRO.json').read_text())
            self.assertEqual(registry['instruments'][0]['status'], 'PENDIENTE_FUENTES')
            self.assertEqual(register_package(evidence, workbook, archive), package)

    def test_changed_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, workbook = self.evidence(root)
            (evidence / 'fuentes/group.lsg').write_text('<broken/>')
            with self.assertRaises(ValueError):
                register_package(evidence, workbook, root / 'archive')

    def test_archive_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, workbook = self.evidence(root)
            package = register_package(evidence, workbook, root / 'archive')
            (package / 'inventory.json').write_text('{}')
            with self.assertRaises(ValueError):
                verify_package(package)


if __name__ == '__main__':
    unittest.main()
