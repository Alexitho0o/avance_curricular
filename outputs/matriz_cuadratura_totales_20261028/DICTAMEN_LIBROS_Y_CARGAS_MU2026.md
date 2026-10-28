# Dictamen de libros internos y prueba acumulativa MU2026

| Libro | (a) Fuente SIES | (b) Brecha 226 | (c) Otro uso |
|---|---|---|---|
| MATRÍCULA UNIFICADA 2026.xlsx | NO SIRVE: libro interno, no descarga PES acreditada | NO SIRVE: derivado que reproduce nuestra base | SIRVE: auditoría de nuestra MU y reproducción histórica H001; no es evidencia independiente de SIES |
| Matricula Unificada_ ABF.xlsx | NO SIRVE: preparación interna anterior al corte | SIRVE PARCIAL: prueba de compatibilidad por código; no acredita aceptación SIES | SIRVE: trazabilidad UMAS pre-corte, continuidad y preparación MU |
| RESPALDO MATRÍCULA UNIFICADA 2026.xlsx | NO SIRVE: libro de preparación anterior al corte, sin prueba de recepción PES | SIRVE PARCIAL: propuesta pre-corte del primer año; no valida la cifra SIES | SIRVE: preparación MU/FCU y control de cohorte inicial. SUBIR contiene estructura MU de 32 campos; no se reduce a FCU. |

## Metadatos y composición de los libros [B]

Las fechas son propiedades OOXML editables, sin zona horaria acreditada; no prueban corte ni recepción PES. Dimensiones incluyen encabezados y posibles celdas de formato.

### MATRÍCULA UNIFICADA 2026.xlsx

Autor: openpyxl. Último modificador: Alexi Marcelo Burgos Flores. Creación: 2026-07-01 04:37:04. Modificación: 2026-10-15 13:02:51.
SHA-256: `7787626606187375b6915a0c0651885fff54567841e87e7685351a8b593d65f1`.

| Hoja | Filas declaradas | Columnas declaradas |
|---|---:|---:|
| 06_DETALLE_TOTAL | 4106 | 20 |
| Hoja1 | 2380 | 25 |
| 00_RESUMEN_GENERAL | 10 | 2 |
| 01_RESUMEN_ESTADO | 3 | 4 |
| 02_VIGENTES_CARRERA_SEDE | 53 | 5 |
| 03_VIGENTES_ANIO_INGRESO | 9 | 4 |
| 04_DETALLE_VIGENTES | 3146 | 19 |
| 05_DETALLE_NO_VIGENTES | 961 | 19 |
| 07_CARRERA_ESTADO | 65 | 4 |
| 08_RUT_MULTIMATRICULA | 35 | 4 |
| 09_CONSOLIDADO_J4 | 14 | 8 |
| 10_CONSOLIDADO_JORNADAS | 30 | 22 |

### Matricula Unificada_ ABF.xlsx

Autor: ALEXI MARCELO BURGOS FLORES. Último modificador: Karla A. Munoz Gajardo. Creación: 2026-04-09 14:56:32. Modificación: 2026-04-09 21:02:13.
SHA-256: `02b48ea4f4de0cd210bfeb743149f063947e121aed70442a1f6a541cb2be1e44`.

| Hoja | Filas declaradas | Columnas declaradas |
|---|---:|---:|
| MATRICULA_UNIFICADA_32 | 1283 | 38 |
| Hoja3 | 1 | 1 |
| Vigentes | 3408 | 68 |
| Continuidades | 401 | 68 |

### RESPALDO MATRÍCULA UNIFICADA 2026.xlsx

Autor: Natalia Gajardo Mejias. Último modificador: ALEXI MARCELO BURGOS FLORES. Creación: 2026-01-06 15:27:12. Modificación: 2026-03-25 15:05:00.
SHA-256: `7a9240c994cbf375a0ff5e871f5a8eca70e94c8605fffa40b5b8c53d3366ada5`.

| Hoja | Filas declaradas | Columnas declaradas |
|---|---:|---:|
| Hoja4 | 35 | 5 |
| Hoja5 | 33 | 8 |
| TASA RESPUESTA | 1040 | 33 |
| SUBIR sin continuidad | 1040 | 32 |
| SUBIR | 1188 | 32 |
| BBDD | 1190 | 63 |
| BD 2 | 1189 | 73 |
| Hoja2 | 1189 | 20 |
| Hoja3 | 1313 | 2 |

