# V11 · Revisión de respaldos históricos de excepciones

**C/E · Estado:** revisión ejecutada con pendientes; v11 candidata no se activa. Se revisaron 100 contextos distintos: 25 diferencias de familia, ocho sin coincidencia T1 completa y 73 CO; seis de los ocho también pertenecen a los 25. Se mantienen separados contexto, persona y expediente.

## 25 diferencias y ocho sin coincidencia T1 completa

- **B/C:** las 25 diferencias comprenden 19 cambios observados de jornada y seis de carrera respecto de la familia T1, 16 personas. En el índice MU anual la familia destino aparece posteriormente para la misma persona en 13 contextos; esto no adjudica automáticamente el código por CODCLI o al periodo anterior.
- **B/C:** en cinco contextos de 2026 (tres personas/expedientes), la jornada de destino no coincide con la observada en DATOSDEALUMNOS 10246, pero sí con 11998. Se trata de tres contextos con periodo nativo 2 y dos con periodo 3. Los respaldos acotan una diferencia entre extracciones; no se ha acreditado fecha efectiva ni corte exacto de cada estado. No extrapolar la jornada posterior al periodo 2.
- **B/C:** de los ocho sin coincidencia T1 completa, los seis contextos con familia diferente siguen siendo excepciones de carrera; dos conservan familia. En el DA 12159 el año de ingreso coincide con el año de origen de la vista, pero no demuestra el código del expediente en T1. Los listados trimestrales son parciales y la ausencia en ellos no acredita ausencia o deserción.
- **E:** faltan respaldo del evento o relación CODCLI/plan con código SIES por periodo para adjudicar el cambio. Estas verificaciones no modifican códigos ni activan una regla de herencia.

## Concepción

- **B/C:** los 73 contextos corresponden a 51 personas/expedientes: 41 COTEIQ, 21 COTFAR y 11 COTENS. En ambas extracciones históricas 10246 y 11998 se encuentra el mismo RUT y CODCLI con sede CO, carrera y jornada concordantes. Las cifras son contextos, no matrículas únicas.
- **B:** en la MU anual del año T1 indexada por persona, los 73 tienen un único código para esa persona y año; son respectivamente `I162S3C114J2V1`, `I162S3C115J2V1` e `I162S3C91J2V1`. Esta observación confirma V1 en la evidencia anual para esas personas.
- **D/E:** Alexi aprobó las familias CO para uso interno. No se ha demostrado que MU por RUT y año atribuya por sí sola cada código al CODCLI/plan en el periodo de destino, ni que la fecha exacta de la sede sea la del corte T2/T3. Por ello la candidata conserva el código destino sin adjudicar; se necesitan enlaces documentales o una decisión aprobada con alcance y evidencia específicos para cerrar esas asignaciones.

## Fuentes, control y privacidad

- **B/C:** datos alumnos 10246, hoja Hoja1, SHA-256 `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869`; datos alumnos 11998, hoja Hoja1, SHA-256 `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`. Los nombres de los respaldos y sus rutas no prueban el corte exacto de cada estado.
- **C:** los seis respaldos y sus hashes completos, hojas y conteos están en `QA_RESPALDOS_HISTORICOS_AGREGADO.json`, SHA-256 `efb00db01a6e02b12de55de26d20e59f5efdc7447ee6ae0cf1e46ad4d4a3fa45`; script `qa_respaldos_historicos.py`, SHA-256 `2ddf93d937a2255188712cdc8e21f5b8e025be743ea8c59d01138fb79ff1f30b`.
- **C:** detalle individual y referencias fuente/hoja/fila permanecen en `/Users/alexi/.local/share/ipss/v11_fase2_20261026/QA_RESPALDOS_HISTORICOS_DETALLE.json`, SHA-256 `c92d2d32c5f3896f85432727bfe002e262f877bb773b9cba91632ee30c804fcc`.
- **E:** revisión completada dentro del alcance de los respaldos disponibles, con atribución individual y temporal pendiente. No se modifica v10, v11, fuentes ni denominadores; no se hace commit ni push.
