Fase 4/4 · Hito 3/3

# Prompt actualizado de retención intermedia IPSS 162

Documento derivado: conserva íntegramente el prompt autorizado a continuación. Las instrucciones adicionales se incorporan después como adendas, sin sobrescribir el original ni alterar retroactivamente sus resultados o reglas. Fecha de preparación: 2026-10-21.

## Prompt original autorizado — copia íntegra

Continúa autónomamente el análisis de retención intermedia IPSS 162 hasta completar los cuatro pasos indicados abajo. Ejecuta el trabajo, no entregues solamente un plan.

## Objetivo

Cerrar, hasta donde permita la evidencia disponible, la revisión de retención intermedia de:

- Cohorte de ingreso 2024, observada en los cierres 2025-T2 y 2025-T3.
- Cohorte de ingreso 2025, observada en los cierres 2026-T2 y 2026-T3.

Debes verificar las bases candidatas existentes, revisar las 20 personas que tenían problemas de identificación y generar una nueva versión del Excel con resultados comprobados y pendientes visibles.

## Acceso y contexto técnico

Repositorio principal local:
`/Users/alexi/Documents/GitHub/avance_curricular`

Rama de trabajo: `feature/ire-2026`.
Último HEAD verificado: `80ca13a5a249a1a2bd53a699f5f73689b1f53040`.

Repositorio de referencia:
`/Users/alexi/Documents/GitHub/CARACTERIZACIÓN`

Antes de trabajar:

1. Comprueba acceso real a repositorios y archivos. No afirmes estar conectado sin verificarlo.
2. Registra rama, HEAD, remotos y cambios pendientes.
3. Lee `agent.md`, los AGENTS.md aplicables, `PROYECTO_IPSS.json` y las instrucciones de gobernanza pertinentes.
4. Respeta la integración de Caracterización en el repositorio principal cuando así lo indiquen sus contratos.
5. No cambies ramas ni integres commits ajenos.

El Excel y su manifiesto se publicaron mediante una rama separada para evitar subir otros commits locales:

- Repositorio: `https://github.com/Alexitho0o/avance_curricular`
- Rama: `feature/retencion-escenario-80-20261021`
- Commit: `b0a0bff9ba70ea8344a258f744960cef8080e04b`

Los diagnósticos locales posteriores y las bases individuales no deben suponerse publicados en GitHub.

## Archivos que debes leer primero

### Excel vigente

`/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_100654/RETENCION_INTERMEDIA_IPSS_ESCENARIO_80_20261021_100654.xlsx`

SHA-256:
`12bf04615558554a30275b4ee8c6197617e7195c059c4c87277a91c4697e719d`

Manifiesto:
`/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_100654/MANIFEST_ESCENARIO_80_EXCEL.json`

Hojas actuales:

- Resumen
- Por_carrera
- Fuentes_y_alcance
- Bases_por_confirmar
- Escenario_80

### Diagnóstico más reciente de las 20 personas

Carpeta:
`/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_115156_llaves_20_codcli/`

Lee:

- `DIAGNOSTICO_LLAVES_20_CODCLI.md`
- `RESULTADOS_AGREGADOS.json`
- `MANIFEST_DIAGNOSTICO.json`

Esta versión sustituye el borrador de las `20261021_103508`.

### Base anual gobernada

`/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`

Hoja: `BASE_RETENCION_MU`.

SHA-256:
`19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`

Contiene datos individuales. Úsalos únicamente para el análisis privado; no los incorpores al Excel agregado ni a Git.

## Resultados ya comprobados: conservar

Denominadores actuales, que NO debes cambiar:

- Cohorte 2024: 558 estudiantes.
- Cohorte 2025: 1.150 estudiantes.
- Ejercicio separado de ingresos 2025-T2: 222 estudiantes.
- Ejercicio separado de ingresos 2025-T3: 124 estudiantes.

Presencias actualmente comprobadas:

| Cohorte | Cierre | Localizados | Estado observado |
|---|---|---:|---|
| 2024 | 2025-T2 | 1 | 1 VIGENTE |
| 2024 | 2025-T3 | 325 | 317 VIGENTE |
| 2025 | 2026-T2 | 2 | Sin campo de estado académico en el listado |
| 2025 | 2026-T3 | 0 con llave comparable | Cobertura pendiente |

