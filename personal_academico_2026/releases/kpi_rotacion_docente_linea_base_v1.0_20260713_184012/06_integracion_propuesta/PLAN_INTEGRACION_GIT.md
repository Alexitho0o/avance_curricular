# Plan de integracion Git

## Diagnostico actual

Rama: `backup/pre-sync-fix-20260410-avance`. HEAD: `5c5cc160cb64b1690dad871e722d52bd2bc5eadc`. Upstream: `origin/backup/pre-sync-fix-20260410-avance` en `6e15e063b85ee4b8b8d8937db5dc050a1833253b`. Relacion: ahead 1, behind 1. La rama observada es una rama backup y no debe resolverse automaticamente.

## Riesgos

- Integrar desde una rama backup puede mezclar trabajos de otros subproyectos.
- El commit local ahead toca multiples subproyectos y tambien rutas de `personal_academico_2026`.
- El commit remoto behind modifica `.gitignore`.
- No se debe hacer merge, rebase ni push sin autorizacion expresa.

## Candidatos a versionamiento

Versionables: documentos publicos de la release v1.0, controles JSON/CSV sin PII, planes de integracion y notas metodologicas.

Excluidos: fuentes gobernadas, normalizados restringidos, CSV/XLSX con claves documentales, bases longitudinales detalladas, artefactos con PII.

## Estrategia recomendada

1. Solicitar autorizacion para crear una rama nueva desde una base acordada.
2. Separar commits por tema: gobernanza, modulos desacoplados, documentacion metodologica, release v1.0 sin PII.
3. Verificar `git status`, `git diff`, `git check-ignore` y escaneo PII antes de cada commit.
4. Preparar PR en borrador con checklist de evidencia.
5. Definir rollback como cierre de PR o revert puntual, no `reset` destructivo.

No ejecutar ninguna accion Git hasta nueva autorizacion del usuario.

## CSV/TSV ignorados

La `.gitignore` global ignora `*.csv` y `*.tsv`. Algunos artefactos agregados de la release son publicables, pero no apareceran individualmente en `git status` hasta definir una excepcion o una estrategia autorizada de incorporacion. No ejecutar `git add -f` sin autorizacion expresa.
