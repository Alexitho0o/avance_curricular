# Reporte FASE 5 - Estado administrativo MU 2026

- Filas incluidas en carga final: 3687
- Distribucion `SIT_FON_SOL`: {'1': 3687}
- Distribucion `SUS_PRE`: {'0': 3687}
- Distribucion `REINCORPORACION`: {'0': 3687}
- Distribucion `VIG`: {'1': 3684, '2': 3}
- Filas `SIT_FON_SOL` por default explicito: 0
- Filas `SUS_PRE` por default explicito: 0
- Filas `SUS_PRE` forzadas a `0` por politica de cohorte 2026: 0
- Filas `REINCORPORACION = 1`: 0
- Filas `REINCORPORACION = 1` sin respaldo temporal: 0
- Filas `VIG = 2`: 3
- Filas `VIG = 2` por politica de titulado aprobado: 3

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| AB | SI | SI | SI | SI | SI | OK |
| AC | SI | SI | SI | SI | SI | OK |
| AE | SI | SI | SI | SI | SI | OK |
| AF | SI | SI | SI | SI | SI | OK |

## Bloqueo residual observado

- `AB SIT_FON_SOL` y `AC SUS_PRE` quedan cerrados por politica local fija auditable sobre todas las filas incluidas.
- `AE REINCORPORACION` queda cerrado por politica local fija auditable en `0` para todas las filas incluidas.