# Auditoría de VIG efectivamente enviado y exposición de retención

**C — Consulta:** 2026-10-21T00:54:35.344272-03:00. Hito de referencia H001-RETENCION-IPSS162. Matrícula Unificada 2026, seguimiento institucional 2025-T2/T3 y diagnóstico anual 2022–2025.

## Conclusión

**B/C:** Sí existieron controles de nómina específicos, además del mapeo general histórico de estados. Las auditorías registran 448 personas cambiadas de VIG 1 a 0 por CODCLI y otras 289 por RUT/DV, sin solapamiento: 737 personas en la preparación. De ellas, 734 aparecen en los envíos efectivos; 729 solo con VIG 0 y cinco con alguna VIG 1 posterior. Tres no están en las copias enviadas. No son 737 errores demostrados.

**D/E:** El control interno designó estas matrículas como VIG 0. La razón académica individual para integrar las nóminas no está en los documentos revisados. No se puede sustituir una decisión documentada por el estado VIGENTE actual ni atribuirla a TITULADO sin evidencia.

## Cadena de evidencia del envío

**B/C:** Se verificó SHA-256 de ambas copias `_orig.zip` devueltas por PES contra el manifiesto Gate09. El CSV PARA_SUBIR y PES_READY del 8 de mayo son idénticos por contenido normalizado de las 32 columnas al `_orig` de 4.070 filas. La hoja SUBIDAS_REALIZADAS_4165 del cierre es idéntica, como multiconjunto de filas, a la concatenación de ambas copias. Se conserva la distinción entre envío y aceptación final de cada estudiante: estos bytes acreditan lo enviado, no validación normativa individual.

| Envío | Filas | VIG 1 | VIG 0 | VIG 2 | Clase |
|---|---:|---:|---:|---:|---|
| 08-05-2026_23-21-16_Matrícula-Pregrado-2026.csv_orig.zip | 4070 | 3110 | 960 | 0 | B |
| 11-05-2026_12-12-47_Matrícula-Pregrado-2026.csv_orig.zip | 95 | 95 | 0 | 0 | B |

## Reglas realmente trazadas

| Control | Registros en nómina | Cambiados 1→0 | Ya eran 0 | No encontrados | Clase |
|---|---:|---:|---:|---:|---|
| CODCLI, año 2026, período 1 | 494 | 448 | 46 | 0 | B/C/D |
| Nómina manual RUT/DV | 754 | 289 | 463 | 2 | B/C/D |

**B/C:** Historial Git `77bdc686ca66fabfe9ef8e6402027aa989b49e5a`: `control/vigencia_0_codcli_mu2026.tsv` tiene exactamente los mismos 494 CODCLI que la auditoría de ejecución; no se exportaron identificadores. La función `_aplicar_control_vigencia_0_codcli` asigna VIG 0 a esa lista. El mismo código incorpora `src/forzar_vig_cero.py` y `patches/mu2026/vig0_nomina_institucional.tsv` antes de exportar PES_READY. El TSV de la nómina por RUT no está en ese commit; su aplicación se acredita con la auditoría y el reporte anexos al envío.

**B/E:** La columna MOTIVO del control CODCLI solo contiene `CONTROL_VIGENCIA_0_CODCLI`; las 752 observaciones de personas encontradas en la auditoría por RUT están vacías. Esto permite probar la transformación, pero no el fundamento individual. El código describe una regla institucional para matrículas consideradas sin matrícula: clasificación C/D, no definición oficial de equivalencia por estado.

## Incidencia en retención, sin corregir nada

| Población | Denominador conservado | Continúan/retenidos actuales | Tasa actual | Personas de las nóminas con cambio 1→0 dentro de la población | Clase |
|---|---:|---:|---:|---:|---|
| Seguimiento 2025-T2 | 222 | 74 | 33,33% | 2 | B/C/D |
| Seguimiento 2025-T3 | 124 | 48 | 38,71% | 2 | B/C/D |
| Retención anual cohorte 2025 | 1.150 | 668 | 58,09% | 291 | B/C |

**B/C:** Las dos personas T2 provienen de la nómina RUT; las dos T3 del control CODCLI. Las tasas T2/T3 coinciden exactamente usando los envíos de mayo o la base consolidada de julio; sus ausentes siguen siendo 142 y 74. Las dos T3 aparecen VIGENTE en la instantánea UMAS de mayo, pero VIG 0 en el envío: la nómina explica técnicamente el cambio, no su justificación académica.

