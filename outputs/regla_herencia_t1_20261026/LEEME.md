# Regla de herencia del código T1 (§6) · evaluación sin adopción (26-10-2026)

**E — Regla evaluada.** Heredar el código SIES de T1 solo si coinciden plan, carrera y
expediente; sede; jornada; modalidad y duración en la oferta; año igual o siguiente; y no hay
otra versión de la familia sede-carrera-jornada en la oferta del año observado.

**C — Prueba sobre 2.742 contextos con código documental (B/C):**
- Variante estricta (cualquier otra versión presente bloquea): 933 cumplen y en los 933 el código
  documental es el de T1. Sin contraejemplos.
- Variante laxa (solo bloquea otra versión abierta a nuevos): 2.218 cumplen; 6 fallan
  (IINF20241: T1 J2V4 → documental J2V1, 4; T1 J1V2 → documental J1V1, 2). Queda descartada.

**C — Impacto sobre los 78 pendientes del diccionario activo v9:** ninguna variante resuelve
ninguno. 73 no comparten plan/carrera/expediente con T1 y 48 cambian de jornada (no aditivos).
Detalle en PENDIENTES_POR_CONDICION.csv.

**D pendiente del usuario.** No se modifica el diccionario. Hashes en MANIFEST.json.

## Decisión aprobada (D) · 26-10-2026 09:52

**D — Opción A.** Variante estricta adoptada solo como control de consistencia (`control_consistencia_herencia_t1.py`); no asigna ni propaga códigos. Primera ejecución sobre v9: 933 consistentes, 0 diferencias. Detalle en DECISION_APROBADA.json.
