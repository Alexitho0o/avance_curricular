# Prueba PES autorizada por el usuario

Proceso 2026, Oferta Academica 2027, segundo proceso, Etapa 1, ID 17467.
El usuario solicita conservar los vacios de SIES y cambiar solo el formato
de fechas para probar la carga. Esta decision habilita una prueba; no modifica
las reglas del manual ni demuestra que PES admita los vacios financieros.

161 registros, 48 columnas, 5.461 vacantes. Solo 88 cambios DD-MM-AAAA a
DD/MM/AAAA. Se conservan las 84 celdas financieras vacias de 21 diplomados.
La proyeccion de columnas y retiro del encabezado son los mismos del derivado
v02; no se agrega ni elimina ningun registro. CSV UTF-8 sin BOM, punto y coma.

Esta version sustituye v02 para la prueba solicitada, sin borrar antecedentes.
No se ha subido a PES ni se ha confirmado su aceptacion. Pendiente registrar
resultado de carga y, si finaliza, conciliar contra reporte validado 6048 antes
de congelar como aceptado. Si falla, conservar los mensajes exactos de PES.
Se mantiene pendiente la comprobacion del separador con la estructura vigente.
Los importes de diplomados quedan pendientes para su tratamiento en Etapa 3.
Gobernanza local: no se realizo commit ni push; los CSV estan ignorados por Git.
