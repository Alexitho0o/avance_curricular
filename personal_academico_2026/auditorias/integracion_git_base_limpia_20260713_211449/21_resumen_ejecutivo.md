# Resumen ejecutivo 3B-B

Dictamen: `BASE_LIMPIA_Y_ALCANCE_CONFIRMADOS_CON_OBSERVACIONES`.

## Base

- Rama observada: `backup/pre-sync-fix-20260410-avance`
- HEAD observado: `a95cb3ab42e936cce99c2db0a9572dae90e8eec6`
- Upstream: `origin/backup/pre-sync-fix-20260410-avance`
- HEAD upstream local: `6e15e063b85ee4b8b8d8937db5dc050a1833253b`
- Referencia remota local conocida: `6e15e063b85ee4b8b8d8937db5dc050a1833253b | origin/backup/pre-sync-fix-20260410-avance@{2026-07-06T13:16:52-04:00} | 2026-07-06T13:16:16-04:00 | update by push`
- Base recomendada: `6e15e063b85ee4b8b8d8937db5dc050a1833253b` (`origin/backup/pre-sync-fix-20260410-avance`)
- Base alternativa: `fe6fb6c549c5634a22eda2f8dcd5dbed6ed103e1` (`merge-base HEAD upstream`)
- Rama limpia propuesta: `feature/personal-academico-kpi-rotacion-v1`

## Alcance

- Archivos candidatos en plan: 91
- Archivos excluidos/no versionables segun 3B-A: 113
- Archivos pendientes segun 3B-A: 215
- Archivos ignorados de release: 5

## Ignorados

personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/INVENTARIO_FUENTES.csv; personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/00_control/MANIFEST_HITO_5.tsv; personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/02_resultados_publicables/KPI_ROTACION_HISTORICO_V1_0.csv; personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/04_evidencia_auditoria/MATRIZ_EVIDENCIA.csv; personal_academico_2026/releases/kpi_rotacion_docente_linea_base_v1.0_20260713_184012/06_integracion_propuesta/INVENTARIO_VERSIONAMIENTO.csv

Solucion recomendada: excepciones especificas por ruta para los cinco archivos publicos CSV/TSV. No modificar reglas globales `*.csv` ni `*.tsv`; no usar `git add -f` como mecanismo permanente.

## Materializacion

Opcion recomendada: rama limpia desde la base recomendada y traslado selectivo por rutas explicitas, con revision de hashes, PII y alcance por commit.

## Riesgos

Requiere fetch futuro autorizado antes de ejecutar; requiere autorizacion para `.gitignore`; no debe integrarse el commit local ahead completo.
