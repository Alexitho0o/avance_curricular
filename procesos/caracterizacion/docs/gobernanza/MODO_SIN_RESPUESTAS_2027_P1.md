# Operacion 2027 P1 antes de recibir respuestas

Decision expresa del usuario: la encuesta 2027 P1 aun no tiene respuestas y debe entregar listas operativas. Fecha de registro: 2026-10-09.

Actualizacion 2026-10-13: las fuentes actuales de la encuesta 141234 contienen respuestas y el comando usa el flujo normal. El incidente Mail_Inst y su auditoria privada se documentan en `INCIDENTE_MAIL_INST_2027_P1_20261013.md`. La confirmacion historica no autoriza usar el modo sin respuestas sobre resultados con filas. Politica vigente desde la autorizacion posterior del 2026-10-13: correo ausente/invalido no detiene la ejecucion; se separa de los listos, se conserva en seguimiento y se informa en el Word INTERNO de05_ANALISIS. El Word de correo es Informe_Categorias, sin estado de incorporacion ni resultados/financiamiento ficticios. El universo usa la misma regla de primer ingreso institucional que el modo con respuestas. Ver `POLITICA_INCORPORACION_CORREO_2027_P1.md`.

## Funcionamiento

El mismo comando `procesar_financiamiento_diario.sh 2027 1` selecciona la encuesta 141234. Si resultados tiene cero bytes o es un libro valido sin registros, los participantes no muestran completed y no hay respondientes historicos, ejecuta `caracterizacion_sin_respuestas.py`.

Este modo registra SIN_RESPUESTAS_CONFIRMADAS y no crea respuestas de ejemplo, cabeceras ficticias de resultados ni porcentajes de financiamiento. El archivo original vacio se conserva como evidencia. Un Excel corrupto no vacio o participantes con respuestas completadas sigue bloqueado. Cuando aparecen filas en resultados, el ejecutor vuelve al flujo normal.

Las listas se derivan de matricula y tokens reales. Los filtros son ano/periodo de matricula, ANOINGRESO=2027, firma SI, ESTADOACADEMICO VIGENTE, exclusion de TITULADO APROBADO, programas y tokens administrativos. El catalogo, normalizador RUT y ventana diaria se consumen desde sus reglas existentes: se extraen solo funciones puras y constantes del codigo congelado, sin ejecutarlo ni modificarlo. Clasificacion de pendientes, programas y titulados usa sus modulos compartidos.

La ausencia de respuestas no cambia la elegibilidad. Un vigente con token permanece pendiente de responder pero no se agrega otra vez al CSV de participantes nuevos. Las listas de estudiantes conservan Responden=NO y EN_LIMESURVEY. Correccion autorizada 2026-10-15: varias matriculas elegibles de un RUT NO bloquean. Se conserva cada matricula, se cuenta una persona por RUT y se publica seguimiento con aviso en el Word. Solo los tokens vacios/repetidos de la fuente de participantes mantienen el bloqueo de integridad. Contactos sin correo institucional se conservan como pendientes no exportables. Politica: PERSONAS_MATRICULAS_2027_P1.md.

Correccion de correo registrada el 2026-10-09: el campo email de los CSV de incorporacion procede exclusivamente de Mail_Inst. MAIL personal no es una alternativa ni un fallback. La politica inicial de bloqueo global es historica: desde la autorizacion del 2026-10-13, si falta un correo valido, no exportar a ese estudiante y conservarlo en seguimiento, sin detener a los demas. El mismo control se aplica al preflight de 2027 P1 cuando ya existen respuestas, para impedir el fallback del codigo historico sin modificar el cierre 2026. El espejo Excel declara EMAIL_PARA_LIMESURVEY y FUENTE_EMAIL_LIMESURVEY.

Version corregida: ejecucion 2027_P1_134921, copia de Escritorio Caracterizacion_2026-10-09_2027_P1_134928. Los 236 correos de los CSV diario y acumulado se compararon por TOKEN contra Mail_Inst de la fuente. No usar los CSV de la primera corrida 133242 para incorporacion: conservan la version anterior con prioridad a correo personal. Validacion: docs/gobernanza/VALIDACION_CORREOS_INSTITUCIONALES_20261009.json.

Cada corrida sin respuestas genera ademas Correo_resumen_matricula_2027_P1_<fecha>.txt, con matricula, vigentes, eliminados, firma, jornadas y pendientes de incorporacion. Omite las secciones de respuestas, categorias especiales y financiamiento. El texto queda listo para el envio manual del usuario; el programa no envia correos.

## Salidas

- Lista_participantes_LimeSurvey: participantes actualmente exportados por LimeSurvey, separados de la matricula objetivo.
- Estudiantes_matriculados_Periodo: universo vigente elegible del ano/periodo. Seguimiento_respuestas_encuesta conserva todos los elegibles; Estudiantes_pendientes_respuesta contiene NO/INCOMPLETO/vacios y excluye SI. En modo sin respuestas ambos tienen el mismo universo, con Responden=NO. Ambos se conservan en05_ANALISIS. No generar el archivo ambiguo Estudiantes_pendientes para nuevas corridas2027. Politica: CLARIDAD_CONTROLES_2027_P1.md.
- Nuevos inscritos hoy: CSV de 14 columnas con matriculas sin token dentro de la ventana cerrada diaria.
- Acumulados no incorporados: CSV solo cuando existen matriculas anteriores a la ventana listas para incorporar; el Excel de seguimiento se genera solo si contiene pendientes y conserva todos los motivos. El espejo incorpora fecha de matricula, fecha de ejecucion y BRECHA_DIAS.
- Fechas posteriores a la ventana o invalidas: auditoria separada. Conservadas en la lista de pendientes; no enviadas como matriculas de ayer ni como rezagos anteriores.
- ESTADO_ENCUESTA: estado, fuentes, reglas, conciliacion y disponibilidad de analisis de respuestas.

Las salidas se archivan y copian al Escritorio con el runtime existente. El conteo del terminal distingue salidas operativas y auditorias. Las exclusiones diagnosticas pueden superponerse y no deben sumarse como categorias disjuntas.

## Validacion real del 2026-10-09

Ejecucion `2027_P1_133242`, finalizada con codigo 0. Copia en Escritorio `Caracterizacion_2026-10-09_2027_P1_133252`.

Matricula del periodo: 243 registros. Vigentes elegibles: 240. Excluidos por estado/situacion: 3. Participantes exportados de LimeSurvey: 1, sin coincidencias con los vigentes elegibles. Respondientes: 0. Pendientes: 240. CSV diario: 17. CSV acumulado y espejo: 219. Fechas posteriores a la ventana: 4. Conciliacion: 17 + 219 + 4 = 240. Diario y acumulado no tienen tokens repetidos ni interseccion y ambos tienen 14 columnas.

Pasaron 5 pruebas del modo sin respuestas, 9 de comandos, 20 de fuentes P2 y 16 de seleccion LimeSurvey. Los libros reales se abrieron y sus cantidades se conciliaron. La copia de Escritorio fue verificada por el runtime. FCU 2026 conserva sus 51 archivos congelados.

Los datos individuales se conservan en las carpetas de ejecucion, no se incorporan a Git. Este documento registra metadatos y reglas. El codigo nuevo permanece local hasta su publicacion en GitHub.
