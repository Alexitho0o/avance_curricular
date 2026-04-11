# Reporte FASE 4 - Rendimiento academico MU 2026

- Filas incluidas en carga final: 3433
- Ventana de referencia observada: {'2025': 3433}
- Alcance historico observado: {'ALCANCE_LIMITADO_ANIO_UNICO': 2351, 'ALCANCE_MULTIANUAL': 1082}
- Anios historicos disponibles por fila: {'1': 2351, '2': 1082}
- Filas `PROM_PRI_SEM = 0`: 2355
- Filas `PROM_SEG_SEM = 0`: 2359
- Filas sin notas calificables sem 1: 2350
- Filas sin notas calificables sem 2: 2354
- Caps visibles `ASI_APR_ANT <= ASI_INS_ANT`: 0
- Caps visibles `ASI_APR_HIS <= ASI_INS_HIS`: 0
- Filas `ASI_INS_HIS = ASI_INS_ANT`: 2120
- Filas `ASI_APR_HIS = ASI_APR_ANT`: 3351
- Filas con alcance historico limitado a un solo anio: 2351

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| U | SI | SI | SI | SI | SI | OK |
| V | SI | SI | SI | SI | SI | OK |
| W | SI | SI | SI | SI | SI | OK |
| X | SI | SI | SI | SI | SI | OK |
| Y | SI | NO | SI | SI | SI | Pendiente |
| Z | SI | NO | SI | SI | SI | Pendiente |

## Bloqueo residual observado

- `Y ASI_INS_HIS` y `Z ASI_APR_HIS` mantienen bloqueo cuando el alcance historico efectivo por fila incluida es de un solo anio (`ANO 2025`).
- La salida deja la limitacion visible en `UZ_HIST_ANIOS_DISPONIBLES`, `UZ_HIST_SCOPE_STATUS` y `resumen_historico_mu_2026.csv`.