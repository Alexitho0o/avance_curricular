# Reporte FASE 5 - Estado administrativo MU 2026

- Filas incluidas en carga final: 1736
- Distribucion `SIT_FON_SOL`: {'0': 1736}
- Distribucion `SUS_PRE`: {'0': 1736}
- Distribucion `REINCORPORACION`: {'0': 1718, '1': 18}
- Distribucion `VIG`: {'1': 1502, '2': 234}
- Filas `SIT_FON_SOL` por default explicito: 1736
- Filas `SUS_PRE` por default explicito: 1736
- Filas `SUS_PRE` forzadas a `0` por politica de cohorte 2026: 0
- Filas `REINCORPORACION = 1`: 18
- Filas `REINCORPORACION = 1` sin respaldo temporal: 16
- Filas `VIG = 2`: 234
- Filas `VIG = 2` por politica de titulado aprobado: 234

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| AB | NO | SI | SI | SI | SI | Pendiente |
| AC | NO | SI | SI | SI | SI | Pendiente |
| AE | NO | SI | SI | SI | SI | Pendiente |
| AF | SI | SI | SI | SI | SI | OK |

## Bloqueo residual observado

- `AB SIT_FON_SOL` y `AC SUS_PRE` permanecen pendientes cuando toda la cohorte incluida queda en fallback explicito y no existe fuente real por fila.
- `AE REINCORPORACION` permanece pendiente cuando `DA_SITUACION = 38 - ...` no puede validarse contra una señal temporal inequívoca de ultima carga del periodo.