# Reporte de Gobernanza — FOR_ING_ACT (MU 2026)

**Fecha:** 2026-04-08 15:20:38
**Fuente:** PROMEDIOSDEALUMNOS_7804.xlsx
**Config:** config_for_ing_act.json
**Registros evaluados:** 1365

## Dictamen Final

**⚠️ LISTO CON OBSERVACIONES**

## Distribución FOR_ING_ACT

| Código | Descripción | Conteo | % |
|--------|-------------|--------|---|
| 1 | Ingreso Directo | 1171 | 85.8% |
| 2 | Continuidad | 97 | 7.1% |
| 3 | Cambio Interno | 60 | 4.4% |
| 11 | Articulación TNS→Prof | 37 | 2.7% |
| **Total** | | **1365** | **100%** |

## Reglas activas

| Prioridad | Regla | Código | Registros |
|-----------|-------|--------|-----------|
| 1 | ARTICULACION_11 | 11 | 37 |
| 2 | CONTINUIDAD_2 | 2 | 97 |
| 3 | EXTERNO_4 | 4 | 0 |
| 4 | INTERNO_3 | 3 | 60 |
| 5 | DIRECTO_1 | 1 | 1171 |

## Hallazgos

- 🟡 **[V_ART_TITULO] WARNING**: 8 FOR=11 con TNS previo no TITULADO en DatosAlumnos (manual requiere título de nivel superior)
- 🟡 **[V1] WARNING**: Validación FOR=1 → ANIO_ING_ORI==ANIO_ING_ACT diferida (campos ORI/SEM no disponibles en DatosAlumnos)
- 🟡 **[V3] WARNING**: Validación pasaporte diferida — TIPO_DOC no presente en DatosAlumnos

## Políticas especiales

- **FOR_ING_ACT=4 (cambio externo):** BLOQUEADO_SIN_FUENTE — no existe indicador explícito en DatosAlumnos. 0 casos asignados.
- **Códigos 5-10:** BLOQUEADOS por política institucional. 0 casos emitidos.
- **Validación V1 (coherencia ORI/ACT):** Diferida — campos ANIO_ING_ORI/SEM no disponibles.
- **Validación V3 (pasaporte):** Diferida — TIPO_DOC no disponible en DatosAlumnos.

## Métricas de flags derivados

| Flag | True | False |
|------|------|-------|
| ES_CONTINUIDAD_DA | 118 | 1247 |
| ES_TECNICO_DA | 639 | 726 |
| PROGRAMA_ACTUAL_ES_PROFESIONAL_DA | 726 | 639 |
| ES_CAMBIO_INTERNO_DA | 63 | 1302 |
| ES_CAMBIO_EXTERNO_DA | 0 | 1365 |
| TIENE_TNS_PREV_DA | 41 | 1324 |

## Checklist Final

- [x] Manual TSV leído y reglas confirmadas para códigos 1,2,3,4,11
- [x] JSON config creado y versionado (config_for_ing_act.json)
- [x] Reglas TSV creadas (for_ing_act_rules.tsv)
- [x] Trazabilidad long TSV creada
- [x] Excel auditoría generado con ≥ 500 CODCLI (1365 evaluados)
- [x] Tests unitarios ejecutados y OK (ver golden_cases)
- [x] 11 vs 3 validado con casos reales
- [x] Códigos bloqueados nunca emitidos
- [x] Reporte de gobernanza emitido con dictamen final