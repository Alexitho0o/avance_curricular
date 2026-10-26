# Fase 2/6 — Códigos individuales y conciliación anual

**B/C — Ejecutada:** 2026-10-25T15:40:29.280280-03:00. IPSS 162, matrícula seleccionada 2022–2026; rama feature/ire-2026, HEAD `8e2fb85bb8703758d6878681c9e2a29016e60c63`.
**D — Alcance autorizado:** reutilizar códigos individuales y conciliar por año+código completo; revisar diferencias. Bases, diccionario, Excel, tasas y denominadores se conservan. Sin commit ni push.

## Resultado ejecutivo

**B/C:** se revisaron las 10.200 matrículas de la base seleccionada. Identidad, sede, carrera, jornada, versión y vigencia coinciden con sus fuentes primarias, en orden y como multiconjunto. La versión procede de cada registro individual; no se asignó distribuyendo los totales del CSV.
**C:** código = I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}; llave de conciliación = año informado + código completo. Se conserva la separación entre matrícula, personas únicas, primer año publicado y cohortes elegibles para retención.

| Año | CSV SIES Pregrado | MU todas las filas | MU VIG=1 | Δ CSV−VIG1 | Códigos pregrado con Δ | Clase |
|---|---:|---:|---:|---:|---:|---|
| 2022 | 1.033 | 1.038 | 1.033 | +0 | 0 | B/C |
| 2023 | 1.142 | 1.145 | 1.142 | +0 | 2 | B/C |
| 2024 | 1.455 | 1.541 | 1.455 | +0 | 0 | B/C |
| 2025 | 2.371 | 2.371 | 2.298 | +73 | 11 | B/C |
| 2026 | 3.371 | 4.105 | 3.145 | +226 | 48 | B/C |

**C — Comparación uniforme:** la tabla mantiene VIG=1 en todos los años; no cambia de filtro para igualar cifras. MU todas incluye los seis códigos/año sin fila en el CSV (dos matrículas 2022 y seis 2024, todas VIG0); su nivel no se infiere del CSV. VIG=2 y otros valores suman cero en estas fuentes: por eso VIG=1 y VIG∈{1,2} coinciden numéricamente aquí, sin convertirlos en una regla universal.
**B/C — Alcance separado:** Postítulo publicado suma 19 en 2023, 13 en 2024, 151 en 2025 y 54 en 2026. Está visible en el detalle, fuera de la base seleccionada de Pregrado. Ausente no se reemplaza por cero fuente: solo las columnas de unión usan un cero estructural explícito.

## Diferencias revisadas

- **B/C, 2022 y 2024:** los 26 y 27 códigos publicados de Pregrado coinciden exactamente con VIG1. Las diferencias frente a todas las filas son 5 y 86 VIG0, respectivamente. Los seis códigos/año exclusivos de MU tienen cero VIG1. Esto no demuestra una reasignación de versiones ni una aceptación individual por SIES.
- **B/C, 2023:** `I162S2C46J1V1` tiene publicación 6 y MU VIG1 7; `I162S2C46J4V3`, publicación 173 y MU VIG1 172. Diferencias −1/+1, neto cero. **E:** falta el antecedente que identifique por qué difieren estos códigos; la compensación no prueba un traslado de una persona.
- **B/C, 2025:** los 43 códigos de Pregrado coinciden contra MU total. Frente a VIG1 hay +73 en 11 códigos de ocho carreras. **E:** la igualdad con 73 VIG0 no prueba que la publicación incluyera esas mismas identidades ni explica el criterio aplicado. Se conserva el filtro actual de retención.
- **B/C, 2026:** la brecha Pregrado sigue en +226, distribuida en 48 códigos (+228/−2); incluye dos códigos solo en CSV: `I162S2C77J1V1` con 1 e `I162S2C87J4V1` con 5. C6 y C79 tienen diferencias +1/−1 compensadas por carrera. **E:** no se acredita con estos agregados la causa individual ni una regla nueva para asignar versiones.
- **B/C, cotejo del cierre de julio:** 66/66 totales publicados y 63/63 comparadores institucionales de Pregrado coinciden por código. Publicación 3.425 = 3.371 Pregrado + 54 Postítulo; institucional comparable 3.199 = 3.145 + 54. Por tanto 226 es la brecha ya conocida. Los 280 al comparar todo el CSV contra esta base Pregrado son 226 + 54 de distinto alcance; no se añade una nueva brecha de 54.
- **B/E, documentación histórica:** se reproducen 990/990 números del puente previo. Su afirmación de que igualar totales por carrera explica una reclasificación jornada/versión excede esa evidencia. Se documenta aquí el límite y se conservan los archivos anteriores intactos.

