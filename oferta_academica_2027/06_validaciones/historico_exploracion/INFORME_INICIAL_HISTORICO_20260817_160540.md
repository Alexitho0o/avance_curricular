# Informe inicial — Histórico Oferta Académica SIES

- Fecha de perfilamiento: `20260817_160540`.
- Fuente explorada: `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Oferta académica`.
- Archivos perfilados: **18**.
- Archivos no encontrados: **0**.
- Errores de perfilamiento: **1**.

## Resumen por clasificación

- **HISTORICO_COMPARABLE_OFERTA**: 10
- **REVISAR**: 8

## Perfiles de archivos

| Año | Etapa | Archivo | Tipo | Filas estimadas | Columnas | Clasificación |
|---|---|---|---:|---:|---:|---|
| 2022 | - | 02-12-2022_Oferta_Académica_Aranceles_TP (oficial) 2023.csv | csv | 70 | 60 | HISTORICO_COMPARABLE_OFERTA |
| 2023 | - | Oferta_Académica_TP oficial_15_09.csv | csv | 35 | 15 | HISTORICO_COMPARABLE_OFERTA |
| 2023 | - | Oferta_Académica_TP oficial_30_11.csv | csv | 77 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2024 | - | Oferta Académica 2024.csv | csv | 76 | 50 | HISTORICO_COMPARABLE_OFERTA |
| 2024 | - | Oferta Académica 2024.xlsx | xlsx | 76 | 50 | HISTORICO_COMPARABLE_OFERTA |
| 2025 | ARANCELES ETAPA 3.CSV | Aranceles Etapa 3.csv | csv | 39 | 13 | REVISAR |
| 2026 | ETAPA 1 | 20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv | csv | 80 | 51 | REVISAR |
| 2026 | ETAPA 2 | 2. IPSS_Etapa2_Carga_Nuevas_Oferta 2026_Nov_2025.xlsx | xlsx | 8 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2026 | ETAPA 2 | ETAPA 2.csv | csv | 7 | 51 | REVISAR |
| 2026 | ETAPA 3 | 20251010_96470_20241010_13950_OA_2_TP_ARANCELES.csv | csv | 0 | 51 | REVISAR |
| 2026 | ETAPA 3 | Aranceles oferta completa 2026.xlsx.xlsx | xlsx | 34 | 5 | REVISAR |
| 2026 | ETAPA 3 | Carga_Aranceles_Etapa3_2026.csv | csv | 123 | 51 | REVISAR |
| 2026 | ETAPA 3 | aferta nueva y antigua.csv | csv | 124 | 52 | HISTORICO_COMPARABLE_OFERTA |
| 2026 | ETAPA 3 | subirR.xlsx | xlsx | 867 | 52 | HISTORICO_COMPARABLE_OFERTA |
| 2027 | - | Vacantes 1° y 2° Sem_carreras_vigentes.xlsx | xlsx | 73 | 27 | REVISAR |
| 2027 | - | reporte_dinamico_5913.csv | csv | 103 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2027 | - | reporte_dinamico_5913_2026-08-12_14_52_50 Modificables_lm.xlsx | xlsx | 103 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2027 | ETAPA 1 | CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv | csv | 102 | 48 | REVISAR |

## Criterio de uso inicial

- `HISTORICO_COMPARABLE_OFERTA`: candidato para indicadores longitudinales de oferta.
- `HISTORICO_COMPLEMENTARIO_ARANCELES`: útil para evolución de aranceles, no necesariamente para oferta completa.
- `ESTRUCTURA_O_PLANTILLA`: evidencia de cambios de estructura de carga; no usar como registros históricos.
- `REVISAR`: requiere revisión manual de encabezados y contenido antes de incorporarlo.

## Errores de perfilamiento

- `2026/ETAPA 3/reporte-20251103-104249-39040 aranceles 2026.xlsx`: `BadZipFile('File is not a zip file')`
