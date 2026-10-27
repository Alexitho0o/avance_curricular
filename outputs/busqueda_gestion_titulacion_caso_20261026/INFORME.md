# Búsqueda de gestión para el caso de titulación · 26-10-2026

**[B/C]** Se revisó de forma específica `GESTIONSGE_1703.xlsx`, hoja `Hoja1`, SHA-256 `2ac487eb0ac09ac66d2c76afde9e62b9a4265357514d7ee696113d125a8e2401`. La búsqueda literal de los tres CODCLI del caso en todas las celdas no encontró coincidencias.

**[B/C/E]** La búsqueda por cuerpo de RUT encontró tres gestiones, una con una mención textual relacionada con titulación. Esta última indica carrera `TCRE` y año 2024. El archivo no contiene CODCLI ni plan en su cabecera y no acredita independientemente el DV; una mención o comunicación no equivale a un acta de título. El texto libre no se exporta.

**[E] Evidencia necesaria:** registro o acta de titulación institucional que indique título otorgado, CODCLI y plan, o un conjunto documental verificable que vincule el acto de título con el expediente y el plan. Una bitácora de migración con fecha y alcance puede complementar la atribución si permite unir el acto al expediente; por sí sola no prueba automáticamente la titulación.

**[B/C/E]** En PROMEDIOS y otros respaldos, el CODCLI posterior está asociado a `TCRE20241` y a un estado titulado; el informe de Docencia registra el título por documento y DV. Estas evidencias apoyan una correspondencia interna, pero el informe no declara CODCLI ni plan. El criterio del puntaje 2130 tampoco se ha recuperado.

**[C] Control:** `revisar.py` lee identificadores solo en memoria y comprueba el hash antes y después. No modifica fuentes, bases, diccionario o denominadores. Sin commit ni push.
