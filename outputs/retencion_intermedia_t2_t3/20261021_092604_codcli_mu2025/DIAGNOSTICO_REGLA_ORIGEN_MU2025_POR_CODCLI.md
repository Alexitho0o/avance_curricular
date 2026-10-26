# MU2025: búsqueda de regla de origen y trazabilidad por CODCLI

Fecha: 2026-10-21T09:30:19.517594-03:00. Proceso: Matrícula Unificada. Referencia: ingresos UMAS T2/T3-2024 frente a observación MU2025. Hito relacionado: H001-RETENCION-IPSS162.

## Resultado

**B/C.** Las 83 personas que mantienen carrera corresponden a 83 CODCLI de origen distintos. En ambos respaldos DatosAlumnos, esos mismos CODCLI tienen ANOINGRESO=2024. Solo tres personas tienen además otro CODCLI de ingreso 2025 en la misma carrera. En las otras 80 no se observa tal matrícula nueva en los respaldos consultados.

**E.** No se localizó un script, bitácora o manifiesto de preparación de MU2025 que demuestre qué regla asignó origen 2025 a estos registros. La regla encontrada de copia de ingreso actual a origen pertenece al motor MU2026. La coincidencia FOR=1/ACT=ORI=2025 en el RAW MU2025 no demuestra que aquel motor se ejecutara para este archivo.

**D.** Sin cambios a fuentes, bases, Excel, reglas ni denominadores 558/1.150 y 222/124. Sin commit/push. Solo derivados agregados.

## Qué demuestra CODCLI

**C.** RUT identifica a la persona para localizar la discrepancia; CODCLI distingue sus matrículas. La investigación se hizo conservando los CODCLI originales y todas las carreras de la persona, sin decodificar año o período desde el texto de CODCLI. Se contrastaron valores de columnas ANOINGRESO/PERIODOINGRESO, no prefijos supuestos.

| Comprobación | T2-2024 | T3-2024 | Total | Clasificación |
|---|---:|---:|---:|---|
| Personas de misma carrera con origen 2025 en MU2025 | 41 | 42 | 83 | B/C |
| CODCLI de origen distintos con ANOINGRESO=2024 | 41 | 42 | 83 | B/C |
| Personas con otro CODCLI de ingreso 2025 en la misma carrera | 1 | 2 | 3 | B/C |
| Personas sin otro CODCLI de ingreso 2025 en esa carrera, en respaldos revisados | 40 | 40 | 80 | B/C |
| Mismo CODCLI de origen con fila ANOMATRICULA=2025 en 11998 | 3 | 7 | 10 | B/C |
| Mismo CODCLI de origen reproducido en respaldo 10246 | 41 | 42 | 83 | B/C |

**B.** No hay colisiones de persona en los 83 CODCLI de origen revisados. En 78 personas solo se observa un CODCLI para esa carrera en 11998 (40 T2 y 38 T3); cinco tienen más de uno (uno T2 y cuatro T3). Tener más de un CODCLI no implica que el segundo sea de ingreso 2025: solo tres cumplen esa condición.

**E.** Los tres nuevos CODCLI son candidatos que pueden afectar el enlace RUT/carrera. No se afirma que sean la matrícula que originó cada fila MU2025, porque dicha fuente no contiene CODCLI ni un puente de preparación que lo recupere. Tampoco se concluye que los diez registros ANOMATRICULA=2025 prueben por sí solos vigencia al corte; son valores observados de una extracción posterior.

## Límite de enlace con la fuente MU2025

**B.** 2025.xlsx, hoja 08-05-2025_22-26-22_Matrícula_P, tiene 2.371 filas y 45 columnas; no contiene CODCLI. Su Hoja1 es un resumen de siete filas por cinco columnas, no un respaldo de matrículas por CODCLI. En los 83 casos, la fuente granular ya trae ANIO_ING_ACT=2025, SEM_ING_ACT=1, ANIO_ING_ORI=2025, SEM_ING_ORI=1 y FOR_ING_ACT=1 como valores guardados. No existe fórmula en esas columnas del libro que explique la derivación.

