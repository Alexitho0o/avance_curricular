# Fase 3 — Reconstrucción de oferta histórica SIES

Autorización del usuario: continuar la fase 3 el 2026-10-15.
Esta especificación precede a la implementación del auxiliar de reconstrucción.

## Contrato H3

Reconstruir, para la institución 162, las versiones y atributos de la oferta
histórica, incluidos los códigos sin matrícula observada. La fuente disponible
cubre 2010–2026; el objetivo 2007–2026 conserva una brecha explícita para
2007–2009 mientras no exista oferta completa verificable. MRUN no rellena esa
brecha: una matrícula prueba observación, no integridad de la oferta.

Se utiliza el XLSX nacional SIES 2010–2026, su extracción institucional TSV,
el resumen académico anual de fase 2 y el archivo `oferta 2026.xlsx` indicado
por el usuario. Todos se fijan mediante SHA-256. El TSV se contrasta contra
los 69 campos originales, filas y hoja del XLSX; se verifica también que
incluya todas las filas de institución 162. El resumen MRUN se valida contra
el manifiesto de fase 2. No se leen ni exportan identidades personales.

## Identidad, tiempo y comparación

1. Clave anual: año de oferta + Código Único literal. Familia moderna:
   institución + sede + carrera + jornada; VERSION es un componente informado,
   no una numeración curricular reconstruida. Ninguna regla elige V máxima,
   primera fila o primera versión observada para asignar una malla.
2. Se preservan nombres literales por año y el nombre literal de oferta 2026
   en una columna separada. No se añaden modalidad, jornada ni continuidad al
   nombre. No se sustituye un nombre histórico por el actual. La publicación
   consolidada puede armonizar atributos históricos: no se afirma que cada
   campo sea copia literal de la edición publicada originalmente ese año.
3. Primera/última aparición y ausencia en un corte describen esta fuente;
   no certifican creación, cierre, retirada formal ni fechas de vigencia UMAS.
   VIGENCIA «sin estudiantes nuevos» sigue siendo vigente. La ausencia de
   matrícula tampoco significa ausencia de oferta o de plan.
4. ANO_INICIO declarado se conserva por código y año, separado del primer año
   observado. El glosario histórico lo define para carrera/programa en sede;
   el instructivo específico 2026 lo define para el código completo. Se
   conserva esta diferencia: no se convierte retrospectivamente en fecha
   efectiva de una malla o regla para seleccionar V.
5. El cruce con MRUN exige el mismo año y Código Único. Los campos compartidos
   se comparan mediante correspondencias explícitas; vacíos no equivalen a
   contradicción. Jornada y modalidad siguen separadas. VIGENCIA usa equivalencia
   textual «alumnos/estudiantes» documentada. Los valores originales permanecen.
6. Se conserva la unión de ambos universos, incluso los códigos heredados MRUN
   no descomponibles. Se distinguen ausencia fuera de cobertura de oferta,
   ausencia dentro de cobertura y oferta sin matrícula en este extracto.
7. Los cambios bajo un mismo Código Único son cambios de atributos publicados;
   no se clasifican automáticamente como reforma de malla. La coexistencia de
   V demuestra variantes simultáneas, sin establecer equivalencia UMAS.
8. La oferta 2026 se coteja contra el corte histórico 2026 mediante sus 15
   campos, con diccionarios explícitos. Las codificaciones de nivel se interpretan
   dentro de su propio esquema; no se extrapolan números de otros instructivos.

## Entregables y aceptación

El auxiliar `scripts/reconstruir_oferta_historica_sies.py` y sus pruebas viven
en las carpetas operativas existentes por la misma justificación de las fases
1 y 2: no importar ni modificar motores oficiales. Salida en
`data/versiones_historicas_sies_umas/fase_3_20261015/`:

- Oferta anual completa con localizadores originales y huellas en manifiesto.
- Historia por código, familias/versiones, coexistencias y cambios de atributos.
- Cobertura conjunta con MRUN, comparación anual y diferencias/ausencias.
- Cotejo de oferta 2026, ejemplos académicos y resumen de límites.
- Verificación original/extracción, auditoría independiente y búsqueda de cobertura.

Controles: claves únicas, componentes coherentes, preservación del universo,
comparaciones sin cruce entre años, ausencia distinta de contradicción,
conservación de variantes sin matrícula y reproducción idéntica. Se rechaza
sobrescribir resultados distintos y toda fuente que no coincida con su hash.
La reconstrucción comprobada de 2010–2026 puede cerrarse con cobertura parcial
explícita del objetivo 2007–2026; no se declarará oferta completa para esos
20 años si persiste la brecha. Los libros Excel, puentes y motores quedan
fuera de los cambios de esta fase. UMAS corresponde a fase 4 y las reglas de
equivalencia a fase 5.

## Resultado de la reconstrucción

