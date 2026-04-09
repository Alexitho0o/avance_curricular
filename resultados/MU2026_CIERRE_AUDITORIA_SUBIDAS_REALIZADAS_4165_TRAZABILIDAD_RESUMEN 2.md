# MU2026 CIERRE AUDITORÍA · SUBIDAS REALIZADAS 4.165 + TRAZABILIDAD

> **Fecha generación**: 2026-05-11 13:42
> **Estado**: EXCEL_TRAZABILIDAD_4165_GENERADO

---

## Archivos generados

| Archivo | Ruta |
|---------|------|
| Excel resultados | `resultados/MU2026_CIERRE_AUDITORIA_SUBIDAS_REALIZADAS_4165_TRAZABILIDAD.xlsx` |
| Excel Desktop | `~/Desktop/MU2026_CIERRE_AUDITORIA_SUBIDAS_REALIZADAS_4165_TRAZABILIDAD.xlsx` |
| SHA256 Excel | `eac2a0ececb5eeed168091adf9942b7de4955dc497280736d6af260390b00011` |

---

## Fuentes utilizadas

| Fuente | Archivo | Registros | SHA256 |
|--------|---------|-----------|--------|
| Carga principal Punto 0 | `resultados/matricula_unificada_2026_pregrado_PES_READY.csv` | 4.070 | `8ac3d586...` |
| Complemento 95 V3 | `resultados/complemento_95_codcli/..._CORREGIDO_V3.csv` | 95 | `1940923b...` |
| DatosAlumnos | `~/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx` | 13.707 filas | — |
| Auditoría reconstrucción 95 | `resultados/auditoria_reconstruccion_95_codcli_para_subir.csv` | 95 | — |
| Multi-CODCLI | `resultados/auditoria_multi_codcli_decision_final.csv` | 98 | — |
| Log correcciones V2 | `resultados/complemento_95_codcli/log_correcciones_v2.tsv` | — | — |

---

## Contenido del Excel

### Hoja 1: SUBIDAS_REALIZADAS_4165

| Campo | Valor |
|-------|-------|
| Filas de datos | **4.165** |
| Columnas | **32** |
| Registros Punto 0 | 4.070 |
| Registros complemento 95 V3 | 95 |
| VIG=1 (vigentes) | 3205 |
| VIG=0 (no vigentes) | 960 |
| N_DOC únicos | 4071 |
| N_DOC con múltiples CODCLI | 94 |

### Hoja 2: TRAZABILIDAD_DATOSALUMNOS

| Campo | Valor |
|-------|-------|
| Filas de datos | **4.165** |
| Columnas | **134** |
| Trazabilidad completa | 0 |
| Trazabilidad parcial | 4165 |
| Sin DatosAlumnos | 0 |

---

## Advertencias

> ⚠️ **ESTE ARCHIVO RECONSTRUYE 4.165 REGISTROS LOCALES TRAZABLES, NO LOS 4.426 ACUMULADOS DE PES/SIES.**

- El total de **4.426 registros** visible en PES/SIES corresponde al acumulado histórico de la plataforma.
- Este Excel documenta exclusivamente las **dos cargas efectivamente realizadas** desde archivos locales:
  1. Carga principal Punto 0: 4.070 registros
  2. Carga complementaria 95 CODCLI V3: 95 registros
- La reconstrucción integral de los 4.426 se realizará cuando exista una exportación desde "Consultar Datos" de PES/SIES.
- Los campos `DA_REGION_COLEGIO_MEDIA`, `DA_PAIS_ESTUDIO_SECUNDARIO`, `DA_PLAN_ESTUDIO`, `DA_VERSION_PLAN` no están disponibles en DatosAlumnos y aparecen vacíos.
- El Punto 0 (4.070 registros) permanece intocable. Este archivo es solo de auditoría.
- El complemento 95 (95 registros) no fue regenerado. Se usa el V3 corregido.

---

## Preservación del Punto 0

```
Carga principal (Punto 0)  : 4.070 registros — SHA256: 8ac3d586...
Complemento 95 V3          :    95 registros — SHA256: 1940923b...
Ambos archivos intactos    : SÍ
Punto 0 modificado         : NO
```
