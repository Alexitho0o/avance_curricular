# Fase 3/4 — Validación de indicadores históricos

[C] Ejecución 27-10-2026. Proceso: Avance Curricular histórico IPSS 162. Referencia oficial: proceso SIES 2026, datos académicos 2025. Perfil interno observado: años 2019–2026 y períodos literales UMAS. Rama feature/ire-2026, HEAD 262f445828f7e939fac59c3cc76d0bb20a101746 antes/después.

[C/E] Resultado: validación matemática y diagnóstico completados, con pendientes de atribución y alcance. QA: 53 controles PASS; estado PASS_CALCULOS_CON_PENDIENTES. Esto no certifica una nueva carga ni una tasa histórica definitiva. No se construyó Excel en esta fase.

## Hito 3.1 · Anual y acumulado

[A] El Instructivo Avance Curricular SIES 2026 (pp. 2–6) separa año de proceso, año académico, unidad del plan, avance respecto del plan y unidades anuales/acumuladas. Los reconocimientos aplicables pertenecen al acumulado, no a las aprobaciones anuales. El correlativo PLAN_ESTUDIOS de SIES no es el nombre del plan UMAS.

[B/C] Se conciliaron los 43 códigos-plan H112B y los 2.371 registros de H113/H114B. La tabla ANUAL_43_CODIGOS_PLAN.csv conserva los controles por código completo y correlativo del plan. Cada cociente se comprobó mediante dos representaciones numéricas (Fraction y Decimal); esto valida aritmética, no constituye una segunda fuente independiente de datos.

| Control observado | Numerador | Denominador explícito | Cociente | Clase |
|---|---:|---:|---:|---|
| Aprobación anual sobre unidades cursadas H113 | 17.628 | 21.389 | 82,42% | B/C |
| Avance acumulado observado H113 | 41.627 | 96.104 | 43,31% | B/C |
| Avance acumulado observado H114B | 38.235 | 96.104 | 39,79% | B/C |

[C] El denominador 96.104 suma las unidades de plan correspondientes a cada registro de la población congelada; no son estudiantes ni unidades de 43 planes contados una sola vez. Los porcentajes son cocientes agregados de sumas, no promedios simples de porcentajes personales. No son tasas de retención.

[B/C/E] H113 contiene 247 registros por encima del total del plan, 166 por encima del 125%. H114B no presenta ninguno de esos excedentes. La reducción de 3.392 aprobaciones acumuladas es una transformación histórica conservada, no una corrección aplicada hoy ni una prueba de exactitud de la atribución. El tope estricto al 100% no se convirtió en regla universal oficial: el instructivo contempla una tolerancia de referencia del 25%. Se reutilizan las auditorías de identidad/atribución previas; los 27 cambios del escenario de identidad y el caso P pendiente no se aplicaron al congelado.

## Hito 3.2 · Actividad por período

[B/C] PERIODOS_UMAS_OBSERVADOS.csv contiene cada extracción por separado, con año, período, personas, expedientes y resultados de asignatura. No se suman ni fusionan 7804 y 12166. Estos inventarios abarcan las fuentes, no reemplazan el universo de 2.371 registros ni los denominadores de retención.

| Fuente | Filas observadas | Personas observadas | Persona–CODCLI | Contextos expediente–plan–jornada | Sin año o período | Clase |
|---|---:|---:|---:|---:|---:|---|
| PROMEDIOS 7804 | 129.493 | 11.241 | 13.068 | 13.072 | 4.211 | B/C |
| PROMEDIOS 12166 | 70.000 | 7.938 | 8.975 | 8.976 | 0 | B/C |

[C] La comparación documental exige cuerpo y DV de formato comparable y CODCLI presente; no certifica la validez matemática del DV. Se conservaron llaves originales en memoria y no se exportaron identificadores. No hubo repeticiones idénticas bajo la llave de evento declarada; esto no demuestra ausencia de intentos repetidos o diferencias entre extracciones.

[B/C/E] Para 2026-3 en 12166 se observan 6.296 filas: A=0, R=0, E=15, I=522, otros/sin resultado=5.759. No se interpreta como cero aprobaciones finales ni como deserción. El archivo 7804 solo presenta período 1 de 2026. La cobertura completa y comparabilidad temporal de los extractos siguen pendientes; no se infiere la fecha de extracción del nombre.

[B/C] Sí existe conversión gobernada: codigo_gobernanza_v2.py, líneas 616–642, implementa PERIODO 1→semestre1 y 2/3→semestre2, y una conversión separada de nivel administrativo trimestral. El documento docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md distingue estos usos del nivel de asignatura. No se afirma que faltan todas las reglas.

