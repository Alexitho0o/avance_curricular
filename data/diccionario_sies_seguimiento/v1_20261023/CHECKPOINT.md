# Checkpoint — diccionario SIES de seguimiento

B/C: integrada y verificada la consulta única; 24.774 observaciones, 5.901 personas,
6.622 expedientes carrera+CODCLI. Se reutilizan 21.561 códigos documentales anuales
atribuidos y 137 correspondencias internas aprobadas. Permanecen 3.076 excepciones
internas (1.750 personas con al menos una pendiente), sin nuevos cierres.

B/C: en familias con varias versiones presentes en las evidencias, 16.823
observaciones: 14.957 reutilizables y 1.866 pendientes. No son tasas de retención
ni denominadores de las cohortes. La cobertura del foco se basa en familias de
códigos documentados/candidatos existentes, no en un catálogo universal completo.

C: consulta desde PROYECTO_IPSS.json, sin copiar reglas. Tres consumidores con
paridad; 24.774 consultas exactas y 12 pruebas de conflictos/temporalidad superadas.
E: no acredita aceptación SIES ni todas las fechas efectivas. 25 filas anuales de
MU con otro tipo documental requieren adaptador de identidad; permanecen en las
bases originales. El constructor histórico del libro y complementos remotos no
se han modificado ni se declaran sincronizados.

Siguiente paso: los nuevos análisis deben consultar este servicio; abrir solo
las excepciones del expediente/período pertinente, manteniendo código de cohorte
de origen separado del código posterior. No reinvestigar los códigos reutilizables.
No incorporar propuestas a la versión activa sin evidencia/decisión específica.

Rama feature/ire-2026; HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040.
Integración local, sin commit ni push. Bases, libros y denominadores intactos.
