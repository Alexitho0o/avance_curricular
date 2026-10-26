# V11 · QA de diferencias de familia, T1 y Concepción

**C — Alcance:** lectura de 100 contextos distintos de la candidata: 25 con diferencia de familia, ocho sin coincidencia completa T1 y 73 con sede CO actual. Los grupos se solapan: seis de los ocho están entre las 25 diferencias; las otras dos no. Ninguno de los 73 CO pertenece a los otros grupos en este alcance. No son 106 contextos independientes.

## Diferencias de familia

- **B/C:** de 25 contextos, 19 muestran diferencias de jornada y seis diferencias de carrera al comparar componentes de familia. Por carrera destino: TENS 12, TPAS 8, CONG 4, TRHU 1. Son 16 personas, no 25 personas.
- **B/C:** en 13 contextos la familia destino aparece para la persona en una MU posterior al año de origen; en los 25 no aparece como familia destino de esa persona en la MU del año T1 consultada. La MU indexada es por persona/año, no asignación automática al CODCLI o a T2/T3.
- **E:** no se concluye fecha del cambio ni se adjudica versión. Es necesario respaldar expediente y periodo con el dato histórico aplicable y revisar que la fuente posterior no se extrapole hacia atrás.

## Ocho sin coincidencia T1 completa

- **B/C:** ocho contextos corresponden a seis personas: TENS 2, CONG 4, TEIQ 1 y TRHU 1. Seis coinciden con diferencias de carrera y dos conservan la familia; no se encontró una coincidencia T1 completa de CODCLI/plan/carrera/jornada en PROMEDIOS bajo el año de origen y periodo nativo 1 revisados.
- **B/C/E:** en los ocho, DATOSDEALUMNOS 12159 registra un año de ingreso igual al año T1 del origen. Es evidencia del corte actual, no prueba de que ese expediente tuviera el código SIES de T1 ni de la fecha de cambio. Buscar respaldo histórico específico si se pretende cerrar la atribución.

## 73 contextos CO

- **B/C:** 41 COTEIQ, 21 COTFAR y 11 COTENS; son 51 personas y 51 expedientes persona/CODCLI. Los tres conteos son de contextos, no de matrícula.
- **B/C:** en los 73, DA del corte revisado vincula la misma persona y CODCLI con CO, y la MU anual de origen contiene para esa persona la familia candidata. Dentro de ese índice no aparecen otros códigos para la misma persona y año de origen de estos 73 contextos.
- **D/E:** las tres familias están aprobadas como candidatas internas, no como atribuciones personales automáticas. La coincidencia anual por persona y la sede actual no acreditan por sí mismas CODCLI/versión/sede histórica en cada T2/T3; se mantienen pendientes los controles de atribución y las excepciones previas.

## QA y trazabilidad

- **C:** se verificaron hashes de las tres fuentes PROMEDIOS, DA, vista, v10 y candidata v11. La revisión usa fuentes de actividad por CODCLI/identidad, MU anual por persona/año y DA por persona/CODCLI. Se conserva el detalle privado con fuente/hoja/fila, sin modificar bases o denominadores.
- **C:** resultado agregado V2 `QA_EXCEPCIONES_T1_AGREGADO_20261026_V2.json`, SHA-256 `1318f4cb1c5ab1150a74893221a41fe70a3b8d5e571b842985cd4748225bd271`. Script `revisar_excepciones_t1.py`, SHA-256 `c12c78a291aee6a56907525a2deae9529c19fe9504e61c8d62efdb6979acb125`. Detalle privado `QA_EXCEPCIONES_T1_DETALLE_20261026_V2.json`, SHA-256 `385a96ef7689d4b16229042eb4ffc1f5f1c7c2d11ff23953eb0255906437927a`.
- **E:** QA revisado con pendientes, no PASS integral ni autorización para activar v11. Las otras 2.394 posiciones sin incorporación de la vista requieren tratamiento separado; la cobertura PROMEDIOS es limitada. No se hizo commit ni push.
