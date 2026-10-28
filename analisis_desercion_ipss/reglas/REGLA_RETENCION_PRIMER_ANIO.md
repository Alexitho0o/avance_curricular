# Retención de 1er año (borrador)

La tasa oficial SIES es el porcentaje de estudiantes de primer año que, matriculados en una institución en el año de referencia, permanecen matriculados en la misma institución y cohorte al año siguiente. El corte es el 30 de abril. La unidad es persona, una vez por cohorte; la tasa es suma de retenidos dividida por suma de elegibles.

La base de esta fase es la corrida MU 2022–2026 `20260901_142342`, hash `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. La regla oficial describe permanencia matriculada en la misma institución y cohorte de origen; la traducción de esa condición a `VIG` en la implementación sigue pendiente (E). Un cambio de carrera dentro de IPSS cuenta como retención institucional. Los programas especiales, incluidos diplomados, se excluyen solo cuando estén identificados de forma gobernada. Las desagregaciones por sector y carrera requieren al menos diez casos.

Estado: `BORRADOR_NO_ACTIVO`.

## Conciliación de definiciones y auditoría VIG

El diagnóstico anual H001 (C/D) utiliza padrones institucionales con denominadores **305, 366, 558 y 1.150**. El componente reproduce la lógica H001 desde el catálogo del diagnóstico: origen del año, semestre 1 o 2, VIG distinto de 0, pregrado regular no especial y duración mínima por nivel; descarta duplicidad activa e inconsistencia de origen en t+1. Retenido es VIG positivo en t+1 con igual año y semestre de origen. Sus cifras no están validadas como SIES. La matriz 2022–2024 de 338, 531 y 715 es un cálculo interno previo, no publicación oficial, según su manifiesto.

La auditoría `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md` (C, commit `55e3b709afb9483f0ecdd2d166f67229a454a5ef`) documenta **960 filas VIG=0** en una carga MU 2026, con controles institucionales de nómina entre ellas. Se conservan como decisión interna con fundamento académico individual pendiente (D/E): no se revierten ni se cuentan automáticamente como retenidas. El contraste por código frente a la matriz interna favorece VIG=1 en dos códigos de 2023 y cualquier VIG en diez de 2024; no acredita una regla universal. Ver `outputs/retencion_discriminacion_codigo_20261028/INFORME.md`.

La cohorte SIES 2025 registra 1.163 casos y 677 retenidos, con 92 `no_considerar` fuera de los casos. El conteo de 2.326 fue una suma duplicada y está retirado. La cohorte 2025 permanece E hasta conciliarla con los 1.163 casos oficiales, explicando cualquier diferencia, y aprobar el tratamiento VIG. H001 es la base interna del componente; la validación SIES es externa y separada.

La comparación externa con los informes públicos por institución y el correo SIES está en `outputs/retencion_validacion_oficial_20261028/INFORME.md`; la nueva reproducción H001 se documenta en `outputs/retencion_h001_base_20261028/INFORME.md`. En el código la cohorte 2025 está bloqueada salvo que se declaren explícitamente la conciliación con la cohorte oficial (1.163 ± explicación) y la aprobación de VIG. Esas declaraciones no prueban por sí solas su respaldo.