Estas presencias todavía no permiten cerrar las tasas intermedias.

El ejercicio separado de ingresos 2025-T2/T3 buscados en MU2026 mantiene:

- T2: 74 con VIG=1 sobre 222 → 33,33%.
- T3: 48 con VIG=1 sobre 124 → 38,71%.

No confundas este seguimiento anual con los cuatro cierres intermedios.

### Las 20 personas sin llave comparable

Ya se verificó:

- Las 20 están incluidas en el denominador 1.150.
- MU2025 las informa como `TIPO_DOC=P`, con DV vacío.
- El cruce anterior solo construía llave de listado para `TIPO_DOC=R`.
- Se encontró una correspondencia explícita entre N_DOC e identificador UMAS en `IPSS_Procesamiento.xlsx`, hoja `2025_carga`, columnas J —RUT—, BU —N_DOC— y BV —DV—.
- Se recuperó CODCLI para 18 personas: 17 tienen un CODCLI observado y una tiene dos. Son 19 CODCLI, pero 18 personas.
- Una persona se recuperó por CODCLI aunque cambió su identificador documental entre respaldos.
- Dos siguen sin CODCLI identificado: una de Ingeniería en Informática y una de Técnico en Programación y Análisis de Sistemas.
- En DatosAlumnos_12112, 14 de las 18 personas identificadas tienen alguna matrícula VIGENTE. Eso NO demuestra vigencia al cierre T2/T3.
- Los 18 CODCLI recuperados no aparecen en los dos listados parciales 2026-T2/T3 recibidos.
- No se ha acreditado deserción.

No sumes estas 18 personas al denominador: ya estaban consideradas.

## Fuentes candidatas existentes

Los cuatro archivos recibidos están en `/Users/alexi/Downloads/cierre/`:

- `Matrícula T2_2025 2.xlsx`
- `Matrícula T3_2025 2.xlsx`
- `Matrícula T_2_13_07_2026.xlsx`
- `Matrícula_T3_02_10_2026.xlsx`

Respaldo candidato para 2026-T2:

`/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx`

SHA-256:
`b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`

Respaldo candidato para 2026-T3:

`/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx`

SHA-256:
`5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`

Base 12112 utilizada en la revisión posterior:

`/Users/alexi/Desktop/Caracterizacion_2026-10-20_2027_P1_082504/01_ENTRADAS/DATOSDEALUMNOS_12112.xlsx`

SHA-256:
`fdd47d99b934479f39d8db6d00eceb40714d3b8c7baa1e3a89a9288b2b8bc471`

Su antigua ruta en Downloads ya no existe. La copia localizada tiene el mismo hash gobernado.

Estas fuentes son candidatas o respaldos observados: sus nombres, fechas de modificación o fechas de ejecución NO acreditan por sí solos la fecha efectiva del cierre.

## Ejecuta estos cuatro pasos

### 1. Validar cobertura y fecha de los cierres

Revisa los manifiestos, inventarios, scripts, respaldos y notas ya existentes.

Para cada cierre determina:

- Archivo y hoja aplicables.
- Fecha efectiva que representa, si está acreditada.
- Cohortes incluidas y filtros del extractor.
- Si contiene toda la matrícula pertinente o solo ingresos del período.
- Si los estados corresponden al cierre o a una extracción posterior.

Busca primero en las fuentes existentes. No solicites nuevamente archivos sin revisar los respaldos disponibles.

### 2. Revisar las 14 personas con alguna matrícula VIGENTE

Sigue los CODCLI recuperados entre fuentes comparables.

Comprueba si existe evidencia fechada de su matrícula y estado en cada cierre correspondiente. Conserva todas las matrículas de una persona y controla duplicados.

No extrapoles el estado observado en octubre a julio u otra fecha. No conviertas directamente ESTADOACADEMICO en VIG SIES ni presentes esos 14 como retenidos sin acreditar población, período y regla aplicable.

### 3. Resolver los dos CODCLI pendientes

Busca en respaldos institucionales y fuentes gobernadas compatibles.

Utiliza correspondencias explícitas de identificadores. No inventes CODCLI, no lo decodifiques por su patrón y no hagas cruces aproximados por nombre, sexo o nacimiento.

