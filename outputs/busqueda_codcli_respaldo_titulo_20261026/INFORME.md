# Búsqueda por CODCLI en respaldo auxiliar · 26-10-2026

**[B/C] Alcance:** caso de Titulación Unificada 2026 cuyo título se observa en 2025 y que tiene varios expedientes. Se revisó `enviar.xlsx`, respaldo de la segunda carga de Matrícula Unificada 2026, SHA-256 `1abd4c4c77d1e665796a59129c28b159323bb638c8528b6b04106e02452acf07`. Este archivo es auxiliar de matrícula, no un registro oficial de titulación.

**[C] Búsqueda nueva:** el análisis anterior filtró por documento antes de contrastar CODCLI; señaló que 2.993 filas de `Hoja2` no tenían cuerpo y DV simples bajo ese lector. Para no depender de ese filtro, se tomaron los tres CODCLI conocidos del caso y se compararon literalmente con todos los valores de ambas hojas. Los identificadores se trataron solo en memoria.

| Hoja [B] | Filas de datos leídas [C] | Estructura observada [B] | CODCLI del caso localizados [B/C] |
|---|---:|---|---:|
| Hoja1 | 426 | Sin columna CODCLI, plan o título | 0 de 3 |
| Hoja2 | 28.933 | Con CODCLI y plan; sin columna de título | 0 de 3 |

**[B/C/E]** No se localizó ninguno de los tres identificadores como valor exacto en las celdas leídas, incluidas las filas cuyo documento no pudo interpretarse con el lector anterior. Esto no descarta representaciones distintas, otras fuentes o registros no contenidos en el libro. Aunque hubiera una coincidencia de matrícula, haría falta evidencia que la vincule al título.

**[E] Puntaje 2130:** esta búsqueda no encontró una implementación del puntaje o desempate; el libro es una tabla auxiliar de matrícula. Los resultados de la búsqueda técnica y de los componentes de las capturas permanecen en `outputs/busqueda_formula_traza_20261026/` y `outputs/busqueda_metadatos_desempate_20261026/`. No se afirma que la regla no exista en otros respaldos.

**[C] QA y conservación:** `revisar.py` verifica el hash de la fuente antes y después, recorre ambas hojas sin filtrar previamente por RUT y comprueba que el resultado agregado no contenga los identificadores buscados. No se alteraron fuentes, diccionario, tasas ni denominadores; sin commit ni push.
