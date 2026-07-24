# Reporte comparación publicacion2026 vs congelado MU Pregrado 2026

## Contexto

Proceso: Matrícula Unificada 2026. Subproyecto: Pregrado. Año de referencia: 2026.

## Fuentes

- Publicación: `/Users/alexi/Documents/GitHub/avance_curricular/publicacion2026.xlsx`; hoja `Hoja1`; filas de datos 66; hash SHA-256 `9312665c74102bef111fa6618a379bfd57170b376ebc8e501ab7c92dba421da2`.
- Congelado seleccionado: combinado derivado desde Punto 0 `PARA_SUBIR` (4070 registros, SHA-256 `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`) más Complemento 95 V3 (95 registros, SHA-256 `1940923b7e9f811df9b5af50d0badc8563bc17ed9ce8078fbab054d221c6e1f2`).
- Hash del combinado derivado: `48a950179066b7beffd31fa46377ab2caaf46ca61edb870796aff0deecfe62e9`.

## Selección de versión congelada

Se seleccionó el paquete institucional respaldado por `control/auditoria_mu2026_punto0_complemento95` y `control/auditoria_mu2026_complemento95_cierre_final`: la carga principal Punto 0 fue validada y no modificada, y el complemento 95 V3 consta como finalizado en PES el 2026-05-11 12:55. No se encontró un único CSV combinado oficial materializado; por eso el combinado usado aquí es derivado y auditable.

## Metodología

No se modificaron fuentes originales. Se extrajeron blobs desde Git a `outputs/` y se aplicó normalización técnica: recorte de espacios, mayúsculas para claves y parseo técnico de `CÓDIGO CARRERA` a `COD_SED`, `COD_CAR`, `JOR` y `VERSION`.

## Llave utilizada

La publicación es agregada por oferta, no por persona. La comparación principal usa `CÓDIGO CARRERA` de la publicación contra `CODIGO_UNICO` derivado del congelado, solo para agregados de oferta.

## Diferencias estructurales

Clasificación: `ESTRUCTURA_DIFERENTE`. La publicación tiene 58 columnas agregadas y encabezados; el congelado tiene 32 campos MU sin encabezado y registros individuales. No es comparable a nivel persona, matrícula ni campo a campo individual.

## Diferencias de universo

- Total matrícula publicación: 3425
- Registros congelado combinado: 4165
- Personas únicas congelado: 4071
- Personas únicas publicación: no disponible
- Ofertas publicación: 66
- Ofertas congelado: 61
- Ofertas con igual total: 7
- Ofertas con total distinto: 54
- Ofertas solo publicación: 5
- Ofertas solo congelado: 0

## Diferencias campo a campo

No ejecutada para campos individuales MU, porque `publicacion2026` no contiene `TIPO_DOC`, `N_DOC`, `DV`, nombres, fechas de nacimiento, trayectoria, vigencia ni otros campos de registro. El detalle agregado por oferta está en el Excel.

## Principales variaciones

| CODIGO_UNICO | PUBLICACION_TOTAL | CONGELADO_TOTAL | Diferencia absoluta |
| --- | --- | --- | --- |
| I162S2C79J4V1 | 87 | 142.0 | -55 |
| I162S2C78J4V1 | 88 | 143.0 | -55 |
| I162S2C1J4V2 | 239 | 286.0 | -47 |
| I162S2C76J4V1 | 132 | 178.0 | -46 |
| I162S2C57J4V1 | 257 | 298.0 | -41 |
| I162S2C83J4V1 | 94 | 131.0 | -37 |
| I162S2C46J4V3 | 256 | 291.0 | -35 |
| I162S2C85J4V1 | 56 | 90.0 | -34 |
| I162S2C87J4V2 | 77 | 110.0 | -33 |
| I162S2C77J4V1 | 98 | 128.0 | -30 |

## Hallazgos críticos

- La publicación no puede usarse para afirmar altas, bajas o modificaciones persona a persona.
- Cualquier diferencia agregada es observada y no implica error ni corrección automática.
- La modalidad aparece como texto en publicación y como código en congelado; no se homologó sin evidencia local específica.

## Limitaciones

La comparación completa solicitada a nivel registro requiere una publicación con registros individuales o una fuente congelada publicada con la misma estructura agregada. El archivo combinado usado es derivado de dos congelados, no un CSV final único materializado.

## Pendientes

Ver hoja `19_PENDIENTES` del Excel.

## Conclusión

La comparación validada queda limitada a nivel agregado por oferta/carrera. La estructura de `publicacion2026` es diferente y no comparable para personas, registros de matrícula ni campos individuales MU.
