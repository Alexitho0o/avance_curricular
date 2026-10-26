# Auditoría metodológica y experimento del puente UMAS–SIES

Solicitud: auditar métodos previos y probar otra formulación, sin modificar bases, denominadores ni diccionario activo. Proceso: conciliación histórica personal/anual y seguimiento T1/T2/T3 IPSS162. Datos observados 2019–2026; cobertura histórica mayor solo donde se compruebe.

Hipótesis C: un diccionario por carrera interna+sede+jornada+plan+año puede predecir el código anual de expedientes no utilizados al construirlo. Contrastar contra carrera+sede+jornada+año y añadir ingreso DA como variable exploratoria (no ingreso original acreditado). La hipótesis queda refutada como regla universal si hay conflictos o predicciones equivocadas.

Validación: usar únicamente etiquetas documentales anuales del diccionario v7; colapsar repetición por períodos al contexto persona+CODCLI+plan+carrera+sede+jornada+año. Mantener conflictos explícitos, nunca elegir primero. Cinco particiones deterministas por persona, sin etiquetas de esa persona en entrenamiento. Medir cobertura, aciertos, errores, abstenciones, precisión condicionada y personas con error; desglose por año y versiones múltiples. Separar prueba de transferencia temporal con otros años del mismo expediente de generalización a otra persona. No validar código trimestral con etiquetas anuales repetidas.

Evaluar correspondencias unánimes; mínimo tres personas como variante declarada, no como aprobación. Prueba adicional prospectiva anual: aprender solo años anteriores. Mostrar rango de resultados por partición; no interpretar precisión observada como garantía ni imponer un umbral aprobado inexistente.

Diagnóstico de identificabilidad C: más de un código con idénticas variables demuestra que esas variables no bastan en los datos observados. Totales se usan como restricciones únicamente si universo, grano, año, vigencia y cobertura son comparables. Demostrar con ejemplo sintético que conservar totales no identifica personas cuando existen permutaciones equivalentes.

Salidas: script y resultados agregados, informe de métodos/comparación y checkpoint. Nada de identificadores en Git ni servicios externos. Fuentes solo lectura; hash y rama/HEAD antes/después. Sin adjudicar códigos, tocar Excel, commit o push.
