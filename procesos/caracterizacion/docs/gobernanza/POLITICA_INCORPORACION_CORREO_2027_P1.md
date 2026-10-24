# Incorporacion 2027 P1: correo pendiente sin bloqueo global

Decision posterior del usuario, 2026-10-13: [SEPARACION_COMUNICACION_ANALISIS_2027_P1.md](./SEPARACION_COMUNICACION_ANALISIS_2027_P1.md) reemplaza la ubicacion del estado de incorporacion. Informe_Categorias vuelve a ser comunicacion breve; el estado se publica en otro Word y Excel dentro de05_ANALISIS. Tambien cambia la elegibilidad a primer ingreso institucional probado con historico completo. La politica de correo individual pendiente se mantiene. No restablecer el estado dentro del Word de correo.

Politica: `INCORPORACION_2027_P1_CORREO_PENDIENTE-v1`. Autorizacion expresa del usuario: 2026-10-13. Esta decision sustituye el bloqueo global por Mail_Inst ausente/invalido documentado inicialmente en `INCIDENTE_MAIL_INST_2027_P1_20261013.md`. No restablecer ese bloqueo global en revisiones futuras. El control final de cada CSV sigue rechazando filas sin correo institucional valido.

## Regla operativa

Los filtros de ano, periodo, cohorte, vigencia/situacion, firma, programas y RUT administrativos preceden a la clasificacion. Duplicados elegibles, tokens vacios/repetidos, columnas requeridas ausentes, errores de lectura, resultados corruptos, incoherencias y cambios en la referencia congelada siguen bloqueando por estructura/integridad.

Dentro de los elegibles que no aparecen en los **tokens actuales**, se evalua exclusivamente Mail_Inst. MAIL personal nunca es fallback. Correo ausente o invalido mantiene al estudiante pendiente de correo institucional; no excluye su matricula ni detiene la corrida. La sintaxis y los caracteres de control/formato se verifican; solo se recortan espacios externos. Una columna Mail_Inst ausente sigue siendo un error estructural.

Se reconstruye el plan en cada corrida desde la fuente actual. Un CSV previo no acredita incorporacion. Cuando llega un correo valido, la fecha original de matricula determina la salida: dentro de la ventana cerrada, diario; anterior al inicio, acumulado; posterior al corte o invalida, pendiente de fecha. La ventana existente `ventana_habil_scl()` usa el calendario gobernado y excluye el dia de ejecucion. Una matricula de hoy no es un rezagado.

Ambos CSV tienen las 14 columnas gobernadas, solo correos validos de Mail_Inst y tokens unicos. Diario y acumulado no se solapan. No se generan CSV vacios, incluido el acumulado.

## Seguimiento Excel y Word

El seguimiento reutiliza el nombre del espejo Excel acumulado cuando contiene pendientes de fechas anteriores. Cuando no hay pendientes anteriores, usa `Seguimiento_incorporacion_LimeSurvey_2027_P1_<fecha>.xlsx`. Nunca se genera un Excel acumulado vacio ni una estructura con hojas vacias para simular estudiantes.

La hoja `Pendientes LimeSurvey` conserva **todos** los elegibles sin token una vez, con CODCLI, RUT/TOKEN, fecha de matricula, fecha de ejecucion, brecha de dias, estado del correo, motivo, estado de incorporacion e indicadores temporales. El Excel es seguimiento, no un archivo importable; puede incluir filas que no aparecen en ningun CSV. El motivo primario de correo no elimina el indicador simultaneo de fecha.

Los pendientes de firma se mantienen en una hoja separada `Pendientes firma`. Se conserva el numero de registros y de personas unicas; las personas con otra matricula elegible se identifican como solapamiento y no se suman al universo de incorporacion. Correo y firma simultaneos mantienen ambos indicadores. Los totales por motivo no se suman para obtener una union.

El Word interno `Estado_incorporacion_LimeSurvey` en `05_ANALISIS` incorpora el estado, con correo valido, disponibles por fecha, pendientes de correo, diario/acumulado, pendientes de fecha, firma, solapamientos y conciliacion. En modo sin respuestas genera un Word operativo y el texto habitual de resumen de matricula, sin resultados de encuesta ni financiamiento. Los casos individuales solo quedan en el Excel operativo privado y la auditoria `.local/auditoria_correos/`, nunca en esta gobernanza ni en GitHub.

