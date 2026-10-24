# Analisis anual integrado 2026

Politica vigente: `ANUAL_INTEGRADO_2026-v2`. Actualizacion autorizada: 2026-10-15.
La v1 y sus entregas se conservan como historico, no como reglas vigentes.

## Decision del usuario

Reemplaza la entrega anual que solo encadenaba tres analisis separados. El usuario
solicito un solo analisis, con combinaciones de P1/P2/P3, sectores, modalidad y
demas dimensiones. Sectores son Tecnologia, Administracion y Comercio y Salud,
no sedes. Autorizo implementarlo y reservo para si la ejecucion real.

No ejecutar caracterizacion.py ni el anual real como prueba rutinaria. Usar datos
sinteticos, pruebas unitarias y `--solo-validar`. No modificar el cierre FCU 2026.

## Ubicacion de entradas

Actualizacion autorizada el 2026-10-15: las parejas de P1=923565, P2=443299 y
P3=967488 se buscan en `Downloads/caracterizacion 1_2_3`; DATOSDEALUMNOS y
PROMEDIOSDEALUMNOS permanecen en `Downloads`. El comando no mueve los originales.
Si existe la subcarpeta, no completar parejas faltantes con otras copias de la
raiz. Si no existe, se admite la distribucion anterior de ocho archivos en la
raiz. Rutas explicitas y precedencias: `COMANDOS_MAC_WINDOWS.md`. La validacion
muestra todas las rutas y el manifiesto de la ejecucion conserva fuentes y hashes.

El preflight debe leer las tres parejas completas con el mismo selector de
contenido LimeSurvey del pipeline, verificar coincidencias por token y exigir
encabezados con codigos de preguntas e id/submitdate/token identificables antes
de iniciar P1. No basta con comprobar nombres, extensiones y contenedores Excel.
No reconstruir codigos de una exportacion solo textual por orden o por otro
periodo. Incidente rector: `INCIDENTE_ENCABEZADOS_ANUAL_2026_P2_20261015.md`.

## Entrega

Una carpeta nueva en Escritorio, `Caracterizacion_anual_2026_<ejecucion>`:

| Carpeta | Documento | Funcion |
|---|---|---|
| 02_SALIDAS | Caracterizacion_anual_2026.xlsx | Analisis integrado e interactivo |
| 02_SALIDAS/P1, P2, P3 | Todas las salidas de cada etapa | Copias identicas verificadas por SHA-256, visibles sin buscar entre respaldos |
| 04_AUDITORIA | Auditoria_caracterizacion_anual_2026.xlsx | Fuentes, incidencias, comparabilidad, cobertura y conciliacion |
| 04_AUDITORIA | manifest_analisis_anual.json | Estado, fuentes, hashes, etapas y copia verificada |
| 03_RESPALDOS/P1, P2, P3 | Archivos originales de cada etapa | Fuentes, Excel previos, Word, CSV y logs sin modificaciones |
| Raiz | SALIDAS_GENERADAS.txt | Ruta final, cantidades por periodo y listado de todas las salidas y Excel de auditoria |

Revision `2026-10-15-entrega-visible-jornada-v`: no son solamente dos archivos.
Los dos Excel integrados se agregan a las salidas originales por periodo. Se
verifican sus copias sin reformatear ni alterar esos originales. Las tablas de
los dos libros integrados (encabezados y datos, incluidas respuestas fuente)
quedan centradas horizontal y verticalmente. La copia de los respaldos es intacta.
Los diagnosticos `.inspect.ndjson` del generador van en 04_AUDITORIA, no en SALIDAS.

El terminal enumera archivos reales y cantidades por P1/P2/P3; el manifiesto
incluye `delivery_inventory`. No contar entradas/logs como salidas de analisis.
Solo mostrar `COPIA ESCRITORIO: OK` despues de publicar, comprobar existencia y
SHA-256 en la ruta final y copiar/verificar el manifiesto. Si se configura
`CARACTERIZACION_DESKTOP_BASE` a otra ruta, mostrar `DESTINO CONFIGURADO`, no
afirmar que es Escritorio. Un error de copia o un periodo sin salidas no es exito.
El mensaje heredado `Copia Escritorio` de cada etapa se presenta en consola como
copia interna; su log original se conserva sin modificaciones.

