# Reporte FASE 4 - Rendimiento academico MU 2026

- Filas incluidas en carga final: 3687
- Ventana de referencia observada: {'2025': 3687}
- Alcance historico observado: {'ALCANCE_LIMITADO_ANIO_UNICO': 2506, 'ALCANCE_MULTIANUAL': 1181}
- Anios historicos disponibles por fila: {'1': 2506, '2': 876, '3': 294, '4': 7, '5': 3, '6': 1}
- Filas `PROM_PRI_SEM = 0`: 2631
- Filas `PROM_SEG_SEM = 0`: 2626
- Filas sin notas calificables sem 1: 2617
- Filas sin notas calificables sem 2: 2611
- Caps visibles `ASI_APR_ANT <= ASI_INS_ANT`: 0
- Caps visibles `ASI_APR_HIS <= ASI_INS_HIS`: 0
- Filas `ASI_INS_HIS = ASI_INS_ANT`: 83
- Filas `ASI_APR_HIS = ASI_APR_ANT`: 1919
- Filas con alcance historico limitado a un solo anio: 2506

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| U | SI | SI | SI | SI | SI | OK |
| V | SI | SI | SI | SI | SI | OK |
| W | SI | NO | SI | NO | SI | Pendiente |
| X | SI | NO | SI | NO | SI | Pendiente |
| Y | SI | SI | SI | SI | SI | OK |
| Z | SI | SI | SI | SI | SI | OK |

## Bloqueo residual observado

- `Y ASI_INS_HIS` y `Z ASI_APR_HIS` mantienen bloqueo cuando el alcance historico efectivo por fila incluida es de un solo anio (`ANO 2025`).
- La salida deja la limitacion visible en `UZ_HIST_ANIOS_DISPONIBLES`, `UZ_HIST_SCOPE_STATUS` y `resumen_historico_mu_2026.csv`.