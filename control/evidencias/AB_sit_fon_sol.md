# Evidencia AB - SIT_FON_SOL

- Columna: AB
- Campo: SIT_FON_SOL
- Fase duena: FASE 5
- Estado tablero: Pendiente
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- No existe fuente real por fila incluida; `SIT_FON_SOL` queda en fallback explicito `0` para `1.736/1.736` filas incluidas.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_sit_fon_sol.tsv
- `ARCHIVO_LISTO_SUBIDA.SIT_FON_SOL_FUENTE_FINAL`
- `ARCHIVO_LISTO_SUBIDA.SIT_FON_SOL_METODO_FINAL`
- `ARCHIVO_LISTO_SUBIDA.SIT_FON_SOL_AUDIT_STATUS`

## Regla vigente observada

- El proyecto normaliza el catalogo `0/1/2`.
- En esta iteracion no existe columna fuente en `Hoja1` ni en `DatosAlumnos`.
- La salida deja visible el fallback con `SIT_FON_SOL_FUENTE_FINAL = REGLA_DEFAULT_0_SIN_FUENTE` y `SIT_FON_SOL_AUDIT_STATUS = DEFAULT_0_SIN_FUENTE`.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase5-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- Distribucion final observada: `0 = 1.736`.
- Fallback explicito `DEFAULT_0_SIN_FUENTE` en `1.736/1.736` filas incluidas.
- Gate binario observado: `NO / SI / SI / SI / SI`.

## Resultado

- Estado final: `Pendiente`.

## Riesgo residual

- Alto. El valor actual es auditable, pero no defendible como situacion FSCU real por fila.

## Criterio de cierre a OK

- Contar con fuente institucional o regla formal que distinga `0/1/2` por fila incluida.

## Evidencia adjunta

- `control/reportes/reporte_fase_5_estado_admin_mu_2026.md`
- `control/reportes/reporte_estado_admin_mu_2026.json`
- `resultados/archivo_listo_para_sies.xlsx`
