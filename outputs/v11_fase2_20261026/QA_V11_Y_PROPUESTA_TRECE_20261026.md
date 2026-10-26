# QA de la candidata v11 y 13 contextos de 2025

**Alcance:** seguimiento interno IPSS de períodos académicos 2 y 3 de 2025; contraste con MU2026, oferta 2025 y respaldos de Datos Alumnos. Las bases originales y los denominadores no se alteran.

## Evaluación de los 13 contextos

- **B/C:** 13 observaciones corresponden a 8 personas y 8 expedientes. Todos muestran actividad en PROMEDIOS para el mismo plan, carrera, jornada y período observado, y un único código de la familia destino en MU2026, con ingreso actual a la carrera no posterior a 2025. Cada expediente tiene un único plan en las fuentes examinadas; no se afirma unicidad universal.
- **B/C:** los dos respaldos revisados de Datos Alumnos 2026 contienen, para los 13, el mismo CODCLI, carrera y jornada; las 8 personas tienen un único CODCLI en cada respaldo revisado. MU2026 identifica a la persona, no incluye por sí mismo el CODCLI. Esto corrobora la relación pero no demuestra una atribución directa en 2025.
- **B/C:** la fuente de oferta `Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx`, hoja `in`, SHA-256 `94d51a6752b40adb45c8eba65786ee8aad9f6667d15b3d07273a969ec4faed77`, tiene en `OFE_2025` los cuatro códigos candidatos, vigentes con estudiantes nuevos: C57J1V1 fila 54284; C57J2V1 fila 54285; C91J1V1 fila 54317; C91J2V1 fila 54318. El índice histórico registra una sola versión por esas familias para 2025. Detalle en `QA_OFERTA_TRECE_2025.json`.
- **C/E · propuesta:** estas 13 observaciones tienen evidencia comparable al criterio aplicado a las 27 anteriores y son candidatas fuertes a una correspondencia interna individual. Ese criterio fue aprobado para 27 observaciones concretas; no se extiende automáticamente a nuevas observaciones. La documentación del período, la fecha efectiva del cambio, la atribución documental y la aceptación SIES siguen pendientes. No se propone que una asignación interna declare retención o vigencia.
- **E:** para una atribución documental del trimestre falta una fuente individual de 2025 que relacione la persona y su expediente con carrera, sede, jornada y versión, o un registro equivalente. La evidencia posterior no acredita por sí sola su existencia o fecha efectiva en 2025.

## Controles de la candidata

- **C:** consultas del servicio comparadas contra la candidata anterior: 25.900; 25.827 sin cambios y 73 con cambio E→D, correspondientes exactamente a la decisión CO aprobada; sin errores de consulta. Los 73 se limitan a la candidata no activa. Ver `QA_CANDIDATA_73_EXHAUSTIVO.json`.
- **C:** integridad SQLite y equivalencia de dimensiones y filas MU anual verificadas; 12 pruebas unitarias pasaron. Tres consumidores coincidieron en tres consultas representativas; no es una comparación exhaustiva de todos los consumidores.
- **C:** partición del índice de posiciones: 1.126 con contexto incorporado + 81 con actividad sin incorporación + 2.286 sin actividad localizada en fuentes leídas + 27 documentos P sin puente = 3.520 posiciones. No son personas distintas; actividad no es vigencia ni ausencia es deserción. La cobertura incompleta de PROMEDIOS 2026 permanece como limitación.
- **E/C · bloqueo de activación:** las dos alternativas excluidas de una misma llave en 2025 son TENS, RE, jornadas 1 y 2. La consulta de la candidata responde `CONTEXTO_NO_LOCALIZADO`, pues ninguna alternativa fue indexada. Ese resultado no comunica la ambigüedad real. Debe conservarse y mostrarse como ambigüedad antes de considerar completo el QA de activación; no escoger una alternativa ni presentar ausencia como hecho.
- **E:** además de esos dos contextos, existen excepciones de familia y de enlace T1 no resueltas; son estados de evidencia pendientes y no deben desaparecer de la cobertura. QA de activación: **BLOQUEADO**, no PASS completo. La candidata permanece no activa y el puntero sigue en v10.

Los resultados completos por contexto y sus identificadores están solo en `~/.local/share/ipss/v11_fase2_20261026/`; los archivos de este directorio de salida contienen agregados, códigos o scripts sin identificadores. Sin commit ni push en esta revisión.
