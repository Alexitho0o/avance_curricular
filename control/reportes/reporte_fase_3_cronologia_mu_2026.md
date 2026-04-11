# Reporte FASE 3 - Cronologia MU 2026

- Filas incluidas en carga final: 3433
- Distribucion `FOR_ING_ACT` en filas incluidas: {'1': 2926, '2': 383, '3': 84, '11': 32, '6': 8}
- Fuentes `ANIO_ING_ACT`: {'DA_ANOINGRESO': 3433}
- Fuentes `SEM_ING_ACT`: {'DA_PERIODOINGRESO': 3433}
- Fuentes `ANIO_ING_ORI`: {'POLITICA_FOR_ING_ACT_1': 2926, 'POLITICA_FOR_ING_ACT_2': 383, 'POLITICA_FOR_ING_ACT_3_SIN_PROGRAMA_ANTERIOR_FECHABLE': 80, 'TRACE_MOTOR_FOR_ING_ACT:TNS_PREV_MIN_ANO_DA': 34, 'PRESERVADO_VALOR_DERIVADO': 8, 'DATOSALUMNOS_PROGRAMA_ANTERIOR_RUT': 2}
- Fuentes `SEM_ING_ORI`: {'POLITICA_FOR_ING_ACT_1': 2926, 'POLITICA_FOR_ING_ACT_2': 383, 'POLITICA_FOR_ING_ACT_3_SIN_PROGRAMA_ANTERIOR_FECHABLE': 80, 'TRACE_MOTOR_FOR_ING_ACT:TNS_PREV_CODCLI': 34, 'PRESERVADO_VALOR_DERIVADO': 8, 'DATOSALUMNOS_PROGRAMA_ANTERIOR_RUT': 2}
- Filas `FOR_ING_ACT = 1` con origen igual al actual: 2926
- Filas continuidad/cambio (`FOR` en [2, 3, 4, 5, 11]) con regla ORI validada: 499
- Filas `ANIO_ING_ORI != ANIO_ING_ACT`: 499
- Filas `SEM_ING_ORI != SEM_ING_ACT`: 469
- Ajustes `NIV_ACA` por duracion: 1
- Ajustes `NIV_ACA` por cohorte 2026: 45
- Filas regimen TRIMESTRAL evaluadas: 3428
- Filas con equivalencia TRIM→SEM aplicada: 3428
- Mismatches trimestrales residuales: 0
- Filas `FECHA_MATRICULA = 01/01/1900`: 1319
- Filas `FECHA_MATRICULA = 01/01/1900` fuera de cohorte 2026: 1319
- Filas `FECHA_MATRICULA = 01/01/1900` dentro de cohorte 2026: 0

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| Q | SI | SI | SI | SI | SI | OK |
| R | SI | SI | SI | SI | SI | OK |
| S | SI | SI | SI | SI | SI | OK |
| T | SI | SI | SI | SI | SI | OK |
| AA | SI | SI | SI | SI | SI | OK |
| AD | SI | SI | SI | SI | SI | OK |