# Separacion de comunicacion, analisis y auditoria 2027 P1

Politica: `COMUNICACION_ANALISIS_AUDITORIA_2027_P1-v1`. Autorizacion expresa del usuario del 2026-10-13. Sustituye la instruccion anterior de insertar estado de incorporacion en Informe_Categorias. No modifica ni regenera FCU2026.

Actualizacion posterior2026-10-13: `SEGUIMIENTO_OPCIONES_2027_P1.md` sustituye el filtro
de condiciones con0, la eliminacion de todo desglose temporal y la reescritura de
la apertura. Se recupera la correspondencia aceptada con Acumulado/Hoy por submitdate.
Lista_tokens_categorias_SI, VCM_Emprendimientos_formalizados y financiamiento son
entregas para las areas en02_SALIDAS; solo los controles internos van a05_ANALISIS.
Los apartados siguientes documentan la primera separacion y su corrida historica,
no autorizan volver a retirar las filas0 ni estos entregables del reporte vigente.

## Tres destinos para nuevas ejecuciones

- `02_SALIDAS`: `Informe_Categorias_2027_P1_<fecha>.docx` para correo colectivo, y CSV importables diario/acumulado solo cuando contienen filas listas.
- `05_ANALISIS`: `Estado_incorporacion_LimeSurvey_2027_P1_<fecha>.docx`, Excel de seguimiento, detalle de trayectorias, matricula, pendientes, comunicaciones y resultados internos en Excel. Se reutiliza el expediente de ejecucion, agregando05; no se duplican esos documentos en02.
- `04_AUDITORIA`: comprobaciones tecnicas, `CONCILIACION_AGREGADA_2027_P1_<fecha>.json` sin datos personales, `EXTRACCION_WORDS_2027_P1_<fecha>.json` en orden de parrafos/tablas y los textos `CONTENIDO_WORD_CORREO/INTERNO_*.txt`.

La recopilacion de salidas, los hashes del manifiesto y la copia integra al Escritorio incluyen05_ANALISIS solo para 2027 P1. Las ejecuciones 2026 conservan su comportamiento anterior. Ninguna salida historica se mueve, borra ni sobrescribe. Los identificadores/contactos individuales permanecen solo en analisis privado,01_ENTRADAS o .local ignorado porGit; esta gobernanza contiene reglas y agregados.

## Informe de correo y semantica de nuevo

Informe_Categorias comunica caracterizacion de **primer ingreso institucional**. Incluye saludo, alcance breve, participacion recalculada, una distribucion por jornada, las tres sedes completas, condiciones positivas relevantes y las11 alternativas de financiamiento **una sola vez**, incluso alternativas con cero selecciones. No incluye incorporacion a LimeSurvey, conciliaciones, instrucciones, motivos individuales ni rutas.

Se retiran tablas antiguas/de total repetidas cuando representan la misma poblacion, bloques sin datos y la columna **DE LOS CUALES NUEVOS**. En el codigo historico, esa columna se calculaba con `usar_ventana=True` en `_registrar_auditoria_nuevos_informe()`, por lo que significaba matriculados en ventana, no personas de primer ingreso institucional. En 2027 el TOTAL del correo se calcula exclusivamente sobre el nuevo objetivo institucional, y no se presenta una segunda columna con otro significado de nuevo. La metrica temporal permanece en auditorias historicas de ventana; no debe reinterpretarse como trayectoria institucional.

Tres conceptos distintos: primer ingreso institucional (objetivo de caracterizacion), trayectoria academica previa (fuera del objetivo, conservada internamente) e incorporaciones nuevas a LimeSurvey (personas sin token actual que pueden importarse). Generar un CSV no acredita incorporacion. Un denominador cero produce **No aplica**, nunca0/0=100%.

