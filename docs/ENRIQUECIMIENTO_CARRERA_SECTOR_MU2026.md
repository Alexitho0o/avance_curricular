# Nombre de carrera y Sector IPSS en el libro analítico MU2026

Fecha: 2026-10-15. Solicitud: agregar nombres legibles, distinguiendo jornada o
modalidad, y Sector IPSS al libro `MATRÍCULA UNIFICADA 2026.xlsx` de OneDrive.

## Adenda vigente: nombre literal de oferta 2026

Por corrección explícita del usuario, `Carrera` debe contener exactamente
`NOMBRE_CARRERA` de `oferta 2026.xlsx`, ubicado en la misma carpeta OneDrive de
Matrícula Unificada 2026. Esta regla reemplaza la presentación editorial y el
descriptor `(Continuidad)` de las revisiones anteriores: no se corrigen caja,
acentos ni denominaciones y no se añaden descriptores. El cruce conserva el
código único completo y verifica modalidad, sede, jornada y versión.

La instantánea de esta revisión reside en
`data/enriquecimiento_mu2026/20261015_oferta_literal/catalogo_carrera_sector_2026.json`.
Registra el SHA-256 de la oferta, hoja y fila exacta de cada nombre literal.
La publicación y los campos de nombre anteriores se conservan como evidencia
de soporte, sin determinar el nombre mostrado. La utilidad exige y verifica
esta evidencia literal antes de autorar columnas.

Esta corrección modifica únicamente los valores de `Carrera`. Conserva Sector
IPSS, Código Único, jornada, encabezados, formatos y las demás celdas. Se
respeta `Jornada` en T1 del detalle total, cambiado por el usuario, y el
encabezado existente en S1 de cada subconjunto. Se prepara un candidato
verificado separado del original, respaldado previamente en
`respaldos/20261015_antes_nombre_oferta_literal/`; su revisión no reemplaza el
original. Los criterios y resultados anteriores se mantienen abajo como
trazabilidad histórica.

## Alcance y criterios de aceptación

- Corregir `Carrera` y `Sector IPSS` de `06_DETALLE_TOTAL` y completar los mismos
  campos en `04_DETALLE_VIGENTES` y `05_DETALLE_NO_VIGENTES`.
- Resolver la oferta por institución 162, sede, carrera, jornada y versión,
  comprobando además la modalidad explícita y `OFERTA_SIES` de cada fila.
- Usar exclusivamente el catálogo anual 2026 (`common/catalogos_sies.py`).
  `publicacion2026.xlsx`, hoja `Hoja1`, permite elegir el nombre oficial y el tipo
  de plan cuando el catálogo conserva varios nombres internos para una clave.
- Presentar el nombre con ortografía legible e indicar continuidad cuando el plan
  la documenta. Por corrección del usuario el 2026-10-15, Carrera no contiene
  Diurno, Vespertino ni Online: se muestran en otra columna `Jornada / modalidad`.
- Aplicar el diccionario sectorial existente en Caracterización, manteniendo
  evidencia explícita de los alias utilizados. No sustituir Sector IPSS por área
  SIES, ni deducirlo de jornada, sede o modalidad.
- La columna auxiliar de la hoja principal se llama `Código Único` y contiene
  la clave completa empleada en el cruce. Sustituye el encabezado previo
  `Código Único (interno)`.
- Conservar filas, orden, datos originales A:P, hojas y resúmenes. Mantener los
  objetos, fórmulas y estilos ajenos a las columnas afectadas.
- Mantener los archivos de carga y el motor MU2026 congelados. Este libro es un
  derivado analítico, no un archivo de envío SIES.
- Guardar respaldo de bytes originales y verificar cobertura completa, ausencia
  de conflictos, integridad de las columnas originales y coherencia de los
  subconjuntos vigentes/no vigentes antes de reemplazar el libro solicitado.

## Implementación

