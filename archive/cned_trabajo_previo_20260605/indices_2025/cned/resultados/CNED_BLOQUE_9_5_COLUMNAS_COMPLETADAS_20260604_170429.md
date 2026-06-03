# CNED BLOQUE 9 - 5 columnas completadas

Fecha de ejecución: 2026-06-04T17:04:36

## Archivos

- Archivo base: `/Users/alexi/Desktop/CNED_BLOQUE_8_5_COLUMNAS_COMPLETADAS.xlsx`
- Fuente PROMEDIOS/matriz: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
- Diccionario complementado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
- Referencia CNED/ÍNDICES: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`
- Metodología de referencia: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx`
- Excel generado en resultados: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_BLOQUE_9_5_COLUMNAS_COMPLETADAS_20260604_170429.xlsx`
- Excel generado en Escritorio: `/Users/alexi/Desktop/CNED_BLOQUE_9_5_COLUMNAS_COMPLETADAS.xlsx`

## Criterio aplicado

- Match: R1 por `CODIGO_UNICO` contra `CODIGO_UNICO_DERIVADO`; luego matriz; luego estructura fuerte; estructura ampliada solo como evidencia secundaria.
- Vacantes: valores enteros, incluido `0`, son válidos y se mantienen/completan solo desde fuente trazable.
- `FECHA_ADMISION_INICIAL`, `MALLA_CURRICULAR` y `PERFIL_EGRESO`: solo se completan con fuente directa explícita. Como las fuentes disponibles vienen vacías, quedan con revisión específica.
- No se inventan fechas, enlaces, rutas, mallas ni perfiles; no se usa web ni información externa.

## Conteos

- Total filas trabajadas: 71
- Total celdas auditadas: 355
- Total completadas: 0
- Total reemplazadas: 0
- Total mantenidas: 120
- Total dejadas en revisión: 233
- Total conflictos: 2
- Total `REVISAR` genérico remanente en estas 5 columnas: 0

## Conteo por columna y acción

| COLUMNA                   | ACCION_APLICADA   |   TOTAL |
|:--------------------------|:------------------|--------:|
| FECHA_ADMISION_INICIAL    | DEJAR_REVISAR     |      71 |
| MALLA_CURRICULAR          | DEJAR_REVISAR     |      71 |
| PERFIL_EGRESO             | DEJAR_REVISAR     |      71 |
| VACANTES_PRIMER_SEMESTRE  | CONFLICTO_REVISAR |       1 |
| VACANTES_PRIMER_SEMESTRE  | DEJAR_REVISAR     |      10 |
| VACANTES_PRIMER_SEMESTRE  | MANTENER          |      60 |
| VACANTES_SEGUNDO_SEMESTRE | CONFLICTO_REVISAR |       1 |
| VACANTES_SEGUNDO_SEMESTRE | DEJAR_REVISAR     |      10 |
| VACANTES_SEGUNDO_SEMESTRE | MANTENER          |      60 |

## Control 79

| HOJA                            |   FILAS |   ESPERADO | VALIDA   |
|:--------------------------------|--------:|-----------:|:---------|
| PROGRAMAS_FALTANTES_PARA_CREAR  |      71 |         71 | True     |
| NO_CREAR_CUBIERTO               |       2 |          2 | True     |
| REQUIERE_DECISION_INSTITUCIONAL |       2 |          2 | True     |
| DUDOSOS_REV_MANUAL_RESUELTOS    |       4 |          4 | True     |
| DUDOSOS_REV_MANUAL_ACTUALIZADO  |       0 |          0 | True     |
| TOTAL_CONTROL                   |      79 |         79 | True     |

## Códigos con revisión o conflicto en bloque 9

I162S2C101J4V1, I162S2C102J4V1, I162S2C103J4V1, I162S2C104J4V1, I162S2C105J4V1, I162S2C10J1V1, I162S2C10J4V1, I162S2C111J4V1, I162S2C111J4V2, I162S2C112J4V1, I162S2C112J4V2, I162S2C113J4V1, I162S2C113J4V2, I162S2C114J2V1, I162S2C115J2V1, I162S2C116J4V1, I162S2C117J4V1, I162S2C118J4V1, I162S2C119J4V1, I162S2C124J4V1, I162S2C124J4V2, I162S2C125J4V1, I162S2C125J4V2, I162S2C13J1V1, I162S2C13J2V1, I162S2C1J2V2, I162S2C1J4V3, I162S2C21J1V1, I162S2C21J2V1, I162S2C23J1V1, I162S2C23J2V1, I162S2C24J1V1, I162S2C24J2V1, I162S2C2J1V2, I162S2C2J2V2, I162S2C2J4V2, I162S2C35J1V2, I162S2C35J2V2, I162S2C35J4V2, I162S2C3J2V2, I162S2C40J2V1, I162S2C41J2V1, I162S2C53J3V1, I162S2C63J4V1, I162S2C64J4V1, I162S2C65J4V1, I162S2C66J4V1, I162S2C67J4V1, I162S2C68J4V1, I162S2C69J4V1, I162S2C6J1V1, I162S2C6J2V1, I162S2C6J4V1, I162S2C70J4V1, I162S2C71J4V1, I162S2C76J4V2, I162S2C77J4V2, I162S2C83J4V2, I162S2C86J4V2, I162S2C87J4V2, I162S2C88J4V2, I162S2C90J2V1, I162S2C90J2V2, I162S2C95J4V1, I162S2C96J4V1, I162S2C97J4V1, I162S2C98J4V1, I162S2C99J4V1, I162S3C114J2V1, I162S3C115J2V1, I162S3C91J2V1

## Hashes de insumos

| INSUMO                    | RUTA                                                                                                                                                             | SHA256_ANTES                                                     | SHA256_DESPUES                                                   | INTACTO   |
|:--------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------|:-----------------------------------------------------------------|:----------|
| excel_base_bloque_8       | /Users/alexi/Desktop/CNED_BLOQUE_8_5_COLUMNAS_COMPLETADAS.xlsx                                                                                                   | cbfe6b3e87b5fdf4027b840a78f361e3812bf8ce782d6f7e2f35f03fcfdc5288 | cbfe6b3e87b5fdf4027b840a78f361e3812bf8ce782d6f7e2f35f03fcfdc5288 | True      |
| promedios_matriz          | /Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx                                                                               | 3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb | 3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb | True      |
| diccionario_complementado | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv | 6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e | 6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e | True      |
| referencia_indices        | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv                                                               | ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0 | ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0 | True      |
| metodologia_referencia    | /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_COLUMNA_POR_COLUMNA_20260604_121448.xlsx                           | f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de | f5e43bcb22dadd0d6c581e6121b6ffe9a3af08105f1b1b91e6ba1f41838f14de | True      |

## Validación técnica del Excel generado

| EXISTE   |   SIZE | ZIP_OOXML_VALIDO   | ABRE_OPENPYXL   | FORMULAS   |   FORMULAS_TOTAL | MACROS   | VINCULOS_EXTERNOS   | CONEXIONES   | DIBUJOS   | GRAFICOS   | VALIDACIONES_DATOS   | HOJAS_MAYOR_31   | HOJAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:---------|-------:|:-------------------|:----------------|:-----------|-----------------:|:---------|:--------------------|:-------------|:----------|:-----------|:---------------------|:-----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True     | 980269 | True               | True            | False      |                0 | False    | False               | False        | False     | False      | False                | False            | ['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION', 'AUDITORIA_5_COLUMNAS_BLOQUE_1', 'AUDITORIA_BLOQUE_2', 'AUDITORIA_BLOQUE_3', 'AUDITORIA_BLOQUE_4', 'AUDITORIA_BLOQUE_5', 'AUDITORIA_BLOQUE_6', 'AUDITORIA_BLOQUE_7', 'AUDITORIA_BLOQUE_8', 'AUDITORIA_BLOQUE_9'] |

## Validación técnica de la copia en Escritorio

| EXISTE   |   SIZE | ZIP_OOXML_VALIDO   | ABRE_OPENPYXL   | FORMULAS   |   FORMULAS_TOTAL | MACROS   | VINCULOS_EXTERNOS   | CONEXIONES   | DIBUJOS   | GRAFICOS   | VALIDACIONES_DATOS   | HOJAS_MAYOR_31   | HOJAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:---------|-------:|:-------------------|:----------------|:-----------|-----------------:|:---------|:--------------------|:-------------|:----------|:-----------|:---------------------|:-----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True     | 980269 | True               | True            | False      |                0 | False    | False               | False        | False     | False      | False                | False            | ['RESUMEN_EJECUTIVO', 'PROGRAMAS_FALTANTES_PARA_CREAR', 'NO_CREAR_CUBIERTO', 'REQUIERE_DECISION_INSTITUCIONAL', 'DUDOSOS_REV_MANUAL_RESUELTOS', 'DUDOSOS_REV_MANUAL_ACTUALIZADO', 'DICCIONARIO_OFERTA_2026', 'MATCH_PROGRAMAS_VS_DICCIONARIO', 'AUDITORIA_COMPLETITUD', 'AUDITORIA_79_REGISTROS', 'CONTROL_TECNICO', 'AUDITORIA_APLICACION', 'CAMBIOS_APLICADOS', 'CELDAS_REVISAR', 'CONFLICTOS_REVISAR', 'CONTROL_TECNICO_APLICACION', 'AUDITORIA_5_COLUMNAS_BLOQUE_1', 'AUDITORIA_BLOQUE_2', 'AUDITORIA_BLOQUE_3', 'AUDITORIA_BLOQUE_4', 'AUDITORIA_BLOQUE_5', 'AUDITORIA_BLOQUE_6', 'AUDITORIA_BLOQUE_7', 'AUDITORIA_BLOQUE_8', 'AUDITORIA_BLOQUE_9'] |

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

DICTAMEN_FINAL: BLOQUE_9_5_COLUMNAS_COMPLETADO_CON_REVISION_JUSTIFICADA
