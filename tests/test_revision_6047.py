"""La revision usa evidencia exacta, no semejanza ni version mayor."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from common.catalogos_sies import resolver_catalogo
from scripts.revisar_equivalencias_6047 import cruzar
from test_catalogos_sies import catalogo, fuente


def dimension(name="CARRERA PRUEBA", **changes):
    return dict({"dimension_id": 1, "codcarpr": "LOCAL", "nombre_interno": name,
                 "sede": "2", "jornada": "4", "registros_por_ano_matricula": {"2027": 1}}, **changes)


def base_catalog(*rows):
    return dict(catalogo(*rows, year=2027), resumen={})


class RevisionTest(unittest.TestCase):
    def test_revision_real_reproducible_sin_datos_personales(self):
        root = Path(__file__).resolve().parents[1] / 'data/catalogos_sies/2027'
        release = root / '5910_20260907_6047_20261013'
        base = json.loads((root / '5910_20260907/catalogo.json').read_text())
        evidence = json.loads((release / 'EVIDENCIA_DIMENSIONES.json').read_text())
        saved = json.loads((release / 'REVISION_EQUIVALENCIAS.json').read_text())
        catalog = json.loads((release / 'catalogo.json').read_text())
        report = {r['codigo_unico']: r for r in evidence['oferta_6047_reducida']}
        updated, audit = cruzar(base, report, evidence['dimensiones'], saved['evidencia'])
        self.assertEqual(audit['resumen_revision'], {'COMPLETADA': 17, 'PENDIENTE_VERSION_AMBIGUA': 6, 'PENDIENTE_SIN_CRUCE_EXACTO': 29})
        self.assertEqual(len(audit['revision_52_originales']), 52)
        self.assertEqual(updated['oferta'], catalog['oferta'])
        self.assertEqual(updated['ambiguedades_cruce'], catalog['ambiguedades_cruce'])
        self.assertEqual(audit['revision_52_originales'], saved['revision_52_originales'])
        self.assertEqual(len(audit['diplomados_fuera_de_alcance']), 21)
        self.assertFalse(evidence['datos_personales_incluidos'])
        allowed = {'dimension_id', 'codcarpr', 'nombre_interno', 'sede_interna', 'jornada_interna', 'sede', 'jornada', 'registros_por_ano_matricula'}
        self.assertTrue(all(set(d) <= allowed for d in evidence['dimensiones']))

    def test_exacta_unica_agrega_equivalencia(self):
        base = base_catalog(fuente(2027))
        updated, audit = cruzar(base, {r["codigo_unico"]: r for r in base["oferta"]}, [dimension()], {})
        self.assertEqual(audit["resumen_revision"], {"COMPLETADA": 1})
        self.assertFalse(base["oferta"][0]["equivalencias"])
        self.assertEqual(resolver_catalogo(updated, codcarpr="LOCAL", sede="RE", jornada="O")["estado"], "RESUELTO")

    def test_no_fuzzy_sp_ni_otra_sede_jornada(self):
        base = base_catalog(fuente(2027))
        for d in [dimension(name="CARRERA PRUEBA SP"), dimension(sede="3"), dimension(jornada="3")]:
            with self.subTest(d=d):
                updated, audit = cruzar(base, {r["codigo_unico"]: r for r in base["oferta"]}, [d], {})
                self.assertEqual(audit["resumen_revision"], {"PENDIENTE_SIN_CRUCE_EXACTO": 1})
                self.assertFalse(updated["oferta"][0]["equivalencias"])

    def test_version_ambigua_no_hereda_falsa_certeza(self):
        base = base_catalog(fuente(2027), fuente(2027, version="2"))
        base["oferta"][0]["equivalencias"] = [{"codcarpr": "LOCAL", "nombre_interno": "Carrera prueba"}]
        updated, audit = cruzar(base, {r["codigo_unico"]: r for r in base["oferta"]}, [dimension()], {})
        result = resolver_catalogo(updated, codcarpr="LOCAL", sede="RE", jornada="O", nombre="Carrera prueba")
        self.assertEqual(result["estado"], "AMBIGUO")
        self.assertEqual(result["codigo_unico"], "")
        self.assertEqual(len(result["candidatos"]), 2)
        self.assertEqual(result["modalidad"], "No presencial")
        self.assertEqual(result["estado_codigo_sies"], "AMBIGUO")
        self.assertEqual(result["estado_modalidad"], "RESUELTA_COINCIDENCIA_CANDIDATOS")
        self.assertEqual(audit["resumen_revision"], {"PENDIENTE_VERSION_AMBIGUA": 1})

    def test_cambio_fuente_6047_no_se_acepta(self):
        base = base_catalog(fuente(2027))
        report = {r["codigo_unico"]: deepcopy(r) for r in base["oferta"]}
        next(iter(report.values()))["modalidad_codigo"] = "1"
        with self.assertRaises(ValueError):
            cruzar(base, report, [dimension()], {})

    def test_no_revisa_2026(self):
        with self.assertRaises(ValueError):
            cruzar(catalogo(fuente()), {}, [], {})

    def test_diplomado_adicional_no_se_agrega_a_oferta(self):
        base = base_catalog(fuente(2027))
        report = {r["codigo_unico"]: deepcopy(r) for r in base["oferta"]}
        other = deepcopy(base["oferta"][0])
        other["codigo_unico"] = "I162S2C90J4V1"
        other["nombres_fuente"] = ["DIPLOMADO EN PRUEBAS"]
        report[other["codigo_unico"]] = other
        updated, audit = cruzar(base, report, [dimension()], {})
        self.assertEqual(len(updated["oferta"]), 1)
        self.assertEqual(audit["diplomados_fuera_de_alcance"], [other["codigo_unico"]])
        other["nombres_fuente"] = ["PROGRAMA SIN RESPALDO"]
        with self.assertRaises(ValueError):
            cruzar(base, report, [], {})


if __name__ == "__main__":
    unittest.main()
