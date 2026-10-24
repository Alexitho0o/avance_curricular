# Dictamen de gobernanza — actualización Manual FCU 2027

## Guía vigente 2026-10-06: fuente, cruces y decisiones

La versión vigente para edición es `evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261006.xlsx`, con tres hojas raw de referencia, `Cruces` y `Guía para editar`. Se reemplaza la lógica de derivar acciones directamente desde las clasificaciones anteriores. La guía obtiene categoría, cambio y resultado del cruce documentado. Los cruces de afirmaciones y opciones incluyen los enunciados literales antiguos y finales; una referencia a un campo PES no se usa como prueba de desaparición de una alternativa.

Verificaciones: 103 códigos incluidos; 279 filas en cruces y guía; 20 elementos con retiro oficial, 65 modificaciones, 103 conservaciones FCU, 28 conservaciones institucionales y 63 correspondencias pendientes. Estos números cuentan elementos y referencias, NO estudiantes ni exclusivamente preguntas principales. No hay orden de eliminación para elementos pendientes o institucionales. La opción de red de apoyo «Otros familiares» se conserva porque aparece en el Manual 2027, aunque cambie el mapa PES.

El raw institucional es el inventario heredado de 46 preguntas, sin correcciones silenciosas. Las clasificaciones originales que contradicen el Manual 2026 se explicitan en la columna de discrepancias de `Cruces`. La numeración del bloque final (2/2) se representa como ID documental `P39.B2`, porque su encabezado en el texto fuente no imprime un número propio; no se inventa un código LimeSurvey.

Las instrucciones históricas de las matrices anteriores no prevalecen sobre esta versión. El manifiesto de la nueva salida contiene su SHA-256 y los de sus fuentes. La estructura activa fuera del grupo 643 no está confirmada por una exportación completa.

## Corrección de clasificación 2026-10-06

Las matrices incorporan la columna `Clasificación y acción FCU 2027` y su evidencia. Esta columna prevalece sobre las instrucciones genéricas anteriores de eliminar. Distingue retiro oficial FCU, modificación, conservación oficial, pregunta institucional a conservar y correspondencia pendiente sin autorización de eliminar. La hoja `Inventario de origen` expone los 103 códigos del inventario y su clasificación anterior para hacer visibles las discrepancias.

El inventario previo clasificó incorrectamente como institucionales contenidos presentes en el Manual FCU 2026: P10.1, P10.2, P11.3, P17.2 y P40.2. La corrección queda identificada por referencia literal al Manual 2026 y por el cambio explícito de 2027. Los filtros y controles complementarios G01Q74, G01Q85 y G06Q91 requieren conciliación propia y se marcan pendientes, no eliminación automática.

`FCU 2027 — ELIMINAR` significa retirar el requisito del bloque oficial FCU 2027. No sustituye la decisión institucional de conservar ese contenido en un bloque propio. `PREGUNTA INSTITUCIONAL — CONSERVAR` excluye expresamente su borrado por cambios del Manual FCU.

## Alcance

Se incorpora como evidencia controlada el Manual de Aplicación FCU 2027 en plataformas propias y se compara contra el Manual FCU 2026 previamente gobernado.

## Evidencia controlada

- `evidencias/Manual_de_Aplicacion_FCU_2027.txt`
- SHA-256: `9b88255dc3467bf684fd8d248b91c919dd4e156a99856d6fede48b3dba74e350`

## Dictamen

**ACTUALIZACION_FCU_2027_REQUIERE_AJUSTE_DE_FORMULARIO_Y_MAPEO_PES**

El Manual declara 17 cambios. La comparación debe tratar como no reutilizables las posiciones del CSV PES de 2026: la estructura pasa de 195 campos declarados en 2026 a 172 campos declarados en 2027. El detalle trazable de cada cambio y su acción requerida se entrega en el libro de control generado para esta actualización.

## Regla operativa

No reutilizar el archivo CSV ni el orden posicional de campos de 2026 para la carga 2027. Implementar y verificar contra el Manual 2027 antes de una carga PES.

## Actualización — libro de control incorporado (2026-10-01)

El libro de control referenciado arriba queda incorporado como evidencia controlada:

- `evidencias/Control_trazable_actualizacion_FCU_2027.xlsx`
- SHA-256: `4616e5e658b0c433b52a31870e6711bd01f7a848ce49a6f797ec0b0782616beb`

