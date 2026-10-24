"""Casos sintéticos de decisiones que pueden falsear una historia de versiones."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

SPEC=spec_from_file_location('historia_mrun',Path(__file__).parents[1]/'scripts/reconstruir_historia_mrun.py')
M=module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def observation(identity='TEST_A',year=2020,code='I162S2C1J1V1',record=2,**overrides):
    row={k:'' for k in M.DETAIL}
    row.update(mrun=identity,cat_periodo=str(year),codigo_unico=code,
        cod_inst='162',cod_sede='2',cod_carrera='1',nomb_carrera='PROGRAMA SINTETICO',
        modalidad='Presencial',jornada='Diurna',version='1',tipo_plan_carr='Plan Regular',
        vigencia_carrera='Vigente con estudiantes nuevos',dur_estudio_carr='8',dur_proceso_tit='0',dur_total_carr='8',
        anio_ing_carr_ori='2019',sem_ing_carr_ori='1',anio_ing_carr_act='2019',sem_ing_carr_act='1',
        _record=record,_line=record)
    parts=M.components(code)
    if parts:
        row.update(cod_inst=str(parts[0]),cod_sede=str(parts[1]),cod_carrera=str(parts[2]),version=str(parts[4]))
    row.update(overrides)
    return row


class HistoryTests(unittest.TestCase):
    def test_missing_identity_preserves_program_but_no_person_link(self):
        result=M.build([observation(identity=''),observation(year=2021,record=3)])
        self.assertEqual(result['resumen.json']['observations'],2)
        self.assertEqual(result['resumen.json']['observations_without_mrun'],1)
        self.assertEqual(result['resumen.json']['transitions_between_observed_years'],0)
        self.assertEqual(sum(r['filas_matricula'] for r in result['historia_codigo_anio.tsv']),2)

    def test_sort_years_and_preserve_gap_and_decreasing_version(self):
        result=M.build([observation(year=2022,record=2),observation(year=2020,code='I162S2C1J1V2',record=3)])
        event=result['transiciones_observadas.tsv'][0]
        self.assertEqual((event['anio_anterior'],event['anio_siguiente_observado']),(2020,2022))
        self.assertEqual(event['anios_sin_observacion'],1)
        self.assertEqual(event['clase'],'CAMBIO_VERSION_DISMINUYE')

    def test_multimatricula_does_not_form_arbitrary_pairs(self):
        result=M.build([observation(),observation(code='I162S2C2J1V1',record=3),observation(year=2021,record=4)])
        summary=result['resumen.json']
        self.assertEqual(summary['transitions_between_observed_years'],1)
        self.assertEqual(summary['transition_counts_all_observed_pairs'],{'CONJUNTOS_CON_MULTIMATRICULA_SIN_EMPAREJAR':1})

    def test_same_cohort_can_leave_two_versions(self):
        result=M.build([observation(),observation(identity='TEST_B',code='I162S2C1J1V2',record=3)])
        self.assertEqual(result['criterios_insuficientes.json']['groups_with_multiple_versions'],1)
        self.assertEqual(result['resumen.json']['transitions_between_observed_years'],0)

    def test_special_missing_future_and_reversed_cohorts_do_not_prove_sufficiency(self):
        for fields in [dict(anio_ing_carr_ori='1900',sem_ing_carr_ori='0'),
                       dict(anio_ing_carr_ori='1900',sem_ing_carr_ori='1'),
                       dict(anio_ing_carr_act=''),dict(anio_ing_carr_act='2021'),
                       dict(anio_ing_carr_ori='2019',sem_ing_carr_ori='2')]:
            with self.subTest(fields=fields):
                rows=[observation(**fields),observation(identity='TEST_B',code='I162S2C1J1V2',record=3,**fields)]
                result=M.build(rows)
                self.assertEqual(result['criterios_insuficientes.json']['groups_with_multiple_versions'],0)
                self.assertEqual(len(result['coexistencias.json']),1)

    def test_legacy_code_kept_without_invented_family(self):
        result=M.build([observation(code='I162M2008N1',year=2008,anio_ing_carr_ori='2007',anio_ing_carr_act='2007')])
        self.assertEqual(result['historia_codigos.json'][0]['estructura'],'HEREDADA_NO_DESCOMPUESTA')
        self.assertIsNone(result['historia_codigos.json'][0]['familia_sies'])

    def test_duplicate_complete_key_is_not_silently_deduplicated(self):
        with self.assertRaises(ValueError):
            M.build([observation(),observation(record=3)])

    def test_serialized_outputs_have_no_person_identifier(self):
        data=M.encode_outputs(M.build([observation(identity='PERSONA_SINTETICA_NO_EXPORTAR')]))
        self.assertFalse(any(b'PERSONA_SINTETICA_NO_EXPORTAR' in body for body in data.values()))


if __name__=='__main__':
    unittest.main()
