# Lectura de codigo_gobernanza_v2.py para columnas 16-19

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Fuente técnica: `codigo_gobernanza_v2.py`  

## Resultado

- Líneas relevantes encontradas: 4434
- Funciones relevantes encontradas: 93
- Bloques de diccionario/lógica encontrados: 128

## Funciones relevantes

| FUNCION                                      |   LINEA_INICIO |   LINEA_FIN |
|:---------------------------------------------|---------------:|------------:|
| _parse_sies_codigo_unico                     |             27 |          37 |
| _split_codcarpr_candidates                   |             38 |          51 |
| _load_duracion_as_governance_df              |             52 |          67 |
| _cargar_matriz_desambiguacion_desde_duracion |             68 |         203 |
| _first_existing_path                         |            204 |         211 |
| _default_input_arg                           |            212 |         218 |
| _resolve_optional_path                       |            219 |         225 |
| _normalize_doc                               |            226 |         229 |
| _rut_num_only                                |            230 |         257 |
| _pick_sheet                                  |            258 |         265 |
| _series_or_default                           |            266 |         271 |
| _normalize_text                              |            272 |         280 |
| _nonempty_mask                               |            281 |         284 |
| _to_int_year                                 |            285 |         291 |
| _infer_year_from_codcli                      |            292 |         302 |
| _infer_sem_from_codcli                       |            303 |         316 |
| _infer_codcarpr_from_codcli                  |            317 |         330 |
| _pick_first_column                           |            331 |         338 |
| _require_column                              |            339 |         344 |
| _load_for_ing_act_catalog                    |            345 |         355 |
| _normalize_semester_scalar                   |            356 |         369 |
| _load_da_origin_records                      |            370 |         399 |
| _sem_sort_value                              |            400 |         412 |
| _load_for_ing_act_tns_origin_trace           |            413 |         448 |
| _lookup_previous_origin_for_row              |            449 |         493 |
| _apply_for_ing_act_origin_rules              |            494 |         508 |
| set_origin                                   |            509 |         520 |
| set_origin_at                                |            521 |         614 |
| _normalize_period_to_semester                |            615 |         623 |
| _trimester_level_to_semester                 |            624 |         643 |
| _normalize_grade_to_mu_scale                 |            644 |         657 |
| _coerce_mu_average                           |            658 |         667 |
| _build_mu_historico_summary                  |            668 |         755 |
| _resolve_for_ing_act_row                     |            756 |         762 |
| _numeric_code                                |            763 |         900 |
| _build_for_ing_act_report_payload            |            901 |        1017 |
| _map_jornada_to_mod_jor                      |           1018 |        1047 |
| _extract_shared_cod_car_from_potenciales     |           1048 |        1059 |
| _build_nombre_carrera_to_cod_car             |           1060 |        1083 |
| _normalize_nombre_carrera_for_lookup         |           1084 |        1092 |
| _extract_sies_components                     |           1093 |        1106 |
| _modalidad_from_jor                          |           1107 |        1115 |
| _normalize_sexo_mu                           |           1116 |        1136 |
| _to_ddmmyyyy                                 |           1137 |        1144 |
| _load_datos_alumnos_lookup                   |           1145 |        1244 |
| _status_from_vig                             |           1245 |        1251 |
| _build_bridge_codcarpr_to_codcar             |           1252 |        1265 |
| _build_revision_manual                       |           1266 |        1331 |
| _write_excel_atomic                          |           1332 |        1371 |
| _write_mu_csv_atomic                         |           1372 |        1395 |

## Bloques de diccionario o lógica

