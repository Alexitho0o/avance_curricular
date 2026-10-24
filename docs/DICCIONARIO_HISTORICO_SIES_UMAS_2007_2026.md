# Diccionario histórico SIES y UMAS 2007–2026

## Edición vigente H8

La [fase 8](fase_8_excel_diccionario_gobernado.md) reemplaza el libro inicial
descrito abajo. Usa los ocho parámetros del maestro H5/H7 y elimina el selector
manual de versión. Un candidato único continúa pendiente de evidencia. El libro
anterior y esta descripción se conservan como antecedentes, no como reglas
vigentes de búsqueda. Se mantienen los nombres literales de oferta 2026.

Solicitud del 2026-10-15: entregar un Excel independiente con el diccionario y
ejemplos del cruce entre códigos SIES y campos UMAS. Debe incluir versiones
históricas, aunque no tengan estudiantes activos ni impartición en 2026.

## Contrato

- Usar los nombres literales de `oferta 2026.xlsx` para las claves que existen
  en ese archivo, sin agregar Continuidad, corregir acentos ni reformularlos.
- Conservar por separado el nombre histórico informado por cada fuente y año,
  el nombre UMAS `NOMBRE_L`, el tipo de plan y la versión. No trasladar un nombre
  actual a un código histórico distinto por semejanza.
- Universo del diccionario: unión de claves observadas en MRUN institucional
  2007–2026, oferta histórica disponible 2010–2026, oferta 2026 y catálogo operativo.
  La ausencia de observación MRUN no excluye una oferta. La ausencia de una clave
  en oferta 2026 no prueba su eliminación histórica.
- Mantener las claves históricas que no tengan estructura SIES moderna y marcar
  los componentes ausentes. No inventar sede, carrera, jornada ni versión.
- Expandir las equivalencias explícitas del puente: una fila por llave UMAS y
  candidato SIES. Exponer las búsquedas ambiguas, sin elegir primera fila ni
  versión máxima. Las equivalencias del catálogo 2026 no se declaran vigentes
  retroactivamente para todo el período 2007–2026.
- Distinguir año observado/de matrícula, año de ingreso y versión curricular.
  La presencia de condiciones temporales en el código no prueba que estén
  pobladas en sus fuentes. Mostrar la evidencia existente y las brechas.
- Incluir ejemplos de combinaciones observadas sin RUT, MRUN, CODCLI, nombres
  de estudiantes, correos ni otros identificadores de personas.
- Las hojas deben permitir búsqueda por código único y por componentes,
  conservar fuente, fila y año, y mostrar qué datos adicionales necesita una
  búsqueda UMAS para resolver una sola versión.

## Implementación y comprobación

La preparación es auxiliar y no modifica motores, puentes ni catálogos
congelados. El código nuevo en `scripts/` mantiene el layout operativo existente.
El Excel se autorará con Artifact Tool y contendrá exclusivamente diccionarios,
ejemplos sin identidad, instrucciones de búsqueda y procedencia.

Comprobar cobertura de todas las fuentes, unicidad al grano declarado,
coherencia entre componentes y código completo, nombres literales de oferta,
ausencia de datos personales y resultados de búsquedas únicas/ambiguas.
Un resultado sin evidencia no se rotula como validado.

## Resultado del corte 2026-10-15

El libro independiente contiene 141 identificadores: 139 con estructura SIES
moderna y dos identificadores históricos de 2008 sin componentes verificables.
La unión incluye 139 códigos en oferta histórica y 106 observados en MRUN;
124 están en la oferta 2026 indicada por el usuario. Los 124 nombres se
conservan literalmente, incluidos mayúsculas y acentos de la fuente.

Se incluyen 257 relaciones candidatas UMAS, 747 observaciones anuales de oferta,
472 combinaciones de atributos académicos proyectadas desde MRUN, 159 ejemplos
UMAS sin identidad, 23 fuentes y 35 reglas o hallazgos. Estas cantidades son
filas de diccionario o evidencia académica; no son cifras de estudiantes.
Las 747 filas de oferta institucional se comprobaron contra las filas del
Excel original de oferta histórica, además de comprobar su hash.

La modalidad se toma de un campo explícito; nunca se infiere a partir de la
jornada. Modalidad y tipo de plan disponen de códigos comparables y de una
columna adicional que conserva el valor literal de la fuente. Las definiciones
se verificaron entre fuentes por código exacto y están en la hoja Reglas.

### Límites que quedan visibles

- El puente del catálogo 2026 no contiene condiciones temporales pobladas.
  Su código soporta límites de año, pero no hay evidencia para aplicarlos a
  todas las versiones históricas ni para equiparar año de ingreso y versión.
- CILOG, jornada O, sede RE y nombre INGENIERIA EN LOGISTICA conserva dos
  candidatos (V1 y V2); ILOG con los mismos campos tiene un candidato (V1).
  La consulta no devuelve código cuando hay más de uno. Ingresar una versión
  restringe candidatos, pero no acredita por sí mismo la malla del estudiante.
- Los códigos históricos de Ciberseguridad I162S2C46J2V2 e I162S2C46J4V2 se
  conservan aunque no estén en el catálogo operativo 2026.
- DCBS, DFSK, DICD y DRID tienen equivalencias, pero no un ejemplo de matrícula
  UMAS observado en el corte revisado. Esa ausencia se marca expresamente.
- Hay evidencia de MRUN 2007–2009, pero no se dispone de la oferta completa de
  esos años; no se puede acreditar oferta que no haya tenido matrícula observada.

## Reproducción y validación

`scripts/preparar_diccionario_sies_umas_2007_2026.py` recibe `--evidencia` y
`--salida`. La carpeta de evidencia contiene siete proyecciones JSON sin
identificadores de personas, con fuente, hash y localizadores originales.
El snapshot se conserva en `data/diccionario_sies_umas/20261015/evidencia/`.
El preparador valida el grano y la cobertura de este corte antes de producir
los descriptores del libro.

`scripts/generar_diccionario_sies_umas.mjs` recibe el JSON preparado, la ruta
de salida XLSX y una carpeta temporal de vistas. Se ejecuta con el runtime
bundled de Node y `@oai/artifact-tool`, mediante un enlace `node_modules` en una
carpeta temporal; no instala dependencias en el repositorio.

La hoja Consulta incluye una búsqueda por Código Único y otra por clave UMAS
del catálogo 2026. Las seis hojas de datos tienen tablas nativas, filtros y
paneles congelados. Las fórmulas usan rangos acotados y guardas de unicidad.
La búsqueda UMAS utiliza XLOOKUP exacto, compatible con Excel moderno. Se
verificaron 13 resultados interactivos, incluyendo ambigüedad, versiones
explícitas, claves inexistentes, campos pendientes y rechazo de extrapolación
a otro año. Se verificaron valores, cachés, tablas y paneles del XLSX exportado;
no se ejecutó recálculo en la aplicación nativa Excel.

El libro se entrega en la carpeta 2026 indicada por el usuario como
`DICCIONARIO_CRUCE_SIES_UMAS_2007_2026.xlsx`. Las auditorías y el manifiesto del
archivo entregado se conservan junto al snapshot. No se modifica el motor
oficial, el puente congelado, los catálogos ni las cargas SIES.
