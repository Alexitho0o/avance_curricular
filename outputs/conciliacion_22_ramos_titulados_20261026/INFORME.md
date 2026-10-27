# Revisión de los 22 ramos y respaldo de titulación · 26-10-2026

**[B/C] Alcance:** 22 ramos discrepantes en siete pares carrera–plan; fuentes institucionales de Avance Curricular, PROMEDIOS y Titulación Unificada, v11 y la oferta anual ya contrastada. Los períodos son códigos nativos UMAS.

## Respaldo recuperado

**[B/C]** Se encontró una copia legible de `1668382 Captura IES Incremental5320 Oferta Académica Titulados5319 Titulados Histórico.xlsx`, en la carpeta `Matrícula Unificada/2026/SEGUNDA CARGA/ARCHIVOS VARIOS/`, SHA-256 `149367ca3f7be7717f958e2ce0f8924e18353e6302766b1abf737c54b5dce8e3`. Se leyeron `Res_Tit_Carga` y `5319 Titulados Histór`. Ruta exacta y SHA en EVIDENCIA_AGREGADA.json.

**[B/C]** Las 431 llaves distintas del CSV de Titulación Unificada 2026 coinciden con `Res_Tit_Carga` en tipo de documento, número, DV y código de obtención del título. La comprobación no cubre los otros campos ni prueba envío o aceptación.

## Equivalencias de los ramos

**[B/C]** `estructura_asignaturas.json` recupera relaciones explícitas de la hoja `BBDD Bruta` del listado de planes. Entre los 22 casos, uno tiene una relación entre el plan y ramo observado y un ramo del plan original: `IETMREOL / EH106IETMREOL` declara como equivalente `IETMREOL20191 / AG106IETMREOL` (fila 4668 de la fuente). Esta relación prueba una referencia declarada en el catálogo; no acredita por sí sola la homologación individual, fecha de migración ni vigencia del plan [E].

**[E]** Para los otros 21 no se encontró una relación explícita de ese tipo en la estructura revisada. Las dos pistas RAMOEQUIV y las tres coincidencias de nombre de la revisión anterior permanecen como pistas, sin asignación automática. La lista de los 22 con sus relaciones y señales está en EVIDENCIA_AGREGADA.json.

## Actividad y titulaciones por plan

**[B/C]** Los períodos extremos indican la primera y última actividad encontrada en PROMEDIOS 12166; no son fechas de apertura ni cierre. Los titulados se cruzaron por RUT con DV y el mismo código SIES de v11. La columna de múltiples expedientes detecta posibles atribuciones ambiguas dentro de v11 para esa persona y código; no excluye otras fuentes o cambios no observados. Las personas no se suman entre planes.

| Carrera / plan | Primera actividad | Última actividad | Personas con registro de título y mismo código v11 | De ellas, con más de un expediente compatible |
|---|---|---|---:|---:|
| IECIREOL / IECIREOL20201 | 2019-2 | 2024-5 | 9 | 0 |
| IECIREOL / IECIREOL20211 | 2021-1 | 2026-2 | 104 | 3 |
| IEMORE / IEMORE20211 | 2019-1 | 2022-2 | 16 | 0 |
| IETMRE / IETMRE20191 | 2019-1 | 2023-2 | 8 | 0 |
| IETMREOL / IETMREOL | 2019-3 | 2022-3 | 14 | 0 |
| TPCREOL / TPCREOL | 2019-1 | 2020-1 | 5 | 0 |
| TTMRE / TTMRE20211 | 2020-2 | 2024-2 | 10 | 1 |

**[E]** Título del mismo RUT y código no demuestra que el título corresponda al plan de cada fila: la persona puede tener más de un CODCLI o haber cambiado de plan. La ausencia de actividad tampoco acredita cierre. Algunas actividades son anteriores al año textual del nombre del plan; por eso no se infiere vigencia desde ese nombre.

**[B/C/E]** Las fechas o años de titulación, códigos y períodos observados por cada uno de los siete planes están en EVIDENCIA_AGREGADA.json. Allí se conserva la distinción entre código documental y correspondencia interna existente en v11; este estudio no crea nuevas asignaciones. Para cerrar vigencia se necesitan fechas efectivas de inicio/fin del plan y, para cada título ambiguo, la correspondencia verificable entre documento, expediente y plan.

## Control

- [Evidencia agregada](EVIDENCIA_AGREGADA.json) y [procedimiento reproducible](revisar_evidencia.py); no se escriben RUT, CODCLI ni nombres de personas.
- Se verificaron SHA-256 de PROMEDIOS, CSV, respaldo y base privada. No se alteraron fuentes, v11, denominadores ni tasas.
- Sin commit ni push.
