# Contraste trazable de las 63 dimensiones — V6

Se aplica el mismo lector multiproceso y el mismo inventario de 38 archivos a todo el universo PR: 5.901 personas, 6.622 expedientes y 24.774 observaciones. No es comparable por resta con el universo previo de 504 personas. Se verifica que las 504 conservan exactamente su resultado 497/7.

## Resultado
4.885 personas aparecen con código completo, 1.016 no localizadas dentro de las fuentes revisadas. 49.225 evidencias conservadas en privado. Las observaciones se particionan en 18.304 que confirman el código propuesto, 1.760 que difieren, 1.497 con código único sin propuesta previa, 86 con contradicción/atribución múltiple, 3.112 sin evidencia anual aplicable y 15 con código anual sin contexto DA exacto. Suma 24.774.

Las 1.760 diferencias afectan 12 dimensiones; no se selecciona arbitrariamente una versión ni se cambia el canon. Las 86 contradicciones/atribuciones múltiples afectan 10 dimensiones. Antes/después y fuente/hoja/fila están en privado; tabla por dimensión agregada en DIMENSIONES_63.csv.

12 dimensiones tienen todas sus observaciones con código anual único y contexto DA exacto: IECIRE/J1, IPRE/J4, NTCCRE/J2 (3 propuestas anteriores), IETMRE/J1, NAUTRE/J2, NECIRE/J2, NETMRE/J2, NICCREOL/J4, NICIRE/J2, NINFREOL/J4, NITMRE/J2, TCRE/J2 (9 pendientes anteriores). No se exige n3/90 para ese hecho documental. NITMRE/J2 conserva conflicto de plan catalogado NCONRE: recuperar código anual no resuelve ese conflicto. Las otras condiciones del catálogo no se confunden con recuperar un código observado.

## Regla y límite
Identidad exacta primero, cualquier año/proceso; después familia institución/sede/carrera/jornada y año MU explícito. Se comprueba expediente en DA del corte y ambigüedad de identidad/expediente; no se supone estabilidad histórica del corte. Avance: año de carga/proceso no se convierte a académico sin regla; titulados no acredita matrícula contemporánea; derivados de retención no son carga independiente. Precargas/borradores se etiquetan y no se promueven como cargas aceptadas.

El bloqueo restante para atribuir el plan vigente no es n3/90 ni una aprobación hipotética: docs/fase_4_planes_asignaciones_umas.md puntos5–7 explicita que PLAN_DE_ESTUDIO en notas puede ser etiqueta del corte. Falta historial de asignación plan por matrícula/periodo o linaje que certifique esa semántica. No se acredita cierre integral de plan para ninguna dimensión con esta prueba; no se afirma falsedad de los vínculos. 24/63=38,10% se conserva como línea base original. 12/63 es nueva cobertura de código observacional, con definición distinta a 8/63 anterior; no reducción comparable de brecha de plan.

## QA y entregas
SQLite verifica independientemente los conjuntos de código anual de 24.774 observaciones usando proyecciones; no segunda lectura de todos los originales. Hashes de fuentes verificados por lector reutilizado. Privado V3 fuera de Git: todas las filas DA pertinentes (13.184), 67 columnas originales por fuente, contexto/antes/después y enlaces. Agregado V6 conserva tasas/denominadores y 13 gráficos, discrepancia T3 documentada. Sin commit, push, uploads ni cambio de rama. Estado PENDIENTE_APROBACION_GOBERNANZA; recuperación descriptiva no altera canon.
