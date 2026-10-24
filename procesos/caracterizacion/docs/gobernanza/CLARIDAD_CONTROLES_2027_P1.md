# Claridad de controles de matricula y respuestas 2027 P1

Politica `CLARIDAD_CONTROLES_2027_P1-v1`, autorizada por el usuario el2026-10-13
al solicitar corregir la confusion del terminal y Estudiantes_pendientes.

## Matricula temporal no equivale a trayectoria institucional

El helper historico `_registrar_auditoria_nuevos_informe(usar_ventana=True)`
llamaba antiguos al complemento de los matriculados dentro de la ventana.
Eso no demostraba una trayectoria academica previa. En2027 el terminal muestra
`[CONTROL MATRICULA]` con tipo de control, cumplen/no cumplen, fuera de ventana,
fuera de cohorte y sin clasificar. El control sin ventana exige cohorte y fecha
valida; no rotularlo como prueba de primer ingreso institucional.

La salida se llama `AUDITORIA_CONTROL_MATRICULA_2027_P1_<fecha>.xlsx` en04_AUDITORIA.
Resumen y Detalle conservan los valores originales pero usan columnas explicitas:
cumplen_control_matricula, no_cumplen_control_matricula, CUMPLE_COHORTE_Y_FECHA_VALIDA
y CUMPLE_COHORTE_Y_VENTANA. La decision institucional sigue exclusivamente en
classify_trajectories y su propia evidencia; no modificar sus reglas con esta tarea.

## Seguimiento completo y pendientes reales

Ambos archivos pertenecen a05_ANALISIS, no al Word de correo:

- `Seguimiento_respuestas_encuesta_2027_P1_<fecha>.xlsx`: todos los elegibles,
  con estado SI/NO/INCOMPLETO/vacio/desconocido conservado. No es una lista de
  personas que deben recibir un recordatorio.
- `Estudiantes_pendientes_respuesta_2027_P1_<fecha>.xlsx`: solo NO, INCOMPLETO
  y vacios, conforme a la normalizacion existente. Excluye SI. Si no hay filas,
  no generar este archivo. Los desconocidos permanecen solo en el control completo
  y se advierten para revision, no se presupone que deban contactarse.
- `CONTROL_SEGUIMIENTO_RESPUESTAS_2027_P1_<fecha>.json`: agregados y rutas,
  sin identificadores individuales, en04_AUDITORIA.

Conciliacion: elegibles = completas + pendientes de respuesta + estados por revisar.
Pendientes de respuesta = sin respuesta + incompletas. No confundirlos con los
pendientes de incorporacion (sin token), correo, firma o fecha del otro seguimiento.
El archivo de pendientes de respuesta no acredita token ni correo disponible;
no es un CSV importable ni autoriza enviar recordatorios sin verificar esos requisitos.

En modo sin respuestas todos conservan NO, por lo que seguimiento y pendientes
pueden coincidir. Se aplica el mismo helper, sin fabricar respuestas ni cambiar
elegibilidad, firma, correo, ventanas, trayectorias o fuente.

## Implementacion y resguardo

`caracterizacion_etiquetas_2027.py` transforma etiquetas y separa listas.
El adaptador aplica anclas verificadas solo en memoria al codigo congelado.
Los exporters Excel existentes conservan columnas y formato. El flujo sin respuestas
reutiliza el mismo contrato. No modificar caracterizacion.py ni el comportamiento
historico de caracterizacion_pendientes.py para corregir2027.

Los mensajes de listos antes de separar diario/acumulado y de exclusiones base
tambien declaran su alcance, sin presentarse como totales finales de rezagos o
de trayectoria. Las salidas anteriores siguen intactas y sus nombres historicos
no se renombraron retroactivamente. El comando operativo no cambia.

Las pruebas estan en tests/test_etiquetas_2027.py. Se comprueba que los valores
de la auditoria temporal sean identicos y que los SI no entren en pendientes.
La validacion de la corrida real se registra en `.local/claridad_2027_20261013/`,
con hashes de entradas/salidas y del expediente anterior. No publicar datos personales.
Estos cambios permanecen locales hasta su publicacion explicita en GitHub.

## Validacion real del 2026-10-13

El comando habitual termino con codigo0 en `2027_P1_112120`. Copia verificada:
`/Users/alexi/Desktop/Caracterizacion_2026-10-13_2027_P1_112202/`.
Seguimiento tiene257 registros; pendientes de respuesta243 (242 NO y1 INCOMPLETO),
sin los14 SI. El seguimiento completo coincide celda por celda con el listado
anterior de todos los elegibles; la lista pendiente es exactamente su subconjunto.
No se generaron los nombres ambiguos antiguos en el nuevo expediente.

Se mantienen257 elegibles,25 incorporaciones listas,1 correo pendiente y1 firma
pendiente separada. El CSV coincide byte a byte con el anterior. El contenido
ordenado de ambos Word y las cifras de negocio no cambiaron. El terminal muestra
fuera_ventana=14 en vez de antiguos=14 para esa fila temporal.

Pasaron93 pruebas focalizadas. Se verificaron32 salidas porSHA-256, los38 archivos
del expediente anterior permanecen identicos y las51 referencias FCU2026 siguen
intactas. Evidencia privada: `.local/claridad_2027_20261013/VALIDACION.json`.
No se ejecuto el analisis anual, envio de correo, cambios en LimeSurvey ni commit/push.
