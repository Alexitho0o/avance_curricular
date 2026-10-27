# Búsqueda adicional en gestiones académicas · 26-10-2026

**[B/C]** Se consultó `GESTIONSGE_1703.xlsx`, hoja `Hoja1`, disponible en la carpeta consolidada de respaldos IPSS; ruta y SHA-256 `2ac487eb0ac09ac66d2c76afde9e62b9a4265357514d7ee696113d125a8e2401` en `RESULTADO_AGREGADO.json`. Se buscaron los cuatro casos por el cuerpo de RUT, verificando que las dos columnas `RUT_ALUMNO` no discreparan y que el cuerpo no fuera ambiguo en la v11. El reporte no acredita el DV de manera independiente **[E]**.

**[B/C]** Se localizaron 20 registros asociados a tres de los cuatro cuerpos buscados. Una búsqueda literal en `ASUNTO` y `OBSERVACION` identificó menciones de plan para dos personas, de titulación para una y de homologación o convalidación para dos. Los grupos pueden superponerse y las filas no se interpretan como eventos distintos.

**[B/C/E]** En esos 20 registros no se identificó literalmente ninguno de los CODCLI de los cuatro casos, los cuatro códigos de plan investigados ni los 21 códigos de ramo. La búsqueda literal también identificó términos de solicitud o consulta en tres registros y no encontró las cadenas seleccionadas para decisión (`APROBAD`, `RESOLUCION`, `DECRETO`). No se interpreta esto como prueba de que no exista una decisión: puede estar expresada con otras palabras o en otro archivo. El texto de gestiones no se exportó.

**[E]** Esta fuente no acredita el vínculo formal título–CODCLI–plan ni la equivalencia de los 21 ramos. Los cuatro títulos y la aplicación general de las equivalencias permanecen pendientes. Se conservan los reconocimientos individuales observados previamente en PROMEDIOS, sin convertirlos en homologaciones universales.

`consultar_gestion.py` reproduce la búsqueda agregada, comprueba hash antes y después y no escribe datos personales. No se alteraron fuentes, diccionario, bases, tasas ni denominadores. Sin commit ni push.
