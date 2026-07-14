# Evaluacion de estrategias Git

## Estrategia A: Integrar desde rama backup actual

- riesgo_mezclar_subproyectos: ALTO
- trazabilidad: MEDIA
- reversibilidad: MEDIA
- complejidad: BAJA
- riesgo_conflicto: MEDIO
- dependencia_actualizacion_remota: MEDIA
- facilidad_revision: BAJA
- compatibilidad_pr: MEDIA
- riesgo_perder_trabajo: MEDIO
- recomendacion: NO_RECOMENDADA
- motivo: HEAD actual contiene commit local amplio con otros subproyectos y release parcial; alto ruido de revision.

## Estrategia B: Crear posteriormente rama limpia desde upstream local de la rama actual

- riesgo_mezclar_subproyectos: MEDIO
- trazabilidad: ALTA
- reversibilidad: ALTA
- complejidad: MEDIA
- riesgo_conflicto: MEDIO
- dependencia_actualizacion_remota: ALTA
- facilidad_revision: ALTA
- compatibilidad_pr: ALTA
- riesgo_perder_trabajo: BAJO
- recomendacion: RECOMENDADA_CON_OBSERVACIONES
- motivo: Base local clara para la rama informada, pero requiere autorizacion y eventual actualizacion remota antes de ejecutar.

## Estrategia C: Crear posteriormente rama limpia desde rama principal vigente

- riesgo_mezclar_subproyectos: BAJO
- trazabilidad: ALTA
- reversibilidad: ALTA
- complejidad: MEDIA
- riesgo_conflicto: ALTO
- dependencia_actualizacion_remota: ALTA
- facilidad_revision: ALTA
- compatibilidad_pr: ALTA
- riesgo_perder_trabajo: BAJO
- recomendacion: PENDIENTE
- motivo: Existe rama local main, pero no hay evidencia local suficiente de rama principal remota vigente sin fetch.

## Estrategia D: Crear rama limpia desde merge-base y aplicar solo subproyecto

- riesgo_mezclar_subproyectos: BAJO
- trazabilidad: MEDIA
- reversibilidad: ALTA
- complejidad: ALTA
- riesgo_conflicto: ALTO
- dependencia_actualizacion_remota: MEDIA
- facilidad_revision: MEDIA
- compatibilidad_pr: MEDIA
- riesgo_perder_trabajo: BAJO
- recomendacion: NO_PREFERIDA
- motivo: Muy aislada, pero ignora intencionalmente cambios del upstream local y puede complicar PR.

## Estrategia E: Reconstruir commits selectivos usando inventario, sin cherry-pick completo

- riesgo_mezclar_subproyectos: BAJO
- trazabilidad: ALTA
- reversibilidad: ALTA
- complejidad: MEDIA_ALTA
- riesgo_conflicto: MEDIO
- dependencia_actualizacion_remota: MEDIA
- facilidad_revision: ALTA
- compatibilidad_pr: ALTA
- riesgo_perder_trabajo: BAJO
- recomendacion: RECOMENDADA
- motivo: Evita mezclar otros subproyectos y permite commits pequenos por alcance.

Recomendacion: combinar B+E, salvo que revision humana confirme una rama principal institucional distinta; en ese caso aplicar E desde esa base confirmada.
