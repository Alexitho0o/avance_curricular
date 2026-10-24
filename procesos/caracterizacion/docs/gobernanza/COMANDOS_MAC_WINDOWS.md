# Comandos operativos Mac y Windows

Actualizacion: 2026-10-13. Perfil estructurado: `COMANDOS_OPERATIVOS.json`, version 2.

Validacion registrada: `VALIDACION_COMANDOS_20261009.json`; esa validacion historica no realizo commit ni push. La publicacion autorizada el 2026-10-13 se documenta por separado en `PUBLICACION_GITHUB_2027_P1_20261013.json`. Windows necesita la misma version de los ejecutores y perfiles. Los Excel nuevos requieren Artifact Tool; si las rutas del runtime difieren, configurar LIMESURVEY_NODE y LIMESURVEY_NODE_MODULES con los ejecutables y modulos del entorno de destino. No se afirma una ejecucion real de Windows a partir de las pruebas de Mac.

## Financiamiento 2027 P1 en Mac

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN" && \
CARACTERIZACION_EXCLUIR_DIPLOMADOS=1 \
CARACTERIZACION_EXCLUIR_SIN_FIRMA=1 \
VERBOSIDAD=1 \
STOP_AFTER_FINANCIAMIENTO=1 \
./procesar_financiamiento_diario.sh 2027 1
```

## Financiamiento 2027 P1 en Windows PowerShell

```powershell
cd "C:\Users\AlexiMarceloBurgosFl\Github\CARACTERIZACION"
$env:CARACTERIZACION_EXCLUIR_DIPLOMADOS="1"
$env:CARACTERIZACION_EXCLUIR_SIN_FIRMA="1"
$env:VERBOSIDAD="1"
$env:STOP_AFTER_FINANCIAMIENTO="1"
& "C:\Users\AlexiMarceloBurgosFl\AppData\Local\Programs\Git\bin\bash.exe" ./procesar_financiamiento_diario.sh 2027 1
```

La encuesta gobernada es 141234. En Descargas se necesitan matricula DATOSDEALUMNOS y los exports `tokens_141234*.csv` / `results-survey141234*.xlsx`. Los resultados deben ser XLSX/XLSM; CSV o XLS no estan admitidos por el selector actual de resultados. Una ruta explicita RUTA_INSCRITOS/RUTA_RESULTADOS de otro ano se bloquea; eliminarla de la sesion o sustituirla por las fuentes correctas. El ejecutor fija ano, periodo y cohorte 2027 y corta despues del financiamiento. No genera la carga oficial FCU 2027.

Los archivos de cero bytes o con estructura Excel invalida se bloquean antes de iniciar el analisis de respuestas. Por confirmacion expresa del usuario, 2027 P1 dispone de un modo operativo SIN_RESPUESTAS_CONFIRMADAS: si resultados tiene cero bytes o un libro valido sin registros, los participantes no muestran completed y no hay respondientes historicos, genera listas de matricula, participantes, pendientes y CSV de incorporacion. La ausencia no se convierte en respuestas ficticias ni resultados de financiamiento. Cuando resultados contiene filas, se utiliza automaticamente el flujo normal. Un libro corrupto no vacio sigue bloqueado.

Este modo reutiliza las reglas de periodo, cohorte, firma, estado/situacion, programas excluidos, RUT y calendario diario. Las filas de hoy o con fecha invalida permanecen auditadas y pendientes; no ingresan en la ventana diaria ni se presentan como rezagados anteriores. El CSV acumulado solo se crea cuando hay rezagados listos para incorporar. El Excel de seguimiento conserva todos los pendientes, incluidos correo y firma, con motivos separados; no es un archivo importable y nunca se genera vacio. El cierre 2026 permanece intacto.

Reglas, archivos y conciliacion de la ejecucion real: `MODO_SIN_RESPUESTAS_2027_P1.md`.

Los CSV de incorporacion 2027 P1 utilizan exclusivamente Mail_Inst, con comprobacion previa tambien en el flujo con respuestas. No sustituir por MAIL personal. El modo sin respuestas guarda el texto del resumen de matricula para correo en sus salidas.

Incidente y comprobaciones: `INCIDENTE_RESULTADOS_2027_P1_20261009.md`.

Bloqueo Mail_Inst del 2026-10-13: `INCIDENTE_MAIL_INST_2027_P1_20261013.md`. El preflight informa fuentes, conciliacion y auditoria privada bajo `.local/auditoria_correos/`. La politica inicial de bloqueo global quedo reemplazada por autorizacion del usuario del 2026-10-13: el comando continua, exporta solo correos validos y conserva los otros casos en seguimiento y en el Word interno de05_ANALISIS. Reglas vigentes: `POLITICA_INCORPORACION_CORREO_2027_P1.md` y `SEPARACION_COMUNICACION_ANALISIS_2027_P1.md`. En nuevas corridas2027P1, 02_SALIDAS contiene correo/CSV;05_ANALISIS informes y Excel internos;04_AUDITORIA conciliaciones y extraccion ordenada de ambos Word. El universo objetivo usa primer ingreso institucional tras revisar todo el historico, no solo ANOINGRESO. Con los resultados actuales (15 filas) se aplica el flujo con respuestas.

La variable STOP_AFTER_FINANCIAMIENTO se mantiene en los comandos habituales; el ejecutor activa efectivamente CARACTERIZACION_STOP_AFTER_FINANCIAMIENTO=1 y CARACTERIZACION_SKIP_FCU=1.

## Analisis completo 2026 P1, P2 y P3 en Mac

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN" && \
bash ./procesar_analisis_anual.sh 2026
```

