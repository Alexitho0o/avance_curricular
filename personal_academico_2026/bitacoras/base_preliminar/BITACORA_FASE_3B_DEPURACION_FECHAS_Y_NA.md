# Bitacora Fase 3B - Depuracion de Fechas y NA

- Fecha/hora: 2026-06-11T23:15:57
- Rama: feature/personal-academico-base-preliminar-2026

## Archivos Modificados
- personal_academico_2026/data/base_general/base_preliminar_en_institucion_normalizada.tsv
- personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv
- personal_academico_2026/docs/REPORTE_FASE_3_BASE_PRELIMINAR.md
- personal_academico_2026/bitacoras/base_preliminar/BITACORA_FASE_3_BASE_PRELIMINAR.md
- personal_academico_2026/docs/REPORTE_FASE_3B_DEPURACION_FECHAS_Y_NA.md
- personal_academico_2026/bitacoras/base_preliminar/BITACORA_FASE_3B_DEPURACION_FECHAS_Y_NA.md
- personal_academico_2026/auditorias/base_preliminar/resumen_ultima_incorporacion_base_preliminar.json

## Archivos Creados
- personal_academico_2026/auditorias/base_preliminar/diagnostico_fechas_base_general_20260611_231557.csv
- personal_academico_2026/auditorias/base_preliminar/auditoria_incorporacion_base_preliminar_20260611_231557.csv

## Comandos Ejecutados
- `git branch --show-current`
- `git status --short`
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/incorporar_base_preliminar_personal_academico_2026.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/tests/fixtures/en_institucion_valido_minimo.csv`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo fuera_institucion --input personal_academico_2026/tests/fixtures/fuera_institucion_valido_minimo.csv`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Resultado Antes
- Base general TSV era rechazada por `fecha_formato` asociado principalmente a `#N/A`.

## Resultado Despues
- `#N/A`, `#N/D`, `N/A`, `NA` y `NO APLICA` se clasifican como no disponibles, no como formato invalido.
- Campos de fecha revisados: 570
- FECHA_NO_DISPONIBLE: 197
- FECHA_INVALIDA: 0
- FECHA_FUTURA: 1

## Validaciones
- Fixture En Institucion: 0 errores criticos, 0 advertencias, estado APROBADO_CON_ADVERTENCIAS.
- Fixture Fuera Institucion: 0 errores criticos, 0 advertencias, estado APROBADO_CON_ADVERTENCIAS.
- Base general TSV: 190 filas, 34 columnas, 1 error critico, 569 advertencias, estado RECHAZADO.
- Base general TSV detalle: 197 `fecha_no_disponible`, 372 `fecha_tolerancia_iso`, 1 `fecha_futura`; 0 `fecha_formato`.
- Exportador bloqueado: OK; no se creo `personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`.

## Pendientes
- Corregir o respaldar valores fuente no disponibles.
- Revisar fecha futura detectada.
- Mantener base como preliminar hasta depuracion y aprobacion.
- No generar PES_READY sin autorizacion y auditoria aprobada.
