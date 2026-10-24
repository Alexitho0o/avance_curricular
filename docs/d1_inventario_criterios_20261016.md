# D1 — Inventario y criterios previos de cierre

Especificación previa. H1 concilia por identificador los universos B4/H5 y reglas
B5 K0, sin alterar agrupaciones. H2 fija semántica temporal y H3 criterios de
revisión. Se añaden scripts y pruebas aislados siguiendo el layout autorizado.
La consulta nueva no cambia resultados ni activa equivalencias.

Las filas de inventario conservan la fuente original y separan relaciones
observadas de candidaturas H5, cuyo ámbito es 2026. El registro agrupa prioridades
por contexto; no suma las 16 reglas problemáticas K0 a los 16 contextos múltiples.
Códigos y planes tendrán listas de contextos relacionados y causas de pendiente.
Las categorías pueden coexistir: el orden de revisión no descarta causas secundarias.

D1 no investiga aún las excepciones ni valida una nueva regla curricular.
Las decisiones de criterio son internas al análisis; no se presentan como
reglas oficiales SIES. No se requieren datos personales para construir este índice.

## H1 — Inventario conciliado

[Inventario completo](../data/cierre_d1/20261016/inventario.json): 141 códigos,
236 planes y 1.986 contextos, identificados por las claves originales. Las 2.363
filas son elementos de tres universos distintos, no carreras ni estudiantes.
Cada fila incluye fuente original, vínculos, causas, prioridad y referencias a
[criterios de revisión](../data/cierre_d1/20261016/criterios.json), que especifican
fuente necesaria, acción y condición de salida. Las causas son multietiqueta.

| Universo | Distribución conservada |
|---|---|
| Códigos SIES | 45 con evidencia B4, 60 solo candidatura H5, 36 sin relación UMAS observada |
| Planes UMAS | 62 con relación observada, 66 con actividad sin relación, 108 sin actividad observada |
| Contextos | 410 con destino único, 36 único con ambigüedad adicional, 16 múltiples, cuatro solo ambiguos, 1.520 sin evidencia |
| Reglas K0 | 197 corroboradas en reserva, 211 sin reserva, 15 conflictivas y una contradictoria |

Las 16 reglas K0 problemáticas remiten exactamente a los 16 contextos múltiples
B4. Se preparan **16 expedientes prioritarios únicos**, con ambos disparadores,
en la [cola D2](../data/cierre_d1/20261016/cola_prioridad_1.json). Esto no demuestra
una causa común: solo evita duplicar su investigación. Se conserva cada regla.

Se localizaron ocho contextos CILOG mediante su código, sin agruparlo con
Logística regular. Hay 916 contextos sin plan observado; dos códigos sin oferta
y ocho con primera oferta en el límite inferior 2010. Ninguna de estas ausencias
se interpreta como inexistencia histórica de la carrera o de la malla.

## H2 — Semántica y fuentes

Se registraron 12 entradas en la [matriz temporal](../data/cierre_d1/20261016/semantica_temporal.json).
Estas separan año de oferta, inicio formal, primera oferta observada, ingreso
original, primera observación de carrera, presencia, períodos, plan y vigencia.

Ficha de fuente formal: `sies-glosario-oferta`,
`Glosario_Oferta_Academica_2010_al_2026_SIES_WEB_EE-1.pdf`, definición de campos de
oferta, no microdatos ni prueba de asignación curricular. Se leyó el derivado por
página: Año y Código Único en página 1, Año Inicio en página 2, Vigencia en página
4 y disponibilidad anual en páginas 5–6. Se conservan [PDF](../data/cierre_d1/20261016/fuentes/glosario_oferta_2010_2026.pdf)
y [texto completo](../data/cierre_d1/20261016/fuentes/glosario_oferta_2010_2026.md)
del recurso documental de la habilidad consultar-fuentes-ipss, con hashes.
Edición declarada 2010–2026; no se verificó vigencia normativa posterior ni se
utilizó una metodología posterior para decidir casos históricos.

Vigencia distingue declaración con nuevos estudiantes de declaración solo con
antiguos. D2 deberá contrastarla por código/año y episodio; este campo no identifica
por sí solo la versión que corresponde a una persona. El año mínimo de oferta
responde a la regla interna de este proyecto y no reemplaza el Año Inicio formal.

