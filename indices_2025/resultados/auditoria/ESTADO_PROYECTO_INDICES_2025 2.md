# Estado Proyecto INDICES 2025

## FASE 0
estado: completada
artefactos principales:
- FASE0_DIAGNOSTICO_MANUAL_INDICES_2025.md
- fase0_indice_secciones_manual.json
- fase0_reglas_detectadas_manual.json

## FASE 1
estado: completada
artefactos principales:
- diccionario_evolucion_carreras.csv
- diccionario_evolucion_carreras.xlsx
- diccionario_evolucion_carreras.json
- reglas_csv_evolucion_carreras.yaml
observaciones: 47 campos, 30 reglas preliminares, 7 campos con revisión manual.

## FASE 2
estado: completada al finalizar esta ejecución
objetivo: arquitectura de esqueletos

## FASE 3
estado: completada
script principal:
- scripts/procesos/17_proceso_evolucion_carreras.py
artefactos generados:
- resultados/reportes_validacion/FASE3_VALIDACION_EVOLUCION_CARRERAS.md
- resultados/reportes_validacion/validacion_evolucion_carreras.xlsx
- resultados/reportes_validacion/validacion_evolucion_carreras.json
- resultados/logs/fase3_validacion_evolucion_carreras.log
- data/fixtures/plantilla_evolucion_carreras.csv
limitaciones:
- No se encontró CSV real en data/raw durante la ejecución inicial.
- Los 7 campos ambiguos heredados de FASE 1 quedan como revisión manual/no bloqueantes.
- Los catálogos externos CNED/SIES quedan como revisión manual hasta disponer de fuente verificable.
próxima fase:
- FASE 4 — Revisión del resultado del validador de Evolución de Carreras y decisión sobre correcciones, catálogos externos o implementación del siguiente proceso INDICES.

