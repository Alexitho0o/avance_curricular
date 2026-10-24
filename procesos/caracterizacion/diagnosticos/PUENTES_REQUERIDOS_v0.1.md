# Puentes y catálogos candidatos — priorización v0.1

Fecha de análisis: 2026-09-27. **Estado: diagnóstico para decidir el siguiente levantamiento; ningún puente queda validado ni implementado.**

## Objetivo

Identificar decisiones de catálogo compartidas detrás de las 177 **filas gobernadas en banda 2** (139 SIES y 38 CNED), sin convertir las equivalencias tentativas del diagnóstico anterior en reglas aprobadas. Separar las 556 filas en banda 3 según la evidencia de aplicabilidad al Instituto Profesional San Sebastián (IPSS) y de disponibilidad en la extracción U+ analizada.

## Fuente y alcance

- `diagnosticos/CAMPOS_GOBERNADOS_SIES_v0.1.md`: 419 filas gobernadas de ocho procesos; banda 2 = 139 y banda 3 = 258. Cada fila cita `2_Inventario_Campos` del libro SIES.
- `diagnosticos/CAMPOS_GOBERNADOS_CNED_v0.1.md`: 338 filas de S01–S17; banda 2 = 38 y banda 3 = 298. La matriz CNED inventaría el Manual INDICES **2025**; la vigencia de las estructuras 2026 no está demostrada.
- `diagnosticos/CRUCE_UPLUS_SIES_CNED_2026_v0.1.md`, revisión interna v0.1.1: correspondencia de las 67 columnas de `DATOSDEALUMNOS` y advertencias de entidad, corte y código oficial. Los resultados de U+ proceden de una extracción congelada 2026/P2, no de cortes históricos independientes.
- `gobernanza/sies/HISTORICO_SIES_MANIFEST.json` y `EXTRACCION_MATRICULA_SIES _2007_2025/salida/reporte_matricula_ip_san_sebastian.csv`: referencia agregada SIES 2007–2025. Se leyeron sin modificar. Se reportan solo conteos y nombres de campos, sin registros individuales.

## Metodología y reglas

**HECHO:** se tomó cada fila de banda 2 exactamente una vez y se agrupó por el **concepto físico del candidato U+**, aunque sus salidas tengan IDs V/K distintos. `RUT` y atributos de nombre/fecha se reúnen bajo persona/documento/rol; `CODCARPR`, `CODIGOCARRERA`, `NOMBRE_L` y las combinaciones con sede/jornada se reúnen bajo programa/oferta. Las demás fuentes físicas (`SEDE`, `JORNADA`, `ESTADOACADEMICO`, etc.) forman grupos propios. Los campos compuestos se cuentan **solo** en su grupo principal de programa: necesitan además los catálogos de sede o jornada, pero no se duplican en sus impactos. Una coincidencia de ID conceptual no fue criterio de agrupación.

**DECISIÓN de medición:** «columna» significa **fila gobernada de una estructura**, no nombre único de campo ni ID V/K único. Un mismo ID puede respaldar varias filas y etapas. «Vinculadas» es el total de filas de banda 2 del grupo; «en condición de resolverse» es un **techo condicional**, que supone disponibles y validados todos los insumos declarados como faltantes. No es una cifra de columnas ya resueltas ni autoriza carga. Las clases F, y las relaciones con entidad claramente distinta, tienen **cero** desbloqueos por convertir el candidato U+; se conservan como filas afectadas para que no desaparezcan del inventario. Las prioridades comparan magnitud potencial con evidencia faltante, sin estimar horas ni costos monetarios.

**REGLA de lectura:** A/B/C/D/F conservan el significado de la v0.1. La banda 2 incluye B con salvedad, C, D y F. Un maestro propuesto es una **HIPÓTESIS técnica** hasta comprobar cobertura, unicidad por entidad/período, procedencia y aceptación de códigos. Una tabla de referencia SIES no se convierte automáticamente en puente U+→CNED.

## Resultados: catálogos candidatos y alcance

Orden por filas **potencialmente resolubles**, de mayor a menor; los grupos con cero van al final. En cada celda SIES/CNED se informa el número de filas, seguido de los IDs conceptuales **distintos** involucrados. Los números entre paréntesis identifican filas vinculadas que **no** se desbloquean con el candidato actual. En todos los casos «desbloqueable» significa *solo si se valida lo faltante*.

