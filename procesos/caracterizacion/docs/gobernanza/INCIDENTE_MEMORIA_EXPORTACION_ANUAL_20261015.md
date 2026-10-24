# Incidente de memoria al exportar el dashboard anual

## Evidencia y alcance

La recuperacion `20261015_171418_124042` reutilizo los periodos de
`20261015_141035_172286`. El log aportado por el usuario acredita calculo,
57 comprobaciones de filtros y 12 cambios de selectores, pero Node termino con
`heap out of memory` y SIGABRT al exportar el libro principal, con limite de
6144 MiB. Esto NO acredita una entrega terminada. Se conservaron P1/P2/P3;
no se debe repetir su ejecucion para resolver este incidente.

La inspeccion de solo lectura encontro 2520 filas de base, 25161 de conteos,
2238 respuestas entre los tres periodos y 254 columnas por hoja de respuestas.
El explorador contenia miles de busquedas repetidas sobre el registro de opciones.
Materializar los literales, sus formatos y ese grafo de formulas dentro del motor
dejaba poco margen para la serializacion XLSX. Las pruebas pequenas anteriores
verificaban resultados, pero no acreditaban capacidad a este volumen.

## Correccion gobernada

1. Agrupar las opciones por pregunta y calcular una vez su inicio y cantidad.
   `Índices panel` comparte las posiciones que utiliza el explorador. Se conservan
   orden de opciones, codigos, etiquetas, escalas y denominadores.
2. Calcular con Artifact Tool todas las formulas, resultados almacenados, estilos
   y graficos. Las hojas originales conservan sus columnas auxiliares calculadas.
3. Completar los literales inmutables de Respuestas P1/P2/P3 por filas dentro del
   mismo XLSX. El transporte XML/ZIP es una solucion puntual a la limitacion de
   exportacion observada, no otro motor de calculo ni un reemplazo del dashboard.
   Conserva los demas miembros ZIP, las formulas y sus resultados; mantiene filtro
   nativo, alineacion central y literalidad de cadenas que comienzan con `=`.
4. Bloquear una futura formula que lea columnas literales diferidas. Las formulas
   actuales solo leen las columnas auxiliares de inclusion; las frecuencias se
   derivan del modelo de perfiles. No se permite diferir una entrada de calculo.
5. Liberar temporales entre verificaciones y antes de exportar; aplicar alturas
   repetidas por bloques. El limite de Node permanece en 6144 MiB.
6. Validar el archivo completado celda a celda, formulas, graficos y filtros antes
   de publicar la nueva copia. Un archivo intermedio o una carpeta no son exito.
   Recorrer cada panel una sola vez al leer su XML, sin volver a parsearlo por
   cada celda verificada. Esta optimizacion conserva todos los controles.

No se cambia elegibilidad, periodo, modalidad, notas, contenido del instrumento,
salidas historicas ni ninguna referencia del cierre FCU 2026. No se editan
entregas existentes. Ningun dato personal se incorpora a pruebas versionadas.

## Pruebas y evidencia

La prueba optativa `test_export_at_incident_volume` utiliza exclusivamente datos
sinteticos: 2520 filas de base, mas de 25000 de conteos, 2238 respuestas con 254
columnas, 94 preguntas, 322 opciones en una pregunta y mas de 1300 opciones en
total. Verifica tres selecciones representativas, selectores locales, exportacion
y lectura final de cada celda fuente. No es una copia exacta del modelo real ni
una promesa de igual duracion. Los fixtures pequenos cubren las combinaciones
completas de filtros y los casos de borde.

```sh
ANUAL_TEST_XLSX=1 python3 -m unittest discover -s tests -p '*analisis_anual*.py'
ANUAL_STRESS_XLSX=1 python3 -m unittest discover -s tests -p 'test_memoria_analisis_anual.py'
python3 -m unittest discover -s tests -p 'test_enriquecimiento_anual.py'
python3 -m unittest discover -s tests -p 'test_comandos_operativos.py'
python3 scripts/gobernanza/verificar_separacion_fcu.py
```

La evidencia sintetica permanece en `.local/pruebas_anual_volumen`, no en
Escritorio ni en el cierre. `nativeExcelTested=false` significa que las pruebas
automaticas no sustituyen una prueba interactiva en Microsoft Excel.

Verificacion final del 2026-10-15: 94 pruebas distintas aprobadas (48 de
analisis/paneles/memoria, 16 de enriquecimiento y 30 de comandos; la prueba
optativa de volumen se ejecuto por separado). La exportacion de volumen y la
lectura final finalizaron correctamente, incluidos tres filtros representativos,
12 cambios de selectores, datos originales, dimensiones de las hojas, alineacion,
formulas almacenadas, graficos y enlaces. Pico de heap observado en puntos de
control: 3145 MiB; limite sin cambiar: 6144 MiB. No es una medicion continua del
pico ni una garantia de igual consumo para otro modelo. Una primera prueba
detecto ausencia de dimension declarada en las hojas fuente; se corrigio y se
repitio con resultado OK. Se verificaron las 51 referencias congeladas sin cambios
y los hashes de entradas de la corrida original, sin ejecutar el pipeline real.

## Recuperacion reservada al usuario

Reutilizar la corrida original con los tres periodos completos:

```sh
bash ./procesar_analisis_anual.sh 2026 --reanudar-consolidacion \
  ".local/analisis_anual/2026/20261015_141035_172286"
```

El comando exige hashes intactos de las entradas archivadas y crea una nueva
entrega. No consultar Descargas actuales ni volver a ejecutar los periodos.
Si aparece `FALLO_MEMORIA_EXCEL`, conservar el log: no anunciar entrega ni repetir
indefinidamente la misma ejecucion.