## Universo, grano y relación con MU [B/C]

06_DETALLE_TOTAL: 4.105 matrículas por documento/código; idéntico por documento, código y VIG, con cero filas exclusivas. Hoja1: 2.379 personas-cohorte H001 (305/366/558/1.150 para 2022/2023/2024/2025), idénticas a V24 por documento/cohorte/indicador. Esto acredita contenido, no la autoría del proceso que creó Hoja1.

ABF · Vigentes: {"registros": 3407, "personas_documento": 3377, "expedientes_documento_codcli": 3407, "estados": {"VIGENTE": 3407}, "grano": "expediente UMAS; la persona puede repetirse por CODCLI", "documentos_en_mu2026": 3259, "relacion_documentos_mu2026": "independiente con intersección parcial", "normalizacion_documento": "RUT cuerpo en columnas A/K + DV en L; se conserva DV numérico 0. No se cruza el cuerpo solo."}
ABF · Continuidades: {"registros": 400, "personas_documento": 400, "expedientes_documento_codcli": 400, "estados": {"VIGENTE": 400}, "grano": "expediente UMAS; la persona puede repetirse por CODCLI", "documentos_en_mu2026": 394, "relacion_documentos_mu2026": "independiente con intersección parcial"}
ABF · MATRICULA_UNIFICADA_32: {"registros": 1282, "matriculas_con_llave": 1282, "llaves_distintas": 1282, "grano": "matrícula preparada de 32 campos MU", "relacion_mu2026_documento_codigo": "independiente con intersección parcial", "interseccion_mu2026": 1229, "coincidencias_tambien_vig": 1036, "sin_correspondencia_mu2026": 53, "campos_ingreso_y_vig": {"ANIO_ING_ACT": {"2026": 1024, "2024": 43, "2025": 199, "2023": 11, "2022": 5}, "SEM_ING_ACT": {"1": 1278, "2": 4}, "ANIO_ING_ORI": {"2026": 953, "2024": 43, "2025": 199, "1900": 71, "2023": 11, "2022": 5}, "SEM_ING_ORI": {"1": 1278, "2": 4}, "VIG": {"1": 1260, "0": 22}}}

Continuidades: 400 de 400 expedientes ya están en Vigentes; no se suman nuevamente.
RESPALDO · SUBIR: {"registros": 1187, "matriculas_con_llave": 1187, "llaves_distintas": 1187, "grano": "matrícula preparada de 32 campos MU", "relacion_mu2026_documento_codigo": "independiente con intersección parcial", "interseccion_mu2026": 830, "coincidencias_tambien_vig": 614, "sin_correspondencia_mu2026": 357, "campos_ingreso_y_vig": {"ANIO_ING_ACT": {"2025": 3, "2026": 1184}, "SEM_ING_ACT": {"1": 1187}, "ANIO_ING_ORI": {"2026": 1039, "2024": 148}, "SEM_ING_ORI": {"2": 3, "1": 1184}, "VIG": {"1": 1187}}, "registros_en_48_codigos": 1050}

Los conjuntos ABF y SUBIR son independientes con intersección parcial respecto de MU anual; no son subconjuntos por documento/código. Las identidades se comparan con DV explícito, incluido 0.

## Compatibilidad por código de la fotografía UMAS de abril [C/E]

**Compatible con el 84,65% (aproximadamente 85%) de la brecha positiva; no acredita aceptación SIES.** La hipótesis contempla una parte de las VIG 0 vigentes en abril, sin sumar automáticamente las 459.

| Grupo disjunto | Códigos | Brecha positiva | Cubrible | Sin cubrir |
|---|---:|---:|---:|---:|
| Positiva cubierta totalmente (4 exactos) | 30 | 139 | 139 | 0 |
| Positiva insuficiente | 16 | 89 | 54 | 35 |
| Total positivo | 46 | 228 | 193 | 35 |

Cubrible = suma de min(brecha positiva, candidatas), calculada por código: 139 + 54 = 193; 193/228 = 84,6491%. Brecha neta: 228 − 2 = 226. Los 32 códigos que cumplen candidatas >= brecha incluyen dos negativos; no equivalen a 32 positivos ni a 193 cubribles por sí solos.

