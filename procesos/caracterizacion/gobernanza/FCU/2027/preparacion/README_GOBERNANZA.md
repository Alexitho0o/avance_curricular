# README Gobernanza - FCU_ACTUALIZACION_MANUAL_2027

## Proceso anual independiente

Esta carpeta corresponde a la preparacion del instrumento 2027. La gobernanza anual esta en `../README_GOBERNANZA.md` y la preparacion de la futura carga en `../carga_pes/README_GOBERNANZA.md`. FCU 2026 permanece congelado y se consume como referencia de solo lectura. La referencia por hash y el contrato de carga se conservan fuera de 2026; no se reescribe su cierre.

## Decision de revision del usuario: 2026-10-07

Actualizacion vigente 2026-10-13: la exportacion 141234 y sus resultados identifican emprendimiento formalizado como alternativa INSTITUCIONAL AO05 de G02Q95. El registro canonico es `json/PREGUNTAS_INSTITUCIONALES_2027.json` version 3. No crear una pregunta independiente ni inferir SIT_LAB. Conservar las cuatro alternativas originales y G02Q20. G02Q27 es una pregunta institucional mixta; su respuesta no confirma el nombre de un emprendimiento. Conservarla literal y con estado de confirmacion. Esta decision sustituye las instrucciones del 2026-10-09 descritas abajo. Los Excel fechados anteriores y sus manifiestos se conservan como evidencia historica; sus filas de codigo pendiente no son instrucciones vigentes. La publicacion del codigo y reglas no libera la carga PES, cuyo cruce integral sigue pendiente.

### Decision historica reemplazada del 2026-10-09

Decision adicional 2026-10-09: `Tengo un emprendimiento formalizado` se incorpora mediante una pregunta INSTITUCIONAL nueva, no como alternativa de G02Q95. G02Q95 y G02Q20 se conservan. Registro canonico: `json/PREGUNTAS_INSTITUCIONALES_2027.json`; reglas de carga y analisis: `docs/EMPRENDIMIENTO_FORMALIZADO_2027.md`. El codigo nuevo y su catalogo no se inventan; siguen pendientes de identificacion en exportacion. Las hojas RAW historicas se conservan y los cruces vigentes incorporan la decision separada del contenido FCU.

La guia vigente incluye esta decision en G02Q95 y una fila propia, `INST_EMPRENDIMIENTO_FORMALIZADO_2027`, con codigo LimeSurvey vacio y estado CODIGO_LIME_PENDIENTE. El Excel de observaciones corregido se conserva en `evidencias/Observaciones_FCU_2027_trazadas_20261008.xlsx`. Las versiones previas permanecen en `evidencias/historico/`; no se reescriben. Identidad y procedimiento: `json/MANIFIESTO_EMPRENDIMIENTO_20261009.json` y `scripts/gobernanza/registrar_emprendimiento_fcu_2027.mjs`. La validacion esta en `validaciones/VALIDACION_EMPRENDIMIENTO_20261009.json`.

La politica vigente es `json/POLITICA_REVISION_FCU_2027.json`. El usuario decidio conservar su configuracion de obligatoriedad y no realizar ajustes formales de relevancia vacia a `1`. No volver a solicitar cambios de Obligatoria Si/No ni listar esos ajustes como pendientes en el chat o en la guia vigente.

La auditoria conserva esas observaciones en `excluded_checks`, con la decision que las excluye, pero no las incluye en `pending_checks`. Excluir una recomendacion no cambia la fuente ni afirma conformidad integral con el manual. Se mantienen activos los controles de filtros que excluyen estudiantes, referencias a preguntas eliminadas, consentimiento de transferencia, escalas, respuestas y codigos.

## Guia historica actualizada 2026-10-07

### Conciliacion de las 25 filas

Las 25 filas antes marcadas CRUCE PENDIENTE fueron desglosadas sin solicitar modificaciones adicionales de la encuesta: tres correspondencias FCU resueltas por contenido, cuatro alternativas institucionales historicas ausentes, cuatro referencias retiradas del manual 2027, un encabezado de domicilio y trece campos que requieren validar la fuente de carga. Los trece ultimos no son trece preguntas que se deban agregar a LimeSurvey.

La guia usa RETIRADO FCU o RETIRADO INSTITUCIONAL para elementos historicos ya ausentes, no una nueva orden de eliminacion. La accion historica permanece en la columna X de Cruces. Los codigos actuales quedan vacios cuando no existe un elemento activo correspondiente.

La guia historica conservaba un filtro que ocultaba 274 filas. La guia vigente muestra todas las filas. `normalizar_visibilidad_guia_fcu.py` modifica exclusivamente la visibilidad y el filtro de esa hoja en el paquete OpenXML exportado, sin alterar celdas, formulas ni otras hojas; cubre una operacion no expuesta por Artifact Tool. El autor requiere `FCU_PYTHON` con el ejecutable Python del runtime de trabajo. La fuente historica conserva su filtro original.

