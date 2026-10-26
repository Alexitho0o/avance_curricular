# Procedencia de versiones: C3/J4 2021–2022 y E04

**Resultado B/C:** los cambios de versión están reproducidos en los respaldos originales. **Resultado E:** no se localizó la consulta, fórmula o decisión que los generó. El punto de origen observable quedó acotado al lote de matrícula 2022 y a la precarga MU2025, respectivamente. No se adoptó ninguna equivalencia nueva.

## Alcance y separación

- **D:** solicitud de investigar 50 personas C3/J4 y E04, conservando bases, denominadores, diccionario y libro de retención. Sin commit, push ni consultas mutantes.
- **B:** proceso Matrícula Unificada; años de datos 2021–2022 y 2024–2026; ejecución 23-oct-2026. Repositorio principal `avance_curricular`, rama `feature/ire-2026`. No se está reconstruyendo una tasa ni el motor anual.
- **C:** identidad exacta normalizada; contexto de carrera/sede/jornada por año; fórmulas y valores literales inspeccionados separadamente. No se cruzó por nombre y no se atribuyó una asignación individual desde totales agregados.
- **E:** un código observado en MU acredita el valor allí registrado; no explica por sí solo por qué se seleccionó ni prueba la fecha efectiva de un cambio de plan. No se halló una nueva regla oficial A aplicable a la asignación investigada.

## 1. C3/J4: los 50 cambios

| Hallazgo | Conteo | Clase | Evidencia |
|---|---:|---|---|
| V1 en 2021 y V2 en 2022, mismo contexto atribuido IETMREOL20211/J4 en diccionario | 50 personas; 50 CODCLI | B/C | c3j4/PRIMARY.json: seis fuentes, hojas, filas y hashes |
| VERSION/código único escritos como valores; ninguna fórmula en las celdas revisadas | 50 por cada fuente | B | PRIMARY.json; CONTRASTE_INDEPENDIENTE.json |
| FECH_CAR de los 50 cambios | 06/05/2022 16:14 | B | RAW 2022.csv; PRIMARY.json |
| Cambia también el año de origen desde un año anterior a 2021 hacia 2021 | 11 de los 50 | B | c3j4/PATRONES.json; no se atribuye causalidad |

**B/C — Control de contexto, no ampliación del denominador:** entre las 75 personas presentes en la familia C3/J4 en ambos años hay 58 V1→V2 (incluyen las 50), 15 V2→V2 y 2 V1→V1. Las 58 cambiadas y las 15 que ya tenían V2 pertenecen al lote 16:14; las dos que conservan V1, al lote 00:11 del mismo día. En la familia completa RAW2022 hay tres filas V1 del lote 00:11 y 155 V2: 153 del lote 16:14 y dos del lote 16:38.

**B — Las variables académicas contrastadas no explican por sí solas la separación:** las dos personas que conservan V1 comparten con las 50 foco ingreso actual 2021-1, modalidad 3, FOR_ING_ACT=1, VIG=1, perfil regular de ocho semestres y contexto IETMREOL20211 en el diccionario. Los informes primarios no conservan CODCLI/PLAN_DE_ESTUDIO; este contexto del diccionario no demuestra automáticamente el plan efectivo en la fecha histórica.

**C — La consolidación no asignó estas versiones:** `scripts/construir_base_retencion_mu_2022_2026.py`, líneas 227–265, lee la fuente, mapea la columna y copia el valor mediante `typed_value`. VERSION ya era V2 en RAW2022. Se verificaron 50/50 en las seis fuentes sin colapso de múltiples códigos: 75 personas comunes tienen una fila/código por familia en cada año. RAW2022 declara TIPO_DOC=R; MAT2021 no contiene ese campo y se usó MM_N_DOCUMENTO+MM_DV, sin inventarlo.

**E — Pendiente exacto:** falta el extracto de preparación anterior al lote 06/05/2022 16:14, su consulta/script o un registro de decisión que explique el cambio a V2 y la conservación de V1 en el lote 00:11. FECH_CAR separa los lotes observados, pero no demuestra migración, corrección ni error. No corresponde convertir esa fecha en una regla de asignación.

## 2. E04: V2→V1→V2

**B — La secuencia documentada permanece:** I162S2C1J1V2 en 2024, I162S2C1J1V1 en 2025 e I162S2C1J1V2 en 2026. E04 se identificó de forma independiente y no es INF35-03.

