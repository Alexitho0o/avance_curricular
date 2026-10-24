# Inventario reutilizable de preguntas y respuestas LimeSurvey

Generador: `scripts/exportar_instrumento_limesurvey.py`. Constructor de Excel: `scripts/exportar_instrumento_limesurvey.mjs`.

## Salida

El Excel tiene dos hojas planas, sin colores:

- Preguntas: una fila por pregunta, en su orden real, con grupo, codigo, enunciado, tipo, resumen de respuestas, subpreguntas, campo Otro y archivo fuente.
- Detalle: todas las opciones y subpreguntas, con su codigo literal, texto, pregunta padre, escala y procedencia. Las opciones de una escala de matriz se listan una vez y se aplican a sus subpreguntas.

Las listas extensas, como paises o anos, se muestran completas en Detalle. Preguntas de texto/numero/fecha se identifican como entrada libre, sin fabricar opciones. El campo Otro activado se conserva. Las alternativas nativas de Si/No y matrices de 5/10 puntos se identifican como propias del tipo LimeSurvey, distintas de alternativas explicitas en el XML. No se agrega una opcion Sin respuesta basandose solo en obligatoriedad: su visualizacion depende tambien de la configuracion de encuesta, que un LSG de grupo puede no contener.

El orden se obtiene de group_order, question_order y sortorder/scale_id, no del numero del codigo ni del orden alfabetico de archivos. Los textos HTML se convierten a texto legible, conservando codigos, acentos, saltos y contenido. Scripts y estilos no se ejecutan ni se presentan como enunciados. Este inventario no clasifica FCU/institucional ni modifica el instrumento.

## Comando actual, 2027 P1

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN"
python3 scripts/exportar_instrumento_limesurvey.py \
  --anio 2027 --periodo 1 \
  --entrada "/Users/alexi/Downloads" \
  --patron 'limesurvey_group_64[3-9].lsg' --registrar
```

Este patron selecciona solo los grupos 643 a 649 de 2027 P1. No usar `limesurvey_group_???.lsg` en Descargas: ahora tambien contiene 547 a 553 de 2026 P2. Para otros instrumentos, usar una carpeta exclusiva o pasar los archivos exactos mediante --archivos.

## Comando 2026 P2

```bash
python3 scripts/exportar_instrumento_limesurvey.py --anio 2026 --periodo 2 --registrar \
  --archivos /Users/alexi/Downloads/limesurvey_group_547.lsg \
  /Users/alexi/Downloads/limesurvey_group_548.lsg \
  /Users/alexi/Downloads/limesurvey_group_549.lsg \
  /Users/alexi/Downloads/limesurvey_group_550.lsg \
  /Users/alexi/Downloads/limesurvey_group_551.lsg \
  /Users/alexi/Downloads/limesurvey_group_552.lsg \
  /Users/alexi/Downloads/limesurvey_group_553.lsg
```

Una vez archivado, tambien se puede usar --entrada con la carpeta fuentes de su version dentro de `gobernanza/instrumentos_limesurvey/2026/P2/`. Asi no depende de Descargas.

Salida por defecto: Escritorio/Preguntas_y_respuestas_LimeSurvey_<anio>_P<periodo>_<fecha>.xlsx. Si el archivo ya existe, se detiene; para otra version, indicar --salida con un nombre distinto.

## Repetir para 2026 o 2028

Guardar las exportaciones reales de cada instrumento en una carpeta exclusiva. Luego ejecutar, por ejemplo:

```bash
python3 scripts/exportar_instrumento_limesurvey.py \
  --anio 2026 --periodo 1 --entrada "/ruta/LSG_2026"

python3 scripts/exportar_instrumento_limesurvey.py \
  --anio 2028 --periodo 1 --entrada "/ruta/LSG_2028"
```

No cambiar solamente el ano del comando manteniendo los archivos 2027. El ano/periodo identifica el inventario, no transforma el contenido. Las encuestas 141234 (2027 P1) y 443299 (2026 P2) no pueden etiquetarse con otro ano/periodo. El registro permite incorporar futuros perfiles. Exportaciones que mezclan encuestas, grupos duplicados o preguntas repetidas se rechazan. Los LSG/LSS originales y el cierre 2026 permanecen intactos.

El parser admite el formato moderno con tablas question_l10ns/answer_l10ns y el antiguo con textos/subpreguntas dentro de questions. Para una exportacion LSS completa, pasar su archivo mediante --archivos. Para otro idioma, indicar --idioma; es es el predeterminado.

## Dependencias y trazabilidad

El parser usa la biblioteca estandar de Python. El Excel se construye con Artifact Tool y el Node del runtime disponible. Por defecto se buscan en la carpeta del usuario `.cache/codex-runtimes/codex-primary-runtime/dependencies/node/`. Si el entorno usa otras rutas, configurar LIMESURVEY_NODE y LIMESURVEY_NODE_MODULES. `--solo-json` permite extraer el inventario sin la dependencia de Excel.

La evidencia de generacion se conserva en `.local/inventarios_limesurvey/<anio>/P<periodo>/` (ignorada por Git). Con `--registrar` se crea ademas el paquete portable en `gobernanza/instrumentos_limesurvey/<anio>/P<periodo>/<encuesta_fecha_hash>/`: originales, modelo, versiones del codigo, Excel, comprobaciones y manifiesto SHA-256. El registro central es `gobernanza/instrumentos_limesurvey/REGISTRO.json`. No se incorporan respuestas ni registros de estudiantes. El Escritorio conserva solo la copia Excel de entrega.

Registrar no hace commit ni push automaticamente. Copia local, seguimiento en Git y publicacion remota son estados diferentes. Verificar hashes y publicar solo el paquete solicitado, sin incluir otros cambios del repositorio. `scripts/registrar_instrumento_limesurvey.py --verificar <carpeta_version>` verifica integridad y conciliacion XML/modelo/tablas. Para archivar una entrega previa sin regenerarla, usar --evidencia <carpeta_local> --excel <archivo_entregado>.

Las pruebas estan en `tests/test_exportar_instrumento_limesurvey.py`. Cubren formato antiguo, tipos nativos, orden por metadatos, rechazo de duplicados/encuestas mezcladas y limpieza de HTML.

## Entrega 2026-10-09

Archivo de entrega: Preguntas_y_respuestas_LimeSurvey_2027_P1_20261009.xlsx, en el Escritorio. Encuesta 141234, siete grupos, 91 preguntas, 138 subpreguntas y 525 opciones explicitas. Detalle contiene 688 filas, incluyendo ocho campos Otro y 17 entradas libres. Ambos contenidos fueron conciliados celda por celda con el modelo extraido. Las dos hojas fueron revisadas visualmente. Evidencia inicial: `.local/inventarios_limesurvey/2027/P1/141234_20261009_79df12c2a8ba/`.

En la primera entrega aun no se habian recibido los grupos 2026. En la segunda se recibieron 547 a 553, encuesta 443299, identificados por el usuario como 2026 P2: siete grupos, 103 preguntas, 150 subpreguntas y 535 opciones explicitas. Detalle tiene 737 filas; incluye las escalas nativas de cinco puntos. El archivo 2026 P2 sigue el mismo formato que 2027 P1.

Los dos instrumentos se archivan separadamente en el registro portable. 2026 P1 queda PENDIENTE_FUENTES; no se reconstruye desde P2 ni desde 2027. La fecha 20261009 es la de registro/entrega, no una fecha inferida de aplicacion del cuestionario. Este inventario no demuestra equivalencia historica: el futuro cruce debe revisar codigo, enunciado, tipo y opciones de cada version, sin recodificar el origen.
