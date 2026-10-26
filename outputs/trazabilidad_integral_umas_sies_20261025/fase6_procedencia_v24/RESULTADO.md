# Cierre de procedencia V24

## Fase 1/3 · Hitos 1–2: antecedentes y alcance

B — Rama local feature/ire-2026 y remoto consultado mediante ls-remote coinciden en 8e2fb85bb8703758d6878681c9e2a29016e60c63. El diccionario activo es v8. La documentación publicada ya registra usos de continuidad por aprobación interna y propuestas no adoptadas. No se había aprobado una extensión automática a cualquier expediente solo por ausencia de versión nueva.

C — La ausencia de nueva versión no identifica una de varias versiones preexistentes. Conservar el código conocido del mismo expediente y contexto es admisible como seguimiento; no prueba envío SIES del período T2/T3. La aparición de otra versión tampoco obliga a migrar a ella.

## Fase 2/3 · Hitos 1–2: comprobación y clasificación

B/C — Se releen 6.358 posiciones de seguimiento, que se despliegan en 6.374 filas debido a contextos múltiples. No son 6.374 estudiantes. Se verifican todas las filas contra el JSON persistente y el libro: código origen, código destino y CODCLI.

| Procedencia del destino | Filas/contextos | Respaldo |
|---|---:|---|
| Código T1 conservado con contexto concordante | 2.705 | B/C; 4 conservan respaldo interno D |
| Código confirmado por matrícula histórica, fuera del grupo anterior | 41 | B/C |
| Correspondencia interna aprobada, fuera del grupo anterior | 9 | D |
| Contexto localizado, código sin atribuir | 99 | E |
| Posición sin contexto localizado | 3.520 | E |

B/C — Los 99 pendientes se descomponen en 63 con jornada distinta (58 sin expediente T1 atribuido y 5 con él) y 36 sin enlace suficiente al expediente T1 (25 con mismo plan observado y 11 sin contexto T1 del mismo CODCLI). Ninguno cumple todas las condiciones para una nueva herencia automática. No se resuelven pendientes mediante un cambio de etiqueta.

## Fase 3/3 · Hitos 1–2: archivo y QA

C — Se genera V24 en Escritorio, agregando AC:AF a la hoja 56 y ampliando su tabla. AC contiene 6.374 fórmulas; AD conserva el resultado de la comprobación contextual, AE su explicación y AF la clase de respaldo. Las columnas originales permanecen intactas. Las fuentes por fila se conservan en X/Y/Z y la regla previa en V.

B/C — Solo cambian sheet56.xml y table37.xml dentro del libro. Todos los demás componentes conservan exactamente sus bytes: gráficos, bases, fórmulas anteriores y denominadores. La V23 conserva su hash. ZIP/XML y reapertura con lector independiente pasan. Se recalculan las fórmulas nuevas con Artifact Tool y sus conteos coinciden con la evaluación independiente. No se realizó reapertura visual ni recálculo completo con Excel nativo; no se declara PASS global de Excel.

E — La comprobación no acredita ausencia exhaustiva de novedades de oferta ni fechas de migración. No se necesita inventar esa evidencia para conservar códigos de destino que ya estaban respaldados. La oferta sola no se presenta como atribución individual.

C — QA_MANIFEST_V24.json registra rutas y hashes. La entrega individual permanece fuera de Git. Código y documentación nuevos quedan sin commit ni push; el cambio preexistente en PROYECTO_IPSS.json permanece intacto. No se modifica el diccionario activo ni las skills, pues no hay nueva adjudicación ni regla funcional aprobada que propagar.

Checkpoint: clasificación de procedencia terminada. Para disminuir los 99 pendientes, atender las condiciones explícitas de AE y las evidencias de cada contexto; no repetir los 2.755 contextos ya respaldados.