## Analisis completo 2026 P1, P2 y P3 en Windows PowerShell

```powershell
cd "C:\Users\AlexiMarceloBurgosFl\Github\CARACTERIZACION"
& "C:\Users\AlexiMarceloBurgosFl\AppData\Local\Programs\Git\bin\bash.exe" ./procesar_analisis_anual.sh 2026
```

### Recuperar solo el Excel anual

Si P1/P2/P3 terminaron con codigo 0 pero fallo la consolidacion, no repetir el
analisis. En Mac, desde el proyecto:

```bash
bash ./procesar_analisis_anual.sh 2026 --reanudar-consolidacion "/ruta/a/la/corrida_anual"
```

En PowerShell, agregar `--reanudar-consolidacion "C:/ruta/a/la/corrida_anual"`
al comando de Git Bash anterior. Usar la carpeta que contiene el manifiesto y
P1/P2/P3, no una carpeta de Descargas. Se verifican los archivos archivados y se
crea una entrega nueva; la anterior y el cierre FCU permanecen intactos.

El comando procesa P1, P2 y P3 como etapas internas y luego genera UN analisis anual integrado. La entrega unica en Escritorio contiene el Excel principal en 02_SALIDAS, el Excel de auditoria en 04_AUDITORIA y las fuentes/salidas originales por periodo en 03_RESPALDOS. No suma personas repetidas ni porcentajes. Se detiene si falla una etapa; solo declara COMPLETO_ANUAL_INTEGRADO despues de validar la consolidacion y su copia. Contrato: `ANALISIS_ANUAL_INTEGRADO_2026.md`.

Distribucion vigente desde el 2026-10-15. El mismo comando busca las seis
exportaciones de encuestas dentro de `Descargas/caracterizacion 1_2_3` y conserva
las dos fuentes administrativas directamente en Descargas:

```text
Descargas/
  DATOSDEALUMNOS_*.xlsx
  PROMEDIOSDEALUMNOS_*.xlsx
  caracterizacion 1_2_3/
    tokens_923565*.csv
    results-survey923565*.xlsx
    tokens_443299*.csv
    results-survey443299*.xlsx
    tokens_967488*.csv
    results-survey967488*.xlsx
```

Son ocho archivos: seis exports de LimeSurvey y dos fuentes administrativas compartidas. El ID gobernado determina el periodo: P1=923565, P2=443299, P3=967488. Se admiten los nombres descriptivos exportados por LimeSurvey, incluidos espacios, acentos y sufijos sin guion bajo, como `results-survey443299Encuesta de Caracterizacion 2026-2 (443299).xlsx`. Los archivos temporales `~$...` de Excel no participan en la seleccion.

Cuando hay varias versiones de un mismo rol/ID, se selecciona la de modificacion mas reciente (desempate por nombre); el terminal muestra las rutas de los cuatro roles por periodo antes de comenzar. Cada periodo recibe exclusivamente su pareja. Una encuesta 2027 u otra encuesta presente en Descargas no puede sustituirla. El preflight bloquea todas las ejecuciones si falta una entrada o si un Excel esta vacio o tiene un contenedor invalido. Ademas, antes de iniciar P1, lee las tres parejas con el selector LimeSurvey del pipeline, valida coincidencias reales de tokens y exige codigos de preguntas e id/submitdate/token identificables. No certifica la conciliacion con matricula ni el contenido completo del analisis: esos controles corresponden al pipeline.