Actualizacion de etiquetas2026-10-13: ver `CLARIDAD_CONTROLES_2027_P1.md`. Los controles de fecha/cohorte no clasifican antiguos institucionales. Seguimiento_respuestas_encuesta conserva el universo completo y Estudiantes_pendientes_respuesta solo NO/INCOMPLETO/vacios. Las referencias a Estudiantes_pendientes y AUDITORIA_DE_LOS_CUALES_NUEVOS en corridas anteriores son historicas; no usar esos nombres ambiguos en nuevas corridas2027. No se alteran las exclusiones ni los resultados de caracterizacion.

En modo sin respuestas, Informe_Categorias comunica solamente el alcance de matricula/objetivo. No contiene resultados ni financiamiento ficticios. El estado operativo se informa en el Word separado de05_ANALISIS.

## Referencia de estilo y limites de aprobacion

Se recupera el proposito de carta y el sistema visual de:

`/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-07-15/2026_P2_172021_HITO4C_OK/02_SALIDAS/Informe_Categorias_2026_P2_20260715.docx`

La ruta literal verificada esta registrada en la conciliacion agregada de cada corrida (el nombre de OneDrive usa SanSebastián). SHA-256: `9f520a6b5f984b93c0c3eb6772d245eb5263c2aa1b2b125832170b3ce9380453`. `gobernanza/HITO_4C_Z_manifest.json` respalda esa corrida con dictamen **APROBADO_PARA_CONGELAMIENTO**. Es aprobacion funcional de la linea base; no se encontro aprobacion editorial individual del DOCX, y no se afirma una nueva.

La referencia se lee, no se sobrescribe. El builder conserva sus estilos y geometria mediante copia en memoria y sustituye solamente el contenido del cuerpo autorizado por esta tarea. No reproduce sus defectos historicos de financiacion repetida/columna nuevo ambigua. La referencia indicada por el usuario (corrida 2027 P1_090630) permanece byte-identica.

El template operativo reside actualmente en OneDriveMac. Para otra ubicacion se admite `CARACTERIZACION_PLANTILLA_CORREO` con una copia byte-identica cuyo SHA supere el control. No afirmar validacion realWindows mientras no se disponga de esa referencia y de las fuentes privadas en esa plataforma.

## Elegibilidad por historico institucional

`classify_trajectories()` lee **todo DATOSDEALUMNOS** antes de reducir la cohorte. Identifica RUT con otra carrera y ano/periodo de ingreso academico estrictamente anterior. Usa CODCARPR, equivalencias gobernadas de `gobernanza/sies/DURACION_ESTUDIOS.tsv` y nombre normalizado para no confundir variantes de una misma carrera. No usa orden de filas ni una fecha de carga/matricula anterior como prueba de trayectoria academica previa.

Un antecedente en otra carrera es valido solo con combinacion gobernada titulada, vigente o salida intermedia. Se reutilizan `_MAPA_ESTADO_OFICIAL`, `_clasificar_estado_oficial` y `_evento_academico_oficial` extraidos como funciones puras del codigo congelado. El catalogo IPSSV001, Tabla4 Seccion6, corrobora31/42 TITULADO,100/VIGENTE proceso de titulacion intermedia y101/VIGENTE titulo intermedio2. La combinacion101/VIGENTE se admite solo con etiqueta concordante, exclusivamente en el modulo nuevo 2027;100/101 ELIMINADO no se convierten por analogia en antecedentes validos. Otros estados o equivalencias ambiguas quedan **POR_REVISAR**, visibles en el detalle, sin inventar una exclusion adicional. La vigencia documental V001 es limitada; el mapa congelado y las etiquetas reales se distinguen de sus codigos auxiliares.

Fuente documental leida: `/Users/alexi/.codex/plugins/cache/created-by-me-remote/analisis-institucional-alexi/1.0.8/skills/consultar-fuentes-ipss/references/fuentes-ipss/catalogo-reportes-ipss-v001.md`, Tabla4, Seccion6.

