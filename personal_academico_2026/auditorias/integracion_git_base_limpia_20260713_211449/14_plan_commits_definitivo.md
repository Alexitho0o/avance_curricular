# Plan definitivo de commits

## C01 - feat(personal-academico): agrega gobernanza historica sin fuentes

- Proposito: Versionar configuracion/homologacion segura sin raw ni normalizados
- Archivos incluidos: 2
- Modifica .gitignore: no
- Dependencias: revision de archivos pendientes de gobernanza
- Rollback: revert C01

Rutas:
- `personal_academico_2026/data/manifests/homologacion_columnas.json`
- `personal_academico_2026/data/manifests/schema_homologado.json`

## C02 - chore(personal-academico): permite versionar artefactos publicos csv tsv de release

- Proposito: Agregar excepciones minimas de .gitignore para cinco archivos publicos
- Archivos incluidos: 1
- Modifica .gitignore: si
- Dependencias: AUTORIZACION_USUARIO_REQUERIDA para modificar .gitignore
- Rollback: revert C02

Rutas:
- `.gitignore`

## C03 - feat(personal-academico): agrega modulos desacoplados de rotacion historica

- Proposito: Versionar codigo modular aprobado
- Archivos incluidos: 33
- Modifica .gitignore: no
- Dependencias: C01
- Rollback: revert C03

Rutas:
- `personal_academico_2026/gobernanza_historica/__init__.py`
- `personal_academico_2026/gobernanza_historica/__main__.py`
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
- `personal_academico_2026/reconstruccion_rotacion/carga.py`
- `personal_academico_2026/reconstruccion_rotacion/cli.py`
- `personal_academico_2026/reconstruccion_rotacion/configuracion.py`
- `personal_academico_2026/reconstruccion_rotacion/exportacion.py`
- `personal_academico_2026/reconstruccion_rotacion/reconstruccion.py`
- `personal_academico_2026/reconstruccion_rotacion/utilidades.py`
- `personal_academico_2026/reconstruccion_rotacion/validaciones.py`

## C04 - test(personal-academico): cubre formula oficial de rotacion docente

- Proposito: Versionar prueba unitaria/harness relacionado
- Archivos incluidos: 0
- Modifica .gitignore: no
- Dependencias: C03
- Rollback: revert C04

Rutas:

## C05 - docs(personal-academico): documenta metodologia de linea base rotacion v1

- Proposito: Versionar documentacion metodologica publica
- Archivos incluidos: 9
- Modifica .gitignore: no
- Dependencias: C01
- Rollback: revert C05

Rutas:
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/CHANGELOG.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/COMPARABILIDAD.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/FUENTES_Y_TRAZABILIDAD.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/GLOSARIO.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/LIMITACIONES_Y_ADVERTENCIAS.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/METODOLOGIA.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/01_documentacion/RELEASE_NOTES.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/NOTA_METODOLOGICA_PUBLICACION.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/RESUMEN_EJECUTIVO.md`

## C06 - docs(personal-academico): agrega release publica v1 de KPI rotacion

- Proposito: Versionar release publica v1.0 sin referencia restringida
- Archivos incluidos: 19
- Modifica .gitignore: no
- Dependencias: C02 y C05
- Rollback: revert C06

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
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/KPI_ROTACION_HISTORICO_V1_0.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/KPI_ROTACION_HISTORICO_V1_0.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/04_evidencia_auditoria/INDICE_AUDITORIAS.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/04_evidencia_auditoria/MATRIZ_EVIDENCIA.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/05_pruebas/RESULTADO_PRUEBAS_TECNICAS.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/05_pruebas/VALIDACION_RELEASE.json`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/05_pruebas/VALIDACION_RELEASE.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/INVENTARIO_VERSIONAMIENTO.csv`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/PLAN_INTEGRACION_GIT.md`
- `personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/PROPUESTA_COMMITS.md`

## C07 - docs(personal-academico): registra preparacion de integracion limpia

- Proposito: Versionar registros publicos 3B-A/3B-B seleccionados
- Archivos incluidos: 28
- Modifica .gitignore: posible si se decide incluir CSV de auditoria
- Dependencias: C01-C06
- Rollback: revert C07

Rutas:
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/02_estado_base_git.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/04_evaluacion_bases.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/05_base_recomendada.json`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/08_alcance_versionable.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/10_parche_gitignore_propuesto.txt`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/11_diseno_rama_limpia.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/12_plan_materializacion_selectiva.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/14_plan_commits_definitivo.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/15_simulacion_integracion.sh.txt`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/16_validaciones.json`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/17_validaciones.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/18_riesgos_y_autorizaciones.md`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/19_manifest.json`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/20_sha256_manifest.txt`
- `personal_academico_2026/auditorias/integracion_git_base_limpia_20260713_211449/21_resumen_ejecutivo.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/02_estado_git.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/04_comparacion_commits_hermanos.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/09_validacion_release.json`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/10_validacion_release.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/11_evaluacion_estrategias_git.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/12_estrategia_recomendada.json`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/14_plan_commits.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/15_simulacion_staging.sh.txt`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/16_plan_publicacion.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/17_riesgos_y_controles.md`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/18_manifest.json`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/19_sha256_manifest.txt`
- `personal_academico_2026/auditorias/integracion_git_preparacion_20260713_193703/20_resumen_ejecutivo.md`
