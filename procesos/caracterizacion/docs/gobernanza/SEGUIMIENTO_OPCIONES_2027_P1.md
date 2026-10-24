# Seguimiento de opciones y correspondencia aceptada 2027 P1

Politica `SEGUIMIENTO_OPCIONES_2027_P1-v2`, autorizada por el usuario el 2026-10-13.
Se recuperan apertura y proposito del correo aceptado, sin reintroducir duplicados,
porcentajes indefinidos ni controles internos en la correspondencia colectiva.

## Antes y despues

El generador anterior reemplazo toda la apertura y filtro las condiciones con total 0.
Tambien retiro el desglose temporal y envio todos los XLSX a 05_ANALISIS. Esto hizo
invisible el seguimiento aprobado y dejo la categoria heredada con codigos 2026.

La referencia preservada es Informe_Categorias_2026_P2_20260715.docx, con SHA-256
9f520a6b5f984b93c0c3eb6772d245eb5263c2aa1b2b125832170b3ce9380453. Sus tres paginas,
tipografia heredada y geometria fueron revisadas. Se conserva Estimados/as,
Junto con saludar informo..., eliminados, matricula, participacion y Detalle numerico.
La instruccion editorial anterior ("identificados para incorporar") queda
REEMPLAZADA por decision explicita del usuario del 2026-10-15: recuperar
"se incorporaron N nuevos estudiantes", eliminaciones en personas, aviso de
conflictos de RUT en el primer parrafo y "estudiantes para el periodo P" sin la
explicacion de elegibilidad en la apertura. Conservar despues el parrafo de
participacion y "Detalle numerico". Numeros y porcentajes siempre dinamicos;
el ejemplo 434/210/217/7 del usuario es de estilo, no una nueva fuente de datos.

N sigue siendo NUEVOS_DIARIOS, no la suma con acumulados ni respuestas de hoy.
La redaccion "se incorporaron" no es evidencia tecnica de importacion: el proceso
solo prepara CSV y conserva EN_LIMESURVEY segun los tokens fuente. No cambiar
estados ni marcar estudiantes como cargados por generar este correo. Verificar
la carga efectiva antes de enviar el texto con ese verbo. No cambia el universo,
el reporte interno, las tablas de seguimiento ni el proceso congelado 2026.

## Dos columnas de seguimiento

- Acumulado: selecciones registradas en la tabla canonica actual de esta encuesta,
  restringidas al objetivo elegible. Una persona se cuenta una vez por opcion.
- Hoy: las selecciones anteriores cuya submitdate corresponde al dia del reporte
  en America/Santiago. Fechas con offset se convierten; las fechas sin offset se
  interpretan con la zona local del proceso, conforme al contrato vigente.
- FECHAMATRICULA y datestamp no son fechas de envio. La ventana de matricula se
  conserva como indicador separado en el detalle privado.
- Una opcion positiva de respuesta incompleta puede estar en el acumulado;
  sin submitdate no se atribuye a Hoy. No inventar su fecha desde la ultima accion.
- Pregunta/columna ausente se informa No disponible, no 0. Filas de preguntas activas
  con 0 selecciones se conservan en el Word para seguimiento. No confundirlas con
  las preguntas retiradas del instrumento.

## Version y mapeo

Fuente: instrumento 141234 registrado el 2026-10-09 en gobernanza/instrumentos_limesurvey/2027/P1.
Se verifica inventory.json contra el manifiesto. Subpreguntas/opciones se leen de
ese modelo, no de los numeros o posiciones de 2026. La discapacidad es una matriz
de severidad: Leve/Moderada/Severa son positivas y No presento es negativa.
Se incorpora G06Q90 como detalle de condicion de larga duracion. G01Q31, G06Q66
y G01Q06 estan retiradas en esta exportacion y quedan solo en el mapa de cambios.
El Word no transforma su ausencia en ceros ni las vuelve a agregar a LimeSurvey.

VCM: G02Q95, opcion institucional AO05. Esta observacion sustituye el codigo pendiente
de pregunta independiente del registro inicial. Las cuatro opciones laborales
originales, G02Q20 y el esquema oficial PES siguen protegidos. AO05 no deriva SIT_LAB.
Otra alternativa no significa que la persona no tenga emprendimiento.

