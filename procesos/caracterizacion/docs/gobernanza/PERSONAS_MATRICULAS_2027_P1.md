# Personas y matriculas: operacion 2027 P1

Decision del usuario, 2026-10-15: corregir el bloqueo, recuperar seguimiento y aviso
en Word, contar una sola vez cada RUT sin perder sus matriculas y no tocar 2026.
Politica: PERSONAS_MATRICULAS_2027_P1-v1.

## Incidente y sustitucion de regla

`eligible_students()` rechazaba cualquier TOKEN repetido en matricula elegible.
El resolutor invocaba esa funcion antes de iniciar el pipeline. Por eso no se
alcanzaba la exportacion historica de conflictos ni el Word. El builder nuevo
del correo tampoco habia conservado el aviso de multimatricula.

Se reemplaza expresamente la instruccion de bloquear duplicados elegibles de
SEPARACION_COMUNICACION_ANALISIS y MODO_SIN_RESPUESTAS. Los tokens vacios o
repetidos en la fuente de participantes, los problemas estructurales y las
conciliaciones inconsistentes siguen bloqueando. Varias carreras de un mismo
RUT no demuestran un error ni una trayectoria institucional anterior.

## Unidades y reglas

- `eligible_students` conserva TODAS las filas elegibles. Las reglas existentes
  de cohorte, estado/situacion, firma, programas, administrativos y trayectoria
  anterior no cambian.
- `IncorporationPlan.eligible_enrollments`: una fila por matricula fuente.
  `eligible`: una fila por TOKEN (RUT normalizado). Se conservan indices/fila
  Excel fuente, cantidad, codigos y nombres de todas las carreras. No se elige
  primera carrera, mayor version, mayor arancel ni matricula mas reciente.
- La vista de persona conserva valores iguales; valores distintos se presentan
  separados por ` | `. Esto incluye CODCLI, CODCARPR, NOMBRE_L, SEDE y JORNADA.
  Una combinacion de sedes/jornadas aparece separada en los desgloses, nunca
  se atribuye a una sede principal ni se suma dos veces. Comunicaciones conserva
  esos casos en la base general para revision, sin asignarlos arbitrariamente
  al archivo de una sede. El catalogo SIES sigue aplicado al detalle por matricula.
- RUT mantiene una representacion normalizable (no se concatenan variantes).
  La fila indice de la vista solo es un ancla tecnica: no una carrera elegida.
- Con FONOACTUAL distintos no seleccionar uno ni concatenar digitos: dejar el
  contacto unico vacio y conservar FONOACTUAL_ORIGINALES y todas las filas fuente.
- Fecha para incorporacion: menor FECHAMATRICULA valida entre las matriculas
  elegibles actuales. Las otras fechas se conservan, incluso invalidas. Si no
  hay fecha valida, la persona queda pendiente de fecha. Hoy/futuro no entran
  en ventana cerrada. Una nueva segunda matricula no convierte a un estudiante
  anterior sin token en alta diaria; queda acumulado segun la fecha inicial.
- Mail_Inst: usar solo un correo valido inequivoco entre matriculas elegibles.
  Mayusculas/espacios exteriores no crean dos direcciones. Si hay varios validos
  distintos: `CONFLICTO_ENTRE_MATRICULAS`, no elegir ninguno ni detener al resto.
  Un valido junto a vacios/invalidos se puede usar; nunca tomar uno de una fila
  excluida, del correo personal ni del historico no elegible.
- Persona ya presente en tokens: no volver a incorporarla por una segunda
  matricula. CSV diario y acumulado son disjuntos y unicos por RUT.
- Respuestas, participacion, opciones y financiamiento se cruzan contra la
  vista de personas antes de conciliacion. Una respuesta no se multiplica por
  cantidad de carreras. Los resultados siguen su deduplicacion canonica previa.

## Salidas y manifiesto

`Conflictos_tokens_duplicados_vigentes_2027_P1_<fecha>.xlsx` conserva su nombre
historico, pero significa RUT con varias matriculas, no tokens duplicados en
LimeSurvey. En02_SALIDAS, solo si hay casos:

- Conflictos_Vigentes: todas las matriculas elegibles de esos RUT, fila fuente
  y presencia en tokens; no se elimina ninguna fila repetida tecnica.
- Personas: una fila por RUT, valores agrupados y reglas de fecha/correo.
- Conciliacion y Reglas: unidades, cantidades y politica utilizada.