**B.** El paquete XLSX no contiene conexiones, queryTables, externalLinks ni proyecto VBA. Metadatos docProps/core.xml: creator y lastModifiedBy ALEXI MARCELO BURGOS FLORES; created 2026-01-22T15:54:40Z; modified 2026-03-29T04:44:00Z. Estas fechas describen metadatos del libro, no el corte académico, la fecha de envío ni quién decidió la regla de origen.

**E.** Para establecer el CODCLI de cada fila de este envío falta el respaldo de preparación que lo conserve, o una relación explícita de salida con identificador de matrícula. No se fuerza una asignación por RUT cuando existen varias matrículas; no se infiere el vínculo desde nombres de personas o fechas de nacimiento.

## Scripts, reglas y manifiestos revisados

| Evidencia | Qué hace / qué contiene | Alcance demostrado | Clasificación |
|---|---|---|---|
| scripts/construir_base_retencion_mu_2022_2026.py, SELECTED_SOURCES 2025 (líneas 48–53), DEMONSTRABLE_ALIASES y main | Lee la hoja granular de 2025.xlsx, toma los campos de ingreso por encabezado y normaliza tipo. Único alias 2025: VIGENCIA→VIG. | Consolida valores ya presentes; no deriva origen 2025 desde CODCLI. | C |
| MANIFEST_BASE_RETENCION_MU_2022_2026.json e INVENTARIO_FUENTES_SHA256.json, run 20260901_142342 | Registran fuente, esquema, hash, filas y faltantes. | Trazabilidad de consolidación; no documentan la creación de la cohorte del envío 2025. | B/C |
| INVENTARIO_CANDIDATOS_Y_EXCLUSIONES.json, mismo run | Un solo candidato dentro de Enviados/Matrícula Unificada/2025: 2025.xlsx, seleccionado. Los otros nombres 2025 son salidas de Avance Curricular bajo carpeta 2026. | No son una segunda fuente MU2025 ni una bitácora del origen. | B/C |
| control/config_campos_ing.json (meta: Manual MU2026, creación declarada 2026-04-08), campos ANIO_ING_ACT/ANIO_ING_ORI | ANOINGRESO es fuente primaria del actual; FOR=1 usa COPIA_ACTUAL. CODCLI figura solo como fallback del actual. | Regla implementada MU2026. No hay evidencia de ejecución sobre el archivo MU2025. | C/E |
| scripts/motor_campos_ing.py, R_ACT_01 (líneas 102–109), R_ORI_A01/R_ORI_S01 (248–257) | Lee ANOINGRESO válido y para FOR=1 copia año/semestre actual a origen. | Con ANOINGRESO=2024 válido, esta ruta empieza por 2024; no contiene una conversión probada de T2/T3-2024 a 2025. | C |
| codigo_gobernanza_v2.py, líneas 3987–3994 y 4403–4408 | Fuerza origen igual al actual bajo política FOR=1; registra campos fuente/método. | Implementación del flujo 2026. Requiere saber qué asignó primero ANIO_ING_ACT=2025; no prueba la generación de MU2025. | C/E |
| control/campos_ing_governance_report.md | Generado 2026-04-08 04:38:06, 1.364 registros; reporta R_ACT_01 y reglas R_ORI. | Corrida diferente a las 2.371 filas MU2025; no hay vínculo por hash ni manifiesto que la declare generadora de 2025.xlsx. | B/C |

**E.** No se localizaron las trazas individuales campos_ing_trace_long.tsv o for_ing_act_trace_long.tsv en las ubicaciones control/ y resultados/ consultadas ni archivos Git registrados con esos nombres. La ausencia en esas ubicaciones no prueba inexistencia global. No se ejecutó ningún motor de producción.

## Alcance de la búsqueda de respaldos

**C.** Se buscaron referencias de MU2025, 2025.xlsx, 08-05-2025_22-26-22, ANIO_ING_ORI y ANOINGRESO en scripts, control, manifiestos, documentación y respaldos textuales de avance_curricular (incluidos archive y .local_restricted) y documentación/manifiestos de CARACTERIZACIÓN. También se buscaron scripts SQL/PQ/notebooks/BAS/PS1 asociados. Las referencias exactas encontradas remiten al archivo de entrada y al diagnóstico; no se identificó el generador 2025 con enlace verificable a su hash.

