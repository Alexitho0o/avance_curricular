# Evidencia R - SEM_ING_ACT

- Columna: R
- Campo: SEM_ING_ACT
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_sem_ing_act.tsv
- `ARCHIVO_LISTO_SUBIDA.DA_PERIODOINGRESO`

## Regla vigente observada

- `SEM_ING_ACT` final prioriza `DA_PERIODOINGRESO` y normaliza `3 -> 2`.
- La fila incluida conserva trazabilidad en `SEM_ING_ACT_FUENTE_FINAL`, `SEM_ING_ACT_METODO_FINAL` y `SEM_ING_ACT_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `DA_PERIODOINGRESO = 1.736`.
- Filas con default `1` en carga final: `0`.
- Catalogo final observado: `1 = 1.525`, `2 = 211`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si aparecieran valores distintos de `1/2/3` en la fuente.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
