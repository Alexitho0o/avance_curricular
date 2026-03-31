# Reporte FASE 4 - Rendimiento academico MU 2026

- Filas incluidas en carga final: 1736
- Ventana de referencia observada: {'2025': 1736}
- Alcance historico observado: {'ALCANCE_LIMITADO_ANIO_UNICO': 1736}
- Anios historicos disponibles por fila: {'1': 1736}
- Filas `PROM_PRI_SEM = 0`: 148
- Filas `PROM_SEG_SEM = 0`: 425
- Filas sin notas calificables sem 1: 148
- Filas sin notas calificables sem 2: 425
- Caps visibles `ASI_APR_ANT <= ASI_INS_ANT`: 0
- Caps visibles `ASI_APR_HIS <= ASI_INS_HIS`: 0
- Filas `ASI_INS_HIS = ASI_INS_ANT`: 1736
- Filas `ASI_APR_HIS = ASI_APR_ANT`: 1445
- Filas con alcance historico limitado a un solo anio: 1736

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| U | SI | SI | SI | SI | SI | OK |
| V | SI | SI | SI | SI | SI | OK |
| W | SI | SI | SI | SI | SI | OK |
| X | SI | SI | SI | SI | SI | OK |
| Y | NO | SI | SI | SI | SI | Pendiente |
| Z | NO | SI | SI | SI | SI | Pendiente |

## Bloqueo residual observado

- `Y ASI_INS_HIS` y `Z ASI_APR_HIS` mantienen bloqueo cuando el alcance historico efectivo por fila incluida es de un solo anio (`ANO 2025`).
- La salida deja la limitacion visible en `UZ_HIST_ANIOS_DISPONIBLES`, `UZ_HIST_SCOPE_STATUS` y `resumen_historico_mu_2026.csv`.