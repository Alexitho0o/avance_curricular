# Revisión de las tres observaciones de jornada restantes

Proceso: seguimiento intertrimestral IPSS 162. Referencia T2/T3-2024; contraste documental MU2025 y MU2026. No se recalcula retención ni se modifica la cohorte.

## Dos cierres aprobados ya aplicados

**D/C.** INF35-04 T3-2024 e INF35-10 T2-2025 están en `v6_20261023_dos_jornadas` como `I162S2C1J2V4`. La atribución documental continúa **E**. El cierre es individual por contexto; no convierte secciones ni fechas de clase en reglas universales. Véase `../cierre_dos_jornadas_20261023_145844/MANIFEST.json`.

## Nueva comprobación

**B.** Se releen cuatro libros de preparación MU2025 y se encuentran 18 filas relacionadas con los dos expedientes del foco. Son registros repetidos entre etapas de preparación, no 18 personas ni respaldos independientes. Se conservan hoja, fila, valor y fórmula en PREPARACION_MU2025.json; los identificadores permanecen privados.

**B. INF35-03:** `IPSS_Procesamiento.xlsx`, `Precarga`, fila 1023, columnas P/Q = 1/1; `Carga_Completa`, fila 1025, y `Carga_Completa (2)/(3)`, fila 1030, mantienen esos componentes. `Final a carga`, fila 1003, también J1V1. La descarga original de matrícula 2025, hoja `08-05-2025_22-26-22_Matrícula_P`, fila 1018, conserva J1V1. La versión ya estaba en la precarga: no la generó este diccionario. Las celdas revisadas de VERSION son valores guardados; no se encontró allí una fórmula o fecha de migración que explique V1 frente a V2. `FECH_CAR` 16-abr-2025 en precarga y 08-may-2025 en descarga son campos observados; no se interpretan como fecha efectiva de cambio de plan.

**B. INF35-04:** GESTIONSGE_1703.xlsx, Hoja1: fila 12434 (07-oct-2024) propuesta de ramos T3 pendiente de confirmación; fila 12436 (08-oct) propuesta diurna; fila 12424 (09-oct) inscripción de ramos sin jornada explícita; fila 12427 (13-nov) relato de cambio de jornada. El nuevo enlace del 09-oct confirma inscripción, pero su texto no confirma jornada ni describe T2. MU2025 `2025_carga` fila 353 ya observa V/J2V4; no acredita que esa situación correspondiera al julio-septiembre anterior.

## Resultado por observación

| Observación | Resultado | Qué falta | Clase |
|---|---|---|---|
| INF35-03 T2-2024 | Sigue pendiente; actividad en secciones mixtas | Situar jornada y versión personal en T2 | B/C/E |
| INF35-03 T3-2024 | Jornada D respaldada; versión sin resolver | Determinar si V1 de MU2025 aplica ya en T3-2024, frente a V2 documentada después | B/C/E |
| INF35-04 T2-2024 | J1V2 sigue como candidato de continuidad T1 | Evidencia de jornada efectiva de T2 o fecha/período del cambio; inscripción de octubre sin jornada no basta | B/C/E |

**E.** No se adjudica ninguna de estas tres. La fecha de incorporación al reporte y la de matrícula anual no prueban cuándo cambió el plan. Una sección reúne estudiantes; no asigna por sí misma la versión SIES personal. JORNADA administrativa vigente en una exportación no constituye una historia por período. MODALIDAD del bloque DatosAlumnos se conserva como dato de origen y no se equipara a MODALIDAD SIES.

**C.** Identidad por RUT con DV en preparación MU; contactos con cuerpo RUT exacto y carrera IINF, verificando unicidad de ese cuerpo en el universo existente, sin inventar DV. Se excluyen notas no académicas. La hoja Formato sin correspondencia de identidad cacheada no se usa para afirmar ausencia. Los libros se leen sin recalcular ni guardar.

## Control y reanudación

**C.** Cinco filas decisivas releídas independientemente; hashes de las fuentes sin cambios; diccionario v6 intacto durante esta revisión. Tres observaciones de dos personas siguen pendientes. Seis homologaciones del foco original permanecen fuera del alcance. Para avanzar: localizar el origen anterior de J1V1 conservado en Precarga o evidencia fechada que vincule explícitamente jornada/plan a T2/T3-2024; no volver a asignar por mayoría de sección.

**D/C.** Bases, Excel y denominadores conservados. Sin commit/push. Código y evidencia agregada local; detalle restringido fuera de Git. Esto no equivale a publicación remota.
