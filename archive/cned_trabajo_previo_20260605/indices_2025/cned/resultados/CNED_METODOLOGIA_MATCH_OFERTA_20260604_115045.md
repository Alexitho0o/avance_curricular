# Metodología de match Oferta Académica 2026 contra PROGRAMAS_FALTANTES_PARA_CREAR

## Objetivo

Esta auditoría establece y prueba reglas de match R1-R5 para los 71 registros de `PROGRAMAS_FALTANTES_PARA_CREAR`. No genera archivo operativo final ni CSV de carga.

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

## Columnas inspeccionadas

- PROGRAMAS_FALTANTES_PARA_CREAR: 88 columnas
- Diccionario complementado: 65 columnas
- PROMEDIOS matriz: 21 columnas
- Referencia ÍNDICES: 23 columnas

## Conteos fuente

- PROGRAMAS_FALTANTES_PARA_CREAR: 71 filas, 71 códigos únicos
- Diccionario complementado: 133 filas, 133 códigos únicos
- PROMEDIOS matriz: 139 filas, 139 códigos únicos
- Referencia ÍNDICES: 79 filas, 65 códigos únicos

## Resultado de reglas R1-R5

| MATCH_METHOD             |   TOTAL |
|:-------------------------|--------:|
| R1_CODIGO_UNICO_DERIVADO |      69 |
| SIN_MATCH                |       2 |

## Estados finales de match

| MATCH_STATUS   |   TOTAL |
|:---------------|--------:|
| MATCH_UNICO    |      69 |
| SIN_MATCH      |       2 |

## Pendientes metodológicos no directos

| CODIGO_UNICO   | NOMBRE_CARRERA                     | MATCH_STATUS_FINAL   | MATCH_METHOD_FINAL   |   MATCH_COUNT_FINAL | MATCH_CODIGO_UNICO_DERIVADO   | MATCH_OBSERVACION                    | DICTAMEN_METODOLOGICO   |
|:---------------|:-----------------------------------|:---------------------|:---------------------|--------------------:|:------------------------------|:-------------------------------------|:------------------------|
| I162S2C3J2V2   | INGENIERIA EN CONECTIVIDAD Y REDES | SIN_MATCH            | SIN_MATCH            |                   0 |                               | No existe candidato en reglas R1-R5. | PENDIENTE_SIN_MATCH     |
| I162S2C6J4V1   | TECNICO EN CONECTIVIDAD Y REDES    | SIN_MATCH            | SIN_MATCH            |                   0 |                               | No existe candidato en reglas R1-R5. | PENDIENTE_SIN_MATCH     |

## Clasificación de campos

| CLASIFICACION              |   TOTAL |
|:---------------------------|--------:|
| SIN_FUENTE                 |     631 |
| AUTO_COMPLETABLE_CON_MAPEO |     524 |
| AUTO_COMPLETABLE           |     322 |
| NO_AUTO_REQUIERE_CRITERIO  |      14 |

## Campos sin fuente en bases actuales

AREA_ACTUAL, Año de inicio de Actividades, Carrera Genérica, Dependencia, Duración régimen, Grado Académico que otorga el programa, Ingreso Directo, Ingreso desde Bachillerato, Ingreso desde un plan Común, Ingreso otro, Otro Tipo de Ingreso, Régimen, Sub Área, Título que otorga el programa, Área del Conocimiento

## Campos no automáticos que requieren criterio

AREA_ACTUAL, Año de inicio de Actividades, Duración régimen, Ingreso Directo, Régimen, Título que otorga el programa, Área del Conocimiento

## Conflictos entre fuentes

(sin filas)

## Rutas de artefactos

- Markdown: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.md`
- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.xlsx`
- CSV: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_METODOLOGIA_MATCH_OFERTA_20260604_115045.csv`

## Estado Git al cierre del script

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

`DICTAMEN_FINAL: METODOLOGIA_MATCH_VALIDADA_69_COMPLETABLES_2_PENDIENTES`
