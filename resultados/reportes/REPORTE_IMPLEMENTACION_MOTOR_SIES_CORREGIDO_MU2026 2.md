# Implementación motor SIES corregido MU2026

Generado: 2026-06-25T18:27:00

## Problema original

Se detectaron 74 ajustes de sede con candidatos no regenerados y un caso crítico independiente (`20171NETMRE016`) que conservaba `VERSION=3` sin fuente ni método pese a `PENDIENTE_GOBERNANZA`.

## Modificaciones implementadas

- Módulo central `scripts/sies_resolver.py`.
- `codigo_gobernanza_v2.py` regenera candidatos después de `AJUSTE_SEDE_GOBERNANZA`.
- `codigo_gobernanza_v2.py` aplica bloqueos antes de exportar.
- Se crea puente gobernado MU -> Extranjeros.

## Comparación histórica

`COMPARACION_HISTORICO_VS_MOTOR_CORREGIDO_MU2026.csv` conserva sin cambios los registros excepto la exclusión controlada diagnóstica de `20171NETMRE016` en la salida de control. No es rectificación oficial.

## Riesgos residuales

`20241ICRE068` permanece pendiente institucional. No se genera PES.
