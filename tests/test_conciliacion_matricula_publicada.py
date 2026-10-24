"""Pruebas con fuentes sinteticas: sin datos personales ni ejecucion del motor."""
import csv
import tempfile
import unittest
from pathlib import Path

import openpyxl

from common.catalogos_sies import json_bytes
from scripts.conciliar_matricula_publicada import (POST_COLUMNS, PRE_COLUMNS, conciliar,
                                                  entero, leer_postitulo, leer_pregrado,
                                                  leer_publicacion, resumir)


def registro(doc="99900001", vig="1", **updates):
    row = dict.fromkeys(PRE_COLUMNS, "")
    row.update(TIPO_DOC="R", N_DOC=doc, DV="K", VIG=vig, MODALIDAD="3", COD_SED="2")
    return dict(row, **updates)


def xlsx(path, name, rows):
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = name
    for row in rows:
        sheet.append(row)
    book.save(path)
    book.close()


def publicacion(path, pre=3, post=1, total=4, posgrado=None, duplicates=False):
    header = ["Nombre de la institucion", "Codigo institucional", "Matricula Total Pregrado 2026",
              "Matricula Total Posgrado 2026", "Matricula Total Postitulo 2026", "Matricula Total 2026"]
    row = ["IP SAN SEBASTIAN", 162, pre, posgrado, post, total]
    xlsx(path, "Listado de instituciones 2026", [[], [], header, row] + ([row] if duplicates else []))


class ConciliacionTest(unittest.TestCase):
    def test_no_reemplazar_nulos_ni_fracciones_por_cero(self):
        for value in (None, "", "nan", float("inf"), True, -1, 1.1, "texto"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                entero(value)
        self.assertEqual(entero("1.0"), 1)
        self.assertEqual(entero(0), 0)

    def test_registros_personas_y_vigencia_son_distintos(self):
        rows = [registro(), registro(vig="2"), registro("99900002", "0")]
        r = resumir(rows)
        self.assertEqual(r["registros"], 3)
        self.assertEqual(r["vig"], {"0": 1, "1": 1, "2": 1})
        self.assertEqual(r["matriculas_comparables"], 2)
        self.assertEqual(r["personas_comparables"], 1)
        self.assertEqual(r["matriculas_adicionales_respecto_personas"], 1)
        self.assertEqual(r["matriculas_por_modalidad"], {"3": 2})
        self.assertNotIn(b"99900001", json_bytes(r))

    def test_fuente_vacia_vigencia_desconocida_e_identidad_incompleta(self):
        for rows in ([], [registro(vig="9")], [registro(doc="")], [registro(MODALIDAD="9")]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                resumir(rows)

    def test_documentos_se_conservan_como_identificadores(self):
        r = resumir([registro(doc=99900001.0), registro(doc="99900001"),
                     registro(doc="EXTERNO-A", TIPO_DOC="P")])
        self.assertEqual(r["personas_comparables"], 2)
        self.assertEqual(r["matriculas_comparables"], 3)

    def test_validacion_encabezados_pregrado(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pre.xlsx"
            row = registro()
            xlsx(path, "CONSOLIDADO", [PRE_COLUMNS, [row[k] for k in PRE_COLUMNS]])
            self.assertEqual(len(leer_pregrado(path)), 1)
            xlsx(path, "CONSOLIDADO", [list(reversed(PRE_COLUMNS))])
            with self.assertRaises(ValueError):
                leer_pregrado(path)
            xlsx(path, "CONSOLIDADO", [PRE_COLUMNS + ["EXTRA"]])
            with self.assertRaises(ValueError):
                leer_pregrado(path)

    def test_postitulo_no_acepta_layout_pregrado(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "post.csv"
            for columns in (PRE_COLUMNS, POST_COLUMNS):
                with path.open("w", newline="", encoding="utf-8") as stream:
                    csv.writer(stream, delimiter=";").writerow(columns)
                with self.assertRaises(ValueError):
                    leer_postitulo(path)

    def test_posgrado_vacio_conservado_y_localizador(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "publicacion.xlsx"
            publicacion(path)
            r = leer_publicacion(path, 2026)
            self.assertIsNone(r["posgrado"])
            self.assertTrue(r["celda_posgrado_vacia"])
            self.assertEqual(r["localizador"], "B4:F4")
            publicacion(path, posgrado=0)
            self.assertEqual(leer_publicacion(path, 2026)["posgrado"], 0)

    def test_publicacion_duplicada_o_incoherente(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "publicacion.xlsx"
            for kwargs in ({"duplicates": True}, {"total": 7}, {"pre": None}):
                publicacion(path, **kwargs)
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    leer_publicacion(path, 2026)

    def test_rechaza_otro_ano_antes_de_leer(self):
        with self.assertRaises(ValueError):
            conciliar(Path("pre"), Path("post"), Path("pub"), anio=2027, fecha="2026-10-13")

    def test_conciliacion_no_identifica_personas_ni_certifica_carga(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pre, post, pub = root / "pre.xlsx", root / "post.csv", root / "pub.xlsx"
            row = registro()
            xlsx(pre, "CONSOLIDADO", [PRE_COLUMNS, [row[k] for k in PRE_COLUMNS]])
            with post.open("w", encoding="utf-8", newline="") as stream:
                csv.writer(stream, delimiter=";").writerow([row[k] for k in POST_COLUMNS])
            publicacion(pub, pre=3, post=1, total=4)
            report = conciliar(pre, post, pub, anio=2026, fecha="2026-10-13")
            self.assertEqual(report["estado"], "DISCREPANCIA_NO_EXPLICADA")
            self.assertEqual(report["diferencia_publicacion_menos_institucional"], {"pregrado": 2, "postitulo": 0, "total": 2})
            self.assertNotIn(b"99900001", json_bytes(report))
            self.assertTrue(all(len(s["sha256"]) == 64 for s in report["fuentes"].values()))
            publicacion(pub, pre=1, post=1, total=2)
            report = conciliar(pre, post, pub, anio=2026, fecha="2026-10-13")
            self.assertEqual(report["estado"], "COINCIDENCIA_AGREGADA_NO_CERTIFICA_CARGA")


if __name__ == "__main__":
    unittest.main()
