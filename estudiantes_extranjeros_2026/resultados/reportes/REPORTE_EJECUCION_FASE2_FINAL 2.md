# Reporte Ejecutivo Fase 2 - Extranjeros Regulares 2025

Fecha de cierre: 2026-06-18 09:13:41

## Resultado operativo

- Universo preliminar: 30 registros.
- Clasificacion universo: {'EXTRANJERO_CONFIRMADO': 29, 'NACIONALIDAD_POR_CONFIRMAR': 1}.
- Base maestra de trabajo: 30 registros, todos en estado pendiente de gestion manual por campos no inferibles.
- Codigo unico: {'RESUELTO_REGLA_INSTITUCIONAL': 14, 'RESUELTO_UNIVOCO': 13, 'AMBIGUO': 3}.
- Validacion base maestra: 106 hallazgos, todos clasificados como {'PENDIENTE': 106}.
- Prueba de incorporacion sin respuestas: {'SIN_RESPUESTA': 150}.
- Archivos en resultados/archivos_subida: 0.

## Archivos clave

- Base maestra: `estudiantes_extranjeros_2026/data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025.csv`
- Planilla gestion: `estudiantes_extranjeros_2026/resultados/archivos_gestion/PLANILLA_GESTION_DOCENCIA_EXTRANJEROS_2025.xlsx`
- Validacion: `estudiantes_extranjeros_2026/resultados/auditorias/VALIDACION_BASE_MAESTRA.csv`
- Manifiesto final: `estudiantes_extranjeros_2026/resultados/auditorias/MANIFIESTO_ARCHIVOS_FASE2_FINAL.csv`

## Cobertura por variable

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

## Estado git al cierre

```text
?? estudiantes_extranjeros_2026/backups/pre_fase2_20260618_091118/
?? estudiantes_extranjeros_2026/resultados/reportes/PRUEBA_REPORTE_INCORPORACION_RESPUESTAS_SIN_RESPUESTAS.md
?? estudiantes_extranjeros_2026/resultados/reportes/REPORTE_BASE_MAESTRA_FASE2.md
?? estudiantes_extranjeros_2026/resultados/reportes/REPORTE_CALIDAD_BASE_MAESTRA.md
?? estudiantes_extranjeros_2026/resultados/reportes/REPORTE_EJECUCION_FASE2_FINAL.md
?? estudiantes_extranjeros_2026/scripts/generar_base_maestra_fase2.py
?? estudiantes_extranjeros_2026/scripts/incorporar_respuestas_docencia.py
?? estudiantes_extranjeros_2026/scripts/validar_base_extranjeros_regulares.py
```
