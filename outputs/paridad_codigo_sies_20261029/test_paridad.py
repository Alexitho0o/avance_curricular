"""Controles de catálogo con ejemplos sintéticos, sin documentos personales."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import construir_paridad as p


def offer(version, tipo='1', duracion='8', vigencia='1', modalidad='3'):
    return 'I162S2C1J4V' + version, {'COD_TIPO_PLAN_CARRERA': tipo,
        'DURACION_TOTAL': duracion, 'VIGENCIA_CARRERA': vigencia, 'MODALIDAD': modalidad,
        'COD_NIVEL_GLOBAL': '1', 'NOMBRE_CARRERA': 'PROGRAMA SINTETICO'}


class Paridad(unittest.TestCase):
    def grupo(self, codes):
        return {'codigos_base': codes, 'familias': ['I162S2C1J4'], 'sede': 'RE', 'jornada': 'O'}

    def test_no_elegir_version_maxima(self):
        a, x = offer('1'); b, y = offer('9', vigencia='2')
        result = p.seleccionar(self.grupo([a, b]), {a: x, b: y}, {('8', '1')}, {'3'})
        self.assertEqual(result['seleccion'], a)

    def test_regular_no_se_mezcla_con_continuidad(self):
        a, x = offer('1'); b, y = offer('2', tipo='3', duracion='4')
        result = p.seleccionar(self.grupo([a, b]), {a: x, b: y}, {('4', '3')}, {'3'})
        self.assertEqual(result['seleccion'], b)

    def test_dos_versiones_compatibles_quedan_E(self):
        a, x = offer('1'); b, y = offer('2')
        self.assertEqual(p.seleccionar(self.grupo([a, b]), {a: x, b: y}, {('8', '1')}, {'3'})['estado'], 'E')

    def test_vigencia_dos_no_es_cierre(self):
        a, x = offer('1', vigencia='2')
        self.assertEqual(p.seleccionar(self.grupo([a]), {a: x}, {('8', '1')}, {'3'})['estado'], 'SIN_NUEVOS')

    def test_no_transferir_jornada(self):
        a, x = offer('1'); g = self.grupo([a]); g['jornada'] = 'V'
        self.assertEqual(p.seleccionar(g, {a: x}, {('8', '1')}, {'3'})['estado'], 'E')
        self.assertNotIn('3', p.JORNADAS.values())

    def test_no_transferir_modalidad(self):
        a, x = offer('1')
        self.assertEqual(p.seleccionar(self.grupo([a]), {a: x}, {('8', '1')}, {'1'})['estado'], 'E')

    def test_version_fuera_del_vinculo_requiere_D(self):
        a, x = offer('1'); b, y = offer('2')
        self.assertEqual(p.seleccionar(self.grupo([a]), {b: y}, {('8', '1')}, {'3'})['estado'], 'E')

    def test_no_excluir_continuidad_pregrado(self):
        _, x = offer('2', tipo='3', duracion='4')
        self.assertFalse(p.fuera(x)); x['NOMBRE_CARRERA'] = 'DIPLOMADO SINTETICO'
        self.assertTrue(p.fuera(x))

    def test_codigo_completo_y_duplicados(self):
        self.assertEqual(p.componentes('I162S3C114J2V1')['cod_sede'], '3')
        with self.assertRaises(ValueError): p.componentes('114')
        row = {'COD_SEDE': '2', 'COD_CARRERA': '1', 'COD_JORNADA': '4', 'VERSION': '1'}
        with self.assertRaises(ValueError): p.indexar_oferta([row, row])

    def test_rechazo_fuente_alterada_sin_escritura(self):
        original = Path.read_bytes
        def altered(path):
            data = original(path)
            return data + b' ' if str(path).endswith('20261016/historias_oferta.json') else data
        with patch.object(Path, 'read_bytes', altered):
            with self.assertRaisesRegex(ValueError, 'Fuente alterada'): p.construir()

    def test_reproducibilidad_y_controles_reales(self):
        a, qa = p.construir(); b, _ = p.construir()
        self.assertEqual(a, b); self.assertTrue(all(qa['controles'].values()))
        self.assertEqual(qa['filas'], 267)


if __name__ == '__main__':
    unittest.main(verbosity=2)
