# Plan de edición de preguntas FCU 2027

## Adicion institucional registrada el 2026-10-09

Agregar una pregunta nueva e independiente: `Tengo un emprendimiento formalizado`, en ANTECEDENTES FAMILIARES Y SOCIOECONOMICOS. Conservar G02Q95 y G02Q20 sin agregar esta alternativa. La pregunta nueva no tiene campo PES y no modifica SIT_LAB. El codigo LimeSurvey y su catalogo quedan pendientes de identificacion; no reutilizar un codigo historico. Registro canonico: `../json/PREGUNTAS_INSTITUCIONALES_2027.json`. Reglas para carga, estudios y comparaciones: `EMPRENDIMIENTO_FORMALIZADO_2027.md`.

## Propósito

Matriz operativa para actualizar el cuestionario institucional de la FCU 2026 a la versión FCU 2027. Este archivo indica qué controles deben eliminarse, modificarse o incorporarse antes de una nueva aplicación en LimeSurvey y antes de reconstruir el archivo PES 2027.

Este documento es una especificación de edición. No ejecuta cambios en LimeSurvey, no modifica el CSV 2026 y no autoriza todavía una carga PES.

## Fuentes y alcance

| Fuente | Uso | Evidencia |
| --- | --- | --- |
| `gobernanza/FCU/2027/preparacion/evidencias/Manual_de_Aplicacion_FCU_2027.txt` | Regla oficial de preguntas, alternativas, condicionalidades y estructura PES | SHA-256 `9b88255dc3467bf684fd8d248b91c919dd4e156a99856d6fede48b3dba74e350` |
| `docs/Manual_de_Aplicacion_FCU_2026.txt` | Línea base de comparación | SHA-256 `ec02e8161ef29427c4dfcc71230153a35fc30d3e468bccdb843bee098adbe770` |
| `gobernanza/FCU/2027/preparacion/evidencias/Control_trazable_actualizacion_FCU_2027.xlsx` | Control de los 17 cambios y mapa PES 2027 | SHA-256 `4616e5e658b0c433b52a31870e6711bd01f7a848ce49a6f797ec0b0782616beb` |
| `gobernanza/FCU/2027/preparacion/evidencias/Resumen_clasificacion_preguntas_FCU_2026.xlsx` | Códigos LimeSurvey y clasificación del instrumento 2026 | SHA-256 `4a52e2930bd02620c637bc679a0a0db9ce07bc7f9b9f35c3aa9da6b9200e0e59` |

### Regla de confianza

- **CONFIRMADO_MANUAL:** acción declarada expresamente en el Manual FCU 2027.
- **CÓDIGO_LS_IDENTIFICADO:** código LimeSurvey observado en la clasificación 2026, pero debe verificarse en la plataforma antes de editarlo.
- **CÓDIGO_LS_PENDIENTE:** el derivado disponible no permite asignar el código con seguridad. No eliminar ni reutilizar un código por posición.
- **PENDIENTE_VALIDACIÓN:** requiere revisar texto completo, grupo, subpreguntas y condicionalidades en LimeSurvey.

La hoja `Codigo_x_Manual` del resumen 2026 declara que sus cruces son inferencias del asistente, no una fuente oficial. Por ello ningún código se promueve a definitivo solamente por aparecer en esta matriz.

## Resumen de decisión

| Acción | Resultado gobernado |
| --- | --- |
| Eliminar | Preguntas/campos retirados por el Manual 2027 y opciones antiguas que ya no deben existir |
| Modificar | 17 cambios declarados por el Manual 2027, incluyendo reubicaciones, textos, alternativas, escalas y condicionalidades |
| Incluir | Nuevas alternativas, la pregunta directa de jefatura de hogar, el ítem de ambiente físico, la alternativa sin red de apoyo y los 15 enunciados finales reorganizados |
| Reconstruir | El mapeo PES completo 2027: 172 campos declarados; no reutilizar las 195 posiciones del CSV 2026 |

## 1. Eliminar

Las siguientes preguntas o componentes deben retirarse del formulario 2027 y del mapeo PES. Cuando se indica un código LimeSurvey, es un candidato identificado en la evidencia 2026 y debe confirmarse en la plataforma.

