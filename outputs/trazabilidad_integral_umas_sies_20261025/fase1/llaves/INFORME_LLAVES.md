# Fase1/H3 — auditoría de llaves del libro original

B/C — Fuente `RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx`; SHA-256 `20fe8438cba065f15240f1e67c066e5feb8bac8841f182864e40ca7bc9512aa8`. Lectura de 2,379 filas de hoja9 y 10,200 filas de hoja11. No se modifica ningún archivo fuente ni denominador.

| Control observado B/C | Filas de hoja9 |
|---|---:|
| filas_analiticas | 2379 |
| coincidencia_unica | 2379 |
| primero_codigo_coincide_con_codigo_excel | 2379 |
| codigo_excel_en_alguna_fila_mu | 2379 |
| codigo_excel_respaldado_tipo_jornada_modalidad | 2379 |
| retenidos | 1476 |
| llave_repetida | 0 |
| sin_match | 0 |
| varios_codigos_completos | 0 |
| repetidos_mismo_codigo | 0 |
| codigo_excel_no_coincide_primera_fila_mu | 0 |
| codigo_excel_no_en_ninguna_fila_mu_de_llave | 0 |
| primera_jornada_difiere | 0 |
| primera_modalidad_difiere | 0 |
| primer_tipo_doc_difiere | 0 |
| sin_candidato_tipo_jornada_modalidad | 0 |
| varios_codigos_tras_tipo_jornada_modalidad | 0 |
| catalogo_nombre_sin_match | 0 |
| catalogo_nombre_varios_codcar | 0 |
| llave_candidatos_varias_sedes | 0 |
| llave_candidatos_varias_jornadas | 0 |
| llave_candidatos_varias_versiones | 0 |
| llave_candidatos_varios_tipos_doc | 0 |
| identidad_o_clave_con_comodin | 0 |

## Por cohorte

| Cohorte | Filas | Retenidos | Llave repetida | Varios códigos candidatos | Código no coincide con primera fila MU | Código fuera de todos los candidatos |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 305 | 224 | 0 | 0 | 0 | 0 |
| 2023 | 366 | 258 | 0 | 0 | 0 | 0 |
| 2024 | 558 | 326 | 0 | 0 | 0 | 0 |
| 2025 | 1150 | 668 | 0 | 0 | 0 | 0 |

C — U obtiene COD_CAR por VLOOKUP del nombre; V/W usan primera coincidencia de cohorte+N_DOC+DV+COD_CAR; X concatena sede/version de la primera fila MU y jornada de hoja9. La clave no incluye tipo documental, jornada, modalidad ni versión.

C — QA: {"original_intacto": true, "formulas_evaluadas_hoja9": 9516, "formulas_evaluadas_AH": 10200, "formulas_fuera_del_patron": 0, "cache_reproduccion_U_V_W_X_distinto": 0, "cache_AH_distinto": 0, "contraste_sqlite_independiente_discrepancias": 0, "conserva_denominador": true, "conserva_retenidos": true}.

C/E — Una llave repetida no demuestra un error: separar filas iguales, mismo código y códigos distintos. Coincidencia de componentes tampoco acredita por sí sola CODCLI/plan ni aceptación SIES. Los candidatos se preservan para revisar; no se adjudica otra versión.

C — Detalle con claves/fila/candidatos solo en ruta privada registrada en RESULTADOS_AGREGADOS.json. Las tablas de este informe son agregadas.

E — Este hito no amplía a Fase2 ni declara resuelta la equivalencia institucional completa.
