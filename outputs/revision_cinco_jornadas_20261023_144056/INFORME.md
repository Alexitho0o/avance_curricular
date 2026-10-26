# Cinco destinos pendientes después de los siete cierres aprobados

**D/C.** Los siete cierres aprobados están aplicados en `v5_20261023_siete_jornadas`.
Este diagnóstico revisa otras cinco observaciones de tres personas, sin nuevas adjudicaciones.
La atribución documental de los cierres internos sigue pendiente. No cambia tasas ni denominadores.

| Caso | Destinos pendientes | Código T1 observado (B) | Hallazgo adicional (B) | Qué falta (E) |
|---|---|---|---|---|
| INF35-03 | T2 y T3-2024 (2) | I162S2C1J2V4 | Se confirma V en los respaldos de preparación 2024; 14 filas entre hojas y copias, no 14 matrículas distintas. | Situar el paso a D por período y distinguir J1V1/J1V2. |
| INF35-04 | T2 y T3-2024 (2) | I162S2C1J1V2 | Se confirma D en los respaldos de preparación 2024; 8 filas entre hojas y copias, no 8 matrículas distintas. | Situar los cambios D/V: los respaldos de promedios discrepan para la actividad histórica. |
| INF35-10 | T2-2025 (1) | I162S2C1J2V4 | DATOS4094 V y DATOS4490/4649 O conservan la misma fecha de matrícula/firma, 24-01-2025. | Determinar si el cambio a O ya regía en T2; las fechas comunes no lo resuelven. |

**B/C. Confirmación del origen 2024.** Se revisaron seis libros de preparación de MU2024,
con 22 filas coincidentes por RUT exacto con DV y contexto IINF. No contienen CODCLI
en el esquema seleccionado: no se inventó esa llave ni se eligió expediente por nombre.
Se conservaron encabezados duplicados separadamente, porque JORNADA UMAS y la
columna posterior JORNADA SIES no son el mismo campo. En DATOS598, filas 1011/926,
y DATOS293, hoja SIES Final, filas 860/775, los componentes y códigos son
respectivamente J2V4 para INF35-03 y J1V2 para INF35-04. Coinciden con el ancla
MU2024 ya documentada. Esto refuerza el origen T1; no acredita el destino T2/T3.
El nombre «SIES Final» no acredita por sí solo envío ni aceptación en plataforma.

**B/E. Actividad fechada no equivale a jornada histórica.** En PRUEBA CUMPLIMIENTO
INGRESO CALIFICACIONES T3_2024.xlsx, hoja DATOS CRUDOS U+ 19-11-2024, hay dos filas
para INF35-03 (1866–1867) y cuatro para INF35-04 (1971–1974), plan IINF20241,
período 3, inicio de asignatura 14-10-2024, fin 04-01-2025 y medición 19-11-2024.
Las secciones son 1 y 20 respectivamente; esa hoja no contiene JORNADA.
Sin equivalencia documentada sección-asignatura-período↔jornada no se transforma
ese número en J1 o J2. Fechas de asignatura no son fechas de cambio de plan/jornada.
PROMEDIOS2071/3233 conservan actividad del período pero no acreditan por sí solos
la vigencia histórica de la jornada que acompaña al reporte.

**B/E. Fechas del tercer caso.** Para INF35-10 se releen DATOS4094, DATOS4490,
DATOS4649, PROMEDIOS3233 y la foto T3-2025. Matrícula/firma permanecen en enero
mientras cambia la jornada V/O y aparece situación 49. Por tanto esas fechas
no identifican el acto del cambio. T1 V y T3 O delimitan los contextos observados,
pero no adjudican T2. No se ordenan eventos por número de reporte, ni se
retropropaga el estado de la foto T3 a T2.

**C. Trazabilidad.** RESULTADOS.json contiene por observación las referencias
archivo/hoja/fila/hash. INVENTARIO.json distingue esquemas leídos y hojas que
no cumplen el esquema buscado; no dice que estas últimas carezcan de personas.
La primera exploración exigía CODCLI y no encontraba estos respaldos: se corrigió
el lector para RUT exacto + contexto de carrera. Los ensayos anteriores sin
manifiesto son exploratorios y no sustituyen este diagnóstico.

**C/E. Resultado:** cero cierres adicionales; permanecen cinco destinos por
jornada y, fuera de este foco, seis homologaciones. El foco original de 35 queda
en 24 reutilizables y 11 pendientes. No se fuerza una versión ni se convierte
una ausencia de evidencia en deserción. Bases, denominadores, Excel y diccionario
v5 permanecen iguales durante esta revisión. Sin commit ni push.