Se verificaron las 396.003 filas nacionales más encabezado del XLSX: exactamente
747 corresponden a la institución 162, ninguna quedó fuera del TSV y sus 69
campos coinciden literalmente. Las claves año + Código Único son únicas.
Los hashes originales se conservan. El nombre del directorio contenedor
`oferta_academica_2027` no cambia el período 2010–2026 del archivo utilizado.

| Unidad | Resultado |
|---|---:|
| Filas de oferta (código-año), 2010–2026 | 747 |
| Códigos de oferta distintos | 139 |
| Familias institución/sede/carrera/jornada | 100 |
| Familias con varias versiones | 31 |
| Grupos familia-año con versiones coexistentes | 167 |
| Códigos presentes tanto en oferta como en MRUN | 104 |
| Códigos de oferta sin observación en este MRUN | 35 |
| Códigos heredados solo en MRUN | 2 |
| Unión de códigos de ambas fuentes | 141 |

Los 35 códigos sin MRUN corresponden a 21 de pregrado y 14 de postítulo.
No se declara que nunca tuvieron estudiantes: es ausencia en el extracto
revisado. Se conservan también los 15 códigos históricos sin oferta observada
en 2026. Ausencia del corte no acredita resolución formal de cierre.

El cruce anual encuentra 452 claves compartidas y 295 claves de oferta sin
matrícula del mismo año. No hay claves MRUN sin oferta dentro de 2010–2026.
Las 20 claves MRUN no emparejadas corresponden a 2007–2009, fuera de cobertura;
los dos códigos heredados `I162M2008N1` e `I162M2008N3` se conservan literales.

En las 452 claves compartidas se compararon 12 atributos, con 5.424 resultados:
4.964 iguales literalmente, 403 iguales tras normalizar vigencia, 49 sin
vigencia en MRUN y 8 sin modalidad en ambas fuentes (2010). No hay valores
contradictorios entre campos informados. La ausencia estructural de modalidad
2010 no se rellena desde jornada ni desde años posteriores.

El archivo del usuario `oferta 2026.xlsx` coincide con las 124 claves del
histórico 2026. Sus 15 campos producen 1.860 coincidencias al traducir las
categorías con el esquema propio del consolidado histórico. Nombre de carrera
se compara literalmente, sin agregar continuidad, jornada o modalidad.
Esta comprobación no valida una carga CFT/IP: el archivo usa Nivel Global
1/3, mientras el instructivo específico de carga 2026 usa 1/2.

### Qué demuestra sobre versiones

Las 100 familias incluyen V1 en su primer año de oferta observada, pero 10
ya incluyen varias versiones ese mismo año. Esta fuente es compatible con V1
como valor inicial; no demuestra que las siguientes V sean reformas sucesivas
de una única malla. El glosario admite variantes por contenidos y otros atributos.

| Carrera literal / familia | Evidencia de oferta | Interpretación para el cruce |
|---|---|---|
| NATUROPATIA / `I162S2C90J2` | V1 en 2025–2026, continuidad, 4 semestres, sin MRUN; V2 desde 2026, regular, 8 semestres, con MRUN. | MRUN por sí solo omite una versión que sí está en oferta. |
| INGENIERIA EN LOGISTICA / `I162S2C77J4` | V1 desde 2024, regular, 8 semestres; V2 desde 2025, continuidad, 4. Ambas declaran inicio 2024. | El inicio declarado no identifica de forma única V; las variantes coexisten. |
| INGENIERIA EN CIBERSEGURIDAD / `I162S2C46J2` | V1, V2 y V3 ya están en oferta 2019: regular 8, continuidad 5 y continuidad 4 semestres. | No asignar versiones ordenando exclusivamente años de inicio. |
| TECNICO EN ANALISIS DE SISTEMAS / `I162S2C35J4V1` | 5 semestres en 2017–2018; 6 desde 2019, conservando el mismo código y V1. | Un cambio de atributo publicado no implica necesariamente cambio de V; tampoco acredita por sí solo reforma curricular. |

La historia conserva 608 pares de observaciones de un mismo código con algún
atributo distinto; este conteo incluye aranceles, vacíos y categorías disponibles
solo desde ciertos años. No equivale a 608 cambios curriculares. ANO_INICIO
cambia en 10 códigos si se incluye cero; cinco tienen más de un año no cero.
Las ocho filas de oferta 2011 con inicio `0` quedan como valor sin año, nunca
como fecha. Los 188 registros con inicio anterior a la primera aparición se
informan como relación entre fechas declaradas/observadas, sin corregirlas.

### Cobertura pendiente y semántica de fuentes