Las versiones de referencia usan código MU cuando es único en la misma familia o un candidato único. Las 49 filas no atribuibles quedan visibles. Todas las 459 coincidencias candidatas tienen familia única en este foco; no se acredita con ello la versión en abril ni aceptación SIES.

| Código | Vigentes abril atribuibles | VIG1 nuestra | Publicado | Brecha | Candidatas VIG0 abril | Cubrible | Sin cubrir |
|---|---:|---:|---:|---:|---:|---:|---:|
| I162S2C10J4V1 | 30 | 16 | 17 | 1 | 14 | 1 | 0 |
| I162S2C111J4V1 | 33 | 24 | 30 | 6 | 9 | 6 | 0 |
| I162S2C112J4V1 | 64 | 56 | 66 | 10 | 8 | 8 | 2 |
| I162S2C113J4V1 | 36 | 26 | 33 | 7 | 10 | 7 | 0 |
| I162S2C114J2V1 | 89 | 74 | 94 | 20 | 11 | 11 | 9 |
| I162S2C115J2V1 | 37 | 23 | 27 | 4 | 15 | 4 | 0 |
| I162S2C116J4V1 | 33 | 23 | 24 | 1 | 10 | 1 | 0 |
| I162S2C118J4V1 | 89 | 62 | 64 | 2 | 27 | 2 | 0 |
| I162S2C124J4V1 | 35 | 24 | 25 | 1 | 11 | 1 | 0 |
| I162S2C125J4V1 | 25 | 11 | 13 | 2 | 14 | 2 | 0 |
| I162S2C1J1V2 | 30 | 33 | 34 | 1 | 0 | 0 | 1 |
| I162S2C1J2V4 | 30 | 29 | 32 | 3 | 2 | 2 | 1 |
| I162S2C1J4V2 | 214 | 232 | 239 | 7 | 21 | 7 | 0 |
| I162S2C3J4V2 | 150 | 152 | 153 | 1 | 7 | 1 | 0 |
| I162S2C3J4V3 | 115 | 112 | 113 | 1 | 3 | 1 | 0 |
| I162S2C46J1V1 | 35 | 34 | 35 | 1 | 1 | 1 | 0 |
| I162S2C46J2V1 | 36 | 39 | 41 | 2 | 4 | 2 | 0 |
| I162S2C46J4V1 | 82 | 77 | 78 | 1 | 4 | 1 | 0 |
| I162S2C46J4V3 | 218 | 242 | 256 | 14 | 14 | 14 | 0 |
| I162S2C47J2V1 | 24 | 25 | 27 | 2 | 0 | 0 | 2 |
| I162S2C57J1V1 | 25 | 24 | 28 | 4 | 1 | 1 | 3 |
| I162S2C57J2V1 | 26 | 22 | 25 | 3 | 2 | 2 | 1 |
| I162S2C57J4V1 | 220 | 255 | 257 | 2 | 16 | 2 | 0 |
| I162S2C6J2V2 | 3 | 6 | 7 | 1 | 0 | 0 | 1 |
| I162S2C6J4V2 | 40 | 46 | 45 | -1 | 5 | 0 | 0 |
| I162S2C76J1V1 | 10 | 6 | 7 | 1 | 4 | 1 | 0 |
| I162S2C76J2V1 | 25 | 18 | 25 | 7 | 7 | 7 | 0 |
| I162S2C76J4V1 | 108 | 120 | 132 | 12 | 21 | 12 | 0 |
| I162S2C77J1V1 | 0 | 0 | 1 | 1 | 0 | 0 | 1 |
| I162S2C77J4V1 | 85 | 91 | 98 | 7 | 15 | 7 | 0 |
| I162S2C78J2V1 | 42 | 34 | 36 | 2 | 6 | 2 | 0 |
| I162S2C78J4V1 | 97 | 82 | 88 | 6 | 26 | 6 | 0 |
| I162S2C79J2V1 | 29 | 26 | 25 | -1 | 5 | 0 | 0 |
| I162S2C79J4V1 | 103 | 86 | 87 | 1 | 31 | 1 | 0 |
| I162S2C83J4V1 | 78 | 84 | 94 | 10 | 11 | 10 | 0 |
| I162S2C84J4V1 | 25 | 30 | 34 | 4 | 1 | 1 | 3 |
| I162S2C85J4V1 | 65 | 52 | 56 | 4 | 17 | 4 | 0 |
| I162S2C86J4V1 | 52 | 60 | 62 | 2 | 13 | 2 | 0 |
| I162S2C87J4V1 | 0 | 0 | 5 | 5 | 0 | 0 | 5 |
| I162S2C87J4V2 | 88 | 69 | 77 | 8 | 36 | 8 | 0 |
| I162S2C88J4V1 | 48 | 47 | 52 | 5 | 6 | 5 | 0 |
| I162S2C89J4V1 | 33 | 30 | 37 | 7 | 6 | 6 | 1 |
| I162S2C90J2V2 | 20 | 19 | 22 | 3 | 1 | 1 | 2 |
| I162S2C91J1V1 | 97 | 69 | 87 | 18 | 17 | 17 | 1 |
| I162S2C91J2V1 | 107 | 92 | 112 | 20 | 20 | 20 | 0 |
| I162S3C114J2V1 | 39 | 33 | 36 | 3 | 2 | 2 | 1 |
| I162S3C115J2V1 | 21 | 18 | 19 | 1 | 2 | 1 | 0 |
| I162S3C91J2V1 | 17 | 14 | 18 | 4 | 3 | 3 | 1 |

