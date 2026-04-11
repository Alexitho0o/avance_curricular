# Auditoría Maestra — Gate de Entrega MU 2026

**Dictamen: ✅ LISTO PARA ENTREGA**

## Metadata
| Campo | Valor |
|-------|-------|
| Fecha/Hora | 2026-04-23 08:21:16 |
| Commit | 0eb1e38 |
| Output-Dir | /Users/alexi/Documents/GitHub/avance_curricular/resultados |
| Modo | solo-validar |
| Input | (outputs existentes) |
| Pipeline-Script | /Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py |
| Pipeline-Líneas | 5692 |
| Git-Diff-Refs | 12 |

## Cambios de Código Aplicados (Git Diff)

- `codigo_gobernanza_v2.py:L1082-L1120`
- `codigo_gobernanza_v2.py:L1687-L1690`
- `codigo_gobernanza_v2.py:L2441-L2458`
- `codigo_gobernanza_v2.py:L3103`
- `codigo_gobernanza_v2.py:L3305-L3312`
- `codigo_gobernanza_v2.py:L3356-L3364`
- `codigo_gobernanza_v2.py:L3375-L3383`
- `codigo_gobernanza_v2.py:L3428-L3436`
- `codigo_gobernanza_v2.py:L5202-L5260`
- `qa_checks.py:L88-L114`
- `qa_checks.py:L121`
- `qa_checks.py:L427-L439`

## Checklist de Componentes

