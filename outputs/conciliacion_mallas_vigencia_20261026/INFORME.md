# Conciliación de mallas, oferta y titulados · 26-10-2026

**Alcance [B/C]:** 75 combinaciones UMAS carrera–plan con actividad en 12166 y estado TITULADO del extracto; comparadas con listado de Avance Curricular, diccionario v11 y oferta anual 2010–2026. Los códigos SIES provienen de v11 y conservan sus clases; no se producen asignaciones nuevas.

## Los 22 ramos no encontrados en su mismo plan [B/C/E]

La coincidencia de nombre o RAMOEQUIV es una pista, no una homologación aprobada. Si hay más de una señal pueden solaparse. El detalle de los planes donde reaparece cada código está en REVISION_AGREGADA.json.

| Carrera | Plan | Ramo observado | RAMOEQUIV que aparece en el plan | Mismo nombre en el plan | Presente en otros planes |
|---|---|---|---|---|---:|
| IECIREOL | IECIREOL20201 | CA101IECIREOL | — | — | 1 |
| IECIREOL | IECIREOL20201 | CA103IECIREOL | — | — | 1 |
| IECIREOL | IECIREOL20201 | CA401IECIREOL | — | — | 1 |
| IECIREOL | IECIREOL20211 | AS31TPAREOL | — | — | 2 |
| IEMORE | IEMORE20211 | AU105IEMORE | — | AU107IEMORE | 2 |
| IEMORE | IEMORE20211 | AU201IEMORE | — | — | 2 |
| IEMORE | IEMORE20211 | AU305IEMORE | — | AU308IEMORE | 1 |
| IEMORE | IEMORE20211 | CA306IEMORE | — | — | 1 |
| IETMRE | IETMRE20191 | CA306IETMRE | — | — | 1 |
| IETMREOL | IETMREOL | AG101IETMREOL | — | — | 2 |
| IETMREOL | IETMREOL | AG102IETMREOL | EH102IETMREOL | — | 2 |
| IETMREOL | IETMREOL | AG106IETMREOL | — | — | 2 |
| IETMREOL | IETMREOL | AG201IETMREOL | — | — | 2 |
| IETMREOL | IETMREOL | AG206IETMREOL | — | — | 2 |
| IETMREOL | IETMREOL | AG302IETMREOL | EH301IETMREOL | — | 2 |
| TPCREOL | TPCREOL | AG11TPCREOL | — | — | 1 |
| TPCREOL | TPCREOL | AG12TPCREOL | — | — | 1 |
| TPCREOL | TPCREOL | AG16TPCREOL | — | — | 1 |
| TPCREOL | TPCREOL | AG17TPCREOL | — | — | 1 |
| TPCREOL | TPCREOL | AG21TPCREOL | — | — | 1 |
| TPCREOL | TPCREOL | AG26TPCREOL | — | — | 1 |
| TTMRE | TTMRE20211 | AS21TTMRE | — | AC21TTMRE | 0 |

**[B/C]** Dos casos tienen RAMOEQUIV presente en el mismo plan; tres presentan igual nombre; 21 presentan el código en otro plan. Los recuentos se superponen. Ninguna de estas señales prueba por sí sola una equivalencia curricular ni fecha efectiva [E].

## Oferta y diccionario

**[B/C]** En 60 de los 75 pares carrera–plan hay contextos en el diccionario v11; los otros 15 no tienen contexto localizado en esta base. Para los 60 se cuentan 19478 observaciones con código documental, 95 con correspondencia interna y 2613 pendientes. Son observaciones, no personas, y cubren todos los años disponibles en v11.

**[B/C]** Las 19573 observaciones con código documental o interno tienen una fila de oferta en el mismo año. La comparación de cada código, sede, jornada, período y estado de oferta está en REVISION_AGREGADA.json. La oferta informa vigencia del código SIES, no vigencia completa del plan UMAS; no prueba envío o aceptación.

**[A]** Manual Oferta 2026, p.3: vigencia 1 con estudiantes nuevos; vigencia 2 sin nuevos, con antiguos; vigencia 3 sin nuevos ni antiguos. La ausencia de fila no acredita cierre. Ver docs/diagnostico_vigencia_oferta_20261016.md. No se extrapola a otro año sin su manual correspondiente.

## Titulados y avance

**[B/E]** El listado de planes de Avance Curricular fue leído y contrastado por carrera, plan, código de ramo y nivel. No acredita por sí solo fechas iniciales/finales ni vigencia histórica de cada plan.

**[B/E]** Se localizó Titulación Unificada 2026.csv: 431 filas, 23 columnas, sin encabezado, SHA-256 b52586f6741109e293c90896721ca5b879f5f51ec98a1c80650464aa52356dec. Los dos XLSX asociados de la misma carpeta no pudieron abrirse en esta sesión (BadZipFile). Una auditoría previa registra lectura de 431 registros y 5319 histórico, sin probar aceptación; no se pudo verificar el esquema del CSV contra los XLSX ahora, por lo que no se atribuyeron fechas de título ni códigos individuales a los planes con ese CSV. Tampoco se trató el estado TITULADO de PROMEDIOS como título formal con fecha.

**[E]** Pendiente por plan: identificar período efectivo y fuente curricular con versión, cotejar los 22 ramos y las dos llaves de plan sin listado; enlazar titulación por identidad y código con esquema acreditado y sin muchos-a-muchos. La documentación anual y las 1.303 asignaturas listadas no observadas deben revisarse como alcance, no como errores.

## Control y salidas

- REVISION_AGREGADA.json detalla los 22 ramos y la evidencia v11/oferta por cada par carrera–plan, sin identificadores individuales.
- revisar.py reproduce el contraste y verifica hashes de listado y base privada; RESUMEN.json conserva los conteos.
- No se modificaron las bases, los denominadores, el diccionario activo ni los originales. No se hizo commit ni push.
