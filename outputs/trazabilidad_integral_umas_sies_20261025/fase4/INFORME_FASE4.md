# Fase 4/6 — Excel trazable V19

**D — Alcance autorizado:** recuperar el libro funcional reutilizando las fases anteriores. Sin cambios de bases, denominadores, diccionario ni nuevas adjudicaciones. Sin commit/push.

**B/C — Entrega local:** `/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V19_TRAZABLE.xlsx`.
SHA-256: `daae975e42698dfb63bb3877e63bd8b7bdc499c50da05092d21772038ef457ee`.
Copia restringida idéntica: `/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V19_TRAZABLE.xlsx`.
Ambas están fuera de Git; contienen el detalle individual de la maqueta recuperada. El manifiesto no publica esas bases.

## Hito 1/3 — Maqueta y correcciones

**B/C:** se recuperaron las cinco hojas individuales originales —9,11,20,24,25 por su nombre visible— y las fórmulas históricas que la edición agregada había fijado. Se preservaron las fórmulas ya vigentes de V18 y las correcciones V14–V18. El resultado contiene 57 hojas, 237,885 fórmulas XML, 13 gráficos y 37 tablas.

**C:** el ensamblado conserva los dibujos/gráficos como partes originales idénticas. No importa/exporta toda la maqueta a un motor que pueda reconstruir esos objetos. Las nuevas hojas y fórmulas se crearon y recalcularon con Artifact Tool; luego se integraron sin reemplazar los estilos anteriores. Se mantuvo la reparación de estilos de V15.

**B/C/D:** valores vigentes conservados: actividad T2-2025=611/1150; actividad T3-2025=546/1150; matrícula T3-2025=1023/1150; T3-2026 grupo1=1360/1467; T2-2026=462/528 matrículas; conjunto2026=2290/2519. No son indicadores intercambiables. Ninguna cifra numérica previa de los resúmenes cambió en el archivo guardado.

## Hito 2/3 — Detalle y fórmulas conectados

**B/C:** hoja56_Vista_T1_T2_T3 integra la vista validada de fase3: 6374 filas que conservan6358 posiciones y2854 contextos. Se incluyen3520 posiciones sin contexto. Cuenta posición impide duplicar el padrón cuando hay más de un expediente; Cuenta contexto identifica la unidad del diccionario.

**C:** hoja53 columnas F/K/M ahora calculan población de origen y posiciones con/sin contexto desde56 mediante SUMIFS. Hoja54 columna N cuenta las221 combinaciones desde56 mediante COUNTIF. Hoja52 sigue consumiendo53/54. Hoja57 presenta cobertura y pendientes con fórmulas sobre56. Se probaron654 conteos de53 y221 grupos de54 contra V18, sin diferencias.

**B/C/D/E:** permanecen2718 contextos con mismo código,37 con otro código ya respaldado y99 pendientes;24 de esos99 pertenecen al foco multiversión. Se distinguen2742documentales,13internos aprobados y99pendientes. No se resuelve ningún pendiente nuevo ni se altera una tasa por falta de versión.

**C/E — Límite explícito:** la vista56 es un derivado materializado de la consulta al diccionario, con fuente/hoja/fila, regla y pendiente; se actualiza reejecutando la preparación, no consultando GitHub desde Excel. Las fuentes y ciertos numeradores/denominadores materializados de53 G/H siguen teniendo script y evidencia; no se presentan falsamente como fórmulas individuales. El avance de cobertura del diccionario no cambia el numerador de retención.

## Hito 3/3 — Guía, navegación y QA

**C:** guía27 reconstruida para57 hojas, con enlaces, rol, contenido, entradas, tipo de cálculo y privacidad. Se distinguen las auditorías históricas29–51 del estado vigente52–57. Portada, hoja18 y resumen52 incorporan navegación al detalle o al resumen actual. Se corrigieron las notas heredadas de104pendientes y v7activo: ahora99 y v8, coherentes con el descriptor.

**E — Pendientes visibles:**99 códigos (24multiversión incluidos),3520 posiciones sin contexto,66 renuncias sin nómina individual, alcance545 frente a ingreso exclusivo2026-3 y diferencias de calendario. No se suman como una misma brecha y no equivalen a desertores.

**C — QA:** 28/28 controles estructurales y de conservación correctos. Todos los XML parseables; relaciones con destinos existentes; tablas con nombres/IDs únicos; originales protegidos por hash; fórmulas previas y cifras históricas conservadas. Se verificó la dependencia en Artifact Tool cambiando temporalmente un pendiente a interno:13/99→14/98→13/99; el estado original se restauró antes de guardar. La revisión visual del suplemento se registra en el manifiesto.

**E — Próxima puerta:** falta la fase5 de conciliación integral y prueba de apertura/recálculo de todo el libro en Excel nativo, incluidos filtros conectados. El QA de este paso no certifica esa apertura ni que todas las cachés históricas se hayan recalculado. No se declara entrega definitiva ni cobertura100%.

**B/C — Git:** rama `feature/ire-2026`; HEAD antes/después `8e2fb85bb8703758d6878681c9e2a29016e60c63`. El cambio previo de PROYECTO_IPSS.json sigue intacto; no hubo staging, commit ni push. Los archivos de esta fase están locales, no publicados.
