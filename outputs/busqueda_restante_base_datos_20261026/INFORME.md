# Revisión de libros y archivos comprimidos · 26-10-2026

**[C] Alcance:** se revisaron los 17 archivos `.xlsx` localizados bajo la carpeta `0 BASES DE DATOS`, con hash antes y después; se buscaron literalmente las etiquetas de la traza en el XML de hojas, cadenas compartidas y libro. Se inspeccionaron las primeras 12 filas y hasta 120 columnas de cada hoja para localizar encabezados con CODCLI y plan. No se encontraron las etiquetas buscadas ni encabezados que contengan ambos campos en ese rango. Esto no demuestra ausencia de un generador, información en otras filas o campos con otro nombre **[E]**.

**[B/C] Respaldo de matrícula 2025:** en `MATRÍCULA UNIFICADA/DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx`, hoja `BBDD`, SHA-256 `63c5cbc05494e4ac36b97041656ded478cf8deab2f562223e851d1cb2a2ef2f1`, se localizaron dos de los tres CODCLI conocidos del caso. En ambos coincide el cuerpo de RUT, pero no se acreditó el DV de forma independiente. No se identificaron campos de plan ni registro de título en la cabecera examinada. Su nombre no acredita fecha de extracción, y el hallazgo no determina el plan formal del título **[E]**.

**[B/C] Comprimidos:** se leyeron correctamente los listados de dos ZIP y dos RAR. Cada uno contiene un CSV y sus nombres corresponden a matrícula u oferta. No se extrajeron ni leyeron los CSV interiores; la inspección del listado no prueba qué contienen sus filas **[E]**.

**[C/E] Pendientes:** no se identificaron el script del puntaje 2130 ni un registro título–CODCLI–plan. La revisión de cabeceras de CSV y GZ está en `outputs/inventario_csv_base_datos_20261026/`; sus errores y límites se informan por separado.

**[C] QA:** `revisar.py` conserva únicamente rutas, hashes, estructuras y conteos; identificadores personales solo se comparan en memoria. No se modificaron fuentes, bases, diccionario, tasas ni denominadores. Sin commit ni push.
