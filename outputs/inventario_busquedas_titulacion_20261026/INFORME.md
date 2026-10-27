# Inventario de búsquedas de titulación · 26-10-2026

**[C] Revisión adicional:** se leyeron cinco scripts identificados por su relación con titulaciones o la incorporación de sus registros. Ninguno contiene las cadenas `TRACE_SCORE_CANDIDATO`, `TRACE_REASONS_CANDIDATO` o `Res_Tit_Unificada`; tampoco se localizaron en ellos cadenas `CODCLI` o `PLAN_DE_ESTUDIO` mediante la comparación literal. Esto no acredita por sí solo el propósito completo de cada script ni excluye algoritmos con otros nombres **[E]**.

| Archivo | SHA-256 [C] |
|---|---|
| `outputs/auditoria_embudo_2317_20261022/completar_titulados.py` | `1f15b3b0b6295a7a3b55d0ca031f85844e3eb560dc5198329eb9b37a911ff316` |
| `procesos/caracterizacion/explorar_fuentes_matricula_titulacion.py` | `cb86d9012a43714d5e086abf634698f8de14793b7abc7407c4b0385e6abc299a` |
| `procesos/caracterizacion/EXTRACCION_MATRICULA_SIES _2007_2025/procesar_titulados_ipss.py` | `bcde21833c6d054ae0612ce3fbfdb3b2ee1ac8800f9ebfad11f6b58e23dc692c` |
| `procesos/caracterizacion/EXTRACCION_MATRICULA_SIES _2007_2025/extraer_titulados_ipss_por_anio.py` | `7adbeee3a2357accdd03df13752e0b15a628edc990a82b935657bed7fd1d2541` |
| `procesos/caracterizacion/EXTRACCION_MATRICULA_SIES _2007_2025/matrices_titulacion_bi.py` | `87a964c489caf3ccee52ff0f7a575bad5a3d6a0ead76293c60d46c8c317ea51d` |

**[E] Conteo:** hay dos evidencias concretas pendientes: (1) generador o especificación del puntaje y desempate; (2) registro que vincule el título con CODCLI y plan. No hay una lista exhaustiva de fuentes pendientes ni una ubicación confirmada para ellas, por lo que no se puede calcular cuántas búsquedas faltan ni afirmar que no existen más respaldos.

**[B/C] Antecedentes:** la traza y sus razones se conservan como valores; los dos expedientes de la misma familia comparten jornada y datos de ingreso. Las fuentes de carga examinadas no atribuyen formalmente un plan. Ver `outputs/revision_criterio_traza_codcli_20261026/INFORME.md` y `outputs/busqueda_desempate_titulacion_20261026/INFORME.md`.

**[C] Conservación:** lectura de código sin modificación de fuentes, bases, diccionario o denominadores. Sin commit ni push. Los hashes corresponden a las lecturas de esta revisión; no se ejecutaron los scripts inspeccionados.