| Punto observado en respaldo MU2025 | Valor | Clase |
|---|---:|---|
| IPSS_Procesamiento.xlsx · Precarga!Q1025 | V1 literal | B |
| Mismo libro · Carga_Completa!Q1027; Carga_Completa (2)/(3)!Q1032; Final a carga!Q1004 | V1 literal | B |
| IPSS2025.xlsx · O1004; descarga de lo cargado · Q1020; RAW2025 · AA867 | V1 literal | B |
| FECH_CAR de E04 en la precarga | 16-abr-2025 11:50:07 | B |

**B/C:** 17 libros de preparación, 32 filas coincidentes y 10 celdas VERSION=1, todas literales. Incluyen copias: no son 32 evidencias independientes ni demuestran el orden de edición entre hojas. No hay fórmula de VERSION ni conexiones/queryTables/VBA en el libro de preparación que expliquen esa asignación. El incremental denominado 02-01-2025 no contiene a E04; el RAW2024 de esa carpeta sí contiene V2.

**B — Control de contexto:** Precarga C1/J1/S2 contiene 22 filas: 14 V2 y ocho V1. Las ocho V1 tienen FECH_CAR del 16 de abril de 2025; también hay una V2 de ese día. De las ocho personas con código de la misma familia en RAW2024, siete mantienen V2 y E04 pasa a V1. Ni el día de carga ni la sola familia bastan para justificar V1.

**E — Pendiente exacto:** la asignación V1 ya venía incorporada en `Precarga!Q1025`. Falta la consulta, transformación o decisión previa a esa precarga/lote. FECH_CAR no acredita cuándo cambió el plan ni quién decidió la versión. Se conserva la secuencia anual observada; no se fuerza una V2 retrospectiva.

## 3. Scripts e historial local

**C:** se inventariaron las referencias Git locales de avance_curricular, CARACTERIZACIÓN e IPSS_Procesos_SIES, sin fetch. Se inspeccionaron estáticamente 756, 2.590 y 143 blobs de extensiones de código, respectivamente (incluyen dependencias); 67 contienen expresiones candidatas. Las coincidencias de texto son una búsqueda, no 67 reglas validadas. `BUSQUEDA_IMPLEMENTACIONES.json` conserva objetos Git, rutas, hashes y líneas. De 150 rutas de código del inventario OneDrive previo, se releyeron seis ajenas a FCU2026; 144 respaldos FCU2026 se conservaron como inventariados fuera de alcance, no como revisados para MU2022/2025.

**C — Implementación encontrada, alcance distinto:** `codigo_gobernanza_v2.py`, líneas 3763–3781, primero extrae VERSION del código final; si falta y hay COD_CAR+JOR, usa la versión máxima del catálogo por esos campos. El propio generador referencia MU/oferta 2026. Su aparición en Git figura en commits d0dc2ebd y 5ddb6868. Esto no acredita ejecución sobre los archivos de 2022 o 2025 ni explica esos lotes. No se ejecutó ni alteró ese motor.

**C:** los blobs históricos `scripts/auditar_logica_versiones_sies_mu.py` (7e6f54e2), `scripts/reconstruir_rectificacion_mu2026_desde_cero.py` (053d4935) y `scripts/sies_resolver.py` (2ad3ccf1) son auditoría, rectificación MU2026 y validación/parseo de códigos. No se localizó en ellos una instrucción que produjera el lote2022 o la precarga2025 del foco. Las copias y las fechas de los archivos tampoco prueban autoría o ejecución.

**E:** no localizar el generador en esta cobertura no equivale a afirmar que nunca existió. No se ha demostrado una regla universal basada en ingreso, plan, lote o versión máxima.

## 4. Resultado operativo

**D:** no aplicar cierres ni cambios de código con esta investigación. Los códigos por año ya estaban documentados; ahora se conoce mejor el tramo donde se pierde la explicación de su asignación. Las dos preguntas causales siguen E.

**B/C:** QA de cardinalidad, relectura de celdas, hashes, privacidad y Git en `QA.json`; evidencia original con rutas/hojas/filas/hashes en los manifiestos de cada subcarpeta y `MANIFEST.json`. Se mantienen Excel, diccionario, bases y denominadores. Ningún dato individual se publica ni incorpora a estos resultados agregados. No se hizo commit ni push.

**E — Reanudación precisa:** buscar el insumo/consulta anterior al CSV2022 del lote16:14 y el insumo/consulta anterior a Precarga2025 con FECH_CAR16-abr. No volver a probar reglas por mayoría o por año sobre estos casos, ni presentar coincidencia de lotes como explicación causal.
