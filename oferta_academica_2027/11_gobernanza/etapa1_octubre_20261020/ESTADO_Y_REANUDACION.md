# Etapa 1 de octubre: borrador sin cambios institucionales

Estado: BORRADOR NO CARGAR. No es una carga aceptada ni una version congelada en PES.
Destino previsto: Oferta Academica Vigente Editada TP, ID 17467. Cierre: 23-10-2026.
Confirmacion de Docencia transmitida por el usuario: no hay cambios. No se adjunto correo.

Se conservaron 161 programas y sus 48 campos de carga, sin modificar valores,
normalizar nombres, completar vacios ni eliminar registros. Se retiraron unicamente
el encabezado y CODIGO_IES_NUM, CANTIDAD_MATRICULA_DFE y CANTIDAD_BENEFICIO_DFE
(manual octubre 2026, p. 14). Se convirtio cp1252 a UTF-8 sin perdida de caracteres.
La secuencia A-AV coincide con el manual pp. 21-28. Se conservan 5.461 vacantes.

## Pendientes que impiden liberar la carga

Los 21 diplomados traen vacios VALOR_MATRICULA_ANUAL, COSTO_TITULACION,
VALOR_CERTIFICADO_DIPLOMA y ARANCEL_ANUAL: 84 celdas. El manual pp. 27-28
los marca obligatorios para postitulos. Esto viene en la precarga de SIES; no
es una modificacion de Docencia. No se rellenaron con 0 ni -1 por criterio propio.
Es necesario completar con datos autorizados o confirmar con SIES que estos vacios
se admiten en Etapa 1. No se afirma que PES ya los haya rechazado.

Ademas, 88 fechas FECHA_ADMISION_INICIAL vienen como DD-MM-AAAA; el manual
p. 26 pide DD/MM/AAAA. Se conserva el original en este borrador. La conversion
de formato debe registrarse en la version liberada. Total: 172 hallazgos sobre
109 programas (84 vacios financieros y 88 formatos de fecha).

El manual p. 14 menciona CSV delimitado por comas; el reporte usa punto y coma.
El borrador conserva punto y coma. Confirmar la estructura vigente ID 17467 en PES
antes de liberar el archivo, incluidos largos y nombre requerido.

## Trazabilidad

Originales completos: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/00_fuentes_originales/etapa1_octubre_20261020
Detalle fila/campo: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/06_validaciones/etapa1_octubre_20261020/HALLAZGOS.tsv
Control de 7.728 celdas: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/06_validaciones/etapa1_octubre_20261020/CONTROL_48_COLUMNAS.tsv
Manifiesto y SHA-256: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/11_gobernanza/etapa1_octubre_20261020/MANIFIESTO_PREPARACION.json
Copia local del proyecto: /Users/alexi/Documents/GitHub/avance_curricular/oferta_academica_2027/07_resultados/borradores_prueba_no_oficiales/etapa1_octubre_20261020/BORRADOR_NO_CARGAR_OFERTA_2027_ETAPA1_OCTUBRE_17467_20261020.csv
Copia identica del Escritorio: /Users/alexi/Desktop/BORRADOR_NO_CARGAR_OFERTA_2027_ETAPA1_OCTUBRE_17467_20261020.csv

Los CSV estan ignorados por Git. Respaldo local reproducible; no se hizo commit ni push.
Reanudacion: resolver pendientes, validar la estructura actual, generar una nueva
version liberada; tras carga comprobar Finalizado, descargar editada y luego 6048.
