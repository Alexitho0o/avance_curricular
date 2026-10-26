# Fase 2 — extensión incremental de la regla anual

**B/C — Resultado:** 14 observaciones pendientes de 6 personas tienen un puente explícito en `2025_carga!J/BU`. Ocho cumplen la regla anual vigente; cinco ya estaban verificadas en fase 1 y **tres son adicionales**. No se modificó el diccionario activo.

| Carrera UMAS (B) | Previas (B/C) | Nuevas (B/C) | Siguen pendientes (E) |
|---|---:|---:|---:|
| IADM | 0 | 0 | 3 |
| TAMD | 3 | 2 | 0 |
| TLOG | 0 | 0 | 3 |
| TPAS | 2 | 1 | 0 |

**B/C — Códigos recuperables:** TPAS → I162S2C57J4V1; TAMD → I162S2C78J2V1. Las tres nuevas observaciones corresponden al período nativo 1 de 2025: una TPAS y dos TAMD. No añaden cierres a T2/T3 de V17.

**C — Método:** búsqueda solo en 3.049 pendientes; puente explícito J/RUT ↔ BU/N_DOC; MU2025 tipo P y documento exacto; familia compatible; código anual único; contexto DA exacto; exclusividad de persona/expediente. Se recorrieron PROMEDIOS (70.000 filas) y DA (15.185) para comprobar exclusividad del lote, sin reconsultar los 21.725 resueltos. BV y DV se conservan diferentes; no se inventó DV. No se extrapola el puente a otros años.

**E — Seis contextos TLOG/IADM:** el código anual pertenece a jornada distinta del contexto. Tres por carrera, períodos nativos 1–3 de 2025. El puente resuelve identidad, no fecha de cambio ni versión de la nueva jornada. Se conserva el diagnóstico previo; no hay un cierre adicional respaldado por esta regla.

**C/E — Hitos:** H1 búsqueda incremental completada; H2 ocho atribuciones verificadas y operaciones preparadas; H3 residual delimitado sin repetir búsquedas agotadas. Los restantes 3.035 no tienen este puente anual aplicable. Las 16 propuestas internas y 12 criterios T2 de fase 1 no fueron aprobados por ejecutar esta fase y siguen separados. No se extendieron aprobaciones nominativas.

**C — Escenario de incorporación, todavía no aplicado:** histórico 21.733/24.774 con código y 3.041 pendientes; V17 2.755/2.854 con código y 99 pendientes. La edición activa conserva 21.725 y 3.049, respectivamente. No confundir candidatura con cierre productivo.

**C — QA:** hashes del diccionario, puntero, V17 y tres cambios previos conservados; ocho IDs únicos; tres nuevos sin duplicar cinco previos; cambios candidatos limitados a atribución/evidencia. Bases, denominadores, tasas, Excel y HEAD sin cambios. Sin commit ni push. QA integral de una edición candidata corresponde a fase 3.

**C — Reproducción:** scripts y detalle individual en `/Users/alexi/.local/share/ipss/fase2_historico_20261025/`, fuera de Git, incluidos en el manifiesto mediante rutas y hashes. Ejecutar `extender.py`, `validar.py`, `cerrar.py` solo para reproducir esta entrega; no promueven códigos al canon. Los scripts contienen rutas, no identificadores incrustados. Los JSON privados no se publican.
