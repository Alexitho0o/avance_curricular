# FASE 0 - Baseline

## Objetivo

Congelar baseline operativo, invariantes y columnas ya cerradas sin redisenar el tablero.

## Columnas duenas

- D `PRIMER_APELLIDO`
- F `NOMBRE`
- G `SEXO`
- P `FOR_ING_ACT`

## Entradas obligatorias

- `control/baseline_mu_2026.json`
- `control/tablero_mu_2026.tsv`
- `gobernanza_columnas_mu/gob_mu_primer_apellido.tsv`
- `gobernanza_columnas_mu/gob_mu_nombre.tsv`
- `gobernanza_columnas_mu/gob_mu_sexo.tsv`
- `gobernanza_columnas_mu/gob_mu_for_ing_act.tsv`

## Checklist de iteracion

1. Confirmar que no cambiaron estados, fases ni invariantes.
2. Confirmar que `D`, `F`, `G` y `P` permanezcan en `OK`.
3. Actualizar evidencias por columna en `control/evidencias/`.
4. Emitir reporte usando `control/reportes/plantilla_reporte_fase.md`.
5. Si aparece una degradacion, registrarla como incidente antes de tocar estados.

## Criterio de salida

- Todas las filas de la fase tienen revision actualizada.
- No hay desviaciones sobre `csv sin header`, `32 columnas`, `;`, `SEXO` valido, `FOR_ING_ACT = 1`, exclusion de `PRIMERA_OPCION`.
- Existe reporte de fase emitido.

## No permitido

- Reclasificar columnas.
- Mover columnas a otra fase.
- Cambiar estados binarios cerrados.
