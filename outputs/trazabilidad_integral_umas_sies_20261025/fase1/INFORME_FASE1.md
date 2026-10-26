# Fase 1/6 — Universo, fuentes y trazabilidad recuperada

**B/C — Estado:** auditoría de los tres hitos ejecutada. La cadena anual de las 2.379 filas del cálculo de retención se reproduce sin diferencias; el contrato intertrimestral conserva discrepancias de alcance explícitas. Esto no certifica todavía el enlace UMAS–expediente–período de todo el padrón ni aceptación SIES.

**D — Alcance autorizado:** ejecutar Fase 1 del plan `../PLAN_FASES_HITOS.md`. Sin cambios de bases, libros, diccionario activo, reglas, tasas o denominadores; sin commit ni push. Proceso: trazabilidad de matrícula y seguimiento interno IPSS162 hasta2026. La oferta, matrícula, actividad y titulaciones mantienen sus universos propios.

**B — Contexto:** avance_curricular, rama `feature/ire-2026`, HEAD `8e2fb85bb8703758d6878681c9e2a29016e60c63`. Se conserva el cambio previo de `PROYECTO_IPSS.json`. Los hashes y controles finales figuran en `QA_FASE1.json` y `MANIFEST_FASE1.json`.

## Hito 1/3 — Fuentes y maqueta recuperadas

**B/C:** se verificaron disponibilidad y SHA-256 de diez entradas seleccionadas: maqueta formularia, V17, V18, MU consolidada, diccionario privado v8 y cinco fuentes anuales2022–2026. Diez coincidencias con los hashes esperados. No se repitieron las reglas de elegibilidad ni los cierres anteriores.

| Libro | Hojas | Gráficos | Tablas | Fórmulas XML | Clase |
|---|---:|---:|---:|---:|---|
| Original AUDITADO_ENTREGA del22-oct | 29 | 13 | 33 | 236.510 | B/C |
| V17 | 55 | 13 | 35 | 2.385 | B/C |
| V18 | 55 | 13 | 35 | 2.385 | B/C |

**B/C:** la maqueta con fórmulas está disponible. La edición agregada preserva cifras, pero no toda la capacidad de recálculo del original. Recuperar esa maqueta no significa volver a sus valores antiguos: se registraron nueve bloques de correcciones V14–V18, con206 entradas exactas de edición V14–V16 y sus evidencias.

**C/D — Correcciones que deben conservarse al integrar una edición futura:** auxiliar de actividadT2-2025 =611/1.150; auxiliarT3-2025 =546/1.150; foto de matrículaT3-2025 =1.023/1.150; T3-2026 grupo1 =1.360/1.467; T2-2026 =462/528 matrículas; conjunto2026 =2.290/2.519. Cada resultado tiene contexto y regla distintos. No sumarlos ni sustituirlos entre sí.

**B/E:** persisten notas heredadas enV18: hoja55 B11 menciona104 pendientes frente a99 del control actualizado; hoja52 A32 menciona v7 aunque el descriptor activo es v8. Se registraron para una próxima edición; ningún libro fue alterado.

**E:** ubicación en carpeta «Enviados» no demuestra por sí sola aceptación o devolución SIES. Esa cadena es objeto de Fase2.

Evidencias: `CADENA_Y_FUENTES.json`; `correcciones/MATRIZ_CORRECCIONES_V14_V18.md` y su JSON con celdas, fuentes y hashes.

## Hito 2/3 — Contrato de universos conservados

**B/C:** se recuperaron las4.473 filas del padrón original de hoja20, con identidad y fila de origen. Los agregados deV18 conservan sus conteos. La hoja20 original no contiene CODCLI: no se inventó ese campo ni se supuso un expediente único por persona.

| Grupo existente | Población del grupo | Base de cálculo T2 | Base de cálculo T3 | Alcance conservado | Clase |
|---|---:|---:|---:|---|---|
| 2024, grupo1 | 558 | 558 | 558 | Cohorte2024; consulta existente observa2025 | B/C/E |
| 2025, grupo1 | 1.150 | 1.150 | 1.150 | Padrón del grupo1 | B/C |
| 2025, grupo2 | 222 | 222 | 222 | Personas del listadoT2 | B/C |
| 2026, grupo1 | 1.471 | 1.471 | 1.467 | Cuatro exclusiones internas deT3 documentadas | B/C/D |
| 2026, grupo2 | 527 | 528 matrículas | 527 personas | T2 yT3 usan unidades distintas | B/C/E |
| 2026, grupo3 | 545 | No aplica en el libro | 545 | Toda la hojaBase del listadoT3, no solo ingreso2026-3 | B/C/E |

**B/C:** los grupos se solapan. En2025,1.372 pertenencias representan1.368 personas; en2026,2.543 pertenencias representan2.523 personas. Estos totales no sustituyen ninguna base de cálculo vigente.

**B/C — Diferencia comprobada de etiqueta en2026-T3:**

| Año/período de ingreso en hojaBase | Matrículas | Personas distintas dentro del grupo | Clase |
|---|---:|---:|---|
| 2024-3 | 22 | 22 | B/C |
| 2025-3 | 34 | 34 | B/C |
| 2026-3 | 501 | 490 | B/C |
| Toda la hojaBase | 557 | 545 | B/C |

**B/C:** una persona pertenece a2024-3 y2026-3; por ello las pertenencias suman546 y la unión545. La hoja2026_3 coincide por conjunto deCODCLI con los501 registros de ingreso2026-3. Las545 personas deBase coinciden exactamente con el grupo2026/3 de la hoja20 original.

