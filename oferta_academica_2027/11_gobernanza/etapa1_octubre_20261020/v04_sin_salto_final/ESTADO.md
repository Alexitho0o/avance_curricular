# Version 04: correccion de salto final

Oferta Academica 2027, proceso 2026, Etapa 1 de octubre, ID 17467.
Autorizacion: eliminar solo el salto de linea final para reintentar en PES.
El reporte de PES informa linea 162 vacia, 1 campo en lugar de 48 y COD_SEDE
invalido. Se conserva el reporte original como evidencia, sin modificarlo.

Cambio unico: retiro del ultimo byte LF (0A). Los otros 45.257 bytes permanecen
identicos; los 161 registros y sus 48 campos son iguales antes y despues.
No se modifican fechas, valores, vacios, delimitador, codificacion ni registros.
Se conservan los antecedentes y versiones previas. Usar V04 para el reintento.

Estado: pendiente de nueva carga y resultado PES; no aceptada ni congelada.
La ausencia de otros errores en el reporte no acredita aceptacion definitiva.
Tras Finalizado, conciliar el reporte validado 6048 con la carga enviada.
Gobernanza local con hashes y script; no se realizo commit ni push.