Conciliaciones obligatorias:

```text
ELEGIBLES = CON_TOKEN_ACTUAL + SIN_TOKEN_ACTUAL
SIN_TOKEN_ACTUAL = CORREO_VALIDO + CORREO_PENDIENTE
CORREO_VALIDO = DIARIO + ACUMULADO + FECHA_PENDIENTE
SIN_TOKEN_ACTUAL = DIARIO + ACUMULADO + CORREO_PENDIENTE + FECHA_PENDIENTE
```

`FECHA_PENDIENTE` en la ultima identidad cuenta solo correo valido. Los casos con correo y fecha pendientes estan en CORREO_PENDIENTE y conservan el indicador temporal, sin contar dos veces. Firma pendiente no se suma a estas identidades.

## Implementacion y separacion FCU

- `caracterizacion_incorporacion.py`: plan puro compartido, seguimiento, CSV y apartado Word.
- `caracterizacion_sin_respuestas.py`: genera el Word operativo y consume el mismo plan. `token_import_frame()` mantiene el bloqueo final frente a una fila no exportable entregada por error; el plan separa esas filas antes de exportar.
- `scripts/gobernanza/resolver_fuentes_operativas.py`: verifica fuentes/integridad y anuncia correo pendiente como advertencia.
- `caracterizacion_financiamiento_2027.py`: adaptador exclusivo 2027 P1. Comprueba las 51 referencias congeladas; aplica anclas unicas y compilacion en memoria sobre `caracterizacion.py`. Sustituye solo incorporacion, exportaciones relacionadas y apartado Word para 2027. Registra hashes de referencia, adaptador y fuente efectiva en `04_AUDITORIA/ADAPTADOR_2027.json`. El archivo congelado en disco no cambia. Un ancla ausente/ambigua bloquea por estructura.
- `procesar_financiamiento_diario.sh`: selecciona el adaptador solo para 2027 P1 con respuestas; mantiene el modo sin respuestas cuando procede y no cambia la ejecucion 2026.

Pruebas focalizadas en `tests/test_incorporacion_2027.py`, `tests/test_correos_institucionales.py` y `tests/test_sin_respuestas.py`. Cubren falta/formato/Unicode, recuperacion, antiguos, tokens actuales, duplicados, firma, motivos simultaneos, fines de semana/feriados/dia actual, salidas vacias y ausencia de fallback personal. No requieren analisis anual ni corridas reales de otros periodos.

La causa inicial permanece: una celda Mail_Inst vacia en la fuente real, cuya identidad/coordenada se conserva en auditoria privada. La nueva politica permite avanzar con los demas estudiantes sin inventar ese dato.

## Verificacion real del 2026-10-13

La ejecucion final repitio el mismo comando operativo, con exclusion de diplomados y sin firma, VERBOSIDAD=1 y STOP_AFTER_FINANCIAMIENTO=1. Corrida `2027_P1_090610`, codigo **0**, corte despues de BLOQUE 6.bis. No se ejecuto el analisis anual ni se procesaron otros periodos. La primera corrida de validacion `2027_P1_085827` se conserva como evidencia; la entrega final corresponde a la copia de 09:06:30.

Fuentes seleccionadas: DATOSDEALUMNOS_11923.xlsx, tokens_141234.csv y results-survey141234.xlsx. El auxiliar opcional PROMEDIOSDEALUMNOS_7804.xlsx se archivo sin modificar. Los resultados contienen 15 filas, de modo que se uso el flujo con respuestas; el modo sin respuestas quedo probado mediante fuentes sinteticas. Los hashes de las fuentes se registran en las entradas archivadas y en el manifiesto privado del correo pendiente.

