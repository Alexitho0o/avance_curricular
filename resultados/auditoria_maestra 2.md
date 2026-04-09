# Auditoría Maestra — Gate de Entrega MU 2026

**Dictamen: ✅ LISTO PARA ENTREGA**

## Metadata
| Campo | Valor |
|-------|-------|
| Fecha/Hora | 2026-04-09 08:57:47 |
| Commit | b78fdb0 |
| Output-Dir | /Users/alexi/Documents/GitHub/avance_curricular/resultados |
| Modo | solo-validar |
| Input | (outputs existentes) |
| Pipeline-Script | /Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py |
| Pipeline-Líneas | 4442 |

## Checklist de Componentes

| # | Check | Estado | Detalle |
|---|-------|--------|---------|
| 1 | Existencia Excel principal | ✅ OK | /Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx |
| 2 | Hojas requeridas presentes | ✅ OK | Hojas encontradas: ARCHIVO_LISTO_SUBIDA, AUDITORIA_CONSOLIDACION, CATALOGO_MANUAL, EXCLUIDOS_CARGA_PREGR, MATRICULA_UNIFICADA_32, PUENTE_SIES, RESUMEN_CARGA_PREGRADO, RESUMEN_EJECUTIVO, RESUMEN_MANUAL |
| 3 | Columnas MU32 regulatorias | ✅ OK | 32 columnas; las 32 regulatorias presentes |
| 4 | Columnas trazabilidad *_DA | ✅ OK | Presentes: ['VIG_ESPERADO_DA', 'FLAG_INCONSISTENCIA_VIG', 'ESTADOACADEMICO_DA', 'SITUACION_DA'] |
| 5 | Columnas trazabilidad *_TSV | ✅ OK | Presentes: ['NOMBRE_CARRERA_TSV', 'DURACION_ESTUDIOS_TSV', 'DURACION_TITULACION_TSV', 'DURACION_TOTAL_TSV'] |
| 6 | Cobertura DURACION por CODIGO_CARRERA | ✅ OK | 6142/6142 con COD_CAR tienen DURACION_TSV (100.0%); 0 sin match SIES |
| 7 | Rango PROM_PRI_SEM [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 8 | Rango PROM_SEG_SEM [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 9 | Rango ASI_INS_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=52 |
| 10 | Rango ASI_APR_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=44 |
| 11 | ASI_APR_HIS ≤ ASI_INS_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | Coherencia OK en todos los registros |
| 12 | Rango PROM_PRI_SEM [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 13 | Rango PROM_SEG_SEM [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 14 | Rango ASI_INS_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=52 |
| 15 | Rango ASI_APR_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=44 |
| 16 | ASI_APR_HIS ≤ ASI_INS_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | Coherencia OK en todos los registros |
| 17 | Regla VIG=0 → 4cols=0 [ARCHIVO_LISTO_SUBIDA] | ✅ OK | VIG=0: 46 registros, todos con 4 cols=0 |
| 18 | Regla VIG=0 → 4cols=0 [MATRICULA_UNIFICADA_32] | ✅ OK | VIG=0: 22 registros, todos con 4 cols=0 |
| 19 | Verificador scripts/verificar_4_columnas_mu.py | ✅ OK | OK: columnas de trazabilidad DA presentes VALIDACION: OK |
| 20 | CSV regulatorio presente | ✅ OK | Tamaño: 158,619 bytes |
| 21 | Año anterior por período (dinámico) | ✅ OK | anio_anterior_prom=2025 == periodo_filtro_anio(2026)-1 / SEM=1 |
| 22 | PROM escala entera (sin decimales) | ✅ OK | Todos los PROM son enteros (escala MU correcta) |
| 23 | Distribución FLAG_INCONSISTENCIA_VIG | ✅ OK | Distribución: {'OK': 6142} |
| 24 | Catálogos gobernanza sin combos nuevos | ✅ OK | 10 combos en datos, todos cubiertos por catálogo (29 reglas) |
| 25 | GOB bloqueante: FOR_ING_ACT vs catálogo | ✅ OK | 4 códigos en datos, todos en catálogo (11 válidos) |
| 26 | GOB bloqueante: COD_SED vs catálogo sede | ✅ OK | 1 sedes en datos, todas en catálogo (2 válidas) |
| 27 | GOB bloqueante: NAC vs catálogo nacionalidades | ✅ OK | 9 nacionalidades en datos, todas en catálogo (15 válidas) |
| 28 | GOB bloqueante: PAIS_EST_SEC vs catálogo | ✅ OK | 1 países en datos, todos en catálogo (1 válidos) |
| 29 | GOB bloqueante: NIV_ACA vs catálogo niveles | ✅ OK | 8 niveles en datos, todos en catálogo (13 válidos) |

**Resumen**: 29 OK, 0 FAIL, 0 WARN, 0 SKIP de 29 checks

## Mapa de Linaje por Columna

### `VIG`
- **Fuentes**: Hoja1/MAT_AC VIGENCIA, DatosAlumnos (catálogo DA), Catálogos gobernanza TSV
- **Transformaciones**: Forzado a 0 por regla DA, Comparación VIG real vs esperado
- **Reglas de negocio**: TITULADO/ELIMINADO/SUSPENDIDO → VIG=0, VIG=0 ⇒ 4 columnas=0
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L108: "UNIDADES_4TO_ANIO", "UNIDADES_5TO_ANIO", "UNIDADES_6TO_ANIO", "UNIDADES_7MO_ANIO", "VIGENCIA",`
  - `L116: "UNID_APROBADAS_TOTAL", "VIGENCIA",`
  - `L1174: base_usecols = ["CODIGO_UNICO", "MODALIDAD", "JORNADA", "DURACION_ESTUDIOS", "VIGENCIA"]`
  - `L2505: vig_esperado_da = pd.Series(pd.NA, index=archivo_subida.index, dtype="Int64")`
  - `L2518: vig_esperado_da = pd.to_numeric(key_da.map(da_vig_map), errors="coerce").astype("Int64")`
  - `L2535: vig_esperado_da = vig_esperado_da.fillna(vig_esperado_h1)`

### `PROM_PRI_SEM`
- **Fuentes**: Hoja1 histórico / MAT_AC, combine_first (input + hist)
- **Transformaciones**: Escala round(promedio*100) → 100-700, PERIODO=1 → PROM_PRI_SEM, Coerción numérica con bounds
- **Reglas de negocio**: Año anterior dinámico (max histórico), Solo APROBADO/REPROBADO
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L100: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L390: "PROM_PRI_SEM_HIST": _coerce_mu_average(sub_ref.loc[graded_ref & sem_ref.eq(1), "NOTA_MU"]),`
  - `L1604: out["PROM_PRI_SEM"] = mat_ac.get("PROM_PRI_SEM", 0)`
  - `L2290: out["PROM_PRI_SEM"] = out["PROM_PRI_SEM"].combine_first(src_work["PROM_PRI_SEM_HIST"])`
  - `L301: out.loc[(nota >= 100) & (nota <= 700)] = nota.loc[(nota >= 100) & (nota <= 700)].round()`
  - `L312: return min(max(avg, 100), 700)`

### `PROM_SEG_SEM`
- **Fuentes**: Hoja1 histórico / MAT_AC, combine_first (input + hist)
- **Transformaciones**: PERIODO∈{2,3} → PROM_SEG_SEM, Coerción numérica con bounds
- **Reglas de negocio**: Año anterior dinámico
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L100: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L391: "PROM_SEG_SEM_HIST": _coerce_mu_average(sub_ref.loc[graded_ref & sem_ref.eq(2), "NOTA_MU"]),`
  - `L1605: out["PROM_SEG_SEM"] = mat_ac.get("PROM_SEG_SEM", 0)`
  - `L2293: out["PROM_SEG_SEM"] = out["PROM_SEG_SEM"].combine_first(src_work["PROM_SEG_SEM_HIST"])`
  - `L291: # El histórico Hoja1 usa PERIODO=3 como equivalente operacional de segundo semestre.`
  - `L292: sem.loc[periodo.isin([2, 3])] = 2`

### `ASI_INS_HIS`
- **Fuentes**: Hoja1 histórico / MAT_AC UNID_CURSADAS_TOTAL, combine_first
- **Transformaciones**: Count CODRAMO distintos
- **Reglas de negocio**: ASI_APR_HIS ≤ ASI_INS_HIS, Rango 0-200
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L99: "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",`
  - `L100: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L388: "ASI_INS_ANT_HIST": int(codramo_ref[~transfer_ref].nunique()),`
  - `L2284: out["ASI_INS_ANT"] = out["ASI_INS_ANT"].combine_first(src_work["ASI_INS_ANT_HIST"])`
  - `L2296: out["ASI_INS_HIS"] = out["ASI_INS_HIS"].combine_first(src_work["ASI_INS_HIS_HIST"])`
  - `L388: "ASI_INS_ANT_HIST": int(codramo_ref[~transfer_ref].nunique()),`

### `ASI_APR_HIS`
- **Fuentes**: Hoja1 histórico / MAT_AC UNID_APROBADAS_TOTAL, combine_first
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: Capped ≤ ASI_INS_HIS
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L99: "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",`
  - `L100: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L389: "ASI_APR_ANT_HIST": int(codramo_ref[aprob_ref].nunique()),`
  - `L2287: out["ASI_APR_ANT"] = out["ASI_APR_ANT"].combine_first(src_work["ASI_APR_ANT_HIST"])`
  - `L2299: out["ASI_APR_HIS"] = out["ASI_APR_HIS"].combine_first(src_work["ASI_APR_HIS_HIST"])`
  - `L94: # Contratos oficiales (Capa C)`

### `FOR_ING_ACT`
- **Fuentes**: Hoja1/DatosAlumnos VIA_ADMISION, Catálogo gobernanza FOR_ING_ACT
- **Transformaciones**: Multi-rule resolution (token/catálogo/fallback), Mapeo textual a código numérico, Fallback código 10
- **Reglas de negocio**: Tokens especiales → códigos
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L98: "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION", "FOR_ING_ACT",`
  - `L159: DEFAULT_GOB_FOR_ING_ACT_CANDIDATES = [`
  - `L160: Path(__file__).with_name("gobernanza_for_ing_act.tsv"),`
  - `L160: Path(__file__).with_name("gobernanza_for_ing_act.tsv"),`
  - `L161: Path.cwd() / "gobernanza_for_ing_act.tsv",`
  - `L162: Path.home() / "Downloads" / "gobernanza_for_ing_act.tsv",`

### `ANIO_ING_ACT`
- **Fuentes**: Hoja1 ANOINGRESO, DatosAlumnos ANOINGRESO, Inferencia desde CODCLI
- **Transformaciones**: Validación rango 1990-2026
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L701: "ANOINGRESO",`
  - `L731: "ANOINGRESO": "DA_ANOINGRESO",`
  - `L1749: col_anio_ing = _pick_first_column(src, ["ANOINGRESO", "ANIO_INGRESO_CARRERA_ACTUAL"])`
  - `L731: "ANOINGRESO": "DA_ANOINGRESO",`
  - `L2135: anio_da_raw = src_work["DA_ANOINGRESO"] if "DA_ANOINGRESO" in src_work.columns else _na_series()`
  - `L2148: anio_act_source.loc[anio_da_mask] = "DA_ANOINGRESO"`

### `SEM_ING_ACT`
- **Fuentes**: Hoja1 PERIODOINGRESO, DatosAlumnos PERIODOINGRESO
- **Transformaciones**: Normalización período→semestre
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L702: "PERIODOINGRESO",`
  - `L732: "PERIODOINGRESO": "DA_PERIODOINGRESO",`
  - `L1750: col_sem_ing = _pick_first_column(src, ["PERIODOINGRESO", "SEM_INGRESO_CARRERA_ACTUAL"])`
  - `L732: "PERIODOINGRESO": "DA_PERIODOINGRESO",`
  - `L2164: sem_da_raw = src_work["DA_PERIODOINGRESO"] if "DA_PERIODOINGRESO" in src_work.columns else _na_series()`
  - `L2176: sem_act_source.loc[sem_da_mask] = "DA_PERIODOINGRESO"`

### `CODCLI`
- **Fuentes**: DatosAlumnos CODIGOCLIENTE
- **Transformaciones**: Normalización (strip/upper), Deduplicación por CODCLI
- **Reglas de negocio**: Drop duplicates keep first
- **Outputs**: ARCHIVO_LISTO_SUBIDA, AUDITORIA_CONSOLIDACION
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L251: def _infer_year_from_codcli(value: object) -> float:`
  - `L676: """Carga lookup por CODCLI desde hoja DatosAlumnos para gobernanza v2.`
  - `L686: if "CODCLI" not in src.columns:`
  - `L19: text = str(codigo_unico or "").strip().upper()`
  - `L31: canon_txt = str(canon or "").strip().upper()`
  - `L926: def _consolidar_candidatos_por_codcli(`

### `VIG_ESPERADO_DA`
- **Fuentes**: Catálogos DA gobernanza, TSVs estado/situación
- **Transformaciones**: Merge/lookup desde catálogo → VIG esperado
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L1794: ["ESTADO_ACADEMICO", "DESCRIPCION_ESTADO", "VIG_ESPERADO"],`
  - `L1798: ["ESTADOACADEMICO", "SITUACION", "VIG_ESPERADO"],`
  - `L2505: vig_esperado_da = pd.Series(pd.NA, index=archivo_subida.index, dtype="Int64")`
  - `L165: Path(__file__).with_name("gobernanza_catalogos") / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
  - `L166: Path.cwd() / "gobernanza_catalogos" / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
  - `L169: Path(__file__).with_name("gobernanza_catalogos") / "gob_datosalumnos_estadoacademico_situacion.tsv",`

### `FLAG_INCONSISTENCIA_VIG`
- **Fuentes**: Derivada de VIG vs VIG_ESPERADO_DA
- **Transformaciones**: Comparación directa
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L3252: archivo_subida["FLAG_INCONSISTENCIA_VIG"] = flag_vig`
  - `L3342: # Recalcular FLAG_INCONSISTENCIA_VIG después de todas las políticas`
  - `L3349: archivo_subida["FLAG_INCONSISTENCIA_VIG"] = flag_vig_post`
  - `L2334: method = pd.Series("SIN_REGLA_FINAL", index=src_work.index, dtype="object")`
  - `L3248: flag_vig = pd.Series("SIN_REGLA_GOB_DA", index=archivo_subida.index, dtype="object")`

### `NOMBRE_CARRERA_TSV`
- **Fuentes**: DURACION_ESTUDIOS.tsv
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L16: # FUENTE ÚNICA GOBERNANZA SIES: DURACION_ESTUDIOS.tsv`
  - `L45: Path(__file__).with_name("DURACION_ESTUDIOS.tsv"),`
  - `L46: Path.cwd() / "DURACION_ESTUDIOS.tsv",`

### `DURACION_ESTUDIOS_TSV`
- **Fuentes**: DURACION_ESTUDIOS.tsv
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L16: # FUENTE ÚNICA GOBERNANZA SIES: DURACION_ESTUDIOS.tsv`
  - `L45: Path(__file__).with_name("DURACION_ESTUDIOS.tsv"),`
  - `L46: Path.cwd() / "DURACION_ESTUDIOS.tsv",`

## Puntos Clave Detectados en el Código

### filtro_periodo
- *(no detectado)*

### recalculo_4_columnas
- L1604: `out["PROM_PRI_SEM"] = mat_ac.get("PROM_PRI_SEM", 0)`
- L1605: `out["PROM_SEG_SEM"] = mat_ac.get("PROM_SEG_SEM", 0)`
- L1606: `out["ASI_INS_HIS"] = mat_ac.get("UNID_CURSADAS_TOTAL", 0)`
- L1607: `out["ASI_APR_HIS"] = mat_ac.get("UNID_APROBADAS_TOTAL", 0)`
- L1759: `col_prom_pri_sem = _pick_first_column(src, ["PROM_PRI_SEM"])`

### regla_VIG0_4cols
- *(no detectado)*

### carga_catalogos_TSV
- L165: `Path(__file__).with_name("gobernanza_catalogos") / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
- L166: `Path.cwd() / "gobernanza_catalogos" / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
- L169: `Path(__file__).with_name("gobernanza_catalogos") / "gob_datosalumnos_estadoacademico_situacion.tsv",`
- L170: `Path.cwd() / "gobernanza_catalogos" / "gob_datosalumnos_estadoacademico_situacion.tsv",`
- L279: `df = _load_governance_tsv(str(path), ["FOR_ING_ACT", "DESCRIPCION_MANUAL"])`

### columnas_DA
- L737: `"SITUACION": "DA_SITUACION",`
- L738: `"ESTADOACADEMICO": "DA_ESTADOACADEMICO",`
- L2387: `if "REINCORPORACION" not in src_work.columns and "DA_SITUACION" in src_work.columns:`
- L2438: `archivo_subida["DA_ESTADOACADEMICO"] = src_work["DA_ESTADOACADEMICO"] if "DA_ESTADOACADEMICO" in src_work.columns else p`
- L2439: `archivo_subida["DA_SITUACION"] = src_work["DA_SITUACION"] if "DA_SITUACION" in src_work.columns else pd.NA`

### columnas_TSV_duracion
- L1209: `dim["OFERTA_SOURCE_SHEET"] = "DURACION_ESTUDIOS_TSV"`
- L3460: `"NOMBRE_CARRERA": "NOMBRE_CARRERA_TSV",`
- L3461: `"DURACION_ESTUDIOS": "DURACION_ESTUDIOS_TSV",`
- L3462: `"DURACION_TITULACION": "DURACION_TITULACION_TSV",`
- L3463: `"DURACION_TOTAL": "DURACION_TOTAL_TSV",`

### escritura_excel
- L862: `def _write_excel_atomic(`
- L872: `with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:`
- L874: `df.to_excel(writer, index=False, sheet_name=sheet_name[:31])`
- L3602: `_write_excel_atomic(sheets_export, out_path, red_rows_sheet="ARCHIVO_LISTO_SUBIDA", red_rows_mask=_red_mask)`
- L4232: `mu_ctrl.to_excel(output_dir / "matricula_unificada_2026_oficial.xlsx", index=False)`

### validacion_bloqueante
- L1130: `Si no encuentra, retorna DataFrame vacío (no bloqueante).`
- L2713: `# Regla de gobernanza bloqueante: combinaciones SOURCE_KEY_3 no catalogadas en SIES.`
- L2714: `sin_match_bloqueante = archivo_subida["SIES_MATCH_STATUS"].eq("SIN_MATCH_SIES") & ~archivo_subida["ES_DIPLOMADO"].fillna`
- L2715: `if sin_match_bloqueante.any():`
- L2718: `sin_match_bloqueante,`

---
## Dictamen Final

### ✅ LISTO PARA ENTREGA

Todos los checks pasaron. El archivo `archivo_listo_para_sies.xlsx` y el CSV regulatorio
son aptos para entrega oficial al SIES.

---
*Generado automáticamente por `scripts/auditoria_maestra.py` el 2026-04-09 08:57:47*