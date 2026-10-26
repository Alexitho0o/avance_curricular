# Rechazo V05: arancel anual cero

Proceso 2026, Oferta Academica 2027, Etapa 1 octubre, ID 17467.
Evidencia entregada por usuario: 23-10-2026_12-44-30_Oferta-Academica-Vigente-Editada-TP.csv.txt
(el archivo original conserva su nombre con acentos en esta carpeta).

PES reporta siete errores: cuando VIGENCIA_CARRERA es 1, ARANCEL_ANUAL
debe ser mayor a 0. Esta es evidencia de validacion observada en plataforma,
no una nueva cita del manual ni una decision institucional sobre los importes.

Filas V05: 56, 64, 66, 67, 68, 104, 107.
Codigos afectados: 53, 66, 68, 69, 70, 96, 99.

Se cotejaron V05 y Hoja2 del Excel institucional incorporado el 23-10-2026.
En los seis primeros codigos: matricula 990000 y arancel 0.
En el codigo 99: matricula 400000 y arancel 0.
Los valores coinciden exactamente con columnas D y G del Excel fuente.
Filas Excel respectivas: 17, 21, 19, 18, 25, 32, 9.

No trasladar ni duplicar la matricula en arancel por suposicion. Se requiere
confirmar los aranceles reales y, si el origen tenia los conceptos invertidos,
confirmar tambien que valor corresponde a matricula.

V05 RECHAZADA; no aceptada ni congelada. El reporte no contiene otros errores,
pero eso no confirma por si solo que no existan validaciones posteriores.
No se modifico el CSV ni se genero V06. Los 14 cambios de vigencia y los
140 registros de pregrado permanecen intactos en V05.
Reanudar con importes autorizados, nueva version, auditoria por celda y carga.
Respaldo local: sin commit ni push.
