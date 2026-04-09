# Identificación gobernada de siguientes 5 columnas post 21 — NO CÁLCULO

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809 / columnas posteriores a 16–21  
Año referencia: 2025  

Esta fase identifica las siguientes 5 columnas detectadas después de la columna final 16–21. No calcula valores, no genera CSV de carga y no genera SIES_READY.

## Resumen

| METRICA                        | VALOR                          |
|:-------------------------------|:-------------------------------|
| TOTAL_MATRIZ_FINAL_16_21       | 2371                           |
| HOJA_MATRIZ_USADA              | MATRIZ_FINAL_2371              |
| COLUMNA_FIN_16_21_DETECTADA    | UNID_APROBADAS_TOTAL_PROPUESTO |
| POSICION_FIN_16_21_DETECTADA   | 48                             |
| SIGUIENTES_COLUMNAS_DETECTADAS | 4                              |
| REGLAS_CANDIDATAS_ENCONTRADAS  | 0                              |
| COLUMNAS_PENDIENTES_GOBERNANZA | 4                              |
| CSV_CARGA_GENERADO             | NO                             |
| SIES_READY_GENERADO            | NO                             |
| FUENTES_ORIGINALES_MODIFICADAS | NO                             |

## Validaciones

| VALIDACION                     | RESULTADO   | DETALLE                                                                                                                                                                                                                                         |
|:-------------------------------|:------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MATRIZ_FINAL_EXISTE            | OK          | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/07_cierre_columnas_16_21_y_preparacion_siguientes/FINALIZACION_51_PENDIENTES_16_21_20260704_140748/02_RESULTADOS/MATRIZ_FINAL_2371_COLUMNAS_16_21_CERRADAS_NO_CARGA.xlsx |
| TOTAL_MATRIZ_FINAL             | OK          | 2371                                                                                                                                                                                                                                            |
| COLUMNA_FIN_21_DETECTADA       | OK          | UNID_APROBADAS_TOTAL_PROPUESTO                                                                                                                                                                                                                  |
| POSICION_FIN_21                | OK          | 48                                                                                                                                                                                                                                              |
| SIGUIENTES_5_DETECTADAS        | REVISAR     | 4                                                                                                                                                                                                                                               |
| CSV_CARGA_GENERADO             | OK          | NO                                                                                                                                                                                                                                              |
| SIES_READY_GENERADO            | OK          | NO                                                                                                                                                                                                                                              |
| FUENTES_ORIGINALES_MODIFICADAS | OK          | NO                                                                                                                                                                                                                                              |

## Siguientes 5 columnas detectadas

|   POSICION_MATRIZ | NOMBRE_COLUMNA           | TIPO_DATO_OBSERVADO   |   N_VALORES_NO_VACIOS |   N_VALORES_UNICOS | EJEMPLOS                                                                                                                                                                                                                                                          | ESTADO_DETECCION                       |
|------------------:|:-------------------------|:----------------------|----------------------:|-------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|
|                49 | ESTADO_PREPARACION_16_21 | TEXTO_CODIGO          |                  2371 |                  1 | CALCULADO_NO_CARGA                                                                                                                                                                                                                                                | NO_DETERMINADO_REQUIERE_IDENTIFICACION |
|                50 | FUENTE_CALCULO_16_21     | TEXTO_CODIGO          |                   147 |                  4 | /Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx | DECISION_INTERNA_RESPONSABLE_PROCESO | /Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx | NO_DETERMINADO_REQUIERE_IDENTIFICACION |
|                51 | HOJA_CALCULO_16_21       | TEXTO_CODIGO          |                   147 |                  3 | Hoja1 | NO_APLICA_SIN_ASIGNATURAS                                                                                                                                                                                                                                 | NO_DETERMINADO_REQUIERE_IDENTIFICACION |
|                52 | NIVEL_RESPALDO_CALCULO   | TEXTO_CODIGO          |                   147 |                  5 | FUENTE_NUEVA_DESCARGAS_VALIDADA_NO_CONGELADA | DECISION_INTERNA_DOCUMENTADA | DECISION_INTERNA_TECNICA_PROPUESTA_APLICADA_NO_CARGA | DECISION_INTERNA_TECNICA_NOMBRE_5810                                                                                         | NO_DETERMINADO_REQUIERE_IDENTIFICACION |

## Gobernanza requerida

|   POSICION_MATRIZ | NOMBRE_COLUMNA           | TIPO_DATO_OBSERVADO   | FUENTE_REQUERIDA_PROPUESTA         | ESTADO_REGLA_INSTRUCTIVO                    | ESTADO_GOBERNANZA       | ACCION_REQUERIDA                                                                                                      |
|------------------:|:-------------------------|:----------------------|:-----------------------------------|:--------------------------------------------|:------------------------|:----------------------------------------------------------------------------------------------------------------------|
|                49 | ESTADO_PREPARACION_16_21 | TEXTO_CODIGO          | NO_DETERMINADA_REQUIERE_GOBERNANZA | SIN_REGLA_LOCALIZADA_EN_BUSQUEDA_AUTOMATICA | PENDIENTE_DE_GOBERNANZA | Confirmar nombre oficial, posición real 5809, regla del instructivo, fuente de dato y validaciones antes de calcular. |
|                50 | FUENTE_CALCULO_16_21     | TEXTO_CODIGO          | NO_DETERMINADA_REQUIERE_GOBERNANZA | SIN_REGLA_LOCALIZADA_EN_BUSQUEDA_AUTOMATICA | PENDIENTE_DE_GOBERNANZA | Confirmar nombre oficial, posición real 5809, regla del instructivo, fuente de dato y validaciones antes de calcular. |
|                51 | HOJA_CALCULO_16_21       | TEXTO_CODIGO          | NO_DETERMINADA_REQUIERE_GOBERNANZA | SIN_REGLA_LOCALIZADA_EN_BUSQUEDA_AUTOMATICA | PENDIENTE_DE_GOBERNANZA | Confirmar nombre oficial, posición real 5809, regla del instructivo, fuente de dato y validaciones antes de calcular. |
|                52 | NIVEL_RESPALDO_CALCULO   | TEXTO_CODIGO          | NO_DETERMINADA_REQUIERE_GOBERNANZA | SIN_REGLA_LOCALIZADA_EN_BUSQUEDA_AUTOMATICA | PENDIENTE_DE_GOBERNANZA | Confirmar nombre oficial, posición real 5809, regla del instructivo, fuente de dato y validaciones antes de calcular. |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/08_gobernanza_siguientes_columnas_5809/IDENTIFICACION_SIGUIENTES_5_COLUMNAS_POST_21_20260704_141429/02_RESULTADOS/IDENTIFICACION_GOBERNADA_SIGUIENTES_5_COLUMNAS_POST_21_NO_CALCULO.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/08_gobernanza_siguientes_columnas_5809/IDENTIFICACION_SIGUIENTES_5_COLUMNAS_POST_21_20260704_141429`
