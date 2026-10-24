"""Pruebas sin estudiantes: rechazo de alteraciones y preservación histórica."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from common import control_reglas_mu2027 as c


class TestControlMU2027(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.reg = self.root / 'registro'
        self.rules = {'proceso': 'MU', 'anio': 2027, 'modo': 'REVISION_INTERNA',
            'equivalencias': [{'estado_umas': 'ELIMINADO', 'situacion_umas': '1 - ALUMNO REGULAR',
                              'resultado': 0, 'clasificacion': 'D'}]}
        self.auth = {'responsable': 'Responsable sintético QA', 'motivo': 'Prueba aislada',
            'referencia_autorizacion': 'Fixture no productivo', 'decision_textual': 'Regla sintética',
            'fecha_registro': c.ahora()}
        self.first = c.registrar(self.reg, 'v1', self.rules, self.auth, 'Prueba automatizada')

    def test_version_and_exact_match(self):
        out = c.consultar('ELIMINADO', '1 - ALUMNO REGULAR', self.reg)
        self.assertEqual((out['resultado'], out['clasificacion']), (0, 'D'))
        out = c.consultar('ELIMINADO', '1', self.reg)
        self.assertEqual((out['resultado'], out['clasificacion']), ('PENDIENTE', 'E'))

    def test_direct_edit_blocks_and_alerts(self):
        (self.reg / 'versiones/v1/reglas.json').write_text('{}')
        n = len(list((self.reg / 'alertas').glob('*.json')))
        with self.assertRaises(c.Bloqueo): c.verificar(self.reg)
        self.assertEqual(len(list((self.reg / 'alertas').glob('*.json'))), n+1)

    def test_missing_responsible_blocks(self):
        auth = {**self.auth, 'responsable': ''}
        with self.assertRaises(c.Bloqueo):
            c.registrar(self.reg, 'v2', self.rules, auth, 'Prueba', self.first['manifest_sha256'])
        self.assertFalse((self.reg / 'versiones/v2').exists())

    def test_stale_version_blocks(self):
        with self.assertRaises(c.Bloqueo):
            c.registrar(self.reg, 'v2', self.rules, self.auth, 'Prueba', '0'*64)

    def test_new_version_preserves_reproduction(self):
        old_bytes = (self.reg / 'versiones/v1/reglas.json').read_bytes()
        rules = copy.deepcopy(self.rules)
        rules['equivalencias'][0]['resultado'] = 1
        c.registrar(self.reg, 'v2', rules, self.auth, 'Prueba', self.first['manifest_sha256'])
        self.assertEqual(c.consultar('ELIMINADO', '1 - ALUMNO REGULAR', self.reg)['resultado'], 1)
        self.assertEqual(c.consultar('ELIMINADO', '1 - ALUMNO REGULAR', self.reg, 'v1',
                                    self.first['manifest_sha256'])['resultado'], 0)
        self.assertEqual((self.reg / 'versiones/v1/reglas.json').read_bytes(), old_bytes)
        alert = c.leer(self.reg / 'versiones/v2/alerta.json')
        self.assertEqual(len(alert['diferencias']), 1)
        self.assertEqual(alert['responsable'], self.auth['responsable'])
        self.assertIsNotNone(c.datetime.fromisoformat(alert['fecha_hora']).tzinfo)

    def test_history_tampering_blocks_latest(self):
        c.registrar(self.reg, 'v2', self.rules, self.auth, 'Prueba', self.first['manifest_sha256'])
        (self.reg / 'versiones/v1/autorizacion.json').write_text('{}')
        with self.assertRaises(c.Bloqueo): c.verificar(self.reg)

    def test_carga_sies_blocks(self):
        with self.assertRaises(c.Bloqueo): c.verificar(self.reg, carga_sies=True)

    def test_duplicate_and_wrong_year_block(self):
        for rules in ({**self.rules, 'anio': 2026},
                      {**self.rules, 'equivalencias': self.rules['equivalencias']*2}):
            with self.assertRaises(c.Bloqueo): c.validar_reglas(rules)

    def test_no_aplica_never_zero(self):
        rules = copy.deepcopy(self.rules)
        rules['equivalencias'][0]['resultado'] = 'NO APLICA'
        c.registrar(self.reg, 'v2', rules, self.auth, 'Prueba', self.first['manifest_sha256'])
        self.assertEqual(c.consultar('ELIMINADO', '1 - ALUMNO REGULAR', self.reg)['resultado'], 'NO APLICA')

    def test_execution_trace_cannot_overwrite(self):
        a, b = self.root/'entrada.txt', self.root/'salida.txt'
        a.write_text('datos sintéticos'); b.write_text('resultado sintético')
        dest = self.root/'run.json'
        r = c.ejecucion(dest, [a], [b], 'Responsable QA', {'anio':2027},
                        self.reg, 'v1', self.first['manifest_sha256'])
        self.assertEqual(r['entradas'][0]['sha256'], c.sha(a))
        self.assertEqual(r['manifest_sha256'], self.first['manifest_sha256'])
        with self.assertRaises(FileExistsError):
            c.ejecucion(dest, [a], [b], 'Responsable QA', {'anio':2027},
                        self.reg, 'v1', self.first['manifest_sha256'])


if __name__ == '__main__': unittest.main()
