# Trazabilidad integral UMAS → SIES → seguimiento y Excel

**C — Versión:** 1, 25-10-2026. Plan posterior al cierre de publicación del diccionario v8; no sustituye ni altera la evidencia de las cuatro fases anteriores.

**D — Encargo:** analizar la debilidad señalada por Alexi y planificar una cadena verificable por persona, expediente, carrera, jornada, plan, nivel, versión y período. Esta entrega solo diagnostica y planifica: no cambia fuentes, diccionario, Excel, tasas ni denominadores; no autoriza otro commit, push ni actualización remota.

**B — Contexto técnico comprobado:** avance_curricular, feature/ire-2026, HEAD 8e2fb85bb8703758d6878681c9e2a29016e60c63. Caracterización se consume desde el módulo integrado. Proceso: trazabilidad de matrícula y retención interna T1/T2/T3 hasta 2026; matrícula, oferta, avance y titulaciones se conservan como procesos distintos. El histórico de actividad del diccionario revisado abarca 2019–2026; no acredita cobertura individual integral 2007–2027.

## 1. Diagnóstico comprobado y límites

| Clase | Hallazgo | Evidencia local | Consecuencia para el plan |
|---|---|---|---|
| B/C | El diccionario sí contiene el código completo. MU2022–2026 aporta COD_SED, COD_CAR, JOR y VERSION; el constructor compone I162S…C…J…V…. Los históricos2019–2021 leen MC_CODIGO_UNICO. | scripts/construir_diccionario_sies_seguimiento.py:99; scripts/reproducir_puente_20261023.py:134 | Reutilizar componentes y códigos documentados; no reconstruir versiones por nombre o por ordinal. |
| B/C/E | v8 tiene tablas observaciones y mu_anual, pero no una vista integral que conecte UMAS, fila de envío, retorno SIES, oferta y seguimiento. Su universo de observaciones procede de PROMEDIOS, no del padrón completo T1. | Constructor:66; reproducción:107–113; SQLite activa referenciada por el descriptor | Partir de toda la población T1 aprobada, incluyendo personas sin actividad, y enlazar el diccionario existente. |
| B/C | La copia agregada fijó 4.940 fórmulas y sustituyó cinco hojas individuales por agregados; el QA registró cero cambios numéricos históricos. | outputs/retencion_puente_provisional_20261022/ensamblar.py:35–56; QA_ENTREGA.json | Hay una pérdida real de recálculo, no prueba de que todos los valores sean erróneos. Recuperar la rama formularia disponible. |
| B | En V18, hoja13 tiene cero fórmulas y B3 advierte que es fotografía; el original tiene 1.253 fórmulas en esa hoja. | 13_Granular_Codigo_Unico; originales y hashes en sección8 | No tratar la copia agregada como si conservara el funcionamiento del libro individual. |
| B/E | Guía27 describe detalle/formulación que ya no corresponde; hoja55 B11 dice104 pendientes, frente a99 en hoja52 A27. Hoja52 A32 conserva el estado previo a promover v8. | V18, 27_Guia_Hojas F14:G16/F18:F25; 55_Pendientes_entrega B11; 52_Codigos_SIES_Revision A27/A32 | Generar guía, controles y estado desde el mismo manifiesto de entrega. |
| C/E | La llave de INDEX/MATCH del libro original usa cohorte+N_DOC+DV+COD_CAR sin jornada. MATCH elige la primera coincidencia. No se ha cuantificado en este diagnóstico si existen colisiones efectivas. | Original: 9_Base_Analitica_Detalle U7:X7; 11_BASE_RETENCION_MU_RAW AH | Auditar unicidad y coherencia de fila antes de certificar el vínculo; no declarar error individual sin prueba. |
| B/C | 2.379 estudiantes y1.476 retenidos son cohortes elegibles2022–2025 del cálculo interno. No son matrícula total ni titulados. | H001 README:163,395–407,435; original13 B49/H136:J136 | Conciliar cada indicador con su propio universo y fuente. |
| B/C/E | DOCUMENTAL_ANUAL_ATRIBUIDO no acredita automáticamente devolución/aceptación SIES. La fuente derivada tiene procedencia general, pero falta presentar el trayecto a la fila primaria y el rol de cada archivo. | docs/DICCIONARIO_SIES_SEGUIMIENTO.md; MANIFEST_BASE_RETENCION_MU_2022_2026.json | Distinguir preparado, enviado, descargado/retornado, publicación agregada y derivado. |
| C/E | aceptación_SIES y plan_efectivo_periodo se inicializaron como NO_ACREDITADA/NO_ACREDITADO. Las24.774 observaciones mantienen esos estados. No prueban que se haya vuelto a evaluar la evidencia de cada cierre. | scripts/reproducir_puente_20261023.py:161; esquema/payloads v8 | Separar no evaluado, evaluado sin evidencia y acreditado por período; actualizar solo con evidencia. |
| B/E | El commit v8 publicó consumidores, descriptores y QA, pero el constructor, reproducción inicial y consolidador fase3 siguen locales, no versionados. | git ls-files de los tres scripts; outputs/auditoria_diccionario_sies_20261025/fase3_20261025/consolidar.py | Completar reproducción de extremo a extremo antes de llamar a todo el circuito reproducible desde Git. |