### Las 35 matrículas no cubiertas: pendientes E por código

| Código | Brecha positiva | Candidatas | Cubrible | Sin cubrir | Sólo publicado, sin MU |
|---|---:|---:|---:|---:|---|
| I162S2C112J4V1 | 10 | 8 | 8 | 2 | No |
| I162S2C114J2V1 | 20 | 11 | 11 | 9 | No |
| I162S2C1J1V2 | 1 | 0 | 0 | 1 | No |
| I162S2C1J2V4 | 3 | 2 | 2 | 1 | No |
| I162S2C47J2V1 | 2 | 0 | 0 | 2 | No |
| I162S2C57J1V1 | 4 | 1 | 1 | 3 | No |
| I162S2C57J2V1 | 3 | 2 | 2 | 1 | No |
| I162S2C6J2V2 | 1 | 0 | 0 | 1 | No |
| I162S2C77J1V1 | 1 | 0 | 0 | 1 | Sí |
| I162S2C84J4V1 | 4 | 1 | 1 | 3 | No |
| I162S2C87J4V1 | 5 | 0 | 0 | 5 | Sí |
| I162S2C89J4V1 | 7 | 6 | 6 | 1 | No |
| I162S2C90J2V2 | 3 | 1 | 1 | 2 | No |
| I162S2C91J1V1 | 18 | 17 | 17 | 1 | No |
| I162S3C114J2V1 | 3 | 2 | 2 | 1 | No |
| I162S3C91J2V1 | 4 | 3 | 3 | 1 | No |

### Brechas negativas: separadas de los pendientes positivos [E]

| Código | Diferencia publicado menos nuestra VIG1 |
|---|---:|
| I162S2C6J4V2 | -1 |
| I162S2C79J2V1 | -1 |

## Cargas acumulativas: preparadas, no ejecutadas [C/E]

A: Manual MU2026 p.15, líneas 468–478: cargas acumulativas; el registro se actualiza al cargarse correctamente, resultado Finalizado. P.16, líneas 483–498: Historial de Carga ordenado por fecha y acción ver el archivo cargado.

Las formulaciones originales documento+código único y documento+S+C+J+V eran equivalentes con I162 fijo y componentes coherentes [C]. Se reemplaza la segunda por una sensibilidad gruesa: L1 documento+código único; L2 documento+COD_CAR, sin sede, jornada ni versión. Documento conserva tipo, número y DV, incluido 0. Son candidatas C/E, no llave normativa PES confirmada.

Hipótesis C/E: si L1 reproduce mejor la publicación que L2 y el linaje identifica registros antiguos no sobrescritos, éstos son una explicación candidata. Se evaluará por código, discrepancia absoluta total y códigos coincidentes; el neto no basta. No acredita aceptación SIES.

Fuente requerida: Alexi descargará export o captura del Historial de Carga MU2026 y el archivo cargado de cada carga Finalizado. Se excluirán errores y se acreditarán orden, hashes y posibles reinicios. No se usarán archivos locales de envío. Protocolo: PREPARACION_CARGAS_ACUMULATIVAS_MU2026.json. No hay cifra reconstruida de VIG1 ni de llaves antiguas.