La propia fila, misma carrera/equivalencia, duplicado tecnico o nueva matricula de la misma cohorte no constituye antecedente academico previo. La evidencia distingue esos casos. Correccion autorizada 2026-10-15: se retira el bloqueo por varias matriculas elegibles de un RUT; se agrupan personas sin elegir carrera principal y se conserva cada matricula en seguimiento. Tokens vacios/repetidos en participantes siguen bloqueando por integridad. PERSONAS_MATRICULAS_2027_P1.md reemplaza expresamente la instruccion anterior de bloquear matriculas repetidas.

Esta decision se aplica al maestro 2027 antes de atribuir respuestas y calcular categorias en el flujo con respuestas, y al mismo `eligible_students()/build_plan()` en el flujo sin respuestas. Las matriculas retiradas del objetivo quedan en el detalle completo de05_ANALISIS. No se eliminan tokens ni respuestas historicas de LimeSurvey ni se alteran archivos fuente. La participacion se recalcula con el nuevo denominador.

## Catalogo completo de sedes

`CATALOGO_SEDES_2027.json`: RE=Santiago, CO=Concepcion, PTG=Patagonia. PTG y la existencia de las tres sedes fueron confirmados expresamente por el usuario en este chat el 2026-10-13. RE/CO tambien estan respaldados por `avance_curricular/gobernanza_sede.tsv`, regla de negocio validada contra oferta academica. Patagonia no se infirio del acronimo ni de sus carreras.

El desglose se calcula sobre **el mismo objetivo del informe**. Codigos vacios/desconocidos quedan visibles y aportan su cantidad a la conciliacion; no se descartan ni se les inventa un nombre. El antiguo desglose fijo de dos sedes en `agregar_tabla_resumen_word()` deja de usarse para el correo 2027.

## Responsabilidades de codigo

- `caracterizacion_trayectorias_2027.py::classify_trajectories`: historico, equivalencias, estado/evento y evidencia de antecedentes.
- `caracterizacion_sin_respuestas.py::eligible_students` y `caracterizacion_incorporacion.py::build_plan`: filtros existentes, decision institucional compartida, correos, tokens y ventanas. Mail_Inst ausente/invalido sigue reteniendo solo la incorporacion individual.
- `caracterizacion_financiamiento_2027.py::adapted_source/filter_characterization_master/publish_communication`: adapta solo 2027 P1 en memoria; verifica anclas y las51 referencias congeladas; genera el nuevo universo antes del calculo de respuestas sin tocar caracterizacion.py.
- `caracterizacion_reportes_2027.py::build_email_report/build_internal_report`: dos publicos y propositos separados, sin repetir financiacion ni sumar denominadores distintos. La API mixta anterior `finish_word_2027` queda retirada y rechaza intentos de restaurarla.
- `caracterizacion_comunicacion_2027.py::publish_reports/publish_trajectory_analysis`: destinos, conciliacion agregada, fuentes y extraccion ordenada.
- `caracterizacion_sedes_2027.py::sede_distribution`: catalogo confirmado, cobertura completa y desconocidos.
- `caracterizacion_runtime.py::output_path/analysis_path/collect_outputs/manifest_dict`:05_ANALISIS, hashes/manifiestos y copia.05 no se habilita retroactivamente para 2026.

## Causas diagnosticadas

1. `agregar_tabla_condiciones_especiales_word()` incluye Financiacion y `agregar_tabla_financiamiento_word()` la vuelve a insertar; construir ambas duplicaba las11 alternativas.
2. `agregar_tabla_jornada_word()` exponia Nuevos, Antiguos y Total aun cuando Nuevos=Total y Antiguos=0; `TOTAL_ANTIGUOS` tenia porcentaje constante100% sin denominador.
3. `finish_word_2027()` insertaba el estado operativo al final del mismo Word de correo. La instruccion se revoca y se separa el documento.
4. `eligible_students()` y el maestro filtraban ANOINGRESO2027 por carrera sin evaluar el historico completo del RUT; cinco casos de otra trayectoria valida ingresaban indebidamente al objetivo.
5. `agregar_tabla_resumen_word()` contaba soloRE/CO:242+13=255 y omitio los7 PTG del universo262.
6. `runtime::_scan_generated_files()` solo recorria02/04. Se amplian recopilacion y manifiesto para05 exclusivamente 2027 P1; copytree ya copia todo el expediente y ahora verifica esa carpeta tambien.

