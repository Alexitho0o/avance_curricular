# Evidencia N - JOR

- Columna: N
- Campo: JOR
- Fase duena: FASE 2
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_jor.tsv
- Oferta academica enriquecida por `CODIGO_CARRERA_SIES_FINAL`

## Regla vigente observada

- `JOR` final prioriza lookup en oferta academica por `CODIGO_CARRERA_SIES_FINAL`.
- La fila incluida conserva trazabilidad en `JOR_FUENTE_FINAL`, `JOR_METODO_FINAL` y `JOR_AUDIT_STATUS`.
- El resultado final queda consistente con el componente jornada del codigo SIES final.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase2-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Fuente final observada: `OFERTA_ACADEMICA = 1.736`.
- Inconsistencias `JOR` vs parseo/lookup final: `0`.
- Valores finales dentro del catalogo `1..4` en `1.736/1.736` filas incluidas.
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
