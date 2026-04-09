# Revisión end to end — Proyecto Avance Curricular / CNED / Matrícula Unificada

Fecha: `2026-06-03T08:58:09`

## Dictamen

`FALTA_CAPTURAR_TABLA_CNED_NUEVA`

## Recomendación

Primero se debe crear DATOS_VALIDACION_CNED_TSV_NUEVO_MANUAL.tsv pegando solo la tabla CNED completa, no el comando ni texto del chat.

## Estado repositorio

- Rama: `clean/pes-ready-final`
- Git status: `limpio`

## Comparación CNED

| archivo          |   filas |   columnas | años   |   cantidad_años |   cod_carrera_unicos |   codigo_sies_unicos |   programas_unicos | pregrado_posgrado   |
|:-----------------|--------:|-----------:|:-------|----------------:|---------------------:|---------------------:|-------------------:|:--------------------|
| TSV anterior     |     168 |         12 |        |               0 |                   34 |                    0 |                 19 |                     |
| TSV actualizado  |         |            |        |               0 |                    0 |                    0 |                  0 |                     |
| TSV nuevo manual |         |            |        |               0 |                    0 |                    0 |                  0 |                     |

## Problemas detectados

| severidad   | area                | problema_detectado                                               | accion_recomendada                                                                                        |
|:------------|:--------------------|:-----------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| MEDIA       | CNED                | El TSV anterior tiene solo 12 columnas.                          | Actualizar la base CNED con una tabla completa, pero solo después de capturar correctamente el TSV nuevo. |
| ALTA        | CNED                | No existe DATOS_VALIDACION_CNED_TSV_NUEVO_MANUAL.tsv.            | Crear el archivo manual pegando solo la tabla CNED completa con encabezados, no el comando.               |
| MEDIA       | CNED                | No existe DATOS_VALIDACION_CNED_TSV_ACTUALIZADO.tsv.             | Generar el TSV actualizado solo cuando el TSV nuevo manual tenga más de 50 columnas y lectura correcta.   |
| ALTA        | Matrícula Unificada | No se encontró matricula_unificada_2026_pregrado_PARA_SUBIR.csv. | Confirmar si la carga principal pregrado está en otra ruta o regenerar artefacto PES_READY.               |

## Archivos generados

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/DIAGNOSTICO_END_TO_END_CNED_MU_20260603_085809.xlsx`
- JSON: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/DIAGNOSTICO_END_TO_END_CNED_MU_20260603_085809.json`
- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/DIAGNOSTICO_END_TO_END_CNED_MU_20260603_085809.md`
