# Diagnóstico de 2.317 personas y comparación de métodos

Cálculo local sobre V 6/privado V 3; sin nueva búsqueda histórica. Clasificación B/C: observaciones y cálculos; D: recomendaciones; E: controles no acreditados. No reglas oficiales nuevas.

## Qué ocurrió
Las 2.317 personas abarcan 38 códigos de carrera. Hay 64 personas en varias carreras, 382 en varios años y 7 en varias jornadas dentro del grupo. Por eso no se suman personas de las tablas por carrera/año/jornada. 4.973 observaciones no equivalen a 4.973 personas.

Categorías: 556 personas/1.760 observaciones con código distinto; 22/86 con posible atribución múltiple; 1.821/3.112 sin coincidencia anual; 2/15 sin DA exacto. Solapamientos: 7 personas entre atribución múltiple y sin anual; 77 entre sin anual y diferencia de propuesta; sin otros solapamientos. Unión 2.317 personas y 2.386 expedientes.

Corrección de interpretación: las 86 observaciones tienen exactamente UN código anual. La alerta proviene de atribución a identidad/expediente, no de códigos SIES contradictorios. No se ha probado que sean 86 errores ni que múltiples expedientes sean ilegítimos: pueden requerir secuencia de matrículas/periodos. No se borran ni reasignan automáticamente.

## Ausencia anual no es ausencia histórica
De las 3.112 observaciones: 1.472 tienen código de la misma familia en otro año/proceso; 261 solo otra familia; 1.379 ningún código completo localizado. Personas disjuntas, priorizando evidencia de misma familia: 696 + 109 + 1.016 = 1.821. Sin esa prioridad son 696 y 115 en las primeras dos categorías, con 6 personas compartidas.

Entre las 1.472 observaciones con evidencia de misma familia, 1.462 tienen matrícula en otra fecha, 946 avance y 511 titulación. Son grupos superpuestos. La búsqueda NO rechazó esa evidencia: el filtro anual la separó para no presentarla como matrícula contemporánea. No se ha probado todavía una regla temporal que la haga aplicable al año pendiente.

## Diferencias con propuesta dominante
De 1.760 observaciones discrepantes: 1.167 (306 personas) muestran versiones fuera del conjunto de candidatos original; 593 (262 personas) muestran una versión candidata distinta de la dominante. Los grupos de personas se superponen. Son contraejemplos a usar sin contexto una versión fija, no prueba de error de la fuente SIES. 1.151 de las 1.167 fuera de candidatos están en 2019–2021; 16 en 2022.

## Comparación idéntica, sin confundir cobertura y exactitud
Universo fijo: 24.774 observaciones. Propuesta dominante disponible: 23.183; código en cualquier fuente: 23.395; código misma familia en cualquier año: 23.134; código anual único con contexto DA: 21.561. Cada cifra responde una pregunta diferente; no se presentan como tasas de exactitud ni mejoras comparables.

En la intersección exacta de propuesta y código anual/contexto DA (20.064 observaciones), 18.304 concuerdan y 1.760 difieren. No es validación de plan vigente ni patrón de verdad independiente.

Sobre los 504 originales: antes 497/504, ahora 497/504, idénticos conjuntos de códigos. Sobre los mismos 508 expedientes: antes 500/508 misma familia, ahora 500/508, idénticos conjuntos. En sus 1.589 observaciones disponibles dentro del universo 504, antes 1.497 y ahora 1.497 con código anual; los 1.589 conjuntos son idénticos. Las 2 observaciones del privado inicial fuera de esas 504 personas se excluyen de ESTA comparación, no de los archivos. No disminuyó ni aumentó la cobertura en casos iguales. Ampliar a 5.901 no es deterioro.

Las 39 dimensiones con propuestas previas abarcan 5.456 personas/6.113 expedientes/23.183 observaciones: 18.304 confirman,1.760 difieren,3.020 sin anual,86 atribución múltiple,13 sin DA exacto. Tener propuesta de dimensión no acreditaba todas esas observaciones.

