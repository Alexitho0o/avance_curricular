# Plan de trazabilidad integral fotos ↔ UMAS ↔ SIES ↔ MRUN · v3

Fecha: 30-10-2026. C: re-anclaje documental H007; D: alcance solicitado por Alexi. Estado: REANCLADO_CON_LIMITES_EXPLICITOS. H008 genera V25 candidata; sin publicación y sin modificar V24.

## Versión conservada

La v1 íntegra está en PLAN_FASES_HITOS_v1_20261025.md; SHA-256 `8031e4a3c0003bc98ea2e0e13d17137646da1639cb858e202655bdd56fc603d7`. MANIFEST_PLAN.json permanece como manifiesto histórico v1 y no acredita este documento v2. El manifiesto v2 está en h007_20261030/MANIFEST_H007.json. DELTA_H007.md explica cada sustitución, con evidencia.

## Fuentes que gobiernan ahora

- Diccionario activo: v20, mediante data/diccionario_sies_seguimiento/activo.json. El descriptor histórico llamado candidata está ACTIVA. No se crea otra edición.
- H002: catálogo 2027 y regla MU2027 ACTIVA. Los antiguos conservan su código; los nuevos usan la oferta y el tipo de plan según su alcance. No es una adjudicación retrospectiva a personas.
- TIPO_PLAN v2 y coherencia R21: distinguir tipo correcto, cruce de tipo y no evaluable. El v3 de H002m es candidato y no reemplaza v2.
- R18: historia 2007–2021 cerrada con causa E; fuente oficial SIES por estudiante/código. No reconstruir historia desde una foto actual de expedientes.
- R10: registro SIES por estudiante 2007–2025 cuadra por registros con la publicación. MRUN se usa solo agregado, nunca como puente con identidades UMAS.
- R19: intertrimestral BORRADOR_NO_ACTIVO, paridad parcial. R20: entrega H003/H006, resultado ejecutivo sin sustituir fuentes privadas. No mezclar unidades.
- R25: H007, excepciones V24 y agregados nuevos delimitados, sin modificar R01–R24.

## Estado real de las fases

| Fase del plan | Estado y evidencia | Qué no acredita / siguiente puerta |
|---|---|---|
| 1: inventario y padrón | EJECUTADA_CON_LIMITES; fase1/CADENA_Y_FUENTES.json y QA_FASE1.json | Universo congelado, no código universalmente atribuido |
| 2: ancla anual | EJECUTADA_CON_LIMITES; fase2/INFORME_FASE2.md; R07–R10 actualizan cierre | Igualdad agregada no prueba aceptación individual; brecha 2026 cerrada con causa E |
| 3: seguimiento | EJECUTADA_INSTANTANEA_V8; fase3/RESULTADOS_FASE3.json; H007 reexamina solo excepciones | H008 integra 1135 posiciones C1 como respaldo v20 en V25; no adjudica código ni acredita expediente T1 |
| 4: Excel | V19–V24 ejecutadas; V25 CANDIDATA_CON_LIMITES, h008_20261030/INFORME_H008.md | Artefacto privado; no datos personales en Git |
| 5: QA | H008 PARCIAL: recálculo y preservación PASS; 77 escenarios nativos pendientes. Antecedente EJECUTADA_EN_ALCANCE_DOCUMENTADO; fase5/INFORME_FASE5.md: V20, 77/77 casos; fase6_procedencia_v24/QA_MANIFEST_V24.json para nuevas columnas | No equivale a paridad cruda completa del indicador R19 ni QA nativo nuevo de V24 |
| 6: circuito reproducible y publicación | PARCIAL; INTEGRAL PENDIENTE | Requiere ejecución integral aislada con fuentes por hash, universos separados, consumidores y autorización de publicación |

La carpeta fase6_procedencia_v24 cierra una clasificación de procedencia, no la Fase 6 del plan. Se conserva su alcance y su evidencia sin renombrarla.

## Universos y reglas conservados

B/C: 3.179 orígenes, 6.358 posiciones, 2.854 contextos, 6.374 filas expandidas. T1-2026 = 1.471 en esta vista y denominador T3-2026 = 1.467 en R19: unidades/reglas distintas, ninguna reemplazada.

Cobertura del padrón, atribución de código y linaje completo son tres controles distintos. Un contexto nuevo en v20 no implica mismo expediente T1; un candidato de catálogo no implica correspondencia personal; ausencia de actividad no es deserción; cambio de jornada impide heredar código completo sin evidencia/decisión delimitada.

## H007 terminado y condiciones de reapertura

Hito 1: delta documental completo, sin recálculo. Hito 2: cada posición/contexto tiene causa observable o E con requisito; 0 nuevas herencias. Hito 3: totales agregados, sin vínculo personal y sin reabrir R09. Hito 4: 0 de 131 en H001 2024; 0,00 pp por inclusión (C), brecha causal E conservada.

No abrir otra iteración con estas mismas fuentes. Reanudar solo con evidencia del período/corte o del expediente que satisfaga el requisito publicado, fuente individual SIES para la brecha, o autorización explícita para integrar la vista v20 y ejecutar la Fase 6. Reutilizar MAPA_RESULTADOS_GOBERNADOS antes de calcular. Sin commit ni push en H007.

## H008 · estado v3

V2 íntegra: PLAN_FASES_HITOS_v2_20261030.md, SHA-256 `6ec8b1f67bcd9cfe44c7fd156fe2095734a760e64efdf9481987e2cf0cdff0a6`.

H1 inventario cerrado: 681 C4 con foto disponible y 733 parciales T2-2025. D Alexi: cierre académico 2/3 sin exigir fecha exacta. H2 V25 candidata: 1135 posiciones/1136 contextos, fotos como respaldo separado, 6740 resultados nativos sin diferencias; falta certificar 77 escenarios nativos. H3 propuesta99 lista sin aplicar. H4 sin nueva fuente MRUN, R09 cerrado. H5 ensamblado incremental idéntico; no reproduce R19 crudo integral. R26 candidata, R19 borrador.

Comando e insumos: h008_20261030/REPRODUCIR.md, FUENTES_H008.json y FUENTES_FOTOS_H008.json. No abrir otra iteración de atribución con las mismas fuentes. Pendientes exactos y paradas en INFORME_H008.md. Sin commit ni push.
