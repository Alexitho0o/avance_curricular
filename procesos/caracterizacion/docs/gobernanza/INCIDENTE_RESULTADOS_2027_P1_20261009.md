# Incidente: resultados vacios 2027 P1

Decision posterior del usuario: no existen respuestas aun, pero deben generarse las listas operativas. Se incorporo el modo SIN_RESPUESTAS_CONFIRMADAS exclusivo 2027 P1, sin inventar respuestas. El estado original de ERROR documentado debajo se conserva como historial. El comando ya puede generar listas usando matricula y tokens, bajo las comprobaciones de `MODO_SIN_RESPUESTAS_2027_P1.md`.

Fecha: 2026-10-09. Ejecucion: `2027_P1_125058`. Encuesta: `141234`.

## Evidencia y causa

El archivo seleccionado `Downloads/results-survey141234.xlsx` tiene cero bytes; su modificacion observada es 2026-10-09 12:45:03. No contiene estructura Excel ni respuestas. No se encontro otra copia de resultados de esa encuesta en Descargas.

La corrida fallo en `caracterizacion.py:1690`, al preseleccionar la pareja LimeSurvey. `read_input_frame` llamaba a pandas/openpyxl usando solamente la extension. El lector intento abrir un ZIP XLSX inexistente y emitio `BadZipFile`. El resolutor operativo previo habia validado existencia, nombre e ID, pero no contenido ni tamano; esa comprobacion era insuficiente.

La ejecucion termino con ERROR y codigo 1. `02_SALIDAS` no contiene informes. Los siete archivos contados como salidas pertenecian a `04_AUDITORIA`; habia ocho archivos en total incluyendo el log. No se publico copia en Escritorio ni se archivaron entradas. Estos archivos documentan una corrida fallida, no resultados estudiantiles.

## Correccion

- `caracterizacion_archivos.py` verifica archivos no vacios y la estructura/integridad del contenedor XLSX/XLSM.
- El resolutor operativo aplica estos controles antes de iniciar el pipeline.
- El lector LimeSurvey informa `LimeSurveySelectionError` con el nombre y la causa del problema.
- Los resultados admitidos por el resolutor coinciden con el selector actual: XLSX/XLSM. No anunciar CSV como formato de resultados admitido.
- El resumen del ejecutor diferencia informes operativos y auditorias, y anuncia una interrupcion cuando el codigo de salida es distinto de cero.

El archivo original y la corrida fallida permanecen intactos. No se fabrican respuestas ni cabeceras para eludir la validacion. Cero bytes no acredita que la encuesta tenga cero respuestas; un libro valido con cabeceras y cero registros es un caso distinto, reportado separadamente por el selector.

## Validacion

Pasaron 9 pruebas de comandos operativos, 16 pruebas de seleccion LimeSurvey y 20 pruebas de fuentes congeladas P2. La validacion real del resolutor devuelve codigo 3 y un mensaje especifico de cero bytes, sin ejecutar caracterizacion.py. La sintaxis Bash y git diff --check son correctos. Los 51 archivos de referencia 2026 siguen intactos.

## Paso necesario para obtener informes

Exportar nuevamente los resultados reales de la encuesta 141234 en XLSX y comprobar que el archivo sea un libro Excel legible. Despues, repetir el mismo comando de financiamiento 2027 P1. Hasta disponer de una entrada valida no puede confirmarse una corrida de informes terminada correctamente.
