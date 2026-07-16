# H114B — Corrección de unidades aprobadas acumuladas

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Matrícula Avance Curricular 2026 — ID 16768.

## Año de referencia

2025.

## Regla aplicada

El avance se mantiene asociado a la carrera y plan informados en Matrícula 2025.

El total aprobado acumulado no puede superar el total de unidades del plan gobernado en Carreras H112B ni las unidades cursadas acumuladas del estudiante.

## Transformación

Se modificó exclusivamente `UNID_APROBADAS_TOTAL`.

Fórmula aplicada:

`min(UNID_APROBADAS_TOTAL original, TOTAL_UNIDADES_MEDIDA, UNID_CURSADAS_TOTAL)`

La conversión de períodos académicos y la distribución anual de las carreras no fueron recalculadas. Se utilizó el resultado H112B previamente gobernado.

## Resultado

- Filas: 2371
- Columnas: 21
- Registros corregidos: 247
- Personas únicas corregidas: 247
- Otros campos modificados: 0
- Aprobadas totales sobre total del plan después: 0
- Aprobadas totales sobre cursadas totales después: 0
- Excesos sobre 125% después: 0

## Dictamen

`CSV_H114B_CORREGIDO_PARA_PRUEBA_PES`

## Archivo de prueba PES

`/Users/alexi/Desktop/5809_MATRICULA_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16768_H114B_CORREGIDO_PLAN.csv`

## Auditoría

`/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/114b_correccion_aprobadas_total_segun_plan_matricula_16768/CORRECCION_APROBADAS_TOTAL_SEGUN_PLAN_MATRICULA_16768_20260710_130853/AUDITORIA_CORRECCION_APROBADAS_TOTAL_SEGUN_PLAN_H114B.xlsx`
