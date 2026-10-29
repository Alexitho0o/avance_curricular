"""Controles de propuestas sin datos ni identidades reales."""
import sys
from pathlib import Path
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolver_planes_h002c import state, txt, dimension, norm, write_same
from tempfile import TemporaryDirectory


class H002c(unittest.TestCase):
    def test_unico_dos_evidencias(self):
        self.assertEqual(state({'OPCION_A'}, {'OPCION_A'}), 'CALCE_UNICO')

    def test_documental_solo_debil(self):
        self.assertEqual(state(set(), {'OPCION_A'}), 'CALCE_DEBIL')

    def test_perfil_solo_debil(self):
        self.assertEqual(state({'OPCION_A'}, set()), 'CALCE_DEBIL')

    def test_conflicto_no_se_elige(self):
        self.assertEqual(state({'OPCION_A'}, {'OPCION_B'}), 'CONFLICTO')

    def test_varias_opciones_no_unico(self):
        self.assertEqual(state({'OPCION_A','OPCION_B'}, {'OPCION_A'}), 'CALCE_DEBIL')

    def test_sin_calce(self):
        self.assertEqual(state(set(),set()), 'SIN_CALCE')

    def test_cero_se_conserva(self):
        self.assertEqual(txt(0),'0')
        self.assertEqual(txt(None),'')

    def test_co_y_j3_son_dimensiones_distintas(self):
        self.assertEqual(dimension('I162S3C999J3V1'), ('3','999','3','1'))
        self.assertNotEqual(dimension('I162S3C999J3V1'),dimension('I162S2C999J4V1'))

    def test_normalizacion_nombre_no_quita_tipo_carrera(self):
        self.assertEqual(norm('Técnico en prueba'),'TECNICO EN PRUEBA')
        self.assertNotEqual(norm('Técnico en prueba'),norm('Ingeniería en prueba'))

    def test_salida_diferente_no_sobrescrita(self):
        with TemporaryDirectory() as td:
            p=Path(td)/'salida.json'
            write_same(p,'ORIGINAL')
            with self.assertRaises(ValueError):
                write_same(p,'OTRA')
            self.assertEqual(p.read_text(),'ORIGINAL')


if __name__=='__main__':
    unittest.main(verbosity=2)
