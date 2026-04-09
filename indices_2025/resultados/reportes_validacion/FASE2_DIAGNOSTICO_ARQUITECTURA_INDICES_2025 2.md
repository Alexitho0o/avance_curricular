# FASE 2 — Diagnóstico de arquitectura INDICES 2025

## 1. Fuente oficial utilizada
- Manual: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/docs/Manual_INDICES_2025.txt`
- Fecha/hora de ejecución: `2026-05-18T20:52:35-04:00`

## 2. Artefactos previos revisados
- `manual`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/docs/Manual_INDICES_2025.txt`
- `fase0_secciones`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/fase0_indice_secciones_manual.json`
- `fase1_diccionario_evolucion_carreras`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_evolucion_carreras.json`
- `procesos_json`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/procesos/procesos_indices_2025.json`
- `procesos_csv`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/procesos/procesos_indices_2025.csv`
- `estado_proyecto`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/auditoria/ESTADO_PROYECTO_INDICES_2025.md`
- `bitacora_decisiones`: existe — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/auditoria/BITACORA_DECISIONES_INDICES_2025.md`

## 3. Procesos detectados
| ID | Nombre | Tipo | Estado | Pendientes |
|---|---|---|---|---:|
| identificacion_casa_central | Identificación y casa central | manual | esqueleto | 0 |
| junta_directiva | Junta directiva | manual | esqueleto | 0 |
| ayudas_estudiantiles | Ayudas estudiantiles | manual | esqueleto | 0 |
| investigacion | Investigación | manual | esqueleto | 0 |
| sede | Sede | manual | esqueleto | 0 |
| campus | Campus | manual | esqueleto | 0 |
| dependencias | Dependencias | manual | esqueleto | 0 |
| docentes | Docentes | mixto | esqueleto | 0 |
| origen_estudiantes | Origen estudiantes | manual | esqueleto | 0 |
| inmueble | Inmueble | manual | esqueleto | 0 |
| biblioteca | Biblioteca | manual | esqueleto | 0 |
| laboratorios_talleres | Laboratorios y talleres | manual | esqueleto | 0 |
| nuevos_programas | Nuevos programas | manual | esqueleto | 0 |
| evolucion_programas | Evolución de programas | manual | esqueleto | 0 |
| evolucion_carreras | Evolución de Carreras | csv | esqueleto | 0 |
| egresados_titulados | Egresados y titulados | mixto | esqueleto | 0 |
| administracion | Administración | manual | esqueleto | 0 |
| malla_curricular | Malla curricular | csv | esqueleto | 0 |
| sobre_carga_datos | Sobre la carga de datos | csv | esqueleto | 0 |
| errores_carga | Errores en la carga | no_informado | esqueleto | 0 |
| obtencion_reportes | Obtención de reportes | no_informado | esqueleto | 0 |

## 4. Estructura de carpetas
- `docs`: OK
- `config/procesos`: OK
- `config/reglas`: OK
- `config/catalogos`: OK
- `scripts/core`: OK
- `scripts/procesos`: OK
- `scripts/validadores`: OK
- `scripts/utilidades`: OK
- `data/raw`: OK
- `data/interim`: OK
- `data/processed`: OK
- `data/fixtures`: OK
- `resultados/reportes_validacion`: OK
- `resultados/diccionarios`: OK
- `resultados/logs`: OK
- `resultados/plantillas_salida`: OK
- `resultados/auditoria`: OK

## 5. Scripts esqueleto creados
- `identificacion_casa_central`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/03_proceso_identificacion_casa_central.py`
- `junta_directiva`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/04_proceso_junta_directiva.py`
- `ayudas_estudiantiles`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/05_proceso_ayudas_estudiantiles.py`
- `investigacion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/06_proceso_investigacion.py`
- `sede`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/07_proceso_sede.py`
- `campus`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/08_proceso_campus.py`
- `dependencias`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/09_proceso_dependencias.py`
- `docentes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/10_proceso_docentes.py`
- `origen_estudiantes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/11_proceso_origen_estudiantes.py`
- `inmueble`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/12_proceso_inmueble.py`
- `biblioteca`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/13_proceso_biblioteca.py`
- `laboratorios_talleres`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/14_proceso_laboratorios_talleres.py`
- `nuevos_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/15_proceso_nuevos_programas.py`
- `evolucion_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/16_proceso_evolucion_programas.py`
- `evolucion_carreras`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/17_proceso_evolucion_carreras.py`
- `egresados_titulados`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/18_proceso_egresados_titulados.py`
- `administracion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/19_proceso_administracion.py`
- `malla_curricular`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/20_proceso_malla_curricular.py`
- `sobre_carga_datos`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/21_proceso_sobre_carga_datos.py`
- `errores_carga`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/22_proceso_errores_carga.py`
- `obtencion_reportes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/scripts/procesos/23_proceso_obtencion_reportes.py`

