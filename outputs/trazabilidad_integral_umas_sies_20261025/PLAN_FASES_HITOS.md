# Plan de trazabilidad integral fotos ↔ UMAS ↔ SIES ↔ MRUN · v2

Fecha: 30-10-2026. C: re-anclaje documental H007; D: alcance solicitado por Alexi. Estado: REANCLADO_CON_LIMITES_EXPLICITOS. Sin publicación nueva ni modificación del libro.

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
| 3: seguimiento | EJECUTADA_INSTANTANEA_V8; fase3/RESULTADOS_FASE3.json; H007 reexamina solo excepciones | V24 no se migra a v20: 1.135 posiciones tienen contexto actual, pero no se integró una vista nueva |
| 4: Excel | EJECUTADA; fase4/MANIFEST_FASE4.json y cadena V19–V24 | Artefacto privado; no datos personales en Git |
| 5: QA | EJECUTADA_EN_ALCANCE_DOCUMENTADO; fase5/INFORME_FASE5.md: V20, 77/77 casos; fase6_procedencia_v24/QA_MANIFEST_V24.json para nuevas columnas | No equivale a paridad cruda completa del indicador R19 ni QA nativo nuevo de V24 |
| 6: circuito reproducible y publicación | PENDIENTE | Requiere ejecución integral aislada con fuentes por hash, universos separados, consumidores y autorización de publicación |

La carpeta fase6_procedencia_v24 cierra una clasificación de procedencia, no la Fase 6 del plan. Se conserva su alcance y su evidencia sin renombrarla.

## Universos y reglas conservados

B/C: 3.179 orígenes, 6.358 posiciones, 2.854 contextos, 6.374 filas expandidas. T1-2026 = 1.471 en esta vista y denominador T3-2026 = 1.467 en R19: unidades/reglas distintas, ninguna reemplazada.

Cobertura del padrón, atribución de código y linaje completo son tres controles distintos. Un contexto nuevo en v20 no implica mismo expediente T1; un candidato de catálogo no implica correspondencia personal; ausencia de actividad no es deserción; cambio de jornada impide heredar código completo sin evidencia/decisión delimitada.

## H007 terminado y condiciones de reapertura

Hito 1: delta documental completo, sin recálculo. Hito 2: cada posición/contexto tiene causa observable o E con requisito; 0 nuevas herencias. Hito 3: totales agregados, sin vínculo personal y sin reabrir R09. Hito 4: 0 de 131 en H001 2024; 0,00 pp por inclusión (C), brecha causal E conservada.

No abrir otra iteración con estas mismas fuentes. Reanudar solo con evidencia del período/corte o del expediente que satisfaga el requisito publicado, fuente individual SIES para la brecha, o autorización explícita para integrar la vista v20 y ejecutar la Fase 6. Reutilizar MAPA_RESULTADOS_GOBERNADOS antes de calcular. Sin commit ni push en H007.
