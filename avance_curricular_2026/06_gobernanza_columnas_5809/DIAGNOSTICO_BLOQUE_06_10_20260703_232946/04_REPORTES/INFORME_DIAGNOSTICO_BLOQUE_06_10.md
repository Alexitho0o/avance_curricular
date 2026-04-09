# Diagnóstico Bloque 06-10 — Matrícula 5809

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

Columnas revisadas:

6. SEGUNDO_APELLIDO  
7. NOMBRES  
8. SEXO  
9. FECHA_NACIMIENTO  
10. CODIGO_UNICO  

## Resultado

Estado del bloque: **PREPARADO_VALIDADO_NO_REQUIERE_CONSTRUCCION**

Estas columnas corresponden a identidad personal y vínculo con carrera. No son campos de avance académico. Vienen desde la precarga 5809 y deben conservarse. `CODIGO_UNICO` además debe validarse contra la precarga Carreras 5810.

## Diagnóstico funcional

Para estas columnas no corresponde calcular curso, unidades, avance anual ni acumulado.  
La información se conserva desde la precarga y se usa como base para cruces posteriores.

## Resultado por columna

|   ORDEN_COLUMNA | CAMPO_5809       | ESTADO_GOBERNANZA       | TIPO_CAMPO              | BLOQUEO_GOBERNANZA   |   REGISTROS_TOTAL |   NO_VACIOS |   VACIOS |   VALORES_UNICOS | MUESTRA_VALORES                                                                                                                                                                                                           | DIAGNOSTICO                      | QUE_FALTA_PARA_CONSTRUIR        | ACCION_PARA_ARCHIVO_SIES     |
|----------------:|:-----------------|:------------------------|:------------------------|:---------------------|------------------:|------------:|---------:|-----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|:--------------------------------|:-----------------------------|
|               6 | SEGUNDO_APELLIDO | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2361 |       10 |              846 | MARTINEZ | VALENZUELA | HERNANDEZ | LEON | LOYOLA | ZUÑIGA | PEREZ | CORNEJO | DURAN | ZAPATA                                                                                                                             | REVISAR_VACIOS_EN_PRECARGA       | EXISTEN_10_VACIOS               | CONSERVAR_VALOR_PRECARGA     |
|               7 | NOMBRES          | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |             1875 | JAVIERA BERNARDITA | JAVIERA IGNACIA | SEBASTIAN ABRAHAM | JOCELYN GLORIA | JAVIER ARTURO | NADIA ARACELI | FABIAN ALEXIS | DANIELA AMBAR | YORGESON LEANDRO | FREDERICK ALEXIS                                           | PREPARADA_NO_SE_CONSTRUYE        | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA     |
|               8 | SEXO             | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |                2 | M | M | H | M | H | M | H | M | H | H                                                                                                                                                                                     | PREPARADA_NO_SE_CONSTRUYE        | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA     |
|               9 | FECHA_NACIMIENTO | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |             2093 | 1997-04-24 00:00:00 | 2005-10-16 00:00:00 | 1983-12-29 00:00:00 | 1994-11-26 00:00:00 | 2002-11-27 00:00:00 | 1991-07-20 00:00:00 | 1991-05-20 00:00:00 | 1993-11-04 00:00:00 | 2000-01-30 00:00:00 | 1982-03-01 00:00:00 | PREPARADA_NO_SE_CONSTRUYE        | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA     |
|              10 | CODIGO_UNICO     | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |               43 | I162S2C57J4V1 | I162S2C1J1V2 | I162S2C1J4V2 | I162S2C1J4V2 | I162S2C1J1V2 | I162S2C1J4V2 | I162S2C1J4V2 | I162S2C1J4V2 | I162S2C1J4V2 | I162S2C1J4V2                                                                      | PREPARADA_VALIDABLE_CON_CARRERAS | NO_FALTA_DATO_PARA_ESTA_COLUMNA | VALIDAR_CON_5810_Y_CONSERVAR |

## Validaciones

| VALIDACION                        | RESULTADO           | DETALLE                                                                                               |
|:----------------------------------|:--------------------|:------------------------------------------------------------------------------------------------------|
| COLUMNAS_BLOQUE_EXISTEN_EN_5809   | OK                  | SEGUNDO_APELLIDO | NOMBRES | SEXO | FECHA_NACIMIENTO | CODIGO_UNICO                                   |
| REGISTROS_5809                    | OK                  | 2371                                                                                                  |
| SEGUNDO_APELLIDO_NO_VACIO         | OK_CON_ADVERTENCIA  | 10                                                                                                    |
| NOMBRES_NO_VACIO                  | OK                  | 0                                                                                                     |
| SEXO_NO_VACIO                     | OK                  | 0                                                                                                     |
| FECHA_NACIMIENTO_NO_VACIO         | OK                  | 0                                                                                                     |
| CODIGO_UNICO_NO_VACIO             | OK                  | 0                                                                                                     |
| CODIGO_UNICO_EXISTE_EN_5810       | OK                  | 0                                                                                                     |
| CATALOGO_SEXO_OBSERVADO           | INFORMATIVO         | H:1753 | M:618                                                                                        |
| FECHA_NACIMIENTO_PARSEABLE        | OK                  | 0                                                                                                     |
| DUPLICADOS_DOCUMENTO_CODIGO_UNICO | OK                  | 0                                                                                                     |
| BLOQUE_06_10_SE_CONSTRUYE         | NO                  | Datos personales y CODIGO_UNICO vienen preparados en la precarga; CODIGO_UNICO se valida contra 5810. |
| PUEDE_USARSE_EN_ARCHIVO_SIES      | SI_PARA_ESTE_BLOQUE | Este bloque no desbloquea el archivo completo; solo valida columnas 6-10.                             |

## Conclusión

El bloque 06-10 no se construye desde fuentes académicas.  
Se conserva desde la precarga 5809 y se valida, especialmente `CODIGO_UNICO` contra Carreras 5810.  
Este bloque no autoriza el archivo completo SIES, porque los bloqueos críticos siguen en columnas académicas 16-21, planes y casos especiales.

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_06_10_20260703_232946/02_RESULTADOS/DIAGNOSTICO_BLOQUE_06_10.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_06_10_20260703_232946`