## Ejecucion final y conciliacion verificada

Entrega final: corrida `2027_P1_101900`, codigo0, corte **2026-10-13**, encuesta141234. Fuentes: DATOSDEALUMNOS_11923.xlsx, tokens_141234.csv y results-survey141234.xlsx; auxiliar opcional PROMEDIOSDEALUMNOS_7804.xlsx archivado sin modificar. Los hashes exactos estan en01_ENTRADAS/manifest_ejecucion y en la auditoria privada. El comando habitual conserva sus variables y admite FECHA_REFERENCIA_PROCESO para identificar el corte; esta comprobacion uso `FECHA_REFERENCIA_PROCESO=2026-10-13` junto a las cuatro variables autorizadas. No se ejecuto el analisis anual.

| Concepto | Antes | Despues |
| --- | ---: | ---: |
| Registros de matricula del periodo conservados | 266 | 266 |
| Personas del objetivo elegible | 262 | 257 |
| Elegibles con token actual | 235 | 231 |
| Elegibles sin token actual | 27 | 26 |
| Listos para incorporar | 26 | 25 |
| Pendientes de correo institucional | 1 | 1 |
| Personas pendientes de firma, poblacion separada | 1 | 1 |
| Respuestas completas | 14 | 14 |
| Respuestas incompletas | 1 | 1 |
| Sin respuesta | 247 | 242 |
| Indice de respuesta completa | 5,3% | 5,4% |

Cinco personas se excluyen por trayectoria previa valida:2 con antecedenteTITULADO y4 VIGENTE, con una persona compartida. Union5; no sumar como6. Todas esas personas sonRE:4 ya tienen token y1 estaba ausente; ninguna tiene respuesta registrada. Se conservan los237 tokens y15 filas de respuestas fuente. El universo elegible es257 personas unicas; la matricula completa tiene266 registros/265 RUT.

Sedes del mismo objetivo: **RE/Santiago237 + CO/Concepcion13 + PTG/Patagonia7 =257**. Antes eran242+13+7=262; el Word viejo solo mostraba242+13=255. Jornadas recalculadas: Diurna12(4,7%), Online155(60,3%), Vespertina90(35,0%). Financiacion:11 alternativas,23 selecciones, sin cambio porque ninguna respuesta pertenecia a las cinco exclusiones.

Conciliaciones:262=257+5;257=231+26;26=25+1;25=25 diarios+0 acumulados+0 fecha. Exportaciones totales de participantes:237=231 objetivo+6 fuera; esos6 incluyen4 por trayectoria previa y2 por otros criterios. Firma pendiente1 no se suma a esos26. Ventana cerrada:2026-10-09 a 2026-10-12 por fin de semana/feriado; el13 queda excluido. No hay acumulado listo y no se genero CSV ni Excel acumulado vacio.

Se detecto en QA un indicador de detalle calculado inicialmente porRUT que marcaba tambien una fila no elegible de una persona elegible. La entrega final distingue **EN_UNIVERSO_OBJETIVO por indice de fila** (257 filas elegibles) de **PERSONA_EN_UNIVERSO_OBJETIVO porRUT** (258 filas de257 personas en la base completa). No son258 estudiantes. Se conserva esa fila con su estado y se probo el caso mediante regresion.

Carpeta original OneDrive:

`/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-10-13/2027_P1_101900/`

Copia integra al Escritorio, verificada porhashes:

