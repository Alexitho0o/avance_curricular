# Documentación Técnica y de Trazabilidad

## Nota de vigencia operativa

Para **Matrícula Unificada Pregrado 2026**, la operación oficial congelada no se toma de las secciones legacy de este documento sino de:

- [ejecucion_oficial_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/ejecucion_oficial_mu_2026.md)
- [validacion_oficial_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/validacion_oficial_mu_2026.md)
- [resultado_corrida_referencia_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/resultado_corrida_referencia_mu_2026.md)

El runtime histórico y las bitácoras legacy se conservan en `archive/` como contexto técnico, pero no forman parte de la ejecución oficial de MU Pregrado 2026.

## 1) Propósito del proyecto

Este repositorio implementa un pipeline de datos para dos procesos institucionales:

- **Avance Curricular** (`--proceso avance`)
- **Matrícula Unificada con asignación SIES** (`--proceso matricula`)
- **Ejecución conjunta** (`--proceso ambos`)

El objetivo es transformar una fuente Excel operacional en salidas controladas, auditables y reutilizables para carga/reportería, con diagnóstico de calidad y trazabilidad de decisiones.

## 2) Arquitectura funcional

La implementación histórica principal quedó archivada en [codigo.py](/Users/alexi/Documents/GitHub/avance_curricular/archive/legacy_runtime/codigo.py) y combina:

- **Matriz de desambiguación SIES** (fase de resolución de ambigüedades).
- **Capa A: Ingesta flexible** (detección de estructura de entrada).
- **Capa B: Modelo intermedio** (normalización y enriquecimiento).
- **Capa C: Validación + exportación** (contratos, reglas y salidas).

### 2.1 Capas y responsabilidades

| Capa | Función | Resultado |
|---|---|---|
| Matriz SIES | Carga de `matriz_desambiguacion_sies_final.tsv` y resolución de ambiguos | Código SIES final o diagnóstico |
| Capa A | Lectura Excel, detección de hojas y modo compatibilidad (`Hoja1`) | DataFrames base |
| Capa B | Construcción de controles (carreras, matrícula AC, matrícula unificada) | DataFrames con contrato objetivo |
| Capa C | Validación semántica/esquemática y exportación | CSV/XLSX/JSON de control y calidad |

## 3) Fases de construcción (qué son y para qué sirven)

Las fases documentadas en `archive/contexto_historico/fases/` son **hitos de evolución** del mapeo SIES y de la lógica de resolución.

### Fase 1

- Define una primera matriz de desambiguación por `(CODCARPR, JORNADA, VERSION)`.
- Enfocada en carreras críticas iniciales y control de formato de códigos SIES.

### Fase 2

- Expande cobertura de mapeos a más `CODCARPR`.
- Fortalece reglas de versión y jornada para reducir incertidumbre.

### Fase 3

- Resuelve ambigüedades en ejecución con heurística (`_resolver_ambiguedades_sies_heuristica`).
- Introduce columnas de trazabilidad:
  - `SIES_RESOLUCION_HEURISTICA`
  - `SIES_CONFIANZA_POST`

## 4) ¿Qué hace `REVIEW.md`?

El archivo [REVIEW.md](/Users/alexi/Documents/GitHub/avance_curricular/archive/contexto_historico/tecnico/REVIEW.md) es una **revisión técnica de referencia** (origen Colab/histórico), no un módulo ejecutable.

Sirve para:

- registrar supuestos de entorno,
- dejar hallazgos de robustez,
- orientar decisiones de portabilidad.

No es consumido por el código en runtime.

## 5) Entradas: contratos y estructura

## 5.1 Entrada principal Excel

Ruta por defecto detectada:

- `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`

El sistema soporta dos modos:

### Modo estándar (preferido)

Detección por presencia de columnas:

- **Carreras**: `CODIGO_UNICO`, `PLAN_ESTUDIOS`
- **Matrícula**: `NUM_DOCUMENTO`, `CODIGO_UNICO`, `PLAN_ESTUDIOS`, `DV`
- **Histórico**: `ANO`, `PERIODO`, `RUT`, `DIG`, `CODCARR`, `CODRAMO`
- **Equivalencia**: hoja `Equivalencia`