G01Q69/SQ008 consta como CONFIRMADO POR USUARIO en `json/CONFIRMACIONES_USUARIO_FCU_2027.json`, por su prueba visual. Se conserva el valor observado del XML como evidencia historica, sin falsificar una nueva exportacion. El auditor no vuelve a solicitar esa comprobacion mientras exista el mismo codigo y contenido de la alternativa.

### Adaptador PES 2027 separado

`scripts/fcu_pes_2027.py` extrae los 172 campos unicos del apartado 6.2 del manual, vincula 158 campos al instrumento o a una regla de catalogo y documenta los trece campos de metadatos/fuente externa mas PROCESO. Los 158 incluyen ocho casos que requieren catalogo o decision de equivalencia: no se declara que todos esten resueltos automaticamente.

La especificacion completa esta en `json/ESPECIFICACION_PES_2027.json`. El adaptador admite registros previamente conciliados con `survey_id`, `instrument_year`, `responses` (codigos literales), `prepared` (campos canonicos PES validados), `consents`, `global_consent` y `cohort`. No admite respuestas de una encuesta 2026 bajo los codigos reutilizados del instrumento 2027. La cohorte debe tener ingreso y matricula 2027 en el periodo elegido (1, 2 o 3) y `eligible_student=true` proveniente del filtro institucional gobernado. El adaptador no reinventa el diccionario de estados academicos ni presupone que todos los registros son elegibles.

No usa posiciones del archivo de 195 columnas de 2026. El total del hogar emplea conteos numericos observados, incluye al estudiante y no suma casillas como si fueran cantidades de personas. Las alternativas institucionales no se convierten automaticamente en opciones FCU. El consentimiento negativo bloquea la transferencia del grupo sensible, incluso si se aportan valores preparados.

La salida de registros, cuando pasa los controles, se denomina BORRADOR. La carga oficial permanece bloqueada: deben validarse fuentes/catalogos y la plantilla final de PES. El manual tiene discrepancias entre letras impresas y la secuencia de sus 172 campos (por ejemplo, DIS_ES_15 figura en FR, posicion 174). Estas discrepancias se registran en `printed_column_conflicts`; no se agregan columnas ficticias para completarlas.

No se ejecuto el analisis diario completo ni se altero `caracterizacion.py`, el flujo 2026 o la encuesta en LimeSurvey. Pruebas adicionales: `scripts/test_fcu_pes_2027.py`.

Usar `evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261007.xlsx`. La version 20261006 permanece intacta como historial. Se conservan las cinco hojas y los contenidos de las tres hojas RAW.

En `Cruces`, B/C identifican codigos historicos. R/S identifican codigos actuales, T contiene exclusivamente FCU o INSTITUCIONAL, U registra el estado observado y V el texto actual. La guia muestra los codigos actuales en B/C y conserva los historicos en K/L. Una clave SQ reutilizada no autoriza eliminar su contenido actual por una instruccion historica.

La exportacion disponible contiene 91 preguntas (59 FCU y 32 institucionales), 135 subpreguntas y los dos bloques oficiales de disposicion con 8 y 7 items. Las siete evidencias actuales se conservan por hash en `evidencias/encuesta_141234_20261007_ea9138c666/`. El estado de revision se calcula solo sobre los controles activos bajo la politica del usuario. Los ajustes excluidos no se solicitan ni se cuentan como pendientes.

`json/MAPEO_PARCIAL_FCU_2027_20261007.json` vincula por contenido los 15 campos DIS_ES y los cinco campos DISCAP con sus codigos actuales y valores de respuesta. Es un mapeo parcial, no un adaptador productivo completo de los 172 campos PES. La matriz de severidad institucional se conserva. La transferencia de discapacidad requiere consentimiento afirmativo; las respuestas ausentes o rechazadas no se convierten en cero.

La auditoria vigente esta en `json/AUDITORIA_ESTRUCTURA_20261007_ea9138c666_50cb0a91_19245f3e.json`; los sufijos identifican la politica aplicada y la confirmacion visual registrada. Las auditorias anteriores quedan como historial. Las clasificaciones historicas de G01Q13, G02Q88, G06Q96 y G06Q98 se corrigen en el cruce sin alterar las hojas RAW. Los filtros institucionales G01Q85 y G06Q91 tienen retiro por redundancia, no retiro exigido por SIES.

Procedimiento reproducible: `scripts/gobernanza/auditar_grupos_fcu_2027.py`, `actualizar_cruce_fcu_2027.py` y `actualizar_guia_fcu_2027.mjs`. Pruebas: `test_auditar_grupos_fcu_2027.py`. Esta actualizacion modifica solo documentacion, cruce y utilidades de preparacion 2027. No modifica LimeSurvey ni el flujo productivo 2026. Los nuevos artefactos son copias locales; no se ha realizado commit ni push.

