# Retención de 1er año (borrador)

La tasa oficial SIES es el porcentaje de estudiantes de primer año que, matriculados en una institución en el año de referencia, permanecen matriculados en la misma institución y cohorte al año siguiente. El corte es el 30 de abril. La unidad es persona, una vez por cohorte; la tasa es suma de retenidos dividida por suma de elegibles.

La única base de esta fase es la corrida MU 2022–2026 `20260901_142342`, hash `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. Una persona retenida es aquella presente en la MU de t+1 de IPSS, con cualquier valor de VIG; el filtro VIG=1 se eliminó porque la regla oficial exige presencia, no un valor particular de VIG. Un cambio de carrera dentro de IPSS cuenta como retención institucional. Los programas especiales, incluidos diplomados, se excluyen solo cuando estén identificados de forma gobernada. Las desagregaciones por sector y carrera requieren al menos diez casos.

Estado: `BORRADOR_NO_ACTIVO`.

## Conciliación de definiciones y auditoría VIG

La definición oficial SIES (A) exige presencia de la persona en la matrícula de IPSS en `t+1`; no agrega un filtro `VIG=1`. El diagnóstico anual H001 (C/D) utiliza padrones institucionales distintos, con denominadores **305, 366, 558 y 1.150**. El código nuevo (C) reproduce la regla oficial sobre MU 142342, con persona una vez y presencia en `t+1`. No se mezclan las tasas: los universos H001 y SIES difieren; SIES informa como referencias **338, 531, 715 y 2.326** antes de exclusiones y `no_considerar`.

La auditoría `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md` (C, commit `55e3b709afb9483f0ecdd2d166f67229a454a5ef`) documenta **960 filas VIG=0** en el envío MU 2026, asignadas por controles institucionales de nómina. Se conservan como decisión interna con fundamento académico individual pendiente (D/E): no se revierten ni se cuentan automáticamente como retenidas en ese control. Para 2023–2025, la lectura oficial se mantiene por presencia en MU de `t+1`; el control 2026 es una transformación específica del envío y no una regla retrospectiva universal.

Las cargas incrementales `2 y 3er Intake.xlsx` y `Gestion_SIES_Matrícula_Pregrado_2025.xlsx` están disponibles, pero la cohorte 2025 sigue E hasta deduplicar, aplicar ingreso actual/original, exclusiones de programas especiales y el tratamiento VIG auditado. El componente 1 debe reproducir SIES como validación externa; H001 se conserva como indicador interno separado.
