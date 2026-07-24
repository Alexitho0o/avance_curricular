# Reporte corregido comparación publicacion2026 vs congelado vigente MU Pregrado 2026

> El análisis anterior comparó la publicación contra el universo histórico completo, incluyendo registros con VIG=0. Conforme al Manual de Matrícula Unificada 2026, dichos registros no se contabilizan en la matrícula total de la institución. Esta versión corrige el universo comparable y utiliza exclusivamente registros con VIG=1 o VIG=2.

## Estado Del Análisis Anterior

`SUPERADO POR CORRECCIÓN METODOLÓGICA`. Motivo: `UNIVERSO_COMPARABLE_INCLUÍA_VIG_0`.

## Fuentes

- Publicación: `/Users/alexi/Documents/GitHub/avance_curricular/publicacion2026.xlsx`, hoja `Hoja1`, hash `9312665c74102bef111fa6618a379bfd57170b376ebc8e501ab7c92dba421da2`.
- Congelado Punto 0: 4070 registros, hash `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`.
- Complemento 95 V3: 95 registros, hash `1940923b7e9f811df9b5af50d0badc8563bc17ed9ce8078fbab054d221c6e1f2`.
- Congelado histórico derivado: 4165 registros, hash `48a950179066b7beffd31fa46377ab2caaf46ca61edb870796aff0deecfe62e9`.

## Universos

- Histórico congelado: 4165 registros, solo trazabilidad/control.
- VIG=0: 960 registros.
- VIG=1: 3205 registros.
- VIG=2: 0 registros.
- Comparable publicado: 3205 registros con VIG IN (1,2).

## Totales Corregidos

- Total publicación: 3425
- Diferencia principal publicación vs congelado vigente: 220
- Diferencia histórica publicación vs congelado completo: -740, `NO COMPARABLE PARA MATRÍCULA TOTAL`.

## Ofertas

| Métrica | Valor |
| --- | --- |
| Ofertas únicas publicación | 66 |
| Ofertas únicas congelado histórico | 61 |
| Ofertas únicas congelado vigente | 61 |
| Ofertas presentes en ambos universos comparables | 61 |
| Ofertas con igual matrícula | 14 |
| Ofertas con diferencias | 47 |
| Ofertas solo publicación | 5 |
| Ofertas solo congelado vigente | 0 |
| Ofertas existentes únicamente con VIG=0 | 0 |

## Principales Variaciones Corregidas

| CODIGO_UNICO | MATRICULA_PUBLICACION | CONGELADO_VIG_1 | CONGELADO_VIG_2 | CONGELADO_VIGENTE_TOTAL | CONGELADO_VIG_0 | CONGELADO_HISTORICO_TOTAL | DIF_PUBLICACION_VS_VIGENTE | CLASIFICACION_COMPARABLE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C70J4V1 | 22 | 0 | 0 | 0 | 0 | 0 | 22 | SOLO_PUBLICACION |
| I162S2C91J2V1 | 112 | 93 | 0 | 93 | 42 | 135 | 19 | PUBLICACION_MAYOR |
| I162S2C91J1V1 | 87 | 69 | 0 | 69 | 28 | 97 | 18 | PUBLICACION_MAYOR |
| I162S2C53J3V1 | 17 | 0 | 0 | 0 | 0 | 0 | 17 | SOLO_PUBLICACION |
| I162S2C114J2V1 | 94 | 79 | 0 | 79 | 11 | 90 | 15 | PUBLICACION_MAYOR |
| I162S2C66J4V1 | 15 | 0 | 0 | 0 | 0 | 0 | 15 | SOLO_PUBLICACION |
| I162S2C57J4V1 | 257 | 246 | 0 | 246 | 52 | 298 | 11 | PUBLICACION_MAYOR |
| I162S2C76J4V1 | 132 | 122 | 0 | 122 | 56 | 178 | 10 | PUBLICACION_MAYOR |
| I162S2C112J4V1 | 66 | 57 | 0 | 57 | 8 | 65 | 9 | PUBLICACION_MAYOR |
| I162S2C83J4V1 | 94 | 85 | 0 | 85 | 46 | 131 | 9 | PUBLICACION_MAYOR |
| I162S2C76J2V1 | 25 | 18 | 0 | 18 | 15 | 33 | 7 | PUBLICACION_MAYOR |
| I162S2C89J4V1 | 37 | 30 | 0 | 30 | 14 | 44 | 7 | PUBLICACION_MAYOR |

## Comparación Por Sede

| COD_SED | Publicación | Congelado VIG=1 | Congelado VIG=2 | Congelado vigente | Congelado VIG=0 | Diferencia principal |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 3352 | 3140 | 0 | 3140 | 952 | 212 |
| 3 | 73 | 65 | 0 | 65 | 8 | 8 |

## Duplicados

Los duplicados son diagnóstico de llave. No se eliminaron ni descontaron automáticamente; la agregación por oferta conserva todos los registros vigentes.

| Llave | Grupos duplicados | Registros involucrados | Máximo registros por grupo | Grupos misma carrera/oferta | Grupos carreras/ofertas distintas | Grupos con diferente VIG | Registros vigentes involucrados |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LLAVE_PERSONA | 94 | 188 | 2 | 89 | 5 | 5 | 183 |
| LLAVE_MATRICULA | 89 | 178 | 2 | 89 | 0 | 5 | 173 |

## Pendientes

- La publicación no define que `TOTAL MATRÍCULA` sean personas únicas; se clasifica como `MATRICULA_AGREGADA_PUBLICADA`.
- No procede comparación persona a persona con esta publicación agregada.
- Para cerrar una brecha institucional definitiva se requiere confirmar la unidad estadística publicada o disponer de exportación oficial publicada con microdatos.
