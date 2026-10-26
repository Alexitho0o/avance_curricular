# Conciliación multiversión T1 · V5 vs. vista gobernada (25-10-2026)

**C — Qué hace.** `reproducir.py` lee la vista privada de Fase 3 (diccionario v8) y la tabla
«Revisión de planes con varias versiones» de la hoja 2_Catalogo_UMAS del Excel V5. Verifica
hashes antes de calcular y escribe solo agregados por plan. No modifica fuentes, diccionario,
Excel ni denominadores. Sin commit/push.

**B/C — Resultado.** Las dos cifras miden cosas distintas sobre los mismos 2.854 contextos:

| Medida | Concordantes | No concordantes | Qué cuenta |
|---|---:|---:|---|
| Diccionario v8 (Fase 3) | 2.755 con código | 99 E | Contextos sin código SIES aplicable |
| Ancla T1, regla uniforme (T1+carrera+sede+jornada+plan) | 2.705 | 149 | Contextos con alguna excepción respecto del ancla T1; = 149 excepciones de Fase 3 |
| V5 publicado | 2.711 | 143 | Igual que la regla uniforme, salvo IINF20241 |

**C — Puente exacto.** 143 = 99 pendientes E + 50 excepciones con código respaldado − 6
cambios solo de versión que V5 aceptó como concordantes en IINF20241.

**E — Inconsistencia.** V5 declara para IINF20241 la misma regla que para los demás planes
(«+ plan»), pero su cifra (414) solo se reproduce aceptando cambios documentados de versión.
Con la regla declarada, IINF tiene 408 concordantes y 41 no concordantes.

**C — Motivos de V5 reproducidos en los 20 planes:** T1 fuera de candidatos 44; jornada no
concordante 90; sin atribución al expediente T1 131 (no aditivos).

**D pendiente del usuario.** Ninguna medida se adopta como rectora sin aprobación.
Archivos: RESULTADO_POR_PLAN.csv, QA.json, MANIFEST.json. QA: 124/125; el control no superado
es la inconsistencia informativa de IINF. QA independiente contra EXCEPCIONES_AGREGADAS.csv y
SEGUIMIENTO_POR_CODIGO.csv: 0 diferencias.

## Decisión aprobada (D) · 25-10-2026 23:49

**D — Opción A, aprobada por Alexi.** Rige 99 como «pendientes de código SIES» (diccionario v8)
y 149 como «excepciones respecto del ancla T1» (regla T1+carrera+sede+jornada+plan; cambio de
versión = excepción). El 143 de V5 queda retirado como cifra rectora. Los 6 cambios solo de
versión de IINF20241 se muestran como «cambio de versión documentado». Detalle, hashes y
reversión en DECISION_APROBADA.json. No modifica V5, diccionario, bases ni denominadores.
