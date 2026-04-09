# Análisis dirigido de codigo_gobernanza_v2.py

## Contexto

- Proceso: Avance Curricular SIES 2026
- Repositorio: `/Users/alexi/Documents/GitHub/avance_curricular`
- Rama: `backup/pre-sync-fix-20260410-avance`
- Commit: `e79521cb6b8f72188ac0827bd511b30312137d08`
- Fecha: `2026-06-26T14:54:36.175548-04:00`
- Fuente: `/Users/alexi/Documents/GitHub/avance_curricular/codigo_gobernanza_v2.py`
- SHA-256: `40bfd42891e8eb593ebcfa8e3e480328c5174daa4d07526fe1b67f736de63023`
- Líneas: `5,313`

## Objetivo

Localizar exclusivamente la arquitectura ya implementada que puede reutilizarse
para Avance Curricular, evitando revisar o copiar linealmente el monolito.

## Resultados

- Funciones detectadas: 93
- Clases detectadas: 1
- Funciones con coincidencias relevantes: 65
- Coincidencias dirigidas: 1,110
- Fragmentos agrupados: 45
- Error AST: NO

## Archivos generados

1. `01_COINCIDENCIAS_DIRIGIDAS.tsv`
2. `02_FUNCIONES.tsv`
3. `03_CLASES.tsv`
4. `04_FUNCIONES_RELEVANTES.tsv`
5. `05_FRAGMENTOS_RELEVANTES.txt`
6. `06_REFERENCIAS_ARCHIVOS.txt`
7. `07_LLAMADAS_ENTRE_FUNCIONES.tsv`
8. `08_RESUMEN.json`

## Próxima acción

Revisar primero `04_FUNCIONES_RELEVANTES.tsv` y luego únicamente los fragmentos
de prioridad ALTA en `05_FRAGMENTOS_RELEVANTES.txt`.

No modificar el monolito hasta identificar:

- funciones transversales reutilizables;
- bloques exclusivos de Matrícula Unificada;
- bloques exclusivos de Estudiantes Extranjeros;
- punto de entrada y selección del proceso;
- contratos y salidas que deben adaptarse para Avance Curricular.
