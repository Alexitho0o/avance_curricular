# Bitacora Fase 3C - Correcciones Controladas

- Fecha/hora: 2026-06-11T23:23:51
- Rama: feature/personal-academico-base-preliminar-2026

## Archivos Creados
- personal_academico_2026/control_correcciones/correcciones_manual_base_general_en_institucion.tsv
- personal_academico_2026/auditorias/base_preliminar/auditoria_correcciones_base_general_20260611_232351.csv
- personal_academico_2026/docs/REPORTE_FASE_3C_CORRECCIONES_CONTROLADAS.md
- personal_academico_2026/bitacoras/base_preliminar/BITACORA_FASE_3C_CORRECCIONES_CONTROLADAS.md

## Archivos Modificados
- Ninguno en base general; sin correcciones autorizadas validas.

## Comandos Ejecutados
- `git branch --show-current`
- `git status --short`
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/aplicar_correcciones_base_general_personal_academico_2026.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Resultado Antes
- Base general preliminar rechazada por 1 `fecha_futura`.

## Resultado Despues
- Correcciones leidas: 1
- Correcciones aplicadas: 0
- Correcciones pendientes: 1
- Correcciones rechazadas: 0

## Validacion Posterior
- Base general TSV: RECHAZADO; 190 filas, 34 columnas, 1 error critico, 569 advertencias.
- Causa exacta: `fecha_futura` en `FECHA_OBT_TIT_O_GRADO`, fila 20, valor `2027-11-29`.
- Fixture En Institucion: 0 errores criticos, 0 advertencias.
- Fixture Fuera Institucion: 0 errores criticos, 0 advertencias.

## Estado de Exportador
- BLOQUEADO correctamente; no se creo `personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`.

## Pendientes
- Completar archivo de control con fecha corregida respaldada, autorizacion, responsable y respaldo.
- Reejecutar correcciones y validaciones.
- No generar PES_READY hasta auditoria aprobada.
