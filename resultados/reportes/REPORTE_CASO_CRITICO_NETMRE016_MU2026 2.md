# Reporte caso crítico NETMRE016 MU2026

Generado: 2026-06-25T17:31:43

## Respuesta corta

El archivo real cargado/regulatorio vigente es `resultados/matricula_unificada_2026_pregrado.csv`.
El registro `CODCLI=20171NETMRE016` sí fue incluido en la salida final por RUT `16935626-2`.

La fila final tiene `VERSION=3` y permite reconstruir el código `I162S2C3J4V3`.
Ese código coincide con **V3**.

Clasificación final: **B. CODIGO_CARGADO_VALIDO_PERO_NO_JUSTIFICADO**.

## Valores finales cargados

- COD_SED: `2`
- COD_CAR: `3`
- MODALIDAD: `3`
- JOR: `4`
- VERSION: `3`
- VIG: `1`
- Código reconstruido: `I162S2C3J4V3`
- Estado reconstrucción: `CODIGO_NO_ES_CANDIDATO_NETMRE`
- Fila CSV: `919`
- Hash archivo: `20f3c67b68630ca82400f1047702a7a5b7055956e0cd03f3ac9979c0490c94b3`

## Staging/trazabilidad

En `ARCHIVO_LISTO_SUBIDA`, el caso figura con:

- CODCLI: `20171NETMRE016`
- Plan: `NETMRE20121`
- CODCARPR: `NETMRE`
- Estado carga: `OK_CARGA_PREGRADO`
- Incluir en MU32: `SI`
- Resolución SIES: `PENDIENTE_GOBERNANZA`
- Candidatos: `I162S2C3J4V1 | I162S2C3J4V2`
- Código SIES final trazado: ``

## Oferta V1/V2

Los candidatos V1/V2 del staging y el V3 reconstruido existen en `DURACION_ESTUDIOS.tsv`. La diferencia relevante es institucional:

- `I162S2C3J4V1`: IP CIISA, modalidad 3, jornada 4, tipo plan 1, duración 8.
- `I162S2C3J4V2`: IP SAN SEBASTIAN, modalidad 3, jornada 4, tipo plan 1, duración 8.
- `I162S2C3J4V3`: IP SAN SEBASTIAN, modalidad 3, jornada 4, tipo plan 3, duración 4, asociado a `CICRE`/continuidad; no aparece como candidato NETMRE en el staging del caso.

## Homólogos

Registros encontrados para `PLAN_DE_ESTUDIO=NETMRE20121`: 1.

No se usa mayoría como regla. En la evidencia estructurada disponible, el caso queda sin resolución institucional explícita para distinguir V1/V2 en staging.

## Validador y post-carga

La evidencia local indica validación general del archivo final y presencia del caso en `sies_pendientes.tsv` como `PENDIENTE_GOBERNANZA` con `OK_CARGA_PREGRADO`.

## Impacto

- Fue efectivamente informado: **SI**.
- SIES recibió componentes que reconstruyen un código válido: **SI, `I162S2C3J4V3`**.
- Riesgo material: **ALTO**.
- Necesidad de rectificación: **REQUIERE_REVISION_INSTITUCIONAL_PREVIA_A_RECTIFICAR**.

## Acción recomendada

No generar rectificación automática desde esta auditoría. Confirmar institucionalmente por qué una fila `NETMRE20121`/`NETMRE` fue cargada con `VERSION=3` (`I162S2C3J4V3`), cuando el staging del caso solo mostraba V1/V2 como candidatos y dejó `PENDIENTE_GOBERNANZA`. Si no existe respaldo, evaluar rectificación con acto institucional separado.

Backup: `/Users/alexi/Documents/GitHub/avance_curricular/backups/pre_auditoria_caso_netmre016_mu2026_20260625_173014`