Verificacion de esta revision: 79 pruebas unitarias aprobadas; la prueba opcional
de exportacion se ejecuto aparte con datos sinteticos y aprobo 21 comprobaciones
de filtros/orden, caches y alineacion del XLSX exportado. Las 51 referencias del
FCU congelado permanecen intactas. No se ejecuto el analisis real ni se modifico
ninguna entrega del Escritorio. Cambios locales; esto no acredita publicacion remota.

El flujo diario 2027, sus archivos operativos, el cierre FCU y los documentos
historicos no cambian. Este libro contiene identificadores y respuestas privadas;
no es un archivo para carga PES ni una entrega publica.

## Estructura del libro principal

| Hoja | Contenido y unidad |
|---|---|
| Resumen | Matriculas, personas distintas, estado de respuesta y participacion; grafico conectado |
| Filtros | Inclusion Si/No por valor de periodo, sector, modalidad de carrera, sede, carrera y jornada |
| Participacion | Personas distintas por segmento y cruces; columnas explicitas Periodo, Sector IPSS y Modalidad; estados mutuamente excluyentes |
| Preguntas | Codigo literal, grupo si esta verificado, enunciado, valor observado, frecuencia, base valida, porcentaje y completas fuera de base valida |
| Financiamiento | Mismo calculo, separado por su finalidad; sin aplicar las preguntas 2027 a 2026 |
| Rendimiento | Media de promedios de notas finales 2026 por matricula, agrupada por periodo de ingreso, sector y nivel; denominador y cobertura academica explicitos |
| Respuestas abiertas | Textos originales y campos de tipo no verificado con alta diversidad; no se inventan categorias cualitativas |
| Base anual | Todos los registros de los universos sectorizados oficiales, dimensiones, identidad, fuente y auxiliares |
| Perfiles seleccion | Combinaciones observadas de las seis dimensiones; comparte el calculo dinamico de inclusion |
| Conteos personas | Pertenencia de una persona a cada segmento; calculos de deduplicacion de vista |
| Respuestas P1/P2/P3 | Preguntas, respuestas y metadatos originales; temporizaciones tecnicas conservadas en el export integro de 03_RESPALDOS y listadas en auditoria; auxiliares identificados a la derecha |
| Diccionario | Relacion codigo-columna-version-inventario; no declara equivalencia por igualdad de codigo |

No se pierden las hojas anteriores: **Hojas anteriores**, en auditoria, enumera
cada archivo/hoja, dimensiones, hash y ubicacion de su respaldo. Sus agregados
estaticos no se suman ni se presentan como interactivos. Las nuevas frecuencias
se calculan desde las respuestas originales seleccionadas por el maestro.

## Controles y calculos

- Seleccion compartida en **Filtros**, reflejada en las hojas. Permite las siete
  combinaciones no vacias de periodos y cualquier subconjunto de otras dimensiones.
- Los controles son listas Si/No, no segmentadores ni Power Pivot. Funcionan con
  formulas ordinarias, sin macros. El autofiltro de una tabla solo oculta detalle;
  no redefine la seleccion ni los indicadores de todo el libro.
- Sin casos: conteos cero y porcentajes **No aplica**. No ampliar automaticamente
  la seleccion a Todos. El retorno a todos los valores recupera el total.
- Matricula: un registro del universo oficial de cada periodo. No quitar duplicados
  administrativos ni repetir los filtros de elegibilidad con reglas nuevas.
- Persona: RUT normalizado; fallback al token ya normalizado del maestro si falta
  aquel. El contrato de BASE_SECTORIZADA conserva DV compacto sin guion: quitarlo,
  salvo si el valor ya coincide con el token sin DV. Tambien admitir DV separado,
  puntos y ceros iniciales; `.0` se
  trata como artefacto numerico antes de normalizar, nunca como digito adicional.
- Personas con al menos una respuesta completa en la seleccion: completas.
  Si no tienen completa pero si incompleta: incompletas. Las restantes: sin respuesta.
  La suma de estos estados es el numero de personas de la seleccion.
- Una persona puede estar en varias carreras/sectores. Cada segmento cuenta sus
  personas una sola vez; **los segmentos pueden solaparse y no deben sumarse**.
- Respuestas: cruce por periodo + ID seleccionado por el maestro, cotejando token.
  No elegir otra respuesta, ni adjudicar arbitrariamente respuestas de tokens
  ambiguos. ID ausente/repetido o correspondencia inconsistente bloquea la integracion.
