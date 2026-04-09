# Bitacora Fase 12B - Correccion institucion de titulo

Fecha/hora: 2026-06-12T17:23:54

## Rama
`feature/personal-academico-base-preliminar-2026`

## Comandos revisados
- Se revisaron `REPORTE_FASE_12_REGENERACION_COMPLETA_LIBRO1_ACTUALIZADO.md` y `BITACORA_FASE_12_REGENERACION_COMPLETA_LIBRO1_ACTUALIZADO.md`.
- Se reutilizaron los comandos reales de Fase 12 para incorporacion, validacion, exportacion PES y generacion de Excel KPI.

## Comandos ejecutados
- `shasum -a 256 /Users/alexi/Desktop/Libro1.xlsx`
- `python personal_academico_2026/scripts/incorporar_base_preliminar_personal_academico_2026.py`
- `python personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv --permitir-exportacion-final true --delimitador-salida punto_coma --encoding-salida cp1252 --formato-fecha-pes true --normalizar-texto-pes true --completar-comuna-mayor true --excluir-registros-no-cargables true --copiar-escritorio true --desktop-output /Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`
- `python personal_academico_2026/scripts/generar_respaldo_carga_kpi_personal_academico_2026.py`
- Validaciones Python de base general, CSV PES, RUT corregido y Excel KPI.

## Respaldo
- Salidas previas respaldadas en `personal_academico_2026/resultados/backups/regeneracion_fase12b_20260612_172145/`.
- Ingreso preliminar anterior respaldado en `personal_academico_2026/insumos/preliminares/backups/Libro1_base_preliminar_personal_academico_2026_PRE_FASE12B_20260612_172145.xlsx`.
- Base general anterior respaldada en `personal_academico_2026/data/base_general/backups/base_general_personal_academico_en_institucion_PRE_REGENERACION_FASE12B_20260612_172145.tsv`.

## Resultado RUT 16749589-3
- Persona: TIARE CARLA AVILA VERGARA.
- Base general: `UNIVERSIDAD ANDRÉS BELLO`.
- CSV PES linea 196: `UNIVERSIDAD ANDRES BELLO`.

## Resultado general
- Filas base: 202.
- Filas CSV PES: 202.
- Pendientes: 0.
- Errores criticos: 0.
- Exclusiones: 0.
- CSV Escritorio reemplazado: `/Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`.
- Excel Escritorio reemplazado: `/Users/alexi/Desktop/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`.

## Confirmaciones
- No se edito manualmente el CSV final.
- No se hizo commit.
- No se hizo push.
