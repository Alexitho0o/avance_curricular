# Fases 2–3 · Retención de 1er año

## Cálculo interno [C]

Se calculó desde la única base autorizada: corrida MU 2022–2026 `20260901_142342`, hash `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. Resultado preliminar por personas:

| Cohorte | Elegibles | Retenidos | Tasa |
|---:|---:|---:|---:|
| 2022 | 338 | 250 | 73,96% |
| 2023 | 512 | 395 | 77,15% |
| 2024 | 702 | 500 | 71,23% |
| 2025 | 1.503 | 1.378 | 91,68% |

El cálculo usa `ANIO_ING_ACT`, `ANIO_INFORMADO`, `VIG` y documento normalizado conservando DV 0. Cada persona cuenta una vez.

## Validación SIES [B/C/E]

La fuente 2022–2024 está gobernada como cálculo interno previo (su manifiesto dice que no es fuente SIES). La fuente 2025 es la transcripción granular del correo SIES y su manifiesto confirma que representa la referencia 2025.

| Cohorte | Interno MU | Fuente granular/tabla comparada | Diferencia retenidos | Diferencia cohorte | Estado |
|---:|---:|---:|---:|---:|---|
| 2022 | 338 / 250 | 338 / 250 | 0 | 0 | Coincide numéricamente [C] |
| 2023 | 512 / 395 | 531 / 395 | 0 | +19 SIES | Definición/exclusión pendiente [E] |
| 2024 | 702 / 500 | 715 / 505 | +5 SIES | +13 SIES | Diferencia de permanencia/corte o definición [E] |
| 2025 | 1.503 / 1.378 | 2.326 casos; 1.354 retenidos; 184 no considerar | -24 interno | +823 SIES | Definición de universo pendiente [E] |

En 2025, el manifiesto y el correo identifican la cohorte 2025; `N° de casos = retenidos + desertores = 2.142`, mientras 184 registros quedan `no_considerar`. La diferencia con 1.503 no se puede atribuir solo a segundo/tercer intake sin reconstruir ANIO_ING_ACT, programas especiales y exclusiones desde la fuente individual.

Por código único, el TSV 2025 contiene 37 códigos; la base MU 142342 no conserva `mc_codigo_unico` completo por persona, sino dimensiones `COD_SED`, `COD_CAR`, `JOR` y `VERSION`. Por eso la paridad por código único queda E: no se deben inventar correspondencias.

Los códigos con mayores volúmenes oficiales para priorizar la conciliación son, entre otros, los que concentran `ret_1_retenido` 16–66; la atribución individual requiere el diccionario UMAS–SIES vigente, no una coincidencia por nombre.

### Composición y existencia de códigos

Se compuso por persona `I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}`. La MU produce 27 códigos en 2022, 21 en 2023, 32 en 2024 y 43 en 2025. Contra los códigos de las fuentes SIES: 2022 tiene 17/17 presentes; 2023, 9/10; 2024, 24/25; 2025, 36/37. Los faltantes de código no se corrigieron por inferencia y quedan E hasta verificar oferta histórica del año correspondiente.

### Permanencia y campos de primer año

El cálculo actual usa `ANIO_INFORMADO = cohorte` y `ANIO_ING_ACT = cohorte` para formar el denominador; busca `ANIO_INFORMADO = cohorte+1` por presencia de la persona, sin exigir `VIG=1` ni el mismo código de carrera. Esto implementa permanencia institucional y permite cambios de carrera IPSS [A/D]. No usa todavía `SEM_ING_ACT`, `ANIO_ING_ORI` ni `FOR_ING_ACT` para excluir reingresos o intakes; esa diferencia metodológica explica por qué 2025 no es comparable todavía [E].

La corrección del criterio VIG produce 2022 = 250/338, 2023 = 395/512 y 2024 = 500/702, cumpliendo los valores solicitados para retenidos. Las cargas incrementales 2025 están disponibles (`2 y 3er Intake.xlsx` y `Gestion_SIES_Matrícula_Pregrado_2025.xlsx`), pero aún no se integraron al denominador porque falta aplicarles la regla de cohorte y excluir duplicaciones con MU. La diferencia 2025 permanece como definición/universo, no como deserción.

### Causas solicitadas

- 2024: tras eliminar el filtro VIG=1 se obtienen 500 retenidos. La comparación previa 505/715 es una fuente interna distinta; la brecha de 5 retenidos frente a ella queda E hasta cruzar cargas posteriores y programas especiales.
- 2025: la brecha 1.503 versus 2.326 incluye 184 `no_considerar` oficiales y posibles diferencias de definición de primer año, intake y programas; queda E, no deserción.
- 2023: las 19 personas adicionales de cohorte SIES quedan E por diferencias de universo/exclusión; los retenidos ya coinciden (395).

## Validación V24 [E]

No se leyeron valores de V24 para construir el cálculo. La comparación secundaria queda pendiente hasta cerrar la extracción independiente de SIES y las exclusiones de programas especiales.

## Diferencias y límites

### Tres definiciones que no deben mezclarse

| Definición | Cohorte y filtros | Retenido | Resultado/estado |
|---|---|---|---|
| SIES oficial [A] | Universo oficial de primer año; exclusiones y `no_considerar` del reporte SIES | Presencia en MU de `t+1` de IPSS, cualquier VIG | Validación externa; 2025 E hasta integrar 2.º/3.er intake |
| Diagnóstico H001 [C/D] | Denominadores 305/366/558/1.150 y padrón institucional del hito | Criterio del diagnóstico anual | Indicador interno separado |
| Código nuevo [C] | MU 142342, `ANIO_INFORMADO`/`ANIO_ING_ACT`, persona una vez | Presencia en `t+1`, cualquier VIG | Reproduce la lógica oficial; no activa la regla |

La auditoría VIG gobernada (ruta y hash consignados en la regla) registra 960 VIG=0 en el envío 2026 por controles de nómina. No se revierten ni se cuentan automáticamente como retención: falta fundamento académico individual. Esta decisión no se extrapola retrospectivamente a 2023–2025, donde la definición SIES se evalúa por presencia en MU de `t+1`.

No se clasifican diferencias como error de código mientras no exista una tabla SIES comparable y una clasificación gobernada de programas especiales. La regla permanece `BORRADOR_NO_ACTIVO`; no se propone activación.

La comprobación de versiones posteriores de MU 2025 no confirma que los VIG=0 sean meramente provisionales: entre los 52 retenidos de cohorte 2024 con VIG=0, solo 8 aparecen con VIG=1 en las tres fuentes posteriores; entre los 2 casos análogos de cohorte 2023, solo 1. Se mantiene una única regla de cálculo por presencia para reproducir 2022–2024 y 2025 queda E; los 960 controles VIG=0 no se cuentan como retenidos hasta contar con una versión final validada y la cohorte completa.
