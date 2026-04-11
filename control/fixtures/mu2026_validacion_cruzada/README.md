# Fixture MU2026 · Validacion cruzada end to end

## Proposito

Este fixture permite validar en paralelo una muestra de 20 registros correctos contra una salida MU32 esperada y 14 casos de error controlados, sin modificar el flujo productivo ni el archivo oficial de carga.

## Alcance

Este control es un test opcional, no productivo y no obligatorio para liberar la carga oficial.

## Que valida

- Proyeccion desde consolidado de referencia hacia MU32.
- Eliminacion de campos auxiliares COD_NIV_GLO, COD_IES y FECH_CAR.
- Estructura de 32 columnas oficiales.
- Reglas de TIPO_DOC.
- Reglas de DV para RUT y pasaporte.
- Reglas de N_DOC para RUT.
- Regla ANIO_ING_ORI=1900 implica SEM_ING_ORI=0.
- Rangos de ASI_INS_HIS y ASI_APR_HIS.
- Cruce ASI_APR_HIS <= ASI_INS_HIS.
- Regla NIV_ACA <= 2 cuando ANIO_ING_ORI=2026.
- Regla FOR_ING_ACT 1, 6, 7, 8, 9 o 10 exige ANIO_ING_ORI = ANIO_ING_ACT.
- Regla VIG en 0, 1 o 2.
- FECH_NAC no vacia.
- Cruce ASI_APR_ANT <= ASI_INS_ANT.
- Regla R12b: en primer ingreso de ano actual, ASI_INS_ANT no puede ser mayor a 0.

## Como ejecutar

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
source .venv/bin/activate
python -m py_compile scripts/fixture_validacion_cruzada_mu2026.py
python scripts/fixture_validacion_cruzada_mu2026.py
```

## Salidas generadas

- control/fixtures/mu2026_validacion_cruzada/resultados/resultado_fixture_validos.tsv
- control/fixtures/mu2026_validacion_cruzada/resultados/resultado_fixture_errores.tsv
- control/fixtures/mu2026_validacion_cruzada/resultados/comparacion_esperado_vs_obtenido.tsv
- control/fixtures/mu2026_validacion_cruzada/resultados/reporte_fixture_mu2026.md
- control/fixtures/mu2026_validacion_cruzada/resultados/resumen_fixture_mu2026.json

## Criterio de aceptacion

- 20 validos evaluados.
- 0 errores en validos.
- 14/14 errores controlados detectados.
- 0 diferencias de proyeccion.
- 0 campos auxiliares indebidos.
- dictamen_fixture = OK.

## Dictamenes posibles

- OK
- CONDICIONAL
- NO_LISTO

## Advertencia operativa

Este fixture no reemplaza qa_checks.py, no reemplaza auditoria_maestra.py y no modifica el gate oficial. Es una prueba paralela de regresion tecnica.
