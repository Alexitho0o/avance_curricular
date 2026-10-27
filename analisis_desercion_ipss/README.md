# Subproyecto ANALISIS_DESERCION_IPSS

Estado: **BORRADOR**. El propósito es separar y documentar la Retención de 1er año oficial SIES de los análisis internos de salida entre períodos y, solo si existe evidencia suficiente, del destino posterior de quienes salen de IPSS.

## Componentes

1. `1_retencion_primer_anio`: indicador oficial SIES, con cohorte, corte del 30 de abril y unidad persona.
2. `2_salida_entre_periodos`: reutiliza el indicador intertrimestral gobernado; no lo duplica ni lo presenta como tasa oficial SIES.
3. `3_destino_de_la_salida`: distingue cambio de institución, deserción del sistema y sin determinar. Permanece E hasta acreditar RUT–MRUN.
4. `4_reporte`: genera tablas agregadas y Excel desde código, nunca desde valores pegados.

## Principios

- Persona una vez por cohorte; agregación como suma de numeradores / suma de denominadores.
- La ausencia de actividad o registro no es deserción.
- «Deserción» siempre lleva calificativo; los casos sin evidencia quedan sin determinar.
- Solo se usan fuentes canónicas por ruta y hash del catálogo; nunca copias marcadas «no usar».

## Relación con la gobernanza existente

El diccionario UMAS–SIES vigente se consulta mediante `data/diccionario_sies_seguimiento/activo.json`. Las fuentes y sus hashes se consultan en `data/catalogo_datos/CATALOGO_DATOS_IPSS.json` y `data/catalogo_fuentes/CATALOGO_FUENTES.json`. El componente intertrimestral se referencia en `data/reglas_negocio/indicador_intertrimestral/REGLA.json`; no se copia. El estado del subproyecto y sus reglas se registra en `PROYECTO_IPSS.json`.
