# Origen de Docencia y selección posterior de expediente

Proceso: Titulación Unificada SIES 2026; fecha del título examinada: 24-07-2025. Subproyecto: vínculo título–CODCLI–plan, caso TTMRE/TCRE. Revisión local del 26-10-2026. No se modifican bases, diccionario, tasas ni denominadores.

## Resultado

**[B]** Se revalidó la fecha 24-07-2025 y el título «TÉCNICO EN CONECTIVIDAD Y REDES» en `Informe de Titulados 2025_vf.xlsx`, Hoja1, fila 107, mediante documento y DV exactos. El informe no contiene CODCLI ni plan. Declara ingreso actual y de origen 2022.

**[B/C]** La inspección del archivo de Docencia no encontró fórmulas, conexiones externas, consultas, comentarios ni archivos incrustados. El XML personalizado solo contiene esquemas/metadatos de Office/SharePoint, sin contenido de origen que permita identificar un acta. Los metadatos indican creación 19-03-2026 y modificación 20-03-2026 en UTC: son fechas del archivo, no del evento institucional. En la carpeta `enviado por docencia` solo se encontró ese libro.

**[B]** Las dos copias adicionales de TITULADOS_3280 en la carpeta `2025` no contienen coincidencias con el caso por CODCLI, documento completo ni cuerpo del documento. Sus metadatos de modificación corresponden al 23-07-2025, antes de la fecha declarada del título. No se deduce de ello cobertura completa ni fecha de exportación.

**[B/C] Hallazgo nuevo:** los respaldos de empleabilidad 2026-1 conservan una selección explícita del expediente posterior. En la versión v4, `Participacion_TIT!AA1476` selecciona la fila 7174 de `DATOS ALUMNOS`: carrera TCRE, estado TITULADO y situación «31 - TITULADO APROBADO». El expediente TTMRE está en la fila 5260, ELIMINADO, situación «10 - ACTUALIZACIÓN DE PLAN DE ESTUDIO 2024». El tercer expediente corresponde a IECIRE y está ELIMINADO.

**[C]** La selección se puede reproducir: la columna BY de DATOS ALUMNOS forma una prioridad con indicador de titulado, año de matrícula, período, fecha y fila; Z de Participacion_TIT obtiene el máximo para la llave y AA recupera el número de fila. El máximo de los tres expedientes es la fila 7174. Las fórmulas exactas y la comprobación aritmética se conservan en los resultados. Esta fórmula pertenece al análisis de empleabilidad; **no es la fórmula aún no localizada del puntaje 2130 de Res_Tit_Unificada**.

**[B/C]** Se cruzó el CODCLI seleccionado, sin aproximación por nombre, con `Promedio-notas-Alexi.xlsx`, Hoja1: 26 filas de asignaturas, las 26 además concordantes en documento y DV, todas con PLAN_DE_ESTUDIO=TCRE20241. Desglose: 2024-P1=16; 2024-P2=4; 2024-P3=4; 2025-P1=2. Son filas de asignaturas de un expediente, no 26 estudiantes ni 26 títulos.

**[E]** La cadena observada es: informe Docencia con fecha y título → persona por documento/DV → expediente TCRE seleccionado en un análisis posterior → plan TCRE20241 observado por CODCLI en PROMEDIOS. Esta cadena aporta respaldo a una correspondencia interna; no acredita por sí misma que el acto del 24-07-2025 se emitiera formalmente contra ese CODCLI/plan. El listado de empleabilidad usa Datos Alumnos y no constituye un acta independiente.

## Qué sigue pendiente exactamente

**[E]** No se localizó en esta revisión el acta, folio, registro de emisión o consulta institucional que originó la fecha de Docencia y conserve el CODCLI/plan, o una referencia que permita enlazarlos sin ambigüedad. Tampoco se recuperó la fórmula de 2130 ni la fecha efectiva de migración. No se promueve el caso ni se atribuye el título al plan por decisión automática.

**[C]** Esta revisión se concentró en seis libros de procedencia y posteriores (incluido Docencia), más el contraste dirigido con PROMEDIOS. No repite la búsqueda general de PDF/Word del informe anterior ni declara agotados todos los respaldos. La búsqueda nominal de mensajes locales identificó dos .msg antiguos en la carpeta de respaldo de Titulados; no se analizaron sus cuerpos ni se cuenta con evidencia de que correspondan a este evento.

## Evidencias y reproducción

- `RESULTADOS.json`: rutas exactas, hashes, hojas, filas, encabezados, metadatos y coincidencias sin identificadores.
- `SELECCION_POSTERIOR.json`: fórmulas, alternativas académicas y vínculo exacto con el plan; no contiene RUT, CODCLI ni nombres personales.
- `revisar.py` y `contrastar_seleccion.py`: lectura de fuentes originales y verificación de integridad. La identificación del caso se lee del respaldo privado existente, sin copiarlo al repositorio.
- `QA.json`: privacidad, integridad de fuentes, control aritmético y HEAD.

**[C]** Se conserva el antecedente de la búsqueda anterior en `outputs/busqueda_documentos_titulo_20261026/INFORME.md`. No hay commit ni push en esta ejecución.