### Modo compatibilidad (`Hoja1`)

Si no existe estructura estándar, se intenta derivar estructuras desde `Hoja1` con columnas mínimas:

- `RUT`, `DIG`, `CODCARR`, `PLAN_DE_ESTUDIO`, `ANO`, `PERIODO`, `CODRAMO`

En este modo, `Carreras`, `Matrícula` y `Equivalencia` se construyen automáticamente.

## 5.2 Entradas auxiliares de catálogo/mapeo

### `catalogo_manual.tsv`

- Propósito: clasificación manual por traza.
- Columnas requeridas:
  - `GRUPO_TRAZA`
  - `JORNADA`
  - `CODCARPR`
  - `NOMBRE_L`
  - `ANOINGRESO` (informativa en catálogo fuente)

### `puente_sies.tsv`

- Propósito: puente de llave de negocio a código SIES.
- Columnas requeridas:
  - `GRUPO_TRAZA`
  - `JORNADA`
  - `CODCARPR`
  - `NOMBRE_L`
  - `CODIGO_CARRERA_SIES`

### `matriz_desambiguacion_sies_final.tsv`

- Propósito: resolver ambigüedades SIES por tripleta.
- Columnas:
  - `CODCARPR`
  - `TIPO_CARRERA`
  - `JORNADA`
  - `VERSION`
  - `CODIGO_SIES_FINAL`
  - `CONFIANZA`
  - `NOTAS`

## 6) Flujo técnico por proceso

## 6.1 Proceso `avance`

Secuencia principal:

1. `cargar_fuentes`
2. `preparar_matricula_intermedia`
3. `construir_puente_equiv`
4. `mapear_historico_con_equiv`
5. `construir_resumen_historico`
6. `construir_carreras_control`
7. `construir_matricula_ac_control`
8. `construir_matricula_unificada_control`
9. Validaciones (`validar_*`)
10. Exportación + reportes de calidad

Puntos clave:

- deduplicación por clave de negocio, no por RUT solamente,
- fallback de mapeo por `CODCARR` cuando la combinación con jornada no es única,
- validación de esquema exacto en outputs de control.

## 6.2 Proceso `matricula`

Secuencia principal:

1. Carga de hoja objetivo.
2. Detección de columnas base obligatorias (`CODCLI`, `CODCARR/CODCARPR`, `CARRERA`, `JORNADA`, `RUT`, `DV`).
3. Normalización de llaves:
   - `SOURCE_KEY_3 = JORNADA|CODCARPR|NOMBRE`
   - `KEY_3_NO_JORNADA`
4. Matching contra catálogo manual (`MANUAL_MATCH_STATUS`).
5. Matching contra puente SIES:
   - `MATCH_SIES_UNICO`
   - `MATCH_SIES_AMBIGUO`
   - diagnósticos por jornada/nombre.
6. Resolución heurística de ambiguos (fase 3).
7. Exportación de workbook `archivo_listo_para_sies.xlsx`.

## 6.3 Proceso `ambos`

Ejecuta `avance` y `matricula` en una sola corrida y retorna ambos reportes en JSON.

## 7) Salidas y trazabilidad

## 7.1 Salidas principales en `resultados/`

| Archivo | Origen | Uso |
|---|---|---|
| `archivo_listo_para_sies.xlsx` | matricula | output final con diagnóstico/matching |
| `matricula_unificada_2026_pregrado.csv` | matricula | CSV regulatorio final |

Las salidas legacy, diagnósticas o históricas de otros flujos ya no viven en `resultados/`. Fueron movidas a `archive/resultados_legacy/`, `archive/resultados_remediacion/` y `archive/resultados_diagnostico/`.

## 7.2 Trazabilidad de decisión SIES

Columnas de trazabilidad en `archivo_listo_para_sies.xlsx`:

- `SIES_MATCH_STATUS`
- `SIES_MATCH_DIAG`
- `CODIGO_CARRERA_SIES_FINAL`
- `SIES_RESOLUCION_HEURISTICA`
- `SIES_CONFIANZA_POST`
- `CODIGOS_SIES_POTENCIALES`

Esto permite auditar:

- qué registros fueron exactos,
- cuáles fueron ambiguos,
- cómo se resolvieron,
- con qué nivel de confianza.

