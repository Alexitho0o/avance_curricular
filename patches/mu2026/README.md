# Patch MU2026: SIT_FON_SOL por RUT

## Estado
- `PROVISORIO_AUDITABLE`

## Propósito
Corregir errores masivos MU 2026 del tipo:
- `La SITUACIÓN SOCIOECONÓMICA FONDO SOLIDARIO no corresponde para el TIPO INSTITUCIÓN.`

La corrección se aplica **solo** a los RUT listados en:
- `patches/mu2026/sit_fon_sol_patch_ruts.json`

## Alcance
- Granularidad por persona (RUT sin DV del JSON).
- Campo objetivo: `SIT_FON_SOL`.
- Valor aplicado: el definido en el JSON (actualmente `0` en todas las correcciones).
- No se modifica la estructura contractual MU32 (`32 columnas`, `;`, sin header).

## Regla normativa
Referencias locales:
- `manual_matrícula_unificada 2.txt`:
  - `AB SIT_FON_SOL`.
  - catálogo válido `0, 1, 2`.
  - error explícito por incompatibilidad con tipo de institución.
- `gobernanza_columnas_mu/gob_mu_sit_fon_sol.tsv`:
  - `0: No cumple/no aplica; 1: Si cumple; 2: No presenta documentación`.

Aplicación de este patch:
- Para RUT listados en el JSON provisional auditado: `SIT_FON_SOL = 0`.

## Hook en pipeline
Integrado en `codigo_gobernanza_v2.py`:
- Se ejecuta sobre `archivo_subida` antes de la exportación final.
- Actualiza trazabilidad por fila objetivo:
  - `SIT_FON_SOL_FUENTE_FINAL = PATCH_JSON_SIT_FON_SOL_MU2026`
  - `SIT_FON_SOL_METODO_FINAL = OVERRIDE_POR_RUT_LISTADO`
  - `SIT_FON_SOL_AUDIT_STATUS = PATCH_PROVISORIO_AUDITABLE_APLICADO`
  - `SIT_FON_SOL_PATCH_FLAG = SI|NO`
  - `SIT_FON_SOL_PATCH_RUT` (RUT base normalizado)

Módulo utilitario:
- `src/patches/apply_patches.py`
  - `load_json_patch(path)`
  - `apply_sit_fon_sol_patch(df, patch_path, ...)`

## Ejecución
```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
make run-and-validate-oficial INPUT_XLSX="/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx"
```

## Verificación rápida
```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
make validate-oficial OUTPUT_DIR=resultados
```

Evidencia esperada:
- `resultados/reporte_matricula.json` (bloque `sit_fon_sol_patch_stats`).
- `resultados/reporte_patch_sit_fon_sol.json`.
- `resultados/archivo_listo_para_sies.xlsx`:
  - hoja `PATCH_SIT_FON_SOL`.
  - hoja `PATCH_SIT_FON_SOL_MISS` (solo si hay RUT del patch no encontrados).
- `control/reportes/reporte_estado_admin_mu_2026.json` con gate AB validado por patch.

## Criterio de conformidad (QA)
- Todas las filas con RUT objetivo deben terminar con `SIT_FON_SOL=0`.
- Filas no objetivo no deben quedar marcadas con fuente patch.
- Se mantiene contrato MU32 sin columnas extra.

## Observaciones
- Este patch no reemplaza gobernanza definitiva; es una medida controlada y trazable mientras se consolida la remediación institucional.
