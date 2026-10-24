"""Contrato H4 con datos sintéticos: enlaces sin identidad ni vigencia inferida."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


SPEC = spec_from_file_location(
    "planes_umas", Path(__file__).parents[1] / "scripts/reconstruir_planes_umas.py"
)
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def plan(**fields):
    row = {
        "CODPESTUD": "PLAN20241", "Codcarr": "C", "Sede": "RE",
        "Nombre_L": "CARRERA SINTÉTICA", "CODRAMO": "R1",
        "RamoEquiv": "", "_fila": 2,
    }
    return {**row, **fields}


def note(**fields):
    row = {
        "CODCLI": "PRIVATE_CODCLI_A", "CODCARR": "C",
        "CARRERA": "CARRERA SINTÉTICA", "JORNADA": "O", "REGIMEN": "1",
        "CODRAMO": "R1", "RAMOEQUIV": "", "ANO": "2024",
        "PERIODO": "1", "NIVEL": "1", "PLAN_DE_ESTUDIO": "PLAN20241",
        "_fila": 2,
    }
    return {**row, **fields}


def student(**fields):
    row = {
        "CODCLI": "PRIVATE_CODCLI_A", "CODCARPR": "C",
        "NOMBRE_L": "CARRERA SINTÉTICA", "JORNADA": "O", "SEDE": "RE",
        "ANOMATRICULA": "2024", "PERIODOMATRICULA": "1",
        "ANOINGRESO": "2024", "PERIODOINGRESO": "1", "_fila": 2,
    }
    return {**row, **fields}


def join_row(result):
    rows = result["conciliacion_contextos_umas.tsv"]
    if len(rows) != 1:
        raise AssertionError(f"Se esperaba un grupo, se obtuvieron {len(rows)}")
    return rows[0]


class UmasPlansTests(unittest.TestCase):
    def test_missing_identifiers_never_join_each_other(self):
        for missing in (None, "", "NULL", "none", "NaN", "   "):
            with self.subTest(missing=missing):
                result = M.analyze([plan()], [note(CODCLI=missing)], [student(CODCLI=missing)])
                row = join_row(result)
                self.assertEqual(row["estado_datos_alumnos"], "SIN_IDENTIFICADOR")
                self.assertEqual(row["CODCARPR_DA"], "")
                self.assertEqual(row["filas_reporte"], 1)
                self.assertEqual(row["identificadores_internos_distintos"], 0)
                self.assertEqual(row["estado_observacion"], "CLAVES_ACADEMICAS_INCOMPLETAS")

    def test_missing_plan_does_not_join_and_empty_catalog_plan_is_rejected(self):
        for missing in (None, "", "NULL", "NaN"):
            with self.subTest(missing=missing):
                result = M.analyze([plan()], [note(PLAN_DE_ESTUDIO=missing)], [student()])
                self.assertEqual(join_row(result)["estado_plan_catalogo"], "PLAN_NO_LOCALIZADO")
                self.assertEqual(len(result["cobertura_planes.tsv"]), 1)
                with self.assertRaisesRegex(ValueError, "Plan vacío"):
                    M.analyze([plan(CODPESTUD=missing)], [], [])

    def test_shared_identifier_count_does_not_require_a_present_plan(self):
        for missing in ("", "NULL"):
            with self.subTest(missing=missing):
                result = M.analyze([plan()], [note(PLAN_DE_ESTUDIO=missing)], [student()])
                self.assertEqual(join_row(result)["estado_datos_alumnos"], "CONTEXTO_UNICO_DEL_REPORTE")
                self.assertEqual(join_row(result)["estado_plan_catalogo"], "PLAN_NO_LOCALIZADO")
                self.assertEqual(result["resumen_asociaciones.json"]["identificadores_compartidos_promedios_da"], 1)

    def test_two_student_rows_are_neither_chosen_nor_expanded(self):
        for alternate in ({}, {"CODCARPR": "OTRA", "JORNADA": "D", "SEDE": "CO"}):
            with self.subTest(alternate=alternate):
                result = M.analyze([plan()], [note()], [student(), student(_fila=3, **alternate)])
                row = join_row(result)
                self.assertEqual(row["estado_datos_alumnos"], "MULTIPLES_FILAS")
                self.assertEqual(row["filas_reporte"], 1)
                self.assertEqual(row["CODCARPR_DA"], "")
                self.assertEqual(row["fila_alumnos_ejemplo"], "")
                self.assertEqual(row["carrera_da_vs_promedios"], "NO_COMPARABLE")
                self.assertEqual(row["jornada_da_vs_promedios"], "NO_COMPARABLE")
                self.assertEqual(row["sede_da_vs_plan"], "NO_COMPARABLE")
                duplicate = result["duplicados_datos_alumnos.json"][0]
                self.assertEqual(duplicate["filas_alumnos"], [2, 3])
                self.assertEqual(duplicate["estado"], "NO_SELECCIONAR_UNA_FILA")

    def test_year_pattern_is_not_validity_or_sies_version(self):
        result = M.analyze([plan()], [note(ANO="2019")], [student()])
        temporal = result["diagnostico_patrones_anuales.tsv"][0]
        self.assertEqual(temporal["relacion_textual"], "ACTIVIDAD_ANTERIOR_AL_PATRON")
        self.assertEqual(temporal["patrones_anuales_textuales"], "2024")
        self.assertEqual(temporal["significado_temporal"], "NO_ACREDITADO")
        coverage = result["cobertura_planes.tsv"][0]
        self.assertIsNone(coverage["vigencia_desde_acreditada"])
        self.assertIsNone(coverage["vigencia_hasta_acreditada"])
        self.assertFalse(coverage["asignacion_temporal_acreditada"])
        self.assertEqual(result["resumen_asociaciones.json"]["asignaciones_temporales_certificadas"], 0)
        self.assertNotIn('"VERSION"', M.json_bytes(result).decode())

    def test_plan_without_observed_activity_is_preserved(self):
        result = M.analyze([plan()], [], [])
        coverage = result["cobertura_planes.tsv"][0]
        self.assertEqual(coverage["presencia"], "SOLO_CATALOGO")
        self.assertEqual(coverage["anios_actividad_observada"], [])
        self.assertEqual(coverage["filas_promedios"], 0)
        self.assertFalse(coverage["asignacion_temporal_acreditada"])

    def test_report_row_without_year_is_preserved_without_dated_activity(self):
        result = M.analyze([plan()], [note(ANO="NULL", PERIODO="NULL", CODRAMO="NULL")], [student()])
        row = join_row(result)
        self.assertEqual(row["estado_observacion"], "ANIO_NO_VALIDO")
        self.assertEqual(row["filas_reporte"], 1)
        coverage = result["cobertura_planes.tsv"][0]
        self.assertEqual(coverage["presencia"], "CATALOGO_Y_PROMEDIOS")
        self.assertEqual(coverage["filas_promedios"], 1)
        self.assertEqual(coverage["filas_con_anio_y_claves"], 0)
        self.assertEqual(coverage["anios_actividad_observada"], [])
        self.assertEqual(result["diagnostico_patrones_anuales.tsv"], [])

    def test_observation_2027_is_outside_scope(self):
        result = M.analyze([plan()], [note(ANO="2027")], [student()])
        self.assertEqual(join_row(result)["estado_observacion"], "FUERA_PERIODO")
        self.assertEqual(result["diagnostico_patrones_anuales.tsv"], [])
        self.assertEqual(result["cobertura_planes.tsv"][0]["anios_actividad_observada"], [])

    def test_student_2027_is_labeled_without_backdating_context(self):
        result = M.analyze([plan()], [note(ANO="2020")], [student(ANOMATRICULA="2027")])
        row = join_row(result)
        self.assertEqual(row["ANO"], "2020")
        self.assertEqual(row["ANOMATRICULA_DA"], "2027")
        self.assertEqual(row["ambito_anio_matricula_da"], "FUERA_AMBITO")
        self.assertEqual(row["carrera_da_vs_promedios"], "IGUAL")
        self.assertFalse(result["cobertura_planes.tsv"][0]["asignacion_temporal_acreditada"])

    def test_career_schedule_and_site_are_compared_separately(self):
        cases = (
            ({"CODCARPR": "OTRA"}, "carrera_da_vs_promedios"),
            ({"JORNADA": "D"}, "jornada_da_vs_promedios"),
            ({"SEDE": "CO"}, "sede_da_vs_plan"),
        )
        keys = {field for _, field in cases}
        for fields, differing in cases:
            with self.subTest(fields=fields):
                row = join_row(M.analyze([plan()], [note()], [student(**fields)]))
                self.assertEqual(row[differing], "DIFERENTE")
                for key in keys - {differing}:
                    self.assertEqual(row[key], "IGUAL")
                self.assertEqual(row["carrera_plan_vs_promedios"], "IGUAL")

    def test_catalog_career_difference_is_independent_of_current_context(self):
        row = join_row(M.analyze([plan(Codcarr="OTRA")], [note()], [student()]))
        self.assertEqual(row["carrera_plan_vs_promedios"], "DIFERENTE")
        self.assertEqual(row["carrera_da_vs_promedios"], "IGUAL")
        self.assertEqual(row["jornada_da_vs_promedios"], "IGUAL")
        self.assertEqual(row["sede_da_vs_plan"], "IGUAL")

    def test_sp_suffix_is_kept_literally_for_plans_and_careers(self):
        result = M.analyze([plan(CODPESTUD="PLAN")], [note(PLAN_DE_ESTUDIO="PLANSP", CODCARR="CSP")], [student()])
        row = join_row(result)
        self.assertEqual(row["estado_plan_catalogo"], "PLAN_NO_LOCALIZADO")
        self.assertEqual(row["carrera_da_vs_promedios"], "DIFERENTE")
        self.assertEqual(row["PLAN_DE_ESTUDIO"], "PLANSP")
        self.assertEqual(row["CODCARR"], "CSP")
        self.assertEqual({r["CODPESTUD"] for r in result["cobertura_planes.tsv"]}, {"PLAN", "PLANSP"})

    def test_multiple_catalog_contexts_remain_ambiguous(self):
        result = M.analyze([plan(), plan(Codcarr="OTRA", Sede="CO", _fila=3)], [note()], [student()])
        row = join_row(result)
        self.assertEqual(row["estado_plan_catalogo"], "PLAN_CONTEXTO_AMBIGUO")
        self.assertEqual(row["carrera_plan_vs_promedios"], "NO_COMPARABLE")
        self.assertEqual(row["sede_da_vs_plan"], "NO_COMPARABLE")
        self.assertEqual(row["CODCARR_LISTADO"], "")
        self.assertEqual(len(result["cobertura_planes.tsv"][0]["contextos_catalogo"]), 2)

    def test_umas_period_five_is_not_converted_to_sies_semester(self):
        result = M.analyze([plan()], [note(PERIODO="5")], [student()])
        self.assertEqual(join_row(result)["PERIODO"], "5")
        self.assertEqual(result["diagnostico_patrones_anuales.tsv"][0]["PERIODO"], "5")

    def test_equivalence_relation_is_not_reported_as_direct_plan_membership(self):
        result = M.analyze([plan(RamoEquiv="OTHER/R2")], [note(CODRAMO="R2")], [student()])
        self.assertEqual(join_row(result)["estado_ramo"], "RAMO_APARECE_EN_EQUIVALENCIA_CATALOGADA")
        self.assertFalse(result["cobertura_planes.tsv"][0]["asignacion_temporal_acreditada"])
        direct = M.analyze([plan(RamoEquiv="R2")], [note(CODRAMO="R2")], [student()])
        self.assertEqual(join_row(direct)["estado_ramo"], "RAMO_NO_LOCALIZADO_EN_PLAN")

    def test_analyze_is_repeatable_and_does_not_mutate_input(self):
        inputs = ([plan()], [note(), note(CODCLI="PRIVATE_CODCLI_B", _fila=3)], [student()])
        before = deepcopy(inputs)
        first = M.json_bytes(M.analyze(*inputs))
        second = M.json_bytes(M.analyze(*inputs))
        self.assertEqual(first, second)
        self.assertEqual(inputs, before)

    def test_private_fields_and_values_never_appear_in_outputs(self):
        private = {
            "RUT": "PRIVATE_RUT_SENTINEL", "DIG": "PRIVATE_DV_SENTINEL",
            "MRUN": "PRIVATE_MRUN_SENTINEL", "NOMBRE": "PRIVATE_NAME_SENTINEL",
            "PATERNO": "PRIVATE_SURNAME_SENTINEL", "MATERNO": "PRIVATE_SECOND_SURNAME_SENTINEL",
            "NOTA_FINAL": "PRIVATE_GRADE_SENTINEL", "EXAMEN": "PRIVATE_EXAM_SENTINEL",
        }
        notes = [note(**private), note(CODCLI="PRIVATE_CODCLI_B", _fila=3, **private)]
        pupils = [student(**private), student(CODCLI="PRIVATE_CODCLI_B", _fila=3, **private)]
        result = M.analyze([plan()], notes, pupils)
        row = join_row(result)
        self.assertEqual(row["filas_reporte"], 2)
        self.assertEqual(row["identificadores_internos_distintos"], 2)
        serialized = M.json_bytes(result).decode()
        for secret in [*private.values(), "PRIVATE_CODCLI_A", "PRIVATE_CODCLI_B"]:
            self.assertNotIn(secret, serialized)

        def check_keys(value):
            if isinstance(value, dict):
                self.assertFalse(set(value) & (set(private) | {"CODCLI", "_personas"}))
                for item in value.values():
                    check_keys(item)
            elif isinstance(value, list):
                for item in value:
                    check_keys(item)

        check_keys(result)


if __name__ == "__main__":
    unittest.main()
