# Informe de estructura histórica — Oferta Académica SIES

- Fecha: `20260817_160716`.
- Archivos analizados: **19**.
- Errores de lectura: **0**.

## Resultado por archivo

| Año | Etapa | Archivo | Tipo | Encabezado | Filas de datos | Columnas | Clasificación |
|---|---|---|---|---|---:|---:|---|
| 2022 | - | 02-12-2022_Oferta_Académica_Aranceles_TP (oficial) 2023.csv | CSV | Sí | 70 | 60 | HISTORICO_COMPARABLE_OFERTA |
| 2023 | - | Oferta_Académica_TP oficial_15_09.csv | CSV | Sí | 35 | 15 | HISTORICO_COMPARABLE_OFERTA |
| 2023 | - | Oferta_Académica_TP oficial_30_11.csv | CSV | Sí | 77 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2024 | - | Oferta Académica 2024.csv | CSV | Sí | 76 | 50 | HISTORICO_COMPARABLE_OFERTA |
| 2024 | - | Oferta Académica 2024.xlsx | XLSX | Sí | 76 | 50 | HISTORICO_COMPARABLE_OFERTA |
| 2025 | ETAPA 3 | Aranceles Etapa 3.csv | CSV | No | 40 | 13 | HISTORICO_COMPLEMENTARIO_ARANCELES |
| 2026 | ETAPA 1 | 20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv | CSV | No | 81 | 51 | CARGA_SIES_HISTORICA_SIN_ENCABEZADO |
| 2026 | ETAPA 2 | 2. IPSS_Etapa2_Carga_Nuevas_Oferta 2026_Nov_2025.xlsx | XLSX | Sí | 8 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2026 | ETAPA 2 | ETAPA 2.csv | CSV | No | 8 | 51 | CARGA_SIES_HISTORICA_SIN_ENCABEZADO |
| 2026 | ETAPA 3 | 20251010_96470_20241010_13950_OA_2_TP_ARANCELES.csv | CSV | Sí | 0 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2026 | ETAPA 3 | Aranceles oferta completa 2026.xlsx.xlsx | XLSX | Sí | 34 | 5 | REVISAR_MANUALMENTE |
| 2026 | ETAPA 3 | Carga_Aranceles_Etapa3_2026.csv | CSV | No | 124 | 51 | CARGA_SIES_COMPLEMENTARIA_ARANCELES_SIN_ENCABEZADO |
| 2026 | ETAPA 3 | aferta nueva y antigua.csv | CSV | Sí | 124 | 52 | HISTORICO_COMPARABLE_OFERTA |
| 2026 | ETAPA 3 | reporte-20251103-104249-39040 aranceles 2026.xlsx | XLSX | Sí | 11038 | 10 | HISTORICO_COMPARABLE_OFERTA |
| 2026 | ETAPA 3 | subirR.xlsx | XLSX | Sí | 871 | 52 | HISTORICO_COMPARABLE_OFERTA |
| 2027 | - | Vacantes 1° y 2° Sem_carreras_vigentes.xlsx | XLSX | No | 72 | 27 | REVISAR_MANUALMENTE |
| 2027 | - | reporte_dinamico_5913.csv | CSV | Sí | 103 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2027 | - | reporte_dinamico_5913_2026-08-12_14_52_50 Modificables_lm.xlsx | XLSX | Sí | 103 | 51 | HISTORICO_COMPARABLE_OFERTA |
| 2027 | ETAPA 1 | CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv | CSV | No | 103 | 48 | CARGA_SIES_HISTORICA_SIN_ENCABEZADO |

## Regla interpretativa

- Los CSV sin encabezado con 48, 50, 51, 52 o 60 columnas se tratan como cargas SIES potenciales.
- La primera fila de un CSV sin encabezado es un registro de datos y no debe descontarse.
- Los reportes de precarga SIES sirven como línea base, pero no reemplazan una carga final congelada.
- Un archivo con extensión XLSX que no sea ZIP OpenXML se clasifica como formato no válido hasta revisar su contenido real.
