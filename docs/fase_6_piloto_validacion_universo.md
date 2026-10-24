# Fase 6 — Piloto y validación del universo disponible

Autorización: «vamos con la fase 6», 2026-10-15. Esta especificación precede
al auxiliar. H5 queda congelado: maestro, reglas vacías, resolvedor y fuentes
se verifican por hash. H6 ejecuta consultas y concilia resultados; no crea
equivalencias ni integra motores ni modifica los Excel.

## Alcance y unidades

Institución 162, años objetivo 2007–2026. El universo es el contenido de las
fuentes seleccionadas, no toda la historia institucional certificada:

- SIES: unión exacta de claves año + Código Único presentes en oferta anual
  y observaciones MRUN del maestro H5. No completar años sin observación.
- UMAS: todas las filas de `conciliacion_contextos_umas.tsv` H4, con
  `filas_reporte` como peso. Contrastar su proyección con
  `observaciones_plan_periodo.tsv`. Ambos representan el mismo reporte;
  no sumarlos entre sí. Son contextos y filas de PROMEDIOS, no estudiantes,
  matrículas ni asignaturas aprobadas.
- Cobertura: conservar los 141 códigos SIES y 236 identificadores de plan
  del maestro, tengan o no observaciones consultables o actividad vigente.

No sumar `identificadores_internos_distintos` entre grupos. No releer ni
exportar identidades, notas individuales o sustitutos de identidad. Las
fuentes primarias permanecen fijadas por H1–H5. La fecha real de extracción
de los reportes UMAS continúa no verificada; el nombre del archivo no la fija.

## Adaptación de la consulta UMAS

Conservar las dimensiones originales de PROMEDIOS: CODCARR, CARRERA,
PLAN_DE_ESTUDIO, JORNADA, ANO, PERIODO y REGIMEN. El parámetro técnico
`codcarpr` de H5 recibe CODCARR del reporte, sujeto al contraste del catálogo;
no se sustituye por CODCARPR de DatosAlumnos. El nombre procede de CARRERA,
no del nombre heredado del snapshot operativo ni de un alias inventado.

`SEDE_LISTADO` solo se incorpora a la consulta cuando
`estado_plan_catalogo=PLAN_CONTEXTO_UNICO` y
`carrera_plan_vs_promedios=IGUAL`, corroborados con el catálogo del maestro.
Representa contexto del catálogo, no sede individual histórica acreditada.
No completar sede o cualquier otra clave desde DatosAlumnos. Su información
queda como contraste del reporte: una diferencia no demuestra error ni fecha
de migración. ANOMATRICULA/ANOINGRESO nunca reemplazan ANO de la actividad.

Revalidar las ocho dimensiones H5; el estado H4 OBSERVACION_CON_ANIO no
comprueba por sí solo nombre, jornada o régimen. Solo recortar espacios
periféricos; NULL/NONE/NAN y vacíos son faltantes. Período y régimen siguen
siendo literales UMAS, sin convertirlos a semestres SIES.

Partición excluyente de entrada, con esta precedencia:

1. Año inválido → `ANIO_NO_VALIDO`.
2. Año fuera de 2007–2026 → `FUERA_AMBITO`.
3. Plan sin contexto único de catálogo → `PLAN_SIN_CONTEXTO_UNICO`.
4. Carrera del reporte distinta de la del plan → `CARRERA_PLAN_DISCREPANTE`.
5. Otras claves ausentes o carrera no comparable → `CLAVES_INCOMPLETAS`.
6. Contexto completo y concordante con catálogo → `CONSULTABLE`.

Solo el último grupo se envía al resolvedor H5, que exige la clave completa.
Los otros conservan todos los campos originales, motivos y localizadores;
no se fabrica una consulta con sede prestada. DatosAlumnos y estado de ramo
son ejes adicionales de diagnóstico, no filtros que borren filas del reporte.

Se deduplican consultas por la lista JSON ordenada de sus ocho parámetros,
manteniendo pesos y filas fuente. Esto evita repetir consultas idénticas;
no deduplica personas ni elimina actividad. El resultado se devuelve a cada
contexto sin expandir filas. No se selecciona primera versión, máxima,
año del código de plan, duración similar ni primera aparición MRUN.

## Estados, controles y ejemplos

Separar estado de adaptación, estado devuelto por H5, número de destinos
candidatos y diagnóstico de evidencia. Un candidato único permanece
pendiente. Los candidatos 2026 no se retrotraen a años anteriores. Los
contextos con nombre distinto muestran el motivo, sin aceptar nombres de
catálogo como alias automáticos. Ningún resultado acredita por sí solo la
asignación individual histórica del plan.

