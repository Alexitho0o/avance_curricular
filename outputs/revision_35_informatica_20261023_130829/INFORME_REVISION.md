# Revisión de los 35 pendientes de Informática

Proceso: retención intertrimestral IPSS 162. Contextos académicos 2024–2026; revisión 23-10-2026. Diccionario común v1 y aplicación V12, sin modificación.

**B/C. Resultado: 14 observaciones recuperables para revisión y 21 pendientes de código de destino. Son 35 observaciones de 12 personas y 12 expedientes objetivo, no 35 estudiantes. No se aplicaron cierres.**

| Resultado | Observaciones | Personas del grupo | Respaldo |
|---|---:|---:|---|
| Ancla T1 documentada, contexto actual de jornada discrepante | 8 | 8 | B/C |
| Código recuperable por puente explícito pasaporte–RUT | 6 | 2 | B/C |
| T2/T3 con cambio de jornada sin período efectivo acreditado | 15 | 8 | E para adjudicación de destino; B para discrepancia observada |
| Homologaciones TPAS20241 de personas cuya cohorte origen es Informática | 6 | 2 | B para filas; E para atribución histórica al destino |

**C.** Las personas de las filas 1 y 3 son las mismas: no se suman. Dos personas tienen todas sus observaciones recuperables (6); ocho solo el ancla T1 (8 recuperables y 15 pendientes); dos mantienen sus seis contextos TPAS pendientes. Total: 2+8+2=12 personas; 8+6+15+6=35 observaciones.

## Lo que sí se puede reutilizar

**B/C.** Dos personas de MU2025 están informadas con tipo documental P. La relación explícita de `IPSS_Procesamiento.xlsx`, hoja `2025_carga`, columnas J (RUT), BU (N_DOC) y BV (DV), enlaza inequívocamente su documento con el RUT observado en UMAS. Se releyó la tabla y se comprobó unicidad global del enlace. MU2025 registra **I162S2C1J1V2**. En PROMEDIOS, el mismo CODCLI mantiene IINF20241, jornada D y asignaturas aprobadas en períodos 1, 2 y 3. Es posible reutilizar ese código anual en las seis observaciones de seguimiento interno. No es evidencia de un envío SIES trimestral. El adaptador documental del diccionario excluía estos P; el código ya existía en la fuente.

**B/C.** Otras ocho observaciones son del propio período 1. El código literal de MU existe, y se encontró un único expediente IINF para cada persona en los respaldos releídos. Se recuperan como **anclas T1**, registrando en paralelo la discrepancia de jornada del contexto actual. No se valida por ello el código de destino T2/T3. Sus códigos se detallan en `RESUMEN_CODIGOS.csv`.

## Qué impide completar las demás

**B/E.** En ocho personas, los respaldos de PROMEDIOS muestran distintas jornadas para el mismo CODCLI y el mismo plan IINF20241, incluso al repetir asignaturas del mismo año/período. No se encontró un cambio de nombre de plan que explique por sí solo el cambio de código. Está comprobada la variación entre respaldos; no está acreditada la fecha o el período efectivo de cada cambio. Quince observaciones T2/T3 quedan pendientes de adjudicación de destino. No se exige el día exacto: bastaría un respaldo que delimite de forma inequívoca qué jornada/versión regía en cada período. Los datos releídos no lo delimitan.

**B.** Ejemplos de secuencias literales MU: J1V2→J1V2→J4V2 (2024, 2025, 2026); J2V4→J1V1→J1V2; J1V2→J2V4 (2024, 2025). Todas dentro de I162S2C1. Estas secuencias no autorizan transportar el código 2026 hacia 2024 ni asignar a todo IINF20241 una misma versión.

**B/E.** Seis de los 35 contextos pertenecen a TPAS20241, aunque las personas ingresaron al seguimiento desde Informática. En PROMEDIOS_12166 sus diez filas académicas 2024 son I/CONVALIDADO=S, distribuidas en tres períodos por persona. MU2024 conserva I162S2C1J4V2; el código de Programación I162S2C57J4V1 aparece después: en 2026 para una persona, en 2025 para la otra. No acreditan matrícula TPAS en cada período 2024 ni permiten asignar retrospectivamente el código posterior. No son seis ambigüedades entre V2/V3 de Informática.

## Fuentes y trazabilidad

**B/C.** Se releyeron MU2022–2026, el puente IPSS_Procesamiento, PROMEDIOS_2071, _3233, _7804 y _12166; DATOSDEALUMNOS_11248, _11998 y _12159; DATOSDEALUMNOS ORIGEN DE LOS DATOS2025; y tres respaldos de calificaciones 2024. Los reportes de calificaciones incorporan fechas internas de reporte 2024 y de inicio/fin de cursos. No contienen por sí mismos código SIES completo ni fecha de migración de jornada.

**B.** DATOSDEALUMNOS_12159 ya no estaba en Descargas. Se recuperó su copia del Escritorio, con el mismo SHA-256 gobernado a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9. No quedó un bloqueo de lectura sin resolver. No se usa la fecha de carpeta como fecha efectiva de matrícula.

**C.** `INVENTARIO.json` identifica archivo, hoja, encabezados, filas y hash; `FUENTES_HASHES.json` fija las fuentes. El detalle privado registra cada observación, consulta original, fuente/hoja/fila/hash, código de origen, resultado recuperable y motivo pendiente. Ningún identificador individual se incluye en este informe o en el CSV agregado.

## QA y reanudación

**C. QA OK_CON_ADVERTENCIAS.** Selección 35/35, doce identidades y doce expedientes objetivo; sin conflictos de identidad detectados; balance 14+21; puente de dos personas unívoco; copia faltante recuperada por hash. Fuentes verificadas de nuevo al cierre; Excel V12 conserva su hash. Las 35 consultas de la edición activa siguen pendientes: este informe no simula que los cierres ya se aplicaron.

**D/C.** Se mantienen bases, denominadores, fórmulas, tasas, Excel y edición activa del diccionario. Sin commit ni push. Rama feature/ire-2026; HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes/después.

**E. Siguiente paso:** revisar/adoptar por alcance los 14 resultados recuperables en una nueva edición: seis mediante el adaptador documental y ocho como anclas T1 con discrepancia histórica explícita. Conservar pendientes los quince destinos de jornada y las seis homologaciones TPAS. No extrapolar a los otros años ni al universo histórico. Para las tasas, el código de cohorte T1 ya documentado se conserva; los códigos de destino pendientes no convierten a nadie en desertor ni alteran denominadores.
