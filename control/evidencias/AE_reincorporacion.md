# Evidencia AE - REINCORPORACION

- Columna: AE
- Campo: REINCORPORACION
- Fase duena: FASE 5
- Estado tablero: Pendiente
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- La derivacion desde `DA_SITUACION = 38 - ...` no cierra la condicion temporal del manual; `16/18` filas con `REINCORPORACION = 1` caen en `PERIODOMATRICULA = 1`.

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

- Estado final: `Pendiente`.

## Riesgo residual

- Alto. La regla actual es auditable, pero no defendible como cierre del criterio funcional/temporal del manual.

## Criterio de cierre a OK

- Contar con una regla temporal institucional verificable o una fuente que identifique inequívocamente la última carga válida del período.

## Evidencia adjunta

- `control/reportes/reporte_fase_5_estado_admin_mu_2026.md`
- `control/reportes/reporte_estado_admin_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
