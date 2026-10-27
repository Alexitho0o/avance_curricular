# Búsqueda de titulación, migración y actas · 26-10-2026

## Titulación

**[B/C]** Se leyó `Titulados 2022_2023.xlsx`, hoja `Hoja1`, 498 filas de dimensión declarada y 30 columnas, SHA-256 `9a37225a1e9adbce67c3bbfd0b070fb609e7fd948512e483b08c2ee5da10e588`. Al contrastar los cuatro documentos por cuerpo y DV, no se encontraron filas. No contiene columnas CODCLI ni PLAN_DE_ESTUDIO; la ausencia en este archivo no demuestra ausencia en otros archivos ni confirma que el dato deba estar en ese período **[E]**.

**[E]** Se localizó `TITULADOS UNIFICADO TOTAL DESDE 1993 EN ADELANTE v2.xlsx`, bajo `Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.5 Otros/Titulados CIISA registro interno/`. La lectura devolvió `TimeoutError`. No se conoce su estructura ni contenido y no se puede decir que contenga CODCLI, plan o alguno de los cuatro casos. No se localizó una segunda copia por nombre en los repositorios y carpetas privadas inspeccionadas. Está pendiente volver a leerlo una vez disponible localmente.

## Homologaciones y migración

**[E]** En `Matricula Extranjeros/2026/dctos/Revision_Caso_NETMRE016_MU2026/` se localizó `PLAN_NETMRE20121_Y_HOMOLOGOS.csv`, potencialmente relacionado con historial de planes. Su lectura también devolvió `TimeoutError`; no se verificó su contenido ni su relación con los 21 ramos. No se encontró copia por nombre en los repositorios ni en la carpeta consolidada. La ubicación exacta se registra en `FUENTES_PENDIENTES.json`.

**[C/E]** La búsqueda por nombres de actas, homologaciones, convalidaciones y cambios de plan dentro de `1.2.1 Datos Institucionales` encontró otros archivos de oferta, infraestructura y extranjeros, pero no identificó un acta específica para los 21 ramos. Una búsqueda por nombre no es búsqueda completa de contenido y no prueba que no exista un acta.

## Resultado y conservación

**[E]** Los cuatro vínculos título–CODCLI–plan y la aplicación de las homologaciones en los contextos investigados continúan pendientes. Se mantiene por separado la evidencia de 15 pares con reconocimiento observado en PROMEDIOS; no se convirtió en una equivalencia universal.

No se alteraron bases, diccionario, fuentes, tasas ni denominadores. Sin commit ni push.
