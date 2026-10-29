# H002h · cohorte derivada y diagnóstico

D · Método aprobado por Alexi, 29-10-2026. B/C/E · Resultados descriptivos, sin activar reglas ni modificar H002/H002g.

## Vías de cohorte SIES

| Año | a actual | b origen | c primera observación | Censurada | Sin identificador | Total |
|---|---:|---:|---:|---:|---:|---:|
| 2007 | 697 | 0 | 0 | 0 | 0 | 697 |
| 2008 | 114 | 591 | 0 | 0 | 0 | 705 |
| 2009 | 104 | 614 | 0 | 0 | 0 | 718 |
| 2010 | 129 | 671 | 0 | 0 | 0 | 800 |
| 2011 | 124 | 705 | 0 | 0 | 0 | 829 |
| 2012 | 171 | 715 | 0 | 0 | 0 | 886 |
| 2013 | 206 | 989 | 0 | 0 | 0 | 1195 |
| 2014 | 244 | 936 | 0 | 0 | 0 | 1180 |
| 2015 | 285 | 911 | 0 | 0 | 0 | 1196 |
| 2016 | 304 | 773 | 0 | 0 | 0 | 1077 |
| 2017 | 298 | 906 | 0 | 0 | 0 | 1204 |
| 2018 | 1088 | 0 | 0 | 0 | 0 | 1088 |
| 2019 | 1112 | 0 | 0 | 0 | 0 | 1112 |
| 2020 | 985 | 0 | 0 | 0 | 0 | 985 |
| 2021 | 1105 | 0 | 0 | 0 | 0 | 1105 |
| 2022 | 1033 | 0 | 0 | 0 | 0 | 1033 |
| 2023 | 1161 | 0 | 0 | 0 | 0 | 1161 |
| 2024 | 1468 | 0 | 0 | 0 | 0 | 1468 |
| 2025 | 2522 | 0 | 0 | 0 | 0 | 2522 |

La vía c sólo estima el año. La vía b conserva el ingreso de origen como sustitución explícita D, sin certificar que sea ingreso a la carrera actual. Censurada no se interpreta como ingreso 2007.

## Historia 2007–2021

Antes: {'NO_CUADRA': 151, 'CUADRA_EXACTO': 8, 'APROXIMA': 13, 'AMBIGUA': 1}. Ahora: {'NO_CUADRA': 167, 'APROXIMA': 17, 'CUADRA_EXACTO': 11, 'AMBIGUA': 1}. Fijadas C: 0.
Mismo universo H002g: {'NO_CUADRA': 144, 'APROXIMA': 17, 'CUADRA_EXACTO': 11, 'AMBIGUA': 1}. Nuevas comparaciones: {'NO_CUADRA': 23}. De los 151 NO_CUADRA originales: {'NO_CUADRA': 140, 'APROXIMA': 6, 'CUADRA_EXACTO': 5}.
La unidad comparable con H002g es familia × año; períodos internos literales y semestre SIES están desglosados en los JSON. Perfil o plan ausente impide fijar.

| Año | Interno total ingreso | Interno familias mapeadas | SIES ingreso derivado | SIES primer año publicado |
|---|---:|---:|---:|---:|
| 2007 | 14 | 14 | 264 | 211 |
| 2008 | 28 | 28 | 246 | 224 |
| 2009 | 47 | 47 | 276 | 246 |
| 2010 | 70 | 70 | 310 | 256 |
| 2011 | 138 | 138 | 317 | 317 |
| 2012 | 228 | 227 | 331 | 276 |
| 2013 | 652 | 603 | 612 | 515 |
| 2014 | 522 | 501 | 446 | 369 |
| 2015 | 429 | 398 | 392 | 298 |
| 2016 | 411 | 378 | 370 | 274 |
| 2017 | 573 | 488 | 547 | 449 |
| 2018 | 505 | 429 | 431 | 315 |
| 2019 | 540 | 410 | 428 | 300 |
| 2020 | 536 | 463 | 418 | 265 |
| 2021 | 656 | 563 | 523 | 307 |

