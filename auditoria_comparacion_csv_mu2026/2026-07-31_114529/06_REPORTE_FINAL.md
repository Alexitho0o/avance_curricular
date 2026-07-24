# Auditoría comparativa CSV históricos MU2026 contra consolidado reconstruido

## Gobernanza

- Proceso: Matrícula Unificada SIES 2026.
- Subproceso: Pregrado.
- Fuente comparación: `/Users/alexi/Desktop/AUDITORIA_MATRICULA_UNIFICADA_2026_RECONSTRUIDA_PARA_REVISION_20260731_002214.xlsx`.
- Hoja solicitada: `RAW_PREGRADO` / `07_PREGRADO_COMPLETO`.
- Hoja usada: `08_PREGRADO_COMPLETO`.
- Observación de equivalencia: El prompt menciona RAW_PREGRADO/07_PREGRADO_COMPLETO; el libro disponible contiene 08_PREGRADO_COMPLETO, usada como hoja equivalente.
- Fuentes evaluadas: 6 CSV históricos ubicados en `/Users/alexi/Downloads`.
- Originales: NO MODIFICADOS.
- Método: lectura, hash, comparación estructural, comparación exacta por 32 campos, comparación por `LLAVE_MATRICULA`, universo y códigos.

## Respuesta directa

1. ¿Cuál CSV coincide con el consolidado?

Ningún CSV coincide exactamente con el consolidado reconstruido de 4.105 registros. No hay `MATCH_EXACTO_CON_RECONSTRUIDO`.

2. ¿Cuál parece ser la fuente utilizada?

Ninguno de los seis CSV por sí solo parece ser la fuente completa utilizada para construir el consolidado final. Todos son cargas parciales/anteriores respecto del universo gobernado. El archivo con mayor coincidencia exacta es `09-04-2026_15-37-28_Matrícula-Pregrado-2026.csv`, con 688 filas exactas coincidentes.

3. ¿Cuál es la evolución temporal de cargas?

| archivo | fecha_nombre | filas | vig0 | vig1 | vig2 | vigente | coincidentes | nuevos | faltantes | clasificacion_final |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09-04-2026_13-19-01_Matrícula-Pregrado-2026.csv | 2026-04-09 13:19:01 | 71 | 0 | 71 | 0 | 71 | 0 | 71 | 4105 | FUENTE_ANTERIOR |
| 09-04-2026_15-37-28_Matrícula-Pregrado-2026.csv | 2026-04-09 15:37:28 | 911 | 0 | 911 | 0 | 911 | 688 | 223 | 3417 | FUENTE_ANTERIOR |
| 09-04-2026_15-55-03_Matrícula-Pregrado-2026.csv | 2026-04-09 15:55:03 | 100 | 100 | 0 | 0 | 0 | 0 | 100 | 4105 | FUENTE_ANTERIOR |
| 09-04-2026_18-21-37_Matrícula-Pregrado-2026.csv | 2026-04-09 18:21:37 | 51 | 0 | 51 | 0 | 51 | 0 | 51 | 4105 | FUENTE_ANTERIOR |
| 09-04-2026_19-20-49_Matrícula-Pregrado-2026.csv | 2026-04-09 19:20:49 | 192 | 0 | 192 | 0 | 192 | 0 | 192 | 4105 | FUENTE_ANTERIOR |
| 11-06-2026_18-41-18_Matrícula-Pregrado-2026.csv | 2026-06-11 18:41:18 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 4105 | FUENTE_ANTERIOR |

4. ¿Qué diferencias explican los 226 registros?

Estos seis CSV no explican directamente la diferencia de 226 registros de publicación versus institucional. Son archivos históricos de carga parcial contra el consolidado reconstruido; el análisis muestra evolución y cobertura parcial, no una reproducción del universo final publicado/institucional. La diferencia de 226 debe interpretarse desde la comparación publicación vs consolidado, no desde estos CSV parciales.

5. ¿Hay evidencia de que el consolidado fue construido correctamente?

Sí hay evidencia técnica de consistencia interna: el consolidado contiene 4.105 registros oficiales, con VIG=0: 960, VIG=1: 3145, VIG=2: 0. Además, los CSV históricos son parciales y no contradicen por sí mismos el consolidado. Sin embargo, esta auditoría no prueba una cadena completa de generación si faltan cargas intermedias fuera de los seis CSV evaluados.

