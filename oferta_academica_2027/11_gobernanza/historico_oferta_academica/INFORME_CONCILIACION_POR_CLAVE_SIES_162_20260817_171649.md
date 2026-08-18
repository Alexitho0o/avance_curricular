# Conciliación por clave — Histórico SIES 162

## Claves empleadas

- Estricta: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`.
- Relajada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, COD_TIPO_PLAN_CARRERA`.

## Resumen

| Período | Archivo interno | SIES | Interno | Compartidas estrictas | Solo SIES | Solo interno |
|---|---|---:|---:|---:|---:|---:|
| OFE_2023 | 2023/Oferta_Académica_TP oficial_30_11.csv | 70 | 77 | 0 | 8 | 77 |
| OFE_2024 | 2024/Oferta Académica 2024.csv | 77 | 76 | 0 | 8 | 76 |
| OFE_2026 | 2026/ETAPA 1/20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv | 124 | 81 | 0 | 8 | 81 |
| OFE_2026 | 2026/ETAPA 2/ETAPA 2.csv | 124 | 8 | 0 | 8 | 8 |
| OFE_2026 | 2026/ETAPA 3/Carga_Aranceles_Etapa3_2026.csv | 124 | 124 | 0 | 8 | 124 |

## Interpretación de clases

- `DIFERENCIA_VERSION_O_CLAVE_ESTRICTA`: hay coincidencia con clave relajada, pero no con VERSION incluida.
- `SOLO_EN_FUENTE`: no existe equivalencia ni siquiera con clave relajada.

## Nota 2026

Para OFE_2026 se presentan por separado Etapa 1, Etapa 2 y Etapa 3. No se deben sumar los resultados de Etapa 3 al conteo de oferta, pues corresponde a una carga de aranceles.
