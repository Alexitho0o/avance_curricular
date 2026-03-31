# Evidencia L - COD_CAR

- Columna: L
- Campo: COD_CAR
- Fase duena: FASE 2
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_cod_car.tsv
- `ARCHIVO_LISTO_SUBIDA.CODIGO_CARRERA_SIES_FINAL`

## Regla vigente observada

- `COD_CAR` final se obtiene por parseo del componente carrera de `CODIGO_CARRERA_SIES_FINAL`.
- La fila incluida conserva trazabilidad en `COD_CAR_FUENTE_FINAL`, `COD_CAR_METODO_FINAL` y `COD_CAR_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase2-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `CODIGO_CARRERA_SIES_FINAL = 1.736`.
- Inconsistencias `COD_CAR` vs parseo SIES final: `0`.
- Filas incluidas con `PRIMERA_OPCION`: `0`.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo para filas incluidas.
- La cola auditable pendiente fuera de la promocion final queda en `control/reportes/sies_pendientes.tsv`.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_2_sies_oferta_mu_2026.md`
- `control/reportes/reporte_sies_oferta_mu_2026.json`
- `control/reportes/sies_pendientes.tsv`
- `resultados/archivo_listo_para_sies.xlsx`
