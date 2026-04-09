# Auditoría Maestra — Gate de Entrega MU 2026

**Dictamen: ✅ LISTO PARA ENTREGA**

## Metadata
| Campo | Valor |
|-------|-------|
| Fecha/Hora | 2026-04-09 17:11:59 |
| Commit | d948941 |
| Output-Dir | /Users/alexi/Documents/GitHub/avance_curricular/resultados |
| Modo | solo-validar |
| Input | (outputs existentes) |
| Pipeline-Script | /Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py |
| Pipeline-Líneas | 5035 |

## Checklist de Componentes

| # | Check | Estado | Detalle |
|---|-------|--------|---------|
| 1 | Existencia Excel principal | ✅ OK | /Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx |
| 2 | Hojas requeridas presentes | ✅ OK | Hojas encontradas: ARCHIVO_LISTO_SUBIDA, AUDITORIA_CONSOLIDACION, CATALOGO_MANUAL, EXCLUIDOS_CARGA_PREGR, MATRICULA_UNIFICADA_32, PATCH_SIT_FON_SOL, PUENTE_SIES, RESUMEN_CARGA_PREGRADO, RESUMEN_EJECUT |
| 3 | Columnas MU32 regulatorias | ✅ OK | 32 columnas; las 32 regulatorias presentes |
| 4 | Columnas trazabilidad *_DA | ✅ OK | Presentes: ['VIG_ESPERADO_DA', 'FLAG_INCONSISTENCIA_VIG', 'ESTADOACADEMICO_DA', 'SITUACION_DA'] |
| 5 | Columnas trazabilidad *_TSV | ✅ OK | Presentes: ['NOMBRE_CARRERA_TSV', 'DURACION_ESTUDIOS_TSV', 'DURACION_TITULACION_TSV', 'DURACION_TOTAL_TSV'] |
| 6 | Cobertura DURACION por CODIGO_CARRERA | ✅ OK | 8977/8977 con COD_CAR tienen DURACION_TSV (100.0%); 0 sin match SIES |
| 7 | Rango PROM_PRI_SEM [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 8 | Rango PROM_SEG_SEM [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=695, sin decimales aparentes |
| 9 | Rango ASI_INS_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=28 |
| 10 | Rango ASI_APR_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=24 |
| 11 | ASI_APR_HIS ≤ ASI_INS_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | Coherencia OK en todos los registros |
| 12 | Rango PROM_PRI_SEM [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=698, sin decimales aparentes |
| 13 | Rango PROM_SEG_SEM [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=695, sin decimales aparentes |
| 14 | Rango ASI_INS_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=26 |
| 15 | Rango ASI_APR_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=24 |
| 16 | ASI_APR_HIS ≤ ASI_INS_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | Coherencia OK en todos los registros |
| 17 | Regla VIG=0 → 4cols=0 [ARCHIVO_LISTO_SUBIDA] | ✅ OK | VIG=0: 59 registros, todos con 4 cols=0 |
| 18 | Regla VIG=0 → 4cols=0 [MATRICULA_UNIFICADA_32] | ✅ OK | VIG=0: 17 registros, todos con 4 cols=0 |
| 19 | Verificador scripts/verificar_4_columnas_mu.py | ✅ OK | OK: columnas de trazabilidad DA presentes VALIDACION: OK |
| 20 | CSV regulatorio presente | ✅ OK | Tamaño: 140,192 bytes |
| 21 | Año anterior por período (dinámico) | ✅ OK | anio_anterior_prom=2025 == periodo_filtro_anio(2026)-1 / SEM=1 |
| 22 | PROM escala entera (sin decimales) | ✅ OK | Todos los PROM son enteros (escala MU correcta) |
| 23 | Distribución FLAG_INCONSISTENCIA_VIG | ✅ OK | Distribución: {'OK': 8977} |
| 24 | Catálogos gobernanza sin combos nuevos | ✅ OK | 9 combos en datos, todos cubiertos por catálogo (29 reglas) |
| 25 | GOB bloqueante: FOR_ING_ACT vs catálogo | ✅ OK | 4 códigos en datos, todos en catálogo (11 válidos) |
| 26 | Anexo 7 continuidad: FOR_ING_ACT {2,3,4,5,11} ⇒ ORI != ACT | ✅ OK | 0 filas continuidad auditadas, todas con ORI != ACT |
| 27 | GOB bloqueante: COD_SED vs catálogo sede | ✅ OK | 2 sedes en datos, todas en catálogo (2 válidas) |
| 28 | GOB bloqueante: NAC vs catálogo nacionalidades | ✅ OK | 9 nacionalidades en datos, todas en catálogo (15 válidas) |
| 29 | GOB bloqueante: PAIS_EST_SEC vs catálogo | ✅ OK | 1 países en datos, todos en catálogo (1 válidos) |
| 30 | GOB bloqueante: NIV_ACA vs catálogo niveles | ✅ OK | 7 niveles en datos, todos en catálogo (13 válidos) |

**Resumen**: 30 OK, 0 FAIL, 0 WARN, 0 SKIP de 30 checks

## Mapa de Linaje por Columna

### `VIG`
- **Fuentes**: Hoja1/MAT_AC VIGENCIA, DatosAlumnos (catálogo DA), Catálogos gobernanza TSV
- **Transformaciones**: Forzado a 0 por regla DA, Comparación VIG real vs esperado
- **Reglas de negocio**: TITULADO/ELIMINADO/SUSPENDIDO → VIG=0, VIG=0 ⇒ 4 columnas=0
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L117: "UNIDADES_4TO_ANIO", "UNIDADES_5TO_ANIO", "UNIDADES_6TO_ANIO", "UNIDADES_7MO_ANIO", "VIGENCIA",`
  - `L125: "UNID_APROBADAS_TOTAL", "VIGENCIA",`
  - `L1382: base_usecols = ["CODIGO_UNICO", "MODALIDAD", "JORNADA", "DURACION_ESTUDIOS", "VIGENCIA"]`
  - `L2801: vig_esperado_da = pd.Series(pd.NA, index=archivo_subida.index, dtype="Int64")`
  - `L2814: vig_esperado_da = pd.to_numeric(key_da.map(da_vig_map), errors="coerce").astype("Int64")`
  - `L2831: vig_esperado_da = vig_esperado_da.fillna(vig_esperado_h1)`

### `PROM_PRI_SEM`
- **Fuentes**: Hoja1 histórico / MAT_AC, combine_first (input + hist)
- **Transformaciones**: Escala round(promedio*100) → 100-700, PERIODO=1 → PROM_PRI_SEM, Coerción numérica con bounds
- **Reglas de negocio**: Solo REGIMEN=SEMESTRAL, Año anterior dinámico (max histórico), Solo APROBADO/REPROBADO, NOTA_FINAL entre 1 y 7
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L470: "PROM_PRI_SEM_HIST": _coerce_mu_average(sub_ref.loc[graded_ref & sem_ref.eq(1), "NOTA_MU"]),`
  - `L1827: out["PROM_PRI_SEM"] = mat_ac.get("PROM_PRI_SEM", 0)`
  - `L2585: out["PROM_PRI_SEM"] = out["PROM_PRI_SEM"].combine_first(src_work["PROM_PRI_SEM_HIST"])`
  - `L372: # Escala fuente → escala MU (100-700), documentada en gobernanza_escala_notas.tsv`
  - `L375: # Fuente 100-700  → ya en escala, usar directamente`

### `PROM_SEG_SEM`
- **Fuentes**: Hoja1 histórico / MAT_AC, combine_first (input + hist)
- **Transformaciones**: PERIODO∈{2,3} → PROM_SEG_SEM, Coerción numérica con bounds
- **Reglas de negocio**: Solo REGIMEN=SEMESTRAL, Año anterior dinámico
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L471: "PROM_SEG_SEM_HIST": _coerce_mu_average(sub_ref.loc[graded_ref & sem_ref.eq(2), "NOTA_MU"]),`
  - `L1828: out["PROM_SEG_SEM"] = mat_ac.get("PROM_SEG_SEM", 0)`
  - `L2588: out["PROM_SEG_SEM"] = out["PROM_SEG_SEM"].combine_first(src_work["PROM_SEG_SEM_HIST"])`
  - `L308: # Estructura esperada CODCLI: YYYY + periodo(1 dígito) + CODCARPR + correlativo(3 dígitos)`
  - `L346: # El histórico Hoja1 usa PERIODO=3 como equivalente operacional de segundo semestre.`

### `ASI_INS_HIS`
- **Fuentes**: Hoja1 histórico / MAT_AC UNID_CURSADAS_TOTAL, combine_first
- **Transformaciones**: Count CODRAMO distintos
- **Reglas de negocio**: ASI_APR_HIS ≤ ASI_INS_HIS, Rango 0-200
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L108: "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",`
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L468: "ASI_INS_ANT_HIST": int(codramo_ref[~transfer_ref].nunique()),`
  - `L2579: out["ASI_INS_ANT"] = out["ASI_INS_ANT"].combine_first(src_work["ASI_INS_ANT_HIST"])`
  - `L2591: out["ASI_INS_HIS"] = out["ASI_INS_HIS"].combine_first(src_work["ASI_INS_HIS_HIST"])`
  - `L468: "ASI_INS_ANT_HIST": int(codramo_ref[~transfer_ref].nunique()),`

### `ASI_APR_HIS`
- **Fuentes**: Hoja1 histórico / MAT_AC UNID_APROBADAS_TOTAL, combine_first
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: Capped ≤ ASI_INS_HIS
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L108: "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",`
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L469: "ASI_APR_ANT_HIST": int(codramo_ref[aprob_ref].nunique()),`
  - `L2582: out["ASI_APR_ANT"] = out["ASI_APR_ANT"].combine_first(src_work["ASI_APR_ANT_HIST"])`
  - `L2594: out["ASI_APR_HIS"] = out["ASI_APR_HIS"].combine_first(src_work["ASI_APR_HIS_HIST"])`
  - `L103: # Contratos oficiales (Capa C)`

### `FOR_ING_ACT`
- **Fuentes**: Hoja1/DatosAlumnos VIA_ADMISION, Catálogo gobernanza FOR_ING_ACT
- **Transformaciones**: Multi-rule resolution (token/catálogo/fallback), Mapeo textual a código numérico, Fallback código 10
- **Reglas de negocio**: Tokens especiales → códigos
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L107: "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION", "FOR_ING_ACT",`
  - `L168: DEFAULT_GOB_FOR_ING_ACT_CANDIDATES = [`
  - `L169: Path(__file__).with_name("gobernanza_for_ing_act.tsv"),`
  - `L169: Path(__file__).with_name("gobernanza_for_ing_act.tsv"),`
  - `L170: Path.cwd() / "gobernanza_for_ing_act.tsv",`
  - `L171: Path.home() / "Downloads" / "gobernanza_for_ing_act.tsv",`

### `ANIO_ING_ACT`
- **Fuentes**: Hoja1 ANOINGRESO, DatosAlumnos ANOINGRESO, Inferencia desde CODCLI
- **Transformaciones**: Validación rango 1990-2026
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L898: "ANOINGRESO",`
  - `L928: "ANOINGRESO": "DA_ANOINGRESO",`
  - `L2031: col_anio_ing = _pick_first_column(src, ["ANOINGRESO", "ANIO_INGRESO_CARRERA_ACTUAL"])`
  - `L928: "ANOINGRESO": "DA_ANOINGRESO",`
  - `L2430: anio_da_raw = src_work["DA_ANOINGRESO"] if "DA_ANOINGRESO" in src_work.columns else _na_series()`
  - `L2443: anio_act_source.loc[anio_da_mask] = "DA_ANOINGRESO"`

### `SEM_ING_ACT`
- **Fuentes**: Hoja1 PERIODOINGRESO, DatosAlumnos PERIODOINGRESO
- **Transformaciones**: Normalización período→semestre
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L899: "PERIODOINGRESO",`
  - `L929: "PERIODOINGRESO": "DA_PERIODOINGRESO",`
  - `L2032: col_sem_ing = _pick_first_column(src, ["PERIODOINGRESO", "SEM_INGRESO_CARRERA_ACTUAL"])`
  - `L929: "PERIODOINGRESO": "DA_PERIODOINGRESO",`
  - `L2459: sem_da_raw = src_work["DA_PERIODOINGRESO"] if "DA_PERIODOINGRESO" in src_work.columns else _na_series()`
  - `L2471: sem_act_source.loc[sem_da_mask] = "DA_PERIODOINGRESO"`

### `CODCLI`
- **Fuentes**: DatosAlumnos CODIGOCLIENTE
- **Transformaciones**: Normalización (strip/upper), Deduplicación por CODCLI
- **Reglas de negocio**: Drop duplicates keep first
- **Outputs**: ARCHIVO_LISTO_SUBIDA, AUDITORIA_CONSOLIDACION
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L292: def _infer_year_from_codcli(value: object) -> float:`
  - `L303: def _infer_codcarpr_from_codcli(value: object) -> str:`
  - `L308: # Estructura esperada CODCLI: YYYY + periodo(1 dígito) + CODCARPR + correlativo(3 dígitos)`
  - `L28: text = str(codigo_unico or "").strip().upper()`
  - `L40: canon_txt = str(canon or "").strip().upper()`
  - `L1123: def _consolidar_candidatos_por_codcli(`

### `VIG_ESPERADO_DA`
- **Fuentes**: Catálogos DA gobernanza, TSVs estado/situación
- **Transformaciones**: Merge/lookup desde catálogo → VIG esperado
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L2089: ["ESTADO_ACADEMICO", "DESCRIPCION_ESTADO", "VIG_ESPERADO"],`
  - `L2093: ["ESTADOACADEMICO", "SITUACION", "VIG_ESPERADO"],`
  - `L2801: vig_esperado_da = pd.Series(pd.NA, index=archivo_subida.index, dtype="Int64")`
  - `L174: Path(__file__).with_name("gobernanza_catalogos") / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
  - `L175: Path.cwd() / "gobernanza_catalogos" / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
  - `L182: Path(__file__).with_name("gobernanza_catalogos") / "gob_datosalumnos_estadoacademico_situacion.tsv",`

### `FLAG_INCONSISTENCIA_VIG`
- **Fuentes**: Derivada de VIG vs VIG_ESPERADO_DA
- **Transformaciones**: Comparación directa
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L3697: archivo_subida["FLAG_INCONSISTENCIA_VIG"] = flag_vig`
  - `L3847: # Recalcular FLAG_INCONSISTENCIA_VIG después de todas las políticas`
  - `L3854: archivo_subida["FLAG_INCONSISTENCIA_VIG"] = flag_vig_post`
  - `L686: .fillna("SIN_DATO")`
  - `L689: .replace("", "SIN_DATO")`

### `NOMBRE_CARRERA_TSV`
- **Fuentes**: DURACION_ESTUDIOS.tsv
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L25: # FUENTE ÚNICA GOBERNANZA SIES: DURACION_ESTUDIOS.tsv`
  - `L54: Path(__file__).with_name("DURACION_ESTUDIOS.tsv"),`
  - `L55: Path.cwd() / "DURACION_ESTUDIOS.tsv",`

### `DURACION_ESTUDIOS_TSV`
- **Fuentes**: DURACION_ESTUDIOS.tsv
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L25: # FUENTE ÚNICA GOBERNANZA SIES: DURACION_ESTUDIOS.tsv`
  - `L54: Path(__file__).with_name("DURACION_ESTUDIOS.tsv"),`
  - `L55: Path.cwd() / "DURACION_ESTUDIOS.tsv",`

## Puntos Clave Detectados en el Código

### filtro_periodo
- *(no detectado)*

### recalculo_4_columnas
- L1827: `out["PROM_PRI_SEM"] = mat_ac.get("PROM_PRI_SEM", 0)`
- L1828: `out["PROM_SEG_SEM"] = mat_ac.get("PROM_SEG_SEM", 0)`
- L1829: `out["ASI_INS_HIS"] = mat_ac.get("UNID_CURSADAS_TOTAL", 0)`
- L1830: `out["ASI_APR_HIS"] = mat_ac.get("UNID_APROBADAS_TOTAL", 0)`
- L2042: `col_prom_pri_sem = _pick_first_column(src, ["PROM_PRI_SEM"])`

### regla_VIG0_4cols
- *(no detectado)*

### carga_catalogos_TSV
- L174: `Path(__file__).with_name("gobernanza_catalogos") / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
- L175: `Path.cwd() / "gobernanza_catalogos" / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
- L182: `Path(__file__).with_name("gobernanza_catalogos") / "gob_datosalumnos_estadoacademico_situacion.tsv",`
- L183: `Path.cwd() / "gobernanza_catalogos" / "gob_datosalumnos_estadoacademico_situacion.tsv",`
- L334: `df = _load_governance_tsv(str(path), ["FOR_ING_ACT", "DESCRIPCION_MANUAL"])`

### columnas_DA
- L934: `"SITUACION": "DA_SITUACION",`
- L935: `"ESTADOACADEMICO": "DA_ESTADOACADEMICO",`
- L2682: `if "REINCORPORACION" not in src_work.columns and "DA_SITUACION" in src_work.columns:`
- L2734: `archivo_subida["DA_ESTADOACADEMICO"] = src_work["DA_ESTADOACADEMICO"] if "DA_ESTADOACADEMICO" in src_work.columns else p`
- L2735: `archivo_subida["DA_SITUACION"] = src_work["DA_SITUACION"] if "DA_SITUACION" in src_work.columns else pd.NA`

### columnas_TSV_duracion
- L1417: `dim["OFERTA_SOURCE_SHEET"] = "DURACION_ESTUDIOS_TSV"`
- L4009: `"NOMBRE_CARRERA": "NOMBRE_CARRERA_TSV",`
- L4010: `"DURACION_ESTUDIOS": "DURACION_ESTUDIOS_TSV",`
- L4011: `"DURACION_TITULACION": "DURACION_TITULACION_TSV",`
- L4012: `"DURACION_TOTAL": "DURACION_TOTAL_TSV",`

### escritura_excel
- L1059: `def _write_excel_atomic(`
- L1069: `with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:`
- L1071: `df.to_excel(writer, index=False, sheet_name=sheet_name[:31])`
- L4169: `_write_excel_atomic(sheets_export, out_path, red_rows_sheet="ARCHIVO_LISTO_SUBIDA", red_rows_mask=_red_mask)`
- L4815: `mu_ctrl.to_excel(output_dir / "matricula_unificada_2026_oficial.xlsx", index=False)`

### validacion_bloqueante
- L1338: `Si no encuentra, retorna DataFrame vacío (no bloqueante).`
- L3050: `# Regla de gobernanza bloqueante: combinaciones SOURCE_KEY_3 no catalogadas en SIES.`
- L3051: `sin_match_bloqueante = archivo_subida["SIES_MATCH_STATUS"].eq("SIN_MATCH_SIES") & ~archivo_subida["ES_DIPLOMADO"].fillna`
- L3052: `if sin_match_bloqueante.any():`
- L3055: `sin_match_bloqueante,`

---
## Dictamen Final

### ✅ LISTO PARA ENTREGA

Todos los checks pasaron. El archivo `archivo_listo_para_sies.xlsx` y el CSV regulatorio
son aptos para entrega oficial al SIES.

---
*Generado automáticamente por `scripts/auditoria_maestra.py` el 2026-04-09 17:11:59*