# V06: correccion autorizada de matricula y arancel

Proceso 2026, Oferta Academica 2027, Etapa 1 octubre, ID 17467.
Base: V05 rechazada por ARANCEL_ANUAL = 0 en siete diplomados con vigencia 1.
El usuario confirmo que los montos corresponden a arancel y la matricula es 0.
Esta confirmacion corrige la interpretacion de encabezados del Excel de
Docencia; se conserva intacto el archivo institucional original.

Codigos 53,66,68,69,70,96: matricula 0; arancel anual 990000.
Codigo 99: matricula 0; arancel anual 400000.
Exactamente 14 celdas modificadas en siete filas. Todos los otros valores,
filas, claves, fechas, vacantes, enlaces, vigencias y vacios quedan intactos.
161 registros, 48 columnas, 5.671 vacantes. Sin encabezado ni salto final.

V06 sustituye V05 para el siguiente intento de carga; no se borra V05.
Estado: PREPARADO PARA REINTENTO, PENDIENTE DE ACEPTACION PES.
El control local confirma arancel mayor a cero para toda vigencia 1;
no acredita ausencia de otras validaciones de plataforma. No se envio a PES.
Conservar el resultado de carga y conciliar reporte 6048 antes de congelar.
Respaldo local reproducible con fuentes, hashes, script y diferencias.
No se realizo commit ni push.
