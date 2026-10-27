# Contraste de reconocimientos en cuatro extracciones · 26-10-2026

**[B/C]** Se tomaron los 15 pares carrera–plan–ramo que contienen al menos una fila `HOMOLOGADO` o `CONVALIDACION` en PROMEDIOS 7804. Se compararon las filas con 3233, 2071 y 12166 mediante RUT+DV+CODCLI+carrera+plan+año+período+ramo+sección+estado+descripción+RAMOEQUIV+CONVALIDADO. Las identidades permanecieron en memoria y no forman parte de la salida agregada.

**[B/C]** Los 15 pares incluyen 21 registros distintos en 7804; los mismos 21 registros se encuentran también en 12166. En 3233 aparecen 11 de esos registros, correspondientes a siete pares; en 2071 aparecen 15, correspondientes a diez pares. Los conjuntos se solapan; no se suman como reconocimientos nuevos. Las extracciones pueden proceder de una misma fuente UMAS y la coincidencia no es una confirmación administrativa independiente **[E]**.

**[B/C]** Ninguno de los 15 pares tiene un registro de reconocimiento asociado por RUT a las cuatro personas investigadas en el conjunto 7804. Esto se refiere a ese grupo y extracción, no a todos sus ramos o documentos **[E]**.

**[E]** Se confirma la repetición de registros de reconocimiento por expediente y período, no la validez universal de una equivalencia ni la autorización formal de una homologación. Los seis pares restantes no tenían estado I/E en 7804; una aprobación o reprobación no se transforma en homologación por coincidencia de nombre. Los cuatro vínculos título–CODCLI–plan continúan pendientes.

## Búsqueda de la traza

**[C/E]** Una búsqueda adicional de textos de la traza en el historial Git local de avance_curricular y en carpetas de trabajo encontró referencias en informes y scripts de análisis que no implementan la fórmula de titulación. La búsqueda en un antiguo worktree se interrumpió y no debe considerarse exhaustiva. No se localizó el generador ni los pesos del puntaje en el alcance completado. No se infiere una regla a partir de la coincidencia de 2130.

## Control

`contrastar.py` verifica los hashes de las cuatro entradas antes y después; `RESULTADO_AGREGADO.json` conserva los resultados por par y los hashes, sin identificadores individuales. No se cambiaron fuentes, bases, diccionario, tasas o denominadores. Sin commit ni push.