Con esto el paquete de gobernanza de este proceso queda completo (README, docs, tablas, json, hashes, validaciones), siguiendo la misma estructura que `FCU_CARGA_PES` y `FCU_ANALISIS_ENCUESTA`.

---

## Addendum 2026-10-02 — Renombre de carpeta (convención año/periodo)

Esta carpeta se renombró de `FCU/2027/actualizacion_manual` a `FCU/2027/preparacion` mediante `git mv` (historia preservada). Motivo: este paquete documenta trabajo previo a la carga FCU 2027 (comparación Manual 2026 vs 2027, ajuste de formulario y mapeo PES); todavía no existe una carga ni un período 2027 ejecutado, por lo que no corresponde numerarlo `1`, `2` o `3` — se usa `preparacion` para todo lo anterior a la primera carga del año.

---

## Addendum 2026-10-02 — Insumo incorporado: clasificación de preguntas encuesta 2026

**Archivo:** `Resumen_clasificacion_preguntas_FCU_2026.xlsx`
**SHA-256:** `803efdeec6e2668a4bd527e9e896d7bc69be0b02fb04381da76ca1c49e18ad3d`
**Origen:** reclasificado desde `FCU/2026/preparacion_encuesta` (ver addendum allí); su insumo original son las evidencias `AUDITORIA_PREGUNTAS_NO_FCU_ENCUESTA_2026.xlsx` y `Manual_de_Aplicacion_FCU_2026.txt` de ese paquete.

**Motivo de incorporación aquí:** según indica el usuario, la clasificación de preguntas de la encuesta 2026 (códigos LimeSurvey vs. preguntas oficiales del Manual, vs. preguntas institucionales adicionales) se hizo específicamente para entender qué preguntas de la plataforma propia deben actualizarse para la FCU 2027 — es insumo de este proceso de actualización, no del instrumento 2026 en sí.

**Contenido:** 5 hojas — `Resumen` (conteos: 73 preguntas oficiales, 45 principales P1–P45, 28 subpreguntas decimales, 22 condicionadas, 6 componentes de domicilio, 46 institucionales adicionales, con corrección de `G00Q91`–`G00Q94` como consentimientos oficiales MINEDUC), `Institucionales` (50 filas: código LimeSurvey + texto + clasificación), `Manual FCU` (75 filas: número de manual P1–P45/condicionadas/domicilio + texto oficial), `Criterio y fuentes`, `Opciones 2026` (465 filas: código LimeSurvey + opción/valor + clasificación, 103 códigos distintos).

**Hallazgo relevante para el siguiente paso (ir pregunta por pregunta en la plataforma):** ninguna hoja trae hoy, en una sola columna, el par código LimeSurvey ↔ número de manual. `Manual FCU` tiene el número sin código; `Opciones 2026` tiene el código sin número de manual. Pendiente: construir ese cruce (por texto de pregunta) antes de usar el archivo como guía definitiva de edición en la plataforma.

**Clasificación de la afirmación:** cifras del archivo = **C/E** (implementación propia / derivado pendiente de conciliación), no **A** ni **B** confirmado por este asistente.

---

## Addendum 2026-10-02 (2) — Hoja de cruce Código LimeSurvey × Manual construida

**Hash anterior (sin hoja de cruce):** `803efdee…8ad3d` (41.713 bytes)
**Hash nuevo (con hoja `Codigo_x_Manual`):** `4a52e293…200e0e59` (55.144 bytes)

Se agregó la hoja `Codigo_x_Manual` (103 filas) cruzando:
- `Opciones 2026` (código LimeSurvey + texto de la pregunta, 53 códigos clasificados "Manual FCU / encuesta")
- `Manual FCU` (número P + tema oficial)
- `Institucionales` (46 preguntas institucionales adicionales sin correspondencia en el Manual + 4 consentimientos MINEDUC)

**Método:** cruce semántico por lectura directa del asistente (no por similitud automática de texto — se probó similitud de texto y falló: 0 coincidencias exactas de 53, y varios "mejores candidatos" fueron semánticamente incorrectos, p. ej. "¿Cuál es tu sexo?" emparejado con "Personas que apoyan en el cuidado"). Por eso el cruce se hizo leyendo cada par.