[C/E] La extensión histórica conserva PERIODO literal (incluidos 4 y 5), porque la regla de ingreso/semestre y la conversión de NIV_ACA no acreditan por sí mismas el calendario aplicable a cada asignatura, régimen y año. El presente perfil no modifica el motor anual. ESTADO_ACADEMICO actual no se retroproyecta; NIVEL de asignatura no equivale a nivel completado por estudiante.

## Hito 3.3 · Aprobaciones y reconocimientos frente a malla

[B/C] El listado curricular contiene 223 pares carrera-plan; no se encontraron conjuntos distintos de CODRAMO entre sus sedes para un mismo par. Incluye 11.413 filas OBL y 25 OPC. La igualdad de listados no demuestra vigencia histórica ni que las opciones deban sumarse como exigencias obligatorias.

[C] MALLAS_CARRERA_PLAN_JORNADA.csv presenta 565 filas agregadas entre ambas fuentes: pertenencia exacta CODCARR + PLAN_DE_ESTUDIO + CODRAMO; aprobaciones A y reconocimientos E/I separados; unión de asignaturas logradas sin contar dos veces el mismo ramo por expediente-plan-jornada. Los ramos fuera del listado permanecen visibles. No se homologan por nombre ni RAMOEQUIV.

| Fuente | Contextos con listado exacto localizado | Sin listado por la llave completa | Nivel de asignatura coincide con listado (filas) | Sin nivel o ramo en listado (filas) | Clase |
|---|---:|---:|---:|---:|---|
| 7804 | 8.855 | 4.217 | 124.739 | 4.754 | B/C |
| 12166 | 8.956 | 20 | 69.898 | 102 | B/C |

[B/C] De los 4.217 contextos sin listado en 7804, 4.211 tienen CODCARR vacío o marcador NULL. Esto identifica la carencia de la llave usada; no significa que su malla no exista. Se conserva el pendiente en lugar de completarlo por similitud.

[C/E] El cociente contra tamaño del listado es descriptivo y está separado del campo avance_historico_validado, que permanece vacío/Pendiente hasta verificar aplicabilidad histórica, obligatoriedad/opcionalidad, atribución y cobertura. No se registra un cero donde falta malla. Las 15 correspondencias de reconocimiento individual ya aprobadas no se convierten en equivalencias generales; los 21 ramos generales pendientes siguen sin cierre nuevo. No se reabrieron los cuatro vínculos internos de titulación ya aprobados.

## Pendientes y reanudación

| Pendiente | Qué falta exactamente | Tratamiento | Clase |
|---|---|---|---|
| 644 contextos de fase 2 | Decisión sobre candidata ya preparada | No activados ni utilizados como código adoptado | E |
| Atribución completa | Excepciones de identidad/contexto del diagnóstico previo | Conservar cifras congeladas y escenario separados | E |
| Mallas históricas | Vigencia por plan/período y exigencia de opciones; equivalencias generales pendientes | Mostrar referencia observada, no avance definitivo | E |
| Períodos y cobertura | Regla de calendario aplicable a actividad por régimen/año y resultados disponibles | Conservar períodos literales y fuentes separadas | E |

[C] Fase 3 termina como diagnóstico reproducible con pendientes visibles. El siguiente trabajo es resolver el alcance de las atribuciones candidatas y del producto provisional antes de construir la fase 4. No repetir lectura de fuentes y conciliaciones congeladas si sus hashes no cambiaron. Este QA no autoriza ni certifica un Excel definitivo.

## Trazabilidad y conservación

[C] Reproducción desde la raíz del repositorio: python3 outputs/avance_historico_fase3_20261027/validar_indicadores.py. MANIFEST.json registra rutas, hashes de entradas y salidas, diccionario y estado Git. FORMULAS_Y_ALCANCE.json describe fórmulas y unidades. CHECKPOINT.json conserva el punto de reanudación.

[C] Incidente técnico de ejecución: una variable de ruta fue reutilizada como tabla y provocó un TypeError en la validación final del primer intento. Se corrigió el nombre, se repitió la ejecución y los 53 controles finalizaron correctamente. No se alteró ninguna fuente durante el incidente.

[B/C] Bases, fuentes, diccionario activo, denominadores, auditorías previas y los cuatro archivos con cambios preexistentes conservan sus hashes. No se generaron archivos individuales, Excel, commits ni push. Las salidas agregadas son locales y todavía no están publicadas.
