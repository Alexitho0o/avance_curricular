# CNED BLOQUE 7 - 5 columnas completadas

Fecha de ejecución: 2026-06-04T16:47:56

## Archivos

- Archivo base: `/Users/alexi/Desktop/CNED_BLOQUE_6_5_COLUMNAS_COMPLETADAS.xlsx`
- Fuente PROMEDIOS/matriz: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
- Diccionario complementado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
- Referencia CNED/ÍNDICES: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`
- Metodología de referencia: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx`
- Excel generado en resultados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_BLOQUE_7_5_COLUMNAS_COMPLETADAS_20260604_164748.xlsx`
- Excel generado en Escritorio: `/Users/alexi/Desktop/CNED_BLOQUE_7_5_COLUMNAS_COMPLETADAS.xlsx`

## Criterio aplicado

- Match: R1 por `CODIGO_UNICO` contra `CODIGO_UNICO_DERIVADO`; luego matriz; luego estructura fuerte; estructura ampliada solo como evidencia secundaria.
- Las columnas de área se tratan como indicadores binarios; `0` y `1` son valores válidos.
- No se convierten códigos a texto y no se infiere área por nombre de carrera.
- Matches ambiguos/no únicos o conflictos con fuente quedan como `CONFLICTO_REVISAR_*`.
- Fuente ausente o `REVISAR` queda con revisión específica por columna.

## Conteos

- Total filas trabajadas: 71
- Total celdas auditadas: 355
- Total completadas: 0
- Total reemplazadas: 0
- Total mantenidas: 300
- Total dejadas en revisión: 50
- Total conflictos: 5
- Total `REVISAR` genérico remanente en estas 5 columnas: 0

## Conteo por columna y acción

| COLUMNA                        | ACCION_APLICADA   |   TOTAL |
|:-------------------------------|:------------------|--------:|
| AREA_ADMIN_DERECHO             | CONFLICTO_REVISAR |       1 |
| AREA_ADMIN_DERECHO             | DEJAR_REVISAR     |      10 |
| AREA_ADMIN_DERECHO             | MANTENER          |      60 |
| AREA_AGRI_SILVI_PESCA_VET      | CONFLICTO_REVISAR |       1 |
| AREA_AGRI_SILVI_PESCA_VET      | DEJAR_REVISAR     |      10 |
| AREA_AGRI_SILVI_PESCA_VET      | MANTENER          |      60 |
| AREA_ARTES_HUMANIDADES         | CONFLICTO_REVISAR |       1 |
| AREA_ARTES_HUMANIDADES         | DEJAR_REVISAR     |      10 |
| AREA_ARTES_HUMANIDADES         | MANTENER          |      60 |
| AREA_CIENCIAS_NAT_MAT_ESTAD    | CONFLICTO_REVISAR |       1 |
| AREA_CIENCIAS_NAT_MAT_ESTAD    | DEJAR_REVISAR     |      10 |
| AREA_CIENCIAS_NAT_MAT_ESTAD    | MANTENER          |      60 |
| AREA_CS_SOCIAL_PERIODISMO_INFO | CONFLICTO_REVISAR |       1 |
| AREA_CS_SOCIAL_PERIODISMO_INFO | DEJAR_REVISAR     |      10 |
| AREA_CS_SOCIAL_PERIODISMO_INFO | MANTENER          |      60 |

## Control 79

| HOJA                            |   FILAS |   ESPERADO | VALIDA   |
|:--------------------------------|--------:|-----------:|:---------|
| PROGRAMAS_FALTANTES_PARA_CREAR  |      71 |         71 | True     |
| NO_CREAR_CUBIERTO               |       2 |          2 | True     |
| REQUIERE_DECISION_INSTITUCIONAL |       2 |          2 | True     |
| DUDOSOS_REV_MANUAL_RESUELTOS    |       4 |          4 | True     |
| DUDOSOS_REV_MANUAL_ACTUALIZADO  |       0 |          0 | True     |
| TOTAL_CONTROL                   |      79 |         79 | True     |

## Códigos con revisión o conflicto en bloque 7

I162S2C13J1V1, I162S2C13J2V1, I162S2C21J1V1, I162S2C21J2V1, I162S2C23J1V1, I162S2C23J2V1, I162S2C24J1V1, I162S2C24J2V1, I162S2C3J2V2, I162S2C41J2V1, I162S2C6J4V1

## Hashes de insumos

| INSUMO                    | RUTA                                                                                                                                                             | SHA256_ANTES                                                     | SHA256_DESPUES                                                   | INTACTO   |
|:--------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------|:-----------------------------------------------------------------|:----------|
| excel_base_bloque_6       | /Users/alexi/Desktop/CNED_BLOQUE_6_5_COLUMNAS_COMPLETADAS.xlsx                                                                                                   | 78a4c3665074c3d5cc44211941b3dd8f06ac00c6b7bfaaac6a269807ae8d51e2 | 78a4c3665074c3d5cc44211941b3dd8f06ac00c6b7bfaaac6a269807ae8d51e2 | True      |
| promedios_matriz          | /Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx                                                                               | 3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb | 3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb | True      |
| diccionario_complementado | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv | 6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e | 6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e | True      |
| referencia_indices        | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv                                                               | ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0 | ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0 | True      |
| metodologia_referencia    | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx                           | f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de | f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de | True      |

## Validación técnica del Excel generado

| EXISTE   |   SIZE | ZIP_OOXML_VALIDO   | ABRE_OPENPYXL   | FORMULAS   |   FORMULAS_TOTAL | MACROS   | VINCULOS_EXTERNOS   | CONEXIONES   | DIBUJOS   | GRAFICOS   | VALIDACIONES_DATOS   | HOJAS_MAYOR_31   | HOJAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|:---------|-------:|:-------------------|:----------------|:-----------|-----------------:|:---------|:--------------------|:-------------|:----------|:-----------|:---------------------|:-----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True     | 927854 | True               | True            | False      |                0 | False    | False               | False        | False     | False      | False                | False            | ['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION', 'AUDITORIA_5_COLUMNAS_BLOQUE_1', 'AUDITORIA_BLOQUE_2', 'AUDITORIA_BLOQUE_3', 'AUDITORIA_BLOQUE_4', 'AUDITORIA_BLOQUE_5', 'AUDITORIA_BLOQUE_6', 'AUDITORIA_BLOQUE_7'] |

## Validación técnica de la copia en Escritorio

| EXISTE   |   SIZE | ZIP_OOXML_VALIDO   | ABRE_OPENPYXL   | FORMULAS   |   FORMULAS_TOTAL | MACROS   | VINCULOS_EXTERNOS   | CONEXIONES   | DIBUJOS   | GRAFICOS   | VALIDACIONES_DATOS   | HOJAS_MAYOR_31   | HOJAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|:---------|-------:|:-------------------|:----------------|:-----------|-----------------:|:---------|:--------------------|:-------------|:----------|:-----------|:---------------------|:-----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True     | 927854 | True               | True            | False      |                0 | False    | False               | False        | False     | False      | False                | False            | ['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION', 'AUDITORIA_5_COLUMNAS_BLOQUE_1', 'AUDITORIA_BLOQUE_2', 'AUDITORIA_BLOQUE_3', 'AUDITORIA_BLOQUE_4', 'AUDITORIA_BLOQUE_5', 'AUDITORIA_BLOQUE_6', 'AUDITORIA_BLOQUE_7'] |

## Estado Git final

```text
git status --short
(sin cambios rastreables en status --short)

On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

nothing to commit, working tree clean
```

## Dictamen

DICTAMEN_FINAL: BLOQUE_7_5_COLUMNAS_COMPLETADO_CON_REVISION_JUSTIFICADA
