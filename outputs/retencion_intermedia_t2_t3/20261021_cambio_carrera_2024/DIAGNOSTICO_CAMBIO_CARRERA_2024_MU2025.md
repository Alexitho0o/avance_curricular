# Ingresos T2/T3-2024 con origen 2025 en MU2025: contraste de carrera

Fecha de ejecución: 2026-10-21T09:20:15.610944-03:00. Hito relacionado: H001-RETENCION-IPSS162.

## Objetivo y alcance

**D.** Revisar la hipótesis de cambio de carrera para las 44 personas de ingreso UMAS T2-2024 y las 44 de T3-2024 encontradas con ANIO_ING_ORI=2025 en MU2025. Son 88 personas distintas entre los dos grupos. Se conservan bases, reglas y denominadores 558/1.150 y 222/124. No se modifica el Excel ni se realiza commit/push.

## Resultado

**B/C.** No se confirma que el conjunto se explique por cambios de carrera. En 83 personas coincide el código de carrera observado en DatosAlumnos con COD_CAR en MU2025; cinco tienen otra carrera. Estos cinco tienen además una matrícula UMAS con ingreso 2025 en la carrera de destino. Solo uno está explícitamente marcado 24 - CAMBIO DE CARRERA; los otros cuatro tienen 23 - RETIRO - RETRACTO en la carrera anterior.

| Grupo observado | Con origen 2025 en MU2025 | Misma carrera observada | Otra carrera observada | Clasificación |
|---|---:|---:|---:|---|
| 2024-T2 | 44 | 41 | 3 | B/C |
| 2024-T3 | 44 | 42 | 2 | B/C |
| Total de personas distintas | 88 | 83 | 5 | B/C |

## Las cinco trayectorias con diferente carrera

| Ingreso | Carrera UMAS de ingreso 2024 | Carrera en RAW MU2025 | Código de carrera origen → destino | Situación en carrera anterior | Personas | Clasificación |
|---|---|---|---|---:|---|
| 2024-T2 | INGENIERIA EN CIBERSEGURIDAD | INGENIERIA EN CONECTIVIDAD Y REDES | 46 → 3 | ELIMINADO / 23 - RETIRO - RETRACTO | 1 | B/C |
| 2024-T2 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | CONTABILIDAD GENERAL | 57 → 85 | ELIMINADO / 23 - RETIRO - RETRACTO | 1 | B/C |
| 2024-T2 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | INGENIERIA EN CIENCIA DE DATOS | 76 → 88 | ELIMINADO / 23 - RETIRO - RETRACTO | 1 | B/C |
| 2024-T3 | INGENIERIA EN INFORMATICA | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 1 → 57 | ELIMINADO / 24 - CAMBIO DE CARRERA | 1 | B/C |
| 2024-T3 | TECNICO EN CONECTIVIDAD Y REDES | TECNICO EN CIBERSEGURIDAD | 6 → 47 | ELIMINADO / 23 - RETIRO - RETRACTO | 1 | B/C |

**B.** Los cinco destinos están presentes en DatosAlumnos con ANOINGRESO=2025 y PERIODOINGRESO=1. Esto prueba carreras distintas observadas para la misma persona; para los cuatro RETIRO - RETRACTO no acredita por sí solo un trámite administrativo de cambio interno. Tampoco prueba que el cambio de carrera sea la causa que generó ANIO_ING_ORI=2025.

## Qué trae ya el archivo original MU2025

**B.** En los 88 registros del RAW 2025.xlsx, hoja 08-05-2025_22-26-22_Matrícula_P, los campos se observan así:

| Campo RAW MU2025 | Valor | Registros/personas del conjunto | Clasificación |
|---|---|---:|---|
| ANIO_ING_ACT | 2025 | 88 | B |
| SEM_ING_ACT | 1 | 88 | B |
| ANIO_ING_ORI | 2025 | 88 | B |
| SEM_ING_ORI | 1 | 88 | B |
| FOR_ING_ACT | 1 | 88 | B |
| NIVEL_1 | 1ER AÑO | 88 | B |
| NIVEL_2 | NUEVO | 88 | B |
| VIGENCIA | VIGENTE | 88 | B |
| FECH_CAR | 2025-05-08 22:23:42 | 88 | B |

**B/C.** Cada persona del conjunto tiene una sola fila en el RAW MU2025. La clasificación de ingreso/origen 2025 ya existe como valor numérico en ese archivo; no la crea el cálculo de retención ni una fórmula de la consolidación. Los campos de ingreso son valores, no fórmulas, en las 2.371 filas del RAW. Su hoja adicional Hoja1 es un resumen de siete filas y cinco columnas, no otra base granular de trayectorias.

**B.** De las 83 personas con la misma carrera, 82 tienen FECHA_MATRICULA de año 2024 en el propio RAW MU2025 y una tiene fecha 2025. No se interpreta esa fecha como creación ni primera matrícula: su semántica temporal sigue pendiente. El mismo FECH_CAR acredita un valor de lote compartido; no identifica quién aplicó la regla de origen ni prueba un defecto.

