# Plan de publicacion futura

No ejecutar en esta fase.

1. Autorizacion humana para refrescar referencias remotas y confirmar rama base.
2. Autorizacion humana para crear rama limpia desde base confirmada. Base candidata actual: `6e15e063b85ee4b8b8d8937db5dc050a1833253b` (`origin/backup/pre-sync-fix-20260410-avance`).
3. Aplicar estrategia E: reconstruir commits selectivos usando rutas explicitas del plan.
4. Validar PII, release, hashes, compileall y harness antes de cada commit.
5. Crear commits pequenos C01-C06, sin incluir otros subproyectos.
6. Revision local completa: `git status`, `git diff`, `git log`, validaciones de release.
7. Autorizacion humana para publicar la rama.
8. Autorizacion humana para abrir pull request.
9. Revision institucional y tecnica.
10. Autorizacion humana para tag/release Git si procede.
11. Merge solo tras aprobacion; no se asume merge ni rebase automatico.
