# Resultado Corrida Referencia MU 2026

Documento de contraste congelado. No reemplaza el gate vigente ni la distribución actual de `FOR_ING_ACT` observada en `resultados/reporte_for_ing_act.json`.

- Fecha de corrida de referencia: 2026-04-01
- Input usado: [PROMEDIOSDEALUMNOS_7804.xlsx](/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx)
- Output usado: [resultados/](/Users/alexi/Documents/GitHub/avance_curricular/resultados)

## Comando de ejecución usado

```bash
cd /ruta/al/repo/avance_curricular
export INPUT_XLSX="/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx"
export OUTPUT_DIR="resultados"
python3 codigo_gobernanza_v2.py --input "$INPUT_XLSX" --output-dir "$OUTPUT_DIR" --proceso matricula --usar-gobernanza-v2 true
```

## Resultado observado de la ejecución

- `output_file = resultados/archivo_listo_para_sies.xlsx`
- `csv_output_file = resultados/matricula_unificada_2026_pregrado.csv`
- `sheet_used = Hoja1`
- `gobernanza_mode = v2_flagged`
- `rows = 24827`
- `rows_matricula_32_final = 1736`
- `rows_excluidas_carga_pregrado = 23091`
- `rows_excluidas_sies_heuristica_opaca = 7973`
- `rows_excluidas_sin_for_ing_act_trazable = 0`
- `rows_enriquecidas_datos_alumnos = 24607`
- `rows_sin_match_datos_alumnos = 220`
- `historico_mu_anio_referencia = 2025`
- `FOR_ING_ACT` final: `{'1': 1736}`

## Comando de validación usado

```bash
cd /ruta/al/repo/avance_curricular
export OUTPUT_DIR="resultados"
python3 qa_checks.py --output-dir "$OUTPUT_DIR" --fase6-control-dir "control"
```

## Resultado observado de la validación

- `qa_checks_ok`
- `decision_final = CONDICIONAL`
- `listo_para_auditoria = true`
- `listo_para_carga = false`
- `ok_count = 27`
- `pending_count = 5`
- `pending_columns = [Y ASI_INS_HIS, Z ASI_APR_HIS, AB SIT_FON_SOL, AC SUS_PRE, AE REINCORPORACION]`

## Invariantes observadas

- CSV final sin header: `SI`
- 32 columnas exactas: `SI`
- separador `;`: `SI`
- `SEXO` solo `H/M/NB`: `SI`
- `FOR_ING_ACT = 1` en esta referencia congelada: `SI`
- exclusión de `PRIMERA_OPCION`: `SI`

## Distribuciones observadas en la corrida de referencia

- Filas finales CSV: `1736`
- `SEXO`: `{'H': 1305, 'M': 428, 'NB': 3}`
- `FOR_ING_ACT`: `{'1': 1736}`

## Artefactos generados o verificados

- [archivo_listo_para_sies.xlsx](/Users/alexi/Documents/GitHub/avance_curricular/resultados/archivo_listo_para_sies.xlsx)
- [matricula_unificada_2026_pregrado.csv](/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_pregrado.csv)
- [gate_final_mu_2026.md](/Users/alexi/Documents/GitHub/avance_curricular/control/gate/gate_final_mu_2026.md)
- [backlog_residual_mu_2026.tsv](/Users/alexi/Documents/GitHub/avance_curricular/control/pendientes/backlog_residual_mu_2026.tsv)

## Conclusión de reproducibilidad

La corrida de referencia reproduce el estado congelado de contraste del `2026-04-01`: `CONDICIONAL`, `27 OK / 5 Pendiente`, auditable y no listo para carga.