Fuentes de análisis: B4 y B5, cortes 20261016, listas completas leídas y manifiestos
verificados; inicios por código 20261015; contrato de presencia anual 20261016.
Son compatibles para inventariar los pendientes ya construidos. D1 no vuelve a
leer los microdatos ni certifica el corte de cada extracto externo. El registro
conserva esta limitación y los localizadores en cada campo.

## H3 — Criterios fijados antes de D2

La evidencia se evalúa en dos ejes separados: **respaldo del vínculo** y **alcance
curricular/temporal**. No se sube de nivel por acumular filas del mismo reporte.

| Evidencia | Qué permite concluir | Condición que sigue pendiente |
|---|---|---|
| Candidatura H5 o inferencia MRUN | Vínculo para investigar, con ámbito y grado de incertidumbre | Confirmar atribución académica; no certifica identidad |
| Reporte institucional atribuido a una carrera concreta | Código reportado para ese episodio/corte | Unicidad de atribución, coherencia de sede/jornada y delimitación temporal |
| Corroboración B5 con personas reservadas | Consistencia observacional dentro de la clave evaluada | No es validación independiente de la fuente ni certificación de malla |
| Plan observado en notas | Presencia de un identificador curricular en el contexto | Probar a qué episodio aplica y desde cuándo |
| Documento curricular o historial equivalente con fecha y programa | Sustento para delimitar malla y vigencia | Contrastar con código SIES y excepciones del mismo ámbito |

Para sostener **una relación de programa**, se requiere atribución no ambigua al
programa concreto, código SIES observado en la fuente correspondiente y ámbito
explícito de año/sede/jornada, conservando posibles contradicciones. Si un campo
histórico no está acreditado, el alcance queda limitado al contexto del extracto.

Para sostener **una relación de malla**, se necesita además plan identificable,
evidencia de su vigencia en ese episodio y relación temporal documentada con el
código SIES. Tener un plan en el nombre o en notas no basta; varias mallas pueden
compartir un código. Sin plan, la conclusión permanece a nivel programa/contexto.

Conflictos, ambigüedad de atribución, datos posteriores al contexto o diferencias
de universo no explicadas impiden presentar una selección unívoca como resuelta.
D2 podrá concluir que el caso no es determinable con las fuentes disponibles.
No se elige por frecuencia, V mayor, similitud nominal, igualdad artificial de
totales ni por el modelo que produzca el resultado deseado. Tampoco se exige una
tabla oficial RUT–MRUN inexistente para investigar relaciones académicas.

Estos son criterios internos de evaluación, no nuevas reglas oficiales SIES.
Cumplirlos no activa cargas: la propuesta de uso operativo corresponde a una
etapa posterior. La reserva B5 ya inspeccionada servirá como regresión, no como
validación nueva de reglas ajustadas a partir de sus resultados.

## Orden de revisión y cierre D1

1. D2 H4: 16 expedientes únicos conflictivos/múltiples.
2. D2 H5: ocho contextos CILOG, articulados con la muestra ya existente; distinguir
   ingreso al técnico, ingreso a continuidad y primera observación disponible.
3. D2 H6: reglas sin reserva, ambigüedades y vigencia de planes observados;
   después, relaciones ausentes y fuentes históricas fuera de cobertura.

Las prioridades se registran en cada elemento. Las filas de código/plan son
índices de cobertura, no expedientes que se deban sumar a los contextos. Las
causas comunes permiten revisar una fuente una sola vez para varios elementos.
El esfuerzo de D2 se planifica primero para 16 expedientes y ocho contextos CILOG;
la búsqueda de fuentes se acota por categoría, sin prometer resolver todo por volumen.

H1, H2 y H3 completados. Pasaron cinco pruebas de integridad, conciliación,
vínculos bidireccionales, deduplicación y límites de inferencia. Se comprobó
reproducción idéntica de las tres salidas generadas. Se preservaron las 137
referencias y las entregas C1/C2; no se promovieron reglas ni se modificó Excel.

Reproducción: `python3 scripts/construir_inventario_d1.py`.
Validación: `python3 -m unittest discover -s tests -p 'test_inventario_d1.py' -v`.
Resultados: [resumen](../data/cierre_d1/20261016/resumen.json),
[manifiesto](../data/cierre_d1/20261016/manifest.json) y
[QA](../data/cierre_d1/20261016/qa.json).

Siguiente fase: D2, investigación de excepciones. Al cerrar cada fase se mantendrá
la frase solicitada por el usuario: «lista para que comience la fase siguiente».
