# Diagnóstico nominal OFE_2026 — SIES 162

- Fuente SIES: histórico comparativo prioritario, OFE_2026.
- Fuente interna: Carga Aranceles Etapa 3 2026.
- Ambas fuentes contienen 124 filas.

## Cobertura por clave candidata

| Clave | Campos | Claves compartidas | Cobertura SIES | Cobertura interna |
|---|---|---:|---:|---:|
| SEDE_CARRERA | NOMBRE_SEDE, NOMBRE_CARRERA | 0 | 0.0% | 0.0% |
| SEDE_CARRERA_TITULO | NOMBRE_SEDE, NOMBRE_CARRERA, NOMBRE_TITULO | 0 | 0.0% | 0.0% |
| SEDE_CARRERA_ANIO_INICIO | NOMBRE_SEDE, NOMBRE_CARRERA, ANO_INICIO | 0 | 0.0% | 0.0% |
| SEDE_CARRERA_TITULO_ANIO_INICIO | NOMBRE_SEDE, NOMBRE_CARRERA, NOMBRE_TITULO, ANO_INICIO | 0 | 0.0% | 0.0% |
| CODIGO_SEDE_CODIGO_CARRERA | CODIGO_SEDE, CODIGO_CARRERA | 0 | 0.0% | 0.0% |
| CODIGO_SEDE_CODIGO_CARRERA_ANIO_INICIO | CODIGO_SEDE, CODIGO_CARRERA, ANO_INICIO | 0 | 0.0% | 0.0% |

## Mejor clave

- Clave seleccionada: **SEDE_CARRERA**.
- Campos: `NOMBRE_SEDE, NOMBRE_CARRERA`.
- Cobertura SIES: 0.0%.
- Cobertura interna: 0.0%.
