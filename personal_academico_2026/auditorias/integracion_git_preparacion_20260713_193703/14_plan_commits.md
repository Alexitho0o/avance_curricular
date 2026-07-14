# Plan de commits

No ejecutar. Rutas exactas propuestas para una fase posterior con autorizacion.

## C01 - Gobernanza y configuracion sin fuentes

- Mensaje: `chore(pa2026): registra configuracion gobernada sin fuentes`
- Riesgo: MEDIO
- Requiere excepcion ignore: no
- Contiene PII: no detectado; pendiente revision humana
- Archivos incluidos: 7
- Excluidos: data/raw_restricted; data/normalized_restricted; auditorias completas
- Rollback: revertir commit C01

Rutas:

- `personal_academico_2026/data/manifests/config_fuentes_aprobadas.json`
- `personal_academico_2026/data/manifests/fuentes_personal_academico.csv`
- `personal_academico_2026/data/manifests/fuentes_personal_academico.json`
- `personal_academico_2026/data/manifests/hashes_fuentes.csv`
- `personal_academico_2026/data/manifests/homologacion_columnas.json`
- `personal_academico_2026/data/manifests/schema_homologado.json`
- `personal_academico_2026/data/manifests/versiones_fuentes.json`

## C02 - Modulos desacoplados y KPI

- Mensaje: `feat(pa2026): agrega modulos desacoplados de rotacion historica`
- Riesgo: MEDIO
- Requiere excepcion ignore: no
- Contiene PII: no
- Archivos incluidos: 66
- Excluidos: fuentes; outputs; auditorias
- Rollback: revertir commit C02

Rutas:

