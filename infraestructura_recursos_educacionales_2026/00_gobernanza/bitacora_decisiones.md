# Bitacora de decisiones - IRE 2026

## HITO 1A

### Decisiones iniciales

1. El subproyecto IRE 2026 se trabajara dentro del repositorio mayor avance_curricular.
2. Las fuentes originales se copiaran desde Descargas manteniendo exactamente sus nombres.
3. Las fuentes originales no seran modificadas.
4. Todo hito posterior debera quedar registrado en el manifiesto.
5. Todo prompt o comando posterior debera tener numero y letra.
6. No se generaran archivos derivados hasta completar inventario, hash y estructura base.
7. No se copiaran archivos al Escritorio salvo solicitud explicita.

## HITO 1B

### Decisiones / criterios aplicados

1. Las fuentes originales se leyeron en modo solo lectura.
2. No se interpretaron reglas funcionales.
3. No se generaron archivos de carga.
4. El inventario tecnico queda como base para la lectura funcional posterior.
5. Cualquier inconsistencia tecnica se tratara en hitos posteriores.

## HITO 2A

### Registro

1. Se leyó funcionalmente el instructivo oficial IRE 2026.
2. Se separaron reglas oficiales de estructura técnica observada.
3. No se generaron archivos de carga.
4. No se modificaron fuentes originales.
5. Las reglas extraídas quedan como base para validaciones posteriores.
6. Los vacíos o contradicciones no se completaron por supuesto.

## HITO 2B

### Decisiones / criterios aplicados

1. Se construyó diccionario estructurado campo a campo.
2. Se comparó instructivo oficial contra estructura CSV.
3. No se modificaron fuentes originales.
4. No se generó archivo de carga.
5. Las contradicciones y vacíos quedaron explícitos.
6. La matriz campo por tipo de infraestructura queda pendiente para HITO 2C.
7. Los bloques funcionales se registraron como clasificación técnica de trabajo y no como agrupación oficial.
8. `CODIGO_INSTITUCION` se registró como variable solo mencionada en el instructivo y no se añadió a la estructura CSV.

## HITO 2C

### Decisiones / criterios aplicados

1. Se construyó matriz funcional campo por tipo de infraestructura.
2. Se mantuvo separación entre regla oficial, estructura técnica y decisión de trabajo.
3. No se modificaron fuentes originales.
4. No se generó archivo de carga.
5. Los campos ambiguos quedaron como pendientes o contradicciones.
6. La matriz será base para diseñar validaciones en HITO 3A.
7. `NO_COMPLETAR` regula el valor funcional, no la presencia de la columna dentro de la estructura fija de 54 campos.
8. No se decidió por supuesto si un campo no aplicable debe representarse con blanco, cero u otro marcador aceptado por PES.

## HITO 3A

### Decisiones / criterios aplicados

1. Se diseñaron reglas de validación técnica y funcional.
2. No se validaron datos institucionales reales.
3. No se generó archivo de carga.
4. No se resolvieron contradicciones por supuesto.
5. Las reglas quedan como insumo para implementar validador en HITO 3B.
6. Las reglas con ambigüedad quedaron como pendientes de confirmación o solo documentadas.
7. La llave propuesta se considera técnica de auditoría y no una llave oficial PES.
8. Las reglas NO_COMPLETAR requieren decisión formal sobre blanco versus cero antes de activarse como bloqueo productivo.

## HITO 3B-Z

### Decisiones / criterios aplicados

1. Se verificó la implementación del validador luego de una interrupción/desconexión.
2. El primer check falló por un `--run-id` inválido, no por falla del validador.
3. El recheck con formato `YYYYMMDD_HHMMSS` confirmó comportamiento esperado.
4. La ejecución normal retorna 0.
5. La ejecución con `--fail-on-blocking` retorna 2 ante bloqueantes.
6. HITO 3B se cierra como COMPLETADO_CON_OBSERVACIONES.
7. La prueba sigue siendo artificial; falta validar fuente institucional real.
