# B4 — Matriz académica de evidencia histórica

Especificación previa, 2026-10-16. Continúa las agrupaciones existentes y no
promueve equivalencias ni modifica el maestro H5, Excel o cargas operativas.

## Grano y evidencia

Contexto: carrera UMAS, sede, jornada, año observado, ingreso original declarado,
primera observación disponible en esa carrera y conjunto de planes observados
ese año. La primera observación se calcula por documento y carrera, conservando
expedientes distintos, sin llamarla ingreso efectivo ni año cero. Los planes
provienen de notas del mismo expediente/carrera/año verificadas por documento;
la etiqueta PLAN_DE_ESTUDIO no acredita asignación histórica efectiva de malla.

Relacionar por separado: (a) código informado en reporte institucional, unido
por documento/año y filtrado por familias existentes; (b) código propuesto por
enlace MRUN condicional que pasa la capa demográfica. Ninguno alimenta al otro.
Reportes y MRUN pueden derivar del mismo proceso: no contar su coincidencia como
dos pruebas independientes. Conservar carreras compartidas, códigos múltiples,
contradicciones y fuente desconocida. No deducir versión de ordinal o año del plan.

La evidencia documental solo es no ambigua para un programa si, entre todos los
expedientes de esa persona, la misma familia SIES no corresponde a otro código
UMAS/sede/jornada distinto. Duplicados del mismo programa no son programas nuevos.
Cada contexto mantiene conteos de personas, expedientes y observaciones separados.

Añadir oferta exacta anual, primera oferta del código, vigencia, duración, tipo y
nombre oficial, sin heredar atributos de otro año. Conservar todos los 141 códigos,
236 planes y 513 candidatos iniciales en tablas de cobertura incluso sin actividad.
Las evidencias personales de enlace de esta edición cubren 2018/2019/2020/2022;
actividad UMAS 2019–2026 no implica que se hayan enlazado personas en todos esos años.

## Estados de contexto

SIN_EVIDENCIA: ningún código respaldado ni candidato observable del cruce.
SOLO_EVIDENCIA_AMBIGUA: hay códigos, pero asignación al programa es ambigua.
DESTINO_UNICO_OBSERVADO: todas las evidencias admisibles señalan un código.
DESTINO_UNICO_CON_EVIDENCIA_AMBIGUA: un destino admisible, pero coexisten
asignaciones ambiguas que impiden tratar el contexto como íntegramente resuelto.
MULTIPLES_DESTINOS: varias versiones/códigos admisibles para la clave disponible.
CONTRADICCION_ENTRE_EVIDENCIAS: conjuntos documental e inferido disjuntos para
una misma observación. Destino único no equivale a regla efectiva: B5 debe validar
alcance temporal y contexto, incluso si hay una sola persona.

## Cierre

Matriz agregada reproducible sin identificadores; cobertura completa del maestro;
conteos y ejemplos; fuentes verificadas; paridad de 2.418 propuestas iniciales
antes de aplicar puerta; prueba de clasificación; preservación de 137 referencias
congeladas y sectores/Excel editados. B4 cierra la organización de evidencia,
no la selección definitiva de versiones ni la identidad de estudiantes.

## Resultado de B4

La matriz contiene 1.986 contextos académicos construidos desde 20.168
observaciones UMAS de expediente/año. Los contextos conservan el año de ingreso
original y la primera observación en esa carrera por separado. No se interpreta
esta última como inicio efectivo; puede provenir de ANOMATRICULA sin actividad.
Se conservaron 141 códigos SIES, 236 planes UMAS y 513 candidaturas H5.

| Estado del contexto | Cantidad |
|---|---:|
| Destino único observado, sin asignaciones ambiguas adicionales | 410 |
| Destino único observado, pero con evidencia ambigua adicional | 36 |
| Varios destinos observados | 16 |
| Solo evidencia ambigua | 4 |
| Sin evidencia de relación en esta edición | 1.520 |
| Total | 1.986 |

No se detectaron conjuntos documental/inferido disjuntos en una misma observación
admisible; esto NO constituye validación independiente. Los contextos con varios
destinos pueden reflejar varias versiones efectivas entre estudiantes y no son
por sí mismos errores. Las 36 filas con un destino y evidencia ambigua no se
mezclan con las 410 sin esa incidencia.

De los 1.520 contextos sin relación observada, 153 corresponden a los cuatro
años con cruce personal disponible y 1.367 están fuera de esa cobertura. No se
presentan estos últimos como fracaso del enlace ni como ausencia de la carrera.
La actividad por sí sola no determina el Código Único correspondiente.

### Cobertura del inventario

| Universo | Resultado |
|---|---|
| 141 códigos SIES | 45 aparecen en evidencia B4 (incluida la ambigua); 60 conservan candidaturas H5 sin evidencia B4 y 36 no tienen relación UMAS observada. |
| 236 planes UMAS | 62 tienen alguna relación observada; 66 tienen actividad sin relación B4; 108 no tienen actividad verificada en esta reconstrucción. |
| 513 candidaturas H5 | 103 tienen su código observado en algún contexto; 88 tienen otros códigos observados y 322 no disponen de contraste. |

