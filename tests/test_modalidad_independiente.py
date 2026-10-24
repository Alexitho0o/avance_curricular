"""Modalidad unanime no significa version SIES identificada."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common.catalogos_sies import json_bytes, resolver_catalogo, sha256
from scripts.exportar_catalogo_caracterizacion import exportar
from test_catalogos_sies import catalogo, fuente


def annual(*rows):
    cat = catalogo(*rows, year=2027)
    for row in cat['oferta']:
        row['equivalencias'] = [{'codcarpr':'LOCAL', 'nombre_interno':name} for name in row['nombres_fuente']]
    return cat


class ModalidadTest(unittest.TestCase):
    def resolve(self, cat, **kwargs):
        return resolver_catalogo(cat, codcarpr='LOCAL', sede='RE', jornada='O', **kwargs)

    def test_unanimidad_no_asigna_codigo_y_conserva_candidatos(self):
        cat = annual(fuente(2027), fuente(2027,version='2',COD_TIPO_PLAN_CARRERA='3'))
        before = deepcopy(cat)
        result = self.resolve(cat)
        self.assertEqual(result['estado_codigo_sies'], 'AMBIGUO')
        self.assertEqual(result['estado_modalidad'], 'RESUELTA_COINCIDENCIA_CANDIDATOS')
        self.assertEqual(result['modalidad'], 'No presencial')
        self.assertEqual(result['codigo_unico'], '')
        self.assertEqual(len(result['candidatos']), 2)
        self.assertEqual(cat, before)

    def test_modalidad_diferente_no_usa_mayoria(self):
        cat = annual(fuente(2027), fuente(2027,version='2'), fuente(2027,version='3',MODALIDAD='2'))
        result = self.resolve(cat)
        self.assertEqual(result['estado_modalidad'], 'AMBIGUA')
        self.assertEqual(result['modalidad'], 'No determinada')
        self.assertEqual(result['modalidad_codigo'], '')
        self.assertEqual(result['codigo_unico'], '')

    def test_codigo_unico_y_sin_equivalencia(self):
        cat = annual(fuente(2027), fuente(2027,version='2'))
        result = self.resolve(cat, version='2')
        self.assertEqual(result['estado_modalidad'], 'RESUELTA_CODIGO_UNICO')
        self.assertEqual(result['estado_codigo_sies'], 'RESUELTO')
        result = self.resolve(cat, nombre='NOMBRE SIN RESPALDO')
        self.assertEqual(result['estado_modalidad'], 'SIN_EQUIVALENCIA')
        self.assertEqual(result['modalidad'], 'No determinada')

    def test_modalidad_invalida_o_inconsistente_es_error(self):
        for code, label in [('9','Desconocida'), ('3','Presencial')]:
            cat = annual(fuente(2027))
            cat['oferta'][0].update(modalidad_codigo=code, modalidad=label)
            with self.subTest(code=code), self.assertRaises(ValueError):
                self.resolve(cat)

    def test_2026_conserva_contrato_anterior(self):
        cat = catalogo(fuente(alias='LOCAL'), fuente(version='2',alias='LOCAL'))
        result = self.resolve(cat)
        self.assertEqual(result['modalidad'], 'No determinada')
        self.assertNotIn('estado_modalidad',result)
        self.assertNotIn('estado_codigo_sies',result)

    def test_nombre_acota_candidatos_antes_de_informar_modalidad(self):
        cat = annual(fuente(2027), fuente(2027,version='2',NOMBRE_CARRERA='OTRA CARRERA',MODALIDAD='1'))
        result = self.resolve(cat, nombre='Carrera prueba')
        self.assertEqual(result['modalidad'], 'No presencial')
        self.assertEqual(result['estado_modalidad'], 'RESUELTA_CODIGO_UNICO')

    def test_modalidad_procede_de_columna_no_del_nombre_o_jornada(self):
        for modalidad, label in [('1', 'Presencial'), ('2', 'Semipresencial')]:
            cat = annual(fuente(2027, jornada='2', NOMBRE_CARRERA='Carrera SP', MODALIDAD=modalidad))
            result = resolver_catalogo(cat, codcarpr='LOCAL', sede='RE', jornada='V')
            with self.subTest(modalidad=modalidad):
                self.assertEqual(result['modalidad_codigo'], modalidad)
                self.assertEqual(result['modalidad'], label)

    def test_sufijo_sp_no_crea_equivalencia(self):
        cat = annual(fuente(2027, jornada='3', MODALIDAD='2'))
        result = resolver_catalogo(cat, codcarpr='LOCALSP', sede='RE', jornada='V')
        self.assertEqual(result['candidatos'], [])
        self.assertEqual(result['modalidad'], 'No determinada')
        self.assertEqual(result['estado_codigo_sies'], 'SIN_EQUIVALENCIA')

    def test_promocion_consumidor_exige_hash_y_respalda_anterior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data, dest = root/'fuente', root/'cliente'
            def seed(version):
                folder = data/'2027'/version
                folder.mkdir(parents=True)
                cat = {'anio':2027,'version':version,'revision_equivalencias':{}}
                for filename in ('catalogo.json','EVIDENCIA_DIMENSIONES.json','REVISION_EQUIVALENCIAS.json'):
                    (folder/filename).write_bytes(json_bytes(cat if filename=='catalogo.json' else {}))
                return cat
            old = seed('v1')
            new = seed('v2')
            with patch('scripts.exportar_catalogo_caracterizacion.DATA',data), patch('scripts.exportar_catalogo_caracterizacion.cargar_catalogo',return_value=old):
                exportar(dest)
            pointer = dest/'gobernanza/sies/anual/ACTIVO_2027.json'
            original = pointer.read_bytes()
            digest = sha256(pointer)
            with patch('scripts.exportar_catalogo_caracterizacion.DATA',data), patch('scripts.exportar_catalogo_caracterizacion.cargar_catalogo',return_value=new):
                for wrong in (None,'incorrecto'):
                    with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                        exportar(dest,expected_descriptor_sha256=wrong)
                    self.assertEqual(pointer.read_bytes(),original)
                    self.assertFalse((pointer.parent/'2027/v2').exists())
                exportar(dest,expected_descriptor_sha256=digest)
                exportar(dest)
            self.assertEqual(json.loads(pointer.read_text())['version'],'v2')
            self.assertEqual((pointer.parent/'2027/v2/ACTIVO_ANTERIOR.json').read_bytes(),original)
            self.assertTrue((pointer.parent/'2027/v1/catalogo.json').exists())


if __name__ == '__main__':
    unittest.main()
