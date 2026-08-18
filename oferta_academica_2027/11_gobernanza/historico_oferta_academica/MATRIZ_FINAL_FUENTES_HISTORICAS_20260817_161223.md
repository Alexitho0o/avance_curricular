# Matriz final gobernada — Histórico Oferta Académica SIES

- Fecha: `20260817_161223`.
- Evidencia de solapamientos: `RESUMEN_SOLAPAMIENTOS_HISTORICOS_20260817_161118.tsv`.
- Alcance: selección de fuentes; no copia ni transforma archivos.

## Fuentes aprobadas para conteo de oferta

| Ciclo | Etapa | Fuente | Rol | Registros esperados |
|---|---|---|---|---:|
| 2023 | CORTE_ANUAL | 2023/Oferta_Académica_TP oficial_30_11.csv | BASE_ANUAL | 77 |
| 2024 | CORTE_ANUAL | 2024/Oferta Académica 2024.csv | BASE_ANUAL | 76 |
| 2026 | ETAPA_1 | 2026/ETAPA 1/20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv | BASE_OFERTA_VIGENTE_EDITADA | 81 |
| 2026 | ETAPA_2 | 2026/ETAPA 2/ETAPA 2.csv | COMPLEMENTO_OFERTA_NUEVA | 8 |
| 2027 | ETAPA_1 | 2027/ETAPA 1/CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv | BASE_ANUAL_CONGELADA | 103 |

## Fuentes de contraste o complemento

| Ciclo | Etapa | Fuente | Rol | Decisión |
|---|---|---|---|---|
| 2023 | CORTE_TEMPRANO | 2022/02-12-2022_Oferta_Académica_Aranceles_TP (oficial) 2023.csv | CONTRASTE_CAMBIOS | CONSERVAR_SIN_SUMAR |
| 2024 | CORTE_ANUAL | 2024/Oferta Académica 2024.xlsx | CONTRASTE_EQUIVALENTE | CONSERVAR_SIN_SUMAR |
| 2025 | ETAPA_3 | 2025/Aranceles Etapa 3.csv | COMPLEMENTO_ARANCELES_PARCIAL | APROBADA_PARCIAL |
| 2026 | ETAPA_2 | 2026/ETAPA 2/2. IPSS_Etapa2_Carga_Nuevas_Oferta 2026_Nov_2025.xlsx | CONTRASTE_ETAPA_2 | CONSERVAR_SIN_SUMAR |
| 2026 | ETAPA_3 | 2026/ETAPA 3/Carga_Aranceles_Etapa3_2026.csv | COMPLEMENTO_ARANCELES | APROBADA_COMO_COMPLEMENTO |
| 2027 | PRE_CARGA | 2027/dctos/reporte_dinamico_5913.csv | CONTRASTE_PRE_CARGA | CONSERVAR_SIN_SUMAR |
| 2027 | PRE_CARGA | 2027/reporte_dinamico_5913_2026-08-12_14_52_50 Modificables_lm.xlsx | CONTRASTE_PRE_CARGA_TRABAJO | CONSERVAR_SIN_SUMAR |

## Regla de consolidación 2026

- Conteo de oferta: Etapa 1 (81) + Etapa 2 CSV (8), dado que no comparten claves.
- La Etapa 3 de aranceles no incrementa el conteo de oferta.
- Etapa 3 puede enriquecer datos financieros cuando la clave coincida.

## Regla de consolidación 2027

- La carga congelada de Etapa 1 es la única fuente base anual.
- La precarga 5913 y su libro modificable se conservan solo para comparar cambios.

## Limitación 2025

- Solo se identificó un complemento de aranceles de 40 registros.
- No se infiere ni se reporta conteo anual completo de oferta hasta identificar una carga anual principal.