**E — Decisión de alcance pendiente:** conservar el conjunto545 exige describirlo como listado completo, no como ingreso exclusivo2026-3. Cambiar la población requeriría una decisión posterior. En esta fase se conservan545 y no se adopta490 como denominador.

**B/C/E — Cobertura del seguimiento ya existente:** los3.179 orígenes del grupo1 generan6.358 posiciones origen×período nativo2/3. Hay2.838 posiciones con contexto,3.520 sin contexto y2.854 contextos porque16 son adicionales en posiciones con varios expedientes/planes. Los2.854 se distribuyen en2.742 documentales atribuidos,13 internos aprobados y99 pendientes. Los99 no representan todo el pendiente del padrón completo.

**E:** estas son posiciones por período nativo, no un calendario homologado de cierres. Para2024 se observa2025; para2025 y2026 se observa el mismo año. «Sin contexto» no significa sin actividad, sin matrícula ni desertor. El enlace al contexto requiere conservar esa distinción en Fases2–3.

**B/E:** las124 personas de ingreso2025-T3 pertenecen a otro ejercicio ya existente y no aparecen como grupo3 en este padrón intertrimestral. No se añadieron silenciosamente. Las66 renuncias deT2-2026 siguen sin nómina de origen que permita convertir462/528 matrículas en una tasa por personas.

Evidencias: `universos/INFORME_UNIVERSOS.md`, `RESULTADOS_UNIVERSOS.json`, rangos y SHA de cada entrada. Son un contrato descriptivo del estado existente, no aprobación de nuevas poblaciones o interpretaciones.

## Hito 3/3 — Prueba del código completo y de la primera coincidencia

**B/C:** se reprodujo el enlace de hoja9 a hoja11 de la maqueta original, incluyendo código completo, jornada, modalidad y tipo documental. Se comprobaron9.516 fórmulasU:X y10.200 fórmulasAH. Una segunda consulta independiente medianteSQLite dio el mismo resultado.

| Cohorte | Filas elegibles auditadas | Retenidos conservados | Coincidencia MU única | Sin coincidencia o múltiples | Clase |
|---|---:|---:|---:|---:|---|
| 2022 | 305 | 224 | 305 | 0 | B/C |
| 2023 | 366 | 258 | 366 | 0 | B/C |
| 2024 | 558 | 326 | 558 | 0 | B/C |
| 2025 | 1.150 | 668 | 1.150 | 0 | B/C |
| Total de filas de cohortes | 2.379 | 1.476 | 2.379 | 0 | B/C |

**B/C:** cero diferencias entre los códigos completos reproducidos y los del libro; cero discrepancias de caché en las fórmulas auditadas. Los20 documentosP de2025 enlazan correctamente en este original. La búsqueda por primera coincidencia no produjo un error dentro de estas2.379 filas.

**B/E:** fuera de ese universo, la MU2026 contiene cinco llaves repetidas, diez filas con códigos diferentes. No son duplicados técnicos exactos. Quedan para atribución por expediente/contexto, sin elegir ahora una fila:

| COD_CAR | Diferencia entre candidatos | Clase |
|---|---|---|
| 1 | J1V1 frente aJ4V2 | B/E |
| 1 | J1V1 frente aJ2V4 | B/E |
| 91 | J1V1 frente aJ2V1 | B/E |
| 114 | Sede2 frente a3, mismaJ2V1 | B/E |
| 115 | Sede2 frente a3, mismaJ2V1 | B/E |

**E — Límite exacto:** el resultado valida código y fila en la MU incorporada. No certifica por sí solo la aceptación SIES, el expedienteCODCLI/plan ni su continuidadT2/T3. El100% comprobado aquí es2.379/2.379 enlaces del cálculo anual, no100% de toda la trazabilidad institucional.

Evidencias: `llaves/INFORME_LLAVES.md`, `RESULTADOS_AGREGADOS.json`, `QA.json`. El detalle mínimo individual permanece exclusivamente fuera deGit, en `/Users/alexi/.local/share/ipss/trazabilidad_integral_fase1_20261025/llaves/DETALLE_LLAVES.json`.

## Cierre y siguiente punto de reanudación

**C — H1 yH3:** verificaciones terminadas. **C/E — H2:** universos existentes reproducidos; no se declara aprobado un alcance corregido donde la etiqueta o el calendario difieren. La discrepancia545/490 bloquea una redefinición silenciosa del grupo, no el trabajo independiente sobre los padrones ya fijados.

**C — Fase2 propuesta:** enlazar identidad y expedienteUMAS con el anclaMU anual y la evidencia primaria de envío/retorno. Reutilizar los2.379 enlaces reproducidos, conservar los3.179 orígenes del grupo1 y revisar las cinco llaves2026 múltiples. No reabrir las asignaciones previas sin contradicción concreta. No comenzar por repartir versiones para igualar totales.

**C/E — QA y límites:** controles estructurales, reproducción de las fórmulas de enlace, comparación independiente y hashes. No se ejecutó recálculo integral ni apertura nueva enExcel nativo; se conserva el antecedente de aperturaV15 sin presentarlo como prueba actual. Los numeradores históricos se conservaron; no se recalculó la regla anual ni se generaron tasas nuevas.

**B/C:** entregables nuevos de auditoría agregada, fuentes originales intactas, sin nueva versiónExcel ni adjudicaciones. Rama yHEAD inicial/final, hashes de preservación y lista exacta de archivos figuran en los controles de esta fase.
