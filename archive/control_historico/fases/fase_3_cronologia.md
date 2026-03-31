# FASE 3 - Cronologia

## Objetivo

Cerrar reglas temporales y cronologicas sin romper los invariantes globales.

## Columnas duenas

- Q `ANIO_ING_ACT`
- R `SEM_ING_ACT`
- S `ANIO_ING_ORI`
- T `SEM_ING_ORI`
- AA `NIV_ACA`
- AD `FECHA_MATRICULA`

## Entradas obligatorias

- `control/tablero_mu_2026.tsv`
- `control/baseline_mu_2026.json`
- `gobernanza_columnas_mu/gob_mu_anio_ing_act.tsv`
- `gobernanza_columnas_mu/gob_mu_sem_ing_act.tsv`
- `gobernanza_columnas_mu/gob_mu_anio_ing_ori.tsv`
- `gobernanza_columnas_mu/gob_mu_sem_ing_ori.tsv`
- `gobernanza_columnas_mu/gob_mu_niv_aca.tsv`
- `gobernanza_columnas_mu/gob_mu_fecha_matricula.tsv`

## Checklist de iteracion

1. Revisar consistencia entre actual y origen.
2. Validar catalogos cronologicos, acotacion de nivel y formatos de fecha.
3. Registrar excepciones y backlog residual si no quedan cerradas.
4. Emitir reporte de fase.

## Criterio de salida

- Reglas temporales quedan trazadas por columna.
- La evidencia muestra compatibilidad con el gate final.
