# Lógica de asignación de VERSION MU2026

Generado: 2026-06-25T18:00:17

Hallazgo demostrado: la VERSION final puede persistir desde la columna oficial `VERSION` ya armada aunque `CODIGO_CARRERA_SIES_FINAL` esté vacío. En el caso control `20171NETMRE016`, staging mantiene `PENDIENTE_GOBERNANZA`, `CODIGO_CARRERA_SIES_FINAL` vacío y candidatos V1/V2, pero el CSV final conserva `VERSION=3`, reconstruyendo `I162S2C3J4V3`.

Ruta responsable observada:

- Script: `codigo_gobernanza_v2.py`
- Función: exportación de `out[MATRICULA_UNIFICADA_COLUMNS]`
- Línea orientativa: `3236`
- Campo origen: `VERSION`
- Efecto: el CSV final puede contener componentes SIES reconstruibles sin que exista `CODIGO_CARRERA_SIES_FINAL` trazable.

La asignación trazable desde `CODIGO_CARRERA_SIES_FINAL` aparece documentada alrededor de la línea `4089`, pero no cubre el caso control porque el código final explícito estaba vacío.

Registros con la misma ruta (código final vacío + VERSION final no vacía): ver TRAZABILIDAD_ASIGNACION_VERSION_MU2026.csv.
