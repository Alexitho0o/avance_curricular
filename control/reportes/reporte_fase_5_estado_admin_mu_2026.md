# Reporte FASE 5 - Estado administrativo MU 2026

- Filas incluidas en carga final: 3433
- Distribucion `SIT_FON_SOL`: {'1': 3237, '0': 196}
- Distribucion `SUS_PRE`: {'0': 3433}
- Distribucion `REINCORPORACION`: {'0': 3433}
- Distribucion `VIG`: {'1': 3338, '0': 95}
- Patch `SIT_FON_SOL` habilitado: True
- Patch `SIT_FON_SOL` path: /Users/alexi/Documents/GitHub/avance_curricular/patches/mu2026/sit_fon_sol_patch_ruts.json
- Patch `SIT_FON_SOL` RUT totales: 196
- Patch `SIT_FON_SOL` filas objetivo: 196
- Patch `SIT_FON_SOL` filas objetivo OK: 196
- Patch `SIT_FON_SOL` no-target con fuente patch: 0
- Filas `SUS_PRE` por default explicito: 0
- Filas `SUS_PRE` forzadas a `0` por politica de cohorte 2026: 0
- Filas `REINCORPORACION = 1`: 0
- Filas `REINCORPORACION = 1` sin respaldo temporal: 0
- Filas `VIG = 2`: 0
- Filas `VIG = 2` por politica de titulado aprobado: 0

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| AB | SI | SI | SI | SI | SI | OK |
| AC | SI | SI | SI | SI | SI | OK |
| AE | SI | SI | SI | SI | SI | OK |
| AF | SI | SI | SI | SI | SI | OK |

## Bloqueo residual observado

- `AB SIT_FON_SOL` queda validado con trazabilidad mixta: politica local fija + patch JSON por RUT en filas objetivo.
- La validacion AB exige que filas objetivo del patch terminen con `SIT_FON_SOL=0` y que filas no objetivo no queden marcadas con fuente de patch.
- `AC SUS_PRE` queda cerrado por politica local fija auditable sobre todas las filas incluidas.
- `AE REINCORPORACION` queda cerrado por politica local fija auditable en `0` para todas las filas incluidas.