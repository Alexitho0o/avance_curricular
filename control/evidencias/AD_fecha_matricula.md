# Evidencia AD - FECHA_MATRICULA

- Columna: AD
- Campo: FECHA_MATRICULA
- Fase duena: FASE 3
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_fecha_matricula.tsv
- `ARCHIVO_LISTO_SUBIDA.DA_FECHAMATRICULA`
- Politica cerrada de cohorte `ANIO_ING_ORI = 2026`

## Regla vigente observada

- `FECHA_MATRICULA` final solo aplica a cohorte de origen `2026`.
- Fuera de cohorte `2026`, el valor final queda en `01/01/1900` por politica explicita.
- En cohorte `2026`, el valor final usa `DA_FECHAMATRICULA`.
- La fila incluida conserva trazabilidad en `FECHA_MATRICULA_FUENTE_FINAL`, `FECHA_MATRICULA_METODO_FINAL` y `FECHA_MATRICULA_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase3-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `POLITICA_COHORTE_ORIGEN_2026 = 1.724`, `DA_FECHAMATRICULA = 12`.
- Filas `01/01/1900` fuera de cohorte `2026`: `1.724`.
- Filas `01/01/1900` dentro de cohorte `2026`: `0`.
- Filas con fecha real fuera de cohorte `2026`: `0`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo si cambian la politica de cohorte o la fuente `DA_FECHAMATRICULA`.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_3_cronologia_mu_2026.md`
- `control/reportes/reporte_cronologia_mu_2026.json`
- `control/reportes/reporte_niv_fecha_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
