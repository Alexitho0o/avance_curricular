# Trazabilidad de Evolución de Errores

Comparación de validaciones: `baseline -> fix1 -> fix2 -> fix3`.

| Regla | baseline | fix1 | fix2 | fix3 |
|---|---:|---:|---:|---:|
| anio_ing_act_out_of_range_1990_2026 | 220 | 0 | 0 | 0 |
| anio_ing_ori_out_of_range_1980_2026_or_1900 | 220 | 0 | 0 | 0 |
| anio_ori_2026_niv_gt_2 | 150 | 0 | 0 | 0 |
| cod_car_non_numeric | 24827 | 0 | 0 | 0 |
| cod_sed_non_numeric | 220 | 0 | 0 | 0 |
| duplicate_identity_career_records | 24751 | 0 | 0 | 0 |
| fech_nac_invalid_date | 220 | 0 | 0 | 0 |
| fecha_matricula_invalid_date | 220 | 0 | 0 | 0 |
| for_ing_act_out_of_range_1_11 | 24827 | 0 | 0 | 0 |
| jor_non_numeric | 24827 | 0 | 0 | 0 |
| modalidad_non_numeric | 24827 | 0 | 0 | 0 |
| nac_out_of_range_1_197 | 220 | 0 | 0 | 0 |
| pais_est_sec_out_of_range_1_197 | 220 | 0 | 0 | 0 |
| required_blank__ANIO_ING_ACT | 220 | 0 | 0 | 0 |
| required_blank__ANIO_ING_ORI | 220 | 0 | 0 | 0 |
| required_blank__COD_SED | 220 | 0 | 0 | 0 |
| required_blank__FECHA_MATRICULA | 220 | 0 | 0 | 0 |
| required_blank__FECH_NAC | 220 | 0 | 0 | 0 |
| required_blank__FOR_ING_ACT | 24827 | 0 | 0 | 0 |
| required_blank__JOR | 24827 | 0 | 0 | 0 |
| required_blank__MODALIDAD | 24827 | 0 | 0 | 0 |
| required_blank__NAC | 220 | 0 | 0 | 0 |
| required_blank__PAIS_EST_SEC | 220 | 0 | 0 | 0 |
| required_blank__SEM_ING_ACT | 220 | 0 | 0 | 0 |
| required_blank__SEM_ING_ORI | 220 | 0 | 0 | 0 |
| required_blank__SEXO | 220 | 0 | 0 | 0 |
| required_blank__VERSION | 24827 | 0 | 0 | 0 |
| rows | 24827 | 2672 | 2672 | 2672 |
| sem_ing_act_not_1_or_2 | 1342 | 0 | 0 | 0 |
| sem_ing_ori_not_0_1_2 | 1342 | 0 | 0 | 0 |
| sexo_invalid | 6802 | 0 | 0 | 0 |
| version_non_numeric | 24827 | 0 | 0 | 0 |

## Reglas cerradas (baseline > 0 y fix3 = 0)
- `cod_car_non_numeric`: 24827 -> 0
- `for_ing_act_out_of_range_1_11`: 24827 -> 0
- `jor_non_numeric`: 24827 -> 0
- `modalidad_non_numeric`: 24827 -> 0
- `required_blank__FOR_ING_ACT`: 24827 -> 0
- `required_blank__JOR`: 24827 -> 0
- `required_blank__MODALIDAD`: 24827 -> 0
- `required_blank__VERSION`: 24827 -> 0
- `version_non_numeric`: 24827 -> 0
- `duplicate_identity_career_records`: 24751 -> 0
- `sexo_invalid`: 6802 -> 0
- `sem_ing_act_not_1_or_2`: 1342 -> 0
- `sem_ing_ori_not_0_1_2`: 1342 -> 0
- `anio_ing_act_out_of_range_1990_2026`: 220 -> 0
- `anio_ing_ori_out_of_range_1980_2026_or_1900`: 220 -> 0
- `cod_sed_non_numeric`: 220 -> 0
- `fech_nac_invalid_date`: 220 -> 0
- `fecha_matricula_invalid_date`: 220 -> 0
- `nac_out_of_range_1_197`: 220 -> 0
- `pais_est_sec_out_of_range_1_197`: 220 -> 0
- `required_blank__ANIO_ING_ACT`: 220 -> 0
- `required_blank__ANIO_ING_ORI`: 220 -> 0
- `required_blank__COD_SED`: 220 -> 0
- `required_blank__FECHA_MATRICULA`: 220 -> 0
- `required_blank__FECH_NAC`: 220 -> 0
- `required_blank__NAC`: 220 -> 0
- `required_blank__PAIS_EST_SEC`: 220 -> 0
- `required_blank__SEM_ING_ACT`: 220 -> 0
- `required_blank__SEM_ING_ORI`: 220 -> 0
- `required_blank__SEXO`: 220 -> 0
