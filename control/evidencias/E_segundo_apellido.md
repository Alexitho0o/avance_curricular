# Evidencia E - SEGUNDO_APELLIDO

- Columna: E
- Campo: SEGUNDO_APELLIDO
- Fase duena: FASE 1
- Estado tablero: OK
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_segundo_apellido.tsv

## Regla vigente observada

- `SEGUNDO_APELLIDO` usa input, fallback `DatosAlumnos` y vacio permitido trazado con `SEGUNDO_APELLIDO_STATUS`.

## Validacion ejecutada

- QA sobre 1.736 filas incluidas.
- Vacios permitidos trazados: `2` filas (`0.12%`).
- El resto queda con fuente o fallback auditado.

## Resultado

- 5/5 `SI`.
- Estado final: `OK`.

## Riesgo residual

- Bajo. Mantener monitoreo de vacios permitidos.

## Criterio de cierre a OK

- Cumplido en esta iteracion.

## Evidencia adjunta

- `control/reportes/reporte_fase_1_identidad_mu_2026.md`
- `control/reportes/reporte_identidad_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