## Auditoría de reglas, columnas y filtros
1. Descubrimiento multiproceso: mismo inventario 38 y mismo lector exacto que recuperó 497/504; RUT/DV y código completo, sin filtrar primero año/familia. Tipos documentales R/1/RUT o columna de tipo ausente en históricos; no nombres/sexo/nacimiento. La ausencia de tipo es una limitación del histórico, no una verificación adicional.
2. Atribución anual V 6: filtro adicional explícito de proceso MATRICULA, MC_CAT_PERIODO o ANIO_INFORMADO igual al año PR, familia institución/sede/carrera/jornada y contexto DA del corte. Es una prueba específica de matrícula anual, NO la única vía posible de enlace contextual. No debe emplearse como descarte universal de avance/titulados.
3. Avance: Año carga/proceso y ANIO_INGRESO_CARRERA_ACTUAL no equivalen por sí solos a ANO/PERIODO de actividad PR. Se debe validar la relación proceso→periodo informado con documentación de esa carga. Titulados: fecha/periodo de obtención y código de título/terminal acreditan un evento; enlazar carrera/expediente puede ser posible, pero no equivale automáticamente a matrícula anual. Derivados de retención corroboran, no son evidencia independiente.
4. Sede/jornada/identidad/expediente: docs/fase_4_planes_asignaciones_umas.md punto 4 pide conservar contextos múltiples. La alerta V 6 de múltiples expedientes por persona/año/familia es cautela de atribución; NO regla oficial que invalide la matrícula. Revisar periodos y secuencia antes de declarar conflicto real.
5. Plan: PLAN_DE_ESTUDIO (PR) frente a PLAN_ESTUDIOS/MATRICULA_PLAN_ESTUDIOS (SIES). No se usó igualdad literal como filtro; tampoco se aplicó VIG=1, mínimo 3,90%,tipo o duración al código documental. El requisito de no retrotraer el plan del corte está documentado en puntos 5–7: puede ser etiqueta actual y no historial. Ese límite impide afirmar vigencia histórica, pero NO debe impedir registrar un código exacto ni añadir requisitos de duración a una relación documental explícita (docs/resultados_fase_b_equivalencias_historicas.md líneas 85–92).
6. Fuente: Publicados/Enviados se etiquetó por procedencia, no se comprobó aceptación individual. MU consolidada derivada se admite como base gobernada; precargas/borradores no se promueven a carga aceptada. Esto es límite de prueba, no ausencia de código.

## Método recomendado y qué cierra
Descubrimiento amplio primero → enlace documental por expediente/plan/contexto → resolución de conflictos → inferencia separada solo donde falte evidencia. Prioridad: registro trazable del proceso pertinente con su significado temporal acreditado; identidad y expediente exactos; plan explícito o puente documental de plan; otras apariciones como corroboración; derivados/borradores como indicios. No elegir arbitrariamente el más reciente ni la mayoría.

Ya acreditado: presencia de código histórico para 4.885/5.901 personas; código anual/contexto DA único para 21.561/24.774 observaciones; cobertura de ese último control en 12/63 dimensiones. No equivale a 12 cierres integrales de plan. La relación documental directa no exige 90% ni 3 personas.

Primero revisar las 1.760 diferencias (código existe); luego las 86 atribuciones múltiples con código único y las 15 sin DA; después validar temporalidad de las 1.472 observaciones con misma familia en otro año/proceso. Las 261 con otra familia requieren demostrar cambio de carrera/jornada, no transferencia automática. Las 1.379 sin código corresponden a 1.016 personas: requieren nueva fuente o rectificación, no una regla estadística que invente correspondencia.

No se ha ejecutado todavía una regla temporal alternativa para avance/titulados: su ganancia es no cuantificada. No se promete cierre del 38,10% ni se impone una vigencia imposible: exigir solo la evidencia necesaria para la afirmación concreta (código observado, enlace de expediente, o plan efectivo).

## Entregables y controles
CSV por carrera, año, jornada y combinación, causa por combinación y partición de sin anual. Diagnóstico JSON conserva cálculos. Excel agregado separado; libros finales y privados previos intactos. Sin fuentes, tasas, denominadores, canon, commit, push ni uploads modificados. Las personas de grupos se solapan; observaciones categorizadas sí se reconcilian.
