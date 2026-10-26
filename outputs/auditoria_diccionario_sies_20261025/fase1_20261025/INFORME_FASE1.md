# Fase 1 — revisión de los 104 pendientes V17

**B/C:** revisadas 104 observaciones de 58 personas, en 12 códigos de carrera UMAS.
Se reutilizaron v7, los índices y las decisiones anteriores; no se repitió el universo histórico.

| Resultado exclusivo | Observaciones | Tratamiento |
|---|---:|---|
| Recuperación documental por regla anual existente | 5 | C: operaciones verificadas y registradas, todavía no promovidas al activo |
| Propuestas internas con evidencia concreta | 16 | E hasta aprobación de un criterio interno D acotado |
| Continuidad T2 entre anclas concordantes | 12 | E: validar/aprobar criterio separado |
| Evidencia temporal, atribución o versión pendiente | 71 | E: preguntas y fuentes precisadas |
| Total | 104 | Sin eliminaciones ni doble conteo |

## Hito 1: evidencia reutilizada

**B/C:** las 46 operaciones anteriores están incorporadas exactamente; una conserva
deliberadamente una homologación en plan rechazado sin código. Las 119 equivalencias
FCU y 45 asignaciones previas explican las 164 correspondencias solo internas de v7.
No había un cierre olvidado en ese bloque que descontar otra vez.

## Hito 2: hallazgos

**B/C:** nueve contextos de cinco personas usan un documento P en MU2025 y RUT en
PROMEDIOS. El puente explícito J/RUT↔BU/N_DOC de 2025_carga y MU P+N_DOC es único.
BV no coincide con DV de MU, que está vacío: se conserva esa discrepancia, no se
rellena DV ni se utiliza coincidencia aproximada. Cinco contextos TPAS/TAMD cumplen
IDENTIDAD_FAMILIA_ANIO_CONTEXTO_DA_NO_MULTIPLE, implementada en
scripts/reproducir_puente_20261023.py:150–160. El lector de la línea 135 omitía P.
Se comprobó identidad, familia/año, código único, contexto DA exacto y exclusividad.
Son dos recuperaciones I162S2C57J4V1 y tres I162S2C78J2V1. Los cuatro contextos
TLOG/IADM restantes requieren ubicar cambio de jornada; no se cierran por el puente.

**B/C/E:** las 63 discrepancias de jornada se apoyaban en un corte DA posterior.
Las 165 filas PROMEDIOS correspondientes repiten esa jornada; no está acreditado
que el campo esté historizado por asignatura. Las fotos T3 permiten separar:
14 propuestas con foto y MU del mismo año; 12 T2 con anclas concordantes; 10 T2 con
cambio todavía sin ubicar; 8 T3 con versión corroborada solo después; 2 T3 pendientes
de jornada/versión tras el puente documental; 17 sin foto aplicable. Total 63.

**B/C/E:** los otros 34 contextos se separan en 17 homologaciones anteriores al
ingreso declarado, dos propuestas IINF, seis con actividad A/R sin código del
expediente destino y nueve sin evaluación A/R. Las dos observaciones IINF20241
de 2025 T2/T3 tienen actividad APROBADO, foto T3 del mismo CODCLI/carrera/jornada,
ingreso 2025-P2 y código I162S2C1J4V2 documentado para el mismo contexto en 2026.
La correspondencia interna propuesta no equivale a atribución documental 2025.

**B/E:** las otras dos observaciones sin candidato también son homologaciones 2025
de un expediente IINF con ingreso declarado 2026. Junto a las 17 anteriores son 19;
no se demostró cuándo se reconocieron ni se eliminaron del universo.

## Hito 3: cambios registrados y próximos actos

**C:** cinco operaciones de reparación quedaron registradas con estado antes/después,
evidencias y campos permitidos en el archivo privado OPERACIONES_REPARACION_CINCO_P.json.
No requieren una regla D nueva. Su incorporación al índice/edición candidata y
promoción se realizará en la consolidación, con QA específico. La función actual
aplicar_adjudicaciones permite solo cambios internos: no debe usarse sin adaptación
para esta reparación documental. No se editó el motor histórico.

**E/D:** las 16 propuestas internas aún no están autorizadas: 14 de T3 con foto y
código anual concordantes, y dos IINF con actividad/foto 2025 y código 2026. Las 12
T2 necesitan un criterio adicional de continuidad; una foto posterior no descarta
por sí sola un cambio intermedio. Sus IDs y fuentes están únicamente en privado.

**B/C:** el activo sigue en 2750/2854 y 104 pendientes; histórico 21725/24774 y 3049.
Incorporar solo las cinco reparaciones llevaría a 2755/2854 y 99 pendientes; histórico
21730/24774 y 3044. Son efectos calculados, no resultados ya promovidos ni tasas de retención.

## QA, conservación y reanudación

**C:** la clasificación cubre 104/104 sin duplicados. Se reutilizaron 269 filas de
PROMEDIOS, 58 filas DA y las extracciones T3 compartidas. La ruta antigua DA en
Descargas ya no existe; se verificó la copia explícita de hash a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9.
Los cinco cambios candidatos conservan identidad, contexto, fuentes y denominadores.
No se regeneró Excel; no hubo prueba de apertura nativa ni recálculo en esta fase.

**C/E:** revisión ejecutada y resultados registrados; cobertura aún parcial.
La próxima acción es consolidar la reparación técnica y resolver las decisiones
internas concretas, sin reabrir los 104 desde cero. No comenzar búsquedas nuevas
del histórico completo en este cierre de Fase 1. Fuentes y preguntas por observación
permanecen en COLA_FASE1_CLASIFICADA.json y sus revisiones privadas.

**B/C:** V17, edición activa, bases y denominadores conservados. Sin commit, push
ni modificación de complementos. Los archivos compartibles no contienen identificadores.