| Catálogo propuesto | Columnas SIES desbloqueadas (IDs V) | Columnas CNED desbloqueadas (IDs K/X) | Estructura mínima propuesta | Evidencia disponible en el repo | Evidencia faltante | Prioridad (impacto vs. evidencia faltante) |
|---|---|---|---|---|---|---|
| **Persona, documento y rol** — candidatos `RUT`, `NOMBRE`/`NOMBRES`, apellidos, `FECHANACIMIENTO`; **39 vinculadas** | **33 condicionales**: V02, V03, V04, V05, V06, V08 | **0**; 6 vinculadas K21, K22 corresponden a rector, junta, responsable o administración, no a estudiantes U+ | Identificador de persona; tipo/número/DV de documento; nombres/apellidos/fecha de nacimiento; rol y entidad; fuente; vigencia; regla de normalización y excepción | U+ posee RUT y atributos personales; la v0.1 observó repetición de RUT y que `CODCLI` representa trayectoria | Tipo documental verificado, reglas por proceso, corte y fuente de autoridades/administradores; resolver si la persona de destino es la misma. Para CNED se necesita otra fuente, no una transformación del estudiante | **Alta por volumen, costo medio/alto**. Pilotar documento de estudiantes; no prometer las 6 CNED |
| **Maestro de programa/oferta por vigencia** — `CODCARPR`, `CODIGOCARRERA`, `NOMBRE_L` y combinaciones; **29 vinculadas** | **25 condicionales**: V11, V12, V13, V15, V16 | **4 condicionales**: K09, K10. K09 es código interno; **no** se equipara a K07/K08 | Código U+ de programa; nombre U+ solo como atributo; sede y jornada U+; institución; programa/sede/jornada/versión oficiales SIES; `CODIGO_UNICO`; IDs CNED **solo si hay correspondencia validada**; inicio/fin de vigencia; fuente/estado de aprobación; regla de unicidad y excepciones | U+ tiene `CODCARPR`/`CODIGOCARRERA` 1:1 **en esta extracción** y `NOMBRE_L`; el CSV SIES trae componentes oficiales y 83 `codigo_unico` distintos | Maestro de oferta aceptada y sus versiones; prueba `CODCARPR`→programa oficial por sede/jornada/período; código institucional; correspondencias CNED y definición de `CodigoSIES`; cortes U+ independientes. Depende de los catálogos de sede/jornada | **Muy alta estratégica, costo alto**. Es el núcleo del cruce entre reguladores; validar primero disponibilidad del maestro oficial |
| **Estado/vigencia de matrícula por corte** — `ESTADOACADEMICO`, `SITUACION`; **17 vinculadas** | **14 condicionales**: V24 | **0**; 3 vinculadas K16 son **estado del programa**, otra entidad | Estado U+; significado operacional; estado de salida por proceso; inicio/fin de vigencia; fecha de corte; precedencia de eventos; fuente y excepciones | U+ contiene ambos campos; la v0.1 identifica su semántica no homologada y ausencia de cortes históricos probados | Historial de cambios/cortes; reglas de matrícula, titulación y vigencia por proceso. Para K16, fuente de estado de programa; no usar estado académico del alumno | **Alta por volumen, costo alto** por temporalidad; las 3 CNED exigen otro catálogo |
| **Sede oficial por vigencia** — `SEDE`; **12 vinculadas** | **REVISIÓN v0.1.3 — retracta v0.1.2. HECHO, no inferencia:** V11 resuelto para SIES con `RE→COD_SEDE_SIES=2`, `CO→COD_SEDE_SIES=3` (no un valor constante). **8 condicionales pasan a 8 validadas** para esta correspondencia por valor de `SEDE_UPLUS` | **0 validadas; 4 condicionales**: K02. `idSede_CNED` sigue sin evidencia — verificado de nuevo (`grep` sin resultados en `cned/` e `indices_2025/` de `avance_curricular`); este hallazgo no lo resuelve | `SEDE_UPLUS` (`RE`/`CO`) **sí** corresponde 1:1 al componente de sede de `CODIGO_UNICO_SIES` (`RE→S2`, `CO→S3`), pero el puente `CODCARPR`+`JORNADA` → `CODIGO_UNICO_FINAL` de `PUENTE_SIES_COMPILADO.tsv` **no basta** para derivarlo: su llave omite `SEDE`, y al menos 3 `CODCARPR` (`COTENS`, `COTEIQ`, `COTFAR`) están matriculados con el mismo `COD_CARRERA`+`COD_JORNADA` en ambas sedes a la vez, por lo que el join colapsa siempre al lado Santiago. `idSede_CNED` sigue pendiente | **HECHO (fuente primaria, independiente de U+ y de `PUENTE_SIES_COMPILADO.tsv`):** `/Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/05_datos_trabajo/PREFINAL_ETAPA1_DOCENCIA02_48_COLUMNAS_CON_ENCABEZADO_20260817_110000.csv` (precarga oficial SIES, reporte 5913, `COD_SEDE`/`NOMBRE_SEDE` "no modificable según manual" — `CONTRATO_CAMPOS_ETAPA1_OFERTA_ACADEMICA_2027.tsv`) registra `COD_SEDE=2 → CASA CENTRAL (SANTIAGO)` (100 filas) y `COD_SEDE=3 → SEDE CONCEPCION` (3 filas), coincidiendo exactamente con `gobernanza_sede.tsv` (`RE→2`, `CO→3`, "validada contra oferta académica") y con los 3 `CODCARPR` distintos de `SEDE='CO'` en U+: `COD_CARRERA 91/TECNICO EN ENFERMERIA`≈`COTENS`, `114/TECNICO EN ENFERMERIA E INSTRUMENTACION QUIRURGICA`≈`COTEIQ`, `115/TECNICO EN FARMACIA`≈`COTFAR`. **Verificado además que esas 3 carreras (91, 114, 115) se ofertan simultáneamente en `COD_SEDE=2` y `COD_SEDE=3` con el mismo `COD_JORNADA`** en ese mismo archivo — confirma el mecanismo exacto de colisión que hizo que `PUENTE_SIES_COMPILADO.tsv` resolviera las 3 filas `SEDE='CO'` hacia `S2` (defecto de llave, no evidencia de que `CO≠Concepción`) | Las 82 combinaciones `CODCARPR`+`JORNADA` de `SEDE='RE'` sin match en `PUENTE_SIES_COMPILADO.tsv` siguen sin confirmarse como ausentes (posible defecto de limpieza de espacios en `JORNADA`, no revisado en esta pasada). No se identificó si existen otras carreras además de 91/114/115 con la misma colisión sede 2/sede 3. `idSede_CNED` sigue sin fuente en ningún subproyecto de `avance_curricular` revisado | **DECISIÓN:** revertir la `REVISIÓN v0.1.2` (sede SIES constante = 2): fue un error de lectura del defecto del puente `PUENTE_SIES_COMPILADO.tsv` como si fuera ausencia real de sede 3. Queda `RE→2`, `CO→3` como HECHO, validado por fuente primaria independiente (oferta académica 2027, reporte 5913). **Pendiente:** para el puente `CODCARPR`+`JORNADA`→`CODIGO_UNICO_FINAL` general (no solo sede), incorporar `SEDE_UPLUS` a la llave de join antes de reutilizarlo; `idSede_CNED` sigue condicionado. **Nota de recálculo:** este hallazgo (v0.1.2 y esta corrección v0.1.3) no fue propagado a los totales agregados de "Lectura de los totales" (129/48) más abajo en este documento — requiere una pasada aparte antes de tratar esas cifras como vigentes |
| **Nacionalidad / país por proceso** — `NACIONALIDAD`; **10 vinculadas** | **10 condicionales**: V09 | **0** | Valor U+; catálogo oficial destino; proceso; vigencia del catálogo; regla para doble nacionalidad, vacío y excepción; fuente | Campo `NACIONALIDAD` en U+ y definición de salida en inventarios SIES | Valores observados y catálogo/regla oficial aplicable a cada reporte; no asumir que el texto U+ es un código | **Media/alta**, costo medio |
| **Sexo por entidad y proceso** — `SEXO`; **10 vinculadas** | **9 condicionales**: V07 | **0**; 1 vinculada K23 es sexo de usuario en S16 Administración | Valor U+; entidad/rol; código y dominio de salida por proceso; vigencia; reglas de vacío y excepciones | U+ contiene `SEXO`; inventarios muestran dominios de salida | Equivalencia validada por proceso y entidad; fuente de usuarios CNED para S16. No trasladar sexo de estudiantes a administración | **Media/alta**, costo bajo/medio para SIES; CNED requiere otra fuente |
| **Jornada / horario de programa** — `JORNADA`; **9 vinculadas** | **6 condicionales**: V15 | **3 condicionales**: K15 | Jornada U+; programa/sede; código o denominación oficial de jornada/horario por regulador; vigencia; fuente; regla para excepciones | U+ tiene `D`/`V`/`O`; CSV SIES contiene cuatro valores distintos de `jornada` | Catálogo oficial de interpretación temporal, especialmente `O`; verificar que `Horario` CNED y jornada U+ describan la misma oferta | **Media/alta**, costo medio; dependiente del maestro de programa |
| **Año y semestre de ingreso** — `ANOINGRESO`, `PERIODOINGRESO`; **8 vinculadas** | **8 condicionales**: V22 | **0** | Trayectoria/programa U+; año; período U+; semestre oficial; fecha de vigencia; regla de ingreso original/actual y excepciones | Campos U+ presentes; la v0.1 observó período de ingreso `3` sin definición | Semántica del período `3`, correspondencia con semestre regulatorio, distinción ingreso original/actual e historial de programa | **Media**, costo medio |
| **Vías de admisión y agregación de cohorte** — `VIASDEADMISION`; **5 vinculadas** | **0** | **5 condicionales**: K39 | Vía U+; categoría oficial por año/proceso; programa y cohorte; regla de agregación; fuente y excepciones | Campo U+ `VIASDEADMISION`; salidas CNED S13/S14 inventariadas | Catálogo validado y denominaciones históricas PAES/PSU; unidad de conteo, universo, período y deduplicación. No basta un reemplazo de etiquetas | **Media**, costo medio/alto |
| **Valores de oferta y ayudas, no `ARANCELREAL`** — clase F; **14 vinculadas** | **0**; 5 afectadas V31 | **0**; 9 afectadas K35/K38 | **Dos fuentes distintas propuestas**, si proceden: tarifa oficial por programa/sede/jornada/año/tipo de valor/moneda; y catálogo de beneficios por clase/alcance/período. Mantener procedencia | U+ tiene `ARANCELREAL` individual; la v0.1 lo clasifica F frente a valor oficial de oferta | Tarifario institucional oficial y fuentes de ayudas; reglas de monto, moneda y período. **Un puente desde `ARANCELREAL` no desbloquea estas 14 filas** | **No priorizar como conversión U+**; levantar fuentes separadas |
| **Nivel de carrera/programa, no `NIVEL` del alumno** — clase C con entidad equivocada; **10 vinculadas** | **0**; 7 afectadas V20 | **0**; 3 afectadas K11 | Atributo oficial de programa por versión/vigencia dentro del maestro de oferta; dominio por regulador | U+ tiene `NIVEL` del estudiante y el CSV histórico contiene atributos de programa, sin vínculo U+ validado | Fuente de nivel/tipo de programa aceptada y vínculo por versión. Convertir `NIVEL` del estudiante no prueba nivel de la carrera | **Integrar al maestro de programa**, no crear conversión del candidato |
| **Modalidad de programa, no `MODALIDAD` escolar** — clase F; **6 vinculadas** | **0**; 6 afectadas V14 | **0** | Modalidad oficial de programa por versión y vigencia en maestro de oferta | `MODALIDAD` U+ se observó como enseñanza media | Fuente de modalidad del programa y regla de salida | **No priorizar como conversión U+** |
| **Comuna de la entidad correcta, no comuna personal/escolar** — B con salvedad; **4 vinculadas** | **0**; 4 afectadas V30 | **0** | Catálogo de ubicación por entidad (persona, sede o programa), territorio oficial y vigencia; fuente explícita | U+ tiene comuna de procedencia, actual y de colegio; v0.1 advierte mezcla de entidades | Fuente de comuna de sede/programa cuando la salida la pida; validar cada rol antes de cualquier correspondencia | **No construir un mapa por etiqueta común**; incorporar al maestro geográfico apropiado |
| **Egreso de educación superior, no egreso de enseñanza media** — clase F; **4 vinculadas** | **0**; 4 afectadas V25 | **0** | Evento de egreso de carrera, con fecha, programa/versión, estado y fuente | U+ tiene `ANOEGRESOENSENANZAMEDIA`, que describe otro nivel educativo | Fuente institucional de egreso superior y cortes; no usar año escolar como sustituto | **No priorizar como conversión U+** |