- Frecuencias: solo respuestas completas seleccionadas. Una respuesta seleccionada
  aparece una vez aunque tenga varias matriculas. Para tipos simples y matrices,
  base valida = respuestas no vacias de la columna. En multiple M/P verificada,
  base = personas con alguna opcion marcada en la pregunta principal; cada opcion
  cuenta las marcas afirmativas. No usar como base solo los Si de esa opcion, lo
  que produciria un 100% falso. Marcadores desconocidos bloquean la interpretacion.
  Tipo no verificado: frecuencia observada sin porcentaje certificado.
  Fuera de base valida no equivale necesariamente a omision: incluye preguntas
  no aplicables por saltos. No afirmar el motivo sin evaluar sus condiciones.
  No interpreta un vacio como No. Las frecuencias preparadas por combinacion de
  perfiles preservan diferencias de mayusculas y comodines. Sus formulas
  ponderan la seleccion actual; MAX impide duplicar respuestas multicarrera.
  No se replica una columna auxiliar por cada pregunta en los exports crudos.
- Porcentajes se recalculan desde numerador/base de la seleccion; no se suman
  porcentajes. Seleccion multiple: no sumar porcentajes entre subpreguntas.
- Rendimiento v2 lee Hoja1 de PROMEDIOSDEALUMNOS archivado. Selecciona ANO=2026
  y PERIODOS=1/2/3 academicos disponibles, notas finales 1 a 7, estados APROBADO
  o REPROBADO, sin convalidacion/homologacion/transferencia. Normaliza coma decimal.
  Cruza por CODCLI + CODCARR de la nota contra CODCLI + CODCARPR de la matricula;
  no traspasa notas entre carreras por RUT. Intento: CODCLI, CODCARR, ANO, PERIODO,
  CODRAMO y CODSECC. Colapsa duplicados exactos de los campos de calculo, excluye
  intentos contradictorios y registra controles de filas. Claves vacias no se usan.
  Cada matricula promedia sus notas originales, no promedios semestrales. La vista
  agrega esos promedios por matricula; no es un promedio ponderado de asignaturas
  del sector ni un promedio de personas distintas. Periodo de ingreso y periodo
  academico no se confunden. No es cierre anual mientras falten notas del ano.
  Conservar promedio previo heredado en Enriquecimiento anual. Ausente queda sin
  dato y fuera del denominador; cero no es nota valida en esta escala.
- La integracion no crea nuevas escalas Likert, KPI compuestos, inferencias
  cualitativas ni autorizaciones de transferencia. Conserva el alcance interno
  y las reglas de seleccion del proceso historico. Una carga FCU requiere su
  propio contrato y controles de consentimientos.

## Comparabilidad y datos faltantes

El usuario confirmo el instrumento comun 2026 P1/P2/P3 y autorizo la equivalencia.
Los tres exports cotejados tienen 242 codigos/textos identicos, todos contenidos
en el inventario 2026 P2. Politica, firma de encabezados y copia del catalogo:
`gobernanza/analisis_anual/2026/v2/`. No se alteran REGISTRO.json ni inventarios.
El preflight verifica los recursos por hash y los codigos/textos antes de P1.
Se admiten encabezados solo codigo si su conjunto es exactamente el autorizado;
todo texto presente debe coincidir. Cambios posteriores bloquean la homologacion,
no se aceptan por posicion ni similitud. Las respuestas originales no se reescriben.
Se comparten grupos, tipos y estructura de referencia; no se afirma que P1/P3
tengan los IDs XML ni los filtros tecnicos de P2. No extender esta regla a 2027.
Las frecuencias mantienen el periodo para no sumar respuestas de personas
repetidas automaticamente. G01Q19 es multiple: una fila por alternativa,
numerador seleccionada y denominador con alguna seleccion en la pregunta.
Los porcentajes pueden sumar mas de 100%. No hay denominador universal.

"Sin respuesta valida a esta pregunta" sustituye "Fuera de base valida": completas
seleccionadas menos base de la pregunta; no distingue omision de salto/no aplica.
"Comparabilidad entre periodos" muestra la equivalencia autorizada, no un texto
fijo de falta de aprobacion ni una evaluacion de calidad individual.

