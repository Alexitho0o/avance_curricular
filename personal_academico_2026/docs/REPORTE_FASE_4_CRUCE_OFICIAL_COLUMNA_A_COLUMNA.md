# Reporte Fase 4 - Cruce Oficial Columna a Columna

## Objetivo
Cruzar la base general preliminar contra el formato oficial del instructivo y las estructuras oficiales CSV para determinar si esta lista para exportacion/carga PES.

## Fuentes
- personal_academico_2026/insumos/Personal Académico SIES - Instructivo 2026.txt
- personal_academico_2026/insumos/20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv
- personal_academico_2026/insumos/20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv
- personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv
- personal_academico_2026/auditorias/auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_20260611_233537.csv

## Metodologia
1. Lectura de estructura oficial En Institucion con delimitador `;`.
2. Lectura de base general TSV con delimitador tab.
3. Comparacion de cantidad, nombres y orden de columnas.
4. Cruce con ultima auditoria del validador para errores y advertencias por columna.
5. Clasificacion columna por columna.

## Scripts Ejecutados
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/cruzar_formato_oficial_personal_academico_2026.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Archivos Generados
- Matriz: personal_academico_2026/auditorias/matriz_cumplimiento_formato_oficial_en_institucion_20260611_233537.csv
- Dictamen: personal_academico_2026/docs/DICTAMEN_PRE_CARGA_PES_PERSONAL_ACADEMICO_EN_INSTITUCION.md
- Reporte: personal_academico_2026/docs/REPORTE_FASE_4_CRUCE_OFICIAL_COLUMNA_A_COLUMNA.md
- Bitacora: personal_academico_2026/bitacoras/BITACORA_FASE_4_CRUCE_OFICIAL_COLUMNA_A_COLUMNA.md

## Conteos Principales
- Columnas oficiales: 34
- Columnas base: 34
- Filas revisadas: 190
- Errores criticos: 1
- Advertencias: 569
- LISTA: 31
- LISTA_CON_ADVERTENCIAS: 2
- REQUIERE_CORRECCION: 1
- PENDIENTE_CONFIRMACION: 0

## Hallazgos Especificos
- fecha_futura: 1
- fecha_formato: 0
- fecha_no_disponible: 197
- campos obligatorios vacios: 1
- duplicados: 1
- RUT/DV: 1
- sexo: 0
- nacionalidad/pais: 0
- nivel formacion: 0
- cargo normalizado: 0
- horas: 1
- vigencia: 0

## Proximos Pasos
- Resolver la fecha futura mediante correccion manual respaldada en el archivo de control.
- Revisar fechas no disponibles y advertencias preventivas.
- Reejecutar validador y cruce oficial.
- Mantener exportador bloqueado hasta no tener errores criticos.

## Comandos Para Reproducir
```bash
python3 -m py_compile personal_academico_2026/scripts/*.py
python3 personal_academico_2026/scripts/cruzar_formato_oficial_personal_academico_2026.py
python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab
```

No se genero PES_READY.
