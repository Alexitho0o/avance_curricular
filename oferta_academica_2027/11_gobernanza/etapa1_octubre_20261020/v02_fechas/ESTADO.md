# Version 02: fechas corregidas, pendiente de liberacion

Fecha: 20-10-2026. Segundo proceso Oferta Academica 2027, Etapa 1, ID 17467.
No es una carga aceptada ni un archivo liberado para subir.

Se mantienen 161 programas, 48 columnas y 5.461 vacantes. Se retiran solamente
el encabezado y las tres columnas de consulta indicadas en el manual p.14.
Se convierten 88 fechas de DD-MM-AAAA a DD/MM/AAAA (p.26), sin cambiar el dia.
Se mantiene punto y coma del reporte de origen y se exporta en UTF-8 sin BOM.
La confirmacion de Docencia sin cambios fue transmitida por el usuario.

Los 84 vacios de los 21 diplomados siguen intactos. No se uso 9, -1 ni 0:
el manual p.5 menciona Sin Informacion (-1) para programas vigentes con alumnos
nuevos informados en el primer proceso; no especifica en ese pasaje un valor
sustituto para los cuatro campos de los diplomados en la carga de octubre.
Las pp.27-28 los califican como obligatorios; las pp.42-45 asignan a Etapa 3
la definicion de esos valores y explicitan que alli no pueden quedar vacios.
No se extrapola la excepcion de pregrado a postitulos ni a costos diferentes.

Antes de liberar: confirmar con la estructura vigente de ID 17467 o SIES la
aceptacion de vacios o el codigo permitido por cada campo para los diplomados;
alternativamente incorporar montos autorizados. Confirmar tambien el separador:
la p.14 dice delimitado por comas, mientras la precarga utiliza punto y coma.
Sin confirmacion no se afirma aceptacion de esta version por PES.

La copia de Escritorio y la del proyecto tienen el mismo SHA-256. Entradas,
procedimiento, cambios y pendientes quedan registrados. Respaldo local;
los CSV estan ignorados por Git. No hubo carga PES, commit ni push.
