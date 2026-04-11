# Reporte FASE 1 - Identidad MU 2026

- Filas incluidas en carga final: 3433
- Filas `FECH_NAC = 01/01/1900`: 0 (0.0%)
- Filas `NAC` con default 38 explícito: 1 (0.03%)
- Filas `PAIS_EST_SEC` con default 38 explícito: 0 (0.0%)
- Filas `PAIS_EST_SEC` inferidas por localidad: 0 (0.0%)
- Filas con DV inválido: 0 (0.0%)
- Filas `TIPO_DOC=R` + `FOR_ING_ACT=6` + `Q/S=2026` + `VIG=1`: 4
- Filas `TIPO_DOC=R` + `FOR_ING_ACT=6` + `VIG=0`: 1
- Filas históricas `TIPO_DOC=R` + `FOR_ING_ACT=6` (`Q/S<2026`): 3

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| A | SI | NO | SI | NO | SI | Pendiente |
| B | SI | SI | SI | SI | SI | OK |
| C | SI | SI | SI | SI | SI | OK |
| E | SI | NO | SI | SI | SI | Pendiente |
| H | SI | SI | SI | SI | SI | OK |
| I | SI | SI | SI | SI | SI | OK |
| J | SI | SI | SI | SI | SI | OK |