## 6. Configuraciones YAML creadas
- `identificacion_casa_central`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_identificacion_casa_central.yaml`
- `junta_directiva`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_junta_directiva.yaml`
- `ayudas_estudiantiles`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_ayudas_estudiantiles.yaml`
- `investigacion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_investigacion.yaml`
- `sede`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_sede.yaml`
- `campus`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_campus.yaml`
- `dependencias`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_dependencias.yaml`
- `docentes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_docentes.yaml`
- `origen_estudiantes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_origen_estudiantes.yaml`
- `inmueble`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_inmueble.yaml`
- `biblioteca`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_biblioteca.yaml`
- `laboratorios_talleres`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_laboratorios_talleres.yaml`
- `nuevos_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_nuevos_programas.yaml`
- `evolucion_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_evolucion_programas.yaml`
- `evolucion_carreras`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_evolucion_carreras.yaml`
- `egresados_titulados`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_egresados_titulados.yaml`
- `administracion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_administracion.yaml`
- `malla_curricular`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_malla_curricular.yaml`
- `sobre_carga_datos`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_sobre_carga_datos.yaml`
- `errores_carga`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_errores_carga.yaml`
- `obtencion_reportes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/config/reglas/reglas_obtencion_reportes.yaml`

## 7. Diccionarios esqueleto creados
- `identificacion_casa_central`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_identificacion_casa_central_esqueleto.json`
- `junta_directiva`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_junta_directiva_esqueleto.json`
- `ayudas_estudiantiles`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_ayudas_estudiantiles_esqueleto.json`
- `investigacion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_investigacion_esqueleto.json`
- `sede`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_sede_esqueleto.json`
- `campus`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_campus_esqueleto.json`
- `dependencias`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_dependencias_esqueleto.json`
- `docentes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_docentes_esqueleto.json`
- `origen_estudiantes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_origen_estudiantes_esqueleto.json`
- `inmueble`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_inmueble_esqueleto.json`
- `biblioteca`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_biblioteca_esqueleto.json`
- `laboratorios_talleres`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_laboratorios_talleres_esqueleto.json`
- `nuevos_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_nuevos_programas_esqueleto.json`
- `evolucion_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_evolucion_programas_esqueleto.json`
- `evolucion_carreras`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_evolucion_carreras_esqueleto.json`
- `egresados_titulados`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_egresados_titulados_esqueleto.json`
- `administracion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_administracion_esqueleto.json`
- `malla_curricular`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_malla_curricular_esqueleto.json`
- `sobre_carga_datos`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_sobre_carga_datos_esqueleto.json`
- `errores_carga`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_errores_carga_esqueleto.json`
- `obtencion_reportes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/diccionario_obtencion_reportes_esqueleto.json`

## 8. Plantillas Markdown creadas
- `identificacion_casa_central`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_identificacion_casa_central.md`
- `junta_directiva`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_junta_directiva.md`
- `ayudas_estudiantiles`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_ayudas_estudiantiles.md`
- `investigacion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_investigacion.md`
- `sede`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_sede.md`
- `campus`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_campus.md`
- `dependencias`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_dependencias.md`
- `docentes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_docentes.md`
- `origen_estudiantes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_origen_estudiantes.md`
- `inmueble`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_inmueble.md`
- `biblioteca`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_biblioteca.md`
- `laboratorios_talleres`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_laboratorios_talleres.md`
- `nuevos_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_nuevos_programas.md`
- `evolucion_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_evolucion_programas.md`
- `evolucion_carreras`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_evolucion_carreras.md`
- `egresados_titulados`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_egresados_titulados.md`
- `administracion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_administracion.md`
- `malla_curricular`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_malla_curricular.md`
- `sobre_carga_datos`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_sobre_carga_datos.md`
- `errores_carga`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_errores_carga.md`
- `obtencion_reportes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/PLANTILLA_REPORTE_obtencion_reportes.md`

