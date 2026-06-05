# Reporte Fase 3 - Base Preliminar Personal Academico 2026

## Objetivo
Incorporar el Excel preliminar editable como RAW TSV, normalizarlo contra la estructura oficial de Personal Academico en la Institucion y alimentar una base general acumulable sin generar archivo final PES_READY.

## Resumen
- Fecha/hora: 2026-06-11T23:15:57
- Ruta Excel original: /Users/alexi/Desktop/Libro1.xlsx
- Ruta copia Excel controlada: personal_academico_2026/insumos/preliminares/Libro1_base_preliminar_personal_academico_2026.xlsx
- Hash SHA256 original: b50569b55424845de28ed541a2febbff256311ebcc35889344bc27efad4d7715
- Hash SHA256 copia: b50569b55424845de28ed541a2febbff256311ebcc35889344bc27efad4d7715
- Hoja seleccionada: Hoja1
- Total hojas detectadas: 1
- Total filas RAW: 192
- Total filas utiles: 191
- Total encabezados repetidos internos: 1
- Total columnas RAW: 34
- Total columnas oficiales: 34
- Total filas normalizadas: 190
- Total filas base general: 190
- Total filas incorporadas: 0
- Total filas actualizadas: 190
- Total posibles duplicados por documento: 0
- Total documentos con multiples funciones/programas: 0
- Total valores #N/D: 0
- Total valores #N/A: 26
- Total valores N/A o NA: 0
- Total valores NO APLICA: 760
- Total campos fecha no disponibles: 197
- Total fechas ambiguas: 0
- Total fechas invalidas reales: 0
- Total fechas futuras: 1
- Total horas con coma decimal: 0
- Total DV minuscula normalizada: 1
- Total campos obligatorios preventivos vacios: 0

## Rutas Generadas
- RAW TSV: personal_academico_2026/insumos/preliminares/base_preliminar_personal_academico_en_institucion_RAW.tsv
- Base normalizada: personal_academico_2026/data/base_general/base_preliminar_en_institucion_normalizada.tsv
- Base general: personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv
- Auditoria: personal_academico_2026/auditorias/base_preliminar/auditoria_incorporacion_base_preliminar_20260611_231557.csv

## Riesgos Detectados
- Existen valores #N/A preservados como datos fuente no disponibles.
- Existen fechas ambiguas o futuras que requieren revision.

## Proximos Pasos
- Revisar valores #N/D, fechas ambiguas/futuras y documentos repetidos.
- Confirmar criterios pendientes antes de exportacion final.
- Ejecutar exportacion final solo con auditoria aprobada y autorizacion explicita.

NO se genero archivo final PES_READY.

La base general sigue siendo preliminar y requiere revision antes de exportacion final.
