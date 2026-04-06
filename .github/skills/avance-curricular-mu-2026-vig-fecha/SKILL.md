---
name: avance-curricular-mu-2026-vig-fecha
description: 'Analiza gobernanza de VIG y FECHA_MATRICULA en avance_curricular. Use for motor_vig_fecha, config_vig_fecha, vig_fecha_rules, vig_fecha_trace_long, test_vig_fecha, VIG, o FECHA_MATRICULA.'
user-invocable: false
---

# Gobernanza VIG y FECHA_MATRICULA

## Tags
#avance_curricular #mu_2026 #skill #vig #fecha_matricula #gate_humano

## When to Use
- Review VIG and FECHA_MATRICULA rules.
- Explain or validate behavior tied to ESTADOACADEMICO or exclusion logic.
- Assess whether a proposed change is safe.
- Check traceability or tests for this domain.

## Sources
1. scripts/motor_vig_fecha.py
2. scripts/test_vig_fecha.py
3. control/config_vig_fecha.json
4. control/vig_fecha_rules.tsv
5. control/vig_fecha_trace_long.tsv
6. control/vig_fecha_golden_cases.json

## Constraints
- DO NOT reinterpret frozen operating truth without surfacing evidence and residual risk.
- DO NOT bypass state-based validation for VIG.
- DO NOT change exclusion-sensitive logic without a human gate.
- ONLY combine code, config, rules, traces, and tests.

## Procedure
1. Read config, rules, traces, and tests before drawing conclusions.
2. Separate state-driven rules from default or fallback behavior.
3. Identify whether the task affects VIG, FECHA_MATRICULA, exclusion logic, or output safety.
4. Recommend the smallest validation that can confirm the claim.
5. Escalate when the conclusion would affect frozen operating expectations.

## Output Format
- Dictamen
- Fields inspected
- Evidence and rule path
- Validation recommended or executed
- Human gate required
