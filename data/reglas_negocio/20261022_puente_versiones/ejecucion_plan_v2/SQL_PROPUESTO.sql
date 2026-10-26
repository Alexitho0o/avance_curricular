-- D/E: PENDIENTE_APROBACION_GOBERNANZA. No ejecutado en bases productivas.
-- Tablas temporales normalizadas p/m/candidates se definen en ejecutar.py.
-- El enlace es anual: NO acredita período académico ni vigencia del plan.
SELECT a.c AS carrera, a.s AS sede, a.j AS jornada,
       p.plan, p.y AS ano, p.t AS periodo_observado,
       m.code AS codigo, COUNT(DISTINCT p.id) AS personas
FROM candidates a
JOIN p ON p.c=a.c AND p.j=a.j
JOIN m ON m.id=p.id AND m.y=p.y AND m.code=a.code
GROUP BY a.c,a.s,a.j,p.plan,p.y,p.t,m.code;
-- No INSERT/UPDATE a equivalencias, ni interpretación de ausencia como deserción.
