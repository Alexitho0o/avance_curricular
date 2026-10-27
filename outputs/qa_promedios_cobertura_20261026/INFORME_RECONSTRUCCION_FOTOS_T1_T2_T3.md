# Reconstrucción por fotografías: discrepancias académicas 2026

**Alcance:** comparar los grupos afectados en 2026-P2/P3 por RUT con DV y CODCLI, sin cambiar bases ni denominadores. **D:** Alexi indica usar las fotos T1/T2/T3 como referencia de matrícula y PROMEDIOS como fuente granular de actividad, sin exigir el día exacto cuando no exista. Una fuente solo puede informar los campos y registros que contiene; no atribuir una ausencia a deserción.

## Estados

- **B/C:** en la foto T3 `Matrícula_T3_02_10_2026.xlsx`, hoja `Base`, se encuentra por RUT y CODCLI el expediente con estado discrepante T3; aparece con año/período de matrícula 2026-3 y **VIGENTE**. Para esa fotografía, ese es el estado observado. La otra extracción PROMEDIOS 12166 registra ELIMINADO, lo que no se corrige ni se interpreta como error sin más evidencia (E).
- **B/C:** para los dos expedientes de T2 con discrepancia de estado, uno aparece en la foto T2 `Matrícula T_2_13_07_2026.xlsx`, hoja `Hoja1`, y el otro no se localiza. La hoja no contiene `ESTADOACADEMICO`, por lo que no puede mostrar directamente el estado de ninguno. Los respaldos Datos Alumnos 10246 y 11998 muestran VIGENTE para ambos; 12159 y PROMEDIOS 12166 muestran SUSPENDIDO. Son observaciones de extracciones, no una secuencia con fecha de evento acreditada. Tampoco se infiere la situación de la persona no encontrada en la foto (E).

## Secciones

- **B/C:** ninguno de los nueve expedientes con secciones diferentes T3 se localiza en las hojas de las fotos T2 o T3 revisadas. Ninguna de esas hojas contiene `CODSECC`. No se observa el mismo CODRAMO para esos nueve expedientes en los períodos 2026-1 o 2026-2 de las dos extracciones PROMEDIOS comparadas. Por tanto se conservan las dos secciones de T3; no hay evidencia para seleccionar una ni se infiere que no cursaron otras asignaturas (E).

## Notas

- **B/C:** las 653 llaves T3 con nota vacía en el respaldo y cero en 12166 corresponden a 585 expedientes. En ambas extracciones, los campos `ESTADO` y `DESCRIPCION_ESTADO` de esas 653 llaves están vacíos. Las fotos T2/T3 no tienen `NOTA_FINAL`, por lo que no deciden entre vacío y cero. No se consideran valores equivalentes ni se deduce aprobación o reprobación (E).
- **B/C:** 51 de esos 585 expedientes aparecen en la hoja `Base` de la foto T3 y todos tienen estado VIGENTE; 49 de esos registros muestran año/período de matrícula 2026-3. Son grupos superpuestos con los demás casos y no se suman para obtener personas distintas.

## Trazabilidad y límites

- **B:** foto T2 SHA-256 `7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769`; foto T3 SHA-256 `de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae`. Rutas, hojas y conteos en `CONTRASTE_FOTOS_DISCREPANCIAS_AGREGADO.json`.
- **C:** `contrastar_fotos_estudiantes.py` y `contrastar_historia_secciones.py` conservan los identificadores únicamente en memoria. La ausencia en estas hojas no demuestra ausencia en toda la matrícula; la observación de actividad tampoco equivale a matrícula vigente ni retención.
- **E:** la cobertura de PROMEDIOS 2026 no está certificada y las dos extracciones proporcionan valores diferentes. No existe evidencia para tratarlas como una única foto completa o reemplazar valores de manera automática. Sin cambios a originales, diccionario, denominadores, commit o push.
