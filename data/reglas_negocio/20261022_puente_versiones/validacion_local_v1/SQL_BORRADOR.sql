-- D/E: PENDIENTE_APROBACION_GOBERNANZA. Solo revisión agregada.
-- Contrato lógico propuesto; adaptar nombres al consumidor antes de ejecutar.
-- No genera equivalencias ni cambia bases.
SELECT carrera_interna, sede, jornada, planes, codigo_predominante_observado,
       personas_coincidentes_unicas, proporcion_incidencias, estado, pendiente
FROM auditoria_puente_versiones
WHERE estado = 'PENDIENTE';