| Elemento FCU 2026 | Código/campo observado | Acción | Estado |
| --- | --- | --- | --- |
| P1 Nombre(s) | `NOMBRE` / código LimeSurvey no identificado en el derivado | Eliminar control y campo | CONFIRMADO_MANUAL; CÓDIGO_LS_PENDIENTE |
| P2 Primer apellido | `APELLIDO_1` / código LimeSurvey no identificado en el derivado | Eliminar control y campo | CONFIRMADO_MANUAL; CÓDIGO_LS_PENDIENTE |
| P3 Segundo apellido | `APELLIDO_2` / código LimeSurvey no identificado en el derivado | Eliminar control y campo | CONFIRMADO_MANUAL; CÓDIGO_LS_PENDIENTE |
| P7 Estado civil | `ESTADO_CIVIL` | Eliminar pregunta y campo | CONFIRMADO_MANUAL |
| P9.1 Nombre social | `G07Q04` | Eliminar pregunta condicional | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| P10.1 Acreditación CONADI | `G01Q06` como candidato actual | Eliminar pregunta y condicionalidad | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| P10.2 Orientación CONADI | `G01Q14` como candidato actual | Eliminar pregunta y condicionalidad | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| P11.3 Orientación para RND | `G01Q31` como candidato actual | Eliminar pregunta y condicionalidad | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| P17.2 Personas que apoyan el cuidado | `G00Q11` y sus subpreguntas `SQ002` a `SQ008` como candidatos actuales | Eliminar pregunta, subpreguntas y regla condicional | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| P19 Ingreso mensual total del hogar | `G02Q17` | Eliminar pregunta y campo `INGRESO` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| P33 opción Prensa (diarios físicos) | `G01Q41[SQ012]` | Eliminar opción; se reemplaza por opción unificada | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| P33 opción Prensa digital | `G01Q41[SQ013]` | Eliminar opción; se reemplaza por opción unificada | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| P40.2 Participación en PIE | `G06Q66` como candidato actual | Eliminar pregunta y condicionalidad | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN. El mapa PES 2027 no contiene un campo `PIE` que retirar |
| P43 campo antiguo de apoyo | `RED_APO_OFAM` en el mapa PES 2026 | Retirar el campo antiguo; no asumir su etiqueta exacta sin revisar el texto y las subpreguntas de LimeSurvey | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| P45 bloque antiguo, afirmaciones retiradas | `DIS_ES_16`, `DIS_ES_17`, `DIS_ES_18` | Eliminar afirmaciones y campos | CONFIRMADO_MANUAL |
| P30 opción neutral | `G01Q55` y campos Likert asociados | Eliminar “Ni de acuerdo ni en desacuerdo” | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| P31 opción neutral | `G01Q84` y campos Likert asociados | Eliminar “Ni de acuerdo ni en desacuerdo”; conservar “No lo utilicé” cuando corresponda | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO. El Manual/PES define `[0–4]`: `0 = No lo utilicé`, `1–4 =` niveles de acuerdo |

La eliminación de una pregunta institucional adicional no debe confundirse con la eliminación de los consentimientos oficiales `G00Q91`–`G00Q94`. Estos cuatro códigos fueron reclasificados como preguntas oficiales de autorización al Ministerio y deben validarse por separado, no eliminarse por similitud de texto.

## 2. Modificar

Esta tabla reproduce los 17 cambios del Manual 2027 y los convierte en acciones concretas de edición.

