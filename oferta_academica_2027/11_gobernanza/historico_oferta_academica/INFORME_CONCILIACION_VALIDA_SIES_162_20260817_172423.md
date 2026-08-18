# Conciliación válida — Histórico SIES 162

- Estado: `CONCILIACION_VALIDA_ESTRUCTURA_HOMOLOGADA`.
- Fuente prioritaria: histórico SIES comparativo, código 162.

## Claves de conciliación

- 2023 y 2024, clave base: `COD_SEDE + COD_CARRERA + VERSION`.
- 2023 y 2024, control estricto: añade modalidad y jornada homologadas.
- 2026, clave base: `COD_SEDE + COD_CARRERA + VERSION`.
- Para 2026 modalidad y jornada quedan como atributos de revisión, no como parte de la clave.

## Resumen

| Período | Etapa | SIES | Interno | Claves base compartidas | Estrictas compartidas | Solo SIES | Solo interno |
|---|---|---:|---:|---:|---:|---:|---:|
| OFE_2023 | CORTE_ANUAL | 70 | 77 | 34 | 64 | 1 | 4 |
| OFE_2024 | CORTE_ANUAL | 77 | 76 | 27 | 66 | 11 | 9 |
| OFE_2026 | ETAPA_1 | 124 | 81 | 0 | 0 | 83 | 34 |
| OFE_2026 | ETAPA_2 | 124 | 8 | 0 | 0 | 83 | 8 |
| OFE_2026 | ETAPA_3_ARANCELES | 124 | 124 | 0 | 0 | 83 | 76 |

## Clasificación

- `COINCIDE_ESTRICTA`: coincide en clave y atributos de modalidad/jornada cuando aplica.
- `COINCIDE_CLAVE_BASE_DIFERENCIAS_ATRIBUTOS`: misma carrera/sede/versión, pero hay diferencias en atributos.
- `SOLO_SIES`: registro oficial sin clave base institucional.
- `SOLO_INTERNO`: registro institucional sin clave base en el histórico SIES.
