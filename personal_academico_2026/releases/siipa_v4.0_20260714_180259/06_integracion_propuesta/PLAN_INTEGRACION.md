# Plan de integración Git propuesto

No ejecutar automáticamente.

1. Revisar esta release y confirmar que los artefactos `VERSIONABLE_SIN_PII` son suficientes.
2. Excluir el Excel completo de Git porque contiene RAW y datos cruzados individuales.
3. Versionar el generador, documentación, KPI agregados, validaciones y evidencia saneada.
4. No modificar `.gitignore` salvo excepciones exactas, documentadas y aprobadas para artefactos publicables de esta release.
5. La integración del PR #12 incluyó excepciones acotadas para CSV publicables; no repetir ni ampliar esas reglas sin una nueva revisión.
6. No usar `git add -f`, `git add .` ni `git add -A`.
7. Excluir siempre Excel completo, RAW, normalizados, PES, auditorías privadas y cualquier artefacto con datos personales.
