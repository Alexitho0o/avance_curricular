# Fase 5 — Maestro de equivalencias gobernadas

Autorización: proceder con fase 5, 2026-10-15. Esta especificación precede
al código auxiliar. H2 aporta observaciones MRUN, H3 oferta anual y H4
planes/asociaciones UMAS. Sus límites se conservan en H5.

## Contrato H5

Construir un maestro reproducible con cobertura histórica y un resolvedor
aislado, sin integrar aún los motores ni modificar los libros entregados.
Se separan tres evidencias: equivalencia de programa, equivalencia de un
plan UMAS con un Código Único SIES durante un ámbito efectivo, y asignación
de ese plan a una matrícula en un período. Ninguna sustituye a otra.

La consulta de oferta por año y Código Único exactos puede devolver los
atributos publicados. Eso no demuestra la equivalencia con UMAS. Los
nombres se conservan literales: nombre anual y nombre de oferta 2026 en
campos distintos, sin añadir jornada, modalidad o «Continuidad». Sector IPSS
es un enriquecimiento separado y nunca selecciona versión.

## Uniones y claves

1. Oferta y MRUN: año + Código Único exacto. Conservar códigos solo MRUN,
   solo oferta, ausencia de oferta 2007–2009 y programas sin actividad.
   No rellenar años intermedios ni interpretar ausencia como cierre.
2. Programa UMAS: leer las equivalencias explícitas del snapshot congelado
   2026; preservar código interno, nombre, sede, jornada, filas y hashes.
   No confundir su universo operativo con la oferta publicada de 2026.
   El puente compilado se audita, sin ampliar por semejanza sus relaciones.
3. Candidatos de plan: igualdad de CODPESTUD con el catálogo H4, CODCARPR
   exacto y sede del plan con la relación del snapshot. Jornada procede de
   esa relación y se contrasta con observaciones H4, sin suponer que el plan
   solo exista en jornadas observadas. Nombre interno distinto se señala;
   no se crea un alias. Cada candidato sigue pendiente de equivalencia
   curricular y vigencia, incluso si es único. Solo ámbito candidato 2026;
   sus años SIES observados no amplían su aplicabilidad histórica.
4. Regla efectiva: clave estructurada **CODCARPR + CODPESTUD + sede UMAS +
   jornada UMAS + año + período UMAS + régimen + nombre interno**; destino
   Código Único exacto. El nombre interno es una restricción obligatoria;
   los conflictos se evalúan con el mismo nombre. No concatenar
   sin delimitadores ni equiparar período UMAS a semestre SIES.
5. Cada regla acredita un conjunto explícito de períodos (año, período,
   régimen), los componentes SIES y evidencia con tipo, ruta, hash y
   localizador. No inferir rangos desde primera/última aparición. Claves
   completas, oferta presente en ese año y coherencia de sede/jornada/carrera/
   versión se verifican antes de devolver una equivalencia. Una regla no
   acredita por sí misma la asignación individual histórica del plan.

La representación canónica de una clave es una lista JSON ordenada de
valores; se recortan solo espacios periféricos. No se quitan tildes, SP,
prefijos ni sufijos para crear equivalencias. No se usa versión máxima,
año incrustado en el plan, año de ingreso o primera matrícula como selector.
RE=2, CO=3 y D=1, V=2, O=4 se usan únicamente para leer el ámbito 2026
existente; no se declaran reglas universales retrospectivas. Cada regla
efectiva futura debe respaldar expresamente sus propios componentes.

## Esquema y estados

`maestro.json` tendrá `schema_version=1`, `periodo_objetivo=[2007,2026]`,
`fuentes`, `oferta_anual`, `mrun_anual`, `universo_sies`, `planes_umas`,
`equivalencias_programa_2026`, `candidatos_plan_sies`, `reglas_efectivas`.
Identificadores de relaciones derivados de su contenido, con procedencia
acumulada sin multiplicar artificialmente candidatos iguales.

Una regla efectiva contiene `id`, `estado=ACREDITADA`, `codcarpr`,
`nombre_interno`, `plan_umas`, `sede_umas`, `jornada_umas`, `periodos`
(listas de objetos `anio`, `periodo`, `regimen`), `codigo_unico`,
`componentes_sies` (institucion, sede, carrera, jornada, version), y
`evidencias` (objetos `tipo`, `path`, `sha256`, `localizador`). Tipos exigidos:
`EQUIVALENCIA_PLAN_SIES` y `AMBITO_TEMPORAL`. Evidencia de asignación
individual queda fuera de este maestro académico, se exige en el consumidor.

