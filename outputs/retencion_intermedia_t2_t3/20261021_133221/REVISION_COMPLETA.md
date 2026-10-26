Fase 4/4 · Hito 3/3

# Entrega de revisión de retención intermedia IPSS 162

Dictamen: **QA técnico aprobado con pendientes E**. Los cuatro cierres siguen sin tasa acreditada. Fecha de entrega: 2026-10-21T14:26:43.113181-03:00.

## 1. Excel y copia idéntica

- Libro: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_133221/RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx`
- Escritorio: `/Users/alexi/Desktop/RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx`
- SHA-256 de ambas copias: `66e7cc11a0206793504e4eb275d8585e070413067df6f20b9fde234d3daaa54c`.

## 2. Cuatro cierres

| Cohorte | Cierre | Denominador fijo | Presencias en listado B/C | VIGENTE observado B | Vigentes acreditados al cierre | Tasa | Fuente/hoja |
|---|---|---:|---:|---|---|---|---|
| 2024 | 2025-T2 | 558 | 1 | 1 | Pendiente E | Pendiente E | Matrícula T2_2025 2.xlsx / T2_2025 |
| 2024 | 2025-T3 | 558 | 325 | 317 | Pendiente E | Pendiente E | Matrícula T3_2025 2.xlsx / T3_2025 |
| 2025 | 2026-T2 | 1.150 | 2 | Sin campo | Pendiente E | Pendiente E | Matrícula T_2_13_07_2026.xlsx / Hoja1 |
| 2025 | 2026-T3 | 1.150 | 0 | 0 en listado | Pendiente E | Pendiente E | Matrícula_T3_02_10_2026.xlsx / Base |

325 personas tienen 328 matrículas en T3-2025; se conservaron todas. Los respaldos 10246/11998 contienen 1.148 personas de la cohorte 2025, verificadas sin doble conteo. Ese dato describe fotografías de varios años/períodos; no reemplaza las presencias de los listados ni acredita retención al cierre.

## 3. Veinte personas y seguimiento de catorce

18 identificadas, 2 pendientes; 19 CODCLI (17 personas con uno y una con dos). Todas ya integraban 1.150. Una persona se recupera por CODCLI pese al cambio documental. Las 18 no figuran en los dos listados parciales 2026. No se acreditó deserción.

Entre las mismas 14 personas, 10246 tiene 13 con alguna VIGENTE; 11998 y 12112 tienen 14. Cada fuente conserva 15 matrículas sin colisiones de llave completa en ese grupo. Julio→octubre mantiene 14 llaves: 13 VIGENTE y una ELIMINADO; la otra persona pasa de una llave 2025-P1 a otra 2026-P3, sin inferir una transición de la misma matrícula.

La búsqueda revisó 64 fuentes adicionales por hash: 58 Base Maestra, 12135, 11248 y cuatro históricos sin esquema comparable. No recuperó los dos CODCLI pendientes (Informática y Programación). Los 58 respaldos muestran 13 de las 14 con alguna VIGENTE hasta el nominal 08-09 y 14 desde 09-09, incluido 02-10. Son fechas nominales, no fechas efectivas del evento o cierre.

12112 fue relocalizado en OneDrive/0_caracterizacion/2026-10-20/2027_P1_082351/01_ENTRADAS; su hash coincide con el gobernado. La antigua ruta del Escritorio ya no está disponible.

## 4. Cambios y distinción conceptual

Se actualizaron las llaves pendientes de 20 a 2 y los conteos derivados de no localizados con llave (1.146 en T2-2026 y 1.148 en T3-2026). Presencias, estados observados y denominadores no cambian. Se añadió Revision_agregada, se precisaron pendientes/fuentes y se conservaron formatos, tablas, filtros, fórmulas, validaciones y el escenario hipotético de 80 casos separado.

La retención interna documentada considera matrícula IPSS t+1 aunque cambie carrera. SIES conserva su propia cohorte, reglas y referencia anual. La auditoría halló una excepción parcial en Caracterización: TITULADO en base se excluye del seguimiento opcional; VIGENTE en base y TITULADO/EGRESADO en destino produce NO_RETENIDO sin fecha de título. Ese resultado técnico no acredita deserción. El componente no se aplica a estos denominadores.

Duración formal de oferta/plan, nivel curricular, avance real, egreso y título son conceptos distintos. No se infirió titulación por duración cumplida. La propuesta E separa culminación acreditada de continuidad/deserción; su efecto en el denominador requiere contrato, fechas y decisión explícita. No se creó una categoría “no recurrido”.

## 5. Pendientes exactos

- 2025-T2: matrícula completa de cohorte 2024 y renovaciones, fecha efectiva y estados del cierre; el listado solo contiene ingresos 2025-T2.
- 2025-T3: acreditación de exhaustividad y fecha efectiva de estados de T3_2025.
- 2026-T2: población completa de cohorte 2025, estados y fecha efectiva. Hoja1 carece de estado; congelamiento de 10246 no acredita corte.
- 2026-T3: cubrir períodos de ingreso 1 y 2, fijar hoja autorizada y fecha efectiva; resolver dos discrepancias Base/2026_3. 11998 no acredita cierre por su ejecución de octubre.
- Todos: regla intermedia propia con población, exclusiones y numerador; historial de matrícula/estado y titulación fechados. No homologar T1/T2/T3 a semestres SIES.
- Identidad: correspondencia institucional explícita para los dos CODCLI pendientes, sin cruce aproximado ni exclusión.
- Regla interna de titulación: definir antes/durante/después del corte, otra carrera, rematrícula, múltiples matrículas y egreso sin título. Decidir cohorte fija o población aún expuesta antes de cualquier tasa ajustada.

## 6. QA y Git

Recálculo con Artifact Tool, pruebas de sensibilidad (cierre sin numerador / numerador sin cierre / selector de carrera), controles independientes, revisión visual e importación del XLSX final. Cero errores de fórmula. Preservación de estilos efectivos, tablas, filtros, validaciones y hojas originales fuera de las celdas autorizadas. Escenario_80 byte idéntico. Solo agregados; sin nóminas, identificadores de alumnos, macros ni vínculos externos.

No se abrió Microsoft Excel: el comportamiento nativo y su configuración regional no se certifican. Las pruebas de reglas incluyeron una prueba existente aislada y cinco casos sintéticos; la suite completa no pudo importarse por unidecode ausente, sin cambiar el entorno.

Rama antes/después: `feature/ire-2026`. HEAD antes/después: `80ca13a5a249a1a2bd53a699f5f73689b1f53040`. Original Excel: SHA-256 `12bf04615558554a30275b4ee8c6197617e7195c059c4c87277a91c4697e719d`. Base anual: `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. Los demás hashes y el control final de fuentes se registran en MANIFEST_REVISION.json.

## 7. Conservación

Fuentes y motor anual intactos. Denominadores 558, 1.150, 222 y 124 conservados. Seguimiento anual separado: 74/222 = 33,33% y 48/124 = 38,71%. Sin cambio de rama, commit, push, merge ni PR. Los cambios previos del checkout no fueron alterados. La entrega es local; no se declara publicada en GitHub.

La bitácora registra doce hitos y distingue revisión ejecutada de acreditación pendiente. PROMPT_ACTUALIZADO_RETENCION.md conserva el prompt original e incorpora las ampliaciones del usuario.

## Adjuntos adicionales autorizados después del cierre local

Fase 4/4 · Hito 3/3. El usuario autorizó posteriormente subir únicamente el Excel agregado y el prompt actualizado a su Library. Creación y lectura posterior confirmadas:

- RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx: libfile_b688ed6a1c24819184aec5f2289cc490.
- PROMPT_ACTUALIZADO_RETENCION.md: libfile_df20350f86dc81918428e96009316a95.

Las copias locales se conservan; no se transfirieron bases ni identificadores individuales. Esta entrega adicional no cambia Git ni resuelve pendientes metodológicos. Comprobante: COMPROBANTE_LIBRARY.json.
