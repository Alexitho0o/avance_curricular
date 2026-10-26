# Fase 1 · Hito 2 — Universos y denominadores conservados

B/C — Se recuperó el padrón granular del original; V18 conserva sus totales mediante agregados. No se modificó ningún libro ni denominador.

| Año/grupo | Población | Base T2 | Base T3 | Numerador T2 | Numerador T3 | Unidad y alcance |
|---|---:|---:|---:|---:|---:|---|
| 2024/1 | 558 | 558 | 558 | 160 | 175 | B/C/E: posiciones personales de cohorte; proxy de actividad |
| 2025/1 | 1150 | 1150 | 1150 | 611 | 1023 | B/C: personas de cohorte; proxy T2 y foto T3 |
| 2025/2 | 222 | 222 | 222 | 200 | 202 | B/C: personas del archivo T2 |
| 2026/1 | 1471 | 1471 | 1467 | 1042 | 1360 | B/C/D: personas; 4 NO APLICA excluidos en T3 por regla interna heredada |
| 2026/2 | 527 | 528 | 527 | 462 | 467 | B/C/E: T2 matrículas, T3 personas; no homogeneizar |
| 2026/3 | 545 | None | 545 | None | 480 | B/C/E: personas de Base completa; no solo ingreso 2026-3 |

B/C — 558, 1150 y 1471 son las filas personales del grupo1 del original (rangos B6:V563, B564:V1713, B1714:V3184). No son la matrícula total anual. La base1467 solo corresponde a la tasaT3-2026 tras4NO APLICA, documentados como TITULADO/31 en el estudioV16.

B/C — 3179 orígenes ×2períodos=6358 posiciones. 2838 tienen contexto y3520 no. Hay2854 contextos porque16 son adicionales en posiciones con más de un expediente/plan. Ninguna de estas unidades se suma como nuevos estudiantes.

| Cohorte | Año observado | Período nativo | Posiciones | Con contexto | Sin contexto | Contextos | Extra |
|---|---|---|---:|---:|---:|---:|---:|
| 2024 | 2025 | 2 | 558 | 245 | 313 | 252 | 7 |
| 2024 | 2025 | 3 | 558 | 269 | 289 | 276 | 7 |
| 2025 | 2025 | 2 | 1150 | 542 | 608 | 542 | 0 |
| 2025 | 2025 | 3 | 1150 | 462 | 688 | 462 | 0 |
| 2026 | 2026 | 2 | 1471 | 682 | 789 | 683 | 1 |
| 2026 | 2026 | 3 | 1471 | 638 | 833 | 639 | 1 |

B/C/E — Las 6.358 posiciones usan período nativo 2/3, según calendario_explicito del estudio V13. No es una homologación acreditada al trimestre ni a la fecha exacta de cierre. Las 3.520 posiciones sin contexto no prueban falta de actividad.

## Descomposición del grupo 2026/3 conservado

B/C — La hoja Base del cierre T3-2026 contiene 557 matrículas y 545 personas. Las 545 identidades coinciden exactamente con el grupo 2026/3 de la hoja 20 original, sin exclusivos.

| Año/período de ingreso declarado | Matrículas | Personas distintas dentro del grupo |
|---|---:|---:|
| 2024/3 | 22 | 22 |
| 2025/3 | 34 | 34 |
| 2026/3 | 501 | 490 |

B/C — Una persona está en los grupos 2024/3 y 2026/3; por eso hay 546 pertenencias y 545 personas distintas en la unión. La hoja 2026_3 reproduce exactamente los 501 CODCLI de Base al filtrar ANOINGRESO=2026 y PERIODOINGRESO=3.

D/E — Se conservan los 545 aprobados. Los 490 verifican una diferencia de rotulado/alcance; no se proponen como sustitución automática del denominador. La decisión posterior es cómo describir el grupo completo ya utilizado.

## Alcance que falta confirmar

