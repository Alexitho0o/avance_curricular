# Incidente: exportacion P2 sin codigos de preguntas

Fecha: 2026-10-15. Alcance: analisis anual actual 2026, no cierre FCU congelado.
Estado: control preventivo corregido; falta reexportar los resultados P2.

## Evidencia

- Corrida del usuario: `.local/analisis_anual/2026/20261015_111509_944865`.
- Manifiesto anual: `INTERRUMPIDO`; P1 termino con codigo 0, P2 con codigo 2.
  P3 no se inicio y no se publico el Excel anual. El Excel y respaldos P1 siguen
  en esa corrida. No se eliminaron ni regeneraron en este diagnostico.
- Resultados P2 encuesta 443299: 310 filas de datos y 362 columnas. Encabezados
  como `ID de respuesta`, `Fecha de envio`, `Codigo de acceso` y los textos de
  las preguntas no contienen los codigos `id`, `submitdate`, `token`, `G...Q...`.
  No es una encuesta vacia ni una ruta incorrecta.
- P1=923565 y P3=967488 tienen 242 columnas con codigos de preguntas cada una.
  P2 tiene cero. Las cantidades de filas no equivalen a participacion elegible.
- Los hashes de los tres resultados coinciden con los registrados en la corrida.
  Hash P2: `06368082233d65b600f0329d061e95eea9e0de017e03966d715682d9da6e2b7c`.

## Causa y brecha del control

`caracterizacion_limesurvey.inspect_results_file()` rechazo P2 al no reconocer
columnas de encuesta. No se altera ese control ni el modulo historico. El
preflight de `scripts/ejecutar_analisis_anual.py` solo llamaba al resolutor de
rutas/contenedores y no inspeccionaba el contenido. Por eso habia declarado
PREFLIGHT=OK antes de ejecutar P1, pero P2 fallo al leer sus respuestas.

## Correccion

`validate_survey_sources()` reutiliza `select_latest_limesurvey_pair()` para
leer cada pareja explicita, validar estructura y coincidencias reales. Reutiliza
`question_column()` del consolidador para exigir preguntas con codigo y comprueba
id/submitdate/token identificables. Todas las parejas se validan antes de iniciar
P1 o crear carpetas. Los controles no modifican fuentes ni cambian elegibilidad.
Las metricas quedan en `source_validation` del plan y manifiesto de nuevas corridas.

La exportacion solo textual no se transforma: la posicion o similitud de texto
con P1/P3 no acredita identidad de pregunta/subpregunta. No se usa el cierre
congelado de P2 como sustituto de las respuestas actuales.

## Accion pendiente

Reexportar resultados de encuesta **443299, 2026 P2** en LimeSurvey: Excel;
encabezados **Codigo de pregunta y texto de pregunta**; separador punto y espacio;
todas las columnas y todas las respuestas (completas e incompletas). Conservar
la configuracion de textos de respuesta; encabezados y valores son opciones
distintas. Guardar la nueva exportacion en `Downloads/caracterizacion 1_2_3`.

Fuente de las opciones de exportacion:
[Manual LimeSurvey, Export responses](https://www.limesurvey.org/manual/Export_responses/en).

Ejecutar primero `bash ./procesar_analisis_anual.sh 2026 --solo-validar`.
Solo con PREFLIGHT=OK ejecutar el comando anual habitual. Actualmente no hay
reanudacion por etapa: una nueva ejecucion completa vuelve a procesar P1. El
diagnostico no implementa ni declara reanudacion automatica.

## Verificacion

- Preflight real con la fuente actual: codigo 3, identifica P2 y explica como
  reexportar; no inicia P1 ni genera salidas.
- Pruebas de regresion: texto sin codigos bloquea antes de P1 y sin modificar
  fuentes; encabezados codigo/texto y solo codigo validos; metadatos faltantes,
  ausencia de preguntas codificadas y parejas sin coincidencias bloqueados.
- Resultado: 97 pruebas correctas y una prueba opcional de generacion XLSX
  omitida. Las 51 referencias congeladas conservan sus hashes. `git diff --check`
  sin errores.
- No se ejecuto nuevamente el analisis completo, no se modificaron exportaciones
  originales, no se enviaron correos ni se altero la encuesta en LimeSurvey.
