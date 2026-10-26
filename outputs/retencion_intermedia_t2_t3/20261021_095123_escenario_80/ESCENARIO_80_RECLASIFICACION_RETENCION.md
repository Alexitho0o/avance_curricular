# Escenario separado: 80 ingresos 2024 reclasificados como origen 2025

Fecha: 2026-10-21T09:56:55.427917-03:00. Institución: IP San Sebastián, código SIES 162. Hito relacionado: H001-RETENCION-IPSS162.

## Alcance y decisión de preservación

**D.** Se mantienen íntegros los datos, fórmulas, reglas y denominadores actuales: cohorte 2024, 558 estudiantes; cohorte 2025, 1.150 estudiantes. También siguen intactos los denominadores del seguimiento T2=222/T3=124. Se construye un diagnóstico agregado externo al Excel. Sin commit/push.

**B/C.** Población: los 80 casos marcados 2+3 Ingreso (50) o Corrección (30) en el respaldo IPSS_Procesamiento.xlsx. Se excluyen los tres casos sin marca que tienen otra matrícula CODCLI de ingreso 2025 en la misma carrera. Son las mismas personas y CODCLI de origen de los diagnósticos anteriores; no se cambia su selección.

## Cruce con MU2026 y participación en el cálculo actual

| Observación MU2026 | Personas | Origen informado en MU2026 | Tratamiento en el cálculo actual de cohorte 2025 | Clasificación |
|---|---:|---|---|---|
| Con VIG=1 | 53 | Año 2024: 52 con semestre 2 y una con semestre 1 | COHORTE_INCONSISTENTE; no están en el denominador ni numerador actuales | B/C |
| Solo VIG=0 | 11 | Año 2024, semestre 2 | Incluidos en denominador 2025, sin retención | B/C |
| Sin registro MU2026 | 16 | No observado | Incluidos en denominador 2025, sin retención | B/C |
| Total | 80 | No se inventa origen para ausentes | 53 excluidos + 27 incluidos sin retención | B/C |

**C.** El cruce MU2026 se hace por TIPO_DOC+N_DOC+DV exactos, en cualquier carrera de la institución, como la lógica institucional del libro; CODCLI sirve para seleccionar la matrícula UMAS de origen. MU no contiene CODCLI. Se preservan todas las filas y se cuentan personas, sin cruces aproximados. No se presentan los 53 vigentes como retenidos de la cohorte 2025, porque su cohorte informada en 2026 es distinta.

**D/E.** COHORTE_INCONSISTENTE es el proxy ya aplicado en el modelo; no se afirma que replique los casos específicos excluidos por SIES. Se mantiene sin reescribir su lógica.

## Resultado manteniendo la población y los denominadores actuales fijos

| Cohorte / observación | Denominador actual fijo | Retenidos actuales | Retenidos del mismo grupo bajo la prueba | Tasa del grupo fijo | Variación pp | Clasificación |
|---|---:|---:|---:|---:|---:|---|
| 2024 / 2025 | 558 | 326 | 326 | 58,42% | +0,00 | C |
| 2025 / 2026 | 1150 | 668 | 668 | 58,09% | +0,00 | C |

**C.** El efecto sobre los estudiantes que hoy integran los denominadores aprobados es cero puntos porcentuales. Las diferencias del escenario de reclasificación de población que sigue proceden de entradas/salidas de elegibilidad, no de sumar 53 retenidos a una cohorte fija ni de restar 80 del denominador 2025.

## Escenario hipotético de pertenencia a cohortes — no aplicado

**E/C.** Se simula exclusivamente en memoria restaurar ANIO_ING_ACT y ANIO_ING_ORI de 2025 a 2024 en las 80 filas MU2025 identificadas. Se conservan los semestres informados (1 en esas filas), los valores VIG, el catálogo, los programas y las fuentes MU2024/MU2026. Se vuelve a evaluar exactamente la lógica del libro. Esta es una sensibilidad del año; no establece una homologación de trimestres ni resuelve el semestre de origen correcto. Los denominadores simulados se muestran como resultados hipotéticos y no sustituyen los actuales.

| Cohorte | Actual: retenidos / estudiantes | Tasa actual C | Escenario: retenidos / estudiantes hipotéticos | Tasa escenario E/C | Cambio pp | SIES B | Brecha actual pp | Brecha escenario pp |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 2024 | 326 / 558 | 58,42% | 328 / 560 | 58,57% | +0,15 | 67,50% | -9,08 | -8,93 |
| 2025 | 668 / 1150 | 58,09% | 668 / 1123 | 59,48% | +1,40 | 58,21% | -0,12 | +1,27 |

Fórmulas del escenario (C, condicionado E):

- Cohorte 2024: actual 326/558; escenario (326+2)/(558+2)=328/560. Cambio de tasa: (328/560−326/558)×100=+0,1484895033 pp.
- Cohorte 2025: actual 668/1.150; escenario (668−0)/(1.150−27)=668/1.123. Cambio de tasa: (668/1.123−668/1.150)×100=+1,3965697472 pp.
- Brecha contra SIES: (tasa interna o hipotética − tasa SIES)×100. Se conserva precisión completa antes de redondear.

**B/C.** Solo dos de las 80 personas tienen alguna fila en MU2024. Actualmente esas dos filas se excluyen por COHORTE_INCONSISTENTE al encontrarse origen 2025 en MU2025; bajo la hipótesis de restituir solo el año, pasan a incluidas y retenidas. Las otras 78 no tienen fila MU2024. No se generan filas para ellas ni se las agrega a la cohorte 2024 mediante supuestos.

