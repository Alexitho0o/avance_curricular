# Auditoria transversal PROMEDIOSDEALUMNOS

Fase observacional. No se modificaron fuentes, scripts, resultados ni conciliaciones.

## Inventario

- Archivos encontrados en Descargas: 8
- Archivos encontrados en repositorio: 44
- Hashes unicos: 29
- Grupos de copias identicas: 8
- Errores de lectura documentados: 2

## Procesos

- Matricula Unificada: 91 scripts relevantes observados.
- Estudiantes Extranjeros: 19 scripts relevantes observados.
- Avance Curricular: 4 scripts relevantes observados.
- Otros procesos: 30 scripts relevantes observados.

## Hallazgos transversales

1. PROMEDIOSDEALUMNOS aparece como fuente o derivado congelado en Avance Curricular y como base normalizada/resultado en Extranjeros.
2. Matricula Unificada conserva evidencia de uso de CODCLI, controles multicodigo y cruces con catalogos; las rutas historicas se clasifican como evidencia secundaria cuando estan en backups/archive.
3. El cruce de mayor trazabilidad observado para Avance Curricular es RUT+DV -> DatosAlumnos.RUT -> CODCLI -> Hoja1.CODCLI -> CODCARR/PLAN_DE_ESTUDIO/asignaturas.
4. Las filas de Hoja1 deben tratarse como actividad academica, no como matriculas independientes.
5. Las copias con hash identico no se cuentan como evidencia independiente.

## Modelo objetivo pendiente

Ver `07_MODELO_OBJETIVO/` para campos minimos, criterios de relacion y controles recomendados. No se implemento ninguna mejora en esta fase.
