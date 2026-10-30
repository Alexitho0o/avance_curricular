# H015 · fuentes internas, foto T2-2025 y residual de v22

**CANDIDATA · Fase 1.** La unidad de la foto es una posición del padrón de seguimiento. La unidad del diccionario es un contexto.

## Inventario (B/C)

117 archivos con SHA-256, incluidos 113 en las categorías 01–12, la ampliación 13 y tres archivos de raíz. Ver INVENTARIO_FUENTES_H015.md e INVENTARIO.json. H008 sí referenció archivos consolidados, pero no inventarió la carpeta completa. MAT_IP_CIISA_2021.xlsx, 2025-2.xlsx y los dos libros de intake no tienen uso acreditado por hash en H007–H014. La MU aporta filas individuales de 2021. Los tres libros de intake sirven de contraste sin acreditar el cierre completo de T2.

## Foto (D/B/C/E)

Alexi acepta PROMEDIOS como fuente de actividad del período. Para estado prevalece una foto DA con corte acreditado. FOTO_T2_2025.md y .json documentan cada extracto y las diferencias.

| Cohorte | Padrón | Con foto | C4 | C4 con foto | C4 vigentes | C4 no vigentes | C4 en conflicto | C4 sin foto |
|---|---|---|---|---|---|---|---|---|
| 2024 | 558 | 308 | 282 | 39 | 37 | 0 | 2 | 243 |
| 2025 | 1150 | 724 | 451 | 33 | 30 | 1 | 2 | 418 |

PROMEDIOS respalda las 72 posiciones C4; una también figura en la foto parcial H008. En el padrón completo, la foto parcial coincide con PROMEDIOS en dos posiciones y difiere o presenta estados múltiples en otras dos. Quedan 118 estados en conflicto en la cohorte 2024 y 80 en 2025. Las 661 C4 sin foto quedan E. La ausencia no acredita salida ni inactividad.

## Contextos (B/C/D/E)

Cuatro contextos de dos expedientes pasan a respaldados en el ensayo por MAT_IP_CIISA_2021.xlsx, el plan observado y el expediente. v22 sigue en 2.990/3.049 y 99/99. v23 candidata alcanza 2.994/3.049 y 99/99. Ver RESIDUAL_59.json y QA_CANDIDATA.json.

| Plan | Año | Período | Nivel | Código | Contextos |
|---|---|---|---|---|---|
| IECIREOL20201 | 2021 | 1 | DOCUMENTAL_T1 | I162S2C1J4V1 | 1 |
| IECIREOL20201 | 2021 | 3 | HERENCIA_T1_MISMO_AÑO | I162S2C1J4V1 | 1 |
| IECIREOL20201 | 2021 | 4 | HERENCIA_T1_MISMO_AÑO | I162S2C1J4V1 | 1 |
| NTCCREOL2020 | 2020 | 4 | PRIMER_T1_POSTERIOR | I162S2C46J4V2 | 1 |

| Motivo residual | Contextos | Requisito |
|---|---|---|
| MU_PLAN_MENOS_DE_TRES_PERSONAS | 1 | Tres personas documentales del mismo plan/año. |
| MU_PLAN_NO_UNANIME | 5 | Evidencia que discrimine las versiones documentadas. |
| NUNCA_INFORMADO_PENDIENTE_DECISION_FASE_3 | 25 | Decisión de Fase 3; sin asignación por referencia grupal. |
| PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO | 6 | Acreditar régimen y período del plan. |
| PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS | 6 | Primer T1 único del expediente con sede y jornada compatibles. |
| SIN_CODIGO_ANUAL_COMPATIBLE | 2 | Un código del año compatible en oferta. |
| SIN_FAMILIA_H002_U_OFERTA_ANUAL | 6 | Correspondencia de familia y oferta anual acreditadas. |
| SIN_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN | 3 | T1 individual del mismo expediente y plan. |
| TIPO_O_DURACION_NO_COINCIDE | 1 | Perfil compatible o referencia documental bajo D7 extendida. |

Los 25 NUNCA_INFORMADO quedan sin código hasta Fase 3: 24 IIND20251 y uno IECIRE20121. La etiqueta se limita a las fuentes examinadas. Los demás requieren evidencia individual del mismo expediente y plan, un perfil compatible, régimen acreditado o referencia documental suficiente y unánime según el motivo.

## Control de indicadores (C)

| Control | Numerador | Denominador | Diferencia v22/ensayo v23 (pp) |
|---|---|---|---|
| H001_2022 | 224 | 305 | 0,00 |
| H001_2023 | 258 | 366 | 0,00 |
| H001_2024 | 326 | 558 | 0,00 |
| H001_2025 | 668 | 1150 | 0,00 |
| R19_INGRESO_T2 | 462 | 528 | 0,00 |
| R19_T1_T3 | 1360 | 1467 | 0,00 |
| R19_TOTAL_T3 | 2290 | 2519 | 0,00 |

El ensayo usa una copia privada y un puntero aislado. La foto candidata no sustituye las banderas de R19. Orden de reproducción: inventario.py, extraer.py, perfilar.py, foto.py, residual.py, candidata.py y cerrar.py.
