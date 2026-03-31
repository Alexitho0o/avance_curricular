# Trazabilidad de mejora (auditoría manual)

## Corridas auditadas
- Antes: `resultados/auditoria_manual_20260331/terminal_run.log`
- Después: `resultados/auditoria_manual_20260331_fix2/terminal_run.log`

## Comparación de validación pregrado (manual)

| Regla | Antes | Después | Delta |
|---|---:|---:|---:|
| anio_ing_act_out_of_range_1990_2026 | 220 | 0 | -220 |
| anio_ing_ori_out_of_range_1980_2026_or_1900 | 220 | 0 | -220 |
| anio_ori_2026_niv_gt_2 | 150 | 0 | -150 |
| cod_car_non_numeric | 24827 | 0 | -24827 |
| cod_sed_non_numeric | 220 | 0 | -220 |
| duplicate_identity_career_records | 24751 | 0 | -24751 |
| fech_nac_invalid_date | 220 | 0 | -220 |
| fecha_matricula_invalid_date | 220 | 0 | -220 |
| for_ing_act_out_of_range_1_11 | 24827 | 0 | -24827 |
| jor_non_numeric | 24827 | 0 | -24827 |
| modalidad_non_numeric | 24827 | 0 | -24827 |
| nac_out_of_range_1_197 | 220 | 0 | -220 |
| pais_est_sec_out_of_range_1_197 | 220 | 0 | -220 |
| required_blank__ANIO_ING_ACT | 220 | 0 | -220 |
| required_blank__ANIO_ING_ORI | 220 | 0 | -220 |
| required_blank__COD_SED | 220 | 0 | -220 |
| required_blank__FECHA_MATRICULA | 220 | 0 | -220 |
| required_blank__FECH_NAC | 220 | 0 | -220 |
| required_blank__FOR_ING_ACT | 24827 | 0 | -24827 |
| required_blank__JOR | 24827 | 0 | -24827 |
| required_blank__MODALIDAD | 24827 | 0 | -24827 |
| required_blank__NAC | 220 | 0 | -220 |
| required_blank__PAIS_EST_SEC | 220 | 0 | -220 |
| required_blank__SEM_ING_ACT | 220 | 0 | -220 |
| required_blank__SEM_ING_ORI | 220 | 0 | -220 |
| required_blank__SEXO | 220 | 0 | -220 |
| required_blank__VERSION | 24827 | 0 | -24827 |
| rows | 24827 | 2672 | -22155 |
| sem_ing_act_not_1_or_2 | 1342 | 0 | -1342 |
| sem_ing_ori_not_0_1_2 | 1342 | 0 | -1342 |
| sexo_invalid | 6802 | 0 | -6802 |
| version_non_numeric | 24827 | 0 | -24827 |

## Estado de carga final

- `EXCLUIDO_DUPLICADO_CLAVE_CARGA`: **21442**
- `OK_CARGA_PREGRADO`: **2672**
- `EXCLUIDO_SIN_MATCH_SIES`: **709**
- `EXCLUIDO_SIN_MATCH_DATOS_ALUMNOS`: **4**

## Resultado

- La hoja `MATRICULA_UNIFICADA_32` quedó en **2672** filas deduplicadas y validadas.
- Las filas no aptas quedaron trazadas en `EXCLUIDOS_CARGA_PREGR` con motivo explícito.
- Las reglas críticas de formato/rango/obligatoriedad del manual quedaron en 0 incumplimientos en la validación local.