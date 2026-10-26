# V11 · Fase 2 · Índice y candidata para revisión

**C — Estado:** candidata privada no activa; QA parcial. El puntero activo continúa en v10. No se modificaron fuentes, bases originales ni denominadores.

## Alcance y resultados

- **B/C:** se revisaron las 3.520 posiciones sin contexto de la vista T1–T2–T3. Se detectó actividad de cualquier carrera en el mismo identificador, año y período en 1.207 posiciones. Actividad no equivale a vigencia ni retención.
- **B/C/E:** se encontraron contextos candidatos dentro de las 32 combinaciones aprobadas y las tres familias CO para 1.127 posiciones. La agrupación produjo 1.128 contextos únicos; dos quedaron fuera de la candidata por compartir una llave sin dimensiones con más de un contexto. No son cierres de versión.
- **C/E:** se agregaron 1.126 contextos pendientes a una copia de v10; corresponden a 1.126 posiciones y 638 personas en la vista. Por período nativo: 2025-2: 181; 2025-3: 155; 2026-2: 369; 2026-3: 421. No se ha acreditado el vínculo de cada nuevo CODCLI con el expediente de origen T1 ni la equivalencia de período nativo con corte administrativo.
- **C/E:** 2.394 de las 3.520 posiciones no recibieron un contexto nuevo en esta candidata. Eso no significa ausencia académica ni deserción. Se excluyeron del cruce de RUT los 27 documentos P sin puente específico; no se imputó DV. Pueden existir posiciones con actividad no incorporada por el alcance o conflictos.
- **C/E:** partición preliminar de las 3.520: 1.126 con contexto incorporado; 81 con actividad en el período pero sin contexto incorporado; 2.286 con documento R sin actividad encontrada en las fuentes leídas; 27 con documento P no cruzado. El grupo sin actividad encontrada depende de la cobertura de las fuentes y no prueba que no exista actividad.
- **B/C:** 73 de los 1.126 contextos nuevos tienen sede CO observada actualmente; no se les asignó código ni se extrapoló sede o versión al pasado. Los restantes 1.053 muestran RE actual. La sede DA del corte 12159 no confirma automáticamente sede histórica.
- **E:** los archivos 12166 y 3233 están limitados a 70.000 filas; la cobertura 2026-2/3 sigue incompleta o no certificada. Solicitar extracción completa es un paso futuro, no inferir personas ausentes.

## Datos y archivos

- **B:** `RESULTADOS_INDICE.json` registra hashes de PROMEDIOS 7804, 12166 y 3233, DATOSDEALUMNOS 12159 y la vista de origen. Hojas `Hoja1`; en PROMEDIOS se emplearon RUT, DIG, CODCLI, CODCARR, PLAN_DE_ESTUDIO, ANO, PERIODO y JORNADA. En DA se usaron RUT, CODCLI y SEDE para la sede actual y control de identidad.
- **C:** `construir_indice.py` conserva evidencia fuente/hoja implícita Hoja1 y filas en índice privado. Los detalles se guardaron en `/Users/alexi/.local/share/ipss/v11_fase2_20261026/`, directorio fuera de Git con permisos restringidos.
- **C:** candidata SQLite `DICCIONARIO_SIES_CANDIDATO_V11.sqlite`, SHA-256 `2df964de1fbb50be8a062708ee689667be1a33afd72d700bcc5792b940bf8423`. `DESCRIPTOR_CANDIDATA.json` apunta a ella, no al puntero activo.

## QA y pendientes antes de activar

- **C:** integridad SQLite OK; las 24.774 consultas de v10 comparadas con dimensiones y también sin dimensiones no cambiaron; las 1.126 consultas nuevas devuelven E sin código. Conteo MU anual 12.207 en ambas bases. El servicio activo v10 pasó 12 pruebas unitarias.
- **C:** los tres consumidores produjeron respuestas iguales para una consulta antigua y una nueva en un entorno aislado privado con la candidata, sin cambiar el puntero activo. Es una prueba acotada, no un contraste exhaustivo de los consumidores.
- **E:** falta verificar de forma independiente el contenido y la atribución de las nuevas observaciones, revisar dos llaves ambiguas, y conciliar personas/expedientes del universo ampliado. El QA es parcial, no autoriza activar v11.
- **E:** revisar el tratamiento de las familias CO aprobadas en sus 73 contextos sin convertir sede actual en sede histórica, y reconciliar los motivos de las posiciones no incorporadas.
- **C:** archivos de esta carpeta son agregados o código. No se hizo commit ni push de la fase 2.

## QA adicional · atribución T1, llaves y universo

- **B/C:** en la MU anual indexada se encuentra el código T1 de la persona en los 1.126 contextos. Esa coincidencia es por persona y año; no demuestra por sí sola que el código corresponda al CODCLI de destino.
- **B/C:** 1.118 contextos tienen en PROMEDIOS del período nativo 1 del año de origen el mismo CODCLI, plan, carrera y jornada que en el contexto nuevo; ocho no fueron localizados con esas dimensiones. Esta evidencia no acredita el momento administrativo de un cambio ni asigna automáticamente una versión SIES.
- **B/C:** la familia del código T1 está entre las familias candidatas en 1.101 contextos; en 25 es distinta o no atribuible. Una coincidencia de familia no acredita la versión individual del período de destino.
- **B/C/E:** las dos observaciones excluidas comparten una misma llave persona/CODCLI/plan/año/período, pero son Técnico en Enfermería, sede RE, jornadas 1 y 2, en 2025-período nativo 2, con familias I162S2C91J1 e I162S2C91J2. No se elige ninguna sin evidencia del contexto o fecha del cambio.
- **C:** la primera ejecución del control reportó 190 supuestas discordancias de identidad. El verificador trataba el dígito 0 como vacío; tras corregirlo y conservar el primer resultado para auditoría, se verificaron 4.329 referencias de fila, sin diferencias. No se modificó ninguna fuente ni la candidata.
- **C:** v10: 5.901 personas y 6.622 expedientes con grano persona/CODCLI/carrera. V11 candidata: 6.523 personas y 7.263 expedientes con el mismo grano. Son 622 personas y 641 expedientes nuevos; las 1.126 observaciones se distribuyen entre 638 personas, de las que 16 ya estaban en v10. Con grano persona/CODCLI, los expedientes son 6.621 y 7.262 respectivamente; no mezclar ambos granos.
- **E:** las comprobaciones de filas y continuidad observada no prueban automáticamente el código de cada CODCLI en T1 ni la versión en T2/T3. La candidata permanece no activa, con los nuevos registros en E; revisar las 25 diferencias de familia, los ocho casos sin coincidencia T1 completa y los 73 con CO actual. Los resultados agregados y el detalle privado están identificados por hash en `QA_ATRIBUCION_T1_AGREGADO_V3.json` y el directorio privado.
- **C:** QA agregado V3 SHA-256 `3659bcbc2a6bd6cffa94420958bab35a71bfafeaebe989a328a64c89a956bc39`; detalle privado V3 SHA-256 `656c4e93e2d1268b62c90f9c850d73dd7015d22b566ac9de6aaffac61b62eb01`; script SHA-256 `a416a87bde47360138dfa17888263cecc347c76964675b3a91f3684d4b17e7f8`.
