# Evidencia S - ANIO_ING_ORI

- Columna: S
- Campo: ANIO_ING_ORI
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-19
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_anio_ing_ori.tsv
- control/reportes/reporte_cronologia_mu_2026.json
- resultados/archivo_listo_para_sies.xlsx

## Regla vigente observada

- Para `FOR_ING_ACT = 1`, `ANIO_ING_ORI` replica `ANIO_ING_ACT`.
- Para continuidad/cambio (`FOR` en `{2,3,4,5,11}`), el origen se toma desde traza previa o fallback `1900` cuando el origen no es fechable.
- Si el runtime preserva otro código gobernado fuera de ese bloque, el valor se conserva con su propia traza en vez de forzarse a `1`.
- La fila incluida conserva trazabilidad en `ANIO_ING_ORI_FUENTE_FINAL`, `ANIO_ING_ORI_METODO_FINAL` y `ANIO_ING_ORI_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `3433`.
- Filas `FOR_ING_ACT = 1` con origen igual al actual: `2926`.
- Filas continuidad/cambio con regla ORI validada: `499`.
- Filas con `ANIO_ING_ORI != ANIO_ING_ACT`: `499`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. El riesgo queda acotado a nuevos códigos no directos sin traza suficiente o a una redefinición funcional de origen para códigos hoy no observados.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
