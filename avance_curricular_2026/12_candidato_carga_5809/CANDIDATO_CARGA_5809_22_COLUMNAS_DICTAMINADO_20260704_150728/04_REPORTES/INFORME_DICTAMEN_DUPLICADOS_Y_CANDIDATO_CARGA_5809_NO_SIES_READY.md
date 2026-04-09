# Dictamen duplicados y candidato de carga 5809 — NO SIES_READY

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año referencia: 2025  

Se revisaron duplicados por llave exacta estudiante-carrera y por persona. No se detectó duplicado exacto CODIGO_UNICO + NUM_DOCUMENTO + DV. El único duplicado por persona corresponde al caso 19356713-4, con dos CODIGO_UNICO distintos, por lo que se dictamina como no bloqueante y se conserva cada fila según la carrera informada.

Se genera un candidato de carga versionado, sin encabezado, delimitador punto y coma y codificación cp1252. Este archivo no se declara SIES_READY.

## Resumen

| METRICA                                        | VALOR                                                            |
|:-----------------------------------------------|:-----------------------------------------------------------------|
| TOTAL_FILAS_CANDIDATO                          | 2371                                                             |
| TOTAL_COLUMNAS_CANDIDATO                       | 22                                                               |
| CSV_SIN_ENCABEZADO                             | SI                                                               |
| DELIMITADOR                                    | ;                                                                |
| ENCODING                                       | cp1252                                                           |
| ERRORES_COLUMNAS_FISICAS                       | 0                                                                |
| ERRORES_VALIDACION_16_22                       | 0                                                                |
| DUPLICADO_EXACTO_CODIGO_UNICO_NUM_DOCUMENTO_DV | NO                                                               |
| DUPLICADO_PERSONA_NUM_DOCUMENTO_DV             | SI                                                               |
| DICTAMEN_DUPLICADO_PERSONA                     | NO_BLOQUEANTE_MULTICARRERA                                       |
| CASO_19356713_4_FILAS                          | 2                                                                |
| CASO_19356713_4_CODIGO_UNICO_DISTINTOS         | 2                                                                |
| SHA256_REVISION                                | f8861361d5fe0bf033ed15500c22031381b058e7e214245cfa04753ed128c28b |
| SHA256_CANDIDATO                               | f8861361d5fe0bf033ed15500c22031381b058e7e214245cfa04753ed128c28b |
| CANDIDATO_CARGA_GENERADO                       | SI                                                               |
| SIES_READY_GENERADO                            | NO                                                               |
| FUENTES_ORIGINALES_MODIFICADAS                 | NO                                                               |

## Validaciones

| VALIDACION                                     | RESULTADO       | DETALLE                                                          |
|:-----------------------------------------------|:----------------|:-----------------------------------------------------------------|
| FILAS_2371                                     | OK              | 2371                                                             |
| COLUMNAS_22                                    | OK              | 22                                                               |
| SIN_ENCABEZADO                                 | OK              | SI                                                               |
| DELIMITADOR_PUNTO_Y_COMA                       | OK              | ;                                                                |
| ENCODING_CP1252                                | OK              | cp1252                                                           |
| LINEAS_CON_22_COLUMNAS                         | OK              | 0                                                                |
| VALORES_16_22                                  | OK              | 0                                                                |
| DUPLICADO_EXACTO_CODIGO_UNICO_NUM_DOCUMENTO_DV | OK              | NO                                                               |
| DUPLICADO_PERSONA_NUM_DOCUMENTO_DV             | OK_CON_DICTAMEN | NO_BLOQUEANTE_MULTICARRERA                                       |
| CASO_19356713_4                                | OK_CON_DICTAMEN | 2 filas, 2 CODIGO_UNICO distintos                                |
| HASH_REVISION_VS_CANDIDATO                     | OK              | f8861361d5fe0bf033ed15500c22031381b058e7e214245cfa04753ed128c28b |
| CANDIDATO_CARGA_GENERADO                       | OK              | SI                                                               |
| SIES_READY_GENERADO                            | OK              | NO                                                               |
| FUENTES_ORIGINALES_MODIFICADAS                 | OK              | NO                                                               |

## Dictamen duplicados

| LLAVE_EVALUADA                    | ESTADO                  |   TOTAL_GRUPOS_DUPLICADOS |   TOTAL_FILAS_INVOLUCRADAS | DICTAMEN                                                                                                                                 |
|:----------------------------------|:------------------------|--------------------------:|---------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------|
| CODIGO_UNICO + NUM_DOCUMENTO + DV | OK                      |                         0 |                          0 | No se detectan duplicados para esta llave.                                                                                               |
| NUM_DOCUMENTO + DV                | NO_BLOQUEANTE_OBSERVADO |                         1 |                          2 | Duplicado por persona. No bloquea si los CODIGO_UNICO son distintos. Debe documentarse como multicarrera o más de una carrera informada. |

## Archivos

- CSV candidato: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/12_candidato_carga_5809/CANDIDATO_CARGA_5809_22_COLUMNAS_DICTAMINADO_20260704_150728/02_RESULTADOS/5809_MATRICULA_AVANCE_CURRICULAR_2026_CANDIDATO_CARGA_NO_SIES_READY.csv`
- Excel dictamen: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/12_candidato_carga_5809/CANDIDATO_CARGA_5809_22_COLUMNAS_DICTAMINADO_20260704_150728/02_RESULTADOS/DICTAMEN_DUPLICADOS_Y_CANDIDATO_CARGA_5809_NO_SIES_READY.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/12_candidato_carga_5809/CANDIDATO_CARGA_5809_22_COLUMNAS_DICTAMINADO_20260704_150728`
