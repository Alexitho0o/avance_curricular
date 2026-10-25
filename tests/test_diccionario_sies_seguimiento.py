"""Controles de no extrapolación de versiones; personas sintéticas, sin datos reales."""
import copy
import json
import sqlite3
import unittest
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, aplicar_adjudicaciones, rut_normalizado


class TestDiccionarioSeguimiento(unittest.TestCase):
    def setUp(self):
        self.d = DiccionarioSiesSeguimiento.__new__(DiccionarioSiesSeguimiento)
        self.d.edicion = 'PRUEBA_SINTETICA'
        self.d.db = sqlite3.connect(':memory:')
        self.d.db.executescript('''CREATE TABLE observaciones(persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload);
           CREATE TABLE mu_anual(persona,anio,payload);''')
        self.r = dict(observacion_id=1, persona='1-9', CODCLI='EXPEDIENTE_FICTICIO', plan='PLAN_FICTICIO',
                      codigo_documental_atribuible='I162S2C3J4V2', codigo_interno_adoptado='I162S2C3J4V2',
                      estado_interno='DOCUMENTAL', codigo_propuesto='I162S2C3J4V1', aceptacion_SIES='NO_ACREDITADA',
                      plan_efectivo_periodo='NO_ACREDITADO', regla='EXACTA', requisito_pendiente='Fecha efectiva')
        self.query = dict(persona='1-9', codcli='EXPEDIENTE_FICTICIO', plan='PLAN_FICTICIO', anio='2024', periodo='2')
        self.add(self.r)
        self.d.db.execute('INSERT INTO mu_anual VALUES (?,?,?)', ('1-9','2024',json.dumps({'codigo':'I162S2C3J4V2'})))

    def tearDown(self):
        self.d.close()

    def add(self, row, period='2', career='CARRERA_FICTICIA'):
        self.d.db.execute('INSERT INTO observaciones VALUES (?,?,?,?,?,?,?,?,?)',
            (row['persona'], row['CODCLI'], row['plan'], '2024', period, career, 'RE', '4', json.dumps(row)))

    def test_documental_no_reemplazado_por_propuesta(self):
        self.assertEqual(self.d.consultar(**self.query)['codigo_sies'], 'I162S2C3J4V2')

    def test_otro_periodo_no_hereda(self):
        self.assertEqual(self.d.consultar(**dict(self.query, periodo='3'))['motivo'], 'CONTEXTO_NO_LOCALIZADO')

    def test_otro_plan_no_hereda(self):
        self.assertIsNone(self.d.consultar(**dict(self.query, plan='OTRO_PLAN'))['codigo_sies'])

    def test_conflicto_no_elije_primera_version(self):
        row = dict(self.r, codigo_interno_adoptado='I162S2C3J4V3')
        self.d.db.execute('DELETE FROM observaciones'); self.add(row)
        self.assertEqual(self.d.consultar(**self.query)['motivo'], 'CONFLICTO_DOCUMENTAL_INTERNO')

    def test_varios_contextos_no_multiplican_persona(self):
        self.add(self.r, career='OTRA_CARRERA')
        self.assertEqual(self.d.consultar(**self.query)['motivo'], 'CONTEXTO_MULTIPLE')

    def test_codcli_con_varios_rut_bloquea(self):
        self.add(dict(self.r, persona='2-7'))
        self.assertEqual(self.d.consultar(**self.query)['motivo'], 'CODCLI_CON_VARIAS_IDENTIDADES')

    def test_correspondencia_aprobada_no_se_vuelve_documental(self):
        self.d.db.execute('DELETE FROM observaciones')
        self.add(dict(self.r, codigo_documental_atribuible='', estado_interno='CORRESPONDENCIA_INTERNA_APROBADA'))
        result = self.d.consultar(**self.query)
        self.assertEqual(result['nivel_respaldo'], 'D_CORRESPONDENCIA_INTERNA_APROBADA')
        self.assertIsNone(result['codigo_documental'])

    def test_codigo_origen_se_conserva_si_destino_cambia(self):
        self.add(dict(self.r, codigo_documental_atribuible='I162S2C3J4V3', codigo_interno_adoptado='I162S2C3J4V3'), period='3')
        target = dict(self.query, periodo='3', corte='T3', fuente_periodo='FUENTE_SINTETICA')
        target.pop('persona')
        result = self.d.seguir_cohorte(persona='1-9', anio_mu=2024, codigo_origen='I162S2C3J4V2', destinos=[target])[0]
        self.assertEqual(result['codigo_cohorte_origen'], 'I162S2C3J4V2')
        self.assertEqual(result['codigo_contexto_destino'], 'I162S2C3J4V3')
        self.assertTrue(result['version_distinta_observada'])

    def test_origen_no_documentado_rechazado(self):
        with self.assertRaises(ValueError):
            self.d.seguir_cohorte(persona='1-9', anio_mu=2024, codigo_origen='I162S2C3J4V1', destinos=[])

    def test_no_conversion_automatica_periodo_a_trimestre(self):
        target = dict(self.query, corte='T2'); target.pop('persona')
        with self.assertRaises(ValueError):
            self.d.seguir_cohorte(persona='1-9', anio_mu=2024, codigo_origen='I162S2C3J4V2', destinos=[target])

    def test_identidad_y_anio_estrictos(self):
        self.assertEqual(rut_normalizado('00.001-9'), '1-9')
        with self.assertRaises(ValueError):
            rut_normalizado('1')
        self.assertIsNone(self.d.consultar(**dict(self.query, anio='2025'))['codigo_sies'])

    def test_aprobacion_idempotente_y_con_estado_previo(self):
        before = dict(self.r, codigo_interno_adoptado='')
        op = {'observacion_id':1, 'estado_antes':before, 'estado_despues':self.r}
        self.assertEqual(aplicar_adjudicaciones([before],[op]), [self.r])
        self.assertEqual(aplicar_adjudicaciones([self.r],[op]), [self.r])
        bad = copy.deepcopy(op); bad['estado_despues']['codigo_documental_atribuible'] = 'I162S2C3J4V3'
        with self.assertRaises(ValueError):
            aplicar_adjudicaciones([before], [bad])


if __name__ == '__main__':
    unittest.main()
