# Evidencia V - ASI_APR_ANT

- Columna: V
- Campo: ASI_APR_ANT
- Fase duena: FASE 4
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_asi_apr_ant.tsv
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_KEY`
- `ARCHIVO_LISTO_SUBIDA.ANIO_REFERENCIA_HIST_UZ`
- `ARCHIVO_LISTO_SUBIDA.UZ_FUENTE_HIST`

## Regla vigente observada

- `ASI_APR_ANT` final se calcula por llave `RUT_NORM + CODCARPR_NORM`.
- La ventana efectiva usada es el anio de referencia maximo disponible en `Hoja1`; en esta iteracion fue `2025`.
- La formula aplicada es `COUNT_DISTINCT_CODRAMO_APROB_ANIO_REFERENCIA_EXCL_EQUIV`.
- Las convalidadas, homologadas, equivalencias y reconocimientos quedan fuera del conteo anual de aprobadas.
- La fila incluida conserva trazabilidad en `ASI_APR_ANT_FUENTE_FINAL`, `ASI_APR_ANT_METODO_FINAL` y `ASI_APR_ANT_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase4-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `HISTORICO_HOJA1_ANIO_2025 = 1.736`.
- Regla `ASI_APR_ANT <= ASI_INS_ANT` valida en `1.736/1.736` filas incluidas.
- Caps visibles aplicados en carga final: `0`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si cambia el tratamiento historico de equivalencias.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_4_rendimiento_mu_2026.md`
- `control/reportes/reporte_rendimiento_mu_2026.json`
- `control/reportes/resumen_historico_mu_2026.csv`
- `resultados/archivo_listo_para_sies.xlsx`