Las utilidades auxiliares se documentan aquí y en `docs/README.md`. Los catálogos,
controles y código versionables no contendrán datos personales. Los registros
de estudiantes y el respaldo del Excel permanecerán en su carpeta autorizada.
Los nombres y sectores se materializan como valores de la edición 2026; la
actualización se reproduce mediante la utilidad, sin referencias a otro libro
abierto ni búsquedas por la primera coincidencia de código de carrera.

El catálogo de presentación reside en
`data/enriquecimiento_mu2026/20261015/catalogo_carrera_sector_2026.json`.
Contiene 61 claves completas, sus nombres, modalidad, jornada, plan, sector y
evidencias por clave, sin identificadores de estudiantes. Las fuentes se fijan
por SHA-256. El nombre oficial es consistente con `nombres_fuente` del catálogo
anual; los acentos y la caja son correcciones editoriales de presentación.

Sector IPSS utiliza el catálogo de
`CARACTERIZACIÓN/analisis_sectorizado_encuesta_ac.py`, líneas 162–215 y 1617–1663:
Tecnología, Administración y Comercio y Salud. Se exige unanimidad entre los
nombres respaldados de una misma clave. Para `I162S2C22J4V2`, el nombre oficial
Ingeniería en automatización y control industrial conserva su denominación;
el sector Tecnología se obtiene de la equivalencia explícita
`CONTINUIDAD INGENIERIA INDUSTRIAL` del mismo código (DURACION_ESTUDIOS.tsv,
fila 150). No se reemplaza el nombre oficial por el alias.

Las nueve claves con continuidad se rotulan según el plan explícito. Nunca se
deduce continuidad a partir del número de versión. Diurno corresponde a jornada
1, Vespertino a 2 y Online a 4, con modalidad de la oferta comprobada.

El libro original tenía un filtro activo sobre `Sector IPSS` que mostraba solo
`Sin coincidencia en Hoja1`. Se retira ese criterio y se muestran sus filas al
corregir las columnas; se mantienen las flechas de filtro. Se amplía el rango
filtrable de los dos detalles a las nuevas columnas.

La autoría de las columnas se realiza con `@oai/artifact-tool`. La importación
completa del libro agotó la memoria del motor, por lo que se autoran las columnas
en un libro temporal sin datos personales y se incorporan al paquete OOXML
original. Se conservan los demás componentes, las fórmulas compartidas y las
cachés de los resúmenes. Las nuevas columnas son valores, sin fórmulas pendientes
de cálculo. No se declara recálculo nativo de los resúmenes existentes.

## Reproducción

`scripts/enriquecer_libro_mu2026.py` valida las fuentes y prepara un JSON sin
datos personales. `scripts/generar_columnas_mu2026.mjs` crea sus columnas con
Artifact Tool. La primera utilidad incorpora las columnas al libro y valida
el resultado antes de escribirlo. La salida debe ser distinta de la entrada;
un destino existente con bytes diferentes se rechaza.

1. Preparar las columnas desde el libro o su respaldo:

```bash
python3 scripts/enriquecer_libro_mu2026.py \
  --entrada "/ruta/MATRÍCULA UNIFICADA 2026.xlsx" \
  --catalogo-nombres data/enriquecimiento_mu2026/20261015_oferta_literal/catalogo_carrera_sector_2026.json \
  --preparar-columnas /ruta/trabajo/columnas.json
```

2. Copiar `scripts/generar_columnas_mu2026.mjs` a una carpeta de trabajo con
   `node_modules` enlazado al runtime de Artifact Tool, sin modificar dependencias
   del repositorio. Ejecutar con el Node de ese runtime:

```bash
node /ruta/trabajo/generar_columnas_mu2026.mjs \
  /ruta/trabajo/columnas.json /ruta/trabajo/columnas.xlsx /ruta/trabajo/vistas
```

3. Incorporar y verificar:

