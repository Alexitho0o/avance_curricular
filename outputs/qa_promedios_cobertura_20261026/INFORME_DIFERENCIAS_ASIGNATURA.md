# Diferencias académicas entre respaldo ampliado y fuentes v11

**Alcance:** IPSS, actividad académica 2026 períodos nativos 2 y 3. Las fuentes usadas en v11 son 7804, 12166 y 3233; se verificaron sus hashes y los resultados de cobertura previos. Solo 12166 contiene filas de 2026-2/3 entre esas tres. Se comparó con el respaldo anual P3 7804, hoja `Hoja1`. No se alteraron bases ni denominadores.

## Comparación de llaves académicas

**C:** la llave es RUT normalizado + DV + CODCLI + carrera + plan + `CODRAMO` + `CODSECC`, por año y período. Los valores son llaves únicas, no estudiantes; las categorías de exclusivas son disjuntas dentro de cada fuente, pero los estudiantes de una fuente pueden aparecer en ambas. No se vincularon casos por nombre de persona.

| Período | Llaves comunes | Solo respaldo | Solo v11 |
|---|---:|---:|---:|
| 2026-2 | 6.148 | 82 | 75 |
| 2026-3 | 6.179 | 125 | 117 |

- **B/C · 2026-2:** las 82 llaves exclusivas del respaldo corresponden a expedientes con otras asignaturas en v11. De las 75 exclusivas de v11, 74 tienen otras asignaturas en el respaldo y una pertenece a una persona no encontrada en ese respaldo para el período. Ninguna exclusiva tiene coincidencia de `CODRAMO` en distinta sección bajo el mismo expediente y plan.
- **B/C · 2026-3:** nueve llaves exclusivas por cada fuente forman nueve pares uno a uno de misma persona, CODCLI, carrera, plan y `CODRAMO` con distinta sección; coinciden también `RAMOEQUIV` y nombre de asignatura. No se ha acreditado cuál sección es la correcta al cierre ni por qué difiere (E).
- **B/C · 2026-3:** otras 116 llaves solo del respaldo y 80 solo de v11 tienen el mismo expediente y plan con otras asignaturas en la fuente contraria; dos exclusivas de v11 corresponden a persona encontrada con otro CODCLI y 26 a personas no encontradas en el respaldo. No se identificó para esas llaves coincidencia de `RAMOEQUIV` o nombre bajo el mismo expediente y plan. Las 26 llaves pertenecen al conjunto de 10 personas presentes solo en v11 ese período; no son 26 personas.
- **E:** las diferencias de asignaturas pueden reflejar cobertura, edición u otro cambio, pero no hay bitácora o fecha efectiva para adjudicar una causa. Una coincidencia de nombre o ramo equivalente es evidencia exploratoria, no autorización para fusionar registros.

## Valores distintos en llaves comunes

- **B/C:** en 2026-2, cinco llaves de dos personas muestran `ESTADO_ACADEMICO` VIGENTE en el respaldo y SUSPENDIDO en 12166; no se encontraron notas distintas entre las 6.148 llaves comunes.
- **B/C:** en 2026-3, 653 llaves de 585 personas muestran `NOTA_FINAL` vacío en el respaldo y cero en 12166. La lectura con fórmulas visibles no encontró fórmulas de `NOTA_FINAL` en esos períodos de ambas fuentes. El significado de vacío y cero sigue sin acreditarse; no se los equipara ni se los trata automáticamente como aprobación o reprobación (E).
- **B/C:** una llave de una persona en 2026-3 muestra VIGENTE en el respaldo y ELIMINADO en 12166. El estado de un extracto no prueba el estado en la fecha administrativa de cierre (E).

## Efecto sobre cobertura y pendiente

- **B/C:** el respaldo aporta llaves de actividad adicionales para personas ya presentes en las fuentes v11, pero ningún CODCLI ni persona adicional en los períodos comparados. Su incorporación potencial requeriría conciliar sección, contenido y fechas; no se aplicó.
- **E:** las diferencias no permiten certificar cobertura completa. Faltan el registro de exportación UMAS, filtros y universo esperado por período; deben aclararse además las discrepancias de sección, notas y estado antes de elegir o fusionar datos. PROMEDIOS representa actividad, no prueba por sí solo matrícula vigente ni retención.
- **C:** detalle agregado en `DIFERENCIAS_ASIGNATURA_AGREGADO.json` y `QA_FORMULAS_NOTA.json`; scripts `analizar_diferencias_asignatura.py` y `verificar_formulas_nota.py`. El cruce usa identificadores exclusivamente en memoria; no crea una nómina individual.

**Fuentes B:** respaldo anual 7804 SHA-256 `78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71`; 12166 SHA-256 `aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015`; los otros dos hash y rutas están en `RESULTADOS_AGREGADOS.json`.
