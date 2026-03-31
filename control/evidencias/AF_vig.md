# Evidencia AF - VIG

- Columna: AF
- Campo: VIG
- Fase duena: FASE 5
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_vig.tsv
- `ARCHIVO_LISTO_SUBIDA.DA_SITUACION`
- `ARCHIVO_LISTO_SUBIDA.VIG_FUENTE_FINAL`
- `ARCHIVO_LISTO_SUBIDA.VIG_METODO_FINAL`
- `ARCHIVO_LISTO_SUBIDA.VIG_AUDIT_STATUS`

## Regla vigente observada

- La salida final usa una politica explicita por fila incluida.
- Si la fila incluida queda con `DA_SITUACION = 31 - TITULADO APROBADO`, entonces `VIG = 2`.
- Si la fila incluida queda en carga final y no está en esa situacion, entonces `VIG = 1`.
- La traza distingue `POLITICA_CARGA_PREGRADO_VIG_1` y `POLITICA_CARGA_PREGRADO_VIG_2_TITULADO`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase5-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Distribucion final observada: `VIG = 1` en `1.502` filas y `VIG = 2` en `234` filas.
- Filas `DA_SITUACION = 31 - TITULADO APROBADO`: `234`.
- Consistencia observada: `234/234` filas tituladas incluidas quedan con `VIG = 2`; `1.502/1.502` filas incluidas no tituladas quedan con `VIG = 1`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si cambia la política institucional de vigencia o la señal `DA_SITUACION`.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_5_estado_admin_mu_2026.md`
- `control/reportes/reporte_estado_admin_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
