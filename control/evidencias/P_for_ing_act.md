# Evidencia P - FOR_ING_ACT

- Columna: P
- Campo: FOR_ING_ACT
- Fase duena: FASE 0
- Estado tablero: OK
- Fecha: 2026-04-19
- Responsable:

## Bloqueo actual

- Sin bloqueo operativo.

## Fuente operativa revisada

- gobernanza_columnas_mu/gob_mu_for_ing_act.tsv
- resultados/reporte_for_ing_act.json
- control/gate/gate_final_mu_2026.md

## Regla vigente observada

- El runtime oficial resuelve `FOR_ING_ACT` dentro de `codigo_gobernanza_v2.py`, conserva el catálogo manual `1..11` y no lo sobreescribe a `1`.
- La validación oficial exige distribución consistente entre `ARCHIVO_LISTO_SUBIDA` y CSV final, con trazabilidad por fila y sin imputados/revisión en filas incluidas.

## Validacion ejecutada

- Validación oficial con `qa_checks.py --fase3-control-dir control --fase6-control-dir control`.
- Distribución vigente observada en stage y CSV final: `1=2926`, `2=383`, `3=84`, `11=32`, `6=8`.
- `FOR_ING_ACT_IMPUTADO = 0` y `FOR_ING_ACT_REQUIERE_REVISION = 0` en filas incluidas.

## Resultado

- OK sostenido.

## Riesgo residual

- Bajo. Mantener monitoreo si aparecieran códigos `4/5/7/8/9/10` en filas incluidas o nuevas fuentes no trazadas.

## Criterio de cierre a OK

- Ya en OK; mantener catálogo `1..11`, distribución consistente stage/CSV y trazabilidad completa por fila incluida.

## Evidencia adjunta

- `resultados/reporte_for_ing_act.json`
- `control/gate/gate_final_mu_2026.md`
- `resultados/archivo_listo_para_sies.xlsx`