| # | Check | Estado | Detalle |
|---|-------|--------|---------|
| 1 | Existencia Excel principal | ✅ OK | /Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx |
| 2 | Hojas requeridas presentes | ✅ OK | Hojas encontradas: ARCHIVO_LISTO_SUBIDA, AUDITORIA_CONSOLIDACION, CATALOGO_MANUAL, EXCLUIDOS_CARGA_PREGR, MATRICULA_UNIFICADA_32, PATCH_SIT_FON_SOL, PUENTE_SIES, RESUMEN_CARGA_PREGRADO, RESUMEN_EJECUT |
| 3 | Columnas MU32 regulatorias | ✅ OK | 32 columnas; las 32 regulatorias presentes |
| 4 | Columnas trazabilidad *_DA | ✅ OK | Presentes: ['VIG_ESPERADO_DA', 'FLAG_INCONSISTENCIA_VIG', 'ESTADOACADEMICO_DA', 'SITUACION_DA'] |
| 5 | Columnas trazabilidad *_TSV | ✅ OK | Presentes: ['NOMBRE_CARRERA_TSV', 'DURACION_ESTUDIOS_TSV', 'DURACION_TITULACION_TSV', 'DURACION_TOTAL_TSV'] |
| 6 | Cobertura DURACION por CODIGO_CARRERA | ✅ OK | 28927/28927 con COD_CAR tienen DURACION_TSV (100.0%); 6 sin match SIES |
| 7 | Rango PROM_PRI_SEM [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 8 | Rango PROM_SEG_SEM [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=697, sin decimales aparentes |
| 9 | Rango ASI_INS_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=41 |
| 10 | Rango ASI_APR_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | min=0, max=37 |
| 11 | ASI_APR_HIS ≤ ASI_INS_HIS [ARCHIVO_LISTO_SUBIDA] | ✅ OK | Coherencia OK en todos los registros |
| 12 | Rango PROM_PRI_SEM [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=700, sin decimales aparentes |
| 13 | Rango PROM_SEG_SEM [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=697, sin decimales aparentes |
| 14 | Rango ASI_INS_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=41 |
| 15 | Rango ASI_APR_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | min=0, max=37 |
| 16 | ASI_APR_HIS ≤ ASI_INS_HIS [MATRICULA_UNIFICADA_32] | ✅ OK | Coherencia OK en todos los registros |
| 17 | Regla VIG=0 → 4cols=0 [ARCHIVO_LISTO_SUBIDA] | ✅ OK | VIG=0: 317 registros, todos con 4 cols=0 |
| 18 | Regla VIG=0 → 4cols=0 [MATRICULA_UNIFICADA_32] | ✅ OK | VIG=0: 95 registros, todos con 4 cols=0 |
| 19 | Verificador scripts/verificar_4_columnas_mu.py | ✅ OK | OK: columnas de trazabilidad DA presentes VALIDACION: OK |
| 20 | CSV regulatorio presente | ✅ OK | Tamaño: 427,932 bytes |
| 21 | Año anterior por período (dinámico) | ✅ OK | anio_anterior_prom=2025 == periodo_filtro_anio(2026)-1 / SEM=1 |
| 22 | PROM escala entera (sin decimales) | ✅ OK | Todos los PROM son enteros (escala MU correcta) |
| 23 | Distribución FLAG_INCONSISTENCIA_VIG | ✅ OK | Distribución: {'OK': 28933} |
| 24 | Catálogos gobernanza sin combos nuevos | ✅ OK | 10 combos en datos, todos cubiertos por catálogo (29 reglas) |
| 25 | GOB bloqueante: FOR_ING_ACT vs catálogo | ✅ OK | 6 códigos en datos, todos en catálogo (11 válidos) |
| 26 | Anexo 7 continuidad: FOR_ING_ACT {2,3,4,5,11} ⇒ ORI != ACT | ✅ OK | 499 filas continuidad auditadas, todas con ORI != ACT |
| 27 | GOB bloqueante: COD_SED vs catálogo sede | ✅ OK | 2 sedes en datos, todas en catálogo (2 válidas) |
| 28 | GOB bloqueante: NAC vs catálogo nacionalidades | ✅ OK | 12 nacionalidades en datos, todas en catálogo (15 válidas) |
| 29 | GOB bloqueante: PAIS_EST_SEC vs catálogo | ✅ OK | 1 países en datos, todos en catálogo (1 válidos) |
| 30 | GOB bloqueante: NIV_ACA vs catálogo niveles | ✅ OK | 8 niveles en datos, todos en catálogo (13 válidos) |

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
  - `L1766: base_usecols = ["CODIGO_UNICO", "MODALIDAD", "JORNADA", "DURACION_ESTUDIOS", "VIGENCIA"]`
  - `L3206: vig_esperado_da = pd.Series(pd.NA, index=archivo_subida.index, dtype="Int64")`
  - `L3219: vig_esperado_da = pd.to_numeric(key_da.map(da_vig_map), errors="coerce").astype("Int64")`
  - `L3236: vig_esperado_da = vig_esperado_da.fillna(vig_esperado_h1)`

### `PROM_PRI_SEM`
- **Fuentes**: Hoja1 histórico / MAT_AC, combine_first (input + hist)
- **Transformaciones**: Escala round(promedio*100) → 100-700, PERIODO=1 → PROM_PRI_SEM, Coerción numérica con bounds
- **Reglas de negocio**: Solo REGIMEN=SEMESTRAL, Año anterior dinámico (max histórico), Solo APROBADO/REPROBADO, NOTA_FINAL entre 1 y 7
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L743: "PROM_PRI_SEM_HIST": _coerce_mu_average(sub_ref.loc[graded_ref & sem_ref.eq(1), "NOTA_MU"]),`
  - `L2213: out["PROM_PRI_SEM"] = mat_ac.get("PROM_PRI_SEM", 0)`
  - `L2989: out["PROM_PRI_SEM"] = out["PROM_PRI_SEM"].combine_first(src_work["PROM_PRI_SEM_HIST"])`
  - `L645: # Escala fuente → escala MU (100-700), documentada en gobernanza_escala_notas.tsv`
  - `L648: # Fuente 100-700  → ya en escala, usar directamente`

### `PROM_SEG_SEM`
- **Fuentes**: Hoja1 histórico / MAT_AC, combine_first (input + hist)
- **Transformaciones**: PERIODO∈{2,3} → PROM_SEG_SEM, Coerción numérica con bounds
- **Reglas de negocio**: Solo REGIMEN=SEMESTRAL, Año anterior dinámico
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L744: "PROM_SEG_SEM_HIST": _coerce_mu_average(sub_ref.loc[graded_ref & sem_ref.eq(2), "NOTA_MU"]),`
  - `L2214: out["PROM_SEG_SEM"] = mat_ac.get("PROM_SEG_SEM", 0)`
  - `L2992: out["PROM_SEG_SEM"] = out["PROM_SEG_SEM"].combine_first(src_work["PROM_SEG_SEM_HIST"])`
  - `L312: if periodo in (2, 3):`
  - `L322: # Estructura esperada CODCLI: YYYY + periodo(1 dígito) + CODCARPR + correlativo(3 dígitos)`

### `ASI_INS_HIS`
- **Fuentes**: Hoja1 histórico / MAT_AC UNID_CURSADAS_TOTAL, combine_first
- **Transformaciones**: Count CODRAMO distintos
- **Reglas de negocio**: ASI_APR_HIS ≤ ASI_INS_HIS, Rango 0-200
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L108: "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",`
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L741: "ASI_INS_ANT_HIST": int(codramo_ref[~transfer_ref].nunique()),`
  - `L2983: out["ASI_INS_ANT"] = out["ASI_INS_ANT"].combine_first(src_work["ASI_INS_ANT_HIST"])`
  - `L2995: out["ASI_INS_HIS"] = out["ASI_INS_HIS"].combine_first(src_work["ASI_INS_HIS_HIST"])`
  - `L741: "ASI_INS_ANT_HIST": int(codramo_ref[~transfer_ref].nunique()),`

### `ASI_APR_HIS`
- **Fuentes**: Hoja1 histórico / MAT_AC UNID_APROBADAS_TOTAL, combine_first
- **Transformaciones**: (ninguna detectada)
- **Reglas de negocio**: Capped ≤ ASI_INS_HIS
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L108: "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",`
  - `L109: "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",`
  - `L742: "ASI_APR_ANT_HIST": int(codramo_ref[aprob_ref].nunique()),`
  - `L2986: out["ASI_APR_ANT"] = out["ASI_APR_ANT"].combine_first(src_work["ASI_APR_ANT_HIST"])`
  - `L2998: out["ASI_APR_HIS"] = out["ASI_APR_HIS"].combine_first(src_work["ASI_APR_HIS_HIST"])`
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
  - `L376: keep = {"CODCLI", "RUT", "CODCARPR", "ANOINGRESO", "PERIODOINGRESO"}`
  - `L378: required = {"CODCLI", "RUT", "ANOINGRESO"}`
  - `L389: work["_ANIO"] = pd.to_numeric(work["ANOINGRESO"], errors="coerce")`
  - `L1307: "ANOINGRESO": "DA_ANOINGRESO",`
  - `L2834: anio_da_raw = src_work["DA_ANOINGRESO"] if "DA_ANOINGRESO" in src_work.columns else _na_series()`
  - `L2847: anio_act_source.loc[anio_da_mask] = "DA_ANOINGRESO"`

### `SEM_ING_ACT`
- **Fuentes**: Hoja1 PERIODOINGRESO, DatosAlumnos PERIODOINGRESO
- **Transformaciones**: Normalización período→semestre
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA, MATRICULA_UNIFICADA_32
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L376: keep = {"CODCLI", "RUT", "CODCARPR", "ANOINGRESO", "PERIODOINGRESO"}`
  - `L391: work["PERIODOINGRESO"].map(_normalize_semester_scalar)`
  - `L392: if "PERIODOINGRESO" in work.columns`
  - `L1308: "PERIODOINGRESO": "DA_PERIODOINGRESO",`
  - `L2863: sem_da_raw = src_work["DA_PERIODOINGRESO"] if "DA_PERIODOINGRESO" in src_work.columns else _na_series()`
  - `L2875: sem_act_source.loc[sem_da_mask] = "DA_PERIODOINGRESO"`

### `CODCLI`
- **Fuentes**: DatosAlumnos CODIGOCLIENTE
- **Transformaciones**: Normalización (strip/upper), Deduplicación por CODCLI
- **Reglas de negocio**: Drop duplicates keep first
- **Outputs**: ARCHIVO_LISTO_SUBIDA, AUDITORIA_CONSOLIDACION
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L292: def _infer_year_from_codcli(value: object) -> float:`
  - `L303: def _infer_sem_from_codcli(value: object) -> int | None:`
  - `L317: def _infer_codcarpr_from_codcli(value: object) -> str:`
  - `L28: text = str(codigo_unico or "").strip().upper()`
  - `L40: canon_txt = str(canon or "").strip().upper()`
  - `L1504: def _consolidar_candidatos_por_codcli(`

### `VIG_ESPERADO_DA`
- **Fuentes**: Catálogos DA gobernanza, TSVs estado/situación
- **Transformaciones**: Merge/lookup desde catálogo → VIG esperado
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L2493: ["ESTADO_ACADEMICO", "DESCRIPCION_ESTADO", "VIG_ESPERADO"],`
  - `L2497: ["ESTADOACADEMICO", "SITUACION", "VIG_ESPERADO"],`
  - `L3206: vig_esperado_da = pd.Series(pd.NA, index=archivo_subida.index, dtype="Int64")`
  - `L174: Path(__file__).with_name("gobernanza_catalogos") / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
  - `L175: Path.cwd() / "gobernanza_catalogos" / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
  - `L182: Path(__file__).with_name("gobernanza_catalogos") / "gob_datosalumnos_estadoacademico_situacion.tsv",`

### `FLAG_INCONSISTENCIA_VIG`
- **Fuentes**: Derivada de VIG vs VIG_ESPERADO_DA
- **Transformaciones**: Comparación directa
- **Reglas de negocio**: (ninguna detectada)
- **Outputs**: ARCHIVO_LISTO_SUBIDA
- **Referencias en código** (`codigo_gobernanza_v2.py`):
  - `L4164: archivo_subida["FLAG_INCONSISTENCIA_VIG"] = flag_vig`
  - `L4314: # Recalcular FLAG_INCONSISTENCIA_VIG después de todas las políticas`
  - `L4321: archivo_subida["FLAG_INCONSISTENCIA_VIG"] = flag_vig_post`
  - `L959: .fillna("SIN_DATO")`
  - `L962: .replace("", "SIN_DATO")`

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
- L2213: `out["PROM_PRI_SEM"] = mat_ac.get("PROM_PRI_SEM", 0)`
- L2214: `out["PROM_SEG_SEM"] = mat_ac.get("PROM_SEG_SEM", 0)`
- L2215: `out["ASI_INS_HIS"] = mat_ac.get("UNID_CURSADAS_TOTAL", 0)`
- L2216: `out["ASI_APR_HIS"] = mat_ac.get("UNID_APROBADAS_TOTAL", 0)`
- L2428: `col_prom_pri_sem = _pick_first_column(src, ["PROM_PRI_SEM"])`

### regla_VIG0_4cols
- *(no detectado)*

### carga_catalogos_TSV
- L174: `Path(__file__).with_name("gobernanza_catalogos") / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
- L175: `Path.cwd() / "gobernanza_catalogos" / "gob_promedios_hoja1_estado_academico_descripcion.tsv",`
- L182: `Path(__file__).with_name("gobernanza_catalogos") / "gob_datosalumnos_estadoacademico_situacion.tsv",`
- L183: `Path.cwd() / "gobernanza_catalogos" / "gob_datosalumnos_estadoacademico_situacion.tsv",`
- L348: `df = _load_governance_tsv(str(path), ["FOR_ING_ACT", "DESCRIPCION_MANUAL"])`

### columnas_DA
- L1313: `"SITUACION": "DA_SITUACION",`
- L1314: `"ESTADOACADEMICO": "DA_ESTADOACADEMICO",`
- L3086: `if "REINCORPORACION" not in src_work.columns and "DA_SITUACION" in src_work.columns:`
- L3139: `archivo_subida["DA_ESTADOACADEMICO"] = src_work["DA_ESTADOACADEMICO"] if "DA_ESTADOACADEMICO" in src_work.columns else p`
- L3140: `archivo_subida["DA_SITUACION"] = src_work["DA_SITUACION"] if "DA_SITUACION" in src_work.columns else pd.NA`

### columnas_TSV_duracion
- L1803: `dim["OFERTA_SOURCE_SHEET"] = "DURACION_ESTUDIOS_TSV"`
- L4502: `"NOMBRE_CARRERA": "NOMBRE_CARRERA_TSV",`
- L4503: `"DURACION_ESTUDIOS": "DURACION_ESTUDIOS_TSV",`
- L4504: `"DURACION_TITULACION": "DURACION_TITULACION_TSV",`
- L4505: `"DURACION_TOTAL": "DURACION_TOTAL_TSV",`

### escritura_excel
- L1440: `def _write_excel_atomic(`
- L1450: `with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:`
- L1452: `df.to_excel(writer, index=False, sheet_name=sheet_name[:31])`
- L4662: `_write_excel_atomic(sheets_export, out_path, red_rows_sheet="ARCHIVO_LISTO_SUBIDA", red_rows_mask=_red_mask)`
- L5468: `mu_ctrl.to_excel(output_dir / "matricula_unificada_2026_oficial.xlsx", index=False)`

### validacion_bloqueante
- L1722: `Si no encuentra, retorna DataFrame vacío (no bloqueante).`
- L3489: `# Regla de gobernanza bloqueante: combinaciones SOURCE_KEY_3 no catalogadas en SIES.`
- L3490: `sin_match_bloqueante = archivo_subida["SIES_MATCH_STATUS"].eq("SIN_MATCH_SIES") & ~archivo_subida["ES_DIPLOMADO"].fillna`
- L3491: `if sin_match_bloqueante.any():`
- L3494: `sin_match_bloqueante,`

---
## Dictamen Final

### ✅ LISTO PARA ENTREGA

Todos los checks pasaron. El archivo `archivo_listo_para_sies.xlsx` y el CSV regulatorio
son aptos para entrega oficial al SIES.

---
*Generado automáticamente por `scripts/auditoria_maestra.py` el 2026-04-23 08:21:16*