# Cierre incremental UMAS–SIES — plan revisado v2

**C — Contexto:** 25-10-2026. Seguimiento T1/T2/T3 hasta 2026; histórico observado
2019–2026. Repositorio avance_curricular, rama feature/ire-2026, HEAD de referencia
55e3b709afb9483f0ecdd2d166f67229a454a5ef. Los períodos nativos 1–5 del histórico
no se convierten automáticamente en trimestres.

**D — Encargo:** cobertura respaldada sin repetir trabajo ya documentado.
**C — Revisión:** cuatro fases y 12 hitos sustituyen siete fases y 21 hitos.
El plan y checkpoint anteriores se conservan en historial_plan/v1/.
Esta entrega modifica la planificación; no modifica códigos, fuentes ni tasas.

## 1. Lo ya comprobado se hereda, no se reinicia

**B/C — Evidencias:** LEEME.md, MANIFEST.json, QA_CONSULTA.json, QA_ENTREGA.json,
insumos/resumen.json e insumos/capas.json de esta carpeta; documentación y
decisiones en docs/DICCIONARIO_SIES_SEGUIMIENTO.md y data/diccionario_sies_seguimiento/
desde la raíz del repositorio.

| Trabajo existente [B/C] | Qué se hará ahora [C] |
|---|---|
| Inventario y 79 entradas verificadas | Consultar sus rutas y evidencias; sin otro barrido general de OneDrive, Descargas o Git. |
| 24.774 consultas históricas y 2.854 de V17 sin diferencias | Reutilizar el QA de esa edición; no reconsultar todo por cada lote. |
| Paridad de tres consumidores y 12 pruebas sintéticas | Repetir únicamente controles afectados y validar la próxima edición de entrega. |
| Ediciones v1–v7, aprobaciones y trayectorias investigadas | Consultar primero sus conclusiones y alcance. No reconstruir cada historia ni pedir nuevamente una aprobación vigente. |
| Excel ejecutivo y V17 ya auditados | Conservarlos. No regenerar Excel por persona o lote; el QA existente no certifica una futura versión. |

**B — Comprobación puntual de esta revisión:** HEAD y hash del descriptor activo
coinciden con la auditoría. v7, su servicio y documentación existen localmente,
pero no están en ese HEAD. No se repitieron cruces, recálculos ni lectura de las
79 fuentes. La consulta remota de complementos no se repitió. Se hereda evidencia
fechada; no se declara que archivos no releídos hayan sido certificados nuevamente.

## 2. Línea base heredada

| Alcance [B/C] | Con código respaldado | Pendientes | Combinaciones con pendientes |
|---|---:|---:|---:|
| V17: contextos localizados | 2.750 / 2.854 | 104 | 16 / 26 |
| Histórico 2019–2026 | 21.725 / 24.774 | 3.049 | 63 / 93 |

**C:** combinación = carrera UMAS + plan + sede + jornada. La asignación conserva
persona, expediente y período. Los 104 están dentro de los 3.049. Los 24 pendientes
de origen multiversión están dentro de los 104: no crear otra investigación paralela.
Las 3.520 posiciones sin contexto y los 23 documentos no RUT fuera del adaptador
son límites distintos; no equivalen a deserción, no se suman a estos pendientes
ni se descuentan de las bases o denominadores.

**C:** resuelto = código documental atribuible al expediente/período, o
correspondencia interna aprobada dentro de su alcance. Candidato único, igualdad
de totales y pendiente explicado no son cierres. Se mantienen separados documental,
interno, propuesta y aceptación SIES. **E:** el 100% es una meta; todavía no se
acredita que las fuentes distingan todas las versiones. No exigir el día exacto
si el período está respaldado, ni presumir continuidad porque no se encontró cambio.

## Fase 1/4 — Completar solo la evidencia faltante de V17

- **Hito 1/3 (C):** consultar las investigaciones y decisiones existentes de los
  104 pendientes. Separar evidencia lista, aprobación aplicable no incorporada,
  prueba nueva necesaria y bloqueo sin evidencia nueva. No suponer cuántos casos
  hay en cada categoría. Escribir una sola pregunta faltante por contexto y la
  fuente concreta que podría responderla. No volver a inventariar ni recalcular
  el universo para preparar esta lista.
- **Hito 2/3 (C/E):** resolver esas preguntas por grupos con evidencia común:
  63 discrepancias de jornada, 34 atribuciones a otra carrera/sede/institución,
  cinco de versión/plan y dos sin candidato/contexto. Priorizar evidencia ya lista
  y fuentes comunes. Leer cada fuente una vez para el lote, conservando código
  T1 de origen y código del contexto posterior como campos diferentes.
- **Hito 3/3 (C/D):** verificar cada resultado por expediente/período y registrar
  cierres con respaldo y autorización aplicable. Criterios nuevos se presentan con
  alcance, afectados y riesgos. Actualizar pendientes y requisito de cada excepción.

**Salida C/E:** diferencia trazable sobre V17; objetivo 104→0. Un grupo bloqueado
no impide investigar otro independiente, pero no se cuenta como resuelto.

## Fase 2/4 — Extender las soluciones al histórico, sin empezar de nuevo

