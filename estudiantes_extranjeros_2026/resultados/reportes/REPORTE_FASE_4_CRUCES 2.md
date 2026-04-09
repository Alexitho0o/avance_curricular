# Reporte fase 4 cruces - Extranjeros Regulares 2025

Fecha de ejecucion: 2026-06-18 11:55:22

## Resumen

- registros_precarga: 185
- personas_unicas_precarga: 185
- registros_locales: 104
- precarga_confirmada_exacta: 32
- precarga_confirmada_con_brechas: 138
- solo_precarga_confirmada_por_otra_fuente: 99
- solo_precarga_pendiente: 35
- solo_matricula_local_confirmado_para_agregar: 30
- solo_matricula_local_pendiente: 20
- misma_persona_distinta_carrera_resuelta_misma_matricula: 5
- segunda_matricula_real: 0
- cambios_de_carrera: 0
- duplicados_tecnicos: 13
- conflictos_resueltos: 10
- conflictos_pendientes: 6
- registros_propuestos_vigencia_0: 0
- universo_depurado_total: 257
- estudiantes_unicos: 234
- registros_persona_carrera: 254
- requiere_docencia: 191
- requiere_registro_academico: 20
- requiere_resolucion_tecnica: 33
- validaciones_error: 0
- validaciones_pendiente: 397

## Tabla final

| Grupo | Total inicial | Resueltos automaticamente | Pendientes | Incluidos | Excluidos |
|---|---:|---:|---:|---:|---:|
| Precarga confirmada | 32 | 30 | 2 | 32 | 0 |
| Solo precarga | 134 | 99 | 35 | 99 | 0 |
| Solo matricula local 2025 | 50 | 30 | 20 | 30 | 0 |
| Misma persona, distinta carrera | 22 | 13 | 9 | 0 | 13 |
| Duplicidades documentales | 8 | 0 | 8 | 0 | 0 |
| Conflictos explicitos | 16 | 10 | 6 | 0 | 0 |
| Total universo | 257 | 181 | 76 | 168 | 13 |

## Cobertura global

| Variable | Cobertura | Pendientes | Conflictos |
|---|---:|---:|---:|
| TIPO_DOCUMENTO | 100.0% | 0 | 0 |
| NUM_DOCUMENTO | 100.0% | 0 | 0 |
| DV | 90.27% | 25 | 0 |
| PRIMER_APELLIDO | 100.0% | 0 | 0 |
| SEGUNDO_APELLIDO | 95.72% | 11 | 0 |
| NOMBRES | 100.0% | 0 | 0 |
| SEXO | 100.0% | 0 | 0 |
| FECHA_NACIMIENTO | 100.0% | 1 | 1 |
| NACIONALIDAD | 58.75% | 106 | 0 |
| TIPO_RESIDENCIA_ESTUDIANTE | 0.0% | 257 | 0 |
| PAIS_DE_ORIGEN | 0.0% | 257 | 0 |
| PAIS_ESTUDIOS_SECUNDARIOS | 71.98% | 72 | 0 |
| CODIGO_UNICO | 88.33% | 32 | 2 |
| ANIO_INGRESO_CARRERA_ACTUAL | 78.99% | 56 | 2 |
| SEM_INGRESO_CARRERA_ACTUAL | 78.99% | 55 | 1 |
| ANIO_INGRESO_CARRERA_ORIGEN | 71.98% | 72 | 0 |
| SEM_INGRESO_CARRERA_ORIGEN | 71.98% | 72 | 0 |
| NOMBRE_UNIVERSIDAD_ORIGEN | 0.0% | 0 | 0 |
| PAIS_UNIVERSIDAD_ORIGEN | 0.0% | 0 | 0 |
| VIGENCIA | 100.0% | 0 | 0 |

## Hashes de salidas

- `estudiantes_extranjeros_2026/resultados/auditorias/METADATA_FASE_DEPURACION_4_CRUCES.csv`: `33fe34b3374cb898179ea36d4acd6b01f481e4d329efe61e0491e6c07ae4f607`
- `estudiantes_extranjeros_2026/resultados/auditorias/NORMALIZACION_COMUN_DEPURACION_4_CRUCES.csv`: `ec20eab0a1b419ec5e77681e0de8b8355878278a814af963246da8ae532e573b`
- `estudiantes_extranjeros_2026/resultados/auditorias/CRUCE_1_PRECARGA_CONFIRMADA.csv`: `72bdd1128b3ac15ec0ff8f22c757030465ce772d4b7557ac9caaf80e1834e7a0`
- `estudiantes_extranjeros_2026/resultados/auditorias/CRUCE_2_SOLO_PRECARGA.csv`: `e06205ce7635f0016fd58aecbf971af541a6a2d16c0c4207235ca6af4c64cb7e`
- `estudiantes_extranjeros_2026/resultados/auditorias/CRUCE_3_SOLO_MATRICULA_LOCAL_2025.csv`: `c5b410d7429788fca78983fa50652b2e5de76375dc52e41667656a4c890866a8`
- `estudiantes_extranjeros_2026/resultados/auditorias/CRUCE_4_MISMA_PERSONA_DISTINTA_CARRERA.csv`: `f4282955ba2eb935ebf0cb73507e4e90a9fff98957c39adb995246dc6312ce95`
- `estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_DUPLICIDADES_DOCUMENTALES.csv`: `3139a62425febcce7e7e63c38669963ba5351d05dc63823c13bc98556df09ebc`
- `estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_CONFLICTOS_EXPLICITOS.csv`: `167e76263bc99ba2f56f9f3207e86b8dc0e36f36251ef1a7fee6ec2fbfbb5af1`
- `estudiantes_extranjeros_2026/resultados/auditorias/UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv`: `9c78b2640f1dbec682a0850f30bd9cb0592568ccc68b864a4f80171894a72b86`
- `estudiantes_extranjeros_2026/data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025_DEPURADA.csv`: `c6ae9266a65997d9f4646a4733e65653cbfb06e42a8692b91702e159aced053a`
- `estudiantes_extranjeros_2026/resultados/archivos_gestion/NOMINA_DATOS_PERSONALES_FALTANTES.xlsx`: `cc4d50d34873985a775b7bdd7ad07bd0bd8ba9768975519107f4d30d12c78b7b`
- `estudiantes_extranjeros_2026/resultados/archivos_gestion/NOMINA_CONFIRMACION_MATRICULA_CARRERA_2025.xlsx`: `5599925b41502655985ba26164f47bdf84f419678de028ec3e315296a61a57a9`
- `estudiantes_extranjeros_2026/resultados/archivos_gestion/NOMINA_RESOLUCION_TECNICA_CODIGOS.xlsx`: `8d792069a327038209767feb6796a83fc4c8535722c16ae29320b83bb6c1e247`
- `estudiantes_extranjeros_2026/resultados/auditorias/COBERTURA_POST_4_CRUCES.csv`: `b179ddf331803b9e6aa1c006e08131e99c8e2d9276a073b64cc6062e8788923e`
- `estudiantes_extranjeros_2026/resultados/auditorias/VALIDACION_FASE_4_CRUCES.csv`: `8d43c91f55f924ba2f9ec29ce7481115ffb172b5e43904ee0892adf6d11297f1`
- `estudiantes_extranjeros_2026/resultados/auditorias/MANIFIESTO_ARCHIVOS_DEPURACION_4_CRUCES.csv`: `428590dbbaed562aa35e0621ece150b2a362280060b62c0d9e9498b77fc472a0`

No se genero archivo CSV final para PES.
