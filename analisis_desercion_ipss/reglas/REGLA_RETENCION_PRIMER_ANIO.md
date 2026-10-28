# Retención de 1er año · indicador interno H001

La tasa oficial SIES es el porcentaje de estudiantes de primer año que, matriculados en una institución en el año de referencia, permanecen matriculados en la misma institución y cohorte al año siguiente. El corte es el 30 de abril. La unidad es persona, una vez por cohorte; la tasa es suma de retenidos dividida por suma de elegibles.

La base de esta fase es la corrida MU 2022–2026 `20260901_142342`, hash `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. La regla oficial describe permanencia matriculada en la misma institución y cohorte de origen; la traducción de esa condición a `VIG` en la implementación sigue pendiente (E). Un cambio de carrera dentro de IPSS cuenta como retención institucional. Los programas especiales, incluidos diplomados, se excluyen solo cuando estén identificados de forma gobernada. Las desagregaciones por sector y carrera requieren al menos diez casos.

Estado: `ACTIVA` para el componente interno, aprobado por Alexi el 28-10-2026. Rótulo: **Indicador interno alineado con la definición oficial SIES; no es la tasa oficial**. El subproyecto completo no se activa.

## Conciliación de definiciones y auditoría VIG

El diagnóstico anual H001 (C/D) utiliza padrones institucionales con denominadores **305, 366, 558 y 1.150**. El componente reproduce la lógica H001 desde el catálogo del diagnóstico: origen del año, semestre 1 o 2, VIG distinto de 0, pregrado regular no especial y duración mínima por nivel; descarta duplicidad activa e inconsistencia de origen en t+1. Retenido es VIG positivo en t+1 con igual año y semestre de origen. Sus cifras no están validadas como SIES. La matriz 2022–2024 de 338, 531 y 715 es un cálculo interno previo, no publicación oficial, según su manifiesto.

La evidencia de VIG y los controles de carga se conserva en `data/reglas_negocio/mu2027/estudio/AUDITORIA_VIG_ENVIOS_RETENCION.md` (C, commit `55e3b709afb9483f0ecdd2d166f67229a454a5ef`) y en la documentación de generación MU 2026 indicada más abajo.

La cohorte SIES 2025 registra 1.163 casos y 677 retenidos, con 92 `no_considerar` fuera de los casos. H001 contiene 1.150 casos y 668 retenidos: la diferencia agregada de 13 casos y 9 retenidos está distribuida en nueve códigos, según H001; su causa individual sigue E. El conteo de 2.326 fue una suma duplicada y está retirado.

La comparación externa con los informes públicos por institución y el correo SIES está en `outputs/retencion_validacion_oficial_20261028/INFORME.md`; la reproducción H001 se documenta en `outputs/retencion_h001_base_20261028/INFORME.md`. La cohorte 2025 está desbloqueada únicamente para el indicador interno aprobado. Las brechas 2022 (+4,49 pp) y 2024 (−9,08 pp) siguen E; se documentan en `manifests/milestones/H001-RETENCION-IPSS162/README.md`.

La generación y cierre de MU 2026 se documentan en `control/reportes/decision_operativa_mu_2026.md`, `control/reportes/ejecucion_oficial_mu_2026.md`, `control/gate/gate_final_mu_2026.md` y `CIERRE_PES_READY_MU2026.md`.

El prototipo de presencia con cualquier VIG está **descartado** para el cálculo porque no acredita matrícula vigente ni la misma cohorte de origen. La comparación con `Retencion_ipss_2022_2024_GRANULAR.xlsx` está **descartada para el trabajo vigente** porque ese archivo es un cálculo interno previo, no una publicación oficial SIES; se conserva como antecedente histórico.
