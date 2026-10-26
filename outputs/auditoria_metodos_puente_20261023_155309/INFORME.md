# Auditoría de métodos y prueba del diccionario UMAS–SIES

**C — Diagnóstico:** el proyecto ha recuperado numerosos códigos, pero la medida de avance se desplazó desde seguir T1 en T2/T3 hacia resolver todas las observaciones de un histórico. El diccionario vigente registra códigos por persona y contexto; aprobar una excepción no crea automáticamente una equivalencia general. La mejora propuesta consiste en reutilizar los códigos T1 documentados, validar correspondencias por grupos anuales y tratar los cambios de destino por separado.

**B/C — Alcance:** avance_curricular, rama feature/ire-2026, HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040. El experimento usa actividad de 2019–2026 y períodos nativos 1–5. No presupone que todos sean trimestres ni que exista cobertura individual completa de 2007–2027. Se utilizaron únicamente fuentes locales entregadas o conectadas. No se modificaron fuentes, tasas, denominadores, Excel ni diccionario activo. No hubo commit, push ni envío de datos a servicios externos.

## 1. Métodos probados: diez familias, no diez ejecuciones

**B/C:** esta clasificación agrupa las reiteraciones de cada método. Sus universos son distintos; los resultados no constituyen un ranking de precisión directamente comparable. Las fuentes específicas y sus hashes están en FUENTES_METODOS.json.

| N.º | Familia de cruce | Variables principales | Resultado documentado | Límite |
|---|---|---|---|---|
| 1 | Identidad exacta en varios procesos | RUT/DV normalizado; luego familia, año y CODCLI | 497 de 504 personas del primer subconjunto con código localizado | Encontrar la persona no atribuye automáticamente expediente y período. |
| 2 | Conciliación anual documental | Persona + familia + año + contexto DatosAlumnos | 1.760 observaciones conciliadas; 479 personas completamente y 77 parcialmente; pendientes de 2.317 a 1.838 entre 5.901 | Mayor avance comparable registrado. No acredita aceptación SIES ni fecha efectiva trimestral. |
| 3 | Equivalencias manuales vigentes | Carrera, plan y demás condiciones de cada equivalencia | 119 observaciones; 87 personas completamente; pendientes internos de 1.838 a 1.751 | Cierre interno, separado del documental. |
| 4 | Ampliación histórica y normalización de lectores | Documentos, componentes SIES, archivos y años omitidos | Evidencia recuperada en 9 de 13 dimensiones inicialmente sin coincidencia | Mejora la cobertura de búsqueda, sin crear una equivalencia universal. |
| 5 | Versión predominante por grupo | Carrera/sede/jornada; predominio del 90% y soporte mínimo | 39 propuestas entre 63 combinaciones | No eran 39 equivalencias aprobadas. Conservar totales no demuestra asignación individual. |
| 6 | Oferta histórica + perfil + ingreso | Familia, duración, tipo, oferta e ingreso registrado en DA | Sobre 3.213 pendientes: 402 propuestas por inicio, 2.370 por intervalo y 441 sin propuesta | El perfil grupal y el ingreso observado no prueban inicio efectivo del plan. |
| 7 | Corroboración personal en otro año | Código propuesto + MU histórica de la persona | 811 de 2.165 observaciones con respaldo en otro año | No prueba invariancia temporal. Solo se adoptaron las 119 correspondencias cubiertas por reglas existentes. |
| 8 | Cohorte/admisión y validación retrospectiva | Ingreso + perfil + oferta; evaluación separada por persona | Prueba agrupada: 15.171 aciertos, 1.387 errores y 1.268 abstenciones sobre 17.826 contextos regulares | 91,62% de acierto entre asignados; no es una regla universal ni una validación trimestral. |
| 9 | Trayectorias, fechas y cambios de plan | Persona → CODCLI → plan → período; anclas MU | 374 personas y 377 relaciones persona–familia examinadas | Fecha de matrícula y año escrito en el plan no equivalen a fecha de asignación. |
| 10 | Excepciones por actividad, secciones y homologaciones | CODCLI, plan, asignaturas, fechas y aprobación individual | 45 cierres internos posteriores a V10; de 3.094 a 3.049 observaciones pendientes y de 1.751 a 1.746 personas | Resuelven casos particulares, pero no generan automáticamente una regla reutilizable. |

**C:** no sumar recuperaciones de métodos diferentes: existen poblaciones solapadas. Las tres heurísticas temporales simplificadas del historial no se presentan como recalculadas en esta auditoría. El 38,10% original medía 24 de 63 combinaciones; no era porcentaje de personas ni tasa de retención. El escenario de 501 personas pendientes no fue adoptado.

## 2. Brújula actual: unidades y resultados separados

**B/C — Recuento reproducido del diccionario activo:**

| Unidad o estado | Cantidad |
|---|---:|
| Observaciones históricas | 24.774 |
| Personas distintas | 5.901 |
| Expedientes carrera + CODCLI | 6.622 |
| Observaciones con código documental anual atribuido | 21.561 |
| Observaciones resueltas solo por correspondencia interna | 164 |
| Observaciones pendientes de correspondencia interna | 3.049 |