## Historial reconstruido 2026-10-06

Referencia historica: `evidencias/Matriz_FCU_2027_GUIA_TRAZABLE_20261006.xlsx`. No usar sus claves historicas para editar la estructura actual sin consultar el cruce actualizado.

El archivo contiene, en orden, `RAW FCU 2026`, `RAW FCU 2027`, `RAW Institucionales`, `Cruces` y `Guía para editar`. Las hojas raw de manuales extraen enunciados, componentes y los ítems/opciones utilizados en los cruces, con referencias de página y fuente. `RAW Institucionales` preserva las 46 clasificaciones heredadas del inventario; NO constituye una ratificación de esas clasificaciones. Las discrepancias se resuelven en `Cruces`.

La columna A de `Guía para editar` reúne categoría, cambio concreto y resultado final mediante referencias a `Cruces`. Se cubren los 103 códigos del inventario y 279 elementos/preguntas, incluidas referencias oficiales sin código confirmado. Los 63 elementos con correspondencia pendiente se marcan `VERIFICAR ORIGEN` y no autorizan eliminaciones. La guía distingue opciones institucionales añadidas a una pregunta oficial de opciones oficiales retiradas.

Procedimiento: `scripts/gobernanza/preparar_guia_fcu_2027.py` produce el cruce JSON desde fuentes de solo lectura; `scripts/gobernanza/generar_guia_fcu_2027.mjs` crea el Excel con Artifact Tool. El manifiesto asociado registra fuentes, hashes, scripts y verificaciones. La extracción normaliza únicamente saltos de línea de enunciados; no presenta IDs documentales `DIS2026`, `DIS2027`, `P*.I*` o `P*.O*` como códigos LimeSurvey.

La copia del grupo 643 de la encuesta 141234 se conserva en `evidencias/LimeSurvey_141234_grupo_643_20261006.lsg`. Solo confirma ese grupo; no se declara validada la estructura completa de la encuesta activa.

## Nombre del proceso

FCU_ACTUALIZACION_MANUAL_2027

## Alcance

Comparación del Manual de Aplicación FCU 2027 contra el Manual FCU 2026 previamente gobernado; dictamen de ajustes requeridos de formulario y mapeo PES (195→172 campos declarados) y libro de control trazable de cada cambio.

## Fuente de clasificación

- Clasificación fina: `gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.tsv`
- Respaldo Excel: `gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.xlsx`
- Mapeo base: `gobernanza/_mapeo_proyecto/MAPEO_ARCHIVOS_PROYECTO_CARACTERIZACION.tsv`

## Estado

GOBERNANZA_ESPERADA_COMPLETA

## Reglas de uso

- No modificar evidencias originales.
- No mover ni borrar archivos productivos.
- Usar `evidencias/` solo para copias controladas.
- Usar `tablas/`, `json/`, `hashes/`, `docs/` y `validaciones/` para auditoría y trazabilidad.
- Tratar archivos referenciales como soporte documental, no como reconstrucción de cargas.

## Estructura de carpetas

- `evidencias/`: copias controladas.
- `tablas/`: índices TSV y validaciones tabulares.
- `json/`: equivalentes JSON y dictámenes estructurados.
- `hashes/`: archivos `.sha256` por evidencia.
- `docs/`: dictámenes, manifiestos y documentación del proceso.
- `validaciones/`: validaciones mínimas por proceso.

## Advertencias

Este paquete formaliza gobernanza documental. No recalcula procesos productivos ni altera fuentes originales. Las columnas `origen_clasificacion` de `tablas/CANDIDATOS_GOBERNANZA.tsv` registran que este paquete específico fue completado manualmente en sesión con Claude el 2026-10-01, no mediante el pipeline automatizado de clasificación fina.

## Próxima acción

Conciliar la estructura exportada de LimeSurvey con el plan de edición pregunta por pregunta. Los códigos clasificados como candidatos o pendientes no autorizan cambios hasta validar texto completo, subpreguntas y condiciones en la plataforma. Después de esa conciliación, implementar el formulario y reconstruir/probar el mapeo PES 2027 contra el Manual y el libro de control, sin reutilizar posiciones del CSV 2026.

Plan operativo: `docs/PLAN_EDICION_PREGUNTAS_FCU_2027.md`.

Matriz Excel plana, sin colores ni formato de tabla, con una fila por pregunta/subpregunta identificada: `evidencias/Matriz_codigos_LimeSurvey_acciones_FCU_2027.xlsx`. Los códigos candidatos requieren validación contra exportación actual de LimeSurvey.

FASE 1 TERMINADA: SÍ.