Exportar resultados de cada encuesta como Excel, con encabezados **Codigo de pregunta y texto de pregunta**, separador punto y espacio, todas las columnas y todas las respuestas (completas e incompletas). Conservar los textos de las respuestas segun el flujo existente. No confundir encabezados de preguntas con codigos de respuestas. El anual tambien admite encabezados solo de codigo, pero no texto sin codigo ni reconstruccion por posicion o desde otra encuesta. Fuente: [manual LimeSurvey, Export responses](https://www.limesurvey.org/manual/Export_responses/en).

Esta nueva ejecucion anual analiza las fuentes actuales de los tres periodos, incluido P2. Sustituye la regla anterior del anual que exigia subcarpetas P1/P3 y leia P2 desde julio. No modifica `FUENTES_CONGELADAS_2026_P2.json`, sus cuatro fuentes ni el resolutor historico; el cierre FCU 2026 permanece como referencia independiente. Los comandos de reproduccion del cierre no cambian. No invocar el resolutor congelado P2 para preparar este analisis anual actual. Git no distribuye automaticamente los datos personales de Descargas.

Para fuentes en otra ubicacion, establecer CARACTERIZACION_FUENTES_ANUAL como carpeta raiz: contiene DATOSDEALUMNOS/PROMEDIOSDEALUMNOS y la subcarpeta `caracterizacion 1_2_3` con las encuestas. Si esa subcarpeta no existe, se conserva compatibilidad con los ocho archivos directamente en la raiz. Si existe pero esta incompleta, bloquear e informar faltantes; nunca completar encuestas con copias de la raiz. Las fuentes administrativas se buscan solo en la raiz, no dentro de la subcarpeta.

Se mantienen CARACTERIZACION_INPUT_DIR_P1/P2/P3 para elegir una carpeta especifica con sus cuatro entradas (prioridad sobre la subcarpeta comun) y RUTA_MATRICULA_P1, RUTA_INSCRITOS_P1, RUTA_RESULTADOS_P1, RUTA_PROMEDIOS_P1 (y equivalentes P2/P3) para fijar cada archivo con maxima prioridad. Una ruta de encuesta incompatible con el periodo se bloquea. Si se conserva la estructura antigua de subcarpetas, indicar cada una con CARACTERIZACION_INPUT_DIR_P1/P2/P3; no se agrega `/P{periodo}` automaticamente a CARACTERIZACION_FUENTES_ANUAL. Las variables RUTA_* genericas de una sesion anterior no se heredan entre periodos.

El anual activa exclusion de diplomados, exclusion sin firma, filtro de ano de ingreso 2026 y verbosidad 1. Desactiva SOLO_GENERAR_FCU, SKIP_FCU, FAST_FCU_ONLY y los cortes de financiamiento/10bis. Emplea el ejecutor completo existente y exige su base sectorizada. Sus logs y manifiesto se guardan en `.local/analisis_anual/2026/<ejecucion>/`, con una carpeta P1/P2/P3 para cada etapa. Sus copias individuales quedan internas; el usuario recibe una sola carpeta anual. El cierre FCU 2026 y sus referencias congeladas permanecen intactos.

El nuevo generador verifica Artifact Tool antes de iniciar P1. Por defecto usa el runtime de Codex; si esta en otra ruta, configurar `CARACTERIZACION_ANUAL_NODE` y `CARACTERIZACION_ANUAL_NODE_MODULES`. Son variables del generador anual, distintas de LIMESURVEY_NODE usado por el inventario de instrumentos. No se ha probado el generador anual en Excel Windows.

El Excel usa selectores Si/No por valor en Filtros, compartidos por las vistas; no requiere macros ni Power Pivot. El autofiltro de una tabla solo oculta detalle, no modifica los indicadores. Desde ANUAL_INTEGRADO_2026-v2 consume el catalogo MU/SIES 2026 portable, con modalidad comun entre candidatos respaldados y estado separado del codigo SIES. Nunca usa modalidad escolar. Incluye los alias de sector CADMP/TFARSP y notas finales del ano analizado, preservando promedios previos en auditoria. El instrumento comun P1/P2/P3 fue confirmado por el usuario: se verifican sus 242 codigos y los textos presentes contra la referencia gobernada, antes de P1. No se extiende a 2027 ni se cambia FCU2026. Participacion incluye columnas Periodo/Sector IPSS/Modalidad. El mismo comando genera Caracterizacion_anual_2026.xlsx y Auditoria_caracterizacion_anual_2026.xlsx, ademas de conservar las salidas originales en 03_RESPALDOS/P1/P2/P3. No requiere pasos ejecutados desde un chat.

Cada corrida recibe copias de sus cuatro entradas en 01_ENTRADAS, verificadas contra los hashes registrados antes de iniciar. Un cambio de fuente durante la ejecucion anual detiene el proceso; no sustituye silenciosamente la entrada por otra version.

## Validar sin ejecutar el analisis

Mac:

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN" && \
bash ./procesar_analisis_anual.sh 2026 --solo-validar
```

Windows PowerShell:

```powershell
cd "C:\Users\AlexiMarceloBurgosFl\Github\CARACTERIZACION"
& "C:\Users\AlexiMarceloBurgosFl\AppData\Local\Programs\Git\bin\bash.exe" ./procesar_analisis_anual.sh 2026 --solo-validar
```

No ejecuta caracterizacion.py ni crea corridas de analisis. Lee y comprueba las tres parejas; muestra las fuentes, filas, columnas de preguntas y coincidencias, o los problemas detectados por periodo. Una exportacion sin codigos se rechaza antes de ejecutar P1. Requiere Python 3.10 o superior; si no se encuentra, configurar CARACTERIZACION_PYTHON con el ejecutable instalado.

## Limites de verificacion

Se verifican sintaxis, seleccion de archivos, aislamiento de periodos, configuracion de corte y preflight. La comprobacion en Mac no certifica una ejecucion real en Windows. No se ejecuta automaticamente el analisis completo para probar estos comandos.

### Ajuste anual verificado el 2026-10-13

- Motivo: el comando buscaba subcarpetas inexistentes para P1/P3 y seleccionaba el P2 congelado de julio, en lugar de las tres parejas actuales entregadas por el usuario.
- `bash ./procesar_analisis_anual.sh 2026 --solo-validar`: codigo 0, `PREFLIGHT=OK`, ocho entradas distintas de Descargas. P1=923565, P2=443299 y P3=967488; fuentes administrativas compartidas DATOSDEALUMNOS_11941.xlsx y PROMEDIOSDEALUMNOS_7804.xlsx.
- Pruebas: 20 en `tests/test_comandos_operativos.py`, 20 en `tests/test_h044_fuentes_congeladas_p2.py` y 5 en `scripts/gobernanza/test_verificar_separacion_fcu.py`, todas correctas. Incluyen nombres descriptivos, bloqueo por falta de entradas, aislamiento de IDs, fuentes explicitas, modo solo-validar sin iniciar procesos y preservacion del resolutor congelado.
- Sintaxis de los dos lanzadores Bash verificada. Las 51 referencias congeladas conservan sus hashes.
- Por solicitud expresa del usuario, NO se ejecuto el analisis anual ni caracterizacion.py. No se generaron nuevas salidas en Escritorio ni se certifican aun los resultados de P1/P2/P3. Esta verificacion no acredita por si sola publicacion en GitHub.

### Consolidacion integrada verificada el 2026-10-13

Se agregaron 27 pruebas sinteticas del consolidador y generador Excel; las 45
pruebas anteriores tambien pasaron (72 en total). El libro sintetico supero
21 comprobaciones de filtros/reordenamiento y controles independientes de
conteos, frecuencias y porcentajes. Las 51 referencias congeladas siguen intactas.
La entrega real, su rendimiento con el volumen completo y la apertura en Excel
Mac/Windows no se han probado: el usuario ejecutara el comando. Detalle y limites
en `ANALISIS_ANUAL_INTEGRADO_2026.md`.

### Subcarpeta de encuestas verificada el 2026-10-15

- El comando habitual no cambia. Preflight real: codigo 0, `PREFLIGHT=OK`, seis
  exportaciones en `Downloads/caracterizacion 1_2_3`, DATOSDEALUMNOS_11998.xlsx
  y PROMEDIOSDEALUMNOS_7804.xlsx en Downloads; ocho entradas distintas.
- Regresion: 76 pruebas correctas y una prueba opcional de generacion XLSX
  omitida. Incluye carpeta con espacios, aislamiento de copias antiguas, fuentes
  administrativas fuera de la subcarpeta, precedencias y validacion sin ejecucion.
- Las 51 referencias congeladas siguen intactas. No se ejecuto el analisis real
  ni se generaron nuevas salidas en Escritorio. Esta validacion no certifica los
  resultados del analisis completo ni una ejecucion en Windows.

### Correccion del preflight tras la ejecucion del usuario, 2026-10-15

La validacion anterior de rutas/contenedores fue insuficiente: P1 termino, pero
P2 fallo por exportacion solo con textos, sin codigos. El preflight ahora lee
el contenido de las tres parejas antes de iniciar cualquier etapa y deja sus
metricas en `source_validation` del plan/manifiesto. La fuente P2 actual queda
bloqueada con instruccion de reexportacion; no se modifica ni se homologan sus
columnas automaticamente. Diagnostico, pruebas y estado pendiente en
`INCIDENTE_ENCABEZADOS_ANUAL_2026_P2_20261015.md`.
