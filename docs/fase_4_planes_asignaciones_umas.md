# Fase 4 — Planes UMAS y evidencia de asignación histórica

Autorización del usuario: proceder con fase 4 el 2026-10-15. Esta especificación
precede al nuevo auxiliar. H1 fija las fuentes; H2 y H3 reconstruyen matrícula
MRUN y oferta SIES por separado. H4 examina el lado UMAS del cruce.

## Contrato H4

Reconstruir el catálogo de planes disponibles y contrastarlo con el plan
informado en PROMEDIOS y la identidad académica de DatosAlumnos. Delimitar
qué evidencia acredita estructura, asociación en un reporte o asignación
efectiva en un período. Unir dentro de UMAS por identificadores explícitos,
conservando ambigüedades y discrepancias. No unir personas MRUN con UMAS.

Fuentes iniciales fijadas en H1: `Listado_Planes_estudio_Sedes RE+CO.xlsx`,
hoja `BBDD Bruta`; `PROMEDIOSDEALUMNOS_7804.xlsx`, hoja `Hoja1`; y
`DATOSDEALUMNOS_11998.xlsx`, hoja `Hoja1`. La fecha de extracción real de estos
archivos no está acreditada. Las hojas auxiliares de PROMEDIOS no se suman
al reporte principal ni se interpretan como cortes solo por su nombre.

## Reglas de reconstrucción

1. Conservar `CODPESTUD` y `PLAN_DE_ESTUDIO` literales. Su igualdad es una
   coincidencia de identificador interno; se contrastan también carrera y sede.
   Un año o sufijo en el identificador no determina vigencia ni VERSION SIES.
2. La fila del listado de planes está expandida por ramo, nivel, equivalencia
   y requisito. Reconstruir grupos plan/ramo/nivel sin contar sus requisitos
   como asignaturas adicionales. Conservar valores contradictorios y filas
   fuente, sin seleccionar arbitrariamente un atributo.
3. Comparar estructuras entre planes de la misma carrera interna y sede.
   Huellas o diferencias de asignaturas describen el archivo disponible; no
   establecen sucesión temporal, aprobación curricular ni equivalencia SIES.
4. `CODCLI` enlaza solo reportes internos en memoria. DatosAlumnos repetido
   se clasifica por número de filas y contextos distintos, sin elegir la
   primera matrícula. Contrastar `CODCARR` y `CODCARPR`, jornada y sede cuando
   estén disponibles. No quitar SP, sufijos o prefijos para forzar coincidencias.
5. Separar año/período de actividad de PROMEDIOS, matrícula e ingreso de
   DatosAlumnos, primera observación de un plan y fecha efectiva de asignación.
   Un enlace entre cortes no acredita que esos atributos fueran iguales en
   cada año anterior. No convertir períodos UMAS en semestres SIES sin regla.
6. Conservar filas con `NULL`, vacíos o año fuera de 2007–2026 como excepciones;
   no tratarlas como año, matrícula o actividad temporal válida. DatosAlumnos
   con matrícula 2027 se registra fuera del ámbito histórico, sin retrotraerlo.
7. Un plan repetido en notas de varios años puede ser una etiqueta del corte.
   El significado se busca en documentación; ni repetición ni año incrustado
   prueban por sí solos cuándo se asignó o migró el plan. Contrastar asignaturas
   con la estructura del plan sin declarar error una ausencia: puede requerir
   equivalencia/homologación que aún no esté acreditada.
8. No se numeran versiones UMAS ni se asigna código SIES en H4. La fase 5
   recibirá evidencia, estados de unión y brechas, no equivalencias fabricadas.

## Entregables y aceptación

Auxiliar `scripts/reconstruir_planes_umas.py`, pruebas focalizadas y salidas en
`data/versiones_historicas_sies_umas/fase_4_20261015/`. El uso de `scripts/`
y `tests/` sigue el layout auxiliar justificado en `agent.md`. No se importa
ni ejecuta el motor oficial. XLSX se lee, sin editar ni crear libros.

- Catálogo de planes, estructura de asignaturas y comparaciones académicas.
- Observaciones agregadas por plan/carrera/jornada/año/período y cobertura
  del cruce con DatosAlumnos y listado de planes.
