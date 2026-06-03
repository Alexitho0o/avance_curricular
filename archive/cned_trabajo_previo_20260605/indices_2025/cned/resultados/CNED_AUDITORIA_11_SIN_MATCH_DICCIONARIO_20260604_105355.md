# Auditoría 11 sin match contra diccionario oferta 2026

## Archivos usados

- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`
- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO.xlsx`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.tsv`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.xlsx`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_CON_DICCIONARIO_REVISION.xlsx`
- `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`

## Hash SHA256

- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`: `ed363f3e1626b3c1d3a2138ef5eb8580738f687a41fa7b796feae5f61187969b`
- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO.xlsx`: `037c490b9d5fb62cf44787d4f54498b9cf7cb8ccac31df6bfe4bb09944ac72c0`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.tsv`: `c457bab06e30221e72ce21e96ce51361e74becb2df49f0f6657291cf946c4990`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.xlsx`: `1f4e9bedbc369e05bd5f9dcb0a860f77964598573c4de3cfba65a0a2f6fa851d`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_CON_DICCIONARIO_REVISION.xlsx`: `037c490b9d5fb62cf44787d4f54498b9cf7cb8ccac31df6bfe4bb09944ac72c0`
- `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`

## Conteos

- Total registros diccionario: 124
- Total PROGRAMAS_FALTANTES_PARA_CREAR: 71
- Total NO_CREAR_CUBIERTO: 2
- Total REQUIERE_DECISION_INSTITUCIONAL: 2
- Total DUDOSOS_REV_MANUAL_RESUELTOS: 4
- Total control operativo: 79
- Total casos sin match auditados: 11

## Los 11 códigos sin match

| CODIGO_UNICO   | NOMBRE_CARRERA_OPERATIVO                                       | EXISTE_EN_MATRIZ   | EXISTE_EN_INDICES_REFERENCIA   | DICTAMEN                       | NIVEL_CONFIANZA   |
|:---------------|:---------------------------------------------------------------|:-------------------|:-------------------------------|:-------------------------------|:------------------|
| I162S2C13J1V1  | SOPORTE DE SERVICIOS DE TELECOMUNICACIONES                     | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C13J2V1  | SOPORTE DE SERVICIOS DE TELECOMUNICACIONES                     | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C21J1V1  | INGENIERIA DE EJECUCION EN AUTOMATIZACION Y CONTROL INDUSTRIAL | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C21J2V1  | INGENIERIA DE EJECUCION EN AUTOMATIZACION Y CONTROL INDUSTRIAL | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C23J1V1  | INGENIERIA DE EJECUCION EN PREVENCION DE RIESGOS               | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C23J2V1  | INGENIERIA DE EJECUCION EN PREVENCION DE RIESGOS               | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C24J1V1  | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL                 | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C24J2V1  | TECNICO EN AUTOMATIZACION Y CONTROL INDUSTRIAL                 | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C3J2V2   | INGENIERIA EN CONECTIVIDAD Y REDES                             | SI                 | NO                             | MATCH_RESUELTO_POR_VERSION     | MEDIA             |
| I162S2C41J2V1  | DIPLOMADO EN GESTION DE PROYECTOS                              | SI                 | NO                             | REQUIERE_AGREGAR_A_DICCIONARIO | ALTA              |
| I162S2C6J4V1   | TECNICO EN CONECTIVIDAD Y REDES                                | SI                 | NO                             | MATCH_RESUELTO_POR_VERSION     | MEDIA             |

## Diagnóstico caso a caso

| CODIGO_UNICO   |   COD_CARRERA_DERIVADO |   COD_JORNADA_DERIVADO |   VERSION_DERIVADA | DICTAMEN                       | MOTIVO_DICTAMEN                                                                                          | ACCION_RECOMENDADA                                                                                                        | NIVEL_CONFIANZA   |
|:---------------|-----------------------:|-----------------------:|-------------------:|:-------------------------------|:---------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------|:------------------|
| I162S2C13J1V1  |                     13 |                      1 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 13 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C13J2V1  |                     13 |                      2 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 13 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C21J1V1  |                     21 |                      1 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 21 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C21J2V1  |                     21 |                      2 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 21 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C23J1V1  |                     23 |                      1 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 23 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C23J2V1  |                     23 |                      2 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 23 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C24J1V1  |                     24 |                      1 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 24 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C24J2V1  |                     24 |                      2 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 24 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C3J2V2   |                      3 |                      2 |                  2 | MATCH_RESUELTO_POR_VERSION     | Existe mismo COD_SEDE+COD_CARRERA+COD_JORNADA con otra VERSION: I162S2C3J2V1, I162S2C3J2V3, I162S2C3J2V4 | No completar automáticamente en esta corrida; revisar versión y, si se aprueba equivalencia, ampliar/ajustar diccionario. | MEDIA             |
| I162S2C41J2V1  |                     41 |                      2 |                  1 | REQUIERE_AGREGAR_A_DICCIONARIO | COD_CARRERA 41 no existe en el diccionario raw de oferta. Existe en matriz.                              | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | ALTA              |
| I162S2C6J4V1   |                      6 |                      4 |                  1 | MATCH_RESUELTO_POR_VERSION     | Existe mismo COD_SEDE+COD_CARRERA+COD_JORNADA con otra VERSION: I162S2C6J4V2                             | No completar automáticamente en esta corrida; revisar versión y, si se aprueba equivalencia, ampliar/ajustar diccionario. | MEDIA             |