## 8) Gobernanza técnica

## 8.1 Reglas de severidad (Issue)

El pipeline usa `Issue(severity, area, message, count)` para control de calidad.

Severidades:

- `BLOCKER`: impide aptitud oficial.
- `ERROR`: incumplimiento relevante.
- `WARN`: observación no bloqueante.

Áreas típicas:

- `carreras`
- `matricula_ac`
- `matricula_unificada`

## 8.2 Criterio de aptitud (`apto_oficial`)

En el flujo histórico de `avance`, el artefacto `reporte_validacion.json` queda archivado y expresa:

- `matricula_unificada = false` si existen `BLOCKER/ERROR` en su área.
- `avance_curricular = false` si existen `BLOCKER/ERROR` en áreas de avance.

## 8.3 Pruebas de consistencia

`qa_checks.py` valida:

- que README no contenga dumps CSV,
- contratos de columnas de outputs control,
- consistencia básica de reportes JSON.

## 8.4 Versionado de artefactos críticos

Se versionan explícitamente:

- `catalogo_manual.tsv`
- `puente_sies.tsv`
- `matriz_desambiguacion_sies_final.tsv`

Esto asegura reproducibilidad de la asignación SIES entre ejecuciones.

## 9) Operación recomendada

## 9.1 Ejecución completa

```bash
cd /ruta/al/repo/avance_curricular
export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 codigo_gobernanza_v2.py --input "$INPUT_XLSX" --output-dir "$OUTPUT_DIR" --proceso matricula --usar-gobernanza-v2 true
```

## 9.2 Checklist operativo

1. Verificar existencia de entrada Excel.
2. Verificar presencia de TSV críticos de gobernanza en la raíz del repo.
3. Ejecutar el pipeline oficial congelado en `codigo_gobernanza_v2.py`.
4. Verificar que existan `resultados/archivo_listo_para_sies.xlsx` y `resultados/matricula_unificada_2026_pregrado.csv`.
5. Ejecutar la validación final desde la raíz del repo:

```bash
export OUTPUT_DIR="resultados"
python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase6-control-dir "control"
```

6. Confirmar que el gate final permanezca en `CONDICIONAL` y que el tablero siga en `27 OK / 5 Pendiente`.

## 10) Limitaciones actuales conocidas

- `MATCH_SIES_AMBIGUO` puede requerir validación manual de negocio en algunos casos.
- El fallback de versión/jornada en heurística prioriza continuidad operativa sobre precisión absoluta.
- `archive/contexto_historico/tecnico/REVIEW.md` refleja contexto histórico y no reemplaza validación funcional en este código.

## 11) Mapa rápido de archivos del repositorio

- [codigo.py](/Users/alexi/Documents/GitHub/avance_curricular/archive/legacy_runtime/codigo.py): pipeline principal histórico.
- [README.md](/Users/alexi/Documents/GitHub/avance_curricular/README.md): guía operativa rápida.
- [DOCUMENTACION_TECNICA.md](/Users/alexi/Documents/GitHub/avance_curricular/DOCUMENTACION_TECNICA.md): este documento.
- [REVIEW.md](/Users/alexi/Documents/GitHub/avance_curricular/archive/contexto_historico/tecnico/REVIEW.md): revisión técnica histórica.
- [catalogo_manual.tsv](/Users/alexi/Documents/GitHub/avance_curricular/catalogo_manual.tsv): catálogo de traza.
- [puente_sies.tsv](/Users/alexi/Documents/GitHub/avance_curricular/puente_sies.tsv): puente llave-código SIES.
- [matriz_desambiguacion_sies_final.tsv](/Users/alexi/Documents/GitHub/avance_curricular/matriz_desambiguacion_sies_final.tsv): matriz de resolución final.

## 12) Confirmación de columnas del Manual (Matrícula Unificada)

Resultado de verificación real de ejecución:

- Archivo generado: `resultados/archivo_listo_para_sies.xlsx`
- Hoja nueva contractual: `MATRICULA_UNIFICADA_32` (32 columnas exactas, en orden oficial del proyecto).
- Hoja operativa extendida: `ARCHIVO_LISTO_SUBIDA` (68 columnas = 32 contractuales + diagnóstico + trazabilidad).

