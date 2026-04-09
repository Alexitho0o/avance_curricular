# Lectura gobernada 5810 Carreras para KPI Avance Esperado — NO CÁLCULO

Proceso: Avance Curricular SIES 2026  
Subproyecto: Carreras 5810 / KPI Avance Curricular Esperado  
Año referencia datos: 2025  

Esta fase lee la precarga 5810 Carreras, identifica columnas, llaves candidatas de cruce con 5809 y posibles columnas de denominador para Avance Curricular Esperado. No genera CSV de carga, no genera SIES_READY y no modifica fuentes originales.

## Resumen

| METRICA                                 | VALOR                                                                                                                                                                                      |
|:----------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ARCHIVO_5810                            | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5810_Precarga Carreras Avance Curricular 20268.csv |
| TOTAL_FILAS_RAW_5810                    | 44                                                                                                                                                                                         |
| TOTAL_FILAS_DATOS_5810                  | 43                                                                                                                                                                                         |
| TOTAL_COLUMNAS_5810                     | 22                                                                                                                                                                                         |
| ENCODING_5810                           | utf-8-sig                                                                                                                                                                                  |
| DELIMITADOR_5810                        | ;                                                                                                                                                                                          |
| TIENE_CODIGO_UNICO                      | SI                                                                                                                                                                                         |
| TIENE_PLAN_ESTUDIOS                     | SI                                                                                                                                                                                         |
| TIENE_VIGENCIA                          | SI                                                                                                                                                                                         |
| COLUMNAS_CANDIDATAS_DENOMINADOR         | 15                                                                                                                                                                                         |
| AVANCE_ESPERADO_CALCULABLE_EN_ESTA_FASE | REVISAR_5810                                                                                                                                                                               |
| CSV_CARGA_GENERADO                      | NO                                                                                                                                                                                         |
| SIES_READY_GENERADO                     | NO                                                                                                                                                                                         |
| FUENTES_ORIGINALES_MODIFICADAS          | NO                                                                                                                                                                                         |

## Validaciones

| VALIDACION                     | RESULTADO   | DETALLE                                                                                                                                                                                    |
|:-------------------------------|:------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 5810_LEIDA                     | OK          | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5810_Precarga Carreras Avance Curricular 20268.csv |
| FILAS_DATOS_5810               | OK          | 43                                                                                                                                                                                         |
| COLUMNAS_5810                  | OK          | 22                                                                                                                                                                                         |
| CODIGO_UNICO_EN_5810           | OK          | SI                                                                                                                                                                                         |
| PLAN_ESTUDIOS_EN_5810          | OK          | SI                                                                                                                                                                                         |
| VIGENCIA_EN_5810               | OK          | SI                                                                                                                                                                                         |
| CRUCE_5809_5810_CANDIDATO      | OK          | 4                                                                                                                                                                                          |
| DENOMINADOR_AVANCE_ESPERADO    | REVISAR     | Columnas candidatas detectadas: 15                                                                                                                                                         |
| CSV_CARGA_GENERADO             | OK          | NO                                                                                                                                                                                         |
| SIES_READY_GENERADO            | OK          | NO                                                                                                                                                                                         |
| FUENTES_ORIGINALES_MODIFICADAS | OK          | NO                                                                                                                                                                                         |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/16_gobernanza_5810_carreras_para_kpi/LECTURA_GOBERNADA_5810_CARRERAS_KPI_ESPERADO_20260704_162722/02_RESULTADOS/LECTURA_GOBERNADA_5810_CARRERAS_PARA_KPI_AVANCE_ESPERADO_NO_CALCULO.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/16_gobernanza_5810_carreras_para_kpi/LECTURA_GOBERNADA_5810_CARRERAS_KPI_ESPERADO_20260704_162722`
