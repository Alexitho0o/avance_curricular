# Evidencia T - SEM_ING_ORI

- Columna: T
- Campo: SEM_ING_ORI
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_sem_ing_ori.tsv
- Politica cerrada de tablero: `FOR_ING_ACT = 1`

## Regla vigente observada

- `SEM_ING_ORI` final queda igual a `SEM_ING_ACT` por politica explicita de cohorte con `FOR_ING_ACT = 1`.
- La fila incluida conserva trazabilidad en `SEM_ING_ORI_FUENTE_FINAL`, `SEM_ING_ORI_METODO_FINAL` y `SEM_ING_ORI_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `POLITICA_FOR_ING_ACT_FIJO_1 = 1.736`.
- Filas con `SEM_ING_ORI != SEM_ING_ACT`: `0`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. El riesgo queda acotado a un eventual cambio futuro del tablero cerrado.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