Causas probables E (no excluyentes, unidad familia-año): {'COBERTURA_INTERNA_NO_CERTIFICADA': 145, 'FAMILIA_SIN_EQUIVALENCIA_GOBERNADA': 22, 'POSIBLE_CAMBIO_PLAN_EXPEDIENTE_POSTERIOR': 16, 'SEGUNDO_SEMESTRE_OBSERVADO': 2}.
Cada NO_CUADRA conserva conteos de vía c, semestre 2 y expedientes posteriores; ninguna diferencia prueba por sí sola migración, corte o integridad del extracto.

## Repartos y candidatas

MU: {'PARCIAL': 13, 'NO_EXPLICADO': 13}. SIES: {'NO_EXPLICADO': 42, 'PARCIAL': 61, 'EXPLICADO_POR_FORMA_INGRESO': 2}.
Candidatas por familia/cohorte/forma (componentes, no grupos completos): {'SIES': {'CANDIDATA_LOCAL_SIN_EXCEPCIONES_OBSERVADAS': 5}, 'MU': {'CON_EXCEPCIONES_E': 25, 'CANDIDATA_LOCAL_SIN_EXCEPCIONES_OBSERVADAS': 34}}.
MU: los tramos unívocos sólo explican parte de repartos con excepciones; no hay grupo MU completamente explicado. SIES: las dos separaciones completas quedan como candidatas locales, sin plan UMAS ni activación.
Título técnico previo acreditado / no acreditado: {'SI': 224, 'NO_ACREDITADO_E': 8590, 'NO_COMPROBABLE_E': 0}. NO_ACREDITADO_E no significa que no exista título.
Gobernanza: gobernanza_for_ing_act.tsv de la raíz (el archivo de data/ es un puntero textual); control/config_for_ing_act.json y reporte de auditoría. Se conservan valores originales, sin derivar FOR nuevamente. Las descripciones 2026 no se convierten en normativa histórica.
EXPLICADO significa separación descriptiva sin excepciones dentro del grupo observado. SIES no incluye plan UMAS; sus grupos son familia/cohorte y no se enlazan a personas internas.

## Las veinte contradicciones

