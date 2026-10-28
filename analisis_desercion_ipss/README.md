# Subproyecto ANALISIS_DESERCION_IPSS

Estado: **BORRADOR**. El propósito es separar y documentar la Retención de 1er año oficial SIES de los análisis internos de salida entre períodos y, solo si existe evidencia suficiente, del destino posterior de quienes salen de IPSS.

## Componentes

1. `1_retencion_primer_anio`: **activo como indicador interno H001**, alineado con la definición SIES; no es la tasa oficial. Cohorte, referencia del 30 de abril y unidad persona; brechas y límites en su regla.
2. `2_salida_entre_periodos`: reutiliza el indicador intertrimestral gobernado; no lo duplica ni lo presenta como tasa oficial SIES.
3. `3_destino_de_la_salida`: distingue cambio de institución, deserción del sistema y sin determinar. Permanece E hasta acreditar RUT–MRUN.
4. `4_reporte`: genera tablas agregadas y Excel desde código, nunca desde valores pegados.

## Principios

- Persona una vez por cohorte; agregación como suma de numeradores / suma de denominadores.
- La ausencia de actividad o registro no es deserción.
- «Deserción» siempre lleva calificativo; los casos sin evidencia quedan sin determinar.
- Solo se usan fuentes canónicas por ruta y hash del catálogo; nunca copias marcadas «no usar».

## Relación con la gobernanza existente

El diccionario UMAS–SIES vigente se consulta mediante `data/diccionario_sies_seguimiento/activo.json`. Las fuentes y sus hashes se consultan en `data/catalogo_datos/CATALOGO_DATOS_IPSS.json` y `data/catalogo_fuentes/CATALOGO_FUENTES.json`. El componente intertrimestral se referencia en `data/reglas_negocio/indicador_intertrimestral/REGLA.json`; no se copia. La auditoría VIG se referencia en `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md` y el hito H001 en `manifests/milestones/H001-RETENCION-IPSS162/`. El estado del subproyecto y sus reglas se registra en `PROYECTO_IPSS.json`.

## Trabajo previo que ya concilia (leer antes de calcular)

- El diagnóstico H001 se encuentra en `manifests/milestones/H001-RETENCION-IPSS162/README.md` y `outputs/retencion_h001_base_20261028/INFORME.md`. Su comparación agregada con SIES presenta diferencias de −0,08 pp en 2023 y −0,12 pp en 2025; son resultados cercanos, no paridad exacta. Las brechas 2022 y 2024 conservan sus pendientes.
- La evidencia sobre VIG enviado y los controles de nómina está en `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md`.
- La generación y cierre MU 2026 están documentados en `control/reportes/decision_operativa_mu_2026.md`, `control/reportes/ejecucion_oficial_mu_2026.md`, `control/gate/gate_final_mu_2026.md` y `CIERRE_PES_READY_MU2026.md`.

No recalcular ni reconciliar lo ya conciliado salvo instrucción explícita; conservar visibles las diferencias y pendientes existentes.