| N° | Referencia 2026 → 2027 | Qué debe cambiar en el formulario | Qué debe cambiar en PES/mapeo | Código o campo candidato | Estado |
| ---: | --- | --- | --- | --- | --- |
| 1 | P1–P3 → eliminadas | Retirar nombre y apellidos | Retirar `NOMBRE`, `APELLIDO_1`, `APELLIDO_2` | Campos PES 2026 | CONFIRMADO_MANUAL |
| 2 | P7 → eliminada | Retirar estado civil | Retirar `ESTADO_CIVIL` | Campo PES 2026 | CONFIRMADO_MANUAL |
| 3 | P8 → P4 | Mantener sexo biológico y reemplazar alternativas por Hombre, Mujer, No binario | Actualizar `SEXO` y catálogo | `G00Q02` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 4 | P9.1 → eliminada | Retirar registro de nombre social | Retirar `NOMBRE_SOCIAL` | `G07Q04` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 5 | P10.1–P10.2 → eliminadas | Retirar acreditación y orientación CONADI | Retirar `CONADI_ACRED`, `CONADI_ORIENT` | `G01Q06`, `G01Q14` candidatos | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| 6 | P11.3 → eliminada | Retirar orientación para RND | Retirar `DISCAP_ORIENT` | `G01Q31` candidato | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| 7 | P13 → P9 | Cambiar texto de ayuda: celular completo con 56 + 9 + ocho dígitos; sin `+`, espacios ni guiones | Validar `CEL` como numérico de 11 dígitos | Código LimeSurvey no identificado en el derivado | CONFIRMADO_MANUAL; CÓDIGO_LS_PENDIENTE |
| 8 | P8 → P13 | Sustituir “quién es el jefe” por “¿Eres el jefe de hogar?” con Sí/No | Codificar `JEFE_HOGAR` como `[1–2]` | `G01Q18` candidato por texto, no confirmado en la plataforma | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| 9 | P17.2 → eliminada | Retirar quién apoya el cuidado | Retirar campos `APO_CUI_*` | `G00Q11` candidato actual | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| 10 | P19 → eliminada | Retirar ingreso mensual total del hogar | Retirar `INGRESO` | `G02Q17` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 11 | P33 → P28 | Reordenar “Visitando personalmente”; fusionar ferias/charlas y prensa física/digital | Reconstruir `MEDIOS_1–MEDIOS_13`; no conservar posiciones antiguas | `G01Q41` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 12 | P35 → P30 | Mantener cuatro afirmaciones y escala de 4 opciones | Recodificar `MAT_FAC`, `MAT_CLARO`, `MAT_RAP`, `MAT_ATE` a `[1–4]` | `G01Q55` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 13 | P36 → P31 | Mantener cinco afirmaciones; eliminar la categoría neutral y conservar “No lo utilicé” | Codificar `MIN_BEC`, `MIN_CAL`, `MIN_BUS`, `MIN_FUT`, `MIN_FUAS` como `[0–4]`: `0 = No lo utilicé`; `1–4` acuerdo | `G01Q85`, `G01Q84` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 14 | P40.2 → eliminada | Retirar participación en PIE | El mapa PES 2027 no contiene el campo `PIE`; retirar el control del formulario si sigue presente | `G06Q66` candidato | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| 15 | P41–P42 → P36 | Reemplazar acceso y espacio físico por una sola matriz de frecuencia de uso | Mapear `REC_TEC_1–10` a `REC_1–10` e incorporar `ESP_EST` como `REC_11`; valores `[1–4]` | `G01Q67`, `G01Q68` | CONFIRMADO_MANUAL; CÓDIGO_LS_IDENTIFICADO |
| 16 | P43 → P37 | Hacer obligatoria la pregunta y agregar “No cuento con red de apoyo” | Retirar `RED_APO_OFAM`, conservar/revisar los campos de apoyo válidos, y crear `RED_APO_NIN` | `G06Q91`, `G01Q69` candidatos | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |
| 17 | P45 → P39–P40 | Reemplazar tres bloques por dos, retirar afirmaciones antiguas y usar escala de 4 opciones | Recrear `DIS_ES_1–15`; retirar `DIS_ES_16–18` | `G07Q71`, `G01Q72`, `G01Q73` candidatos | CONFIRMADO_MANUAL; PENDIENTE_VALIDACIÓN |

## 3. Incluir

Estos elementos deben existir en la versión 2027. La inclusión se refiere al contenido del formulario y no implica reutilizar códigos o posiciones 2026.

### 3.1 Alternativas y reglas nuevas

| Ubicación FCU 2027 | Elemento que debe incorporarse | Regla de edición |
| --- | --- | --- |
| P4 Sexo | `H: Hombre`, `M: Mujer`, `X: No binario` | Reemplazar catálogo anterior y validar código de salida `SEXO` |
| P9 Celular | Texto de ayuda completo: `56912345678`; sin signo `+`, espacios ni guiones | Validar 11 dígitos y conservar el valor como texto o número según la implementación compatible con PES |
| P13 Jefatura de hogar | Pregunta directa: `¿Eres el jefe de hogar?` | Solo `Sí` / `No`; retirar la pregunta antigua de categorías de jefatura |
| P28 Medios | `En ferias, exposiciones educativas o en charlas realizadas en mi colegio o liceo` | Sustituye las dos opciones 2026 separadas |
| P28 Medios | `Prensa digital o física` | Sustituye `Prensa digital` y `Prensa (diarios físicos)` |
| P36 Recursos | `Un ambiente y espacio físico que permite la concentración y que sea cómodo para estudiar` | Incorporar como nuevo ítem de la matriz Likert |
| P37 Red de apoyo | `No cuento con red de apoyo` | Incorporar como alternativa; validar exclusividad con las demás alternativas |

