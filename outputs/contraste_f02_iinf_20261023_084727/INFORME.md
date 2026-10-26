# IINF20241: contraste V2/V3 y F02

**Resultado C/E:** la evidencia converge en V2 como propuesta interna para las
tres observaciones IINF20241 de F02, pero el criterio nuevo de continuidad entre
cortes no se adopta automáticamente. La instrucción vigente exige dejar las
propuestas nuevas para aprobación. El cierre anterior autorizado se conserva.

## Comparación observada — B/C

| Elemento | V2 documentada: 132 personas | V3 documentada: una persona | F02 |
|---|---|---|---|
| Ingreso DA | 2021: 1; 2022: 8; 2023: 38; 2024: 85 | 2020 | 2023 |
| FOR_ING_ACT en MU2024 (código, sin reinterpretar) | 1: 130; 11: 2 | 11 | 1 |
| Ingreso actual/origen MU2024 | Distribución en RESULTADOS_DESCRIPTIVOS.json | 2020/2019 | 2023/2023 |
| Trayectoria dirigida | No se supone idéntica para todo el grupo | IECIRE2020/J2 hasta 2023; IINF20241/J4 en 2024 | IECIREOL20211/J4 desde 2023; IINF20241/J4 en 2024 |
| Código MU 2023 → 2024 → 2025 | Se prueba por persona, no por mayoría | C1J2V4 → C1J4V3 → sin fila localizada en la base leída | C1J4V2 → C1J4V2 → C1J4V2 |
| Homologaciones IINF20241 en 2024/T1 | No se usa como discriminador general | 3 asignaturas | 4 asignaturas |
| Plan y año de actividad IINF20241 | 2024 | 2024 | 2024 |

Todos los códigos abreviados tienen prefijo I162S2. Los conteos se calculan por
persona, evitando contar tres veces a quien tiene actividad en T1/T2/T3. Las
etiquetas documentales corresponden al diagnóstico y al código MU anual
releído; no son comprobantes de aceptación SIES por cada período UMAS.

**B:** oferta 2024: C1J4V2 es Plan Regular, ocho semestres; C1J4V3 es Plan
Regular de Continuidad, cuatro semestres. El plan previo C1J2V4 de la persona
V3 figura como Plan Regular de ocho semestres en oferta 2022 y 2023. Por tanto,
no se puede explicar su V3 afirmando que ya cursaba continuidad: lo observado
es un cambio de jornada y código/perfil declarado, cuya causa no se acredita.

**B/C:** PROMEDIOS confirma diez filas IINF20241 para F02 en 2024: seis T1
(cuatro homologadas y dos aprobadas), dos T2 aprobadas y dos T3 aprobadas.
La persona V3 tiene nueve filas: cinco T1 (tres homologadas y dos reprobadas),
dos T2 y dos T3 reprobadas. Son registros académicos del reporte, no un censo
completo de asignaturas esperadas ni prueba de matrícula al cierre. Los niveles
se solapan; tampoco distinguen por sí solos la versión. No se cambian tasas.

## Prueba independiente de selección — C

Se ocultó el código objetivo MU2024. Para cada una de las 133 personas con
versión atribuida se consultó exclusivamente MU2023 y MU2025 de la misma
persona y familia I162S2C1J4. Solo se seleccionó un código si ambos cortes
tenían el mismo código único. Después se contrastó con MU2024.

- 31 personas seleccionadas: 31 coincidencias, cero diferencias.
- 102 abstenciones por falta de los dos extremos concordantes.
- La única persona V3 no cumple el criterio y queda en abstención.
- F02, fuera del grupo documental de prueba, obtiene V2 por ambos extremos;
  además MU2024 documenta V2 para la persona/familia.

**Límite E:** la prueba valida concordancia anual en el subconjunto cubierto.
No demuestra la fecha efectiva de asignación al nuevo expediente ni valida
una regla universal: no hay caso V3 seleccionado. No usar 31/31 como precisión
general ni suponer que un ingreso 2023 obliga a V2. FOR_ING_ACT=11 tampoco
obliga a V3: hay dos personas V2 con ese valor.

## Propuesta concreta para F02 — C, pendiente de decisión D

Registrar las tres observaciones IINF20241 2024/T1, T2 y T3 como
**correspondencia interna contextual V2**, apoyada en identidad exacta,
plan/períodos observados, misma familia y V2 antes, durante y después del año.
Conservar el código documental por expediente pendiente y la fecha
administrativa del cambio como desconocida. No generalizar a todo IINF20241.

Esta propuesta relaja la exigencia previa de enlace explícito al nuevo
expediente; por eso requiere aprobación y no se aplica silenciosamente. La
instrucción del usuario que rige esta decisión dice: «Deja propuestas nuevas
para aprobación con número de afectados y riesgos».

Si se autoriza, cerraría tres observaciones de una persona: pendientes internos
3.093 → 3.090 y personas con pendiente 1.751 → 1.750, sobre los mismos
denominadores. Esto es un escenario, no el estado adoptado. Los pendientes
documentales seguirían en 3.213 observaciones / 1.838 personas.

**Estado vigente:** tres observaciones IINF20241 de F02 pendientes; una
observación IECIREOL20211 ya cerrada internamente por la autorización anterior.
No se alteraron bases, denominadores, códigos documentales ni el motor anual.

## Trazabilidad y QA

Fuentes: OBSERVACIONES_PRIVADAS.json del diagnóstico reproducido (24.774
observaciones); BASE_RETENCION_MU de la base anual 2022–2026; Hoja1 de
PROMEDIOSDEALUMNOS_12166.xlsx; oferta anual de maestro.json. Se releyeron 355
filas MU y 1.858 filas PROMEDIOS para las 134 personas del contraste.
Localizadores fuente/hoja/fila e identificadores quedan en el detalle privado;
MANIFEST.json y FUENTES_HASHES.json fijan entradas y resultados por SHA-256.

QA técnico OK_CON_ADVERTENCIAS: fuentes intactas, grupos sin doble conteo,
prueba separada por persona, cierre anterior conservado, sin promoción del
criterio nuevo. No se afirma causalidad de las diferencias. Sin commit/push.
