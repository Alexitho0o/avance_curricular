# Procedencia de códigos en V24

Proceso: seguimiento interno de retención IPSS, contextos T2/T3 observados en 2025–2026 y anclas 2024–2026. Fecha de revisión: 25-10-2026.

C/D — Se aplica una clasificación de procedencia, no una regla nueva de adjudicación. Se conserva el código destino adoptado por el diccionario v8. La ausencia de nueva oferta no selecciona una versión entre versiones preexistentes ni demuestra continuidad individual. Un código de T1 puede conservarse cuando coinciden expediente atribuido, carrera, sede, jornada y plan, sin contradicción documental. No se exige que las demás versiones dejen de ofertarse.

B/C — El historial publicado contiene aprobaciones internas acotadas (v6 y v7) y propuestas de continuidad no adoptadas. Por ello no corresponde afirmar que el criterio nunca se utilizó o que se descartó universalmente. Fuentes: docs/DICCIONARIO_SIES_SEGUIMIENTO.md, apartados v6–v8; docs/ESPECIFICACION_FASE3_SEGUIMIENTO_T1_20261025.md; outputs/trazabilidad_integral_umas_sies_20261025/fase3/seguir_t1.py.

C — V24 agrega AC:AF a 56_Vista_T1_T2_T3. AC clasifica mediante fórmula; AD registra la comprobación contextual reproducida del JSON de fase3; AE explica respaldo o condición faltante; AF conserva clase B/C, D o E. Los campos originales M y N permanecen intactos. O mantiene la fuerza documental original, incluso cuando AC dice heredado.

D — La solicitud del usuario autoriza validar y aplicar el criterio donde esté respaldado. No autoriza inventar continuidad temporal ni alterar tasas. Se agrega una cuarta categoría «Correspondencia interna aprobada» para no presentar decisiones internas como confirmación documental. La categoría histórica se denomina «confirmado por matrícula histórica»: oferta sola acredita existencia del código, no asignación personal.

E — No se crean nuevas adjudicaciones: ninguno de los 99 contextos pendientes satisface todas las condiciones. Los 3.520 espacios sin contexto siguen pendientes de atribución de destino y no son desertores demostrados. Son unidades diferentes de personas.

C — QA previsto: comparar fila por fila el JSON fuente con M/N/H del Excel; verificar categorías, fórmulas y caché; preservar todos los demás componentes ZIP, bases, gráficos y denominadores. El libro contiene detalle individual y solo se guarda localmente, fuera de Git. Documentación y código sin identificadores quedan locales, sin commit/push.
