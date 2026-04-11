# Evidencia T - SEM_ING_ORI

- Columna: T
- Campo: SEM_ING_ORI
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-19
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_sem_ing_ori.tsv
- control/reportes/reporte_cronologia_mu_2026.json
- resultados/archivo_listo_para_sies.xlsx

## Regla vigente observada

- Para `FOR_ING_ACT = 1`, `SEM_ING_ORI` replica `SEM_ING_ACT`.
- Para continuidad/cambio (`FOR` en `{2,3,4,5,11}`), el semestre de origen se toma desde traza previa o `0` si `ANIO_ING_ORI=1900`.
- Si el runtime preserva otro código gobernado fuera de ese bloque, el valor se conserva con su propia traza en vez de forzarse a `1`.
- La fila incluida conserva trazabilidad en `SEM_ING_ORI_FUENTE_FINAL`, `SEM_ING_ORI_METODO_FINAL` y `SEM_ING_ORI_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `3433`.
- Filas `FOR_ING_ACT = 1` con origen igual al actual: `2926`.
- Filas continuidad/cambio con regla ORI validada: `499`.
- Filas con `SEM_ING_ORI != SEM_ING_ACT`: `469`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. El riesgo queda acotado a nuevos códigos no directos sin traza suficiente o a una redefinición funcional del semestre de origen para códigos hoy no observados.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
