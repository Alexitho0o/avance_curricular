# Validación Oficial MU 2026

- Fecha de congelamiento: 2026-04-01
- Baseline congelada de referencia: `CONDICIONAL`

## Unica forma oficial de validar

```bash
make validate-oficial
```

Si se requiere disparar ejecución + validación en una sola secuencia:

```bash
make run-and-validate-oficial INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
```

Equivalente subyacente:

```bash
cd /ruta/al/repo/avance_curricular
export OUTPUT_DIR="resultados"
python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase3-control-dir "control" --fase6-control-dir "control"
```

## Por que esta es la forma oficial

- Valida los invariantes estructurales del CSV final.
- Queda autoservida y versionada dentro del repo vía `Makefile` y `scripts/`.
- Refresca la evidencia cronológica FASE 3 usada por `ANIO_ING_ORI` y `SEM_ING_ORI`.
- Recalcula el gate final sobre el estado vigente del tablero.
- Refresca [gate_final_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/gate/gate_final_mu_2026.md).
- Refresca [reporte_cronologia_mu_2026.json](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/reporte_cronologia_mu_2026.json) y [reporte_fase_3_cronologia_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/reporte_fase_3_cronologia_mu_2026.md).
- Refresca [backlog_residual_mu_2026.tsv](/Users/alexi/Documents/GitHub/avance_curricular/control/pendientes/backlog_residual_mu_2026.tsv) en formato ejecutivo.
- Devuelve un resultado máquina-legible con `qa_checks_ok`.

## Prerequisitos

- Haber ejecutado antes el comando oficial documentado en [ejecucion_oficial_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/reportes/ejecucion_oficial_mu_2026.md).
- Ejecutar desde la raíz del repo.
- Existencia de:
  - [archivo_listo_para_sies.xlsx](/Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx)
  - [matricula_unificada_2026_pregrado.csv](/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_pregrado.csv)
  - [tablero_mu_2026.tsv](/Users/alexi/Documents/GitHub/avance_curricular/control/tablero_mu_2026.tsv)

## Resultado esperado mínimo

- `qa_checks_ok`
- invariantes en `true` para:
  - `csv_final_sin_header`
  - `columnas_exactas_32`
  - `separador_punto_y_coma`
  - `sexo_valido`
  - `for_ing_act_catalogo_1_11`
  - `for_ing_act_continuidad_origen_distinto`
  - `exclusion_primera_opcion`
- distribución stage/CSV consistente para `FOR_ING_ACT`
- `FOR_ING_ACT_IMPUTADO = 0`
- `FOR_ING_ACT_REQUIERE_REVISION = 0`
- con los outputs versionados actuales del repo, el gate vigente queda en `APROBADO`, `32 OK / 0 Pendiente`

## Artefactos verificados o refrescados

- [matricula_unificada_2026_pregrado.csv](/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_pregrado.csv)
- [archivo_listo_para_sies.xlsx](/Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx)
- [gate_final_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/gate/gate_final_mu_2026.md)
- [backlog_residual_mu_2026.tsv](/Users/alexi/Documents/GitHub/avance_curricular/control/pendientes/backlog_residual_mu_2026.tsv)

## Lo que no hace esta validación

- No reescribe el runtime de exportación.
- No corrige por sí sola una fuente faltante fuera de los artefactos ya presentes en `resultados/`.
- No convierte artefactos históricos o archivados en autoridad operativa.
