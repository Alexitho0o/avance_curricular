# Comprobación de cobertura: ingresos T1/T2/T3 y MU del año siguiente

Fecha: 2026-10-21T09:11:19.297684-03:00. Proceso: Matrícula Unificada y revisión de retención intermedia IPSS 162. Referencias: ingresos 2024 frente a MU2025; ingresos 2025 frente a MU2026. Hito relacionado: H001-RETENCION-IPSS162.

## Resultado y alcance

**B/C.** Ambos archivos MU contienen personas observadas como ingresos de los tres períodos del año anterior. No contienen a todas las personas observadas en DatosAlumnos. La presencia se verificó por identificador; no implica coincidencia de cohorte, vigencia ni retención elegible.

**D.** Se mantienen sin cambios los denominadores anuales 558/1.150 y los denominadores específicos aprobados T2-2025=222 / T3-2025=124. Las poblaciones de DatosAlumnos de este reporte son controles de cobertura, no denominadores nuevos. No se modificó Excel ni fuente original; no se ejecutó commit/push.

## Regla aplicable y limitación normativa

**A — MU2026, Manual_Matrícula_Unificada_2026.pdf, página 5, sección 2.** Deben informarse estudiantes matriculados o con actividades inscritas en carreras/programas impartidos durante 2026. La fecha estadística de pregrado es 30 de abril (página 3); la página 5 vincula la contabilización SIES a matrícula del primer semestre 2026 o anterior. Las páginas 17–18 indican que un registro con VIG=0 permanece en datos pero no cuenta en matrícula total ni beneficios.

**C.** Por tanto, el manual 2026 no acredita que todo ingreso de 2025 deba arrastrarse automáticamente como matrícula de 2026, con independencia de su matrícula/actividad de 2026. Tampoco convierte la presencia de una fila VIG=0 en matrícula vigente.

**E.** No se localizó un manual MU2025 específico en la búsqueda por nombre en los repositorios/proyecto consultados. No se presenta MU2026 como norma de MU2025 ni se anticipa una regla MU2027. El alcance observado de MU2025 sí se comprobó con sus datos.

## Método

**C.** Se seleccionan ANOINGRESO y PERIODOINGRESO en Hoja1 de DATOSDEALUMNOS_11998; se cuentan RUT válidos distintos por grupo. Se busca la misma persona, sin filtrar año de origen ni VIG, en BASE_RETENCION_MU del año siguiente, TIPO_DOC=R, N_DOC+DV. Se normalizan puntos, espacios, mayúscula K y ceros iniciales; se valida dígito verificador. Se prueba además limpieza de separadores y coincidencia de cuerpo con otro DV, sin aceptar esta última como match. Los conteos VIG=1 son personas con alguna fila 1; VIG=0 son personas con todas sus filas 0.

**B/E.** DATOSDEALUMNOS_11998 está respaldado por manifiesto P3 y el inventario de fuentes; la fecha de ejecución/congelamiento no certifica un cierre académico. El inventario no acredita su fecha de extracción como snapshot del cierre. DATOSDEALUMNOS_10246 es un segundo respaldo congelado, no otro cierre certificado. Ninguno acredita por sí solo el universo histórico completo de ingresos. Una persona puede pertenecer a más de un grupo; no sumar filas como total global único.

## Presencia por período de ingreso observado

| Ingreso UMAS | MU consultada | Personas observadas | Presentes | Con VIG=1 | Solo VIG=0 | Ausentes | Clasificación |
|---|---:|---:|---:|---:|---:|---:|---|
| 2024-T1 | 2025 | 979 | 510 | 457 | 53 | 469 | B/C |
| 2024-T2 | 2025 | 97 | 44 | 44 | 0 | 53 | B/C |
| 2024-T3 | 2025 | 95 | 49 | 48 | 1 | 46 | B/C |
| 2025-T1 | 2026 | 1744 | 1340 | 926 | 414 | 404 | B/C |
| 2025-T2 | 2026 | 266 | 84 | 76 | 8 | 182 | B/C |
| 2025-T3 | 2026 | 180 | 53 | 50 | 3 | 127 | B/C |

**B/C.** Cero filas con llave inválida en estos seis grupos. Cero ausencias recuperadas por normalización adicional y cero coincidencias del mismo cuerpo con otro DV. El respaldo 10246 reproduce los seis conteos de personas/presentes/ausentes del 11998. Esta coincidencia no acredita exhaustividad de los ingresos.

## Presencia no equivale a cohorte de origen coincidente

