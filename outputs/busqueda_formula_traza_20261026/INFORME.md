# Búsqueda de la fórmula de titulación y respaldos · 26-10-2026

## Libro con la traza

**[B/C]** Se inspeccionó `Res_Tit_Unificada` en la copia legible de la captura de titulación, SHA-256 `149367ca3f7be7717f958e2ce0f8924e18353e6302766b1abf737c54b5dce8e3`. Para los cuatro casos se revisaron 28 columnas `TRACE_` por fila: 100 celdas tienen valores y 12 están vacías; ninguna es fórmula. `TRACE_SCORE_CANDIDATO` y `TRACE_REASONS_CANDIDATO` son valores en las cuatro filas. No se encontraron VBA, `xl/connections.xml` ni enlaces externos en el paquete del libro.

**[C/E]** Se buscó literalmente `TRACE_SCORE_CANDIDATO` en código y documentación de todos los commits locales de avance_curricular y CARACTERIZACIÓN, y `TRACE_REASONS_CANDIDATO` en archivos técnicos accesibles de esos repositorios y la carpeta institucional de Titulación Unificada. No se localizó el generador en ese alcance. Esto no demuestra que no exista en otro respaldo ni descarta una fórmula que use otros nombres. Las razones observadas y el puntaje 2130 quedaron documentados en el informe anterior; no permiten reconstruir los pesos.

## Reportes de carga

**[B/C]** Se leyeron 16 archivos `.txt` de `Titulación Unificada/2026/errores en las subidas`, verificando sus hashes y sin exportar el texto. No se encontró ninguna de las cuatro identidades mediante búsqueda literal de cuerpo de RUT y DV; tampoco se identificaron menciones literales a sus CODCLI, los cuatro códigos de plan ni los 21 códigos de ramo. La búsqueda es acotada a esos reportes y patrones; no acredita ausencia de una bitácora u homologación en otro formato o fuente **[E]**.

## Copias del respaldo ampliado

**[B/C]** Se verificaron las dos copias `PROMEDIOSDEALUMNOS_7804.xlsx` y `PROMEDIOSDEALUMNOS_7804_001.xlsx` en el respaldo P3: ambas tienen SHA-256 `78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71`. Las dos copias `DATOSDEALUMNOS_11998.xlsx` y `_001.xlsx` también son idénticas entre sí, SHA-256 `5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35`. Sus sufijos no constituyen nuevas fuentes. Para los 21 ramos se mantiene la comparación de 33 llaves y 12 diferencias de `CONVALIDADO` ya documentada.

## Pendientes y conservación

**[E]** No se localizó en esta revisión la fórmula de selección, un vínculo formal título–CODCLI–plan para los cuatro casos ni nuevas actas de homologación de los 21 ramos. Siguen visibles las evidencias individuales de reconocimiento ya observadas en PROMEDIOS, sin generalizarlas. El detalle de fuentes, hashes y resultados de búsqueda está en `RESULTADO_AGREGADO.json`.

`inspeccionar.py` hace las comprobaciones sin escribir las fuentes ni exportar identificadores o textos personales. No se cambiaron las bases, diccionario, tasas ni denominadores. Sin commit ni push.
