---
name: avance-curricular-mu-2026-for-ing-act
description: 'Analiza gobernanza FOR_ING_ACT en avance_curricular. Use for motor_for_ing_act, config_for_ing_act, for_ing_act_rules, for_ing_act_trace_long, test_for_ing_act, conflicto FOR_ING_ACT, o via de ingreso MU 2026.'
user-invocable: false
---

# Gobernanza FOR_ING_ACT

## Tags
#avance_curricular #mu_2026 #skill #for_ing_act #gate_humano

## When to Use
- Review FOR_ING_ACT logic, traces, rules, or tests.
- Explain or validate FOR_ING_ACT behavior.
- Compare frozen truth against BUG-004 remediation evidence.
- Assess whether a proposed change is safe.

## Sources
1. scripts/motor_for_ing_act.py
2. scripts/test_for_ing_act.py
3. control/config_for_ing_act.json
4. control/for_ing_act_rules.tsv
5. control/for_ing_act_trace_long.tsv
6. control/reportes/ejecucion_oficial_mu_2026.md
7. control/reportes/validacion_oficial_mu_2026.md
8. /memories/repo/avance_curricular_fix5_recovery_note.md

## Constraints
- DO NOT collapse the FOR_ING_ACT conflict into a single truth silently.
- DO NOT treat code 4 as enabled unless a new validated source exists.
- DO NOT change runtime truth without a human gate.
- ONLY use traces, rules, config, tests, and frozen evidence together.

## Procedure
1. Read config, rules, trace, and tests before drawing conclusions.
2. Separate frozen operating truth from validated remediation evidence.
3. Identify whether the task is documentary, behavioral, or regression-sensitive.
4. Recommend the smallest validation that can confirm the claim.
5. Escalate to a human gate if the conclusion would change operating truth.

## Output Format
- Dictamen
- Rule or path inspected
- Evidence and conflict status
- Validation recommended or executed
- Human gate required
