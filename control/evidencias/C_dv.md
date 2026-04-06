# Evidencia C - DV

- Columna: C
- Campo: DV
- Fase duena: FASE 1
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_dv.tsv

## Regla vigente observada

- `DV` se toma desde input y queda auditado contra el calculo esperado del RUT.

## Validacion ejecutada

- QA sobre 1.736 filas incluidas.
- `DV` invalido: `0` filas (`0.0%`).
- Regla condicional con `TIPO_DOC = R` validada sin desvio.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Solo monitoreo de no degradacion.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_1_identidad_mu_2026.md`
- `control/reportes/reporte_identidad_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
