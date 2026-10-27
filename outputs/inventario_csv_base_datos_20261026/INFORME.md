# Inventario de cabeceras CSV y GZ · 26-10-2026

**[C] Alcance:** se enumeraron 146 archivos `.csv` o `.gz` bajo `0 BASES DE DATOS` y se intentó leer su primera línea, con un límite de cinco segundos por archivo. Se guardaron solo indicadores estructurales y hash de la primera línea, no datos individuales. El hash de la primera línea no es hash del archivo completo.

**[C/E] Resultado:** se leyeron 30 primeras líneas; 116 lecturas agotaron el tiempo y quedan sin examinar. De las 30 leídas, 28 tuvieron una cabecera reconocible bajo los patrones utilizados y dos no. Ninguna cabecera leída reunió literalmente CODCLI, plan y título ni las etiquetas de la traza. Un CSV sin encabezado, un campo con otro nombre o un archivo cuyo contenido no se leyó podrían dar otro resultado; no se declara ausencia universal **[E]**.

**[C/E] Nota:** los archivos pendientes por tiempo incluyen fuentes de matrícula y titulados con MRUN y derivados SIES; no se intentó vincular MRUN con RUT. `RESULTADO_AGREGADO.json` registra ruta y resultado por archivo. Para saber qué archivos deben descargarse localmente se requiere revisar esas rutas; un timeout no identifica por sí solo su causa.

**[C] Conservación:** `revisar.py` solo lee la primera línea y no modifica fuentes, bases ni denominadores. Sin commit ni push.
