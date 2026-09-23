# PENDIENTE_EVALUAR_RECTIFICACION_MU2026_C09_02_C09_03

Estado: **PENDIENTE_DECISION_INSTITUCIONAL** · Registrado: 2026-09-23 · No forma parte del requerimiento Bettersoft.

En este gate no se rectificó nada, no se prepararon cargas correctivas y no se modificó Matrícula Unificada 2026.

## Universo afectado (MU 2026 pregrado cargada en PES, 08-05 y 11-05-2026)

| Resolución | Registros | Detalle |
|---|---|---|
| C09-02 Forma de ingreso 3 por cambio de jornada | 95 con FOR 3 | 46 con el mismo COD_CAR y otra jornada en MU 2025; 37 con el mismo COD_CAR y la misma jornada; 2 con otro COD_CAR; 10 sin registro 2025. Los de mismo COD_CAR tenían FOR 1 en 2025. |
| C09-03 Forma de ingreso 2 por nombre "CONTINUIDAD" | 382 con FOR 2 | 164 con FOR 11 en 2025 en el mismo programa; 4 con FOR 1; 214 sin el mismo programa en 2025. |

## Naturaleza del problema

- C09-02: la regla oficial de Cambio Interno exige una carrera nueva (código de carrera distinto al del año anterior). Un cambio de jornada no lo prueba.
- C09-03: la forma 2 exige haber cursado un plan común o bachillerato. El nombre del programa no lo prueba, y la forma de ingreso del mismo estudiante al mismo programa cambió entre 2025 y 2026 sin un hecho que lo explique.

## Evidencia

- `REPORTE_CIERRE_GATE09_UPLUS_SIES_2026.md`, secciones C y D.
- `resultados/AUDITORIA_GATE09_CONTRADICCIONES_UPLUS_SIES_2026.xlsx`, hojas 01 y 02.
- `resultados/gate09/METRICAS_EVIDENCIA_GATE09.json` (claves `ct02` y `ct03`).
- Archivos cargados en PES, solo locales: `.local_restricted/requerimiento_bettersoft_uplus_2026/gate09_evidencia/matricula_unificada_2026/`.

## Impacto posible

Indicadores de cohorte, cambio interno y continuidad, y asignación o renovación de beneficios que dependen de la forma de ingreso y del año de origen. El impacto real depende de la regla de beneficios aplicable, que no se evaluó.

## Decisión institucional requerida

Definir si se solicita a SIES la corrección histórica de estos registros y con qué forma de ingreso correcta para cada uno. Esto requiere reconstruir los hechos de cada caso, no solo reemplazar un código. Según el Instructivo AC 2026, la corrección histórica se solicita formalmente a SIES y se hace efectiva en 2027.