**Niveles de confianza declarados en la hoja:**
- **ALTA (81 filas):** correspondencia clara por contenido.
- **MEDIA (11 filas):** mismo texto o tema repetido bajo distintos códigos de grupo (`G00`, `G01`, `G02`, `G03`, `G04`, `G06`, `G07`) — hipótesis de ramas condicionales por tipo de postulante; **no se encontró documentación en el Manual ni en el proyecto que confirme qué representa cada prefijo de grupo**, así que esto queda como **E (hipótesis)**, no como dato confirmado.
- **BAJA (11 filas):** sin número de manual evidente (posibles desagregaciones sin P-número propio) o, en los 4 códigos de consentimiento MINEDUC (`G00Q91`–`94`), ambigüedad real entre `Consentimiento` y `Consentimiento sensible` del Manual porque el texto resumido de los 4 códigos es casi idéntico entre sí.

**Clasificación de la afirmación:** toda la hoja es **D/E** (inferencia del asistente / hipótesis), nunca **A** ni **B**. Pendiente obligatorio: validar fila por fila contra la plataforma LimeSurvey real (donde el texto completo de cada pregunta y su lógica condicional sí distinguen los casos MEDIA/BAJA) antes de eliminar o modificar cualquier pregunta para la FCU 2027.

---

## Addendum 2026-10-02 (3) — Plan operativo de edición FCU 2027

Se incorpora `docs/PLAN_EDICION_PREGUNTAS_FCU_2027.md` como matriz operativa para separar eliminaciones, modificaciones e inclusiones requeridas por el Manual 2027.

**Límite de uso:** el plan documenta el contenido y las reglas respaldadas por el Manual, pero los códigos LimeSurvey derivados del instrumento 2026 siguen siendo candidatos. Antes de editar se debe contrastar cada código con una exportación actual que incluya texto íntegro, tipo, subpreguntas, opciones y condiciones. El plan no autoriza eliminar preguntas en producción ni cargar un PES.

**Próximo control:** realizar la conciliación de la exportación LimeSurvey contra las filas del plan; registrar código confirmado, diferencias, decisión y evidencia para cada cambio. Solo después se implementarán el formulario versionado y el mapeo PES 2027 de 172 campos.

## Addendum 2026-10-02 (4) — Matriz Excel por código y acción

Se incorpora `evidencias/Matriz_codigos_LimeSurvey_acciones_FCU_2027.xlsx`, con 31 registros clasificados como `ELIMINAR`, `MODIFICAR`, `INCLUIR` o control explícito de no eliminación. Cada fila muestra el código/campo, texto observado, requisito SIES y el nivel de validación. “Borrar” se representa como `ELIMINAR` para evitar categorías duplicadas.

**Límite:** los códigos heredados de la clasificación 2026 son candidatos, no confirmaciones de la estructura vigente. Los requisitos nuevos sin identificador actual se marcan `POR CREAR / SIN CÓDIGO 2026`; ningún código se inventa. La matriz no autoriza cambios en producción.

**Actualización 2026-10-02:** se reemplazó por una hoja plana sin colores, tablas ni celdas combinadas. La versión actual contiene una fila por pregunta/subpregunta identificada en la clasificación 2026, con texto de la pregunta y del ítem, acción propuesta, requisito SIES y nivel de certeza; los IDs compuestos o no disponibles se mantienen pendientes de cotejo con LimeSurvey. Total: 81 filas de contenido.

**SHA-256 vigente:** `87613b9e545bf78c3e49c08bb50635063ba6b4c8fc61d3062b4cd7ee282f1ed1`.

## Actualización 2026-10-05 — Recorrido por grupos LimeSurvey

La matriz conserva sus 81 filas y ahora tiene 14 columnas. Se agregan al inicio orden de grupo, nombre del grupo, posición de pregunta dentro del grupo y evidencia de ubicación. Se ordena por los siete grupos visibles en las capturas de la encuesta 141234 suministradas por el usuario, manteniendo juntas las subpreguntas.

Los grupos y posiciones visibles se transcriben desde las capturas. La sección Bienestar no aparece desplegada: su asignación por tema se indica como propuesta y la posición interna queda vacía. Las filas sin identificador único se conservan al final o con posición vacía. Las capturas confirman ubicación de preguntas visibles, pero no verifican sus subpreguntas ni condiciones.

Procedimiento de actualización: `scripts/gobernanza/ordenar_matriz_fcu_2027.py`. Respaldo de cada entrada por hash en `backups/FCU_2027/matriz_antes_orden_grupos/`, ignorado por Git. El procedimiento verifica que las columnas originales y el número de filas se conserven, y sincroniza los hashes y tamaños de los registros del paquete.
