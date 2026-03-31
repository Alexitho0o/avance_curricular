# Evidencia AA - NIV_ACA

- Columna: AA
- Campo: NIV_ACA
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_niv_aca.tsv
- `ARCHIVO_LISTO_SUBIDA.INPUT_NIVEL`
- `ARCHIVO_LISTO_SUBIDA.DURACION_ESTUDIOS_REF`

## Regla vigente observada

- `NIV_ACA` final se alimenta desde `INPUT_NIVEL`.
- El valor final queda acotado por `DURACION_ESTUDIOS_REF`.
- Para cohorte `2026`, el valor final queda limitado a `<= 2`.
- La fila incluida conserva trazabilidad en `NIV_ACA_FUENTE_FINAL`, `NIV_ACA_METODO_FINAL` y `NIV_ACA_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `INPUT_NIVEL = 1.736`.
- Defaults `1` por falta de fuente: `0`.
- Ajustes por duracion: `263`.
- Ajustes por cohorte `2026`: `8`.
- Filas con `NIV_ACA > DURACION_ESTUDIOS_REF`: `0`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si cambia la duracion de referencia o la politica de cohorte.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `control/reportes/reporte_niv_fecha_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
