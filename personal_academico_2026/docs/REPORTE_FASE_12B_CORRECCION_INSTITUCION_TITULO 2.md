# Reporte Fase 12B - Correccion institucion de titulo

Fecha/hora: 2026-06-12T17:23:54

## Objetivo
Regenerar la salida PES/SIES despues de la correccion confirmada en `Libro1.xlsx` para el registro `16749589-3`, sin editar manualmente el CSV final.

## Fuente corregida
- Fuente: `/Users/alexi/Desktop/Libro1.xlsx`
- Hash SHA256: `9e325bd86bf91de842c2e7c25af7b2f96ec4512ec648d86d765db9ba48bc67a6`
- Respaldo usuario informado: `/Users/alexi/Desktop/Libro1_ANTES_CORRECCION_TIARE_20260612_172005.xlsx`
- Copia controlada actualizada: `personal_academico_2026/insumos/preliminares/Libro1_base_preliminar_personal_academico_2026.xlsx`

## Respaldo antes de reemplazar
- Carpeta respaldo Fase 12B: `personal_academico_2026/resultados/backups/regeneracion_fase12b_20260612_172145/`
- Respaldo insumo previo: `personal_academico_2026/insumos/preliminares/backups/Libro1_base_preliminar_personal_academico_2026_PRE_FASE12B_20260612_172145.xlsx`
- Respaldo base previa: `personal_academico_2026/data/base_general/backups/base_general_personal_academico_en_institucion_PRE_REGENERACION_FASE12B_20260612_172145.tsv`

## Incorporacion y validacion
- Script incorporador: `personal_academico_2026/scripts/incorporar_base_preliminar_personal_academico_2026.py`
- Auditoria incorporacion: `personal_academico_2026/auditorias/base_preliminar/auditoria_incorporacion_base_preliminar_20260612_172153.csv`
- Filas base general: 202
- Columnas: 34
- Errores criticos validador: 0
- Advertencias: 606
- Estado validador: APROBADO_CON_ADVERTENCIAS
- Auditoria validacion: `personal_academico_2026/auditorias/auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_20260612_172207.csv`

## Validacion especifica RUT 16749589-3
- Persona: TIARE CARLA AVILA VERGARA
- Fila en base general: 197
- Campo: `NOMBRE_INSTITUCION_OBT_TITULO`
- Valor en base general: `UNIVERSIDAD ANDRÉS BELLO`
- Linea en CSV PES: 196
- Valor en CSV PES: `UNIVERSIDAD ANDRES BELLO`

## Exportacion PES
- Script exportador: `personal_academico_2026/scripts/exportar_personal_academico_2026.py`
- CSV repo: `personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv`
- CSV Escritorio: `/Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`
- Filas CSV: 202
- Columnas por fila: 34
- Delimitador: punto y coma
- Encoding: cp1252
- Encabezado: NO
- Exclusiones: 0
- Auditoria exportacion: `personal_academico_2026/auditorias/auditoria_exportacion_en_institucion_personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO_20260612_172218.csv`
- Auditoria transformaciones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_172218.csv`
- Auditoria exclusiones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_172218.csv`

## Validaciones PES
- Todas las filas tienen 34 columnas: OK
- Sin encabezado: OK
- Sin fechas ISO: OK
- Sin valores #N/A, #N/D, N/A o NA en campos estructurados cargables: OK
- Horas obligatorias no vacias: OK
- COMUNA_MAYOR_FUNCION no vacia: OK
- NOMBRE_TITULO_O_GRADO cumple A-Z y espacios: OK
- Sin institucion de titulo vacia cuando existe nivel, titulo, pais y fecha: OK

## Comparacion Fase 12B vs Fase 12
- Auditoria comparativa: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_comparacion_fase12b_vs_fase12.csv`
- Resumen comparativo Excel: `personal_academico_2026/auditorias/exportacion_controlada/resumen_cambios_fase12b_vs_fase12.xlsx`
- Base Fase 12: 202
- Base Fase 12B: 202
- CSV Fase 12: 202
- CSV Fase 12B: 202
- RUTs agregados: 0
- RUTs eliminados: 0
- RUTs modificados en CSV: 1
- Pendientes Fase 12: 0
- Pendientes Fase 12B: 0

## Excel KPI
- Excel repo: `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- Excel Escritorio: `/Users/alexi/Desktop/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- DETALLE_TRAZABILIDAD: 202
- BASE_KPI: 202
- Cargados: 202
- Pendientes: 0
- OpenPyXL: OK
- Tablas: 30
- Graficos: 41
- Pivots nativos: 0
- Vinculos externos: 0

## Confirmaciones
- No se modifico manualmente el CSV final.
- No se modifico el historico original.
- No se modifico el glosario original.
- No se hizo commit.
- No se hizo push.