- Diagnóstico de claves, excepciones y ejemplos académicos con localizadores.
- Evidencia documental temporal, brechas, resumen, fuentes y manifiesto.

No se exportan CODCLI, RUT, MRUN, nombres de estudiantes, notas individuales
ni sustitutos de identidad. Solo dimensiones académicas, conteos y localizadores
de ejemplo. Las identidades se usan en memoria para cardinalidad y enlace interno.
Se exige SHA-256 antes/después, conciliación de todas las filas, preservación de
planes sin actividad observada, rechazo de fuentes alteradas/salidas distintas
y reproducción idéntica. Una revisión independiente comprobará resultados.

H4 se cierra con los planes y asociaciones disponibles reconstruidos y los
límites temporales explícitos. Si no aparece historial efectivo de asignación,
se registrará como pendiente: no se declarará reconstruida la malla de cada
estudiante para 2007–2026 ni se habilitará un resolvedor histórico completo.

## Reconstrucción del catálogo y de las asociaciones

Las tres fuentes conservan su huella H1. El catálogo contiene **223 planes**
asociados a 127 combinaciones de carrera interna y sede (RE/CO). Cada plan
observado tiene una sola carrera y sede en esta fuente. No se afirma que todas
esas carreras internas pertenezcan al universo SIES, ni que 223 códigos
equivalgan a 223 mallas curricularmente distintas.

Las 11.438 filas del listado se descomponen en:

| Rol observado | Filas |
|---|---:|
| Base de asignatura por plan/ramo/nivel | 4.854 |
| Detalle de equivalencia | 2.480 |
| Detalle de requisito | 2.674 |
| Encabezado «Requisitos:» | 1.430 |

Cada grupo plan/ramo/nivel tiene exactamente una fila base. Los atributos
académicos repetidos en las expansiones no presentan contradicciones. Se
preservan los tipos y valores originales del catálogo, incluidos sus espacios
de relleno, junto con claves de comparación sin espacios periféricos.

`RamoEquiv` contiene referencias compuestas `PLAN_DESTINO/RAMO_DESTINO`.
Se localizaron 2.477 destinos en su plan y tres permanecen pendientes: fila
503, `NETMRE20121/TM212NETMRE20101`; filas 6663 y 6776,
`IECIREOL20191/IC07IECIREOL`. No se corrigen por semejanza ni se convierten
en homologaciones de estudiantes. Los 2.674 requisitos están en su plan.

Se compararon 672 pares de planes de la misma carrera interna y sede.
Ninguno tiene exactamente el mismo conjunto de identificadores de ramo/nivel.
Esto describe claves de estructura: códigos diferentes pueden referirse a
contenidos equivalentes. No prueba renovación curricular ni orden temporal.

### Cobertura de planes en PROMEDIOS

| Presencia en los archivos revisados | Planes |
|---|---:|
| Catálogo y PROMEDIOS | 184 |
| Solo catálogo | 39 |
| Solo PROMEDIOS | 13 |
| Unión de ambos | 236 |

PROMEDIOS contiene 197 etiquetas de plan, pero solo **144** tienen al menos
un registro con año y claves académicas completos. De esos 144, 143 aparecen
en el catálogo; el restante es `TPCPASO`, con una fila completa. Las otras 53
etiquetas solo acompañan registros sin año o claves suficientes. Hay 80 planes
del catálogo sin actividad con año y claves en este extracto, incluidos los 39
sin ninguna aparición en PROMEDIOS. Estos estados no equivalen a cierre o
inactividad institucional.

Las 13 etiquetas sin catálogo son `ASREPASO`, `IECIPASO`, `IETMPASO`, `NITMPASO`,
`TCIBPASO`, `TCREPASO`, `TCSREOLPASO`, `TPAPASO`, `TPASPASO`, `TPCPASO`, `TPRPASO`,
`TTMPASO` y `TTMRE20081`. No se elimina PASO para inventar el plan correspondiente.

### Alcance del enlace interno

PROMEDIOS aporta 129.493 filas: 125.282 tienen año y claves académicas completos
entre 2019 y 2026; 4.211 tienen año `NULL` y se mantienen como excepciones.
No se suman esas filas como matrículas ni asignaturas aprobadas. No hay
actividad con año acreditada 2007–2018 en este extracto, aunque el catálogo
incluye identificadores que contienen años anteriores.