**C:** los códigos reutilizables suman 21.725 de 24.774 observaciones: 87,69%. Esta es cobertura de correspondencias, no tasa de retención.

| Estado por persona, categorías excluyentes | Interno | Documental |
|---|---:|---:|
| Sin observaciones pendientes | 4.155 | 4.063 |
| Parcialmente resuelta | 704 | 699 |
| Ninguna observación resuelta | 1.042 | 1.139 |
| Total | 5.901 | 5.901 |
| Personas con algún pendiente | 1.746 | 1.838 |

**B/C:** las 3.049 observaciones pendientes se distribuyen en 2.966 sin evidencia anual aplicable, 67 con atribución múltiple, 15 sin contexto DA exacto y una homologación en plan rechazado. No equivalen a 3.049 estudiantes sin retención. El foco INF35, con 27 de 35 observaciones reutilizables, es otro subconjunto.

**E:** falta medir explícitamente cuántos de esos pendientes afectan a los denominadores concretos del Excel solicitado. Esta auditoría no recalculó ese subconjunto; no afirma que toda la cola histórica bloquee el seguimiento T1→T2/T3.

## 3. Hipótesis y experimento nuevo

**C — Hipótesis:** el código SIES anual puede predecirse mediante carrera UMAS + sede + jornada + año + plan, con posible mejora al incorporar el año de ingreso registrado en DatosAlumnos. El nombre de carrera es una etiqueta, no la llave principal. La hipótesis se evalúa; no se presume su validez.

**C — Diseño:** las 21.561 etiquetas anuales repetidas en diferentes períodos se redujeron a 8.354 contextos anuales de 4.762 personas. La unidad es persona + expediente + plan + carrera + sede + jornada + año. Ningún contexto anual tuvo que excluirse por etiquetas contradictorias. Se separaron las personas completas en cinco particiones: ninguna persona aparece simultáneamente en los datos usados para construir y evaluar el cruce. Solo se propone un código si el grupo de construcción es unánime y contiene al menos tres personas distintas. Es un umbral experimental, no una regla funcional aprobada.

| Variables | Aciertos | Errores | Sin asignación | Cobertura | Acierto entre asignados |
|---|---:|---:|---:|---:|---:|
| Carrera + sede + jornada + año | 6.789 | 5 | 1.560 | 81,33% | 99,93% |
| Las anteriores + plan | 7.662 | 10 | 682 | 91,84% | 99,87% |
| Las anteriores + ingreso DA | 7.664 | 6 | 684 | 91,81% | 99,92% |

**C — Fórmulas:** cobertura = asignados / 8.354; acierto entre asignados = correctos / asignados; abstención = sin asignación / 8.354. No son tasas de retención. Las dos últimas variantes no asignan exactamente los mismos registros; sus porcentajes no bastan para declarar una ganadora universal.

**B/C:** en las familias con varias versiones, la tercera variante asigna 4.619 de 5.256 contextos: 4.613 aciertos y seis errores; cobertura del 87,88% y acierto del 99,87% entre asignados. Una revisión independiente con código propio reprodujo el universo y las dos últimas filas sin diferencias. Los resultados por partición y año están en VALIDACION_POR_PERSONA.json.

**B/C — Procedencia de las variables:** carrera y plan proceden de CODCARR y PLAN_DE_ESTUDIO de PROMEDIOS; jornada procede de JORNADA mediante el mapa observado D→1, V→2, O→4. No se extrajeron de la versión objetivo. La sede proviene de la dimensión previa carrera/jornada del puente, pues PROMEDIOS no contiene sede individual. La etiqueta documental fue atribuida dentro de familias previamente permitidas por carrera/jornada y con contexto DA concordante. Por ello, esta prueba evalúa principalmente la discriminación de versión dentro del contexto preasignado; no demuestra de nuevo, desde cero, los componentes institución/sede/carrera/jornada. DA_ANOINGRESO procede de los cortes 12159 y 11248, no necesariamente de una captura contemporánea al período histórico.

**E — Límites:** se predicen etiquetas anuales previamente atribuidas; no se certifica la versión efectiva de cada trimestre, el envío o aceptación SIES ni la calidad absoluta del emparejamiento heredado. La separación por persona evita reutilizar su propia etiqueta, pero no elimina todos los posibles sesgos de los perfiles y de la atribución original. La jornada contextual y el plan deben comprobarse históricamente antes de usar el resultado para T2/T3. El universo documentado puede diferir del pendiente. El 99,92% no es una garantía para los pendientes ni para nuevos años. ANOINGRESO del corte DA no acredita por sí solo la fecha original del plan.