**Lectura de los totales:** las 14 agrupaciones anteriores conservan **177/177** filas banda 2 sin doble conteo. Su techo condicional suma **129** filas (113 SIES y 16 CNED); las otras **48** no se desbloquean por el candidato U+ señalado: 38 por falso equivalente/entidad distinta en grupos de cero y 10 por rol/entidad distinta dentro de persona, estado y sexo. Incluso las 129 requieren evidencia adicional; **el número de puentes validados hoy es cero**. Los IDs de la tabla son conjuntos de conceptos, no cantidades de columnas.

### Reconciliación de las firmas U+ originales

Esta tabla permite reproducir la agrupación sin listar ni resolver las 177 columnas individualmente. La «firma» es el texto de `Campo U+ candidato` en las especificaciones previas; su clase A–F no cambia. Las 22 firmas son mutuamente excluyentes **como filas de origen**; una firma compuesta se asignó al grupo principal de programa.

| Firma de candidato U+ | Grupo físico asignado | SIES | CNED |
|---|---|---:|---:|
| `RUT (D)` | Persona/documento/rol | 18 | 2 |
| `NOMBRE (B), NOMBRES (B)` | Persona/documento/rol | 9 | 4 |
| `APELLIDO PATERNO (B)` | Persona/documento/rol | 2 | 0 |
| `APELLIDO MATERNO (B)` | Persona/documento/rol | 2 | 0 |
| `FECHANACIMIENTO (B)` | Persona/documento/rol | 2 | 0 |
| `CODCARPR (C), CODIGOCARRERA (C)` | Programa/oferta | 11 | 1 |
| `NOMBRE_L (B)` | Programa/oferta | 7 | 3 |
| `SEDE (C), CODCARPR (C), CODIGOCARRERA (C)` | Programa/oferta, compuesto | 5 | 0 |
| `CODCARPR (C), CODIGOCARRERA (C), JORNADA (C)` | Programa/oferta, compuesto | 2 | 0 |
| `ESTADOACADEMICO (C), SITUACION (C)` | Estado/vigencia | 14 | 0 |
| `ESTADOACADEMICO (C)` | Estado/vigencia; entidad distinta en CNED | 0 | 3 |
| `ARANCELREAL (F)` | Valores/ayudas; falso equivalente | 5 | 9 |
| `SEDE (C)` | Sede | 8 | 4 |
| `SEXO (C)` | Sexo | 9 | 1 |
| `NACIONALIDAD (C)` | Nacionalidad | 10 | 0 |
| `NIVEL (C)` | Nivel; entidad distinta | 7 | 3 |
| `JORNADA (C)` | Jornada | 6 | 3 |
| `ANOINGRESO (D), PERIODOINGRESO (C)` | Año/semestre de ingreso | 8 | 0 |
| `MODALIDAD (F)` | Modalidad de programa; falso equivalente | 6 | 0 |
| `VIASDEADMISION (C)` | Vías de admisión | 0 | 5 |
| `ANOEGRESOENSENANZAMEDIA (F)` | Egreso superior; falso equivalente | 4 | 0 |
| `COMUNAPROCEDENCIA (B), COMUNAACTUAL (B), COMUNACOLEGIO (B)` | Comuna; entidad distinta | 4 | 0 |
| **Total** | **22 firmas → 14 grupos** | **139** | **38** |

