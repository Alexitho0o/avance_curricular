# Auditoría end to end por bloques de 10 columnas

Fecha ejecución: 2026-05-07 11:49:32

## Resumen de archivos

| archivo                                        | estado   | separador_detectado   |   filas |   columnas |   bloques_10_columnas |
|:-----------------------------------------------|:---------|:----------------------|--------:|-----------:|----------------------:|
| matricula_unificada_2026_pregrado.csv          | OK       | ;                     |    3441 |         32 |                     4 |
| matricula_unificada_2026_oficial.xlsx          | OK       | xlsx                  |    3442 |         32 |                     4 |
| matricula_unificada_2026_control.csv           | OK       | ,                     |    3442 |         32 |                     4 |
| archivo_listo_para_sies.xlsx                   | OK       | xlsx                  |      33 |          4 |                     1 |
| carreras_avance_curricular_2025_control.csv    | OK       | ,                     |      72 |         22 |                     3 |
| carreras_avance_curricular_2025_pes_ready.csv  | OK       | ,                     |      71 |         21 |                     3 |
| matricula_avance_curricular_2025_control.csv   | OK       | ,                     |    5173 |         22 |                     3 |
| matricula_avance_curricular_2025_pes_ready.csv | OK       | ,                     |    5172 |         21 |                     3 |
| EXCLUSIONES_PROVISORIAS_RUT_MULTI_CODCLI.tsv   | OK       | \t                    |     106 |          7 |                     1 |
| auditoria_consolidacion_codcli.tsv             | OK       | \t                    |   26321 |         11 |                     2 |

## Carpeta de salida

`/Users/alexi/Documents/GitHub/avance_curricular/resultados/auditoria_end_to_end_bloques_10cols_FIX_20260507_114929`

## Criterio aplicado

Cada archivo fue leído sin modificarlo. Los CSV fueron leídos con detección automática de separador. Las columnas se dividieron en bloques consecutivos de 10. Para cada bloque se exportó un resumen de columnas y una muestra de las primeras 20 filas.