# Evidencia Q - ANIO_ING_ACT

- Columna: Q
- Campo: ANIO_ING_ACT
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_anio_ing_act.tsv
- `ARCHIVO_LISTO_SUBIDA.DA_ANOINGRESO`

## Regla vigente observada

- `ANIO_ING_ACT` final prioriza `DA_ANOINGRESO` para la cohorte incluida.
- Si la fuente faltara o fuera invalida, la traza deja visible el fallback autorizado; en esta iteracion no hubo defaults `2026` en filas incluidas.
- La fila incluida conserva trazabilidad en `ANIO_ING_ACT_FUENTE_FINAL`, `ANIO_ING_ACT_METODO_FINAL` y `ANIO_ING_ACT_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `DA_ANOINGRESO = 1.736`.
- Filas con default `2026` en carga final: `0`.
- Rango valido `1990..2026` en `1.736/1.736` filas incluidas.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo de no degradacion si aparecieran filas sin `DA_ANOINGRESO`.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
