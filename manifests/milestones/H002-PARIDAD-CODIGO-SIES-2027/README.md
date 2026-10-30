# H002-PARIDAD-CODIGO-SIES-2027

## Objetivo

Paridad de catálogo para códigos SIES y candidatos internos, años 2026 y 2027. Sin atribuciones personales, ni cambios en retención, fuentes o motores.

## Alcance

106 códigos de 135 grupos existentes y 161 de V06. Una fila por código y año, total 267. Los 52 grupos con varios códigos se preservan. Diplomados/postítulos/educación continua: FUERA_ALCANCE.

## Entradas

Ver data/paridad_codigo_sies/20261029/FUENTES.json: rutas, clases y hashes. V06 preparada C, con confirmación de aceptación por usuario D, sin comprobante PES B. Manual de octubre: páginas 22 y 28.

## Salidas y archivos

- data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.csv y .json; README, FUENTES y MANIFEST.
- outputs/paridad_codigo_sies_20261029/: generador, pruebas, QA, decisiones numeradas, resoluciones por grupo, CHECKPOINT y control de preservación.

## Validaciones

Llaves únicas 106/161, estados disjuntos, selección de nuevos única o E, perfil de duración/tipo y modalidad, separación de jornadas y continuidad, reproducción por bytes, rechazo de fuente alterada y preservación de fuentes/cambios ajenos. 11 pruebas focalizadas. VALIDACION_ENTREGA.json documenta la verificación independiente.

## Resultado

COMPLETADO_CATALOGO_CON_PENDIENTES_E. Todos los códigos están representados, no todas las equivalencias están acreditadas. 12 combinaciones internas E repercuten en 14 códigos de cada año. Seis propuestas NUEVO_2027_CON_PLAN requieren decisión D; 43 NUEVO_2027_SIN_PLAN_E; cuatro SIN_OFERTA_2027 no son cierres acreditados.

## Evidencias

MANIFEST.json fija entradas/salidas. CHECKPOINT.md lista las 24 entradas ajenas iniciales. El único archivo preexistente a modificar es la línea H002 del índice, según autorización del encargo.

## Pendientes

Aprobar o rechazar propuestas con evidencia del perfil, plan y ámbito; obtener asignaciones internas para nuevos códigos/jornadas; no reconstruir el diccionario por persona.

## Deuda técnica

No hay validación directa de aceptación PES para V06 ni catálogo completo de todas las mallas 2027. El perfil derivado de una equivalencia por código no sustituye el contraste curricular. Los años de primera oferta no certifican migración ni versión por año de ingreso.

## Siguiente paso

Revisar DECISIONES_PENDIENTES.md antes de cualquier promoción. Sin commit/push en este hito.

## Actualización H002b · 29-10-2026 [D/C/E]

Alexi aprobó seis relaciones código SIES–CODCARPR: estado APROBADA_D_2027, clase D. Las cohortes con varias mallas siguen E; no se extrapola una equivalencia individual. Las doce combinaciones permanecen pendientes y tienen fichas con agregados MU×plan×código×FOR_ING_ACT, cobertura y fuerza de la propuesta. Los 43 esperan el listado oficial UMAS. Plantilla vacía y script de cruce separados; pruebas solo ficticias, sin ejecutar contra un listado real. Commit y push H002 expresamente autorizados con QA aprobado; los textos del hito inicial sobre ausencia de autorización quedan como antecedente.

## Antecedente H002e (superado sólo en alcance H002k)

D · Alexi, 29-10-2026. Esta sección reemplaza los estados pendientes de los antecedentes anteriores: 11 códigos con relaciones D (6 previas + 5 nuevas), 6 grupos históricos con ambigüedad E sin versión, 6 códigos C35 históricos. Pendientes: CADMP y 37 códigos sin planes. Las 106 filas 2026 se conservan. Los códigos compartidos no se cierran por retirar un plan.

Decisión: DECISIONES_APROBADAS_v2.json. QA vigente: QA_H002E.json; QA.json es el control del constructor. Los informes H002b–d se conservan y se reproducen en checkout aislado del commit de origen. Observaciones de oferta: OBSERVACIONES_OFERTA_2027.md; no se modifica PES ni v20.

## Estado vigente H002k · 29-10-2026

D · Alexi: ADMP20251/V1 y CADMP20251/V2 aprobados; 13 códigos APROBADA_D_2027 y cero VERSION_MULTIPLE_E en 2027.
Regla interna activa: data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json. Antiguos conservan su código, aun inconsistente; tipo E y otros casos pasan a revisión.
Pendientes: 37 códigos sin plan hasta MU 2027, revisión manual y reemplazo de V06 preparada por aceptada.
No se modifica retención, VIG, v20 ni cargas. QA: outputs/activacion_codigo_mu2027_20261029/QA.json.
