# Opcion institucional de emprendimiento formalizado

Decision registrada el 2026-10-09 por instruccion expresa del usuario.

Actualizacion del2026-10-13, version2 del registro: el LSG644 de la encuesta141234 archivado el2026-10-09 contiene **G02Q95, alternativa AO05, Tengo un emprendimiento formalizado**. Los resultados actuales contienen selecciones literales y el usuario confirma su seguimiento VCM. La instruccion inicial de una pregunta independiente se sustituye por la implementacion observada. No crear una segunda pregunta ni modificar LimeSurvey.

Revision vigente version3, 2026-10-13: se corrige la atribucion de G02Q27 a
NOMBRE_EMPRENDIMIENTO. Su texto es mixto y su filtro no incluye AO05. Se conserva
la respuesta literal como EMPRESA_O_EMPRENDIMIENTO_DECLARADO, con estado de
confirmacion separado. Diagnostico: docs/gobernanza/NOMBRE_EMPRENDIMIENTO_2027_P1.md
desde la raiz del proyecto.

## Registro y evidencia

La fuente inicial fue el usuario y la observacion PPT9. El registro canonico sigue siendo `../json/PREGUNTAS_INSTITUCIONALES_2027.json`. El ID `INST_EMPRENDIMIENTO_FORMALIZADO_2027` identifica la variable institucional, no una columna ni codigo nuevo.

Evidencia: `gobernanza/instrumentos_limesurvey/2027/P1/141234_20261009_406d959cedfd/fuentes/limesurvey_group_644.lsg` y su manifiesto SHA-256. G02Q95 es la pregunta/columna; AO05 es su alternativa, no una subpregunta fisica G02Q95[AO05]. Se mantienen intactos los LSG y las cuatro alternativas originales.

## Carga PES

- La alternativa institucional no agrega campos al esquema oficial de 172 columnas.
- No se utiliza para calcular, corregir, sustituir ni completar SIT_LAB.
- La conversion existente usa G02Q20 para tiempo completo, parcial o esporadico y G02Q95 para el caso sin trabajo. Esta regla se conserva.
- No excluir a un estudiante de la carga porque la opcion no exista en una version anterior, este sin seleccion o falte respuesta. Elegir otra alternativa no prueba ausencia de emprendimiento.
- No inferir horas, ingresos, elegibilidad o relacion del trabajo con la carrera desde la existencia de un emprendimiento formalizado.

Las cuatro categorias del manual P17, paginas 21-22 del PDF, son No trabajo actualmente, Trabajo a tiempo completo, Trabajo a tiempo parcial y Trabajo esporadicamente o en pololos. La alternativa de emprendimiento formalizado no figura en esa lista. El bloque actual de LimeSurvey es una adaptacion existente; conservarlo no equivale a afirmar que reproduce literalmente el enunciado del manual. G02Q27 es institucional y no tiene campo PES oficial.

## Estudios, KPI y comparaciones

Conservar G02Q95 y su respuesta original; usar la variable separada `INST_EMPRENDIMIENTO_FORMALIZADO` para la seleccion de AO05. Informar version, cobertura, faltantes y denominador. El reporte distingue Acumulado/Hoy por submitdate en America/Santiago; no por matricula. VCM recibe un Excel con seleccionados, respuesta literal, codigo y contactos institucionales.

G02Q27 pregunta "¿En qué empresa trabajas o como se llama tu emprendimiento?".
Es texto libre institucional, no identifica exclusivamente un emprendimiento.
EMPRESA_O_EMPRENDIMIENTO_DECLARADO conserva ese texto sin reinterpretarlo.
ESTADO_NOMBRE_EMPRENDIMIENTO distingue NO_CONFIRMADO_PREGUNTA_MIXTA,
SIN_RESPUESTA_G02Q27 y COLUMNA_AUSENTE. No usar la columna NOMBRE_EMPRENDIMIENTO,
ni fuentes administrativas de empresa como sustituto. El vacio no implica negativa
ni inexistencia. El instrumento archivado habilita G02Q27 solo con AO01/AO02 de
G02Q95, excluyendo AO05. No afirmar que la persona omitio una pregunta que pudo
no haberse mostrado. Un eventual cambio del formulario requiere nueva version y
no resuelve automaticamente el significado de los textos anteriores.

No reconstruir retrospectivamente esta variable con las respuestas de situacion laboral de 2026 o anos anteriores. La ausencia de la pregunta en otra version significa que no fue medida. Cualquier comparacion debe documentar equivalencia de contenido y diferencias de cobertura. No mezclar sus resultados con el indicador oficial SIT_LAB.

## Comprobaciones

El auditor comprueba los controles laborales originales y permite exclusivamente la extension AO05 registrada. Rechaza extras distintos, duplicados o texto cambiado. No reclasifica toda G02Q95 como institucional por esta opcion. El adaptador PES impide usar AO05 en un mapeo oficial; si falta SIT_LAB no lo fabrica desde emprendimiento. Las versiones anteriores sin AO05 quedan identificadas como opcion no medida en esa version.

Los informes de auditoria y las especificaciones nuevas incluyen la identidad y el SHA-256 del registro usado. Las guias futuras incorporan la decision sin reescribir las hojas RAW historicas. FCU 2026 permanece congelado.