```bash
python3 scripts/enriquecer_libro_mu2026.py \
  --entrada "/ruta/MATRÍCULA UNIFICADA 2026.xlsx" \
  --catalogo-nombres data/enriquecimiento_mu2026/20261015_oferta_literal/catalogo_carrera_sector_2026.json \
  --columnas /ruta/trabajo/columnas.xlsx \
  --salida /ruta/trabajo/matricula_enriquecida.xlsx \
  --auditoria /ruta/trabajo/auditoria.json
```

El diccionario es una instantánea de 61 claves, no un resolutor para futuras
ofertas. Una clave nueva, modalidad contradictoria o fuente modificada detiene
la ejecución. Un cambio anual requiere catálogo y evidencia correspondientes.

## Primera entrega verificada

- Libro actualizado en la carpeta OneDrive indicada por el usuario, con el mismo
  nombre `MATRÍCULA UNIFICADA 2026.xlsx`.
- Respaldo previo en `respaldos/20261015_antes_carrera_sector/` dentro de esa carpeta.
- `06_DETALLE_TOTAL`: 4.105 registros completos; `04_DETALLE_VIGENTES`: 3.145;
  `05_DETALLE_NO_VIGENTES`: 960. Son registros de estas hojas, no una afirmación
  de matrícula total institucional. Los dos subconjuntos repiten el detalle total.
- Cero nombres o sectores pendientes. Se resolvieron las 763 filas que antes
  mostraban `Sin coincidencia en Hoja1`.
- Se compararon todas las celdas A:P y las nueve hojas restantes: valores,
  fórmulas, estilos y bytes XML preservados. Se mantuvieron exactamente las
  126 entradas de cálculo ajenas al detalle y las cachés de sus resúmenes.
- Se verificaron las tres vistas de columnas con Artifact Tool, incluyendo
  recortes del paquete final con sus estilos originales. ZIP y XML válidos.
- Se comprobaron rechazos por clave ausente y modalidad contradictoria.
- Auditoría agregada en
  `data/enriquecimiento_mu2026/20261015/auditoria_enriquecimiento_mu2026.json`.

SHA-256 original: `2f66cb8490c69d469395f1ad7dbf27a3c58b60ac9017d5e95b5680790e393f46`.
SHA-256 instalado: `4347bad30c62b581beda37cd36af3d0607bea336f4d70e757c3950785be8bad2`.

El libro y su respaldo se guardaron localmente en OneDrive. No se certificó la
sincronización remota. El código, el catálogo y la auditoría quedaron en el
repositorio local; no se realizaron commit ni push.

## Corrección solicitada: columnas separadas

El usuario solicitó el mismo día cambiar el encabezado a `Código Único` y
separar la modalidad del nombre de carrera. La hoja principal queda con Q
Código Único, R Carrera, S Sector IPSS y T Jornada / modalidad. En los dos
subconjuntos, Q contiene Carrera, R Sector IPSS y S Jornada / modalidad.
Diurno, Vespertino y Online aparecen exclusivamente en la nueva columna;
se conserva `(Continuidad)` cuando corresponde al plan. Los campos originales
MODALIDAD y JOR no se modifican.

La utilidad y el generador ahora reproducen este formato. El catálogo de fuentes
se conserva: se usa `nombre_legible_base` más el descriptor de continuidad, y
`jornada_legible` se exporta por separado. Los filtros y nombres definidos se
amplían hasta T en el detalle total y S en los subconjuntos.

Antes de esta corrección, el libro había sido guardado en Excel: sus valores y
fórmulas seguían idénticos, pero cambió su serialización. Se tomó esa versión
actual como base para conservar también sus formatos y vistas, con respaldo en
`respaldos/20261015_antes_separar_modalidad/`.

SHA-256 de esa base: `6546dd2f86da903ff6b769becaed40ac05692a85c7543128c9e0921793939e8a`.
SHA-256 de la corrección: `179085fe7896819a36f958f32e269f872fcff0a39235b63bdc67af0d2d1c827b`.
Auditoría de esta revisión:
`data/enriquecimiento_mu2026/20261015/auditoria_columnas_separadas_mu2026.json`.
