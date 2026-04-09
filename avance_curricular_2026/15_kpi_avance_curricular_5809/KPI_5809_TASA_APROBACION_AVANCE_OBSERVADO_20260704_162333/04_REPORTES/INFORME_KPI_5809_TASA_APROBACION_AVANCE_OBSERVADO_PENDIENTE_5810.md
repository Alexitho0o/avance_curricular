# KPI 5809 — Tasa de aprobación anual y avance observado

Proceso: Avance Curricular SIES 2026  
Subproyecto: KPI posterior a Matrícula 5809  
Año referencia de datos: 2025  

Se construyen KPI internos derivados desde la carga Matrícula 5809, segmentados por sede, carrera, nivel, jornada, año de ingreso, año matrícula, sexo y edad. El Avance Curricular Esperado queda pendiente, porque requiere la carga Carreras 5810 para obtener las unidades esperadas del plan.

## Resumen

| METRICA                           | VALOR              |
|:----------------------------------|:-------------------|
| TOTAL_REGISTROS_BASE              | 2371               |
| TOTAL_PERSONAS                    | 2370               |
| TOTAL_SEDES                       | 1                  |
| TOTAL_CARRERAS_COD                | 19                 |
| TOTAL_JORNADAS_COD                | 3                  |
| TOTAL_NIVELES_DERIVADOS           | 8                  |
| TOTAL_HOMBRES                     | 1753               |
| TOTAL_MUJERES                     | 618                |
| UNIDADES_CURSADAS_2025            | 21505              |
| UNIDADES_APROBADAS_2025           | 17673              |
| TASA_APROBACION_ANUAL_GLOBAL      | 0.821808881655429  |
| UNID_CURSADAS_TOTAL_GLOBAL        | 21594              |
| UNID_APROBADAS_TOTAL_GLOBAL       | 18673              |
| AVANCE_ACUMULADO_OBSERVADO_GLOBAL | 0.8647309437806798 |
| AVANCE_CURRICULAR_ESPERADO        | PENDIENTE_5810     |
| FUENTES_ORIGINALES_MODIFICADAS    | NO                 |

## Metodología

| KPI                        | NIVEL                           | FORMULA_GRUPO                                        | DENOMINADOR_CERO   | OBSERVACION                                                                            |
|:---------------------------|:--------------------------------|:-----------------------------------------------------|:-------------------|:---------------------------------------------------------------------------------------|
| TASA_APROBACION_ANUAL      | KPI interno derivado desde 5809 | SUM(UNIDADES_APROBADAS) / SUM(UNIDADES_CURSADAS)     | NO_APLICA          | Mide aprobación anual 2025 sobre unidades cursadas 2025.                               |
| AVANCE_ACUMULADO_OBSERVADO | KPI interno derivado desde 5809 | SUM(UNID_APROBADAS_TOTAL) / SUM(UNID_CURSADAS_TOTAL) | NO_APLICA          | Mide aprobación acumulada sobre unidades cursadas históricas informadas.               |
| AVANCE_CURRICULAR_ESPERADO | Pendiente                       | Requiere unidades esperadas del plan desde 5810      | PENDIENTE_5810     | No se calcula solo con 5809 para evitar inventar denominador esperado.                 |
| NIVEL_DERIVADO             | Implementación técnica          | ANIO_REFERENCIA_DATOS - ANIO_INGRESO + 1             | No aplica          | Nivel académico derivado internamente; validar si 5810 entrega nivel oficial distinto. |
| EDAD_31_12_2025            | Implementación técnica          | Edad calculada al 31-12-2025 desde FECHA_NACIMIENTO  | No aplica          | Se usa cierre del año académico de referencia.                                         |

## Validaciones

| VALIDACION                       | RESULTADO      | DETALLE                                                          |
|:---------------------------------|:---------------|:-----------------------------------------------------------------|
| TOTAL_REGISTROS_2371             | OK             | 2371                                                             |
| COLUMNAS_22_ORIGEN               | OK             | 22                                                               |
| SEDE_COD_DETERMINADO             | OK             | 0                                                                |
| CARRERA_COD_DETERMINADO          | OK             | 0                                                                |
| JORNADA_COD_DETERMINADO          | OK             | 0                                                                |
| ANIO_INGRESO_DETERMINADO         | OK             | 0                                                                |
| EDAD_DETERMINADA                 | OK             | 0                                                                |
| SEXO_HM_VALIDO                   | OK             | 0                                                                |
| TASA_APROBACION_ANUAL_CALCULABLE | OK             | Con UNIDADES_CURSADAS > 0: 2320; sin cursadas: 51                |
| AVANCE_CURRICULAR_ESPERADO       | PENDIENTE_5810 | Requiere carga Carreras 5810 para denominador esperado del plan. |

## Archivo

- Excel KPI: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/15_kpi_avance_curricular_5809/KPI_5809_TASA_APROBACION_AVANCE_OBSERVADO_20260704_162333/02_RESULTADOS/KPI_5809_TASA_APROBACION_Y_AVANCE_OBSERVADO_PENDIENTE_5810.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/15_kpi_avance_curricular_5809/KPI_5809_TASA_APROBACION_AVANCE_OBSERVADO_20260704_162333`
