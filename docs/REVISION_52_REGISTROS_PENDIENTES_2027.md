# Revision de los 52 registros pendientes, 2027 P1

Encargo del usuario 2026-10-13: revisar diccionarios y fuentes existentes,
completar solo equivalencias respaldadas e identificar que falta, sin inferir
modalidad ni modificar el proceso congelado 2026.

## Alcance y criterio

Los 52 pendientes son registros de matricula del archivo DatosAlumnos 11941,
agrupados en 14 CODCARPR/sede/jornada. No son las 52 combinaciones de oferta sin
alias del primer inventario, ni 52 preguntas, carreras o personas unicas.
La auditoria base es modalidad_v2, 271 registros 2027 P1, sin filtros de
elegibilidad. Se conserva su universo y se verifica el hash de la fuente.

Una coincidencia de nombre sin el sufijo SP solo identifica candidatos para
revision. No autoriza retirar SP en el resolutor, convertir jornada V a 3,
asignar modalidad ni elegir version. Para cerrar una equivalencia debe existir
un respaldo que vincule el CODCARPR y su sede/plan con el codigo SIES de 2027.
La modalidad se lee despues en MODALIDAD del registro de oferta correspondiente.

## Fuentes y limites

- DURACION_ESTUDIOS.tsv y PUENTE_SIES_COMPILADO.tsv: buscar los codigos internos
  literales, conservando su caracter historico. No modificar ni recompilar.
- DIC_CARRERAS.csv de 2025: comprobar presencia de codigo; es un diccionario de
  nombres/sectores, no una equivalencia SIES 2027.
- Oferta validada 5910, corroborada por 6047: atributos oficiales y candidatos.
- Entrega de Docencia/Rectoria etapa 2: nombres, sede, modalidad y version;
  no contiene CODCARPR. El cotejo de una fila no demuestra su enlace a U+.
- PROMEDIOSDEALUMNOS_7804, hoja matriz: contiene oferta, no CODCARPR. No usar las
  hojas personales para inventar un enlace inexistente.
- Diccionario maestro U+ SIES v1.0: UP-26 y UP-27 identifican los atributos de
  oferta y codigo unico como datos maestros requeridos; no asignan estos 14 codigos.
- IP SAN SEBASTIAN.xlsx, programas: codigos SIES y enlaces de 14 programas;
  no contiene CODCARPR ni constituye un puente U+.
- Planilla aranceles inicio 2027.xlsx y Redisenyo curricular.docx se localizaron
  en OneDrive, pero la lectura fallo por timeout y sus archivos tienen indicador
  dataless. No afirmar que se leyeron o que no contienen respaldo util.

## Entrega reproducible

`scripts/auditar_pendientes_catalogo_2027.py` genera JSON y Markdown sin datos
personales. Conserva cantidades, nombres de programas, candidatos, atributos
de oferta, localizadores y hashes de las fuentes leidas. Todos los candidatos
nominales quedan explicitamente NO_APLICADOS. El auditor no modifica catalogos,
equivalencias, registros activos ni fuentes, ni ejecuta pipelines productivos.

No crear otra version operativa si no se confirma ninguna equivalencia nueva.
Documentar por separado fuentes no disponibles y datos maestros faltantes.

Correccion de presentacion solicitada por el usuario: la tabla debe mostrar
`NOMBRE_L (DatosAlumnos)` despues de Registros, usando el valor literal ya
conservado en el JSON. Se actualiza la vista Markdown y su generador, sin
modificar la evidencia JSON, los candidatos ni las equivalencias.

## Resultado de la revision

No se encontraron nuevas equivalencias confirmables: 0 aplicadas, 52 registros
siguen pendientes. La revision separo 21 registros de candidato nominal unico,
16 con varias modalidades, 14 de nombre ampliado Veterinario y 1 TGEIN sin
coincidencia nominal. La busqueda fue sobre las fuentes leidas indicadas, no
afirma inexistencia de otro respaldo institucional.

Detalle individual con codigos SIES, sede y conteos:
[tabla de pendientes](../data/catalogos_sies/auditorias/20261013_pendientes_52/REVISION_PENDIENTES.md).
[Evidencia reproducible JSON](../data/catalogos_sies/auditorias/20261013_pendientes_52/REVISION_PENDIENTES.json).

No se necesita volver a revisar las 52 filas de estudiantes individualmente:
falta un maestro de los 14 CODCARPR/sede/plan con su CODIGO_UNICO_SIES 2027 y
vigencia. Puede respaldarlo un catalogo U+ o una equivalencia institucional
formal con el programa de oferta. La confirmacion aislada "SP es semipresencial"
no sustituye ese enlace. La brecha ya existe en UP-26/UP-27 del diccionario maestro,
hoja 20_MATRIZ_SOLICITUD_BETTERSOFT, filas 5 y 6.

Se conserva activa modalidad_v2: 219 registros con modalidad determinada;
88 codigos resueltos, 131 ambiguos y 52 sin equivalencia. No se modificaron
el catalogo, el resolutor ni su paquete en Caracterizacion.

## Verificacion de cierre

- 54 pruebas de avance_curricular y 103 pruebas focalizadas 2027 de
  Caracterizacion: correctas (157 en total).
- Las cinco referencias historicas 2026 de Matricula Unificada conservan sus
  hashes, comprobados por el auditor y las pruebas.
- `verificar_separacion_fcu.py`: 51 archivos verificados, sin diferencias,
  baseline `85e265f5d317ed6b1f2d595cc9ce415628c9c7aa94822152092052723a67e294`.
- Repeticion de la auditoria con las mismas fuentes: resultado identico; no
  sobrescribe evidencia diferente ni promueve candidatos automaticamente.
- No se ejecuto el procesamiento productivo ni se publicaron cambios en GitHub.
  Las pruebas que generan documentos usan carpetas temporales y datos de prueba.
