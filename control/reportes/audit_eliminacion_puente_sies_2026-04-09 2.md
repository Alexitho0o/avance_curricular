# Auditoria Eliminacion de puente_sies.tsv (MU 2026)

Fecha: 2026-04-09  
Repositorio: `avance_curricular`

## 1) Objetivo

Eliminar `puente_sies.tsv` como dependencia operativa del cruce SIES, dejando:

- Canónico de oferta/duración: `DURACION_ESTUDIOS.tsv`
- Canónico runtime de cruce SIES: `control/catalogos/PUENTE_SIES_COMPILADO.tsv`
- Flujo oficial (`make run-and-validate-oficial`) sin consumo directo de `puente_sies.tsv`

## 2) Diagnostico (reglas CICIB)

Reglas históricas del puente (respaldo humano):

1. `V|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` -> `I162S2C46J2V3`
2. `O|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` -> `I162S2C46J4V1`

Evidencia previa sin override (diagnóstico pre-remediación):

- `control/reportes/reporte_compilacion_puente_sies_diag_pre.json`
- `override_rows = 0`
- `total_source_keys = 159` (faltaban 2 llaves de continuidad CICIB)

## 3) Remediacion canonica aplicada en DURACION_ESTUDIOS.tsv

Se consolidó en el canónico (no override) agregando 2 filas de continuidad con los mismos `CODIGO_UNICO` de oferta real:

- `DURACION_ESTUDIOS.tsv:77` -> `I162S2C46J2V3` con `NOMBRE_CARRERA = CONTINUIDAD INGENIERIA  CIBERSEGURIDAD`, `JORNADA=2`, `CODCARPR_CANONICO=CICIB`, `CODCARPR_RESOLUCION_ESTADO=UNICO`, `FUENTE_GOBERNANZA=REVISION_MANUAL`.
- `DURACION_ESTUDIOS.tsv:79` -> `I162S2C46J4V1` con `NOMBRE_CARRERA = CONTINUIDAD INGENIERIA  CIBERSEGURIDAD`, `JORNADA=4`, `CODCARPR_CANONICO=CICIB`, `CODCARPR_RESOLUCION_ESTADO=UNICO`, `FUENTE_GOBERNANZA=REVISION_MANUAL`.

Nota de trazabilidad:

- `DURACION_ESTUDIOS.tsv` está ignorado por `.gitignore` (`*.tsv`), por lo que el cambio no aparece en `git diff` aunque sí queda operativo en runtime.

## 4) Verificacion de compilado canónico sin puente

Comando ejecutado:

```bash
make compile-sies
```

Evidencia:

- `control/reportes/reporte_compilacion_puente_sies.json`
  - `base_rows = 257`
  - `override_rows = 0`
  - `total_source_keys = 161`
  - `source_keys_unicos = 91`
  - `source_keys_ambiguos = 70`
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv` contiene ambas llaves como `UNICO`:
  - Línea 35: `O|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` -> `I162S2C46J4V1`
  - Línea 119: `V|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` -> `I162S2C46J2V3`

## 5) Eliminacion de dependencia operativa puente_sies.tsv

Estado final de archivo puente:

- `puente_sies.tsv` en raíz: **NO ENCONTRADO**
- Respaldo: `control/backups/puente_sies_eliminado_2026-04-09.tsv`

Verificación de flujo:

- El runtime cruza SIES contra `control/catalogos/PUENTE_SIES_COMPILADO.tsv` (no puente directo).
- `cruces_proyecto.tsv:60` mantiene cruce central L2447 contra compilado canónico.

## 6) Ejecucion oficial + QA (sin puente)

Comando ejecutado:

```bash
make run-and-validate-oficial \
  INPUT_XLSX="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
  OUTPUT_DIR="resultados/run_and_validate_oficial_2026-04-09_sin_puente"
```

Resultados:

- No se generó `resultados/run_and_validate_oficial_2026-04-09_sin_puente/sies_combinaciones_nuevas_bloqueantes.tsv`.
- `qa_checks.py`: `qa_checks_ok`.
- `resultados/run_and_validate_oficial_2026-04-09_sin_puente/auditoria_maestra.md`: `Dictamen: LISTO PARA ENTREGA`.
- Contrato MU32 verificado:
  - `matricula_unificada_2026_pregrado.csv` sin header, delimitador `;`, 32 columnas.
  - Conteo observado: `1282` filas, `32` columnas por fila.

Validación puntual de llaves CICIB en universo observado:

- `V|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` -> `MATCH_SIES_UNICO` -> `I162S2C46J2V3`
- `O|CICIB|CONTINUIDAD INGENIERIA CIBERSEGURIDAD` -> `MATCH_SIES_UNICO` -> `I162S2C46J4V1`
- `SIN_MATCH_SIES` total en corrida: `0`

No regresión de ambiguos observados (comparado con corrida previa `run_and_validate_oficial_2026-04-09_fix_cicre_v2`):

- `MATCH_SIES_AMBIGUO`: `1553 -> 1553` (sin aumento)
- `MATCH_SIES_UNICO`: `4589 -> 4589`

## 7) Cambios aplicados (diff resumido)

- `DURACION_ESTUDIOS.tsv`: +2 filas de continuidad CICIB (`J2/J4`) para resolver llaves sin override.
- `puente_sies.tsv` retirado de raíz y respaldado en `control/backups/puente_sies_eliminado_2026-04-09.tsv`.
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv` recompilado desde `DURACION_ESTUDIOS.tsv` con `override_rows=0`.
- `control/reportes/reporte_compilacion_puente_sies.json` actualizado a estado sin overrides.

## Dictamen final

**LISTO**

La dependencia operativa de `puente_sies.tsv` quedó eliminada sin romper el flujo oficial, preservando trazabilidad del linaje SIES y manteniendo el contrato MU32 intacto.
