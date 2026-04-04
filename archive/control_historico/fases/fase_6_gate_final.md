# FASE 6 - Gate Final

## Objetivo

Consolidar la decision final del lote documental sin cambiar el tablero ni las invariantes.

## Entradas obligatorias

- `control/tablero_mu_2026.tsv`
- `control/baseline_mu_2026.json`
- `control/reportes/`
- `control/evidencias/`
- `control/pendientes/plantilla_backlog_residual_bloqueo.tsv`
- `control/gate/gate_final_mu_2026.md`

## Checklist de iteracion

1. Confirmar que solo existan estados `OK` y `Pendiente`.
2. Confirmar que las cuatro columnas cerradas sigan en `OK`.
3. Confirmar que no existan cambios de fase no autorizados.
4. Confirmar invariantes globales del lote.
5. Emitir decision de gate en `control/gate/gate_final_mu_2026.md`.

## Resultado esperado

- `APROBADO` solo si invariantes y evidencias estan completas y no existe bloqueo critico abierto.
- `CONDICIONAL` si persisten pendientes no bloqueantes pero estan trazados.
- `RECHAZADO` si se rompe algun invariante o falta trazabilidad minima.