Si no aparecen, documenta exactamente qué se revisó y qué falta. No los retires del denominador ni los clasifiques como desertores.

### 4. Generar una nueva versión del Excel

Conserva el original y crea una nueva carpeta con timestamp bajo:

`/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/`

En la nueva versión:

- Actualiza las llaves resueltas y pendientes.
- Actualiza presencias solamente cuando exista evidencia verificable.
- Calcula tasas intermedias únicamente para cierres con cobertura y estado acreditados.
- Donde falte evidencia, muestra “Pendiente”, con el motivo; no uses cero como sustituto.
- Mantén los denominadores 558, 1.150, 222 y 124.
- Conserva colores, tablas, filtros y fórmulas existentes.
- Mantén `Escenario_80` separado: sus universos hipotéticos no sustituyen los actuales.
- Incluye una hoja sencilla de revisión agregada de llaves, cierres y pendientes.
- Usa fórmulas vivas y trazables para tasas, totales y diferencias.
- No incorpores identificadores individuales al libro de entrega.
- Genera una copia idéntica en el Escritorio y comprueba su hash.
- Crea un manifiesto con entradas, hojas, hashes, método, validaciones y pendientes.

## Gobernanza y autonomía

Clasifica las afirmaciones:

A: definición oficial.
B: dato observado.
C: implementación o cálculo.
D: decisión interna.
E: hipótesis o pendiente.

No modifiques fuentes originales, reglas históricas ni el motor anual de retención. No equipares automáticamente períodos T1/T2/T3 con semestres SIES. La regla anual SIES no define por sí sola una tasa intermedia T2/T3.

No hagas commit, push, merge ni PR: la autorización anterior fue exclusiva del Excel y manifiesto del escenario de 80 casos.

No publiques datos individuales. Los cruces se ejecutan en memoria o en una ruta privada ya autorizada y excluida de Git. Las salidas compartibles serán agregadas.

Trabaja autónomamente hasta producir el punto 4. Si una comprobación queda bloqueada por falta de evidencia, regístrala como E y continúa con lo independiente. No completes vacíos mediante supuestos ni declares una tasa cerrada para terminar el encargo.

Antes de entregar, recalcula las fórmulas, revisa errores y compara la nueva versión con el original para detectar cambios no autorizados. Si no puedes ejecutar alguna validación, decláralo expresamente.

## Entrega final

Devuelve:

1. Ruta del nuevo Excel y su copia idéntica en el Escritorio.
2. Tabla de los cuatro cierres: cohorte, denominador fijo, presencias, vigentes acreditados, tasa o “Pendiente”, fuente y clasificación.
3. Resultado de las 20 personas: identificadas, pendientes y qué se pudo demostrar sobre su continuidad.
4. Qué cambió frente al Excel anterior y por qué.
5. Pendientes exactos para cerrar cada T2/T3.
6. Dictamen QA, hashes y rama/HEAD antes y después.
7. Confirmación de originales y denominadores intactos, sin commit ni push.

---

## Adenda 1 — Trazabilidad de cuatro fases y tres hitos

Esta adenda organiza el trabajo y sus evidencias. No modifica los denominadores, las reglas históricas, la definición de los cierres ni las restricciones del prompt original.

Cada actualización de progreso y cada entrega debe comenzar literalmente con `Fase X/4 · Hito Y/3`, sustituyendo X e Y por la fase e hito que se está comunicando. Si una entrega consolida varios hitos, comienza con el hito de entrega y detalla el estado de los restantes en la bitácora.

