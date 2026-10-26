# INF35-07 cerrado y revisión temporal de 14 observaciones

**D/C.** Aplicada la autorización de Alexi: **INF35-07/T3-2025 → I162S2C1J2V4**, como correspondencia interna. Edición activa `v3_20261023_inf35_07`. Conserva v2 y las decisiones previas; el documental y aceptación SIES siguen pendientes. La jornada V observada en la foto T3 no se confunde con O del contexto posterior conservado. Solo se adjudicó esta observación.

**C.** Foco original de 35 observaciones: **15 reutilizables y 20 pendientes** (14 destinos de jornada y 6 homologaciones TPAS). No son 35 personas ni denominadores de retención.

## Hallazgo nuevo: INF35-12

**B.** Se localizaron en la auditoría gobernada de DatosAlumnos y se releyeron directamente los respaldos originales:

| Respaldo nominal | Jornada observada |
|---|---|
| DATOSDEALUMNOS_10246, congelamiento 21-jul-2026 | O |
| 25-ago-2026 | O |
| 29-sep-2026 12:00:39 | O |
| 30-sep-2026 12:00:38 | D |
| 2-oct-2026 12:00:40 | D |
| 21-oct-2026 12:00:37 | D |

**B/C.** Entre las extracciones nominales del 29 y 30 de septiembre cambia JORNADA de O a D, conservando RUT, CODCLI, carrera y clave de matrícula. Cambia también SITUACION; FECHAMATRICULA se mantiene. El respaldo de 2 de octubre corrobora D. La relación con la fuente está registrada por hoja, fila y hash en el detalle privado.

**E.** Esto acota cuándo aparece el cambio en los datos, no acredita la fecha efectiva de la solicitud/acto académico. La auditoría declara zona horaria de cortes no confirmada. No se presenta el instante del archivo como fecha oficial. El dato de 2-oct es evidencia temporal adicional para revisar T3-2026, pero no constituye una adjudicación de versión. **Jornada D por sí sola no decide V1/V2 u otra versión histórica**. I162S2C1J4V2 se conserva como código T1 de origen. No se asignó automáticamente J1V2 al destino.

**B/E.** Para T2, O está corroborado en el respaldo congelado de julio y en agosto/septiembre; no se convierte el congelamiento 21-jul en una foto exacta del 13-jul ni se presume ausencia de cambios intermedios. Las dos observaciones de INF35-12 quedan con evidencia temporal mejorada y código destino pendiente; no con una fecha inventada.

## Otras siete personas

**B/C.** La auditoría existente cubre 58 cortes nominales del 25-ago al 21-oct-2026. Para las ocho personas del foco registra 17 cambios de campos: uno de JORNADA (INF35-12), uno de SITUACION y otros de FECHAMATRICULA/NIVEL/NOTAENSENANZAMEDIA. No se localizaron otros cambios de jornada en ese intervalo. Se verificaron hashes de los derivados y se releyeron cinco originales de esa serie más DATOSDEALUMNOS_10246: 48 filas exactas, ocho por respaldo.

**B/E.** INF35-04 figura D en DATOSDEALUMNOS_10246 y O en Base Maestra desde agosto. Son respaldos de extractores distintos: la diferencia se documenta, pero no se certifica por sí sola como fecha de cambio en UMAS ni explica sus T2/T3-2024.

**E.** Los otros doce destinos siguen sin intervalo aplicable acreditado. Para los de 2024/2025, una serie que comienza en agosto 2026 es posterior al período investigado. Para INF35-11/T2-T3-2026, los seis respaldos releídos registran O; no ubican cuándo pasó desde el contexto T1 diurno. Se mantiene la evidencia previa y no se extrapola hacia atrás.

**C.** `RESUMEN_14_OBSERVACIONES.csv` conserva las catorce filas con año, período, código T1 y pendiente. Los cambios y las 48 filas de evidencia con identificadores permanecen únicamente en el almacenamiento privado declarado en MANIFEST.json. No se crean nuevas tasas ni se clasifica a nadie como desertor.

## QA y conservación

**C.** 24.774 consultas comparadas con v2: un cambio autorizado, 24.773 idénticas salvo edición. Índice MU completo idéntico; dimensiones y documental intactos. Tres consumidores locales coinciden en 35/35 consultas; doce pruebas sintéticas correctas. Excel V12 y fuentes conservan sus hashes. QA **OK_CON_ADVERTENCIAS**, por las limitaciones temporales y de atribución descritas, no por fallos de integridad.

**D/C.** Se registraron responsable Alexi, autorización, fecha/hora, alerta, descriptor anterior y operación antes/después. No se cambiaron bases, denominadores, fórmulas, tasas ni Excel. Rama feature/ire-2026; HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes/después. Sin commit ni push; no se afirma publicación remota ni sincronización de complementos.

**E. Reanudación:** contrastar la versión de destino de INF35-12 con evidencia personal/plan que corresponda a la jornada D del respaldo de 2-oct, conservando por separado el código de cohorte. Para el resto, localizar evidencia anterior a agosto 2026 que sea temporalmente comparable; no repetir la búsqueda de códigos T1 ya cerrados.