## Linaje de las fuentes individuales

**B/C:** `QA_LINEAJE_MU.json` conserva ruta, hoja, hash y rango de filas por año. No exporta identificadores. En cada año las filas aparecen en el mismo orden y sin pérdidas: fila primaria = fila BASE − primera fila BASE del año + 2. El auditor comprueba también los multiconjuntos de claves y valores.
| Año | Filas | Filas BASE | Filas fuente | Clase |
|---|---:|---|---|---|
| 2022 | 1038 | [2, 1039] | [2, 1039] | B/C |
| 2023 | 1145 | [1040, 2184] | [2, 1146] | B/C |
| 2024 | 1541 | [2185, 3725] | [2, 1542] | B/C |
| 2025 | 2371 | [3726, 6096] | [2, 2372] | B/C |
| 2026 | 4105 | [6097, 10201] | [2, 4106] | B/C |

**C:** en 2025 se reproduce la transformación existente VIGENCIA ‘Vigente’→1 y ‘No vigente’→0: 2.298 y 73. La primera comprobación textual detectó esa diferencia de representación; la prueba corregida por la transformación documentada pasa sin cambios en los datos.
**E:** el CSV público no contiene RUT ni CODCLI; no permite comparar conjuntos de personas con la publicación. La atribución UMAS por expediente y el estado de aceptación no se certifican mediante este control agregado. Se conservan el diccionario v8 y los resultados de la Fase 1; no se vuelven a adjudicar casos cerrados.

## Archivos, QA y reanudación

- **C:** `conciliacion/DETALLE_CONCILIACION.csv`: 198 combinaciones año+código, totales, vigencias, personas distintas, presencias y localizadores.
- **C:** `conciliacion/SOLO_DIFERENCIAS.csv`: 118 filas con diferencia en al menos un comparador o presencia exclusiva; no equivale a 118 códigos de versión pendientes ni a 118 personas.
- **C:** `RESUMEN_EJECUTIVO.csv`: cinco filas con lectura ejecutiva; `brechas2022_2025/` y `brechas2026/`: detalle y evidencia de las excepciones.
- **C:** `QA_FASE2.json` y `MANIFEST_FASE2.json`: controles, rutas, hashes, scripts y preservación. No se creó otro Excel ni se recalculó el libro existente.
**B/C — QA:** linaje de 10.200 filas correcto en los ocho campos; 990/990 valores contra puente anterior; cero duplicados de identidad dentro de un mismo año+código. Una persona puede tener varios códigos, por lo que los totales anuales de matrícula no se sustituyen por personas únicas. Los 13 archivos protegidos conservan hash, incluido el cambio previo de PROYECTO_IPSS.json; también se verificaron los hashes del CSV SIES y del puente anterior. No hubo commit/push; HEAD permanece igual.
**E — Estado:** conciliación pedida ejecutada y técnicamente validada, con causas aún abiertas. No equivale a 100% de atribución UMAS↔SIES ni al cierre de las brechas. Para la siguiente fase, reutilizar el ancla individual preservada y el diccionario actual; revisar solo cambios de carrera/sede/jornada/plan T2/T3. No reasignar versiones para anular las diferencias ni reabrir la búsqueda completa por nombre.

## Fuentes y hashes

- **B:** `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx` — SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
- **B:** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/MATRÍCULA/Matricula_2007_2026_WEB_10_07_2026.csv` — SHA-256 `4c630e05e07312ebd567ed77b0c26c5d0230380deea4fc89a6123b11b7aba154`.
- **B:** `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv` — SHA-256 `d4f3675d5d63247b0118412f983729cb18924c2971cea1b7d0ef731e6c8e7803`.
- **B:** `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json` — SHA-256 `c205fed8061bc02ea2623eea8d789ffc1bc1355e41f82bb1298d319bd76b08ad`.

**B/C:** hashes de las cinco fuentes primarias, del libro y del diccionario en QA_LINEAJE_MU.json y QA_FASE2.json. Los roles de las fuentes se conservan: institucional granular seleccionada, derivado, publicación agregada y auditoría. Ninguno se transforma en prueba de aceptación SIES por su nombre de archivo.
