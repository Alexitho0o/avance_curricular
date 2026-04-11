# Fixture paralelo · Validación cruzada MU2026 · End to end

## Propósito

Este fixture permite probar en paralelo el flujo de Matrícula Unificada 2026 usando 20 registros correctos y 14 casos de error controlados. La prueba permite comparar entrada correcta, salida esperada MU32 y reglas críticas del Manual de Proceso Matrícula Unificada 2026, sin modificar el pipeline productivo ni el archivo oficial.

## Ubicación

`control/fixtures/mu2026_validacion_cruzada/`

## Archivos

* `entrada_correcta_20.tsv`: datos correctos de referencia con columnas auxiliares del consolidado.
* `salida_esperada_mu32.tsv`: salida esperada con las 32 columnas oficiales MU pregrado.
* `reglas_manual.tsv`: reglas críticas tomadas desde mensajes de error y estructura del Manual de Proceso Matrícula Unificada 2026.
* `casos_error_controlados.tsv`: registros alterados intencionalmente para probar detección de errores.
* `guia_comparacion.tsv`: pasos de comparación end to end.

## Criterio de aceptación

El fixture queda OK solo si:

* Los 20 registros válidos se proyectan exactamente a MU32.
* La salida obtenida coincide fila a fila y columna a columna con `salida_esperada_mu32.tsv`.
* Los campos auxiliares `COD_NIV_GLO`, `COD_IES` y `FECH_CAR` no aparecen en la salida MU32.
* Los 20 registros válidos no generan errores.
* Los 14 casos de error controlados generan errores esperados.
* El script no modifica archivos productivos.
* Toda evidencia queda bajo `control/fixtures/mu2026_validacion_cruzada/resultados/`.
