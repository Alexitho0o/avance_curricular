# Modulo CNED - Carga de Informacion

Este modulo separa el trabajo CNED del flujo estable de Matricula Unificada 2026 / PES_READY.

## Proposito

Centralizar insumos, scripts, auditorias, reportes y archivos de salida asociados a cargas CNED/INDICES, manteniendo trazabilidad independiente y evitando mezclar artefactos CNED con procesos MU2026.

## Separacion respecto de Matricula Unificada

El flujo MU2026/PES_READY es considerado estable y protegido. Los scripts, resultados y auditorias CNED deben vivir bajo `cned/` y no deben modificar, reemplazar ni depender de artefactos internos de MU2026 salvo que exista una interfaz documentada.

## Estructura

- `cned/data/input/`: insumos originales CNED.
- `cned/data/catalogos/`: catalogos y diccionarios controlados.
- `cned/data/processed/`: datos intermedios derivados.
- `cned/scripts/`: scripts operativos CNED.
- `cned/resultados/archivos_subida/`: archivos candidatos para carga.
- `cned/resultados/auditorias/`: auditorias tecnicas y conciliaciones.
- `cned/resultados/reportes/`: reportes Markdown, logs y controles.
- `cned/docs/`: documentacion y reglas.
- `cned/tests/`: pruebas y validaciones del modulo.

## Criterios de trazabilidad

Todo resultado CNED debe registrar fuente, fecha de generacion, regla aplicada, validaciones realizadas y dictamen. Los archivos finales deben tener version o timestamp para evitar sobrescrituras.

## Regla de no intervencion PES_READY

No se deben modificar scripts ni artefactos base PES_READY/MU2026 desde este modulo. Cualquier cambio sobre archivos protegidos debe ser tratado como alerta y revisado fuera del flujo CNED.

## Respaldo previo

Antes de reorganizar trabajo CNED existente, se debe respaldar el material previo en `archive/` con fecha de ejecucion. Si existe duda sobre pertenencia de un archivo a CNED o MU2026, no se mueve: se documenta para revision manual.

## Ubicacion esperada

Los insumos originales van en `cned/data/input/`; catalogos oficiales o complementarios en `cned/data/catalogos/`; salidas, auditorias y reportes en `cned/resultados/`.
