# Fase 3/6 — Seguimiento T1 en T2/T3 y excepciones

**B/C — Resultado:** se reprodujo el seguimiento del padrón existente con el diccionario activo. Se conservan los 3.179 orígenes y sus 6.358 posiciones origen×período. No se agregan estudiantes ni se cambia ningún denominador.

**D — Alcance aprobado:** reutilizar códigos documentados y correspondencias internas ya autorizadas; revisar solo excepciones de carrera, sede, jornada y plan. No hubo adjudicaciones nuevas, cambios al diccionario ni modificación del Excel.

**C — Unidad:** un contexto identifica persona, CODCLI, plan y período; no equivale a una persona adicional ni a un retenido. Hay 2.854 contextos únicos en 2.838 posiciones, correspondientes a 1.527 orígenes. Las 3.520 posiciones restantes no tienen contexto en este diccionario; este resultado no prueba deserción ni ausencia en la foto de matrícula.

## Resumen de códigos por período

| Cohorte de origen | Año observado | Período nativo | Padrón T1 | Mismo código | Otro respaldado | Código pendiente | Sin contexto |
|---|---|---|---:|---:|---:|---:|---:|
| 2024 | 2025 | 2 | 558 | 210 | 15 | 27 | 313 |
| 2024 | 2025 | 3 | 558 | 229 | 17 | 30 | 289 |
| 2025 | 2025 | 2 | 1150 | 535 | 0 | 7 | 608 |
| 2025 | 2025 | 3 | 1150 | 456 | 0 | 6 | 688 |
| 2026 | 2026 | 2 | 1471 | 666 | 2 | 15 | 789 |
| 2026 | 2026 | 3 | 1471 | 622 | 3 | 14 | 833 |

**B/C/D/E — Lectura:** las tres columnas de códigos cuentan contextos; “Sin contexto” cuenta posiciones de origen. Por eso no deben sumarse como estudiantes. El calendario heredado se conserva explícitamente: cohorte 2024 se observa en 2025; cohortes 2025 y 2026 en su propio año. No se convierte automáticamente un período académico nativo en fecha de cierre.

## Excepciones verificadas

- **B/C:** 2.718 contextos conservan exactamente el código completo T1. Otros 37 contienen un código distinto ya respaldado: 32 documentales anuales atribuidos y cinco correspondencias internas aprobadas (**D**).
- **B/C:** los 37 se distribuyen, sin solapamientos, en 23 diferencias de jornada (12 también de versión), ocho de carrera (siete también de versión) y seis solo de versión. No hay diferencias de sede en esos códigos. Una segunda carrera puede ser matrícula paralela: no se afirma abandono de la primera (**E**).
- **B/C:** se revisaron 149 contextos de excepción y sus 352 filas citadas de PROMEDIOS, con 2.112 comparaciones exactas de CODCLI, plan, año, período, documento y DV. Cero diferencias. El detalle preserva fuente, hoja y fila; está fuera de Git.
- **B/C:** en 2.828 contextos el mismo CODCLI conserva carrera UMAS y plan respecto del período nativo 1 disponible. En 26 no existe ese contexto comparable (**E**). No se infiere una fecha administrativa de cambio.
- **B/C:** entre T2 y T3, 1.316 trayectorias de expediente comparables conservan el plan; otras 222 no tienen ambos períodos. No se observó cambio de plan en las comparables. Esto no demuestra ausencia de cambios fuera de los períodos/cobertura revisados (**E**).
- **E:** quedan 99 contextos sin código de destino aplicable, vinculados a 55 orígenes; no son 99 estudiantes. En el foco heredado de carreras con varias versiones: 1.040 contextos documentales, 13 internos aprobados y 24 pendientes. Los 24 están incluidos en los 99.
- **B/C:** respecto de la instantánea v7, se reutilizan cinco recuperaciones documentales ya aprobadas en v8, todas con el mismo código T1. No son cierres nuevos de esta fase.
- **B/C/E:** 3.165 códigos de origen se recuperan en el índice MU de la API; 14 conservan respaldo literal de la fuente MU previamente verificada. Se mantienen visibles sin inventar una equivalencia de identidad ni excluirlos.

## Qué queda pendiente

**E — Atribución por contexto:** los 99 requieren evidencia de código aplicable al expediente/período. Los archivos EXCEPCIONES_AGREGADAS.csv y la vista privada conservan la regla y el requisito pendiente de cada observación. Un código T1 diferente de la jornada actual no se impone sobre una excepción histórica.

**E — Cobertura:** las 3.520 posiciones sin contexto requieren distinguir ausencia en el índice de ausencia en fuentes de matrícula/actividad. No se usan para bajar las tasas ni se reabren todos los históricos en esta fase. Los 26 contextos sin plan T1 comparable y las 14 anclas fuera del índice de la API son pendientes distintos; no se suman a los 99 como si fueran personas nuevas.

## Trazabilidad y conservación

**C:** seguir_t1.py consulta la API común a través del descriptor activo v8, contrasta las excepciones y produce una vista longitudinal. cerrar_fase3.py vuelve a contar las salidas y verifica preservación. RESULTADOS_FASE3.json registra entradas y hashes; MANIFEST_FASE3.json registra salidas y hashes.

**C:** QA técnico: 20/20 controles correctos; 13 archivos protegidos sin cambios. Se corrigió durante el QA un doble incremento del contador auxiliar de pendientes; no afectó fuentes ni adjudicaciones. El recuento independiente final verifica 2.718 + 37 + 99 = 2.854.

**C/D:** no se recalcularon tasas, no se modificaron bases, denominadores, reglas ni los libros existentes. En particular, población T1-2026 de 1.471 y denominador específico T3-2026 de 1.467 se mantienen distintos según la entrega previa; esta auditoría no los reemplaza.

**B/C:** rama `feature/ire-2026`, HEAD antes/después `8e2fb85bb8703758d6878681c9e2a29016e60c63`. Sin commit ni push; PROYECTO_IPSS.json mantiene su modificación previa. Archivos agregados locales listos para revisión; esto no equivale a publicación en GitHub.

## Archivos

- RESUMEN_POR_PERIODO.csv: conteos por cohorte y período.
- SEGUIMIENTO_POR_CODIGO.csv: origen/destino, carrera UMAS, plan y respaldo agregados.
- CODIGOS_DISTINTOS_RESPALDADOS.csv: los 37 contextos agregados por combinación.
- EXCEPCIONES_AGREGADAS.csv: los 149 contextos de revisión, motivos, reglas y pendientes.
- PLANES_T2_T3.csv: comparación del plan entre períodos.
- Detalle local restringido: `/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025`. VISTA_T1_T2_T3.json conserva todas las posiciones y los contextos; REVISION_FILAS_PROMEDIOS.json, los controles de evidencia; TRAYECTORIAS_PLANES.json, la comparación de planes. Permisos 700/600; fuera de repositorios Git.

**C — Reanudación:** usar esta vista y las excepciones para la siguiente fase autorizada. No volver a inferir códigos por totales ni promover pendientes por candidato único. La fase queda ejecutada con límites visibles, no como cobertura completa del 100%.
