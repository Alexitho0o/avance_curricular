# Auditoría MU2026 · Bloque 3 · Columnas 21 a 30

Fecha: 2026-05-07 11:53:40

## Columnas revisadas

ASI_INS_ANT, ASI_APR_ANT, PROM_PRI_SEM, PROM_SEG_SEM, ASI_INS_HIS, ASI_APR_HIS, NIV_ACA, SIT_FON_SOL, SUS_PRE, FECHA_MATRICULA

## Resumen de validación

| campo                        | regla                                                                       |   errores | estado   | detalle                                                   |
|:-----------------------------|:----------------------------------------------------------------------------|----------:|:---------|:----------------------------------------------------------|
| ASI_INS_ANT                  | Debe ser numérico entre 0 y 99                                              |         0 | OK       | Asignaturas inscritas año anterior fuera de rango         |
| ASI_APR_ANT                  | Debe ser numérico entre 0 y 99                                              |         0 | OK       | Asignaturas aprobadas año anterior fuera de rango         |
| ASI_APR_ANT_vs_ASI_INS_ANT   | ASI_APR_ANT no puede ser mayor a ASI_INS_ANT                                |         0 | OK       | Aprobadas año anterior mayores que inscritas año anterior |
| PROM_PRI_SEM                 | Debe ser numérico entre 100 y 700, o 0                                      |         0 | OK       | Promedio primer semestre fuera de rango                   |
| PROM_SEG_SEM                 | Debe ser numérico entre 100 y 700, o 0                                      |         0 | OK       | Promedio segundo semestre fuera de rango                  |
| ASI_INS_HIS                  | Debe ser numérico entre 0 y 200                                             |         0 | OK       | Asignaturas inscritas históricas fuera de rango           |
| ASI_APR_HIS                  | Debe ser numérico entre 0 y 200                                             |         0 | OK       | Asignaturas aprobadas históricas fuera de rango           |
| ASI_APR_HIS_vs_ASI_INS_HIS   | ASI_APR_HIS no puede ser mayor a ASI_INS_HIS                                |         0 | OK       | Aprobadas históricas mayores que inscritas históricas     |
| NIV_ACA                      | Debe ser numérico mayor o igual a 1                                         |         0 | OK       | Nivel académico vacío, no numérico o menor que 1          |
| SIT_FON_SOL                  | Debe ser numérico 0, 1 o 2                                                  |         0 | OK       | Situación Fondo Solidario fuera de catálogo               |
| SUS_PRE                      | Debe ser numérico entre 0 y 99                                              |         0 | OK       | Suspensiones previas fuera de rango                       |
| FECHA_MATRICULA              | Debe tener formato dd/mm/aaaa                                               |         0 | OK       | Fecha matrícula vacía o con formato inválido              |
| FECHA_MATRICULA_COHORTE_2026 | Si ANIO_ING_ORI es 2026, FECHA_MATRICULA debiera ser distinta de 01/01/1900 |         0 | OK       | Cohorte 2026 con fecha matrícula por defecto              |

## Perfil de columnas

| columna         |   filas |   vacios |   unicos | min        | max        | muestra                                                                                                                         |
|:----------------|--------:|---------:|---------:|:-----------|:-----------|:--------------------------------------------------------------------------------------------------------------------------------|
| ASI_INS_ANT     |    3442 |        0 |       15 | 0          | 9          | 0 | 12 | 11 | 3 | 4 | 10 | 14 | 13 | 5 | 6                                                                                      |
| ASI_APR_ANT     |    3442 |        0 |       16 | 0          | 9          | 0 | 12 | 8 | 3 | 4 | 10 | 14 | 11 | 13 | 6                                                                                      |
| PROM_PRI_SEM    |    3442 |        0 |      210 | 0          | 700        | 0 | 608 | 100 | 636 | 535 | 677 | 555 | 448 | 588 | 590                                                                         |
| PROM_SEG_SEM    |    3442 |        0 |      286 | 0          | 697        | 0 | 685 | 688 | 667 | 683 | 582 | 619 | 674 | 624 | 632                                                                         |
| ASI_INS_HIS     |    3442 |        0 |       29 | 0          | 9          | 0 | 16 | 8 | 9 | 15 | 4 | 18 | 17 | 14 | 5                                                                                      |
| ASI_APR_HIS     |    3442 |        0 |       25 | 0          | 9          | 0 | 12 | 8 | 4 | 10 | 14 | 11 | 13 | 9 | 15                                                                                     |
| NIV_ACA         |    3442 |        0 |        8 | 1          | 8          | 1 | 3 | 5 | 2 | 4 | 7 | 6 | 8                                                                                                   |
| SIT_FON_SOL     |    3442 |        0 |        2 | 0          | 1          | 1 | 0                                                                                                                           |
| SUS_PRE         |    3442 |        0 |        1 | 0          | 0          | 0                                                                                                                               |
| FECHA_MATRICULA |    3442 |        0 |      220 | 01/01/1900 | 31/12/2025 | 26/01/2026 | 04/03/2026 | 27/02/2026 | 01/01/1900 | 14/01/2026 | 30/01/2026 | 17/03/2026 | 02/01/2026 | 20/01/2026 | 31/03/2026 |

## Archivos generados

- `resultados/auditoria_mu2026_bloque_03_cols_21_30_20260507_115340/resumen_validacion_bloque_03_cols_21_30.csv`
- `resultados/auditoria_mu2026_bloque_03_cols_21_30_20260507_115340/perfil_columnas_bloque_03_cols_21_30.csv`
- `resultados/auditoria_mu2026_bloque_03_cols_21_30_20260507_115340/muestra_50_filas_bloque_03_cols_21_30.csv`