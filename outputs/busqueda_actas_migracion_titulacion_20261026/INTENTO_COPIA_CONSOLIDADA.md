# Intento de copia a carpeta consolidada · 26-10-2026

**[D]** Alexi autorizó copiar los dos archivos identificados en `FUENTES_PENDIENTES.json` a `IPSS_CONCILIACION_UMAS_SIES_BASES`.

**[B/E]** La carpeta de destino existe. El intento de abrir cada archivo origen devolvió `TimeoutError: [Errno 60] Operation timed out`, sin permitir leer los bytes. Una búsqueda por nombre en la carpeta consolidada, los repositorios y `~/.local/share/ipss` no encontró otra copia. No se creó una copia vacía o parcial y no se obtuvo hash.

**[E]** Pendiente materializar los dos originales en OneDrive o disponer de copias legibles. Una vez disponibles, copiar sin sobrescribir y comparar SHA-256 de origen y destino antes de analizarlos; el archivo de titulados puede contener datos personales y debe tratarse como sensible. Las rutas exactas están en `FUENTES_PENDIENTES.json`.

**[C]** No se modificaron bases, diccionario, tasas, denominadores ni originales. Sin commit ni push.
