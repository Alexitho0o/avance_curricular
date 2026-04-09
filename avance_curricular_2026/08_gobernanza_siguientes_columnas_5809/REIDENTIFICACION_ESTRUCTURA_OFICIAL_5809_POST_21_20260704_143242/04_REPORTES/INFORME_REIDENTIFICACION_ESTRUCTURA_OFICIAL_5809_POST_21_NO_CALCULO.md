# Reidentificación estructura oficial 5809 post columna 21 — NO CÁLCULO

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809 / columnas 16–21 y estructura posterior  
Año referencia: 2025  

Esta revisión corrige la identificación anterior: las columnas posteriores a `UNID_APROBADAS_TOTAL_PROPUESTO` en la matriz final corresponden a trazabilidad interna, no necesariamente a columnas oficiales 5809.

## Resumen

| METRICA                               | VALOR                                                  |
|:--------------------------------------|:-------------------------------------------------------|
| TOTAL_FILAS_MATRIZ_FINAL              | 2371                                                   |
| TOTAL_COLUMNAS_MATRIZ_FINAL           | 52                                                     |
| HOJA_MATRIZ_USADA                     | MATRIZ_FINAL_2371                                      |
| TOTAL_FILAS_PRECARGA_5809_RAW         | 2372                                                   |
| TOTAL_COLUMNAS_PRECARGA_5809_RAW      | 22                                                     |
| ENCODING_5809                         | cp1252                                                 |
| DELIMITADOR_5809                      | ;                                                      |
| POSICION_FIN_16_21_EN_MATRIZ          | 48                                                     |
| ESTADO_IDENTIFICACION_POST_21         | COLUMNAS_OFICIALES_POST_21_DETECTADAS_EN_PRECARGA_5809 |
| COLUMNAS_OFICIALES_POST_21_DETECTADAS | 1                                                      |
| COLUMNAS_INTERNAS_POST_21_DETECTADAS  | 4                                                      |
| CSV_CARGA_GENERADO                    | NO                                                     |
| SIES_READY_GENERADO                   | NO                                                     |
| FUENTES_ORIGINALES_MODIFICADAS        | NO                                                     |

## Validaciones

| VALIDACION                        | RESULTADO   | DETALLE                                                                                                                                                                                    |
|:----------------------------------|:------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MATRIZ_FINAL_2371                 | OK          | 2371                                                                                                                                                                                       |
| PRECARGA_5809_LEIDA               | OK          | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5809_Precarga Matrícula Avance Curricular 2026.csv |
| COLUMNAS_16_21_PROPUESTAS_EXISTEN | OK          |                                                                                                                                                                                            |
| NO_CONFUNDIR_COLUMNAS_INTERNAS    | OK          | 4                                                                                                                                                                                          |
| COLUMNAS_OFICIALES_POST_21        | REVISAR     | COLUMNAS_OFICIALES_POST_21_DETECTADAS_EN_PRECARGA_5809                                                                                                                                     |
| CSV_CARGA_GENERADO                | OK          | NO                                                                                                                                                                                         |
| SIES_READY_GENERADO               | OK          | NO                                                                                                                                                                                         |
| FUENTES_ORIGINALES_MODIFICADAS    | OK          | NO                                                                                                                                                                                         |

## Criterio

| PUNTO                          | DETALLE                                                                                                                                                                                         |
|:-------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Corrección metodológica        | Las columnas detectadas después de UNID_APROBADAS_TOTAL_PROPUESTO en la matriz final son internas de trazabilidad, no columnas oficiales 5809.                                                  |
| Fuente rectora para estructura | La estructura oficial se verifica contra la precarga 5809 original, no contra columnas agregadas en matrices de trabajo.                                                                        |
| Resultado                      | COLUMNAS_OFICIALES_POST_21_DETECTADAS_EN_PRECARGA_5809                                                                                                                                          |
| Siguiente paso                 | Si la precarga 5809 original no tiene columnas posteriores a la 21, no corresponde continuar con 'siguientes 5 columnas' de matrícula 5809. Corresponde pasar a otra sección/carga del proceso. |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/08_gobernanza_siguientes_columnas_5809/REIDENTIFICACION_ESTRUCTURA_OFICIAL_5809_POST_21_20260704_143242/02_RESULTADOS/REIDENTIFICACION_ESTRUCTURA_OFICIAL_5809_POST_21_NO_CALCULO.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/08_gobernanza_siguientes_columnas_5809/REIDENTIFICACION_ESTRUCTURA_OFICIAL_5809_POST_21_20260704_143242`
