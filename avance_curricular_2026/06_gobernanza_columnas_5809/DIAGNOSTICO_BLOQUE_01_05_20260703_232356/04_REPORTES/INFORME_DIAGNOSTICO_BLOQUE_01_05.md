# Diagnóstico Bloque 01-05 — Matrícula 5809

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

Columnas revisadas:

1. CODIGO_IES_NUM  
2. TIPO_DOCUMENTO  
3. NUM_DOCUMENTO  
4. DV  
5. PRIMER_APELLIDO  

## Resultado

Estado del bloque: **REVISAR_VACIOS**

Estas columnas corresponden a datos de identificación institucional/documental/persona. Según la gobernanza ya construida, no son campos calculados de avance curricular. Vienen desde la precarga 5809 y deben conservarse, validarse y arrastrarse al archivo de carga cuando el archivo completo esté autorizado.

## Diagnóstico funcional

Para estas columnas no corresponde calcular curso, unidades, avance anual ni acumulado.  
La pregunta no es cómo construirlas, sino si están presentes y si presentan errores críticos.

## Resultado por columna

|   ORDEN_COLUMNA | CAMPO_5809      | ESTADO_GOBERNANZA       | TIPO_CAMPO              | BLOQUEO_GOBERNANZA   |   REGISTROS_TOTAL |   NO_VACIOS |   VACIOS |   VALORES_UNICOS | MUESTRA_VALORES                                                                                             | DIAGNOSTICO                | QUE_FALTA_PARA_CONSTRUIR        | ACCION_PARA_ARCHIVO_SIES   |
|----------------:|:----------------|:------------------------|:------------------------|:---------------------|------------------:|------------:|---------:|-----------------:|:------------------------------------------------------------------------------------------------------------|:---------------------------|:--------------------------------|:---------------------------|
|               1 | CODIGO_IES_NUM  | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |                1 | 162 | 162 | 162 | 162 | 162 | 162 | 162 | 162 | 162 | 162                                                   | PREPARADA_NO_SE_CONSTRUYE  | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA   |
|               2 | TIPO_DOCUMENTO  | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |                2 | R | R | R | R | R | R | R | R | R | R                                                                       | PREPARADA_NO_SE_CONSTRUYE  | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA   |
|               3 | NUM_DOCUMENTO   | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |             2370 | 19647300 | 21956441 | 15954288 | 18783552 | 20793663 | 17873266 | 17877433 | 18662447 | 27004806 | 15430259 | PREPARADA_NO_SE_CONSTRUYE  | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA   |
|               4 | DV              | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2346 |       25 |               12 | 9 | 4 | 2 | 6 | 4 | 8 | 6 | 5 | 4 | K                                                                       | REVISAR_VACIOS_EN_PRECARGA | EXISTEN_25_VACIOS               | NO_COMPLETAR_POR_SUPUESTO  |
|               5 | PRIMER_APELLIDO | NO_MODIFICABLE_PRECARGA | NO_MODIFICABLE_PRECARGA |                      |              2371 |        2371 |        0 |              880 | LAS HERAS | GONZALEZ | LAGOS | QUINTEROS | CASTRO | DIAZ | TORRES | BAEZA | LOPEZ | ESCOBAR                 | PREPARADA_NO_SE_CONSTRUYE  | NO_FALTA_DATO_PARA_ESTA_COLUMNA | CONSERVAR_VALOR_PRECARGA   |

## Validaciones

| VALIDACION                      | RESULTADO   | DETALLE                                                                                           |
|:--------------------------------|:------------|:--------------------------------------------------------------------------------------------------|
| COLUMNAS_BLOQUE_EXISTEN_EN_5809 | OK          | CODIGO_IES_NUM | TIPO_DOCUMENTO | NUM_DOCUMENTO | DV | PRIMER_APELLIDO                            |
| REGISTROS_5809                  | OK          | 2371                                                                                              |
| CODIGO_IES_NUM_NO_VACIO         | OK          | 0                                                                                                 |
| TIPO_DOCUMENTO_NO_VACIO         | OK          | 0                                                                                                 |
| NUM_DOCUMENTO_NO_VACIO          | OK          | 0                                                                                                 |
| DV_NO_VACIO                     | REVISAR     | 25                                                                                                |
| PRIMER_APELLIDO_NO_VACIO        | OK          | 0                                                                                                 |
| DUPLICADOS_DOCUMENTO_COMPLETO   | REVISAR     | 1                                                                                                 |
| BLOQUE_01_05_SE_CONSTRUYE       | NO          | Las columnas vienen preparadas en la precarga y se conservan; no se calculan.                     |
| PUEDE_USARSE_EN_ARCHIVO_SIES    | REVISAR     | Este bloque no desbloquea el archivo completo; solo indica que las columnas 1-5 están preparadas. |

## Conclusión

Para el bloque 01-05, la información está preparada en la precarga.  
No se requiere construir datos adicionales para estas columnas.  
Esto no autoriza el archivo completo SIES, porque los bloqueos críticos siguen en columnas académicas 16-21, planes y casos especiales.

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_01_05_20260703_232356/02_RESULTADOS/DIAGNOSTICO_BLOQUE_01_05.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/DIAGNOSTICO_BLOQUE_01_05_20260703_232356`