|   LINEA | TEXTO                                                                                                                                          |
|--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------|
|     173 | DEFAULT_GOB_HOJA1_ESTADO_DESC_CANDIDATES = [                                                                                                   |
|     181 | DEFAULT_GOB_DA_ESTADO_SITUACION_CANDIDATES = [                                                                                                 |
|     680 | extra_cols = [c for c in ["DESCRIPCION_ESTADO", "ESTADO", "CONVALIDADO", "NOTA_FINAL"] if c in src.columns]                                    |
|     693 | hist["ESTADO_HIST_NORM"] = _series_or_default(hist, "DESCRIPCION_ESTADO").map(_normalize_text)                                                 |
|     694 | hist["CONVALIDADO_NORM"] = _series_or_default(hist, "CONVALIDADO").map(_normalize_text)                                                        |
|     708 | estado_ref = sub_ref["ESTADO_HIST_NORM"]                                                                                                       |
|     709 | estado_hist = sub["ESTADO_HIST_NORM"]                                                                                                          |
|     710 | transfer_ref = estado_ref.str.contains(r"CONVALID|HOMOLOG|RECONOC|EQUIV", regex=True, na=False) | sub_ref["CONVALIDADO_NORM"].eq("S")          |
|     713 | aprob_ref = estado_ref.str.contains("APROB", na=False) & ~transfer_ref                                                                         |
|     714 | aprob_hist = estado_hist.str.contains(r"APROB|CONVALID|RECONOC|EQUIV|HOMOLOG", regex=True, na=False)                                           |
|     737 | "UZ_HIST_FILAS_REF_REPROB": int(estado_ref.str.contains("REPROB", na=False).sum()),                                                            |
|     742 | "ASI_APR_ANT_HIST": int(codramo_ref[aprob_ref].nunique()),                                                                                     |
|     746 | "ASI_APR_HIS_HIST": int(codramo_hist[aprob_hist].nunique()),                                                                                   |
|    1435 | estado_carga.loc[candidatos.index[intra_dup]] = "EXCLUIDO_DUPLICADO_INTRA_CODCLI"                                                              |
|    1461 | estado_carga.loc[candidatos.index[dup_8col]] = "EXCLUIDO_DUPLICADO_CLAVE_CARGA"                                                                |
|    1849 | extra_hist = [c for c in ["DESCRIPCION_ESTADO", "ESTADO_ACADEMICO", "JORNADA"] if c in src.columns]                                            |
|    1852 | hist["DESCRIPCION_ESTADO"] = src["ESTADO"]                                                                                                     |
|    1969 | estado_ref = _series_or_default(s_ref, "DESCRIPCION_ESTADO").str.upper()                                                                       |
|    1970 | estado_hist = _series_or_default(sub, "DESCRIPCION_ESTADO").str.upper()                                                                        |
|    1982 | "UNIDADES_APROBADAS": codramo_ref[estado_ref.str.contains("APROB", na=False)].nunique(),                                                       |
|    1984 | "UNID_APROBADAS_TOTAL": codramo_hist[                                                                                                          |
|    1985 | estado_hist.str.contains(r"APROB|CONVALID|RECONOC|EQUIV|HOMOLOG", regex=True, na=False)                                                        |
|    2098 | out["ASI_INS_ANT"] = mat_ac.get("UNIDADES_CURSADAS", 0)                                                                                        |
|    2099 | out["ASI_APR_ANT"] = mat_ac.get("UNIDADES_APROBADAS", 0)                                                                                       |
|    2103 | out["ASI_APR_HIS"] = mat_ac.get("UNID_APROBADAS_TOTAL", 0)                                                                                     |
|    2358 | gob_hoja1_estado_desc_path = _first_existing_path(DEFAULT_GOB_HOJA1_ESTADO_DESC_CANDIDATES)                                                    |
|    2359 | gob_da_estado_situ_path = _first_existing_path(DEFAULT_GOB_DA_ESTADO_SITUACION_CANDIDATES)                                                     |
|    2360 | gob_hoja1_estado_desc_df = _load_governance_tsv(                                                                                               |
|    2362 | ["ESTADO_ACADEMICO", "DESCRIPCION_ESTADO", "VIG_ESPERADO"],                                                                                    |
|    2364 | gob_da_estado_situ_df = _load_governance_tsv(                                                                                                  |
|    2366 | ["ESTADOACADEMICO", "SITUACION", "VIG_ESPERADO"],                                                                                              |
|    2542 | .get("ESTADO_GOBERNANZA", pd.Series(dtype="object"))                                                                                           |
|    2965 | estado_inicial = out["VIG"].map(_status_from_vig)                                                                                              |
|    2966 | estado_inicial = estado_inicial.where(~duplicated_vig, "Matrícula Duplicada")                                                                  |
|    2967 | estado_final = estado_inicial.copy()                                                                                                           |
|    2976 | archivo_subida["ESTADO_INICIAL_REGISTRO"] = estado_inicial                                                                                     |
|    2979 | archivo_subida["ESTADO_FINAL_REGISTRO"] = estado_final                                                                                         |
|    3007 | archivo_subida["DA_ESTADOACADEMICO"] = src_work["DA_ESTADOACADEMICO"] if "DA_ESTADOACADEMICO" in src_work.columns else pd.NA                   |
|    3008 | archivo_subida["DA_SITUACION"] = src_work["DA_SITUACION"] if "DA_SITUACION" in src_work.columns else pd.NA                                     |
|    3019 | archivo_subida["UZ_HIST_FILAS_REF_APROB"] = src_work["UZ_HIST_FILAS_REF_APROB"] if "UZ_HIST_FILAS_REF_APROB" in src_work.columns else pd.NA    |
|    3020 | archivo_subida["UZ_HIST_FILAS_REF_REPROB"] = src_work["UZ_HIST_FILAS_REF_REPROB"] if "UZ_HIST_FILAS_REF_REPROB" in src_work.columns else pd.NA |
|    3072 | estado_da_norm = archivo_subida["DA_ESTADOACADEMICO"].fillna("").map(_normalize_text)                                                          |
|    3073 | situ_da_norm = archivo_subida["DA_SITUACION"].fillna("").map(_normalize_text)                                                                  |
|    3077 | da_map_df = gob_da_estado_situ_df.copy()                                                                                                       |
|    3078 | da_map_df["ESTADOACADEMICO_NORM"] = da_map_df["ESTADOACADEMICO"].map(_normalize_text)                                                          |
|    3079 | da_map_df["SITUACION_NORM"] = da_map_df["SITUACION"].map(_normalize_text)                                                                      |
|    3080 | da_map_df["KEY_DA"] = da_map_df["ESTADOACADEMICO_NORM"] + "|" + da_map_df["SITUACION_NORM"]                                                    |
|    3086 | key_da = estado_da_norm + "|" + situ_da_norm                                                                                                   |
|    3091 | estado_h1_norm = src_work.get("ESTADO_ACADEMICO", pd.Series("", index=src_work.index)).fillna("").map(_normalize_text)                         |
|    3092 | desc_h1_norm = src_work["DESCRIPCION_ESTADO"].fillna("").map(_normalize_text)                                                                  |
|    3093 | h1_map_df = gob_hoja1_estado_desc_df.copy()                                                                                                    |
|    3094 | h1_map_df["ESTADO_ACADEMICO_NORM"] = h1_map_df["ESTADO_ACADEMICO"].map(_normalize_text)                                                        |
|    3095 | h1_map_df["DESCRIPCION_ESTADO_NORM"] = h1_map_df["DESCRIPCION_ESTADO"].fillna("").map(_normalize_text)                                         |
|    3096 | h1_map_df["KEY_H1"] = h1_map_df["ESTADO_ACADEMICO_NORM"] + "|" + h1_map_df["DESCRIPCION_ESTADO_NORM"]                                          |
|    3102 | key_h1 = estado_h1_norm + "|" + desc_h1_norm                                                                                                   |
|    3106 | # Regla institucional explícita: estados sin matrícula siempre VIG=0.                                                                          |
|    3107 | force_vig0_da = estado_da_norm.isin(["TITULADO", "ELIMINADO", "SUSPENDIDO"])                                                                   |
|    3354 | {"metrica": "matricula_ok_inicial", "valor": int((estado_inicial == "Matrícula OK").sum())},                                                   |
|    3355 | {"metrica": "matricula_duplicada_inicial", "valor": int((estado_inicial == "Matrícula Duplicada").sum())},                                     |
|    3356 | {"metrica": "matricula_no_utilizada_inicial", "valor": int((estado_inicial == "Matrícula No Utilizada").sum())},                               |
|    3363 | archivo_subida["MANUAL_MATCH_STATUS"].fillna("<NA>").value_counts(dropna=False).rename_axis("estado").reset_index(name="n")                    |
|    3366 | archivo_subida["SIES_MATCH_DIAG"].fillna("<NA>").value_counts(dropna=False).rename_axis("estado").reset_index(name="n")                        |
|    3375 | homol_dict = _load_cuadro_homologacion(input_file)                                                                                             |
|    3750 | _da_sit = archivo_subida.get("DA_SITUACION", pd.Series("", index=archivo_subida.index)).fillna("").astype(str).str.strip().str.upper()         |
|    3757 | archivo_subida.loc[_m3, "FOR_ING_ACT_METODO"] = "DA_SITUACION_CAMBIO_INTERNO"                                                                  |
|    3758 | archivo_subida.loc[_m3, "FOR_ING_ACT_FUENTE_CAMPO"] = "DA_SITUACION"                                                                           |
|    3841 | ] = "CALCULADO_APROB_ANIO_REFERENCIA_EXCL_EQUIV"                                                                                               |
|    3955 | titulo_elim_susp = archivo_subida["DA_ESTADOACADEMICO"].fillna("").astype(str).str.strip().str.upper().isin(                                   |
|    3971 | flag_vig.loc[archivo_subida["DA_ESTADOACADEMICO"].fillna("").astype(str).str.strip().eq("")] = "SIN_ESTADO_DA"                                 |
|    4056 | estado_carga = pd.Series("OK_CARGA_PREGRADO", index=archivo_subida.index, dtype="object")                                                      |
|    4080 | estado_carga.loc[sin_cod_car_final] = "EXCLUIDO_SIN_MATCH_SIES"                                                                                |
|    4081 | estado_carga.loc[(estado_carga == "OK_CARGA_PREGRADO") & excl_dipl] = "EXCLUIDO_DIPLOMADO"                                                     |
|    4082 | estado_carga.loc[(estado_carga == "OK_CARGA_PREGRADO") & sin_match_da] = "EXCLUIDO_SIN_MATCH_DATOS_ALUMNOS"                                    |
|    4085 | estado_carga.loc[(estado_carga == "OK_CARGA_PREGRADO") & heuristica_sies_opaca] = "EXCLUIDO_SIES_HEURISTICA_OPACA"                             |
|    4086 | estado_carga.loc[(estado_carga == "OK_CARGA_PREGRADO") & sin_for_ing_trazable] = "EXCLUIDO_SIN_FOR_ING_ACT_TRAZABLE"                           |
|    4087 | estado_carga.loc[                                                                                                                              |
|    4088 | (estado_carga == "OK_CARGA_PREGRADO") & for_ing_continuidad_invalida                                                                           |
|    4090 | estado_carga.loc[                                                                                                                              |
|    4091 | (estado_carga == "OK_CARGA_PREGRADO") & for_ing_requires_review                                                                                |
|    4094 | included_final_mask_pre_dedupe = estado_carga == "OK_CARGA_PREGRADO"                                                                           |

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/LECTURA_CODIGO_GOBERNANZA_V2_16_19_20260704_001259/02_RESULTADOS/LECTURA_CODIGO_GOBERNANZA_V2_16_19.xlsx`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/06_gobernanza_columnas_5809/LECTURA_CODIGO_GOBERNANZA_V2_16_19_20260704_001259`
