# Metodologia KPI Rotacion Docente SIES

## Objetivo

Documentar la linea base historica 2022-2026 del KPI de rotacion docente para Personal Academico SIES.

## Definicion SIES

La tasa de rotacion corresponde a la proporcion de academicos presentes en el anio base t que ya no figuran contratados en la misma institucion en t+1, respecto del total de academicos del anio base.

## Unidad y clave

La unidad de analisis es la persona. La identidad se construye exclusivamente con `TIPO_DOCUMENTO`, `NUM_DOCUMENTO` y `DV`. Nombres y apellidos solo sirven para auditoria, no para fusionar identidades.

## Formula

- `PERMANECEN = UNIVERSO_t interseccion UNIVERSO_t+1`
- `ROTAN = UNIVERSO_t - UNIVERSO_t+1`
- `NUEVOS = UNIVERSO_t+1 - UNIVERSO_t`
- `TASA_ROTACION_SIES = ROTAN / DOTACION_BASE * 100`

Los nuevos ingresos no participan en la tasa oficial. No se usa promedio de dotaciones, formula clasica de RR.HH. ni ponderacion por horas.

## Reingresos y movilidad

Los reingresos posteriores no corrigen retrospectivamente la rotacion anual. La movilidad describe cambios de atributos para personas que permanecen y no altera la permanencia.

## Limites interpretativos

Rotacion significa ausencia en el anio siguiente. No equivale necesariamente a renuncia, despido o salida definitiva. La serie es descriptiva censal, no causal ni inferencial.
