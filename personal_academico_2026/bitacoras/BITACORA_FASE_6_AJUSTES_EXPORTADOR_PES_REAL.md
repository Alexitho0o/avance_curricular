# Bitacora Fase 6 - Ajustes Exportador PES Real

- Fecha/hora: 2026-06-12T00:51:54
- Rama: feature/personal-academico-base-preliminar-2026

## Archivos Creados
- personal_academico_2026/docs/REPORTE_FASE_6_AJUSTES_EXPORTADOR_PES_REAL.md
- personal_academico_2026/bitacoras/BITACORA_FASE_6_AJUSTES_EXPORTADOR_PES_REAL.md
- personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_005154.csv
- personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_005154.csv
- personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv

## Archivos Modificados
- personal_academico_2026/scripts/exportar_personal_academico_2026.py
- personal_academico_2026/scripts/transformaciones_pes_personal_academico_2026.py

## Comandos Ejecutados
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/candidatos_exportacion/base_general_en_institucion_SIN_PENDIENTE_FECHA_FUTURA_20260611_234029.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/candidatos_exportacion/base_general_en_institucion_SIN_PENDIENTE_FECHA_FUTURA_20260611_234029.tsv --output personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv --permitir-exportacion-final true --delimitador-salida punto_coma --encoding-salida cp1252 --formato-fecha-pes true --normalizar-texto-pes true --completar-comuna-mayor true --excluir-registros-no-cargables true --copiar-escritorio true --desktop-output /Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`

## Resultado
- Filas exportadas: 181
- Filas excluidas: 8
- Comunas completadas: 169
- Fechas transformadas: 371

## Pendientes
- Registrar en codigo cualquier nueva correccion detectada por PES/SIES.
- Mantener la base general intacta salvo correcciones manuales autorizadas.
