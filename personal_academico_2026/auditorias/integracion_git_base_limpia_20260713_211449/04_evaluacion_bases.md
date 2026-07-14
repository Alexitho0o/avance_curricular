# Evaluacion de bases

## A - origin/backup/pre-sync-fix-20260410-avance

- Hash: `6e15e063b85ee4b8b8d8937db5dc050a1833253b`
- Fecha: 2026-07-06T13:16:16-04:00
- Asunto: chore(git): excluye diagnostico mayor a 100MB
- Diff personal_academico_2026 vs HEAD: 121 rutas
- Diff total repo vs HEAD: 533 rutas
- Otros subproyectos en diff: 411
- Riesgo: MEDIO
- Recomendacion: BASE_RECOMENDADA
- Ventajas: base remota local de la rama observada; incluye commit remoto behind de .gitignore
- Riesgos: referencia remota local puede estar desactualizada; requiere fetch futuro autorizado

## B - main

- Hash: `435f7be59fc509b792e46c28f139fa32313f9516`
- Fecha: 2026-05-07T13:27:53-04:00
- Asunto: chore: remove generated MU2026 audit artifacts
- Diff personal_academico_2026 vs HEAD: 126 rutas
- Diff total repo vs HEAD: 2293 rutas
- Otros subproyectos en diff: 2161
- Riesgo: ALTO
- Recomendacion: NO_RECOMENDADA_SIN_CONFIRMACION_RAMA_PRINCIPAL
- Ventajas: requiere confirmacion institucional
- Riesgos: rama principal no confirmada para este subproyecto

## C - NO_EXISTE

- Hash: ``
- Fecha: 
- Asunto: 
- Diff personal_academico_2026 vs HEAD: None rutas
- Diff total repo vs HEAD: None rutas
- Otros subproyectos en diff: 0
- Riesgo: ALTO
- Recomendacion: NO_RECOMENDADA
- Ventajas: requiere confirmacion institucional
- Riesgos: rama principal no confirmada para este subproyecto

## D - merge-base HEAD upstream

- Hash: `fe6fb6c549c5634a22eda2f8dcd5dbed6ed103e1`
- Fecha: 2026-07-06T11:58:19-04:00
- Asunto: chore(git): refuerza exclusiones de temporales
- Diff personal_academico_2026 vs HEAD: 121 rutas
- Diff total repo vs HEAD: 534 rutas
- Otros subproyectos en diff: 412
- Riesgo: MEDIO_ALTO
- Recomendacion: BASE_ALTERNATIVA
- Ventajas: aisla del commit remoto behind
- Riesgos: puede omitir commit remoto behind

## E - backup/antes_limpieza_100mb_20260706_131221

- Hash: `fe6fb6c549c5634a22eda2f8dcd5dbed6ed103e1`
- Fecha: 2026-07-06T11:58:19-04:00
- Asunto: chore(git): refuerza exclusiones de temporales
- Diff personal_academico_2026 vs HEAD: 121 rutas
- Diff total repo vs HEAD: 534 rutas
- Otros subproyectos en diff: 412
- Riesgo: ALTO
- Recomendacion: NO_RECOMENDADA
- Ventajas: requiere confirmacion institucional
- Riesgos: rama principal no confirmada para este subproyecto
