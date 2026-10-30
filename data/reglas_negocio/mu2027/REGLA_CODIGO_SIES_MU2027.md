# Regla activa de código SIES · MU 2027

D · Alexi, 29-10-2026. Activación interna H002k.

- **ANTIGUO**: Conserva código MU 2026 sin usar tipo de plan. Revisión sólo (1) código/fila no resuelta; (2) código ausente en oferta 2027; (3) VIGENCIA 3. Tipo E/plan ausente son informativos.
- **CODIGOS_SIN_HISTORIA**: Se cierran cuando exista MU 2027 por cuadratura de código y total; no solicitar listado nuevo a UMAS.
- **NUEVO**: Cohorte 2027: familia respaldada + plan/sede de tipo conocido + una única versión VIGENCIA 1 del mismo tipo.
- **REVISION_MANUAL**: Antiguo: sólo motivos 1/2/3 anteriores.; Nuevo: familia admite pero tipo no determinable o sin versión compatible; varias versiones vigentes del mismo tipo; códigos sin plan.; OTRO: revisión fuera de la vía ANTIGUO; no convertir cambios de carrera ni reingresos sin evidencia en antiguos.
- **PLAN_SIN_ADMISION_2027**: Si no hay ninguna VIGENCIA 1 en la familia, informativo (incluye tipo E); no asigna código para nuevos. Si la familia admite pero no el tipo, REVISION_REAL.

## Límites

- Oferta V06 preparada C, sustituir por carga aceptada con hash y revisión antes de carga.
- Decisión interna; no modifica norma, VIG, retención, v20, bases ni denominadores.
- No hay exportador ni archivo de carga PES; no acredita matrícula ni elegibilidad 2027.
- Sin plan anual observado no se rellena por nombre ni mayoría. Tipo por plan no se deduce de FOR_ING_ACT.

## Fuentes fijadas

| id | ruta | sha256 | clase |
|---|---|---|---|
| decision | data/paridad_codigo_sies/20261029/DECISIONES_APROBADAS_v3.json | be16b491bf0a61bbb6cc56af4567c6e21292ef8de04aa584448ed194753ed63f | D |
| enlaces_privados_H002g | /Users/alexi/.local/share/ipss/h002g_20261029/ENLACES_MU_DA.json | 56782ae435caca8c880120df3304424e5663097e6303119f3f94f4ccdd59b05b | C |
| metricas | data/paridad_codigo_sies/regla_operativa_mu_v2/METRICAS_H002i_H002j.json | 8d2018cf17ab26c89160e7cd05fd9b4ccf48271ca6811f36cf0290031ca5c5cf | C |
| oferta_2027 | oferta_academica_2027/10_entrega/etapa1_octubre_20261023_v06/CARGA_OFERTA_2027_ETAPA1_17467_20261023_V06.csv | d7fe88035cd1215d448272a9854bee0932c45c200f4f80bb58636b62a6ae4e0b | C |
| prueba_privada_H002j | /Users/alexi/.local/share/ipss/h002j_20261029/PRUEBA.json | abb86b96adb8afdc732920653777c5aeb2f708710321740c797ba2747f8a055d | C |
| tipo_plan | data/paridad_codigo_sies/regla_operativa_mu_v2/TIPO_PLAN_POR_PLAN_UMAS.json | 784af467f6ed85d08e39ea677ba35b62c113f50902d8c4ddbbf290b5045ead1f | C |
| tabla_H002 | data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json | 0ed5e17b1a452c85ab25b08ef0e65cdfc7258fd920d0f4dd40c60c9c4eb71063 | C/D |

## Métricas históricas H002j (C)

| anio | grupo | filas_mu | aciertos_H002j | acierto_H002j_pct |
|---|---|---|---|---|
| 2023 | ANTIGUO | 527 | 518 | 98.29222 |
| 2023 | NUEVO | 515 | 515 | 100.0 |
| 2023 | OTRO | 103 | 0 | None |
| 2024 | ANTIGUO | 651 | 650 | 99.84639 |
| 2024 | NUEVO | 782 | 779 | 99.616368 |
| 2024 | OTRO | 108 | 0 | None |
| 2025 | ANTIGUO | 810 | 746 | 92.098765 |
| 2025 | NUEVO | 1503 | 1419 | 94.411178 |
| 2025 | OTRO | 58 | 0 | None |
| 2026 | ANTIGUO | 1668 | 1555 | 93.22542 |
| 2026 | NUEVO | 2212 | 1969 | 89.014467 |
| 2026 | OTRO | 225 | 0 | None |

Estas métricas no son una tasa SIES ni un resultado de matrícula 2027.

## Uso

`common.codigo_sies_mu2027.asignar_codigo_mu2027(fila)` verifica hashes antes de resolver.
Antiguo: referencia exacta `fila_mu2026`; tipo E y plan ausente sólo informativos. La clasificación previa ANTIGUO debe estar acreditada por el llamador.
Nuevo: `anio=2027`, `cohorte=2027`, familia y clave de plan/sede exactos.
Sin actividad anual no se inventa plan; FOR_ING_ACT no decide regular/continuidad.

## Corrección H002l · D, Alexi, 29-10-2026

Sustituye el bloqueo de tipo E de H002k. VIGENCIA 2 permite conservar antiguos; VIGENCIA 3 bloquea.
La regla no revisa tipo de plan para conservar el código anterior. Las marcas no son decisiones pendientes.
Lista vigente: `outputs/depuracion_codigo_mu2027_20261029/LISTA_REVISION_MANUAL_MU2027_v2.json`. V1 preservada por commit y archivo original.
Nuevos: familia sin admisión es informativa; familia con admisión y sin tipo compatible requiere revisión.
La oferta V06 sigue preparada C; no se genera carga y no se alteran fuentes ni H002.
