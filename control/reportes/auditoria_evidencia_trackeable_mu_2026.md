# Auditoria Evidencia Trackeable MU 2026

- Fecha: 2026-04-01
- Regla global que ocultaba evidencia critica antes de esta iteracion: `.gitignore` con `*.tsv`.
- Evidencia afectada antes del ajuste:
  - `control/tablero_mu_2026.tsv`
  - `control/reportes/reporte_fech_nac.tsv`
  - `control/reportes/reporte_nac_pais_sec.tsv`
  - `control/reportes/sies_pendientes.tsv`

## Correccion aplicada

- Se agregaron excepciones explicitas en `.gitignore` para:
  - `!control/tablero_mu_2026.tsv`
  - `!control/reportes/reporte_fech_nac.tsv`
  - `!control/reportes/reporte_nac_pais_sec.tsv`
  - `!control/reportes/sies_pendientes.tsv`
- No se abrio tracking masivo de `*.tsv`; solo quedaron re-incluidos los artefactos de control operativo/auditable.

## Verificacion posterior

- `git check-ignore -v` ya no aplica la regla global `*.tsv` como bloqueo final sobre esos archivos.
- El mismo comando resuelve ahora a las excepciones explicitas de `.gitignore`:
  - `control/tablero_mu_2026.tsv`
  - `control/reportes/reporte_fech_nac.tsv`
  - `control/reportes/reporte_nac_pais_sec.tsv`
  - `control/reportes/sies_pendientes.tsv`
- `git status --short` muestra estos archivos como trackeables en la working tree.

## Resultado

- La evidencia critica del tablero y de las colas/reportes auditables ya no queda oculta por reglas globales de ignore.