**B/C:** De las 291 personas de las nóminas incluidas en la cohorte anual 2025, 288 corresponden a la regla por RUT y tres a CODCLI; todas están actualmente como no retenidas. Para 276 existe matrícula 2026 con la misma cohorte de origen, pero con VIG 0. Para las otras 15, cambiar solo VIG no garantiza continuidad con la misma cohorte. Los grupos anual/T2/T3 pueden solaparse; no se suman.

**E:** No se calcula una nueva tasa validada: que VIG fuera 1 antes del control no demuestra que ese 1 fuese correcto. Revertir 1→0 exigiría justificar cada matrícula al corte; esta auditoría no lo autoriza. No se modificaron fórmulas, bases, numeradores publicados ni denominadores.

## TITULADO y el antecedente de 234 filas

**B:** Los envíos efectivos revisados tienen cero VIG 2. En ellos hay 104 filas de 101 personas con algún registro TITULADO en la instantánea U+; 99 filas VIG 1 y cinco VIG 0. No hay personas enviadas con registros U+ exclusivamente TITULADO.

**B/E:** Solo una de las 737 personas cambiadas por nómina tiene algún antecedente TITULADO en U+; eso no demuestra que la causa del cambio fuera titularse. No se acredita que las 234 filas de la ficha antigua llegaran como VIG 2 a estas cargas. No corresponde tratarlas como 234 errores efectivos ni convertir el estado de una matrícula en regla para todas las matrículas de la persona.

## Fuentes históricas y diferencias de versión

**B/C:** Se comparó VIG fila por fila entre cada fuente seleccionada 2022–2026 y BASE_RETENCION_MU: cero diferencias, incluidos alias VIGENCIA→VIG y normalización declarada. La hoja RAW del diagnóstico anual coincide con la base gobernada. La consolidación no aplicó un nuevo estado→VIG.

**B/C:** Los envíos suman 4.165 filas; la base de julio tiene 4.105. Ambos abarcan las mismas 4.071 personas. En 4.018 claves comunes unívocas no hay diferencias de VIG; otras claves requieren considerar duplicación o cambios de campos. Cinco personas tienen alguna VIG 1 en mayo y solo VIG 0 en julio: son de cohorte origen 2026/1, ninguna de las poblaciones de retención aquí evaluadas. No se sustituyeron versiones.

**C:** Las fórmulas del diagnóstico anual no tienen resultados en caché. Para verificar pertenencia e impacto se reprodujo su lógica en memoria con el mismo RAW y catálogo, sin guardar ni recalcular el XLSX. Se reprodujeron exactamente los cuatro controles:

| Cohorte | Denominador | Retenidos | Tasa | Clase |
|---|---:|---:|---:|---|
| 2022 | 305 | 224 | 73.44% | C |
| 2023 | 366 | 258 | 70.49% | C |
| 2024 | 558 | 326 | 58.42% | C |
| 2025 | 1150 | 668 | 58.09% | C |

**E:** Los controles específicos de 2026 no pueden explicar por sí mismos las brechas de retención 2022 y 2024, que observan continuidad en 2023 y 2025. Para esas fuentes se probó preservación de VIG, pero no se dispone aquí de una auditoría equivalente de asignación histórica por matrícula que permita atribuir errores a TITULADO.

## Discrepancias observadas que no se presentan como errores

**B/C:** En los 3.175 cruces con una sola fila U+ de matrícula 2026 por persona se observan 78 ELIMINADO→VIG0, dos SUSPENDIDO→VIG0, 442 VIGENTE→VIG0 y 2.653 VIGENTE→VIG1. La coincidencia por persona/año no certifica la condición académica al 30 de abril ni reemplaza la llave de programa. Las 442 incluyen cuatro personas de la cohorte anual elegible 2025. No sumar este grupo a las nóminas: son cortes de la misma población que pueden solaparse.

## Pendiente concreto

**E:** Falta el fundamento académico y temporal que originó cada nómina (matrícula/renovación y cambios de estado al corte, o acto institucional que justifique la selección). Las fuentes prueban quiénes fueron cambiados y qué se envió; no prueban qué asignaciones deben corregirse. Mantener las bases, denominadores y tasas hasta resolverlo.

## Validaciones y archivos

**C:** QA técnica OK: hashes esperados, cadenas archivo preparado→PES, control Git de 494 coincidencias, ausencia de solapamiento entre las 448 y 289 modificaciones, balance 737=729+5+3, reproducción de retención anual e integridad de fuentes al cierre. La causalidad académica sigue E.

**D/C:** Solo se generan este reporte, resultados agregados, script de auditoría de lectura y manifiesto. No se guardan identificadores individuales, nombres ni fechas de nacimiento. Sin commit/push. Rama feature/ire-2026, HEAD antes/después b8140dcba0f179865671cff75f98b9e1041eeb0a.

