# Matriz gobernada inicial — Histórico Oferta Académica SIES

- Fecha: `20260817_160828`.
- Perfil técnico fuente: `PERFILES_ESTRUCTURA_HISTORICA_20260817_160716.json`.
- Estado: selección inicial; aún no consolida ni transforma datos.

## Fuentes por decisión

| Ciclo propuesto | Año carpeta | Etapa | Archivo | Filas | Columnas | Decisión | Estado |
|---|---|---|---|---:|---:|---|---|
| 2023 | 2022 | - | 02-12-2022_Oferta_Académica_Aranceles_TP (oficial) 2023.csv | 70 | 60 | USAR_BASE_ANUAL | APROBADO_PROVISIONAL |
| 2023 | 2023 | - | Oferta_Académica_TP oficial_15_09.csv | 35 | 15 | SOLO_CONTRASTE | PENDIENTE_REVISION |
| 2023 | 2023 | - | Oferta_Académica_TP oficial_30_11.csv | 77 | 51 | USAR_BASE_ANUAL | APROBADO_PROVISIONAL |
| 2024 | 2024 | - | Oferta Académica 2024.csv | 76 | 50 | USAR_BASE_ANUAL | APROBADO_PROVISIONAL |
| 2024 | 2024 | - | Oferta Académica 2024.xlsx | 76 | 50 | SOLO_CONTRASTE | PENDIENTE_REVISION |
| 2025 | 2025 | ETAPA 3 | Aranceles Etapa 3.csv | 40 | 13 | USAR_COMPLEMENTO | APROBADO_PROVISIONAL |
| 2026 | 2026 | ETAPA 1 | 20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv | 81 | 51 | USAR_BASE_ANUAL | APROBADO_PROVISIONAL |
| 2026 | 2026 | ETAPA 2 | 2. IPSS_Etapa2_Carga_Nuevas_Oferta 2026_Nov_2025.xlsx | 8 | 51 | USAR_COMPLEMENTO | APROBADO_PROVISIONAL |
| 2026 | 2026 | ETAPA 2 | ETAPA 2.csv | 8 | 51 | USAR_COMPLEMENTO | APROBADO_PROVISIONAL |
| 2026 | 2026 | ETAPA 3 | 20251010_96470_20241010_13950_OA_2_TP_ARANCELES.csv | - | 51 | REVISAR | PENDIENTE_REVISION |
| 2026 | 2026 | ETAPA 3 | Aranceles oferta completa 2026.xlsx.xlsx | 34 | 5 | REVISAR | PENDIENTE_REVISION |
| 2026 | 2026 | ETAPA 3 | Carga_Aranceles_Etapa3_2026.csv | 124 | 51 | USAR_COMPLEMENTO | APROBADO_PROVISIONAL |
| 2026 | 2026 | ETAPA 3 | aferta nueva y antigua.csv | 124 | 52 | REVISAR | PENDIENTE_REVISION |
| 2026 | 2026 | ETAPA 3 | reporte-20251103-104249-39040 aranceles 2026.xlsx | 11038 | 10 | NO_USAR_AUN | PENDIENTE_REVISION |
| 2026 | 2026 | ETAPA 3 | subirR.xlsx | 871 | 52 | NO_USAR_AUN | PENDIENTE_REVISION |
| 2027 | 2027 | - | Vacantes 1° y 2° Sem_carreras_vigentes.xlsx | 72 | 27 | USAR_COMPLEMENTO | APROBADO_PROVISIONAL |
| 2027 | 2027 | - | reporte_dinamico_5913.csv | 103 | 51 | SOLO_CONTRASTE | PENDIENTE_REVISION |
| 2027 | 2027 | - | reporte_dinamico_5913_2026-08-12_14_52_50 Modificables_lm.xlsx | 103 | 51 | SOLO_CONTRASTE | PENDIENTE_REVISION |
| 2027 | 2027 | ETAPA 1 | CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv | 103 | 48 | USAR_BASE_ANUAL | APROBADO_PROVISIONAL |

## Reglas de interpretación

- `USAR_BASE_ANUAL`: fuente principal para el corte histórico del ciclo.
- `USAR_COMPLEMENTO`: fuente que añade información de una etapa específica, por ejemplo, oferta nueva o aranceles.
- `SOLO_CONTRASTE`: fuente equivalente, precarga o versión anterior; no debe sumarse al histórico final.
- `REVISAR`: archivo potencialmente útil cuya semántica, duplicidad o granularidad no está resuelta.
- `NO_USAR_AUN`: archivo operativo, masivo o de formato no confirmado; no incorpora datos al modelo histórico.

## Próximo paso

Antes de consolidar, se deben comparar encabezados, claves de carrera/sede, duplicados y solapamientos entre las fuentes aprobadas provisionalmente.
