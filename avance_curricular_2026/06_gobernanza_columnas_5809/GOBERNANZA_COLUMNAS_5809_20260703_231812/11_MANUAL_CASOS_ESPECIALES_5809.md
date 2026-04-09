# Manual casos especiales 5809

Resultado incorporado: 2 casos adecuados, 27 pendientes, 0 rechazos definitivos.

## Nivel historico con CODCLI exacto y reporte individual
- Problema: Nivel fuera de rango con evidencia directa.
- Accion permitida: Aplicar gobernanza solo al caso evidenciado.
- Accion prohibida: Generalizar regla a otros casos.
- Bloquea archivo final: SI si no esta demostrado.
- Evidencia minima: Reporte individual + CODCLI.

## Nivel historico sin reporte individual
- Problema: Nivel no interpretable sin fuente directa.
- Accion permitida: Mantener pendiente.
- Accion prohibida: Convertir por semejanza.
- Bloquea archivo final: SI
- Evidencia minima: Reporte individual o tabla institucional.

## Familia CODCLI + carrera, sin evidencia directa
- Problema: Coincidencia parcial por familia.
- Accion permitida: Solicitar respaldo.
- Accion prohibida: Convertir por familia.
- Bloquea archivo final: SI
- Evidencia minima: Evidencia directa por caso.

## Solo carrera similar
- Problema: Coincidencia solo por carrera.
- Accion permitida: Mantener pendiente.
- Accion prohibida: Convertir por carrera.
- Bloquea archivo final: SI
- Evidencia minima: CODCLI/reporte.

## Sin modelo demostrado
- Problema: No hay modelo de conversion.
- Accion permitida: Mantener pendiente.
- Accion prohibida: Eliminar o rechazar definitivo.
- Bloquea archivo final: SI
- Evidencia minima: Modelo institucional.

## Plan multiple
- Problema: Mas de un plan posible.
- Accion permitida: Bloquear por plan.
- Accion prohibida: Elegir keep first/last.
- Bloquea archivo final: SI
- Evidencia minima: Confirmacion institucional.

## Contradiccion documento
- Problema: Documento institucional no coincide.
- Accion permitida: Bloquear identidad.
- Accion prohibida: Corregir documento de precarga.
- Bloquea archivo final: SI
- Evidencia minima: Resolucion institucional.

## Contradiccion carrera
- Problema: Carrera de fuente no coincide.
- Accion permitida: Bloquear identidad/carrera.
- Accion prohibida: Forzar carrera.
- Bloquea archivo final: SI
- Evidencia minima: Resolucion institucional.

## Multiples CODCLI
- Problema: Persona con varias trayectorias.
- Accion permitida: Resolver trayectoria.
- Accion prohibida: Decidir por nombre.
- Bloquea archivo final: SI
- Evidencia minima: CODCLI vigente/carrera.

## Fuente academica ausente
- Problema: No hay fuente completa para avance.
- Accion permitida: Solicitar fuente avance 2025.
- Accion prohibida: Inventar valores.
- Bloquea archivo final: SI
- Evidencia minima: Base academica 2025 validada.

## Avance anual no demostrable
- Problema: No hay cursadas/aprobadas 2025 trazables.
- Accion permitida: Bloquear anual.
- Accion prohibida: Mezclar historico con anual.
- Bloquea archivo final: SI
- Evidencia minima: Estados academicos 2025.

## Acumulado no demostrable
- Problema: No hay historico trazable hasta 2025.
- Accion permitida: Bloquear acumulado.
- Accion prohibida: Usar anual como total.
- Bloquea archivo final: SI
- Evidencia minima: Historico + plan.

## Convalidacion observada sin regla confirmada
- Problema: Estados de convalidacion observados.
- Accion permitida: Separar anual/acumulado segun instructivo.
- Accion prohibida: Incluir anual sin respaldo.
- Bloquea archivo final: SI
- Evidencia minima: Regla operacional y catalogo.

## Plan/malla sin semantica de nivel
- Problema: NIVEL no mapeado institucionalmente.
- Accion permitida: Bloquear Carreras/Matricula.
- Accion prohibida: Convertir nivel por supuesto.
- Bloquea archivo final: SI
- Evidencia minima: Mapa NIVEL->anio/unidades.

## Unidades acumuladas fuera de rango
- Problema: Acumulado excede plan/tolerancia.
- Accion permitida: Bloquear salvo evidencia.
- Accion prohibida: Cargar excedente sin respaldo.
- Bloquea archivo final: SI
- Evidencia minima: Total plan + tolerancia + evidencia.