**C — Alcance del QA previo:** comprobó conservación respecto de la copia agregada, cambios de la edición y paridad de consumidores. No certificó el recálculo integral de las hojas cuyas fórmulas se habían fijado previamente ni la cadena completa de envío/retorno.

**B/C — Línea base reutilizable:** v8 conserva24.774 observaciones:21.569 documentales atribuidas,164 exclusivamente internas aprobadas y 3.041 pendientes. El alcance del Excel revisado contiene2.854 contextos localizados:2.742 documentales,13 internos y99 pendientes;24 pertenecen al foco multiversión. No son cantidades equivalentes de estudiantes, matrículas ni tasas de retención. Los contextos no localizados quedan fuera de ese denominador de consulta y deben contabilizarse aparte al medir el padrón T1 completo.

## 2. Diseño propuesto: una sola vista consultable, con sus fuentes conservadas

**C — Grano:** una fila por persona–expediente/matrícula–contexto académico observado. La llave se valida; no imponer una sola fila por RUT. Una persona puede tener varios CODCLI, y un CODCLI puede tener cambios de plan/contexto. Las asignaturas se relacionan como detalle y no multiplican estudiantes en los totales.

**C — Vista maestra hacia la derecha, como solicita el usuario:**

| Bloque de columnas | Contenido y procedencia exigidos |
|---|---|
| Identidad UMAS | Tipo de documento, documento y DV originales, llave normalizada, CODCLI, relación explícita cuando hay documentos distintos. No inventar DV ni equivalencia RUT↔MRUN. |
| Contexto UMAS | CODCARPR/CODCARR original, carrera, sede, jornada, PLAN_DE_ESTUDIO, fechas disponibles, año/período de matrícula y año/período de actividad por separado. |
| Ancla MU T1 | Año informado, identidad original, COD_SED, COD_CAR, JOR, VERSION, código completo literal o compuesto explícitamente, vigencia nativa y fila primaria. |
| Envío y retorno SIES | Código/atributos enviados, recibidos y publicados en columnas diferentes; archivo y rol acreditado, fecha/corte, hoja/fila/hash, resultado de comparación. No declarar aceptación sin su evidencia. |
| Oferta del año | Código completo vigente en el catálogo pertinente, modalidad, tipo de plan, nivel del programa, duración y unidades; referencia exacta. No reemplazar años históricos por oferta2027. |
| Seguimiento T2/T3 | Presencia, matrícula vigente del cierre, actividad académica, resultados de asignaturas, cambio de expediente/plan/jornada y respaldo temporal. Ausente en una fuente no se convierte automáticamente en desertor. |
| Resultado del diccionario | Código de cohorte/origen, código documental del contexto, correspondencia interna aprobada, propuesta y pendiente en campos separados; no fusionarlos ocultando su respaldo. |
| Nivel y trayectoria | Nivel declarado, posición en malla, avance observado y unidad; egreso y título con carrera/fecha. No equiparar NIVEL a trimestre ni título por duración cumplida. |
| Linaje y auditoría | Fuente/hoja/fila/campo/hash, versión de lector/regla, método de enlace, cardinalidad, alternativas, decisión/responsable/fecha y requisito pendiente. |

**C — Implementación:** una vista plana para revisar y filtrar, respaldada por tablas de identidad, expedientes, eventos, oferta y evidencias. Es un único modelo de consulta, no una única unión gigantesca que duplique matrículas por cada asignatura. Las bases originales son entradas de solo lectura; la vista consolidada es un derivado reproducible.

**C — Literal no significa error:** los valores fuente deben conservarse literalmente. Un resultado materializado es válido si tiene fuente, regla/script y prueba de reconstrucción. Los indicadores y controles del Excel deben ser fórmulas o consultas actualizables desde esa vista, no cachés sin una ruta visible de cálculo. Tener una fórmula de división tampoco acredita por sí solo las personas que integran el numerador.

