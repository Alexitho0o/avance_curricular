# Brechas agregadas de matrícula 2022–2025

B/C — Fase 2/6, diagnóstico de fuentes agregadas. No modifica Excel, fuentes, códigos ni denominadores. Diferencias expresadas como publicación menos MU. Los conteos son registros de matrícula agregados, no personas deduplicadas ni tasas de retención.

## Resultado por año

| Año | Códigos | Publicación pregrado | MU total | MU VIG1 | Δ total | Δ VIG1 | Códigos Δ VIG1 | Clase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 27 | 1033 | 1038 | 1033 | -5 | 0 | 0 | B/C |
| 2023 | 21 | 1142 | 1145 | 1142 | -3 | 0 | 2 | B/C |
| 2024 | 32 | 1455 | 1541 | 1455 | -86 | 0 | 0 | B/C |
| 2025 | 43 | 2371 | 2371 | 2298 | 0 | 73 | 11 | B/C |

B/C — En 2022 y 2024 los códigos publicados coinciden contra VIG1; los códigos solo MU tienen cero filas VIG1. No hay compensación entre códigos bajo ese filtro y esto no acredita una equivalencia individual del 100%. En 2023 solo C46 presenta -1 y +1 entre dos códigos: se compensan al agregar carrera. En 2025 los 43 códigos de pregrado coinciden contra MU total; 11 códigos de 8 carreras difieren contra VIG1 en 73 registros.

## Compensación exacta 2023

| Código | Publicación | MU total | MU VIG1 | Δ total | Δ VIG1 | Clase |
| --- | --- | --- | --- | --- | --- | --- |
| I162S2C46J1V1 | 6 | 7 | 7 | -1 | -1 | B/C; causa E |
| I162S2C46J2V1 | 41 | 42 | 41 | -1 | 0 | B/C; causa E |
| I162S2C46J4V3 | 173 | 172 | 172 | 1 | 1 | B/C; causa E |

E — La coincidencia de C46 a nivel carrera no demuestra qué matrícula cambió de código ni que ocurrió una reclasificación. Cambian a la vez jornada y versión entre los dos códigos con diferencia; no se asigna una causa por ese patrón.

## Diferencia de 73 en 2025 por carrera

| COD_CAR | Carrera | Publicación | MU total | MU VIG1 | Δ VIG1 | Clase |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | INGENIERIA EN INFORMATICA | 351 | 351 | 334 | 17 | B/C; causa E |
| 3 | INGENIERIA EN CONECTIVIDAD Y REDES | 302 | 302 | 297 | 5 | B/C; causa E |
| 6 | TECNICO EN CONECTIVIDAD Y REDES | 71 | 71 | 64 | 7 | B/C; causa E |
| 46 | INGENIERIA EN CIBERSEGURIDAD | 375 | 375 | 366 | 9 | B/C; causa E |
| 47 | TECNICO EN CIBERSEGURIDAD | 166 | 166 | 157 | 9 | B/C; causa E |
| 57 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 356 | 356 | 332 | 24 | B/C; causa E |
| 76 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | 123 | 123 | 122 | 1 | B/C; causa E |
| 78 | TECNICO EN ADMINISTRACION DE EMPRESAS | 85 | 85 | 84 | 1 | B/C; causa E |

B — La auditoría agregada preservada en data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json registra VIG0=5,3,86,73 para 2022–2025 y ningún VIG2. También documenta 0 cambios VIG entre fuentes anuales y base consolidada, incluido alias 2025 VIGENCIA→VIG. Son resultados de esa auditoría previa; este subestudio no relee personas. C — Por esas fuentes concretas, VIG1 y VIG1 o 2 dan el mismo conteo; no son una regla universal intercambiable.

E — Que publicación 2025 coincida con total MU no permite afirmar que SIES publicó exactamente a las 73 personas/filas VIG0. Falta una trazabilidad de carga/publicación o criterio que lo explique; tampoco son automáticamente errores de vigencia. El estudio de nóminas 2026 no se extrapola retrospectivamente a 2025.

## Todas las diferencias por código

