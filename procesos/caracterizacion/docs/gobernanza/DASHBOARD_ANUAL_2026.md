# Dashboard anual de caracterizacion 2026

## Alcance y precedencia

Decision del usuario del 2026-10-15: incorporar el diseno aprobado al generador
del analisis anual, no editar los reportes anteriores. Esta revision de
ANUAL_INTEGRADO_2026-v2 cambia presentacion y navegacion, no elegibilidad,
instrumentos, catalogos ni cierre FCU 2026. Los numeros de las maquetas no son
resultados. Los libros se calculan exclusivamente desde las fuentes de la corrida.

Se conservan las hojas originales del consolidado, el libro de auditoria,
02_SALIDAS/P1/P2/P3 y todos los respaldos de 03_RESPALDOS. No se prometen solo dos
archivos: el inventario final enumera los integrados y cada salida original.

## Vistas y unidades

| Hoja | Contenido | Unidad y controles |
|---|---|---|
| Panel ejecutivo | Personas, completas, participacion, sin respuesta; estados por periodo y tasas por sector | RUT unico en la seleccion. No sumar personas entre periodos o sectores solapados. |
| Cobertura | Matriz sector-periodo, ranking de carreras y detalle completo | Brecha = personas sin respuesta completa, incluidas incompletas. Orden recalculado al filtrar. |
| Explorador preguntas | Grupo y codigo dependiente, distribuciones P1/P2/P3 y detalle de todas las opciones | Respuestas completas. Base valida y ausentes por codigo literal y periodo; no convertir saltos en respuestas negativas. |
| Panel financiamiento | Todas las alternativas identificadas, N y porcentaje por periodo | Seleccion multiple: los porcentajes pueden sumar mas de 100%. No sumar denominadores ni personas entre alternativas. |
| Panel rendimiento | Media, matriculas con notas, cobertura, detalle por nivel y distribucion de promedios | Matriculas, no personas. Promedios de notas finales validas del ano segun politica existente; no promedio previo. |
| Panel sectorial | Sector elegido, participacion por periodo, modalidades y carreras del sector | Personas para participacion; matriculas para modalidad. El selector local se intersecta con los filtros comunes. |

La distribucion de rendimiento usa tramos menor a 4,0; 4,0 a menos de 5,0;
5,0 a menos de 6,0; y 6,0 a 7,0. Solo cuenta matriculas con notas validas.
No implica cierre academico anual si faltan periodos de notas.

## Filtros y navegacion

- Filtros conserva inclusion Si/No por periodo, sector, modalidad, sede, carrera
  y jornada. Admite las combinaciones P1/P2/P3 y seleccion vacia. El encabezado
  de cada panel refleja la seleccion activa; no son segmentadores de Power BI.
- Explorador preguntas: C6 selecciona grupo y J6 codigo. Al cambiar grupo, elegir
  un codigo de ese grupo. Si queda un codigo del grupo anterior, se vacia el
  detalle y aparece un aviso; nunca se muestran respuestas del grupo incorrecto.
- Panel sectorial: D6 selecciona el sector local, sin ampliar los filtros comunes.
- Los enlaces internos superiores llevan a Filtros y a los seis paneles.
- Las tablas fuente y auxiliares no son formularios de captura. Cambiar las
  fuentes o pertenencias requiere regenerar con el comando del proyecto.

## Presentacion y trazabilidad

Fondo blanco, cabeceras petroleo, azul/verde/ambar para series y gris para
ausencia de respuesta. Todas las celdas de tabla quedan centradas horizontal
y verticalmente. Medias con formato numerico 0.0; porcentajes con un decimal
salvo 0% y 100%. Los valores numericos conservan precision, sin ROUND en fuentes.

Los graficos son objetos nativos vinculados a celdas con formulas, no capturas.
Se conservan las tablas debajo de los graficos, codigos y denominadores.
El explorador grafica las primeras diez opciones en orden del registro; el
detalle contiene todas. Financiamiento grafica todas las alternativas detectadas.
Para evitar repetir el enunciado en cada barra, una subpregunta entre corchetes
se presenta con su texto literal; el encabezado completo permanece en Preguntas,
Financiamiento y las hojas de respuestas. No se homologan opciones por parecido.

Marcadores distintos: Sin notas disponibles al corte = no hay notas finales
validas al corte; No aplica = denominador cero;
No disponible = codigo ausente en ese periodo; Tipo no verificado = inventario
insuficiente para interpretar el porcentaje. Nunca se reemplazan por cero.

La falta de notas no es un error ni una calificacion cero. Las filas sin nota
mantienen `PROMEDIO_AC_REFERENCIA` vacio; las columnas auxiliares de suma y
denominador aportan cero solo para excluirlas del promedio. Por eso no alteran
la media, la cobertura ni los totales de matriculas. La etiqueta se aplica solo
a la presentacion de rendimiento cuando el denominador de notas es cero.

