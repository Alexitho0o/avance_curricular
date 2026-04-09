# Auditoría transversal gobernanza SIES vs carga MU2026

Generado: 2026-06-25T17:58:08

| Indicador | Total |
|---|---:|
| Registros finales auditados | 4115 |
| Registros completamente coherentes | 0 |
| Código final explícito | 4114 |
| Código final vacío | 1 |
| Pendiente gobernanza incluido | 1 |
| Código reconstruido dentro de candidatos | 4040 |
| Código reconstruido fuera de candidatos | 75 |
| Final sin candidatos | 0 |
| Candidatos sin final | 1 |
| Diferencias staging vs final | 0 |
| VERSION completada desde vacío | 0 |
| VERSION reemplazada | 0 |
| VERSION conservada | 4115 |
| VERSION sin fuente trazable | 0 |
| Código válido no justificado | 75 |
| Código incompatible con plan | 1 |
| Código incompatible con duración | 0 |
| Código incompatible con tipo de plan | 1 |
| Código inexistente en oferta | 0 |
| Componentes incompletos | 0 |
| Casos críticos | 75 |
| Casos altos | 0 |
| Casos medios | 0 |
| Casos bajos | 4040 |
| Estudiantes afectados | 75 |
| Combinaciones afectadas | 4 |
| Carreras afectadas | 4 |
| Planes afectados | 4 |

## Caso control NETMRE016

El caso aparece dentro del universo transversal de 4.115 registros. Resultado:

- `CODIGO_CARRERA_SIES_FINAL`: vacío
- candidatos: `I162S2C3J4V1 | I162S2C3J4V2`
- gobernanza: `PENDIENTE_GOBERNANZA`
- estado carga: `OK_CARGA_PREGRADO`
- versión final: `3`
- código reconstruido: `I162S2C3J4V3`
- clasificación: `FINAL_VALIDO_FUERA_DE_CANDIDATOS | PENDIENTE_INCLUIDO`

## Causa exacta

La causa no es que SIES haya recibido una versión vacía: el CSV final informó `VERSION=3`. El problema es que la exportación final conserva la columna oficial `VERSION` ya armada aunque la resolución de gobernanza siga pendiente y `CODIGO_CARRERA_SIES_FINAL` esté vacío. La ruta responsable es la exportación de `out[MATRICULA_UNIFICADA_COLUMNS]` en `codigo_gobernanza_v2.py` alrededor de la línea 3236. La ruta trazable por parse de `CODIGO_CARRERA_SIES_FINAL` no aplica porque en NETMRE016 ese campo está vacío.

Registros con la misma ruta crítica (pendiente incluido + final fuera de candidatos): 1.

## Riesgo y recomendación

No es seguro reutilizar la lógica sin controles adicionales. Deben bloquearse `PENDIENTE_GOBERNANZA`, `CODIGO_CARRERA_SIES_FINAL` vacío en incluidos, código reconstruido fuera de candidatos y `VERSION` sin fuente/método trazable. No se generó rectificación ni PES.