| Fase | Hito | Trabajo y evidencia exigida |
|---|---|---|
| 1. Acceso, reglas y fuentes | 1/3 | Comprobar acceso; registrar rama, HEAD, remotos y cambios pendientes; leer contratos y gobernanza. |
| 1. Acceso, reglas y fuentes | 2/3 | Auditar reglas internas IPSS y externas SIES, titulados sin rematrícula, duración formal y nivel teórico frente a avance real, egreso y titulación fechada; aplicar la adenda de alcance sin inventar equivalencias. |
| 1. Acceso, reglas y fuentes | 3/3 | Construir matriz de fuentes, hojas, hashes, cobertura, temporalidad y pendientes de los cuatro cierres. |
| 2. Revisión de las 14 personas | 1/3 | Seguir llaves explícitas de las 14 personas con algún VIGENTE observado y conservar todas sus matrículas; controlar duplicados. |
| 2. Revisión de las 14 personas | 2/3 | Contrastar la temporalidad de matrícula y estados entre respaldos comparables; separar observación fechada de estado efectivo al cierre. |
| 2. Revisión de las 14 personas | 3/3 | Documentar conclusiones agregadas sobre continuidad demostrada y no demostrada, con clasificación A–E y pendientes. |
| 3. Resolución de las dos identidades pendientes | 1/3 | Inventariar respaldos institucionales y correspondencias explícitas pertinentes para las dos personas. |
| 3. Resolución de las dos identidades pendientes | 2/3 | Resolver cada CODCLI mediante evidencia explícita o documentar la no resolución y la evidencia faltante. |
| 3. Resolución de las dos identidades pendientes | 3/3 | Conciliar las 20 personas, distinguiendo personas, CODCLI y matrículas; conservar su inclusión en el denominador 1.150. |
| 4. Excel, validación y entrega | 1/3 | Generar la nueva versión agregada del Excel, con fórmulas, revisión de llaves/cierres/pendientes y Escenario_80 separado. |
| 4. Excel, validación y entrega | 2/3 | Recalcular, revisar errores y presentación, comparar con el original, verificar privacidad y denominadores; declarar validaciones no ejecutadas. |
| 4. Excel, validación y entrega | 3/3 | Completar manifiesto, copia idéntica en Escritorio y hashes; registrar Git antes/después y entregar los siete puntos originales. |

Mantén una bitácora que contenga, para cada fase/hito: **estado, evidencia, salida y pendientes**. Añade fecha/hora real de la anotación y clasificación A–E cuando corresponda. Los estados deben distinguir trabajo ejecutado y validado, trabajo en curso y comprobación pendiente por evidencia insuficiente.

No inventes hitos retrospectivos, fechas de ejecución ni validaciones. Si esta estructura se incorpora cuando ya existe trabajo realizado, regístralo como evidencia previa vinculada al hito, indicando cuándo se incorporó a la bitácora. No presentes una clasificación posterior como seguimiento contemporáneo de la ejecución. Un hito puede completar la revisión y conservar una conclusión E pendiente; eso no cierra una tasa ni demuestra continuidad.

Conserva la prohibición de modificar el motor anual, las fuentes originales y las reglas históricas. No cambies rama ni ejecutes commit, push, merge o PR. Este documento derivado no amplía esas autorizaciones.

## Adenda 2 — Retención interna IPSS, SIES y titulados sin rematrícula

Solicitud adicional del usuario, conservada literalmente:

> agrega también no recurrido si es que está escrito en las reglas de negocio en el proyecto complementos y skill que el nivel del estudiante debe presumir cuanto están matriculados en carreras de acuerdo a la duración informada en la oferta académica en matrícula unificada en titulados en caracterización y/o avance curricular que si no se matriculó al año siguiente por estar titulado no cuenta como retención o deserción, esto lo debemos gobernar y definir cuando volvamos a tener conexión por mientras analiza la diferencia entre ambos conceptos en los complementos y skill para luego gobernarlo en el proyecto o entenderlo para aplicarlo o revisar si es que ya se aplicaba esa diferencia conceptual importante cuando analizamos de manera interna la retención. (osea sin aplicar las reglas de sies) sino que aplicando reglas internas de negocio (se supone que gobernamos en complementos skill y los proyectos de github reglas de negocio y que existían dos internas propias de ipss y externas de sies presentes en los manuales de cada proceso)

Alcance de ejecución transmitido para esta ampliación:

> Incorpora el alcance adicional del usuario antes de cerrar indicadores: audita manuales, contratos, código y pruebas para distinguir retención interna IPSS de SIES y el tratamiento de titulados sin rematrícula. Revisa duración formal por oferta/plan y nivel teórico versus avance real, egreso y titulación fechada. No infieras titulación por duración cumplida ni conviertas ausencia en deserción. Preserva denominadores 558, 1150, 222 y 124; documenta decisiones de denominador pendientes sin alterar tasas históricas. Si no existe regla implementada, documenta la propuesta y pendientes con clasificación D/E, sin presentar una decisión ambigua como aprobada. Puedes reflejar la distinción acreditada en la nueva entrega agregada, manteniendo fuentes originales y motor anual intactos.

