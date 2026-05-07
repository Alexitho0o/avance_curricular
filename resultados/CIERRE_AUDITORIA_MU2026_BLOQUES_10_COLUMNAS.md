# Cierre Auditoría End to End · Matrícula Unificada 2026

Fecha: 2026-05-07

## Archivo auditado principal

`resultados/matricula_unificada_2026_pregrado.csv`

## Resultado general

La auditoría end to end por bloques de 10 columnas finalizó sin errores estructurales ni de catálogo en el archivo principal de carga de Matrícula Unificada 2026.

## Validación de estructura

- Archivo CSV delimitado por punto y coma `;`.
- Archivo sin encabezado.
- Total real de filas: 3442.
- Total de columnas: 32.
- Estructura compatible con la carga de pregrado definida en el Manual de Proceso Matrícula Unificada 2026.

## Resultados por bloque

| Bloque | Columnas | Campos revisados | Resultado |
|---|---:|---|---|
| Bloque 1 | 01–10 | Identificación, nombre, sexo, fecha nacimiento, nacionalidad y país estudios secundarios | OK · 0 errores |
| Bloque 2 | 11–20 | Sede, carrera, modalidad, jornada, versión, forma de ingreso, años y semestres de ingreso | OK · 0 errores |
| Bloque 3 | 21–30 | Asignaturas, promedios, nivel académico, Fondo Solidario, suspensiones y fecha matrícula | OK · 0 errores |
| Bloque 4 | 31–32 | Reincorporación y vigencia | OK · 0 errores |

## Hallazgos relevantes

- El archivo `matricula_unificada_2026_pregrado.csv` debe leerse sin encabezado.
- Si se lee con encabezado automático, pandas interpreta la primera fila como nombres de columnas y muestra 3441 filas.
- Al leerlo correctamente sin encabezado, contiene 3442 filas y 32 columnas.
- Esta diferencia no corresponde a pérdida de registros, sino al formato esperado para carga oficial.

## Distribución final de VIG

| VIG | Registros |
|---:|---:|
| 0 | 97 |
| 1 | 3345 |

## Reincorporación

| REINCORPORACION | Registros |
|---:|---:|
| 0 | 3442 |

## Conclusión

El archivo `matricula_unificada_2026_pregrado.csv` queda validado estructuralmente para carga, de acuerdo con la estructura de pregrado del Manual de Proceso Matrícula Unificada 2026.

No se detectaron errores en los 32 campos auditados por bloques.
