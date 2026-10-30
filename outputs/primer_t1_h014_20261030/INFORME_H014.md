# H014 · v22 activa

**D · Alexi, 30-10-2026.** En PRIMER_T1_POSTERIOR el año de oferta que valida el código es el año de ese primer T1. Exigir el mismo expediente y plan, sede, jornada, tipo y duración total coherentes. Sólo esa vía usa la marca OFERTA_AÑO_T1. Las atribuciones anteriores se conservaron sin reclasificación.

**B/C.** De los 59 contextos E revisados, cero cumplieron D10. El universo queda en 2.990/3.049 contextos respaldados y 99/99 posiciones. Los 24 IIND20251 sin línea individual MU en 2026 no pueden usar por esta vía la referencia grupal de 83 personas en I162S2C87J4V2. En los otros cinco casos, tres IECSREOL20211 carecen de primer T1 posterior atribuible en las fuentes y dos tienen un T1 en 2022 que falla el control de perfil. NCONREOL2019 tiene continuidad de cuatro semestres frente a C3J4V2 regular de ocho. NTCCREOL2020 tiene continuidad de cinco semestres frente a C46J4V3 regular de ocho. CONTROL_CASOS_ESPERADOS.json conserva año, código, perfil y conteos. No se atribuye la referencia de otra persona.

## Residual E

| Motivo vigente | Contextos | Requisito actual |
|---|---|---|
| MU_PLAN_MENOS_DE_TRES_PERSONAS | 2 | Referencia documental unánime de al menos tres personas o primer T1 propio acreditado. |
| MU_PLAN_NO_UNANIME | 8 | Documento del expediente que distinga las versiones observadas del plan. |
| PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO | 6 | Calendario UMAS que defina 4/5 para los tres contextos semestrales y tres trimestrales. |
| PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS | 6 | T1 único del expediente/plan con sede y jornada efectivas del cambio. |
| SIN_CODIGO_ANUAL_COMPATIBLE | 2 | Equivalencia formal del plan, sede, jornada y duración con la versión de oferta. |
| SIN_FAMILIA_H002_U_OFERTA_ANUAL | 6 | Evidencia anual que identifique familia y código ofertado. |
| SIN_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN | 27 | Aportar el primer T1 individual del mismo expediente y plan. Incluye 24 IIND20251 sin fila MU 2026 y tres IECSREOL20211 sin T1 posterior localizado. |
| TIPO_O_DURACION_NO_COINCIDE | 2 | Conciliar la versión regular de ocho semestres informada en 2022 con el plan de continuidad de cuatro semestres de NCONREOL2019 o cinco de NTCCREOL2020. |

## Control del puntero real

| Indicador | Numerador | Denominador | Diferencia (pp) |
|---|---|---|---|
| H001_2022 | 224 | 305 | 0,00 |
| H001_2023 | 258 | 366 | 0,00 |
| H001_2024 | 326 | 558 | 0,00 |
| H001_2025 | 668 | 1150 | 0,00 |
| R19_INGRESO_T2 | 462 | 528 | 0,00 |
| R19_T1_T3 | 1360 | 1467 | 0,00 |
| R19_TOTAL_T3 | 2290 | 2519 | 0,00 |

H001 se recalculó sobre su MU y catálogo gobernados. R19 usa las banderas de la foto aprobada. Los totales se reagruparon por contexto de cada puntero, incluyendo los casos sin enlace y con múltiples contextos. El ingreso T2 usa la fuente de matrículas y renuncias agregadas por área. QA_ACTIVACION.json compara v21, el ensayo aislado v22 y el puntero v22 real.

Las tres interfaces coincidieron en 78 consultas cada una. MU2027 probó 4.105 antiguos. Pasaron las pruebas de paridad H002 y MU2027. Se reprodujeron las asignaciones, base SQLite y salidas agregadas por hash antes de activar. Reproducción: ejecutar construir_v22.py con v21 activa, luego activar_v22.py y cerrar_h014.py. El constructor protege la base activa contra sobrescritura.

El puntero activo selecciona `data/diccionario_sies_seguimiento/v22_20261030_h014/descriptor.json` con SHA-256 `40958a9c3ff9b878072656ac6bce2f69dc35beca02a2aacd34d14c16788734f9`. La capa PROMEDIOS conserva sus bytes. La base v22, sus asignaciones privadas y la tabla asignaciones_v22 materializan esta edición. Las bases v20 y v21 se verificaron por sus hashes originales.