Revision v2: G02Q27 es texto libre institucional de empresa O emprendimiento,
no un nombre confirmado de emprendimiento. Retirar NOMBRE_EMPRENDIMIENTO como
etiqueta derivada; conservar EMPRESA_O_EMPRENDIMIENTO_DECLARADO literal y
ESTADO_NOMBRE_EMPRENDIMIENTO. Incluir G02Q27 en Respuestas fuente y registrar
en CONTROL_SEGUIMIENTO_OPCIONES el enunciado, filtro, origen y conteos por estado.
La seleccion AO05 no habilita G02Q27 en el instrumento archivado. Detalle y reglas:
NOMBRE_EMPRENDIMIENTO_2027_P1.md. No derivar nuevos indicadores PES desde estos datos.

## Entrega y control interno

02_SALIDAS contiene Word para correo, CSV importables y estos XLSX de uso por areas:
Lista_tokens_categorias_SI (Resumen, Detalle, Respuestas fuente y Mapa2027),
VCM_Emprendimientos_formalizados (Resumen, Emprendimientos y Respuestas fuente),
y financiamiento. Los identificadores/contactos son para uso autorizado de las
areas, no para distribuir en el correo colectivo ni publicar en GitHub.

05_ANALISIS conserva Estado_incorporacion, controles de respuestas, pendientes,
trayectorias y otras bases internas. 04_AUDITORIA conserva agregados y evidencias.
La excepcion de destino XLSX es explicita y exclusiva de 2027 P1. La decision posterior
del 2026-10-13 agrega BD_Comunicaciones_*, Consolidado_eliminados_reporte_* y
Actualmente_eliminados_matricula_en_ventana_* a 02_SALIDAS, segun
ENTREGAS_COMUNICACIONES_SEDES_2027_P1.md. Los controles restantes siguen en 05_ANALISIS.
No se aplica retroactivamente ni mueve/borra corridas anteriores.

Las columnas Acumulado/Hoy de los nuevos Excel se calculan con COUNTIFS desde el
detalle y se cotejan con conteos independientes del codigo. Las respuestas fuente
son una copia de las columnas pertinentes de los registros canonicos, sin inventar
estudiantes, respuestas ni formularios. Los modelos y vistas de revision privados quedan en .local.
Las fechas se muestran como fecha y hora local, nunca como numero serial de Excel.
Se conserva SUBMITDATE_ORIGINAL y se formatea FECHA_ENVIO en ambas hojas de detalle
y respaldo. El control acumulado de financiamiento valida la cohorte; no exige
matricula en la ventana ni se interpreta como respuestas enviadas hoy.

No cambian elegibilidad, firma, correo institucional, ventanas de incorporacion,
clasificacion de trayectorias ni cierre FCU 2026. Las fuentes y referencias originales
se conservan. Pruebas: tests/test_seguimiento_opciones_2027.py y tests/test_reportes_2027.py.

## Limite de esta validacion

El cierre es del reporte diario y sus Excel de seguimiento, no de la carga PES.
La prueba integral PES con la ultima estructura detecta RAZ_INT_6 sin coincidencia
univoca de etiqueta oficial. No se omite ese control ni se adivina su correspondencia.
La alternativa institucional AO05 no se convierte en SIT_LAB. El generador historico
registrar_emprendimiento_fcu_2027.mjs rechaza el registro v2 para no reintroducir la
instruccion antigua de crear una pregunta independiente.

## Validacion del 2026-10-13

Corrida final: 2027_P1_122146; copia Escritorio: Caracterizacion_2026-10-13_2027_P1_122232.
Termino con codigo 0, 41 archivos y 5 entregables en 02_SALIDAS. Se verificaron
125 pruebas focalizadas y 1.630 celdas de los nuevos Excel contra sus modelos,
las 15 respuestas fuente y los conteos del Word. Se revisaron las tres paginas
del correo, las tres internas y las siete hojas de los nuevos Excel.

Hay 33 elementos monitoreados, 23 selecciones de financiamiento y 2 personas que
eligieron AO05. Hoy = 0: las 14 respuestas completas se enviaron entre el 9 y el
12 de octubre, no el 13. La fila incompleta no tiene fecha de envio. No se trasladan
esas respuestas a Hoy usando la fecha de matricula ni la ultima accion.

El objetivo sigue en 257 personas (14 completas, 1 incompleta, 242 sin respuesta).
El CSV diario de 25 personas conserva exactamente su hash anterior. Los 39 archivos
de la corrida previa y las 51 referencias congeladas de 2026 no cambiaron. La
evidencia privada, incluidos los registros individuales, queda en
.local/restauracion_seguimiento_20261013; no se publica en GitHub.
