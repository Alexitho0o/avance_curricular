# Reporte Fase 3B - Depuracion de Fechas y Valores No Disponibles

## Objetivo
Distinguir tecnicamente fechas invalidas reales, fechas futuras, fechas ambiguas, campos de fecha vacios y valores no disponibles preservados como `#N/A`, `#N/D`, `N/A`, `NA` o `NO APLICA`.

## Resumen
- Fecha/hora: 2026-06-11T23:15:57
- Archivo revisado: personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv
- Cantidad de filas: 190
- Campos de fecha revisados: FECHA_NACIMIENTO, FECHA_OBTENCION_ESPECIALIDAD, FECHA_OBT_TIT_O_GRADO
- Total campos de fecha revisados: 570
- Total FECHA_OK: 372
- Total FECHA_VACIA: 0
- Total FECHA_NO_DISPONIBLE: 197
- Total FECHA_AMBIGUA: 0
- Total FECHA_INVALIDA: 0
- Total FECHA_FUTURA: 1
- Total #N/A: 26
- Total #N/D: 0
- Total N/A o NA: 0
- Total NO APLICA: 760
- Diagnostico CSV: personal_academico_2026/auditorias/base_preliminar/diagnostico_fechas_base_general_20260611_231557.csv

## Columnas Con Mas Problemas
- FECHA_OBTENCION_ESPECIALIDAD: 190
- FECHA_OBT_TIT_O_GRADO: 8

## Muestra de Registros Problematicos
- Fila 2 | Documento R|10063280|2 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 3 | Documento R|10393519|9 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 4 | Documento R|10536500|4 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 5 | Documento R|10727793|5 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 6 | Documento R|11250569|5 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 7 | Documento R|11481000|2 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 8 | Documento R|11613889|1 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 9 | Documento R|11640980|1 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 10 | Documento R|11944423|3 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 11 | Documento R|12141132|6 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 12 | Documento R|12240733|0 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 13 | Documento R|12534768|1 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 14 | Documento R|12632439|1 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 15 | Documento R|12721395|K | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 16 | Documento R|12816751|K | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 17 | Documento R|13021689|7 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 18 | Documento R|13056867|K | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 19 | Documento R|13191365|6 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 20 | Documento R|13255405|6 | FECHA_OBTENCION_ESPECIALIDAD | `NO APLICA` | FECHA_NO_DISPONIBLE | Confirmar dato fuente o respaldar que no aplica; no inventar fecha.
- Fila 20 | Documento R|13255405|6 | FECHA_OBT_TIT_O_GRADO | `2027-11-29` | FECHA_FUTURA | Revisar contra documento fuente; confirmar si corresponde o corregir con respaldo.

## Criterio Aplicado
- `#N/A` no fue corregido.
- `#N/A` se preservo como dato fuente no disponible.
- Los valores no disponibles se clasifican como `FECHA_NO_DISPONIBLE` con fuente `VALIDACION_TECNICA_PREVENTIVA`.
- La base sigue preliminar.
- No se genero PES_READY.