## Resumen de dictámenes

- REQUIERE_AGREGAR_A_DICCIONARIO: 9
- MATCH_RESUELTO_POR_VERSION: 2

## Acción recomendada caso a caso

| CODIGO_UNICO   | ACCION_RECOMENDADA                                                                                                        | BLOQUEA_COPIA_FINAL_VALIDADA   | BLOQUEA_CSV_SIN_ENCABEZADOS   | MOTIVO                                                                                                   |
|:---------------|:--------------------------------------------------------------------------------------------------------------------------|:-------------------------------|:------------------------------|:---------------------------------------------------------------------------------------------------------|
| I162S2C13J1V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 13 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C13J2V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 13 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C21J1V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 21 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C21J2V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 21 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C23J1V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 23 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C23J2V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 23 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C24J1V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 24 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C24J2V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 24 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C3J2V2   | No completar automáticamente en esta corrida; revisar versión y, si se aprueba equivalencia, ampliar/ajustar diccionario. | SI                             | SI                            | Existe mismo COD_SEDE+COD_CARRERA+COD_JORNADA con otra VERSION: I162S2C3J2V1, I162S2C3J2V3, I162S2C3J2V4 |
| I162S2C41J2V1  | Agregar fila institucional A:AH al diccionario desde fuente oficial antes de completar campos.                            | SI                             | SI                            | COD_CARRERA 41 no existe en el diccionario raw de oferta. Existe en matriz.                              |
| I162S2C6J4V1   | No completar automáticamente en esta corrida; revisar versión y, si se aprueba equivalencia, ampliar/ajustar diccionario. | SI                             | SI                            | Existe mismo COD_SEDE+COD_CARRERA+COD_JORNADA con otra VERSION: I162S2C6J4V2                             |

## ¿Se puede generar copia final enriquecida?

NO. Solo se genera copia final si los 11 quedan resueltos sin `NO_APTO`, sin `REQUIERE_AGREGAR_A_DICCIONARIO`, sin `REQUIERE_REVISION_COMBINACION` y sin `REQUIERE_DECISION_INSTITUCIONAL`.

## ¿Se puede generar CSV sin encabezados?

NO. No corresponde generar CSV mientras existan pendientes o faltantes de diccionario.

## Validaciones técnicas

- Excel de auditoría OOXML válido: OK
- Abre con openpyxl: OK
- Sin fórmulas: OK
- Sin macros: OK
- Sin vínculos externos: OK
- Sin gráficos, dibujos ni conexiones: OK
- Hojas con nombres <=31 caracteres y sin caracteres inválidos: OK
- DICTAMEN_11_CASOS tiene exactamente 11 filas: OK
- Sin CODIGO_UNICO vacío ni duplicado: OK
- ACCION_RECOMENDADA, MOTIVO_DICTAMEN y NIVEL_CONFIANZA completos: OK

## Estado Git observado antes de escribir este Markdown

### git status --short

```text
(sin cambios)
```

### git status

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

nothing to commit, working tree clean
```

## Dictamen final

`DICTAMEN_FINAL: ERROR_EN_CONCILIACION_DICCIONARIO_OFERTA_11_CASOS_PENDIENTES`


## Estado Git final posterior a artefactos

### git status --short

```text
?? indices_2025/cned/resultados/CNED_AUDITORIA_11_SIN_MATCH_DICCIONARIO_20260604_105355.md
```

### git status

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	indices_2025/cned/resultados/CNED_AUDITORIA_11_SIN_MATCH_DICCIONARIO_20260604_105355.md

nothing added to commit but untracked files present (use "git add" to track)
```