Para SIES, exigir una respuesta OFERTA_ANUAL_LOCALIZADA por cada fila
publicada y atributos literales idénticos. Las observaciones MRUN sin oferta
mantienen motivo de cobertura y sus pesos; no se presentan como oferta.
Nombre anual y nombre de oferta 2026 permanecen separados. La jornada J3
no se convierte a O/J4. Sector IPSS no interviene en selección de versión.

Ejemplos deterministas por situaciones generales: Logística regular y
continuidad, Naturopatía, Computación e Informática con actividad anterior
al año del identificador, plan ausente, carrera discrepante, nombre distinto,
código solo oferta, código histórico ausente en 2026 y código heredado MRUN.
Se seleccionan contextos existentes y se conserva su localizador; cualquier
caso sin observación se indica sin inventar matrícula o período.

## Entregables y aceptación H6

Auxiliar `scripts/validar_piloto_equivalencias.py` y pruebas focalizadas en
`tests/`, conforme al layout auxiliar justificado en `agent.md`. Salidas en
`data/versiones_historicas_sies_umas/fase_6_20261015/`: consultas únicas,
resultados por contexto, validación anual SIES, cobertura por plan/código,
distribuciones por año y estado, excepciones y evidencia requerida, ejemplos,
fichas de unidades/procedencia, resumen, aceptación, fuentes y manifiesto.

Se exige conciliación de todos los pesos y universos, contraste independiente
de consultas y denominadores, preservación literal de atributos, fuentes y
H5 intactos, ausencia de identidades, rechazo de fuentes/salidas alteradas y
reproducción idéntica. El piloto usa el resolvedor H5 real, sin copiar una
versión alternativa que produzca resultados diferentes.

H6 puede completar la validación técnica con excepciones trazadas. Se
informarán por separado aceptación técnica del piloto y disponibilidad de
equivalencias acreditadas. Con el registro H5 actual vacío, no habilita
asignación automática de versiones históricas. Una futura integración H7
debe propagar esos estados; no reemplazarlos por la heurística anterior.
La integración y el Excel H8 no se ejecutan en esta fase.

## Reubicación explícita de la fuente histórica PROMEDIOS

El primer control H6 rechazó la ruta original de Descargas: su SHA-256 ahora
es `78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71`,
distinto del registrado en H1–H5. No se presume que solo cambió metadata:
el paquete XLSX presenta diferencias en varias partes XML y no se ha
certificado igualdad de valores de la copia actual de Descargas.

Se localizó una copia **idéntica byte por byte al hash histórico** en
`/Users/alexi/Documents/GitHub/seguimiento_titulados_empleabilidad_2026/data/raw/PROMEDIOSDEALUMNOS_7804.xlsx`:
`83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca`.
H6 la registra como reubicación explícita para comprobar la fuente de las
proyecciones congeladas. No sustituye archivos ni cambia manifiestos H1–H5.

El verificador admite únicamente esa ruta de respaldo y el hash original
declarados en fuentes H6; exige igualdad con el hash del descriptor anterior.
No busca automáticamente otra copia ni admite una fuente de contenido nuevo.
La ruta actual de Descargas se registra como desviación, separada de la
integridad de la fuente histórica efectivamente utilizada por el piloto.

## Resultados del piloto completo

Se evaluaron **5.176 contextos agregados**, equivalentes a **129.493 filas de
PROMEDIOS**. Su proyección coincide exactamente, por dimensiones y peso,
con los 1.581 grupos de observaciones H4. No hubo pérdida ni expansión de
filas. Estos dos conteos describen el mismo reporte; no se suman.

| Adaptación de entrada | Contextos H4 | Filas del reporte |
|---|---:|---:|
| Consultable con las ocho dimensiones | 4.795 | 125.264 |
| Año ausente/no válido | 370 | 4.211 |
| Carrera del reporte distinta de la del plan | 10 | 17 |
| Plan sin contexto único de catálogo | 1 | 1 |
| Total | 5.176 | 129.493 |

Las 125.264 filas consultables se agrupan en **1.349 consultas distintas**.
El resultado de cada consulta se devuelve a sus contextos originales sin
duplicar sus pesos. Las 4.229 filas restantes conservan estado NO_CONSULTADO
y su motivo; no cuentan como búsquedas fallidas ni se corrigen desde DA.

| Resultado entre las filas consultables | Filas del reporte |
|---|---:|
| Un destino candidato, todavía sin acreditar | 9.938 |
| Dos destinos candidatos, sin acreditar | 2.987 |
| Tres destinos candidatos, sin acreditar | 800 |
| Cuatro destinos candidatos, sin acreditar | 154 |
| Sin regla histórica acreditada para 2019–2025 | 110.605 |
| Sin candidato exacto en 2026 | 779 |
| Nombre distinto sin alias en 2026 | 1 |
| Total consultable | 125.264 |