| Año | Código | Presencia | Publicación | MU total | MU VIG1 | Δ total | Δ VIG1 | Clase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | I162S2C11J2V1 | AMBAS | 8 | 9 | 8 | -1 | 0 | B/C; causa E |
| 2022 | I162S2C3J2V1 | SOLO_MU | Ausente | 2 | 0 | -2 | 0 | B/C; causa E |
| 2022 | I162S2C46J2V1 | AMBAS | 39 | 40 | 39 | -1 | 0 | B/C; causa E |
| 2022 | I162S2C57J1V1 | AMBAS | 30 | 31 | 30 | -1 | 0 | B/C; causa E |
| 2023 | I162S2C3J2V4 | AMBAS | 29 | 30 | 29 | -1 | 0 | B/C; causa E |
| 2023 | I162S2C46J1V1 | AMBAS | 6 | 7 | 7 | -1 | -1 | B/C; causa E |
| 2023 | I162S2C46J2V1 | AMBAS | 41 | 42 | 41 | -1 | 0 | B/C; causa E |
| 2023 | I162S2C46J4V3 | AMBAS | 173 | 172 | 172 | 1 | 1 | B/C; causa E |
| 2023 | I162S2C57J4V1 | AMBAS | 252 | 253 | 252 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C11J2V1 | SOLO_MU | Ausente | 1 | 0 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C1J1V2 | AMBAS | 16 | 17 | 16 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C1J2V4 | AMBAS | 28 | 29 | 28 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C1J4V2 | AMBAS | 231 | 237 | 231 | -6 | 0 | B/C; causa E |
| 2024 | I162S2C1J4V3 | AMBAS | 1 | 2 | 1 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C3J1V2 | SOLO_MU | Ausente | 1 | 0 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C3J4V2 | AMBAS | 267 | 276 | 267 | -9 | 0 | B/C; causa E |
| 2024 | I162S2C3J4V3 | SOLO_MU | Ausente | 2 | 0 | -2 | 0 | B/C; causa E |
| 2024 | I162S2C46J2V1 | AMBAS | 42 | 43 | 42 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C46J4V3 | AMBAS | 233 | 243 | 233 | -10 | 0 | B/C; causa E |
| 2024 | I162S2C47J2V1 | AMBAS | 12 | 16 | 12 | -4 | 0 | B/C; causa E |
| 2024 | I162S2C47J4V1 | AMBAS | 117 | 123 | 117 | -6 | 0 | B/C; causa E |
| 2024 | I162S2C57J2V1 | AMBAS | 24 | 27 | 24 | -3 | 0 | B/C; causa E |
| 2024 | I162S2C57J4V1 | AMBAS | 275 | 282 | 275 | -7 | 0 | B/C; causa E |
| 2024 | I162S2C6J1V2 | AMBAS | 1 | 2 | 1 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C6J2V2 | AMBAS | 6 | 7 | 6 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C6J4V2 | AMBAS | 63 | 66 | 63 | -3 | 0 | B/C; causa E |
| 2024 | I162S2C76J1V1 | SOLO_MU | Ausente | 1 | 0 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C76J2V1 | AMBAS | 1 | 3 | 1 | -2 | 0 | B/C; causa E |
| 2024 | I162S2C76J4V1 | AMBAS | 7 | 12 | 7 | -5 | 0 | B/C; causa E |
| 2024 | I162S2C77J2V1 | AMBAS | 7 | 9 | 7 | -2 | 0 | B/C; causa E |
| 2024 | I162S2C78J1V1 | SOLO_MU | Ausente | 1 | 0 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C78J2V1 | AMBAS | 7 | 11 | 7 | -4 | 0 | B/C; causa E |
| 2024 | I162S2C78J4V1 | AMBAS | 8 | 12 | 8 | -4 | 0 | B/C; causa E |
| 2024 | I162S2C79J2V1 | AMBAS | 8 | 9 | 8 | -1 | 0 | B/C; causa E |
| 2024 | I162S2C79J4V1 | AMBAS | 15 | 23 | 15 | -8 | 0 | B/C; causa E |
| 2025 | I162S2C1J2V4 | AMBAS | 24 | 24 | 21 | 0 | 3 | B/C; causa E |
| 2025 | I162S2C1J4V2 | AMBAS | 254 | 254 | 240 | 0 | 14 | B/C; causa E |
| 2025 | I162S2C3J4V2 | AMBAS | 244 | 244 | 239 | 0 | 5 | B/C; causa E |
| 2025 | I162S2C46J2V1 | AMBAS | 36 | 36 | 34 | 0 | 2 | B/C; causa E |
| 2025 | I162S2C46J4V3 | AMBAS | 264 | 264 | 257 | 0 | 7 | B/C; causa E |
| 2025 | I162S2C47J4V1 | AMBAS | 140 | 140 | 131 | 0 | 9 | B/C; causa E |
| 2025 | I162S2C57J2V1 | AMBAS | 25 | 25 | 24 | 0 | 1 | B/C; causa E |
| 2025 | I162S2C57J4V1 | AMBAS | 306 | 306 | 283 | 0 | 23 | B/C; causa E |
| 2025 | I162S2C6J4V2 | AMBAS | 63 | 63 | 56 | 0 | 7 | B/C; causa E |
| 2025 | I162S2C76J4V1 | AMBAS | 84 | 84 | 83 | 0 | 1 | B/C; causa E |
| 2025 | I162S2C78J4V1 | AMBAS | 74 | 74 | 73 | 0 | 1 | B/C; causa E |

C — Ausente significa que no existe fila de ese código/año en el CSV publicado. Para calcular la diferencia de la unión se usa un cero estructural, no una matrícula publicada igual a cero. El JSON conserva ambos conceptos por separado. AMBAS indica presencia en las dos fuentes; SOLO_MU, presencia únicamente en MU.

