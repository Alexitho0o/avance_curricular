# Revisión de subirR.xlsx · 26-10-2026

**[B/C] Fuente:** copia accesible `/Users/alexi/Downloads/subirR.xlsx`, SHA-256 `0699151cc817ed821cd50776bd4b379f87a3f63a5ed6e54f68825db1cc51c3c9`. Se verificó el mismo hash antes y después. El libro tiene siete hojas; sus campos y nombre de origen lo sitúan en la preparación de Oferta Académica 2026, etapa 3. No se afirma que el archivo haya sido enviado o aceptado.

**[B] Estructura:** entre sus encabezados figuran `COD_SEDE`, `COD_JORNADA`, `COD_TIPO_PLAN_CARRERA`, `CARACTERISTICAS_TIPO_PLAN`, `DURACION_TITULACION`, `NOMBRE_TITULO`, `COSTO_TITULACION` y `ARANCEL_ANUAL`. En los encabezados inspeccionados no se observaron CODCLI ni RUT, número de documento o DV. La presencia de un nombre de título y tipo de plan describe la oferta del programa, no identifica por sí misma a una persona titulada.

**[C] Cruce:** se buscaron los tres CODCLI del caso, el RUT con DV y el cuerpo de RUT como valores exactos en las celdas de las siete hojas, tanto al leer fórmulas como sus valores cacheados. No se encontraron coincidencias en ninguna de las tres búsquedas. Los identificadores se usaron solo en memoria; otras representaciones podrían no coincidir **[E]**.

**[E] Conclusión:** esta copia no permite establecer el vínculo del título individual con CODCLI y plan; tampoco contiene evidencia verificada del algoritmo del puntaje 2130. El plan de oferta no se interpreta automáticamente como plan de estudios UMAS del título.

**[C] Control:** `revisar.py` registra estructura, búsqueda y hash sin escribir identificadores personales. No se modificaron fuentes, bases, diccionario, tasas ni denominadores; sin commit ni push.
