# Auditoría de las hojas auxiliares de titulación · 26-10-2026

## Alcance y resultado

**[B/C]** Proceso: titulación y conciliación de mallas IPSS 162. Se examinaron las ocho hojas de dos copias del libro institucional de captura usado en 2026, en relación con los cuatro casos ya delimitados. La fecha de ejecución no acredita la fecha de extracción ni de migración de los planes. Se conservaron fuentes, bases, diccionario, tasas y denominadores; no se ejecutó carga, commit ni push.

**[B/C]** Se recuperaron las fórmulas auxiliares de carrera y jornada en una copia del libro alojada en `Archivos de chat de Microsoft Teams`. No se recuperó la fórmula de puntuación de la traza. Las dos cosas son distintas.

## Copias y fórmulas recuperadas

Las rutas completas, hojas, dimensiones y hashes están en `RESULTADO_AGREGADO.json`.

| Copia [B] | SHA-256 | Fórmulas observadas [B/C] |
|---|---|---|
| Segunda carga MU2026, ARCHIVOS VARIOS | `149367ca3f7be7717f958e2ce0f8924e18353e6302766b1abf737c54b5dce8e3` | 862, todas con `#REF!`, en columnas M/N de `Matricula Unificada 2026 subir` |
| Archivos de chat de Microsoft Teams | `1f4866a53d254d329dc2a1a85eaab135458a8963a11333de6b2cea9871bf9b2c` | 862, sin `#REF!`, en las mismas columnas |

**[B/C]** En la copia de Teams, M2 contiene `=VLOOKUP($C2,Datos_alumnos!$A$2:$BO$9677,4,0)` y N2 contiene `=VLOOKUP($C2,Datos_alumnos!$A$2:$BO$9677,10,0)`. Son 431 fórmulas por columna. Consultan el documento de C contra RUT en la primera columna del rango y devuelven NOMBRE_L o JORNADA. No condicionan por CODCLI, plan ni fecha de titulación. Las otras siete hojas no contienen fórmulas.

**[B/C]** Para los cuatro casos, la copia de Teams contiene más de un CODCLI por documento dentro de ese rango. Al inspeccionar la primera coincidencia literal, su CODCLI coincide con el candidato guardado en la traza en tres casos y difiere en uno. Esta inspección no es un recálculo en Excel ni una prueba de que el candidato guardado sea correcto o incorrecto. Confirma que la búsqueda auxiliar y la selección de candidato de la traza no son intercambiables **[E]**.

## Referencias de la traza a sus fuentes

**[B/C]** En los cuatro casos de Teams, `TRACE_ROWINDEX_DATOS_ALUMNOS + 1` señala una fila que coincide simultáneamente en documento y CODCLI con la traza. En ambas copias, `TRACE_HOMO_OBT_ROW + 1` señala una fila de `CUADRO HOMOLOGACIÓN` que coincide en CODCARPR, JORNADA_DA y código SIES. Se ensayaron offsets −1, 0, +1 y +2; se informa la coincidencia observada, sin atribuir al generador una convención no documentada.

**[B/C]** En la copia de segunda carga, las referencias posicionales a Datos_alumnos no coinciden para esos offsets, aunque los cuatro pares documento–CODCLI sí están en otras filas de esa hoja. Por tanto, para reproducir esas referencias debe conservarse la copia exacta con su hash; no basta el nombre del archivo. No se acredita el orden cronológico de las modificaciones ni su responsable **[E]**.

**[B/C/E]** Las cuatro trazas conservan puntaje 2130 como valor, no como fórmula. La copia recuperada permite verificar el expediente seleccionado y la tabla de carrera–jornada–código SIES que se utilizó; no explica los pesos de selección ni acredita el vínculo formal título–CODCLI–plan. Las cuatro atribuciones permanecen pendientes. No se reemplaza el plan anterior por el posterior mediante esta auditoría.

## Los 21 ramos

**[B/C]** `CUADRO HOMOLOGACIÓN` contiene CODCARPR, familia, tipo, jornada, código SIES, versión y duración de carrera. No contiene CODRAMO, ramo origen/destino, PLAN_DE_ESTUDIO, acta o fecha de autorización de equivalencia de asignaturas. El nombre de la hoja no la convierte en un registro de homologaciones curriculares.

**[B/C/E]** Esta revisión no aporta nuevas equivalencias para los 21 pares carrera–plan–ramo. Se mantiene el resultado precedente de `outputs/confirmacion_reconocimientos_20261026/`: 15 pares tienen registros individuales I/E, con 21 registros de reconocimiento repetidos entre extracciones; los seis restantes no se convierten por ello en homologaciones. Los 21 pares no equivalen a esos 21 registros. No se suman extractos ni se generaliza el reconocimiento de una persona a todo el plan. La vigencia y el alcance de las equivalencias siguen pendientes.

## Búsqueda de implementación y reanudación

**[C/E]** Se completó la búsqueda que había quedado interrumpida en `_worktrees/avance_curricular_personal_academico_siipa_v4`, sobre archivos Python, SQL, JS/MJS y notebooks, excluyendo Git y dependencias. No hubo coincidencias de los campos de puntuación/razones, nombre de hoja ni dos etiquetas del criterio. El comando y su salida están registrados. No se afirma ausencia del generador en otras ubicaciones o con otros nombres.

**[E]** Para cerrar lo pendiente se requiere: (1) la implementación que calcula `TRACE_SCORE_CANDIDATO` o su especificación de pesos; (2) registro de título que vincule el expediente y plan, o decisión institucional respaldada que resuelva la atribución; (3) equivalencias curriculares con plan origen/destino y alcance aplicable. La nueva copia de Teams ya quedó inspeccionada: no corresponde volver a buscar en ella una fórmula del puntaje ni actas de ramos.

## QA

**[C]** `verificar.py` reproduce el examen, comprueba los hashes de los dos libros antes y después y guarda solo agregados. Verifica que las cuatro identidades y sus CODCLI candidatos no aparezcan en la salida. No modifica los libros ni ejecuta fórmulas. Este QA acredita la inspección y conservación de fuentes, no el cierre académico de los cuatro casos o los 21 ramos.