`/Users/alexi/Desktop/Caracterizacion_2026-10-13_2027_P1_101944/`

Archivos finales:

- `02_SALIDAS/Informe_Categorias_2027_P1_20261013.docx` —2 paginas.
- `02_SALIDAS/+ Nuevos inscritos hoy_2027_P1_20261013.csv` —25 filas,14 columnas, token unico y emailexacto deMail_Inst.
- `05_ANALISIS/Estado_incorporacion_LimeSurvey_2027_P1_20261013.docx` —3 paginas.
- `05_ANALISIS/Seguimiento_incorporacion_LimeSurvey_2027_P1_20261013.xlsx` —26 pendientes elegibles, firma en hoja separada.
- `05_ANALISIS/Trayectorias_institucionales_2027_P1_20261013.xlsx` —266 filas originales del periodo y evidencia del historico completo.
- `04_AUDITORIA/CONCILIACION_AGREGADA_2027_P1_20261013.json` —solo agregados, denominadores, checks, catalogo y hashes.
- `04_AUDITORIA/EXTRACCION_WORDS_2027_P1_20261013.json` y `CONTENIDO_WORD_CORREO/INTERNO_2027_P1_20261013.txt` —parrafos/tablas en orden, contrastados con los Word finales.

## Pruebas y resguardo

**126 pruebas focalizadas pasaron** en el entornoPython3.14 usado por el comando real:17 trayectorias,15 reportes,6 separacion/carpeta/ruta/matricula-persona,10 correos,7 sin respuestas,13 incorporacion,13 runtimeaplicables,9 comandos,16 seleccionLimeSurvey y20 fuentesP2. Primero se probaron funciones aisladas; despues se ejecuto 2027 P1 real. Se mantuvieron pruebas de firma, recuperacion de correo, presencia en tokens, matriculas antiguas, fines de semana/feriados, dia actual, duplicados y salidas vacias.

Tres pruebas preexistentes de descubrimiento de rutas (default_archivo_baseMac/Windows yDesktopredireccionadoWindows) fallan tambien contra el runtime original deHEAD; se aislaron y documentaron en `.local/separacion_2027_20261013/PRUEBAS_RUNTIME_BASELINE.log`. No se ocultaron como aprobadas ni se cambiaron rutas 2026 para resolverlas. La entrega validada esMac y no certifica una ejecucionWindows.

AmbosWord finales fueron renderizados con LibreOffice empaquetado en el runtimeCodex y se revisaron **todas las cinco paginas**. La comunicacion no tiene estado de incorporacion; financiacion aparece una sola vez; no hay tablas vacias/duplicadas. El informe interno conserva bases y conciliaciones, con la tabla de fuentes completa y sin una fila aislada en una pagina final. Los PNG/PDF son QAprivado, no entregas solicitadas.

Se verificaron25 emails porTOKEN contraMail_Inst, ausencia de los cinco excluidos enCSV, unionCSV+correo pendiente=26 filas de seguimiento, firma separada,266 filas conservadas y23 selecciones contra el Excel financiero. Los30 artefactos de salidas del manifiesto se cotejaron porSHA-256 con la copia de Escritorio;05_ANALISIS esta incluido.

**281 archivos anteriores resguardados permanecen byte-identicos**, incluida la referencia del usuario. El DOCXde estilo aprobado funcionalmente conserva suhash. Las **51 referencias congeladas deFCU2026** pasaron antes/despues sin diferencias, incluido caracterizacion.py. No hubo commit/push, movimientos historicos, envio de correo ni cambios enLimeSurvey.

Evidencia privada: `.local/separacion_2027_20261013/VALIDACION_ENTREGA_FINAL.json`, logs, matriz/evidencia de trayectorias y renders. No publicar identificadores de esos expedientes. La politica queda tambien enAGENTS, comandos operativos, modo sin respuestas e indice maestro; la instruccion de mezclar estado de incorporacion en el Word de correo se reemplazo expresamente.