### Histórico SIES como referencia, no como puente

**HECHO:** el manifiesto declara 20.961 registros, 2007–2025, nivel `AGREGADO_PROGRAMA_ANIO`, `SIES_VERSIONADA_NO_DINAMICA` y SHA-256 `1ae2bf5b1ac47e9ffebc0d4d9040a8fd080b42602fe3176e39b409cad4353de6`. La lectura del CSV confirmó ese hash, 20.961 filas, 53 columnas y 83 `codigo_unico` distintos. Hay 30 valores no vacíos distintos de `cod_carrera`, uno de `cod_sede`, cuatro de `jornada` y cuatro de `version`; 334 filas no informan `cod_carrera` ni `version`. Dentro del CSV, cada `codigo_unico` observado se asocia a una sola tupla (`cod_sede`, `cod_carrera`, `jornada`, `version`) y viceversa. Esto valida **consistencia interna observada**, no un catálogo oficial completo. El manifiesto llama `TOTAL_CARRERAS=83` a lo que en el CSV se observa como 83 códigos únicos; no se iguala esa etiqueta a los 30 `cod_carrera` distintos.

**INFERENCIA:** el CSV puede iniciar una **tabla de referencia SIES histórica** para verificar valores y versiones observados. **LÍMITE:** carece de `CODCARPR`, `CODIGOCARRERA`, `SEDE` y `CODCLI` de U+; solo exhibe una sede SIES mientras U+ exhibe dos códigos de sede; 334 filas tienen componentes vacíos. No prueba qué programa/sede U+ corresponde a cada código SIES, no contiene `Codcarr`/`idSede` CNED y no es una serie de snapshots U+ por corte. Por ello **no** puede usarse solo como puente ni completar automáticamente `CODIGO_UNICO` o `CodigoSIES` CNED.

