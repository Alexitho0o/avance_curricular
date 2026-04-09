# Auditoría de conversión de NIVEL en Matrícula Unificada

## Conclusión

**EQUIVALENCIA_DE_NIVEL_NO_DEMOSTRADA**

Matrícula Unificada contiene una lógica gobernada y reproducible para `NIV_ACA`, pero esa lógica opera sobre el nivel académico del matriculado. La evidencia técnica prioriza `DatosAlumnos.NIVEL` como `DA_NIVEL` y deja `Hoja1.NIVEL` solo como fallback porque fue identificado como nivel del ramo en malla.

La columna `NIVEL` utilizada por Avance Curricular proviene del listado institucional de planes y se usa como atributo de asignatura/plan para distribución de créditos. Con la evidencia local revisada, no queda demostrada la equivalencia entre `DA_NIVEL`/`NIV_ACA` de MU y `NIVEL` de planes de Avance.

## Conteos

- Scripts MU revisados con referencias: 38
- Referencias a NIVEL/NIV_ACA/semestre/año detectadas: 24621
- Conversiones o tratamientos relevantes documentados: 8
- Planes comparados en muestra controlada: 10
- Asignaturas comparadas por código: 306
- Contradicciones por nivel distinto: 0
- Casos candidatos a desbloqueo directo: 0
- Casos que requieren validación adicional o fuente específica: 33

## Criterio

No se debe trasladar la conversión de Matrícula Unificada a Avance Curricular sin una fuente adicional que defina expresamente la semántica de `NIVEL` del listado institucional de planes o una equivalencia validada entre ambas fuentes.