### 12.1 Encabezados esperados (manual/captura) y equivalencia técnica

- `Código Carrera` (manual/captura) = `COD_CAR` (nombre técnico en archivo).
- `Version` (captura) = `VERSION` (sin tilde ni minúsculas).
- `NI2_ACA` observado en captura corresponde operacionalmente a `NIV_ACA` (nombre contractual interno).

Las 32 columnas contractuales son:

`TIPO_DOC`, `N_DOC`, `DV`, `PRIMER_APELLIDO`, `SEGUNDO_APELLIDO`, `NOMBRE`, `SEXO`, `FECH_NAC`, `NAC`, `PAIS_EST_SEC`, `COD_SED`, `COD_CAR`, `MODALIDAD`, `JOR`, `VERSION`, `FOR_ING_ACT`, `ANIO_ING_ACT`, `SEM_ING_ACT`, `ANIO_ING_ORI`, `SEM_ING_ORI`, `ASI_INS_ANT`, `ASI_APR_ANT`, `PROM_PRI_SEM`, `PROM_SEG_SEM`, `ASI_INS_HIS`, `ASI_APR_HIS`, `NIV_ACA`, `SIT_FON_SOL`, `SUS_PRE`, `FECHA_MATRICULA`, `REINCORPORACION`, `VIG`.

## 13) Mapeo End-to-End del proyecto

| Etapa | Función principal | Entrada | Salida |
|---|---|---|---|
| Ingesta AC | `cargar_fuentes` | Excel fuente | `df_carreras`, `df_matricula`, `df_historico`, `df_equiv` |
| Modelo AC | `preparar_matricula_intermedia`, `construir_resumen_historico` | DataFrames de ingesta | métricas académicas por estudiante/programa |
| Controles AC | `construir_carreras_control`, `construir_matricula_ac_control`, `construir_matricula_unificada_control` | DataFrames modelados | archivos contractuales de control |
| Validación AC | `validar_*` + `generar_procedencia_y_calidad` | controles | artefactos legacy hoy archivados: `reporte_validacion.json`, `reporte_calidad_semantica.json`, `reporte_procedencia.csv` |
| Ingesta MU | `ejecutar_pipeline_matricula_unificada_legacy_like` | Excel fuente + `catalogo_manual.tsv` + `puente_sies.tsv` | `archivo_subida` |
| Match manual | `_prepare_catalog_manual` + merge por `SOURCE_KEY_3` | `catalogo_manual.tsv` | `MANUAL_MATCH_STATUS`, `GRUPO_TRAZA_*` |
| Match SIES | `_prepare_puente_sies` + reglas de diagnóstico | `puente_sies.tsv` | `SIES_MATCH_STATUS`, `SIES_MATCH_DIAG`, códigos SIES potenciales/finales |
| Resolución ambiguos | `_resolver_ambiguedades_sies_heuristica` | filas `AMBIGUO_SIES` + `matriz_desambiguacion_sies_final.tsv` | `CODIGO_CARRERA_SIES_FINAL`, `SIES_RESOLUCION_HEURISTICA`, `SIES_CONFIANZA_POST` |
| Exportación MU | `_write_excel_atomic` | `archivo_subida` + resúmenes | `archivo_listo_para_sies.xlsx` con hojas de control/diagnóstico |

## 14) Mapeo técnico de columnas Matrícula Unificada (32)

Referencia histórica de implementación en modo `--proceso matricula`: [codigo.py](/Users/alexi/Documents/GitHub/avance_curricular/archive/legacy_runtime/codigo.py).

