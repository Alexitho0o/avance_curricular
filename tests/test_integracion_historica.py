"""Controles H7 sobre copias temporales; no ejecuta flujos institucionales."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common import consulta_sies_historica as client
from scripts import exportar_consulta_historica as exporter


class IntegracionHistoricaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.temp.name) / 'consumidor aislado'
        cls.delivery = exporter.exportar(cls.repo)
        cls.package = cls.repo / 'gobernanza/sies/historico'
        cls.consumer = client.ConsultaHistorica(cls.package)
        cls.regular = dict(anio=2026, periodo='1', regimen='TRIMESTRAL', codcarpr='ILOG',
                           nombre_interno='INGENIERIA EN LOGISTICA', plan_umas='ILOG20241',
                           sede_umas='RE', jornada_umas='O')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_candidato_unico_no_asigna(self):
        result = self.consumer.consultar_umas(**self.regular)
        self.assertEqual(result['estado'], 'PENDIENTE_EVIDENCIA')
        self.assertEqual({c['codigo_unico'] for c in result['candidatos']}, {'I162S2C77J4V1'})
        self.assertIsNone(result['codigo_unico'])
        self.assertFalse(result['acredita_asignacion_individual'])

    def test_continuidad_no_escoge_version(self):
        query = dict(self.regular, codcarpr='CILOG', plan_umas='CILOG20241',
                     nombre_interno='CONTINUIDAD INGENIERIA LOGISTICA')
        result = self.consumer.consultar_umas(**query)
        self.assertEqual(result['estado'], 'PENDIENTE_EVIDENCIA')
        self.assertEqual({c['codigo_unico'] for c in result['candidatos']},
                         {'I162S2C77J4V1', 'I162S2C77J4V2'})
        self.assertIsNone(result['codigo_unico'])

    def test_anio_obligatorio(self):
        with self.assertRaises(TypeError):
            self.consumer.consultar_sies(codigo_unico='I162S2C77J4V1')

    def test_historico_no_hereda_candidatos_2026(self):
        result = self.consumer.consultar_umas(**dict(self.regular, anio=2025))
        self.assertEqual(result['estado'], 'SIN_EQUIVALENCIA')
        self.assertEqual(result['candidatos'], [])

    def test_2027_no_usa_catalogo_operativo(self):
        for result in (self.consumer.consultar_umas(**dict(self.regular, anio=2027)),
                       self.consumer.consultar_sies(anio=2027, codigo_unico='I162S2C77J4V1')):
            self.assertEqual(result['estado'], 'FUERA_AMBITO')
            self.assertIsNone(result['codigo_unico'])

    def test_claves_incompletas_no_se_completan(self):
        for field in ('periodo', 'regimen', 'nombre_interno', 'plan_umas', 'sede_umas', 'jornada_umas'):
            with self.subTest(field=field):
                result = self.consumer.consultar_umas(**dict(self.regular, **{field: None}))
                self.assertEqual(result['estado'], 'ENTRADA_INCOMPLETA')

    def test_sies_no_acredita_umas_y_nombre_literal(self):
        result = self.consumer.consultar_sies(anio=2026, codigo_unico='I162S2C77J4V2')
        self.assertEqual(result['estado'], 'OFERTA_ANUAL_LOCALIZADA')
        self.assertFalse(result['acredita_equivalencia_umas'])
        self.assertFalse(result['acredita_asignacion_individual'])
        master = json.loads((self.package / client.VERSION / 'maestro.json').read_text())
        row = next(r for r in master['oferta_anual'] if r['anio']==2026 and r['codigo_unico']=='I162S2C77J4V2')
        self.assertEqual(result['oferta_anual'], row)

    def test_mrun_sin_oferta_se_conserva(self):
        result = self.consumer.consultar_sies(anio=2008, codigo_unico='I162M2008N1')
        self.assertEqual(result['estado'], 'SIN_OFERTA_ANUAL')
        self.assertTrue(result['observaciones_mrun'])

    def test_lote_conserva_orden_repetidos_y_entrada(self):
        a = {'tipo':'UMAS', 'parametros':self.regular}
        b = {'tipo':'SIES', 'parametros':{'anio':2008, 'codigo_unico':'I162M2008N1'}}
        queries = [a,b,a]; before = copy.deepcopy(queries)
        result = self.consumer.consultar_lote(queries)
        self.assertEqual(result['cantidad_consultas'], 3)
        self.assertEqual([r['consulta'] for r in result['consultas']], before)
        self.assertEqual(queries, before)
        self.assertEqual(result['consultas'][0], result['consultas'][2])

    def test_lote_rechaza_columnas_personales_y_sin_anio(self):
        for params in ({'RUT':'dato no admitido', 'anio':2026}, {'codigo_unico':'I162S2C77J4V1'}):
            with self.assertRaises(ValueError):
                self.consumer.consultar_lote([{'tipo':'SIES', 'parametros':params}])

    def test_resultado_mutado_no_altera_sesion(self):
        result = self.consumer.consultar_umas(**self.regular)
        result['candidatos'][0]['codigo_unico'] = 'MUTADO'
        self.assertNotEqual(self.consumer.consultar_umas(**self.regular)['candidatos'][0]['codigo_unico'], 'MUTADO')

    def test_componentes_alterados_rechazados_antes_de_ejecutar(self):
        for filename in client.FILES | {client.DESCRIPTOR}:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp); exporter.exportar(repo)
                base = repo/'gobernanza/sies/historico'
                path = base/filename if filename==client.DESCRIPTOR else base/client.VERSION/filename
                path.write_bytes(path.read_bytes()+b'\n')
                with self.assertRaises(ValueError): client.ConsultaHistorica(base)

    def test_paquete_ausente_no_es_cobertura_cero(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(FileNotFoundError):
            client.ConsultaHistorica(tmp)

    def test_ruta_simbolica_externa_rechazada(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)/'repo'; exporter.exportar(repo)
            base=repo/'gobernanza/sies/historico'; path=base/client.VERSION/'resolutor.py'
            external=Path(tmp)/'external.py'; external.write_bytes(path.read_bytes())
            path.unlink(); path.symlink_to(external)
            with self.assertRaises(ValueError): client.ConsultaHistorica(base)

    def test_exportacion_idempotente(self):
        self.assertEqual(exporter.exportar(self.repo), self.delivery)

    def test_exportacion_conflictiva_no_escribe_parcial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); conflict=root/'scripts/consultar_sies_historico.py'
            conflict.parent.mkdir(); conflict.write_text('contenido previo')
            with self.assertRaises(ValueError): exporter.exportar(root)
            self.assertEqual(conflict.read_text(), 'contenido previo')
            self.assertEqual([p for p in root.rglob('*') if p.is_file()], [conflict])

    def test_fuente_h5_alterada_no_exporta(self):
        with patch.object(exporter, 'DESCRIPTOR_SHA256', '0'*64), tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): exporter.exportar(tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_cli_portable_aislado_y_codigos_salida(self):
        with tempfile.TemporaryDirectory() as cwd:
            for year,code,expected,state in ((2026,'I162S2C77J4V1',0,'OFERTA_ANUAL_LOCALIZADA'),
                                            (2027,'I162S2C77J4V1',2,'FUERA_AMBITO')):
                run=subprocess.run([sys.executable,'-I',str(self.repo/'scripts/consultar_sies_historico.py'),
                                    '--anio',str(year),'--codigo-unico',code], cwd=cwd,
                                   capture_output=True,text=True)
                self.assertEqual(run.returncode,expected,run.stderr)
                self.assertEqual(json.loads(run.stdout)['consultas'][0]['resultado']['estado'],state)


if __name__ == '__main__':
    unittest.main()
