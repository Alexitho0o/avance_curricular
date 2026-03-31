# Evidencia U - ASI_INS_ANT

- Columna: U
- Campo: ASI_INS_ANT
- Fase duena: FASE 4
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_asi_ins_ant.tsv
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_KEY`
- `ARCHIVO_LISTO_SUBIDA.ANIO_REFERENCIA_HIST_UZ`
- `ARCHIVO_LISTO_SUBIDA.UZ_FUENTE_HIST`

## Regla vigente observada

- `ASI_INS_ANT` final se calcula por llave `RUT_NORM + CODCARPR_NORM`.
- La ventana efectiva usada es el anio de referencia maximo disponible en `Hoja1`; en esta iteracion fue `2025`.
- La formula aplicada es `COUNT_DISTINCT_CODRAMO_ANIO_REFERENCIA`.
- La fila incluida conserva trazabilidad en `ASI_INS_ANT_FUENTE_FINAL`, `ASI_INS_ANT_METODO_FINAL` y `ASI_INS_ANT_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase4-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `HISTORICO_HOJA1_ANIO_2025 = 1.736`.
- Rango valido `0..99` en `1.736/1.736` filas incluidas.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si cambia la profundidad historica o la llave de calculo.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_4_rendimiento_mu_2026.md`
- `control/reportes/reporte_rendimiento_mu_2026.json`
- `control/reportes/resumen_historico_mu_2026.csv`
- `resultados/archivo_listo_para_sies.xlsx`
