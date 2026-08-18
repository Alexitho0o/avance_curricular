# Conciliación 2026 — Contrato corregido de primeras 18 columnas

- Fuente interna: Etapa 3 Aranceles 2026.
- Fuente SIES: Histórico comparativo, OFE_2026.
- Filas en cada fuente: 124.

## Cobertura por clave

| Clave | Campos | Compartidas | Cobertura SIES | Cobertura interna |
|---|---|---:|---:|---:|
| CODIGO_SEDE_CODIGO_CARRERA_VERSION | CODIGO_SEDE, CODIGO_CARRERA, VERSION | 83 | 100.0% | 100.0% |
| SEDE_CARRERA_VERSION | NOMBRE_SEDE, NOMBRE_CARRERA, VERSION | 83 | 100.0% | 100.0% |
| CODIGO_SEDE_CODIGO_CARRERA_NOMBRE_TITULO_VERSION | CODIGO_SEDE, CODIGO_CARRERA, NOMBRE_TITULO, VERSION | 83 | 100.0% | 100.0% |
| CODIGO_SEDE_CODIGO_CARRERA_ANO_INICIO_VERSION | CODIGO_SEDE, CODIGO_CARRERA, ANO_INICIO, VERSION | 95 | 100.0% | 100.0% |

## Mejor clave

- `CODIGO_SEDE_CODIGO_CARRERA_ANO_INICIO_VERSION`.
- Campos: `CODIGO_SEDE, CODIGO_CARRERA, ANO_INICIO, VERSION`.
- Cobertura SIES: 100.0%.
- Cobertura interna: 100.0%.
