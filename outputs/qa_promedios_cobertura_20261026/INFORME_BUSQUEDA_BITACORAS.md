# Búsqueda de bitácoras para diferencias de 2026-P2/P3

**Alcance:** revisión de inventarios, documentación y respaldos históricos disponibles de avance_curricular y CARACTERIZACIÓN; contraste por identidad y CODCLI de los grupos discrepantes. Las fuentes no se modificaron.

## Fuentes localizadas

- **B:** los reportes privados `PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P2_20261015.xlsx` y `...P3...`, en `CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/`, tienen hojas `CAMBIOS_ACADEMICOS` y `TRAYECTORIA_POR_PERIODO`. P2 SHA-256 `cdf44e2e49feed5cf5bcd83e85d38ff35c556e56a6a8455bc01b6b34f31a6631`; P3 SHA-256 `e29caff998dc6de4eba69628a602a1d81df270cc3657b1b21b488bc057865685`.
- **B/C:** `CAMBIOS_ACADEMICOS` contiene seis registros en P2 y 62 en P3. Incluye año, período, jornada, sede, estado y situación, pero no fecha/hora efectiva de evento, valor previo, sección ni nota individual. No constituye una bitácora UMAS de las modificaciones investigadas.
- **C:** el código disponible `procesos/caracterizacion/caracterizacion.py`, líneas 25678–25706, construye un `df_cambios` filtrando eventos y estados de `dl`; la implementación consultada es evidencia de cómo se construye esa versión, no prueba independiente de fecha del evento ni de la versión exacta que produjo el respaldo histórico.

## Contraste con casos discrepantes

- **B/C:** de nueve expedientes con diferente sección T3, ninguno aparece en `CAMBIOS_ACADEMICOS` ni en `TRAYECTORIA_POR_PERIODO` de los reportes P2/P3 revisados. Esto no prueba ausencia de una bitácora en UMAS ni resuelve el cambio (E).
- **B/C:** de 585 expedientes con diferencias de nota T3, uno aparece en `CAMBIOS_ACADEMICOS` de P2; ninguno en esa hoja de P3. La hoja no tiene campos de nota anterior/nueva ni fecha del cambio, por lo que la coincidencia del expediente no explica su nota. En `TRAYECTORIA_POR_PERIODO` se encontraron 87 en P2 y 37 en P3; el cruce se hizo por persona y CODCLI sin exigir el mismo período de la fila, y no acredita una modificación de la nota (E).
- **B/C:** de los tres expedientes con diferencia de estado, ninguno aparece en `CAMBIOS_ACADEMICOS` de P2 o P3; uno aparece en la trayectoria de P2 y uno en la de P3. No se deduce que sean expedientes distintos ni se fecha el cambio (E). Los respaldos de Datos Alumnos y sus estados ya comparados constan en `CONTRASTE_ESTADOS_RESPALDOS_AGREGADO.json`.
- **C/E:** `CONTRASTE_CAMBIOS_TRAYECTORIA_AGREGADO.json` y `contrastar_cambios_trayectoria.py` registran las hojas revisadas y los conteos. Los tres grupos pueden solaparse; no se suman. Los identificadores se procesaron solo en memoria.

## Conclusión

**E:** no se localizó en los respaldos examinados una bitácora UMAS con identidad, expediente, valor anterior/nuevo y fecha/hora efectiva que resuelva las diferencias de sección, nota o estado. Esto es un límite de la búsqueda, no prueba de inexistencia. Para resolverlas hace falta localizar, si existe, la auditoría de eventos UMAS o un respaldo equivalente que incorpore esos campos, con cobertura y corte declarados.

**C:** se mantienen las dos fuentes, el diccionario y los denominadores. No se hizo commit ni push.
