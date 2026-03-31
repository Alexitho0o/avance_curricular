# Evidencia AC - SUS_PRE

- Columna: AC
- Campo: SUS_PRE
- Fase duena: FASE 5
- Estado tablero: Pendiente
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- No existe fuente real por fila incluida; `SUS_PRE` queda en fallback explicito `0` para `1.736/1.736` filas incluidas.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_sus_pre.tsv
- `ARCHIVO_LISTO_SUBIDA.SUS_PRE_FUENTE_FINAL`
- `ARCHIVO_LISTO_SUBIDA.SUS_PRE_METODO_FINAL`
- `ARCHIVO_LISTO_SUBIDA.SUS_PRE_AUDIT_STATUS`

## Regla vigente observada

- El proyecto normaliza `SUS_PRE` en rango `0..99`.
- En esta iteracion no existe columna fuente en `Hoja1` ni en `DatosAlumnos`.
- La salida deja visible el fallback con `SUS_PRE_FUENTE_FINAL = REGLA_DEFAULT_0_SIN_FUENTE` y `SUS_PRE_AUDIT_STATUS = DEFAULT_0_SIN_FUENTE`.
- No hubo filas forzadas a `0` por politica de cohorte 2026; el total observado proviene de ausencia de fuente.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase5-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Distribucion final observada: `0 = 1.736`.
- Fallback explicito `DEFAULT_0_SIN_FUENTE` en `1.736/1.736` filas incluidas.
- Filas forzadas a `0` por politica de cohorte 2026: `0`.
- Gate binario observado: `NO / SI / SI / SI / SI`.

## Resultado

- Estado final: `Pendiente`.

## Riesgo residual

- Alto. El valor actual es auditable, pero no defendible como conteo real de suspensiones previas por fila.

## Criterio de cierre a OK

- Contar con fuente institucional o regla formal que cuantifique suspensiones previas por fila incluida.

## Evidencia adjunta

- `control/reportes/reporte_fase_5_estado_admin_mu_2026.md`
- `control/reportes/reporte_estado_admin_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
