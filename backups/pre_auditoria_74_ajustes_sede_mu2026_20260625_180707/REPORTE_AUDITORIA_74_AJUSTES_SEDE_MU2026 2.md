# Auditoría 74 ajustes de sede gobernanza MU2026

Generado: 2026-06-25T18:06:51

Esta auditoría excluye explícitamente `20171NETMRE016` y analiza solo los registros con `AJUSTE_SEDE_GOBERNANZA`, código final explícito y código reconstruido fuera de candidatos.

## Resumen

| Indicador | Total |
|---|---:|
| Registros auditados | 477 |
| Código correcto con candidatos preajuste | 0 |
| Código correcto con candidatos no regenerados | 477 |
| Código correcto con trazabilidad incompleta | 0 |
| Ajuste de sede no justificado | 0 |
| Código final no compatible | 0 |
| Información insuficiente | 0 |
| Casos bajos | 477 |
| Casos medios | 0 |
| Casos altos | 0 |
| Casos críticos | 0 |
| Estudiantes con posible error real | 0 |
| Carreras afectadas | 3 |
| Planes afectados | 3 |
| Combinaciones afectadas | 3 |

## Conclusión diagnóstica

Los 74 registros corresponden a códigos finales compatibles con la sede final. Los candidatos originales quedaron en la sede previa (`S2`) y no fueron regenerados después del ajuste hacia la sede final (`S3`). El código final aparece al regenerar candidatos con la sede final usando la misma combinación C/J/V contra `DURACION_ESTUDIOS.tsv`.

La causa es de orden de ejecución: `CODIGOS_SIES_POTENCIALES` se construye antes del ajuste de sede; luego `AJUSTE_SEDE_GOBERNANZA` reemplaza `CODIGO_CARRERA_SIES_FINAL` por un código equivalente de oferta para la sede solicitada, pero la columna de candidatos conserva el valor preajuste.

## Impacto consolidado 4.115

| Grupo | Registros |
|---|---:|
| Completamente coherentes | 4040 |
| Ajustes de sede correctos, solo trazabilidad | 477 |
| Ajustes de sede con posible error | 0 |
| NETMRE016 crítico | 1 |
| Total | 4115 |

No se modificaron archivos productivos, no se generó rectificación, V7 ni PES.