## Fuentes verificadas: ruta y SHA-256

**B:** Cada huella corresponde a bytes leídos en esta ejecución. Los hashes esperados provienen del manifiesto Gate09 o de los manifiestos de consolidación y continuidad. Las fuentes adicionales conservan hash calculado sin atribuirles una verificación anterior inexistente.

- `/Users/alexi/Documents/GitHub/avance_curricular/.local_restricted/requerimiento_bettersoft_uplus_2026/gate09_evidencia/matricula_unificada_2026/08-05-2026_23-21-16_Matrícula-Pregrado-2026.csv_orig.zip` — SHA-256 `5368eb33a0431deebea50b382a5f187249f3fb437e67f533fed05bf202c3b9ef`.

- `/Users/alexi/Documents/GitHub/avance_curricular/.local_restricted/requerimiento_bettersoft_uplus_2026/gate09_evidencia/matricula_unificada_2026/11-05-2026_12-12-47_Matrícula-Pregrado-2026.csv_orig.zip` — SHA-256 `18731c93e288ad5feb4357579a015f87eba4180a06eb9d85bda27d0323fa29b4`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/QUINTA SUBIDA +95/PROMEDIOSDEALUMNOS_7804.xlsx` — SHA-256 `1e383ea54a679aff32bffc9f4673fee3162784ba3dce80ac2c0cb09dee188ce6`.

- `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx` — SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.

- `/Users/alexi/Downloads/cierre/Matrícula T2_2025 2.xlsx` — SHA-256 `ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3`.

- `/Users/alexi/Downloads/cierre/Matrícula T3_2025 2.xlsx` — SHA-256 `68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2022/2022.csv` — SHA-256 `08ee0b7973f4a2705b388c73413f2ce5402b849f8c3c09c3843d5c2f8c060a4f`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2023/2023.csv` — SHA-256 `cf13147baa2d0a10ad021e867362b593a95337259889b18b483d8710a4b90e35`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2024/08-05-2024_18-31-54_Matrícula_Pregrado_2024.csv` — SHA-256 `5cd5c664b303301bc4e1c5f910c708c1d68e78465eebe3002364a07ea8e4a068`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx` — SHA-256 `9ceb4f3e15111a4d968410fcb799d56bd349a6e91a9d473d5a9cceedaab15062`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/REPORTE JULIO 2026/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx` — SHA-256 `fab3f4c3ba10534e0ec1d8eea4249a5bbbdc03cc012534b3184f59d9d3d663d7`.

- `/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx` — SHA-256 `5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/procesamiento código/auditoria_ruts_forzados_vigencia_0.csv` — SHA-256 `a6eb8d0aac58e5016f1e633fdf4ed9e76b53f2d70ccd3f3e74ce8e09b97818fc`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/procesamiento código/auditoria_vigencia_0_codcli_mu2026_20260508_230520.csv` — SHA-256 `ec8d7ca55d82cbb50fac210d0cccf1e0ba44a1bf8965ff5fe2a8e20642be1458`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/procesamiento código/auditoria_correcciones_pes_ready_20260508_230900.csv` — SHA-256 `783113916d2b2a9d73e19e2e10f06ede3c2b1423cb61415b092d2d78d61e41d5`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/matricula_unificada_2026_pregrado_PARA_SUBIR.csv` — SHA-256 `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/procesamiento código/matricula_unificada_2026_pregrado_PES_READY.csv` — SHA-256 `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/MU2026_CIERRE_AUDITORIA_SUBIDAS_REALIZADAS_4165_TRAZABILIDAD.xlsx` — SHA-256 `8b05e58189f79247fd0684327c3cc3afac9e65a91c45d964d7498a434935fea4`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/procesamiento código/reporte_matricula.json` — SHA-256 `c5e8498430061cac95b9adf6bb6fa4710acfe8c39fdba5015627584a9e672924`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/procesamiento código/resumen_pes_ready_20260508_230900.md` — SHA-256 `78e9bee5d119bc6e0cdf40d9eb9c0e551f9db87b466a14da609d8af9a497db13`.

- `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/CUARTA SUBIDA FINAL/KPI_Matricula_Unificada_2026.xlsx` — SHA-256 `cd0472766514a7ef945cba043961ca1496d4d0bc68db34e9b21abb55f8ca790a`.

- **B/C:** Blob Git `77bdc686ca66fabfe9ef8e6402027aa989b49e5a:control/vigencia_0_codcli_mu2026.tsv` — SHA-256 `fb2b13d8d4d0c64cd0428e92747d43eb8bc832dbf1993997baa5d7fc3175399d`.