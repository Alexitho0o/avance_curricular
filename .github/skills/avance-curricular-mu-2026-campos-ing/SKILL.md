---
name: avance-curricular-mu-2026-campos-ing
description: 'Analiza gobernanza de campos ING en avance_curricular. Use for motor_campos_ing, config_campos_ing, campos_ing_rules, campos_ing_trace_long, test_campos_ing, ANIO_ING_ACT, SEM_ING_ACT, ANIO_ING_ORI, o SEM_ING_ORI.'
user-invocable: false
---

# Gobernanza Campos ING

## Tags
#avance_curricular #mu_2026 #skill #campos_ing #gate_humano

## When to Use
- Review ANIO_ING_ACT, SEM_ING_ACT, ANIO_ING_ORI, or SEM_ING_ORI.
- Explain or validate field derivation behavior.
- Check consistency between FOR and ORI related rules.
- Assess whether a proposed change is low-risk.

## Sources
1. scripts/motor_campos_ing.py
2. scripts/test_campos_ing.py
3. control/config_campos_ing.json
4. control/campos_ing_rules.tsv
5. control/campos_ing_trace_long.tsv
6. control/campos_ing_golden_cases.json

## Constraints
- DO NOT infer consistency beyond configured and traceable rules.
- DO NOT treat derived values as canonical when the source path is missing or ambiguous.
- DO NOT change sensitive chronology behavior without a human gate.
- ONLY combine code, config, rules, traces, and tests.

## Procedure
1. Read config, rules, traces, and tests before summarizing behavior.
2. Separate deterministic rules from source-dependent fallbacks.
3. Identify whether the task affects chronology, FOR and ORI coherence, or output schema.
4. Recommend the narrowest validation that can confirm the behavior.
5. Escalate when the conclusion would change frozen expectations or high-risk chronology.

## Output Format
- Dictamen
- Fields inspected
- Evidence and rule path
- Validation recommended or executed
- Human gate required
