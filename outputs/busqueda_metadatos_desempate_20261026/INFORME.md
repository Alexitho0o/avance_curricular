# Búsqueda de desempate en componentes internos de los respaldos · 26-10-2026

**[B/C] Alcance:** Titulación Unificada 2026, para el caso cuyo título se observa en 2025. Se revisaron los componentes internos, no las filas individuales, de la captura `16683-82...xlsx` y del libro `titulación unificada 2026.xlsx`. Son los respaldos cuyo examen de hojas se documentó en `outputs/busqueda_desempate_titulacion_20261026/`.

**[B/C] Captura:** sus seis componentes `customXml` son esquemas y metadatos; una búsqueda literal de `TRACE_SCORE_CANDIDATO`, `TRACE_REASONS_CANDIDATO`, `2130`, `CODCLI`, `PLAN_DE_ESTUDIO` y `desempate` no produjo coincidencias en esos componentes. No se identificaron macros VBA, conexiones, consultas, enlaces externos ni objetos incrustados en el paquete inspeccionado.

**[B/C] Libro de carga:** también contiene seis componentes `customXml` sin esas coincidencias literales y una definición de caché de tabla dinámica. Los nombres de campo de esa caché corresponden a los de la carga de titulación y dimensiones derivadas de fecha; no se observan campos CODCLI o plan. No se inspeccionaron ni exportaron registros de la caché.

**[E] Resultado:** estos componentes no permitieron recuperar la regla de puntuación/desempate ni un registro de título vinculado a CODCLI y plan. La ausencia de términos literales no demuestra que la regla o el registro no existan en otros archivos ni que un criterio no pueda expresarse con otros nombres. La hipótesis de selección por orden continúa sin demostración.

**[C] QA:** `inspeccionar.py` registra las rutas, hashes, nombres de componentes y campos observados en `RESULTADO_AGREGADO.json`; verifica SHA-256 antes y después de abrir cada respaldo. No escribe datos de personas ni altera fuentes. Las bases, diccionario, tasas y denominadores permanecen sin cambios; no se hizo commit ni push.

**[E] Evidencia aún necesaria:** el script o especificación original que generó `TRACE_SCORE_CANDIDATO` y sus reglas de desempate; el acto o registro institucional de titulación que declare CODCLI y plan, o la bitácora de migración que permita vincularlos con evidencia verificable.