| Columna salida | Equivalente manual | Origen en fuente | Regla de construcción |
|---|---|---|---|
| `TIPO_DOC` | `TIPO_DOC` | constante | se fija en `"R"` |
| `N_DOC` | `N_DOC` | `RUT` o `NUM_DOCUMENTO` o `N_DOC` | copia directa |
| `DV` | `DV` | `DIG` o `DV` | copia directa |
| `PRIMER_APELLIDO` | `PRIMER_APELLIDO` | `PATERNO` o `PRIMER_APELLIDO` | copia directa; si no existe, `NA` |
| `SEGUNDO_APELLIDO` | `SEGUNDO_APELLIDO` | `MATERNO` o `SEGUNDO_APELLIDO` | copia directa; si no existe, `NA` |
| `NOMBRE` | `NOMBRE` | `NOMBRE` (fallback carrera) | copia directa |
| `SEXO` | `SEXO` | `SEXO` | copia directa; si no existe, `NA` |
| `FECH_NAC` | `FECH_NAC` | `FECHANACIMIENTO` o `FECHA_NACIMIENTO` | copia directa; si no existe, `NA` |
| `NAC` | `NAC` | `NACIONALIDAD` o `NAC` | copia directa; si no existe, `NA` |
| `PAIS_EST_SEC` | `PAIS_EST_SEC` | `PAIS_EST_SEC` | copia directa; si no existe, `NA` (en modo `avance`, fallback `CL`) |
| `COD_SED` | `COD_SED` | `COD_SED` | copia directa; si no existe, `NA` |
| `COD_CAR` | `Código Carrera` | `CODCARR` o `CODCARPR` | copia directa |
| `MODALIDAD` | `MODALIDAD` | `JORNADA` | mapeo: diurna/vespertina=`PRESENCIAL`, semi=`SEMIPRESENCIAL`, distancia/online=`DISTANCIA` |
| `JOR` | `JOR` | `JORNADA` | mapeo: diurna=`1`, vespertina=`2`, semi=`3`, distancia=`4` |
| `VERSION` | `Version` | no provista | `NA` por defecto |
| `FOR_ING_ACT` | `FOR_ING_ACT` | derivada por `scripts/motor_for_ing_act.py` desde DatosAlumnos + Hoja1 | árbol gobernable: 11 (articulación TNS→Prof) → 2 (continuidad) → 4 (externo, bloqueado) → 3 (interno por SITUACION) → 1 (directo); códigos 5-10 bloqueados; config en `control/config_for_ing_act.json` |
| `ANIO_ING_ACT` | `ANIO_ING_ACT` | `ANOINGRESO` o `ANIO_INGRESO_CARRERA_ACTUAL` | año normalizado; fallback inferido desde `CODCLI` |
| `SEM_ING_ACT` | `SEM_ING_ACT` | `PERIODOINGRESO` o `SEM_INGRESO_CARRERA_ACTUAL` | copia directa |
| `ANIO_ING_ORI` | `ANIO_ING_ORI` | derivada de `ANIO_ING_ACT` | se replica `ANIO_ING_ACT` |
| `SEM_ING_ORI` | `SEM_ING_ORI` | derivada de `SEM_ING_ACT` | se replica `SEM_ING_ACT` |
| `ASI_INS_ANT` | `ASI_INS_ANT` | `ASI_INS_ANT` (si existe) | fallback operativo `0`; en proceso `avance` se deriva de `UNIDADES_CURSADAS`; rango validado `0..99` |
| `ASI_APR_ANT` | `ASI_APR_ANT` | `ASI_APR_ANT` (si existe) | fallback operativo `0`; en proceso `avance` se deriva de `UNIDADES_APROBADAS`; rango validado `0..99` y `<= ASI_INS_ANT` |
| `PROM_PRI_SEM` | `PROM_PRI_SEM` | `PROM_PRI_SEM` (si existe) | fallback operativo `0`; rango validado `0` o `100..700` |
| `PROM_SEG_SEM` | `PROM_SEG_SEM` | `PROM_SEG_SEM` (si existe) | fallback operativo `0`; rango validado `0` o `100..700` |
| `ASI_INS_HIS` | `ASI_INS_HIS` | `ASI_INS_HIS` (si existe) | fallback operativo `0`; en proceso `avance` se deriva de `UNID_CURSADAS_TOTAL`; rango validado `0..200` |
| `ASI_APR_HIS` | `ASI_APR_HIS` | `ASI_APR_HIS` (si existe) | fallback operativo `0`; en proceso `avance` se deriva de `UNID_APROBADAS_TOTAL`; rango validado `0..200` y `<= ASI_INS_HIS` |
| `NIV_ACA` | `NIV_ACA` | `NIV_ACA` o `NIVEL` | se toma de fuente si existe; se valida `>= 1` (obligatorio según manual) |
| `SIT_FON_SOL` | `SIT_FON_SOL` | `SIT_FON_SOL` (si existe) | fallback operativo `0`; catálogo validado `0/1/2` |
| `SUS_PRE` | `SUS_PRE` | `SUS_PRE` (si existe) | fallback operativo `0`; rango validado `0..99` |
| `FECHA_MATRICULA` | `FECHA_MATRICULA` | `FECHAMATRICULA` o `FECHA_MATRICULA` | copia directa; si no existe, `NA` |
| `REINCORPORACION` | `REINCORPORACION` | `REINCORPORACION` | copia directa; fallback `0` |
| `VIG` | `VIG` | `VIGENCIA` o `VIG` | copia directa; fallback `1`; catálogo validado `0/1/2` (manual 2026) |