**C/E.** En 2025, los 53 vigentes ya estaban excluidos: sacarlos otra vez del denominador duplicaría el efecto. Solo salen los 27 que hoy figuran incluidos sin retención; se mantienen 668 retenidos. Esta sensibilidad aumenta la tasa y cambia el signo de la brecha contra SIES. No se utiliza el grado de cercanía a SIES como criterio para aprobar una corrección.

## Desglose de los 80 por programa informado en MU2025

| Código único | Carrera | Personas | Vigentes MU2026 | Solo VIG0 MU2026 | Ausentes MU2026 | Incluidos actualmente en cohorte 2025 | Retenidos actuales del grupo | Clasificación |
|---|---|---:|---:|---:|---:|---:|---:|---|
| I162S2C1J4V2 | INGENIERIA EN INFORMATICA | 9 | 4 | 2 | 3 | 5 | 0 | B/C |
| I162S2C3J4V2 | INGENIERIA EN CONECTIVIDAD Y REDES | 5 | 2 | 2 | 1 | 3 | 0 | B/C |
| I162S2C46J4V3 | INGENIERIA EN CIBERSEGURIDAD | 22 | 13 | 3 | 6 | 9 | 0 | B/C |
| I162S2C47J4V1 | TECNICO EN CIBERSEGURIDAD | 5 | 2 | 1 | 2 | 3 | 0 | B/C |
| I162S2C57J4V1 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 29 | 25 | 1 | 3 | 4 | 0 | B/C |
| I162S2C6J4V2 | TECNICO EN CONECTIVIDAD Y REDES | 2 | 2 | 0 | 0 | 0 | 0 | B/C |
| I162S2C76J4V1 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | 8 | 5 | 2 | 1 | 3 | 0 | B/C |

## Interpretación y pendientes

**C/E.** La reclasificación examinada tiene un efecto pequeño en la sensibilidad 2024 (+0,15 pp): no explica la brecha aproximada de −9,08 pp. El efecto hipotético 2025 es mayor (+1,40 pp), pero depende de cambiar la pertenencia a la cohorte en el escenario; los datos y denominadores actuales permanecen intactos.

**E.** La recuperación del año no determina automáticamente el semestre correcto ni acredita la elegibilidad al corte de los 78 sin fila MU2024. Tampoco se obtuvo autorización/bitácora de la reclasificación histórica. Los resultados del escenario no se presentan como tasas corregidas, oficiales o listas para sustituir el libro.

## Fuentes y método

**C.** Se leyó la lógica de 02_COHORTE_ELEGIBILIDAD del diagnóstico 20260930. Al carecer de cachés numéricas en esa copia, se evaluaron las mismas condiciones en memoria: cohorte de origen, catálogo anual/código único unívoco, Pregrado, Plan Regular, no especial, duración mínima por tipo, VIG, duplicados y siguiente año/cohorte. Antes de simular se reprodujeron exactamente los cuatro controles: 2022=305/224, 2023=366/258, 2024=558/326, 2025=1.150/668 (denominador/retenidos). No se reescribieron fórmulas ni se ejecutó el generador de producción.

**B.** BASE_RETENCION_MU del diagnóstico coincide en contenido con la base congelada usada en los diagnósticos previos. El informe SIES se reabrió: fila 59 identifica IPSS 162; T59=0,675 y U59=0,5821152192605331. Las cifras de comparación se conservan como datos observados de la publicación, no como resultado interno.

Fuentes verificadas:
- `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`; hoja/rango `BASE_RETENCION_MU` ; SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
- `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx`; hoja/rango `Hoja1` ; SHA-256 `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`.
- `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx`; hoja/rango `Hoja1` ; SHA-256 `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx`; hoja/rango `08-05-2025_22-26-22_Matrícula_P` ; SHA-256 `9ceb4f3e15111a4d968410fcb799d56bd349a6e91a9d473d5a9cceedaab15062`.
- `/Users/alexi/Documents/GitHub/avance_curricular/DURACION_ESTUDIOS.tsv`; SHA-256 `701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e`.
- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx`; hoja/rango `Final a carga / Carga_Completa (2) / Carga_Completa (3)` ; SHA-256 `e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4`.
- `/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx`; hoja/rango `BASE_RETENCION_MU / 01_CATALOGO_CARRERA / 02_COHORTE_ELEGIBILIDAD` ; SHA-256 `5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3`.
- `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/sies/RETENCION/Informe_Retencion_SIES_2026_270702026.xlsx`; hoja/rango `Retención 1er año x IES` T59:U59; institución A59:B59; SHA-256 `168ac8baea6aee65fa8a40dfca5a269993951142c89cb536805f550b1ac3297b`.

## QA y checkpoint

**C.** QA de consistencia OK: población=80; 53+11+16=80; 53 excluidos+27 incluidos=80; aporte actual del grupo 27 estudiantes/0 retenidos; siete programas suman 80. Controles actuales 2022–2025 reproducidos exactamente. En la prueba de población fija no cambian numeradores ni denominadores. En el escenario solo varían 80 registros en memoria; las dos nuevas inclusiones 2024 y las 27 salidas 2025 quedan explícitas. Hashes de fuentes revalidados; cero archivos de identificadores individuales generados.

**B/C.** `/Users/alexi/Documents/GitHub/avance_curricular`: rama `feature/ire-2026`, HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040`.

**B/C.** `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN`: rama `main`, HEAD antes/después `aba337784ccde0537fc21b2977b351170ed335e8`.

**D.** No se modificaron bases, archivos fuente, libro de retención ni denominadores actuales. Se conservan cambios previos ajenos. Sin commit/push. El siguiente paso, si se decide evaluar una corrección real, requiere resolver los pendientes históricos y aprobarla expresamente; este escenario no la ejecuta.
