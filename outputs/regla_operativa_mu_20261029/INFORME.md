# H002i · Cierre histórico y prueba retrospectiva

Estado: CANDIDATA_NO_ACTIVA (D/C/E).

| anio | filas_mu | antiguos | antiguos_acierto_pct | nuevos | nuevos_acierto_pct | otros | total_evaluable | total_acierto_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2023 | 1145 | 527 | 98.29222 | 515 | 100.0 | 103 | 1042 | 99.136276 |
| 2024 | 1541 | 651 | 99.84639 | 782 | 99.616368 | 108 | 1433 | 99.720865 |
| 2025 | 2371 | 810 | 92.098765 | 1503 | 83.832335 | 58 | 2313 | 86.727194 |
| 2026 | 4105 | 1668 | 93.22542 | 2212 | 82.052441 | 225 | 3880 | 86.85567 |

## Desaciertos (incluye sin predicción)

| causa | filas |
| --- | --- |
| CAMBIO_DE_CODIGO_DEL_ALUMNO | 187 |
| TIPO_PLAN_NO_DETERMINABLE | 361 |
| VERSION_NUEVA_NO_DECLARADA | 282 |

## Cinco familias con más desaciertos

| familia | filas |
| --- | --- |
| I162S2C3J4 | 145 |
| I162S2C76J4 | 108 |
| I162S2C46J4 | 104 |
| I162S2C1J4 | 101 |
| I162S2C77J4 | 98 |

## Simulación 2027

| comparacion | familias |
| --- | --- |
| COINCIDE | 84 |
| NO_COMPARABLE_E | 37 |

## Solapamientos y cambios observados

| anio | tipo | filas |
| --- | --- | --- |
| 2024 | EXPEDIENTE_OBSERVADO_DISTINTO | 269 |
| 2024 | PLAN_OBSERVADO_DISTINTO | 269 |
| 2025 | EXPEDIENTE_OBSERVADO_DISTINTO | 1 |
| 2026 | EXPEDIENTE_OBSERVADO_DISTINTO | 2 |
| 2026 | PLAN_OBSERVADO_DISTINTO | 2 |

La prioridad literal del Paso 2 conserva estos casos en ANTIGUO si hay presencia anterior en la misma familia. No deben interpretarse automáticamente como antiguos sin cambio para una carga futura; la regla candidata requiere resolver ese alcance. Un cambio observado en el enlace anual no acredita una migración administrativa.

## Control FOR de 2026 (separado)

| anio | control | filas |
| --- | --- | --- |
| 2023 | SIN_INCOMPATIBILIDAD_FOR_2026 | 1145 |
| 2024 | SIN_INCOMPATIBILIDAD_FOR_2026 | 1541 |
| 2025 | SIN_INCOMPATIBILIDAD_FOR_2026 | 2371 |
| 2026 | CONTROL_FOR_2026_INCOMPATIBLE | 2 |
| 2026 | SIN_INCOMPATIBILIDAD_FOR_2026 | 4103 |

Los dos casos incompatibles del control FOR de 2026 no se corrigen ni se usan para alterar el dato informado. No se convierte este control en norma retrospectiva.

## Cierre histórico

{'ABIERTA': 28, 'CERRADAS_POR_DECISION_D': 35, 'CIERRE_PARCIAL': 9}; todas las entradas originales conservadas. Ver data/paridad_codigo_sies/cierre_historico_2007_2021/README.md y LOTES_REVISION_v3_CIERRE_H002i.md.

D · Alexi, 29-10-2026 autoriza probar; no activar. ANTIGUO prevalece sobre NUEVO si hay solapamiento. Identidad exacta y misma familia (S+C+J), sin filtro VIG. Código previo múltiple no se resuelve por mayoría. NUEVO: ANIO_ING_ACT del año, sin presencia anterior en esa familia. OTRO queda fuera de la tasa evaluable. Cambios de plan/expediente observados se informan sin alterar esta precedencia; no equivalen a bitácora de migración.

C · % acierto = aciertos / todas las filas ANTIGUO o NUEVO, incluidas las no predecibles. Total = suma de aciertos / suma de ambos grupos; nunca promedio de porcentajes. OTRO no es error ni acierto. Son matrículas, no personas únicas. CSV de métricas por grupo; JSON incluye familias y denominadores completos.

B/C · Oferta anual extraída del histórico 2010–2026 del 05-06-2026, contrastada con maestro y TSV gobernados. No acredita qué versión del catálogo estaba disponible el día de la carga. Perfiles H112B son evidencia interna candidata, no aceptación PES. FOR observado no se transforma en tipo de plan: FOR 11 no distingue por sí solo regular de continuidad. El control de compatibilidad FOR de 2026 se presenta separado, como sensibilidad C/E y no filtro histórico. Una oferta única permite predecir aun sin plan formal; no acredita compatibilidad individual del plan.

C/E · Para 2027 V06 es carga preparada; cada familia puede tener opciones distintas por tipo, no una versión universal. H002 con E es NO_COMPARABLE_E. ADMP/CADMP permanece pendiente incluso si su catálogo tiene opciones únicas por tipo. Antiguos 2027: universo potencial MU 2026 de 4.105 matrículas, no retención ni carga ni asignación personal. Aprobación expresa y métricas por año son requisitos previos a activar.

Fuentes por ruta/hash en MANIFEST.json. Reproducción: ejecutar construir.py; --check compara los bytes sin reescribir salidas. Detalle individual sólo en ~/.local/share/ipss/h002i_20261029/. No cambia H002–H002h, diccionario v20, fuentes ni tasas.