## Banda 3: aplicabilidad y ausencia de fuente

**DECISIÓN de clasificación:** (a) «no aplica a IPSS» exige una exclusión expresa del campo para el instituto y el período vigente; no se infiere por palabras como “universidad” en una definición o por un valor condicional. (b) «aplicaría, pero no está en esta extracción U+» se afirma **al nivel de columna de la estructura de los ocho procesos SIES 2026/2027 entregados como vigentes**, sin afirmar que cada fila de alumno deba tener valor. La columna no se encontró entre las 67 candidatas del diagnóstico. Para CNED, el libro procede del Manual 2025 y no demuestra qué estructura rige en 2026; por tanto se mantiene «indeterminado» y no se fuerza (a) ni (b) como estado vigente. Esto no impide que sus campos puedan ser relevantes, pero exige la plantilla actual.

| Regulador / proceso o sección | (a) No aplica a IPSS, demostrado | (b) En estructura aplicable, sin candidato en esta extracción U+ | Indeterminado por vigencia o aplicabilidad | Justificación |
|---|---:|---:|---:|---|
| SIES — Titulados y Egresados | 0 | 23 | 0 | Proceso del inventario vigente; faltan candidatos en la extracción evaluada. Reglas condicionales de título/grado se conservan |
| SIES — Matrícula Pregrado | 0 | 20 | 0 | Estructura del proceso vigente; campos pueden ser condicionales |
| SIES — Personal Académico | 0 | 40 | 0 | Estructura vigente; la extracción observada es de alumnos, no de personal |
| SIES — Matrícula Extranjeros | 0 | 18 | 0 | Estructura vigente; ausencia de candidato no prueba inexistencia en otras fuentes |
| SIES — Avance Curricular | 0 | 26 | 0 | Estructura vigente; `PROMEDIOSDEALUMNOS` es fuente auxiliar no perfilada aquí como puente de estas filas |
| SIES — Infraestructura y Recursos Educacionales | 0 | 52 | 0 | Estructura vigente; extracción de alumnos no es inventario de inmuebles/recursos |
| SIES — Oferta Académica Acceso (CFT e IP) | 0 | 78 | 0 | Proceso explícito para CFT/IP; extracción carece del maestro de oferta completo |
| SIES — Oferta Académica 2027 Final | 0 | 1 | 0 | Estructura incluida entre los ocho procesos; sin candidato U+ en la v0.1 |
| **Subtotal SIES** | **0** | **258** | **0** | Clasificación de columna estructural; no equivale a obligatoriedad por registro |
| CNED — S01 Identificación y Casa Central | 0 | 0 | 11 | Manual 2025; estructura 2026 no acreditada |
| CNED — S03 Ayudas Estudiantiles | 0 | 0 | 11 | Igual límite de vigencia |
| CNED — S04 Investigación | 0 | 0 | 9 | Igual límite de vigencia |
| CNED — S05 Sede | 0 | 0 | 6 | Igual límite de vigencia |
| CNED — S06 Campus | 0 | 0 | 5 | Igual límite de vigencia |
| CNED — S07 Dependencias | 0 | 0 | 5 | Igual límite de vigencia |
| CNED — S08 Docentes | 0 | 0 | 83 | Igual límite de vigencia; datos docentes no están en la extracción de alumnos |
| CNED — S09 Origen Estudiantes | 0 | 0 | 13 | Igual límite de vigencia |
| CNED — S10 Inmueble | 0 | 0 | 10 | Igual límite de vigencia |
| CNED — S11 Biblioteca | 0 | 0 | 29 | Igual límite de vigencia |
| CNED — S12 Laboratorios y Talleres | 0 | 0 | 7 | Igual límite de vigencia |
| CNED — S13 Nuevos Programas | 0 | 0 | 12 | Igual límite de vigencia |
| CNED — S14 Evolución de Programas | 0 | 0 | 63 | Igual límite de vigencia; incluye `Codcarr` y `CodigoSIES` sin puente U+ demostrado |
| CNED — S15 Egresados y Titulados | 0 | 0 | 14 | Igual límite de vigencia |
| CNED — S16 Administración | 0 | 0 | 4 | Igual límite de vigencia; roles del portal, no estudiantes U+ |
| CNED — S17 Malla Curricular | 0 | 0 | 16 | Igual límite de vigencia |
| **Subtotal CNED** | **0** | **0** | **298** | S02 no aparece porque sus dos campos están en banda 2 |
| **Total banda 3** | **0** | **258** | **298** | **556** filas clasificadas, sin declarar exclusiones no probadas |