## 3. Plan de seis fases, tres hitos por fase

Todos los hitos siguientes son **C — trabajo propuesto**, con pendientes de evidencia **E** y decisiones nuevas **D** cuando se indiquen. No están ejecutados por redactar este plan.

### Fase 1/6 — Fijar universo y recuperar la cadena existente

- **H1:** conservar v8, V17 y V18, y localizar la copia formularia comprobada. Reutilizar inventarios,79 entradas ya verificadas y decisiones previas; comparar hashes solo de archivos que se usarán. Registrar qué cierre, año y universo representa cada fuente.
- **H2:** registrar padrones T1 y denominadores aprobados para cada indicador, más matrículas totales, expedientes y actividad como universos separados. Contabilizar también las posiciones T2/T3 sin contexto, sin equipararlas a deserción ni omitirlas del control de cobertura.
- **H3:** auditar la llave actual del Excel contra sus filas MU: unicidad, coincidencias múltiples, jornada/versión y resultados de primera coincidencia. Separar respaldado sin cambios, contradicción verificable y evidencia insuficiente. Identificar las correcciones ya aprobadas posteriores al libro original para no revertirlas al recuperar fórmulas.

**Salida/puerta:** contrato de universos y matriz de linaje; una lista precisa de excepciones, sin cambiar denominadores. El 100% se mide sobre un padrón completo fijado, no solo sobre quienes aparezcan en PROMEDIOS.

### Fase 2/6 — Conciliar el ancla anual UMAS ↔ MU ↔ SIES

- **H1:** por año y código completo, reutilizar la MU original y sus componentes, enlazando identidad→CODCLI→expediente/contexto. No reducir el enlace a nombre o COD_CAR. Conservar conflictos y relaciones múltiples válidas.
- **H2:** enlazar envío y retorno cuando existan a nivel individual. Si un archivo SIES es solo agregado o usa una identidad no comparable, registrarlo como control agregado, sin simular un enlace personal. Contrastarlo con oferta del mismo año y con las fuentes ya inventariadas.
- **H3:** conciliar matrícula por año+código completo, tanto filas como personas únicas según el alcance del archivo. Comparar además conjuntos de identidades, no únicamente sus totales. Investigar solo diferencias y dejar fuente/rol/estado de aceptación explícitos.

**Salida/puerta:** tabla ancla por estudiante/expediente/año con código completo respaldado y evidencia primaria. La igualdad de totales es necesaria cuando los universos coinciden, pero no identifica por sí sola a qué versión pertenece cada estudiante. En familias con varias soluciones compatibles, registrar ambigüedad en lugar de escoger una distribución para igualar números.

### Fase 3/6 — Completar la vista longitudinal y las excepciones T2/T3

- **H1:** expandir el padrón T1 hacia T2/T3 mediante uniones que conserven a todos los integrantes. Relacionar CODCLI e identidad con las matrículas y actividad observadas. Reutilizar códigos T1 sin reabrir asignaciones cerradas; conservar código de origen separado del destino.
- **H2:** conectar calendario nativo/regímenes con los cierres solicitados mediante evidencia. Revisar por lotes solo cambios de carrera, plan, jornada o sede y múltiples matrículas. Distinguir fecha exacta, período acreditado y simple primera aparición; no exigir día cuando el período basta ni presumir continuidad por falta de un cambio localizado.
- **H3:** aplicar únicamente correspondencias ya aprobadas dentro de su alcance. Usar oferta, plan, malla y actividad para contrastar excepciones; no decidir una versión porque otra tenga el mismo total. Titulación acredita su propio evento, no automáticamente una matrícula anterior. Propuestas nuevas se cuantifican y quedan separadas hasta aprobación.

**Salida/puerta:** cada integrante T1 tiene una trayectoria o un pendiente específico en T2/T3; código de origen nunca se pierde por no conocer el código del destino. Se informa cobertura por personas, expedientes y contextos, con denominadores separados. La retención interna no se descarta por una versión SIES pendiente.

### Fase 4/6 — Recuperar el Excel trazable y su diseño

