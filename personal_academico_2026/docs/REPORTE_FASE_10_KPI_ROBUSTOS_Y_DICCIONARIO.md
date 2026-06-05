# Reporte Fase 10 - KPIs robustos y diccionario metodologico

Fecha/hora: 2026-06-12T11:20:08

## Objetivo
Robustecer el Excel de respaldo de carga PES/SIES con KPIs ejecutivos ampliados, tablas resumen trazables y una hoja DICCIONARIO_KPI con definiciones cualitativas y cuantitativas.

## Archivos revisados
- Base original: `personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv`
- CSV cargado PES/SIES: `personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv`
- Auditorias de exportacion: `personal_academico_2026/auditorias/exportacion_controlada`

## Resultado
- Excel repo: `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- Excel Escritorio: `/Users/alexi/Desktop/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- Hojas: DETALLE_TRAZABILIDAD, RESUMEN_EJECUTIVO, BASE_KPI, DICCIONARIO_KPI, TABLAS_RESUMEN
- Registros base: 190
- Cargados PES/SIES: 181
- Pendientes/no cargados: 9
- Porcentaje carga efectiva: 95.3%
- Horas totales: 3339.75
- JCE total estimada: 75.90
- Promedio horas: 17.58
- Mediana horas: 15.00
- Edad promedio: 41.4
- Años promedio desde titulo: 9.5
- Magister: 41
- Doctorado: 0
- KPIs documentados: 54

## Metodologia
Los indicadores de `RESUMEN_EJECUTIVO` referencian `TABLAS_RESUMEN`, y esas tablas se calculan desde `BASE_KPI`. `BASE_KPI` conserva una fila por registro original y contiene los campos derivados usados para indicadores de edad, formacion, dedicacion, JCE, carga PES y pendientes.

## Confirmaciones
- No se modifico la base general original.
- No se modifico el CSV cargado a PES/SIES.
- No se ingresaron KPIs como numeros sueltos en el resumen ejecutivo; se usan formulas hacia tablas resumen calculadas.