## Controles de trayectoria y método

**C.** Misma persona mediante RUT normalizado de DatosAlumnos frente a TIPO_DOC=R + N_DOC + DV de MU; no se cruzan personas por nombres u otras características. Se mantiene toda matrícula encontrada. Se contrasta CODCARPR de las filas ANOINGRESO=2024/PERIODOINGRESO=2 o 3 contra COD_CAR usando solo las asociaciones explícitas CODCARPR_CANONICO/CODCARPR_ALIAS_LIST de DURACION_ESTUDIOS.tsv. Para los códigos del conjunto, las asociaciones son unívocas a nivel COD_CAR: IADM→76, ICIB→46, ICRE→3, IINF→1, TCIB→47, TCRE→6 y TPAS→57. Se corroboran además los nombres literales de carrera en el RAW MU2025. No se usa el puente compilado sin SEDE ni se construye un código único por inferencia.

**C/E.** La comparación determina identidad de carrera a nivel COD_CAR; no certifica igualdad de sede, jornada, versión o plan. Una carrera igual en estas observaciones tampoco demuestra ausencia de cualquier cambio intermedio no documentado. No se convierte trimestre UMAS en semestre SIES.

**B.** El respaldo gobernado anterior DATOSDEALUMNOS_10246 reproduce el ingreso 2024-T2/T3 y el mismo CODCARPR de los 88 registros del conjunto. Por tanto, la divergencia no aparece exclusivamente en el respaldo 11998.

**B/C.** Dos de las 88 personas también están en MU2024 (una de T2 y una de T3), ambas con origen 2024 y con COD_CAR distinto al informado en MU2025. Las otras 86 no tienen fila en MU2024; esa ausencia no demuestra que no hubieran ingresado durante T2/T3-2024. Los controles se presentan en CONTROLES.json.

## Referencia normativa y causa pendiente

**A — referencia exclusiva MU2026.** Manual_Matrícula_Unificada_2026.pdf, página 8, diferencia año de ingreso a carrera actual y año de origen y describe FOR_ING_ACT=3 para cambio interno. No se traslada esta edición como norma retroactiva a MU2025; para un dictamen normativo del envío 2025 falta su manual/regla de preparación aplicable.

**E.** Las fuentes revisadas no entregan información suficiente para responder con certeza por qué se asignó origen 2025 a las 83 personas que conservan carrera. Falta la regla o bitácora de generación del envío MU2025 que vincule ingreso trimestral UMAS, ingreso actual y cohorte de origen. Tampoco se acredita que los cinco cambios de carrera justifiquen reiniciar el año de origen. El archivo original demuestra la clasificación aplicada, pero no contiene su justificación causal.

**D.** No se propone ni aplica corrección o nueva regla de retención. Se conserva la hipótesis como parcialmente contrastada: cinco trayectorias con otra carrera, una marcada expresamente como cambio, 83 con misma carrera y causa de origen 2025 pendiente.

## Fuentes y SHA-256

1. `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`; hoja `BASE_RETENCION_MU`; SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
2. `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx`; hoja `Hoja1`; SHA-256 `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`.
3. `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx`; hoja `Hoja1`; SHA-256 `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`.
4. `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx`; hoja `08-05-2025_22-26-22_Matrícula_P`; SHA-256 `9ceb4f3e15111a4d968410fcb799d56bd349a6e91a9d473d5a9cceedaab15062`.
5. `/Users/alexi/Documents/GitHub/avance_curricular/DURACION_ESTUDIOS.tsv`; SHA-256 `701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e`.
6. `/Users/alexi/Documents/GitHub/avance_curricular/Manual_Matrícula_Unificada_2026.pdf`; SHA-256 `3626600782798fbb5afa4100975eeffd2155b4912a112f63cee42f9741a82990`.

## QA y checkpoint

**C.** QA OK para el contraste agregado: 44+44=88 personas sin intersección; 41+42=83 con misma carrera; 3+2=5 con distinta carrera; 83+5=88. Cinco destinos UMAS con ingreso 2025 comprobados. Hashes de entradas revalidados sin cambios. Ningún archivo de salida contiene RUT, N_DOC, CODCLI, nombre de persona ni fecha de nacimiento. La causa de origen 2025 permanece E.

**B/C.** Rama/HEAD antes y después:
- `/Users/alexi/Documents/GitHub/avance_curricular`: rama `feature/ire-2026`, HEAD `80ca13a5a249a1a2bd53a699f5f73689b1f53040` sin cambio.
- `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN`: rama `main`, HEAD `aba337784ccde0537fc21b2977b351170ed335e8` sin cambio.

**D.** Solo se crean derivados agregados en esta carpeta. Se conservan los cambios ajenos previos. Sin commit/push.
