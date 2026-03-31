# Validación Oficial MU 2026

- Fecha de congelamiento: 2026-04-01
- Estado congelado esperado: `CONDICIONAL`

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
python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase6-control-dir "control"
```

## Por que esta es la forma oficial

- Valida los invariantes estructurales del CSV final.
- Queda autoservida y versionada dentro del repo vía `Makefile` y `scripts/`.
- Recalcula el gate final sobre el estado vigente del tablero.
- Refresca [gate_final_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/gate/gate_final_mu_2026.md).
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
- `decision_final = CONDICIONAL`
- `ok_count = 27`
- `pending_count = 5`
- invariantes en `true` para:
  - `csv_final_sin_header`
  - `columnas_exactas_32`
  - `separador_punto_y_coma`
  - `sexo_valido`
  - `for_ing_act_fijo_1`
  - `exclusion_primera_opcion`

## Artefactos verificados o refrescados

- [matricula_unificada_2026_pregrado.csv](/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_pregrado.csv)
- [archivo_listo_para_sies.xlsx](/Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx)
- [gate_final_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/gate/gate_final_mu_2026.md)
- [backlog_residual_mu_2026.tsv](/Users/alexi/Documents/GitHub/avance_curricular/control/pendientes/backlog_residual_mu_2026.tsv)

## Lo que no hace esta validación

- No reabre columnas en `OK`.
- No intenta cerrar `Y`, `Z`, `AB`, `AC` o `AE`.
- No reemplaza una fuente faltante ni una decisión funcional/normativa pendiente.
