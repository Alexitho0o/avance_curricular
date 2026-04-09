# Reporte FASE 2 - SIES Oferta MU 2026

- Filas incluidas en carga final: 1282
- Filas pendientes SIES/oferta: 131
- Excluidas por heurística opaca: 0
- Excluidas por sin match SIES: 0
- Filas incluidas con heurística `PRIMERA_OPCION`: 0
- Inconsistencias incluidas COD_SED/COD_CAR/MODALIDAD/JOR/VERSION: 0/0/0/0/0
- Fuente final `COD_SED`: {'CODIGO_CARRERA_SIES_FINAL': 1256, 'DA_SEDE_GOBERNANZA': 26}
- Fuente final `COD_CAR`: {'CODIGO_CARRERA_SIES_FINAL': 1256, 'CODIGOS_SIES_POTENCIALES': 26}
- Fuente final `MODALIDAD`: {'OFERTA_ACADEMICA': 1256, 'JOR_FINAL': 26}
- Fuente final `JOR`: {'OFERTA_ACADEMICA': 1256, 'JORNADA_FUENTE_LEGACY': 26}
- Fuente final `VERSION`: {'CODIGO_CARRERA_SIES_FINAL': 1256, 'SIN_FUENTE_FINAL': 26}

## Gate por columna

| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |
|---|---|---|---|---|---|---|
| K | SI | SI | SI | SI | SI | OK |
| L | SI | SI | SI | SI | SI | OK |
| M | SI | SI | SI | SI | SI | OK |
| N | SI | SI | SI | SI | SI | OK |
| O | SI | SI | SI | NO | SI | Pendiente |