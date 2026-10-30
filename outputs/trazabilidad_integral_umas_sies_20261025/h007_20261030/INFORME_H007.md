# H007 · Re-anclaje de trazabilidad integral

Estado: **REANCLADO_CON_LIMITES_EXPLICITOS**. C: consultas acotadas; B: evidencias observadas; D: decisiones previas conservadas; E: causas no acreditadas. Fecha 30-10-2026. Sin commit, push, adjudicación, recálculo de tasas ni modificación del libro.

## Hito 1 · Delta documental

DELTA_H007.md contiene 11 contrastes con R01–R24, con ruta y hash. V8 es una instantánea histórica; el activo es v20. H002 y la regla MU2027 gobiernan catálogo/carga 2027, sin atribuir retrospectivamente expedientes. R19 sigue borrador; R20 es la entrega ejecutiva, no una nueva base. El registro SIES cuadra por filas con publicación según R10; MRUN distintos es otra unidad. Parada documental cumplida sin recalcular estos resultados.

## Hito 2a · 3.520 posiciones sin contexto

B/C: el universo se conserva: 3.179 orígenes, 6.358 posiciones, 2.854 contextos en 2.838 posiciones. Las filas expandidas de V24 son 6.374; no son un denominador de personas. Fuente: fase3/RESULTADOS_FASE3.json y fase6_procedencia_v24/QA_MANIFEST_V24.json.

La consulta por persona/año/período encuentra contexto v20 en 1.135 posiciones que estaban vacías en v8; no afirma mismo expediente T1 ni matrícula vigente. Estas posiciones tienen prioridad en la siguiente partición. Las otras 2.385 siguen sin contexto. Para ellas se conserva la observación de la foto de ingreso de V24 recalculada, separada de la causa no probada de falta de actividad.

| cohorte_T1 | año_observado | período_nativo | C1 | C2 | C3 | C4 | C5 | C6 | total |
|---|---|---|---|---|---|---|---|---|---|
| 2024 | 2025 | 2 | 31 | 0 | 0 | 282 | 0 | 0 | 313 |
| 2024 | 2025 | 3 | 28 | 0 | 0 | 261 | 0 | 0 | 289 |
| 2025 | 2025 | 2 | 157 | 0 | 0 | 451 | 0 | 0 | 608 |
| 2025 | 2025 | 3 | 129 | 90 | 435 | 0 | 34 | 0 | 688 |
| 2026 | 2026 | 2 | 369 | 0 | 0 | 420 | 0 | 0 | 789 |
| 2026 | 2026 | 3 | 421 | 107 | 301 | 0 | 0 | 4 | 833 |

| Causa observable / clase | Total | Requisito o límite |
|---|---:|---|
| C1: CONTEXTO_PRESENTE_EN_V20_AUSENTE_EN_INSTANTANEA_V8 (B/C) | 1135 | Integrar una nueva vista con autorización; V24 conserva v8. Contexto de la misma persona/año/período, no prueba de mismo expediente T1 ni vigencia. |
| C2: FOTO_INGRESO_VIG0_SIN_CONTEXTO_DE_ACTIVIDAD (B/E) | 197 | Causa académica/administrativa y cobertura del período; VIG 0 observado no prueba abandono ni explica por sí solo la ausencia de actividad. |
| C3: FOTO_INGRESO_VIG1_SIN_CONTEXTO_DE_ACTIVIDAD (B/E) | 736 | Actividad/expediente del período con identidad y calendario acreditados; VIG 1 no aporta un contexto PROMEDIOS. |
| C4: FOTO_NO_COMPLETA_Y_SIN_CONTEXTO (E) | 1414 | Foto completa del mismo corte y correspondencia del período nativo con el trimestre; no clasificable como no matriculado ni falla de llave. |
| C5: MATRICULA_DE_INGRESO_NO_LOCALIZADA_EN_FOTO (B/E) | 34 | Expediente de ingreso en corte y revisión de selección/llave; no significa que la persona carezca de otra matrícula. |
| C6: NO_APLICA_EN_FOTO_SIN_CONTEXTO (B/E) | 4 | Conservar exclusión temporal de la foto; no retirar la posición de V24 ni certificar ausencia de actividad. |

La foto de origen no coincide automáticamente con el año observado: los orígenes 2024 se siguen en 2025. Los períodos nativos 2/3 son las ranuras heredadas; no se convierten a fechas de trimestre. T2 sin foto completa queda E; no se inventa una ausencia de matrícula. Tampoco se atribuye a truncamiento o falla de llave sin evidencia específica. La llave fila del padrón/documento/año se verificó en las 3.520 posiciones; no se observó discrepancia en ese vínculo. Esto no certifica las llaves internas de cada fuente.

Detalle agregado y foto sin prioridad: POSICIONES_SIN_CONTEXTO.json. Detalle por posición únicamente en ~/.local/share/ipss/h007_20261030/. Cada posición tiene causa observable o requisito E. No se abre otra iteración.

## Hito 2b · Los 99 contextos

C/E: 95 candidatos únicos de catálogo y 4 múltiples; **0 pasan a respaldados personales y 99 continúan pendientes**. La aprobación del catálogo no acredita identidad, continuidad ni código del período.

| motivo_v24 | estado | n |
|---|---|---|
| JORNADA_DISTINTA | CATALOGO_CANDIDATO_UNICO_NO_ATRIBUCION | 63 |
| SIN_ENLACE_EXPEDIENTE_T1 | CATALOGO_CANDIDATO_UNICO_NO_ATRIBUCION | 32 |
| SIN_ENLACE_EXPEDIENTE_T1 | CATALOGO_MULTIPLE_E | 4 |

