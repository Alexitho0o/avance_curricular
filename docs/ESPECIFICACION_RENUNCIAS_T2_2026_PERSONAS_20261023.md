# Renuncias T2-2026: búsqueda y escenario por personas

Proceso: seguimiento interno de retención intertrimestral IPSS162, ingreso2026/P2.
Solicitud: localizar el detalle individual de las66 renuncias y calcular un escenario
por personas sin sustituir bases, denominadores ni la V16 vigente.

- B: releer el T2 congelado, sus hojas y caché de tabla dinámica; contrastar por
  CODCLI exacto con los respaldos gobernados10246,11998 y12159. Validar RUT en los
  cruces; conservar matrículas y personas como unidades distintas.
- C: conciliar estados/situaciones por carrera y total. La igualdad de un total no
  acredita pertenencia a una nómina. No usar nombre ni cruces aproximados.
- E: no convertir ausencia, cambio de carrera o suspensión en renuncia, ni
  trasladar estados de otra fecha al resumen de66. Si no hay nómina atribuible,
  declarar la tasa por personas pendiente y calcular únicamente sus alternativas
  matemáticas condicionadas al tratamiento de la matrícula duplicada.
- D: conservar V16, fuentes y denominadores actuales. No hacer commit/push.

Salidas: informe, evidencia agregada, QA y manifiesto, sin identificadores. El script
usa identificadores solo en memoria. Se mantienen `scripts/` y `outputs/` por la
convención operativa existente del subproyecto; no se ejecuta el motor anual.
QA: hashes antes/después; control528/527/66/462; cardinalidad de las uniones;
conciliación de todos los estados; control de diferencias por carrera y verificación
independiente del rango por personas. Los escenarios no son tasas confirmadas.