## Alcance y documentación previa

B/C — Los códigos presentes solo en MU de 2022/2024 tienen cero VIG1, de modo que la diferencia corresponde al filtro observado; no se necesita afirmar una reclasificación para reconciliar los conteos. Postítulo se conserva aparte y no se suma a MU pregrado. El detalle está en EXCEPCIONES_Y_FUENTES.json.

B/E — El manifiesto del puente, su resumen por carrera y README H001 de 30-sep afirman que las diferencias eran reclasificación jornada/versión y que todas las causas salvo 2025 estaban explicadas. La reproducción confirma sus números pero no esa causalidad: para 2022/2024 no hay diferencias frente a VIG1 entre los códigos publicados y los solo MU tienen cero VIG1; para 2023 hay compensación aritmética cuya causa sigue pendiente. Se conserva íntegra la evidencia anterior y se documenta aquí su límite, sin reescribirla.

B/E — El manifiesto de consolidación registra FECHA_MATRICULA ausente en 2022/2023, FECH_CAR descartada en 2022/2024/2025 y columnas distintas por edición. No convierte la fecha de generación/exportación en fecha efectiva de matrícula. Este subestudio no acredita nuevos cortes temporales.

## QA y fuentes

C — QA técnico: 123 códigos/año; 46 excepciones; 47 agregados carrera/año reproducen las cinco columnas numéricas del resumen gobernado. No se exportaron identificadores. Hashes antes/después idénticos. Fuentes y copia integrada/original verificadas en el JSON.

- B — `puente`: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv`; SHA-256 `d4f3675d5d63247b0118412f983729cb18924c2971cea1b7d0ef731e6c8e7803`.
- B — `resumen_carrera`: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU_RESUMEN_POR_CARRERA.csv`; SHA-256 `d17e02be25e979c96dcafac407e7496426b067fbdc4d4f9ee6380923fdd66f00`.
- B — `manifest_puente`: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json`; SHA-256 `c205fed8061bc02ea2623eea8d789ffc1bc1355e41f82bb1298d319bd76b08ad`.
- B — `manifest_publicacion`: `/Users/alexi/Documents/GitHub/avance_curricular/procesos/caracterizacion/gobernanza/sies/MATRICULA_2007_2026.manifest.json`; SHA-256 `dcf5a3400b4f0335cd8ba3eb3bd255c08713e0f9fff472e7043100a8b58b64cc`.
- B — `manifest_mu`: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json`; SHA-256 `746539ed62a3a3a051da14fd7f32b90fc6fd30a426304386d54e19c203d74145`.
- B — `auditoria_vig_agregada`: `/Users/alexi/Documents/GitHub/avance_curricular/data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json`; SHA-256 `003c55b57e2aa476a8bd6d9223ec46d4155f59f7311d0183eea24c795226cff0`.
- B — `auditoria_vig_informe`: `/Users/alexi/Documents/GitHub/avance_curricular/data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md`; SHA-256 `7ccfc88001e7e36ef3299d52dc5f7d6448bce63b995da1aa400634e465774f00`.
- B — `readme_hito`: `/Users/alexi/Documents/GitHub/avance_curricular/manifests/milestones/H001-RETENCION-IPSS162/README.md`; SHA-256 `6f1184f40f91d2c0df73fed2296cd11323aa108ce1cb30474bb000b8bdef7c48`.
- B — `conciliacion_actual`: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/RESULTADOS.json`; SHA-256 `3bc390117918e72438557435b8d031fbf71f152b00bf9abf452bab82282e1005`.
- B — `detalle_conciliacion_actual`: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/DETALLE_CONCILIACION.csv`; SHA-256 `f60b2e327f016ca1abeb8f26f65d11b4b9ebdbaff785a9a4912c40bb21235eaa`.

B/C — Contraste adicional con la nueva reconstrucción de esta Fase 2: DETALLE_CONCILIACION.csv confirma las cinco columnas numéricas en 132 códigos/año de 2022–2025 (660 comparaciones, incluidos 9 códigos Postítulo). También confirma VIG0 y ausencia de VIG2/otros por año. Este subestudio consume sus agregados y no vuelve a leer datos individuales.

B — Localizadores: puente CSV, filas originales indicadas en cada excepción JSON; manifiesto del puente, cierre_carrera_2026_09_30 y qa.detalle; README H001 líneas 99–117; auditoría de vigencia, RESULTADOS_AGREGADOS.json → base_por_anio/fuentes_anuales_vig y AUDITORIA_VIG_ENVIOS_RETENCION.md líneas 53–66. E — La causa se declara no acreditada en este conjunto específico de evidencias, no inexistente universalmente.

C — Reproducción: ejecutar analizar_brechas.py desde cualquier directorio con Python 3. Usa únicamente CSV/JSON/Markdown agregados ya disponibles; no modifica entradas. No ejecuta commit ni push.