Modalidad se obtiene del catalogo **2026** de avance_curricular (mu2026_20261013),
copiado sin cambios y fijado por hash, sin depender de otro checkout instalado.
Clave CODCARPR+SEDE+JORNADA contra equivalencias explicitas. Sede/jornada solo
seleccionan candidatos; MODALIDAD viene del catalogo, no de esas claves. Una
modalidad valida comun a todos los candidatos se asigna aunque el codigo SIES
siga ambiguo. Modalidades distintas o sin equivalencia: No determinada. No usar
MODALIDAD escolar, inferir SP ni escoger primera fila/version. No se cambia el
catalogo ni el resolutor congelado de MU2026; es una politica del consumidor anual.

Excepcion posterior autorizada por el usuario el 2026-10-15: **JORNADA V =
Presencial** para esta capa anual 2026. Tiene precedencia sobre el valor del
catalogo y se registra como `REGLA_INSTITUCIONAL_JORNADA_V`, con fuente en la
politica, no como conclusion de SIES. Conservar modalidad/regla del catalogo y
discrepancia en Enriquecimiento anual; no cambiar candidatos ni estado del codigo
SIES, incluso si falta equivalencia. La integridad interna del catalogo sigue
validandose. No extrapolar a D/O, MODALIDAD escolar, sufijos SP ni 2027. Esta
decision sustituye solamente la prohibicion de usar V dentro del anual vigente;
no modifica el catalogo, las fuentes, los respaldos ni el proceso congelado 2026.

Sector: alias exactos por codigo y nombre CADMP (Continuidad Ingenieria
Administracion Publica) -> Administracion y Comercio; TFARSP (Tecnico en Farmacia
SP) -> Salud. La segunda equivalencia no acredita modalidad ni codigo SIES.
Contradiccion con sector ya clasificado es error; otros desconocidos permanecen
visibles. Se conserva el sector previo y la nueva clasificacion en auditoria.

Auditoria incorpora Enriquecimiento anual (privado, por matricula: candidatos,
modalidad, sector antes/despues, promedio previo/2026, numero de notas y periodos)
y Calidad notas. La cobertura de una fuente compartida por tres etapas no debe
sumarse tres veces. Fuentes conserva hashes de politica, catalogo, columnas e
inventario. Manifiesto identifica la politica v2 y hashes de todos los archivos.

## Ejecucion y publicacion

1. Validar las ocho entradas, IDs de encuesta y referencia congelada.
2. Verificar runtime del generador antes de iniciar el procesamiento largo.
3. Archivar entradas con hash y ejecutar las tres etapas existentes. Exigir
   BASE_SECTORIZADA; no aceptar su fallo como una advertencia no bloqueante.
4. Integrar, recalcular, comparar con controles independientes y exportar ambos Excel.
5. Conservar todos los respaldos, copiar a carpeta temporal `.incompleto`, verificar
   hashes y publicar la carpeta anual. Solo entonces indicar COMPLETO_ANUAL_INTEGRADO.

Error de consolidacion: conservar etapas y estado ERROR_CONSOLIDACION. No presentar
como terminado un conjunto de periodos sin Excel anual. Los JSON intermedios con
identificadores quedan en `.local`, excluidos de Git. Las fuentes ya estan
archivadas; un dato faltante no se rellena con informacion ficticia.

Runtime del generador: Artifact Tool del host, con alternativas explicitas
`CARACTERIZACION_ANUAL_NODE` y `CARACTERIZACION_ANUAL_NODE_MODULES` en otros equipos.
El flujo no depende de un Office Script, una conexion cloud ni de Excel abierto.
El comando `--solo-validar` verifica entradas y esquema gobernado, no simula el analisis ni certifica
el contenido final ni la compatibilidad nativa de Excel en otro equipo.

## Bitacora de implementacion

- 2026-10-13: nueva capa independiente; no se edito caracterizacion.py.
- Se preservaron las modificaciones previas de seleccion de fuentes actuales.
- Pruebas sinteticas de repeticion entre periodos/carreras, vacios/cero, IDs,
  token, correspondencia de periodo y frecuencias por version.
- Generacion de ambos libros sinteticos, recalculo de selecciones y retorno al
  total, inspeccion del XLSX exportado y vistas PNG. Prueba adicional de orden de
  filas de fuente y controles, sin cambiar la seleccion.
- La evidencia local esta en `.local/pruebas_anual_integrado/04_AUDITORIA`;
  no contiene datos reales y no es el resultado anual del usuario.
