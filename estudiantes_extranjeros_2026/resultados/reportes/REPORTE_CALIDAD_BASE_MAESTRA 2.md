# Reporte Calidad Base Maestra

Fecha de ejecucion: 2026-06-18 09:12:18

- Base validada: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025.csv`
- SHA-256 base: `8a592b3ba3001bab8f4fbee1ce90276f2b4479f39043338125cb69edbb044999`
- Registros validados: 30
- Hallazgos totales: 106
- Errores: 0
- Pendientes: 106
- Advertencias: 0

## Principales campos con hallazgos

- TIPO_RESIDENCIA_ESTUDIANTE: 30
- PAIS_DE_ORIGEN: 30
- PAIS_ESTUDIOS_SECUNDARIOS: 14
- ANIO_INGRESO_CARRERA_ORIGEN: 14
- SEM_INGRESO_CARRERA_ORIGEN: 14
- CODIGO_UNICO: 3
- NACIONALIDAD: 1

## Cobertura por variable

| Variable | Total | Completos | Pendientes | Conflictos | No aplica | Cobertura | Fuente principal | Accion |
|---|---:|---:|---:|---:|---:|---:|---|---|
| TIPO_DOCUMENTO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| NUM_DOCUMENTO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| DV | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| PRIMER_APELLIDO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| SEGUNDO_APELLIDO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| NOMBRES | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| SEXO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| FECHA_NACIMIENTO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| NACIONALIDAD | 30 | 29 | 1 | 0 | 0 | 96.7% | DatosAlumnos + gobernanza_nac.tsv | Gestionar/validar antes de carga final |
| TIPO_RESIDENCIA_ESTUDIANTE | 30 | 0 | 30 | 0 | 0 | 0.0% | No detectada | Gestionar/validar antes de carga final |
| PAIS_DE_ORIGEN | 30 | 0 | 30 | 0 | 0 | 0.0% | No detectada | Gestionar/validar antes de carga final |
| PAIS_ESTUDIOS_SECUNDARIOS | 30 | 16 | 14 | 0 | 0 | 53.3% | archivo_listo_para_sies normalizado | Gestionar/validar antes de carga final |
| CODIGO_UNICO | 30 | 27 | 0 | 3 | 0 | 90.0% | resultados/archivo_listo_para_sies.xlsx::ARCHIVO_LISTO_SUBIDA | Gestionar/validar antes de carga final |
| ANIO_INGRESO_CARRERA_ACTUAL | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| SEM_INGRESO_CARRERA_ACTUAL | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| ANIO_INGRESO_CARRERA_ORIGEN | 30 | 16 | 14 | 0 | 0 | 53.3% | archivo_listo_para_sies normalizado | Gestionar/validar antes de carga final |
| SEM_INGRESO_CARRERA_ORIGEN | 30 | 16 | 14 | 0 | 0 | 53.3% | archivo_listo_para_sies normalizado | Gestionar/validar antes de carga final |
| NOMBRE_UNIVERSIDAD_ORIGEN | 30 | 0 | 0 | 0 | 30 | 0.0% | DatosAlumnos | Sin accion |
| PAIS_UNIVERSIDAD_ORIGEN | 30 | 0 | 0 | 0 | 30 | 0.0% | No detectada | Sin accion |
| VIGENCIA | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |

## Nota

Esta validacion controla la base maestra de trabajo. No constituye autorizacion
para generar el CSV final de PES mientras existan pendientes o errores.
