# Reporte FASE 2 - SIES Oferta MU 2026

- Filas incluidas en carga final: 3433
- Filas pendientes SIES/oferta: 923
- Excluidas por heurística opaca: 0
- Excluidas por sin match SIES: 6
- Filas incluidas con heurística `PRIMERA_OPCION`: 0
- Inconsistencias incluidas COD_SED/COD_CAR/MODALIDAD/JOR/VERSION: 0/0/0/0/0
- Fuente final `COD_SED`: {'CODIGO_CARRERA_SIES_FINAL': 3356, 'DA_SEDE_GOBERNANZA': 77}
- Fuente final `COD_CAR`: {'CODIGO_CARRERA_SIES_FINAL': 3356, 'CODIGOS_SIES_POTENCIALES': 77}
- Fuente final `MODALIDAD`: {'OFERTA_ACADEMICA': 3356, 'JOR_FINAL': 77}
- Fuente final `JOR`: {'OFERTA_ACADEMICA': 3356, 'JORNADA_FUENTE_LEGACY': 77}
- Fuente final `VERSION`: {'CODIGO_CARRERA_SIES_FINAL': 3356, 'SIN_FUENTE_FINAL': 77}

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| K | SI | SI | SI | SI | SI | OK |
| L | SI | SI | SI | SI | SI | OK |
| M | SI | SI | SI | SI | SI | OK |
| N | SI | SI | SI | SI | SI | OK |
| O | SI | SI | SI | NO | SI | Pendiente |