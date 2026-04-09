# Solicitud institucional de datos para distribución anual de créditos

Proceso: Avance Curricular SIES 2026.  
Carga: Carreras.  
Motivo: 33 códigos únicos continúan bloqueados porque no existe una relación explícita disponible entre plan, asignatura y semestre/año curricular.

## Tabla solicitada

- CODCARR
- CODPESTUD
- código de asignatura
- nombre de asignatura
- créditos
- semestre curricular o año curricular
- versión del plan
- vigencia del plan
- fecha de extracción
- definición del campo semestre/año
- fuente de origen

## Planes afectados

ADMP20251, AUDT20251, CIIND20251, CONG20251, IADM20241, ICDA20251, ICIB20241, ICRE20241, IINF20241, ILOG20241, TAMD20241, TCRE20241, TENS20251, TLOG20241, TMIRE20171, TPAS20241

## CODIGO_UNICO bloqueados

I162S2C1J1V1, I162S2C1J1V2, I162S2C1J2V1, I162S2C1J2V4, I162S2C1J4V2, I162S2C3J2V1, I162S2C3J2V4, I162S2C3J4V2, I162S2C46J1V1, I162S2C46J2V1, I162S2C46J4V3, I162S2C47J4V1, I162S2C57J1V1, I162S2C57J2V1, I162S2C57J4V1, I162S2C6J2V1, I162S2C6J2V2, I162S2C6J4V2, I162S2C76J2V1, I162S2C76J4V1, I162S2C77J2V1, I162S2C77J4V1, I162S2C78J2V1, I162S2C78J4V1, I162S2C79J2V1, I162S2C79J4V1, I162S2C83J4V1, I162S2C85J4V1, I162S2C86J4V1, I162S2C87J4V1, I162S2C88J4V1, I162S2C91J1V1, I162S2C91J2V1

## Cantidad de asignaturas canónicas involucradas

592

## Razón por la que NIVEL no es suficiente

La auditoría `INVESTIGACION_SEMANTICA_NIVEL_PLANES_20260701_191051` determinó que `NIVEL` no cuenta con definición explícita, no tiene origen técnico encontrado, toma valores entre 1 y 20 y no demuestra equivalencia con semestre ni año curricular.

## Impacto sobre la carga SIES

Sin una relación explícita `CODPESTUD -> código de asignatura -> semestre/año curricular`, no es posible completar de forma trazable las columnas `UNIDADES_1ER_ANIO` a `UNIDADES_7MO_ANIO` para los 33 casos bloqueados.
