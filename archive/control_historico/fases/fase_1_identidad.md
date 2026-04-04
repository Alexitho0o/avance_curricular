# FASE 1 - Identidad

## Objetivo

Cerrar campos identitarios y personales de la fase sin defaults silenciosos invisibles.

## Columnas duenas

- A `TIPO_DOC`
- B `N_DOC`
- C `DV`
- E `SEGUNDO_APELLIDO`
- H `FECH_NAC`
- I `NAC`
- J `PAIS_EST_SEC`

## Entradas obligatorias

- `control/tablero_mu_2026.tsv`
- `control/baseline_mu_2026.json`
- `gobernanza_columnas_mu/gob_mu_tipo_doc.tsv`
- `gobernanza_columnas_mu/gob_mu_n_doc.tsv`
- `gobernanza_columnas_mu/gob_mu_dv.tsv`
- `gobernanza_columnas_mu/gob_mu_segundo_apellido.tsv`
- `gobernanza_columnas_mu/gob_mu_fech_nac.tsv`
- `gobernanza_columnas_mu/gob_mu_nac.tsv`
- `gobernanza_columnas_mu/gob_mu_pais_est_sec.tsv`

## Checklist de iteracion

1. Validar `TIPO_DOC`, `N_DOC` y `DV` como bloque documental coherente.
2. Cerrar o bloquear exactamente `SEGUNDO_APELLIDO`, `FECH_NAC`, `NAC` y `PAIS_EST_SEC`.
3. Cuantificar defaults, vacios permitidos y filas que requieren revision.
4. Registrar bloqueos residuales si no se puede cerrar un campo.
5. Emitir reporte de fase.

## Criterio de salida

- Toda columna de la fase queda con gate binario 5/5 o con bloqueo exacto.
- La evidencia deja trazabilidad suficiente para decision de gate.