- E: 124 de ingreso 2025-T3 es el ejercicio anual separado: está en la fuente, pero no incorporado como grupo 3 del padrón intertrimestral actual. No añadir una fila ni sumarlo sin decisión.
- E: denominador 528 de T2-2026 es matrículas; población 527 es personas. Las 66 renuncias son agregadas. No confundir la tasa 462/528 con una tasa por personas.
- E: hoja 20 original no tiene CODCLI; 3.520 posiciones sin contexto diccionario no prueban deserción ni falta de matrícula. No inventar expedientes faltantes.
- E: cohorte 2024 se observa en 2025-2/3, mientras 2025 y 2026 se observan en su mismo año. La disponibilidad del padrón no acredita equivalencia de calendario ni cobertura del cierre.

## QA

C — PASS: padrón y grupos reproducidos, agregado V18 conserva conteos, orígenes T1 coinciden con las filas originales, identidades Base T3-2026 coinciden con grupo 3, hoja 2026_3 coincide con Base filtrada, ecuaciones 3.179×2=6.358; 2.838+3.520=6.358; 2.838+16=2.854; numeradores y poblaciones coinciden con las celdas guardadas de V18. Fuentes revalidadas por hash al terminar. Sin exportar identificadores ni modificar bases, denominadores o libros.

E — Este QA no acredita cobertura temporal completa, aceptación SIES ni recálculo integral/apertura en Excel nativo.

## Fuentes y reproducción

C — Ejecutar auditar_universos.py con el Python del runtime, en salida nueva. Solo exporta agregados; identifica fórmulas originales y valores materializados V18. RESULTADOS_UNIVERSOS.json contiene fuentes+hashes, rangos, conteos y fórmulas de control.

- B: `/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx` — `20fe8438cba065f15240f1e67c066e5feb8bac8841f182864e40ca7bc9512aa8` (libro derivado original con padrón granular).

- B: `/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx` — `2bd21ca31d391b59f4bd2c56d4876becd12aae05cb9673a7e069b5542ed66b01` (libro derivado agregado V18).

- B: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/seguimiento_t1_hasta_2026_20261023_v13/CONSULTA_CALENDARIO_AGREGADA.json` — `b887bd8d8202922b5e2b708134c657c9c0c9afdaa0ec05daeb29dcd8991e6dd3` (auditoría agregada).

- B: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/aclaracion_tasas_2026_20261023_v16/EVIDENCIA_AGREGADA.json` — `99a78d43ba1f51f318177ebaeab834029b9608aabbdef2262b5345a420ad5fee` (auditoría agregada).

- B: `/Users/alexi/.local/share/ipss/aplicacion_diccionario_intertrimestral_20261023_125556/ORIGENES_T1.json` — `9ba34a21ce89170f6343e068ba38ac1a546a927c1bd5ffcab9f4fd6ef48288a0` (padrón privado anterior).

- B: `/Users/alexi/.local/share/ipss/destinos_calendario_v7_20261023/RANURAS_POR_ORIGEN_PERIODO.json` — `2b6c4772818695af0d7473c9ed3998ebad6aba5c3f62fe7cce6559e4bab2f094` (posiciones privadas origen×período).

- B: `/Users/alexi/.local/share/ipss/destinos_calendario_v7_20261023/CONTEXTOS_POR_ORIGEN_PERIODO.json` — `82a12e4dbbd9d3ea751f2601d6b4a2f4ffe6485cb7c1f53268015169dba585ca` (contextos privados existentes).

- B: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/auditoria_diccionario_sies_20261025/fase3_20261025/ENTRADAS_EXCEL.json` — `cc55985deef50da4639aaec5fbf39d93798affca0ddba8501ada04d9e7dbf4eb` (auditoría agregada).

- B: `/Users/alexi/Downloads/cierre/Matrícula T2_2025 2.xlsx` — `ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3` (fuente institucional de cierre/ingresos).

- B: `/Users/alexi/Downloads/cierre/Matrícula T3_2025 2.xlsx` — `68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc` (fuente institucional de cierre/ingresos).

- B: `/Users/alexi/Downloads/cierre/Matrícula T_2_13_07_2026.xlsx` — `7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769` (fuente institucional de cierre/ingresos).

- B: `/Users/alexi/Downloads/cierre/Matrícula_T3_02_10_2026.xlsx` — `de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae` (fuente institucional de cierre/ingresos).