## 15) Salidas a usar sin confusión

- Si se requiere archivo contractual de Matrícula Unificada (32 columnas exactas), usar:
  - hoja `MATRICULA_UNIFICADA_32` de `archivo_listo_para_sies.xlsx`, o
  - `matricula_unificada_2026_pregrado.csv` como CSV regulatorio final vigente.
- Si se requiere diagnóstico operativo y trazabilidad de matching SIES, usar:
  - hoja `ARCHIVO_LISTO_SUBIDA` de `archivo_listo_para_sies.xlsx`.
- Si se requiere contexto histórico de controles o validaciones de otros flujos, revisar `archive/` y no `resultados/`.

## 16) Fuente normativa usada para gobernanza de columnas

Manual utilizado:

- `/Users/alexi/Desktop/20260106_36454_Manual_Matrícula_Unificada_2026.pdf`

Evidencia clave extraída del manual:

- Página 28: “Todos los campos son obligatorios…”
- Página 30: definiciones y rangos de `ASI_INS_ANT`, `ASI_APR_ANT`, `PROM_PRI_SEM`, `PROM_SEG_SEM`, `ASI_INS_HIS`.
- Página 31: definiciones y rangos de `ASI_APR_HIS`, `NIV_ACA`, `SIT_FON_SOL`, `SUS_PRE`, y catálogo de `VIG` (`0/1/2`).

## 17) Motor de derivación FOR_ING_ACT

A partir de abril 2026, `FOR_ING_ACT` no se toma de la fuente Excel sino que se **deriva por evidencia** usando `scripts/motor_for_ing_act.py`.

### Arquitectura

| Componente | Ruta | Función |
|---|---|---|
| Motor | `scripts/motor_for_ing_act.py` | Carga datos, calcula flags _DA, aplica árbol, genera artefactos |
| Config | `control/config_for_ing_act.json` | Códigos soportados/bloqueados, reglas, umbrales, validaciones |
| Reglas | `control/for_ing_act_rules.tsv` | Catálogo auditable de 5 reglas con prioridad y estado |
| Tests | `scripts/test_for_ing_act.py` | 19 tests: dominio, integridad, prioridad, golden cases |
| Golden cases | `control/for_ing_act_golden_cases.json` | 12 casos de prueba validados |
| Trace | `control/for_ing_act_trace_long.tsv` | Trazabilidad completa con 7 flags _DA por registro |
| Reporte | `control/for_ing_act_governance_report.md` | Dictamen, distribución, hallazgos, checklist |
| Audit XLSX | `resultados/AUDIT_FOR_ING_ACT.xlsx` | Excel con pestañas AUDITORIA, RESUMEN, HALLAZGOS |

### Árbol de decisión (orden de evaluación)

1. **Código 11 — Articulación**: TNS previo encontrado (Hoja1 o DatosAlumnos) + programa actual es profesional
2. **Código 2 — Continuidad**: programa con "CONTINUIDAD" en nombre, sin TNS previo
3. **Código 4 — Cambio Externo**: BLOQUEADO (no existe indicador explícito en DatosAlumnos)
4. **Código 3 — Cambio Interno**: SITUACION ∈ {24 - CAMBIO DE CARRERA, 49 - CAMBIO DE JORNADA, 27 - CAMBIO PLAN OTRA JORNADA}
5. **Código 1 — Ingreso Directo**: default

