"""Regresión DV cero sin ejecutar el pipeline ni alterar componentes congelados."""
import ast
from pathlib import Path
import re
import unittest

from common.diccionario_sies_seguimiento import rut_normalizado

ROOT = Path(__file__).resolve().parents[1]


def cargar_normalizador_puente():
    # Importar el script ejecutaría el pipeline: se ejecutan solo sus definiciones reales.
    tree = ast.parse((ROOT / 'scripts/reproducir_puente_20261023.py').read_text())
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'val', 'norm'}]
    if {n.name for n in funcs} != {'val', 'norm'}:
        raise AssertionError('No se encontraron ambas funciones originales')
    namespace = {'re': re}
    exec(compile(ast.Module(body=funcs, type_ignores=[]), '<normalizadores originales>', 'exec'), namespace)
    return namespace['norm']


class TestDVCero(unittest.TestCase):
    def test_diccionario_con_dv_cero(self):
        self.assertEqual(rut_normalizado('000001-0'), '1-0')

    def test_puente_con_dv_cero_numerico_y_texto(self):
        norm = cargar_normalizador_puente()
        for dv in (0, 0.0, '0'):
            with self.subTest(dv=dv):
                self.assertEqual(norm('000001', dv), '1-0')
        self.assertEqual(norm('000001-0'), '1-0')

    def test_puente_no_inventa_dv(self):
        self.assertIsNone(cargar_normalizador_puente()('000001', None))

if __name__ == '__main__':
    unittest.main()