- `personal_academico_2026/gobernanza_historica/__init__.py`
- `personal_academico_2026/gobernanza_historica/__main__.py`
- `personal_academico_2026/gobernanza_historica/__pycache__/__init__.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/__main__.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/cli.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/configuracion.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/congelamiento.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/descubrimiento_fuentes.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/homologacion.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/integridad.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/inventario.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/manifiestos.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/__pycache__/normalizacion.cpython-314.pyc`
- `personal_academico_2026/gobernanza_historica/cli.py`
- `personal_academico_2026/gobernanza_historica/configuracion.py`
- `personal_academico_2026/gobernanza_historica/congelamiento.py`
- `personal_academico_2026/gobernanza_historica/descubrimiento_fuentes.py`
- `personal_academico_2026/gobernanza_historica/homologacion.py`
- `personal_academico_2026/gobernanza_historica/integridad.py`
- `personal_academico_2026/gobernanza_historica/inventario.py`
- `personal_academico_2026/gobernanza_historica/manifiestos.py`
- `personal_academico_2026/gobernanza_historica/normalizacion.py`
- `personal_academico_2026/kpi_rotacion/__init__.py`
- `personal_academico_2026/kpi_rotacion/__main__.py`
- `personal_academico_2026/kpi_rotacion/__pycache__/__init__.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/__main__.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/auditoria.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/cli.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/comparacion.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/config.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/exportacion.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/historico_consolidacion.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/historico_exportacion.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/historico_fuentes.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/kpis.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/lectura.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/__pycache__/validacion.cpython-314.pyc`
- `personal_academico_2026/kpi_rotacion/auditoria.py`
- `personal_academico_2026/kpi_rotacion/cli.py`
- `personal_academico_2026/kpi_rotacion/comparacion.py`
- `personal_academico_2026/kpi_rotacion/config.py`
- `personal_academico_2026/kpi_rotacion/exportacion.py`
- `personal_academico_2026/kpi_rotacion/historico_consolidacion.py`
- `personal_academico_2026/kpi_rotacion/historico_exportacion.py`
- `personal_academico_2026/kpi_rotacion/historico_fuentes.py`
- `personal_academico_2026/kpi_rotacion/kpis.py`
- `personal_academico_2026/kpi_rotacion/lectura.py`
- `personal_academico_2026/kpi_rotacion/validacion.py`
- `personal_academico_2026/reconstruccion_rotacion/__init__.py`
- `personal_academico_2026/reconstruccion_rotacion/__main__.py`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/__init__.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/__main__.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/carga.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/cli.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/configuracion.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/exportacion.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/reconstruccion.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/utilidades.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/__pycache__/validaciones.cpython-314.pyc`
- `personal_academico_2026/reconstruccion_rotacion/carga.py`
- `personal_academico_2026/reconstruccion_rotacion/cli.py`
- `personal_academico_2026/reconstruccion_rotacion/configuracion.py`
- `personal_academico_2026/reconstruccion_rotacion/exportacion.py`
- `personal_academico_2026/reconstruccion_rotacion/reconstruccion.py`
- `personal_academico_2026/reconstruccion_rotacion/utilidades.py`
- `personal_academico_2026/reconstruccion_rotacion/validaciones.py`

## C03 - Pruebas y validadores

- Mensaje: `test(pa2026): cubre formula oficial de rotacion SIES`
- Riesgo: BAJO
- Requiere excepcion ignore: no
- Contiene PII: no
- Archivos incluidos: 0
- Excluidos: fixtures con datos reales
- Rollback: revertir commit C03

Rutas:


## C04 - Documentacion metodologica existente del subproyecto

- Mensaje: `docs(pa2026): documenta metodologia y decisiones PES`
- Riesgo: MEDIO
- Requiere excepcion ignore: no
- Contiene PII: no detectado en plan
- Archivos incluidos: 4
- Excluidos: documentos con personas individuales si aparecen
- Rollback: revertir commit C04

Rutas:

- `personal_academico_2026/bitacoras/BITACORA_FASE_12B_CORRECCION_INSTITUCION_TITULO 2.md`
- `personal_academico_2026/docs/REPORTE_FASE_12B_CORRECCION_INSTITUCION_TITULO 2.md`
- `personal_academico_2026/docs/REPORTE_FASE_12C_CORRECCION_CARGOS_Y_HORAS 2.md`
- `personal_academico_2026/docs/REPORTE_FASE_12_REGENERACION_COMPLETA_LIBRO1_ACTUALIZADO 2.md`

## C05 - Release publica v1.0

- Mensaje: `docs(pa2026): publica release metodologica v1.0 sin PII`
- Riesgo: MEDIO
- Requiere excepcion ignore: si para CSV/TSV publicables
- Contiene PII: no
- Archivos incluidos: 28
- Excluidos: 03_resultados_internos_restringidos; fuentes; auditorias con PII
- Rollback: revertir commit C05

Rutas:

- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/CONTROL_NO_MODIFICACION.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/DIAGNOSTICO_GIT.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/DICTAMEN_CONGELAMIENTO.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/INVENTARIO_FUENTES.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/MANIFEST.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/MANIFEST_HITO_5.tsv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/RESUMEN_FINAL_GENERACION.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/SHA256SUMS.txt`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/VERSION.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/CHANGELOG.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/COMPARABILIDAD.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/FUENTES_Y_TRAZABILIDAD.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/GLOSARIO.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/LIMITACIONES_Y_ADVERTENCIAS.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/METODOLOGIA.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/RELEASE_NOTES.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/KPI_ROTACION_HISTORICO_V1_0.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/KPI_ROTACION_HISTORICO_V1_0.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/NOTA_METODOLOGICA_PUBLICACION.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/RESUMEN_EJECUTIVO.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/04_evidencia_auditoria/INDICE_AUDITORIAS.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/04_evidencia_auditoria/MATRIZ_EVIDENCIA.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/05_pruebas/RESULTADO_PRUEBAS_TECNICAS.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/05_pruebas/VALIDACION_RELEASE.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/05_pruebas/VALIDACION_RELEASE.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/INVENTARIO_VERSIONAMIENTO.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/PLAN_INTEGRACION_GIT.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/PROPUESTA_COMMITS.md`

## C06 - Registro de hito e integracion propuesta

- Mensaje: `docs(pa2026): agrega preparacion forense de integracion Git`
- Riesgo: BAJO
- Requiere excepcion ignore: si para CSV si se versiona 13_plan_commits.csv
- Contiene PII: no
- Archivos incluidos: 6
- Excluidos: inventario completo si se decide no versionarlo
- Rollback: revertir commit C06

Rutas:

- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/20_resumen_ejecutivo.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/12_estrategia_recomendada.json`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/13_plan_commits.csv`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/14_plan_commits.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/16_plan_publicacion.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/17_riesgos_y_controles.md`
