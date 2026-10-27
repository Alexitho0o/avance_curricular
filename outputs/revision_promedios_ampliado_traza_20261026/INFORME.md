# PROMEDIOS ampliado y origen de traza de titulación · 26-10-2026

## 21 ramos

**[B/C]** Se compararon `PROMEDIOSDEALUMNOS_7804.xlsx` consolidado, SHA-256 `83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca`, con el respaldo ampliado del mismo nombre en `CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/`, SHA-256 `78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71`. Ambos fueron leídos y verificados antes y después.

La llave es RUT cuerpo+DV+CODCLI+carrera+plan+año+período+CODRAMO+CODSECC; los identificadores se usan solo en memoria. Cada extracción contiene **33 llaves distintas** para los **21 pares carrera–plan–ramo**; las 33 coinciden y ninguna es exclusiva de una fuente.

**[B/C]** En 12 llaves el campo `CONVALIDADO` dice literalmente `NULL` en el archivo previo y está vacío en el ampliado. `ESTADO`, `DESCRIPCION_ESTADO` y `RAMOEQUIV` coinciden en las 33 llaves comparadas. Los dos valores distintos se conservan sin declarar que signifiquen lo mismo **[E]**. El respaldo ampliado no aporta nuevas llaves en este grupo ni transforma la evidencia en una homologación universal.

## Cuatro trazas de titulación

**[B/C]** El libro institucional enriquecido de titulación guarda para las cuatro personas una traza de candidato de puntaje `2130`. Sus razones contienen los mismos criterios textuales: RUT exacto; jornada exacta; comparación de año y semestre de ingreso actual y de origen con `ANOINGRESO` y `PERIODOINGRESO`; familia por `NOMBRE_TITULO` y `NOMBRE_L`; nivel de salida frente al nivel del plan; y cercanía entre semestre de ingreso actual y `PERIODOMATRICULA`.

La traza seleccionó el expediente anterior para los cuatro casos; la evidencia ya revisada de Datos Alumnos y PROMEDIOS muestra actividad posterior y estado titulado en los expedientes posteriores. Las razones registran criterios del candidato elegido, no una comparación completa y verificable de todos los candidatos ni la fecha efectiva del cambio.

**[E]** Se buscó la implementación por `TRACE_SCORE_CANDIDATO` y la cadena `NIVEL DE SALIDA` en código y documentación de avance_curricular, CARACTERIZACIÓN y el directorio institucional de Titulación Unificada. No se localizó la fórmula de puntuación o sus pesos en el alcance revisado. No se atribuye el puntaje a una regla oficial ni se confirma por él el plan formal del título. Los cuatro casos siguen pendientes de registro título–CODCLI–plan o bitácora de migración con fecha efectiva.

## Reproducción y conservación

`contrastar.py` verifica hashes, compara llaves y guarda en `RESULTADO_AGREGADO.json` únicamente conteos y etiquetas. Las fuentes, bases, diccionario, tasas y denominadores permanecen intactos. No se realizó commit ni push.