El Word de correo incluye aviso breve y agregado, sin RUT ni detalles de correo.
La primera redaccion aprobada el 2026-10-15 ("Se identificaron N estudiantes con
mas de una matricula vigente") queda REEMPLAZADA por la peticion posterior del
usuario del mismo dia: "A la fecha se detectan N conflictos de RUT matriculado
en mas de una carrera", con tildes en el Word, dentro del primer parrafo despues
de eliminaciones y antes de matricula vigente. Numero dinamico, singular para un
caso y omision con cero casos. Sin parrafo adicional de conteo/archivo adjunto.
"Conflictos" es el rotulo editorial solicitado, no un error que bloquee el flujo.
La regla de persona unica y el seguimiento interno siguen vigentes sin cambios.
El Word interno distingue personas/matriculas. Trayectorias y matricula completa
conservan filas individuales y elegibilidad por fila/persona en05_ANALISIS.
Seguimiento de pendientes contiene ademas cantidad de matriculas y valores
originales de fecha/correo. Sin casos, no generar Excel vacio de conflictos.
El manifiesto registra GENERADO u OMITIDO_SIN_CASOS con filas y columnas.

Controles: matriculas elegibles = personas + filas adicionales por RUT;
personas = con token + sin token; sin token = diarios + acumulados + pendientes
de correo + pendientes de fecha. CANDIDATOS_ANTES_TRAYECTORIA y
EXCLUIDOS_TRAYECTORIA_PREVIA conservan su unidad historica de filas; los informes
de personas usan la union de RUT, no esos contadores de filas.

## Implementacion y pruebas

`caracterizacion_personas_2027.py` contiene proyeccion y seguimiento compartidos.
El adaptador 2027 modifica la referencia solo en memoria: exporta primero la
matricula, construye personas antes de conciliar respuestas y publica el plan
comun. La busqueda de matricula para los controles Word usa la misma vista.
El modo sin respuestas utiliza el mismo plan y exporta las matriculas completas.
No se cambia caracterizacion.py ni la referencia congelada de 51 archivos.

Regresiones en tests/test_multimatricula_2027.py y suites de incorporacion,
correos, separacion, trayectorias, reportes, opciones, comunicaciones y salidas.
Las pruebas sinteticas y diagnostico focalizado no sustituyen la proxima corrida
operativa del usuario. No generar ni sobrescribir salidas historicas para probar.

## Verificacion del cambio: 2026-10-15

Con las fuentes reales de Descargas, el resolutor 2027 P1 termina con codigo 0,
tambien en Python 3.14 con `.deps_local/py3.14`, utilizado por el comando operativo.
Se ejecuto la validacion de fuentes y el plan, no el pipeline operativo completo.
No se genero una nueva entrega real en Escritorio ni se sobrescribieron corridas.

| Control | Resultado |
| --- | ---: |
| Filas DATOSDEALUMNOS | 15045 |
| Matriculas del periodo 2027 P1 | 319 |
| Filas candidatas antes de trayectoria | 315 |
| Filas excluidas por trayectoria anterior | 6 |
| Matriculas elegibles conservadas | 309 |
| Personas elegibles, una vez por RUT | 307 |
| Personas con varias matriculas elegibles | 2 |
| Filas de esas personas para seguimiento | 4 |
| Personas elegibles con token | 283 |
| Personas elegibles sin token | 24 |
| Listos diarios / acumulados | 21 / 3 |
| Pendientes de correo / fecha | 0 / 0 |

Las dos personas con varias matriculas ya tienen token: no se reimportan por
su segunda matricula. Conciliaciones: 315=309+6; 309=307+2; 307=283+24;
24=21+3. No mezclar las filas extra (2) con las filas de seguimiento (4).

Fuentes verificadas por SHA-256, sin incorporar sus datos personales al repo:

- DATOSDEALUMNOS_11998.xlsx: `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`.
- tokens_141234.csv: `a8129f8d770194a9a87e4d233d287413f0fc3adff22f79f12265361e503b2f38`.
- results-survey141234.xlsx: `00aae47f7efbc40369706c8b3d7bfc54a5f9222ebd15b920a945af53f4e2b38f`.

Pruebas finales: 183 ejecutadas en Python 3.14, 180 aprobadas. Incluyen las 18
regresiones nuevas de multimatricula, lectura posterior del Excel, aviso Word,
manifiesto, omision sin casos, correo, fechas, CSV unico, respuestas no duplicadas,
adaptador en memoria, resolutor y modo sin respuestas con fuentes sinteticas.
Se revisaron visualmente las tres paginas del Word sintetico de control.

Tres pruebas generales de rutas ya fallan usando `HEAD:caracterizacion_runtime.py`
ejecutado en memoria, sin cambiar archivos. No son regresiones de esta correccion:

- `test_default_archivo_base_conserva_descubrimiento_en_mac`: falta default_archivo_base.
- `test_default_archivo_base_descubre_onedrive_en_windows`: falta default_archivo_base.
- `test_escritorio_redirigido_a_onedrive_en_windows`: diferencia Desktop/OneDrive.

El verificador de separacion FCU confirma 51 archivos sin diferencias, antes y
despues. SHA-256 de la referencia:
`85e265f5d317ed6b1f2d595cc9ce415628c9c7aa94822152092052723a67e294`.
`git diff --check` sin incidencias. No se modifico caracterizacion.py.

Regresion focalizada reproducible desde la raiz del proyecto:

```sh
PYTHONPATH=".deps_local/py3.14:tests" python3 -B -m unittest \
  test_multimatricula_2027 test_incorporacion_2027 test_correos_institucionales \
  test_sin_respuestas test_separacion_2027 test_reportes_2027 \
  test_trayectorias_2027 test_etiquetas_2027 test_salidas_condicionales_2027 \
  test_seguimiento_opciones_2027 test_comunicaciones_sedes_2027 test_catalogo_sies_2027
```

La ruta de dependencias de ese ejemplo corresponde al Python 3.14 del Mac
verificado; utilizar el entorno de dependencias equivalente en otro equipo.