Los 63 con jornada distinta no admiten heredar el código T1 completo. De los 36 restantes, 32 tienen un candidato de catálogo y cuatro IINF20241 tienen alternativas V1/V2 en J1 o V1/V4 en J2. CASOS_99.md abre las combinaciones por año, período, plan, código, tipo y requisito. No se aplicó ninguna herencia ni se consultó v20 para adjudicar este conjunto. La coherencia R21 permite revisar el tipo, pero no corregir un código individual histórico por ese solo criterio.

## Hito 3 · MRUN, agregado comparable por nivel

B/C. MRUN se cuenta solo en memoria por año+código completo; MU usa las personas y selección ya congeladas de H002g. Es la foto MU anual, no la población de ingreso T1 de V24 ni Datos Alumnos actuales. Observado − referencia.

| anio | nivel | referencia | observado | diferencia | cero | distinta | sin_par |
|---|---|---|---|---|---|---|---|
| 2022 | Pregrado | 1033 | 1033 | 0 | 26 | 0 | 0 |
| 2023 | Pregrado | 1142 | 1142 | 0 | 19 | 2 | 0 |
| 2024 | Pregrado | 1455 | 1455 | 0 | 27 | 0 | 0 |
| 2025 | Pregrado | 2371 | 2371 | 0 | 43 | 0 | 0 |
| 2026 | Pregrado | 3371 | 3145 | -226 | 15 | 46 | 2 |

Los códigos sin par en 2026 son C77J1V1 (1 SIES) y C87J4V1 (5 SIES). Los dos desacuerdos de 2023 son C46J1V1 (+1) y C46J4V3 (−1); se compensan en el total y se mantienen visibles. Hay códigos solo en MU con selección cero: uno en 2022 y cinco en 2024; no se convierten en matrícula SIES faltante.

Postítulos SIES: 19 en 2023, 13 en 2024, 151 en 2025 y 54 en 2026, sin par en la selección MU pregrado. No se suman a la brecha de pregrado. Ningún duplicado de MRUN dentro de código/año en estas fuentes (diferencia registros−personas-código = 0). MRUN_POR_CODIGO.md y MRUN_AGREGADO.json contienen todos los códigos, incluidos los sin par.

Conclusión (tres líneas): 2022, 2024 y 2025 cuadran en pregrado por código; 2023 conserva dos diferencias compensadas.
2026 conserva el observado−referencia de −226 y dos códigos publicados sin par, sin identificar personas ni explicar la causa.
R09 sigue CERRADA_DOCUMENTADA, causa E: un agregado MRUN no habilita reconstruir identidades ni reabrir esa investigación.

## Hito 4 · Prueba acotada de los 131

C: se reutilizaron los 131 de COHERENCIA_TIPO_H005C (CICRE 59, CICIB 44, CIINF 28), el detalle congelado H002g y la cohorte ya calculada de hoja 9 en la copia gobernada de V24. Se verificó que los 558 elegibles existen en MU 2024 con la misma llave completa; 326 retenidos, sin reproducir el motor H001. Los 131 son personas distintas en este conjunto.

**Intersección con H001 2024: 0 de 131; aporte por inclusión en esa cohorte: 0,00 pp (C).** De los 131, 80 tienen origen 1900/semestre 0 (sin dato válido) y 51 origen anterior a 2024. H001 exige origen del año de cohorte; ingreso a la carrera actual no lo sustituye. El cambio de código regular/continuidad no los incluye en ese denominador. No se identifica una causa nueva de la brecha −9,08 pp (E).

ESCENARIO_131_H001.json conserva el desglose por plan, código, origen y resultado. El escenario de exclusión no cambia nada (558 casos y 326 retenidos); no se cambia ni la tasa interna ni la oficial.

## Pendientes y parada

- E: las 2.385 posiciones aún sin contexto requieren cobertura del período y/o foto completa, según la tabla; no se les atribuye abandono.
- E/D: los 99 requieren código contextual o autorización de adjudicación delimitada; la tabla H002 por sí sola no basta.
- E: atribuir causalmente la brecha H001 exige evidencia adicional, no inferencia por coherencia de tipos. La prueba de inclusión se cierra en 0.
- E: Fase 6 del plan —reproducción integral y publicación— sigue pendiente. La clasificación de procedencia de V24 no la cierra.

No se generó Excel. Fuentes y hashes: FUENTES_H007.json; QA y preservación: QA_H007.json; trazabilidad de salidas: MANIFEST_H007.json. R25 registra este resultado y sus condiciones de reapertura.

## Mensaje de commit preparado (no ejecutado)

`H007 reancla trazabilidad fotos–UMAS–SIES–MRUN, explica pendientes V24 y conserva límites`

## Archivos tocados

Modificados: `docs/MAPA_RESULTADOS_GOBERNADOS.md`, `docs/MAPA_RESULTADOS_GOBERNADOS.json` y `outputs/trazabilidad_integral_umas_sies_20261025/PLAN_FASES_HITOS.md`.

Nuevos en la carpeta del plan: `DELTA_H007.md` y `PLAN_FASES_HITOS_v1_20261025.md` (copia íntegra).

Nuevos en `h007_20261030/`:

- `reanclar.py`
- `documentar.py`
- `qa_h007.py`
- `POSICIONES_SIN_CONTEXTO.json`
- `REEVALUACION_99.json`
- `CASOS_99.md`
- `MRUN_AGREGADO.json`
- `MRUN_POR_CODIGO.md`
- `ESCENARIO_131_H001.json`
- `FUENTES_H007.json`
- `INFORME_H007.md`
- `QA_H007.json`
- `MANIFEST_H007.json`

Intermedios privados: registro inicial de preservación, POSICIONES_3520.json y PENDIENTES_99.json en ~/.local/share/ipss/h007_20261030/. No forman parte de una futura lista Git.