**Códigos 5-10**: bloqueados por política institucional, nunca emitidos.

### Flags derivados (_DA)

| Flag | Descripción | Fuente |
|---|---|---|
| `ES_CONTINUIDAD_DA` | Programa contiene "CONTINUIDAD" en NOMBRE_L | DatosAlumnos |
| `ES_TECNICO_DA` | CODCARPR empieza con T o NOMBRE_L contiene TECNICO/TNS | DatosAlumnos |
| `PROGRAMA_ACTUAL_ES_PROFESIONAL_DA` | Inverso de ES_TECNICO_DA | derivado |
| `ES_CAMBIO_INTERNO_DA` | SITUACION ∈ {24, 49, 27} | DatosAlumnos |
| `ES_CAMBIO_EXTERNO_DA` | Siempre 0 (bloqueado sin fuente) | política |
| `TIENE_TNS_PREV_DA` | Mismo RUT con programa TNS en año anterior | DatosAlumnos + Hoja1 |
| `FOR_ING_ACT_RULE_DA` | Nombre de la regla que disparó | árbol |

### Validaciones

| ID | Severidad | Descripción |
|---|---|---|
| V0 | BLOQUEANTE | FOR_ING_ACT fuera de {1,2,3,4,11} |
| V1 | WARNING | Coherencia ANIO_ING_ORI==ANIO_ING_ACT para FOR=1 (diferida) |
| V2 | ERROR | Programa CONTINUIDAD con FOR=1 (viola manual) |
| V3 | WARNING | Pasaporte → FOR∈{4,6} (diferida, TIPO_DOC no disponible) |

## 18) Motor de derivación Campos ING (ANIO_ING_ACT, SEM_ING_ACT, ANIO_ING_ORI, SEM_ING_ORI)

A partir de abril 2026, los campos Q, R, S, T del Cuadro N°1 se **derivan por reglas gobernables** usando `scripts/motor_campos_ing.py`, consumiendo el trace de `FOR_ING_ACT` como insumo.

### Arquitectura

| Componente | Ruta | Función |
|---|---|---|
| Motor | `scripts/motor_campos_ing.py` | Carga datos + trace FOR, deriva 4 campos con cascada/mapeo, genera artefactos |
| Config | `control/config_campos_ing.json` | Rangos, catálogos, mapeo PERIODOINGRESO, reglas por FOR_ING_ACT |
| Reglas | `control/campos_ing_rules.tsv` | Catálogo auditable de 22 reglas (R_ACT, R_SEM, R_ORI_A, R_ORI_S) |
| Tests | `scripts/test_campos_ing.py` | 26 tests: reglas ACT/SEM, coherencia FOR×ORI, catálogos, golden cases |
| Golden cases | `control/campos_ing_golden_cases.json` | 9 casos de prueba validados |
| Trace | `control/campos_ing_trace_long.tsv` | Trazabilidad 1364 registros: 4 campos + fuente + regla |
| Reporte | `control/campos_ing_governance_report.md` | Dictamen, distribución, coherencia FOR×ORI, hallazgos |
| Audit XLSX | `resultados/AUDIT_CAMPOS_ING.xlsx` | Excel con TRAZABILIDAD, RESUMEN×4, CRUCE_FOR×ORI, HALLAZGOS |

### Reglas de derivación

**ANIO_ING_ACT (Campo Q)**: Cascada `ANOINGRESO → DA_ANOINGRESO → CODCLI[:4] → 2026`. Rango válido: [1990, 2026].

**SEM_ING_ACT (Campo R)**: Mapeo institucional de PERIODOINGRESO: `{1→1, 2→2, 3→2}`. Catálogo: {1, 2}.

**ANIO_ING_ORI (Campo S)** — depende de FOR_ING_ACT:

| FOR | Regla | Valor |
|-----|-------|-------|
| 1 | COPIA_ACTUAL | = ANIO_ING_ACT |
| 11 | TNS_PREV | = TNS_PREV_MIN_ANO_DA (o 1900 si desconocido) |
| 2 | ORIGEN_DESCONOCIDO | = 1900 |
| 3 | BUSCAR_PROG_ANTERIOR | = ANOINGRESO del programa anterior en DA/Hoja1 (o 1900) |
| 4 | BLOQUEADO | = 1900 |