**B.** La carpeta original Enviados/Matrícula Unificada/2025 se inventarió recursivamente: contiene solo 2025.xlsx, 811.353 bytes. Esto coincide con el único candidato MU2025 de la corrida de consolidación. No se emplearon reportes de caracterización/FCU o Avance Curricular como sustitutos del envío MU2025.

## Conclusión y pendiente concreto

**B/C.** Se verificó la matrícula interna por CODCLI, no solo la persona. Los 83 CODCLI originales permanecen con ingreso 2024 en los respaldos; tres personas tienen otra matrícula de ingreso 2025 en igual carrera y 80 no. El cambio de origen observado ya viene de la fuente MU2025.

**E.** Las fuentes revisadas no entregan información suficiente para responder con certeza qué regla asignó origen 2025. Falta la versión del generador/exportador o consulta de preparación MU2025, sus parámetros y una traza CODCLI→fila enviada→regla de año/semestre. No corresponde identificar R_ORI_A01 como causa confirmada de MU2025 ni convertir la hipótesis en una corrección.

## Fuentes y hashes

1. `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`; hoja `BASE_RETENCION_MU`; SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
2. `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx`; hoja `Hoja1`; SHA-256 `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`.
3. `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx`; hoja `Hoja1`; SHA-256 `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`.
4. `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx`; hoja `08-05-2025_22-26-22_Matrícula_P`; SHA-256 `9ceb4f3e15111a4d968410fcb799d56bd349a6e91a9d473d5a9cceedaab15062`.
5. `/Users/alexi/Documents/GitHub/avance_curricular/DURACION_ESTUDIOS.tsv`; SHA-256 `701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e`.
6. `/Users/alexi/Documents/GitHub/avance_curricular/scripts/construir_base_retencion_mu_2022_2026.py`; SHA-256 `edcade5f199443517ce6ec88a7c43a58cf52ee80a671ab0b9eddec0f1e6de19e`.
7. `/Users/alexi/Documents/GitHub/avance_curricular/control/config_campos_ing.json`; SHA-256 `d02d2affe3069b79caf64a1df0c8e6f2ad0ac4833db9527f74b6dd0b50279f63`.
8. `/Users/alexi/Documents/GitHub/avance_curricular/scripts/motor_campos_ing.py`; SHA-256 `5414b19d1e6e9a7f3291103004c8b37488802e6fd93abd0ce2d2e83d33149cd5`.
9. `/Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py`; SHA-256 `ddb8cba1f4af1df8c273db90b462951db3db1ce52c3218af8d472e62da9e3c4d`.
10. `/Users/alexi/Documents/GitHub/avance_curricular/control/campos_ing_governance_report.md`; SHA-256 `6ee210b408b31bd2f080df29f0c7d7a0fb49b6b77e673cb1deaad500c750c640`.
11. `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json`; SHA-256 `746539ed62a3a3a051da14fd7f32b90fc6fd30a426304386d54e19c203d74145`.
12. `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/INVENTARIO_CANDIDATOS_Y_EXCLUSIONES.json`; SHA-256 `ad50d57a8c72ab8a6fccb8e16e98bc8d241298bcbe786130144310200993822f`.
13. `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/INVENTARIO_FUENTES_SHA256.json`; SHA-256 `a5b5f4e393c51b0dcfb6a34c4f796c94e396c903679950d246dc36eaba719e1b`.
14. `/Users/alexi/Documents/GitHub/avance_curricular/data/reglas_negocio/mu2027/estudio/MANIFEST.json`; SHA-256 `a8893104074228e643492a4a63dbc04c85be080b020915d6b15a02313432fd42`.

## QA y checkpoint

**C.** QA de consistencia OK: 41+42=83 personas y CODCLI distintos; 3+80=83; todos los CODCLI de origen conservan ANOINGRESO=2024; cero colisiones de persona por CODCLI; hashes de las fuentes revalidados sin cambios. Solo se guardan conteos y descripciones, sin identificadores individuales. La causalidad sigue pendiente E.

**B/C.** `/Users/alexi/Documents/GitHub/avance_curricular`: rama `feature/ire-2026`, HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040` sin cambio.

**B/C.** `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN`: rama `main`, HEAD antes/después `aba337784ccde0537fc21b2977b351170ed335e8` sin cambio.

**D.** Derivados nuevos únicamente en esta carpeta. Cambios ajenos preservados; sin commit/push.
