# Evidencia X - PROM_SEG_SEM

- Columna: X
- Campo: PROM_SEG_SEM
- Fase duena: FASE 4
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_prom_seg_sem.tsv
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_KEY`
- `ARCHIVO_LISTO_SUBIDA.ANIO_REFERENCIA_HIST_UZ`
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_FILAS_REF_SEM2_CALIFICADAS`

## Regla vigente observada

- `PROM_SEG_SEM` final se calcula por llave `RUT_NORM + CODCARPR_NORM`.
- La ventana efectiva usada es el anio de referencia maximo disponible en `Hoja1`; en esta iteracion fue `2025`.
- La formula aplicada es `AVG_NOTA_MU_SEM2_ANIO_REFERENCIA_EXCL_EQUIV`.
- La escala final queda acotada a `0` o `100..700`.
- Un `0` solo es admisible cuando la fila queda marcada como `SIN_NOTAS_CALIFICABLES_SEM2_ANIO_REF`.
- La fila incluida conserva trazabilidad en `PROM_SEG_SEM_FUENTE_FINAL`, `PROM_SEG_SEM_METODO_FINAL` y `PROM_SEG_SEM_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase4-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `HISTORICO_HOJA1_ANIO_2025 = 1.736`.
- Filas con `PROM_SEG_SEM = 0`: `425`.
- Filas con `0` explicitamente justificadas por falta de notas calificables: `425`.
- Rango valido `0 | 100..700` en `1.736/1.736` filas incluidas.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si cambia la normalizacion de escala o el tratamiento de equivalencias.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_4_rendimiento_mu_2026.md`
- `control/reportes/reporte_rendimiento_mu_2026.json`
- `control/reportes/resumen_historico_mu_2026.csv`
- `resultados/archivo_listo_para_sies.xlsx`
