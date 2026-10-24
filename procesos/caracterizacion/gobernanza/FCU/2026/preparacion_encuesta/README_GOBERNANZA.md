# README Gobernanza - FCU_ANALISIS_ENCUESTA

## Nombre del proceso

FCU_ANALISIS_ENCUESTA

## Alcance

Encuesta/LimeSurvey, preguntas no FCU, sustentabilidad, SEP_TODAS y reglas KPI de uso interno.

## Fuente de clasificación

- Clasificación fina: `gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.tsv`
- Respaldo Excel: `gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.xlsx`
- Mapeo base: `gobernanza/_mapeo_proyecto/MAPEO_ARCHIVOS_PROYECTO_CARACTERIZACION.tsv`

## Estado

GOBERNANZA_ESPERADA_COMPLETA

## Reglas de uso

- No modificar evidencias originales.
- No mover ni borrar archivos productivos.
- Usar `evidencias/` solo para copias controladas.
- Usar `tablas/`, `json/`, `hashes/`, `docs/` y `validaciones/` para auditoría y trazabilidad.
- Tratar archivos referenciales como soporte documental, no como reconstrucción de cargas.

## Estructura de carpetas

- `evidencias/`: copias controladas.
- `tablas/`: índices TSV y validaciones tabulares.
- `json/`: equivalentes JSON y dictámenes estructurados.
- `hashes/`: archivos `.sha256` por evidencia.
- `docs/`: dictámenes, manifiestos y documentación del proceso.
- `validaciones/`: validaciones mínimas por proceso.

## Advertencias

Este paquete formaliza gobernanza documental. No recalcula procesos productivos ni altera fuentes originales.

## Próxima acción

Versionar auditoría y separar usos internos de KPI oficial FCU.

FASE 1 TERMINADA: SÍ.
