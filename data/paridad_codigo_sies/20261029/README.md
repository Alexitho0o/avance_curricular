# H002 · Paridad de catálogo UMAS–SIES, 2026 y 2027

Especificación previa. Proceso Oferta Académica 2027 ejecutado en 2026; años del catálogo 2026/2027. Sin período personal, atribuciones individuales ni retención. La tabla tiene una fila por año y código completo: 106 de los grupos 2026 y 161 de la V06 para 2027. El universo 2026 es el catálogo interno heredado, no toda la oferta 2026 ni estudiantes. “Nuevo 2027” significa ausente en esos grupos, no primer año de existencia en SIES.

## Fuentes y precedencia

FUENTES.json fija cada entrada por ruta y SHA-256. La V06 es una carga preparada C y tiene confirmación del usuario D de aceptación; no hay comprobante ni verificación directa de PES. No se la presenta como descarga validada de SIES. Se contrasta su copia congelada. Manual de octubre (PDF): VERSION y tipo de plan, página 22; vigencia, página 28. La extracción TXT anterior tiene otra paginación: 23 y 29, respectivamente. No intercambiarlas.

A: definiciones oficiales. B: atributos observados. C: descomposición, cruces y estados calculados. D: alcance y equivalencias internas previas aprobadas. E: candidatos no acreditados, aceptación técnica y planes/ámbitos insuficientes. Una confirmación D no se eleva a comprobante B ni regla A.

## Reglas de construcción

1. Reutilizar grupos, duración/tipo y candidatos H5, sin reconstruir equivalencias por nombre. Conservar las asociaciones completas en candidatos_internos; listas planas de CODCARPR/sede/jornada son solo índices, nunca un producto cartesiano.
2. Modalidad procede de oferta, no de la etiqueta de jornada ni de DatosAlumnos. J3 y J4 son diferentes. Las sedes existentes RE/CO se leen del catálogo y PTG solo del ámbito 2027 gobernado.
3. Regular, especial y continuidad se separan por tipo y duración total formal; no elegir V mayor ni año del nombre del plan. El historial de cohortes aporta opciones/advertencias, no asignación personal ni regla automática para continuidad.
4. Resolver nuevos de un grupo solo con perfil de duración/tipo no ambiguo, sede/jornada/modalidad concordantes y exactamente una versión de la carga con vigencia 1 compatible. Vigencia 2 no admite nuevos y no es cierre. Sin candidata o con varias, E explícito. Separar elegibilidad del código SIES de equivalencia del plan interno.
5. Una relación NUEVO_2027_CON_PLAN es propuesta E pendiente de aprobación D, nunca alta activa: exige relación explícita previa por código, sede/jornada, nombre normalizado, perfil formal concordante y plan catalogado del mismo CODCARPR/sede. El perfil derivado del código de una equivalencia de 2027 no certifica la duración curricular independiente de la malla; se declara ese límite. Sin CODPESTUD catalogado o si solo coincide el nombre, SIN_PLAN_E. No transferir otra jornada o duración.
6. Los cuatro códigos heredados ausentes en la carga 2027 quedan SIN_OFERTA_2027: ausencia no prueba cierre. No completar atributos 2026 a partir de 2027 sin señalarlo: atributos anuales H5/precarga 5913 y operativo DURACION como fallback explícito C.
7. FUERA_ALCANCE prevalece para diplomado, postítulo y educación continua. No excluir continuidades de pregrado por su prefijo. “Versión para nuevos” es catálogo propuesto de la carga; no acredita autorización de matrícula ni equivalencia individual.

## Estados (prioridad)

FUERA_ALCANCE → SIN_OFERTA_2027 → NUEVO_2027_CON_PLAN / NUEVO_2027_SIN_PLAN_E (solo códigos 2027 sin grupo) → VERSION_MULTIPLE_E → VERSION_MULTIPLE_RESUELTA → CONTINUA. Un código puede tener varios alias: se conservan las resoluciones separadas por grupo; si alguno tiene ambigüedad relevante, el estado de la fila conserva E. El estado de una fila 2026 es comparativo hacia 2027, no una selección retrospectiva del plan.

CONTINUA acredita presencia del mismo código, no que todos los alias o planes queden resueltos. VERSION_MULTIPLE_RESUELTA solo declara la selección de nuevos dentro de los grupos expresamente respaldados; no adjudica estudiantes ni certifica malla. VERSION_MULTIPLE_E mantiene opciones sin elegir.

## Salidas y QA

CSV UTF-8, separador punto y coma; las listas y asociaciones se serializan como JSON dentro de la celda. JSON manda con el CSV. Se conservan nombres SIES literales y códigos exactos. MANIFEST.json fija entradas y salidas; el generador lee solo fuentes de catálogo. QA: 106 + 161 filas, llaves únicas, conteos disjuntos, selección única o E, fuentes intactas, ausencia de identificadores y reproducción por bytes.

Las decisiones numeradas y sus evidencias se entregan en outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.md/.json. CHECKPOINT.md lista las 24 entradas ajenas iniciales y los límites. El único archivo preexistente a modificar es una línea del índice de hitos, por excepción expresa de H002. Sin commit/push.

## H002b · decisiones y revisión [D, 29-10-2026]

DECISIONES_APROBADAS.json autoriza seis relaciones código SIES–CODCARPR, ahora APROBADA_D_2027. La aprobación no selecciona personas ni mallas por el año del nombre. Para las cohortes observadas y 2027 se conserva el ensayo histórico de código y se evalúa la unicidad del catálogo de planes. Si hay varias mallas y no hay ámbito explícito acreditado, plan_por_cohorte queda E. La vigencia 2 sigue sin admitir nuevos.

Las doce combinaciones permanecen VERSION_MULTIPLE_E; FOR_ING_ACT se presenta como valor observado de MU, nunca como regla general de selección. El vínculo MU–plan requiere identidad con DV, año, código y contexto del diccionario v20 consultado en modo solo lectura. Solo se publican agregados; sin vínculo único se muestra cobertura E, sin atribuir esas matrículas a un alias interno concreto. La presencia de un plan en actividad no acredita su vigencia curricular formal.

El listado UMAS 2027 aún no se recibió. La plantilla vacía vive en data/paridad_codigo_sies/PLANTILLA_PLANES_UMAS_2027.tsv; el cruce genera propuestas separadas, no modifica esta tabla.
