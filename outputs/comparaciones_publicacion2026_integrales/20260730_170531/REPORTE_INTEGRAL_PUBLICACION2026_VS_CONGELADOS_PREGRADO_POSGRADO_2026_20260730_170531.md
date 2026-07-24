# Reporte integral publicacion2026 vs congelados pregrado/posgrado 2026

## Contexto
Proceso: Matrícula Unificada 2026. La publicación se trata como `MATRICULA_AGREGADA_PUBLICADA`; no como personas únicas.

## Problema corregido
El análisis anterior se marca como `SUPERADO POR SEPARACIÓN OBLIGATORIA DE PREGRADO Y POSGRADO`. Esta versión separa `publicacion2026.xlsx` por el campo explícito `NIVEL GLOBAL` y compara cada nivel contra su congelado correspondiente.

## Fuentes
- Publicación: `/Users/alexi/Documents/GitHub/avance_curricular/publicacion2026.xlsx`; hoja `Hoja1`; hash `9312665c74102bef111fa6618a379bfd57170b376ebc8e501ab7c92dba421da2`.
- Pregrado: congelado histórico derivado Punto 0 + complemento 95; hash `48a950179066b7beffd31fa46377ab2caaf46ca61edb870796aff0deecfe62e9`.
- Posgrado/Postítulo: `matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv`; hash `0cd4c6343dbd886e259db5f86ecff70a08840d2b556bc398543711b66a94608a`.

## Selección de congelados
Pregrado se selecciona desde dos componentes gobernados: Punto 0 `PARA_SUBIR` validado y complemento 95 V3 finalizado en PES. Posgrado/Postítulo se selecciona desde el archivo con encabezados de 54 registros, respaldado por el cierre de RUT inválido y la reconciliación 66 a 54.

## Clasificación de la publicación
- Total publicación: 3425.
- Pregrado publicado: 3371.
- Posgrado/Postítulo publicado: 54.
- Ambiguo: 0.
- No clasificado: 0.

## Resultados de pregrado
- Congelado histórico: 4165.
- VIG=0: 960; VIG=1: 3205; VIG=2: 0.
- Congelado comparable: 3205.
- Diferencia pregrado: 166.

Principales variaciones de pregrado:
| CODIGO_UNICO | Nombre_oferta | Publicación | Congelado VIG=1 | Congelado VIG=2 | Congelado vigente | VIG=0 | Congelado histórico | Diferencia | Clasificación | COD_SED | COD_CAR | MODALIDAD | JOR | VERSION | Filas_publicacion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C91J2V1 | TECNICO EN ENFERMERIA | 112 | 93 | 0 | 93 | 42 | 135 | 19 | PUBLICACION_MAYOR | 2 | 91 | 1 | 2 | 1 | 1 |
| I162S2C91J1V1 | TECNICO EN ENFERMERIA | 87 | 69 | 0 | 69 | 28 | 97 | 18 | PUBLICACION_MAYOR | 2 | 91 | 1 | 1 | 1 | 1 |
| I162S2C114J2V1 | TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA | 94 | 79 | 0 | 79 | 11 | 90 | 15 | PUBLICACION_MAYOR | 2 | 114 | 1 | 2 | 1 | 1 |
| I162S2C57J4V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 257 | 246 | 0 | 246 | 52 | 298 | 11 | PUBLICACION_MAYOR | 2 | 57 | 3 | 4 | 1 | 1 |
| I162S2C76J4V1 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | 132 | 122 | 0 | 122 | 56 | 178 | 10 | PUBLICACION_MAYOR | 2 | 76 | 3 | 4 | 1 | 1 |
| I162S2C112J4V1 | INGENIERIA EN MARKETING DIGITAL | 66 | 57 | 0 | 57 | 8 | 65 | 9 | PUBLICACION_MAYOR | 2 | 112 | 3 | 4 | 1 | 1 |
| I162S2C83J4V1 | ADMINISTRACION PUBLICA | 94 | 85 | 0 | 85 | 46 | 131 | 9 | PUBLICACION_MAYOR | 2 | 83 | 3 | 4 | 1 | 1 |
| I162S2C76J2V1 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | 25 | 18 | 0 | 18 | 15 | 33 | 7 | PUBLICACION_MAYOR | 2 | 76 | 1 | 2 | 1 | 1 |
| I162S2C89J4V1 | TECNICO EN CIENCIA DE DATOS | 37 | 30 | 0 | 30 | 14 | 44 | 7 | PUBLICACION_MAYOR | 2 | 89 | 3 | 4 | 1 | 1 |
| I162S2C111J4V1 | INGENIERIA EN FINANZAS | 30 | 24 | 0 | 24 | 9 | 33 | 6 | PUBLICACION_MAYOR | 2 | 111 | 3 | 4 | 1 | 1 |
| I162S2C113J4V1 | INGENIERIA EN RECURSOS HUMANOS | 33 | 27 | 0 | 27 | 10 | 37 | 6 | PUBLICACION_MAYOR | 2 | 113 | 3 | 4 | 1 | 1 |
| I162S2C47J4V1 | TECNICO EN CIBERSEGURIDAD | 111 | 105 | 0 | 105 | 34 | 139 | 6 | PUBLICACION_MAYOR | 2 | 47 | 3 | 4 | 1 | 1 |
| I162S2C88J4V1 | INGENIERIA EN CIENCIA DE DATOS | 52 | 46 | 0 | 46 | 26 | 72 | 6 | PUBLICACION_MAYOR | 2 | 88 | 3 | 4 | 1 | 1 |
| I162S2C77J4V1 | INGENIERIA EN LOGISTICA | 98 | 93 | 0 | 93 | 35 | 128 | 5 | PUBLICACION_MAYOR | 2 | 77 | 3 | 4 | 1 | 1 |
| I162S2C87J4V1 | INGENIERIA INDUSTRIAL | 5 | 0 | 0 | 0 | 0 | 0 | 5 | SOLO_PUBLICACION |  |  |  |  |  | 1 |

