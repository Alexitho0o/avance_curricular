# CNED BLOQUE 5 - 5 columnas completadas

Fecha de ejecución: 2026-06-04T16:34:02

## Archivos

- Archivo base: `/Users/alexi/Desktop/CNED_BLOQUE_4_5_COLUMNAS_COMPLETADAS.xlsx`
- Fuente PROMEDIOS/matriz: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
- Diccionario complementado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
- Referencia CNED/ÍNDICES: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`
- Metodología de referencia: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx`
- Excel generado en resultados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_BLOQUE_5_5_COLUMNAS_COMPLETADAS_20260604_163355.xlsx`
- Excel generado en Escritorio: `/Users/alexi/Desktop/CNED_BLOQUE_5_5_COLUMNAS_COMPLETADAS.xlsx`

## Criterio aplicado

- Ingreso otro: `NO APLICA` cuando `Otro Tipo de Ingreso` ya estaba como no aplica; revisión específica si falta descripción de ingreso alternativo.
- Observaciones: se enriquecen con trazabilidad a matriz, diccionario oferta 2026, revisión específica y listado ÍNDICES; los casos R3/R4 quedan marcados explícitamente.
- ANIO_INICIO: se mantiene/completa desde diccionario con match exacto o estructural fuerte; match ambiguo queda en conflicto/revisión específica.
- REGIMEN: se mantiene/completa como código técnico cuando existe fuente directa; no se convierte a texto por falta de tabla oficial.
- DURACION_REGIMEN: se mantiene/completa desde fuente directa; se registra coherencia contra duración del programa sin inferencias adicionales.

## Conteos

- Total filas trabajadas: 71
- Total celdas auditadas: 355
- Total completadas: 36
- Total reemplazadas: 71
- Total mantenidas: 180
- Total dejadas en revisión: 65
- Total conflictos: 3
- Total `REVISAR` genérico remanente en estas 5 columnas: 0

## Conteo por columna y acción

| COLUMNA          | ACCION_APLICADA   |   TOTAL |
|:-----------------|:------------------|--------:|
| ANIO_INICIO      | CONFLICTO_REVISAR |       1 |
| ANIO_INICIO      | DEJAR_REVISAR     |      10 |
| ANIO_INICIO      | MANTENER          |      60 |
| DURACION_REGIMEN | CONFLICTO_REVISAR |       1 |
| DURACION_REGIMEN | DEJAR_REVISAR     |      10 |
| DURACION_REGIMEN | MANTENER          |      60 |
| Ingreso otro     | COMPLETAR         |      36 |
| Ingreso otro     | DEJAR_REVISAR     |      35 |
| Observaciones    | REEMPLAZAR        |      71 |
| REGIMEN          | CONFLICTO_REVISAR |       1 |
| REGIMEN          | DEJAR_REVISAR     |      10 |
| REGIMEN          | MANTENER          |      60 |

## Control 79

| HOJA                            |   FILAS |   ESPERADO | VALIDA   |
|:--------------------------------|--------:|-----------:|:---------|
| PROGRAMAS_FALTANTES_PARA_CREAR  |      71 |         71 | True     |
| NO_CREAR_CUBIERTO               |       2 |          2 | True     |
| REQUIERE_DECISION_INSTITUCIONAL |       2 |          2 | True     |
| DUDOSOS_REV_MANUAL_RESUELTOS    |       4 |          4 | True     |
| DUDOSOS_REV_MANUAL_ACTUALIZADO  |       0 |          0 | True     |
| TOTAL_CONTROL                   |      79 |         79 | True     |

## Códigos con revisión o conflicto en bloque 5

I162S2C101J4V1, I162S2C102J4V1, I162S2C103J4V1, I162S2C104J4V1, I162S2C105J4V1, I162S2C111J4V2, I162S2C112J4V2, I162S2C113J4V2, I162S2C124J4V2, I162S2C125J4V2, I162S2C13J1V1, I162S2C13J2V1, I162S2C1J2V2, I162S2C1J4V3, I162S2C21J1V1, I162S2C21J2V1, I162S2C23J1V1, I162S2C23J2V1, I162S2C24J1V1, I162S2C24J2V1, I162S2C3J2V2, I162S2C40J2V1, I162S2C41J2V1, I162S2C53J3V1, I162S2C63J4V1, I162S2C64J4V1, I162S2C65J4V1, I162S2C66J4V1, I162S2C67J4V1, I162S2C68J4V1, I162S2C69J4V1, I162S2C6J4V1, I162S2C70J4V1, I162S2C71J4V1, I162S2C76J4V2, I162S2C77J4V2, I162S2C83J4V2, I162S2C86J4V2, I162S2C88J4V2, I162S2C90J2V1, I162S2C95J4V1, I162S2C96J4V1, I162S2C97J4V1, I162S2C98J4V1, I162S2C99J4V1

## Hashes de insumos

| INSUMO                    | RUTA                                                                                                                                                             | SHA256_ANTES                                                     | SHA256_DESPUES                                                   | INTACTO   |
|:--------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------|:-----------------------------------------------------------------|:----------|
| excel_base_bloque_4       | /Users/alexi/Desktop/CNED_BLOQUE_4_5_COLUMNAS_COMPLETADAS.xlsx                                                                                                   | c637bf6792c5ee12bac087c9932c1e3abcce23b1bc43872e2ff49b39305443d2 | c637bf6792c5ee12bac087c9932c1e3abcce23b1bc43872e2ff49b39305443d2 | True      |
| promedios_matriz          | /Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx                                                                               | 3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb | 3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb | True      |
| diccionario_complementado | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv | 6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e | 6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e | True      |
| referencia_indices        | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv                                                               | ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0 | ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0 | True      |
| metodologia_referencia    | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx                           | f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de | f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de | True      |

## Validación técnica del Excel generado

| EXISTE   |   SIZE | ZIP_OOXML_VALIDO   | ABRE_OPENPYXL   | FORMULAS   |   FORMULAS_TOTAL | MACROS   | VINCULOS_EXTERNOS   | CONEXIONES   | DIBUJOS   | GRAFICOS   | VALIDACIONES_DATOS   | HOJAS_MAYOR_31   | HOJAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:---------|-------:|:-------------------|:----------------|:-----------|-----------------:|:---------|:--------------------|:-------------|:----------|:-----------|:---------------------|:-----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True     | 873291 | True               | True            | False      |                0 | False    | False               | False        | False     | False      | False                | False            | ['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION', 'AUDITORIA_5_COLUMNAS_BLOQUE_1', 'AUDITORIA_BLOQUE_2', 'AUDITORIA_BLOQUE_3', 'AUDITORIA_BLOQUE_4', 'AUDITORIA_BLOQUE_5'] |

## Validación técnica de la copia en Escritorio

| EXISTE   |   SIZE | ZIP_OOXML_VALIDO   | ABRE_OPENPYXL   | FORMULAS   |   FORMULAS_TOTAL | MACROS   | VINCULOS_EXTERNOS   | CONEXIONES   | DIBUJOS   | GRAFICOS   | VALIDACIONES_DATOS   | HOJAS_MAYOR_31   | HOJAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:---------|-------:|:-------------------|:----------------|:-----------|-----------------:|:---------|:--------------------|:-------------|:----------|:-----------|:---------------------|:-----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True     | 873291 | True               | True            | False      |                0 | False    | False               | False        | False     | False      | False                | False            | ['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION', 'AUDITORIA_5_COLUMNAS_BLOQUE_1', 'AUDITORIA_BLOQUE_2', 'AUDITORIA_BLOQUE_3', 'AUDITORIA_BLOQUE_4', 'AUDITORIA_BLOQUE_5'] |

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

DICTAMEN_FINAL: BLOQUE_5_5_COLUMNAS_COMPLETADO_CON_REVISION_JUSTIFICADA
