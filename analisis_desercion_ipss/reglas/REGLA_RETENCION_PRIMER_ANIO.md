# Retención de 1er año (borrador)

La tasa oficial SIES es el porcentaje de estudiantes de primer año que, matriculados en una institución en el año de referencia, permanecen matriculados en la misma institución y cohorte al año siguiente. El corte es el 30 de abril. La unidad es persona, una vez por cohorte; la tasa es suma de retenidos dividida por suma de elegibles.

La base de esta fase es la corrida MU 2022–2026 `20260901_142342`, hash `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. La regla oficial describe permanencia matriculada en la misma institución y cohorte de origen; la traducción de esa condición a `VIG` en la implementación sigue pendiente (E). Un cambio de carrera dentro de IPSS cuenta como retención institucional. Los programas especiales, incluidos diplomados, se excluyen solo cuando estén identificados de forma gobernada. Las desagregaciones por sector y carrera requieren al menos diez casos.

Estado: `BORRADOR_NO_ACTIVO`.

## Conciliación de definiciones y auditoría VIG

El diagnóstico anual H001 (C/D) utiliza padrones institucionales con denominadores **305, 366, 558 y 1.150**. El código nuevo (C/E) ensaya presencia de la persona en `t+1` con cualquier VIG, sin verificar la cohorte de origen en ese año. Sus cifras no están validadas como SIES. La matriz 2022–2024 de 338, 531 y 715 es un cálculo interno previo, no publicación oficial, según su manifiesto.

La auditoría `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md` (C, commit `55e3b709afb9483f0ecdd2d166f67229a454a5ef`) documenta **960 filas VIG=0** en una carga MU 2026, con controles institucionales de nómina entre ellas. Se conservan como decisión interna con fundamento académico individual pendiente (D/E): no se revierten ni se cuentan automáticamente como retenidas. El contraste por código frente a la matriz interna favorece VIG=1 en dos códigos de 2023 y cualquier VIG en diez de 2024; no acredita una regla universal. Ver `outputs/retencion_discriminacion_codigo_20261028/INFORME.md`.

Las cargas incrementales `2 y 3er Intake.xlsx` y `Gestion_SIES_Matrícula_Pregrado_2025.xlsx` están disponibles, pero la cohorte 2025 sigue E hasta deduplicar, aplicar ingreso actual/original, exclusiones de programas especiales y el tratamiento VIG auditado. El componente 1 debe reproducir SIES como validación externa; H001 se conserva como indicador interno separado.
