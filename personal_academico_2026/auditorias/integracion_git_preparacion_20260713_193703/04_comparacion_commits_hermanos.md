# Comparacion de commits hermanos

Los commits 2A, 2B, 3A informado y HEAD actual comparten asunto y fecha, pero no se consideran equivalentes por eso. La comparacion usa rutas y hashes de blobs.

## FASE_2A_INFORMADO_vs_FASE_2B_INFORMADO

- Rutas diferentes: 15
- Categorias: `{"personal_academico_2026": 15}`
- Blobs cambiados: 0
- Solo A: 0 | Solo B: 15

## FASE_2A_INFORMADO_vs_HEAD_ACTUAL_OBSERVADO

- Rutas diferentes: 52
- Categorias: `{"personal_academico_2026": 52}`
- Blobs cambiados: 0
- Solo A: 0 | Solo B: 52

## FASE_2B_INFORMADO_vs_HEAD_ACTUAL_OBSERVADO

- Rutas diferentes: 37
- Categorias: `{"personal_academico_2026": 37}`
- Blobs cambiados: 0
- Solo A: 0 | Solo B: 37

## HEAD_3A_INFORMADO_vs_HEAD_ACTUAL_OBSERVADO

- Rutas diferentes: 24
- Categorias: `{"personal_academico_2026": 24}`
- Blobs cambiados: 0
- Solo A: 0 | Solo B: 24

## HEAD_ACTUAL_OBSERVADO_vs_UPSTREAM_LOCAL

- Rutas diferentes: 519
- Categorias: `{"avance_curricular_2026": 312, "estudiantes_extranjeros_2026": 72, "infraestructura_recursos_educacionales_2026": 26, "personal_academico_2026": 107, "scripts": 1, "tests": 1}`
- Blobs cambiados: 1
- Solo A: 509 | Solo B: 9

## UPSTREAM_LOCAL_vs_PADRE_COMUN_INFORMADO

- Rutas diferentes: 1
- Categorias: `{".gitignore": 1}`
- Blobs cambiados: 1
- Solo A: 0 | Solo B: 0

## Interpretacion

Los commits observados son reconstrucciones alternativas o commits regenerados con padre comun, no una cadena lineal unica. El HEAD actual observado agrega contenido de release frente al HEAD 3A informado y el commit actual mezcla multiples subproyectos. Por ello no se recomienda cherry-pick completo ni integracion desde la rama backup actual.
