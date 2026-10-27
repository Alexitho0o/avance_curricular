# Procedencia de PROMEDIOS y contraste de estados: 2026-P2/P3

**Proceso:** seguimiento interno de actividad académica IPSS. **Período de datos:** 2026-2 y 2026-3 nativos. Las fechas de ejecución de Caracterización no son fechas certificadas de exportación UMAS ni fechas administrativas de cierre.

## Fuentes y fechas

- **B:** el manifiesto de Caracterización anual P3 registra el respaldo ampliado 7804, SHA-256 `78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71`, como `promedios_auxiliar` en un procesamiento del 15-10-2026 entre 14:18:42 y 14:20:42, zona America/Santiago. Manifiesto P3 SHA-256 `c0f23e85071dd0c319d1bd1bff05f22a49d898a7ba6d67bc4882595113690c8a`. Esto acredita que esa edición se usó en ese procesamiento; no establece cuándo se exportó originalmente de UMAS.
- **B/C:** los manifiestos P1, P2 y P3 del proceso del 15-10 registran exactamente el mismo SHA-256 para PROMEDIOS. No son tres exportaciones independientes por período. Rutas y hashes de los manifiestos en `PROCEDENCIA_EXPORTACION_AGREGADA.json`.
- **B:** el inventario del proyecto del 22-10-2026 registra `PROMEDIOSDEALUMNOS_12166.xlsx`, SHA-256 `aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015`, con 70.000 filas; registra el archivo en Descargas, no la consulta ni la fecha de exportación UMAS. Inventario SHA-256 `5073cff946c59febd56cf14f72023494d4c42bb54eee143553353dfb1428b159`.
- **B/C:** lectura directa de `docProps/core.xml`: 12166 no contiene `created` ni `modified`; el respaldo tiene `modified=2026-10-15T16:51:57Z` y no contiene `created`. Son metadatos del archivo, no una fecha validada de exportación UMAS.
- **C:** se corrigió `RESULTADOS_AGREGADOS.json` y el lector, porque `openpyxl` completó fechas de creación ausentes con la hora de lectura. El resultado conserva el hash de su versión anterior; los conteos y las fuentes no cambiaron. Los valores actuales de fechas se leen del XML directamente.
- **B/C/E:** ambas hojas registran autofiltro de Excel sin criterios de columna ni filas ocultas; eso no demuestra qué filtros se usaron en la consulta UMAS que produjo cada extracción. No se localizó en los registros revisados la consulta, su fecha de ejecución ni el universo esperado por período.

## Diferencias contrastadas

- **B/C:** para los dos expedientes de T2 y el de T3 con discrepancia de estado, los dos respaldos `DATOSDEALUMNOS_10246` y `DATOSDEALUMNOS_11998` muestran VIGENTE; `DATOSDEALUMNOS_12159` muestra respectivamente SUSPENDIDO para los dos de T2 y ELIMINADO para el de T3, coincidiendo con PROMEDIOS 12166. Identidad y CODCLI se cruzaron exactamente; conteos y hashes en `CONTRASTE_ESTADOS_RESPALDOS_AGREGADO.json`.
- **E:** los respaldos muestran estados distintos, pero no incluyen una fecha efectiva acreditada del cambio para estos casos. No se concluye cuándo ocurrió ni cuál fue el estado exacto en el cierre.
- **B/C:** permanecen nueve pares en T3 con igual expediente/plan/asignatura y secciones diferentes, y 653 llaves con nota vacía en el respaldo y cero en 12166. No se encontró en los manifiestos examinados una bitácora que explique sección o la representación de nota; faltan los registros UMAS pertinentes (E).
- **E:** no hay evidencia suficiente para confirmar cobertura completa de T2/T3 ni para afirmar que alguna extracción sustituye a la otra. Se requieren parámetros originales de exportación, fecha/hora y universo por período, además de historial de secciones, notas y eventos de estado, si existe.

**C:** Métodos y resultados agregados en `auditar_procedencia_exportaciones.py`, `PROCEDENCIA_EXPORTACION_AGREGADA.json`, `contrastar_estados_respaldos.py` y `CONTRASTE_ESTADOS_RESPALDOS_AGREGADO.json`. Identificadores procesados solo en memoria. No se modificaron bases, diccionario o denominadores; sin commit ni push.
