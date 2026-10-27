# Copias de respaldos no legibles · 26-10-2026

**[C] Alcance:** se buscaron nombres `reporte_filtrado*.xlsx` y `subirR*.xlsx` en `avance_curricular`, `CARACTERIZACIÓN`, la carpeta de respaldos SIES de OneDrive, la carpeta consolidada IPSS, Descargas y, adicionalmente, el árbol OneDrive indicado por el usuario. La búsqueda por nombre no identifica necesariamente duplicados renombrados.

**[B/C] `reporte_filtrado.xlsx`:** las dos rutas de respaldos FCU previamente revisadas devolvieron tamaño cero. Se identificaron seis copias en los dos repositorios o sus respaldos locales: todas devolvieron cero bytes y SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. Otra ruta en OneDrive devolvió el mismo hash de archivo vacío y aparece como `dataless` en metadatos; el hash de los bytes entregados no acredita que no exista una versión remota diferente **[E]**.

**[C]** El historial Git revisado de los dos repositorios registra ese nombre con el objeto vacío `e69de29`; no se localizó en esos historiales una versión no vacía. El contenido no pudo examinarse y no se puede confirmar si ese archivo contenía título, CODCLI o plan **[E]**.

**[B/C] `subirR.xlsx`:** no apareció una segunda ruta con ese nombre en los ámbitos enumerados ni un archivo con ese nombre en el historial local de Git. La ruta original de Oferta Académica 2026 etapa 3 tiene tamaño lógico 166.111 bytes y el atributo `dataless`. Los intentos de `file` y listado de ZIP devolvieron error de lectura; no se pudo obtener un hash ni verificar hojas, campos o contenido. El atributo indica que los datos no están materializados localmente, pero no confirma el contenido remoto ni demuestra corrupción **[E]**.

**[E] Pendiente:** para revisar `subirR.xlsx` hace falta una copia accesible localmente, por ejemplo tras marcarla como disponible sin conexión en OneDrive. Para `reporte_filtrado.xlsx` se requiere una copia no vacía o una fuente verificable de contenido. La búsqueda por nombre no agota copias con nombres diferentes ni versiones en la nube.

**[C] Conservación:** se revisaron metadatos, hashes accesibles y Git en modo lectura. No se ejecutaron procesos de regeneración, no se modificaron fuentes, bases, diccionario, tasas o denominadores, ni se hizo commit o push.