Aplica esta ampliación dentro de los hitos existentes, sin crear retrospectivamente trabajo realizado:

1. En **Fase 1/4 · Hito 2/3**, consulta las habilidades y complementos pertinentes disponibles, los manuales por proceso/año, contratos, código y pruebas. Registra qué distingue efectivamente las reglas internas IPSS de las reglas externas SIES, qué tratamiento de titulados sin rematrícula ya está implementado y qué sigue siendo propuesta. La disponibilidad de una habilidad o el nombre de una regla no prueba implementación.
2. Distingue **duración formal de oferta/plan**, **nivel teórico**, **avance académico real**, **egreso** y **titulación fechada**. Registra fuente, unidad, año/versión y alcance de cada concepto. La duración cumplida o el nivel teórico no acreditan titulación; no sustituyen avance real ni fecha de título. La falta de rematrícula tampoco acredita por sí sola la causa de salida.
3. En **Fase 2/4 · Hitos 2/3 y 3/3**, contrasta las fechas y reglas acreditadas antes de atribuir continuidad o una salida por titulación. Mantén separados el estado observado y la interpretación interna aplicable. No conviertas automáticamente una salida por titulación en deserción ni uses una regla interna como definición SIES.
4. En **Fase 4/4 · Hitos 1/3 y 2/3**, refleja únicamente distinciones y resultados acreditados en la entrega agregada. Si falta una regla implementada o una decisión de denominador, registra la propuesta y la evidencia pendiente como **D/E**, sin cambiar 558, 1.150, 222 y 124 ni las tasas históricas. Una propuesta documentada no es una regla aprobada ni aplicada.
5. No interpretes la expresión literal **“no recurrido”** como categoría técnica sin evidencia. Conserva la expresión en la solicitud y documenta cualquier significado pendiente en lugar de inventarlo.
6. Esta ampliación permite auditar y documentar el alcance conceptual y reflejar lo acreditado en la nueva entrega. Mantiene intactos fuentes, reglas históricas y motor anual. No autoriza cambios de rama, commit, push, merge o PR.

## Adenda 3 — Origen del seguimiento solicitado

Última solicitud del usuario, conservada literalmente:

> en qué etapa vas? el prompt separaba fases e hitos trazables, si no fue así actualízalo con las nuevas solicitudes que incorporé, debes ir a medida que avanzas partir con fase X/X hito x/x

El prompt original enumera cuatro pasos. La Adenda 1 formaliza su seguimiento en cuatro fases con tres hitos cada una, sin afirmar que esa estructura ya estuviera escrita ni que se hubiera ejecutado o registrado antes de esta actualización. Usa el prefijo `Fase X/4 · Hito Y/3` en adelante y conserva una bitácora verificable.


## Addenda de reanudación: cierre exclusivamente local

Fase 4/4 · Hito 3/3. Inspeccionar finalize.py y las salidas existentes antes de ejecutar para evitar duplicados. Completar localmente manifiesto, bitácora, informe y esta copia del prompt en 20261021_133221. Comprobar Git final y los hashes del libro y su copia de Escritorio. No subir ni transferir archivos a Library ni a otros servicios externos. Conservar tasas pendientes, ausencia de validación Excel nativo y limitación de suite completa por unidecode. No repetir el análisis validado salvo verificaciones necesarias; no modificar fuentes, motor anual, rama ni realizar commit, push, merge o PR. Entregar los siete puntos con rutas locales verificadas y pendientes sustantivos explícitos.


## Addenda posterior: adjuntos autorizados en Library

Fase 4/4 · Hito 3/3. Después de completar el cierre local, el usuario autorizó explícitamente subir a su Library de ChatGPT únicamente el Excel agregado y este prompt actualizado para adjuntarlos en la conversación. Esta autorización sustituye la restricción anterior solo para esos dos archivos. Conservar copias locales, verificar ausencia de identificadores individuales y utilizar exclusivamente el flujo soportado de Library; no subir bases ni otros archivos. Confirmar nombres e IDs reales; comprobar resultados inciertos antes de repetir. Ante una nueva denegación, detener esa transferencia e informar el motivo.
