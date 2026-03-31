# Evidencia A - TIPO_DOC

- Columna: A
- Campo: TIPO_DOC
- Fase duena: FASE 1
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_tipo_doc.tsv

## Regla vigente observada

- `TIPO_DOC` queda fijo en `R` para las 1.736 filas incluidas en carga final.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py`.
- Distribucion final observada: `R = 1.736`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Solo monitoreo de no degradacion si aparece una casuistica distinta de `R`.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_1_identidad_mu_2026.md`
- `control/reportes/reporte_identidad_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
- `resultados/matricula_unificada_2026_pregrado.csv`
