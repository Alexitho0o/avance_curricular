# Desglose por CODIGO_UNICO de diferencia +166 pregrado

## Contexto

Se amplia la auditoria de pregrado entre `publicacion2026.xlsx` y el congelado combinado gobernado de 4.165 registros. Posgrado/Postitulo permanece fuera del analisis y sigue conciliado 54 publicado versus 54 congelado.

## Metodologia

La publicacion fue tratada como `MATRICULA_AGREGADA_PUBLICADA`: se filtro `NIVEL GLOBAL=Pregrado` y se sumo `TOTAL MATRICULA` por `CODIGO CARRERA`. El congelado se agrego por `CODIGO_UNICO = I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}`, usando como matricula vigente solo `VIG in (1,2)`.

## Limitacion de publicacion agregada

`publicacion2026.xlsx` no contiene RUT ni registros individuales. Por eso se identifican codigos con diferencia y RUT/repeticiones dentro del congelado, pero no se puede afirmar que un RUT institucional especifico fue contado o no contado en la publicacion.

## Desglose completo por codigo

La tabla completa esta en `01_RESUMEN_POR_CODIGO`. Totales: publicacion pregrado 3371, vigente congelado 3205, diferencia neta 166.

## Concentracion de diferencias

- Suma diferencias positivas: 186.
- Suma diferencias negativas absolutas: 20.
- Neto: 166.
- Codigos para 25% de positivos: 3.
- Codigos para 50% de positivos: 8.
- Codigos para 75% de positivos: 16.
- Codigos para 90% de positivos: 24.

### Mayores diferencias positivas

| CODIGO_UNICO | TOTAL_PUBLICACION | CONGELADO_VIGENTE | VIG_0 | DIF_PUBLICACION_VS_VIGENTE | CLASIFICACION_DIAGNOSTICA |
| --- | --- | --- | --- | --- | --- |
| I162S2C91J2V1 | 112 | 93 | 42 | 19 | CON_MULTIPLES_HALLAZGOS |
| I162S2C91J1V1 | 87 | 69 | 28 | 18 | SIN_HALLAZGOS_DE_DUPLICIDAD |
| I162S2C114J2V1 | 94 | 79 | 11 | 15 | CON_MULTIPLES_HALLAZGOS |
| I162S2C57J4V1 | 257 | 246 | 52 | 11 | CON_REPETICION_MISMA_MATRICULA |
| I162S2C76J4V1 | 132 | 122 | 56 | 10 | CON_MULTIPLES_HALLAZGOS |
| I162S2C112J4V1 | 66 | 57 | 8 | 9 | CON_MULTIPLES_HALLAZGOS |
| I162S2C83J4V1 | 94 | 85 | 46 | 9 | CON_MULTIPLES_HALLAZGOS |
| I162S2C76J2V1 | 25 | 18 | 15 | 7 | SIN_HALLAZGOS_DE_DUPLICIDAD |
| I162S2C89J4V1 | 37 | 30 | 14 | 7 | SIN_HALLAZGOS_DE_DUPLICIDAD |
| I162S2C113J4V1 | 33 | 27 | 10 | 6 | CON_MULTIPLES_HALLAZGOS |
| I162S2C88J4V1 | 52 | 46 | 26 | 6 | SIN_HALLAZGOS_DE_DUPLICIDAD |
| I162S2C47J4V1 | 111 | 105 | 34 | 6 | CON_MULTIPLES_HALLAZGOS |
| I162S2C111J4V1 | 30 | 24 | 9 | 6 | SIN_HALLAZGOS_DE_DUPLICIDAD |
| I162S2C87J4V1 | 5 | 0 | 0 | 5 | SIN_HALLAZGOS_DE_DUPLICIDAD |
| I162S2C77J4V1 | 98 | 93 | 35 | 5 | CON_MULTIPLES_HALLAZGOS |

### Diferencias negativas

| CODIGO_UNICO | TOTAL_PUBLICACION | CONGELADO_VIGENTE | VIG_0 | DIF_PUBLICACION_VS_VIGENTE | CLASIFICACION_DIAGNOSTICA |
| --- | --- | --- | --- | --- | --- |
| I162S2C3J4V2 | 153 | 158 | 22 | -5 | CON_MULTIPLES_HALLAZGOS |
| I162S2C1J4V2 | 239 | 242 | 44 | -3 | CON_MULTIPLES_HALLAZGOS |
| I162S2C22J4V2 | 36 | 39 | 4 | -3 | CON_REPETICION_MISMA_MATRICULA |
| I162S2C1J4V3 | 86 | 88 | 1 | -2 | CON_REPETICION_MISMA_MATRICULA |
| I162S2C119J4V1 | 28 | 29 | 22 | -1 | CON_MULTIPLES_HALLAZGOS |
| I162S2C1J1V2 | 34 | 35 | 2 | -1 | CON_MULTIPLES_HALLAZGOS |
| I162S2C46J4V1 | 78 | 79 | 4 | -1 | CON_REPETICION_MISMA_MATRICULA |
| I162S2C76J1V1 | 7 | 8 | 4 | -1 | CON_MULTIPLES_HALLAZGOS |
| I162S2C77J2V1 | 20 | 21 | 10 | -1 | CON_REPETICION_MISMA_MATRICULA |
| I162S2C77J4V2 | 32 | 33 | 3 | -1 | CON_REPETICION_MISMA_MATRICULA |
| I162S2C79J2V1 | 25 | 26 | 14 | -1 | CON_MULTIPLES_HALLAZGOS |

## RUT repetidos y matriculas repetidas

- Grupos de RUT repetidos: 94.
- Grupos de matricula repetida: 0.
- Grupos de duplicado exacto de 32 campos: 0.
- Personas en multiples carreras: 0.

Estos hallazgos son diagnosticos y no fueron descontados de la matricula.

## Registros VIG=0

Se identificaron 960 registros `VIG=0`; no fueron sumados al vigente. El resumen por codigo esta en `13_RESUMEN_VIG0_CODIGO` y el detalle completo en `14_DETALLE_VIG0`.

## Punto 0 versus complemento 95

El complemento 95 fue comparado contra Punto 0 por persona, matricula y fila exacta. La hoja `16_PUNTO0_VS_COMPLEMENTO95` contiene coincidencias y registros nuevos reales por codigo.

## Simulaciones

Se calcularon escenarios diagnosticos por codigo: registros vigentes originales, personas unicas vigentes, llaves de matricula unicas, vigentes sin duplicado exacto y vigentes sin repeticion de llave matricula. Ningun escenario se declara como regla de publicacion.

## Codigos prioritarios

Se generaron fichas para: I162S2C91J2V1, I162S2C91J1V1, I162S2C114J2V1, I162S2C57J4V1, I162S2C76J4V1, I162S2C87J4V1, I162S2C77J1V1. Cada ficha localiza totales, repetidos, VIG=0 y efecto de componentes.

## Hallazgos demostrados

La diferencia se localiza numericamente por codigo: positivos 186 y negativos 20, neto 166. Hay repeticiones institucionales en el congelado, pero no demuestran por si mismas el origen de la publicacion.

## Diferencias no explicadas y pendientes

La causa documental de los 166 sigue pendiente porque falta una publicacion individual con RUT o una descarga/reporte PES que conecte esos totales agregados con registros concretos.

## Conclusion

El analisis ampliado identifica donde esta la diferencia, que duplicados/repeticiones existen y que registros no estan vigentes. No atribuye RUT a la publicacion agregada ni modifica el congelado.
