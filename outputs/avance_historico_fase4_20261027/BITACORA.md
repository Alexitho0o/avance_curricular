# Fase 4 — Bitácora de construcción

[C] 4.1. Se leyó el plan de cuatro fases, la fase 3 y sus fuentes por hash. Se creó especificación antes del libro. No se aplicó la candidata de 644 atribuciones.

[C] 4.2. Se construyeron tres vistas separadas, fuentes, guía y controles. Fórmulas y objetos con Artifact Tool. Datos grandes incorporados secuencialmente a hojas 12–14 por límite de memoria. Se conserva la clasificación B de entradas y C de conteos preparados.

[C] 4.3. Se corrigió la búsqueda de unidades del plan, se distinguió cero de celda vacía y se verificaron las 40.245 fórmulas: 38.649 cachés no vacías y 1.596 resultados vacíos esperados contrastados con fuente. Cero errores de fórmula. 48 controles correctos y seis selecciones representativas. Quince hojas revisadas visualmente en rangos representativos; las bases individuales se revisaron en recortes de columnas sin identificadores. Los dos recortes RAW conservan filas y estilos de la entrega, sin cargar millones de celdas para la imagen. No hubo sesión de Excel conectada: QA nativo pendiente.

[C] Reproducción local: ejecutar preparar.py, construir.mjs (Node con --max-old-space-size=4096 --expose-gc), incorporar_bases.py, verificar.py y cerrar.py. El constructor requiere @oai/artifact-tool del runtime de Codex; durante la ejecución se usó un enlace temporal node_modules al runtime, retirado al finalizar. No usar IPSS_SOLO_FORMATO=1 en una reproducción completa: esa opción conserva las seis pruebas previas cuando solo se vuelve a exportar la presentación. Los intermedios individuales permanecen fuera de Git en ~/.local/share/ipss/avance_historico_fase4_20261027.

[C] Sin commit/push. La publicación de documentación y la confirmación de indicadores pendientes requieren su propia revisión; el Excel individual permanece excluido de Git.


[B/C] QA nativo: apertura sin reparación, recálculo completo y guardado. Se corrigieron 2.758 fórmulas de selección para comparar año/período como texto; seis filtros y 12 controles coinciden. Sin errores de fórmula observados; tres gráficos revisados. Bases sin cambios en comparación de celdas. Excel quitó espacios finales en 12 etiquetas de presentación y convirtió dos selectores en números. Copia anterior conservada en almacenamiento privado. Ver QA_EXCEL_NATIVO.json. [E] Los pendientes metodológicos de hoja 05 continúan; no constituyen aprobación de la candidata 644. Sin commit ni push.
