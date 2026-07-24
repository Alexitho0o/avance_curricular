# Auditoría integral MU2026 publicación vs pregrado y posgrado

## Contexto y alcance

Proceso Matrícula Unificada 2026. Se comparan la publicación institucional/SIES `publicacion2026.xlsx` contra las últimas bases disponibles de Pregrado y Posgrado/Postítulo indicadas como prioritarias. No se mezclan estructuras: Pregrado usa 32 columnas y Posgrado/Postítulo usa 21 columnas.

## Fuentes y hashes

- Publicación: `/Users/alexi/Documents/GitHub/avance_curricular/publicacion2026.xlsx`. SHA-256 `9312665c74102bef111fa6618a379bfd57170b376ebc8e501ab7c92dba421da2`.
- Pregrado CSV PES-ready: `git_blob:9b2c4628c0357f5ce66debddee8034aa3a8ce54a:resultados/auditoria_multicodcli_mu2026_reconstruida_desde_cero/05_cierre_controlado/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL.csv`. SHA-256 `3d038ae0872a9e06b657c89bb3a1725c9ad2cb14a8fa4b270c737b78ae0839ac`.
- Pregrado con encabezados: `git_blob:d14e72505255ffead372ae5d014c0dfc621513f8:resultados/auditoria_multicodcli_mu2026_reconstruida_desde_cero/05_cierre_controlado/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx`. SHA-256 `1d554423e4434aa46c18b5234932e9db2eb46f88a726e4636ffb6f3b357ba405`.
- Posgrado PES-ready: `git_blob:3e44d69adc25cab16958c4317d16306b0e9eab20:resultados/matricula_unificada_2026_postgrado_postitulo.csv`. SHA-256 `a0dbff084d6b448d3443bbd68c5efd45c77b499e5ef91bb145dc8ba0d9b80111`.
- Posgrado con títulos: `git_blob:1c1d4833b5dc5637b0c1670b5823c8aab4683f93:resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv`. SHA-256 `0cd4c6343dbd886e259db5f86ecff70a08840d2b556bc398543711b66a94608a`.
- Regla/catálogo TV: `/Users/alexi/Documents/GitHub/avance_curricular/DURACION_ESTUDIOS.tsv` y `/Users/alexi/Documents/GitHub/avance_curricular/gobernanza_niveles.tsv`.

## Reglas de clasificación

`AUD_TV` corresponde al `CODIGO_UNICO`. La clasificación se obtiene por fórmula contra `tblReglaTV`, construido desde `DURACION_ESTUDIOS.tsv` y `gobernanza_niveles.tsv`. Todos los códigos del universo auditado fueron encontrados en el catálogo local.

## Estructuras

- Pregrado: 4.105 registros, 32 columnas, sin encabezado en CSV final, cuerpo del Excel con encabezados coincide exactamente.
- Posgrado/Postítulo: 54 registros, 21 columnas, PES-ready sin encabezado coincide con cuerpo del archivo con títulos.
- Publicación: 66 filas de datos, 58 columnas, agregada por código/nivel; no contiene RUT.

## Totales recalculados

| Indicador | Publicación | Institucional | Diferencia |
|---|---:|---:|---:|
| Pregrado | 3.371 | 3.145 | 226 |
| Posgrado/Postítulo | 54 | 54 | 0 |
| Total | 3.425 | 3.199 | 226 |

## Comparación por código

La hoja `11_RESUMEN_POR_CODIGO` contiene el cruce completo con fórmulas. La diferencia integral se concentra en pregrado; posgrado/postítulo queda conciliado.

## Duplicados y multimatrícula

La hoja `17_DUPLICADOS_Y_MULTIMATRICULA` reporta diagnósticos institucionales. No se eliminan registros automáticamente y matrícula no se presenta como persona única.

## Limitaciones

La publicación es agregada; por tanto no es posible demostrar presencia o ausencia de RUT individuales en la publicación. Las fuentes pregrado/posgrado prioritarias fueron recuperadas como blobs Git, no como archivos físicos del árbol actual, aunque sus hashes coinciden con los controles esperados.

## Pendientes

Ver `20_PENDIENTES`: granularidad individual de publicación y materialización física actual de algunas fuentes fuera del historial Git.

## Conclusión

Estado final: `AUDITORIA_INTEGRAL_COMPLETADA`. El libro permite auditar fuentes, hashes, RAW, reglas, fórmulas y totales sin depender de explicaciones externas.
