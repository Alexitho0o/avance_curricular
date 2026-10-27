# Búsqueda de PROMEDIOS para 2026 períodos 2 y 3

**Alcance:** seguimiento interno de actividad académica IPSS; comparación de respaldos por año y período nativos, no de matrícula vigente ni de tasas de retención. Sin cambios en bases, diccionario ni denominadores.

## Resultado

- **B/C:** el respaldo gobernado `PROMEDIOSDEALUMNOS_7804.xlsx` de Caracterización anual 2026, P3, hoja `Hoja1`, contiene 142.215 filas no vacías. SHA-256 `78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71`. El manifiesto de ejecución lo identifica como `promedios_auxiliar` y registra ese hash; no acredita que sea la extracción completa ni fija la fecha efectiva de los datos.
- **B/C:** el respaldo tiene 6.230 filas y 2.844 CODCLI distintos en 2026-período 2; 6.304 filas y 2.746 CODCLI distintos en 2026-período 3. Las filas son registros académicos, no personas ni matrículas.
- **B/C:** la unión de las tres fuentes usadas en v11 contiene 2.845 CODCLI en 2026-2 y 2.757 en 2026-3. Todos los CODCLI del respaldo ampliado aparecen en esa unión; la unión contiene uno adicional en 2026-2 y 11 adicionales en 2026-3. Un CODCLI no equivale necesariamente a una persona.
- **C:** con llave RUT normalizado + DV + CODCLI + carrera + plan + asignatura + sección por año y período, en 2026-2 hay 6.148 llaves comunes, 82 exclusivas del respaldo y 75 exclusivas de la unión v11; en 2026-3 hay 6.179 comunes, 125 exclusivas del respaldo y 117 exclusivas de la unión. Una llave única no es necesariamente una fila única, ni significa que sus calificaciones o estados coincidan.
- **B/C:** `PROMEDIOSDEALUMNOS_7804_001.xlsx` del mismo respaldo P3 tiene hash idéntico al 7804 analizado; no constituye una extracción independiente adicional.
- **E:** no se localizó y acreditó una extracción completa de 2026-T2/T3 dentro de las fuentes leídas. Más filas históricas o coincidencia de CODCLI no demuestran completitud. Falta evidencia de exportación, filtros y universo esperado por período, además de revisar los otros respaldos potencialmente accesibles.
- **E:** se localizó `PROMEDIOSDEALUMNOS_7952.xlsx` en OneDrive, pero su lectura falló por timeout/archivo no legible; no se atribuye contenido ni se afirma que esté vacío. `PROMEDIOS DE ALUMNOS_2019_202X.xlsx` tampoco pudo leerse. Su cobertura permanece no verificada.

## Fuentes y método

- **B:** tres fuentes v11 en `IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/`: 7804 SHA-256 `83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca`; 12166 SHA-256 `aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015`; 3233 SHA-256 `b1f2e395b9c5fbbd20e2a99f9e652843c24d2d743d3c9a2901303c4a06b0a25e`.
- **B:** respaldo ampliado: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/PROMEDIOSDEALUMNOS_7804.xlsx`. Manifiesto: mismo árbol, `P3/04_AUDITORIA/manifest_ejecucion.json`.
- **C:** `comparar_respaldos.py` lee las fuentes sin modificarlas y conserva identificadores solo en memoria; `RESULTADOS_AGREGADOS.json` contiene hashes, encabezados, conteos y resultados agregados. Las fechas `core.xml` se registran como metadatos del archivo, no como fecha certificada de corte o exportación.
- **E:** la fuente exacta, fecha y universo de una extracción realmente completa deben confirmarse en los registros de exportación UMAS. El período académico nativo no prueba por sí mismo la foto administrativa de cierre T2/T3.
