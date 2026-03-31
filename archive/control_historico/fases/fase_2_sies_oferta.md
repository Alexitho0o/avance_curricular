# FASE 2 - SIES Oferta

## Objetivo

Cerrar trazabilidad de oferta, sede, carrera y atributos derivados de la capa SIES/oferta sin reabrir el tablero.

## Columnas duenas

- K `COD_SED`
- L `COD_CAR`
- M `MODALIDAD`
- N `JOR`
- O `VERSION`

## Entradas obligatorias

- `control/tablero_mu_2026.tsv`
- `control/baseline_mu_2026.json`
- `puente_sies.tsv`
- `matriz_desambiguacion_sies_final.tsv`
- `gobernanza_columnas_mu/gob_mu_cod_sed.tsv`
- `gobernanza_columnas_mu/gob_mu_cod_car.tsv`
- `gobernanza_columnas_mu/gob_mu_modalidad.tsv`
- `gobernanza_columnas_mu/gob_mu_jor.tsv`
- `gobernanza_columnas_mu/gob_mu_version.tsv`

## Checklist de iteracion

1. Revisar match contractual vigente para sede y carrera.
2. Confirmar tabla de mapeo a `MODALIDAD` y `JOR`.
3. Dejar evidencia exacta de la derivacion de `VERSION`.
4. Registrar cualquier bloqueo residual por dependencia de oferta/SIES.
5. Emitir reporte de fase.

## Criterio de salida

- Trazabilidad de oferta cerrada por columna.
- Mapeos documentados y referenciados en evidencia.
- Bloqueos residuales escalados por backlog si corresponde.
