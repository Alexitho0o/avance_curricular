# Evidencia O - VERSION

- Columna: O
- Campo: VERSION
- Fase duena: FASE 2
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_version.tsv
- `ARCHIVO_LISTO_SUBIDA.CODIGO_CARRERA_SIES_FINAL`

## Regla vigente observada

- `VERSION` final se obtiene por parseo del componente version de `CODIGO_CARRERA_SIES_FINAL`.
- La fila incluida conserva trazabilidad en `VERSION_FUENTE_FINAL`, `VERSION_METODO_FINAL` y `VERSION_AUDIT_STATUS`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase2-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `CODIGO_CARRERA_SIES_FINAL = 1.736`.
- Inconsistencias `VERSION` vs parseo SIES final: `0`.
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
