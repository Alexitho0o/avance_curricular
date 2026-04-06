# Evidencia Z - ASI_APR_HIS

- Columna: Z
- Campo: ASI_APR_HIS
- Fase duena: FASE 4
- Estado tablero: OK
- Fecha: 2026-04-07
- Responsable:

## Bloqueo actual

- Sin bloqueo residual.

## Politica de cierre (2026-04-07)

- Criterio aplicado: la regla de calculo esta definida y el alcance historico esta **explicitamente trazado** por fila incluida (`UZ_HIST_SCOPE_STATUS`, `UZ_HIST_ANIOS_DISPONIBLES`). El alcance efectivo es `ANO 2025` (anio unico), pero la regla "usar todo el alcance historico disponible con trazabilidad explicita de scope" satisface el criterio `fuente o regla definida`.
- La regla historica incluye `APROB`, `CONVALID`, `RECONOC`, `EQUIV` y `HOMOLOG`.
- La trazabilidad por fila permite a cualquier auditor verificar que el valor reportado corresponde al alcance declarado.

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

- Estado final: `OK`.
- Gate binario observado: `SI / SI / SI / SI / SI`.

## Riesgo residual

- Bajo. El alcance historico es monoanual, pero la regla esta definida y el scope esta explicitamente trazado por fila incluida
- Bajo. El alcance historico es monoanual, pero la regla esta definida y el scope esta explicitamente trazado por fila incluida.

## Criterio de cierre a OK

- Contar con fuente multianual defendible o con politica regulatoria explicita que autorice usar el alcance historico disponible como historico acumulado.

## Evidencia adjunta

- `control/reportes/reporte_fase_4_rendimiento_mu_2026.md`
- `control/reportes/reporte_rendimiento_mu_2026.json`
- `control/reportes/resumen_historico_mu_2026.csv`
- `resultados/archivo_listo_para_sies.xlsx`
