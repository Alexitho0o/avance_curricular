# Fase 2/5 · Los 78 pendientes de código SIES (26-10-2026)

**Hito 1/4 · C.** Clasificación: 45 misma carrera y otra jornada en la MU del año; 2 otra versión;
28 cambio de carrera posterior a la MU; 3 sin MU del año. `CLASIFICACION_78.json`.

**Hito 2/4 · B/C.** Las cargas SIES 2025 no traen el código del nuevo contexto (0/57): la matrícula
SIES es anual. La MU 2026 documenta exactamente el código propuesto en 41 de los 57 casos de 2025.
`HITO2_RESULTADO.json`.

**Hito 3/4 · C.** Propuesta: D1 = 31, D2 = 10 (revisión caso por caso), E = 37. `PROPUESTA_DECISION_78.json`.

**Hito 4/4 · D/C.** Alexi aprobó la opción A (solo los 31 D1). Candidata v10 construida y verificada,
**no activa**: 24.774 observaciones, cambian exactamente 31 (E → D), solo campos permitidos, índice MU y
dimensiones idénticos, `aplicar_adjudicaciones(v9, ops)` reproduce la candidata, v9 intacta.
Consultas por el módulo común: 24.774, distintas 31. Niveles v10: 21.569 B/C, 216 D, 2.989 E.
Seguimiento T1→T2/T3: pendientes 78 → 47. Las 149 excepciones respecto del ancla T1 no cambian.
`DECISION_APROBADA_D1.json`, `QA_CANDIDATA_V10.json`, `MANIFEST_CANDIDATA_V10.json`.
Base privada: `~/.local/share/ipss/v10_candidata_31_20261026/`.

**E.** 10 D2 por revisar; 37 E (21 de 2026 sin fuente aún; 16 de 2025 sin evidencia coherente).

## Corrección aprobada · 26-10-2026 11:47 (Fase 2A)

**D.** Alexi aprobó corregir la decisión de 31 a **27**. El control nuevo y obligatorio —año de ingreso a
la carrera según la MU 2026 no posterior al año del contexto— excluye 4 D1 y los 10 D2: en ellos SIES
informa el ingreso a la ingeniería en 2026 mientras en 2025 la persona estaba informada en el técnico
(o, en un caso, la MU 2026 tiene VIG = 0 sin año de ingreso). `DECISION_APROBADA_D1_CORREGIDA.json`;
la decisión de 31 queda marcada como REEMPLAZADA.

**C.** Candidata v10 reconstruida desde v9 en `~/.local/share/ipss/v10_candidata_27_20261026/`
(`c6c4b5a4…`), no activa. Cambian exactamente 27 observaciones (E → D); consultas por el módulo común:
24.774, distintas 27. Niveles: 21.569 B/C, 212 D, 2.993 E. Pendientes del seguimiento: 78 → 51.
La candidata de 31 (`v10_candidata_31_20261026/`) queda marcada REEMPLAZADA y no se usa.