Los 103 candidatos no quedan aprobados ni habilitados para resolver. H5 mantiene
su ámbito candidato 2026; una observación en 2019 no convierte automáticamente
esa candidatura en regla de 2019 ni valida 2026. Los otros 88 tampoco se descartan:
pueden corresponder a otros períodos, cohortes o versiones no observados.
Los 108 planes sin actividad se conservan, sin declarar cierre o inexistencia.

Los contextos incluyen las candidaturas H5 por separado, para que un programa
sin enlace personal siga siendo revisable. El archivo de oferta anual contiene
las 747 filas del maestro, con nombre, modalidad, tipo, duración y vigencia.
Para cada relación observada se adjunta la oferta de su año exacto y la primera
oferta del Código Único. Si no hay oferta anual, queda vacío; no se hereda 2026.

La matriz preserva las agrupaciones previas. Cuando una persona tiene varios
programas UMAS distintos compatibles con la misma familia SIES, se retiene la
ambigüedad aunque uno no tenga actividad anual. Es una guarda conservadora:
una trayectoria posterior no prueba pertenencia al programa anterior. B5 podrá
examinar la temporalidad sin alterar silenciosamente la agrupación.

### Ejemplos verificables

**B4-00355 — IECIRE, sede RE, jornada D, año 2019.** Una persona con plan
observado IECIRE20191 aporta I162S2C1J1V1 en reporte. Es un destino observado;
una sola persona no acredita toda la vigencia de esa malla ni su aplicabilidad
a otra cohorte.

**B4-00362 — IECIRE, RE, D, 2019, ingreso original 2018.** Tres personas comparten
la primera observación disponible en carrera (2019) y el plan IECIRE20191.
Los reportes y propuestas MRUN contienen I162S2C1J1V1 e I162S2C1J1V2. Por tanto,
esa clave no basta para seleccionar una única versión. B5 debe revisar el
semestre y el ingreso a la carrera actual, contexto de matrícula y semántica de
la etiqueta de plan, sin elegir por V mayor. No se declara que dos versiones
constituyan una contradicción entre las fuentes.

**B4-00533 — IECIREOL, año 2019.** Hay evidencia de código, pero la atribución a
programa UMAS es ambigua. El código permanece visible en la columna de
asignación ambigua, sin convertirlo en correspondencia resuelta.

Los ejemplos no identifican estudiantes. Los conteos de personas son internos a
cada contexto; no deben sumarse entre contextos, fuentes o versiones. Una persona
puede cursar más de una carrera y aparecer en varios años.

## Cierre y siguiente hito

B4 queda **completado como matriz de evidencia**, sin promover reglas efectivas.
La cobertura está cuantificada y no se omitieron carreras o planes inactivos.
El siguiente hito es B5: diseñar y contrastar reglas por contexto con estados de
evidencia explícitos, priorizando los 410 contextos de destino único observado y
examinando las ambigüedades/los 16 contextos con destinos múltiples. También se
mantiene la revisión de los 153 contextos sin evidencia dentro de años cubiertos.
No se exige resolver cada identidad antes de avanzar en una relación académica.

Pasaron tres pruebas de clasificación/contradicciones. Se reprodujeron las 2.418
propuestas iniciales previas a la puerta demográfica; se conciliaron todas las
observaciones, cobertura y claves únicas. Se verificaron fuentes por hash,
137 referencias congeladas y el Excel editado por Alexi. No se modificaron maestro,
sectores, consultas operativas ni resultados previos. No se exportaron datos
personales. El manifiesto registra las fuentes externas y código; no equivale a
respaldo íntegro ni publicación remota de esos archivos.

```sh
python3 -m unittest discover -s tests -p test_matriz_academica.py
python3 scripts/construir_matriz_academica_b4.py
```

[Resumen](../data/matriz_academica_b4/20261016/resumen.json),
[matriz](../data/matriz_academica_b4/20261016/matriz_contextos.json),
[cobertura SIES](../data/matriz_academica_b4/20261016/cobertura_sies.json),
[cobertura de planes](../data/matriz_academica_b4/20261016/cobertura_planes.json),
[contraste de candidatos](../data/matriz_academica_b4/20261016/contraste_513_candidatos.json),
[oferta anual](../data/matriz_academica_b4/20261016/oferta_anual_referencia.json).

### Cobertura dentro de cada contexto

Cada fila informa personas totales y personas con código admisible, además de
observaciones con código, solo ambiguas y sin código. Un destino único entre
las evidencias disponibles no significa que todas las personas del contexto
estén enlazadas. B5 debe examinar esa cobertura antes de generalizar una regla.

Control adicional: de los 410 contextos con destino único sin ambigüedad
adicional, 336 tienen código admisible para todas sus personas observadas y 74
solo para parte de ellas. Ni siquiera la cobertura completa certifica por sí sola
la asignación histórica del plan; sí permite priorizar la revisión B5.
