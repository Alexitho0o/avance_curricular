# H002l · Depuración y cierre de catálogo MU 2027

D · Alexi, 29-10-2026. Corrección de H002k decisión 3. ANTIGUO conserva
su código de MU 2026; el tipo E y plan no observado son informativos.
Sólo revisión si (1) falta código/fila inequívoca, (2) el código no está en oferta
2027, (3) tiene VIGENCIA 3. VIGENCIA 2 permite conservar antiguos. No se
reinterpreta VIG de MU ni se acredita continuidad 2027 por este cálculo.
La clasificación ANTIGUO/NUEVO/OTRO pertenece al contexto del llamador: esta
función no convierte cambios de carrera en antiguos ni asigna otra matrícula.

Para NUEVO, prevalece la segunda condición explícita de la decisión: si la
familia admite nuevos pero no el tipo del plan, queda REVISION_REAL. Si no hay
ninguna versión VIGENCIA 1 en la familia, PLAN_SIN_ADMISION_2027 es informativo,
incluso con tipo E; nunca devuelve código para cargar. Tipo E con admisión sí
requiere revisión. Oferta ausente no prueba falta de admisión: queda E/revisión.

Se usa el mismo universo potencial y opciones de catálogo de H002k, sin alterar
su lista v1, su tabla H002 ni denominadores. La lista v2 separa matrículas,
opciones de catálogo y 37 códigos sin plan. Detalle individual sólo privado.
Regla activa corregida y cierre documental H002: no equivale a concordancia total
histórica ni a carga 2027 completa. Casos de contraste y pendientes se preservan.

QA: pruebas sintéticas para cada vía, conservación con tipo E/VIG 0/DV 0,
VIGENCIA 2/3, admisión por familia/tipo, integridad, reproducción y privacidad.
Sólo se modifican función, regla activa y registro del hito; nuevos archivos H002l.
