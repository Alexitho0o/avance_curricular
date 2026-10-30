# H013 · v21 activa

D · Alexi, 30-10-2026. Se acepta el riesgo de D7 con 956 aciertos, 1 error y 233 abstenciones (99,8955 % sobre 957 predicciones). El caso fue IECIREOL20201 en 2021. Se predijo V1 y la MU informó V2 en la misma familia C1J4. Al conservar todos los documentales se observan diez personas en V1 y una en V2. Cuando se ocultó esa persona, las diez referencias restantes eran unánimes. La correspondencia interna conserva su nivel y no acredita documentalmente al contexto.

La referencia de D7 prioriza mismo plan y año. En ausencia de documentales busca primero el T1 posterior y luego el anterior. Un año con evidencia mixta o insuficiente queda E. Se exigen tres personas distintas y presencia del código en la oferta del año. Las 23 altas esperadas se verificaron (13 TTMREOL20211 y 10 IETMREOL20211, año 2021). La extensión resuelve 15 de 41 descalces. DESCALCES_41.md contiene oferta, niveles, duración derivada, referencia MU y lectura por plan/año. IIND20251 conserva 24 E.

## Cobertura final

2.990 de 3.049 contextos respaldados y 59 E (1,94 %). Las 99 posiciones conservan sus 99 respaldos. A continuación se cuentan contextos o posiciones, sin sumar entre columnas.

| Nivel | 3.049 contextos | 99 posiciones |
|---|---|---|
| ARRASTRE_ULTIMO_T1 | 56 | 0 |
| CAMBIO_PLAN_ANTES_DE_T1_CATALOGO | 38 | 2 |
| CAMBIO_PLAN_SEDE_CATALOGO_D3 | 70 | 7 |
| DOCUMENTAL_T1 | 7 | 0 |
| E | 59 | 0 |
| FAMILIA_CORREGIDA_CANDIDATA | 80 | 0 |
| HERENCIA_T1_MISMO_AÑO | 20 | 0 |
| INGRESO_2026_NO_INFORMADO | 840 | 21 |
| MU2027 | 19 | 8 |
| NUNCA_INFORMADO | 479 | 10 |
| NUNCA_INFORMADO_EN_FUENTES | 248 | 4 |
| PRIMER_T1_POSTERIOR | 1095 | 47 |
| VERSION_POR_MU_DEL_PLAN | 38 | 0 |

## Recálculo institucional

| Indicador | Numerador | Denominador | Tasa % | Diferencia pp |
|---|---|---|---|---|
| H001_2022 | 224 | 305 | 73,44 | 0,00 |
| H001_2023 | 258 | 366 | 70,49 | 0,00 |
| H001_2024 | 326 | 558 | 58,42 | 0,00 |
| H001_2025 | 668 | 1150 | 58,09 | 0,00 |
| R19_INGRESO_T2 | 462 | 528 | 87,50 | 0,00 |
| R19_T1_T3 | 1360 | 1467 | 92,71 | 0,00 |
| R19_TOTAL_T3 | 2290 | 2519 | 90,91 | 0,00 |

QA_ACTIVACION.json conserva los controles con el puntero v20, con el puntero v21 aislado y con el puntero v21 real. H001 se recalculó sobre su MU congelada y el catálogo de carreras. R19 se recalculó con los indicadores de la foto V24 aprobada. Se reagruparon numeradores y denominadores por los códigos de cada puntero, conservando los casos sin contexto y múltiples. El ingreso T2 usa matrículas menos renuncias sobre el total por área. Su fuente no contiene clave individual para asociar código de contexto. R19 conserva el estado BORRADOR.

## Activación y contrato

Descriptor activo `data/diccionario_sies_seguimiento/v21_20261030_h013/descriptor.json`, SHA-256 `4f6530860a529fbc39ca5c607ecbf14498c0c74de0c14e2c5d4be7f092ab64be`. El puntero v20 archivado conserva todos sus hashes. La base nueva incluye las tablas MU y una copia íntegra de cada fila de observaciones v20 en observaciones_archivo_v20. La proyección observaciones entrega el código documental únicamente para DOCUMENTAL_T1 y el código interno para adjudicaciones D. La tabla asignaciones_v21 contiene nivel, regla, año fuente, evidencia, clase y código. El consumidor devuelve esos campos en evidencia. El año de referencia de D7 es del plan, sin implicar T1 propio de la persona. La capa PROMEDIOS conserva sus bytes privados y sus claves de observación, con metadatos vinculados al SHA-256 de v21.

Las tres interfaces de consulta se probaron con 78 contextos por interfaz, seis por nivel, y con capa PROMEDIOS disponible. MU2027 evaluó 4.105 filas de antiguos. H001 y R19 usan sus bases aprobadas para la población y el resultado. H002 consulta un catálogo histórico fijado a v20. En el primer ensayo, la comprobación del hash del puntero histórico detectó el cambio y se restauró v20. La lectura de H002 se dirigió a la copia archivada, con el mismo hash exigido por FUENTES.json. Pasaron 11 pruebas de paridad y 27 de MU2027.

## Residual

| Motivo | Contextos | Requisito |
|---|---|---|
| CODIGO_MU_PLAN_AUSENTE_OFERTA_ANUAL | 24 | Acreditar oferta aceptada del año del contexto y versión efectivamente informada. Para IIND20251 confirmar V2 en 2025 o documentar su ausencia. |
| MU_PLAN_MENOS_DE_TRES_PERSONAS | 2 | Aportar T1 documental atribuible al expediente y plan, o referencia unánime suficiente del año aplicable. |
| MU_PLAN_NO_UNANIME | 8 | Distinguir versiones por expediente y plan con evidencia anual individual en carpeta restringida. |
| PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO | 6 | Calendario UMAS y definición de los períodos 4/5 por año y régimen semestral/trimestral. |
| PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS | 6 | Primera matrícula del expediente/plan con fecha, sede y jornada efectiva del cambio. |
| SIN_CODIGO_ANUAL_COMPATIBLE | 2 | Equivalencia formal de plan y versión del año con sede, jornada y duración. |
| SIN_FAMILIA_H002_U_OFERTA_ANUAL | 6 | Acreditar familia o existencia del código en la oferta del año. |
| T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO | 5 | Documento que concilie el código del T1 con la oferta y el perfil del año del contexto. |

SOLICITUD_UMAS_RESIDUAL.md es un borrador. La reproducción aislada produjo la misma base SQLite y las mismas asignaciones privadas. Antes de publicar se escanearon únicamente archivos agregados y de código. Ningún libro ni detalle individual forma parte de este respaldo.