No se localizó oferta completa 2007–2009 en la búsqueda acotada documentada.
El catálogo oficial [MiFuturo](https://www.mifuturo.cl/bases-de-datos-de-oferta-academica/)
publica oferta histórica 2010–2026. El producto de matrícula histórica de
[CNED](https://cned.cl/institucional/bases-de-datos/) no sustituye oferta sin
matrícula. Esto describe lo localizado; no prueba inexistencia de otros archivos.

MiFuturo indica armonización de nombres institucionales y clasificaciones de
áreas en la consolidación. No se extiende esa afirmación a todos los campos o
nombres de carrera. Se preserva el literal de esta publicación, sin asegurar
que reproduzca cada edición anual originalmente difundida.

El glosario histórico (p. 2) define Año Inicio para carrera/programa en sede;
el instructivo Oferta 2026 (p. 8), para el código completo. Se documentan ambos
alcances. Ninguno aporta la asignación temporal de un plan UMAS a un estudiante.
Vigencia 2 significa vigente sin estudiantes nuevos (glosario p. 4), no cerrado.
Fuentes, huellas, páginas y alcance de búsqueda están en
[búsqueda de cobertura](../data/versiones_historicas_sies_umas/fase_3_20261015/busqueda_cobertura.json).

### Archivos y reproducción

La salida conserva datos académicos sin identidades de estudiantes:

- [Resumen](../data/versiones_historicas_sies_umas/fase_3_20261015/resumen.json),
  [cobertura de códigos](../data/versiones_historicas_sies_umas/fase_3_20261015/cobertura_codigos.tsv)
  e [historia de códigos](../data/versiones_historicas_sies_umas/fase_3_20261015/historia_codigos.json).
- [Oferta anual](../data/versiones_historicas_sies_umas/fase_3_20261015/oferta_codigo_anio.tsv),
  [cruce anual MRUN](../data/versiones_historicas_sies_umas/fase_3_20261015/cruce_oferta_mrun_anual.tsv)
  y [comparación de atributos](../data/versiones_historicas_sies_umas/fase_3_20261015/comparacion_atributos_mrun.tsv).
- [Familias/versiones](../data/versiones_historicas_sies_umas/fase_3_20261015/versiones_por_familia.json),
  [coexistencias](../data/versiones_historicas_sies_umas/fase_3_20261015/coexistencias.json),
  [cambios publicados](../data/versiones_historicas_sies_umas/fase_3_20261015/cambios_atributos.json)
  y [ejemplos](../data/versiones_historicas_sies_umas/fase_3_20261015/ejemplos_academicos.json).

El auxiliar usa Python 3.11+ y openpyxl solo para lectura. El verificador del
XLSX nacional usa lxml. Las rutas y huellas están fijadas en `fuentes.json`.

```bash
python3 scripts/reconstruir_oferta_historica_sies.py --fuentes data/versiones_historicas_sies_umas/fase_3_20261015/fuentes.json --salida /ruta/nueva/fase_3
python3 -m unittest discover -s tests -p test_oferta_historica_sies.py -v
```

Para renovar la comprobación del original se usa
`scripts/verificar_extraccion_oferta_sies.py --original "$XLSX_HISTORICO" --tsv "$TSV_HISTORICO" --expected-xlsx-sha256 94d51a6752b40adb45c8eba65786ee8aad9f6667d15b3d07273a969ec4faed77 --expected-tsv-sha256 c3bc04a39816792c144e846c74da723b2c842627d5724141e1802a82407f455a --output /ruta/nueva/verificacion.json`.
Las dos variables representan las rutas explícitas del descriptor, no búsqueda
del archivo más reciente. Los auxiliares rechazan fuentes alteradas y salidas
existentes diferentes. No ejecutan motores oficiales.

### Cierre H3: 2026-10-15

Estado: **reconstrucción completada para 2010–2026, con brecha explícita de
oferta 2007–2009**. La brecha permanece abierta para el maestro histórico;
no impide examinar los planes UMAS en fase 4.

Pasaron 19 pruebas sintéticas. La revisión independiente confirmó cobertura,
coexistencias, atributos académicos y los 15 campos actuales. Una segunda
ejecución reprodujo los 14 archivos generados idénticos byte por byte, incluido
el manifiesto. El control de cierre confirma sin cambios los dos libros Excel,
MRUN original, puente compilado, duración y tres motores de ambos proyectos.

La [validación final](../data/versiones_historicas_sies_umas/fase_3_20261015/qa_fase3.json)
conserva hashes y conciliaciones. La
[auditoría independiente](../data/versiones_historicas_sies_umas/fase_3_20261015/auditoria_independiente.json)
y la [verificación del original](../data/versiones_historicas_sies_umas/fase_3_20261015/verificacion_original_completa.json)
documentan métodos y alcance. El QA del candidato se conserva como antecedente;
la corrección de inicio cero queda comprobada en el QA final.

Quedan gobernadas las claves y observaciones de oferta, no la selección de un
plan UMAS. La fase 4 debe verificar catálogo de planes, asignaciones y alcance
temporal; la fase 5 decidirá equivalencias solo con evidencia suficiente.