**C:** al construir el modelo solo con etiquetas de años anteriores, la variante que usa plan e ingreso registra 91,60% de acierto entre asignados y 38,32% de cobertura. Tampoco es universal trasladar un código del mismo expediente desde cualquier otro año: esa prueba obtuvo 4.536 aciertos y 381 errores en 4.917 asignaciones. No revoca los cierres aprobados con evidencia adicional; demuestra que la continuidad por sí sola no basta. Esta es transferencia retrospectiva con atributos disponibles hoy, no una predicción prospectiva estricta: plan, jornada e ingreso pueden contener información posterior al año evaluado.

## 4. Diccionario anual observado, visible y no promovido

**B/C:** DICCIONARIO_ANUAL_OBSERVADO.csv contiene 278 combinaciones de año + carrera + sede + jornada + plan: 256 con un único código observado y 22 con varios. Son combinaciones, no 278 carreras. Incluye los códigos, conteos y estado, sin identificadores individuales. Un grupo observado unívoco no es automáticamente una equivalencia aprobada para otra persona.

| Año | Carrera / plan | Jornada | Códigos observados y personas |
|---|---|---:|---|
| 2024 | IINF / IINF20241 | 4 | I162S2C1J4V2: 132; I162S2C1J4V3: 1 |
| 2025 | IINF / IINF20241 | 1 | I162S2C1J1V2: 18; I162S2C1J1V1: 5 |
| 2025 | IINF / IINF20241 | 2 | I162S2C1J2V4: 13; I162S2C1J2V1: 7 |

**B/C:** las mismas variables de esa llave coexisten con versiones distintas. Debe identificarse un atributo omitido, comprobarse una corrección de fuente o formularse una regla interna delimitada. Escoger la versión mayoritaria no resuelve la evidencia de la minoría.

**C/E:** en las 3.049 observaciones pendientes, la variante con plan genera 2.738 candidatos; al añadir ingreso DA, 2.668. Se excluyó a la persona del grupo utilizado para predecirla. Son propuestas exploratorias, no cierres ni una reducción del pendiente. Ninguna se adoptó.

## 5. Conciliación de totales e identificabilidad

**C — Formulación propuesta, no aplicada a las personas:** para cada expediente/contexto i y código candidato v, definir una variable binaria x(i,v). Si el universo requiere una única clasificación, exigir suma_v x(i,v) = 1. Fijar las correspondencias documentadas y excluir incompatibilidades respaldadas de carrera, sede, jornada, perfil y tiempo. La continuidad entre períodos es una hipótesis adicional; no se vuelve prueba documental por favorecerla.

Solo cuando los dos lados representan exactamente el mismo universo —año, fecha de corte, vigencia, institución, nivel y grano— se puede exigir suma_i x(i,v) = total(v). Si difieren, conservar y explicar la brecha; no forzar igualdad ni usar matrícula completa para una subcohorte de primer año.

La comprobación decisiva es la unicidad. Se calcula el mínimo y máximo de x(i,v) entre todas las soluciones admisibles: si ambos son uno, las restricciones fuerzan esa asignación; si varía entre cero y uno, sigue ambigua. Esto demuestra unicidad bajo las restricciones declaradas, no prueba de envío SIES. Si no existe solución, hay incompatibilidad entre las restricciones o la cobertura.

**C — Ejemplo sintético comprobado:** dos expedientes indistinguibles y totales V1 = 1, V2 = 1 admiten dos asignaciones: A→V1/B→V2 y A→V2/B→V1. Ambas calzan. Un ancla comprobada A→V1 permite deducir B→V2 únicamente si el universo es exacto. No se ejecutó un optimizador sobre poblaciones reales en esta auditoría.

## 6. Solución operativa propuesta

**C — Sin cambiar reglas ni denominadores:**

1. Fijar el universo T1 del Excel y recuperar su código SIES de origen por persona, expediente y año. Consultar primero el vínculo documental existente.
2. Seguir cada expediente en la actividad y los respaldos T2/T3. Separar actividad académica, vigencia al cierre, egreso y titulación. La ausencia en un extracto no prueba deserción; una nota no prueba automáticamente matrícula vigente al cierre.
3. Conservar el código de origen para analizar la cohorte y registrar aparte el código de destino cuando se acredite. Si el indicador exige permanencia en el mismo programa, identificar el cambio sin confundirlo con desaparición institucional. La consulta seguir_cohorte ya separa ambos códigos.
4. Construir las nuevas correspondencias por grupos anuales. Revisar los 22 grupos con varios códigos y los errores del control antes de promover reglas. Las propuestas conservan su clasificación C/E hasta validación y aprobación aplicables.
5. Conciliar totales comparables y probar unicidad. No asignar por cuota si distintas distribuciones individuales cumplen los mismos totales.
6. Medir por separado cobertura del universo del Excel, precisión evaluada fuera de la persona, grupos conflictivos y pendientes internos/documentales. Los consumidores deben consultar el mismo descriptor; un experimento no actualiza automáticamente complementos o skills.

**C/E — Conclusión:** hay una vía comprobable para trabajar por grupos y evitar redescubrir cada expediente. No está demostrada una equivalencia universal. La auditoría entrega resultados, límites y un diccionario observado para concentrar el siguiente trabajo, sin alterar el canon ni los indicadores vigentes.
