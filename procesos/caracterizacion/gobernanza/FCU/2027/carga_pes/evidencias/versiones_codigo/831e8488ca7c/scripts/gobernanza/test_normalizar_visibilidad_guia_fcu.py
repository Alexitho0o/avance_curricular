from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from lxml import etree
import normalizar_visibilidad_guia_fcu as visibility


class VisibilityTests(unittest.TestCase):
    def test_only_guide_visibility_changes_not_other_workbook_parts(self):
        source = Path(__file__).resolve().parents[2] / 'gobernanza/FCU/2027/preparacion/evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261006.xlsx'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'guide.xlsx'
            shutil.copy2(source, target)
            with zipfile.ZipFile(target) as archive:
                before = {name:archive.read(name) for name in archive.namelist()}
            result = visibility.normalize(target)
            self.assertGreater(result['guide_hidden_rows_cleared'],0)
            self.assertEqual(result['guide_filters_cleared'],1)
            with zipfile.ZipFile(target) as archive:
                after = {name:archive.read(name) for name in archive.namelist()}
            changed = [name for name in before if before[name] != after[name]]
            self.assertEqual(len(changed),1)
            original, final = etree.fromstring(before[changed[0]]), etree.fromstring(after[changed[0]])
            self.assertEqual([etree.tostring(c) for c in original.findall(f'.//{{{visibility.MAIN}}}c')],
                             [etree.tostring(c) for c in final.findall(f'.//{{{visibility.MAIN}}}c')])
            self.assertFalse(final.findall(f'{{{visibility.MAIN}}}autoFilter'))
            self.assertFalse(any(r.get('hidden') for r in final.findall(f'{{{visibility.MAIN}}}sheetData/{{{visibility.MAIN}}}row')))

    def test_normalization_is_idempotent(self):
        source = Path(__file__).resolve().parents[2] / 'gobernanza/FCU/2027/preparacion/evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261006.xlsx'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'guide.xlsx'
            shutil.copy2(source,target)
            visibility.normalize(target)
            result = visibility.normalize(target)
            self.assertEqual(result['guide_hidden_rows_cleared'],0)
            self.assertEqual(result['guide_filters_cleared'],0)


if __name__ == '__main__':
    unittest.main()
