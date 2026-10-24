# Reconstrucción de presencia anual por carrera

Especificación previa, 2026-10-16. Continúa el enlace conjunto sin cambiar
catálogos, Excel ni asignaciones productivas. Scripts y pruebas aislados conforme
al layout de agent.md. Se conserva la agrupación existente.

## Contrato

Construir tres evidencias separadas: año declarado en ANOMATRICULA, actividad
académica anual y matrícula documentada en reportes institucionales. No usar
estado actual como estado histórico ni interpolar años entre dos observaciones.
La actividad exige nota APROBADO/REPROBADO y no convalidación; otros registros
se conservan en conteos de calidad y no se usan como cursado efectivo.

Unir notas a DatosAlumnos por CODCLI y CODCARR=CODCARPR y verificar documento
RUT+DV. Rechazar conflictos o documentos no comparables; no transferir notas
entre carreras por compartir RUT. Una persona puede conservar varias carreras.
Duplicados entre extractos aportan una sola presencia persona/carrera/año,
conservando fuentes de evidencia. El primer año observado NO acredita año cero.

Evaluar la ampliación ANOMATRICULA + actividad en los 500 casos del ensayo con
extracto 12023. El reporte institucional se reserva para validar y para comparar
universos documentados, no para generar candidatos del nuevo grafo. La familia,
sexo, nacimiento e ingreso original conservan las reglas del ensayo previo.
Cuantificar cobertura de personas y carreras de los reportes frente a UMAS.
No confundir concordancia documental indirecta con identidad certificada.

Leer completos los extractos académicos seleccionados, inventariar columnas,
años, filas y hashes; no exportar identificadores. Salidas agregadas y 500 casos
anónimos. Conservar 137 referencias congeladas y Excel del usuario. Pruebas de
exclusión de convalidaciones, identidad conflictiva y carrera distinta.

## Resultados

Se leyeron completas las filas disponibles en cuatro extractos: PROMEDIOS 7804
(129.493), archivo 2020 (70.000), 2021 (70.000) y 2022 (68.464). Sus nombres no
representan el año de cada nota: contienen varios años. Dos tienen exactamente
70.000 filas; no se acredita que esos extractos cubran íntegramente el sistema
original. Las presencias se deduplican aunque existan en varios extractos.
Los archivos aportan actividad 2019–2026. No se inventó actividad 2007–2018.
Las columnas, años reales, hashes y exclusiones quedan en el resumen/manifest.

Se rechazaron notas cuyo documento no coincidía con DatosAlumnos, aunque
coincidieran expediente y carrera. Los conteos de conflictos por fuente son
filas de notas (8, 60, 58 y 69), no personas distintas, y pueden repetirse entre
extractos. No se corrigieron documentos automáticamente. Las convalidaciones y
registros sin aprobación/reprobación no aportan presencia de cursado.

| Año | Solo ANOMATRICULA: personas | Con actividad: personas | Personas del reporte institucional con presencia UMAS / total del reporte |
|---|---:|---:|---:|
| 2018 | 495 | 495 | 457 / 1.077 |
| 2019 | 609 | 1.155 | 1.080 / 1.085 |
| 2020 | 487 | 1.057 | 958 / 966 |
| 2022 | 545 | 1.155 | 1.021 / 1.021 |

La última columna cruza documento entre reporte y UMAS: no utiliza MRUN para
identificar a la persona. Es cobertura de persona/año, no certificación de su
carrera/versión. La auditoría adicional por familia de carrera encuentra
presencia para 422 filas de reporte en 2018, 915 en 2019, 874 en 2020 y 990 en
2022. Las demás conservan su causa: falta de observación anual, agrupación sin
familia compatible, persona ausente o documento no normalizable. Una familia
compatible no determina por sí sola regular/continuidad ni versión.

En 2019, 2020 y 2022 quedan respectivamente 75, 99 y 134 personas con presencia
UMAS fuera del reporte institucional consultado. Son diferencias de universo
pendientes de revisar por corte, ingreso, retiro o edición del reporte: NO se
atribuyen automáticamente a errores de información ni se eliminan para cuadrar.
En 2018 hay 38 personas fuera del reporte y 620 del reporte sin presencia anual
reconstruida; faltan notas de ese período, aunque 1.074 de las 1.077 personas
reportadas sí aparecen en DatosAlumnos en algún contexto.

