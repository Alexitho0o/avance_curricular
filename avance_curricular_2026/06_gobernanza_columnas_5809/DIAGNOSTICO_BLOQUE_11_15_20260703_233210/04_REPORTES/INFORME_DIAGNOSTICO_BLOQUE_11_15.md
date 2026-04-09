# Diagnóstico Bloque 11-15 — Matrícula 5809

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

Columnas revisadas:

11. PLAN_ESTUDIOS  
12. ANIO_INGRESO_CARRERA_ACTUAL  
13. SEM_INGRESO_CARRERA_ACTUAL  
14. ANIO_INGRESO_CARRERA_ORIGEN  
15. SEM_INGRESO_CARRERA_ORIGEN  

## Resultado

Estado del bloque: **PREPARADO_CON_ADVERTENCIA_PLAN**

Estas columnas vienen desde la precarga 5809 y no se deben modificar por supuesto.  
Las columnas de ingreso son datos de ingreso, no campos de avance curricular.  
`PLAN_ESTUDIOS` se conserva, pero requiere validación funcional contra Carreras, planes y malla.

## Diagnóstico por columna

|   ORDEN_COLUMNA | CAMPO_5809                  | ESTADO_GOBERNANZA       | TIPO_CAMPO                  | BLOQUEO_GOBERNANZA   |   REGISTROS_TOTAL |   NO_VACIOS |   VACIOS |   VALORES_UNICOS | MUESTRA_VALORES                                                     | DIAGNOSTICO                     | QUE_FALTA_PARA_CONSTRUIR                                      | ACCION_PARA_ARCHIVO_SIES                |
|----------------:|:----------------------------|:------------------------|:----------------------------|:---------------------|------------------:|------------:|---------:|-----------------:|:--------------------------------------------------------------------|:--------------------------------|:--------------------------------------------------------------|:----------------------------------------|
|              11 | PLAN_ESTUDIOS               | BLOQUEADO_POR_PLAN      | PLAN_MODIFICABLE_CONTROLADO | BLOQUEO_PLAN         |              2371 |        2371 |        0 |                1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1                               | PRECARGA_CON_VALIDACION_DE_PLAN | NO_FALTA_DATO_EN_PRECARGA_PERO_REQUIERE_VALIDACION_PLAN_MALLA | CONSERVAR_VALOR_PRECARGA_Y_VALIDAR_PLAN |
|              12 | ANIO_INGRESO_CARRERA_ACTUAL | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA     |                      |              2371 |        2371 |        0 |                8 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | PREPARADA_NO_SE_CONSTRUYE       | NO_FALTA_DATO_PARA_ESTA_COLUMNA                               | CONSERVAR_VALOR_PRECARGA                |
|              13 | SEM_INGRESO_CARRERA_ACTUAL  | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA     |                      |              2371 |        2371 |        0 |                2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1                               | PREPARADA_NO_SE_CONSTRUYE       | NO_FALTA_DATO_PARA_ESTA_COLUMNA                               | CONSERVAR_VALOR_PRECARGA                |
|              14 | ANIO_INGRESO_CARRERA_ORIGEN | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA     |                      |              2371 |        2371 |        0 |               17 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | 2024 | PREPARADA_NO_SE_CONSTRUYE       | NO_FALTA_DATO_PARA_ESTA_COLUMNA                               | CONSERVAR_VALOR_PRECARGA                |
|              15 | SEM_INGRESO_CARRERA_ORIGEN  | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA     |                      |              2371 |        2371 |        0 |                3 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1                               | PREPARADA_NO_SE_CONSTRUYE       | NO_FALTA_DATO_PARA_ESTA_COLUMNA                               | CONSERVAR_VALOR_PRECARGA                |

## Validaciones

| VALIDACION                                    | RESULTADO               | DETALLE                                                                                                                             |
|:----------------------------------------------|:------------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| COLUMNAS_BLOQUE_EXISTEN_EN_5809               | OK                      | PLAN_ESTUDIOS | ANIO_INGRESO_CARRERA_ACTUAL | SEM_INGRESO_CARRERA_ACTUAL | ANIO_INGRESO_CARRERA_ORIGEN | SEM_INGRESO_CARRERA_ORIGEN |
| REGISTROS_5809                                | OK                      | 2371                                                                                                                                |
| PLAN_ESTUDIOS_NO_VACIO                        | OK                      | 0                                                                                                                                   |
| ANIO_INGRESO_CARRERA_ACTUAL_NO_VACIO          | OK                      | 0                                                                                                                                   |
| SEM_INGRESO_CARRERA_ACTUAL_NO_VACIO           | OK                      | 0                                                                                                                                   |
| ANIO_INGRESO_CARRERA_ORIGEN_NO_VACIO          | OK                      | 0                                                                                                                                   |
| SEM_INGRESO_CARRERA_ORIGEN_NO_VACIO           | OK                      | 0                                                                                                                                   |
| COMBO_CODIGO_UNICO_PLAN_EXISTE_EN_5810        | OK                      | 0                                                                                                                                   |
| ANIO_INGRESO_CARRERA_ACTUAL_NUMERICO          | OK                      | 0                                                                                                                                   |
| ANIO_INGRESO_CARRERA_ORIGEN_NUMERICO          | OK                      | 0                                                                                                                                   |
| SEM_INGRESO_CARRERA_ACTUAL_CATALOGO_OBSERVADO | OK                      | 1 | 2                                                                                                                               |
| SEM_INGRESO_CARRERA_ORIGEN_CATALOGO_OBSERVADO | REVISAR                 | 0 | 1 | 2                                                                                                                           |
| ANIO_INGRESO_NO_ES_CAMPO_AVANCE               | OK                      | No escribir ANIO_CURRICULAR_ADECUADO en ANIO_INGRESO_*.                                                                             |
| BLOQUE_11_15_SE_CONSTRUYE                     | NO                      | Campos vienen preparados en precarga; PLAN_ESTUDIOS se conserva pero requiere validación de plan/malla.                             |
| PUEDE_USARSE_EN_ARCHIVO_SIES                  | SI_CON_ADVERTENCIA_PLAN | Este bloque no desbloquea archivo completo; PLAN_ESTUDIOS depende de validación de planes.                                          |

## Conclusión

El bloque 11-15 no se construye desde fuentes académicas de avance.  
Se conserva desde la precarga.  
Sin embargo, `PLAN_ESTUDIOS` mantiene advertencia/bloqueo funcional si la semántica del plan o malla no está demostrada para las columnas académicas posteriores.

No se genera CSV de carga ni SIES_READY.

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_11_15_20260703_233210/02_RESULTADOS/DIAGNOSTICO_BLOQUE_11_15.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_11_15_20260703_233210`