Los primeros cuatro grupos suman **13.879 filas**, todas con actividad 2026;
representan 59 consultas distintas. Las otras 1.290 consultas no encuentran
equivalencia aplicable. Las 110.605 filas históricas no se resuelven con el
catálogo operativo 2026 porque su alcance no se extiende retrospectivamente.
No son 110.605 estudiantes ni un conteo de errores de registro.

**Ninguna consulta acredita un Código Único por equivalencia plan/período.**
El maestro H5 conserva cero reglas efectivas acreditadas. El piloto valida
que los candidatos no se conviertan indebidamente en asignaciones.

### Cobertura histórica SIES

La unión de oferta y MRUN produjo **767 claves anuales** de los 141 códigos.
Se consultaron todas; las 747 filas de oferta conservaron todos sus atributos
del maestro, incluidos nombres literales. La lectura exacta SIES no acredita
la relación de ese código con un plan UMAS.

| Presencia en fuentes por año/código | Claves | Registros MRUN asociados |
|---|---:|---:|
| Oferta y MRUN | 452 | 22.266 |
| Solo oferta | 295 | 0 |
| Solo MRUN, sin cobertura de oferta 2007–2009 | 20 | 2.120 |
| Total | 767 | 24.386 |

Los 24.386 son registros históricos observados en el extracto MRUN, no
personas únicas ni matrícula institucional de un año. Las 20 claves sin
oferta están fuera de la cobertura anual disponible; no demuestran ausencia
de oferta real. Se conservan los 35 códigos solo oferta y los dos códigos
heredados solo MRUN. Quince códigos de oferta histórica no aparecen en
oferta 2026; al añadir los heredados, 17 códigos de la unión carecen de
nombre literal en ese corte. No se inventa un nombre 2026 por familia.

La cobertura UMAS mantiene los **236 planes**: 197 observados en PROMEDIOS
y 39 presentes solo en el catálogo. Conserva también los 87 planes sin
candidato H5. Los planes sin actividad completa no se etiquetan como cerrados.
El extracto no aporta actividad con año entre 2007 y 2018; el piloto no
rellena ese intervalo con los años escritos en los identificadores de plan.

### Casos comprobados

- **Logística regular:** `ILOG20241`, RE/O, 2026/1/TRIMESTRAL, nombre del
  reporte `INGENIERIA EN LOGISTICA`: candidato `I162S2C77J4V1`, pendiente.
  Localizador: H4 fila 2635; PROMEDIOS fila 39082.
- **Logística continuidad:** `CILOG20241`, RE/O, 2026/1/TRIMESTRAL, nombre
  interno observado `CONTINUIDAD INGENIERIA LOGISTICA`: candidatos
  `I162S2C77J4V1` y `I162S2C77J4V2`. Ese nombre interno se conserva para
  trazar la unión; no sustituye al nombre oficial de la oferta 2026.
  Localizador: H4 fila 267; PROMEDIOS fila 48168.
- **Naturopatía:** `NATP20251`, RE/V, 2026/1/TRIMESTRAL: candidatos
  `I162S2C90J2V1` y `I162S2C90J2V2`, sin selección automática.
  Localizador: H4 fila 2679; PROMEDIOS fila 34836.
- **Historia del plan:** `IECIRE20211` aparece con actividad 2019/1/SEMESTRAL.
  La consulta conserva 2019; no usa 2021 como fecha efectiva ni aplica
  retrospectivamente equivalencias 2026. H4 fila 971; PROMEDIOS fila 7251.
- **Nombre pendiente:** `IECIRE20151`, O, 2026/1/SEMESTRAL tiene en CARRERA
  `INGENIERIA EN  INFORMATICA` (dos espacios internos). H5 no lo convierte
  en alias. H4 fila 741; PROMEDIOS fila 124285. Una regla de normalización
  futura debe quedar explícita; corregir esta diferencia de escritura por
  sí sola tampoco acreditaría la equivalencia curricular temporal.
- **Plan ausente:** `TPCPASO`, 2023/1/SEMESTRAL, queda sin consulta por falta
  de contexto de catálogo. H4 fila 4357; PROMEDIOS fila 12525. No se elimina
  PASO para asignarle otro plan.

Las diferencias con DatosAlumnos se publican por eje en
`controles_contextos_umas.tsv`. Cada eje vuelve a cubrir el mismo reporte:
sus totales no se suman entre ejes. Jornada distinta del corte DA, carrera
distinta o asignatura no localizada no demuestran por sí solas un error
histórico ni autorizan modificar los parámetros originales de PROMEDIOS.

Los **779 registros 2026 sin candidato exacto** se concentran en ocho
planes. No deben resolverse copiando un código de otra sede o jornada:

| Planes | Filas del reporte | Contexto que queda pendiente |
|---|---:|---|
| COTEIQ20261, COTENS20261, COTFAR20261 | 495 | Sede CO del catálogo; las relaciones del maestro no acreditan ese contexto. |
| DCBS20251 | 96 | Jornada O en el reporte; el candidato SIES J3 no tiene correspondencia UMAS acreditada. |
| DDASC, DFSCK20261, DHIAD20261, DREIN20261 | 188 | Sin candidato exacto para los parámetros reportados. |

El caso nominal de IECIRE20151 es una fila adicional: total 780 filas
2026 sin equivalencia, separadas de las 13.879 con candidatos pendientes.

## Entrega y reproducción

El constructor H6 utiliza el resolvedor H5 congelado y las proyecciones
académicas; no se importa ni ejecuta el motor MU2026. La reubicación de
PROMEDIOS exige el mismo SHA-256 histórico y queda declarada en fuentes.
Python 3.11+, biblioteca estándar; esta fase no abre ni edita los XLSX.

```bash
python3 scripts/validar_piloto_equivalencias.py --fuentes data/versiones_historicas_sies_umas/fase_6_20261015/fuentes.json --salida /ruta/nueva/fase_6
python3 -m unittest discover -s tests -p 'test_piloto_equivalencias.py' -v
```

La ejecución exitosa produce resultados y excepciones. No indica que las
equivalencias estén certificadas. Cambiar una fuente, el resolvedor H5 o una
salida existente distinta bloquea la ejecución. Una edición nueva requiere
su propio contrato y destino; no se cambia el hash esperado para aceptar
contenido diferente en la edición histórica.

## Cierre H6

Estado: **COMPLETADA_CON_EXCEPCIONES**. La validación técnica es satisfactoria;
la asignación automática de versiones históricas no queda habilitada.

Pasaron **18 pruebas sintéticas**: precedencia de exclusiones, claves nulas,
contrastes de catálogo, prohibición de completar desde DA, deduplicación de
consultas sin perder pesos, rechazo de compensaciones entre grupos, literalidad
SIES/MRUN y reubicación solo por SHA histórico idéntico. Las pruebas reales
de CLI rechazaron una fuente con hash distinto, una reubicación con hash
distinto y una salida preexistente diferente, sin escritura parcial.

La reproducción produjo **13 archivos idénticos**, incluido el manifiesto,
y coincide con la candidata auditada. Una revisión independiente contrastó
las 1.349 consultas y los 5.176 contextos, con sus parámetros, pesos,
destinos y localizadores. Otra contrastó las 767 consultas SIES, nombres,
atributos, cobertura y ejemplos. Ambas aprobaron los resultados.

El maestro, resolvedor y manifiestos H5 conservan sus huellas. Diez referencias
congeladas mantienen su hash en la ruta original; PROMEDIOS se verificó en
el respaldo histórico idéntico, mientras Descargas quedó registrada como
ruta modificada. No se modificaron fuentes primarias, motores ni Excel.
No se enviaron ni publicaron registros.

- [Resumen](../data/versiones_historicas_sies_umas/fase_6_20261015/resumen.json)
  y [aceptación técnica y límites](../data/versiones_historicas_sies_umas/fase_6_20261015/aceptacion_h6.json).
- [Consultas UMAS](../data/versiones_historicas_sies_umas/fase_6_20261015/consultas_umas.tsv)
  y [resultados por contexto](../data/versiones_historicas_sies_umas/fase_6_20261015/resultados_contextos_umas.tsv).
- [Consultas SIES anuales](../data/versiones_historicas_sies_umas/fase_6_20261015/consultas_sies_anuales.tsv),
  [cobertura de planes](../data/versiones_historicas_sies_umas/fase_6_20261015/cobertura_planes_piloto.tsv)
  y [cobertura de códigos](../data/versiones_historicas_sies_umas/fase_6_20261015/cobertura_codigos_piloto.tsv).
- [Ejemplos](../data/versiones_historicas_sies_umas/fase_6_20261015/ejemplos_piloto.json),
  [brechas priorizadas](../data/versiones_historicas_sies_umas/fase_6_20261015/brechas_priorizadas.json)
  y [fichas de fuentes y unidades](../data/versiones_historicas_sies_umas/fase_6_20261015/ficha_fuentes_metricas.json).
- [QA final](../data/versiones_historicas_sies_umas/fase_6_20261015/qa_fase6.json)
  y [reubicación documentada](../data/versiones_historicas_sies_umas/fase_6_20261015/reubicacion_fuente_promedios.json).

H7 permanece pendiente. Su integración deberá conservar los motivos y
campos no resueltos; H6 no autoriza sustituirlos por elección de versión
máxima ni retrotraer las equivalencias operativas 2026.
