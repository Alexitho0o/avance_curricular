# Reporte Fase 7 - Reglas PES Horas y Especialidad

## Objetivo
Corregir en codigo las reglas pendientes detectadas por PES/SIES y regenerar el archivo final candidato sin parches manuales sobre el CSV.

## Reglas Incorporadas
- Textos PES con caracteres seguros: mayusculas, sin tildes, `Ñ -> N`, `Ü -> U`, sin caracteres raros.
- `NUM_HORAS_PLANTA`, `NUM_HORAS_CONTRATA` y `NUM_HORAS_HONORARIOS` no salen nulos: valores vacios o no cargables se exportan como `0`.
- Horas numericas se reducen a maximo 2 decimales.
- Si `NIVEL_FORMACION_ACADEMICO` es 5, 6, 7 u 8, se limpia todo el bloque de especialidad.
- Si falta `NIVEL_FORMACION_ESPECIALIDAD`, se limpian campos dependientes de especialidad para no inventar el nivel.
- Si `FECHA_OBTENCION_ESPECIALIDAD` no es cargable, se limpia en exportacion.
- La deteccion/exclusion de registros no cargables ocurre despues de transformar.

## Resultado
- Salida modulo: personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv
- Copia Escritorio: /Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv
- Filas exportadas: 181
- Filas excluidas: 8
- Horas nulas completadas con 0: 330
- Bloques de especialidad limpiados: 567
- Fechas de especialidad limpiadas: 0
- Textos normalizados: 184
- Delimitador: punto_coma
- Encoding: cp1252
- Encabezado: NO

## Motivos de Exclusion
- FECHA_OBT_TIT_O_GRADO=VALOR_NO_CARGABLE: 7
- NIVEL_FORMACION_ACADEMICO=VALOR_NO_CARGABLE: 5
- PAIS_OBTENCION_TIT_O_GRADO=VALOR_NO_CARGABLE: 7

## Auditorias
- Transformaciones: personal_academico_2026/auditorias/exportacion_controlada/auditoria_transformaciones_pes_fase7_20260612_005154.csv
- Exclusiones: personal_academico_2026/auditorias/exportacion_controlada/auditoria_exclusiones_pes_fase7_20260612_005154.csv

La base general original no fue modificada. Toda transformacion ocurre solo en exportacion.
