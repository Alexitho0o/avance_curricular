# Auditoría MU2026 · Bloque 4 · Columnas 31 a 32

Fecha: 2026-05-07 11:54:24

## Columnas revisadas

REINCORPORACION, VIG

## Resumen de validación

| campo           | regla                                                |   errores | estado   | detalle                                   |
|:----------------|:-----------------------------------------------------|----------:|:---------|:------------------------------------------|
| REINCORPORACION | Debe ser obligatorio y admitir solo valores 0 o 1    |         0 | OK       | Reincorporación vacía o fuera de catálogo |
| VIG             | Debe ser obligatorio y admitir solo valores 0, 1 o 2 |         0 | OK       | Vigencia vacía o fuera de catálogo        |

## Perfil de columnas

| columna         |   filas |   vacios |   unicos | muestra   | distribucion                             |
|:----------------|--------:|---------:|---------:|:----------|:-----------------------------------------|
| REINCORPORACION |    3442 |        0 |        1 | 0         | {'0': np.int64(3442)}                    |
| VIG             |    3442 |        0 |        2 | 1 | 0     | {'0': np.int64(97), '1': np.int64(3345)} |

## Archivos generados

- `resultados/auditoria_mu2026_bloque_04_cols_31_32_20260507_115424/resumen_validacion_bloque_04_cols_31_32.csv`
- `resultados/auditoria_mu2026_bloque_04_cols_31_32_20260507_115424/perfil_columnas_bloque_04_cols_31_32.csv`
- `resultados/auditoria_mu2026_bloque_04_cols_31_32_20260507_115424/muestra_50_filas_bloque_04_cols_31_32.csv`