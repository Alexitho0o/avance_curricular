# Búsqueda de desempate y vínculo del título · 26-10-2026

**[B/C] Alcance.** Titulación Unificada 2026, título observado en 2025: caso anteriormente identificado con dos expedientes de la misma familia de carrera. Se contrastaron el libro de captura guardado en Teams, una copia de captura en la carpeta institucional de Titulación, el libro de carga de la misma carpeta y el CSV allí disponible. Se usó el documento y su DV en memoria. Esto no constituye una verificación de recepción o aceptación por SIES **[E]**.

| Fuente [B] | SHA-256 | Resultado [B/C] |
|---|---|---|
| Captura de Teams `1668382...xlsx` | `1f4866a53d254d329dc2a1a85eaab135458a8963a11333de6b2cea9871bf9b2c` | `Res_Tit_Unificada` registra el candidato, puntaje y razones. |
| Captura de Titulación `16683-82...xlsx` | `edef1e2574884fbd5f1bbc7f820f9c081d7a0daccd5d4c0555ca26447ba148ac` | Para el caso, candidato, 2130 y razones coinciden con Teams. El puntaje es valor almacenado, no fórmula. |
| `titulación unificada 2026.xlsx` | `33ceda0c3cd3bfbc9da37c1d5920e7ef7330cf0be1af5ab336b6d1dea424fa27` | Una coincidencia de documento y DV en `Res_Tit_Carga`; sus encabezados no incluyen CODCLI ni plan. |
| `Titulación Unificada 2026.csv` | `b52586f6741109e293c90896721ca5b879f5f51ec98a1c80650464aa52356dec` | 431 filas de 23 campos; una coincidencia en posiciones 3 y 4 tratadas como documento y DV, conforme a las primeras columnas del XLSX. No tiene encabezados de campo acreditados en el archivo. |

**[B/C/E]** Las dos capturas coinciden en el candidato, puntaje y texto de razones; son copias relacionadas y no pruebas independientes de la atribución. No aparece la fórmula de puntuación ni una regla de desempate en las celdas del caso revisadas. La hipótesis sobre el orden del respaldo `titulados.xlsx` sigue siendo eso: una hipótesis, no una explicación confirmada.

**[B/C/E]** El título está presente en el libro de carga y en el CSV revisados. La hoja de carga no declara CODCLI ni plan de estudios. El código SIES y el RUT no resuelven por sí solos cuál de los dos expedientes de la misma carrera corresponde al título. El candidato guardado sigue siendo una atribución calculada, no una prueba documental del plan.

**[E] Pendientes concretos:** localizar la implementación o especificación que produjo `TRACE_SCORE_CANDIDATO`, incluyendo pesos y desempate; y el registro institucional de titulación o decisión respaldada que vincule título, CODCLI y plan. La fecha de cambio de plan tampoco se establece mediante esta búsqueda. El alcance de la lectura no demuestra inexistencia de esos documentos en otros respaldos.

**[C] QA y conservación:** `revisar.py` localiza el caso en memoria, contrasta datos en las cuatro fuentes y comprueba sus hashes antes y después. En la captura con formato extendido lee las primeras 499 filas de datos; el caso se localizó en ese rango. El resultado detallado, sin RUT ni CODCLI impresos, se guardó en `~/.local/share/ipss/busqueda_desempate_titulacion_20261026/` con permisos 0600, pues describe un caso individual. No se cambiaron bases, diccionario, denominadores ni tasas; sin commit ni push.