## Resultados de posgrado/postítulo
- Congelado histórico/comparable: 54 / 54.
- Publicado posgrado/postítulo: 54.
- Diferencia posgrado/postítulo: 0.

| CODIGO_UNICO | Publicación | Nombre_programa | Filas_publicacion | Congelado comparable | Congelado histórico | Diferencia | Clasificación |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I162S2C53J3V1 | 17 | DIPLOMADO EN CIBERSEGURIDAD APLICADA | 1 | 17 | 17 | 0 | IGUAL |
| I162S2C66J4V1 | 15 | DIPLOMADO EN FULLSTACK | 1 | 15 | 15 | 0 | IGUAL |
| I162S2C70J4V1 | 22 | DIPLOMADO REDES INDUSTRIALES | 1 | 22 | 22 | 0 | IGUAL |

## Validación de la diferencia de 220
Estado: `HIPOTESIS_NO_CONFIRMADA`.
Los 220 no corresponden íntegramente a posgrado/postítulo: la publicación posgrado/postítulo suma 54 y coincide con el congelado posgrado/postítulo comparable. La diferencia remanente observada está en pregrado: 3371 publicado contra 3205 vigente congelado, diferencia +166.

## Duplicados
- Pregrado, llave persona: 94 grupos y 188 registros involucrados.
- Pregrado, llave matrícula: 89 grupos y 178 registros involucrados.
- Posgrado/Postítulo: sin duplicados por persona ni por programa en el congelado seleccionado.
Los duplicados no fueron eliminados ni descontados automáticamente.

## Limitaciones y pendientes
- El archivo de carga posgrado/postítulo sin encabezados de 54 filas no está materializado en el árbol de trabajo actual; se usa el archivo local con encabezados de 54 filas respaldado por el cierre gobernado.
- Dos ofertas publicadas como pregrado no aparecen en el congelado pregrado vigente/histórico y quedan como `SOLO_PUBLICACION`.

## Conclusión
La hipótesis de que los 220 corresponden a posgrado/postítulo queda rechazada con evidencia local: posgrado/postítulo explica 54 registros publicados y concilia contra su congelado; no explica 220. La comparación principal queda separada por nivel y no vuelve a comparar los 3425 publicados exclusivamente contra pregrado.
