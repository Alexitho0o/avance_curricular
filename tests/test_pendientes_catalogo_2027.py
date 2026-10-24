"""Las sugerencias nominales no son equivalencias autorizadas."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from common.catalogos_sies import cargar_catalogo, resolver_catalogo, sha256
from scripts.auditar_pendientes_catalogo_2027 import candidatos_para_revision, markdown

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/catalogos_sies/auditorias/20261013_pendientes_52/REVISION_PENDIENTES.json"


class PendientesTest(unittest.TestCase):
    def setUp(self):
        self.catalog = cargar_catalogo(2027)

    def test_candidato_nominal_unico_no_se_aplica(self):
        row = {"CODCARPR": "ICONSSP", "NOMBRE_L": "INGENIERIA EN CONSTRUCCION SP", "SEDE": "RE", "JORNADA": "V"}
        before = deepcopy(self.catalog)
        state, candidates = candidatos_para_revision(row, self.catalog)
        self.assertEqual(state, "CANDIDATO_NOMINAL_UNICO_NO_APLICADO")
        self.assertEqual([r["codigo_unico"] for r in candidates], ["I162S2C132J3V1"])
        result = resolver_catalogo(self.catalog, codcarpr=row["CODCARPR"], sede="RE", jornada="V")
        self.assertEqual(result["estado_codigo_sies"], "SIN_EQUIVALENCIA")
        self.assertEqual(result["modalidad"], "No determinada")
        self.assertEqual(self.catalog, before)

    def test_enfermeria_conserva_todas_las_modalidades_de_oferta(self):
        state, rows = candidatos_para_revision({"NOMBRE_L": "TECNICO EN ENFERMERIA SP", "SEDE": "CO"}, self.catalog)
        self.assertEqual(state, "VARIAS_MODALIDADES_NO_APLICADAS")
        self.assertEqual({r["modalidad_codigo"] for r in rows}, {"1", "2"})
        self.assertEqual({r["sede"] for r in rows}, {"3"})
        self.assertEqual(len(rows), 3)

    def test_nombre_veterinario_es_propuesta_no_homologacion(self):
        state, rows = candidatos_para_revision({"NOMBRE_L": "TECNICO VETERINARIO SP", "SEDE": "RE"}, self.catalog)
        self.assertEqual(state, "NOMBRE_AMPLIADO_NO_APLICADO")
        self.assertEqual(rows[0]["codigo_unico"], "I162S2C143J3V1")
        result = resolver_catalogo(self.catalog, codcarpr="TVETSP", sede="RE", jornada="V")
        self.assertEqual(result["candidatos"], [])

    def test_gestion_no_se_equipara_con_control_o_ingenieria(self):
        state, rows = candidatos_para_revision({"NOMBRE_L": "TECNICO EN GESTION INDUSTRIAL", "SEDE": "RE"}, self.catalog)
        self.assertEqual(state, "SIN_COINCIDENCIA_NOMINAL")
        self.assertEqual(rows, [])

    def test_auditoria_real_concilia_52_en_14_sin_asignar(self):
        report = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(report["registros_revisados"], 52)
        self.assertEqual(report["codigos_internos_revisados"], 14)
        self.assertEqual(sorted(report["por_motivo"].values()), [1, 14, 16, 21])
        self.assertEqual(sum(r["registros"] for r in report["casos"]), 52)
        self.assertEqual(report["equivalencias_aplicadas"], [])
        self.assertTrue(all(not r["codigo_sies_asignado"] and r["modalidad_asignada"] == "No determinada"
                            for r in report["casos"]))
        self.assertTrue(all(not report["fuentes"][k]["codigos_pendientes_encontrados"]
                            for k in ("duracion", "puente", "dic_carreras")))

    def test_casos_no_contienen_datos_personales(self):
        report = json.loads(AUDIT.read_text(encoding="utf-8"))
        allowed = {"CODCARPR", "NOMBRE_L", "SEDE", "JORNADA", "registros", "estado_revision",
                   "candidatos_no_aplicados", "codigo_sies_asignado", "modalidad_asignada",
                   "falta", "coincidencias_diccionarios_codcarpr"}
        for row in report["casos"]:
            self.assertEqual(set(row), allowed)

    def test_tabla_incluye_nombre_literal_de_datosalumnos(self):
        report = json.loads(AUDIT.read_text(encoding="utf-8"))
        rendered = markdown(report)
        self.assertIn("| Registros | NOMBRE_L (DatosAlumnos) |", rendered)
        for row in report["casos"]:
            with self.subTest(codcarpr=row["CODCARPR"]):
                self.assertIn(
                    f"| {row['CODCARPR']} | {row['SEDE']} | {row['registros']} | {row['NOMBRE_L']} |",
                    rendered,
                )
        saved = AUDIT.with_suffix(".md").read_text(encoding="utf-8")
        self.assertEqual(
            [line for line in rendered.splitlines() if line.startswith("|")],
            [line for line in saved.splitlines() if line.startswith("|")],
        )

    def test_referencias_congeladas_permanecen_intactas(self):
        report = json.loads(AUDIT.read_text(encoding="utf-8"))
        for path, digest in report["referencias_2026_verificadas"].items():
            with self.subTest(path=path):
                self.assertEqual(sha256(ROOT / path), digest)


if __name__ == "__main__":
    unittest.main()
