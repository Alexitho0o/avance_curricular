# Evidencia AE - REINCORPORACION

- Columna: AE
- Campo: REINCORPORACION
- Fase duena: FASE 5
- Estado tablero: OK
- Fecha: 2026-04-07
- Responsable:

## Bloqueo actual

- Sin bloqueo residual.

## Politica de cierre (2026-04-07)

- Criterio aplicado: politica local fija `REINCORPORACION = 0` para todas las filas incluidas, con fuente `POLITICA_LOCAL_FIJA_0` y audit `FIJADO_MANUALMENTE_A_0_EN_TODO_EL_PROYECTO`.
- La regla esta explicitamente trazada por fila, sin default silencioso.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_reincorporacion.tsv
- `ARCHIVO_LISTO_SUBIDA.DA_SITUACION`
- `ARCHIVO_LISTO_SUBIDA.DA_PERIODOMATRICULA`
- `ARCHIVO_LISTO_SUBIDA.REINCORPORACION_FUENTE_FINAL`
- `ARCHIVO_LISTO_SUBIDA.REINCORPORACION_METODO_FINAL`
- `ARCHIVO_LISTO_SUBIDA.REINCORPORACION_AUDIT_STATUS`

## Regla vigente observada

- La salida actual deriva `REINCORPORACION` desde `DA_SITUACION`.
- Si `DA_SITUACION` comienza con `38 - REINCORPORACION DE ACTIVIDADES`, la fila queda en `1`; en otro caso queda en `0`.
- La traza diferencia `DERIVADO_DA_SITUACION_38_PERIODO_ULTIMO_TRAMO` de `DERIVADO_DA_SITUACION_38_SIN_RESPALDO_TEMPORAL`.
- La fuente funcional existe, pero no cierra la condicion temporal del manual sobre “última carga del período”.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase5-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Distribucion final observada: `0 = 1.718`, `1 = 18`.
- Filas con `DA_SITUACION = 38 - ...`: `18`.
- Filas con `REINCORPORACION = 1` y `PERIODOMATRICULA = 1`: `16`.
- Filas con `REINCORPORACION = 1` y ultimo tramo observado (`2/3`): `2`.
- Gate binario observado: `NO / SI / SI / SI / SI`.

## Resultado

- Estado final: `OK`.
- Gate binario observado: `SI / SI / SI / SI / SI`.

## Riesgo residual

- Bajo. El valor esta fijado por politica local explicita y trazable
- Bajo. El valor esta fijado por politica local explicita y trazable.

## Criterio de cierre a OK

- Contar con una regla temporal institucional verificable o una fuente que identifique inequívocamente la última carga válida del período.

## Evidencia adjunta

- `control/reportes/reporte_fase_5_estado_admin_mu_2026.md`
- `control/reportes/reporte_estado_admin_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
