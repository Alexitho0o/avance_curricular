# Resolución de conciliación histórica — SIES 162

## Regla de precedencia

Para OFE_2010–OFE_2026, los KPI históricos usan el histórico comparativo SIES filtrado por código de institución 162.

## Resolución OFE_2026

- Estado: **CONCILIADO_100_PORCIENTO**.
- SIES prioritario: 124 registros.
- Fuente interna Etapa 3: 124 registros.
- Clave validada: `CODIGO_SEDE + CODIGO_CARRERA + ANO_INICIO + VERSION`.
- Cobertura: 100% SIES y 100% fuente interna.
- Conclusión: `Carga_Aranceles_Etapa3_2026.csv` se reclasifica como `BASE_ANUAL_COMPLETA_CONCILIADA` para OFE_2026.

## Matriz vigente

| Período | SIES | Interno | Rol interno | Estado |
|---|---:|---:|---|---|
| OFE_2023 | 70 | 77 | BASE_INTERNA_CONCILIACION_PARCIAL | PENDIENTE_DIFERENCIAS_RESIDUALES |
| OFE_2024 | 77 | 76 | BASE_INTERNA_CONCILIACION_PARCIAL | PENDIENTE_DIFERENCIAS_RESIDUALES |
| OFE_2025 | 102 | - | COMPLEMENTO_FINANCIERO_PARCIAL | SIN_BASE_INTERNA_ANUAL_COMPLETA |
| OFE_2026 | 124 | 124 | BASE_ANUAL_COMPLETA_CONCILIADA | CONCILIADO_100_PORCIENTO |
| OFE_2027 | - | 103 | CARGA_INSTITUCIONAL_CONGELADA | PENDIENTE_PUBLICACION_SIES |

## Regla 2026 reemplazada

La regla anterior de conteo `Etapa 1 (81) + Etapa 2 (8) = 89` queda reemplazada para el histórico anual por `Etapa 3 = 124`. Etapa 1 y Etapa 2 se preservan para trazabilidad del flujo de carga, pero no constituyen el corte anual completo.
