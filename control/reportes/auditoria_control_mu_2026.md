# Auditoria de control/ - MU 2026

- Fecha: 2026-04-01
- Alcance: verificacion de `control/` contra la verdad cerrada del tablero.

## Inconsistencias detectadas

1. `control/tablero_mu_2026.tsv` tenia fases duenas incompatibles con la distribucion aprobada.
2. `archive/control_historico/fases/fase_0_baseline.md` estaba modelada como fase de columnas `A/B/C/J`, pero la verdad cerrada fija `FASE 0` para `D/F/G/P`.
3. `archive/control_historico/fases/fase_1_identidad.md` estaba modelada como fase de `D/E/F/G/H/I`, pero la verdad cerrada fija `FASE 1` para `A/B/C/E/H/I/J`.
4. `archive/control_historico/fases/fase_3_cronologia.md` no incluia `AA NIV_ACA`, que pertenece a `FASE 3`.
5. `archive/control_historico/fases/fase_4_rendimiento.md` incluia `AA NIV_ACA`, pero esa columna no pertenece a `FASE 4`.
6. Los expedientes en `control/evidencias/*.md` replicaban las fases duenas incorrectas para `A`, `B`, `C`, `D`, `F`, `G`, `J`, `P` y `AA`.

## Correccion aplicada

- Se alineo `control/` completo con la distribucion cerrada:
  - `FASE 0`: `D`, `F`, `G`, `P`
  - `FASE 1`: `A`, `B`, `C`, `E`, `H`, `I`, `J`
  - `FASE 2`: `K`, `L`, `M`, `N`, `O`
  - `FASE 3`: `Q`, `R`, `S`, `T`, `AA`, `AD`
  - `FASE 4`: `U`, `V`, `W`, `X`, `Y`, `Z`
  - `FASE 5`: `AB`, `AC`, `AE`, `AF`
  - `FASE 6`: gate final

## Resultado

- Estados preservados: `OK` solo para `D`, `F`, `G`, `P`; `Pendiente` para las otras 28 columnas.
- Fases duenas corregidas antes de ejecutar FASE 1 real.
