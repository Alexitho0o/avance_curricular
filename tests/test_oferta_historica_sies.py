"""Controles sintéticos del contrato H3, sin fuentes reales ni escritura Excel."""
import csv
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SPEC = spec_from_file_location(
    "oferta_historica_sies",
    Path(__file__).parents[1] / "scripts/reconstruir_oferta_historica_sies.py",
)
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def offer(year=2026, code="I162S2C1J1V1", record=2, **fields):
    """Una fila de oferta ficticia; las dimensiones se declaran explícitamente."""
    row = {
        "ANO": f"OFE_{year}", "CODIGO_UNICO": code,
        "CODIGO_IES": "162", "CODIGO_SEDE": "2", "CODIGO_CARRERA": "1",
        "NOMBRE_CARRERA": "PROGRAMA SINTÉTICO", "MODALIDAD": "Presencial",
        "JORNADA": "Diurna", "VERSION": "1", "TIPO_CARRERA": "Plan Regular",
        "PLAN_ESPECIAL": "", "DURACION_ESTUDIOS": "8",
        "DURACION_TITULACION": "0", "DURACION_TOTAL": "8",
        "ANO_INICIO": "2018", "VIGENCIA": "Vigente con estudiantes nuevos",
        "NIVEL_GLOBAL": "Pregrado", "NIVEL_CARRERA": "Profesional Sin Licenciatura",
        "hoja_origen": "in", "fila_origen": str(record),
    }
    row.update(fields)
    return row


def enrollment(year=2026, code="I162S2C1J1V1", **fields):
    """Resumen de programa y año; no incluye ninguna identidad individual."""
    row = {
        "cat_periodo": str(year), "codigo_unico": code,
        "cod_inst": "162", "cod_sede": "2", "cod_carrera": "1",
        "nomb_carrera": "PROGRAMA SINTÉTICO", "modalidad": "Presencial",
        "jornada": "Diurna", "version": "1", "tipo_plan_carr": "Plan Regular",
        "vigencia_carrera": "Vigente con estudiantes nuevos",
        "dur_estudio_carr": "8", "dur_proceso_tit": "0", "dur_total_carr": "8",
        "filas_matricula": "3", "registro_ejemplo": "7",
    }
    row.update(fields)
    return row


def current_offer(**fields):
    row = {
        "CODIGO_IES_NUM": "162", "CODIGO_UNICO": "I162S2C1J1V1",
        "CODIGO_CARRERA": "1", "NOMBRE_CARRERA": "PROGRAMA SINTÉTICO",
        "MODALIDAD": "1", "CODIGO_JORNADA": "1", "VERSION_CARRERA": "1",
        "CODIGO_TIPO_CARRERA": "1", "CARACT_PLAN_ESPECIAL": "",
        "DURACION_ESTUDIO": "8", "DURACION_TITULACION": "0", "DURACION_TOTAL": "8",
        "CODIGO_NIVEL_GLOBAL": "1", "CODIGO_NIVEL_CARRERA": "2", "VIGENCIA": "1",
        "_fila": 2,
    }
    row.update(fields)
    return row