## Procesos detectados
| Proceso | Tipo | Estado | Script | YAML | Diccionario | Plantilla Excel | Plantilla Markdown |
|---|---|---|---|---|---|---|---|
| Identificación y casa central | manual | esqueleto | scripts/procesos/03_proceso_identificacion_casa_central.py | config/reglas/reglas_identificacion_casa_central.yaml | resultados/diccionarios/diccionario_identificacion_casa_central_esqueleto.json | resultados/plantillas_salida/plantilla_salida_identificacion_casa_central.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_identificacion_casa_central.md |
| Junta directiva | manual | esqueleto | scripts/procesos/04_proceso_junta_directiva.py | config/reglas/reglas_junta_directiva.yaml | resultados/diccionarios/diccionario_junta_directiva_esqueleto.json | resultados/plantillas_salida/plantilla_salida_junta_directiva.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_junta_directiva.md |
| Ayudas estudiantiles | manual | esqueleto | scripts/procesos/05_proceso_ayudas_estudiantiles.py | config/reglas/reglas_ayudas_estudiantiles.yaml | resultados/diccionarios/diccionario_ayudas_estudiantiles_esqueleto.json | resultados/plantillas_salida/plantilla_salida_ayudas_estudiantiles.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_ayudas_estudiantiles.md |
| Investigación | manual | esqueleto | scripts/procesos/06_proceso_investigacion.py | config/reglas/reglas_investigacion.yaml | resultados/diccionarios/diccionario_investigacion_esqueleto.json | resultados/plantillas_salida/plantilla_salida_investigacion.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_investigacion.md |
| Sede | manual | esqueleto | scripts/procesos/07_proceso_sede.py | config/reglas/reglas_sede.yaml | resultados/diccionarios/diccionario_sede_esqueleto.json | resultados/plantillas_salida/plantilla_salida_sede.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_sede.md |
| Campus | manual | esqueleto | scripts/procesos/08_proceso_campus.py | config/reglas/reglas_campus.yaml | resultados/diccionarios/diccionario_campus_esqueleto.json | resultados/plantillas_salida/plantilla_salida_campus.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_campus.md |
| Dependencias | manual | esqueleto | scripts/procesos/09_proceso_dependencias.py | config/reglas/reglas_dependencias.yaml | resultados/diccionarios/diccionario_dependencias_esqueleto.json | resultados/plantillas_salida/plantilla_salida_dependencias.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_dependencias.md |
| Docentes | mixto | esqueleto | scripts/procesos/10_proceso_docentes.py | config/reglas/reglas_docentes.yaml | resultados/diccionarios/diccionario_docentes_esqueleto.json | resultados/plantillas_salida/plantilla_salida_docentes.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_docentes.md |
| Origen estudiantes | manual | esqueleto | scripts/procesos/11_proceso_origen_estudiantes.py | config/reglas/reglas_origen_estudiantes.yaml | resultados/diccionarios/diccionario_origen_estudiantes_esqueleto.json | resultados/plantillas_salida/plantilla_salida_origen_estudiantes.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_origen_estudiantes.md |
| Inmueble | manual | esqueleto | scripts/procesos/12_proceso_inmueble.py | config/reglas/reglas_inmueble.yaml | resultados/diccionarios/diccionario_inmueble_esqueleto.json | resultados/plantillas_salida/plantilla_salida_inmueble.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_inmueble.md |
| Biblioteca | manual | esqueleto | scripts/procesos/13_proceso_biblioteca.py | config/reglas/reglas_biblioteca.yaml | resultados/diccionarios/diccionario_biblioteca_esqueleto.json | resultados/plantillas_salida/plantilla_salida_biblioteca.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_biblioteca.md |
| Laboratorios y talleres | manual | esqueleto | scripts/procesos/14_proceso_laboratorios_talleres.py | config/reglas/reglas_laboratorios_talleres.yaml | resultados/diccionarios/diccionario_laboratorios_talleres_esqueleto.json | resultados/plantillas_salida/plantilla_salida_laboratorios_talleres.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_laboratorios_talleres.md |
| Nuevos programas | manual | esqueleto | scripts/procesos/15_proceso_nuevos_programas.py | config/reglas/reglas_nuevos_programas.yaml | resultados/diccionarios/diccionario_nuevos_programas_esqueleto.json | resultados/plantillas_salida/plantilla_salida_nuevos_programas.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_nuevos_programas.md |
| Evolución de programas | manual | esqueleto | scripts/procesos/16_proceso_evolucion_programas.py | config/reglas/reglas_evolucion_programas.yaml | resultados/diccionarios/diccionario_evolucion_programas_esqueleto.json | resultados/plantillas_salida/plantilla_salida_evolucion_programas.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_evolucion_programas.md |
| Evolución de Carreras | csv | funcional FASE 3 | scripts/procesos/17_proceso_evolucion_carreras.py | config/reglas/reglas_evolucion_carreras.yaml | resultados/diccionarios/diccionario_evolucion_carreras_esqueleto.json | resultados/reportes_validacion/validacion_evolucion_carreras.xlsx | resultados/reportes_validacion/FASE3_VALIDACION_EVOLUCION_CARRERAS.md |
| Egresados y titulados | mixto | esqueleto | scripts/procesos/18_proceso_egresados_titulados.py | config/reglas/reglas_egresados_titulados.yaml | resultados/diccionarios/diccionario_egresados_titulados_esqueleto.json | resultados/plantillas_salida/plantilla_salida_egresados_titulados.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_egresados_titulados.md |
| Administración | manual | esqueleto | scripts/procesos/19_proceso_administracion.py | config/reglas/reglas_administracion.yaml | resultados/diccionarios/diccionario_administracion_esqueleto.json | resultados/plantillas_salida/plantilla_salida_administracion.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_administracion.md |
| Malla curricular | csv | esqueleto | scripts/procesos/20_proceso_malla_curricular.py | config/reglas/reglas_malla_curricular.yaml | resultados/diccionarios/diccionario_malla_curricular_esqueleto.json | resultados/plantillas_salida/plantilla_salida_malla_curricular.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_malla_curricular.md |
| Sobre la carga de datos | csv | esqueleto | scripts/procesos/21_proceso_sobre_carga_datos.py | config/reglas/reglas_sobre_carga_datos.yaml | resultados/diccionarios/diccionario_sobre_carga_datos_esqueleto.json | resultados/plantillas_salida/plantilla_salida_sobre_carga_datos.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_sobre_carga_datos.md |
| Errores en la carga | no_informado | esqueleto | scripts/procesos/22_proceso_errores_carga.py | config/reglas/reglas_errores_carga.yaml | resultados/diccionarios/diccionario_errores_carga_esqueleto.json | resultados/plantillas_salida/plantilla_salida_errores_carga.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_errores_carga.md |
| Obtención de reportes | no_informado | esqueleto | scripts/procesos/23_proceso_obtencion_reportes.py | config/reglas/reglas_obtencion_reportes.yaml | resultados/diccionarios/diccionario_obtencion_reportes_esqueleto.json | resultados/plantillas_salida/plantilla_salida_obtencion_reportes.xlsx | resultados/reportes_validacion/PLANTILLA_REPORTE_obtencion_reportes.md |

## Pendientes críticos
- Completar diccionarios técnicos específicos desde el manual.
- Confirmar estructuras reales de archivos CSV cuando existan fixtures institucionales.
- Mantener reglas ambiguas como no bloqueantes hasta revisión manual.
- Definir validadores solo con reglas explícitas del manual.

## Próxima fase sugerida
FASE 4 — Revisión del resultado del validador de Evolución de Carreras y decisión sobre correcciones, catálogos externos o implementación del siguiente proceso INDICES.
