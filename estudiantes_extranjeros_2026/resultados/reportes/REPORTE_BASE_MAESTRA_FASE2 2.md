# Reporte Fase 2 - Base Maestra Extranjeros Regulares 2025

Fecha de ejecucion: 2026-06-18 09:11:18

## Universo preliminar

- Total candidatos: 30
- Extranjeros confirmados: 29
- Nacionalidad por confirmar: 1
- Posible intercambio: 0
- No corresponde: 0

## Base maestra

- Registros en base maestra: 30
- Registros que requieren gestion manual: 30
- Archivo: `data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025.csv`

## Codigo unico

{
  "RESUELTO_REGLA_INSTITUCIONAL": 14,
  "RESUELTO_UNIVOCO": 13,
  "AMBIGUO": 3
}

## Vigencia 2025

{
  "1": 30
}

La vigencia propuesta se basa en evidencia 2025 de DatosAlumnos; no se uso vigencia 2026.

## Respaldo

`estudiantes_extranjeros_2026/backups/pre_fase2_20260618_091118`

## Tabla de control por variable

| Variable | Total | Completos | Pendientes | Conflictos | No aplica | Cobertura | Fuente principal | Accion pendiente |
|---|---:|---:|---:|---:|---:|---:|---|---|
| TIPO_DOCUMENTO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| NUM_DOCUMENTO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| DV | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| PRIMER_APELLIDO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| SEGUNDO_APELLIDO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| NOMBRES | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| SEXO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| FECHA_NACIMIENTO | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| NACIONALIDAD | 30 | 29 | 1 | 0 | 0 | 96.7% | DatosAlumnos + gobernanza_nac.tsv | Gestion manual / resolver conflicto |
| TIPO_RESIDENCIA_ESTUDIANTE | 30 | 0 | 30 | 0 | 0 | 0.0% | No detectada | Gestion manual / resolver conflicto |
| PAIS_DE_ORIGEN | 30 | 0 | 30 | 0 | 0 | 0.0% | No detectada | Gestion manual / resolver conflicto |
| PAIS_ESTUDIOS_SECUNDARIOS | 30 | 16 | 14 | 0 | 0 | 53.3% | archivo_listo_para_sies normalizado | Gestion manual / resolver conflicto |
| CODIGO_UNICO | 30 | 27 | 0 | 3 | 0 | 90.0% | resultados/archivo_listo_para_sies.xlsx::ARCHIVO_LISTO_SUBIDA | Gestion manual / resolver conflicto |
| ANIO_INGRESO_CARRERA_ACTUAL | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| SEM_INGRESO_CARRERA_ACTUAL | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
| ANIO_INGRESO_CARRERA_ORIGEN | 30 | 16 | 14 | 0 | 0 | 53.3% | archivo_listo_para_sies normalizado | Gestion manual / resolver conflicto |
| SEM_INGRESO_CARRERA_ORIGEN | 30 | 16 | 14 | 0 | 0 | 53.3% | archivo_listo_para_sies normalizado | Gestion manual / resolver conflicto |
| NOMBRE_UNIVERSIDAD_ORIGEN | 30 | 0 | 0 | 0 | 30 | 0.0% | DatosAlumnos | Sin accion |
| PAIS_UNIVERSIDAD_ORIGEN | 30 | 0 | 0 | 0 | 30 | 0.0% | No detectada | Sin accion |
| VIGENCIA | 30 | 30 | 0 | 0 | 0 | 100.0% | DatosAlumnos | Sin accion |
