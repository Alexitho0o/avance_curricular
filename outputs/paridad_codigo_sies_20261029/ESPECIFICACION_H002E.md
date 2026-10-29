# H002e · aplicación de decisiones de Alexi

D · Alexi, 29-10-2026. Cinco relaciones aprobadas, seis grupos históricos, CADMP
pendiente y seis códigos C35 históricos. No cambia oferta, v20 ni estudiantes.

La tabla conserva grano año/código. Las decisiones de plan se aplican a las
asociaciones CODCARPR+sede+jornada; no se extienden a otros alias del mismo código.
Cuando un código tiene otros planes activos no se marca histórico todo el código.
Se conserva el estado D de los seis grupos en RESOLUCIONES_POR_GRUPO y dentro de
las filas que los referencian. Ambigüedad histórica E, sin versión asignada.

Las 106 filas 2026 quedan idénticas. En 2027 cambian sólo las filas que referencian
los doce grupos de la decisión y los seis C35. Las 37 filas pendientes sin historia
de matrícula quedan idénticas. Los metadatos de aprobación no acreditan vigencia
curricular individual ni asignación retrospectiva por cohorte. Para IECIREOL,
aprobar el código del grupo no elige entre sus varias mallas por año de ingreso.

La admisión se conserva separada de la correspondencia: TAMD V1 tiene vigencia 2
y no admite nuevos, aunque su relación sea D. No habilitar V2 por esa aprobación.

CONTROL_VIGENTES_H002E verifica cero etiquetas UMAS VIGENTE en los seis grupos;
IECIRE tiene una fila TITULADO. No presentarla como cero filas totales, ni convertir
el estado de octubre en VIG al 30-abr.

El constructor reconstituye primero el catálogo anterior y aplica DECISIONES_APROBADAS_v2.
La sustitución de salidas requiere --aplicar-h002e y el HEAD/huellas previos esperados;
--verificar es sólo lectura. El QA compara todas las filas y campos con el commit
2969b63, además de probar las reglas y la reproducción por bytes.

Los informes H002b–d permanecen congelados. Su reproducción histórica usa checkout
aislado de 2969b63 o del commit indicado en su manifiesto: la tabla vigente y los
componentes cambian de forma deliberada. No regenerar históricos para ocultarlo.
Las verificaciones de hashes históricos pueden leer sus versiones desde Git.