- **Hito 1/3 (C):** por cada criterio respaldado, buscar solo entre pendientes
  históricos los contextos que cumplen sus condiciones. Los 21.725 ya resueltos
  no vuelven a investigación salvo una contradicción nueva.
- **Hito 2/3 (C/D/E):** validar los candidatos afectados con la evidencia existente.
  Una aprobación nominativa no se extiende a otras personas. Una regla nueva se
  prueba una vez por alcance contra casos documentados pertinentes, ocultando el
  código objetivo y controlando dependencia entre filas de la misma persona.
  Registrar errores y límites; no repetir todas las hipótesis históricas.
- **Hito 3/3 (C/E):** investigar grupos residuales solo cuando exista una fuente,
  variable o criterio nuevo que pueda distinguir versiones. Conservar diagnósticos
  previos de los demás y precisar qué dato o decisión falta. No repetir búsquedas
  agotadas ni interpretar un requisito pendiente como prueba de que el dato no existe.

**Salida C/E:** pendiente histórico actualizado, descontando cada cierre una vez;
objetivo 3.049→0 sobre 24.774 observaciones fijas. Reutilizar la matriz de requisitos
existente (2.650 + 202 + 94 + 51 + 32 + 19 + 1), sin reconstruirla.

## Fase 3/4 — Consolidar una edición y validar sus cambios

- **Hito 1/3 (C/D):** acumular resultados aprobados en una edición candidata,
  preservando v7. Mantener una bitácora y un checkpoint, sin crear nuevos informes,
  diccionarios o Excel por cada persona.
- **Hito 2/3 (C):** por lote comprobar observaciones modificadas, contextos
  relacionados que podrían verse afectados, unicidad, conflictos, aprobación y
  conciliación. Para una edición de entrega, contrastar globalmente las diferencias
  contra la línea base y comprobar consumidores. Adelantar QA integral si cambia
  lector, normalización, contrato o regla transversal; cambiar pocas filas no
  vuelve inocuo un cambio de lógica.
- **Hito 3/3 (C):** generar y recalcular una copia del Excel solo al preparar una
  entrega. Comparar bases, denominadores, fórmulas, gráficos y resultados afectados
  con V17. Explicar redistribuciones entre segmentos conservando totales; cambios
  de elegibilidad o tasas requieren escenario separado antes de adoptarlos.
  Distinguir apertura nativa de QA estructural y recálculo por otra herramienta.

**Salida C:** edición y Excel candidatos con cero cambios inesperados, pérdidas
o duplicados. Puede entregarse un avance parcial identificado como tal, sin esperar
a resolver todo el histórico y sin llamarlo 100%.

## Fase 4/4 — Publicar y conectar el servicio existente

- **Hito 1/3 (C):** preparar únicamente código, contratos, decisiones agregadas y
  QA que faltan en Git. Reutilizar la integración existente: no diseñar otra
  arquitectura ni copiar equivalencias a cada complemento.
- **Hito 2/3 (C/E):** con autorización aplicable y QA correcto, publicar la edición
  y conectar complementos/skills al mismo punto de consulta. Aprobar este plan no
  autoriza commit, push ni cambios remotos.
- **Hito 3/3 (C):** comprobar versión realmente publicada y una prueba breve de
  consumo desde cada entrada; conservar actualización, alerta y reversión.
  Si no hay acceso al servicio local desde un complemento, declarar ese límite.

**Salida C/E:** publicación y conexiones comprobadas. Puede prepararse en paralelo:
no necesita redescubrir códigos ni esperar el 100% histórico. La cobertura de
códigos y la publicación siguen siendo controles diferentes.

## 3. Reanudación, límites y ahorro de trabajo

**C:** cada avance comienza «Fase X/4 · Hito Y/3». La bitácora registra desde el
primer lote: evidencia/hash/hoja/fila, pregunta, regla/aprobación, resultado anterior
y nuevo, responsable, fecha/hora y próxima acción. Identificadores solo en la ruta
privada existente; checkpoint compartible agregado.

**C:** agrupar por regla o evidencia común, revisar hasta diez observaciones por
lote y conservar la trayectoria necesaria. Reutilizar la misma extracción de una
fuente/version entre lotes; verificar condiciones individuales, sin asignar una
versión por la sola coincidencia de totales del grupo.

**C:** no repetir fuente/hash + pregunta + método ya agotados sin novedad. No
releer manuales completos, pedir archivos inventariados, probar reglas aprobadas
desde cero, regenerar libros por lote ni duplicar adjudicaciones. Si cambia una
fuente o regla, invalidar solo los resultados dependientes; conservar el resto.

**C — Control:** pendientes iniciales − cierres respaldados + reaperturas =
pendientes finales dentro del mismo universo. Nuevos universos se informan aparte.
Meta completa: V17 2.854/2.854 e histórico 24.774/24.774, cero asignaciones ambiguas
adoptadas, QA correcto y consumidores sincronizados; interno y documental separados.

**B/C — Estado actual:** plan v2 preparado; QA anterior heredado, no repetido.
Siguiente: Fase 1/4 · Hito 1/3, consultar evidencia ya registrada de los 104.
Cero cierres nuevos; bases, denominadores, V17 y edición activa intactos.
Sin commit, push ni cambios remotos.
