# Puente candidato 5810 ↔ Planes RE+CO — requiere validación

Proceso: Avance Curricular SIES 2026  
Subproyecto: KPI Avance Curricular Esperado  
Año referencia datos: 2025  

Se construye una tabla puente candidata entre 5810 y Planes RE+CO usando similitud de nombres de carrera. No se calcula todavía el KPI de Avance Curricular Esperado, porque el puente requiere validación del usuario.

## Resumen

| METRICA                        | VALOR                                |
|:-------------------------------|:-------------------------------------|
| TOTAL_CODIGO_UNICO_5810        | 43                                   |
| TOTAL_PROGRAMAS_PLANES_RECO    | 223                                  |
| TOTAL_MATCHES_CANDIDATOS_TOP10 | 430                                  |
| TOTAL_TOP1                     | 43                                   |
| MATCH_ALTO_TOP1                | 43                                   |
| MATCH_MEDIO_TOP1               | 0                                    |
| MATCH_BAJO_TOP1                | 0                                    |
| DENOMINADOR_PLANES_FILAS       | 1371                                 |
| KPI_ESPERADO_CALCULADO         | NO                                   |
| ESTADO                         | PUENTE_CANDIDATO_REQUIERE_VALIDACION |
| FUENTES_ORIGINALES_MODIFICADAS | NO                                   |

## Validaciones

| VALIDACION                     | RESULTADO   | DETALLE                                                            |
|:-------------------------------|:------------|:-------------------------------------------------------------------|
| 5810_FILAS_43                  | OK          | 43                                                                 |
| PLANES_RECO_FILAS              | OK          | 11438                                                              |
| TOP1_PARA_CADA_CODIGO_UNICO    | OK          | top1=43 / 5810=43                                                  |
| MATCH_ALTO_TOP1                | REVISAR     | 43                                                                 |
| MATCH_MEDIO_TOP1               | REVISAR     | 0                                                                  |
| MATCH_BAJO_TOP1                | REVISAR     | 0                                                                  |
| APLICACION_AUTOMATICA_KPI      | NO          | Puente requiere validación usuario antes de calcular KPI esperado. |
| FUENTES_ORIGINALES_MODIFICADAS | OK          | NO                                                                 |

## Archivo

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/18_puente_5810_planes_reco/PUENTE_CANDIDATO_5810_PLANES_RECO_20260704_164116/02_RESULTADOS/PUENTE_CANDIDATO_5810_PLANES_RECO_REQUIERE_VALIDACION.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/18_puente_5810_planes_reco/PUENTE_CANDIDATO_5810_PLANES_RECO_20260704_164116`
