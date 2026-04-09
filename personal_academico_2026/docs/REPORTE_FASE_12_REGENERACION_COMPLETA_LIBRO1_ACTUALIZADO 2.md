# Reporte Fase 12 - Regeneracion completa Libro1 actualizado

Fecha/hora: 2026-06-12T16:59:27

## Objetivo
Regenerar el flujo de Personal Academico 2026 desde `/Users/alexi/Desktop/Libro1.xlsx`, manteniendo respaldo de la carga PES/SIES anterior aceptada y produciendo un nuevo CSV candidato para carga.

## Fuente actualizada
- Archivo fuente: `/Users/alexi/Desktop/Libro1.xlsx`
- Hash SHA256: `56aa6dc1f3cd69ec1bc3268e75024cc55179d28a731c68480de554eb83858c90`
- Copia controlada: `personal_academico_2026/insumos/preliminares/Libro1_base_preliminar_personal_academico_2026.xlsx`
- Hojas detectadas: 1
- Hoja usada: Hoja1
- Filas Excel: 203
- Columnas Excel: 34
- Filas utiles normalizadas: 202

## Respaldo previo
- Carpeta respaldo Fase 12: `personal_academico_2026/resultados/backups/regeneracion_fase12_20260612_165715/`
- Respaldo adicional insumo preliminar: `personal_academico_2026/insumos/preliminares/backups/Libro1_base_preliminar_personal_academico_2026_PRE_FASE12_20260612_165745.xlsx`
- Respaldo adicional base general: `personal_academico_2026/data/base_general/backups/base_general_personal_academico_en_institucion_PRE_REGENERACION_FASE12_20260612_165745.tsv`

## Incorporacion
- Script ejecutado: `personal_academico_2026/scripts/incorporar_base_preliminar_personal_academico_2026.py`
- RAW TSV regenerado: `personal_academico_2026/insumos/preliminares/base_preliminar_personal_academico_en_institucion_RAW.tsv`
- Base normalizada regenerada: `personal_academico_2026/data/base_general/base_preliminar_en_institucion_normalizada.tsv`
- Base general regenerada: `personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv`
- Auditoria incorporacion: `personal_academico_2026/auditorias/base_preliminar/auditoria_incorporacion_base_preliminar_20260612_165757.csv`
- Resumen JSON: `personal_academico_2026/auditorias/base_preliminar/resumen_ultima_incorporacion_base_preliminar.json`

## Validacion base general
- Filas base nueva: 202
- Columnas: 34
- Errores criticos: 0
- Advertencias: 606
- Duplicados criticos: 0
- Estado: APROBADO_CON_ADVERTENCIAS
- Auditoria validacion: `personal_academico_2026/auditorias/auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_20260612_165810.csv`

## Exportacion PES/SIES
- CSV repo: `personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv`
- CSV Escritorio: `/Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`
- Filas exportadas: 202
- Filas excluidas: 0
- Delimitador: punto y coma
- Encoding: cp1252
- Encabezado: NO
- Auditoria exportacion: `personal_academico_2026/auditorias/auditoria_exportacion_en_institucion_personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO_20260612_165822.csv`
- Auditoria transformaciones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_165822.csv`
- Auditoria exclusiones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_165822.csv`

## Comparacion con carga anterior aceptada
- Base anterior: 190 registros
- Base nueva: 202 registros
- PES anterior: 181 registros
- PES nuevo: 202 registros
- RUTs agregados: 16
- RUTs eliminados: 4
- RUTs modificados: 12
- Pendientes anteriores: 9
- Pendientes actuales: 0
- Pendientes resueltos: 9
- Pendientes nuevos: 0
- Auditoria comparativa: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_comparacion_fase12_vs_carga_anterior.csv`
- Resumen comparativo Excel: `personal_academico_2026/auditorias/exportacion_controlada/resumen_cambios_fase12_vs_carga_anterior.xlsx`

## Validacion CSV PES
- Existe en repo y Escritorio: OK
- Encoding cp1252: OK
- Delimitador punto y coma: OK
- Todas las filas tienen 34 columnas: OK
- Sin encabezado: OK
- Fechas no quedan en formato ISO YYYY-MM-DD: OK
- Sin valores #N/A, #N/D, N/A, NA en campos estructurados cargables: OK
- COMUNA_MAYOR_FUNCION no queda vacia: OK
- Horas obligatorias no quedan vacias: OK
- NOMBRE_TITULO_O_GRADO cumple letras A-Z y espacios: OK

## Excel KPI e historico
- Excel repo: `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- Excel Escritorio: `/Users/alexi/Desktop/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- DETALLE_TRAZABILIDAD: 202 registros
- BASE_KPI: 202 registros
- Cargados: 202
- Pendientes: 0
- Tablas Excel: 30
- Graficos: 41
- Pivots nativos: 0
- Vinculos externos: 0
- Continuidad institucional Codigo SIES 162: OK

## Confirmaciones
- No se modifico el historico original.
- No se modifico el glosario original.
- No se edito manualmente el CSV final.
- No se hizo commit.
- No se hizo push.

## Actualizacion Fase 12B
- Fecha/hora: 2026-06-12T17:23:54
- Motivo: correccion confirmada de `NOMBRE_INSTITUCION_OBT_TITULO` para `16749589-3`.
- Valor en base general: `UNIVERSIDAD ANDRÉS BELLO`.
- Valor en CSV PES: `UNIVERSIDAD ANDRES BELLO`.
- Filas base: 202.
- Filas CSV PES: 202.
- Pendientes: 0.
- Errores criticos: 0.
- Reporte especifico: `personal_academico_2026/docs/REPORTE_FASE_12B_CORRECCION_INSTITUCION_TITULO.md`.