El resolvedor exige todas las claves; distingue `ENTRADA_INCOMPLETA`,
`FUERA_AMBITO`, `SIN_OFERTA_ANUAL`, `SIN_EQUIVALENCIA`,
`PENDIENTE_EVIDENCIA`, `CONFLICTO_REGLAS` y `EQUIVALENCIA_ACREDITADA`.
Los candidatos informativos nunca devuelven un código como resuelto.
`SIN_OFERTA_ANUAL` distingue ausencia de cobertura anual (2007–2009)
de un código no observado dentro de la cobertura disponible (2010–2026).
Más de un destino acreditado para una clave bloquea la resolución; múltiples
evidencias del mismo destino se agregan. Una fuente alterada o regla inválida
bloquea la carga. Una coincidencia directa SIES tiene estado distinto
`OFERTA_ANUAL_LOCALIZADA` y no ejecuta reglas UMAS.

## Implementación, pruebas y aceptación

Auxiliares en `common/`, `scripts/`, `tests/`, conforme a la excepción de
layout de `agent.md`. No importar ni ejecutar motores oficiales. Usar fuentes
fijadas, proyecciones académicas verificadas H2–H4 y snapshot 2026 explícito;
no leer el año activo 2027 como alternativa. Sin datos personales.

Entregables en `data/versiones_historicas_sies_umas/fase_5_20261015/`:
maestro, tablas de cobertura y candidatos, registro de reglas efectivas,
excepciones, ejemplos de consulta, fuentes, resumen y manifiesto. Se requieren
pruebas de claves completas, período exacto, ambigüedad, conflictos,
no extrapolación, fuentes alteradas, nombres literales, y reproducción
idéntica. Auditoría independiente de evidencia y preservación de fuentes.

H5 puede cerrar la implementación del maestro con equivalencias pendientes;
no se presentará como una certificación completa de mallas históricas.
La evidencia hoy disponible no acredita ninguna regla plan/período→SIES:
el registro efectivo comienza vacío. Completarlo exige nueva evidencia
documental, revisión y un snapshot nuevo. H6 probará el universo; H7 integrará
consumidores; H8 regenerará el Excel. No se adelantan esas fases.

## Resultado del maestro

El maestro conserva **141 códigos SIES y 236 identificadores de plan UMAS**.
Incluye 747 observaciones de oferta anual y 472 observaciones agregadas
MRUN por año/código. Los dos códigos heredados solo MRUN permanecen visibles;
las consultas sin oferta muestran su observación MRUN exacta sin convertirla
en oferta ni equivalencia UMAS.

| Evidencia académica | Resultado |
|---|---:|
| Relaciones del catálogo operativo 2026 | 257 |
| Candidatos plan UMAS–código SIES | 513 |
| Planes con al menos un candidato | 149 |
| Planes sin candidato en esta fuente | 87 |
| Candidatos con nombre igual al catálogo de planes | 342 |
| Candidatos con nombre distinto, sin alias aprobado | 171 |
| Reglas plan/período→Código Único acreditadas | 0 |

Los 87 planes sin candidato incluyen 74 del catálogo y las 13 etiquetas
solo observadas en PROMEDIOS. No desaparecen del maestro. Los 513 candidatos
conservan relaciones nominales distintas: no representan 513 mallas ni
estudiantes. Hay 178 candidatos sin actividad observada en esa jornada;
la ausencia de actividad no los elimina ni demuestra que el programa cerró.

Las 257 relaciones operativas se distribuyen en 161 llaves de
nombre/código interno/sede/jornada: 91 con un destino y 70 con varios.
Sus tres representaciones existentes —catálogo, puente y expandido del
diccionario— provienen de DURACION_ESTUDIOS.tsv. No son respaldos
independientes. Ninguna contiene CODPESTUD ni período efectivo acreditado.
El campo `plan` del snapshot es el tipo de plan SIES, no la malla UMAS.

