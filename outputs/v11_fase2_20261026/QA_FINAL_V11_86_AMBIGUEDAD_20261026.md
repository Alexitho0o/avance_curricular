# QA de candidata v11 · 86 decisiones internas y jornadas ambiguas

**Alcance:** conciliación IPSS–SIES–UMAS, observaciones T2/T3 2025 y 2026; QA de consultas y trazabilidad de una candidata local, sin modificación de bases originales ni denominadores.

## Decisiones y evidencia

- **D:** Alexi aprobó las 73 correspondencias internas CO V1 y luego las 13 correspondencias de 2025. Las 13 son específicas, no extienden automáticamente la regla a otros expedientes; la atribución documental de 2025 sigue pendiente (E). `DECISION_73_CO_V1_20261026.md`, `DECISION_13_2025_Y_AMBIGUEDAD.md`.
- **B/C:** 13 contextos, ocho personas y ocho expedientes: C91J1V1 dos, C91J2V1 cinco, C57J1V1 dos y C57J2V1 cuatro. El respaldo y los controles están en `QA_TRECE_CRITERIO_V10.json` y `QA_OFERTA_TRECE_2025.json`.
- **C/E:** los dos contextos TENS RE 2025 período nativo 2 se incorporan como alternativas sin adjudicación, jornada 1 y jornada 2. Sin jornada la consulta responde `CONTEXTO_MULTIPLE` con dos evidencias; con jornada devuelve la alternativa consultada en E sin código. El problema `CONTEXTO_NO_LOCALIZADO` queda corregido en esta candidata. Las 11 referencias de las alternativas en tres archivos PROMEDIOS fueron comprobadas; no prueban vigencia al cierre ni fecha de cambio. `QA_FUENTES_JORNADAS_AMBIGUAS.json`.

## Controles

- **C:** comparación de 25.900 consultas anteriores con dimensiones y 25.900 sin dimensiones: exactamente 13 cambios E→D autorizados en cada modalidad, ningún cambio adicional y cero errores. Se prueban la ambigüedad sin jornada y ambas consultas con jornada. `QA_V11_86_REGRESION.json`.
- **C:** integridad SQLite correcta; 25.900 filas previas conservan dimensiones y solo los 13 payloads autorizados cambian; 12.207 filas MU anual permanecen idénticas. Se agregan dos alternativas, llegando a 25.902 observaciones. Las candidatas y fuentes anteriores conservan su hash. `QA_CANDIDATA_86_Y_AMBIGUEDAD.json`.
- **C:** 12 pruebas unitarias correctas; tres consumidores coinciden en cinco consultas representativas cada uno, en entorno aislado. No se compararon exhaustivamente las 25.902 consultas a través de cada consumidor.
- **B/C:** el universo candidato tiene 6.524 personas y 7.264 expedientes con grano persona/CODCLI/carrera. Por observación, 21.569 tienen código documental atribuible, 298 solo correspondencia interna y 4.035 siguen pendientes. Son conteos del diccionario, no denominadores ni tasas de retención.
- **C:** de las 3.520 posiciones inicialmente sin contexto, 1.127 tienen al menos un contexto candidato ahora visible; una posición nueva muestra dos alternativas. Hay 80 con actividad y sin contexto incorporado, 2.286 sin actividad encontrada en fuentes revisadas y 27 de documento P sin puente. 1.127 + 80 + 2.286 + 27 = 3.520. La presencia de contexto no demuestra retención.

**Estado: QA funcional PASS CON ALCANCE.** Las verificaciones descritas pasan en la candidata, incluida la excepción de jornada. **E:** no se certifica integridad de las fuentes PROMEDIOS truncadas, atribución documental de los 86 cierres internos, aceptación SIES por trimestre, vigencia histórica, ni se resuelven otras excepciones o las dos jornadas. Esos son pendientes de evidencia y no se convierten en cero o en deserción.

**C:** el puntero activo sigue en v10; la candidata no se activó, ni se realizó commit o push. Candidata privada SHA-256 `1dafb1486f3ebd080ad4435a3af80b65a1a7016ba47b51f30d91b9a050985141`; descriptor SHA-256 `0818890e4365834615cb8bcfdf8c6e6c765439bf322339628509f70a52d630af`. Detalles individuales y SQLite solo bajo `~/.local/share/ipss/v11_fase2_20261026/`.
