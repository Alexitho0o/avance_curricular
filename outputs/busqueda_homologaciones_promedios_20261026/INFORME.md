# Reconocimientos observados en respaldos PROMEDIOS · 26-10-2026

**[B/C]** Se revisaron tres extracciones PROMEDIOS por la llave literal `CODCARR + PLAN_DE_ESTUDIO + CODRAMO` para los 21 ramos pendientes, conservando estado, descripción, CONVALIDADO y RAMOEQUIV. Las fuentes son instantáneas potencialmente solapadas: no se suman sus filas ni se infiere fecha de extracción por el nombre.

| Respaldo | Ramos de los 21 encontrados en el mismo plan | Filas encontradas |
|---|---:|---:|
| PROMEDIOSDEALUMNOS_7804.xlsx | 21 | 33 |
| PROMEDIOSDEALUMNOS_3233.xlsx | 11 | 17 |
| PROMEDIOSDEALUMNOS_2071.xlsx | 14 | 21 |

**[B/C]** En 7804, los 21 pares plan–ramo están presentes en 33 filas. En **15 de los 21** hay al menos una fila cuyo estado es `I / HOMOLOGADO` o `E / CONVALIDACION`; en los otros seis se observaron estados `A / APROBADO` o `R / REPROBADO` sin I/E en esta extracción. Un mismo ramo puede tener ambos estados de reconocimiento. Los 15 son pares plan–ramo, no 15 personas, y no prueban una homologación universal.

| Plan | Ramo | Estados observados en 7804 | RAMOEQUIV observados |
|---|---|---|---|
| IECIREOL20201 | CA101IECIREOL | I HOMOLOGADO | CA101IECIRE |
| IECIREOL20201 | CA103IECIREOL | I HOMOLOGADO | CA103IECIRE |
| IECIREOL20201 | CA401IECIREOL | A APROBADO | CA401IECIREOL |
| IECIREOL20211 | AS31TPAREOL | A APROBADO | AS31TPAREOL |
| IEMORE20211 | AU105IEMORE | I HOMOLOGADO | AU105IEMORE |
| IEMORE20211 | AU201IEMORE | I HOMOLOGADO | AU201IEMORE |
| IEMORE20211 | AU305IEMORE | A APROBADO | AU305IEMORE |
| IEMORE20211 | CA306IEMORE | A APROBADO | CA306IEMORE |
| IETMRE20191 | CA306IETMRE | A APROBADO, R REPROBADO | CA306IETMRE |
| IETMREOL | AG101IETMREOL | E CONVALIDACION, I HOMOLOGADO | AG101IETMREOL, MA108IECIREOL |
| IETMREOL | AG102IETMREOL | E CONVALIDACION, I HOMOLOGADO, R REPROBADO | AG102IETMREOL, EH102IETMREOL |
| IETMREOL | AG201IETMREOL | E CONVALIDACION, I HOMOLOGADO | AG201IETMREOL, EH201IECIREOL |
| IETMREOL | AG206IETMREOL | E CONVALIDACION, I HOMOLOGADO | AG206IETMREOL, EH208IECIREOL |
| IETMREOL | AG302IETMREOL | A APROBADO | EH301IETMREOL |
| TPCREOL | AG11TPCREOL | E CONVALIDACION | AG11TPCREOL |
| TPCREOL | AG12TPCREOL | E CONVALIDACION | AG12TPCREOL |
| TPCREOL | AG16TPCREOL | E CONVALIDACION | AG16TPCREOL |
| TPCREOL | AG17TPCREOL | E CONVALIDACION | AG17TPCREOL |
| TPCREOL | AG21TPCREOL | E CONVALIDACION | AG21TPCREOL |
| TPCREOL | AG26TPCREOL | E CONVALIDACION | AG26TPCREOL |
| TTMRE20211 | AS21TTMRE | E CONVALIDACION, I HOMOLOGADO | AC201IETMRE, AS21TTMRE |

**[B/C/E]** El estado HOMOLOGADO o CONVALIDACION acredita que esa etiqueta fue observada en las filas correspondientes. No acredita por sí mismo una tabla institucional de equivalencias para todos los estudiantes ni la fecha efectiva de cambio de plan. Los valores de RAMOEQUIV se conservan como fueron observados, sin invertir su dirección ni aplicarlos a otros expedientes.

**[E]** Los cuatro vínculos formales título–CODCLI–plan siguen pendientes: los respaldos PROMEDIOS revisados contienen actividad por expediente, pero estos campos no son un registro de titulación formal con plan ni una bitácora de migración. Ver el informe anterior de búsqueda de titulación.

## Fuentes y control

Las rutas, hashes, filtros, años/períodos y recuentos por extracción están en RESULTADO_AGREGADO.json; el procedimiento `consultar_respaldos.py` verifica los hashes antes y después. No se cambian fuentes, bases, diccionario, tasas ni denominadores. No se realizó commit ni push.
