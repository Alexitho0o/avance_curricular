# Fase 3/6 — Seguimiento T1 y excepciones de contexto

D — Alexi solicita seguir el padrón T1 en T2/T3 con el diccionario vigente, sin cambiar bases ni denominadores. Esta ejecución genera una vista de auditoría; no promueve reglas, asignaciones ni un nuevo Excel.

C — Reutilizar los 3.179 orígenes y 6.358 posiciones origen×período ya conciliados en Fase1. Conservar calendario observado: cohorte2024→2025 períodos nativos2/3; cohortes2025/2026→mismo año períodos2/3. No homologar el período nativo a un cierre distinto ni convertir ausencia de contexto en deserción.

C — Leer el puntero de PROYECTO_IPSS.json y consultar la API común, sin copiar el diccionario. Mantener código de origen, código documental destino, correspondencia interna destino y pendientes en campos separados. Validar identidades/contextos exactos y preservar destinos múltiples como hijos, sin multiplicar integrantes del padrón.

C — Contrastar sede/carrera/jornada/versión de los códigos respaldados; comparar plan y carrera UMAS contra contexto nativo1 del mismo CODCLI cuando exista. Cuando haya varios o ninguno, registrar el límite. Dos expedientes simultáneos no prueban un cambio de carrera; una diferencia de versión no prueba una fecha administrativa ni un cambio de plan.

C — Revisar solo excepciones: código distinto, dimensiones observadas distintas, falta de código destino, plan diferente/múltiple o ausencia de comparación T1. Releer únicamente las filas de PROMEDIOS citadas por esas excepciones; conservar código/carrera/jornada/plan originales y su procedencia. No recalcular toda la historia ni deducir códigos por totales.

C/D — Se reutilizan exclusivamente respuestas documentales o internas ya aprobadas. No cerrar nuevos pendientes por semejanza, falta de cambios visibles o candidatos únicos sin respaldo. Conservar las decisiones históricas sobre jornadas sin sobreescribir dimensiones de fuentes posteriores.

C — Salidas: vista privada origen→posiciones→contextos fuera de Git y comprobada antes de escribir; tablas agregadas por cohorte/período, origen/destino, excepción y plan; informe, QA, manifiesto y checkpoint. Sin nombres ni identificadores en agregados.

C — QA: 558+1.150+1.471=3.179; dos posiciones por origen; mismos orígenes/posiciones/contextos que Fase1; respuestas iguales al diccionario activo; cada destino pertenece a la identidad y período consultados; clasificación documental/interna separada; fuentes/diccionario/libros/denominadores conservados por hash. Sin commit/push. El estado técnico correcto no certifica aceptación SIES ni cobertura de fotos de cierre.
