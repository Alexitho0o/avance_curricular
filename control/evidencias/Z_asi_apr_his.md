# Evidencia Z - ASI_APR_HIS

- Columna: Z
- Campo: ASI_APR_HIS
- Fase duena: FASE 4
- Estado tablero: Pendiente
- Fecha: 2026-04-01
- Responsable:

## Bloqueo actual

- Alcance historico efectivo disponible en `Hoja1` = solo `ANO 2025`; no existe profundidad multianual para sostener un acumulado historico defendible.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_asi_apr_his.tsv
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_KEY`
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_ANIOS_DISPONIBLES`
- `ARCHIVO_LISTO_SUBIDA.UZ_HIST_SCOPE_STATUS`

## Regla vigente observada

- La salida actual calcula `ASI_APR_HIS` por llave `RUT_NORM + CODCARPR_NORM` usando `COUNT_DISTINCT_CODRAMO_APROB_O_EQUIV_ALCANCE_HIST_DISPONIBLE`.
- La regla historica incluye `APROB`, `CONVALID`, `RECONOC`, `EQUIV` y `HOMOLOG`.
- La traza deja visible que el alcance historico efectivo por fila incluida es `ALCANCE_LIMITADO_ANIO_UNICO`.
- Eso permite auditoria, pero no cierra la semantica exigida de historico acumulado multianual.

## Validacion ejecutada

- Ejecucion oficial de `codigo_gobernanza_v2.py --proceso matricula --usar-gobernanza-v2 true`.
- QA extendida en `qa_checks.py --fase4-control-dir control`.
- Filas incluidas evaluadas: `1.736`.
- `UZ_HIST_ANIOS_DISPONIBLES = 1` en `1.736/1.736` filas incluidas.
- `UZ_HIST_SCOPE_STATUS = ALCANCE_LIMITADO_ANIO_UNICO` en `1.736/1.736` filas incluidas.
- `ASI_APR_HIS = ASI_APR_ANT` en `1.445/1.736` filas incluidas; la diferencia restante responde a la inclusion explicita de homologaciones/convalidaciones/equivalencias en `Z`.
- Gate binario observado: `NO / SI / SI / SI / SI`.

## Resultado

- Estado final: `Pendiente`.

## Riesgo residual

- Alto. El valor actual es auditable, pero no defendible como historico acumulado pleno.

## Criterio de cierre a OK

- Contar con fuente multianual defendible o con politica regulatoria explicita que autorice usar el alcance historico disponible como historico acumulado.

## Evidencia adjunta

- `control/reportes/reporte_fase_4_rendimiento_mu_2026.md`
- `control/reportes/reporte_rendimiento_mu_2026.json`
- `control/reportes/resumen_historico_mu_2026.csv`
- `resultados/archivo_listo_para_sies.xlsx`
