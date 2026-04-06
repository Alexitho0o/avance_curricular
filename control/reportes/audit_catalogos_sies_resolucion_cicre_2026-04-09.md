# Resolución Bloqueo SIES CICRE (MU 2026)

Fecha: 2026-04-09  
Repositorio: `avance_curricular`

## 1) Bloqueo de origen

Llave bloqueante observada en corridas oficiales previas:

- `V|CICRE|CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES`

Evidencia (runs fallidos previos):

- `resultados/run_and_validate_oficial_2026-04-09_catalogos/sies_combinaciones_nuevas_bloqueantes.tsv`
- `resultados/run_and_validate_oficial_2026-04-09_catalogos_minimo/sies_combinaciones_nuevas_bloqueantes.tsv`
- `resultados/run_oficial_compilado_2026-04-09/sies_combinaciones_nuevas_bloqueantes.tsv`

## 2) Determinación del CODIGO_UNICO con evidencia

### Evidencia del universo real

En `resultados/archivo_listo_para_sies.xlsx` (hoja `ARCHIVO_LISTO_SUBIDA`) la llave estaba en:

- `SIES_MATCH_STATUS = SIN_MATCH_SIES`
- `SIES_MATCH_DIAG = PROBABLE_PROBLEMA_JORNADA_SIES`
- `PLAN_DE_ESTUDIO = CICRE20241`
- `JORNADA_FUENTE = V`

Para la misma carrera/plan en jornada `O`, el pipeline resolvía consistentemente a:

- `CODIGO_CARRERA_SIES_FINAL = I162S2C3J4V3`
- `VERSION = 3`
- `COD_CAR = 3`

### Evidencia en `DURACION_ESTUDIOS.tsv`

Filtro solicitado:

- `CODIGO_CARRERA = 3`
- `JORNADA = 2`
- búsqueda por `CODCARPR_CANONICO = CICRE` o `CODCARPR_ALIAS_LIST` contiene `CICRE`

Resultado:

- Candidato encontrado para jornada `2` con `CICRE`: **`I162S2C3J2V3`** (único bajo ese criterio).
- No existía fila con nombre exacto `CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES` en jornada `2`.

Dictamen técnico de selección:

- Se selecciona `I162S2C3J2V3` por consistencia de carrera (`C3`), jornada (`J2`), plan continuidad (versión `V3`) y patrón observado en jornada `O` (`...J4V3`).
- No hubo empate de candidatos bajo criterio `CICRE + J2`, por lo que no se marcó `PENDIENTE_GOBERNANZA` para esta llave.

## 3) Decisión de catalogación y cambio mínimo

Se corrigió en **`DURACION_ESTUDIOS.tsv`** (canónico de oferta/duración), no en override, porque el problema era ausencia de oferta/nombre en catálogo base para jornada `2`.

Fila agregada (evidencia):

- `DURACION_ESTUDIOS.tsv:153`
- `CODIGO_UNICO = I162S2C3J2V3`
- `NOMBRE_CARRERA = CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES`
- `CODCARPR_CANONICO = CICRE`
- `FUENTE_GOBERNANZA = REVISION_MANUAL`
- `CODCARPR_RESOLUCION_ESTADO = UNICO`

## 4) Recompilación canónica

Comando:

- `make compile-sies`

Resultado (`control/reportes/reporte_compilacion_puente_sies.json`):

- `base_rows: 255`
- `override_rows: 2`
- `total_source_keys: 161`
- `source_keys_unicos: 91`
- `source_keys_ambiguos: 70`
- `source_keys_pendiente_gobernanza: 21`
- `cobertura_llaves_unicas_pct: 56.52`

Validación directa en compilado:

- `V|CICRE|CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES` =>
  - `RESOLUCION_STATUS = UNICO`
  - `CODIGO_UNICO_FINAL = I162S2C3J2V3`

## 5) Ejecución oficial + QA

Comando ejecutado:

- `make run-and-validate-oficial INPUT_XLSX="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" OUTPUT_DIR="resultados/run_and_validate_oficial_2026-04-09_fix_cicre_v2"`

Resultado:

- Ejecución pipeline: OK
- `qa_checks.py`: OK (`qa_checks_ok`)
- `scripts/auditoria_maestra.py`: `DICTAMEN: LISTO PARA ENTREGA`

Evidencia de desbloqueo:

- No existe `resultados/run_and_validate_oficial_2026-04-09_fix_cicre_v2/sies_combinaciones_nuevas_bloqueantes.tsv`
- En `archivo_listo_para_sies.xlsx` de esa corrida, la llave objetivo queda:
  - `SIES_MATCH_STATUS = MATCH_SIES`
  - `SIES_MATCH_DIAG = MATCH_SIES_UNICO`
  - `CODIGO_CARRERA_SIES_FINAL = I162S2C3J2V3`
- Conteo `SIN_MATCH_SIES` en `ARCHIVO_LISTO_SUBIDA`: `0`

## 6) Estado documental y trazabilidad

- `README.md` mantiene referencia explícita a `cruces_proyecto.tsv`.
- `cruces_proyecto.tsv` ya apunta en L2447 al catálogo compilado:
  - `bridge_exact (control/catalogos/PUENTE_SIES_COMPILADO.tsv)`
- No cambió el origen del cruce SIES en esta resolución puntual; no se requirió ajuste adicional de contrato.

## Dictamen final

**LISTO**

La llave bloqueante `V|CICRE|CONTINUIDAD INGENIERIA CONECTIVIDAD Y REDES` quedó resuelta con evidencia trazable, el catálogo canónico fue recompilado y la corrida oficial con validación completa cerró en verde.