## Validaciones

- Banda 2 de las especificaciones: SIES 139 + CNED 38 = **177** filas, agrupadas una vez en 14 grupos. Los totales por grupo son 39 + 29 + 17 + 14 + 12 + 10 + 10 + 10 + 9 + 8 + 6 + 5 + 4 + 4 = **177**. Las filas compuestas (`SEDE`/programa/jornada) cuentan en programa/oferta y las referencias cruzadas no las suman otra vez.
- Banda 3: SIES 258 + CNED 298 = **556** filas. La suma de los subtotales por proceso y sección reproduce ambos archivos.
- SHA-256 del CSV coincide con el manifiesto. Las cuentas de `codigo_unico` y componentes fueron obtenidas del CSV, sin incorporar identificadores personales al informe.
- **No** se declaró como «no aplica» ninguna columna sin una exclusión verificable; **no** se declaró CNED 2025 como estructura vigente 2026.

## Hallazgos, riesgos y decisiones

1. **HECHO:** múltiples filas reutilizan pocos conceptos físicos U+; la mayor concentración está en persona/rol, programa/oferta y estado. **INFERENCIA:** gobernar maestros comunes puede reducir el trabajo por columna, pero solo tras probar entidad y período.
2. **HECHO:** `ARANCELREAL`, `MODALIDAD` escolar y egreso de enseñanza media son candidatos F; `NIVEL` del alumno, comuna personal/escolar y estado académico tampoco resuelven atributos de **otra entidad** mediante una simple traducción. **DECISIÓN:** no contarlos como beneficios de un catálogo U+.
3. **RIESGO:** los conteos condicionales son techo documental, no cobertura del dato ni costo de construcción. Un catálogo puede fallar por cambios de versión, cortes históricos, claves múltiples, formatos o falta de fuente de autoridades/programas.
4. **RIESGO:** la misma palabra «código», «nombre», «estado», «comuna» o «valor» agrupa entidades distintas. `Codcarr`, `CodigoSIES`, `CODIGO_UNICO` e `idSede` permanecen identificadores separados hasta validación oficial e institucional.
5. **DECISIÓN:** mantener 298 filas CNED banda 3 en estado de vigencia/aplicabilidad indeterminada; el manual 2025 no permite descartarlas ni exigirlas para 2026 por sí solo.

## Estado y próximo paso

**Estado:** priorización diagnóstica lista para revisión. No existe un puente aprobado ni una cifra de columnas efectivamente automatizables hoy. No se implementó extracción, transformación, catálogo ni carga; no se modificaron fuentes originales.

**RECOMENDACIÓN:** obtener primero el maestro institucional de oferta **aceptada** y sus versiones, junto con la evidencia de equivalencia `CODCARPR`/sede/jornada por vigencia: es la dependencia estratégica para el código único y la salida CNED. Como prueba acotada de bajo alcance, validar el catálogo de sedes (`RE`/`CO` frente a SIES y CNED) y medir unicidad y excepciones; el histórico SIES sirve para contrastar códigos, no para asignarlos. En paralelo, solicitar las estructuras INDICES vigentes de 2026 para reclasificar las 298 filas CNED y separar las fuentes de autoridades, valores oficiales, personal e infraestructura. Solo después de verificar cobertura y conflictos por período corresponde estimar el costo y elegir el orden de implementación.
