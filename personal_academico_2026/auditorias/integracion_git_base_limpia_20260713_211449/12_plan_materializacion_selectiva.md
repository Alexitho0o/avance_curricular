# Plan de materializacion selectiva

Opcion recomendada: copia controlada por rutas explicitas desde el working tree/release vigente hacia una rama limpia creada desde la base confirmada.

No se recomienda cherry-pick completo porque el commit local ahead mezcla otros subproyectos. No se recomienda copiar `personal_academico_2026/` completo porque incluiria fuentes, normalizados, auditorias y salidas no versionables.

## Opciones evaluadas

- Copia por rutas desde working tree: recomendada con manifest de hashes y revision humana.
- `git restore --source=<commit> -- <rutas>`: aceptable solo con rutas explicitas y base limpia; requiere autorizacion posterior.
- Extraccion desde commit especifico: aceptable para archivos tracked, no cubre ignorados CSV/TSV.
- Parche por subproyecto: riesgo medio por incluir rutas no revisadas.
- Copia desde respaldo controlado: util si se materializa desde release, preservando hashes.
- Reconstruccion desde artefactos congelados: util para release publica, no para fuentes restringidas.

La opcion final debe preservar hashes, evitar otros subproyectos y mantener fuera raw/normalized/auditorias con PII.