| Ingreso UMAS | Presentes en MU | Con año de origen MU igual al ingreso UMAS | Otros años de origen MU (año:personas) | Clasificación |
|---|---:|---:|---|---|
| 2024-T1 | 510 | 396 | 1900: 67; 2009: 1; 2011: 1; 2012: 1; 2013: 1; 2015: 3; 2016: 1; 2017: 2; 2018: 3; 2019: 2; 2020: 4; 2021: 7; 2022: 13; 2023: 2; 2025: 6 | B/C |
| 2024-T2 | 44 | 0 | 2025: 44 | B/C |
| 2024-T3 | 49 | 3 | 2021: 1; 2023: 1; 2025: 44 | B/C |
| 2025-T1 | 1340 | 1087 | 2018: 1; 2019: 1; 2021: 1; 2022: 1; 2023: 4; 2024: 229; 2026: 16 | B/C |
| 2025-T2 | 84 | 79 | 2024: 2; 2026: 3 | B/C |
| 2025-T3 | 53 | 48 | 2023: 1; 2026: 4 | B/C |

**B.** En particular, los 44 ingresos T2-2024 encontrados figuran en MU2025 con ANIO_ING_ORI=2025 y SEM_ING_ORI=1. De los 49 ingresos T3-2024 encontrados, 44 figuran con origen 2025, tres con 2024 y dos con otros años. Las distribuciones completas de semestre y año están en RESULTADOS_AGREGADOS.json.

**E.** Esta divergencia entre ANOINGRESO UMAS y ANIO_ING_ORI SIES no demuestra cuál campo está equivocado ni una causa de recodificación. No se equipara PERIODOINGRESO trimestral a SEM_ING_ORI semestral; no se altera la cohorte para forzar coincidencias.

## Contexto observado de las ausencias

| Ingreso | Ausentes en MU | Sin fila ANOMATRICULA del año siguiente en 11998 | Con fila del año siguiente y algún VIGENTE UMAS | Con fila del año siguiente, sin VIGENTE UMAS | Clasificación |
|---|---:|---:|---:|---:|---|
| 2024-T1 | 469 | 461 | 3 | 5 | B/C |
| 2024-T2 | 53 | 50 | 0 | 3 | B/C |
| 2024-T3 | 46 | 44 | 0 | 2 | B/C |
| 2025-T1 | 404 | 373 | 19 | 12 | B/C |
| 2025-T2 | 182 | 175 | 6 | 1 | B/C |
| 2025-T3 | 127 | 123 | 3 | 1 | B/C |

**E.** No tener una fila ANOMATRICULA del año siguiente en esta extracción no demuestra no renovación o deserción; podría intervenir la cobertura o actualización de la extracción. VIGENTE en UMAS tampoco prueba vigencia al corte histórico ni equivale automáticamente al VIG enviado. Las categorías describen evidencia y no causas cerradas.

## Control de los denominadores aprobados: 222 y 124

| Origen | Denominador sin cambio | Presentes MU2026 | VIG=1 | Solo VIG=0 | Ausentes | Clasificación |
|---|---:|---:|---:|---:|---:|---|
| 2025-T2 | 222 | 80 | 74 | 6 | 142 | B/C |
| 2025-T3 | 124 | 50 | 48 | 2 | 74 | B/C |

**B/C.** De los 142 ausentes T2, 139 no tienen fila ANOMATRICULA=2026 en 11998; tres sí tienen fila 2026 VIGENTE y todas sus fechas de matrícula observadas son posteriores al 30 de abril. De los 74 ausentes T3, 72 no tienen fila 2026; uno tiene fila 2026 sin VIGENTE y uno tiene fila 2026 VIGENTE con fecha de matrícula posterior al 30 de abril. Todos tienen match en 11998. Las claves válidas no recuperan ausencias por formato ni por otro DV.

**E.** Las cuatro matrículas posteriores al corte son compatibles con una diferencia temporal, pero no prueban la causa de omisión en el envío: falta historia de cambios/envíos y estado al corte. Para las restantes ausencias no existe causa individual acreditada con estas fuentes. No se clasifican como desertores.

**B.** Entre los presentes de los archivos aprobados, T2 tiene 78 con origen SIES 2025 y dos con 2024; T3 tiene 47 con origen SIES 2025 y tres con 2026. No se elimina a estas personas ni se cambia el denominador.

## Verificación contra los archivos originales enviados

| Archivo | Hoja | Filas fuente | Filas consolidadas | Comparación | Clasificación |
|---|---|---:|---:|---|---|
| 2025.xlsx | 08-05-2025_22-26-22_Matrícula_P | 2.371 | 2.371 | 32 columnas normalizadas idénticas fila a fila | B/C |
| MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx | CONSOLIDADO | 4.105 | 4.105 | 32 columnas normalizadas idénticas fila a fila | B/C |