- **H1:** usar una copia de la maqueta formularia original; incorporar las correcciones posteriores documentadas, sin volver a sus errores antiguos. Preservar13 gráficos, colores, filtros y tablas; no sobrescribir V17/V18 ni el original.
- **H2:** alimentar una vista granular canónica en la copia local autorizada. Restaurar fórmulas de resúmenes y controles desde esa vista; conservar reglas anuales verificadas. Una tabla de detalle y sus agregados deben permitir explicar quién entra, quién sale y por qué, sin modificar el denominador vigente. Mantener claramente separados actividad, matrícula vigente, retención interna y comparación SIES.
- **H3:** actualizar guía de hojas, notas y QA desde el manifiesto real: distinguir RAW, vista derivada, cálculo, fuente oficial y fotografía histórica. Añadir navegación del indicador al detalle y de ese detalle a la evidencia. Identificadores solo en almacenamiento local privado; Git recibe código, contratos y controles agregados.

**Salida/puerta:** copia funcional con filtros conectados, fórmulas trazables y descripciones vigentes. No generar libros por lote; generar una edición al integrar y validar el conjunto. Un agregado para compartir, si se necesita, se etiqueta como tal y no sustituye al libro local funcional.

### Fase 5/6 — Conciliar cifras y demostrar qué parte alcanza el 100%

- **H1:** comprobar unicidad, documentos, relaciones uno-a-varios, asignaturas repetidas y cardinalidad de cada unión; impedir que dos errores se compensen en el total. Comparación fila a fila de claves y valores contra el ancla cuando el alcance lo permita.
- **H2:** cálculo independiente de numeradores/denominadores y comparación con fórmulas Excel. Controles por año, cohorte, carrera, código completo, jornada, sector y nivel pertinente; separar tabla de matrícula, tabla de retención y tabla de titulaciones. Probar filtros y combinaciones de cohortes: tasa = suma retenidos / suma estudiantes elegibles, no promedio simple de porcentajes.
- **H3:** abrir/recalcular una copia con Excel nativo cuando esté disponible, comprobar mensajes de reparación, tablas,13 gráficos, validaciones y cachés. Distinguir QA estructural, recálculo alternativo y apertura nativa. Presentar cualquier diferencia hallada como escenario antes de modificar cifras o denominadores aprobados.

**Salida/puerta:** cero diferencias matemáticas o de conjuntos sin explicar dentro de un mismo alcance, cero asignaciones ambiguas adoptadas y cero cambios no autorizados. Si falta evidencia, la fase no se declara100%; se conserva el pendiente con su requisito exacto.

### Fase 6/6 — Reproducción y publicación del circuito completo

- **H1:** versionar, previa depuración de datos personales, los constructores, lectores, transformaciones, parámetros y pruebas que hoy solo están locales. Un comando reproduce la vista y el libro desde fuentes con hashes conocidos. Validar una ejecución aislada con acceso autorizado a los insumos privados, sin depender de temporales o de valores pegados.
- **H2:** complementar el descriptor común con esquema, linaje, definición de universos y estado efectivo. Skills/complemento consultan esa misma entrada; no crean tablas copiadas. Integrar los tres GPT heredados solo al localizar su fuente editable y comprobar su consumo, sin prometer acceso remoto a la base privada.
- **H3:** preparar cambios exactos, responsable/fecha, alertas y reversión. Commit/push y cambios remotos solo con autorización específica del nuevo alcance y QA aprobado. Publicar evidencia agregada y código; comprobar lectura remota y conservar fuentes privadas.

**Salida/puerta:** reproducción comprobada y una sola definición activa. Publicación, trazabilidad y cobertura son controles separados; publicar no resuelve estudiantes pendientes.

## 4. Qué significa cerrar el 100%

**C — Tres medidas separadas; no intercambiables:**

1. **Cobertura del padrón:** todos los integrantes aprobados aparecen en la vista, incluidos los que no tienen actividad. Un pendiente visible cuenta como registro conservado, no como código resuelto.
2. **Cobertura de atribución:** contextos con código documental atribuible y contextos con correspondencia interna aprobada, presentados por separado. La proporción reutilizable se calcula sobre el universo fijado de la misma unidad; no sobre una selección de casos fáciles. La aceptación SIES se informa aparte y solo donde exista evidencia.
3. **Cobertura de linaje/cálculo:** cada campo derivado e indicador se puede reconstruir desde fuentes, reglas y contexto; cada celda de resultado conduce al detalle y a su fuente. Una regla o campo no evaluado no puede aparecer como confirmado.

**C/E — Objetivo:**100% del universo acordado trazado y100% de los códigos requeridos correctamente atribuidos con respaldo explícito. No se garantiza ahora que existan en los archivos todos los discriminantes necesarios para cerrar el segundo 100%. Si el retorno es agregado y persisten varias asignaciones personales compatibles, faltará evidencia individual o una decisión interna delimitada; cambiar la definición de resuelto no cierra el objetivo documental.