Se observan 13.068 CODCLI distintos en PROMEDIOS y 15.044 en DatosAlumnos,
con 11.075 compartidos. DatosAlumnos tiene 15.045 filas: un CODCLI aparece
dos veces y se conserva sin escoger una fila. Ese duplicado no aparece en
PROMEDIOS. El enlace permite contextualizar 126.782 filas del reporte;
2.711 no encuentran CODCLI en DatosAlumnos. El enlace no multiplica filas.
CODCLI se trata como identificador interno de enlace, no como persona única
institucional; los conteos de registros, claves y planes no se suman entre sí.
Las 319 filas de DatosAlumnos con ANOMATRICULA 2027 se registran fuera del
ámbito. Ninguna coincide con las filas de PROMEDIOS de esta reconstrucción;
no se incorpora oferta 2027 ni se retrotrae ese contexto al historial.

El plan asociado a cada CODCLI es único en este reporte, pero hay 3.485 CODCLI
con actividad de varios años. Eso no acredita que conservaran el mismo plan
durante todos esos años. También se observaron cuatro CODCLI con más de un
CODCARR en el reporte: ni siquiera la carrera se supone inmutable por clave.

Se conservaron diferencias entre contextos: 17 filas de PROMEDIOS tienen
carrera distinta de la carrera del plan catalogado; 11 difieren de la carrera
de DatosAlumnos; 356 difieren en jornada frente a DatosAlumnos. Son
comparaciones de reportes, sin causa ni fecha de cambio acreditadas. No se
afirma que sean errores ni migraciones. Sede coincide en los contextos
comparables. MODALIDAD escolar de DatosAlumnos no se usa.

La comparación del código de asignatura encuentra 124.749 filas directamente
en el plan, 12 con el ramo citado en una relación de equivalencia, 520 sin
ramo localizado en el plan, una con plan sin catálogo y 4.211 sin ramo.
La coincidencia en una relación no acredita la homologación de esa persona
ni el plan de origen de la nota. La ausencia tampoco autoriza borrar la fila.

## Qué se sabe de la vigencia

El catálogo documental U+ V001 describe PROMEDIOS por estudiante/asignatura,
enumera ANO, PERIODO y PLAN_DE_ESTUDIO y las tablas MT_ALUMNO, MT_CLIENT,
RA_NOTA y RA_RAMO. No proporciona el linaje SQL del campo de plan ni define
si su valor corresponde al corte o al período de cada nota. La revisión
documental no permite escoger entre esas dos interpretaciones.

UP-28 pide el plan adscrito al período; BR-08 pide exponer el plan vigente.
Son requerimientos existentes, no prueba de que el reporte ya implemente
esa temporalidad. REGISTRO DE ASIGNATURAS y RA_CARGA_RASTRO son candidatos
documentales para profundizar, sin extracto ni vigencia de plan acreditados.
La evidencia y sus localizadores están en
[evidencia temporal](../data/versiones_historicas_sies_umas/fase_4_20261015/evidencia_temporal.json).

Hay **689 filas de 16 planes** con año de actividad anterior al patrón de año
contenido en el identificador del plan. Es un diagnóstico textual. No prueba
la fecha de creación del plan, una migración ni que las notas estén mal.
Impide convertir ese patrón, sin otra evidencia, en vigencia de cada nota.

| Código de plan UMAS | Hecho observado | Límite |
|---|---|---|
| `ILOG20241` / `CILOG20241` | Actividad completa desde 2024 / 2025 respectivamente. | Ambos contienen 2024; el sufijo no fija el primer año observado ni VERSION SIES. |
| `NATP20251` / `CNATP20251` | El primero tiene actividad completa en 2026; el segundo solo una fila sin año completo. | No certificar inicio 2025 ni inexistencia de estudiantes por el nombre del plan. |
| `IECIRE20211` | Acompaña actividad de 2019–2024. | El plan visible no demuestra qué malla estaba asignada en 2019. |
| `ASREOL` / `TASREOL20191` | Ambos acompañan actividad de 2019–2022. | Preservar ambos planes y sus estructuras; no reemplazar uno por el otro usando solo año. |

`CODPESTUD`/`PLAN_DE_ESTUDIO`, VERSION SIES y el correlativo PLAN_ESTUDIOS de
Avance Curricular son conceptos separados. Esta fase no establece una
equivalencia numérica entre ellos.