**C.** Se reutilizó exclusivamente typed_value y alias demostrados del constructor para comparar el contenido de las 32 columnas, sin ejecutar la construcción ni reescribir la base. Los SHA-256 de los archivos originales coincidieron con el inventario de la corrida 20260901_142342. Se descarta pérdida de filas en esa consolidación; no se acredita que el origen enviado capture todas las matrículas que debían existir.

## Pendientes y siguiente paso

**E.** Permanecen pendientes la cobertura completa de ingresos/renovaciones y el motivo documentado de cada ausencia; la explicación de años de origen distintos; y los respaldos de matrícula al cierre específico T2/T3. Los archivos anuales sí permiten esta comprobación de presencia, pero no acreditan automáticamente cada cierre intermedio.

**D/C.** Siguiente paso: contrastar en el proyecto de DatosAlumnos la historia de matrícula y cambios de las personas ausentes y la definición de ANOINGRESO, manteniendo los identificadores en área sensible. No cambiar fórmulas, reglas ni denominadores a partir de esta observación.

## Fuentes, hashes y trazabilidad

1. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`; hoja `BASE_RETENCION_MU`. SHA-256: `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
2. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx`; hoja `Hoja1`. SHA-256: `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`.
3. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx`; hoja `Hoja1`. SHA-256: `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`.
4. B — archivo/manifiesto observado: `/Users/alexi/Downloads/cierre/Matrícula T2_2025 2.xlsx`; hoja `T2_2025`. SHA-256: `ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3`.
5. B — archivo/manifiesto observado: `/Users/alexi/Downloads/cierre/Matrícula T3_2025 2.xlsx`; hoja `T3_2025`. SHA-256: `68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc`.
6. B — archivo/manifiesto observado: `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx`; hoja `08-05-2025_22-26-22_Matrícula_P`. SHA-256: `9ceb4f3e15111a4d968410fcb799d56bd349a6e91a9d473d5a9cceedaab15062`.
7. B — archivo/manifiesto observado: `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/REPORTE JULIO 2026/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx`; hoja `CONSOLIDADO`. SHA-256: `fab3f4c3ba10534e0ec1d8eea4249a5bbbdc03cc012534b3184f59d9d3d663d7`.
8. A — manual: `/Users/alexi/Documents/GitHub/avance_curricular/Manual_Matrícula_Unificada_2026.pdf`. SHA-256: `3626600782798fbb5afa4100975eeffd2155b4912a112f63cee42f9741a82990`.
9. C — implementación: `/Users/alexi/Documents/GitHub/avance_curricular/scripts/construir_base_retencion_mu_2022_2026.py`. SHA-256: `edcade5f199443517ce6ec88a7c43a58cf52ee80a671ab0b9eddec0f1e6de19e`.
10. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json`. SHA-256: `746539ed62a3a3a051da14fd7f32b90fc6fd30a426304386d54e19c203d74145`.
11. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/INVENTARIO_FUENTES_SHA256.json`. SHA-256: `a5b5f4e393c51b0dcfb6a34c4f796c94e396c903679950d246dc36eaba719e1b`.
12. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/04_AUDITORIA/manifest_ejecucion.json`. SHA-256: `c0f23e85071dd0c319d1bd1bff05f22a49d898a7ba6d67bc4882595113690c8a`.
13. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json`. SHA-256: `bda8a15c0f0689bf013f94882a20cdb6fac25107888641af69c9210bc663f588`.
14. B — archivo/manifiesto observado: `/Users/alexi/Documents/GitHub/avance_curricular/data/versiones_historicas_sies_umas/fase_1_20261015/inventario.json`. SHA-256: `8c0b9f02c013f94b98dc72be1eae9912dadd991ba0e5a3fa7a64da3ef3904ae2`.

## QA y checkpoint

**C.** QA de conteos OK: presentes+ausentes=población; VIG1+soloVIG0=presentes; categorías de ausencia suman ausentes; denominadores 222/124 y presencias 80/50 reproducidos; comparación 32 columnas sin diferencias en ambos años; hashes de entrada revalidados al cierre. Solo resultados agregados en disco. No se generaron archivos de identificadores individuales.

**B/C.** avance_curricular: rama `feature/ire-2026`, HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040`. CARACTERIZACIÓN: lectura de fuentes en rama `main`, HEAD verificado `aba337784ccde0537fc21b2977b351170ed335e8`. Se conservaron cambios previos ajenos. No hubo commit/push. Los únicos archivos nuevos de esta comprobación están en `/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_090522_cobertura`.
