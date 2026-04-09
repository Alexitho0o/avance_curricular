# Reporte de Precargas - Avance Curricular SIES 2026

Fecha: 2026-06-26T00:58:26.544655-04:00 America/Santiago

## Carreras

- Archivo: `5810_Precarga Carreras Avance Curricular 20268.csv`
- Filas de datos: 43
- Columnas: 22
- Codificación: utf-8
- Delimitador: PUNTO_Y_COMA
- Primera columna: `CODIGO_IES_NUM` (COLUMNA_INSTITUCIONAL_A_ELIMINAR_SOLO_EN_PES)
- Campos faltantes oficiales: ninguno

Campos modificables: PLAN_ESTUDIOS, TIPO_UNIDAD_MEDIDA, OTRA_UNIDAD_MEDIDA, TOTAL_UNIDADES_MEDIDA, UNIDADES_1ER_ANIO, UNIDADES_2DO_ANIO, UNIDADES_3ER_ANIO, UNIDADES_4TO_ANIO, UNIDADES_5TO_ANIO, UNIDADES_6TO_ANIO, UNIDADES_7MO_ANIO, VIGENCIA

## Matrícula

- Archivo: `5809_Precarga Matrícula Avance Curricular 2026.csv`
- Filas de datos: 2371
- Columnas: 22
- Codificación: cp1252
- Delimitador: PUNTO_Y_COMA
- Primera columna: `CODIGO_IES_NUM` (COLUMNA_INSTITUCIONAL_A_ELIMINAR_SOLO_EN_PES)
- Campos faltantes oficiales: ninguno

Campos modificables: PLAN_ESTUDIOS, CURSO_1ER_SEM, CURSO_2DO_SEM, UNIDADES_CURSADAS, UNIDADES_APROBADAS, UNID_CURSADAS_TOTAL, UNID_APROBADAS_TOTAL, VIGENCIA

## Observaciones

- La columna `CODIGO_IES_NUM` se observa como primera columna institucional en ambas precargas; no se elimina en la carga congelada ni en derivados TSV.
- Los perfiles no contienen muestras reales de estudiantes.
- Los TSV derivados preservan orden de filas y columnas y se validan contra la lectura estructurada del CSV original.
