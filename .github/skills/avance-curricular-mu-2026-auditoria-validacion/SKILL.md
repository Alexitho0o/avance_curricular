---
name: avance-curricular-mu-2026-auditoria-validacion
description: 'Audita y valida MU 2026 en avance_curricular. Use for auditoria_maestra, qa_checks, validate-oficial, invariantes, gating, o validacion barata antes de rerun.'
user-invocable: false
---

# Auditoria y Validacion MU 2026

## Tags
#avance_curricular #mu_2026 #skill #auditoria #validacion

## When to Use
- Review auditoria_maestra and qa_checks behavior.
- Choose the cheapest safe validation path.
- Validate outputs that already exist before any rerun.
- Summarize what was validated, what was not, and what remains blocked.

## Sources
1. scripts/auditoria_maestra.py
2. qa_checks.py
3. Makefile
4. scripts/run_oficial.sh
5. scripts/validate_oficial.sh
6. control/reportes/ejecucion_oficial_mu_2026.md
7. control/reportes/validacion_oficial_mu_2026.md
8. control/reportes/resultado_corrida_referencia_mu_2026.md

## Constraints
- DO NOT rerun the full pipeline when existing outputs and a cheaper validation path are enough.
- DO NOT treat gate_final as stronger than frozen reports without surfacing the conflict.
- ONLY choose the narrowest meaningful validation first.

## Procedure
1. Determine whether outputs already exist or whether the task is purely structural.
2. Pick the cheapest safe validation path.
3. If the task touches runtime or a specialized domain, recommend targeted tests first.
4. Record validated and not-validated areas separately.
5. Surface any divergence that affects the dictamen.

## Output Format
- Dictamen
- Validation path chosen
- Evidence checked
- Residual risk
- Next safe action
