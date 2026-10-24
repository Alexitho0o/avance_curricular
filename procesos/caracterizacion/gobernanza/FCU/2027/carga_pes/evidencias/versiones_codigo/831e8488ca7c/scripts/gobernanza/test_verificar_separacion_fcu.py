import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import verificar_separacion_fcu as separation


class FrozenReferenceTests(unittest.TestCase):
    def test_real_frozen_reference_is_intact(self):
        result = separation.verify_frozen_reference()
        self.assertTrue(result['ok'])
        self.assertGreater(result['checked_files'],0)

    def test_missing_and_changed_files_are_not_silently_rebased(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root/'reference.txt'
            reference.write_text('original')
            baseline = root/'baseline.json'
            baseline.write_text(json.dumps({'files':[{'path':'reference.txt','sha256':hashlib.sha256(reference.read_bytes()).hexdigest()}]}))
            self.assertTrue(separation.verify_frozen_reference(baseline,root)['ok'])
            reference.write_text('changed')
            result = separation.verify_frozen_reference(baseline,root)
            self.assertEqual(result['issues'][0]['issue'],'FROZEN_REFERENCE_CHANGED')
            reference.unlink()
            result = separation.verify_frozen_reference(baseline,root)
            self.assertEqual(result['issues'][0]['issue'],'FROZEN_REFERENCE_MISSING')

    def test_protected_output_tree_and_exact_file_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frozen, other = root/'2026', root/'2027'
            for target in [frozen, frozen/'run'/'data.csv']:
                with self.assertRaises(ValueError):
                    separation.assert_2027_output_path(target,[frozen],[])
            with self.assertRaises(ValueError):
                separation.assert_2027_output_path(other/'inventory.xlsx',[],[other/'inventory.xlsx'])
            self.assertEqual(separation.assert_2027_output_path(other/'data.csv',[frozen],[]),(other/'data.csv').resolve())

    def test_symlink_does_not_bypass_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frozen = root/'2026'
            frozen.mkdir()
            alias = root/'alias'
            alias.symlink_to(frozen,target_is_directory=True)
            with self.assertRaises(ValueError):
                separation.assert_2027_output_path(alias/'data.csv',[frozen],[])

    def test_student_data_does_not_go_into_publishable_governance(self):
        with self.assertRaises(ValueError):
            separation.assert_private_output_path(separation.ROOT/'gobernanza/FCU/2027/carga_pes/evidencias')
        self.assertEqual(separation.assert_private_output_path(separation.ROOT/'.local/FCU/2027'),
                         (separation.ROOT/'.local/FCU/2027').resolve())
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(separation.assert_private_output_path(directory),Path(directory).resolve())


if __name__ == '__main__':
    unittest.main()