- Pendiente de validacion operativa: corrida real autorizada por el usuario y
  apertura del resultado en Excel Mac/Windows. No afirmar que se ejecutaron.
  Actualizacion 2026-10-15: corrida real recuperada y verificada segun el cierre
  siguiente; la apertura interactiva en Excel Mac/Windows sigue sin realizarse.
- Referencia congelada: verificador independiente; no modificar su baseline.
- Publicacion en GitHub no incluida en esta autorizacion; archivo local no prueba push.

### Evidencia del 2026-10-13

- 27 pruebas en `tests/test_analisis_anual_integrado.py`, con
  `ANUAL_TEST_XLSX=1`: correctas, incluidos ambos libros sinteticos exportados.
- 20 pruebas de comandos operativos, 20 del resolutor congelado P2 y 5 del
  verificador de separacion: correctas. Total: 72 pruebas focalizadas.
- 21 comprobaciones del libro: siete combinaciones no vacias de periodos,
  selecciones cruzadas por dimension, seleccion vacia y reordenamiento de filas.
  Conteos y frecuencias coinciden con el control independiente. Cero errores
  de formula detectados; porcentajes calculados sobre su base valida.
- Vistas PNG revisadas y estructura/cache del XLSX inspeccionados. Esto no
  reemplaza la apertura en Excel nativo, que no se realizo.
- 51 referencias congeladas verificadas sin incidencias; baseline SHA-256:
  `85e265f5d317ed6b1f2d595cc9ce415628c9c7aa94822152092052723a67e294`.
## Recuperacion de consolidacion (2026-10-15)

Si los tres periodos terminaron y fallo la generacion del Excel, no repetir el
analisis completo. Recuperar con:

```bash
bash ./procesar_analisis_anual.sh 2026 --reanudar-consolidacion "/ruta/a/la/corrida_anual"
```

La carpeta debe contener `manifest_analisis_anual.json`, P1/P2/P3 terminados con
codigo 0 y las entradas archivadas con sus hashes originales. La recuperacion
usa esas fuentes, no las versiones actuales en Descargas. Genera una corrida
nueva, registra `recovery_of`, conserva el error original y copia los respaldos.
No sustituye el cierre FCU 2026 ni modifica el proceso diario 2027.

El generador registra el avance por hoja y su memoria. Limita el heap de Node a
6144 MiB para cubrir la serializacion final y evita aplicar estilos celda a celda a las exportaciones crudas anchas.
No materializa celdas vacias de esos exports; conserva sus encabezados, posiciones
y valores originales. La lectura del archivo exportado comprueba esa igualdad.
Primero escribe datos y luego formulas en orden de dependencias. La seleccion se
calcula una vez por perfil de dimensiones; las pertenencias de personas y
respuestas a esos perfiles proceden del cruce validado y no de una busqueda
repetida de toda la matricula. No cambia el universo ni los denominadores.
El Excel es una vista interactiva de un corte: Filtros y los selectores locales
de pregunta/grupo y sector son entradas editables segun
`DASHBOARD_ANUAL_2026.md`;
para cambiar fuentes o pertenencias hay que regenerarlo. Las tablas internas de
calculo conservan su orden de generacion y no se usan como captura de datos.
La consolidacion verifica filtros mediante recalculo, restaura todos a Si y
solo publica tras validar los dos libros y los hashes de la copia.
`nativeExcelTested=false` significa que la verificacion fue en el motor generador,
no una prueba interactiva en Microsoft Excel.

### Incidente de memoria y controles de recuperacion

La corrida `20261015_113241_388114` termino P1/P2/P3 con codigo 0, pero el proceso
Node agoto memoria al consolidar. Se conserva su estado ERROR_CONSOLIDACION.
Un ensayo de recuperacion tambien alcanzo el limite durante la exportacion:
validar numeros en memoria no equivale a haber entregado un Excel valido.

La correccion elimina cientos de columnas auxiliares repetidas: prepara las
frecuencias exactas por combinacion de perfiles y pondera esas frecuencias con
formulas de seleccion. Conserva todas las preguntas y respuestas originales.
Las columnas `GxxQyyTime`, `groupTime...` e `interviewtime`, no usadas en los
indicadores, se conservan en los exports integros de 03_RESPALDOS en lugar de
duplicarlas en el libro anual. `Columnas en respaldo` registra sus encabezados
y posiciones originales. No se retiran submitdate, startdate ni datestamp.
La comparacion independiente por registro y opcion se ejecuta para cada filtro;
despues se comprueban los valores guardados y las celdas originales del XLSX.
El grafico del resumen se vincula despues del calculo para evitar interpretar
la primera respuesta completa como un encabezado y omitirla del grafico.

