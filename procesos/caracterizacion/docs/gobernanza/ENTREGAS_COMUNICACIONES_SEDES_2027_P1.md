# Entregas de comunicaciones y tres sedes 2027 P1

Politica `ENTREGAS_COMUNICACIONES_TRES_SEDES_2027_P1-v1`.
Decision expresa del usuario el 2026-10-13: los cinco Excel seleccionados en su
captura deben quedar en SALIDAS y PTG es Patagonia, con un tercer archivo por sede.
Esta decision amplifica la excepcion de entrega anterior; no cambia el correo,
la elegibilidad ni la definicion de nuevos o de respuesta diaria.

## Archivos en 02_SALIDAS

- Actualmente_eliminados_matricula_en_ventana_*.xlsx, solo si tiene casos.
- Consolidado_eliminados_reporte_*.xlsx.
- BD_Comunicaciones_*.xlsx: general, Santiago, Concepcion y Patagonia.
- Se conservan Informe_Categorias, CSV importables, Lista_tokens_categorias_SI,
  financiamiento y VCM_Emprendimientos_formalizados.

Estado_incorporacion, Seguimiento_incorporacion, Seguimiento_respuestas,
Estudiantes_pendientes_respuesta, matricula completa y trayectorias siguen en
05_ANALISIS. Las auditorias siguen en 04_AUDITORIA. Los datos personales de estos
Excel son para las areas autorizadas; no publicarlos en GitHub.

## Origen y correccion

El BLOQUE 5.5 de caracterizacion.py admitia solo SANTIAGO/CONCEPCION y convertia
el resto a OTRA. El BLOQUE 5.7 exportaba solo esas dos sedes. Por eso el catalogo
del Word reconocia PTG pero comunicaciones no creaba su archivo. El ruteo XLSX
de caracterizacion_runtime.py enviaba los cinco archivos seleccionados a analisis.

La correccion se aplica exclusivamente en caracterizacion_financiamiento_2027.py
sobre el codigo ejecutado en memoria. caracterizacion.py permanece congelado.
caracterizacion_comunicaciones_2027.py toma la columna SEDE identificada por el
encabezado gobernado; en DATOSDEALUMNOS_11941.xlsx se confirmo Hoja1!BL1 = SEDE.
El catalogo CATALOGO_SEDES_2027.json es la autoridad: RE = Santiago, CO = Concepcion,
PTG = Patagonia. No tomar BL como indice universal si la fuente cambia de estructura.

## Controles recurrentes

- Una fila por token en comunicaciones, sin tokens vacios o duplicados.
- La columna SEDE fuente debe alinearse por indice con la base exportada.
- Los tres subconjuntos son disjuntos y su suma, mas sedes no gobernadas, coincide
  con el general. Codigos desconocidos permanecen visibles en general y auditoria;
  no se convierten silenciosamente en OTRA ni se descartan.
- El archivo Patagonia contiene exclusivamente PATAGONIA y conserva los contactos,
  estado de respuesta y marca NUEVO de la misma fila general. No recalcula elegibilidad.
- Si una sede no tiene personas, no generar ni anunciar su Excel vacio.
- Si eliminados en ventana no tiene casos, aplicar la misma omision explicita.
  Registrar GENERADO u OMITIDO_SIN_CASOS en manifest_ejecucion y en el resumen.
  No modificar retroactivamente el manifiesto o los archivos de corridas previas.
- Registrar CONTROL_COMUNICACIONES_SEDES en auditoria y mostrar la conciliacion
  de general/Santiago/Concepcion/Patagonia en terminal.
- Copiar y verificar 02_SALIDAS junto al resto de la corrida mediante el manifiesto.
- Preservar las fuentes, las corridas anteriores y las referencias FCU 2026.

Pruebas: tests/test_comunicaciones_sedes_2027.py y tests/test_separacion_2027.py.
El archivo Patagonia mantiene la estructura BD de once columnas del general,
incluidos EMAIL (personal) y EMAIL__2 (institucional), sin intercambiarlos. Los
CSV de incorporacion siguen usando solo Mail_Inst.

## Validacion del 2026-10-13

Corrida real 2027_P1_132949, codigo de salida 0. Copia de entrega:
Caracterizacion_2026-10-13_2027_P1_133041. Contiene 11 archivos en 02_SALIDAS,
21 de auditoria y 6 de analisis interno. Se verificaron los hashes del manifiesto.

DATOSDEALUMNOS_11941.xlsx confirma SEDE en BL y PTG en las siete personas del
archivo Patagonia. Comunicaciones concilia: 262 = 241 Santiago + 14 Concepcion
+ 7 Patagonia; cero sedes no gobernadas en este corte. La union de los tres
archivos coincide exactamente con el general, sin duplicados ni omisiones.

Se cotejaron todos los campos de comunicaciones contra la corrida previa:
solo cambia SEDE de OTRA a PATAGONIA en esos siete registros. Los dos Excel de
eliminados conservan sus hojas y valores. El CSV diario conserva su hash.
Los 42 archivos previos, incluido el archivo oculto de Finder, siguen intactos;
las 51 referencias congeladas de 2026 tambien. Pasaron 134 pruebas focalizadas
y se revisaron tabla, filtros, marca NUEVO, contactos y las dos vistas de Patagonia.
Evidencia privada: .local/comunicaciones_sedes_20261013/VALIDACION.json.

La validacion anterior conserva el estado de esa corrida: incluia el Excel de
eliminados vacio. La regla condicional se corrige posteriormente conforme a
AUDITORIA_CAMBIOS_SALIDAS_2027_P1.md; no presentar las 134 pruebas anteriores como
prueba de una condicion de cero casos que entonces no estaba cubierta.
