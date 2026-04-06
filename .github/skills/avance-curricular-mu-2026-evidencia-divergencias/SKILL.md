---
name: avance-curricular-mu-2026-evidencia-divergencias
description: 'Analiza evidencia congelada, dictamen, conflictos documentales y divergencias operativas en avance_curricular. Use when comparing ejecucion_oficial_mu_2026, validacion_oficial_mu_2026, resultado_corrida_referencia_mu_2026, gate_final_mu_2026, o memoria validada del repo.'
user-invocable: false
---

# Evidencia y Divergencias MU 2026

## Tags
#avance_curricular #mu_2026 #skill #evidencia_congelada #divergencias #gate_humano

## When to Use
- Compare frozen reports against gate_final or repository memory.
- Review CONDICIONAL vs APROBADO disagreements.
- Review FOR_ING_ACT documentary conflict.
- Prepare an evidence-based dictamen without editing sources.

## Sources
1. control/reportes/ejecucion_oficial_mu_2026.md
2. control/reportes/validacion_oficial_mu_2026.md
3. control/reportes/resultado_corrida_referencia_mu_2026.md
4. control/gate/gate_final_mu_2026.md
5. README.md
6. /memories/repo/avance_curricular_fix5_recovery_note.md

## Constraints
- DO NOT pick a single truth silently when sources conflict.
- DO NOT edit frozen reports, gate files, or regulatory artifacts.
- ONLY summarize evidence, divergence, impact, and next safe action.

## Procedure
1. Read frozen reports first and extract the operating baseline.
2. Read gate_final or repository memory only after the frozen baseline is clear.
3. Build a compact table with source, claim, conflict, and impact.
4. Mark whether the conflict is documentary, operational, or governance-sensitive.
5. Require a human gate when the conflict would change the operating truth.

## Output Format
- Dictamen
- Sources compared
- Divergence
- Recommended base truth
- Human gate required