El test de reordenamiento mueve datos A:Q y formulas R:W por separado; nunca
reemplaza formulas por sus valores calculados. Los respaldos originales no se
reordenan ni se modifican. La recuperacion exige hashes de entradas y bases,
rechaza periodos incompletos y no consulta archivos mas recientes en Descargas.
La prueba de reordenamiento se ejecuta en fixtures de hasta 500 filas, no como
operacion adicional sobre la fuente real de solo lectura. Los 57 casos reales
de filtros y la lectura de los valores exportados siguen siendo obligatorios.

### Cierre operativo historico v1 del 2026-10-15

- Recuperacion `20261015_130336_379868`: codigo 0 y estado
  `COMPLETO_ANUAL_INTEGRADO`. No se volvieron a ejecutar P1/P2/P3.
- Entrega: `~/Desktop/Caracterizacion_anual_2026_20261015_130336_379868`.
  Los 172 archivos coinciden por SHA-256 con el manifiesto; incluye 03_RESPALDOS
  P1/P2/P3. El error original permanece registrado en su propia carpeta.
- Matriculas: P1=1622, P2=467, P3=431; total=2520. Personas unicas: P1=1621,
  P2=466, P3=428; union anual=2514. Una persona aparece en dos periodos.
- Estados de personas: 1583 completas + 11 incompletas + 920 sin respuesta = 2514.
  Participacion completa=62,9673826571%, presentada con un decimal.
- 57 selecciones reales recalculadas y conciliadas, sin errores de formula.
  Lectura de ambos XLSX: 9677 valores de control correctos, caches validos y
  celdas originales incluidas preservadas. 52 controles restaurados a Si.
- 61 pruebas focalizadas correctas, incluido reordenamiento sintetico y prueba
  de que solo se apartan temporizaciones tecnicas (333 columnas inventariadas).
  Las 242 columnas de preguntas de cada periodo permanecen en el libro.
- Revision visual de hojas y grafico; series del XLSX enlazadas a A9:A11 y
  B9:B11 del Resumen, incluidas las respuestas completas. No se probo Excel nativo.
- 51 referencias FCU 2026 verificadas intactas. No se modifico el flujo diario
  2027 ni se publico este cambio en GitHub.
- Limites del corte: 2520 registros sin modalidad de carrera y sin promedio AC;
  24 sin sector. No se sustituyen por inferencias o ceros. P1/P3 sin inventario
  de instrumento completo: porcentajes no verificados se identifican como tales
  y las respuestas no se homologan automaticamente entre versiones.

## Verificacion de codigo v2 (2026-10-15)

Correccion posterior autorizada sobre el generador, sin ejecutar el analisis
ni reemplazar las entregas del escritorio. Los limites del cierre v1 de arriba
describen aquella entrega, no las reglas vigentes v2.

- 74 pruebas aprobadas; 1 prueba optativa de exportacion XLSX omitida. Suite:
  `test_enriquecimiento_anual`, `test_analisis_anual_integrado`,
  `test_comandos_operativos`. Datos sinteticos, procesos productivos simulados
  mediante mocks; ningun P1/P2/P3 real ejecutado.
- Cobertura: recursos portables y hashes, modalidades ambiguas/coincidentes,
  alias de sector, notas 2026 frente a 2025, notas invalidas/transferidas,
  duplicados/contradicciones, carreras separadas, preservacion de fuentes,
  equivalencia de preguntas, encabezados solo codigo y cambios de texto,
  cruces y denominadores de Participacion, filtros sin casos y publicacion.
- Los controles que ejecutara el comando incluyen ahora celdas de Participacion
  y Rendimiento bajo cada seleccion, ademas de preguntas y conciliacion general.
- Sintaxis del generador JS validada. No se certifica una nueva exportacion
  real ni una revision visual de Excel v2: corresponde a la siguiente corrida
  reservada al usuario. No se modificaron archivos Excel de entrega.
- Comprobadas intactas las 51 referencias FCU2026 antes/despues del cambio,
  baseline `85e265f5d317ed6b1f2d595cc9ce415628c9c7aa94822152092052723a67e294`.
- Cambios en el repositorio local. Esta bitacora no acredita commit/push a GitHub.