De esas relaciones, 26 apuntan a cuatro códigos sin fila en oferta 2026:
`I162S2C1J4V1`, `I162S2C3J2V2`, `I162S2C3J4V1`, `I162S2C6J4V1`.
Al expandir por los planes catalogados resultan 76 candidatos sin oferta
2026. Se conservan como evidencia operativa, sin habilitar su resolución
ni reinterpretar la ausencia como cierre.

El candidato `DCBS20251`→`I162S2C53J3V1` conserva J3, con `jornada_umas=null`.
El puente antiguo representaba J3 y J4 como O; H5 no copia esa conversión.
Una futura excepción requiere evidencia explícita. Para nombres, el campo
heredado `nombre_interno` del snapshot procede de NOMBRE_CARRERA del catálogo
operativo: no acredita por sí mismo NOMBRE_L en DatosAlumnos. Las diferencias
quedan visibles en `estado_nombre_catalogo`, sin inventar alias.

### Precedencia de oferta y nombres

Los atributos oficiales proceden de la oferta del año consultado. Se
preservan en campos distintos el nombre anual y el nombre literal de la
oferta 2026. Para un código ausente en 2026, este último queda vacío; no se
hereda por familia. No se añaden sufijos de continuidad, jornada o modalidad.
Las ocho modalidades ausentes en oferta 2010 se conservan como literal vacío
y valor de consulta null. Sector IPSS queda `NO_EVALUADO_EN_H5`.

Se encontraron **41 diferencias de vigencia** entre catálogo operativo y
oferta 2026. Por ejemplo, `I162S2C77J4V2` tiene vigencia 1 en el operativo,
pero la oferta anual indica «Vigente sin estudiantes nuevos». H5 presenta
la oferta anual y conserva la discrepancia; no modifica el catálogo congelado.
La comparación usa códigos categóricos de modalidad y tipo de plan, por lo
que diferencias de caja como «No presencial»/«No Presencial» no se cuentan
como cambios de modalidad.

### Ejemplos de la lógica

| Consulta académica | Resultado H5 | Motivo |
|---|---|---|
| ILOG + ILOG20241 + RE + O + 2026/1/TRIMESTRAL + nombre exacto | Un candidato, `I162S2C77J4V1`; pendiente. | La unicidad operativa no prueba la equivalencia de ese plan en ese período. |
| CILOG + CILOG20241 + RE + O + 2026/1/TRIMESTRAL + nombre exacto | Candidatos `I162S2C77J4V1` y `I162S2C77J4V2`; pendiente. | Ni el prefijo C ni el año 2024 seleccionan V2. |
| NATP + NATP20251 + RE + V + 2026/1/TRIMESTRAL + NATUROPATIA | Candidatos `I162S2C90J2V1` y `I162S2C90J2V2`; pendiente. | Se requiere la equivalencia explícita del plan, no numerar por aparición. |
| IECIRE + IECIRE20211 + RE + V + 2019/1/SEMESTRAL + nombre exacto | Sin equivalencia acreditada para la consulta. | La actividad 2019 del reporte no autoriza retrotraer el catálogo 2026. |
| Año 2020 + `I162S2C46J2V2` | Oferta anual localizada. | Consulta SIES exacta; no afirma equivalencia con un plan UMAS. |
| Año 2008 + `I162M2008N1` | Sin cobertura anual de oferta; observación MRUN preservada. | La brecha de oferta no elimina la evidencia de matrícula. |

Los [ejemplos de consulta](../data/versiones_historicas_sies_umas/fase_5_20261015/ejemplos_consulta.json)
incluyen entradas, estados y localizadores académicos. No son el piloto del
universo de estudiantes ni certifican la asignación individual del plan.

## Uso y actualización

El constructor es `scripts/construir_maestro_equivalencias.py`, el resolvedor
aislado `common/equivalencias_historicas.py` y la consulta
`scripts/consultar_equivalencias_historicas.py`. No se conectaron todavía a
Matricula ni Caracterización. Python 3.11+; esta fase no requiere abrir XLSX.

Desde la raíz de avance_curricular:

```bash
python3 scripts/construir_maestro_equivalencias.py --fuentes data/versiones_historicas_sies_umas/fase_5_20261015/fuentes.json --salida /ruta/nueva/fase_5
python3 scripts/consultar_equivalencias_historicas.py --maestro data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json --anio 2026 --codigo-unico I162S2C77J4V2
python3 scripts/consultar_equivalencias_historicas.py --maestro data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json --anio 2026 --codcarpr CILOG --nombre-interno 'INGENIERIA EN LOGISTICA' --plan-umas CILOG20241 --sede-umas RE --jornada-umas O --periodo 1 --regimen TRIMESTRAL
python3 -m unittest discover -s tests -p 'test_*equivalencias*.py' -v
```

La CLI retorna 0 para oferta localizada o equivalencia acreditada, que son
estados distintos; 2 para pendiente/conflicto/falta de dato; 1 si rechaza la
carga por archivo, esquema o hash. El consumidor debe leer el estado, no
interpretar un código de salida 0 como asignación curricular de un estudiante.
Para los usos desde Python se carga con `cargar_maestro` antes de consultar:
verifica el manifiesto y los archivos de evidencia de reglas acreditadas.
La validación sobre un diccionario en memoria comprueba estructura sin IO.

`registro_reglas_efectivas.json` es la fuente explícita, hoy vacía;
`reglas_efectivas.json` es su salida verificada. Una nueva regla requiere
documentos que respalden plan↔SIES y períodos exactos, fuentes fijadas por
hash y localizador, revisión de su contenido y generación en un destino
nuevo. Etiquetar un archivo con un tipo de evidencia no constituye esa
revisión: el validador comprueba integridad y estructura, no decide por sí
solo la validez académica de un documento. Tampoco certifica la asignación
del plan a una matrícula individual.

Hasta acreditar esas piezas, ningún candidato puede promoverse por
unicidad, año incrustado, primera aparición, duración similar o versión mayor.

## Cierre H5 y validación

Estado: **COMPLETADA_CON_EQUIVALENCIAS_PENDIENTES**. El maestro y la consulta
determinista están implementados; la equivalencia curricular histórica
continúa pendiente de evidencia. El registro efectivo vacío es una
conclusión de alcance documental, no la afirmación de que no existan
equivalencias reales ni planes válidos en la institución.

Pasaron **32 pruebas** del constructor y resolvedor. Se comprobaron también
el rechazo real por SHA incorrecto, el bloqueo de salida preexistente
distinta sin escritura parcial, la consulta SIES exacta, el candidato UMAS
pendiente, un código heredado MRUN sin oferta y el rechazo del ámbito 2027.
La reproducción produjo **12 archivos idénticos**, incluido el manifiesto.

La auditoría independiente contrastó las 513 claves candidatas, sus campos
académicos, actividad y localizadores. Otra revisión pasó 30 controles de
contrato, oferta, nombres, cobertura y conservación. Tras añadir la guarda
J3 al resolvedor, se regeneró el manifiesto con el hash final del código:
la candidata anterior y su rechazo de trazabilidad quedaron registrados;
sus 11 archivos de datos son idénticos a la entrega final. No se corrigió
un hash a mano para hacer pasar la revisión.

Las 17 referencias de entrada y las 11 fuentes/consumidores congelados
verificados conservan sus huellas. No se modificaron motores, puentes,
catálogos previos ni Excel, y no se publicó material en remoto. Las salidas
son académicas agregadas, sin identidades ni notas individuales.

- [Maestro](../data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json)
  y [resumen](../data/versiones_historicas_sies_umas/fase_5_20261015/resumen.json).
- [Candidatos trazables](../data/versiones_historicas_sies_umas/fase_5_20261015/candidatos_plan_sies.tsv),
  [cobertura de planes](../data/versiones_historicas_sies_umas/fase_5_20261015/cobertura_planes.tsv)
  y [cobertura SIES](../data/versiones_historicas_sies_umas/fase_5_20261015/cobertura_sies.tsv).
- [QA final](../data/versiones_historicas_sies_umas/fase_5_20261015/qa_fase5.json),
  [auditoría de la entrega](../data/versiones_historicas_sies_umas/fase_5_20261015/validacion_entrega_maestro.json)
  y [validación contractual](../data/versiones_historicas_sies_umas/fase_5_20261015/validacion_entrega_contrato.json).

H6 debe conservar estos estados en el piloto y cuantificar las excepciones;
no tratar coincidencias candidatas como versiones verificadas. H7 y H8
permanecen pendientes de autorización y de los resultados de las fases previas.