**C — Control numérico por población comparable:** diferencia de conteo = observado − referencia; diferencia relativa solo si la referencia no es cero. Retención = retenidos/elegibles; brecha de tasas en puntos porcentuales, no diferencia de matrícula. Titulaciones puede tener más de un evento por persona. No exigir matrícula total = elegibles = titulados.

## 5. Eficiencia: qué no repetiremos

**C:** reutilizar las 24.774 consultas auditadas, las adjudicaciones aprobadas y las extracciones con hash vigente. No repetir hipótesis universales de versión por año, mayorías ni búsquedas agotadas. La nueva prueba de primera coincidencia y los controles de linaje sí son necesarios: no estaban cubiertos por la paridad de consumidores.

**C:** procesar una fuente una vez y resolver lotes por evidencia común. Reabrir solo una asignación respaldada si aparece contradicción concreta. No rehacer todo2007–2027 para cerrar primero el Excel2022–2026; el histórico adicional se incorpora por alcance explícito. Una bitácora, un registro de excepciones y un checkpoint; nada de un Excel por persona.

## 6. Priorización y primer resultado esperado

**C:** ejecutar primero Fase1/H1–H3 y Fase2 para el ancla del libro actual2022–2026. Entregar una tabla por año+código completo: filas fuente, personas, expedientes enlazados, coincidencias envío/retorno, múltiples, pendientes y discrepancia. Ese control mostrará si el problema es lector, llave, cobertura o evidencia de versión; no exige resolver primero 3.041 observaciones históricas de actividad.

**E:** no hay una nueva cifra validada de carreras/combinaciones pendientes de este universo integral todavía. Los 99 y 3.041 del diccionario miden contextos de alcances anteriores; no deben reutilizarse como porcentaje de todos los matriculados. Fase1 fija el universo completo y concilia su relación con esos contadores.

## 7. Checkpoint de esta entrega

**B/C:** diagnóstico documental/XML de solo lectura; fases de este plan aún no ejecutadas. Sin cambios de fuentes, motores, v8, bases, Excel, tasas o denominadores. Sin commit/push. Se conserva el cambio pendiente previo de PROYECTO_IPSS.json. Siguiente paso: Fase1/6 · Hito1/3; recuperar linaje y ancla T1 utilizando lo existente.

## 8. Fuentes principales y localizadores

**B — Original formularia disponible:**
`/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx`
SHA-256: `20fe8438cba065f15240f1e67c066e5feb8bac8841f182864e40ca7bc9512aa8`.
13 gráficos y 33 tablas. Hoja13 H51=COUNTIFS de hoja9 B/X; I51=SUMIFS de hoja9 F con B/X; H136/I136=SUBTOTAL109; J136=I136/H136. Hoja9 U7:X7 y hoja11 AH documentan la llave a revisar.

**B — Copia V18 revisada:**
`/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx`
SHA-256: `2bd21ca31d391b59f4bd2c56d4876becd12aae05cb9673a7e069b5542ed66b01`.
55 hojas, 13 gráficos y 35 tablas. La preservación de gráficos no implica conservación de todas las fórmulas.

**B/C — Documentación local dentro del repositorio:**
- `manifests/milestones/H001-RETENCION-IPSS162/README.md`, líneas163,395–407,435.
- `outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json` e `INVENTARIO_FUENTES_SHA256.json`.
- `procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json`: reutilizar el control agregado; igualdad de totales por carrera no acredita reasignación individual entre versiones.
- `outputs/auditoria_embudo_2317_20261022/INFORME_EMBUDO.md`.
- `outputs/retencion_puente_provisional_20261022/ensamblar.py` y `QA_ENTREGA.json`.
- `common/diccionario_sies_seguimiento.py`, `scripts/construir_diccionario_sies_seguimiento.py`, `scripts/reproducir_puente_20261023.py`.
- `data/diccionario_sies_seguimiento/activo.json` y descriptorv8.
- `outputs/auditoria_diccionario_sies_20261025/fase3_20261025/` y `fase4_20261025/RECIBO_PUBLICACION.json`.

**A — Referencia delimitada:** manual Oferta-Acceso2027, página física66, extracción en `data/reglas_negocio/20261015/fuentes/manual_oferta_acceso_2027_texto_completo.json`, procedencia en `fuentes.json`: ISCJV y distinción entre cambio curricular y atributos que cambian versión. Solo orienta su edición; no se usa como justificación retrospectiva de versiones2019.