## Implementacion y evidencia

- `scripts/paneles_analisis_anual.py`: definicion de vistas, registros auxiliares
  y controles independientes a partir del modelo anual.
- `scripts/renderizar_paneles_anual.mjs`: estilo y graficos nativos.
- `scripts/consolidar_analisis_anual.py`: integracion, enlaces internos OOXML
  y verificacion del XLSX guardado sin reescribirlo con openpyxl.
- `scripts/exportar_analisis_anual.mjs`: recalculo, pruebas de filtros/selectores,
  render y exportacion mediante Artifact Tool.
- `scripts/ejecutar_analisis_anual.py`: publicacion y verificacion de visibilidad
  de la nueva copia en macOS.

La entrega elimina UF_HIDDEN y el bit invisible de FinderInfo SOLO en la nueva
copia. Conserva el resto de metadatos, verifica nuevamente visibilidad y hashes
del contenido y registra el resultado en el manifiesto. No mueve ni modifica
archivos historicos ni reinicia Finder. La publicacion informa ruta e inventario
real, o fallo explicito; no declara exito por existir solamente la carpeta.

Pruebas reproducibles, sin ejecutar datos reales:

```sh
ANUAL_TEST_XLSX=1 python3 -m unittest discover -s tests -p '*analisis_anual*.py'
python3 -m unittest discover -s tests -p 'test_enriquecimiento_anual.py'
python3 -m unittest discover -s tests -p 'test_comandos_operativos.py'
python3 scripts/gobernanza/verificar_separacion_fcu.py
```

Los fixtures prueban filtros sin casos, personas repetidas entre periodos,
ranking, selectores de grupos/carreras, once alternativas con etiquetas largas,
precision decimal, formulas exportadas, graficos, enlaces y metadatos Finder.
`validacion_excel.json` registra controles comunes/locales y
`validacion_archivos_exportados.json` verifica el libro guardado.
`nativeExcelTested=false` distingue estas verificaciones de una prueba
interactiva en Microsoft Excel. No afirmar esa prueba sin realizarla.

Verificacion del 2026-10-15: 89 pruebas focalizadas (43 de analisis/paneles,
16 de enriquecimiento y 30 de comandos). Dos exportaciones sinteticas con
20 selecciones de filtros, una prueba de reordenamiento y ocho cambios de
selectores locales por libro; revision visual de los seis paneles y distribucion
de notas. Las 51 referencias congeladas pasaron sin diferencias. No se ejecuto
el analisis real ni se publico una entrega de datos sinteticos en Escritorio.

## Correccion de capacidad de exportacion

El incidente posterior de memoria invalido la suficiencia de los fixtures pequenos
para acreditar el volumen real. Causa, solucion y prueba de volumen:
`INCIDENTE_MEMORIA_EXPORTACION_ANUAL_20261015.md`. Se mantiene el contrato visual
y numerico anterior; no se modifica el cierre FCU.

`Indices panel` (rotulada `Índices panel` en Excel) comparte las posiciones del
explorador. Las respuestas originales se completan por filas en sus mismas hojas
mediante `scripts/completar_fuentes_excel_anual.py`, despues de calcular/exportar
con Artifact Tool. Sus columnas auxiliares mantienen formulas y resultados.
No editar estos literales como si fueran entradas interactivas: regenerar el modelo.
Los filtros siguen operando sobre las formulas auxiliares calculadas.

La auditoria incorpora `escritura_fuentes_incremental.json` y
`recursos_generador.json`. El pico observado de heap en puntos de control no
equivale al maximo continuo ni a la RAM total; se informa ademas maxRSS del proceso.
La lectura final celda a celda y las validaciones existentes siguen siendo
obligatorias antes de publicar.

La revision de capacidad paso la prueba sintetica de volumen y 94 pruebas
distintas en total. El registro de resultados y sus limites se detalla en el
documento del incidente; la ejecucion real queda reservada al usuario.

```sh
ANUAL_STRESS_XLSX=1 python3 -m unittest discover -s tests -p 'test_memoria_analisis_anual.py'
```

## Ejecucion del usuario

El comando habitual no cambia: `bash ./procesar_analisis_anual.sh 2026`.
Si P1/P2/P3 ya finalizaron correctamente, se puede usar
`--reanudar-consolidacion <carpeta_corrida>` para reutilizar las entradas
archivadas: exige codigos 0 y hashes intactos, no consulta Descargas ni ejecuta
otra vez los tres periodos. Genera una entrega nueva con manifiesto e inventario.
No ejecutar el pipeline real durante desarrollo ni sobrescribir el cierre FCU.