## 9. Plantillas Excel creadas
- `identificacion_casa_central`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_identificacion_casa_central.xlsx`
- `junta_directiva`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_junta_directiva.xlsx`
- `ayudas_estudiantiles`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_ayudas_estudiantiles.xlsx`
- `investigacion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_investigacion.xlsx`
- `sede`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_sede.xlsx`
- `campus`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_campus.xlsx`
- `dependencias`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_dependencias.xlsx`
- `docentes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_docentes.xlsx`
- `origen_estudiantes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_origen_estudiantes.xlsx`
- `inmueble`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_inmueble.xlsx`
- `biblioteca`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_biblioteca.xlsx`
- `laboratorios_talleres`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_laboratorios_talleres.xlsx`
- `nuevos_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_nuevos_programas.xlsx`
- `evolucion_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_evolucion_programas.xlsx`
- `evolucion_carreras`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_evolucion_carreras.xlsx`
- `egresados_titulados`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_egresados_titulados.xlsx`
- `administracion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_administracion.xlsx`
- `malla_curricular`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_malla_curricular.xlsx`
- `sobre_carga_datos`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_sobre_carga_datos.xlsx`
- `errores_carga`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_errores_carga.xlsx`
- `obtencion_reportes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/plantillas_salida/plantilla_salida_obtencion_reportes.xlsx`

## 10. Fixtures creados
- `identificacion_casa_central`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_identificacion_casa_central.csv`
- `junta_directiva`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_junta_directiva.csv`
- `ayudas_estudiantiles`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_ayudas_estudiantiles.csv`
- `investigacion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_investigacion.csv`
- `sede`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_sede.csv`
- `campus`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_campus.csv`
- `dependencias`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_dependencias.csv`
- `docentes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_docentes.csv`
- `origen_estudiantes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_origen_estudiantes.csv`
- `inmueble`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_inmueble.csv`
- `biblioteca`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_biblioteca.csv`
- `laboratorios_talleres`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_laboratorios_talleres.csv`
- `nuevos_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_nuevos_programas.csv`
- `evolucion_programas`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_evolucion_programas.csv`
- `evolucion_carreras`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_evolucion_carreras.csv`
- `egresados_titulados`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_egresados_titulados.csv`
- `administracion`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_administracion.csv`
- `malla_curricular`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_malla_curricular.csv`
- `sobre_carga_datos`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_sobre_carga_datos.csv`
- `errores_carga`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_errores_carga.csv`
- `obtencion_reportes`: OK — `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/data/fixtures/fixture_obtencion_reportes.csv`

## 11. Estado por proceso
| Proceso | Script | YAML | Diccionario | Excel | Markdown | Fixture |
|---|---|---|---|---|---|---|
| identificacion_casa_central | OK | OK | OK | OK | OK | OK |
| junta_directiva | OK | OK | OK | OK | OK | OK |
| ayudas_estudiantiles | OK | OK | OK | OK | OK | OK |
| investigacion | OK | OK | OK | OK | OK | OK |
| sede | OK | OK | OK | OK | OK | OK |
| campus | OK | OK | OK | OK | OK | OK |
| dependencias | OK | OK | OK | OK | OK | OK |
| docentes | OK | OK | OK | OK | OK | OK |
| origen_estudiantes | OK | OK | OK | OK | OK | OK |
| inmueble | OK | OK | OK | OK | OK | OK |
| biblioteca | OK | OK | OK | OK | OK | OK |
| laboratorios_talleres | OK | OK | OK | OK | OK | OK |
| nuevos_programas | OK | OK | OK | OK | OK | OK |
| evolucion_programas | OK | OK | OK | OK | OK | OK |
| evolucion_carreras | OK | OK | OK | OK | OK | OK |
| egresados_titulados | OK | OK | OK | OK | OK | OK |
| administracion | OK | OK | OK | OK | OK | OK |
| malla_curricular | OK | OK | OK | OK | OK | OK |
| sobre_carga_datos | OK | OK | OK | OK | OK | OK |
| errores_carga | OK | OK | OK | OK | OK | OK |
| obtencion_reportes | OK | OK | OK | OK | OK | OK |

## 12. Riesgos técnicos
- Los procesos quedan en estado esqueleto; no validan datos reales todavía.
- Las reglas específicas no se completaron salvo referencias ya disponibles en FASE 1 para Evolución de Carreras.
- Las tablas del manual provienen de texto extraído y pueden requerir revisión manual antes de reglas bloqueantes.
- Los fixtures creados son vacíos; se necesitan archivos reales de prueba para FASE 3.
- Los catálogos CNED/SIES mencionados por el manual quedan como dependencia a confirmar, no como reglas implementadas.

## 13. Recomendación de FASE 3
FASE 3 — Implementación del primer validador funcional, comenzando por CSV Evolución de Carreras, usando el diccionario técnico de FASE 1 y la arquitectura de esqueletos de FASE 2.

## 14. Punto exacto para reanudar
PUNTO EXACTO PARA REANUDAR:
FASE 3 — Implementación del primer validador funcional, comenzando por CSV Evolución de Carreras, usando el diccionario técnico de FASE 1 y la arquitectura de esqueletos de FASE 2.
