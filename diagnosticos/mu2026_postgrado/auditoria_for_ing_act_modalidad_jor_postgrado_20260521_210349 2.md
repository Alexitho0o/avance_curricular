# Auditoría FOR_ING_ACT, MODALIDAD y JOR · Postgrado/Postítulo MU2026

Fecha de ejecución: 2026-05-21 21:03:50

## Resultado

- Filas PES-ready auditadas: 55
- Filas CON_TITULOS revisadas: 55
- Registros control OK: 55
- Cambios propuestos en JOR: 0
- Cambios propuestos en MODALIDAD: 0
- Cambios propuestos en FOR_ING_ACT: 0
- CSV corregido: `resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO.csv`
- Planilla de auditoría: `resultados/matricula_unificada_2026_postgrado_postitulo_FOR_ING_ACT_MODALIDAD_JOR_AUDITORIA.xlsx`

No se modifica JOR en la simulación: los 55 registros coinciden con matriz/oferta, diccionario gobernado y componente `J` del `CODIGO_UNICO`.

## Archivos revisados

- PES-ready final: `resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY.csv`
- CON_TITULOS: `resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv`
- CONTROL_FINAL: `resultados/matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv`
- Trazabilidad: `resultados/trazabilidad_matricula_unificada_2026_postgrado_postitulo.tsv`
- Diccionario postgrado/postitulo: `control/diccionarios/diccionario_postgrado_postitulo_mu2026.tsv`
- Matriz/oferta: `input/PROMEDIOSDEALUMNOS_7804.xlsx`
- Manual MU2026 extraido: `manual_matrícula_unificada.txt`

## Significado de JOR y alcance del manual

- Manual MU2026, Cuadro N°2 postgrado/postítulo: `JOR` es la jornada de la carrera o programa y debe informarse con códigos numéricos institucionales.
- El manual no trae una tabla semántica institucional que confirme que `1/2/3/4` equivalen a diurna/vespertina/semi/distancia.
- La gobernanza técnica local documenta el mapeo operativo: `1=diurna`, `2=vespertina`, `3=semi`, `4=distancia/online`.

El manual adjunto no entrega información suficiente para responder con certeza esta consulta respecto del significado oficial institucional de cada código de `JOR`; la certeza operativa de esta auditoría viene de la matriz/oferta, el `CODIGO_UNICO` y el diccionario gobernado.

## Origen de JOR

- Fuente final: matriz/oferta académica (`PROMEDIOSDEALUMNOS_7804.xlsx`, hoja `matriz`) y diccionario `control/diccionarios/diccionario_postgrado_postitulo_mu2026.tsv`.
- `CODIGO_UNICO` respalda el componente de jornada: por ejemplo `I162S2C70J4V1` implica `JOR=4`; `I162S2C53J3V1` implica `JOR=3`.
- `JORNADA_ORIGEN` del archivo fuente se conserva solo como evidencia. No gobierna el valor final si contradice la matriz.
- Evidencia previa: `diagnosticos/mu2026_postgrado/puente_postgrado_jornada_codcar_20260508_085709.md` líneas 84-85: usar matriz como fuente oficial para `COD_SED`, `COD_CAR`, `MODALIDAD`, `JOR`, `VERSION`.
- Validación previa: `diagnosticos/mu2026_postgrado/auditoria_cierre_postgrado_postitulo.py` líneas 539-553 compara `JOR` del control contra diccionario gobernado.

## Distribución JOR

| JOR | Antes | Después |
| --- | ---: | ---: |
| 3 | 18 | 18 |
| 4 | 37 | 37 |

## Distribuciones FOR_ING_ACT y MODALIDAD

### FOR_ING_ACT

| FOR_ING_ACT | Antes | Después |
| --- | ---: | ---: |
| 1 | 35 | 35 |
| 10 | 20 | 20 |

### MODALIDAD

| MODALIDAD | Antes | Después |
| --- | ---: | ---: |
| 2 | 18 | 18 |
| 3 | 37 | 37 |

## Contraste CODIGO_UNICO ↔ COD_SED ↔ COD_CAR ↔ MODALIDAD ↔ JOR ↔ VERSION

| CODIGO_UNICO | COD_CAR | MODALIDAD | JOR | VERSION | NOMBRE_CARRERA | n |
| --- | --- | --- | --- | --- | --- | ---: |
| I162S2C53J3V1 | 53 | 2 | 3 | 1 | DIPLOMADO EN CIBERSEGURIDAD APLICADA | 18 |
| I162S2C66J4V1 | 66 | 3 | 4 | 1 | DIPLOMADO EN FULLSTACK | 15 |
| I162S2C70J4V1 | 70 | 3 | 4 | 1 | DIPLOMADO REDES INDUSTRIALES | 22 |

## Coherencia online

- Registros con matriz online/distancia (`MODALIDAD=3`, `JOR=4`): 37. Todos quedan coherentes.
- Registros no online según matriz/oferta: 18. Corresponden a `I162S2C53J3V1` (`MODALIDAD=2`, `JOR=3`) y se conservan porque ese es el código gobernado.
- Si se confirma institucionalmente que `DIPLOMADO EN CIBERSEGURIDAD APLICADA` debe ser online/distancia, la corrección debe nacer en la matriz/oferta/diccionario y cambiar el `CODIGO_UNICO`; no corresponde inferirlo desde la letra `O` de la fuente.

## Registros modificados por JOR

No hay registros modificados por `JOR`.

## Validaciones obligatorias

- Distribución JOR antes/después generada: OK.
- Lista de registros modificados por JOR: 0 registros.
- Coherencia con `CODIGO_UNICO`: 55/55 OK.
- Coherencia con matriz/oferta: 55/55 OK.
- Coherencia con diccionario gobernado: 55/55 OK.
- Archivo corregido con 21 campos por fila, sin encabezado y delimitado por punto y coma: OK.

## Artefactos

- `resultados/matricula_unificada_2026_postgrado_postitulo_FOR_ING_ACT_MODALIDAD_JOR_AUDITORIA.xlsx`
- `resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO.csv`
- `diagnosticos/mu2026_postgrado/auditoria_for_ing_act_modalidad_jor_postgrado_20260521_210349.md`
- `diagnosticos/mu2026_postgrado/auditoria_for_ing_act_modalidad_jor_postgrado_20260521_210349.json`
