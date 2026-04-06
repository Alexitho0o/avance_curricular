# Control MU 2026

Este directorio materializa el tablero cerrado de Matricula Unificada Pregrado 2026 como capa operativa del repo.

## Estado congelado actual

- Decision vigente: `APROBADO`
- Listo para auditoria: `SI`
- Listo para carga: `SI`
- Conteo vigente del tablero: `32 OK / 0 Pendiente`
- Pendientes residuales vigentes: ninguno

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
- Columnas actualmente en `OK` (32): `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `I`, `J`, `K`, `L`, `M`, `N`, `O`, `P`, `Q`, `R`, `S`, `T`, `U`, `V`, `W`, `X`, `Y`, `Z`, `AA`, `AB`, `AC`, `AD`, `AE`, `AF`.
- Columnas actualmente en `Pendiente` (0): ninguna.
- Invariantes no negociables:
  - CSV final sin header
  - 32 columnas exactas
  - separador `;`
  - `SEXO` valido
  - `FOR_ING_ACT` derivado por motor gobernable (códigos válidos: 1, 2, 3, 4, 11; bloqueados: 5-10)
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
- `config_for_ing_act.json`: configuración gobernable del motor FOR_ING_ACT (reglas, códigos, umbrales).
- `for_ing_act_rules.tsv`: catálogo de 5 reglas con prioridad y estado (ACTIVA/BLOQUEADA).
- `for_ing_act_golden_cases.json`: 12 golden cases para tests de regresión.
- `for_ing_act_trace_long.tsv`: trazabilidad completa (1364 registros, 7 flags _DA).
- `for_ing_act_governance_report.md`: reporte de gobernanza con distribución, hallazgos y dictamen.
- `config_campos_ing.json`: configuración gobernable del motor campos ING (rangos, catálogos, mapeo PERIODO, reglas por FOR).
- `campos_ing_rules.tsv`: catálogo de 22 reglas de derivación (R_ACT, R_SEM, R_ORI_A, R_ORI_S).
- `campos_ing_golden_cases.json`: 9 golden cases para tests de regresión campos ING.
- `campos_ing_trace_long.tsv`: trazabilidad completa (1364 registros, 4 campos derivados + fuente + regla).
- `campos_ing_governance_report.md`: reporte de gobernanza campos ING con coherencia FOR×ORI y dictamen.
- `config_vig_fecha.json`: configuración gobernable del motor VIG + FECHA_MATRICULA (catálogos, mapeo ESTADOACADEMICO, validaciones).
- `vig_fecha_rules.tsv`: catálogo de 16 reglas de derivación VIG (R_VIG_01–R_VIG_11) y FECHA_MATRICULA (R_FM_01–R_FM_05).
- `vig_fecha_golden_cases.json`: 6 golden cases para tests de regresión VIG + FECHA_MATRICULA.
- `vig_fecha_trace_long.tsv`: trazabilidad completa (1364 registros, VIG + FECHA_MATRICULA + fuente + regla).
- `vig_fecha_governance_report.md`: reporte de gobernanza VIG + FECHA_MATRICULA con cruce ESTADOACADEMICO×VIG y dictamen.
- `archive/control_historico/`: guias de fase y plantillas legacy movidas fuera del camino operativo principal.

## Regla de uso

1. Ejecutar desde la raíz del repo usando `make run-oficial`, `make validate-oficial` o `make run-and-validate-oficial`.
2. Mantener `tablero_mu_2026.tsv` en `32 OK / 0 Pendiente` salvo reapertura controlada con fuente nueva o decisión funcional/normativa explícita.
3. Conservar evidencia y gate final como insumo de auditoría.
4. Gestionar los cinco bloqueos abiertos desde `pendientes/backlog_residual_mu_2026.tsv`.
5. No mover columnas de fase, no cambiar estados cerrados y no redefinir invariantes.
