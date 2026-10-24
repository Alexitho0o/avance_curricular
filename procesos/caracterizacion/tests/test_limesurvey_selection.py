from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from caracterizacion_limesurvey import (
    LimeSurveyCoherenceError,
    LimeSurveySelectionError,
    build_coherence_report,
    inspect_matricula_file,
    inspect_results_file,
    read_input_frame,
    select_latest_limesurvey_pair,
    validate_coherence_report,
    validate_high_new_records,
)


class LimeSurveySelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.downloads = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def set_mtime(self, path: Path, mtime: int) -> Path:
        os.utime(path, (mtime, mtime))
        return path

    def write_tokens(self, name: str, tokens: list[str], *, mtime: int = 10) -> Path:
        path = self.downloads / name
        df = pd.DataFrame({
            "tid": range(1, len(tokens) + 1),
            "firstname": [f"Nombre{i}" for i in range(len(tokens))],
            "lastname": [f"Apellido{i}" for i in range(len(tokens))],
            "email": [f"a{i}@test.cl" for i in range(len(tokens))],
            "token": tokens,
            "completed": ["N"] * len(tokens),
            "usesleft": [1] * len(tokens),
            "validfrom": [""] * len(tokens),
            "validuntil": [""] * len(tokens),
        })
        if path.suffix.lower() == ".csv":
            df.to_csv(path, index=False)
        else:
            df.to_excel(path, index=False)
        return self.set_mtime(path, mtime)

    def write_results(self, name: str, tokens: list[str], *, mtime: int = 10) -> Path:
        path = self.downloads / name
        df = pd.DataFrame({
            "id": range(1, len(tokens) + 1),
            "submitdate": ["2026-06-01 10:00:00"] * len(tokens),
            "lastpage": [3] * len(tokens),
            "startlanguage": ["es"] * len(tokens),
            "token": tokens,
            "G01Q01": ["Si"] * len(tokens),
        })
        df.to_excel(path, index=False)
        return self.set_mtime(path, mtime)

    def test_nombres_con_ids_iguales(self):
        self.write_tokens("tokens_443299.csv", ["1", "2"], mtime=10)
        self.write_results("results-survey443299.xlsx", ["1", "2"], mtime=11)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.tokens_path.name, "tokens_443299.csv")
        self.assertEqual(pair.results_path.name, "results-survey443299.xlsx")
        self.assertEqual(pair.evaluation.coincidencias, 2)

    def test_zero_byte_explicit_excel_raises_selection_error(self):
        path = self.downloads / 'results-survey141234.xlsx'
        path.touch()
        with self.assertRaisesRegex(LimeSurveySelectionError, r'vacio \(0 bytes\)'):
            read_input_frame(path)

    def test_text_with_excel_extension_raises_selection_error(self):
        path = self.downloads / 'results-survey141234.xlsx'
        path.write_text('invalid workbook')
        with self.assertRaisesRegex(LimeSurveySelectionError, 'Excel invalido'):
            read_input_frame(path)

    def test_valid_excel_without_responses_has_a_distinct_error(self):
        path = self.write_results('results-survey141234.xlsx', [])
        with self.assertRaisesRegex(LimeSurveySelectionError, 'Archivo resultados vacio'):
            inspect_results_file(path)

    def test_nombres_con_ids_distintos_pero_contenido_compatible(self):
        self.write_tokens("tokens_441454.csv", ["10", "11"], mtime=10)
        self.write_results("results-survey443299.xlsx", ["10", "11"], mtime=11)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertIn("441454", pair.survey_id)
        self.assertIn("443299", pair.survey_id)
        self.assertEqual(pair.evaluation.coincidencias, 2)

    def test_nombres_sin_numero(self):
        self.write_tokens("tokens actuales.csv", ["21", "22"], mtime=10)
        self.write_results("resultados encuesta.xlsx", ["21", "22"], mtime=11)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.survey_id, "sin_id_en_nombre")
        self.assertEqual(pair.evaluation.coincidencias, 2)

    def test_nombres_con_espacios_y_parentesis(self):
        self.write_tokens("tokens encuesta (1).csv", ["31", "32"], mtime=10)
        self.write_results("results-survey descarga (final).xlsx", ["31", "32"], mtime=11)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.evaluation.cobertura_pct, 100.0)

    def test_multiples_tokens(self):
        self.write_tokens("tokens_A.csv", ["1", "2", "3"], mtime=30)
        self.write_tokens("tokens_B.csv", ["90", "91"], mtime=40)
        self.write_results("results-surveyX.xlsx", ["1", "2", "3"], mtime=20)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.tokens_path.name, "tokens_A.csv")
        self.assertEqual(pair.evaluation.coincidencias, 3)

    def test_multiples_resultados(self):
        self.write_tokens("tokens_A.csv", ["1", "2", "3"], mtime=30)
        self.write_results("resultados_X.xlsx", ["90"], mtime=50)
        self.write_results("resultados_Y.xlsx", ["1", "2", "3"], mtime=20)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.results_path.name, "resultados_Y.xlsx")
        self.assertEqual(pair.evaluation.coincidencias, 3)

    def test_selecciona_pareja_con_mayor_interseccion(self):
        self.write_tokens("tokens_A.csv", ["1", "2", "3", "4"], mtime=10)
        self.write_tokens("tokens_B.csv", ["1"], mtime=50)
        self.write_results("resultados_X.xlsx", ["1", "2", "3"], mtime=20)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.tokens_path.name, "tokens_A.csv")
        self.assertEqual(pair.results_path.name, "resultados_X.xlsx")
        self.assertEqual(pair.evaluation.coincidencias, 3)

    def test_rechazo_de_pareja_con_cero_coincidencias(self):
        self.write_tokens("tokens_111111.csv", ["1", "2"], mtime=10)
        self.write_results("results-survey222222.xlsx", ["90", "91"], mtime=11)
        with self.assertRaisesRegex(LimeSurveySelectionError, "cero coincidencias"):
            select_latest_limesurvey_pair(self.downloads)

    def test_nombres_correctos_con_contenido_incompatible(self):
        tokens = self.downloads / "tokens_443299.csv"
        pd.DataFrame({"col_a": ["x"], "col_b": ["y"]}).to_csv(tokens, index=False)
        self.set_mtime(tokens, 10)
        self.write_results("results-survey443299.xlsx", ["1"], mtime=11)
        with self.assertRaisesRegex(LimeSurveySelectionError, "tokens"):
            select_latest_limesurvey_pair(self.downloads)

    def test_nombres_distintos_con_contenido_compatible(self):
        self.write_tokens("participantes junio.csv", ["100", "101"], mtime=10)
        self.write_results("respuestas finales.xlsx", ["100", "101"], mtime=11)
        pair = select_latest_limesurvey_pair(self.downloads)
        self.assertEqual(pair.tokens_path.name, "participantes junio.csv")
        self.assertEqual(pair.results_path.name, "respuestas finales.xlsx")

    def test_cero_coincidencias_rechaza_en_validacion(self):
        report = build_coherence_report(
            tokens_survey_id="441454",
            results_survey_id="443299",
            token_rows=1,
            result_rows=1,
            token_ids=["111"],
            result_ids=["222"],
            matricula_ids=["111"],
            complete_response_rows=0,
            respondents=0,
        )
        with self.assertRaisesRegex(LimeSurveyCoherenceError, "Cero coincidencias"):
            validate_coherence_report(report)

    def test_nuevos_inscritos_anormalmente_altos_rechaza_salvo_excepcion(self):
        with self.assertRaisesRegex(LimeSurveyCoherenceError, "Nuevos inscritos"):
            validate_high_new_records(new_records=81, universe_size=100)
        validate_high_new_records(new_records=81, universe_size=100, allow_override=True)

    def test_detecta_matricula_por_estructura_sin_depender_del_nombre(self):
        columns = [f"COL_{i}" for i in range(64)]
        expected = {
            1: "CODCLI", 2: "CODCARPR", 3: "NOMBRE_L", 4: "ANOMATRICULA",
            5: "PERIODOMATRICULA", 6: "ANOINGRESO", 7: "PERIODOINGRESO",
            8: "FECHAMATRICULA", 9: "JORNADA", 10: "RUT", 11: "NOMBRE",
            12: "SEXO", 22: "FONOACTUAL", 23: "MAIL", 24: "MAIL_INST",
            56: "ESTADOACADEMICO", 57: "SITUACION", 59: "NIVEL",
            61: "CON_FIRMA", 63: "SEDE",
        }
        for idx, name in expected.items():
            columns[idx] = name
        path = self.downloads / "archivo sin nombre reconocible.xlsx"
        pd.DataFrame([["x"] * len(columns)], columns=columns).to_excel(path, index=False)
        record = inspect_matricula_file(path)
        self.assertEqual(record.kind, "matricula")
        self.assertEqual(record.path.name, path.name)


if __name__ == "__main__":
    unittest.main()