class OfferHistoryTests(unittest.TestCase):
    def test_duplicate_offer_year_code_rejected_not_deduplicated(self):
        with self.assertRaisesRegex(ValueError, "Clave duplicada oferta anual"):
            M.build([offer(), offer(record=3)], [], [], [2026])

    def test_duplicate_mrun_year_code_rejected(self):
        with self.assertRaisesRegex(ValueError, "Clave duplicada MRUN anual"):
            M.build([offer()], [enrollment(), enrollment(registro_ejemplo="8")], [], [2026])

    def test_duplicate_current_code_rejected(self):
        with self.assertRaisesRegex(ValueError, "Clave duplicada oferta actual"):
            M.build([offer()], [], [current_offer(), current_offer(_fila=3)], [2026])

    def test_join_requires_same_year_even_when_code_exists_in_other_year(self):
        rows = [offer(year=2025), offer(code="I162S2C2J1V1", CODIGO_CARRERA="2", record=3)]
        result = M.build(rows, [enrollment()], [], [2025, 2026])
        annual = {(r["anio"], r["codigo_unico"]): r for r in result["cruce_oferta_mrun_anual.tsv"]}
        self.assertEqual(annual[(2025, "I162S2C1J1V1")]["estado"], "SOLO_OFERTA")
        self.assertEqual(annual[(2026, "I162S2C1J1V1")]["estado"], "MRUN_SIN_OFERTA_DEL_ANIO")
        self.assertEqual(result["comparacion_atributos_mrun.tsv"], [])

    def test_offer_without_enrollment_is_preserved(self):
        result = M.build([offer()], [], [], [2026])
        self.assertEqual(result["oferta_codigo_anio.tsv"], [offer()])
        self.assertEqual(len(result["historia_codigos.json"]), 1)
        self.assertEqual(result["cobertura_codigos.tsv"][0]["presencia"], "SOLO_OFERTA")
        self.assertEqual(result["cruce_oferta_mrun_anual.tsv"][0]["filas_matricula_mrun"], 0)

    def test_legacy_mrun_code_has_no_invented_family_or_version(self):
        legacy = enrollment(year=2008, code="I162M2008N1", cod_carrera="", version="")
        result = M.build([offer()], [legacy], [], [2026])
        row = next(r for r in result["cobertura_codigos.tsv"] if r["codigo_unico"] == legacy["codigo_unico"])
        self.assertIsNone(row["familia"])
        self.assertEqual(row["presencia"], "SOLO_MRUN")
        self.assertEqual(row["anios_mrun"], "2008")
        annual = next(r for r in result["cruce_oferta_mrun_anual.tsv"] if r["anio"] == 2008)
        self.assertEqual(annual["estado"], "MRUN_FUERA_COBERTURA_OFERTA")
        self.assertFalse(any(r["codigo_unico"] == legacy["codigo_unico"] for r in result["historia_codigos.json"]))
        self.assertEqual(legacy["version"], "")

    def test_modality_and_schedule_are_independent_attributes(self):
        result = M.build([offer(MODALIDAD="Semipresencial")], [enrollment()], [], [2026])
        compared = {r["campo_oferta"]: r for r in result["comparacion_atributos_mrun.tsv"]}
        self.assertEqual(compared["MODALIDAD"]["estado"], "DIFERENTE")
        self.assertEqual(compared["JORNADA"]["estado"], "IGUAL_LITERAL")
        self.assertEqual(result["oferta_codigo_anio.tsv"][0]["JORNADA"], "Diurna")

    def test_missing_values_are_not_attribute_contradictions(self):
        cases = [("", "Presencial", "SIN_DATO_OFERTA"),
                 ("Presencial", "", "SIN_DATO_MRUN"), ("", "", "SIN_DATO_AMBAS")]
        for left, right, expected in cases:
            with self.subTest(left=left, right=right):
                result = M.build([offer(MODALIDAD=left)], [enrollment(modalidad=right)], [], [2026])
                compared = next(r for r in result["comparacion_atributos_mrun.tsv"] if r["campo_oferta"] == "MODALIDAD")
                self.assertEqual(compared["estado"], expected)
                annual = result["cruce_oferta_mrun_anual.tsv"][0]
                self.assertEqual(annual["atributos_diferentes"], 0)
                self.assertEqual(annual["atributos_sin_dato"], 1)

    def test_coexisting_versions_with_same_start_year_both_survive(self):
        rows = [offer(ANO_INICIO="2020"),
                offer(code="I162S2C1J1V2", VERSION="2", ANO_INICIO="2020", record=3,
                      TIPO_CARRERA="Plan Regular de Continuidad", DURACION_ESTUDIOS="4", DURACION_TOTAL="4")]
        result = M.build(rows, [], [], [2026])
        self.assertEqual(len(result["historia_codigos.json"]), 2)
        self.assertEqual(result["versiones_por_familia.json"][0]["versiones_en_primer_anio"], ["1", "2"])
        variants = result["coexistencias.json"][0]["variantes"]
        self.assertEqual({r["VERSION"] for r in variants}, {"1", "2"})
        self.assertEqual({r["ANO_INICIO"] for r in variants}, {"2020"})
        self.assertEqual({r["relacion"] for r in result["inicio_declarado_vs_observado.json"]}, {"ANTERIOR"})

    def test_duration_change_under_same_code_does_not_create_version(self):
        result = M.build([offer(year=2025), offer(DURACION_ESTUDIOS="9", DURACION_TOTAL="9", record=3)], [], [], [2025, 2026])
        self.assertEqual(len(result["historia_codigos.json"]), 1)
        self.assertEqual(result["versiones_por_familia.json"][0]["versiones_informadas"], ["1"])
        change = result["cambios_atributos.json"][0]
        self.assertEqual(change["cambios"], {
            "DURACION_ESTUDIOS": {"anterior": "8", "posterior": "9"},
            "DURACION_TOTAL": {"anterior": "8", "posterior": "9"},
        })

    def test_zero_start_year_is_preserved_as_missing_year_not_chronology(self):
        result = M.build([offer(year=2011, ANO_INICIO="0")], [], [], [2011])
        start = result["inicio_declarado_vs_observado.json"][0]
        self.assertEqual(start["ano_inicio_declarado"], "0")
        self.assertEqual(start["relacion"], "VALOR_CERO_SIN_ANIO")
        self.assertEqual(start["primer_anio_oferta_observada"], 2011)

    def test_postitulo_uses_published_schema_not_other_instructive_codes(self):
        result = M.build(
            [offer(NIVEL_GLOBAL="Postítulo", NIVEL_CARRERA="Diplomado (desde un semestre)")], [],
            [current_offer(CODIGO_NIVEL_GLOBAL="3", CODIGO_NIVEL_CARRERA="5")], [2026],
        )
        self.assertEqual({r["estado"] for r in result["comparacion_oferta_2026.tsv"]}, {"IGUAL"})
        self.assertEqual(result["cobertura_codigos.tsv"][0]["presencia"], "SOLO_OFERTA")
        self.assertEqual(result["historia_codigos.json"][0]["historia"][0]["NIVEL_GLOBAL"], "Postítulo")

    def test_code_components_must_agree_with_observed_columns(self):
        for fields in [{"CODIGO_IES": "999"}, {"CODIGO_SEDE": "3"},
                       {"CODIGO_CARRERA": "2"}, {"VERSION": "2"}, {"JORNADA": "Vespertina"}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                M.build([offer(**fields)], [], [], [2026])

    def test_year_label_and_declared_coverage_must_be_exact(self):
        for year_label in ["MAT_2026", "2026", "OFE_2026_extra"]:
            with self.subTest(year_label=year_label), self.assertRaises(ValueError):
                M.build([offer(ANO=year_label)], [], [], [2026])
        with self.assertRaisesRegex(ValueError, "Cobertura anual"):
            M.build([offer()], [], [], [2025, 2026])

    def test_current_literal_name_does_not_replace_historical_name(self):
        result = M.build([offer(year=2025, NOMBRE_CARRERA="NOMBRE ANTERIOR"),
                          offer(NOMBRE_CARRERA="Nombre literal actual", record=3)], [],
                         [current_offer(NOMBRE_CARRERA="Nombre literal actual")], [2025, 2026])
        history = result["historia_codigos.json"][0]
        self.assertEqual(history["nombre_literal_oferta_2026"], "Nombre literal actual")
        self.assertEqual([r["NOMBRE_CARRERA"] for r in history["historia"]],
                         ["NOMBRE ANTERIOR", "Nombre literal actual"])
        self.assertEqual({r["estado"] for r in result["comparacion_oferta_2026.tsv"]}, {"IGUAL"})

    def test_same_bytes_idempotent_different_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resultado.json"
            M.safe_write(path, b"original\n")
            M.safe_write(path, b"original\n")
            with self.assertRaisesRegex(ValueError, "Salida existente distinta"):
                M.safe_write(path, b"nuevo\n")
            self.assertEqual(path.read_bytes(), b"original\n")

    def test_input_order_does_not_change_result(self):
        rows = [offer(year=2025), offer(record=3)]
        mrun = [enrollment(year=2025), enrollment()]
        self.assertEqual(M.build(rows, mrun, [], [2025, 2026]),
                         M.build(list(reversed(rows)), list(reversed(mrun)), [], [2025, 2026]))


class RunWriteGateTests(unittest.TestCase):
    """El doble de lector evita crear XLSX para probar los controles de escritura."""

    def fixture(self, directory):
        root = Path(directory)
        historic = root / "historico.tsv"
        row = offer()
        with historic.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row), delimiter="\t")
            writer.writeheader()
            writer.writerow(row)
        mrun = root / "mrun.tsv"
        mrun.write_text("cat_periodo\tcodigo_unico\n")
        original = root / "original.fixture"
        original.write_bytes(b"lector XLSX sustituido; no es una fuente real")
        current = root / "actual.fixture"
        current.write_bytes(b"lector XLSX sustituido; no se crea libro")
        phase2 = root / "fase2.json"
        phase2.write_text(json.dumps({"outputs": {"historia_codigo_anio.tsv": M.digest(mrun)}}))
        verification = root / "verificacion.json"
        verification.write_text(json.dumps({"status": "PASS", "checks": {"synthetic_fixture": True},
                                           "hashes_after": {"original": M.digest(original),
                                                            "tsv": M.digest(historic)}}))
        paths = {"historico_xlsx": original, "historico_tsv": historic, "mrun_anual": mrun,
                 "oferta_2026": current, "manifest_fase2": phase2, "verificacion_extraccion": verification}
        config = root / "config.json"
        config.write_text(json.dumps({"coverage_years": [2026], "current_year": 2026,
                                     "institution": "162", "sources": {
            key: {"path": str(path), "sha256": M.digest(path)} for key, path in paths.items()}}))
        row = current_offer()
        row.pop("_fila")
        sheet = SimpleNamespace(iter_rows=lambda **kwargs: iter([tuple(row), tuple(row.values())]))

        class Workbook:
            def __getitem__(self, name):
                if name != "Hoja1":
                    raise KeyError(name)
                return sheet

            def close(self):
                pass

        reader = SimpleNamespace(load_workbook=lambda *args, **kwargs: Workbook())
        return config, historic, reader

    def test_collision_preflight_writes_no_partial_results(self):
        with tempfile.TemporaryDirectory() as directory:
            config, _, reader = self.fixture(directory)
            output = Path(directory) / "salida"
            output.mkdir()
            existing = output / "resumen.json"
            existing.write_bytes(b"resultado anterior distinto")
            with patch.dict("sys.modules", {"openpyxl": reader}):
                with self.assertRaisesRegex(ValueError, "Salida existente distinta"):
                    M.run(config, output)
            self.assertEqual(list(output.iterdir()), [existing])
            self.assertEqual(existing.read_bytes(), b"resultado anterior distinto")

    def test_altered_source_blocks_before_any_output(self):
        with tempfile.TemporaryDirectory() as directory:
            config, historic, reader = self.fixture(directory)
            historic.write_text(historic.read_text() + "alteracion\n")
            output = Path(directory) / "salida"
            with patch.dict("sys.modules", {"openpyxl": reader}):
                with self.assertRaisesRegex(ValueError, "Fuente alterada: historico_tsv"):
                    M.run(config, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
