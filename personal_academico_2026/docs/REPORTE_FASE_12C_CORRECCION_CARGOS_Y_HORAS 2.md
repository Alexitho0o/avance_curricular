# Reporte Fase 12C - Correccion cargos y horas

Fecha/hora: 2026-06-12T17:40:29

## Fuente unica de verdad
- Archivo fuente usado: `/Users/alexi/Desktop/Libro1.xlsx`
- Hash antes de correccion: `9e325bd86bf91de842c2e7c25af7b2f96ec4512ec648d86d765db9ba48bc67a6`
- Hash despues de correccion: `f6110656880ba36ec35e15e680c94542f07f951ad37d84c42655b24be385e2b2`
- Respaldo tecnico creado antes de guardar: `/Users/alexi/Desktop/Libro1_ANTES_FASE12C_20260612_173521.xlsx`

No se consultaron respaldos historicos para completar campos. Las correcciones se aplicaron exclusivamente sobre el contenido vigente de `/Users/alexi/Desktop/Libro1.xlsx`.

## Correcciones aplicadas
- Total de cambios auditados: 8
- Correcciones de `CARGO_NORMALIZADO`: 6
- Correcciones de `NUM_HORAS_HONORARIO`: 2

### CARGO_NORMALIZADO
Regla aplicada: si `PRINCIPAL_CARGO_ACADEMICO` normalizado es exactamente `DOCENTE`, entonces `CARGO_NORMALIZADO = 9`.

RUTs corregidos:
- `16104597-7`
- `15064502-6`
- `11592558-K`
- `17041952-9`
- `15300890-6`
- `17041767-4`

### Horas honorarios
Correcciones puntuales, sin regla general de copia:
- `17610012-5`: `NUM_HORAS_HONORARIO = 18`
- `15356649-6`: `NUM_HORAS_HONORARIO = 24`

Auditoria de correcciones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_correcciones_fase12c.csv`

## Refuerzo de codigo
Se reforzaron las validaciones para:
- `CARGO_NORMALIZADO` entero entre 1 y 11.
- `PRINCIPAL_CARGO_ACADEMICO = DOCENTE` exige `CARGO_NORMALIZADO = 9`.
- Suma de `NUM_HORAS_PLANTA + NUM_HORAS_CONTRATA + NUM_HORAS_HONORARIOS` mayor que 0.
- Institucion de titulo vacia cuando existe bloque de titulo completo.
- Exportador bloquea controles criticos antes de escribir o copiar CSV PES.

## Regeneracion
- Incorporacion: `personal_academico_2026/auditorias/base_preliminar/auditoria_incorporacion_base_preliminar_20260612_173811.csv`
- Validacion base: `personal_academico_2026/auditorias/auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_20260612_173817.csv`
- Auditoria exportacion: `personal_academico_2026/auditorias/auditoria_exportacion_en_institucion_personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO_20260612_173915.csv`
- Auditoria transformaciones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_173915.csv`
- Auditoria exclusiones: `personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_173915.csv`

## Validaciones obligatorias
- `17610012-5`: cargo 9, total programa 18, honorarios 18, suma contractual 18.
- `15356649-6`: cargo 9, total programa 24, honorarios 24, suma contractual 24.
- `11592558-K`: cargo 9, suma contractual 18.
- `17041952-9`: cargo 9, suma contractual 20.
- `15300890-6`: cargo 9, suma contractual 20.
- `17041767-4`: cargo 9, suma contractual 20.

Controles globales:
- Todos los registros con `PRINCIPAL_CARGO_ACADEMICO = DOCENTE` tienen `CARGO_NORMALIZADO = 9`: OK.
- No existen codigos de cargo menores que 1 o mayores que 11: OK.
- Todas las sumas contractuales son mayores que 0: OK.
- Base general: 202 filas.
- CSV PES: 202 filas.
- CSV PES: 34 columnas exactas en todas las filas.
- Delimitador: punto y coma.
- Encoding: cp1252.
- Encabezado: NO.
- Pendientes: 0.
- Exclusiones: 0.
- Errores criticos: 0.

## Salidas
- CSV repo: `personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv`
- CSV Escritorio: `/Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`
- Excel repo: `personal_academico_2026/resultados/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`
- Excel Escritorio: `/Users/alexi/Desktop/Personal_Academico_2026_RESPALDO_CARGA_Y_KPI.xlsx`

## Confirmaciones
- No se modifico manualmente el CSV PES.
- No se hizo commit.
- No se hizo push.
