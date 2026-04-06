# Evidencia AC - SUS_PRE

- Columna: AC
- Campo: SUS_PRE
- Fase duena: FASE 5
- Estado tablero: OK
- Fecha: 2026-04-07
- Responsable:

## Bloqueo actual

- Sin bloqueo residual.

## Politica de cierre (2026-04-07)

- Criterio aplicado: politica local fija `SUS_PRE = 0` para todas las filas incluidas, con fuente `POLITICA_LOCAL_FIJA_0` y audit `FIJADO_MANUALMENTE_A_0_EN_TODO_EL_PROYECTO`.
- La regla esta explicitamente trazada por fila, sin default silencioso.

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

- Estado final: `OK`.
- Gate binario observado: `SI / SI / SI / SI / SI`.

## Riesgo residual

- Bajo. El valor esta fijado por politica local explicita y trazable
- Bajo. El valor esta fijado por politica local explicita y trazable.

## Criterio de cierre a OK

- Contar con fuente institucional o regla formal que cuantifique suspensiones previas por fila incluida.

## Evidencia adjunta

- `control/reportes/reporte_fase_5_estado_admin_mu_2026.md`
- `control/reportes/reporte_estado_admin_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