**SEM_ING_ORI (Campo T)** — depende de FOR_ING_ACT + ANIO_ING_ORI:

| Condición | Valor |
|-----------|-------|
| FOR=1 | = SEM_ING_ACT |
| ANIO_ING_ORI=1900 | = 0 (invariante) |
| FOR=11 con periodo TNS | = periodo del primer registro TNS en Hoja1 |
| FOR=3 con prog anterior | = periodo del programa anterior |
| Sin datos | = 0 |

### Validaciones

| ID | Severidad | Descripción |
|---|---|---|
| V_RANGO_ACT | BLOQUEANTE | ANIO_ING_ACT fuera de [1990, 2026] |
| V_CATALOGO_SEM_ACT | BLOQUEANTE | SEM_ING_ACT fuera de {1, 2} |
| V_RANGO_ORI | BLOQUEANTE | ANIO_ING_ORI fuera de [1980, 2026] ∪ {1900} |
| V_CATALOGO_SEM_ORI | BLOQUEANTE | SEM_ING_ORI fuera de {0, 1, 2} |
| V_COHERENCIA_FOR1 | BLOQUEANTE | FOR=1 y ORI ≠ ACT |
| V_COHERENCIA_1900 | BLOQUEANTE | ANIO_ORI=1900 con SEM_ORI ≠ 0 |
| V_COHERENCIA_FOR_NO1 | WARNING | FOR≠1 con ANIO_ACT ≤ ANIO_ORI (excepto ORI=1900) |

## §19. Motor de derivación VIG + FECHA_MATRICULA

### Arquitectura

| Componente | Ruta |
|-----------|------|
| Motor | `scripts/motor_vig_fecha.py` |
| Config | `control/config_vig_fecha.json` |
| Reglas | `control/vig_fecha_rules.tsv` (16 reglas) |
| Tests | `scripts/test_vig_fecha.py` (23 tests, 4 clases) |
| Trace | `control/vig_fecha_trace_long.tsv` |
| Auditoría | `resultados/AUDIT_VIG_FECHA.xlsx` |
| Reporte | `control/vig_fecha_governance_report.md` |

### Derivación AF VIG (Vigencia)

Campo AF del Cuadro N°1. Valores permitidos: 0, 1, 2.

| ESTADOACADEMICO | VIG | Regla | Significado |
|----------------|-----|-------|------------|
| VIGENTE | 1 | R_VIG_01 | Matrícula vigente |
| ELIMINADO | 0 | R_VIG_02 | Sin matrícula |
| SUSPENDIDO | 0 | R_VIG_03 | Sin matrícula |
| EGRESADO | 2 | R_VIG_04 | Egresado con matrícula vigente |
| TITULADO | 0 | R_VIG_05 | Titulado (ya completó) |
| null/vacío | 1 | R_VIG_10 | Fallback default |
| No reconocido | 1 | R_VIG_11 | Fallback default |

Cascada: mapeo exacto → mapeo parcial (contains) → fallback VIG=1.

### Derivación AD FECHA_MATRICULA

Campo AD del Cuadro N°1. Formato: dd/mm/yyyy.

| Condición | Resultado | Regla |
|----------|-----------|-------|
| FECHAMATRICULA parseable | dd/mm/yyyy | R_FM_01 |
| Fecha nula/inválida | 01/01/1900 | R_FM_03 |

### Validaciones

| Validación | Severidad | Condición |
|-----------|-----------|----------|
| V_CATALOGO_VIG | BLOQUEANTE | VIG fuera de {0, 1, 2} |
| V_COHERENCIA_VIG_ESTADO | BLOQUEANTE | VIG incoherente con catálogo gobernanza |
| V_FORMATO_FECHA | BLOQUEANTE | FECHA_MATRICULA en formato inválido |
| V_FECHA_NO_FUTURA | WARNING | Fecha posterior a 2026-04-30 |
| V_FECHA_RANGO | WARNING | Fecha anterior a 2020-01-01 |
| V_VIG0_MARCADO_ROJO | INFO | Filas VIG=0 marcadas en rojo en auditoría |
