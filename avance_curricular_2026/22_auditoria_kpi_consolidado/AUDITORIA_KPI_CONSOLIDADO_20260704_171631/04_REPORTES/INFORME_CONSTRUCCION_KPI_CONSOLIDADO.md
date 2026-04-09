# Auditoría de construcción KPI_CONSOLIDADO

Proceso: Avance Curricular SIES 2026  
Subproyecto: Excel maestro KPI + trazabilidad 5809/5810  

## Hallazgo principal

La hoja KPI_CONSOLIDADO es una tabla apilada de distintos niveles de agregación. No debe sumarse completa, porque repite el universo en GENERAL, SEDE, CARRERA, JORNADA, EDAD, SEXO, NIVEL y SEDE_CARRERA_JORNADA.

## Cómo se construye

| ETAPA   | OBJETO                   | DESCRIPCION                                                                                                              |   FILAS | COLUMNAS_CLAVE                                                                                                                                              |
|:--------|:-------------------------|:-------------------------------------------------------------------------------------------------------------------------|--------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ENTRADA | RAW_KPI_AJUSTADO         | Base individual enriquecida desde 5809, puente 5810 ↔ Planes RE+CO y denominador esperado ajustado.                      |    2371 | ID_FILA_5809, NUM_DOCUMENTO, SEDE_COD, CARRERA_COD, JORNADA_COD, SEXO_HM, EDAD_31_12_2025, NIVEL_DERIVADO, unidades cursadas/aprobadas, unidades esperadas. |
| PROCESO | KPI_GENERAL              | Agrupa RAW_KPI_AJUSTADO por ANIO_MATRICULA.                                                                              |       1 | ANIO_MATRICULA                                                                                                                                              |
| PROCESO | KPI_SEDE                 | Agrupa RAW_KPI_AJUSTADO por SEDE_COD + ANIO_MATRICULA.                                                                   |       1 | SEDE_COD, ANIO_MATRICULA                                                                                                                                    |
| PROCESO | KPI_CARRERA              | Agrupa RAW_KPI_AJUSTADO por CARRERA_COD + NOMBRE_L_CANDIDATO + ANIO_MATRICULA.                                           |      19 | CARRERA_COD, NOMBRE_L_CANDIDATO, ANIO_MATRICULA                                                                                                             |
| PROCESO | KPI_JORNADA              | Agrupa RAW_KPI_AJUSTADO por JORNADA_COD + ANIO_MATRICULA.                                                                |       3 | JORNADA_COD, ANIO_MATRICULA                                                                                                                                 |
| PROCESO | KPI_EDAD                 | Agrupa RAW_KPI_AJUSTADO por TRAMO_EDAD + ANIO_MATRICULA.                                                                 |       8 | TRAMO_EDAD, ANIO_MATRICULA                                                                                                                                  |
| PROCESO | KPI_SEXO                 | Agrupa RAW_KPI_AJUSTADO por SEXO_HM + ANIO_MATRICULA.                                                                    |       2 | SEXO_HM, ANIO_MATRICULA                                                                                                                                     |
| PROCESO | KPI_NIVEL                | Agrupa RAW_KPI_AJUSTADO por NIVEL_DERIVADO + ANIO_MATRICULA.                                                             |       8 | NIVEL_DERIVADO, ANIO_MATRICULA                                                                                                                              |
| PROCESO | KPI_SEDE_CARRERA_JORNADA | Agrupa RAW_KPI_AJUSTADO por SEDE_COD + CARRERA_COD + NOMBRE_L_CANDIDATO + JORNADA_COD + ANIO_MATRICULA.                  |      34 | SEDE_COD, CARRERA_COD, NOMBRE_L_CANDIDATO, JORNADA_COD, ANIO_MATRICULA                                                                                      |
| SALIDA  | KPI_CONSOLIDADO          | Apila las hojas KPI anteriores en una sola tabla. No es sumable completa porque repite el universo en distintos niveles. |      76 | NIVEL_CONSOLIDADO + dimensiones + KPI.                                                                                                                      |

## Riesgos

| RIESGO                                  | SEVERIDAD   | DETALLE                                                                                                                                              | ACCION                                                                              |
|:----------------------------------------|:------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
| Suma completa de KPI_CONSOLIDADO        | ALTA        | La hoja mezcla niveles de agregación. Si se suman todas las filas, se multiplica el universo.                                                        | Filtrar siempre NIVEL_CONSOLIDADO antes de analizar.                                |
| Promediar porcentajes                   | ALTA        | TASA_APROBACION_ANUAL, AVANCE_ACUMULADO_OBSERVADO y AVANCE_ESPERADO no deben promediarse entre filas.                                                | Recalcular siempre con sumas de numerador y denominador.                            |
| PERSONAS en niveles cruzados            | MEDIA       | PERSONAS se calcula como nunique dentro de cada segmento. Si una persona aparece en más de un segmento, sumar PERSONAS entre segmentos puede inflar. | Usar PERSONAS solo dentro del nivel de análisis o recalcular desde base individual. |
| SEDE_CARRERA_JORNADA como detalle final | MEDIA       | Es el nivel más detallado disponible en KPI_CONSOLIDADO, pero sigue siendo agregado, no base individual.                                             | Para auditoría de casos usar RAW_KPI_AJUSTADO.                                      |

## Totales por nivel

| NIVEL_CONSOLIDADO    |   FILAS |   SUM_REGISTROS |   SUM_PERSONAS |   SUM_UNIDADES_CURSADAS_2025 |   SUM_UNIDADES_APROBADAS_2025 |   SUM_UNID_CURSADAS_TOTAL |   SUM_UNID_APROBADAS_TOTAL |   SUM_UNIDADES_ESPERADAS_TODAS |   SUM_UNIDADES_ESPERADAS_OBL |   SUM_AJUSTADOS_NIVEL_MAX |
|:---------------------|--------:|----------------:|---------------:|-----------------------------:|------------------------------:|--------------------------:|---------------------------:|-------------------------------:|-----------------------------:|--------------------------:|
| CARRERA              |      19 |            2371 |           2371 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| EDAD                 |       8 |            2371 |           2370 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| GENERAL              |       1 |            2371 |           2370 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| JORNADA              |       3 |            2371 |           2370 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| NIVEL                |       8 |            2371 |           2370 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| SEDE                 |       1 |            2371 |           2370 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| SEDE_CARRERA_JORNADA |      34 |            2371 |           2371 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |
| SEXO                 |       2 |            2371 |           2370 |                        21505 |                         17673 |                     21594 |                      18673 |                          29576 |                        29576 |                        73 |

## Archivo

- Excel auditoría: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/22_auditoria_kpi_consolidado/AUDITORIA_KPI_CONSOLIDADO_20260704_171631/02_RESULTADOS/AUDITORIA_CONSTRUCCION_KPI_CONSOLIDADO.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/22_auditoria_kpi_consolidado/AUDITORIA_KPI_CONSOLIDADO_20260704_171631`