| Código | Causa principal | Planes observados (matrículas-año) | Repartos diagnosticados | Propuesta |
|---|---|---|---|---|
| I162S2C1J1V1 | SIN_EXPLICACION | {'IINF20241': 6} | {'PARCIAL': 2} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C1J1V2 | VARIOS_PLANES_UN_CODIGO | {'IECIRE20191': 2, 'IECIRE2020': 2, 'IECIRE20211': 13, 'IINF20241': 31} | {'PARCIAL': 2} | AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION |
| I162S2C1J2V1 | SIN_EXPLICACION | {'IINF20241': 7} | {'NO_EXPLICADO': 2, 'PARCIAL': 1} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C1J2V4 | SIN_EXPLICACION | {'IECIRE20191': 9, 'IECIRE2020': 11, 'IECIRE20211': 42, 'IINF20241': 31} | {'NO_EXPLICADO': 2, 'PARCIAL': 1} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C1J4V2 | SIN_EXPLICACION | {'CIINF20241': 70, 'IECIREOL': 8, 'IECIREOL20191': 15, 'IECIREOL20201': 21, 'IECIREOL20211': 329, 'IINF20241': 303, 'NINFREOL2019': 1} | {'PARCIAL': 2, 'NO_EXPLICADO': 2} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C1J4V3 | VARIOS_PLANES_UN_CODIGO | {'CIINF20241': 33, 'IINF20241': 1} | {'PARCIAL': 2} | AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION |
| I162S2C3J2V1 | VARIOS_PLANES_UN_CODIGO | {'ICRE20241': 3, 'IETMRE20121': 1, 'IETMRE20161': 1, 'IETMRE20211': 1} | {'NO_EXPLICADO': 1, 'PARCIAL': 1} | AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION |
| I162S2C3J2V4 | VARIOS_PLANES_UN_CODIGO | {'ICRE20241': 12, 'IETMRE20161': 1, 'IETMRE20191': 12, 'IETMRE20211': 74, 'NCONRE': 2, 'NITMRE20121': 1} | {'NO_EXPLICADO': 1, 'PARCIAL': 1} | AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION |
| I162S2C3J4V2 | SIN_EXPLICACION | {'CICRE20241': 130, 'ICRE20241': 259, 'IETMREOL': 1, 'IETMREOL20191': 26, 'IETMREOL20211': 424, 'NCONREOL2019': 7} | {'PARCIAL': 2, 'NO_EXPLICADO': 2} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C3J4V3 | SIN_EXPLICACION | {'CICRE20241': 43} | {'PARCIAL': 2} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C46J4V1 | VARIOS_PLANES_UN_CODIGO | {'CICIB20241': 41, 'IECSREOL20211': 1} | {'PARCIAL': 3} | AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION |
| I162S2C46J4V3 | VARIOS_PLANES_UN_CODIGO | {'CICIB20241': 98, 'ICIB20241': 294, 'IECSREOL20211': 340, 'NTCCREOL2020': 17} | {'PARCIAL': 3} | AMPLIAR_CANDIDATOS_PARA_REVISION_SIN_ASIGNAR_VERSION |
| I162S2C6J1V1 | SIN_EXPLICACION | {'TTMRE20211': 3} | {'NO_EXPLICADO': 2} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C6J1V2 | SIN_EXPLICACION | {'TTMRE20191': 2, 'TTMRE20211': 4} | {'NO_EXPLICADO': 2} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C6J2V1 | SIN_EXPLICACION | {'TCRE20241': 2, 'TTMRE20161': 1, 'TTMRE20211': 9} | {'NO_EXPLICADO': 3} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C6J2V2 | SIN_EXPLICACION | {'TCRE20241': 9, 'TTMRE20191': 19, 'TTMRE20211': 4} | {'NO_EXPLICADO': 3} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C76J4V1 | SIN_EXPLICACION | {'CIADM20241': 1, 'IADM20241': 87} | {'PARCIAL': 1} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C76J4V2 | SIN_EXPLICACION | {'CIADM20241': 15} | {'PARCIAL': 1} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C77J4V1 | SIN_EXPLICACION | {'CILOG20241': 3, 'ILOG20241': 67} | {'PARCIAL': 1} | MANTENER_PROVISIONAL; no corregir sin evidencia |
| I162S2C77J4V2 | SIN_EXPLICACION | {'CILOG20241': 14} | {'PARCIAL': 1} | MANTENER_PROVISIONAL; no corregir sin evidencia |

VERSION_POR_COHORTE no explica un reparto que ya está dentro de la misma cohorte. No hay causa CAMBIO_DE_PLAN ni POSIBLE_ERROR_DE_CARGA demostrada para adjudicarla a los códigos. Compartir código y repartir una cohorte son fenómenos distintos; el diagnóstico muestra ambos. No hay error de carga demostrado. No se aplica ninguna ampliación ni corrección.

Revisión: 4 lotes y 72 decisiones familia/problema. ADMP/CADMP sigue pendiente de Alexi.

## Trazabilidad y límites

FUENTES.json y MANIFEST.json fijan rutas y hashes. Los enlaces H002g se reutilizan íntegros, cotejados línea a línea con identidad/código/selección de la base MU; no se modifica su detalle privado. Los códigos y totales SIES originales no cambian. MRUN sólo en memoria; sin nacimiento ni enlace RUT–MRUN.
QA separado: hashes, sumas, reproducción byte a byte, pruebas y privacidad; fuentes, bases, denominadores, tasas y 24 cambios ajenos preservados.
