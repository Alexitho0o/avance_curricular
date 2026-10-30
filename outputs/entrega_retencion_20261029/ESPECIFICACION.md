# H003 · Entrega agregada

Encargo D de Alexi, 29-10-2026. Seis hojas, sin recalcular elegibilidad ni
reconciliaciones cerradas. Las tasas y diferencias son fórmulas; los insumos
se leen de fuentes fijadas por SHA-256. V24 original se verifica; sus cachés
vacías se sustituyen únicamente por la copia recalculada ya declarada en REGLA.
No se incorporan bases personales. La extracción de XLSX se limita a rangos
agregados. Los sectores SIES 2025 usan el mapeo gobernado y excluyen la fila
Total general para no duplicar su denominador.

`construir_excel.py` verifica fuentes, prepara bloques y controles y llama al
autor JavaScript con Artifact Tool. `verificar_entrega.py` recalcula una copia
con LibreOffice es-CL, coteja celdas y conserva el libro original con cachés
recalculadas. Los PNG proceden del PDF renderizado por LibreOffice y de la
verificación con Artifact Tool. No se modifica ninguna fuente ni instalación.

Marca: paleta oficial; Arial como sustitución declarada porque las fuentes
oficiales no están instaladas. Formato chileno con números tipados. Años sin
separador, conteos con puntos literales y porcentajes con formato invariante
`0.0%`, verificados en es-CL. No se genera carga PES ni se publica en Git.
