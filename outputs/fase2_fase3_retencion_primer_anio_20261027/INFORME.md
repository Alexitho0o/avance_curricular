# Fases 2–3 · Retención de 1er año

## Cálculo interno [C]

Se calculó desde la única base autorizada: corrida MU 2022–2026 `20260901_142342`, hash `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. Resultado preliminar por personas:

| Cohorte | Elegibles | Retenidos | Tasa |
|---:|---:|---:|---:|
| 2022 | 338 | 250 | 73,96% |
| 2023 | 512 | 393 | 76,76% |
| 2024 | 702 | 448 | 63,82% |
| 2025 | 1.503 | 953 | 63,41% |

El cálculo usa `ANIO_ING_ACT`, `ANIO_INFORMADO`, `VIG` y documento normalizado conservando DV 0. Cada persona cuenta una vez.

## Validación SIES [B/E]

Se localizaron los manifiestos y fuentes oficiales: `RETENCION_SIES_IPSS_162_GRANULAR_2025_CORREO_20260909.tsv`, `Retencion_ipss_2022_2024_GRANULAR.xlsx` e `Informe_Retencion_SIES_2026_270702026.xlsx`. Esta ejecución aún no extrae una tabla comparable completa para 2022–2025 por institución/carrera/persona; por tanto la paridad numérica queda **E** y no se declara diferencia porcentual.

## Validación V24 [E]

No se leyeron valores de V24 para construir el cálculo. La comparación secundaria queda pendiente hasta cerrar la extracción independiente de SIES y las exclusiones de programas especiales.

## Diferencias y límites

No se clasifican diferencias como error de código mientras no exista una tabla SIES comparable y una clasificación gobernada de programas especiales. La regla permanece `BORRADOR_NO_ACTIVO`; no se propone activación.