## Comparación por vigencia

| archivo | VIG0 | VIG1 | VIG2 | Total |
| --- | --- | --- | --- | --- |
| 09-04-2026_13-19-01_Matrícula-Pregrado-2026.csv | 0 | 71 | 0 | 71 |
| 09-04-2026_15-37-28_Matrícula-Pregrado-2026.csv | 0 | 911 | 0 | 911 |
| 09-04-2026_15-55-03_Matrícula-Pregrado-2026.csv | 100 | 0 | 0 | 100 |
| 09-04-2026_18-21-37_Matrícula-Pregrado-2026.csv | 0 | 51 | 0 | 51 |
| 09-04-2026_19-20-49_Matrícula-Pregrado-2026.csv | 0 | 192 | 0 | 192 |
| 11-06-2026_18-41-18_Matrícula-Pregrado-2026.csv | 0 | 1 | 0 | 1 |

## Clasificación final por archivo

| archivo | filas | vig0 | vig1 | vig2 | coincidentes | coincidentes_llave_matricula | nuevos | faltantes | tipo_comparacion | clasificacion_final |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09-04-2026_13-19-01_Matrícula-Pregrado-2026.csv | 71 | 0 | 71 | 0 | 0 | 69 | 71 | 4105 | PARCIAL | FUENTE_ANTERIOR |
| 09-04-2026_15-37-28_Matrícula-Pregrado-2026.csv | 911 | 0 | 911 | 0 | 688 | 876 | 223 | 3417 | PARCIAL | FUENTE_ANTERIOR |
| 09-04-2026_15-55-03_Matrícula-Pregrado-2026.csv | 100 | 100 | 0 | 0 | 0 | 4 | 100 | 4105 | PARCIAL | FUENTE_ANTERIOR |
| 09-04-2026_18-21-37_Matrícula-Pregrado-2026.csv | 51 | 0 | 51 | 0 | 0 | 49 | 51 | 4105 | PARCIAL | FUENTE_ANTERIOR |
| 09-04-2026_19-20-49_Matrícula-Pregrado-2026.csv | 192 | 0 | 192 | 0 | 0 | 191 | 192 | 4105 | PARCIAL | FUENTE_ANTERIOR |
| 11-06-2026_18-41-18_Matrícula-Pregrado-2026.csv | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 4105 | PARCIAL | FUENTE_ANTERIOR |

## Hallazgos

- Consolidado reconstruido: 4.105 registros; matrícula vigente VIG1+VIG2 = 3.145.
- Ningún CSV reproduce 4.105 registros ni 3.145 vigentes.
- Los seis CSV suman físicamente 1326 filas, pero esa suma no debe interpretarse como universo final porque son archivos históricos separados.
- Cobertura exacta de la unión de hashes históricos contra consolidado: 688 filas del consolidado aparecen exactas en al menos uno de los CSV.
- Registros de CSV con hash no presente en consolidado, sumados por archivo: 638. Pueden deberse a cargas superadas, cambios de dato o registros excluidos posteriormente.

## Limitaciones

- Los CSV no tienen encabezado físico; se asignaron los 32 encabezados oficiales para comparación.
- La comparación individual usa `LLAVE_MATRICULA = TIPO_DOC + N_DOC + DV + CODIGO_NORMALIZADO`; no existe `CODCLI` en los CSV.
- No se eliminó VIG=0 ni se trató como matrícula vigente.
- Diferencias no se clasifican como errores sin evidencia adicional.

## Archivos generados

- `01_INVENTARIO_ARCHIVOS.csv`
- `02_COMPARACION_ESTRUCTURA.xlsx`
- `03_COMPARACION_UNIVERSO.csv`
- `04_COMPARACION_CODIGOS.csv`
- `05_DETALLE_DIFERENCIAS.csv`
- `06_REPORTE_FINAL.md`

## Conclusión

No se identificó un CSV histórico que explique o coincida completamente con la base consolidada reconstruida. La línea de tiempo muestra cargas parciales anteriores, con estructura compatible de 32 campos, pero con universos muy inferiores al consolidado final.
