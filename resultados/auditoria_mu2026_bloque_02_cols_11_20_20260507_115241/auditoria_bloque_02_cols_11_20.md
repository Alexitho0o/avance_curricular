# Auditoría MU2026 · Bloque 2 · Columnas 11 a 20

Fecha: 2026-05-07 11:52:41

## Columnas revisadas

COD_SED, COD_CAR, MODALIDAD, JOR, VERSION, FOR_ING_ACT, ANIO_ING_ACT, SEM_ING_ACT, ANIO_ING_ORI, SEM_ING_ORI

## Resumen de validación

| campo                               | regla                                                                                                 |   errores | estado   | detalle                                                                    |
|:------------------------------------|:------------------------------------------------------------------------------------------------------|----------:|:---------|:---------------------------------------------------------------------------|
| COD_SED                             | Obligatorio; usar solo números                                                                        |         0 | OK       | Vacío o no numérico                                                        |
| COD_CAR                             | Obligatorio; usar solo números                                                                        |         0 | OK       | Vacío o no numérico                                                        |
| MODALIDAD                           | Obligatorio; usar solo números                                                                        |         0 | OK       | Vacío o no numérico                                                        |
| JOR                                 | Obligatorio; usar solo números                                                                        |         0 | OK       | Vacío o no numérico                                                        |
| VERSION                             | Obligatorio; usar solo números                                                                        |         0 | OK       | Vacío o no numérico                                                        |
| FOR_ING_ACT                         | Debe ser numérico entre 1 y 11                                                                        |         0 | OK       | Forma de ingreso fuera de catálogo                                         |
| ANIO_ING_ACT                        | Debe ser numérico entre 1990 y 2026                                                                   |         0 | OK       | Año ingreso carrera actual fuera de rango                                  |
| SEM_ING_ACT                         | Debe ser numérico 1 o 2                                                                               |         0 | OK       | Semestre ingreso carrera actual fuera de rango                             |
| ANIO_ING_ORI                        | Debe ser numérico entre 1980 y 2026, o 1900                                                           |         0 | OK       | Año ingreso carrera origen fuera de rango                                  |
| SEM_ING_ORI                         | Debe ser numérico 1, 2 o 0                                                                            |         0 | OK       | Semestre ingreso carrera origen fuera de rango                             |
| ANIO_ING_ORI_vs_ANIO_ING_ACT        | Año ingreso carrera origen no puede ser mayor al año ingreso carrera actual                           |         0 | OK       | Origen mayor que actual                                                    |
| ANIO_ING_ORI_1900_SEM_0             | Cuando ANIO_ING_ORI es 1900, SEM_ING_ORI debe ser 0                                                   |         0 | OK       | Año origen 1900 con semestre distinto de 0                                 |
| ANIO_ING_ORI_DISTINTO_1900_SEM_NO_0 | Cuando ANIO_ING_ORI es distinto de 1900, SEM_ING_ORI no puede ser 0                                   |         0 | OK       | Año origen distinto de 1900 con semestre 0                                 |
| FOR_ING_ACT_DIRECTO_ANIO            | Para FOR_ING_ACT 1,6,7,8,9,10, ANIO_ING_ORI debe coincidir con ANIO_ING_ACT                           |         0 | OK       | Año origen no coincide con actual en ingreso directo/especial              |
| FOR_ING_ACT_DIRECTO_SEM             | Para FOR_ING_ACT 1,6,7,8,9,10, SEM_ING_ORI debe coincidir con SEM_ING_ACT                             |         0 | OK       | Semestre origen no coincide con actual en ingreso directo/especial         |
| FOR_ING_ACT_2_3_4_11_SEMESTRE       | Para FOR_ING_ACT 2,3,4,11, si ANIO_ING_ORI = ANIO_ING_ACT, SEM_ING_ORI debe ser menor que SEM_ING_ACT |         0 | OK       | Semestre origen mayor o igual al actual en continuidad/cambio/articulación |

## Perfil de columnas

| columna      |   filas |   vacios |   unicos | muestra                                                             |
|:-------------|--------:|---------:|---------:|:--------------------------------------------------------------------|
| COD_SED      |    3442 |        0 |        2 | 3 | 2                                                               |
| COD_CAR      |    3442 |        0 |       32 | 91 | 1 | 3 | 46 | 85 | 57 | 86 | 119 | 76 | 87                      |
| MODALIDAD    |    3442 |        0 |        2 | 1 | 3                                                               |
| JOR          |    3442 |        0 |        3 | 2 | 1 | 4                                                           |
| VERSION      |    3442 |        0 |        4 | 1 | 2 | 3 | 4                                                       |
| FOR_ING_ACT  |    3442 |        0 |        5 | 1 | 2 | 3 | 11 | 6                                                  |
| ANIO_ING_ACT |    3442 |        0 |        9 | 2026 | 2025 | 2023 | 2024 | 2022 | 2016 | 2017 | 2021 | 2019        |
| SEM_ING_ACT  |    3442 |        0 |        2 | 1 | 2                                                               |
| ANIO_ING_ORI |    3442 |        0 |       12 | 2026 | 1900 | 2023 | 2025 | 2024 | 2019 | 2022 | 2021 | 2016 | 2017 |
| SEM_ING_ORI  |    3442 |        0 |        3 | 1 | 0 | 2                                                           |

## Archivos generados

- `resultados/auditoria_mu2026_bloque_02_cols_11_20_20260507_115241/resumen_validacion_bloque_02_cols_11_20.csv`
- `resultados/auditoria_mu2026_bloque_02_cols_11_20_20260507_115241/perfil_columnas_bloque_02_cols_11_20.csv`
- `resultados/auditoria_mu2026_bloque_02_cols_11_20_20260507_115241/muestra_50_filas_bloque_02_cols_11_20.csv`