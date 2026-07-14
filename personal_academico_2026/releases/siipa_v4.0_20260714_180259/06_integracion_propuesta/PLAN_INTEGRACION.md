# Plan de integración Git propuesto

No ejecutar automáticamente.

1. Revisar esta release y confirmar que los artefactos `VERSIONABLE_SIN_PII` son suficientes.
2. Excluir el Excel completo de Git porque contiene RAW y datos cruzados individuales.
3. Versionar el generador, documentación, KPI agregados, validaciones y evidencia saneada.
4. No modificar `.gitignore` sin autorización.
5. No usar `git add -f`.
