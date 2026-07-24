# Auditoria diferencia +166 pregrado MU 2026

## Contexto

Esta auditoria reabre solo la diferencia de pregrado entre `publicacion2026.xlsx` y el congelado actual de Matricula Unificada Pregrado 2026. El bloque de Posgrado y Postitulo se mantiene separado: CONCILIADO_54_VS_54, con 54 publicados versus 54 congelados segun el manifest integral vigente.

## Problema

La publicacion contiene 3.371 registros agregados de pregrado, mientras el congelado pregrado comparable contiene 3.205 registros con `VIG in (1,2)`. La diferencia inicial es +166. No se interpreta como personas ni como error.

## Fuentes

- Publicacion: `/Users/alexi/Documents/GitHub/avance_curricular/publicacion2026.xlsx`. SHA-256 `9312665c74102bef111fa6618a379bfd57170b376ebc8e501ab7c92dba421da2`.
- Punto 0: `git:4f1108c:control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv`. SHA-256 `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`.
- Complemento 95 V3: `git_blob:d4bd44f9d1f11640056b8e990f5e1fcda9aebf7d`. SHA-256 `1940923b7e9f811df9b5af50d0badc8563bc17ed9ce8078fbab054d221c6e1f2`.
- Congelado actual combinado analitico: 4.165 registros historicos; hash logico `395e2041d5b23c07531e3f4097bc6ba9745b65c8de2ac0cded2b28c2c1db8093`.
- Manual local: `/Users/alexi/Documents/GitHub/avance_curricular/docs/manual_matricula_unificada.txt`.

## Congelado actualmente utilizado

El congelado actual validado sigue siendo el combinado derivado de Punto 0 `PARA_SUBIR` y complemento 95 V3. La evidencia local indica Punto 0 como archivo PES-ready/carga principal y el complemento 95 como carga complementaria finalizada en PES. No se encontro un candidato posterior gobernado que reemplace materialmente ese universo.

## Versiones candidatas

Se inventariaron 2780 candidatos/referencias CSV fisicas y de historial Git. La mejor coincidencia numerica no fue usada como criterio de seleccion institucional. No se identifico una version gobernada con 3.371 vigentes de pregrado ni una descarga posterior de PES que reproduzca la publicacion.

## Evidencia de PES

- Punto 0: validacion local de `PARA_SUBIR` con 4.070 filas y 32 columnas.
- Complemento 95 V3: manifest de cierre con estado `CARGA_COMPLEMENTARIA_95_FINALIZADA_EN_PES`.
- Manual: la carga se actualiza por recarga correcta/finalizada y `VIG=0` permanece almacenado pero no contabiliza en matricula total institucional.

## Origen de la publicacion

`publicacion2026.xlsx` trae un campo explicito de nivel. La publicacion pregrado se obtuvo filtrando `NIVEL GLOBAL = Pregrado` y sumando `TOTAL MATRICULA` por `CODIGO CARRERA`. No se encontro dentro del proyecto una fuente anterior, log o descarga PES que explique directamente el origen de los 3.371 de pregrado.

## Conciliacion de los 166

| Concepto | Valor |
|---|---:|
| Publicacion pregrado | 3371 |
| Congelado VIG=1 | 3205 |
| Congelado VIG=2 | 0 |
| Congelado comparable | 3205 |
| Diferencia inicial | 166 |
| Suma diferencias positivas | 186 |
| Suma absoluta diferencias negativas | 20 |
| Diferencia neta | 166 |

La diferencia queda aritmeticamente reconciliada por oferta: la suma de diferencias por `CODIGO_UNICO` es 166 y la suma positiva menos la negativa tambien es 166.

## Principales diferencias por oferta

| CODIGO_UNICO | Publicacion | CONGELADO_VIGENTE | DIFERENCIA | CLASIFICACION | ALERTA_POSIBLE |
| --- | --- | --- | --- | --- | --- |
| I162S2C91J2V1 | 112 | 93 | 19 | PUBLICACION_MAYOR |  |
| I162S2C91J1V1 | 87 | 69 | 18 | PUBLICACION_MAYOR |  |
| I162S2C114J2V1 | 94 | 79 | 15 | PUBLICACION_MAYOR |  |
| I162S2C57J4V1 | 257 | 246 | 11 | PUBLICACION_MAYOR |  |
| I162S2C76J4V1 | 132 | 122 | 10 | PUBLICACION_MAYOR |  |
| I162S2C112J4V1 | 66 | 57 | 9 | PUBLICACION_MAYOR |  |
| I162S2C83J4V1 | 94 | 85 | 9 | PUBLICACION_MAYOR |  |
| I162S2C76J2V1 | 25 | 18 | 7 | PUBLICACION_MAYOR |  |
| I162S2C89J4V1 | 37 | 30 | 7 | PUBLICACION_MAYOR |  |
| I162S2C111J4V1 | 30 | 24 | 6 | PUBLICACION_MAYOR |  |
| I162S2C113J4V1 | 33 | 27 | 6 | PUBLICACION_MAYOR |  |
| I162S2C47J4V1 | 111 | 105 | 6 | PUBLICACION_MAYOR |  |

## Analisis de VIG

El congelado historico contiene VIG=0: 960, VIG=1: 3205, VIG=2: 0. Incluir VIG=0 llevaria la comparacion a 4.165 historicos y produciria una diferencia de -794, por lo que VIG=0 no explica la publicacion como simple inclusion. Los VIG=0 se mantienen como auditoria historica.

## Duplicados

Llave persona: 94 grupos, 188 registros involucrados y 183 vigentes involucrados. Llave matricula: 89 grupos, 178 registros involucrados y 173 vigentes involucrados. La simulacion de conservar una fila por llave matricula reduce 84 registros vigentes, no explica causalmente el +166 y no fue aplicada al universo.

## Cargas y recargas

Se revisaron archivos fisicos, outputs, archive, scripts, manifiestos, reportes Markdown/TXT/JSON/logs y objetos del historial Git. No se encontro evidencia material de una recarga integral posterior de pregrado que produzca 3.371 vigentes ni reporte `Consultar Datos` posterior con ese total.

## Explicacion final

Estado final: `BLOQUEADO_POR_FALTA_DE_FUENTE`.

La diferencia +166 esta completamente descompuesta por oferta, pero no queda causalmente demostrada como registros agregados despues del congelado, cambio de regla de conteo, duplicados, uso de VIG=0, recarga posterior o cambio de codigos. La fuente material que explique los 3.371 publicados de pregrado no esta disponible en el proyecto.

## Diferencia residual

- Residual aritmetico por oferta: 0.
- Residual causal/documental: 166.

## Limitaciones

No se utilizaron fuentes externas. No se dedujeron personas desde la publicacion agregada. No se modificaron archivos originales. La seleccion final no se basa solamente en fecha, nombre o cantidad de filas.

## Pendientes

- Obtener fuente o reporte que genero `publicacion2026.xlsx`.
- Obtener descarga PES `Consultar Datos` posterior al cierre, si existio.
- Confirmar si hubo una recarga integral institucional posterior no materializada en este repositorio.

## Conclusion

La version congelada de pregrado actualmente respaldada por evidencia local suma 3.205 registros vigentes. La publicacion pregrado suma 3.371. La brecha de +166 se reconcilia por oferta pero no se explica documentalmente con las fuentes locales disponibles.
