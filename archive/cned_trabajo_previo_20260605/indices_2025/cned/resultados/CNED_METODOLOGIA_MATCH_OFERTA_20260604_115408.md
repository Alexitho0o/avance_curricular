# Metodología de match Oferta Académica 2026 contra PROGRAMAS_FALTANTES_PARA_CREAR

## Objetivo

Esta auditoría establece y prueba reglas de match R1-R5 para los 71 registros de `PROGRAMAS_FALTANTES_PARA_CREAR`. No genera archivo operativo final ni CSV de carga.

## Corrección metodológica aplicada

Las reglas R3 y R5 usan `PROMEDIOSDEALUMNOS_7804.xlsx / matriz` como respaldo para campos estructurales que no están completos en la hoja operativa, evitando confundir ausencia real de fuente con una falla de lógica de match.

## Archivos usados

- Operativo reconciliado: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_RECONCILIADO.xlsx`
- PROMEDIOS matriz: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`
- Diccionario complementado TSV: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`
- Referencia CNED/ÍNDICES: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`

## Hashes SHA256

- `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO_CON_DICCIONARIO_RECONCILIADO.xlsx`: `5b3989d80aeef13798f9369eccd28767257b72f92317b6bac9b2f73e02d1e172`
- `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx`: `3013fed700f871f93379bc93ebf974910f30c7c4320d40bd3d8b8638fad6a5fb`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS_COMPLEMENTADO_20260604_110722.tsv`: `6f37fb1b393092fd0db6e3659ff6c2f663e677ffe435f719ce088f03c6152c0e`
- `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/listado_referencia_cned.tsv`: `ed6a947de6650842eb739e85f5c1be8d77c1d591fe256990abd8cacfddffcde0`

## Conteos fuente

- PROGRAMAS_FALTANTES_PARA_CREAR: 71 filas, 71 códigos únicos
- Diccionario complementado: 133 filas, 133 códigos únicos
- PROMEDIOS matriz: 139 filas, 139 códigos únicos
- Referencia ÍNDICES: 79 filas, 65 códigos únicos

## Resultado de reglas R1-R5

| MATCH_METHOD             |   TOTAL |
|:-------------------------|--------:|
| R1_CODIGO_UNICO_DERIVADO |      69 |
| R4_NOMBRE_SEDE_JORNADA   |       1 |
| R3_ESTRUCTURAL_FUERTE    |       1 |

## Estados finales de match

| MATCH_STATUS   |   TOTAL |
|:---------------|--------:|
| MATCH_UNICO    |      70 |
| MATCH_AMBIGUO  |       1 |

## Pendientes metodológicos no directos

| CODIGO_UNICO   | NOMBRE_CARRERA                     | MATCH_STATUS_FINAL   | MATCH_METHOD_FINAL     |   MATCH_COUNT_FINAL | MATCH_CODIGO_UNICO_DERIVADO            | MATCH_OBSERVACION                                                                                                                   | DICTAMEN_METODOLOGICO                                    |
|:---------------|:-----------------------------------|:---------------------|:-----------------------|--------------------:|:---------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------|
| I162S2C3J2V2   | INGENIERIA EN CONECTIVIDAD Y REDES | MATCH_AMBIGUO        | R4_NOMBRE_SEDE_JORNADA |                   3 | I162S2C3J2V1|I162S2C3J2V3|I162S2C3J2V4 | Múltiples candidatos; no completar automáticamente.                                                                                 | PENDIENTE_MATCH_AMBIGUO_EXPLICADO                        |
| I162S2C6J4V1   | TECNICO EN CONECTIVIDAD Y REDES    | MATCH_UNICO          | R3_ESTRUCTURAL_FUERTE  |                   1 | I162S2C6J4V2                           | Match no directo usando estructura/nombre; candidato trazable, pero no aplicar automáticamente si cambia CODIGO_UNICO sin criterio. | MATCH_NO_DIRECTO_REQUIERE_CRITERIO_NO_APLICAR_AUTOMATICO |

## Clasificación de campos

| CLASIFICACION              |   TOTAL |
|:---------------------------|--------:|
| SIN_FUENTE                 |     568 |
| AUTO_COMPLETABLE_CON_MAPEO |     528 |
| AUTO_COMPLETABLE           |     325 |
| NO_AUTO_REQUIERE_CRITERIO  |      70 |

## Campos sin fuente en bases actuales

Carrera Genérica, Dependencia, Grado Académico que otorga el programa, Ingreso desde Bachillerato, Ingreso desde un plan Común, Ingreso otro, Otro Tipo de Ingreso, Sub Área

## Campos no automáticos que requieren criterio

AREA_ACTUAL, Año de inicio de Actividades, Duración régimen, Ingreso Directo, Régimen, Título que otorga el programa, Área del Conocimiento

## Conflictos entre fuentes

(sin filas)

## Rutas de artefactos

- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115408.md`
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115408.xlsx`
- CSV: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115408.csv`

## Estado Git al cierre del script

### git status --short

```text
?? indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.md
```

### git status

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.md

nothing added to commit but untracked files present (use "git add" to track)
```

## Dictamen final

`DICTAMEN_FINAL: METODOLOGIA_MATCH_VALIDADA_69_COMPLETABLES_2_PENDIENTES`


## Estado Git final posterior a artefactos

### git status --short

```text
?? indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.md
?? indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115408.md
```

### git status

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.md
	indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115408.md

nothing added to commit but untracked files present (use "git add" to track)
```
