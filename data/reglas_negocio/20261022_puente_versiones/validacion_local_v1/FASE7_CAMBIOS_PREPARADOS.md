# Preparación controlada — PENDIENTE_APROBACION_GOBERNANZA

D: Borrador autorizado por el usuario; no instalado ni publicado. Ningún cambio productivo.

| Componente | Cambio preparado | Puerta pendiente |
|---|---|---|
| Reglas de negocio | Exigir TIPO_DOC=R, RUT/DV exactos y contexto temporal explícito. Predominio >=90% y n>=3 es propuesta interna, nunca regla oficial SIES. | Tipo y duración UMAS acreditados; conciliación MU exacta; responsable y aprobación |
| SQL | Consulta de revisión SQL_BORRADOR.sql, sobre tablas agregadas; no actualiza tablas productivas. | Esquema real del consumidor y aprobación |
| Complementos | Contrato: consumir solo estado aprobado y hash fijo; devolver PENDIENTE sin código ante conflicto, falta de evidencia o contexto temporal ausente. | Identificar complementos consumidores y sus versiones; sin instalación automática |
| Skills | Texto propuesto: conservar fuentes, separar A/B/C/D/E, prohibir homologación por nombre, distinguir personas de matrículas y no sumar personas entre planes/años. | Revisión de responsables; no editar skills instaladas |
| Regresión | Dos implementaciones coinciden, hashes intactos, cero diferencia de totales MU; exigir no coincidencia R/P, no doble conteo de personas y ausencia de match distinta de cero/deserción. | Conciliación semántica de denominadores, retenidos y tasas |
| Diccionario | Usar TABLA_63_DIMENSIONES como auditoría, conservar estado previo y evidencia, sin promover. El definitivo requiere grano carrera/sede/jornada/plan/año acreditado. | Fases 1–5 con puertas satisfechas |
| Bitácora | Auditoría local 2026-10-22: 63 dimensiones, 141 pares dimensión/candidato, 0 asignaciones nuevas; 2 discrepancias de conteo cuya causa sigue pendiente. | Cierre de brechas y aprobación formal |

E: No existe diccionario definitivo. No se atribuye autoridad A a cálculos internos. VERSION y VIGENCIA se mantienen separadas.
