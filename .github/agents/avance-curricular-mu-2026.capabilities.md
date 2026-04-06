# Avance Curricular MU 2026 Operator Guide

## Tags
#avance_curricular #mu_2026 #operator_guide #quick_reference

## Donde mirar
- Routing, limites operativos y gates humanos: .github/agents/avance-curricular-mu-2026.agent.md
- Estado estructurado, skills activas, dominios centralizados, no-touch, conflictos y validacion: .github/agents/avance-curricular-mu-2026.config.json
- Esta guia solo resume uso, alcance y limites de la capa actual.

## Cobertura actual
- Hay cobertura separada para divergencias documentales, auditoria y validacion, FOR_ING_ACT, campos ING, y VIG con FECHA_MATRICULA.
- Lo sensible, incierto o no particionado sigue centralizado; el listado canonico vive en domain_status de config.json.

## Piloto Fase 5
- Auditoria y validacion tiene un mini-agente piloto minimo: .github/agents/avance-curricular-mu-2026-auditoria-validacion.agent.md
- Su valor es aislar contexto, fijar un contrato de salida y elegir fallback seguro cuando la validacion barata oficial escribe artefactos.
- Si el piloto no aplica o no aporta, el fallback canonico sigue siendo la skill de auditoria y validacion.

## Estado base
- Base operativa actual: CONDICIONAL, listo para auditoria y no listo para carga.
- El detalle canonico vive en operating_baseline.frozen_state de config.json.

## Alertas activas
- known_conflicts en config.json es la fuente principal.
- Hoy las alertas activas son FOR_ING_ACT y gate_final vs reportes congelados.

## Limites rapidos
- No crea mini-agentes persistentes ni memoria localizada canonica.
- No expande dominios inciertos en esta fase.
- No toca runtime productivo ni artefactos congelados sin gate humano.

## Uso recomendado
- Entra por el orquestador.
- Usa una skill solo si aparece habilitada en config.json y el dominio ya esta separado.
- Valida con la estrategia mas barata de config.json antes de cualquier rerun.
- Si cambia la verdad operativa o hay evidencia en conflicto, detente y eleva gate humano.