| Concepto | Total |
| --- | ---: |
| Registros fuente del periodo | 266 |
| Excluidos unicos | 4 |
| Excluidos por estado/situacion | 3 |
| Pendientes de firma fuera de elegibles | 1 |
| Elegibles | 262 |
| Elegibles con token actual | 235 |
| Elegibles sin token actual | 27 |
| Correos validos y disponibles | 26 |
| Pendientes de correo | 1 |
| CSV diario | 26 |
| CSV acumulado | 0, no generado |
| Correo valido pendiente de fecha | 0 |

Ventana gobernada: **2026-10-09 a 2026-10-12**, por fin de semana y feriado del 12. El dia 13 queda excluido. Todos los casos listos corresponden a esa ventana; no hay rezagados listos y no se genero acumulado CSV ni Excel vacio. El seguimiento no vacio usa el nombre separado `Seguimiento_incorporacion_LimeSurvey`.

Los 27 pendientes se conservan una vez en `Pendientes LimeSurvey`; la firma pendiente figura en `Pendientes firma` con sus propios indicadores y no se suma a esos 27. En esta fuente no existe solapamiento entre firma pendiente y elegibles, ni correo pendiente entre la persona sin firma. 266 = 262 elegibles + 3 excluidos por estado + 1 sin firma; 262 = 235 con token + 27 sin token; 27 = 26 listos + 1 pendiente de correo.

Entregas finales, con copia verificada por hashes:

```text
/Users/alexi/Desktop/Caracterizacion_2026-10-13_2027_P1_090630/02_SALIDAS/
  Informe_Categorias_2027_P1_20261013.docx
  Seguimiento_incorporacion_LimeSurvey_2027_P1_20261013.xlsx
  + Nuevos inscritos hoy_2027_P1_20261013.csv
```

Expediente original:

`/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-10-13/2027_P1_090610/`

El Word incluye el apartado requerido, la firma pendiente y las conciliaciones; su introduccion dice «listos para incorporar mediante el CSV», sin afirmar una incorporacion efectiva por generar archivos. Se revisaron visualmente sus cuatro paginas despues de renderizar con el LibreOffice del runtime Codex. Se repiten cabeceras y se evita partir filas de tabla entre paginas.

Se verificaron los 26 emails por TOKEN contra Mail_Inst del universo elegible de la fuente: coincidencia exacta despues de recortar espacios externos, sin MAIL personal. CSV con 14 columnas y tokens unicos. El caso sin correo permanece en el Excel y no aparece en el CSV. La union CSV + correo pendiente coincide con las 27 filas del seguimiento; no hay desapariciones ni duplicados.

Pasaron **75 pruebas focalizadas**: 13 de incorporacion, 10 de correos, 7 de modo sin respuestas, 9 de comandos, 16 de seleccion LimeSurvey y 20 de fuentes P2. La regresion de recuperacion verifica tanto diario como acumulado segun fecha original, repeticiones de corrida sin token actual, y retiro del CSV una vez presente en tokens. Tambien se probo firma duplicada contando personas una sola vez, errores estructurales, Unicode y salidas sin listos. Las 23 pruebas de incorporacion/correo tambien se repitieron con el Python 3.14 y las dependencias efectivamente usadas por el comando real: todas pasaron. Compilacion Python, sintaxis Bash y `git diff --check` correctos.

Los **101 archivos previos resguardados** (incluida la primera corrida de esta intervencion) permanecen byte-identicos. Las **51 referencias congeladas de FCU 2026** se verificaron antes y despues sin diferencias, incluido caracterizacion.py. No se actualizaron hashes de referencia para ocultar cambios. No se realizo commit, push, incorporacion efectiva en LimeSurvey ni envio de correo.

Validacion individual y evidencia de comprobaciones: `.local/incorporacion_2027_20261013/VALIDACION_FINAL.json`; auditoria del correo pendiente en la ruta privada indicada por `ESTADO_INCORPORACION_2027_P1_20261013.json` de la corrida. No publicar esos datos individuales. Los documentos de gobernanza solo contienen metadatos y totales.

**Operacion posterior:** puede seguir utilizandose el mismo comando. El correo real sigue pendiente de completar en la fuente, pero ya no impide el informe ni la incorporacion de los demas. En cada corrida se reevalua sin considerar que un archivo previo equivalga a un token realmente incorporado.