### 3.2 Escalas que deben existir

| Pregunta 2027 | Escala requerida |
| --- | --- |
| P30 Evaluación de matrícula | 1 Muy en desacuerdo; 2 En desacuerdo; 3 De acuerdo; 4 Muy de acuerdo |
| P31 Información MINEDUC | `[0–4]`: 0 No lo utilicé; 1 Muy en desacuerdo; 2 En desacuerdo; 3 De acuerdo; 4 Muy de acuerdo |
| P36 Recursos | 1 Nunca; 2 A veces; 3 Frecuentemente; 4 Siempre |
| P39–P40 Disposición | 1 Muy en desacuerdo; 2 En desacuerdo; 3 De acuerdo; 4 Muy de acuerdo |

### 3.3 Bloques P39–P40 que deben reconstruirse

El Manual 2027 exige dos bloques y 15 afirmaciones. Deben cargarse con el texto oficial, no copiando las posiciones de `G07Q71`, `G01Q72` y `G01Q73`.

**P39, bloque 1**

1. Me esfuerzo por terminar todo lo que empiezo.
2. He superado momentos difíciles para alcanzar una meta importante.
3. Cuando estoy en un entorno educacional o laboral, me siento parte de una comunidad.
4. Soy capaz de sacrificar el descanso y la diversión para dedicarme a mis estudios.
5. Pongo mucho esfuerzo en mis estudios y actividades académicas.
6. Realizo mis actividades académicas con dedicación y a conciencia.
7. Estoy seguro(a) de que si estudio y me organizo, puedo obtener las notas que quiero.
8. Me siento seguro(a) de la carrera que elegí.

**P40, bloque 2**

1. Tengo dificultades para mantener el foco en proyectos que duran más de unos meses.
2. Cuando me va mal en algo, me cuesta manejar emociones fuertes como la rabia, la pena o el nerviosismo.
3. Dudo que con mis habilidades académicas tenga un buen desempeño en la carrera.
4. Cuando tengo un desafío académico, me cuesta organizarme para resolverlo.
5. Tengo dificultades para comprender los textos que leo.
6. Se me hace difícil expresar mis ideas por escrito.
7. No me siento tan confiado(a) en que podré titularme.

El mapa PES 2027 denomina el resultado de este bloque `DIS_ES_1–DIS_ES_15`. Los nombres de pregunta/subpregunta en LimeSurvey deben definirse después de revisar la plataforma, manteniendo una clave estable y no posicional.

## 4. Condicionalidades que deben revisarse

1. Retirar las condiciones de P9.1, P10.1, P10.2, P11.3, P17.2 y P40.2 junto con sus controles.
2. Revisar la transición de la antigua jefatura de hogar a la pregunta binaria de P13.
3. Revisar cómo representar en LimeSurvey la P37 obligatoria y sus alternativas; el Manual 2027 no presenta una pregunta filtro Sí/No previa. No asignar el código `G06Q91` a la pregunta nueva sin validar la estructura activa.
4. Rehacer las condiciones de la sección P39–P40 después de crear los dos bloques nuevos.
5. Validar que `G00Q91`–`G00Q94` sean consentimientos oficiales y no preguntas eliminables de la encuesta institucional.

## 5. Orden de implementación

1. Exportar la estructura actual de LimeSurvey con código, texto completo, tipo de pregunta, subpreguntas, opciones y condiciones.
2. Confirmar en la plataforma los códigos marcados como `CÓDIGO_LS_PENDIENTE` o `PENDIENTE_VALIDACIÓN`.
3. Crear una copia/versionado del instrumento 2026.
4. Editar primero eliminaciones y condicionalidades.
5. Crear las preguntas y alternativas 2027 con claves estables, sin reutilizar posiciones 2026.
6. Validar la encuesta completa contra las secciones del Manual 2027.
7. Construir el mapa PES 2027 de 172 campos y probarlo con respuestas ficticias controladas.
8. Ejecutar la auditoría estructural y de dominios antes de cualquier carga en PES.

## Estado

**ESPECIFICACIÓN DOCUMENTAL CREADA. IMPLEMENTACIÓN EN LIMSURVEY Y CARGA PES PENDIENTES.**

La decisión de eliminar, modificar o incluir contenido está respaldada por el Manual FCU 2027. Los códigos LimeSurvey anotados son candidatos observados en la clasificación 2026. La correspondencia exacta y las condiciones vigentes se deben confirmar con una exportación actual de la encuesta antes de editarla.