## Evidencia necesaria para cerrar lo pendiente

La pieza que falta es una tabla documentada de **matrícula interna + plan
asignado + inicio/fin efectivo**, o de matrícula + año/período + plan cuando
la fuente garantice expresamente esa semántica. Debe conservar fuente, fecha
de extracción y evento de cambio, si existe. No se reconstruyen intervalos
rellenando años entre primera y última aparición.

Además quedan las 13 etiquetas sin catálogo, tres referencias de equivalencia,
diferencias de contextos y el enlace individual MRUN–UMAS no acreditado.
Las [brechas](../data/versiones_historicas_sies_umas/fase_4_20261015/brechas.json)
identifican la evidencia requerida y su efecto en fase 5. La búsqueda fue
acotada: no localizado no significa inexistente en U+ o en otras carpetas.

## Entrega, reproducción y cierre H4

Estado al 2026-10-15: **COMPLETADA_CON_BRECHAS_TEMPORALES**. Se reconstruyó
la estructura disponible y se conciliaron las asociaciones de los reportes.
La asignación histórica efectiva de cada plan sigue pendiente de evidencia.
La fase 5 debe conservar ese estado en sus reglas y no sustituirlo por
selección automática del mayor año o versión.

- [Resumen](../data/versiones_historicas_sies_umas/fase_4_20261015/resumen.json)
  y [fuentes](../data/versiones_historicas_sies_umas/fase_4_20261015/fuentes.json).
- [Catálogo de planes](../data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json),
  [estructura de asignaturas](../data/versiones_historicas_sies_umas/fase_4_20261015/estructura_asignaturas.json)
  y [comparaciones de planes](../data/versiones_historicas_sies_umas/fase_4_20261015/comparaciones_planes.json).
- [Cobertura de planes](../data/versiones_historicas_sies_umas/fase_4_20261015/cobertura_planes.tsv),
  [observaciones por período](../data/versiones_historicas_sies_umas/fase_4_20261015/observaciones_plan_periodo.tsv)
  y [conciliación de contextos](../data/versiones_historicas_sies_umas/fase_4_20261015/conciliacion_contextos_umas.tsv).
- [Diagnóstico de patrones de año](../data/versiones_historicas_sies_umas/fase_4_20261015/diagnostico_patrones_anuales.tsv)
  y [ejemplos académicos](../data/versiones_historicas_sies_umas/fase_4_20261015/ejemplos_academicos.json).
- [QA final](../data/versiones_historicas_sies_umas/fase_4_20261015/qa_fase4.json),
  [auditoría de asignaciones observadas](../data/versiones_historicas_sies_umas/fase_4_20261015/auditoria_asignaciones.json)
  y [auditoría del catálogo](../data/versiones_historicas_sies_umas/fase_4_20261015/auditoria_catalogo.json).

Pasaron **26 pruebas sintéticas** y **30 conciliaciones contra la auditoría
independiente**. Una segunda ejecución reprodujo los **15 archivos generados**,
incluido el manifiesto, idénticos byte por byte. Se comprobaron el rechazo de
hash incorrecto, el bloqueo de salida distinta sin escritura parcial y la
ausencia de identidades/notas individuales en las salidas de prueba.

Las once fuentes y referencias críticas comprobadas conservan sus huellas:
los tres XLSX UMAS, los dos libros entregados, MRUN original, puente compilado,
duraciones y tres motores de ambos proyectos. No se ejecutaron pipelines
oficiales, no se promovieron equivalencias y no se modificaron los Excel.
Los datos de esta fase son dimensiones académicas agregadas y localizadores.

El generador usa Python 3.11+ con openpyxl exclusivamente para lectura y el
auxiliar puro `scripts/estructura_planes_umas.py`. Para reproducir en un destino
nuevo desde la raíz de `avance_curricular`:

```bash
python3 scripts/reconstruir_planes_umas.py --fuentes data/versiones_historicas_sies_umas/fase_4_20261015/fuentes.json --salida /ruta/nueva/fase_4
python3 -m unittest discover -s tests -p 'test_*planes_umas.py' -v
```

Las rutas son explícitas y los SHA-256 obligatorios. La misma entrada produce
la misma salida; no se busca el archivo más reciente ni se reemplazan fuentes.
