"""Pruebas con catálogo ficticio: sin documentos ni personas reales."""
import io
import csv
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruzar_planes_2027 as p
from revisar_casos import text, identidad, vinculo_unico


class CrucePlanes(unittest.TestCase):
    def plan(self, **kwargs):
        row = dict(zip(p.HEADER, ['PROGRAMA_FICTICIO', 'PLAN_FICTICIO', 'PROGRAMA DE PRUEBA',
                   'RE', 'O', '3', '4', '1', 'SI']))
        row.update(kwargs)
        return row

    def target(self):
        return {'codigo_unico': 'I162S2C999J4V1', 'nombre_carrera': 'PROGRAMA DE PRUEBA',
                'cod_sede': '2', 'cod_jornada': '4', 'modalidad_codigo': '3',
                'duracion_total_semestres': '4', 'tipo_plan_codigo': '1', 'vigencia_2027': '1'}

    def test_candidato_ficticio_no_aprobado(self):
        r = p.proponer([self.plan()], [self.target()])[0]
        self.assertEqual(len(r['candidatos']), 1)
        self.assertFalse(r['eleccion_automatica']); self.assertFalse(r['tabla_H002_modificada'])

    def test_nombre_solo_no_basta(self):
        self.assertFalse(p.proponer([self.plan(DURACION_SEMESTRES='8')], [self.target()])[0]['candidatos'])

    def test_nombre_no_es_selector(self):
        r = p.proponer([self.plan(NOMBRE_PLAN='OTRO NOMBRE FICTICIO')], [self.target()])[0]
        self.assertEqual(r['candidatos'][0]['apoyo_nombre'], 'NOMBRE_DISTINTO_REVISAR')

    def test_j3_no_se_transforma_en_O(self):
        self.assertFalse(p.proponer([self.plan(JORNADA='3')], [self.target()])[0]['candidatos'])

    def test_regular_no_continuidad(self):
        self.assertFalse(p.proponer([self.plan(TIPO_PLAN='3')], [self.target()])[0]['candidatos'])

    def test_encabezado_exacto(self):
        raw = ('\t'.join(p.HEADER) + '\n').encode()
        self.assertEqual(p.parse(raw), [])
        with self.assertRaises(ValueError): p.parse(raw.replace(b'CODIGO_PLAN', b'PLAN'))

    def test_no_elegir_primero_ni_nombre(self):
        candidates = p.proponer([self.plan(), self.plan(CODIGO_PLAN='SEGUNDO_PLAN_FICTICIO')], [self.target()])[0]
        self.assertEqual(len(candidates['candidatos']), 2); self.assertFalse(candidates['eleccion_automatica'])

    def test_duplicados_bloquean(self):
        out = io.StringIO(); w = csv.DictWriter(out, fieldnames=p.HEADER, delimiter='\t');w.writeheader();w.writerow(self.plan());w.writerow(self.plan())
        with self.assertRaises(ValueError): p.parse(out.getvalue().encode())

    def test_cero_no_se_pierde(self):
        self.assertEqual(text(0), '0')
        with patch('revisar_casos.rut_normalizado', return_value='LLAVE_FICTICIA') as fn:
            self.assertEqual(identidad({'TIPO_DOC': 'R', 'N_DOC': 'DOCUMENTO_FICTICIO', 'DV': 0}), 'LLAVE_FICTICIA')
            fn.assert_called_once_with('DOCUMENTO_FICTICIO-0')

    def test_contextos_repetidos_no_multiplican_matricula(self):
        rec = ('EXPEDIENTE_FICTICIO', 'PLAN_FICTICIO', 'B/C_DOCUMENTAL_ANUAL')
        self.assertEqual(vinculo_unico([rec, rec, rec]), ('PLAN_FICTICIO', 'B/C_DOCUMENTAL_ANUAL'))

    def test_dos_expedientes_no_se_asignan_a_ciegas(self):
        self.assertIsNone(vinculo_unico([('EXPEDIENTE_UNO', 'PLAN_FICTICIO', 'B/C_DOCUMENTAL_ANUAL'),
                                        ('EXPEDIENTE_DOS', 'PLAN_FICTICIO', 'B/C_DOCUMENTAL_ANUAL')]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
