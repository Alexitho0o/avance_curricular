# Control MU 2026

Este directorio materializa el tablero cerrado de Matricula Unificada Pregrado 2026 como capa operativa del repo.

## Estado congelado actual

- Decision vigente: `CONDICIONAL`
- Listo para auditoria: `SI`
- Listo para carga: `NO`
- Conteo vigente del tablero: `27 OK / 5 Pendiente`
- Pendientes residuales vigentes: `Y ASI_INS_HIS`, `Z ASI_APR_HIS`, `AB SIT_FON_SOL`, `AC SUS_PRE`, `AE REINCORPORACION`

## Reglas fijas

- Estados permitidos: `OK` y `Pendiente`.
- Fases permitidas: `FASE 0` a `FASE 6`.
- Distribucion cerrada por fases:
  - `FASE 0`: `D`, `F`, `G`, `P`
  - `FASE 1`: `A`, `B`, `C`, `E`, `H`, `I`, `J`
  - `FASE 2`: `K`, `L`, `M`, `N`, `O`
  - `FASE 3`: `Q`, `R`, `S`, `T`, `AA`, `AD`
  - `FASE 4`: `U`, `V`, `W`, `X`, `Y`, `Z`
  - `FASE 5`: `AB`, `AC`, `AE`, `AF`
  - `FASE 6`: gate final
- Columnas actualmente en `OK` (27): `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `I`, `J`, `K`, `L`, `M`, `N`, `O`, `P`, `Q`, `R`, `S`, `T`, `U`, `V`, `W`, `X`, `AA`, `AD`, `AF`.
- Columnas actualmente en `Pendiente` (5): `Y`, `Z`, `AB`, `AC`, `AE`.
- Invariantes no negociables:
  - CSV final sin header
  - 32 columnas exactas
  - separador `;`
  - `SEXO` valido
  - `FOR_ING_ACT = 1`
  - exclusion de `PRIMERA_OPCION`

## Artefactos

- `tablero_mu_2026.tsv`: tablero maestro por columna.
- `baseline_mu_2026.json`: baseline operacional e invariantes.
- `reportes/ejecucion_oficial_mu_2026.md`: comando oficial congelado de ejecución.
- `reportes/validacion_oficial_mu_2026.md`: comando oficial congelado de validación final.
- `reportes/resultado_corrida_referencia_mu_2026.md`: evidencia de corrida de referencia.
- `evidencias/`: plantilla reusable y un archivo por columna.
- `pendientes/backlog_residual_mu_2026.tsv`: backlog residual ejecutivo vigente.
- `gate/gate_final_mu_2026.md`: gate final de liberacion documental.
- `archive/control_historico/`: guias de fase y plantillas legacy movidas fuera del camino operativo principal.

## Regla de uso

1. Ejecutar desde la raíz del repo usando `make run-oficial`, `make validate-oficial` o `make run-and-validate-oficial`.
2. Mantener `tablero_mu_2026.tsv` en `27 OK / 5 Pendiente` salvo reapertura controlada con fuente nueva o decisión funcional/normativa explícita.
3. Conservar evidencia y gate final como insumo de auditoría.
4. Gestionar los cinco bloqueos abiertos desde `pendientes/backlog_residual_mu_2026.tsv`.
5. No mover columnas de fase, no cambiar estados cerrados y no redefinir invariantes.
