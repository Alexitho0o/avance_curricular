# Diagnóstico de solapamientos — Histórico Oferta Académica

- Fecha: `20260817_161118`.
- Pares analizados: **6**.
- Errores de lectura: **0**.

## 2023_CORTE_TEMPRANO_VS_NOVIEMBRE

- Propósito: Seleccionar corte anual principal 2023.
- Archivo izquierdo: `2022/02-12-2022_Oferta_Académica_Aranceles_TP (oficial) 2023.csv`
- Archivo derecho: `2023/Oferta_Académica_TP oficial_30_11.csv`
- Filas: 70 vs. 77
- Encabezados: SI vs. SI
- Clave usada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`
- Columnas comunes: 51
- Claves compartidas: 64
- Solo izquierdo: 6
- Solo derecho: 13
- Solapamiento izquierdo: 91.4%
- Solapamiento derecho: 83.1%
- Sugerencia: **SOLAPAMIENTO_PARCIAL: no sumar directamente; requiere consolidación o deduplicación.**

## 2024_CSV_VS_XLSX

- Propósito: Confirmar si CSV y XLSX son equivalentes.
- Archivo izquierdo: `2024/Oferta Académica 2024.csv`
- Archivo derecho: `2024/Oferta Académica 2024.xlsx`
- Filas: 76 vs. 76
- Encabezados: SI vs. SI
- Clave usada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`
- Columnas comunes: 50
- Claves compartidas: 76
- Solo izquierdo: 0
- Solo derecho: 0
- Solapamiento izquierdo: 100.0%
- Solapamiento derecho: 100.0%
- Sugerencia: **EQUIVALENTES: usar solo una fuente como base; la otra queda como contraste.**

## 2026_ETAPA2_CSV_VS_XLSX

- Propósito: Confirmar si ambos representan la misma carga de oferta nueva.
- Archivo izquierdo: `2026/ETAPA 2/ETAPA 2.csv`
- Archivo derecho: `2026/ETAPA 2/2. IPSS_Etapa2_Carga_Nuevas_Oferta 2026_Nov_2025.xlsx`
- Filas: 8 vs. 8
- Encabezados: NO vs. SI
- Clave usada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`
- Columnas comunes: 47
- Claves compartidas: 0
- Solo izquierdo: 8
- Solo derecho: 3
- Solapamiento izquierdo: 0.0%
- Solapamiento derecho: 0.0%
- Sugerencia: **SIN_SOLAPAMIENTO: fuentes complementarias o cortes distintos; no sumar sin revisar semántica.**

## 2027_5913_CSV_VS_XLSX

- Propósito: Confirmar equivalencia entre precarga CSV y libro modificable.
- Archivo izquierdo: `2027/dctos/reporte_dinamico_5913.csv`
- Archivo derecho: `2027/reporte_dinamico_5913_2026-08-12_14_52_50 Modificables_lm.xlsx`
- Filas: 103 vs. 103
- Encabezados: SI vs. SI
- Clave usada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`
- Columnas comunes: 51
- Claves compartidas: 0
- Solo izquierdo: 103
- Solo derecho: 103
- Solapamiento izquierdo: 0.0%
- Solapamiento derecho: 0.0%
- Sugerencia: **SIN_SOLAPAMIENTO: fuentes complementarias o cortes distintos; no sumar sin revisar semántica.**

## 2026_ETAPA1_VS_ETAPA2

- Propósito: Medir solapamiento entre oferta vigente/editada y oferta nueva.
- Archivo izquierdo: `2026/ETAPA 1/20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv`
- Archivo derecho: `2026/ETAPA 2/ETAPA 2.csv`
- Filas: 81 vs. 8
- Encabezados: NO vs. NO
- Clave usada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`
- Columnas comunes: 51
- Claves compartidas: 0
- Solo izquierdo: 81
- Solo derecho: 8
- Solapamiento izquierdo: 0.0%
- Solapamiento derecho: 0.0%
- Sugerencia: **SIN_SOLAPAMIENTO: fuentes complementarias o cortes distintos; no sumar sin revisar semántica.**

## 2026_ETAPA1_VS_ETAPA3_ARANCELES

- Propósito: Separar oferta base de carga complementaria de aranceles.
- Archivo izquierdo: `2026/ETAPA 1/20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv`
- Archivo derecho: `2026/ETAPA 3/Carga_Aranceles_Etapa3_2026.csv`
- Filas: 81 vs. 124
- Encabezados: NO vs. NO
- Clave usada: `COD_SEDE, COD_CARRERA, MODALIDAD, COD_JORNADA, VERSION, COD_TIPO_PLAN_CARRERA`
- Columnas comunes: 51
- Claves compartidas: 81
- Solo izquierdo: 0
- Solo derecho: 43
- Solapamiento izquierdo: 100.0%
- Solapamiento derecho: 65.3%
- Sugerencia: **SOLAPAMIENTO_PARCIAL: no sumar directamente; requiere consolidación o deduplicación.**

