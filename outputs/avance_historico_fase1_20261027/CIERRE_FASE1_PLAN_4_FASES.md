# Cierre de fase 1 del plan de cuatro fases

[D] Ejecución autorizada: fase 1, recuperación y verificación del trabajo existente. Objetivo final: análisis histórico de avance académico, con avance anual SIES, seguimiento interno por períodos y aprobaciones frente a malla en capas separadas. No se genera todavía Excel ni se autorizan nuevas asignaciones.

## Estado ejecutivo

[B/C] **Fase 1 cerrada como diagnóstico reproducible.** Se comprobaron 71 controles de integridad, sin fallos, sobre 15 fuentes distintas, resultados, código y evidencias Git. Esta ejecución revalida la evidencia existente; no repite el cálculo académico completo ni certifica que todas las atribuciones sean correctas.

| Hito | Resultado | Estado | Clase |
|---|---|---|---|
| 1. Fuentes y cadena | Manual 2026, mallas H112A, carreras H112B, cálculo H94D/H113 y transformación H114B localizados; rutas y hashes registrados | Completo para el diagnóstico | A/B/C |
| 2. Reproducción y diferencias | Transformación H114B reproducida sin diferencias; cálculo primario coincide en 2.370 de 2.371 filas en los seis campos académicos examinados | Completo como conciliación; una fila sigue pendiente | B/C/E |
| 3. Registro y reanudación | Pendientes separados, ruta de cuatro fases y referencias verificadas | Completo | C |

[A] Contexto normativo: Avance Curricular SIES proceso 2026, actividad académica anual de 2025 y acumulada hasta su cierre. Instructivo local, pp. 2 y 4–5. La ampliación a otros períodos será un análisis interno y no prueba de envíos oficiales de esos períodos.

[B/C] Universo de esta precarga: **2.371 filas** y **43 combinaciones código único–plan**. No se equipara al universo de retención de 2.379 registros ni se cambia ningún denominador. La fase inicial reprodujo 49 controles parciales; la revisión primaria posterior cotejó los seis campos académicos contra H113. El control actual de 71 comprobaciones es de integridad y no se suma a aquellos como si todos verificaran lo mismo.

## Línea base recuperada

| Medida (unidades, no estudiantes) | H113 observado | Reproducción primaria sin mapeo externo | H114B observado | Clase |
|---|---:|---:|---:|---|
| Cursadas 2025 | 21.389 | 21.377 | 21.389 | B/C |
| Aprobadas 2025 | 17.628 | 17.616 | 17.628 | B/C |
| Cursadas acumuladas | 47.205 | 47.193 | 47.205 | B/C |
| Aprobadas acumuladas | 41.627 | 41.615 | 38.235 | B/C |

[E] La diferencia de 12 unidades en los cuatro campos corresponde a una fila cuyo puente externo no se recuperó. No se reemplazó el dato por cero ni se asumió falta de actividad.

[C] H114B aplica el mínimo entre aprobadas acumuladas H113, unidades del plan y cursadas acumuladas H113. Se reprodujeron sus 247 filas modificadas y 20 combinaciones afectadas, conservando las otras 20 columnas. Reproducir esta transformación no acredita la causa académica de cada reducción.

## Pendientes que se conservan y fase responsable

| Pendiente | Tratamiento | Fase | Clase |
|---|---|---|---|
| Una fila sin reproducción primaria completa | Reutilizar búsqueda ya registrada; no asumir equivalencia ni actividad cero | 2 | E |
| Normalización de identidad y atribución a expediente/carrera/plan | Continuar las auditorías ya ejecutadas; escenarios todavía no aplicados | 2 | B/C/E |
| 644 contextos con coincidencia anual comprobada pero período sin indexar | Preparar propuesta acotada de ampliación, sin presentarla como cierre aprobado | 2 | C/E |
| Resto de contextos pendientes | Conservar desglose y revisar por causa, sin repetir inventario | 2 | E |
| Relación entre plan UMAS y PLAN_ESTUDIOS de la precarga | El correlativo SIES no equivale al nombre UMAS; acreditar su correspondencia | 2–3 | A/E |
| Reconocimientos aplicables y límite usado por H114B | Separar conteo primario, reconocimiento académico y transformación histórica; no asumir que el recorte estricto es regla universal | 3 | C/E |
| Conversión de períodos/niveles | No convertir automáticamente períodos UMAS 1–5 en trimestres o semestres | 3 | E |
| Aceptación final PES | La evidencia localizada acredita pruebas/validación, no aceptación final; no bloquea describir el análisis interno con este límite | Trazabilidad | E |

## Trabajo ya avanzado que no se repetirá

[B/C] La auditoría de atribución consultó 5.144 contextos: 3.109 con respaldo documental anual, 17 con correspondencia interna aprobada y 2.018 pendientes. Es el foco examinado, no todo el diccionario institucional.

[B/C/E] Dentro de los 2.018 pendientes se distinguen 644 candidatos con coincidencia verificada, 171 restantes del bloque de períodos no indexados, 762 expedientes no indexados, una discrepancia de carrera y 440 excepciones adicionales. Los 644 no se han aplicado. Las búsquedas de títulos y los reconocimientos individuales aprobados no se reabren.

## Archivos y punto de continuación

[C] Plan: docs/PLAN_AVANCE_HISTORICO_4_FASES_20261027.md. El checkpoint identifica la siguiente fase y evita confundir los informes históricos con el estado actual. Este cierre complementa INFORME_FASE1.md y MANIFEST_FASE1.json, que se conservan intactos; sus pendientes de reproducción deben leerse junto con los avances posteriores referenciados.

[C] La próxima acción, cuando se continúe, es **fase 2, hito 2.3: preparar la ampliación de los 644 candidatos, evaluar su alcance y presentar el efecto antes de activarla**. La revisión de los 171 restantes continúa por causas, priorizando los 107 con código anual único. No se repite fase 1.

[B/C] Rama feature/ire-2026; HEAD antes/después 262f445828f7e939fac59c3cc76d0bb20a101746. Fuentes, bases, denominadores, motor, diccionario y cambios preexistentes conservados. Sin Excel nuevo, commit, push ni publicación. Las salidas de este cierre son documentación y controles agregados.

[C] Verificación reproducible desde el repositorio:

```sh
python3 outputs/avance_historico_fase1_20261027/verificar_cierre_fase1.py
```

[C] El comando comprueba hashes y evidencias previas; no vuelve a calcular ni modifica los resultados académicos.
