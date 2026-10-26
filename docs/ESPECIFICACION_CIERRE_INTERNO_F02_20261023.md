# Cierre interno dirigido F02 — 2026-10-23

Proceso: conciliación histórica UMAS–SIES, retención IPSS162. Referencia: 2024.

Decisión D autorizada por Alexi en este chat: cerrar internamente como
I162S2C1J4V2 la observación IECIREOL20211, período 2 bimestral, de F02.
Revisar además las tres observaciones IINF20241 de 2024, sin extender esta
autorización a una equivalencia general de plan, a envío SIES ni a otras personas.

Implementación C: registrar una adjudicación versionada local, enlazada por
observacion_id exclusivamente en almacenamiento privado fuera de Git. Aplicarla
en memoria al diagnóstico de 24.774 observaciones para verificar su efecto.
Conservar intactos los archivos anteriores, fuentes, motor anual, bases, libros,
tasas y denominadores. No modificar códigos documentales.

Revisión B/C de IINF: consultar oferta 2024, equivalencias operativas 2026,
equivalencias manuales, observaciones individuales ya conciliadas, cronología
F02 y respaldo T3. No extrapolar 2026 a 2024, ni convertir mayoría de plan en
equivalencia individual. Comprobar contra la base MU las versiones observadas
en el mismo plan/contexto. Conservar pendientes E cuando no se acredite enlace.

Salidas: informe, decisión, resultados, QA y manifiesto sin identificadores en
outputs/cierre_interno_f02_<timestamp> (continuidad justificada de diagnósticos
previos); adjudicación y observaciones F02 en ~/.local/share/ipss/. Script en
scripts/ por continuidad del flujo existente. Sin commit/push ni publicación.

QA: hashes de entradas, identidad de observaciones, modificación interna de una
sola observación autorizada, invariancia documental, denominadores, referencias
MU releídas, privacidad y Git antes/después. No declarar resuelto F02 si conserva
observaciones pendientes. Fecha exacta administrativa separada de versión por
período; su ausencia no invalida por sí sola un cierre interno respaldado.
