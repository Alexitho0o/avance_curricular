# Delta CNED depurado — faltantes reales 2026

## Criterio aplicado

Se depuró el delta original de 52 registros para priorizar solo programas que cumplen:

1. Están en `ARCHIVO_LISTO_SUBIDA`.
2. Tienen año observado 2026.
3. Tienen matrícula observada.
4. No aparecen en el listado CNED existente entregado por el usuario.

## Resultados

| Grupo | Total |
|---|---:|
| Delta original detectado | 52 |
| Faltantes reales 2026 con matrícula | 22 |
| Revisar oferta/catálogo sin matrícula | 17 |
| No priorizar por año anterior | 12 |
| Revisión no priorizada | 1 |

## Hoja principal

`FALTANTES_REALES_2026`

## Recomendación

Trabajar primero solo con `FALTANTES_REALES_2026`.

Las hojas de revisión no deben cargarse como nuevos programas sin validación adicional.
