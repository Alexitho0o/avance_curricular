# Revisión de 21 ramos y cuatro personas con más de un expediente

**[B/C] Alcance:** siete pares carrera–plan y los 21 ramos que quedaron sin relación explícita en la revisión anterior. Cuatro personas fueron seleccionadas porque tienen título con el mismo RUT y código SIES asociado a más de un expediente en la v11. La búsqueda no pretende cubrir todas las ambigüedades del proyecto.

## 21 ramos

**[B/C]** Se verificaron las relaciones declaradas de `estructura_asignaturas.json`, derivada del listado institucional de Avance Curricular `Listado_Planes_estudio_Sedes RE+CO.xlsx`, hoja `BBDD Bruta`. Para ninguno de los 21 se encontró una relación explícita directa, en ese mismo plan, entre el ramo observado y sus candidatos identificados por `RAMOEQUIV` o nombre. Las dos coincidencias de `RAMOEQUIV` y tres de nombre siguen disponibles como indicios **[E]**. La conclusión se limita a esta estructura y esos candidatos; no descarta equivalencias en otros documentos.

La relación previamente encontrada para el ramo 22, `IETMREOL/EH106IETMREOL` → `IETMREOL20191/AG106IETMREOL`, permanece documentada; no se extendió a los demás ramos.

**[B/E]** El listado leído contiene plan, ramo, nivel, equivalencia y sede, pero no trae campos de fecha de inicio o término de vigencia del plan. La oferta anual acredita el estado declarado de un código SIES por año; no fecha automáticamente la vigencia de un plan UMAS.

## Cuatro personas

**[B/C]** En los cuatro casos la hoja `Res_Tit_Unificada` tiene una traza calculada que selecciona el CODCLI del expediente anterior. En `DATOSDEALUMNOS_12159` y `11248`, el expediente anterior figura ELIMINADO con situación `10 - ACTUALIZACIÓN DE PLAN DE ESTUDIO 2024`, mientras el expediente posterior figura TITULADO, situación `31 - TITULADO APROBADO`. Las trayectorias de PROMEDIOS muestran actividad en ambos expedientes. La traza es un candidato técnico, no una declaración original de plan en el registro de título.

| Grupo | Personas | Plan anterior observado | Plan posterior observado | Título observado |
|---|---:|---|---|---|
| Informática | 3 | IECIREOL20211 | IINF20241 | Código I162S2C1J4V2, fecha en 2026 |
| Conectividad | 1 | TTMRE20211 | TCRE20241 | Código I162S2C6J2V2, fecha en 2025 |

**[B/C]** En los tres casos de Informática PROMEDIOS muestra actividad del expediente anterior en 2022–2023 y del posterior en 2024–2025; en Conectividad, anterior en 2022–2023 y posterior en 2024. Estos datos respaldan revisar la atribución hacia el expediente posterior, pero no acreditan la fecha efectiva de migración ni demuestran por sí solos el plan formal del título **[E]**. Las fechas de matrícula declaradas en Datos Alumnos son distintas de la fecha efectiva de cambio y no se convierten en ella.

**[E]** Quedan cuatro atribuciones individuales pendientes. Hace falta una fuente que declare el expediente/plan del título o una bitácora de asignación/migración con fecha y alcance; el código SIES compartido no desambigua por sí solo. No se cambió la traza previa ni se asignó el título al plan posterior automáticamente.

## Archivos y resguardo

- `RESULTADO_AGREGADO.json` contiene los 21 ramos y las dos agrupaciones sin identificadores personales.
- `analizar.py` verifica hashes y usa el diccionario en modo lectura. Las fuentes y hashes están en el resultado.
- El detalle individual se guarda solo fuera de Git en la ruta privada indicada en el resultado, con permisos 0600; no se publican RUT ni CODCLI en este informe.
- No se modificaron fuentes, bases, diccionario, denominadores ni tasas; sin commit ni push.