Reportes institucionales y MRUN tampoco tienen idénticos totales de personas:
2019 tiene 1.085 documentos normalizados frente a 1.088 MRUN; 2020, 966 frente a
968; 2022, 1.021 frente a 1.018. No se fuerza una biyección. El CSV enviado 2022
no acredita por sí solo la edición final aceptada de matrícula.

### Repetición de los 500 casos

Se conservan las mismas 500 personas del ensayo con DATOSDEALUMNOS_12023 y sus
años ancla. Se amplía el grafo a todas las personas con presencia observada,
sin usar el código del reporte para generar candidatos.

| Variante | Concordantes con referencia | Contradictorios | Sin referencia unívoca | Sin enlace forzado |
|---|---:|---:|---:|---:|
| Familia, sexo y nacimiento | 305 | 1 | 8 | 186 |
| Además ingreso original | 362 | 1 | 8 | 129 |

En la segunda variante había 360 concordantes antes de reconstruir la presencia
anual: ahora hay 362. No es una mejora suficiente para activar identidades.
Al ampliar el universo aparecen competidores antes omitidos; la base disminuye
de 310 a 305 concordantes. Esto es esperable al corregir cobertura y muestra
por qué no debemos optimizar solo el número de candidatos únicos.

El universo del grafo aumenta de 2.136 a 3.862 personas/año. Con ingreso
original hay 2.418 pares forzados condicionales; fuera de los 500 casos no se
ha acreditado su concordancia individual. Se conserva una contradicción en la
muestra y la referencia sigue siendo documental indirecta. No existe una tabla
oficial RUT–MRUN en este trabajo y no se exige una para seguir investigando.

Entre las filas de reporte con familia compatible se observaron 46 sin
coincidencia conjunta de nacimiento/sexo o con datos faltantes, frente a 3.691
coincidentes. Son filas de reporte, no 46 estudiantes diferentes ni 46 errores
confirmados. No se reemplazan automáticamente los valores UMAS con el reporte.

### Qué queda resuelto y qué sigue pendiente

Queda implementada una presencia histórica observable por expediente/carrera/año,
con evidencia diferenciada y sin trasladar la actividad técnica a continuidad.
Su mínimo año es primera observación disponible, no año cero acreditado ni
primera oferta SIES. El reporte permite auditar la pertenencia histórica aunque
el estudiante no tenga actividad en el extracto de notas.

Antes de imponer los totales como cupos exactos quedan pendientes: observaciones
académicas 2007–2018, diferencias de corte frente a los reportes, las familias
incompatibles y las discrepancias demográficas. También falta acreditar que la
sede/jornada actual del expediente represente cada año histórico. Los estados
actuales no se convierten en estados al corte anterior.

## Validación y entrega

Cinco pruebas verifican actividad, convalidación, documento incompatible,
ausencia del expediente de la misma carrera y año inválido. Se mantienen las
pruebas exhaustivas del algoritmo de enlace. Se verificaron las 137 referencias
congeladas y el Excel del usuario. No se activó ninguna asignación ni se
modificaron los resultados previos. Agregados de carrera pueden solaparse por
persona entre jornadas/evidencias: no sumarlos para obtener personas anuales.

Fuentes externas quedan referenciadas por hash; el paquete no respalda sus
contenidos completos. Código y resultados permanecen en el proyecto sin
publicación remota ni datos identificatorios exportados.

```sh
python3 -m unittest discover -s tests -p test_presencia_anual.py
python3 scripts/reconstruir_presencia_anual.py
```

[Resumen](../data/presencia_anual/20261016/resumen.json),
[presencia por carrera](../data/presencia_anual/20261016/presencia_por_carrera.json),
[500 casos](../data/presencia_anual/20261016/casos_500.json),
[cohortes del reporte frente a MRUN](../data/presencia_anual/20261016/cohortes_reporte_mrun.json),
[manifest](../data/presencia_anual/20261016/manifest.json).
