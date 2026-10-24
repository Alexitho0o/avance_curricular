# HITO 4B-P — Reparación Integral de SECTORIZADO_AC, Cruce SIES y Retención Longitudinal

Fecha de cierre técnico: 2026-07-15
Repositorio: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN`
Rama: `main`
HEAD inicial: `2c35809bf3fc7e2ad05c9dd159881434f04bbe32`
HEAD final: `2c35809bf3fc7e2ad05c9dd159881434f04bbe32`
Sin `git add`, `commit`, `push`, `pull`, `merge`, `rebase`, `reset --hard` ni `clean`.

## Problema original

La corrida de referencia `2026_P2_144254` terminó el pipeline completo con código 0, pero dejó tres problemas críticos:

- `SECTORIZADO_AC` terminó con código 2 y no generó su libro permanente.
- `CRUCE_SIES` clasificó 20.961 registros como `SIN_MATCH`.
- El KPI de retención informaba tasas no confiables sin una definición longitudinal por persona, periodo y llave comparable.

## Evidencia y diagnóstico

- La auditoría histórica del fallo sectorizado solo contenía resumen del fallo, sin traceback completo. Se corrigió la política de fallo para guardar traceback y código de salida en hoja dedicada.
- La forma del error sectorizado era compatible con un identificador no escalar, por ejemplo una tupla accidental con arreglo NumPy. La lógica nueva rechaza explícitamente `Series`, `Index`, `ndarray`, listas o tuplas cuando aparecen dentro de una celda escalar, y acepta colecciones solo como entrada vectorial controlada.
- En SIES, `mrun` no es semánticamente comparable con el RUT interno con DV a nivel persona. En la fuente real solo hubo 2 RUT comunes y 0 llaves `RUT+AÑO` comunes.
- La base interna usada por el cruce SIES estaba restringida al universo vigente/encuesta, por eso quedaba en 1.168 personas-año y no representaba el histórico necesario para comparar contra SIES.
- En retención, la metodología previa estaba basada en tokens/cohorte de ingreso y no separaba retención institucional por persona de retención en el mismo programa. Al validar la fuente real 2025 P2 -> 2026 P2, la intersección de RUT normalizado vigente fue 0; por eso se conserva la tasa 0, pero ahora queda auditada y marcada con advertencia de plausibilidad.

## Causa raíz

### SECTORIZADO_AC

Ausencia de validación defensiva para identificadores no escalares y auditoría insuficiente del fallo. El defecto permitía que una forma como `(str, array([...], dtype=object))` llegara a normalización/selección sin un mensaje institucional claro.

### Cruce SIES

Combinación de dos causas:

1. La base interna histórica de B10quater provenía de una cache restringida al universo maestro corriente, insuficiente para SIES.
2. La llave persona SIES (`mrun`) no demostró comparabilidad con el RUT interno; forzar match por RUT habría creado falsos positivos o un `SIN_MATCH` ciego.

### Retención

La unidad de análisis anterior no era una persona elegible por RUT en periodo base/seguimiento. Además, el cálculo mezclaba continuidad institucional, continuidad de programa y cohortes históricas sin advertencias de comparabilidad/provisionalidad.

## Solución implementada

### SECTORIZADO_AC

- Se agregó `normalizar_identificadores_controlado()` para aceptar `Series`, `Index`, listas y arreglos NumPy unidimensionales como entradas vectoriales, preservando identificadores como texto.
- Se rechazan valores no escalares dentro de celdas con `SectorizadoValidationError`.
- `write_failure_audit()` ahora genera:
  - `FALLO_SECTORIZADO`;
  - `TRACEBACK`;
  - `AUDITORIA_UNIVERSO`;
  - `bloque_fallido=SECTORIZADO_AC`;
  - `codigo_salida=2`;
  - `salida_generada=NO`.
- La regresión final generó `SECTORIZADO_AC` con 627 filas, llave única y estados exhaustivos.

### Cruce SIES

- Se incorporó normalización canónica de RUT/RUN en `caracterizacion_rut.py`, con:
  - `RUT_ORIGINAL`;
  - `RUT_NORMALIZADO`;
  - `RUT_SIN_DV`;
  - `DV`;
  - `RUT_VALIDO_ESTRUCTURAL`;
  - `RUT_DV_VALIDO`.
- Se agregó una cache histórica interna amplia para SIES en B10bis: `CRUCE_SIES_BASE_HIST_PREGRADO_TOTAL`.
- B10quater ahora prioriza la cache histórica total y mantiene separada la trayectoria restringida del universo corriente.
- Se agregó un match `MATCH_PROGRAMA_ANIO` vía `PUENTE_SIES_COMPILADO.tsv` solo para resoluciones `UNICO`.
- El match programa-año no atribuye identidad individual: se marca como `PROGRAMA_ANIO_NO_PERSONAL`.
- El estado del cruce queda `VALIDADO_CON_ADVERTENCIAS` cuando hay match programa-año pero no match persona confiable.

### Retención longitudinal

- Se creó `caracterizacion_retencion.py`.
- Se define retención institucional por persona como RUT normalizado en periodo base que aparece vigente/suspendido en periodo de seguimiento.
- Se separa:
  - `RETENIDOS_INSTITUCIONALES`;
  - `RETENIDOS_MISMO_PROGRAMA`;
  - `RETENIDOS_CAMBIO_PROGRAMA`;
  - `NO_RETENIDOS`;
  - `EXCLUIDOS`;
  - `SIN_LLAVE_VALIDA`.
- Se conserva salida legacy de Bloque 7, pero ahora proviene del detalle longitudinal.
- Se agregan hojas:
  - `RET_LONG_RESUMEN`;
  - `RET_LONG_DETALLE`;
  - `RET_LONG_AUDITORIA`.
- Si una cohorte grande queda con cero retenidos, se registra advertencia de plausibilidad.
- El semáforo de comparación queda `NO_COMPARABLE` cuando falta cohorte comparable previa; no se fuerza `ALZA/BAJA`.

## Archivos modificados

- `analisis_sectorizado_encuesta_ac.py`
- `caracterizacion.py`

## Archivos nuevos

- `caracterizacion_rut.py`
- `caracterizacion_retencion.py`
- `scripts/auditar_hito_4b_p.py`
- `tests/test_hito4b_sectorizado_sies_retencion.py`
- `gobernanza/HITO_4B_P.md`
- `gobernanza/HITO_4B_P_manifest.json`

## Funciones principales modificadas o agregadas

- `normalizar_identificadores_controlado`
- `_normalizar_identificador_scalar`
- `write_failure_audit`
- `_build_cruce_sies_base_historica_pregrado_total`
- `_ejecutar_bloque_10bis`
- `_build_program_year_match`
- `_preparar_base_interna_historica`
- `_ejecutar_bloque_10quater`
- `_retencion_source_from_hist`
- `_legacy_retencion_from_detail`
- `_comparativo_retencion`
- `normalizar_rut_componentes`
- `normalizar_rut_dataframe`
- `calcular_retencion_longitudinal`
- `auditar_sectorizado`
- `auditar_sies`
- `auditar_retencion`

## Resultados de regresión final

Ejecución final:

`/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0_caracterizacion/2026-07-15/2026_P2_161137`

Estado:

- `codigo_salida=0`
- `pipeline_completo=SI`
- `ultimo_bloque=BLOQUE 12`
- `modo_corte=NINGUNO`

### SECTORIZADO_AC

- Archivo generado: `02_SALIDAS/ENCUESTA_CARACTERIZACION_2026_P2_20260715_ANALISIS_SECTORIZADO_AC.xlsx`
- Filas: 627
- Duplicados llave maestra: 0
- Estados:
  - `SI`: 285
  - `INCOMPLETO`: 2
  - `NO`: 340
- Con datos AC: 506
- Sin datos AC: 121

### SIES

- Archivo generado: `02_SALIDAS/CRUCE_SIES_2026_P2_20260715.xlsx`
- Registros SIES: 20.961
- `MATCH_PROGRAMA_ANIO`: 4.228
- `SIN_MATCH`: 16.733
- Conflictos de mejor score: 0
- Estado: `VALIDADO_CON_ADVERTENCIAS`
- Observación: no se generó match persona porque la llave `mrun` no demostró comparabilidad con RUT interno; el match programa-año es agregado y auditado.

### Retención

- Archivo: `02_SALIDAS/KPI_ACADEMICOS_2026_P2_20260715.xlsx`
- Hoja `RET_LONG_RESUMEN`:
  - Cohorte elegible 2025 P2 -> 2026 P2: 117
  - Retenidos institucionales: 0
  - Retenidos mismo programa: 0
  - Retenidos cambio programa: 0
  - No retenidos: 117
  - Excluidos: 1
  - Tasa institucional: 0,00 %
- Auditoría:
  - `periodos_comparables=OK`
  - `identidad_retenidos_en_cohorte=OK`
  - `plausibilidad_retencion_cero_cohorte_grande=ADVERTENCIA`
  - Comparativo legacy global: `SEMAFORO=NO_COMPARABLE`

## Pruebas ejecutadas

- `python -m py_compile analisis_sectorizado_encuesta_ac.py caracterizacion.py caracterizacion_rut.py caracterizacion_retencion.py scripts/auditar_hito_4b_p.py`
- `bash -n run_caracterizacion_con_sectorizado_ac.sh scripts/normalizar_stop_after_financiamiento.sh scripts/run_consolidado_rut_10bis.sh`
- `pytest -q`: 173 passed, 86 subtests passed
- `git diff --check`: OK
- Regresión integral 2026 P2 con entradas históricas: OK
- Auditor automático:
  - `sectorizado.archivo_generado=OK`
  - `sectorizado.filas_salida=OK`
  - `sies.identidad_filas=OK`
  - `sies.estado_validacion=OK`
  - `retencion.retenidos_en_cohorte=OK`
  - `retencion.tasa_rango=OK`

## Hashes SHA-256

### Código

- `analisis_sectorizado_encuesta_ac.py`: `abab6c580b55a1aec1902b8b9101d5d79c8b7498a07eb4a40f8f037f72210298`
- `caracterizacion.py`: `d69e59706e52dab4386ff9763f123463bb2728b18b24da61046500b988337bd0`
- `caracterizacion_rut.py`: `1728281958c557a05986325bf62c7f9bd188e27ad60c14a06be587be172a8e0a`
- `caracterizacion_retencion.py`: `a80a39b554617cfbd16550cee6f2a793ea1558643aca9cb7534b00b073e913e1`
- `scripts/auditar_hito_4b_p.py`: `47d4d2be1819172dbe05fe3492057383aedfdc9832f6d98fc019e5b7636eb31c`
- `tests/test_hito4b_sectorizado_sies_retencion.py`: `3435a4960171625d62a1bdfc286d80208b4352e1b68024722aae3d978245c2f5`

### Artefactos de regresión

- `ENCUESTA_CARACTERIZACION_2026_P2_20260715_ANALISIS_SECTORIZADO_AC.xlsx`: `9cdde0a038a27b8b351e236b7e10aa1eb7b931aa6c68dbe8068af6e2c13d29ba`
- `CRUCE_SIES_2026_P2_20260715.xlsx`: `853d1ae1b3b836136fa70de7c06b33687c4c29ba25e305f4754fc6352c8c8b3b`
- `KPI_ACADEMICOS_2026_P2_20260715.xlsx`: `8cefec37c0b93f62a630fec855e29d54bafb8403619505c88908e31c874cf7f8`
- `manifest_ejecucion.json`: `026da08f4c1ffd962c88aec67fdf2c107c031392d12a34cfc4c18f54d31bd077`

## Limitaciones y riesgos pendientes

- SIES queda `VALIDADO_CON_ADVERTENCIAS`, no `VALIDADO`, porque no existe evidencia de comparabilidad persona entre `mrun` y RUT interno. El match disponible es programa-año vía puente gobernado.
- La retención 2025 P2 -> 2026 P2 queda en 0 retenidos porque no hay intersección de RUT normalizado entre vigentes de ambos cortes bajo las reglas actuales. Se documenta como advertencia de plausibilidad, no como error matemático.
- El cierre institucional de retención puede requerir una definición oficial adicional para casos de continuidad que no aparezcan como RUT vigente en el mismo periodo de seguimiento.

## Instrucciones de ejecución dinámica

Ejemplo reproducible:

```bash
ANIO_ANALISIS=2026 \
PERIODO_ANALISIS=2 \
VERBOSIDAD=3 \
COHORTE_TXT='' \
RUTA_MATRICULA='/ruta/DATOSDEALUMNOS_10170.xlsx' \
RUTA_INSCRITOS='/ruta/tokens_443299.csv' \
RUTA_RESULTADOS='/ruta/results-survey443299.xlsx' \
CARACTERIZACION_INPUT_DIR='/ruta/entradas' \
AUTO_INSTALL_DEPS=0 \
PYTHONPATH=.deps_local \
python3 caracterizacion.py
```

Auditor:

```bash
python3 scripts/auditar_hito_4b_p.py \
  --universo 627 \
  --sectorizado /ruta/ENCUESTA_CARACTERIZACION_2026_P2_20260715_ANALISIS_SECTORIZADO_AC.xlsx \
  --sies /ruta/CRUCE_SIES_2026_P2_20260715.xlsx \
  --retencion /ruta/KPI_ACADEMICOS_2026_P2_20260715.xlsx
```

## Dictamen técnico

HITO 4B-P: COMPLETADO_CON_OBSERVACIONES

Motivo: SECTORIZADO_AC queda reparado y SIES deja de ser una clasificación ciega `SIN_MATCH`; retención queda calculada por persona y auditada. Sin embargo, SIES no puede declararse validado a nivel persona con la fuente actual y retención conserva advertencia de plausibilidad por 0 retenidos en una cohorte de 117.
